---
comparison_pair: 4
ic_component: Adversarial Pipeline
lw_component: Anti-Sycophancy System
ic_source: .claude/skills/sc-adversarial-protocol/SKILL.md, .claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md
lw_source: .dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md
mapping_type: functional_analog
verdict_class: IC stronger
confidence: 0.83
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Adversarial Pipeline (IC) vs Anti-Sycophancy System (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude adversarial pipeline is a **deep, multi-step structured debate system** that forces LLM variants to explicitly argue for their positions, surface assumptions, and produce a scored, merged output. The 5-step sequential protocol (diff → debate → base selection → refactoring plan → merge) with 6 named artifacts creates a complete evidence trail. The CEV (Claim-Evidence-Verdict) protocol prevents hallucinated quality scores. Position-bias mitigation (double-pass forward + reverse evaluation) eliminates a systematic LLM bias. The tiebreaker protocol (debate performance → correctness count → input order) is deterministic.

**Key strengths** (`.claude/skills/sc-adversarial-protocol/SKILL.md:412`, `refs/scoring-protocol.md:189`):
- CEV protocol: every qualitative criterion requires explicit evidence citation
- Position-bias double-pass: forward + reverse evaluation averaged
- 3-level deterministic tiebreaker protocol
- Pipeline Mode with manifest-based resume for interrupted comparisons
- Convergence plateau detection prevents infinite debate loops
- Return contract: callers can inspect `status` and `unresolved_conflicts`

### LW Advocate Position
The llm-workflows anti-sycophancy system is a **proactive, per-query risk detection system** that operates before the LLM response is generated — not after. Where IC's adversarial pipeline is invoked explicitly for structured comparisons, LW's system is always-active at Tier 1, embedded as ~30 lines in `ib_agent_core`. The 12-category pattern taxonomy with quantified risk scoring and non-linear multipliers (2+ patterns: ×1.3; 3+: ×1.5) catches sycophancy risk at the finest granularity (individual query). The four-tier response protocol routes queries to appropriate handling without requiring explicit invocation.

**Key strengths** (`RISK_PATTERNS_COMPREHENSIVE.md:9-304`, `RISK_PATTERNS_COMPREHENSIVE.md:308-349`):
- 12 pattern categories covering full sycophancy-inducing query space
- Non-linear multiple-pattern multiplier (1.3× for 2+, 1.5× for 3+)
- Four-tier response routing: Low → standard; Medium → trade-offs; High → escalate; Critical → challenge premise
- Always-active Tier 1: embedded in every agent interaction, not invoked explicitly
- Validation test corpus: 50 queries with >90% detection, <10% false positive targets

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | — | 5-step sequential protocol (diff → debate → base → refactor → merge) |
| `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` | 189 | Tiebreaker: debate wins → correctness count → input order |
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | 412 | Return contract: merged_output_path, convergence_score, status, unresolved_conflicts |
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | — | CEV protocol: claim-evidence-verdict for every qualitative criterion |
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | — | Position-bias: double forward + reverse pass, scores averaged |
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | — | Pipeline Mode: manifest-based resume for interrupted comparisons |
| `.claude/skills/sc-adversarial-protocol/SKILL.md` | — | Convergence plateau detection: halts when no further progress achievable |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 9-304 | 12 pattern categories with weights and examples |
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 308-349 | Risk scoring: sum weights, apply multipliers, cap at 1.0 |
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 339-349 | Non-linear multiplier: 2+ patterns ×1.3; 3+ patterns ×1.5 |
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 353-386 | Four-tier response protocol with explicit routing |
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 391-412 | v5.3 plan: deferred adaptive pattern learning via Serena MCP |
| `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 444-477 | Test corpus: 50 queries, >90% detection, <10% false positive |

## 3. Adversarial Debate

**IC attacks LW**: LW's anti-sycophancy system is a detection system, not a correction system. Detecting that a query has sycophancy risk and routing it to a "balanced response" does not guarantee the response is actually unbiased — it relies on the model to behave differently after risk detection. IC's adversarial pipeline forces explicit disagreement through structured debate, producing artifacts that demonstrate the adversarial process was actually executed (diff analysis, debate transcript, scoring). LW's Tier 1 detection has no equivalent audit trail.

**LW attacks IC**: IC's adversarial pipeline is explicitly invoked — it requires a user or system to decide to run `/sc:adversarial`. Sycophancy risks in routine responses (answering a leading question, over-agreeing with a user's flawed premise) occur in interactions where `/sc:adversarial` would never be invoked. LW's Tier 1 is always-active: every query is scanned, every response is risk-routed. IC's adversarial pipeline addresses deep structured comparison; LW's system addresses ambient sycophancy in everyday interaction.

**IC counter**: The comparison is addressing different problem spaces. IC's adversarial pipeline is for document/artifact comparison, not conversational sycophancy detection. Within its intended domain (comparing 2–10 substantive documents), IC is demonstrably more rigorous: CEV protocol, position-bias mitigation, and a convergence score. LW has nothing equivalent for deep structured artifact comparison.

**LW counter**: LW's 12-category taxonomy and quantified risk scoring is more systematic than IC's implicit assumption that "adversarial debate produces unbiased output." IC's debate step involves the same LLM (possibly different persona) arguing positions — there is no external validation that the debate actually mitigated bias. LW's test corpus (50 queries with measured detection rates) provides empirical validation IC lacks.

**Convergence**: These systems address orthogonal problems. IC excels at deep structured comparison between substantive artifacts. LW excels at ambient sycophancy detection in everyday agent interactions. A complete framework would use both: IC's adversarial protocol for explicit comparison tasks, LW's risk scoring for inline response risk assessment.

## 4. Verdict

**Verdict class: IC STRONGER (for artifact comparison); LW STRONGER (for ambient sycophancy protection)**

**Primary verdict class: IC STRONGER**

The adversarial pipeline comparison dimension in the D-0010 mapping is the IC adversarial pipeline vs. LW anti-sycophancy system. For the specific problem of structured adversarial comparison between artifacts, IC is decisively stronger: CEV protocol, position-bias mitigation, convergence scoring, pipeline resume, and a structured return contract all exceed anything in LW's anti-sycophancy system.

For ambient sycophancy detection in routine interactions, LW's always-active Tier 1 with 12-category scoring exceeds IC's capability.

**Conditions where IC is stronger:**
- Structured comparison between 2–10 substantive documents
- Situations requiring an audit trail of the adversarial process
- When convergence scoring and unresolved conflict reporting are needed
- Any use case of the adversarial protocol (explicit invocation)

**Conditions where LW is stronger:**
- Ambient sycophancy detection in routine interactions
- Always-active risk scoring without explicit invocation
- Per-query fine-grained risk routing

**Confidence: 0.83**

**Adopt patterns, not mass**: From LW: the 12-category sycophancy risk taxonomy (directly adoptable as IC's NFR vocabulary for sycophancy detection), the non-linear multiple-pattern multiplier (1.3×/1.5× escalation principle), the four-tier response protocol (standard → trade-offs → escalate → challenge premise), and the 50-query validation corpus methodology. From IC: CEV protocol (evidence-backed qualitative scoring), position-bias double-pass (forward + reverse evaluation averaged), convergence plateau detection. Do NOT adopt: LW's specific `/rf:opinion` command, static pattern weights without adaptive learning, or LW's reference to its own tool list.
