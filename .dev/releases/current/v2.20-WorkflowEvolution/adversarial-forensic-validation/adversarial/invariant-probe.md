# Invariant Probe Results

## Round 2.5 — Fault-Finder Analysis

| ID | Category | Assumption | Status | Severity | Evidence |
|----|----------|------------|--------|----------|----------|
| INV-001 | state_variables | Prior synthesis can be reused as a neutral base without inheriting earlier compression loss | ADDRESSED | MEDIUM | Round 1 and Round 2 repeatedly flagged Variant 1 as potentially lossy; merge decision moved away from it as base. |
| INV-002 | guard_conditions | Strong evidence density alone guarantees minority-insight preservation | UNADDRESSED | MEDIUM | Round 2 Variant 4 rebuttal notes that Variant 3 can create false closure despite strong evidence. |
| INV-003 | collection_boundaries | All disagreements can be reduced to one dominant diagnosis without loss of causal precision | ADDRESSED | LOW | Scoring matrix preserved X-001 as unresolved and retained multi-causal tension. |
| INV-004 | interaction_effects | Combining Variant 3 evidence chains with Variant 1 epistemic taxonomy will not create over-complexity or duplicated claims | UNADDRESSED | MEDIUM | Emerging consensus favored this merge strategy, but no advocate fully specified how duplication would be controlled. |

## Summary

- **Total findings**: 4
- **ADDRESSED**: 2
- **UNADDRESSED**: 2
  - HIGH: 0
  - MEDIUM: 2
  - LOW: 0