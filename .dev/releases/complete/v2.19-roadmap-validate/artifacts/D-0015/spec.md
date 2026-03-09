# D-0015: Validation Status State Persistence Spec

## State Schema

Added to existing `.roadmap-state.json` under new `validation` key:

```json
{
  "validation": {
    "status": "pass" | "fail" | "skipped",
    "timestamp": "2026-03-08T12:00:00+00:00"
  }
}
```

## Resume Interaction
- On `--resume`, if `validation.status` is `pass` or `fail`, skip re-validation
- On `--resume`, if `validation.status` is `skipped` or key is missing, invoke validation

## Backward Compatibility
- New `validation` key is additive; no existing keys modified
- `read_state()` gracefully handles missing `validation` key

## Implementation
- File: `src/superclaude/cli/roadmap/executor.py`
- Function: `_save_validation_status(config, status)`
- Uses existing `write_state()` / `read_state()` helpers
