# Phase 4 -- Rename Test Class

This phase renames `test_100kb_guard_fallback` to `test_embed_size_guard_fallback` in `tests/roadmap/test_file_passing.py`. Per spec Section 4.6, this is a distinct parallel track -- not a sub-task of Phase 3. Can execute concurrently with Phase 3 on a multi-person team.

### T04.01 -- Rename `test_100kb_guard_fallback` to `test_embed_size_guard_fallback`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Test class name references the obsolete 100 KB limit; must be renamed to reflect the new `_EMBED_SIZE_LIMIT` constant name (FR-ATL.3). |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | LIGHT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0019/evidence.md

**Deliverables:**
- Renamed test class: `test_100kb_guard_fallback` -> `test_embed_size_guard_fallback` in `tests/roadmap/test_file_passing.py`

**Steps:**
1. **[PLANNING]** Read `tests/roadmap/test_file_passing.py` and locate `test_100kb_guard_fallback`
2. **[PLANNING]** Confirm no other references to old name exist in the codebase
3. **[EXECUTION]** Rename class `test_100kb_guard_fallback` to `test_embed_size_guard_fallback`
4. **[EXECUTION]** Verify no import or reference breakage
5. **[VERIFICATION]** Quick sanity check: class name updated, file parses without syntax error
6. **[COMPLETION]** Record diff in D-0019/evidence.md

**Acceptance Criteria:**
- Class name `test_embed_size_guard_fallback` exists in `tests/roadmap/test_file_passing.py`
- Class name `test_100kb_guard_fallback` no longer exists in the file
- File parses without syntax errors (`python -c "import ast; ast.parse(open('tests/roadmap/test_file_passing.py').read())"`)
- Diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0019/evidence.md

**Validation:**
- Manual check: grep for `test_100kb_guard_fallback` returns no results in `tests/roadmap/test_file_passing.py`
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0019/evidence.md

**Dependencies:** T01.05 (Phase 1 must complete first)
**Rollback:** `git checkout tests/roadmap/test_file_passing.py`
**Notes:** FR-ATL.3 deliverable. Parallel with Phase 3 per spec Section 4.6.

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm test class rename is complete before integration testing.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P04-END.md

**Verification:**
- `test_embed_size_guard_fallback` exists in `tests/roadmap/test_file_passing.py`
- `test_100kb_guard_fallback` no longer exists anywhere in the codebase
- File parses without syntax errors

**Exit Criteria:**
- FR-ATL.3 rename complete
- No reference breakage from rename
- File syntactically valid
