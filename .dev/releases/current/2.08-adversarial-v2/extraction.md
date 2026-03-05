---
schema_version: "2.0.0"
spec_source: ".dev/releases/current/2.07-adversarial-v2/brainstorm-adversarial.md"
generated: "2026-03-04T00:00:00Z"
generator: "sc:roadmap v2.0.0"
functional_requirements: 19
nonfunctional_requirements: 4
total_requirements: 23
domains_detected: ["backend_architecture", "performance", "documentation", "quality"]
risks_identified: 6
dependencies_identified: 6
success_criteria_count: 5
extraction_mode: "standard"
project_title: "Improving sc:adversarial to Catch Implementation-Level Bugs"
project_version: "2.0"
complexity_score: 0.440
complexity_class: "MEDIUM"
primary_persona: "architect"
consulting_personas: ["analyzer", "performance"]
domain_distribution:
  backend_architecture: 60
  performance: 15
  documentation: 15
  quality: 10
requirement_counts:
  functional: 19
  non_functional: 4
  dependencies: 6
  success_criteria: 5
  risks: 6
  total: 40
extraction_status: "complete"
---

# Extraction: Improving sc:adversarial to Catch Implementation-Level Bugs

## 1. Project Overview

**Title**: Improving sc:adversarial to Catch Implementation-Level Bugs
**Version**: 2.0 (enhancement to existing sc:adversarial pipeline)
**Source**: `brainstorm-adversarial.md` (2026-03-04)

**Summary**: Proposes 6 targeted enhancements to the `sc:adversarial` debate pipeline to close a structural blind spot — the current pipeline excels at architectural trade-off analysis but does not descend into operational state analysis. Two concrete production bugs (Index Tracking Stall, Replay Guard Bypass) that escaped v0.03 adversarial review motivate these proposals. Each proposal independently catches both bugs; together they form a mutually reinforcing 4-layer defense.

**Problem Statement**: The debate operates at the design abstraction layer and never traces concrete data through proposed state machines. No debater was prompted to ask: "given this input sequence, what value does variable X hold at step N?"

---

## 2. Functional Requirements

### FR-001 — Failure Mode Enumeration Phase
- **Description**: Add mandatory Step 1.5 between Diff Analysis and Adversarial Debate. Each advocate must enumerate concrete failure modes for every variant (including their own), structured as: Precondition / Trigger / Mechanism / Consequence / Detection difficulty.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L26-L66

### FR-002 — Failure Mode Novelty Scoring
- **Description**: Score failure modes for novelty. Advocates who identify failure modes no other advocate found earn bonus weight in debate scoring.
- **Domain**: backend_architecture
- **Priority**: P2
- **Source Lines**: L33-L34

### FR-003 — Scenario Traces Debate Round Type
- **Description**: Add a new debate round type called Scenario Traces (injectable at `--depth standard` or deeper). Debate orchestrator generates 3-5 concrete input scenarios derived from diff analysis; each advocate must trace the scenario step by step, showing value of every state variable at each step.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L69-L118

### FR-004 — Scenario Category Requirements
- **Description**: Generated scenarios must include: (1) Happy path (normal expected usage), (2) Boundary conditions (empty, maximum, single-element), (3) Filter/transform scenarios (intermediate processing changes cardinality), (4) Temporal edge cases (start/end/boundary of sequence), (5) Adversarial inputs (sequences designed to stress assumptions).
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L76-L82

### FR-005 — Diff-Driven Scenario Selection
- **Description**: Orchestrator selects scenarios based on diff points — if variants disagree on pagination handling, scenarios must include pagination-stressing inputs. Scenarios are targeted to the specific disagreement dimensions identified in Step 1.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L83-L85

### FR-006 — Divergent Trace Flagging
- **Description**: When advocates trace the same scenario and produce different end states, flag as unresolved divergences requiring explicit resolution before convergence can be declared.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L86-L89

### FR-007 — Invariant Declaration Phase
- **Description**: Add a structured phase where each advocate declares the invariants their design relies upon. An invariant is a property that must always hold true for the design to be correct (e.g., "After replay completes, `_replayed_event_offset > 0`").
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L122-L132

### FR-008 — Invariant Challenge Round
- **Description**: After invariant declaration, opposing advocates enter a Challenge Round where they attempt to construct input sequences that violate declared invariants. Violated invariants are flagged as "unproven."
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L133-L137

### FR-009 — Invariant Resolution Requirement
- **Description**: Designs with unproven invariants must either be modified to restore the invariant, or the invariant weakened. Weakened invariants become debate points about whether the weakened form is sufficient for correctness.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L137-L138

### FR-010 — Devil's Advocate Agent Role
- **Description**: Add a new permanent agent role — the Devil's Advocate. This agent does not advocate for any variant. Its sole functions are: (1) identify implicit and explicit assumptions per variant, (2) construct adversarial input sequences to violate those assumptions, (3) flag under-specified state transitions, (4) identify guard condition gaps, (5) enumerate degenerate inputs (empty, zero, max, boundary).
- **Domain**: backend_architecture
- **Priority**: P0
- **Source Lines**: L167-L179

### FR-011 — Devil's Advocate Ordering
- **Description**: Devil's Advocate produces its analysis before Round 1. Advocates must address DA concerns in their opening statements.
- **Domain**: backend_architecture
- **Priority**: P0
- **Source Lines**: L179-L181

### FR-012 — DA Concerns as Convergence Blockers
- **Description**: Any DA concern left unaddressed by all advocates is flagged as a convergence blocker. The debate cannot declare convergence until every Devil's Advocate concern has been explicitly resolved.
- **Domain**: backend_architecture
- **Priority**: P0
- **Source Lines**: L181-L183

### FR-013 — Devil's Advocate Prompt Design
- **Description**: Devil's Advocate is implemented as a separate agent with a distinct system prompt emphasizing destructive creativity — not "which design is better?" but "how does each design break?"
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L183-L184

### FR-014 — State Coverage Gate (Convergence Formula Modification)
- **Description**: Modify convergence formula to: `convergence = (agreed_points / total_diff_points) * state_coverage_factor`. The state_coverage_factor < 1.0 when any required state coverage category has not been addressed in any debate round.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L220-L230

### FR-015 — State Coverage Category Definitions
- **Description**: Define required and conditional state coverage categories: Required (always): Happy path, Empty/zero inputs, Boundary conditions. Conditional (if relevant): Filter divergence (when any variant involves filtering), Error/exception paths (when error handling is specified), Concurrent/reentrant (when concurrency is involved).
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L233-L245

### FR-016 — Coverage Gate Enforcement
- **Description**: If a required coverage category has not been addressed in any debate round, `state_coverage_factor < 1.0` and convergence cannot be reached regardless of diff point agreement percentage.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L245-L246

### FR-017 — Post-Merge Trace Validation (Step 5.5)
- **Description**: Add Step 5.5 after merge execution. The merged solution is subjected to 3-5 concrete Scenario Traces by a validation agent. Agent flags inconsistencies, ambiguities, and underdetermined states in the merged design.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L269-L280

### FR-018 — Fresh Validation Agent Requirement
- **Description**: Post-merge validation agent must be a fresh agent with no prior advocacy bias — it has no stake in any original variant and evaluates the merge purely on operational correctness.
- **Domain**: backend_architecture
- **Priority**: P1
- **Source Lines**: L278-L280

### FR-019 — Depth-Gated Scenario Traces
- **Description**: Scenario Traces (Proposal 2 / FR-003) are gated behind `--depth standard` or deeper. Not activated at `--depth quick` to control token cost.
- **Domain**: performance
- **Priority**: P1
- **Source Lines**: L320

---

## 3. Non-Functional Requirements

### NFR-001 — Token Cost Containment
- **Description**: Scenario Traces are the highest token-cost addition. Must be gated to `--depth standard` or deeper to prevent cost explosion for quick debates.
- **Category**: performance
- **Constraint**: Scenario Traces activate only at `--depth standard` or deeper
- **Source Lines**: L320

### NFR-002 — Convergence Quality Gate
- **Description**: The pipeline must not declare convergence before all required state coverage categories are verified as having been addressed.
- **Category**: reliability
- **Constraint**: `state_coverage_factor < 1.0` when any required category unaddressed
- **Source Lines**: L245-L246

### NFR-003 — Validation Agent Independence
- **Description**: Post-merge validation agent must have no prior debate context or advocacy stake to ensure unbiased operational evaluation.
- **Category**: reliability
- **Constraint**: Fresh agent instantiation with no debate context
- **Source Lines**: L278-L280

### NFR-004 — Minimum Failure Mode Count
- **Description**: Failure Mode Enumeration phase requires each advocate to produce a minimum number of failure modes per variant. Count is configurable; default is 3.
- **Category**: reliability
- **Constraint**: `min_failure_modes >= 3` per variant per advocate (configurable)
- **Source Lines**: L32-L33

---

## 4. Dependencies

### DEP-001 — Failure Mode → Scenario Trace Input
- **Description**: Scenario Traces (FR-003) benefit from Failure Mode Enumeration (FR-001) — FME outputs provide candidate failure scenarios that become trace inputs for Proposal 2.
- **Type**: internal
- **Affected Requirements**: FR-001, FR-003
- **Source Lines**: L316-L322

### DEP-002 — Devil's Advocate → Invariant Candidates
- **Description**: Devil's Advocate (FR-010) outputs feed into Invariant Challenge Round (FR-008). DA-flagged assumptions become primary candidates for invariant declaration and challenge.
- **Type**: internal
- **Affected Requirements**: FR-007, FR-008, FR-010
- **Source Lines**: L316-L337

### DEP-003 — Scenario Traces + Invariants → Coverage Gate Data
- **Description**: State Coverage Gate (FR-014) depends on Scenario Traces (FR-003) and Invariant Challenge (FR-008) generating the per-category coverage evidence needed to compute state_coverage_factor.
- **Type**: internal
- **Affected Requirements**: FR-003, FR-008, FR-014
- **Source Lines**: L248-L266

### DEP-004 — Merge → Post-Merge Validation
- **Description**: Post-Merge Trace Validation (FR-017) requires a completed merged output to trace scenarios through. Must execute after merge step completion.
- **Type**: internal
- **Affected Requirements**: FR-017
- **Source Lines**: L269-L276

### DEP-005 — debate-orchestrator Extension
- **Description**: The existing `debate-orchestrator` agent requires prompt engineering extensions to support diff-driven scenario generation (FR-005) and DA concern tracking (FR-012).
- **Type**: external
- **Affected Requirements**: FR-003, FR-005, FR-010, FR-012
- **Source Lines**: L82-L85

### DEP-006 — sc:adversarial SKILL.md Modification
- **Description**: Convergence formula modification (FR-014) and new phase insertions (FR-001, FR-007, FR-010, FR-017) require direct changes to the sc:adversarial-protocol SKILL.md file.
- **Type**: external
- **Affected Requirements**: FR-001, FR-007, FR-010, FR-014, FR-015, FR-016, FR-017
- **Source Lines**: L220-L246

---

## 5. Success Criteria

### SC-001 — Retroactive Bug Detection
- **Description**: Both concrete bugs (Index Tracking Stall — cursor advances by widget count not events consumed; Replay Guard Bypass — guard fails when tail is empty) would be caught by at least 2 of the 6 implemented proposals under retroactive simulation.
- **Derived From**: FR-001, FR-003, FR-007, FR-010, FR-014, FR-017
- **Measurable**: Yes
- **Source Lines**: L303-L313

### SC-002 — Coverage Gate Enforcement
- **Description**: Convergence is not declared when a required state coverage category (happy path, empty/zero inputs, boundary conditions) has not been addressed in any debate round.
- **Derived From**: FR-014, FR-015, FR-016
- **Measurable**: Yes
- **Source Lines**: L245-L246

### SC-003 — DA Convergence Blocking
- **Description**: Devil's Advocate concerns block convergence declaration. No convergence is reached while unresolved DA concerns exist in the concern registry.
- **Derived From**: FR-011, FR-012
- **Measurable**: Yes
- **Source Lines**: L181-L183

### SC-004 — Merge Artifact Detection
- **Description**: Post-merge trace validation detects at least one integration-specific bug in a simulation where Variant A's cursor logic is combined with Variant C's condensation filtering without adaptation.
- **Derived From**: FR-017, FR-018
- **Measurable**: Yes
- **Source Lines**: L276-L292

### SC-005 — Trace Divergence Flagging
- **Description**: When advocates trace the same scenario and reach different values for the same state variable, the divergence is automatically flagged and prevents convergence declaration.
- **Derived From**: FR-006
- **Measurable**: Yes
- **Source Lines**: L86-L89

---

## 6. Risk Register

### RISK-001 — Token Cost Explosion
- **Description**: Adding 3+ new debate phases (Failure Mode Enumeration + Scenario Traces + Invariant Challenge + Devil's Advocate) significantly increases token consumption per debate session, potentially making `--depth deep` sessions cost-prohibitive.
- **Probability**: High
- **Impact**: High
- **Affected Requirements**: NFR-001, FR-001, FR-003, FR-007, FR-010
- **Source**: Inferred from L320, explicit "highest token cost" note

### RISK-002 — Orchestrator Complexity
- **Description**: The debate-orchestrator agent requires significant prompt engineering to coordinate new phases (scenario generation, DA concern tracking, coverage gate evaluation) without context overflow or phase ordering errors.
- **Probability**: High
- **Impact**: Medium
- **Affected Requirements**: FR-005, FR-010, FR-012
- **Source**: Inferred

### RISK-003 — Advocate Overload
- **Description**: Requiring advocates to simultaneously propose designs, trace scenarios step-by-step, enumerate failure modes, and declare formal invariants may exceed the quality threshold for any single response, degrading output quality per phase.
- **Probability**: Medium
- **Impact**: High
- **Affected Requirements**: FR-001, FR-003, FR-007
- **Source**: Inferred

### RISK-004 — Convergence Deadlock
- **Description**: DA concerns becoming hard convergence blockers (FR-012) may prevent convergence on legitimate designs with inherent edge-case ambiguities, creating debates that never terminate.
- **Probability**: Medium
- **Impact**: Medium
- **Affected Requirements**: FR-012, FR-016
- **Source**: Inferred

### RISK-005 — Partial Implementation Synergy Loss
- **Description**: Implementing only 1-2 proposals from the recommended 4-layer set (DA + Coverage Gate + Scenario Traces + Invariant Challenge) loses the compounding benefit. The proposals are designed to work synergistically — partial implementation reduces effectiveness non-linearly.
- **Probability**: Medium
- **Impact**: High
- **Affected Requirements**: FR-003, FR-007, FR-010, FR-014
- **Source**: Inferred from L328-L337

### RISK-006 — Scenario Generation Shallow Coverage
- **Description**: Orchestrator-generated scenarios may miss the specific edge cases they're designed to catch if scenario generation logic is too shallow or doesn't account for domain-specific filtering semantics.
- **Probability**: Medium
- **Impact**: High
- **Affected Requirements**: FR-003, FR-004, FR-005
- **Source**: Inferred

---

## 7. Domain Analysis Summary

| Domain | Weight | Key Requirements |
|--------|--------|-----------------|
| Backend/Architecture | 60% | FR-001–FR-018 (pipeline modifications, agent roles, convergence formulas) |
| Performance | 15% | NFR-001, FR-019 (token cost gating) |
| Documentation | 15% | DEP-006, SKILL.md changes, new phase specifications |
| Quality/Testing | 10% | SC-001–SC-005, FR-006, FR-016 |

**Implementation Priority Order** (per spec recommendation):
1. FR-010/FR-011/FR-012/FR-013 — Devil's Advocate (highest ROI, minimal pipeline change)
2. FR-014/FR-015/FR-016 — State Coverage Gate (low implementation cost)
3. FR-003/FR-004/FR-005/FR-006/FR-019 — Scenario Traces (highest bug-catch power, depth-gated)
4. FR-007/FR-008/FR-009 — Invariant Challenge (requires formal reasoning discipline)
5. FR-001/FR-002 — Failure Mode Enumeration (overlaps with DA, lower marginal value)
6. FR-017/FR-018 — Post-Merge Validation (addresses merge-specific artifact class)
