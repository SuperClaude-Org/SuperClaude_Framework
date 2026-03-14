# Base Selection: v2.25 Roadmap v5 Spec

## Quantitative Scoring (50% weight)

### Per-Metric Breakdown

| Metric | Weight | Variant A | Variant B | Notes |
|--------|--------|-----------|-----------|-------|
| Requirement Coverage (RC) | 0.30 | 0.92 | 0.85 | A covers blast radius (brainstorm §4), YAML parsing constraints. B defers blast radius, has parser placeholder. |
| Internal Consistency (IC) | 0.25 | 0.95 | 0.90 | A has no internal contradictions. B has minor inconsistency: `parse_findings_from_classify_output()` marked "implementation detail" but required for pipeline function. |
| Specificity Ratio (SR) | 0.15 | 0.88 | 0.82 | A has 12 concrete Python code blocks, all with complete signatures. B has 10, with 1 placeholder ("regex or structured parsing"). |
| Dependency Completeness (DC) | 0.15 | 0.90 | 0.88 | A's section cross-references all resolve. B's LoopStep references `gate_passed()` import not explicitly stated. |
| Section Coverage (SC) | 0.15 | 0.93 | 1.00 | B has 16 sections + 3 appendices = max coverage. A has 15 sections. |

**Quantitative Scores**:
- Variant A: (0.92×0.30) + (0.95×0.25) + (0.88×0.15) + (0.90×0.15) + (0.93×0.15) = 0.276 + 0.238 + 0.132 + 0.135 + 0.140 = **0.921**
- Variant B: (0.85×0.30) + (0.90×0.25) + (0.82×0.15) + (0.88×0.15) + (1.00×0.15) = 0.255 + 0.225 + 0.123 + 0.132 + 0.150 = **0.885**

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements from source input | **MET** — All 10 brainstorm open questions resolved (Section 13) | **MET** — All 10 open questions resolved (Section 15) |
| 2 | Addresses edge cases and failure scenarios | **MET** — Composition table (Section 9.1) covers 6 scenarios including over-approval, all-ambiguous | **MET** — v2.24 retroactive analysis (Section 14), loop exhaustion (Section 6.4) |
| 3 | Includes dependencies and prerequisites | **MET** — Phase dependency chain explicit (Phase 2 depends on Phase 1 output) | **MET** — Deliverable dependency graph (Section 10.2) |
| 4 | Defines success/completion criteria | **MET** — 10 success criteria (Section 15) covering functional and non-functional | **MET** — 6 success criteria (Section 16) |
| 5 | Specifies what is explicitly out of scope | **MET** — OQ-6 (blast radius depth configurable: "v6 consideration"), OQ-8 (spec update: "manual handoff") | **MET** — OQ-6 (blast radius: "deferred to v2.26"), OQ-8 (spec update: "deferred") |

**Variant A: 5/5 | Variant B: 5/5**

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | **MET** — All code aligns with existing codebase | **MET** — All code aligns; LoopStep is clearly marked as new |
| 2 | Technical approaches are feasible with stated constraints | **MET** — Uses only existing primitives, tested patterns | **MET** — LoopStep is feasible; `isinstance` dispatch is standard |
| 3 | Terminology used consistently and accurately | **MET** — Consistent use of INTENTIONAL/SLIP/AMBIGUOUS/PRE_APPROVED throughout | **MET** — Consistent use of INTENTIONAL/SLIP/AMBIGUOUS/UNCLASSIFIED throughout |
| 4 | No internal contradictions | **MET** — No contradictions detected | **NOT MET** — `parse_findings_from_classify_output()` says "implementation detail: regex or structured parsing" but the function is critical path. Contradicts spec's claim of "concrete, implementation-ready" design. |
| 5 | Claims supported by evidence or rationale | **MET** — Each design decision cites root cause (F-1 through F-6) | **MET** — Each decision references brainstorm sections |

**Variant A: 5/5 | Variant B: 4/5**

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering (prerequisites before dependents) | **MET** — Problem → Design → New Steps → Modifications → Implementation | **MET** — Problem → Design → Pipeline Flow → Steps → Primitives → Implementation |
| 2 | Consistent hierarchy depth | **MET** — H2 → H3 throughout, no orphaned subsections | **MET** — H2 → H3 throughout |
| 3 | Clear separation of concerns between sections | **MET** — Each step has its own section with definition/prompt/gate/output | **MET** — Similar pattern |
| 4 | Navigation aids present | **NOT MET** — No table of contents or appendices | **MET** — Three appendices (A: type signatures, B: gate summary, C: code references) |
| 5 | Follows conventions of the artifact type | **MET** — YAML frontmatter, code examples, risk matrix | **MET** — Same conventions |

**Variant A: 4/5 | Variant B: 5/5**

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | **MET** — Concrete language throughout; no "should consider" or "as appropriate" | **MET** — Similar concrete language |
| 2 | Concrete rather than abstract | **MET** — All 12 code blocks are complete with signatures and logic | **NOT MET** — `parse_findings_from_classify_output()` has "regex or structured parsing" placeholder |
| 3 | Each section has clear purpose | **MET** — Section purposes are clear and bounded | **MET** — Section purposes clear |
| 4 | Acronyms and domain terms defined on first use | **MET** — F-1 through F-6 defined in Section 1.2; SLIP/INTENTIONAL defined in Section 1.3 | **MET** — Terms defined in Section 1.3 |
| 5 | Actionable next steps identified | **MET** — Phase deliverable tables with per-file changes | **MET** — 20-deliverable table with LOC estimates |

**Variant A: 5/5 | Variant B: 4/5**

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Identifies at least 3 risks with probability and impact | **MET** — 9 risks with severity + probability + mitigation (Section 12) | **MET** — 8 risks + 2 structural risks (Section 12) |
| 2 | Provides mitigation strategy for each identified risk | **MET** — All 9 risks have mitigations; R-9 has dedicated subsection | **MET** — All risks have mitigations |
| 3 | Addresses failure modes and recovery | **MET** — Terminal halt with manual-fix instructions (Section 8.5); resume flow diagram (Section 8.6) | **MET** — Loop exhaustion terminal halt (Section 6.4) |
| 4 | Considers external dependencies and their failure scenarios | **MET** — Context window pressure (R-4), YAML parsing (R-9) | **MET** — Single-pass quality (Risk 2), LoopStep complexity (Risk 1) |
| 5 | Includes monitoring or validation mechanism | **MET** — `remediation_attempts` counter for monitoring; composition table for validation | **MET** — Iteration-scoped step IDs for monitoring |

**Variant A: 5/5 | Variant B: 5/5**

### Invariant & Edge Case Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Addresses boundary conditions for collections | **MET** — Empty routing lists handled in `deviations_to_findings()` (returns []) | **MET** — Empty findings list handled by parser |
| 2 | Handles state variable interactions across components | **MET** — `remediation_attempts` counter interaction with resume logic explicitly documented | **MET** — Iteration-scoped step IDs prevent state collision |
| 3 | Identifies guard condition gaps | **MET** — R-9 identifies `_parse_frontmatter()` limitation as a guard condition gap | **NOT MET** — No equivalent analysis of parser guard conditions |
| 4 | Covers count divergence scenarios | **MET** — Section 5.6 explicitly explains why `ambiguous_count == 0` and NOT `adjusted_high_severity_count == 0` | **MET** — Section 4.5 critical design decision explains same |
| 5 | Considers interaction effects | **MET** — Composition table (Section 9.1) covers 6 interaction scenarios between Scope 1 and Scope 2 | **NOT MET** — No equivalent interaction analysis between classify-and-validate and LoopStep |

**Variant A: 5/5 | Variant B: 3/5**

### Edge Case Floor Check
- Variant A: 5/5 — eligible
- Variant B: 3/5 — eligible (above 1/5 threshold)

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 5/5 | 5/5 |
| Correctness | 5/5 | 4/5 |
| Structure | 4/5 | 5/5 |
| Clarity | 5/5 | 4/5 |
| Risk Coverage | 5/5 | 5/5 |
| Invariant & Edge Case | 5/5 | 3/5 |
| **Total** | **29/30** | **26/30** |

**Qualitative Scores**:
- Variant A: 29/30 = **0.967**
- Variant B: 26/30 = **0.867**

---

## Position-Bias Mitigation

| Dimension | Variant | Pass 1 (A,B) | Pass 2 (B,A) | Agreement | Final |
|-----------|---------|-------------|-------------|-----------|-------|
| Correctness #4 | B | NOT MET | NOT MET | Agree | NOT MET |
| Structure #4 | A | NOT MET | NOT MET | Agree | NOT MET |
| Clarity #2 | B | NOT MET | NOT MET | Agree | NOT MET |
| Invariant #3 | B | NOT MET | NOT MET | Agree | NOT MET |
| Invariant #5 | B | NOT MET | NOT MET | Agree | NOT MET |

Disagreements found: 0
All verdicts agreed across both passes.

---

## Combined Scoring

| Metric | Variant A | Variant B |
|--------|-----------|-----------|
| Quantitative (50%) | 0.921 × 0.50 = 0.461 | 0.885 × 0.50 = 0.443 |
| Qualitative (50%) | 0.967 × 0.50 = 0.484 | 0.867 × 0.50 = 0.434 |
| **Combined Score** | **0.944** | **0.876** |
| **Margin** | — | -6.8% |

Tiebreaker not needed (margin > 5%).

---

## Selected Base: Variant A (opus:architect — Incremental Refactor)

### Selection Rationale

Variant A wins on both quantitative (0.921 vs 0.885) and qualitative (0.967 vs 0.867) axes. The margin (6.8%) exceeds the 5% tiebreaker threshold.

Key factors:
1. **Higher implementation specificity**: All code blocks are complete — no placeholders
2. **Stronger invariant/edge case coverage**: YAML parsing risk (R-9), composition table, blast radius analysis
3. **Phased delivery**: Intermediate value with lower risk
4. **No generic-layer changes**: Zero risk to non-roadmap pipelines

### Strengths to Preserve from Base (Variant A)
- Two-step classification architecture (annotate → classify)
- Defense-in-depth composition (Scope 2 prevents, Scope 1 recovers)
- Phased implementation plan with intermediate deliverables
- Spec-fidelity retained as diagnostic step
- Blast radius analysis for INTENTIONAL deviations
- YAML frontmatter flat-field mitigation (R-9)
- `deviations_to_findings()` deterministic conversion
- 4-class annotation granularity

### Strengths to Incorporate from Variant B
- `_certified_is_true` semantic check implementation (B's is slightly more concise)
- "UNCLASSIFIED" vs empty string for backward compat default (B's is more semantic)
- Backward compatibility section depth (B covers 5 explicit surfaces)
- Appendices for quick reference (type signatures, gate summary, code references)
- Terminal halt formatting for loop exhaustion (B's format is clearer)
- Consideration of LoopStep as v2.26 follow-up (noted, not implemented)
