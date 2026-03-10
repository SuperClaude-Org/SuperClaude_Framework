# Adversarial Challenge: sc:task vs sc:task-unified Report Findings

**Date**: 2026-02-22
**Challenger**: Adversarial Agent (Opus 4.6)
**Branch**: feature/v2.0-Roadmap-v2
**Scope**: Critically evaluate 4 analysis reports for accuracy, completeness, and correctness of conclusions

---

## Adversarial Summary

| Challenge | Original Claim | Verdict | Notes |
|-----------|---------------|---------|-------|
| 1. Duplicate `name:` frontmatter | Both have `name: task` | **CONFIRMED** | Verified independently |
| 2. Incomplete migration narrative | task-unified replaces task.md | **CONFIRMED** | Evidence is unambiguous |
| 3. Risk rating (HIGH) | HIGH due to routing confusion | **PARTIALLY INVALIDATED** | Risk is overstated; actual routing is filename-based |
| 4. Proposed fix completeness | Replace task.md with task-unified.md content | **CONFIRMED with caveat** | One persona (`project-manager`) lost, but likely intentional |
| 5. Overlooked risks | N/A | **NEW RISKS FOUND** | Installer logic, plugins directory, skill dedup logic |

**Scorecard**: 2 CONFIRMED, 1 PARTIALLY INVALIDATED, 1 CONFIRMED WITH CAVEAT, 1 NEW RISKS FOUND

---

## Challenge 1: Duplicate `name:` Claim

### Reports' Claim
Both `task.md` and `task-unified.md` declare `name: task` in their YAML frontmatter, creating a namespace collision.

### Independent Verification

**File**: `src/superclaude/commands/task.md` (line 2)
```yaml
name: task
```

**File**: `src/superclaude/commands/task-unified.md` (line 2)
```yaml
name: task
```

**File**: `.claude/commands/sc/task.md` (line 2)
```yaml
name: task
```

**File**: `.claude/commands/sc/task-unified.md` (line 2)
```yaml
name: task
```

**File**: `src/superclaude/commands/task-mcp.md` (line 2)
```yaml
name: task-mcp
```

The reports correctly identify that both `task.md` and `task-unified.md` share `name: task`. The `task-mcp.md` file correctly uses a distinct name (`task-mcp`).

### Verdict: **CONFIRMED**

The duplicate `name: task` frontmatter is a verifiable fact. No error in the reports on this point.

---

## Challenge 2: Incomplete Migration Narrative

### Reports' Claim
`task-unified.md` was designed to replace `task.md` but the migration was never completed. The two files are NOT intentionally separate commands.

### Counter-Hypothesis
Could they be intentionally separate? Perhaps `task.md` is a simple orchestrator and `task-unified.md` is an advanced compliance-enforced variant, and the user is meant to choose between them.

### Evidence Against Counter-Hypothesis

1. **Explicit migration section in task-unified.md** (lines 537-560):
   ```markdown
   ## Migration from Legacy Commands
   ### From `/sc:task` (v1.x)
   # Old
   /sc:task create "feature" --strategy systematic
   # New (equivalent)
   /sc:task "feature" --strategy systematic --compliance auto
   ```

2. **Version history in task-unified.md** (lines 564-567):
   ```markdown
   - **v2.0.0** - Unified command merging sc:task and sc:task-mcp
   - **v1.0.0** - Original sc:task orchestration command
   ```

3. **task-mcp.md deprecation** (lines 8-10):
   ```yaml
   deprecated: true
   deprecated_by: "task-unified"
   migration_guide: "Use /sc:task --compliance [tier] instead"
   ```

4. **SKILL.md purpose statement** (line 26):
   ```markdown
   Single command replaces confusion between `sc:task` and `sc:task-mcp`
   ```

5. **No `sc-task` skill directory exists**. Only `sc-task-unified` exists at `src/superclaude/skills/sc-task-unified/`.

6. **task.md has NO version, NO deprecation markers, NO awareness of task-unified**. It is entirely self-contained and makes no reference to the unified variant.

7. **COMMANDS.md** (global framework) describes the `/sc:task` command with compliance tiers -- which is task-unified behavior, not task.md behavior. This confirms the framework documentation has already been updated to assume task-unified IS the `/sc:task` command, but the old file was never removed.

### Evidence Supporting Counter-Hypothesis

None found. There is zero evidence that the two were meant to coexist as separate commands.

### Verdict: **CONFIRMED**

The migration narrative is correct and strongly supported. `task-unified.md` is the intended successor. The old `task.md` was simply never cleaned up.

---

## Challenge 3: Risk Rating (HIGH)

### Reports' Claim
Risk is HIGH because both files share `name: task` frontmatter, leading to non-deterministic command routing.

### Counter-Evidence: How Claude Code Actually Resolves Commands

Based on [official Claude Code documentation](https://code.claude.com/docs/en/slash-commands) and the installer code at `src/superclaude/cli/install_commands.py`:

**For command files in `.claude/commands/`**: Claude Code resolves by **filename**, not frontmatter `name:` field.

- `/sc:task` resolves to `.claude/commands/sc/task.md` (the old v1.x command)
- `/sc:task-unified` resolves to `.claude/commands/sc/task-unified.md` (the v2.0 command)

**For skills in `.claude/skills/`**: The `name:` frontmatter field determines the slash command name. But the `sc-task-unified` skill is NOT installed as a skill. The installer (`install_skills.py`, lines 19-29) explicitly checks:

```python
def _has_corresponding_command(skill_name: str) -> bool:
    if not skill_name.startswith("sc-"):
        return False
    cmd_name = skill_name[3:]  # strip "sc-" prefix
    return (package_root / "commands" / f"{cmd_name}.md").exists()
```

Since `commands/task-unified.md` exists, the skill `sc-task-unified` is served by the command file, NOT installed separately. This means the `name: sc-task-unified` in the SKILL.md frontmatter is **never used for routing by Claude Code**.

### Actual Risk Analysis

| Scenario | What Happens | Risk |
|----------|-------------|------|
| User types `/sc:task` | Routes to `task.md` (old v1.x) by filename | **MEDIUM** -- gets old behavior, misses compliance |
| User types `/sc:task-unified` | Routes to `task-unified.md` (v2.0) by filename | **NONE** -- correct behavior |
| Framework docs say `/sc:task` has compliance tiers | User expects compliance, gets old command | **MEDIUM** -- documentation mismatch |
| SKILL.md says "Use `/sc:task` when:" | User follows guidance, gets wrong command | **MEDIUM** -- misdirection |

### Why This Is NOT HIGH Risk

1. **No non-deterministic routing**. The routing IS deterministic: filename wins. `/sc:task` always goes to `task.md`, `/sc:task-unified` always goes to `task-unified.md`.
2. **No crash, no data loss**. The old command still works, it just lacks compliance features.
3. **The user can always explicitly use `/sc:task-unified`** to get the v2.0 behavior.

### Why This IS Still MEDIUM Risk

1. **Documentation mismatch**: COMMANDS.md and ORCHESTRATOR.md describe compliance tiers under `/sc:task`, but `/sc:task` actually resolves to the old command without compliance tiers.
2. **SKILL.md misdirection**: The skill's trigger documentation says "Use `/sc:task` when:" which routes to the wrong file.
3. **User confusion**: A user who reads the docs expects `/sc:task` to have compliance tiers. It does not.
4. **The frontmatter `name: task` duplication IS a latent defect** that could cause issues if any tooling (help system, indexer, autocomplete) uses the `name:` field for deduplication.

### Verdict: **PARTIALLY INVALIDATED**

The reports overstate the risk. The actual severity is **MEDIUM**, not **HIGH**. The routing is deterministic (filename-based), not non-deterministic as the reports repeatedly claim. There is no "unpredictable behavior depending on file load order." However, the documentation-to-behavior mismatch is a real and meaningful problem that justifies MEDIUM risk.

The trigger-risks report (Report 3) does acknowledge in Section 4 that "In practice, Claude Code uses filenames for command resolution" but then continues to rate the overall risk as HIGH. This is internally inconsistent.

---

## Challenge 4: Proposed Fix Completeness

### Reports' Claim
Replace `task.md` with `task-unified.md` content (rename task-unified.md to task.md). No functionality is lost.

### Independent Comparison: What Is In task.md But NOT In task-unified.md?

1. **`project-manager` persona**: Listed in `task.md` frontmatter but absent from `task-unified.md`. The unified file adds `qa`, `refactorer`, `python-expert`, `quality-engineer` but drops `project-manager`.

2. **"CRITICAL BOUNDARIES" section** (task.md lines 91-116): Explicit boundary defining `/sc:task` as a "user-invoked discrete task execution" with strict completion criteria (stop when complete, do not continue). This behavioral guardrail is not present in task-unified.md.

3. **Distinction from `/sc:pm`** (task.md lines 97-99): Explicit documentation that `/sc:pm` is session-level orchestration while `/sc:task` is discrete execution. This context is absent from the unified version.

### Assessment

- The `project-manager` persona omission appears **intentional**. The unified version replaced it with more specialized personas (`qa`, `refactorer`, `quality-engineer`). The framework report (Report 1) correctly identified this as the only tangible gap.

- The "CRITICAL BOUNDARIES" section is **semantically important** but could be considered implicit in the unified command's more structured tier system. The unified command has explicit "Boundaries" (Will/Will Not) tables that cover similar ground, plus the compliance tiers inherently constrain behavior.

- The `/sc:pm` distinction is **useful documentation** that should ideally be preserved in the unified command to avoid scope creep confusion.

### Verdict: **CONFIRMED WITH CAVEAT**

The proposed fix is sound. The unified command is a strict functional superset. However:
- The `project-manager` persona drop is likely intentional but should be confirmed.
- The "CRITICAL BOUNDARIES" section and `/sc:pm` distinction from `task.md` should be merged into the unified command to preserve those behavioral guardrails.

The reports correctly identified the `project-manager` gap but did not flag the "CRITICAL BOUNDARIES" or `/sc:pm` distinction sections. This is a minor oversight.

---

## Challenge 5: Overlooked Risks

### 5A: task-mcp.md Three-Way Collision

**Reports' claim**: `task-mcp.md` is properly deprecated and not a collision risk.

**Verification**: `task-mcp.md` declares `name: task-mcp` (distinct from `task`), has `deprecated: true` frontmatter, and redirects to `/sc:task --compliance [tier]`. This is correctly handled.

However, `task-mcp.md` IS still installed to `.claude/commands/sc/task-mcp.md`. A user can still invoke `/sc:task-mcp`. The deprecation notice is only visible INSIDE the file -- Claude Code does not filter out deprecated command files during installation or display warnings at invocation time. This means `/sc:task-mcp` silently loads a deprecated command.

**Risk**: LOW. The file is properly self-documenting with a deprecation notice. But the installer could benefit from a deprecation filter.

**Report coverage**: Reports mention this briefly but do not flag the silent-installation-of-deprecated-files as a systemic issue. **Partially overlooked.**

### 5B: Plugins Directory Staleness

**Finding**: The `plugins/superclaude/commands/` directory contains ONLY `task.md` (the old v1.x version). It does NOT contain `task-unified.md`.

This means:
- Users installing via the plugins path (Priority 2 in install_commands.py) will ONLY get the old `task.md`.
- The plugins directory is stale and out of sync with `src/superclaude/commands/`.

**Risk**: MEDIUM. The plugins path is a secondary install source, but anyone using it gets an incomplete installation missing `task-unified.md` entirely.

**Report coverage**: Report 2 (cross-refs) briefly mentions the plugins directory having `task.md` but does NOT flag it as a risk. **Overlooked.**

### 5C: Installer Dedup Logic in install_skills.py

**Finding**: The skill installer has a `_has_corresponding_command()` check (line 19-29) that strips the `sc-` prefix and checks if a matching command file exists. For `sc-task-unified`, it checks for `commands/task-unified.md`. Since that file exists, the skill is NOT installed separately.

But if the proposed fix renames `task-unified.md` to `task.md`, then the check would look for `commands/task-unified.md`, which NO LONGER EXISTS. This means `sc-task-unified` would suddenly be installed as a standalone skill to `.claude/skills/sc-task-unified/`, creating a new entry point (`/sc-task-unified` via skill `name:` field) that didn't exist before.

**Risk**: MEDIUM. The proposed fix (rename task-unified.md to task.md) would break the installer's skill deduplication logic and potentially create a new duplicate entry.

**Report coverage**: None of the 4 reports mention this installer logic dependency. **Completely overlooked.**

### 5D: COMMANDS.md and ORCHESTRATOR.md References

**Finding**: Both framework files (in `src/superclaude/core/` and the global `~/.claude/` copies) reference `/sc:task` with compliance tier behavior. They do NOT reference `task-unified` at all.

- `COMMANDS.md` line 81: `/sc:task [description] [flags]` described as "Unified Task Command (Compliance-Enforced)"
- `ORCHESTRATOR.md` line 153: "Route `/sc:task` commands to appropriate compliance tier"

These references are **already correct for the proposed fix** (renaming task-unified.md to task.md). No breaking changes needed.

**Risk**: NONE from the rename. But currently these references describe behavior that `/sc:task` does NOT have (because it resolves to the old `task.md`). This is a documentation-reality mismatch.

**Report coverage**: Report 4 mentions this at E5 but understates it. The framework documentation has ALREADY been updated as if the migration were complete. The migration itself is the lagging component.

### 5E: Skill Directory Name After Rename

**Finding**: If `task-unified.md` is renamed to `task.md`, the skill directory `sc-task-unified/` becomes orphaned in name. The `_has_corresponding_command()` function strips `sc-` to get `task-unified` and checks for `commands/task-unified.md`. After the rename, that file no longer exists.

Options:
1. Also rename the skill directory from `sc-task-unified/` to `sc-task/`
2. Update the `_has_corresponding_command()` function to handle the mapping

**Risk**: MEDIUM. Must be addressed as part of the rename or the skill dedup breaks.

**Report coverage**: **Completely overlooked.**

---

## Final Verdict

### Do the reports' conclusions hold up under adversarial scrutiny?

**Largely yes, with significant nuance.**

The core finding -- that `task.md` and `task-unified.md` represent an incomplete migration and should be consolidated -- is **correct and well-supported**. The evidence is overwhelming that `task-unified.md` was designed to replace `task.md`.

However, the reports make **two significant errors**:

1. **Overstated risk severity**: The reports repeatedly claim "non-deterministic routing" and "unpredictable behavior depending on file load order." This is factually wrong. Claude Code resolves commands by filename, not frontmatter `name:` field. The routing IS deterministic. The actual risk is a documentation-to-behavior mismatch (MEDIUM), not a routing collision (HIGH).

2. **Incomplete fix analysis**: The proposed fix (rename `task-unified.md` to `task.md`) would break the installer's skill deduplication logic in `install_skills.py`. The `_has_corresponding_command()` function checks for `commands/task-unified.md`, and after the rename that file no longer exists. This causes `sc-task-unified` to be installed as a standalone skill, creating a new potential duplicate entry. None of the 4 reports identified this dependency.

### Corrected Risk Rating

| Risk Area | Reports' Rating | Corrected Rating | Rationale |
|-----------|----------------|------------------|-----------|
| Frontmatter collision | HIGH | **MEDIUM** | Filename routing prevents hard collision; `name:` is metadata, not routing key |
| Documentation mismatch | Not explicitly rated | **MEDIUM** | Framework docs describe unified behavior under `/sc:task`, but old file resolves |
| SKILL.md misdirection | MEDIUM | **MEDIUM** | Accurate; triggers point to wrong command |
| Proposed fix breakage | Not rated | **MEDIUM** | Installer dedup logic breaks on rename |
| Overall | HIGH | **MEDIUM** | Degraded experience, not system failure |

### Recommended Fix (Amended)

The reports' proposed fix is directionally correct but incomplete. The full fix should include:

1. Delete `src/superclaude/commands/task.md` (old v1.x)
2. Rename `src/superclaude/commands/task-unified.md` to `src/superclaude/commands/task.md`
3. Rename `src/superclaude/skills/sc-task-unified/` to `src/superclaude/skills/sc-task/` (or update the installer dedup logic)
4. Update SKILL.md invocation references for consistency
5. Remove or update `plugins/superclaude/commands/task.md` to match the unified content
6. Merge the "CRITICAL BOUNDARIES" section and `/sc:pm` distinction from old `task.md` into the unified file
7. Consider removing `task-mcp.md` entirely (deprecated, migration guide exists in unified file)
8. Run `make sync-dev` and `make verify-sync`
