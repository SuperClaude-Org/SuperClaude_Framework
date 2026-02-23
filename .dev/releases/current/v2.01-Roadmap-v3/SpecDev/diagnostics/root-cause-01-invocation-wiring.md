# Root Cause #1: Invocation Wiring Gap

## Summary

The SKILL.md instruction "Invoke sc:adversarial" in Wave 2 is aspirational natural language text that has no executable binding to Claude Code's Skill tool. There is no mechanism in the SuperClaude framework -- or in Claude Code's runtime -- for one skill to programmatically invoke another skill during execution. The instruction is interpreted as prose guidance, not as a tool call directive.

## Evidence

### Evidence 1: The failing instruction (sc-roadmap SKILL.md, line 137)

The Wave 2 behavioral instruction reads:

```
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from
   `refs/adversarial-integration.md` "Agent Specification Parsing" section.
   Expand model-only agents with the primary persona from Wave 1B. If agent
   count >=5, orchestrator is added automatically. Invoke sc:adversarial for
   multi-roadmap generation per `refs/adversarial-integration.md`
   "Multi-Roadmap Generation" invocation pattern. Handle return contract per
   `refs/adversarial-integration.md` "Return Contract Consumption" section.
   The adversarial output replaces template-based generation.
```

This is a natural language behavioral instruction embedded in markdown. It tells Claude what to do conceptually ("Invoke sc:adversarial") but does not specify HOW to invoke it -- there is no tool-call syntax, no explicit reference to the Skill tool, and no programmatic mechanism.

### Evidence 2: The Skill tool's design constraint

The Skill tool (defined in the system prompt) has the following description:

> "Execute a skill within the main conversation. When users ask you to perform tasks, check if any of the available skills match."

And critically:

> "If you see a `<command-name>` tag in the current conversation turn, the skill has ALREADY been loaded -- follow the instructions directly instead of calling this tool again."

This reveals that the Skill tool is designed for **user-initiated invocation**, not for skill-to-skill chaining. When a skill is loaded via the Skill tool, its SKILL.md content is injected into the conversation context as behavioral instructions. The executing model (Claude) then follows those instructions. But the instructions are just text -- they do not have the ability to call the Skill tool themselves.

The key constraint: **a loaded skill's behavioral instructions are consumed as prose by the model**. The instruction "Invoke sc:adversarial" is read by Claude as guidance about what it should do, but there is no enforced mechanism that translates this prose into an actual Skill tool call.

### Evidence 3: No precedent for skill-to-skill invocation in the codebase

A comprehensive search of all SKILL.md files in `src/superclaude/skills/` found:

- **sc-roadmap** references `sc:adversarial` (the case under investigation)
- **sc-roadmap** references `sc:save` (a slash command, not a skill)
- **sc-adversarial** mentions "Called by `/sc:roadmap`" in its Triggers section (line 37)
- **sc-adversarial** describes a generic integration pattern (line 1582): "Any command can invoke sc:adversarial and consume the return contract"

**Zero instances** of any SKILL.md containing explicit Skill tool call syntax (e.g., "Use the Skill tool with skill='sc:adversarial'"). All cross-skill references use natural language like "Invoke", "Call", or "Trigger".

### Evidence 4: `sc:save` is a command, not a skill -- revealing a category confusion

sc:roadmap's exit criteria repeatedly say "Trigger `sc:save`" (lines 90, 110, 128, 143, 166, 184). However:

- `sc:save` is a **slash command** (`src/superclaude/commands/save.md`), not a skill
- `sc:adversarial` exists as both a **slash command** (`src/superclaude/commands/adversarial.md`) AND a **skill** (`src/superclaude/skills/sc-adversarial/SKILL.md`)

The SKILL.md instructions conflate two different invocation mechanisms:
1. Slash commands (`.claude/commands/sc/save.md`) -- invoked by users typing `/sc:save`
2. Skills (`.claude/skills/sc-adversarial/SKILL.md`) -- invoked via the Skill tool

Neither mechanism supports being called from within another skill's execution context.

### Evidence 5: The return contract assumes structured data flow that cannot exist

`refs/adversarial-integration.md` defines a detailed return contract (lines 139-186):

```yaml
return_contract:
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list of unresolved items>"]
```

And routing logic:
```
status == "success" -> Use merged_output_path as input for subsequent waves
status == "partial" -> Check convergence_score >= 60%
status == "failed" -> Abort roadmap generation
```

This contract assumes sc:adversarial can **return structured data** to sc:roadmap's execution context. But the Skill tool has no return value mechanism -- it loads a skill's instructions into the conversation. There is no structured data channel between skills. Claude could theoretically write the return contract to a file, but the SKILL.md instructions do not specify this intermediary mechanism.

### Evidence 6: The Skill tool explicitly warns against re-invocation

The Skill tool description states:

> "Do not invoke a skill that is already running"

This implies skills are mutually exclusive, single-occupancy execution contexts. If sc:roadmap is "running" (its instructions are loaded), invoking sc:adversarial via the Skill tool would either replace the running skill's context or be blocked.

## Analysis

The root cause is a **semantic gap** between three layers:

1. **Design intent** (refs/adversarial-integration.md): Specifies precise invocation formats, parameter mapping, return contracts, and error handling -- as if skills were callable functions with typed interfaces.

2. **Behavioral instruction** (SKILL.md line 137): Says "Invoke sc:adversarial" as a natural language directive -- which Claude reads as guidance but has no enforced way to execute.

3. **Runtime capability** (Claude Code Skill tool): Provides user-initiated skill loading only. No skill-to-skill invocation API. No structured return channel. No re-entrant skill execution.

The design documents (adversarial-integration.md, the return contract in sc-adversarial SKILL.md) are written as though a function-call interface exists between skills. The sc:adversarial SKILL.md even has an "integration_pattern" section (lines 1561-1588) that says "Any command can invoke sc:adversarial and consume the return contract." But no such invocation mechanism exists in Claude Code's skill system.

When Claude encounters the instruction "Invoke sc:adversarial" during Wave 2 execution, it faces an unresolvable ambiguity:

- It could call the Skill tool -- but that would load sc:adversarial's SKILL.md, potentially displacing the currently-running sc:roadmap context, and it has no way to "return" to sc:roadmap afterward with structured data.
- It could spawn a Task agent to run sc:adversarial -- but the SKILL.md does not instruct this, and Task agents cannot invoke the Skill tool themselves.
- It could attempt to inline the adversarial behavior -- but sc:adversarial is a 1700+ line skill with its own wave structure, far too complex to inline.
- It could skip the instruction -- which is what likely happened.

The most probable runtime behavior: Claude recognized it could not fulfill "Invoke sc:adversarial" through any available mechanism, and either silently skipped the step or fell through to step 4 ("Otherwise: create milestone structure based on complexity class"), treating the `--multi-roadmap` branch as a no-op.

## Likelihood Score: 0.95/1.0

This is almost certainly the root cause. The evidence chain is complete:
- The instruction uses natural language, not tool-call syntax
- No skill-to-skill invocation mechanism exists in the framework
- No precedent exists in any other skill
- The Skill tool explicitly prevents re-invocation while a skill is running
- The return contract assumes data flow capabilities that do not exist

The 0.05 uncertainty accounts for the possibility that a specific Claude model version might have attempted a creative workaround (e.g., calling the Skill tool anyway, or inlining the behavior) that failed for a secondary reason.

## Impact Score: 1.0/1.0

This fully explains the observed failure. If sc:adversarial cannot be invoked from within sc:roadmap, then `--multi-roadmap --agents opus,haiku` can never work as designed. The entire adversarial pipeline (agent parsing, variant generation, debate rounds, scoring, merge, return contract consumption) is unreachable. Wave 2 has no path from the instruction "Invoke sc:adversarial" to actual execution of the adversarial skill.

## Recommendation

Three approaches, from simplest to most robust:

### Option A: Explicit Skill Tool Call Syntax (Minimal Change)

Rewrite SKILL.md line 137 to contain an explicit instruction for Claude to use the Skill tool:

```markdown
3. If `--multi-roadmap`: ... Use the Skill tool to invoke sc:adversarial
   with args: `--source <spec-path> --generate roadmap --agents <expanded-specs>
   --depth <depth> --output <output-dir>`. After sc:adversarial completes,
   read the return contract from `<output-dir>/adversarial/return-contract.yaml`.
```

**Risk**: The Skill tool says "Do not invoke a skill that is already running." This may cause the invocation to fail or displace sc:roadmap's context. Additionally, there is no file-based return contract mechanism defined in sc:adversarial.

### Option B: Task Agent Delegation (Recommended)

Replace the "Invoke sc:adversarial" instruction with a Task agent delegation pattern:

```markdown
3. If `--multi-roadmap`: ... Spawn a Task agent with the following prompt:
   "You are the adversarial orchestrator. Load skill sc:adversarial and execute
   with flags: --source <spec-path> --generate roadmap --agents <expanded-specs>
   --depth <depth> --output <output-dir>. Write the return contract to
   <output-dir>/adversarial/return-contract.yaml when complete."
   Wait for the Task agent to complete. Read return-contract.yaml and proceed
   with status routing per refs/adversarial-integration.md.
```

**Advantage**: Task agents have their own execution context and can invoke the Skill tool independently. The file-based return contract provides a concrete data channel.

**Risk**: Task agent timeout limits may be insufficient for deep adversarial debates with 5+ agents.

### Option C: Inline Behavioral Merge (Fallback)

If skill-to-skill invocation proves fundamentally impossible, merge the relevant adversarial behavior directly into sc:roadmap's Wave 2 instructions. Extract the core adversarial loop (variant generation, diff analysis, debate, scoring, merge) into a `refs/adversarial-inline.md` reference document that sc:roadmap loads directly.

**Advantage**: No cross-skill invocation needed.

**Risk**: Duplicates logic, increases sc:roadmap's complexity, makes independent adversarial usage harder to maintain.

### Additional Required Fix

Regardless of which option is chosen, the **return contract** must be concretized into a file-based mechanism. The current design assumes structured data can flow between skills in-memory, which is not possible. Define a `return-contract.yaml` file schema and write/read pattern that both skills use.
