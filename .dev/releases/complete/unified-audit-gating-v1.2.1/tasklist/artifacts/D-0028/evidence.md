# Evidence: D-0028 — Remediation Prompt Construction

## Implementation
- Path: `src/superclaude/cli/pipeline/trailing_gate.py` (`build_remediation_prompt` function)

## Test Results
- Tests: 6 passing in `tests/pipeline/test_trailing_gate.py::TestRemediationPrompt`
- Command: `uv run pytest tests/pipeline/test_trailing_gate.py::TestRemediationPrompt -v`

## Acceptance Criteria Met
- Prompt includes gate failure reason
- Prompt includes original acceptance criteria
- Prompt includes relevant file paths
- Prompt is scoped to remediation (not full re-execution)
- Prompt output is deterministic given the same inputs
