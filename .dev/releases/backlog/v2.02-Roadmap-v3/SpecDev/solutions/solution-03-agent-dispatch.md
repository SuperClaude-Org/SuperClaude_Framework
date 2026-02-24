# Solution 03: Agent Dispatch Mechanism

**Root Cause**: RC3 (Rank 5, Score 0.72) -- Agent Dispatch Mechanism
**Date**: 2026-02-22
**Author**: claude-opus-4-6 (system architect)
**Fix Reference**: Fix 2 (partial), standalone solution

---

## Problem Summary

There is no binding mechanism between skill invocations and agent definitions. The dispatch chain `sc:roadmap -> sc:adversarial -> debate-orchestrator` has three breaks:

1. **debate-orchestrator.md is passive documentation**. The file at `src/superclaude/agents/debate-orchestrator.md` contains 69 lines of behavioral specification (mindset, responsibilities, boundaries, focus areas) but is never programmatically loaded when sc:adversarial executes. Claude has no instruction to read it.

2. **`subagent_type: "general-purpose"` is a dead field**. The Task tool API has no `subagent_type` parameter. The YAML blocks at SKILL.md lines 802 and 1411 that specify `subagent_type: "general-purpose"` are documentation artifacts, not executable configuration. Claude ignores them because they correspond to nothing in the Task tool's interface.

3. **No agent bootstrap step exists**. When sc:adversarial dispatches Task agents for advocates or merge-executor, it generates prompts from templates in the SKILL.md but never reads the corresponding agent `.md` files (`debate-orchestrator.md`, `merge-executor.md`) to inject their behavioral contracts into the Task prompt.

**Contrast with working precedent**: The sc:cleanup-audit skill's agents (`audit-scanner.md`, `audit-analyzer.md`, etc.) work because they have proper frontmatter (`tools`, `model`, `maxTurns`, `permissionMode`) and are loaded natively by Claude Code's Task tool as agent definitions. The adversarial agents lack this frontmatter structure.

---

## Options Analysis

### Option A: Inline debate-orchestrator.md Content into Task Prompts

Embed the full debate-orchestrator behavioral specification directly into sc:adversarial's SKILL.md Task agent prompt templates.

| Dimension | Assessment |
|-----------|------------|
| Effort | Low -- copy 69 lines into SKILL.md prompt template |
| Maintenance | Poor -- two copies of the same behavioral spec drift independently |
| Scalability | None -- every skill that references an agent must inline it |
| Correctness | High -- Claude receives the behavioral contract directly |
| Precedent | None -- no existing skill does this |

**Critical flaw**: debate-orchestrator is NOT a sub-agent to be dispatched via Task. It is the orchestrator ROLE that sc:adversarial itself should adopt. Inlining its content into a Task prompt misidentifies the architectural relationship. The SKILL.md (1747 lines) already contains all implementation details; debate-orchestrator.md (69 lines) is the behavioral contract for how to execute them.

**Verdict**: Solves the symptom but misunderstands the architecture. Rejected.

### Option B: Convention -- Skills MUST Read Agent .md Files

Establish a framework convention: when a SKILL.md invokes the Task tool, it MUST instruct Claude to first read the corresponding agent `.md` file and include its content as system context in the Task prompt.

| Dimension | Assessment |
|-----------|------------|
| Effort | Medium -- update sc:adversarial and sc:cleanup-audit SKILL.md files |
| Maintenance | Good -- single source of truth in agent .md files |
| Scalability | Good -- convention applies to all future skills |
| Correctness | High -- agent behavioral contracts are loaded at dispatch time |
| Precedent | Partial -- cleanup-audit agents use native frontmatter, not explicit read |

**Key distinction**: This convention needs to handle TWO different agent-skill relationships:
1. **Role adoption**: sc:adversarial should READ debate-orchestrator.md and ADOPT its behavioral mindset (the SKILL.md executor becomes the orchestrator)
2. **Sub-agent dispatch**: When dispatching Task agents (advocates, merge-executor), READ the agent .md and INJECT its content into the Task prompt

**Verdict**: Architecturally sound. Makes agent files functional. Convention is simple to document.

### Option C: Agent Loader Pattern -- Reusable Template

Create a reusable "agent loader" abstraction: a Task agent prompt template that takes an agent name, reads the corresponding `.md` file, and constructs the prompt.

| Dimension | Assessment |
|-----------|------------|
| Effort | Medium-High -- design template, document pattern, update skills |
| Maintenance | Excellent -- centralized loader pattern, agent files are modular |
| Scalability | Excellent -- any skill can load any agent by name |
| Correctness | High -- standardized loading eliminates per-skill wiring errors |
| Precedent | None -- new abstraction |

**Risk**: Over-engineering. The "agent loader" is effectively a 5-line YAML block in the SKILL.md. Making it a separate reusable template adds indirection for minimal gain when only 2 skills currently use Task agents.

**Verdict**: Correct direction but premature. The convention (Option B) achieves the same result without a new abstraction layer.

### Option D: Inline Behavior, Remove Agent .md File

Remove `debate-orchestrator.md` entirely. Inline its behavioral specification directly into sc:adversarial's SKILL.md as a "Behavioral Contract" section.

| Dimension | Assessment |
|-----------|------------|
| Effort | Low -- move 69 lines, delete file |
| Maintenance | Good -- single source of truth |
| Scalability | Poor -- loses modularity, no reuse possible |
| Correctness | Medium -- merge-executor.md would also need inlining |
| Precedent | None -- contradicts the agent system's design intent |

**Critical flaw**: The agent `.md` system exists for a reason. Cleanup-audit has 5 agent files that are functionally loaded. Removing adversarial's agent files would create an inconsistency: some agents are standalone files, others are inlined into skills. This makes the agent system harder to reason about.

**Verdict**: Simplifies one case but degrades the overall architecture. Rejected.

---

## Recommended Solution: Option B -- Agent Bootstrap Convention

### Rationale

Option B is recommended because it:

1. **Makes existing agent files functional** without new infrastructure
2. **Establishes a reusable convention** that applies to future skills
3. **Correctly models both relationships**: role adoption (orchestrator) and sub-agent dispatch (advocates, merge-executor)
4. **Aligns with the working precedent**: cleanup-audit agents work because Claude Code loads their `.md` files natively; the adversarial agents need the same treatment via explicit read instructions
5. **Minimal blast radius**: Changes are confined to SKILL.md files and a convention documented once

When the framework grows to need 5+ skills using Task agents, Option C (agent loader template) can be extracted from the convention as a natural refactoring. Option B is the correct first step.

---

## Implementation Details

### System Design Diagram

```
sc:roadmap (SKILL.md)
    |
    | [1] Skill tool invocation
    v
sc:adversarial (SKILL.md)
    |
    | [2] BOOTSTRAP: Read debate-orchestrator.md
    |     Adopt behavioral mindset, responsibilities, boundaries
    |
    | [3] Execute 5-step protocol per SKILL.md implementation details
    |
    |--- Step 1: Diff Analysis (orchestrator executes directly)
    |
    |--- Step 2: Adversarial Debate
    |       |
    |       | [4] DISPATCH: Task agents for advocates
    |       |     Prompt generated from advocate_prompt_template
    |       |     (advocates are dynamic -- no agent .md files)
    |       v
    |       Advocate Agent 1 (Task)
    |       Advocate Agent 2 (Task)
    |       ...
    |
    |--- Step 3: Scoring (orchestrator executes directly)
    |
    |--- Step 4: Refactoring Plan (orchestrator executes directly)
    |
    |--- Step 5: Merge Execution
            |
            | [5] DISPATCH: Read merge-executor.md
            |     Inject behavioral contract into Task prompt
            v
            Merge Executor (Task)
```

### Change 1: Add Agent Bootstrap Section to sc:adversarial SKILL.md

**Location**: Insert after line 7 (after `allowed-tools` in frontmatter), before `## Purpose`.

Add a new top-level section that instructs Claude to load the orchestrator behavioral contract before executing the pipeline:

```yaml
## Agent Bootstrap (MANDATORY -- execute before pipeline)

Before executing any pipeline step, you MUST:

1. **Read** the orchestrator behavioral contract:
   - File: `src/superclaude/agents/debate-orchestrator.md`
   - Adopt its behavioral mindset, responsibilities, boundaries, and focus areas
   - You ARE the debate-orchestrator for this execution

2. **For merge-executor dispatch** (Step 5):
   - File: `src/superclaude/agents/merge-executor.md`
   - Read this file and include its FULL content in the Task agent prompt
   - The merge-executor agent MUST receive its behavioral contract as system context

3. **For advocate dispatch** (Step 2):
   - Advocates are dynamic agents -- no agent .md files exist
   - Use the advocate_prompt_template defined in this SKILL.md
   - This is correct: advocates are instantiated per-debate, not persistent agents
```

### Change 2: Update task_dispatch_config for Merge Executor

**Location**: SKILL.md line 1407-1416 (merge_execution.dispatch)

Replace the current dead `subagent_type: "general-purpose"` with an agent bootstrap instruction:

```yaml
merge_execution:
  dispatch:
    agent_bootstrap:
      action: "Read src/superclaude/agents/merge-executor.md"
      inject: "Include FULL file content as system context prefix in Task prompt"
      rationale: "Merge executor needs its behavioral contract to maintain plan fidelity and provenance tracking"
    via: "Task tool"
    model: "opus or sonnet (highest available)"
    prompt_structure:
      system_context: "{content of merge-executor.md}"
      task_instructions: "Execute the following refactoring plan against the base variant..."
    input:
      base_variant: "Full text of selected base variant"
      refactoring_plan: "Full text of refactor-plan.md"
    max_turns: 10
```

### Change 3: Update Advocate task_dispatch_config

**Location**: SKILL.md line 801-810 (task_dispatch_config for advocates)

Remove the dead `subagent_type` field and clarify that advocates do NOT use agent .md files:

```yaml
  task_dispatch_config:
    # Advocates are dynamic agents -- no agent .md file to bootstrap
    # Their behavioral contract is generated from the advocate_prompt_template above
    model: "{parsed_model}"
    max_turns: 5
    prompt: "{generated_prompt from advocate_prompt_template}"
    input_data:
      own_variant: "Full text of advocate's variant"
      other_variants: "Full text of all other variants"
      diff_analysis: "Full text of diff-analysis.md"
```

### Change 4: Add Agent Frontmatter to debate-orchestrator.md

**Location**: `src/superclaude/agents/debate-orchestrator.md` frontmatter (lines 1-5)

Add the same frontmatter fields that make cleanup-audit agents functional:

```yaml
---
name: debate-orchestrator
description: Coordinate adversarial debate pipeline without participating in debates
category: analysis
tools: Task, Read, Write, Glob, Grep, Bash
model: opus
maxTurns: 50
permissionMode: plan
---
```

### Change 5: Add Agent Frontmatter to merge-executor.md

**Location**: `src/superclaude/agents/merge-executor.md` frontmatter (lines 1-5)

```yaml
---
name: merge-executor
description: Execute refactoring plans to produce unified merged artifacts with provenance
category: quality
tools: Read, Write, Edit, Grep
model: sonnet
maxTurns: 10
permissionMode: plan
---
```

### Change 6: Document the Convention

**Location**: `src/superclaude/agents/README.md` (update existing stale README)

Add a section documenting the agent bootstrap convention:

```markdown
## Agent Bootstrap Convention

When a SKILL.md dispatches Task agents, it MUST follow one of two patterns:

### Pattern 1: Role Adoption (orchestrator agents)
The skill executor READS the agent .md file and ADOPTS its behavioral contract.
The agent is not spawned as a separate Task -- the skill executor BECOMES the agent.

Example: sc:adversarial reads debate-orchestrator.md and adopts its mindset.

### Pattern 2: Sub-Agent Dispatch (worker agents)
The skill executor READS the agent .md file and INJECTS its content as system
context in the Task prompt. The agent IS spawned as a separate Task.

Example: sc:adversarial reads merge-executor.md and includes it in the Task prompt.

### Pattern 3: Dynamic Agents (no .md file)
Some agents are instantiated dynamically from user-provided specifications.
Their behavioral contract is generated from prompt templates in the SKILL.md.

Example: Advocate agents in sc:adversarial are generated from --agents specs.

### Agent .md Frontmatter

All agent .md files MUST include functional frontmatter:

- name: Agent identifier
- description: One-line purpose
- tools: Comma-separated tool list
- model: Preferred model (opus, sonnet, haiku)
- maxTurns: Maximum conversation turns
- permissionMode: plan (read-only) or full
```

---

## Blast Radius Assessment

### Files Modified

| File | Change Type | Risk |
|------|------------|------|
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Add bootstrap section, update dispatch configs | Medium -- large file, but changes are additive |
| `src/superclaude/agents/debate-orchestrator.md` | Add frontmatter fields | Low -- additive only |
| `src/superclaude/agents/merge-executor.md` | Add frontmatter fields | Low -- additive only |
| `src/superclaude/agents/README.md` | Add convention documentation | Low -- documentation only |

### Files NOT Modified

| File | Reason |
|------|--------|
| `src/superclaude/skills/sc-roadmap/SKILL.md` | No changes needed -- roadmap invokes adversarial via Skill tool, not Task |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | No changes needed -- integration reference describes invocation patterns, not agent dispatch |
| `src/superclaude/skills/sc-cleanup-audit/SKILL.md` | No changes needed -- cleanup-audit agents already have proper frontmatter and are loaded natively |
| Any test files | Convention is documentation-level; no code changes required |

### Dependency Impact

- **Upstream**: sc:roadmap is unaffected. It invokes sc:adversarial via the Skill tool. The agent bootstrap happens INSIDE sc:adversarial's execution.
- **Downstream**: Advocate agents and merge-executor are affected only positively -- they receive clearer behavioral contracts.
- **Cross-cutting**: The convention documented in README.md applies to all future skills that use Task agents. Existing skills (cleanup-audit) already comply implicitly.

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Convention not followed by future skills | Medium | Low | README documentation + code review checklist |
| Bootstrap read fails (file not found) | Low | High | SKILL.md should include fallback: "If agent .md not found, proceed with SKILL.md instructions only" |
| Frontmatter breaks existing agent loading | Very Low | Medium | Frontmatter is additive; existing fields preserved |
| SKILL.md changes introduce new parsing issues | Low | Medium | Changes are in YAML documentation blocks, not executable code |

---

## Confidence Score

**Overall Confidence: 0.82**

| Factor | Score | Rationale |
|--------|-------|-----------|
| Problem understanding | 0.90 | Clear evidence chain: agent files are passive, `subagent_type` is dead, no bootstrap step exists |
| Solution correctness | 0.85 | Convention aligns with working precedent (cleanup-audit), addresses both role-adoption and sub-agent dispatch patterns |
| Implementation feasibility | 0.80 | All changes are to markdown documentation files; no code changes; risk is in Claude's behavioral interpretation of the instructions |
| Blast radius containment | 0.90 | Changes confined to 4 files; no upstream impact; convention is backward-compatible |
| Residual risk | 0.65 | The fundamental constraint remains: Claude interprets markdown instructions heuristically, not deterministically. Even with perfect bootstrap instructions, Claude may still not read the agent .md file in all cases. This is an inherent limitation of the instruction-following architecture. |

**Key uncertainty**: This solution depends on Claude reliably following the "MANDATORY: Read this file before proceeding" instruction. The cleanup-audit precedent suggests this works (Claude does read agent files when the Task tool loads them), but the agent bootstrap pattern for role adoption (Change 1) is untested. Validation requires an end-to-end test of the `sc:roadmap --multi-roadmap --agents opus,haiku` flow.

---

## Relationship to Other Fixes

This solution (Fix 2 partial) works in conjunction with:

- **Fix 1** (Solution 01 -- RC1): Adding `Skill` to allowed-tools. Without Fix 1, sc:roadmap cannot invoke sc:adversarial at all, making agent bootstrap irrelevant.
- **Fix 3** (Solution 04 -- RC4): Return contract file convention. The debate-orchestrator's final responsibility ("Compile final return contract") depends on the return contract having a defined transport mechanism.

**Implementation order**: Fix 1 MUST be applied before this solution has any observable effect. Fix 3 can be applied independently.

---

*Solution designed 2026-02-22. Analyst: claude-opus-4-6 (system architect persona).*
