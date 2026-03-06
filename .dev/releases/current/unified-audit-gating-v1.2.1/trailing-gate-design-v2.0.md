# Trailing Gate Architecture -- Design Specification v2.0

**Status**: DESIGN DRAFT
**Refactors**: unified-audit-gating v1.2.1
**Date**: 2026-03-05
**Paradigm Shift**: Synchronous blocking gates -> Asynchronous trailing gates with deferred remediation

---

## 1. Architecture Overview

### 1.1 Core Concept

The v1.2.1 spec enforces gates **before** allowing task progression (pessimistic model). This design shifts to an **optimistic model** centered on **deferred remediation**: gate evaluation is decoupled from task progression so the agent can finish its current task, then be pulled back at the next seam to remediate before continuing. The background-thread gate check is an implementation mechanism, not the primary value proposition. The throughput win comes from **non-blocking enforcement with bounded drift** (`grace_period=1`), not from raw compute parallelism.

```
v1.2.1 (BLOCKING):
  Task A -> [GATE CHECK] -> block if fail -> Task B -> [GATE CHECK] -> ...

v2.0 (TRAILING):
  Task A ---------> Task B ---------> Task C
     |                |
     +-- gate(A) --+  +-- gate(B) --+
        (daemon)         (daemon)

  If gate(A) FAILS while Task B is running:
    1. Task B finishes naturally
    2. Agent remediates gate(A) failure
    3. Conflict review of Task B
    4. Resume at Task C
```

### 1.2 Component Diagram

```
src/superclaude/cli/pipeline/
  |
  +-- models.py           [MODIFIED] Add GateMode, TrailingGateResult, RemediationEntry
  +-- executor.py          [MODIFIED] Add trailing gate orchestration to execute_pipeline()
  +-- gates.py             [UNCHANGED] gate_passed() reused as-is
  +-- trailing_gate.py     [NEW] GateResultQueue, TrailingGateRunner, DeferredRemediationLog
  +-- conflict_review.py   [NEW] File-level overlap detection and re-gate logic
  +-- diagnostic_chain.py  [NEW] Troubleshoot -> adversarial -> adversarial -> summary

src/superclaude/cli/sprint/
  |
  +-- models.py            [MODIFIED] Add gate_status to PhaseResult, GateDisplayState
  +-- executor.py          [MODIFIED] Wire trailing gate into phase loop
  +-- tui.py               [MODIFIED] Inline gate status column in phase table

src/superclaude/cli/audit/
  |
  +-- (ALL MODULES)        [UNCHANGED] Classification, evidence, manifest gates unaffected
```

### 1.3 Data Flow

```
Step completes
  |
  v
on_step_complete() callback fires
  |
  +---> [Main Thread] records StepResult, starts next step
  |
  +---> [Daemon Thread] TrailingGateRunner.submit(step, output_file, gate_criteria)
           |
           v
         gate_passed(output_file, criteria)  # reuses existing pure-Python gate
           |
           +-- PASS --> TrailingGateResult(passed=True) --> GateResultQueue
           |
           +-- FAIL --> TrailingGateResult(passed=False, reason=...) --> GateResultQueue
                          |
                          v
                        DeferredRemediationLog.append(RemediationEntry)

[Main Thread] between steps:
  |
  v
Wait for pending gate results (strict grace_period=1 enforcement)
  |
  v
Check GateResultQueue.drain()
  |
  +-- No failures --> continue to next step
  |
  +-- Has failures --> finish current step --> inject remediation step
                         |
                         v
                       Execute remediation (synchronous, with gate)
                         |
                         +-- PASS --> conflict_review(intervening_tasks) --> resume
                         |
                         +-- FAIL (attempt 1) --> retry once
                         |
                         +-- FAIL (attempt 2) --> HALT --> diagnostic_chain()
```

### 1.4 Thread Model

```
Main Thread (executor loop):
  - Runs steps sequentially (or parallel groups)
  - Between steps: waits for pending gate results, then drains GateResultQueue
  - Owns all state mutation (StepResult list, remediation log)

Gate Daemon Threads (one per trailing gate check):
  - Spawned by TrailingGateRunner.submit()
  - Runs gate_passed() (pure Python, no subprocess, no side effects)
  - Writes result to GateResultQueue (thread-safe queue.Queue)
  - Daemon=True: abandoned cleanly if pipeline halts

No shared mutable state between threads except:
  - GateResultQueue (queue.Queue -- inherently thread-safe)
  - cancel_event (threading.Event -- inherently thread-safe)
```

---

## 2. New Module Specifications

### 2.1 `pipeline/trailing_gate.py`

```python
"""Trailing gate infrastructure -- async gate evaluation with deferred remediation.

Implements FR-01 (async gates), FR-02 (continuation on failure), FR-03 (remediation).
NFR-001: Thread safety via queue.Queue. NFR-007: No sprint/roadmap imports.
"""

@dataclass
class TrailingGateResult:
    """Result posted to the queue by a gate daemon thread."""
    step_id: str
    passed: bool
    reason: str | None = None
    output_file: Path
    gate_criteria: GateCriteria
    checked_at: datetime

@dataclass
class RemediationEntry:
    """A deferred gate failure requiring remediation."""
    failed_step_id: str
    gate_failure_reason: str
    acceptance_criteria: list[str]  # extracted from Step.gate
    detected_during_step_id: str    # the step that was running when failure detected
    output_file: Path               # the file that failed the gate
    remediation_attempt: int = 0    # 0 = not yet attempted, 1 = first try, 2 = retry
    remediated: bool = False
    conflict_reviewed: bool = False

class GateResultQueue:
    """Thread-safe queue for trailing gate results.

    Writer: gate daemon threads (one per submit() call)
    Reader: main executor thread (via drain())
    """
    def __init__(self) -> None:
        self._queue: queue.Queue[TrailingGateResult] = queue.Queue()

    def put(self, result: TrailingGateResult) -> None: ...
    def drain(self) -> list[TrailingGateResult]: ...
    def pending_count(self) -> int: ...

class DeferredRemediationLog:
    """Tracks deferred gate failures and remediation state.

    Serializable to disk for --resume support (NFR-03).
    Only mutated by the main thread.
    """
    def __init__(self) -> None:
        self._entries: list[RemediationEntry] = []

    def append(self, entry: RemediationEntry) -> None: ...
    def pending_remediations(self) -> list[RemediationEntry]: ...
    def mark_remediated(self, step_id: str) -> None: ...
    def mark_conflict_reviewed(self, step_id: str) -> None: ...
    def to_dict(self) -> dict: ...  # for --resume serialization
    @classmethod
    def from_dict(cls, data: dict) -> DeferredRemediationLog: ...

class TrailingGateRunner:
    """Submits gate checks to daemon threads and collects results.

    Usage:
        runner = TrailingGateRunner()
        runner.submit(step)  # non-blocking, spawns daemon thread
        results = runner.drain()  # non-blocking, returns available results
    """
    def __init__(self) -> None:
        self._queue = GateResultQueue()

    def submit(self, step: Step) -> None:
        """Spawn a daemon thread to evaluate step's gate."""
        ...

    def drain(self) -> list[TrailingGateResult]:
        """Return all available results (non-blocking)."""
        return self._queue.drain()

    def wait_for_pending(self, timeout_seconds: float = 5.0) -> list[TrailingGateResult]:
        """Block briefly for all submitted gate checks to report back.

        This enforces the grace_period=1 contract: at most one subsequent task
        may complete before the executor knows whether the prior trailing gate
        passed or failed. Since gate_passed() is pure Python and normally
        completes in <10ms, this should return almost immediately.
        """
        ...
```

### 2.2 `pipeline/conflict_review.py`

```python
"""File-level conflict review after remediation.

Implements FR-05: checks whether remediation changes overlap with files
touched by tasks that ran during the grace period.
"""

@dataclass
class ConflictReviewResult:
    """Result of reviewing one intervening task for conflicts."""
    task_id: str
    has_conflicts: bool
    overlapping_files: list[str]  # files touched by both remediation and this task
    re_gate_required: bool

def review_conflicts(
    remediation_step_id: str,
    remediation_files_changed: set[str],
    intervening_results: list[StepResult],
) -> list[ConflictReviewResult]:
    """Check file-level overlap between remediation and intervening tasks.

    With grace_period=1, intervening_results has exactly 1 entry.
    """
    ...

class FileChangeProvider(Protocol):
    """Consumer-owned strategy for deterministic file-change capture.

    The pipeline layer must not parse freeform model output to infer changed
    files. Sprint/roadmap consumers provide a structural implementation, e.g.
    git diff snapshots around each step.
    """

    def __call__(self, step: Step, result: StepResult) -> set[str]: ...
```

### 2.3 `pipeline/diagnostic_chain.py`

```python
"""Automatic diagnostic chain on remediation halt.

Implements FR-04: troubleshoot -> adversarial(root causes) -> adversarial(solutions) -> summary.
Runs as sub-agents, no user interaction needed until final summary.
"""

@dataclass
class DiagnosticResult:
    """Final output of the diagnostic chain."""
    root_cause: str           # winning root cause from adversarial debate
    root_cause_runner_up: str # second-place for context
    solution: str             # winning solution from adversarial debate
    solution_runner_up: str   # second-place for context
    summary: str              # human-readable summary for user

def run_diagnostic_chain(
    failed_step: Step,
    gate_failure_reason: str,
    remediation_attempts: int,
    pipeline_context: dict,  # accumulated state for context
) -> DiagnosticResult:
    """Execute the full diagnostic chain.

    1. Build concise troubleshoot prompt from failure context
    2. Invoke /sc:troubleshoot to propose 3 root causes
    3. Spawn agent: /sc:adversarial --depth quick on the 3 root causes -> winner
    4. Build 3 solution proposals from winning root cause
    5. Spawn agent: /sc:adversarial --depth quick on the 3 solutions -> winner
    6. Compose summary of winning root cause + winning solution
    """
    ...
```

### 2.4 Modifications to `pipeline/models.py`

```python
# NEW ADDITIONS (backward-compatible):

class GateMode(Enum):
    """How gate checking is performed for a step."""
    BLOCKING = "blocking"   # v1.2.1 behavior: check immediately, halt on fail
    TRAILING = "trailing"   # v2.0 behavior: check async, defer remediation

@dataclass
class Step:
    # ... existing fields ...
    gate_mode: GateMode = GateMode.BLOCKING  # default preserves v1.2.1 behavior

@dataclass
class PipelineConfig:
    # ... existing fields ...
    grace_period: int = 0  # 0 = blocking (v1.2.1 compat), 1 = trailing
```

### 2.5 Modifications to `pipeline/executor.py`

The core change is in `execute_pipeline()`. To preserve NFR-007, the pipeline owns lifecycle/orchestration while consumers own remediation prompt construction and changed-file detection. This is represented as a consumer-supplied policy object or callback bundle.

```python
class TrailingGatePolicy(Protocol):
    """Consumer-owned hooks required for trailing gate orchestration."""

    def build_remediation_step(
        self,
        failed_step: Step,
        gate_failure_reason: str,
        acceptance_criteria: list[str],
    ) -> Step | None:
        """Return remediation Step, or None to halt immediately."""
        ...

    def files_changed(self, step: Step, result: StepResult) -> set[str]:
        """Return deterministic changed-file set for conflict review."""
        ...
```

The current flow:

```python
# CURRENT (v1.2.1):
result = _execute_single_step(entry, ...)  # includes synchronous gate check
if result.status != StepStatus.PASS:
    break  # halt immediately
```

Becomes:

```python
# NEW (v2.0):
if entry.gate_mode == GateMode.TRAILING and config.grace_period > 0:
    # Run step WITHOUT gate check
    result = _execute_step_no_gate(entry, ...)
    all_results.append(result)
    # Submit gate to background thread
    trailing_runner.submit(entry)
    # Strict grace_period=1 enforcement: before launching the next-next step,
    # wait briefly for all pending gate results to arrive.
    deferred = trailing_runner.wait_for_pending(timeout_seconds=5.0)
    failures = [r for r in deferred if not r.passed]
    if failures:
        # Current step just finished -- inject remediation built by consumer policy
        remediation_results = _handle_deferred_remediation(
            failures, remediation_log, config, run_step, trailing_policy, ...
        )
        if any(r.status != StepStatus.PASS for r in remediation_results):
            # Remediation failed after retry -- HALT + diagnostic chain
            _run_diagnostic_chain(failures, config)
            break
else:
    # Original blocking behavior (unchanged)
    result = _execute_single_step(entry, ...)
    if result.status != StepStatus.PASS:
        break
```

Key design constraint: `_execute_step_no_gate()` is a new private function that runs the step and returns a result WITHOUT the gate check portion. The gate check is deferred to the trailing runner. This avoids duplicating the existing `_execute_single_step()` logic.

### 2.6 Modifications to `sprint/tui.py`

Add a "Gate" column to the phase table:

```python
# In _build_phase_table():
table.add_column("Gate", width=16, justify="center")  # NEW column

# Per-row gate status:
gate_display = self._gate_status_for_phase(phase)
# Returns one of:
#   "[dim]-[/]"                          (no trailing gate / not started)
#   "[yellow]checking...[/]"             (gate daemon running)
#   "[green]PASS[/]"                     (gate passed)
#   "[red]FAIL (deferred)[/]"            (gate failed, remediation pending)
#   "[yellow]REMEDIATING[/]"             (remediation in progress)
#   "[green]REMEDIATED[/]"               (remediation succeeded)
#   "[red]HALT[/]"                       (remediation failed)
```

The TUI receives gate state via a new `gate_states: dict[int, GateDisplayState]` field on `SprintResult`, updated by the executor. The label should consistently read **non-blocking trailing gate** in user-facing documentation and telemetry, not merely "parallel gate," to reflect the actual objective.

### 2.7 Modifications to `sprint/executor.py`

The sprint executor's phase loop integrates trailing gates:

```python
# After phase completes and status is determined:
if config.grace_period > 0 and not is_release_scope(phase):
    # Submit trailing gate for this phase
    trailing_runner.submit_phase(phase, phase_result)
    # Check for deferred failures from previous phases
    deferred_failures = trailing_runner.drain_failures()
    if deferred_failures:
        # Inject remediation phase
        remediation_result = _remediate_phase(deferred_failures, config, ...)
        if remediation_result.is_failure:
            # Retry once
            remediation_result = _remediate_phase(deferred_failures, config, ...)
            if remediation_result.is_failure:
                # HALT + diagnostic chain
                diagnostic = run_diagnostic_chain(...)
                _print_diagnostic_summary(diagnostic)
                sprint_result.outcome = SprintOutcome.HALTED
                break
        # Conflict review
        conflicts = review_conflicts(remediation_result, intervening_phases)
        for conflict in conflicts:
            if conflict.re_gate_required:
                _re_gate_phase(conflict.phase, config)
```

### 2.8 Modifications to `sprint/models.py`

```python
class GateDisplayState(Enum):
    """Visual state of a trailing gate in the TUI."""
    NONE = "none"           # no trailing gate configured
    CHECKING = "checking"   # daemon thread running
    PASS = "pass"
    FAIL_DEFERRED = "fail_deferred"
    REMEDIATING = "remediating"
    REMEDIATED = "remediated"
    HALT = "halt"

@dataclass
class PhaseResult(StepResult):
    # ... existing fields ...
    gate_display_state: GateDisplayState = GateDisplayState.NONE  # NEW
```

---

## 3. Scope-Based Gate Strategy (FR-06)

| Scope | Gate Mode | Grace Period | Rationale |
|-------|-----------|-------------|-----------|
| Release | BLOCKING | 0 (always) | Release failures are catastrophic; no trailing allowed |
| Milestone | Configurable | 0 (default) | Milestones aggregate tasks; blocking by default for safety |
| Task | TRAILING | 1 (default) | Task-level gates benefit most from parallelism |

The scope determination uses the existing `validate_transition()` function from v1.2.1:
- If `scope == "release"`: force `GateMode.BLOCKING` regardless of config
- If `scope == "milestone"`: use config default (blocking)
- If `scope == "task"`: use config default (trailing with grace_period=1)

---

## 4. Thread Safety Analysis

### 4.1 Shared State Inventory

| State | Owner | Readers | Writers | Mechanism |
|-------|-------|---------|---------|-----------|
| `GateResultQueue._queue` | TrailingGateRunner | Main thread (drain) | Gate daemon threads (put) | `queue.Queue` (inherently thread-safe) |
| `cancel_event` | Pipeline executor | Gate daemon threads | Main thread | `threading.Event` (inherently thread-safe) |
| `DeferredRemediationLog._entries` | Main thread only | Main thread | Main thread | No synchronization needed (single writer) |
| `StepResult` list | Main thread only | Main thread | Main thread | No synchronization needed |
| `SprintResult` | Main thread only | TUI thread (read), Main thread (write) | Main thread | Existing pattern: TUI reads are best-effort snapshots |

### 4.2 Synchronization Points

1. **Gate submission**: `TrailingGateRunner.submit()` spawns a daemon thread. No lock needed -- thread creation is atomic.
2. **Gate result collection**: `GateResultQueue.drain()` calls `queue.Queue.get_nowait()` in a loop. Thread-safe by design.
3. **Grace-period enforcement**: `TrailingGateRunner.wait_for_pending()` blocks briefly for submitted gate checks to finish, guaranteeing `grace_period=1` semantics.
4. **Cancel propagation**: `threading.Event.set()` is thread-safe. Gate daemons check `cancel_event.is_set()` before starting work.
5. **TUI reads**: The existing TUI already reads `SprintResult` and `MonitorState` without locks (best-effort rendering). Adding `gate_display_state` follows the same pattern.

### 4.3 Deadlock Analysis

No deadlock is possible because:
- Gate daemon threads never acquire locks or wait on the main thread
- The main thread only performs a bounded wait (`wait_for_pending(timeout=5.0)`) on gate completion
- `queue.Queue.get_nowait()` raises `Empty` instead of blocking during drain
- All daemon threads are `daemon=True`, so they're abandoned on pipeline exit

---

## 5. Backward Compatibility Contract

### 5.1 `grace_period=0` Guarantees

When `grace_period=0` (the default):

1. **No trailing gates are created**. `TrailingGateRunner` is never instantiated.
2. **`execute_pipeline()` follows the v1.2.1 code path exactly**. The `if entry.gate_mode == GateMode.TRAILING` branch is never taken.
3. **No daemon threads are spawned**. Zero threading overhead.
4. **All existing tests pass without modification**. The `Step` dataclass gets a new `gate_mode` field with default `GateMode.BLOCKING`, which is backward-compatible.
5. **`PipelineConfig.grace_period` defaults to 0**. No opt-in required to maintain current behavior.

### 5.2 Migration Path

- v1.2.1 users: no changes needed. Default behavior is identical.
- v2.0 opt-in: set `grace_period=1` in config or via CLI flag `--trailing-gates`.
- v2.0 per-step override: set `step.gate_mode = GateMode.TRAILING` on individual steps.

---

## 6. Diagnostic Chain Specification (FR-04)

### 6.1 Trigger Condition

The chain fires when:
1. A trailing gate fails
2. Remediation is attempted (synchronous, with its own gate check)
3. Remediation fails its gate
4. Remediation is retried once
5. Retry also fails its gate
6. Pipeline HALTs

### 6.2 Chain Steps

```
Step 1: Build troubleshoot prompt
  Input:  failed_step.id, gate_failure_reason, remediation output, pipeline state
  Output: Concise prompt (~200 tokens) describing the failure context

Step 2: /sc:troubleshoot
  Input:  The troubleshoot prompt
  Output: 3 potential root causes (ranked by likelihood)

Step 3: /sc:adversarial --depth quick (root cause debate)
  Input:  The 3 root causes as competing proposals
  Output: Winning root cause with rationale

Step 4: Build solution proposals
  Input:  Winning root cause + pipeline context
  Output: 3 potential solutions (each actionable)

Step 5: /sc:adversarial --depth quick (solution debate)
  Input:  The 3 solutions as competing proposals
  Output: Winning solution with rationale

Step 6: Summary
  Input:  Winning root cause + winning solution
  Output: Human-readable summary printed to user
```

### 6.3 Sub-Agent Invocation

Each `/sc:adversarial` and `/sc:troubleshoot` invocation runs as a **spawned sub-agent** via the Task tool. This ensures:
- The diagnostic chain does not consume main conversation context
- Each step gets fresh context focused on its specific input
- Failures in the diagnostic chain do not crash the pipeline (best-effort)

### 6.4 Output Format

```
================================================================================
PIPELINE HALTED: Remediation failed after 2 attempts
================================================================================

FAILED STEP:  T02.06 -- Enforce Transition Validator in tui.py
GATE FAILURE: Semantic check 'validate_transition_called' failed: ...
ATTEMPTS:     2/2 exhausted

ROOT CAUSE (via adversarial debate):
  The transition validator function is not imported in tui.py. The
  remediation added the call site but missed the import statement,
  causing a NameError at runtime that prevents the output file from
  containing the expected validation markers.

PROPOSED SOLUTION (via adversarial debate):
  Add `from ..pipeline.models import validate_transition` to tui.py
  imports, then re-run the remediation step targeting only the import
  fix. Verify with `uv run pytest tests/sprint/ -k validate -v`.

To resume: superclaude sprint run <index> --start <phase> --end <phase>
================================================================================
```

---

## 7. v1.2.1 Refactoring Plan

### 7.1 Refactoring Principles

1. **Preserve all v1.2.1 data structures** -- state enums, validate_transition(), OverrideRecord
2. **Shift enforcement timing** -- from pre-execution blocking to post-execution trailing (for task scope)
3. **Keep release-scope blocking** -- no trailing gates for release transitions
4. **Add, don't remove** -- new modules and fields; no deletion of existing code
5. **Default to v1.2.1 behavior** -- grace_period=0 means no change

### 7.2 Phase-by-Phase Disposition

#### Phase 1: Blocker Resolution and Decision Lock (5 tasks, 5 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T01.01 | **KEPT** | Profile thresholds still needed for gate evaluation |
| T01.02 | **MODIFIED** | Retry/backoff values now also parameterize remediation retry timing |
| T01.03 | **KEPT** | Rollback triggers unchanged |
| T01.04 | **KEPT** | Decision registry unchanged |
| T01.05 | **KEPT** | Override approver model unchanged |

#### Phase 2: State Machine and Illegal-Transition Tests (8 tasks, 8 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T02.01 | **KEPT** | Audit state enums still needed |
| T02.02 | **MODIFIED** | validate_transition() shifts from pre-exec to post-exec for task scope; still pre-exec for release scope |
| T02.03 | **KEPT** | Legal transition tests still valid |
| T02.04 | **KEPT** | Illegal transition tests still valid |
| T02.05 | **MODIFIED** | Stuck-state recovery now includes "deferred remediation" as a recovery path |
| T02.06 | **SUPERSEDED** | tui.py completion guard replaced by trailing gate + remediation pull-back. New task: T02.06v2 "Wire trailing gate into tui.py phase loop" |
| T02.07 | **KEPT** | Regression check still required |
| T02.08 | **KEPT** | OverrideRecord release prohibition unchanged |

#### Phase 3: Deterministic Gate Evaluator and Profile Tests (8 tasks, 8 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T03.01 | **MODIFIED** | Evaluator contract adds trailing gate mode specification |
| T03.02 | **MODIFIED** | Command spec adds --trailing-gates flag |
| T03.03 | **KEPT** | GateResult schema unchanged |
| T03.04 | **KEPT** | Determinism tests unchanged |
| T03.05 | **KEPT** | Major-severity tests unchanged |
| T03.06 | **KEPT** | Unknown/missing input tests unchanged |
| T03.07 | **KEPT** | Evidence completeness tests unchanged |
| T03.08 | **KEPT** | --strictness alias tests unchanged |

#### Phase 4: Runtime Controls and Override Governance (13 tasks, 15 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T04.01 | **MODIFIED** | Lease/heartbeat now covers trailing gate daemon threads too |
| T04.02 | **KEPT** | Release guard is always blocking |
| T04.03 | **MODIFIED** | Task/milestone override path now includes deferred remediation override |
| T04.04 | **KEPT** | OverrideRecord validation unchanged |
| T04.05 | **KEPT** | Override approval test unchanged |
| T04.06 | **KEPT** | Field-absence tests unchanged |
| T04.07 | **KEPT** | Release override forbidden unchanged |
| T04.08 | **KEPT** | Scope isolation tests unchanged |
| T04.09 | **KEPT** | Expired override tests unchanged |
| T04.10 | **MODIFIED** | Timeout/retry now includes remediation retry path |
| T04.11 | **MODIFIED** | Correlation ID propagation extended to trailing gate events |
| T04.12 | **MODIFIED** | Fault injection adds: gate daemon crash, queue corruption, remediation timeout |
| T04.13 | **MODIFIED** | Deadlock analysis includes trailing gate thread interactions |

#### Phase 5: Sprint CLI Regression Gate (5 tasks, 5 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T05.01 | **KEPT** | Baseline regression unchanged |
| T05.02 | **MODIFIED** | Backward-compat now also asserts GateMode.BLOCKING default |
| T05.03 | **KEPT** | Regression gaps unchanged |
| T05.04 | **MODIFIED** | Non-audit guard bypass now also verifies trailing gate does not fire for non-audit phases |
| T05.05 | **KEPT** | Zero new failures unchanged |

#### Phase 6: Rollout Validation and Promotion Gates (13 tasks, 12 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T06.01 | **MODIFIED** | Shadow mode now records trailing gate timing metrics alongside blocking metrics |
| T06.02 | **KEPT** | --strictness alias unchanged |
| T06.03 | **MODIFIED** | KPI report adds: trailing gate latency, remediation frequency, conflict review rate |
| T06.04 | **MODIFIED** | Threshold calibration includes trailing gate thresholds |
| T06.05 | **MODIFIED** | Shadow-to-Soft promotion adds: trailing gate stability criterion |
| T06.06 | **MODIFIED** | Soft mode test verifies trailing gates active for task scope |
| T06.07 | **MODIFIED** | Full mode test verifies trailing gates active, blocking for release |
| T06.08 | **KEPT** | Rollback trigger tests unchanged |
| T06.09 | **KEPT** | Rollback drill unchanged |
| T06.10 | **MODIFIED** | Soft-to-Full promotion adds trailing gate approval criterion |

#### New Tasks (v2.0 additions)

| Task | Phase | Description |
|------|-------|-------------|
| T02.06v2 | P2 | Wire TrailingGateRunner into sprint executor phase loop |
| T02.09 | P2 | Implement GateResultQueue and DeferredRemediationLog |
| T02.10 | P2 | Implement conflict_review.py with file-level overlap detection |
| T03.09 | P3 | Trailing gate determinism tests (same input -> same gate result regardless of timing) |
| T04.14 | P4 | Implement diagnostic_chain.py (troubleshoot -> adversarial -> adversarial -> summary) |
| T04.15 | P4 | Remediation retry tests: first fail -> retry -> second fail -> halt + diagnostic |
| T04.16 | P4 | Conflict review tests: overlapping files -> re-gate; no overlap -> resume |
| T05.06 | P5 | grace_period=0 backward-compat test: zero daemon threads, identical to v1.2.1 |
| T06.11 | P6 | Shadow mode trailing gate metrics collection and comparison to blocking baseline |

---

## 8. v1.2.1 -> v2.0 Traceability Matrix (Paper Trail)

### 8.1 Task Disposition Summary

| Disposition | Count | Percentage |
|------------|-------|------------|
| KEPT (unchanged) | 27 | 51.9% |
| MODIFIED (adapted for trailing gates) | 20 | 38.5% |
| SUPERSEDED (replaced by new task) | 1 | 1.9% |
| REMOVED | 0 | 0.0% |
| NEW (v2.0 additions) | 9 | -- |
| **Total v2.0 tasks** | **61** | -- |

### 8.2 Full Task Traceability

| v1.2.1 Task | v2.0 Disposition | v2.0 Task | Change Description |
|------------|-----------------|-----------|-------------------|
| T01.01 | KEPT | T01.01 | No change |
| T01.02 | MODIFIED | T01.02 | Add remediation retry timing to policy document |
| T01.03 | KEPT | T01.03 | No change |
| T01.04 | KEPT | T01.04 | No change |
| T01.05 | KEPT | T01.05 | No change |
| T02.01 | KEPT | T02.01 | No change |
| T02.02 | MODIFIED | T02.02 | validate_transition() called post-exec for task scope |
| T02.03 | KEPT | T02.03 | No change |
| T02.04 | KEPT | T02.04 | No change |
| T02.05 | MODIFIED | T02.05 | Add deferred-remediation recovery path |
| T02.06 | SUPERSEDED | T02.06v2 | Blocking tui.py guard -> trailing gate wiring |
| T02.07 | KEPT | T02.07 | No change |
| T02.08 | KEPT | T02.08 | No change |
| -- | NEW | T02.09 | GateResultQueue + DeferredRemediationLog |
| -- | NEW | T02.10 | conflict_review.py |
| T03.01 | MODIFIED | T03.01 | Add trailing gate mode to evaluator contract |
| T03.02 | MODIFIED | T03.02 | Add --trailing-gates flag spec |
| T03.03 | KEPT | T03.03 | No change |
| T03.04 | KEPT | T03.04 | No change |
| T03.05 | KEPT | T03.05 | No change |
| T03.06 | KEPT | T03.06 | No change |
| T03.07 | KEPT | T03.07 | No change |
| T03.08 | KEPT | T03.08 | No change |
| -- | NEW | T03.09 | Trailing gate determinism tests |
| T04.01 | MODIFIED | T04.01 | Lease/heartbeat covers daemon threads |
| T04.02 | KEPT | T04.02 | No change (release always blocking) |
| T04.03 | MODIFIED | T04.03 | Override path includes deferred remediation |
| T04.04 | KEPT | T04.04 | No change |
| T04.05 | KEPT | T04.05 | No change |
| T04.06 | KEPT | T04.06 | No change |
| T04.07 | KEPT | T04.07 | No change |
| T04.08 | KEPT | T04.08 | No change |
| T04.09 | KEPT | T04.09 | No change |
| T04.10 | MODIFIED | T04.10 | Add remediation retry exhaustion path |
| T04.11 | MODIFIED | T04.11 | Correlation ID in trailing gate events |
| T04.12 | MODIFIED | T04.12 | Add gate daemon fault scenarios |
| T04.13 | MODIFIED | T04.13 | Deadlock analysis includes daemon threads |
| -- | NEW | T04.14 | diagnostic_chain.py implementation |
| -- | NEW | T04.15 | Remediation retry tests |
| -- | NEW | T04.16 | Conflict review tests |
| T05.01 | KEPT | T05.01 | No change |
| T05.02 | MODIFIED | T05.02 | Assert GateMode.BLOCKING default |
| T05.03 | KEPT | T05.03 | No change |
| T05.04 | MODIFIED | T05.04 | Verify trailing gate inactive for non-audit |
| T05.05 | KEPT | T05.05 | No change |
| -- | NEW | T05.06 | grace_period=0 full backward-compat test |
| T06.01 | MODIFIED | T06.01 | Shadow records trailing gate timing |
| T06.02 | KEPT | T06.02 | No change |
| T06.03 | MODIFIED | T06.03 | KPI report adds trailing gate metrics |
| T06.04 | MODIFIED | T06.04 | Calibration includes trailing thresholds |
| T06.05 | MODIFIED | T06.05 | Promotion adds trailing gate criterion |
| T06.06 | MODIFIED | T06.06 | Soft mode verifies trailing active |
| T06.07 | MODIFIED | T06.07 | Full mode verifies trailing + blocking |
| T06.08 | KEPT | T06.08 | No change |
| T06.09 | KEPT | T06.09 | No change |
| T06.10 | MODIFIED | T06.10 | Promotion adds trailing approval |
| -- | NEW | T06.11 | Shadow trailing metrics collection |

### 8.3 Timing Semantics Lens

In addition to kept/modified/superseded disposition, each v1.2.1 element should be tagged with its timing-model outcome:

| Timing Semantics | Meaning |
|------------------|---------|
| Still blocking | Enforcement remains pre-execution and synchronous |
| Shifted to trailing | Enforcement now occurs after task completion with deferred remediation |
| Still synchronous but moved | Enforcement remains synchronous but is relocated in the lifecycle |
| Newly added recovery behavior | New v2.0 mechanism for remediation, conflict review, or diagnostics |

Representative mapping:

| Element | Timing Semantics | Notes |
|---------|------------------|-------|
| Release guard (`T04.02`, `D-0023`) | Still blocking | Release scope always hard-stop |
| `validate_transition()` for task scope (`T02.02`) | Shifted to trailing | Evaluated after task output, before next-next task |
| `OverrideRecord` constructor prohibition (`T02.08`, `D-0013`) | Still blocking | Compile-time / construction-time invariant |
| `tui.py` task completion guard (`T02.06`) | Still synchronous but moved | Replaced by post-task seam enforcement |
| Deferred remediation log / conflict review / diagnostic chain | Newly added recovery behavior | v2.0 additions only |

### 8.4 Deliverable Disposition Summary

| v1.2.1 Deliverable | v2.0 Disposition |
|---------------------|-----------------|
| D-0001 through D-0005 | KEPT (P1 decision docs) |
| D-0006, D-0007 | KEPT (state enums, validator) |
| D-0008, D-0009 | KEPT (transition tests) |
| D-0010 | MODIFIED (add deferred remediation recovery) |
| D-0011 | SUPERSEDED by new trailing gate integration deliverable |
| D-0012, D-0013 | KEPT |
| D-0014, D-0015 | MODIFIED (add trailing gate mode) |
| D-0016 through D-0021 | KEPT |
| D-0022 | MODIFIED (covers daemon threads) |
| D-0023 | KEPT (release always blocking) |
| D-0024 | MODIFIED (includes deferred remediation) |
| D-0025 through D-0030 | KEPT |
| D-0031 | MODIFIED (remediation retry path) |
| D-0032 | MODIFIED (trailing gate correlation) |
| D-0033 through D-0034 | MODIFIED (daemon fault scenarios) |
| D-0035 through D-0039 | KEPT or MODIFIED (backward-compat additions) |
| D-0040 through D-0049 | MODIFIED (trailing gate metrics in rollout) |
| D-0050 through D-0056 | KEPT (subtask deliverables) |
| D-0057+ | NEW (trailing gate, conflict review, diagnostic chain deliverables) |

---

## 9. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gate daemon thread crashes silently | Gate failure goes undetected | Daemon threads catch all exceptions and post FAIL result to queue |
| Remediation changes break subsequent work | Cascading failures | Conflict review with file-level overlap detection (FR-05) |
| Trailing gate adds latency | Pipeline slower than blocking | Gate evaluation is pure Python (<10ms); daemon thread overhead negligible |
| grace_period > 1 increases blast radius | More tasks to review after remediation | grace_period=1 is the only supported value initially |
| Diagnostic chain fails | No root cause/solution for user | Best-effort: chain errors are caught; user still gets standard HALT output |
| Queue corruption under load | Results lost | queue.Queue is stdlib, well-tested; no custom synchronization |

---

## 10. Test Strategy Outline

### 10.1 Unit Tests (per module)

- `test_trailing_gate.py`: GateResultQueue thread safety, DeferredRemediationLog serialization, TrailingGateRunner submit/drain
- `test_conflict_review.py`: File overlap detection, re-gate logic, no-overlap passthrough
- `test_diagnostic_chain.py`: Prompt construction, chain step sequencing (mocked sub-agents)

### 10.2 Integration Tests

- `test_executor_trailing.py`: Full pipeline with trailing gates, remediation injection, conflict review
- `test_executor_compat.py`: grace_period=0 produces identical results to v1.2.1
- `test_sprint_trailing.py`: Sprint executor with trailing gates through TUI

### 10.3 Property-Based Tests

- Trailing gate result ordering: results arrive in submission order (or are correctly associated)
- Remediation idempotency: running remediation twice produces same result
- grace_period=0 invariant: no daemon threads spawned (check threading.active_count())
