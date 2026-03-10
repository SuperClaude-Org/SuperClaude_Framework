# Decision D-0001: Cross-Reference Strictness Rollout

| Field | Value |
|---|---|
| Decision ID | D-0001 |
| Open Question | OQ-001 |
| Related Requirements | FR-019 |
| Risk Mitigation | RSK-003 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

Should `_cross_refs_resolve()` fix be warning-first (log but don't block) for one release cycle before becoming blocking? Existing roadmaps may have dangling references.

## Decision

**Warning-first for one release cycle, then blocking enforcement.**

### Rollout Phases

1. **Phase A — Warning Mode (v2.20)**: `_cross_refs_resolve()` logs all unresolved cross-references as warnings. The pipeline continues execution; MERGE_GATE is not blocked by dangling references. Warning output includes: reference text, expected anchor, source file, and line number.

2. **Phase B — Blocking Mode (v2.21)**: `_cross_refs_resolve()` returns `False` for any unresolved cross-reference. MERGE_GATE blocks pipeline progression. All existing artifacts must be updated to resolve dangling references before this release.

### Warning-First Duration

One full release cycle (v2.20). Blocking enforcement begins with v2.21.

## Rationale

- Existing roadmaps in `.dev/releases/complete/` may contain dangling cross-references that were never validated. Immediate blocking would cause false-positive pipeline failures (RSK-003).
- Warning-first provides a migration window: teams can audit and fix existing artifacts during v2.20 without breaking workflows.
- The warning output format is designed to be machine-parseable, enabling automated remediation tooling.

## Impacts

- **FR-019**: Implementation must support a `strict_mode: bool` parameter (default `False` in v2.20, `True` in v2.21).
- **RSK-003**: Fully mitigated by the warning-first approach — no existing valid roadmaps will fail MERGE_GATE.
- **Downstream**: Gate logic in `roadmap/gates.py` needs a configurable enforcement level.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-001 | Warning-first for v2.20, blocking in v2.21 | FR-019 |
