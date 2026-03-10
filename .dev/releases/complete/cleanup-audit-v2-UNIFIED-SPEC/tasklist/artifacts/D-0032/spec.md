# D-0032: Budget Accounting Specification

**Task**: T04.06 — Budget Accounting System
**Status**: Complete

## Purpose

Track and enforce token budget consumption across audit phases with configurable limits.

## Budget Schema

```json
{
  "total_budget": "integer (tokens)",
  "consumed": "integer",
  "remaining": "integer",
  "per_phase_limits": {
    "phase_1": "integer",
    "phase_2": "integer",
    "phase_3": "integer",
    "phase_4": "integer"
  },
  "per_phase_consumed": {
    "phase_1": "integer",
    "phase_2": "integer",
    "phase_3": "integer",
    "phase_4": "integer"
  }
}
```

## Enforcement Rules

| Threshold | Action | Behavior |
|-----------|--------|----------|
| 75% of phase limit | WARN | Log warning, continue execution |
| 90% of phase limit | DEGRADE | Activate degradation sequence (see D-0033) |
| 100% of phase limit | HALT | Stop current phase, proceed to next or finalize |

## Global Budget

- Global halt at 100% of `total_budget` regardless of per-phase state.
- Global degrade at 90% of `total_budget`.

## Accounting Rules

- Budget is checked before each batch of files, not per-file.
- Consumed tokens are estimated from prompt + completion token counts.
- Budget state is persisted to allow resume (see D-0037).

## Constraints

- Budget cannot be negative; floor is 0.
- Phase limits must sum to <= total_budget.
- Budget overruns (batch completes past limit) are tolerated but logged.
