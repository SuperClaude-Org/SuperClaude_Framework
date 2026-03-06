# D-0003 Spec: Batch-Level Checkpointing

## Module
`src/superclaude/cli/audit/checkpoint.py`

## progress.json Schema
```json
{
  "run_id": "string",
  "total_batches": "int",
  "batches": [{"batch_id": "str", "status": "PENDING|COMPLETED|FAILED", "files_processed": "int", "files_remaining": "int", "failure_reason": "str|null"}],
  "last_updated": "ISO 8601"
}
```

## Atomic Write
Uses tempfile.mkstemp + os.replace for crash-safe writes.
