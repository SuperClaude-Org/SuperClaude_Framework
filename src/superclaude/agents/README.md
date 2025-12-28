# SuperClaude Agents

This directory contains agent definition files for specialized AI agents.

## Available Agents

- **deep-research.md** - Autonomous web research agent
- **repo-index.md** - Repository indexing agent
- **self-review.md** - Code review and quality check agent

## Important

These agents are copies from `plugins/superclaude/agents/` for package distribution.

When updating agents:
1. Edit files in `plugins/superclaude/agents/`
2. Copy changes to `src/superclaude/agents/`
3. Both locations must stay in sync

In v5.0, the plugin system will use `plugins/` directly.
