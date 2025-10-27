<div align="center">

# 🚀 SuperClaude 框架

### **将Claude Code转换为结构化开发平台**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.5-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://superclaude.netlify.app/">
    <img src="https://img.shields.io/badge/🌐_访问网站-blue" alt="Website">
  </a>
  <a href="https://pypi.org/project/superclaude/">
    <img src="https://img.shields.io/pypi/v/SuperClaude.svg?" alt="PyPI">
  </a>
  <a href="https://www.npmjs.com/package/@bifrost_inc/superclaude">
    <img src="https://img.shields.io/npm/v/@bifrost_inc/superclaude.svg" alt="npm">
  </a>
</p>

<!-- Language Selector -->
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
  <a href="#-快速安装">快速开始</a> •
  <a href="#-支持项目">支持项目</a> •
  <a href="#-v4版本新功能">新功能</a> •
  <a href="#-文档">文档</a> •
  <a href="#-贡献">贡献</a>
</p>

</div>

---

<div align="center">

## 📊 **框架统计**

| **命令数** | **智能体** | **模式** | **MCP服务器** |
|:------------:|:----------:|:---------:|:---------------:|
| **21** | **14** | **5** | **6** |
| 斜杠命令 | 专业AI | 行为模式 | 集成服务 |

</div>

---

<div align="center">

## 🎯 **概述**

SuperClaude是一个**元编程配置框架**，通过行为指令注入和组件编排，将Claude Code转换为结构化开发平台。它提供系统化的工作流自动化，配备强大的工具和智能代理。

## ⚡ **快速安装**

### **选择您的安装方式**

| 方式 | 命令 | 最适合 |
|:------:|---------|----------|
| **🐍 pipx** | `pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install` | **✅ 推荐** - Linux/macOS |
| **📦 pip** | `pip install SuperClaude && pip upgrade SuperClaude && SuperClaude install` | 传统Python环境 |
| **🌐 npm** | `npm install -g @bifrost_inc/superclaude && superclaude install` | 跨平台，Node.js用户 |

</div>

<details>
<summary><b>⚠️ 重要：从SuperClaude V3升级</b></summary>

**如果您已安装SuperClaude V3，应在安装V4前先卸载它：**

```bash
# 先卸载V3
删除所有相关文件和目录：
*.md *.json 和 commands/

# 然后安装V4
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

**✅ 升级时保留的内容：**
- ✓ 您的自定义斜杠命令（`commands/sc/`之外的）
- ✓ 您在`CLAUDE.md`中的自定义内容
- ✓ Claude Code的`.claude.json`、`.credentials.json`、`settings.json`和`settings.local.json`
- ✓ 您添加的任何自定义代理和文件

**⚠️ 注意：** V3的其他SuperClaude相关`.json`文件可能会造成冲突，应当移除。

</details>

<details>
<summary><b>💡 PEP 668错误故障排除</b></summary>

```bash
# 选项1：使用pipx（推荐）
pipx install SuperClaude

# 选项2：用户安装
pip install --user SuperClaude

# 选项3：强制安装（谨慎使用）
pip install --break-system-packages SuperClaude
```
</details>

---

<div align="center">

## 💖 **支持项目**

> 说实话，维护SuperClaude需要时间和资源。
> 
> *仅Claude Max订阅每月就要100美元用于测试，这还不包括在文档、bug修复和功能开发上花费的时间。*
> *如果您在日常工作中发现SuperClaude的价值，请考虑支持这个项目。*
> *哪怕几美元也能帮助覆盖基础成本并保持开发活跃。*
> 
> 每个贡献者都很重要，无论是代码、反馈还是支持。感谢成为这个社区的一员！🙏

<table>
<tr>
<td align="center" width="33%">
  
### ☕ **Ko-fi**
[![Ko-fi](https://img.shields.io/badge/Support_on-Ko--fi-ff5e5b?logo=ko-fi)](https://ko-fi.com/superclaude)

*一次性贡献*

</td>
<td align="center" width="33%">

### 🎯 **Patreon**
[![Patreon](https://img.shields.io/badge/Become_a-Patron-f96854?logo=patreon)](https://patreon.com/superclaude)

*月度支持*

</td>
<td align="center" width="33%">

### 💜 **GitHub**
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsor-30363D?logo=github-sponsors)](https://github.com/sponsors/SuperClaude-Org)

*灵活层级*

</td>
</tr>
</table>

### **您的支持使以下工作成为可能：**

| 项目 | 成本/影响 |
|------|-------------|
| 🔬 **Claude Max测试** | 每月100美元用于验证和测试 |
| ⚡ **功能开发** | 新功能和改进 |
| 📚 **文档编写** | 全面的指南和示例 |
| 🤝 **社区支持** | 快速问题响应和帮助 |
| 🔧 **MCP集成** | 测试新服务器连接 |
| 🌐 **基础设施** | 托管和部署成本 |

> **注意：** 不过没有压力——无论如何框架都会保持开源。仅仅知道有人在使用和欣赏它就很有激励作用。贡献代码、文档或传播消息也很有帮助！🙏

</div>

---

<div align="center">

## 🎉 **V4版本新功能**

> *第4版基于社区反馈和实际使用模式带来了重大改进。*

<table>
<tr>
<td width="50%">

### 🤖 **更智能的代理系统**
**14个专业代理**，具有领域专业知识：
- 安全工程师发现真实漏洞
- 前端架构师理解UI模式
- 基于上下文的自动协调
- 按需提供领域专业知识

</td>
<td width="50%">

### 📝 **改进的命名空间**
**`/sc:`前缀**用于所有命令：
- 与自定义命令无冲突
- 21个命令覆盖完整生命周期
- 从头脑风暴到部署
- 清晰有序的命令结构

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP服务器集成**
**6个强大服务器**协同工作：
- **Context7** → 最新文档
- **Sequential** → 复杂分析
- **Magic** → UI组件生成
- **Playwright** → 浏览器测试
- **Morphllm** → 批量转换
- **Serena** → 会话持久化

</td>
<td width="50%">

### 🎯 **行为模式**
**5种自适应模式**适应不同上下文：
- **头脑风暴** → 提出正确问题
- **编排** → 高效工具协调
- **令牌效率** → 30-50%上下文节省
- **任务管理** → 系统化组织
- **内省** → 元认知分析

</td>
</tr>
<tr>
<td width="50%">

### ⚡ **优化性能**
**更小的框架，更大的项目：**
- 减少框架占用
- 为您的代码提供更多上下文
- 支持更长对话
- 启用复杂操作

</td>
<td width="50%">

### 📚 **文档全面改写**
**为开发者完全重写：**
- 真实示例和用例
- 记录常见陷阱
- 包含实用工作流
- 更好的导航结构

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
<th align="center">🚀 快速开始</th>
<th align="center">📖 用户指南</th>
<th align="center">🛠️ 开发资源</th>
<th align="center">📋 参考资料</th>
</tr>
<tr>
<td valign="top">

- 📝 [**快速开始指南**](docs/getting-started/quick-start.md)  
  *快速上手使用*

- 💾 [**安装指南**](docs/getting-started/installation.md)  
  *详细的安装说明*

</td>
<td valign="top">

- 🎯 [**命令参考**](docs/user-guide-zh/commands.md)  
  *全部21个斜杠命令*

- 🤖 [**智能体指南**](docs/user-guide-zh/agents.md)  
  *14个专业智能体*

- 🎨 [**行为模式**](docs/user-guide-zh/modes.md)  
  *5种自适应模式*

- 🚩 [**标志指南**](docs/user-guide-zh/flags.md)  
  *控制行为参数*

- 🔧 [**MCP服务器**](docs/user-guide-zh/mcp-servers.md)  
  *6个服务器集成*

- 💼 [**会话管理**](docs/user-guide-zh/session-management.md)  
  *保存和恢复状态*

</td>
<td valign="top">

- 🏗️ [**技术架构**](docs/developer-guide/technical-architecture.md)  
  *系统设计详情*

- 💻 [**贡献代码**](docs/developer-guide/contributing-code.md)  
  *开发工作流程*

- 🧪 [**测试与调试**](docs/developer-guide/testing-debugging.md)  
  *质量保证*

</td>
<td valign="top">

- ✨ [**最佳实践**](docs/reference/quick-start-practices.md)  
  *专业技巧和模式*

- 📓 [**示例手册**](docs/reference/examples-cookbook.md)  
  *实际应用示例*

- 🔍 [**故障排除**](docs/reference/troubleshooting.md)  
  *常见问题和修复*

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🤝 **贡献**

### **加入SuperClaude社区**

我们欢迎各种类型的贡献！以下是您可以帮助的方式：

| 优先级 | 领域 | 描述 |
|:--------:|------|-------------|
| 📝 **高** | 文档 | 改进指南，添加示例，修复错误 |
| 🔧 **高** | MCP集成 | 添加服务器配置，测试集成 |
| 🎯 **中** | 工作流 | 创建命令模式和配方 |
| 🧪 **中** | 测试 | 添加测试，验证功能 |
| 🌐 **低** | 国际化 | 将文档翻译为其他语言 |

<p align="center">
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/📖_阅读-贡献指南-blue" alt="Contributing Guide">
  </a>
  <a href="https://github.com/SuperClaude-Org/SuperClaude_Framework/graphs/contributors">
    <img src="https://img.shields.io/badge/👥_查看-所有贡献者-green" alt="Contributors">
  </a>
</p>

</div>

---

<div align="center">

## ⚖️ **许可证**

本项目基于**MIT许可证**授权 - 详情请参阅[LICENSE](LICENSE)文件。

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?" alt="MIT License">
</p>

</div>

---

<div align="center">

## ⭐ **Star历史**

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

### **🚀 由SuperClaude社区倾情打造**

<p align="center">
  <sub>为突破边界的开发者用❤️制作</sub>
</p>

<p align="center">
  <a href="#-superclaude-框架">返回顶部 ↑</a>
</p>

</div>
