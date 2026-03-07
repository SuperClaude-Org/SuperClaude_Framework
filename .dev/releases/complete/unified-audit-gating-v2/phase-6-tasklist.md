# Phase 6 -- Validation: End-to-End

Run the complete test suite, verify backward compatibility, and confirm the 46-task sprint sustainability claim before release. This is the final validation gate.

---

### T06.01 -- Run full test suite and confirm zero failures

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | Final gate: all existing tests plus 6 new tests must pass to confirm release readiness |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0030/evidence.md`

**Deliverables:**
- Full test suite execution report with zero failures (existing + 6 new tests)

**Steps:**
1. **[PLANNING]** Confirm all Phase 1-5 deliverables are complete before running final validation
2. **[EXECUTION]** Run `uv run pytest tests/ -v --tb=short` to execute the complete test suite
3. **[EXECUTION]** Capture test count, pass count, and failure count
4. **[VERIFICATION]** Confirm zero failures and zero errors in output
5. **[VERIFICATION]** Verify new tests appear in output: `test_budget_decay_rate_08`, `test_max_sustainable_tasks_at_08`, `test_46_task_sprint_sustainability`, `test_budget_exhaustion_property`, `test_explicit_max_turns_override`, `test_rate_boundary_validation`
6. **[COMPLETION]** Record full pytest output in D-0030 artifact

**Acceptance Criteria:**
- `uv run pytest tests/ -v` exits 0 with zero failures and zero errors
- All 6 new tests appear in the test run output and pass
- All 4 updated assertions pass with new expected values (100, 100, 100, 0.8)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0030/evidence.md`

**Validation:**
- `uv run pytest tests/ -v --tb=short` exits 0
- Evidence: complete pytest output captured in evidence artifact

**Dependencies:** T04.01-T04.10 (all test updates), T05.01-T05.04 (documentation complete)
**Rollback:** N/A (validation-only task)

---

### T06.02 -- Confirm 46-task sprint integration test passes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | SC-004 validation: the specific 46-task sprint sustainability claim must be independently confirmed with budget > 0 |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0031/evidence.md`

**Deliverables:**
- Confirmation that `test_46_task_sprint_sustainability` passes with budget remaining > 0

**Steps:**
1. **[PLANNING]** Identify the specific test to run: `tests/sprint/test_models.py::test_46_task_sprint_sustainability`
2. **[EXECUTION]** Run `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` as an isolated execution
3. **[VERIFICATION]** Confirm test passes with assertion `available() > 0` after 46 tasks
4. **[COMPLETION]** Record pytest output in D-0031 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` exits 0
- Test output confirms budget remaining > 0 after 46 tasks (SC-004)
- Test ran in isolation (not dependent on test ordering)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0031/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T06.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### T06.03 -- Confirm explicit override regression test passes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | SC-005 validation: explicit `--max-turns=50` must preserve v1.2.1 behavior |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0032/evidence.md`

**Deliverables:**
- Confirmation that `test_explicit_max_turns_override` passes with `max_turns == 50` when explicitly set

**Steps:**
1. **[PLANNING]** Identify the specific test: `tests/sprint/test_config.py::test_explicit_max_turns_override`
2. **[EXECUTION]** Run `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` as an isolated execution
3. **[VERIFICATION]** Confirm test passes: explicit `--max-turns=50` overrides new default of 100
4. **[COMPLETION]** Record pytest output in D-0032 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` exits 0
- Test verifies `max_turns == 50` when explicitly set (backward compatibility per SC-005)
- Test ran in isolation
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0032/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T06.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### T06.04 -- Confirm Tier 3 no-change tests still pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | Regression check: tests with explicit `max_turns=50` fixtures (Tier 3) must continue passing — they test intentional behavior, not defaults |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0033/evidence.md`

**Deliverables:**
- Confirmation that Tier 3 no-change tests pass: `test_e2e_trailing.py`, `test_process.py` (sprint + pipeline), `test_full_flow.py`

**Steps:**
1. **[PLANNING]** Identify Tier 3 test files from spec §6.4: `tests/sprint/test_e2e_trailing.py`, `tests/sprint/test_process.py`, `tests/pipeline/test_process.py`, `tests/pipeline/test_full_flow.py`
2. **[EXECUTION]** Run `uv run pytest tests/sprint/test_e2e_trailing.py tests/sprint/test_process.py tests/pipeline/test_process.py tests/pipeline/test_full_flow.py -v`
3. **[VERIFICATION]** Confirm all Tier 3 tests pass with zero failures — these use explicit fixtures and should be unaffected by default changes
4. **[COMPLETION]** Record pytest output in D-0033 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_e2e_trailing.py tests/sprint/test_process.py tests/pipeline/test_process.py tests/pipeline/test_full_flow.py -v` exits 0
- Tests with explicit `max_turns=50` fixtures pass (fixture value is intentional, not default-dependent)
- Tests with derived `ledger.reimbursement_rate` computations pass (auto-adjust to new default)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0033/evidence.md`

**Validation:**
- `uv run pytest <tier-3-test-files> -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T06.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### Checkpoint: End of Phase 6

**Purpose:** Final release gate — all success criteria (SC-001 through SC-007) verified; release is ready.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P06-END.md`

**Verification:**
- D-0030 full test suite report shows zero failures
- D-0031 confirms 46-task sprint sustainability (SC-004)
- D-0032 confirms explicit override backward compatibility (SC-005)
- D-0033 confirms Tier 3 no-change tests pass (no regressions)

**Exit Criteria:**
- All 7 success criteria verified: SC-001 (12 edits), SC-002 (4 assertions), SC-003 (6 new tests), SC-004 (46-task sprint), SC-005 (explicit override), SC-006 (CHANGELOG), SC-007 (spec prose)
- All 33 deliverables (D-0001 through D-0033) have evidence artifacts
- Release is ready for final review and merge
