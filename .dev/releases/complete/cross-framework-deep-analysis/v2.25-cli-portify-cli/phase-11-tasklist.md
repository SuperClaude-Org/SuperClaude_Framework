# Phase 11 -- Verification and Release

Prove the implementation satisfies all 14 explicit success criteria and recoverability expectations. Unit tests, integration tests, edge case tests, sample runs, and release readiness validation.

### T11.01 -- Implement Unit Tests for Validation Errors, Gates, Status, TurnLedger, and Exit Codes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-122 |
| Why | All 5 validation error paths, all 12 gates with passing and failing inputs, _determine_status() exhaustively, TurnLedger budget tracking, exit code mapping, and timeout classification must be unit tested. |
| Effort | XL |
| Risk | Medium |
| Risk Drivers | system-wide, end-to-end |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0061 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0061/spec.md

**Deliverables:**
- Unit test suite covering: all 5 validation error paths (NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED), all 12 gates with passing and failing inputs, `_determine_status()` exhaustive paths, `TurnLedger` budget tracking and exhaustion, exit code mapping, timeout classification (exit 124 → TIMEOUT)

**Steps:**
1. **[PLANNING]** Enumerate all unit test categories from roadmap Phase 10 requirements
2. **[PLANNING]** Map test cases to success criteria: SC-001, SC-002, SC-011, SC-014
3. **[EXECUTION]** Write unit tests for all 5 validation error paths
4. **[EXECUTION]** Write unit tests for all 12 gates with passing and failing synthetic inputs
5. **[EXECUTION]** Write unit tests for _determine_status() covering PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, TIMEOUT, ERROR
6. **[EXECUTION]** Write unit tests for TurnLedger: budget tracking, can_launch(), exhaustion → HALTED
7. **[EXECUTION]** Write unit tests for exit code mapping and timeout classification (exit 124 → TIMEOUT, SC-014)
8. **[VERIFICATION]** Run `uv run pytest tests/` and verify all unit tests pass
9. **[COMPLETION]** Document test coverage in D-0061/spec.md

**Acceptance Criteria:**
- All 5 validation error paths tested with correct error codes raised
- All 12 gates tested with both passing and failing synthetic inputs
- `_determine_status()` tested exhaustively: PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, TIMEOUT (SC-014), ERROR
- TurnLedger budget tracking and exhaustion tested: `can_launch()` returns false at exhaustion, HALTED outcome set
- Exit code mapping tested: each PortifyOutcome maps to correct CLI exit code (SC-013)
- `uv run pytest tests/ -k "test_unit"` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/ -k "test_unit" --tb=short` exits 0
- Evidence: linkable artifact produced at D-0061/spec.md

**Dependencies:** All Phase 1-10 implementation tasks
**Rollback:** TBD (if not specified in roadmap)
**Notes:** XL effort — covers validation errors, 12 gates, status classification, TurnLedger, exit codes, timeout classification.

---

### T11.02 -- Implement Integration Tests for Dry-Run, Resume, Signal Handling, and Gate Retry

| Field | Value |
|---|---|
| Roadmap Item IDs | R-123 |
| Why | Integration tests required: dry-run against real skill directory, resume flow across both review boundaries, signal handling (SIGINT → INTERRUPTED + contract), gate failure + retry (missing EXIT_RECOMMENDATION → retry triggers). |
| Effort | XL |
| Risk | High |
| Risk Drivers | end-to-end, system-wide |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0062 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0062/spec.md

**Deliverables:**
- Integration test suite: dry-run against real skill directory (SC-012), resume flow across Phase 1 and Phase 2 review boundaries (SC-007), signal handling SIGINT → INTERRUPTED + return contract (SC-011), gate failure + retry with missing EXIT_RECOMMENDATION

**Steps:**
1. **[PLANNING]** Identify test skill directory for dry-run integration test
2. **[PLANNING]** Map integration test scenarios to success criteria: SC-007, SC-011, SC-012
3. **[EXECUTION]** Write integration test: dry-run against real skill directory, assert no SYNTHESIS/CONVERGENCE artifacts
4. **[EXECUTION]** Write integration test: resume flow across Phase 1 review boundary (phase1-approval.yaml)
5. **[EXECUTION]** Write integration test: resume flow across Phase 2 review boundary (phase2-approval.yaml)
6. **[EXECUTION]** Write integration test: SIGINT handling → INTERRUPTED outcome + return-contract.yaml emitted
7. **[EXECUTION]** Write integration test: gate failure (missing EXIT_RECOMMENDATION) → retry triggers
8. **[VERIFICATION]** Run `uv run pytest tests/ -k "test_integration"` and verify all pass
9. **[COMPLETION]** Document integration test coverage in D-0062/spec.md

**Acceptance Criteria:**
- Dry-run integration test runs against real skill directory producing no SYNTHESIS/CONVERGENCE artifacts (SC-012)
- Resume integration tests verify skip of completed steps across both review boundaries (SC-007)
- Signal handling test verifies SIGINT → INTERRUPTED + return-contract.yaml emitted (SC-011)
- Gate retry integration test verifies missing EXIT_RECOMMENDATION triggers retry mechanism (PASS_NO_SIGNAL status → retry)
- `uv run pytest tests/ -k "test_integration"` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/ -k "test_integration" --tb=short` exits 0
- Evidence: linkable artifact produced at D-0062/spec.md

**Dependencies:** T11.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** XL effort — 5 integration test scenarios with subprocess coordination, file system state, and signal handling.

---

### T11.03 -- Implement Edge Case Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-124 |
| Why | Edge cases must be tested: ambiguous skill name, name collision with non-portified module, budget exhaustion mid-pipeline, convergence ESCALATED path, template >50KB. |
| Effort | L |
| Risk | High |
| Risk Drivers | end-to-end, breaking (edge cases) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0063 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0063/spec.md

**Deliverables:**
- Edge case test suite: ambiguous skill name (AMBIGUOUS_PATH), name collision with non-portified module (NAME_COLLISION), budget exhaustion mid-pipeline (HALTED), convergence ESCALATED path, template >50KB (--file argument)

**Steps:**
1. **[PLANNING]** Enumerate edge case scenarios from roadmap Phase 10
2. **[PLANNING]** Map edge cases to error codes and outcome paths
3. **[EXECUTION]** Write test: ambiguous skill name → AMBIGUOUS_PATH error with candidate list
4. **[EXECUTION]** Write test: name collision with non-portified module → NAME_COLLISION error
5. **[EXECUTION]** Write test: budget exhaustion mid-pipeline → HALTED outcome + return-contract.yaml
6. **[EXECUTION]** Write test: convergence ESCALATED path → status: partial + panel-report.md
7. **[EXECUTION]** Write test: template >50KB → --file argument used for Claude subprocess
8. **[VERIFICATION]** Run `uv run pytest tests/ -k "test_edge_case"` and verify all pass
9. **[COMPLETION]** Document edge case coverage in D-0063/spec.md

**Acceptance Criteria:**
- Ambiguous skill name test verifies AMBIGUOUS_PATH error with candidate list in message
- Name collision test verifies NAME_COLLISION when existing module lacks portification markers
- Budget exhaustion test verifies HALTED outcome with return-contract.yaml emitted
- Convergence ESCALATED test verifies status: partial with panel-report.md and downstream_ready=false
- Template >50KB test verifies --file argument passed to Claude subprocess
- `uv run pytest tests/ -k "test_edge_case"` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/ -k "test_edge_case" --tb=short` exits 0
- Evidence: linkable artifact produced at D-0063/spec.md

**Dependencies:** T11.01
**Rollback:** TBD (if not specified in roadmap)

---

### T11.04 -- Run Project Validation via uv run pytest

| Field | Value |
|---|---|
| Roadmap Item IDs | R-125 |
| Why | Full project test suite must pass using UV-only commands to validate no regressions. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0064 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0064/evidence.md

**Deliverables:**
- Full project validation run via `uv run pytest` with pass/fail results documented

**Steps:**
1. **[PLANNING]** Confirm test command: `uv run pytest` (UV-only, no python -m)
2. **[PLANNING]** Identify any test fixtures or configuration needed
3. **[EXECUTION]** Run `uv run pytest` against full project test suite
4. **[EXECUTION]** Capture and document results: total tests, passed, failed, errors
5. **[VERIFICATION]** Verify zero failures and zero errors in full suite
6. **[COMPLETION]** Document validation results in D-0064/evidence.md

**Acceptance Criteria:**
- `uv run pytest` exits 0 with all tests passing (zero failures, zero errors)
- No regressions in existing project tests
- All cli-portify tests integrated into project test suite
- Validation results documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0064/evidence.md

**Validation:**
- `uv run pytest --tb=short` exits 0
- Evidence: linkable artifact produced at D-0064/evidence.md

**Dependencies:** T11.01, T11.02, T11.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 11 / Tasks T11.01-T11.04

**Purpose:** Verify all test categories pass: unit tests, integration tests, edge case tests, and full project validation.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P11-T01-T04.md

**Verification:**
- All unit tests pass covering validation errors, gates, status, TurnLedger, exit codes
- All integration tests pass covering dry-run, resume, signal handling, gate retry
- Full project validation via `uv run pytest` passes with zero failures

**Exit Criteria:**
- All test categories pass with zero failures
- SC-011 (return contract on all paths), SC-012 (dry-run filtering), SC-014 (timeout classification) validated
- No regressions in existing project test suite

---

### T11.05 -- Validate All 14 Success Criteria (SC-001 through SC-014)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-126 |
| Why | All 14 success criteria must be validated with evidence mapping each criterion to its test or verification method. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | end-to-end, system-wide |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0065 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0065/spec.md

**Deliverables:**
- Validation report mapping each of SC-001 through SC-014 to its test result with pass/fail evidence

**Steps:**
1. **[PLANNING]** Map each SC to its validation method from roadmap SC-to-Phase Validation Matrix
2. **[PLANNING]** Collect test results from T11.01, T11.02, T11.03
3. **[EXECUTION]** Validate SC-001 (Step 0 ≤30s, valid config YAML) and SC-002 (Step 1 ≤60s, inventory ≥1)
4. **[EXECUTION]** Validate SC-003 through SC-008 (gates, review, resume, release spec)
5. **[EXECUTION]** Validate SC-009 through SC-014 (convergence, quality score, contract, dry-run, exit codes, timeout)
6. **[VERIFICATION]** Verify all 14 criteria have PASS status with evidence references
7. **[COMPLETION]** Write validation report to D-0065/spec.md

**Acceptance Criteria:**
- All 14 success criteria (SC-001 through SC-014) validated with PASS status
- Each criterion mapped to specific test or verification evidence
- Validation follows milestone-incremental approach: A (SC-001,002,011,014), B (SC-003-008), C (SC-009-013)
- Validation report at .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0065/spec.md

**Validation:**
- Manual check: all 14 SC entries show PASS with evidence references
- Evidence: linkable artifact produced at D-0065/spec.md

**Dependencies:** T11.04
**Rollback:** TBD (if not specified in roadmap)

---

### T11.06 -- Perform Sample Runs Across 5 Scenarios

| Field | Value |
|---|---|
| Roadmap Item IDs | R-127 |
| Why | Sample runs must validate real-world behavior across: valid workflow, ambiguous workflow, insufficient turn budget, interrupted execution, escalation case. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0066 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0066/evidence.md

**Deliverables:**
- Sample run results for 5 scenarios: valid workflow (success), ambiguous workflow (AMBIGUOUS_PATH), insufficient turn budget (HALTED), interrupted execution (INTERRUPTED), escalation case (ESCALATED)

**Steps:**
1. **[PLANNING]** Prepare test fixtures for each scenario
2. **[PLANNING]** Define expected outcomes per scenario
3. **[EXECUTION]** Run scenario 1: valid workflow → expected success outcome with all artifacts
4. **[EXECUTION]** Run scenario 2: ambiguous workflow → expected AMBIGUOUS_PATH error with candidates
5. **[EXECUTION]** Run scenario 3: insufficient budget → expected HALTED with resume command
6. **[EXECUTION]** Run scenario 4: interrupted → expected INTERRUPTED with return contract
7. **[EXECUTION]** Run scenario 5: escalation → expected ESCALATED with panel-report.md
8. **[VERIFICATION]** Verify each scenario produces expected outcome and artifacts
9. **[COMPLETION]** Document sample run results in D-0066/evidence.md

**Acceptance Criteria:**
- Valid workflow produces success outcome with all expected artifacts
- Ambiguous workflow produces AMBIGUOUS_PATH error with candidate list
- Insufficient budget produces HALTED outcome with resume command and suggested_resume_budget
- Interrupted execution produces INTERRUPTED outcome with return-contract.yaml emitted
- Escalation case produces ESCALATED status with panel-report.md and downstream_ready=false
- Sample run results documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0066/evidence.md

**Validation:**
- Manual check: all 5 scenarios produce expected outcomes verified by reviewer
- Evidence: linkable artifact produced at D-0066/evidence.md

**Dependencies:** T11.05
**Rollback:** TBD (if not specified in roadmap)

---

### T11.07 -- Produce Release Readiness Checklist

| Field | Value |
|---|---|
| Roadmap Item IDs | R-128, R-129, R-130, R-131 |
| Why | Final release readiness requires: acceptable logs/workdir behavior confirmed, test coverage documented, SC validation report complete, release checklist produced. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | LIGHT |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0067 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0067/spec.md

**Deliverables:**
- Release readiness checklist confirming: logs and workdir behavior acceptable, test coverage complete, SC-001-014 validation report finalized, implementation ready for merge

**Steps:**
1. **[PLANNING]** Collect all validation artifacts from T11.04, T11.05, T11.06
2. **[PLANNING]** Review logs and workdir behavior acceptability
3. **[EXECUTION]** Confirm logs are workdir-scoped and cleanup expectations documented
4. **[EXECUTION]** Compile release readiness checklist: test coverage, SC validation, sample runs, log behavior
5. **[VERIFICATION]** Quick sanity check: all checklist items have pass status
6. **[COMPLETION]** Write release readiness checklist to D-0067/spec.md

**Acceptance Criteria:**
- Release readiness checklist at D-0067/spec.md confirms all categories pass
- Logs confirmed as workdir-scoped with documented cleanup expectations
- All 14 success criteria validated with evidence
- Implementation declared ready for merge in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0067/spec.md

**Validation:**
- Manual check: release readiness checklist reviewed and all items pass
- Evidence: linkable artifact produced at D-0067/spec.md

**Dependencies:** T11.05, T11.06
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 11

**Purpose:** Verify all 14 success criteria validated by automated tests; implementation ready for merge.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P11-END.md

**Verification:**
- All 14 success criteria (SC-001 through SC-014) have PASS status with test evidence
- All 5 sample run scenarios produce expected outcomes
- Release readiness checklist confirms all categories pass

**Exit Criteria:**
- Milestone M10 satisfied: all 14 success criteria validated; implementation ready for merge
- All 7 tasks (T11.01-T11.07) completed with deliverables D-0061 through D-0067 produced
- Super-milestone C (Quality Loop and Release Readiness) complete: roadmap Phases 7-10 / tasklist Phases 8-11 done
