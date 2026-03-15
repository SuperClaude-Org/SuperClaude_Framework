"""Sprint TUI — Rich-based terminal dashboard for sprint execution."""

from __future__ import annotations

import logging
from typing import Optional

from rich.console import Console
from rich.console import Group as RichGroup
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from .debug_logger import debug_log
from .models import (
    GateDisplayState,
    MonitorState,
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintResult,
)

_dbg = logging.getLogger("superclaude.sprint.debug.tui")

STATUS_STYLES = {
    PhaseStatus.PASS: "bold green",
    PhaseStatus.PASS_NO_SIGNAL: "green",
    PhaseStatus.PASS_NO_REPORT: "green",
    PhaseStatus.PASS_RECOVERED: "green",
    PhaseStatus.INCOMPLETE: "bold red",
    PhaseStatus.HALT: "bold red",
    PhaseStatus.TIMEOUT: "bold red",
    PhaseStatus.ERROR: "bold red",
    PhaseStatus.RUNNING: "bold yellow",
    PhaseStatus.PENDING: "dim",
    PhaseStatus.SKIPPED: "dim strikethrough",
}

STATUS_ICONS = {
    PhaseStatus.PASS: "[green]PASS[/]",
    PhaseStatus.PASS_NO_SIGNAL: "[green]PASS[/]",
    PhaseStatus.PASS_NO_REPORT: "[green]PASS[/]",
    PhaseStatus.PASS_RECOVERED: "[green]PASS✓[/]",
    PhaseStatus.INCOMPLETE: "[red]INCOMPLETE[/]",
    PhaseStatus.HALT: "[red]HALT[/]",
    PhaseStatus.TIMEOUT: "[red]TIMEOUT[/]",
    PhaseStatus.ERROR: "[red]ERROR[/]",
    PhaseStatus.RUNNING: "[yellow]RUNNING[/]",
    PhaseStatus.PENDING: "[dim]pending[/]",
    PhaseStatus.SKIPPED: "[dim]skipped[/]",
}


class SprintTUI:
    """Rich-based terminal UI for sprint execution."""

    def __init__(self, config: SprintConfig, console: Console | None = None):
        self.config = config
        self.console = console or Console()
        self.sprint_result: Optional[SprintResult] = None
        self.monitor_state = MonitorState()
        self.current_phase: Optional[Phase] = None
        self._live: Optional[Live] = None
        self._live_failed: bool = False
        # Per-phase gate display state; updated via update() by executor.
        # Only rendered when grace_period > 0 (trailing gates enabled).
        self.gate_states: dict[int, GateDisplayState] = {}
        self._show_gate_column: bool = getattr(config, "grace_period", 0) > 0  # silences future updates after first render error

    def start(self) -> Live:
        """Start the Live display and return it for the executor to use."""
        debug_log(_dbg, "tui_start")
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=2,
            screen=False,
        )
        self._live.start()
        return self._live

    def stop(self):
        """Stop the Live display."""
        debug_log(_dbg, "tui_stop")
        if self._live:
            self._live.stop()

    def update(
        self,
        sprint_result: SprintResult,
        monitor_state: MonitorState,
        current_phase: Optional[Phase],
    ):
        """Called by the executor to refresh the display.

        Rendering errors (terminal resize race, broken pipe, etc.) are caught
        so a display glitch cannot abort the running sprint.
        """
        self.sprint_result = sprint_result
        self.monitor_state = monitor_state
        self.current_phase = current_phase
        if self._live and not self._live_failed:
            try:
                self._live.update(self._render())
                debug_log(
                    _dbg,
                    "tui_update",
                    events_received=monitor_state.events_received,
                    stall_status=monitor_state.stall_status,
                    last_event_time=round(monitor_state.last_event_time, 1),
                )
            except Exception as exc:
                import sys
                self._live_failed = True
                debug_log(_dbg, "tui_live_failed", error=str(exc), error_type=type(exc).__name__)
                print(f"[TUI] Display error (continuing sprint): {exc}", file=sys.stderr)

    def _render(self) -> Panel:
        """Build the complete TUI layout."""
        header = self._build_header()
        table = self._build_phase_table()
        progress = self._build_progress()
        detail = self._build_active_panel()

        body = RichGroup(header, "", table, "", progress, "", detail)

        return Panel(
            body,
            title="[bold]SUPERCLAUDE SPRINT RUNNER[/]",
            border_style="blue",
            padding=(1, 2),
        )

    def _build_header(self) -> Text:
        elapsed = self.sprint_result.duration_display if self.sprint_result else "0s"
        index_name = self.config.index_path.parent.name
        return Text.from_markup(
            f"[dim]{index_name}[/]    Elapsed: [bold]{elapsed}[/]"
        )

    def _build_phase_table(self) -> Table:
        table = Table(
            show_header=True,
            header_style="bold",
            border_style="dim",
            pad_edge=False,
            box=None,
        )
        table.add_column("#", width=3, justify="right")
        table.add_column("Phase", min_width=30)
        table.add_column("Status", width=12, justify="center")
        if self._show_gate_column:
            table.add_column("Gate", width=6, justify="center")
        table.add_column("Duration", width=10, justify="right")
        table.add_column("Tasks", width=8, justify="center")

        if not self.sprint_result:
            return table

        for phase in self.config.active_phases:
            result = next(
                (
                    r
                    for r in self.sprint_result.phase_results
                    if r.phase.number == phase.number
                ),
                None,
            )
            status = result.status if result else PhaseStatus.PENDING
            if phase == self.current_phase and not (result and result.status.is_terminal):
                status = PhaseStatus.RUNNING

            style = STATUS_STYLES[status]
            duration = (
                result.duration_display
                if result and status.is_terminal
                else (
                    f"{int(self.monitor_state.stall_seconds)}s"
                    if status == PhaseStatus.RUNNING
                    else "-"
                )
            )
            tasks = f"{result.last_task_id}" if result else "-"

            row: list[str] = [
                str(phase.number),
                phase.display_name,
                STATUS_ICONS.get(status, str(status.value)),
            ]
            if self._show_gate_column:
                gate_state = self.gate_states.get(phase.number, GateDisplayState.NONE)
                row.append(gate_state.icon)
            row.extend([duration, tasks])

            table.add_row(
                *row,
                style=style if status == PhaseStatus.PENDING else "",
            )

        return table

    def _build_progress(self) -> Progress:
        """Overall sprint progress bar."""
        progress = Progress(
            TextColumn("[bold]Progress"),
            BarColumn(bar_width=40),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("[dim]{task.completed}/{task.total} tasks[/]"),
        )
        total = len(self.config.active_phases)
        done = self.sprint_result.phases_passed if self.sprint_result else 0
        progress.add_task("sprint", total=total, completed=done)
        return progress

    def _build_active_panel(self) -> Panel:
        """Detail panel for the currently-running phase."""
        if not self.current_phase:
            # Terminal state
            if self.sprint_result and self.sprint_result.finished_at:
                return self._build_terminal_panel()
            return Panel("[dim]Waiting...[/]", title="Active Phase")

        ms = self.monitor_state
        stall_display = ms.stall_status
        stall_style = (
            "bold red blink"
            if stall_display == "STALLED"
            else "yellow"
            if stall_display == "thinking..."
            else "green"
        )

        lines = [
            f"File:    {self.current_phase.basename}",
            f"Status:  RUNNING -- [{stall_style}]{stall_display}[/]",
            "",
            f"Last task:     {ms.last_task_id or '-'}",
            f"Last tool:     {ms.last_tool_used or '-'}",
            f"Output size:   {ms.output_size_display}  (+{ms.growth_rate_bps:.1f} B/s)",
            f"Files changed: {ms.files_changed}",
        ]

        return Panel(
            "\n".join(lines),
            title=f"[bold yellow]ACTIVE: Phase {self.current_phase.number}[/]",
            border_style="yellow",
        )

    def _build_terminal_panel(self) -> Panel:
        """Build the final state panel (complete or halted)."""
        sr = self.sprint_result
        if sr.outcome.value == "success":
            content = (
                f"Result:  [bold green]ALL PHASES PASSED[/]\n"
                f"Log:     {self.config.execution_log_md}"
            )
            return Panel(content, title="[bold green]Sprint Complete[/]", border_style="green")
        else:
            lines = [
                f"Result:  [bold red]{sr.outcome.value.upper()}[/]"
            ]
            if sr.halt_phase:
                lines.append(f"Halted at Phase {sr.halt_phase}")
            resume = sr.resume_command()
            if resume:
                lines.append(f"\nResume:  [bold]{resume}[/]")
            content = "\n".join(lines)
            return Panel(content, title="[bold red]Sprint Halted[/]", border_style="red")
