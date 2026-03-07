# D-0033: Return Contract Extension — `unaddressed_invariants` Field

## Overview

Extends the return contract with a new `unaddressed_invariants` field that lists HIGH-severity UNADDRESSED items from the invariant probe (Round 2.5). All existing fields remain unchanged (NFR-003 backward compatibility).

## Field Schema

```yaml
unaddressed_invariants:
  type: list
  items:
    type: object
    properties:
      id: "INV-NNN identifier from invariant-probe.md"
      category: "One of: state_variables, guard_conditions, count_divergence, collection_boundaries, interaction_effects"
      assumption: "The specific assumption text that was probed"
      severity: "HIGH (always HIGH — only HIGH items are included)"
  default: []
  description: "Empty list on success or when Round 2.5 skipped; populated when HIGH-severity UNADDRESSED items exist"
```

## Behavior

| Scenario | Value |
|----------|-------|
| Successful convergence, no HIGH items | `[]` |
| Round 2.5 skipped (`--depth quick`) | `[]` |
| HIGH-severity UNADDRESSED items exist | `[{id: "INV-001", category: "state_variables", assumption: "...", severity: "HIGH"}, ...]` |
| Pipeline failed before debate | `[]` (field always present per write-on-failure rule) |

## NFR-003 Compliance

All 9 existing return contract fields remain unchanged:
1. `merged_output_path` — unchanged
2. `convergence_score` — unchanged
3. `artifacts_dir` — unchanged
4. `status` — unchanged
5. `base_variant` — unchanged
6. `unresolved_conflicts` — unchanged
7. `fallback_mode` — unchanged
8. `failure_stage` — unchanged
9. `invocation_method` — unchanged

The new `unaddressed_invariants` field is additive. Existing callers that do not read this field are unaffected.

## Files Modified

- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`:
  - Return contract YAML block: added `unaddressed_invariants: []` with comment
  - Field definitions table: added row for `unaddressed_invariants`

## Deliverable Status

- **Task**: T05.02 (originally T04.06)
- **Roadmap Item**: R-033
- **Status**: COMPLETE
- **Tier**: STRICT
