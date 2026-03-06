# Cross-Reference Audit: sc:task vs sc:task-unified

**Generated**: 2026-02-22
**Scope**: Full codebase scan of `/config/workspace/SuperClaude_Framework`
**Branch**: `feature/v2.0-Roadmap-v2`

---

## Summary

| Metric | Count |
|--------|-------|
| Total files with `task-unified` references | 52 |
| Total files with `sc:task` (non-unified) references | 64 |
| **Intentional references** | ~210+ |
| **Unintentional references** | 5 |
| **Ambiguous references** | 4 |

### Critical Finding: Namespace Collision

The most significant issue is **not** cross-referencing but a **namespace collision**: both `task.md` and `task-unified.md` command files declare `name: task` in their frontmatter and both claim the `/sc:task` command invocation. This means Claude Code cannot distinguish which command file to load when a user types `/sc:task`.

Additionally, the `sc-task-unified` SKILL.md is internally inconsistent: its Usage section shows `/sc:task-unified` syntax but its Examples section uses `/sc:task` syntax.

---

## Unintentional References

| # | File | Line(s) | Reference | Context | Why Unintentional | Risk |
|---|------|---------|-----------|---------|-------------------|------|
| U1 | `src/superclaude/commands/task-unified.md` | 1 (frontmatter) | `name: task` | Frontmatter declares the same name as `task.md` | Both command files claim `name: task`, creating a namespace collision. Claude Code may load the wrong file when `/sc:task` is invoked. The unified command file should use `name: task-unified` or the old `task.md` should be removed/deprecated. | **HIGH** - Users invoking `/sc:task` get unpredictable behavior depending on which file loads first. |
| U2 | `src/superclaude/skills/sc-task-unified/SKILL.md` | 48-52 vs 233-271 | `/sc:task-unified` in Usage, `/sc:task` in Examples | Usage section: `/sc:task-unified [description]`; Examples section: `/sc:task "implement user authentication with JWT"` | Internal inconsistency within the same file. The Usage section tells users to type `/sc:task-unified` but all 5 examples show `/sc:task` without the `-unified` suffix. | **MEDIUM** - Users will be confused about which command to actually type. |
| U3 | `src/superclaude/skills/sc-task-unified/SKILL.md` | 34 | `Use /sc:task when:` | Triggers section of the sc-task-unified SKILL | The skill file for `sc-task-unified` tells users to invoke `/sc:task` (the simpler command) rather than `/sc:task-unified`. This could route users to the wrong command. | **MEDIUM** - Trigger documentation points to wrong command name. |
| U4 | `.claude/commands/sc/task-unified.md` | 1 (frontmatter) | `name: task` | Mirror of U1 in `.claude/` dev copy | Same namespace collision as U1. The `.claude/` copy has the same issue. | **HIGH** - Same as U1 (this is the dev copy that Claude Code actually reads). |
| U5 | `src/superclaude/skills/sc-roadmap/SKILL.md` | 24 | `sc:task-unified` | Pipeline Position: `spec(s) -> sc:roadmap -> ... -> sc:task-unified` | References the internal skill name `sc:task-unified` as the pipeline endpoint rather than the user-facing command `/sc:task`. Users reading this pipeline would try to invoke `sc:task-unified` which is a skill, not a command. | **LOW** - Pipeline documentation uses internal name instead of user-facing command. |

---

## Ambiguous References

| # | File | Line(s) | Reference | Context | Why Ambiguous |
|---|------|---------|-----------|---------|---------------|
| A1 | `src/superclaude/commands/validate-tests.md` | 100 | `/sc:task` - Unified task command | See Also section | Labels `/sc:task` as "Unified task command" but `/sc:task` is the simple task.md command. The "unified" qualifier suggests task-unified was intended. |
| A2 | `/config/.claude/COMMANDS.md` | 81+ | `/sc:task [description] [flags]` | Describes compliance tiers (strict/standard/light/exempt), verification flags, and tier classification | Uses the `/sc:task` command name but describes task-unified behavior (compliance tiers, verification). It is unclear whether this section documents task.md or task-unified.md. |
| A3 | `docs/user-guide/flags.md` | 81 | `Task Command Flags (/sc:task)` | Flag documentation section header | Lists flags that belong to task-unified (compliance, verify, strategy) under the `/sc:task` heading. Could mean either command. |
| A4 | `docs/generated/dev-guide-research/extract-opus-12-skills-multi.md` | 492 | `/sc:task -> sc-task-unified skill` | Mapping notation | Shows a routing from `/sc:task` command to `sc-task-unified` skill. This is likely the intended architecture but makes the relationship between the two unclear to readers. |

---

## Intentional References (Summary by Category)

These are correctly placed references that belong where they are. Listed in summary form to avoid noise.

### Category: Own Files (skill/command referencing itself)

| File | Count | Notes |
|------|-------|-------|
| `src/superclaude/skills/sc-task-unified/SKILL.md` | 8 | Self-references to `/sc:task-unified` in Usage section |
| `src/superclaude/skills/sc-task-unified/__init__.py` | 1 | Package comment |
| `src/superclaude/commands/task-unified.md` | 25+ | Self-references throughout |
| `src/superclaude/commands/task.md` | 12+ | Self-references throughout |
| `.claude/commands/sc/task.md` | 12+ | Dev copy of task.md |
| `.claude/commands/sc/task-unified.md` | 25+ | Dev copy of task-unified.md |

### Category: Deprecation & Migration (task-mcp pointing to replacements)

| File | Count | Notes |
|------|-------|-------|
| `src/superclaude/commands/task-mcp.md` | 8 | Correctly deprecated, points to both `/sc:task` and `/sc:task-unified` |
| `.claude/commands/sc/task-mcp.md` | 8 | Dev copy, same correct deprecation notices |

### Category: Validate-Tests Skill (testing sc-task-unified behavior)

| File | Count | Notes |
|------|-------|-------|
| `src/superclaude/skills/sc-validate-tests/SKILL.md` | 10 | Correctly references `sc-task-unified` as its test target |
| `src/superclaude/commands/validate-tests.md` | 3 | Default target `tests/sc-task-unified/`, example paths |
| `.claude/commands/sc/validate-tests.md` | 3 | Dev copy |

### Category: Release Archives & Backlog (historical/planning docs)

| Directory | `task-unified` refs | `sc:task` refs | Notes |
|-----------|--------------------:|---------------:|-------|
| `.dev/releases/archive/` | 18 | 12 | Completed release docs, read-only historical |
| `.dev/releases/backlog/v.2.0-task-unified/` | 80+ | 40+ | Task-unified feature development docs |
| `.dev/releases/backlog/v3.0-analyze-auggie/` | 25 | 5 | Auggie MCP integration planning |
| `.dev/releases/backlog/v.1.5-Tasklists/` | 3 | 0 | Tasklist generator integration |
| `.dev/releases/backlog/v.4.0-Spec-generator/` | 0 | 2 | Spec generator planning |

### Category: Documentation (user guides, dev guides)

| Directory | `task-unified` refs | `sc:task` refs | Notes |
|-----------|--------------------:|---------------:|-------|
| `docs/user-guide/` | 0 | 30+ | User guide only documents `/sc:task` |
| `docs/user-guide-jp/` | 0 | 1 | Japanese localization |
| `docs/user-guide-kr/` | 0 | 1 | Korean localization |
| `docs/user-guide-zh/` | 0 | 1 | Chinese localization |
| `docs/generated/` | 20 | 15 | Generated dev guide research extracts |
| `docs/capability-mapping-v5.md` | 0 | 1 | Capability mapping |

### Category: Plugins

| File | `task-unified` refs | `sc:task` refs | Notes |
|------|--------------------:|---------------:|-------|
| `plugins/superclaude/commands/task.md` | 0 | 8 | Plugin copy of task.md |
| `plugins/superclaude/commands/help.md` | 0 | 2 | Plugin help file |

### Category: Core Framework Files

| File | `task-unified` refs | `sc:task` refs | Notes |
|------|--------------------:|---------------:|-------|
| `src/superclaude/core/COMMANDS.md` | 0 | 1 | Describes unified task command under `/sc:task` name |
| `src/superclaude/core/ORCHESTRATOR.md` | 0 | 1 | Routes `/sc:task` to compliance tiers |
| `src/superclaude/commands/help.md` | 0 | 2 | Help command lists `/sc:task` |

---

## Risk Assessment

### U1 + U4: Namespace Collision (HIGH RISK)

**Impact**: When a user types `/sc:task`, Claude Code must choose between `task.md` and `task-unified.md`. Both declare `name: task`. The behavior is unpredictable -- it depends on file load order.

**Recommendation**: One of:
- (a) Rename `task-unified.md` frontmatter to `name: task-unified` so it responds to `/sc:task-unified`
- (b) Remove or deprecate `task.md` so only `task-unified.md` responds to `/sc:task`
- (c) Merge both into a single `task.md` file

### U2 + U3: SKILL.md Internal Inconsistency (MEDIUM RISK)

**Impact**: The `sc-task-unified` SKILL.md uses `/sc:task-unified` in its Usage section but `/sc:task` everywhere else (Triggers, Examples). Users reading the file get contradictory guidance about which command to type.

**Recommendation**: Make all invocations consistent. If the user-facing command is `/sc:task`, change the Usage section. If it is `/sc:task-unified`, change the Triggers and Examples sections.

### U5: Roadmap Pipeline Reference (LOW RISK)

**Impact**: The sc-roadmap SKILL.md pipeline string uses `sc:task-unified` (the internal skill name) as the terminal step. Users reading this would try to invoke a skill name rather than a command.

**Recommendation**: Change to `/sc:task` (or `/sc:task-unified` if that becomes the canonical command name).

### A1-A4: Ambiguous References (LOW-MEDIUM RISK)

**Impact**: Several files describe task-unified features (compliance tiers, verification) under the `/sc:task` name. This is only problematic if the two commands remain separate; if they are intended to be unified under `/sc:task`, these references are correct.

**Recommendation**: Resolve the namespace collision first (U1/U4). Once the canonical command name is decided, audit these ambiguous references to ensure they point to the correct entity.

---

## Architectural Observation

The root cause of all issues is that the project is mid-migration from a two-command system (`sc:task` + `sc:task-mcp`) to a unified command. The unified command was implemented as `task-unified.md` / `sc-task-unified` skill, but the original `task.md` was never removed or deprecated. The unified command also uses `/sc:task` as its invocation name (not `/sc:task-unified`), creating a collision.

**The codebase currently has three task-related command files**:
1. `task.md` -- old simple task command (name: task)
2. `task-unified.md` -- new unified command (name: task, should probably be task-unified or task.md should be removed)
3. `task-mcp.md` -- deprecated, correctly points to unified command

**Resolution path**: Decide whether `/sc:task` means the old or new command, then:
- If old: keep `task.md`, rename `task-unified.md` to respond to `/sc:task-unified`
- If new (likely intended): remove `task.md`, rename `task-unified.md` to `task.md` (or change its frontmatter name)
- Either way: update all ambiguous references to match the decision
