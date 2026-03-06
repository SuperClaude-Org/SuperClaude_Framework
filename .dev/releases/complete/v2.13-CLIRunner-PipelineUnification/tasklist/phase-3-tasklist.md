# Phase 3 -- Roadmap File-Passing Fix

Fix the unreliable --file flag approach in roadmap step execution by embedding input file contents inline in the prompt, with a 100KB size guard for large files. This phase modifies roadmap/executor.py after dead code was cleaned up in Phase 2.

### T03.01 -- Add _embed_inputs() helper to roadmap/executor.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | A dedicated helper function encapsulates the logic for reading input files and embedding them as fenced code blocks with path headers, replacing the unreliable --file flag approach. |
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
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0012/evidence.md

**Deliverables:**
- _embed_inputs() function in roadmap/executor.py that reads input files, embeds each as a fenced code block with path header, and handles empty input list as no-op

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/executor.py` to identify where input files are currently referenced and how --file flags are constructed
2. **[PLANNING]** Design _embed_inputs(input_paths: list[str]) -> str signature; returns concatenated fenced blocks or empty string for empty list
3. **[EXECUTION]** Implement _embed_inputs() in roadmap/executor.py: iterate input_paths, read each file, wrap in fenced code block with `# <path>` header
4. **[EXECUTION]** Handle empty input list as no-op (return empty string)
5. **[VERIFICATION]** Add unit test in `tests/roadmap/` verifying _embed_inputs() produces correct fenced blocks for 1+ files and returns empty string for empty list
6. **[COMPLETION]** Record function signature and test output in TASKLIST_ROOT/artifacts/D-0012/evidence.md

**Acceptance Criteria:**
- `grep -n "_embed_inputs" src/superclaude/cli/roadmap/executor.py` returns the function definition
- _embed_inputs([]) returns empty string (no-op for empty input list)
- _embed_inputs(["path/to/file.md"]) returns fenced code block with path header containing file contents
- Unit test passes: `uv run pytest tests/roadmap/ -v -k embed`

**Validation:**
- `uv run pytest tests/roadmap/ -v -k embed`
- Evidence: function signature + test output in TASKLIST_ROOT/artifacts/D-0012/evidence.md

**Dependencies:** T02.07 (roadmap/executor.py cleaned up before modification)
**Rollback:** Delete _embed_inputs() function
**Notes:** —

---

### T03.02 -- Modify roadmap_run_step() to use inline embedding with 100KB size guard

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Replacing --file flags with inline embedding in the prompt eliminates path-resolution failures; the 100KB guard prevents context overflow for unusually large input files by falling back to --file. |
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
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0013/evidence.md

**Deliverables:**
- roadmap_run_step() modified: extra_args=[] (no --file flags); prompt includes embedded input content via _embed_inputs(); if total content > 100KB, falls back to --file with warning logged

**Steps:**
1. **[PLANNING]** Read roadmap_run_step() in `src/superclaude/cli/roadmap/executor.py` to identify current --file flag construction and extra_args handling
2. **[PLANNING]** Identify the prompt construction point where embedded content should be injected
3. **[EXECUTION]** Modify roadmap_run_step(): call _embed_inputs() to get embedded content; if len(embedded) <= 100*1024, append to prompt and set extra_args=[]; else log warning and fall back to --file flags
4. **[EXECUTION]** Ensure paths with spaces are handled correctly in both inline and fallback paths
5. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -v` to confirm modification works; add test for 100KB guard trigger
6. **[COMPLETION]** Record modification details and test output in TASKLIST_ROOT/artifacts/D-0013/evidence.md

**Acceptance Criteria:**
- roadmap_run_step() sets extra_args=[] when total embedded content <= 100KB (no --file flags in subprocess args)
- Prompt contains embedded file content as fenced code blocks when under 100KB threshold
- 100KB guard triggers fallback to --file with warning logged (verified by test)
- `uv run pytest tests/roadmap/ -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/roadmap/ -v`
- Evidence: test output in TASKLIST_ROOT/artifacts/D-0013/evidence.md

**Dependencies:** T03.01
**Rollback:** Revert roadmap_run_step() to previous --file flag approach
**Notes:** —

---

### T03.03 -- Write integration test for roadmap file-passing

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Integration test validates end-to-end file-passing behavior: inline embedding, space-handling, and 100KB guard fallback, preventing regressions in the new approach. |
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
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0014/evidence.md

**Deliverables:**
- Integration test file with 3 scenarios: prompt contains embedded content, paths with spaces handled correctly, 100KB guard triggers fallback

**Steps:**
1. **[PLANNING]** Identify test fixture requirements: mock input files of various sizes, paths with spaces
2. **[PLANNING]** Design 3 test cases aligned to roadmap acceptance criteria
3. **[EXECUTION]** Create integration test file in `tests/roadmap/` with test_prompt_contains_embedded_content, test_paths_with_spaces, test_100kb_guard_fallback
4. **[EXECUTION]** Use tmp_path fixture for test files; create >100KB file for guard test
5. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -v` and confirm all 3 integration tests pass
6. **[COMPLETION]** Record test output in TASKLIST_ROOT/artifacts/D-0014/evidence.md

**Acceptance Criteria:**
- Integration test file exists in `tests/roadmap/` with 3 test cases
- test_prompt_contains_embedded_content verifies prompt string includes fenced code blocks with file content
- test_paths_with_spaces verifies paths containing spaces are embedded correctly
- test_100kb_guard_fallback verifies fallback to --file when total content exceeds 100KB

**Validation:**
- `uv run pytest tests/roadmap/ -v`
- Evidence: test output in TASKLIST_ROOT/artifacts/D-0014/evidence.md

**Dependencies:** T03.02
**Rollback:** Delete integration test file
**Notes:** —

---

### Checkpoint: End of Phase 3

**Purpose:** Verify roadmap file-passing fix is complete with inline embedding, size guard, and integration test coverage.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P03-END.md
**Verification:**
- `uv run pytest tests/roadmap/ -v` exits 0 with all roadmap tests passing (including 3 new integration tests)
- _embed_inputs() function exists in roadmap/executor.py
- roadmap_run_step() no longer uses --file flags for inputs under 100KB
**Exit Criteria:**
- All 3 integration test scenarios pass (embedded content, space handling, 100KB guard)
- `uv run pytest -v` exits 0 (full suite, zero regressions)
- Phase 4 validation dependencies satisfied (M1, M2, M3 complete)
