---
comparison_pair: 3
ic_component: PM Agent
lw_component: Anti-Hallucination Rules + PABLOV Method
ic_source: src/superclaude/pm_agent/confidence.py, src/superclaude/pm_agent/reflexion.py, src/superclaude/pm_agent/self_check.py
lw_source: .gfdoc/rules/core/anti_hallucination_task_completion_rules.md, .gfdoc/rules/core/ib_agent_core.md
mapping_type: functional_analog
verdict_class: split by context
confidence: 0.80
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: PM Agent (IC) vs Anti-Hallucination + PABLOV (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude PM Agent provides **three orthogonal, testable, token-efficient quality patterns**: ConfidenceChecker (pre-execution, 100–200 token cost), SelfCheckProtocol (post-implementation), and ReflexionPattern (cross-session error learning). The Python implementation is testable via pytest fixtures, composable without coupling, and token-efficient by design. A 90% confidence threshold prevents wrong-direction work before it starts — a proactive approach. The reported ROI is 25–250x (100–200 tokens spent to avoid 5K–50K tokens of misdirected implementation).

**Key strengths** (`src/superclaude/pm_agent/confidence.py:42`, `src/superclaude/pm_agent/reflexion.py:76`):
- Pre-execution gate: 5 weighted checks totaling confidence score
- Post-implementation: 7 hallucination red flags including uncertainty language detection
- Cross-session learning: JSONL + Mindbase storage survives session resets
- pytest fixtures via `pyproject.toml` entry-point auto-loading (zero-config)
- Token budgets: static constants (simple: 200, medium: 1000, complex: 2500)

### LW Advocate Position
The llm-workflows combination of anti-hallucination rules and PABLOV provides **deeper, more rigorous verification** through presumption of falsehood and artifact-chain completeness. Anti-hallucination rules invert the default epistemic stance: claims are "Incorrect" by default, with a FAS -100 penalty for fabricated sources. PABLOV goes further: every execution stage requires a filesystem-verifiable artifact, not just a self-report. The Worker's `worker_handoff` (claim) is validated against the `programmatic_handoff` (proof), not against the Worker's own confidence score.

**Key strengths** (`anti_hallucination_task_completion_rules.md:59-82`, `ib_agent_core.md:106-112`):
- Presumption of Falsehood: "Incorrect" by default, burden of proof on agent
- FAS -100 penalty for forgery: genuine deterrence against confabulation
- Mandatory negative evidence documentation: "Not found" is required, not silent
- Five mandatory artifact types: no stage skippable
- Zero-trust QA: treats all Worker claims with skepticism by default

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/pm_agent/confidence.py` | 42 | `ConfidenceChecker.assess()` with 5 weighted checks |
| `src/superclaude/pm_agent/confidence.py` | 162 | `_architecture_compliant()` and `_root_cause_identified()` are placeholder implementations |
| `src/superclaude/pm_agent/self_check.py` | 64 | `SelfCheckProtocol.validate()` with 4 mandatory questions |
| `src/superclaude/pm_agent/self_check.py` | 212 | 7 hallucination red flag detection patterns |
| `src/superclaude/pm_agent/reflexion.py` | 76 | `ReflexionPattern.get_solution()` with Mindbase + JSONL fallback |
| `src/superclaude/pm_agent/token_budget.py` | 17 | Static token limits: simple=200, medium=1000, complex=2500 |
| `src/superclaude/pytest_plugin.py` | 1 | Auto-loaded via `entry-points.pytest11` |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 59-66 | Presumption of Falsehood: default status "Incorrect" |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 76-82 | FAS -100 penalty for forgery: task fails immediately |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 83-89 | Mandatory negative evidence: "Not found" is required entry |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 128-137 | Strict COMPLETE definition: all requirements + warnings resolved + tested |
| `.gfdoc/rules/core/ib_agent_core.md` | 106-112 | Five mandatory artifacts in unbroken chain |
| `.gfdoc/rules/core/ib_agent_core.md` | 87-97 | Agent Contracts: explicit output requirements per role |
| `.gfdoc/rules/core/ib_agent_core.md` | 99-104 | Zero-trust verification: character-level verification for EXACT specs |

## 3. Adversarial Debate

**IC attacks LW**: IC's confidence check prevents wrong-direction work before it starts. LW's PABLOV detects failure after execution — the Worker has already run, consumed tokens, and produced a flawed `worker_handoff` before the QA agent catches it. IC's pre-execution investment (100–200 tokens) replaces post-execution rework (5K–50K tokens). Furthermore, LW's anti-hallucination evidence table requires a structured table for every technical claim — high overhead for routine tasks. IC's SelfCheckProtocol is lighter: 4 mandatory questions + 7 red flag checks without per-claim structured tables.

**LW attacks IC**: IC's `ConfidenceChecker._architecture_compliant()` is a documented placeholder — it checks for dict keys, not real architectural compliance. A caller that sets `architecture_check_complete: True` in the context dict without actual verification bypasses this check entirely. IC's confidence gate is only as strong as its weakest check. LW's PABLOV cannot be bypassed by setting a dict key — it requires real filesystem artifacts. The `programmatic_handoff` must exist as an actual file with verifiable content, not a Python dict entry.

**IC counter**: LW's PABLOV costs two full Claude sessions per batch (Worker + QA). For a 50-item task with batch size 5, that's 10 Worker sessions + 10 QA sessions. IC's three-pattern system (confidence check + self-check + reflexion) runs within a single session at a fraction of the cost. The placeholder implementation weakness in `ConfidenceChecker` is a known, documented gap with explicit extension guidance — not a hidden flaw.

**LW counter**: IC's cross-session error learning (ReflexionPattern) requires Mindbase MCP to be available. If Mindbase is unavailable, fallback to grep-based text search, then to `None`. When `get_solution()` returns `None`, the error learning falls through entirely. LW's JSONL-to-PABLOV artifact chain degrades gracefully: even a synthesized `programmatic_handoff` (fallback path) provides a filesystem-verifiable artifact.

**Convergence**: IC optimizes for token efficiency and developer experience; LW optimizes for verification completeness and fabrication prevention. Both address agent reliability but at different layers: IC at session level (behavioral pattern), LW at pipeline level (artifact chain). A combined approach would be more powerful than either alone.

## 4. Verdict

**Verdict class: SPLIT BY CONTEXT**

**Conditions where IC is stronger:**
- Single-session tasks where pre-execution confidence checking prevents wrong-direction work
- Token-constrained environments where full PABLOV overhead is prohibitive
- Developer workflows where pytest integration and programmatic quality checks are valued
- Cross-session learning use cases (ReflexionPattern JSONL persistence)

**Conditions where LW is stronger:**
- Multi-session pipeline execution where filesystem-verifiable artifacts are required
- High-trust-sensitivity tasks where "Presumption of Falsehood" and FAS -100 provide genuine deterrence
- Environments with dedicated QA agents able to independently verify Worker claims
- When the distinction between claim (worker_handoff) and proof (programmatic_handoff) is architecturally significant

**Confidence: 0.80**

**Adopt patterns, not mass**: From LW: Presumption of Falsehood as the default epistemic stance (stronger than IC's confidence threshold approach), mandatory negative evidence documentation (IC's self-check does not require documenting "not found"), the claim/proof distinction (IC's SelfCheckProtocol could add a `filesystem_verified` field analogous to `programmatic_handoff`), and the strict COMPLETE definition. From IC: pre-execution confidence gating (prevent wrong-direction work), token budget management, cross-session error learning via JSONL. Do NOT adopt: PABLOV's mandatory sequential item execution (prohibits parallelism), the full five-artifact chain for lightweight tasks, LW's prescribed tool list.
