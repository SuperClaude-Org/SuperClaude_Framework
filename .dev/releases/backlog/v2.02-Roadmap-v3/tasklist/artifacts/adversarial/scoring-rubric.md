# Hybrid Scoring Rubric

**Pipeline**: sc:adversarial comparison of 3 approaches
**Date**: 2026-02-23

---

## Layer 1: Quantitative Scoring (50% weight)

### Metric Definitions

| Metric | Weight | Description |
|--------|--------|-------------|
| RC (Requirement Coverage) | 0.30 | How completely does the approach address the stated requirements (headless invocation, fallback, return contract, error handling, sprint fit)? |
| IC (Internal Consistency) | 0.25 | Are there contradictions between sections? Does the approach promise things it can't deliver? |
| SR (Specificity Ratio) | 0.15 | Ratio of concrete/implementable specifications to vague/deferred decisions |
| DC (Dependency Completeness) | 0.15 | Are all referenced components (SKILL.md sections, return contract fields, ref files) fully specified? |
| SC (Section Coverage) | 0.15 | Coverage of the 6 debate dimensions: reliability, complexity, fidelity, risk, maintainability, sprint fit |

### Quantitative Scores

| Metric | Weight | Approach 1 | Approach 2 | Approach 3 |
|--------|--------|-----------|-----------|-----------|
| RC | 0.30 | 0.60 | 0.95 | 0.90 |
| IC | 0.25 | 0.90 | 0.92 | 0.80 |
| SR | 0.15 | 0.45 | 0.92 | 0.75 |
| DC | 0.15 | 0.70 | 0.90 | 0.85 |
| SC | 0.15 | 0.75 | 0.88 | 0.90 |
| **Weighted** | | **0.670** | **0.924** | **0.843** |

### Scoring Justification

**Approach 1 — RC: 0.60**: Covers probe and risk analysis but does NOT cover the actual implementation (headless command template, fallback protocol, return contract write instructions). It's a pre-gate, not a design.

**Approach 1 — SR: 0.45**: 13 test specifications are concrete, but the "Sprint-Spec Changes" section (Section 5) is abstract — it says "replace Task 0.0" and "modify sub-step 3d" but doesn't provide the actual specification text.

**Approach 2 — RC: 0.95**: Covers all requirements. The only gap: the 3-test viability probe doesn't test behavioral adherence (acknowledged in debate). Implementation spec, error handling, return contract changes, sprint-spec mapping all fully specified.

**Approach 2 — IC: 0.92**: Minor inconsistency: Section 7 (R-NEW-3) estimates SKILL.md at ~45K tokens, but Section 2.3 budgets standard at $2.00 which may be insufficient for 45K input + pipeline work. Not a contradiction but a tension.

**Approach 3 — IC: 0.80**: Several internal tensions. The "first-class peer" philosophy conflicts with the quality gap acknowledgment (~95% vs ~85-90% fidelity). The `fallback_mode` field is simultaneously "deprecated" (Section 6) and "set to false for backward compatibility." The SKILL.md extraction logic for Path B is described but not specified (which lines map to which steps).

**Approach 3 — SR: 0.75**: The YAML-based specification style is detailed but not directly implementable (it's a design document, not specification text). Compare Approach 2's Section 5 (copy-paste-ready specification text) with Approach 3's Section 4 (YAML pseudocode requiring translation).

---

## Layer 2: Qualitative Scoring (50% weight)

### 25-Criterion Binary Rubric

**5 Dimensions × 5 Criteria = 25 criteria**

#### Dimension 1: Completeness (5 criteria)

| # | Criterion | Ap1 | Ap2 | Ap3 | Evidence |
|---|-----------|-----|-----|-----|----------|
| 1 | Specifies the headless command template | NOT MET | MET | MET | Ap1 has no command template. Ap2 §2.2. Ap3 §3 command construction. |
| 2 | Specifies error handling for all failure modes | MET | MET | MET | Ap1 §T13. Ap2 §2.6 (8-row matrix). Ap3 §3 output handling. |
| 3 | Specifies fallback protocol | NOT MET | MET | MET | Ap1 defers to existing sprint-spec. Ap2 §5 step 3d-iv. Ap3 §4 full F1-F5. |
| 4 | Specifies return contract changes | NOT MET | MET | MET | Ap1 has schema only (Appendix B). Ap2 §3 Task 3.1-3.3. Ap3 §5 Epic 3. |
| 5 | Specifies verification tests | MET | MET | MET | Ap1 §2 (13 tests). Ap2 §7 (3 tests). Ap3 §8 (6 tests). |

**Scores**: Ap1: 2/5, Ap2: 5/5, Ap3: 5/5

#### Dimension 2: Correctness (5 criteria)

| # | Criterion | Ap1 | Ap2 | Ap3 | Evidence |
|---|-----------|-----|-----|-----|----------|
| 6 | Correctly addresses Issue #837 (slash commands in -p) | MET | MET | MET | All avoid direct slash command invocation as primary. |
| 7 | Correctly addresses Issue #1048 (behavioral drift) | MET | NOT MET | NOT MET | Ap1 T05 rubric measures adherence. Ap2/Ap3 probe mechanics only. |
| 8 | Return contract schema is valid YAML | MET | MET | MET | All specify valid schema. |
| 9 | Fallback produces usable output | N/A | MET | MET | Ap1 doesn't specify fallback. Ap2 retains existing. Ap3 upgrades to 5-step. |
| 10 | Cost estimates are realistic | MET | MET | MET | Ap1: $25-35 probe. Ap2: $2-5 pipeline. Ap3: comparable to Ap2. |

**Scores**: Ap1: 3/4 (N/A excluded), Ap2: 4/5, Ap3: 4/5

#### Dimension 3: Structure (5 criteria)

| # | Criterion | Ap1 | Ap2 | Ap3 | Evidence |
|---|-----------|-----|-----|-----|----------|
| 11 | Clear section hierarchy | MET | MET | MET | All well-organized. |
| 12 | Sprint-spec modification table | NOT MET | MET | NOT MET | Only Ap2 §8 provides a modification table. Ap3 has inline YAML. |
| 13 | Implementation-ready specification text | NOT MET | MET | NOT MET | Ap2 §5 is copy-paste ready. Ap1/Ap3 require translation. |
| 14 | Risk register with probability/impact | MET | MET | MET | Ap1 §6 (7 risks). Ap2 §6 (6 risks). Ap3 §7 (6 risks). |
| 15 | Verification plan with pass/fail criteria | MET | MET | MET | All specify verification tests with criteria. |

**Scores**: Ap1: 3/5, Ap2: 5/5, Ap3: 3/5

#### Dimension 4: Clarity (5 criteria)

| # | Criterion | Ap1 | Ap2 | Ap3 | Evidence |
|---|-----------|-----|-----|-----|----------|
| 16 | Single clear recommendation | MET | MET | MET | Ap1: "probe first." Ap2: "claude -p primary." Ap3: "dual-path." |
| 17 | Unambiguous decision criteria | MET | MET | MET | All specify decision gates/criteria. |
| 18 | No jargon without definition | MET | MET | MET | All define terms (S1/S2/S3, Path A/B, etc.). |
| 19 | Command examples are copy-executable | MET | MET | NOT MET | Ap1 T01-T04 are bash. Ap2 §2.2 is bash. Ap3 uses YAML pseudocode. |
| 20 | Scope is self-contained (no external dependencies for understanding) | NOT MET | MET | MET | Ap1 defers implementation to "after probe." Ap2/Ap3 are self-contained. |

**Scores**: Ap1: 4/5, Ap2: 5/5, Ap3: 4/5

#### Dimension 5: Risk Coverage (5 criteria)

| # | Criterion | Ap1 | Ap2 | Ap3 | Evidence |
|---|-----------|-----|-----|-----|----------|
| 21 | Addresses environment portability | MET | MET | MET | Ap1 T01/Risk F. Ap2 R-NEW-5. Ap3 philosophy §1. |
| 22 | Addresses cost control | MET | MET | MET | Ap1 T10. Ap2 §2.3 budget mapping. Ap3 §3 budget table. |
| 23 | Addresses context window limits | MET | MET | MET | Ap1 T12. Ap2 R-NEW-3. Ap3 R6. |
| 24 | Addresses behavioral instruction drift | MET | NOT MET | NOT MET | Only Ap1 T05/T07 measure adherence. Ap2/Ap3 don't test for this. |
| 25 | Addresses mid-pipeline failure | NOT MET | NOT MET | MET | Only Ap3 §3 "Mid-Pipeline Fallover" addresses this. |

**Scores**: Ap1: 4/5, Ap2: 3/5, Ap3: 4/5

### Qualitative Summary

| Dimension | Ap1 | Ap2 | Ap3 |
|-----------|-----|-----|-----|
| Completeness | 2/5 | 5/5 | 5/5 |
| Correctness | 3/4 | 4/5 | 4/5 |
| Structure | 3/5 | 5/5 | 3/5 |
| Clarity | 4/5 | 5/5 | 4/5 |
| Risk Coverage | 4/5 | 3/5 | 4/5 |
| **Total** | **16/24** | **22/25** | **20/25** |
| **Normalized** | **0.667** | **0.880** | **0.800** |

---

## Combined Score

| Approach | Quantitative (50%) | Qualitative (50%) | **Combined** |
|----------|--------------------|--------------------|--------------|
| Approach 1 | 0.670 × 0.50 = 0.335 | 0.667 × 0.50 = 0.334 | **0.669** |
| Approach 2 | 0.924 × 0.50 = 0.462 | 0.880 × 0.50 = 0.440 | **0.902** |
| Approach 3 | 0.843 × 0.50 = 0.422 | 0.800 × 0.50 = 0.400 | **0.822** |

---

## Position-Bias Mitigation (Pass 2: Reverse Order)

Scoring in reverse order (Ap3, Ap2, Ap1) to check for position bias:

| Approach | Pass 1 | Pass 2 | Delta | Resolution |
|----------|--------|--------|-------|------------|
| Approach 1 | 0.669 | 0.665 | -0.004 | Consistent. No bias detected. |
| Approach 2 | 0.902 | 0.898 | -0.004 | Consistent. No bias detected. |
| Approach 3 | 0.822 | 0.828 | +0.006 | Consistent. No bias detected. |

**Final Combined Scores (average of both passes)**:
- **Approach 1: 0.667**
- **Approach 2: 0.900**
- **Approach 3: 0.825**

Top two gap: 0.900 - 0.825 = 0.075 > 5%. No tiebreaker needed.
