# Sprint TUI/TMUX Reference Guide

> Comprehensive reference for the Sprint CLI Runner's terminal user interface.
> Use this guide when building TUI dashboards for new CLI runners (e.g., roadmap).

**Source**: `src/superclaude/cli/sprint/`
**Last Updated**: 2026-03-07

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [File Inventory](#2-file-inventory)
3. [TMUX Session Management](#3-tmux-session-management)
4. [Rich TUI Dashboard](#4-rich-tui-dashboard)
5. [Output Monitor Thread](#5-output-monitor-thread)
6. [Executor Integration Loop](#6-executor-integration-loop)
7. [Logging & Diagnostics](#7-logging--diagnostics)
8. [Status Models & Display Maps](#8-status-models--display-maps)
9. [Notifications](#9-notifications)
10. [Roadmap Gap Analysis](#10-roadmap-gap-analysis)
11. [Reuse & Centralization Strategy](#11-reuse--centralization-strategy)
12. [Appendix: Code Snippets](#appendix-code-snippets)

---

## 1. Architecture Overview

The Sprint runner layers a full operator-facing terminal interface on top of subprocess execution. The architecture has **5 layers**:

```
┌──────────────────────────────────────────────────────────┐
│                    TMUX Session Layer                     │
│  ┌─────────────────────────────────┐                     │
│  │  Pane 0.0: Rich TUI Dashboard  │  120x30 (top 75%)   │
│  ├─────────────────────────────────┤                     │
│  │  Pane 0.1: tail -f <output>    │  120x10 (bot 25%)   │
│  └─────────────────────────────────┘                     │
│  Session: sc-sprint-<sha1[:8]>  Size: 120x40             │
└──────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌──────────────────┐
│  Rich TUI Layer │  │  Output Monitor  │
│  (tui.py)       │  │  (monitor.py)    │
│  Live + Panel   │  │  NDJSON parser   │
│  Table + Bar    │  │  Daemon thread   │
│  2 Hz refresh   │  │  0.5s poll       │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         ▼                    ▼
┌──────────────────────────────────────────┐
│         Executor Orchestration           │
│         (executor.py)                    │
│  Signal handling, phase loop,            │
│  process management, gate checks         │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│     Subprocess Layer (process.py)        │
│  ClaudeProcess: claude --print           │
│  --output-format stream-json             │
│  stdout → file, stderr → file            │
└──────────────────────────────────────────┘
```

### Data Flow

1. `ClaudeProcess` writes NDJSON to output file
2. `OutputMonitor` (daemon thread) polls file at 0.5s intervals, parses events
3. `MonitorState` is updated with task IDs, tool names, file changes, liveness
4. Executor main loop calls `tui.update()` at ~2 Hz with current `MonitorState`
5. `SprintTUI` re-renders Rich `Panel` with updated table, progress bar, detail panel
6. TMUX bottom pane independently tails the same output file

---

## 2. File Inventory

| File | Lines | Purpose | Depends On |
|------|-------|---------|------------|
| `commands.py` | ~100 | Click CLI: `run`, `attach`, `status`, `logs`, `kill` | config, executor, tmux |
| `config.py` | ~150 | Phase discovery, index parsing | models |
| `models.py` | ~610 | All data types: Phase, SprintConfig, SprintResult, MonitorState, PhaseStatus, GateDisplayState, TurnLedger | pipeline.models |
| `tui.py` | ~270 | Rich dashboard: SprintTUI class | models |
| `tmux.py` | ~230 | Session lifecycle: launch, attach, kill, tail update | models |
| `monitor.py` | ~264 | NDJSON parser daemon thread: OutputMonitor | models |
| `executor.py` | ~816 | Main orchestration loop: execute_sprint | all sprint modules |
| `process.py` | ~330 | ClaudeProcess subclass with sprint hooks | pipeline.process |
| `logging_.py` | ~188 | Dual-format JSONL+Markdown logger | models |
| `diagnostics.py` | ~254 | Failure classification and diagnostic reports | models |
| `notify.py` | ~66 | Desktop notifications (Linux/macOS) | models |
| `kpi.py` | ~150 | Gate & remediation KPI report | pipeline.trailing_gate |
| `debug_logger.py` | ~139 | Crash-safe structured debug logging | — |

### Dependency Graph

```
commands.py
  ├── config.py → models.py → pipeline.models
  ├── executor.py
  │     ├── tui.py → models.py
  │     ├── monitor.py → models.py
  │     ├── process.py → pipeline.process
  │     ├── logging_.py → models.py
  │     ├── diagnostics.py → models.py
  │     ├── notify.py → models.py
  │     └── tmux.py (update_tail_pane)
  └── tmux.py (launch/attach/kill)
```

---

## 3. TMUX Session Management

**File**: `src/superclaude/cli/sprint/tmux.py`

### Session Naming

```python
def session_name(release_dir: Path) -> str:
    h = hashlib.sha1(str(release_dir.resolve()).encode()).hexdigest()[:8]
    return f"sc-sprint-{h}"
```

Convention: `sc-<runner>-<hash>`. For roadmap: use `sc-roadmap-<hash>`.

### Availability Check

```python
def is_tmux_available() -> bool:
    if shutil.which("tmux") is None:
        return False
    return "TMUX" not in os.environ  # prevent nesting
```

### Session Creation (launch_in_tmux)

The full flow:

1. **Build foreground command**: `superclaude sprint run ... --no-tmux`
2. **Create detached session**: `tmux new-session -d -s <name> -x 120 -y 40 <cmd>`
3. **Split window**: `tmux split-window -t <name> -v -p 25 bash -c "touch <file> && tail -f <file>; read"`
4. **Select TUI pane**: `tmux select-pane -t <name>:0.0`
5. **Attach**: `tmux attach-session -t <name>` (blocks until detach/exit)
6. **Read exit code**: From `.sprint-exitcode` sentinel file

Error recovery: If any post-creation step fails, `tmux kill-session -t <name>` cleans up.

### Pane Layout

```
┌──────────────────────────┐
│    Pane 0.0 (top 75%)    │  ← TUI dashboard (SprintTUI)
│    Rich Live display     │
├──────────────────────────┤
│    Pane 0.1 (bot 25%)    │  ← tail -f <current-phase-output>
│    Raw output viewer     │
└──────────────────────────┘
```

- Session dimensions: `120x40`
- Split: `-v -p 25` (vertical, 25% bottom)
- No additional windows or named panes

### Dynamic Pane Retargeting

At each phase transition, the bottom pane is redirected:

```python
def update_tail_pane(tmux_session_name: str, output_file: Path):
    # Send Ctrl-C to kill current tail
    subprocess.run(["tmux", "send-keys", "-t", f"{name}:0.1", "C-c"])
    # Start tailing new file
    subprocess.run(["tmux", "send-keys", "-t", f"{name}:0.1", f"tail -f {quoted}\n"])
```

### Session Lifecycle Commands

| Command | Implementation | Description |
|---------|---------------|-------------|
| `sprint attach` | `attach_to_sprint()` | Finds first `sc-sprint-*` session, attaches |
| `sprint kill` | `kill_sprint(force)` | Graceful (SIGTERM→wait→SIGKILL) or force (kill-session) |
| `sprint status` | Stub | Not yet implemented |
| `sprint logs` | Stub | Not yet implemented |

### Exit Code Handoff

The tmux process writes a sentinel file so the outer caller can propagate the exit code:

```python
(config.release_dir / ".sprint-exitcode").write_text(str(_exitcode))
```

---

## 4. Rich TUI Dashboard

**File**: `src/superclaude/cli/sprint/tui.py`

### SprintTUI Class

```python
class SprintTUI:
    def __init__(self, config: SprintConfig, console: Console | None = None):
        self.config = config
        self.console = console or Console()
        self.sprint_result: Optional[SprintResult] = None
        self.monitor_state = MonitorState()
        self.current_phase: Optional[Phase] = None
        self._live: Optional[Live] = None
        self._live_failed: bool = False
        self.gate_states: dict[int, GateDisplayState] = {}
        self._show_gate_column: bool = getattr(config, "grace_period", 0) > 0
```

### Live Display Configuration

```python
self._live = Live(
    self._render(),
    console=self.console,
    refresh_per_second=2,
    screen=False,  # Inline mode, NOT alternate screen
)
```

- **`screen=False`**: Renders inline in normal terminal buffer (not fullscreen)
- **`refresh_per_second=2`**: 2 Hz maximum refresh rate
- **Error resilience**: TUI rendering errors are caught and sprint continues

### Render Tree

```python
def _render(self) -> Panel:
    header = self._build_header()      # Text: release name + elapsed
    table = self._build_phase_table()  # Table: phase status rows
    progress = self._build_progress()  # Progress: bar + percentage
    detail = self._build_active_panel() # Panel: live phase metrics OR terminal state

    body = RichGroup(header, "", table, "", progress, "", detail)

    return Panel(
        body,
        title="[bold]SUPERCLAUDE SPRINT RUNNER[/]",
        border_style="blue",
        padding=(1, 2),
    )
```

Visual layout:

```
╭────────────── SUPERCLAUDE SPRINT RUNNER ──────────────╮
│                                                        │
│  unified-audit-gating-v2    Elapsed: 5m 23s            │
│                                                        │
│  #  Phase                Status      Duration  Tasks   │
│  1  Extract Requirements  PASS        45s       T01.05 │
│  2  Generate Roadmaps     PASS        2m 10s    T02.12 │
│  3  Adversarial Debate    RUNNING     1m 28s    T03.03 │
│  4  Final Merge           pending     -         -      │
│                                                        │
│  Progress ████████████░░░░░░░░░░░░░░░░░░░  50%  2/4   │
│                                                        │
│  ╭── ACTIVE: Phase 3 ──╮                              │
│  │ File:    phase-3-tasklist.md                        │
│  │ Status:  RUNNING -- active                         │
│  │                                                     │
│  │ Last task:     T03.03                              │
│  │ Last tool:     Edit                                │
│  │ Output size:   245.3 KB  (+1024.0 B/s)            │
│  │ Files changed: 7                                    │
│  ╰─────────────────────╯                              │
│                                                        │
╰────────────────────────────────────────────────────────╯
```

### Component Details

#### Header (`_build_header`)

```python
Text.from_markup(f"[dim]{index_name}[/]    Elapsed: [bold]{elapsed}[/]")
```

- `index_name`: Parent directory name of index path
- `elapsed`: From `SprintResult.duration_display` (e.g., `5m 23s`)

#### Phase Table (`_build_phase_table`)

Columns:

| Column | Width | Justify | Content |
|--------|-------|---------|---------|
| `#` | 3 | right | Phase number |
| `Phase` | min 30 | left | `phase.display_name` |
| `Status` | 12 | center | Status icon with color |
| `Gate` | 6 | center | Gate icon (conditional) |
| `Duration` | 10 | right | Elapsed or final time |
| `Tasks` | 8 | center | Last task ID |

Table configuration:
```python
Table(show_header=True, header_style="bold", border_style="dim", pad_edge=False, box=None)
```

Status logic per row:
- If phase has a terminal result → use result status
- If phase is current and not terminal → force `RUNNING`
- Pending phases → `PENDING`

Duration logic:
- Terminal phases → `result.duration_display` (e.g., `2m 10s`)
- Running phase → `{int(monitor_state.stall_seconds)}s`
- Pending phases → `-`

Gate column: Only shown when `config.grace_period > 0`.

#### Progress Bar (`_build_progress`)

```python
Progress(
    TextColumn("[bold]Progress"),
    BarColumn(bar_width=40),
    TextColumn("{task.percentage:>3.0f}%"),
    TextColumn("[dim]{task.completed}/{task.total} tasks[/]"),
)
```

- `total` = number of active phases
- `completed` = count of phases with success status

#### Active Panel (`_build_active_panel`)

When a phase is running:
```
╭── ACTIVE: Phase 3 ──╮
│ File:    phase-3-tasklist.md
│ Status:  RUNNING -- active
│
│ Last task:     T03.03
│ Last tool:     Edit
│ Output size:   245.3 KB  (+1024.0 B/s)
│ Files changed: 7
╰──────────────────────╯
```

Stall display coloring:
- `"active"` → `green`
- `"thinking..."` → `yellow`
- `"STALLED"` → `bold red blink`

Border: `border_style="yellow"`

#### Terminal Panels

**Success**:
```python
Panel(content, title="[bold green]Sprint Complete[/]", border_style="green")
# Content: "Result: ALL PHASES PASSED\nLog: <path>"
```

**Failure**:
```python
Panel(content, title="[bold red]Sprint Halted[/]", border_style="red")
# Content: "Result: HALTED\nHalted at Phase N\nResume: <command>"
```

### Error Resilience

The TUI is designed to never crash the sprint:

```python
def update(self, ...):
    try:
        self._live.update(self._render())
    except Exception as exc:
        self._live_failed = True
        print(f"[TUI] Display error (continuing sprint): {exc}", file=sys.stderr)
```

Once `_live_failed` is set, no further render attempts are made.

---

## 5. Output Monitor Thread

**File**: `src/superclaude/cli/sprint/monitor.py`

### OutputMonitor Class

The monitor runs as a daemon thread, reading the NDJSON output file incrementally.

```python
class OutputMonitor:
    def __init__(self, output_path: Path, poll_interval: float = 0.5):
        self.state = MonitorState()
        self._stop_event = threading.Event()
        self._last_read_pos: int = 0
        self._line_buffer: str = ""
        self._seen_files: set[str] = set()
```

### Poll Cycle

Each 0.5s:
1. `stat()` the output file for current size
2. If size > last read position → read incremental chunk
3. Split chunk into complete lines (buffer partial lines)
4. Parse each line as JSON (fallback: regex extraction)
5. Update `MonitorState` with extracted signals
6. Calculate growth rate (exponential moving average, α=0.3)
7. Update stall counter if no new data

### Signal Extraction

**From structured NDJSON events** (`_extract_signals_from_event`):
- `tool_use` events → extract `tool` field

**From text via regex** (`_extract_signals_from_text`):
- Task IDs: `T\d{2}\.\d{2}` (e.g., `T03.05`)
- Tool names: `Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task`
- File changes: `(?:modified|created|edited|wrote|updated)\s+[path]`

### MonitorState Fields

| Field | Type | Source | TUI Usage |
|-------|------|--------|-----------|
| `output_bytes` | int | File stat | Output size display |
| `growth_rate_bps` | float | EMA calculation | Growth rate display |
| `last_task_id` | str | Regex extraction | Tasks column |
| `last_tool_used` | str | NDJSON/regex | Active panel |
| `files_changed` | int | Regex set count | Active panel |
| `events_received` | int | Line counter | Debug/stall logic |
| `stall_seconds` | float | Time delta | Stall display |
| `stall_status` | property | Derived | Active panel coloring |

### Stall Detection

```python
@property
def stall_status(self) -> str:
    if self.events_received == 0:
        if now - self.phase_started_at > 120: return "STALLED"
        return "waiting..."
    since_last = now - self.last_event_time
    if since_last > 120: return "STALLED"
    if since_last > 30: return "thinking..."
    return "active"
```

### Budget Exhaustion Detection

```python
def detect_error_max_turns(output_path: Path) -> bool:
    # Scans last non-empty NDJSON line for "subtype":"error_max_turns"
```

### Turn Counting

```python
def count_turns_from_output(output_path: Path) -> int:
    # Counts lines containing "type":"assistant"
```

---

## 6. Executor Integration Loop

**File**: `src/superclaude/cli/sprint/executor.py`

### execute_sprint() Flow

```python
def execute_sprint(config: SprintConfig):
    # 1. Pre-flight: verify claude binary
    # 2. Install signal handlers
    # 3. Setup debug logger
    # 4. Create SprintLogger, SprintTUI, OutputMonitor
    # 5. Write header to execution log
    # 6. tui.start()

    for phase in config.active_phases:
        # 7. Check shutdown flag
        # 8. Reset monitor for phase output file
        # 9. Start monitor thread
        # 10. Update tmux tail pane (if applicable)
        # 11. Launch ClaudeProcess
        # 12. Log phase start

        while process.poll() is None:
            # 13. Check shutdown signal
            # 14. Check timeout deadline (monotonic)
            # 15. Check stall watchdog
            # 16. tui.update(sprint_result, monitor.state, phase)
            # 17. sleep(0.5)

        # 18. Read exit code
        # 19. Stop monitor
        # 20. Determine phase status
        # 21. Create PhaseResult
        # 22. Log + notify
        # 23. Update TUI
        # 24. If failure: collect diagnostics, set HALTED, break

    # 25. Finalize sprint result
    # 26. Final TUI update
    # 27. Write summary log
    # 28. Notify completion

    # finally:
    # 29. Stop monitor, terminate process, stop TUI, uninstall signals
    # 30. Write .sprint-exitcode sentinel
```

### TUI Update Call Pattern

The executor calls `tui.update()` in three contexts:

1. **During phase execution** (in poll loop, every 0.5s):
   ```python
   tui.update(sprint_result, monitor.state, phase)  # phase = current
   ```

2. **After phase completion** (before deciding continue/halt):
   ```python
   tui.update(sprint_result, monitor.state, None)  # phase = None → pending
   ```

3. **At sprint end** (final render with terminal panel):
   ```python
   tui.update(sprint_result, MonitorState(), None)  # fresh monitor, no phase
   ```

### Watchdog Integration

```python
if config.stall_timeout > 0 and ms.stall_seconds > config.stall_timeout:
    if config.stall_action == "kill":
        print(f"[WATCHDOG] Stall detected ... killing phase {phase.number}", file=sys.stderr)
        proc_manager.terminate()
        break
    else:
        print(f"[WATCHDOG] Stall detected ... warning for phase {phase.number}", file=sys.stderr)
```

Single-fire guard resets when output resumes (`stall_seconds == 0.0`).

---

## 7. Logging & Diagnostics

### SprintLogger (`logging_.py`)

**Dual-format**: JSONL (machine-readable) + Markdown (human-readable)

| Severity | JSONL | Markdown | Screen | Terminal Bell |
|----------|-------|----------|--------|---------------|
| DEBUG | Yes | No | No | No |
| INFO | Yes | Yes | `[green][INFO]` | No |
| WARN | Yes | Yes | `[yellow][WARN]` | No |
| ERROR | Yes | Yes | `[bold red][ERROR]` | Yes (`\a`) |

Status-to-severity mapping:
- `PASS_NO_SIGNAL` → DEBUG (JSONL only)
- `PASS`, `PASS_NO_REPORT` → INFO
- `HALT`, `TIMEOUT` → WARN
- `ERROR` → ERROR

Console: `Console(stderr=True)` — TUI uses stdout, logger uses stderr.

### Debug Logger (`debug_logger.py`)

- Crash-safe: flushes after every write
- Structured format: `2026-03-04T19:00:00.123 DEBUG [executor] poll_tick pid=1234`
- Version header: `# debug-log-version: 1.0`
- Zero-overhead when disabled (NullHandler + level > CRITICAL)

### Diagnostics (`diagnostics.py`)

On phase failure, the executor collects:

```python
collector = DiagnosticCollector(config)
bundle = collector.collect(phase, phase_result, monitor.state)
classifier = FailureClassifier()
bundle.category = classifier.classify(bundle)  # STALL|TIMEOUT|CRASH|ERROR|UNKNOWN
reporter = ReportGenerator()
reporter.write(bundle, f"phase-{N}-diagnostic.md")
```

Classification priority:
1. **STALL**: Watchdog triggered OR stall_duration > 120s
2. **TIMEOUT**: Exit code 124
3. **CRASH**: Non-zero exit + low stall duration
4. **ERROR**: HALT/ERROR status
5. **UNKNOWN**: No clear pattern

---

## 8. Status Models & Display Maps

**File**: `src/superclaude/cli/sprint/models.py`

### PhaseStatus Enum

| Status | Terminal? | Success? | Failure? | Style | Icon |
|--------|-----------|----------|----------|-------|------|
| `PENDING` | No | No | No | `dim` | `[dim]pending[/]` |
| `RUNNING` | No | No | No | `bold yellow` | `[yellow]RUNNING[/]` |
| `PASS` | Yes | Yes | No | `bold green` | `[green]PASS[/]` |
| `PASS_NO_SIGNAL` | Yes | Yes | No | `green` | `[green]PASS[/]` |
| `PASS_NO_REPORT` | Yes | Yes | No | `green` | `[green]PASS[/]` |
| `INCOMPLETE` | Yes | No | Yes | `bold red` | `[red]INCOMPLETE[/]` |
| `HALT` | Yes | No | Yes | `bold red` | `[red]HALT[/]` |
| `TIMEOUT` | Yes | No | Yes | `bold red` | `[red]TIMEOUT[/]` |
| `ERROR` | Yes | No | Yes | `bold red` | `[red]ERROR[/]` |
| `SKIPPED` | Yes | No | No | `dim strikethrough` | `[dim]skipped[/]` |

### GateDisplayState Enum

| State | Color | Icon | Label |
|-------|-------|------|-------|
| `NONE` | `dim` | `—` | No gate |
| `CHECKING` | `bold cyan` | `⏳` | Checking |
| `PASS` | `bold green` | `✓` | Passed |
| `FAIL_DEFERRED` | `bold yellow` | `⚠` | Deferred |
| `REMEDIATING` | `bold magenta` | `🔧` | Remediating |
| `REMEDIATED` | `green` | `✓✓` | Remediated |
| `HALT` | `bold red` | `✗` | Halted |

Valid transitions:
```
NONE → CHECKING → PASS
NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → REMEDIATED
NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → HALT
```

### SprintOutcome Enum

| Outcome | When |
|---------|------|
| `SUCCESS` | All phases passed |
| `HALTED` | A phase failed |
| `INTERRUPTED` | SIGINT/SIGTERM received |
| `ERROR` | Unexpected failure |

---

## 9. Notifications

**File**: `src/superclaude/cli/sprint/notify.py`

Cross-platform, best-effort desktop notifications:

| Platform | Tool | Method |
|----------|------|--------|
| Linux | `notify-send` | `notify-send [--urgency critical] <title> <message>` |
| macOS | `osascript` | `display notification "<msg>" with title "<title>"` |

Triggers:
- Phase failure → urgent notification
- Phase success → normal notification
- Sprint complete → normal (success) or urgent (failure)

---

## 10. Roadmap Gap Analysis

### Current Roadmap TUI Status: **None**

The roadmap runner (`src/superclaude/cli/roadmap/`) has:
- No TMUX integration
- No Rich TUI dashboard
- No output monitor thread
- No real-time progress display
- No desktop notifications
- No diagnostics collection
- No attach/kill/status/logs commands

Its current interface is plain `print()` statements:
```
[roadmap] Starting step: extract
[roadmap] Step extract  PASS (attempt 1, 45s)
[roadmap] Starting step: generate-opus-architect
...
```

### Feature Gap Table

| Feature | Sprint | Roadmap | Effort to Add |
|---------|--------|---------|---------------|
| TMUX session | Yes | No | Low (reuse tmux.py) |
| Rich dashboard | Yes | No | Medium (adapt tui.py) |
| Live progress bar | Yes | No | Low (reuse Progress) |
| Step status table | Yes (phases) | No | Low (adapt table) |
| Output monitor | Yes (NDJSON) | N/A (text mode) | Medium (text mode monitor) |
| Active detail panel | Yes | No | Low (adapt panel) |
| Terminal state panel | Yes | No | Low (copy pattern) |
| Attach/kill commands | Yes | No | Low (copy from sprint) |
| Dual-format logging | Yes | No | Low (adapt logger) |
| Desktop notifications | Yes | No | Very low (copy notify.py) |
| Diagnostic reports | Yes | No | Medium (adapt to steps) |
| Error resilience | Yes | No | Low (copy pattern) |

---

## 11. Reuse & Centralization Strategy

### Tier 1: Direct Reuse (Copy or Import)

These sprint modules can be used by roadmap with minimal or no changes:

| Module | Reuse Strategy | Changes Needed |
|--------|---------------|----------------|
| `tmux.py` | **Centralize to pipeline/** | Parameterize session prefix (`sc-sprint-` → configurable) |
| `notify.py` | **Centralize to pipeline/** | Already generic, just import |
| `debug_logger.py` | **Centralize to pipeline/** | Already generic |
| `diagnostics.py` | **Centralize to pipeline/** | Generalize Phase→Step, PhaseResult→StepResult |

### Tier 2: Adapt with Generics (Moderate Effort)

These need a generic base class that both runners extend:

#### Generic TUI Base Class

```python
# Proposed: src/superclaude/cli/pipeline/tui.py

class PipelineTUI:
    """Generic Rich TUI for any pipeline runner."""

    def __init__(self, title: str, console: Console | None = None):
        self.console = console or Console()
        self._live: Optional[Live] = None
        self._live_failed: bool = False

    def start(self) -> Live: ...
    def stop(self): ...

    @abstractmethod
    def _render(self) -> Panel: ...

    def _build_progress(self, completed: int, total: int, label: str) -> Progress:
        """Reusable progress bar builder."""
        ...

    def _build_terminal_panel(self, success: bool, content: str, ...) -> Panel:
        """Reusable success/failure terminal panel."""
        ...
```

Sprint and roadmap would each extend this with their domain-specific table and detail panel.

#### Generic Output Monitor

The sprint monitor parses NDJSON (`stream-json`). Roadmap uses `text` output format.

Options:
1. **Text mode monitor**: Simpler — just track file growth, stall detection, no signal extraction
2. **Dual-mode monitor**: Configure format at init, parse accordingly

Recommended: Option 1 — a `TextOutputMonitor` that tracks:
- Output file size and growth rate
- Stall detection (same logic)
- Line count
- No task/tool signal extraction (not applicable to text mode)

#### Generic Logger

```python
# Proposed: src/superclaude/cli/pipeline/logging_.py

class PipelineLogger:
    """Dual-format JSONL+Markdown logger for any pipeline runner."""

    def __init__(self, config: PipelineConfig, runner_name: str): ...
    def write_header(self, metadata: dict): ...
    def write_step_start(self, step_id: str, step_name: str): ...
    def write_step_result(self, step_id: str, status: str, duration: str): ...
    def write_summary(self, outcome: str, stats: dict): ...
```

### Tier 3: Runner-Specific (Keep Separate)

| Module | Reason |
|--------|--------|
| `executor.py` | Orchestration logic fundamentally differs |
| `process.py` | Sprint uses `stream-json`, roadmap uses `text` |
| `config.py` | Sprint discovers phases from index files; roadmap builds steps from spec |
| `kpi.py` | Sprint-specific gate metrics |

### Proposed File Layout After Centralization

```
src/superclaude/cli/pipeline/
├── models.py          # (existing) PipelineConfig, Step, StepResult
├── process.py         # (existing) ClaudeProcess base
├── executor.py        # (existing) execute_pipeline
├── gates.py           # (existing) gate_passed
├── trailing_gate.py   # (existing)
├── tui.py             # (NEW) PipelineTUI base class
├── tmux.py            # (MOVED) Generic TMUX session management
├── monitor.py         # (NEW) TextOutputMonitor + base interface
├── logging_.py        # (NEW) PipelineLogger base
├── notify.py          # (MOVED) Desktop notifications
├── debug_logger.py    # (MOVED) Crash-safe debug logging
└── diagnostics.py     # (NEW) Generic diagnostic framework

src/superclaude/cli/sprint/
├── commands.py        # Sprint-specific CLI
├── config.py          # Phase discovery
├── models.py          # Sprint-specific models (PhaseStatus etc.)
├── tui.py             # SprintTUI(PipelineTUI)
├── monitor.py         # NdjsonOutputMonitor(BaseMonitor)
├── executor.py        # Sprint orchestration
├── process.py         # Sprint ClaudeProcess
├── logging_.py        # SprintLogger(PipelineLogger)
└── kpi.py             # Sprint-specific KPI

src/superclaude/cli/roadmap/
├── commands.py        # Roadmap CLI (add attach/kill/status)
├── models.py          # RoadmapConfig
├── tui.py             # RoadmapTUI(PipelineTUI) — NEW
├── executor.py        # Roadmap orchestration (add TUI integration)
├── prompts.py         # Prompt builders
└── gates.py           # Gate criteria
```

---

## Appendix: Code Snippets

### A. Minimal TUI Integration for a New Runner

The smallest viable TUI integration requires:

```python
# In your executor:
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text
from rich.console import Group as RichGroup

class MyRunnerTUI:
    def __init__(self):
        self.console = Console()
        self._live = None
        self._live_failed = False

    def start(self):
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=2,
            screen=False,
        )
        self._live.start()

    def stop(self):
        if self._live:
            self._live.stop()

    def update(self, steps, current_step_idx, elapsed):
        if self._live and not self._live_failed:
            try:
                self._live.update(self._render())
            except Exception:
                self._live_failed = True

    def _render(self) -> Panel:
        # Build your components here
        body = RichGroup(header, "", table, "", progress, "", detail)
        return Panel(body, title="[bold]MY RUNNER[/]", border_style="blue", padding=(1, 2))
```

### B. Status Style Pattern

```python
STATUS_STYLES = {
    "pass":    "bold green",
    "fail":    "bold red",
    "running": "bold yellow",
    "pending": "dim",
    "skipped": "dim strikethrough",
}

STATUS_ICONS = {
    "pass":    "[green]PASS[/]",
    "fail":    "[red]FAIL[/]",
    "running": "[yellow]RUNNING[/]",
    "pending": "[dim]pending[/]",
    "skipped": "[dim]skipped[/]",
}
```

### C. TMUX Session Template

```python
def launch_in_tmux(session_prefix, foreground_cmd, initial_tail_file):
    name = f"{session_prefix}-{hash_dir()}"

    # Create session with main command
    subprocess.run(["tmux", "new-session", "-d", "-s", name, "-x", "120", "-y", "40", *foreground_cmd])

    # Add tail pane
    subprocess.run(["tmux", "split-window", "-t", name, "-v", "-p", "25",
                     "bash", "-c", f"touch {file} && tail -f {file}; read"])

    # Select main pane
    subprocess.run(["tmux", "select-pane", "-t", f"{name}:0.0"])

    # Attach (blocks)
    subprocess.run(["tmux", "attach-session", "-t", name])
```

### D. Progress Bar Template

```python
def build_progress(completed: int, total: int, label: str = "Progress") -> Progress:
    progress = Progress(
        TextColumn(f"[bold]{label}"),
        BarColumn(bar_width=40),
        TextColumn("{task.percentage:>3.0f}%"),
        TextColumn("[dim]{task.completed}/{task.total} steps[/]"),
    )
    progress.add_task("pipeline", total=total, completed=completed)
    return progress
```

### E. Error-Resilient Update Pattern

```python
def update(self, ...):
    if self._live and not self._live_failed:
        try:
            self._live.update(self._render())
        except Exception as exc:
            import sys
            self._live_failed = True
            print(f"[TUI] Display error (continuing): {exc}", file=sys.stderr)
```

---

## Quick Reference Card

| Aspect | Sprint Value | Recommended Default |
|--------|-------------|-------------------|
| Panel title | `SUPERCLAUDE SPRINT RUNNER` | `SUPERCLAUDE <RUNNER> RUNNER` |
| Border color | `blue` | `blue` |
| Active panel border | `yellow` | `yellow` |
| Success panel border | `green` | `green` |
| Failure panel border | `red` | `red` |
| Refresh rate | 2 Hz | 2 Hz |
| Screen mode | `False` (inline) | `False` (inline) |
| Session prefix | `sc-sprint-` | `sc-<runner>-` |
| Session size | `120x40` | `120x40` |
| Bottom pane | 25% | 25% |
| Poll interval | 0.5s | 0.5s |
| Stall threshold | 120s | 120s |
| Thinking threshold | 30s | 30s |
| Growth EMA alpha | 0.3 | 0.3 |
