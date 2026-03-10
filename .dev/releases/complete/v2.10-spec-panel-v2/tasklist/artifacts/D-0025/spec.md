# D-0025: Auto-Suggestion Heuristic FR-16

## Deliverable
Auto-suggestion heuristic FR-16 in `spec-panel.md`: triggers recommendation (not forced activation) when specification meets trigger conditions.

## Evidence

### Location
`src/superclaude/commands/spec-panel.md`, Correctness Focus > Auto-Suggestion paragraph

### Trigger Conditions (FR-16)
1. Specification introduces **3+ mutable state variables**
2. Specification contains **guard conditions with numeric thresholds**
3. Specification describes **pipeline/filter operations**

### Advisory Nature
- Suggestion is **advisory-only**: recommendation appears in panel output
- Panel does NOT force-activate `--focus correctness`
- User retains full control over focus mode selection

### False Positive Rate Target
- NFR-8: target false positive rate <30%
- Measurement deferred to Gate B (T05.02) per roadmap

### AC-10 / AC-11 Scenario Verification
- **AC-10 (should trigger)**: A specification with 4 mutable state variables, a `threshold > 0` guard, and a map/filter pipeline would trigger all three conditions -- auto-suggestion fires correctly
- **AC-11 (should not trigger)**: A simple CRUD specification with no mutable state tracking, no numeric guards, and no pipeline operations -- no trigger conditions met, suggestion does not fire

## Notes
The heuristic is specified at the specification level (not code level). Implementation as executable logic would require a future code milestone. The current deliverable is the specification of the heuristic behavior in spec-panel.md.

## Traceability
- Roadmap Item: R-026
- Task: T04.04
- Deliverable: D-0025
