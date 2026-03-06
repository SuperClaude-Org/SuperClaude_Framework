# Phase 4 -- Validation and Acceptance

Verify all milestones meet their acceptance criteria and success metrics. Confirm zero regressions across the full test suite, coverage thresholds, line removal targets, and NFR compliance.

### T04.01 -- Verify full test suite passes with zero regressions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Final acceptance gate: the complete test suite must pass with zero failures to confirm no regressions from Phase 1-3 changes. |
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
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0015/evidence.md

**Deliverables:**
- Full test suite run output confirming `uv run pytest` exits 0 with all tests passing

**Steps:**
1. **[PLANNING]** Confirm all Phase 1-3 tasks are marked complete
2. **[PLANNING]** Identify expected test count from Phase 1-3 additions
3. **[EXECUTION]** Run `uv run pytest -v` and capture full output
4. **[EXECUTION]** Verify exit code is 0 and no tests are marked as failed, error, or skipped-unexpectedly
5. **[VERIFICATION]** Manual check: all tests pass with zero failures
6. **[COMPLETION]** Record full test output in TASKLIST_ROOT/artifacts/D-0015/evidence.md

**Acceptance Criteria:**
- `uv run pytest` exits 0 with all tests passing
- Zero test failures, errors, or unexpected skips in output
- Test count includes all Phase 1 characterization tests and Phase 3 integration tests
- Output recorded as evidence artifact

**Validation:**
- `uv run pytest -v`
- Evidence: full test output in TASKLIST_ROOT/artifacts/D-0015/evidence.md

**Dependencies:** T01.01-T01.04, T02.01-T02.07, T03.01-T03.03
**Rollback:** N/A (read-only validation)
**Notes:** Classified STANDARD per adversarial merge verdict: pytest execution is not read-only and requires direct test verification.

---

### T04.02 -- Verify sprint executor coverage >= 70%

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Coverage threshold validates that Phase 1 characterization tests achieved the target safety net depth before refactoring was performed. |
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
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0016/evidence.md

**Deliverables:**
- Coverage report output showing sprint executor coverage >= 70%

**Steps:**
1. **[PLANNING]** Identify correct coverage command from roadmap: `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor`
2. **[PLANNING]** Confirm coverage tooling (pytest-cov) is available
3. **[EXECUTION]** Run `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor` and capture output
4. **[EXECUTION]** Parse coverage percentage from output; confirm >= 70%
5. **[VERIFICATION]** Manual check: coverage percentage meets threshold
6. **[COMPLETION]** Record coverage report in TASKLIST_ROOT/artifacts/D-0016/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor` reports coverage >= 70%
- Coverage report captured as evidence artifact
- No coverage measurement errors or tool failures
- Coverage includes all Phase 1 characterization test contributions

**Validation:**
- `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor`
- Evidence: coverage report in TASKLIST_ROOT/artifacts/D-0016/evidence.md

**Dependencies:** T01.01-T01.04, T02.01-T02.07
**Rollback:** N/A (read-only validation)
**Notes:** —

---

### T04.03 -- Verify net lines removed >= 58 from sprint/process.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Line removal metric confirms the duplication elimination objective was achieved in Phase 2 refactoring. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0017/evidence.md

**Deliverables:**
- `git diff --stat` output confirming >= 58 net lines removed from sprint/process.py

**Steps:**
1. **[PLANNING]** Identify baseline commit (before Phase 2 changes) for diff comparison
2. **[PLANNING]** Confirm git diff command scope: `git diff --stat <baseline>..HEAD -- src/superclaude/cli/sprint/process.py`
3. **[EXECUTION]** Run `git diff --stat` against baseline for sprint/process.py
4. **[EXECUTION]** Parse insertions/deletions; compute net removal (deletions - insertions)
5. **[VERIFICATION]** Manual check: net lines removed >= 58
6. **[COMPLETION]** Record diff output in TASKLIST_ROOT/artifacts/D-0017/evidence.md

**Acceptance Criteria:**
- `git diff --stat` shows net lines removed >= 58 from src/superclaude/cli/sprint/process.py
- Diff computed against pre-Phase-2 baseline commit
- Net removal = deletions minus insertions >= 58
- Diff output recorded as evidence artifact

**Validation:**
- `git diff --stat <baseline>..HEAD -- src/superclaude/cli/sprint/process.py`
- Evidence: diff output in TASKLIST_ROOT/artifacts/D-0017/evidence.md

**Dependencies:** T02.01-T02.07
**Rollback:** N/A (read-only validation)
**Notes:** —

---

### T04.04 -- Verify dead code lines removed >= 25 from roadmap/executor.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Line removal metric confirms dead code (_FORBIDDEN_FLAGS, _build_subprocess_argv) was successfully eliminated from roadmap/executor.py. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0018/evidence.md

**Deliverables:**
- `git diff --stat` output confirming >= 25 lines removed from roadmap/executor.py

**Steps:**
1. **[PLANNING]** Identify baseline commit for diff comparison (same as T04.03)
2. **[PLANNING]** Confirm git diff command scope: `git diff --stat <baseline>..HEAD -- src/superclaude/cli/roadmap/executor.py`
3. **[EXECUTION]** Run `git diff --stat` against baseline for roadmap/executor.py
4. **[EXECUTION]** Parse deletions; confirm >= 25 lines removed
5. **[VERIFICATION]** Manual check: dead code lines removed >= 25
6. **[COMPLETION]** Record diff output in TASKLIST_ROOT/artifacts/D-0018/evidence.md

**Acceptance Criteria:**
- `git diff --stat` shows >= 25 lines removed from src/superclaude/cli/roadmap/executor.py
- _FORBIDDEN_FLAGS and _build_subprocess_argv no longer present in file
- Diff output recorded as evidence artifact
- Net change accounts for Phase 3 additions (_embed_inputs, modified roadmap_run_step)

**Validation:**
- `git diff --stat <baseline>..HEAD -- src/superclaude/cli/roadmap/executor.py`
- Evidence: diff output in TASKLIST_ROOT/artifacts/D-0018/evidence.md

**Dependencies:** T02.07, T03.01-T03.03
**Rollback:** N/A (read-only validation)
**Notes:** —

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Verify all quantitative success criteria (test pass, coverage, line removal, NFR compliance) before final dependency check.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P04-T01-T05.md
**Verification:**
- Full test suite passes (T04.01)
- Sprint executor coverage >= 70% (T04.02)
- Net lines removed >= 58 from sprint/process.py (T04.03) and >= 25 from roadmap/executor.py (T04.04)
**Exit Criteria:**
- All 4 quantitative checks pass
- NFR-007 verified (T04.05)
- Only T04.06 (dependency check) remains

---

### T04.05 -- Verify NFR-007 zero violations

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | Final NFR-007 check confirms no cross-module imports were introduced during Phase 3 modifications to roadmap/executor.py. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0019/evidence.md

**Deliverables:**
- Grep output confirming `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results

**Steps:**
1. **[PLANNING]** Confirm NFR-007 command from roadmap
2. **[PLANNING]** Note this is a repeat of T02.06 to catch any Phase 3 regressions
3. **[EXECUTION]** Run `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/`
4. **[EXECUTION]** Verify 0 results returned
5. **[VERIFICATION]** Manual check: no cross-module imports
6. **[COMPLETION]** Record grep output in TASKLIST_ROOT/artifacts/D-0019/evidence.md

**Acceptance Criteria:**
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results
- No cross-module imports introduced by Phase 3 changes
- Verification is read-only
- Grep output recorded as evidence

**Validation:**
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/`
- Evidence: grep output in TASKLIST_ROOT/artifacts/D-0019/evidence.md

**Dependencies:** T02.06, T03.01-T03.03
**Rollback:** N/A (read-only validation)
**Notes:** —

---

### T04.06 -- Verify no new Python package dependencies (NFR-004)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | NFR-004 requires no new runtime dependencies; this check confirms pyproject.toml [project.dependencies] is unchanged. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0020/evidence.md

**Deliverables:**
- `git diff pyproject.toml` output confirming no additions to [project.dependencies]

**Steps:**
1. **[PLANNING]** Identify baseline for pyproject.toml diff
2. **[PLANNING]** Confirm diff scope: only [project.dependencies] section matters
3. **[EXECUTION]** Run `git diff <baseline>..HEAD -- pyproject.toml`
4. **[EXECUTION]** Parse output; verify no new entries in [project.dependencies]
5. **[VERIFICATION]** Manual check: no new dependencies added
6. **[COMPLETION]** Record diff output in TASKLIST_ROOT/artifacts/D-0020/evidence.md

**Acceptance Criteria:**
- `git diff pyproject.toml` shows no additions to [project.dependencies]
- Only dev dependencies (if any) may change; runtime dependencies unchanged
- Diff output recorded as evidence artifact
- NFR-004 compliance confirmed

**Validation:**
- `git diff <baseline>..HEAD -- pyproject.toml`
- Evidence: diff output in TASKLIST_ROOT/artifacts/D-0020/evidence.md

**Dependencies:** All prior tasks
**Rollback:** N/A (read-only validation)
**Notes:** —

---

### Checkpoint: End of Phase 4

**Purpose:** Final acceptance gate confirming all success criteria from the roadmap are met and the sprint is complete.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P04-END.md
**Verification:**
- All 6 validation tasks (T04.01-T04.06) completed with passing results
- All success criteria met: SC-001 through SC-005 from roadmap
- Evidence artifacts exist for all deliverables
**Exit Criteria:**
- Full test suite green (SC-004)
- Sprint executor coverage >= 70% (SC-003)
- Lines removed >= 58 sprint/process.py (SC-001) and >= 25 roadmap/executor.py (SC-002)
- NFR-007 zero violations (SC-005) and NFR-004 no new dependencies
