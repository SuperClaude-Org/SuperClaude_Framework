# D-0027: 4-Step Pipeline Analysis Process (FR-18)

## Deliverable
4-step analysis process: Pipeline Detection (Fowler leads), Quantity Annotation (N in/M out), Downstream Tracing (verify count usage), Consistency Check (flag mismatches).

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, Review Heuristics > Pipeline Dimensional Analysis > 4-Step Analysis Process (FR-18)

### Steps
1. **Pipeline Detection** -- Fowler leads: identify all multi-stage data flows, document topology
2. **Quantity Annotation** -- Fowler leads: annotate N in / M out per stage, flag N != M
3. **Downstream Tracing** -- Fowler + Whittaker: trace consumers of each divergence point, verify count assumptions
4. **Consistency Check** -- Whittaker leads: verify spec handles each divergence, flag count conservation assumptions

### Expert Assignments
- Fowler: identification, annotation (Steps 1-2), co-leads tracing (Step 3)
- Whittaker: attacks divergence points (Step 3), leads consistency check (Step 4)

## Traceability
- Roadmap Item: R-028
- Task: T04.05
- Deliverable: D-0027
