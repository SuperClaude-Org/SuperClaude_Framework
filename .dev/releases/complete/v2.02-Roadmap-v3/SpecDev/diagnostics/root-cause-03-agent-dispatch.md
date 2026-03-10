# Root Cause #3: Agent Dispatch Mechanism

## Summary

There is no explicit binding mechanism between skill invocations (e.g., `sc:adversarial`) and agent definitions (e.g., `debate-orchestrator`). The SuperClaude framework relies entirely on Claude's interpretation of SKILL.md prose to determine which agent behavior to adopt, but the Task tool has no `subagent_type` parameter and agent `.md` files are not programmatically loaded during skill execution. When Claude reads sc:adversarial's SKILL.md, it encounters references to `debate-orchestrator` as a conceptual role, but has no mechanism to activate that specific agent definition file. Instead, Claude falls back to its own heuristic selection, choosing `system-architect` based on keyword affinity with the "architecture" and "design" concepts in the roadmap generation context.

## Evidence

### Available Agent Types

Complete listing of all 30 agent definition files in `src/superclaude/agents/`:

| # | File | Category | Created/Modified |
|---|------|----------|------------------|
| 1 | `audit-analyzer.md` | analysis | Feb 19 |
| 2 | `audit-comparator.md` | analysis | Feb 19 |
| 3 | `audit-consolidator.md` | analysis | Feb 19 |
| 4 | `audit-scanner.md` | analysis | Feb 19 |
| 5 | `audit-validator.md` | analysis | Feb 19 |
| 6 | `backend-architect.md` | engineering | Jan 27 |
| 7 | `business-panel-experts.md` | analysis | Jan 27 |
| 8 | `debate-orchestrator.md` | analysis | Feb 21 |
| 9 | `deep-research-agent.md` | research | Jan 27 |
| 10 | `deep-research.md` | research | Jan 27 |
| 11 | `devops-architect.md` | engineering | Jan 27 |
| 12 | `frontend-architect.md` | engineering | Jan 27 |
| 13 | `learning-guide.md` | education | Jan 27 |
| 14 | `merge-executor.md` | quality | Jan 27 (updated Feb 21) |
| 15 | `performance-engineer.md` | engineering | Jan 27 |
| 16 | `pm-agent.md` | management | Jan 27 |
| 17 | `python-expert.md` | engineering | Jan 27 |
| 18 | `quality-engineer.md` | quality | Jan 27 |
| 19 | `refactoring-expert.md` | quality | Jan 27 |
| 20 | `repo-index.md` | tooling | Jan 27 |
| 21 | `requirements-analyst.md` | analysis | Jan 27 |
| 22 | `root-cause-analyst.md` | analysis | Jan 27 |
| 23 | `security-engineer.md` | engineering | Jan 27 |
| 24 | `self-review.md` | quality | Jan 27 |
| 25 | `socratic-mentor.md` | education | Jan 27 |
| 26 | `system-architect.md` | engineering | Jan 27 |
| 27 | `technical-writer.md` | documentation | Jan 27 |

Note: The `README.md` in the agents directory is stale -- it only lists 3 agents (deep-research, repo-index, self-review) despite 30 agent files existing. This is a documentation drift issue that compounds the dispatch problem.

### debate-orchestrator Registration

**Is `debate-orchestrator` registered as a valid `subagent_type` in the Task tool?**

No. The Task tool does **not have** a `subagent_type` parameter at all. This is a documented "Critical Correction #1" that was identified during v1.4 development:

- From `SC-ROADMAP-FEATURE-SPEC.md`: *"IMPORTANT: The Task tool does NOT have a subagent_type parameter. Agent specialization must be embedded in the Task prompt itself."*
- Compliance tests (`tests/sc-roadmap/compliance/test_critical_corrections.py` and `test_task_tool_pattern.py`) explicitly verify that `subagent_type` does NOT appear as a parameter in SKILL.md call patterns.
- The sc:adversarial SKILL.md itself contains `subagent_type: "general-purpose"` in its `task_dispatch_config` YAML blocks (lines 802 and 1411), but this is **descriptive metadata** within a YAML specification block, not an actual Task tool parameter. The compliance tests specifically exclude these from violations (they only flag `subagent_type` inside `call_pattern:` blocks).

**Conclusion**: `debate-orchestrator` cannot be "registered" as a subagent type because no such registration mechanism exists. The Task tool spawns generic sub-agents whose behavior is shaped entirely by the prompt text passed to them.

### sc:adversarial -> Agent Mapping

**Any explicit mapping found?**

No explicit programmatic mapping exists. The connection between `sc:adversarial` and `debate-orchestrator` is expressed only through:

1. **Prose in SKILL.md** (lines 105, 144, 204, 354-366): The skill mentions `debate-orchestrator` by name in delegation notes:
   - *"Delegation: debate-orchestrator agent coordinates; advocate agents participate"*
   - *"### debate-orchestrator Agent"* section describing its role

2. **Agent definition file** (`src/superclaude/agents/debate-orchestrator.md`, line 10): The agent says *"Invoked by /sc:adversarial command to coordinate the 5-step adversarial pipeline"*

3. **The `task_dispatch_config` blocks** (SKILL.md lines 801-809, 1407-1417): These specify `subagent_type: "general-purpose"` -- they do NOT specify `subagent_type: "debate-orchestrator"`. This means even the SKILL.md's own dispatch configuration does not reference the debate-orchestrator agent.

**What is missing**:
- No code-level registry mapping skill names to agent types
- No configuration file associating `sc:adversarial` with `debate-orchestrator`
- No mechanism to load `debate-orchestrator.md` content as the system prompt for Task-spawned agents
- No CLI handler that routes skill invocations to specific agent files
- The `adversarial-integration.md` reference (loaded by sc:roadmap during Wave 2) makes zero mention of `debate-orchestrator` -- it describes invocation patterns and return contracts but not agent selection

### system-architect Selection

**Why was `system-architect` chosen instead of `debate-orchestrator`?**

The evidence points to Claude's heuristic keyword matching as the cause:

1. **Context saturation with architecture keywords**: When sc:roadmap invokes sc:adversarial with `--generate roadmap`, the context is saturated with terms like "architecture", "design", "scalability", "system" -- all of which are trigger keywords for the `system-architect` agent (per its definition: *"System architecture design and scalability analysis needs"*, *"Architectural pattern evaluation and technology selection decisions"*).

2. **The `--agents opus,haiku` flag interpretation**: The `--agents` flag specifies model identifiers, not agent types. Claude likely interpreted the need to spawn Task agents with `opus` and `haiku` models, then selected `system-architect` as the behavioral template because:
   - The task involved generating "roadmap" artifacts (architecture-adjacent)
   - The `system-architect` agent's triggers include *"Long-term technical strategy"* which aligns with roadmap generation
   - No instruction in the prompt chain explicitly said "use debate-orchestrator behavior"

3. **`system-architect` as a heuristic default**: The `system-architect` agent is a general-purpose engineering agent that appears broadly applicable. In the absence of explicit agent routing, Claude's persona auto-activation system (PERSONAS.md, ORCHESTRATOR.md) would score `system-architect` highly for any task involving system-level analysis and planning.

4. **The `general-purpose` dispatch config**: The SKILL.md specifies `subagent_type: "general-purpose"` in its task dispatch configuration. This tells Claude to spawn a generic agent, not to look for a specific agent definition file.

5. **Research file evidence**: `docs/research/parallel-execution-findings.md` (line 234) shows historical pseudocode using `subagent_type="system-architect"` as an example of Task-based parallelism. This suggests `system-architect` may have been a commonly used agent type in the project's development history, reinforcing Claude's tendency to select it.

## Analysis

The agent dispatch failure is a **systemic architecture gap**, not a one-off bug. The SuperClaude framework has two disconnected layers:

### Layer 1: Agent Definition Files (Passive)
Agent `.md` files in `src/superclaude/agents/` are **passive documentation**. They define triggers, behavioral mindsets, tools, and boundaries for specialized agents. However, they are never programmatically loaded, never registered in a lookup table, and never automatically injected into Task tool prompts.

### Layer 2: Skill Execution (Active)
Skills (SKILL.md files) describe multi-step protocols with delegation patterns. When they say "delegate to debate-orchestrator", this is a **natural language instruction to Claude**, not a function call. Claude must:
1. Read the skill and understand the intent
2. Find the correct agent definition file
3. Load its content
4. Embed it into the Task tool prompt

Steps 2-4 have no automated mechanism. Claude must discover and load agent files through its own initiative (using Read/Glob tools), which requires:
- Knowing that agent files exist in `src/superclaude/agents/`
- Knowing which agent file corresponds to the current skill context
- Choosing to read the file before spawning Task agents
- Embedding the agent definition content into the Task prompt

In practice, this chain of inference breaks down. Claude encounters the skill, sees the delegation instruction, but lacks a reliable path from "delegate to debate-orchestrator" to "read `src/superclaude/agents/debate-orchestrator.md` and embed its content as the system prompt for the Task agent." Instead, Claude falls back to its built-in persona system and keyword matching, selecting `system-architect` because it best matches the roadmap-generation context.

### The Critical Gap

The `adversarial-integration.md` reference file -- which is the primary document sc:roadmap loads when invoking sc:adversarial in Wave 2 -- **does not mention debate-orchestrator at all**. It describes:
- Mode detection
- Agent specification parsing
- Invocation patterns (command-line format)
- Return contract consumption
- Error handling

But it never says: "The sc:adversarial invocation should spawn a debate-orchestrator agent." It assumes this happens automatically through the skill system, but the skill system has no automation for agent dispatch.

### Compounding Factor: Stale README

The `src/superclaude/agents/README.md` only lists 3 agents (deep-research, repo-index, self-review) despite 30 agent files existing in the directory. If Claude consulted this README for agent discovery, it would not find `debate-orchestrator` listed at all.

## Likelihood Score: 0.95/1.0

**Justification**: This is almost certainly a contributing root cause. The evidence chain is clear:
- No programmatic agent dispatch mechanism exists
- The Task tool has no `subagent_type` parameter (confirmed by compliance tests)
- The SKILL.md uses `subagent_type: "general-purpose"` instead of referencing debate-orchestrator
- The adversarial-integration.md (the ref file loaded during Wave 2) never mentions debate-orchestrator
- system-architect's keyword triggers align strongly with roadmap generation context

The only scenario where this is NOT the cause is if Claude never attempted to spawn Task agents at all (i.e., the failure happened at a different level). But the problem statement confirms system-architect agents WERE spawned, which directly implicates the agent selection mechanism.

## Impact Score: 0.90/1.0

**Justification**: This root cause explains the primary failure symptom (wrong agent type spawned) and has cascading effects:
- Without debate-orchestrator behavior, the 5-step adversarial protocol is not followed
- system-architect agents would perform architecture analysis instead of structured debate
- The scoring algorithm, convergence tracking, and merge coordination would all be absent
- The return contract would not be properly compiled

However, it does not fully explain other potential failures (e.g., whether sc:adversarial was even invoked correctly by sc:roadmap, or whether the return contract was properly consumed). Those may have separate root causes.

## Recommendation

### Short-term Fix (High Priority)

**Option A: Explicit Agent Loading Instructions in SKILL.md**

Add explicit instructions to the sc:adversarial SKILL.md that tell Claude to:
1. Read `src/superclaude/agents/debate-orchestrator.md` at pipeline start
2. Embed its content as behavioral instructions in the orchestration context
3. Read `src/superclaude/agents/merge-executor.md` before Step 5

This would look like adding a "Bootstrap" or "Agent Loading" step before Step 1:

```yaml
agent_bootstrap:
  step_0:
    action: "Read agent definition files before pipeline execution"
    load:
      - path: "src/superclaude/agents/debate-orchestrator.md"
        role: "Pipeline orchestrator behavioral instructions"
      - path: "src/superclaude/agents/merge-executor.md"
        role: "Step 5 merge executor behavioral instructions"
    embed: "Include loaded agent definitions in Task tool prompts when delegating"
```

**Option B: Embed Agent Behavior Directly in SKILL.md**

Instead of referencing external agent files, embed the critical behavioral instructions from `debate-orchestrator.md` directly into the SKILL.md's delegation sections. This eliminates the file-loading dependency entirely.

### Medium-term Fix

**Option C: Agent Registry in `refs/` Directory**

Create a `refs/agent-registry.md` file within the skill that maps delegation roles to agent file paths:

```yaml
agent_registry:
  orchestrator:
    file: "src/superclaude/agents/debate-orchestrator.md"
    load_at: "pipeline start"
  merge_executor:
    file: "src/superclaude/agents/merge-executor.md"
    load_at: "step 5"
  advocate:
    generation: "dynamic from --agents spec"
    load_at: "step 2"
```

### Long-term Fix

**Option D: Framework-Level Agent Dispatch (v5.0)**

Implement a proper agent dispatch system in the TypeScript plugin architecture planned for v5.0, with:
- Agent registry with skill-to-agent mappings
- Automatic agent definition loading when skills are invoked
- Task tool integration that injects agent definitions into sub-agent prompts

### Additional: Update Stale README

Update `src/superclaude/agents/README.md` to list all 30 agent files with their categories, replacing the current 3-agent listing.

---

*Investigation performed: 2026-02-22*
*Files examined: 30 agent definitions, SKILL.md (sc-adversarial), SKILL.md (sc-roadmap), adversarial-integration.md, test_critical_corrections.py, test_task_tool_pattern.py, parallel-execution-findings.md, agents/README.md*
*Analyst: Root Cause Analyst (claude-opus-4-6)*
