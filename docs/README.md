# SuperClaude Documentation

## 🎯 Essential Understanding

**SuperClaude is a Context Framework for Claude Code** - it installs behavioral instruction files that Claude Code reads to enhance its capabilities.

### How It Works
1. **Installation**: Python CLI installs context files to `~/.claude/`
2. **Commands**: Type `/sc:analyze` → Claude Code reads `analyze.md` instruction file
3. **Behavior**: Claude adopts behaviors defined in context files
4. **Result**: Enhanced development workflows through context switching

## 🚀 Quick Start (5 Minutes)

**New Users**: [Quick Start Guide →](Getting-Started/quick-start.md)
```bash
# Recommended for Linux/macOS
pipx install SuperClaude && SuperClaude install

# Traditional method
pip install SuperClaude && SuperClaude install

# Then try: /sc:brainstorm "web app idea" in Claude Code
```

**Having Issues**: [Quick Fixes →](Reference/common-issues.md) | [Troubleshooting →](Reference/troubleshooting.md)

## 📚 Documentation Structure

### 🌱 Start Here (New Users)
| Guide | Purpose |
|-------|---------|
| **[Quick Start](Getting-Started/quick-start.md)** | Setup and first commands |
| **[Installation](Getting-Started/installation.md)** | Detailed setup instructions |
| **[Commands Guide](User-Guide/commands.md)** | All 21 `/sc:` commands |

### 🌿 Daily Usage (Regular Users)
| Guide | Purpose | Use For |
|-------|---------|---------|
| **[Commands Guide](User-Guide/commands.md)** | Master all `/sc:` commands | Daily development |
| **[Agents Guide](User-Guide/agents.md)** | 14 domain specialists (`@agent-*`) | Expert assistance |
| **[Flags Guide](User-Guide/flags.md)** | Command behavior modification | Optimization |
| **[Modes Guide](User-Guide/modes.md)** | 5 behavioral modes | Workflow optimization |

### 🌲 Reference & Advanced (Power Users)
| Guide | Purpose | Use For |
|-------|---------|---------|
| **[Troubleshooting](Reference/troubleshooting.md)** | Problem resolution | When things break |
| **[Examples Cookbook](Reference/examples-cookbook.md)** | Practical usage patterns | Learning workflows |
| **[MCP Servers](User-Guide/mcp-servers.md)** | 6 enhanced capabilities | Advanced features |

### 🔧 Development & Contributing
| Guide | Purpose | Audience |
|-------|---------|----------|
| **[Technical Architecture](Developer-Guide/technical-architecture.md)** | System design | Contributors |
| **[Contributing](Developer-Guide/contributing-code.md)** | Development workflow | Developers |

## 🔑 Key Concepts

### What Gets Installed
- **Python CLI Tool** - Manages framework installation
- **Context Files** - `.md` behavioral instructions in `~/.claude/`
- **MCP Configurations** - Optional external tool settings

### Framework Components
- **21 Commands** (`/sc:*`) - Workflow automation patterns
- **14 Agents** (`@agent-*`) - Domain specialists
- **5 Modes** - Behavioral modification patterns
- **6 MCP Servers** - Optional external tools

## 🚀 Quick Command Reference

### In Your Terminal (Installation)
```bash
# Install framework (choose one)
pipx install SuperClaude       # Recommended for Linux/macOS
pip install SuperClaude        # Traditional method
npm install -g @bifrost_inc/superclaude  # Cross-platform

# Configure and maintain
SuperClaude install            # Configure Claude Code
SuperClaude update             # Update framework
python3 -m SuperClaude --version  # Check installation
```

### In Claude Code (Usage)
```bash
/sc:brainstorm "project idea"              # Start new project
/sc:implement "feature"                    # Build features
/sc:analyze src/                           # Analyze code
@agent-python-expert "optimize this"      # Manual specialist
@agent-security "review authentication"   # Security review
```

## 📊 Framework vs Software Comparison

| Component | Type | Where It Runs | What It Does |
|-----------|------|---------------|--------------|
| **SuperClaude Framework** | Context Files | Read by Claude Code | Modifies AI behavior |
| **Claude Code** | Software | Your computer | Executes everything |
| **MCP Servers** | Software | Node.js processes | Provide tools |
| **Python CLI** | Software | Python runtime | Manages installation |

## 🔄 How Everything Connects

```
User Input → Claude Code → Reads SuperClaude Context → Modified Behavior → Enhanced Output
                ↓
        May use MCP Servers
         (if configured)
```

## 🆘 Getting Help

**Quick Issues** (< 2 min): [Common Issues →](Reference/common-issues.md)  
**Complex Problems**: [Full Troubleshooting Guide →](Reference/troubleshooting.md)  
**Installation Issues**: [Installation Guide →](Getting-Started/installation.md)  
**Command Help**: [Commands Guide →](User-Guide/commands.md)  
**Community Support**: [GitHub Discussions](https://github.com/SuperClaude-Org/SuperClaude_Framework/discussions)

## 🤔 Common Misconceptions Clarified

❌ **"SuperClaude is an AI assistant"**  
✅ SuperClaude is a configuration framework that enhances Claude Code

❌ **"I'm running SuperClaude"**  
✅ You're running Claude Code with SuperClaude context loaded

❌ **"Claude Code executes; SuperClaude provides context my commands"**  
✅ Claude Code executes everything; SuperClaude provides the instructions

❌ **"The .md files are documentation"**  
✅ The .md files ARE the framework - active instruction sets

---

*Remember: SuperClaude enhances Claude Code through context - it doesn't replace it or run alongside it. Everything happens within Claude Code itself.*