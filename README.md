<div align="center">

# 🚀 SuperClaude Framework

### **Transform Claude Code into a Structured Development Platform**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.0.8-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://superclaude.netlify.app/">
    <img src="https://img.shields.io/badge/🌐_Visit_Website-blue" alt="Website">
  </a>
  <a href="https://pypi.org/project/SuperClaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
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
| **21** | **14** | **5** | **6** |
| Slash Commands | Specialized AI | Behavioral | Integrations |

</div>

---

<div align="center">

## 🎯 **Overview**

SuperClaude is a **meta-programming configuration framework** that transforms Claude Code into a structured development platform through behavioral instruction injection and component orchestration. It provides systematic workflow automation with powerful tools and intelligent agents.

## ⚡ **Quick Installation**

### **Choose Your Installation Method**

| Method | Command | Best For |
|:------:|---------|----------|
| **🐍 pipx** | `pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install` | **✅ Recommended** - Linux/macOS |
| **📦 pip** | `pip install SuperClaude && pip upgrade SuperClaude && SuperClaude install` | Traditional Python environments |
| **🌐 npm** | `npm install -g @bifrost_inc/superclaude && superclaude install` | Cross-platform, Node.js users |

</div>

<details>
<summary><b>⚠️ IMPORTANT: Upgrading from SuperClaude V3</b></summary>

**If you have SuperClaude V3 installed, you SHOULD uninstall it before installing V4:**

```bash
# Uninstall V3 first
Remove all related files and directories :
*.md *.json and commands/

# Then install V4
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

**✅ What gets preserved during upgrade:**
- ✓ Your custom slash commands (outside `commands/sc/`)
- ✓ Your custom content in `CLAUDE.md` 
- ✓ Claude Code's `.claude.json`, `.credentials.json`, `settings.json` and `settings.local.json`
- ✓ Any custom agents and files you've added

**⚠️ Note:** Other SuperClaude-related `.json` files from V3 may cause conflicts and should be removed.

</details>

<details>
<summary><b>💡 Troubleshooting PEP 668 Errors</b></summary>

```bash
# Option 1: Use pipx (Recommended)
pipx install SuperClaude

# Option 2: User installation
pip install --user SuperClaude

# Option 3: Force installation (use with caution)
pip install --break-system-packages SuperClaude
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

## 🎉 **What's New in V4**

> *Version 4 brings significant improvements based on community feedback and real-world usage patterns.*

<table>
<tr>
<td width="50%">

### 🤖 **Smarter Agent System**
**14 specialized agents** with domain expertise:
- Security engineer catches real vulnerabilities
- Frontend architect understands UI patterns
- Automatic coordination based on context
- Domain-specific expertise on demand

</td>
<td width="50%">

### 📝 **Improved Namespace**
**`/sc:` prefix** for all commands:
- No conflicts with custom commands
- 21 commands covering full lifecycle
- From brainstorming to deployment
- Clean, organized command structure

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP Server Integration**
**6 powerful servers** working together:
- **Context7** → Up-to-date documentation
- **Sequential** → Complex analysis
- **Magic** → UI component generation
- **Playwright** → Browser testing
- **Morphllm** → Bulk transformations
- **Serena** → Session persistence

</td>
<td width="50%">

### 🎯 **Behavioral Modes**
**5 adaptive modes** for different contexts:
- **Brainstorming** → Asks right questions
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

- 📝 [**Quick Start Guide**](Docs/Getting-Started/quick-start.md)  
  *Get up and running fast*

- 💾 [**Installation Guide**](Docs/Getting-Started/installation.md)  
  *Detailed setup instructions*

</td>
<td valign="top">

- 🎯 [**Commands Reference**](Docs/User-Guide/commands.md)  
  *All 21 slash commands*

- 🤖 [**Agents Guide**](Docs/User-Guide/agents.md)  
  *14 specialized agents*

- 🎨 [**Behavioral Modes**](Docs/User-Guide/modes.md)  
  *5 adaptive modes*

- 🚩 [**Flags Guide**](Docs/User-Guide/flags.md)  
  *Control behaviors*

- 🔧 [**MCP Servers**](Docs/User-Guide/mcp-servers.md)  
  *6 server integrations*

- 💼 [**Session Management**](Docs/User-Guide/session-management.md)  
  *Save & restore state*

</td>
<td valign="top">

- 🏗️ [**Technical Architecture**](Docs/Developer-Guide/technical-architecture.md)  
  *System design details*

- 💻 [**Contributing Code**](Docs/Developer-Guide/contributing-code.md)  
  *Development workflow*

- 🧪 [**Testing & Debugging**](Docs/Developer-Guide/testing-debugging.md)  
  *Quality assurance*

</td>
<td valign="top">

- ✨ [**Best Practices**](Docs/Reference/quick-start-practices.md)  
  *Pro tips & patterns*

- 📓 [**Examples Cookbook**](Docs/Reference/examples-cookbook.md)  
  *Real-world recipes*

- 🔍 [**Troubleshooting**](Docs/Reference/troubleshooting.md)  
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
