# Phase 5 -- Trailing Gate Infrastructure

Implement the trailing gate evaluation infrastructure: TrailingGateRunner, GateResultQueue, DeferredRemediationLog, and scope-based gate strategy. This is the quality enforcement layer that evaluates task output after subprocess termination.

### T05.01 -- Implement TrailingGateRunner in pipeline/trailing_gate.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | TrailingGateRunner is the core gate evaluation engine — it spawns daemon threads to evaluate task output against gate criteria while the runner continues to the next task. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (threading architecture), performance (gate evaluation latency) |
| Tier | STRICT |
| Confidence | [████████──] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0019/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0019/evidence.md

**Deliverables:**
- TrailingGateRunner class (~120 lines) in `src/superclaude/cli/pipeline/trailing_gate.py` with methods: submit(), drain(), wait_for_pending(), cancel()

**Steps:**
1. **[PLANNING]** Read existing pipeline gate patterns to align TrailingGateRunner interface
2. **[PLANNING]** Design thread safety model: daemon threads for evaluation, main thread for orchestration
3. **[EXECUTION]** Implement submit(): spawn daemon thread to evaluate gate criteria on task output
4. **[EXECUTION]** Implement drain(): collect completed gate results from daemon threads
5. **[EXECUTION]** Implement wait_for_pending(): block main thread with bounded timeout until all pending gates complete
6. **[EXECUTION]** Implement cancel(): propagate cancellation to all pending daemon threads
7. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k trailing_gate_runner -v` with concurrent submit/drain scenarios
8. **[COMPLETION]** Record deliverable evidence in D-0019/evidence.md

**Acceptance Criteria:**
- `submit()` spawns daemon thread for gate evaluation; thread terminates after evaluation completes
- `wait_for_pending()` blocks with bounded timeout (no indefinite hangs); returns when all pending gates complete
- `cancel()` propagates to all active daemon threads; threads terminate gracefully
- `uv run pytest tests/pipeline/test_trailing_gate.py -k runner` exits 0

**Validation:**
- `uv run pytest tests/pipeline/test_trailing_gate.py -k runner -v`
- Evidence: linkable artifact produced at D-0019/evidence.md

**Dependencies:** T02.05 (GateMode enum)
**Rollback:** Remove TrailingGateRunner; gates evaluate synchronously only

---

### T05.02 -- Implement GateResultQueue in pipeline/trailing_gate.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | A thread-safe queue is needed to collect gate evaluation results from daemon threads without race conditions or data corruption. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | system-wide (thread safety) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0020/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0020/evidence.md

**Deliverables:**
- GateResultQueue class using stdlib `queue.Queue` with methods: put(), drain(), pending_count(); thread-safe under concurrent access from multiple daemon threads

**Steps:**
1. **[PLANNING]** Review stdlib `queue.Queue` API for thread-safe put/get patterns
2. **[PLANNING]** Define TrailingGateResult data structure: step_id, passed, evaluation_ms, failure_reason
3. **[EXECUTION]** Implement GateResultQueue wrapping `queue.Queue` with put(), drain(), pending_count() methods
4. **[EXECUTION]** Ensure drain() collects all available results without blocking; pending_count() returns accurate count
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k gate_result_queue -v` with concurrent put/drain from multiple threads
6. **[COMPLETION]** Record deliverable evidence in D-0020/evidence.md

**Acceptance Criteria:**
- put() and drain() are thread-safe under concurrent access from ≥3 threads (no data loss or corruption)
- pending_count() returns accurate count of unprocessed results at any point
- Results are associated with correct step_id (no cross-contamination between gate evaluations)
- `uv run pytest tests/pipeline/ -k gate_result_queue` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k gate_result_queue -v`
- Evidence: linkable artifact produced at D-0020/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner uses queue)
**Rollback:** Remove GateResultQueue; results collected synchronously

---

### T05.03 -- Implement DeferredRemediationLog in pipeline/trailing_gate.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | DeferredRemediationLog tracks gate failures that require remediation, enabling the runner to process them at sync points and persist state for --resume support. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (serialization), system-wide (cross-task state) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0021/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0021/evidence.md

**Deliverables:**
- DeferredRemediationLog class (~80 lines) with methods: append(), pending_remediations(), mark_remediated(), serialize(), deserialize(); single-writer thread safety with disk persistence for --resume

**Steps:**
1. **[PLANNING]** Define remediation entry schema: step_id, gate_result, failure_reason, remediation_status
2. **[PLANNING]** Design serialization format for --resume persistence (JSON on disk)
3. **[EXECUTION]** Implement append(), pending_remediations(), mark_remediated() with single-writer thread safety
4. **[EXECUTION]** Implement serialize()/deserialize() for disk persistence and --resume recovery
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k deferred_remediation -v` testing persistence and recovery
6. **[COMPLETION]** Record deliverable evidence in D-0021/evidence.md

**Acceptance Criteria:**
- append() adds remediation entries; pending_remediations() returns unresolved entries; mark_remediated() updates status
- Serialization to disk produces valid JSON; deserialize() recovers exact state for --resume
- Single-writer thread safety: no corruption when main thread writes while daemon threads read
- `uv run pytest tests/pipeline/ -k deferred_remediation` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k deferred_remediation -v`
- Evidence: linkable artifact produced at D-0021/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner produces gate failures)
**Rollback:** Remove DeferredRemediationLog; gate failures trigger immediate HALT

---

### T05.04 -- Implement Scope-Based Gate Strategy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | Different scopes require different gate behavior: release gates must always block (safety), while task-level gates can trail (throughput). Scope-based strategy enforces this invariant. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (gate policy) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0022/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0022/evidence.md

**Deliverables:**
- Scope-based gate strategy logic: Release scope = BLOCKING always, Milestone scope = configurable (default BLOCKING), Task scope = TRAILING default; uses existing `validate_transition()` for scope detection

**Steps:**
1. **[PLANNING]** Read existing `validate_transition()` to understand scope detection mechanism
2. **[PLANNING]** Map scope → GateMode: Release → BLOCKING (immutable), Milestone → configurable, Task → TRAILING
3. **[EXECUTION]** Implement scope-to-gate-mode resolution function using existing scope detection
4. **[EXECUTION]** Enforce Release scope as always BLOCKING (not configurable, not overridable)
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k scope_gate -v` verifying all scope combinations
6. **[COMPLETION]** Record deliverable evidence in D-0022/evidence.md

**Acceptance Criteria:**
- Release gates are always BLOCKING regardless of configuration (enforced invariant)
- Milestone gates default to BLOCKING but configurable to TRAILING
- Task gates default to TRAILING when grace_period > 0
- `uv run pytest tests/pipeline/ -k scope_gate` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k scope_gate -v`
- Evidence: linkable artifact produced at D-0022/evidence.md

**Dependencies:** T02.05 (GateMode enum, grace_period)
**Rollback:** All scopes revert to BLOCKING (v1.2.1 behavior)

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.04

**Purpose:** Verify core trailing gate components before adding executor branching logic.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P05-T01-T04.md

**Verification:**
- TrailingGateRunner spawns and manages daemon threads correctly
- GateResultQueue handles concurrent access without data loss
- Scope-based strategy enforces Release = BLOCKING invariant

**Exit Criteria:**
- `uv run pytest tests/pipeline/ -k "trailing_gate or gate_result_queue or deferred or scope_gate" -v` exits 0
- Thread safety tests pass under concurrent load
- No deadlocks detected in bounded-wait scenarios

---

### T05.05 -- Implement Executor Trailing vs Blocking Branch Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | The executor must branch between trailing and blocking paths based on GateMode and grace_period, routing to the correct evaluation strategy for each gate scope. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (executor branching) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0023/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0023/evidence.md

**Deliverables:**
- Executor branching logic in `execute_pipeline()` that selects trailing or blocking evaluation path based on GateMode + grace_period configuration; trailing path includes sync point execution

**Steps:**
1. **[PLANNING]** Read `execute_pipeline()` in pipeline executor to identify gate evaluation callsite
2. **[PLANNING]** Map branching conditions: BLOCKING → synchronous gate evaluation, TRAILING → submit to TrailingGateRunner
3. **[EXECUTION]** Implement branching: if gate_mode == TRAILING and grace_period > 0 → submit to TrailingGateRunner
4. **[EXECUTION]** Implement sync point: at phase boundary, call `wait_for_pending()` to collect trailing gate results
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k executor_branch -v` testing both paths
6. **[COMPLETION]** Record deliverable evidence in D-0023/evidence.md

**Acceptance Criteria:**
- BLOCKING mode: gate evaluates synchronously before proceeding to next step (existing behavior)
- TRAILING mode: gate submitted to TrailingGateRunner, execution continues; sync point at phase boundary
- grace_period=0 forces BLOCKING path regardless of gate_mode (backward compatibility)
- `uv run pytest tests/pipeline/ -k executor_branch` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k executor_branch -v`
- Evidence: linkable artifact produced at D-0023/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner), T05.04 (scope-based strategy)
**Rollback:** Remove branching; all gates evaluate synchronously (BLOCKING only)

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm trailing gate infrastructure is operational before validation milestone V2.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P05-END.md

**Verification:**
- TrailingGateRunner, GateResultQueue, and DeferredRemediationLog function correctly under concurrent load
- Executor correctly branches between trailing and blocking paths
- Scope-based strategy enforces Release=BLOCKING invariant

**Exit Criteria:**
- `uv run pytest tests/pipeline/ -v` exits 0 (full pipeline test suite)
- All 5 deliverables (D-0019 through D-0023) have evidence artifacts
- Success criterion SC-003 (every task output passes gate) partially validated
