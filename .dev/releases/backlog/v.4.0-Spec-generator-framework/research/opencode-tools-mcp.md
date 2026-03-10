# OpenCode Tool & MCP Capabilities Research Report

**Research Date:** 2026-01-17
**Objective:** Comprehensive analysis of OpenCode's tool system and MCP integration capabilities
**Confidence Level:** HIGH (90%+) - Based on official documentation and multiple authoritative sources

---

## 1. Executive Summary

OpenCode is an open-source AI coding agent built for the terminal that provides comprehensive tool support and full Model Context Protocol (MCP) integration. Key findings:

- **MCP Support:** FULLY SUPPORTED - OpenCode functions as an MCP client with support for both local and remote MCP servers
- **Built-in Tools:** 13 core tools covering file I/O, search, execution, and task management
- **Tool Orchestration:** Supports agent-based delegation via Task tool with community plugins enabling parallel execution
- **Sequential Thinking:** Supported via MCP integration with Sequential Thinking server; native model reasoning effort configuration available
- **External Integration:** Full MCP client support with OAuth 2.0 authentication for remote servers
- **Tool Call Syntax:** JSON-based with Zod schema validation; supports multiple model-specific formats
- **Parallel Execution:** Currently synchronous by default; async background execution is a requested feature with community workarounds available

---

## 2. Built-in Tools Inventory

OpenCode provides **13 built-in tools** that enable LLM agents to interact with codebases:

### File I/O Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| **read** | Access file contents with optional line range support | `read` |
| **write** | Create new files or overwrite existing ones | `edit` |
| **edit** | Modify files using exact string replacements (patch-based) | `edit` |
| **patch** | Apply patch files/diffs to codebases | `edit` |

### Search Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| **grep** | Search file contents using regular expressions (uses ripgrep) | `grep` |
| **glob** | Find files via pattern matching (e.g., `**/*.js`) | `glob` |
| **list** | Display directory contents with glob filtering | `list` |

### Execution Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| **bash** | Execute shell commands in project environment | `bash` |
| **task** | Delegate subtasks to specialized subagents | `task` |

### Task Management Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| **todowrite** | Create/update task lists during sessions | `todowrite` |
| **todoread** | Read current todo list state | `todoread` |

### Utility Tools

| Tool | Description | Permission Key |
|------|-------------|----------------|
| **webfetch** | Fetch and read web pages for documentation lookup | `webfetch` |
| **question** | Prompt users for input, preferences, or clarifications | `question` |
| **skill** | Load SKILL.md files into conversations | `skill` |

### Experimental Tools

| Tool | Description | Activation |
|------|-------------|------------|
| **lsp** | Code intelligence (definitions, references, hover info) | `OPENCODE_EXPERIMENTAL_LSP_TOOL=true` |

**LSP Supported Operations:**
- `goToDefinition`
- `findReferences`
- `hover`
- `documentSymbol`
- `workspaceSymbol`
- `goToImplementation`
- `prepareCallHierarchy`
- `incomingCalls`
- `outgoingCalls`

### Tool Configuration Example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "bash": true,
    "read": true,
    "write": true,
    "edit": true,
    "glob": true,
    "grep": true,
    "list": true,
    "webfetch": true,
    "task": true,
    "todowrite": true,
    "todoread": true
  },
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow",
    "glob": "allow",
    "list": "allow"
  }
}
```

---

## 3. MCP Support Status

### Status: FULLY SUPPORTED

OpenCode implements comprehensive MCP client functionality, allowing integration with external tool servers that implement the Model Context Protocol specification.

### Supported Transport Types

| Type | Description | Configuration Key |
|------|-------------|-------------------|
| **Local** | Run as child processes using stdio | `type: "local"` |
| **Remote** | Communicate over HTTP/SSE with OAuth 2.0 | `type: "remote"` |

### MCP Configuration Structure

```json
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
      "environment": {
        "API_KEY": "your-key"
      },
      "enabled": true,
      "timeout": 5000
    },
    "remote-server": {
      "type": "remote",
      "url": "https://mcp.example.com",
      "headers": {
        "Authorization": "Bearer token"
      },
      "oauth": true
    }
  }
}
```

### Authentication Methods

1. **Automatic OAuth 2.0:** Detects 401 responses and initiates OAuth flows with Dynamic Client Registration (RFC 7591)
2. **Pre-registered Credentials:** Store client ID, secret, and scopes in configuration
3. **API Keys:** Disable OAuth with `"oauth": false` and pass keys via headers
4. **Manual Authentication:** Run `opencode mcp auth server-name` for individual servers

### Key MCP Capabilities

- **Dynamic Tool Discovery:** Automatically discovers available tools from connected MCP servers
- **Seamless Integration:** MCP tools work alongside built-in tools in the same pipeline
- **Permission Model:** MCP tools follow the same permission model as built-in tools
- **Multiple Server Support:** Configure multiple MCP servers per project
- **Tool Filtering:** Control availability through glob patterns in the `tools` section

### MCP Server Functionality (Upcoming)

There is an open feature request ([Issue #3306](https://github.com/sst/opencode/issues/3306)) to add native MCP server functionality, enabling OpenCode to act as an MCP server that external clients can connect to.

---

## 4. Tool Orchestration Patterns

### Agent Architecture

OpenCode implements a two-tier agent system:

**Primary Agents:**
- **Build Agent:** Default agent with full tool access for implementation
- **Plan Agent:** Read-only agent for analysis and planning

**Subagents:**
- **General:** Multi-step research and complex reasoning
- **Explore:** Fast codebase searching and navigation

### Task Delegation Flow

```
Primary Agent (Build/Plan)
    │
    ├── Task Tool invocation
    │       │
    │       └── Creates child session
    │               │
    │               └── Subagent executes (General/Explore/Custom)
    │                       │
    │                       └── Results returned to parent
    │
    └── Parent session continues
```

### Orchestrator Pattern

For complex workflows, OpenCode supports orchestrator agents that:
1. Analyze user requests
2. Delegate work to specialized subagents
3. Manage workflows through chaining (sequential) or parallelization

**Community Plugins for Enhanced Orchestration:**

| Plugin | Capability |
|--------|------------|
| **oh-my-opencode** | Hub-and-spoke architecture with 6+ specialist agents |
| **Open Orchestra** | Multi-agent orchestration with worker management |
| **Agent Orchestrator** | High-performance parallel execution framework |

### Permission Control for Delegation

```json
{
  "permission": {
    "task": "allow",
    "task.general": "allow",
    "task.explore": "ask",
    "task.*": "deny"
  }
}
```

---

## 5. Sequential Reasoning Capabilities

### Native Model Support

OpenCode supports configuring reasoning effort at the model level:

| Provider | Reasoning Levels |
|----------|-----------------|
| **Anthropic** | `max` (maximum thinking budget) |
| **OpenAI** | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| **Google** | `low`, `high` |

**Configuration Example:**

```json
{
  "models": {
    "claude-sonnet-4": {
      "provider": "anthropic",
      "variants": {
        "thinking": {
          "reasoningEffort": "max"
        }
      }
    }
  }
}
```

### Sequential Thinking via MCP

OpenCode can integrate with the [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) for structured problem-solving:

**Capabilities:**
- Breaking down complex problems into steps
- Branching into alternative reasoning paths
- Dynamic thought count adjustment
- Hypothesis generation and verification
- Revisable thought sequences

**Integration:**

```json
{
  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"]
    }
  }
}
```

### Chain-of-Thought Techniques

OpenCode supports various prompting techniques:
- **Zero-shot CoT:** Adding "Let's think step by step" patterns
- **Explicit Think Tags:** Using `<think>` tags to force reasoning traces (as in OpenCodeReasoning)
- **Model Variants:** Configure different reasoning depths for the same model

---

## 6. External Integration Options

### Integration Methods

| Method | Use Case | Configuration |
|--------|----------|---------------|
| **MCP Servers** | External tool providers | `mcp` config section |
| **Custom Tools** | Project-specific functions | `.opencode/tool/` directory |
| **Plugins** | Extended functionality | `.opencode/plugin/` or npm packages |
| **Hooks** | Event-driven automation | Plugin hook system |

### Custom Tool Definition

Custom tools are defined as TypeScript/JavaScript files:

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Search for packages in npm registry",
  args: {
    query: tool.schema.string().describe("Search query"),
    limit: tool.schema.number().optional().describe("Max results")
  },
  async execute(args, context) {
    const { agent, sessionID, messageID } = context
    // Implementation using any language via shell
    return { results: [...] }
  }
})
```

**File Locations:**
- Local (project): `.opencode/tool/<tool-name>.ts`
- Global (user): `~/.config/opencode/tool/<tool-name>.ts`

### Plugin System

Plugins extend OpenCode with custom tools, hooks, and integrations:

```json
{
  "plugin": ["oh-my-opencode", "./local-plugin"]
}
```

### Server Mode

OpenCode can run in headless HTTP server mode:

```bash
opencode serve
```

This exposes an OpenAPI 3.1 endpoint that clients can use for programmatic access.

---

## 7. Comparison with Claude Code Tools

| Feature | OpenCode | Claude Code |
|---------|----------|-------------|
| **Provider Lock-in** | None (75+ providers) | Anthropic only |
| **Open Source** | Yes | No |
| **Built-in Tools** | 13 core tools | Similar tool set |
| **MCP Support** | Full client support | Full client support |
| **Tool Syntax** | JSON with Zod validation | XML-like function calls |
| **Parallel Execution** | Community plugins (sync default) | Native subagent parallelization |
| **Checkpoint System** | Basic | Sophisticated (code + conversation) |
| **Sequential Thinking** | Via MCP integration | Native `mcp__sequential-thinking` |
| **LSP Integration** | Experimental | Not available |
| **Session Sharing** | URL-based sharing | GitHub-connected sessions |
| **Custom Tools** | TypeScript/JavaScript files | Not user-extensible |
| **Permission Model** | `allow`/`ask`/`deny` | Similar approval system |

### Tool Mapping (OpenCode to Claude Code)

| OpenCode Tool | Claude Code Equivalent | Notes |
|---------------|----------------------|-------|
| `read` | `Read` | Similar functionality |
| `write` | `Write` | Similar functionality |
| `edit` | `Edit` | OpenCode uses exact string replacement |
| `bash` | `Bash` | Similar with different timeout handling |
| `glob` | `Glob` | Similar pattern matching |
| `grep` | `Grep` | Both use ripgrep |
| `list` | N/A (use Bash `ls`) | OpenCode has dedicated tool |
| `task` | `Task` | OpenCode synchronous by default |
| `todowrite` | `TodoWrite` | Similar functionality |
| `todoread` | N/A | OpenCode has explicit read |
| `webfetch` | `WebFetch` | Similar functionality |
| `question` | N/A | OpenCode-specific |
| `skill` | `Skill` | Similar loading mechanism |
| `patch` | N/A | OpenCode-specific |
| `lsp` | N/A | OpenCode experimental feature |

---

## 8. Migration Strategy for SuperClaude Tools

### Phase 1: Core Tool Mapping

Map SuperClaude's tool orchestration to OpenCode equivalents:

| SuperClaude Concept | OpenCode Implementation |
|---------------------|------------------------|
| Wave System | Custom orchestrator agent with task delegation |
| Persona System | Agent configurations with specialized prompts |
| MCP Integration | Native MCP client configuration |
| Sequential Thinking | MCP server integration |
| Parallel Execution | oh-my-opencode plugin or custom orchestrator |

### Phase 2: Configuration Translation

**SuperClaude Flags to OpenCode:**

| SuperClaude Flag | OpenCode Equivalent |
|------------------|---------------------|
| `--think` | Model variant with reasoning effort |
| `--seq` | MCP sequential-thinking server |
| `--c7` | MCP context7 server |
| `--delegate` | Task tool with subagents |
| `--uc` | Custom compression rules |

### Phase 3: Custom Tool Development

Create OpenCode custom tools for SuperClaude-specific functionality:

```typescript
// .opencode/tool/wave-orchestrator.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Execute multi-wave operation",
  args: {
    operation: tool.schema.string(),
    waves: tool.schema.number().default(3)
  },
  async execute(args) {
    // Wave orchestration logic
  }
})
```

### Phase 4: Agent Configuration

Create specialized agents matching SuperClaude personas:

```json
{
  "agents": {
    "architect": {
      "model": "claude-sonnet-4",
      "system": "You are a systems architecture specialist...",
      "tools": ["read", "grep", "glob", "list", "task"],
      "permission": {
        "edit": "deny"
      }
    },
    "implementer": {
      "model": "claude-sonnet-4",
      "system": "You are an implementation specialist...",
      "tools": ["*"],
      "permission": {
        "bash": "ask"
      }
    }
  }
}
```

### Phase 5: Plugin Integration

Consider using or extending community plugins:

```json
{
  "plugin": [
    "oh-my-opencode",
    "@superclaude/opencode-plugin"
  ]
}
```

### Migration Checklist

- [ ] Map all SuperClaude commands to OpenCode agents/tools
- [ ] Configure MCP servers (Context7, Sequential Thinking)
- [ ] Create custom tools for unsupported features
- [ ] Develop agent configurations for personas
- [ ] Test wave orchestration patterns
- [ ] Validate permission models
- [ ] Document migration gaps and workarounds

---

## 9. Source References

### Official Documentation
- [OpenCode Tools Documentation](https://opencode.ai/docs/tools/)
- [OpenCode MCP Servers Guide](https://opencode.ai/docs/mcp-servers/)
- [OpenCode Custom Tools](https://opencode.ai/docs/custom-tools/)
- [OpenCode Agents](https://opencode.ai/docs/agents/)
- [OpenCode Models Configuration](https://opencode.ai/docs/models/)
- [OpenCode Configuration](https://opencode.ai/docs/config/)

### GitHub Resources
- [OpenCode Repository (sst/opencode)](https://github.com/sst/opencode)
- [MCP Server Feature Request - Issue #3306](https://github.com/sst/opencode/issues/3306)
- [Async Sub-Agent Feature Request - Issue #5887](https://github.com/sst/opencode/issues/5887)
- [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)

### Community Resources
- [oh-my-opencode Plugin](https://deepwiki.com/code-yeongyu/oh-my-opencode)
- [Awesome OpenCode](https://awesome-opencode.com/)
- [Oh My OpenCode MCPs](https://ohmyopencode.com/mcps/)

### DeepWiki Analysis
- [Built-in Tools Reference](https://deepwiki.com/sst/opencode/5.3-built-in-tools-reference)
- [Model Context Protocol Integration](https://deepwiki.com/sst/opencode/5.6-model-context-protocol-(mcp))
- [MCP and External Tools](https://deepwiki.com/opencode-ai/opencode/6.3-mcp-and-external-tools)

### Comparison Articles
- [OpenCode vs Claude Code - Builder.io](https://www.builder.io/blog/opencode-vs-claude-code)
- [OpenCode vs Claude Code - Daniel Miessler](https://danielmiessler.com/blog/opencode-vs-claude-code)
- [Comparing Claude Code vs OpenCode](https://www.andreagrandi.it/posts/comparing-claude-code-vs-opencode-testing-different-models/)

### Protocol Specifications
- [Model Context Protocol Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP First Anniversary Blog](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)

---

## Appendix A: Tool Call Syntax Examples

### OpenCode Standard JSON Format

```json
{
  "name": "read",
  "arguments": {
    "filePath": "/path/to/file.ts",
    "lineStart": 1,
    "lineEnd": 100
  }
}
```

### Multiple Tool Call Formats Supported

| Format | Use Case | Example |
|--------|----------|---------|
| Standard JSON | Most models | `{"name": "bash", "arguments": {"command": "ls"}}` |
| Gemma Tool Middleware | Gemma models | JSON in markdown fences |
| Morph XML Middleware | GLM models | Plain XML tool calls |
| Hermes Tool Middleware | Llama/Hermes | JSON in `<tool_call>` XML tags |

### Custom Tool Call with Context

```typescript
// Tool receives context with session information
async execute(args, context) {
  const {
    agent,      // Current agent name
    sessionID,  // Session identifier
    messageID   // Message identifier
  } = context

  // Use args validated by Zod schema
  const { query, limit } = args

  return { /* results */ }
}
```

---

## Appendix B: Configuration File Precedence

```
1. Remote config      (.well-known/opencode)     <- Lowest priority
2. Global config      (~/.config/opencode/opencode.json)
3. Custom config      (OPENCODE_CONFIG env var)
4. Project config     (opencode.json in project) <- Highest priority
```

---

## Appendix C: Known Limitations

1. **Parallel Execution:** Native parallel subagent execution not yet implemented (community plugins provide workarounds)
2. **MCP Server Mode:** OpenCode cannot yet act as an MCP server (feature requested)
3. **LSP Tool:** Experimental, requires environment flag
4. **JSON Parsing:** Some models may double-encode nested JSON structures
5. **UTF-8 Characters:** Known issues with accented characters in tool parameters
6. **Mistral API:** Requires specific tool call ID format (alphanumeric, 9 characters)

---

*Research compiled from official documentation, community resources, and comparative analysis. Last updated: 2026-01-17*
