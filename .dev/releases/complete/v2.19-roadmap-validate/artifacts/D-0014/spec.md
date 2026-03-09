# D-0014: Auto-Invocation and Skip Logic Spec

## Code Paths (4 branches)

1. **Success + Invoke**: All 8 pipeline steps pass -> auto-invoke `execute_validate()` with 2 agents (inherited from parent config)
2. **No-validate + Skip**: `--no-validate` flag set -> skip validation, record "skipped" in state file
3. **Resume-success + Invoke**: `--resume` with all steps passing -> validate invoked (unless already completed per state file)
4. **Resume-failure + Skip**: `--resume` pipeline halts on failed step -> sys.exit(1) before validation reached

## Option Inheritance
- `--agents`: defaults to first 2 agents from parent roadmap config
- `--model`: inherited from parent
- `--max-turns`: inherited from parent
- `--debug`: inherited from parent

## Implementation
- File: `src/superclaude/cli/roadmap/executor.py`
- Function: `_auto_invoke_validate(config: RoadmapConfig)`
- Called at end of `execute_roadmap()` after all steps pass
