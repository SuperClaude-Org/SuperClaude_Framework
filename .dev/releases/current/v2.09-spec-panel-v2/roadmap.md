---
spec_source: ".dev/releases/current/v2.06-spec-panel-v2/spec-panel-release-spec.md"
generated: "2026-03-04T00:00:00Z"
generator: "sc:roadmap"
complexity_score: 0.561
complexity_class: MEDIUM
domain_distribution:
  documentation: 40
  quality: 35
  performance: 10
  security: 10
  backend: 5
primary_persona: scribe
consulting_personas: [qa, architect]
milestone_count: 7
milestone_index:
  - id: M1
    title: "Adversarial Persona Definition"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Low
  - id: M2
    title: "Panel Integration and Output Format"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Low
  - id: M3
    title: "Guard Condition Boundary Table"
    type: FEATURE
    priority: P0
    dependencies: [M1, M2]
    deliverable_count: 7
    risk_level: Medium
  - id: M4
    title: "Gate A: Phase 1-2 Validation"
    type: TEST
    priority: P0
    dependencies: [M1, M2, M3]
    deliverable_count: 3
    risk_level: Low
  - id: M5
    title: "Correctness Focus Mode"
    type: FEATURE
    priority: P1
    dependencies: [M4]
    deliverable_count: 7
    risk_level: Medium
  - id: M6
    title: "Pipeline Dimensional Analysis"
    type: FEATURE
    priority: P1
    dependencies: [M4]
    deliverable_count: 6
    risk_level: Medium
  - id: M7
    title: "Gate B: Validation and Release"
    type: TEST
    priority: P2
    dependencies: [M5, M6]
    deliverable_count: 7
    risk_level: Low
total_deliverables: 38
total_risks: 6
estimated_phases: 3
validation_score: 0.0
validation_status: SKIPPED
adversarial:
  mode: multi-roadmap
  agents: [opus:scribe, haiku:scribe]
  convergence_score: 1.0
  base_variant: "opus:scribe"
  artifacts_dir: ".dev/releases/current/v2.06-spec-panel-v2/adversarial/"
---

# Roadmap: /sc:spec-panel Correctness & Adversarial Review Enhancements

<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant 1 (opus:scribe) -->
<!-- Merge date: 2026-03-04 -->
<!-- Changes applied: 4 — Gate A milestone inserted (M4), M5/M6/M7 renumbered, Gate B evidence pack added, Validation-First Checkpoints table inserted -->

**Document status**: Generated from SPEC-PANEL-2026-Q1 via adversarial merge (opus:scribe base + haiku:scribe Gate A/B structure)
**Generation date**: 2026-03-04
**Source specification**: SPEC-PANEL-2026-Q1 v1.0

---

<!-- Source: Base (original) -->
## Overview

The `/sc:spec-panel` command assembles a panel of software-engineering experts to review specifications. Today it catches design and architecture issues well, but misses a class of bugs that only surface at execution time: off-by-one boundaries, silent data loss in pipelines, state corruption under edge inputs. This roadmap introduces four capabilities — delivered across three phases — that close that gap.

The core idea is layered: first add an adversarial tester who thinks like an attacker (Phase 1), then force structured boundary analysis that cannot be hand-waved (Phase 2), then deepen the entire panel's correctness awareness with focused review modes and pipeline analysis (Phase 3). Each phase builds on the previous one. Nothing in Phase 2 works without the adversarial persona from Phase 1, and Phase 3's correctness focus depends on both the persona and the boundary table infrastructure.

Two interleaved validation gates (Gate A after Phase 2, Gate B at release) enforce the MEDIUM-complexity 1:2 interleave ratio and prevent Phase 3 from starting on a defective Phase 1-2 foundation.

Four specification items drive this work:

| ID | Capability | Phase | Purpose |
|----|-----------|-------|---------|
| SP-2 | James Whittaker adversarial tester persona | 1 | Introduce attack-oriented thinking to the expert panel |
| SP-3 | Guard condition boundary table artifact | 2 | Force explicit enumeration of boundary behaviors with gap detection |
| SP-1 | `--focus correctness` review pass | 3 | Reconfigure the full panel for correctness-intensive review |
| SP-4 | Pipeline dimensional analysis heuristic | 3 | Detect data count mismatches across multi-stage pipelines |

SP-5 (Cross-Expert Challenge Protocol, 57.5/100 B-Tier) is deferred until SP-2 is validated in practice.

---

## Milestone Summary

<!-- Source: Base (original), modified per adversarial Change #1 — Gate A inserted as M4; M5/M6/M7 renumbered -->

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Adversarial Persona Definition | FEATURE | P0 | S | None | 4 | Low |
| M2 | Panel Integration and Output Format | FEATURE | P0 | S | M1 | 4 | Low |
| M3 | Guard Condition Boundary Table | FEATURE | P0 | M | M1, M2 | 7 | Medium |
| M4 | Gate A: Phase 1–2 Validation | TEST | P0 | S | M1, M2, M3 | 3 | Low |
| M5 | Correctness Focus Mode | FEATURE | P1 | M | M4 | 7 | Medium |
| M6 | Pipeline Dimensional Analysis | FEATURE | P1 | S | M4 | 6 | Medium |
| M7 | Gate B: Validation and Release | TEST | P2 | S | M5, M6 | 7 | Low |

**Total estimated effort**: 12–20 days. M5 and M6 can execute in parallel within Phase 3.

---

## Dependency Graph

```
M1 (Adversarial Persona)
│
└──► M2 (Panel Integration)
     │
     └──► M3 (Boundary Table)
          │
          └──► M4 (Gate A: Phase 1–2 Validation)
               │
               ├──► M5 (Correctness Focus Mode) ──┐
               │                                   │
               └──► M6 (Pipeline Analysis) ────────┴──► M7 (Gate B: Validation & Release)
```

**Linearized critical path**: M1 → M2 → M3 → M4 → M5 ‖ M6 → M7

M5 and M6 share the same prerequisite (M4/Gate A) and have no dependency on each other. They can execute in parallel within Phase 3. M7 gates on both.

<!-- Source: Variant 2 (haiku:scribe), Section 5 — inserted per adversarial Change #4 -->
## Validation-First Checkpoints

| Gate | Trigger | Required Evidence | Exit Condition |
|------|---------|-------------------|----------------|
| Gate A (M4) | End of M3 (Boundary Table complete) | v0.04 run logs, overhead report, artifact completeness report | Phase 3 authorized |
| Gate B (M7) | End of M5 + M6 (Phase 3 complete) | End-to-end metrics dashboard, risk review, integration verification | Release go/no-go |

---

<!-- Source: Base (original) -->
## Phase 1: Adversarial Mindset (Milestones M1–M2)

**Timeline**: Immediate, 1–3 days total
**Theme**: Introduce attack-oriented thinking to the expert panel without disrupting existing review flow.

Phase 1 is deliberately small. It adds a single new expert persona — modeled on James Whittaker's attack-based testing methodology — and wires it into the existing panel sequence. The goal is to start generating adversarial findings immediately, with minimal integration risk and token overhead (target: 5–10% additional).

---

### M1: Adversarial Persona Definition

**Objective**: Define the James Whittaker adversarial tester persona with a precise, bounded scope and structured attack methodology, ready for integration into the `/sc:spec-panel` review sequence.

**Why this matters**: The current panel has experts in architecture (Fowler), resilience (Nygard), testing (Crispin), and specification (Adzic), but none whose primary job is to break things. Whittaker's attack-based approach fills this gap by systematically probing for execution-correctness failures that design-oriented reviewers overlook.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Persona specification in `spec-panel.md`: identity, role description, behavioral directives, scope boundaries | Follows existing YAML structure; scope does not duplicate Nygard or Crispin roles |
| D1.2 | Five attack methodologies defined: Zero/Empty, Divergence, Sentinel Collision, Sequence, Accumulation | Each methodology is concrete enough to apply mechanically to a specification |
| D1.3 | Output format template: "I can break this by [attack]. Invariant at [location] fails when [condition]. Concrete: [state trace]." | Template produces findings that cite specific invariant location and include a state trace |
| D1.4 | Boundaries section update: panel grows from 10 to 11 experts | Count is correct; existing expert descriptions are unchanged |

### Dependencies
- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Persona scope creep duplicating Nygard/Crispin | Low | Low | Explicit scope boundary in persona definition |
| YAML structure mismatch with existing panel | Low | Low | Copy existing expert format as template |

---

### M2: Panel Integration and Output Format

**Objective**: Wire the Whittaker persona into the live review sequence and add the "Adversarial Analysis" section to the panel's output format.

**Why this matters**: A persona definition that sits in documentation but never executes is worthless. M2 makes the adversarial tester an active participant in every panel review.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Review sequence update: Whittaker appears after Fowler and Nygard | Ordering verified in spec-panel.md; Whittaker sees architectural and resilience context before attacking |
| D2.2 | Output format addition: "Adversarial Analysis" section in panel output template | Section appears in every panel run; not gated behind a flag |
| D2.3 | Token overhead measurement on two representative specifications | Measured overhead ≤10%; measurement documented |
| D2.4 | Validation run against v0.04 specification | Whittaker findings present; no regressions in existing expert outputs |

### Dependencies
- M1: Whittaker persona must be defined before wiring into execution path

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration breaks existing expert outputs | Low | Medium | Additive-only change; run regression check on v0.04 |
| Token overhead exceeds 10% budget | Low | Medium | Measure before M4 Gate A; optimize if needed |

---

## Phase 2: Structural Forcing Functions (Milestone M3)

**Timeline**: Next cycle, 3–5 days
**Theme**: Force explicit, gap-aware boundary analysis that cannot be skipped or hand-waved.

Phase 2 introduces the guard condition boundary table — a structured artifact that the panel must produce and complete before synthesis can proceed. The key design decision is that **incomplete tables block synthesis**, making boundary analysis a structural gate rather than an optional annotation.

---

### M3: Guard Condition Boundary Table

**Objective**: Define a mandatory, machine-parseable boundary table artifact that forces the panel to enumerate guard conditions, identify gaps, and block synthesis until the table is complete.

**Why this matters**: Expert reviews can miss boundary conditions not because the experts lack skill, but because nothing forces them to systematically enumerate every edge. The boundary table is a forcing function: it makes gaps visible by requiring explicit cells for every condition, and it escalates missing entries to MAJOR severity automatically.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Mandatory Output Artifacts section added to `spec-panel.md` | Section is present; clearly documents when the table is triggered |
| D3.2 | 7-column table template: Guard, Location, Input Condition, Variable Value, Guard Result, Specified Behavior, Status | Minimum 6 input condition rows per guard: zero/empty, one/minimal, typical, max/overflow, sentinel match, legitimate edge case |
| D3.3 | Completion enforcement: GAP cells → MAJOR severity; blank Specified Behavior → MAJOR severity | Rules are enforced as hard gates, not advisory |
| D3.4 | Synthesis-blocking logic: incomplete table prevents synthesis output | Hard gate verified on v0.04 test |
| D3.5 | Expert role assignments: Nygard leads, Crispin validates, Whittaker attacks entries | Role assignments documented; all three participate when table is triggered |
| D3.6 | Table trigger detection logic | Trigger fires on specs with conditional logic, threshold checks, boolean guards, or sentinel comparisons |
| D3.7b | NFR-4 overhead measurement for SP-3 | Token overhead for SP-3 boundary table measured on v0.04; must be ≤10% above Phase 1 baseline before M3 closes |
| D3.7 | Downstream propagation format for sc:adversarial AD-1 (invariant probe input) | Machine-parseable markdown; format documented for AD-1 consumer; SP-4→RM-3 and SP-2→RM-2 wired in M6 |

### Dependencies
- M1: Whittaker persona must be active to attack boundary table entries
- M2: Panel integration must be complete for role assignments to execute

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-1: Correctness theater — formulaic entries | Medium | High | Whittaker attacks each entry; track GAP ratio as quality signal; <50% formulaic target |
| R-3: Context window competition | Low | Medium | Concise structured format; abbreviation conventions for long guard expressions |
| Cumulative overhead exceeds 20% | Medium | Medium | Measure at M4 Gate A; optimize M2/M3 if needed before Phase 3 |

---

<!-- Source: Variant 2 (haiku:scribe) — inserted as dedicated M4 per adversarial Change #1 -->
### M4: Gate A — Phase 1–2 Validation

**Objective**: Validate Phase 1 (adversarial persona) and Phase 2 (boundary table) quality before authorizing Phase 3 work.

**Why this matters**: Gate A is a structural quality freeze. It prevents Phase 3 from starting on a foundation with unresolved defects in SP-2 or SP-3. Once Gate A passes, Phase 3 milestones can start with confidence.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Gate A evidence pack | Includes: v0.04 run logs with Whittaker findings + boundary table output; overhead measurement report; artifact completeness report |
| D4.2 | Phase 3 sign-off (go/no-go gate) | Explicit authorization for Phase 3 entry |
| D4.3 | Defect log | All issues found and fixes applied documented |

### Dependencies
- M1, M2, M3: All Phase 1–2 work must be complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Overhead exceeds 25% — Phase 3 blocked | Medium | Medium | Targeted optimization of M2/M3 before Phase 3 entry; correctness focus is additive so Phase 3 can start on M6 (pipeline) while M5 overhead is optimized |

---

## Phase 3: Depth and Breadth (Milestones M5–M6)

**Timeline**: Future, 5–8 days total (M5 and M6 can run in parallel)
**Theme**: Give the panel a dedicated correctness mode and teach it to analyze data pipelines.

Phase 3 has two parallel workstreams. M5 builds the `--focus correctness` mode that reconfigures the entire panel for correctness-intensive review. M6 adds pipeline dimensional analysis — a targeted heuristic for catching data count mismatches in multi-stage processing. Both depend on Gate A (M4) but not on each other.

---

### M5: Correctness Focus Mode (`--focus correctness`)

**Objective**: Add a `--focus correctness` flag that reconfigures the panel for deep correctness review, with a specialized 5-expert subset, three mandatory output artifacts, and an auto-suggestion heuristic.

**Why this matters**: Not every specification needs deep correctness analysis — but when it does, the panel should shift its entire posture. The correctness focus mode assembles the right experts, mandates the right artifacts, and even suggests itself when it detects correctness-sensitive patterns in the spec.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `--focus correctness` flag added to Focus Areas section in `spec-panel.md` | Appears in usage line; documented in Focus Areas section |
| D5.2 | Specialized 5-expert panel activated when flag is set: Nygard (lead), Fowler, Adzic, Crispin, Whittaker | Exactly 5 experts; correct lead assignment; verified on v0.04 |
| D5.3 | Modified expert behaviors FR-14.1 through FR-14.6 implemented | Each expert's review priorities shift under correctness focus as specified |
| D5.4 | State Variable Registry output template | Catalogs all mutable state, transitions, and invariants; present in every correctness-focus run |
| D5.5 | Guard Condition Boundary Table mandatory under correctness focus | Table always produced (not just triggered) when `--focus correctness` active |
| D5.6 | Pipeline Flow Diagram output specification | Annotated with counts at each stage when pipelines present |
| D5.7 | Auto-suggestion heuristic FR-16 | Triggers on: 3+ mutable state vars, numeric threshold guards, pipeline/filter ops; false positive rate <30% |

### Dependencies
- M4: Gate A must pass before Phase 3 authorized

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-2: Overhead exceeds 25% above standard | Medium | Medium | Measure at each deliverable; FR-14 behavior deltas are additive to existing reviews |
| R-4: Auto-suggestion false positives | Medium | Low | Advisory-only suggestion (not forced activation); <30% FP rate target; measured at M7 |
| R-6: Expert panel bloat | Low | Low | Whittaker's scope explicitly bounded; SP-5 deferred |

---

### M6: Pipeline Dimensional Analysis

**Objective**: Add a heuristic that detects multi-stage data pipelines and verifies that quantity relationships (input count vs. output count) are explicitly specified and consistent across stages.

**Why this matters**: A common class of correctness bugs occurs when a pipeline stage silently changes the number of items flowing through it — filters drop records, flatMaps multiply them, aggregations collapse them — and downstream stages assume the count is unchanged. This heuristic catches those mismatches before they become runtime bugs.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Pipeline detection trigger | Activates on specs with 2+ stage data flow where output count may differ from input count; does not trigger on CRUD-only specs |
| D6.2 | 4-step analysis: Pipeline Detection → Quantity Annotation → Downstream Tracing → Consistency Check | All 4 steps execute when triggered; Fowler leads detection/annotation; Whittaker attacks each stage |
| D6.3 | CRITICAL severity for dimensional mismatches | Any mismatch flagged as CRITICAL; concrete scenario included in finding |
| D6.4 | Quantity Flow Diagram output artifact | Shows counts at each pipeline stage; annotates which count each downstream consumer uses |
| D6.5 | Downstream integration wiring | SP-4 Quantity Flow → sc:roadmap RM-3; SP-2 Attack Findings → sc:roadmap RM-2; SP-1 Correctness → sc:adversarial AD-5; SP-2 Assumptions → sc:adversarial AD-2 |
| D6.6 | Token overhead validation | <5% overhead when no pipelines detected; ≤10% when pipelines detected |

### Dependencies
- M4: Gate A — no causal dependency on M5 (parallel execution in Phase 3)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-5: Pipeline detection under-triggers | Low | Medium | Broad trigger condition (any 2+ stage data flow with possible count change); manual `--focus correctness` as fallback |
| R-3: Context window competition | Low | Medium | Detection-gated: analysis only activates on detected pipelines; <10% overhead cap |

---

<!-- Source: Base (original) + Variant 2 (haiku:scribe) Gate B evidence pack — merged per adversarial Change #2 -->
### M7: Gate B — Validation and Release

**Objective**: Perform end-to-end validation of all capabilities (SP-1 through SP-4) working together, confirm integration points, measure cumulative overhead, and issue a go/no-go release decision.

**Why this matters**: Individual milestones are validated in isolation, but the complete system must work as a coherent whole. Gate B is the integration gate that confirms all four capabilities interact correctly and cumulative overhead stays within budget.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | End-to-end validation suite on 3 representative specs | Correctness-heavy spec, pipeline-heavy spec, baseline spec (no state/pipelines) |
| D7.2 | Gate B evidence pack | End-to-end metrics dashboard, risk review (R-1 through R-6), integration verification report |
| D7.3 | Cumulative overhead measurement | <25% without `--focus correctness`; <40% with `--focus correctness` |
| D7.4 | Integration point verification | All 5 integration points (SP-3→AD-1, SP-2→AD-2, SP-1→AD-5, SP-4→RM-3, SP-2→RM-2) produce valid parseable output |
| D7.5 | Quality metric validation | Formulaic entries <50%; auto-suggestion FP rate <30%; adversarial findings ≥2 per mutable-state review; GAP cells >0 per review with guard conditions |
| D7.6 | Go/no-go decision with rollback plan | Explicit decision record with rationale; rollback plan specifying reversion steps documented before release authorization |
| D7.7 | Release documentation | Updated changelog, version bump, migration notes if any |

### Dependencies
- M5, M6: All Phase 3 work must be complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cumulative overhead exceeds budget at Gate B | Low | High | Overhead measured at M2, M3, M4 (Gate A); late discovery unlikely; targeted optimization available |
| Integration point format incompatibility | Low | Medium | Format specified in M3/M5/M6 deliverables; verify early with stub consumers |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | **Correctness theater** — boundary tables become formulaic checkbox exercises without genuine analysis | M3, M5 | Medium | High | Whittaker validates entries by attempting attacks; track GAP ratio and formulaic entry rate (<50% target) | qa |
| R-002 | **Overhead exceeds tolerance** — cumulative token cost makes enhanced panel impractical | M2, M5, M7 | Medium | Medium | Phased implementation with measurement gates (M4, M7); explicit overhead budget per phase | architect |
| R-003 | **Context window competition** — structured artifacts compete for limited context space | M3, M6 | Low | Medium | Concise structured formats; compact markdown; boundary table uses abbreviation conventions | scribe |
| R-004 | **Adversarial tester false positives** — Whittaker generates non-actionable findings | M1, M7 | Medium | Low | Require concrete state traces in every finding; synthesis step filters low-evidence findings | qa |
| R-005 | **Pipeline detection under-triggers** — heuristic misses pipelines in unusual language | M6 | Low | Medium | Broad trigger condition (any 2+ stage data flow); manual `--focus correctness` as fallback | qa |
| R-006 | **Expert persona bloat** — Whittaker creates precedent for unbounded expert growth | M1 | Low | Low | Whittaker's scope explicitly bounded in persona definition; SP-5 deferred to prevent further expansion | architect |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | scribe | qa (0.269), architect (0.269) | Highest domain confidence (documentation 40%, coverage_bonus 1.3) |
| Template | inline generation | None found (Tiers 1-3 empty) | No project/user templates available; quality domain primary |
| Milestone Count | 7 (5 work + 2 gate) | 5-7 range for MEDIUM | base 5 + floor(4 domains/2) = 7; 2 gate milestones added for 1:2 interleave ratio |
| Adversarial Mode | multi-roadmap | none | `--multi-roadmap --agents opus,haiku` flags present |
| Adversarial Base Variant | opus:scribe (score 0.956) | haiku:scribe (score 0.847) | 10.9% margin; 11/14 debate points; higher section coverage (14 vs 8) |
| M4+M5 parallelism | Parallel (both depend on M4 only) | Sequential M5→M6 (haiku:scribe variant) | No causal dependency between SP-1 and SP-4; M7 handles integration testing |
| Gate A milestone | Inserted as M4 after Phase 2 | Embedded validation in per-milestone ACs only | Required by MEDIUM complexity 1:2 interleave ratio; V1 advocate conceded Round 1 |

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | >80% catch rate for boundary condition bugs (retrospective on past specs) | M3, M5, M7 | Yes |
| SC-002 | >0 GAP cells in boundary tables for specs with guard conditions | M3, M7 | Yes |
| SC-003 | ≥2 adversarial tester findings per review for specs with mutable state | M1, M2, M7 | Yes |
| SC-004 | <25% token overhead (Phase 1+2); <40% (Phase 3 with correctness focus) | M2, M3, M4, M7 | Yes |
| SC-005 | <50% formulaic boundary table entries (quarterly manual audit) | M3, M7 | Yes (manual) |

---

## Integration Map

The enhanced `/sc:spec-panel` produces structured outputs consumed by two downstream commands:

```
/sc:spec-panel (enhanced)
│
├── SP-3: Boundary Table ──────────► sc:adversarial AD-1 (invariant probe)
│
├── SP-2: Attack Findings ─────────► sc:adversarial AD-2 (assumption extraction)
│
├── SP-1: Correctness Findings ────► sc:adversarial AD-5 (taxonomy L3)
│
├── SP-4: Quantity Flow ───────────► sc:roadmap RM-3 (state flow tracing)
│
└── SP-2: Attack Scenarios ────────► sc:roadmap RM-2 (negative acceptance criteria)
```

All downstream formats are machine-parseable structured markdown. No downstream changes are required in this release — the integration contract is output format compatibility.

---

## Deferred Work

### SP-5: Cross-Expert Challenge Protocol

**Prioritization score**: 57.5/100 (B-Tier)
**Reason for deferral**: Depends on Whittaker's attack findings being well-calibrated, which can only be validated after SP-2 has been used in practice across multiple reviews. Adds 20–30% overhead for an indirect mechanism without new analytical techniques.
**Revisit trigger**: After SP-2 has been active for at least 10 reviews and the false positive rate (R-004) is measured below threshold.

---

## Appendix: Phase-to-Milestone Mapping

| Phase | Name | Milestones | Duration | Cumulative Overhead Target |
|-------|------|-----------|----------|---------------------------|
| 1 | Adversarial Mindset | M1, M2 | 1–3 days | 5–10% |
| 2 | Structural Forcing Functions | M3 | 3–5 days | 15–20% |
| Gate A | Phase 1–2 Validation | M4 | 1 day | Verify <25% |
| 3 | Depth and Breadth (parallel) | M5 ‖ M6 | 5–8 days | 25% (standard) / 40% (correctness focus) |
| Gate B | Phase 3 Validation & Release | M7 | 1–2 days | Final verification |
