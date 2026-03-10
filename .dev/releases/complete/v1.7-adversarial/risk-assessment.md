# v1.7 sc:adversarial — Risk Assessment & Mitigation Strategy

## Risk Matrix

### Probability × Impact Scoring
- **Probability**: Low (10-30%) | Medium (30-60%) | High (60-90%)
- **Impact**: Low (workaround exists) | Medium (delays milestone) | High (blocks release)
- **Risk Score**: P×I → Low-Low=1 | Med-Med=4 | High-High=9

---

## Technical Risks

### R1: Sycophantic Convergence [Score: 6 — Medium-High]
- **Probability**: Medium (40-50%)
- **Impact**: High — defeats the purpose of adversarial debate
- **Description**: Advocate agents agree too quickly or superficially, producing debates that lack genuine adversarial pressure. Research confirms LLMs exhibit sycophantic agreement, especially same-model debates.
- **Milestone**: M2 (Adversarial Debate Protocol)
- **Mitigation**:
  1. Steelman protocol: advocates must construct strongest version of opposing positions before critiquing
  2. Explicit "maintain distinct positions" meta-prompt in advocate instructions
  3. Longer advocate prompts (research shows longer prompts encourage "stubbornness")
  4. Different personas per advocate to create genuine perspective diversity
  5. Convergence detection catches premature agreement (<10% diff → skip debate entirely)
- **Contingency**: If same-model sycophancy persists, recommend users specify different models per advocate (multi-model debate architecture)
- **Detection**: Monitor Round 1 agreement rate — if >90% agreement on first round, flag as potential sycophancy

### R2: Quantitative Metrics Inconsistency [Score: 4 — Medium]
- **Probability**: Medium (40%)
- **Impact**: Medium — undermines scoring credibility
- **Description**: The 5 quantitative metrics (RC, IC, SR, DC, SC) require text analysis that may produce different results on different artifact types (specs vs. roadmaps vs. code). Vague/concrete statement classification (SR) is particularly subjective.
- **Milestone**: M3 (Hybrid Scoring)
- **Mitigation**:
  1. Calibrate metrics against test corpus of 3+ artifact types during M3 development
  2. Use deterministic grep/regex patterns for quantitative layer (no LLM judgment)
  3. Normalize all metrics to [0.0, 1.0] with explicit formulas
  4. Log raw counts alongside normalized scores for debuggability
- **Contingency**: If metrics prove unreliable for certain artifact types, allow per-type weight overrides via future `--rubric` flag
- **Detection**: Run scoring twice on same inputs — quantitative scores must be bit-identical

### R3: Merge Execution Corruption [Score: 3 — Low-High]
- **Probability**: Low (20%)
- **Impact**: High — produces unusable output
- **Description**: The merge executor may produce structurally broken output when integrating changes from non-base variants into the base, especially with complex cross-section dependencies.
- **Milestone**: M4 (Merge Execution)
- **Mitigation**:
  1. Post-merge structural validation (headings, internal references, section completeness)
  2. All original variants preserved in adversarial/ directory — manual recovery always possible
  3. merge-log.md documents each applied change for rollback tracing
  4. Dedicated merge-executor agent with strong writing model (opus/sonnet)
- **Contingency**: If merge fails validation, return refactor-plan.md as output with status "partial" — user can execute plan manually
- **Detection**: Post-merge consistency check catches structural breaks automatically

### R4: Rate Limits / Timeouts on Parallel Dispatch [Score: 2 — Medium-Low]
- **Probability**: Medium (35%)
- **Impact**: Low — delays but doesn't block
- **Description**: Parallel advocate dispatch (M2) and variant generation (M5) may hit API rate limits when spawning 5-10 concurrent agents.
- **Milestone**: M2, M5
- **Mitigation**:
  1. Sequential fallback when parallel dispatch fails
  2. Retry logic with exponential backoff
  3. No cost constraints per spec — can afford retries
- **Contingency**: Reduce parallelism to batches of 3-4 agents instead of all-at-once
- **Detection**: Timeout monitoring on Task agent dispatch

### R5: Position-Bias Mitigation Overhead [Score: 2 — Low-Medium]
- **Probability**: Low (25%)
- **Impact**: Medium — doubles qualitative evaluation time
- **Description**: Running qualitative evaluation twice (forward + reverse order) per variant doubles the cost of M3. If many criteria disagree across passes, re-evaluation adds further cost.
- **Milestone**: M3
- **Mitigation**:
  1. Cap re-evaluations at 1 per criterion per variant
  2. Parallel execution of forward and reverse passes
  3. No cost constraints per spec
- **Contingency**: If disagreement rate exceeds 30%, log warning and use forward-pass scores only (with documented limitation)
- **Detection**: Track disagreement rate across dual passes

### R6: sc:roadmap v2 Contract Mismatch [Score: 2 — Low-Medium]
- **Probability**: Low (20%)
- **Impact**: Medium — requires rework of return contract
- **Description**: The return contract (FR-007) defined in the spec may not match what sc:roadmap v2 actually needs when that command is implemented.
- **Milestone**: M4 (return contract), M5 (integration)
- **Mitigation**:
  1. Define return contract early (M4 T4.7) with generous fields
  2. Test against documented sc:roadmap v2 integration patterns (Section 7.1)
  3. Return contract is a simple data structure — cheap to extend later
- **Contingency**: Add fields to return contract in a backward-compatible way when sc:roadmap v2 is built
- **Detection**: Review return contract against Section 7.1 before finalizing M4

---

## Process Risks

### R7: Scope Creep into Domain-Specific Validation [Score: 3 — Medium-Low]
- **Probability**: Medium (35%)
- **Impact**: Low — delays milestone
- **Description**: Temptation to add domain-specific validation (e.g., "is this roadmap technically feasible?") during merge execution. Spec explicitly excludes this (Section 2.2).
- **Mitigation**: Strict adherence to spec boundaries — sc:adversarial validates process and structure, not domain correctness. Calling command handles domain validation.
- **Detection**: Review merged output for domain-specific assertions

### R8: SKILL.md Complexity [Score: 3 — Medium-Low]
- **Probability**: Medium (40%)
- **Impact**: Low — requires iteration
- **Description**: The SKILL.md behavioral instructions need to encode a complex 5-step protocol with error handling, interactive mode, and MCP integration in ~400-500 lines. Getting the prompt engineering right may require multiple iterations.
- **Mitigation**: Start with core protocol (steps 1-5), add error handling and interactive mode incrementally. Test each step independently before combining.
- **Detection**: E2E validation in M5 reveals behavioral issues

---

## Risk Heatmap

```
Impact →     Low          Medium       High
           ┌────────────┬────────────┬────────────┐
High       │            │            │ R1         │
Prob       │            │            │ Sycophancy │
           ├────────────┼────────────┼────────────┤
Medium     │ R4 Rate    │ R2 Metrics │            │
Prob       │ R7 Scope   │ R8 SKILL   │            │
           ├────────────┼────────────┼────────────┤
Low        │            │ R5 Bias    │ R3 Merge   │
Prob       │            │ R6 Contract│            │
           └────────────┴────────────┴────────────┘
```

## Top 3 Risks to Monitor

1. **R1 Sycophantic Convergence** — Most likely to undermine the command's core value proposition. Monitor debate quality from first M2 test.
2. **R2 Quantitative Metrics** — Must be deterministic and consistent. Test across artifact types early in M3.
3. **R3 Merge Corruption** — Low probability but high impact. Post-merge validation is mandatory, not optional.

---

*Generated from SC-ADVERSARIAL-SPEC.md v1.1.0 — 2026-02-21*
