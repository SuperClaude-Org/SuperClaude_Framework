# D-0012: Monorepo-Aware Batch Decomposition Specification

## Module
`src/superclaude/cli/audit/batch_decomposer.py`

## Segment Detection
Detects monorepo segments via workspace config markers (`package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `setup.py`, `pom.xml`, `build.gradle`) under monorepo root directories (`packages/`, `apps/`, `services/`, `modules/`, `libs/`, `crates/`).

Files not under a detected segment belong to `__root__`.

## Batch Rules
- No batch contains files from different segments (segment isolation)
- Batch sizes capped at `max_batch_size` (default: 50)
- Each batch includes: batch_id, segment, file_count, estimated_tokens, files list

## Manifest Format
```json
{
  "batch_count": 3,
  "total_files": 100,
  "max_batch_size": 50,
  "segments_detected": ["packages/auth", "packages/ui", "__root__"],
  "batches": [{"batch_id": "B-0001", "segment": "packages/auth", ...}]
}
```
