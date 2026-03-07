# D-0012 Evidence: Per-Task Subprocess Integration Test

## Test Execution

```
3 passed in 0.10s
```

## Tests Implemented

| Test | Tasks | Outcomes | Budget Verified |
|------|-------|----------|-----------------|
| test_integration_subprocess_five_tasks_mixed_outcomes | 5 | PASS/PASS/FAIL/PASS/INCOMPLETE | Yes: net consumed = 21, available = 79 |
| test_integration_subprocess_budget_exhaustion_skips_remaining | 5 (3 run, 2 skipped) | 3 PASS, 2 SKIPPED | Yes: budget exhaustion halts loop |
| test_integration_subprocess_all_pass_aggregation | 5 | All PASS | Yes: 15 consumed, 85 available |

## Acceptance Criteria Checklist

- [x] Integration test exercises >= 5 tasks through full per-task subprocess loop
- [x] All tasks launched (subprocess count == task count, verified with call counter)
- [x] Results aggregated into AggregatedPhaseReport
- [x] Budget accounting correct: sum of per-task actual turns == net consumed in TurnLedger
- [x] Mixed outcomes tested: PASS, FAIL, INCOMPLETE, SKIPPED
- [x] Budget exhaustion skips remaining tasks correctly
- [x] `uv run pytest tests/sprint/test_executor.py -k integration_subprocess` exits 0
