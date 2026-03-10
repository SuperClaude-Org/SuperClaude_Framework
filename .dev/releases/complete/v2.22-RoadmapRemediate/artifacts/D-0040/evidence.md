# D-0040 Evidence: Deliberate-Failure Test

## Task: T07.06 -- SC-003

## Test File
`tests/roadmap/test_phase7_hardening.py::TestDeliberateFailure`

## Test Results
```
6 passed
```

## Tests Executed
| Test | Description | Status |
|------|------------|--------|
| test_unfixed_finding_reported_as_fail | Unfixed → FAIL in report | PASS |
| test_all_fail_no_false_passes | All FAIL → 0 passes | PASS |
| test_fail_has_specific_justification | FAIL includes specific text | PASS |
| test_route_outcome_with_failures | Outcome routes to certified-with-caveats | PASS |
| test_parse_certification_output_with_failures | FAIL lines parsed correctly | PASS |
| test_certification_report_with_failures_passes_gate | Report with FAILs passes gate | PASS |

## SC-003 Verification
- Unfixed findings correctly reported as FAIL in certification-report.md
- Each FAIL entry includes a specific justification (not generic)
- No false passes on unfixed findings
- route_certification_outcome correctly identifies failures and sets loop=False (NFR-012)

## Validation Command
```bash
uv run pytest tests/roadmap/test_phase7_hardening.py -k "DeliberateFailure" -v
```
