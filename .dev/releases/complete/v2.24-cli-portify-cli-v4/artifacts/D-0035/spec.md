# D-0035: Rich TUI Live Dashboard Specification

## Overview

The TUI dashboard (`src/superclaude/cli/cli_portify/tui.py`) provides real-time
visibility into pipeline execution state using the Rich library.

## Architecture

### Components

- `DashboardState`: Aggregate state model tracking all 7 step states, timing,
  iteration counter, review pause status, and warnings
- `StepDisplayState`: Per-step display state (status, duration, gate result, iteration, warning)
- `TuiDashboard`: Live rendering controller using `rich.live.Live`
- `_build_dashboard_table()`: Builds a Rich Table from current state

### Dashboard Layout

```
cli-portify pipeline
  #  Step                   Status  Gate   Time     Info
  1  validate-config        OK      -      0.2s
  2  discover-components    OK      pass   1.1s
  3  analyze-workflow       >>>     -      -
  4  design-pipeline        ...     -      -
  5  synthesize-spec        ...     -      -
  6  brainstorm-gaps        ...     -      -
  7  panel-review           ...     -      -
     Total elapsed                         45.3s
```

### Rendering Elements

| Element | Column | Values |
|---------|--------|--------|
| Step progress | Status | `...` pending, `>>>` running, `OK` pass, `FAIL` fail, `TOUT` timeout, `SKIP` skipped, `ERR` error |
| Gate state | Gate | `pass`/`fail`/`-` |
| Timing | Time | Per-step elapsed in seconds |
| Iteration | Info | `iter=N` for convergence steps |
| Warnings | Info | Appended to info column |
| Review pause | Dashboard stops live rendering, resumes after review |
| Total elapsed | Footer row | Pipeline total elapsed time |

### Graceful Degradation

In non-terminal environments (`sys.stderr.isatty()` is False or Rich unavailable):
- Falls back to simple line-based output on stderr
- Prints `[portify] <step> running... (<elapsed>)` per step transition

### Review Gate Integration

When a review gate prompts the user:
1. `pause_for_review(prompt)` stops the Live display
2. The review prompt is displayed on stderr (by review module)
3. After user responds, `resume_after_review()` restarts Live display

## API

```python
dashboard = TuiDashboard()
dashboard.start()
dashboard.step_start("validate-config")
dashboard.step_complete("validate-config", "pass", 0.2)
dashboard.set_iteration("panel-review", 2)
dashboard.pause_for_review("Accept design? [y/N]")
# user interaction
dashboard.resume_after_review()
dashboard.stop()
```
