

---
base_variant: "Opus Architect (A)"
variant_scores: "A:81 B:76"
---

# Base Selection: v2.24.1 CLI Portify v5 Roadmap

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced 5 key divergence points which map to these evaluation criteria:

| # | Criterion | Weight | Source |
|---|-----------|--------|--------|
| C1 | Structural clarity & actionability | 20% | D-1 (phase granularity), D-4 (time estimation) |
| C2 | Compatibility safety | 25% | D-2 (Phase 0), D-6 (validation), core debate theme |
| C3 | Technical completeness | 20% | D-11 (consolidation fallback), resolution coverage |
| C4 | Implementation guidance | 20% | Dependency visualization, sizing, architectural recs |
| C5 | Cognitive efficiency for implementer | 15% | Phase count, context switching, flow preservation |

Weights reflect the debate's consensus that compatibility is the dominant risk (both variants agreed), while the remaining criteria capture the substantive disagreements.

## 2. Per-Criterion Scores

### C1: Structural Clarity & Actionability (20%)

| Aspect | Variant A (Opus) | Variant B (Haiku) |
|--------|-----------------|-------------------|
| Phase structure | 3 phases with nested milestones — compact, navigable | 8 phases — granular, auditable progress markers |
| Time estimation | Hour ranges (19-28h) + line counts (350-450 LOC) — directly actionable | Phase units (5.25) + session grouping — avoids anchoring but requires conversion |
| Dependency visualization | ASCII dependency graph with parallel markers | Textual ordering with implicit dependencies |
| Progress reporting | Requires decomposing Phase 2 for status updates | Each phase = one status update |

**Scores**: A: 84 | B: 74

**Rationale**: Opus's hour ranges with line-count grounding are more immediately useful than abstract phase units. The ASCII dependency graph (Opus) is a concrete artifact that Haiku lacks. However, Haiku's per-phase progress reporting is genuinely easier for stakeholders. Opus wins on balance because the primary consumer is a single implementer (both roadmaps assume this), where actionable sizing matters more than reporting granularity.

### C2: Compatibility Safety (25%)

| Aspect | Variant A (Opus) | Variant B (Haiku) |
|--------|-----------------|-------------------|
| Upfront guardrails | No Phase 0; constraints assumed internalized | Phase 0 with change map, compatibility checklist, test matrix |
| Continuous testing | Architectural Recommendation #4 (advisory) | Structural concern raised but not formalized as gate |
| Validation placement | Bundled in Phase 3 with artifacts and test suite | Dedicated Phase 6 for validation logic |
| Regression proof | Phase 3.3 with 12 success criteria | Phase 7 with explicit regression validation stream |
| Internal consistency | Rec #4 ("test at every milestone") contradicts single Phase 3 gate | Phase 0 deliverables address the gap Opus leaves |

**Scores**: A: 74 | B: 83

**Rationale**: Haiku is stronger here. The debate exposed a genuine inconsistency in Opus: Recommendation #4 advocates continuous testing, but the formal structure concentrates validation in Phase 3. Haiku's Phase 0 deliverables (change map, compatibility checklist) are low-cost, high-value artifacts for a compatibility-sensitive release. Haiku's validation streams (A/B/C/D) provide clearer coverage organization.

### C3: Technical Completeness (20%)

| Aspect | Variant A (Opus) | Variant B (Haiku) |
|--------|-----------------|-------------------|
| Consolidation strategy | `commonpath()` only; edge cases deferred to v2.25 | Two-tier: `commonpath()` + top-10-by-component-count fallback |
| Error/warning coverage | All codes defined in Phase 1, tested in Phase 1.2 | Codes defined in Phase 6 — later but with dedicated focus |
| Edge case handling | FR-018 (standalone, multi-skill) explicit in Phase 1.2 | Standalone/multi-skill in Phase 3, less prominent |
| Risk coverage | 6 risks | 7 risks (adds "CLI contract drift" — D-9) |
| Deferred items | 5 items, clearly bounded | Implicitly deferred but less explicitly catalogued |

**Scores**: A: 78 | B: 80

**Rationale**: Close. Haiku's two-tier consolidation fallback is the stronger position — the debate showed Opus's "defer to v2.25" argument was weak given the trivial implementation cost. Haiku also identifies CLI contract drift as a distinct risk. Opus counters with earlier error-code definition and more explicit edge-case placement. Haiku edges ahead on the consolidation point alone.

### C4: Implementation Guidance (20%)

| Aspect | Variant A (Opus) | Variant B (Haiku) |
|--------|-----------------|-------------------|
| Architectural recommendations | Dedicated section with 5 numbered recommendations | Inline "Architect focus" boxes per phase |
| Sizing guidance | Line counts (350-450 for resolution.py), test counts (~37) | No line counts, no test counts |
| Parallel execution marking | Explicit: "Can run in parallel with 2.2" on milestones 2.1/2.2 | Implicit: "Discovery/process in parallel" in dependency section |
| Success criteria mapping | Table with test method and phase for each SC | Functional acceptance list + validation streams |
| NFR verification | Specific commands (`grep -r`, `git diff --name-only`) | Descriptive ("grep/static proof") |

**Scores**: A: 88 | B: 72

**Rationale**: Opus is substantially stronger. Line counts, test counts, specific verification commands, and explicit parallel markers give the implementer concrete targets. Haiku's "Architect focus" boxes are useful framing but don't substitute for sizing data. Opus's success criteria table (SC-1 through SC-12 with test methods and phase assignments) is a ready-made implementation checklist.

### C5: Cognitive Efficiency for Implementer (15%)

| Aspect | Variant A (Opus) | Variant B (Haiku) |
|--------|-----------------|-------------------|
| Phase transitions | 3 major transitions — minimal context switching | 7 transitions (Phase 0→7) — frequent context switching |
| Scope per phase | Phase 2 bundles 8-12h — large but contextually coherent | Phases 3-5 at 0.5-1.0 units each — smaller but more frequent |
| Mental model | "Foundation → Integration → Validation" — simple narrative | Linear sequence of 8 concerns — harder to hold in working memory |
| Parallel awareness | Built into phase structure (milestones 2.1 || 2.2) | Requires reading dependency section separately |

**Scores**: A: 85 | B: 70

**Rationale**: For a single implementer (the assumed primary case), Opus's 3-phase model maps to natural work sessions. The "Foundation → Integration → Validation" narrative is easy to internalize. Haiku's 8 phases create transition overhead that isn't justified for this scope — the debate acknowledged this depends on consumption pattern, but for implementation (not stakeholder reporting), fewer phases wins.

## 3. Overall Scores

| Criterion | Weight | Variant A | Variant B | A Weighted | B Weighted |
|-----------|--------|-----------|-----------|------------|------------|
| C1: Structural clarity | 20% | 84 | 74 | 16.8 | 14.8 |
| C2: Compatibility safety | 25% | 74 | 83 | 18.5 | 20.75 |
| C3: Technical completeness | 20% | 78 | 80 | 15.6 | 16.0 |
| C4: Implementation guidance | 20% | 88 | 72 | 17.6 | 14.4 |
| C5: Cognitive efficiency | 15% | 85 | 70 | 12.75 | 10.5 |
| **Total** | **100%** | — | — | **81.25** | **76.45** |

**Final Scores**: **A: 81 | B: 76**

## 4. Base Variant Selection Rationale

**Selected base: Variant A (Opus Architect)**

Opus wins on 3 of 5 criteria (C1, C4, C5) and loses on 2 (C2, C3). The wins are decisive in C4 (+16 points) and C5 (+15 points), while the losses are narrower in C2 (-9 points) and C3 (-2 points).

The critical factor: Opus's weaknesses are **additive fixes** — incorporating Phase 0 deliverables and the consolidation fallback into Opus's structure is straightforward. Haiku's weaknesses are **structural** — adding line counts, dependency graphs, parallel markers, and specific verification commands to an 8-phase structure requires reworking the entire document's level of detail.

It is cheaper to add Haiku's compatibility safety measures to Opus's well-structured base than to retrofit Opus's implementation precision into Haiku's framework.

## 5. Specific Improvements to Incorporate from Variant B (Haiku)

### Must-incorporate (address Opus's scored weaknesses):

1. **Phase 0 deliverables as Phase 1 pre-work** (from D-2 debate convergence): Add a "Pre-work" section at the start of Phase 1 producing: change map, compatibility checklist, test matrix outline. Not a separate phase — embedded as Milestone 1.0. This resolves Opus's internal inconsistency between Rec #4 and the Phase 3 validation gate.

2. **Two-tier consolidation fallback** (D-11): Replace Opus's `commonpath()`-only strategy in Milestone 2.2 with Haiku's two-tier approach: `commonpath()` first, then top-10-by-component-count if still over cap. The debate demonstrated this is trivial to implement and eliminates a known gap.

3. **Validation streams A/B/C/D naming** (Phase 7, §5): Adopt Haiku's organized validation stream taxonomy in Phase 3.3. The four-stream structure (unit, integration, regression, non-functional) is clearer than Opus's flat list.

4. **CLI contract drift as distinct risk** (D-9, Risk #5 in Haiku): Add as Risk 7 in Opus's risk table. The debate showed Opus subsumes this under backward-compat but doesn't call it out — it deserves explicit mention given CLI is the highest user-visible surface.

5. **Formalize continuous testing as a gate** (from D-2 rebuttal): Convert Opus's Architectural Recommendation #4 from advisory to a structural requirement: "Run `uv run pytest` at each milestone boundary. Milestone is not complete until existing tests pass." This closes the inconsistency Haiku correctly identified.

### Nice-to-incorporate (lower priority):

6. **"Architect focus" callout boxes**: Haiku's per-phase architectural guidance notes are useful for maintaining design intent. Add as brief callouts within Opus's milestones where the guidance isn't already covered by the Architectural Recommendations section.

7. **Session-based grouping alongside hours**: Add Haiku's 3-session grouping (Sessions 1-3) as a secondary scheduling signal alongside Opus's hour ranges, per the debate's convergence recommendation.
