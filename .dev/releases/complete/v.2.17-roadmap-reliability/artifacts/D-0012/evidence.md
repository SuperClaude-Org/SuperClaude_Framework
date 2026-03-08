# D-0012: Full Test Suite Regression Results

## Summary

| Metric | Value |
|---|---|
| Total Tests | 2168 collected |
| Passed | 2075 |
| Failed | 1 |
| Skipped | 92 |
| Warnings | 30 |
| Duration | 46.09s |
| Exit Code | 1 (due to pre-existing failure) |

## Pipeline-Specific Tests

| Suite | Passed | Failed |
|---|---|---|
| `tests/pipeline/` | 540 | 0 |
| `tests/roadmap/` | (included above) | 0 |

**All pipeline gate tests and executor tests pass with zero failures.**

## Pre-Existing Failure (Not Related to Phase 1/Phase 2)

```
FAILED tests/audit/test_credential_scanner.py::TestScanContent::test_detects_real_secrets
  - AssertionError: Expected >= 3 real secrets, got 2
  - Last modified: commit b9bc0ce ("fixed this BS"), prior to Phase 1/Phase 2
  - Module: audit/credential_scanner (unrelated to pipeline gates or sanitizer)
```

## Gate/Sanitizer-Related Warnings

No new warnings related to gate fix or sanitizer changes were observed.

## Conclusion

Phase 1 (gate fix) and Phase 2 (output sanitizer + prompt hardening) introduce **zero regressions** to the existing test suite. The single failure is a pre-existing issue in an unrelated audit module.
