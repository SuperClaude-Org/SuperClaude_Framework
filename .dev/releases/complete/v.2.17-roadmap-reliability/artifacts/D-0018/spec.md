# D-0018: Generate Prompt + Executor Pipeline Diagnostics

## Deliverable

1. `build_generate_prompt()` in `src/superclaude/cli/roadmap/prompts.py` references expanded extraction fields
2. `_inject_pipeline_diagnostics()` in `src/superclaude/cli/roadmap/executor.py` populates executor-only fields

## Generate Prompt Changes

- Added extraction field reference block listing all 13 fields the generate step should use
- Grouped fields by purpose: provenance, scope counts, complexity, domains/risks/deps, criteria, mode

## Executor Changes

- New function `_inject_pipeline_diagnostics(output_file, started_at, finished_at)`
- Injects `pipeline_diagnostics` YAML field into extract step frontmatter post-subprocess
- Contains: `elapsed_seconds`, `started_at`, `finished_at`
- Only activates for `step.id == "extract"`

## Verification

- Generate prompt references all expanded extraction fields
- Executor populates `pipeline_diagnostics` in extraction frontmatter
- All tests pass
