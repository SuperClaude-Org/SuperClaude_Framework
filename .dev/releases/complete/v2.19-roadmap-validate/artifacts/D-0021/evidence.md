# D-0021: Integration Test Evidence -- SC-004, SC-005, Resume Paths

## Test Files

- `tests/roadmap/test_validate_cli.py` (existing, 19 tests)
- `tests/roadmap/test_validate_resume_failure.py` (new, 2 tests)

## SC-004: Auto-Invocation (1 test)

| Test | File | Verifies |
|------|------|----------|
| test_auto_invoke_after_success | test_validate_cli.py | `roadmap run` calls `_auto_invoke_validate` after all steps pass |

## SC-005: --no-validate Skip (1 test)

| Test | File | Verifies |
|------|------|----------|
| test_no_validate_skips_auto_invoke | test_validate_cli.py | `roadmap run --no-validate` does NOT call `_auto_invoke_validate`, records "skipped" in state |

## Resume Path Tests (3 tests)

| Test | File | Verifies |
|------|------|----------|
| test_resume_skips_when_already_passed | test_validate_cli.py | Resumed pipeline with completed validation skips re-validation |
| test_resume_invokes_when_not_yet_validated | test_validate_cli.py | Resumed pipeline without prior validation invokes validation |
| test_resume_halt_skips_validation | test_validate_resume_failure.py | Resumed pipeline that halts on failure does NOT invoke validation |

## Additional Coverage (test_validate_resume_failure.py)

| Test | Verifies |
|------|----------|
| test_non_resume_halt_also_skips_validation | Normal (non-resume) pipeline halt also skips validation |

## Execution Evidence

```
$ uv run pytest tests/roadmap/test_validate_cli.py tests/roadmap/test_validate_resume_failure.py -v
21 passed in 0.14s
```

## Acceptance Criteria Verification

| Criterion | Status | Test |
|-----------|--------|------|
| SC-004: `roadmap run` auto-invokes validation | PASS | test_auto_invoke_after_success |
| SC-005: `--no-validate` skips validation | PASS | test_no_validate_skips_auto_invoke |
| Resume-success: resumed pipeline invokes validation | PASS | test_resume_invokes_when_not_yet_validated |
| Resume-failure: halted pipeline does NOT invoke validation | PASS | test_resume_halt_skips_validation |
