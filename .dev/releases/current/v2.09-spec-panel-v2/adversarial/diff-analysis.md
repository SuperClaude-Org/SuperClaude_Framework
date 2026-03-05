# Diff Analysis: Roadmap Comparison
## Metadata
- Generated: 2026-03-04T00:00:00Z
- Variants compared: 2
- Agent specs: variant-1 (opus:scribe), variant-2 (haiku:scribe)
- Total differences found: 14
- Categories: structural (4), content (5), contradictions (1), unique contributions (4)

---

## Structural Differences

| # | Area | Variant 1 (opus:scribe) | Variant 2 (haiku:scribe) | Severity |
|---|------|------------------------|--------------------------|----------|
| S-001 | Milestone count and split | 6 milestones: M1 (Persona Definition), M2 (Panel Integration), M3 (Boundary Table), M4 (Correctness Focus), M5 (Pipeline Analysis), M6 (Validation) | 6 milestones: M1 (SP-2), M2 (SP-3 foundations), M3 (Gate A validation), M4 (SP-1), M5 (SP-4 + integrations), M6 (Gate B validation) | Medium |
| S-002 | Validation milestone placement | M6 only — final validation after all work milestones | M3 (Gate A after Phase 1-2) AND M6 (Gate B after Phase 3) — interleaved validation per 1:2 ratio | High |
| S-003 | Phase 1 milestone granularity | 2 milestones for Phase 1 (M1: Persona Definition, M2: Panel Integration) — split workflow | 1 milestone for Phase 1 (M1: entire SP-2) — consolidated | Medium |
| S-004 | Section organization style | Narrative prose sections (Phase 1/2/3 overviews + per-milestone detail) — 14 main sections | Table-first, lean-prose structure — 8 main sections with tables as primary | Low |

---

## Content Differences

| # | Topic | Variant 1 (opus:scribe) Approach | Variant 2 (haiku:scribe) Approach | Severity |
|---|-------|----------------------------------|-----------------------------------|----------|
| C-001 | Validation gate strategy | Single final validation at M6; Phase milestones include "run v0.04 validation" as per-milestone AC | Explicit Gate A (M3) and Gate B (M6) as dedicated validation milestones; interleaved 1:2 ratio per MEDIUM complexity | High |
| C-002 | SP-4 dependency on SP-1 | M5 (pipeline) depends on M1, M2, M3 (not M4) — SP-4 is independent of correctness focus mode | M5 depends on M4 — SP-4 treated as sequential with --focus correctness | Medium |
| C-003 | Phase 1 work structure | Separates persona definition (M1) from panel integration (M2) — cleaner separation of concerns | Combines into single M1 milestone — simpler tracking but less granular progress | Low |
| C-004 | Integration map coverage | Explicit Integration Map section with ASCII diagram; confirms no downstream command changes needed | Integration mappings listed inline in M5 work items; no dedicated section | Low |
| C-005 | Milestone effort framing | Effort expressed as day ranges with overhead percentages per phase in Appendix table | Effort as day ranges in milestone plan table; overhead only stated in ACs | Low |

---

## Contradictions

| # | Point of Conflict | Variant 1 Position | Variant 2 Position | Impact |
|---|-------------------|--------------------|-------------------|--------|
| X-001 | SP-4 dependency on SP-1 | M5 (Pipeline Analysis) has dependencies M1, M2, M3 — does NOT depend on M4 (Correctness Focus). M4 and M5 share same prerequisites and can run in parallel in Phase 3. | M5 depends on M4 — "Pipeline dimensional analysis is part of Phase 3 depth package" making it sequential after correctness focus | High — affects execution parallelism and critical path length. Spec itself is ambiguous: Phase 3 items share dependencies on Phase 1+2 but the spec does not mandate M5 depends on M4 |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|--------------|-----------------|
| U-001 | Variant 1 (opus:scribe) | Parallel M4+M5 execution opportunity explicitly called out in dependency graph and prose: "M4 and M5 share the same prerequisites and have no dependency on each other. They can execute in parallel within Phase 3." Reduces critical path. | High — significant timeline optimization; 2-3 days saved if parallelism exploited |
| U-002 | Variant 1 (opus:scribe) | Integration Map section with ASCII diagram and explicit statement "no downstream changes required in this release — the integration contract is output format compatibility." | Medium — useful communication artifact for downstream team awareness |
| U-003 | Variant 1 (opus:scribe) | SP-5 revisit trigger condition made explicit: "After SP-2 has been active for at least 10 reviews and the false positive rate is measured below threshold." | Medium — provides actionable re-evaluation criteria rather than vague "revisit later" |
| U-004 | Variant 2 (haiku:scribe) | Dedicated validation milestones (Gate A, Gate B) with explicit evidence pack requirements: "v0.04 run logs, overhead report, artifact completeness report" and "end-to-end metrics dashboard, risk review, integration verification." Interleaved validation per 1:2 ratio. | High — interleaved validation gates are required by MEDIUM complexity interleave ratio; this variant correctly implements the protocol |

---

## Summary
- Total structural differences: 4
- Total content differences: 5
- Total contradictions: 1
- Total unique contributions: 4
- Highest-severity items: S-002 (validation interleaving), C-001 (validation gate strategy), X-001 (SP-4 dependency conflict)
- Similarity check: Variants are substantially different in structure and validation strategy — debate warranted
