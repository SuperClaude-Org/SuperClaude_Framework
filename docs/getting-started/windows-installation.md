# Windows Installation Guide

Step-by-step guide for installing SuperClaude Framework on Windows using PowerShell.

## Prerequisites

| Component | Version | Check Command |
|-----------|---------|---------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | Latest | `pip --version` |
| **Claude Code** | Latest | `claude --version` |
| **Git** | Any | `git --version` |

> **Note:** On Windows, use `python` instead of `python3`. If `python` is not found, check that you selected "Add Python to PATH" during installation.

### Installing Python

1. Download from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer and **check "Add python.exe to PATH"** at the bottom of the first screen
3. Click "Install Now"
4. Open a **new** PowerShell window and verify:
   ```powershell
   python --version
   pip --version
   ```

### Installing Claude Code

Follow the official instructions at [claude.ai/code](https://claude.ai/code), then verify:

```powershell
claude --version
```

---

## Installation

### Method 1: pip (Recommended for Windows)

Open PowerShell and run:

```powershell
pip install superclaude
```

Then install the slash commands:

```powershell
superclaude install
```

If `superclaude` is not recognized after install, use:

```powershell
python -m superclaude install
```

### Method 2: pipx

```powershell
pip install pipx
pipx ensurepath
```

Close and reopen PowerShell, then:

```powershell
pipx install superclaude
superclaude install
```

### Method 3: Development install from source

```powershell
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

pip install -e ".[dev]"
superclaude install
```

> **Note:** The `install.sh` script is for Linux/macOS. On Windows, use the pip commands above instead.

---

## Verify Installation

```powershell
# Check version
superclaude --version

# List installed commands
superclaude install --list

# Run health check
superclaude doctor
```

You should see 30 slash commands installed to `~/.claude/commands/sc/`.

---

## Post-Install: Test in Claude Code

Open Claude Code and try:

```
/sc:help
/sc:brainstorm "test project"
```

If `/sc:` commands are not appearing, restart Claude Code — it reads commands from `~/.claude/commands/` on startup.

---

## Optional: MCP Servers

MCP servers add enhanced capabilities (web search, context retrieval, etc.):

```powershell
# List available servers
superclaude mcp --list

# Interactive install
superclaude mcp

# Install specific servers
superclaude mcp --servers tavily --servers context7
```

Requires Node.js. Install from [nodejs.org](https://nodejs.org/) if needed.

---

## Troubleshooting

### "superclaude" is not recognized

pip installs scripts to a `Scripts/` directory that may not be on your PATH.

```powershell
# Find where pip installed it
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"

# Add that directory to your PATH (current session)
$env:PATH += ";$(python -c \"import sysconfig; print(sysconfig.get_path('scripts'))\")"

# Or run via python module
python -m superclaude install
```

To add it permanently, search "Environment Variables" in the Start menu, edit the user `Path` variable, and add the scripts directory.

### Permission errors

Run PowerShell as Administrator, or use `--user` flag:

```powershell
pip install --user superclaude
```

### Python not found / wrong version

If you have multiple Python versions, use the full path or the `py` launcher:

```powershell
py -3.12 -m pip install superclaude
py -3.12 -m superclaude install
```

### Slash commands don't appear in Claude Code

1. Verify commands were installed: `superclaude install --list`
2. Check the directory exists: `ls ~/.claude/commands/sc/`
3. Restart Claude Code completely (close and reopen)
4. If using a custom `CLAUDE_CONFIG_DIR`, ensure commands are installed there

### install.sh doesn't work on Windows

The `install.sh` script is a bash script for Linux/macOS. On Windows, use the pip commands from the Installation section above. If you need bash, install [Git for Windows](https://gitforwindows.org/) which includes Git Bash, then run:

```bash
bash install.sh
```
