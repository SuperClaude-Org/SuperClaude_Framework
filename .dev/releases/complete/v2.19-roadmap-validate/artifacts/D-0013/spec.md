# D-0013: validate Subcommand and --no-validate Flag Spec

## CLI Surface

### `roadmap validate OUTPUT_DIR`
- Arguments: `OUTPUT_DIR` (required, path to directory containing pipeline outputs)
- Options:
  - `--agents` (default: `opus:architect` -- single-agent for cost efficiency per OQ-1)
  - `--model` (default: `""`)
  - `--max-turns` (default: 100)
  - `--debug` (flag)
- Constructs `ValidateConfig` and calls `execute_validate()`

### `roadmap run` addition
- New flag: `--no-validate` (boolean flag)
- When set: skips post-pipeline validation, records "skipped" in state file

## Implementation
- File: `src/superclaude/cli/roadmap/commands.py`
- Standalone validate default: 1 agent (cost efficiency)
- Roadmap run auto-invoke default: 2 agents (rigor)
