# D-0036 Evidence — Shadow Mode (--shadow-gates)

## Deliverable
Shadow mode: when `--shadow-gates` is passed, trailing gate evaluation runs in parallel with blocking gates but results are collected as metrics only (do not affect behavior).

## Files Modified
- `src/superclaude/cli/sprint/models.py` — Added `shadow_gates` field to SprintConfig, added `ShadowGateMetrics` dataclass
- `src/superclaude/cli/sprint/commands.py` — Added `--shadow-gates` CLI flag to `run` command
- `src/superclaude/cli/sprint/config.py` — Added `shadow_gates` parameter to `load_sprint_config`
- `tests/sprint/test_shadow_mode.py` — 10 tests covering flag, metrics collection, and behavior isolation

## Test Results
```
uv run pytest tests/sprint/test_shadow_mode.py -v
10 passed in 0.05s

uv run pytest tests/sprint/test_config.py tests/sprint/test_models.py -v
160 passed in 0.10s (existing tests unbroken)
```

## Acceptance Criteria Verification
- [x] `--shadow-gates` flag enables shadow mode; metrics collected without affecting sprint behavior
- [x] Blocking gate results determine task outcome (shadow results are informational only)
- [x] Shadow metrics include: trailing gate latency (p50/p95), pass/fail rate
- [x] `uv run pytest tests/sprint/ -k shadow_mode` exits 0
