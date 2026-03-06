# D-0028: Spot-Check Validator — Evidence

**Tests**: 10 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | 10% sample size calculated correctly | PASS |
| 2 | Minimum 5 files enforced | PASS |
| 3 | Maximum 50 files capped | PASS |
| 4 | Stratified selection covers all tiers | PASS |
| 5 | Reproducible results with same seed | PASS |
| 6 | Consistency rate computed correctly | PASS |
| 7 | Per-tier breakdown reported | PASS |
| 8 | Mismatch details logged | PASS |
| 9 | Warning emitted when rate < 85% | PASS |
| 10 | Consolidated results not modified | PASS |

## Validation Report Sample

```
Spot-Check Validation Report
  Sample: 40 / 400 files (10.0%)
  Overall consistency rate: 92.5%
  Per-tier: remove=95.0% refactor=88.0% keep=93.3%
  Mismatches: 3 files (see mismatch_log.json)
```
