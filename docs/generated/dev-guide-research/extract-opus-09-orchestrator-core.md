# Extraction: ORCHESTRATOR.md - Routing, Commands, Agents, and Skills Integration

**Source**: `/config/workspace/SuperClaude_Framework/src/superclaude/core/ORCHESTRATOR.md`
**Extracted**: 2026-02-21
**Focus**: All information relevant to developing custom commands, skills, or agents for the SuperClaude framework

---

## 1. Detection Engine: How Requests Are Analyzed Before Routing

The orchestrator begins by analyzing every request through a multi-stage detection engine. Understanding this engine is critical for anyone adding new commands or agents, because **your new component must be discoverable by these detection mechanisms**.

### 1.1 Pre-Operation Validation Checks

Before routing, the orchestrator validates three dimensions:

**Resource Validation**:
> - Token usage prediction based on operation complexity and scope
> - Memory and processing requirements estimation
> - File system permissions and available space verification
> - MCP server availability and response time checks

**Compatibility Validation**:
> - Flag combination conflict detection (e.g., `--no-mcp` with `--seq`)
> - Persona + command compatibility verification
> - Tool availability for requested operations
> - Project structure requirements validation

**Risk Assessment**:
> - Operation complexity scoring (0.0-1.0 scale)
> - Failure probability based on historical patterns
> - Resource exhaustion likelihood prediction
> - Cascading failure potential analysis

**Key threshold**: Operations with risk scores >0.8 trigger safe mode suggestions.

### 1.2 Resource Management Thresholds

These zones govern how aggressively the orchestrator allocates resources to any command or agent:

| Zone | Range | Behavior |
|------|-------|----------|
| Green | 0-60% | Full operations, predictive monitoring active |
| Yellow | 60-75% | Resource optimization, caching, suggest `--uc` mode |
| Orange | 75-85% | Warning alerts, defer non-critical operations |
| Red | 85-95% | Force efficiency modes, block resource-intensive operations |
| Critical | 95%+ | Emergency protocols, essential operations only |

**Implication for new commands**: A resource-heavy custom command may be deferred or blocked if the system enters Orange/Red zones. Design commands with token budgets in mind.

---

## 2. Pattern Recognition Rules: How Intent Is Detected

The detection engine uses three classification matrices. **New commands or agents must register their keywords, file patterns, and operation types in these matrices** to be properly routed.

### 2.1 Complexity Detection

```
| Level    | Indicators                                                          | Token Budget | Time      |
|----------|---------------------------------------------------------------------|-------------|-----------|
| Simple   | Single file, basic CRUD, straightforward queries, <3 steps         | 5K          | <5 min    |
| Moderate | Multi-file, analysis tasks, refactoring, 3-10 steps               | 15K         | 5-30 min  |
| Complex  | System-wide changes, architectural decisions, performance opt, >10 steps | 30K+   | >30 min   |
```

### 2.2 Domain Identification

The full domain matrix with keywords, file patterns, and typical operations:

```
| Domain          | Keywords                                                        | File Patterns                                      | Typical Ops                                         |
|-----------------|-----------------------------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
| Frontend        | UI, component, React, Vue, CSS, responsive, accessibility       | *.jsx, *.tsx, *.vue, *.css                         | create, implement, style, optimize, test            |
| Backend         | API, database, server, endpoint, authentication, performance    | *.js, *.ts, *.py, *.go, controllers/*, models/*    | implement, optimize, secure, scale                  |
| Infrastructure  | deploy, Docker, CI/CD, monitoring, scaling                      | Dockerfile, *.yml, .github/*, terraform/*          | setup, configure, automate, monitor                 |
| Security        | vulnerability, authentication, encryption, audit, compliance    | *auth*, *security*, *.pem, *.key                   | scan, harden, audit, fix                            |
| Documentation   | document, README, wiki, guide, commit, changelog                | *.md, *.rst, docs/*, README*, CHANGELOG*           | write, document, explain, localize                  |
| Iterative       | improve, refine, enhance, correct, polish, iterate, loop        | *.*                                                | improve, refine, enhance, correct, polish           |
| Wave-eligible   | comprehensive, systematically, enterprise, large-scale          | (complexity indicators)                            | comprehensive_improvement, systematic_optimization  |
```

**For new commands**: Add your domain's keywords and file patterns here so the detection engine can identify when your command should be activated.

### 2.3 Operation Type Classification

```
| Type           | Verbs                                              | Outputs                                 | Tools                                                |
|----------------|----------------------------------------------------|-----------------------------------------|------------------------------------------------------|
| Analysis       | analyze, review, explain, investigate, troubleshoot| insights, recommendations, reports      | Grep, Read, Sequential                               |
| Creation       | create, build, implement, generate, design         | new files, features, components         | Write, Magic, Context7                               |
| Implementation | implement, develop, code, construct                | working features, functional code       | Write, Edit, MultiEdit, Magic, Context7, Sequential  |
| Modification   | update, refactor, improve, optimize, fix           | edited files, improvements              | Edit, MultiEdit, Sequential                          |
| Debugging      | debug, fix, troubleshoot, resolve                  | fixes, root causes, solutions           | Grep, Sequential, Playwright                         |
| Iterative      | improve, refine, enhance, polish, iterate          | progressive improvements                | Sequential, Read, Edit, MultiEdit, TodoWrite         |
| Wave ops       | comprehensively, systematically, progressively     | comprehensive improvements              | Sequential, Task, Read, Edit, MultiEdit, Context7    |
```

### 2.4 Intent Extraction Algorithm

The exact 7-step algorithm the orchestrator follows:

```
1. Parse user request for keywords and patterns
2. Match against domain/operation matrices
3. Score complexity based on scope and steps
4. Evaluate wave opportunity scoring
5. Estimate resource requirements
6. Generate routing recommendation (traditional vs wave mode)
7. Apply auto-detection triggers for wave activation
```

### 2.5 Enhanced Wave Detection Algorithm

> - **Flag Overrides**: `--single-wave` disables, `--force-waves`/`--wave-mode` enables
> - **Scoring Factors**: Complexity (0.2-0.4), scale (0.2-0.3), operations (0.2), domains (0.1), flag modifiers (0.05-0.1)
> - **Thresholds**: Default 0.7, customizable via `--wave-threshold`, enterprise strategy lowers file thresholds
> - **Decision Logic**: Sum all indicators, trigger waves when total >= threshold

---

## 3. Routing Intelligence: How Detected Patterns Map to Execution

### 3.1 Wave Routing System

Wave-enabled commands use multi-stage execution. The control matrix:

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

**Wave-Enabled Commands** (two tiers):
- **Tier 1**: `/analyze`, `/build`, `/implement`, `/improve`
- **Tier 2**: `/design`, `/task`

**Wave Opportunity Scoring** (how the system decides to activate waves):
> - High Complexity >0.8: +0.4
> - Multiple Operation Types >2: +0.3
> - Critical Quality: +0.2
> - Large File Count >50: +0.1
> - Iterative Indicators: +0.2
> - Enterprise Scale: +0.15

**Wave Strategy Selection** mapping:
> Security -> `wave_validation` | Performance -> `progressive_waves` | Critical -> `wave_validation` | Multiple Ops -> `adaptive_waves` | Enterprise -> `enterprise_waves` | Default -> `systematic_waves`

**Wave Auto-Triggers** (exact conditions):
> - complexity >0.8 AND files >20 AND operation_types >2 -> --wave-count 5
> - domains >3 AND tokens >15K -> --adaptive-waves
> - production_deploy OR security_audit -> --wave-validation
> - files >100 AND complexity >0.7 AND domains >2 -> --enterprise-waves

**For new commands**: To make a command wave-enabled, it must (a) be registered in the Wave-Enabled Commands list, (b) have a complexity profile that can score >= 0.7, and (c) define which wave strategy it uses.

### 3.2 Master Routing Table

This is the complete routing table showing how patterns map to auto-activations:

| Pattern | Complexity | Domain | Auto-Activates | Confidence |
|---------|------------|--------|----------------|------------|
| "analyze architecture" | complex | infrastructure | architect persona, --ultrathink, Sequential | 95% |
| "create component" | simple | frontend | frontend persona, Magic, --uc | 90% |
| "implement feature" | moderate | any | domain-specific persona, Context7, Sequential | 88% |
| "implement API" | moderate | backend | backend persona, --seq, Context7 | 92% |
| "implement UI component" | simple | frontend | frontend persona, Magic, --c7 | 94% |
| "implement authentication" | complex | security | security persona, backend persona, --validate | 90% |
| "fix bug" | moderate | any | analyzer persona, --think, Sequential | 85% |
| "optimize performance" | complex | backend | performance persona, --think-hard, Playwright | 90% |
| "security audit" | complex | security | security persona, --ultrathink, Sequential | 95% |
| "write documentation" | moderate | documentation | scribe persona, --persona-scribe=en, Context7 | 95% |
| "improve iteratively" | moderate | iterative | intelligent persona, --seq, loop creation | 90% |
| "analyze large codebase" | complex | any | --delegate --parallel-dirs, domain specialists | 95% |
| "comprehensive audit" | complex | multi | --multi-agent --parallel-focus, specialized agents | 95% |
| "improve large system" | complex | any | --wave-mode --adaptive-waves | 90% |
| "security audit enterprise" | complex | security | --wave-mode --wave-validation | 95% |
| "modernize legacy system" | complex | legacy | --wave-mode --enterprise-waves --wave-checkpoint | 92% |
| "comprehensive code review" | complex | quality | --wave-mode --wave-validation --systematic-waves | 94% |
| "cleanup audit" | complex | quality | analyzer persona, --wave-mode --systematic-waves, Sequential + Serena | 95% |
| "repository audit" | complex | quality | analyzer persona, --delegate --multi-agent, 5 custom subagents | 95% |
| "dead code detection" | complex | quality | analyzer persona, --think-hard, Sequential | 90% |

**For new commands/agents**: Add rows to this table. Each row specifies: the trigger pattern (keyword phrase), complexity level, domain, what gets auto-activated (personas, flags, MCP servers), and routing confidence percentage.

---

## 4. Tier Classification Routing (Compliance Enforcement)

This system routes `/sc:task` commands to compliance tiers. It demonstrates how the orchestrator classifies and routes based on task characteristics.

### 4.1 Classification Decision Tree

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

### 4.2 Tier Priority Rules

| Priority | Tier | Triggers | Rationale |
|----------|------|----------|-----------|
| 1 | STRICT | security, auth, database, refactor, multi-file | Safety-critical changes |
| 2 | EXEMPT | explain, search, git status, brainstorm | Non-code work |
| 3 | LIGHT | typo, comment, formatting, minor | Trivial changes |
| 4 | STANDARD | add, implement, fix, update | Default development |

### 4.3 Context Boosters

| Signal | Tier Boost | Amount | Rationale |
|--------|------------|--------|-----------|
| estimated_files > 2 | STRICT | +0.3 | Multi-file changes need scrutiny |
| estimated_files == 1 | LIGHT | +0.1 | Single-file often simpler |
| security path detected | STRICT | +0.4 | auth/, security/, crypto/ paths |
| all test files | STANDARD | +0.2 | Tests are moderate risk |
| all doc files | EXEMPT | +0.5 | Docs are read-only equivalent |
| is_read_only | EXEMPT | +0.4 | No modifications needed |
| is_git_operation | EXEMPT | +0.5 | Git ops are metadata |

### 4.4 Compound Phrase Overrides

```yaml
light_compound_overrides:
  - "quick fix" -> LIGHT (overrides "fix" -> STANDARD)
  - "minor change" -> LIGHT (overrides "change" -> STANDARD)
  - "fix typo" -> LIGHT (overrides "fix" -> STANDARD)
  - "refactor comment" -> LIGHT (overrides "refactor" -> STRICT)

strict_compound_overrides:
  - "fix security" -> STRICT (overrides "fix" -> STANDARD)
  - "add authentication" -> STRICT (overrides "add" -> STANDARD)
  - "update database" -> STRICT (overrides "update" -> STANDARD)
  - "quick security" -> STRICT (security always wins)
  - "minor auth change" -> STRICT (auth changes never minor)
```

### 4.5 Tier-to-Verification Mapping

| Compliance Tier | Verification Method | Token Cost | Timeout |
|-----------------|---------------------|------------|---------|
| STRICT | Sub-agent (quality-engineer) | 3-5K | 60s |
| STANDARD | Direct test execution | 300-500 | 30s |
| LIGHT | Skip verification | 0 | 0s |
| EXEMPT | Skip verification | 0 | 0s |

---

## 5. Decision Trees: Tool Selection Logic

### 5.1 Base Tool Selection

> - **Search**: Grep (specific patterns) or Agent (open-ended)
> - **Understanding**: Sequential (complexity >0.7) or Read (simple)
> - **Documentation**: Context7
> - **UI**: Magic
> - **Testing**: Playwright

### 5.2 Delegation and Wave Evaluation

> - **Delegation Score >0.6**: Add Task tool, auto-enable delegation flags based on scope
> - **Wave Score >0.7**: Add Sequential for coordination, auto-enable wave strategies

### 5.3 Auto-Flag Assignment

> - Directory count >7 -> `--delegate --parallel-dirs`
> - Focus areas >2 -> `--multi-agent --parallel-focus`
> - High complexity + critical quality -> `--wave-mode --wave-validation`
> - Multiple operation types -> `--wave-mode --adaptive-waves`

**For new commands**: Define which tools your command needs and under what conditions delegation or wave modes should activate.

---

## 6. Task Delegation Intelligence

### 6.1 Delegation Scoring Factors

> - Complexity >0.6: +0.3
> - Parallelizable Operations: +0.4 (scaled)
> - Token >15K: +0.2
> - Multi-domain >2: +0.1/domain

### 6.2 Auto-Delegation Triggers

| Condition | Action | Confidence |
|-----------|--------|------------|
| directory_count > 7 | --delegate --parallel-dirs | 95% |
| file_count > 50 AND complexity > 0.6 | --delegate --sub-agents | 90% |
| domains > 3 | --delegate --parallel-focus | 85% |
| complexity > 0.8 AND scope = comprehensive | --delegate --focus-agents | 90% |
| estimated_tokens > 20000 | --delegate --aggregate-results | 80% |

### 6.3 Delegation Routing Table

| Operation | Complexity | Auto-Delegates | Gain |
|-----------|------------|----------------|------|
| `/load @monorepo/` | moderate | --delegate --parallel-dirs | 65% |
| `/analyze --comprehensive` | high | --multi-agent --parallel-focus | 70% |
| Comprehensive system improvement | high | --wave-mode --progressive-waves | 80% |
| Enterprise security audit | high | --wave-mode --wave-validation | 85% |
| Large-scale refactoring | high | --wave-mode --systematic-waves | 75% |

### 6.4 Sub-Agent Specialization Matrix

Standard sub-agent types and their tool allocations:

> - **Quality**: qa persona, complexity/maintainability, Read/Grep/Sequential
> - **Security**: security persona, vulnerabilities/compliance, Grep/Sequential/Context7
> - **Performance**: performance persona, bottlenecks/optimization, Read/Sequential/Playwright
> - **Architecture**: architect persona, patterns/structure, Read/Sequential/Context7
> - **API**: backend persona, endpoints/contracts, Grep/Context7/Sequential

### 6.5 Wave-Specific Specialization

> - **Review**: analyzer -> Read/Grep/Sequential
> - **Planning**: architect -> Sequential/Context7/Write
> - **Implementation**: domain-specific -> Edit/MultiEdit/Task
> - **Validation**: qa -> Sequential/Playwright/Context7
> - **Optimization**: performance -> Read/Sequential/Grep

**For new agents**: Register your agent in the Sub-Agent Specialization Matrix. Define its persona, focus area, and tool set.

---

## 7. Persona and Flag Auto-Activation

### 7.1 Context-Based Flag Auto-Activation

The complete auto-activation mapping:

> - Performance issues -> --persona-performance + --focus performance + --think
> - Security concerns -> --persona-security + --focus security + --validate
> - UI/UX tasks -> --persona-frontend + --magic + --c7
> - Complex debugging -> --think + --seq + --persona-analyzer
> - Large codebase -> --uc when context >75% + --delegate auto
> - Testing -> --persona-qa + --play + --validate
> - DevOps -> --persona-devops + --safe-mode + --validate
> - Refactoring -> --persona-refactorer + --wave-strategy systematic + --validate
> - Iterative improvement -> --loop for polish, refine, enhance keywords

### 7.2 Flag Precedence Rules (Complete List)

> 1. Safety flags (--safe-mode) > optimization flags
> 2. Explicit flags > auto-activation
> 3. Thinking depth: --ultrathink > --think-hard > --think
> 4. --no-mcp overrides all individual MCP flags
> 5. Scope: system > project > module > file
> 6. Last specified persona takes precedence
> 7. Wave mode: --wave-mode off > --wave-mode force > --wave-mode auto
> 8. Sub-Agent delegation: explicit --delegate > auto-detection
> 9. Loop mode: explicit --loop > auto-detection
> 10. --uc auto-activation overrides verbose flags

**For new commands/agents**: Your flags must respect this precedence hierarchy. Safety flags always override your command's optimizations.

---

## 8. Confidence Scoring

How the orchestrator evaluates routing confidence:

> Based on pattern match strength (40%), historical success rate (30%), context completeness (20%), resource availability (10%).

**For new commands**: Aim for >= 85% confidence in your routing table entries by ensuring strong keyword matching and clear domain identification.

---

## 9. Quality Gates and Validation Framework

### 9.1 8-Step Validation Cycle

> 1. Syntax (parsers, Context7)
> 2. Types (Sequential)
> 3. Lint (Context7)
> 4. Security (Sequential, OWASP)
> 5. Test (Playwright, >=80% unit / >=70% integration)
> 6. Performance (Sequential, benchmarks)
> 7. Docs (Context7, completeness)
> 8. Integration (Playwright, deployment)

### 9.2 Task Completion Criteria

> All 8 gates pass, evidence provided, metrics documented. MCP coordination active, >=90% context retention. Quality standards, security compliance, integration testing verified.

---

## 10. Performance Optimization

### 10.1 Token Management

> Intelligent resource allocation based on Resource Management Thresholds (see Detection Engine).

### 10.2 Resource Allocation by Component

> - **Detection Engine**: 1-2K tokens for pattern analysis
> - **Decision Trees**: 500-1K tokens for routing logic
> - **MCP Coordination**: Variable based on servers activated

---

## 11. Integration Intelligence

### 11.1 MCP Server Selection (Quick Reference)

> Context7 (docs) | Sequential (analysis) | Magic (UI) | Playwright (testing)

### 11.2 Cross-References

> - See MCP.md for detailed server capabilities, workflows, and integration patterns.
> - See PERSONAS.md for detailed persona specifications and MCP server preferences.

---

## 12. Emergency Protocols

### 12.1 Graceful Degradation Levels

> - **Level 1**: Reduce verbosity, skip optional enhancements, use cached results
> - **Level 2**: Disable advanced features, simplify operations, batch aggressively
> - **Level 3**: Essential operations only, maximum compression, queue non-critical

### 12.2 Error Recovery Patterns

> - **MCP Timeout**: Use fallback server (see MCP.md Circuit Breaker Configuration)
> - **Token Limit**: Activate compression
> - **Tool Failure**: Try alternative tool
> - **Parse Error**: Request clarification

**For new commands**: Define fallback behavior for each error recovery scenario your command might encounter.

---

## 13. Configuration: Orchestrator Settings

> Caching: TTL 3600s. Parallel: max 3. Learning: enabled. Confidence threshold: 0.7. Pattern detection: aggressive. Token reserve: 10%. Emergency: 90%. Compression: 75%. Wave: auto-detect at 0.7, max 5 waves, adaptive sizing, validation required.

---

## 14. Summary: Integration Checklist for New Commands/Agents/Skills

Based on the orchestrator's architecture, a new command, agent, or skill must integrate with these systems:

1. **Detection Engine Registration**: Add keywords to Domain Identification table, add verbs to Operation Type Classification, define complexity level
2. **Master Routing Table Entry**: Add a row with pattern, complexity, domain, auto-activations, and confidence score
3. **Tool Selection**: Define which tools (Read, Write, Edit, Grep, etc.) and MCP servers (Sequential, Context7, Magic, Playwright) the component uses
4. **Persona Association**: Specify which personas auto-activate and which MCP servers are primary/secondary
5. **Wave Eligibility** (if applicable): Define wave strategy, opportunity scoring factors, and auto-trigger conditions
6. **Delegation Rules** (if applicable): Add to the Delegation Routing Table and Sub-Agent Specialization Matrix
7. **Flag Integration**: Define which flags apply, and ensure compliance with the 10-rule Flag Precedence hierarchy
8. **Compliance Tier** (for task-type commands): Register keywords in the Tier Priority Rules and add any compound phrase overrides
9. **Quality Gates**: Define which of the 8 validation steps apply to your component
10. **Error Recovery**: Define fallback behavior for MCP timeouts, token limits, and tool failures
11. **Resource Budget**: Specify expected token budget (5K/15K/30K+) and time estimate
12. **Confidence Target**: Aim for routing confidence >= 85% via strong keyword matching
