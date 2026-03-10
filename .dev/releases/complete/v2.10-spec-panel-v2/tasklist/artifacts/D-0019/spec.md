# D-0019: --focus correctness Flag Definition

## Deliverable
`--focus correctness` flag added to Focus Areas section of `spec-panel.md` per FR-12, targeting execution correctness of stateful specifications.

## Evidence

### Usage Line Update
- **Location**: `src/superclaude/commands/spec-panel.md` line 20
- **Change**: Added `correctness` to focus options: `--focus requirements|architecture|testing|compliance|correctness`

### Correctness Focus Subsection
- **Location**: `src/superclaude/commands/spec-panel.md`, Focus Areas section, after Compliance Focus
- **Header**: `### Correctness Focus (--focus correctness)`
- **Analysis Areas** (5 items):
  1. Execution correctness of stateful specifications
  2. State variable lifecycle and invariant preservation
  3. Guard condition completeness and boundary behavior
  4. Pipeline data flow integrity and count conservation
  5. Degenerate input handling and edge case coverage

## Traceability
- Roadmap Item: R-020
- Task: T04.01
- Deliverable: D-0019
