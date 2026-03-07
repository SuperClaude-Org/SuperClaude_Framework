# RCA Agent 2: Protocol and Command File Changes

## Problem Summary

After restructuring `task-unified.md` from 567 lines (self-contained monolith) to 107 lines (slim command + Skill delegation), ALL behavioral tests timeout at 100% failure rate. Classification tests (B1-B4) produce "TIMEOUT after 225-300s" and wiring tests (W1-W4) produce "TIMEOUT after 270-600s". The timeouts exactly match the computed ceiling: `per_turn_seconds x max_turns`.

---

## Investigation Angle 1: 107-Line Command File Overhead and Duplication

### Findings

The restructuring introduced a **duplication problem** between the command file and the Skill file:

**Command file (`task-unified.md`, lines 46-66)** contains:
- Full classification header template (lines 49-56)
- Complete tier rules with keywords, compounds, and context triggers (lines 59-63)
- "MANDATORY FIRST OUTPUT" instruction (line 46)
- "Before ANY text, emit this exact header" (line 48)

**Skill file (`SKILL.md`, lines 7-98)** contains:
- The SAME classification header template (lines 9-17)
- The SAME "MANDATORY FIRST OUTPUT" instruction (line 7)
- The SAME tier classification rules, expanded (lines 100-121)
- Additional examples of completed headers (lines 71-90)
- Six explicit "Rules" for when to output the header (lines 92-98)

The model sees the classification requirement **three times**: once in the command (lines 46-66), once in the Skill warning banner (line 7), and once in Skill Section 0 (lines 57-69). This triplication does not just waste context -- it creates an ambiguity about WHEN the model should classify. The command says "before ANY text" but also says "invoke Skill" on line 70. The Skill then says "MANDATORY FIRST OUTPUT" again, potentially causing the model to attempt re-classification or second-guess its first classification.

### Evidence

- The **previous 567-line version** had NO "MANDATORY FIRST OUTPUT" instruction (grep confirms only "VERIFICATION (MANDATORY)" at line 179)
- The previous version had NO Skill invocation -- it was entirely self-contained
- The previous version had NO `allowed-tools` in frontmatter
- The current version added ALL THREE of these features simultaneously

---

## Investigation Angle 2: "MANDATORY FIRST OUTPUT" Instruction Creates Tool-Call Loop

### Findings

This is the **most likely primary root cause**.

The command file line 48 says: "Before ANY text, emit this exact header." But the command frontmatter (line 6) also declares `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill`. When Claude Code loads this command in `-p` mode, the model sees:

1. A task description: "fix security vulnerability in auth module"
2. Instructions to classify it into a tier (STRICT/STANDARD/LIGHT/EXEMPT)
3. A list of 9 available tools
4. Instructions to invoke a Skill
5. A list of 6 MCP servers
6. 10 persona references

The model interprets the task description as a real task requiring action. Before it can classify, it may decide it needs context -- what auth module? What files? So it begins making tool calls:

- **Turn 1**: Tries to `Read` or `Grep` to find the auth module
- **Turn 2**: Tries to invoke `Skill sc:task-unified-protocol`
- **Turn 3**: Skill loads 308 lines of protocol, model follows it (activate_project, git status, etc.)
- **Turn 4-5**: More tool calls following the STRICT tier protocol steps (codebase-retrieval, list_memories, etc.)

All 5 turns are consumed by tool calls. No text output is ever produced. The process hits the timeout ceiling.

### Evidence

- **Timeout values match exactly**: B1-opus = 225s = 45s/turn x 5 turns. B1-sonnet = 300s = 60s/turn x 5 turns. This means the process ran for the FULL duration with all turns consumed.
- **Classification scores are all 0.0**: No header, no tier, no confidence, no keywords were found in output. The model produced zero parseable text.
- **Wiring scores are 0.15**: Only `no_raw_dump = 1.0` passes (the command file was NOT echoed verbatim, meaning the model engaged with it rather than dumping it). `skill_invoked = 0.0`, `protocol_flow = 0.0`, `tool_engagement = 0.0` all failed.
- **100% failure rate across both models (sonnet, opus)**: Not a model-capability issue; both models exhibit identical behavior, suggesting the command structure itself is driving the behavior.
- **Previous version had NO allowed-tools**: Without `allowed-tools` in frontmatter, the previous version gave the model no tools to call, so it would produce text output directly.

### Mechanism

The fundamental conflict is:

```
"Before ANY text, emit this exact header"  (wants: immediate text output)
    +
"allowed-tools: Read, Glob, Grep, ..."     (enables: tool calls before text)
    +
"> Skill sc:task-unified-protocol"          (wants: tool call to load skill)
```

These three instructions are contradictory. The model cannot simultaneously "emit text before ANY text" AND "invoke the Skill tool" AND "use allowed tools to gather context." In practice, the tool-call path wins because the model sees the task description as requiring investigation.

---

## Investigation Angle 3: Skill Tool Behavior in `-p` Mode

### Findings

The command file line 70 contains: `> Skill sc:task-unified-protocol`. In Claude Code, this is a Skill invocation directive. When the model encounters this in `-p` mode:

1. The model calls the `Skill` tool with argument `sc:task-unified-protocol`
2. Claude Code looks up the skill in `.claude/skills/sc-task-unified-protocol/SKILL.md`
3. The 308-line SKILL.md content is loaded into the model's context
4. The model now has BOTH the command file AND the skill file instructions

This creates a **context cascade**: the 107-line command + 308-line skill = 415 lines of instructions, which is actually close to the original 567-line file but with critical structural problems:

- **Duplicated classification instructions** (as detailed in Angle 1)
- **Contradictory sequencing**: Command says "classify first, then invoke skill." Skill says "classify first, then execute." The model has already classified (or tried to) before the Skill loaded, but the Skill tells it to classify again.
- **Skill loads a multi-step protocol** that references tools like `mcp__serena__activate_project`, `codebase-retrieval`, `list_memories`, `read_memory`, `pytest`, `quality-engineer sub-agent` -- each of which would consume a turn.

If the Skill tool invocation succeeds, the model then attempts to follow the STRICT tier protocol (lines 144-156 of SKILL.md), which has 11 steps. With only 4 remaining turns (1 consumed by Skill invocation), the model cannot complete the protocol and runs out of turns.

If the Skill tool invocation fails or is not supported in `-p` mode, the model may retry it, consuming additional turns.

### Evidence

- The Skill file's STRICT execution checklist (lines 144-156) has 11 mandatory steps
- With `max_turns=5` and 1 turn consumed by Skill invocation, only 4 turns remain
- Each step in the protocol requires a tool call (activate_project, git status, codebase-retrieval, etc.)
- The model would need approximately 11+ turns to complete the protocol, but only 5 are available

---

## Investigation Angle 4: MCP Server Connection Overhead Under Concurrency

### Findings

The command frontmatter lists 6 MCP servers: `[sequential, context7, serena, playwright, magic, morphllm]`. The orchestrator runs up to 30 concurrent `claude -p` processes. This creates:

- 30 processes x 6 MCP servers = 180 potential connection attempts
- Each MCP server connection could add 5-30 seconds of startup time
- If MCP servers are unavailable or rate-limited, connection retries would add delay

However, this is likely a **contributing factor, not a root cause**:

- MCP server connection happens at `claude -p` startup, before any turns are consumed
- Even without MCP overhead, the tool-call exhaustion (Angle 2) would still cause timeouts
- The timeout values match `per_turn x max_turns` exactly, suggesting the turns ARE being consumed (not that startup is slow)

### Evidence

- The SKILL.md protocol (line 199) explicitly states: "STRICT: Sequential, Serena (fallback not allowed)" -- meaning if these servers are unavailable, the model should BLOCK, not proceed
- With 30 concurrent processes, server contention is plausible
- However, both opus and sonnet show identical 100% failure, suggesting the issue is structural, not resource-based

---

## Investigation Angle 5: Slash Command Recognition in `-p` Mode

### Findings

The orchestrator constructs prompts like: `/sc:task "fix security vulnerability in auth module"`. In `claude -p` mode, Claude Code DOES recognize slash commands (confirmed by the `--disable-slash-commands` flag existing in `claude --help`). So the command IS being loaded.

The evidence confirms this: wiring test `no_raw_dump = 1.0` means the command file was NOT echoed as raw text. The model engaged with the command content rather than treating it as a plain-text prompt.

However, there is a subtle issue: in `-p` mode, the prompt is the ENTIRE input. The model sees `/sc:task "fix security vulnerability in auth module"` as both a command invocation AND a task to execute. The command file's "MANDATORY FIRST OUTPUT" instruction competes with the model's instinct to actually fix the security vulnerability.

### Evidence

- `no_raw_dump = 1.0` across all W tests: command was recognized, not dumped
- `skill_invoked = 0.0`: despite recognition, the Skill invocation was not reflected in output
- The previous version (567 lines, no Skill) would have been self-contained and not required a Skill tool call

---

## Investigation Angle 6: `allowed-tools` in Frontmatter Enables Turn Consumption

### Findings

The previous version of `task-unified.md` had NO `allowed-tools` field in its frontmatter. The current version adds:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

This is critical. In Claude Code, the `allowed-tools` frontmatter field tells the system which tools the model may use when executing this command. By listing 9 tools (including `Task` for sub-agent delegation and `Skill` for skill invocation), the command **explicitly enables** the model to make tool calls.

Combined with the task description ("fix security vulnerability"), the model has both the TOOLS and the MOTIVATION to start making tool calls instead of producing text output.

The previous 567-line version, having no `allowed-tools`, would have forced the model to produce text output directly -- which is exactly what the classification tests expect.

### Evidence

- `git show HEAD~3:src/superclaude/commands/task-unified.md | head -15` confirms NO `allowed-tools` in previous frontmatter
- Current version line 6: `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill`
- This is the ONLY structural change that directly enables tool-call consumption of turns

---

## Top 3 Contributing Factors (Ranked by Likelihood)

### #1: Tool-Call Exhaustion from `allowed-tools` + "MANDATORY FIRST OUTPUT" Conflict (95% confidence)

**The primary root cause.** Adding `allowed-tools` to the frontmatter enabled the model to make tool calls. The "Before ANY text" instruction is contradicted by the presence of tools and a task description that implies investigation. The model consumes all `max_turns` making tool calls (Read, Grep, Skill invocation, etc.) and never produces text output.

**Key evidence:**
- Previous version: no `allowed-tools` = model produces text = tests pass
- Current version: `allowed-tools` added = model makes tool calls = tests timeout
- Timeouts match `per_turn x max_turns` exactly = all turns consumed
- 100% failure rate across both models = structural, not capability issue
- Classification scores all 0.0 = zero text output produced

**Proposed experiment:**
1. Create a stripped-down `task-unified.md` with NO `allowed-tools` in frontmatter and NO Skill invocation
2. Run B1-B4 classification tests with this version
3. If tests pass, `allowed-tools` is confirmed as the root cause
4. Alternatively, reduce `allowed-tools` to just `Skill` and test again

### #2: Skill Invocation Creates Cascading Protocol That Exceeds Turn Budget (85% confidence)

**A strong secondary cause.** Even if the model correctly outputs the classification header on Turn 1, it then invokes the Skill tool on Turn 2 (as instructed by line 70). The Skill loads 308 lines of protocol with 11+ mandatory steps for STRICT tier. The model attempts to follow these steps, consuming Turns 3-5 without completing the protocol.

**Key evidence:**
- SKILL.md STRICT execution has 11 steps, each requiring a tool call
- `max_turns=5` with 1 turn for classification + 1 turn for Skill invocation = only 3 turns for protocol
- 3 turns is insufficient for 11 steps
- Skill file duplicates the classification requirement, potentially causing re-classification

**Proposed experiment:**
1. Remove `> Skill sc:task-unified-protocol` from line 70 of `task-unified.md`
2. Keep the inlined classification logic (lines 46-66)
3. Remove `allowed-tools` from frontmatter OR keep only non-investigative tools
4. Run B1-B4 tests -- if classification header appears, Skill cascade is confirmed as secondary cause
5. Compare with a version that has Skill but NO `allowed-tools`

### #3: Duplicated "MANDATORY FIRST OUTPUT" Instructions Cause Classification Confusion (70% confidence)

**A contributing factor.** The classification instruction appears THREE times across the command file and SKILL.md. While this alone would not cause timeouts, it creates ambiguity about whether the model should classify in the command phase or the Skill phase, potentially causing it to defer classification until after tool calls (which consume all turns).

**Key evidence:**
- Command file line 46: "Classification (MANDATORY FIRST OUTPUT)"
- SKILL.md line 7: "MANDATORY FIRST OUTPUT"
- SKILL.md line 57: "0. MANDATORY Classification Header (ALWAYS FIRST)"
- Model never produces the header (scores = 0.0), suggesting it deferred rather than emitted immediately

**Proposed experiment:**
1. Remove classification instructions from either the command file OR the SKILL.md (not both)
2. Test whether a single instruction source produces better compliance
3. If the command file's instructions are sufficient alone (with no Skill invocation), remove them from SKILL.md
4. If the Skill's instructions are needed, remove them from the command file

---

## Summary of Changes from Previous Version

| Aspect | Previous (567 lines) | Current (107 lines) | Impact |
|--------|---------------------|---------------------|--------|
| `allowed-tools` in frontmatter | Not present | 9 tools listed | Enables tool-call turns |
| Skill invocation | None | Line 70: `> Skill sc:task-unified-protocol` | Loads 308 more lines, consumes a turn |
| "MANDATORY FIRST OUTPUT" | Not present | Lines 46-48 | Contradicts tool-call behavior |
| Classification logic | Implicit in behavioral flow | Explicitly inlined (lines 46-66) | Creates duplication with SKILL.md |
| Self-contained protocol | Yes (all 567 lines) | No (split: 107 command + 308 skill) | Two-phase loading with turn overhead |
| Total instruction volume | 567 lines | 107 + 308 = 415 lines | Slightly less, but structurally worse |

## Recommended Fix Direction

The most direct fix is to make the command file's classification phase **tool-free**. Options:

1. **Remove `allowed-tools` from frontmatter entirely** -- let the Skill handle tool authorization
2. **Add `--no-tools` or equivalent flag** for the classification phase, enabling tools only after the Skill loads
3. **Remove the Skill invocation** and inline a minimal execution protocol (the original approach, but trimmed)
4. **Reduce `allowed-tools` to `Skill` only** -- the model can invoke the Skill but cannot make investigative tool calls during classification
5. **Remove the classification requirement from the command file** and let ONLY the Skill handle it (single instruction source)
