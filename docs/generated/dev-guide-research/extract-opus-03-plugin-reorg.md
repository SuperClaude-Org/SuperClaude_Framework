# Extraction: Plugin Re-organization Plan

**Source file**: `/config/workspace/SuperClaude_Framework/docs/plugin-reorg.md`
**Extracted**: 2026-02-21
**Focus**: Developing custom commands, skills, and agents for the SuperClaude framework

---

## 1. Source of Truth Locations

The document defines a canonical source-of-truth table mapping each component type to its current and target location:

| Area | Current Repo | Target Location (Framework) | Notes |
|------|--------------|-----------------------------|-------|
| Agent docs (`agents/*.md`) | `SuperClaude_Plugin/agents/` | `plugins/superclaude/agents/` | "Markdown instructions consumed by `/sc:*` commands." |
| Command definitions (`commands/*.md`) | `SuperClaude_Plugin/commands/` | `plugins/superclaude/commands/` | "YAML frontmatter + markdown bodies." |
| Hook config | `SuperClaude_Plugin/hooks/hooks.json` | `plugins/superclaude/hooks/hooks.json` | "SessionStart automation." |
| Skill source (`skills/confidence-check/`) | "Divergent copies in both repos" | `plugins/superclaude/skills/confidence-check/` | "Replace plugin repo copy with build artefact." Single canonical copy in Framework. |
| Session init scripts | `SuperClaude_Plugin/scripts/*.sh` | `plugins/superclaude/scripts/` | "Executed via Claude Code hooks." |
| Plugin manifest | `SuperClaude_Plugin/.claude-plugin/` (`plugin.json`, `marketplace.json`) | "Generated from `plugins/superclaude/manifest/` templates" | "Manifest fields will be parameterised for official distribution/local builds." |
| Confidence skill tests | `SuperClaude_Plugin/.claude-plugin/tests/` | `plugins/superclaude/tests/` | "Keep with Framework to ensure tests run before packaging." |

Key takeaway: The Framework repository (`SuperClaude_Framework`) is the single canonical source. The Plugin repository (`SuperClaude_Plugin`) receives generated artefacts and should not be edited directly.

---

## 2. Plugin Layout and Directory Structure

The proposed directory structure within `SuperClaude_Framework`:

```
plugins/
  superclaude/
    agents/
    commands/
    hooks/
    scripts/
    skills/
      confidence-check/
        SKILL.md
        confidence.ts
    manifest/
      plugin.template.json
      marketplace.template.json
    tests/
      confidence/
        test_cases.json
        expected_results.json
        run.py
```

### Component Breakdown

- **`agents/`** -- Agent definition files as Markdown (`.md`). These are "Markdown instructions consumed by `/sc:*` commands."
- **`commands/`** -- Command definition files as Markdown (`.md`) with "YAML frontmatter + markdown bodies."
- **`hooks/`** -- Contains `hooks.json` for SessionStart automation.
- **`scripts/`** -- Shell scripts (`.sh`) "Executed via Claude Code hooks."
- **`skills/`** -- Skill packages. Each skill is a subdirectory containing at minimum a `SKILL.md` file plus implementation files (e.g., `confidence.ts`).
- **`manifest/`** -- Template files for plugin distribution manifests (`plugin.template.json`, `marketplace.template.json`). These are rendered at build time with version/author metadata.
- **`tests/`** -- Tests co-located with the Framework so they "run before packaging." Test suites contain `test_cases.json`, `expected_results.json`, and a runner script (`run.py`).

---

## 3. Build Workflow for Skills, Commands, and Agents

Two make targets govern the build and sync pipeline:

### `make build-plugin`

> 1. "Validates skill tests (`uv run` / Node unit tests)."
> 2. "Copies `plugins/superclaude/*` into a fresh `dist/plugins/superclaude/.claude-plugin/...` tree."
> 3. "Renders manifest templates with version/author pulled from `pyproject.toml` / git tags."

This means:
- Tests must pass before any packaging occurs.
- The build output lands in `dist/plugins/superclaude/.claude-plugin/`.
- Manifest templates (`plugin.template.json`, `marketplace.template.json`) are parameterized and rendered with values from `pyproject.toml` and git tags.

### `make sync-plugin-repo`

> 1. "Rsyncs the generated artefacts into `../SuperClaude_Plugin/`."
> 2. "Cleans stale files before copy (to avoid drift)."

This is a one-directional sync from Framework build output to the Plugin repository. Stale files are cleaned first to prevent divergence.

---

## 4. Manifest Templates

Manifests live in `plugins/superclaude/manifest/` as templates:

- **`plugin.template.json`** -- The main plugin descriptor. Fields are parameterized for both official distribution and local builds.
- **`marketplace.template.json`** -- Marketplace listing metadata.

At build time (`make build-plugin`), these templates are rendered with:
- **Version**: pulled from `pyproject.toml`
- **Author/metadata**: pulled from `pyproject.toml` and/or git tags

The rendered output lands in `dist/plugins/superclaude/.claude-plugin/`.

---

## 5. Sync Workflows Between src/ and .claude/

### Current State (v4.2.0 per CLAUDE.md)

The current sync workflow (separate from the plugin reorg plan) uses `src/superclaude/` as the canonical source:

- `src/superclaude/skills/` and `src/superclaude/agents/` are the source of truth.
- `.claude/skills/` and `.claude/agents/` are convenience copies for development.
- `make sync-dev` copies from `src/superclaude/{skills,agents}` to `.claude/`.
- `make verify-sync` confirms both sides match (CI-friendly).

### Future State (Plugin Reorg Plan)

The plugin reorg plan introduces `plugins/superclaude/` as the canonical location for plugin-distributable components. The workflow becomes:

1. Edit files in `plugins/superclaude/{agents,commands,skills,hooks,scripts}/`
2. `make build-plugin` validates tests and assembles into `dist/`
3. `make sync-plugin-repo` pushes artefacts to `../SuperClaude_Plugin/`

The Plugin repository is intended to become a generated output with a "do not edit" banner and optional CI guard.

---

## 6. Key Conventions for Custom Development

### Commands
- Format: Markdown files with **YAML frontmatter** + markdown body
- Location: `plugins/superclaude/commands/`
- Consumed by Claude Code as `/sc:*` slash commands

### Agents
- Format: Markdown files (`.md`)
- Location: `plugins/superclaude/agents/`
- Purpose: "Markdown instructions consumed by `/sc:*` commands"

### Skills
- Format: Directory containing at minimum `SKILL.md` plus implementation files
- Location: `plugins/superclaude/skills/<skill-name>/`
- Example structure:
  ```
  skills/
    confidence-check/
      SKILL.md
      confidence.ts
  ```
- Tests live separately in `plugins/superclaude/tests/`

### Hooks
- Format: JSON configuration (`hooks.json`)
- Location: `plugins/superclaude/hooks/`
- Purpose: SessionStart automation

---

## 7. Pending Work (from Next Steps)

The document lists these incomplete items:

> - [ ] Port existing assets from `SuperClaude_Plugin` into the Framework layout.
> - [ ] Update Framework docs (CLAUDE.md, README) to reference the new build commands.
> - [ ] Strip direct edits in `SuperClaude_Plugin` by adding a readme banner ("generated -- do not edit") and optional CI guard.
> - [ ] Define the roadmap for expanding `/sc:*` commands (identify which legacy flows warrant reintroduction as optional modules).

This indicates the plugin reorg is **planned but not yet implemented**. The current v4.2.0 system uses `src/superclaude/` as the source of truth with `make sync-dev` / `make verify-sync`, while the future system will use `plugins/superclaude/` with `make build-plugin` / `make sync-plugin-repo`.
