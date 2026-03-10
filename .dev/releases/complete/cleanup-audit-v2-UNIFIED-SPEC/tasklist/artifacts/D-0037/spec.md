# D-0037: Resume Semantics Specification

**Task**: T04.11 — Resume Semantics
**Status**: Complete

## Purpose

Define how audit runs can be resumed after interruption at phase or batch level.

## Resume Entry Points

### Phase-Level Resume

- Resume from the beginning of a specific phase.
- All results from prior completed phases are retained.
- The resumed phase re-processes all its files from scratch.
- Flag: `--resume-from phase_N`

### Batch-Level Resume

- Resume from a specific batch within a phase.
- Results from prior batches in the same phase are retained.
- Only unprocessed batches are executed.
- Flag: `--resume-from phase_N:batch_M`

## Result Merging Logic

1. Load persisted results from the checkpoint file.
2. Execute remaining phases/batches.
3. Merge new results into existing results.
4. Deduplication: if a `file_path` exists in both old and new results, the new result wins.

## Deduplication by file_path

- `file_path` is the dedup key (normalized, absolute).
- New classification replaces old classification for the same file.
- Evidence is replaced (not merged) on re-processing.

## Checkpoint File

- Written after each completed batch.
- Contains: phase/batch index, accumulated results, budget state, degradation state.
- Format: JSON, one file per run (`checkpoint_{run_id}.json`).

## Constraints

- Resume requires a valid checkpoint file; missing file causes a clear error.
- Resume does not re-validate already-consolidated results.
- Budget accounting continues from checkpoint state.
