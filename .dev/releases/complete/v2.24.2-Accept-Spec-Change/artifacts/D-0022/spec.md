# D-0022: Developer Guide — Auto-Resume Behavior

## Auto-Resume Detection Gate

When `execute_roadmap()` is called with `auto_accept=True` and the spec-fidelity step fails, the executor evaluates a three-condition detection gate before triggering an automatic resume:

1. **Recursion guard**: `cycle_count == 0` (at most one retry per invocation)
2. **Qualifying deviation files**: At least one `dev-*-accepted-deviation.md` with `disposition: ACCEPTED`, `spec_update_required: true`, and `mtime > started_at`
3. **Spec hash mismatch**: Current spec file hash differs from the `initial_spec_hash` captured at `execute_roadmap()` entry

All three conditions must be true. If `started_at` is absent from the state, the condition fails closed (no retry).

## Six-Step Disk-Reread Sequence

When all conditions are met, the executor performs:

1. Reread state from disk
2. Recompute spec hash from current spec file bytes
3. Atomically write new hash (`.tmp` + `os.replace()`)
4. Reread state from disk again (this is the state passed to resume)
5. Rebuild steps with `_build_steps(config)`
6. Call `_apply_resume(post_write_state, steps)`

Step 4 is critical: the resume must use the post-write disk state, not stale in-memory state.

## Failure Handling

- **Write failure** (step 3): Abort cycle, log error to stderr, fall through to normal halt
- **Second spec-fidelity failure** (after resume): `sys.exit(1)` with second-run results
- **Cycle guard blocks**: Log suppression message, fall through to normal halt

## API

```python
execute_roadmap(config, resume=False, no_validate=False, auto_accept=False)
```

`auto_accept` defaults to `False` for backward compatibility. Only the sprint runner passes `True`.
