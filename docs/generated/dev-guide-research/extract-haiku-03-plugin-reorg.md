<!--
Source file: /config/workspace/SuperClaude_Framework/docs/plugin-reorg.md
Extraction focus: developing custom commands, skills, and agents for the SuperClaude framework.
-->

# Extraction: Plugin re-organization details relevant to custom commands, skills, and agents

## Source of truth + where command/skill/agent assets live

The document defines a “Source of Truth” table mapping *what exists today* vs the *target location (Framework)*.

### Agents

**Exact quote:**

> Agent docs (`agents/*.md`) | `SuperClaude_Plugin/agents/` | `plugins/superclaude/agents/` | Markdown instructions consumed by `/sc:*` commands.

**Implications for developing custom agents:**
- Agent definitions are Markdown files (`agents/*.md`).
- They are intended to live in the framework under:
  - `plugins/superclaude/agents/`
- They are “consumed by `/sc:*` commands” (i.e., the slash-command system uses these Markdown instructions).

### Commands

**Exact quote:**

> Command definitions (`commands/*.md`) | `SuperClaude_Plugin/commands/` | `plugins/superclaude/commands/` | YAML frontmatter + markdown bodies.

**Implications for developing custom commands:**
- Command definitions are Markdown files (`commands/*.md`).
- Format expectation: **“YAML frontmatter + markdown bodies.”**
- They are intended to live in the framework under:
  - `plugins/superclaude/commands/`

### Skills

**Exact quote:**

> Skill source (`skills/confidence-check/`) | Divergent copies in both repos | **Single canonical copy in Framework** under `plugins/superclaude/skills/confidence-check/` | Replace plugin repo copy with build artefact.

**Implications for developing custom skills:**
- Skill source should have a *single canonical copy* in the framework.
- Example skill path provided:
  - `plugins/superclaude/skills/confidence-check/`
- Guidance: the plugin repo copy should be replaced with a generated build artefact (avoid divergent edits in two repos).

## Proposed Framework layout for plugin assets (commands, skills, agents)

The doc proposes a concrete directory tree inside `SuperClaude_Framework`.

**Exact quote (code block):**

```text
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

### Agents directory
- `plugins/superclaude/agents/`

### Commands directory
- `plugins/superclaude/commands/`

### Skills directory structure + contents
- `plugins/superclaude/skills/`
- Example skill package:
  - `plugins/superclaude/skills/confidence-check/`
    - `SKILL.md`
    - `confidence.ts`

## Build workflow relevant to command/skill/agent development

The build workflow describes how plugin assets (including commands/skills/agents in `plugins/superclaude/*`) should be validated and packaged.

### `make build-plugin` (new target)

**Exact quote:**

> 1. `make build-plugin` (new target):
>    - Validates skill tests (`uv run` / Node unit tests).
>    - Copies `plugins/superclaude/*` into a fresh `dist/plugins/superclaude/.claude-plugin/…` tree.
>    - Renders manifest templates with version/author pulled from `pyproject.toml` / git tags.

**What this means for skills/commands/agents:**
- There is an explicit validation step for **skill tests**.
- All plugin assets under `plugins/superclaude/*` (which includes `agents/`, `commands/`, `skills/`) are copied into a distribution directory:
  - `dist/plugins/superclaude/.claude-plugin/...`
- Manifests are rendered during build, pulling version/author from `pyproject.toml` and/or git tags.

### `make sync-plugin-repo`

**Exact quote:**

> 2. `make sync-plugin-repo`:
>    - Rsyncs the generated artefacts into `../SuperClaude_Plugin/`.
>    - Cleans stale files before copy (to avoid drift).

**What this means for developing custom commands/skills/agents:**
- The plugin repo (`../SuperClaude_Plugin/`) should receive **generated artefacts** rather than being directly edited.
- Stale-file cleanup before copy is explicitly called out “to avoid drift.”

## Guidance against direct edits in plugin repo (keeps development canonical)

The “Next Steps” section includes a specific guardrail relevant to command/skill/agent development practices.

**Exact quote:**

> - [ ] Strip direct edits in `SuperClaude_Plugin` by adding a readme banner (“generated – do not edit”) and optional CI guard.

**Implication:**
- Developers should treat `SuperClaude_Plugin` as build output, not a primary editing location.

## Notes on command expansion (roadmap)

While not implementation details, the doc mentions a forward-looking step for developing/expanding `/sc:*` commands.

**Exact quote:**

> - [ ] Define the roadmap for expanding `/sc:*` commands (identify which legacy flows warrant reintroduction as optional modules).
