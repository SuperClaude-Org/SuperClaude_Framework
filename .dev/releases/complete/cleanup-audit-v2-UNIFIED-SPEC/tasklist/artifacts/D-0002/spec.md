# D-0002 Spec: Coverage Tracking

## Module
`src/superclaude/cli/audit/coverage.py`

## CoverageArtifact Schema
- total_files_scanned: int
- total_files_classified: int
- tier_breakdown: dict[tier -> {file_count, percentage, file_paths}]
- percentages_sum: float (must equal 100.0 ± 0.01%)

## Invariants
- No file counted in multiple tiers (dedup by file_path)
- Idempotent: same input → same output
