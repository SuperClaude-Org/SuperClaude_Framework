# D-0034: Override Handler — Evidence

**Tests**: 6 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Valid reorder changes execution sequence | PASS |
| 2 | Invalid capability name rejected with error | PASS |
| 3 | Error message lists valid options | PASS |
| 4 | Disabling all capabilities rejected | PASS |
| 5 | Omitted capabilities retain default order | PASS |
| 6 | Override state logged in report metadata | PASS |

## Override Behavior Test Log

```
INPUT: --capability-order git_history,import_analysis
RESULT: Execution order = [git_history, import_analysis, reference_check, test_coverage, cross_reference]

INPUT: --disable-capability test_coverage
RESULT: test_coverage skipped; 4 capabilities active

INPUT: --capability-order invalid_name,import_analysis
RESULT: ERROR: Unknown capability 'invalid_name'. Valid: import_analysis, reference_check, test_coverage, git_history, cross_reference
```
