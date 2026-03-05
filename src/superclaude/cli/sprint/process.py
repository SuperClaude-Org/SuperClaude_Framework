"""Sprint process management — subprocess lifecycle and signal handling.

ClaudeProcess extends pipeline.process.ClaudeProcess with sprint-specific
constructor (config, phase) and build_prompt(). subprocess and os are
imported at module level for test-patch compatibility.
SignalHandler remains sprint-specific.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
from typing import Optional

from superclaude.cli.pipeline.process import ClaudeProcess as _PipelineClaudeProcess

from .debug_logger import debug_log
from .models import Phase, SprintConfig

_dbg = logging.getLogger("superclaude.sprint.debug.process")


class ClaudeProcess(_PipelineClaudeProcess):
    """Sprint-specific claude process extending the pipeline base.

    Preserves the sprint (config, phase) constructor, build_prompt(),
    and debug logging while inheriting command building from pipeline.
    """

    def __init__(self, config: SprintConfig, phase: Phase):
        self.config = config
        self.phase = phase
        prompt = self.build_prompt()
        super().__init__(
            prompt=prompt,
            output_file=config.output_file(phase),
            error_file=config.error_file(phase),
            max_turns=config.max_turns,
            model=config.model,
            permission_flag=config.permission_flag,
            timeout_seconds=config.max_turns * 120 + 300,
            output_format="stream-json",
        )

    def build_prompt(self) -> str:
        """Build the /sc:task-unified prompt for this phase."""
        pn = self.phase.number
        result_file = self.config.result_file(self.phase)
        phase_file = self.phase.file

        return (
            f"/sc:task-unified Execute all tasks in @{phase_file} "
            f"--compliance strict --strategy systematic\n"
            f"\n"
            f"## Execution Rules\n"
            f"- Execute tasks in order (T{pn:02d}XX.01, T{pn:02d}XX.02, etc.)\n"
            f"- For STRICT tier tasks: use Sequential MCP for analysis, "
            f"run quality verification\n"
            f"- For STANDARD tier tasks: run direct test execution per "
            f"acceptance criteria\n"
            f"- For LIGHT tier tasks: quick sanity check only\n"
            f"- For EXEMPT tier tasks: skip formal verification\n"
            f"- If a STRICT-tier task fails, STOP and report -- "
            f"do not continue to next task\n"
            f"- For all other tier failures, log the failure and continue\n"
            f"\n"
            f"## Completion Protocol\n"
            f"When ALL tasks in this phase are complete "
            f"(or halted on STRICT failure):\n"
            f"1. Write a phase completion report to {result_file} containing:\n"
            f"   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), "
            f"tasks_total, tasks_passed, tasks_failed\n"
            f"   - Per-task status table: Task ID, Title, Tier, Status "
            f"(pass/fail/skip), Evidence\n"
            f"   - Files modified (list all paths)\n"
            f"   - Blockers for next phase (if any)\n"
            f"   - The literal string EXIT_RECOMMENDATION: CONTINUE "
            f"or EXIT_RECOMMENDATION: HALT\n"
            f"2. If any task produced file changes, list them under "
            f"## Files Modified\n"
            f"\n"
            f"## Important\n"
            f"- This is Phase {pn} of a multi-phase sprint\n"
            f"- Previous phases have already been executed in separate sessions\n"
            f"- Do not re-execute work from prior phases\n"
            f"- Focus only on the tasks defined in the phase file"
        )

    def start(self) -> subprocess.Popen:
        """Launch the claude process with sprint debug logging."""
        output_file = self.config.output_file(self.phase)
        error_file = self.config.error_file(self.phase)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        self._stdout_fh = open(output_file, "w")
        self._stderr_fh = open(error_file, "w")

        popen_kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": self._stdout_fh,
            "stderr": self._stderr_fh,
            "env": self.build_env(),
        }
        if hasattr(os, "setpgrp"):
            popen_kwargs["preexec_fn"] = os.setpgrp

        self._process = subprocess.Popen(self.build_command(), **popen_kwargs)

        debug_log(
            _dbg,
            "spawn",
            pid=self._process.pid,
            cmd=str(self.build_command()[:3]),
            phase=self.phase.number,
        )
        debug_log(
            _dbg,
            "files_opened",
            stdout=str(output_file),
            stderr=str(error_file),
        )

        return self._process

    def wait(self) -> int:
        """Wait for the process with timeout. Returns exit code."""
        try:
            self._process.wait(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            self.terminate()
            return 124

        self._close_handles()
        return self._process.returncode if self._process.returncode is not None else -1

    def terminate(self):
        """Graceful shutdown: SIGTERM, wait 10s, then SIGKILL."""
        if self._process is None or self._process.poll() is not None:
            self._close_handles()
            return

        use_pgroup = all(hasattr(os, attr) for attr in ("getpgid", "killpg"))
        pgid = os.getpgid(self._process.pid) if use_pgroup else None

        try:
            if use_pgroup and pgid is not None:
                os.killpg(pgid, signal.SIGTERM)
            else:
                self._process.terminate()
            debug_log(_dbg, "signal_sent", signal="SIGTERM", pid=self._process.pid)
        except ProcessLookupError:
            self._close_handles()
            return

        try:
            self._process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                if use_pgroup and pgid is not None:
                    os.killpg(pgid, signal.SIGKILL)
                else:
                    self._process.kill()
                debug_log(_dbg, "signal_sent", signal="SIGKILL", pid=self._process.pid)
                self._process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass

        rc = self._process.returncode
        debug_log(
            _dbg,
            "exit",
            pid=self._process.pid,
            code=rc,
            was_timeout=(rc == 124 or getattr(self, "_timed_out", False)),
        )
        self._close_handles()

    def _close_handles(self):
        for fh in (self._stdout_fh, self._stderr_fh):
            if fh is not None:
                try:
                    fh.close()
                except Exception:
                    pass


class SignalHandler:
    """Register signal handlers for graceful sprint shutdown.

    On SIGINT/SIGTERM:
    1. Set the shutdown flag (checked by the executor loop)
    2. The executor terminates the current claude process
    3. Writes partial execution log
    4. Exits with appropriate code
    """

    def __init__(self):
        self.shutdown_requested = False
        self._original_sigint = None
        self._original_sigterm = None

    def install(self):
        """Install signal handlers."""
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handle)
        signal.signal(signal.SIGTERM, self._handle)

    def uninstall(self):
        """Restore original signal handlers."""
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm is not None:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle(self, signum, frame):
        self.shutdown_requested = True
