---
spec_source: .dev/releases/current/v.2.08-roadmap-v4/brainstorm-roadmap.md
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
functional_requirements: 10
nonfunctional_requirements: 5
total_requirements: 15
domains_detected: [documentation, quality, backend]
complexity_score: 0.378
complexity_class: LOW
risks_identified: 5
dependencies_identified: 4
success_criteria_count: 5
extraction_mode: standard
---

# Extraction: sc:roadmap Enhancement — Edge Case and Invariant Violation Coverage

**Spec**: `.dev/releases/current/v.2.08-roadmap-v4/brainstorm-roadmap.md`
**Extraction date**: 2026-03-04
**Mode**: Single-pass (203 lines < 500-line chunked threshold)

---

## Project Overview

**Title**: sc:roadmap Enhancement — Edge Case and Invariant Violation Surface Coverage

**Context**: Two bugs escaped the v0.04 roadmap planning phase. Both involved state-tracking variables whose correctness depended on conditions (filtering, empty inputs) that were never identified as separate deliverables or risks. This spec proposes five complementary enhancements to sc:roadmap's deliverable generation methodology to systematically surface such bugs during planning.

**Motivating bugs**:
- Bug 1: `_loaded_start_index -= mounted` used widget count instead of `events_consumed` — wrong operand in state mutation
- Bug 2: `_replayed_event_offset = len(plan.tail_events)` = 0 when `tail_events` is empty after condensation — zero ambiguity in guard sentinel

---

## Functional Requirements

| ID | Description | Priority | Source Lines |
|----|-------------|----------|-------------|
| FR-001 | **State Variable Invariant Registry**: for each deliverable introducing or modifying a state-tracking variable (counters, offsets, flags, cursors), generate: (1) invariant predicate in plain-language predicate form, (2) mutation inventory of every code path that writes to the variable, (3) edge case inputs per mutation site (zero, negative, type mismatch), (4) verification deliverable asserting the invariant after each mutation path | P1 | L10-L38 |
| FR-002 | **FMEA Pass**: after deliverable generation, execute a Failure Mode and Effects Analysis over each computational deliverable, asking: (1) what inputs can this computation receive including degenerate cases, (2) what happens if the result is correct in type but wrong in value, (3) what downstream consumers depend on the result and what they assume. Output a failure mode table with each mode either promoted to a test deliverable or documented as accepted risk | P1 | L42-L74 |
| FR-003 | **Guard and Sentinel Analysis**: for each deliverable introducing conditional logic (guards, sentinels, flags, early returns), enumerate all states the guard variable can hold and their semantic meanings, detect ambiguous states (one value mapping to multiple meanings), perform transition analysis for type changes (bool→int, enum→string), require disambiguation mechanism or accepted-risk documentation when ambiguity is detected | P1 | L78-L106 |
| FR-004 | **Implement/Verify Decomposition**: split every behavioral deliverable D.x into D.x.a (implement — the feature implementation) and D.x.b (verify — a test targeting internal correctness including: input domain boundary tests, operand identity tests, post-condition assertions on internal state variables, not just external behavior) | P1 | L109-L143 |
| FR-005 | **Cross-Deliverable Data Flow Tracing**: generate a data flow trace following each mutable state variable from creation through all deliverables that read or write it. Include: variable birth (initial value, semantic meaning), write trace (mutation expression + intended semantics), read trace (reader assumptions), cross-milestone contract extraction, conflict detection between writer semantics and reader assumptions | P2 | L146-L173 |
| FR-006 | Automatic scanning during deliverable generation for state variable introductions: assignments to `self._*` fields, new class attributes, counter/offset/cursor patterns. Each detected variable triggers invariant registry entry generation (mechanism for FR-001) | P1 | L19-L26 |
| FR-007 | Automatic scanning of deliverable descriptions for computational verbs (compute, extract, filter, count, calculate, determine, select) to trigger the FMEA pass on that deliverable (mechanism for FR-002) | P1 | L55-L62 |
| FR-008 | Silent corruption failures — where the system continues operating with wrong internal state and no crash — must be classified as highest severity in FMEA output, above crash and degraded-UX failures | P0 | L61-L63 |
| FR-009 | Guard analysis transition analysis (within FR-003): for any type migration change in a deliverable (bool→int, int→enum, enum→string), verify that every semantic state from the old type maps to a unique, unambiguous state in the new type. If not, flag as ambiguity requiring resolution | P1 | L90-L93 |
| FR-010 | Data flow trace (within FR-005) must explicitly capture: variable birth record, per-deliverable write trace entries, per-deliverable read trace entries, cross-milestone implicit contracts extracted as explicit acceptance criteria, and conflict flags where writer semantics ≠ reader assumptions | P1 | L156-L169 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|-----------|-------------|
| NFR-001 | Proposals 1 and 2 (invariant registry + FMEA) have medium implementation cost — they are analysis passes over existing deliverable generation | maintainability | Medium effort; does not require restructuring existing pipeline | L178-L185 |
| NFR-002 | Proposals 3 and 4 (guard analysis + implement/verify decomposition) have low implementation cost — they are structural changes to deliverable generation, not new analysis passes | maintainability | Low effort; can be added in Phase 1 without touching other proposals | L178-L185 |
| NFR-003 | Proposal 5 (data flow tracing) has high implementation cost and must execute as a post-generation pass, not during deliverable generation. Recommended only for roadmaps with 6+ milestones | maintainability | High effort; conditional activation by milestone count | L184-L192 |
| NFR-004 | All 5 proposals must be composable — designing them as alternatives is explicitly prohibited. Incremental adoption must be supported (Phase 1 → 2 → 3) without requiring all proposals to be active simultaneously | maintainability | No mutual exclusion between proposals | L196-L202 |
| NFR-005 | All artifacts produced by proposals (invariant tables, failure mode tables, guard analysis tables, verify sub-deliverables, data flow traces) must serve double duty: usable as implementation guidance during development AND as review checklists during code review | maintainability | Dual-purpose artifacts | L202-L203 |

---

## Dependencies

| ID | Description | Type | Affected Requirements | Source Lines |
|----|-------------|------|-----------------------|-------------|
| DEP-001 | FR-005 (cross-deliverable data flow tracing) requires the full roadmap deliverable list to be generated before it can execute — it is a post-generation analysis pass, not part of deliverable generation | internal | FR-005 | L192 |
| DEP-002 | FR-007 (computational verb scanning) is the trigger mechanism for FR-002 (FMEA pass) — FMEA cannot activate without the scanning step | internal | FR-002, FR-007 | L55-L58 |
| DEP-003 | FR-006 (state variable scanning) is the trigger mechanism for FR-001 (invariant registry) — the registry cannot be populated without the scanning step | internal | FR-001, FR-006 | L19-L26 |
| DEP-004 | FR-004 (implement/verify decomposition) is a structural prerequisite for FR-001 and FR-002 to produce their verify sub-deliverables in a standardized format | internal | FR-001, FR-002, FR-004 | L188-L190 |

---

## Success Criteria

| ID | Description | Derived From | Measurable | Source Lines |
|----|-------------|--------------|------------|-------------|
| SC-001 | The invariant registry (FR-001) + implement/verify decomposition (FR-004) together catch Bug 1 class: wrong operand in state mutation during load_older_events — surfaced during planning, not post-deployment | FR-001, FR-004 | Yes — example fully traced in spec | L27-L29 |
| SC-002 | Guard analysis (FR-003) + FMEA pass (FR-002) together catch Bug 2 class: zero/empty ambiguity in sentinel guard after type migration bool→int — surfaced during planning | FR-002, FR-003 | Yes — example fully traced in spec | L31-L33 |
| SC-003 | All 5 proposals produce artifacts usable as both implementation guidance and review checklists — no artifact is purpose-limited | FR-001, FR-002, FR-003, FR-004, FR-005 | Yes — explicitly stated | L202-L203 |
| SC-004 | Proposals are implementable incrementally: Phase 1 (P3+P4, low cost), Phase 2 (P1+P2, medium cost), Phase 3 (P5, high cost) without requiring redesign between phases | NFR-004 | Yes — phased ordering with rationale defined | L197-L200 |
| SC-005 | Silent corruption failures (system continues with wrong state) are surfaced by FMEA at planning time and classified as highest severity — before they can escape to production | FR-008 | Yes — severity classification is a required output field | L61-L63 |

---

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|-----------------------|--------|
| RISK-001 | Data flow tracing (FR-005) has high implementation cost and may introduce unacceptable generation overhead for small/medium roadmaps where cross-milestone state sharing is rare | Medium | High | FR-005 | L184-L192 |
| RISK-002 | Automated state variable scanning (FR-006) may miss non-standard patterns: closures capturing local state, module-level globals, dataclass fields without `self._*` prefix | Medium | Medium | FR-001, FR-006 | inferred |
| RISK-003 | FMEA pass (FR-002, FR-007) adds per-deliverable analysis time — for large specs with many computational deliverables, this may make roadmap generation impractically slow | Low | Medium | FR-002, FR-007 | inferred |
| RISK-004 | Implement/verify decomposition (FR-004) may over-fragment simple deliverables (pure configuration, rendering-only) where edge cases are trivial, increasing roadmap verbosity without proportional bug-catching value | Low | Medium | FR-004 | inferred |
| RISK-005 | Guard analysis (FR-003) for complex multi-variable guards (compound boolean expressions, guard chains) may require human review rather than automated enumeration — automated coverage may be incomplete | Low | Medium | FR-003, FR-009 | inferred |

---

## Domain Distribution

| Domain | Score | % | Driver Requirements |
|--------|-------|---|-------------------|
| Documentation/Methodology | 8.0 | 45% | All FRs (improvements to roadmap generation methodology = meta-documentation work) |
| Quality/Testing | 7.0 | 39% | FR-002 (FMEA), FR-004 (verify sub-deliverables), FR-008 (severity), SC-001, SC-002 |
| Backend/Systems | 3.0 | 16% | FR-001 (state variables), FR-005 (data flow), FR-006 (scanning), FR-009 (type transitions) |

**Primary persona selected**: `architect` (generalist — most appropriate for meta-methodology work spanning documentation, quality engineering, and systems analysis)
**Consulting personas**: `qa` (quality domain 39%), `scribe` (documentation domain 45%)

---

## Complexity Scoring

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 15 (10 FR + 5 NFR) | 0.30 | 0.25 | 0.075 |
| dependency_depth | 2 (max chain: DEP-004→FR-004→FR-001) | 0.25 | 0.25 | 0.063 |
| domain_spread | 3 (documentation, quality, backend) | 0.60 | 0.20 | 0.120 |
| risk_severity | 1 high-impact + 4 medium-impact = (3+8)/5 = 2.2 avg | 0.60 | 0.15 | 0.090 |
| scope_size | 203 lines | 0.20 | 0.15 | 0.030 |

**Complexity score**: 0.075 + 0.063 + 0.120 + 0.090 + 0.030 = **0.378**
**Classification**: LOW (< 0.4) → 3-4 milestones, 1:3 interleave ratio

> Note: Despite low raw complexity score, --compliance strict and --depth deep are active. Wave 2 will apply --multi-roadmap with opus + haiku agents, which adds adversarial planning depth appropriate for this methodology improvement work.
