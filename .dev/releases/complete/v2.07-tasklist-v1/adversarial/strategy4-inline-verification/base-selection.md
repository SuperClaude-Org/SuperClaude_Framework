# Base Selection & Scoring — Strategy 4: Inline Verification Coupling

**Pipeline Step**: 3 of 5
**Date**: 2026-03-04

---

## 1. Scoring Methodology

Two-component hybrid scoring: quantitative metrics (objective, deterministic) + qualitative rubric (CEV protocol — Claim, Evidence, Verdict).

**Final score** = (Quantitative × 0.55) + (Qualitative × 0.45)
**Adoption threshold**: ≥ 0.65 combined score = Adopt | 0.45–0.64 = Modify | < 0.45 = Reject

---

## 2. Quantitative Metrics

### 2.1 Sub-component S4a — Semantic constraint on existing Acceptance Criteria fields

| Metric | Score (0–1) | Rationale |
|---|---|---|
| Gap addressability | 0.85 | Gap confirmed in diff-analysis: proximity problem is real and affects executor reliability |
| Parity compatibility | 0.80 | Semantic constraint on existing fields; no new schema fields; output format identical |
| Implementation precision | 0.45 | "Near-field" and "explicit completion condition" are underspecified in source text; require definition |
| Risk surface | 0.75 | Low structural risk; medium semantic non-determinism risk (mitigable) |
| Effort proportionality | 0.85 | Spec change to §4.7 Acceptance Criteria rules + §8 self-check; no template restructuring |
| Uniqueness vs existing content | 0.60 | Partial overlap: existing §4.7 mandates Acceptance Criteria; S4a adds a quality standard on top |

**S4a Quantitative Average**: 0.717

### 2.2 Sub-component S4b — §8 self-check semantic gate

| Metric | Score (0–1) | Rationale |
|---|---|---|
| Gap addressability | 0.90 | Directly addresses absence of semantic verification in self-check |
| Parity compatibility | 0.90 | Changes generator process only; output format unchanged |
| Implementation precision | 0.60 | Requires "explicit completion condition" to be quantified; source is underspecified |
| Risk surface | 0.80 | Self-check failure forces regeneration; padding risk is real but mitigable |
| Effort proportionality | 0.90 | Single sentence addition to §8 + quantification definition; minimal spec change |
| Uniqueness vs existing content | 0.80 | No existing self-check verifies semantic content quality |

**S4b Quantitative Average**: 0.817

**Combined Quantitative Score** (S4a + S4b weighted by relative scope — S4b is 60% of the strategy value, S4a 40%):
= (0.717 × 0.40) + (0.817 × 0.60) = 0.287 + 0.490 = **0.777**

---

## 3. Qualitative Rubric (CEV Protocol)

### Criterion 1: Sprint CLI Execution Value

**Claim**: Inline verification coupling increases Sprint CLI execution reliability by reducing executor search distance for completion signals.

**Evidence**:
- v3.0 §6B places `Acceptance Criteria` and `Validation` after the metadata table (16 rows) and Steps (3-8 items) — structural distance is 25-45 lines from task title.
- Sprint CLI executes tasks as discrete agent invocations. Each invocation has a bounded context. Far-field completion signals risk falling out of the active context window during execution.
- taskbuilder v2 co-location pattern (`"ensuring..."` clause) was designed specifically for this constraint and is documented as production-tested in headless agent execution.

**Verdict**: Claim supported. Execution value is real and directly applicable to Sprint CLI.

Score: 0.85

### Criterion 2: Parity Constraint Compatibility

**Claim**: Strategy 4 as scoped (semantic constraints, no new fields) is compatible with the strict v1.0 parity requirement.

**Evidence**:
- v1.0 parity = "output is identical to running the v3.0 generator prompt manually" (Acceptance Criterion 7, sc-tasklist-command-spec-v1.0.md).
- S4a as semantic constraint does not change output schema — same fields, higher quality standard for field content.
- S4b adds a generator internal self-check that forces regeneration if quality standard is not met, but does not add fields to output.
- Final output from a generator with S4a+S4b applied contains the same fields as v3.0, with substantively better Acceptance Criteria content.
- The parity claim is about functional and structural output identity, not content quality identity. Higher quality content within the same schema is parity-compatible.

**Verdict**: Claim supported with one caveat: if "parity" is interpreted as byte-identical output rather than schema-compatible output, S4a fails because it requires different content in Acceptance Criteria bullets. The spec does not define parity at byte level; functional parity is the operative definition.

Score: 0.78

### Criterion 3: Implementation Determinism

**Claim**: Strategy 4 can be implemented deterministically in the generator algorithm.

**Evidence**:
- S4b requires evaluating whether an Acceptance Criteria bullet is "explicitly verifiable." This requires NL judgment.
- Debate convergence: the rule must be quantified as "names a specific artifact, command, or test result" to be bounded.
- Bounded check is semi-deterministic: the generator can apply a pattern check (does the bullet mention a file path, test command, or observable state?).
- Non-determinism risk: borderline cases will exist where the generator's judgment varies across runs.
- Mitigation: 2 example pass/fail pairs calibrate the generator's judgment. With examples, variance is significantly reduced but not eliminated.

**Verdict**: Partially supported. Semi-deterministic is achievable with quantification. Full determinism is not achievable for NL content evaluation. This is acceptable for quality gates (which are inherently evaluative) and aligns with existing practices in v3.0 §5.4 confidence scoring, which is also semi-deterministic.

Score: 0.70

### Criterion 4: Risk Profile

**Claim**: The risk profile of Strategy 4 (as scoped) is low enough to justify v1.0 inclusion.

**Evidence**:
- Structural risk: None if no new fields are added.
- Semantic risk: Generator may pad Acceptance Criteria to satisfy the rule. Mitigation: require criteria to derive from roadmap content (non-invention rule already exists in §0).
- Self-check risk: Generator may fail tasks with legitimately adequate criteria. Mitigation: quantified definition with examples bounds the failure rate.
- Parity risk: Low — schema unchanged, content quality increases.
- Regression risk: No existing tests check Acceptance Criteria content quality, so no existing tests break.

**Verdict**: Claim supported. Risk profile is low-to-medium with specified mitigations applied.

Score: 0.80

---

## 4. Qualitative Score

| Criterion | Weight | Score | Weighted |
|---|---|---|---|
| Sprint CLI execution value | 30% | 0.85 | 0.255 |
| Parity constraint compatibility | 30% | 0.78 | 0.234 |
| Implementation determinism | 25% | 0.70 | 0.175 |
| Risk profile | 15% | 0.80 | 0.120 |

**Qualitative Total**: 0.784

---

## 5. Combined Score

**Combined** = (Quantitative × 0.55) + (Qualitative × 0.45)
= (0.777 × 0.55) + (0.784 × 0.45)
= 0.427 + 0.353
= **0.780**

**Threshold check**: 0.780 ≥ 0.65 → **ADOPT (with modifications)**

---

## 6. Selection Rationale

Strategy 4 clears the adoption threshold with a score of 0.780 against a threshold of 0.65.

The strategy addresses a real and documented gap: v3.0 places completion signals structurally far from action content, which degrades executor reliability in Sprint CLI's bounded-context execution model.

Adoption is conditional on three required modifications that emerged from the debate:
1. "Near-field" must be defined as "first Acceptance Criteria bullet must name a specific output, command, or observable state derived from the roadmap."
2. "Explicit completion condition" in the §8 self-check must be quantified as above.
3. The non-invention rule (§0) must be explicitly referenced in the §8 check to prevent padding.

The structural format change variant (new `Verify:` field, repositioned content) scores below threshold for v1.0 due to parity constraint conflict and must be deferred to v1.1.

---

## 7. Tiebreaker Protocol

Not triggered. Score 0.780 is 0.130 above threshold. No ambiguity.

---

## 8. Decision

**ADOPT — Modified scope**:
- S4a: Semantic constraint on first Acceptance Criteria bullet (near-field completion criterion defined as specific artifact/command/state).
- S4b: §8 self-check upgrade with quantified "explicit completion condition" definition.
- Deferred to v1.1: Structural `Verify:` field addition, content repositioning.
