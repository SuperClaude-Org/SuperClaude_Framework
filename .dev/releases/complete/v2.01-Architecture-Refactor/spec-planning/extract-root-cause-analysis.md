# Root Cause Analysis: Why Claude Code Agents Don't Follow Custom Instructions

**Date**: 2026-02-24
**Scope**: v2.01 Architecture Refactor -- the adherence problem
**Sources**: framework-synthesis-A.md, framework-synthesis-B.md, master-traceability.md, command-skill-policy.md
**Purpose**: Extract verified root causes from rollback analysis evidence to inform v2.01 spec

---

## 1. The Core Problem Statement

Claude Code agents partially follow, silently ignore, or hallucinate protocol steps from custom command and skill files. This is not a model capability failure -- it is a **structural failure** in how instructions are authored, loaded, and enforced.

Evidence from the Rollback Incident: An agent was given a 4-file plan, executed 68 file changes, and had to be rolled back entirely. Context compaction caused the agent to "go rogue." This is the failure mode v2.01 must eliminate systemically.

---

## 2. Identified Root Causes (Evidence-Backed)

### RC-1: Monolithic Command Files Exceed Agent Attention Budget

**Evidence**: `task-unified.md` was 567 lines containing syntax, flags, examples, tier classification algorithms, compliance checklists, MCP routing tables, sub-agent delegation matrices, and escape hatches -- all in a single file auto-loaded into context.

**Mechanism**: When a command file is auto-loaded on `/sc:<name>` invocation, every line consumes context tokens. At 567 lines, the agent's attention degrades across the document. The behavioral protocol (the part that actually matters for execution) competes with metadata, examples, and boundary definitions for attention weight.

**Measured scale**: `task-unified.md` at 567 lines is the worst case, but other commands also exceed reasonable limits: `recommend.md` (1005L), `review-translation.md` (913L), `pm.md` (592L), `spec-panel.md` (435L), `task-mcp.md` (375L).

**Source**: Framework Synthesis A, Section 3.1 ("Commands acted as monolithic specifications"), Section 3.3 (extraction ratios)

### RC-2: No Separation Between Interface and Behavioral Specification

**Evidence**: Pre-v2.01, command files contained both "what to invoke" (syntax, flags, usage) and "how to behave" (algorithms, step sequences, YAML specs). These are fundamentally different concerns:
- Interface metadata tells the agent what arguments it received
- Behavioral protocol tells the agent what to do with them

When both are in one document, the agent has no clear signal about which sections are descriptive context vs. executable instructions. The agent may treat a "Behavioral Summary" as the complete protocol, ignoring the detailed steps that follow.

**Failure mode**: "Silent degradation. If the command's behavioral summary was incomplete or outdated relative to the skill, Claude would guess or hallucinate protocol steps." (Framework Synthesis A, Section 3.1)

**Source**: Framework Synthesis A, Section 3.1; Command-Skill Policy, "Core Principle" section

### RC-3: No Enforcement Mechanism -- Commands Are Suggestions, Not Contracts

**Evidence**: Before this release, there was:
- No CI validation that command files stayed within size limits
- No check that commands actually referenced their protocol skills
- No validation that skill frontmatter was complete and consistent
- No build-time verification of the command-to-skill relationship
- No runtime enforcement that the agent actually loaded the skill before executing

Commands were suggestions that the agent could follow or ignore. There was no mechanism to detect when an agent skipped the skill invocation and executed from its own inference of the protocol.

**Source**: Framework Synthesis B, Section 5 (Test Coverage Gap Analysis -- "NONE" for activation flow, allowed-tools enforcement, content extraction correctness); Command-Skill Policy, "CI Enforcement" section

### RC-4: Naming Collision Causes Skill Re-Entry Block

**Evidence**: The Skill tool in Claude Code has a re-entry block: if a skill with the same name as the running command is already active, invoking it again fails silently. When the command name equals the skill name (e.g., command `adversarial` tries to invoke skill `sc:adversarial`), the invocation is blocked because the system considers the skill "already running."

This forces a structural requirement: command names and skill names MUST be different. The `-protocol` suffix convention exists specifically to solve this.

**Source**: Command-Skill Policy, "Why Separate Names?" section; Framework Synthesis A, Section 4.1-4.4

### RC-5: Missing `allowed-tools` Declarations Cause Silent Tool Failures

**Evidence**: BUG-001, independently identified by both synthesis agents: 4 of 5 commands added mandatory `Skill` invocations in their `## Activation` sections but did NOT add `Skill` to their `allowed-tools` frontmatter. Only `roadmap.md` did this correctly.

If Claude Code enforces the `allowed-tools` whitelist strictly, the agent is instructed to use a tool it is not permitted to use. The result is either a silent failure (agent skips the invocation) or a hard error. Either way, the protocol skill never loads, and the agent falls back to whatever behavioral guidance remains in the 106-line command stub -- which, for `task-unified.md`, is essentially nothing.

**Affected files**: `adversarial.md`, `cleanup-audit.md`, `task-unified.md`, `validate-tests.md` (8 files counting both `.claude/` and `src/` copies)

**Source**: Framework Synthesis A, Section 5.3; Framework Synthesis B, Section 3.1 (BUG-001); Master Traceability, Section 6 (BUG-001)

### RC-6: No Loading Order Guarantee or Dependency Chain

**Evidence**: The system has no mechanism to ensure that:
1. The command file is loaded first
2. The skill is loaded second (via explicit invocation)
3. Ref files are loaded third (via `claude -p`)

Without this guarantee, the agent may attempt to execute protocol steps before the skill has been loaded, or may never load the skill at all if context compaction drops the `## Activation` directive.

The master traceability matrix documents a clean DAG of dependencies (Layer 1: skills, Layer 2: commands, Layer 3: dev copies, Layer 4: build system), but this is a build-time dependency graph, not a runtime loading order guarantee.

**Source**: Framework Synthesis B, Section 6 (Recreation Dependency Graph); Master Traceability, Section 4 (Cross-Category Dependencies)

### RC-7: No CI Validation Means Drift Goes Undetected

**Evidence**: Before v2.01, there was no `make lint-architecture` target. The Makefile's `sync-dev` and `verify-sync` targets checked file parity between `src/` and `.claude/`, but they did NOT validate:
- Command-to-skill bidirectional link integrity
- Command size limits
- Presence of `## Activation` sections
- Skill frontmatter completeness
- Naming convention consistency

The architecture policy specifies 10 CI checks. Only 6 were implemented (BUG-006). The 4 unimplemented checks represent ongoing drift vectors.

**Source**: Framework Synthesis A, Section 6.2 (lint-architecture target); Framework Synthesis B, Section 2.4 (Makefile consistency); Master Traceability, Section 5.2 (BUG-006)

---

## 3. Structural Problems (Deeper Analysis)

### SP-1: Commands Mixing Dispatch Logic with Behavioral Specification

The fundamental architectural flaw: a single markdown file serves as both a dispatch interface (parsing user input, determining what to do) and a behavioral specification (defining how to do it). These are separate responsibilities that require different handling:

- **Dispatch** should be small, deterministic, and always loaded
- **Behavioral spec** should be detailed, authoritative, and loaded on-demand

When combined, the dispatch metadata dilutes the behavioral instructions. The agent reads the usage examples and flag tables, consuming attention budget that should be spent on the protocol steps.

### SP-2: No Separation Between "What to Invoke" and "How to Behave"

The `## Activation` section introduced in v2.01 is the first structural attempt to create this separation. It explicitly tells the agent: "Stop. Load the skill. Then follow the skill's instructions, not this file's."

But this is a soft directive. If the agent's context is compacted, the `## Activation` section may be summarized or dropped. The "Do NOT proceed" warning is natural language, not a machine-enforced gate.

### SP-3: Inconsistent Frontmatter Creates Unpredictable Tool Availability

Different commands use different frontmatter conventions:
- Some use `allowed-tools` (whitelist)
- Some use `mcp-servers` (MCP server list)
- Some have both
- Some have neither

This inconsistency means the agent cannot reliably predict which tools are available during command execution. The frontmatter is supposed to be a contract, but it functions as optional metadata.

### SP-4: No Loading Order Guarantee

The 3-tier loading model (Command -> Skill -> Refs) is a design, not an enforcement. There is no runtime mechanism that:
1. Blocks protocol execution until the skill is loaded
2. Validates that the loaded skill matches the expected version
3. Prevents the agent from proceeding if skill loading fails

---

## 4. Evidence from the Rollback Incident

### What Happened
- An agent was given a plan involving 4 files
- The agent executed changes across 68 files
- Context compaction occurred mid-execution
- The agent continued executing with degraded context, making changes beyond scope
- The entire change set had to be rolled back

### Root Causes Mapped to Incident

| Incident Symptom | Root Cause | Structural Gap |
|---|---|---|
| Agent changed 68 files when 4 were planned | RC-3 (no enforcement) | No scope control mechanism to limit file set |
| Context compaction caused "going rogue" | RC-1 (monolithic files), RC-6 (no loading guarantee) | No safeguard against context loss of critical directives |
| Half-cooked plans were executed | RC-3 (no enforcement) | No gate mechanism requiring plan validation before execution |
| Agent hallucinated protocol steps | RC-2 (no separation) | No single source of truth for behavioral spec |

### What Safeguards Were Missing

1. **Scope Control**: No mechanism to declare "this command operates on files X, Y, Z and ONLY those files." The agent's scope was unbounded.

2. **Context Compaction Resilience**: When context was compacted, the behavioral directives (which were mixed into a monolithic command file) were summarized away. A separated, on-demand-loaded skill would be more resilient because it enters context later and more recently.

3. **Plan Validation Gate**: No checkpoint requiring the agent to present its plan and receive approval before executing. The `## Activation` pattern is a step toward this (load skill first, then execute), but it needs a mandatory "present plan" step.

4. **Atomic Change Groups**: No mechanism to declare that certain files must change together (or not at all). The synthesis documents define atomic change groups (Groups A-D), but these are documentation, not enforcement.

---

## 5. Proposed Solutions (Extracted from Analysis)

### Solution 1: 3-Tier Loading Model

**Source**: Command-Skill Policy, "Tiered Loading Architecture" section

| Tier | What | Loading | Max Size |
|---|---|---|---|
| 0 -- Command | Entry point: metadata, usage, activation directive | Auto-loaded on `/sc:<name>` | 150 lines |
| 1 -- Protocol Skill | Full behavioral protocol: steps, agents, YAML specs | On-demand via `Skill sc:<name>-protocol` | Unlimited |
| 2 -- Refs | Detailed algorithms, templates, scoring rubrics | On-demand via `claude -p` per step | Unlimited |

**How it addresses root causes**:
- RC-1 (monolithic files): Commands capped at 150 lines
- RC-2 (no separation): Interface in command, behavior in skill
- RC-6 (loading order): Explicit 3-tier loading flow

### Solution 2: Thin Command Dispatchers

**Source**: Framework Synthesis A, Section 3.2 ("Commands are thin dispatchers")

The command file template is strictly defined:
- Frontmatter (name, description, category, complexity, mcp-servers, personas)
- Usage section
- Arguments section
- Examples section
- Activation section (mandatory `Skill sc:<name>-protocol` directive)
- Behavioral Summary (5 sentences max)
- Boundaries section

Hard constraints: no protocol YAML blocks, no step definitions, no scoring algorithms.

**How it addresses root causes**:
- RC-1: Forces commands below 150 lines
- RC-2: Behavioral logic ONLY in skills
- RC-3: Template is a contract, not a suggestion

### Solution 3: Protocol Skill Separation with `-protocol` Suffix

**Source**: Command-Skill Policy, "Naming Convention" section; Framework Synthesis A, Section 4

Protocol skills are named `sc:<name>-protocol` with directory `sc-<name>-protocol/`. This:
- Avoids the re-entry block (RC-4)
- Creates clear semantic signal ("this is a protocol, not a standalone skill")
- Enables CI linting (match directory name pattern to frontmatter name)

### Solution 4: CI Enforcement via `make lint-architecture`

**Source**: Command-Skill Policy, "CI Enforcement" section; Framework Synthesis A, Section 6.2

10 CI checks defined:
1. Bidirectional link: command -> skill directory exists
2. Bidirectional link: skill directory -> command exists
3. Command size warning (>200 lines)
4. Command size error (>500 lines)
5. No inline protocol YAML in commands with skills (>20 lines)
6. Activation section present in paired commands
7. Activation references correct skill name
8. Skill frontmatter complete (name, description, allowed-tools)
9. Skill naming consistency (directory name matches frontmatter)
10. Sync integrity (src/ matches .claude/)

**Current status**: 6 of 10 implemented. Missing: checks 5, 7, and possibly others.

**How it addresses root causes**:
- RC-3: Enforcement, not suggestion
- RC-5: Validates frontmatter completeness
- RC-7: Catches drift at PR time

### Solution 5: Mandatory `allowed-tools` Including `Skill`

**Source**: BUG-001 across all three synthesis documents

All commands with `## Activation` sections MUST include `Skill` in their `allowed-tools` frontmatter. This is currently a bug in 4 of 5 commands.

### Solution 6: Scope Control Mechanism (Not Yet Designed)

**Source**: Inferred from rollback incident analysis

A mechanism to declare the file scope of a command execution:
- The command or skill specifies which files/directories it may modify
- The agent presents its plan before execution
- A validation gate checks the plan against the declared scope
- Execution is blocked if the plan exceeds scope

This is the most significant gap -- none of the analysis documents propose a concrete design for runtime scope control.

### Solution 7: Context Compaction Resilience (Not Yet Designed)

**Source**: Inferred from rollback incident analysis

Strategies to survive context compaction:
- Critical directives (activation, scope limits, boundaries) placed at document boundaries where compaction algorithms are less likely to summarize them
- Redundant placement of "Do NOT proceed without loading skill" at top AND bottom of command files
- Skill-level "re-anchor" directives that re-state boundaries after loading

This is partially addressed by the 3-tier model (skills load later, so they're "fresher" in context) but has no explicit design.

---

## 6. Gap Analysis: What v2.01 Must Still Solve

| Gap | Priority | Status in Analysis | Required for v2.01? |
|---|---|---|---|
| Runtime scope control (file-set limits) | CRITICAL | Not designed | YES -- prevents "68 files changed" class of failure |
| Context compaction resilience | HIGH | Partially addressed by 3-tier model | YES -- prevents "going rogue" after compaction |
| Plan validation gate | HIGH | Not designed | YES -- prevents half-cooked plan execution |
| Complete `allowed-tools` declarations | HIGH | BUG-001 identified, fix specified | YES -- trivial fix |
| Remaining 4 CI lint checks | MEDIUM | BUG-006 identified | YES -- complete enforcement |
| 6 oversized command splits | MEDIUM | Identified in backlog | PARTIAL -- address worst offenders |
| Architecture policy deduplication | LOW | BUG-004 identified | NO -- can defer |
| `claude -p` Tier 2 ref loader design | HIGH | Not started | DEPENDS -- needed for full 3-tier model |
| Cross-skill invocation patterns | HIGH | Not started | DEPENDS -- needed for roadmap->adversarial |

---

## 7. Summary: The Five Root Causes That Matter Most

1. **Commands are too long** (RC-1): Monolithic files exceed agent attention budget. Solution: 150-line cap, 3-tier loading.

2. **No separation of concerns** (RC-2): Interface and behavior mixed in one file. Solution: Thin command dispatchers + protocol skills.

3. **No enforcement** (RC-3): Instructions are suggestions. Solution: CI lint checks, mandatory activation sections, frontmatter validation.

4. **Naming collision** (RC-4): Re-entry block prevents skill loading. Solution: `-protocol` suffix convention.

5. **No scope control** (not yet solved): Agent can modify unlimited files. Solution: NEEDS DESIGN -- file-set declarations, plan gates, boundary enforcement.

The first four are addressed by the command-skill decoupling architecture already designed. The fifth is the open problem v2.01 must solve to prevent the rollback incident class of failure from recurring.
