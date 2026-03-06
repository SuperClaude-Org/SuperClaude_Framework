# Phase 3 -- Tests and Validation

Comprehensive test coverage for the scaffold lifecycle: parsing, creation, status classification, executor integration, and prompt content. All tests must be mocked (no real subprocess execution). At least one test uses fixture content from a real phase tasklist file. Full regression verification against the sprint and project test suites.

### T03.01 -- Implement `TestParsePhaseTasks` test class in `test_scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Parser correctness is critical — incorrect task extraction would produce scaffolds with wrong task IDs or missing tasks |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Deliverables:**
- `TestParsePhaseTasks` class in `tests/sprint/test_scaffold.py` with 5 test methods

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/scaffold.py` to understand `parse_phase_tasks()` interface and edge cases
2. **[PLANNING]** Copy a section from a real phase tasklist file (e.g., `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/tasklist/phase-1-tasklist.md`) for the fixture test
3. **[EXECUTION]** Create `tests/sprint/test_scaffold.py` with `TestParsePhaseTasks` class containing: `test_parse_extracts_ids_titles_tiers` (3 tasks, STRICT/STANDARD/LIGHT), `test_parse_task_without_tier` (heading with no Tier row → UNKNOWN), `test_parse_missing_file` (non-existent path → []), `test_parse_empty_file` (file with heading only → []), `test_parse_real_tasklist_fixture` (real phase file content)
4. **[EXECUTION]** Use `tmp_path` pytest fixture for all file-based tests
5. **[VERIFICATION]** `uv run pytest tests/sprint/test_scaffold.py::TestParsePhaseTasks -v` — all 5 tests pass
6. **[COMPLETION]** Record deliverable D-0008 in execution log

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_scaffold.py::TestParsePhaseTasks -v` exits 0 with 5 tests passing
- `test_parse_real_tasklist_fixture` uses content copied from an actual phase tasklist file (not synthetic)
- All tests use `tmp_path` fixture for file creation (no real filesystem dependencies)
- Tests validate all four tier values (STRICT, STANDARD, LIGHT, EXEMPT) plus the UNKNOWN default

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py::TestParsePhaseTasks -v`
- Evidence: test output shows 5 passed, 0 failed

**Dependencies:** T01.02 (parse_phase_tasks must be implemented)
**Rollback:** Delete `tests/sprint/test_scaffold.py`
**Notes:** Fixture content must be copied from a real file, not fabricated.

---

### T03.02 -- Implement `TestScaffoldResultFile` test class in `test_scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Scaffold file correctness is the foundation of Layer 1 defense — incorrect format could cause false status signals |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/evidence.md`

**Deliverables:**
- `TestScaffoldResultFile` class in `tests/sprint/test_scaffold.py` with 7 test methods

**Steps:**
1. **[PLANNING]** Read `scaffold_result_file()` interface and `SCAFFOLD_TEMPLATE` format
2. **[PLANNING]** Identify the critical design properties to verify: no `status:`, no `EXIT_RECOMMENDATION`, correct YAML fields, task table population
3. **[EXECUTION]** Add `TestScaffoldResultFile` class with: `test_scaffold_creates_file`, `test_scaffold_yaml_frontmatter` (correct fields + no `status:`), `test_scaffold_task_table` (all tasks as `pending`), `test_scaffold_no_exit_recommendation`, `test_scaffold_creates_parent_dirs`, `test_scaffold_overwrites_existing`, `test_scaffold_empty_tasks` (0 tasks → `tasks_total: 0`)
4. **[EXECUTION]** Use `tmp_path` for all file operations; create `TaskMeta` instances directly for test inputs
5. **[VERIFICATION]** `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldResultFile -v` — all 7 tests pass
6. **[COMPLETION]** Record deliverable D-0009 in execution log

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldResultFile -v` exits 0 with 7 tests passing
- `test_scaffold_yaml_frontmatter` asserts `phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0` present AND `status:` absent
- `test_scaffold_no_exit_recommendation` asserts `EXIT_RECOMMENDATION` string does not appear anywhere in file content
- `test_scaffold_creates_parent_dirs` creates scaffold in a path with non-existent parent directories

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldResultFile -v`
- Evidence: test output shows 7 passed, 0 failed

**Dependencies:** T01.04 (scaffold_result_file must be implemented)
**Rollback:** Remove `TestScaffoldResultFile` class from `test_scaffold.py`
**Notes:** These tests verify the critical invariant: scaffold → PASS_NO_SIGNAL, not PASS or HALT.

---

### T03.03 -- Implement status classification and primary scenario tests in `test_scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | The integration between scaffold format and `_determine_phase_status()` is the core correctness property of the entire v2.14 design |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0010/evidence.md`

**Deliverables:**
- `TestScaffoldStatusClassification` class (5 tests) + `TestScaffoldPrimaryScenario` class (1 test) in `tests/sprint/test_scaffold.py`

**Steps:**
1. **[PLANNING]** Read `_determine_phase_status()` in `executor.py` to understand the exact signal matching logic and priority order
2. **[PLANNING]** Map each scaffold state to expected `PhaseStatus` outcome per the spec's status outcome matrix
3. **[EXECUTION]** Add `TestScaffoldStatusClassification` with: `test_untouched_scaffold_returns_pass_no_signal` (scaffold as-is → PASS_NO_SIGNAL), `test_partially_updated_scaffold` (some rows changed → PASS_NO_SIGNAL), `test_fully_completed_scaffold` (agent adds status + EXIT_RECOMMENDATION → PASS), `test_scaffold_with_halt` (status: FAIL + EXIT_RECOMMENDATION: HALT → HALT), `test_scaffold_overwritten_entirely` (full report → normal classification)
4. **[EXECUTION]** Add `TestScaffoldPrimaryScenario` with `test_max_turns_scenario`: 10 tasks, scaffold created, 6 rows updated to `pass`, 4 remain `pending`, no `status:` or `EXIT_RECOMMENDATION:` added → `_determine_phase_status()` returns `PASS_NO_SIGNAL`, and `PASS_NO_SIGNAL.is_success is True`
5. **[VERIFICATION]** `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldStatusClassification tests/sprint/test_scaffold.py::TestScaffoldPrimaryScenario -v` — all 6 tests pass
6. **[COMPLETION]** Record deliverable D-0010 in execution log

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldStatusClassification -v` exits 0 with 5 tests passing
- `test_untouched_scaffold_returns_pass_no_signal` calls `_determine_phase_status(exit_code=0, result_file=<scaffold>, output_file=<exists>)` and asserts result is `PhaseStatus.PASS_NO_SIGNAL`
- `test_max_turns_scenario` simulates the exact failure mode from the problem evidence: 10 tasks, 6 completed, max_turns hit, result is `PASS_NO_SIGNAL` with `is_success=True`
- All tests use `_determine_phase_status()` directly (not mocked) to verify real status classification behavior

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py -v` — all scaffold tests pass (parser + result file + classification + scenario)
- Evidence: test output shows all status classification tests passing with correct PhaseStatus values

**Dependencies:** T01.04 (scaffold_result_file), T02.01 (executor integration for _determine_phase_status import)
**Rollback:** Remove classification and scenario test classes from `test_scaffold.py`
**Notes:** These are integration tests — they call real `_determine_phase_status()` against scaffold files.

---

### T03.04 -- Add prompt content tests to `test_process.py` and run full regression

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Prompt content tests verify the Completion Protocol was fully replaced and the new Reporting Protocol references the scaffold correctly |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Deliverables:**
- 3 new test methods in `tests/sprint/test_process.py` + full regression pass across sprint and project test suites

**Steps:**
1. **[PLANNING]** Read existing `tests/sprint/test_process.py` to understand test patterns and fixtures for `build_prompt()` testing
2. **[PLANNING]** Identify the correct test class to add the new methods to (or create a new class if appropriate)
3. **[EXECUTION]** Add `test_prompt_references_scaffold`: assert `build_prompt()` output contains `"scaffold report already exists"`
4. **[EXECUTION]** Add `test_prompt_incremental_protocol`: assert output contains `"you MUST finalize"`
5. **[EXECUTION]** Add `test_prompt_no_old_completion_protocol`: assert output does NOT contain `"Completion Protocol"`
6. **[VERIFICATION]** Run full regression: `uv run pytest tests/sprint/ -v` (sprint suite) and `uv run pytest tests/ -v` (project suite)
7. **[COMPLETION]** Record deliverable D-0011 and final test counts in execution log

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_process.py -v` exits 0 with all tests passing (existing + 3 new)
- `uv run pytest tests/sprint/ -v` exits 0 with no regressions in any sprint test file
- `uv run pytest tests/ -v` exits 0 with no regressions in the full project test suite
- Total new test count across `test_scaffold.py` (18 tests) + `test_process.py` (3 tests) is >= 17

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py tests/sprint/test_process.py -v`
- Evidence: test count >= 17 new tests, all passing, zero regressions

**Dependencies:** T02.03 (Reporting Protocol must be in build_prompt()), T03.01-T03.03 (scaffold tests must exist)
**Rollback:** Remove the 3 new test methods from `test_process.py`
**Notes:** This is the final validation gate. All success criteria (SC-001 through SC-005) should be verifiable after this task.

---

### Checkpoint: End of Phase 3

**Purpose:** Final validation that all scaffold changes are correct, backward-compatible, and comprehensively tested.

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`

**Verification:**
- `uv run pytest tests/sprint/test_scaffold.py -v` shows >= 18 tests passing (5 parser + 7 result file + 5 classification + 1 scenario)
- `uv run pytest tests/sprint/ -v` shows zero regressions across the entire sprint test suite
- `uv run pytest tests/ -v` shows zero regressions across the full project test suite

**Exit Criteria:**
- All 11 deliverables (D-0001 through D-0011) are complete
- SC-001: Scaffold file creation verified via `test_scaffold_creates_file` and `test_max_turns_scenario`
- SC-003/SC-004: Full sprint and project test suites pass with no regressions
