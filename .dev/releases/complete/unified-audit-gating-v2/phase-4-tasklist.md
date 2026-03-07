# Phase 4 -- Test Suite Updates

Update 4 existing test assertions to match the new default values and add 6 new tests covering budget decay, sprint sustainability, boundary conditions, and backward compatibility at the new defaults.

---

### T04.01 -- Update test_models.py:54 assertion to == 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | Test assertion `== 50` no longer matches `PipelineConfig.max_turns` default of 100 |
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
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0016/evidence.md`

**Deliverables:**
- Updated assertion at `tests/pipeline/test_models.py:54` from `== 50` to `== 100`

**Steps:**
1. **[PLANNING]** Read `tests/pipeline/test_models.py` and locate line 54 containing `assert cfg.max_turns == 50`
2. **[PLANNING]** Confirm this tests the default `PipelineConfig` max_turns (not an explicit fixture)
3. **[EXECUTION]** Edit `tests/pipeline/test_models.py:54` to read `assert cfg.max_turns == 100`
4. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_models.py -k "max_turns" -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0016 artifact

**Acceptance Criteria:**
- `uv run pytest tests/pipeline/test_models.py -v` exits 0 with the updated assertion passing
- Only the single assertion value was changed (50 → 100), not the test structure
- Tier 3 explicit fixtures (`max_turns=50` in test parameters) remain unchanged
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0016/evidence.md`

**Validation:**
- `uv run pytest tests/pipeline/test_models.py -k "max_turns" -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T03.03 (V1 validation must pass before modifying tests)
**Rollback:** Revert line 54 to `assert cfg.max_turns == 50`

---

### T04.02 -- Update test_models.py:188 assertion to == 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Test assertion `== 50` no longer matches `SprintConfig.max_turns` default of 100 |
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
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0017/evidence.md`

**Deliverables:**
- Updated assertion at `tests/sprint/test_models.py:188` from `== 50` to `== 100`

**Steps:**
1. **[PLANNING]** Read `tests/sprint/test_models.py` and locate line 188 containing `assert cfg.max_turns == 50`
2. **[PLANNING]** Confirm this tests the default `SprintConfig` max_turns (not an explicit fixture)
3. **[EXECUTION]** Edit `tests/sprint/test_models.py:188` to read `assert cfg.max_turns == 100`
4. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py -k "max_turns" -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0017 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_sprint_config_defaults -v` exits 0
- Only the single assertion value was changed (50 → 100)
- Other `max_turns` assertions in the same file (e.g., Tier 3 explicit fixtures) remain unchanged
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0017/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py -k "max_turns" -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T03.03 (V1 validation must pass)
**Rollback:** Revert line 188 to `assert cfg.max_turns == 50`

---

### T04.03 -- Update test_config.py:215 assertion to == 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Test assertion `== 50` no longer matches `load_sprint_config` default of 100 |
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
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0018/evidence.md`

**Deliverables:**
- Updated assertion at `tests/sprint/test_config.py:215` from `== 50` to `== 100`

**Steps:**
1. **[PLANNING]** Read `tests/sprint/test_config.py` and locate line 215 containing `assert config.max_turns == 50`
2. **[PLANNING]** Confirm this tests the default `load_sprint_config` return value
3. **[EXECUTION]** Edit `tests/sprint/test_config.py:215` to read `assert config.max_turns == 100`
4. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_config.py -k "max_turns" -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0018 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_config.py -v` exits 0 with the updated assertion passing
- Only the single assertion value was changed (50 → 100)
- No other assertions in `test_config.py` were modified
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0018/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_config.py -k "max_turns" -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T03.03 (V1 validation must pass)
**Rollback:** Revert line 215 to `assert config.max_turns == 50`

---

### T04.04 -- Update test_models.py:527 assertion to == 0.8

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Test assertion `== 0.5` no longer matches `TurnLedger.reimbursement_rate` default of 0.8 |
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
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0019/evidence.md`

**Deliverables:**
- Updated assertion at `tests/sprint/test_models.py:527` from `== 0.5` to `== 0.8`

**Steps:**
1. **[PLANNING]** Read `tests/sprint/test_models.py` and locate line 527 containing `assert ledger.reimbursement_rate == 0.5`
2. **[PLANNING]** Confirm this tests the default `TurnLedger` rate (not an explicit fixture)
3. **[EXECUTION]** Edit `tests/sprint/test_models.py:527` to read `assert ledger.reimbursement_rate == 0.8`
4. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py -k "reimbursement" -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0019 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py -k "reimbursement" -v` exits 0
- Only the single assertion value was changed (0.5 → 0.8)
- Explicit fixtures using `reimbursement_rate=0.5` (Tier 3) remain unchanged
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0019/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py -k "reimbursement" -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T03.03 (V1 validation must pass)
**Rollback:** Revert line 527 to `assert ledger.reimbursement_rate == 0.5`

---

### T04.05 -- Add test_budget_decay_rate_08 unit test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Verifies the core budget decay math at rate=0.8: net cost per passing task = 4 turns (spec §4.1) |
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
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0020/evidence.md`

**Deliverables:**
- New unit test `test_budget_decay_rate_08` added to `tests/sprint/test_models.py`

**Steps:**
1. **[PLANNING]** Read `tests/sprint/test_models.py` to identify the appropriate location for new TurnLedger tests
2. **[PLANNING]** Review `TurnLedger` API: constructor signature, `debit()`, `credit()`, `available()` methods
3. **[EXECUTION]** Add `test_budget_decay_rate_08` test: create `TurnLedger(initial_budget=200, reimbursement_rate=0.8)`, call `debit(8)` then `credit(8)`, assert `reimbursed == 6` (floor(8*0.8)=6) and net cost = 4
4. **[EXECUTION]** Verify assertions match spec §4.1: `credit = floor(actual_turns * rate) = floor(8 * 0.80) = 6`, `net_cost = 8 - 6 + 2 = 4`
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py::test_budget_decay_rate_08 -v` and confirm test passes
6. **[COMPLETION]** Record test output in D-0020 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_budget_decay_rate_08 -v` exits 0
- Test verifies: `floor(8 * 0.8) = 6` reimbursed turns, net cost = 4 per task
- Test uses `TurnLedger` API directly (no mocking of core budget logic)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0020/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_budget_decay_rate_08 -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.01-T04.04 (assertion updates complete; existing tests passing)
**Rollback:** Remove the added test function

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Mid-phase checkpoint — verify 4 assertion updates and first new test are passing before adding remaining 5 new tests.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P04-T01-T05.md`

**Verification:**
- All 4 updated assertions (D-0016 through D-0019) pass: `uv run pytest tests/pipeline/test_models.py tests/sprint/test_models.py tests/sprint/test_config.py -v`
- New test `test_budget_decay_rate_08` (D-0020) passes
- No regressions in existing test suite

**Exit Criteria:**
- All 5 tasks (T04.01-T04.05) have evidence artifacts
- `uv run pytest tests/ -v` shows no failures
- Ready to proceed with remaining 5 new tests

---

### T04.06 -- Add test_max_sustainable_tasks_at_08 unit test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | Verifies sustainability boundary: budget=200 at rate=0.8 sustains ~50 tasks before exhaustion (spec §4.2) |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0021/evidence.md`

**Deliverables:**
- New unit test `test_max_sustainable_tasks_at_08` added to `tests/sprint/test_models.py`

**Steps:**
1. **[PLANNING]** Review TurnLedger budget depletion loop pattern from spec §4.2 (net cost 4/task, 200/4=50 max)
2. **[EXECUTION]** Add `test_max_sustainable_tasks_at_08` test: loop debit(8)+credit(8)+debit(2 overhead) until `available() < minimum_allocation`, assert loop count is approximately 50
3. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py::test_max_sustainable_tasks_at_08 -v` and confirm test passes
4. **[COMPLETION]** Record test output in D-0021 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_max_sustainable_tasks_at_08 -v` exits 0
- Test verifies exhaustion occurs at approximately task 50 (budget=200, rate=0.8, net_cost=4/task)
- Test uses deterministic loop with explicit task counting
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0021/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_max_sustainable_tasks_at_08 -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.05 (build on budget decay test)
**Rollback:** Remove the added test function

---

### T04.07 -- Add test_46_task_sprint_sustainability integration test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Validates NFR-003: a 46-task sprint at rate=0.8, budget=200 completes without exhaustion (spec §4.2: 16-turn margin) |
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
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0022/evidence.md`

**Deliverables:**
- New integration test `test_46_task_sprint_sustainability` added to `tests/sprint/test_models.py`

**Steps:**
1. **[PLANNING]** Review NFR-003 acceptance: 46-task sprint, avg 8 turns/task, 2 overhead, rate=0.8, budget=200 → all complete, budget > 0
2. **[EXECUTION]** Add `test_46_task_sprint_sustainability` test: create `TurnLedger(initial_budget=200, reimbursement_rate=0.8)`, loop 46 times with debit(8)+credit(8)+debit(2), assert `available() > 0` after all 46 iterations
3. **[EXECUTION]** Assert final budget equals 16 (200 - 46*4 = 200 - 184 = 16)
4. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0022 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` exits 0
- Test verifies: after 46 tasks, `available() > 0` (specifically expects ~16 remaining)
- Test simulates realistic sprint pattern (debit + credit + overhead per task)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0022/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_46_task_sprint_sustainability -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.05 (build on budget decay test)
**Rollback:** Remove the added test function
**Notes:** This is the key NFR-003 validation test. P1 priority per Crispin (Round 3).

---

### T04.08 -- Add test_budget_exhaustion_property property-based test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | Validates NFR-008: for any rate < 1.0, budget monotonically decays and always reaches 0 in finite steps |
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
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0023/evidence.md`

**Deliverables:**
- New property-based test `test_budget_exhaustion_property` added to `tests/sprint/test_models.py`

**Steps:**
1. **[PLANNING]** Review NFR-008 requirement: monotonic decay guarantee for any rate < 1.0
2. **[EXECUTION]** Add `test_budget_exhaustion_property` test using hypothesis or deterministic seed: for random task counts (1-100) with random turns (1-50) at rate=0.8, verify budget always reaches 0
3. **[EXECUTION]** Use deterministic seed per roadmap risk mitigation (R-005: "Use deterministic seed; bound hypothesis space")
4. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py::test_budget_exhaustion_property -v` and confirm test passes
5. **[COMPLETION]** Record test output in D-0023 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_budget_exhaustion_property -v` exits 0
- Test uses deterministic seed for reproducibility (no flakiness)
- Test verifies budget monotonic decay property for varied inputs
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0023/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_budget_exhaustion_property -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.05 (build on budget decay test)
**Rollback:** Remove the added test function
**Notes:** P2 priority per Crispin. Use deterministic seed per roadmap risk R-005.

---

### T04.09 -- Add test_explicit_max_turns_override regression test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | Validates NFR-006 and SC-004: explicit `--max-turns=50` overrides the new default of 100 |
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
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0024/evidence.md`

**Deliverables:**
- New regression test `test_explicit_max_turns_override` added to `tests/sprint/test_config.py`

**Steps:**
1. **[PLANNING]** Review NFR-006 and SC-004: explicit CLI overrides must take precedence over defaults
2. **[EXECUTION]** Add `test_explicit_max_turns_override` test to `tests/sprint/test_config.py`: invoke `load_sprint_config(max_turns=50)` and assert `config.max_turns == 50` (not 100)
3. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` and confirm test passes
4. **[COMPLETION]** Record test output in D-0024 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` exits 0
- Test verifies: `load_sprint_config(max_turns=50)` returns config with `max_turns == 50`
- Test demonstrates backward compatibility (SC-004 enforcement)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0024/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_config.py::test_explicit_max_turns_override -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.03 (test_config.py assertion update complete)
**Rollback:** Remove the added test function
**Notes:** P1 priority per Crispin. Validates backward compatibility guarantee.

---

### T04.10 -- Add test_rate_boundary_validation boundary test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | Validates SC-001 enforcement: rate=0.0 (valid edge), rate=0.99 (valid edge), rate=1.0 (rejected), rate=-0.1 (rejected) |
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
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0025/evidence.md`

**Deliverables:**
- New boundary test `test_rate_boundary_validation` added to `tests/sprint/test_models.py`

**Steps:**
1. **[PLANNING]** Review SC-001: `reimbursement_rate` MUST be in range `(0.0, 1.0)` exclusive. Review Whittaker adversarial attacks (Round 2) for boundary cases.
2. **[EXECUTION]** Add `test_rate_boundary_validation` test with four sub-cases:
   - rate=0.0 → accepted (zero reimbursement, valid per SC-001 exclusive lower bound — or rejected depending on SC-001 interpretation)
   - rate=0.99 → accepted (high reimbursement, valid)
   - rate=1.0 → rejected (SC-001 exclusive upper bound; Whittaker Attack 2)
   - rate=-0.1 → rejected (negative rate invalid)
3. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py::test_rate_boundary_validation -v` and confirm test passes
4. **[COMPLETION]** Record test output in D-0025 artifact

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py::test_rate_boundary_validation -v` exits 0
- Test covers all 4 boundary cases specified in roadmap D3.10
- Test validates SC-001 enforcement (rate < 1.0 strictly; Whittaker Attack 2 mitigation)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0025/evidence.md`

**Validation:**
- `uv run pytest tests/sprint/test_models.py::test_rate_boundary_validation -v` exits 0
- Evidence: pytest output captured in evidence artifact

**Dependencies:** T04.04 (reimbursement_rate assertion update complete)
**Rollback:** Remove the added test function
**Notes:** Addresses Whittaker adversarial findings (Round 2). RISK-009 mitigation: verify SC-001 enforcement.

---

### Checkpoint: End of Phase 4

**Purpose:** Gate for Phase 5 — confirm all 4 assertion updates and all 6 new tests pass before documentation begins.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P04-END.md`

**Verification:**
- All 10 deliverables (D-0016 through D-0025) have evidence artifacts
- `uv run pytest tests/pipeline/ tests/sprint/ -v` exits 0 with zero failures
- No regressions in Tier 3 (no-change) tests

**Exit Criteria:**
- All 4 assertion updates passing (SC-002)
- All 6 new tests passing (SC-003)
- Full existing test suite still passing
