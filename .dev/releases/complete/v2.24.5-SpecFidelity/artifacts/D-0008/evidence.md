# D-0008 — Update `test_required_flags`

**Task:** T02.03
**Date:** 2026-03-15
**Status:** PASS

## Change Applied

**File:** `tests/pipeline/test_process.py`

### Diff

```diff
         assert "--no-session-persistence" in cmd
+        assert "--tools" in cmd
+        assert "default" in cmd
         assert "--dangerously-skip-permissions" in cmd
```

## Test Output

```
tests/pipeline/test_process.py::TestClaudeProcessCommand::test_required_flags PASSED [100%]
============================== 1 passed in 0.09s ===============================
```

## Acceptance Criteria — All Met

- [x] `test_required_flags` asserts `"--tools"` present in command list
- [x] `test_required_flags` asserts `"default"` present in command list
- [x] Test passes with `uv run pytest tests/pipeline/test_process.py::TestClaudeProcessCommand::test_required_flags -v`
