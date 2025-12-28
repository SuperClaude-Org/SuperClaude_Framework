<div align="center">

# 🚀 SuperClaude Framework

[![Run in Smithery](https://smithery.ai/badge/skills/SuperClaude-Org)](https://smithery.ai/skills?ns=SuperClaude-Org&utm_source=github&utm_medium=badge)


### **Transform Claude Code into a Structured Development Platform**

<p align="center">
  <a href="https://github.com/hesreallyhim/awesome-claude-code/">
  <img src="https://awesome.re/mentioned-badge-flat.svg" alt="Mentioned in Awesome Claude Code">
  </a>
<a href="https://github.com/SuperClaude-Org/SuperGemini_Framework" target="_blank">
  <img src="https://img.shields.io/badge/Try-SuperGemini_Framework-blue" alt="Try SuperGemini Framework"/>
</a>
<a href="https://github.com/SuperClaude-Org/SuperQwen_Framework" target="_blank">
  <img src="https://img.shields.io/badge/Try-SuperQwen_Framework-orange" alt="Try SuperQwen Framework"/>
</a>
  <img src="https://img.shields.io/badge/version-4.1.9-blue" alt="Version">
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml">
    <img src="https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://superclaude.netlify.app/">
    <img src="https://img.shields.io/badge/🌐_Visit_Website-blue" alt="Website">
  </a>
  <a href="https://pypi.org/project/superclaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
  </a>
  <a href="https://pepy.tech/projects/superclaude">
    <img src="https://static.pepy.tech/personalized-badge/superclaude?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI sats">
  </a>
  <a href="https://www.npmjs.com/package/@bifrost_inc/superclaude">
    <img src="https://img.shields.io/npm/v/@bifrost_inc/superclaude.svg" alt="npm">
  </a>
</p>

<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇸_English-blue" alt="English">
  </a>
  <a href="README-zh.md">
    <img src="https://img.shields.io/badge/🇨🇳_中文-red" alt="中文">
  </a>
  <a href="README-ja.md">
    <img src="https://img.shields.io/badge/🇯🇵_日本語-green" alt="日本語">
  </a>
</p>

<p align="center">
  <a href="#-quick-installation">Quick Start</a> •
  <a href="#-support-the-project">Support</a> •
  <a href="#-whats-new-in-v4">Features</a> •
  <a href="#-documentation">Docs</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

<div align="center">

## 📊 **Framework Statistics**

| **Commands** | **Agents** | **Modes** | **MCP Servers** |
|:------------:|:----------:|:---------:|:---------------:|
| **30** | **16** | **7** | **8** |
| Slash Commands | Specialized AI | Behavioral | Integrations |

30 slash commands covering the complete development lifecycle from brainstorming to deployment.

</div>

---

<div align="center">

## 🎯 **Overview**

SuperClaude is a **meta-programming configuration framework** that transforms Claude Code into a structured development platform through behavioral instruction injection and component orchestration. It provides systematic workflow automation with powerful tools and intelligent agents.


## Disclaimer

This project is not affiliated with or endorsed by Anthropic.
Claude Code is a product built and maintained by [Anthropic](https://www.anthropic.com/).

## 📖 **For Developers & Contributors**

**Essential documentation for working with SuperClaude Framework:**

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[PLANNING.md](PLANNING.md)** | Architecture, design principles, absolute rules | Session start, before implementation |
| **[TASK.md](TASK.md)** | Current tasks, priorities, backlog | Daily, before starting work |
| **[KNOWLEDGE.md](KNOWLEDGE.md)** | Accumulated insights, best practices, troubleshooting | When encountering issues, learning patterns |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution guidelines, workflow | Before submitting PRs |

> **💡 Pro Tip**: Claude Code reads these files at session start to ensure consistent, high-quality development aligned with project standards.

## ⚡ **Quick Installation**

> **IMPORTANT**: The TypeScript plugin system described in older documentation is
> not yet available (planned for v5.0). For current installation
> instructions, please follow the steps below for v4.x.

### **Current Stable Version (v4.1.9)**

SuperClaude currently uses slash commands.

**Option 1: pipx (Recommended)**
```bash
# Install from PyPI
pipx install superclaude

# Install commands (installs all 30 slash commands)
superclaude install

# Install MCP servers (optional, for enhanced capabilities)
superclaude mcp --list         # List available MCP servers
superclaude mcp                # Interactive installation
superclaude mcp --servers tavily --servers context7  # Install specific servers

# Verify installation
superclaude install --list
superclaude doctor
```

After installation, restart Claude Code to use 30 commands including:
- `/sc:research` - Deep web research (enhanced with Tavily MCP)
- `/sc:brainstorm` - Structured brainstorming
- `/sc:implement` - Code implementation
- `/sc:test` - Testing workflows
- `/sc:pm` - Project management
- `/sc` - Show all 30 available commands

**Option 2: Direct Installation from Git**
```bash
# Clone the repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Run the installation script
./install.sh
```

### **Coming in v5.0 (In Development)**

We are actively working on a new TypeScript plugin system (see issue [#419](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/419) for details). When released, installation will be simplified to:

```bash
# This feature is not yet available
/plugin marketplace add SuperClaude-Org/superclaude-plugin-marketplace
/plugin install superclaude
```

**Status**: In development. No ETA has been set.

### **Enhanced Performance (Optional MCPs)**

For **2-3x faster** execution and **30-50% fewer tokens**, optionally install MCP servers:

```bash
# Optional MCP servers for enhanced performance (via airis-mcp-gateway):
# - Serena: Code understanding (2-3x faster)
# - Sequential: Token-efficient reasoning (30-50% fewer tokens)
# - Tavily: Web search for Deep Research
# - Context7: Official documentation lookup
# - Mindbase: Semantic search across all conversations (optional enhancement)

# Note: Error learning available via built-in ReflexionMemory (no installation required)
# Mindbase provides semantic search enhancement (requires "recommended" profile)
# Install MCP servers: https://github.com/agiletec-inc/airis-mcp-gateway
# See docs/mcp/mcp-integration-policy.md for details
```

**Performance Comparison:**
- **Without MCPs**: Fully functional, standard performance ✅
- **With MCPs**: 2-3x faster, 30-50% fewer tokens ⚡

</div>

---

<div align="center">

## 💖 **Support the Project**

> Hey, let's be real - maintaining SuperClaude takes time and resources.
> 
> *The Claude Max subscription alone runs $100/month for testing, and that's before counting the hours spent on documentation, bug fixes, and feature development.*
> *If you're finding value in SuperClaude for your daily work, consider supporting the project.*
> *Even a few dollars helps cover the basics and keeps development active.*
> 
> Every contributor matters, whether through code, feedback, or support. Thanks for being part of this community! 🙏

<table>
<tr>
<td align="center" width="33%">
  
### ☕ **Ko-fi**
[![Ko-fi](https://img.shields.io/badge/Support_on-Ko--fi-ff5e5b?logo=ko-fi)](https://ko-fi.com/superclaude)

*One-time contributions*

</td>
<td align="center" width="33%">

### 🎯 **Patreon**
[![Patreon](https://img.shields.io/badge/Become_a-Patron-f96854?logo=patreon)](https://patreon.com/superclaude)

*Monthly support*

</td>
<td align="center" width="33%">

### 💜 **GitHub**
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsor-30363D?logo=github-sponsors)](https://github.com/sponsors/SuperClaude-Org)

*Flexible tiers*

</td>
</tr>
</table>

### **Your Support Enables:**

| Item | Cost/Impact |
|------|-------------|
| 🔬 **Claude Max Testing** | $100/month for validation & testing |
| ⚡ **Feature Development** | New capabilities & improvements |
| 📚 **Documentation** | Comprehensive guides & examples |
| 🤝 **Community Support** | Quick issue responses & help |
| 🔧 **MCP Integration** | Testing new server connections |
| 🌐 **Infrastructure** | Hosting & deployment costs |

> **Note:** No pressure though - the framework stays open source regardless. Just knowing people use and appreciate it is motivating. Contributing code, documentation, or spreading the word helps too! 🙏

</div>

---

<div align="center">

## 🎉 **What's New in v4.1**

> *Version 4.1 focuses on stabilizing the slash command architecture, enhancing agent capabilities, and improving documentation.*

<table>
<tr>
<td width="50%">

### 🤖 **Smarter Agent System**
**16 specialized agents** with domain expertise:
- PM Agent ensures continuous learning through systematic documentation
- Deep Research agent for autonomous web research
- Security engineer catches real vulnerabilities
- Frontend architect understands UI patterns
- Automatic coordination based on context
- Domain-specific expertise on demand

</td>
<td width="50%">

### ⚡ **Optimized Performance**
**Smaller framework, bigger projects:**
- Reduced framework footprint
- More context for your code
- Longer conversations possible
- Complex operations enabled

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP Server Integration**
**8 powerful servers** with easy CLI installation:

```bash
# List available MCP servers
superclaude mcp --list

# Install specific servers
superclaude mcp --servers tavily context7

# Interactive installation
superclaude mcp
```

**Available servers:**
- **Tavily** → Primary web search (Deep Research)
- **Context7** → Official documentation lookup
- **Sequential-Thinking** → Multi-step reasoning
- **Serena** → Session persistence & memory
- **Playwright** → Cross-browser automation
- **Magic** → UI component generation
- **Morphllm-Fast-Apply** → Context-aware code modifications
- **Chrome DevTools** → Performance analysis

</td>
<td width="50%">

### 🎯 **Behavioral Modes**
**7 adaptive modes** for different contexts:
- **Brainstorming** → Asks right questions
- **Business Panel** → Multi-expert strategic analysis
- **Deep Research** → Autonomous web research
- **Orchestration** → Efficient tool coordination
- **Token-Efficiency** → 30-50% context savings
- **Task Management** → Systematic organization
- **Introspection** → Meta-cognitive analysis

</td>
</tr>
<tr>
<td width="50%">

### 📚 **Documentation Overhaul**
**Complete rewrite** for developers:
- Real examples & use cases
- Common pitfalls documented
- Practical workflows included
- Better navigation structure

</td>
<td width="50%">

### 🧪 **Enhanced Stability**
**Focus on reliability:**
- Bug fixes for core commands
- Improved test coverage
- More robust error handling
- CI/CD pipeline improvements

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🔬 **Deep Research Capabilities**

### **Autonomous Web Research Aligned with DR Agent Architecture**

SuperClaude v4.2 introduces comprehensive Deep Research capabilities, enabling autonomous, adaptive, and intelligent web research.

<table>
<tr>
<td width="50%">

### 🎯 **Adaptive Planning**
**Three intelligent strategies:**
- **Planning-Only**: Direct execution for clear queries
- **Intent-Planning**: Clarification for ambiguous requests
- **Unified**: Collaborative plan refinement (default)

</td>
<td width="50%">

### 🔄 **Multi-Hop Reasoning**
**Up to 5 iterative searches:**
- Entity expansion (Paper → Authors → Works)
- Concept deepening (Topic → Details → Examples)
- Temporal progression (Current → Historical)
- Causal chains (Effect → Cause → Prevention)

</td>
</tr>
<tr>
<td width="50%">

### 📊 **Quality Scoring**
**Confidence-based validation:**
- Source credibility assessment (0.0-1.0)
- Coverage completeness tracking
- Synthesis coherence evaluation
- Minimum threshold: 0.6, Target: 0.8

</td>
<td width="50%">

### 🧠 **Case-Based Learning**
**Cross-session intelligence:**
- Pattern recognition and reuse
- Strategy optimization over time
- Successful query formulations saved
- Performance improvement tracking

</td>
</tr>
</table>

### **Research Command Usage**

```bash
# Basic research with automatic depth
/research "latest AI developments 2024"

# Controlled research depth (via options in TypeScript)
/research "quantum computing breakthroughs"  # depth: exhaustive

# Specific strategy selection
/research "market analysis"  # strategy: planning-only

# Domain-filtered research (Tavily MCP integration)
/research "React patterns"  # domains: reactjs.org,github.com
```

### **Research Depth Levels**

| Depth | Sources | Hops | Time | Best For |
|:-----:|:-------:|:----:|:----:|----------|
| **Quick** | 5-10 | 1 | ~2min | Quick facts, simple queries |
| **Standard** | 10-20 | 3 | ~5min | General research (default) |
| **Deep** | 20-40 | 4 | ~8min | Comprehensive analysis |
| **Exhaustive** | 40+ | 5 | ~10min | Academic-level research |

### **Integrated Tool Orchestration**

The Deep Research system intelligently coordinates multiple tools:
- **Tavily MCP**: Primary web search and discovery
- **Playwright MCP**: Complex content extraction
- **Sequential MCP**: Multi-step reasoning and synthesis
- **Serena MCP**: Memory and learning persistence
- **Context7 MCP**: Technical documentation lookup

</div>

---

<div align="center">

## 📚 **Documentation**

### **Complete Guide to SuperClaude**

<table>
<tr>
<th align="center">🚀 Getting Started</th>
<th align="center">📖 User Guides</th>
<th align="center">🛠️ Developer Resources</th>
<th align="center">📋 Reference</th>
</tr>
<tr>
<td valign="top">

- 📝 [**Quick Start Guide**](docs/getting-started/quick-start.md)  
  *Get up and running fast*

- 💾 [**Installation Guide**](docs/getting-started/installation.md)  
  *Detailed setup instructions*

</td>
<td valign="top">

- 🎯 [**Slash Commands**](docs/reference/commands-list.md)
  *All 30 commands organized by category*

- 🤖 [**Agents Guide**](docs/user-guide/agents.md)  
  *16 specialized agents*

- 🎨 [**Behavioral Modes**](docs/user-guide/modes.md)  
  *7 adaptive modes*

- 🚩 [**Flags Guide**](docs/user-guide/flags.md)  
  *Control behaviors*

- 🔧 [**MCP Servers**](docs/user-guide/mcp-servers.md)  
  *8 server integrations*

- 💼 [**Session Management**](docs/user-guide/session-management.md)  
  *Save & restore state*

</td>
<td valign="top">

- 🏗️ [**Technical Architecture**](docs/developer-guide/technical-architecture.md)  
  *System design details*

- 💻 [**Contributing Code**](docs/developer-guide/contributing-code.md)  
  *Development workflow*

- 🧪 [**Testing & Debugging**](docs/developer-guide/testing-debugging.md)  
  *Quality assurance*

</td>
<td valign="top">
- 📓 [**Examples Cookbook**](docs/reference/examples-cookbook.md)  
  *Real-world recipes*

- 🔍 [**Troubleshooting**](docs/reference/troubleshooting.md)  
  *Common issues & fixes*

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🤝 **Contributing**

### **Join the SuperClaude Community**

We welcome contributions of all kinds! Here's how you can help:

| Priority | Area | Description |
|:--------:|------|-------------|
| 📝 **High** | Documentation | Improve guides, add examples, fix typos |
| 🔧 **High** | MCP Integration | Add server configs, test integrations |
| 🎯 **Medium** | Workflows | Create command patterns & recipes |
| 🧪 **Medium** | Testing | Add tests, validate features |
| 🌐 **Low** | i18n | Translate docs to other languages |

<p align="center">
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/📖_Read-Contributing_Guide-blue" alt="Contributing Guide">
  </a>
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors">
    <img src="https://img.shields.io/badge/👥_View-All_Contributors-green" alt="Contributors">
  </a>
</p>

</div>

---

<div align="center">

## ⚖️ **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?" alt="MIT License">
</p>

</div>

---

<div align="center">

## ⭐ **Star History**

<a href="https://www.star-history.com/#SuperClaude-Org/SuperClaude_Framework&Timeline">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=SuperClaude-Org/SuperClaude_Framework&type=Timeline" />
 </picture>
</a>


</div>

---

<div align="center">

### **🚀 Built with passion by the SuperClaude community**

<p align="center">
  <sub>Made with ❤️ for developers who push boundaries</sub>
</p>

<p align="center">
  <a href="#-superclaude-framework">Back to Top ↑</a>
</p>

</div>

---

## 📋 **All 30 Commands**

<details>
<summary><b>Click to expand full command list</b></summary>

### 🧠 Planning & Design (4)
- `/brainstorm` - Structured brainstorming
- `/design` - System architecture
- `/estimate` - Time/effort estimation
- `/spec-panel` - Specification analysis

### 💻 Development (5)
- `/implement` - Code implementation
- `/build` - Build workflows
- `/improve` - Code improvements
- `/cleanup` - Refactoring
- `/explain` - Code explanation

### 🧪 Testing & Quality (4)
- `/test` - Test generation
- `/analyze` - Code analysis
- `/troubleshoot` - Debugging
- `/reflect` - Retrospectives

### 📚 Documentation (2)
- `/document` - Doc generation
- `/help` - Command help

### 🔧 Version Control (1)
- `/git` - Git operations

### 📊 Project Management (3)
- `/pm` - Project management
- `/task` - Task tracking
- `/workflow` - Workflow automation

### 🔍 Research & Analysis (2)
- `/research` - Deep web research
- `/business-panel` - Business analysis

### 🎯 Utilities (9)
- `/agent` - AI agents
- `/index-repo` - Repository indexing
- `/index` - Indexing alias
- `/recommend` - Command recommendations
- `/select-tool` - Tool selection
- `/spawn` - Parallel tasks
- `/load` - Load sessions
- `/save` - Save sessions
- `/sc` - Show all commands

[**📖 View Detailed Command Reference →**](docs/reference/commands-list.md)

</details>

