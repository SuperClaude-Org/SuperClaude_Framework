# D-0032: Budget Accounting — Evidence

**Tests**: 10 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Budget initialized with correct totals | PASS |
| 2 | Per-phase limits sum to <= total_budget | PASS |
| 3 | 75% threshold emits warning | PASS |
| 4 | 90% threshold triggers degradation | PASS |
| 5 | 100% threshold halts phase | PASS |
| 6 | Global budget halt at 100% | PASS |
| 7 | Budget checked per-batch not per-file | PASS |
| 8 | Budget state persisted for resume | PASS |
| 9 | Overrun tolerated but logged | PASS |
| 10 | Budget floor is zero, no negatives | PASS |

## Budget Enforcement Log

```
[BUDGET] phase_2: 74% consumed (14800/20000) — OK
[BUDGET] phase_2: 76% consumed (15200/20000) — WARN: approaching limit
[BUDGET] phase_2: 91% consumed (18200/20000) — DEGRADE: activating L1
[BUDGET] phase_2: 100% consumed (20000/20000) — HALT: phase complete
[BUDGET] global: 62% consumed (49600/80000) — OK
```
