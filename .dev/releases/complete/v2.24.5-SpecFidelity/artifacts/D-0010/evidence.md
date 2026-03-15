# D-0010 — Add `test_tools_default_in_command`

**Task:** T02.05
**Date:** 2026-03-15
**Status:** PASS

## Test Added

**File:** `tests/pipeline/test_process.py`

### Test Code

```python
def test_tools_default_in_command(self, tmp_path):
    p = ClaudeProcess(
        prompt="test",
        output_file=tmp_path / "out.txt",
        error_file=tmp_path / "err.txt",
    )
    cmd = p.build_command()
    assert "--tools" in cmd
    assert cmd[cmd.index("--tools") + 1] == "default"
```

### Assertion Design

- `assert "--tools" in cmd` — verifies presence
- `assert cmd[cmd.index("--tools") + 1] == "default"` — verifies adjacency (value immediately follows flag)

## Test Output

```
tests/pipeline/test_process.py::TestClaudeProcessCommand::test_tools_default_in_command PASSED [100%]
============================== 1 passed in 0.09s ===============================
```

## Acceptance Criteria — All Met

- [x] Function `test_tools_default_in_command` exists in `tests/pipeline/test_process.py`
- [x] Assertion verifies `cmd[cmd.index("--tools") + 1] == "default"` (adjacency, not just presence)
- [x] Test passes with `uv run pytest tests/pipeline/test_process.py::TestClaudeProcessCommand::test_tools_default_in_command -v`
