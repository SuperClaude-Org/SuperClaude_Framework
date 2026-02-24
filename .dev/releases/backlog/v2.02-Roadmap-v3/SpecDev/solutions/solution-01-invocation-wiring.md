# Solution #1: Invocation Wiring Fix

## Problem Summary

The `--multi-roadmap --agents opus,haiku` feature failed because `sc:roadmap` instructs Claude to "Invoke sc:adversarial" but provides no executable mechanism. The `Skill` tool is absent from `allowed-tools` in both `.claude/commands/sc/roadmap.md` (line 4) and `src/superclaude/skills/sc-roadmap/SKILL.md` (line 4). The verb "Invoke" has no tool-call mapping, and zero precedents exist for skill-to-skill invocation in the framework. Claude rationally fell back to spawning generic Task agents, forfeiting the adversarial pipeline's 5-step structured debate.

**Root cause rank**: 1 of 5, combined score 0.90.

---

## Options Analysis

### Option A: Add `Skill` to allowed-tools

**Description**: Add `Skill` to the `allowed-tools` frontmatter in both `roadmap.md` (command) and `SKILL.md` (skill), then rewrite Wave 2 step 3 to explicitly reference the Skill tool.

**Pros**:
- Minimal change (1 line per file + instruction clarification)
- Directly addresses the root cause
- Clean architectural intent: skills invoke skills

**Cons**:
- The Skill tool documentation states: "Do not invoke a skill that is already running." When sc:roadmap is running and attempts to invoke sc:adversarial, this constraint is triggered.
- **Critical question**: Does invoking sc:adversarial via the Skill tool *replace* sc:roadmap's loaded context, or does it *nest*? The Skill tool is documented as loading a skill's instructions into the current conversation. If it replaces, sc:roadmap loses its Wave 2-4 instructions. If it nests, the "already running" warning may block execution.
- No existing skill-to-skill invocation precedent exists anywhere in the codebase to validate behavior.
- Even if invocation works, there is no in-memory return contract mechanism. The Skill tool returns control to the conversation, but sc:adversarial's return contract fields (status, convergence_score, merged_output_path, etc.) have no defined transport.

**Feasibility**: LOW. The "already running" constraint is a fundamental design boundary of the Skill tool, not a configuration oversight. Without empirical testing of Skill tool nesting behavior, this option carries high uncertainty. Even if it works, the return contract transport problem remains.

**Blast radius**: Minimal file changes but high behavioral uncertainty. If Skill tool replaces context, sc:roadmap's post-invocation waves (3-4) would be lost.

### Option B: Task Agent Wrapper

**Description**: Spawn a Task agent whose sole job is to invoke sc:adversarial via the Skill tool. The Task agent runs in a fresh execution context, sidestepping the "already running" constraint.

**Pros**:
- Avoids the "skill already running" constraint entirely -- the Task agent is a fresh context
- Task agents already exist in sc:roadmap's allowed-tools
- File-based return contract (return-contract.yaml) provides a concrete data channel
- Task agents can invoke the Skill tool because no skill is running in their context
- Established pattern: sc:roadmap already dispatches Task agents in Wave 4 (quality-engineer, self-review)

**Cons**:
- Extra indirection: sc:roadmap -> Task agent -> Skill tool -> sc:adversarial
- The Task agent prompt must carry all context (spec path, agent specs, depth, output dir, interactive flag)
- Task agent timeout limits may be insufficient for deep adversarial debates with 5+ agents (3 debate rounds, 5 pipeline steps, each with sub-agent delegation)
- The Task agent may not have access to the Skill tool -- this depends on the Task tool's tool permissions model

**Feasibility**: MEDIUM-HIGH. The indirection is clean and the pattern is established. The timeout concern is real but manageable (Claude Code Task agents have configurable timeouts). The Skill tool access question needs verification but is likely available since Task agents inherit the conversation's tool set.

**Blast radius**: Localized to Wave 2 step 3 instructions and adversarial-integration.md. No structural changes to either skill.

### Option C: Inline Protocol Execution

**Description**: Instead of invoking sc:adversarial as a separate skill, embed the adversarial 5-step protocol directly in sc:roadmap's Wave 2 instructions. Use Task agents for each step (diff analysis, debate, scoring, refactoring plan, merge).

**Pros**:
- No inter-skill invocation needed -- entirely within sc:roadmap's existing tool budget
- Full control over each step's execution and error handling
- No "already running" constraint, no return contract transport problem
- Each of the 5 steps can be a dedicated Task agent dispatch, matching sc:roadmap's existing Wave 4 delegation pattern
- The adversarial 5-step protocol is already fully documented in sc:adversarial's SKILL.md (1746 lines of detailed instructions) -- it can be referenced as a ref document

**Cons**:
- Duplicates adversarial logic between sc:roadmap and sc:adversarial
- Maintenance burden: changes to the adversarial protocol must be reflected in two places
- Increases sc:roadmap's complexity and context load
- sc:adversarial becomes unreachable from sc:roadmap, reducing composability

**Feasibility**: HIGH. No external dependencies, no uncertain tool behaviors. Everything uses established patterns (Task agents + ref documents).

**Blast radius**: Moderate. Requires new ref document in sc:roadmap (e.g., `refs/adversarial-inline.md`), modification to Wave 2 step 3, and potentially increased context usage.

### Option D: File-Based Handoff

**Description**: sc:roadmap writes an invocation request file, a separate orchestration layer picks it up and runs sc:adversarial.

**Pros**:
- Clean separation of concerns
- Decoupled execution contexts

**Cons**:
- No such orchestration layer exists in the framework
- Would require building a new execution engine (polling, state management, error propagation)
- Massively over-engineered for the problem at hand
- No precedent in the framework for asynchronous file-based orchestration

**Feasibility**: VERY LOW. Requires building infrastructure that does not exist and is not on any roadmap.

**Blast radius**: Would require entirely new framework component. Not viable.

---

## Recommended Solution: Option B (Task Agent Wrapper) with Option C Fallback

### Rationale

Option B is the correct architectural choice for three reasons:

1. **It preserves composability.** sc:adversarial remains a standalone, reusable skill that any command can invoke. The Task agent wrapper is a thin delegation layer, not a logic duplication.

2. **It uses established patterns.** sc:roadmap already dispatches Task agents in Wave 4 for validation. The same pattern applies to Wave 2 for adversarial invocation. The Task agent inherits the conversation's available tools (including Skill), runs in a fresh context (no "already running" conflict), and returns results via file.

3. **The return contract has a clean transport.** sc:adversarial writes `return-contract.yaml` to the output directory. sc:roadmap reads it after the Task agent completes. This is the same fan-out/fan-in pattern used by sc:cleanup-audit.

**Why not Option A**: The "already running" constraint is a design boundary, not a bug. Even if it works today, relying on undocumented nesting behavior is fragile.

**Why not Option C**: It works, but it duplicates ~1700 lines of adversarial protocol logic and makes independent adversarial usage harder to maintain. It should be the fallback if Option B proves unworkable.

**Why not Option D**: It requires building infrastructure that does not exist.

### Fallback Protocol

If the Task agent cannot access the Skill tool (tool permissions are restricted), fall back to Option C: the Task agent receives the adversarial protocol instructions directly in its prompt, extracted from `refs/adversarial-inline.md`. This is documented as the degraded-mode path.

---

## Implementation Details

### Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `.claude/commands/sc/roadmap.md` | Add `Skill` to allowed-tools | Line 4 |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Add `Skill` to allowed-tools | Line 4 |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Rewrite Wave 2 step 3 with Task agent delegation pattern | Line 137 (within Wave 2 section) |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Add "Invocation Mechanism" section with Task agent wrapper instructions | New section after "Invocation Patterns" |
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Add return-contract.yaml write step to Step 5 | After line 253 (merge execution output) |

### Code Changes

#### Change 1: Add `Skill` to allowed-tools in command file

**File**: `.claude/commands/sc/roadmap.md`, line 4

```yaml
# BEFORE:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task

# AFTER:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

#### Change 2: Add `Skill` to allowed-tools in skill file

**File**: `src/superclaude/skills/sc-roadmap/SKILL.md`, line 4

```yaml
# BEFORE:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task

# AFTER:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

#### Change 3: Rewrite Wave 2 step 3 with explicit delegation pattern

**File**: `src/superclaude/skills/sc-roadmap/SKILL.md`, Wave 2 section

Replace the current step 3 (line 137) with:

```markdown
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Expand model-only agents with the primary persona from Wave 1B. If agent count >=5, orchestrator is added automatically. **Invoke sc:adversarial via Task agent delegation**:

   **Step 3a**: Construct the sc:adversarial invocation arguments:
   - `--source`: spec file path (or unified spec from Wave 1A if combined mode)
   - `--generate roadmap`
   - `--agents`: expanded agent specs (comma-separated)
   - `--depth`: value of sc:roadmap's `--depth` flag
   - `--output`: sc:roadmap's resolved output directory
   - `--interactive`: only if sc:roadmap's `--interactive` flag is set

   **Step 3b**: Dispatch a Task agent with the following prompt (substitute actual values for placeholders):
   ```
   You are the adversarial pipeline orchestrator. Your sole job is to execute the sc:adversarial skill and write its return contract to a file.

   STEP 1: Use the Skill tool to invoke sc:adversarial with these arguments:
     --source {spec_path} --generate roadmap --agents {expanded_agents} --depth {depth} --output {output_dir} {--interactive if set}

   STEP 2: After sc:adversarial completes, write the return contract to:
     {output_dir}/adversarial/return-contract.yaml

   The return contract MUST contain these fields:
     status: success | partial | failed
     merged_output_path: <path to merged file>
     convergence_score: <0.0-1.0>
     artifacts_dir: <path to adversarial/ directory>
     unresolved_conflicts: <count of unresolved items>
     base_variant: <model:persona of winning variant>

   STEP 3: If the Skill tool is unavailable or fails, respond with:
     "SKILL_UNAVAILABLE: sc:adversarial could not be invoked via Skill tool."
   ```

   **Step 3c**: After the Task agent completes, read `{output_dir}/adversarial/return-contract.yaml`. If the file exists, consume the return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section.

   **Step 3d (fallback)**: If the Task agent reports SKILL_UNAVAILABLE, or if return-contract.yaml does not exist after Task completion, execute the degraded-mode fallback:
   - Read `src/superclaude/skills/sc-adversarial/SKILL.md` directly
   - Dispatch Task agents to execute each of the 5 adversarial steps inline (diff analysis, debate, scoring, refactoring plan, merge), using the protocol from sc:adversarial's SKILL.md as behavioral instructions
   - Write return-contract.yaml manually from the inline execution results
   - Log warning: "Adversarial pipeline executed in degraded mode (inline). Results may differ from full sc:adversarial invocation."

   The adversarial output replaces template-based generation.
```

#### Change 4: Add Invocation Mechanism section to adversarial-integration.md

**File**: `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`

Insert after the "Invocation Patterns" section (after line 136), before "Return Contract Consumption":

```markdown
---

## Invocation Mechanism

sc:roadmap invokes sc:adversarial via **Task agent delegation**, not direct Skill tool call. This is required because the Skill tool cannot invoke a skill while another skill (sc:roadmap) is already running.

### Task Agent Delegation Pattern

```
sc:roadmap (running)
  -> dispatches Task agent (fresh context)
    -> Task agent uses Skill tool to invoke sc:adversarial
    -> sc:adversarial executes 5-step pipeline
    -> sc:adversarial writes artifacts to output directory
  -> Task agent writes return-contract.yaml
  -> sc:roadmap reads return-contract.yaml
```

### Return Contract File Convention

sc:adversarial writes its return contract to `{output_dir}/adversarial/return-contract.yaml` as the final step of its pipeline. sc:roadmap reads this file after the Task agent completes.

**File format**:
```yaml
# Written by sc:adversarial as final pipeline step
status: success          # success | partial | failed
merged_output_path: ./adversarial/merged-roadmap.md
convergence_score: 0.85  # 0.0-1.0
artifacts_dir: ./adversarial/
unresolved_conflicts: 0  # integer count
base_variant: opus:architect  # model:persona of winning variant
```

### Degraded Mode Fallback

If the Task agent cannot invoke sc:adversarial via the Skill tool (tool unavailable, permission error, or skill not found), sc:roadmap falls back to inline execution:

1. Read `src/superclaude/skills/sc-adversarial/SKILL.md` as a behavioral reference
2. Execute each of the 5 adversarial steps via individual Task agents
3. Write return-contract.yaml from inline results
4. Log warning in extraction.md: "Adversarial pipeline executed in degraded mode"

This fallback preserves the adversarial pipeline's functionality at the cost of increased context usage and reduced separation of concerns.
```

#### Change 5: Add return-contract.yaml write step to sc:adversarial

**File**: `src/superclaude/skills/sc-adversarial/SKILL.md`

In the Return Contract section (after line 350), add a file-write instruction:

```markdown
### Return Contract File Output

When sc:adversarial is invoked by another command (detected by the presence of a calling context), write the return contract to a YAML file as the final pipeline step:

**File path**: `{output_dir}/adversarial/return-contract.yaml`

**Write step**: After Step 5 (merge execution) completes, write:

```yaml
# sc:adversarial return contract
# Generated: <ISO-8601 timestamp>
status: <determined from pipeline outcome>
merged_output_path: <relative path to merged output>
convergence_score: <final convergence from debate>
artifacts_dir: <relative path to adversarial/ directory>
unresolved_conflicts: <count of unresolved diff points>
base_variant: <model:persona of selected base>
```

**Status determination**:
- `success`: All 5 steps completed, post-merge validation passed
- `partial`: Steps completed but with validation failures, non-convergence, or skipped debate
- `failed`: Pipeline aborted (insufficient variants, agent failures, merge failure)

This file-based return contract enables programmatic consumption by calling commands (sc:roadmap, sc:design) without requiring in-memory data transport.
```

### Blast Radius Assessment

**Directly affected files** (5 files):
1. `.claude/commands/sc/roadmap.md` -- frontmatter only (1 line)
2. `src/superclaude/skills/sc-roadmap/SKILL.md` -- frontmatter (1 line) + Wave 2 step 3 rewrite
3. `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` -- new section added
4. `src/superclaude/skills/sc-adversarial/SKILL.md` -- new subsection in Return Contract

**Indirectly affected**:
- Any future command that invokes sc:adversarial benefits from the file-based return contract convention
- The `make sync-dev` target must be run after changes to sync `src/` to `.claude/`

**Not affected**:
- sc:adversarial's core 5-step pipeline (unchanged)
- sc:roadmap's Waves 0, 1A, 1B, 3, 4 (unchanged)
- All other skills and commands (no shared interfaces modified)
- Test suite (no Python code changes in this fix)

**Risk assessment**:
- LOW risk for the `Skill` addition to allowed-tools (additive, non-breaking)
- MEDIUM risk for the Task agent delegation pattern (new execution path, untested)
- LOW risk for return-contract.yaml convention (additive, no existing behavior modified)
- Fallback to inline execution (Option C) mitigates the MEDIUM risk

---

## Confidence Score: 0.80/1.0

**Justification**:

The solution is architecturally sound and uses established patterns (Task agent delegation, file-based data exchange). The confidence is 0.80 rather than higher because:

1. **Untested assumption** (0.80 -> 0.75): Whether Task agents can access the Skill tool has not been empirically verified. The fallback protocol mitigates this, but the primary path is unproven.

2. **Timeout uncertainty** (0.75 -> 0.80 with mitigation): Deep adversarial debates with 5+ agents may exceed Task agent timeout limits. The timeout is configurable but the default may be insufficient for 3-round debates with 10 sub-agents.

3. **Established pattern boost** (+0.05): The Task agent delegation pattern is already used in sc:roadmap Wave 4 (quality-engineer, self-review agents), reducing integration risk.

4. **Fallback protocol boost** (+0.05): The degraded-mode inline execution path ensures the feature works even if the primary Task-agent-with-Skill-tool path fails. This eliminates the single-point-of-failure risk.

**What would raise confidence to 0.90+**: Empirical verification that a Task agent can successfully invoke the Skill tool to load and execute sc:adversarial, with return-contract.yaml written correctly.

---

*Solution designed 2026-02-22. Analyst: claude-opus-4-6 (self-review agent).*
*Addresses: RC1 (Invocation Wiring Gap, rank 1, score 0.90).*
*Partially addresses: RC2 (Spec-Execution Gap), RC4 (Return Contract), RC5 (Claude Behavior).*
