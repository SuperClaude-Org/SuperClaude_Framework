# D-0015: Post-Round Taxonomy Coverage Check + Forced Round Trigger

## Overview

Post-round taxonomy coverage check that blocks convergence when any level has zero coverage, plus forced round trigger dispatching a targeted debate round for the uncovered level.

## Algorithm

1. After each debate round, count diff points per taxonomy level (L1, L2, L3)
2. If any level has zero coverage:
   - Block convergence regardless of score
   - Trigger forced debate round targeting uncovered level
3. Forced round uses level-specific prompt with auto-tag signals

## Integration Points

| Location | Change |
|----------|--------|
| Convergence Detection | Added `taxonomy_coverage_gate` section with gate_condition and forced_round_trigger |
| Round 2 post_round_2 | Added taxonomy_coverage_check and if_blocked_by_taxonomy flow |
| Early termination conditions | Updated to require `AND all taxonomy levels covered` |
| Status output | Added `BLOCKED_BY_TAXONOMY` status |

## Forced Round Prompt Template

```
FORCED ROUND: Taxonomy Level {level} has zero coverage.
The debate has not addressed any {level_description} concerns.
Please identify and debate at least one {level} issue from the diff analysis.
Focus on: {level_auto_tag_signals}
```

## AC-AD5-1 Test

- Scenario: 87% convergence achieved, L3 has zero coverage
- Expected: Convergence blocked, forced L3 round triggered

## AC-AD5-4 Test

- Scenario: depth=quick, L3 has zero coverage
- Expected: Forced round still triggers (coverage check applies at all depths)

## Deliverable Status

- **Task**: T02.11
- **Roadmap Item**: R-015
- **Status**: COMPLETE
- **Tier**: STRICT
