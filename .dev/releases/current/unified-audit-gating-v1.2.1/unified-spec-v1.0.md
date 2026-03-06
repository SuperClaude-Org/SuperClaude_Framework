# Turn-Budget Reimbursement with Trailing Gate Enforcement — Unified Specification v1.0

**Status**: UNIFIED SPEC — Panel-reviewed merge of Solution A + Solution B
**Date**: 2026-03-06
**Sources**: MaxTurn_SolutionDoc.md (Solution A), trailing-gate-design-v2.0.md (Solution B)
**Panel**: Fowler, Nygard, Newman, Wiegers, Crispin, Hohpe
**Gaps Addressed**: 7 (all identified by panel)
**Overlaps Resolved**: 3 (retry, executor, reporting)

---

<!-- Source: MaxTurnProblemStatement.md -->
## 1. Problem Statement

The sprint runner (`superclaude sprint`) spawns Claude Code subprocesses with a fixed `--max-turns` budget. When a subprocess exhausts its budget, Claude Code exits with code 0 (indistinguishable from normal completion), and any unfinished tasks — including the Completion Protocol report — are silently dropped. The sprint reports success when work is incomplete.

### 1.1 Root Cause

The runner relies entirely on the agent's self-reporting (the result file) to determine phase outcome, but the agent's ability to self-report is constrained by the same turn budget that limits its work. The Completion Protocol is the last step in the prompt, making it the first casualty when turns run out.

### 1.2 Contributing Factors

| Factor | Detail |
|--------|--------|
| Claude Code exit code | `error_max_turns` exits with code 0, indistinguishable from normal completion |
| No task inventory | The runner never parses the phase tasklist file to know how many tasks exist |
| Report is last-mile | The Completion Protocol is at the end of the prompt |
| Monitor is liveness-only | OutputMonitor tracks output growth but doesn't compare against expected tasks |
| PASS_NO_REPORT is success | The status is classified as `is_success`, same as PASS |
| No turn-budget awareness | The runner has no visibility into how many turns were actually consumed |

### 1.3 Evidence

From the cleanup-audit-v2-UNIFIED-SPEC sprint:

| Phase | Tasks | Last Task Reached | Status | What Happened |
|-------|-------|-------------------|--------|---------------|
| 1 | 8 | T01.08 (8/8) | pass_no_report | All tasks done but report not written |
| 2 | 6 | T02.06 (6/6) | pass_no_report | All tasks done, report was in_progress when killed |
| 3 | 10 | T03.10 (10/10) | pass | Completed within budget |
| 4 | 13 | T04.13 (13/13) | pass | Completed within budget |
| 5 | 9 | T05.05 (5/9) | pass_no_report | **4 tasks never executed (T05.06–T05.09)** |

Phase 5 is the critical case: tasks T05.06 (benchmarking), T05.07 (concurrent-run isolation), T05.08 (non-determinism documentation), and T05.09 (release readiness decision) were never run. The sprint reported `outcome: success`.

### 1.4 Design Principles Derived From the Problem

1. **Runner owns completion state**: The runner must never depend on agent self-reporting
2. **Per-task isolation**: No task should be starved because another task consumed too many turns
3. **Verified quality**: Every task output must pass a gate before the runner considers it complete
4. **Budget discipline**: The system must be mathematically bounded — no infinite loops
5. **Backward compatibility**: `grace_period=0` produces identical behavior to v1.2.1

---

<!-- Source: Solution A §2 (subprocess model) + Solution B §1.1 (gate concept) -->
## 2. Architecture Overview

### 2.1 Dual-Layer Design

The architecture addresses two distinct layers of the MaxTurn problem:

| Layer | Concern | Mechanism | Source |
|-------|---------|-----------|--------|
| **Execution Architecture** | Who owns completion state? | Per-task subprocess spawning with TurnLedger economics | Solution A |
| **Quality Enforcement** | What happens when a gate fails? | Trailing gates with deferred remediation and diagnostic chains | Solution B |

```
Sprint Runner (owns all state)
  │
  ├── TurnLedger (economic model — budget, debit, credit)
  │
  ├── Per-Task Subprocess Loop
  │   ├── T01.01 subprocess (--max-turns N)
  │   ├── T01.02 subprocess (--max-turns N)
  │   └── ...one per task
  │
  ├── TrailingGateRunner (quality enforcement)
  │   ├── gate(T01.01) daemon thread → GateResultQueue
  │   ├── gate(T01.02) daemon thread → GateResultQueue
  │   └── ...one per completed task
  │
  ├── DeferredRemediationLog (failure tracking)
  │
  └── DiagnosticChain (failure intelligence — runner-side)
```

### 2.2 Key Architectural Decisions

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Subprocess granularity | Per-task | Structural elimination of Completion Protocol dependence |
| Gate timing | Trailing (async) with configurable grace_period | Non-blocking enforcement with bounded drift |
| Budget scope | Per-sprint TurnLedger | Simplest model; tasks draw from shared pool |
| Agent awareness | None | Budget is runner-side only; agent is untrusted |
| 4-layer isolation | Mandatory | Without it, cold-start overhead is prohibitive (50K→5K tokens) |
| error_max_turns detection | Included | Orthogonal defense-in-depth, zero cost |
| Backward compatibility | grace_period=0 default | Zero daemon threads, identical to v1.2.1 |
| Release-scope gates | Always BLOCKING | Release failures are catastrophic; no trailing allowed |

### 2.3 Component Diagram

```
src/superclaude/cli/pipeline/
  │
  ├── models.py              [MODIFIED] Add GateMode, TrailingGateResult, RemediationEntry
  ├── executor.py             [MODIFIED] Per-task loop + trailing gate orchestration
  ├── gates.py                [UNCHANGED] gate_passed() reused as-is
  ├── trailing_gate.py        [NEW] GateResultQueue, TrailingGateRunner, DeferredRemediationLog
  ├── conflict_review.py      [NEW] File-level overlap detection and re-gate logic
  └── diagnostic_chain.py     [NEW] Troubleshoot → adversarial → adversarial → summary

src/superclaude/cli/sprint/
  │
  ├── models.py               [MODIFIED] TurnLedger, GateDisplayState, PhaseResult.gate_display_state
  ├── executor.py             [MODIFIED] Per-task subprocess loop + trailing gate wiring
  ├── process.py              [MODIFIED] Per-task prompt construction + context injection
  ├── monitor.py              [MODIFIED] error_max_turns NDJSON detection
  ├── config.py               [MODIFIED] Task budget + isolation settings
  └── tui.py                  [MODIFIED] Inline gate status column in phase table

src/superclaude/cli/audit/
  │
  └── (ALL MODULES)           [UNCHANGED] Classification, evidence, manifest gates unaffected
```

<!-- Source: Panel §1 — Hohpe's three-channel model -->
### 2.4 Three-Channel Event Flow

The unified architecture coordinates three communication channels (Hohpe):

```
Channel 1: TurnLedger (synchronous, runner-owned)
  debit on subprocess exit → credit on gate PASS

Channel 2: GateResultQueue (async, thread-safe)
  submit on subprocess exit → result arrives async via daemon thread

Channel 3: Context Injection (synchronous, runner-owned)
  prior results + gate outcomes + remediation history → next task prompt
```

**Critical synchronization point**: The credit decision (Channel 1) depends on the gate result (Channel 2). The next task's context injection (Channel 3) must include whether the prior task's gate passed or failed. This creates a mandatory sync:

```
subprocess exits
  → debit turns from TurnLedger (Channel 1)
  → submit gate check to daemon thread (Channel 2)
  → build next task prompt in parallel with gate evaluation (Channel 3, partial)
  → wait_for_pending() ←── SYNCHRONIZATION POINT
  → gate result arrives (Channel 2 → Channel 1)
  → credit or no-credit to TurnLedger (Channel 1)
  → finalize context injection with gate outcome (Channel 3, complete)
  → launch next subprocess
```

---

<!-- Source: Solution A §2.1–2.5 -->
## 3. Core Economic Model (TurnLedger)

### 3.1 The Turn Ledger

A per-sprint budget managed by the runner. Never visible to the agent doing the work.

```python
@dataclass
class TurnLedger:
    """Per-sprint turn budget with reimbursement economics.

    The runner owns this entirely. The agent subprocess never sees it.
    Diagnostic chain invocations are runner-side and do NOT consume
    TurnLedger turns (Gap 2).
    """
    initial_budget: int = 200         # configurable per sprint
    consumed: int = 0                 # total turns debited
    reimbursed: int = 0              # total turns credited back
    reimbursement_rate: float = 0.90  # 90% reimbursement on PASS
    minimum_allocation: int = 5       # minimum turns to launch a task
    minimum_remediation_budget: int = 10  # minimum to attempt remediation (Gap 1)

    def available(self) -> int:
        return self.initial_budget - self.consumed + self.reimbursed

    def debit(self, turns: int) -> None:
        """Debit turns consumed by a subprocess."""
        self.consumed += turns

    def credit(self, turns: int) -> None:
        """Credit reimbursed turns for a passing gate."""
        self.reimbursed += math.floor(turns * self.reimbursement_rate)

    def can_launch(self) -> bool:
        """Check if budget allows launching another task."""
        return self.available() >= self.minimum_allocation

    def can_remediate(self) -> bool:
        """Check if budget allows spawning a remediation subprocess (Gap 1)."""
        return self.available() >= self.minimum_remediation_budget
```

### 3.2 Transaction Flow Per Task

```
1. BEFORE LAUNCH:  Check ledger.can_launch()
                   If not: HALT sprint (budget exhausted)
2. ALLOCATE:       max_turns = min(ledger.available(), default_task_budget)
3. BUILD PROMPT:   Include task description + context summary from prior tasks
4. LAUNCH:         claude --max-turns {max_turns} -p <task_prompt>
5. ON EXIT:        actual_turns = count_turns(output)
                   ledger.debit(actual_turns)
6. TRAILING GATE:  Submit gate check to daemon thread
7. SYNC POINT:     wait_for_pending() — block until gate result arrives
8. REIMBURSE:      if PASS: ledger.credit(actual_turns)
                   if FAIL: no credit → may trigger remediation (if can_remediate())
9. AGGREGATE:      Runner updates phase-level result from task results
```

### 3.3 Retry Reimbursement Rule

- First attempt fails gate → turns NOT reimbursed
- Remediation (second attempt) passes gate → only remediation turns reimbursed
- Both attempts fail → both sets of turns permanently lost → diagnostic chain fires → budget drains

### 3.4 The 90% Reimbursement Rate

A 90% reimbursement rate creates natural budget decay even when everything passes:

```
net_cost_per_task = (actual_turns × 0.10) + overhead_turns
                  = (8 × 0.10) + 2
                  = 2.8 turns per passing task
```

For a 46-task sprint: ~129 turns of net drain. A 200-turn budget sustains this with ~71 turns of margin. This makes infinite-run mathematically impossible while providing generous capacity for legitimate work.

<!-- Source: Panel Gap 1 — Nygard -->
### 3.5 Pre-Remediation Budget Check (Gap 1)

When a trailing gate fails AND the TurnLedger is low, the runner must not waste remaining turns on doomed remediation:

```python
if not gate_result.passed:
    if ledger.can_remediate():
        # Spawn remediation subprocess
        remediation_result = _spawn_remediation(...)
    else:
        # Cannot afford remediation — halt immediately
        outcome = HaltReason.BUDGET_EXHAUSTED_WITH_GATE_FAILURE
        # Emit: "Sprint halted: insufficient budget for remediation.
        #        Task {id} failed gate: {reason}.
        #        Remaining budget: {n} turns.
        #        Resume with: superclaude sprint run --budget 300"
        break
```

<!-- Source: Panel Gap 2 — Nygard -->
### 3.6 Diagnostic Chain Budget Boundary (Gap 2)

The diagnostic chain (troubleshoot → adversarial → adversarial → summary) runs as sub-agents in the runner's process. These consume API calls but NOT TurnLedger turns. The TurnLedger exclusively tracks agent subprocess turns, not runner-side intelligence operations. The diagnostic chain fires regardless of ledger state — it is a runner-owned failure analysis mechanism.

---

<!-- Source: Solution A §2.2, §2.3 -->
## 4. Per-Task Subprocess Model

### 4.1 Subprocess Structure

One Claude Code subprocess per task. The runner owns task sequencing, context injection, and result aggregation.

```
Sprint Runner
  ├── Phase 1
  │   ├── T01.01 subprocess (--max-turns N)
  │   ├── T01.02 subprocess (--max-turns N)
  │   └── ... (one per task)
  ├── Phase 2
  │   └── ... (one per task)
  └── Phase K
      └── ... (one per task)
```

The runner constructs phase reports by aggregating individual task results. No dependence on agent self-reporting.

<!-- Source: Solution A §5.2 + Panel Gap 3 -->
### 4.2 4-Layer Subprocess Isolation

Mandatory for per-task viability. Without isolation: ~50K tokens per cold-start (~10 turns). With isolation: ~5K tokens per cold-start (~2 turns).

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| 1. Scoped working directory | Already in `ClaudeProcess` | Filesystem isolation |
| 2. Git boundary | `.git/HEAD` in workspace | Repository isolation |
| 3. Empty plugin directory | `--plugin-dir` pointing to empty folder | Plugin isolation |
| 4. Restricted settings | `--setting-sources project,local` | Configuration isolation |

**Gap 3**: Gate daemon threads are runner-side. They run in the runner's process, not in agent subprocesses. They read static output files from terminated subprocesses. They are completely unaffected by the 4-layer subprocess isolation boundaries. This is explicitly documented to prevent confusion during implementation.

<!-- Source: Solution A §5.1 + Panel Gap 4 -->
### 4.3 Context Injection

Each task subprocess receives a deterministic summary of prior task results in its prompt. The runner auto-generates this from result files.

```
## Prior Work Context
- T05.01: Added AuditState enum to models.py (lines 45-67)
  Files changed: src/superclaude/cli/pipeline/models.py
  Gate: PASS | Reimbursed: 7/8 turns
- T05.02: Implemented validate_transition() in gates.py (lines 89-134)
  Files changed: src/superclaude/cli/pipeline/gates.py
  Gate: PASS | Reimbursed: 5/6 turns
- T05.03: Added legal transition tests
  Files changed: tests/pipeline/test_gates.py
  Gate: FAIL → Remediated (remediation changed tests/pipeline/test_gates.py:45-67)
  Gate (post-remediation): PASS | Reimbursed: 4/5 turns (remediation only)
[Budget remaining: ~165 turns]
```

**Mitigations for context fragmentation** (ordered by effectiveness):

1. **Structured context injection**: Deterministic summary from result files (shown above), including gate outcomes and remediation history (Gap 4)
2. **Git diff context**: `git diff --stat` since sprint start, providing structural overview of changes
3. **Dependency-aware prompt enrichment**: For tasks with explicit dependencies, include the output of the dependency task directly in the prompt
4. **Progressive summarization**: Running summary compressed every N tasks to stay within budget

**Context injection vs. session memory trade-off**: The structured summary approach provides deterministic, verifiable context. A long-running session's memory degrades — the agent may silently forget details from 30+ turns ago. Per-task subprocess trades implicit, opaque context for explicit, inspectable context.

<!-- Source: Solution A §3.4 -->
### 4.4 error_max_turns Detection

Orthogonal to per-task subprocess. The runner detects the `error_max_turns` event in the NDJSON output stream as the final `"subtype":"error_max_turns"` JSON line when Claude Code hits its turn ceiling.

**Implementation**: Regex on the last NDJSON line of the subprocess output. Zero extra turn cost.

**Value**: Distinguishes three exit conditions:
- Task completed normally (no error_max_turns, output present)
- Task exhausted budget (error_max_turns detected, partial/no output)
- Task crashed (non-zero exit code)

### 4.5 Runner as Source of Truth

The runner owns the task inventory (parsed from the tasklist file). It tracks:
- Which tasks have been launched
- Which tasks completed (subprocess exited)
- Which tasks passed their trailing gate
- Which tasks remain in the queue
- How many turns each task consumed
- Current TurnLedger balance

Phase reports are runner-constructed:

```yaml
phase: 5
status: PARTIAL
tasks_total: 9
tasks_passed: 5
tasks_failed: 0
tasks_incomplete: 1 (T05.06 - max_turns exhausted)
tasks_not_attempted: 3 (T05.07, T05.08, T05.09)
budget_remaining: 42
EXIT_RECOMMENDATION: HALT
```

---

<!-- Source: Solution B §2.1–2.3, adapted for per-task loop per Fowler -->
## 5. Trailing Gate Enforcement

### 5.1 Core Concept

<!-- Source: Solution B §1.1 + Panel §1 — Fowler reinterpretation -->

Gate evaluation is decoupled from task progression. In the per-task subprocess model, the trailing gate evaluates a **static output file from a terminated subprocess**, not a running agent's intermediate work. This simplifies the threading model compared to Solution B's original per-phase design.

```
Per-task trailing gate flow:

T01 subprocess exits → runner debits ledger
  │                         │
  ├── gate(T01) daemon ──┐  ├── prepare T02 prompt (context injection, partial)
  │   evaluates static   │  │
  │   output file        │  │
  │                      │  │
  gate result arrives ←──┘  │
  │                         │
  ├── credit/no-credit      │
  ├── finalize T02 context  │
  └── launch T02 subprocess ←┘
```

**Grace period reinterpretation** (Fowler): In per-phase mode, `grace_period=1` meant "one more task can run before gate result required." In per-task mode, it means "one more subprocess can be *prepared* (prompt built) but not *launched* until the prior gate resolves." This preserves the non-blocking benefit (prompt construction overlaps gate evaluation) without the conflict review complexity of overlapping running tasks.

### 5.2 New Module: `pipeline/trailing_gate.py`

```python
"""Trailing gate infrastructure — async gate evaluation with deferred remediation.

Implements FR-01 (async gates), FR-02 (continuation on failure), FR-03 (remediation).
NFR-001: Thread safety via queue.Queue. NFR-007: No sprint/roadmap imports.
NFR-NEW: Gate evaluation completes within 50ms for output files up to 100KB (Gap 7).
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
    evaluation_ms: float  # Gap 7: track for NFR compliance

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

    Serializable to disk for --resume support.
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

    Gate daemon threads are runner-side — they run in the runner's process,
    not in agent subprocesses. They are unaffected by 4-layer subprocess
    isolation (Gap 3).

    Usage:
        runner = TrailingGateRunner()
        runner.submit(step)        # non-blocking, spawns daemon thread
        results = runner.drain()   # non-blocking, returns available results
        results = runner.wait_for_pending()  # bounded wait for sync point
    """
    def __init__(self) -> None:
        self._queue = GateResultQueue()
        self._cancel_event = threading.Event()

    def submit(self, step: Step) -> None:
        """Spawn a daemon thread to evaluate step's gate.

        The daemon reads a static output file from a terminated subprocess.
        No race condition with a running agent (Fowler reinterpretation).
        """
        ...

    def drain(self) -> list[TrailingGateResult]:
        """Return all available results (non-blocking)."""
        return self._queue.drain()

    def wait_for_pending(self, timeout_seconds: float = 5.0) -> list[TrailingGateResult]:
        """Block briefly for all submitted gate checks to report back.

        This is the SYNCHRONIZATION POINT in Hohpe's three-channel model.
        Enforces the per-task grace contract: the next subprocess is NOT
        launched until the prior gate resolves.

        Since gate_passed() is pure Python and completes in <50ms (Gap 7),
        this should return almost immediately.
        """
        ...

    def cancel(self) -> None:
        """Signal all daemon threads to stop."""
        self._cancel_event.set()
```

<!-- Source: Solution B §3 -->
### 5.3 Scope-Based Gate Strategy

| Scope | Gate Mode | Grace Period | Rationale |
|-------|-----------|-------------|-----------|
| Release | BLOCKING | 0 (always) | Release failures are catastrophic; no trailing allowed |
| Milestone | Configurable | 0 (default) | Milestones aggregate tasks; blocking by default for safety |
| Task | TRAILING | 1 (default) | Task-level gates benefit most from non-blocking evaluation |

The scope determination uses the existing `validate_transition()` function from v1.2.1:
- If `scope == "release"`: force `GateMode.BLOCKING` regardless of config
- If `scope == "milestone"`: use config default (blocking)
- If `scope == "task"`: use config default (trailing with grace_period=1)

<!-- Source: Solution B §4 -->
### 5.4 Thread Safety

#### 5.4.1 Shared State Inventory

| State | Owner | Readers | Writers | Mechanism |
|-------|-------|---------|---------|-----------|
| `GateResultQueue._queue` | TrailingGateRunner | Main thread (drain) | Gate daemon threads (put) | `queue.Queue` (inherently thread-safe) |
| `cancel_event` | Pipeline executor | Gate daemon threads | Main thread | `threading.Event` (inherently thread-safe) |
| `DeferredRemediationLog._entries` | Main thread only | Main thread | Main thread | No synchronization needed (single writer) |
| `TurnLedger` | Main thread only | Main thread | Main thread | No synchronization needed (single writer) |
| `StepResult` list | Main thread only | Main thread | Main thread | No synchronization needed |
| `SprintResult` | Main thread only | TUI thread (read), Main thread (write) | Main thread | Existing pattern: TUI reads are best-effort snapshots |

#### 5.4.2 Synchronization Points

1. **Gate submission**: `TrailingGateRunner.submit()` spawns a daemon thread. No lock needed — thread creation is atomic.
2. **Gate result collection**: `GateResultQueue.drain()` calls `queue.Queue.get_nowait()` in a loop. Thread-safe by design.
3. **Three-channel sync point**: `TrailingGateRunner.wait_for_pending()` blocks briefly for submitted gate checks to finish, guaranteeing that ledger credit/debit and context injection are resolved before next subprocess launch.
4. **Cancel propagation**: `threading.Event.set()` is thread-safe. Gate daemons check `cancel_event.is_set()` before starting work.
5. **TUI reads**: The existing TUI already reads `SprintResult` without locks (best-effort rendering). Adding `gate_display_state` follows the same pattern.

#### 5.4.3 Deadlock Analysis

No deadlock is possible because:
- Gate daemon threads never acquire locks or wait on the main thread
- The main thread only performs a bounded wait (`wait_for_pending(timeout=5.0)`) on gate completion
- `queue.Queue.get_nowait()` raises `Empty` instead of blocking during drain
- All daemon threads are `daemon=True`, so they're abandoned on pipeline exit

---

<!-- Source: Overlap Resolution #1 — Panel §2 -->
## 6. Unified Retry + Remediation Model

### 6.1 Retry Economics (Solution A) + Escalation Path (Solution B)

The TurnLedger governs resource accounting. The diagnostic chain governs failure intelligence. They don't conflict — one is about cost, the other about understanding.

```
Gate FAIL on task T
  │
  ├── ledger.can_remediate()? ─── NO ──→ HALT (budget exhausted with gate failure)
  │                                       Emit budget-specific message (Gap 1)
  │                                       No diagnostic chain (can't afford more work)
  YES
  │
  ├── Spawn remediation subprocess
  │   ledger.debit(remediation_turns)
  │
  ├── Remediation gate check
  │   ├── PASS → ledger.credit(remediation_turns)
  │   │          conflict_review(intervening_work)
  │   │          resume at next task
  │   │
  │   └── FAIL → Retry once (if ledger.can_remediate())
  │              │
  │              ├── Retry PASS → credit retry turns, conflict review, resume
  │              │
  │              └── Retry FAIL → HALT
  │                               diagnostic_chain() fires (Gap 2: runner-side, free)
  │                               Emit root cause + solution + resume command
  │
  └── (Budget drain occurs naturally: failed attempts = no reimbursement)
```

### 6.2 Reimbursement Rules

| Outcome | Turns Debited | Turns Credited | Net Cost |
|---------|---------------|----------------|----------|
| Task passes gate | actual_turns | floor(actual_turns × 0.90) | ~10% of actual |
| Task fails, remediation passes | actual + remediation | floor(remediation × 0.90) | actual + ~10% remediation |
| Task fails, remediation fails, retry passes | actual + remediation + retry | floor(retry × 0.90) | actual + remediation + ~10% retry |
| Task fails, both remediation attempts fail | actual + remediation + retry | 0 | All turns permanently lost |

### 6.3 Remediation Subprocess Construction

Remediation is a new subprocess with a focused prompt:

```python
class TrailingGatePolicy(Protocol):
    """Consumer-owned hooks for trailing gate orchestration.

    The pipeline layer owns lifecycle/orchestration. Consumers (sprint, roadmap)
    own remediation prompt construction and changed-file detection.
    """

    def build_remediation_step(
        self,
        failed_step: Step,
        gate_failure_reason: str,
        acceptance_criteria: list[str],
    ) -> Step | None:
        """Return remediation Step, or None to halt immediately."""
        ...

    def files_changed(self, step: Step, result: StepResult) -> set[str]:
        """Return deterministic changed-file set for conflict review.

        Must NOT parse freeform model output. Use structural mechanisms
        (e.g., git diff snapshots around each step).
        """
        ...
```

---

<!-- Source: Solution B §2.2 -->
## 7. Conflict Review

### 7.1 Purpose

After remediation, check whether the remediation changes overlap with files touched by tasks that ran during the grace period. In the per-task model with `grace_period=1`, the next subprocess is not launched until the gate resolves (Fowler reinterpretation), so conflict review is only relevant if prompt preparation for the next task pre-cached file reads that remediation then changed.

### 7.2 Module: `pipeline/conflict_review.py`

```python
"""File-level conflict review after remediation.

Implements FR-05: checks whether remediation changes overlap with files
touched by tasks that ran during the grace period.

In per-task mode with grace_period=1 and Fowler reinterpretation,
the primary use case is checking whether remediation invalidated
context that was already injected into a prepared (but not yet launched)
task prompt.
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

    With grace_period=1 in per-task mode, intervening_results has at most
    1 entry (the prepared-but-not-launched task's expected file set).
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

---

<!-- Source: Solution B §6 + Panel Gap 2 + Panel Gap 5 -->
## 8. Diagnostic Chain

### 8.1 Trigger Condition

The chain fires when:
1. A trailing gate fails
2. Remediation is attempted (synchronous, with its own gate check)
3. Remediation fails its gate
4. Remediation is retried once
5. Retry also fails its gate
6. Pipeline HALTs

<!-- Source: Panel Gap 2 -->
The diagnostic chain is a **runner-side** intelligence mechanism. It runs as sub-agents in the runner's process and does NOT consume TurnLedger turns. It fires regardless of ledger state because its purpose is failure analysis, not task execution.

### 8.2 Chain Steps

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

### 8.3 Module: `pipeline/diagnostic_chain.py`

```python
"""Automatic diagnostic chain on remediation halt.

Implements FR-04: troubleshoot → adversarial(root causes) → adversarial(solutions) → summary.
Runs as sub-agents. Runner-side — does NOT consume TurnLedger turns (Gap 2).
Best-effort: chain errors are caught; user still gets standard HALT output.
"""

@dataclass
class DiagnosticResult:
    """Final output of the diagnostic chain."""
    root_cause: str            # winning root cause from adversarial debate
    root_cause_runner_up: str  # second-place for context
    solution: str              # winning solution from adversarial debate
    solution_runner_up: str    # second-place for context
    summary: str               # human-readable summary for user
    resume_command: str         # actionable resume command (Gap 5)

def run_diagnostic_chain(
    failed_step: Step,
    gate_failure_reason: str,
    remediation_attempts: int,
    pipeline_context: dict,  # accumulated state for context
) -> DiagnosticResult:
    """Execute the full diagnostic chain.

    Each /sc:adversarial and /sc:troubleshoot invocation runs as a
    spawned sub-agent via the Task tool. This ensures:
    - The diagnostic chain does not consume main conversation context
    - Each step gets fresh context focused on its specific input
    - Failures in the diagnostic chain do not crash the pipeline
    """
    ...
```

<!-- Source: Panel Gap 5 -->
### 8.4 Output Format (with Resume Semantics — Gap 5)

```
================================================================================
PIPELINE HALTED: Remediation failed after 2 attempts
================================================================================

FAILED STEP:  T02.06 — Enforce Transition Validator in tui.py
GATE FAILURE: Semantic check 'validate_transition_called' failed: ...
ATTEMPTS:     2/2 exhausted
BUDGET:       42 turns remaining (of 200 initial)

ROOT CAUSE (via adversarial debate):
  The transition validator function is not imported in tui.py. The
  remediation added the call site but missed the import statement,
  causing a NameError at runtime that prevents the output file from
  containing the expected validation markers.

PROPOSED SOLUTION (via adversarial debate):
  Add `from ..pipeline.models import validate_transition` to tui.py
  imports, then re-run the remediation step targeting only the import
  fix. Verify with `uv run pytest tests/sprint/ -k validate -v`.

RESUME FROM TASK: T02.06 (re-gate after manual fix)
TASKS REMAINING: T02.07, T02.08, T02.09, T02.10

To resume: superclaude sprint run <index> --start-task T02.06 --budget 200
================================================================================
```

---

<!-- Source: Solution A §3.2 (runner-constructed data) + Solution B §2.6 (TUI gate column) -->
## 9. Reporting Model

### 9.1 Task-Level Result

The runner constructs a `TaskResult` for each completed subprocess, combining execution data with gate outcome and reimbursement decision.

```python
@dataclass
class TaskResult:
    """Runner-constructed result for a single task subprocess."""
    task_id: str
    phase: int
    exit_code: int
    turns_allocated: int
    turns_consumed: int
    error_max_turns: bool         # True if NDJSON shows error_max_turns event
    output_file: Path | None
    gate_result: TrailingGateResult | None  # None if grace_period=0
    turns_reimbursed: int         # 0 if gate failed or grace_period=0
    remediation: RemediationEntry | None  # None if no remediation needed
    status: TaskStatus            # PASS, FAIL, INCOMPLETE, NOT_ATTEMPTED
```

### 9.2 Phase-Level Report

Runner aggregates task results into phase reports. No dependence on agent self-reporting.

```yaml
phase: 5
status: PARTIAL
tasks_total: 9
tasks_passed: 5
tasks_failed: 1 (T05.06 - gate failure, remediation failed)
tasks_incomplete: 0
tasks_not_attempted: 3 (T05.07, T05.08, T05.09)
turns_consumed: 68
turns_reimbursed: 45
budget_remaining: 42
gate_results:
  T05.01: PASS (7ms)
  T05.02: PASS (4ms)
  T05.03: PASS (12ms)
  T05.04: PASS (6ms)
  T05.05: PASS (8ms)
  T05.06: FAIL → REMEDIATED(FAIL) → HALT
EXIT_RECOMMENDATION: HALT
```

### 9.3 TUI Gate Column

```python
# In sprint/tui.py _build_phase_table():
table.add_column("Gate", width=16, justify="center")  # NEW column

# Per-row gate status (from GateDisplayState):
#   "[dim]-[/]"                          (no trailing gate / not started)
#   "[yellow]checking...[/]"             (gate daemon running)
#   "[green]PASS[/]"                     (gate passed)
#   "[red]FAIL (deferred)[/]"            (gate failed, remediation pending)
#   "[yellow]REMEDIATING[/]"             (remediation in progress)
#   "[green]REMEDIATED[/]"               (remediation succeeded)
#   "[red]HALT[/]"                       (remediation failed)

class GateDisplayState(Enum):
    """Visual state of a trailing gate in the TUI."""
    NONE = "none"
    CHECKING = "checking"
    PASS = "pass"
    FAIL_DEFERRED = "fail_deferred"
    REMEDIATING = "remediating"
    REMEDIATED = "remediated"
    HALT = "halt"
```

The TUI receives gate state via a `gate_states: dict[str, GateDisplayState]` field on `SprintResult`, updated by the executor. User-facing documentation and telemetry consistently use **non-blocking trailing gate**, not "parallel gate."

---

<!-- Source: Solution B §5 -->
## 10. Backward Compatibility

### 10.1 `grace_period=0` Guarantees

When `grace_period=0` (the default):

1. **No trailing gates are created.** `TrailingGateRunner` is never instantiated.
2. **`execute_pipeline()` follows the v1.2.1 code path exactly.** The trailing gate branch is never taken.
3. **No daemon threads are spawned.** Zero threading overhead.
4. **All existing tests pass without modification.** The `Step` dataclass gets a new `gate_mode` field with default `GateMode.BLOCKING`, which is backward-compatible.
5. **`PipelineConfig.grace_period` defaults to 0.** No opt-in required to maintain current behavior.
6. **TurnLedger is still active** (if per-task subprocess is enabled). The TurnLedger and trailing gates are independent features.

### 10.2 Model Additions (backward-compatible)

```python
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

### 10.3 Migration Path

- **v1.2.1 users**: no changes needed. Default behavior is identical.
- **v2.0 opt-in (trailing gates)**: set `grace_period=1` in config or via CLI flag `--trailing-gates`.
- **v2.0 per-step override**: set `step.gate_mode = GateMode.TRAILING` on individual steps.
- **Per-task subprocess**: enabled via CLI flag `--per-task` or config. Independent of trailing gates.

### 10.4 Executor Branching

```python
# In execute_pipeline():

if entry.gate_mode == GateMode.TRAILING and config.grace_period > 0:
    # NEW: Trailing gate path
    result = _execute_step_no_gate(entry, ...)
    all_results.append(result)
    trailing_runner.submit(entry)
    # SYNCHRONIZATION POINT (Hohpe three-channel model)
    deferred = trailing_runner.wait_for_pending(timeout_seconds=5.0)
    failures = [r for r in deferred if not r.passed]
    if failures:
        # Check budget before attempting remediation (Gap 1)
        if not ledger.can_remediate():
            _halt_budget_exhausted(failures, ledger)
            break
        remediation_results = _handle_deferred_remediation(
            failures, remediation_log, config, run_step, trailing_policy, ...
        )
        if any(r.status != StepStatus.PASS for r in remediation_results):
            # Remediation failed — diagnostic chain (Gap 2: runner-side, free)
            diagnostic = run_diagnostic_chain(failures, config)
            _print_diagnostic_summary(diagnostic)
            break
else:
    # ORIGINAL: Blocking gate path (unchanged)
    result = _execute_single_step(entry, ...)
    if result.status != StepStatus.PASS:
        break
```

---

<!-- Source: Panel §4 — unified 4-phase roadmap -->
## 11. Implementation Roadmap

### Phase 1: Foundation (Week 1) — Immediate Detection Value

| Deliverable | Source | Lines | Risk |
|-------------|--------|-------|------|
| TurnLedger dataclass | Solution A §2.1 | ~50 | None |
| error_max_turns NDJSON detection in OutputMonitor | Solution A §3.4 | ~15 | Low |
| Reclassify PASS_NO_REPORT + error_max_turns → INCOMPLETE | Solution A §7.1 | ~10 | Low |
| Budget check before subprocess launch | Solution A §2.3 | ~10 | None |
| **Total** | | **~85 lines** | **Low** |

**Value**: Immediately detects silent incompletion. No per-task migration yet — still per-phase subprocess. But the runner now knows when budget ran out and which phase was incomplete.

**Backward compatibility**: The TurnLedger tracks but does not enforce. INCOMPLETE status triggers HALT instead of silent PASS.

### Phase 2: Per-Task Subprocess Migration (Weeks 2–4) — Structural Fix

| Deliverable | Source | Lines | Risk |
|-------------|--------|-------|------|
| Tasklist parser | Solution A §5.5 | ~100 | Low |
| Context injection builder (with gate/remediation history) | Solution A §5.1 + Gap 4 | ~180 | Medium |
| Per-task subprocess orchestration | Solution A §5.5 | ~200 | Medium |
| 4-layer isolation setup | Solution A §5.2 | ~40 | Low |
| Result aggregation + phase report construction | Solution A §3.2 | ~140 | Low |
| GateMode enum + Step.gate_mode field | Solution B §2.4 | ~20 | None |
| PipelineConfig.grace_period field | Solution B §2.4 | ~10 | None |
| Turn counting + reimbursement wiring | Solution A §2.3 | ~15 | Low |
| Pre-remediation budget check | Gap 1 | ~20 | Low |
| Full-flow integration test (budget + gate + remediation + context) | Gap 6 | ~200 | Low |
| **Total** | | **~925 lines** | **Medium** |

**Value**: Full per-task subprocess with TurnLedger economics. Gates still blocking (`grace_period=0` default). Runner owns all completion state. **The MaxTurn problem is structurally eliminated at this phase.**

<!-- Source: Panel — Crispin recommendation -->
**Gap 6 (Crispin)**: The full-flow integration test is a Phase 2 deliverable, not deferred. It must exercise:
1. Task passes gate → reimbursed → context injection includes gate PASS
2. Task fails gate → remediation spawned → remediation passes → credit remediation turns → context includes remediation history
3. Task fails gate → remediation fails → diagnostic chain → HALT with resume command
4. Budget too low for remediation → skip remediation → HALT with budget message

### Phase 3: Trailing Gates + Remediation (Weeks 5–6) — Quality Enforcement

| Deliverable | Source | Lines | Risk |
|-------------|--------|-------|------|
| TrailingGateRunner + GateResultQueue | Solution B §2.1 | ~120 | Medium |
| DeferredRemediationLog | Solution B §2.1 | ~80 | Low |
| Trailing gate integration into per-task loop | Solution B §2.5 (adapted) | ~100 | Medium |
| conflict_review.py | Solution B §2.2 | ~80 | Low |
| diagnostic_chain.py | Solution B §2.3 | ~100 | Medium |
| Remediation retry with TurnLedger integration | Overlap Resolution #1 | ~60 | Medium |
| TUI gate column | Solution B §2.6 | ~40 | Low |
| GateDisplayState + PhaseResult modifications | Solution B §2.8 | ~30 | None |
| Resume semantics with diagnostic output | Gap 5 | ~40 | Low |
| **Total** | | **~650 lines** | **Medium** |

**Value**: Opt-in trailing gates with `--trailing-gates` or `grace_period=1`. Backward compatible — `grace_period=0` is identical to Phase 2 behavior.

### Phase 4: Rollout + Optimization (Week 7+) — Production Hardening

| Deliverable | Source |
|-------------|--------|
| Shadow mode: trailing gate metrics alongside blocking | Solution B §7.2 T06.01 |
| Dynamic task budget calibration from observed costs | Solution A §7.1 Phase 3 |
| Parallel task spawning for independent tasks | Solution A §7.1 Phase 3 |
| KPI report with trailing gate latency | Solution B §7.2 T06.03 |
| Shadow-to-Soft-to-Full promotion gates | Solution B §7.2 T06.05–T06.10 |
| Progressive summarization for context injection | Solution A §5.1.4 |
| Subprocess warm-start caching | Solution A §7.1 Phase 3 |

### Sequencing Rationale (Newman)

Each phase is independently deployable and valuable:
- **Phase 1 alone**: Detects the problem (no structural fix, but no more silent failures)
- **Phase 1+2**: Structurally eliminates the problem (per-task subprocess + TurnLedger)
- **Phase 1+2+3**: Adds quality enforcement (trailing gates + remediation)
- **Phase 1+2+3+4**: Production-hardened with metrics and gradual rollout

A user can stop at Phase 2 and have a fully working solution to the MaxTurn problem.

---

<!-- Source: Solution B §8 expanded to include Solution A components -->
## 12. Traceability Matrix

### 12.1 Task Disposition Summary

| Disposition | Count | Percentage |
|------------|-------|------------|
| KEPT (unchanged from v1.2.1) | 27 | 49.1% |
| MODIFIED (adapted for unified design) | 20 | 36.4% |
| SUPERSEDED (replaced by new task) | 1 | 1.8% |
| REMOVED | 0 | 0.0% |
| NEW (unified spec additions) | 7 | 12.7% |
| **Total** | **55** | 100% |

Plus 9 new tasks from Solution B's trailing gate additions = **64 total tasks**.

### 12.2 Phase-by-Phase Disposition

#### Phase 1: Blocker Resolution and Decision Lock (5 tasks, 5 deliverables)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T01.01 | **KEPT** | Profile thresholds still needed for gate evaluation |
| T01.02 | **MODIFIED** | Retry/backoff values now also parameterize remediation retry timing |
| T01.03 | **KEPT** | Rollback triggers unchanged |
| T01.04 | **KEPT** | Decision registry unchanged |
| T01.05 | **KEPT** | Override approver model unchanged |

#### Phase 2: State Machine and Illegal-Transition Tests (8 → 10 tasks)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T02.01 | **KEPT** | Audit state enums still needed |
| T02.02 | **MODIFIED** | validate_transition() shifts from pre-exec to post-exec for task scope; still pre-exec for release scope |
| T02.03 | **KEPT** | Legal transition tests still valid |
| T02.04 | **KEPT** | Illegal transition tests still valid |
| T02.05 | **MODIFIED** | Stuck-state recovery now includes "deferred remediation" as a recovery path |
| T02.06 | **SUPERSEDED** | tui.py completion guard replaced by trailing gate + remediation pull-back. New: T02.06v2 |
| T02.07 | **KEPT** | Regression check still required |
| T02.08 | **KEPT** | OverrideRecord release prohibition unchanged |
| T02.09 | **NEW** | GateResultQueue + DeferredRemediationLog |
| T02.10 | **NEW** | conflict_review.py with file-level overlap detection |

#### Phase 3: Deterministic Gate Evaluator and Profile Tests (8 → 9 tasks)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T03.01 | **MODIFIED** | Evaluator contract adds trailing gate mode specification |
| T03.02 | **MODIFIED** | Command spec adds `--trailing-gates` flag |
| T03.03 | **KEPT** | GateResult schema unchanged |
| T03.04 | **KEPT** | Determinism tests unchanged |
| T03.05 | **KEPT** | Major-severity tests unchanged |
| T03.06 | **KEPT** | Unknown/missing input tests unchanged |
| T03.07 | **KEPT** | Evidence completeness tests unchanged |
| T03.08 | **KEPT** | --strictness alias tests unchanged |
| T03.09 | **NEW** | Trailing gate determinism tests (same input → same gate result regardless of timing) |

#### Phase 4: Runtime Controls and Override Governance (13 → 16 tasks)

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
| T04.14 | **NEW** | diagnostic_chain.py implementation (troubleshoot → adversarial → adversarial → summary) |
| T04.15 | **NEW** | Remediation retry tests: first fail → retry → second fail → halt + diagnostic |
| T04.16 | **NEW** | Conflict review tests: overlapping files → re-gate; no overlap → resume |

#### Phase 5: Sprint CLI Regression Gate (5 → 6 tasks)

| Task | Disposition | Rationale |
|------|------------|-----------|
| T05.01 | **KEPT** | Baseline regression unchanged |
| T05.02 | **MODIFIED** | Backward-compat now also asserts GateMode.BLOCKING default |
| T05.03 | **KEPT** | Regression gaps unchanged |
| T05.04 | **MODIFIED** | Non-audit guard bypass now also verifies trailing gate does not fire for non-audit phases |
| T05.05 | **KEPT** | Zero new failures unchanged |
| T05.06 | **NEW** | grace_period=0 backward-compat test: zero daemon threads, identical to v1.2.1 |

#### Phase 6: Rollout Validation and Promotion Gates (10 → 11 tasks)

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
| T06.11 | **NEW** | Shadow trailing gate metrics collection and comparison to blocking baseline |

#### New Tasks from Unified Spec (Solution A components)

| Task | Phase | Description | Source |
|------|-------|-------------|--------|
| T-A.01 | P2 (unified) | TurnLedger dataclass implementation | Solution A §2.1 |
| T-A.02 | P1 (unified) | error_max_turns NDJSON detection in OutputMonitor | Solution A §3.4 |
| T-A.03 | P1 (unified) | Reclassify PASS_NO_REPORT + error_max_turns → INCOMPLETE | Solution A §7.1 |
| T-A.04 | P2 (unified) | Tasklist parser (markdown → task inventory) | Solution A §5.5 |
| T-A.05 | P2 (unified) | Context injection builder (with gate/remediation history — Gap 4) | Solution A §5.1 + Gap 4 |
| T-A.06 | P2 (unified) | Per-task subprocess orchestration loop | Solution A §5.5 |
| T-A.07 | P2 (unified) | 4-layer subprocess isolation setup | Solution A §5.2 |
| T-A.08 | P2 (unified) | Result aggregation + runner-constructed phase reports | Solution A §3.2 |
| T-A.09 | P2 (unified) | Pre-remediation budget check (Gap 1) | Gap 1 |
| T-A.10 | P2 (unified) | Full-flow integration test (budget + gate + remediation + context) (Gap 6) | Gap 6 |

### 12.3 Timing Semantics Lens

| Element | Timing Semantics | Notes |
|---------|------------------|-------|
| Release guard (T04.02, D-0023) | Still blocking | Release scope always hard-stop |
| validate_transition() for task scope (T02.02) | Shifted to trailing | Evaluated after task output, before next-next task |
| OverrideRecord constructor prohibition (T02.08, D-0013) | Still blocking | Compile-time / construction-time invariant |
| tui.py task completion guard (T02.06) | Still synchronous but moved | Replaced by post-task seam enforcement |
| TurnLedger debit/credit cycle | Newly added economic model | Solution A contribution |
| Per-task subprocess spawning | Newly added execution architecture | Solution A contribution |
| Deferred remediation / conflict review / diagnostic chain | Newly added recovery behavior | Solution B contribution |

---

<!-- Source: Solution A §5 (weaknesses) + Solution B §9 (risks) + Panel gaps -->
## 13. Risk Assessment

### 13.1 Inherited Risks

| Risk | Source | Impact | Mitigation |
|------|--------|--------|------------|
| Context fragmentation | Solution A §5.1 | Task N+1 doesn't know what task N did | Structured context injection with gate/remediation history (§4.3, Gap 4) |
| Subprocess cold-start overhead | Solution A §5.2 | ~92 turns for 46 tasks | 4-layer isolation reduces to ~5K tokens; budgeted in TurnLedger model |
| Loss of inter-task optimization | Solution A §5.3 | Redundant file reads | Context injection + observation that many tasks touch different files |
| More total turns consumed | Solution A §5.4 | ~138 turns overhead vs ~12 for per-phase | Budget model accommodates this; 71 turns of margin |
| Complex orchestration | Solution A §5.5 | ~865+ lines of new code | 10+ independently testable components |
| API rate limiting | Solution A §5.6 | 46+ subprocess spawns | Configurable concurrency; sequential default; backoff between spawns |
| Gate daemon thread crashes | Solution B §9 | Gate failure undetected | Daemons catch all exceptions and post FAIL result to queue |
| Remediation breaks subsequent work | Solution B §9 | Cascading failures | Conflict review with file-level overlap detection (§7) |
| Queue corruption under load | Solution B §9 | Results lost | queue.Queue is stdlib, well-tested; no custom synchronization |

### 13.2 Newly Identified Risks (Panel Gaps)

| Risk | Source | Impact | Mitigation |
|------|--------|--------|------------|
| Low budget + gate failure compound failure | Gap 1 | Wasted turns on doomed remediation | Pre-remediation budget check: `ledger.can_remediate()` (§3.5) |
| Diagnostic chain confused by budget problem | Gap 2 | Root cause analysis targets wrong issue | Diagnostic chain is runner-side, free; budget-specific halt message skips chain |
| Isolation boundary confusion | Gap 3 | Implementer creates daemon inside subprocess | Explicit documentation: gate daemons are runner-side (§5.2) |
| Missing gate/remediation context | Gap 4 | Task N+1 doesn't know about gate failures | Context injection includes gate outcomes + remediation history (§4.3) |
| Unusable resume after diagnostic | Gap 5 | User can't act on HALT | Resume command includes task ID + diagnostic output (§8.4) |
| No full-flow integration test | Gap 6 | Compound scenarios untested | Phase 2 deliverable: 4-scenario integration test (§11, Phase 2) |
| Gate evaluation too slow on large output | Gap 7 | Sync point blocks too long | NFR: <50ms for output files up to 100KB; tracked in TrailingGateResult.evaluation_ms (§5.2) |

### 13.3 Risk Priority Matrix

| Priority | Risk | Probability | Impact | Phase Addressed |
|----------|------|-------------|--------|-----------------|
| 🔴 Critical | Silent incompletion (the original problem) | Already materialized | Sprint reports false success | Phase 1 (detection) + Phase 2 (elimination) |
| 🔴 Critical | Low budget + gate failure (Gap 1) | Medium | Wasted turns, delayed halt | Phase 2 |
| 🟡 High | Context fragmentation | High | Suboptimal task output | Phase 2 (context injection) |
| 🟡 High | Cold-start overhead | Certain | ~92 turns fixed cost | Phase 2 (isolation) |
| 🟢 Medium | Gate daemon crash | Low | One gate result missed | Phase 3 (exception handling) |
| 🟢 Medium | Remediation cascading failure | Low | Extra tasks re-gated | Phase 3 (conflict review) |
| 🟢 Low | API rate limiting | Low | Slight delay between tasks | Phase 4 (concurrency config) |

---

<!-- Source: Solution B §10 + Panel Gap 6 + Panel Gap 7 -->
## 14. Test Strategy

### 14.1 Unit Tests (per module)

| Test File | Module | Key Scenarios |
|-----------|--------|---------------|
| `test_turn_ledger.py` | sprint/models.py | Debit/credit arithmetic, budget exhaustion, can_launch/can_remediate boundary, reimbursement rate |
| `test_tasklist_parser.py` | sprint/config.py | Markdown parsing, task ID extraction, dependency annotation, malformed input |
| `test_context_injection.py` | sprint/process.py | Prior results summary, gate outcome inclusion, remediation history, progressive summarization |
| `test_trailing_gate.py` | pipeline/trailing_gate.py | GateResultQueue thread safety, DeferredRemediationLog serialization, TrailingGateRunner submit/drain/wait |
| `test_conflict_review.py` | pipeline/conflict_review.py | File overlap detection, re-gate logic, no-overlap passthrough, empty intervening set |
| `test_diagnostic_chain.py` | pipeline/diagnostic_chain.py | Prompt construction, chain step sequencing (mocked sub-agents), chain failure graceful degradation |
| `test_error_max_turns.py` | sprint/monitor.py | NDJSON regex detection, last-line extraction, false positive rejection |

### 14.2 Integration Tests

| Test File | Scope | Key Scenarios |
|-----------|-------|---------------|
| `test_executor_per_task.py` | Sprint executor | Per-task subprocess loop, TurnLedger debit/credit across tasks, phase aggregation |
| `test_executor_trailing.py` | Pipeline executor | Full pipeline with trailing gates, remediation injection, conflict review |
| `test_executor_compat.py` | Both | grace_period=0 produces identical results to v1.2.1; zero daemon threads (Gap 7 validation) |
| `test_sprint_trailing.py` | Sprint + TUI | Sprint executor with trailing gates through TUI, gate column rendering |

<!-- Source: Panel Gap 6 — Crispin -->
### 14.3 Full-Flow Integration Test (Gap 6)

**Phase 2 deliverable** (Crispin: "should not be deferred"). Exercises the complete unified flow:

```python
class TestFullFlowIntegration:
    """Integration test exercising budget + gate + remediation + context."""

    def test_pass_flow(self):
        """Scenario 1: Task passes gate → reimbursed → context includes PASS."""
        # Launch task subprocess → exits normally
        # Gate evaluates output → PASS
        # TurnLedger credits 90%
        # Next task's context injection includes: "T01.01: PASS, reimbursed 7/8"
        ...

    def test_fail_remediate_pass(self):
        """Scenario 2: Task fails gate → remediation passes → credit remediation."""
        # Launch task subprocess → exits normally
        # Gate evaluates output → FAIL
        # Pre-remediation budget check → sufficient
        # Spawn remediation subprocess → exits normally
        # Remediation gate → PASS
        # TurnLedger credits remediation turns only
        # Context injection includes remediation history
        ...

    def test_fail_remediate_fail_halt(self):
        """Scenario 3: Task fails → remediation fails → diagnostic → HALT."""
        # Launch task subprocess → exits normally
        # Gate evaluates output → FAIL
        # Remediation subprocess → exits, gate FAIL
        # Retry → exits, gate FAIL
        # Diagnostic chain fires (mocked)
        # HALT with resume command + diagnostic output
        ...

    def test_low_budget_gate_fail(self):
        """Scenario 4: Budget too low for remediation → skip → HALT."""
        # Drain ledger to near-zero
        # Launch task subprocess → exits normally
        # Gate evaluates output → FAIL
        # ledger.can_remediate() → False
        # HALT with budget-specific message
        # No diagnostic chain (budget problem, not quality problem)
        ...
```

### 14.4 Property-Based Tests

- Trailing gate result ordering: results arrive in submission order (or are correctly associated by step_id)
- Remediation idempotency: running remediation twice produces same result
- `grace_period=0` invariant: no daemon threads spawned (check `threading.active_count()`)
- TurnLedger invariant: `available() == initial_budget - consumed + reimbursed` always holds
- Budget monotonicity: `available()` is non-increasing over time (credits never exceed debits due to 90% rate)

<!-- Source: Panel Gap 7 — Crispin -->
### 14.5 Performance NFR (Gap 7)

**NFR-GATE-PERF**: Gate evaluation SHALL complete within 50ms for output files up to 100KB.

Validation:
- Unit test: time `gate_passed()` on synthetic 100KB output → assert <50ms
- Tracked at runtime: `TrailingGateResult.evaluation_ms` field
- Monitored in Phase 4 shadow mode KPI report

---

## Appendix A: Worked Example (46-Task Sprint)

<!-- Source: Solution A §6 -->

Using task-level data extrapolated from the cleanup-audit-v2 sprint:

| Task | Allocated | Used | Overhead | Gate | Reimbursed (90%) | Budget |
|------|-----------|------|----------|------|-------------------|--------|
| T01.01 | 15 | 8 | ~2 | PASS | 7 | 199 |
| T01.02 | 15 | 6 | ~2 | PASS | 5 | 198 |
| T01.03 | 15 | 7 | ~2 | PASS | 6 | 197 |
| ... | ... | ... | ... | ... | ... | ... |
| T05.06 | 15 | 10 | ~2 | PASS | 9 | ~185 |
| T05.07 | 15 | 8 | ~2 | PASS | 7 | ~184 |
| T05.08 | 15 | 6 | ~2 | PASS | 5 | ~183 |
| T05.09 | 15 | 12 | ~2 | PASS | 10 | ~181 |

Every task — including T05.06 through T05.09 (the 4 tasks that were never executed in the original sprint) — gets its own budget allocation. No task is starved because another task consumed too many turns.

## Appendix B: Implementation Complexity Summary

| Component | Lines | Complexity | Phase |
|-----------|-------|------------|-------|
| TurnLedger | ~50 | Trivial (arithmetic) | 1 |
| error_max_turns detection | ~15 | Trivial (regex) | 1 |
| INCOMPLETE reclassification | ~10 | Trivial (enum) | 1 |
| Tasklist parser | ~100 | Standard (regex/markdown) | 2 |
| Context injection builder | ~180 | Moderate (prompt engineering + Gap 4) | 2 |
| Per-task subprocess orchestration | ~200 | Standard (loop + spawn + wait) | 2 |
| 4-layer isolation setup | ~40 | Simple (directory ops) | 2 |
| Result aggregation | ~140 | Standard (reduction) | 2 |
| Pre-remediation budget check | ~20 | Simple (conditional) | 2 |
| Full-flow integration test | ~200 | Standard (test scenarios — Gap 6) | 2 |
| TrailingGateRunner + GateResultQueue | ~120 | Moderate (threading) | 3 |
| DeferredRemediationLog | ~80 | Standard (serialization) | 3 |
| Trailing gate integration | ~100 | Moderate (executor modification) | 3 |
| conflict_review.py | ~80 | Standard (set operations) | 3 |
| diagnostic_chain.py | ~100 | Moderate (sub-agent orchestration) | 3 |
| Remediation retry + TurnLedger | ~60 | Moderate (state machine) | 3 |
| TUI gate column | ~40 | Simple (display) | 3 |
| GateDisplayState + model updates | ~30 | Simple (enum + field) | 3 |
| Resume semantics | ~40 | Simple (string formatting — Gap 5) | 3 |
| Turn counting | ~15 | Trivial (file read + count) | 2 |
| Task dependency ordering | ~120 | Standard (topological sort) | 2 |
| **Total** | **~1,740 lines** | **Medium overall** | **Weeks 1–6** |
