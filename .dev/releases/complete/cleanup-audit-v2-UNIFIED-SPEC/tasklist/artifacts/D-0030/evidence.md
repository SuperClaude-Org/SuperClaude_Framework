# D-0030: Output Artifacts — Evidence

**Tests**: 11 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Coverage artifact validates against schema | PASS |
| 2 | Validation artifact validates against schema | PASS |
| 3 | Missing required field causes hard failure | PASS |
| 4 | tier_breakdown sums to total_files_scanned | PASS |
| 5 | consistency_rate within 0.0-1.0 range | PASS |
| 6 | sample_size <= total_files | PASS |
| 7 | Mismatches array contains valid objects | PASS |
| 8 | Timestamp is valid ISO 8601 | PASS |
| 9 | Artifacts written as pretty-printed JSON | PASS |
| 10 | Empty scan produces valid zero-count artifact | PASS |
| 11 | Phases_completed reflects actual phases run | PASS |

## Artifact Content Samples

Coverage: `{"total_files_scanned": 412, "tier_breakdown": {"remove": 87, "refactor": 145, "keep": 172, "unclassified": 8}, "phases_completed": [1,2,3], "timestamp": "2026-03-05T14:22:00Z"}`

Validation: `{"consistency_rate": 0.925, "sample_size": 40, "total_files": 412, "per_tier_rates": {"remove": 0.95, "refactor": 0.88, "keep": 0.93}}`
