# D-0006: validate_prompts.py Specification

## Module

`src/superclaude/cli/roadmap/validate_prompts.py`

## Functions

### `build_reflect_prompt(roadmap: str, test_strategy: str, extraction: str) -> str`

- **Purpose**: Single-agent reflection prompt covering all 7 validation dimensions
- **Parameters**: 3 string arguments (paths to pipeline output files)
- **Returns**: Prompt string with YAML frontmatter contract and structured body
- **Frontmatter fields**: `blocking_issues_count`, `warnings_count`, `tasklist_ready`
- **Severity classifications**:
  - BLOCKING: Schema, Structure, Traceability, Cross-file consistency, Parseability
  - WARNING: Interleave, Decomposition
- **Embedded formula**: `interleave_ratio = unique_phases_with_deliverables / total_phases`
- **False-positive constraint**: "false positives waste user time"
- **Imports**: Reuses `_OUTPUT_FORMAT_BLOCK` from `prompts.py`

### `build_merge_prompt(reflect_reports: list[str]) -> str`

- **Purpose**: Adversarial merge prompt consolidating multiple agent reports
- **Parameters**: List of string paths to reflection reports
- **Returns**: Prompt string with merge categorization instructions
- **Frontmatter fields**: `blocking_issues_count`, `warnings_count`, `tasklist_ready`, `validation_mode`, `validation_agents`
- **Categories**: BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT
- **Agreement table**: Instructed to produce markdown table with Finding ID, Agent columns, Agreement Category

## Design Decisions

- Followed existing `prompts.py` pattern: pure functions, no I/O, shared `_OUTPUT_FORMAT_BLOCK`
- Imported `_OUTPUT_FORMAT_BLOCK` from `.prompts` rather than duplicating it
- All 7 validation dimensions from spec FR-050.5 embedded with severity labels
- Interleave ratio formula embedded verbatim per OQ-3 decision
- `build_merge_prompt` accepts dynamic agent count via `len(reflect_reports)`

## Verification

```bash
uv run python -c "from superclaude.cli.roadmap.validate_prompts import build_reflect_prompt, build_merge_prompt; p = build_reflect_prompt('r','t','e'); assert 'BLOCKING' in p and 'WARNING' in p; print('OK')"
```

Result: OK (exit 0)
