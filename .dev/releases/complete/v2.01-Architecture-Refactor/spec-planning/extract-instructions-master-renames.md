# Architectural Patterns Extracted from v2.02 Rollback Analysis

**Source files**:
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/instructions/00-MASTER-RECREATION-GUIDE.md`
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/instructions/01-skill-renames.md`

**Extraction date**: 2026-02-24
**Filter**: v2.01 architectural patterns only. v2.02 roadmap-specific implementation details excluded.

---

## 1. Skill Rename Pattern (General Procedure)

The general procedure for renaming any skill directory follows this sequence. This is reusable for ALL skills, not just the 5 that were renamed in v2.02.

### 1.1 Directory Rename Convention

```
OLD: src/superclaude/skills/sc-{name}/
NEW: src/superclaude/skills/sc-{name}-protocol/
```

- Use `git mv` (not filesystem `mv`) to preserve git history tracking.
- All companion files within the directory (refs/, rules/, templates/, scripts/, `__init__.py`) are carried along by the directory rename -- no individual file renames needed.

### 1.2 SKILL.md Frontmatter `name` Field Convention

The canonical naming convention for the `name:` frontmatter field is:

```
sc:{name}-protocol
```

Key rules:
- **Prefix**: Always `sc:` (colon, not hyphen). Several legacy skills used `sc-` (hyphen) or had no prefix at all. The convention normalizes ALL to `sc:`.
- **Suffix**: Always `-protocol`.
- **Separator**: Colon between `sc` and the name, hyphens within the name itself.

**Pre-existing inconsistencies found and fixed** (systemic issue to watch for in any future skill):

| Skill | Old `name` Value | Problem |
|-------|-----------------|---------|
| cleanup-audit | `cleanup-audit` | Missing `sc:` prefix entirely |
| task-unified | `sc-task-unified` | Used hyphen (`sc-`) instead of colon (`sc:`) |
| validate-tests | `sc-validate-tests` | Used hyphen (`sc-`) instead of colon (`sc:`) |
| adversarial | `sc:adversarial` | Correct prefix, just missing `-protocol` suffix |
| roadmap | `sc:roadmap` | Correct prefix, just missing `-protocol` suffix |

**Lesson**: Any rename operation should audit existing `name` values for prefix inconsistencies, not just append `-protocol`.

### 1.3 Required SKILL.md Frontmatter Fields

Every SKILL.md must have at minimum:

| Field | Required | Notes |
|-------|----------|-------|
| `name` | YES | Must follow `sc:{name}-protocol` convention |
| `description` | YES | Short description of skill purpose |
| `allowed-tools` | YES | Comma-separated list of tools the skill may use |

Optional but observed fields: `category`, `complexity`, `mcp-servers`, `personas`, `argument-hint`.

### 1.4 `allowed-tools` Must Include `Skill`

**Systemic bug (BUG-001)**: When skills invoke other skills via `> Skill sc:{name}-protocol`, the `Skill` tool must be listed in the invoking skill's `allowed-tools` frontmatter. This was missed in 4 of 5 skills during original implementation.

**Rule**: Any skill that references another skill (or any command that invokes a skill) MUST include `Skill` in its `allowed-tools` list.

**Risk if omitted**: If Claude Code enforces the `allowed-tools` whitelist strictly, the skill invocation will fail silently or with an error.

---

## 2. Execution Order / Dependency Graph

The general dependency graph for any architectural refactor involving skills, commands, and build tooling:

```
Phase A: Policy/Planning Documents (foundation, no deps)
    |
Phase B: Artifact Verification (read-only, no deps)
    |
Phase C: Skill Renames (foundation layer, no deps on commands)
    |
    v
Phase D: Command Updates (DEPENDS ON Phase C -- commands reference skill names)
    |
Phase E: Build Tooling / Makefile Updates (DEPENDS ON Phase C naming convention)
    |
    v
Phase F: Dev Copy Sync (DEPENDS ON C, D, E all complete)
    |
    v
Phase G: Lint / Validation (DEPENDS ON Phase F)
```

**Key dependency rules**:
1. Skill renames are the foundation layer -- they have no dependencies.
2. Command updates MUST follow skill renames because commands reference `-protocol` skill names.
3. Makefile/build tooling updates depend on the naming convention being finalized.
4. Dev copy sync (`make sync-dev`) must happen AFTER all `src/` changes are complete.
5. Validation (`make lint-architecture`, `make verify-sync`) runs last.

**Phase file counts** (for estimation):

| Phase | Typical Files Affected |
|-------|----------------------|
| Skill Renames | 5-6 files per skill (SKILL.md + companions) |
| Command Updates | 1 per command |
| Build Tooling | 1 (Makefile) |
| Dev Copy Sync | Mirrors all src/ changes to .claude/ |
| Validation | 0 (read-only) |

---

## 3. Verification Checklist Pattern

Reusable verification template for any architectural refactor:

### 3.1 Structural Validation

```bash
# All skill directories renamed (parameterize skill list)
for skill in $SKILL_LIST; do
  test -d "src/superclaude/skills/$skill/" && echo "PASS: $skill" || echo "FAIL: $skill"
done

# No old directories remain
ls src/superclaude/skills/ | grep -v protocol | grep "^sc-"
# Expected: no output
```

### 3.2 Naming Convention Validation

```bash
# All SKILL.md name fields use sc: prefix and -protocol suffix
for d in src/superclaude/skills/sc-*-protocol/SKILL.md; do
  name=$(grep "^name:" "$d" | head -1)
  echo "$d -> $name"
  echo "$name" | grep -q "sc:.*-protocol" && echo "  PASS" || echo "  FAIL"
done
```

### 3.3 Command-to-Skill Wiring Validation

```bash
# All paired commands have ## Activation sections
for f in $COMMAND_LIST; do
  grep -q "## Activation" "src/superclaude/commands/$f.md" && echo "$f: PASS" || echo "$f: FAIL"
done

# All commands reference correct skill name
for f in $COMMAND_LIST; do
  grep -q "sc:.*-protocol" "src/superclaude/commands/$f.md" && echo "$f: PASS" || echo "$f: FAIL"
done
```

### 3.4 Sync Validation

```bash
make verify-sync    # src/ and .claude/ parity
make lint-architecture   # Convention enforcement (if target exists)
```

### 3.5 Comprehensive Checklist Template

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | N skill dirs renamed | `ls src/superclaude/skills/ \| grep protocol \| wc -l` | N |
| 2 | 0 old skill dirs | `ls src/superclaude/skills/ \| grep -v protocol \| grep "^sc-" \| wc -l` | 0 |
| 3 | N commands have Activation | `grep -rl "## Activation" src/superclaude/commands/` | N files |
| 4 | Sync passes | `make verify-sync` | exit 0 |
| 5 | Lint passes | `make lint-architecture` | 0 errors |
| 6 | All commands have Skill in allowed-tools | grep for each | N/N |
| 7 | All stale path references updated | grep for old paths | 0 matches |

---

## 4. Systemic Bugs Revealing Architectural Issues

These bugs are not v2.02-specific -- they reveal patterns that will recur in any skill/command refactor.

### 4.1 BUG-001: `allowed-tools` Inconsistency

**Pattern**: When adding a new invocation mechanism (e.g., `> Skill`), the tool must be added to `allowed-tools` in ALL files that use it, not just one. Original implementation added `Skill` to 1 of 5 skills.

**Prevention rule**: After any change that introduces a new tool usage, audit ALL skills and commands for the tool in their `allowed-tools`.

### 4.2 BUG-002 / BUG-005: Stale Path References After Rename

**Pattern**: When renaming directories, internal cross-references within other files become stale. The original implementation missed:
- `validate-tests.md` line 63 still referencing `skills/sc-validate-tests/` (old path)
- `roadmap SKILL.md` Wave 0 step 5 still referencing `sc-adversarial/` (old path)

**Prevention rule**: After any directory rename, run a project-wide grep for the old path:
```bash
grep -r "sc-{old-name}/" src/ .claude/ docs/
# Any matches are stale references that need updating
```

### 4.3 BUG-004: Architecture Policy Duplication

**Pattern**: Two identical files existed (`docs/architecture/command-skill-policy.md` and `src/superclaude/ARCHITECTURE.md`) with no indication of which was canonical and no sync mechanism.

**Prevention rule**: Single source of truth for policy documents. If a file must exist in two locations, use one of: symlink, Makefile sync target, or a one-line pointer file.

### 4.4 BUG-011/012: Historical Artifacts Using Pre-Rename Paths

**Pattern**: Dev artifacts and tasklist files continue to reference old paths after a rename. 24 of 25 dev artifacts used pre-rename paths.

**Decision**: Accept as historical records OR batch-update. Low priority since these are non-executable design documents. The key is to not confuse historical artifact paths with current canonical paths.

---

## 5. Command-to-Skill Wiring Architecture

### 5.1 The `## Activation` Section Pattern

Every command that has a paired protocol skill MUST include this section:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:{name}-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification ({description}) is in the protocol skill.
```

**Placement**: After the Options/Arguments table, before any Behavioral Summary.

### 5.2 Command Size Policy

Commands that have paired skills should be kept lean (routing + flags only). The full behavioral specification lives in the skill.

| Threshold | Severity |
|-----------|----------|
| >500 lines | ERROR (must split) |
| >200 lines | WARN |
| <200 lines | PASS |

The `task-unified.md` command was reduced from ~567 to ~106 lines by extracting behavioral content to its skill.

### 5.3 `allowed-tools` in Commands

Commands that invoke skills via `> Skill` must ALSO have `Skill` in their own `allowed-tools` (or add an `allowed-tools` field if only `mcp-servers` exists).

---

## 6. `lint-architecture` CI Checks (Reusable Conventions)

Six checks implemented as a Makefile target, enforcing the command-skill architecture:

| Check | Policy | What It Validates | Severity |
|-------|--------|-------------------|----------|
| 1 | Command -> Skill link | Command `## Activation` references a skill directory that exists | ERROR |
| 2 | Skill -> Command link | Skill `sc-*-protocol/` has a matching command file | ERROR |
| 3 | Command size | >500 = ERROR, >200 = WARN | ERROR/WARN |
| 4 | Activation section | Paired command has `## Activation` section | ERROR |
| 5 | SKILL.md frontmatter | Has `name`, `description`, `allowed-tools` fields | ERROR |
| 6 | Protocol naming | Directory `-protocol` suffix matches SKILL.md `name` `-protocol` suffix | ERROR |

**Missing checks** (noted as gaps, not yet implemented):
- Policy #5: Inline protocol detection (command with `-protocol` skill contains YAML blocks >20 lines)
- Policy #7: Activation reference correctness (`## Activation` contains `Skill sc:<name>-protocol`)

---

## 7. Rollback Procedure Pattern

Two rollback strategies, reusable for any architectural refactor:

### 7.1 Full Git Rollback (Recommended)

When no other work is intermixed with the refactor:

```bash
# Undo all staged and unstaged changes in the affected area
git checkout HEAD -- src/superclaude/skills/

# Remove any .claude/ directories that were created by sync
rm -rf .claude/skills/sc-*-protocol

# Re-sync .claude/ from restored src/
make sync-dev
```

### 7.2 Manual Reverse (When Other Work Must Be Preserved)

When the refactor is interleaved with other changes:

```bash
# Step 1: Reverse git mv operations
git mv src/superclaude/skills/sc-{name}-protocol src/superclaude/skills/sc-{name}

# Step 2: Restore original SKILL.md frontmatter from known-good commit
git checkout {base-commit} -- src/superclaude/skills/sc-{name}/SKILL.md

# Step 3: Remove .claude/ protocol directories
rm -rf .claude/skills/sc-{name}-protocol

# Step 4: Re-sync
make sync-dev
make verify-sync
```

### 7.3 Rollback Verification

```bash
# Confirm old directories restored
ls -d src/superclaude/skills/sc-{name}/

# Confirm no -protocol directories remain
ls -d src/superclaude/skills/sc-*-protocol/ 2>/dev/null
# Expected: no output

# Confirm old name values restored
grep "^name:" src/superclaude/skills/sc-{name}/SKILL.md
```

---

## 8. Skill Directory Structure Requirements

Every skill package must contain at minimum:

| File | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | YES | Main skill definition with YAML frontmatter |
| `__init__.py` | YES | Python package marker (can be empty) |

Optional subdirectories observed:
- `refs/` -- Reference documents (algorithms, integration specs, scoring)
- `rules/` -- Rule definitions (pass definitions, checklists)
- `templates/` -- Output templates (reports, profiles)
- `scripts/` -- Utility scripts (shell scripts for analysis)

**File counts observed** (for estimation):
- Minimal skill: 2 files (SKILL.md + `__init__.py`)
- Small skill: 3 files (+ 1 support file like a YAML spec)
- Medium skill: 6-7 files (+ refs/)
- Large skill: 12 files (+ rules/ + templates/ + scripts/)

---

## 9. Governing Policy Document

All architectural conventions are governed by:
- **File**: `docs/architecture/command-skill-policy.md`
- **Version**: v1.0.0
- This document defines the naming conventions, CI checks, and migration checklists.
- Any v2.01 architectural refactor should reference and comply with this policy.

---

## 10. Dev Copy Sync Workflow

The dual-location architecture (src/ canonical, .claude/ dev copies) requires:

1. ALL edits happen in `src/superclaude/` first.
2. `make sync-dev` copies to `.claude/`.
3. `make verify-sync` confirms parity.
4. The Makefile previously contained a "skill-skip heuristic" that skipped syncing skills matching a command name. This heuristic was REMOVED because the `-protocol` suffix convention eliminates the name collision.

**Heuristic that was removed** (for reference -- do not re-introduce):
```bash
# This skip logic is OBSOLETE and was removed:
cmd_name=${skill_name#sc-};
if [ "$cmd_name" != "$skill_name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    continue;
fi;
```

The `-protocol` suffix on skill directories ensures skill names never collide with command names, making this heuristic unnecessary.
