# Specification: `superclaude roadmap` CLI Command

**Version**: v1.1
**Status**: Draft
**Date**: 2026-03-04
**Source**: Brainstorming session + sc:spec-panel review
**Output directory**: `.dev/releases/current/v2.06-RoadmapCLI/`

---

## 1. Problem Statement

The `/sc:roadmap` skill executes inside a single Claude Code context where all steps — extraction, variant generation, adversarial debate, merge — run as behavioral instructions within the same session. This makes fabrication structurally possible: Claude can skip expensive steps (e.g. actually invoking sc:adversarial-protocol) and self-report completion. The skill-to-skill invocation chain fails silently.

**Root cause**: Claude controls its own workflow. Nothing external enforces step completion before the next step begins.

**Solution**: A CLI command (`superclaude roadmap`) that acts as a conductor — calling Claude as a subprocess once per step, with a file-on-disk gate between each step. Claude cannot advance to step N+1 because the CLI hasn't issued that prompt yet. Fabrication becomes impossible without writing the required output files.

---

## 2. Scope

### In Scope (v1)
- `superclaude roadmap <spec-file>` CLI command
- 8-step pipeline (extract → generate-A/B in parallel → diff → debate → score → merge → test-strategy)
- Shared `pipeline/` base module extracted from `sprint/`
- Sprint migration to use `pipeline/` internals
- Gate validation: file existence + YAML frontmatter fields + minimum line count
- Retry-once-then-halt failure policy
- `--resume` flag for restarting from failed step
- `--dry-run` flag for plan preview
- Single PR delivery (pipeline/ extraction + sprint migration + roadmap/ all together)

### Out of Scope (v1)
- TUI / rich progress display (stdout logging only)
- `--blind` adversarial mode flag
- Multi-spec consolidation (`--specs`)
- Tasklist generation from roadmap output
- `--agents` count > 2 (v1 supports exactly 2 agents for generate-A / generate-B)

---

## 3. Architecture

### 3.1 Module Structure

```
src/superclaude/cli/
  pipeline/                  ← NEW: shared base, both sprint and roadmap extend it
    __init__.py
    process.py               ← ClaudeProcess (moved from sprint/process.py)
    executor.py              ← execute_pipeline(): generic step sequencer
    models.py                ← PipelineConfig, Step, StepResult, StepStatus
    gates.py                 ← gate_passed() validator
  sprint/                    ← MIGRATED: imports from pipeline/ instead of owning logic
    __init__.py
    commands.py              ← unchanged external API
    config.py                ← SprintConfig extends PipelineConfig (new inheritance)
    executor.py              ← execute_sprint() wraps execute_pipeline()
    models.py                ← SprintStep extends Step; PhaseResult extends StepResult
    process.py               ← re-exports ClaudeProcess from pipeline.process
    monitor.py               ← unchanged
    tui.py                   ← unchanged
    tmux.py                  ← unchanged
    logging_.py              ← unchanged
    notify.py                ← unchanged
  roadmap/                   ← NEW
    __init__.py
    commands.py              ← Click entry point; registered in main.py
    models.py                ← RoadmapConfig extends PipelineConfig; RoadmapStep extends Step
    prompts.py               ← per-step prompt builders (pure functions, no I/O)
    gates.py                 ← roadmap gate definitions (data, not logic)
    executor.py              ← execute_roadmap() wraps execute_pipeline()
```

### 3.2 `pipeline/` Interface Contract

`PipelineConfig` — fields shared by both sprint and roadmap:

```python
@dataclass
class PipelineConfig:
    work_dir: Path          # where output files are written
    dry_run: bool = False
    max_turns: int = 50     # passed to each claude -p subprocess
    model: str = ""         # empty = claude default; accepts shorthand (opus/sonnet/haiku)
    permission_flag: str = "--dangerously-skip-permissions"
    debug: bool = False
```

`SprintConfig` retains sprint-specific fields (not in `PipelineConfig`):
- `index_path`, `release_dir`, `phases`, `start_phase`, `end_phase`
- `stall_timeout`, `stall_action`, `phase_timeout`
- `tmux_session_name`

`RoadmapConfig` adds roadmap-specific fields (not in `PipelineConfig`):
- `spec_file: Path`
- `agents: list[AgentSpec]`  (default: `[AgentSpec("opus","architect"), AgentSpec("haiku","architect")]`)
- `depth: Literal["quick","standard","deep"]`  (default: `"standard"`)
- `output_dir: Path`  (default: parent dir of spec_file)

`Step` — a single pipeline step:

```python
@dataclass
class Step:
    id: str                  # e.g. "extract", "generate-opus", "diff"
    prompt: str              # full prompt text passed to claude -p
    output_file: Path        # gate checks this file
    gate: GateCriteria       # what constitutes a passing output
    timeout_seconds: int     # hard timeout for this step's subprocess
    inputs: list[Path]       # files this step reads (injected into prompt context)
    retry_limit: int = 1     # default: retry once on gate failure
```

`StepResult`:

```python
@dataclass
class StepResult:
    step: Step
    status: StepStatus       # PASS | FAIL | TIMEOUT | SKIPPED
    attempt: int             # 1 or 2 (retry)
    gate_failure_reason: str | None   # populated on FAIL
    started_at: datetime
    finished_at: datetime
```

`GateCriteria`:

```python
@dataclass
class GateCriteria:
    required_frontmatter_fields: list[str]
    min_lines: int
```

`gate_passed()` in `pipeline/gates.py`:

```python
def gate_passed(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]:
    """
    Returns (True, None) on pass.
    Returns (False, reason) on failure where reason is a human-readable message.

    Failure reasons:
    - "File not found: {path}"
    - "File empty (0 bytes): {path}"
    - "Below minimum line count: {actual} < {required} in {path}"
    - "YAML frontmatter missing or unparseable in {path}: {parse_error}"
    - "Missing required frontmatter field '{field}' in {path}"
    """
```

Note: `gate_passed()` is pure Python — no subprocess, no Claude invocation.

### 3.3 Context Isolation

Each step receives its context exclusively through the prompt string and the `--file` flags passed to `claude -p`. The executor builds the prompt by calling the step's prompt builder function (in `roadmap/prompts.py`) with the paths of the step's `inputs` list. No shared in-memory state passes between steps. Each subprocess is a fresh `claude -p` invocation with no session continuity.

Prompt injection pattern (enforced by executor):
```
claude -p "<step.prompt>" \
  --file <input_1> \
  --file <input_2> \
  --model <agent.model> \
  --max-turns <config.max_turns> \
  <config.permission_flag>
```

The executor does not pass `--continue` or any session ID between steps.

---

## 4. Pipeline Steps

Steps 2a and 2b (generate-A and generate-B) run as concurrent subprocesses. Step 3a (diff) waits for both generate steps' gates to pass before starting.

All other steps are sequential.

### Step Definitions

| ID | Name | Inputs | Output file | Required frontmatter fields | Min lines | Timeout |
|----|------|--------|-------------|----------------------------|-----------|---------|
| `extract` | Extract requirements | spec-file | `extraction.md` | `functional_requirements`, `complexity_score`, `complexity_class` | 50 | 300s |
| `generate-{agent.id}` | Generate variant (×2, parallel) | extraction.md | `roadmap-{agent.id}.md` | `spec_source`, `complexity_score`, `primary_persona` | 100 | 900s |
| `diff` | Diff analysis | roadmap-A.md, roadmap-B.md | `diff-analysis.md` | `total_diff_points`, `shared_assumptions_count` | 30 | 300s |
| `debate` | Structured debate | diff-analysis.md, roadmap-A.md, roadmap-B.md | `debate-transcript.md` | `convergence_score`, `rounds_completed` | 50 | 600s |
| `score` | Base selection + scoring | debate-transcript.md, roadmap-A.md, roadmap-B.md | `base-selection.md` | `base_variant`, `variant_scores` | 20 | 300s |
| `merge` | Merge to final roadmap | base-selection.md, roadmap-A.md, roadmap-B.md, debate-transcript.md | `roadmap.md` | `spec_source`, `complexity_score`, `adversarial` | 150 | 600s |
| `test-strategy` | Test strategy | roadmap.md, extraction.md | `test-strategy.md` | `validation_milestones`, `interleave_ratio` | 40 | 300s |

**Timeout rationale**:
- `generate-{agent}`: 900s (15 min) — full roadmap generation with adversarial variant is the most expensive single step
- `debate`: 600s (10 min) — structured multi-round debate
- `merge`: 600s (10 min) — synthesis across multiple large artifacts
- All other steps: 300s (5 min) — bounded, single-concern tasks

### Step Output Directory

All output files are written to `config.output_dir`. By default this is the parent directory of `spec_file`:

```
spec:   .dev/releases/current/v2.07/spec.md
output: .dev/releases/current/v2.07/
  extraction.md
  roadmap-opus-architect.md
  roadmap-haiku-architect.md
  diff-analysis.md
  debate-transcript.md
  base-selection.md
  roadmap.md
  test-strategy.md
```

---

## 5. CLI Interface

```
superclaude roadmap <spec-file> [OPTIONS]

Arguments:
  spec-file          Path to specification markdown file (required)

Options:
  --agents TEXT      Comma-separated agent specs: model[:persona]
                     Default: "opus:architect,haiku:architect"
                     Model shorthand (opus/sonnet/haiku) passed directly to
                     claude CLI — no resolution required.

  --output PATH      Output directory for all artifacts.
                     Default: parent directory of spec-file.

  --depth [quick|standard|deep]
                     Controls debate step round count.
                     quick=1 round, standard=2, deep=3.
                     Default: standard

  --resume           Skip steps whose output files already pass their gates.
                     Re-run from the first step that fails its gate.
                     If spec-file has changed since last run: warn user and
                     force re-run of the extract step regardless of gate state.
                     (See §7.3 for stale-spec detection.)

  --dry-run          Print step plan and gate criteria to stdout. Exit without
                     launching any subprocesses.

  --model TEXT       Override model for all steps. Normally model is set
                     per-agent for generate steps; this flag overrides all.

  --max-turns INT    Max turns passed to each claude -p invocation.
                     Default: 50

  --debug            Enable debug logging to output_dir/roadmap-debug.log
```

### Registration in `main.py`

```python
from superclaude.cli.roadmap import roadmap_group
main.add_command(roadmap_group, name="roadmap")
```

---

## 6. Failure Policy

### 6.1 Step Execution Flow

```
for each step (in order):
  attempt 1:
    launch claude -p subprocess
    wait for subprocess exit (with timeout)
    run gate_passed()
    if gate passes → record StepResult(PASS, attempt=1), continue to next step
    if gate fails  → log gate_failure_reason, proceed to attempt 2
    if timeout     → log timeout, proceed to attempt 2

  attempt 2 (retry):
    same prompt, same inputs, fresh subprocess
    run gate_passed()
    if gate passes → record StepResult(PASS, attempt=2), continue to next step
    if gate fails  → HALT: record StepResult(FAIL), report to user, exit non-zero
    if timeout     → HALT: record StepResult(TIMEOUT), report to user, exit non-zero
```

Parallel steps (generate-A, generate-B): each follows this flow independently. If either halts, the pipeline halts — the other subprocess is terminated.

### 6.2 HALT Output

On halt, the CLI prints to stderr:

```
ERROR: Roadmap pipeline halted at step 'generate-opus-architect' (attempt 2/2)
  Gate failure: Missing required frontmatter field 'primary_persona' in roadmap-opus-architect.md
  Output file: .dev/releases/current/v2.07/roadmap-opus-architect.md
  Output size: 847 bytes (86 lines)
  Step timeout: 900s | Elapsed: 234s

Completed steps: extract (PASS, attempt 1)
Failed step:     generate-opus-architect (FAIL, attempt 2)
Skipped steps:   generate-haiku-architect, diff, debate, score, merge, test-strategy

To retry from this step:
  superclaude roadmap spec.md --resume

To inspect the failing output:
  cat .dev/releases/current/v2.07/roadmap-opus-architect.md
```

### 6.3 Resume Behavior

`--resume` checks each step's gate in order. The first step that fails its gate is re-run (with its full 2-attempt retry policy). All prior steps that pass their gates are skipped.

**Stale spec detection**: On `--resume`, the CLI computes a SHA-256 hash of the spec-file and compares it to a hash stored in `output_dir/.roadmap-state.json` (written after the extract step passes). If the hashes differ:

```
WARNING: spec-file has changed since last run.
  Last run: 2026-03-04T18:22:00Z  hash: abc123...
  Current:                         hash: def456...

The extraction artifact may be stale. Forcing re-run of extract step.
Other completed steps will be reused if their gates still pass.

Continue? [Y/n]
```

The extract step is always re-run when the spec hash changes, regardless of whether `extraction.md` passes its gate.

---

## 7. Progress Display

While a step is running, the CLI emits to stdout:

```
[roadmap] Step 2/7: generate-opus-architect
  Model:   claude opus (architect)
  Timeout: 900s
  Elapsed: 00:01:43 ...
```

Updated every 5 seconds (overwrite the same line using `\r`). On step completion:

```
[roadmap] Step 2/7: generate-opus-architect  PASS (attempt 1, 1m43s)
           Gate: roadmap-opus-architect.md — 312 lines, frontmatter OK
```

On parallel steps:

```
[roadmap] Step 2a/7: generate-opus-architect   00:01:43 ...
[roadmap] Step 2b/7: generate-haiku-architect  00:01:21 ...
```

---

## 8. Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-01 | `superclaude roadmap <spec>` executes steps in the defined sequence with gates enforced between each step | Core |
| FR-02 | Steps generate-A and generate-B launch as concurrent subprocesses; step diff waits for both gates to pass | Core |
| FR-03 | Each step's prompt is built from only the files in its `inputs` list; no other context is passed to the subprocess | Core |
| FR-04 | `gate_passed()` checks: file exists AND non-empty AND line count >= minimum AND YAML frontmatter parseable AND all required fields present | Wiegers |
| FR-05 | On gate failure: retry once (same prompt), then halt with diagnostic output per §6.2 | Core |
| FR-06 | `--resume` skips steps whose output files pass their gates; forces extract re-run if spec-file hash changed | Newman |
| FR-07 | `--dry-run` prints step plan (step ID, output file, gate criteria, timeout) and exits without subprocess invocations | Core |
| FR-08 | Default output directory is the parent directory of the spec-file | Core |
| FR-09 | `superclaude roadmap` registered as a Click command group in `main.py` | Core |
| FR-10 | Sprint module migrated to import `ClaudeProcess`, generic step execution from `pipeline/`; sprint's external CLI API unchanged | Fowler |
| FR-11 | `gate_passed()` returns `(bool, str | None)` — failure reason is a human-readable string per the defined message format | Adzic |
| FR-12 | `.roadmap-state.json` written to `output_dir` after extract step passes, containing spec-file SHA-256 hash and timestamp | Newman |
| FR-13 | Progress output emitted to stdout during step execution per §7 | Nygard |
| FR-14 | Per-step timeouts enforced per the timeout values in §4 | Nygard |
| FR-15 | `--agents` value is passed directly to `claude -p --model`; no model ID resolution performed by the CLI | Core |

---

## 9. Non-Functional Requirements

| ID | Requirement | Verification |
|----|-------------|--------------|
| NFR-01 | Sprint's external CLI API (`superclaude sprint`) produces identical behavior before and after pipeline/ migration | All existing sprint tests pass after migration |
| NFR-02 | All existing sprint tests pass after migration | `uv run pytest tests/sprint/` exits 0 |
| NFR-03 | `gate_passed()` is pure Python — no subprocess, no I/O beyond reading the output file | Unit test: `gate_passed()` called with pre-written files; assert no subprocess spawned |
| NFR-04 | Step prompts defined in `roadmap/prompts.py` as pure functions returning strings; no I/O or subprocess calls | Module imports cleanly; functions return str |
| NFR-05 | Gate criteria defined in `roadmap/gates.py` as data (list of `GateCriteria` instances); not embedded in executor logic | Gate criteria readable without running executor |
| NFR-06 | `PipelineConfig`, `Step`, `StepResult`, `GateCriteria` have no sprint-specific fields | sprint-specific fields live only in `SprintConfig`, `SprintStep` |
| NFR-07 | The `pipeline/` module has no imports from `sprint/` or `roadmap/` (dependency flows one direction only) | Import check: `pipeline/__init__.py` imports; assert no `sprint` or `roadmap` references |

---

## 10. Acceptance Criteria

End-to-end acceptance tests (not unit tests — these validate the full CLI):

**AC-01**: Given a valid spec-file, `superclaude roadmap spec.md --dry-run` prints 7 step entries (each with ID, output filename, gate criteria, timeout) and exits 0. No files written.

**AC-02**: Given a valid spec-file, `superclaude roadmap spec.md` completes all 7 steps and writes 8 files to output-dir: `extraction.md`, `roadmap-opus-architect.md`, `roadmap-haiku-architect.md`, `diff-analysis.md`, `debate-transcript.md`, `base-selection.md`, `roadmap.md`, `test-strategy.md`.

**AC-03**: Given a generate step that produces a file missing the `primary_persona` frontmatter field, the CLI retries once, then halts and prints the gate failure message containing the field name and file path. Exits non-zero.

**AC-04**: Given a completed run (all gates pass), `superclaude roadmap spec.md --resume` prints `Skipping N steps (gates pass)` and exits 0 without launching any subprocesses.

**AC-05**: Given a completed run followed by a spec-file modification, `superclaude roadmap spec.md --resume` detects the hash mismatch, prints the stale-spec warning, and re-runs the extract step.

**AC-06**: `uv run pytest tests/sprint/` exits 0 after the pipeline/ migration (sprint external API unchanged).

**AC-07**: `superclaude roadmap spec.md --agents sonnet:security,haiku:qa` uses `sonnet` and `haiku` as the model values in the two generate step subprocess invocations (verified via `--dry-run` output showing model per step).

---

## 11. Open Questions (Resolved)

| Question | Resolution |
|----------|-----------|
| Debate step granularity | 3 gated sub-steps: diff → debate → score (then merge as step 4) |
| PR strategy | Single PR: pipeline/ extraction + sprint migration + roadmap/ |
| Model shorthand resolution | Not needed — claude CLI accepts opus/sonnet/haiku natively |

---

## 12. Implementation Notes

### Sprint Migration Strategy

The migration should not change any sprint behavior. Recommended approach:

1. Create `pipeline/models.py` with `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`
2. Move `ClaudeProcess` from `sprint/process.py` to `pipeline/process.py`; re-export from `sprint/process.py`
3. Create `pipeline/executor.py` with `execute_pipeline()` as a generalized version of `execute_sprint()`
4. Create `pipeline/gates.py` with `gate_passed()`
5. Refactor `sprint/executor.py` to call `execute_pipeline()` internally
6. Refactor `sprint/models.py`: `SprintConfig` inherits from `PipelineConfig`
7. Run `uv run pytest tests/sprint/` — all tests must pass before proceeding to roadmap/ work
8. Build `roadmap/` on top of the now-stable `pipeline/` base

### Prompt Contract for Debate Sub-Steps

Each of the three debate sub-steps (diff, debate, score) receives only the files listed in its `inputs` column. The debate step in particular must not receive the original spec-file — it operates only on the diff analysis and the two variant roadmaps. This is enforced by the executor's context isolation (FR-03).

### `AgentSpec` Type

```python
@dataclass
class AgentSpec:
    model: str      # e.g. "opus", "sonnet", "haiku"
    persona: str    # e.g. "architect", "security", "qa"

    @property
    def id(self) -> str:
        return f"{self.model}-{self.persona}"  # used in output filenames

    @classmethod
    def parse(cls, s: str) -> "AgentSpec":
        """Parse 'opus:architect' → AgentSpec(model='opus', persona='architect')"""
        parts = s.split(":", 1)
        model = parts[0].strip()
        persona = parts[1].strip() if len(parts) > 1 else "architect"
        return cls(model=model, persona=persona)
```

---

## 13. Design & Architecture

### 13.1 PipelineConfig Field Allocation

The extraction boundary is governed by one rule: **PipelineConfig owns fields that appear in `claude -p` subprocess invocation or control generic execution flow**. Sprint-specific orchestration (TUI, tmux, stall detection, phase numbering) stays in SprintConfig.

| Field | PipelineConfig | SprintConfig | Rationale |
|-------|:-:|:-:|-----------|
| `work_dir: Path` | **✓** (new) | — | Both pipelines write output to a directory. Sprint sets this to `release_dir`; roadmap sets it to `output_dir`. |
| `dry_run: bool` | **✓** | — | Both pipelines support `--dry-run`. |
| `max_turns: int` | **✓** | — | Passed to `claude -p --max-turns` in both pipelines. |
| `model: str` | **✓** | — | Passed to `claude -p --model` in both pipelines (roadmap overrides per-step for generate). |
| `permission_flag: str` | **✓** | — | Passed to every `claude -p` invocation. |
| `debug: bool` | **✓** | — | Both pipelines support debug logging. |
| `index_path: Path` | — | **✓** | Sprint discovers phases from an index file. Roadmap has no index concept. |
| `release_dir: Path` | — | **✓** (property alias → `work_dir`) | Sprint code references `release_dir` extensively. Becomes `@property` returning `self.work_dir` for backward compatibility. |
| `phases: list[Phase]` | — | **✓** | Sprint-specific: numbered phases discovered from index. |
| `start_phase: int` | — | **✓** | Sprint range selection. |
| `end_phase: int` | — | **✓** | Sprint range selection. |
| `tmux_session_name: str` | — | **✓** | Sprint-only TUI/tmux integration. |
| `stall_timeout: int` | — | **✓** | Sprint-specific watchdog. |
| `stall_action: str` | — | **✓** | Sprint-specific watchdog. |
| `phase_timeout: int` | — | **✓** | Sprint-specific per-phase timeout. |

**Migration safety for `release_dir`**: SprintConfig inherits from PipelineConfig. The constructor sets `work_dir` from the existing `release_dir` value. A `release_dir` property aliases `work_dir`. All existing sprint code that reads `config.release_dir` continues to work without modification. This is the mechanism that guarantees NFR-01/02.

```python
@dataclass
class SprintConfig(PipelineConfig):
    index_path: Path = Path(".")
    phases: list[Phase] = field(default_factory=list)
    start_phase: int = 1
    end_phase: int = 0
    tmux_session_name: str = ""
    stall_timeout: int = 0
    stall_action: str = "warn"
    phase_timeout: int = 0

    @property
    def release_dir(self) -> Path:
        """Backward-compatible alias for work_dir."""
        return self.work_dir

    @release_dir.setter
    def release_dir(self, value: Path):
        self.work_dir = value
```

### 13.2 Parallel Subprocess Concurrency Model

**Chosen approach**: `threading.Thread` with a shared `threading.Event` for cross-cancellation.

**Rationale**: ClaudeProcess already uses blocking `subprocess.Popen.wait(timeout=)`. Threads are the natural concurrency primitive for I/O-bound blocking calls. `asyncio` would require rewriting ClaudeProcess to use `asyncio.create_subprocess_exec`, which is invasive and risks sprint regression. `concurrent.futures.ThreadPoolExecutor` adds abstraction without benefit — we need exactly 2 threads with cross-cancellation, not a pool.

**Signal handling**: `SignalHandler.shutdown_requested` is already a boolean flag checked in the poll loop. Both threads check it. On SIGINT, both threads' ClaudeProcess instances are terminated. The existing pattern is thread-safe (boolean reads are atomic in CPython; the flag is set from the signal handler on the main thread and read from worker threads).

**Cross-cancellation**: A `threading.Event` (`cancel_event`) is shared between the two generate threads. When one thread's step fails after retry exhaustion, it calls `cancel_event.set()`. The other thread checks `cancel_event.is_set()` in its subprocess poll loop alongside `shutdown_requested`.

**Timeout enforcement**: Each thread enforces its own step timeout independently via `time.monotonic()` deadline — identical to the existing sprint poll loop pattern.

**Gate aggregation**: The main thread joins both worker threads, then checks both results. If either result is not PASS, the pipeline halts.

```python
def _run_parallel_steps(
    steps: list[Step],
    config: PipelineConfig,
    run_step: StepRunner,
    cancel_check: Callable[[], bool],
) -> list[StepResult]:
    """Run steps concurrently. Returns when all complete or one fails.

    Cross-cancellation: if any step fails after retry, a shared Event
    is set, causing remaining steps to terminate their subprocesses.
    """
    cancel_event = threading.Event()
    results: list[StepResult | None] = [None] * len(steps)

    def _worker(idx: int, step: Step):
        def combined_cancel() -> bool:
            return cancel_check() or cancel_event.is_set()

        result = _execute_single_step(step, config, run_step, combined_cancel)
        results[idx] = result
        if result.status != StepStatus.PASS:
            cancel_event.set()  # signal other threads to abort

    threads = [
        threading.Thread(target=_worker, args=(i, s), daemon=True)
        for i, s in enumerate(steps)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return [r for r in results if r is not None]
```

**Failure propagation sequence**:
1. generate-A fails gate on attempt 2 → `cancel_event.set()`
2. generate-B's poll loop sees `cancel_event.is_set()` → calls `proc.terminate()`
3. generate-B records `StepResult(status=CANCELLED)`
4. Main thread sees generate-A FAIL → pipeline halts
5. HALT output shows generate-A as failed, generate-B as cancelled

### 13.3 Prompt Builder Contract

All functions live in `roadmap/prompts.py`. Each is a **pure function**: takes concrete values, returns `str`, performs no I/O or subprocess calls (NFR-04).

The returned string is passed to `claude -p "<prompt>"`. The executor separately appends `--file <path>` for each entry in `step.inputs`. The prompt text references files by description (not path) since `--file` makes content available in context.

```python
# roadmap/prompts.py

from pathlib import Path
from typing import Literal
from ..pipeline.models import AgentSpec


def build_extract_prompt(spec_file: Path) -> str:
    """Prompt for step 'extract'.

    Instructs Claude to read the provided specification and produce
    extraction.md with YAML frontmatter containing functional_requirements,
    complexity_score, and complexity_class.
    """

def build_generate_prompt(agent: AgentSpec, extraction_path: Path) -> str:
    """Prompt for step 'generate-{agent.id}'.

    Instructs Claude to read the extraction document and generate a
    complete project roadmap. The agent's persona is embedded in the
    prompt as a role instruction. Output: roadmap-{agent.id}.md with
    frontmatter fields spec_source, complexity_score, primary_persona.
    """

def build_diff_prompt(variant_a_path: Path, variant_b_path: Path) -> str:
    """Prompt for step 'diff'.

    Instructs Claude to compare two roadmap variants and produce
    diff-analysis.md with frontmatter fields total_diff_points,
    shared_assumptions_count.
    """

def build_debate_prompt(
    diff_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
    depth: Literal["quick", "standard", "deep"],
) -> str:
    """Prompt for step 'debate'.

    Depth controls the number of debate rounds embedded in the prompt:
      quick    → 1 round  ("Single focused round...")
      standard → 2 rounds ("Two rounds: initial positions, then rebuttals...")
      deep     → 3 rounds ("Three rounds: positions, rebuttals, final synthesis...")

    Output: debate-transcript.md with frontmatter fields convergence_score,
    rounds_completed.
    """

def build_score_prompt(
    debate_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
) -> str:
    """Prompt for step 'score'.

    Instructs Claude to select a base variant and score both against
    criteria from the debate. Output: base-selection.md with frontmatter
    fields base_variant, variant_scores.
    """

def build_merge_prompt(
    base_selection_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
    debate_path: Path,
) -> str:
    """Prompt for step 'merge'.

    Instructs Claude to produce the final merged roadmap using the
    base variant, incorporating improvements identified in the debate.
    Output: roadmap.md with frontmatter fields spec_source,
    complexity_score, adversarial.
    """

def build_test_strategy_prompt(
    roadmap_path: Path,
    extraction_path: Path,
) -> str:
    """Prompt for step 'test-strategy'.

    Instructs Claude to produce a test strategy for the roadmap.
    Output: test-strategy.md with frontmatter fields
    validation_milestones, interleave_ratio.
    """
```

**`--file` injection in the executor** (pipeline/executor.py):

```python
def _build_subprocess_argv(step: Step, config: PipelineConfig) -> list[str]:
    argv = [
        "claude", "-p", step.prompt,
        "--max-turns", str(config.max_turns),
        config.permission_flag,
    ]
    for input_path in step.inputs:
        argv.extend(["--file", str(input_path)])
    model = step.model or config.model
    if model:
        argv.extend(["--model", model])
    return argv
```

This requires adding `model: str = ""` to the `Step` dataclass. For generate steps, `model` is set from `AgentSpec.model`. For all other steps, it defaults to `""` (falls through to `config.model`).

**Depth-to-prompt mapping** (inside `build_debate_prompt`):

```python
_DEPTH_INSTRUCTIONS = {
    "quick": (
        "Conduct a single focused debate round. Each perspective states its "
        "position on the key divergence points, then provide a convergence assessment."
    ),
    "standard": (
        "Conduct two debate rounds:\n"
        "  Round 1: Each perspective states initial positions on divergence points.\n"
        "  Round 2: Each perspective rebuts the other's key claims.\n"
        "Then provide a convergence assessment."
    ),
    "deep": (
        "Conduct three debate rounds:\n"
        "  Round 1: Each perspective states initial positions on divergence points.\n"
        "  Round 2: Each perspective rebuts the other's key claims.\n"
        "  Round 3: Final synthesis — each perspective identifies concessions and "
        "remaining disagreements.\n"
        "Then provide a convergence assessment."
    ),
}
```

### 13.4 `.roadmap-state.json` Schema

Written to `output_dir/.roadmap-state.json`. Updated atomically (write to `.tmp`, then `os.replace`). Updated after **each step completes** — not only after extract.

```json
{
  "schema_version": 1,
  "spec_file": ".dev/releases/current/v2.07/spec.md",
  "spec_hash": "sha256:a1b2c3d4e5f6...",
  "agents": [
    {"model": "opus", "persona": "architect", "id": "opus-architect"},
    {"model": "haiku", "persona": "architect", "id": "haiku-architect"}
  ],
  "depth": "standard",
  "pipeline_started_at": "2026-03-04T18:22:00Z",
  "updated_at": "2026-03-04T18:45:00Z",
  "steps": {
    "extract": {
      "status": "PASS",
      "attempts": 1,
      "output_file": "extraction.md",
      "started_at": "2026-03-04T18:22:00Z",
      "finished_at": "2026-03-04T18:23:12Z",
      "gate_failure_reason": null
    },
    "generate-opus-architect": {
      "status": "PASS",
      "attempts": 1,
      "output_file": "roadmap-opus-architect.md",
      "started_at": "2026-03-04T18:23:13Z",
      "finished_at": "2026-03-04T18:38:45Z",
      "gate_failure_reason": null
    },
    "generate-haiku-architect": {
      "status": "PASS",
      "attempts": 2,
      "output_file": "roadmap-haiku-architect.md",
      "started_at": "2026-03-04T18:23:13Z",
      "finished_at": "2026-03-04T18:40:01Z",
      "gate_failure_reason": null
    },
    "diff": {
      "status": "SKIPPED",
      "attempts": 0,
      "output_file": "diff-analysis.md",
      "started_at": null,
      "finished_at": null,
      "gate_failure_reason": null
    }
  }
}
```

**Field descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `int` | Schema version for forward compatibility. Currently `1`. |
| `spec_file` | `str` | Relative path to the specification file (relative to repo root). |
| `spec_hash` | `str` | `"sha256:<hex>"` hash of spec file contents at pipeline start. Used by `--resume` for stale detection. |
| `agents` | `list[object]` | Agent specs used for this run. Each has `model`, `persona`, `id`. |
| `depth` | `str` | Debate depth setting: `"quick"`, `"standard"`, or `"deep"`. |
| `pipeline_started_at` | `str` | ISO 8601 UTC timestamp of pipeline start. |
| `updated_at` | `str` | ISO 8601 UTC timestamp of last state file write. |
| `steps.<id>.status` | `str` | One of: `"PASS"`, `"FAIL"`, `"TIMEOUT"`, `"CANCELLED"`, `"SKIPPED"`, `"PENDING"`. |
| `steps.<id>.attempts` | `int` | Number of attempts executed (0 = not yet run, 1 = first attempt, 2 = retried). |
| `steps.<id>.output_file` | `str` | Filename (relative to `output_dir`) of the step's output artifact. |
| `steps.<id>.started_at` | `str\|null` | ISO 8601 UTC timestamp of first attempt start, or `null` if not yet run. |
| `steps.<id>.finished_at` | `str\|null` | ISO 8601 UTC timestamp of final attempt completion, or `null` if not yet run. |
| `steps.<id>.gate_failure_reason` | `str\|null` | Human-readable gate failure message from last attempt, or `null` on PASS. |

**Resume algorithm using state file**:

```python
def resolve_resume_steps(
    steps: list[Step],
    state_path: Path,
    spec_file: Path,
) -> tuple[list[Step], bool]:
    """Determine which steps to run on --resume.

    Returns (steps_to_run, spec_changed).

    1. If no state file exists, run all steps.
    2. Compare spec_hash. If changed, force extract re-run.
    3. For each step in order: if state says PASS and gate still passes,
       skip. Otherwise, run from this step onward.
    """
```

### 13.5 `execute_pipeline()` Extension Pattern

**Chosen pattern**: Composition via callable injection.

**Rationale**: Sprint's executor contains ~150 lines of tightly-coupled orchestration (TUI updates, monitor thread, stall detection, diagnostic collection, tmux pane updates) that cannot be meaningfully abstracted into hooks without creating a leaky abstraction. Subclassing would require sprint to conform to a template method that doesn't match its actual control flow. Composition lets each consumer provide its own subprocess lifecycle while the generic layer handles only what is genuinely shared: step ordering, retry logic, parallel dispatch, and state management.

**Interface definition** (`pipeline/executor.py`):

```python
from typing import Callable, Protocol
from .models import PipelineConfig, Step, StepResult, StepStatus


class StepRunner(Protocol):
    """Callable that executes a single step's subprocess and returns a result.

    The runner is responsible for:
    - Launching the claude -p subprocess
    - Waiting for completion (with timeout enforcement)
    - Returning a StepResult with appropriate status

    The runner is NOT responsible for:
    - Retry logic (handled by execute_pipeline)
    - Gate checking (handled by execute_pipeline)
    - Step ordering (handled by execute_pipeline)
    """
    def __call__(
        self,
        step: Step,
        config: PipelineConfig,
        cancel_check: Callable[[], bool],
    ) -> StepResult: ...


def execute_pipeline(
    steps: list[Step | list[Step]],
    config: PipelineConfig,
    run_step: StepRunner,
    on_step_start: Callable[[Step], None] = lambda s: None,
    on_step_complete: Callable[[Step, StepResult], None] = lambda s, r: None,
    on_state_update: Callable[[dict], None] = lambda state: None,
    cancel_check: Callable[[], bool] = lambda: False,
) -> list[StepResult]:
    """Generic pipeline executor.

    Processes steps in order. Each element in `steps` is either:
    - A single Step (executed sequentially)
    - A list[Step] (all steps in the list executed in parallel)

    For each step:
    1. Call on_step_start(step)
    2. Call run_step(step, config, cancel_check)
    3. If step has gate criteria: run gate_passed()
    4. If gate fails and attempts < retry_limit: retry (go to 2)
    5. If gate fails and attempts exhausted: HALT
    6. Call on_step_complete(step, result)
    7. Call on_state_update(updated_state_dict)

    For parallel step groups:
    - All steps in the group run concurrently via _run_parallel_steps()
    - If any step in the group fails, remaining steps are cancelled
    - All results from the group must be PASS before proceeding

    Returns list of all StepResults (one per step, flattened).
    """
```

**How sprint uses it** (`sprint/executor.py`):

```python
def execute_sprint(config: SprintConfig):
    # ... existing pre-flight, signal handler, TUI, logger setup ...

    # Wrap each Phase as a Step (no gate criteria — sprint uses EXIT_RECOMMENDATION)
    steps = [_phase_to_step(phase, config) for phase in config.active_phases]

    def sprint_run_step(step, pipeline_config, cancel_check):
        # Sprint's existing poll loop: TUI updates, monitor, stall detection
        # This is the ~100 lines of existing logic, unchanged in behavior
        ...
        return StepResult(...)

    results = execute_pipeline(
        steps=steps,
        config=config,  # SprintConfig IS-A PipelineConfig
        run_step=sprint_run_step,
        on_step_start=lambda s: logger.write_phase_start(...),
        on_step_complete=lambda s, r: logger.write_phase_result(...),
        cancel_check=lambda: signal_handler.shutdown_requested,
    )

    # ... existing post-run logic (summary, notification, exit code) ...
```

Sprint's `_phase_to_step()` wraps a `Phase` as a `Step` with no `GateCriteria` (gate is `None`). The executor skips gate checking when `step.gate is None`. Sprint's `sprint_run_step` returns the status based on its own EXIT_RECOMMENDATION parsing, and `execute_pipeline` trusts the returned `StepResult.status`.

**How roadmap uses it** (`roadmap/executor.py`):

```python
def execute_roadmap(config: RoadmapConfig):
    steps = build_roadmap_steps(config)  # returns list[Step | list[Step]]
    signal_handler = SignalHandler()
    signal_handler.install()

    def roadmap_run_step(step, pipeline_config, cancel_check):
        # Simple: build argv, launch subprocess, wait with timeout
        argv = _build_subprocess_argv(step, pipeline_config)
        proc = subprocess.Popen(argv, ...)
        # Poll loop with cancel_check and timeout
        ...
        return StepResult(...)

    try:
        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=roadmap_run_step,
            on_step_start=lambda s: _print_step_start(s),
            on_step_complete=lambda s, r: _print_step_result(s, r),
            on_state_update=lambda state: _write_state_file(config, state),
            cancel_check=lambda: signal_handler.shutdown_requested,
        )
    finally:
        signal_handler.uninstall()
```

**Step type modification**: `Step.gate` becomes `Optional[GateCriteria]` (default `None`). When `None`, `execute_pipeline` skips gate checking and trusts the `StepResult.status` returned by `run_step`.

```python
@dataclass
class Step:
    id: str
    prompt: str
    output_file: Path
    gate: GateCriteria | None       # None = no gate check (sprint mode)
    timeout_seconds: int
    inputs: list[Path]
    model: str = ""                  # per-step model override; "" = use config.model
    retry_limit: int = 1
```

### 13.6 Test Architecture

**Directory structure**:

```
tests/
  pipeline/                          ← NEW: shared pipeline module tests
    __init__.py
    test_models.py                   ← PipelineConfig, Step, StepResult, GateCriteria, StepStatus
    test_gates.py                    ← gate_passed() with pre-written markdown files
    test_executor.py                 ← execute_pipeline() with mocked StepRunner
    test_process.py                  ← ClaudeProcess after move (same assertions as sprint)
    test_parallel.py                 ← _run_parallel_steps(), cross-cancellation, timeout

  sprint/                            ← EXISTING: all 14 files unchanged
    __init__.py                      ← (no modifications)
    test_cli_contract.py             ← (no modifications)
    test_config.py                   ← (no modifications)
    test_executor.py                 ← (no modifications)
    test_process.py                  ← (no modifications — imports via re-export)
    test_models.py                   ← (no modifications)
    test_tui.py                      ← (no modifications)
    test_monitor.py                  ← (no modifications)
    test_e2e_halt.py                 ← (no modifications)
    test_e2e_success.py              ← (no modifications)
    test_integration_halt.py         ← (no modifications)
    test_integration_signal.py       ← (no modifications)
    test_integration_lifecycle.py    ← (no modifications)
    test_regression_gaps.py          ← (no modifications)

  roadmap/                           ← NEW: roadmap-specific tests
    __init__.py
    test_models.py                   ← RoadmapConfig, AgentSpec.parse()
    test_prompts.py                  ← All 7 prompt builders: assert str output, required phrases
    test_gates_data.py               ← Gate definitions: correct fields, min_lines per step
    test_executor.py                 ← execute_roadmap() with mocked subprocess
    test_cli_contract.py             ← Click CLI surface via CliRunner
    test_resume.py                   ← --resume: skip logic, stale spec detection
    test_parallel.py                 ← Parallel generate: both launched, cross-cancel on failure
    test_state.py                    ← .roadmap-state.json: write, read, atomic update
    test_dry_run.py                  ← --dry-run: output format, no subprocess launched
```

**Unit vs integration boundary**:

| Category | Test type | Mock strategy | Files |
|----------|-----------|---------------|-------|
| `gate_passed()` | Unit | Pre-written markdown files via `tmp_path` fixture. No subprocess. | `pipeline/test_gates.py` |
| Prompt builders | Unit | Pure function assertions. No I/O. Assert output contains required phrases, frontmatter field names, depth instructions. | `roadmap/test_prompts.py` |
| Data models | Unit | Dataclass construction, property assertions. | `pipeline/test_models.py`, `roadmap/test_models.py` |
| `AgentSpec.parse()` | Unit | String parsing assertions. | `roadmap/test_models.py` |
| `execute_pipeline()` | Unit | Mock `StepRunner` that returns pre-defined `StepResult`. Verify step ordering, retry logic, parallel dispatch, halt-on-failure. | `pipeline/test_executor.py` |
| Parallel dispatch | Unit | Mock `StepRunner` with `time.sleep()` to simulate concurrent execution. Verify cross-cancellation via `cancel_event`. | `pipeline/test_parallel.py` |
| `--resume` logic | Unit | Pre-create output files with valid/invalid frontmatter. Pre-create `.roadmap-state.json`. Assert skip/re-run decisions. | `roadmap/test_resume.py` |
| State file I/O | Unit | `tmp_path` fixture. Write state, read back, verify schema. | `roadmap/test_state.py` |
| CLI surface | Unit | `click.testing.CliRunner`. Verify option parsing, `--dry-run` output, `--agents` parsing. No subprocess. | `roadmap/test_cli_contract.py` |
| Sprint regression | Existing | All existing mocks/fixtures unchanged. `uv run pytest tests/sprint/` must exit 0. | All `sprint/test_*.py` |
| Full pipeline E2E | Integration (optional) | Requires `claude` binary in PATH. Marked `@pytest.mark.skipif(not shutil.which("claude"))`. Uses a trivial spec file. | Not in v1 scope — AC-02 validated manually. |

**Mock strategy details**:

- **`subprocess.Popen`**: Mocked via `unittest.mock.patch("subprocess.Popen")` for all subprocess tests. The mock returns a configurable exit code and writes pre-defined content to the output file path.
- **Pre-written gate files**: `conftest.py` in `tests/pipeline/` provides fixtures that write markdown files with valid/invalid/missing frontmatter to `tmp_path`.
- **StepRunner mock**: A simple callable that records its invocations and returns pre-configured `StepResult` objects. Supports "fail first, pass second" for retry testing.
- **CliRunner**: Click's built-in test runner. Captures stdout/stderr. Used for `--dry-run`, `--agents` parsing, and help text verification.

**Sprint test stability guarantee**: The 14 existing sprint test files are not modified. Sprint's `process.py` re-exports `ClaudeProcess` from `pipeline.process`, so `from superclaude.cli.sprint.process import ClaudeProcess` continues to resolve. If any sprint test imports break, the migration has a bug — this is the canary.
