# Decision D-0004: Multi-Agent Mode Deferral

| Field | Value |
|---|---|
| Decision ID | D-0004 |
| Open Question | OQ-007 |
| Related Requirements | FR-012 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

FR-051.1 AC-16 references "multi-agent mode" with conservative severity resolution, but no other part of the spec defines how multi-agent mode is invoked, coordinated, or merged. Should this be implemented in v2.20?

## Decision

**Defer FR-012 multi-agent severity resolution to v2.21. No implementation in v2.20. Document the conservative merge protocol only.**

### What Is Deferred

- Multi-agent invocation mechanism
- Agent coordination protocol
- Individual agent report merging
- Severity conflict resolution logic
- `validation_complete` aggregation across agents

### What Is Documented (v2.20)

The conservative merge protocol is documented as a design specification for v2.21 implementation:

1. **Severity Resolution**: When multiple agents report different severity levels for the same deviation, the highest stated severity wins.
2. **Validation Status**: `validation_complete: false` if any single agent fails or does not complete.
3. **Report Merging**: Individual agent deviation reports are union-merged; duplicate deviations (same ID) use the highest severity.

### No Partial Implementation

No code, no interfaces, no stubs, and no feature flags for multi-agent mode exist in v2.20. The single-agent pipeline is the only supported execution mode.

## Rationale

- The spec provides insufficient detail for reliable multi-agent implementation (no invocation API, no coordination protocol).
- Partial implementation would introduce dead code and untestable paths.
- Deferral reduces v2.20 scope and complexity without affecting single-agent functionality.
- The documented protocol provides a clear starting point for v2.21 design.

## Impacts

- **FR-012**: Explicitly deferred to v2.21. No v2.20 code references FR-012.
- **v2.20 scope**: Reduced complexity; single-agent pipeline only.
- **v2.21 planning**: Conservative merge protocol is pre-documented as a design input.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-007 | Defer to v2.21; document conservative merge protocol only | FR-012 |
