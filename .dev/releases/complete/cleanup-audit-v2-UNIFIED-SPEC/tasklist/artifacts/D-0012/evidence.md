# D-0012: Evidence — Monorepo-Aware Batch Decomposition

## Test Results
- 15/15 tests passed (`tests/audit/test_batch_decomposer.py`)
- Segment isolation verified: no cross-segment batches
- Batch size limits enforced

## 3-Package Monorepo Fixture Test
```
Input: packages/a, packages/b, packages/c (6 files)
Result: 3 isolated batch groups, one per package segment
```

## Acceptance Criteria Verification
- [x] Batches never contain files from different segments
- [x] Batch sizes do not exceed configured maximum
- [x] Monorepo detection correctly identifies segment boundaries
- [x] Decomposition rules documented in D-0012/spec.md
