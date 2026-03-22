# Claude Code Integration Guide

How SuperClaude integrates with Claude Code's native features.

## Overview

SuperClaude enhances Claude Code through **context engineering** — it doesn't replace Claude Code but configures it with specialized commands, agents, modes, and development patterns. This guide explains how SuperClaude maps to Claude Code's native capabilities.

## Integration Points

### 1. Slash Commands (`~/.claude/commands/sc/`)

SuperClaude installs **30 slash commands** to Claude Code's custom commands directory.

**How it works**: Claude Code reads `.md` files from `~/.claude/commands/` and makes them available as `/` commands. SuperClaude installs to the `sc/` subdirectory, namespacing all commands as `/sc:*`.

**Installation**: `superclaude install`

**Key commands**:
| Command | Purpose |
|---------|---------|
| `/sc:pm` | Project management with PM Agent |
| `/sc:research` | Deep research with citations |
| `/sc:implement` | Implementation with confidence checks |
| `/sc:analyze` | Code analysis and quality review |
| `/sc:test` | Test generation and coverage |
| `/sc:troubleshoot` | Debugging with root cause analysis |
| `/sc:design` | Architecture and design patterns |
| `/sc:document` | Documentation generation |

See [Commands Reference](commands.md) for the full list.

### 2. Agents (`~/.claude/agents/`)

SuperClaude installs **20 domain-specialist agents** that Claude Code can invoke.

**How it works**: Claude Code reads agent definitions from `~/.claude/agents/` and makes them available via `@agent-name` syntax.

**Installation**: `superclaude install` (installs both commands and agents)

**Key agents**:
| Agent | Specialization |
|-------|---------------|
| `@pm-agent` | Project management, PDCA cycles, context persistence |
| `@system-architect` | System design, architecture decisions |
| `@frontend-architect` | UI/UX, component design, accessibility |
| `@backend-architect` | APIs, databases, infrastructure |
| `@security-engineer` | Security audit, vulnerability analysis |
| `@deep-research` | Multi-source research with citations |
| `@quality-engineer` | Testing strategy, code quality |
| `@performance-engineer` | Optimization, profiling, benchmarks |
| `@python-expert` | Python-specific best practices |
| `@technical-writer` | Documentation, API docs |

See [Agents Guide](agents.md) for the full list.

### 3. Behavioral Modes (`src/superclaude/modes/`)

7 behavioral modes adapt Claude Code's response patterns:

| Mode | Effect |
|------|--------|
| **Brainstorming** | Divergent thinking, idea generation |
| **Business Panel** | Multi-stakeholder analysis |
| **Deep Research** | Systematic investigation with citations |
| **Introspection** | Self-reflection, meta-analysis |
| **Orchestration** | Multi-agent coordination |
| **Task Management** | PDCA cycles, progress tracking |
| **Token Efficiency** | Minimal token usage, concise responses |

See [Modes Guide](modes.md) for details.

### 4. Skills (`~/.claude/skills/`)

Skills are installable capability packages for Claude Code.

**Installation**: `superclaude install-skill <name>`

**Available skills**:
- `confidence-check` — Pre-implementation confidence assessment (>=90% to proceed)

### 5. Hooks (`src/superclaude/hooks/`)

Claude Code hooks are shell commands that execute in response to events (tool calls, session start/stop, etc.). SuperClaude provides hook definitions that can be configured in `.claude/settings.json`.

**Configuration**: Hooks are defined in `src/superclaude/hooks/hooks.json` and can be enabled via Claude Code's settings.

### 6. Settings (`.claude/settings.json`)

SuperClaude's project-level settings are stored in `.claude/settings.json`. This file configures:
- Permission rules for tools
- Hook definitions
- MCP server references

### 7. MCP Servers

SuperClaude supports **8+ MCP servers** for external tool integration:

| Server | Purpose |
|--------|---------|
| **AIRIS Gateway** | Unified gateway with 60+ tools (recommended) |
| **Tavily** | Web search for deep research |
| **Context7** | Official library documentation |
| **Sequential Thinking** | Multi-step problem solving |
| **Playwright** | Browser automation and E2E testing |
| **Serena** | Semantic code analysis |
| **Magic** | UI component generation |
| **MorphLLM** | Fast Apply for code modifications |

**Installation**: `superclaude mcp` (interactive) or `superclaude mcp --servers tavily context7`

### 8. Pytest Plugin (Auto-loaded)

SuperClaude's pytest plugin is registered via `pyproject.toml` entry points and auto-loads when pytest runs.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Auto-markers**: Tests in `/unit/` get `@pytest.mark.unit`, tests in `/integration/` get `@pytest.mark.integration`

## How SuperClaude Maps to Claude Code Features

| Claude Code Feature | SuperClaude Enhancement |
|--------------------|------------------------|
| Custom slash commands | 30 specialized `/sc:*` commands |
| Custom agents | 20 domain-specialist `@agents` |
| Hooks | Session lifecycle and tool hooks |
| Skills | confidence-check, more planned |
| MCP servers | 8 pre-configured servers + AIRIS gateway |
| Settings | Project-level `.claude/settings.json` |
| Pytest | Auto-loaded plugin with fixtures and markers |

## Gaps & Planned Features

Features planned for future releases:
- **v5.0**: TypeScript plugin system for native Claude Code plugin marketplace
- **IDE integration**: VS Code / JetBrains extensions for SuperClaude features
- **Cross-session memory**: Enhanced persistence via Serena/Mindbase MCP servers
