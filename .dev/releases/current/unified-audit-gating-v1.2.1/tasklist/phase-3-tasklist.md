# Phase 3 -- Validation — Foundation & Subprocess

Validate M1 and M2 deliverables against spec requirements before proceeding to trailing gate infrastructure. This validation milestone ensures TurnLedger arithmetic, per-task subprocess orchestration, and backward compatibility are correct.

### T03.01 -- Implement TurnLedger Unit Tests with Full Branch Coverage

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | TurnLedger arithmetic correctness is foundational — debit/credit errors propagate to every downstream budget decision, potentially causing silent failures or false HALTs. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0011/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0011/evidence.md

**Deliverables:**
- TurnLedger unit test suite covering: debit/credit arithmetic, budget exhaustion boundary, reimbursement rate application, can_launch()/can_remediate() edge cases, budget monotonicity property

**Steps:**
1. **[PLANNING]** Read TurnLedger implementation from T01.01 to identify all branches and edge cases
2. **[PLANNING]** Design test cases: normal operations, boundary conditions (0 budget, max budget), reimbursement edge cases
3. **[EXECUTION]** Implement debit/credit arithmetic tests with exact expected values
4. **[EXECUTION]** Implement boundary tests: budget exhaustion, minimum_allocation threshold, minimum_remediation_budget threshold
5. **[EXECUTION]** Implement budget monotonicity property test: consumed never decreases across a sequence of operations
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py -k TurnLedger --cov=superclaude.cli.sprint.models -v`
7. **[COMPLETION]** Record coverage report in D-0011/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py -k TurnLedger --cov=superclaude.cli.sprint.models` exits 0 with 100% branch coverage on TurnLedger methods
- Tests cover: zero budget, exact-threshold budget, over-budget debit, negative reimbursement rejection
- Budget monotonicity property validated across 10+ operation sequences
- Test file located at `tests/sprint/test_models.py` following existing test conventions

**Validation:**
- `uv run pytest tests/sprint/test_models.py -k TurnLedger --cov=superclaude.cli.sprint.models -v`
- Evidence: coverage report artifact at D-0011/evidence.md

**Dependencies:** T01.01 (TurnLedger implementation)
**Rollback:** Remove TurnLedger test cases

---

### T03.02 -- Implement Per-Task Subprocess Integration Test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Integration testing validates that the full per-task loop (parse → allocate → launch → collect → aggregate) works correctly with budget tracking across multiple tasks. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0012/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0012/evidence.md

**Deliverables:**
- Integration test exercising the full per-task subprocess loop with budget tracking across ≥5 tasks, verifying all tasks launched, results aggregated, and budget accounting correct

**Steps:**
1. **[PLANNING]** Design test scenario: 5+ tasks with varied outcomes (pass, fail, incomplete) and budget consumption
2. **[PLANNING]** Identify mock boundaries: mock subprocess execution while testing real orchestration and budget logic
3. **[EXECUTION]** Implement test fixture: 5-task inventory with dependencies
4. **[EXECUTION]** Implement integration test: run full loop, assert all tasks launched, results collected, budget correct
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k integration_subprocess -v`
6. **[COMPLETION]** Record test output in D-0012/evidence.md

**Acceptance Criteria:**
- Integration test exercises ≥5 tasks through the full per-task subprocess loop
- All tasks launched (subprocess count == task count), results aggregated into PhaseResult
- Budget accounting correct: sum of per-task debits == total consumed in TurnLedger
- `uv run pytest tests/sprint/ -k integration_subprocess` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k integration_subprocess -v`
- Evidence: test output artifact at D-0012/evidence.md

**Dependencies:** T02.02 (orchestration loop), T02.04 (result aggregation)
**Rollback:** Remove integration test

---

### T03.03 -- Implement Backward Compatibility Test (grace_period=0)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Backward compatibility ensures existing users are not affected by the architectural change — grace_period=0 must produce behavior identical to v1.2.1 with zero daemon threads. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking (backward compatibility), rollback |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0013/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0013/evidence.md

**Deliverables:**
- Backward compatibility test verifying grace_period=0 produces identical results to v1.2.1 behavior, with zero daemon threads spawned

**Steps:**
1. **[PLANNING]** Capture v1.2.1 baseline behavior: expected output format, thread count, timing characteristics
2. **[PLANNING]** Identify behavioral equivalence criteria: same output, same status codes, no additional threads
3. **[EXECUTION]** Implement test: run sprint with grace_period=0 and compare output to v1.2.1 baseline
4. **[EXECUTION]** Assert `threading.active_count()` unchanged from baseline (zero daemon threads from gate system)
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k backward_compat -v`
6. **[COMPLETION]** Record comparison results in D-0013/evidence.md

**Acceptance Criteria:**
- Sprint with grace_period=0 produces results matching v1.2.1 baseline output format
- `threading.active_count()` shows zero additional daemon threads beyond v1.2.1 baseline
- All existing sprint tests pass without modification under grace_period=0 configuration
- `uv run pytest tests/sprint/ -k backward_compat` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k backward_compat -v`
- Evidence: comparison artifact at D-0013/evidence.md

**Dependencies:** T02.05 (GateMode + grace_period), T02.02 (per-task subprocess)
**Rollback:** Remove backward compatibility test

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm foundation (M1) and subprocess (M2) validation passes before building context injection and trailing gate infrastructure.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P03-END.md

**Verification:**
- TurnLedger unit tests achieve 100% branch coverage with all edge cases passing
- Per-task subprocess integration test exercises ≥5 tasks with correct budget accounting
- Backward compatibility test confirms grace_period=0 equivalence to v1.2.1

**Exit Criteria:**
- `uv run pytest tests/sprint/ -v` exits 0 with all validation tests passing
- All 3 deliverables (D-0011 through D-0013) have evidence artifacts
- Success criteria SC-001 (no silent incompletion) and SC-002 (per-task budget allocation) validated
