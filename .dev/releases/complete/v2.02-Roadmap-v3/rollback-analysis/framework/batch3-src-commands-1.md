# Batch 3 — Source Commands Analysis (Part 1)

**Files analyzed**: 3 modified source command files
**Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Verdict**: All changes implement a consistent command-to-skill activation policy. All `.claude/` mirrors are in sync.

---

## 1. `src/superclaude/commands/adversarial.md`

### Diff

```diff
@@ -47,6 +47,14 @@ personas: [architect, analyzer, scribe]
 | `--output` | `-o` | No | Auto | Output directory for artifacts |
 | `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |

+## Activation
+
+**MANDATORY**: Before executing any protocol steps, invoke:
+> Skill sc:adversarial-protocol
+
+Do NOT proceed with protocol execution using only this command file.
+The full behavioral specification (5-step pipeline, agent dispatch, scoring algorithms, error handling) is in the protocol skill.
+
 ## Behavioral Summary
```

### What Changed

A new `## Activation` section was **inserted** between the flags table and the existing `## Behavioral Summary` section. The section contains:

1. A **MANDATORY** directive telling the agent to invoke the `sc:adversarial-protocol` skill before doing any work.
2. An explicit prohibition: "Do NOT proceed with protocol execution using only this command file."
3. A summary of what the skill contains (5-step pipeline, agent dispatch, scoring algorithms, error handling).

### Why

Previously, the command file contained the full behavioral specification inline. The skills were renamed from `sc-adversarial` to `sc-adversarial-protocol` (visible in the git status rename entries). This change decouples the **command** (parameter parsing, metadata, flag definitions) from the **protocol** (full execution logic). The command becomes a thin launcher that delegates to the skill, which is the canonical source of behavioral instructions. This follows the new command-skill separation policy introduced in v2.01.

### Sync Status

| Comparison | Result |
|---|---|
| `HEAD` (committed): `src/` vs `.claude/` | **IDENTICAL** |
| Working tree: `src/` vs `.claude/` | **IDENTICAL** |

No discrepancies. Both locations received the same edit.

---

## 2. `src/superclaude/commands/cleanup-audit.md`

### Diff

```diff
@@ -32,6 +32,14 @@ personas: [analyzer, architect, devops, qa, refactorer]
 - **--batch-size**: Files per agent batch (default: 50 for surface, 25 for structural, 30 for cross-cutting)
 - **--focus**: Domain filter for targeted auditing (`infrastructure`, `frontend`, `backend`, `all`)

+## Activation
+
+**MANDATORY**: Before executing any protocol steps, invoke:
+> Skill sc:cleanup-audit-protocol
+
+Do NOT proceed with protocol execution using only this command file.
+The full behavioral specification (3-pass audit protocol, subagent dispatch, evidence gates, report templates) is in the protocol skill.
+
 ## Behavioral Summary
```

### What Changed

Same structural pattern as adversarial.md: a new `## Activation` section was inserted between the parameter documentation and the behavioral summary. The skill reference is `sc:cleanup-audit-protocol`, and the parenthetical describes the skill's contents as "3-pass audit protocol, subagent dispatch, evidence gates, report templates."

### Why

Identical rationale to adversarial.md. The cleanup-audit skill was renamed from `sc-cleanup-audit` to `sc-cleanup-audit-protocol` (confirmed in git status). The command file now serves purely as the entry-point definition (metadata, allowed tools, flags, persona list) while delegating all execution logic to the protocol skill. This prevents behavioral drift if the command file is edited independently of the skill.

### Sync Status

| Comparison | Result |
|---|---|
| `HEAD` (committed): `src/` vs `.claude/` | **IDENTICAL** (both share index `0a85091..4716523`) |
| Working tree: `src/` vs `.claude/` | **IDENTICAL** |

No discrepancies.

---

## 3. `src/superclaude/commands/roadmap.md`

### Diff

```diff
@@ -1,7 +1,7 @@
 ---
 name: sc:roadmap
 description: Generate comprehensive project roadmaps from specification documents
-allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
+allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
 ---

@@ -67,7 +67,11 @@ When the user requests roadmap generation from a specification file. Requires a

 ## Activation

-Load and execute the full behavioral instructions from `src/superclaude/skills/sc-roadmap/SKILL.md`.
+**MANDATORY**: Before executing any protocol steps, invoke:
+> Skill sc:roadmap-protocol
+
+Do NOT proceed with protocol execution using only this command file.
+The full behavioral specification (wave-based generation, adversarial integration, validation protocol) is in the protocol skill.

 ## Boundaries
```

### What Changed

Two changes in this file:

**Change A — Frontmatter `allowed-tools` (line 4)**: The `Skill` tool was appended to the allowed-tools list. This is necessary because the new activation pattern uses `> Skill sc:roadmap-protocol`, which requires the `Skill` tool to be whitelisted in the command's frontmatter.

**Change B — Activation section rewrite (line 70)**: The old activation line was a simple file-path reference:
```
Load and execute the full behavioral instructions from `src/superclaude/skills/sc-roadmap/SKILL.md`.
```
This was replaced with the standardized MANDATORY skill invocation block referencing `sc:roadmap-protocol`, matching the pattern used in adversarial.md and cleanup-audit.md.

### Why

**Change A**: The roadmap command is the first of the three to already have had an `## Activation` section. However, that section used a file-path-based loading instruction (`src/superclaude/skills/sc-roadmap/SKILL.md`) rather than the `Skill` tool invocation. Since the skill was renamed to `sc-roadmap-protocol`, the old path would be broken. The fix converts to the proper skill invocation mechanism and adds `Skill` to the allowed-tools so the invocation can succeed.

**Change B**: Standardizes the activation language across all command files. The old approach (file-path reference) was fragile -- it would break on renames, and it did not use Claude Code's native skill dispatch system. The new approach uses the `> Skill sc:roadmap-protocol` blockquote syntax, which is the canonical way to invoke skills in the SuperClaude framework.

### Sync Status

| Comparison | Result |
|---|---|
| `HEAD` (committed): `src/` vs `.claude/` | **IDENTICAL** |
| Working tree: `src/` vs `.claude/` | **IDENTICAL** |

No discrepancies.

---

## Cross-File Pattern Analysis

### Consistent Pattern Applied

All three files received the same structural change -- insertion of a standardized `## Activation` block with this template:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:{command}-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification ({specifics}) is in the protocol skill.
```

The `{specifics}` parenthetical is customized per command to describe what the skill contains.

### Skill Rename Alignment

| Command | Old Skill Name | New Skill Name |
|---|---|---|
| adversarial | `sc-adversarial` | `sc-adversarial-protocol` |
| cleanup-audit | `sc-cleanup-audit` | `sc-cleanup-audit-protocol` |
| roadmap | `sc-roadmap` | `sc-roadmap-protocol` |

All three renames are confirmed in the git status output (R and RM entries for skill directories).

### Allowed-Tools Discrepancy

Only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other two files (`adversarial.md`, `cleanup-audit.md`) did **not** add `Skill` to their allowed-tools. This is a potential issue:

- **adversarial.md** allowed-tools: `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` -- **missing `Skill`**
- **cleanup-audit.md** allowed-tools: `Read, Glob, Grep, Bash, TodoWrite, Task, Write` -- **missing `Skill`**
- **roadmap.md** allowed-tools: `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` -- **has `Skill`**

If the `Skill` tool must be in `allowed-tools` for the `> Skill` invocation to work, then adversarial.md and cleanup-audit.md have a latent bug. If `Skill` invocation bypasses the allowed-tools gate (i.e., it is always available), then this is a non-issue but an inconsistency.

**Recommendation**: Verify whether `Skill` must be in `allowed-tools` for the activation blockquote to function. If yes, add it to adversarial.md and cleanup-audit.md for consistency.

### Sync Verdict

All three files are **perfectly synchronized** between `src/superclaude/commands/` and `.claude/commands/sc/`. No manual reconciliation needed.

---

## Summary Table

| File | Change Type | Lines Added | Lines Removed | Allowed-Tools Modified | Activation Added | Sync OK |
|---|---|---|---|---|---|---|
| `adversarial.md` | Section insert | +8 | 0 | No | Yes (new) | Yes |
| `cleanup-audit.md` | Section insert | +8 | 0 | No | Yes (new) | Yes |
| `roadmap.md` | Frontmatter + section rewrite | +5 | -2 | Yes (`+Skill`) | Yes (rewritten) | Yes |
