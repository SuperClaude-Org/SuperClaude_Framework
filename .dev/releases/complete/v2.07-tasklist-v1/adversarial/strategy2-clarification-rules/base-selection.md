# Base Selection & Scoring — Strategy 2: Single-Pass Clarification Rules

**Adversarial Pipeline Step 3**
**Date**: 2026-03-04

---

## 1. Deliverable Mapping

The user's six deliverables map to this adversarial pipeline as follows:

| Deliverable | Pipeline Artifact |
|-------------|-------------------|
| 1) Strongest arguments FOR | debate-transcript.md §Round 1 FOR (F1-F4) |
| 2) Strongest arguments AGAINST / risks | debate-transcript.md §Round 1 AGAINST (A1-A4) |
| 3) Compatibility with v1.0 parity constraint | This document §2 |
| 4) Final adjudication | This document §3 |
| 5) Refactored strategy text | refactor-plan.md |
| 6) Specific spec patch locations/wording | refactor-plan.md §4 |

---

## 2. Compatibility Assessment: v1.0 Parity Constraint

### 2.1 Parity constraint definition (from spec)

From §2 Goal item 5: "Achieves **exact functional parity** with the current v3.0 generator — no new features."
From §9 Acceptance Criteria item 7: "Functional parity: output is identical to running the v3.0 generator prompt manually."

### 2.2 Scope of parity

The parity constraint is scoped to **generator output**: the tasklist bundle produced when inputs are valid. This is confirmed by:
- The phrase "output is identical" — the constraint is on the artifact content
- The non-goals list explicitly scopes out interactive mode and new features in the generator
- §2 Goal item 4: "Replaces the manual `TasklistGenPrompt.md` workflow" — the workflow being replaced is the generation workflow, not the error-handling workflow

### 2.3 Does Strategy 2 violate parity?

**No.** Strategy 2 operates exclusively at the validation pre-flight layer (command layer, before the skill is invoked). When inputs are valid, the behavior is byte-for-byte identical to the current spec. Strategy 2 only changes behavior on invalid inputs — and the current spec has no defined behavior on invalid inputs. Specifying undefined behavior is not a parity violation.

**One edge case**: If the current v3.0 manual workflow produces some error output on invalid inputs, and that output format is considered "parity-relevant," then specifying a different format could be a parity issue. However:
- The v3.0 manual workflow is a prompt, not a CLI — it has no defined error format
- Error messages are LLM-generated free text in the manual workflow, which varies between runs
- Deterministic structured errors are strictly better and do not violate the "identical output on valid inputs" parity criterion

**Verdict**: Compatible with v1.0 parity constraint. Score: 10/10.

---

## 3. Quantitative Scoring

### 3.1 Scoring dimensions

| Dimension | Weight | Score (0-10) | Weighted |
|-----------|--------|-------------|---------|
| Architectural compatibility | 25% | 10 | 2.50 |
| Parity constraint compliance | 25% | 10 | 2.50 |
| Implementation risk (inverse) | 20% | 6 | 1.20 |
| Operational value (CI/automation) | 15% | 8 | 1.20 |
| Specification completeness (as-written) | 15% | 4 | 0.60 |
| **TOTAL** | 100% | — | **8.00/10** |

### 3.2 Scoring rationale

**Architectural compatibility (10/10)**: Strategy 2 touches only §5.4 and §5.6 Boundaries. It does not touch the skill, templates, self-check, or any output-generating section. Zero architectural conflict.

**Parity constraint compliance (10/10)**: As established in §2.3, parity is scoped to valid-input output. Strategy 2 does not affect valid-input output.

**Implementation risk (6/10)**: The as-written strategy text is underspecified on fallback scope and error format. These are concrete fixable risks but not fatal ones. Score reflects the raw strategy text before tightening.

**Operational value (8/10)**: Structured errors and explicit fail-fast are high-value for CI consumers. The value is real but not critical-path for v1.0 launch (the tool works on valid inputs regardless).

**Specification completeness as-written (4/10)**: The proposed spec text ("One-pass resolution for ambiguous path/state") is too vague to implement deterministically without interpretation. Two implementers would produce different results.

---

## 4. Qualitative Assessment (CEV Protocol)

**Counterfactual**: If Strategy 2 is not adopted, what is the cost?

- CI integration will encounter variable, unstructured error output
- Operators cannot reliably parse failure reasons from automation logs
- The spec will have an undefined-behavior gap at the validation layer
- Future implementers will fill this gap ad hoc, producing inconsistency

**Evidential weight**: The pipeline PRD (FR-3, Non-Functional §"Reliability: fail-fast on invalid contracts") already mandates fail-fast behavior at the pipeline level. Strategy 2 at the command layer is consistent with this requirement — it would be anomalous for the pipeline to require fail-fast at the compiler/execution level but leave the command validation layer unspecified.

**Value alignment**: The spec's target persona is developers using CI automation (evidenced by sprint CLI integration focus). Structured error output is a basic expectation of CLI tools in CI contexts.

---

## 5. Tiebreaker Protocol

No tiebreaker needed. Score is 8.00/10 with clear adopt recommendation subject to tightening conditions identified in the debate.

---

## 6. Base Selection Result

**Decision: ADOPT with mandatory modifications**

The strategy's core value (explicit fail-fast + structured error) is sound, architecturally compatible, and parity-safe. The as-written spec text is insufficient for deterministic implementation. Adoption is conditioned on the two tightening requirements from the debate:

1. Restrict one-pass fallback to TASKLIST_ROOT derivation case only
2. Specify concrete, deterministic error format in §5.4

These modifications do not change the strategy's intent — they make it implementable.
