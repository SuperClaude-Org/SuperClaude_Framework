---
deliverable_id: D-0004
task_id: T01.04
roadmap_item: R-004
phase: 1
type: signal-vocabulary
status: FINAL
---

# D-0004: Minimal Signal Vocabulary Constants

## Purpose

Define the 6 initial signal constants for machine-readable event logging (NDJSON) across the `cli_portify` pipeline. These constants are used by `monitor.py` for event classification and are consumed by execution logs and TUI rendering.

---

## Signal Constants

| # | Constant Name | String Value | Usage Context | Emitted By |
|---|--------------|-------------|---------------|------------|
| 1 | `STEP_START` | `"step_start"` | Emitted when a pipeline step begins execution | `executor.py` before each step invocation |
| 2 | `STEP_COMPLETE` | `"step_complete"` | Emitted when a pipeline step finishes successfully and passes its gate | `executor.py` after successful step + gate pass |
| 3 | `STEP_ERROR` | `"step_error"` | Emitted when a pipeline step encounters an error (exception, malformed output, gate failure) | `executor.py` on step failure |
| 4 | `STEP_TIMEOUT` | `"step_timeout"` | Emitted when a pipeline step exceeds its timeout limit | `process.py` / `executor.py` on timeout |
| 5 | `GATE_PASS` | `"gate_pass"` | Emitted when a gate check passes for a step | `gates.py` on successful gate evaluation |
| 6 | `GATE_FAIL` | `"gate_fail"` | Emitted when a gate check fails for a step | `gates.py` on failed gate evaluation |

---

## NDJSON Event Format

Each signal produces an NDJSON line with the following schema:

```json
{
  "timestamp": "2026-03-13T12:00:00.000Z",
  "signal": "step_start",
  "step": "validate_config",
  "step_number": 1,
  "phase": 2,
  "data": {}
}
```

The `data` field contains signal-specific payload:

| Signal | `data` Contents |
|--------|----------------|
| `step_start` | `{"step_name": "<name>"}` |
| `step_complete` | `{"step_name": "<name>", "duration_ms": <int>, "artifact_path": "<path>"}` |
| `step_error` | `{"step_name": "<name>", "error_type": "<classification>", "message": "<detail>"}` |
| `step_timeout` | `{"step_name": "<name>", "timeout_ms": <int>, "iteration": <int or null>}` |
| `gate_pass` | `{"step_name": "<name>", "gate_tier": "<EXEMPT|STANDARD|STRICT>", "checks_passed": <int>}` |
| `gate_fail` | `{"step_name": "<name>", "gate_tier": "<EXEMPT|STANDARD|STRICT>", "failed_checks": ["<check_name>", ...]}` |

---

## Extension Policy

The vocabulary extends during Phase 4 (subprocess orchestration) when subprocess behavior is understood. Expected extensions include:

- `subprocess_start` / `subprocess_complete` / `subprocess_error` — for Claude subprocess lifecycle
- `convergence_iteration` / `convergence_terminal` — for convergence loop events in Step 7
- `review_pause` / `review_resume` / `review_reject` — for user review gate events
- `budget_warning` / `budget_exhausted` — for TurnLedger budget events

Extensions MUST follow the same NDJSON event format. New constants are added to the signal vocabulary module; existing constants are never renamed or removed (append-only vocabulary).

---

## Implementation Reference

These constants will be defined in a constants module or directly within `monitor.py` (per D-0002 ownership boundary). The implementation location is:

```python
# In cli_portify/monitor.py or a dedicated constants submodule

STEP_START = "step_start"
STEP_COMPLETE = "step_complete"
STEP_ERROR = "step_error"
STEP_TIMEOUT = "step_timeout"
GATE_PASS = "gate_pass"
GATE_FAIL = "gate_fail"
```

---

## Cross-References

- Consumed by: T04.03 (Phase 4 monitoring implementation)
- Defined by: Roadmap Phase 0, Work Item 4
- Extended in: Phase 4 (subprocess orchestration)
- Used in: D-0003 Artifact 9 (NDJSON execution logs)
