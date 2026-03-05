# Roadmap: sc:roadmap Edge Case and Invariant Violation Detection [Pragmatic Variant]

Document status: **Generated from brainstorm spec (203 lines)**
Generation date: **2026-03-04**
Persona: **architect** — pragmatic structure, phased delivery, risk-first thinking, implementation feasibility
Source specification: Brainstorm: Improving sc:roadmap to Surface Edge Cases and Invariant Violations

---

## Overview

This roadmap implements five methodology enhancements to `sc:roadmap` deliverable generation to prevent the class of bugs observed in v0.04: state-tracking variables whose correctness depended on conditions (filtering, empty inputs) that were never identified as separate deliverables or risks.

The implementation follows cost/impact ordering: Proposal 4 first (lowest cost, highest immediate value), then Proposals 1+2 bundled together (complementary: invariant registry defines expected state truth, FMEA models failure propagation), then Proposal 3 (guard analysis with invariant/FMEA context), and finally Proposal 5 conditionally gated on roadmap complexity.

The pragmatic philosophy: high-severity silent-corruption risks must surface early and block downstream expansion until mitigated or explicitly accepted with ownership. Process complexity should be proportional to roadmap complexity.

---

## Milestone Summary

| Milestone | Focus | Proposals Covered | Cost | Impact | Exit Gate |
|---|---|---|---|---|---|
| M1 | Baseline safety via implement/verify split | P4 | Low | High | All behavioral deliverables generated as `implement + verify` pairs |
| M2 | Invariant + failure-mode coverage for computational/state logic | P1, P2 | Medium | High | Invariant registry + FMEA table emitted for eligible deliverables |
| M3 | Guard/sentinel ambiguity control | P3 | Low | Medium | Guard state map + ambiguity checks integrated into generation |
| M4 | Conditional deep trace for high-complexity plans | P5 (gated) | High | Medium/High (for large plans) | Enabled only when roadmap complexity threshold is met |

---

## Dependency Graph

```
M1 → M2 → M3
          ↘
           M4 (conditional; only if complexity gate passes)
```

Dependency notes:
- D1.1/D1.2 are prerequisites for verification linking in D2.4
- D2.1 + D2.2 provide structured inputs to D3.x ambiguity and transition checks
- D4.x consumes M2/M3 outputs and should not run without them

---

## M1: Enforce Implement/Verify Decomposition (Foundation)

### Objective

Eliminate "single deliverable blind spots" by making internal correctness explicit for every behavioral change. Lowest cost, highest immediate impact — establishes the structural pattern all subsequent proposals consume.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Generator rule: split each behavioral deliverable `D.x` into `D.x.a` (implement) and `D.x.b` (verify) | For a representative input spec, 100% of behavioral deliverables appear as paired `.a/.b` items |
| D1.2 | Verification template for `.b` items including boundary tests, operand-identity checks, and post-condition assertions on internal state | Each verify item includes at minimum one state assertion or boundary case tied to its corresponding `.a` change |
| D1.3 | Pipeline lint/check to reject unpaired behavioral deliverables | Pipeline fails if any behavioral `D.x` lacks corresponding verify deliverable |

### Dependencies

None. Intentionally first; highest cost/impact ratio and lowest implementation risk.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Verify deliverables become generic boilerplate | Medium | High | Require at least one state assertion or boundary case tied to each `.a` change |
| R-002: Over-splitting creates roadmap noise | Medium | Medium | Scope split only to behavioral deliverables, not documentation/meta tasks |

---

## M2: Invariant Registry + FMEA for Computational/State Changes

### Objective

Catch value-wrong/type-correct failures and state drift by introducing structured invariants and failure-mode analysis where correctness is most fragile. Bundle Proposals 1 and 2 — they are complementary: the invariant registry defines expected state truth, FMEA models failure propagation.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | State Variable Invariant Registry pass triggered by `self._*`, counter/offset/cursor patterns | For each matched state variable: invariant predicate, mutation inventory, edge-case inputs per mutation, linked verification deliverable |
| D2.2 | FMEA pass for computational deliverables triggered by compute/extract/filter/count/calculate/determine/select verbs | Failure mode table with columns: input class, failure mode, downstream assumption, severity, detection, mitigation |
| D2.3 | Severity policy: silent corruption auto-tagged highest severity; roadmap orders mitigations before feature expansion | High-severity silent-corruption items surface in first review; cannot be deprioritized without explicit owner acceptance |
| D2.4 | Cross-linking between invariant registry rows and `.b` verify tasks | Every invariant row references at least one concrete verify deliverable ID |

### Dependencies

M1 (uses implement/verify decomposition as anchor for verification linkage).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-003: False positives from pattern-based trigger scans | High | Medium | Conservative trigger set + explicit allow/ignore list |
| R-004: FMEA quality varies by deliverable wording | Medium | Medium | Normalize computational verb detection; require structured output schema |
| R-005: Analysis overhead slows roadmap generation | Medium | Low | Run pass only on eligible deliverables; cache parsed metadata |
| R-006: Verify deliverables become checklist theater | Medium | High | Enforce state-specific assertions in each `.b` task via acceptance criteria |

---

## M3: Guard and Sentinel State Analysis

### Objective

Prevent ambiguous guard semantics and type-transition bugs in conditional logic paths — the class of failures seen in Bug 2 (bool→int type change introducing ambiguous zero value). Implemented after M2 to leverage invariant/FMEA context.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Guard-state enumeration pass for conditional deliverables | For each guard variable: all possible states listed with explicit semantic meaning |
| D3.2 | Ambiguity detector: one state, multiple meanings | Ambiguous guards are flagged and must be resolved or explicitly risk-accepted with owner and review date |
| D3.3 | Type-transition analyzer for guard/sentinel variables | Bool→int, enum→string, and equivalent transitions detected and annotated with transition safety checks |
| D3.4 | Accepted-risk decision artifact for unresolved ambiguity | If unresolved: explicit accepted-risk note with owner, review date, and release gate warning |

### Dependencies

M1 (verification pairing), M2 (guard failures appear in FMEA/invariant-linked checks; context reduces false alarms).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-007: Narrow heuristics miss hidden guard semantics | Medium | Medium | Seed detection with known bug archetypes (empty, filtered, tail, cursor conditions) |
| R-008: Team ignores accepted-risk output | Medium | High | Make unresolved ambiguity a release gate warning with mandatory owner |
| R-009: False positives for intentionally overloaded guard values | Low | Medium | Allow suppression annotation with documented rationale |

---

## M4: Conditional Cross-Deliverable Data Flow Tracing (Gated)

### Objective

Introduce deep mutable-state tracing only when roadmap complexity justifies cost. Hard-gated at 6+ milestones (or explicit override) to avoid over-engineering small plans. Pilot-first rollout.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Gating rule for Proposal 5 activation | Trace pass runs only when roadmap has 6+ milestones (configurable; explicit override available) |
| D4.2 | Variable lifecycle trace model (birth/write/read/contract/conflict) | For each traced mutable variable: lifecycle and cross-milestone contract emitted |
| D4.3 | Conflict detector for cross-milestone state assumptions | Conflicts produce explicit blockers linked to affected milestones/deliverables |
| D4.4 | Pilot execution + go/no-go decision | Pilot on one high-complexity roadmap; decision recorded with measured overhead vs defects prevented |

### Dependencies

M2 (registry + FMEA data as inputs), M3 (guard semantics for cleaner trace contracts).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-010: High compute and cognitive cost on low-complexity roadmaps | Medium | High | Hard gate by complexity; default OFF |
| R-011: Trace output too dense to act on | Medium | Medium | Emit only contract-relevant hops and conflict summaries, not raw full graphs |
| R-012: Premature rollout creates process fatigue | Medium | High | Pilot-first rollout with success criteria before general enablement |
| R-013: Cross-milestone contracts drift over time | Medium | Medium | Contract extraction tied to deliverable IDs and verify links |

---

## Risk Register

| Risk ID | Risk | Likelihood | Impact | Affected Milestones | Mitigation |
|---|---|---:|---:|---|---|
| R-001 | Verify deliverables become checklist theater | Medium | High | M1-M3 | Enforce state-specific assertions in each `.b` task |
| R-002 | Over-splitting creates roadmap noise | Medium | Medium | M1 | Scope split only to behavioral deliverables |
| R-003 | Trigger scans over/under-match target deliverables | High | Medium | M2-M3 | Conservative heuristics + allow/ignore controls + sample audits |
| R-004 | FMEA output generated but not prioritized | Medium | High | M2 | Severity policy: silent corruption = highest + ordering gate |
| R-005 | Guard ambiguity accepted too often without follow-up | Medium | High | M3 | Mandatory owner + review date + release warning |
| R-006 | Proposal 5 imposes excessive cost for marginal value | Medium | Medium/High | M4 | Strict complexity gate + pilot go/no-go decision |
| R-007 | Cross-milestone contracts drift over time | Medium | Medium | M2-M4 | Contract extraction tied to deliverable IDs and verify links |

---

## Decision Summary

1. **Start with Proposal 4 (M1)**: Best cost/impact ratio; immediately reduces blind spots by design; establishes Implement/Verify pair structure consumed by all subsequent proposals.
2. **Bundle Proposals 1 and 2 (M2)**: Invariant registry and FMEA are complementary — one defines expected state truth, the other models failure propagation. Shared trigger detection reduces implementation overhead.
3. **Run Proposal 3 after M2 (M3)**: Guard analysis with invariant/FMEA context reduces false alarms. Ambiguous guards surfacing with severity context from M2 are more actionable.
4. **Treat Proposal 5 as conditional (M4)**: High cost, low ROI on low-complexity roadmaps. Pilot-first with success criteria before general enablement.
5. **Release gating philosophy**: High-severity silent-corruption risks must surface early and block downstream roadmap expansion until mitigated or explicitly accepted with ownership.

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Bug 1 class (wrong operand) caught by invariant registry + implement/verify decomposition | M1, M2 | Yes |
| SC-002 | Bug 2 class (zero ambiguity after bool→int) caught by guard analysis + FMEA | M2, M3 | Yes |
| SC-003 | All artifacts usable as implementation guidance and review checklists | M1, M2, M3, M4 | Yes |
| SC-004 | Incremental adoption: M1 first, then M2+M3, then M4 without redesign | M1, M2, M3, M4 | Yes |
| SC-005 | Silent corruption failures surfaced at planning time, classified highest severity, block downstream expansion | M2, M3 | Yes |
