---
component: quality-agents
deliverable: D-0026
source_comparison: comparison-quality-agents.md
verdict: split by context
principle_primary: Scalable Quality Enforcement
principle_secondary: Evidence Integrity
generated: 2026-03-15
---

# Improvement Plan: Quality Agents

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM QA-001 — Executor Validation Gate for All Agent Entry Points

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's executor validation gate pattern (validate input before starting execution, emit BLOCKED for invalid input) without LW's permissionMode:bypassPermissions
**Why not full import**: LW's validation gate is bundled with `permissionMode: bypassPermissions` for rf-* agents (explicitly rejected in D-0022 Principle 4); IC's validation gate must be the inverse — validate first and block on invalid input, without bypassing permissions.

**File paths and change description**:
- `.claude/agents/quality-engineer.md` — Add to the agent's operating instructions: "Before beginning any verification task, validate that the task specification includes: (a) an explicit acceptance criteria list, (b) at least one file path reference, (c) a compliance tier. If any of these is absent, emit BLOCKED with reason and request the missing fields before proceeding."
- `src/superclaude/agents/quality-engineer.md` — Sync copy.
- `.claude/agents/self-review.md` — Add the same pre-execution validation checklist: validate that the implementation record includes at least one artifact path and a stated completion claim.
- `src/superclaude/agents/self-review.md` — Sync copy.
- `.claude/agents/audit-validator.md` — Confirm this agent already has `permissionMode: plan` (read-only). Add: "If the sample of audit findings provided has fewer than 3 items, emit BLOCKED with reason 'insufficient sample size for validation' rather than producing an unreliable PASS."

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 6: "Before any agent begins execution, it should validate its input file/specification and emit BLOCKED if the structure is invalid."

**Dependencies**: None
**Acceptance criteria**: quality-engineer.md has a pre-execution validation checklist with 3 required fields; self-review.md has a pre-execution validation requiring artifact path; audit-validator.md has minimum sample size check; all dev copies are synced.
**Risk**: Low. Agent instruction additions; behavioral improvement with no code changes.

---

## ITEM QA-002 — Typed State Transitions for Sequential Agent Invocation

**Priority**: P0
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's typed message protocol (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE, BLOCKED) as IC-native typed state enums for quality agent coordination, not LW's bash IPC or all-opus model mandate
**Why not full import**: LW's typed message protocol uses bash inter-process communication and requires all-opus model selection for agent coordination (both explicitly rejected); IC needs only the typed state concept as named constants in agent handoff documentation and the sprint/roadmap pipeline agent invocation code.

**File paths and change description**:
- `src/superclaude/cli/pipeline/models.py` — Add `AgentHandoffState` enum: `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`, `VALIDATED`. This enum is used by pipeline code that invokes agents sequentially (quality-engineer verification, audit pass progression).
- `src/superclaude/cli/sprint/executor.py` — At quality-engineer agent invocation sites (STRICT-tier task verification), emit `AgentHandoffState.TASK_READY` before invocation and `AgentHandoffState.EXECUTION_COMPLETE` or `AgentHandoffState.BLOCKED` after. Log these transitions to the sprint result file.
- `.claude/agents/pm-agent.md` — Document the typed handoff states: "When delegating to quality-engineer, set state to TASK_READY. After quality-engineer returns, check for BLOCKED state before proceeding."
- `src/superclaude/agents/pm-agent.md` — Sync copy.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 5: "For IC components that involve sequential agent invocation, adopt explicit typed state transitions. BLOCKED as a first-class message type prevents silent failures in agent coordination."

**Dependencies**: QA-001 (BLOCKED state from validation gate must use the same enum)
**Acceptance criteria**: `AgentHandoffState` enum exists in models.py; sprint executor emits TASK_READY before quality-engineer invocation; BLOCKED state is emitted when agent cannot proceed; pm-agent.md documents handoff states.
**Risk**: Medium. New enum and emission logic in sprint executor; requires integration test verifying state transitions are logged correctly.

---

## ITEM QA-003 — Model Tier Proportionality Policy for Quality Agents

**Priority**: P2
**Effort**: XS
**Classification**: strengthen existing code
**patterns_not_mass**: true — formalizing IC's existing tiered model usage as an explicit policy document to prevent future all-opus drift (anti-pattern from LW)
**Why not full import**: LW's all-opus mandate for all rf-* agents is the explicit anti-pattern; this item documents IC's existing tier-proportional approach as policy to prevent regression, not to adopt any LW pattern.

**File paths and change description**:
- `.claude/agents/quality-engineer.md` — Add "Model Tier Policy": "quality-engineer runs at Sonnet tier. Escalation to Opus tier is permitted only when: (a) STRICT-tier task involves cross-component dependency analysis spanning >5 files, or (b) security domain path (auth/, crypto/) is involved. Haiku tier is not appropriate for quality-engineer (insufficient depth for STRICT verification)."
- `src/superclaude/agents/quality-engineer.md` — Sync copy.
- `.claude/agents/audit-validator.md` — Add "Model Tier Policy": "audit-validator uses Haiku tier (10% spot-check validation; Sonnet-level depth is not required for random sampling)."
- `src/superclaude/agents/audit-validator.md` — Sync copy.
- `.claude/agents/self-review.md` — Add "Model Tier Policy": "self-review uses Haiku tier for routine 4-question post-implementation checks; escalate to Sonnet for STRICT-tier implementation reviews."
- `src/superclaude/agents/self-review.md` — Sync copy.

**Rationale**: D-0022 Principle 4 (Bounded Complexity), direction 1: "IC's tiered model selection should be formalized into an explicit model-selection policy. The audit-validator (10% spot-check) should not use the same model as quality-engineer (STRICT-tier deep verification)."

**Dependencies**: None
**Acceptance criteria**: All three agent .md files (quality-engineer, audit-validator, self-review) have a "Model Tier Policy" section; each specifies a primary tier and explicit escalation conditions; all dev copies are synced.
**Risk**: Low. Documentation only; no behavioral change.
