# SuperClaude — Framework Context

## Python Environment
Use UV for all Python operations. Never use `python -m`, `pip install`, or `python script.py`.
```
uv run pytest                    # run tests
uv run pytest tests/path/ -v     # specific tests
uv pip install package           # install deps
uv run python script.py          # execute scripts
```

## Project Structure
```
src/superclaude/        # Source of truth for all distributable components
  core/                 # This file + framework .md files (RULES, PRINCIPLES, etc.)
  commands/             # Slash command definitions
  skills/               # Skill packages (SKILL.md + refs/ + rules/ + templates/)
  agents/               # Agent definitions
  cli/                  # Python CLI: sprint, roadmap, tasklist, audit, pipeline
  pm_agent/             # confidence.py, self_check.py, reflexion.py
.claude/                # Dev copies — synced from src/, read by Claude Code
  commands/sc/          # Active slash commands
  skills/               # Active skills (loaded on-demand, ~50 tokens each)
  agents/               # Active agents
tests/                  # Python test suite
docs/                   # Documentation (docs/generated/ = CLI pipeline artifacts)
```

## Dev Commands
```
make dev                # Install editable + dev dependencies
make test               # Full test suite
make sync-dev           # src/superclaude/{skills,agents,commands} → .claude/
make verify-sync        # Confirm src/ and .claude/ match (run before committing)
make lint && make format
superclaude sprint run <tasklist-index.md>   # Execute sprint pipeline
superclaude roadmap run <spec.md>            # Generate roadmap pipeline
superclaude roadmap validate <output-dir>    # Validate roadmap artifacts
```

## Component Sync
Source of truth is `src/superclaude/`. Always edit there first, then `make sync-dev`.
If you edited `.claude/` directly: copy changes back to `src/superclaude/`, then `make verify-sync`.

## MCP Servers
| Server         | Primary Use                                  | Flag       |
|----------------|----------------------------------------------|------------|
| auggie         | Codebase search — call before significant edits | (auto)  |
| serena         | Symbol navigation, project memory            | --serena   |
| sequential     | Multi-step reasoning, deep analysis          | --seq      |
| context7       | Official library/framework docs              | --c7       |
| tavily         | Web search, current information              | --tavily   |
| magic          | UI component generation                      | --magic    |
| playwright     | Browser automation, E2E testing              | --play     |

## Personas (auto-activated by context; override with --persona-X)
| Persona      | Domain                         | Primary MCP       |
|--------------|--------------------------------|-------------------|
| architect    | systems design, scalability    | sequential, c7    |
| frontend     | UI/UX, components              | magic, playwright |
| backend      | APIs, reliability              | c7, sequential    |
| security     | vulnerabilities, auth          | sequential        |
| analyzer     | root cause, investigation      | sequential, c7    |
| qa           | testing, coverage              | playwright, seq   |
| refactorer   | cleanup, tech debt             | sequential        |
| devops       | deploy, infrastructure         | sequential        |
| scribe       | docs, localization             | c7, sequential    |

## Core Rules
1. **UV only** — never `python -m` or bare `pip`
2. **Parallel by default** — batch independent tool calls; sequential only for true dependencies
3. **Confidence check** — ≥90% proceed, 70-89% present options, <70% ask before implementing
4. **Git** — feature branches only; never commit directly to master/main
5. **Output paths** — write files next to their source or to the `--output` dir the CLI command specifies; `docs/generated/` is a roadmap pipeline artifact directory, not a general output sink
6. **Component edits** — `src/superclaude/` → `make sync-dev` → `.claude/`; never reverse without syncing back
7. **Finish what you start** — no TODO stubs for core logic; if you begin a feature, complete it to working state
8. **Scope discipline** — build exactly what's asked; no speculative additions
9. **Auggie first** — call `codebase-retrieval` before significant edits to load relevant context
10. **Temporal** — verify current date from env context before any date/version reasoning

## Key Docs
- `PLANNING.md` — architecture decisions, absolute rules
- `TASK.md` — current tasks and priorities
- `KNOWLEDGE.md` — accumulated insights and debugging patterns
- `src/superclaude/core/RULES.md` — full behavioral rules (referenced by skills)
- `src/superclaude/core/PRINCIPLES.md` — engineering principles (referenced by skills)

## Skills & Commands
Skills in `~/.claude/skills/` load on-demand (~50 tokens each at session start).
Commands in `~/.claude/commands/sc/` — use `/sc:help` to list all available.
Agents in `~/.claude/agents/` — delegated by skills and commands.
Full behavioral specs (personas, MCP workflows, wave strategies) live in the skill files.
