# Batch 2: Architecture Documentation Analysis

> **Generated**: 2026-02-24
> **Branch**: `feature/v2.01-Roadmap-V3`
> **Purpose**: Rollback-recreation analysis of new dev planning files

---

## File Inventory

| # | File | Status | Lines | Role |
|---|------|--------|-------|------|
| 1 | `docs/architecture/command-skill-policy.md` | NEW | 337 | Architecture policy document |
| 2 | `src/superclaude/ARCHITECTURE.md` | NEW | 337 | Identical copy placed alongside source code |

**Critical finding**: Both files are byte-for-byte identical. They contain the exact same 337-line document. This is either intentional duplication (one for documentation readers, one for developers working in `src/`) or an oversight that should be resolved by making one a symlink or canonical reference to the other.

---

## Content Summary: Command/Skill Architecture Policy (v1.0.0)

### Purpose

This document defines the **tiered loading architecture** that governs how SuperClaude commands and skills relate to each other. It establishes a strict separation of concerns:

- **Commands** (Tier 0): Slim entry points, auto-loaded into context on `/sc:<name>` invocation. Hard-capped at 150 lines.
- **Protocol Skills** (Tier 1): Full behavioral specifications containing the actual execution logic. No size limit.
- **Ref Files** (Tier 2): Step-specific detail documents (algorithms, templates, scoring rubrics) loaded on-demand via `claude -p`.

The core metaphor: "Commands are doors. Skills are rooms. Refs are drawers."

### Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Command != Skill name | Avoids the "skill already running" re-entry block in Claude Code's Skill tool |
| `-protocol` suffix convention | Clear semantic signal for protocol skills, easy to lint |
| `claude -p` for Tier 2 loading | Guaranteed context injection without trust gap |
| 150-line command cap | Commands are auto-loaded; must stay small to preserve context budget |
| 500-line error threshold for command-only files | Catches worst outliers; forces split into command + protocol skill |

### Naming Convention

| Component | Pattern | Example |
|-----------|---------|---------|
| Command | `<name>` | `adversarial` |
| Protocol Skill | `sc:<name>-protocol` | `sc:adversarial-protocol` |
| Skill Directory | `sc-<name>-protocol/` | `sc-adversarial-protocol/` |
| Ref files | descriptive name | `scoring-protocol.md` |
| Standalone Skill | no `sc-` prefix | `confidence-check` |

### Contracts Defined

The document defines three formal contracts:

1. **Command File Contract (Tier 0)**: Template with frontmatter, Usage, Arguments, Examples, Activation section (mandatory if protocol skill exists), Behavioral Summary (max 5 sentences), Boundaries.

2. **Protocol Skill Contract (Tier 1)**: Template with frontmatter (`name`, `description`, `allowed-tools`), Purpose, Triggers, Protocol Steps, Configurable Parameters, Agent Delegation, MCP Integration, Error Handling, Return Contract, Boundaries.

3. **Ref File Contract (Tier 2)**: Self-contained documents with Purpose section, independently useful, one concern per file.

### CI Enforcement (`make lint-architecture`)

Defines 10 automated checks:

| # | Check | Severity |
|---|-------|----------|
| 1 | Bidirectional link cmd -> skill exists | ERROR |
| 2 | Bidirectional link skill -> cmd exists | ERROR |
| 3 | Command >200 lines | WARN |
| 4 | Command >500 lines | ERROR |
| 5 | Inline protocol YAML >20 lines in command with skill | ERROR |
| 6 | Missing `## Activation` when protocol skill directory exists | ERROR |
| 7 | Activation section references wrong skill name | ERROR |
| 8 | Skill frontmatter missing required fields | ERROR |
| 9 | Skill directory/name mismatch on `-protocol` | ERROR |
| 10 | Sync integrity between `src/` and `.claude/` | ERROR |

### Migration Checklist (4 Phases)

**Phase 1 -- Rename Skill Directories**: Rename 5 skill directories to add `-protocol` suffix:
- `sc-adversarial` -> `sc-adversarial-protocol`
- `sc-cleanup-audit` -> `sc-cleanup-audit-protocol`
- `sc-roadmap` -> `sc-roadmap-protocol`
- `sc-task-unified` -> `sc-task-unified-protocol`
- `sc-validate-tests` -> `sc-validate-tests-protocol`

**Phase 2 -- Refactor Command Files**: Trim each of the 5 paired commands to 150 lines, add `## Activation` sections, remove inline protocol YAML.

**Phase 3 -- Update Build System**: Remove skip logic from `sync-dev` Makefile target, add `lint-architecture` target, update `verify-sync`.

**Phase 4 -- Validate**: Run `make sync-dev`, `make verify-sync`, `make lint-architecture`.

### Backlog Items

| Item | Priority |
|------|----------|
| Split `recommend.md` (1005L) | Medium |
| Split `review-translation.md` (913L) | Medium |
| Split `pm.md` (592L) | Medium |
| Split `task-unified.md` command (567L) | Low |
| Split `spec-panel.md` (435L) | Low |
| Split `task-mcp.md` (375L) | Low |
| Design `claude -p` Tier 2 ref loader script | High |
| Cross-skill invocation patterns | High |

---

## Dependencies and Cross-References

### Files This Document Depends On

| Referenced File/Target | Context |
|------------------------|---------|
| `src/superclaude/commands/adversarial.md` | Listed as Tier 0 command example |
| `src/superclaude/commands/cleanup-audit.md` | Listed as Tier 0 command example |
| `src/superclaude/commands/roadmap.md` | Listed as Tier 0 command example |
| `src/superclaude/commands/analyze.md` | Listed as command-only example |
| `src/superclaude/commands/build.md` | Listed as command-only example |
| `src/superclaude/skills/sc-adversarial-protocol/` | Primary example throughout document |
| `src/superclaude/skills/sc-cleanup-audit-protocol/` | Source layout reference |
| `src/superclaude/skills/sc-roadmap-protocol/` | Source layout reference |
| `src/superclaude/skills/sc-task-unified-protocol/` | Source layout reference |
| `src/superclaude/skills/sc-validate-tests-protocol/` | Source layout reference |
| `src/superclaude/skills/confidence-check/` | Standalone skill example |
| `Makefile` | References `sync-dev` (lines 114-117), `verify-sync`, and planned `lint-architecture` targets |

### Files That Should Reference This Document

| Consumer | Why |
|----------|-----|
| `CLAUDE.md` (project root) | Should reference as the authoritative architecture policy |
| `Makefile` | Implements the CI enforcement checks described here |
| All 5 command `.md` files | Must conform to the Tier 0 contract |
| All 5 protocol `SKILL.md` files | Must conform to the Tier 1 contract |
| All ref files under `refs/` directories | Must conform to the Tier 2 contract |

### Relationship to Git Status

The git status shows these renames are **already in progress** on the current branch:

```
RM src/superclaude/skills/sc-adversarial/SKILL.md -> src/superclaude/skills/sc-adversarial-protocol/SKILL.md
RM src/superclaude/skills/sc-cleanup-audit/SKILL.md -> src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md
RM src/superclaude/skills/sc-roadmap/SKILL.md -> src/superclaude/skills/sc-roadmap-protocol/SKILL.md
RM src/superclaude/skills/sc-task-unified/SKILL.md -> src/superclaude/skills/sc-task-unified-protocol/SKILL.md
RM src/superclaude/skills/sc-validate-tests/SKILL.md -> src/superclaude/skills/sc-validate-tests-protocol/SKILL.md
```

This confirms Phase 1 of the migration checklist is already executed. The `RM` (rename with modification) status on several SKILL.md files indicates the files were both renamed and had their content updated (likely the `name` frontmatter field).

The command files are also shown as modified (`M`), indicating Phase 2 (refactor to 150 lines with `## Activation`) is also underway.

---

## Observations for Rollback-Recreation

1. **Duplicate files**: `docs/architecture/command-skill-policy.md` and `src/superclaude/ARCHITECTURE.md` are identical. During recreation, decide whether to keep both or make one the canonical source.

2. **This is the foundational policy document** for the entire v2.01 branch's architecture changes. All skill directory renames, command file trims, and SKILL.md frontmatter updates flow from the decisions recorded here.

3. **The `make lint-architecture` target does not yet exist** in the Makefile (Phase 3 backlog). Recreation should track whether this was implemented before the rollback point.

4. **Two high-priority backlog items** remain unaddressed: the `claude -p` Tier 2 ref loader script and cross-skill invocation patterns. These are blocking items for full Tier 2 functionality.

5. **All decisions dated 2026-02-23**, meaning this policy was authored the day before this analysis. It represents very recent architectural thinking that drove the current branch's changes.
