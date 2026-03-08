"""Cleanup Audit TUI — Rich-based terminal dashboard for audit execution.

Follows the sprint TUI pattern with audit-specific status styles and display fields.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.console import Group as RichGroup
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from .models import (
    CleanupAuditConfig,
    CleanupAuditMonitorState,
    CleanupAuditStatus,
    CleanupAuditStep,
)

STATUS_STYLES = {
    CleanupAuditStatus.PASS: "bold green",
    CleanupAuditStatus.PASS_NO_SIGNAL: "green",
    CleanupAuditStatus.PASS_NO_REPORT: "green",
    CleanupAuditStatus.INCOMPLETE: "bold red",
    CleanupAuditStatus.HALT: "bold red",
    CleanupAuditStatus.TIMEOUT: "bold red",
    CleanupAuditStatus.ERROR: "bold red",
    CleanupAuditStatus.RUNNING: "bold yellow",
    CleanupAuditStatus.PENDING: "dim",
    CleanupAuditStatus.SKIPPED: "dim strikethrough",
}

STATUS_ICONS = {
    CleanupAuditStatus.PASS: "[green]PASS[/]",
    CleanupAuditStatus.PASS_NO_SIGNAL: "[green]PASS[/]",
    CleanupAuditStatus.PASS_NO_REPORT: "[green]PASS[/]",
    CleanupAuditStatus.INCOMPLETE: "[red]INCOMPLETE[/]",
    CleanupAuditStatus.HALT: "[red]HALT[/]",
    CleanupAuditStatus.TIMEOUT: "[red]TIMEOUT[/]",
    CleanupAuditStatus.ERROR: "[red]ERROR[/]",
    CleanupAuditStatus.RUNNING: "[yellow]RUNNING[/]",
    CleanupAuditStatus.PENDING: "[dim]pending[/]",
    CleanupAuditStatus.SKIPPED: "[dim]skipped[/]",
}


class CleanupAuditTUI:
    """Rich-based terminal UI for cleanup audit execution."""

    def __init__(self, config: CleanupAuditConfig, console: Console | None = None):
        self.config = config
        self.console = console or Console()
        self.current_step: Optional[CleanupAuditStep] = None
        self.monitor_state = CleanupAuditMonitorState()
        self._live: Optional[Live] = None
        self._live_failed: bool = False

    def start(self) -> Live:
        """Start the Live display."""
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
        if self._live:
            self._live.stop()

    def update(
        self,
        current_step: CleanupAuditStep,
        monitor_state: CleanupAuditMonitorState,
    ):
        """Called by the executor to refresh the display."""
        self.current_step = current_step
        self.monitor_state = monitor_state
        if self._live and not self._live_failed:
            try:
                self._live.update(self._render())
            except Exception:
                self._live_failed = True

    def _render(self) -> Panel:
        """Build the complete TUI layout."""
        header = self._build_header()
        detail = self._build_active_panel()

        body = RichGroup(header, "", detail)

        return Panel(
            body,
            title="[bold]CLEANUP AUDIT RUNNER[/]",
            border_style="blue",
            padding=(1, 2),
        )

    def _build_header(self) -> Text:
        target = str(self.config.target_path)
        return Text.from_markup(
            f"[dim]Target: {target}[/]    "
            f"Pass: [bold]{self.config.pass_selection}[/]    "
            f"Focus: [bold]{self.config.focus}[/]"
        )

    def _build_active_panel(self) -> Panel:
        """Detail panel for the currently-running step."""
        if not self.current_step:
            return Panel("[dim]Waiting...[/]", title="Active Step")

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
            f"Step:    {self.current_step.id} ({self.current_step.pass_type.value})",
            f"Agent:   {self.current_step.agent_type or 'default'}",
            f"Status:  RUNNING -- [{stall_style}]{stall_display}[/]",
            "",
            f"Last task:     {ms.last_task_id or '-'}",
            f"Last tool:     {ms.last_tool_used or '-'}",
            f"Output size:   {ms.output_size_display}  (+{ms.growth_rate_bps:.1f} B/s)",
            f"Files changed: {ms.files_changed}",
        ]

        return Panel(
            "\n".join(lines),
            title=f"[bold yellow]ACTIVE: {self.current_step.id}[/]",
            border_style="yellow",
        )
