# SuperClaude 行为模式指南 🧠

## ✅ 快速验证
使用 `/sc:` 命令测试模式 - 它们会根据任务复杂性自动激活。有关完整命令参考，请参阅 [命令指南](commands.md)。

## 快速参考表

| 模式 | 目的 | 自动触发 | 关键行为 | 最适合 |
|------|---------|---------------|---------------|---------------|
| **🧠 头脑风暴** | 交互式发现 | "brainstorm"、"maybe"、模糊请求 | 苏格拉底式问题、需求发掘 | 新项目规划、不明确需求 |
| **🔍 内省** | 元认知分析 | 错误恢复、"分析推理" | 透明思维标记 (🤔, 🎯, 💡) | 调试、学习、优化 |
| **📋 任务管理** | 复杂协调 | >3 步骤、>2 目录 | 阶段分解、内存持久化 | 多步操作、项目管理 |
| **🎯 编排** | 智能工具选择 | 多工具操作、高资源使用 | 最优工具路由、并行执行 | 复杂分析、性能优化 |
| **⚡ 令牌效率** | 压缩通信 | 高上下文使用、`--uc` 标志 | 符号系统，预计减少 30-50% 令牌 | 资源约束、大型操作 |


---

## 入门指南（2 分钟概览）

**模式通过行为指令激活** - Claude Code 读取上下文文件，根据您的任务模式和复杂性来决定采用哪种模式行为。

**快速示例：**
```bash
# 自动激活示例
/sc:brainstorm "mobile app"        # → 苏格拉底式发现问题
/sc:implement "authentication system"        # → 多阶段协调
"--uc analyze large-codebase/"     # → 压缩符号输出
```

**何时使用手动标志：**
- 需要特定行为：`--brainstorm`、`--introspect`、`--uc`
- 为学习/调试而覆盖自动检测
- 针对特定约束进行优化（内存、时间、清晰度）

---

## 模式详情

### 🧠 头脑风暴模式 - 交互式发现

**目的**：通过协作发现将模糊的想法转化为结构化的需求。

**自动激活触发器：**
- 模糊的项目请求："我想构建..."、"正在考虑创建..."
- 探索关键词：brainstorm、explore、discuss、figure out、not sure
- 不确定指示器："maybe"、"possibly"、"could we"
- 手动标志：`--brainstorm`、`--bs`

**行为变化：**
- **苏格拉底式提问**：提出探性问题以发掘隐藏需求
- **非预设性方法**：避免假设，让您引导发现方向
- **协作伙伴关系**：在探索中与您合作，而不是指导性咨询
- **需求综合**：将见解转化为结构化的技术简报
- **跨会话内存**：为后续讨论维护发现上下文

**体验示例:**
```
Standard Approach: "I'll build a user authentication system with JWT tokens..."
Brainstorming Approach: 
"🤔 Let's explore this together:
 - What specific user problems does auth solve for your app?
 - Who are your users and what's their technical comfort level?  
 - Any existing systems or social logins to integrate with?
 - What security/compliance requirements do you have?
 📝 Outcome: Detailed auth requirements brief ready for implementation"
```

#### 成功标准  
- [ ] 用问题而不是直接解决方案来回应
- [ ] 问题探索用户需求、技术约束和业务目标
- [ ] 在整个发现过程中保持协作语调
- [ ] 产生结构化需求或技术简介作为结果

**验证：** `/sc:brainstorm "web app"` 应该询问用户、功能、技术相关问题
**测试：** 模糊请求应该触发发现性问题，而不是假设
**检查：** 模式应该在同一会话的后续问题中保持一致

**最佳搭配：**
- **→ 任务管理**：需求发现 → 系统性实施规划
- **→ 编排**：需求明确化 → 实施的最优工具选择
- **手动覆盖**：使用 `--brainstorm` 强制发现，即使对于"明确"的需求

---

### 🔍 内省模式 - 元认知分析

**目的**：为学习优化和透明决策制定暴露推理过程。

**自动激活触发器：**
- 自我分析请求："分析我的推理"、"反思决策"
- 错误恢复场景和需要调查的意外结果
- 具有多种可行方法的复杂问题求解
- 优化机会的模式识别需求
- 手动标志：`--introspect`

**行为变化：**
- **推理透明度**：通过清晰标记暴露思维过程 (🤔, 🎯, ⚡, 📊, 💡)
- **决策分析**：评估选择逻辑并考虑替代方案
- **模式识别**：识别重复行为和改进机会
- **元学习**：提取见解以持续改进框架
- **框架合规性**：根据 SuperClaude 原则和质量门控验证行为

**体验示例：**
```
Standard Approach: "I'll analyze this code structure and suggest improvements..."
Introspective Approach:
"🧠 Meta-Analysis: Why did I choose structural analysis over functional flow analysis?
 🎯 Decision Logic: Saw class hierarchy → assumed OOP patterns dominate
 🔄 Alternative Considered: Data flow analysis might reveal hidden dependencies
 📊 Evidence Check: File imports suggest functional composition, not OOP
 💡 Learning: Need to analyze imports before choosing analysis strategy
 ⚡ Correction: Switching to functional flow analysis approach"
```

**最佳搭配：**
- **→ 任务管理**：为复杂阶段决策提供透明推理
- **任何模式**：为任何其他模式的操作添加推理透明度层
- **手动覆盖**：在学习会话和调试工作流中使用 `--introspect`

---

### 📋 任务管理模式 - 复杂协调

**目的**：具有会话持久性的分层任务组织，用于多步操作。

**自动激活触发器：**
- 需要超过 3 个协调步骤的操作
- 多文件/目录范围（>2 目录或 >3 文件）
- 需要阶段和检查点的复杂依赖关系
- 质量改进请求：完善、优化、增强
- 手动标志：`--task-manage`、`--delegate`

**行为变化：**
- **分层规划**：将复杂工作分解为计划 → 阶段 → 任务 → 待办结构
- **会话持久性**：在中断期间维护项目上下文和进度
- **内存集成**：使用 write_memory/read_memory 进行状态保存
- **进度编排**：协调 TodoWrite 与内存更新以进行跟踪
- **质量门控**：在阶段之间实施系统验证检查点

**体验示例：**
```
Standard Approach: "I'll implement user authentication..." → Direct implementation
Task Management Approach:
"📋 Multi-Phase Implementation Plan:
 🎯 Phase 1: Security requirements analysis (Session 1)
 🎯 Phase 2: API design & documentation (Session 2)
 🎯 Phase 3: Implementation & testing (Sessions 3-4)
 🎯 Phase 4: Integration & validation (Session 5)
 💾 Session Persistence: Auto-resume context
 ✓ Quality Gates: Validation before each phase transition"
```

**最佳搭配：**
- **头脑风暴 →**：需求发现然后系统化实施
- **+ 编排**：任务协调与最优工具选择
- **+ 内省**：复杂阶段决策的透明推理

---

### 🎯 编排模式 - 智能工具选择

**目的**：通过智能工具路由和并行协调优化任务执行。

**自动激活触发器：**
- 需要复杂协调的多工具操作
- 性能约束（高资源使用）
- 并行执行机会（>3 个独立文件/操作）
- 具有多种有效工具方法的复杂路由决策

**行为变化：**
- **智能工具路由**：为每种任务类型选择最优的 MCP 服务器和原生工具
- **资源感知**：基于系统约束和可用性调整方法
- **并行优化**：识别独立操作以进行并发执行
- **协调焦点**：通过协调执行优化工具选择和使用
- **自适应回退**：当首选选项不可用时优雅地切换工具

**体验示例：**
```
Standard Approach: Sequential file-by-file analysis and editing
Orchestration Approach:
"🎯 Multi-Tool Coordination Strategy:
 🔍 Phase 1: Serena (semantic analysis) + Sequential (architecture review)
 ⚡ Phase 2: Morphllm (pattern edits) + Magic (UI components)
 🧪 Phase 3: Playwright (testing) + Context7 (doc patterns)
 🔄 Parallel Execution: 3 tools working simultaneously"
```

**最佳搭配：**
- **任务管理 →**：为复杂多阶段计划提供工具协调
- **+ 令牌效率**：带压缩通信的最优工具选择
- **任何复杂任务**：添加智能工具路由以增强执行

---

### ⚡ 令牌效率模式 - 压缩通信

**目的**：通过符号系统实现预计 30-50% 的令牌减少，同时保持信息质量。

**自动激活触发器：**
- 高上下文使用接近限制
- 需要资源效率的大规模操作
- 用户显式标志：`--uc`、`--ultracompressed`
- 具有多个输出的复杂分析工作流

**行为变化：**
- **符号通信**：为逻辑流程、状态和技术领域使用视觉符号
- **技术缩写**：对重复技术术语进行上下文感知压缩
- **结构化密度**：使用要点、表格和简洁格式，而非冗长段落
- **信息保留**：尽管压缩，仍保持 ≥95% 的信息质量
- **结构化格式**：为清晰度和任务完成而组织

**体验示例：**
```
Standard Approach: "Authentication system implementation shows security vulnerability in user validation function requiring immediate attention..."
Token-Efficient Approach:
"🛡️ Security Alert:
 auth.js:45 → user val() → critical vuln
 📊 Impact: ❌ possible token bypass
 ⚡ Action: fix validation + audit ∵ high severity
 🔧 Estimate: 2hr impl + 1hr test"
```

**最佳搭配：**
- **任何模式**：在保持特定模式行为的同时添加压缩层
- **编排 →**：压缩的工具协调和状态更新
- **手动覆盖**：当上下文压力或效率是优先级时使用 `--uc`

---

### 🎨 标准模式 - 均衡默认

**目的**：为直接的开发任务提供清晰、专业的沟通。

**自动激活触发器：**
- 没有复杂性指标的简单、明确定义的任务
- 具有明确要求的单文件操作
- 基本解释和标准开发工作流
- 未检测到其他模式触发器（默认回退）

**行为变化：**
- **专业沟通**：清晰、简洁的技术语言，无压缩
- **适度细节**：适合大多数开发任务的平衡信息深度
- **标准工具选择**：使用原生 Claude 能力和基本工具
- **质量焦点**：在无复杂编排开销的情况下保持代码质量
- **响应式适应**：当复杂性增加时准备切换到专门模式

**体验示例：**
```
Standard Approach: Consistent, professional baseline for all tasks
"I'll implement the login functionality with proper error handling:

 1. Validate user input (email format, password requirements)
 2. Authenticate against database with secure hashing
 3. Generate JWT token with appropriate expiration
 4. Return success response with user data

 Implementation will follow security best practices and include comprehensive error handling."
```

**最佳搭配：**
- **→ 任何模式**：作为其他模式增强的基线
- **模式切换**：需要时自动升级到专门模式
- **清晰优先**：当直接沟通比优化更重要时

---

## 高级用法

### 模式组合

**多模式工作流：**
```bash
# 发现 → 规划 → 实现
/sc:brainstorm "microservices architecture" --task-manage
# → 头脑风暴：需求发现
# → 任务管理：多阶段协调

# 透明和高效的分析
/sc:analyze legacy-system/ --introspect --uc
# → 内省：透明推理
# → 令牌效率：压缩输出
```

### 手动模式控制

**强制特定行为：**
- `--brainstorm`：为任何任务强制协作发现
- `--introspect`：为任何模式添加推理透明度
- `--task-manage`：启用分层协调
- `--orchestrate`：优化工具选择和并行执行
- `--uc`：为效率压缩通信

**覆盖示例：**
```bash
# 对“明确”的需求强制头脑风暴
/sc:implement "user login" --brainstorm

# 为调试添加推理透明度
# 使用透明推理调试认证问题

# 为简单操作启用任务管理
# 系统化任务管理更新样式文件
```

### 模式边界和优先级

**模式激活时机：**
1. **复杂度阈值**：>3 文件 → 任务管理
2. **资源压力**：高上下文使用 → 令牌效率
3. **多工具需求**：复杂分析 → 编排
4. **不确定性**：模糊需求 → 头脑风暴
5. **错误恢复**：问题 → 内省

**优先级规则：**
- **安全第一**：质量和验证总是覆盖效率
- **用户意图**：手动标志覆盖自动检测
- **上下文适应**：基于复杂性堆叠模式
- **资源管理**：在压力下激活效率模式

---

## 现实世界示例

### 完整工作流示例

**新项目开发：**
```bash
# 阶段 1：发现（头脑风暴模式自动激活）
"I want to build a productivity app"
→ 🤔 关于用户、功能、平台选择的苏格拉底式问题
→ 📝 结构化需求简报

# 阶段 2：规划（任务管理模式自动激活）
/sc:implement "core productivity features"
→ 📋 带依赖关系的多阶段分解
→ 🎯 带质量门控的阶段协调

# 阶段 3：实现（编排模式协调工具）
/sc:implement "frontend and backend systems"
→ 🎯 Magic (UI) + Context7 (模式) + Sequential (架构)
→ ⚡ 并行执行优化
```

**调试复杂问题：**
```bash
# 问题分析（内省模式自动激活）
"Users experiencing intermittent authentication failures"
→ 🤔 关于潜在原因的透明推理
→ 🎯 假设形成和证据收集
→ 💡 跨相似问题的模式识别

# 系统性解决（任务管理协调）
# 全面修复认证系统
→ 📋 阶段 1：根因分析
→ 📋 阶段 2：解决方案实现
→ 📋 阶段 3：测试和验证
```

### 模式组合模式

**高复杂度场景：**
```bash
# 带多重约束的大型重构
/sc:improve legacy-system/ --introspect --uc --orchestrate
→ 🔍 透明推理introspect（内省）
→ ⚡ 压缩通信uc（令牌效率）
→ 🎯 最优工具协调orchestrate（编排）
→ 📋 系统化阶段（任务管理自动激活）
```

---

## 快速参考

### 模式激活模式

| 触发类型 | 输入示例 | 激活模式 | 关键行为 |
|---------|---------|----------|----------|
| **模糊请求** | "我想构建一个应用" | 🧠 头脑风暴 | 苏格拉底式发现问题 |
| **复杂范围** | >3 文件或 >2 目录 | 📋 任务管理 | 阶段协调 |
| **多工具需求** | 分析 + 实施 | 🎯 编排 | 工具优化 |
| **错误恢复** | "这没有按预期工作" | 🔍 内省 | 透明推理 |
| **资源压力** | 高上下文使用 | ⚡ 令牌效率 | 符号压缩 |
| **简单任务** | "修复这个函数" | 🎨 标准 | 清晰、直接的方法 |

### 手动覆盖命令

```bash
# 强制特定模式行为
/sc:command --brainstorm    # 协作发现
/sc:command --introspect    # 推理透明度
/sc:command --task-manage   # 分层协调
/sc:command --orchestrate   # 工具优化
/sc:command --uc            # 令牌压缩

# 组合多种模式
/sc:command --introspect --uc    # 透明 + 高效
/sc:command --task-manage --orchestrate  # 协调 + 优化
```

---

## 故障排除

有关故障排除帮助，请参阅：
- [常见问题](../Reference/common-issues.md) - 频繁问题的快速修复
- [故障排除指南](../Reference/troubleshooting.md) - 全面的问题解决方案

### 常见问题
- **模式未激活**：使用手动标志：`--brainstorm`、`--introspect`、`--uc`
- **激活了错误的模式**：检查请求中的复杂性触发器和关键词
- **模式意外切换**：基于任务演化的正常行为
- **执行影响**：模式优化工具使用，不应影响执行
- **模式冲突**：检查[标志指南](flags.md)中的标志优先级规则

### 即时修复
- **强制特定模式**：使用明确标志如 `--brainstorm` 或 `--task-manage`
- **重置模式行为**：重启 Claude Code 会话以重置模式状态
- **检查模式指示器**：在响应中查找 🤔、🎯、📋 符号
- **验证复杂性**：简单任务使用标准模式，复杂任务自动切换

### 特定模式故障排除

**头脑风暴模式问题：**
```bash
# 问题：模式给出解决方案而不是问题
# 快速修复：检查请求清晰度并使用显式标志
/sc:brainstorm "web app" --brainstorm         # 强制发现模式
"I have a vague idea about..."                # 使用不确定语言
"Maybe we could build..."                     # 触发探索
```

**任务管理模式问题：**
```bash
# 问题：简单任务得到复杂协调
# 快速修复：减少范围或使用更简单的命令
/sc:implement "function" --no-task-manage     # 禁用协调
/sc:troubleshoot bug.js                       # 使用基本命令
# 检查任务是否真正复杂（>3 文件，>2 目录）
```

**令牌效率模式问题：**
```bash
# 问题：输出过于压缩或不清楚
# 快速修复：禁用压缩以提高清晰度
/sc:command --no-uc                           # 禁用压缩
/sc:command --verbose                         # 强制详细输出
# 当清晰度比效率更重要时使用
```

**内省模式问题：**
```bash
# 问题：过多元评论，行动不足
# 快速修复：为直接工作禁用内省
/sc:command --no-introspect                   # 直接执行
# 仅在学习和调试时使用内省
```

**编排模式问题：**
```bash
# 问题：工具协调造成混乱
# 快速修复：简化工具使用
/sc:command --no-mcp                          # 仅使用原生工具
/sc:command --simple                          # 基本执行
# 检查任务复杂度是否需要编排
```

### 错误代码参考

| 模式错误 | 含义 | 快速修复 |
|---------|-----|----------|
| **B001** | 头脑风暴激活失败 | 使用显式 `--brainstorm` 标志 |
| **T001** | 任务管理开销 | 对简单任务使用 `--no-task-manage` |
| **U001** | 令牌效率过于激进 | 使用 `--verbose` 或 `--no-uc` |
| **I001** | 内省模式卡住 | 对直接行动使用 `--no-introspect` |
| **O001** | 编排协调失败 | 使用 `--no-mcp` 或 `--simple` |
| **M001** | 检测到模式冲突 | 检查标志优先级规则 |
| **M002** | 模式切换循环 | 重启会话以重置状态 |
| **M003** | 模式无法识别 | 更新 SuperClaude 或检查拼写 |

### 渐进式支持级别

**级别 1：快速修复（< 2 分钟）**
- 使用手动标志覆盖自动模式选择
- 检查任务复杂性是否与预期模式行为匹配
- 尝试重启 Claude Code 会话

**级别 2：详细帮助（5-15 分钟）**
```bash
# 特定模式诊断
/sc:help modes                            # 列出所有可用模式
/sc:reflect --type mode-status            # 检查当前模式状态
# 检查请求复杂性和触发器
```
- 有关模式安装问题，请参阅[常见问题指南](../Reference/common-issues.md)

**级别 3：专家支持（30+ 分钟）**
```bash
# 深度模式分析
SuperClaude install --diagnose
# 检查模式激活模式
# 检查行为触发器和阈值
```
- 有关行为模式分析，请参阅[诊断参考指南](../Reference/diagnostic-reference.md)

**级别 4：社区支持**
- 在 [GitHub Issues](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues) 报告模式问题
- 包括意外模式行为的示例
- 描述期望与实际模式激活的差异

### 成功验证

应用模式修复后，进行测试：
- [ ] 简单请求使用标准模式（清晰、直接的响应）
- [ ] 复杂请求自动激活适当的模式（协调、推理）
- [ ] 手动标志正确覆盖自动检测
- [ ] 模式指示器（🤔、🎯、📋）在预期时出现
- [ ] 在不同模式下性能保持良好

## 快速故障排除（旧版）
- **模式未激活** → 使用手动标志：`--brainstorm`、`--introspect`、`--uc`
- **激活了错误的模式** → 检查请求中的复杂性触发器和关键词
- **模式意外切换** → 基于任务演化的正常行为
- **执行影响** → 模式优化工具使用，不应影响执行
- **模式冲突** → 检查[标志指南](flags.md)中的标志优先级规则

## 常见问题

**问：如何知道哪个模式处于激活状态？**
答：在通信模式中查找这些指示器：
- 🤔 发现性问题 → 头脑风暴
- 🎯 推理透明度 → 内省
- 阶段分解 → 任务管理
- 工具协调 → 编排
- 符号压缩 → 令牌效率

**问：我可以强制特定模式吗？**
答：是的，使用手动标志覆盖自动检测：
```bash
/sc:command --brainstorm     # 强制发现模式
/sc:command --introspect     # 增加透明性
/sc:command --task-manage    # 启用协调
/sc:command --uc             # 压缩输出
```

**问：模式会影响执行吗？**
答：模式通过协调优化工具使用：
- **令牌效率**：上下文减少 30-50%
- **编排**：并行处理
- **任务管理**：通过系统化规划防止返工

**问：模式可以协同工作吗？**
答：是的，模式设计为互相补充：
- **任务管理**协调其他模式
- **令牌效率**压缩任何模式的输出
- **内省**为任何工作流添加透明度

---

## 总结

SuperClaude 的 5 种行为模式创建了一个**智能适应系统**，自动匹配您的需求：

- **🧠 头脑风暴**：将模糊想法转化为清晰需求
- **🔍 内省**：为学习和调试提供透明推理
- **📋 任务管理**：协调复杂的多步操作
- **🎯 编排**：优化工具选择和并行执行
- **⚡ 令牌效率**：在保持清晰度的同时压缩通信
- **🎨 标准**：为直接任务维护专业基线

**关键洞察**：您无需思考模式 - 它们透明地工作以增强您的开发体验。只需描述您想要完成的任务，SuperClaude 会自动调整其方法以匹配您的需求。

---

## 相关指南

**学习进展：**

**🌱 基础（第1周）**
- [快速开始指南](../Getting-Started/quick-start.md) - 模式激活示例
- [命令参考](commands.md) - 命令自动激活模式
- [安装指南](../Getting-Started/installation.md) - 设置行为模式

**🌿 中级（第2-3周）**
- [智能体指南](agents.md) - 模式如何与专家协调
- [标志指南](flags.md) - 手动模式控制和优化
- [示例手册](../Reference/examples-cookbook.md) - 实践中的模式模式

**🌲 高级（第2+个月）**
- [MCP 服务器](mcp-servers.md) - 模式与增强能力的集成
- [会话管理](session-management.md) - 任务管理模式工作流
- [入门指南](../Getting-Started/quick-start.md) - 模式使用模式

**🔧 专家级**
- [技术架构](../Developer-Guide/technical-architecture.md) - 模式实现细节
- [代码贡献](../Developer-Guide/contributing-code.md) - 扩展模式能力

**特定模式指南：**
- **头脑风暴**：[需求发现模式](../Reference/examples-cookbook.md#requirements)
- **任务管理**：[会话管理指南](session-management.md)
- **编排**：[MCP 服务器指南](mcp-servers.md)
- **令牌效率**：[命令基础](commands.md#token-efficiency)