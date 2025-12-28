# MCP Installer Fix Summary

## Problem Identified
The SuperClaude Framework installer was using `claude mcp add` CLI commands which are designed for Claude Desktop, not Claude Code. This caused installation failures.

## Root Cause
- Original implementation: Used `claude mcp add` CLI commands
- Issue: CLI commands are unreliable with Claude Code
- Best Practice: Claude Code prefers direct JSON file manipulation at `~/.claude/mcp.json`

## Solution Implemented

### 1. JSON-Based Helper Methods (Lines 213-302)
Created new helper methods for JSON-based configuration:
- `_get_claude_code_config_file()`: Get config file path
- `_load_claude_code_config()`: Load JSON configuration
- `_save_claude_code_config()`: Save JSON configuration
- `_register_mcp_server_in_config()`: Register server in config
- `_unregister_mcp_server_from_config()`: Unregister server from config

### 2. Updated Installation Methods

#### `_install_mcp_server()` (npm-based servers)
- **Before**: Used `claude mcp add -s user {server_name} {command} {args}`
- **After**: Direct JSON configuration with `command` and `args` fields
- **Config Format**:
```json
{
  "command": "npx",
  "args": ["-y", "@package/name"],
  "env": {
    "API_KEY": "value"
  }
}
```

#### `_install_docker_mcp_gateway()` (Docker Gateway)
- **Before**: Used `claude mcp add -s user -t sse {server_name} {url}`
- **After**: Direct JSON configuration with `url` field for SSE transport
- **Config Format**:
```json
{
  "url": "http://localhost:9090/sse",
  "description": "Dynamic MCP Gateway for zero-token baseline"
}
```

#### `_install_github_mcp_server()` (GitHub/uvx servers)
- **Before**: Used `claude mcp add -s user {server_name} {run_command}`
- **After**: Parse run command and create JSON config with `command` and `args`
- **Config Format**:
```json
{
  "command": "uvx",
  "args": ["--from", "git+https://github.com/..."]
}
```

#### `_install_uv_mcp_server()` (uv-based servers)
- **Before**: Used `claude mcp add -s user {server_name} {run_command}`
- **After**: Parse run command and create JSON config
- **Special Case**: Serena server includes project-specific `--project` argument
- **Config Format**:
```json
{
  "command": "uvx",
  "args": ["--from", "git+...", "serena", "start-mcp-server", "--project", "/path/to/project"]
}
```

#### `_uninstall_mcp_server()` (Uninstallation)
- **Before**: Used `claude mcp remove {server_name}`
- **After**: Direct JSON configuration removal via `_unregister_mcp_server_from_config()`

### 3. Updated Check Method
#### `_check_mcp_server_installed()`
- **Before**: Used `claude mcp list` CLI command
- **After**: Reads `~/.claude/mcp.json` directly and checks `mcpServers` section
- **Special Case**: For AIRIS Gateway, also verifies SSE endpoint is responding

## Benefits
1. **Reliability**: Direct JSON manipulation is more reliable than CLI commands
2. **Compatibility**: Works correctly with Claude Code
3. **Performance**: No subprocess calls for registration
4. **Consistency**: Follows AIRIS MCP Gateway working pattern

## Testing Required
- Test npm-based server installation (sequential-thinking, context7, magic)
- Test Docker Gateway installation (airis-mcp-gateway)
- Test GitHub/uvx server installation (serena)
- Test server uninstallation
- Verify config file format at `~/.claude/mcp.json`

## Files Modified
- `/Users/kazuki/github/SuperClaude_Framework/setup/components/mcp.py`
  - Added JSON helper methods (lines 213-302)
  - Updated `_check_mcp_server_installed()` (lines 357-381)
  - Updated `_install_mcp_server()` (lines 509-611)
  - Updated `_install_docker_mcp_gateway()` (lines 571-747)
  - Updated `_install_github_mcp_server()` (lines 454-569)
  - Updated `_install_uv_mcp_server()` (lines 325-452)
  - Updated `_uninstall_mcp_server()` (lines 972-987)

## Reference Implementation
AIRIS MCP Gateway Makefile pattern:
```makefile
install-claude: ## Install and register with Claude Code
    @mkdir -p $(HOME)/.claude
    @rm -f $(HOME)/.claude/mcp.json
    @ln -s $(PWD)/mcp.json $(HOME)/.claude/mcp.json
```

## Next Steps
1. Test the modified installer with a clean Claude Code environment
2. Verify all server types install correctly
3. Check that uninstallation works properly
4. Update documentation if needed
