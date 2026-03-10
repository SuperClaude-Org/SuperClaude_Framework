# D-0016: Updated Convergence Formula with Taxonomy Gate + A-NNN Denominator

## Overview

Updated convergence formula that includes taxonomy coverage gate as a boolean pre-condition and A-NNN points in `total_diff_points` denominator.

## Formula

### Updated Denominator

```
total_diff_points = count(S-NNN) + count(C-NNN) + count(X-NNN) + count(A-NNN)
convergence = agreed_points / total_diff_points
```

### Taxonomy Gate (Boolean AND)

```
can_converge = (convergence_score >= threshold) AND (all_taxonomy_levels_covered)
```

Where `all_taxonomy_levels_covered` = L1_count > 0 AND L2_count > 0 AND L3_count > 0.

## Backward Compatibility

- Debates without shared assumptions: A-NNN count = 0, so denominator is unchanged
- Debates without taxonomy: all points default to L2, so coverage check passes trivially
- Identical convergence scores for pre-existing debates

## Status Output Extensions

| Status | Condition |
|--------|-----------|
| CONVERGED | Agreement >= threshold AND all taxonomy levels covered |
| NOT_CONVERGED | Agreement < threshold after max rounds |
| BLOCKED_BY_TAXONOMY | Agreement >= threshold BUT a taxonomy level has zero coverage |

## Test Scenario

- 10 original diff points + 2 A-NNN points = 12 total
- 10 agreed / 12 total = 83.3% convergence (not 100%)
- If L3 has zero coverage: BLOCKED_BY_TAXONOMY even at 83.3%

## Deliverable Status

- **Task**: T02.12
- **Roadmap Item**: R-016
- **Status**: COMPLETE
- **Tier**: STANDARD
