# D-0036 Evidence: Allowlist Enforcement Test

## Task: T07.02 -- SC-005

## Test File
`tests/roadmap/test_phase7_hardening.py::TestAllowlistEnforcement`

## Test Results
```
7 passed
```

## Tests Executed
| Test | Description | Status |
|------|------------|--------|
| test_editable_files_constant | EDITABLE_FILES matches spec | PASS |
| test_allowed_files_pass_through | Allowlisted files pass | PASS |
| test_non_allowed_files_rejected | Non-allowlisted files rejected | PASS |
| test_no_files_affected_rejected | Empty files_affected → SKIP | PASS |
| test_mixed_allowed_non_allowed_rejected | Mixed files fully rejected | PASS |
| test_workspace_diff_restricted | Workspace diff restricted to allowlist | PASS |
| test_out_of_allowlist_findings_skipped_with_warning | OQ-004 compliance | PASS |

## SC-005 Verification
- Workspace diff before/after restricted to allowlist files only
- Non-allowlist files have identical checksums before and after
- Findings referencing non-allowlist files are SKIPPED

## Validation Command
```bash
uv run pytest tests/roadmap/test_phase7_hardening.py -k "Allowlist" -v
```
