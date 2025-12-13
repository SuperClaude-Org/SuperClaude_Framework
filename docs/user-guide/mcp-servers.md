# SuperClaude MCP Servers Guide 🔌

## Overview

MCP (Model Context Protocol) servers extend Claude Code's capabilities through specialized tools. SuperClaude integrates 8 MCP servers and provides Claude with instructions on when to activate them based on your tasks.

### 🔍 Reality Check
- **What MCP servers are**: External Node.js processes that provide additional tools
- **What they aren't**: Built-in SuperClaude functionality
- **How activation works**: Claude reads instructions to use appropriate servers based on context
- **What they provide**: Real tools that extend Claude Code's native capabilities

**Core Servers:**
- **context7**: Official library documentation and patterns
- **sequential-thinking**: Multi-step reasoning and analysis  
- **magic**: Modern UI component generation
- **playwright**: Browser automation and E2E testing
- **morphllm-fast-apply**: Pattern-based code transformations
- **serena**: Semantic code understanding and project memory
- **tavily**: Web search and real-time information retrieval
- **chrome-devtools**: Performance analysis and debugging

## Quick Start

**Setup Verification**: MCP servers activate automatically. For installation and troubleshooting, see [Installation Guide](../getting-started/installation.md) and [Troubleshooting](../reference/troubleshooting.md).

**Auto-Activation Logic:**

| Request Contains | Servers Activated |
|-----------------|------------------|
| Library imports, API names | **context7** |
| `--think`, debugging | **sequential-thinking** |  
| `component`, `UI`, frontend | **magic** |
| `test`, `e2e`, `browser` | **playwright** |
| Multi-file edits, refactoring | **morphllm-fast-apply** |
| Large projects, sessions | **serena** |
| `/sc:research`, `latest`, `current` | **tavily** |
| `performance`, `debug`, `LCP` | **chrome-devtools** |

## Server Details

### context7 📚
**Purpose**: Official library documentation access
**Triggers**: Import statements, framework keywords, documentation requests
**Requirements**: Node.js 16+, no API key

```bash
# Automatic activation
/sc:implement "React authentication system"
# → Provides official React patterns

# Manual activation  
/sc:analyze auth-system/ --c7
```

### sequential-thinking 🧠
**Purpose**: Structured multi-step reasoning and systematic analysis
**Triggers**: Complex debugging, `--think` flags, architectural analysis
**Requirements**: Node.js 16+, no API key

```bash
# Automatic activation
/sc:troubleshoot "API performance issues"
# → Enables systematic root cause analysis

# Manual activation
/sc:analyze --think-hard architecture/
```

### magic ✨
**Purpose**: Modern UI component generation from 21st.dev patterns
**Triggers**: UI requests, `/ui` commands, component development
**Requirements**: Node.js 16+, TWENTYFIRST_API_KEY ()

```bash
# Automatic activation
/sc:implement "responsive dashboard component"
# → Generates accessible UI with modern patterns

# API key setup
export TWENTYFIRST_API_KEY="your_key_here"
```

### playwright 🎭
**Purpose**: Real browser automation and E2E testing
**Triggers**: Browser testing, E2E scenarios, visual validation
**Requirements**: Node.js 16+, no API key

```bash
# Automatic activation
/sc:test --type e2e "user login flow"
# → Enables browser automation testing

# Manual activation
/sc:validate "accessibility compliance" --play
```

### morphllm-fast-apply 🔄
**Purpose**: Efficient pattern-based code transformations
**Triggers**: Multi-file edits, refactoring, framework migrations
**Requirements**: Node.js 16+, MORPH_API_KEY

```bash
# Automatic activation
/sc:improve legacy-codebase/ --focus maintainability
# → Applies consistent patterns across files

# API key setup
export MORPH_API_KEY="your_key_here"
```

### serena 🧭
**Purpose**: Semantic code understanding with project memory
**Triggers**: Symbol operations, large codebases, session management
**Requirements**: Python 3.9+, uv package manager, no API key

```bash
# Automatic activation  
/sc:load existing-project/
# → Builds project understanding and memory

# Manual activation
/sc:refactor "extract UserService" --serena
```

### tavily 🔍
**Purpose**: Web search and real-time information retrieval for research
**Triggers**: `/sc:research` commands, "latest" information requests, current events, fact-checking
**Requirements**: Node.js 16+, TAVILY_API_KEY (free tier available at https://app.tavily.com)

```bash
# Automatic activation
/sc:research "latest AI developments 2024"
# → Performs intelligent web research

# Manual activation  
/sc:analyze "market trends" --tavily

# API key setup (get free key at https://app.tavily.com)
export TAVILY_API_KEY="tvly-your_api_key_here"
```

### chrome-devtools 📊
**Purpose**: Performance analysis, debugging, and real-time browser inspection
**Triggers**: Performance auditing, debugging layout issues (e.g., CLS), slow loading times (LCP), console errors, network requests
**Requirements**: Node.js 16+, no API key

```bash
# Automatic activation
/sc:debug "page is loading slowly"
# → Enables performance analysis with Chrome DevTools

# Manual activation
/sc:analyze --performance "homepage"
```

**Capabilities:**
- **Web Search**: Comprehensive searches with ranking and filtering
- **News Search**: Time-filtered current events and updates
- **Content Extraction**: Full-text extraction from search results  
- **Domain Filtering**: Include/exclude specific domains
- **Multi-Hop Research**: Iterative searches based on findings (up to 5 hops)

**Research Depth Control:**
- `--depth quick`: 5-10 sources, basic synthesis
- `--depth standard`: 10-20 sources, structured report (default)
- `--depth deep`: 20-40 sources, comprehensive analysis
- `--depth exhaustive`: 40+ sources, academic-level research

## Unified MCP Gateway (Alternative Setup)

For users who want a simpler, unified setup that manages all MCP servers through a single endpoint, **AIRIS MCP Gateway** provides:

- **Single SSE endpoint** instead of 8+ separate stdio connections
- **HOT/COLD server management** for token optimization
- **Lazy loading** - servers start only when needed
- **Unified tool discovery** - all tools from one endpoint
- **Web UI** for server management

### Quick Setup

```bash
# One-command installation (no git clone required)
curl -O https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/docker-compose.dist.yml
docker compose -f docker-compose.dist.yml up -d

# Configure Claude Code to use gateway
claude mcp add airis-gateway -- npx -y mcp-remote http://localhost:9400/sse --allow-http
```

### Configuration

Create `mcp-config.json` for server customization:
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "enabled": true,
      "mode": "cold"
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "enabled": true,
      "mode": "cold"
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.tavily.com/mcp/?tavilyApiKey=${TAVILY_API_KEY}"],
      "enabled": true,
      "mode": "cold"
    }
  }
}
```

### HOT vs COLD Servers

| Mode | Behavior | Best For |
|------|----------|----------|
| **HOT** | Always running, immediate response | Memory, session persistence |
| **COLD** | Start on-demand, 1-5s startup | Web search, heavy tools |

**Token Optimization**: HOT servers advertise all tools upfront. COLD servers only advertise when activated, reducing initial token cost.

### More Information

- **Repository**: [github.com/agiletec-inc/airis-mcp-gateway](https://github.com/agiletec-inc/airis-mcp-gateway)
- **Documentation**: See gateway README for advanced configuration

---

## Configuration

**MCP Configuration File (`~/.claude.json`):**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "magic": {
      "command": "npx",
      "args": ["@21st-dev/magic"],
      "env": {"TWENTYFIRST_API_KEY": "${TWENTYFIRST_API_KEY}"}
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "morphllm-fast-apply": {
      "command": "npx",
      "args": ["@morph-llm/morph-fast-apply"],
      "env": {"MORPH_API_KEY": "${MORPH_API_KEY}"}
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant"]
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

## Usage Patterns

**Server Control:**
```bash
# Enable specific servers
/sc:analyze codebase/ --c7 --seq

# Disable all MCP servers
/sc:implement "simple function" --no-mcp

# Enable all servers
/sc:design "complex architecture" --all-mcp
```

**Multi-Server Coordination:**
```bash
# Full-stack development
/sc:implement "e-commerce checkout"
# → Sequential: workflow analysis
# → Context7: payment patterns  
# → Magic: UI components
# → Serena: code organization
# → Playwright: E2E testing
```

## Troubleshooting

**Common Issues:**
- **No servers connected**: Check Node.js: `node --version` (need v16+)
- **Context7 fails**: Clear cache: `npm cache clean --force`
- **Magic/Morphllm errors**: Expected without API keys (paid services)
- **Server timeouts**: Restart Claude Code session

**Quick Fixes:**
```bash
# Reset connections
# Restart Claude Code session

# Check dependencies  
node --version  # Should show v16+

# Test without MCP
/sc:command --no-mcp

# Check configuration
ls ~/.claude.json
```

**API Key Configuration:**
```bash
# For Magic server (required for UI generation)
export TWENTYFIRST_API_KEY="your_key_here"

# For Morphllm server (required for bulk transformations)
export MORPH_API_KEY="your_key_here"

# For Tavily server (required for web search - free tier available)
export TAVILY_API_KEY="tvly-your_key_here"

# Add to shell profile for persistence
echo 'export TWENTYFIRST_API_KEY="your_key"' >> ~/.bashrc
echo 'export MORPH_API_KEY="your_key"' >> ~/.bashrc
echo 'export TAVILY_API_KEY="your_key"' >> ~/.bashrc
```

**Environment Variable Usage:**
- ✅ `TWENTYFIRST_API_KEY` - Required for Magic MCP server functionality
- ✅ `MORPH_API_KEY` - Required for Morphllm MCP server functionality  
- ✅ `TAVILY_API_KEY` - Required for Tavily MCP server functionality (free tier available)
- ❌ Other env vars in docs - Examples only, not used by framework
- 📝 Magic and Morphllm are paid services, Tavily has free tier, framework works without them

## Server Combinations

**No API Keys (Free)**:
- context7 + sequential-thinking + playwright + serena

**1 API Key**:
- Add magic for professional UI development

**2 API Keys**:
- Add morphllm-fast-apply for large-scale refactoring

**Common Workflows:**
- **Learning**: context7 + sequential-thinking
- **Web Development**: magic + context7 + playwright  
- **Enterprise Refactoring**: serena + morphllm + sequential-thinking
- **Complex Analysis**: sequential-thinking + context7 + serena
- **Deep Research**: tavily + sequential-thinking + serena + playwright
- **Current Events**: tavily + context7 + sequential-thinking
- **Performance Tuning**: chrome-devtools + sequential-thinking + playwright

## Integration

**With SuperClaude Commands:**
- Analysis commands automatically use Sequential + Serena
- Implementation commands use Magic + Context7
- Testing commands use Playwright + Sequential
- Research commands use Tavily + Sequential + Playwright

**With Behavioral Modes:**
- Brainstorming Mode: Sequential for discovery
- Task Management: Serena for persistence
- Orchestration Mode: Optimal server selection
- Deep Research Mode: Tavily + Sequential + Playwright coordination

**Performance Control:**
- Automatic resource management based on system load
- Concurrency control: `--concurrency N` (1-15)
- Priority-based server selection under constraints

## Related Resources

**Essential Reading:**
- [Commands Guide](commands.md) - Commands that activate MCP servers
- [Quick Start Guide](../getting-started/quick-start.md) - MCP setup guide

**Advanced Usage:**
- [Behavioral Modes](modes.md) - Mode-MCP coordination
- [Agents Guide](agents.md) - Agent-MCP integration
- [Session Management](session-management.md) - Serena workflows

**Technical References:**
- [Examples Cookbook](../reference/examples-cookbook.md) - MCP workflow patterns
- [Technical Architecture](../developer-guide/technical-architecture.md) - Integration details