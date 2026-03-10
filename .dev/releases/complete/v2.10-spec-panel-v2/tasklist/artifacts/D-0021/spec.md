# D-0021: Modified Expert Behaviors FR-14.1 through FR-14.6

## Deliverable
All 6 expert correctness-focus behavior shifts documented as additive extensions to standard behaviors.

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, section "#### Modified Expert Behaviors Under Correctness Focus"

### Behavior Shifts Documented

| FR | Expert | Correctness Shift Summary |
|----|--------|--------------------------|
| FR-14.1 | Wiegers | Identifies implicit state assumptions; flags unspecified initial values, ranges, invariants |
| FR-14.2 | Fowler | Annotates data flow with count divergence; documents input/output counts per transformation |
| FR-14.3 | Nygard | Extends guard boundary analysis to zero/empty/null/negative inputs |
| FR-14.4 | Adzic | State-annotated Given/When/Then scenarios with degenerate input variants |
| FR-14.5 | Crispin | Boundary value test cases for every guard: below-min, at-min, typical, at-max, above-max, degenerate |
| FR-14.6 | Whittaker | All 5 attack methodologies per invariant (minimum 1 attack per methodology per invariant) |

### Verification
- [x] All 6 experts covered (Wiegers, Fowler, Nygard, Adzic, Crispin, Whittaker)
- [x] Behaviors described as additive shifts (not replacements)
- [x] Preamble states: "Standard behaviors remain unchanged"

## Traceability
- Roadmap Item: R-022
- Task: T04.02
- Deliverable: D-0021
