<div align="center">

# 🚀 SuperClaude Framework

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
  <img src="https://img.shields.io/badge/version-4.2.0-blue" alt="Version">
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

| **Plugins** | **Agents** | **Modes** | **MCP Servers** |
|:------------:|:----------:|:---------:|:---------------:|
| **3** | **16** | **7** | **8** |
| Plugin Commands | Specialized AI | Behavioral | Integrations |

Three core plugins: **PM Agent** (orchestration), **Research** (web search), **Index** (context optimization).

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

### **Project-Local Plugin (Recommended)**

SuperClaude v2.0+ uses **TypeScript plugins** with project-local auto-detection:

```bash
# Clone repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Start Claude Code in this directory
claude
```

**That's it!** `.claude-plugin/` is auto-detected and PM Agent activates on session start.

**Key Features**:
- ✅ **Zero Install**: No copying, no configuration
- ✅ **Hot Reload**: Edit TypeScript → Save → Instant reflection
- ✅ **Auto-Activation**: PM Agent starts automatically (SessionStart hook)
- ✅ **Safe Development**: Separate sandbox from global Claude Code

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

<details>
<summary><b>⚠️ IMPORTANT: Upgrading from SuperClaude V1.x (Slash Commands)</b></summary>

**V2.0 introduces breaking changes - migration from slash commands to TypeScript plugins:**

```bash
# 1. Remove old slash commands (if installed)
rm -rf ~/.claude/commands/sc/

# 2. Use new plugin (project-local)
cd SuperClaude_Framework
claude  # .claude-plugin/ auto-detected
```

**What's New in V2.0:**
- ✅ TypeScript plugins (hot reload support)
- ✅ Project-local detection (zero install)
- ✅ Auto-activation via SessionStart hook
- ✅ 3 core plugins: PM Agent, Research, Index
- ✅ Confidence-driven workflow (≥90% threshold, Precision/Recall 1.0)

**Migration Notes:**
- Old: `/sc:pm`, `/sc:research`, `/sc:index-repo` (27 commands)
- New: `/pm`, `/research`, `/index-repo` (3 plugin commands)
- Installation: Global `~/.claude/commands/` → Project-local `.claude-plugin/`
- Just `cd` to project directory and run `claude`

</details>

<details>
<summary><b>💡 Troubleshooting</b></summary>

**Plugin not loading?**
```bash
# Verify you're in the project directory
pwd  # Should show: /path/to/SuperClaude_Framework

# Check .claude-plugin/ exists
ls .claude-plugin/plugin.json

# Restart Claude Code in this directory
claude
```

**Commands not working (/pm, /research, /index-repo)?**
- Ensure you started `claude` from the SuperClaude_Framework directory
- Check for errors in Claude Code output
- Verify `.claude-plugin/plugin.json` has correct structure

**Hot reload not working?**
- Edit `.claude-plugin/pm/index.ts`
- Save file
- Changes should reflect immediately (no restart needed)

**Development mode (for contributors):**
```bash
# Install Python package for testing
make install
make verify
uv run pytest
```
</details>

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

## 🎉 **What's New in V2.0**

> *Version 2.0 brings architectural transformation: migration from 27 slash commands to 3 TypeScript plugins with hot reload and auto-activation.*

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

### 🔥 **TypeScript Plugins**
**3 core plugins** with hot reload:
- **PM Agent**: Confidence-driven orchestration (≥90% threshold)
- **Research**: Deep web search with adaptive planning
- **Index**: 94% token reduction (58K → 3K)
- Auto-activation via SessionStart hook
- Edit → Save → Instant reflection (no restart)

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP Server Integration**
**8 powerful servers** (via airis-mcp-gateway):
- **Tavily** → Primary web search (Deep Research)
- **Serena** → Session persistence & memory
- **Mindbase** → Cross-session learning (zero-footprint)
- **Sequential** → Token-efficient reasoning
- **Context7** → Official documentation lookup
- **Playwright** → JavaScript-heavy content extraction
- **Magic** → UI component generation
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

### ⚡ **Optimized Performance**
**Smaller framework, bigger projects:**
- Reduced framework footprint
- More context for your code
- Longer conversations possible
- Complex operations enabled

</td>
<td width="50%">

### 📚 **Documentation Overhaul**
**Complete rewrite** for developers:
- Real examples & use cases
- Common pitfalls documented
- Practical workflows included
- Better navigation structure

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

- 🎯 [**Plugin Commands**](docs/user-guide/commands.md)
  *3 core plugin commands*

- 🤖 [**Agents Guide**](docs/user-guide/agents.md)  
  *15 specialized agents*

- 🎨 [**Behavioral Modes**](docs/user-guide/modes.md)  
  *7 adaptive modes*

- 🚩 [**Flags Guide**](docs/user-guide/flags.md)  
  *Control behaviors*

- 🔧 [**MCP Servers**](docs/user-guide/mcp-servers.md)  
  *7 server integrations*

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
