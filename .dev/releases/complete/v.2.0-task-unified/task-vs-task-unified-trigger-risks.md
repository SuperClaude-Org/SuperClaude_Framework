# Trigger Collision Analysis: sc:task vs sc:task-unified

**Date**: 2026-02-22
**Scope**: Command routing, skill activation, keyword overlap, namespace collision, runtime delegation
**Overall Risk Level**: **HIGH**

---

## Executive Summary

There are multiple collision vectors between `sc:task` and `sc:task-unified`. The most severe issue is that **both command files (`task.md` and `task-unified.md`) declare `name: task` in their frontmatter**, creating an identical-name collision in the command registry. Additionally, the SKILL.md for `sc-task-unified` instructs users to invoke `/sc:task` (not `/sc:task-unified`), creating intentional aliasing that nonetheless means Claude Code has two competing definitions for the same command name. The risk is HIGH because the system currently has no deterministic disambiguation mechanism -- which command loads when a user types `/sc:task` depends on file enumeration order, which is undefined.

---

## 1. Command Routing Analysis

### Evidence

**Source file frontmatter (`src/superclaude/commands/`):**

| File | `name:` field | Title heading |
|------|--------------|---------------|
| `task.md` | `name: task` | `/sc:task - Enhanced Task Management` |
| `task-unified.md` | `name: task` | `/sc:task - Unified Task Command` |
| `task-mcp.md` | `name: task-mcp` | `/sc:task-mcp` (deprecated) |

**Installed command files (`.claude/commands/sc/`):**

Both `task.md` and `task-unified.md` exist as separate files in the same directory. Both declare `name: task`.

| File | Size | Both present |
|------|------|-------------|
| `.claude/commands/sc/task.md` | 4,862 bytes | Yes |
| `.claude/commands/sc/task-unified.md` | 18,447 bytes | Yes |

### Finding

**CRITICAL COLLISION**: Both files declare `name: task` in frontmatter. When Claude Code scans `.claude/commands/sc/` for available slash commands, it will find two files claiming to be the `/sc:task` command. The behavior is **non-deterministic** -- it depends on:

1. File enumeration order (alphabetical by filename on most filesystems)
2. Whether Claude Code uses filename or frontmatter `name:` for routing
3. Whether last-loaded or first-loaded wins

If Claude Code routes by **filename**, then `/sc:task` maps to `task.md` and `/sc:task-unified` maps to `task-unified.md` -- no collision. But if it routes by the **`name:` frontmatter field**, both claim `name: task`, which is a direct collision.

The `task-unified.md` file (v2.0.0) was designed as a replacement for `task.md` (v1.x), as evidenced by its "Migration from Legacy Commands" section. However, both files coexist, creating ambiguity.

**Risk**: **HIGH** -- Duplicate `name: task` frontmatter creates undefined routing behavior.

---

## 2. Skill Activation Analysis

### Evidence

**Skill directories found:**

| Skill directory | SKILL.md exists | `name:` field |
|-----------------|-----------------|---------------|
| `src/superclaude/skills/sc-task-unified/` | Yes | `name: sc-task-unified` |
| `src/superclaude/skills/sc-task/` | **Does not exist** | N/A |

**SKILL.md frontmatter for sc-task-unified:**
```yaml
name: sc-task-unified
description: Unified task execution with intelligent workflow management...
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**Installed skills (`.claude/skills/`):**
Only `confidence-check` is installed. Neither `sc-task-unified` nor `sc-task` is installed as a skill in the active workspace.

### Finding

The skill namespace is **clean**. The skill `sc-task-unified` has a distinct name (`sc-task-unified`) that does not collide with any `sc-task` skill (which does not exist). However, there is a notable inconsistency:

- The SKILL.md **title** says `/sc:task-unified`
- The SKILL.md **trigger documentation** says "Use `/sc:task` when:" -- directing users to invoke the `/sc:task` command, not `/sc:task-unified`
- The SKILL.md **usage examples** show both `/sc:task-unified [description]` and `/sc:task "..."` interchangeably

This creates confusion about whether the skill is activated via `/sc:task` or `/sc:task-unified`.

**Risk**: **LOW** for skill activation (distinct `name:` field), but **MODERATE** for user confusion (mixed invocation guidance).

---

## 3. Keyword Overlap Analysis

### Evidence

**Auto-activation keywords comparison:**

| Keyword/Phrase | `task.md` triggers | `task-unified.md` triggers | Overlap |
|----------------|-------------------|---------------------------|---------|
| "implement feature" | Implicit (complex task) | Explicit high-confidence | Yes |
| "refactor system" | Implicit (complex task) | Explicit high-confidence | Yes |
| "fix security" | Implicit (complex task) | Explicit high-confidence | Yes |
| "add authentication" | Implicit (complex task) | Explicit high-confidence | Yes |
| "create component" | Implicit | Explicit moderate-confidence | Yes |
| "update service" | Implicit | Explicit moderate-confidence | Yes |
| Multi-file scope | Yes (>3 files) | Yes (>2 files) | Yes |
| Security domain | Yes | Yes | Yes |
| Complexity >0.6 | Not explicit | Explicit | Partial |

**ORCHESTRATOR.md routing table entries for "task":**
- The orchestrator references `/sc:task` generically in the routing table
- No separate routing entry for `/sc:task-unified`
- The Tier Classification Routing section describes the unified command's behavior under the `/sc:task` name

**COMMANDS.md definitions:**
- Lists `/sc:task [operation] [flags]` as a command
- Separately lists `/sc:task [description] [flags]` as the "Unified Task Command"
- Both entries share the same `/sc:task` prefix

### Finding

The keyword overlap is **near-total**. Both commands target the same problem domain (task execution), the same keywords (implement, refactor, security, authentication), and the same context signals (multi-file scope, security paths). Since `task-unified.md` was designed to replace `task.md`, this overlap is by design -- but the coexistence of both files means the auto-activation system has no way to choose between them.

**Risk**: **HIGH** -- Identical keyword triggers with no disambiguation mechanism.

---

## 4. Namespace Collision Analysis

### Evidence

**Prefix relationship**: `/sc:task` is a strict prefix of `/sc:task-unified`.

**Claude Code command resolution**: Claude Code resolves slash commands by matching the command name after `/`. The files in `.claude/commands/sc/` are:
- `task.md` -- resolves as `/sc:task`
- `task-unified.md` -- resolves as `/sc:task-unified`

**Filename-based routing test**: If Claude Code uses filenames (sans `.md` extension) for routing:
- `/sc:task` matches `task.md` exactly
- `/sc:task-unified` matches `task-unified.md` exactly
- No prefix ambiguity because the match is exact on the filename

**Frontmatter-based routing test**: If Claude Code uses the `name:` field:
- `/sc:task` matches both `task.md` (`name: task`) and `task-unified.md` (`name: task`) -- **COLLISION**
- `/sc:task-unified` matches neither (no file has `name: task-unified`)

### Finding

The namespace collision risk depends entirely on how Claude Code resolves command names:

1. **Filename-based**: **LOW risk**. `/sc:task` and `/sc:task-unified` resolve to distinct files.
2. **Frontmatter name-based**: **CRITICAL risk**. Both files declare `name: task`, making `/sc:task-unified` unreachable via its name field, and `/sc:task` ambiguous.

In practice, Claude Code uses **filenames** for command resolution in the `commands/` directory structure. The `name:` frontmatter field is metadata used by the command's internal logic, not by the routing system. This means the namespace collision via filename is LOW, but the duplicate `name:` field could cause confusion if any system component (installer, indexer, help system) uses frontmatter for deduplication.

**Risk**: **MODERATE** -- Filename routing prevents hard collision, but frontmatter duplication is a latent defect.

---

## 5. Runtime Delegation Analysis

### Evidence

**Does `task.md` reference `task-unified`?**
Searched `task.md` for "task-unified" -- **no matches found**. The `task.md` command has no awareness of `task-unified.md`.

**Does `task-unified.md` reference `task`?**
The `task-unified.md` command contains:
- A "Migration from Legacy Commands" section referencing `/sc:task` (v1.x) as the predecessor
- Examples using `/sc:task` as the invocation command (treating itself as the replacement)
- A deprecation notice for `/sc:task-mcp`, redirecting to `/sc:task --compliance [tier]`

**Does SKILL.md delegate to either?**
The SKILL.md for `sc-task-unified` tells users to invoke `/sc:task` (not `/sc:task-unified`), effectively treating the two as the same command. It does not programmatically delegate to the command file.

**Does `task-mcp.md` delegate?**
Yes -- `task-mcp.md` declares `deprecated: true` and `deprecated_by: "task-unified"`, redirecting users to `/sc:task --compliance [tier]`.

### Finding

There is no programmatic delegation between the commands (no command file invokes the other). However, the documentation creates a **conceptual delegation loop**:

1. `task-unified.md` claims to BE the new `/sc:task` (via `name: task` and migration docs)
2. `task.md` still exists as the original `/sc:task`
3. `task-mcp.md` redirects to `/sc:task --compliance [tier]` which could hit either file
4. SKILL.md tells users to type `/sc:task` to use the unified command

A user typing "run the task command" would trigger keyword matching that could route to either `task.md` or `task-unified.md` with equal probability.

**Risk**: **MODERATE** -- No hard delegation, but documentation and naming create a circular reference that confuses the routing intent.

---

## Risk Matrix

| Risk Area | Severity | Likelihood | Impact | Overall Rating |
|-----------|----------|------------|--------|----------------|
| **Command Routing (frontmatter `name:` collision)** | Critical | High | User gets wrong command behavior | **HIGH** |
| **Skill Activation** | Low | Low | Wrong skill loads | **LOW** |
| **Keyword Overlap** | High | High | Auto-suggest picks wrong command | **HIGH** |
| **Namespace Collision (filename)** | Low | Low | Wrong command loads | **LOW** |
| **Namespace Collision (frontmatter)** | High | Medium | Indexer/help system confusion | **MODERATE** |
| **Runtime Delegation** | Moderate | Medium | User confusion, wrong workflow | **MODERATE** |

**Aggregate Risk**: **HIGH**

---

## Recommended Remediations

### Immediate (P0)

1. **Remove `task.md` or rename its `name:` field**: Since `task-unified.md` is the v2.0 replacement, either:
   - Delete `src/superclaude/commands/task.md` and `.claude/commands/sc/task.md` entirely, OR
   - Rename `task.md` to `task-legacy.md` with `name: task-legacy` and mark it deprecated

2. **Fix `task-unified.md` frontmatter**: If `task-unified.md` IS the canonical `/sc:task`, rename the file to `task.md` (replacing the old one) so the filename matches the intent. This eliminates the prefix collision entirely.

### Short-term (P1)

3. **Update SKILL.md invocation guidance**: The SKILL.md currently shows both `/sc:task-unified` and `/sc:task` as invocation patterns. Pick one and be consistent.

4. **Update ORCHESTRATOR.md**: Add explicit routing entry that distinguishes which file handles `/sc:task`.

### Long-term (P2)

5. **Add frontmatter uniqueness validation**: The `make verify-sync` or `superclaude install` process should validate that no two command files share the same `name:` frontmatter value.

6. **Add deprecation enforcement**: Commands with `deprecated: true` should emit a warning when loaded, not silently coexist.

---

## Conclusion

The coexistence of `task.md` and `task-unified.md` with identical `name: task` frontmatter represents a **HIGH** collision risk. While Claude Code's filename-based routing prevents a hard crash, the duplicate naming creates undefined behavior in any system component that indexes by frontmatter, confuses auto-activation keyword matching, and leaves users uncertain which version of the command they are invoking. The root cause is that `task-unified.md` was designed to replace `task.md` but both files remain present. The simplest fix is to consolidate: rename `task-unified.md` to `task.md` (overwriting the v1 file) or delete the v1 file entirely.
