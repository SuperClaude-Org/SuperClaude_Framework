"""Sprint logging — dual-format JSONL + Markdown execution logs."""

from __future__ import annotations

import json

from rich.console import Console

from .models import PhaseResult, SprintConfig, SprintResult


class SprintLogger:
    """Dual-format sprint logger: JSONL (machine) + Markdown (human).

    Log levels:
    - DEBUG: JSONL file only
    - INFO:  JSONL + Markdown + screen
    - WARN:  JSONL + Markdown + screen (highlighted)
    - ERROR: JSONL + Markdown + screen (highlighted) + terminal bell
    """

    def __init__(self, config: SprintConfig):
        self.config = config
        self.console = Console(stderr=True)  # TUI uses stdout
        config.results_dir.mkdir(parents=True, exist_ok=True)

    def write_header(self, sprint: SprintResult):
        """Write sprint header to both log formats."""
        # JSONL
        self._jsonl(
            {
                "event": "sprint_start",
                "timestamp": sprint.started_at.isoformat(),
                "index": str(self.config.index_path),
                "phases": f"{self.config.start_phase}-"
                f"{self.config.end_phase or 'last'}",
                "max_turns": self.config.max_turns,
                "model": self.config.model or "default",
            }
        )

        # Markdown
        end = self.config.end_phase or max(p.number for p in self.config.phases)
        md = [
            "# Sprint Execution Log",
            "",
            f"**Started**: {sprint.started_at.isoformat()}",
            f"**Index**: {self.config.index_path}",
            f"**Phases**: {self.config.start_phase}--{end}",
            f"**Max turns**: {self.config.max_turns}",
            f"**Model**: {self.config.model or 'default'}",
            "",
            "| Phase | Status | Started | Completed | Duration | Exit |",
            "|-------|--------|---------|-----------|----------|------|",
        ]
        self.config.execution_log_md.write_text("\n".join(md) + "\n")

    def write_phase_start(self, phase, started_at):
        """Log phase start transition (RUNNING)."""
        self._jsonl(
            {
                "event": "phase_start",
                "phase": phase.number,
                "phase_name": phase.display_name,
                "phase_file": str(phase.file),
                "timestamp": started_at.isoformat(),
            }
        )

    def write_phase_interrupt(self, phase, started_at, finished_at, exit_code: int):
        """Log a phase that was interrupted mid-execution by a signal.

        Balances the phase_start event so the JSONL log has a closing event
        for every opening phase_start event.
        """
        self._jsonl(
            {
                "event": "phase_interrupt",
                "phase": phase.number,
                "phase_name": phase.display_name,
                "started_at": started_at.isoformat(),
                "interrupted_at": finished_at.isoformat(),
                "duration_seconds": (finished_at - started_at).total_seconds(),
                "exit_code": exit_code,
            }
        )

    def write_phase_result(self, result: PhaseResult):
        """Log a phase completion."""
        # JSONL
        self._jsonl(
            {
                "event": "phase_complete",
                "phase": result.phase.number,
                "phase_name": result.phase.display_name,
                "status": result.status.value,
                "exit_code": result.exit_code,
                "started_at": result.started_at.isoformat(),
                "finished_at": result.finished_at.isoformat(),
                "duration_seconds": result.duration_seconds,
                "output_bytes": result.output_bytes,
                "error_bytes": result.error_bytes,
                "last_task_id": result.last_task_id,
                "files_changed": result.files_changed,
            }
        )

        # Markdown (append row)
        row = (
            f"| Phase {result.phase.number} "
            f"| {result.status.value} "
            f"| {result.started_at.isoformat()} "
            f"| {result.finished_at.isoformat()} "
            f"| {result.duration_display} "
            f"| {result.exit_code} |"
        )
        with open(self.config.execution_log_md, "a") as f:
            f.write(row + "\n")

        # Screen output for important events
        if result.status.is_failure:
            self._screen_error(
                f"Phase {result.phase.number}: {result.status.value} "
                f"({result.duration_display})"
            )
        elif result.status.is_success:
            self._screen_info(
                f"Phase {result.phase.number}: {result.status.value} "
                f"({result.duration_display})"
            )

    def write_summary(self, sprint: SprintResult):
        """Write sprint summary to both logs."""
        self._jsonl(
            {
                "event": "sprint_complete",
                "outcome": sprint.outcome.value,
                "duration_seconds": sprint.duration_seconds,
                "phases_passed": sprint.phases_passed,
                "phases_failed": sprint.phases_failed,
                "halt_phase": sprint.halt_phase,
            }
        )

        with open(self.config.execution_log_md, "a") as f:
            f.write(f"\n**Outcome**: {sprint.outcome.value}\n")
            f.write(f"**Total duration**: {sprint.duration_display}\n")
            if sprint.halt_phase:
                f.write(f"**Halted at**: Phase {sprint.halt_phase}\n")
                f.write(f"**Resume**: `{sprint.resume_command()}`\n")

    def _jsonl(self, data: dict):
        with open(self.config.execution_log_jsonl, "a") as f:
            f.write(json.dumps(data, default=str) + "\n")

    def _screen_info(self, msg: str):
        self.console.print(f"[green][INFO][/] {msg}")

    def _screen_warn(self, msg: str):
        self.console.print(f"[yellow][WARN][/] {msg}")

    def _screen_error(self, msg: str):
        self.console.print(f"[bold red][ERROR][/] {msg}\a")  # \a = terminal bell


def read_status_from_log():
    """Read and display sprint status from execution log. (Stub)"""
    import click

    click.echo("Status command not yet connected to active sprint.")


def tail_log(lines: int = 50, follow: bool = False):
    """Tail the execution log. (Stub)"""
    import click

    click.echo("Logs command not yet connected to active sprint.")
