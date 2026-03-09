# D-0017: CLI Integration Test Evidence

## Test File
`tests/roadmap/test_validate_cli.py`

## Test Count
20 tests total, 20 passed, 0 failed

## Test Classes and Coverage

| Class | Tests | Coverage Area |
|-------|-------|---------------|
| TestValidateSubcommandHelp | 6 | validate --help output, all options present |
| TestRunNoValidateFlag | 1 | run --help shows --no-validate |
| TestValidateConfigConstruction | 2 | Single-agent default, custom agents |
| TestExitCodeBehavior | 3 | Exit 0 with no issues, with blocking, warning display |
| TestAutoInvocation | 2 | Auto-invoke after success, --no-validate skip |
| TestValidationStatePersistence | 4 | Pass/fail/skipped status, backward compatibility |
| TestResumeSkipsValidation | 2 | Resume skips completed, invokes when missing |

## Execution Output
```
============================= 201 passed in 0.26s ==============================
```
(201 = 181 existing + 20 new)
