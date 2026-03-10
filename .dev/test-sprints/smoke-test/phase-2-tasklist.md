# Phase 2 -- Validation: End-to-End Test Execution

Run the complete test suite, verify backward compatibility, and confirm the 46-task sprint sustainability claim. This is a read-only validation phase that runs real pytest commands.

---

### T02.01 -- Run full test suite and confirm zero failures

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | Final gate: all existing tests plus new tests must pass to confirm release integrity |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0030/evidence.md`

**Deliverables:**
- Full test suite execution report with zero failures

**Steps:**
1. **[PLANNING]** Confirm Phase 1 validation deliverables are complete
2. **[EXECUTION]** Run `uv run pytest tests/sprint/test_models.py tests/sprint/test_config.py tests/pipeline/test_models.py tests/pipeline/test_full_flow.py tests/sprint/test_property_based.py tests/sprint/test_backward_compat_regression.py -v --tb=short`
3. **[EXECUTION]** Capture test count, pass count, and failure count
4. **[VERIFICATION]** Confirm zero failures and zero errors in output
5. **[COMPLETION]** Record full pytest output in D-0030 artifact

**Acceptance Criteria:**
- pytest exits 0 with zero failures and zero errors
- All key tests appear in output and pass
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0030/evidence.md`

**Validation:**
- pytest exits 0
- Evidence: complete pytest output captured in evidence artifact

**Dependencies:** T03.01-T03.03 (Phase 1 validation)
**Rollback:** N/A (validation-only task)

---

### T02.02 -- Confirm 46-task sprint integration test passes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | The specific 46-task sprint sustainability claim must be independently confirmed with budget > 0 |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0031/evidence.md`

**Deliverables:**
- Confirmation that `test_46_task_sprint_sustainability` passes with budget remaining > 0

**Steps:**
1. **[EXECUTION]** Run `uv run pytest tests/sprint/test_models.py -k test_46_task_sprint_sustainability -v`
2. **[VERIFICATION]** Confirm test passes with assertion `available() > 0` after 46 tasks
3. **[COMPLETION]** Record pytest output in D-0031 artifact

**Acceptance Criteria:**
- pytest exits 0 for test_46_task_sprint_sustainability
- Test output confirms budget remaining > 0 after 46 tasks
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0031/evidence.md`

**Validation:**
- pytest exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T02.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### T02.03 -- Confirm explicit override regression test passes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | Explicit `--max-turns=50` must preserve backward-compatible behavior |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0032/evidence.md`

**Deliverables:**
- Confirmation that `test_explicit_max_turns_override` passes

**Steps:**
1. **[EXECUTION]** Run `uv run pytest tests/sprint/test_config.py -k test_explicit_max_turns_override -v`
2. **[VERIFICATION]** Confirm test passes: explicit `--max-turns=50` overrides new default of 100
3. **[COMPLETION]** Record pytest output in D-0032 artifact

**Acceptance Criteria:**
- pytest exits 0 for test_explicit_max_turns_override
- Test verifies `max_turns == 50` when explicitly set (backward compatibility)
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0032/evidence.md`

**Validation:**
- pytest exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T02.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### T02.04 -- Confirm Tier 3 no-change tests still pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | Regression check: tests with explicit fixtures must continue passing |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████████] 60%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0033/evidence.md`

**Deliverables:**
- Confirmation that Tier 3 no-change tests pass

**Steps:**
1. **[EXECUTION]** Run `uv run pytest tests/sprint/test_e2e_trailing.py tests/sprint/test_process.py tests/pipeline/test_process.py tests/pipeline/test_full_flow.py -v --tb=short`
2. **[VERIFICATION]** Confirm all tests pass with zero failures
3. **[COMPLETION]** Record pytest output in D-0033 artifact

**Acceptance Criteria:**
- pytest exits 0 for all Tier 3 test files
- Tests with explicit fixtures pass (not default-dependent)
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0033/evidence.md`

**Validation:**
- pytest exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T02.01 (full suite should pass first)
**Rollback:** N/A (validation-only task)

---

### Checkpoint: End of Phase 2

**Purpose:** Final gate — all tests pass, backward compatibility confirmed, sprint sustainability verified.
**Checkpoint Report Path:** `.dev/test-sprints/smoke-test/checkpoints/CP-P02-END.md`

**Verification:**
- D-0030 full test suite report shows zero failures
- D-0031 confirms 46-task sprint sustainability
- D-0032 confirms explicit override backward compatibility
- D-0033 confirms Tier 3 no-change tests pass

**Exit Criteria:**
- All 4 validation deliverables have evidence artifacts
- Zero test failures across all test files
