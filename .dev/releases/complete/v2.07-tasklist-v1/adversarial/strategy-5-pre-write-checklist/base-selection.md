# Base Selection — Strategy 5: Pre-Write Structural Validation Checklist

**Pipeline Step**: 3 of 5
**Date**: 2026-03-04
**Method**: Hybrid quantitative-qualitative scoring with position-bias mitigation
**Decision options evaluated**: A (Adopt as-is), B (Adopt with modifications), C (Reject)

---

## 1. Quantitative Metrics

Scoring each option across five weighted dimensions. Scale: 0–10. Weight column sums to 100%.

| Dimension | Weight | Option A: Adopt as-is | Option B: Adopt modified | Option C: Reject |
|---|---|---|---|---|
| Correctness impact (closes real gaps) | 30% | 6 | 9 | 0 |
| Spec maintainability (no dual-maintenance) | 20% | 3 | 9 | 10 |
| Parity constraint compliance | 25% | 4 | 9 | 10 |
| Implementation complexity (lower = better) | 15% | 3 | 7 | 10 |
| CI-testability of output | 10% | 7 | 9 | 4 |

**Weighted scores:**

- **Option A**: (6×0.30) + (3×0.20) + (4×0.25) + (3×0.15) + (7×0.10) = 1.80 + 0.60 + 1.00 + 0.45 + 0.70 = **4.55**
- **Option B**: (9×0.30) + (9×0.20) + (9×0.25) + (7×0.15) + (9×0.10) = 2.70 + 1.80 + 2.25 + 1.05 + 0.90 = **8.70**
- **Option C**: (0×0.30) + (10×0.20) + (10×0.25) + (10×0.15) + (4×0.10) = 0 + 2.00 + 2.50 + 1.50 + 0.40 = **6.40**

### Evidence for scoring

**Option A (Adopt as-is) — 4.55:**
- Correctness: 6/10 — closes some gaps but 4/5 integration-strategies checks are §8 duplicates, so real correctness gain is diluted
- Maintainability: 3/10 — creates dual-maintenance obligation; 4 checks exist in two places
- Parity: 4/10 — taskbuilder semantic checks include behavioral constraints (XL splitting, count bounds) that change generator behavior
- Complexity: 3/10 — full 13-check §7.5 adds significant prompt complexity
- CI-testability: 7/10 — named section provides clear contract

**Option B (Adopt modified) — 8.70:**
- Correctness: 9/10 — closes all genuine gaps (metadata completeness, Deliverable ID uniqueness, non-empty descriptions) without dilution
- Maintainability: 9/10 — no duplication; net-new checks only, cross-references §8 for structural checks
- Parity: 9/10 — scoped to pure validation with no behavioral generation changes
- Complexity: 7/10 — 3–4 new checks rather than 13; manageable prompt overhead
- CI-testability: 9/10 — named or inline section still provides clear contract

**Option C (Reject) — 6.40:**
- Correctness: 0/10 — known gaps (metadata completeness, D-### uniqueness) remain open
- Maintainability: 10/10 — no new maintenance surface
- Parity: 10/10 — no changes
- Complexity: 10/10 — no added complexity
- CI-testability: 4/10 — existing §8 testability only; semantic quality gaps persist

---

## 2. Qualitative Rubric (CEV Protocol)

Evaluated by examining evidence from spec documents and debate transcript.

### 2.1 Strategic fit with v1.0 goals

The v1.0 PRD (§2 Goal item 5) states: "Achieves exact functional parity with the current v3.0 generator — no new features." The PRD Acceptance Criterion 7 states: "Functional parity: output is identical to running the v3.0 generator prompt manually."

**Finding**: Validation rules that prevent already-invalid output from reaching disk do not change what the generator WOULD produce for a valid roadmap — they only gate invalid outputs. The parity constraint applies to output specification, not to internal validation behavior. Modified Strategy 5 (Option B) is within parity scope.

**Finding**: Behavioral generation constraints (auto-splitting XL tasks, rejecting phases with >25 tasks) DO change output for edge-case roadmaps. These are out of parity scope.

### 2.2 Value of genuinely new checks

Three checks not present anywhere in v3.0:
1. **Metadata/tier field completeness**: High value. A task with empty Tier assignment passes all §8 checks today but will fail Sprint CLI execution. This is a Sprint compatibility gap disguised as a structural issue.
2. **Deliverable ID global uniqueness**: Medium-high value. Duplicate D-### assignments corrupt the Traceability Matrix and Deliverable Registry silently. No existing check catches this.
3. **Non-empty task descriptions**: Medium value. The §8 check for "no empty shells" exists implicitly (a task without description cannot satisfy §6B format), but making it explicit closes a loophole.

### 2.3 Temporal positioning (pre-write vs. post-generation)

The debate established that the temporal distinction only provides benefit if the generator uses incremental writes. The v3.0 spec does not specify write atomicity. However, explicitly declaring atomic write semantics is a zero-cost clarification that makes the temporal positioning unambiguous and prevents future misinterpretation by an incremental-write implementation.

**Finding**: The temporal positioning claim is worth preserving through an atomic-write declaration, even if current LLM execution makes it a no-op. It becomes binding specification for future implementations.

### 2.4 Risk of rejection

Rejecting Strategy 5 entirely leaves three confirmed gaps open:
- Metadata field completeness (not checked anywhere)
- Deliverable ID uniqueness (not checked anywhere)
- Non-empty description enforcement (implicit only)

These gaps are not theoretical — they are the class of errors most likely to produce Sprint CLI failures that pass all current validation checks. Rejection would require explicitly documenting these as known gaps and deferring them to v1.1, which is a worse outcome than a lightweight extension.

---

## 3. Combined Scoring

| Option | Quantitative | Qualitative Weight | Combined |
|---|---|---|---|
| A: Adopt as-is | 4.55 | Below acceptable (parity violation risk, dual-maintenance) | **Not selected** |
| B: Adopt modified | 8.70 | Strongly positive (closes real gaps, within parity scope, maintainable) | **Selected** |
| C: Reject | 6.40 | Neutral-negative (leaves confirmed gaps open, degrades test coverage) | **Not selected** |

---

## 4. Selection Decision

**Decision: MODIFY — Adopt Strategy 5 with the following constraints.**

### 4.1 What to include (net-new checks only)

Add the following checks to §8 Sprint Compatibility Self-Check as items 9–12 (OR as a named subsection §8.1 "Semantic Quality Gate" within §8):

**Check 9**: Every task in every phase file has non-empty Effort, Risk, Tier, and Confidence fields.
**Check 10**: All Deliverable IDs (D-####) are globally unique across the entire bundle (no duplicates across phases).
**Check 11**: No task has an empty or placeholder description (no "TBD", no title-only entries).
**Check 12**: Every task has at least one `R-###` Roadmap Item ID assigned (no orphan tasks).

Plus a one-sentence atomic write declaration in §6 or §9: "The generator validates the complete in-memory bundle against §8 before issuing any Write() calls."

### 4.2 What to exclude (out of parity scope)

- ≤25 tasks per phase constraint (behavioral; changes output for dense roadmaps)
- XL task splitting enforcement at validation time (behavioral; changes output)
- Circular dependency auto-detection and fix (behavioral; changes generation algorithm)
- Confidence bar format consistency check (formatting-only; low impact, adds complexity)
- Phase count ≤N bounds (covered by §8 structural checks already)

### 4.3 What to avoid (duplication prevention)

Do NOT restate in the new checks what §8 already verifies:
- Index existence with "Phase Files" table → §8 check 1
- Every referenced phase file generated → §8 check 2
- Phase numbering contiguity → §8 check 3
- Task ID format `T<PP>.<TT>` → §8 check 4
- Phase heading format → §8 check 5
- End-of-phase checkpoint → §8 check 6
- No forbidden sections → §8 check 7
- Literal filenames in index → §8 check 8

### 4.4 Placement decision

Placement: Extend §8 Sprint Compatibility Self-Check rather than creating a new §7.5.

Rationale:
- §8 is already the "validate before emit" gate in the spec
- Extending §8 avoids the ambiguity of two separate fix-before-proceed gates
- Option B's maintainability score (9/10) assumes no duplication; §8 extension achieves this
- A named subsection within §8 (e.g., `### 8.1 Semantic Quality Gate`) provides CI-testability signal without creating a parallel gate

