# D-0038: Anti-Lazy Guard — Evidence

**Tests**: 8 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | 90% uniformity triggers guard | PASS |
| 2 | 89% uniformity does not trigger | PASS |
| 3 | Small batches (<10) exempt from guard | PASS |
| 4 | Re-analysis executes on trigger | PASS |
| 5 | Second trigger accepts with warning flag | PASS |
| 6 | No infinite re-analysis loops | PASS |
| 7 | Custom threshold via flag works | PASS |
| 8 | Guard disabled via --disable-lazy-guard | PASS |

## Guard Trigger Log

```
[GUARD] batch_7 (25 files): remove=23 refactor=1 keep=1 — uniformity 92% — TRIGGERED
[GUARD] batch_7 re-analysis: remove=18 refactor=4 keep=3 — uniformity 72% — PASSED
[GUARD] batch_12 (20 files): keep=19 refactor=1 — uniformity 95% — TRIGGERED
[GUARD] batch_12 re-analysis: keep=18 refactor=2 — uniformity 90% — ACCEPTED with uniformity_warning
```
