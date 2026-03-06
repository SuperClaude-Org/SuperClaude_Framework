# D-0027: Consolidation Engine Specification

**Task**: T04.01 — Cross-Phase Consolidation Engine
**Status**: Complete

## Purpose

Merge per-phase classification results into a single unified dataset with deterministic conflict resolution.

## Primary Key

- `file_path` (absolute, normalized) serves as the unique key across all phase outputs.
- Duplicate entries for the same `file_path` are resolved, never retained as separate rows.

## Conflict Resolution: Highest-Confidence-Wins

When multiple phases classify the same file differently:

1. Compare `confidence` scores from each phase result.
2. Select the classification with the highest confidence value.
3. On tie: prefer the result from the later (higher-numbered) phase.
4. Record the conflict in `conflict_log` with both classifications and scores.

## Evidence Merging

- Evidence arrays from all phases are concatenated (union, not intersection).
- Duplicate evidence entries (same `type` + `detail`) are deduplicated.
- Source phase is tagged on each evidence item: `{"phase": 2, "type": "import_check", "detail": "..."}`.

## Output Schema

```json
{
  "file_path": "string",
  "classification": "string",
  "confidence": "float (0.0-1.0)",
  "source_phase": "int",
  "evidence": [{"phase": "int", "type": "string", "detail": "string"}],
  "conflict_resolved": "bool"
}
```

## Constraints

- Engine must process all files from all phases in a single pass.
- No file from any phase input may be silently dropped.
- Conflict log must be available as a separate output artifact.
