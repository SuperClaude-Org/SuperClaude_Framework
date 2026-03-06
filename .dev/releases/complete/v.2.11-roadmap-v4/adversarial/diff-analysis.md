# Diff Analysis: Roadmap Variant Comparison

## Metadata
- Generated: 2026-03-04
- Variants compared: 2
- Variant 1: variant-1-opus-architect.md (opus:architect — dependency ordering, structural correctness)
- Variant 2: variant-2-haiku-architect.md (haiku:architect — pragmatic, risk-first, phased delivery)
- Total differences found: 18
- Categories: structural (4), content (8), contradictions (2), unique contributions (4)

---

## Structural Differences

| # | Area | Variant 1 (opus:architect) | Variant 2 (haiku:architect) | Severity |
|---|------|---------------------------|----------------------------|----------|
| S-001 | Deliverable granularity | Each behavioral deliverable split into D.x.a + D.x.b pairs (implement + verify), yielding 8/10/12/10 deliverables per milestone | Each milestone has 3-4 coarser deliverables without .a/.b internal sub-splitting | Medium — V1 is self-consistent (applies its own Proposal 4), V2 describes Proposal 4 but doesn't apply it to its own deliverables |
| S-002 | M2 milestone composition | Proposals 1 (Invariant Registry) alone in M2, Proposals 2+3 (FMEA + Guard) in M3 | Proposals 1+2 (Invariant Registry + FMEA) in M2, Proposal 3 (Guard) in M3 | Medium — grouping difference changes M2/M3 dependency structure |
| S-003 | Pipeline execution section | Explicit "Pipeline Execution Order" section with ASCII diagram showing M1→M2→M3→M4 pass ordering | Pipeline ordering is implicit in dependency graph; no dedicated section | Low — cosmetic difference, V1 adds useful clarity |
| S-004 | Deliverable ID scheme | Implements .a/.b suffix scheme across all milestones (D1.1a, D1.1b, etc.) | Flat IDs without .a/.b suffixing (D1.1, D1.2, D2.1, etc.) | Low — V2's deliverables describe the .a/.b scheme as an output but don't use it internally |

---

## Content Differences

| # | Topic | Variant 1 Approach | Variant 2 Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Grouping rationale for P2+P3 | "Share trigger patterns, operate at same abstraction level, produce same output type. Guard analysis benefits from FMEA severity classification for silent corruption." | V2 groups P1+P2 together, rationale: "Invariant registry defines expected state truth, FMEA models failure propagation — complementary pair." P3 grouped separately after with FMEA context. | High — fundamentally different grouping decisions with competing rationales. V1: P2+P3 together because same output type. V2: P1+P2 together because complementary analysis inputs. |
| C-002 | Invariant predicate grammar | Explicit constrained grammar requirement: `variable_name comparison_op expression [AND/OR ...]`; free-form rejected with validation error | Not specified — invariant predicates described as "predicate form" without grammar constraint | Medium — V1 adds testability guarantee; V2 leaves implementer discretion |
| C-003 | FMEA silent corruption dual signal | Dual detection: (1) invariant predicate cross-reference + (2) independent "no error path" detection. V1 explicitly guards against M2 completeness dependency | Single detection path: invariant cross-reference. No independent fallback mentioned. | High — V1's dual signal is architecturally important: if M2 misses a variable, M3 can still detect silent corruption independently |
| C-004 | Data flow threshold configurability | Configurable via `--dataflow-threshold N`; override with `--force-dataflow`; default 6 per spec | Gating at 6+ milestones; "explicit override available" mentioned but no specific flag named | Low — V1 more specific, V2 sufficient |
| C-005 | Verification deliverable boilerplate risk | Addressed via acceptance criteria requiring "description references corresponding Implement deliverable by ID" | Explicitly called out as R-001 "Verify deliverables become checklist theater" with mitigation: "require at least one state assertion or boundary case" | Medium — V2 surfaces this risk more prominently; V1 addresses via structural constraint; both approaches valid but different emphasis |
| C-006 | Release gating / blocking behavior | Not mentioned as explicit blocking behavior; silent corruption classified as highest severity but no gate described | "Release gating philosophy": high-severity silent-corruption risks block downstream roadmap expansion until mitigated or accepted with ownership. Unresolved guard ambiguity = release gate warning with mandatory owner. | High — V2 adds an operational enforcement mechanism that V1 lacks entirely. Critical for ensuring the methodology is actually used. |
| C-007 | Pilot execution for M4 | No pilot mentioned; M4 implemented and integrated with configurable threshold | D4.4 explicit: "Pilot execution + go/no-go decision: pilot on one high-complexity roadmap; decision recorded with measured overhead vs defects prevented" | Medium — V2's pilot-first approach for the highest-cost proposal is more risk-prudent |
| C-008 | State variable detector false-positive handling | "Flag low-confidence detections for human review" | "Conservative trigger set + explicit allow/ignore list" — implementer-facing controls | Low — different mitigation strategies, both reasonable |

---

## Contradictions

| # | Point of Conflict | Variant 1 Position | Variant 2 Position | Impact |
|---|-------------------|--------------------|-------------------|--------|
| X-001 | Milestone grouping of P1/P2/P3 | P2 (FMEA) and P3 (Guard) grouped in M3 together. P1 (Invariant Registry) alone in M2. Rationale: shared output type and trigger pattern between P2+P3. | P1 (Invariant Registry) and P2 (FMEA) grouped in M2 together. P3 (Guard) alone in M3. Rationale: P1+P2 are complementary analysis inputs to each other; P3 needs P1+P2 context. | High — implementation teams cannot do both; one grouping must be chosen. Both have valid rationale. This is the primary decision point for the merged roadmap. |
| X-002 | FMEA dependency on M2 invariants | FMEA has a dual detection signal — independent of M2 completeness by design. "Invariant cross-reference is enhancement only." | FMEA cross-links to invariant registry rows (D2.4); implies FMEA quality depends on M2 quality. No independent fallback mentioned. | Medium — V1's explicit dual signal is safer and reduces circular dependency risk; V2's approach requires M2 to be comprehensive. |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | Variant 1 (opus) | Constrained invariant predicate grammar (`variable_name comparison_op expression [AND/OR ...]`) with validation that rejects free-form predicates | High — makes invariants machine-verifiable; directly addresses R-006; prevents the "ambiguous predicate" failure mode that would undermine the registry's value |
| U-002 | Variant 1 (opus) | Explicit Pipeline Execution Order section with ASCII diagram showing M1→M2→M3→M4 post-generation pass ordering and idempotency guarantee | Medium — valuable for implementers; clarifies integration model |
| U-003 | Variant 2 (haiku) | Release gating philosophy: high-severity silent-corruption risks block downstream roadmap expansion; unresolved guard ambiguity = release gate warning with mandatory owner | High — the methodology only works if it's enforced. V1 describes detection but not enforcement. V2's gating mechanism is the operational backbone that makes the rest actionable. |
| U-004 | Variant 2 (haiku) | M4 pilot-first approach (D4.4): explicit go/no-go decision based on measured overhead vs defects prevented before general enablement | Medium — reduces risk of over-engineering for Proposal 5; provides evidence-based adoption decision |

---

## Summary

- Total structural differences: 4
- Total content differences: 8
- Total contradictions: 2
- Total unique contributions: 4
- Highest-severity items: X-001 (milestone grouping contradiction), C-001 (same topic), C-003 (dual signal architecture), C-006 (release gating — unique to V2), U-001 (constrained grammar — unique to V1), U-003 (release gating — unique to V2)

**Primary decision required**: Milestone grouping (X-001) — P2+P3 together (V1) vs P1+P2 together (V2). This drives M2/M3 structure and all downstream dependency relationships.

**Both variants agree on**: 4-milestone structure, M1 as foundation (Proposal 4 first), M4 conditional on complexity, post-generation pass architecture, implementation priority ordering.
