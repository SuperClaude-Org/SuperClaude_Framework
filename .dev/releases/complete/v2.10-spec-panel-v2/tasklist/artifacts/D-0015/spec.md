# D-0015 Evidence: Downstream Propagation Format for sc:adversarial AD-1

## Deliverable
Downstream Propagation section in boundary table documentation specifying machine-parseable markdown format for AD-1 consumer, with format documented for invariant probe input.

## Verification

### Section Location
- `#### Downstream Propagation` subsection within Guard Condition Boundary Table

### Format Specification
- Format type: Structured markdown table (not prose) per NFR-5
- Consumer named: `sc:adversarial` AD-1 (invariant probe round)
- Format described: "Structured markdown table with the 7 columns defined above"

### GAP-to-Priority-Target Mapping
- Text: "Entries with Status = 'GAP' become priority targets for AD-1 invariant probing. GAP entries are propagated as high-priority invariant candidates."
- Mapping is explicit and concrete

### Deferred Wiring
- Text: "SC-4 to RM-3 and SP-2 to RM-2 integration wiring is deferred to Phase 4 (T04.05)."
- Correctly defers M6 wiring per tasklist dependencies

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| Machine-parseable markdown format specified | PASS |
| AD-1 named as consumer | PASS |
| GAP-to-priority-target mapping documented | PASS |
| Structured format per NFR-5 | PASS |
| Traceable to R-016 | PASS |

## Traceability
- Roadmap Item: R-016
- Task: T02.07
- Deliverable: D-0015
