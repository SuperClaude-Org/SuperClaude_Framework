# Framework Analysis: sc:task vs sc:task-unified

**Date**: 2026-02-22
**Branch**: feature/v2.0-Roadmap-v2
**Scope**: Command and skill separation analysis for task-related components

---

## Executive Summary

**Verdict: sc:task and sc:task-unified are NOT two distinct, co-existing commands. They represent two VERSIONS of the same command at different evolutionary stages.**

The repository contains three task-related command files:

| File | Status | Role |
|------|--------|------|
| `task.md` | **Legacy v1.x** | Original task orchestration command |
| `task-mcp.md` | **Deprecated** | MCP compliance enforcement (explicitly deprecated by `task-unified`) |
| `task-unified.md` | **Current v2.0.0** | Unified replacement merging `task.md` + `task-mcp.md` |

`task-unified.md` is the canonical successor. It absorbed the orchestration capabilities of `task.md` and the compliance enforcement of `task-mcp.md` into a single command. The SKILL.md for `sc-task-unified` is the only skill backing any of these commands. There is no separate `sc-task` skill directory.

However, the legacy `task.md` command file **still exists and is still installed** to `.claude/commands/sc/task.md`, meaning Claude Code can still route to it via `/sc:task`. This creates a potential routing ambiguity: both `task.md` and `task-unified.md` respond to `/sc:task` invocations, and the SKILL.md references `/sc:task` as a trigger.

---

## sc:task Profile (Legacy v1.x)

**Source file**: `src/superclaude/commands/task.md`

### Identity

| Field | Value |
|-------|-------|
| **Frontmatter name** | `task` |
| **Description** | "Execute complex tasks with intelligent workflow management and delegation" |
| **Category** | special |
| **Complexity** | advanced |
| **Version** | Not specified (pre-v2.0) |

### Purpose

General-purpose task orchestration focused on:
- Multi-agent coordination and delegation
- Structured workflow management with cross-session persistence
- Intelligent MCP server routing
- Hierarchical task breakdown (Epic > Story > Task)

### Behavioral Flow

5-step linear pipeline:
1. Analyze (parse requirements)
2. Delegate (route to MCP/personas)
3. Coordinate (execute with parallel processing)
4. Validate (quality gates)
5. Optimize (enhancement recommendations)

### Flags

| Flag | Options |
|------|---------|
| `--strategy` | systematic, agile, enterprise |
| `--parallel` | Enable parallel processing |
| `--delegate` | Enable sub-agent delegation |

**No compliance flags.** This is the key distinction -- the original `task.md` has no concept of tiered compliance enforcement.

### MCP Servers

All six servers listed: Sequential, Context7, Magic, Playwright, Morphllm, Serena

All treated as equally available; no tier-based conditional activation.

### Personas

7 personas: architect, analyzer, frontend, backend, security, devops, project-manager

### Key Characteristics

- **No compliance model**: No STRICT/STANDARD/LIGHT/EXEMPT tiers
- **No auto-classification**: No keyword-based tier detection algorithm
- **No verification tiers**: No sub-agent verification routing
- **No escape hatches**: No `--skip-compliance` or `--force-strict`
- **Strategy-only orchestration**: The `--strategy` flag is its primary orchestration dimension

---

## sc:task-unified Profile (v2.0.0)

**Source files**:
- Command: `src/superclaude/commands/task-unified.md`
- Skill: `src/superclaude/skills/sc-task-unified/SKILL.md`

### Identity

| Field | Value |
|-------|-------|
| **Frontmatter name** | `task` (command) / `sc-task-unified` (skill) |
| **Description** | "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation" |
| **Category** | special |
| **Complexity** | advanced |
| **Version** | 2.0.0 |

### Purpose

Two orthogonal dimensions merged into one command:
1. **Strategy** (orchestration): How to coordinate work
2. **Compliance** (quality): How strictly to enforce verification

Explicitly designed to replace both `task.md` (v1.x) and `task-mcp.md`.

### Behavioral Flow

7-step pipeline with classification phase:
1. Analyze (parse requirements, detect keywords, estimate scope)
2. **Classify** (determine compliance tier using auto-detection algorithm)
3. **Display** (announce tier with confidence and rationale)
4. Delegate (route to MCP/personas)
5. Execute (apply tier-appropriate checklist)
6. **Verify** (tier-appropriate verification)
7. **Report** (summarize enforcement outcomes)

The SKILL.md adds a mandatory Step 0: output a machine-readable classification header before any other output.

### Flags

| Flag Category | Flag | Options |
|---------------|------|---------|
| **Strategy** | `--strategy` | systematic, agile, enterprise, auto |
| **Compliance** | `--compliance` | strict, standard, light, exempt, auto |
| **Verification** | `--verify` | critical, standard, skip, auto |
| **Control** | `--skip-compliance` | Bypass all enforcement |
| **Control** | `--force-strict` | Override to STRICT |
| **Control** | `--parallel` | Enable parallel execution |
| **Control** | `--delegate` | Enable sub-agent delegation |
| **Control** | `--reason "..."` | Justification for override |

### MCP Servers

Tiered activation model:

| Server | Always Active | Conditional |
|--------|--------------|-------------|
| Sequential | Yes | - |
| Context7 | Yes | - |
| Serena | Yes | - |
| Playwright | No | STRICT + UI/E2E tasks |
| Magic | No | `--with-ui` flag |
| Morphllm | No | `--with-bulk-edit` flag |

### Personas

10 personas: architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer

Organized into core (always available) and domain-specific (triggered by file patterns/tier).

### Key Characteristics

- **4-tier compliance model**: STRICT, STANDARD, LIGHT, EXEMPT
- **Auto-classification algorithm**: Keyword + path + file-count + complexity scoring
- **Compound phrase handling**: "quick fix" -> LIGHT, "fix security" -> STRICT
- **Verification routing**: Sub-agent for STRICT, direct tests for STANDARD, skip for LIGHT/EXEMPT
- **Circuit breaker integration**: STRICT blocks if required MCP servers unavailable
- **SMART acceptance criteria**: Per-tier measurable success criteria
- **Escape hatches**: `--skip-compliance`, `--force-strict`, `--verify skip`
- **Machine-readable telemetry**: Classification header for A/B testing
- **Migration path**: Explicit deprecation of `task-mcp.md`, migration guide from `task.md` v1.x

---

## Comparison Matrix

| Dimension | sc:task (v1.x) | sc:task-unified (v2.0) |
|-----------|---------------|----------------------|
| **Command file** | `task.md` (4.8 KB) | `task-unified.md` (18.4 KB) |
| **Skill directory** | None | `sc-task-unified/SKILL.md` |
| **Frontmatter name** | `task` | `task` |
| **Version** | Unversioned | 2.0.0 |
| **Core dimensions** | Strategy only | Strategy + Compliance |
| **Compliance model** | None | 4-tier (STRICT/STANDARD/LIGHT/EXEMPT) |
| **Auto-classification** | None | Keyword + path + complexity scoring |
| **Verification routing** | Generic quality gates | Tier-specific (sub-agent, direct test, skip) |
| **MCP activation** | All always available | Conditional by tier |
| **Persona count** | 7 | 10 |
| **Flag count** | 3 | 8+ |
| **Behavioral steps** | 5 | 7 (+ Step 0 in SKILL.md) |
| **Escape hatches** | None | 4 (`--skip-compliance`, `--force-strict`, `--verify skip`, manual override) |
| **Telemetry** | None | Machine-readable classification header |
| **Success metrics** | None defined | 7 measurable targets |
| **Deprecates** | Nothing | `task-mcp.md` |
| **Migration guide** | N/A | From v1.x `task.md` and from `task-mcp` |

---

## Overlap Analysis

### Shared Functionality

Both commands share these capabilities:
1. **Task orchestration**: Multi-agent coordination and delegation
2. **Strategy flags**: `--strategy systematic|agile|enterprise`
3. **Parallel execution**: `--parallel` flag
4. **Sub-agent delegation**: `--delegate` flag
5. **MCP server integration**: Sequential, Context7, Serena, Magic, Playwright, Morphllm
6. **TodoWrite integration**: Hierarchical task breakdown and tracking
7. **Persona activation**: architect, analyzer, frontend, backend, security, devops

### Exclusive to sc:task-unified

1. **Compliance tier system** (STRICT/STANDARD/LIGHT/EXEMPT)
2. **Auto-classification algorithm** with confidence scoring
3. **Compound phrase detection** for tier disambiguation
4. **Tier-specific checklists** (6-category STRICT checklist, core rules STANDARD checklist)
5. **Verification agent routing** (quality-engineer sub-agent for STRICT)
6. **Adversarial review** step in STRICT tier
7. **SMART acceptance criteria** per tier
8. **Circuit breaker integration** (blocks STRICT if MCP unavailable)
9. **Escape hatches** (`--skip-compliance`, `--force-strict`)
10. **Machine-readable telemetry header** for A/B testing
11. **Feedback collection** for calibration learning
12. **Additional personas**: qa, refactorer, python-expert, quality-engineer
13. **Post-task "Did I?" checklist** for STRICT tier
14. **Memory persistence** via `write_memory` at completion

### Exclusive to sc:task (v1.x)

1. **project-manager persona** (not listed in task-unified)
2. **Simpler behavioral model** (5 steps vs 7+)

The project-manager persona is the only tangible capability present in the legacy command that is absent from the unified version.

---

## Architectural Separation Assessment

### Current State: Incomplete Migration

The codebase is in a **transitional state** where the v2.0 unified command exists alongside the v1.x legacy command.

**Evidence of intended unification**:
- `task-unified.md` explicitly states: "v2.0.0 - Unified command merging sc:task and sc:task-mcp"
- `task-unified.md` contains a "Migration from Legacy Commands" section with `From /sc:task (v1.x)` guidance
- `task-mcp.md` frontmatter contains `deprecated: true` and `deprecated_by: "task-unified"`
- The SKILL.md for `sc-task-unified` instructs use of `/sc:task` as the invocation command

**Evidence of incomplete cleanup**:
- `task.md` still exists in `src/superclaude/commands/` and is installed to `.claude/commands/sc/`
- `task.md` has no deprecation markers in its frontmatter
- `task-mcp.md` still exists (though marked deprecated)
- No `sc-task` skill directory exists, but the command file is still installable

### Routing Ambiguity

Both `task.md` and `task-unified.md` are installed as slash commands. The frontmatter `name` field is:
- `task.md`: `name: task`
- `task-unified.md`: `name: task`

Both share the same frontmatter name. Claude Code slash command routing depends on the **filename** under `.claude/commands/sc/`:
- `/sc:task` routes to `task.md`
- `/sc:task-unified` routes to `task-unified.md`

The SKILL.md for `sc-task-unified` instructs usage as `/sc:task`, but the actual file path means it responds to `/sc:task-unified`. This creates a disconnect: the skill expects to be invoked as `/sc:task`, but Claude Code would route `/sc:task` to the legacy `task.md` file instead.

### Recommended Resolution

To complete the migration:
1. Add `deprecated: true` and `deprecated_by: "task-unified"` to `task.md` frontmatter
2. Either rename `task-unified.md` to `task.md` (replacing the legacy) or redirect `/sc:task` to the unified version
3. Remove `task-mcp.md` entirely (already deprecated)

---

## Conclusion

**sc:task and sc:task-unified are not distinct, complementary commands.** They are the v1.x and v2.0 versions of the same command, respectively. The unified version is a strict superset that absorbed all orchestration capabilities from `task.md` and all compliance enforcement from `task-mcp.md`.

The only skill backing these commands is `sc-task-unified`. There is no `sc-task` skill.

The current state represents an **incomplete migration** where the legacy `task.md` has not yet been removed or marked deprecated. The three task-related command files should be consolidated:

| Action | File | Rationale |
|--------|------|-----------|
| **Replace or deprecate** | `task.md` | Superseded by `task-unified.md` |
| **Remove** | `task-mcp.md` | Already deprecated, migration guide exists |
| **Retain as canonical** | `task-unified.md` | v2.0.0 unified command |
| **Retain as canonical** | `sc-task-unified/SKILL.md` | Only skill definition for task execution |

The framework would benefit from renaming `task-unified.md` to `task.md` to complete the migration and eliminate routing ambiguity.
