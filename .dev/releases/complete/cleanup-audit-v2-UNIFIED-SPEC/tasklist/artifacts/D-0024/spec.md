# D-0024: Duplication Matrix Specification

## Similarity Metric

Similarity is computed as the **Jaccard index** of two sets:
- Set A: union of file's imports and exports
- Set B: union of comparison file's imports and exports
- Jaccard = |A intersection B| / |A union B|

## Action Thresholds

| Similarity | Recommendation | Rationale |
|------------|---------------|-----------|
| > 80% | consolidate | Near-identical API surface; strong merge candidate |
| > 60% | investigate | Significant overlap; may share extracted utility |
| <= 60% | ignore | Insufficient overlap for actionable recommendation |

## Output Schema

Each pair above the 60% threshold produces a record:

| Field | Description |
|-------|-------------|
| file_a | First file in the comparison pair |
| file_b | Second file in the comparison pair |
| similarity | Jaccard index as a float (0.0 - 1.0) |
| shared_imports | List of import statements common to both files |
| shared_exports | List of export symbols common to both files |
| recommendation | `consolidate` or `investigate` based on threshold |

## Implementation

- Module: `src/superclaude/cli/audit/duplication.py`
- Pairwise comparison across all profiled files (O(n^2) pairs, filtered by threshold)
- Uses import/export data from Phase 2 profiles; no content hashing
