# Evidence: D-0032 — Resume Semantics

## Implementation
- Path: `src/superclaude/cli/sprint/models.py` (`build_resume_output` function)

## Test Results
- Tests: 9 passing in `tests/sprint/test_resume_semantics.py`
- Command: `uv run pytest tests/sprint/test_resume_semantics.py -v`

## Acceptance Criteria Met
- HALT output includes resume command with task ID
- HALT output includes remaining tasks list
- HALT output includes budget suggestion
- Diagnostic path included when available
- Budget status sourced from TurnLedger when provided
