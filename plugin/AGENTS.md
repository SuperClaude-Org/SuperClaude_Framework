# Repository Guidelines

## Project Structure & Module Organization
- `src/airiscode/` hosts the Python package; subpackages like `pm_agent/`, `execution/`, and `cli/` drive confidence workflows and the CLI.
- Claude plugin assets land in `pm/`, `research/`, `index/`, plus `commands/` and `hooks/` for session wiring; group new skills under `skills/`.
- Python tests live under `tests/`, mirroring the package layout; stash fixtures beside the suites that rely on them.

## Build, Test & Development Commands
- `make dev` installs editable deps via `uv pip`; pair with `uv venv` when creating a fresh environment.
- `make test` (with optional `ARGS="tests/pm_agent/ -m confidence_check"`) runs pytest, while `make verify` exercises CLI, plugin discovery, and manifest checks.
- `make lint` and `make format` use Ruff for linting and formatting; run them before opening a PR, and call `make doctor` or `make install-plugin-dev` when tweaking Claude integration.

## Coding Style & Naming Conventions
- Python follows Black’s 88-char line width with Ruff enforcing `E`, `F`, `I`, `N`, `W`; prefer fixing violations over adding ignores.
- Use snake_case for modules, functions, and pytest fixtures; keep classes in PascalCase and constants in ALL_CAPS.
- TypeScript files in `pm/`, `research/`, and `index/` favor single quotes, camelCase functions, and explicit exports matching each module’s surface.

## Testing Guidelines
- Pytest auto-discovers `test_*.py` inside `tests/`; align new directories with their source counterparts for predictable imports.
- Annotate suites with existing markers (`confidence_check`, `self_check`, `reflexion`, etc.) so contributors can run targeted subsets.
- Track coverage with `uv run pytest --cov=airiscode`; highlight meaningful deltas in PRs whenever coverage drops.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `security:`) as reflected in recent history.
- PRs should explain workflow impact, list verification commands (`make test`, `make verify`, `make lint`), and link issues or design notes.
- Share CLI transcripts, log snippets, or screenshots whenever Claude-facing behavior changes, and rebase onto `develop` before requesting review.
