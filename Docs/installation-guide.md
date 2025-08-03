# SuperClaude Installation Guide 📦

## 🎯 It's Easier Than It Looks!

**The honest truth**: This guide looks long because we want to cover all the details, but installation is actually pretty simple. Most people are done in 2 minutes with one command! 

### Step 1: Install the Package

**Option A: From PyPI (Recommended)**
```bash
uv add SuperClaude
```

**Option B: From Source**
```bash
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework
uv sync
```
### 🔧 UV / UVX Setup Guide

SuperClaude v3 also supports installation via [`uv`](https://github.com/astral-sh/uv) (a faster, modern Python package manager) or `uvx` for cross-platform usage.

### 🌀 Install with `uv`

Make sure `uv` is installed:

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

> Or follow instructions from: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

Once `uv` is available, you can install SuperClaude like this:

```bash
uv venv
source .venv/bin/activate
uv pip install SuperClaude
```

### ⚡ Install with `uvx` (Cross-platform CLI)

If you’re using `uvx`, just run:

```bash
uvx pip install SuperClaude
```
## 🔧 UV / UVX Setup Guide

SuperClaude v3 also supports installation via [`uv`](https://github.com/astral-sh/uv) (a faster, modern Python package manager) or `uvx` for cross-platform usage.

### 🌀 Install with `uv`

Make sure `uv` is installed:

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

> Or follow instructions from: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

Once `uv` is available, you can install SuperClaude like this:

```bash
uv venv
source .venv/bin/activate
uv pip install SuperClaude
```

### ⚡ Install with `uvx` (Cross-platform CLI)

If you’re using `uvx`, just run:

```bash
uvx pip install SuperClaude
```

### ✅ Finish Installation

After installing, continue with the usual installer step:

```bash
python3 -m SuperClaude install
```

Or using bash-style CLI:

```bash
SuperClaude install
```

### 🧠 Note:

* `uv` provides better caching and performance.
* Compatible with Python 3.8+ and works smoothly with SuperClaude.

---

### ⚠️ Important Note 
**After installing the SuperClaude.**
**You can use `SuperClaude commands`
, `python3 -m SuperClaude commands` or also `python3 SuperClaude commands`**

**What just happened?** SuperClaude tried to set up everything you need. Usually no complex configuration, dependency hunting, or setup headaches! 🎉

---

A comprehensive guide to installing SuperClaude v3. But remember - most people never need to read past the quick start above! 😊

## Before You Start 🔍

### What You Need 💻

SuperClaude works on **Windows**, **macOS**, and **Linux**. Here's what you need:

**Required:**
- **Python 3.8 or newer** - The framework is written in Python
- **Claude CLI** - SuperClaude enhances Claude Code, so you need it installed first

**Optional (but recommended):**
- **Node.js 16+** - Only needed if you want MCP server integration
- **Git** - Helpful for development workflows

### Quick Check 🔍

Before installing, let's make sure you have the basics:

```bash
# Check Python version (should be 3.8+)
python3 --version

# Check if Claude CLI is installed
claude --version

# Check Node.js (optional, for MCP servers)
node --version
```

If any of these fail, see the [Prerequisites Setup](#prerequisites-setup-🛠️) section below.

## Quick Start 🚀

**🏆 The "Just Get It Working" Approach (Recommended for 90% of Users)**
**Option A: From PyPI (Recommended)**
```bash
pip install SuperClaude

# Install with recommended settings  
SuperClaude install --quick

# That's it! 🎉
```
**Option B: From Source**
```bash
# Clone the repo
git clone <repository-url>
cd SuperClaude
pip install .

# Install with recommended settings  
SuperClaude install --quick

# That's it! 🎉
```
**⚠️ Important Note**
**After installing the SuperClaude.**
**You can use `SuperClaude commands`
, `python3 -m SuperClaude commands` or also `python3 SuperClaude commands`**

**What you just got:**
- ✅ All 16 smart commands that auto-activate experts
- ✅ 11 specialist personas that know when to help
- ✅ Intelligent routing that figures out complexity for you
- ✅ About 2 minutes of your time and ~50MB disk space

**Seriously, you're done.** Open Claude Code, type `/help`, and watch SuperClaude work its magic.

**Nervous about what it will do?** See first with:
```bash
SuperClaude install --quick --dry-run
```

## Installation Options 🎯

We have three installation profiles to choose from:

### 🎯 Minimal Installation
```bash
SuperClaude install --minimal
```
- **What**: Just the core framework files
- **Time**: ~1 minute
- **Space**: ~20MB  
- **Good for**: Testing, basic enhancement, minimal setups
- **Includes**: Core behavior documentation that guides Claude

### 🚀 Quick Installation (Recommended)
```bash
SuperClaude install --quick
```
- **What**: Core framework + 16 slash commands
- **Time**: ~2 minutes
- **Space**: ~50MB
- **Good for**: Most users, general development
- **Includes**: Everything in minimal + specialized commands like `/analyze`, `/build`, `/improve`

### 🔧 Developer Installation  
```bash
SuperClaude install --profile developer
```
- **What**: Everything including MCP server integration
- **Time**: ~5 minutes
- **Space**: ~100MB
- **Good for**: Power users, contributors, advanced workflows
- **Includes**: Everything + Context7, Sequential, Magic, Playwright servers

### 🎛️ Interactive Installation
```bash
SuperClaude install
```
- Lets you pick and choose components
- Shows detailed descriptions of what each component does
- Good if you want control over what gets installed

## Step-by-Step Installation 📋

### Prerequisites Setup 🛠️

**Missing Python?**
```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip

# macOS  
brew install python3

# Windows
# Download from https://python.org/downloads/
#or open command prompt or powershell
winget install python
```

**Missing Claude CLI?**
- Visit https://claude.ai/code for installation instructions
- SuperClaude enhances Claude Code, so you need it first

**Missing Node.js? (Optional)**
```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install nodejs npm

# macOS
brew install node

# Windows  
# Download from https://nodejs.org/
#or open command prompt or powershell
winget install nodejs
```

### Getting SuperClaude 📥

**Option 1: From PyPI (Recommended)**
```bash
pip install SuperClaude
```

**Option 2: Download the latest release**
```bash
# Download and extract the latest release
# (Replace URL with actual release URL)
curl -L <release-url> -o superclaude-v3.zip
unzip superclaude-v3.zip
cd superclaude-v3
pip install .
```

**Option 3: Clone from Git**
```bash
git clone <repository-url>
cd SuperClaude
pip install .
```

### Running the Installer 🎬

The installer is pretty smart and will guide you through the process:

```bash
# See all available options
SuperClaude install --help

# Quick installation (recommended)
SuperClaude install --quick

# Want to see what would happen first?
SuperClaude install --quick --dry-run

# Install everything
SuperClaude install --profile developer

# Quiet installation (minimal output)
SuperClaude install --quick --quiet

# Force installation (skip confirmations)
python3 SuperClaude.py install --quick --force
```

### During Installation 📱

Here's what happens when you install:

1. **System Check** - Verifies you have required dependencies
2. **Directory Setup** - Creates `~/.claude/` directory structure
3. **Core Files** - Copies framework documentation files
4. **Commands** - Installs slash command definitions (if selected)
5. **MCP Servers** - Downloads and configures MCP servers (if selected)
6. **Configuration** - Sets up `settings.json` with your preferences
7. **Validation** - Tests that everything works

The installer shows progress and will tell you if anything goes wrong.

## After Installation ✅

### Quick Test 🧪

Let's make sure everything worked:

```bash
# Check if files were installed
ls ~/.claude/

# Should show: CLAUDE.md, COMMANDS.md, settings.json, etc.
```

**Test with Claude Code:**
1. Open Claude Code
2. Try typing `/help` - you should see SuperClaude commands
3. Try `/analyze --help` - should show command options

### What Got Installed 📂

SuperClaude installs to `~/.claude/` by default. Here's what you'll find:

```
~/.claude/
├── CLAUDE.md              # Main framework entry point
├── COMMANDS.md             # Available slash commands  
├── FLAGS.md                # Command flags and options
├── PERSONAS.md             # Smart persona system
├── PRINCIPLES.md           # Development principles
├── RULES.md                # Operational rules
├── MCP.md                  # MCP server integration
├── MODES.md                # Operational modes
├── ORCHESTRATOR.md         # Intelligent routing
├── settings.json           # Configuration file
└── commands/               # Individual command definitions
    ├── analyze.md
    ├── build.md
    ├── improve.md
    └── ... (13 more)
```

**What each file does:**
- **CLAUDE.md** - Tells Claude Code about SuperClaude and loads other files
- **settings.json** - Configuration (MCP servers, hooks, etc.)
- **commands/** - Detailed definitions for each slash command

### First Steps 🎯

Try these commands to get started:

```bash
# In Claude Code, try these:
/sc:help                    # See available commands
/sc:analyze README.md       # Analyze a file
/sc:build --help           # See build options
/sc:improve --help         # See improvement options
```

**Don't worry if it seems overwhelming** - SuperClaude enhances Claude Code gradually. You can use as much or as little as you want.

## Managing Your Installation 🛠️

### Updates 📅

Keep SuperClaude up to date:

```bash
# Check for updates
SuperClaude update

# Force update (overwrite local changes)
SuperClaude update --force

# Update specific components only
SuperClaude update --components core,commands

# See what would be updated
SuperClaude update --dry-run
```

**When to update:**
- When new SuperClaude versions are released
- If you're having issues (updates often include fixes)
- When new MCP servers become available

### Backups 💾

Create backups before major changes:

```bash
# Create a backup
SuperClaude backup --create

# List existing backups  
SuperClaude backup --list

# Restore from backup
SuperClaude backup --restore

# Create backup with custom name
SuperClaude backup --create --name "before-update"
```

**When to backup:**
- Before updating SuperClaude
- Before experimenting with settings
- Before uninstalling
- Periodically if you've customized heavily

### Uninstallation 🗑️

If you need to remove SuperClaude:

```bash
# Remove SuperClaude (keeps backups)
SuperClaude uninstall

# Complete removal (removes everything)
SuperClaude uninstall --complete

# See what would be removed
SuperClaude uninstall --dry-run
```

**What gets removed:**
- All files in `~/.claude/` 
- MCP server configurations
- SuperClaude settings from Claude Code

**What stays:**
- Your backups (unless you use `--complete`)
- Claude Code itself (SuperClaude doesn't touch it)
- Your projects and other files

## Troubleshooting 🔧

### Common Issues 🚨

**"Python not found"**
```bash
# Try python instead of python3
python --version

# Or check if it's installed but not in PATH
which python3
```

**"Claude CLI not found"**
- Make sure Claude Code is installed first
- Try `claude --version` to verify
- Visit https://claude.ai/code for installation help

**"Permission denied"**
```bash
# Try with explicit Python path
/usr/bin/python3 SuperClaude.py install --quick

# Or check if you need different permissions
ls -la ~/.claude/
```

**"MCP servers won't install"**
- Check that Node.js is installed: `node --version`
- Check that npm is available: `npm --version`  
- Try installing without MCP first: `--minimal` or `--quick`

**"Installation fails partway through"**
```bash
# Try with verbose output to see what's happening
SuperClaude install --quick --verbose

# Or try a dry run first
SuperClaude install --quick --dry-run
```

### Platform-Specific Issues 🖥️

**Windows:**
- Use `python` instead of `python3` if you get "command not found"
- Run Command Prompt as Administrator if you get permission errors
- Make sure Python is in your PATH

**macOS:**  
- You might need to approve SuperClaude in Security & Privacy settings
- Use `brew install python3` if you don't have Python 3.8+
- Try using `python3` explicitly instead of `python`

**Linux:**
- Make sure you have `python3-pip` installed
- You might need `sudo` for some package installations
- Check that `~/.local/bin` is in your PATH

### Still Having Issues? 🤔

**Check our troubleshooting resources:**
- GitHub Issues: https://github.com/SuperClaude-Org/SuperClaude_Framework/issues
- Look for existing issues similar to yours
- Create a new issue if you can't find a solution

**When reporting bugs, please include:**
- Your operating system and version
- Python version (`python3 --version`)
- Claude CLI version (`claude --version`)
- The exact command you ran
- The complete error message
- What you expected to happen

**Getting Help:**
- GitHub Discussions for general questions
- Check the README.md for latest updates
- Look at the ROADMAP.md to see if your issue is known

## Advanced Options ⚙️

### Custom Installation Directory

```bash
# Install to custom location
SuperClaude install --quick --install-dir /custom/path

# Use environment variable
export SUPERCLAUDE_DIR=/custom/path
SuperClaude install --quick
```

### Component Selection

```bash
# See available components
SuperClaude install --list-components

# Install specific components only
SuperClaude install --components core,commands

# Skip certain components
SuperClaude install --quick --skip mcp
```

### Development Setup

If you're planning to contribute or modify SuperClaude:

```bash
# Developer installation with all components
SuperClaude install --profile developer

# Install in development mode (symlinks instead of copies)
SuperClaude install --profile developer --dev-mode

# Install with git hooks for development
SuperClaude install --profile developer --dev-hooks
```

## What's Next? 🚀

**Now that SuperClaude is installed (that was easy, right?):**

1. **Just start using it** - Try `/analyze some-file.js` or `/build` and see what happens ✨
2. **Don't stress about learning** - SuperClaude usually figures out what you need
3. **Experiment freely** - Commands like `/improve` and `/troubleshoot` are pretty forgiving
4. **Read guides if curious** - Check `Docs/` when you want to understand what just happened
5. **Give feedback** - Let us know what works and what doesn't

**The real secret**: SuperClaude is designed to enhance your existing workflow without you having to learn a bunch of new stuff. Just use it like you'd use regular Claude Code, but notice how much smarter it gets! 🎯

**Still feeling uncertain?** Start with just `/help` and `/analyze README.md` - you'll see how non-intimidating it actually is.

---

## Final Notes 📝

- **Installation takes 1-5 minutes** depending on what you choose
- **Disk space needed: 20-100MB** (not much!)
- **Works alongside existing tools** - doesn't interfere with your setup
- **Easy to uninstall** if you change your mind
- **Community supported** - we actually read and respond to issues
- ### ⚠️ Important Note 
**After installing the SuperClaude.**
**You can use `SuperClaude commands`
, `python3 -m SuperClaude commands` or also `python3 SuperClaude commands`**

Thanks for trying SuperClaude! We hope it makes your development workflow a bit smoother. 🙂

---

*Last updated: July 2024 - Let us know if anything in this guide is wrong or confusing!*
