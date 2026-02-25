# Instruction 02: Command File Updates

**Purpose**: Step-by-step recreation of all 5 command file changes after git rollback.
**Prerequisite**: Instruction 01 (skill directory renames) MUST be completed first. All skill directories must exist under their `-protocol` names before any command edits.
**Scope**: 10 files (5 in `src/superclaude/commands/`, 5 mirrored to `.claude/commands/sc/`)
**Estimated effort**: ~15 minutes

---

## Table of Contents

1. [Prerequisites Check](#1-prerequisites-check)
2. [Command 1: adversarial.md](#2-command-1-adversarialmd)
3. [Command 2: cleanup-audit.md](#3-command-2-cleanup-auditmd)
4. [Command 3: roadmap.md](#4-command-3-roadmapmd)
5. [Command 4: task-unified.md (MAJOR REWRITE)](#5-command-4-task-unifiedmd-major-rewrite)
6. [Command 5: validate-tests.md](#6-command-5-validate-testsmd)
7. [Dual-Location Sync](#7-dual-location-sync)
8. [Bug Fix: Skill in allowed-tools](#8-bug-fix-skill-in-allowed-tools)
9. [Verification](#9-verification)

---

## 1. Prerequisites Check

Before starting, verify that Instruction 01 (skill renames) is complete:

```bash
# All 5 protocol skill directories must exist
ls -d src/superclaude/skills/sc-adversarial-protocol/
ls -d src/superclaude/skills/sc-cleanup-audit-protocol/
ls -d src/superclaude/skills/sc-roadmap-protocol/
ls -d src/superclaude/skills/sc-task-unified-protocol/
ls -d src/superclaude/skills/sc-validate-tests-protocol/

# Old directories must NOT exist
! ls -d src/superclaude/skills/sc-adversarial/ 2>/dev/null
! ls -d src/superclaude/skills/sc-cleanup-audit/ 2>/dev/null
! ls -d src/superclaude/skills/sc-roadmap/ 2>/dev/null
! ls -d src/superclaude/skills/sc-task-unified/ 2>/dev/null
! ls -d src/superclaude/skills/sc-validate-tests/ 2>/dev/null
```

If any check fails, STOP and complete Instruction 01 first.

---

## 2. Command 1: adversarial.md

**File**: `src/superclaude/commands/adversarial.md`
**Change type**: Section insert (+8 lines, 0 removed)
**Insertion point**: After the `## Options` table (after line 49 in the pre-change file), before `## Behavioral Summary`

### 2.1 What to do

Insert the `## Activation` section between the `## Options` table and the `## Behavioral Summary` section.

### 2.2 Locate the insertion point

Find the line that reads:

```
## Behavioral Summary
```

Insert the following block BEFORE that line (with a blank line separator above and below):

### 2.3 EXACT content to insert

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:adversarial-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (5-step pipeline, agent dispatch, scoring algorithms, error handling) is in the protocol skill.

```

### 2.4 Expected result

The file should transition from:

```
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |

## Behavioral Summary
```

To:

```
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:adversarial-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (5-step pipeline, agent dispatch, scoring algorithms, error handling) is in the protocol skill.

## Behavioral Summary
```

### 2.5 No other changes

The rest of the file (frontmatter, usage, options, behavioral summary, examples, boundaries, related commands) remains EXACTLY as-is. No frontmatter modifications.

---

## 3. Command 2: cleanup-audit.md

**File**: `src/superclaude/commands/cleanup-audit.md`
**Change type**: Section insert (+8 lines, 0 removed)
**Insertion point**: After the `### Arguments` section (after line 34 in the pre-change file), before `## Behavioral Summary`

### 3.1 What to do

Insert the `## Activation` section between the `### Arguments` list and the `## Behavioral Summary` section.

### 3.2 Locate the insertion point

Find the line that reads:

```
## Behavioral Summary
```

Insert the following block BEFORE that line:

### 3.3 EXACT content to insert

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:cleanup-audit-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (3-pass audit protocol, subagent dispatch, evidence gates, report templates) is in the protocol skill.

```

### 3.4 Expected result

The file should transition from:

```
- **--focus**: Domain filter for targeted auditing (`infrastructure`, `frontend`, `backend`, `all`)

## Behavioral Summary
```

To:

```
- **--focus**: Domain filter for targeted auditing (`infrastructure`, `frontend`, `backend`, `all`)

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:cleanup-audit-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (3-pass audit protocol, subagent dispatch, evidence gates, report templates) is in the protocol skill.

## Behavioral Summary
```

### 3.5 No other changes

The rest of the file remains EXACTLY as-is. No frontmatter modifications.

---

## 4. Command 3: roadmap.md

**File**: `src/superclaude/commands/roadmap.md`
**Change type**: Frontmatter edit + section rewrite (+5 lines, -2 lines, net +3)

### 4.1 Frontmatter change: Add `Skill` to `allowed-tools`

**FIND** this line in the YAML frontmatter:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**REPLACE WITH**:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

(Appended `, Skill` to the end of the list.)

### 4.2 Flags table restructure

**FIND** the existing flags section. The pre-change file has:

```markdown
## Core Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--depth` | `standard` | Analysis depth: quick, standard, deep |
| `--template` | Auto-detect | Template type: feature, quality, docs, security, performance, migration |
| `--output` | `.dev/releases/current/<spec-name>/` | Output directory |
| `--specs` | - | Comma-separated spec paths for multi-spec consolidation |
| `--multi-roadmap` | `false` | Enable multi-roadmap adversarial generation |
| `--agents` | - | Agent specs for multi-roadmap: `model[:persona[:"instruction"]]` |
| `--interactive` | `false` | User approval at adversarial decision points |
| `--no-validate` | `false` | Skip Wave 4 validation |
| `--compliance` | Auto-detect | Force compliance tier: strict, standard, light |
| `--persona` | Auto-select | Override primary persona |
| `--dry-run` | `false` | Preview structure without writing files |
```

**REPLACE THE ENTIRE FLAGS SECTION WITH**:

```markdown
## Flags

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `<spec-file-path>` | | Yes (single-spec) | - | Path to specification document |
| `--specs` | | Yes (multi-spec) | - | Comma-separated spec file paths (2-10) |
| `--template` | `-t` | No | Auto-detect | Template type: feature, quality, docs, security, performance, migration |
| `--output` | `-o` | No | `.dev/releases/current/<spec-name>/` | Output directory |
| `--depth` | `-d` | No | `standard` | Analysis depth: quick, standard, deep |
| `--multi-roadmap` | | No | `false` | Enable multi-roadmap adversarial generation |
| `--agents` | `-a` | With --multi-roadmap | - | Agent specs: `model[:persona[:"instruction"]]` |
| `--interactive` | `-i` | No | `false` | User approval at adversarial decision points |
| `--validate` | `-v` | No | `true` | Enable multi-agent validation (Wave 4) |
| `--no-validate` | | No | `false` | Skip validation. Sets validation_status: SKIPPED |
| `--compliance` | `-c` | No | Auto-detect | Compliance tier: strict, standard, light |
| `--persona` | `-p` | No | Auto-select | Override primary persona |
| `--dry-run` | | No | `false` | Preview structure without writing files |
```

Note: The heading changed from `## Core Flags` to `## Flags`, and the table gained `Short` and `Required` columns.

### 4.3 Usage section update

**FIND**:

```markdown
## Usage

```
/sc:roadmap <spec-file-path> [options]
/sc:roadmap --specs <spec1.md,spec2.md,...> [options]
```
```

**REPLACE WITH**:

```markdown
## Usage

```
/sc:roadmap <spec-file-path> [options]
/sc:roadmap --specs <spec1.md,spec2.md,...> [options]
/sc:roadmap <spec-file-path> --multi-roadmap --agents <agent-specs> [options]
```
```

(Added the third usage line for multi-roadmap mode.)

### 4.4 Examples section addition

**FIND** the old Activation section (the line immediately after the flags table or usage section). The pre-change file has NO examples section. The post-change file adds examples between `## Flags` and `## Activation`.

**INSERT** the following `## Examples` section AFTER the flags table and BEFORE `## Activation`:

```markdown
## Examples

```bash
# Basic single-spec
/sc:roadmap specs/auth-system.md

# Deep analysis with security template
/sc:roadmap specs/migration-plan.md --template security --depth deep

# Consolidate 3 specs into one roadmap
/sc:roadmap --specs specs/frontend.md,specs/backend.md,specs/security.md

# Generate 3 competing roadmaps (model-only — all use auto-detected persona)
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus,sonnet,gpt52

# Generate with explicit personas
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus:architect,sonnet:security,opus:analyzer

# Mixed: some with persona, some model-only
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus:architect,sonnet,gpt52:security

# Full combined mode with interactive approval
/sc:roadmap --specs specs/v2-prd.md,specs/v2-addendum.md \
  --multi-roadmap --agents opus:architect,sonnet:security --interactive --depth deep

# Custom output directory
/sc:roadmap specs/auth.md --output .dev/releases/current/v2.0-auth/
```
```

### 4.5 Activation section rewrite

**FIND** the old `## Activation` section:

```markdown
## Activation

Load and execute the full behavioral instructions from `src/superclaude/skills/sc-roadmap/SKILL.md`.
```

**REPLACE WITH**:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:roadmap-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (wave-based generation, adversarial integration, validation protocol) is in the protocol skill.
```

### 4.6 Boundaries section rewrite

**FIND** the old `## Boundaries` section:

```markdown
## Boundaries

- Requires specification file input — will not generate from ad-hoc descriptions
- Produces planning artifacts only — does not execute implementation
- Does not trigger downstream commands — user manually proceeds
```

**REPLACE WITH**:

```markdown
## Boundaries

**Will do**: Generate structured roadmaps from spec files; invoke sc:adversarial for multi-spec/multi-roadmap; apply multi-agent validation; create milestone-based roadmaps with dependency graphs and risk registers; persist session state for cross-session resumability.

**Will not do**: Generate tasklists or execution prompts; execute implementation; trigger downstream commands automatically; generate roadmaps without spec input; write outside designated output directories; modify source specifications.
```

### 4.7 Complete target state for roadmap.md

For reference, the COMPLETE final file should be exactly 81 lines. See the current version at `src/superclaude/commands/roadmap.md` for the exact target.

---

## 5. Command 4: task-unified.md (MAJOR REWRITE)

**File**: `src/superclaude/commands/task-unified.md`
**Change type**: 81% content extraction (-461 lines, +24 lines, net -461). From 567 lines to 106 lines.
**This is the highest-risk change in the entire release.**

### 5.1 Overview of what is removed vs kept

**KEPT (in final 106-line file)**:
- YAML frontmatter (lines 1-10) -- UNCHANGED
- `# /sc:task - Unified Task Command` heading
- `## Purpose` section with dimension table -- UNCHANGED
- `## Usage` line -- UNCHANGED
- `### Strategy Flags` table -- UNCHANGED (but heading loses parenthetical)
- `### Compliance Flags` table -- UNCHANGED (but heading loses parenthetical)
- `### Execution Control Flags` table -- MODIFIED (verification flags merged in)
- `## Examples` -- REWRITTEN (6 compact inline examples)
- `## Activation` -- NEW section
- `## Behavioral Summary` -- NEW section
- `## Boundaries` -- REWRITTEN (collapsed from 2 tables to inline)
- `## Migration` -- REWRITTEN (collapsed to 1 line)

**REMOVED (461 lines)**:
- `---` horizontal rules (decorative separators)
- `## Triggers` section (~60 lines): Auto-activation patterns, keyword triggers, context signals
- `## Behavioral Flow` section (~8 lines)
- `## Tiered Compliance Model` section (~200 lines): All 4 tier definitions with SMART criteria, checklists
- `## Auto-Detection Algorithm` section (~80 lines): Full YAML spec, compound phrase handling
- `## MCP Integration` section (~45 lines): Server selection matrix, persona coordination YAML
- `## Tool Coordination` section (~25 lines): Tool table, tier-specific tool usage
- `## Sub-Agent Delegation Matrix` section (~15 lines)
- `## Escape Hatches` section (~20 lines)
- `## Success Metrics` section (~12 lines)
- `## Version History` section (~4 lines)
- Verbose examples (replaced with compact versions)
- Two-table Boundaries format (replaced with inline)

### 5.2 COMPLETE target file content

Replace the ENTIRE contents of `src/superclaude/commands/task-unified.md` with the following (106 lines exactly):

```markdown
---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
version: "2.0.0"
---

# /sc:task - Unified Task Command

## Purpose

A unified command with **orthogonal dimensions** that merges orchestration capabilities with MCP compliance enforcement:

```
/sc:task [operation] --strategy [systematic|agile|enterprise] --compliance [strict|standard|light|exempt]
```

| Dimension | Purpose | Options |
|-----------|---------|---------|
| **Strategy** | HOW to coordinate work | systematic, agile, enterprise, auto |
| **Compliance** | HOW strictly to enforce quality | strict, standard, light, exempt, auto |

**Philosophy**: "Better false positives than false negatives" - when uncertain, escalate to higher compliance tier.

## Usage

```bash
/sc:task [operation] [target] [flags]
```

### Strategy Flags

| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

### Compliance Flags

| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) | Most tasks |

### Execution Control Flags

| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--verify [critical\|standard\|skip\|auto]` | Verification level |
| `--reason "..."` | Required justification for tier override |

## Examples

```bash
# Systematic feature with strict compliance
/sc:task "implement user authentication system" --strategy systematic --compliance strict

# Standard code update (auto-detects STANDARD)
/sc:task "add input validation to user endpoint"

# Quick fix (explicit LIGHT tier)
/sc:task "fix typo in error message" --compliance light

# Exploration (auto-detects EXEMPT)
/sc:task "explain how the auth middleware works"

# Force strict override
/sc:task "update logging format" --force-strict

# Skip compliance (escape hatch)
/sc:task "experimental change" --skip-compliance
```

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:task-unified-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (tier classification algorithm, compliance checklists, MCP integration, sub-agent delegation, verification protocol) is in the protocol skill.

## Behavioral Summary

Analyzes task requirements, auto-classifies compliance tier (STRICT/STANDARD/LIGHT/EXEMPT) using keyword detection and context boosters, displays tier with confidence, then enforces tier-appropriate checklists and verification. STRICT tier spawns verification sub-agents and runs adversarial review. Supports overrides via flags with documented justification.

## Boundaries

**Will:** Classify tasks into compliance tiers, enforce tier-appropriate checklists, spawn verification sub-agents (STRICT), track decisions in memory, coordinate MCP servers, escalate uncertainty to higher tiers, support overrides with justification.

**Will Not:** Modify code without verification (STRICT), skip security checks, execute destructive operations silently, override user tier selection, store sensitive data in memory, bypass MCP circuit breakers.

## Migration

`/sc:task-mcp` is deprecated. Use `/sc:task --compliance [tier]` instead.
```

### 5.3 Key differences from the pre-change file (summary)

| Section | Pre-change | Post-change |
|---------|-----------|-------------|
| Frontmatter | 10 lines, identical | 10 lines, identical |
| Purpose | 12 lines + `---` separator | 12 lines, no separator |
| Triggers | 38 lines | REMOVED |
| Usage | 4 lines | 4 lines, identical |
| Strategy Flags | 8 lines, heading `### Strategy Flags (Orchestration Dimension)` | 8 lines, heading `### Strategy Flags` |
| Compliance Flags | 9 lines, heading `### Compliance Flags (Quality Dimension)` | 9 lines, heading `### Compliance Flags` |
| Execution Control Flags | 7 lines | 8 lines (verification merged in as `--verify` row) |
| Verification Flags | 7 lines (separate table) | REMOVED (merged into Execution Control) |
| Behavioral Flow | 9 lines | REMOVED |
| Tiered Compliance Model | ~200 lines (4 full tier specs with SMART + checklists) | REMOVED |
| Auto-Detection Algorithm | ~80 lines (YAML spec + compound phrases) | REMOVED |
| MCP Integration | ~45 lines (matrix + persona YAML) | REMOVED |
| Tool Coordination | ~25 lines | REMOVED |
| Sub-Agent Delegation Matrix | ~15 lines | REMOVED |
| Examples | ~35 lines (verbose with comments) | ~14 lines (6 compact inline) |
| Escape Hatches | ~20 lines | REMOVED |
| Success Metrics | ~12 lines | REMOVED |
| Activation | N/A | 6 lines (NEW) |
| Behavioral Summary | N/A | 3 lines (NEW) |
| Boundaries | ~30 lines (2 tables: Will/Will Not) | 4 lines (2 inline paragraphs) |
| Migration | ~20 lines (2 examples + deprecation + version history) | 2 lines (1 deprecation line) |

---

## 6. Command 5: validate-tests.md

**File**: `src/superclaude/commands/validate-tests.md`
**Change type**: Section insert + path update (+10 lines, -2 lines, net +8)

### 6.1 Insert `## Activation` section

**Insertion point**: After the `## Report Format` section (after the closing triple-backtick of the report format code block), before `## See Also`.

**FIND**:

```
  ...
```
```

## See Also
```

(The closing of the Report Format code block followed by `## See Also`)

**INSERT the following block between them**:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:validate-tests-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (classification algorithm, test execution protocol, report generation) is in the protocol skill.

```

### 6.2 Update `## See Also` paths

**FIND**:

```markdown
## See Also

- `/sc:task` - Unified task command
- `skills/sc-task-unified/SKILL.md` - Task skill definition
- `skills/sc-validate-tests/SKILL.md` - Full validation skill spec
```

**REPLACE WITH**:

```markdown
## See Also

- `/sc:task` - Unified task command
- `skills/sc-task-unified-protocol/SKILL.md` - Task skill definition
- `skills/sc-validate-tests-protocol/SKILL.md` - Full validation skill spec
```

(Changed `sc-task-unified` to `sc-task-unified-protocol` and `sc-validate-tests` to `sc-validate-tests-protocol`)

### 6.3 KNOWN BUG (not fixed by original implementation)

Line 63 of the post-change file still reads:

```
Reference: `skills/sc-validate-tests/classification-algorithm.yaml`
```

This references the OLD directory name (without `-protocol`). The original implementation missed this update. The executing agent SHOULD also fix this line:

**FIND**:

```
Reference: `skills/sc-validate-tests/classification-algorithm.yaml`
```

**REPLACE WITH**:

```
Reference: `skills/sc-validate-tests-protocol/classification-algorithm.yaml`
```

**NOTE**: This fix was NOT in the original implementation. Including it here as a recommended improvement. If the goal is exact reproduction of the original changes, skip this fix.

---

## 7. Dual-Location Sync

After editing all 5 files in `src/superclaude/commands/`, copy them to `.claude/commands/sc/`:

```bash
# Copy all 5 command files to their .claude/ mirror locations
cp src/superclaude/commands/adversarial.md .claude/commands/sc/adversarial.md
cp src/superclaude/commands/cleanup-audit.md .claude/commands/sc/cleanup-audit.md
cp src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md
cp src/superclaude/commands/task-unified.md .claude/commands/sc/task-unified.md
cp src/superclaude/commands/validate-tests.md .claude/commands/sc/validate-tests.md
```

Alternatively, if `make sync-dev` is functional (requires Makefile changes from Instruction 03), use:

```bash
make sync-dev
```

**IMPORTANT**: Both locations MUST be byte-identical. The `src/` files are the source of truth; `.claude/` files are convenience copies that Claude Code reads directly.

---

## 8. Bug Fix: Skill in allowed-tools

### 8.1 Issue description

The original implementation has an inconsistency: `roadmap.md` added `Skill` to its `allowed-tools` frontmatter, but `adversarial.md` and `cleanup-audit.md` did NOT -- even though all three commands now have `## Activation` sections that invoke the `Skill` tool.

`adversarial.md` and `cleanup-audit.md` use `mcp-servers` instead of `allowed-tools` in their frontmatter. The `task-unified.md` and `validate-tests.md` commands also lack `Skill` in their tool lists.

### 8.2 What to fix (OPTIONAL -- not in original implementation)

If the executing agent wants to fix this inconsistency for consistency with the architecture policy:

**adversarial.md** -- Change frontmatter from:

```yaml
---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---
```

To:

```yaml
---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---
```

**cleanup-audit.md** -- Change frontmatter from:

```yaml
---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
---
```

To:

```yaml
---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
---
```

(Note: cleanup-audit uses Read, Glob, Grep, Bash, TodoWrite, Task -- no Edit/Write since it is read-only. Plus `Skill` for activation.)

**NOTE**: This bug fix was NOT in the original implementation. It is flagged in both synthesis documents (framework-synthesis-A Section 5.3, framework-synthesis-B Section 3.1) as a HIGH severity inconsistency. The executing agent should decide whether to include this fix or reproduce the original implementation exactly.

---

## 9. Verification

After all changes are complete, run these verification commands:

### 9.1 File parity check

```bash
# Verify all 5 command pairs are byte-identical
diff src/superclaude/commands/adversarial.md .claude/commands/sc/adversarial.md
diff src/superclaude/commands/cleanup-audit.md .claude/commands/sc/cleanup-audit.md
diff src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md
diff src/superclaude/commands/task-unified.md .claude/commands/sc/task-unified.md
diff src/superclaude/commands/validate-tests.md .claude/commands/sc/validate-tests.md
```

All 5 diffs should produce NO output (empty = identical).

### 9.2 Activation section presence

```bash
# All 5 commands must have ## Activation
grep -l "## Activation" src/superclaude/commands/adversarial.md \
  src/superclaude/commands/cleanup-audit.md \
  src/superclaude/commands/roadmap.md \
  src/superclaude/commands/task-unified.md \
  src/superclaude/commands/validate-tests.md
```

Expected: all 5 files listed.

### 9.3 Skill references check

```bash
# Each command references its protocol skill correctly
grep "sc:adversarial-protocol" src/superclaude/commands/adversarial.md
grep "sc:cleanup-audit-protocol" src/superclaude/commands/cleanup-audit.md
grep "sc:roadmap-protocol" src/superclaude/commands/roadmap.md
grep "sc:task-unified-protocol" src/superclaude/commands/task-unified.md
grep "sc:validate-tests-protocol" src/superclaude/commands/validate-tests.md
```

All 5 greps should return matches.

### 9.4 Roadmap allowed-tools includes Skill

```bash
grep "Skill" src/superclaude/commands/roadmap.md | head -5
```

Should show `Skill` in the `allowed-tools` frontmatter line.

### 9.5 task-unified.md line count

```bash
wc -l src/superclaude/commands/task-unified.md
```

Expected: approximately 106-107 lines (the most dramatic reduction).

### 9.6 validate-tests.md See Also paths

```bash
grep "protocol" src/superclaude/commands/validate-tests.md
```

Should show `-protocol` in:
- The Activation section (`sc:validate-tests-protocol`)
- The See Also paths (`sc-task-unified-protocol`, `sc-validate-tests-protocol`)

### 9.7 No stale references to old skill names in commands

```bash
# Should return NO matches (no old-style skill references)
grep -n "skills/sc-adversarial/" src/superclaude/commands/*.md || echo "CLEAN"
grep -n "skills/sc-cleanup-audit/" src/superclaude/commands/*.md || echo "CLEAN"
grep -n "skills/sc-roadmap/" src/superclaude/commands/*.md || echo "CLEAN"
grep -n "skills/sc-task-unified/" src/superclaude/commands/*.md || echo "CLEAN"
grep -n "skills/sc-validate-tests/" src/superclaude/commands/*.md || echo "CLEAN"
```

Expected: All return "CLEAN" (no old references). **Exception**: validate-tests.md line 63 (`classification-algorithm.yaml` path) still uses the old name in the original implementation. This is a known bug (see Section 6.3).

---

## Appendix: Execution Order Summary

```
Step 1: Verify prerequisites (Instruction 01 complete)
Step 2: Edit src/superclaude/commands/adversarial.md    (insert ## Activation)
Step 3: Edit src/superclaude/commands/cleanup-audit.md  (insert ## Activation)
Step 4: Edit src/superclaude/commands/roadmap.md        (frontmatter + flags + examples + activation + boundaries rewrite)
Step 5: Edit src/superclaude/commands/task-unified.md   (FULL REWRITE to 106 lines)
Step 6: Edit src/superclaude/commands/validate-tests.md (insert ## Activation + update See Also paths)
Step 7: Copy all 5 files to .claude/commands/sc/
Step 8: (Optional) Fix allowed-tools inconsistency
Step 9: Run verification commands
```

Steps 2-6 can be executed in any order (no inter-dependencies within this set). Step 7 must follow Steps 2-6. Step 9 must be last.
