---
deliverable: D-0023
task: T03.12
title: PortifyTUI Start/Stop Lifecycle
status: PASS
---

# D-0023: PortifyTUI Lifecycle

## Implementation

`src/superclaude/cli/cli_portify/tui.py`

## Components

| Symbol | Description |
|--------|-------------|
| `PIPELINE_STEPS` | Tuple of 7 step names (validate-config → panel-review) |
| `StepDisplayState` | Per-step display state (name, status, duration, gate, iteration, warning) |
| `DashboardState` | Mutable dashboard state with update_step, mark_running, mark_complete, set_review_pause, clear_review_pause, add_warning, compute_elapsed |
| `_build_dashboard_table(state)` | Builds Rich Table with 6 columns (#, Step, Status, Gate, Time, Info) + footer row |
| `TuiDashboard` | Controller: start() / stop() lifecycle |

## TUI Lifecycle

```python
dashboard = TuiDashboard()
dashboard.start()              # Registers Live display (no-op in non-terminal)
dashboard.step_start("s1")    # Marks step running
dashboard.step_complete("s1", "pass", 1.2)  # Updates display
dashboard.stop()               # Cleans up
```

## Graceful Degradation

In non-terminal environments (CI, tests), `start()` and `stop()` are no-ops. State mutations still occur for testability. `is_live` is always False in test environments.

## Validation

`uv run pytest tests/ -k "test_tui_lifecycle"` → 6 passed
`uv run pytest tests/cli_portify/test_tui.py` → 28 passed
