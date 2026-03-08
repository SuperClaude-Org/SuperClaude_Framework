# Phase 2 -- Output Sanitizer + Prompt Hardening

Implement the P2 output sanitizer (`_sanitize_output()` in `roadmap/executor.py`) and P3 prompt hardening (XML `<output_format>` blocks in `roadmap/prompts.py`). These are independent defense layers that both depend on Phase 1's gate fix as fallback.

---

### T02.01 -- Implement `_sanitize_output()` function in `src/superclaude/cli/roadmap/executor.py` with atomic write

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007, R-008, R-009 |
| Why | Subprocess output may contain conversational preamble before YAML frontmatter. The sanitizer strips preamble before gate validation, using atomic writes to prevent partial file corruption. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (strips file content), data (atomic file rewrite) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Sequential, Context7 · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005, D-0006 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/spec.md`
- `TASKLIST_ROOT/artifacts/D-0006/spec.md`

**Deliverables:**
1. `D-0005`: `_sanitize_output(output_file: Path) -> int` function in `src/superclaude/cli/roadmap/executor.py` that strips content before first `^---` line and returns byte count stripped
2. `D-0006`: Atomic write implementation using `.tmp` suffix + `os.replace()` to prevent partial file states

**Steps:**
1. **[PLANNING]** Read current `src/superclaude/cli/roadmap/executor.py` to identify insertion point and existing patterns
2. **[PLANNING]** Verify `os` and `re` imports are available; check Path usage patterns in the file
3. **[EXECUTION]** Implement `_sanitize_output()`: read file, check if content starts with `---` (after `.lstrip()`), if so return 0; search for `^---` via `re.search(r'^---[ \t]*$', content, re.MULTILINE)`; if no match return 0; slice content from match start; write to `.tmp` file; `os.replace()` to target
4. **[EXECUTION]** Add logging: `_log.info("Stripped %d-byte preamble from %s", len(preamble.encode()), output_file)`
5. **[VERIFICATION]** Run `uv run pytest tests/ -v` to verify no regressions
6. **[COMPLETION]** Record implementation in `TASKLIST_ROOT/artifacts/D-0005/spec.md`

**Acceptance Criteria:**
- `_sanitize_output()` function exists in `src/superclaude/cli/roadmap/executor.py` and returns `int` (byte count of stripped preamble)
- Files already starting with `---` are unchanged (returns 0)
- Atomic write uses `.tmp` + `os.replace()` pattern — no partial file state possible during rewrite
- Implementation documented in `TASKLIST_ROOT/artifacts/D-0005/spec.md`

**Validation:**
- Manual check: call `_sanitize_output()` on a file with preamble; verify file starts with `---` after call
- Evidence: `TASKLIST_ROOT/artifacts/D-0005/spec.md` produced

**Dependencies:** None (independent of T01.xx at code level; Phase 1 gate fix is a runtime dependency)
**Rollback:** `git checkout src/superclaude/cli/roadmap/executor.py`
**Notes:** Reference implementation provided in spec §3.2.

---

### T02.02 -- Wire `_sanitize_output()` into `roadmap_run_step()` between subprocess completion and gate validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The sanitizer must run after subprocess writes its output and before `_check_frontmatter()` validates it. This ensures clean artifacts enter the gate. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████▒░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Sequential · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/spec.md`

**Deliverables:**
1. `D-0007`: `_sanitize_output()` call inserted in `roadmap_run_step()` at the correct position: after subprocess completion, before gate validation

**Steps:**
1. **[PLANNING]** Read `roadmap_run_step()` in `src/superclaude/cli/roadmap/executor.py` to identify the subprocess call and subsequent gate call
2. **[PLANNING]** Confirm call order: subprocess → `_sanitize_output()` → `_check_frontmatter()`
3. **[EXECUTION]** Insert `_sanitize_output(output_file)` call between subprocess completion and gate validation in `roadmap_run_step()`
4. **[VERIFICATION]** Run `uv run pytest tests/ -v` to verify no regressions
5. **[COMPLETION]** Record wiring evidence in `TASKLIST_ROOT/artifacts/D-0007/spec.md`

**Acceptance Criteria:**
- `roadmap_run_step()` in `src/superclaude/cli/roadmap/executor.py` calls `_sanitize_output()` after subprocess and before gate
- Call order verified by code inspection: subprocess → sanitize → gate
- No regressions in existing tests
- Wiring documented in `TASKLIST_ROOT/artifacts/D-0007/spec.md`

**Validation:**
- Manual check: read `roadmap_run_step()` and verify call order
- Evidence: `TASKLIST_ROOT/artifacts/D-0007/spec.md` produced

**Dependencies:** T02.01 (function must exist before wiring)
**Rollback:** Remove the `_sanitize_output()` call line from `roadmap_run_step()`
**Notes:** None.

---

### T02.03 -- Write 5 unit tests for `_sanitize_output()` covering spec §6.2 test matrix

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | Spec §6.2 defines 5 test cases: preamble present, no preamble, no frontmatter, atomic write safety, and multi-line preamble. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[█████████░] 90%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Context7 · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Deliverables:**
1. `D-0008`: 5 unit test functions covering all spec §6.2 sanitizer test cases

**Steps:**
1. **[PLANNING]** Review spec §6.2 test matrix with input/expected pairs
2. **[PLANNING]** Determine test file location following existing patterns (e.g., `tests/test_executor.py`)
3. **[EXECUTION]** Write tests: preamble present (file rewritten, returns byte count), no preamble (unchanged, returns 0), no frontmatter (unchanged, returns 0), multi-line preamble (all lines stripped)
4. **[EXECUTION]** Write atomic write safety test: verify `.tmp` file used and `os.replace()` called (mock or inspect)
5. **[VERIFICATION]** Run `uv run pytest tests/test_executor.py -v` and verify all 5 tests pass
6. **[COMPLETION]** Record test results in `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Acceptance Criteria:**
- `uv run pytest tests/test_executor.py -v` exits 0 with all 5 test cases passing
- Each test case matches the input/expected pairs from spec §6.2
- Tests are deterministic
- Test results documented in `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Validation:**
- `uv run pytest tests/test_executor.py -v` exits 0
- Evidence: `TASKLIST_ROOT/artifacts/D-0008/evidence.md` produced

**Dependencies:** T02.01 (function must exist before tests can run)
**Rollback:** Remove test file
**Notes:** None.

---

### T02.04 -- Add `<output_format>` XML block to all 7 `build_*_prompt()` functions in `src/superclaude/cli/roadmap/prompts.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016, R-017, R-018 |
| Why | XML-tagged output format constraints at the end of each prompt exploit LLM recency bias to reduce preamble frequency in subprocess output. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 82%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Context7 · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009, D-0010 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/spec.md`
- `TASKLIST_ROOT/artifacts/D-0010/spec.md`

**Deliverables:**
1. `D-0009`: `<output_format>` XML block appended to all 7 `build_*_prompt()` function return values in `src/superclaude/cli/roadmap/prompts.py`
2. `D-0010`: XML block positioned as the last XML block in each prompt string (recency bias placement)

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/prompts.py` and identify all 7 `build_*_prompt()` functions
2. **[PLANNING]** Prepare the XML template per spec §3.3: `<output_format>` with CRITICAL instruction, negative prohibition, and format example
3. **[EXECUTION]** Append the XML block to the return value of each `build_*_prompt()` function, ensuring it is the last content in the prompt string
4. **[EXECUTION]** Verify all 7 functions: `build_extract_prompt`, `build_generate_prompt`, `build_diff_prompt`, `build_debate_prompt`, `build_score_prompt`, `build_merge_prompt`, `build_test_strategy_prompt` (confirm exact function names from file)
5. **[VERIFICATION]** Run `uv run pytest tests/ -v` to verify no regressions; grep all 7 functions for `<output_format>` presence
6. **[COMPLETION]** Record implementation in `TASKLIST_ROOT/artifacts/D-0009/spec.md`

**Acceptance Criteria:**
- All 7 `build_*_prompt()` functions in `src/superclaude/cli/roadmap/prompts.py` contain the `<output_format>` XML block
- `<output_format>` is the last XML block in each prompt return value
- No existing tests regress
- Implementation documented in `TASKLIST_ROOT/artifacts/D-0009/spec.md`

**Validation:**
- Manual check: grep `src/superclaude/cli/roadmap/prompts.py` for `<output_format>` — expect 7 matches
- Evidence: `TASKLIST_ROOT/artifacts/D-0009/spec.md` produced

**Dependencies:** None (independent of sanitizer tasks)
**Rollback:** `git checkout src/superclaude/cli/roadmap/prompts.py`
**Notes:** None.

---

### T02.05 -- Validate token budget: ≤200 tokens added per `build_*_prompt()` function (NFR-005)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | NFR-005 constrains prompt hardening to ≤200 additional tokens per function to avoid exceeding context budgets. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████▒░] 88%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Deliverables:**
1. `D-0011`: Token budget measurement results showing each of the 7 functions has ≤200 tokens added

**Steps:**
1. **[PLANNING]** Identify method for token counting (character-based approximation: ~4 chars per token)
2. **[EXECUTION]** Measure the `<output_format>` XML block character count; divide by 4 for approximate token count
3. **[EXECUTION]** Verify the block is identical across all 7 functions (same text = same token count)
4. **[VERIFICATION]** Confirm measured delta ≤200 tokens for each function
5. **[COMPLETION]** Record measurements in `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Acceptance Criteria:**
- Token delta measurement recorded for all 7 `build_*_prompt()` functions
- Each function's measured delta is ≤200 tokens (NFR-005)
- Measurement method documented (character count / 4 approximation or tokenizer)
- Results recorded in `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Validation:**
- Manual check: verify XML block character count / 4 ≤ 200
- Evidence: `TASKLIST_ROOT/artifacts/D-0011/evidence.md` produced

**Dependencies:** T02.04 (XML blocks must be added before measurement)
**Rollback:** N/A (read-only measurement)
**Notes:** None.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify output sanitizer and prompt hardening are both functional before integration testing in Phase 3.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`

**Verification:**
- `_sanitize_output()` function passes all 5 unit tests and is wired into `roadmap_run_step()`
- All 7 `build_*_prompt()` functions contain `<output_format>` XML block at end position
- Token budget ≤200 tokens per function confirmed

**Exit Criteria:**
- All T02.xx tasks completed with passing validation
- No unresolved STANDARD-tier issues
- Evidence artifacts produced for D-0005 through D-0011
