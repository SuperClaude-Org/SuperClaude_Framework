# D-0024: design-pipeline Step Implementation

## Deliverable

`design_pipeline` step implementation in `src/superclaude/cli/cli_portify/steps/design_pipeline.py`.

## Implementation

The step:
1. Loads portify-analysis.md (D-0023) as input
2. Constructs prompt using `DesignPipelinePrompt` builder (D-0018)
3. Executes via `PortifyProcess` (D-0017)
4. Runs SC-004 STRICT gate validation
5. Produces portify-spec.md with step graph, domain models, gate criteria

## Files

- `src/superclaude/cli/cli_portify/steps/design_pipeline.py` (implementation)
- `tests/cli_portify/test_design_pipeline.py` (9 tests)

## Gate: SC-004 (STRICT)

- Required frontmatter: step, source_skill, cli_name, pipeline_steps, gate_count
- At least 5 frontmatter fields
- Data flow diagram with arrows
- Minimum 30 lines

## Verification

`uv run python3 -m pytest tests/cli_portify/test_design_pipeline.py -v` exits 0 (9/9 passed)
