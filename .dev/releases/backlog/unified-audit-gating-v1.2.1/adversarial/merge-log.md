# Merge Log: Unified Audit Gating System v1.2.1

**Pipeline**: Adversarial 3-variant merge
**Timestamp**: 2026-03-03T00:00:00Z
**Base variant**: V2 (sonnet:qa) -- score 0.9488
**Output file**: `adversarial/merged-roadmap.md`

---

## Changes Applied

### MERGE-001: M2-D2 Enhanced with Closed-World Assumption

**Source**: V1 (opus:architect) U-001
**Target section**: M2 Deliverables, M2-D2 acceptance criteria
**Change type**: Enhancement (added constraint to existing deliverable)

**Before** (V2 original):
> A callable `validate_transition(scope, from_state, to_state, override_record=None)` exists; returns (allowed: bool, reason: str); raises no exceptions for any combination of valid enum values

**After** (merged):
> A callable `validate_transition(scope, from_state, to_state, override_record=None)` exists; returns (allowed: bool, reason: str); raises no exceptions for any combination of valid enum values; **uses closed-world assumption: only transitions explicitly listed in the transition table return allowed=True; all other pairs return allowed=False**; test: inject a synthetic state not in the table, validator returns allowed=False

**Also updated**: M2 Objective paragraph to state the closed-world assumption explicitly.

---

### MERGE-002: M2-D8 Added (Compile-Time Release Override Prohibition)

**Source**: V1 (opus:architect) U-002
**Target section**: M2 Deliverables
**Change type**: New deliverable added

**Content**:
> M2-D8: OverrideRecord constructor/validator rejects scope='release' at instantiation time; test: attempt to create OverrideRecord with scope='release' and all other fields valid; constructor raises ValueError or equivalent; this check is independent of and in addition to the transition validator's release override prohibition (M2-D2)

**Also updated**: M2 Objective paragraph to state defense-in-depth at construction time.

---

### MERGE-003: M4-D12 Added (Fault-Injection Suite)

**Source**: V3 (haiku:analyzer) U-005, drawing from V3 M3-D3.5 and M3-D3.2
**Target section**: M4 Deliverables
**Change type**: New deliverable added

**Content**:
> M4-D12: Fault-injection suite. Transient, system, and timeout fault tests that prove lease/heartbeat/retry controls work under adversarial conditions: (1) inject heartbeat failure mid-run; (2) inject lease expiry during evaluation; (3) inject retry with concurrent heartbeat; (4) inject system fault during state transition. Pass threshold must be met before M6 can begin.

**Also updated**: M4 Objective paragraph, M4 Dependencies (M4-D12 depends on M1-D2), M4 Risk Assessment (added timing risk for fault-injection tests).

---

### MERGE-004: M4-D13 Added (Deadlock-Resistance Formal Argument)

**Source**: V3 (haiku:analyzer) U-005, drawing from V3 M3-D3.2
**Target section**: M4 Deliverables
**Change type**: New deliverable added

**Content**:
> M4-D13: Deadlock-resistance formal argument. Documented proof-by-construction that no cycle exists in the state machine that can be entered without a bounded exit. Every `running` state has a timeout exit; every `failed` state has either retry (bounded) or terminal; retry budget is monotonically decreasing. Supported by property-based test with random state sequences (minimum 10K sequences, all must terminate).

**Also updated**: M4 Risk Assessment (added risk for concurrent multi-entity scenarios).

---

### MERGE-005: M6 Restructured into Sub-Phases

**Source**: V3 (haiku:analyzer) U-006
**Target section**: M6 Deliverables
**Change type**: Structural reorganization (no content removed; ordering constraints added)

**Before** (V2 original): M6 deliverables listed as a flat table (M6-D1 through M6-D10).

**After** (merged): M6 deliverables organized into two sub-phases:
- **Sub-Phase A (Shadow + Shadow-to-Soft Gate)**: M6-D1, M6-D5, M6-D6, M6-D7, M6-D9
  - Gate constraint: M6-D9 must be signed off before Sub-Phase B begins
- **Sub-Phase B (Soft/Full + Rollback Drill + Soft-to-Full Gate)**: M6-D2, M6-D3, M6-D4, M6-D8, M6-D10
  - Gate constraint: M6-D8 must pass before M6-D10 can be signed off

**Also updated**: M6 Objective paragraph, M6 Risk Assessment (added sub-phase timing risk).

---

### MERGE-006: Risk Register Extended

**Source**: V1 U-001 (R11), V3 U-005 (R12, R13)
**Target section**: Risk Register
**Change type**: New risks added

**Added**:
- R11: Closed-world assumption creates friction when adding new states (from V1 U-001)
- R12: Fault-injection tests produce non-deterministic results due to timing (from V3 U-005)
- R13: Deadlock-resistance argument incomplete for concurrent multi-entity scenarios (from V3 U-005)

---

### MERGE-007: Decision Summary Extended

**Source**: V1 U-001, V1 U-002, V3 U-005, V3 U-006
**Target section**: Decision Summary
**Change type**: New decisions added

**Added decisions**:
- Closed-world state machine assumption (from V1 U-001)
- Compile-time release override prohibition (from V1 U-002)
- Rollout sub-phase ordering (from V3 U-006)
- Fault-injection as explicit M4 deliverable (from V3 U-005)

---

### MERGE-008: Success Criteria Extended

**Source**: V1 U-001 (SC-4, SC-5), V3 U-005 (SC-11, SC-12), V3 U-006 (SC-20)
**Target section**: Success Criteria
**Change type**: New criteria added

**Added**:
- SC-4: Closed-world enforcement test (from V1 U-001)
- SC-5: OverrideRecord release rejection at construction time (from V1 U-002)
- SC-11: Fault-injection suite pass (from V3 U-005)
- SC-12: Deadlock-resistance 10K sequence test (from V3 U-005)
- SC-20: Sub-Phase A signed off before Sub-Phase B begins (from V3 U-006)

---

### MERGE-009: M2 Risk Assessment Extended

**Source**: V1 U-001
**Target section**: M2 Risk Assessment
**Change type**: New risk added

**Added**: Risk that closed-world assumption creates false negatives for legitimate new transitions added later. Mitigation: document requirement that any new state MUST be accompanied by explicit transition declarations.

---

### MERGE-010: M4 Risk Assessment Extended

**Source**: V3 U-005
**Target section**: M4 Risk Assessment
**Change type**: New risks added

**Added**:
- Fault-injection tests create non-deterministic timing interactions. Mitigation: deterministic mock-based fault injection.
- Deadlock-resistance proof incomplete for concurrent gate runs. Mitigation: scope formal argument to single-entity paths.

---

### MERGE-011: Provenance Annotations Added

**Source**: Orchestrator
**Target section**: All sections
**Change type**: HTML comments added throughout

All sections in the merged roadmap include `<!-- Provenance: ... -->` comments indicating whether content is from the QA base (V2) unchanged, or enhanced/added from V1 or V3, with specific U-### references.

---

## Changes NOT Applied

| ID | Source | Description | Reason |
|----|--------|-------------|--------|
| SKIP-001 | V1 | M1 = Lock Data Contracts (contracts before blockers) | Debate resolved X-001: blocker resolution must precede contracts. Architect conceded in Round 2. |
| SKIP-002 | V3 | Three separate rollout milestones (M4/M5/M6) | Consumes 50% of milestone budget. Analyzer conceded in Round 2. Sub-phase approach (MERGE-005) captures the benefit. |
| SKIP-003 | V1 | DAG dependency graph (M3/M4 parallel) | V2 linear chain is simpler and matches debate consensus. Parallelism limited in practice since M4 depends on M3 for runtime integration. |
| SKIP-004 | V1 | Per-deliverable "Reqs Covered" column | V1's strongest feature but not integrated because the QA base uses acceptance-gate-level requirement traceability which is adequate. Could be added as a future enhancement. |

---

## Verification Summary

| Check | Status | Notes |
|-------|--------|-------|
| All V2 base deliverables preserved | PASS | M1-D1 through M6-D10 all present |
| V1 U-001 integrated | PASS | M2-D2 enhanced, M2 objective updated, SC-4 added |
| V1 U-002 integrated | PASS | M2-D8 added, M2 objective updated, SC-5 added |
| V3 U-005 integrated | PASS | M4-D12 and M4-D13 added, M4 objective updated, SC-11 and SC-12 added |
| V3 U-006 integrated | PASS | M6 restructured into sub-phases, SC-20 added |
| V2 U-003 preserved | PASS | M4-D7 unchanged |
| V2 U-004 preserved | PASS | M5 milestone unchanged |
| Risk register updated | PASS | R11, R12, R13 added |
| Decision summary updated | PASS | 4 new decisions added |
| Success criteria updated | PASS | 5 new criteria added (SC-4, SC-5, SC-11, SC-12, SC-20) |
| Provenance annotations | PASS | All sections annotated |
| Milestone count | PASS | 6 milestones (unchanged from V2 base) |
| No V2 content removed | PASS | All original V2 content preserved or enhanced |
