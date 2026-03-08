# TUI Unification Blueprint

> Refactoring plan to give the roadmap runner the same "fine dining" TUI/TMUX
> experience as the sprint runner, while centralizing shared code in `pipeline/`.

**Status**: Design — not yet implemented
**Date**: 2026-03-07

---

## The Problem

The sprint runner has a rich operator experience:

```
╭──────────── SUPERCLAUDE SPRINT RUNNER ──────────────╮
│  Phase table, progress bar, live metrics, stall     │
│  detection, TMUX detach/attach, notifications...    │
╰─────────────────────────────────────────────────────╯
```

The roadmap runner has this:

```
[roadmap] Starting step: extract
[roadmap] Step extract  PASS (attempt 1, 45s)
```

They should look and feel identical.

---

## The Hard Problem: Live Updates During Blocking Steps

The sprint executor owns its own poll loop — it calls `tui.update()` at 2 Hz
while polling `process.poll()`. This gives it real-time TUI updates.

The roadmap executor delegates to `execute_pipeline()`, which calls
`roadmap_run_step()` — a **blocking** function that doesn't return until the
subprocess exits. During that blocking period, there's nowhere to call
`tui.update()`.

### Solution: Background Refresh Thread

```
┌─────────────────────────────────────────────────────┐
│  execute_roadmap()                                   │
│                                                      │
│  1. Create TUI + Monitor                             │
│  2. Start background refresh thread (2 Hz)           │
│  3. Call execute_pipeline() with callbacks            │
│     ├── on_step_start → reset monitor, update TUI    │
│     ├── [step runs... refresh thread updates TUI]    │
│     └── on_step_complete → stop monitor, update TUI  │
│  4. Stop refresh thread                              │
│  5. Render terminal panel                            │
└─────────────────────────────────────────────────────┘
```

The refresh thread runs independently of the pipeline executor. It reads
`monitor.state` and calls `tui.update()` every 0.5s. The pipeline executor's
callbacks handle **transitions** (step start/stop, tmux pane retargeting),
while the refresh thread handles **live display**.

This requires **zero changes** to `pipeline/executor.py`.

---

## Phase 1: Extract Generics to `pipeline/`

**Goal**: Move universally-useful code out of `sprint/` into `pipeline/` without
any behavior change. Sprint continues to work identically.

### 1A. Move `notify.py` → `pipeline/notify.py`

Sprint's `notify.py` is already fully generic. It takes title+message strings.

```python
# pipeline/notify.py — moved verbatim from sprint/notify.py
def _notify(title: str, message: str, urgent: bool = False): ...
```

Sprint imports change: `from .notify import ...` → `from ..pipeline.notify import ...`

### 1B. Move `debug_logger.py` → `pipeline/debug_logger.py`

Also already generic. No sprint-specific imports.

### 1C. Create `pipeline/tmux.py`

Extract from sprint's `tmux.py`, parameterizing the session prefix:

```python
# pipeline/tmux.py

def session_name(work_dir: Path, prefix: str = "sc-pipeline") -> str:
    h = hashlib.sha1(str(work_dir.resolve()).encode()).hexdigest()[:8]
    return f"{prefix}-{h}"

def is_tmux_available() -> bool: ...  # identical

def find_running_session(prefix: str = "sc-") -> str | None:
    # Finds any session matching prefix pattern
    ...

def launch_in_tmux(
    session_prefix: str,
    foreground_cmd: list[str],
    initial_tail_file: Path,
    session_size: tuple[int, int] = (120, 40),
    tail_pane_pct: int = 25,
) -> int:
    """Generic tmux launcher. Returns exit code from sentinel file."""
    ...

def update_tail_pane(tmux_session_name: str, output_file: Path): ...  # identical
def attach_to_session(prefix: str): ...
def kill_session(prefix: str, force: bool = False): ...
```

Sprint's `tmux.py` becomes a thin adapter:

```python
# sprint/tmux.py
from ..pipeline.tmux import (
    is_tmux_available,
    launch_in_tmux as _launch,
    update_tail_pane,
    attach_to_session,
    kill_session,
)

SESSION_PREFIX = "sc-sprint"

def session_name(release_dir): return pipeline_session_name(release_dir, SESSION_PREFIX)
def launch_in_tmux(config): return _launch(SESSION_PREFIX, _build_cmd(config), ...)
def attach_to_sprint(): return attach_to_session(SESSION_PREFIX)
def kill_sprint(force=False): return kill_session(SESSION_PREFIX, force)
```

### 1D. Create `pipeline/monitor.py`

A simple text-mode output monitor — no NDJSON, no signal extraction:

```python
# pipeline/monitor.py

@dataclass
class BaseMonitorState:
    """Universal output monitoring state."""
    output_bytes: int = 0
    output_bytes_prev: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    last_growth_time: float = field(default_factory=time.monotonic)
    phase_started_at: float = field(default_factory=time.monotonic)
    lines_total: int = 0

    @property
    def stall_status(self) -> str:
        now = time.monotonic()
        if self.lines_total == 0:
            if now - self.phase_started_at > 120: return "STALLED"
            return "waiting..."
        since_last = now - self.last_growth_time
        if since_last > 120: return "STALLED"
        if since_last > 30: return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str: ...


class TextOutputMonitor:
    """File growth monitor for text-mode output. No NDJSON parsing."""

    def __init__(self, output_path: Path, poll_interval: float = 0.5): ...
    def start(self): ...
    def stop(self): ...
    def reset(self, new_output_path: Path): ...

    def _poll_once(self):
        size = self.output_path.stat().st_size
        # Track byte growth, line count growth, stall detection
        # EMA growth rate (alpha=0.3) — same as sprint
        ...
```

Sprint's `monitor.py` keeps its NDJSON-specific `OutputMonitor` but `MonitorState`
is refactored to extend `BaseMonitorState`:

```python
# sprint/models.py
@dataclass
class MonitorState(BaseMonitorState):
    """Sprint-specific: adds NDJSON signal fields."""
    events_received: int = 0
    last_task_id: str = ""
    last_tool_used: str = ""
    files_changed: int = 0
    last_event_time: float = field(default_factory=time.monotonic)
```

### 1E. Create `pipeline/tui.py` — Base TUI Class

Template Method pattern. The outer render structure is identical across runners;
only the inner components differ.

```python
# pipeline/tui.py

from abc import ABC, abstractmethod
from rich.console import Console, Group as RichGroup
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text


class PipelineTUI(ABC):
    """Base TUI for any pipeline runner. Template Method pattern.

    Subclasses implement: _build_header(), _build_step_table(),
    _build_active_panel(). Everything else is shared.
    """

    def __init__(self, title: str, console: Console | None = None):
        self.title = title
        self.console = console or Console()
        self._live: Live | None = None
        self._live_failed: bool = False

    def start(self) -> Live:
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=2,
            screen=False,
        )
        self._live.start()
        return self._live

    def stop(self):
        if self._live:
            self._live.stop()

    def safe_update(self):
        """Error-resilient display refresh. Call from refresh thread."""
        if self._live and not self._live_failed:
            try:
                self._live.update(self._render())
            except Exception as exc:
                import sys
                self._live_failed = True
                print(f"[TUI] Display error (continuing): {exc}", file=sys.stderr)

    def _render(self) -> Panel:
        """Template: assemble the 4 components into the standard layout."""
        header = self._build_header()
        table = self._build_step_table()
        progress = self._build_progress()
        detail = self._build_active_panel()

        body = RichGroup(header, "", table, "", progress, "", detail)

        return Panel(
            body,
            title=f"[bold]{self.title}[/]",
            border_style="blue",
            padding=(1, 2),
        )

    # --- Shared builders ---

    def build_progress_bar(
        self, completed: int, total: int, label: str = "Progress"
    ) -> Progress:
        progress = Progress(
            TextColumn(f"[bold]{label}"),
            BarColumn(bar_width=40),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("[dim]{task.completed}/{task.total} steps[/]"),
        )
        progress.add_task("pipeline", total=max(total, 1), completed=completed)
        return progress

    def build_terminal_panel(
        self, success: bool, content: str, success_title: str = "Complete",
        failure_title: str = "Halted",
    ) -> Panel:
        if success:
            return Panel(content, title=f"[bold green]{success_title}[/]",
                         border_style="green")
        return Panel(content, title=f"[bold red]{failure_title}[/]",
                     border_style="red")

    # --- Abstract: subclass implements these ---

    @abstractmethod
    def _build_header(self) -> Text: ...

    @abstractmethod
    def _build_step_table(self): ...

    @abstractmethod
    def _build_progress(self) -> Progress: ...

    @abstractmethod
    def _build_active_panel(self) -> Panel: ...
```

### 1F. Create `pipeline/logging_.py` — Base Logger

```python
# pipeline/logging_.py

class PipelineLogger:
    """Dual-format JSONL+Markdown execution logger."""

    def __init__(self, config: PipelineConfig, runner_name: str):
        self.config = config
        self.runner_name = runner_name
        self.console = Console(stderr=True)
        self._jsonl_path = config.work_dir / "execution-log.jsonl"
        self._md_path = config.work_dir / "execution-log.md"

    def write_header(self, metadata: dict): ...
    def write_step_start(self, step_id: str, step_name: str): ...
    def write_step_result(self, step_id: str, status: str, duration: str,
                          exit_code: int = 0): ...
    def write_summary(self, outcome: str, stats: dict): ...

    # Severity-routed screen output
    def screen_info(self, msg: str): self.console.print(f"[green][INFO][/] {msg}")
    def screen_warn(self, msg: str): self.console.print(f"[yellow][WARN][/] {msg}")
    def screen_error(self, msg: str): self.console.print(f"[bold red][ERROR][/] {msg}\a")
```

### Phase 1 Summary

| New file | Lines (est.) | Source |
|----------|-------------|--------|
| `pipeline/tmux.py` | ~180 | Extracted from sprint/tmux.py |
| `pipeline/monitor.py` | ~120 | New (simplified monitor) |
| `pipeline/tui.py` | ~100 | New (base class) |
| `pipeline/logging_.py` | ~100 | Extracted from sprint/logging_.py |
| `pipeline/notify.py` | ~60 | Moved from sprint/notify.py |
| `pipeline/debug_logger.py` | ~140 | Moved from sprint/debug_logger.py |

**Sprint changes**: Import paths only. Zero behavior change.

---

## Phase 2: Build Roadmap TUI

### 2A. `roadmap/tui.py` — RoadmapTUI

```python
# roadmap/tui.py

from ..pipeline.tui import PipelineTUI
from ..pipeline.models import StepStatus

# Roadmap uses pipeline's StepStatus directly (6 states vs sprint's 10)
STATUS_STYLES = {
    StepStatus.PASS:      "bold green",
    StepStatus.FAIL:      "bold red",
    StepStatus.TIMEOUT:   "bold red",
    StepStatus.CANCELLED: "bold red",
    StepStatus.PENDING:   "dim",
    StepStatus.SKIPPED:   "dim strikethrough",
}

STATUS_ICONS = {
    StepStatus.PASS:      "[green]PASS[/]",
    StepStatus.FAIL:      "[red]FAIL[/]",
    StepStatus.TIMEOUT:   "[red]TIMEOUT[/]",
    StepStatus.CANCELLED: "[red]CANCELLED[/]",
    StepStatus.PENDING:   "[dim]pending[/]",
    StepStatus.SKIPPED:   "[dim]skipped[/]",
}


class RoadmapTUI(PipelineTUI):

    def __init__(self, config, steps, console=None):
        super().__init__("SUPERCLAUDE ROADMAP RUNNER", console)
        self.config = config
        self.steps = steps  # flat list of Step objects
        self.results: dict[str, StepResult] = {}
        self.current_step: Step | None = None
        self.monitor_state: BaseMonitorState = BaseMonitorState()
        self.started_at: float = time.monotonic()
        self.finished: bool = False
        self.outcome: str | None = None

    def _build_header(self) -> Text:
        elapsed = self._format_elapsed()
        spec_name = self.config.spec_file.stem
        return Text.from_markup(
            f"[dim]{spec_name}[/]    Elapsed: [bold]{elapsed}[/]"
        )

    def _build_step_table(self) -> Table:
        table = Table(show_header=True, header_style="bold",
                      border_style="dim", pad_edge=False, box=None)
        table.add_column("#", width=3, justify="right")
        table.add_column("Step", min_width=25)
        table.add_column("Status", width=12, justify="center")
        table.add_column("Gate", width=8, justify="center")
        table.add_column("Duration", width=10, justify="right")
        table.add_column("Attempt", width=7, justify="center")

        for i, step in enumerate(self.steps, 1):
            result = self.results.get(step.id)
            status = result.status if result else StepStatus.PENDING
            if step == self.current_step and status == StepStatus.PENDING:
                # Force RUNNING display (no RUNNING in StepStatus, use markup)
                status_display = "[bold yellow]RUNNING[/]"
                style = "bold yellow"
            else:
                status_display = STATUS_ICONS.get(status, str(status.value))
                style = STATUS_STYLES.get(status, "")

            duration = self._step_duration(step, result)
            gate_tier = step.gate.enforcement_tier[:3] if step.gate else "—"
            attempt = str(result.attempt) if result else "-"

            table.add_row(str(i), step.id, status_display,
                          f"[dim]{gate_tier}[/]", duration, attempt,
                          style=style if status == StepStatus.PENDING else "")
        return table

    def _build_progress(self) -> Progress:
        total = len(self.steps)
        done = sum(1 for r in self.results.values()
                   if r.status == StepStatus.PASS)
        return self.build_progress_bar(done, total)

    def _build_active_panel(self) -> Panel:
        if self.finished:
            return self._build_terminal()

        if not self.current_step:
            return Panel("[dim]Waiting...[/]", title="Active Step")

        ms = self.monitor_state
        stall = ms.stall_status
        stall_style = ("bold red blink" if stall == "STALLED"
                       else "yellow" if stall == "thinking..."
                       else "green")

        lines = [
            f"Step:    {self.current_step.id}",
            f"Status:  RUNNING -- [{stall_style}]{stall}[/]",
            "",
            f"Output:        {self.current_step.output_file.name}",
            f"Output size:   {ms.output_size_display}  (+{ms.growth_rate_bps:.1f} B/s)",
            f"Timeout:       {self.current_step.timeout_seconds}s",
        ]

        return Panel(
            "\n".join(lines),
            title=f"[bold yellow]ACTIVE: {self.current_step.id}[/]",
            border_style="yellow",
        )

    def _build_terminal(self) -> Panel:
        if self.outcome == "success":
            content = (f"Result:  [bold green]ALL STEPS PASSED[/]\n"
                       f"Output:  {self.config.output_dir}")
            return self.build_terminal_panel(True, content,
                                             "Pipeline Complete", "Pipeline Halted")
        failed = [r for r in self.results.values() if r.status.is_failure]
        fail_id = failed[-1].step.id if failed else "unknown"
        content = (f"Result:  [bold red]HALTED[/]\n"
                   f"Failed:  {fail_id}\n"
                   f"Resume:  superclaude roadmap run {self.config.spec_file} --resume")
        return self.build_terminal_panel(False, content,
                                         "Pipeline Complete", "Pipeline Halted")
```

### 2B. Parallel Step Display

The roadmap has a parallel group (generate-A + generate-B). The step table
handles this naturally — both steps appear as rows, both show RUNNING
simultaneously. The `current_step` tracking needs to support a set:

```python
self.current_steps: set[str] = set()

# In _build_step_table, check:
if step.id in self.current_steps and status == StepStatus.PENDING:
    status_display = "[bold yellow]RUNNING[/]"
```

### 2C. Roadmap Commands Expansion

Currently roadmap has only `run`. Add:

```python
# roadmap/commands.py

@roadmap.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("--no-tmux", is_flag=True)
# ... existing options ...
def run(spec_file, no_tmux, ...):
    ...

@roadmap.command()
def attach():
    """Attach to a running roadmap session."""
    from ..pipeline.tmux import attach_to_session
    attach_to_session("sc-roadmap")

@roadmap.command()
@click.option("--force", is_flag=True)
def kill(force):
    """Kill a running roadmap session."""
    from ..pipeline.tmux import kill_session
    kill_session("sc-roadmap", force)

@roadmap.command()
def status():
    """Show roadmap execution status."""
    # Read .roadmap-state.json and display with Rich
    ...
```

---

## Phase 3: Integrate TUI into Roadmap Executor

This is the core integration. The key pattern is:

```python
# roadmap/executor.py — changes to execute_roadmap()

def execute_roadmap(config: RoadmapConfig, resume: bool = False) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    steps = _build_steps(config)
    flat_steps = _flatten_steps(steps)  # for TUI display

    if config.dry_run:
        _dry_run_output(steps)
        return

    # --- NEW: TUI + TMUX integration ---
    use_tmux = not getattr(config, 'no_tmux', False) and is_tmux_available()

    if use_tmux:
        from ..pipeline.tmux import launch_in_tmux
        launch_in_tmux("sc-roadmap", _build_foreground_cmd(config),
                       flat_steps[0].output_file if flat_steps else Path("/dev/null"))
        return

    # Foreground execution with TUI
    tui = RoadmapTUI(config, flat_steps)
    monitor = TextOutputMonitor(Path("/dev/null"))
    logger = PipelineLogger(config, "roadmap")
    tmux_session = getattr(config, 'tmux_session_name', '')

    tui.start()
    refresh_stop = threading.Event()
    refresh_thread = _start_refresh(tui, monitor, refresh_stop)

    try:
        def on_step_start(step):
            monitor.reset(step.output_file)
            monitor.start()
            tui.current_step = step
            tui.current_steps.add(step.id)
            if tmux_session:
                update_tail_pane(tmux_session, step.output_file)
            logger.write_step_start(step.id, step.id)

        def on_step_complete(step, result):
            monitor.stop()
            tui.current_steps.discard(step.id)
            tui.results[step.id] = result
            if not tui.current_steps:
                tui.current_step = None
            logger.write_step_result(step.id, result.status.value,
                                     f"{result.duration_seconds:.0f}s")
            notify_step(step, result)

        if resume:
            steps = _apply_resume(steps, config, gate_passed)

        results = execute_pipeline(
            steps=steps, config=config, run_step=roadmap_run_step,
            on_step_start=on_step_start, on_step_complete=on_step_complete,
        )

        # Terminal state
        failures = [r for r in results if r.status.is_failure]
        tui.outcome = "halted" if failures else "success"
        tui.finished = True
        tui.safe_update()

        _save_state(config, results)
        logger.write_summary(tui.outcome, {"passed": len(results) - len(failures),
                                            "failed": len(failures)})
        notify_pipeline_complete(tui.outcome, config)

        if failures:
            halt_msg = _format_halt_output(results, config)
            print(halt_msg, file=sys.stderr)

    finally:
        refresh_stop.set()
        refresh_thread.join(timeout=2)
        tui.stop()

    # Write sentinel for tmux caller
    _exitcode = 0 if tui.outcome == "success" else 1
    (config.output_dir / ".roadmap-exitcode").write_text(str(_exitcode))
    if _exitcode != 0:
        raise SystemExit(_exitcode)


def _start_refresh(tui, monitor, stop_event, interval=0.5):
    """Background thread that refreshes TUI at 2 Hz."""
    def _loop():
        while not stop_event.is_set():
            tui.monitor_state = monitor.state
            tui.safe_update()
            stop_event.wait(interval)

    t = threading.Thread(target=_loop, daemon=True, name="tui-refresh")
    t.start()
    return t
```

### What the Roadmap Dashboard Looks Like

```
╭────────────── SUPERCLAUDE ROADMAP RUNNER ─────────────╮
│                                                        │
│  my-feature-spec    Elapsed: 3m 45s                    │
│                                                        │
│  #  Step                  Status     Gate  Duration  A │
│  1  extract               PASS       STD   45s       1 │
│  2  generate-opus-arch    PASS       STR   2m 10s    1 │
│  3  generate-haiku-arch   PASS       STR   1m 55s    1 │
│  4  diff                  PASS       STD   30s       1 │
│  5  debate                RUNNING    STR   -         - │
│  6  score                 pending    STD   -         - │
│  7  merge                 pending    STR   -         - │
│  8  test-strategy         pending    STD   -         - │
│                                                        │
│  Progress ████████████████░░░░░░░░░░░░░░░░  50%  4/8  │
│                                                        │
│  ╭── ACTIVE: debate ──────────────────────╮           │
│  │ Step:    debate                         │           │
│  │ Status:  RUNNING -- active              │           │
│  │                                         │           │
│  │ Output:        debate-transcript.md     │           │
│  │ Output size:   18.3 KB  (+512.0 B/s)   │           │
│  │ Timeout:       600s                     │           │
│  ╰─────────────────────────────────────────╯           │
│                                                        │
╰────────────────────────────────────────────────────────╯
```

With TMUX:
```
┌──────────────────────────────────────────┐
│  [Rich TUI dashboard as above]           │  ← pane 0.0 (75%)
├──────────────────────────────────────────┤
│  $ tail -f debate-transcript.md          │  ← pane 0.1 (25%)
│  ## Round 1: Position A                  │
│  The extraction covers all...            │
└──────────────────────────────────────────┘
```

---

## Phase 4: Retrofit Sprint to Use Shared Modules

After Phase 1 creates the pipeline generics, sprint should be updated to inherit from them.

### Sprint TUI → extends PipelineTUI

```python
# sprint/tui.py
class SprintTUI(PipelineTUI):
    def __init__(self, config: SprintConfig, console=None):
        super().__init__("SUPERCLAUDE SPRINT RUNNER", console)
        # ... sprint-specific state ...

    def _build_header(self) -> Text: ...       # unchanged
    def _build_step_table(self) -> Table: ...  # renamed from _build_phase_table
    def _build_progress(self) -> Progress: ... # uses self.build_progress_bar()
    def _build_active_panel(self) -> Panel: ... # unchanged
```

### Sprint imports → pipeline

```python
# sprint/tmux.py → thin wrapper around pipeline/tmux.py
# sprint/notify.py → deleted, import from pipeline/
# sprint/debug_logger.py → deleted, import from pipeline/
# sprint/logging_.py → SprintLogger extends PipelineLogger
# sprint/models.py → MonitorState extends BaseMonitorState
```

---

## Phase 5: Visual Consistency Contract

Both runners MUST share these visual constants:

| Element | Value | Enforcement |
|---------|-------|-------------|
| Outer panel border | `blue` | PipelineTUI base |
| Outer panel title | `[bold]SUPERCLAUDE <X> RUNNER[/]` | PipelineTUI base |
| Padding | `(1, 2)` | PipelineTUI base |
| Refresh rate | 2 Hz | PipelineTUI base |
| Screen mode | `False` (inline) | PipelineTUI base |
| Progress bar width | 40 | `build_progress_bar()` |
| Active panel border | `yellow` | Convention (both implement) |
| Success panel border | `green` | `build_terminal_panel()` |
| Failure panel border | `red` | `build_terminal_panel()` |
| Stall → "active" | `green` | Convention |
| Stall → "thinking..." | `yellow` | Convention |
| Stall → "STALLED" | `bold red blink` | Convention |
| TMUX session size | `120x40` | `pipeline/tmux.py` |
| TMUX tail pane | 25% bottom | `pipeline/tmux.py` |
| Stall threshold | 120s | `BaseMonitorState` |
| Thinking threshold | 30s | `BaseMonitorState` |
| Growth EMA alpha | 0.3 | Monitor implementations |
| Table style | `show_header=True, header_style="bold", border_style="dim", box=None` | Convention |

---

## Dependency Changes Summary

### Before

```
sprint/tui.py         → sprint/models.py
sprint/tmux.py        → sprint/models.py
sprint/monitor.py     → sprint/models.py
sprint/notify.py      → sprint/models.py
sprint/debug_logger.py → (none)
sprint/logging_.py    → sprint/models.py

roadmap/executor.py   → pipeline/executor.py, pipeline/process.py
```

### After

```
pipeline/tui.py       → (rich only, no models)
pipeline/tmux.py      → (stdlib only)
pipeline/monitor.py   → (stdlib only)
pipeline/notify.py    → (stdlib only)
pipeline/debug_logger.py → (stdlib only)
pipeline/logging_.py  → pipeline/models.py

sprint/tui.py         → pipeline/tui.py, sprint/models.py
sprint/tmux.py        → pipeline/tmux.py
sprint/monitor.py     → pipeline/monitor.py, sprint/models.py
sprint/logging_.py    → pipeline/logging_.py, sprint/models.py

roadmap/tui.py        → pipeline/tui.py, pipeline/models.py
roadmap/executor.py   → pipeline/executor.py, pipeline/tmux.py,
                         pipeline/monitor.py, pipeline/notify.py,
                         roadmap/tui.py
```

The pipeline layer depends on nothing runner-specific. Both runners depend on pipeline.
Clean dependency inversion.

---

## File Change Summary

| Action | File | Est. Lines |
|--------|------|-----------|
| CREATE | `pipeline/tui.py` | ~100 |
| CREATE | `pipeline/tmux.py` | ~180 |
| CREATE | `pipeline/monitor.py` | ~120 |
| CREATE | `pipeline/logging_.py` | ~100 |
| MOVE | `sprint/notify.py` → `pipeline/notify.py` | ~60 |
| MOVE | `sprint/debug_logger.py` → `pipeline/debug_logger.py` | ~140 |
| CREATE | `roadmap/tui.py` | ~180 |
| MODIFY | `roadmap/commands.py` | +50 (attach/kill/status, --no-tmux) |
| MODIFY | `roadmap/executor.py` | +80 (TUI integration, refresh thread) |
| MODIFY | `roadmap/models.py` | +10 (no_tmux, tmux_session_name fields) |
| MODIFY | `sprint/tui.py` | ~30 changed (extend PipelineTUI) |
| MODIFY | `sprint/tmux.py` | ~50 changed (delegate to pipeline) |
| MODIFY | `sprint/models.py` | ~10 changed (extend BaseMonitorState) |
| MODIFY | `sprint/monitor.py` | ~5 changed (import base) |
| MODIFY | `sprint/executor.py` | ~10 changed (import paths) |
| MODIFY | `sprint/logging_.py` | ~20 changed (extend PipelineLogger) |
| DELETE | `sprint/notify.py` | -60 (moved) |
| DELETE | `sprint/debug_logger.py` | -140 (moved) |

**Net new code**: ~630 lines (pipeline generics + roadmap TUI)
**Net deleted from sprint**: ~200 lines (moved to pipeline)
**Net modification**: ~135 lines of import/inheritance changes

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sprint regression from import changes | High | Phase 1 tests sprint before Phase 2 |
| Rich thread safety (refresh thread + callbacks) | Medium | TUI `safe_update()` uses `_live_failed` guard |
| TMUX nesting detection breaks | Low | `is_tmux_available()` already handles this |
| Monitor thread leak on exception | Medium | `finally` block stops monitor + refresh |
| Parallel steps confuse TUI | Low | Track `current_steps` as set, display both |
| `--no-tmux` falls back gracefully | Low | Foreground path works independently |

---

## Testing Plan

1. **Unit**: `RoadmapTUI._render()` produces valid Rich objects
2. **Unit**: `TextOutputMonitor` stall detection matches sprint behavior
3. **Unit**: `PipelineTUI` base class render structure matches expected layout
4. **Integration**: `execute_roadmap()` with `--no-tmux --dry-run` produces plan
5. **Integration**: `execute_roadmap()` with mocked `run_step` shows TUI progression
6. **Smoke**: TMUX launch + attach + kill lifecycle
7. **Visual**: Side-by-side screenshots of sprint vs roadmap confirm consistency
