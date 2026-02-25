# Current State Inventory — SuperClaude Framework

**Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3` (commit `9060a65`)
**Purpose**: Baseline "before" picture for v2.01 architectural refactor

---

## 1. Commands Inventory

### src/superclaude/commands/ (37 commands + README)

| # | Command File | Lines | Over 200? | Has Paired Skill? |
|---|-------------|-------|-----------|-------------------|
| 1 | adversarial.md | 112 | No | Yes (`sc-adversarial-protocol`) |
| 2 | agent.md | 71 | No | No |
| 3 | analyze.md | 97 | No | No |
| 4 | brainstorm.md | 121 | No | No |
| 5 | build.md | 93 | No | No |
| 6 | business-panel.md | 112 | No | No |
| 7 | cleanup-audit.md | 93 | No | Yes (`sc-cleanup-audit-protocol`) |
| 8 | cleanup.md | 111 | No | No |
| 9 | design.md | 95 | No | No |
| 10 | document.md | 87 | No | No |
| 11 | estimate.md | 107 | No | No |
| 12 | explain.md | 91 | No | No |
| 13 | git.md | 79 | No | No |
| 14 | help.md | 148 | No | No |
| 15 | implement.md | 110 | No | No |
| 16 | improve.md | 113 | No | No |
| 17 | index.md | 85 | No | No |
| 18 | index-repo.md | 165 | No | No |
| 19 | load.md | 92 | No | No |
| 20 | **pm.md** | **592** | **YES** | No |
| 21 | **recommend.md** | **1005** | **YES** | No |
| 22 | reflect.md | 88 | No | No |
| 23 | research.md | 122 | No | No |
| 24 | **review-translation.md** | **913** | **YES** | No |
| 25 | roadmap.md | 76 | No | Yes (`sc-roadmap-protocol`) |
| 26 | save.md | 92 | No | No |
| 27 | sc.md | 130 | No | No |
| 28 | select-tool.md | 87 | No | No |
| 29 | spawn.md | 104 | No | No |
| 30 | **spec-panel.md** | **435** | **YES** | No |
| 31 | **task-mcp.md** | **375** | **YES** | No |
| 32 | task.md | 115 | No | Yes (`sc-task-unified-protocol`) |
| 33 | **task-unified.md** | **567** | **YES** | Yes (`sc-task-unified-protocol`) |
| 34 | test.md | 92 | No | No |
| 35 | troubleshoot.md | 119 | No | No |
| 36 | validate-tests.md | 102 | No | Yes (`sc-validate-tests-protocol`) |
| 37 | workflow.md | 117 | No | No |

**Total lines across all commands**: ~6,717
**Commands over 200 lines**: 6 (pm, recommend, review-translation, spec-panel, task-mcp, task-unified)
**README.md**: 22 lines (not a command)

### .claude/commands/sc/ (37 commands)

Identical file list and line counts to `src/superclaude/commands/` (excluding README.md which is src-only). **Commands are in sync.**

---

## 2. Skills Inventory

### src/superclaude/skills/ (6 skill directories)

| # | Skill Directory | File Count | Contents |
|---|----------------|------------|----------|
| 1 | `confidence-check` | 3 | SKILL.md, confidence.ts, __init__.py |
| 2 | `sc-adversarial-protocol` | 6 | SKILL.md, __init__.py, refs/{agent-specs, artifact-templates, debate-protocol, scoring-protocol}.md |
| 3 | `sc-cleanup-audit-protocol` | 12 | SKILL.md, __init__.py, rules/5, scripts/1, templates/4 |
| 4 | `sc-roadmap-protocol` | 7 | SKILL.md, __init__.py, refs/{adversarial-integration, extraction-pipeline, scoring, templates, validation}.md |
| 5 | `sc-task-unified-protocol` | 2 | SKILL.md, __init__.py |
| 6 | `sc-validate-tests-protocol` | 3 | SKILL.md, __init__.py, classification-algorithm.yaml |

### .claude/skills/ (6 skill directories)

| # | Skill Directory | File Count | Sync Status |
|---|----------------|------------|-------------|
| 1 | `confidence-check` | 2 | MISMATCH (src=3, .claude=2) |
| 2 | `sc-adversarial-protocol` | 0 | MISMATCH (src=6, .claude=0) — empty shell dirs only |
| 3 | `sc-cleanup-audit-protocol` | 0 | MISMATCH (src=12, .claude=0) — empty shell dirs only |
| 4 | `sc-roadmap-protocol` | 0 | MISMATCH (src=7, .claude=0) — empty shell dirs only |
| 5 | `sc-task-unified-protocol` | 0 | MISMATCH (src=2, .claude=0) — empty |
| 6 | `sc-validate-tests-protocol` | 0 | MISMATCH (src=3, .claude=0) — empty |

**Skills are NOT in sync.** The `.claude/skills/` directories for the `-protocol` suffixed skills contain only empty subdirectory structures (from git renames that moved files but `make sync-dev` was not run). Only `confidence-check` has any files in `.claude/` (2 of 3).

---

## 3. Agents Inventory

### src/superclaude/agents/ (27 agents + README)

| # | Agent File | Lines | Category |
|---|-----------|-------|----------|
| 1 | audit-analyzer.md | 88 | Audit |
| 2 | audit-comparator.md | 78 | Audit |
| 3 | audit-consolidator.md | 69 | Audit |
| 4 | audit-scanner.md | 93 | Audit |
| 5 | audit-validator.md | 100 | Audit |
| 6 | backend-architect.md | 48 | Technical |
| 7 | business-panel-experts.md | 247 | Business |
| 8 | debate-orchestrator.md | 68 | Orchestration |
| 9 | deep-research-agent.md | 184 | Research |
| 10 | deep-research.md | 31 | Research |
| 11 | devops-architect.md | 48 | Technical |
| 12 | frontend-architect.md | 48 | Technical |
| 13 | learning-guide.md | 48 | Education |
| 14 | merge-executor.md | 60 | Git |
| 15 | performance-engineer.md | 48 | Technical |
| 16 | **pm-agent.md** | **692** | Orchestration |
| 17 | python-expert.md | 48 | Technical |
| 18 | quality-engineer.md | 48 | Technical |
| 19 | refactoring-expert.md | 48 | Technical |
| 20 | repo-index.md | 30 | Utility |
| 21 | requirements-analyst.md | 48 | Business |
| 22 | root-cause-analyst.md | 48 | Analysis |
| 23 | security-engineer.md | 50 | Technical |
| 24 | self-review.md | 33 | Quality |
| 25 | socratic-mentor.md | 291 | Education |
| 26 | system-architect.md | 48 | Technical |
| 27 | technical-writer.md | 48 | Technical |

### .claude/agents/ (27 agents)

Identical file list and line counts to `src/superclaude/agents/` (excluding README.md which is src-only). **Agents are in sync.**

---

## 4. Structural Analysis

### 4.1 Commands with `## Activation` Sections

**Only 1 command**: `roadmap.md`

The Activation section reads:
```
## Activation
Load and execute the full behavioral instructions from `src/superclaude/skills/sc-roadmap/SKILL.md`.
```

Note: This references the **old** skill path (`sc-roadmap/`) not the new renamed path (`sc-roadmap-protocol/`). This is a broken reference after the rename.

### 4.2 Commands Referencing `Skill` in `allowed-tools`

**Zero commands** reference `Skill` in their `allowed-tools` frontmatter. Only `roadmap.md` has the `allowed-tools` field at all, and it lists: `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task`.

### 4.3 Command Frontmatter Patterns

Two distinct frontmatter patterns exist:

**Pattern A (36 commands)** — Standard frontmatter:
```yaml
---
name: <command-name>
description: "<description>"
category: <utility|orchestration|...>
complexity: <basic|enhanced|meta>
mcp-servers: [<server-list>]
---
```

**Pattern B (1 command: `roadmap.md`)** — Minimal with allowed-tools:
```yaml
---
name: sc:roadmap
description: <description>
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

### 4.4 Skill Naming Convention

**Current convention** (post staged rename): `sc-<domain>-protocol`

| Old Name (pre-rename, staged) | New Name (current on disk) |
|-------------------------------|---------------------------|
| `sc-adversarial` | `sc-adversarial-protocol` |
| `sc-cleanup-audit` | `sc-cleanup-audit-protocol` |
| `sc-roadmap` | `sc-roadmap-protocol` |
| `sc-task-unified` | `sc-task-unified-protocol` |
| `sc-validate-tests` | `sc-validate-tests-protocol` |

The `confidence-check` skill does NOT follow the `sc-` prefix convention and has no `-protocol` suffix.

### 4.5 Sync Status Summary

| Component | src/ Count | .claude/ Count | In Sync? |
|-----------|-----------|---------------|----------|
| Commands | 37 | 37 | YES |
| Agents | 27 | 27 | YES |
| Skills | 6 dirs, 33 files | 6 dirs, 2 files | **NO** |

The skill desync is caused by staged git renames (`sc-X` -> `sc-X-protocol`) that moved files in src/ but `.claude/` was not re-synced. The `.claude/skills/` `-protocol` directories contain only empty subdirectory structures.

---

## 5. Command Size Analysis

### Commands Over 200 Lines (Candidates for Extraction)

| Command | Lines | Notes |
|---------|-------|-------|
| `recommend.md` | 1005 | Largest command. Strong extraction candidate. |
| `review-translation.md` | 913 | Second largest. Strong extraction candidate. |
| `pm.md` | 592 | PM agent orchestration. |
| `task-unified.md` | 567 | Unified task system. Has paired skill. |
| `spec-panel.md` | 435 | Spec panel workflow. |
| `task-mcp.md` | 375 | Task with MCP integration. |

### Commands Under 100 Lines

| Command | Lines |
|---------|-------|
| agent.md | 71 |
| git.md | 79 |
| index.md | 85 |
| roadmap.md | 76 |
| document.md | 87 |
| reflect.md | 88 |
| select-tool.md | 87 |
| explain.md | 91 |
| build.md | 93 |
| cleanup-audit.md | 93 |
| load.md | 92 |
| save.md | 92 |
| test.md | 92 |
| design.md | 95 |
| analyze.md | 97 |

---

## 6. Command-Skill Pairings

### Definite Pairings (command name appears in skill name)

| Command | Paired Skill | Skill File Count |
|---------|-------------|-----------------|
| `adversarial.md` | `sc-adversarial-protocol` | 6 |
| `cleanup-audit.md` | `sc-cleanup-audit-protocol` | 12 |
| `roadmap.md` | `sc-roadmap-protocol` | 7 |
| `task.md` / `task-unified.md` | `sc-task-unified-protocol` | 2 |
| `validate-tests.md` | `sc-validate-tests-protocol` | 3 |

### Unpaired Skills

| Skill | No Matching Command |
|-------|-------------------|
| `confidence-check` | No `confidence-check.md` command exists |

### Unpaired Large Commands (no skill, over 200 lines)

| Command | Lines | Extraction Opportunity |
|---------|-------|----------------------|
| `recommend.md` | 1005 | High |
| `review-translation.md` | 913 | High |
| `pm.md` | 592 | Medium |
| `spec-panel.md` | 435 | Medium |
| `task-mcp.md` | 375 | Medium |

---

## 7. Makefile Targets

### All Targets

| Target | Purpose |
|--------|---------|
| `install` | Install package |
| `test` | Run test suite |
| `test-plugin` | Run plugin tests |
| `doctor` | Health check |
| `verify` | Verify installation |
| `lint` | Run ruff linter |
| `format` | Format code |
| `clean` | Remove build artifacts |
| `build-plugin` | Build plugin artefacts to dist/ |
| `sync-plugin-repo` | Sync artefacts to ../SuperClaude_Plugin |
| `translate` | Translation workflow |
| `sync-dev` | Sync src/ to .claude/ for local dev |
| `verify-sync` | Check src/ and .claude/ are in sync |
| `help` | Show target help |
| `uninstall-legacy` | Remove legacy installation |

### Key Observations

- **No `lint-architecture` target exists.** This would need to be created for v2.01.
- **`sync-dev`** exists and handles commands, agents, and skills sync.
- **`verify-sync`** exists for CI-friendly drift detection.
- No target validates command structure (e.g., required sections, line count limits).

---

## 8. Summary of Key Findings for v2.01

### What Exists
- 37 commands, 27 agents, 6 skills
- Commands and agents are synced between src/ and .claude/
- Skills are NOT synced (broken by in-progress rename)
- Only 1 command (`roadmap.md`) has an `## Activation` section
- Only 1 command (`roadmap.md`) uses `allowed-tools` frontmatter
- 6 commands exceed 200 lines (largest: 1005 lines)
- 5 commands have paired skills; 1 skill has no paired command

### What Does NOT Exist Yet
- No `lint-architecture` Makefile target
- No `Skill` tool reference in any command's `allowed-tools`
- No standardized `## Activation` section across commands
- No convention for when a command should delegate to a skill vs inline behavior
- No maximum line count enforcement for commands
- No structural validation for command frontmatter consistency (two incompatible patterns)

### Broken References
- `roadmap.md` Activation section references old path `src/superclaude/skills/sc-roadmap/SKILL.md` (should be `sc-roadmap-protocol/SKILL.md`)
- `.claude/skills/` directories for `-protocol` skills are empty shells (need `make sync-dev`)

### Naming Inconsistencies
- `confidence-check` skill lacks `sc-` prefix and `-protocol` suffix
- Two task-related commands exist: `task.md` (115 lines) and `task-unified.md` (567 lines)
- Two task MCP commands: `task.md` and `task-mcp.md` (375 lines)
- Two research agents: `deep-research.md` (31 lines) and `deep-research-agent.md` (184 lines)
