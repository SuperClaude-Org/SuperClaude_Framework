# D-0012: Synthetic [SHARED-ASSUMPTION] Diff Points (A-NNN Scheme)

## Overview

Promotion logic that converts UNSTATED assumptions to `[SHARED-ASSUMPTION]` tagged diff points with A-NNN identifiers. These are added to diff-analysis.md and included in the convergence denominator.

## A-NNN Identifier Scheme

- Sequential assignment starting from A-001 per debate session
- No gaps in sequence
- Only UNSTATED preconditions receive A-NNN IDs (STATED and CONTRADICTED are documented but not promoted)

## Promotion Rules

1. Only preconditions classified as `UNSTATED` are promoted
2. Each promoted assumption receives:
   - A-NNN identifier
   - `[SHARED-ASSUMPTION]` tag
   - Impact assessment
   - Status (initially UNRESOLVED, resolved during debate)

## Placement in diff-analysis.md

Added as section `6_shared_assumptions` in the diff-analysis.md artifact assembly, with table format:

| A-NNN | Assumption | Source Agreement | Impact | Status |
|-------|-----------|-----------------|--------|--------|

## Convergence Impact

A-NNN points are included in `total_diff_points` denominator:
```
total_diff_points = S_count + C_count + X_count + A_count
convergence = agreed_points / total_diff_points
```

## AC-AD2-3 Test

- Scenario: Debate produces 10 original diff points + 2 A-NNN shared assumption points
- Expected: Convergence denominator = 12 (not 10)

## Deliverable Status

- **Task**: T02.09 (first occurrence)
- **Roadmap Item**: R-012
- **Status**: COMPLETE
- **Tier**: STRICT
