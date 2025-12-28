# Serena MCP Installation Troubleshooting

## Common Issues and Solutions

### Issue: "Failed to spawn: serena" Error

**Symptoms:**
```
error: Failed to spawn: `serena`
Caused by: No such file or directory (os error 2)
```

**Root Cause:**
The SuperClaude installer was incorrectly configured to use `uv run serena` instead of `uvx` for Serena MCP server installation.

**Solution:**

1. **Remove existing broken installation:**
   ```bash
   claude mcp remove serena
   ```

2. **Install Serena using correct uvx method:**
   ```bash
   uvx --from git+https://github.com/oraios/serena serena --help
   ```

3. **Register with Claude CLI:**
   ```bash
   claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant
   ```

4. **Verify installation:**
   ```bash
   claude mcp list
   ```

### Issue: uv vs uvx Confusion

**Difference:**
- `uv run serena` - Runs serena from local project dependencies (fails if not installed locally)
- `uvx --from git+https://github.com/oraios/serena serena` - Runs serena directly from GitHub repository

**Correct Usage:**
Always use `uvx` for Serena, as it's designed to work with remote GitHub repositories.

### GitHub Codespace Specific Issues

**Issue: UV Installation Method**
If you installed UV with the curl method:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Make sure `uvx` is available:
```bash
uvx --version
```

If not available, install uv with pip:
```bash
pip install uv
```

### Verification Steps

After successful installation, verify Serena is working:

1. **Check MCP connection:**
   ```bash
   claude mcp list
   ```

2. **Test basic functionality:**
   Start Claude Code and verify Serena appears in available MCP servers

3. **Check logs for errors:**
   ```bash
   ls ~/.cache/claude-cli-nodejs/*/mcp-logs-serena/
   cat ~/.cache/claude-cli-nodejs/*/mcp-logs-serena/latest.txt
   ```

### Environment-Specific Notes

**GitHub Codespaces:**
- UV is often pre-installed but may not include uvx
- Default Python environment may need UV package installation
- Network connectivity for git+https:// URLs required

**Local Development:**
- Ensure uvx is installed: `pip install uv` or `pipx install uv`
- Verify git access to GitHub repositories

**WSL/Linux:**
- Ensure proper permissions for ~/.claude/ directory
- Check Python environment compatibility

### Manual Configuration

If automatic installation fails, manually configure `~/.claude.json`:

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant"
      ]
    }
  }
}
```

### Getting Help

If issues persist:
1. Check [Serena documentation](https://github.com/oraios/serena)
2. Verify uvx installation: `uvx --version`
3. Test direct installation: `uvx --from git+https://github.com/oraios/serena serena --help`
4. Report issues to [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)

### Version Information

This troubleshooting guide is for:
- SuperClaude Framework v4.1.5+
- Serena MCP (latest from GitHub)
- UV/UVX package manager

For older versions, refer to legacy documentation or upgrade to latest SuperClaude Framework.