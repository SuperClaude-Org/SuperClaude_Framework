# D-0029: Consistency-Rate Language Specification

**Task**: T04.03 — Consistency-Rate Language Guidelines
**Status**: Complete

## Purpose

Establish standard language for reporting audit validation results, avoiding misleading terminology.

## Terminology Rules

| Use | Do Not Use | Rationale |
|-----|------------|-----------|
| consistency rate | accuracy | Implies ground truth we do not have |
| agreement rate | correctness | Same reason |
| classification stability | precision/recall | Statistical terms require labeled data |
| confidence calibration | validation score | Avoids implying external validation |

## Report Language Template

```
Classification Consistency Report
  The spot-check validator re-analyzed {sample_size} files ({pct}% of total).
  The overall consistency rate is {rate}%.
  This measures agreement between the consolidated result and an independent
  re-classification, not accuracy against a human-verified ground truth.
```

## Calibration Notes Template

When consistency rate < 90%, include:

```
Calibration Note: The consistency rate of {rate}% indicates moderate
classification stability. Tiers with rates below 85% ({low_tiers})
may benefit from manual review. Variance is expected in files with
ambiguous signals (e.g., partially used utilities, conditional imports).
```

## Constraints

- All user-facing output must use approved terminology.
- No report may claim "accuracy" without a human-labeled reference set.
- Calibration notes are mandatory when any per-tier rate falls below 90%.
