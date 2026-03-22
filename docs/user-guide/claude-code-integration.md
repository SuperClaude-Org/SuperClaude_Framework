# Claude Code Integration Guide

How SuperClaude integrates with — and extends — Claude Code's native features.

## Overview

SuperClaude enhances Claude Code through **context engineering**. It doesn't replace Claude Code — it configures and extends it with specialized commands, agents, modes, and development patterns through Claude Code's native extension points.

This guide maps every SuperClaude feature to its Claude Code integration point, and identifies gaps where SuperClaude could better leverage Claude Code's capabilities.

---

## Integration Points

### 1. Slash Commands → Claude Code Custom Commands

**Claude Code native**: Reads `.md` files from `~/.claude/commands/` and makes them available as `/` commands. Supports YAML frontmatter, argument substitution (`$ARGUMENTS`, `$0`, `$1`), dynamic context injection (`` !`command` ``), and subagent execution (`context: fork`).

**SuperClaude provides**: 30 slash commands installed to `~/.claude/commands/sc/`, namespaced as `/sc:*`.

| Category | Commands |
|----------|----------|
| **Planning & Design** | `/sc:pm`, `/sc:brainstorm`, `/sc:design`, `/sc:estimate`, `/sc:spec-panel` |
| **Development** | `/sc:implement`, `/sc:build`, `/sc:improve`, `/sc:cleanup`, `/sc:explain` |
| **Testing & Quality** | `/sc:test`, `/sc:analyze`, `/sc:troubleshoot`, `/sc:reflect` |
| **Documentation** | `/sc:document`, `/sc:help` |
| **Version Control** | `/sc:git` |
| **Research** | `/sc:research`, `/sc:business-panel` |
| **Project Management** | `/sc:task`, `/sc:workflow` |
| **Utilities** | `/sc:agent`, `/sc:index-repo`, `/sc:recommend`, `/sc:select-tool`, `/sc:spawn`, `/sc:load`, `/sc:save` |

**Installation**: `superclaude install`

### 2. Agents → Claude Code Custom Subagents

**Claude Code native**: Supports custom subagent definitions in `~/.claude/agents/` (user) and `.claude/agents/` (project). Agents have YAML frontmatter with `model`, `allowed-tools`, `effort`, `context`, and `hooks` fields. Invocable via `@agent-name` syntax. 6 built-in subagents: Explore, Plan, General-purpose, Bash, statusline-setup, Claude Code Guide.

**SuperClaude provides**: 20 domain-specialist agents installed to `~/.claude/agents/`.

| Agent | Specialization |
|-------|---------------|
| `@pm-agent` | Project management, PDCA cycles, context persistence |
| `@system-architect` | System design, architecture decisions |
| `@frontend-architect` | UI/UX, component design, accessibility |
| `@backend-architect` | APIs, databases, infrastructure |
| `@security-engineer` | Security audit, vulnerability analysis |
| `@deep-research` | Multi-source research with citations |
| `@deep-research-agent` | Alternative research agent |
| `@quality-engineer` | Testing strategy, code quality |
| `@performance-engineer` | Optimization, profiling, benchmarks |
| `@python-expert` | Python-specific best practices |
| `@technical-writer` | Documentation, API docs |
| `@devops-architect` | CI/CD, deployment, infrastructure |
| `@refactoring-expert` | Code refactoring patterns |
| `@requirements-analyst` | Requirements engineering |
| `@root-cause-analyst` | Root cause analysis |
| `@socratic-mentor` | Teaching through questions |
| `@learning-guide` | Learning path guidance |
| `@self-review` | Code self-review |
| `@repo-index` | Repository indexing |
| `@business-panel-experts` | Business stakeholder analysis |

**Installation**: `superclaude install` (installs both commands and agents)

### 3. Behavioral Modes

**Claude Code native**: Supports permission modes (`default`, `plan`, `acceptEdits`, `bypassPermissions`), effort levels (`low`, `medium`, `high`, `max`), and extended thinking. No direct "behavioral mode" concept — SuperClaude adds this through context injection.

**SuperClaude provides**: 7 behavioral modes that adapt Claude's response patterns:

| Mode | Effect | Claude Code Mapping |
|------|--------|-------------------|
| **Brainstorming** | Divergent thinking, idea generation | Context injection via command |
| **Business Panel** | Multi-stakeholder analysis | Multi-agent orchestration |
| **Deep Research** | Systematic investigation with citations | Extended thinking + research agent |
| **Introspection** | Self-reflection, meta-analysis | Extended thinking context |
| **Orchestration** | Multi-agent coordination | Subagent delegation |
| **Task Management** | PDCA cycles, progress tracking | TodoWrite + session persistence |
| **Token Efficiency** | Minimal token usage, concise responses | Effort level adjustment |

### 4. Skills → Claude Code Skills System

**Claude Code native**: Full skills system with YAML frontmatter (`name`, `description`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`), argument substitution, dynamic context injection, subagent execution, and auto-discovery in `.claude/skills/` directories. Skills can be user-invocable or auto-triggered.

**SuperClaude provides**: 1 skill currently (`confidence-check`). This is a significant gap — many SuperClaude commands could be reimplemented as proper Claude Code skills for better integration.

**Installation**: `superclaude install-skill <name>`

### 5. Hooks → Claude Code Hooks System

**Claude Code native**: 28 hook event types with 4 handler types (command, HTTP, prompt, agent). Events include `SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `TaskCompleted`, `WorktreeCreate`, and more. Hooks are configured in `settings.json` under the `hooks` key.

**SuperClaude provides**: Hook definitions in `src/superclaude/hooks/hooks.json`. Currently limited — does not leverage many available hook events.

**Gap**: SuperClaude could use hooks for:
- `SessionStart` — Auto-restore PM Agent context
- `PostToolUse` — Self-check validation after edits
- `Stop` — Session summary and next-actions persistence
- `TaskCompleted` — Reflexion pattern trigger
- `SubagentStop` — Quality gate checks

### 6. Settings → Claude Code Settings System

**Claude Code native**: 5 settings scopes (managed, CLI flags, local project, shared project, user). Supports permissions (`allow`/`ask`/`deny`), tool-specific rules with wildcards (`Bash(npm *)`, `Edit(/path/**)`), sandbox configuration, model overrides, auto-memory, and MCP server management.

**SuperClaude provides**: Project-level `.claude/settings.json` with basic permission rules.

**Gap**: Could provide recommended settings profiles for different workflows (e.g., strict security mode, autonomous development mode, research mode).

### 7. MCP Servers → Claude Code MCP Integration

**Claude Code native**: Supports stdio and SSE transports, OAuth authentication, 3 configuration scopes (local, project, user), tool search, channel push notifications, and elicitation (interactive input). 60+ servers in the official registry.

**SuperClaude provides**: 8 pre-configured servers + AIRIS Gateway:

| Server | Purpose | Transport |
|--------|---------|-----------|
| **AIRIS Gateway** | Unified gateway with 60+ tools | SSE |
| **Tavily** | Web search for deep research | stdio |
| **Context7** | Official library documentation | stdio |
| **Sequential Thinking** | Multi-step problem solving | stdio |
| **Playwright** | Browser automation and E2E testing | stdio |
| **Serena** | Semantic code analysis | stdio |
| **Magic** | UI component generation | stdio |
| **MorphLLM** | Fast Apply for code modifications | stdio |

**Installation**: `superclaude mcp` (interactive) or `superclaude mcp --servers tavily context7`

### 8. Pytest Plugin (Auto-loaded)

**Claude Code native**: No built-in test framework — relies on tool use (`Bash`) to run tests.

**SuperClaude adds**: Auto-loaded pytest plugin registered via `pyproject.toml` entry point.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Auto-markers**: Tests in `/unit/` → `@pytest.mark.unit`, `/integration/` → `@pytest.mark.integration`

**Custom markers**: `confidence_check`, `self_check`, `reflexion`, `complexity`

---

## Feature Mapping: Claude Code ↔ SuperClaude

| Claude Code Feature | SuperClaude Enhancement | Gap? |
|--------------------|------------------------|------|
| 60+ built-in `/` commands | 30 custom `/sc:*` commands | Complementary |
| 6 built-in subagents | 20 domain-specialist `@agents` | Complementary |
| Skills system (YAML + MD) | 1 skill (confidence-check) | **Large gap** — should convert commands to skills |
| 28 hook events | Basic hook definitions | **Large gap** — most events unused |
| 5 settings scopes | 1 project scope used | **Medium gap** — no recommended profiles |
| Permission modes (4) | Not leveraged | **Gap** — could provide mode presets |
| Extended thinking | Deep Research mode uses it | Partial |
| Agent teams (preview) | Orchestration mode | Partial alignment |
| Voice dictation (20 langs) | Not leveraged | Not applicable |
| Desktop app features | Not leveraged | Not applicable (CLI-focused) |
| Plan mode | Not leveraged | **Gap** — could integrate with confidence checks |
| Session persistence | PM Agent memory files | Partial — could use native sessions |
| `/compact` context mgmt | Token Efficiency mode | Partial alignment |
| MCP 60+ registry servers | 8 pre-configured + gateway | Partial |
| Worktree isolation | Documented in CLAUDE.md | Documented |
| `--effort` levels | Token Efficiency mode | Partial alignment |
| `/batch` parallel changes | Parallel execution engine | Complementary |
| Fast mode | Not leveraged | Not applicable |

---

## Key Gaps to Address

### High Priority

1. **Skills Migration**: Convert key `/sc:*` commands into proper Claude Code skills with YAML frontmatter. This enables auto-triggering, tool restrictions, effort overrides, and better IDE integration.

2. **Hooks Integration**: Leverage Claude Code's 28 hook events for:
   - `SessionStart` → PM Agent context restoration
   - `Stop` → Session summary persistence
   - `PostToolUse` → Self-check after edits
   - `TaskCompleted` → Reflexion pattern

3. **Plan Mode Integration**: Connect confidence checks with Claude Code's native plan mode — block implementation when confidence < 70%.

### Medium Priority

4. **Settings Profiles**: Provide recommended `.claude/settings.json` profiles for different workflows (strict security, autonomous dev, research).

5. **Native Session Persistence**: Use Claude Code's `--continue` / `--resume` instead of custom memory files for PM Agent context.

6. **Permission Presets**: Pre-configured permission rules for SuperClaude's common workflows.

### Future (v5.0+)

7. **TypeScript Plugin System**: Native Claude Code plugin marketplace distribution.
8. **IDE Extensions**: VS Code / JetBrains integration for SuperClaude features.
9. **Agent Teams**: Align Orchestration mode with Claude Code's agent teams feature.

---

## Claude Code Native Features Reference

For developers working on SuperClaude, these are the key Claude Code capabilities to be aware of:

| Feature | Documentation |
|---------|--------------|
| Custom commands | `~/.claude/commands/*.md` with YAML frontmatter |
| Custom agents | `~/.claude/agents/*.md` with model/tools/effort config |
| Skills | `~/.claude/skills/` with auto-discovery and argument substitution |
| Hooks | 28 events in `settings.json` → command/HTTP/prompt/agent handlers |
| Settings | 5 scopes: managed > CLI > local > shared > user |
| Permissions | `Bash(pattern)`, `Edit(path)`, `mcp__server__tool` rules |
| MCP | stdio/SSE transports, OAuth, 3 scopes, elicitation |
| Subagents | `Agent` tool with model/tools/isolation/background options |
| Plan mode | Read-only exploration, visual plan markdown |
| Extended thinking | `--effort max`, `Alt+T` toggle, `MAX_THINKING_TOKENS` |
| Voice | 20 languages, push-to-talk, `/voice` command |
| Session mgmt | Named sessions, resume, fork, 7-day persistence |
| Context | `/context` visualization, auto-compaction at ~95% |
