# MCP Server Installation Guide

SuperClaude provides a convenient CLI command for installing and managing MCP (Model Context Protocol) servers for Claude Code.

## Quick Start

```bash
# List available MCP servers
superclaude mcp --list

# Interactive installation (recommended for first-time users)
superclaude mcp

# Install specific servers
superclaude mcp --servers tavily --servers context7

# Install all servers
superclaude mcp --servers sequential-thinking context7 magic playwright serena morphllm-fast-apply tavily chrome-devtools
```

## Available MCP Servers

| Server | Description | Requires API Key |
|--------|-------------|------------------|
| **sequential-thinking** | Multi-step problem solving and systematic analysis | No |
| **context7** | Official library documentation and code examples | No |
| **magic** | Modern UI component generation and design systems | Yes (`TWENTYFIRST_API_KEY`) |
| **playwright** | Cross-browser E2E testing and automation | No |
| **serena** | Semantic code analysis and intelligent editing | No |
| **morphllm-fast-apply** | Fast Apply for context-aware code modifications | Yes (`MORPH_API_KEY`) |
| **tavily** | Web search and real-time information retrieval | Yes (`TAVILY_API_KEY`) |
| **chrome-devtools** | Chrome DevTools debugging and performance analysis | No |

## Installation Scopes

MCP servers can be installed at different scopes:

- **local** (default): Project-specific, private configuration
- **project**: Team-shared via `.mcp.json` file in version control
- **user**: Available across all projects on your machine

```bash
# Install for current project only
superclaude mcp --servers tavily --scope local

# Install for team (shared in version control)
superclaude mcp --servers context7 --scope project

# Install for all your projects
superclaude mcp --servers sequential-thinking --scope user
```

## API Key Management

Some MCP servers require API keys for full functionality. SuperClaude will prompt you to enter these keys during installation.

### Getting API Keys

- **Tavily**: Get your API key from [https://app.tavily.com](https://app.tavily.com)
- **Magic (21st.dev)**: Get your API key from [https://21st.dev](https://21st.dev)
- **Morphllm**: Get your API key from the Morphllm service

### Setting API Keys

During installation, you'll be prompted:

```
🔑 MCP server 'tavily' requires an API key
   Environment variable: TAVILY_API_KEY
   Description: Tavily API key for web search (get from https://app.tavily.com)
   Would you like to set TAVILY_API_KEY now? [Y/n]:
```

You can also set environment variables beforehand:

```bash
export TAVILY_API_KEY="your-api-key-here"
export TWENTYFIRST_API_KEY="your-api-key-here"
export MORPH_API_KEY="your-api-key-here"
```

## Prerequisites

Before installing MCP servers, ensure you have the following tools installed:

### Required
- **Claude CLI**: Required for all MCP server management
- **Node.js 18+**: Required for npm-based MCP servers (most servers)

### Optional
- **uv**: Required only for Serena MCP server

Check prerequisites:

```bash
# Check Claude CLI
claude --version

# Check Node.js
node --version

# Check uv (optional)
uv --version
```

## Installation Process

1. **Check Available Servers**
   ```bash
   superclaude mcp --list
   ```

2. **Install Servers**

   Interactive mode (recommended):
   ```bash
   superclaude mcp
   ```

   Or specify servers directly:
   ```bash
   superclaude mcp --servers tavily context7
   ```

3. **Verify Installation**
   ```bash
   claude mcp list
   ```

4. **Restart Claude Code**

   After installation, restart your Claude Code session to use the new servers.

5. **Test Servers**

   In Claude Code, use `/mcp` command to check server status and authenticate.

## Advanced Usage

### Dry Run

Preview what would be installed without actually installing:

```bash
superclaude mcp --servers tavily --dry-run
```

### Multiple Servers

Install multiple servers in one command:

```bash
superclaude mcp --servers sequential-thinking context7 tavily
```

### Custom Scope

Specify installation scope:

```bash
superclaude mcp --servers tavily --scope project
```

## Troubleshooting

### Server Not Found

If you see "Unknown server: xxx", check the available servers:

```bash
superclaude mcp --list
```

### API Key Issues

If a server isn't working:

1. Check if the API key is set:
   ```bash
   echo $TAVILY_API_KEY
   ```

2. Verify the server is installed:
   ```bash
   claude mcp list
   ```

3. Check server status in Claude Code:
   ```
   /mcp
   ```

### Installation Fails

1. **Check prerequisites**:
   ```bash
   claude --version
   node --version
   ```

2. **Check Node.js version** (must be 18+):
   ```bash
   node --version
   ```

3. **Try with verbose output**:
   ```bash
   superclaude mcp --servers tavily 2>&1 | tee install.log
   ```

## Integration with SuperClaude Commands

MCP servers enhance SuperClaude commands with additional capabilities:

- **/sc:research** - Uses Tavily for web search and real-time information
- **/sc:implement** - Can use Context7 for official documentation
- **/sc:design** - Can use Magic for UI component generation
- **/sc:test** - Can use Playwright for browser automation

## Best Practices

1. **Start with essentials**: Install `sequential-thinking` and `context7` first
2. **Add as needed**: Install other servers based on your workflow needs
3. **Use project scope**: For team projects, use `--scope project` for shared configuration
4. **Secure API keys**: Never commit API keys to version control

## See Also

- [MCP Server Documentation](mcp-servers.md) - Detailed server descriptions
- [Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp) - Official MCP documentation
- [Commands Guide](commands.md) - SuperClaude commands that use MCP servers
