# Base Selection & Adjudication — Strategy 3: Self-Contained Task Item Quality Gate

**Pipeline**: sc:adversarial — Step 3 of 5
**Date**: 2026-03-04

---

## 1. Quantitative Scoring

### 1.1 Scoring Dimensions (0-10 per dimension)

| Dimension | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| Problem validity | 15% | 9 | Both advocates converged: the Sprint CLI session-rollover failure mode is real, documented, and high-impact |
| Parity constraint compatibility | 25% | 5 | Central dispute: §7 rule changes generator output content; literal parity reads as content-identical; spirit reads as schema-identical |
| Enforcement completeness | 20% | 3 | As written (§7 + §9 only), has zero enforcement mechanism. §8 gate absent. Acceptance criterion is not CI-verifiable |
| Operationalization quality | 15% | 4 | "Standalone and action-oriented (explicit artifact/target)" is partially defined but lacks rubric, examples, or measurable criteria |
| Sprint CLI benefit | 15% | 8 | High benefit if enforced: session-rollover safety, delegation safety, async execution reliability |
| Implementation cost | 10% | 9 | Minimal: one §7 sentence, one §9 sentence, zero schema changes |

### 1.2 Weighted Score Calculation

| Dimension | Weight | Score | Contribution |
|-----------|--------|-------|-------------|
| Problem validity | 0.15 | 9 | 1.35 |
| Parity compatibility | 0.25 | 5 | 1.25 |
| Enforcement completeness | 0.20 | 3 | 0.60 |
| Operationalization | 0.15 | 4 | 0.60 |
| Sprint CLI benefit | 0.15 | 8 | 1.20 |
| Implementation cost | 0.10 | 9 | 0.90 |
| **Total** | 1.00 | — | **5.90 / 10** |

---

## 2. Qualitative Rubric Assessment

### 2.1 Does it solve a real problem?
**Yes, clearly.** The Sprint CLI automated execution model requires tasks to be self-interpreting units. Any task that requires session context to interpret is functionally incomplete for the stated deployment target. This is the strongest point for adoption.

### 2.2 Is it compatible with stated constraints?
**Partially, with conditions.** The v1.0 parity constraint ("output identical to v3.0 generator") is genuinely ambiguous. Read strictly: any generation rule that changes prose content breaks parity. Read functionally: a style rule that improves description quality without changing schema/structure/format is within scope.

The ambiguity is the primary risk. If the parity constraint is interpreted strictly by a future reviewer, Strategy 3 creates a spec-internal conflict. The safest interpretation: adopt Strategy 3 but explicitly note in the spec that the §7 rule may produce cosmetically different but structurally identical output versus v3.0, and that this is intentional.

### 2.3 Is the enforcement adequate?
**No, as written.** This is the decisive weakness. A generation rule without an enforcement gate is advisory. The Sprint Compatibility Self-Check (§8) must gain a corresponding check, or the §7 rule has no operational effect beyond hope that the generating LLM complies.

However, adding a §8 check for self-containment faces the verifiability problem: semantic self-containment cannot be tested by a structural parser. The practical resolution: the §8 check should be a generation-time assertion ("before emitting each task, verify it satisfies the §7.N standalone criterion") rather than a post-hoc parse-and-validate check.

### 2.4 Is the scope appropriate for v1.0?
**Yes, if held to the minimal interpretation.** The minimal interpretation (one §7 rule + one §9 criterion, no new fields, no schema change) is within v1.0 scope. It is additive within existing sections. It does not require new command arguments, new output files, or installation changes.

The expanded interpretation (Proposal 1: `Context:`, `Verify:`, `Blocked-Until:` fields) is explicitly out of scope and should be deferred to v1.1.

---

## 3. Position-Bias Mitigation

The AGAINST position was more technically precise in identifying enforcement gaps and parity risks. The FOR position made the stronger case for problem importance and cost-benefit ratio. Neither advocate had a structural advantage. The key mediating insight is: **the debate is not about whether to adopt the principle — both advocates agree the principle is sound — but about whether the v1.0 spec is the right place to enforce it and whether the proposed text is adequate enforcement.**

---

## 4. Final Adjudication

### Verdict: MODIFY

Strategy 3 is adopted with mandatory modifications before it is implementation-ready.

**Rationale for not REJECT:**
- The problem it addresses is real, high-impact, and unaddressed elsewhere in the spec
- The minimal-scope interpretation is genuinely compatible with v1.0
- The implementation cost is low

**Rationale for not unconditional KEEP:**
- As written, it has zero enforcement mechanism
- "Standalone and action-oriented" is underspecified
- The parity constraint intersection is unresolved without a clarifying note

### Required Modifications for Adoption

**M1 — Operationalize "standalone"**: The §7 rule must define what "standalone" means with specific, measurable criteria. Proposed: a task is standalone if it (a) names the specific artifact or file it operates on, (b) contains enough context for an agent starting a fresh session to begin execution, and (c) does not use pronouns or references ("the above", "as discussed") that require prior conversation.

**M2 — Add §8 enforcement gate**: The Sprint Compatibility Self-Check must gain a corresponding check. Because semantic self-containment is not structurally parseable, the check is a generation-time assertion: "For each task, before emitting, confirm description satisfies §7.N standalone criteria." This makes the check part of generation discipline, not post-hoc validation.

**M3 — Clarify parity note**: Add an explicit note in the parity criterion (§9 criterion 7) or in §6.2 content mapping: "The §7.N standalone rule may produce cosmetically different task descriptions than a raw v3.0 run; this is intentional and within parity scope as it does not change schema, structure, or output file format."

**M4 — Defer schema expansion to v1.1**: Explicitly note in the integration strategies doc that Proposal 1's `Context:`, `Verify:`, `Blocked-Until:` fields are the full implementation of Strategy 3's principle and are targeted for v1.1. This prevents scope creep while preserving the roadmap.

---

## 5. Scoring Summary

| Metric | Value |
|--------|-------|
| Raw weighted score | 5.90 / 10 |
| Debate convergence (post-round 2) | 62% |
| Verdict | MODIFY |
| Confidence in verdict | 82% |
| Key condition | Modifications M1-M4 must be included |
| v1.0 compatibility (modified) | Yes |
| Deferred to v1.1 | Schema expansion (Proposal 1 fields) |
