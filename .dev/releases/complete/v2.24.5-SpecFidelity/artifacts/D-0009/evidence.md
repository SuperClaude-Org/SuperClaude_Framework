# D-0009 — Update `test_stream_json_matches_sprint_flags`

**Task:** T02.04
**Date:** 2026-03-15
**Status:** PASS

## Change Applied

**File:** `tests/pipeline/test_process.py`

### Diff

```diff
         assert "--no-session-persistence" in cmd
+        assert "--tools" in cmd
+        assert "default" in cmd
         assert "--output-format" in cmd
```

## RISK-003 Check (Index-Based Assertions)

All existing assertions in `test_stream_json_matches_sprint_flags` use either:
- `assert "FLAG" in cmd` (membership, position-independent)
- `cmd.index("FLAG")` + adjacency check (named-flag index, not positional)

No raw positional index access (e.g. `cmd[3]`) exists in this test. RISK-003 does not apply.

## Test Output

```
tests/pipeline/test_process.py::TestClaudeProcessStreamJsonCompat::test_stream_json_matches_sprint_flags PASSED [100%]
============================== 1 passed in 0.09s ===============================
```

## Acceptance Criteria — All Met

- [x] `test_stream_json_matches_sprint_flags` asserts `"--tools"` and `"default"` present
- [x] No index-based assertion failures from flag position shifts (RISK-003 verified)
- [x] Test passes with `uv run pytest tests/pipeline/test_process.py::TestClaudeProcessStreamJsonCompat::test_stream_json_matches_sprint_flags -v`
