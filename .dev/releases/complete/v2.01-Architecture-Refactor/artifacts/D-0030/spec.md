# D-0030 — Spec: Cross-Skill Invocation Patterns

**Task**: T06.01
**Date**: 2026-02-24
**Status**: COMPLETE
**Tier**: STANDARD

## Purpose

Documents the 3 cross-skill invocation patterns available in the SuperClaude framework. This specification addresses policy gap #2 from sprint-spec §16: "Cross-skill invocation not specified."

## Pattern 1: Task Agent Wrapper (Dispatch)

**Mechanism**: Use the `Task` tool to spawn a fresh sub-agent that loads the target skill.

**When to Use**:
- One protocol skill needs to invoke a different protocol skill (e.g., `sc:roadmap-protocol` invoking `sc:adversarial-protocol`)
- The target skill is heavyweight and would consume too much context in the current agent
- You need parallel execution of multiple skill invocations
- Re-entry block prevents direct Skill tool usage (see Pattern 2 constraints)

**How It Works**:
1. The calling protocol dispatches a Task agent with `subagent_type` appropriate to the work
2. The Task agent prompt instructs the sub-agent to invoke `Skill sc:<target>-protocol`
3. The sub-agent loads the target SKILL.md, executes the protocol, and returns results
4. Structured output (return contracts, artifacts) is written to disk; the Task agent returns a prose summary

**Return Contract Handling**:
- The sub-agent writes structured output (e.g., return contracts) to a specified file path
- The calling protocol reads the file after the Task agent completes
- The calling protocol applies its own routing logic to the return contract

**Canonical Pattern** (from D-0027 glossary):
```
Dispatch <agent-type> agent [using Task tool]
  → Sub-agent invokes: Skill sc:<target>-protocol
  → Sub-agent writes output to: <specified-path>
  → Caller reads output via: Read tool
```

**Example**: `sc:roadmap-protocol` Wave 2 dispatches adversarial debate:
```
Task(subagent_type="debate-orchestrator",
     prompt="Invoke Skill sc:adversarial-protocol with --compare ...")
→ debate-orchestrator loads adversarial protocol
→ Executes 5-step pipeline
→ Writes return contract to artifacts/
→ Roadmap protocol reads return contract and routes (PASS/PARTIAL/FAIL)
```

## Pattern 2: Skill Tool Direct (Invoke)

**Mechanism**: Use the `Skill` tool to load a target skill directly into the current agent context.

**When to Use**:
- A command file needs to load its paired protocol skill (primary use case)
- The invocation is Tier 0 → Tier 1 (command → protocol), not skill → skill
- The target skill context is needed in the current agent's conversation

**How It Works**:
1. The command file's `## Activation` section instructs: `Skill sc:<name>-protocol`
2. Claude Code loads the SKILL.md content into the current conversation context
3. The agent now has the full protocol specification and executes it

**Re-Entry Deadlock Risk**:
- **CRITICAL**: Skill-to-skill chaining via the Skill tool may trigger a re-entry block
- If `sc:A-protocol` (already loaded via Skill tool) attempts to `Skill sc:B-protocol`, the second Skill invocation may fail or deadlock
- This is because the Skill tool loads content into the *current* context — a second Skill invocation would attempt to load into an already-specialized context
- **Mitigation**: Always use Pattern 1 (Task agent wrapper) for cross-skill invocation. Pattern 2 is only for command → protocol loading.

**Canonical Pattern** (from D-0027 glossary):
```
Invoke Skill sc:<name>-protocol
```

**Constraint**: One Skill invocation per agent context. Do not chain Skill calls.

## Pattern 3: `claude -p` Script (Deferred)

**Mechanism**: Use the `claude -p` CLI command with `--append-system-prompt` to spawn a headless sub-agent with injected SKILL.md content.

**Current Status**: **UNFINALIZED** — Design only. See T06.02 (D-0031) for the design document. Implementation deferred to v2.02.

**When to Use** (proposed):
- Tier 2 ref file loading (injecting reference material into agent context)
- Headless execution of skills in CI/CD pipelines
- Batch processing where multiple skill invocations are needed without interactive context

**How It Works** (proposed design):
1. Shell script wrapper reads the target SKILL.md
2. Invokes `claude -p --append-system-prompt "$(cat SKILL.md)" "<prompt>"`
3. The spawned agent receives the SKILL.md as system prompt context
4. Agent executes the protocol and writes output to disk

**T01.01 Probe Findings** (from D-0001):
- `claude` binary is available at `/config/.local/bin/claude` (v2.1.52)
- Binary existence confirmed but `claude -p` runtime behavior with large SKILL.md payloads is **unverified**
- Sandbox restrictions on subprocess execution may affect viability

**Design Considerations** (to be addressed in D-0031):
- SKILL.md injection size limits (some skills exceed 1000 lines)
- `TOOL_NOT_AVAILABLE` error handling when injected skill references tools not available in `claude -p` context
- File system interaction: does the `claude -p` agent have the same working directory access?
- Return contract: how does the caller receive structured output?

## Decision Rule: Choosing Between Patterns

```
Is this command → protocol loading?
  YES → Pattern 2 (Skill tool direct)
  NO  ↓

Is this skill → skill invocation?
  YES → Pattern 1 (Task agent wrapper)
  NO  ↓

Is this headless/CI execution?
  YES → Pattern 3 (claude -p) — DEFERRED, use Pattern 1 as interim
  NO  → Pattern 1 (Task agent wrapper) — default for cross-skill
```

**Priority Order**:
1. **Pattern 2** for command → protocol (always first choice for Tier 0 → Tier 1)
2. **Pattern 1** for skill → skill (avoids re-entry block, supports return contracts)
3. **Pattern 3** deferred to v2.02 (unverified runtime behavior)

## Consistency with Sprint-Spec §8

This specification is consistent with sprint-spec §8 "Task Agent vs Skill Tool vs claude -p" table:
- Skill tool = "Invoke skill directly in current context" → Pattern 2
- Task tool = "Delegate to sub-agent in fresh context" → Pattern 1
- `claude -p` = "Inject ref/detail into current context" → Pattern 3

## Consistency with D-0027 Glossary

All patterns use the verb bindings established in D-0027:
- **Invoke** → Skill tool (Pattern 2)
- **Dispatch** → Task tool (Pattern 1)
- **Load** → Read tool (for return contract file reading in Pattern 1)

*Artifact produced by T06.01*
