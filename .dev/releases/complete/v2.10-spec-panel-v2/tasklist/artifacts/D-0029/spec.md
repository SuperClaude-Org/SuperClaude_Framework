# D-0029: Quantity Flow Diagram Output Artifact (FR-21)

## Deliverable
Quantity Flow Diagram template: shows counts at each pipeline stage, annotates which count each downstream consumer uses.

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, Review Heuristics > Pipeline Dimensional Analysis > Quantity Flow Diagram (FR-21)

### Specification
- MUST be produced when Pipeline Dimensional Analysis triggers
- Shows N in -> M out at each stage
- Annotates which count each downstream consumer uses
- Highlights divergence points (N != M)
- Uses structured text format for machine-parseability
- Template provided with Source/Stage/Consumer/MISMATCH annotation

## Traceability
- Roadmap Item: R-030
- Task: T04.05
- Deliverable: D-0029
