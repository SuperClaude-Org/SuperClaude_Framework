# Base Selection: Hybrid Scoring & Selection

## Quantitative Scoring (50% weight)

### Metric Computation

#### Requirement Coverage (RC) — Weight: 0.30
Source requirements extracted from the shared subject matter: sc-tasklist v1.0 spec improvements across 5 strategies (stage gating, error handling, task quality, acceptance criteria, pre-write validation).

| Requirement | Variant A | Variant B |
|------------|-----------|-----------|
| Strategy 1: Stage execution model | ✅ Full stage-gated contract with 6 stages | ✅ Stage completion reporting via TodoWrite |
| Strategy 2: Input validation improvements | ✅ 5-patch implementation with error format | ✅ Empty-file guard + Generation Notes |
| Strategy 3: Task quality rules | ✅ 4-criterion standalone requirement | ✅ 2-criterion minimum specificity |
| Strategy 4: Acceptance criteria enforcement | ✅ Near-field completion criterion + non-invention | ✅ Tier-proportional enforcement |
| Strategy 5: Pre-write validation | ✅ Checks 9-12 + atomic write | ✅ Checks 13-17 |
| Cross-strategy patch ordering | ❌ Per-strategy only | ✅ Unified ordering with estimates |
| Debate provenance/rationale | ❌ Not included | ✅ Full debate verdicts |
| v1.1 deferral tracking | ⚠️ Per-strategy scattered | ✅ Consolidated table |
| Token cost analysis | ❌ Not included | ✅ Per-strategy annotations |
| Risks to address | ⚠️ Per-strategy risk tables | ✅ Consolidated risks section |

**Variant A**: 5 full + 2 partial = 6/10 = **RC_A = 0.60**
**Variant B**: 8 full + 0 partial = 8/10 = **RC_B = 0.80**

#### Internal Consistency (IC) — Weight: 0.25
Contradictions detected within each variant:

**Variant A**:
- Strategy 1 uses "halt" language that debates already renamed → internally inconsistent with post-debate status
- Strategy 4 adds §9 criterion 8; Strategy 5 also adds §9 criterion 8 → numbering collision
- Strategy 3 adds §8.N check; Strategy 4 adds §8 item 9; Strategy 5 adds §8.1 checks 9-12 → numbering conflicts across strategies
- Total contradictions: 3 within ~980 lines, ~45 substantive claims
- **IC_A = 1 - (3/45) = 0.93**

**Variant B**:
- Strategy 5 adds checks "13-17" but existing spec only has checks 1-8; gap 9-12 unaccounted for → numbering assumption
- No other internal contradictions detected
- Total contradictions: 1 within ~226 lines, ~25 substantive claims
- **IC_B = 1 - (1/25) = 0.96**

#### Specificity Ratio (SR) — Weight: 0.15
Concrete vs vague statements:

**Variant A**: Heavy on exact patch text with specific section references (§4.3, §5.4, §6.2, §8, §9), specific formats (TASKLIST VALIDATION ERROR), specific file paths. Concrete indicators: ~120. Vague indicators: ~8.
- **SR_A = 120/128 = 0.94**

**Variant B**: Mix of concrete spec changes ("In §5.4, add...") and softer language ("catches worst offenders", "paves the way"). Concrete indicators: ~40. Vague indicators: ~12.
- **SR_B = 40/52 = 0.77**

#### Dependency Completeness (DC) — Weight: 0.15
Internal references that resolve:

**Variant A**: References §4.3, §5.4, §6.2, §6B, §7, §8, §9, §10 — all resolve within the document or to the target spec. Self-contained patch blocks. One unresolved: "Tasklist-Generator-Prompt-v2.1-unified.md" file path referenced but not included. Total: 22 refs, 21 resolved.
- **DC_A = 21/22 = 0.95**

**Variant B**: References §5.4, §5.7, §6.2, §6.4, §7, §8, §8.1 — all resolve to target spec sections. References "debates/debate-proposal-{1..5}-*.md" — external. Total: 15 refs, 14 resolved.
- **DC_B = 14/15 = 0.93**

#### Section Coverage (SC) — Weight: 0.15
Top-level sections (H2):

**Variant A**: 5 strategy plans × ~6 sections each = ~30 H2 sections (highest)
**Variant B**: Executive Summary + 5 strategies + Additional Context + Patch Order + Deferred Items = 9 H2 sections

- **SC_A = 30/30 = 1.00**
- **SC_B = 9/30 = 0.30**

### Quantitative Formula

```
quant_score = (RC × 0.30) + (IC × 0.25) + (SR × 0.15) + (DC × 0.15) + (SC × 0.15)
```

**Variant A**: (0.60 × 0.30) + (0.93 × 0.25) + (0.94 × 0.15) + (0.95 × 0.15) + (1.00 × 0.15)
= 0.180 + 0.233 + 0.141 + 0.143 + 0.150 = **0.847**

**Variant B**: (0.80 × 0.30) + (0.96 × 0.25) + (0.77 × 0.15) + (0.93 × 0.15) + (0.30 × 0.15)
= 0.240 + 0.240 + 0.116 + 0.140 + 0.045 = **0.781**

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A (Pass 1) | Variant A (Pass 2) | Variant B (Pass 1) | Variant B (Pass 2) |
|---|-----------|----------|----------|----------|----------|
| 1 | Covers all explicit requirements from source input | MET — All 5 strategies addressed with patches | MET | MET — All 5 strategies addressed with verdicts | MET |
| 2 | Addresses edge cases and failure scenarios | MET — Risk tables per strategy, failure handling noted | MET | NOT MET — No explicit edge case / failure handling beyond debate rejections | NOT MET |
| 3 | Includes dependencies and prerequisites | MET — Implementation orders with dependency notes (e.g., "IP-1 complete before IP-2") | MET | NOT MET — Patch order given but no inter-strategy dependencies identified | NOT MET |
| 4 | Defines success/completion criteria | MET — Validation tables with method/pass criteria (Strategy 1 lines 176-183, Strategy 5 lines 970-980) | MET | NOT MET — No explicit success criteria beyond "apply patches" | NOT MET |
| 5 | Specifies what is explicitly out of scope | MET — "Non-Modified Sections" and "What This Does NOT Change" sections per strategy | MET | MET — "What was rejected" per strategy + v1.1 deferral table | MET |

**EVIDENCE (CEV)**:
- A-C2 MET: Strategy 1 lines 176-183 list 5 validation checks. Strategy 3 lines 613-621 list 4 risks with mitigation.
- B-C2 NOT MET: Searched all 5 strategy sections; no "edge case", "failure scenario", or "risk" subsection found. Debate rejections are scope constraints, not failure handling.
- A-C4 MET: Strategy 5 lines 970-980: "After applying the four patches, the following must be true" with verification table.
- B-C4 NOT MET: No "success criteria", "validation", or "verification" section found.

**Variant A Completeness**: 5/5
**Variant B Completeness**: 2/5

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | NOT MET — Uses pre-debate strategy names despite post-debate rename; §9 criterion 8 collision across strategies | MET — Post-debate names used consistently |
| 2 | Technical approaches are feasible with stated constraints | MET — All patches are additive, low-risk, targeting existing spec sections | MET — All changes are parity-compatible |
| 3 | Terminology used consistently and accurately | NOT MET — "Stage-Gated" title retained despite debate renaming; inconsistent check numbering (9-12 vs item 9 across strategies) | MET — Consistent post-debate terminology |
| 4 | No internal contradictions | NOT MET — Multiple §9 criterion 8 additions; §8 check numbering collisions (see IC analysis) | MET — Single numbering scheme (13-17) |
| 5 | Claims supported by evidence or rationale | MET — Each change includes rationale, risk level, and patch location | MET — Each change includes debate verdict and rationale |

**EVIDENCE (CEV)**:
- A-Cor1 NOT MET: Title "Step 4: Refactoring Plan — Strategy 1: Stage-Gated Generation Contract" (line 5) uses pre-debate name; debate renamed to "Stage Completion Reporting".
- A-Cor3 NOT MET: Strategy 3 adds "§8.N" check (line 514); Strategy 4 adds "§8 item 9" (line 705); Strategy 5 adds "§8.1 checks 9-12" (line 864) — three different numbering schemes for the same self-check section.
- A-Cor4 NOT MET: Both Strategy 3 IP-3 (line 548) and Strategy 5 IP-2A (line 910) add "criterion 8" to §9 Acceptance Criteria.

**Variant A Correctness**: 2/5
**Variant B Correctness**: 5/5

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | NOT MET — 5 concatenated documents without logical integration; Strategy 5 follows Strategy 4 but they share §8 modifications without cross-referencing | MET — Single unified flow: summary → strategies → context → patch order |
| 2 | Consistent hierarchy depth | NOT MET — Each strategy has its own H1; depth varies from H1-H3 across strategies | MET — Single H1, consistent H2-H3 hierarchy |
| 3 | Clear separation of concerns | MET — Each strategy is fully self-contained | MET — Each strategy is a numbered section |
| 4 | Navigation aids present | NOT MET — No table of contents, no cross-strategy index | NOT MET — No table of contents (though shorter doc) |
| 5 | Follows conventions of artifact type (refactor plan) | MET — Standard refactor plan structure per strategy | MET — Standard integration strategy document |

**Variant A Structure**: 2/5
**Variant B Structure**: 4/5

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | MET — Exact patch text eliminates ambiguity in implementation | MET — "MUST", "Do NOT" language used throughout |
| 2 | Concrete rather than abstract | MET — Every change has current/replacement text blocks | NOT MET — Some directions are abstract: "tighten existing fields" without patch text |
| 3 | Each section has clear purpose | MET — Clear section purposes throughout | MET — Clear section purposes |
| 4 | Acronyms and domain terms defined | NOT MET — Uses §6B, §4.3, etc. without defining these for new readers | NOT MET — Same issue |
| 5 | Actionable next steps clearly identified | MET — Implementation order tables per strategy | MET — Unified patch order with time estimates |

**Variant A Clarity**: 4/5
**Variant B Clarity**: 3/5

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Identifies ≥3 risks with probability and impact | MET — Strategy 3: 4 risks with Probability/Severity (lines 613-621); Strategy 4: 4 risks (lines 800-805) | NOT MET — No explicit risk assessment section |
| 2 | Provides mitigation strategy for each risk | MET — Mitigation column in risk tables | NOT MET — No mitigation strategies |
| 3 | Addresses failure modes and recovery | MET — "What This Does NOT Change" sections + validation checks | NOT MET — No failure mode analysis |
| 4 | Considers external dependencies | MET — References to v3.0 generator, sprint CLI, SKILL.md carry-forward | MET — References to taskbuilder.md, debate artifacts, v1.1 dependencies |
| 5 | Includes monitoring/validation mechanism | MET — Validation tables per strategy (lint-architecture, manual review, text diff) | NOT MET — No validation mechanism described |

**Variant A Risk Coverage**: 5/5
**Variant B Risk Coverage**: 1/5

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 5/5 | 2/5 |
| Correctness | 2/5 | 5/5 |
| Structure | 2/5 | 4/5 |
| Clarity | 4/5 | 3/5 |
| Risk Coverage | 5/5 | 1/5 |
| **Total** | **18/25** | **15/25** |

**qual_A = 18/25 = 0.72**
**qual_B = 15/25 = 0.60**

---

## Position-Bias Mitigation

### Dual-Pass Results

| Criterion | Variant | Pass 1 | Pass 2 | Agreement | Final |
|-----------|---------|--------|--------|-----------|-------|
| Completeness-2 | A | MET | MET | ✅ | MET |
| Completeness-2 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Completeness-3 | A | MET | MET | ✅ | MET |
| Completeness-3 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Completeness-4 | A | MET | MET | ✅ | MET |
| Completeness-4 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Correctness-1 | A | NOT MET | NOT MET | ✅ | NOT MET |
| Correctness-3 | A | NOT MET | NOT MET | ✅ | NOT MET |
| Correctness-4 | A | NOT MET | NOT MET | ✅ | NOT MET |
| Structure-1 | A | NOT MET | NOT MET | ✅ | NOT MET |
| Structure-2 | A | NOT MET | NOT MET | ✅ | NOT MET |
| Clarity-2 | B | NOT MET | MET | ❌ | **RE-EVALUATED** |
| Risk-1 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Risk-2 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Risk-3 | B | NOT MET | NOT MET | ✅ | NOT MET |
| Risk-5 | B | NOT MET | NOT MET | ✅ | NOT MET |

### Disagreement Resolution

**Clarity-2 for Variant B (concrete rather than abstract)**:
- Pass 1 evidence: "tighten existing fields" and "catch worst offenders" are abstract guidance without patch text → NOT MET
- Pass 2 evidence: "In §5.4 Input Validation, add:" followed by exact quotes of new text; "In §7 Style Rules, add:" with exact rule text → MET
- Re-evaluation: Variant B includes specific quoted text for concrete spec changes in each strategy section ("Every task description MUST reference at least one specific artifact"). While less detailed than Variant A's full current/replacement blocks, the changes ARE concrete. However, several strategies lack patch text for all locations. Mixed evidence.
- **Final verdict: NOT MET** — Concreteness is inconsistent; some strategies have specific text, others are directive-only.

**Disagreements found**: 1
**Verdicts changed**: 0 (re-evaluation confirmed original)

**Final scores unchanged**: qual_A = 0.72, qual_B = 0.60

---

## Combined Scoring

```
variant_score = (0.50 × quant_score) + (0.50 × qual_score)
```

**Variant A**: (0.50 × 0.847) + (0.50 × 0.72) = 0.424 + 0.360 = **0.784**
**Variant B**: (0.50 × 0.781) + (0.50 × 0.60) = 0.391 + 0.300 = **0.691**

### Margin Analysis

| Metric | Variant A | Variant B | Delta |
|--------|-----------|-----------|-------|
| Quant Score | 0.847 | 0.781 | +0.066 (A) |
| Qual Score | 0.720 | 0.600 | +0.120 (A) |
| Combined | 0.784 | 0.691 | +0.093 (A) |

**Margin**: 9.3% — exceeds 5% tiebreaker threshold. No tiebreaker required.

### Tiebreaker Status
- Tiebreaker applied: **No** (margin 9.3% > 5% threshold)

---

## Selected Base: Variant A (refactor-plan-merged.md)

### Selection Rationale
Variant A wins on combined scoring (0.784 vs 0.691) driven by superior completeness (5/5 vs 2/5), clarity through exact patch text (4/5 vs 3/5), and comprehensive risk coverage (5/5 vs 1/5). Despite losing on correctness (2/5 vs 5/5) and structure (2/5 vs 4/5), the implementation-readiness of Variant A — with exact current/replacement patch blocks, validation tables, and risk assessments — makes it the stronger base for producing a unified refactor plan.

### Strengths to Preserve from Base (Variant A)
1. Exact patch text with current/replacement blocks for all spec locations
2. Per-strategy risk assessment tables with probability/severity/mitigation
3. Near-field completion criterion with non-invention constraint (Strategy 4)
4. Atomic write declaration (Strategy 5)
5. Per-strategy validation/verification tables
6. Comprehensive edge case and failure mode coverage

### Strengths to Incorporate from Variant B
1. **Post-debate strategy names and verdicts** — Replace A's pre-debate names with B's debate-tested names (corrects A's Correctness-1 and Correctness-3 failures)
2. **Unified document structure** — Restructure from concatenated plans to single unified document (corrects A's Structure-1 and Structure-2 failures)
3. **Consolidated v1.1 deferral table** — Replace scattered per-strategy deferrals with B's consolidated table
4. **Unified patch order with time estimates** — Add B's cross-strategy implementation sequence
5. **Debate context and rejection rationale** — Integrate B's "What was rejected" sections for decision provenance
6. **Token cost annotations** — Add B's per-strategy token cost notes
7. **Strategy 1 scope adjustment** — Adopt B's debate verdict: rename to "Stage Completion Reporting", apply debate convergence (hybrid gating from Round 3)
8. **Strategy 2 scope adjustment** — Adopt B's reduced v1.0 scope (empty-file guard + Generation Notes + 2-field error format per debate convergence)
9. **Strategy 3 scope adjustment** — Adopt 3-criterion compromise from debate convergence
10. **Checks numbering reconciliation** — Resolve A's check numbering collisions using debate outcomes
