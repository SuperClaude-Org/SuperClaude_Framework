# Step 3: Base Selection + Scoring — Strategy 1: Stage-Gated Generation Contract

**Date**: 2026-03-04
**Purpose**: Score Strategy 1 on quantitative metrics and qualitative rubric; produce adjudication decision.

---

## Quantitative Metrics

### Q1 — Spec Delta Size
**Metric**: Lines of spec change required
**Measurement**:
- §6.2: 1 required sentence + 1 clarification note = ~4 lines
- §4.3: Canonicalize 6-stage names, annotate 8-step list = ~12 lines
- §9: Update 1 criterion + add 1 criterion = ~4 lines
- Total: approximately 20 lines net addition
**Score**: 9/10 (minimal footprint for the reliability gain achieved)

### Q2 — Surface Area Risk
**Metric**: Number of spec sections modified
**Measurement**: §4.3, §6.2, §9 — three sections touched
**Score**: 8/10 (well-contained; command layer, §8 self-check, and all output schemas untouched)

### Q3 — Breaking Change Index
**Metric**: Does this change alter the command contract, output schema, or installation behavior?
**Measurement**:
- Command contract (`tasklist.md`): NOT modified
- Output schema (task format, file names, ID conventions): NOT modified
- Installation behavior (lint-architecture checks): NOT modified
- Behavioral change: yes — adds stage validation semantics to skill execution
- Parity delta: skill adds reliability semantics not in v3.0 generator
**Score**: 7/10 (non-breaking on external contracts; internal behavioral addition only)

### Q4 — Testability
**Metric**: Can acceptance criteria be verified without running the full generator?
**Measurement**:
- "Each stage must complete and validate before advancing" — verifiable via SKILL.md review
- "Generation reports completed stages in order" — verifiable via TodoWrite usage review
- "Halts on failed stage validation" — verifiable only at runtime by injecting a bad input
- Per-stage validation criteria (when added per M2) — static verification possible
**Score**: 6/10 (partially testable statically; runtime behavior requires integration test)

### Q5 — Alignment with PRD Requirements
**Metric**: How many PRD functional requirements does this satisfy or strengthen?
**Measurement**:
- FR-3 (Deterministic Rebuild): Stage gates enforce consistent intermediate states — direct alignment
- FR-5 (Handoff Contract): Stage gates enforce contract field completeness per stage — indirect alignment
- §13 Risks: "Partial artifact inconsistencies" risk — stage gates directly mitigate this
- §13 Risks: "Compiler introduces new failure point" — stage gates improve failure isolation
**Score**: 8/10 (strong PRD alignment on determinism and reliability requirements)

**Quantitative Total**: (9 + 8 + 7 + 6 + 8) / 5 = **7.6 / 10**

---

## Qualitative Rubric

### R1 — Problem-Solution Fit
**Assessment**: The problem (no stage-boundary protection, post-hoc error detection) is real and well-evidenced in the diff analysis. The solution (stage gates before advancement, halt on failure) directly addresses the problem mechanism, not just its symptoms.
**Score**: HIGH

### R2 — Proportionality
**Assessment**: The proposed fix is proportionate to the problem. A 20-line spec addition that converts implicit pipeline ordering into an explicit reliability contract is not over-engineered. The alternative (post-hoc detection only) is under-engineered for a skill used in automated sprint workflows.
**Score**: HIGH

### R3 — Reversibility
**Assessment**: Fully reversible. The spec change is additive (strengthening language). The output schema is unchanged. If the stage gates prove unworkable in practice (e.g., LLMs consistently ignore them), the language can be removed without affecting any other part of the spec.
**Score**: HIGH

### R4 — Implementation Clarity
**Assessment**: Currently MEDIUM. The strategy as originally proposed does not define per-stage validation criteria. With modification M2 (add per-stage validation criteria table), this becomes HIGH. Without M2, implementers have no guidance on what constitutes a valid Stage 2 vs. a valid Stage 4 output.
**Score**: MEDIUM (upgrades to HIGH upon M2 adoption)

### R5 — v1.0 Parity Compatibility
**Assessment**: The parity constraint requires "no new features beyond what v3.0 already does." Stage gates are not a feature — they are an execution reliability mechanism that does not alter what tasks are generated, how they are structured, or what files are emitted. The v3.0 algorithm's logic is preserved. The difference is that failures now halt rather than propagating. With parity clarification note M4, this is fully compatible.
**Score**: MEDIUM-HIGH (MEDIUM without M4 clarification, HIGH with it)

### R6 — Sprint Automation Compatibility
**Assessment**: Stage reporting via TodoWrite is already in the tool usage table (§6.4). Stage gates align with Sprint CLI's fail-fast philosophy. No sprint runtime changes required. The command/skill boundary is fully preserved.
**Score**: HIGH

**Qualitative Summary**: 5x HIGH, 1x MEDIUM (upgrades to HIGH with M2). No LOW scores.

---

## Combined Scoring

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|---------|
| Quantitative average | 7.6/10 | 40% | 3.04 |
| Qualitative (5 HIGH, 1 MEDIUM = 8.3/10) | 8.3/10 | 60% | 4.98 |
| **Combined** | | | **8.02 / 10** |

**Threshold for adoption**: 7.0 (ADOPT), 5.0-6.9 (MODIFY-FIRST), below 5.0 (REJECT)

**Result**: 8.02 — ADOPT with modifications

---

## Tiebreaker Protocol

Tiebreaker not required. Score 8.02 is above adoption threshold with no significant disqualifying factors.

---

## Selection Rationale

Strategy 1 is a high-confidence adoption. The quantitative score (7.6) reflects the minor implementation-clarity gap (R4 MEDIUM, resolved by M2). The qualitative score (8.3) reflects strong problem-solution fit, proportionality, and reversibility.

The debate produced 5 required modifications (M1-M5). These are not reasons to defer adoption — they are implementation requirements that make the strategy production-ready. The modifications are low-effort and have no dependencies on other strategies.

**Critical dependency**: M2 (per-stage validation criteria table) is a required condition for adoption. The strategy must not be merged into the spec without it.

---

## Adjudication Decision

**ADOPT with modifications M1, M2, M3, M4, M5**

M2 is a hard condition. M1, M3, M5 are required. M4 is recommended.
