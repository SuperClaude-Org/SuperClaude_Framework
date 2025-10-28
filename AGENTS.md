# Repository Guidelines

## Project Structure & Module Organization
- `src/superclaude/` holds the Python package and pytest plugin entrypoints.
- `tests/` contains Python integration/unit suites; markers map to features in `pyproject.toml`.
- `pm/`, `research/`, and `index/` house TypeScript agents with standalone `package.json`.
- `skills/` holds runtime skills (e.g., `confidence-check`); `commands/` documents scripted Claude commands.
- `docs/` provides reference packs; start with `docs/developer-guide` for workflow expectations.

## Build, Test, and Development Commands
- `make install` installs the framework editable via `uv pip install -e ".[dev]"`.
- `make test` runs `uv run pytest` across `tests/`.
- `make doctor` or `make verify` check CLI wiring and plugin health.
- `make lint` and `make format` delegate to Ruff; run after significant edits.
- TypeScript agents: inside `pm/`, run `npm install` once, then `npm test` or `npm run build`; repeat for `research/` and `index/`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, Black line length 88, Ruff `E,F,I,N,W`; prefer snake_case for modules/functions and PascalCase for classes.
- Keep pytest markers explicit (`@pytest.mark.unit`, etc.) and match file names `test_*.py`.
- TypeScript: rely on project `tsconfig.json`; keep filenames kebab-case and exported classes PascalCase; align with existing PM agent modules.
- Reserve docstrings or inline comments for non-obvious orchestration; let clear naming do the heavy lifting.

## Testing Guidelines
- Default to `make test`; add `uv run pytest -m unit` to scope runs during development.
- When changes touch CLI or plugin startup, extend integration coverage in `tests/test_pytest_plugin.py`.
- Respect coverage focus on `src/superclaude` (`tool.coverage.run`); adjust configuration instead of skipping logic.
- For TypeScript agents, add Jest specs under `__tests__/*.test.ts` and keep coverage thresholds satisfied via `npm run test:coverage`.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `refactor:`) as seen in `git log`; keep present-tense summaries under ~72 chars.
- Group related file updates per commit to simplify bisects and release notes.
- Before opening a PR, run `make lint`, `make format`, and `make test`; include summaries of verification steps in the PR description.
- Reference linked issues (`Closes #123`) and, for agent workflow changes, add brief reproduction notes; screenshots only when docs change.
- Tag reviewers listed in `CODEOWNERS` when touching owned directories.

## Plugin Deployment Tips
- Use `make install-plugin` to mirror the development plugin into `~/.claude/plugins/pm-agent`; prefer `make reinstall-plugin` after local iterations.
- Validate plugin detection with `make test-plugin` before sharing artifact links or release notes.
