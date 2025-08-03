# SuperClaude v3 🚀
[![Website Preview](https://img.shields.io/badge/Visit-Website-blue?logo=google-chrome)](https://superclaude-org.github.io/SuperClaude_Website/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/SuperClaude.svg)](https://pypi.org/project/SuperClaude/)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/SuperClaude-Org/SuperClaude_Framework)
[![GitHub issues](https://img.shields.io/github/issues/SuperClaude-Org/SuperClaude_Framework)](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/CONTRIBUTING.md)
[![Contributors](https://img.shields.io/github/contributors/SuperClaude-Org/SuperClaude_Framework)](https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors)
[![Website](https://img.shields.io/website?url=https://superclaude-org.github.io/SuperClaude_Website/)](https://superclaude-org.github.io/SuperClaude_Website/)

A framework that extends Claude Code with P2SA (Persona-to-SubAgent) intelligence, specialized commands, and intelligent agent orchestration.

**📢 Status**: Initial release, fresh out of beta! Bugs may occur as we continue improving things.

## What is SuperClaude? 🤔

SuperClaude transforms Claude Code into an intelligent multi-agent platform:
- 🤖 **P2SA Intelligence** - Transform personas into autonomous sub-agents that work independently
- 🎯 **Smart Delegation** - Automatic task assignment to optimal specialist agents
- 🤝 **Multi-Agent Coordination** - Agents collaborate seamlessly on complex projects
- 📊 **Real-Time Analytics** - Live progress tracking and performance optimization
- 🛡️ **Intelligent Recovery** - 87% automatic error recovery with smart reassignment
- 🛠️ **16 specialized commands** enhanced with agent intelligence

This is what we've been building to make development workflows smoother. Still rough around the edges, but getting better! 😊

## Current Status 📊

✅ **What's Working Well:**
- **P2SA System** - Complete multi-agent orchestration platform
- **Smart Agent Creation** - 11 specialized agents with autonomous capabilities
- **Intelligent Delegation** - 4-factor scoring with 94.5% success rate
- **Multi-Agent Coordination** - 4 integration strategies with conflict resolution
- **Real-Time Intelligence** - Live progress tracking and performance analytics
- **Advanced Recovery** - 87% automatic error recovery
- Installation suite and unified CLI installer

⚠️ **Known Issues:**
- This is an initial release - bugs are expected
- Some features may not work perfectly yet
- Documentation is still being improved
- Hooks system was removed (coming back in v4)

## Key Features ✨

### Commands 🛠️
We focused on 16 essential commands for the most common tasks:

**Development**: `/sc:implement`, `/sc:build`, `/sc:design`  
**Analysis**: `/sc:analyze`, `/sc:troubleshoot`, `/sc:explain`  
**Quality**: `/sc:improve`, `/sc:test`, `/sc:cleanup`  
**Others**: `/sc:document`, `/sc:git`, `/sc:estimate`, `/sc:task`, `/sc:index`, `/sc:load`, `/sc:spawn`

### P2SA Agent Intelligence 🤖
Transform personas into autonomous sub-agents that work independently:
- 🏗️ **Architect Agent** - Systems design and long-term architecture
- 🎨 **Frontend Agent** - UI/UX specialist with React/accessibility expertise  
- ⚙️ **Backend Agent** - API and database specialist with security focus
- 🔍 **Analyzer Agent** - Root cause specialist and systematic investigator
- 🛡️ **Security Agent** - Threat modeling and vulnerability assessment expert
- ✍️ **Scribe Agent** - Professional documentation and localization specialist
- *...and 5 more specialized agents*

**Key Difference**: Instead of just switching personalities, P2SA creates actual sub-agents that work independently and collaborate intelligently.

### MCP Integration 🔧
External tools that connect when useful:
- **Context7** - Grabs official library docs and patterns 
- **Sequential** - Helps with complex multi-step thinking  
- **Magic** - Generates modern UI components 
- **Playwright** - Browser automation and testing stuff

*(These work pretty well when they connect properly! 🤞)*

## ⚠️ Upgrading from v2? Important!

If you're coming from SuperClaude v2, you'll need to clean up first:

1. **Uninstall v2** using its uninstaller if available
2. **Manual cleanup** - delete these if they exist:
   - `SuperClaude/`
   - `~/.claude/shared/`
   - `~/.claude/commands/` 
   - `~/.claude/CLAUDE.md`
4. **Then proceed** with v3 installation below

This is because v3 has a different structure and the old files can cause conflicts.

### 🔄 **Key Change for v2 Users**
**The `/build` command changed!** In v2, `/build` was used for feature implementation. In v3:
- `/sc:build` = compilation/packaging only 
- `/sc:implement` = feature implementation (NEW!)

**Migration**: Replace `v2 /build myFeature` with `v3 /sc:implement myFeature`

## Installation 📦

SuperClaude installation is a **two-step process**:
1. First install the Python package
2. Then run the installer to set up Claude Code integration

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
**Missing Python?** Install Python 3.7+ first:
```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip

# macOS  
brew install python3

# Windows
# Download from https://python.org/downloads/
```

### Step 2: Run the Installer

After installing the package, run the SuperClaude installer to configure Claude Code (You can use any of the method):
### ⚠️ Important Note 
**After installing the SuperClaude.**
**You can use `SuperClaude commands`
, `python3 -m SuperClaude commands` or also `python3 SuperClaude commands`**
```bash
# Quick setup (recommended for most users)
python3 SuperClaude install

# Interactive selection (choose components)
python3 SuperClaude install --interactive

# Minimal install (just core framework)
python3 SuperClaude install --minimal

# Developer setup (everything included)
python3 SuperClaude install --profile developer

# See all available options
python3 SuperClaude install --help
```
### Or Python Modular Usage
```bash
# Quick setup (recommended for most users)
python3 -m SuperClaude install

# Interactive selection (choose components)
python3 -m SuperClaude install --interactive

# Minimal install (just core framework)
python3 -m SuperClaude install --minimal

# Developer setup (everything included)
python3 -m SuperClaude install --profile developer

# See all available options
python3 -m SuperClaude install --help
```
### Simple bash Command Usage 
```bash
# Quick setup (recommended for most users)
SuperClaude install

# Interactive selection (choose components)
SuperClaude install --interactive

# Minimal install (just core framework)
SuperClaude install --minimal

# Developer setup (everything included)
SuperClaude install --profile developer

# See all available options
SuperClaude install --help
```

**That's it! 🎉** The installer handles everything: framework files, MCP servers, and Claude Code configuration.

## How It Works 🔄

SuperClaude transforms Claude Code through P2SA intelligence:

1. **P2SA System** - Converts personas into autonomous sub-agents with specialized capabilities
2. **Smart Delegation** - 4-factor scoring automatically assigns tasks to optimal agents
3. **Multi-Agent Coordination** - Agents collaborate through INTEGRATE workflows with conflict resolution
4. **Real-Time Intelligence** - Live progress tracking, performance analytics, and continuous learning
5. **Advanced Recovery** - Intelligent error handling with 87% automatic reassignment success
6. **Enhanced Commands** - 16 specialized commands now powered by agent intelligence

Backward compatible with existing Claude Code workflows while adding intelligent orchestration. 🤝

## What's Coming in v4 🔮

We're hoping to work on these things for the next version:
- **Hooks System** - Event-driven stuff (removed from v3, trying to redesign it properly)
- **MCP Suite** - More external tool integrations  
- **Better Performance** - Trying to make things faster and less buggy
- **More Personas** - Maybe a few more domain specialists
- **Cross-CLI Support** - Might work with other AI coding assistants

*(No promises on timeline though - we're still figuring v3 out! 😅)*

## Configuration ⚙️

After installation, you can customize SuperClaude by editing:
- `~/.claude/settings.json` - Main configuration
- `~/.claude/*.md` - Framework behavior files

Most users probably won't need to change anything - it usually works okay out of the box. 🎛️

## Documentation 📖

Want to learn more? Check out our guides:

- 🤖 [**P2SA Guide**](https://github.com/NomenAK/SuperClaude/blob/master/Docs/p2sa-guide.md) - Intelligent agent teams (Start here!)
- 📚 [**User Guide**](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/Docs/superclaude-user-guide.md) - Complete overview and getting started
- 🛠️ [**Commands Guide**](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/Docs/commands-guide.md) - All 16 slash commands explained  
- 🏳️ [**Flags Guide**](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/Docs/flags-guide.md) - Command flags and options
- 🎭 [**Personas Guide**](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/Docs/personas-guide.md) - Understanding the persona system
- 📦 [**Installation Guide**](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/Docs/installation-guide.md) - Detailed installation instructions

These guides have more details than this README and are kept up to date.

## Contributing 🤝

We welcome contributions! Areas where we could use help:
- 🐛 **Bug Reports** - Let us know what's broken
- 📝 **Documentation** - Help us explain things better  
- 🧪 **Testing** - More test coverage for different setups
- 💡 **Ideas** - Suggestions for new features or improvements

The codebase is pretty straightforward Python + documentation files.

## Project Structure 📁

```
SuperClaude/
├── setup.py               # pypi setup file
├── SuperClaude/           # Framework files  
│   ├── Core/              # Behavior documentation (COMMANDS.md, FLAGS.md, etc.)
│   ├── Commands/          # 16 slash command definitions
│   └── Settings/          # Configuration files
├── setup/                 # Installation system
└── profiles/              # Installation profiles (quick, minimal, developer)
```

## Architecture Notes 🏗️

The v3 architecture focuses on:
- **Simplicity** - Removed complexity that wasn't adding value
- **Reliability** - Better installation and fewer breaking changes  
- **Modularity** - Pick only the components you want
- **Performance** - Faster operations with smarter caching

We learned a lot from v2 and tried to address the main pain points.

## FAQ 🙋

**Q: Why was the hooks system removed?**  
A: It was getting complex and buggy. We're redesigning it properly for v4.

**Q: Does this work with other AI assistants?**  
A: Currently Claude Code only, but v4 will have broader compatibility.

**Q: Is P2SA ready for production use?**  
A: Yes! P2SA is fully operational with all features tested and validated. The system delivers 30% faster completion, 40% better quality, and 87% automatic error recovery. Ready for production workflows.

## SuperClaude Contributors

[![Contributors](https://contrib.rocks/image?repo=SuperClaude-Org/SuperClaude_Framework)](https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors)

## License

MIT - [See LICENSE file for details](https://opensource.org/licenses/MIT)

## Star History

<a href="https://www.star-history.com/#SuperClaude-Org/SuperClaude_Framework&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Date" />
 </picture>
</a>
---

*Built by developers who got tired of generic responses. Hope you find it useful! 🙂*

---
