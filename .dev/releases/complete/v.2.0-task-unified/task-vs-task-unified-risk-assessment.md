# Risk Assessment: `sc:task` vs `sc:task-unified` Command Collision

**Date**: 2026-02-22
**Analyst**: T4 (Independent Risk Assessment)
**Scope**: Command naming collision, routing ambiguity, user confusion

---

## Executive Summary

**Risk Rating: HIGH**

Both `src/superclaude/commands/task.md` and `src/superclaude/commands/task-unified.md` declare **`name: task`** in their YAML frontmatter. This is an identical namespace collision. Three separate `.md` files are installed into `.claude/commands/sc/` (`task.md`, `task-unified.md`, `task-mcp.md`), two of which claim to be the authoritative `/sc:task` command. The `task-unified.md` file is designed to be the successor to `task.md` (as stated in its own v2.0.0 migration section), but the old `task.md` has not been removed or renamed. This creates guaranteed confusion for Claude Code's command resolution and for users.

---

## Independent Analysis Methodology

1. Read all three source command files (`task.md`, `task-unified.md`, `task-mcp.md`) in `src/superclaude/commands/`
2. Read the SKILL.md for `sc-task-unified`
3. Read the installed command files in `.claude/commands/sc/`
4. Compared `name:` frontmatter across all relevant files
5. Examined CLI routing code in `src/superclaude/cli/install_commands.py`
6. Searched COMMANDS.md and ORCHESTRATOR.md for routing rules referencing `task-unified`
7. Cross-referenced SKILL.md trigger instructions against command file triggers

---

## Evidence Collected

### E1: Duplicate `name: task` Frontmatter (CRITICAL)

| File | `name:` value | Version | Status |
|------|---------------|---------|--------|
| `src/superclaude/commands/task.md` | `task` | (none) | Active |
| `src/superclaude/commands/task-unified.md` | `task` | 2.0.0 | Active |
| `src/superclaude/commands/task-mcp.md` | `task-mcp` | (none) | `deprecated: true` |
| `src/superclaude/skills/sc-task-unified/SKILL.md` | `sc-task-unified` | (none) | Active |

**Finding**: Two files (`task.md` and `task-unified.md`) both declare `name: task`. This is a direct namespace collision. Claude Code may resolve `/sc:task` to either file unpredictably depending on load order, caching, or alphabetical sorting.

### E2: Three Installed Files Coexist

In `.claude/commands/sc/`:
- `task.md` (4,862 bytes) -- the old task command
- `task-unified.md` (18,447 bytes) -- the new unified command
- `task-mcp.md` (10,595 bytes) -- deprecated, properly marked

The installer (`install_commands.py`) copies all `.md` files from `src/superclaude/commands/` to the target directory without any filtering or deduplication logic. It uses filename-based identity (`command_file.name`), not `name:` frontmatter-based identity.

### E3: SKILL.md Uses `/sc:task` as Invocation

The SKILL.md for `sc-task-unified` (line 34) instructs:

> Use `/sc:task` when:

But the skill itself is invoked as `/sc:task-unified`. The SKILL.md examples (lines 233-275) all show `/sc:task "..."` syntax, not `/sc:task-unified "..."`. This creates confusion about which entry point triggers the skill.

### E4: `task-unified.md` Claims `/sc:task` Identity

The `task-unified.md` command file titles itself:

> `# /sc:task - Unified Task Command`

And its migration section explicitly states it replaces both the old `/sc:task` and `/sc:task-mcp`. But the old `task.md` still exists and still claims the same identity.

### E5: No Routing Disambiguation in Framework Files

Neither `COMMANDS.md` nor `ORCHESTRATOR.md` reference `task-unified` at all. The COMMANDS.md section titled "Unified Task Command" references only `/sc:task` (with no mention of the separate `task-unified.md` file). The ORCHESTRATOR.md routing tables only reference `/task` patterns.

This means the framework documentation treats there as being one command called `/sc:task`, but the filesystem contains two competing implementations.

### E6: No CLI-Level Routing Logic

The `install_commands.py` file performs a simple file copy (`shutil.copy2`) with no awareness of `name:` frontmatter. There is no deduplication, conflict detection, or priority system. Both files are always installed.

### E7: Contradictory Trigger Overlap

Both `task.md` and `task-unified.md` claim to handle:
- Complex task execution
- Multi-agent coordination
- Strategy flags (`--strategy systematic|agile|enterprise`)
- `--parallel` and `--delegate` flags
- MCP server routing

The `task-unified.md` adds compliance tiers (`--compliance strict|standard|light|exempt`) but otherwise subsumes all of `task.md`'s functionality.

---

## Risk Rating: HIGH

**Justification**: Under normal usage, when a user types `/sc:task "implement feature"`, Claude Code must resolve which of the two installed command files (`task.md` or `task-unified.md`) to load. Since both declare `name: task`, the resolution is non-deterministic from the user's perspective. This is not a theoretical risk -- it is a structural defect present in every installation.

### Why Not CRITICAL

The risk is HIGH rather than CRITICAL because:
1. Claude Code likely resolves by filename (`task.md` wins over `task-unified.md` alphabetically/by shorter name)
2. The SKILL mechanism (`/sc:task-unified`) provides an alternative explicit entry point
3. Both commands share enough behavioral overlap that partial functionality works regardless of which resolves

### Why Not MODERATE

The risk exceeds MODERATE because:
1. The `name:` collision is a concrete, present defect -- not theoretical
2. Users who want the compliance-tier behavior may get the old command instead
3. The framework documentation (`COMMANDS.md`, `ORCHESTRATOR.md`) is unaware of `task-unified` as a separate entity
4. The SKILL.md itself directs users to use `/sc:task` (not `/sc:task-unified`), which may resolve to the wrong file

---

## Safeguards Present

1. **task-mcp.md is properly deprecated**: It has `deprecated: true` and `deprecated_by: "task-unified"` frontmatter. This is the correct pattern.
2. **SKILL.md has a distinct name**: `sc-task-unified` (not `task`), so the skill system itself is not in collision.
3. **Filename differentiation**: The files have different filenames (`task.md` vs `task-unified.md`), which Claude Code's file-based resolution can distinguish.

---

## Vulnerabilities Found

| # | Vulnerability | Severity | Impact |
|---|---------------|----------|--------|
| V1 | Duplicate `name: task` in frontmatter of two files | HIGH | Non-deterministic command resolution |
| V2 | Both files installed with no conflict detection | HIGH | Every installation has both competing files |
| V3 | SKILL.md directs to `/sc:task` instead of `/sc:task-unified` | MODERATE | Users directed to ambiguous entry point |
| V4 | COMMANDS.md/ORCHESTRATOR.md unaware of `task-unified` | MODERATE | Framework routing cannot disambiguate |
| V5 | No deprecation marker on old `task.md` | MODERATE | Old command appears fully active |
| V6 | `task-unified.md` claims to BE `/sc:task` (title + name) | HIGH | Identity confusion -- is it a replacement or an addition? |

---

## Refactoring Proposal

### Recommended Approach: Complete the Unification

The `task-unified.md` file was designed to replace `task.md` (as stated in its own migration section). The unification was started but never completed. The fix is to finish the job.

### Step-by-Step Plan

#### Phase 1: Deprecate Old `task.md` (Immediate)

**File**: `src/superclaude/commands/task.md`

Add deprecation frontmatter matching the pattern already used by `task-mcp.md`:

```yaml
---
name: task-legacy
description: "[DEPRECATED] Execute complex tasks - use /sc:task instead"
deprecated: true
deprecated_by: "task-unified"
migration_guide: "Use /sc:task --strategy [type] instead"
---
```

**Rationale**: The old `task.md` becomes `task-legacy.md` (or gets deprecation markers) so it no longer collides with the `name: task` in `task-unified.md`.

#### Phase 2: Rename `task-unified.md` to `task.md` (Primary Fix)

1. **Delete** `src/superclaude/commands/task.md` (the old one)
2. **Rename** `src/superclaude/commands/task-unified.md` to `src/superclaude/commands/task.md`
3. The renamed file keeps `name: task` and becomes the sole owner of that namespace
4. **Mirror** to `.claude/commands/sc/` via `make sync-dev`

**Files modified**:
- `src/superclaude/commands/task.md` (deleted, replaced by renamed unified)
- `src/superclaude/commands/task-unified.md` (renamed to `task.md`)
- `.claude/commands/sc/task.md` (synced)
- `.claude/commands/sc/task-unified.md` (removed)

#### Phase 3: Update SKILL.md References

**File**: `src/superclaude/skills/sc-task-unified/SKILL.md`

- Change usage examples from `/sc:task-unified [description]` to `/sc:task [description]`
- The skill name (`sc-task-unified`) can remain as-is (it is the skill name, not the command name)
- OR rename the skill directory to `sc-task` for consistency

#### Phase 4: Update Framework Documentation

**Files**:
- `COMMANDS.md`: Add note that `/sc:task` now includes compliance tiers
- `ORCHESTRATOR.md`: Update routing tables if needed (currently no `task-unified` references, so minimal change)

#### Phase 5: Installer Enhancement (Optional, Recommended)

**File**: `src/superclaude/cli/install_commands.py`

Add a post-install cleanup step:

```python
# Remove deprecated command files that have been superseded
deprecated_files = ['task-unified.md']  # Now merged into task.md
for dep_file in deprecated_files:
    dep_path = target_path / dep_file
    if dep_path.exists():
        dep_path.unlink()
```

### Migration Path for Existing Users

1. Users currently invoking `/sc:task` get the unified behavior (improvement)
2. Users currently invoking `/sc:task-unified` see a deprecation notice directing them to `/sc:task`
3. The skill `/sc:task-unified` continues to work via the SKILL.md mechanism (skills resolve by directory name, not command `name:` frontmatter)
4. `task-mcp.md` remains deprecated with its existing migration notice

### Estimated Effort

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1: Deprecate old task.md | 5 minutes | None |
| Phase 2: Rename task-unified to task | 10 minutes | Low (file rename) |
| Phase 3: Update SKILL.md | 10 minutes | None |
| Phase 4: Update framework docs | 15 minutes | None |
| Phase 5: Installer cleanup | 20 minutes | Low |
| **Total** | **~1 hour** | **Low** |

---

## Recommendations

1. **Immediate**: Execute Phase 1 and Phase 2 to eliminate the `name: task` collision. This is the minimum viable fix.
2. **Short-term**: Execute Phases 3-4 to ensure documentation consistency.
3. **Optional**: Execute Phase 5 for a robust installer that prevents stale files.
4. **Principle**: Establish a rule that no two command files may share the same `name:` frontmatter value. Consider adding a CI check (`make verify-sync` or similar) that detects duplicate `name:` values across command files.
5. **Pattern**: The `task-mcp.md` deprecation pattern (`deprecated: true`, `deprecated_by: "..."`) is well-designed and should be applied consistently. Future command supersessions should follow this same pattern.

---

## Appendix: File Locations

| File | Absolute Path |
|------|---------------|
| Old task command (source) | `/config/workspace/SuperClaude_Framework/src/superclaude/commands/task.md` |
| Unified task command (source) | `/config/workspace/SuperClaude_Framework/src/superclaude/commands/task-unified.md` |
| Deprecated task-mcp (source) | `/config/workspace/SuperClaude_Framework/src/superclaude/commands/task-mcp.md` |
| Task-unified SKILL.md | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-task-unified/SKILL.md` |
| Old task command (installed) | `/config/workspace/SuperClaude_Framework/.claude/commands/sc/task.md` |
| Unified task command (installed) | `/config/workspace/SuperClaude_Framework/.claude/commands/sc/task-unified.md` |
| Deprecated task-mcp (installed) | `/config/workspace/SuperClaude_Framework/.claude/commands/sc/task-mcp.md` |
| CLI installer | `/config/workspace/SuperClaude_Framework/src/superclaude/cli/install_commands.py` |
| Framework COMMANDS.md | `/config/.claude/COMMANDS.md` |
| Framework ORCHESTRATOR.md | `/config/.claude/ORCHESTRATOR.md` |
