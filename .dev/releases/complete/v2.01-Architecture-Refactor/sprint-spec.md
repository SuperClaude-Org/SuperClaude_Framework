# v2.01 Architecture Refactor — Sprint Spec (Merged)

**Generated**: 2026-02-24
**Base**: `v2.01_spec-planning-sonnet.md` (Doc-A)
**Augmented with**: `spec-planning/v2.01-spec-planning.md` (Doc-B)
**Merge method**: sc:adversarial pipeline (5-round, 3-agent debate → R1–R8 refactoring operations)
**Scope**: v2.01 release ONLY — see §14 for explicit v2.02 boundary
**⚠️ ALL PHASES TODO**: The rollback to commit `5733e32` erased all prior implementation work. No phase is complete. Begin from Phase 1.

---

## Table of Contents

1. [Overview](#1-overview)
2. [The Core Problem](#2-the-core-problem)
3. [Root Causes (Ranked by Severity)](#3-root-causes-ranked-by-severity)
4. [Architectural Solution: Three-Tier Model](#4-architectural-solution-three-tier-model)
5. [Component Formal Definitions + Verbatim Templates](#5-component-formal-definitions--verbatim-templates)
6. [Naming Convention](#6-naming-convention)
7. [The 5 Skills to Rename](#7-the-5-skills-to-rename)
8. [Invocation Wiring](#8-invocation-wiring)
9. [Fallback Protocol (FALLBACK-ONLY Variant)](#9-fallback-protocol-fallback-only-variant)
10. [Return Contract Schema](#10-return-contract-schema)
11. [Enforcement Mechanisms + Verification Scripts](#11-enforcement-mechanisms--verification-scripts)
12. [Bug Inventory](#12-bug-inventory)
13. [Phase Plan (6 Phases, 18 Tasks)](#13-phase-plan-6-phases-18-tasks)
14. [v2.01 vs v2.02 Explicit Boundary](#14-v201-vs-v202-explicit-boundary)
15. [Status at Rollback + Current Branch State](#15-status-at-rollback--current-branch-state)
16. [Open Issues and Gaps](#16-open-issues-and-gaps)
16b. [Risk Assessment](#16b-risk-assessment)
17. [Key Architectural Decisions (Decision Log)](#17-key-architectural-decisions-decision-log)
18. [Policy Document Reference](#18-policy-document-reference)

---

## 1. Overview

**v2.01** is a **strict architectural refactor** of the SuperClaude Framework. It is NOT a feature release. Its sole purpose is to fix the root causes of agents not following `/sc:command` instructions by enforcing a clean separation between:

- **Commands** — thin entry points (target ≤150 lines, hard limit ≤350 lines) that dispatch to skills
- **Skills** — full behavioral protocol specifications (unlimited size)
- **Refs** — step-specific detail loaded on-demand via `claude -p`

The central metaphor of this release: **"Commands are doors. Skills are rooms. Refs are drawers."**

### What v2.01 Delivers

1. A formal **architecture policy** (`docs/architecture/command-skill-policy.md`)
2. **5 skill directory renames** with `-protocol` suffix convention
3. **5 command file refactors** with mandatory `## Activation` sections
4. **`make lint-architecture`** CI enforcement target (6 of 10 policy checks, 2 needing design)
5. **Makefile sync cleanup** removing the old "skills served by commands" heuristic
6. **Fallback invocation protocol** (F1/F2-3/F4-5) for when Skill tool is unavailable
7. **Return contract schema** for structured agent output

### What v2.01 Is NOT

- Not a feature release (no new user-facing functionality)
- Not a roadmap improvement (that is v2.02)
- Not a full headless `claude -p` implementation (deferred after `TOOL_NOT_AVAILABLE` probe)
- Not a complete fix of all root causes (RC3/RC5 deferred to v2.02)
- Not a runtime scope control solution (CRITICAL open gap — see §9.3 and §16)

---

## 2. The Core Problem

### Symptom

Agents invoked by `/sc:command` instructions do not reliably follow the behavioral spec defined in the associated skill. The `sc:roadmap` command is the primary documented failure case — when it attempts to invoke `sc:adversarial`, the adversarial pipeline is silently skipped or partially executed.

### Evidence

- GitHub issues: #837, #1048
- 5 scored root causes + 2 structural root causes identified through adversarial debate pipeline
- 27 findings from expert panel review of `specification-draft-v2.md`
- Rollback incident: agent planned 4 files, executed 68 file changes, full rollback required

### Why This Happened

**Before v2.01**, the architecture had no enforced separation between commands and skills:

```
BEFORE (v2.0 — Monolithic Model):
User: /sc:task
  ↓
Claude reads task-unified.md (567 lines, includes full protocol)
  ↓
Claude infers steps from behavioral summary
  ↓
Claude fills gaps with hallucination when spec is incomplete
```

**Problems**:
1. Commands contained full protocols → token waste (567 lines auto-loaded per invocation)
2. Agents guessed protocol steps when summaries drifted from actual skill specs
3. No explicit invocation wiring — "Invoke sc:adversarial" was prose, not executable
4. `subagent_type: "general-purpose"` in SKILL.md YAML is dead metadata (no such Task tool parameter)
5. No return contract abstraction — consumers couldn't parse producer output reliably
6. No loading order guarantee — context compaction could drop `## Activation` directive silently
7. No CI validation — policy without enforcement degraded to suggestion

---

## 3. Root Causes (Ranked by Severity)

Root causes use formula: `problem_score = likelihood × 0.6 + impact × 0.4`
Combined ranking: `(problem_score × 0.5) + (solution_score × 0.5)`

### Structural Cross-Reference

| Structural Problem | Root Causes | Evidence |
|---|---|---|
| Commands mix dispatch logic with behavioral spec | RC1, RC2 | `task-unified.md` at 567 lines |
| No machine-enforced gate between command and skill | RC3, RC6 | `## Activation` is natural language, not enforcement |
| Inconsistent frontmatter creates unpredictable tool availability | RC5 | Two incompatible frontmatter patterns across 37 commands |
| No loading order guarantee | RC6 | 3-tier model is design, not enforcement |
| No CI validation loop | RC7 | `lint-architecture` implements 6 of 10 checks |

---

### RC1: Invocation Wiring Gap — Score: 0.90 ⚡ CRITICAL

**Problem**: The instruction "Invoke sc:adversarial" in `sc:roadmap`'s SKILL.md is **natural language prose**, not an executable tool call. The Skill tool has no skill-to-skill chaining capability. When Claude encounters this instruction during Wave 2 execution, it faces an unresolvable ambiguity and most likely silently skips the step.

**Evidence Chain**:
- Failing instruction is plain text at line 137 of SKILL.md
- Skill tool is designed for user-initiated invocation only
- Zero precedents in codebase for skill-to-skill invocation via Skill tool
- Return contract assumes in-memory data flow that doesn't exist

**Fix (v2.01)**: Task agent wrapper — dispatch a fresh Task agent that invokes `Skill sc:adversarial-protocol`, then read the return contract file.

---

### RC2: Spec Execution Gap — Score: 0.770 HIGH

**Problem**: Wave 2 Step 3 contained a bare "Invoke" verb with no tool binding. The entire step was a single vague line with no sub-steps, no fallback, no return handling. Agents had no executable specification to follow.

**Fix (v2.01)**: Decompose Wave 2 Step 3 into 6 atomic sub-steps (3a–3f) with explicit tool bindings, fallback protocol, and return contract routing.

---

### RC4: Return Contract Undefined — Score: 0.750 HIGH

**Problem**: No unified interface for returning results from agent invocation. Consumers didn't know which invocation method was used, causing inconsistent branching logic. Field count mismatch between spec and implementation (5 fields vs 10 fields). Type conflicts (`unresolved_conflicts` was integer, should be `list[string]`).

**Fix (v2.01)**: 10-field canonical return contract schema with explicit producer/consumer ownership model. File-based YAML transport at `<output-dir>/adversarial/return-contract.yaml`.

---

### RC3: Agent Dispatch Mechanism — Score: 0.70 MEDIUM *(Deferred to v2.02)*

**Problem**: `subagent_type: "debate-orchestrator"` in SKILL.md YAML is dead metadata — the Task tool has no `subagent_type` parameter. Claude falls back to keyword matching, selecting the wrong agent. The adversarial pipeline's 5-step protocol is never followed.

**v2.01 Deferral Rationale**: Latent defect that surfaces only after RC1/RC2/RC4 are fixed. Combined score (0.728) below the v2.01 cut line.

---

### RC5: Claude Behavioral Fallback — Score: 0.765 MEDIUM *(Deferred to v2.02)*

**Problem**: Full fallback protocol complexity when Claude deviates from behavioral spec. Two-tier quality gate (artifact existence + structural consistency) needed but not in scope.

**v2.01 Deferral Rationale**: The 5-step fallback protocol in v2.01 partially addresses this; the full quality gate is v2.02 work.

---

### RC6: No Loading Order Guarantee *(Doc-B addition)*

**Problem**: The system has no mechanism to ensure that: (1) the command file is loaded first, (2) the skill is loaded second via explicit invocation, (3) ref files are loaded third via `claude -p`. Without this guarantee, the agent may attempt to execute protocol steps before the skill has been loaded, or may never load the skill at all if context compaction drops the `## Activation` directive.

**Partial fix (v2.01)**: The `## Activation` section with "Do NOT proceed" warning partially addresses this. Full loading order enforcement is a v2.02 concern.

---

### RC7: No CI Validation *(Doc-B addition)*

**Problem**: Before v2.01, there was no `make lint-architecture` target. The architecture policy specifies 10 CI checks. Only 6 were designed (BUG-006). The 4 unimplemented checks represent ongoing drift vectors. Policy without enforcement degrades to suggestion.

**Fix (v2.01)**: Implement `make lint-architecture` with 6 of 10 checks before any migration work begins (Rule 7.5).

---

## 4. Architectural Solution: Three-Tier Model

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 0 — COMMAND                                           │
│  Auto-loaded on /sc:<name>  |  target ≤150, max ≤350 lines  │
│  Location: src/superclaude/commands/<name>.md               │
│  "Commands are DOORS"                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ ## Activation → Skill sc:<name>-protocol
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1 — PROTOCOL SKILL                                    │
│  Loaded by agent via Skill tool  |  Unlimited size          │
│  Location: src/superclaude/skills/sc-<name>-protocol/       │
│  "Skills are ROOMS"                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ Ref: Load refs/<file>.md via claude -p
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2 — REF FILES                                         │
│  On-demand via claude -p  |  One concern per file           │
│  Location: src/superclaude/skills/sc-<name>-protocol/refs/  │
│  "Refs are DRAWERS"                                         │
└─────────────────────────────────────────────────────────────┘
```

### Loading Flow

```
User types:     /sc:adversarial --compare file1.md,file2.md
                        |
                        v
Tier 0:         adversarial.md auto-loaded (target ≤150, max ≤350 lines)
                        |
                        v (## Activation section: Invoke Skill sc:adversarial-protocol)
                        |
Tier 1:         Agent calls Skill tool → sc:adversarial-protocol/SKILL.md loaded
                        |
                        v (Step 3 says: Load refs/scoring-protocol.md via claude -p)
                        |
Tier 2:         claude -p injects scoring-protocol.md into sub-agent context
```

### Why This Works

| Problem | v2.0 Behavior | v2.01 Behavior |
|---------|--------------|----------------|
| Protocol bloat | 567 lines auto-loaded per invocation | ≤106 lines + skill loaded on-demand |
| Behavioral inference | Claude guesses steps from summaries | Explicit skill invocation: hard failure if skill not found |
| Token waste | All detail loaded upfront | Refs loaded per-step only |
| Agent compliance | Ambiguous (which file to trust?) | Clear: command → activation → skill |

### Tier Summary

| Tier | Component | Loading Mechanism | Max Size |
|------|-----------|-------------------|----------|
| **0** — Command | Entry point: metadata, usage, examples, activation directive, boundaries | Auto-loaded on `/sc:<name>` invocation | **target ≤150, max ≤350 lines** |
| **1** — Protocol Skill | Full behavioral protocol: steps, agent dispatch, YAML specs, error handling | Agent invokes `Skill sc:<name>-protocol` | Unlimited |
| **2** — Refs | Detailed algorithms, templates, scoring rubrics | Loaded via `claude -p` script per step | Unlimited |

---

## 5. Component Formal Definitions + Verbatim Templates

### COMMAND (Tier 0)

**Definition**: A slim, user-facing entry point auto-loaded by Claude Code when the user types `/sc:<name>`. Contains metadata, usage documentation, and a mandatory activation directive pointing to the protocol skill.

**Verbatim Template**:

```markdown
---
name: <name>
description: "<one-line description>"
category: <development|analysis|quality|testing|documentation|meta>
complexity: <basic|moderate|advanced>
mcp-servers: [<server-list>]
personas: [<persona-list>]
allowed-tools: <tool-list including Skill>
---

# /sc:<name> - <Title>

## Usage
<invocation patterns with code blocks>

## Arguments
<flags/options table>

## Examples
<3-5 concrete usage examples>

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:<name>-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Behavioral Summary
<<= 5 sentences describing what the pipeline does at a high level>

## Boundaries
**Will:** <bullet list>
**Will Not:** <bullet list>

## Related Commands
<optional: table of related commands>
```

**Hard Constraints**:
- **Max size**: target ≤150 lines; hard limit ≤350 lines (WARN at 350, ERROR at 500)
- **Required sections**: metadata (YAML frontmatter), `## Usage`, `## Arguments`, `## Examples`, `## Activation` *(if protocol skill exists)*, `## Behavioral Summary` (≤5 sentences), `## Boundaries`
- **NO** protocol YAML blocks, step definitions, or scoring algorithms
- **MUST** have `## Activation` section if a protocol skill exists
- `## Activation` MUST name the exact skill: `sc:<name>-protocol`
- `## Activation` MUST include the "Do NOT proceed" warning
- `Skill` MUST appear in `allowed-tools` frontmatter

**Command-Only Files (No Skill)**: Commands without a matching protocol skill omit `## Activation`, may contain full behavioral instructions inline, and are subject to: WARN at 200 lines, ERROR at 500 lines.

**Anti-patterns**:
- Command files >350 lines when a protocol skill exists
- Missing `## Activation` section when paired with protocol skill
- Inline protocol steps or scoring algorithms
- Re-defining behavioral logic already in the skill

---

### SKILL (Tier 1 — Protocol Skill)

**Definition**: A full behavioral specification that agents invoke via the Skill tool. Contains all executable logic, step definitions, agent dispatch, MCP integration, and error handling. Unlimited size.

**Verbatim Template**:

```markdown
---
name: sc:<name>-protocol
description: "<description>"
allowed-tools: <tool list including Skill if cross-invocation needed>
argument-hint: "<usage hint>"
---

# sc:<name>-protocol - <Title>

## Purpose
<what this protocol does and why>

## Triggers
<when this skill is invoked>

## Protocol Steps
### Step 1: <Name>
<full specification with YAML blocks>
### Step 2: <Name>
...

## Configurable Parameters
<flags, thresholds, defaults>

## Agent Delegation
<which agents are spawned, their roles, dispatch config>

## MCP Integration
<which MCP servers, which steps, circuit breakers>

## Error Handling
<error matrix with recovery actions>

## Return Contract
<output fields for programmatic integration>

## Boundaries
**Will:** / **Will Not:**
```

**Hard Constraints**:
- **Naming**: `sc:<name>-protocol` in frontmatter `name:` field (MUST end in `-protocol`)
- **Directory**: `src/superclaude/skills/sc-<name>-protocol/`
- **Required frontmatter**: `name`, `description`, `allowed-tools`
- **Required sections**: `## Purpose`, `## Triggers`, `## Protocol Steps`, `## Agent Delegation`, `## MCP Integration`, `## Error Handling`, `## Return Contract`, `## Boundaries`
- **Tier 2 reference format**: `**Ref**: Load refs/<filename>.md via claude -p before executing this step.`
- **MUST** define all behavioral logic (the command file contains NONE)
- **MUST NOT** be auto-loaded; only loaded when agent explicitly invokes via Skill tool
- No size limit, but prefer splitting deep detail into refs/ for context efficiency

**Anti-patterns**:
- Missing or incomplete frontmatter
- Skill name not matching directory pattern
- Using same name as command (creates "skill already running" re-entry block)
- Putting user-facing documentation in skill (belongs in command)
- Loading all Tier 2 refs upfront

---

### REF FILE (Tier 2)

**Verbatim Template**:

```markdown
# <Title>

## Purpose
<what this ref contains and when to load it>

## Content
<the actual specification, algorithm, template, or rubric>

---
*Reference document for sc:<name>-protocol skill*
*Source: <original source attribution>*
```

**Hard Constraints**:
- **MUST** be independently useful (no dangling references requiring SKILL.md context)
- **MUST** have a `## Purpose` section explaining when to load it
- Loaded via `claude -p` with ref content as `--append-system-prompt`
- One ref per concern (do not combine scoring + templates in one file)

---

### AGENT

**Role**: NOT a primary component in this policy, but the invocation mechanism. Agents are instantiated during skill execution to perform specific work.

**How agents fit**:
- Skills define `## Agent Delegation`: which agents to spawn, their roles, dispatch config
- Agents invoke the Skill tool to load Tier 1 protocol
- Agents receive refs via `claude -p` (Tier 2) as context setup
- Agent `.md` files in `src/superclaude/agents/` are loaded via Read tool and injected into Task prompts (not via `subagent_type` — that field is dead metadata)

---

## 6. Naming Convention

### The `-protocol` Suffix Pattern

**Pattern**: `sc-{domain}-protocol` (directories), `sc:{domain}-protocol` (SKILL.md `name:` field)

**Why different names for command and skill are MANDATORY**:

```
WITHOUT SEPARATE NAMES (re-entry block):
User: /sc:adversarial
  → Skill "sc:adversarial" marked as running
  → Command tries to invoke Skill "sc:adversarial"
  → Framework blocks: "Skill already running"
  ❌ DEADLOCK

WITH SEPARATE NAMES (correct):
User: /sc:adversarial
  → Command "adversarial" loaded (no skill marker set)
  → Command invokes Skill "sc:adversarial-protocol"
  → Framework sees different name
  ✅ INVOCATION SUCCEEDS
```

### Convention Table

| Component | Pattern | Example | Location |
|-----------|---------|---------|----------|
| Command file | `<name>.md` | `adversarial.md` | `commands/<name>.md` |
| Command slug | `<name>` | `adversarial` | — |
| Skill directory | `sc-<name>-protocol/` | `sc-adversarial-protocol/` | `skills/sc-<name>-protocol/` |
| SKILL.md `name:` field | `sc:<name>-protocol` | `sc:adversarial-protocol` | SKILL.md frontmatter |
| Ref files | descriptive name | `debate-protocol.md` | `skills/sc-<name>-protocol/refs/` |
| Standalone skills (no paired command) | `<name>` (no prefix/suffix) | `confidence-check` | `skills/<name>/SKILL.md` |

**Rules**:
- Protocol skills MUST end in `-protocol` (both directory and frontmatter name)
- Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`
- Standalone skills (no matching command) do NOT use the `-protocol` suffix
- Command names NEVER include `-protocol`
- Directory names use hyphens (`sc-adversarial-protocol`); frontmatter `name:` uses colons (`sc:adversarial-protocol`) — directories cannot contain colons

---

## 7. The 5 Skills to Rename

All 5 affected skill directories must be renamed. Each rename requires:
1. Directory rename: `sc-<name>/` → `sc-<name>-protocol/`
2. SKILL.md frontmatter `name:` field update
3. Update to `.claude/skills/` dev copy (via `make sync-dev`)
4. Fix stale path references in command files

**⚠️ DO NOT TRUST ANY STAGED FILES**: The prior sprint was executed by a rogue agent. Any staged or partially-applied changes on the current branch should be treated as untrusted. All 5 skill renames must be executed fresh as part of this sprint. Do not assume any rename is already complete.

| Old Directory | New Directory | Old `name:` | New `name:` | Special Notes |
|---------------|---------------|-------------|-------------|---------------|
| `sc-adversarial/` | `sc-adversarial-protocol/` | `sc:adversarial` | `sc:adversarial-protocol` | |
| `sc-cleanup-audit/` | `sc-cleanup-audit-protocol/` | `cleanup-audit` | `sc:cleanup-audit-protocol` | Also fix missing `sc:` prefix |
| `sc-roadmap/` | `sc-roadmap-protocol/` | `sc:roadmap` | `sc:roadmap-protocol` | Body changes required (Wave 2 Step 3) |
| `sc-task-unified/` | `sc-task-unified-protocol/` | `sc-task-unified` | `sc:task-unified-protocol` | Major rewrite: 567→106 lines |
| `sc-validate-tests/` | `sc-validate-tests-protocol/` | `sc-validate-tests` | `sc:validate-tests-protocol` | Fix stale path on line 63 |

**Scale**: ~30 files renamed across 5 skill directories + 5 command updates + 10 dev copy mirrors.

---

## 8. Invocation Wiring

### The Correct Invocation Chain

```
User: /sc:roadmap --multi-roadmap
                  ↓
[TIER 0] roadmap.md auto-loaded (target ≤150, max ≤350 lines)
                  ↓
  Reads ## Activation: "Invoke Skill sc:roadmap-protocol"
                  ↓
[TIER 1] sc-roadmap-protocol/SKILL.md loaded via Skill tool
                  ↓
  Wave 2 Step 3: "Dispatch Task agent to invoke sc:adversarial-protocol"
                  ↓
[TASK AGENT] Spawned in fresh context (no re-entry conflict)
                  ↓
  Task agent invokes: Skill sc:adversarial-protocol
                  ↓
[TIER 1] sc-adversarial-protocol/SKILL.md loaded in Task agent context
                  ↓
  Adversarial pipeline executes (F1 → F2/3 → F4/5)
                  ↓
  Writes: <output-dir>/adversarial/return-contract.yaml
                  ↓
[BACK IN ROADMAP] Reads return-contract.yaml (Step 3e)
                  ↓
  Routes: Pass (≥0.6) | Partial (≥0.5) | Fail (<0.5)
```

### Task Agent vs Skill Tool vs claude -p

| Mechanism | Use Case | Context | Returns |
|-----------|----------|---------|---------|
| **Skill tool** | Invoke skill directly in current context | Loads SKILL.md into conversation | None (context-based) |
| **Task tool** | Delegate to sub-agent in fresh context | Spawns new agent | Prose response |
| **claude -p** | Inject ref/detail into current context | `--append-system-prompt` | None (becomes context) |
| **claude -p script** | Shell-script wrapper that invokes `claude -p` to run a sub-agent headlessly | Subprocess; SKILL.md passed as `--append-system-prompt` | File output (return contract written to disk) |

**Decision rule**:
- Need full skill protocol in current context? → Skill tool
- Need to invoke a skill without re-entry conflict? → Task tool (Task agent wrapper)
- Need step-specific detail without separate execution? → `claude -p` (ref loading)
- Need headless sub-agent invocation without spawning a full Task tool agent? → `claude -p` shell script (see below)

### The `claude -p` Script Strategy (Unfinalized — Under Consideration)

**Status**: This strategy was discussed and analyzed during planning but was **not finalized** for v2.01. It is documented here as an open design option for T01.01 probe and future refinement.

**Concept**: A shell script wraps the `claude -p` command to invoke a skill headlessly. The SKILL.md content is passed as `--append-system-prompt`. The sub-agent executes the skill protocol and writes its output (including `return-contract.yaml`) to disk. The parent workflow reads the file.

```bash
# Conceptual pattern (not yet implemented):
claude -p \
  --append-system-prompt "$(cat src/superclaude/skills/sc-adversarial-protocol/SKILL.md)" \
  --output-dir "<output-dir>/adversarial/" \
  "Execute the adversarial pipeline with these inputs: ..."
```

**Why not yet finalized**:
- T01.01 probe returned `TOOL_NOT_AVAILABLE` in prior sprint environment — whether this applies to `claude -p` subprocess invocation is unverified
- The `--append-system-prompt` flag behavior for SKILL.md injection size limits is unknown
- Interaction between `claude -p` subprocess and the parent conversation's file system is unspecified
- No probe fixtures exist yet (referenced in §16 as "References That Don't Exist Yet")

**T01.01 scope**: The T01.01 probe must also test this strategy. If `claude -p` script invocation is viable, it becomes a third invocation path alongside Skill tool and Task tool, potentially replacing the Task agent wrapper with a lighter-weight mechanism.

### `allowed-tools` Requirement

Both the command file AND the SKILL.md must declare `Skill` in their `allowed-tools` list for invocation to work:

```yaml
# In command frontmatter (e.g., roadmap.md):
allowed-tools: [Read, Grep, Glob, Bash, Skill, ...]

# In SKILL.md frontmatter:
allowed-tools: [Read, Write, Edit, Task, Skill, ...]
```

**Current status**: All 5 commands are missing `Skill` in `allowed-tools` (BUG-001). This is Phase 3 work.

---

## 9. Fallback Protocol (FALLBACK-ONLY Variant)

### Critical Finding: TOOL_NOT_AVAILABLE

**T01.01 Probe Result** (Decision D-0001): The Skill tool has no callable API for skill-to-skill invocation in the current environment. Attempting to invoke `Skill sc:adversarial-protocol` from within another skill execution returns `TOOL_NOT_AVAILABLE`.

**Impact** (Decision D-0002): The entire sprint variant is **FALLBACK-ONLY**. The primary `claude -p` headless path is conceptually designed but not executable. Task agent dispatch is the sole viable invocation path.

### The Fallback Protocol (Wave 2 Step 3 — Sub-steps 3a–3f)

```
3a: Parse agent specs from --agents flag (or SKILL.md FR-008 section)
    Output: agent list with invocation hints

3b: Expand agent specs with model/persona
    Output: variant configurations

3c: Add debate-orchestrator if agent_count >= 3
    Output: orchestrator config (threshold: >=3, not >=5)

3d: Execute fallback protocol
    ├─ F1: Variant generation
    │     Task agents generate variants (one per expanded spec)
    ├─ F2/3: Diff analysis + adversarial debate (merged stage)
    │     Diff against spec; parallel advocates → sequential rebuttals
    └─ F4/5: Base selection + merge + contract (merged stage)
          Select winning variant (convergence_score driven)
          Produce return-contract.yaml
    Output: return-contract.yaml written to <output-dir>/adversarial/

3e: Consume return contract
    ├─ Missing-file guard: If no contract → skip (return empty result)
    ├─ YAML parse error: If parse fails → use fallback convergence_score: 0.5
    └─ 3-status routing:
          IF convergence_score >= 0.6 → PASS (proceed)
          ELIF convergence_score >= 0.5 → PARTIAL (continue with warnings)
          ELSE → FAIL (abort + escalate)

3f: Skip primary template (no-op in FALLBACK-ONLY variant)
    Note: This step remains for future when claude -p becomes available
```

### Convergence Threshold Design

- **Routing threshold**: 0.6 (below this = low-confidence output)
- **Fallback sentinel**: 0.5 (deliberately below threshold; forces Partial path when no real convergence measurement possible)
- **Implication**: In fallback-only mode, ALL results where real convergence can't be computed are routed through the Partial path — this is by design, not a bug

---

## 10. Return Contract Schema

### Canonical 10-Field Schema

| Field | Owner | Type | Example | Purpose |
|-------|-------|------|---------|---------|
| `status` | Producer | `enum` | `success\|partial\|failed` | Pipeline outcome |
| `merged_output_path` | Producer | `path\|null` | `./adversarial/merged.md` | Where merged result lives |
| `convergence_score` | Producer | `float 0.0-1.0` | `0.73` | Real consensus measurement |
| `artifacts_dir` | Producer | `path` | `./adversarial/` | All intermediate artifacts |
| `unresolved_conflicts` | Producer | `list[string]` | `["diff-003", "diff-007"]` | Conflicts that didn't converge |
| `fallback_mode` | Consumer | `bool` | `false` | `true` when Task-agent fallback used |
| `base_variant` | Consumer | `string\|null` | `opus:architect` | Winning variant from scoring |
| `schema_version` | Consumer | `string` | `"1.0"` | Fixed; additive-only semantics |
| `failure_stage` | Consumer | `string\|null` | `"F3 debate round 2"` | Where failure occurred |
| `invocation_method` | Consumer | `enum` | `"task_agent"` | `"headless"\|"task_agent"` |

### Consumer Defaults (Dual-Format Handling)

```yaml
# If field is absent, consumer applies these defaults:
schema_version: "0.0"        # absent = unknown schema
fallback_mode: false          # absent = assume headless (primary path)
base_variant: null            # absent = no winning variant
failure_stage: null           # absent = no failure
invocation_method: "headless" # absent = assume primary path
unresolved_conflicts: []      # absent = no conflicts
```

### Return Contract File Location

```
<output-dir>/adversarial/return-contract.yaml
```

This file-based transport decouples producer (skill) from consumer (parent workflow). The consumer reads the file after Task agent completion — no in-memory data channel needed.

### `## Return Contract` Section in SKILL.md

Every protocol SKILL.md MUST include a `## Return Contract` section specifying the expected output structure.

---

## 11. Enforcement Mechanisms + Verification Scripts

### `make lint-architecture` (New Target)

**Purpose**: Enforce `docs/architecture/command-skill-policy.md` at PR time.

**Validation Pipeline**:
```
sync-dev          -->  verify-sync       -->  lint-architecture
(copy src->.claude)    (diff check)           (policy enforcement)
```

### All 10 Policy-Defined Checks

| # | Check | Severity | Status | What It Validates |
|---|-------|----------|--------|------------------|
| 1 | Command → Skill link | ERROR | **DESIGNED** | Commands with `## Activation` reference existing skill directory |
| 2 | Skill → Command link | ERROR | **DESIGNED** | Each `sc-*-protocol/` has corresponding command file |
| 3 | Command size (warn) | WARN | **DESIGNED** | Command file >200 lines |
| 4 | Command size (error) | ERROR | **DESIGNED** | Command file >500 lines |
| 5 | Inline protocol in command | ERROR | **NEEDS DESIGN** | Command with matching `-protocol` skill contains YAML code blocks >20 lines |
| 6 | Activation section present | ERROR | **DESIGNED** | Commands with `-protocol` skill missing `## Activation` |
| 7 | Activation references correct skill | ERROR | **NEEDS DESIGN** | `## Activation` does not contain `Skill sc:<name>-protocol` |
| 8 | Skill frontmatter complete | ERROR | **DESIGNED** | SKILL.md missing `name:`, `description:`, `allowed-tools:` |
| 9 | Protocol naming consistency | ERROR | **DESIGNED** | Skill directory SKILL.md `name:` field ends in `-protocol` |
| 10 | Sync integrity | ERROR | **DELEGATED** | `src/` ↔ `.claude/` parity (delegated to `verify-sync`) |

**Exit behavior**: Any ERROR → `exit 1` (CI failure). Warnings only → `exit 0`.

### `make sync-dev` Changes

**Remove**: 4-line skill-skip heuristic that stripped `sc-` prefix and skipped syncing if a command of that name existed.

**New behavior**: Sync ALL skills including `-protocol` ones. Commands delegate TO skills; both must exist in `.claude/`.

### `make verify-sync` Changes

**Remove**: 5-line skip heuristic with user-facing message ("served by command").

**New behavior**: Check ALL skills for sync drift, enforce `-protocol` naming.

### Verification Script Examples

```bash
# Check 1/2: Bidirectional links
for f in src/superclaude/commands/*.md; do
  if grep -q "## Activation" "$f"; then
    skill_ref=$(grep "Skill sc:" "$f" | sed 's/.*Skill sc:/sc-/' | sed 's/-protocol.*/-protocol/')
    test -d "src/superclaude/skills/$skill_ref/" && echo "PASS: $f" || echo "FAIL: $f"
  fi
done

# Check 3/4: Command size limits
for f in src/superclaude/commands/*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 500 ]; then echo "ERROR: $f ($lines lines)"
  elif [ "$lines" -gt 200 ]; then echo "WARN: $f ($lines lines)"
  fi
done

# Check 6: Activation section present in paired commands
for d in src/superclaude/skills/sc-*-protocol/; do
  cmd_name=$(basename "$d" | sed 's/^sc-//' | sed 's/-protocol$//')
  grep -q "## Activation" "src/superclaude/commands/$cmd_name.md" && echo "PASS: $cmd_name" || echo "FAIL: $cmd_name"
done

# Check 8: Skill frontmatter validation
for d in src/superclaude/skills/sc-*-protocol/SKILL.md; do
  for field in "name:" "description:" "allowed-tools:"; do
    grep -q "$field" "$d" || echo "FAIL: $d missing $field"
  done
done

# Check 9: Naming consistency
for d in src/superclaude/skills/sc-*-protocol/SKILL.md; do
  name=$(grep "^name:" "$d" | head -1)
  echo "$name" | grep -q ".*-protocol" && echo "PASS" || echo "FAIL: $d -> $name"
done

# Post-rename stale reference check
grep -rn "sc-adversarial/" src/ .claude/ docs/ --include="*.md" || echo "CLEAN"
grep -rn "sc-cleanup-audit/" src/ .claude/ docs/ --include="*.md" || echo "CLEAN"
grep -rn "sc-roadmap/" src/ .claude/ docs/ --include="*.md" || echo "CLEAN"
grep -rn "sc-task-unified/" src/ .claude/ docs/ --include="*.md" || echo "CLEAN"
grep -rn "sc-validate-tests/" src/ .claude/ docs/ --include="*.md" || echo "CLEAN"
```

---

## 12. Bug Inventory

| Bug ID | Severity | Description | Affected Files | Fix |
|--------|----------|-------------|----------------|-----|
| **BUG-001** | HIGH 🔴 | All 5 commands missing `Skill` in `allowed-tools`. If Claude Code enforces tool whitelists, all command invocations fail at skill dispatch. | `adversarial.md`, `cleanup-audit.md`, `roadmap.md`, `task-unified.md`, `validate-tests.md` (+ their `.claude/` copies) | Add `Skill` to `allowed-tools` in all 5 |
| **BUG-002** | MEDIUM 🟡 | `validate-tests.md` line 63 still references old path `skills/sc-validate-tests/classification-algorithm.yaml` (pre-rename). | `validate-tests.md` | Update line 63 to `sc-validate-tests-protocol/` |
| **BUG-003** | MEDIUM 🟡 | Orchestrator threshold inconsistency: step 3c says `agent_count >= 3`; Section 5 says `>= 5`. D-0006 specifies `>= 3`. | `sc-roadmap-protocol/SKILL.md` | Align all references to `>= 3` |
| **BUG-004** | MEDIUM 🟡 | Architecture policy duplicated: `docs/architecture/command-skill-policy.md` and `src/superclaude/ARCHITECTURE.md` are byte-identical. No canonical source. | Both files | Designate `docs/architecture/` as canonical; symlink from `src/superclaude/` |
| **BUG-005** | MEDIUM 🟡 | Wave 0 Step 5 in `sc-roadmap-protocol/SKILL.md` references stale path `src/superclaude/skills/sc-adversarial/SKILL.md` (pre-rename). | `sc-roadmap-protocol/SKILL.md` | Update to `sc-adversarial-protocol/SKILL.md` |
| **BUG-006** | HIGH 🔴 | `roadmap.md` `## Activation` section references old path `src/superclaude/skills/sc-roadmap/SKILL.md` instead of `Skill sc:roadmap-protocol`. This breaks the entire invocation chain for the primary command. | `roadmap.md`, `.claude/commands/sc/roadmap.md` | Rewrite `## Activation` to use `Skill sc:roadmap-protocol` |

---

## 13. Phase Plan (6 Phases, 18 Tasks)

> **⚠️ ALL PHASES ARE TODO**
> The codebase was rolled back to commit `5733e32`. All implementation work from the prior sprint was erased. No phase is complete. Begin from Phase 1, Task 1.
>
> Before executing any phase work, verify current state against §15 "Status at Rollback + Current Branch State."

---

### Phase 1: Foundation ⏳ TODO

| Task | Description | Compliance | Notes |
|------|-------------|------------|-------|
| T01.01 | Skill tool probe (empirical `claude -p` viability test) | EXEMPT | Re-run in current environment. Prior result: `TOOL_NOT_AVAILABLE` → fallback-only variant. Verify this still holds. |
| T01.02 | Prerequisite validation (all checks) | EXEMPT | Verify all files exist, build targets valid, branch state clean. |
| T01.03 | Tier classification policy — executable `.md` files are NOT exempt | EXEMPT | Apply Rule 7.6: skills/commands/agents are STANDARD minimum. |

**Phase 1 Exit Criteria**: T01.01–T01.03 complete. Variant decision documented. Current state verified.

---

### Phase 2: Invocation Wiring ⏳ TODO

> **Blocked on Phase 1 completion.**

| Task | Description | Compliance | Notes |
|------|-------------|------------|-------|
| T02.01 | Add `Skill` to `roadmap.md` `allowed-tools` | LIGHT | Part of BUG-001 fix. |
| T02.02 | Add `Skill` to `sc-roadmap-protocol/SKILL.md` `allowed-tools` | LIGHT | Part of BUG-001 fix. |
| T02.03 | Rewrite Wave 2 Step 3 (6 sub-steps 3a–3f, fallback F1/F2-3/F4-5, return contract routing) | STRICT | Must pass 8-point audit (see §9). |
| T02.04 | Fix BUG-006: Rewrite `roadmap.md` `## Activation` to reference `Skill sc:roadmap-protocol` | LIGHT | Not in prior sprint. Required before any invocation test. |

**Phase 2 Exit Criteria**: Wave 2 Step 3 8-point audit passes. `roadmap.md` activation chain is valid end-to-end.

---

### Phase 3: Build System ⏳ TODO

> **⚠️ MUST precede Phase 4 (Rule 7.5: Enforcement BEFORE Migration)**

| Task | Description | Compliance |
|------|-------------|------------|
| T03.01 | Remove skill-skip heuristic from `sync-dev` and `verify-sync` | STANDARD |
| T03.02 | Add `lint-architecture` target to Makefile (6 designed checks) | STANDARD |
| T03.03 | Run `make lint-architecture` against current tree; all ERRORs must be resolved before Phase 4 | STANDARD |

**Phase 3 Exit Criteria**: `make lint-architecture` runs without errors on the current codebase state.

---

### Phase 4: Structural Validation ⏳ TODO

> **Blocked on Phase 3 completion.**

| Task | Description | Compliance |
|------|-------------|------------|
| T04.01 | Return contract validation (consumer routing tests) | STRICT |
| T04.02 | Adversarial pipeline integration tests | STRICT |
| T04.03 | Artifact gate specification and standards | STRICT |

---

### Phase 5: Polish ⏳ TODO

| Task | Description | Compliance |
|------|-------------|------------|
| T05.01 | Verb-to-tool glossary (disambiguates "Invoke" → Bash/`claude -p` vs "Dispatch" → Task tool) | STANDARD |
| T05.02 | Wave 1A Step 2 fix (semantic alignment) | STANDARD |
| T05.03 | Pseudo-CLI invocation conversion | STANDARD |

---

### Phase 6: Integration & Closure ⏳ TODO

| Task | Description | Priority |
|------|-------------|----------|
| T06.01 | Cross-skill invocation pattern documentation | HIGH |
| T06.02 | Tier 2 ref loader design (`claude -p` script) | HIGH |
| T06.03 | `task-unified.md` major extraction (-461 lines, 567→106) | HIGH |
| T06.04 | Remaining 4 command files — add `## Activation` + fix BUG-001 for each | HIGH |
| T06.05 | Architecture policy duplication resolution (BUG-004) | MEDIUM |
| T06.06 | Fix BUG-002 (validate-tests stale path) + BUG-003 (orchestrator threshold) | MEDIUM |

### 13.7 Execution Dependency DAG

```
Layer 0 (Foundation — ALWAYS FIRST):
  docs/architecture/command-skill-policy.md
        |
        v
Layer 1 (Skill Renames — execute fresh, do NOT rely on any staged rogue-agent work):
  src/superclaude/skills/sc-{all 5}-protocol/
        |
        v
Layer 2 (Enforcement Infrastructure — BEFORE any command migration):
  Makefile: sync-dev + verify-sync + lint-architecture
  make lint-architecture → must pass (exit 0) before Layer 3
        |
        v
Layer 3 (Command Updates — depend on Layer 1 naming):
  src/superclaude/commands/{5 paired commands}
  → ## Activation sections
  → allowed-tools frontmatter (Skill)
        |
        v
Layer 4 (Dev Copies — depend on Layer 1 + 3):
  .claude/commands/sc/{all 5} + .claude/skills/sc-{all 5}-protocol/
  → make sync-dev && make verify-sync
        |
        v
Layer 5 (Validation — depends on all above):
  make sync-dev && make verify-sync && make lint-architecture
  → T04 integration tests
```

**No circular dependencies. Clean DAG.**

**⚠️ ATOMIC CHANGE GROUPS**: The following files MUST be changed together per command. Partial changes produce broken references.

**Group A: Per-Command Unit** (repeat for each of 5 paired commands):

| File | Change |
|------|--------|
| `src/superclaude/commands/{name}.md` | Add/rewrite `## Activation` section + `Skill` in `allowed-tools` |
| `.claude/commands/sc/{name}.md` | Identical change (sync copy) |
| `src/superclaude/skills/sc-{name}-protocol/SKILL.md` | Frontmatter update |
| `.claude/skills/sc-{name}-protocol/` | New dev copy directory (via `make sync-dev`) |

**Group B: Makefile Enforcement**:

| File | Change |
|------|--------|
| `Makefile` (sync-dev) | Remove skip logic |
| `Makefile` (verify-sync) | Remove skip logic |
| `Makefile` (lint-architecture) | Add new target |
| `Makefile` (.PHONY, help) | Reference new target |

---

## 14. v2.01 vs v2.02 Explicit Boundary

### ✅ IN SCOPE: v2.01 Architecture Refactor

| Item | Status |
|------|--------|
| 3-tier loading model definition and policy | DONE (policy doc exists) |
| 5 skill directory renames to `-protocol` suffix | TODO (rogue-agent staged work — untrusted, redo from scratch) |
| 5 command `## Activation` section additions | TODO (rollback erased) |
| All 5 commands `allowed-tools` update (BUG-001) | TODO |
| BUG-006 fix (roadmap.md Activation old path) | TODO |
| Wave 2 Step 3 decomposition (3a–3f, fallback F1/F2-3/F4-5) | TODO (rollback erased) |
| Return contract routing (Step 3e, convergence threshold 0.6) | TODO (rollback erased) |
| `make lint-architecture` target (6 of 10 checks) | TODO |
| `make sync-dev` + `make verify-sync` heuristic removal | TODO |
| BUG-002 through BUG-005 fixes | TODO |
| Phase 3–6 tasks | TODO |

### ❌ OUT OF SCOPE: v2.02-Roadmap-v3 Features

| Item | Why Deferred |
|------|-------------|
| RC3+S03: Agent dispatch convention (debate-orchestrator selection) | Latent defect; surfaces after v2.01 fixes |
| RC5+S05: Full Claude behavioral fallback quality gate (2-tier) | Partial coverage in v2.01; full gate is v2.02 work |
| Primary `claude -p` headless implementation | TOOL_NOT_AVAILABLE; architectural design done, implementation deferred |
| DVL verification scripts (Tier 2 and 3: scripts 4–7) | Post-implementation utilities; not sprint-critical |
| Framework-level Skill Return Protocol (cross-framework standard) | Requires RFC/consensus |
| Agent registry and framework-level agent dispatch | TypeScript v5.0 long-term |
| `--invocation-mode` flag | YAGNI — internal routing, user-facing flag unjustified |
| Phases 3–6 CI checks (4 remaining policy checks — #5 and #7 need design) | Phase 3 not started |
| Tier 2 ref loader design (`claude -p` script) | Phase 6 backlog |
| Runtime scope control (file-set limits) | CRITICAL gap — not yet designed (see §16) |
| **v2.02-Roadmap-v3 roadmap generation improvements** | Separate release, separate branch |

---

## 15. Status at Rollback + Current Branch State

### Why the Rollback Happened

The rollback occurred because during deep analysis and planning, Claude's conversation was compacted and it moved out of planning mode — making unauthorized changes throughout the framework under half-cooked plans. Specific failure conditions:

1. **BUG-001 unresolved**: 4 of 5 commands missing `Skill` in `allowed-tools` → 80% of command invocations would fail at skill dispatch
2. **Incomplete migration**: Commands had `## Activation` sections but no permission gates → invocation blocked by Claude Code
3. **Atomic unit broken**: The entire change set must be applied atomically — partial migration breaks invocation wiring for all affected commands
4. **Planning session went rogue**: Context compaction caused Claude to start implementing instead of planning
5. **Scale**: Agent planned 4 files, executed 68 file changes — zero scope control

### What Survived the Rollback (Design Artifacts Only)

These artifacts are preserved in `.dev/releases/` and this spec synthesizes them. They are **not in the codebase**:

| Artifact | Location | Value |
|----------|----------|-------|
| Architecture policy document | `docs/architecture/command-skill-policy.md` | Primary: YES (check if still present) |
| 5 skill directory renames | ⚠️ Rogue-agent work — untrusted | Treat as TODO; redo from scratch |
| Decision artifacts D-0001 through D-0008 | `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/` | Reference only |
| Adversarial design pipeline outputs | `.dev/releases/backlog/` | Reference only |

### Current Branch State (feature/v2.01-Roadmap-V3, commit 9060a65)

| Component | Count | Source Location | Dev Copy Location | Sync Status |
|-----------|-------|----------------|-------------------|-------------|
| Commands | 37 | `src/superclaude/commands/` | `.claude/commands/sc/` | IN SYNC |
| Skills | 6 dirs, 33 files | `src/superclaude/skills/` | `.claude/skills/` | **NOT IN SYNC** |
| Agents | 27 | `src/superclaude/agents/` | `.claude/agents/` | IN SYNC |

**Commands over 200 lines (extraction candidates)**:

| Command | Lines | Has Paired Skill? | Priority |
|---------|-------|-------------------|----------|
| `recommend.md` | 1005 | No | High |
| `review-translation.md` | 913 | No | High |
| `pm.md` | 592 | No | Medium |
| `task-unified.md` | 567 | Yes (`sc-task-unified-protocol`) | Medium |
| `spec-panel.md` | 435 | No | Medium |
| `task-mcp.md` | 375 | No | Medium |

**Activation section coverage**:

| Metric | Count |
|--------|-------|
| Commands with `## Activation` section | **1** (`roadmap.md` — broken path) |
| Commands that need `## Activation` (have paired skill) | **5** |
| Commands with `Skill` in `allowed-tools` | **0** |
| Commands using `allowed-tools` frontmatter at all | **1** (`roadmap.md`) |

**Skill sync status** (`.claude/skills/` `-protocol` dirs contain only empty shells):

| Skill Directory | src/ Files | .claude/ Files | Status |
|---|---|---|---|
| `confidence-check` | 3 | 2 | MISMATCH |
| `sc-adversarial-protocol` | 6 | 0 | EMPTY |
| `sc-cleanup-audit-protocol` | 12 | 0 | EMPTY |
| `sc-roadmap-protocol` | 7 | 0 | EMPTY |
| `sc-task-unified-protocol` | 2 | 0 | EMPTY |
| `sc-validate-tests-protocol` | 3 | 0 | EMPTY |

**Day 1 verification procedure**: Before beginning any Phase 1 task, run:
```bash
git status                                    # Check for any rogue-agent staged changes (treat all as untrusted)
ls docs/architecture/command-skill-policy.md  # Confirm policy doc exists
grep -l "## Activation" src/superclaude/commands/*.md  # Should return only roadmap.md
grep "Skill" src/superclaude/commands/roadmap.md | head -5  # Check allowed-tools
```

---

## 16. Open Issues and Gaps

### Unimplemented Spec-v2 Requirements

| Requirement | Impact if Missing | Priority |
|-------------|------------------|----------|
| `unresolved_conflicts` as `list[string]` (not integer) | Integer loses conflict detail; consumers cannot act on specific conflicts | HIGH |
| `invocation_method` field in return contract | Cannot distinguish headless vs task_agent in logs | HIGH |
| 4-state artifact scan (A/B/C/D states) | Mid-pipeline resume cannot detect existing artifacts | MEDIUM |
| `schema_version: "1.0"` field | No versioning for contract evolution | MEDIUM |
| SKILL.md content validation (empty + ARG_MAX check) | Silent failure on empty or oversized SKILL.md injection | HIGH |
| Budget ceiling (2× BUDGET) | Unbounded adversarial cost | LOW |
| Schema ownership model documentation | No producer/consumer contract for field evolution | MEDIUM |
| Exact SKILL.md heading matching algorithm | Fragile line-number references not replaced with heading matches | MEDIUM |

### Policy Gaps

| # | Gap | Priority | Notes |
|---|-----|----------|-------|
| 1 | `claude -p` Tier 2 ref loader not designed | HIGH | Policy references `claude -p` for ref files but provides no script. Full 3-tier model is incomplete without this. |
| 2 | Cross-skill invocation not specified | HIGH | No specification for how one protocol skill invokes another. T01.01 probe returned TOOL_NOT_AVAILABLE. |
| 3 | `__init__.py` purpose undefined | LOW | Present in skill directories but policy never explains purpose. |
| 4 | `argument-hint` frontmatter — required or optional? | LOW | Present in Skill Contract template but not validated by CI checks. |
| 5 | Standalone skill contract not fully specified | MEDIUM | Policy says standalone skills don't use `-protocol` suffix but provides no contract template. |
| 6 | Command frontmatter not CI-validated | MEDIUM | Only skill frontmatter is checked (Check 8). No check validates command frontmatter completeness. |
| 7 | No rollback procedure documented | MEDIUM | Migration checklist defines forward path only. |

### References That Don't Exist Yet

- `refs/headless-invocation.md` (referenced by `approach-2`, `merged-approach`, `spec-v2`)
- Probe fixtures (`spec-minimal.md`, `variant-a.md`, etc.)
- `expected-schema.yaml` (referenced in `approach-1` Appendix B)

---

## 16b. Risk Assessment

### Partial Application Risks

| Partial Application | What Breaks | Severity |
|---------------------|-------------|----------|
| Commands updated, skills NOT renamed | `Skill sc:*-protocol` invocations fail (skill directories don't exist under new names) | CRITICAL |
| Skills renamed, commands NOT updated | Old commands reference old skill names or use implicit loading | CRITICAL |
| `lint-architecture` added, skills NOT renamed | Check 2 and Check 6 fail (expect `-protocol` directories) | HIGH |
| Makefile skip-heuristic removed, skills NOT renamed | `sync-dev` creates redundant `.claude/skills/sc-*` directories | MEDIUM |
| `.claude/` updated, `src/` NOT updated | `make verify-sync` fails; source-of-truth diverges | HIGH |
| `src/` updated, `.claude/` NOT updated | Claude Code reads stale skill content; runtime behavior mismatch | HIGH |
| BUG-001 unresolved when commands are refactored | `Skill` invocations blocked by tool whitelist → silently ignored | CRITICAL |

### Test Coverage Gaps

| Change | Test Coverage | Gap Severity |
|--------|---------------|--------------|
| Command-skill activation flow | NONE — no test verifies `Skill sc:X-protocol` loads the skill | HIGH |
| `allowed-tools` enforcement | NONE — no test verifies tool whitelist is respected | HIGH |
| `task-unified.md` content extraction | NONE — no test verifies 106-line command still works | HIGH |
| Skill directory renames | PARTIAL — `lint-architecture` validates naming | MEDIUM |
| Makefile `sync-dev` behavior change | PARTIAL — `verify-sync` checks parity | MEDIUM |
| `lint-architecture` correctness | NONE — no test verifies the 6 checks produce correct results | MEDIUM |

### Recommended Test Additions (Phase 4)

1. **Integration test**: Invoke each command and verify skill activation loads the correct skill
2. **Regression test**: Verify `task-unified` performs tier classification correctly after extraction
3. **Positive lint test**: Run `make lint-architecture` against the final tree and verify exit 0
4. **Negative lint test**: Verify `make lint-architecture` fails when a skill is missing or `## Activation` is absent
5. **`allowed-tools` test**: Verify `Skill` tool works for commands where it is/isn't in `allowed-tools`

### The Critical Unsolved Problem: Runtime Scope Control

This is the most significant architectural gap. The rollback incident's primary symptom — an agent changing 68 files when 4 were planned — **cannot be prevented by the current architecture**. The 3-tier loading model addresses instruction quality but not execution boundaries.

Possible approaches (not yet evaluated):
- File-set declarations in command/skill boundaries
- Plan presentation gates before execution
- Boundary enforcement via tool permissions
- Atomic change group declarations

**⚠️ This sprint does NOT solve runtime scope control. It is explicitly OUT OF SCOPE for v2.01.**

---

## 17. Key Architectural Decisions (Decision Log)

| Decision ID | Decision | Rationale | Impact |
|-------------|----------|-----------|--------|
| D-0001 | Skill tool probe result: `TOOL_NOT_AVAILABLE` | Empirical finding; cannot be changed | Forces FALLBACK-ONLY variant for entire sprint |
| D-0002 | Sprint variant: FALLBACK-ONLY | Probe result eliminates primary path | Task agent dispatch is sole viable invocation mechanism |
| D-0003 | 6/6 prerequisites pass | All files exist, build targets valid | Phase 2+ gates cleared (re-verify before this sprint) |
| D-0004 | Add `Skill` to `roadmap.md` `allowed-tools` | Required for skill invocation to work | BUG-001 partial fix |
| D-0005 | Add `Skill` to SKILL.md `allowed-tools` | Required for skill invocation to work | BUG-001 partial fix |
| D-0006 | Wave 2 Step 3 decomposition (3a–3f) | Ambiguous "Invoke" verb had no tool binding | Executable specification with explicit tool dispatch |
| D-0007 | Fallback protocol F1/F2-3/F4-5 | FALLBACK-ONLY requires reliable fallback | 5-step cascade covering 3 error types |
| D-0008 | Return contract routing inline in Step 3e | Decouples producer from consumer | File-based YAML transport pattern |
| D-T01.03 | Executable `.md` files NOT exempt from compliance | `.md` extension ≠ documentation; SKILL.md is code | 9 downstream tasks → STRICT/STANDARD/LIGHT tiers |
| C-003 | Primary/fallback hierarchy (NOT peer mechanisms) | Architectural clarity; one correct path | All invocation goes through one design |
| C-004 | REJECTED: `--invocation-mode` flag | YAGNI; internal routing choice, not user-facing | Complexity eliminated |
| C-006 | `invocation_method` field in return contract | Observability without branching | Consumers can log but not branch on invocation method |
| T01.03 | Convergence threshold: 0.6 | Below = low-confidence partial results | Routing gate for Pass/Partial/Fail |
| T01.03 | Fallback sentinel: 0.5 | Deliberately below threshold; forces Partial path | All fallback results where convergence unmeasurable → Partial |

> **Note**: D-0003 through D-0008 were derived in the prior sprint. Re-verify D-0001 (TOOL_NOT_AVAILABLE) in T01.01 to confirm the fallback-only variant still applies in the current environment.

---

## 18. Policy Document Reference

**File**: `docs/architecture/command-skill-policy.md`
**Version**: 1.0.0
**Authored**: 2026-02-23
**Sections**:
1. Overview and Metaphor
2. Three-Tier Model (Tier 0/1/2)
3. Naming Conventions
4. Command File Contract (template + constraints)
5. Protocol Skill Contract (template + constraints)
6. Ref File Convention (template + constraints)
7. Invocation Patterns (Skill tool, Task tool, `claude -p`)
8. Anti-Patterns (Command, Skill, Ref, Invocation)
9. CI Enforcement (10 checks for `make lint-architecture`)
10. Migration Checklist (4-phase migration plan)
11. Architectural Decision Log

**⚠️ WARNING**: A byte-identical duplicate exists at `src/superclaude/ARCHITECTURE.md`. This is BUG-004. Resolve before Phase 6 closes.

---

## Appendix: Sources

### Merge Provenance

| Section | Source | Operation |
|---------|--------|-----------|
| §1–2, §6–10, §13 (base), §14, §17–18 | Doc-A (`v2.01_spec-planning-sonnet.md`) | Base (R1 applied: phases reset to TODO) |
| §5 verbatim templates | Doc-B §4.2–4.4 | R6 augmentation |
| §11 CI checks table + scripts | Doc-A §11 + Doc-B §5 | R5 augmentation |
| §12 BUG-006 | Doc-B §8.3 | R1 augmentation (missing from Doc-A) |
| §13.7 DAG + atomic groups | Doc-B §6.8 | R3 augmentation |
| §15 Current Branch State | Doc-B §3 | R8 augmentation |
| §16b Risk Assessment | Doc-B §10 | R4 augmentation |
| §3 RC-6, RC-7, cross-reference table | Doc-B §2 | R7 augmentation |
| Process requirements | → Serena memory `v2.01/process-requirements-rollback-lessons` | R2 (excluded from spec) |

### Extraction Files (12)

| # | File | Content Focus |
|---|------|--------------|
| 1 | `extract-synthesis-planning.md` | 3-Tier model, naming conventions, CI requirements |
| 2 | `extract-synthesis-artifacts.md` | Spec quality patterns, adversarial QA, root cause patterns |
| 3 | `extract-synthesis-framework.md` | Command-skill decoupling, `-protocol` naming, atomic change groups |
| 4 | `extract-instructions-master-renames.md` | Skill rename procedure, verification checklists |
| 5 | `extract-instructions-commands-makefile.md` | Activation template, `lint-architecture` spec |
| 6 | `extract-instructions-planning-artifacts.md` | Sprint artifact structure, evidence chains |
| 7 | `extract-context-commands-skills.md` | Traceability gaps, `allowed-tools` inconsistency |
| 8 | `extract-context-makefile-adversarial.md` | 10-check vs 6-check gap, sync-dev requirements |
| 9 | `extract-context-traceability.md` | Consolidated bug list, cross-category dependency model |
| 10 | `extract-policy-command-skill.md` | Verbatim policy: 3-tier model, contracts, naming |
| 11 | `extract-root-cause-analysis.md` | 7 root causes with evidence |
| 12 | `extract-current-state-inventory.md` | 37 commands, 6 skills, 27 agents: sizes, sync status |

---

*Merged Sprint Spec — v2.01 Architecture Refactor*
*Base: Doc-A (v2.01_spec-planning-sonnet.md) | Augmented: Doc-B (v2.01-spec-planning.md)*
*Merge method: sc:adversarial 5-round/3-agent debate, operations R1–R8 (R2 → Serena memory)*
*Generated: 2026-02-24*
