# CLAUDE.md

Development guide for SuperClaude v5 (branch `v5`, package `5.0.0a1`, plugin `5.0.0-alpha.1`).

## Python: UV only

All Python operations go through UV. Never use bare `python`, `pip install`, or the
`pytest` console script (it is broken in this venv — always go through `python -m`).

```bash
uv run python -m pytest -q                 # full test suite (257 tests)
uv run python -m pytest tests/unit -v      # one directory
uv run python -m pytest -m confidence_check
uv pip install <package>
uv run python script.py
```

## Repository layout

```
plugins/superclaude/      # PLUGIN SOURCE OF TRUTH
  skills/                 #   confidence-check, spec-panel, socratic, pm-reflexion
  agents/                 #   explore-haiku.md
  hooks/hooks.json        #   5 hooks (see below)
  scripts/                #   session-restore.sh, tab-title.sh, ...
  manifest/               #   plugin.template.json (version comes from VERSION file)
src/superclaude/          # Python package for the wheel
  skills/, agents/        #   mirrored FROM plugins/superclaude (edit the plugin side)
  cli/                    #   superclaude CLI (install, update, doctor, mcp, install-skill)
  pm_agent/               #   confidence.py, self_check.py, reflexion.py, token_budget.py
  pytest_plugin.py        #   fixtures + markers; never writes files by itself
eval/                     # gate-zero A/B eval harness (eval/README.md, eval/preregister.yaml)
dist/                     # built plugin artefacts — output of `make build-plugin`
docs/knowledge/           # community best-practices hub
docs/migration/           # v4 → v5 migration guide
tests/                    # unit/ auto-marked @unit, integration/ auto-marked @integration
```

`plugins/superclaude/` is canonical for skills/agents/hooks. `make build-plugin`
(`scripts/build_superclaude_plugin.py`) reads the repo `VERSION` file (PEP 440,
normalized to semver) and assembles `dist/plugins/superclaude/`.

## What ships in v5

- **4 skills**: confidence-check (+ `confidence.ts`), spec-panel, socratic, pm-reflexion
- **1 agent**: explore-haiku — cheap codebase exploration on Haiku
- **5 hooks** (`plugins/superclaude/hooks/hooks.json`):
  - `session-restore` — SessionStart command script
  - `confidence-gate` — PreToolUse prompt on `Write|Edit`
  - `session-summary`, `reflexion-trigger` — Stop prompts
  - `tab-title` — opt-in via `SUPERCLAUDE_TAB_TITLE=1` (silent no-op otherwise)
- **Eval harness** in `eval/` — A/B against native Claude Code, machine-scored
- **CLI**: `superclaude install [--minimal]`, `update`, `doctor`, `mcp`, `install-skill`, `version`

## The eval gate — rule for adding ANY component

No skill, agent, hook, or command is added on intuition. The bar is: it must beat
*native* Claude Code behavior in an A/B eval. To propose a component:

1. Build a single-component variant: `eval/variants/<comp>/.claude-plugin/plugin.json`
   plus the one skill/agent/hook under test.
2. Run it: `cd eval && uv run sc-eval --trials 5 --k 3` (smoke; real decisions need
   ≥20 tasks per `eval/preregister.yaml`).
3. It survives only if both pre-registered rules in `eval/preregister.yaml` hold:
   disjoint 95% CIs above the native baseline AND no quality-per-token regression.
4. Attach the numbers to the PR. Overlapping CIs are INCONCLUSIVE, not a win.

Never tune `eval/preregister.yaml` to make a candidate pass. `parallel.py` is a
confirmed cut (native subagents cover it; see `confirmed_cuts` in preregister.yaml).

Keep only what models cannot do alone: deterministic enforcement (hooks), external
access (MCP), persistence — plus structured-format content skills that demonstrably
hold up under eval.

## Tests, lint, health

```bash
make test          # uv run python -m pytest
make lint          # ruff check
make format        # ruff format
make doctor        # installation health check
make build-plugin  # build dist/ plugin artefacts
make verify        # package + plugin + health verification
```

Reflexion file persistence is opt-in: set `SUPERCLAUDE_REFLEXION_OUTPUT_DIR` to
enable writes. Default is no file output; `docs/mistakes/` is gitignored. Do not
reintroduce unconditional file writes in the pytest plugin.

## Git workflow

- Active branch: `v5`. Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
- `master` carries v4.3.x, frozen on PyPI (security fixes only).
- Branch from `v5` for v5 work; PRs target `v5`. Do not push to `master`.
- For parallel sessions use `git worktree add ../SuperClaude_Framework-<name> <branch>`.

## MCP servers (optional)

Everything works with zero MCP servers; integrations must degrade gracefully.
`airis-mcp-gateway` and `mindbase` are maintained by Agile Tech Inc. (the v5
author's company) — disclose this wherever they are recommended, and always list
alternatives (e.g. `superclaude mcp --servers context7 tavily` for individual
servers). Never make them a hard dependency.

## Documentation map

- `README.md` — the v5 pitch and component list
- `docs/migration/v4-to-v5.md` — what was removed, why, and how to upgrade
- `docs/knowledge/README.md` — best-practices hub (eval-or-evidence required)
- `docs/rfc/v5-slim-down.md` — upstream RFC draft
- `eval/README.md` — how the gate works
