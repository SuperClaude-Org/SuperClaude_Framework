# Batch 8 - .claude/skills/ Protocol Directories (Part 1 of 2)

**Scope**: Three NEW untracked `.claude/skills/` protocol directories
**Status**: All untracked (`??` in git status)
**Origin**: Dev copies synced from `src/superclaude/skills/` via `make sync-dev`
**Parity**: All three are byte-identical to their `src/` counterparts (excluding `__init__.py`)

---

## Relationship: src/ vs .claude/

Per `CLAUDE.md` project instructions:

- **Source of truth**: `src/superclaude/skills/` is the canonical location
- **Dev copies**: `.claude/skills/` are convenience copies that Claude Code reads directly during development
- **Sync mechanism**: `make sync-dev` copies `src/superclaude/skills/` to `.claude/skills/`
- **Difference**: `src/` directories contain `__init__.py` (Python package marker); `.claude/` copies omit it

These directories were renamed from their non-`-protocol` variants (visible in git status as `R` renames in `src/`), and the `.claude/` copies are new untracked directories reflecting the renamed structure.

---

## 1. `.claude/skills/sc-adversarial-protocol/`

**Git status**: `?? .claude/skills/sc-adversarial-protocol/`
**Mirrors**: `src/superclaude/skills/sc-adversarial-protocol/` (verified identical, excluding `__init__.py`)

### File listing

```
.claude/skills/sc-adversarial-protocol/
  SKILL.md
  refs/
    agent-specs.md
    artifact-templates.md
    debate-protocol.md
    scoring-protocol.md
```

**Total files**: 5

### SKILL.md header (first 20 lines)

```yaml
---
name: sc:adversarial-protocol
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

- **Category**: analysis
- **Complexity**: advanced
- **MCP servers**: sequential, context7, serena
- **Personas**: architect, analyzer, scribe
- **Purpose**: Generic adversarial debate, comparison, and merge pipeline. Accepts multiple artifacts, identifies differences/contradictions, orchestrates structured debate between agents, selects strongest base via hybrid scoring, produces refactoring plan, and executes unified output. Core objective is verifying accuracy and weeding out hallucinations through steelman debate strategy.

---

## 2. `.claude/skills/sc-cleanup-audit-protocol/`

**Git status**: `?? .claude/skills/sc-cleanup-audit-protocol/`
**Mirrors**: `src/superclaude/skills/sc-cleanup-audit-protocol/` (verified identical, excluding `__init__.py`)

### File listing

```
.claude/skills/sc-cleanup-audit-protocol/
  SKILL.md
  rules/
    dynamic-use-checklist.md
    pass1-surface-scan.md
    pass2-structural-audit.md
    pass3-cross-cutting.md
    verification-protocol.md
  scripts/
    repo-inventory.sh
  templates/
    batch-report.md
    final-report.md
    finding-profile.md
    pass-summary.md
```

**Total files**: 11

### SKILL.md header (first 20 lines)

```yaml
---
name: sc:cleanup-audit-protocol
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---
```

- **Category**: utility
- **Complexity**: high
- **MCP servers**: sequential, serena, context7
- **Personas**: analyzer, architect, devops, qa, refactorer
- **Purpose**: Multi-pass read-only repository audit. Triggers include large repos with tech debt, post-migration cleanup, periodic hygiene audits, pre-release cleanup, and new team member onboarding.
- **Structure**: Three subdirectories (rules/, scripts/, templates/) containing pass definitions, shell scripts, and report templates -- the most complex skill in this batch.

---

## 3. `.claude/skills/sc-roadmap-protocol/`

**Git status**: `?? .claude/skills/sc-roadmap-protocol/`
**Mirrors**: `src/superclaude/skills/sc-roadmap-protocol/` (verified identical, excluding `__init__.py`)

### File listing

```
.claude/skills/sc-roadmap-protocol/
  SKILL.md
  refs/
    adversarial-integration.md
    extraction-pipeline.md
    scoring.md
    templates.md
    validation.md
```

**Total files**: 6

### SKILL.md header (first 20 lines)

```yaml
---
name: sc:roadmap-protocol
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---
```

- **Category**: planning
- **Complexity**: advanced
- **MCP servers**: sequential, context7, serena
- **Personas**: architect, scribe, analyzer
- **Version**: 2.0.0
- **Purpose**: Generate deterministic release roadmap packages from specification documents with integrated multi-agent validation. Transforms project requirements, feature descriptions, or PRD files into structured milestone-based roadmaps.

---

## Parity Verification Summary

| Directory | .claude/ files | src/ files | Content match | Notes |
|-----------|---------------|------------|---------------|-------|
| sc-adversarial-protocol | 5 | 5 + `__init__.py` | Identical | `__init__.py` only in src/ |
| sc-cleanup-audit-protocol | 11 | 11 + `__init__.py` | Identical | `__init__.py` only in src/ |
| sc-roadmap-protocol | 6 | 6 + `__init__.py` | Identical | `__init__.py` only in src/ |

All `.md`, `.sh`, and other non-Python content files are byte-identical between `.claude/skills/` and `src/superclaude/skills/`. The only difference is `__init__.py` present in `src/` (Python package marker) and absent in `.claude/` (not needed for Claude Code skill resolution).

---

## Rollback Implications

- **Safe to delete**: These `.claude/skills/` directories are untracked dev copies. Deleting them has zero impact on the source of truth in `src/`.
- **Recreatable**: Running `make sync-dev` regenerates them from `src/superclaude/skills/`.
- **Rename context**: These `-protocol` suffixed directories replace the old non-suffixed names (e.g., `sc-adversarial` became `sc-adversarial-protocol`). The old `.claude/skills/` directories (without `-protocol`) may still exist and should be cleaned up during rollback if present.
