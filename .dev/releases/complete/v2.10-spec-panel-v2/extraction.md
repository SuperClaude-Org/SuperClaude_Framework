---
schema_version: "2.0.0"
spec_source: ".dev/releases/current/v2.06-spec-panel-v2/spec-panel-release-spec.md"
document_id: "SPEC-PANEL-2026-Q1"
generated: "2026-03-04T00:00:00Z"
generator: "sc:roadmap"
extraction_date: "2026-03-04"
extraction_mode: "standard (511 lines, below 500-line chunked threshold)"
extractor_version: "sc:roadmap v2.0.0"
functional_requirements: 21
nonfunctional_requirements: 10
total_requirements: 31
domains_detected: [documentation, quality, performance, security, backend]
complexity_score: 0.561
complexity_class: MEDIUM
risks_identified: 7
dependencies_identified: 7
success_criteria_count: 5

summary:
  project_title: "/sc:spec-panel Correctness & Adversarial Review Enhancements"
  project_version: "1.0"
  one_liner: "Adds adversarial tester persona, mandatory boundary table, correctness focus area, and pipeline dimensional heuristic to catch execution-correctness bugs in specifications."

counts:
  functional_requirements: 21
  non_functional_requirements: 10
  dependencies: 7
  success_criteria: 5
  risks: 7

complexity:
  score: 0.561
  class: "MEDIUM"
  milestone_range: "5-7"
  interleave_ratio: "1:2"
  factors:
    requirement_count_raw: 31
    requirement_count_norm: 0.62
    dependency_depth_raw: 3
    dependency_depth_norm: 0.375
    domain_spread_raw: 4
    domain_spread_norm: 0.80
    risk_severity_raw: 2.0
    risk_severity_norm: 0.50
    scope_size_raw: 511
    scope_size_norm: 0.511

domain_distribution:
  documentation: 40
  quality: 35
  performance: 10
  security: 10
  backend: 5

personas:
  primary: "scribe"
  primary_confidence: 0.364
  consulting:
    - persona: "qa"
      confidence: 0.269
    - persona: "architect"
      confidence: 0.269

phases:
  - id: "Phase-1"
    name: "Adversarial Mindset"
    timeline: "Immediate (1-3 days)"
    items: ["SP-2 adversarial tester persona"]
    dependencies: []
  - id: "Phase-2"
    name: "Structural Forcing Functions"
    timeline: "Next Cycle (3-5 days)"
    items: ["SP-3 guard condition boundary table"]
    dependencies: ["Phase-1"]
  - id: "Phase-3"
    name: "Depth and Breadth"
    timeline: "Future (5-8 days, after Phase 1-2 validation)"
    items: ["SP-1 --focus correctness", "SP-4 pipeline dimensional analysis"]
    dependencies: ["Phase-1", "Phase-2"]

deferred:
  - id: "SP-5"
    name: "Cross-Expert Challenge Protocol"
    score: 57.5
    tier: "B-Tier"
    reason: "High overhead (20-30%), no new analytical techniques, dependent on SP-2 validation"

integration_points:
  - source: "SP-3 boundary table"
    target: "sc:adversarial AD-1 invariant probe"
    mechanism: "Structured markdown table consumed as priority probe targets"
  - source: "SP-2 attack findings"
    target: "sc:adversarial AD-2 assumption extraction"
    mechanism: "Attack findings become candidate shared assumptions"
  - source: "SP-1 correctness findings"
    target: "sc:adversarial AD-5 taxonomy L3"
    mechanism: "Findings map to state mechanics debate level"
  - source: "SP-4 quantity flow diagrams"
    target: "sc:roadmap RM-3 state flow tracing"
    mechanism: "Diagrams referenced as pipeline-specific flow base"
  - source: "SP-2 attack scenarios"
    target: "sc:roadmap RM-2 negative ACs"
    mechanism: "Each attack failure mode becomes negative AC candidate"
---

# Extraction: /sc:spec-panel Correctness & Adversarial Review Enhancements

## Functional Requirements

| ID | Description | Priority | Domain | Source Lines |
|----|-------------|----------|--------|-------------|
| FR-001 | Spec-panel SHALL include new expert persona "James Whittaker" as Adversarial Testing Pioneer | P0 | quality, documentation | L112 |
| FR-002 | Adversarial tester SHALL execute 5 attack methodologies: Zero/Empty, Divergence, Sentinel Collision, Sequence, Accumulation | P0 | quality | L114–L124 |
| FR-003 | Adversarial tester SHALL produce findings in structured format: "I can break this specification by [attack]. The invariant at [location] fails when [condition]. Concrete attack: [scenario with state trace]." | P0 | quality, documentation | L125–L127 |
| FR-004 | Adversarial tester SHALL be activated in ALL focus areas; leads when `--focus correctness` specified | P0 | quality | L128–L130 |
| FR-005 | Adversarial tester SHALL review AFTER Fowler and Nygard, attacking every interface contract and guard condition they identified | P0 | quality | L131–L133 |
| FR-006 | Spec-panel SHALL produce Guard Condition Boundary Table as mandatory output whenever spec contains conditional logic, threshold checks, boolean guards, or sentinel value comparisons | P0 | quality | L170–L173 |
| FR-007 | Boundary table SHALL contain 7 columns (Guard, Location, Input Condition, Variable Value, Guard Result, Specified Behavior, Status) with 6 input condition rows per guard (zero/empty, one/minimal, typical, max/overflow, sentinel match, legitimate edge case) | P0 | quality | L174–L184 |
| FR-008 | Any GAP cell SHALL automatically generate a finding at MAJOR severity minimum | P0 | quality | L185–L186 |
| FR-009 | Any row where "Specified behavior" is blank or "unspecified" SHALL be classified as at least MAJOR severity | P0 | quality | L187–L188 |
| FR-010 | Boundary table SHALL be completed before synthesis output is generated; incomplete tables SHALL block synthesis | P0 | quality | L189–L190 |
| FR-011 | Nygard leads boundary table construction; Crispin validates completeness; Whittaker (SP-2) attacks each table entry | P0 | quality | L191–L192 |
| FR-012 | Spec-panel SHALL support `--focus correctness` as a fifth focus area targeting execution correctness of stateful specifications | P0 | quality, documentation | L244–L246 |
| FR-013 | Correctness focus expert panel SHALL consist of: Nygard (lead), Fowler, Adzic, Crispin, Whittaker | P0 | quality | L248–L250 |
| FR-014 | Each correctness focus expert SHALL apply modified methodology: Wiegers (implicit state assumptions), Fowler (data flow annotation), Nygard (guard boundary enumeration), Adzic (state-annotated Given/When/Then/State scenarios), Crispin (boundary value tests), Whittaker (invariant attacks) | P0 | quality | L251–L263 |
| FR-015 | Correctness focus SHALL produce 3 mandatory outputs: State Variable Registry (mutable vars + invariants + operations), Guard Condition Boundary Table (per SP-3), Pipeline Flow Diagram (annotated with counts, when pipelines present) | P0 | quality, documentation | L264–L267 |
| FR-016 | Spec-panel SHALL auto-suggest `--focus correctness` (as recommendation, not forced) when spec introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations | P1 | quality | L268–L271 |
| FR-017 | Pipeline dimensional analysis heuristic SHALL trigger when spec describes data flowing through 2+ stages where output count can differ from input count (filtering, transformation, aggregation, deduplication) | P0 | quality | L320–L325 |
| FR-018 | When triggered, heuristic SHALL execute: Pipeline Detection → Quantity Annotation → Downstream Tracing → Consistency Check | P0 | quality | L326–L336 |
| FR-019 | Any dimensional mismatch SHALL be classified as CRITICAL severity by default | P0 | quality | L337–L338 |
| FR-020 | Fowler SHALL lead pipeline identification and quantity annotation; Whittaker SHALL attack each annotated stage with divergence attacks | P0 | quality | L339–L341 |
| FR-021 | Heuristic SHALL produce a Quantity Flow Diagram showing counts at each pipeline stage and annotating which count each downstream consumer uses | P0 | quality, documentation | L342–L344 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|------------|-------------|
| NFR-001 | Adversarial tester persona SHALL add no more than 10% token overhead per invocation | performance | ≤10% overhead | L135–L136 |
| NFR-002 | Adversarial tester persona definition SHALL follow existing expert panel YAML structure | maintainability | Match existing YAML schema | L137–L138 |
| NFR-003 | Attack findings SHALL use existing severity classification system (CRITICAL, MAJOR, MINOR) | compliance | Existing severity enum | L139–L140 |
| NFR-004 | Guard condition boundary table SHALL add no more than 10% token overhead per invocation | performance | ≤10% overhead | L196–L197 |
| NFR-005 | Boundary table format SHALL be structured markdown table (not prose) for downstream machine consumption | maintainability | Structured markdown | L198–L199 |
| NFR-006 | Boundary table SHALL appear in a dedicated "Mandatory Artifacts" section of panel output | documentation | Dedicated section | L200–L201 |
| NFR-007 | Correctness focus SHALL add no more than 25% token overhead compared to a standard focus invocation | performance | ≤25% overhead | L273–L274 |
| NFR-008 | Auto-suggestion heuristic (FR-016) SHALL have a false positive rate below 30% | reliability | <30% false positive rate | L275–L276 |
| NFR-009 | Pipeline heuristic SHALL add less than 5% token overhead when no pipelines are detected | performance | <5% overhead (no pipelines) | L348–L349 |
| NFR-010 | When pipelines are detected, pipeline heuristic SHALL add no more than 10% additional overhead | performance | ≤10% overhead (with pipelines) | L350–L351 |

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|-----------------------|
| DEP-001 | SP-3 boundary table validation requires SP-2 adversarial tester (Whittaker attacks entries) | internal | FR-011 ← FR-001..FR-005 |
| DEP-002 | SP-1 correctness focus requires SP-2 (Whittaker in panel) and SP-3 (boundary table mandatory output) | internal | FR-012..FR-015 ← FR-001..FR-011 |
| DEP-003 | SP-4 pipeline heuristic requires SP-2 (Whittaker divergence attack on each stage) | internal | FR-017..FR-021 ← FR-001..FR-005 |
| DEP-004 | SP-3 boundary table output designed for consumption by sc:adversarial (AD-1) and sc:roadmap (RM-1) | external | FR-006..FR-011 → downstream |
| DEP-005 | SP-2 attack findings feed sc:adversarial (AD-2) and sc:roadmap (RM-2) | external | FR-001..FR-005 → downstream |
| DEP-006 | Phase 2 (SP-3) depends on Phase 1 (SP-2) completion — Whittaker must exist before validating boundary tables | internal | FR-006..FR-011 ← FR-001..FR-005 |
| DEP-007 | Phase 3 (SP-1, SP-4) depends on Phase 1 (SP-2) AND Phase 2 (SP-3) completion per spec phasing rules | internal | FR-012..FR-021 ← FR-001..FR-011 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | >80% catch rate for boundary condition bugs — validated by retrospective analysis on past specs where bugs were later found | FR-001..FR-021 | Yes |
| SC-002 | >0 GAP cells in boundary tables for specs with guard conditions (table is substantively completed) | FR-006..FR-011 | Yes |
| SC-003 | ≥2 adversarial tester findings per review for specs with mutable state | FR-001..FR-005 | Yes |
| SC-004 | <25% token overhead for Phase 1+2 combined; <40% for Phase 3 with correctness focus active | NFR-001, NFR-004, NFR-007 | Yes |
| SC-005 | <50% formulaic boundary table entries assessed via quarterly manual audit | FR-006..FR-011 | Yes (manual) |

## Risks

| ID | Description | Probability | Impact | Affected Requirements |
|----|-------------|-------------|--------|----------------------|
| RISK-001 | Correctness theater: formulaic low-quality boundary table entries satisfy structure without genuine analysis | Medium | High | FR-006..FR-011 |
| RISK-002 | Cumulative overhead of all phases exceeds 40% token budget ceiling | Medium | Medium | NFR-001, NFR-004, NFR-007 |
| RISK-003 | Context window competition: artifacts consume context needed for expert analysis depth | Low | Medium | FR-006..FR-011, FR-015 |
| RISK-004 | Adversarial tester produces false positives for well-specified systems without mutable state | Medium | Low | FR-001..FR-005 |
| RISK-005 | Pipeline detection heuristic under-triggers for complex non-obvious data flows | Low | Medium | FR-017..FR-021 |
| RISK-006 | Expert persona bloat (11 experts) increases cognitive load and prompt coordination complexity | Low | Low | FR-012..FR-013 |
| RISK-007 | Integration drift: sc:adversarial and sc:roadmap do not consume SP-3/SP-4 artifacts as designed | Medium | High | DEP-004, DEP-005 |

## Deferred Items

| ID | Name | Score | Reason |
|----|------|-------|--------|
| SP-5 | Cross-Expert Challenge Protocol | 57.5/100 (B-Tier) | High overhead (20–30%), no new analytical techniques, dependent on SP-2 validation before revisit |
