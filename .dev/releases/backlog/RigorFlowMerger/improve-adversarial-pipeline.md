---
component: adversarial-pipeline
deliverable: D-0026
source_comparison: comparison-adversarial-pipeline.md
verdict: IC stronger
principle_primary: Scalable Quality Enforcement
principle_secondary: Evidence Integrity
generated: 2026-03-15
---

# Improvement Plan: Adversarial Pipeline

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM AP-001 — Ambient Sycophancy Detection in Agent Definitions

**Priority**: P0
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's 12-category sycophancy risk taxonomy with non-linear multipliers as a lightweight Tier 1 check embedded in agent definitions, not LW's static weight system without adaptive learning
**Why not full import**: LW's full anti-sycophancy system uses static pattern weights without adaptive learning (explicitly rejected in D-0022 Principle 4) and is implemented as a standalone behavioral system outside agent definitions; IC needs only the taxonomy and response routing embedded as behavioral NFRs in existing agent .md files, not a new standalone component.

**File paths and change description**:
- `.claude/agents/quality-engineer.md` — Add a "Sycophancy Detection NFR" section with: the 12-category taxonomy (immediate agreement, validation seeking, context abandonment, etc.) and the non-linear multiplier rule (1.0× for 1 pattern, 1.3× for 2 patterns, 1.5× for 3+ patterns). Add the four-tier response routing: score < 1.0 → standard response; 1.0–1.3 → explicitly present trade-offs; 1.3–1.5 → escalate to adversarial check; > 1.5 → challenge the premise.
- `src/superclaude/agents/quality-engineer.md` — Sync copy.
- `.claude/agents/self-review.md` — Add the same Sycophancy Detection NFR section (self-review agent is the most susceptible to sycophantic affirmations of the implementer's own work).
- `src/superclaude/agents/self-review.md` — Sync copy.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 2: "IC should adopt this taxonomy as a lightweight Tier 1 check embedded in agent definitions (not requiring explicit invocation), with the four-tier response routing applied proportionally to the risk score."

**Dependencies**: None
**Acceptance criteria**: quality-engineer.md and self-review.md both contain a "Sycophancy Detection NFR" section with the 12-category taxonomy and four-tier response routing; dev copies are synced; section is not a stub (contains actionable instructions).
**Risk**: Low. Agent instruction additions; no code changes; behavioral improvement in agent output quality.

---

## ITEM AP-002 — CEV Vocabulary Extension to All Verification Outputs

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting IC's own CEV (Claim-Evidence-Verdict) vocabulary from the adversarial pipeline as a cross-component standard for all qualitative claims in verification outputs
**Why not full import**: This is IC-native extension, not LW adoption. No LW mass is imported. The pattern is extracted from the adversarial pipeline's own output format and applied to other IC verification contexts.

**File paths and change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — Add to the STRICT tier execution instructions: "All qualitative claims in verification outputs must cite specific evidence (file:line or artifact reference). Format: [CLAIM] — [EVIDENCE:file:line] — [VERDICT: confirmed|rejected|inconclusive]."
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — Sync copy.
- `.claude/agents/quality-engineer.md` — Add to the output format requirements: "Use CEV (Claim-Evidence-Verdict) structure for all qualitative findings: state the claim, provide the evidence citation, state the verdict."

**Rationale**: D-0022 Principle 1 (Evidence Integrity), direction 4: "Extend [CEV vocabulary] to the IC framework as a whole: all qualitative claims in verification outputs should cite specific evidence (file:line or artifact reference)."

**Dependencies**: AP-001 (sycophancy detection ensures the CEV structure is not used sycophantically to validate without challenge)
**Acceptance criteria**: sc-task-unified-protocol/SKILL.md contains CEV format requirement in STRICT tier instructions; quality-engineer.md contains CEV output format requirement; at least one example of CEV format is shown in each file.
**Risk**: Low. Instruction additions; no structural code changes.

---

## ITEM AP-003 — Four-Category Failure Classification in Adversarial Debate Outputs

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's 4-category failure classification taxonomy (execution failures, template failures, evidence failures, workflow failures) as a classification layer for adversarial debate failure modes, not LW's point-based scoring with confidence tiers
**Why not full import**: LW's full failure classification uses a confidence scoring system (High ≥5 pts, Medium 3-4, Low ≤2) tied to its batch execution model; IC's adversarial pipeline needs only the four-category taxonomy as a structural classifier for debate outputs, without point scoring.

**File paths and change description**:
- `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` — Add a "Failure Mode Classification" section with the four categories: (1) Execution failures (model refused, output truncated, agent timeout), (2) Template failures (output does not match artifact schema), (3) Evidence failures (claims without file:line citations, CEV violations), (4) Workflow failures (pipeline stage skipped, convergence plateau not detected). When a debate round produces an artifact with failures, classify each failure before scoring.
- `src/superclaude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` — Sync copy.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 4: "Adopting this taxonomy allows IC to produce scored, categorized failure reports that are actionable and comparable across runs."

**Dependencies**: AP-002 (CEV structure establishes what an evidence failure looks like)
**Acceptance criteria**: scoring-protocol.md has a "Failure Mode Classification" section with all four categories; each category has at least one example; dev copy is synced.
**Risk**: Low. Document addition to existing scoring protocol; no structural change to the scoring algorithm.
