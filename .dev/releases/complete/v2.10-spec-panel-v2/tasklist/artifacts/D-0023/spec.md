# D-0023: Guard Condition Boundary Table Mandatory Under Correctness Focus

## Deliverable
Guard Condition Boundary Table specified as always-produced (not trigger-gated) when `--focus correctness` is active per FR-15.2.

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, Correctness Focus > Mandatory Outputs

### Specification
- Under `--focus correctness`, the boundary table is **always produced** regardless of trigger conditions
- This overrides the standard trigger-gating from Phase 2 (which requires conditional logic, threshold checks, etc.)
- Standard (non-correctness) panel behavior is **unchanged**: boundary table remains trigger-gated per Phase 2 Mandatory Output Artifacts section

### Scope Verification
- [x] Override correctly scoped to `--focus correctness` only
- [x] Standard panel behavior unchanged
- [x] Phase 2 boundary table template (7-column format) reused, not redefined

## Traceability
- Roadmap Item: R-024
- Task: T04.03
- Deliverable: D-0023
