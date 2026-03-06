# D-0037: Release Gate Rule 2 Enforcement Verification

## Enforcement Behavior

Release Gate Rule 2 is a **blocking** condition:
- Unresolved guard ambiguity without owner assignment prevents pipeline advancement to M4
- `GuardAnalysisOutput.can_advance_to_m4` returns `False` when any `ReleaseGateWarning.is_blocking` is True
- `ReleaseGateWarning.is_blocking` = True when `owner` is empty AND `accepted_risk` is None

## Resolution Paths

| Path | Condition | Effect |
|------|-----------|--------|
| Owner assignment | `warning.owner = "Name"` | `is_resolved=True`, `is_blocking=False` |
| Accepted risk | `warning.accepted_risk = AcceptedRisk(owner, rationale)` | `is_resolved=True`, `is_blocking=False` |

## Validation Results

| Check | Status |
|-------|--------|
| Unresolved ambiguity blocks advancement | PASS |
| Owner assignment unblocks advancement | PASS |
| Accepted risk unblocks advancement | PASS |
| Empty owner rejected by AcceptedRisk | PASS |
| Empty rationale rejected by AcceptedRisk | PASS |

## Known Bug Pattern Verification

The sentinel ambiguity pattern `_replayed_event_offset = len(plan.tail_events)` where value `0` means both "no events" and "start offset" is caught by the guard analyzer:
- Type transition: BOOL_TO_INT detected
- Value `0`: 2 semantic meanings documented
- Ambiguity flagged: True
- FMEA elevation: Yes (when severity >= high)
