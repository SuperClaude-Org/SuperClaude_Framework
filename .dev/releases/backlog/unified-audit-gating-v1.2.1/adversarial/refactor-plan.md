# Refactoring Plan: Merge Into V2 (QA) Base

**Pipeline**: Adversarial 3-variant merge
**Timestamp**: 2026-03-03T00:00:00Z
**Base variant**: V2 (sonnet:qa) -- score 0.9488
**Source variants**: V1 (opus:architect), V3 (haiku:analyzer)
**Debate convergence**: 92%

---

## Integrations from V1 (opus:architect)

### INT-01: Closed-World State Machine Enforcement (U-001)

**Source**: V1 M1.5 risk mitigation, M2.2 validator design
**Target**: V2 M2 deliverables
**Risk level**: Low (additive, no existing deliverable modified)

**Change**: Add to M2 deliverables a design constraint specifying that the transition validator uses a closed-world assumption: only listed transitions are legal, all others are illegal by default. Any new state added to the state machine in the future is automatically blocked until its transitions are explicitly declared.

**Specific insertion**: Add to M2-D2 acceptance criteria: "Transition validator uses closed-world assumption: only transitions explicitly listed in the transition table are legal. All other (from_state, to_state) pairs return allowed=False. Test: inject a synthetic state not in the table; validator returns allowed=False."

**Rationale**: Eliminates an entire class of bypass vulnerabilities where a new state is added without declaring transitions, creating an implicit path from failed to completed. The closed-world approach makes the absence of a transition declaration equivalent to a prohibition. No other variant makes this architectural decision explicit.

---

### INT-02: Compile-Time Release Override Prohibition (U-002)

**Source**: V1 M1.2 acceptance criteria
**Target**: V2 M2 deliverables
**Risk level**: Low (additive, strengthens existing M4-D7)

**Change**: Add to M2 deliverables a requirement that OverrideRecord validation rejects release scope at construction time (object instantiation), not only at transition validation time. This provides defense-in-depth: even if the transition validator has a bug that fails to check scope, the OverrideRecord itself refuses to be created with scope=release.

**Specific insertion**: Add to M2-D1 (or as new M2-D8): "OverrideRecord constructor/validator rejects scope='release' at instantiation time. Test: attempt to create OverrideRecord with scope='release' and all other fields valid; constructor raises ValueError or equivalent. This check is independent of and in addition to the transition validator's release override prohibition."

**Rationale**: Defense-in-depth at the data model layer. V2's M4-D7 already tests that the transition validator rejects release overrides, but V1's approach catches the invalid record before it even reaches the validator. Two independent enforcement layers.

---

## Integrations from V3 (haiku:analyzer)

### INT-03: Fault-Injection Suite and Deadlock-Resistance Argument (U-005)

**Source**: V3 M3 deliverables (D3.2 deadlock resistance, D3.5 fault-injection suite)
**Target**: V2 M4 deliverables
**Risk level**: Medium (adds deliverables to an already large milestone)

**Change**: Add two explicit deliverables to V2's M4 (Runtime Controls, Override Governance, and Override Test Suite):

1. **M4-D12 Fault-injection suite**: Transient, system, and timeout fault tests that prove lease/heartbeat/retry controls work under adversarial conditions. Pass threshold must be met before any rollout milestone (M6) can begin. Tests include: inject heartbeat failure mid-run, inject lease expiry during evaluation, inject retry with concurrent heartbeat, inject system fault during state transition.

2. **M4-D13 Deadlock-resistance formal argument**: Documented proof-by-construction that no cycle exists in the state machine that can be entered without a bounded exit. Every `running` state has a timeout exit. Every `failed` state has either retry (bounded) or terminal. Retry budget is monotonically decreasing. Supported by property-based test with random state sequences (minimum 10K sequences, all must terminate).

**Rationale**: V3's M3 isolates reliability hardening as a dedicated milestone. Within V2's structure, M4 already covers runtime controls (lease/heartbeat/retry), so the fault-injection and deadlock-resistance work is a natural extension. Adding these as explicit deliverables ensures reliability is proven before rollout, matching V3's intent without adding a new milestone.

---

### INT-04: Rollout Sub-Phase Granularity (U-006)

**Source**: V3 M4/M5/M6 structure (three separate rollout gate milestones)
**Target**: V2 M6 structure
**Risk level**: Low (restructures existing deliverables, does not add milestones)

**Change**: Restructure V2's M6 (Rollout Validation, Rollback Drill, and Phase Promotion Gate) into two explicit sub-phases with ordering constraints:

**Sub-Phase A: Shadow Deployment and Shadow-to-Soft Gate** (M6-D1 through M6-D7, M6-D9)
- Shadow mode produces metrics without blocking (M6-D1)
- Two consecutive shadow windows completed (M6-D6)
- Threshold calibration signed off (M6-D7)
- Shadow-to-Soft promotion gate sign-off (M6-D9)
- **Gate constraint**: M6-D9 must be signed off before any Sub-Phase B deliverable can begin

**Sub-Phase B: Soft Enforcement, Rollback Drill, and Soft-to-Full Gate** (M6-D2, M6-D3, M6-D8, M6-D10)
- Soft mode enforces selective profiles (M6-D2)
- Full mode enforces globally (M6-D3)
- Rollback drill executed and documented (M6-D8)
- Soft-to-Full promotion gate sign-off (M6-D10)
- **Gate constraint**: M6-D8 (rollback drill) must pass before M6-D10 can be signed off

**Rationale**: V3 splits rollout into three milestones (M4/M5/M6), providing the most granular phase-gate tracking. However, this consumes 50% of the milestone budget on rollout alone. The sub-phase approach provides equivalent ordering constraints within a single milestone, matching V3's intent (no Soft enforcement before Shadow-to-Soft is approved; no Full enforcement before rollback drill passes) without adding milestones.

---

## Preservations (Already in V2 Base)

### PRES-01: Adversarial Release Override Test (U-003)

**Location**: V2 M4-D7
**Status**: Already present. No change needed.
**Note**: This is the adversarial test that supplies a fully valid OverrideRecord at release scope and asserts it is still rejected. The dangerous failure mode (valid record + forbidden scope) is covered.

### PRES-02: Sprint CLI Regression Gate (U-004)

**Location**: V2 M5 (entire milestone)
**Status**: Already present. No change needed.
**Note**: Standalone milestone with baseline audit, PhaseStatus backward-compatibility assertions, guard isolation test, and zero-failure gate.

---

## Changes NOT Being Made

### REJECT-01: Architect's M1 = Lock Data Contracts Approach

**Source**: V1 M1 structure
**Rationale for rejection**: V2's M1 = Blocker Resolution is superior for testability. The debate resolved X-001 in favor of QA/Analyzer position (95% convergence). The Architect formally conceded that front-loading blocker resolution eliminates the false-confidence problem of parametrized tests with provisional values. Blocker closure must precede contract work to avoid provisional implementations.

### REJECT-02: Analyzer's 3-Milestone Rollout Split

**Source**: V3 M4/M5/M6 structure
**Rationale for rejection**: Would require adding a 7th milestone or compressing implementation into too few milestones. The Analyzer conceded this in Round 2 of debate (modified position). The sub-phase approach within M6 (INT-04) captures the granularity benefit without the milestone overhead.

### REJECT-03: Architect's DAG Dependency Graph

**Source**: V1 dependency graph (M2 branches to M3 and M4 in parallel)
**Rationale for rejection**: V2's linear chain (M1->M2->M3->M4->M5->M6) is simpler and matches the debate consensus. The parallel opportunity (M3 and M4 overlap) saves calendar time but creates coordination risk: M4 depends on M3 for runtime control integration, so the parallelism is limited in practice.

---

## Integration Summary

| ID | Source | Target | Change Type | Risk |
|----|--------|--------|-------------|------|
| INT-01 | V1 U-001 | V2 M2 | Add design constraint + acceptance criterion | Low |
| INT-02 | V1 U-002 | V2 M2 | Add deliverable/acceptance criterion | Low |
| INT-03 | V3 U-005 | V2 M4 | Add 2 deliverables (M4-D12, M4-D13) | Medium |
| INT-04 | V3 U-006 | V2 M6 | Restructure into sub-phases with ordering | Low |
| PRES-01 | V2 U-003 | V2 M4-D7 | No change (preserve) | None |
| PRES-02 | V2 U-004 | V2 M5 | No change (preserve) | None |

**Total new deliverables**: 2 (M4-D12, M4-D13)
**Total modified deliverables**: 3 (M2-D2 or M2-D1, M6 sub-phase restructure)
**Total milestone count change**: 0 (remains 6)
