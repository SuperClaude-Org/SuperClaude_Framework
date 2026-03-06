# Refactoring Plan: Merge Variant A Strengths into Variant B Base

## Overview
- **Base**: Variant B (Per-Task Subprocess with Turn-Budget Reimbursement)
- **Incorporated from**: Variant A (Per-Phase Subprocess)
- **Planned changes**: 5
- **Changes NOT being made**: 2
- **Overall risk**: Low-Medium (all changes are additive to the base)
- **Review**: Auto-approved

---

## Planned Changes

### Change #1: Add error_max_turns Detection (from U-002)
- **Source**: Variant A, Section 3.2
- **Target**: New subsection in merged Section 3 (after "Structural Elimination")
- **Integration approach**: APPEND — add as defense-in-depth mechanism
- **Rationale**: Variant B's advocate acknowledged in Round 2 that this is "genuinely valuable and orthogonal." Even with per-task subprocess, detecting error_max_turns provides explicit confirmation of WHY a subprocess exited. This strengthens the runner's diagnostic capability beyond binary "exited/didn't exit."
- **Risk**: Low (additive, no modification to existing content)

### Change #2: Add Staged Adoption Strategy
- **Source**: Variant A Round 2 new evidence (incremental improvement path) + Section 7 (implementation timeline)
- **Target**: New Section 7.1 "Staged Delivery Plan" in merged output
- **Integration approach**: INSERT — new subsection before implementation table
- **Rationale**: Variant A's strongest practical argument is speed-to-value. A staged approach captures this: ship TurnLedger + error_max_turns in 1 week (immediate value), then per-task migration in 3-4 weeks (structural value). This also addresses Variant B's acknowledged C-003 weakness (implementation complexity).
- **Risk**: Low (additive, provides migration path)

### Change #3: Strengthen Context Injection Design
- **Source**: Variant A, Section 4.2 (context preservation arguments) + Variant A Round 1 concession #3 (per-task accountability)
- **Target**: Merged Section 5.1 (context fragmentation weakness)
- **Integration approach**: MODIFY — expand the existing mitigation with more specific design
- **Rationale**: Variant A won diff point X-001 (context fragmentation) at 65% confidence. The concern is legitimate. The merged output should strengthen the context injection design beyond "80-90% of benefit" hand-waving, with specific mechanisms for common inter-task dependencies (test writing, refactoring sequences).
- **Risk**: Medium (modifies existing content; must preserve B's core argument)

### Change #4: Add Turn Reservation as Optional Enhancement
- **Source**: Variant A, U-001 (budget - 5 concept)
- **Target**: Merged Section 2.3 (Transaction Flow Per Task), as an optional refinement
- **Integration approach**: APPEND — add note after transaction flow
- **Rationale**: Even with per-task subprocess, reserving 1-2 turns per task for output formatting is prudent. Low cost, marginal benefit, but rounds out the design.
- **Risk**: Low (additive, clearly marked as optional)

### Change #5: Add Migration Stepping Stone (Intra-Phase Checkpointing)
- **Source**: Variant A Round 2 new evidence
- **Target**: Merged Section 7.1 (Staged Delivery Plan), as Phase 1.5
- **Integration approach**: INSERT — add intermediate milestone
- **Rationale**: For teams not ready for full per-task migration, intra-phase checkpointing provides ~80% of the blast-radius benefit at ~20% of the cost. This creates a gradual adoption ramp: TurnLedger → checkpointing → per-task.
- **Risk**: Low (additive, optional intermediate step)

---

## Changes NOT Being Made

### Rejected: Context Preservation as Primary Architecture Driver
- **Diff point**: X-001
- **Variant A approach**: Full intra-phase context via shared subprocess session
- **Rationale for rejection**: While context preservation is a real benefit (Variant A won this point at 65% confidence), it does not outweigh the structural advantages of per-task isolation. Variant B's Round 2 rebuttal raised two counter-arguments: (1) context injection provides deterministic, verifiable context vs. opaque degrading session memory, and (2) the observed 6-8 turns/task from cleanup-audit-v2 data fits comfortably within per-task budgets. The merged output addresses context concerns via strengthened injection design (Change #3) rather than architectural concession.

### Rejected: Per-Phase as Default Architecture
- **Diff point**: C-001
- **Variant A approach**: Preserve per-phase subprocess as the primary model
- **Rationale for rejection**: The core architectural decision was resolved by the debate. Per-task won on 5 of 8 resolved diff points. The decisive factor is C-002 (Completion Protocol): the MaxTurn problem already materialized in production, and probabilistic mitigation was insufficient. However, per-phase is preserved as a backward-compatible fallback in the staged adoption strategy (Change #2).

---

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 error_max_turns | Low | Additive detection | Remove subsection |
| #2 Staged adoption | Low | Additive strategy | Remove subsection |
| #3 Context injection | Medium | Modifies weakness section | Revert to original B text |
| #4 Turn reservation | Low | Additive optional note | Remove note |
| #5 Migration stepping stone | Low | Additive intermediate step | Remove from staged plan |

---

## Review Status
- Approval: auto-approved
- Timestamp: 2026-03-06
