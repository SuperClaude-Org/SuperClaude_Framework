# Strategy: LW Component — Agent Definitions

**Component**: Agent Definitions (rf-*.md)
**Source**: `.claude/agents/rf-team-lead.md`, `.claude/agents/rf-task-builder.md`, `.claude/agents/rf-task-executor.md`, `.claude/agents/rf-task-researcher.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The Rigorflow agent definitions implement a structured role-based multi-agent team with explicit communication protocols, clear role boundaries, and persistent memory mechanisms.

**Core rigor mechanisms:**

- **Explicit role specialization**: Each agent has a single, well-defined primary responsibility. Researcher: codebase exploration. Builder: MDTM task file creation. Executor: `automated_qa_workflow.sh` execution. Team lead: orchestration and coordination. No agent assumes another's responsibilities. `README.md:8-11`
- **Formal communication protocol**: All inter-agent messages use typed structured formats (`RESEARCH_READY`, `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`). Each agent definition specifies exactly which messages it sends, to whom, when — and which messages it receives and what action to take. `rf-task-researcher.md:43-56, rf-task-builder.md:43-49`
- **Track isolation enforcement**: Builder-T is explicitly instructed to message only `researcher-T`, never another track's researcher. `pipeline.md:779`
- **Task-scoped memory persistence**: All agents use `memory: project` — agent memory accumulates across conversations within the project. `rf-task-builder.md:5, rf-team-lead.md:5`
- **Researcher negative result reporting**: "Report what you DON'T find — Negative results are valuable. Don't guess." `rf-task-researcher.md:424-430`
- **Executor validation gate**: Before executing any task, executor reads and validates the task file (YAML frontmatter, checklist items, structure). If invalid, sends BLOCKED rather than executing a malformed task. `rf-task-executor.md:95-118`
- **Team lead cleanup obligation**: Team lead is explicitly responsible for shutting down teammates after completion. `rf-team-lead.md:291 "Clean up when done"`

**Rigor verdict**: The typed communication protocol and the executor validation gate are the strongest elements. The validation gate prevents the most common failure mode (executing a malformed task file) at zero cost — a file read before a 4-hour workflow invocation.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- All four agents use `model: opus` with `permissionMode: bypassPermissions` and full tool lists (17+ tools per agent). This is maximum-cost, maximum-capability configuration for all roles, including the researcher whose primary work is file reading.
- Agent definitions are verbose. Each agent's definition includes the full team structure, communication protocol, workflow steps, and examples. The researcher definition alone is 400+ lines.
- The `memory: project` configuration means every agent loads project memory on initialization. For large projects, this memory loading adds latency.

**Operational drag:**
- The team lead's review step between researcher completion and builder spawning is a serialization point. Even in event-driven mode, the team lead must evaluate research quality before spawning the builder.
- The "Let teammates work autonomously — only intervene when blocked" instruction conflicts with the review step. These two behaviors create ambiguity about when intervention is appropriate.

**Token/runtime expense:**
- All agents at opus level: researcher (codebase scanning), builder (file creation), executor (workflow invocation), team lead (orchestration) — 4× opus invocations per track per pipeline. For 5-track: 20 opus invocations.
- Agent definitions are loaded as system prompts. Four large definition files = 4 full context loads per pipeline.
- The agent memory file (`rf-task-builder/MEMORY.md`) grows across conversations without a defined size limit. Large memory files slow initialization.

**Maintenance burden:**
- The teammate name/routing protocol (single track: `researcher`, `builder`, `executor`; multi-track: `researcher-1`, `builder-1`, etc.) requires all agent definitions to agree on naming conventions. Changes require synchronized updates.
- `permissionMode: bypassPermissions` is a significant security decision that bypasses all permission gates for all agents. This is convenient but eliminates the ability to audit or restrict agent actions.
- The researcher explicitly prohibits modifying source code files but has Write tool access. The permission boundary is behavioral (instruction), not technical (tool restriction).

---

## 3. Execution Model

Agent definitions operate as **role-scoped Claude Code sub-agent specifications**:

Each `.md` file in `.claude/agents/` defines:
- Agent name (routing key for SendMessage)
- Model (all: opus)
- Memory scope (all: project)
- Permission mode (all: bypassPermissions)
- Allowed tools (all: full set)
- Role description and responsibilities
- Communication protocol (messages in/out)
- Workflow steps
- Behavioral constraints ("Do NOT modify source code")

Agents are spawned by the team lead with role-specific prompts. They communicate via `SendMessage` using the typed protocol. They share state via filesystem (research notes, task files) and in-context messages.

**Quality enforcement**: Quality within each agent's scope is governed by the agent's role constraints. The team lead is the only quality gate at the orchestration level — it reviews researcher output before builder spawning.

**Extension points**:
- Additional agent types can be added (e.g., `rf-task-reviewer.md` for a dedicated review agent)
- Agent prompts can be customized via spawn-time prompt injection
- Team lead memory can accumulate pipeline patterns across conversations

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The typed communication protocol (structured message types with explicit sender/receiver/trigger/action tables) is directly adoptable for SuperClaude's multi-agent delegation pattern.
- The executor validation gate (validate task file before executing it) is directly adoptable for any SuperClaude agent that accepts a specification file as input.
- Negative result reporting as an explicit researcher obligation is directly adoptable for SuperClaude's research agents.

**Conditionally Adoptable:**
- The role specialization model (separate researcher/builder/executor agents) is conditionally adoptable. The roles are well-defined; the implementation cost (opus × 3+ agents) is high. SuperClaude should use model-tiered agents (haiku for research, sonnet for building, opus for critical execution).
- The `memory: project` agent memory mechanism is conditionally adoptable — valuable for cross-session learning, but requires memory size management.

**Reject:**
- All-`opus` model selection. A tiered model approach (haiku for researcher, sonnet for builder, opus for executor) would reduce cost significantly without material quality loss.
- `permissionMode: bypassPermissions` for all agents. Permissions should be scoped to each agent's actual needs.
- The researcher Write tool access with behavioral-only restriction (instruction not to modify source files). Technical restrictions are more reliable than behavioral ones for security-sensitive operations.
