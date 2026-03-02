# `superclaude sprint` -- Design Specification

**Version**: 1.0
**Date**: 2026-02-25
**Status**: Draft
**Replaces**: `.dev/releases/execute-sprint.sh`
**Target release**: SuperClaude v4.3.0

---

## 1. Module Architecture

```
src/superclaude/
  cli/
    main.py                   # Existing -- add `sprint` group import
    sprint/
      __init__.py             # Click group definition + subcommand registration
      commands.py             # Click commands: run, attach, status, logs, kill
      config.py               # SprintConfig, phase discovery, validation
      executor.py             # Core orchestration loop (run phases sequentially)
      monitor.py              # Sidecar thread: reads output file, extracts signals
      tui.py                  # Rich Live display: dashboard, active-phase panel
      tmux.py                 # Tmux session create/attach/status/layout
      process.py              # Subprocess management, signal handling, timeouts
      notify.py               # Desktop notifications (notify-send, osascript, bell)
      logging_.py             # Structured JSONL + human-readable markdown logs
      models.py               # All dataclasses and enums
```

### File Responsibilities

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `models.py` | ~180 | Pure data: Phase, SprintConfig, PhaseResult, SprintResult, MonitorState, enums |
| `config.py` | ~200 | Parse tasklist-index.md, discover phase files, validate, build SprintConfig |
| `commands.py` | ~250 | Click command group with `run`, `attach`, `status`, `logs`, `kill` subcommands |
| `executor.py` | ~300 | Main loop: iterate phases, launch subprocess, delegate to monitor, collect results |
| `monitor.py` | ~250 | Background thread: poll output file, extract task IDs, tool names, detect stalls |
| `tui.py` | ~350 | Rich Live layout: sprint dashboard table, active phase panel, progress bars |
| `tmux.py` | ~200 | Create/attach/query tmux sessions, build pane layout |
| `process.py` | ~180 | Popen wrapper, signal handler registration, graceful shutdown, process groups |
| `notify.py` | ~80 | Platform-detect and send desktop notifications |
| `logging_.py` | ~150 | JSONL writer, markdown summary writer, log-level filtering |
| `__init__.py` | ~20 | Exports the click group |

**Total**: ~2,160 lines estimated across 11 files.

---

## 2. Data Models

```python
# src/superclaude/cli/sprint/models.py

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class PhaseStatus(Enum):
    """Lifecycle of a single phase."""
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"

    @property
    def is_terminal(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
            PhaseStatus.HALT,
            PhaseStatus.TIMEOUT,
            PhaseStatus.ERROR,
            PhaseStatus.SKIPPED,
        )

    @property
    def is_success(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
        )

    @property
    def is_failure(self) -> bool:
        return self in (PhaseStatus.HALT, PhaseStatus.TIMEOUT, PhaseStatus.ERROR)


class SprintOutcome(Enum):
    """Final sprint result."""
    SUCCESS = "success"
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class Phase:
    """A single phase discovered from the tasklist index."""
    number: int
    file: Path
    name: str = ""  # extracted from phase file heading, or auto-generated

    @property
    def basename(self) -> str:
        return self.file.name

    @property
    def display_name(self) -> str:
        return self.name or f"Phase {self.number}"


@dataclass
class SprintConfig:
    """Complete configuration for a sprint execution."""
    index_path: Path
    release_dir: Path
    phases: list[Phase]
    start_phase: int = 1
    end_phase: int = 0  # 0 = auto-detect (last phase)
    max_turns: int = 50
    model: str = ""  # empty = claude default
    dry_run: bool = False
    permission_flag: str = "--dangerously-skip-permissions"
    tmux_session_name: str = ""

    @property
    def results_dir(self) -> Path:
        return self.release_dir / "results"

    @property
    def execution_log_jsonl(self) -> Path:
        return self.release_dir / "execution-log.jsonl"

    @property
    def execution_log_md(self) -> Path:
        return self.release_dir / "execution-log.md"

    @property
    def active_phases(self) -> list[Phase]:
        """Phases within the [start, end] range."""
        end = self.end_phase or max(p.number for p in self.phases)
        return [p for p in self.phases if self.start_phase <= p.number <= end]

    def output_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-output.txt"

    def error_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-errors.txt"

    def result_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-result.md"


@dataclass
class PhaseResult:
    """Outcome of executing a single phase."""
    phase: Phase
    status: PhaseStatus
    exit_code: int
    started_at: datetime
    finished_at: datetime
    output_bytes: int = 0
    error_bytes: int = 0
    last_task_id: str = ""
    files_changed: int = 0

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()

    @property
    def duration_display(self) -> str:
        s = int(self.duration_seconds)
        if s < 60:
            return f"{s}s"
        return f"{s // 60}m {s % 60}s"


@dataclass
class SprintResult:
    """Aggregate result for the entire sprint."""
    config: SprintConfig
    phase_results: list[PhaseResult] = field(default_factory=list)
    outcome: SprintOutcome = SprintOutcome.SUCCESS
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    halt_phase: Optional[int] = None

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    @property
    def duration_display(self) -> str:
        s = int(self.duration_seconds)
        if s < 3600:
            return f"{s // 60}m {s % 60}s"
        return f"{s // 3600}h {(s % 3600) // 60}m"

    @property
    def phases_passed(self) -> int:
        return sum(1 for r in self.phase_results if r.status.is_success)

    @property
    def phases_failed(self) -> int:
        return sum(1 for r in self.phase_results if r.status.is_failure)

    def resume_command(self) -> str:
        if self.halt_phase is not None:
            end = self.config.end_phase or max(
                p.number for p in self.config.phases
            )
            return (
                f"superclaude sprint run {self.config.index_path} "
                f"--start {self.halt_phase} --end {end}"
            )
        return ""


@dataclass
class MonitorState:
    """Real-time state extracted by the sidecar monitor thread."""
    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = field(default_factory=time.monotonic)
    last_task_id: str = ""
    last_tool_used: str = ""
    files_changed: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0  # bytes per second
    stall_seconds: float = 0.0

    @property
    def stall_status(self) -> str:
        if self.stall_seconds > 60:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str:
        if self.output_bytes < 1024:
            return f"{self.output_bytes} B"
        if self.output_bytes < 1024 * 1024:
            return f"{self.output_bytes / 1024:.1f} KB"
        return f"{self.output_bytes / (1024 * 1024):.1f} MB"
```

---

## 3. CLI Interface

The `sprint` subcommand plugs into the existing `superclaude` click group in `main.py`.

### 3.1 Integration Point

```python
# Addition to src/superclaude/cli/main.py

# After existing command definitions, before `if __name__`:
from superclaude.cli.sprint import sprint_group
main.add_command(sprint_group, name="sprint")
```

### 3.2 Sprint Command Group

```python
# src/superclaude/cli/sprint/commands.py

import click

@click.group("sprint")
def sprint_group():
    """Orchestrate multi-phase Claude Code sprint execution.

    Reads a tasklist-index.md, discovers phase files, and executes
    each phase as a fresh Claude Code session with strict compliance.
    Supports tmux for detachable long-running sprints.

    Examples:
        superclaude sprint run path/to/tasklist-index.md
        superclaude sprint run path/to/tasklist-index.md --start 3 --end 6
        superclaude sprint run path/to/tasklist-index.md --dry-run
        superclaude sprint attach
        superclaude sprint status
        superclaude sprint logs
        superclaude sprint kill
    """
    pass


@sprint_group.command()
@click.argument("index_path", type=click.Path(exists=True, path_type=Path))
@click.option("--start", "start_phase", type=int, default=1,
              help="Start from phase N (default: 1)")
@click.option("--end", "end_phase", type=int, default=0,
              help="End at phase N (default: last discovered)")
@click.option("--max-turns", type=int, default=50,
              help="Max agent turns per phase (default: 50)")
@click.option("--model", default="",
              help="Claude model to use (default: env CLAUDE_MODEL or claude default)")
@click.option("--dry-run", is_flag=True,
              help="Show discovered phases without executing")
@click.option("--no-tmux", is_flag=True,
              help="Run in foreground even if tmux is available")
@click.option("--permission-flag",
              type=click.Choice([
                  "--dangerously-skip-permissions",
                  "--allow-hierarchical-permissions",
              ]),
              default="--dangerously-skip-permissions",
              help="Permission flag for claude CLI")
def run(index_path, start_phase, end_phase, max_turns, model,
        dry_run, no_tmux, permission_flag):
    """Execute a sprint from a tasklist index.

    INDEX_PATH is the path to a tasklist-index.md file.

    Discovers phase files, validates they exist, then executes each
    phase sequentially in fresh Claude Code sessions. Results are
    written to a results/ directory alongside the index.

    By default, starts a tmux session so the sprint survives SSH
    disconnects. Use --no-tmux to run in the foreground.
    """
    from .config import load_sprint_config
    from .executor import execute_sprint
    from .tmux import is_tmux_available, launch_in_tmux

    config = load_sprint_config(
        index_path=index_path,
        start_phase=start_phase,
        end_phase=end_phase,
        max_turns=max_turns,
        model=model or os.environ.get("CLAUDE_MODEL", ""),
        dry_run=dry_run,
        permission_flag=permission_flag,
    )

    if dry_run:
        _print_dry_run(config)
        return

    # Tmux decision: use tmux unless --no-tmux or tmux unavailable
    if not no_tmux and is_tmux_available():
        launch_in_tmux(config)
    else:
        execute_sprint(config)


@sprint_group.command()
def attach():
    """Attach to a running sprint tmux session.

    Reconnects to the sc-sprint-* tmux session to see the
    live TUI dashboard.
    """
    from .tmux import attach_to_sprint


@sprint_group.command()
def status():
    """Show current sprint status without attaching.

    Reads the execution log to display phase completion
    status, timing, and current activity.
    """
    from .logging_ import read_status_from_log


@sprint_group.command()
@click.option("--lines", "-n", type=int, default=50,
              help="Number of lines to show (default: 50)")
@click.option("--follow", "-f", is_flag=True,
              help="Follow log output (like tail -f)")
def logs(lines, follow):
    """Tail the sprint execution log.

    Shows the human-readable execution log. Use -f to
    follow new output as it appears.
    """
    from .logging_ import tail_log


@sprint_group.command()
@click.option("--force", is_flag=True,
              help="Force kill without grace period")
def kill(force):
    """Stop a running sprint.

    Sends SIGTERM to the sprint process with a 10-second
    grace period, then SIGKILL if needed. Use --force
    to skip the grace period.
    """
    from .tmux import kill_sprint
```

### 3.3 Full CLI Help Tree

```
superclaude sprint --help
superclaude sprint run <index_path> [OPTIONS]
superclaude sprint attach
superclaude sprint status
superclaude sprint logs [-n 50] [-f]
superclaude sprint kill [--force]
```

---

## 4. TUI Layout Mockup

### 4.1 Sprint Dashboard -- All Phases Visible

This is what the user sees during execution. The top section is a persistent dashboard; the bottom is a live-updating detail panel for the active phase.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SUPERCLAUDE SPRINT RUNNER                         │
│            v2.02 Roadmap v3 -- Adversarial Pipeline                 │
│                   Elapsed: 47m 23s                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  # │ Phase                           │ Status    │ Duration │ Tasks  │
│ ───┼─────────────────────────────────┼───────────┼──────────┼─────── │
│  1 │ Pre-Implementation Gates        │ PASS      │   8m 12s │  4/4   │
│  2 │ Invocation Wiring Restoration   │ PASS      │  12m 45s │  2/2   │
│  3 │ Return Contract Transport       │ RUNNING   │  14m 02s │  3/5   │
│  4 │ Specification Rewrite           │ pending   │        - │  -/3   │
│  5 │ Post-Edit Sync & Quality Gates  │ pending   │        - │  -/4   │
│  6 │ E2E Validation & Acceptance     │ pending   │        - │  -/7   │
│ ───┼─────────────────────────────────┼───────────┼──────────┼─────── │
│    │ Overall: 2 done, 1 running, 3 pending       │  35m 00s │  9/25  │
│                                                                      │
│  Progress: ████████████░░░░░░░░░░░░░░░░░░░░░░░░░  33%  [6/25 tasks] │
│                                                                      │
├───────────────── ACTIVE: Phase 3 ────────────────────────────────────┤
│                                                                      │
│  File:   phase-3-tasklist.md                                         │
│  Status: RUNNING -- active                                           │
│                                                                      │
│  Last task:   T03.03                                                 │
│  Last tool:   Edit                                                   │
│  Output size: 847.3 KB  (+2.1 KB/s)                                 │
│  Files changed: 4                                                    │
│                                                                      │
│  Phase progress: ████████████████░░░░░░░░░  60%  [3/5 tasks]        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.2 State Variations

**Phase PASS (green row)**:
```
│  1 │ Pre-Implementation Gates        │ PASS      │   8m 12s │  4/4   │
```
Rendered with `style="green"` on the status cell and a green checkmark prefix.

**Phase FAIL / HALT (red row)**:
```
│  3 │ Return Contract Transport       │ HALT      │  18m 33s │  3/5   │
```
Rendered with `style="bold red"`. The active panel shows the failure reason.

**Phase pending (dim row)**:
```
│  4 │ Specification Rewrite           │ pending   │        - │  -/3   │
```
Rendered with `style="dim"`.

**Phase RUNNING (yellow row)**:
```
│  3 │ Return Contract Transport       │ RUNNING   │  14m 02s │  3/5   │
```
Rendered with `style="bold yellow"` and a spinner character.

**Stall Warning (>60s no growth)**:
```
├───────────────── ACTIVE: Phase 3 ────────────────────────────────────┤
│                                                                      │
│  File:   phase-3-tasklist.md                                         │
│  Status: RUNNING -- STALLED (78s no output)                          │
│                                                                      │
```
The "STALLED" text renders `style="bold red blink"`.

### 4.3 Sprint Complete State

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SUPERCLAUDE SPRINT RUNNER                         │
│            v2.02 Roadmap v3 -- Adversarial Pipeline                 │
│                   Total: 1h 23m 45s                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  # │ Phase                           │ Status    │ Duration │ Tasks  │
│ ───┼─────────────────────────────────┼───────────┼──────────┼─────── │
│  1 │ Pre-Implementation Gates        │ PASS      │   8m 12s │  4/4   │
│  2 │ Invocation Wiring Restoration   │ PASS      │  12m 45s │  2/2   │
│  3 │ Return Contract Transport       │ PASS      │  22m 18s │  5/5   │
│  4 │ Specification Rewrite           │ PASS      │  15m 33s │  3/3   │
│  5 │ Post-Edit Sync & Quality Gates  │ PASS      │   9m 07s │  4/4   │
│  6 │ E2E Validation & Acceptance     │ PASS      │  15m 50s │  7/7   │
│ ───┼─────────────────────────────────┼───────────┼──────────┼─────── │
│    │ SPRINT COMPLETE                             │ 1h 23m   │ 25/25  │
│                                                                      │
│  Progress: ████████████████████████████████████████ 100% [25/25]     │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Result:  ALL PHASES PASSED                                          │
│  Log:     .dev/releases/current/v2.02-Roadmap-v3/execution-log.md   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.4 Sprint Halted State

```
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Result:  HALTED at Phase 3 -- STRICT task T03.01 failed             │
│  Review:  results/phase-3-result.md                                  │
│                                                                      │
│  Resume:  superclaude sprint run tasklist-index.md --start 3         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.5 Rich API Mapping

```python
# src/superclaude/cli/sprint/tui.py

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

STATUS_STYLES = {
    PhaseStatus.PASS: "bold green",
    PhaseStatus.PASS_NO_SIGNAL: "green",
    PhaseStatus.PASS_NO_REPORT: "green",
    PhaseStatus.HALT: "bold red",
    PhaseStatus.TIMEOUT: "bold red",
    PhaseStatus.ERROR: "bold red",
    PhaseStatus.RUNNING: "bold yellow",
    PhaseStatus.PENDING: "dim",
    PhaseStatus.SKIPPED: "dim strikethrough",
}

STATUS_ICONS = {
    PhaseStatus.PASS: "[green]PASS[/]",
    PhaseStatus.HALT: "[red]HALT[/]",
    PhaseStatus.TIMEOUT: "[red]TIMEOUT[/]",
    PhaseStatus.ERROR: "[red]ERROR[/]",
    PhaseStatus.RUNNING: "[yellow]RUNNING[/]",
    PhaseStatus.PENDING: "[dim]pending[/]",
    PhaseStatus.SKIPPED: "[dim]skipped[/]",
}


class SprintTUI:
    """Rich-based terminal UI for sprint execution."""

    def __init__(self, config: SprintConfig):
        self.config = config
        self.console = Console()
        self.sprint_result: Optional[SprintResult] = None
        self.monitor_state = MonitorState()
        self.current_phase: Optional[Phase] = None
        self._live: Optional[Live] = None

    def start(self) -> Live:
        """Start the Live display and return it for the executor to use."""
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
        sprint_result: SprintResult,
        monitor_state: MonitorState,
        current_phase: Optional[Phase],
    ):
        """Called by the executor to refresh the display."""
        self.sprint_result = sprint_result
        self.monitor_state = monitor_state
        self.current_phase = current_phase
        if self._live:
            self._live.update(self._render())

    def _render(self) -> Panel:
        """Build the complete TUI layout."""
        # Header
        header = self._build_header()
        # Phase table
        table = self._build_phase_table()
        # Overall progress bar
        progress = self._build_progress()
        # Active phase detail panel
        detail = self._build_active_panel()

        from rich.console import Group as RichGroup
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
        table.add_column("Duration", width=10, justify="right")
        table.add_column("Tasks", width=8, justify="center")

        if not self.sprint_result:
            return table

        for phase in self.config.active_phases:
            result = next(
                (r for r in self.sprint_result.phase_results
                 if r.phase.number == phase.number),
                None,
            )
            status = result.status if result else PhaseStatus.PENDING
            style = STATUS_STYLES[status]
            duration = result.duration_display if result and status.is_terminal else (
                f"{int(self.monitor_state.stall_seconds)}s"
                if status == PhaseStatus.RUNNING else "-"
            )
            tasks = (
                f"{result.last_task_id}" if result else "-"
            )

            table.add_row(
                str(phase.number),
                phase.display_name,
                STATUS_ICONS.get(status, str(status.value)),
                duration,
                tasks,
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
        task_id = progress.add_task("sprint", total=total, completed=done)
        return progress

    def _build_active_panel(self) -> Panel:
        """Detail panel for the currently-running phase."""
        if not self.current_phase:
            return Panel("[dim]Waiting...[/]", title="Active Phase")

        ms = self.monitor_state
        stall_display = ms.stall_status
        stall_style = (
            "bold red blink" if stall_display == "STALLED"
            else "yellow" if stall_display == "thinking..."
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
```

---

## 5. Tmux Integration Design

### 5.1 Session Naming

Session name format: `sc-sprint-{release_dir_hash[:8]}` where `release_dir_hash` is the first 8 characters of the SHA-1 of the absolute release directory path. This allows multiple concurrent sprints on different release directories.

### 5.2 Tmux Pane Layout

```
┌─────────────────────────────────────────────┐
│                                             │
│              Rich TUI Dashboard             │
│         (superclaude sprint run ...)        │
│                                             │
│                                             │
│                                             │  ~75% height
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│ $ tail -f results/phase-3-output.txt        │  ~25% height
│ [raw claude output scrolling here]          │
│                                             │
└─────────────────────────────────────────────┘
```

### 5.3 Implementation

```python
# src/superclaude/cli/sprint/tmux.py

import hashlib
import shutil
import subprocess
from pathlib import Path


def is_tmux_available() -> bool:
    """Check if tmux is installed and we are not already inside tmux."""
    if shutil.which("tmux") is None:
        return False
    # If TMUX env var is set, we are already inside a tmux session.
    # In that case, we can still create a new session but should not
    # nest -- just run in foreground.
    return "TMUX" not in os.environ


def session_name(release_dir: Path) -> str:
    """Deterministic session name from release directory."""
    h = hashlib.sha1(str(release_dir.resolve()).encode()).hexdigest()[:8]
    return f"sc-sprint-{h}"


def find_running_session() -> str | None:
    """Find any running sc-sprint-* session."""
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.strip().splitlines():
        if line.startswith("sc-sprint-"):
            return line
    return None


def launch_in_tmux(config: SprintConfig):
    """Create a tmux session and run the sprint inside it.

    1. Create new detached session with the TUI pane
    2. Split horizontally for the raw output tail
    3. Attach to the session (or print instructions if non-interactive)

    The sprint process itself is the main pane command, so if the
    sprint finishes the pane shows the final TUI state until the
    user closes it.
    """
    name = session_name(config.release_dir)
    config.tmux_session_name = name

    # Build the command that runs the sprint in foreground (--no-tmux)
    sprint_cmd = _build_foreground_command(config)

    # Create the session with the sprint as the main command
    subprocess.run([
        "tmux", "new-session",
        "-d",                     # detached
        "-s", name,               # session name
        "-x", "120", "-y", "40",  # default size
        *sprint_cmd,
    ], check=True)

    # Split: bottom pane tails the output of the first active phase.
    # The executor will update this pane's command as phases progress
    # by writing a small shell script that the pane sources.
    output_file = config.output_file(config.active_phases[0])
    subprocess.run([
        "tmux", "split-window",
        "-t", name,
        "-v",                     # vertical split
        "-p", "25",               # 25% height for tail pane
        "bash", "-c",
        f"touch {output_file} && tail -f {output_file}; read",
    ], check=True)

    # Select the top pane (the TUI)
    subprocess.run(["tmux", "select-pane", "-t", f"{name}:0.0"], check=True)

    # Now attach
    subprocess.run(["tmux", "attach-session", "-t", name])


def _build_foreground_command(config: SprintConfig) -> list[str]:
    """Build the superclaude sprint run ... --no-tmux command."""
    cmd = [
        "superclaude", "sprint", "run",
        str(config.index_path),
        "--no-tmux",
        "--start", str(config.start_phase),
        "--max-turns", str(config.max_turns),
        "--permission-flag", config.permission_flag,
    ]
    if config.end_phase:
        cmd.extend(["--end", str(config.end_phase)])
    if config.model:
        cmd.extend(["--model", config.model])
    return cmd


def update_tail_pane(session_name: str, output_file: Path):
    """Switch the bottom pane to tail a different output file.

    Called by the executor when starting a new phase.
    """
    subprocess.run([
        "tmux", "send-keys",
        "-t", f"{session_name}:0.1",  # bottom pane
        "C-c",  # kill current tail
    ], check=False)
    subprocess.run([
        "tmux", "send-keys",
        "-t", f"{session_name}:0.1",
        f"tail -f {output_file}\n",
    ], check=False)


def attach_to_sprint():
    """Attach to a running sprint session."""
    name = find_running_session()
    if name is None:
        click.echo("No running sprint session found.")
        raise SystemExit(1)
    subprocess.run(["tmux", "attach-session", "-t", name])


def kill_sprint(force: bool = False):
    """Kill a running sprint session."""
    name = find_running_session()
    if name is None:
        click.echo("No running sprint session found.")
        raise SystemExit(1)
    if force:
        subprocess.run(["tmux", "kill-session", "-t", name])
    else:
        # Send SIGTERM to the sprint process, wait, then kill session
        subprocess.run(["tmux", "send-keys", "-t", f"{name}:0.0", "C-c"])
        click.echo(f"Sent interrupt to {name}. Waiting 10s for graceful shutdown...")
        import time
        time.sleep(10)
        subprocess.run(["tmux", "kill-session", "-t", name], check=False)
```

### 5.4 Tmux + Rich Interaction

Rich's `Live` display uses standard ANSI escape codes (cursor movement, color, clear-line). Tmux handles these natively. When a user detaches and reattaches:

1. Tmux preserves the full terminal state in its internal buffer.
2. On reattach, tmux redraws the screen from its buffer.
3. The Rich `Live` continues updating at 2 FPS in the background.
4. The user sees the current state immediately on reattach, as if they never left.

No special handling is needed. The one caveat is terminal resize: Rich detects `SIGWINCH` and adjusts, and tmux forwards this signal on reattach if the terminal size changed. Rich handles this automatically.

---

## 6. Sidecar Monitor Design

The monitor runs in a daemon thread, polling the output file every 500ms to extract signals for the TUI.

```python
# src/superclaude/cli/sprint/monitor.py

import os
import re
import threading
import time
from pathlib import Path

from .models import MonitorState

# Patterns to extract from claude output
TASK_ID_PATTERN = re.compile(r"T\d{2}\.\d{2}")
TOOL_PATTERN = re.compile(
    r"\b(Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task)\b"
)
FILES_CHANGED_PATTERN = re.compile(
    r"(?:modified|created|edited|wrote|updated)\s+[`'\"]?([^\s`'\"]+\.\w+)"
)


class OutputMonitor:
    """Background thread that watches an output file and extracts signals.

    The monitor does not hold the file open. It stat()s and reads only
    the new bytes since the last poll. This is safe even when the file
    is being written by a child process.
    """

    def __init__(self, output_path: Path, poll_interval: float = 0.5):
        self.output_path = output_path
        self.poll_interval = poll_interval
        self.state = MonitorState()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_read_pos: int = 0
        self._seen_files: set[str] = set()

    def start(self):
        """Start the monitor thread."""
        self._stop_event.clear()
        self._last_read_pos = 0
        self._seen_files.clear()
        self.state = MonitorState()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="output-monitor",
        )
        self._thread.start()

    def stop(self):
        """Stop the monitor thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def reset(self, new_output_path: Path):
        """Reset for a new phase (new output file)."""
        self.output_path = new_output_path
        self._last_read_pos = 0
        self._seen_files.clear()
        self.state = MonitorState()

    def _poll_loop(self):
        while not self._stop_event.is_set():
            self._poll_once()
            self._stop_event.wait(self.poll_interval)

    def _poll_once(self):
        now = time.monotonic()

        try:
            size = self.output_path.stat().st_size
        except FileNotFoundError:
            return

        self.state.output_bytes_prev = self.state.output_bytes
        self.state.output_bytes = size

        if size > self._last_read_pos:
            # New data available -- read incremental chunk
            self.state.last_growth_time = now
            new_text = self._read_new_bytes(size)
            self._extract_signals(new_text)
        else:
            # No growth -- update stall counter
            self.state.stall_seconds = now - self.state.last_growth_time

        # Growth rate: exponential moving average
        delta = self.state.output_bytes - self.state.output_bytes_prev
        alpha = 0.3
        self.state.growth_rate_bps = (
            alpha * (delta / self.poll_interval)
            + (1 - alpha) * self.state.growth_rate_bps
        )

    def _read_new_bytes(self, current_size: int) -> str:
        """Read only the bytes added since last poll."""
        try:
            with open(self.output_path, "r", errors="replace") as f:
                f.seek(self._last_read_pos)
                chunk = f.read(current_size - self._last_read_pos)
                self._last_read_pos = current_size
                return chunk
        except (OSError, UnicodeDecodeError):
            return ""

    def _extract_signals(self, text: str):
        """Extract task IDs, tool names, file paths from new output text."""
        # Last task ID (take the last match)
        task_matches = TASK_ID_PATTERN.findall(text)
        if task_matches:
            self.state.last_task_id = task_matches[-1]

        # Last tool used
        tool_matches = TOOL_PATTERN.findall(text)
        if tool_matches:
            self.state.last_tool_used = tool_matches[-1]

        # Files changed (accumulate unique paths)
        file_matches = FILES_CHANGED_PATTERN.findall(text)
        for f in file_matches:
            self._seen_files.add(f)
        self.state.files_changed = len(self._seen_files)

        # Line count
        self.state.lines_total += text.count("\n")
```

### Monitor-TUI Data Flow

```
                   +-----------+
                   |  claude   |  (child process)
                   |  -p ...   |
                   +-----+-----+
                         |
                    stdout → file
                         |
                   +-----v-----+
                   | output.txt |  (on disk)
                   +-----+-----+
                         |
                    stat() + read()
                         |
                   +-----v-----+
                   |  Monitor   |  (daemon thread, 2 Hz)
                   |  Thread    |
                   +-----+-----+
                         |
                   MonitorState
                         |
                   +-----v-----+
                   |  SprintTUI |  (main thread, via Live.update)
                   |  .update() |
                   +-----+-----+
                         |
                    ANSI → terminal
```

The executor calls `tui.update(sprint_result, monitor.state, current_phase)` in a loop. The monitor thread mutates `MonitorState` in place; the TUI reads it. There is no lock because writes are to individual scalar fields (atomic on CPython due to the GIL) and stale reads are acceptable for display purposes.

---

## 7. Process Management

```python
# src/superclaude/cli/sprint/process.py

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .models import Phase, SprintConfig


class ClaudeProcess:
    """Manages a single claude -p subprocess with signal handling.

    Key design decisions:
    - Uses process groups (os.setpgrp) so we can kill the entire
      child tree on shutdown.
    - CLAUDECODE= env prefix prevents nested session detection.
    - stdout/stderr redirected to files for the monitor to read.
    - Timeout computed from max_turns * 120s + 300s buffer.
    """

    def __init__(self, config: SprintConfig, phase: Phase):
        self.config = config
        self.phase = phase
        self._process: Optional[subprocess.Popen] = None

    @property
    def timeout_seconds(self) -> int:
        return self.config.max_turns * 120 + 300

    def build_prompt(self) -> str:
        """Build the /sc:task-unified prompt for this phase."""
        pn = self.phase.number
        result_file = self.config.result_file(self.phase)
        phase_file = self.phase.file

        return f"""/sc:task-unified Execute all tasks in @{phase_file} --compliance strict --strategy systematic

## Execution Rules
- Execute tasks in order (T{pn:02d}XX.01, T{pn:02d}XX.02, etc.)
- For STRICT tier tasks: use Sequential MCP for analysis, run quality verification
- For STANDARD tier tasks: run direct test execution per acceptance criteria
- For LIGHT tier tasks: quick sanity check only
- For EXEMPT tier tasks: skip formal verification
- If a STRICT-tier task fails, STOP and report -- do not continue to next task
- For all other tier failures, log the failure and continue

## Completion Protocol
When ALL tasks in this phase are complete (or halted on STRICT failure):
1. Write a phase completion report to {result_file} containing:
   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), tasks_total, tasks_passed, tasks_failed
   - Per-task status table: Task ID, Title, Tier, Status (pass/fail/skip), Evidence
   - Files modified (list all paths)
   - Blockers for next phase (if any)
   - The literal string EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT
2. If any task produced file changes, list them under ## Files Modified

## Important
- This is Phase {pn} of a multi-phase sprint
- Previous phases have already been executed in separate sessions
- Do not re-execute work from prior phases
- Focus only on the tasks defined in the phase file"""

    def build_command(self) -> list[str]:
        """Build the claude CLI command."""
        cmd = [
            "claude",
            "--print",
            self.config.permission_flag,
            "--no-session-persistence",
            "--max-turns", str(self.config.max_turns),
            "--output-format", "text",
            "-p", self.build_prompt(),
        ]
        if self.config.model:
            cmd.extend(["--model", self.config.model])
        return cmd

    def build_env(self) -> dict[str, str]:
        """Build environment for the child process."""
        env = os.environ.copy()
        env["CLAUDECODE"] = ""  # prevent nested session detection
        return env

    def start(self) -> subprocess.Popen:
        """Launch the claude process."""
        output_file = self.config.output_file(self.phase)
        error_file = self.config.error_file(self.phase)

        # Ensure results directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self._stdout_fh = open(output_file, "w")
        self._stderr_fh = open(error_file, "w")

        self._process = subprocess.Popen(
            self.build_command(),
            stdout=self._stdout_fh,
            stderr=self._stderr_fh,
            env=self.build_env(),
            preexec_fn=os.setpgrp,  # new process group for clean kill
        )
        return self._process

    def wait(self) -> int:
        """Wait for the process with timeout. Returns exit code."""
        try:
            self._process.wait(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            self.terminate()
            return 124  # match bash timeout exit code

        self._close_handles()
        return self._process.returncode

    def terminate(self):
        """Graceful shutdown: SIGTERM, wait 10s, then SIGKILL."""
        if self._process is None or self._process.poll() is not None:
            self._close_handles()
            return

        pgid = os.getpgid(self._process.pid)

        # Phase 1: SIGTERM to the process group
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            self._close_handles()
            return

        # Phase 2: Wait up to 10 seconds
        try:
            self._process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Phase 3: SIGKILL
            try:
                os.killpg(pgid, signal.SIGKILL)
                self._process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass

        self._close_handles()

    def _close_handles(self):
        for fh in (self._stdout_fh, self._stderr_fh):
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
        if self._original_sigint:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle(self, signum, frame):
        self.shutdown_requested = True
```

---

## 8. Executor Core Loop

```python
# src/superclaude/cli/sprint/executor.py

import re
from datetime import datetime, timezone
from pathlib import Path

from .logging_ import SprintLogger
from .models import (
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
)
from .monitor import OutputMonitor
from .notify import notify_phase_complete, notify_sprint_complete
from .process import ClaudeProcess, SignalHandler
from .tmux import update_tail_pane
from .tui import SprintTUI


def execute_sprint(config: SprintConfig):
    """Main orchestration loop.

    For each active phase:
    1. Launch claude -p subprocess
    2. Start output monitor thread
    3. Update TUI in a polling loop until process exits
    4. Parse result file for CONTINUE/HALT
    5. Record PhaseResult
    6. Decide whether to continue or halt
    """
    signal_handler = SignalHandler()
    signal_handler.install()

    logger = SprintLogger(config)
    tui = SprintTUI(config)
    monitor = OutputMonitor(Path("/dev/null"))  # reset per phase

    sprint_result = SprintResult(config=config)
    logger.write_header(sprint_result)

    live = tui.start()

    try:
        for phase in config.active_phases:
            if signal_handler.shutdown_requested:
                sprint_result.outcome = SprintOutcome.INTERRUPTED
                break

            # Reset monitor for this phase
            output_path = config.output_file(phase)
            monitor.reset(output_path)
            monitor.start()

            # Update tmux tail pane if running in tmux
            if config.tmux_session_name:
                update_tail_pane(config.tmux_session_name, output_path)

            # Launch claude
            proc_manager = ClaudeProcess(config, phase)
            proc_manager.start()
            started_at = datetime.now(timezone.utc)

            tui.update(sprint_result, monitor.state, phase)

            # Poll loop: wait for process to finish while updating TUI
            while proc_manager._process.poll() is None:
                if signal_handler.shutdown_requested:
                    proc_manager.terminate()
                    break
                # Update TUI at ~2 Hz (monitor thread handles data extraction)
                tui.update(sprint_result, monitor.state, phase)
                import time
                time.sleep(0.5)

            exit_code = proc_manager._process.returncode or 0
            monitor.stop()
            finished_at = datetime.now(timezone.utc)

            # Determine phase status
            status = _determine_phase_status(
                exit_code=exit_code,
                result_file=config.result_file(phase),
                output_file=config.output_file(phase),
            )

            phase_result = PhaseResult(
                phase=phase,
                status=status,
                exit_code=exit_code,
                started_at=started_at,
                finished_at=finished_at,
                output_bytes=monitor.state.output_bytes,
                last_task_id=monitor.state.last_task_id,
                files_changed=monitor.state.files_changed,
            )
            sprint_result.phase_results.append(phase_result)

            # Log and notify
            logger.write_phase_result(phase_result)
            notify_phase_complete(phase_result)

            tui.update(sprint_result, monitor.state, None)

            # Decide: continue or halt?
            if status.is_failure:
                sprint_result.outcome = SprintOutcome.HALTED
                sprint_result.halt_phase = phase.number
                break

        # Sprint finished
        sprint_result.finished_at = datetime.now(timezone.utc)
        if sprint_result.outcome == SprintOutcome.SUCCESS:
            # Verify all phases actually passed
            if not all(r.status.is_success for r in sprint_result.phase_results):
                sprint_result.outcome = SprintOutcome.ERROR

        tui.update(sprint_result, MonitorState(), None)
        logger.write_summary(sprint_result)
        notify_sprint_complete(sprint_result)

    finally:
        tui.stop()
        signal_handler.uninstall()

    # Exit code
    if sprint_result.outcome != SprintOutcome.SUCCESS:
        raise SystemExit(1)


def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
) -> PhaseStatus:
    """Parse result file and exit code to determine phase status.

    Priority:
    1. Timeout (exit 124) -> TIMEOUT
    2. Non-zero exit -> ERROR
    3. Result file with EXIT_RECOMMENDATION: HALT -> HALT
    4. Result file with EXIT_RECOMMENDATION: CONTINUE -> PASS
    5. Result file with status: PASS/FAIL -> PASS/HALT
    6. No result file but output exists -> PASS_NO_REPORT
    7. No result file and no output -> ERROR
    """
    if exit_code == 124:
        return PhaseStatus.TIMEOUT
    if exit_code != 0:
        return PhaseStatus.ERROR

    if result_file.exists():
        content = result_file.read_text(errors="replace")
        if "EXIT_RECOMMENDATION: CONTINUE" in content:
            return PhaseStatus.PASS
        if "EXIT_RECOMMENDATION: HALT" in content:
            return PhaseStatus.HALT
        if re.search(r"status:\s*PASS", content, re.IGNORECASE):
            return PhaseStatus.PASS
        if re.search(r"status:\s*FAIL", content, re.IGNORECASE):
            return PhaseStatus.HALT
        return PhaseStatus.PASS_NO_SIGNAL

    if output_file.exists() and output_file.stat().st_size > 0:
        return PhaseStatus.PASS_NO_REPORT

    return PhaseStatus.ERROR
```

---

## 9. Logging Architecture

```python
# src/superclaude/cli/sprint/logging_.py

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console

from .models import PhaseResult, PhaseStatus, SprintConfig, SprintResult


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
        self._jsonl({
            "event": "sprint_start",
            "timestamp": sprint.started_at.isoformat(),
            "index": str(self.config.index_path),
            "phases": f"{self.config.start_phase}-{self.config.end_phase or 'last'}",
            "max_turns": self.config.max_turns,
            "model": self.config.model or "default",
        })

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

    def write_phase_result(self, result: PhaseResult):
        """Log a phase completion."""
        # JSONL
        self._jsonl({
            "event": "phase_complete",
            "phase": result.phase.number,
            "status": result.status.value,
            "exit_code": result.exit_code,
            "started_at": result.started_at.isoformat(),
            "finished_at": result.finished_at.isoformat(),
            "duration_seconds": result.duration_seconds,
            "output_bytes": result.output_bytes,
            "last_task_id": result.last_task_id,
            "files_changed": result.files_changed,
        })

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
        self._jsonl({
            "event": "sprint_complete",
            "outcome": sprint.outcome.value,
            "duration_seconds": sprint.duration_seconds,
            "phases_passed": sprint.phases_passed,
            "phases_failed": sprint.phases_failed,
            "halt_phase": sprint.halt_phase,
        })

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
```

---

## 10. Phase Discovery & Configuration

```python
# src/superclaude/cli/sprint/config.py

import re
from pathlib import Path

import click

from .models import Phase, SprintConfig


# Matches: phase-1-tasklist.md, p1-tasklist.md, phase1-tasklist.md,
# Phase_1_tasklist.md, tasklist-P1.md, tasklist-p1.md
PHASE_FILE_PATTERN = re.compile(
    r"(?:phase|p)[-_]?(\d+)[-_]tasklist[^\s|)]*\.md"
    r"|"
    r"tasklist[-_](?:phase|p)[-_]?(\d+)[^\s|)]*\.md",
    re.IGNORECASE,
)


def discover_phases(index_path: Path) -> list[Phase]:
    """Discover phase files from the index and/or directory.

    Strategy 1: grep the index file for phase file references.
    Strategy 2: scan the directory for files matching the pattern.
    Deduplicates by phase number, sorts ascending.
    """
    index_dir = index_path.parent
    index_name = index_path.name
    phases: dict[int, Phase] = {}

    # Strategy 1: parse index file
    index_text = index_path.read_text(errors="replace")
    for match in PHASE_FILE_PATTERN.finditer(index_text):
        num = int(match.group(1) or match.group(2))
        filename = match.group(0)
        filepath = index_dir / filename
        if filepath.exists() and num not in phases:
            phases[num] = Phase(number=num, file=filepath)

    # Strategy 2: scan directory if nothing found
    if not phases:
        for f in sorted(index_dir.iterdir()):
            if f.name == index_name or not f.is_file():
                continue
            m = PHASE_FILE_PATTERN.search(f.name)
            if m:
                num = int(m.group(1) or m.group(2))
                if num not in phases:
                    phases[num] = Phase(number=num, file=f)

    return [phases[k] for k in sorted(phases)]


def _extract_phase_name(phase_file: Path) -> str:
    """Try to extract a phase name from the first heading."""
    try:
        for line in phase_file.open():
            line = line.strip()
            if line.startswith("# "):
                # Strip markdown heading and phase number prefix
                name = re.sub(r"^#\s+(?:Phase\s+\d+\s*[-:—]\s*)?", "", line)
                return name[:50]  # truncate
    except OSError:
        pass
    return ""


def validate_phases(
    phases: list[Phase],
    start: int,
    end: int,
) -> list[str]:
    """Validate phase files exist and check for gaps.
    Returns list of warning/error messages.
    """
    messages = []
    active = [p for p in phases if start <= p.number <= end]

    # Check files exist
    for p in active:
        if not p.file.exists():
            messages.append(f"ERROR: Phase {p.number} file missing: {p.file}")

    # Check for gaps
    numbers = [p.number for p in active]
    for i in range(1, len(numbers)):
        if numbers[i] != numbers[i - 1] + 1:
            messages.append(
                f"WARN: Gap in sequence: Phase {numbers[i-1]} -> Phase {numbers[i]}"
            )

    return messages


def load_sprint_config(
    index_path: Path,
    start_phase: int = 1,
    end_phase: int = 0,
    max_turns: int = 50,
    model: str = "",
    dry_run: bool = False,
    permission_flag: str = "--dangerously-skip-permissions",
) -> SprintConfig:
    """Load and validate a complete sprint configuration."""
    index_path = Path(index_path).resolve()

    if not index_path.exists():
        raise click.ClickException(f"Index file not found: {index_path}")

    phases = discover_phases(index_path)
    if not phases:
        raise click.ClickException(
            "No phase files discovered. Expected filenames like: "
            "phase-1-tasklist.md, p1-tasklist.md, tasklist-P1.md"
        )

    # Enrich phases with names
    for phase in phases:
        phase.name = _extract_phase_name(phase.file)

    # Auto-detect end phase
    if end_phase == 0:
        end_phase = max(p.number for p in phases)

    # Validate
    messages = validate_phases(phases, start_phase, end_phase)
    errors = [m for m in messages if m.startswith("ERROR")]
    if errors:
        for e in errors:
            click.echo(e, err=True)
        raise click.ClickException(f"{len(errors)} phase file(s) missing.")

    for m in messages:
        if m.startswith("WARN"):
            click.echo(m, err=True)

    return SprintConfig(
        index_path=index_path,
        release_dir=index_path.parent,
        phases=phases,
        start_phase=start_phase,
        end_phase=end_phase,
        max_turns=max_turns,
        model=model,
        dry_run=dry_run,
        permission_flag=permission_flag,
    )
```

---

## 11. Desktop Notifications

```python
# src/superclaude/cli/sprint/notify.py

import platform
import shutil
import subprocess

from .models import PhaseResult, SprintResult


def _notify(title: str, message: str, urgent: bool = False):
    """Send a desktop notification. Fails silently."""
    system = platform.system()
    try:
        if system == "Linux" and shutil.which("notify-send"):
            cmd = ["notify-send"]
            if urgent:
                cmd.extend(["--urgency", "critical"])
            cmd.extend([title, message])
            subprocess.run(cmd, timeout=5, check=False)

        elif system == "Darwin" and shutil.which("osascript"):
            script = (
                f'display notification "{message}" '
                f'with title "{title}"'
            )
            subprocess.run(
                ["osascript", "-e", script],
                timeout=5, check=False,
            )
    except Exception:
        pass  # notifications are best-effort


def notify_phase_complete(result: PhaseResult):
    """Notify on phase completion."""
    if result.status.is_failure:
        _notify(
            "Sprint HALT",
            f"Phase {result.phase.number} failed: {result.status.value}",
            urgent=True,
        )
    elif result.status.is_success:
        _notify(
            "Phase Complete",
            f"Phase {result.phase.number}: {result.status.value} "
            f"({result.duration_display})",
        )


def notify_sprint_complete(result: SprintResult):
    """Notify on sprint completion."""
    if result.outcome.value == "success":
        _notify(
            "Sprint Complete",
            f"All phases passed in {result.duration_display}",
        )
    else:
        _notify(
            "Sprint Finished",
            f"Outcome: {result.outcome.value} ({result.duration_display})",
            urgent=True,
        )
```

---

## 12. Testing Strategy

### 12.1 Test File Layout

```
tests/sprint/
  __init__.py
  test_models.py        # PhaseStatus properties, SprintResult aggregation
  test_config.py        # Phase discovery, validation, gap detection
  test_monitor.py       # Signal extraction from mock output files
  test_process.py       # Command building, env construction (no subprocess)
  test_executor.py      # Integration test with mocked subprocess
  test_tui.py           # Render output verification (snapshot tests)
  test_tmux.py          # Tmux command construction (no actual tmux)
  test_logging.py       # JSONL/Markdown output format verification
  fixtures/
    sample-index.md     # Minimal tasklist-index for testing
    phase-1-tasklist.md
    phase-2-tasklist.md
    sample-result.md    # Phase result with EXIT_RECOMMENDATION
```

### 12.2 What Gets Tested and How

| Component | Test Type | Mocking Strategy |
|-----------|-----------|-----------------|
| `models.py` | Unit | None needed -- pure dataclasses |
| `config.py` | Unit | Temp directory with fixture files via `tmp_path` |
| `monitor.py` | Unit | Write to temp file, verify extraction |
| `process.py` | Unit | Mock `subprocess.Popen`, verify command construction |
| `executor.py` | Integration | Mock `ClaudeProcess.start/wait`, mock monitor, verify flow |
| `tui.py` | Snapshot | Render to string via `Console(file=StringIO)`, compare |
| `tmux.py` | Unit | Mock `subprocess.run`, verify tmux commands |
| `logging_.py` | Unit | Write to temp dir, verify file contents |
| `notify.py` | Unit | Mock `subprocess.run`, verify platform detection |

### 12.3 Key Test Cases

```python
# tests/sprint/test_config.py

def test_discover_phases_from_index(tmp_path):
    """Phases referenced in index are discovered."""
    index = tmp_path / "tasklist-index.md"
    index.write_text("| Phase 1 | phase-1-tasklist.md |\n| Phase 2 | phase-2-tasklist.md |")
    (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
    (tmp_path / "phase-2-tasklist.md").write_text("# Phase 2")

    phases = discover_phases(index)
    assert len(phases) == 2
    assert phases[0].number == 1
    assert phases[1].number == 2


def test_discover_phases_directory_fallback(tmp_path):
    """Falls back to directory scan when index has no refs."""
    index = tmp_path / "tasklist-index.md"
    index.write_text("# Sprint\nNo phase refs here.")
    (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
    (tmp_path / "p2-tasklist.md").write_text("# Phase 2")

    phases = discover_phases(index)
    assert len(phases) == 2


def test_discover_flexible_naming(tmp_path):
    """Various naming conventions are recognized."""
    index = tmp_path / "tasklist-index.md"
    index.write_text("Nothing")
    for name in ["phase-1-tasklist.md", "p2-tasklist.md", "Phase_3_tasklist.md",
                  "tasklist-P4.md"]:
        (tmp_path / name).write_text(f"# {name}")

    phases = discover_phases(index)
    assert [p.number for p in phases] == [1, 2, 3, 4]


def test_validate_detects_missing_files(tmp_path):
    """Missing files produce error messages."""
    phases = [Phase(number=1, file=tmp_path / "missing.md")]
    messages = validate_phases(phases, 1, 1)
    assert any("ERROR" in m for m in messages)


def test_validate_detects_gaps():
    """Non-sequential phase numbers produce warnings."""
    phases = [
        Phase(number=1, file=Path("/fake/p1.md")),
        Phase(number=3, file=Path("/fake/p3.md")),
    ]
    messages = validate_phases(phases, 1, 3)
    assert any("Gap" in m for m in messages)


# tests/sprint/test_monitor.py

def test_extract_task_id(tmp_path):
    """Monitor extracts task IDs from output."""
    output = tmp_path / "output.txt"
    output.write_text("Working on T03.02 now\nCompleted T03.03")

    monitor = OutputMonitor(output)
    monitor._poll_once()

    assert monitor.state.last_task_id == "T03.03"


def test_extract_tool_name(tmp_path):
    """Monitor extracts tool names from output."""
    output = tmp_path / "output.txt"
    output.write_text("Using Read to examine the file\nApplying Edit to fix")

    monitor = OutputMonitor(output)
    monitor._poll_once()

    assert monitor.state.last_tool_used == "Edit"


def test_stall_detection(tmp_path):
    """Stall detected when file stops growing."""
    output = tmp_path / "output.txt"
    output.write_text("initial content")

    monitor = OutputMonitor(output, poll_interval=0.1)
    monitor._poll_once()

    # Simulate time passing with no growth
    import time
    monitor.state.last_growth_time = time.monotonic() - 35
    monitor._poll_once()

    assert monitor.state.stall_status == "thinking..."


# tests/sprint/test_process.py

def test_build_command_default():
    """Default command includes required flags."""
    config = SprintConfig(
        index_path=Path("/test/index.md"),
        release_dir=Path("/test"),
        phases=[Phase(1, Path("/test/p1.md"))],
    )
    proc = ClaudeProcess(config, config.phases[0])
    cmd = proc.build_command()

    assert "claude" in cmd
    assert "--print" in cmd
    assert "--no-session-persistence" in cmd
    assert "--max-turns" in cmd
    assert "50" in cmd


def test_build_command_with_model():
    """Model flag included when specified."""
    config = SprintConfig(
        index_path=Path("/test/index.md"),
        release_dir=Path("/test"),
        phases=[Phase(1, Path("/test/p1.md"))],
        model="sonnet",
    )
    proc = ClaudeProcess(config, config.phases[0])
    cmd = proc.build_command()

    assert "--model" in cmd
    assert "sonnet" in cmd


def test_env_has_claudecode_empty():
    """CLAUDECODE env var set to empty string."""
    config = SprintConfig(
        index_path=Path("/test/index.md"),
        release_dir=Path("/test"),
        phases=[Phase(1, Path("/test/p1.md"))],
    )
    proc = ClaudeProcess(config, config.phases[0])
    env = proc.build_env()

    assert env["CLAUDECODE"] == ""
```

---

## 13. Migration Plan

### 13.1 Phase 1: Ship Python Version (v4.3.0)

1. Implement all modules under `src/superclaude/cli/sprint/`.
2. Add `sprint_group` to `main.py`.
3. Write tests in `tests/sprint/`.
4. Validate against the existing v2.02 tasklist-index.md.

### 13.2 Phase 2: Bash Shim (Backward Compatibility)

Replace `.dev/releases/execute-sprint.sh` with a thin shim:

```bash
#!/usr/bin/env bash
# execute-sprint.sh -- DEPRECATED: Use `superclaude sprint run` instead.
# This shim forwards to the Python implementation for backward compatibility.

set -euo pipefail

echo "[DEPRECATED] execute-sprint.sh is deprecated. Use: superclaude sprint run $@"
echo ""

# Forward all arguments
exec superclaude sprint run "$@" --no-tmux
```

### 13.3 Phase 3: Remove Bash (v4.4.0)

- Delete the shim.
- Update all documentation referencing `execute-sprint.sh`.
- Update CLAUDE.md workflow instructions.

### 13.4 Dependency Impact

No new dependencies. The implementation uses only:
- `click` (existing) -- CLI framework
- `rich` (existing) -- TUI display
- `subprocess`, `threading`, `signal`, `os`, `re`, `json`, `hashlib` -- stdlib

---

## 14. Open Design Questions

| # | Question | Recommendation | Impact |
|---|----------|---------------|--------|
| 1 | Should `--start N` auto-detect incomplete previous runs? | Yes: check for partial execution-log.jsonl and warn. | Low complexity, high UX value. |
| 2 | Should the monitor track token usage from claude output? | Defer to v4.4: requires parsing structured output format. | Nice-to-have, not blocking. |
| 3 | Should `sprint status` work without tmux (read log file only)? | Yes: `status` should always work by reading the JSONL log. | Already in the design. |
| 4 | Maximum concurrent sprints? | Allow multiple via unique tmux session names. Document but don't enforce a limit. | Already handled by hash-based naming. |
| 5 | Should we support `--resume` as an alias for `--start` with auto-detection? | Yes in v4.4: parse last successful phase from log and set start=N+1. | UX improvement, defer. |
