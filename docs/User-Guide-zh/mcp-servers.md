# SuperClaude MCP 服务器指南 🔌

## 概览

MCP（模型上下文协议）服务器通过专业工具扩展 Claude Code 的能力。SuperClaude 集成了 6 个 MCP 服务器，并为 Claude 提供指令，告诉它何时根据您的任务激活它们。

### 🔍 现实检查
- **MCP 服务器是什么**：提供附加工具的外部 Node.js 进程
- **它们不是什么**：内置的 SuperClaude 功能
- **激活如何工作**：Claude 读取指令，根据上下文使用适当的服务器
- **它们提供什么**：扩展 Claude Code 本地能力的真实工具

**核心服务器：**
- **context7**：官方库文档和模式
- **sequential-thinking**：多步推理和分析
- **magic**：现代 UI 组件生成
- **playwright**：浏览器自动化和 E2E 测试
- **morphllm-fast-apply**：基于模式的代码转换
- **serena**：语义代码理解和项目内存

## 快速开始

**设置验证**：MCP 服务器会自动激活。有关安装和故障排除，请参阅 [安装指南](../Getting-Started/installation.md) 和 [故障排除](../Reference/troubleshooting.md)。

**自动激活逻辑：**

| 请求包含 | 激活的服务器 |
|-----------------|------------------|
| 库导入、API 名称 | **context7** |
| `--think`、调试 | **sequential-thinking** |
| `component`、`UI`、前端 | **magic** |
| `test`、`e2e`、`browser` | **playwright** |
| 多文件编辑、重构 | **morphllm-fast-apply** |
| 大型项目、会话 | **serena** |

## 服务器详情

### context7 📚
**目的**：官方库文档访问
**触发器**：导入语句、框架关键词、文档请求
**要求**：Node.js 16+，无需 API 密钥

```bash
# 自动激活
/sc:implement "React authentication system"
# → 提供官方 React 模式

# 手动激活
/sc:analyze auth-system/ --c7
```

### sequential-thinking 🧠
**目的**：结构化多步推理和系统分析
**触发器**：复杂调试、`--think` 标志、架构分析
**要求**：Node.js 16+，无需 API 密钥

```bash
# 自动激活
/sc:troubleshoot "API performance issues"
# → 启用系统性根因分析

# 手动激活
/sc:analyze --think-hard architecture/
```

### magic ✨
**目的**：从 21st.dev 模式生成现代 UI 组件
**触发器**：UI 请求、`/ui` 命令、组件开发
**要求**：Node.js 16+，TWENTYFIRST_API_KEY

```bash
# 自动激活
/sc:implement "responsive dashboard component"
# → 使用现代模式生成可访问的 UI

# API 密钥设置
export TWENTYFIRST_API_KEY="your_key_here"
```

### playwright 🎭
**目的**：真实浏览器自动化和 E2E 测试
**触发器**：浏览器测试、E2E 场景、视觉验证
**要求**：Node.js 16+，无需 API 密钥

```bash
# 自动激活
/sc:test --type e2e "user login flow"
# → 启用浏览器自动化测试

# 手动激活
/sc:validate "accessibility compliance" --play
```

### morphllm-fast-apply 🔄
**目的**：高效的基于模式的代码转换
**触发器**：多文件编辑、重构、框架迁移
**要求**：Node.js 16+，MORPH_API_KEY

```bash
# 自动激活
/sc:improve legacy-codebase/ --focus maintainability
# → 在文件中应用一致的模式

# API 密钥设置
export MORPH_API_KEY="your_key_here"
```

### serena 🧭
**目的**：带有项目内存的语义代码理解
**触发器**：符号操作、大型代码库、会话管理
**要求**：Python 3.9+、uv 包管理器，无需 API 密钥

```bash
# 自动激活
/sc:load existing-project/
# → 构建项目理解和内存

# 手动激活
/sc:refactor "extract UserService" --serena
```

## 配置

**MCP 配置文件 (`~/.claude.json`)：**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "magic": {
      "command": "npx",
      "args": ["@21st-dev/magic"],
      "env": {"TWENTYFIRST_API_KEY": "${TWENTYFIRST_API_KEY}"}
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "morphllm-fast-apply": {
      "command": "npx",
      "args": ["@morph-llm/morph-fast-apply"],
      "env": {"MORPH_API_KEY": "${MORPH_API_KEY}"}
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant"]
    }
  }
}
```

## 使用模式

**服务器控制：**
```bash
# 启用特定服务器
/sc:analyze codebase/ --c7 --seq

# 禁用所有 MCP 服务器
/sc:implement "simple function" --no-mcp

# 启用所有服务器
/sc:design "complex architecture" --all-mcp
```

**多服务器协调：**
```bash
# 全栈开发
/sc:implement "e-commerce checkout"
# → Sequential：工作流分析
# → Context7：支付模式
# → Magic：UI 组件
# → Serena：代码组织
# → Playwright：E2E 测试
```

## 故障排除

**常见问题：**
- **无服务器连接**：检查 Node.js：`node --version`（需要 v16+）
- **Context7 失败**：清除缓存：`npm cache clean --force`
- **Magic/Morphllm 错误**：在没有 API 密钥时是预期的（付费服务）
- **服务器超时**：重启 Claude Code 会话

**快速修复：**
```bash
# 重置连接
# 重启 Claude Code 会话

# 检查依赖
node --version  # 应该显示 v16+

# 不使用 MCP 测试
/sc:command --no-mcp

# 检查配置
ls ~/.claude.json
```

**API 密钥配置：**
```bash
# 用于 Magic 服务器（UI 生成所需）
export TWENTYFIRST_API_KEY="your_key_here"

# 用于 Morphllm 服务器（批量转换所需）
export MORPH_API_KEY="your_key_here"

# 添加到 shell 配置文件以保持持久
echo 'export TWENTYFIRST_API_KEY="your_key"' >> ~/.bashrc
echo 'export MORPH_API_KEY="your_key"' >> ~/.bashrc
```

**环境变量使用：**
- ✅ `TWENTYFIRST_API_KEY` - Magic MCP 服务器功能所需
- ✅ `MORPH_API_KEY` - Morphllm MCP 服务器功能所需
- ❌ 文档中的其他环境变量 - 仅作示例，框架中不使用
- 📝 两者都是付费服务 API 密钥，框架在没有它们的情况下也可以工作

## 服务器组合

**无 API 密钥（免费）**：
- context7 + sequential-thinking + playwright + serena

**1 个 API 密钥**：
- 添加 magic 用于专业 UI 开发

**2 个 API 密钥**：
- 添加 morphllm-fast-apply 用于大规模重构

**常见工作流：**
- **学习**：context7 + sequential-thinking
- **Web 开发**：magic + context7 + playwright
- **企业重构**：serena + morphllm + sequential-thinking
- **复杂分析**：sequential-thinking + context7 + serena

## 集成

**与 SuperClaude 命令：**
- 分析命令自动使用 Sequential + Serena
- 实现命令使用 Magic + Context7
- 测试命令使用 Playwright + Sequential

**与行为模式：**
- 头脑风暴模式：Sequential 用于发现
- 任务管理：Serena 用于持久化
- 编排模式：最佳服务器选择

**性能控制：**
- 基于系统负载的自动资源管理
- 并发控制：`--concurrency N` (1-15)
- 在约束条件下基于优先级的服务器选择

## 相关资源

**必读资料：**
- [命令指南](commands.md) - 激活 MCP 服务器的命令
- [快速开始指南](../Getting-Started/quick-start.md) - MCP 设置指南

**高级使用：**
- [行为模式](modes.md) - 模式-MCP 协调
- [智能体指南](agents.md) - 智能体-MCP 集成
- [会话管理](session-management.md) - Serena 工作流

**技术参考：**
- [示例手册](../Reference/examples-cookbook.md) - MCP 工作流模式
- [技术架构](../Developer-Guide/technical-architecture.md) - 集成详情