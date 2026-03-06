# D-0035 Evidence — TUI Gate Column

## Deliverable
TUI gate column in `src/superclaude/cli/sprint/tui.py`: inline gate status column in the phase task table using GateDisplayState for rendering.

## Files Modified
- `src/superclaude/cli/sprint/tui.py` — Added GateDisplayState import, `gate_states` dict + `_show_gate_column` flag to `__init__`, gate column to `_build_phase_table`
- `tests/sprint/test_tui_gate_column.py` — 8 tests covering visibility, rendering, and backward compatibility

## Test Results
```
uv run pytest tests/sprint/test_tui_gate_column.py -v
8 passed in 0.08s

uv run pytest tests/sprint/test_tui.py -v
10 passed in 0.08s (existing tests unbroken)
```

## Acceptance Criteria Verification
- [x] Gate column renders GateDisplayState per task in the phase table
- [x] Column uses non-blocking reads (dict.get with default, no locks)
- [x] Gate column hidden when grace_period=0 (backward compatibility)
- [x] `uv run pytest tests/sprint/ -k tui_gate_column` exits 0
