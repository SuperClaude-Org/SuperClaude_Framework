---
spec_source: .dev/releases/current/v.2.08-roadmap-v4/brainstorm-roadmap.md
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.378
complexity_class: LOW
domain_distribution:
  documentation: 45
  quality: 39
  backend: 16
  frontend: 0
  security: 0
  performance: 0
primary_persona: architect
consulting_personas: [qa, scribe]
milestone_count: 4
milestone_index:
  - id: M1
    title: Deliverable Decomposition and Schema Extension
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 8
    risk_level: Low
  - id: M2
    title: State Variable Invariant Registry + FMEA Pass
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 18
    risk_level: Medium
  - id: M3
    title: Guard and Sentinel Analysis
    type: FEATURE
    priority: P1
    dependencies: [M1, M2]
    deliverable_count: 6
    risk_level: Medium
  - id: M4
    title: Cross-Deliverable Data Flow Tracing
    type: FEATURE
    priority: P2
    dependencies: [M1, M2, M3]
    deliverable_count: 12
    risk_level: High
total_deliverables: 44
total_risks: 15
estimated_phases: 3
validation_score: 0.906
validation_status: PASS
adversarial:
  mode: multi-roadmap
  agents: [opus:architect, haiku:architect]
  convergence_score: 0.82
  base_variant: opus:architect
  artifacts_dir: .dev/releases/current/v.2.08-roadmap-v4/adversarial/
---

# Roadmap: sc:roadmap Edge Case and Invariant Violation Detection

## Overview

This roadmap implements five methodology enhancements to the `sc:roadmap` deliverable generation pipeline. The motivation is two concrete bugs from v0.04 that escaped planning: (1) `_loaded_start_index -= mounted` used widget count instead of `events_consumed` — a wrong-operand state mutation; (2) `_replayed_event_offset = len(plan.tail_events)` set to zero on empty tail — a boolean-to-integer sentinel ambiguity. Both bugs shared a root cause: state-variable mutations were treated as atomic deliverables without invariant assertions, edge-case enumeration, or cross-deliverable data flow verification.

The five proposals address this gap at different abstraction levels and are implemented in four milestones ordered by cost/impact ratio. M1 (Proposal 4 — Implement/Verify decomposition) is the structural foundation that all subsequent passes build against. M2 (Proposals 1+2 — Invariant Registry + FMEA) layers detection of state variable invariant violations and computational failure modes. M3 (Proposal 3 — Guard Analysis) adds sentinel and type-transition ambiguity detection with enforcement via release gating. M4 (Proposal 5 — Data Flow Tracing) adds cross-milestone contract extraction, conditionally activated for roadmaps with 6+ milestones.

All enhancements operate as **post-generation passes** over the existing roadmap generator's deliverable list. The existing generator's output schema is the integration contract. This design preserves backward compatibility, enables incremental adoption (Phase 1: M1 → Phase 2: M2+M3 → Phase 3: M4), and allows each pass to be composed, reordered, or disabled independently.

**Adversarial generation note**: This roadmap was generated via adversarial comparison of opus:architect and haiku:architect variants (convergence: 82%). Key merge decisions: M2 groups Proposals 1+2 together (V2 grouping adopted by V1 in Round 3); FMEA uses dual detection signals independent of M2 completeness (V1 architecture retained); release gating with mandatory owner is incorporated from V2 (U-003); M4 pilot deliverable incorporated from V2 (U-004); constrained invariant predicate grammar incorporated from V1 (U-001).

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Deliverable Decomposition and Schema Extension | FEATURE | P0 | S | None | 8 | Low |
| M2 | State Variable Invariant Registry + FMEA Pass | FEATURE | P0 | L | M1 | 18 | Medium |
| M3 | Guard and Sentinel Analysis | FEATURE | P1 | S | M1, M2 | 6 | Medium |
| M4 | Cross-Deliverable Data Flow Tracing | FEATURE | P2 | M | M1, M2, M3 | 12 | High |

---

## Dependency Graph

```
M1 (Decomposition + Schema)
│
└──► M2 (Invariant Registry + FMEA — shared detection infrastructure)
     │
     └──► M3 (Guard Analysis — uses invariant predicates + FMEA severity)
          │
          └──► M4 (Data Flow Tracing — conditional: 6+ milestones)
```

Linearized: **M1 → M2 → M3 → M4**

Dependency rationale:
- M2 depends on M1: the invariant registry and FMEA pass attach metadata to the extended deliverable schema defined in M1; verification deliverables use the Implement/Verify pair structure from Proposal 4
- M3 depends on M1 (targets Implement deliverables) and M2 (guard severity classification requires both invariant predicates and FMEA output to determine whether ambiguity constitutes silent corruption)
- M4 depends on all prior milestones: reads invariant predicates (M2), failure mode tables (M2), guard analysis (M3), and Implement/Verify pairs (M1) to construct cross-deliverable contracts

---

## Release Gating

This methodology only delivers value if its findings are acted on. The following enforcement rules apply across all milestones:

**Rule 1 — Silent Corruption Block**: Any FMEA finding classified as silent corruption (system continues with wrong internal state, no error raised) blocks downstream milestone progression until either: (a) a mitigation deliverable is accepted, or (b) the finding is explicitly accepted as risk with a named owner and documented rationale.

**Rule 2 — Guard Ambiguity Gate**: Any guard ambiguity flagged by M3 that is not resolved by a disambiguation deliverable becomes a release gate warning. The warning requires a mandatory owner field and review date before the next milestone begins.

**Rule 3 — Verify Deliverable Quality**: Exit criteria for each milestone require that all `.b` verify deliverables contain at least one state assertion or boundary case tied to the corresponding `.a` deliverable's internal state. Generic "tests pass" is not sufficient.

---

## M1: Deliverable Decomposition and Schema Extension

### Objective

Implement Proposal 4 (Implement/Verify pair decomposition) and extend the deliverable schema to support metadata attachments from subsequent analytical passes. This milestone establishes the structural contract that all downstream milestones build against. No analytical logic is introduced — only the decomposition rule and the schema surface.

The core insight: every behavioral deliverable `D.x` becomes `D.x.a` (Implement) and `D.x.b` (Verify). The Verify deliverable targets internal correctness — input domain boundaries, operand identity, post-condition assertions on internal state — not just external behavior.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1a | Define extended deliverable schema with `kind` field (`implement`, `verify`, `invariant_check`, `fmea_test`, `guard_test`, `contract_test`) and `metadata` attachment point | Schema definition exists. All six `kind` values enumerated. `metadata` defaults to empty dict. Unknown `kind` raises ValueError. Round-trip serialization preserves `kind` and `metadata`. Existing deliverables without `kind` default to `implement`. |
| D1.1b | Verify extended deliverable schema | Tests: (1) unknown `kind` raises ValueError, (2) `metadata` defaults to empty dict, (3) pre-extension deliverables default to `implement`, (4) backward-compatibility: existing roadmaps parse without error. |
| D1.2a | Implement decomposition rule: behavioral deliverables split into `D.x.a` (Implement) and `D.x.b` (Verify) pairs | Decomposition function expands behavioral deliverables into Implement/Verify pairs. Non-behavioral deliverables pass through unchanged. ID suffixes `.a` and `.b` appended correctly. Already-decomposed deliverables (IDs ending in `.a`/`.b`) not re-decomposed. |
| D1.2b | Verify decomposition rule | Tests: (1) 3 behavioral → 6 output, (2) 2 behavioral + 1 doc → 5 output, (3) empty → empty, (4) already-decomposed not re-decomposed, (5) Verify description references Implement deliverable by ID. |
| D1.3a | Implement behavioral detection heuristic for deliverable descriptions | Heuristic detects: computational verbs (compute, extract, filter, count, calculate, determine, select, track, increment, update, replace, introduce), state mutation patterns (`self._*`, counter/offset/cursor), conditional logic patterns (guard, sentinel, flag, early return). Returns boolean `is_behavioral`. |
| D1.3b | Verify behavioral detection heuristic | Tests: (1) "Replace boolean with int offset" → behavioral, (2) "Document API endpoint" → not behavioral, (3) "Add type definition for GateResult" → not behavioral, (4) "Implement retry with bounded attempts" → behavioral, (5) "Update README" → not behavioral, (6) empty description → false. |
| D1.4a | Integrate decomposition into roadmap generator pipeline as a post-generation pass | Pass runs after deliverable generation, before output formatting. Idempotent (running twice = same result). Preserves deliverable ordering within each milestone. |
| D1.4b | Verify generator integration | Integration test: known spec → output contains Implement/Verify pairs for all behavioral deliverables; non-behavioral unchanged; milestone structure preserved. Exit criterion: all `.b` deliverables contain at least one state assertion or boundary case (Release Gate Rule 3). |

### Dependencies

None. This is the foundation milestone.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Behavioral detection false positives on documentation deliverables | Low | Low | Negative signal suppression (doc-specific verbs: document, describe, explain, list). Tunable threshold. |
| R-002: ID suffix scheme (`.a`, `.b`) collides with existing conventions | Low | Medium | Validate against existing roadmap corpus. Fallback: `/impl` and `/verify` suffixes. |
| R-003: Decomposition increases deliverable count, readability impact | Medium | Low | Visual distinction in output formatting. Collapse option for summary views. |

---

## M2: State Variable Invariant Registry + FMEA Pass

### Objective

Implement Proposals 1 and 2 as a combined analytical milestone. Both share trigger detection infrastructure (text scanning over deliverable descriptions), are complementary (invariant registry defines expected state truth; FMEA models failure propagation), and their cross-linking (D2.9) requires both to be in the same milestone.

This is the proposal that would have caught both source bugs: the invariant registry for `_loaded_start_index` would have required "offset must advance by exactly the number of events consumed" — not widgets mounted; and the FMEA pass on `_replayed_event_offset = len(plan.tail_events)` would have flagged the empty-tail case as a value-correct, type-correct, semantically-wrong failure.

**FMEA detection uses dual signals**: (1) cross-reference against invariant predicates to detect invariant violations without error output, and (2) independent "no error path" detection for computations that produce wrong values silently. Both signals contribute to severity classification. The independent signal ensures FMEA quality does not depend entirely on M2's invariant registry completeness.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1a | Implement invariant registry data structure: `InvariantEntry(variable_name, scope, invariant_predicate, mutation_sites[], verification_deliverable_ids[])` | Data structure instantiates with all fields. `invariant_predicate` uses constrained grammar: `variable_name comparison_op expression [AND\|OR ...]`. `mutation_sites` is a list of `MutationSite(location, expression, context)`. |
| D2.1b | Verify invariant registry data structure | Tests: (1) empty `mutation_sites` valid, (2) `verification_deliverable_ids` can cross milestones, (3) serialization round-trip preserves all fields, (4) duplicate `variable_name` within same scope warns. |
| D2.2a | Implement state variable detector: scan deliverable descriptions for state variable introduction patterns | Detects: `self._*` assignments, "introduce variable", "add counter/offset/cursor/flag", "replace X with Y" where Y is state-tracking type (int, bool, enum, cursor). Returns `(variable_name, deliverable_id, introduction_type)` tuples. Low-confidence detections flagged for human review. |
| D2.2b | Verify state variable detector | Tests: (1) "Replace boolean with int offset" → replacement, (2) "Add replay guard flag" → flag, (3) "Document offset behavior" → not detected, (4) "Introduce cursor for pagination" → cursor, (5) multiple variables in one deliverable handled. |
| D2.3a | Implement mutation inventory generator: enumerate code paths that write to each detected variable | Parses descriptions for mutation indicators: "update X", "increment X", "reset X", "set X to", "advance X by", "clear X". Cross-references all roadmap deliverables (not just introducing deliverable). Ambiguous mutations flagged for human review. |
| D2.3b | Verify mutation inventory generator | Tests: (1) variable introduced in D2.3, mutated in D3.1 and D4.2 → 3 mutation sites, (2) no mutations beyond birth → 1 site, (3) mutation sites include deliverable ID, (4) ambiguous mutations flagged rather than silently dropped. |
| D2.4a | Implement verification deliverable emitter: generate invariant-check deliverables for each mutation site | Emits `kind=invariant_check` deliverables. Each includes: variable name, invariant predicate, specific mutation being verified, edge cases (zero, negative, empty, boundary). IDs follow `D{milestone}.{seq}.inv`. Inserted into correct milestone by mutation site location. |
| D2.4b | Verify verification deliverable emitter | Tests: (1) 3 mutation sites → 3 invariant-check deliverables, (2) each references correct predicate, (3) edge cases include at minimum: zero, empty, boundary, (4) deliverables inserted into correct milestone. Each generated verify deliverable must contain at least one state assertion (Release Gate Rule 3). |
| D2.5a | Implement invariant registry pipeline integration (post-decomposition) | Registry pass runs after decomposition (M1). Reads Implement deliverables, detects state variables, generates invariant entries, emits verification deliverables, appends invariant registry section to roadmap output. |
| D2.5b | Verify registry integration | Integration test: spec with state variable introductions → invariant registry section present, invariant-check deliverables in correct milestones, entries cross-reference generated deliverables by ID. |
| D2.6a | Implement FMEA input domain enumerator: for each computational deliverable, enumerate input domains including degenerate cases | Triggered by computational verbs. Generates domain list: normal, empty, null/None, zero, negative, duplicate, out-of-order, single-element, maximum-size. Limit: 8 domains per computation. Degenerate cases prioritized. |
| D2.6b | Verify FMEA input domain enumerator | Tests: (1) "filter events by type" → at minimum: normal, empty, filter-removes-all, filter-removes-none, single-element, (2) "count active sessions" → normal, zero, single, large-count, (3) non-computational → empty list, (4) multiple computations → separate domain lists. |
| D2.7a | Implement FMEA failure mode classifier with dual detection signal | **Signal 1**: Cross-reference against invariant predicates — failure modes that violate an invariant without raising an error = silent corruption. **Signal 2**: Independent "no error path" detection — computation paths that return a value without raising any exception, even with degenerate inputs = potential silent corruption. Silent corruption = highest severity regardless of downstream impact. Classifier outputs: detection difficulty (immediate/delayed/silent) + severity (data loss, wrong state, degraded, cosmetic). |
| D2.7b | Verify FMEA failure mode classifier | Tests: (1) "offset advances by wrong amount, no error raised" → silent corruption + highest severity, (2) "TypeError on null input" → immediate + medium, (3) "filter returns empty instead of raising on invalid predicate" → delayed + high, (4) Signal 2 independently detects silent corruption even when no invariant predicate registered for the variable. |
| D2.8a | Implement FMEA deliverable promotion: failure modes above severity threshold → promoted test deliverables | Generates `kind=fmea_test` deliverables for failure modes at/above "wrong state" severity. Below-threshold modes → accepted risk in metadata with documented rationale. High-severity findings trigger Release Gate Rule 1 (block downstream progression). |
| D2.8b | Verify FMEA deliverable promotion | Tests: (1) silent corruption → promoted fmea_test deliverable + release gate triggered, (2) cosmetic → accepted risk in metadata, (3) promoted deliverable includes detection mechanism, (4) threshold configurable, (5) zero above-threshold failure modes → no promotion and no accepted-risk entries. |
| D2.9a | Integrate invariant registry + FMEA as combined pipeline pass | Runs after decomposition pass. Both passes share deliverable scanning infrastructure. Cross-link: D2.9 connects invariant registry rows to corresponding fmea_test deliverables where applicable. Combined pass is idempotent. |
| D2.9b | Verify combined pipeline integration | Integration test: spec with state variable introductions and computational deliverables → invariant registry + FMEA failure mode tables both present; cross-links correct; silent corruption findings trigger release gate. |

### Dependencies

M1 (extended deliverable schema, Implement/Verify pair structure, behavioral detection heuristic).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-004: State variable detector relies on non-standard description phrasing | Medium | Medium | Extensible synonym dictionary. Low-confidence detections flagged for human review rather than silently dropped. |
| R-005: Excessive invariant-check deliverables for high-mutation variables | Medium | Low | Cap at 5 per variable. Group related mutations. Configurable via `--max-invariant-checks`. |
| R-006: Invariant predicates stated in ambiguous free-form | Medium | High | Constrained grammar required: `variable_name comparison_op expression [AND\|OR ...]`. Free-form predicates rejected with validation error during registry generation. |
| R-007: FMEA input domain enumeration combinatorially explosive | Medium | Medium | Limit to 8 domains per computation. Prioritize degenerate cases (empty, zero, boundary). Configurable via `--max-fmea-domains`. |
| R-008: FMEA output generated but not acted on | Medium | High | Severity policy: silent corruption = highest + Release Gate Rule 1 blocks downstream progression until resolved or explicitly accepted. |

---

## M3: Guard and Sentinel Analysis

### Objective

Implement Proposal 3 (Guard and Sentinel Analysis). For each deliverable introducing conditional logic (guards, sentinels, flags, early returns), enumerate all states of the guard variable, detect ambiguous states where one value maps to multiple semantic meanings, perform transition analysis for type changes, and require disambiguation or documented accepted risk.

M3 depends on both M1 and M2: FMEA output from M2 is required to determine whether guard ambiguity constitutes silent corruption, which determines whether Release Gate Rule 2 is triggered.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1a | Implement guard and sentinel analyzer: enumerate guard variable states, detect ambiguity | Detects guards (if/else, early return, sentinel values, flag checks) and type changes (bool→int, enum→string). For each guard, enumerates all possible values and semantic meanings. Flags ambiguity when one value maps to multiple meanings (e.g., `0` means both "no events" and "start offset"). Type change from bool→int always triggers transition analysis. |
| D3.1b | Verify guard and sentinel analyzer | Tests: (1) "Replace boolean replay guard with integer offset" → ambiguity for value `0`, (2) boolean with clear semantics → no flag, (3) enum with exhaustive match → no flag, (4) integer without documented zero/negative semantics → flagged, (5) bool→int always triggers transition analysis. |
| D3.2a | Implement guard resolution requirement: ambiguous guards → disambiguation deliverables with release gate | Generates `kind=guard_test` deliverables for ambiguous guards requiring: explicit documentation of every guard value's semantic meaning, test that each semantic state maps to exactly one value, and for type transitions, test that all pre-transition semantic states have post-transition equivalents. **Unresolved ambiguity activates Release Gate Rule 2**: release gate warning with mandatory owner field and review date. Ambiguity can be accepted as risk only with documented rationale and owner. |
| D3.2b | Verify guard resolution requirement | Tests: (1) ambiguous integer guard → ≥2 guard_test deliverables (documentation + uniqueness test) + release gate warning with mandatory owner, (2) unambiguous boolean → zero guard deliverables, (3) bool→3-state enum → transition mapping deliverable, (4) accepted-risk rationale is non-empty string with owner name. |
| D3.3a | Integrate guard analysis as post-generation pass, after combined invariant registry + FMEA pass (M2) | Guard analysis runs after M2 combined pass. Cross-references invariant predicates (to verify guard variables have registered invariants) and FMEA severity (to determine if guard ambiguity elevation to silent corruption is warranted). Output: guard analysis section in roadmap with state enumeration tables, ambiguity flags, and gate warnings. |
| D3.3b | Verify guard analysis integration | Integration test: roadmap with type-migration deliverable (bool→int) → guard analysis section present, ambiguity for `0` detected, release gate warning generated with mandatory owner field, guard_test deliverables in correct milestone. Second test: boolean guard with clear semantics → no ambiguity flags, no release gate. |

### Dependencies

M1 (deliverable schema, Implement/Verify structure), M2 (invariant predicates for guard cross-reference; FMEA severity output for silent corruption determination).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-009: Guard ambiguity false positives for intentionally overloaded values | Low | Medium | `@no-ambiguity-check` annotation in deliverable descriptions suppresses detection. Requires documented rationale. |
| R-010: Narrow heuristics miss hidden guard semantics | Medium | Medium | Seed detection with known bug archetypes (empty, filtered, tail, cursor conditions). Extensible pattern library. |
| R-011: Team ignores release gate warning | Medium | High | Release Gate Rule 2: unresolved ambiguity with no owner is a blocking condition, not an advisory. Pipeline must fail to advance without owner assignment. |

---

## M4: Cross-Deliverable Data Flow Tracing

### Objective

Implement Proposal 5 (Cross-Deliverable Data Flow Tracing). Construct a data flow graph following each mutable state variable through all deliverables that read or write it. Extract implicit cross-milestone contracts, promote them to explicit acceptance criteria, and detect conflicts where writer semantics diverge from reader assumptions.

**Activation**: Conditional on roadmaps with 6+ milestones (configurable via `--dataflow-threshold N`; override with `--force-dataflow`). For smaller roadmaps, the pass emits a summary noting that tracing was skipped and directs reviewers to the invariant registry (M2) for per-variable tracking.

**Pilot requirement (D4.6)**: Before general enablement, execute a pilot on one high-complexity roadmap and record the overhead vs defects prevented. The go/no-go decision is documented with evidence.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1a | Implement data flow graph builder | Directed graph: nodes are `(deliverable_id, variable_name, operation)` where operation ∈ {birth, write, read}. Edges connect writes to subsequent reads. Cross-milestone edges annotated with milestone boundary. Cycle detection. Dead writes generate warnings. |
| D4.1b | Verify data flow graph builder | Tests: (1) M1.D1→M2.D3→M3.D1 chain → 3-node, 2 cross-milestone edges, (2) same-deliverable birth+read → 2-node, no cross-milestone, (3) read before birth → error, (4) dead write → warning, (5) empty deliverable list → empty graph. |
| D4.2a | Implement implicit contract extractor: for each cross-milestone edge, extract writer semantics and reader assumptions | Writer semantics parsed from: "set X to mean Y", "X represents Z after this operation". Reader assumptions parsed from: "assumes X is", "when X equals", "based on X". Produces `ImplicitContract(variable, writer_deliverable, reader_deliverable, writer_semantics, reader_assumption)`. Below 60% confidence → `UNSPECIFIED`; mandatory human review. |
| D4.2b | Verify implicit contract extractor | Tests: (1) writer "set offset to events delivered" + reader "assumes offset equals events processed" → contract captured, (2) no explicit semantics → `writer_semantics=UNSPECIFIED` (flagged), (3) both UNSPECIFIED → highest-risk classification, (4) confidence scoring calibrated (not all 0.5 or 1.0). |
| D4.3a | Implement conflict detector: flag contracts where writer semantics diverge from reader assumptions | Detects: direct contradiction, scope mismatch (filtered subset vs full set), type mismatch, completeness mismatch (edge cases not considered by reader). Cross-references invariant predicates (M2) and failure mode tables (M2) to enrich conflict detection. Conflict report includes suggested resolution action. |
| D4.3b | Verify conflict detector | Tests: (1) "offset tracks filtered events" vs "offset tracks all events" → scope mismatch, (2) "flag is boolean" vs "flag is integer" → type mismatch, (3) identical semantics → no conflict, (4) unspecified writer semantics → always conflicts (cannot verify compatibility). |
| D4.4a | Implement cross-milestone verification deliverable emitter | Generates `kind=contract_test` deliverables for conflicts and high-risk implicit contracts. Inserted into reader's milestone (consumer bears verification burden). Below 6-milestone threshold → summary only (no deliverables generated). |
| D4.4b | Verify cross-milestone verification deliverable emitter | Tests: (1) scope mismatch → contract_test in reader's milestone, (2) no-conflict edge + registered invariant → invariant boundary check, (3) no cross-milestone edges → no contract_test, (4) below threshold → summary only with M2 reference. |
| D4.5a | Integrate data flow tracing as final post-generation pass | Runs last in pipeline. Reads all deliverables (including M1/M2/M3 generated deliverables). Appends data flow trace section: graph summary, implicit contracts table, conflict report, generated deliverable list. Skip summary for roadmaps under threshold. |
| D4.5b | Verify data flow tracing integration | Integration test (6+ milestones): trace section present, contracts listed, conflicts flagged, contract_test deliverables in correct milestones. Integration test (3 milestones): skip summary with M2 reference. |
| D4.6a | Pilot execution: run data flow tracing on one high-complexity roadmap (6+ milestones) | Pilot executed on a real roadmap. Outputs: runtime overhead measured, defects detected vs would-have-been-missed count, false positive rate measured. |
| D4.6b | Pilot go/no-go decision: record evidence-based decision before general enablement | Go/no-go decision documented with: overhead measurement, defect detection rate, false positive count, recommendation (enable/refine/disable). General enablement blocked until this deliverable is accepted. |

### Dependencies

M1 (deliverable schema), M2 (invariant registry, invariant predicates, FMEA failure mode tables), M3 (guard analysis for type transition detection in conflict analysis).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-012: Data flow graph O(V×E) slow for large roadmaps | Medium | Medium | Adjacency list representation. Warning at 100+ deliverables. `--skip-dataflow` flag. Cache intermediate results. |
| R-013: Implicit contract extraction from natural language is unreliable | High | High | Confidence scoring. Below 60% → `UNSPECIFIED`. Mandatory human review for all UNSPECIFIED contracts. This is a fundamental limitation of text-based analysis. |
| R-014: False positive conflicts from synonym variation | Medium | Medium | Extensible synonym dictionary (e.g., "total" == "count", "events delivered" == "events returned"). Per-project customizable. |
| R-015 (shared with Risk Register): Premature general enablement before pilot | Medium | High | D4.6b pilot go/no-go deliverable is a hard gate — general enablement blocked until accepted. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Severity | Mitigation | Owner |
|----|------|---------------------|-------------|--------|----------|------------|-------|
| R-001 | Behavioral detection false positives on doc deliverables | M1 | Low | Low | Low | Negative signal suppression (doc-specific verbs) | architect |
| R-002 | ID suffix scheme collision with existing conventions | M1 | Low | Medium | Low | Validate against corpus; fallback `/impl`, `/verify` | architect |
| R-003 | Decomposition increases deliverable count, readability impact | M1 | Medium | Low | Low | Visual distinction; collapse option for summary views | architect |
| R-004 | State variable detector non-standard phrasing | M2 | Medium | Medium | Medium | Extensible synonym dictionary; flag low-confidence | architect |
| R-005 | Excessive invariant-check deliverables per variable | M2 | Medium | Low | Low | Cap at 5; group related mutations; configurable | architect |
| R-006 | Ambiguous free-form invariant predicates | M2 | Medium | High | High | Constrained grammar; validation rejects free-form | architect |
| R-007 | FMEA combinatorial domain explosion | M2 | Medium | Medium | Medium | Limit 8 domains; prioritize degenerate cases; configurable | architect |
| R-008 | FMEA output not acted on | M2 | Medium | High | High | Release Gate Rule 1 blocks downstream progression on silent corruption | architect |
| R-009 | Guard ambiguity false positives (intentionally overloaded) | M3 | Low | Medium | Low | `@no-ambiguity-check` annotation with rationale | architect |
| R-010 | Narrow heuristics miss hidden guard semantics | M3 | Medium | Medium | Medium | Seed with known archetypes; extensible pattern library | architect |
| R-011 | Team ignores release gate warning | M3 | Medium | High | High | Release Gate Rule 2: blocking condition, not advisory | architect |
| R-012 | Data flow graph performance on large roadmaps | M4 | Medium | Medium | Medium | Adjacency list; 100-deliverable warning; `--skip-dataflow`; caching | architect |
| R-013 | Implicit contract extraction unreliable | M4 | High | High | Critical | Confidence scoring; UNSPECIFIED below 60%; mandatory human review | architect |
| R-014 | False positive conflicts from synonym variation | M4 | Medium | Medium | Medium | Extensible synonym dictionary; per-project customization | architect |
| R-015 | Verify deliverables become checklist theater | M1-M4 | Medium | High | High | Release Gate Rule 3: each `.b` deliverable must contain at least one state assertion or boundary case | architect |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect | scribe (45%), qa (39%) | Generalist appropriate for meta-methodology work spanning documentation, quality engineering, and systems analysis; highest domain coverage bonus |
| Template | inline (Tier 4) | No templates found in Tier 1/2 | No template files found at `.dev/templates/roadmap/` or `~/.claude/templates/roadmap/`; no template scored ≥0.60 |
| Milestone Count | 4 | 3-4 (LOW complexity range) | Complexity 0.378 → LOW → base 3 + floor(3 domains / 2) = 4 |
| Adversarial Mode | multi-roadmap | none | `--multi-roadmap --agents opus:architect,haiku:architect` flags active |
| Adversarial Base Variant | opus:architect | haiku:architect (score 0.866) | Combined score 0.945 vs 0.866; margin 9%; V1 wins tiebreaker on debate performance (11/18 diff points) |
| M2 grouping: P1+P2 together | P1+P2 in M2 | P1 in M2, P2+P3 in M3 (V1 original) | Converged in adversarial Round 3: both advocates agreed P1+P2 share trigger detection infrastructure; V1 withdrew original position |
| M3 = Guard Analysis alone | Yes | M3 = P2+P3 (V1 original) | Guard analysis (P3) requires FMEA output from P2 for severity classification; P3 must come after P2; grouping P2+P3 in M3 would delay P2 unnecessarily |
| Dual FMEA detection signal | Yes (V1 architecture) | Invariant-only detection (V2) | V2 conceded in Round 2; dual signal prevents circular dependency on M2 completeness; Signal 2 independent of registry |
| Release gating with mandatory owner | Yes (from V2) | No enforcement (V1 original) | V1 conceded in Round 1; detection without enforcement is insufficient; U-003 voted 95% in favor |
| Constrained invariant grammar | Yes (from V1) | Free-form NLP predicates | V2 conceded in Round 2; constrained grammar enables automated validation; covers all source bug invariant patterns |
| M4 pilot-first | Yes (from V2) | Direct implementation | V1 conceded in Round 2; pilot-first is risk-appropriate for highest-cost proposal; D4.6 pilot deliverable is hard gate |
| Post-generation passes | Yes | Inline generator modification | Preserves backward compatibility; passes composable, reorderable, disableable independently; integration contract is existing schema |
| P5 conditional on 6+ milestones | Yes (both) | Always-on | Natural language contract extraction has fundamental reliability limits; noise on small roadmaps; configurable threshold |

---

## Pipeline Execution Order

```
Existing Generator Output (deliverable list)
    │
    ▼
[M1] Decomposition Pass
     • Extends deliverable schema (kind + metadata fields)
     • Splits behavioral deliverables into D.x.a (Implement) + D.x.b (Verify) pairs
     │
     ▼
[M2] Invariant Registry + FMEA Pass (shared detection infrastructure)
     • State variable detector → invariant registry entries → invariant_check deliverables
     • FMEA computational verb detector → failure mode tables → fmea_test deliverables
     • Cross-link: invariant rows ↔ fmea_test deliverables
     • Release Gate Rule 1: silent corruption findings block downstream progression
     │
     ▼
[M3] Guard Analysis Pass
     • Guard/sentinel detector → state enumeration → ambiguity detection
     • Cross-reference: invariant predicates (M2) + FMEA severity (M2)
     • Disambiguation deliverables (guard_test) for ambiguous guards
     • Release Gate Rule 2: unresolved ambiguity → mandatory owner assignment
     │
     ▼
[M4] Data Flow Tracing Pass  [conditional: roadmap has 6+ milestones]
     • Data flow graph builder → cross-milestone edges
     • Implicit contract extractor → writer/reader semantics
     • Conflict detector → scope/type/completeness mismatches
     • Verification deliverable emitter → contract_test deliverables in reader milestones
     │
     ▼
Output Formatting
```

All passes are idempotent (running twice = identical result). Each pass reads the full deliverable list including deliverables generated by prior passes.

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Bug 1 class (wrong operand in state mutation: `_loaded_start_index -= mounted` using widget count vs events consumed) caught during planning by invariant registry entry requiring "offset advances by exactly events consumed" + decomposed verify deliverable testing the distinction | M1, M2 | Yes — example fully traced in spec (L27-L29) |
| SC-002 | Bug 2 class (zero/empty sentinel ambiguity after bool→int type change: `_replayed_event_offset = len(plan.tail_events)` = 0 on empty tail) caught during planning by guard analysis detecting `0` is ambiguous + FMEA enumerating empty-tail as degenerate input | M2, M3 | Yes — example fully traced in spec (L31-L33) |
| SC-003 | All 5 proposals produce artifacts usable as both implementation guidance and review checklists (invariant tables, failure mode tables, guard analysis tables, verify sub-deliverables, data flow traces) | M1, M2, M3, M4 | Yes — stated requirement in spec (L202-L203) |
| SC-004 | Incremental adoption supported: Phase 1 (M1 only), Phase 2 (M1+M2+M3), Phase 3 (M1+M2+M3+M4) without requiring redesign between phases | M1, M2, M3, M4 | Yes — post-generation pass architecture; each pass independently disableable |
| SC-005 | Silent corruption failures surfaced by FMEA at planning time, classified as highest severity, and block downstream milestone progression via Release Gate Rule 1 until mitigated or explicitly accepted with owner | M2, M3 | Yes — severity classification and release gate are required output fields |
