# Strategy: LW Component — Anti-Sycophancy System

**Component**: Anti-Sycophancy System
**Source (primary)**: `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md`
**Source (degraded)**: `.gfdoc/rules/core/anti_sycophancy.md`
**Path Verified**: true (both paths)
**Strategy Analyzable**: true (primary path); degraded (anti_sycophancy.md — content duplicates anti_hallucination file)
**Degraded Evidence Note**: `.gfdoc/rules/core/anti_sycophancy.md` content is identical to `anti_hallucination_task_completion_rules.md`. All pattern-level analysis uses `RISK_PATTERNS_COMPREHENSIVE.md` as authoritative source per D-0009 OQ-001 resolution.
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The anti-sycophancy system is a two-tier, risk-scored framework for detecting and neutralizing bias-seeking query patterns before they corrupt LLM outputs.

**Core rigor mechanisms:**

- **12 well-defined pattern categories**: Each category has explicit linguistic examples, risk weights, and modifiers. The categories cover the full space of sycophancy-inducing queries: Comparative Bias, Confirmation Seeking, User Belief Statements, Challenge/Disagreement, Loaded Questions, Hidden Assumptions, Stated Preference, Absolute Statements, Authority Appeals, Strawman Arguments, Emotional Language, Rhetorical Questions. `RISK_PATTERNS_COMPREHENSIVE.md:9-304`
- **Quantified risk scoring algorithm**: Base score calculated by summing matched pattern weights. Modifiers for compound patterns. Cap at 1.0. `RISK_PATTERNS_COMPREHENSIVE.md:308-349`
- **Multiple pattern multiplier**: When 2+ patterns detected: risk_score × 1.3. When 3+ patterns: × 1.5. This non-linear escalation reflects that combined sycophancy triggers are more dangerous than isolated ones. `RISK_PATTERNS_COMPREHENSIVE.md:339-349`
- **Four-tier response protocol**: Low (0.0-0.3): standard response. Medium (0.3-0.6): explicit trade-offs and confidence. High (0.6-0.8): balanced + suggest /rf:opinion. Critical (0.8-1.0): challenge premise + counter-evidence + strong escalation. `RISK_PATTERNS_COMPREHENSIVE.md:353-386`
- **Two-tier architecture**: Tier 1 (always-active, embedded ~30 lines in ib_agent_core) for lightweight detection. Tier 2 (/rf:opinion command, full 3-layer analysis: Constitutional AI, Chain-of-Verification, multi-perspective debate). `anti_sycophancy_guide.md:89-108`
- **Validation test corpus**: 50 queries (15 low, 15 medium, 15 high, 15 critical) with success criteria >90% pattern detection accuracy, <10% false positive rate. `RISK_PATTERNS_COMPREHENSIVE.md:444-477`

**Rigor verdict**: The quantified risk scoring with non-linear multipliers and the two-tier architecture are both rigorous. The pattern library is comprehensive and covers edge cases (hidden assumption patterns, rhetorical questions) that simpler systems miss.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- 12 pattern categories with multiple sub-patterns per category represents a large pattern space. The lightweight Tier 1 embedding (~30 lines) only covers the highest-priority patterns. The full library is referenced by Tier 2 only.
- The Tier 2 `/rf:opinion` command spawns a separate agent with full 3-layer analysis. This adds 5-10 seconds latency per invocation. `anti_sycophancy_guide.md:411-413`
- The two-tier architecture requires maintaining two separate representations of the same patterns — a lightweight version and the full library.

**Operational drag:**
- The system calibration note ("suggest /rf:opinion too often" is intentional) means high-volume usage will frequently divert users to a slower, more expensive analysis path.
- Pattern weights are static — the v5.3 plan for cross-session pattern learning via Serena MCP is deferred. Without adaptive thresholds, false positive rates cannot improve automatically. `RISK_PATTERNS_COMPREHENSIVE.md:391-412`

**Token/runtime expense:**
- Tier 2 full analysis uses Constitutional AI + Chain-of-Verification + Adversarial Debate in sequence. Token cost is high (~2000 tokens of agent context per invocation). `anti_sycophancy_guide.md:407-408`
- The test corpus maintenance (50 queries, ongoing calibration) is a non-trivial operational cost.

**Maintenance burden:**
- The degraded duplicate file (`anti_sycophancy.md` = copy of `anti_hallucination_task_completion_rules.md`) is a maintenance risk. Any divergence between these files creates confusion about which is authoritative.
- Pattern weights are manually calibrated. As language models change, recalibration is required but there is no automated feedback mechanism.

---

## 3. Execution Model

The anti-sycophancy system operates as a **pre-response risk assessment layer**:

1. Every query: scan for pattern matches from the 12 categories (Tier 1 lightweight)
2. Compute risk score: sum weights, apply multipliers, cap at 1.0
3. Route response strategy by risk level:
   - Low: standard response
   - Medium: include trade-offs and confidence levels
   - High: balanced response + escalation suggestion
   - Critical: premise challenge + counter-evidence + strong escalation
4. Tier 2 (optional): when `/rf:opinion` invoked, run Constitutional AI + CoVe + Adversarial Debate

**Quality enforcement**: Risk scoring is computed per-query, not per-task. This means protection applies at the finest granularity (individual user queries) rather than only at task level.

**Extension points**:
- v5.3 planned MCP integration: Sequential for bias detection, Context7 for fact verification, Serena for adaptive thresholds. `RISK_PATTERNS_COMPREHENSIVE.md:391-412`
- Pattern weights are explicitly configurable.
- Test corpus can be extended with new patterns.

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The 12-category pattern taxonomy is directly adoptable as SuperClaude's anti-sycophancy NFR vocabulary. The categories provide a shared language for identifying sycophancy risk.
- The non-linear multiple-pattern multiplier (1.3x for 2+ patterns, 1.5x for 3+) is directly adoptable as a risk escalation principle.
- The four-tier response protocol (standard → balanced → suggest escalation → challenge premise) is directly adoptable as SuperClaude's sycophancy response strategy.

**Conditionally Adoptable:**
- The two-tier architecture (lightweight embedded detection + on-demand deep analysis) is conditionally adoptable. SuperClaude's equivalent would be: always-on NFR checking (Tier 1) + adversarial skill invocation for high-risk analysis (Tier 2).
- The validation test corpus methodology is conditionally adoptable for validating SuperClaude's own compliance behavior.

**Reject:**
- The specific `/rf:opinion` command as a Tier 2 invocation path — SuperClaude has its own `/sc:adversarial` skill for this purpose.
- Static pattern weights without adaptive learning (this is a known gap that should be addressed, not adopted).
