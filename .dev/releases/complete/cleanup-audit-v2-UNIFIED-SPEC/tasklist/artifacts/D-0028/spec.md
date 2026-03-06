# D-0028: Spot-Check Validator Specification

**Task**: T04.02 — Spot-Check Validator
**Status**: Complete

## Purpose

Validate consolidated audit results via stratified sampling to produce a consistency rate.

## Sampling Methodology

1. **Sample size**: 10% of total consolidated files, minimum 5, maximum 50.
2. **Stratified selection**: Sample proportionally from each classification tier.
3. **Random seed**: Configurable for reproducibility (default: hash of run timestamp).

## Validation Process

For each sampled file:

1. Re-run the classification pipeline on the file in isolation.
2. Compare the re-classification result against the consolidated result.
3. Record match/mismatch with both classifications and confidence values.

## Consistency Rate Computation

```
consistency_rate = matched_files / total_sampled_files
```

- Reported as a percentage (e.g., `92.5%`).
- Threshold: >= 85% is acceptable; < 85% triggers a warning in the report.

## Per-Tier Breakdown

Output includes consistency rate broken down by tier:

```json
{
  "overall": 0.925,
  "per_tier": {
    "remove": 0.95,
    "refactor": 0.88,
    "keep": 0.93
  },
  "sample_size": 40,
  "total_files": 400
}
```

## Constraints

- Validator must not modify consolidated results.
- Mismatch details must be logged for manual review.
- Sampling must cover all tiers that contain >= 1 file.
