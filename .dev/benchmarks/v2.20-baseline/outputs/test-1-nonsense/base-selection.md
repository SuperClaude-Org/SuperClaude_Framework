

---
base_variant: A
variant_scores: "A:81 B:74"
---

# Base Selection: Opus Architect (A) vs Haiku Analyst (B)

## Scoring Criteria (Derived from Debate)

The debate surfaced four key divergences. I derive six scoring criteria from these plus the shared requirements:

1. **Intellectual Honesty** — Does the document avoid presenting speculative content as actionable?
2. **Recovery Granularity** — Does the recovery plan provide useful operational detail?
3. **Risk Coverage** — Are risks comprehensive and practically useful?
4. **Requirement Traceability** — Does the document map fictional requirements to real alternatives?
5. **Structural Discipline** — Is the document free of internal contradictions?
6. **Professional Authority** — Does the document maintain consistent tone and usability?

## Per-Criterion Scores (0–100)

| Criterion | Variant A (Opus) | Variant B (Haiku) | Rationale |
|---|---|---|---|
| Intellectual Honesty | **95** | 65 | Opus refuses to include phases for unscoped work. Haiku includes Phases 4–5 with timelines (2–4 weeks, 1–2 weeks) while simultaneously saying "do not authorize implementation." This is the contradiction Opus identified in the debate: headline-level commitments with footnote-level caveats. |
| Recovery Granularity | 60 | **88** | Haiku's four-phase recovery breakdown (triage → workshops → architecture → backlog) with sub-estimates provides genuinely useful operational detail. Opus's single "1–2 weeks" block is honest but operationally thin. Debate confirmed this is Haiku's strongest point. |
| Risk Coverage | 70 | **85** | Haiku includes the "False Low-Complexity Interpretation" risk — a real organizational hazard the debate validated. Haiku also has five risks vs Opus's four, with clearer prioritization tiers. Opus's counterargument (infinite regress) was weaker than Haiku's empirical point about risk register consumption patterns. |
| Requirement Traceability | **90** | 75 | Opus provides explicit 1:1 mapping (FR-001 → OAuth2/OIDC, FR-002 → connection pooling/read replicas/caching, etc.) in a scannable format. Haiku lists domains but doesn't map specific fictional requirements to specific real replacements as clearly. |
| Structural Discipline | **92** | 60 | Opus has zero internal contradictions. Haiku contradicts itself: "Do not authorize implementation work" followed by Phases 4–5 with staffing-grade timelines. The debate's strongest point was Opus's observation that stakeholders reading only Phases 4–5 would see commitments, not caveats. |
| Professional Authority | 78 | **82** | Haiku maintains consistent in-role analyst tone throughout. Opus's "Architect's Assessment" section breaks the fourth wall with benchmark speculation, which — as the debate noted — introduces tonal inconsistency. However, the gap is small because Opus's content authority is strong. |

## Overall Scores

**Variant A (Opus Architect): 81/100**
- Strengths: Disciplined refusal to speculate, strong requirement traceability, zero internal contradictions
- Weaknesses: Recovery plan lacks operational granularity, no named risk for complexity misinterpretation

**Variant B (Haiku Analyst): 74/100**
- Strengths: Excellent recovery decomposition, comprehensive risk register, consistent professional tone
- Weaknesses: Includes speculative phases that contradict its own recommendation, weaker requirement mapping

## Base Variant Selection Rationale

**Opus (A) is the base** because the most damaging flaw in a "do not implement" roadmap is including implementation phases. Haiku's Phases 4–5 undermine the document's core message — this is a structural problem that cannot be patched by adding caveats. Opus's weaknesses (thin recovery detail, missing a risk entry) are additive fixes that don't require restructuring.

The debate's convergence assessment reached the same conclusion: "An optimal merged artifact would adopt Opus's single-phase discipline."

## Specific Improvements to Incorporate from Variant B

1. **Recovery sub-phases**: Replace Opus's monolithic Phase 0 with Haiku's four-step breakdown (triage 0.5–1d → workshops 2–4d → architecture framing 3–5d → backlog construction 2–3d), but keep them as sub-phases within Phase 0 rather than independent phases
2. **Risk #5 — False Low-Complexity Interpretation**: Add Haiku's named risk with its mitigation language verbatim. The debate validated this as a real organizational hazard worth three lines
3. **Validation gates**: Adopt Haiku's five-gate validation structure (Spec Quality → Dependency Validity → Architecture → Backlog Readiness → Release) as a section in the merged document
4. **Role specificity**: Incorporate Haiku's five-role breakdown for the planning phase (business owner, BA, architect, engineering lead, QA lead) into Opus's Resource Requirements section
5. **Phase success criteria**: Add Haiku's per-phase success criteria for the recovery sub-phases — these provide measurable checkpoints Opus lacks
6. **Remove meta-commentary**: Drop Opus's "Architect's Assessment" section with benchmark speculation. The debate showed this introduces tonal inconsistency without adding decision-relevant content
