# D-0032: 6th Qualitative Dimension — Invariant & Edge Case Coverage

## Overview

Adds a 6th scoring dimension to the qualitative scoring layer, expanding from 25 to 30 criteria. The new dimension "Invariant & Edge Case Coverage" evaluates how well each variant addresses boundary conditions, state interactions, guard conditions, count divergence, and interaction effects.

## 5 CEV Criteria

| # | Criterion | Detection Focus |
|---|-----------|-----------------|
| 1 | Addresses boundary conditions for collections (empty, single-element, maximum size) | Collection edge cases |
| 2 | Handles state variable interactions across component boundaries | Cross-component state |
| 3 | Identifies guard condition gaps (missing validation, unguarded type assumptions) | Validation completeness |
| 4 | Covers count divergence scenarios (off-by-one, inclusive/exclusive ranges) | Numeric boundary errors |
| 5 | Considers interaction effects when features or components combine | Emergent behavior risks |

## Scoring Formula

```
qual_score = total_criteria_met / 30
```

Previous: `qual_score = total_criteria_met / 25` (5 dimensions × 5 criteria)
Updated: `qual_score = total_criteria_met / 30` (6 dimensions × 5 criteria)

## Floor Rule

| Parameter | Value |
|-----------|-------|
| Floor threshold | 1/5 |
| Enforcement | Variants scoring <1/5 on Invariant & Edge Case Coverage are ineligible as base variant |
| Suspension | When ALL variants score 0/5, suspend floor with warning |
| Warning text | "Edge case floor suspended: no variant meets minimum coverage" |

### Floor Behavior Examples

- **AC-AD3-1**: Variant scores 24/25 on original dimensions but 0/5 on edge case → total 24/30 → ineligible as base (floor not met)
- **AC-AD3-2**: Variant A scores 4/5, Variant B scores 1/5 → scoring differentiates them (both eligible, A ranked higher on this dimension)
- **Suspension**: All variants score 0/5 → floor suspended with warning, selection proceeds on remaining 25 criteria

## Files Modified

- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`:
  - Summary block (line ~226): Updated to 6 dimensions, /30 formula, added edge_case_floor
  - Qualitative scoring section (~line 1595): Updated descriptive text, added invariant_edge_case_coverage dimension with 5 criteria and floor_rule
  - Formula: Changed from /25 to /30
  - base-selection assembly: Added 6th dimension subsection and edge case floor check subsection
- `src/superclaude/skills/sc-adversarial-protocol/refs/scoring-protocol.md`:
  - Added 6th dimension criteria
  - Added edge case floor rule
  - Updated formula from /25 to /30
  - Updated scoring output format

## Deliverable Status

- **Task**: T05.01 (originally T04.05)
- **Roadmap Item**: R-032
- **Status**: COMPLETE
- **Tier**: STRICT
