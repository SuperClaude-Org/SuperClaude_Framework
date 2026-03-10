# Extraction: Custom commands/skills/agents guidance from orchestrator core

Source: `/config/workspace/SuperClaude_Framework/src/superclaude/core/ORCHESTRATOR.md`

This document extracts **all content in the source file that informs how to develop/customize SuperClaude commands, skills, or agents**—primarily via routing logic (intent detection, wave/delegation decisions), tool/persona auto-activation, and validation frameworks.

---

## 1) What the Orchestrator is (scope for implementers)

> "# ORCHESTRATOR.md - SuperClaude Intelligent Routing System"
>
> "Intelligent routing system for Claude Code SuperClaude framework."

Implication for custom commands/skills/agents: the orchestrator is the *policy layer* that decides which personas/tools/modes to activate and when to escalate into wave/delegation patterns.

---

## 2) Detection Engine (what your command/skill/agent must be compatible with)

### 2.1 Pre-operation validation checks

When building a command/skill/agent, ensure it can operate under these pre-checks and that your flags/tools/personas fit the compatibility model.

> "### Pre-Operation Validation Checks"
>
> "**Resource Validation**:
> - Token usage prediction based on operation complexity and scope
> - Memory and processing requirements estimation
> - File system permissions and available space verification
> - MCP server availability and response time checks"
>
> "**Compatibility Validation**:
> - Flag combination conflict detection (e.g., `--no-mcp` with `--seq`)
> - Persona + command compatibility verification
> - Tool availability for requested operations
> - Project structure requirements validation"
>
> "**Risk Assessment**:
> - Operation complexity scoring (0.0-1.0 scale)
> - Failure probability based on historical patterns
> - Resource exhaustion likelihood prediction
> - Cascading failure potential analysis"
>
> "**Validation Logic**: Resource availability, flag compatibility, risk assessment, outcome prediction, and safety recommendations. Operations with risk scores >0.8 trigger safe mode suggestions."

### 2.2 Resource management thresholds (designing command behavior under load)

Commands/skills/agents should degrade or reduce scope as resource pressure rises.

> "**Resource Management Thresholds**:
> - **Green Zone** (0-60%): Full operations, predictive monitoring active
> - **Yellow Zone** (60-75%): Resource optimization, caching, suggest --uc mode
> - **Orange Zone** (75-85%): Warning alerts, defer non-critical operations
> - **Red Zone** (85-95%): Force efficiency modes, block resource-intensive operations
> - **Critical Zone** (95%+): Emergency protocols, essential operations only"

---

## 3) Pattern recognition rules (inputs your custom command should map to)

These tables define how requests are categorized. When adding a new command/skill/agent, align naming/keywords and expected file patterns to fit this classification.

### 3.1 Complexity detection

> "#### Complexity Detection"
>
> "| Level | Indicators | Token Budget | Time |
> |-------|-----------|-------------|------|
> | Simple | Single file, basic CRUD, straightforward queries, <3 steps | 5K | <5 min |
> | Moderate | Multi-file, analysis tasks, refactoring, 3-10 steps | 15K | 5-30 min |
> | Complex | System-wide changes, architectural decisions, performance opt, >10 steps | 30K+ | >30 min |"

### 3.2 Domain identification

This directly impacts persona selection and tool routing.

> "#### Domain Identification"
>
> "| Domain | Keywords | File Patterns | Typical Ops |
> |--------|---------|--------------|-------------|
> | Frontend | UI, component, React, Vue, CSS, responsive, accessibility | *.jsx, *.tsx, *.vue, *.css | create, implement, style, optimize, test |
> | Backend | API, database, server, endpoint, authentication, performance | *.js, *.ts, *.py, *.go, controllers/*, models/* | implement, optimize, secure, scale |
> | Infrastructure | deploy, Docker, CI/CD, monitoring, scaling | Dockerfile, *.yml, .github/*, terraform/* | setup, configure, automate, monitor |
> | Security | vulnerability, authentication, encryption, audit, compliance | *auth*, *security*, *.pem, *.key | scan, harden, audit, fix |
> | Documentation | document, README, wiki, guide, commit, changelog | *.md, *.rst, docs/*, README*, CHANGELOG* | write, document, explain, localize |
> | Iterative | improve, refine, enhance, correct, polish, iterate, loop | *.* | improve, refine, enhance, correct, polish |
> | Wave-eligible | comprehensive, systematically, enterprise, large-scale | (complexity indicators) | comprehensive_improvement, systematic_optimization |"

### 3.3 Operation type classification (drives tool choices)

If you add a custom command, it should declare/behave like one of these operation types so the orchestrator can route tools correctly.

> "#### Operation Type Classification"
>
> "| Type | Verbs | Outputs | Tools |
> |------|-------|---------|-------|
> | Analysis | analyze, review, explain, investigate, troubleshoot | insights, recommendations, reports | Grep, Read, Sequential |
> | Creation | create, build, implement, generate, design | new files, features, components | Write, Magic, Context7 |
> | Implementation | implement, develop, code, construct | working features, functional code | Write, Edit, MultiEdit, Magic, Context7, Sequential |
> | Modification | update, refactor, improve, optimize, fix | edited files, improvements | Edit, MultiEdit, Sequential |
> | Debugging | debug, fix, troubleshoot, resolve | fixes, root causes, solutions | Grep, Sequential, Playwright |
> | Iterative | improve, refine, enhance, polish, iterate | progressive improvements | Sequential, Read, Edit, MultiEdit, TodoWrite |
> | Wave ops | comprehensively, systematically, progressively | comprehensive improvements | Sequential, Task, Read, Edit, MultiEdit, Context7 |"

---

## 4) Intent extraction algorithm (what your command must “fit into”)

Custom commands/skills/agents should be designed so their invocation text and flags can be parsed by this pipeline.

> "### Intent Extraction Algorithm"
>
> "```
> 1. Parse user request for keywords and patterns
> 2. Match against domain/operation matrices
> 3. Score complexity based on scope and steps
> 4. Evaluate wave opportunity scoring
> 5. Estimate resource requirements
> 6. Generate routing recommendation (traditional vs wave mode)
> 7. Apply auto-detection triggers for wave activation
> ```"

### 4.1 Enhanced wave detection algorithm (for wave-enabled command design)

> "**Enhanced Wave Detection Algorithm**:
> - **Flag Overrides**: `--single-wave` disables, `--force-waves`/`--wave-mode` enables
> - **Scoring Factors**: Complexity (0.2-0.4), scale (0.2-0.3), operations (0.2), domains (0.1), flag modifiers (0.05-0.1)
> - **Thresholds**: Default 0.7, customizable via `--wave-threshold`, enterprise strategy lowers file thresholds
> - **Decision Logic**: Sum all indicators, trigger waves when total ≥ threshold"

---

## 5) Routing intelligence (how commands should declare wave support & orchestration)

### 5.1 Wave routing (control matrix, strategies, and command eligibility)

If you create a new command intended to be wave-enabled, it must support these activation paths and strategy concepts.

> "### Wave Routing (Consolidated)"
>
> "Multi-stage command execution with compound intelligence. Automatic complexity assessment or explicit flag control."

Wave control matrix (exact YAML):

```yaml
wave-activation:
  automatic: "complexity >= 0.7"
  explicit: "--wave-mode, --force-waves"
  override: "--single-wave, --wave-dry-run"

wave-strategies:
  progressive: "Incremental enhancement"
  systematic: "Methodical analysis"
  adaptive: "Dynamic configuration"
```

Wave-enabled commands list (important for command development decisions and naming consistency):

> "**Wave-Enabled Commands**:
> - **Tier 1**: `/analyze`, `/build`, `/implement`, `/improve`
> - **Tier 2**: `/design`, `/task`"

Wave opportunity scoring (signals your command could hook into):

> "**Wave Opportunity Scoring**:
> - High Complexity >0.8: +0.4 | Multiple Operation Types >2: +0.3 | Critical Quality: +0.2
> - Large File Count >50: +0.1 | Iterative Indicators: +0.2 | Enterprise Scale: +0.15"

Wave strategy selection rules (used to select *how* your command should orchestrate):

> "**Wave Strategy Selection**: Security → `wave_validation` | Performance → `progressive_waves` | Critical → `wave_validation` | Multiple Ops → `adaptive_waves` | Enterprise → `enterprise_waves` | Default → `systematic_waves`"

Wave auto-triggers (conditions a custom command should respect if it operates at scale):

> "**Wave Auto-Triggers**:
> - complexity >0.8 AND files >20 AND operation_types >2 → --wave-count 5
> - domains >3 AND tokens >15K → --adaptive-waves
> - production_deploy OR security_audit → --wave-validation
> - files >100 AND complexity >0.7 AND domains >2 → --enterprise-waves"

### 5.2 Master routing table (patterns to auto-activate personas/tools)

For custom commands, you can align your command’s phrasing/purpose with these patterns so it triggers the intended routing behavior.

> "### Master Routing Table"
>
> "| Pattern | Complexity | Domain | Auto-Activates | Confidence |
> |---------|------------|---------|----------------|------------|
> | \"analyze architecture\" | complex | infrastructure | architect persona, --ultrathink, Sequential | 95% |
> | \"create component\" | simple | frontend | frontend persona, Magic, --uc | 90% |
> | \"implement feature\" | moderate | any | domain-specific persona, Context7, Sequential | 88% |
> | \"implement API\" | moderate | backend | backend persona, --seq, Context7 | 92% |
> | \"implement UI component\" | simple | frontend | frontend persona, Magic, --c7 | 94% |
> | \"implement authentication\" | complex | security | security persona, backend persona, --validate | 90% |
> | \"fix bug\" | moderate | any | analyzer persona, --think, Sequential | 85% |
> | \"optimize performance\" | complex | backend | performance persona, --think-hard, Playwright | 90% |
> | \"security audit\" | complex | security | security persona, --ultrathink, Sequential | 95% |
> | \"write documentation\" | moderate | documentation | scribe persona, --persona-scribe=en, Context7 | 95% |
> | \"improve iteratively\" | moderate | iterative | intelligent persona, --seq, loop creation | 90% |
> | \"analyze large codebase\" | complex | any | --delegate --parallel-dirs, domain specialists | 95% |
> | \"comprehensive audit\" | complex | multi | --multi-agent --parallel-focus, specialized agents | 95% |
> | \"improve large system\" | complex | any | --wave-mode --adaptive-waves | 90% |
> | \"security audit enterprise\" | complex | security | --wave-mode --wave-validation | 95% |
> | \"modernize legacy system\" | complex | legacy | --wave-mode --enterprise-waves --wave-checkpoint | 92% |
> | \"comprehensive code review\" | complex | quality | --wave-mode --wave-validation --systematic-waves | 94% |
> | \"cleanup audit\" | complex | quality | analyzer persona, --wave-mode --systematic-waves, Sequential + Serena | 95% |
> | \"repository audit\" | complex | quality | analyzer persona, --delegate --multi-agent, 5 custom subagents | 95% |
> | \"dead code detection\" | complex | quality | analyzer persona, --think-hard, Sequential | 90% |"

---

## 6) Compliance enforcement routing (relevant to implementing commands like `/sc:task`)

### 6.1 Purpose & decision tree

If you develop or extend task-like commands, this is the canonical tiering model.

> "### Tier Classification Routing (Compliance Enforcement)"
>
> "**Purpose**: Route `/sc:task` commands to appropriate compliance tier based on task characteristics."

Exact YAML decision tree:

```yaml
tier_classification:
  step_1_override:
    condition: "user_override_tier != null"
    action: "use override tier with 100% confidence"

  step_2_compound:
    condition: "compound_phrase_detected"
    action: "use compound phrase tier with 90% confidence"

  step_3_keywords:
    action: "score all keywords, apply context boosters"
    scoring: "sum(keyword_matches * weight) + context_boosts"

  step_4_resolve:
    condition: "scores within 0.1 of each other"
    action: "escalate to higher priority tier"
    priority: "STRICT > EXEMPT > LIGHT > STANDARD"

  step_5_confidence:
    condition: "confidence < 0.7"
    action: "prompt user for confirmation"
```

### 6.2 Tier priority rules

> "#### Tier Priority Rules"
>
> "| Priority | Tier | Triggers | Rationale |
> |----------|------|----------|-----------|
> | 1 | STRICT | security, auth, database, refactor, multi-file | Safety-critical changes |
> | 2 | EXEMPT | explain, search, git status, brainstorm | Non-code work |
> | 3 | LIGHT | typo, comment, formatting, minor | Trivial changes |
> | 4 | STANDARD | add, implement, fix, update | Default development |"

### 6.3 Context boosters (signals that adjust compliance tier)

> "#### Context Boosters"
>
> "| Signal | Tier Boost | Amount | Rationale |
> |--------|------------|--------|-----------|
> | estimated_files > 2 | STRICT | +0.3 | Multi-file changes need scrutiny |
> | estimated_files == 1 | LIGHT | +0.1 | Single-file often simpler |
> | security path detected | STRICT | +0.4 | auth/, security/, crypto/ paths |
> | all test files | STANDARD | +0.2 | Tests are moderate risk |
> | all doc files | EXEMPT | +0.5 | Docs are read-only equivalent |
> | is_read_only | EXEMPT | +0.4 | No modifications needed |
> | is_git_operation | EXEMPT | +0.5 | Git ops are metadata |"

### 6.4 Compound phrase overrides (how phrasing affects tier)

Exact YAML:

```yaml
light_compound_overrides:
  - "quick fix" → LIGHT (overrides "fix" → STANDARD)
  - "minor change" → LIGHT (overrides "change" → STANDARD)
  - "fix typo" → LIGHT (overrides "fix" → STANDARD)
  - "refactor comment" → LIGHT (overrides "refactor" → STRICT)

strict_compound_overrides:
  - "fix security" → STRICT (overrides "fix" → STANDARD)
  - "add authentication" → STRICT (overrides "add" → STANDARD)
  - "update database" → STRICT (overrides "update" → STANDARD)
  - "quick security" → STRICT (security always wins)
  - "minor auth change" → STRICT (auth changes never minor)
```

### 6.5 Tier-to-verification mapping (how strictness impacts toolchain)

> "#### Tier-to-Verification Mapping"
>
> "| Compliance Tier | Verification Method | Token Cost | Timeout |
> |-----------------|---------------------|------------|---------|
> | STRICT | Sub-agent (quality-engineer) | 3-5K | 60s |
> | STANDARD | Direct test execution | 300-500 | 30s |
> | LIGHT | Skip verification | 0 | 0s |
> | EXEMPT | Skip verification | 0 | 0s |"

---

## 7) Tool selection logic (guidance for command/skill implementation)

When building a skill or command, align your internal steps with this tool-selection model.

> "#### Tool Selection Logic"
>
> "**Base Tool Selection**:
> - **Search**: Grep (specific patterns) or Agent (open-ended)
> - **Understanding**: Sequential (complexity >0.7) or Read (simple)
> - **Documentation**: Context7
> - **UI**: Magic
> - **Testing**: Playwright"
>
> "**Delegation & Wave Evaluation**:
> - **Delegation Score >0.6**: Add Task tool, auto-enable delegation flags based on scope
> - **Wave Score >0.7**: Add Sequential for coordination, auto-enable wave strategies"
>
> "**Auto-Flag Assignment**:
> - Directory count >7 → `--delegate --parallel-dirs`
> - Focus areas >2 → `--multi-agent --parallel-focus`
> - High complexity + critical quality → `--wave-mode --wave-validation`
> - Multiple operation types → `--wave-mode --adaptive-waves`"

---

## 8) Task delegation intelligence (agent/sub-agent development guidance)

This section is the most directly relevant for designing *agents* (including specialized sub-agents) and knowing when the system should delegate.

### 8.1 Delegation scoring factors and triggers

> "**Delegation Scoring Factors**:
> - Complexity >0.6: +0.3 | Parallelizable Operations: +0.4 (scaled) | Token >15K: +0.2 | Multi-domain >2: +0.1/domain"

> "**Auto-Delegation Triggers**:
> | Condition | Action | Confidence |
> |-----------|--------|------------|
> | directory_count > 7 | --delegate --parallel-dirs | 95% |
> | file_count > 50 AND complexity > 0.6 | --delegate --sub-agents | 90% |
> | domains > 3 | --delegate --parallel-focus | 85% |
> | complexity > 0.8 AND scope = comprehensive | --delegate --focus-agents | 90% |
> | estimated_tokens > 20000 | --delegate --aggregate-results | 80% |"

### 8.2 Delegation routing table (what types of operations delegate)

> "**Delegation Routing Table**:
>
> | Operation | Complexity | Auto-Delegates | Gain |
> |-----------|------------|----------------|------|
> | `/load @monorepo/` | moderate | --delegate --parallel-dirs | 65% |
> | `/analyze --comprehensive` | high | --multi-agent --parallel-focus | 70% |
> | Comprehensive system improvement | high | --wave-mode --progressive-waves | 80% |
> | Enterprise security audit | high | --wave-mode --wave-validation | 85% |
> | Large-scale refactoring | high | --wave-mode --systematic-waves | 75% |"

### 8.3 Sub-agent specialization matrix (how to define agent roles)

If you add new agents, this mapping defines intended specialization boundaries.

> "**Sub-Agent Specialization Matrix**:
> - **Quality**: qa persona, complexity/maintainability, Read/Grep/Sequential
> - **Security**: security persona, vulnerabilities/compliance, Grep/Sequential/Context7
> - **Performance**: performance persona, bottlenecks/optimization, Read/Sequential/Playwright
> - **Architecture**: architect persona, patterns/structure, Read/Sequential/Context7
> - **API**: backend persona, endpoints/contracts, Grep/Context7/Sequential"

### 8.4 Wave-specific specialization (roles across wave phases)

> "**Wave-Specific Specialization**:
> - **Review**: analyzer → Read/Grep/Sequential
> - **Planning**: architect → Sequential/Context7/Write
> - **Implementation**: domain-specific → Edit/MultiEdit/Task
> - **Validation**: qa → Sequential/Playwright/Context7
> - **Optimization**: performance → Read/Sequential/Grep"

---

## 9) Persona & flag auto-activation (how to make your command trigger the right personas)

### 9.1 Persona activation reference

> "**Persona Activation**: See PERSONAS.md for detailed persona specifications, MCP preferences, and auto-activation triggers."

### 9.2 Context-based flag auto-activation rules

If you add a new command, these are the rules that should remain consistent with expected behavior.

> "**Context-Based Flag Auto-Activation**:
> - Performance issues → --persona-performance + --focus performance + --think
> - Security concerns → --persona-security + --focus security + --validate
> - UI/UX tasks → --persona-frontend + --magic + --c7
> - Complex debugging → --think + --seq + --persona-analyzer
> - Large codebase → --uc when context >75% + --delegate auto
> - Testing → --persona-qa + --play + --validate
> - DevOps → --persona-devops + --safe-mode + --validate
> - Refactoring → --persona-refactorer + --wave-strategy systematic + --validate
> - Iterative improvement → --loop for polish, refine, enhance keywords"

### 9.3 Flag precedence rules (important when extending command flags)

> "#### Flag Precedence Rules
> 1. Safety flags (--safe-mode) > optimization flags
> 2. Explicit flags > auto-activation
> 3. Thinking depth: --ultrathink > --think-hard > --think
> 4. --no-mcp overrides all individual MCP flags
> 5. Scope: system > project > module > file
> 6. Last specified persona takes precedence
> 7. Wave mode: --wave-mode off > --wave-mode force > --wave-mode auto
> 8. Sub-Agent delegation: explicit --delegate > auto-detection
> 9. Loop mode: explicit --loop > auto-detection
> 10. --uc auto-activation overrides verbose flags"

---

## 10) Confidence scoring (for routing decisions in new commands)

> "### Confidence Scoring"
>
> "Based on pattern match strength (40%), historical success rate (30%), context completeness (20%), resource availability (10%)."

---

## 11) Quality gates & validation framework (for command/skill/agent completion definitions)

If your custom command performs implementation work (not just read-only), align completion with this validation model.

### 11.1 8-step validation cycle

> "### 8-Step Validation Cycle"
>
> "1. Syntax (parsers, Context7) → 2. Types (Sequential) → 3. Lint (Context7) → 4. Security (Sequential, OWASP) → 5. Test (Playwright, ≥80% unit/≥70% integration) → 6. Performance (Sequential, benchmarks) → 7. Docs (Context7, completeness) → 8. Integration (Playwright, deployment)"

### 11.2 Task completion criteria

> "### Task Completion Criteria"
>
> "All 8 gates pass, evidence provided, metrics documented. MCP coordination active, ≥90% context retention. Quality standards, security compliance, integration testing verified."

---

## 12) Performance optimization guidance (for tool orchestration inside commands)

> "## ⚡ Performance Optimization"
>
> "**Token Management**: Intelligent resource allocation based on Resource Management Thresholds (see Detection Engine)."
>
> "**Operation Batching**: See RULES.md §Planning Efficiency for parallel-first doctrine. Tool coordination uses parallel operations when no dependencies, context sharing across routing decisions, and cache for session reuse."
>
> "**Resource Allocation**:
> - **Detection Engine**: 1-2K tokens for pattern analysis
> - **Decision Trees**: 500-1K tokens for routing logic
> - **MCP Coordination**: Variable based on servers activated"

---

## 13) Integration intelligence references (where to look when implementing command integrations)

> "## 🔗 Integration Intelligence"
>
> "### MCP Server Selection"
> "**Reference**: See MCP.md for detailed server capabilities, workflows, and integration patterns."
>
> "**Quick Selection**: Context7 (docs) | Sequential (analysis) | Magic (UI) | Playwright (testing)"
>
> "### Persona Integration"
> "**Reference**: See PERSONAS.md for detailed persona specifications and MCP server preferences."

---

## 14) Emergency protocols (what your commands should do when things go wrong)

### 14.1 Graceful degradation levels

> "### Graceful Degradation"
>
> "- **Level 1**: Reduce verbosity, skip optional enhancements, use cached results
> - **Level 2**: Disable advanced features, simplify operations, batch aggressively
> - **Level 3**: Essential operations only, maximum compression, queue non-critical"

### 14.2 Error recovery patterns

> "### Error Recovery Patterns"
>
> "- **MCP Timeout**: Use fallback server (see MCP.md §Circuit Breaker Configuration)
> - **Token Limit**: Activate compression
> - **Tool Failure**: Try alternative tool
> - **Parse Error**: Request clarification"

---

## 15) Orchestrator configuration defaults (constants to respect when extending)

> "### Orchestrator Settings"
>
> "Caching: TTL 3600s. Parallel: max 3. Learning: enabled. Confidence threshold: 0.7. Pattern detection: aggressive. Token reserve: 10%. Emergency: 90%. Compression: 75%. Wave: auto-detect at 0.7, max 5 waves, adaptive sizing, validation required."
