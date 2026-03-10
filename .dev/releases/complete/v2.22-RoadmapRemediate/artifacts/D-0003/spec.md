# D-0003: Finding Lifecycle Model

## Overview

Canonical finding status lifecycle for the v2.22 remediate/certify pipeline extension. Defines valid statuses, transitions, terminal states, and initial state assignment rules.

---

## State Machine

```
                  +---> FIXED    (agent remediation succeeded)
                  |
PENDING ----+---> FAILED   (agent remediation failed / timed out / rollback triggered)
                  |
                  +---> SKIPPED  (filtered out / NO_ACTION_REQUIRED / OUT_OF_SCOPE)
```

---

## Status Definitions

| Status | Value | Description | Terminal? |
|--------|-------|-------------|-----------|
| PENDING | `"PENDING"` | Finding parsed from validation report; awaiting remediation | No |
| FIXED | `"FIXED"` | Remediation agent successfully applied fix; certify step confirms | Yes |
| FAILED | `"FAILED"` | Remediation agent failed, timed out, or rollback was triggered | Yes |
| SKIPPED | `"SKIPPED"` | Finding excluded from remediation by filter or classification | Yes |

---

## Transition Rules

### Valid Transitions

| From | To | Trigger | Phase |
|------|----|---------|-------|
| PENDING | FIXED | Agent completes successfully; output passes verification | Phase 3 (Remediation Execution) |
| PENDING | FAILED | Agent exits non-zero, times out, or rollback is triggered | Phase 3 (Remediation Execution) |
| PENDING | SKIPPED | Finding filtered by scope selection (option 1/2/3) | Phase 2 (Prompt & Filter) |
| PENDING | SKIPPED | Finding classified as NO_ACTION_REQUIRED | Phase 2 (Prompt & Filter) |
| PENDING | SKIPPED | Finding classified as OUT_OF_SCOPE | Phase 2 (Prompt & Filter) |

### Invalid Transitions (Enforced)

- FIXED -> any: terminal state, no further transitions
- FAILED -> any: terminal state, no further transitions
- SKIPPED -> any: terminal state, no further transitions
- Any -> PENDING: initial state only, never re-assigned

---

## Initial State Assignment

1. **Parser output**: All findings parsed from validation reports are assigned `status = PENDING`
2. **Immediate SKIP**: During Phase 2 filtering:
   - Findings with `agreement_category == "NO_ACTION_REQUIRED"` -> `SKIPPED`
   - Findings with `agreement_category == "OUT_OF_SCOPE"` -> `SKIPPED`
   - Findings outside the user's scope selection (option 1: BLOCKING only, option 2: BLOCKING+WARNING) -> `SKIPPED`
3. **Zero-findings guard**: If 0 actionable findings remain after filtering, all findings are `SKIPPED` and pipeline proceeds to certify with stub tasklist

---

## Scenario Coverage

### Scenario 1: Filtering (Phase 2)
- User selects Option 1 (BLOCKING only)
- WARNING and INFO findings -> `SKIPPED`
- BLOCKING findings remain `PENDING` for remediation

### Scenario 2: Successful Remediation (Phase 3)
- Agent receives finding with `status = PENDING`
- Agent modifies target files successfully
- Output passes basic verification
- Finding -> `FIXED`

### Scenario 3: Failed Remediation (Phase 3)
- Agent receives finding with `status = PENDING`
- Agent exits non-zero or times out
- Snapshot rollback triggers (`.pre-remediate` files restored)
- Finding -> `FAILED`

### Scenario 4: Rollback-Triggered Failure (Phase 3)
- Agent modifies files but introduces errors
- Post-remediation check detects issues
- Rollback to `.pre-remediate` snapshot
- Finding -> `FAILED`

### Scenario 5: Skip Remediation Path (Phase 2)
- User selects option `n` (skip remediation)
- All PENDING findings -> remain `PENDING` (state saved as `validated-with-issues`)
- No transition occurs; pipeline ends without remediation

### Scenario 6: Zero Actionable Findings (Phase 2)
- All findings are NO_ACTION_REQUIRED or OUT_OF_SCOPE
- All findings -> `SKIPPED`
- Stub tasklist generated (`actionable: 0`)
- Pipeline proceeds to certify

---

## Implementation Notes

### Finding Dataclass Field
```python
status: str = "PENDING"  # One of: PENDING, FIXED, FAILED, SKIPPED
```

### Tasklist Representation
- `remediation-tasklist.md` records each finding with its status
- Pre-execution: all actionable findings show `PENDING`, filtered findings show `SKIPPED`
- Post-execution: updated in-place with `FIXED` or `FAILED` outcomes

### State File Integration
- Finding statuses are summarized in `.roadmap-state.json` under the `remediate` key
- Summary counts: `{fixed: N, failed: N, skipped: N, total: N}`
- Individual finding statuses stored in the tasklist artifact, not in the state file

---

## Alignment with Existing Pipeline Patterns

The finding lifecycle intentionally mirrors the existing `StepStatus` enum in `pipeline/models.py`:
- `StepStatus.PASS` ~ `Finding.FIXED` (success)
- `StepStatus.FAIL` / `StepStatus.TIMEOUT` ~ `Finding.FAILED` (failure)
- `StepStatus.SKIPPED` ~ `Finding.SKIPPED` (not executed)
- `StepStatus.PENDING` ~ `Finding.PENDING` (awaiting execution)

This alignment ensures conceptual consistency across the pipeline.
