# D-0018: Parallel Agent Execution Coordinator

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Function
`execute_remediation(findings_by_file, config, output_dir) -> tuple[str, list[Finding]]`

## Architecture
- One thread per file group via `ThreadPoolExecutor`
- Each thread spawns `ClaudeProcess(prompt=..., files=[target_file])`
- Context isolation: no --continue, --session, --resume flags (NFR-003)
- Model inherited from parent pipeline config (NFR-010)

## ClaudeProcess Pattern
Matches `validate_executor.py` usage:
- `ClaudeProcess(prompt=..., output_file=..., error_file=..., max_turns=..., model=..., ...)`
- `proc.start()` -> `proc.wait()`
