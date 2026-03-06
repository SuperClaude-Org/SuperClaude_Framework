# Refactoring Plan: Merge V2 Strengths into V1 Base

## Overview
- **Base**: Variant 1 (opus:scribe) — combined score 0.956
- **Incorporating from**: Variant 2 (haiku:scribe) — selected strengths
- **Changes planned**: 4
- **Changes NOT being made**: 3
- **Risk**: Low-Medium overall
- **Review status**: Auto-approved

---

## Planned Changes

### Change 1: Restructure M3 into Gate A Validation Milestone
**Source**: Variant 2, Section 2 (Milestone Plan) and Section 3 (M3 details)
**Target location**: V1 Phase 2 section — currently ends at M3 (Boundary Table) with validation embedded in ACs
**Integration approach**: Insert dedicated Gate A milestone — rename current M6 to M7, renumber Phase 3 milestones accordingly. Add Gate A as M4 (after Phase 2 M3 Boundary Table). Gate A contains V2's evidence pack.

**Evidence pack from V2 to incorporate**:
- v0.04 run logs
- Overhead report
- Artifact completeness report
- Explicit sign-off for Phase 3 entry

**Rationale**: S-002/C-001 (95% confidence). Interleaved validation is protocol-required for MEDIUM complexity. V1 conceded this in Round 1.
**Risk**: Low — additive milestone; no existing content deleted

---

### Change 2: Add Gate B Evidence Pack to Final Validation Milestone
**Source**: Variant 2, Section 3 (M6 details), Section 5 (Validation checkpoints table)
**Target location**: V1 M6 (Validation and Release) — currently lacks explicit evidence pack and rollback plan requirement
**Integration approach**: Append to existing M6 Deliverables list:
- Evidence pack: "end-to-end metrics dashboard, risk review, integration verification"
- Gate B designation added to milestone heading
- Explicit "go/no-go decision and rollback plan" acceptance criterion
- Add "Validation-first checkpoints" summary table after dependency graph

**Rationale**: U-004 (92% confidence). Gate evidence packs make go/no-go decisions concrete and auditable.
**Risk**: Low — additive content to existing section

---

### Change 3: Add M4+M5 Parallelism Explicit Note to Dependency Section
**Source**: Variant 1 (already present in V1 base), but needs explicit expression in dependency graph and prose
**Target location**: Phase 3 section intro and dependency graph
**Integration approach**: The V1 base already has "M4 and M5 share the same prerequisites and have no dependency on each other. They can execute in parallel within Phase 3." Confirm this is retained and that the milestone renumbering (due to Change 1) preserves the parallelism reference.
**Rationale**: C-002/X-001 (80% confidence). V2 conceded in Round 2.
**Risk**: Low — preservation check only

---

### Change 4: Add Validation-First Checkpoints Summary Table
**Source**: Variant 2, Section 5
**Target location**: After Dependency Graph section in V1
**Integration approach**: Insert table after the dependency graph:

| Gate | Trigger | Required Evidence | Exit Condition |
|------|---------|-------------------|----------------|
| Gate A (M4) | End of M3 (Boundary Table complete) | v0.04 run logs, overhead report, artifact completeness report | Phase 3 authorized |
| Gate B (M7) | End of M5+M6 (Phase 3 complete) | End-to-end metrics dashboard, risk review, integration verification | Release go/no-go |

**Rationale**: V2's structured checkpoint table is a useful navigation aid absent from V1.
**Risk**: Low — additive content

---

## Changes NOT Being Made

| Diff Point | V2 Approach | Reason Rejected |
|------------|-------------|-----------------|
| S-001/C-003 | Consolidate Phase 1 into single M1 | V2 advocate conceded in Round 3. V1's separation of persona definition (M1) from panel integration (M2) is better engineering — enables isolated review and rollback. |
| S-004 | Table-first lean-prose structure | V1's narrative phase overviews provide richer stakeholder context (65% confidence). The prose sections explain WHY each phase exists, not just WHAT it does. This is appropriate for a planning artifact. |
| C-002 (wrong direction) | M5 sequential dependency on M4 | V2 conceded in Round 2. M4 and M5 are parallel in Phase 3. |
