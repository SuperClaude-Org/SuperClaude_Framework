---
comparison_pair: 6
ic_component: Quality Agents
lw_component: Agent Definitions (rf-*.md)
ic_source: .claude/agents/quality-engineer.md, .claude/agents/audit-validator.md, src/superclaude/agents/pm-agent.md
lw_source: .claude/agents/rf-team-lead.md, .claude/agents/rf-task-builder.md, .claude/agents/rf-task-executor.md, .claude/agents/rf-task-researcher.md
mapping_type: direct
verdict_class: split by context
confidence: 0.79
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Quality Agents (IC) vs Agent Definitions / rf-* (LW)

## 1. Debating Positions

### IC Advocate Position
IronClaude's quality agent ecosystem is **role-differentiated and safety-scoped**: each agent has a distinct verification function (quality-engineer: STRICT-tier testing; audit-validator: spot-check with CRITICAL FAIL on false-negative DELETE; self-review: evidence-focused post-implementation checklist; pm-agent: session-level meta-orchestration). The `audit-validator` uses `permissionMode: plan` enforcing read-only verification — it cannot accidentally modify what it is auditing. The stratified sampler (`spot_check.py:49`) with `seed=42` produces reproducible samples. The pm-agent implements PDCA and triggers on error detection, not just on explicit invocation.

**Key strengths** (`src/superclaude/agents/audit-validator.md:16`, `.claude/agents/quality-engineer.md:15`):
- `audit-validator`: CRITICAL FAIL on false-negative DELETE (hard-coded safety policy)
- `permissionMode: plan` on audit-validator: architectural read-only enforcement
- Stratified sampling with `seed=42`: reproducible verification
- pm-agent: session start MANDATORY context restoration via Serena MCP
- quality-engineer: invoked for STRICT-tier, tests edge cases and boundary conditions
- self-review: brief checklist output (evidence, not narrative) for fast consumption

### LW Advocate Position
The Rigorflow rf-* agents implement a **formal role specialization with typed communication protocols** and explicit agent contracts. Every inter-agent message uses typed structured formats (`RESEARCH_READY`, `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`). Each agent definition specifies exactly which messages it sends, to whom, when — and exactly which messages it receives and what action to take. The executor validation gate (validate task file before executing it) prevents the most common failure mode at zero cost. The `memory: project` persistence accumulates team lead patterns across conversations.

**Key strengths** (`.claude/agents/rf-task-executor.md:95-118`, `rf-task-researcher.md:43-56`):
- Typed communication protocol: structured message types with explicit sender/receiver/trigger tables
- Executor validation gate: reads and validates task file before executing — sends BLOCKED on invalid structure
- Negative result reporting: researcher must document "what you DON'T find" — negative results are valuable
- Track isolation enforcement: builder-T messages only researcher-T (never cross-track)
- Team lead cleanup obligation: explicitly responsible for agent shutdown
- `memory: project`: agent memory accumulates across conversations for cross-session learning

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/agents/audit-validator.md` | 16 | "Do NOT assume the prior agent was correct. Verify everything from scratch." |
| `.claude/agents/quality-engineer.md` | 15 | "Think beyond the happy path to discover hidden failure modes" |
| `src/superclaude/cli/audit/spot_check.py` | 49 | `_stratified_sample()` with `seed=42` for reproducible sampling |
| `src/superclaude/agents/audit-validator.md` | — | CRITICAL FAIL: false negative on DELETE → unconditional validation fail |
| `src/superclaude/agents/pm-agent.md` | 138 | PDCA self-evaluation cycle |
| `.claude/agents/audit-validator.md` | — | `permissionMode: plan` enforces read-only architectural constraint |
| `src/superclaude/agents/self-review.md` | 14 | "Keep answers brief—focus on evidence, not storytelling" |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.claude/agents/rf-task-executor.md` | 95-118 | Executor validation gate: validate task file before executing |
| `.claude/agents/rf-task-researcher.md` | 43-56 | Typed communication protocol: message types with sender/receiver/trigger tables |
| `.claude/agents/rf-task-builder.md` | 43-49 | Builder typed messages: TASK_READY with explicit fields |
| `.claude/agents/rf-team-lead.md` | 1-30 | All agents: `model: opus`, `permissionMode: bypassPermissions` |
| `.claude/agents/rf-task-researcher.md` | 424-430 | Negative result reporting: "Don't guess. Report what you DON'T find." |
| `.claude/commands/rf/pipeline.md` | 779 | Track isolation: builder-T messages only researcher-T |
| `.claude/agents/rf-team-lead.md` | 5 | `memory: project` for cross-session accumulation |

## 3. Adversarial Debate

**IC attacks LW**: LW uses `permissionMode: bypassPermissions` for ALL agents — including the researcher, which IC would argue should never have write access. The LW researcher is explicitly instructed not to modify source code files, but this restriction is behavioral (instruction), not technical (tool restriction). IC's `audit-validator` has architectural enforcement: `permissionMode: plan` prevents file modification at the system level, not just at the instruction level. Technical constraints are more reliable than behavioral constraints for safety-critical operations.

**LW attacks IC**: IC's quality agents lack a formal communication protocol. quality-engineer, audit-validator, self-review, and pm-agent have no typed inter-agent messages — they produce reports and return results, but there is no formal handoff protocol between them. LW's typed message system (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE, BLOCKED) ensures reliable inter-agent coordination and makes agent failures explicit (BLOCKED message type). IC agents silently complete or fail; LW agents communicate state.

**IC counter**: IC's quality agents are verification-focused, not execution-focused. They don't need typed inter-agent communication because they're invoked for single-purpose verification tasks, not multi-agent pipelines. The `audit-validator`'s CRITICAL FAIL → PASS/FAIL verdict is a simpler, more direct result than LW's multi-message orchestration. Furthermore, IC's model is tiered: `audit-validator` likely uses a lighter model than `quality-engineer`, while LW forces opus for all rf-* agents regardless of task complexity.

**LW counter**: IC's pm-agent "mistake detection" trigger depends on the pm-agent being active and Serena MCP being available. If Serena MCP is unavailable at session start, the pm-agent's context restoration fails and automatic mistake detection becomes unavailable. LW's team lead uses `memory: project` with in-process persistence — no external MCP dependency for basic memory.

**Convergence**: IC's read-only enforcement (`permissionMode: plan`) and LW's typed communication protocol are both adoptable to the other framework. IC excels at safety-scoped verification; LW excels at multi-agent coordination formalism. The key difference: IC's agents are quality-gatekeepers; LW's agents are execution-collaborators.

## 4. Verdict

**Verdict class: SPLIT BY CONTEXT**

**Conditions where IC is stronger:**
- Quality verification use cases (post-implementation checking, audit validation)
- Safety-critical verification where read-only enforcement is required (`permissionMode: plan`)
- Tasks requiring reproducible, stratified sampling (seeded audit validation)
- Single-session verification where lightweight, evidence-focused reports are preferred

**Conditions where LW is stronger:**
- Multi-agent execution pipelines where typed communication protocols enable reliable coordination
- Research → build → execute chains where BLOCKED messages prevent silent failures
- Cross-session agent coordination where `memory: project` persistence accumulates patterns
- Scenarios requiring executor validation gates (validate task file before executing it)

**Confidence: 0.79**

**Adopt patterns, not mass**: From LW: the typed communication protocol (explicit message types with sender/receiver/trigger — IC agents should communicate state, not just produce reports), the executor validation gate (validate agent input before executing, send BLOCKED on invalid), negative result reporting as an explicit agent obligation, and the track isolation rule (agents communicate only with their designated counterpart). From IC: `permissionMode: plan` as the default for all verification agents (not just audit-validator), stratified sampling with reproducible seeds for spot-check validation, and the CRITICAL FAIL condition (a specific failure type forces unconditional fail — not just a high discrepancy rate). Do NOT adopt: LW's all-opus model selection, `permissionMode: bypassPermissions` for all agents, or the researcher Write tool access with behavioral-only restriction.
