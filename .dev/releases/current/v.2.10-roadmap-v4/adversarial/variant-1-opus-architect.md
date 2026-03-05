# Roadmap: sc:roadmap Edge Case and Invariant Violation Detection v1.0 [Architect Variant]

Document status: **Generated from brainstorm spec (203 lines)**
Generation date: **2026-03-04**
Persona: **architect** — dependency ordering, decomposition discipline, structural correctness
Source specification: Brainstorm: Improving sc:roadmap to Surface Edge Cases and Invariant Violations

---

## Overview

This roadmap implements five methodology enhancements to the `sc:roadmap` generation pipeline. The source bugs (index tracking stall in `load_older_events()`, replay guard bypass with empty tail after condensation) share a common root cause: the roadmap generator treated state-variable mutations as atomic deliverables without decomposing them into invariant assertions, edge-case enumeration, or cross-deliverable data flow verification. The five proposals address this gap at different abstraction levels.

The architectural ordering follows the implementation priority stated in the spec: Proposal 4 first (Implement/Verify pair decomposition — lowest cost, highest immediate impact), then Proposal 1 (State Variable Invariant Registry), Proposal 2 (FMEA Pass), Proposal 3 (Guard and Sentinel Analysis), and finally Proposal 5 (Cross-Deliverable Data Flow Tracing — highest cost, conditional on milestone count). Milestones M1 and M2 are the structural foundation; M3 and M4 layer analytical depth on top. No milestone may begin before its predecessors are accepted.

The key architectural constraint: every enhancement operates as a **post-generation pass** over the deliverable list produced by the existing roadmap generator. This means the existing generator's output schema is the integration contract. Changes to that schema belong in M1. Analytical passes in M2–M4 consume that schema and append structured metadata (invariant entries, failure mode tables, guard analyses, data flow traces) without mutating the core deliverables.

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Deliverable Decomposition and Schema Extension | FEATURE | P0 | S | None | 8 | Low |
| M2 | State Variable Invariant Registry | FEATURE | P0 | M | M1 | 10 | Medium |
| M3 | FMEA Pass and Guard Analysis | FEATURE | P1 | M | M1, M2 | 12 | Medium |
| M4 | Cross-Deliverable Data Flow Tracing | FEATURE | P2 | M | M1, M2, M3 | 10 | High |

---

## Dependency Graph

```
M1 (Decomposition + Schema)
│
├──► M2 (Invariant Registry)
│    │
│    ├──► M3 (FMEA + Guard Analysis)
│    │    │
│    │    └──► M4 (Cross-Deliverable Data Flow)
│    │
│    └──► M4 (reads invariant predicates for contract extraction)
│
└──► M3 (consumes Implement/Verify pairs for failure mode targeting)
```

Linearized: **M1 → M2 → M3 → M4**

---

## M1: Deliverable Decomposition and Schema Extension

### Objective

Implement Proposal 4 (Implement/Verify pair decomposition) and extend the deliverable schema to support metadata attachments from subsequent analytical passes. This milestone establishes the structural contract that all downstream milestones build against. No analytical logic is introduced here — only the decomposition rule and the schema surface.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1a | Define extended deliverable schema with `kind` field (`implement`, `verify`, `invariant_check`, `fmea_test`, `guard_test`, `contract_test`) and `metadata` attachment point | Schema definition exists. All six `kind` values enumerated. `metadata` defaults to empty dict. Round-trip serialization preserves `kind` and `metadata`. |
| D1.1b | Verify extended deliverable schema | Tests: (1) unknown `kind` raises ValueError, (2) `metadata` defaults to empty dict, (3) existing deliverables without `kind` default to `implement`, (4) schema is backward-compatible. |
| D1.2a | Implement decomposition rule: behavioral deliverables split into `D.x.a` (Implement) and `D.x.b` (Verify) pairs | Decomposition function expands behavioral deliverables into Implement/Verify pairs. Non-behavioral deliverables pass through unchanged. ID suffixes `.a` and `.b` appended correctly. |
| D1.2b | Verify decomposition rule | Tests: (1) 3 behavioral deliverables → 6 output, (2) mixed list (2 behavioral + 1 doc) → 5 output, (3) empty input → empty output, (4) already-decomposed not re-decomposed, (5) Verify description references Implement by ID. |
| D1.3a | Implement behavioral detection heuristic for deliverable descriptions | Heuristic detects computational verbs, state mutation patterns (`self._*`, counter/offset/cursor), and conditional logic patterns. Returns boolean `is_behavioral`. |
| D1.3b | Verify behavioral detection heuristic | Tests: (1) "Replace boolean with int offset" → behavioral, (2) "Document API endpoint" → not behavioral, (3) "Add type definition for GateResult" → not behavioral, (4) "Implement retry with bounded attempts" → behavioral, (5) "Update README" → not behavioral. |
| D1.4a | Integrate decomposition into roadmap generator pipeline as a post-generation pass | Pass runs after deliverable generation, before output formatting. Idempotent. Preserves deliverable ordering within each milestone. |
| D1.4b | Verify generator integration | Integration test: known spec → output contains Implement/Verify pairs for all behavioral deliverables; non-behavioral deliverables unchanged; milestone structure preserved. |

### Dependencies

None. This is the foundation milestone.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Behavioral detection false positives on documentation deliverables | Low | Low | Negative signal suppression (doc-specific verbs). Tunable threshold. |
| R-002: ID suffix scheme (`.a`, `.b`) collides with existing conventions | Low | Medium | Validate against corpus; fallback to `/impl` and `/verify` suffixes. |
| R-003: Decomposition increases deliverable count, readability impact | Medium | Low | Visual distinction in output; collapse option for summary views. |

---

## M2: State Variable Invariant Registry

### Objective

Implement Proposal 1 (State Variable Invariant Registry). For every deliverable introducing or modifying a state-tracking variable, generate a registry entry naming the variable, stating its invariant in predicate form, and inventorying all mutation sites. Each mutation site becomes a verification sub-deliverable asserting the invariant holds after the mutation.

This is the proposal that would have caught the `load_older_events()` index tracking bug: an invariant entry for the offset variable would have stated "offset must advance by exactly the number of events delivered" and enumerated the mutation site inside the filtering branch.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1a | Implement invariant registry data structure: `InvariantEntry(variable_name, scope, invariant_predicate, mutation_sites[], verification_deliverable_ids[])` | Data structure instantiates with all fields. `invariant_predicate` uses constrained grammar. `mutation_sites` is a list of `MutationSite(location, expression, context)`. |
| D2.1b | Verify invariant registry data structure | Tests: (1) empty `mutation_sites` valid, (2) `verification_deliverable_ids` can cross milestones, (3) serialization round-trip, (4) duplicate variable_name warns. |
| D2.2a | Implement state variable detector | Detects `self._*` assignments, "introduce variable", "add counter/offset/cursor/flag", "replace X with Y" where Y is state-tracking type. Returns `(variable_name, deliverable_id, introduction_type)` tuples. |
| D2.2b | Verify state variable detector | Tests: (1) "Replace boolean with int offset" → replacement, (2) "Add replay guard flag" → flag, (3) "Document offset" → not detected, (4) "Introduce cursor" → cursor, (5) multiple variables in one deliverable handled. |
| D2.3a | Implement mutation inventory generator | Parses descriptions for mutation indicators: "update X", "increment X", "reset X", "set X to", "advance X by". Cross-references all roadmap deliverables. |
| D2.3b | Verify mutation inventory generator | Tests: (1) variable in D2.3 mutated in D3.1 and D4.2 → 3 mutation sites, (2) no mutations beyond birth → 1 site, (3) mutation sites include deliverable ID, (4) ambiguous mutations flagged for review. |
| D2.4a | Implement verification deliverable emitter | Emits `kind=invariant_check` deliverables. Each includes variable name, invariant predicate, specific mutation, edge cases (zero, negative, empty, boundary). IDs follow `D{milestone}.{seq}.inv`. |
| D2.4b | Verify verification deliverable emitter | Tests: (1) 3 mutation sites → 3 invariant-check deliverables, (2) references correct predicate, (3) edge cases enumerated, (4) deliverables inserted into correct milestone. |
| D2.5a | Integrate invariant registry pass into generator pipeline, after decomposition pass | Reads Implement deliverables, detects state variables, generates invariant entries, emits verification deliverables, appends invariant registry section to output. |
| D2.5b | Verify registry integration | Integration test: spec with state variable introductions → invariant registry section present, invariant-check deliverables in correct milestones, registry entries cross-reference generated deliverables. |

### Dependencies

M1 (extended deliverable schema, Implement/Verify pair structure, behavioral detection heuristic).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-004: State variable detector relies on description text, non-standard phrasing | Medium | Medium | Extensible synonym dictionary. Flag low-confidence detections. |
| R-005: Excessive verification deliverables for high-mutation variables | Medium | Low | Cap at 5 per variable. Group related mutations. Configurable via `--max-invariant-checks`. |
| R-006: Natural language invariant predicates are ambiguous | Medium | High | Constrained grammar: `variable_name comparison_op expression`. Reject free-form during validation. |

---

## M3: FMEA Pass and Guard Analysis

### Objective

Implement Proposal 2 (Failure Mode and Effects Analysis) and Proposal 3 (Guard and Sentinel Analysis) as a combined analytical pass. Grouped because they share trigger patterns, operate at the same abstraction level, and produce the same output type.

The combined pass covers the failure surface the original roadmap missed: the replay guard bypass occurred because a boolean-to-integer type change introduced an ambiguous zero value.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1a | Implement FMEA input domain enumerator | Parses computational verbs (compute, extract, filter, count, calculate, determine, select). Generates input domain list: normal, empty, null, zero, negative, duplicate, out-of-order, single-element, maximum-size. |
| D3.1b | Verify FMEA input domain enumerator | Tests: (1) "filter events by type" → at minimum: normal, empty, filter-removes-all, filter-removes-none, single-element, (2) "count active sessions" → normal, zero, single, large-count, (3) non-computational → empty domain list. |
| D3.2a | Implement FMEA failure mode classifier with silent corruption detection | Classifies by detection difficulty (immediate/delayed/silent) and severity. Silent corruption = highest severity regardless of downstream impact. |
| D3.2b | Verify FMEA failure mode classifier | Tests: (1) "offset advances by wrong amount, no error" → silent corruption + highest severity, (2) "TypeError on null" → immediate + medium, (3) "filter returns empty instead of raising" → delayed + high. |
| D3.3a | Implement FMEA deliverable promotion | Generates `kind=fmea_test` deliverables for failure modes at/above "wrong state" severity. Below-threshold modes → accepted risk in metadata. |
| D3.3b | Verify FMEA deliverable promotion | Tests: (1) silent corruption → promoted test deliverable, (2) cosmetic → accepted risk, (3) promoted deliverable includes detection mechanism, (4) configurable threshold. |
| D3.4a | Implement guard and sentinel analyzer | Detects guards/sentinels/flags/early returns, type changes (bool→int, enum→string). Enumerates all possible values and semantic meanings. Flags ambiguity when one value maps to multiple meanings. |
| D3.4b | Verify guard and sentinel analyzer | Tests: (1) "Replace boolean replay guard with integer offset" → ambiguity for value `0`, (2) boolean with clear semantics → no flag, (3) enum with exhaustive match → no flag, (4) integer without documented zero/negative semantics → flagged, (5) bool→int always triggers transition analysis. |
| D3.5a | Implement guard resolution requirement | Generates `kind=guard_test` deliverables requiring: explicit documentation of guard value semantics, test that each semantic state maps to exactly one value, transition mapping for type changes. |
| D3.5b | Verify guard resolution requirement | Tests: (1) ambiguous integer guard → ≥2 deliverables (documentation + uniqueness test), (2) unambiguous boolean → zero guard deliverables, (3) bool→3-state enum → transition mapping deliverable. |
| D3.6a | Integrate FMEA + guard analysis as combined post-generation pass, after invariant registry | Runs after M2 registry pass. FMEA references invariant predicates for silent corruption severity. Guard analysis cross-references invariant registry. |
| D3.6b | Verify combined pass integration | Integration test: roadmap with computational deliverables and guard introductions → failure mode tables in metadata, promoted deliverables in correct milestones, guard analysis section, FMEA classifications reference invariant predicates. |

### Dependencies

M1 (deliverable schema, Implement/Verify decomposition), M2 (invariant predicates for silent corruption classification, invariant registry for guard cross-referencing).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-007: FMEA input domain enumeration combinatorially explosive | Medium | Medium | Limit to 8 domains per computation. Prioritize degenerate cases. Configurable via `--max-fmea-domains`. |
| R-008: Guard ambiguity false positives for intentionally overloaded values | Low | Medium | `@no-ambiguity-check` annotation with documented rationale. |
| R-009: FMEA + guard analysis increases generation time | Medium | Low | Optional pass; auto-enabled for specs >100 lines; `--fmea` flag. |
| R-010: Silent corruption classification depends on potentially incomplete invariants | Medium | High | Independent "no error path" detection as dual signal. Invariant cross-reference is enhancement only. |

---

## M4: Cross-Deliverable Data Flow Tracing

### Objective

Implement Proposal 5 (Cross-Deliverable Data Flow Tracing). Construct a data flow graph following each mutable state variable through all deliverables that read or write it. Extract implicit cross-milestone contracts, promote them to explicit acceptance criteria, and detect conflicts where writer semantics diverge from reader assumptions.

Conditional on roadmaps with 6+ milestones. For smaller roadmaps, emits summary noting tracing was skipped and directs to invariant registry (M2).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1a | Implement data flow graph builder | Directed graph: nodes are `(deliverable_id, variable_name, operation)` where operation ∈ {birth, write, read}. Cross-milestone edges annotated with milestone boundary. Cycle detection. |
| D4.1b | Verify data flow graph builder | Tests: (1) M1.D1→M2.D3→M3.D1 chain → 3-node graph, 2 cross-milestone edges, (2) same-deliverable birth+read → 2-node, no cross-milestone, (3) read before birth → error, (4) dead write → warning. |
| D4.2a | Implement implicit contract extractor | Parses write-site semantics ("set X to mean Y", "X represents Z"). Parses read-site assumptions ("assumes X is", "based on X"). Produces `ImplicitContract(variable, writer_deliverable, reader_deliverable, writer_semantics, reader_assumption)`. |
| D4.2b | Verify implicit contract extractor | Tests: (1) writer "set offset to number of events delivered" + reader "assumes offset equals total events processed" → contract captured, (2) no explicit semantics → `writer_semantics=UNSPECIFIED`, (3) both unspecified → highest-risk classification. |
| D4.3a | Implement conflict detector | Detects: direct contradiction, scope mismatch (filtered subset vs full set), type mismatch, completeness mismatch (edge cases not considered). Cross-references invariant predicates and failure mode tables. |
| D4.3b | Verify conflict detector | Tests: (1) "offset tracks filtered events" vs "offset tracks all events" → scope mismatch, (2) "flag is boolean" vs "flag is integer" → type mismatch, (3) identical semantics → no conflict, (4) unspecified writer semantics → always conflicts. |
| D4.4a | Implement cross-milestone verification deliverable emitter | Generates `kind=contract_test` deliverables for conflicts and high-risk implicit contracts. Inserted into reader's milestone. Below 6-milestone threshold → summary only. |
| D4.4b | Verify cross-milestone verification deliverable emitter | Tests: (1) scope mismatch → contract_test in reader's milestone, (2) no-conflict cross-milestone edge + registered invariant → invariant boundary check deliverable, (3) no cross-milestone edges → no contract_test, (4) below threshold → summary only. |
| D4.5a | Integrate data flow tracing as final post-generation pass | Runs last in pipeline. Reads all deliverables including those from M1/M2/M3 passes. Appends data flow trace section: graph summary, implicit contracts table, conflict report, generated deliverable list. |
| D4.5b | Verify data flow tracing integration | Integration test (6+ milestones): trace section present, contracts table lists cross-milestone variables, conflict report flags known divergences, contract_test deliverables in correct milestones. Integration test (3 milestones): skip summary with M2 reference. |

### Dependencies

M1 (deliverable schema), M2 (invariant registry, invariant predicates), M3 (failure mode tables, guard analysis for type transition detection).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-011: Data flow graph O(V*E) slow for large roadmaps | Medium | Medium | Adjacency list representation. Warning at 100+ deliverables. `--skip-dataflow` flag. Cache intermediates. |
| R-012: Implicit contract extraction from natural language is unreliable | High | High | Confidence scoring. Below 60% → `UNSPECIFIED`. Mandatory human review for unspecified contracts. |
| R-013: False positive conflicts from synonym variation | Medium | Medium | Extensible synonym dictionary (e.g., "total" == "count"). Per-project customizable. |
| R-014: 6-milestone threshold excludes beneficial analysis | Low | Low | Configurable via `--dataflow-threshold N`. Override with `--force-dataflow`. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Severity | Mitigation | Owner |
|----|------|---------------------|-------------|--------|----------|------------|-------|
| R-001 | Behavioral detection false positives on doc deliverables | M1 | Low | Low | Low | Negative signal suppression | architect |
| R-002 | ID suffix scheme collision | M1 | Low | Medium | Low | Validate against corpus; fallback to `/impl`, `/verify` | architect |
| R-003 | Decomposition increases deliverable count readability | M1 | Medium | Low | Low | Visual distinction; collapse option | architect |
| R-004 | State variable detector non-standard phrasing | M2 | Medium | Medium | Medium | Extensible synonym dictionary; flag low-confidence | architect |
| R-005 | Excessive verification deliverables | M2 | Medium | Low | Low | Cap at 5; group mutations; configurable | architect |
| R-006 | Ambiguous invariant predicates | M2 | Medium | High | High | Constrained grammar; reject free-form | architect |
| R-007 | FMEA combinatorial explosion | M3 | Medium | Medium | Medium | Limit 8 domains; prioritize degenerate; configurable | architect |
| R-008 | Guard ambiguity false positives | M3 | Low | Medium | Low | `@no-ambiguity-check` annotation | architect |
| R-009 | FMEA + guard increases generation time | M3 | Medium | Low | Low | Optional; auto-enable >100 lines; `--fmea` flag | architect |
| R-010 | Silent corruption depends on incomplete invariants | M3 | Medium | High | High | Dual detection signal; invariant cross-ref as enhancement | architect |
| R-011 | Data flow graph performance | M4 | Medium | Medium | Medium | Adjacency list; warning >100 deliverables; caching | architect |
| R-012 | Contract extraction unreliability | M4 | High | High | Critical | Confidence scoring; UNSPECIFIED below 60%; mandatory review | architect |
| R-013 | False positive conflicts from synonyms | M4 | Medium | Medium | Medium | Synonym dictionary; per-project customization | architect |
| R-014 | 6-milestone threshold miscalibrated | M4 | Low | Low | Low | Configurable threshold; `--force-dataflow` override | architect |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect | scribe (45%), qa (39%) | Generalist appropriate for meta-methodology work spanning documentation, quality engineering, and systems analysis |
| Template | inline | No templates scored ≥0.6 | No template files found in Tier 1/2 search; inline generation applied |
| Milestone Count | 4 | 3-4 (LOW complexity range) | Complexity 0.378 → LOW → base 3 + floor(3/2) = 4 |
| Adversarial Mode | multi-roadmap | none | `--multi-roadmap --agents opus:architect,haiku:architect` flags present |
| Proposal 4 first | Yes | Proposal 1 first | Decomposition establishes Implement/Verify pair structure consumed by invariant registry |
| Group P2+P3 in M3 | Yes | Separate milestones | Same abstraction level, shared triggers, shared output type; guard analysis benefits from FMEA severity classification |
| P5 conditional on 6+ milestones | Yes | Always-on | Natural language contract extraction has fundamental reliability limits; noise on small roadmaps where manual review is feasible |
| Post-generation passes | Yes | Inline generator modification | Preserves backward compatibility; passes composable, reorderable, and independently disableable |
| Constrained invariant grammar | Yes | Free-form NLP | Enables automated predicate validation; covers the invariant patterns from source bugs |
| Dual FMEA signals | Yes | Invariant-only detection | Guards against M2 completeness dependency; avoids circular dependency |

---

## Pipeline Execution Order

```
Existing Generator
    │
    ▼
[M1] Decomposition Pass (Implement/Verify pairs)
    │
    ▼
[M2] Invariant Registry Pass (state variable detection + verification deliverable emission)
    │
    ▼
[M3] FMEA + Guard Analysis Pass (failure modes + guard ambiguity + promoted deliverables)
    │
    ▼
[M4] Data Flow Tracing Pass (cross-deliverable contracts + conflict detection)  [conditional: 6+ milestones]
    │
    ▼
Output Formatting
```

Each pass reads the enriched deliverable list from prior passes, appends metadata and new deliverables, and passes the result downstream. All passes are idempotent.

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Bug 1 class (wrong operand in state mutation) caught during planning by invariant registry + implement/verify decomposition | M1, M2 | Yes — traced example in spec |
| SC-002 | Bug 2 class (zero/empty ambiguity in sentinel guard after bool→int migration) caught during planning by guard analysis + FMEA | M2, M3 | Yes — traced example in spec |
| SC-003 | All 5 proposals produce artifacts usable as implementation guidance and review checklists | M1, M2, M3, M4 | Yes — explicitly stated in spec |
| SC-004 | Incremental adoption supported: Phase 1 (M1), Phase 2 (M2+M3), Phase 3 (M4) without redesign | M1, M2, M3, M4 | Yes — phased ordering with rationale defined |
| SC-005 | Silent corruption failures surfaced by FMEA at planning time, classified as highest severity | M3 | Yes — severity classification is required output field |
