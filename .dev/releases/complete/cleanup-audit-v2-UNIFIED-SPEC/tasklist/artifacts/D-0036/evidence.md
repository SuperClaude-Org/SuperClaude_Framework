# D-0036: Report Depth — Evidence

**Tests**: 12 passed, 0 failed

## Test Summary

| # | Test | Result |
|---|------|--------|
| 1 | Summary mode shows tier counts | PASS |
| 2 | Summary mode shows top 10 per tier | PASS |
| 3 | Summary mode omits per-file data | PASS |
| 4 | Standard mode includes per-section breakdown | PASS |
| 5 | Standard mode includes directory assessments | PASS |
| 6 | Detailed mode includes per-file evidence | PASS |
| 7 | Detailed mode includes full conflict log | PASS |
| 8 | Default depth is standard | PASS |
| 9 | Invalid depth value rejected | PASS |
| 10 | Mandated sections present at all depths | PASS |
| 11 | Budget caveats present at all depths | PASS |
| 12 | Depth mode recorded in metadata | PASS |

## Sample Output at Each Depth

**Summary**: `Tier counts: remove=87 refactor=145 keep=172 | Consistency: 92.5% | Budget: 65.5% consumed`

**Standard**: Above + `Phase 1: 200 files, 3 findings | Phase 2: 212 files, 5 findings | Dir: src/cli/ (63 files, 60% refactor)`

**Detailed**: Above + `src/utils/legacy.py: remove (0.92) evidence=[import_analysis, git_history] conflict=resolved`
