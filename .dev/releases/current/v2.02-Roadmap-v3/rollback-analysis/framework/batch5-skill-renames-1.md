# Batch 5: Skill Directory Renames (Part 1 of 2)

**Analysis Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Scope**: 3 skill directories renamed with SKILL.md content modifications

---

## Naming Convention Change

**Pattern**: `sc-{name}` --> `sc-{name}-protocol`

All three skill directories add a `-protocol` suffix. This aligns the directory name with a naming convention that distinguishes skill packages (behavioral protocol definitions) from other component types (commands, agents). The SKILL.md frontmatter `name:` field is updated to match.

---

## 1. sc-adversarial --> sc-adversarial-protocol

### Rename Details

| Property | Value |
|----------|-------|
| Old Path | `src/superclaude/skills/sc-adversarial/` |
| New Path | `src/superclaude/skills/sc-adversarial-protocol/` |
| Git Similarity | R099 (99% similar) |
| Line Count | 1747 --> 1747 (unchanged) |

### Content Modification (SKILL.md)

**Single change** -- frontmatter name field only:

```diff
 ---
-name: sc:adversarial
+name: sc:adversarial-protocol
 description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
 allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
 ---
```

No other content changes. The body of the 1747-line file is identical.

### Companion Files (Pure Renames, R100)

| File | Status |
|------|--------|
| `__init__.py` | R100 (pure rename) |
| `refs/agent-specs.md` | R100 (pure rename) |
| `refs/artifact-templates.md` | R100 (pure rename) |
| `refs/debate-protocol.md` | R100 (pure rename) |
| `refs/scoring-protocol.md` | R100 (pure rename) |

**Total files moved**: 6 (1 modified, 5 pure renames)

---

## 2. sc-cleanup-audit --> sc-cleanup-audit-protocol

### Rename Details

| Property | Value |
|----------|-------|
| Old Path | `src/superclaude/skills/sc-cleanup-audit/` |
| New Path | `src/superclaude/skills/sc-cleanup-audit-protocol/` |
| Git Similarity | R099 (99% similar) |
| Line Count | 133 --> 133 (unchanged) |

### Content Modification (SKILL.md)

**Single change** -- frontmatter name field only:

```diff
 ---
-name: cleanup-audit
+name: sc:cleanup-audit-protocol
 description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
```

Note: This change also fixes a naming inconsistency. The old name was `cleanup-audit` (missing the `sc:` prefix), while the new name is `sc:cleanup-audit-protocol` (adding both the `sc:` prefix and `-protocol` suffix).

No other content changes. The body of the 133-line file is identical.

### Companion Files (Pure Renames, R100)

| File | Status |
|------|--------|
| `__init__.py` | R100 (pure rename) |
| `rules/dynamic-use-checklist.md` | R100 (pure rename) |
| `rules/pass1-surface-scan.md` | R100 (pure rename) |
| `rules/pass2-structural-audit.md` | R100 (pure rename) |
| `rules/pass3-cross-cutting.md` | R100 (pure rename) |
| `rules/verification-protocol.md` | R100 (pure rename) |
| `scripts/repo-inventory.sh` | R100 (pure rename) |
| `templates/batch-report.md` | R100 (pure rename) |
| `templates/final-report.md` | R100 (pure rename) |
| `templates/finding-profile.md` | R100 (pure rename) |
| `templates/pass-summary.md` | R100 (pure rename) |

**Total files moved**: 12 (1 modified, 11 pure renames)

---

## 3. sc-roadmap --> sc-roadmap-protocol

### Rename Details

| Property | Value |
|----------|-------|
| Old Path | `src/superclaude/skills/sc-roadmap/` |
| New Path | `src/superclaude/skills/sc-roadmap-protocol/` |
| Git Similarity | R081 (81% similar) |
| Line Count | 333 --> 350 (+17 lines) |

### Content Modifications (SKILL.md)

This is the most substantially modified file in the batch. Three categories of changes:

#### Change A: Frontmatter name field

```diff
 ---
-name: sc:roadmap
+name: sc:roadmap-protocol
```

#### Change B: Allowed-tools addition

```diff
-allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
+allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

The `Skill` tool is added to the allowed-tools list. This enables the roadmap skill to invoke other skills (specifically `sc:adversarial-protocol`) via the Skill tool.

#### Change C: Wave 2, Step 3 -- Multi-roadmap expansion (major rewrite)

The old version had a single condensed paragraph for `--multi-roadmap` handling:

```
OLD (1 line):
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from
   `refs/adversarial-integration.md` [...] The adversarial output replaces
   template-based generation.
```

The new version replaces this with a detailed multi-step protocol (18 new lines replacing 1 old line, net +17):

```
NEW (steps 3a through 3f):
3a [Parse agents]       - Agent spec parsing algorithm detail
3b [Expand variants]    - Model-only agent expansion with auto-detected persona
3c [Add orchestrator]   - Orchestrator threshold lowered from >=5 to >=3
3d [Execute fallback]   - Full fallback protocol (F1-F5) for when Skill tool unavailable
3e [Consume contract]   - Return contract consumption with error handling
3f [Skip template]      - Template bypass when adversarial path succeeds
```

Key substantive changes within the expansion:

1. **Orchestrator threshold lowered**: Old version added orchestrator at agent count >= 5; new version adds at >= 3.

2. **Fallback protocol introduced**: Step 3d defines a complete fallback mechanism (F1 through F5) for when the Skill tool is unavailable. This was not present in the old version. The fallback uses the `Task` tool to:
   - F1: Dispatch variant generation agents
   - F2/F3 (merged): Diff analysis + single-round debate
   - F4/F5 (merged): Base selection + merge + return contract generation

3. **Return contract consumption detailed**: Step 3e adds explicit handling for missing files, YAML parse errors, and status routing with convergence thresholds (0.6).

4. **Template skip logic**: Step 3f explicitly documents that template-based generation is bypassed when adversarial path succeeds.

#### Change D: Wave 2 Step 3 duplication (second occurrence)

The same Wave 2 Step 3 expansion appears twice in the diff. The old file had this same block structure duplicated in the document (once in Wave 2 section, once in a later reference section), and both occurrences received the identical expansion treatment.

### Companion Files (Pure Renames, R100)

| File | Status |
|------|--------|
| `__init__.py` | R100 (pure rename) |
| `refs/adversarial-integration.md` | R100 (pure rename) |
| `refs/extraction-pipeline.md` | R100 (pure rename) |
| `refs/scoring.md` | R100 (pure rename) |
| `refs/templates.md` | R100 (pure rename) |
| `refs/validation.md` | R100 (pure rename) |

**Total files moved**: 7 (1 modified, 6 pure renames)

---

## Summary Statistics

| Skill Directory | Files Moved | SKILL.md Changes | Similarity |
|----------------|-------------|------------------|------------|
| sc-adversarial-protocol | 6 | Name field only | R099 |
| sc-cleanup-audit-protocol | 12 | Name field + prefix fix | R099 |
| sc-roadmap-protocol | 7 | Name, tools, Wave 2 rewrite | R081 |
| **Total** | **25** | | |

### Rollback Considerations

1. **Directory renames**: All 25 files need path restoration from `sc-{name}-protocol/` back to `sc-{name}/`.

2. **Frontmatter name restoration**:
   - `sc:adversarial-protocol` --> `sc:adversarial`
   - `sc:cleanup-audit-protocol` --> `cleanup-audit` (note: restoring the old inconsistent name without `sc:` prefix)
   - `sc:roadmap-protocol` --> `sc:roadmap`

3. **Roadmap SKILL.md content restoration**: The `Skill` tool must be removed from allowed-tools, and the expanded Wave 2 Step 3 must be collapsed back to the single-paragraph version. This is the only file with non-trivial content changes requiring careful restoration.

4. **Cross-references**: Any other files that reference the old skill directory paths (e.g., `sc-adversarial/SKILL.md` in Wave 0 of the roadmap skill) should be checked for consistency. The roadmap SKILL.md Wave 0 step 5 still references `src/superclaude/skills/sc-adversarial/SKILL.md` (old path) -- this may be intentional (checking at runtime) or a missed update.
