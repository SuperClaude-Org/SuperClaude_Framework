"""Pipeline process management -- subprocess lifecycle for claude -p invocations.

Extracted from sprint/process.py. This version is generic: it accepts
PipelineConfig-compatible parameters and an output_format flag.

  output_format="stream-json"  ->  Sprint backward-compatible (NDJSON on stdout)
  output_format="text"         ->  Roadmap gate-compatible (plain text)

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
from pathlib import Path
from typing import Callable, Optional

_log = logging.getLogger("superclaude.pipeline.process")


class ClaudeProcess:
    """Manages a single claude -p subprocess with signal handling.

    Uses process groups (os.setpgrp) so we can kill the entire
    child tree on shutdown. CLAUDECODE= env prefix prevents nested
    session detection. stdout/stderr redirected to files.

    Lifecycle hooks (all optional, default None):
      on_spawn(pid)           — called after Popen in start()
      on_signal(pid, signal)  — called before signal send in terminate()
      on_exit(pid, returncode)— called before _close_handles() in wait()/terminate()
    """

    def __init__(
        self,
        *,
        prompt: str,
        output_file: Path,
        error_file: Path,
        max_turns: int = 100,
        model: str = "",
        permission_flag: str = "--dangerously-skip-permissions",
        timeout_seconds: int = 6300,
        output_format: str = "stream-json",
        extra_args: list[str] | None = None,
        on_spawn: Callable[[int], None] | None = None,
        on_signal: Callable[[int, str], None] | None = None,
        on_exit: Callable[[int, int | None], None] | None = None,
    ):
        self.prompt = prompt
        self.output_file = output_file
        self.error_file = error_file
        self.max_turns = max_turns
        self.model = model
        self.permission_flag = permission_flag
        self.timeout_seconds = timeout_seconds
        self.output_format = output_format
        self.extra_args = extra_args or []
        self._on_spawn = on_spawn
        self._on_signal = on_signal
        self._on_exit = on_exit
        self._process: Optional[subprocess.Popen] = None
        self._stdout_fh = None
        self._stderr_fh = None

    def build_command(self) -> list[str]:
        """Build the claude CLI command."""
        cmd = [
            "claude",
            "--print",
            "--verbose",
            self.permission_flag,
            "--no-session-persistence",
            "--tools",
            "default",
            "--max-turns",
            str(self.max_turns),
            "--output-format",
            self.output_format,
            "-p",
            self.prompt,
        ]
        if self.model:
            cmd.extend(["--model", self.model])
        cmd.extend(self.extra_args)
        return cmd

    def build_env(self) -> dict[str, str]:
        """Build environment for the child process.

        Remove CLAUDECODE and CLAUDE_CODE_ENTRYPOINT to prevent
        nested-session detection in the child claude process.
        """
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)
        env.pop("CLAUDE_CODE_ENTRYPOINT", None)
        return env

    def start(self) -> subprocess.Popen:
        """Launch the claude process."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self._stdout_fh = open(self.output_file, "w")
        self._stderr_fh = open(self.error_file, "w")

        popen_kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": self._stdout_fh,
            "stderr": self._stderr_fh,
            "env": self.build_env(),
        }
        if hasattr(os, "setpgrp"):
            popen_kwargs["preexec_fn"] = os.setpgrp

        self._process = subprocess.Popen(self.build_command(), **popen_kwargs)

        if self._on_spawn is not None:
            self._on_spawn(self._process.pid)

        _log.debug(
            "spawn pid=%d cmd=%s",
            self._process.pid,
            str(self.build_command()[:3]),
        )

        return self._process

    def wait(self) -> int:
        """Wait for the process with timeout. Returns exit code."""
        try:
            self._process.wait(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            self.terminate()
            return 124  # match bash timeout exit code

        rc = self._process.returncode if self._process.returncode is not None else -1
        if self._on_exit is not None:
            self._on_exit(self._process.pid, rc)
        self._close_handles()
        return rc

    def terminate(self) -> None:
        """Graceful shutdown: SIGTERM, wait 10s, then SIGKILL."""
        if self._process is None or self._process.poll() is not None:
            self._close_handles()
            return

        use_pgroup = all(hasattr(os, attr) for attr in ("getpgid", "killpg"))
        pgid = os.getpgid(self._process.pid) if use_pgroup else None

        try:
            if self._on_signal is not None:
                self._on_signal(self._process.pid, "SIGTERM")
            if use_pgroup and pgid is not None:
                os.killpg(pgid, signal.SIGTERM)
            else:
                self._process.terminate()
            _log.debug("signal_sent SIGTERM pid=%d", self._process.pid)
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
                _log.debug("signal_sent SIGKILL pid=%d", self._process.pid)
                self._process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass

        _log.debug(
            "exit pid=%d code=%s",
            self._process.pid,
            self._process.returncode,
        )
        if self._on_exit is not None:
            self._on_exit(self._process.pid, self._process.returncode)
        self._close_handles()

    def _close_handles(self) -> None:
        for fh in (self._stdout_fh, self._stderr_fh):
            if fh is not None:
                try:
                    fh.close()
                except Exception:
                    pass
