# Batch 1 — Command Files Analysis (adversarial, cleanup-audit, roadmap)

**Branch**: `feature/v2.01-Roadmap-V3`
**Analysis date**: 2026-02-24
**Scope**: `.claude/commands/sc/` and `src/superclaude/commands/` (3 files each, 6 total)

---

## Summary of Changes

All three command files received the **same structural change**: insertion of a new `## Activation` section that replaces ad-hoc skill loading with a mandatory `Skill` invocation directive. This implements the **command-skill decoupling policy** — commands become thin dispatchers, skills hold the full behavioral specification.

The `roadmap.md` file additionally received a frontmatter change adding `Skill` to its `allowed-tools` list, and its pre-existing `## Activation` section was rewritten (the other two files had no prior activation section).

---

## File 1: `.claude/commands/sc/adversarial.md`

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

**Lines affected**: 8 lines inserted between the Options table and the Behavioral Summary section (after line 48 in the original).

### What Changed

- **Added**: A new `## Activation` section with a mandatory `Skill sc:adversarial-protocol` invocation.
- **No deletions**: The command previously had no activation section at all. The behavioral summary remains intact as a compressed reference.

### Why

The old `adversarial.md` command had its full behavioral logic implied by the `## Behavioral Summary` section — Claude would read the summary and attempt to execute the protocol inline. This was fragile because:

1. The summary is a compressed description, not executable instructions.
2. The actual protocol lives in `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` (renamed from `sc-adversarial/`).
3. Without an explicit skill invocation, Claude could hallucinate protocol steps or skip the scoring algorithms.

The new activation section forces Claude to load the full skill before proceeding, making the command a **thin dispatcher**.

### Relationship to `src/superclaude/commands/adversarial.md`

The diffs are **identical**. Both `.claude/commands/sc/adversarial.md` and `src/superclaude/commands/adversarial.md` received the same 8-line insertion. This is consistent with the `make sync-dev` workflow (source of truth is `src/`, `.claude/` is a dev copy).

### Breaking Changes

- **Behavioral**: Yes. The command now **requires** the skill `sc:adversarial-protocol` to be installed at `.claude/skills/sc-adversarial-protocol/`. If the skill directory does not exist (e.g., after a partial install or on the old `sc-adversarial` naming), the `Skill` invocation will fail.
- **Note**: The skill was renamed from `sc-adversarial` to `sc-adversarial-protocol` in this same branch (visible in git status as `RM src/superclaude/skills/sc-adversarial/SKILL.md -> src/superclaude/skills/sc-adversarial-protocol/SKILL.md`). Both the rename and this activation change must land together.

---

## File 2: `.claude/commands/sc/cleanup-audit.md`

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

**Lines affected**: 8 lines inserted between the Arguments section and the Behavioral Summary section (after line 33 in the original).

### What Changed

- **Added**: A new `## Activation` section with a mandatory `Skill sc:cleanup-audit-protocol` invocation.
- **No deletions**: Same pattern as adversarial — no prior activation section existed.

### Why

Same rationale as adversarial. The cleanup-audit command is particularly complex (3-pass protocol, 5 subagent types, evidence gates, checkpoint resumption). Without explicit skill loading, Claude was expected to derive all of this from a single-paragraph behavioral summary. The skill at `sc-cleanup-audit-protocol/SKILL.md` contains the full pass specifications, subagent dispatch rules, template references, and error recovery procedures.

### Relationship to `src/superclaude/commands/cleanup-audit.md`

The diffs are **identical**. Both copies received the same 8-line insertion.

### Breaking Changes

- **Behavioral**: Yes. Requires `sc:cleanup-audit-protocol` skill (renamed from `sc-cleanup-audit`). Same dependency coupling as adversarial — the skill rename and the activation directive must land together.
- **Frontmatter note**: Unlike roadmap, the `allowed-tools` list was NOT updated to include `Skill`. This is a potential issue — if Claude Code enforces the allowed-tools whitelist strictly, the `Skill` invocation may be blocked. However, looking at the frontmatter, `cleanup-audit.md` does not have an `allowed-tools` field at all (it uses `mcp-servers` instead), so this is not a concern for this file.

---

## File 3: `.claude/commands/sc/roadmap.md`

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

**Lines affected**: 2 change sites. Line 4 modified (frontmatter). Lines 69-70 replaced with 69-73 (activation section rewritten, net +4 lines).

### What Changed

1. **Frontmatter** (line 4): Added `Skill` to the `allowed-tools` list. This is necessary because the `Skill` tool must be permitted for the activation directive to work.

2. **Activation section** (lines 69-73): Replaced the old `Load and execute the full behavioral instructions from src/superclaude/skills/sc-roadmap/SKILL.md` with the standardized mandatory skill invocation block referencing `sc:roadmap-protocol`.

### Why

The roadmap command already had an activation section, but it used a **file-path-based** loading instruction (`Load and execute the full behavioral instructions from src/superclaude/skills/sc-roadmap/SKILL.md`). This had two problems:

1. **Brittle path reference**: It pointed to `sc-roadmap/`, but the skill was renamed to `sc-roadmap-protocol/`. The old instruction would fail after the rename.
2. **Mechanism mismatch**: It told Claude to "load and execute" a file path, but the proper mechanism is the `Skill` tool invocation, which handles the skill resolution, loading, and context injection automatically.

The new activation section standardizes on the `Skill sc:roadmap-protocol` invocation, matching the pattern established in adversarial and cleanup-audit.

### Relationship to `src/superclaude/commands/roadmap.md`

The diffs are **identical**. Both copies received the same changes.

### Breaking Changes

- **Behavioral**: Yes. The skill reference changed from `sc-roadmap` (file path) to `sc:roadmap-protocol` (skill invocation). Requires the renamed skill directory.
- **Tool permissions**: The `Skill` tool is now explicitly whitelisted in frontmatter. This is a **necessary prerequisite** — without it, the activation directive would be self-contradicting (commanding an invocation that the tool whitelist forbids).
- **Note**: The other two commands (adversarial, cleanup-audit) do NOT have `allowed-tools` in their frontmatter, so they did not need this addition.

---

## Cross-Cutting Analysis

### Pattern: Command-Skill Decoupling

All three changes implement the same architectural pattern:

| Aspect | Before | After |
|--------|--------|-------|
| Skill loading | Implicit (from behavioral summary) or file-path-based | Explicit `Skill` tool invocation |
| Command role | Mixed (dispatcher + partial spec) | Pure dispatcher (metadata + activation) |
| Skill naming | `sc-{name}` | `sc-{name}-protocol` |
| Failure mode | Silent degradation (Claude guesses) | Hard failure (skill not found) |

### Consistency Check

| Property | adversarial | cleanup-audit | roadmap |
|----------|-------------|---------------|---------|
| New activation section added | Yes | Yes | Yes (replaced) |
| Skill name uses `-protocol` suffix | Yes | Yes | Yes |
| `Skill` added to `allowed-tools` | N/A (no field) | N/A (no field) | Yes |
| Behavioral summary preserved | Yes | Yes | Yes |
| `src/` copy matches `.claude/` copy | Yes | Yes | Yes |

### Dependency Chain

These command changes depend on the **skill renames** visible in git status:

```
src/superclaude/skills/sc-adversarial/       -> sc-adversarial-protocol/
src/superclaude/skills/sc-cleanup-audit/      -> sc-cleanup-audit-protocol/
src/superclaude/skills/sc-roadmap/            -> sc-roadmap-protocol/
```

If the command changes are rolled back but the skill renames are kept (or vice versa), the system breaks:
- **Commands rolled back + skills renamed**: Old commands reference old skill names or use implicit loading; skills exist under new names.
- **Commands kept + skills rolled back**: New commands invoke `sc:*-protocol` skills that don't exist under that name.

Both must be rolled back or kept together.

### Rollback Risk Assessment

| Risk | Level | Detail |
|------|-------|--------|
| Partial rollback | HIGH | Command-skill name coupling means both must move together |
| Missing `Skill` tool permission | LOW | Only affects roadmap.md; other commands lack `allowed-tools` field |
| Behavioral regression | MEDIUM | Rolling back restores implicit loading, which worked before but was less reliable |
| Sync divergence | LOW | Both `src/` and `.claude/` copies are identical; rollback of one without the other would break `make verify-sync` |
