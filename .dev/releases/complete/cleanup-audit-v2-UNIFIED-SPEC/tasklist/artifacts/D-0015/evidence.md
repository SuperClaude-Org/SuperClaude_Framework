# D-0015: Evidence — Dry-Run Mode

## Test Results
- 12/12 tests passed (`tests/audit/test_dry_run.py`)

## Acceptance Criteria Verification
- [x] Dry-run produces estimates without analysis output (no classification fields)
- [x] Output includes file_count, batch_count, estimated_tokens, domain_distribution
- [x] Output format documented in D-0015/spec.md
