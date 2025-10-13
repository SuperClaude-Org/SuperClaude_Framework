<div align="center">

# 📦 SuperClaude Installation Guide

### **Transform Claude Code with 21 Commands, 14 Agents & 6 MCP Servers**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.5-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux%20|%20macOS%20|%20Windows-orange?style=for-the-badge" alt="Platform">
</p>

<p align="center">
  <a href="#-quick-installation">Quick Install</a> •
  <a href="#-requirements">Requirements</a> •
  <a href="#-installation-methods">Methods</a> •
  <a href="#-verification">Verify</a> •
  <a href="#-troubleshooting">Troubleshoot</a>
</p>

</div>

---

## ⚡ **Quick Installation**

<div align="center">

### **Choose Your Preferred Method**

| Method | Command | Platform | Best For |
|:------:|---------|:--------:|----------|
| **🐍 pipx** | `pipx install SuperClaude && SuperClaude install` | Linux/macOS | **✅ Recommended** - Isolated environment |
| **📦 pip** | `pip install SuperClaude && SuperClaude install` | All | Traditional Python setups |
| **🌐 npm** | `npm install -g @bifrost_inc/superclaude && superclaude install` | All | Node.js developers |
| **🔧 Dev** | `git clone ... && pip install -e ".[dev]"` | All | Contributors & developers |

</div>

---

## 📋 **Requirements**

<div align="center">

<table>
<tr>
<td align="center" width="50%">

### ✅ **Required**

| Component | Version | Check Command |
|-----------|---------|---------------|
| **Python** | 3.8+ | `python3 --version` |
| **pip** | Latest | `pip --version` |
| **Claude Code** | Latest | `claude --version` |
| **Disk Space** | 50MB | `df -h` |

</td>
<td align="center" width="50%">

### 💡 **Optional**

| Component | Purpose | Check Command |
|-----------|---------|---------------|
| **Node.js** | MCP Servers | `node --version` |
| **Git** | Version Control | `git --version` |
| **pipx** | Isolated Install | `pipx --version` |
| **RAM** | Performance | 1GB recommended |

</td>
</tr>
</table>

</div>

<details>
<summary><b>🔍 Quick System Check</b></summary>

```bash
# Run this to check all requirements at once
python3 --version && echo "✅ Python OK" || echo "❌ Python missing"
claude --version && echo "✅ Claude Code OK" || echo "❌ Claude Code missing"
node --version 2>/dev/null && echo "✅ Node.js OK (optional)" || echo "⚠️ Node.js missing (optional)"
git --version 2>/dev/null && echo "✅ Git OK (optional)" || echo "⚠️ Git missing (optional)"
```

</details>

---

## 🚀 **Installation Methods**

<div align="center">

### **Detailed Installation Instructions**

</div>

### **Method 1: pipx (Recommended)**

<table>
<tr>
<td width="60%">

```bash
# Install pipx if not present
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install SuperClaude
pipx install SuperClaude

# Run the installer
SuperClaude install
```

</td>
<td width="40%">

**✅ Advantages:**
- Isolated environment
- No dependency conflicts
- Clean uninstall
- Automatic PATH setup

**📍 Best for:**
- Linux/macOS users
- Clean system installs
- Multiple Python projects

</td>
</tr>
</table>

### **Method 2: pip (Traditional)**

<table>
<tr>
<td width="60%">

```bash
# Standard installation
pip install SuperClaude

# Or user installation
pip install --user SuperClaude

# Run the installer
SuperClaude install
```

</td>
<td width="40%">

**✅ Advantages:**
- Works everywhere
- Familiar to Python users
- Direct installation

**📍 Best for:**
- Windows users
- Virtual environments
- Quick setup

</td>
</tr>
</table>

### **Method 3: npm (Cross-platform)**

<table>
<tr>
<td width="60%">

```bash
# Global installation
npm install -g @bifrost_inc/superclaude

# Run the installer
superclaude install
```

</td>
<td width="40%">

**✅ Advantages:**
- Cross-platform
- NPM ecosystem
- JavaScript familiar

**📍 Best for:**
- Node.js developers
- NPM users
- Cross-platform needs

</td>
</tr>
</table>

### **Method 4: Development Installation**

<table>
<tr>
<td width="60%">

```bash
# Clone repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Install in development mode
pip install -e ".[dev]"

# Test installation
SuperClaude install --dry-run
```

</td>
<td width="40%">

**✅ Advantages:**
- Latest features
- Contribute to project
- Full source access

**📍 Best for:**
- Contributors
- Custom modifications
- Testing new features

</td>
</tr>
</table>

---

## 🎛️ **Installation Options**

<div align="center">

### **Customize Your Installation**

| Option | Command | Description |
|--------|---------|-------------|
| **Interactive** | `SuperClaude install` | Guided setup with prompts |
| **Specific Components** | `SuperClaude install --components core mcp modes` | Install only what you need |
| **Preview Mode** | `SuperClaude install --dry-run` | See what will be installed |
| **Force Install** | `SuperClaude install --force --yes` | Skip all confirmations |
| **List Components** | `SuperClaude install --list-components` | View available components |

</div>

---

## ✅ **Verification**

<div align="center">

### **Confirm Successful Installation**

</div>

### **Step 1: Check Installation**

```bash
# Verify SuperClaude version
python3 -m SuperClaude --version
# Expected: SuperClaude 4.1.5

# List installed components
SuperClaude install --list-components
# Expected: List of available components
```

### **Step 2: Test in Claude Code**

```bash
# Open Claude Code and try these commands:
/sc:brainstorm "test project"     # Should trigger discovery questions
/sc:analyze README.md              # Should provide structured analysis
@agent-security "review code"     # Should activate security specialist
```

### **Step 3: What's Installed**

<div align="center">

| Location | Contents | Size |
|----------|----------|------|
| `~/.claude/` | Framework files | ~50MB |
| `~/.claude/CLAUDE.md` | Main entry point | ~2KB |
| `~/.claude/*.md` | Behavioral instructions | ~200KB |
| `~/.claude/claude-code-settings.json` | MCP configurations | ~5KB |

</div>

---

## 🛠️ **Management**

<div align="center">

<table>
<tr>
<th>📦 Update</th>
<th>💾 Backup</th>
<th>🗑️ Uninstall</th>
</tr>
<tr>
<td>

```bash
# Update to latest
pip install --upgrade SuperClaude
SuperClaude update
```

</td>
<td>

```bash
# Create backup
SuperClaude backup --create

# Restore backup
SuperClaude backup --restore [file]
```

</td>
<td>

```bash
# Remove framework
SuperClaude uninstall

# Uninstall package
pip uninstall SuperClaude
```

</td>
</tr>
</table>

</div>

---

## 🔧 **Troubleshooting**

<details>
<summary><b>❌ PEP 668 Error (Python Package Management)</b></summary>

This error occurs on systems with externally managed Python environments.

**Solutions (in order of preference):**

```bash
# Option 1: Use pipx (Recommended)
pipx install SuperClaude

# Option 2: User installation
pip install --user SuperClaude

# Option 3: Virtual environment
python3 -m venv superclaude-env
source superclaude-env/bin/activate  # Linux/macOS
# or
superclaude-env\Scripts\activate  # Windows
pip install SuperClaude

# Option 4: Force (use with caution)
pip install --break-system-packages SuperClaude
```

</details>

<details>
<summary><b>❌ Command Not Found</b></summary>

If `SuperClaude` command is not found after installation:

```bash
# Check if package is installed
python3 -m pip show SuperClaude

# Run using Python module
python3 -m SuperClaude install

# Add to PATH (if using --user)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # Linux
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc   # macOS
```

</details>

<details>
<summary><b>❌ Claude Code Not Found</b></summary>

If Claude Code is not installed or not in PATH:

1. Download from [https://claude.ai/code](https://claude.ai/code)
2. Install following platform instructions
3. Verify with: `claude --version`
4. Restart terminal after installation

</details>

<details>
<summary><b>❌ Permission Denied</b></summary>

For permission errors during installation:

```bash
# Use user installation
pip install --user SuperClaude

# Or use sudo (not recommended)
sudo pip install SuperClaude

# Better: use pipx
pipx install SuperClaude
```

</details>

<details>
<summary><b>❌ Missing Python or pip</b></summary>

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# Install Homebrew first if needed
brew install python3
```

**Windows:**
- Download from [python.org](https://python.org)
- Check "Add Python to PATH" during installation
- Restart terminal after installation

</details>

---

## 📚 **Next Steps**

<div align="center">

### **Your Learning Journey**

<table>
<tr>
<th>🌱 Start Here</th>
<th>🌿 Expand Skills</th>
<th>🌲 Master Framework</th>
</tr>
<tr>
<td valign="top">

**First Week:**
- [Quick Start Guide](quick-start.md)
- [Commands Reference](../User-Guide/commands.md)
- Try `/sc:brainstorm`

</td>
<td valign="top">

**Week 2-3:**
- [Behavioral Modes](../User-Guide/modes.md)
- [Agents Guide](../User-Guide/agents.md)
- [Examples Cookbook](../Reference/examples-cookbook.md)

</td>
<td valign="top">

**Advanced:**
- [MCP Servers](../User-Guide/mcp-servers.md)
- [Technical Architecture](../Developer-Guide/technical-architecture.md)
- [Contributing Code](../Developer-Guide/contributing-code.md)

</td>
</tr>
</table>

</div>

---

<div align="center">

### **🎉 Installation Complete!**

You now have access to:

<p align="center">
  <b>21 Commands</b> • <b>14 AI Agents</b> • <b>6 Behavioral Modes</b> • <b>6 MCP Servers</b>
</p>

**Ready to start?** Try `/sc:brainstorm` in Claude Code for your first SuperClaude experience!

<p align="center">
  <a href="quick-start.md">
    <img src="https://img.shields.io/badge/📖_Continue_to-Quick_Start_Guide-blue?style=for-the-badge" alt="Quick Start">
  </a>
</p>

</div>