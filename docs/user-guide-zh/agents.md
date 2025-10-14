# SuperClaude 智能体指南 🤖

SuperClaude 提供了 14 个领域专业智能体，Claude Code 可以调用它们获得专业知识。


## 🧪 测试智能体激活

使用本指南之前，请验证智能体选择功能是否正常：

```bash
# 测试手动智能体调用
@agent-python-expert "explain decorators"
# 期望行为：Python 专家提供详细解释

# 测试安全智能体自动激活
/sc:implement "JWT authentication"
# 期望行为：安全工程师应自动激活

# 测试前端智能体自动激活
/sc:implement "responsive navigation component"
# 期望行为：前端架构师 + Magic MCP 应激活

# 测试系统分析
/sc:troubleshoot "slow API performance"
# 期望行为：根因分析师 + 性能工程师激活

# 测试手动和自动结合
/sc:analyze src/
@agent-refactoring-expert "suggest improvements"
# 期望行为：分析后跟随重构建议
```

**如果测试失败**：检查 `~/.claude/agents/` 中是否存在智能体文件，或重启 Claude Code 会话

## 核心概念

### 什么是 SuperClaude 智能体？
**智能体**是专业的 AI 领域专家，以上下文指令的形式实现，用于修改 Claude Code 的行为。每个智能体都是 `superclaude/Agents/` 目录中精心制作的 `.md` 文件，包含领域特定的专业知识、行为模式和问题解决方法。

**重要提示**：智能体不是独立的 AI 模型或软件 - 它们是 Claude Code 读取的上下文配置，用于采用专门的行为。

### 两种使用智能体的方式

#### 1. 使用 @agent- 前缀手动调用
```bash
# 直接调用特定智能体
@agent-security "review authentication implementation"
@agent-frontend "design responsive navigation"
@agent-architect "plan microservices migration"
```

#### 2. 自动激活Auto-Activation（行为路由）
"自动激活"意味着 Claude Code 读取行为指令，根据您请求中的关键词和模式来调用相应的上下文。SuperClaude 提供行为指导原则，Claude 遵循这些原则路由到最合适的专业人员。

> **📝 智能体"自动激活"工作原理**:
> 智能体激活并非自动的系统逻辑——它是上下文文件中的行为指令。
> 当文档说智能体"自动激活"时，意味着 Claude Code 读取指令，根据您请求中的关键词和模式
> 调用特定的领域专业知识。这创造了智能路由的体验，同时保持底层机制的透明性。

```bash
# 这些命令自动激活相关智能体
/sc:implement "JWT authentication"  # → security-engineer 自动激活
/sc:design "React dashboard"        # → frontend-architect 自动激活
/sc:troubleshoot "memory leak"      # → performance-engineer 自动激活
```

**MCP 服务器** 通过专业工具提供增强功能，如 Context7（文档）、Sequential（分析）、Magic（UI）、Playwright（测试）和 Morphllm（代码转换）。

**领域专家** 专注于狭窄的专业领域，提供比通用方法更深入、更准确的解决方案。

### 智能体选择规则

**优先级层次：**
1. **手动覆盖** - @agent-[name] 优先于自动激活
2. **关键词** - 直接的领域术语触发主要智能体
3. **文件类型** - 扩展名激活语言/框架专家
4. **复杂度** - 多步骤任务调用协调智能体
5. **上下文** - 相关概念触发互补智能体

**冲突解决：**
- 手动调用 → 指定的智能体优先
- 多个匹配 → 多智能体协调
- 不明确的上下文 → 需求分析师激活
- 高复杂度 → 系统架构师监督
- 质量关注 → 自动包含质量保证智能体

**选择决策树：**
```
Task Analysis →
├─ Manual @agent-? → Use specified agent
├─ Single Domain? → Activate primary agent
├─ Multi-Domain? → Coordinate specialist agents
├─ Complex System? → Add system-architect oversight
├─ Quality Critical? → Include security + performance + quality agents
└─ Learning Focus? → Add learning-guide + technical-writer
```

## 快速开始示例

### 手动调用智能体
```bash
# 使用 @agent- 前缀显式调用特定智能体
@agent-python-expert "optimize this data processing pipeline"
@agent-quality-engineer "create comprehensive test suite"
@agent-technical-writer "document this API with examples"
@agent-socratic-mentor "explain this design pattern"
```

### 自动智能体协调
```bash
# 触发自动激活的命令
/sc:implement "JWT authentication with rate limiting"
# → 触发：security-engineer + backend-architect + quality-engineer

/sc:design "accessible React dashboard with documentation"
# → 触发：frontend-architect + learning-guide + technical-writer

/sc:troubleshoot "slow deployment pipeline with intermittent failures"
# → 触发：devops-architect + performance-engineer + root-cause-analyst

/sc:audit "payment processing security vulnerabilities"
# → 触发：security-engineer + quality-engineer + refactoring-expert
```

### 结合手动和自动方式
```bash
# 以命令开始（自动激活）
/sc:implement "user profile system"

# 然后显式添加专家审查
@agent-security "review the profile system for OWASP compliance"
@agent-performance-engineer "optimize database queries"
```

---

## SuperClaude 智能体团队 👥

### 架构和系统设计智能体 🏗️

### system-architect 🏢
**专业领域：** 大规模分布式系统设计，专注于可扩展性和服务架构

**自动激活：**
- 关键词："架构"、"微服务"、"可扩展性"、"系统设计"、"分布式"
- 上下文：多服务系统、架构决策、技术选择
- 复杂度：>5 个组件或跨领域集成需求

**能力：**
- 服务边界定义和微服务分解
- 技术栈选择和集成策略
- 可扩展性规划和性能架构
- 事件驱动架构和消息模式
- 数据流设计和系统集成

**示例：**
1. **电子商务平台**：为用户、产品、支付和通知服务设计微服务，采用事件源模式
2. **实时分析**：高吞吐量数据接入架构，采用流处理和时间序列存储
3. **多租户 SaaS**：具有租户隔离、共享基础架构和水平扩展策略的系统设计

### 成功标准
- [ ] 响应中体现系统级思维
- [ ] 提及服务边界和集成模式
- [ ] 包含可扩展性和可靠性考虑
- [ ] 提供技术栈建议

**验证：** `/sc:design "microservices platform"` 应该激活 system-architect
**测试：** 输出应包含服务分解和集成模式
**检查：** 应与 devops-architect 协调处理基础架构问题

**最佳搭配：** devops-architect（基础架构）、performance-engineer（优化）、security-engineer（合规）

---

### backend-architect ⚙️
**专业领域**: 强大的服务端系统设计，重点关注 API 可靠性和数据完整性

**自动激活**:
- 关键词: "API", "backend", "server", "database", "REST", "GraphQL", "endpoint"
- 文件类型: API 规范、服务器配置、数据库架构
- 上下文: 服务端逻辑、数据持久化、API 开发

**能力**:
- RESTful 和 GraphQL API 架构和设计模式
- 数据库架构设计和查询优化策略
- 身份验证、授权和安全实现
- 错误处理、日志记录和监控集成
- 缓存策略和性能优化

**示例**:
1. **用户管理 API**: JWT 身份验证与基于角色的访问控制和速率限制
2. **支付处理**: PCI 合规的交易处理与幂等性和审计跟踪
3. **内容管理**: 带有缓存、分页和实时通知的 RESTful APIs

**最佳搭配**: security-engineer（身份验证/安全）、performance-engineer（优化）、quality-engineer（测试）

---

### frontend-architect 🎨
**专业领域**: 现代 Web 应用程序架构，重点关注可访问性和用户体验

**自动激活**:
- 关键词: "UI", "frontend", "React", "Vue", "Angular", "component", "accessibility", "responsive"
- 文件类型: .jsx, .vue, .ts (前端), .css, .scss
- 上下文: 用户界面开发、组件设计、客户端架构

**能力**:
- 组件架构和设计系统实现
- 状态管理模式（Redux、Zustand、Pinia）
- 无障碍合规性（WCAG 2.1）和包容性设计
- 性能优化和包分析
- 渐进式 Web 应用和移动优先开发

**示例**:
1. **仪表板界面**: 具有实时更新和响应式网格布局的可访问数据可视化
2. **表单系统**: 具有验证、错误处理和无障碍功能的复杂多步骤表单
3. **设计系统**: 具有一致样式和交互模式的可重用组件库

**最佳搭配**: learning-guide（用户指导）、performance-engineer（优化）、quality-engineer（测试）

---

### devops-architect 🚀
**专业领域**: 基础设施自动化和部署管道设计，用于可靠的软件交付

**自动激活**:
- 关键词: "deploy", "CI/CD", "Docker", "Kubernetes", "infrastructure", "monitoring", "pipeline"
- 文件类型: Dockerfile、docker-compose.yml、k8s 清单、CI 配置
- 上下文: 部署流程、基础设施管理、自动化

**能力**:
- 具有自动化测试和部署的 CI/CD 管道设计
- 容器编排和 Kubernetes 集群管理
- 使用 Terraform 和云平台的基础设施即代码
- 监控、日志记录和可观测性堆栈实现
- 安全扫描和合规自动化

**示例**:
1. **微服务部署**: 具有服务网格、自动扩展和蓝绿发布的 Kubernetes 部署
2. **多环境管道**: 具有自动化测试、安全扫描和分阶段部署的 GitOps 工作流
3. **监控堆栈**: 具有指标、日志、跟踪和警报系统的综合可观测性

**最佳搭配**: system-architect（基础设施规划）、security-engineer（合规）、performance-engineer（监控）

### 质量与分析智能体 🔍

### security-engineer 🔒
**专业领域**: 应用安全架构，重点关注威胁建模和漏洞预防

**自动激活**:
- 关键词: "security", "auth", "authentication", "vulnerability", "encryption", "compliance", "OWASP"
- 上下文: 安全审查、身份验证流程、数据保护需求
- 风险指标: 支付处理、用户数据、API 访问、法规合规需求

**能力**:
- 威胁建模和攻击面分析
- 安全身份验证和授权设计（OAuth、JWT、SAML）
- 数据加密策略和密钥管理
- 漏洞评估和渗透测试指导
- 安全合规（GDPR、HIPAA、PCI-DSS）实施

**示例**:
1. **OAuth 实现**: 具有令牌刷新和基于角色访问控制的安全多租户身份验证
2. **API 安全**: 速率限制、输入验证、SQL 注入防护和安全头
3. **数据保护**: 静态/传输加密、密钥轮转和隐私设计架构

**最佳搭配**: backend-architect（API 安全）、quality-engineer（安全测试）、root-cause-analyst（事件响应）

---

### performance-engineer ⚡
**专业领域**: 系统性能优化，重点关注可扩展性和资源效率

**自动激活**:
- 关键词: "performance", "slow", "optimization", "bottleneck", "latency", "memory", "CPU"
- 上下文: 性能问题、可扩展性担忧、资源约束
- 指标: 响应时间 >500ms、高内存使用、低吞吐量

**能力**:
- 性能分析和瓶颈识别
- 数据库查询优化和索引策略
- 缓存实现（Redis、CDN、应用级别）
- 负载测试和容量规划
- 内存管理和资源优化

**示例**:
1. **API 优化**: 通过缓存和查询优化将响应时间从 2 秒减少到 200ms
2. **数据库扩展**: 实现读副本、连接池和查询结果缓存
3. **前端性能**: 包优化、延迟加载和 CDN 实现，实现 <3 秒加载时间

**最佳搭配**: system-architect（可扩展性）、devops-architect（基础设施）、root-cause-analyst（调试）

---

### root-cause-analyst 🔍
**专业领域**: 使用基于证据的分析和假设测试进行系统化问题调查

**自动激活**:
- 关键词: "bug", "issue", "problem", "debugging", "investigation", "troubleshoot", "error"
- 上下文: 系统故障、意外行为、复杂的多组件问题
- 复杂性: 需要有方法的调查的跨系统问题

**能力**:
- 系统化调试方法和根本原因分析
- 跨系统的错误关联和依赖关系映射
- 日志分析和故障调查的模式识别
- 复杂问题的假设形成和测试
- 事件响应和事后分析程序

**示例**:
1. **数据库连接失败**: 通过连接池、网络超时和资源限制跟踪间歇性故障
2. **支付处理错误**: 通过 API 日志、数据库状态和外部服务响应调查交易失败
3. **性能降级**: 通过指标关联、资源使用和代码更改分析逐渐放慢

**最佳搭配**: performance-engineer（性能问题）、security-engineer（安全事件）、quality-engineer（测试失败）

---

### quality-engineer ✅
**专业领域**: 综合测试策略和质量保证，重点关注自动化和覆盖率

**自动激活**:
- 关键词: "test", "testing", "quality", "QA", "validation", "coverage", "automation"
- 上下文: 测试规划、质量门禁、验证需求
- 质量担忧: 代码覆盖率 <80%、缺少测试自动化、质量问题

**能力**:
- 测试策略设计（单元、集成、端到端、性能测试）
- 测试自动化框架实现和 CI/CD 集成
- 质量指标定义和监控（覆盖率、缺陷率）
- 边缘用例识别和边界测试场景
- 无障碍测试和合规验证

**示例**:
1. **电子商务测试**: 涵盖用户流程、支付处理和库存管理的综合测试套件
2. **API 测试**: REST/GraphQL API 的自动化合约测试、负载测试和安全测试
3. **无障碍验证**: WCAG 2.1 合规测试，包括自动化和手动无障碍审计

**最佳搭配**: security-engineer（安全测试）、performance-engineer（负载测试）、frontend-architect（UI 测试）

---

### refactoring-expert 🔧
**专业领域**: 通过系统化重构和技术债务管理来改进代码质量

**自动激活**:
- 关键词: "refactor", "clean code", "technical debt", "SOLID", "maintainability", "code smell"
- 上下文: 遗留代码改进、架构更新、代码质量问题
- 质量指标: 高复杂性、重复代码、较低的测试覆盖率

**能力**:
- SOLID 原则应用和设计模式实现
- 代码异味识别和系统性消除
- 遗留代码现代化策略和迁移规划
- 技术债务评估和优先级框架
- 代码结构改进和架构重构

**示例**:
1. **遗留现代化**: 将单体应用转换为具有改进可测试性的模块化架构
2. **设计模式**: 为支付处理实现策略模式，以减少耦合并提高扩展性
3. **代码清理**: 移除重复代码、改进命名约定和提取可重用组件

**最佳搭配**: system-architect（架构改进）、quality-engineer（测试策略）、python-expert（语言特定模式）

### 专业化开发智能体 🎯

### python-expert 🐍
**专业领域**: 生产就绪的 Python 开发，重点关注现代框架和性能

**自动激活**:
- 关键词: "Python", "Django", "FastAPI", "Flask", "asyncio", "pandas", "pytest"
- 文件类型: .py、requirements.txt、pyproject.toml、Pipfile
- 上下文: Python 开发任务、API 开发、数据处理、测试

**能力**:
- 现代 Python 架构模式和框架选择
- 使用 asyncio 和并发 futures 的异步编程
- 通过性能分析和算法改进进行性能优化
- 使用 pytest、fixture 和测试自动化的测试策略
- 使用 pip、poetry 和 Docker 的包管理和部署

**示例**:
1. **FastAPI 微服务**: 具有 Pydantic 验证、依赖注入和 OpenAPI 文档的高性能异步 API
2. **数据管道**: 基于 Pandas 的 ETL，具有错误处理、日志记录和大数据集的并行处理
3. **Django 应用**: 具有自定义用户模型、API 端点和综合测试覆盖的全栈 Web 应用

**最佳搭配**: backend-architect（API 设计）、quality-engineer（测试）、performance-engineer（优化）

---

### requirements-analyst 📝
**专业领域**: 通过系统化利益相关者分析进行需求发现和规范开发

**自动激活**:
- 关键词: "requirements", "specification", "PRD", "user story", "functional", "scope", "stakeholder"
- 上下文: 项目启动、不明确的需求、范围定义需求
- 复杂性: 多利益相关者项目、不明确的目标、相互冲突的需求

**能力**:
- 通过利益相关者访谈和研讨会进行需求引出
- 具有接受标准和完成定义的用户故事编写
- 功能和非功能规范文档编制
- 利益相关者分析和需求优先级框架
- 范围管理和变更控制流程

**示例**:
1. **产品需求文档**: 金融科技移动应用的综合 PRD，包括用户画像、功能规范和成功指标
2. **API 规范**: 支付处理 API 的详细需求，包括错误处理、安全和性能标准
3. **迁移需求**: 遗留系统现代化需求，包括数据迁移、用户培训和回滚程序

**最佳搭配**: system-architect（技术可行性）、technical-writer（文档）、learning-guide（用户指导）

### 沟通与学习智能体 📚

### technical-writer 📚
**专业领域**: 技术文档和沟通，重点关注受众分析和清晰性

**自动激活**:
- 关键词: "documentation", "readme", "API docs", "user guide", "technical writing", "manual"
- 上下文: 文档请求、API 文档、用户指南、技术解释
- 文件类型: .md、.rst、API 规范、文档文件

**能力**:
- 技术文档架构和信息设计
- 受众分析和面向不同技能水平的内容定位
- 具有工作示例和集成指导的 API 文档
- 具有分步程序和故障排除的用户指南创建
- 无障碍标准应用和包容性语言使用

**示例**:
1. **API 文档**: 具有身份验证、端点、示例和 SDK 集成指南的综合 REST API 文档
2. **用户手册**: 具有截图、故障排除和 FAQ 部分的分步安装和配置指南
3. **技术规范**: 具有图表、数据流和实现细节的系统架构文档

**最佳搭配**: requirements-analyst（规范清晰度）、learning-guide（教育内容）、frontend-architect（UI 文档）

---

### learning-guide 🎓
**专业领域**: 教育内容设计和渐进式学习，重点关注技能开发和指导

**自动激活**:
- 关键词: "explain", "learn", "tutorial", "beginner", "teaching", "education", "training"
- 上下文: 教育请求、概念解释、技能开发、学习路径
- 复杂性: 需要分步骤分解和渐进理解的复杂主题

**能力**:
- 具有渐进技能开发的学习路径设计
- 通过类比和示例进行复杂概念解释
- 具有实践练习的交互式教程创建
- 技能评估和能力评估框架
- 指导策略和个性化学习方法

**示例**:
1. **编程教程**: 具有实践练习、代码示例和渐进复杂性的交互式 React 教程
2. **概念解释**: 通过实际示例、视觉图表和练习解释数据库规范化
3. **技能评估**: 具有实际项目和反馈的全栈开发综合评估框架

**最佳搭配**: technical-writer（教育文档）、frontend-architect（交互学习）、requirements-analyst（学习目标）

---

## 智能体协调与集成 🤝

### 协调模式

**架构团队**:
- **全栈开发**: frontend-architect + backend-architect + security-engineer + quality-engineer
- **系统设计**: system-architect + devops-architect + performance-engineer + security-engineer
- **遗留现代化**: refactoring-expert + system-architect + quality-engineer + technical-writer

**质量团队**:
- **安全审计**: security-engineer + quality-engineer + root-cause-analyst + requirements-analyst
- **性能优化**: performance-engineer + system-architect + devops-architect + root-cause-analyst
- **测试策略**: quality-engineer + security-engineer + performance-engineer + frontend-architect

**沟通团队**:
- **文档项目**: technical-writer + requirements-analyst + learning-guide + domain experts
- **学习平台**: learning-guide + frontend-architect + technical-writer + quality-engineer
- **API 文档**: backend-architect + technical-writer + security-engineer + quality-engineer

### MCP 服务器集成

**通过 MCP 服务器增强能力**:
- **Context7**: 为所有架构师和专家提供官方文档模式
- **Sequential**: 为 root-cause-analyst、system-architect、performance-engineer 提供多步骤分析
- **Magic**: 为 frontend-architect 提供 UI 生成，为 learning-guide 提供交互内容
- **Playwright**: 为 quality-engineer 提供浏览器测试，为 frontend-architect 提供无障碍验证
- **Morphllm**: 为 refactoring-expert 提供代码转换，为 python-expert 提供批量更改
- **Serena**: 为所有智能体提供项目内存，在会话间保持上下文

### 智能体激活故障排除

## 故障排除

获取故障排除帮助，请参阅：
- [常见问题](../Reference/common-issues.md) - 常见问题的快速修复
- [故障排除指南](../Reference/troubleshooting.md) - 综合问题解决

### 常见问题
- **无智能体激活**: 使用领域关键词："security"、"performance"、"frontend"
- **选择了错误的智能体**: 检查智能体文档中的触发关键词
- **智能体过多**: 将关键词聚焦在主要领域或使用 `/sc:focus [领域]`
- **智能体不协调**: 增加任务复杂性或使用多领域关键词
- **智能体专业知识不匹配**: 使用更具体的技术术语

### 即时修复
- **强制激活智能体**: 在请求中使用明确的领域关键词
- **重置智能体选择**: 重启 Claude Code 会话以重置智能体状态
- **检查智能体模式**: 查看智能体文档中的触发关键词
- **测试基本激活**: 尝试 `/sc:implement "security auth"` 测试 security-engineer

### 特定智能体故障排除

**无安全智能体：**
```bash
# 问题：安全问题未触发 security-engineer
# 快速修复：使用明确的安全关键词
"实现身份验证"                          # 通用 - 可能不会触发
"实现 JWT 身份验证安全"                # 明确 - 触发 security-engineer
"使用加密的安全用户登录"            # 安全聚焦 - 触发 security-engineer
```

**无性能智能体：**
```bash
# 问题：性能问题未触发 performance-engineer
# 快速修复：使用性能相关术语
"让它更快"                          # 模糊 - 可能不会触发
"优化缓慢的数据库查询"            # 具体 - 触发 performance-engineer
"减少 API 延迟和瓶颈"               # 性能聚焦 - 触发 performance-engineer
```

**无架构智能体：**
```bash
# 问题：系统设计未触发架构智能体
# 快速修复：使用架构关键词
"构建一个应用"                         # 通用 - 触发基本智能体
"设计微服务架构"                    # 具体 - 触发 system-architect
"可扩展的分布式系统设计"        # 架构聚焦 - 触发 system-architect
```

**错误的智能体组合：**
```bash
# 问题：在后端任务中获得前端智能体
# 快速修复：使用领域特定术语
"创建用户界面"                       # 可能触发 frontend-architect
"创建 REST API 端点"                  # 具体 - 触发 backend-architect
"实现服务端身份验证"              # 后端聚焦 - 触发 backend-architect
```

### 支持级别

**快速修复：**
- 从智能体触发表中使用明确的领域关键词
- 尝试重启 Claude Code 会话
- 聚焦在单一领域以避免混淆

**详细帮助：**
- 查看[常见问题指南](../Reference/common-issues.md)了解智能体安装问题
- 查看目标智能体的触发关键词

**专家支持：**
- 使用 `SuperClaude install --diagnose`
- 查看[诊断参考指南](../Reference/diagnostic-reference.md)进行协调分析

**社区支持：**
- 在 [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues) 报告问题
- 包括预期与实际智能体激活的示例

### 成功验证

应用智能体修复后，请测试：
- [ ] 领域特定请求激活正确的智能体（security → security-engineer）
- [ ] 复杂任务触发多智能体协调（3+ 智能体）
- [ ] 智能体专业知识匹配任务需求（API → backend-architect）
- [ ] 质量智能体在适当时自动包含（安全、性能、测试）
- [ ] 响应显示领域专业知识和专业化知识

## 快速故障排除（遗留）
- **无智能体激活** → 使用领域关键词："security"、"performance"、"frontend"
- **错误的智能体** → 检查智能体文档中的触发关键词
- **智能体过多** → 将关键词聚焦在主要领域
- **智能体不协调** → 增加任务复杂性或使用多领域关键词

**智能体未激活？**
1. **检查关键词**: 使用领域特定术语（例如，对于 security-engineer 使用 "authentication" 而不是 "login"）
2. **添加上下文**: 包含文件类型、框架或特定技术
3. **增加复杂性**: 多领域问题会触发更多智能体
4. **使用示例**: 引用与智能体专业知识匹配的具体场景

**智能体过多？**
- 将关键词聚焦在主要领域需求上
- 使用 `/sc:focus [领域]` 限制范围
- 从特定智能体开始，按需扩展

**错误的智能体？**
- 查看智能体文档中的触发关键词
- 为目标领域使用更具体的术语
- 添加明确的需求或约束

## 快速参考 📋

### 智能体触发查找

| 触发类型 | 关键词/模式 | 激活的智能体 |
|-------------|-------------------|------------------|
| **安全** | "auth", "security", "vulnerability", "encryption" | security-engineer |
| **性能** | "slow", "optimization", "bottleneck", "latency" | performance-engineer |
| **前端** | "UI", "React", "Vue", "component", "responsive" | frontend-architect |
| **后端** | "API", "server", "database", "REST", "GraphQL" | backend-architect |
| **测试** | "test", "QA", "validation", "coverage" | quality-engineer |
| **DevOps** | "deploy", "CI/CD", "Docker", "Kubernetes" | devops-architect |
| **架构** | "architecture", "microservices", "scalability" | system-architect |
| **Python** | ".py", "Django", "FastAPI", "asyncio" | python-expert |
| **问题** | "bug", "issue", "debugging", "troubleshoot" | root-cause-analyst |
| **代码质量** | "refactor", "clean code", "technical debt" | refactoring-expert |
| **文档** | "documentation", "readme", "API docs" | technical-writer |
| **学习** | "explain", "tutorial", "beginner", "teaching" | learning-guide |
| **需求** | "requirements", "PRD", "specification" | requirements-analyst |

### 命令-智能体映射

| 命令 | 主要智能体 | 支持智能体 |
|---------|----------------|-------------------|
| `/sc:implement` | Domain architects (frontend, backend) | security-engineer, quality-engineer |
| `/sc:analyze` | quality-engineer, security-engineer | performance-engineer, root-cause-analyst |
| `/sc:troubleshoot` | root-cause-analyst | Domain specialists, performance-engineer |
| `/sc:improve` | refactoring-expert | quality-engineer, performance-engineer |
| `/sc:document` | technical-writer | Domain specialists, learning-guide |
| `/sc:design` | system-architect | Domain architects, requirements-analyst |
| `/sc:test` | quality-engineer | security-engineer, performance-engineer |
| `/sc:explain` | learning-guide | technical-writer, domain specialists |

### 有效的智能体组合

**开发工作流**:
- Web 应用: frontend-architect + backend-architect + security-engineer + quality-engineer + devops-architect
- API 开发: backend-architect + security-engineer + technical-writer + quality-engineer
- 数据平台: python-expert + performance-engineer + security-engineer + system-architect

**分析工作流**:
- 安全审计: security-engineer + quality-engineer + root-cause-analyst + technical-writer
- 性能调查: performance-engineer + root-cause-analyst + system-architect + devops-architect
- 遗留评估: refactoring-expert + system-architect + quality-engineer + security-engineer + technical-writer

**沟通工作流**:
- 技术文档: technical-writer + requirements-analyst + domain experts + learning-guide
- 教育内容: learning-guide + technical-writer + frontend-architect + quality-engineer

## 最佳实践 💡

### 入门（简单方法）

**自然语言优先：**
1. **描述目标**: 使用包含领域特定关键词的自然语言
2. **信任自动激活**: 让系统自动路由到适当的智能体
3. **从模式中学习**: 观察不同请求类型激活的智能体
4. **迭代和优化**: 添加具体性以吸引额外的专家智能体

### 优化智能体选择

**有效的关键词使用：**
- **具体 > 通用**: 对于 security-engineer 使用 "authentication" 而不是 "login"
- **技术术语**: 包含框架名称、技术和具体挑战
- **上下文线索**: 提及文件类型、项目范围和复杂性指标
- **质量关键词**: 添加 "security"、"performance"、"accessibility" 以实现全面覆盖

**请求优化示例：**
```bash
# 通用（有限的智能体激活）
"修复登录功能"

# 优化（多智能体协调）
"实现具有速率限制和无障碍合规的安全 JWT 身份验证"
# → 触发: security-engineer + backend-architect + frontend-architect + quality-engineer
```

### 常见用法模式

**开发工作流：**
```bash
# 全栈功能开发
/sc:implement "具有实时通知的响应式用户仪表板"
# → frontend-architect + backend-architect + performance-engineer

# 带文档的 API 开发
/sc:create "带有综合文档的支付处理 REST API"
# → backend-architect + security-engineer + technical-writer + quality-engineer

# 性能优化调查
/sc:troubleshoot "影响用户体验的数据库查询缓慢"
# → performance-engineer + root-cause-analyst + backend-architect
```

**分析工作流：**
```bash
# 安全评估
/sc:analyze "身份验证系统的 GDPR 合规漏洞"
# → security-engineer + quality-engineer + requirements-analyst

# 代码质量审查
/sc:review "遗留代码库的现代化机会"
# → refactoring-expert + system-architect + quality-engineer + technical-writer

# 学习和解释
/sc:explain "带实践示例的微服务模式"
# → system-architect + learning-guide + technical-writer
```

### 高级智能体协调

**多领域项目：**
- **从广泛开始**: 从系统级关键词开始以吸引架构智能体
- **添加具体性**: 包含领域特定需求以激活专家智能体
- **质量集成**: 自动包含安全、性能和测试视角
- **文档包含**: 添加学习或文档需求以实现全面覆盖

**智能体选择故障排除：**

**问题：错误的智能体激活**
- 解决方案：使用更具体的领域术语
- 示例："数据库优化" → performance-engineer + backend-architect

**问题：智能体不够**
- 解决方案：增加复杂性指标和跨领域关键词
- 示例：向请求添加 "security"、"performance"、"documentation"

**问题：智能体过多**
- 解决方案：使用具体技术术语聚焦于主要领域
- 示例：使用 "/sc:focus backend" 来限制范围

### 质量驱动开发

**安全优先方法：**
始终在开发请求中包含安全考虑，以在领域专家之外自动吸引 security-engineer。

**性能集成：**
包含性能关键词（"fast"、"efficient"、"scalable"）以确保从一开始就有 performance-engineer 的协调。

**无障碍合规：**
使用 "accessible"、"WCAG" 或 "inclusive" 在前端开发中自动包含无障碍验证。

**文档文化：**
向请求添加 "documented"、"explained" 或 "tutorial" 以自动包含 technical-writer 和知识转移。

---

## 理解智能体智能 🧠

### 使智能体高效的因素

**领域专业知识**: 每个智能体都具有专业知识模式、行为方法和针对其领域的问题解决方法。

**上下文激活**: 智能体分析请求上下文，而不仅仅是关键词，以确定相关性和参与程度。

**协作智能**: 多智能体协调产生的协同结果超越了单个智能体的能力。

**自适应学习**: 智能体选择根据请求模式和成功的协调结果不断改进。

### 智能体与传统 AI

**传统方法**: 单个 AI 以不同的专业知识水平处理所有领域
**智能体方法**: 专业专家以深度领域知识和聚焦问题解决进行协作

**优点**:
- 在领域特定任务中更高的准确性
- 更复杂的问题解决方法
- 通过专家审查实现更好的质量保证
- 协调的多视角分析

### 信任系统，理解模式

**期望什么**:
- 自动路由到适当的领域专家
- 复杂任务的多智能体协调
- 通过自动包含 QA 智能体实现质量集成
- 通过教育智能体激活的学习机会

**不用担心什么**:
- 手动选择或配置智能体
- 复杂的路由规则或智能体管理
- 智能体配置或协调
- 微管理智能体交互

---

## 相关资源 📚

### 基本文档
- **[命令指南](commands.md)** - 掌握触发最优智能体协调的 SuperClaude 命令
- **[MCP 服务器](mcp-servers.md)** - 通过专业化工具集成增强智能体能力
- **[会话管理](session-management.md)** - 具有持久智能体上下文的长期工作流

### 高级用法
- **[行为模式](modes.md)** - 用于增强智能体协调的上下文优化
- **[入门指南](../Getting-Started/quick-start.md)** - 智能体优化的专家技巧
- **[示例食谱](../Reference/examples-cookbook.md)** - 实际的智能体协调模式

### 开发资源
- **[技术架构](../Developer-Guide/technical-architecture.md)** - 理解 SuperClaude 的智能体系统设计
- **[贡献指南](../Developer-Guide/contributing-code.md)** - 扩展智能体能力和协调模式

---

## 您的智能体之旅 🚀

**第 1 周：自然使用**
从自然语言描述开始。注意哪些智能体会激活以及原因。在不过度思考过程的情况下建立对关键词模式的直觉。

**第 2-3 周：模式识别**
观察智能体协调模式。理解复杂性和领域关键词如何影响智能体选择。开始优化请求措辞以实现更好的协调。

**第 2 个月+：专家协调**
掌握触发最优智能体组合的多领域请求。利用故障排除技巧进行有效的智能体选择。使用高级模式处理复杂工作流。

**SuperClaude 优势：**
体验 14 个专业 AI 专家协调响应的威力，所有这一切都通过简单的自然语言请求实现。无需配置，无需管理，只有随您的需求而扩展的智能协作。

🎯 **准备体验智能智能体协调？从 `/sc:implement` 开始，发现专业 AI 协作的魔力。**