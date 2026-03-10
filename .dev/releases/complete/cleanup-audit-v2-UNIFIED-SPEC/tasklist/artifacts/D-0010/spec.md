# D-0010 Spec: Batch Failure and Retry Handling

## Module
`src/superclaude/cli/audit/batch_retry.py`

## Retry Policy
- Default max_retries: 2
- Per-batch retry: execute_fn called up to max_retries times
- On exhaustion: batch marked FAILED with failure_reason in progress.json

## Cascading Failure
All batches fail → `is_cascading_failure()` returns True → emit `MinimumViableReport` with error summary.

## MinimumViableReport Schema
```json
{
  "run_id": "str",
  "total_batches": "int",
  "failed_batches": "int",
  "status": "CASCADING_FAILURE",
  "error_summary": [{"batch_id": "str", "attempts": "int", "last_error": "str"}]
}
```
