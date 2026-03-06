# D-0029: Consistency-Rate Language — Evidence

**Tests**: 8 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Output uses "consistency rate" not "accuracy" | PASS |
| 2 | Output uses "agreement rate" not "correctness" | PASS |
| 3 | No precision/recall terminology in reports | PASS |
| 4 | Calibration note included when rate < 90% | PASS |
| 5 | Calibration note omitted when rate >= 90% | PASS |
| 6 | Low-tier names listed in calibration note | PASS |
| 7 | Template renders with actual values | PASS |
| 8 | Language consistent across summary and detail views | PASS |

## Output Template Sample

```
Classification Consistency Report
  The spot-check validator re-analyzed 40 files (10.0% of total).
  The overall consistency rate is 92.5%.
  This measures agreement between the consolidated result and an independent
  re-classification, not accuracy against a human-verified ground truth.
```
