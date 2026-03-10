# Phase 1 -- Gate Fix (Foundation)

Replace the strict byte-0 `_check_frontmatter()` implementation in `src/superclaude/cli/pipeline/gates.py` with a regex-based search that discovers YAML frontmatter anywhere in the document. This is the P0 foundation that unblocks all 8 pipeline steps and is a prerequisite for all subsequent phases.

---

### T01.01 -- Replace `_check_frontmatter()` with regex-based frontmatter discovery in `pipeline/gates.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002, R-003, R-004, R-005 |
| Why | `_check_frontmatter()` requires `---` at byte 0, rejecting valid extraction output with conversational preamble. All 8 pipeline steps share this code path. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (shared gate across all pipeline steps), breaking (backward compatibility required) |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer), 3-5K tokens, 60s timeout |
| MCP Requirements | Required: Sequential, Serena · Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001, D-0002, D-0003 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/spec.md`
- `TASKLIST_ROOT/artifacts/D-0002/spec.md`
- `TASKLIST_ROOT/artifacts/D-0003/spec.md`

**Deliverables:**
1. `D-0001`: Regex-based `_check_frontmatter()` function in `src/superclaude/cli/pipeline/gates.py` using `re.MULTILINE` pattern anchoring `^---` to line beginnings (not byte 0)
2. `D-0002`: Regex validation requiring at least one `key: value` line between `---` delimiters to distinguish frontmatter from markdown horizontal rules
3. `D-0003`: `required_fields` validation extracting and checking all required fields from the discovered frontmatter block

**Steps:**
1. **[PLANNING]** Read current `_check_frontmatter()` implementation in `src/superclaude/cli/pipeline/gates.py`; identify the startswith `---` check and all callers
2. **[PLANNING]** Identify all pipeline commands that share `_check_frontmatter()` for backward-compatibility verification
3. **[EXECUTION]** Replace `_check_frontmatter()` body with regex pattern `r'^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$'` using `re.MULTILINE`; use `.search()` instead of checking byte 0
4. **[EXECUTION]** Implement key extraction loop: parse discovered frontmatter block for `key: value` lines, collect found keys into a set
5. **[EXECUTION]** Implement required field validation: iterate `required_fields`, return `(False, f"Missing required frontmatter field '{field}' in {output_file}")` for any missing field
6. **[VERIFICATION]** Run `uv run pytest tests/` to verify no existing tests break; dispatch quality-engineer sub-agent to validate regex handles all edge cases (preamble, horizontal rules, empty files)
7. **[COMPLETION]** Record implementation evidence in `TASKLIST_ROOT/artifacts/D-0001/spec.md`

**Acceptance Criteria:**
- `_check_frontmatter()` in `src/superclaude/cli/pipeline/gates.py` returns `(True, None)` when called with content containing preamble before valid YAML frontmatter
- Horizontal rules (`---` with no `key: value` content between delimiters) are rejected with `(False, "YAML frontmatter not found in ...")`
- All files that currently pass `_check_frontmatter()` continue to pass (NFR-002 backward compatibility)
- Implementation documented in `TASKLIST_ROOT/artifacts/D-0001/spec.md` with regex pattern and validation logic

**Validation:**
- `uv run pytest tests/ -v` exits 0 with no regressions in existing pipeline tests
- Evidence: `TASKLIST_ROOT/artifacts/D-0001/spec.md` produced with implementation details

**Dependencies:** None (foundation task)
**Rollback:** Revert `_check_frontmatter()` to original startswith implementation via `git checkout src/superclaude/cli/pipeline/gates.py`
**Notes:** Reference implementation provided in spec §3.1; regex pattern uses `re.MULTILINE` for `^---` anchoring per FR-006.

---

### T01.02 -- Write 8 unit tests for `_check_frontmatter()` in `tests/` covering spec §6.1 test matrix

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Spec §6.1 defines 8 test cases covering preamble, clean, horizontal rule, missing frontmatter, missing field, multiple blocks, whitespace, and empty file scenarios. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[█████████░] 90%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution, 300-500 tokens, 30s timeout |
| MCP Requirements | Preferred: Sequential, Context7 · Fallback Allowed: Yes |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Deliverables:**
1. `D-0004`: 8 unit test functions in `tests/` validating `_check_frontmatter()` across all spec §6.1 cases

**Steps:**
1. **[PLANNING]** Review spec §6.1 test matrix: 8 test cases with input/expected pairs
2. **[PLANNING]** Determine test file location (e.g., `tests/test_gates.py` or `tests/pipeline/test_gates.py`) following existing project test organization
3. **[EXECUTION]** Write test for preamble before frontmatter: input `"Preamble\n---\nkey: val\n---\nBody"` → expected `(True, None)`
4. **[EXECUTION]** Write tests for: clean frontmatter `(True, None)`, horizontal rule `(False, "not found")`, missing frontmatter `(False, "not found")`, missing required field `(False, "Missing required")`, multiple `---` blocks (matches first valid), whitespace before frontmatter `(True, None)`, empty file `(False, "not found")`
5. **[VERIFICATION]** Run `uv run pytest tests/test_gates.py -v` and verify all 8 tests pass
6. **[COMPLETION]** Record test results in `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Acceptance Criteria:**
- `uv run pytest tests/test_gates.py -v` exits 0 with all 8 test cases passing
- Each test case matches the input/expected pairs from spec §6.1
- Tests are deterministic (same result on repeated runs)
- Test file location documented in `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Validation:**
- `uv run pytest tests/test_gates.py -v` exits 0
- Evidence: `TASKLIST_ROOT/artifacts/D-0004/evidence.md` produced with test results

**Dependencies:** T01.01 (function must exist before tests can run)
**Rollback:** Remove test file via `git checkout`
**Notes:** None.

---

### Checkpoint: End of Phase 1

**Purpose:** Verify gate fix foundation is solid before building output sanitizer and prompt hardening on top of it.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`

**Verification:**
- `_check_frontmatter()` regex implementation passes all 8 unit tests from T01.02
- Existing pipeline tests pass with no regressions (backward compatibility confirmed)
- Regex correctly rejects horizontal rules while accepting frontmatter with preamble

**Exit Criteria:**
- All T01.xx tasks completed with passing validation
- No STRICT-tier tasks have unresolved issues
- Evidence artifacts produced for D-0001 through D-0004
