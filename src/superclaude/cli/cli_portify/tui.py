"""Rich TUI live dashboard for cli-portify pipeline.

Renders real-time pipeline execution state: step progress, gate state,
timing, convergence iteration, review pause prompts, and warnings.

Degrades gracefully in non-terminal environments by falling back to
simple line-based output.

Per D-0035 / R-024: TUI rendering for operational visibility.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import Any

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:  # pragma: no cover
    HAS_RICH = False

from superclaude.cli.cli_portify.models import PortifyStatus


# --- Step definitions for display ---

PIPELINE_STEPS = [
    ("validate-config", 1, "EXEMPT"),
    ("discover-components", 1, "STANDARD"),
    ("analyze-workflow", 2, "STRICT"),
    ("design-pipeline", 2, "STRICT"),
    ("synthesize-spec", 3, "STRICT"),
    ("brainstorm-gaps", 4, "STANDARD"),
    ("panel-review", 4, "STRICT"),
]

_STATUS_STYLES = {
    "pending": ("dim", "..."),
    "running": ("bold yellow", ">>>"),
    "pass": ("bold green", "OK"),
    "fail": ("bold red", "FAIL"),
    "timeout": ("bold red", "TOUT"),
    "skipped": ("dim", "SKIP"),
    "error": ("bold red", "ERR"),
}


@dataclass
class StepDisplayState:
    """Display state for a single pipeline step."""

    name: str
    phase: int
    gate_tier: str
    status: str = "pending"
    duration_seconds: float = 0.0
    gate_result: str = ""
    iteration: int = 0
    warning: str = ""


@dataclass
class DashboardState:
    """Aggregate dashboard state for TUI rendering."""

    steps: list[StepDisplayState] = field(default_factory=list)
    total_elapsed: float = 0.0
    current_step: str = ""
    current_iteration: int = 0
    review_paused: bool = False
    review_prompt: str = ""
    warnings: list[str] = field(default_factory=list)
    pipeline_start: float = 0.0

    def __post_init__(self) -> None:
        if not self.steps:
            self.steps = [
                StepDisplayState(name=name, phase=phase, gate_tier=tier)
                for name, phase, tier in PIPELINE_STEPS
            ]

    def update_step(
        self,
        step_name: str,
        *,
        status: str | None = None,
        duration: float | None = None,
        gate_result: str | None = None,
        iteration: int | None = None,
        warning: str | None = None,
    ) -> None:
        """Update a step's display state."""
        for step in self.steps:
            if step.name == step_name:
                if status is not None:
                    step.status = status
                if duration is not None:
                    step.duration_seconds = duration
                if gate_result is not None:
                    step.gate_result = gate_result
                if iteration is not None:
                    step.iteration = iteration
                if warning is not None:
                    step.warning = warning
                break

    def mark_running(self, step_name: str) -> None:
        self.current_step = step_name
        self.update_step(step_name, status="running")

    def mark_complete(
        self, step_name: str, status: str, duration: float, gate_result: str = ""
    ) -> None:
        self.update_step(
            step_name, status=status, duration=duration, gate_result=gate_result
        )
        if self.current_step == step_name:
            self.current_step = ""

    def set_review_pause(self, prompt: str) -> None:
        self.review_paused = True
        self.review_prompt = prompt

    def clear_review_pause(self) -> None:
        self.review_paused = False
        self.review_prompt = ""

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def compute_elapsed(self) -> None:
        if self.pipeline_start > 0:
            self.total_elapsed = time.time() - self.pipeline_start


def _build_dashboard_table(state: DashboardState) -> Table:
    """Build a Rich Table from the current dashboard state."""
    table = Table(
        title="cli-portify pipeline",
        show_header=True,
        header_style="bold",
        expand=False,
        min_width=60,
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Step", min_width=22)
    table.add_column("Status", width=6, justify="center")
    table.add_column("Gate", width=6, justify="center")
    table.add_column("Time", width=8, justify="right")
    table.add_column("Info", min_width=12)

    for i, step in enumerate(state.steps, 1):
        style, label = _STATUS_STYLES.get(step.status, ("dim", "?"))

        gate_text = step.gate_result or "-"
        gate_style = "green" if gate_text == "pass" else "red" if gate_text == "fail" else "dim"

        dur = f"{step.duration_seconds:.1f}s" if step.duration_seconds > 0 else "-"

        info_parts: list[str] = []
        if step.iteration > 0:
            info_parts.append(f"iter={step.iteration}")
        if step.warning:
            info_parts.append(step.warning)
        info = " ".join(info_parts) if info_parts else ""

        table.add_row(
            str(i),
            step.name,
            Text(label, style=style),
            Text(gate_text, style=gate_style),
            dur,
            info,
        )

    # Footer with total elapsed
    table.add_section()
    elapsed_str = f"{state.total_elapsed:.1f}s"
    table.add_row("", "Total elapsed", "", "", elapsed_str, "")

    return table


class TuiDashboard:
    """Rich TUI live dashboard for pipeline execution.

    Renders a live-updating table showing step progress, gate results,
    timing, iteration count, and warnings. Pauses display for review
    gate prompts.

    Falls back to simple stderr line output in non-terminal environments.
    """

    def __init__(self, state: DashboardState | None = None) -> None:
        self._state = state or DashboardState()
        self._live: Live | None = None
        self._console: Console | None = None
        self._is_terminal = HAS_RICH and hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    @property
    def state(self) -> DashboardState:
        return self._state

    @property
    def is_live(self) -> bool:
        return self._live is not None

    def start(self) -> None:
        """Start the live dashboard display."""
        self._state.pipeline_start = time.time()
        if not self._is_terminal:
            return
        self._console = Console(stderr=True)
        self._live = Live(
            _build_dashboard_table(self._state),
            console=self._console,
            refresh_per_second=2,
            transient=True,
        )
        self._live.start()

    def stop(self) -> None:
        """Stop the live dashboard and print final state."""
        self._state.compute_elapsed()
        if self._live is not None:
            self._live.stop()
            self._live = None
        if self._console is not None:
            self._console.print(_build_dashboard_table(self._state))

    def refresh(self) -> None:
        """Refresh the live display with current state."""
        self._state.compute_elapsed()
        if self._live is not None:
            self._live.update(_build_dashboard_table(self._state))
        elif not self._is_terminal and self._state.current_step:
            _fallback_status(self._state)

    def step_start(self, step_name: str) -> None:
        """Mark a step as running and refresh."""
        self._state.mark_running(step_name)
        self.refresh()

    def step_complete(
        self, step_name: str, status: str, duration: float, gate_result: str = ""
    ) -> None:
        """Mark a step as complete and refresh."""
        self._state.mark_complete(step_name, status, duration, gate_result)
        self.refresh()

    def set_iteration(self, step_name: str, iteration: int) -> None:
        """Update the iteration counter for a step."""
        self._state.update_step(step_name, iteration=iteration)
        self._state.current_iteration = iteration
        self.refresh()

    def pause_for_review(self, prompt: str) -> None:
        """Pause the live display for a review gate prompt."""
        self._state.set_review_pause(prompt)
        if self._live is not None:
            self._live.stop()
            self._live = None

    def resume_after_review(self) -> None:
        """Resume the live display after review gate completes."""
        self._state.clear_review_pause()
        if self._is_terminal and self._console is not None:
            self._live = Live(
                _build_dashboard_table(self._state),
                console=self._console,
                refresh_per_second=2,
                transient=True,
            )
            self._live.start()

    def add_warning(self, warning: str) -> None:
        """Add a warning to the dashboard."""
        self._state.add_warning(warning)
        self.refresh()


def _fallback_status(state: DashboardState) -> None:
    """Print simple status line for non-terminal environments."""
    step = state.current_step
    elapsed = f"{state.total_elapsed:.1f}s"
    print(f"[portify] {step} running... ({elapsed})", file=sys.stderr)
