# D-0019: Timeout Enforcement and Retry Logic

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Constants
- `_AGENT_TIMEOUT_SECONDS = 300` (NFR-001)
- `_AGENT_RETRY_LIMIT = 1` (NFR-002)

## Function
`_run_agent_with_retry(target_file, findings, config, output_dir, all_target_files) -> tuple[str, int, int]`

## Retry Semantics
1. First attempt: run agent
2. On failure: restore from snapshot, re-create snapshot, retry once
3. On second failure: return failure exit code (triggers T04.07 rollback)
