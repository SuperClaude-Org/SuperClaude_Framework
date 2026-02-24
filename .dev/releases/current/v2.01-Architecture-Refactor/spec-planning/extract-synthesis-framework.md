# v2.01 Architecture Refactor -- Synthesis Extraction (Framework)

**Source**: `framework-synthesis-A.md` + `framework-synthesis-B.md` (v2.02 rollback analysis)
**Filter**: v2.01-relevant items only (systemic architectural patterns, NOT roadmap-sprint-specific work)
**Extraction date**: 2026-02-24

---

## 1. Command-Skill Decoupling Architecture

The core v2.01 transformation. Separates concerns between command files and skill packages.

### Before (v2.0)

```
command.md = syntax + flags + examples + FULL behavioral protocol (inline)
skill/SKILL.md = behavioral protocol (may duplicate command content)
```

Commands acted as monolithic specifications. Skills were loosely referenced or loaded via file-path instructions (e.g., `Load and execute from src/superclaude/skills/sc-roadmap/SKILL.md`).

**Failure mode**: Silent degradation. If the command's behavioral summary was incomplete or outdated relative to the skill, Claude would guess or hallucinate protocol steps.

### After (v2.01)

```
command.md = syntax + flags + examples + Activation directive (lightweight)
skill/SKILL.md = FULL behavioral protocol (loaded on-demand via Skill tool)
```

Commands are thin dispatchers. Each command with a corresponding protocol skill contains a mandatory `## Activation` section.

**Failure mode**: Hard failure. If the skill is not installed or cannot be found, the `Skill` invocation fails explicitly rather than silently degrading.

### Benefits

1. **Token efficiency**: `task-unified.md` no longer loads 461 lines of protocol on every invocation
2. **Single source of truth**: Protocol lives exclusively in the skill; no duplication
3. **Independent evolution**: Command interface and skill protocol can be versioned separately
4. **Explicit dependency**: Hard skill invocation replaces implicit behavioral inference
5. **Lint enforcement**: `make lint-architecture` validates the relationship at build time

### Extraction Scale (Reference)

| Command | Content Extracted | Remaining in Command | Extraction Ratio |
|---------|-------------------|---------------------|-----------------|
| `task-unified` | 461 lines (tier algorithms, checklists, MCP matrix, delegation tables, escape hatches, metrics) | 106 lines (frontmatter, flags, examples, activation, boundaries) | 81% |
| `adversarial` | 0 lines (protocol already in skill) | Full file + 8 new lines | 0% (additive only) |
| `cleanup-audit` | 0 lines (protocol already in skill) | Full file + 8 new lines | 0% (additive only) |
| `roadmap` | 0 lines (protocol already in skill) | Full file + 3 net new lines | 0% (rewrite only) |
| `validate-tests` | 0 lines (already lean) | Full file + 8 new lines | 0% (additive only) |

---

## 2. `-protocol` Naming Convention

### Directory Naming

**Pattern**: `sc-{name}` --> `sc-{name}-protocol`

Applied to all 5 skill directories: adversarial, cleanup-audit, roadmap, task-unified, validate-tests.

### Frontmatter Name Field

**Pattern**: `sc-{name}` or `{name}` --> `sc:{name}-protocol`

Dual transformation:
- Hyphen prefix (`sc-`) becomes colon prefix (`sc:`) in the frontmatter `name` field
- `-protocol` suffix is appended

| Old Frontmatter `name` | New Frontmatter `name` | Notes |
|-------------------------|------------------------|-------|
| `sc:adversarial` | `sc:adversarial-protocol` | Standard transformation |
| `cleanup-audit` | `sc:cleanup-audit-protocol` | Also fixed missing `sc:` prefix |
| `sc:roadmap` | `sc:roadmap-protocol` | Standard transformation |
| `sc-task-unified` | `sc:task-unified-protocol` | Hyphen changed to colon |
| `sc-validate-tests` | `sc:validate-tests-protocol` | Hyphen changed to colon |

### Convention: Directory vs Frontmatter Names

Directory names use hyphens (`sc-adversarial-protocol`) while frontmatter `name:` values use colons (`sc:adversarial-protocol`). This is intentional -- directories cannot contain colons. The `name:` field uses the colon-prefixed invocation syntax that the `Skill` tool resolves.

### Purpose of `-protocol` Suffix

Distinguishes skill packages that contain behavioral protocol definitions (loaded by commands via `## Activation`) from other skill types that may exist in the future. Enforced by `make lint-architecture` Check 6.

### Pre-Existing Naming Inconsistencies Fixed

The rename fixed pre-existing naming inconsistencies where some skills used the `sc:` prefix and others did not (cleanup-audit was `cleanup-audit`, task-unified was `sc-task-unified` with hyphen instead of colon). Rolling back restores these inconsistencies.

---

## 3. `## Activation` Section Pattern

All 5 commands use the same template structure:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:{name}-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification ({description}) is in the protocol skill.
```

The `{description}` parenthetical is customized per command. Template application is consistent.

### Insertion Points by Command

| Command | Insert Location |
|---------|-----------------|
| `adversarial.md` | After Options table, before Behavioral Summary |
| `cleanup-audit.md` | After Arguments section, before Behavioral Summary |
| `roadmap.md` | Rewrite existing Activation from file-path to skill invocation |
| `task-unified.md` | After Usage section (part of major 81% rewrite) |
| `validate-tests.md` | Before See Also section |

---

## 4. 3-Tier Loading Model

```
commands (syntax/flags/activation)
  --> skills (SKILL.md = full behavioral protocol)
    --> refs/ rules/ templates/ scripts/ (companion files loaded on-demand by skill)
```

### Layer Details

- **Commands** (`src/superclaude/commands/*.md` --> `.claude/commands/sc/*.md`): Thin dispatchers with frontmatter, flags, examples, and mandatory `## Activation` section.
- **Skills** (`src/superclaude/skills/sc-*-protocol/SKILL.md` --> `.claude/skills/sc-*-protocol/SKILL.md`): Full behavioral protocol specification with frontmatter (name, description, allowed-tools).
- **Refs/Rules/Templates/Scripts** (subdirectories of skill packages): Companion files loaded on-demand by the skill protocol. Examples: `refs/agent-specs.md`, `rules/pass1-surface-scan.md`, `templates/batch-report.md`, `scripts/repo-inventory.sh`.

---

## 5. Makefile `lint-architecture` Target

113 lines, 6 validation checks enforcing the command-skill separation policy:

| Check | What It Validates | Failure Type |
|-------|-------------------|-------------|
| 1. Command -> Skill links | Commands with `## Activation` reference existing skill directories | ERROR |
| 2. Skill -> Command links | `-protocol` skill directories have corresponding command files | ERROR |
| 3. Command size limits | Commands >500 lines = ERROR, >200 lines = WARNING | ERROR/WARNING |
| 4. Activation section | Commands paired with protocol skills have `## Activation` | ERROR |
| 5. Skill frontmatter | All SKILL.md files have `name:`, `description:`, `allowed-tools:` | ERROR |
| 6. Naming consistency | `-protocol` directory SKILL.md `name:` ends in `-protocol` | ERROR |

**Exit behavior**: Any errors --> `exit 1` (CI failure). Warnings only --> `exit 0`. References `docs/architecture/command-skill-policy.md`.

---

## 6. `sync-dev` / `verify-sync` Changes

### Removed: Skill-Skip Heuristic

**Affected targets**: `sync-dev`, `verify-sync`

**Old behavior**: When syncing skills to `.claude/`, if a skill directory name (after stripping the `sc-` prefix) matched an existing command file, the skill was skipped. Example: `sc-adversarial` --> strip `sc-` --> `adversarial` --> `adversarial.md` exists --> skip sync.

**New behavior**: ALL skill directories (including `-protocol` ones) are synced to `.claude/skills/`. The heuristic was removed because under the new model, commands delegate TO skills rather than replacing them.

**Lines removed**: 4 in `sync-dev`, 5 in `verify-sync` (9 total)

### Logical Pipeline

```
sync-dev          -->  verify-sync       -->  lint-architecture
(copy src->.claude)    (diff check)           (policy enforcement)
```

These three targets form a progressive validation pipeline, though there are no Make-level dependency declarations between them.

---

## 7. Systemic Bugs

### 7.1 CRITICAL: `allowed-tools` Inconsistency (Missing `Skill` Tool)

**Severity**: HIGH -- Potential functional break
**Affected Files**: `adversarial.md`, `cleanup-audit.md`, `task-unified.md`, `validate-tests.md` (both `.claude/` and `src/` copies)

All 5 commands now include a mandatory `## Activation` section that invokes `> Skill sc:{name}-protocol`. However, only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other 4 commands did NOT.

| Command | `allowed-tools` Includes `Skill` | Has `## Activation` with Skill Invocation |
|---------|-----------------------------------|-------------------------------------------|
| `adversarial.md` | NO | YES |
| `cleanup-audit.md` | NO | YES |
| `roadmap.md` | YES | YES |
| `task-unified.md` | NO | YES |
| `validate-tests.md` | NO | YES |

**Risk**: If Claude Code enforces the `allowed-tools` whitelist strictly, 4 of 5 commands will fail when attempting to invoke their protocol skill.

**Mitigating factors**:
1. Some commands use `mcp-servers` instead of `allowed-tools` in their frontmatter, so this field may not apply.
2. The `Skill` tool may bypass the `allowed-tools` gate entirely (treated as a meta-tool).

**Recommendation**: Add `Skill` to `allowed-tools` in all 4 affected command files for consistency.

### 7.2 MEDIUM: Roadmap SKILL.md Stale Internal Path

**Affected File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Wave 0 step 5 still references `src/superclaude/skills/sc-adversarial/SKILL.md` (old path without `-protocol` suffix). Missed update during the rename.

### 7.3 LOW: Pre-Existing Naming Inconsistencies

The rename fixed naming inconsistencies that existed before v2.01. Rolling back restores the inconsistencies. This is informational only.

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

### Minimum Viable Atomic Set

The absolute minimum set that can be applied without breaking anything is ALL of Group A (for all 5 commands) + Group B + Group C. In practice, the entire change set is one atomic unit.

---

## 9. Recreation Dependency DAG

```
Layer 0 (Foundation - No Dependencies):
  docs/architecture/command-skill-policy.md        [policy document]

Layer 1 (Skill Renames - Independent of Each Other):
  src/superclaude/skills/sc-adversarial-protocol/   [rename + frontmatter]
  src/superclaude/skills/sc-cleanup-audit-protocol/  [rename + frontmatter]
  src/superclaude/skills/sc-roadmap-protocol/        [rename + frontmatter + content]
  src/superclaude/skills/sc-task-unified-protocol/   [rename + frontmatter]
  src/superclaude/skills/sc-validate-tests-protocol/ [rename + frontmatter]

Layer 2 (Command Updates - Depend on Layer 1):
  src/superclaude/commands/adversarial.md           [depends on sc-adversarial-protocol]
  src/superclaude/commands/cleanup-audit.md         [depends on sc-cleanup-audit-protocol]
  src/superclaude/commands/roadmap.md               [depends on sc-roadmap-protocol]
  src/superclaude/commands/task-unified.md          [depends on sc-task-unified-protocol]
  src/superclaude/commands/validate-tests.md        [depends on sc-validate-tests-protocol + sc-task-unified-protocol]

Layer 3 (Dev Copies - Depend on Layer 1 + Layer 2):
  .claude/commands/sc/{all 5 commands}              [mirror of Layer 2]
  .claude/skills/sc-{all 5}-protocol/               [mirror of Layer 1]
  (via `make sync-dev`)

Layer 4 (Build System - Depends on Layer 1 naming convention):
  Makefile: sync-dev heuristic removal              [depends on Layer 1 naming]
  Makefile: verify-sync heuristic removal           [depends on Layer 1 naming]
  Makefile: lint-architecture target                 [depends on Layer 1 + Layer 2 conventions]
```

### Critical Ordering Constraints

1. **Skill renames BEFORE command updates**: Commands reference `sc:X-protocol` skills. Skills must exist under new names first.
2. **Both `src/` and `.claude/` in sync**: After editing `src/`, run `make sync-dev` before testing.
3. **Makefile heuristic removal AFTER skill renames**: The old heuristic won't trigger for `-protocol` names anyway, but removing it before the renames would cause existing skills to be synced redundantly.
4. **`lint-architecture` AFTER everything else**: This is a validation target that checks all the conventions are met.

### Circular Dependencies

None detected. The dependency graph is a clean DAG.

---

## 10. Test Coverage Gaps

### Framework Changes with No Automated Tests

| Change | Test Coverage | Gap Severity |
|--------|---------------|--------------|
| **Command-skill activation flow** | NONE -- no test verifies that `> Skill sc:X-protocol` actually loads the skill | HIGH |
| **`allowed-tools` enforcement** | NONE -- no test verifies the tool whitelist is respected | HIGH |
| **task-unified.md content extraction** | NONE -- no test verifies the 106-line command still produces correct behavior | HIGH |
| **Skill directory renames** | PARTIAL -- `make lint-architecture` validates naming, but no runtime test | MEDIUM |
| **Makefile `sync-dev` behavior change** | PARTIAL -- `make verify-sync` checks parity, but does not regression-test the removed heuristic | MEDIUM |
| **`lint-architecture` target correctness** | NONE -- no test verifies the 6 checks produce correct pass/fail results | MEDIUM |
| **`.claude/skills/` parity** | COVERED -- `make verify-sync` validates these | LOW |

### Recommended Test Additions

1. **Integration test**: Invoke each command and verify the skill activation directive causes the correct skill to be loaded.
2. **Regression test**: Verify `task-unified` command still performs tier classification correctly after content extraction.
3. **Makefile test**: Run `make lint-architecture` against the current tree and verify it passes (exit 0).
4. **Negative test**: Verify `make lint-architecture` fails when a skill is missing or a command lacks `## Activation`.
5. **allowed-tools test**: Verify that the `Skill` tool works for commands where it is not in `allowed-tools` (to confirm whether this is a real bug or a non-issue).

---

## 11. Minimum Viable Recreation Set

The smallest set of changes to achieve a working command-skill decoupling system:

### Phase 1: Core Renames (5 operations)

```bash
git mv src/superclaude/skills/sc-adversarial src/superclaude/skills/sc-adversarial-protocol
git mv src/superclaude/skills/sc-cleanup-audit src/superclaude/skills/sc-cleanup-audit-protocol
git mv src/superclaude/skills/sc-roadmap src/superclaude/skills/sc-roadmap-protocol
git mv src/superclaude/skills/sc-task-unified src/superclaude/skills/sc-task-unified-protocol
git mv src/superclaude/skills/sc-validate-tests src/superclaude/skills/sc-validate-tests-protocol
```

### Phase 2: Frontmatter Updates (5 edits)

Update `name:` field in each SKILL.md:
- `sc:adversarial` -> `sc:adversarial-protocol`
- `cleanup-audit` -> `sc:cleanup-audit-protocol`
- `sc:roadmap` -> `sc:roadmap-protocol`
- `sc-task-unified` -> `sc:task-unified-protocol`
- `sc-validate-tests` -> `sc:validate-tests-protocol`

### Phase 3: Command Activation Sections (5 edits)

Add `## Activation` section to each command in `src/superclaude/commands/`:
- `adversarial.md`: Insert after Options table
- `cleanup-audit.md`: Insert after Arguments section
- `roadmap.md`: Rewrite existing Activation section
- `task-unified.md`: Insert after Usage section (minimal -- keep existing content for now)
- `validate-tests.md`: Insert before See Also

### Phase 4: Sync (1 command)

```bash
make sync-dev
```

### What MVR SKIPS (can be added later)

- task-unified.md content extraction (the 461-line reduction)
- Makefile `lint-architecture` target
- Makefile sync heuristic removal
- `allowed-tools` updates
- validate-tests.md See Also path updates
- Policy document creation

**MVR achieves**: Working skill invocation from all 5 commands. The system functions but task-unified.md remains bloated and the build-system validation is absent.

---

## 12. Partial Application Risk Matrix

| Partial Application | What Breaks | Severity |
|---------------------|-------------|----------|
| Commands updated, skills NOT renamed | `Skill sc:*-protocol` invocations fail (skill directories don't exist under new names) | CRITICAL |
| Skills renamed, commands NOT updated | Old commands reference old skill names or use implicit loading; skills exist under new names only | CRITICAL |
| Makefile `lint-architecture` kept, skills NOT renamed | Check 2 and Check 6 fail (expect `-protocol` directories) | HIGH |
| Makefile skip-heuristic removed, skills NOT renamed | `sync-dev` creates redundant `.claude/skills/sc-*` directories alongside commands | MEDIUM |
| `.claude/` updated, `src/` NOT updated | `make verify-sync` fails; source-of-truth diverges | HIGH |
| `src/` updated, `.claude/` NOT updated | Claude Code reads stale skill content; runtime behavior mismatch | HIGH |

---

## 13. Grand Totals

| Category | Files Changed | Lines Added | Lines Removed |
|----------|--------------|-------------|---------------|
| Command files (.claude/) | 5 | ~55 | ~489 |
| Command files (src/) | 5 | ~55 | ~489 |
| Skill renames (src/) | 30 | ~22 | ~5 |
| .claude/skills/ dev copies | 25 (new) | N/A | N/A |
| Makefile | 1 | ~114 | ~9 |
| Documentation | 2 (new) | N/A | N/A |
| **Total** | **~68** | **~246** | **~992** |

---

## Items Excluded (v2.02 scope)

The following items from the synthesis files were excluded as v2.02-specific:
- Roadmap SKILL.md Wave 2 Step 3 expansion (+17 lines for multi-roadmap protocol with `sc:adversarial-protocol` cross-invocation) -- this is roadmap-sprint-specific behavioral content, not architectural pattern.
- Group D atomic change group (roadmap skill content enhancement) -- behavioral content, not architectural.
