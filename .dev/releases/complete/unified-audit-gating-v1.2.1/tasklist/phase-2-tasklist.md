# Phase 2 -- Per-Task Subprocess Architecture

Migrate from per-phase subprocess to per-task subprocess spawning with runner-owned task sequencing, 4-layer isolation, and TurnLedger integration. This structurally eliminates the MaxTurn problem by giving each task its own budget allocation and subprocess lifecycle.

### T02.01 -- Implement Tasklist Parser in sprint/config.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | The runner needs to parse phase tasklist markdown files into a structured task inventory with IDs and dependency annotations to drive per-task subprocess spawning. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (task inventory parsing) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0005/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0005/evidence.md

**Deliverables:**
- Tasklist parser (~100 lines) in `src/superclaude/cli/sprint/config.py` that converts phase tasklist markdown into a task inventory with task IDs, descriptions, and dependency annotations

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/config.py` to identify existing config parsing patterns
2. **[PLANNING]** Analyze phase tasklist markdown format (T<PP>.<TT> headers, dependency fields)
3. **[EXECUTION]** Implement markdown parser extracting task ID, title, dependencies, and description from each `### T<PP>.<TT>` block
4. **[EXECUTION]** Return structured TaskInventory list with dependency graph edges
5. **[EXECUTION]** Handle malformed input gracefully: missing fields default to empty, invalid IDs logged as warnings
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k tasklist_parser -v` with valid and malformed inputs
7. **[COMPLETION]** Record deliverable evidence in D-0005/evidence.md

**Acceptance Criteria:**
- Parser extracts task IDs matching `T<PP>.<TT>` pattern from phase tasklist markdown headings
- Dependency field values are parsed into a list of task ID references per task
- Malformed input (missing headings, invalid IDs, empty files) is handled without exceptions
- `uv run pytest tests/sprint/test_config.py -k tasklist_parser` exits 0

**Validation:**
- `uv run pytest tests/sprint/test_config.py -k tasklist_parser -v`
- Evidence: linkable artifact produced at D-0005/evidence.md

**Dependencies:** None (parser is independent of TurnLedger)
**Rollback:** Remove parser function from sprint/config.py

---

### T02.02 -- Implement Per-Task Subprocess Orchestration Loop in sprint/executor.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The core architectural change: each task gets its own subprocess with budget allocation from TurnLedger, eliminating the shared-budget exhaustion problem that causes silent incompletion. |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide (orchestration architecture), performance (subprocess overhead), data (task state management) |
| Tier | STRICT |
| Confidence | [████████──] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0006/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0006/evidence.md

**Deliverables:**
- Per-task subprocess orchestration loop (~200 lines) in `src/superclaude/cli/sprint/executor.py`: iterates over TaskInventory, spawns one subprocess per task, integrates with TurnLedger for budget allocation and tracking

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` to understand existing per-phase subprocess flow
2. **[PLANNING]** Map the transition from per-phase to per-task: identify callsites that assume one subprocess per phase
3. **[EXECUTION]** Implement task iteration loop: for each task in TaskInventory, allocate budget from ledger, spawn subprocess, collect result
4. **[EXECUTION]** Integrate TurnLedger: debit on launch, track consumed turns from output, credit reimbursement on completion
5. **[EXECUTION]** Implement task starvation prevention: if any task cannot launch due to budget, HALT with remaining task list
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k "per_task or orchestration" -v` with multi-task scenarios
7. **[COMPLETION]** Record deliverable evidence in D-0006/evidence.md

**Acceptance Criteria:**
- Each task in the inventory gets its own subprocess (verified by subprocess count == task count in test output)
- TurnLedger debit/credit occurs per-task: budget decreases on launch, reimbursement applied on completion
- No task starvation: if budget insufficient for next task, HALT includes remaining task IDs
- `uv run pytest tests/sprint/test_executor.py -k per_task` exits 0

**Validation:**
- `uv run pytest tests/sprint/test_executor.py -k per_task -v`
- Evidence: linkable artifact produced at D-0006/evidence.md

**Dependencies:** T01.01 (TurnLedger), T02.01 (TaskInventory parser)
**Rollback:** Revert to per-phase subprocess loop in executor.py

---

### T02.03 -- Implement 4-Layer Subprocess Isolation Setup

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | Subprocess isolation ensures cold-start cost stays within ~5K tokens (~2 turns) and prevents cross-task state leakage that could corrupt budget accounting or task output. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (cold-start overhead) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0007/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0007/evidence.md

**Deliverables:**
- 4-layer isolation setup (~40 lines): scoped working directory, git boundary, empty plugin directory, restricted settings — applied before each subprocess launch

**Steps:**
1. **[PLANNING]** Read existing subprocess launch code to identify where isolation layers can be injected
2. **[PLANNING]** Define the 4 isolation layers: working dir scoping, git boundary, plugin dir, settings restriction
3. **[EXECUTION]** Implement isolation layer setup function called before each subprocess spawn
4. **[EXECUTION]** Verify cold-start cost target: subprocess with all 4 layers active should consume ≤5K tokens (~2 turns)
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k isolation -v` verifying all 4 layers are active per subprocess
6. **[COMPLETION]** Record deliverable evidence in D-0007/evidence.md

**Acceptance Criteria:**
- All 4 isolation layers (scoped working dir, git boundary, empty plugin dir, restricted settings) are verified active per subprocess
- Cold-start cost measured at ≤5K tokens (~2 turns) in test subprocess with isolation enabled
- No cross-task state leakage between consecutive subprocess invocations
- Isolation setup function is independently testable with a clear interface

**Validation:**
- `uv run pytest tests/sprint/ -k isolation -v`
- Evidence: linkable artifact produced at D-0007/evidence.md

**Dependencies:** T02.02 (orchestration loop spawns subprocesses)
**Rollback:** Remove isolation setup; subprocesses run without layer restrictions

---

### T02.04 -- Implement Result Aggregation and Phase Reports

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Runner-constructed phase reports eliminate dependency on agent self-reporting, ensuring accurate task outcome tracking even when subprocesses are budget-exhausted. |
| Effort | M |
| Risk | Low |
| Risk Drivers | data (result aggregation state) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0008/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0008/evidence.md

**Deliverables:**
- Result aggregation logic (~140 lines) that collects TaskResult objects from each subprocess and constructs a PhaseResult report without relying on agent self-reporting

**Steps:**
1. **[PLANNING]** Read existing phase report format to maintain backward compatibility
2. **[PLANNING]** Define TaskResult → PhaseResult aggregation: tasks_total, tasks_passed, tasks_failed, tasks_incomplete
3. **[EXECUTION]** Implement TaskResult collection from subprocess output parsing
4. **[EXECUTION]** Implement PhaseResult construction: aggregate task outcomes, budget tracking, timing data
5. **[EXECUTION]** Write PhaseResult as runner-constructed report (not agent-generated)
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k "result_aggregation or phase_report" -v`
7. **[COMPLETION]** Record deliverable evidence in D-0008/evidence.md

**Acceptance Criteria:**
- PhaseResult contains tasks_total, tasks_passed, tasks_failed, tasks_incomplete counts matching actual subprocess outcomes
- Phase report is constructed by the runner, not by parsing agent self-reported output
- All task outcomes are tracked including INCOMPLETE (budget-exhausted) tasks
- `uv run pytest tests/sprint/ -k phase_report` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k "result_aggregation or phase_report" -v`
- Evidence: linkable artifact produced at D-0008/evidence.md

**Dependencies:** T02.02 (orchestration loop produces TaskResults)
**Rollback:** Revert to existing phase report mechanism

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify core subprocess architecture is functional before adding GateMode and turn counting.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P02-T01-T04.md

**Verification:**
- Tasklist parser correctly extracts tasks and dependencies from phase markdown files
- Per-task subprocess loop launches one subprocess per task with budget integration
- Result aggregation produces accurate PhaseResult from collected TaskResults

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k "tasklist_parser or per_task or isolation or phase_report" -v` exits 0
- At least one multi-task integration test exercises the full loop (parse → launch → collect → aggregate)
- No regressions in existing sprint tests

---

### T02.05 -- Add GateMode Enum and PipelineConfig.grace_period

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | GateMode enum and grace_period configuration enable the trailing gate system (Phase 5) while maintaining backward compatibility via BLOCKING default and grace_period=0. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0009/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0009/evidence.md

**Deliverables:**
- GateMode enum (~20 lines) with BLOCKING and TRAILING values, plus Step.gate_mode field defaulting to BLOCKING
- PipelineConfig.grace_period field (~10 lines) defaulting to 0 for backward compatibility

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/models.py` to identify Step and PipelineConfig dataclasses
2. **[PLANNING]** Verify BLOCKING default ensures identical behavior to v1.2.1 when grace_period=0
3. **[EXECUTION]** Add GateMode enum (BLOCKING, TRAILING) and Step.gate_mode field with BLOCKING default
4. **[EXECUTION]** Add PipelineConfig.grace_period integer field with default 0
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k gate_mode -v` to verify defaults and backward compat
6. **[COMPLETION]** Record deliverable evidence in D-0009/evidence.md

**Acceptance Criteria:**
- GateMode.BLOCKING is the default for Step.gate_mode
- PipelineConfig.grace_period defaults to 0
- Existing tests pass without modification (backward compatibility verified)
- `uv run pytest tests/pipeline/ -k gate_mode` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k gate_mode -v`
- Evidence: linkable artifact produced at D-0009/evidence.md

**Dependencies:** None (enum and config are independent)
**Rollback:** Remove GateMode enum and grace_period field

---

### T02.06 -- Implement Turn Counting and TurnLedger Debit Wiring

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Accurate turn counting from subprocess output enables the TurnLedger to track actual consumption and enforce pre-remediation budget checks, preventing wasted turns on doomed remediation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (turn counting accuracy) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0010/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0010/evidence.md

**Deliverables:**
- Turn counting logic (~15 lines) that extracts actual turn count from subprocess NDJSON output
- TurnLedger debit wiring: consumed turns debited from ledger after each task completion
- Pre-remediation budget check (~20 lines): call `ledger.can_remediate()` before spawning remediation subprocess

**Steps:**
1. **[PLANNING]** Identify NDJSON output fields that indicate turn consumption in subprocess output
2. **[PLANNING]** Map debit wiring into the per-task orchestration loop from T02.02
3. **[EXECUTION]** Implement turn counting from subprocess NDJSON output (count turn-indicating lines)
4. **[EXECUTION]** Wire `ledger.debit(actual_turns)` call after each task subprocess completes
5. **[EXECUTION]** Add `ledger.can_remediate()` guard before remediation subprocess spawn (Gap 1 mitigation)
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k "turn_count or debit" -v` verifying accounting accuracy
7. **[COMPLETION]** Record deliverable evidence in D-0010/evidence.md

**Acceptance Criteria:**
- Turn count extracted from subprocess output matches actual turns consumed (verified against synthetic output)
- `ledger.debit()` called with correct turn count after each task completion
- `ledger.can_remediate()` prevents remediation spawn when budget insufficient
- `uv run pytest tests/sprint/ -k turn_count` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k "turn_count or debit" -v`
- Evidence: linkable artifact produced at D-0010/evidence.md

**Dependencies:** T01.01 (TurnLedger), T02.02 (orchestration loop)
**Rollback:** Remove turn counting and debit wiring; ledger tracks only initial budget

---

### Checkpoint: End of Phase 2

**Purpose:** Validate the complete per-task subprocess architecture before proceeding to validation milestone V1.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P02-END.md

**Verification:**
- Per-task subprocess orchestration loop launches individual subprocesses with budget allocation
- GateMode enum and grace_period defaults ensure backward compatibility
- Turn counting accurately debits TurnLedger from subprocess output

**Exit Criteria:**
- `uv run pytest tests/sprint/ -v` exits 0 (full sprint test suite including new tests)
- `uv run pytest tests/pipeline/ -v` exits 0 (pipeline tests with GateMode addition)
- All 6 deliverables (D-0005 through D-0010) have evidence artifacts
