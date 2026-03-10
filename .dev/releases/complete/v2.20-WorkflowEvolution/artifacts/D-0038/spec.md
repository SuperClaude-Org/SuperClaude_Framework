---
deliverable: D-0038
task: T05.02
status: PASS
date: 2026-03-09
scope: FR-012 deferred to v2.21
---

# Multi-Agent Severity Resolution Protocol

## Status

FR-012 (multi-agent severity resolution) is **deferred to v2.21** per OQ-007
decision from T01.04. This document specifies the conservative merge protocol
for future implementation.

## Conservative Merge Protocol

### Rule 1: Highest Severity Wins

When multiple agents report severity assessments for the same deviation:

| Agent A | Agent B | Resolved Severity |
|---------|---------|-------------------|
| HIGH    | MEDIUM  | HIGH              |
| MEDIUM  | LOW     | MEDIUM            |
| HIGH    | LOW     | HIGH              |
| HIGH    | HIGH    | HIGH              |

**Rationale**: Conservative merge ensures no genuine issue is downgraded. False
positives are preferred over false negatives for safety-critical pipeline gates.

### Rule 2: validation_complete Semantics

| Condition | validation_complete |
|-----------|---------------------|
| All agents succeed | `true` |
| Any agent fails | `false` |
| Any agent times out | `false` |
| Any agent produces invalid output | `false` |

When `validation_complete: false`, the pipeline emits a **degraded** status
(not a hard failure), preserving successful agent results while clearly
flagging incomplete validation.

### Rule 3: Failure Handling

1. **Agent timeout**: Record timeout as failure; emit warning with agent ID
2. **Invalid output**: Record as failure; preserve raw output for debugging
3. **Partial results**: Merge available results; flag missing agents in report
4. **All agents fail**: Set `validation_complete: false`; `tasklist_ready: false`

### Rule 4: Merge Order

1. Collect per-agent deviation tables
2. Deduplicate by deviation ID (same upstream/downstream quote pair)
3. For duplicates: apply Rule 1 (highest severity wins)
4. For unique deviations: include as-is
5. Compute aggregate counts from merged table

## Deferral Notice

Full implementation of FR-012 multi-agent severity resolution is deferred to
**v2.21 (RoadmapRemediate)**. The current v2.20 pipeline operates in
single-agent mode for fidelity validation. This specification serves as the
design contract for the v2.21 implementation.

## References

- OQ-007: Multi-Agent Mode Specification Gap (extraction.md:393)
- T01.04: OQ-007 deferral decision
- RSK-003: False-positive regression risk (mitigated by conservative merge)
