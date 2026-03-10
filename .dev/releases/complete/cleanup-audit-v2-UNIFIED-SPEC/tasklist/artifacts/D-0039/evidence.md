# D-0039: Report Completeness — Evidence

**Tests**: 9 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | All 6 mandated sections present in valid report | PASS |
| 2 | Missing Executive Summary detected | PASS |
| 3 | Missing Validation Results detected | PASS |
| 4 | Empty section treated as missing | PASS |
| 5 | Directory assessment count matches threshold dirs | PASS |
| 6 | Missing directory assessment detected | PASS |
| 7 | Degraded report (L4) still requires all sections | PASS |
| 8 | Draft file written on failure | PASS |
| 9 | Check cannot be bypassed via flags | PASS |

## Pass/Fail Test Results

```
COMPLETE REPORT:
  [PASS] Executive Summary — present (12 lines)
  [PASS] Classification Breakdown — present (45 lines)
  [PASS] Validation Results — present (8 lines)
  [PASS] Budget Report — present (15 lines)
  [PASS] Methodology Notes — present (10 lines)
  [PASS] Recommendations — present (18 lines)
  [PASS] Directory assessments: 3/3 threshold dirs covered
  Result: FINALIZED

INCOMPLETE REPORT:
  [FAIL] Budget Report — MISSING
  [FAIL] Directory assessments: 2/3 threshold dirs covered
  Result: DRAFT (report.draft.json written)
```
