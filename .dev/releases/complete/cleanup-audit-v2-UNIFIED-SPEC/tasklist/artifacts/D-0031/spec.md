# D-0031: Directory Assessment Specification

**Task**: T04.05 — Directory Assessment Mode
**Status**: Complete

## Purpose

Provide aggregate directory-level summaries when a directory exceeds the file threshold.

## Activation Threshold

- Directories containing >= 50 files trigger directory assessment mode.
- Directories below threshold receive per-file classification as normal.

## Aggregate Format

```json
{
  "directory": "string",
  "file_count": "integer",
  "tier_distribution": {
    "remove": "integer",
    "refactor": "integer",
    "keep": "integer"
  },
  "dominant_classification": "string",
  "dominant_pct": "float",
  "risk_summary": "string",
  "assessed_as_directory": true
}
```

## Field Definitions

- **file_count**: Total files in the directory (non-recursive).
- **tier_distribution**: Count of files per classification tier.
- **dominant_classification**: Tier with the highest count.
- **dominant_pct**: Percentage of files in the dominant tier.
- **risk_summary**: One-line risk statement (e.g., "78% classified as remove; high cleanup potential").

## Constraints

- Directory assessments supplement, not replace, per-file data.
- Per-file records are still stored; the directory block is an additional summary.
- Nested directories are assessed independently if they also exceed the threshold.
- Threshold is configurable via `--dir-threshold N` (default 50).
