# Phase 5 -- Test Suite and Quality Gates

Prove lifecycle correctness, compatibility safety, and recovery behavior. Lock down guarantees for all Phase 8 requirements with 10 targeted tests across 3 test classes, then run the full validation suite.

---

### T05.01 -- Implement TestIsolationWiring Test Class

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | Isolation lifecycle is the primary system objective; dedicated tests lock down directory creation, single-file copy, cleanup on success/failure, and orphan removal. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0017/evidence.md

**Deliverables:**
- D-0017: `TestIsolationWiring` class in `tests/sprint/test_phase8_halt_fix.py` with 4 tests:
  - T04.01: Isolation directory created before subprocess launch; contains exactly one file
  - T04.02: Isolation directory removed after successful phase
  - T04.03: Isolation directory removed after failed phase (finally block)
  - T04.04: Startup orphan cleanup removes stale `.isolation/` tree

**Steps:**
1. **[PLANNING]** Review implementation from Phases 1-2 to understand isolation directory lifecycle
2. **[PLANNING]** Design test fixtures for mocking subprocess launch and SprintConfig
3. **[EXECUTION]** Create `tests/sprint/test_phase8_halt_fix.py` with `TestIsolationWiring` class
4. **[EXECUTION]** Implement T04.01: assert isolation dir exists and contains exactly one file before subprocess launch
5. **[EXECUTION]** Implement T04.02: assert isolation dir does not exist after successful phase completion
6. **[EXECUTION]** Implement T04.03: assert isolation dir does not exist after failed phase (finally block guarantees)
7. **[EXECUTION]** Implement T04.04: assert startup orphan cleanup removes pre-existing `.isolation/` tree
8. **[VERIFICATION]** `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestIsolationWiring -v` exits 0 with 4 tests passing
9. **[COMPLETION]** Record test results in evidence

**Acceptance Criteria:**
- `tests/sprint/test_phase8_halt_fix.py` exists with `TestIsolationWiring` class containing 4 test methods
- `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestIsolationWiring -v` exits 0 with 4 passed
- Tests verify isolation directory lifecycle: creation **before subprocess launch**, single-file content, success cleanup, failure cleanup, orphan cleanup
- Test fixtures properly mock subprocess launch boundary

**Validation:**
- Manual check: `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestIsolationWiring -v` exits 0 with 4 passed
- Evidence: TASKLIST_ROOT/artifacts/D-0017/evidence.md produced

**Dependencies:** T02.01, T02.02, T02.03, T02.04
**Rollback:** Remove test file
**Notes:** FR-016/FR-017/FR-018/FR-019 implementation. Test names T04.01-T04.04 are roadmap test IDs, not tasklist task IDs.

---

### T05.02 -- Implement TestPromptAndContext Test Class

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Sprint Context header and error_path detection are core resilience features that must be locked down with dedicated tests. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0018/evidence.md

**Deliverables:**
- D-0018: `TestPromptAndContext` class in `tests/sprint/test_phase8_halt_fix.py` with 3 tests:
  - T04.05: `build_prompt()` output contains `## Sprint Context` header
  - T04.06: `detect_prompt_too_long()` returns `True` when pattern found in `error_path`
  - T04.07: `error_path=None` maintains backward-compatible behavior

**Steps:**
1. **[PLANNING]** Review `build_prompt()` and `detect_prompt_too_long()` implementations from Phase 3
2. **[PLANNING]** Design test fixtures for prompt output and error file content
3. **[EXECUTION]** Implement T04.05: assert `build_prompt()` output contains `## Sprint Context` section
4. **[EXECUTION]** Implement T04.06: create temp error file with prompt-too-long pattern; assert `detect_prompt_too_long(error_path=error_file)` returns `True`
5. **[EXECUTION]** Implement T04.07: assert `detect_prompt_too_long(error_path=None)` behaves identically to original (backward compatibility)
6. **[VERIFICATION]** `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestPromptAndContext -v` exits 0 with 3 tests passing
7. **[COMPLETION]** Record test results in evidence

**Acceptance Criteria:**
- `TestPromptAndContext` class in `test_phase8_halt_fix.py` contains 3 test methods
- `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestPromptAndContext -v` exits 0 with 3 passed
- Tests verify Sprint Context header presence, error_path detection, and backward compatibility
- No false positives or negatives in prompt-too-long detection tests

**Validation:**
- Manual check: `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestPromptAndContext -v` exits 0 with 3 passed
- Evidence: TASKLIST_ROOT/artifacts/D-0018/evidence.md produced

**Dependencies:** T03.01, T03.02, T03.03
**Rollback:** Remove TestPromptAndContext class from test file
**Notes:** FR-020/FR-021 implementation. Test names T04.05-T04.07 are roadmap test IDs.

---

### T05.03 -- Implement TestFixesAndDiagnostics Test Class

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | PASS_RECOVERED routing, FailureClassifier config path, and error_file plumbing must be verified with dedicated tests to prevent regression. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0019/evidence.md

**Deliverables:**
- D-0019: `TestFixesAndDiagnostics` class in `tests/sprint/test_phase8_halt_fix.py` with 3 tests:
  - T04.08: PASS_RECOVERED appears in screen output (INFO routing)
  - T04.09: FailureClassifier uses config-driven path via `SprintConfig.output_file()`
  - T04.10 (named, explicit): `_determine_phase_status()` passes `error_file` through to `detect_prompt_too_long()` — covers FR-010/FR-011/FR-012

**Steps:**
1. **[PLANNING]** Review SprintLogger, FailureClassifier, and _determine_phase_status() implementations from Phase 4
2. **[PLANNING]** Design test fixtures for logger output capture, DiagnosticBundle with config, and phase status determination
3. **[EXECUTION]** Implement T04.08: mock SprintLogger, trigger write_phase_result with PASS_RECOVERED, assert INFO-level output
4. **[EXECUTION]** Implement T04.09: create DiagnosticBundle with config, call FailureClassifier.classify(), assert config-driven path used
5. **[EXECUTION]** Implement T04.10: mock detect_prompt_too_long, call _determine_phase_status(error_file=path), assert error_file forwarded
6. **[VERIFICATION]** `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestFixesAndDiagnostics -v` exits 0 with 3 tests passing
7. **[COMPLETION]** Record test results in evidence

**Acceptance Criteria:**
- `TestFixesAndDiagnostics` class in `test_phase8_halt_fix.py` contains 3 test methods
- `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestFixesAndDiagnostics -v` exits 0 with 3 passed
- T04.10 explicitly named per Variant A adoption — covers FR-010/FR-011/FR-012 error_file plumbing
- Tests use proper mocking to isolate units under test

**Validation:**
- Manual check: `uv run pytest tests/sprint/test_phase8_halt_fix.py::TestFixesAndDiagnostics -v` exits 0 with 3 passed
- Evidence: TASKLIST_ROOT/artifacts/D-0019/evidence.md produced

**Dependencies:** T04.01, T04.02, T04.03
**Rollback:** Remove TestFixesAndDiagnostics class from test file
**Notes:** FR-022 implementation. T04.10 is a named test adopted from Variant A to cover FR-010-FR-012 which otherwise lack dedicated test coverage.

---

### T05.04 -- Run Full Validation Sequence

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | The complete validation sequence must pass to confirm zero regressions, lint compliance, and format compliance before advancing to smoke validation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0020/evidence.md

**Deliverables:**
- D-0020: Validation suite passing with all 4 commands:
  1. `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` — 10 tests pass
  2. `uv run pytest tests/ -v --tb=short` — >= 638 passed (629 baseline + 10 new), exit 0
  3. `uv run ruff check` — exit 0, zero violations
  4. `uv run ruff format --check` — exit 0

**Steps:**
1. **[PLANNING]** Confirm all Phase 1-4 implementation and Phase 5 test tasks are complete
2. **[EXECUTION]** Run `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` and verify 10 tests pass
3. **[EXECUTION]** Run `uv run pytest tests/ -v --tb=short` and verify >= 638 passed, exit 0
4. **[EXECUTION]** Run `uv run ruff check` and verify exit 0, zero violations
5. **[EXECUTION]** Run `uv run ruff format --check` and verify exit 0
6. **[VERIFICATION]** All 4 validation commands exit 0 with expected results
7. **[COMPLETION]** Record all command outputs as evidence

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` exits 0 with 10 tests passed
- `uv run pytest tests/ -v --tb=short` exits 0 with >= 638 passed and zero failures
- `uv run ruff check` exits 0 with zero violations
- `uv run ruff format --check` exits 0

**Validation:**
- Manual check: All 4 validation commands produce expected exit codes and counts
- Evidence: TASKLIST_ROOT/artifacts/D-0020/evidence.md produced with full command outputs

**Dependencies:** T05.01, T05.02, T05.03
**Rollback:** TBD — fix any failing tests or lint issues before proceeding
**Notes:** NFR-001 through NFR-005 validation. Milestones M5.1, M5.2, M5.3. SC-001, SC-002, SC-003.

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm all 10 new tests pass, full regression suite is green, and static analysis is clean.

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P05-END.md

**Verification:**
- 10 new targeted tests pass in `test_phase8_halt_fix.py` (M5.1)
- Full regression suite passes with zero regressions: >= 638 passed (M5.2)
- Ruff lint and format checks clean (M5.3)

**Exit Criteria:**
- SC-001 (10 new tests pass), SC-002 (zero regressions), SC-003 (static analysis clean) all satisfied
- All deliverables D-0017 through D-0020 produced
- No unresolved test failures or lint violations
