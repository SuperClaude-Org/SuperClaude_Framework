# D-0008: OQ Resolution Summary

**Task**: T01.09
**Roadmap Items**: R-014, R-015
**Date**: 2026-03-08

## Open Question Resolutions

### OQ-001: Spec typo — §5.3 → §11.2
- **Status**: Resolved (Non-blocking)
- **Resolution**: Confirmed as typo. Document in protocol: all section references in spec should reference by heading name, not section number, to prevent drift.

### OQ-002: TurnLedger in pipeline API
- **Status**: Resolved (Blocking)
- **Resolution**: `TurnLedger` is NOT in the pipeline API (`superclaude.cli.pipeline.models`). It exists only in `superclaude.cli.sprint.models` (line 466). Portified pipelines that need budget tracking should import from `superclaude.cli.sprint.models.TurnLedger` directly. The pipeline-spec.md reference (line ~419) correctly shows this import path. No spec change needed.

### OQ-003: --dry-run behavior
- **Status**: Resolved (Blocking)
- **Resolution**: `--dry-run` = execute Phases 0-2 only. Emit contracts (`portify-prerequisites.yaml`, `portify-analysis.yaml`), display analysis to user. No code generation (Phase 3) or integration (Phase 4). `--skip-integration` = generate code (Phase 3) but skip `main.py` wiring (Phase 4).

### OQ-004: Integration schema
- **Status**: Resolved (Blocking)
- **Resolution**: `portify-integration.yaml` schema:
  ```yaml
  schema_version: "1.0"
  phase: 4
  status: "passed" | "failed"
  timestamp: <ISO8601>
  main_py_patched: true | false
  command_registered: true | false
  test_file_generated: true | false
  smoke_test_passed: true | false
  ```

### OQ-005: batch_dynamic
- **Status**: Resolved (Non-blocking)
- **Resolution**: Set `batch_dynamic: false` always. Dynamic fan-out is unsupported. Remove the field from the contract schema; static batch sizes only.

### OQ-006: refs/analysis-protocol.md exists
- **Status**: Resolved (Non-blocking)
- **Resolution**: Confirmed. File exists at `src/superclaude/skills/sc-cli-portify/refs/analysis-protocol.md` (216 lines). Contains: discovery checklist, step decomposition algorithm, classification rubric, output format template, common workflow patterns.

### OQ-007: Approval gate mechanism
- **Status**: Resolved (Blocking)
- **Resolution**: Approval gates use TodoWrite checkpoint pattern:
  1. Write contract artifact to disk
  2. Mark TodoWrite task as "awaiting review"
  3. Present summary to user with key decisions
  4. User resumes by continuing (implicit approval) or provides overrides
  5. Protocol reads contract on resume and validates completed phases

### OQ-008: Default output path
- **Status**: Resolved (Blocking)
- **Resolution**: Default `--output` to `src/superclaude/cli/<derived_name>/` where `<derived_name>` is the kebab-case CLI name with `sc-` prefix and `-protocol` suffix stripped. This affects contract emission paths — all contracts are written to the output directory.

### OQ-009: Test file location
- **Status**: Resolved (Non-blocking)
- **Resolution**: Structural tests go to `tests/` per project convention. File named `test_<cli_name>_structure.py`. This follows the existing project pattern where all tests reside in the `tests/` directory.

### OQ-010: Step boundary algorithm
- **Status**: Resolved (Blocking for Phase 3)
- **Resolution**: The step boundary algorithm is already documented in `refs/analysis-protocol.md` under "## Step Decomposition Algorithm" → "### Identify Step Boundaries". The algorithm states a new Step starts when:
  - A new artifact is produced
  - A different agent takes over
  - The execution mode changes (sequential → parallel)
  - A quality gate must be evaluated
  - The operation type changes (analysis → generation → validation)

  No additional extraction needed — the algorithm is already explicitly documented.

## Summary

| OQ | Blocking? | Status |
|----|-----------|--------|
| OQ-001 | No | Resolved |
| OQ-002 | Yes | Resolved — TurnLedger not in pipeline API |
| OQ-003 | Yes | Resolved — dry-run = Phases 0-2 only |
| OQ-004 | Yes | Resolved — schema defined |
| OQ-005 | No | Resolved — batch_dynamic removed |
| OQ-006 | No | Resolved — file confirmed |
| OQ-007 | Yes | Resolved — TodoWrite checkpoint pattern |
| OQ-008 | Yes | Resolved — default src/superclaude/cli/<name>/ |
| OQ-009 | No | Resolved — tests/ directory |
| OQ-010 | Yes | Resolved — already in analysis-protocol.md |

**All 10 OQs resolved. Zero TBD items remain.**
