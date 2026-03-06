# D-0033: Degradation Sequence Specification

**Task**: T04.07 — Graceful Degradation Sequence
**Status**: Complete

## Purpose

Define ordered degradation levels that reduce analysis depth while preserving valid output.

## Degradation Levels

| Level | Name | Activation | Behavior | Output Validity |
|-------|------|------------|----------|-----------------|
| L1 | Reduce Detail | 90% phase budget | Drop per-file evidence details; keep classification + confidence | Full |
| L2 | Skip Cross-Refs | 92% phase budget | Skip cross-reference analysis; use phase-local data only | Full |
| L3 | Batch Increase | 95% phase budget | Double batch size to reduce overhead; accept lower granularity | Full |
| L4 | Heuristic Only | 97% phase budget | Use heuristic classifiers only; skip LLM-based analysis | Partial (flagged) |
| L5 | Emergency Stop | 100% phase budget | Halt phase; finalize with available data | Partial (flagged) |

## Activation Order

- Levels activate sequentially: L1 before L2 before L3, etc.
- No level may be skipped (L1 must be active before L2 activates).
- Each activation is logged with timestamp and budget state.

## Valid Output at Each Level

- **L1-L3**: Output is complete and unflagged. All mandated report sections present.
- **L4**: Output is complete but flagged with `"degraded": true, "degradation_level": 4`.
- **L5**: Output includes only files processed before halt. Flagged with `"partial": true`.

## Constraints

- Degradation is one-directional within a phase (no recovery to lower level).
- Override order (D-0034) does not affect degradation sequence.
- Degradation state is included in budget persistence for resume.
