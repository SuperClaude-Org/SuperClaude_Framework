# D-0029: Release Gate Rule 1 Enforcement Validation

## Verification
- Silent corruption findings produce blocking conditions
- Pipeline `has_blocking_violations` returns True when unresolved violations exist
- `accept_violation()` requires non-empty `accepted_by` and `acceptance_rationale`
- After acceptance, `has_blocking_violations` returns False

## Known Bug Pattern Detection
| Bug Pattern | Variable | Detection Method | Status |
|-------------|----------|-----------------|--------|
| Wrong-operand state mutation | `_loaded_start_index` | State detector + invariant registry | DETECTED |
| Sentinel ambiguity | `_replayed_event_offset` | State detector + invariant registry | DETECTED |

## Blocking Behavior
- `CombinedM2Output.has_blocking_violations` property enforces gate
- Downstream M3 guard analysis should check this property before proceeding
- Acceptance requires: named owner (non-empty string) + documented rationale (non-empty string)
