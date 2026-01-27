# OpenCode Architecture & Command System Research

**Research Date**: 2026-01-17
**Research Objective**: Deep investigation of OpenCode's architecture for custom commands, agents, and extensibility mechanisms
**Confidence Level**: HIGH (Primary sources from official documentation)

---

## 1. Executive Summary

OpenCode is an open-source AI coding agent built for the terminal that provides a sophisticated command and agent system with high extensibility. Key findings:

- **Command System**: Markdown-based custom commands with YAML frontmatter, supporting arguments, file injection, and shell command execution
- **Agent Architecture**: Two-tier system (Primary Agents + Subagents) with configurable tools, permissions, and model overrides
- **Extensibility**: Plugin system via `@opencode-ai/plugin`, MCP server integration, and comprehensive configuration merging
- **Configuration**: JSON/JSONC files with hierarchical precedence from remote configs to inline environment variables
- **Key Differentiator from Claude Code**: Provider-agnostic (75+ providers), open-source, client/server architecture enabling remote operation

The architecture is well-suited for porting SuperClaude-style command frameworks, with some adaptation needed for the different configuration paradigms.

---

## 2. Command System Overview

### 2.1 Command Definition Format

Commands are defined as **Markdown files with YAML frontmatter**:

```markdown
---
description: Brief description of command purpose
agent: agent-name
model: model-identifier
subtask: true/false
---
Your prompt template content here with $ARGUMENTS placeholder
```

### 2.2 Command File Locations

Commands are discovered from multiple locations with later sources taking precedence:

| Location | Scope | Priority |
|----------|-------|----------|
| `~/.config/opencode/command/` | Global (user-wide) | Lower |
| `.opencode/command/` | Project-specific | Higher |
| `opencode.json` `command` section | Config-defined | Highest |

### 2.3 Command Naming Convention

- **Filename becomes command name**: `test.md` creates `/test`
- **Nested directories preserved**: `tasks/research.md` creates `tasks/research` command
- **Extension stripped**: `.md` extension is removed

### 2.4 Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `template` | string | Yes | The prompt sent to the LLM |
| `description` | string | No | Displayed in TUI interface |
| `agent` | string | No | Specifies which agent executes the command |
| `model` | string | No | Overrides default model for this command |
| `subtask` | boolean | No | Forces subagent invocation |

### 2.5 Placeholder Syntax

OpenCode supports rich placeholder syntax for dynamic commands:

| Placeholder | Purpose | Example |
|-------------|---------|---------|
| `$ARGUMENTS` | All passed arguments | `Review $ARGUMENTS for issues` |
| `$1`, `$2`, `$N` | Positional arguments | `Fix issue #$1 with priority $2` |
| `$NAME` | Named arguments (uppercase) | `Deploy to $ENVIRONMENT` |
| `!command` | Shell command injection | `Current branch: !git branch --show-current` |
| `@filename` | File content inclusion | `Review @package.json` |

### 2.6 JSON Configuration Alternative

Commands can also be defined in `opencode.json` or `opencode.jsonc`:

```json
{
  "command": {
    "test": {
      "template": "Run all tests and report coverage for $ARGUMENTS",
      "description": "Run tests with coverage",
      "agent": "build"
    },
    "review": {
      "template": "Review the code in @$1 for best practices",
      "description": "Code review command",
      "model": "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

### 2.7 Built-in Commands

OpenCode provides these built-in commands that can be overridden:

- `/init` - Initialize project configuration
- `/undo` - Undo last action
- `/redo` - Redo undone action
- `/share` - Share session
- `/help` - Display help

---

## 3. Agent Architecture

### 3.1 Agent Types

OpenCode implements a **two-tier agent system**:

#### Primary Agents
- Main assistants for direct user interaction
- Switch between them using `Tab` key or `switch_agent` keybind
- Handle main conversation with full tool access

#### Subagents
- Specialized assistants invoked by primary agents
- Triggered automatically based on task descriptions
- Manually invoked via `@agent-name` mention
- Create isolated sub-sessions

### 3.2 Built-in Agents

| Agent | Type | Purpose | Tool Access |
|-------|------|---------|-------------|
| **Build** | Primary | Default development agent | Full access to all tools |
| **Plan** | Primary | Analysis without modifications | Read-only, bash requires approval |
| **General** | Subagent | Complex questions and research | Multi-step task handling |
| **Explore** | Subagent | Rapid codebase exploration | Pattern-based file discovery |

### 3.3 Agent Configuration Methods

#### Method 1: JSON Configuration

```json
{
  "agent": {
    "review": {
      "description": "Reviews code for best practices",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.3,
      "maxSteps": 10,
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      },
      "permission": {
        "bash": {
          "git *": "ask",
          "grep *": "allow"
        }
      }
    }
  }
}
```

#### Method 2: Markdown Files

Create agent files in:
- Global: `~/.config/opencode/agent/`
- Project: `.opencode/agent/`

```markdown
---
description: Writes and maintains project documentation
mode: subagent
temperature: 0.5
maxSteps: 15
tools:
  bash: false
  edit: true
  write: true
permission:
  edit: allow
---
You are a technical writer creating clear, comprehensive documentation.
Focus on clarity, accuracy, and completeness.
```

### 3.4 Agent Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `description` | string | **Required** - Brief explanation of agent purpose |
| `mode` | enum | `primary`, `subagent`, or `all` |
| `model` | string | Override default model (e.g., `anthropic/claude-haiku-4-20250514`) |
| `temperature` | float | Response randomness (0.0-1.0) |
| `maxSteps` | integer | Maximum agentic iterations before text-only response |
| `prompt` | string | Path to custom system prompt file |
| `tools` | object | Enable/disable specific tools; supports wildcards |
| `permission` | object | Control action approval: `ask`, `allow`, `deny` |
| `hidden` | boolean | Hide subagent from autocomplete (subagents only) |

### 3.5 Permission System

Permissions control tool execution behavior:

```json
{
  "permission": {
    "edit": "ask",
    "bash": {
      "git *": "ask",
      "npm *": "allow",
      "rm *": "deny"
    },
    "webfetch": "allow"
  }
}
```

| Permission Value | Behavior |
|------------------|----------|
| `"allow"` | Execute without approval |
| `"ask"` | Require user approval before execution |
| `"deny"` | Disable the tool entirely |

### 3.6 Creating Custom Agents (Interactive)

```bash
opencode agent create
```

This interactive command guides through:
1. Save location selection (global or project)
2. Agent description input
3. System prompt generation
4. Tool selection
5. Markdown file creation

---

## 4. Extensibility Mechanisms

### 4.1 Plugin System

Plugins extend OpenCode via the `@opencode-ai/plugin` package:

```javascript
// .opencode/plugin/my-plugin.js
export default {
  tools: {
    myCustomTool: {
      description: "Description for LLM",
      parameters: z.object({
        input: z.string()
      }),
      execute: async ({ input }) => {
        // Tool implementation
        return { result: "output" };
      }
    }
  },
  hooks: {
    onSessionStart: async (session) => {
      // Hook implementation
    }
  }
}
```

**Plugin Locations**:
- `.opencode/plugin/` - Project-specific
- `~/.config/opencode/plugin/` - Global
- NPM packages via `plugin` config option

### 4.2 MCP Server Integration

#### Local MCP Server Configuration

```json
{
  "mcp": {
    "my-local-mcp": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": {
        "API_KEY": "{env:MY_API_KEY}"
      },
      "timeout": 5000
    }
  }
}
```

#### Remote MCP Server Configuration

```json
{
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://my-mcp-server.com",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:API_TOKEN}"
      },
      "oauth": {
        "clientId": "my-client-id",
        "clientSecret": "{env:CLIENT_SECRET}",
        "scope": "read write"
      }
    }
  }
}
```

#### MCP Tool Management

MCP tools integrate as standard tools:

```json
{
  "tools": {
    "my-mcp-server": false,
    "my-mcp*": true
  },
  "agent": {
    "build": {
      "tools": {
        "github-mcp*": true,
        "filesystem-mcp*": false
      }
    }
  }
}
```

### 4.3 Custom Tools Definition

Custom tools are defined via plugins or configuration:

```json
{
  "tools": {
    "customDeploy": {
      "description": "Deploy the application to staging",
      "parameters": {
        "type": "object",
        "properties": {
          "environment": { "type": "string" },
          "version": { "type": "string" }
        }
      },
      "execute": "scripts/deploy.sh"
    }
  }
}
```

### 4.4 Rules System (AGENTS.md)

Rules provide custom instructions for AI behavior:

**File Locations**:
- `AGENTS.md` - Project root (primary)
- `~/.config/opencode/AGENTS.md` - Global
- `CLAUDE.md` - Legacy compatibility

**Additional Instructions via Config**:
```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    "https://example.com/team-standards.md"
  ]
}
```

---

## 5. Command Routing Mechanism

### 5.1 CLI Command Processing

OpenCode uses **yargs** for CLI command parsing:

1. **Initialization**: Log system setup, environment variables set
2. **Parsing**: Arguments parsed via yargs framework
3. **Middleware**: Common initialization applied
4. **Routing**: Commands dispatched to registered handlers
5. **Bootstrap**: Project instance initialized
6. **Execution**: Handler logic runs
7. **Cleanup**: Resources released via finally block

### 5.2 Custom Command Discovery

```
loadCommand() function process:
1. Scan directories using Bun's Glob pattern matching
2. Parse markdown files with YAML frontmatter
3. Derive command names from file paths
4. Merge configurations from multiple sources
5. Register commands with TUI
```

### 5.3 Slash Command Execution Flow

```
User Input: /command arg1 arg2
    |
    v
Command Lookup (config + files)
    |
    v
Template Processing ($ARGUMENTS, !shell, @files)
    |
    v
Agent Selection (default or specified)
    |
    v
Model Override (if configured)
    |
    v
SessionPrompt.command() invocation
    |
    v
LLM Loop (streamText with tools)
    |
    v
Response + Tool Execution
```

### 5.4 Event-Driven Architecture

OpenCode employs a **pub-sub event bus**:

```
Events broadcast: Session updates, Tool executions, LLM responses
    |
    v
Event Bus (global distribution)
    |
    v
Subscribers:
  - TUI (Bubble Tea messages)
  - SSE clients (real-time updates)
  - Persistence layer (SQLite)
```

---

## 6. Configuration System

### 6.1 Configuration Precedence (Low to High)

1. **Remote config**: `.well-known/opencode` endpoint
2. **Global config**: `~/.config/opencode/opencode.json`
3. **Custom config**: `OPENCODE_CONFIG` environment variable
4. **Project config**: `opencode.json` in project root
5. **Directory configs**: `.opencode/` agents, commands, plugins
6. **Inline config**: `OPENCODE_CONFIG_CONTENT` environment variable

### 6.2 Configuration File Format

Supported formats:
- JSON (`opencode.json`)
- JSONC (`opencode.jsonc`) - JSON with comments

**NOT TOML** - Despite common misconceptions, OpenCode uses JSON/JSONC, not TOML.

### 6.3 Variable Substitution

```json
{
  "provider": {
    "anthropic": {
      "apiKey": "{env:ANTHROPIC_API_KEY}"
    }
  },
  "instructions": ["{file:./CODING_STANDARDS.md}"]
}
```

| Syntax | Purpose |
|--------|---------|
| `{env:VAR_NAME}` | Environment variable substitution |
| `{file:path}` | File content inclusion |

### 6.4 Complete Configuration Schema

```json
{
  "$schema": "https://opencode.ai/config.json",

  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "default_agent": "build",

  "provider": {
    "timeout": 600000,
    "setCacheKey": true,
    "anthropic": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
  },

  "agent": { /* agent definitions */ },
  "command": { /* command definitions */ },
  "tools": { /* tool enable/disable */ },
  "mcp": { /* MCP server configs */ },
  "plugin": ["plugin-name"],

  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow"
  },

  "instructions": ["AGENTS.md"],

  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true
  },

  "theme": "opencode",
  "tui": {
    "scroll_speed": 3,
    "diff_style": "auto"
  },

  "compaction": { "auto": true, "prune": true },
  "watcher": { "ignore": ["node_modules/**"] },
  "autoupdate": true
}
```

---

## 7. Comparison with Claude Code

### 7.1 Architecture Comparison

| Aspect | OpenCode | Claude Code |
|--------|----------|-------------|
| **Provider Support** | 75+ providers (OpenAI, Claude, Gemini, Bedrock, etc.) | Claude models only |
| **Configuration Format** | JSON/JSONC | Markdown (CLAUDE.md) + JSON |
| **Command Format** | Markdown + YAML frontmatter | Markdown + YAML frontmatter |
| **Agent System** | Primary + Subagents | Primary + Skills + Subagents |
| **Client Architecture** | Client/Server (remote capable) | Terminal-based |
| **TUI Framework** | Bubble Tea (Go) + SolidJS | Native terminal |
| **Extensibility** | Plugins + MCP | Skills + Hooks + MCP |
| **Checkpoint System** | Git-based snapshotting | Sophisticated rollback system |
| **Parallel Execution** | Currently synchronous subagents | Parallel subagents supported |

### 7.2 Command System Comparison

| Feature | OpenCode | Claude Code |
|---------|----------|-------------|
| **Command Location** | `.opencode/command/` | `.claude/commands/` |
| **Rules File** | `AGENTS.md` | `CLAUDE.md` |
| **Argument Syntax** | `$ARGUMENTS`, `$1`, `$NAME` | `$ARGUMENTS`, `$1` |
| **Shell Injection** | `` !`command` `` | Not documented |
| **File Inclusion** | `@filename` | `@filename` |
| **Model Override** | Yes (per-command) | Yes (per-command) |
| **Agent Assignment** | Yes | Via Skills |
| **Frontmatter** | YAML | YAML |
| **Namespacing** | Directory-based | Directory-based |

### 7.3 Agent System Comparison

| Feature | OpenCode | Claude Code |
|---------|----------|-------------|
| **Primary Agents** | Build, Plan | Yes (configurable) |
| **Subagents** | Yes (@mention) | Yes (parallel capable) |
| **Skills** | Not native | Yes (SKILL.md directories) |
| **Tool Permissions** | Granular (allow/ask/deny) | Yes |
| **Model Override** | Per-agent | Per-agent |
| **Temperature Control** | Yes | Yes |
| **Max Steps** | Yes (maxSteps) | Yes |

### 7.4 Unique OpenCode Features

1. **Provider Agnosticism**: Works with any LLM provider
2. **Client/Server Architecture**: Remote control via mobile app
3. **LSP Integration**: Native language server support
4. **Plugin System**: Extensible via `@opencode-ai/plugin`
5. **OAuth for MCP**: Automatic OAuth handling for remote servers
6. **Configuration Merging**: Sophisticated multi-source config merging

### 7.5 Unique Claude Code Features

1. **Checkpoints**: Granular conversation + code state rollback
2. **Thinking Mode**: Visible reasoning process (Opus 4.5)
3. **Parallel Subagents**: True concurrent execution
4. **Skills System**: Directory-based skill bundles with scripts
5. **Hooks**: Pre/Post tool execution hooks
6. **Cost Optimization**: Automatic model rotation for efficiency

---

## 8. Gaps and Differences Identified

### 8.1 Missing in OpenCode (vs Claude Code)

| Feature | Status | Notes |
|---------|--------|-------|
| **Parallel Subagent Execution** | NOT FOUND | Currently synchronous/modal |
| **Sophisticated Checkpoints** | PARTIAL | Git-based, less granular than Claude Code |
| **Skills System** | NOT FOUND | No SKILL.md equivalent |
| **Thinking Mode** | NOT FOUND | No visible reasoning process |
| **Hooks System** | PARTIAL | Plugin hooks exist, not command hooks |
| **Cost Optimization Routing** | NOT FOUND | No automatic model switching |

### 8.2 Missing in Claude Code (vs OpenCode)

| Feature | Status | Notes |
|---------|--------|-------|
| **Multi-Provider Support** | NOT AVAILABLE | Claude models only |
| **Client/Server Architecture** | NOT AVAILABLE | Terminal-only |
| **Native LSP Integration** | NOT AVAILABLE | External tooling required |
| **Plugin System** | PARTIAL | Skills/Hooks provide some extensibility |
| **OAuth for MCP** | NOT DOCUMENTED | May require manual auth |
| **Remote Configuration** | NOT DOCUMENTED | No `.well-known/opencode` equivalent |

### 8.3 Behavioral Differences

| Aspect | OpenCode | Claude Code |
|--------|----------|-------------|
| **Default Safety** | More permissive | Read-only default, approval required |
| **Context Management** | Manual awareness needed | Automatic compaction |
| **Session Persistence** | SQLite | Proprietary |
| **Update Mechanism** | Auto-update option | Anthropic-managed |

---

## 9. Recommendations for Porting

### 9.1 Command System Porting

**Compatible Elements**:
- Markdown format with YAML frontmatter transfers directly
- `$ARGUMENTS` and positional `$1`, `$2` work identically
- `@filename` file inclusion works identically
- Directory-based namespacing is equivalent

**Required Adaptations**:
```
Claude Code                    OpenCode
-----------                    --------
.claude/commands/             .opencode/command/
CLAUDE.md                     AGENTS.md
Skills (SKILL.md)             Custom Agents + Plugins
Hooks (PreToolUse, etc.)      Plugin hooks
```

### 9.2 Agent System Porting

**Direct Mapping**:
- Primary agents map to OpenCode primary agents
- Tool permissions translate directly
- Model overrides work equivalently

**Adaptations Needed**:
- Claude Code Skills need conversion to OpenCode agents + plugins
- Parallel subagent patterns need sequential workflow adaptation
- Hook system needs plugin-based implementation

### 9.3 Configuration Migration

**Migration Strategy**:
1. Convert CLAUDE.md to AGENTS.md format
2. Move commands from `.claude/commands/` to `.opencode/command/`
3. Adapt any Skills to agent + plugin combinations
4. Configure provider settings in `opencode.json`
5. Set up equivalent MCP servers

### 9.4 Recommended OpenCode Configuration for SuperClaude-style Framework

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",

  "agent": {
    "architect": {
      "description": "Systems architecture specialist",
      "mode": "subagent",
      "temperature": 0.3,
      "tools": { "bash": false }
    },
    "analyzer": {
      "description": "Root cause analysis specialist",
      "mode": "subagent",
      "temperature": 0.2
    }
  },

  "command": {
    "analyze": {
      "template": "Analyze $ARGUMENTS with focus on architecture and quality",
      "description": "Multi-dimensional code analysis",
      "agent": "analyzer"
    },
    "build": {
      "template": "Build $ARGUMENTS following best practices",
      "description": "Project builder with framework detection"
    }
  },

  "instructions": ["AGENTS.md", "docs/PRINCIPLES.md"],

  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

---

## 10. Source References

### Official Documentation
- [OpenCode Main Documentation](https://opencode.ai/docs/)
- [OpenCode Commands](https://opencode.ai/docs/commands/)
- [OpenCode Agents](https://opencode.ai/docs/agents/)
- [OpenCode Configuration](https://opencode.ai/docs/config/)
- [OpenCode Tools](https://opencode.ai/docs/tools/)
- [OpenCode MCP Servers](https://opencode.ai/docs/mcp-servers/)
- [OpenCode Rules](https://opencode.ai/docs/rules/)
- [OpenCode CLI](https://opencode.ai/docs/cli/)

### GitHub Repositories
- [OpenCode GitHub Repository](https://github.com/opencode-ai/opencode)
- [OpenAgents Framework](https://github.com/darrenhinde/OpenAgents)
- [OpenCode Config Example](https://github.com/joelhooks/opencode-config)
- [OpenCode Orchestration Mode](https://github.com/agents-to-go/opencode-orch-mode)

### Technical Deep Dives
- [How Coding Agents Actually Work: Inside OpenCode](https://cefboud.com/posts/coding-agents-internals-opencode-deepdive/)
- [Inside OpenCode: How to Build an AI Coding Agent](https://medium.com/@gaharwar.milind/inside-opencode-how-to-build-an-ai-coding-agent-that-actually-works-28c614494f4f)

### Comparison Articles
- [OpenCode vs Claude Code - Builder.io](https://www.builder.io/blog/opencode-vs-claude-code)
- [Comparing Claude Code vs OpenCode](https://www.andreagrandi.it/posts/comparing-claude-code-vs-opencode-testing-different-models/)
- [OpenCode vs Claude Code - Daniel Miessler](https://danielmiessler.com/blog/opencode-vs-claude-code)

### Community Resources
- [DeepWiki: Custom Commands and Agents](https://deepwiki.com/anomalyco/opencode/8.4-custom-commands-and-agents)
- [DeepWiki: Agent Configuration](https://deepwiki.com/anomalyco/opencode/5.1-agent-configuration)
- [Sisyphus Orchestrator Documentation](https://deepwiki.com/code-yeongyu/oh-my-opencode/4.1-sisyphus-orchestrator)

### Claude Code References
- [Claude Code Slash Commands Documentation](https://code.claude.com/docs/en/slash-commands)
- [Claude Code SDK Slash Commands](https://platform.claude.com/docs/en/agent-sdk/slash-commands)

---

## 11. Research Metadata

| Field | Value |
|-------|-------|
| **Research Date** | 2026-01-17 |
| **Primary Sources Consulted** | 15+ official documentation pages |
| **Secondary Sources** | 10+ comparison articles and technical deep dives |
| **Confidence Level** | HIGH |
| **Information Gaps** | Parallel execution details, internal routing code, plugin API specifics |
| **Recommended Follow-up** | Review actual OpenCode source code for implementation details |

---

*This research document was generated through systematic web research and documentation analysis. All claims are sourced from official OpenCode documentation or credible technical sources.*
