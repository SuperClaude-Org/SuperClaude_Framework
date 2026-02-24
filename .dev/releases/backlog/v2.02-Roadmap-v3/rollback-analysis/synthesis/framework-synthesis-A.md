# Framework Changes Synthesis -- v2.01-Roadmap-V3

**Branch**: `feature/v2.01-Roadmap-V3`
**Analysis date**: 2026-02-24
**Baseline commit**: `9060a65`
**Source batches**: 9 analysis files (batch1 through batch9)

---

## 1. Executive Summary

The v2.01-Roadmap-V3 release implements a single architectural transformation across the entire SuperClaude framework: the **command-skill decoupling pattern**. Previously, slash commands (`.claude/commands/sc/*.md` and their `src/superclaude/commands/*.md` source-of-truth copies) contained both interface metadata (flags, usage examples, frontmatter) and full behavioral protocol specifications (algorithms, checklists, MCP routing tables, sub-agent delegation matrices). This release separates the two concerns: commands become thin dispatchers that define syntax and invoke a corresponding protocol skill, while skills (`src/superclaude/skills/sc-*-protocol/`) hold the complete behavioral specification loaded on-demand via the `Skill` tool.

Five skill directories were renamed from `sc-{name}` to `sc-{name}-protocol` (adversarial, cleanup-audit, roadmap, task-unified, validate-tests), affecting 30 files total (5 modified SKILL.md files with frontmatter name updates, 25 pure-rename companion files). Five command files received a new `## Activation` section containing a mandatory `Skill sc:{name}-protocol` invocation directive. The most dramatic change was to `task-unified.md`, which was reduced from 567 lines to 106 lines (81% reduction) as its entire tier classification engine, compliance checklists, MCP integration matrix, and sub-agent delegation tables were extracted to the skill. The other four commands received smaller additions (8-12 lines each) since their protocol content was already primarily in the skill files.

The Makefile received three categories of changes to enforce the new architecture: removal of a skill-skip heuristic from `sync-dev` and `verify-sync` (which previously prevented syncing skills that had matching command files), addition of a new 113-line `lint-architecture` target with 6 validation checks (bidirectional link verification, command size limits, activation section enforcement, frontmatter validation, naming consistency), and help text updates. A new policy document `docs/architecture/command-skill-policy.md` was created to codify the convention.

All changes maintain perfect parity between `.claude/` dev copies and `src/superclaude/` source-of-truth files. Five new `.claude/skills/sc-*-protocol/` directories were created as untracked dev copies (via `make sync-dev`), byte-identical to their `src/` counterparts minus the `__init__.py` Python package markers. The entire change set is tightly coupled: commands reference skills by their new `-protocol` names, the Makefile enforces the naming convention, and partial application of any subset will produce broken references or lint failures.

---

## 2. Change Inventory

### 2.1 Command Files (10 files: 5 in `.claude/commands/sc/`, 5 in `src/superclaude/commands/`)

| File | Change Type | Lines Added | Lines Removed | Net Delta | Key Changes |
|------|------------|-------------|---------------|-----------|-------------|
| `adversarial.md` (x2) | Section insert | +8 | 0 | +8 | New `## Activation` section |
| `cleanup-audit.md` (x2) | Section insert | +8 | 0 | +8 | New `## Activation` section |
| `roadmap.md` (x2) | Frontmatter + section rewrite | +5 | -2 | +3 | `Skill` added to allowed-tools; activation rewritten from file-path to skill invocation |
| `task-unified.md` (x2) | Major rewrite | +24 | -485 | -461 | 81% content extraction to skill; flag table consolidation; heading simplification |
| `validate-tests.md` (x2) | Section insert + path update | +10 | -2 | +8 | New `## Activation` section; See Also paths updated to `-protocol` |

**Note**: Each command file exists in two locations (`.claude/commands/sc/` and `src/superclaude/commands/`). All pairs are byte-identical.

### 2.2 Skill Directory Renames (30 files in `src/superclaude/skills/`)

| Old Directory | New Directory | SKILL.md Change | Companion Files (R100) | Total Files |
|---------------|---------------|-----------------|----------------------|-------------|
| `sc-adversarial/` | `sc-adversarial-protocol/` | Frontmatter `name` only (R099) | 5 | 6 |
| `sc-cleanup-audit/` | `sc-cleanup-audit-protocol/` | Frontmatter `name` + `sc:` prefix fix (R099) | 11 | 12 |
| `sc-roadmap/` | `sc-roadmap-protocol/` | Frontmatter `name`, `+Skill` in allowed-tools, Wave 2 Step 3 expansion (+17 lines) (R081) | 6 | 7 |
| `sc-task-unified/` | `sc-task-unified-protocol/` | Frontmatter `name` only (R099) | 1 | 2 |
| `sc-validate-tests/` | `sc-validate-tests-protocol/` | Frontmatter `name` only (R099) | 2 | 3 |
| **Totals** | | **5 modified** | **25 pure renames** | **30** |

### 2.3 .claude/skills/ Dev Copies (5 new untracked directories)

| Directory | Files | Mirrors | Content Parity |
|-----------|-------|---------|----------------|
| `.claude/skills/sc-adversarial-protocol/` | 5 | `src/superclaude/skills/sc-adversarial-protocol/` | Identical (minus `__init__.py`) |
| `.claude/skills/sc-cleanup-audit-protocol/` | 11 | `src/superclaude/skills/sc-cleanup-audit-protocol/` | Identical (minus `__init__.py`) |
| `.claude/skills/sc-roadmap-protocol/` | 6 | `src/superclaude/skills/sc-roadmap-protocol/` | Identical (minus `__init__.py`) |
| `.claude/skills/sc-task-unified-protocol/` | 1 | `src/superclaude/skills/sc-task-unified-protocol/` | Identical (minus `__init__.py`) |
| `.claude/skills/sc-validate-tests-protocol/` | 2 | `src/superclaude/skills/sc-validate-tests-protocol/` | Identical (minus `__init__.py`) |
| **Total** | **25** | | |

### 2.4 Makefile

| Change | Lines Added | Lines Removed | Description |
|--------|-------------|---------------|-------------|
| `.PHONY` update | 0 (modified) | 0 (modified) | Added `lint-architecture` to phony list |
| `sync-dev` heuristic removal | 0 | -4 | Removed skill-skip logic for command-matching skills |
| `verify-sync` heuristic removal | 0 | -5 | Removed skill-skip logic + skip message |
| `lint-architecture` target | +113 | 0 | New 6-check architecture enforcement target |
| `help` target | +1 | 0 | Added lint-architecture to help text |
| **Total** | **+114** | **-9** | **Net +105** |

### 2.5 New Documentation

| File | Status | Description |
|------|--------|-------------|
| `docs/architecture/command-skill-policy.md` | New (untracked) | Policy document for command/skill separation convention |
| `src/superclaude/ARCHITECTURE.md` | New (untracked) | Architecture overview document |

### 2.6 Grand Total

| Category | Files Changed | Lines Added | Lines Removed |
|----------|--------------|-------------|---------------|
| Command files (.claude/) | 5 | ~55 | ~489 |
| Command files (src/) | 5 | ~55 | ~489 |
| Skill renames (src/) | 30 | ~22 | ~5 |
| .claude/skills/ dev copies | 25 (new) | N/A | N/A |
| Makefile | 1 | ~114 | ~9 |
| Documentation | 2 (new) | N/A | N/A |
| **Total** | **68** | **~246** | **~992** |

---

## 3. Architecture Transformation: Command-Skill Decoupling

### 3.1 Before (v2.0)

```
command.md = syntax + flags + examples + FULL behavioral protocol (inline)
skill/SKILL.md = behavioral protocol (may duplicate command content)
```

Commands acted as monolithic specifications. Claude would read the command file and execute its protocol inline. Skills were loosely referenced or loaded via file-path instructions (e.g., `Load and execute from src/superclaude/skills/sc-roadmap/SKILL.md`).

**Failure mode**: Silent degradation. If the command's behavioral summary was incomplete or outdated relative to the skill, Claude would guess or hallucinate protocol steps.

### 3.2 After (v2.01)

```
command.md = syntax + flags + examples + Activation directive (lightweight)
skill/SKILL.md = FULL behavioral protocol (loaded on-demand via Skill tool)
```

Commands are thin dispatchers. Each command with a corresponding protocol skill contains:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:{name}-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification ({specifics}) is in the protocol skill.
```

**Failure mode**: Hard failure. If the skill is not installed or cannot be found, the `Skill` invocation fails explicitly rather than silently degrading.

### 3.3 Extraction Scale by Command

| Command | Content Extracted | Remaining in Command | Extraction Ratio |
|---------|-------------------|---------------------|-----------------|
| `task-unified` | 461 lines (tier algorithms, checklists, MCP matrix, delegation tables, escape hatches, metrics) | 106 lines (frontmatter, flags, examples, activation, boundaries) | 81% |
| `adversarial` | 0 lines (protocol already in skill) | Full file + 8 new lines | 0% (additive only) |
| `cleanup-audit` | 0 lines (protocol already in skill) | Full file + 8 new lines | 0% (additive only) |
| `roadmap` | 0 lines (protocol already in skill) | Full file + 3 net new lines | 0% (rewrite only) |
| `validate-tests` | 0 lines (already lean) | Full file + 8 new lines | 0% (additive only) |

### 3.4 Benefits

1. **Token efficiency**: `task-unified.md` no longer loads 461 lines of protocol on every invocation
2. **Single source of truth**: Protocol lives exclusively in the skill; no duplication
3. **Independent evolution**: Command interface and skill protocol can be versioned separately
4. **Explicit dependency**: Hard skill invocation replaces implicit behavioral inference
5. **Lint enforcement**: `make lint-architecture` validates the relationship at build time

---

## 4. Rename Convention: `-protocol` Suffix

### 4.1 Directory Naming

**Pattern**: `sc-{name}` --> `sc-{name}-protocol`

| Old Directory Name | New Directory Name |
|--------------------|--------------------|
| `sc-adversarial` | `sc-adversarial-protocol` |
| `sc-cleanup-audit` | `sc-cleanup-audit-protocol` |
| `sc-roadmap` | `sc-roadmap-protocol` |
| `sc-task-unified` | `sc-task-unified-protocol` |
| `sc-validate-tests` | `sc-validate-tests-protocol` |

### 4.2 Frontmatter Name Field

**Pattern**: `sc-{name}` or `{name}` --> `sc:{name}-protocol`

Note the dual transformation:
- Hyphen prefix (`sc-`) becomes colon prefix (`sc:`) in the frontmatter `name` field
- `-protocol` suffix is appended

| Old Frontmatter `name` | New Frontmatter `name` | Notes |
|-------------------------|------------------------|-------|
| `sc:adversarial` | `sc:adversarial-protocol` | Standard transformation |
| `cleanup-audit` | `sc:cleanup-audit-protocol` | Also fixed missing `sc:` prefix |
| `sc:roadmap` | `sc:roadmap-protocol` | Standard transformation |
| `sc-task-unified` | `sc:task-unified-protocol` | Hyphen changed to colon |
| `sc-validate-tests` | `sc:validate-tests-protocol` | Hyphen changed to colon |

### 4.3 Convention Inconsistency (Known)

The directory name uses hyphens (`sc-adversarial-protocol`) while the frontmatter name uses a colon prefix (`sc:adversarial-protocol`). This is intentional -- directories use filesystem-safe hyphens while the `name:` field uses the colon-prefixed invocation syntax that the `Skill` tool resolves.

### 4.4 Purpose of `-protocol` Suffix

The suffix distinguishes skill packages that contain behavioral protocol definitions (loaded by commands via `## Activation`) from other skill types that may exist in the future. It establishes a naming convention enforced by `make lint-architecture` Check 6.

---

## 5. Sync Verification: .claude/ <-> src/ Parity

### 5.1 Command Files

| Command | `.claude/commands/sc/` | `src/superclaude/commands/` | Parity |
|---------|----------------------|-----------------------------|--------|
| `adversarial.md` | Modified | Modified | IDENTICAL |
| `cleanup-audit.md` | Modified | Modified | IDENTICAL |
| `roadmap.md` | Modified | Modified | IDENTICAL |
| `task-unified.md` | Modified | Modified | IDENTICAL |
| `validate-tests.md` | Modified | Modified | IDENTICAL |

### 5.2 Skill Directories

| Skill | `.claude/skills/` | `src/superclaude/skills/` | Parity | Difference |
|-------|-------------------|---------------------------|--------|------------|
| `sc-adversarial-protocol` | 5 files | 6 files | Content IDENTICAL | `__init__.py` only in src/ |
| `sc-cleanup-audit-protocol` | 11 files | 12 files | Content IDENTICAL | `__init__.py` only in src/ |
| `sc-roadmap-protocol` | 6 files | 7 files | Content IDENTICAL | `__init__.py` only in src/ |
| `sc-task-unified-protocol` | 1 file | 2 files | Content IDENTICAL | `__init__.py` only in src/ |
| `sc-validate-tests-protocol` | 2 files | 3 files | Content IDENTICAL | `__init__.py` only in src/ |

The `__init__.py` omission in `.claude/` copies is expected behavior -- `make sync-dev` intentionally excludes Python packaging artifacts.

### 5.3 Allowed-Tools Discrepancy (Potential Issue)

Only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other commands (`adversarial.md`, `cleanup-audit.md`) have `allowed-tools` lists that do NOT include `Skill`, yet their `## Activation` sections invoke the `Skill` tool. If Claude Code enforces the `allowed-tools` whitelist strictly, this is a latent bug.

`task-unified.md` and `validate-tests.md` may or may not have the same issue depending on their frontmatter (needs verification if `allowed-tools` is present and whether `Skill` is listed).

---

## 6. Makefile Changes

### 6.1 Removed: Skill-Skip Heuristic

**Affected targets**: `sync-dev`, `verify-sync`

**Old behavior**: When syncing skills to `.claude/`, if a skill directory name (after stripping the `sc-` prefix) matched an existing command file, the skill was skipped. Example: `sc-adversarial` --> strip `sc-` --> `adversarial` --> `adversarial.md` exists --> skip sync.

**New behavior**: ALL skill directories (including `-protocol` ones) are synced to `.claude/skills/`. The heuristic was removed because under the new model, commands delegate TO skills rather than replacing them.

**Lines removed**: 4 in `sync-dev`, 5 in `verify-sync` (9 total)

### 6.2 Added: `lint-architecture` Target (113 lines)

Six validation checks enforcing the command-skill separation policy:

| Check | What It Validates | Failure Type |
|-------|-------------------|-------------|
| 1. Command -> Skill links | Commands with `## Activation` reference existing skill directories | ERROR |
| 2. Skill -> Command links | `-protocol` skill directories have corresponding command files | ERROR |
| 3. Command size limits | Commands >500 lines = ERROR, >200 lines = WARNING | ERROR/WARNING |
| 4. Activation section | Commands paired with protocol skills have `## Activation` | ERROR |
| 5. Skill frontmatter | All SKILL.md files have `name:`, `description:`, `allowed-tools:` | ERROR |
| 6. Naming consistency | `-protocol` directory SKILL.md `name:` ends in `-protocol` | ERROR |

**Exit behavior**: Any errors --> `exit 1` (CI failure). Warnings only --> `exit 0`. References `docs/architecture/command-skill-policy.md`.

### 6.3 Updated: `.PHONY` and `help`

- `lint-architecture` added to `.PHONY` declaration
- `lint-architecture` added to `help` target under "Component Sync" section

### 6.4 Logical Pipeline

```
sync-dev          -->  verify-sync       -->  lint-architecture
(copy src->.claude)    (diff check)           (policy enforcement)
```

These three targets form a progressive validation pipeline, though there are no Make-level dependency declarations between them.

---

## 7. Breaking Changes

### 7.1 What Breaks if Partially Applied

| Partial Application | What Breaks | Severity |
|---------------------|-------------|----------|
| Commands updated, skills NOT renamed | `Skill sc:*-protocol` invocations fail (skill directories don't exist under new names) | CRITICAL |
| Skills renamed, commands NOT updated | Old commands reference old skill names or use implicit loading; skills exist under new names only | CRITICAL |
| Makefile `lint-architecture` kept, skills NOT renamed | Check 2 and Check 6 fail (expect `-protocol` directories) | HIGH |
| Makefile skip-heuristic removed, skills NOT renamed | `sync-dev` creates redundant `.claude/skills/sc-*` directories alongside commands | MEDIUM |
| `.claude/` updated, `src/` NOT updated | `make verify-sync` fails; source-of-truth diverges | HIGH |
| `src/` updated, `.claude/` NOT updated | Claude Code reads stale skill content; runtime behavior mismatch | HIGH |

### 7.2 Task-Unified Specific Risk

The `task-unified.md` command was reduced from 567 to 106 lines. If the `sc-task-unified-protocol` skill fails to load, the command becomes a syntax reference with NO behavioral guidance -- no tier classification algorithm, no compliance checklists, no MCP routing, no sub-agent delegation. This is the highest-risk individual change.

### 7.3 Allowed-Tools Gap

Commands `adversarial.md` and `cleanup-audit.md` mandate `Skill` invocation in their `## Activation` section but do not list `Skill` in their `allowed-tools` frontmatter. If Claude Code enforces the whitelist, these commands will fail to activate their skills.

---

## 8. Atomic Change Groups

These groups of files MUST be changed together. Changing any file without its group members will produce broken references, sync failures, or lint errors.

### Group A: Per-Command Atomic Unit (repeat for each of 5 commands)

For each command `{name}` in {adversarial, cleanup-audit, roadmap, task-unified, validate-tests}:

| File | Change |
|------|--------|
| `src/superclaude/commands/{name}.md` | Add/rewrite `## Activation` section |
| `.claude/commands/sc/{name}.md` | Identical change (sync copy) |
| `src/superclaude/skills/sc-{name}/` --> `sc-{name}-protocol/` | Directory rename |
| `src/superclaude/skills/sc-{name}-protocol/SKILL.md` | Frontmatter `name` update |
| `.claude/skills/sc-{name}-protocol/` | New dev copy directory |

**Dependency**: The command's `## Activation` section references `sc:{name}-protocol`, which must exist as a skill directory.

### Group B: Makefile Enforcement

| File | Change |
|------|--------|
| `Makefile` (sync-dev heuristic) | Remove skip logic |
| `Makefile` (verify-sync heuristic) | Remove skip logic |
| `Makefile` (lint-architecture) | Add new target |
| `Makefile` (.PHONY, help) | Reference new target |

**Dependency**: `lint-architecture` checks expect `-protocol` skill directories. The heuristic removal expects skills to be synced alongside commands.

### Group C: Cross-Reference Consistency

| File | Change |
|------|--------|
| `src/superclaude/commands/validate-tests.md` | See Also paths updated to `-protocol` |
| `.claude/commands/sc/validate-tests.md` | Same path updates |

**Dependency**: Cross-references must match actual directory names.

### Group D: Roadmap Skill Content Enhancement

| File | Change |
|------|--------|
| `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | Wave 2 Step 3 expansion (+17 lines), `Skill` added to allowed-tools |
| `.claude/skills/sc-roadmap-protocol/SKILL.md` | Identical content |

**Dependency**: The expanded Wave 2 Step 3 references `sc:adversarial-protocol` skill, which must exist. The `Skill` tool in allowed-tools enables this cross-skill invocation.

### Minimum Viable Atomic Set

The absolute minimum set that can be applied without breaking anything is ALL of Group A (for all 5 commands) + Group B + Group C + Group D. In practice, the entire change set is one atomic unit.

---

## 9. Rollback Procedure

### 9.1 Full Rollback (Undo All Changes)

Execute in this order to avoid intermediate broken states:

```bash
# Step 1: Identify the pre-change commit
PRE_COMMIT=$(git log --oneline | grep -m1 "Phase 5 complete" | awk '{print $1}')
# Expected: 5733e32

# Step 2: Rollback command files (src/ is source of truth)
git checkout $PRE_COMMIT -- src/superclaude/commands/adversarial.md
git checkout $PRE_COMMIT -- src/superclaude/commands/cleanup-audit.md
git checkout $PRE_COMMIT -- src/superclaude/commands/roadmap.md
git checkout $PRE_COMMIT -- src/superclaude/commands/task-unified.md
git checkout $PRE_COMMIT -- src/superclaude/commands/validate-tests.md

# Step 3: Rollback skill directory renames
#   Git mv back from -protocol to original names
git mv src/superclaude/skills/sc-adversarial-protocol src/superclaude/skills/sc-adversarial
git mv src/superclaude/skills/sc-cleanup-audit-protocol src/superclaude/skills/sc-cleanup-audit
git mv src/superclaude/skills/sc-roadmap-protocol src/superclaude/skills/sc-roadmap
git mv src/superclaude/skills/sc-task-unified-protocol src/superclaude/skills/sc-task-unified
git mv src/superclaude/skills/sc-validate-tests-protocol src/superclaude/skills/sc-validate-tests

# Step 4: Restore SKILL.md frontmatter name fields
#   For adversarial: sc:adversarial-protocol -> sc:adversarial
#   For cleanup-audit: sc:cleanup-audit-protocol -> cleanup-audit  (note: restores old inconsistency)
#   For roadmap: sc:roadmap-protocol -> sc:roadmap (also remove Skill from allowed-tools, revert Wave 2 Step 3)
#   For task-unified: sc:task-unified-protocol -> sc-task-unified
#   For validate-tests: sc:validate-tests-protocol -> sc-validate-tests
# Easiest approach: checkout SKILL.md from pre-change commit
git checkout $PRE_COMMIT -- src/superclaude/skills/sc-adversarial/SKILL.md
git checkout $PRE_COMMIT -- src/superclaude/skills/sc-cleanup-audit/SKILL.md
git checkout $PRE_COMMIT -- src/superclaude/skills/sc-roadmap/SKILL.md
git checkout $PRE_COMMIT -- src/superclaude/skills/sc-task-unified/SKILL.md
git checkout $PRE_COMMIT -- src/superclaude/skills/sc-validate-tests/SKILL.md

# Step 5: Rollback Makefile
git checkout $PRE_COMMIT -- Makefile

# Step 6: Remove new .claude/skills/ dev copies
rm -rf .claude/skills/sc-adversarial-protocol
rm -rf .claude/skills/sc-cleanup-audit-protocol
rm -rf .claude/skills/sc-roadmap-protocol
rm -rf .claude/skills/sc-task-unified-protocol
rm -rf .claude/skills/sc-validate-tests-protocol

# Step 7: Re-sync .claude/ from restored src/
make sync-dev

# Step 8: Verify
make verify-sync
```

### 9.2 Full Recreation (Reapply All Changes)

If starting from the pre-change state and recreating:

```bash
# Step 1: Rename skill directories
git mv src/superclaude/skills/sc-adversarial src/superclaude/skills/sc-adversarial-protocol
git mv src/superclaude/skills/sc-cleanup-audit src/superclaude/skills/sc-cleanup-audit-protocol
git mv src/superclaude/skills/sc-roadmap src/superclaude/skills/sc-roadmap-protocol
git mv src/superclaude/skills/sc-task-unified src/superclaude/skills/sc-task-unified-protocol
git mv src/superclaude/skills/sc-validate-tests src/superclaude/skills/sc-validate-tests-protocol

# Step 2: Update SKILL.md frontmatter name fields
#   adversarial: name: sc:adversarial -> name: sc:adversarial-protocol
#   cleanup-audit: name: cleanup-audit -> name: sc:cleanup-audit-protocol
#   roadmap: name: sc:roadmap -> name: sc:roadmap-protocol
#     + Add Skill to allowed-tools
#     + Expand Wave 2 Step 3 (see batch5 analysis for exact content)
#   task-unified: name: sc-task-unified -> name: sc:task-unified-protocol
#   validate-tests: name: sc-validate-tests -> name: sc:validate-tests-protocol

# Step 3: Add ## Activation sections to command files (src/)
#   adversarial.md: Insert 8 lines after Options table, before Behavioral Summary
#   cleanup-audit.md: Insert 8 lines after Arguments section, before Behavioral Summary
#   roadmap.md: Add Skill to allowed-tools; rewrite ## Activation from file-path to skill invocation
#   task-unified.md: MAJOR REWRITE - remove 461 lines, add activation + behavioral summary + compact sections
#   validate-tests.md: Insert 8 lines before See Also; update See Also paths

# Step 4: Sync to .claude/
make sync-dev

# Step 5: Update Makefile
#   Remove 4-line skip heuristic from sync-dev target
#   Remove 5-line skip heuristic from verify-sync target
#   Add lint-architecture target (113 lines)
#   Add lint-architecture to .PHONY
#   Add lint-architecture to help target

# Step 6: Verify
make verify-sync
make lint-architecture
```

### 9.3 Rollback Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Partial rollback leaves broken references | HIGH | Use full rollback procedure; verify with `make verify-sync` and `make lint-architecture` |
| Rollback restores old naming inconsistency (`cleanup-audit` without `sc:` prefix) | LOW | Cosmetic; does not affect functionality |
| Rollback re-inflates `task-unified.md` to 567 lines | MEDIUM | Increases context token usage per invocation |
| Rolling back Makefile without skills creates redundant sync | MEDIUM | Restore skip heuristic if reverting to old names |
| Old `.claude/skills/` directories may linger | LOW | Clean up with `rm -rf .claude/skills/sc-{name}` for old non-protocol names |

---

## Appendix A: Complete File Path Reference

### Modified Files (tracked)

```
src/superclaude/commands/adversarial.md
src/superclaude/commands/cleanup-audit.md
src/superclaude/commands/roadmap.md
src/superclaude/commands/task-unified.md
src/superclaude/commands/validate-tests.md
.claude/commands/sc/adversarial.md
.claude/commands/sc/cleanup-audit.md
.claude/commands/sc/roadmap.md
.claude/commands/sc/task-unified.md
.claude/commands/sc/validate-tests.md
Makefile
```

### Renamed Files (tracked, 30 files in src/superclaude/skills/)

```
# sc-adversarial -> sc-adversarial-protocol (6 files)
src/superclaude/skills/sc-adversarial-protocol/SKILL.md          (R099, modified)
src/superclaude/skills/sc-adversarial-protocol/__init__.py        (R100)
src/superclaude/skills/sc-adversarial-protocol/refs/agent-specs.md        (R100)
src/superclaude/skills/sc-adversarial-protocol/refs/artifact-templates.md (R100)
src/superclaude/skills/sc-adversarial-protocol/refs/debate-protocol.md    (R100)
src/superclaude/skills/sc-adversarial-protocol/refs/scoring-protocol.md   (R100)

# sc-cleanup-audit -> sc-cleanup-audit-protocol (12 files)
src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md                          (R099, modified)
src/superclaude/skills/sc-cleanup-audit-protocol/__init__.py                       (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/rules/dynamic-use-checklist.md    (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/rules/pass1-surface-scan.md       (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/rules/pass2-structural-audit.md   (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/rules/pass3-cross-cutting.md      (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/rules/verification-protocol.md    (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/scripts/repo-inventory.sh         (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/templates/batch-report.md         (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/templates/final-report.md         (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/templates/finding-profile.md      (R100)
src/superclaude/skills/sc-cleanup-audit-protocol/templates/pass-summary.md         (R100)

# sc-roadmap -> sc-roadmap-protocol (7 files)
src/superclaude/skills/sc-roadmap-protocol/SKILL.md                      (R081, modified)
src/superclaude/skills/sc-roadmap-protocol/__init__.py                   (R100)
src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md (R100)
src/superclaude/skills/sc-roadmap-protocol/refs/extraction-pipeline.md   (R100)
src/superclaude/skills/sc-roadmap-protocol/refs/scoring.md               (R100)
src/superclaude/skills/sc-roadmap-protocol/refs/templates.md             (R100)
src/superclaude/skills/sc-roadmap-protocol/refs/validation.md            (R100)

# sc-task-unified -> sc-task-unified-protocol (2 files)
src/superclaude/skills/sc-task-unified-protocol/SKILL.md        (R099, modified)
src/superclaude/skills/sc-task-unified-protocol/__init__.py     (R100)

# sc-validate-tests -> sc-validate-tests-protocol (3 files)
src/superclaude/skills/sc-validate-tests-protocol/SKILL.md                    (R099, modified)
src/superclaude/skills/sc-validate-tests-protocol/__init__.py                 (R100)
src/superclaude/skills/sc-validate-tests-protocol/classification-algorithm.yaml (R100)
```

### New Untracked Files (25 files in .claude/skills/)

```
.claude/skills/sc-adversarial-protocol/SKILL.md
.claude/skills/sc-adversarial-protocol/refs/agent-specs.md
.claude/skills/sc-adversarial-protocol/refs/artifact-templates.md
.claude/skills/sc-adversarial-protocol/refs/debate-protocol.md
.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md
.claude/skills/sc-cleanup-audit-protocol/SKILL.md
.claude/skills/sc-cleanup-audit-protocol/rules/dynamic-use-checklist.md
.claude/skills/sc-cleanup-audit-protocol/rules/pass1-surface-scan.md
.claude/skills/sc-cleanup-audit-protocol/rules/pass2-structural-audit.md
.claude/skills/sc-cleanup-audit-protocol/rules/pass3-cross-cutting.md
.claude/skills/sc-cleanup-audit-protocol/rules/verification-protocol.md
.claude/skills/sc-cleanup-audit-protocol/scripts/repo-inventory.sh
.claude/skills/sc-cleanup-audit-protocol/templates/batch-report.md
.claude/skills/sc-cleanup-audit-protocol/templates/final-report.md
.claude/skills/sc-cleanup-audit-protocol/templates/finding-profile.md
.claude/skills/sc-cleanup-audit-protocol/templates/pass-summary.md
.claude/skills/sc-roadmap-protocol/SKILL.md
.claude/skills/sc-roadmap-protocol/refs/adversarial-integration.md
.claude/skills/sc-roadmap-protocol/refs/extraction-pipeline.md
.claude/skills/sc-roadmap-protocol/refs/scoring.md
.claude/skills/sc-roadmap-protocol/refs/templates.md
.claude/skills/sc-roadmap-protocol/refs/validation.md
.claude/skills/sc-task-unified-protocol/SKILL.md
.claude/skills/sc-validate-tests-protocol/SKILL.md
.claude/skills/sc-validate-tests-protocol/classification-algorithm.yaml
```
