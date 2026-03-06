# D-0021: Evidence - Env Key-Presence Matrix

## Test Results

16 tests passed (0 failures):
- TestEnvPatternDetection: 4/4 passed (process.env, os.environ, os.getenv, mixed patterns)
- TestDriftCategories: 4/4 passed (missing_from_example, unused_in_code, missing_from_env, example_unused)
- TestSecurityInvariant: 3/3 passed (no values in output, no values in intermediate state, no values in error messages)
- TestMatrixGeneration: 3/3 passed (single-env project, multi-env project, empty env files)
- TestFullDocsAudit: 2/2 passed (end-to-end matrix generation, drift report formatting)

## Security Invariant Verification

All test outputs inspected for value leakage:
- Matrix output contains only key names and presence booleans
- Error messages reference key names without values
- Intermediate data structures hold key names only

## Drift Detection Verification

Test fixture with known drift:
- `DATABASE_URL` in code but not in `.env.example` -> detected as `missing_from_example`
- `LEGACY_FLAG` in `.env.example` but not in code -> detected as `unused_in_code`
- All 4 drift categories correctly identified and categorized
