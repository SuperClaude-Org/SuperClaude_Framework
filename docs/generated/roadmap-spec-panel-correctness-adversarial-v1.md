---
document_id: ROAD-SPECPANEL-2026-Q1
title: "Roadmap: /sc:spec-panel Correctness & Adversarial Review Enhancements"
version: "1.0"
date: "2026-03-04"
status: draft
source_specification: SPEC-PANEL-2026-Q1
persona: scribe
complexity: MEDIUM
milestone_count: 6
phases: 3
estimated_duration: "9-16 days across three phases"
deferred:
  - SP-5 (Cross-Expert Challenge Protocol)
---

# Roadmap: /sc:spec-panel Correctness & Adversarial Review Enhancements

**Document status**: Generated from release specification SPEC-PANEL-2026-Q1
**Generation date**: 2026-03-04
**Persona**: scribe -- clarity-focused, audience-first, structured information flow
**Source specification**: SPEC-PANEL-2026-Q1 v1.0

---

## Overview

The `/sc:spec-panel` command assembles a panel of software-engineering experts to review specifications. Today it catches design and architecture issues well, but misses a class of bugs that only surface at execution time: off-by-one boundaries, silent data loss in pipelines, state corruption under edge inputs. This roadmap introduces four capabilities -- delivered across three phases -- that close that gap.

The core idea is layered: first add an adversarial tester who thinks like an attacker (Phase 1), then force structured boundary analysis that cannot be hand-waved (Phase 2), then deepen the entire panel's correctness awareness with focused review modes and pipeline analysis (Phase 3). Each phase builds on the previous one. Nothing in Phase 2 works without the adversarial persona from Phase 1, and Phase 3's correctness focus depends on both the persona and the boundary table infrastructure.

Four specification items drive this work:

| ID | Capability | Phase | Purpose |
|----|-----------|-------|---------|
| SP-2 | James Whittaker adversarial tester persona | 1 | Introduce attack-oriented thinking to the expert panel |
| SP-3 | Guard condition boundary table artifact | 2 | Force explicit enumeration of boundary behaviors with gap detection |
| SP-1 | `--focus correctness` review pass | 3 | Reconfigure the full panel for correctness-intensive review |
| SP-4 | Pipeline dimensional analysis heuristic | 3 | Detect data count mismatches across multi-stage pipelines |

SP-5 (Cross-Expert Challenge Protocol) scored 57.5/100 in prioritization and is deferred until SP-2 is validated in practice.

---

## Milestone Summary

| ID | Title | Phase | Priority | Effort | Dependencies | Primary Risk |
|----|-------|-------|----------|--------|--------------|-------------|
| M1 | Adversarial Persona Definition | 1 | P0-Critical | 1-2 days | None | Low -- pure specification |
| M2 | Panel Integration and Output Format | 1 | P0-Critical | 1-2 days | M1 | Low -- additive change |
| M3 | Guard Condition Boundary Table | 2 | P0-Critical | 3-5 days | M1, M2 | Medium -- structural forcing function must not become theater |
| M4 | Correctness Focus Mode | 3 | P1-High | 3-5 days | M1, M2, M3 | Medium -- overhead management |
| M5 | Pipeline Dimensional Analysis | 3 | P1-High | 2-3 days | M1, M2, M3 | Medium -- detection accuracy |
| M6 | Validation and Release | 3 | P2-Standard | 1-2 days | M1, M2, M3, M4, M5 | Low -- integration testing |

**Total estimated effort**: 11-19 days (phases may overlap where dependencies allow).

---

## Dependency Graph

```
M1 (Adversarial Persona)
│
├──► M2 (Panel Integration)
│    │
│    ├──► M3 (Boundary Table)
│    │    │
│    │    ├──► M4 (Correctness Focus)
│    │    │    │
│    │    │    └──► M6 (Validation & Release)
│    │    │         ▲
│    │    └──► M5 (Pipeline Analysis)──┘
│    │
│    └─────────────────────────────────┘
```

**Linearized critical path**: M1 --> M2 --> M3 --> M4 + M5 (parallel) --> M6

M4 and M5 share the same prerequisites (M1, M2, M3) and have no dependency on each other. They can execute in parallel within Phase 3. M6 gates on all five preceding milestones.

---

## Phase 1: Adversarial Mindset (Milestones M1-M2)

**Timeline**: Immediate, 1-3 days total
**Theme**: Introduce attack-oriented thinking to the expert panel without disrupting existing review flow.

Phase 1 is deliberately small. It adds a single new expert persona -- modeled on James Whittaker's attack-based testing methodology -- and wires it into the existing panel sequence. The goal is to start generating adversarial findings immediately, with minimal integration risk and token overhead (target: 5-10% additional).

---

### M1: Adversarial Persona Definition

**Objective**: Define the James Whittaker adversarial tester persona with a precise, bounded scope and structured attack methodology, ready for integration into the `/sc:spec-panel` review sequence.

**Why this matters**: The current panel has experts in architecture (Fowler), resilience (Nygard), testing (Crispin), and specification (Adzic), but none whose primary job is to break things. Whittaker's attack-based approach fills this gap by systematically probing for execution-correctness failures that design-oriented reviewers overlook.

**Deliverables**:

1. **Persona specification** in `spec-panel.md`: identity, role description, behavioral directives, and scope boundaries
2. **Five attack methodologies** defined with structured output format:
   - **Zero/Empty Attack**: What happens when inputs are absent, null, or empty?
   - **Divergence Attack**: Where can state drift from its expected trajectory?
   - **Sentinel Collision Attack**: Can special values collide with legitimate data?
   - **Sequence Attack**: Does ordering matter, and what breaks when it changes?
   - **Accumulation Attack**: What happens when small effects compound over many iterations?
3. **Output format template**: "I can break this by [attack]. Invariant at [location] fails when [condition]. Concrete: [state trace]."
4. **Boundaries section update**: Panel grows from 10 to 11 experts; document this clearly

**Acceptance criteria**:
- Persona follows existing YAML structure conventions
- Uses existing severity levels (CRITICAL / MAJOR / MINOR) -- no new taxonomy
- Attack methodologies are concrete enough to apply mechanically
- Scope is bounded: Whittaker does not duplicate Nygard's resilience focus or Crispin's test-case focus

**Risks**: Minimal. This is additive specification work with no runtime coupling.

**Success metric link**: This milestone enables the ">=2 adversarial findings per review with mutable state" target.

---

### M2: Panel Integration and Output Format

**Objective**: Wire the Whittaker persona into the live review sequence and add the "Adversarial Analysis" section to the panel's output format.

**Why this matters**: A persona definition that sits in documentation but never executes is worthless. M2 makes the adversarial tester an active participant in every panel review.

**Deliverables**:

1. **Review sequence update**: Whittaker appears after Fowler and Nygard in the expert ordering. Rationale: Whittaker needs to see the architectural and resilience context before attacking.
2. **Output format addition**: New "Adversarial Analysis" section in the panel output template, positioned after existing expert sections.
3. **Token overhead measurement**: Validate that the addition stays within the 5-10% overhead budget on at least two representative specifications.
4. **Validation against v0.04 specification**: Run the updated panel against the v0.04 spec to confirm correct behavior.

**Acceptance criteria**:
- Whittaker's output appears in every panel run (not gated behind a flag)
- Output follows the structured format from M1 (attack / invariant / condition / state trace)
- Token overhead measured and documented; must be <= 10%
- No regressions in existing expert outputs

**Dependencies**: M1 (persona must be defined before integration)

**Risks**: Low. The integration is additive -- existing experts are not modified.

---

## Phase 2: Structural Forcing Functions (Milestone M3)

**Timeline**: Next cycle, 3-5 days
**Theme**: Force explicit, gap-aware boundary analysis that cannot be skipped or hand-waved.

Phase 2 introduces the guard condition boundary table -- a structured artifact that the panel must produce and complete before synthesis can proceed. This is the phase where rigor moves from "the adversarial tester found something" to "the panel systematically enumerated every boundary and flagged every gap." The key design decision is that **incomplete tables block synthesis**, making boundary analysis a structural gate rather than an optional annotation.

---

### M3: Guard Condition Boundary Table

**Objective**: Define a mandatory, machine-parseable boundary table artifact that forces the panel to enumerate guard conditions, identify gaps, and block synthesis until the table is complete.

**Why this matters**: Expert reviews can miss boundary conditions not because the experts lack skill, but because nothing forces them to systematically enumerate every edge. The boundary table is a forcing function: it makes gaps visible by requiring explicit cells for every condition, and it escalates missing entries to MAJOR severity automatically.

**Deliverables**:

1. **Mandatory Output Artifacts section** added to `spec-panel.md`
2. **Table template**: 7-column structured markdown table
   - Columns: Guard, Input Condition, Boundary Value, Expected Behavior, Specified Behavior, Gap Status, Severity
   - Minimum 6 input condition rows per guard
3. **Completion criteria and enforcement**:
   - Any cell marked GAP automatically triggers MAJOR severity minimum
   - Any blank "Specified behavior" cell triggers MAJOR severity minimum
   - Synthesis is blocked until all rows are populated (incomplete table = incomplete review)
4. **Expert role assignments**:
   - Nygard leads table construction (resilience perspective)
   - Crispin validates entries (testing perspective)
   - Whittaker attacks entries (adversarial perspective -- feeds from M1)
5. **Table trigger detection logic**: When and how the panel decides a guard condition boundary table is needed
6. **Downstream propagation format**: Machine-parseable markdown compatible with:
   - `sc:adversarial` AD-1 (invariant probe input)
   - `sc:roadmap` RM-1 (requirement traceability)
7. **Validation against v0.04 specification**: Produce a boundary table for v0.04 and measure overhead.

**Acceptance criteria**:
- Table format is structured markdown, parseable by downstream tools
- GAP and blank-cell escalation rules are enforced, not advisory
- Synthesis blocking is implemented as a hard gate
- Token overhead (cumulative with Phase 1) stays within 15-20%
- Table entries are not formulaic (quality metric: <50% formulaic entries)

**Dependencies**: M1 (Whittaker persona), M2 (panel integration -- Whittaker must be active to attack table entries)

**Risks**:
- **R-1 (Correctness theater)**: The table could become a checkbox exercise with formulaic entries. Mitigation: Whittaker validates entries by attempting attacks against them; track the GAP ratio as a quality signal.
- **R-3 (Context window competition)**: Structured tables consume tokens. Mitigation: Concise format with abbreviation conventions.

**Success metric links**:
- ">0 GAP cells per review" -- the table makes gaps visible by construction
- "<50% formulaic boundary table entries" -- quality gate on table content
- ">80% catch rate for boundary condition bugs" -- the table is the primary mechanism for this

---

## Phase 3: Depth and Breadth (Milestones M4-M6)

**Timeline**: Future, 5-8 days total (M4 and M5 can run in parallel)
**Theme**: Give the panel a dedicated correctness mode and teach it to analyze data pipelines.

Phase 3 has two parallel workstreams. M4 builds the `--focus correctness` mode that reconfigures the entire panel for correctness-intensive review. M5 adds pipeline dimensional analysis -- a targeted heuristic for catching data count mismatches in multi-stage processing. Both depend on the persona (M1-M2) and boundary table (M3) infrastructure from earlier phases, but they do not depend on each other.

---

### M4: Correctness Focus Mode (`--focus correctness`)

**Objective**: Add a `--focus correctness` flag that reconfigures the panel for deep correctness review, with a specialized 5-expert subset, three mandatory output artifacts, and an auto-suggestion heuristic.

**Why this matters**: Not every specification needs deep correctness analysis -- but when it does, the panel should shift its entire posture. The correctness focus mode assembles the right experts, mandates the right artifacts, and even suggests itself when it detects correctness-sensitive patterns in the spec.

**Deliverables**:

1. **`--focus correctness` flag** added to the Focus Areas section in `spec-panel.md`
2. **Specialized 5-expert panel**:
   - Nygard (lead) -- state and resilience
   - Fowler -- structural correctness
   - Adzic -- specification completeness
   - Crispin -- test boundary coverage
   - Whittaker -- adversarial attack surface
3. **Modified expert behaviors** (FR-14.1 through FR-14.6): Each expert's review priorities shift toward correctness concerns when this flag is active
4. **Three mandatory output artifacts**:
   - **State Variable Registry**: Template for cataloging all mutable state, transitions, and invariants
   - **Guard Condition Boundary Table**: Inherited from M3, now mandatory rather than triggered
   - **Pipeline Flow Diagram**: Visual specification of data flow stages (feeds into M5)
5. **Auto-suggestion heuristic** (FR-16): The panel suggests `--focus correctness` when it detects:
   - 3 or more mutable state variables
   - Numeric threshold guards
   - Pipeline or filter operations
6. **Usage line update**: Document the new focus option in the command usage section
7. **Validation**: Run `--focus correctness` against the v0.04 specification and measure overhead

**Acceptance criteria**:
- `--focus correctness` activates the 5-expert subset with modified behaviors
- All three mandatory artifacts are produced when the flag is active
- Auto-suggestion triggers with <30% false positive rate
- Token overhead with correctness focus is <= 25% above standard (no correctness focus)
- Token overhead without correctness focus is unchanged from Phase 2 baseline

**Dependencies**: M1 (Whittaker persona), M2 (panel integration), M3 (boundary table infrastructure)

**Risks**:
- **R-2 (Overhead exceeds tolerance)**: Correctness focus adds significant analysis. Mitigation: Phased implementation with measurement at each step; overhead budget is explicit (25%).
- **R-4 (False positives)**: Auto-suggestion may trigger on specs that do not need correctness focus. Mitigation: <30% false positive target; auto-suggestion is advisory, not mandatory.

**Success metric links**:
- ">80% catch rate for boundary condition bugs" -- correctness mode is the full expression of this capability
- "<40% overhead (Phase 3 correctness)" -- overhead budget for the complete system

---

### M5: Pipeline Dimensional Analysis

**Objective**: Add a heuristic that detects multi-stage data pipelines and verifies that quantity relationships (input count vs. output count) are explicitly specified and consistent across stages.

**Why this matters**: A common class of correctness bugs occurs when a pipeline stage silently changes the number of items flowing through it -- filters drop records, flatMaps multiply them, aggregations collapse them -- and downstream stages assume the count is unchanged. This heuristic catches those mismatches before they become runtime bugs.

**Deliverables**:

1. **Pipeline detection trigger**: Activates when the specification describes 2 or more stages of data flow where output count may differ from input count
2. **Four-step analysis process**:
   - **Pipeline Detection**: Identify multi-stage data flows in the specification
   - **Quantity Annotation**: For each stage, annotate whether output count equals, exceeds, or is less than input count
   - **Downstream Tracing**: Follow quantity changes through all subsequent stages
   - **Consistency Check**: Verify that downstream consumers account for quantity changes
3. **Expert role assignments**:
   - Fowler leads the analysis (structural patterns)
   - Whittaker attacks each stage (adversarial probe for silent data loss)
4. **Output artifact**: Quantity Flow Diagram showing stage-by-stage count relationships
5. **Severity rules**: Dimensional mismatches (unacknowledged count changes) are CRITICAL severity
6. **Downstream integration**: Quantity flow output feeds `sc:roadmap` RM-3 (state flow tracing)

**Acceptance criteria**:
- Pipeline detection triggers on specifications with 2+ stage data flows
- Quantity annotations are produced for every detected stage
- Dimensional mismatches are flagged as CRITICAL
- Token overhead: <5% when no pipelines detected, <=10% when pipelines detected
- Detection does not produce excessive false triggers on non-pipeline specifications

**Dependencies**: M1 (Whittaker persona), M2 (panel integration), M3 (boundary table -- pipeline stages may have guard conditions)

**Risks**:
- **R-5 (Pipeline detection under-triggers)**: The heuristic may miss pipelines described in unusual ways. Mitigation: Broad trigger condition (any 2+ stage flow); manual `--focus correctness` fallback forces pipeline analysis.
- **R-3 (Context window competition)**: Pipeline analysis adds tokens. Mitigation: Analysis only activates on detected pipelines; overhead is bounded.

**Success metric links**:
- ">80% catch rate for boundary condition bugs" -- pipeline dimensional mismatches are a subset of boundary bugs
- "<5% overhead when no pipelines" -- ensures the feature does not penalize non-pipeline specs

---

### M6: Validation and Release

**Objective**: Perform end-to-end validation of all capabilities (SP-1 through SP-4) working together, measure cumulative overhead, and confirm integration points with downstream commands.

**Why this matters**: Individual milestones are validated in isolation, but the complete system must work as a coherent whole. M6 is the integration gate that confirms all four capabilities interact correctly and that cumulative overhead stays within budget.

**Deliverables**:

1. **End-to-end validation suite**: Run the full enhanced panel (with and without `--focus correctness`) against at least three representative specifications:
   - A specification with mutable state and guard conditions (correctness-heavy)
   - A specification with multi-stage pipeline processing (pipeline-heavy)
   - A specification with neither (baseline -- overhead regression check)
2. **Cumulative overhead measurement**:
   - Without `--focus correctness`: target <25% overhead vs. pre-enhancement baseline
   - With `--focus correctness`: target <40% overhead vs. pre-enhancement baseline
3. **Integration point verification**:
   - SP-3 boundary table --> `sc:adversarial` AD-1 (invariant probe)
   - SP-2 attack findings --> `sc:adversarial` AD-2 (assumption extraction)
   - SP-1 correctness findings --> `sc:adversarial` AD-5 (taxonomy L3)
   - SP-4 quantity flow --> `sc:roadmap` RM-3 (state flow tracing)
   - SP-2 attack scenarios --> `sc:roadmap` RM-2 (negative ACs)
4. **Quality metric validation**:
   - Boundary table formulaic entry rate: <50%
   - Auto-suggestion false positive rate: <30%
   - Adversarial findings per review (with mutable state): >=2
   - GAP cells per review: >0
5. **Release documentation**: Updated changelog, version bump, migration notes if any

**Acceptance criteria**:
- All integration points produce valid, parseable output
- Overhead measurements are within budget
- Quality metrics meet targets
- No regressions in existing (non-correctness) panel behavior

**Dependencies**: M1, M2, M3, M4, M5 (all preceding milestones)

**Risks**: Low. This is validation and documentation work. The primary risk is discovering that cumulative overhead exceeds budget, which would require targeted optimization in M4 or M5.

---

## Risk Register

| ID | Risk | Probability | Impact | Phase | Mitigation | Owner | Status |
|----|------|-------------|--------|-------|-----------|-------|--------|
| R-1 | **Correctness theater** -- boundary tables become formulaic checkbox exercises that miss real bugs | Medium | High | 2-3 | Whittaker persona validates table entries by attempting attacks; track GAP ratio and formulaic entry rate as quality signals | M3, M4 | Open |
| R-2 | **Overhead exceeds tolerance** -- cumulative token cost makes the enhanced panel impractical | Medium | Medium | 1-3 | Phased implementation with measurement at each milestone; explicit overhead budgets per phase (10%, 20%, 25/40%) | M2, M4, M6 | Open |
| R-3 | **Context window competition** -- structured artifacts compete for limited context space | Low | Medium | 2-3 | Concise structured formats with abbreviation conventions; boundary table uses compact markdown | M3, M5 | Open |
| R-4 | **Adversarial tester false positives** -- Whittaker generates findings that are not actionable | Medium | Low | 1-3 | Require concrete state traces in every finding; synthesis step filters low-evidence findings | M1, M6 | Open |
| R-5 | **Pipeline detection under-triggers** -- heuristic misses pipelines described in unusual language | Low | Medium | 3 | Broad trigger condition (any 2+ stage data flow); manual `--focus correctness` as fallback | M5 | Open |
| R-6 | **Expert persona bloat** -- adding Whittaker creates precedent for unbounded expert growth | Low | Low | 1 | Whittaker's scope is explicitly bounded in persona definition; SP-5 deferred to prevent further expansion | M1 | Open |

---

## Success Criteria

### Primary Metric

| Metric | Target | Measurement | Linked Milestones |
|--------|--------|-------------|-------------------|
| Boundary condition bug catch rate | >80% | Run enhanced panel against specifications with known boundary bugs; measure detection rate | M3, M4, M6 |

### Secondary Metrics

| Metric | Target | Measurement | Linked Milestones |
|--------|--------|-------------|-------------------|
| GAP cells per review | >0 per review | Count GAP cells in boundary tables across reviews | M3, M6 |
| Adversarial findings per review (mutable state specs) | >=2 | Count Whittaker findings on specs with mutable state | M1, M2, M6 |

### Tertiary Metrics (Overhead Budgets)

| Metric | Target | Measurement | Linked Milestones |
|--------|--------|-------------|-------------------|
| Phase 1+2 overhead | <25% vs. baseline | Token count comparison on same specification | M2, M3, M6 |
| Phase 3 overhead (with correctness focus) | <40% vs. baseline | Token count comparison with `--focus correctness` | M4, M6 |
| Phase 3 overhead (without correctness focus) | <25% vs. baseline | Token count comparison without `--focus correctness` | M5, M6 |
| Pipeline analysis overhead (no pipelines) | <5% | Token count on non-pipeline specification | M5, M6 |

### Quality Metrics

| Metric | Target | Measurement | Linked Milestones |
|--------|--------|-------------|-------------------|
| Formulaic boundary table entries | <50% | Manual review of table entry diversity | M3, M6 |
| Auto-suggestion false positive rate | <30% | Track suggestion triggers vs. actual correctness need | M4, M6 |

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

All downstream formats are machine-parseable structured markdown. No downstream changes are required in this release -- the integration contract is output format compatibility.

---

## Deferred Work

### SP-5: Cross-Expert Challenge Protocol

**Prioritization score**: 57.5/100 (B-Tier)
**Reason for deferral**: SP-5 requires experts to formally challenge each other's findings. This is valuable but premature -- the protocol depends on Whittaker's attack findings being well-calibrated, which can only be validated after SP-2 has been used in practice across multiple reviews.
**Revisit trigger**: After SP-2 has been active for at least 10 reviews and the false positive rate (R-4) is measured below threshold.

---

## Appendix: Phase-to-Milestone Mapping

| Phase | Name | Milestones | Duration | Cumulative Overhead Target |
|-------|------|-----------|----------|---------------------------|
| 1 | Adversarial Mindset | M1, M2 | 1-3 days | 5-10% |
| 2 | Structural Forcing Functions | M3 | 3-5 days | 15-20% |
| 3 | Depth and Breadth | M4, M5, M6 | 5-8 days | 25% (standard) / 40% (correctness focus) |
