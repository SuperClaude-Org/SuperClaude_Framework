# D-0024: Evidence - Duplication Matrix

## Test Results

9 tests passed (0 failures):
- TestJaccardSimilarity: 3/3 passed (identical sets = 1.0, disjoint sets = 0.0, partial overlap computed correctly)
- TestThresholdClassification: 3/3 passed (85% -> consolidate, 65% -> investigate, 50% -> ignored)
- TestMatrixOutput: 3/3 passed (output schema fields present, shared_imports populated, shared_exports populated)

## Similarity Calculation Verification

Test fixture pair:
- File A imports: `[os, sys, pathlib]`, exports: `[main, helper]`
- File B imports: `[os, sys, json]`, exports: `[main, utils]`
- Shared: `{os, sys, main}` = 3 items, Union: `{os, sys, pathlib, json, main, helper, utils}` = 7 items
- Jaccard: 3/7 = 0.4286 -> correctly classified as `ignore`

## Threshold Boundary Verification

- Pair at exactly 80%: classified as `investigate` (threshold is strictly greater-than)
- Pair at 81%: classified as `consolidate`
- Pair at 60%: classified as `ignore` (threshold is strictly greater-than)
