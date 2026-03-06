"""Sprint process management — subprocess lifecycle and signal handling.

ClaudeProcess extends pipeline.process.ClaudeProcess with sprint-specific
constructor (config, phase) and build_prompt(). Lifecycle hooks delegate
debug logging to factory closures, eliminating method overrides.
SignalHandler remains sprint-specific.
"""

from __future__ import annotations

import logging
import signal
from typing import Optional

from superclaude.cli.pipeline.process import ClaudeProcess as _PipelineClaudeProcess

from .debug_logger import debug_log
from .models import Phase, SprintConfig

_dbg = logging.getLogger("superclaude.sprint.debug.process")


def _make_spawn_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_spawn closure for sprint debug logging.

    Captures phase number and config output/error paths so the hook
    can log spawn and files_opened events with full context.
    """
    output_file = config.output_file(phase)
    error_file = config.error_file(phase)
    phase_number = phase.number

    def on_spawn(pid: int) -> None:
        debug_log(
            _dbg,
            "spawn",
            pid=pid,
            cmd="['claude', '--print', '--verbose']",
            phase=phase_number,
        )
        debug_log(
            _dbg,
            "files_opened",
            stdout=str(output_file),
            stderr=str(error_file),
        )

    return on_spawn


def _make_signal_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_signal closure for sprint debug logging.

    Logs signal_sent events with the signal name and process id.
    """

    def on_signal(pid: int, signal_name: str) -> None:
        debug_log(_dbg, "signal_sent", signal=signal_name, pid=pid)

    return on_signal


def _make_exit_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_exit closure for sprint debug logging.

    Logs exit events with pid, return code, and timeout detection.
    """

    def on_exit(pid: int, returncode: int | None) -> None:
        debug_log(
            _dbg,
            "exit",
            pid=pid,
            code=returncode,
            was_timeout=(returncode == 124),
        )

    return on_exit


class ClaudeProcess(_PipelineClaudeProcess):
    """Sprint-specific claude process extending the pipeline base.

    Defines only __init__ (with hook wiring) and build_prompt().
    All subprocess lifecycle (start, wait, terminate) is inherited
    from the pipeline base class; sprint debug logging is injected
    via lifecycle hook factories.
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
            on_spawn=_make_spawn_hook(phase, config),
            on_signal=_make_signal_hook(phase, config),
            on_exit=_make_exit_hook(phase, config),
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
