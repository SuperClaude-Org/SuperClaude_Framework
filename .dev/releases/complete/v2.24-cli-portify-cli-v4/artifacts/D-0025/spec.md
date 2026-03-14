# D-0025: --dry-run Halt Logic

## Deliverable

`--dry-run` halt logic integrated into `design_pipeline` step.

## Implementation

When `config.dry_run` is True:
1. After subprocess execution, emits `dry_run` contract via `build_dry_run_contract()`
2. Contract marks phases 3-4 as `skipped` per SC-011
3. Returns `PortifyStepResult` with `SKIPPED` status
4. Prints contract JSON to stdout

## Verification

- `TestDesignPipelineDryRun::test_dry_run_emits_contract` - verifies contract emission
- `TestDesignPipelineDryRun::test_dry_run_marks_phases_skipped` - verifies phase status
