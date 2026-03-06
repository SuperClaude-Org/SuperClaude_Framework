# D-0024: Pipeline Flow Diagram Output Specification

## Deliverable
Pipeline Flow Diagram output specification: annotated with counts at each stage when pipelines are present per FR-15.3.

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, Correctness Focus > Mandatory Outputs

### Specification
- Pipeline Flow Diagram is produced when pipelines are present in the specification under review
- Diagram is annotated with counts at each pipeline stage (N in / M out)
- Purpose: visualize data flow integrity and identify count divergence points

### Activation Conditions
- Active when `--focus correctness` is specified AND specification contains pipeline/filter operations
- Not produced for non-pipeline specifications (no overhead when not applicable)

## Traceability
- Roadmap Item: R-025
- Task: T04.03
- Deliverable: D-0024
