# SuperClaude Contributor Knowledge Base

This generated documentation set expands the repository README into a contributor-facing map of the current codebase.

All content in this bundle is grounded in the repository state observed during generation and is intentionally placed under `docs/generated/`.

## Documents in this bundle

- [Repository Overview](./repository-overview.md)
- [Architecture Guide](./architecture-guide.md)
- [Components Guide](./components-guide.md)
- [Contributor Workflow Guide](./contributor-workflow.md)

## Audience

This bundle is for contributors who need to quickly understand:
- what this repository actually contains today
- which paths are source-of-truth versus development mirrors
- how the Python package, CLI, pytest plugin, commands, agents, and skills relate
- how to work safely within the project’s documented workflow

## Fast orientation

### 1. Product shape
SuperClaude Framework is a Python package that ships a Claude Code-oriented framework composed of:
- a CLI (`superclaude`)
- a pytest plugin (`superclaude.pytest_plugin`)
- distributable command, agent, and skill assets
- documentation and research material

### 2. Most important repository rule
For distributable framework components, treat `src/superclaude/` as the source of truth.

The repository’s own instructions describe `.claude/` as development-facing convenience copies used directly by Claude Code during local iteration.

### 3. Best starting path
Recommended reading order:
1. `README.md`
2. `CLAUDE.md`
3. `pyproject.toml`
4. `Makefile`
5. `src/superclaude/cli/main.py`
6. `src/superclaude/pytest_plugin.py`
7. `src/superclaude/pm_agent/`
8. the rest of this generated bundle

## Bundle map

```text
contributor-knowledge-base/
├── README.md
├── repository-overview.md
├── architecture-guide.md
├── components-guide.md
└── contributor-workflow.md
```

## Notes on scope

This bundle does not replace the existing hand-maintained docs in `docs/`, `README.md`, or `CLAUDE.md`.
It is a generated orientation layer intended to help contributors navigate the repository efficiently.
