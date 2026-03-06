# D-0033: Guard Resolution and Release Gate Rule 2 Specification

## Guard Test Deliverable Generation

For each ambiguous guard detection, generates `kind=guard_test` deliverables:

1. **Semantic documentation** (`GT-NNNN.sem`): Documents every guard value's semantic meaning
2. **Uniqueness test** (`GT-NNNN.uniq`): Verifies each semantic state maps to exactly one value
3. **Transition mapping** (`GT-NNNN.trans`): For type transitions, verifies all pre-transition states have post-transition equivalents

### Deliverable ID Format

`GT-{seq:04d}.{type}` where type is `sem`, `uniq`, or `trans`.

## Release Gate Rule 2

**Trigger**: Unresolved guard ambiguity (ambiguity_flagged=True, not suppressed)

**Enforcement**:
- Creates `ReleaseGateWarning` with mandatory owner field
- `is_blocking` = True when no owner assigned and no accepted risk
- Pipeline advancement blocked while `has_blocking_warnings` = True

**Resolution paths**:
1. Assign owner + review date → `is_resolved` = True
2. Accept risk with `AcceptedRisk(owner, rationale)` → `is_resolved` = True

### Accepted Risk Validation

- `owner`: Non-empty string required (empty string rejected with ValueError)
- `rationale`: Non-empty string required (empty string rejected with ValueError)

## Implementation

- File: `src/superclaude/cli/pipeline/guard_resolution.py`
- Exports: `resolve_guards`, `GuardResolutionOutput`, `ReleaseGateWarning`, `AcceptedRisk`
- NFR-007 compliant
