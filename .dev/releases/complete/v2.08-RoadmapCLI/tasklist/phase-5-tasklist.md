# Phase 5 -- Validation & Acceptance Testing

Implement comprehensive test suites for pipeline, roadmap, and sprint regression. Validate all acceptance criteria (AC-01 through AC-07) and non-functional requirements (NFR-003 through NFR-007). This phase requires both M2 (sprint migration) and M4 (CLI features) to be complete.

### T05.01 -- Create comprehensive `tests/pipeline/` test suite covering all gate tiers, retry logic, and parallel dispatch

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | Pipeline tests validate the shared foundation independently, ensuring both sprint and roadmap consumers build on proven components. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0029/spec.md`
- `TASKLIST_ROOT/artifacts/D-0029/evidence.md`

**Deliverables:**
- `tests/pipeline/test_models.py`, `test_gates.py`, `test_executor.py`, `test_process.py`, `test_parallel.py` covering gate tier enforcement, retry logic, parallel dispatch, and cross-cancellation

**Steps:**
1. **[PLANNING]** Review existing tests from T01.07; identify coverage gaps for edge cases
2. **[PLANNING]** Plan additional test scenarios: gate tier boundary conditions, retry exhaustion, parallel timeout races
3. **[EXECUTION]** Extend `test_gates.py` with edge cases: whitespace-only files, UTF-8 BOM, frontmatter with empty values
4. **[EXECUTION]** Extend `test_executor.py` with scenarios: all steps pass, middle step fails with retry, retry exhaustion triggers halt
5. **[EXECUTION]** Extend `test_parallel.py` with timing-sensitive scenarios: near-simultaneous completion, timeout during cancellation
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -v --tb=long` and confirm all tests pass
7. **[COMPLETION]** Record test count and coverage summary

**Acceptance Criteria:**
- `uv run pytest tests/pipeline/ -v` exits 0 with all 5 test files passing
- Gate tests cover all 4 tiers with edge cases: empty file, malformed YAML, missing frontmatter, whitespace-only
- Executor tests verify retry logic and halt behavior with mock StepRunner
- Parallel tests verify cross-cancellation and timeout scenarios

**Validation:**
- `uv run pytest tests/pipeline/ -v` exits 0
- Evidence: test output with test count per file

**Dependencies:** T01.07 (initial test suite), all Phase 1 tasks
**Rollback:** Tests are additive; no rollback needed

---

### T05.02 -- Create comprehensive `tests/roadmap/` test suite covering all 9 test file categories

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | Roadmap tests validate the full command including CLI surface, models, prompts, gates data, executor, resume, parallel, state, and dry-run. |
| Effort | L |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0030/spec.md`
- `TASKLIST_ROOT/artifacts/D-0030/evidence.md`

**Deliverables:**
- 9 test files: `test_models.py`, `test_prompts.py`, `test_gates_data.py`, `test_executor.py`, `test_cli_contract.py`, `test_resume.py`, `test_parallel.py`, `test_state.py`, `test_dry_run.py`

**Steps:**
1. **[PLANNING]** Enumerate all test files and their coverage targets; verify each Phase 3-4 task has corresponding test coverage
2. **[PLANNING]** Design shared test fixtures in `tests/roadmap/conftest.py`: sample spec files, mock subprocess, state file factory
3. **[EXECUTION]** Consolidate and extend individual task tests into comprehensive test files
4. **[EXECUTION]** Add integration-style tests in `test_executor.py`: full pipeline run with mock subprocesses producing gate-passing output
5. **[EXECUTION]** Add CliRunner tests in `test_cli_contract.py`: flag parsing, help output, error handling
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -v --tb=long` and confirm all 9 test files pass
7. **[COMPLETION]** Record test count per file and overall coverage

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -v` exits 0 with all 9 test files discovered and passing
- `test_cli_contract.py` covers flag parsing, help output, and error handling via CliRunner
- `test_executor.py` includes integration test with mock subprocesses and gate-passing output
- All test files use `unittest.mock.patch("subprocess.Popen")` for subprocess isolation

**Validation:**
- `uv run pytest tests/roadmap/ -v` exits 0
- Evidence: test output listing all 9 files with pass counts

**Dependencies:** All Phase 3 and Phase 4 tasks
**Rollback:** Tests are additive; no rollback needed

---

### T05.03 -- Run sprint regression verification: all sprint test files pass with zero modifications during pipeline/ migration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Final sprint regression confirms NFR-001 (CLI API unchanged) and NFR-002 (no test modifications) hold after all phases complete (AC-06). |
| Effort | S |
| Risk | Medium |
| Risk Drivers | migration keyword; system-wide regression scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0031/spec.md`
- `TASKLIST_ROOT/artifacts/D-0031/evidence.md`

**Deliverables:**
- Sprint regression report: `uv run pytest tests/sprint/` exits 0 with all sprint test files passing and zero test modifications during pipeline/ migration (AC-06 verification)

**Steps:**
1. **[PLANNING]** Verify T02.04 regression passed; confirm no subsequent changes affect sprint
2. **[PLANNING]** Check `git diff tests/sprint/` to verify zero test file modifications since Phase 2
3. **[EXECUTION]** Run `uv run pytest tests/sprint/ -v --tb=long` to execute full regression suite
4. **[EXECUTION]** If any failures: trace root cause to specific phase change; fix without modifying test files
5. **[VERIFICATION]** Confirm exit 0 with all sprint test files collected and passing
6. **[COMPLETION]** Record final regression report with test output and git diff evidence

**Acceptance Criteria:**
- `uv run pytest tests/sprint/ -v` exits 0 with all sprint test files discovered and passing
- `git diff tests/sprint/` shows zero modifications across entire project history since migration
- Sprint CLI external behavior fully preserved (NFR-001, AC-06)
- No sprint test file was modified at any point during pipeline/ migration (v2.08 scope)

**Validation:**
- `uv run pytest tests/sprint/ -v` exits 0
- Evidence: `git diff --name-only tests/sprint/` returns empty

**Dependencies:** T02.04 (initial regression), all phases complete
**Rollback:** If regression fails, bisect to identify breaking change; revert that change

---

### T05.04 -- Validate acceptance criteria AC-01, AC-03, AC-04, AC-05, AC-07 via CliRunner tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Acceptance criteria validation ensures the roadmap command meets all specified behavioral requirements via automated tests. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0032/spec.md`
- `TASKLIST_ROOT/artifacts/D-0032/evidence.md`

**Deliverables:**
- CliRunner-based acceptance tests verifying: AC-01 (--dry-run prints 7 entries, exits 0), AC-03 (gate failure triggers halt), AC-04 (--resume skips completed steps), AC-05 (stale spec forces extract re-run), AC-07 (--agents routes models to subprocess)

**Steps:**
1. **[PLANNING]** Map each AC to specific test scenario and expected observable behavior
2. **[PLANNING]** Design CliRunner test harness with mock subprocess and temp directories
3. **[EXECUTION]** Implement AC-01 test: invoke with `--dry-run`, assert 7 entries in stdout, exit 0, no files created
4. **[EXECUTION]** Implement AC-03 test: mock subprocess to produce gate-failing output, assert HALT with diagnostic
5. **[EXECUTION]** Implement AC-04 test: pre-populate state file with completed steps, assert skip behavior
6. **[EXECUTION]** Implement AC-05 test: modify spec after state file creation, assert extract re-run warning
7. **[EXECUTION]** Implement AC-07 test: pass `--agents`, assert model values in mock subprocess argv
8. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_cli_contract.py -k acceptance -v`
9. **[COMPLETION]** Record AC validation results

**Acceptance Criteria:**
- AC-01: `--dry-run` test passes (7 entries, exit 0, no files)
- AC-03: gate failure triggers HALT with diagnostic output matching spec section 6.2
- AC-04: `--resume` with pre-populated state skips completed steps
- AC-05: stale spec (modified after state creation) triggers extract re-run with warning
- AC-07: `--agents "opus:architect,haiku:architect"` routes models correctly to subprocess argv

**Validation:**
- `uv run pytest tests/roadmap/test_cli_contract.py -k acceptance -v` exits 0
- Evidence: test output showing all 5 AC tests passing

**Dependencies:** T04.01-T04.07 (all CLI features), T05.02 (test infrastructure)
**Rollback:** Acceptance tests are additive; no rollback needed

---

### T05.05 -- Verify NFR-003, NFR-004, NFR-005, NFR-006, NFR-007 compliance via targeted assertions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Non-functional requirements enforce architectural constraints: pure Python gates, pure function prompts, gate data separation, no sprint fields in pipeline, no cross-module imports. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0033/spec.md`
- `TASKLIST_ROOT/artifacts/D-0033/evidence.md`

**Deliverables:**
- NFR compliance test file verifying: NFR-003 (gate_passed pure Python, no subprocess), NFR-004 (prompts pure functions, no I/O), NFR-005 (gate data separation from logic), NFR-006 (no sprint fields in pipeline models), NFR-007 (no sprint/roadmap imports in pipeline)

**Steps:**
1. **[PLANNING]** Map each NFR to verifiable assertion strategy (import scanning, AST analysis, or grep)
2. **[PLANNING]** Design test file structure: one test function per NFR
3. **[EXECUTION]** NFR-003: assert no `subprocess` import in `pipeline/gates.py`
4. **[EXECUTION]** NFR-004: assert no `open()`, `subprocess`, `os.path` in `roadmap/prompts.py`
5. **[EXECUTION]** NFR-005: assert `roadmap/gates.py` contains only `GateCriteria` instances (no function definitions importing from `pipeline/gates.py`)
6. **[EXECUTION]** NFR-006: assert no sprint-specific field names (`index_path`, `phases`, `stall_timeout`) in `pipeline/models.py`
7. **[EXECUTION]** NFR-007: assert no `from superclaude.cli.sprint` or `from superclaude.cli.roadmap` in any file under `pipeline/`
8. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_nfr_compliance.py -v`
9. **[COMPLETION]** Record NFR compliance verification results

**Acceptance Criteria:**
- NFR-003: `pipeline/gates.py` contains zero `subprocess` imports
- NFR-004: `roadmap/prompts.py` contains zero file I/O or subprocess calls
- NFR-005: `roadmap/gates.py` contains only data definitions, no enforcement logic
- NFR-006: `pipeline/models.py` contains zero sprint-specific fields (index_path, phases, stall_timeout)
- NFR-007: no file under `pipeline/` imports from `sprint/` or `roadmap/`

**Validation:**
- `uv run pytest tests/roadmap/test_nfr_compliance.py -v` exits 0
- Evidence: test output showing all 5 NFR checks passing

**Dependencies:** All phases (NFRs span entire codebase)
**Rollback:** NFR tests are additive; no rollback needed

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm all validation and acceptance testing is complete; project is ready for release.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P05-END.md`
**Verification:**
- `uv run pytest tests/pipeline/ tests/roadmap/ tests/sprint/ -v` exits 0 with all test files passing
- All 5 acceptance criteria (AC-01, AC-03, AC-04, AC-05, AC-07) verified via automated tests
- All 5 non-functional requirements (NFR-003 through NFR-007) verified via targeted assertions

**Exit Criteria:**
- Sprint regression: all sprint test files pass with zero modifications during pipeline/ migration
- Roadmap test suite: 9+ test files covering CLI, models, prompts, gates, executor, resume, parallel, state, dry-run
- NFR compliance: all architectural constraints enforced via automated tests
