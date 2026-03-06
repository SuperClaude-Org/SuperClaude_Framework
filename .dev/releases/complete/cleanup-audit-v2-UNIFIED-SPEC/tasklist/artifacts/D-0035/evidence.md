# D-0035: Budget Caveats — Evidence

**Tests**: 6 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Caveat section present in budget-containing reports | PASS |
| 2 | Variance range stated as 20-50% | PASS |
| 3 | Estimation methodology section present | PASS |
| 4 | Caveat not suppressed by --depth summary | PASS |
| 5 | Caveat unmodified under degradation | PASS |
| 6 | Caveat placed after budget summary section | PASS |

## Caveat Section Sample

```
--- Budget Summary ---
  Total: 80,000 tokens | Consumed: 52,400 (65.5%) | Remaining: 27,600

--- Budget Caveat ---
  Token estimates are approximations based on prompt and completion
  token counting. Actual consumption may vary 20-50% from estimates
  depending on file complexity, model behavior, and response length
  variability. Budget thresholds (warn/degrade/halt) account for this
  variance by using conservative activation points.
```
