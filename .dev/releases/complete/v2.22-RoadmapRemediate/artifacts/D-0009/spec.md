# D-0009: Terminal Summary Printer and Interactive Prompt

## Implementation

- `format_validation_summary(findings: list[Finding]) -> str` in `src/superclaude/cli/roadmap/remediate.py`
- `should_skip_prompt(findings: list[Finding]) -> bool` in `src/superclaude/cli/roadmap/remediate.py`
- `RemediationScope` enum for prompt option mapping

## Prompt Behavior

The interactive 4-option prompt maps to `RemediationScope`:
- `[1]` BLOCKING -> `RemediationScope.BLOCKING_ONLY`
- `[2]` +WARNING -> `RemediationScope.BLOCKING_WARNING`
- `[3]` All -> `RemediationScope.ALL`
- `[n]` Skip -> caller handles skip path

## Edge Cases

- Zero BLOCKING + zero WARNING: `should_skip_prompt()` returns True, prompt auto-skipped
- Empty findings list: summary shows "Total findings: 0", prompt auto-skipped
- Prompt logic lives in `execute_roadmap()`, NOT in `execute_pipeline()` (FR-032)

## Verification

`uv run pytest tests/roadmap/test_remediate.py -k "summary or prompt"` exits 0
