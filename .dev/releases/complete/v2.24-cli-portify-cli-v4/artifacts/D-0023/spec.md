# D-0023: analyze-workflow Step Implementation

## Deliverable

`analyze_workflow` step implementation in `src/superclaude/cli/cli_portify/steps/analyze_workflow.py`.

## Implementation

The step:
1. Loads component inventory (D-0015) via @path references
2. Constructs prompt using `AnalyzeWorkflowPrompt` builder (D-0018)
3. Executes via `PortifyProcess` (D-0017) with `--add-dir` scoping
4. Validates output through SC-003 STRICT gate (5 required sections, data flow diagram, 5 YAML frontmatter fields)
5. Handles failure modes: missing artifact, subprocess timeout, gate failure

## Files

- `src/superclaude/cli/cli_portify/steps/analyze_workflow.py` (implementation)
- `tests/cli_portify/test_analyze_workflow.py` (7 tests)

## Gate: SC-003 (STRICT)

- 5 required frontmatter fields: step, source_skill, cli_name, component_count, analysis_sections
- 5 required sections: Workflow Summary, Component Analysis, Data Flow, Complexity Assessment, Recommendations
- Data flow diagram with arrow notation
- Output < 400 lines

## Verification

`uv run python3 -m pytest tests/cli_portify/test_analyze_workflow.py -v` exits 0 (7/7 passed)
