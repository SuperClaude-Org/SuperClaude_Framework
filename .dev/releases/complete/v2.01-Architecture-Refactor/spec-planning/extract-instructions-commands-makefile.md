# v2.01 Architecture Refactor: Extracted Patterns from Command & Makefile Instructions

**Source files analyzed**:
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/instructions/02-command-updates.md`
- `.dev/releases/backlog/v2.02-Roadmap-v3/rollback-analysis/instructions/03-makefile-updates.md`

**Filter applied**: Only items relevant to systemic architectural refactoring (command structure, activation patterns, Makefile CI, compliance). All v2.02-specific roadmap content excluded.

---

## 1. Activation Section Template (General Pattern for ALL Commands)

Every command that delegates to a protocol skill MUST contain an `## Activation` section with this exact structure:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:<command-name>-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (<parenthetical listing key protocol elements>) is in the protocol skill.
```

**Placement rule**: Insert between the last flags/options/arguments section and `## Behavioral Summary` (or equivalent behavioral section).

**Template variables**:
- `<command-name>` = the command's base name (e.g., `adversarial`, `cleanup-audit`, `task-unified`)
- `<parenthetical listing>` = comma-separated list of the skill's key behavioral components, specific to each command

**Examples of parenthetical listings**:
- adversarial: "5-step pipeline, agent dispatch, scoring algorithms, error handling"
- cleanup-audit: "3-pass audit protocol, subagent dispatch, evidence gates, report templates"
- task-unified: "tier classification algorithm, compliance checklists, MCP integration, sub-agent delegation, verification protocol"
- validate-tests: "classification algorithm, test execution protocol, report generation"

---

## 2. Command Line-Count Constraint

Commands should be **thin dispatchers**, not protocol containers.

| Threshold | Severity | Action |
|-----------|----------|--------|
| >500 lines | ERROR | Must split into command + protocol skill |
| >200 lines | WARNING | Consider splitting into command + protocol skill |
| <200 lines | IDEAL | Thin dispatcher with frontmatter, flags, examples, activation, boundaries |

**Rationale**: Commands define the interface (name, flags, usage, examples, boundaries). Protocol skills contain the behavioral specification (algorithms, checklists, multi-step workflows, YAML specs).

---

## 3. Content Extraction Pattern (task-unified.md as Exemplar)

The task-unified.md rewrite demonstrates the canonical pattern for refactoring bloated commands: **81% content extraction** (567 lines down to 106 lines, -461 lines).

### What a thin command KEEPS:
- YAML frontmatter (unchanged)
- `# Heading` with command name
- `## Purpose` section with dimension table
- `## Usage` line with syntax
- Flag tables (Strategy, Compliance, Execution Control) -- interface definition only
- `## Examples` -- compact inline examples (6 examples in ~14 lines, not verbose)
- `## Activation` -- NEW, mandatory skill delegation
- `## Behavioral Summary` -- NEW, 1-3 sentence behavioral overview
- `## Boundaries` -- collapsed to inline "Will do" / "Will not do" format
- `## Migration` -- 1-line deprecation notice (if applicable)

### What gets EXTRACTED to the protocol skill:
- `## Triggers` section (auto-activation patterns, keyword triggers, context signals)
- `## Behavioral Flow` section
- `## Tiered Compliance Model` (full tier definitions with SMART criteria, checklists)
- `## Auto-Detection Algorithm` (full YAML spec, compound phrase handling)
- `## MCP Integration` (server selection matrix, persona coordination YAML)
- `## Tool Coordination` (tool table, tier-specific tool usage)
- `## Sub-Agent Delegation Matrix`
- `## Escape Hatches`
- `## Success Metrics`
- `## Version History`
- Verbose examples (replaced with compact versions)
- Two-table Boundaries format (replaced with inline)

### Key structural changes in the extraction:
- Separate `### Verification Flags` table merged INTO `### Execution Control Flags` as a single `--verify` row
- Flag table headings simplified (e.g., `### Strategy Flags (Orchestration Dimension)` becomes `### Strategy Flags`)
- Decorative `---` horizontal rules removed
- Two-table Boundaries format collapsed to inline paragraphs

---

## 4. Dual-Location Sync Requirement

**Architecture**: `src/superclaude/commands/` is the source of truth. `.claude/commands/sc/` contains convenience copies that Claude Code reads directly.

**Rule**: Both locations MUST be byte-identical after any edit.

**Sync methods**:
1. Manual copy: `cp src/superclaude/commands/<name>.md .claude/commands/sc/<name>.md`
2. Automated: `make sync-dev` (copies all commands and skills from src/ to .claude/)

**Verification**: `make verify-sync` checks that src/ and .claude/ are in sync. CI-friendly (exits non-zero on drift).

**Applies to**: Commands (`commands/`), skills (`skills/`), and agents (`agents/`).

---

## 5. Complete `lint-architecture` Target Specification (6 Checks)

A new Makefile target that enforces the command/skill architectural policy.

### Check Summary Table

| Check | Name | What it validates | Failure mode |
|-------|------|-------------------|--------------|
| 1 | Command -> Skill links | Commands with `## Activation` that reference `Skill sc:X` have a corresponding `src/superclaude/skills/sc-X/` directory | ERROR |
| 2 | Skill -> Command links | Each `sc-*-protocol/` skill directory has a corresponding `{name}.md` command (after stripping `sc-` prefix and `-protocol` suffix) | ERROR |
| 3 | Command size limits | Commands >500 lines = ERROR; >200 lines = WARNING | ERROR/WARN |
| 4 | Activation section present | Commands that have a matching `-protocol` skill directory must contain `## Activation` | ERROR |
| 5 | Skill frontmatter validation | All SKILL.md files must have `name:`, `description:`, and `allowed-tools:` frontmatter fields | ERROR |
| 6 | Protocol skill naming consistency | `-protocol` skill directories must have a SKILL.md `name:` field ending in `-protocol` | ERROR |

### Exit behavior:
- errors > 0: prints failure message referencing policy doc, exits code 1
- warns > 0, errors = 0: prints warning message, exits code 0
- both 0: prints success message, exits code 0

### Known gaps vs full policy (10 checks):
- **Missing**: Inline Protocol Detection (commands with >20-line YAML code blocks in markdown). Partially covered by Check 3 size limits.
- **Missing**: Activation Reference Correctness (verifying the skill name in `## Activation` matches the expected name derived from the command name). Partially covered by Check 1 + Check 2 together.
- **Delegated**: File sync parity delegated to existing `make verify-sync` target.
- **Combined**: Two separate line-count thresholds (WARN at 200, ERROR at 500) combined into single Check 3 with two branches.

### Makefile integration:
- Added to `.PHONY` declaration (between `verify-sync` and `uninstall-legacy`)
- Added to `help` target under "Component Sync" section
- Inserted after `verify-sync` target, before `help` target

---

## 6. Skill-Skip Heuristic Removal Rationale

### What was removed:
Both `sync-dev` and `verify-sync` targets contained a heuristic that:
1. Stripped the `sc-` prefix from skill directory names
2. Checked if a matching command file existed
3. If so, skipped syncing that skill entirely

### Why it was removed:
Under the old model, `sc-adversarial` would be skipped because `adversarial.md` existed (the command was self-contained). Under the new architecture, **commands delegate TO skills**, so all skills -- including protocol skills that have matching commands -- must be synced to `.claude/skills/`.

### Exact lines removed:
- `sync-dev`: 4 lines (strip prefix, check command exists, continue, fi)
- `verify-sync`: 5 lines (same logic plus a user-facing skip message `"served by /sc:$cmd_name command"`)

### Impact:
Without removal, `make verify-sync` would report protocol skills as "served by" their commands instead of checking them for sync drift. All `-protocol` skills would be missing from `.claude/skills/`.

---

## 7. Command Frontmatter Requirements

### `allowed-tools` must include `Skill`

Every command that has an `## Activation` section invoking a skill MUST include `Skill` in its `allowed-tools` frontmatter list.

**Example**:
```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

**Known inconsistency identified**: The original v2.02 implementation only added `Skill` to `roadmap.md`'s `allowed-tools`. The following commands were missing it:
- `adversarial.md` (uses `mcp-servers` instead of `allowed-tools` -- needs `allowed-tools` added)
- `cleanup-audit.md` (uses `mcp-servers` instead of `allowed-tools` -- needs `allowed-tools` added)
- `task-unified.md` (needs `Skill` appended)
- `validate-tests.md` (needs `Skill` appended)

**Severity**: HIGH -- flagged in both synthesis documents as an architectural inconsistency.

**Note for read-only commands**: `cleanup-audit.md` should use `Read, Glob, Grep, Bash, TodoWrite, Task, Skill` (no Edit/Write since it is read-only).

---

## 8. Reusable Verification Patterns

### 8.1 File parity check (dual-location sync)
```bash
# Verify all command pairs are byte-identical
diff src/superclaude/commands/<name>.md .claude/commands/sc/<name>.md
# Empty output = identical
```

### 8.2 Activation section presence
```bash
# All commands with protocol skills must have ## Activation
grep -l "## Activation" src/superclaude/commands/*.md
```

### 8.3 Skill reference correctness
```bash
# Each command references its protocol skill correctly
grep "sc:<name>-protocol" src/superclaude/commands/<name>.md
```

### 8.4 Frontmatter tool inclusion
```bash
grep "Skill" src/superclaude/commands/<name>.md | head -5
# Should show Skill in allowed-tools frontmatter
```

### 8.5 Line count check
```bash
wc -l src/superclaude/commands/<name>.md
# Should be <200 (ideal) or <500 (maximum)
```

### 8.6 No stale references to old skill names
```bash
# Should return NO matches
grep -n "skills/sc-<old-name>/" src/superclaude/commands/*.md || echo "CLEAN"
```

### 8.7 Full Makefile verification sequence
```bash
make sync-dev           # Sync all components
make verify-sync        # Verify sync parity
make lint-architecture  # Run all 6 architectural checks
make help | grep lint-architecture  # Verify help entry
```

---

## Summary: v2.01 Architectural Principles Extracted

| Principle | Description |
|-----------|-------------|
| **Thin Dispatchers** | Commands are interface definitions (<200 lines ideal, <500 max). Protocol logic lives in skills. |
| **Mandatory Activation** | Every command with a protocol skill must have `## Activation` with `Skill sc:<name>-protocol` invocation. |
| **Bidirectional Links** | Command references skill (via Activation), skill maps back to command (via naming convention). CI enforces both directions. |
| **Dual-Location Sync** | `src/` is source of truth, `.claude/` is convenience copy. Must be byte-identical. |
| **Frontmatter Completeness** | Commands need `Skill` in `allowed-tools`. Skills need `name:`, `description:`, `allowed-tools:` in frontmatter. |
| **No Skip Heuristics** | All skills sync regardless of whether a matching command exists. Commands delegate to skills, not replace them. |
| **CI Enforcement** | `make lint-architecture` runs 6 checks with ERROR/WARN severity. Non-zero exit on errors. |
| **Content Extraction Pattern** | Bloated commands should extract triggers, algorithms, compliance models, MCP integration, delegation matrices, and verbose examples into the protocol skill. |
