# D-0017 Evidence — Git Diff Context Integration

## Deliverable
`get_git_diff_context()` function in `src/superclaude/cli/sprint/process.py`

## Implementation
- `get_git_diff_context(start_commit)` runs `git diff --stat <start_commit>` with 10s timeout
- Returns structured markdown section with code block containing diff summary
- Graceful handling: returns empty string on git not found, timeout, non-zero exit, or empty diff
- Integrated into `build_task_context()` — appended after prior-work summary when start_commit provided

## Test Evidence
```
tests/sprint/test_process.py::TestGetGitDiffContext::test_git_diff_context_success PASSED
tests/sprint/test_process.py::TestGetGitDiffContext::test_git_diff_context_empty_diff PASSED
tests/sprint/test_process.py::TestGetGitDiffContext::test_git_diff_context_non_zero_exit PASSED
tests/sprint/test_process.py::TestGetGitDiffContext::test_git_diff_context_git_not_found PASSED
tests/sprint/test_process.py::TestGetGitDiffContext::test_git_diff_context_timeout PASSED
```

## Acceptance Criteria Met
- [x] Git diff summary appended to each task's context injection after prior-work summary
- [x] Diff computed relative to sprint start commit (not working tree)
- [x] Graceful handling when git not available or no changes exist (empty diff section)
- [x] `uv run pytest tests/sprint/ -k git_diff_context` exits 0
