# Phase 1 -- Sprint Executor Characterization Tests

Establish a characterization test safety net for the sprint executor by covering 6 untested subsystems before any refactoring begins. This phase increases line coverage from ~45% to >= 70% and pins current behavior so that Phase 2 refactoring can proceed safely.

### T01.01 -- Write watchdog/stall detection tests for sprint executor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | Sprint executor lines 126-162 (stall_timeout, stall_action, _stall_acted) have no test coverage; characterization tests must pin current behavior before hook refactoring in Phase 2. |
| Effort | S |
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
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0001/evidence.md

**Deliverables:**
- Test file with 3 test cases covering: kill action on stall timeout, warn action on stall timeout, stall counter reset on resume

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` lines 126-162 to understand stall_timeout, stall_action, and _stall_acted fields
2. **[PLANNING]** Identify existing test patterns in `tests/sprint/` for consistent fixture and mock style
3. **[EXECUTION]** Create `tests/sprint/test_watchdog.py` with 3 test cases: test_stall_kill_action, test_stall_warn_action, test_stall_reset_on_resume
4. **[EXECUTION]** Use MagicMock for subprocess and timer dependencies; no real subprocess invocation
5. **[EXECUTION]** Assert that stall_timeout, stall_action, and _stall_acted are all exercised in each relevant case
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_watchdog.py -v` and confirm all 3 tests pass
7. **[COMPLETION]** Record test output in TASKLIST_ROOT/artifacts/D-0001/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_watchdog.py -v` exits 0 with 3 tests passing
- MagicMock used for all external components; no real subprocess invocation in tests
- Tests pin current behavior of executor lines 126-162 (stall_timeout, stall_action, _stall_acted all exercised)
- Test file location follows project convention at `tests/sprint/test_watchdog.py`

**Validation:**
- `uv run pytest tests/sprint/test_watchdog.py -v`
- Evidence: test output log captured in TASKLIST_ROOT/artifacts/D-0001/evidence.md

**Dependencies:** None
**Rollback:** Delete `tests/sprint/test_watchdog.py`
**Notes:** —

---

### T01.02 -- Write multi-phase sequencing tests for sprint executor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | Multi-phase execution ordering and halt propagation across >1 phase are untested; characterization tests needed before Phase 2 refactoring. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0002/evidence.md

**Deliverables:**
- Test file with 2 test cases covering: 3-phase happy path execution order, halt propagation at phase 3

**Steps:**
1. **[PLANNING]** Read sprint executor phase-sequencing logic to identify how phases are iterated and how halt propagates
2. **[PLANNING]** Check for existing multi-phase test patterns in `tests/sprint/`
3. **[EXECUTION]** Create `tests/sprint/test_multi_phase.py` with test_three_phase_happy_path and test_halt_at_phase_three
4. **[EXECUTION]** Mock phase execution to verify ordering (phase 1 before phase 2 before phase 3) and halt propagation
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_multi_phase.py -v` and confirm both tests pass
6. **[COMPLETION]** Record test output in TASKLIST_ROOT/artifacts/D-0002/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_multi_phase.py -v` exits 0 with 2 tests passing
- Tests verify phases execute in order (1 -> 2 -> 3) via assertion on call sequence
- Tests verify halt propagates correctly across >1 phase
- Test file location follows project convention at `tests/sprint/test_multi_phase.py`

**Validation:**
- `uv run pytest tests/sprint/test_multi_phase.py -v`
- Evidence: test output log captured in TASKLIST_ROOT/artifacts/D-0002/evidence.md

**Dependencies:** None
**Rollback:** Delete `tests/sprint/test_multi_phase.py`
**Notes:** —

---

### T01.03 -- Write TUI/monitor/tmux integration tests for sprint executor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | TUI.update(), OutputMonitor lifecycle, and tmux tail pane calls are untested; 4 cases needed to pin behavior before hook migration. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0003/evidence.md

**Deliverables:**
- Test file with 4 test cases: TUI updates with MonitorState, TUI exception resilience, OutputMonitor reset/start/stop lifecycle, tmux update when session_name is set

**Steps:**
1. **[PLANNING]** Read TUI, OutputMonitor, and tmux integration points in sprint executor to map call sites
2. **[PLANNING]** Identify MonitorState structure and TUI.update() signature for accurate mocking
3. **[EXECUTION]** Create `tests/sprint/test_tui_monitor.py` with 4 test cases: test_tui_update_called_with_monitor_state, test_tui_exception_non_fatal, test_output_monitor_lifecycle, test_tmux_update_with_session_name
4. **[EXECUTION]** Use MagicMock for TUI, OutputMonitor, and tmux dependencies; verify call counts and arguments
5. **[EXECUTION]** Ensure TUI exception test confirms sprint does not abort when TUI.update() raises
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_tui_monitor.py -v` and confirm all 4 tests pass
7. **[COMPLETION]** Record test output in TASKLIST_ROOT/artifacts/D-0003/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_tui_monitor.py -v` exits 0 with 4 tests passing
- TUI.update() verified called with MonitorState argument via mock assertion
- TUI exception test confirms sprint execution continues after TUI.update() raises
- tmux update test confirms call occurs only when session_name is set

**Validation:**
- `uv run pytest tests/sprint/test_tui_monitor.py -v`
- Evidence: test output log captured in TASKLIST_ROOT/artifacts/D-0003/evidence.md

**Dependencies:** None
**Rollback:** Delete `tests/sprint/test_tui_monitor.py`
**Notes:** —

---

### T01.04 -- Write diagnostics collector tests for sprint executor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | DiagnosticCollector.collect() call on failure and non-fatal collection failure are untested; 2 cases needed to complete characterization coverage. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0004/evidence.md

**Deliverables:**
- Test file with 2 test cases: failure triggers DiagnosticCollector.collect(), exception in diagnostics does not abort sprint

**Steps:**
1. **[PLANNING]** Read DiagnosticCollector integration in sprint executor to identify collect() call site and error handling
2. **[PLANNING]** Check existing test patterns for consistent mock and fixture approach
3. **[EXECUTION]** Create `tests/sprint/test_diagnostics.py` with test_failure_triggers_collector and test_diagnostics_exception_non_fatal
4. **[EXECUTION]** Mock DiagnosticCollector; verify collect() is called on task failure and that collector exceptions do not propagate
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_diagnostics.py -v` and confirm both tests pass
6. **[COMPLETION]** Record test output in TASKLIST_ROOT/artifacts/D-0004/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_diagnostics.py -v` exits 0 with 2 tests passing
- DiagnosticCollector.collect() verified called on sprint task failure via mock assertion
- Exception in DiagnosticCollector.collect() confirmed non-fatal (sprint continues)
- Test file location follows project convention at `tests/sprint/test_diagnostics.py`

**Validation:**
- `uv run pytest tests/sprint/test_diagnostics.py -v`
- Evidence: test output log captured in TASKLIST_ROOT/artifacts/D-0004/evidence.md

**Dependencies:** None
**Rollback:** Delete `tests/sprint/test_diagnostics.py`
**Notes:** —

---

### Checkpoint: End of Phase 1

**Purpose:** Verify all 4 characterization test suites pass and sprint executor coverage has increased, establishing the safety net required before Phase 2 refactoring.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P01-END.md
**Verification:**
- `uv run pytest tests/sprint/ -v` exits 0 with all characterization tests passing (11 total cases across 4 suites)
- Sprint executor test coverage measured via `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor`
- No pre-existing tests broken by new test additions
**Exit Criteria:**
- All 4 test files exist and pass: test_watchdog.py, test_multi_phase.py, test_tui_monitor.py, test_diagnostics.py
- Sprint executor coverage >= 70% (target threshold from roadmap)
- Phase 2 dependencies satisfied (M1 complete)
