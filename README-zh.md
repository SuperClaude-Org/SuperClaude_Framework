<div align="center">

# 🚀 SuperClaude 框架

### **将Claude Code转换为结构化开发平台**

<p align="center">
  <img src="https://img.shields.io/badge/version-4.1.9-blue" alt="Version">
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

| **命令** | **智能体** | **模式** | **MCP服务器** |
|:------------:|:----------:|:---------:|:---------------:|
| **30** | **16** | **7** | **8** |
| 斜杠命令 | 专业AI | 行为模式 | 集成服务 |

30个斜杠命令覆盖从头脑风暴到部署的完整开发生命周期。

</div>

---

<div align="center">

## 🎯 **概述**

SuperClaude是一个**元编程配置框架**，通过行为指令注入和组件编排，将Claude Code转换为结构化开发平台。它提供系统化的工作流自动化，配备强大的工具和智能代理。


## 免责声明

本项目与Anthropic无关联或认可。
Claude Code是由[Anthropic](https://www.anthropic.com/)构建和维护的产品。

## 📖 **开发者与贡献者指南**

**使用SuperClaude框架的必备文档：**

| 文档 | 用途 | 何时阅读 |
|----------|---------|--------------|
| **[PLANNING.md](PLANNING.md)** | 架构、设计原则、绝对规则 | 会话开始、实施前 |
| **[TASK.md](TASK.md)** | 当前任务、优先级、待办事项 | 每天、开始工作前 |
| **[KNOWLEDGE.md](KNOWLEDGE.md)** | 积累的见解、最佳实践、故障排除 | 遇到问题时、学习模式 |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 贡献指南、工作流程 | 提交PR前 |

> **💡 专业提示**：Claude Code在会话开始时会读取这些文件，以确保符合项目标准的一致、高质量开发。

## ⚡ **快速安装**

> **重要**：旧文档中描述的TypeScript插件系统
> 尚未可用（计划在v5.0中推出）。请按照以下v4.x的
> 当前安装说明操作。

### **当前稳定版本 (v4.1.9)**

SuperClaude目前使用斜杠命令。

**选项1：pipx（推荐）**
```bash
# 从PyPI安装
pipx install superclaude

# 安装命令（安装 /research, /index-repo, /agent, /recommend）
superclaude install

# 验证安装
superclaude install --list
superclaude doctor
```

安装后，重启Claude Code以使用命令：
- `/sc:research` - 并行搜索的深度网络研究
- `/sc:index-repo` - 用于上下文优化的仓库索引
- `/sc:agent` - 专业AI智能体
- `/sc:recommend` - 命令推荐
- `/sc` - 显示所有可用的SuperClaude命令

**选项2：从Git直接安装**
```bash
# 克隆仓库
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# 运行安装脚本
./install.sh
```

### **v5.0即将推出（开发中）**

我们正在积极开发新的TypeScript插件系统（详见issue [#419](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/419)）。发布后，安装将简化为：

```bash
# 此功能尚未可用
/plugin marketplace add SuperClaude-Org/superclaude-plugin-marketplace
/plugin install superclaude
```

**状态**：开发中。尚未设定ETA。

### **增强性能（可选MCP）**

要获得**2-3倍**更快的执行速度和**30-50%**更少的token消耗，可选择安装MCP服务器：

```bash
# 用于增强性能的可选MCP服务器（通过airis-mcp-gateway）：
# - Serena: 代码理解（快2-3倍）
# - Sequential: Token高效推理（减少30-50% token）
# - Tavily: 用于深度研究的网络搜索
# - Context7: 官方文档查找
# - Mindbase: 跨所有对话的语义搜索（可选增强）

# 注意：错误学习通过内置的ReflexionMemory提供（无需安装）
# Mindbase提供语义搜索增强（需要"recommended"配置文件）
# 安装MCP服务器：https://github.com/agiletec-inc/airis-mcp-gateway
# 详见 docs/mcp/mcp-integration-policy.md
```

**性能对比：**
- **不使用MCP**：功能完整，标准性能 ✅
- **使用MCP**：快2-3倍，减少30-50% token ⚡

</div>

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

## 🎉 **V4.1版本新功能**

> *版本4.1专注于稳定斜杠命令架构、增强智能体能力和改进文档。*

<table>
<tr>
<td width="50%">

### 🤖 **更智能的智能体系统**
**16个专业智能体**具有领域专业知识：
- PM Agent通过系统化文档确保持续学习
- 深度研究智能体用于自主网络研究
- 安全工程师发现真实漏洞
- 前端架构师理解UI模式
- 基于上下文的自动协调
- 按需提供领域专业知识

</td>
<td width="50%">

### ⚡ **优化性能**
**更小的框架，更大的项目：**
- 减少框架占用
- 为您的代码提供更多上下文
- 支持更长对话
- 启用复杂操作

</td>
</tr>
<tr>
<td width="50%">

### 🔧 **MCP服务器集成**
**8个强大服务器**(通过airis-mcp-gateway)：
- **Tavily** → 主要网络搜索(深度研究)
- **Serena** → 会话持久化和内存
- **Mindbase** → 跨会话学习(零占用)
- **Sequential** → Token高效推理
- **Context7** → 官方文档查找
- **Playwright** → JavaScript重度内容提取
- **Magic** → UI组件生成
- **Chrome DevTools** → 性能分析

</td>
<td width="50%">

### 🎯 **行为模式**
**7种自适应模式**适应不同上下文：
- **头脑风暴** → 提出正确问题
- **商业面板** → 多专家战略分析
- **深度研究** → 自主网络研究
- **编排** → 高效工具协调
- **令牌效率** → 30-50%上下文节省
- **任务管理** → 系统化组织
- **内省** → 元认知分析

</td>
</tr>
<tr>
<td width="50%">

### 📚 **文档全面改写**
**为开发者完全重写：**
- 真实示例和用例
- 记录常见陷阱
- 包含实用工作流
- 更好的导航结构

</td>
<td width="50%">

### 🧪 **增强稳定性**
**专注于可靠性：**
- 核心命令的错误修复
- 改进测试覆盖率
- 更健壮的错误处理
- CI/CD流水线改进

</td>
</tr>
</table>

</div>

---

<div align="center">

## 🔬 **深度研究能力**

### **与DR智能体架构一致的自主网络研究**

SuperClaude v4.2引入了全面的深度研究能力，实现自主、自适应和智能的网络研究。

<table>
<tr>
<td width="50%">

### 🎯 **自适应规划**
**三种智能策略：**
- **仅规划**：对明确查询直接执行
- **意图规划**：对模糊请求进行澄清
- **统一**：协作式计划完善(默认)

</td>
<td width="50%">

### 🔄 **多跳推理**
**最多5次迭代搜索：**
- 实体扩展(论文 → 作者 → 作品)
- 概念深化(主题 → 细节 → 示例)
- 时间进展(当前 → 历史)
- 因果链(效果 → 原因 → 预防)

</td>
</tr>
<tr>
<td width="50%">

### 📊 **质量评分**
**基于置信度的验证：**
- 来源可信度评估(0.0-1.0)
- 覆盖完整性跟踪
- 综合连贯性评估
- 最低阈值：0.6，目标：0.8

</td>
<td width="50%">

### 🧠 **基于案例的学习**
**跨会话智能：**
- 模式识别和重用
- 随时间优化策略
- 保存成功的查询公式
- 性能改进跟踪

</td>
</tr>
</table>

### **研究命令使用**

```bash
# 使用自动深度的基本研究
/research "2024年最新AI发展"

# 控制研究深度(通过TypeScript中的选项)
/research "量子计算突破"  # depth: exhaustive

# 特定策略选择
/research "市场分析"  # strategy: planning-only

# 领域过滤研究(Tavily MCP集成)
/research "React模式"  # domains: reactjs.org,github.com
```

### **研究深度级别**

| 深度 | 来源 | 跳数 | 时间 | 最适合 |
|:-----:|:-------:|:----:|:----:|----------|
| **快速** | 5-10 | 1 | ~2分钟 | 快速事实、简单查询 |
| **标准** | 10-20 | 3 | ~5分钟 | 一般研究(默认) |
| **深入** | 20-40 | 4 | ~8分钟 | 综合分析 |
| **详尽** | 40+ | 5 | ~10分钟 | 学术级研究 |

### **集成工具编排**

深度研究系统智能协调多个工具：
- **Tavily MCP**：主要网络搜索和发现
- **Playwright MCP**：复杂内容提取
- **Sequential MCP**：多步推理和综合
- **Serena MCP**：内存和学习持久化
- **Context7 MCP**：技术文档查找

</div>

---

<div align="center">

## 📚 **文档**

### **SuperClaude完整指南**

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

- 🎯 [**斜杠命令**](docs/user-guide/commands.md)
  *完整的 `/sc` 命令列表*

- 🤖 [**智能体指南**](docs/user-guide/agents.md)
  *16个专业智能体*

- 🎨 [**行为模式**](docs/user-guide/modes.md)
  *7种自适应模式*

- 🚩 [**标志指南**](docs/user-guide/flags.md)
  *控制行为参数*

- 🔧 [**MCP服务器**](docs/user-guide/mcp-servers.md)
  *8个服务器集成*

- 💼 [**会话管理**](docs/user-guide/session-management.md)
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

---

## 📋 **全部30个命令**

<details>
<summary><b>点击展开完整命令列表</b></summary>

### 🧠 规划与设计 (4)
- `/brainstorm` - 结构化头脑风暴
- `/design` - 系统架构
- `/estimate` - 时间/工作量估算
- `/spec-panel` - 规格分析

### 💻 开发 (5)
- `/implement` - 代码实现
- `/build` - 构建工作流
- `/improve` - 代码改进
- `/cleanup` - 重构
- `/explain` - 代码解释

### 🧪 测试与质量 (4)
- `/test` - 测试生成
- `/analyze` - 代码分析
- `/troubleshoot` - 调试
- `/reflect` - 回顾

### 📚 文档 (2)
- `/document` - 文档生成
- `/help` - 命令帮助

### 🔧 版本控制 (1)
- `/git` - Git操作

### 📊 项目管理 (3)
- `/pm` - 项目管理
- `/task` - 任务跟踪
- `/workflow` - 工作流自动化

### 🔍 研究与分析 (2)
- `/research` - 深度网络研究
- `/business-panel` - 业务分析

### 🎯 实用工具 (9)
- `/agent` - AI智能体
- `/index-repo` - 仓库索引
- `/index` - 索引别名
- `/recommend` - 命令推荐
- `/select-tool` - 工具选择
- `/spawn` - 并行任务
- `/load` - 加载会话
- `/save` - 保存会话
- `/sc` - 显示所有命令

[**📖 查看详细命令参考 →**](docs/reference/commands-list.md)

</details>
