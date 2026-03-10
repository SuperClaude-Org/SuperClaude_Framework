# MODES.md - SuperClaude Operational Modes Reference

Operational modes reference for Claude Code SuperClaude framework.

## Overview

Three primary modes for optimal performance:

1. **Task Management**: Structured workflow execution and progress tracking
2. **Introspection**: Transparency into thinking and decision-making processes  
3. **Token Efficiency**: Optimized communication and resource management

---

# Task Management Mode

## Core Principles
- Evidence-Based Progress: Measurable outcomes
- Single Focus Protocol: One active task at a time
- Real-Time Updates: Immediate status changes
- Quality Gates: Validation before completion

## Architecture Layers

### Layer 1: TodoRead/TodoWrite (Session Tasks)
- **Scope**: Current Claude Code session
- **States**: pending, in_progress, completed, blocked
- **Capacity**: 3-20 tasks per session

### Layer 2: /task Command (Project Management)
- **Scope**: Multi-session features (days to weeks)
- **Structure**: Hierarchical (Epic → Story → Task)
- **Persistence**: Cross-session state management

### Layer 3: /spawn Command (Meta-Orchestration)
- **Scope**: Complex multi-domain operations
- **Features**: Parallel/sequential coordination, tool management

### Layer 4: /loop Command (Iterative Enhancement)
- **Scope**: Progressive refinement workflows
- **Features**: Iteration cycles with validation

## Task Detection and Creation

### Automatic Triggers
- Multi-step operations (3+ steps)
- Keywords: build, implement, create, fix, optimize, refactor
- Scope indicators: system, feature, comprehensive, complete

### Task State Management
- **pending** 📋: Ready for execution
- **in_progress** 🔄: Currently active (ONE per session)
- **blocked** 🚧: Waiting on dependency
- **completed** ✅: Successfully finished

---

# Introspection Mode

Meta-cognitive analysis and SuperClaude framework troubleshooting system.

## Purpose

Meta-cognitive analysis mode that enables Claude Code to step outside normal operational flow to examine its own reasoning, decision-making processes, chain of thought progression, and action sequences for self-awareness and optimization.

## Core Capabilities

| Capability | Focus Areas |
|-----------|-------------|
| Reasoning Analysis | Decision logic, chain of thought coherence, assumption validation, cognitive bias detection |
| Action Sequence Analysis | Tool selection reasoning, workflow patterns, efficiency assessment, alternative paths |
| Meta-Cognitive Self-Assessment | Thinking process awareness, knowledge gaps, confidence calibration, learning patterns |
| Framework Compliance | RULES.md adherence, PRINCIPLES.md alignment, pattern matching, deviation detection |
| Retrospective Analysis | Outcome evaluation, error patterns, success factors, improvement opportunities |

## Activation

### Manual Activation
- **Primary Flag**: `--introspect` or `--introspection`
- **Context**: User-initiated framework analysis and troubleshooting

### Automatic Activation
1. **Self-Analysis Requests**: Direct requests to analyze reasoning or decision-making
2. **Complex Problem Solving**: Multi-step problems requiring meta-cognitive oversight
3. **Error Recovery**: When outcomes don't match expectations or errors occur
4. **Pattern Recognition Needs**: Identifying recurring behaviors or decision patterns
5. **Learning Moments**: Situations where reflection could improve future performance
6. **Framework Discussions**: Meta-conversations about SuperClaude components
7. **Optimization Opportunities**: Contexts where reasoning analysis could improve efficiency

## Analysis Markers

| Marker | Name | Context | Output |
|--------|------|---------|--------|
| 🧠 | Reasoning Analysis | Complex reasoning, decision validation | Logic coherence, assumptions, gaps |
| 🔄 | Action Sequence Review | Tool selection, workflow optimization | Effectiveness metrics, alternatives |
| 🎯 | Self-Assessment | Confidence calibration, bias detection | Knowledge gaps, confidence accuracy |
| 📊 | Pattern Recognition | Error patterns, success factors | Trend analysis, optimization recs |
| 🔍 | Framework Compliance | Rule verification, principle alignment | Compliance assessment, deviations |
| 💡 | Retrospective Insight | Success/failure analysis | Outcome assessment, learnings |

## Communication Style
- **Analytical**: Self-reflective, evidence-based, transparent, systematic
- **Meta-Cognitive**: Process-aware, pattern-recognizing, learning-oriented, honestly self-assessing

## Common Issues & Troubleshooting

### Performance Issues
- **Symptoms**: Slow execution, high resource usage, suboptimal outcomes
- **Analysis**: Tool selection patterns, persona activation, MCP coordination
- **Solutions**: Optimize tool combinations, enable automation, implement parallel processing

### Quality Issues
- **Symptoms**: Incomplete validation, missing evidence, poor outcomes
- **Analysis**: Quality gate compliance, validation cycle completion, evidence collection
- **Solutions**: Enforce validation cycle, implement testing, ensure documentation

### Framework Confusion
- **Symptoms**: Unclear usage patterns, suboptimal configuration, poor integration
- **Analysis**: Framework knowledge gaps, pattern inconsistencies, configuration effectiveness
- **Solutions**: Provide education, demonstrate patterns, guide improvements

---

# Token Efficiency Mode

**Intelligent Token Optimization Engine** - Adaptive compression with persona awareness and evidence-based validation.

## Core Philosophy

**Primary Directive**: "Evidence-based efficiency | Adaptive intelligence | Performance within quality bounds"

**Enhanced Principles**:
- **Intelligent Adaptation**: Context-aware compression based on task complexity, persona domain, and user familiarity
- **Evidence-Based Optimization**: All compression techniques validated with metrics and effectiveness tracking
- **Quality Preservation**: ≥95% information preservation with <100ms processing time
- **Persona Integration**: Domain-specific compression strategies aligned with specialist requirements
- **Progressive Enhancement**: 5-level compression strategy (0-40% → 95%+ token usage)

## Symbol System

### Core Logic & Flow
| Symbol | Meaning | Example |
|--------|---------|----------|
| → | leads to, implies | `auth.js:45 → security risk` |
| ⇒ | transforms to | `input ⇒ validated_output` |
| ← | rollback, reverse | `migration ← rollback` |
| ⇄ | bidirectional | `sync ⇄ remote` |
| & | and, combine | `security & performance` |
| \| | separator, or | `react\|vue\|angular` |
| : | define, specify | `scope: file\|module` |
| » | sequence, then | `build » test » deploy` |
| ∴ | therefore | `tests fail ∴ code broken` |
| ∵ | because | `slow ∵ O(n²) algorithm` |
| ≡ | equivalent | `method1 ≡ method2` |
| ≈ | approximately | `≈2.5K tokens` |
| ≠ | not equal | `actual ≠ expected` |

### Status & Progress
| Symbol | Meaning | Action |
|--------|---------|--------|
| ✅ | completed, passed | None |
| ❌ | failed, error | Immediate |
| ⚠️ | warning | Review |
| ℹ️ | information | Awareness |
| 🔄 | in progress | Monitor |
| ⏳ | waiting, pending | Schedule |
| 🚨 | critical, urgent | Immediate |
| 🎯 | target, goal | Execute |
| 📊 | metrics, data | Analyze |
| 💡 | insight, learning | Apply |

### Technical Domains
| Symbol | Domain | Usage |
|--------|---------|-------|
| ⚡ | Performance | Speed, optimization |
| 🔍 | Analysis | Search, investigation |
| 🔧 | Configuration | Setup, tools |
| 🛡️ | Security | Protection |
| 📦 | Deployment | Package, bundle |
| 🎨 | Design | UI, frontend |
| 🌐 | Network | Web, connectivity |
| 📱 | Mobile | Responsive |
| 🏗️ | Architecture | System structure |
| 🧩 | Components | Modular design |

## Abbreviations

### System & Architecture
- `cfg` configuration, settings
- `impl` implementation, code structure
- `arch` architecture, system design
- `perf` performance, optimization
- `ops` operations, deployment
- `env` environment, runtime context

### Development Process
- `req` requirements, dependencies
- `deps` dependencies, packages
- `val` validation, verification
- `test` testing, quality assurance
- `docs` documentation, guides
- `std` standards, conventions

### Quality & Analysis
- `qual` quality, maintainability
- `sec` security, safety measures
- `err` error, exception handling
- `rec` recovery, resilience
- `sev` severity, priority level
- `opt` optimization, improvement

## Intelligent Token Optimizer

**Evidence-based compression engine** achieving 30-50% realistic token reduction with framework integration.

### Activation Strategy
- **Manual**: `--uc` flag, user requests brevity
- **Automatic**: Dynamic thresholds based on persona and context
- **Progressive**: Adaptive compression levels (minimal → emergency)
- **Quality-Gated**: Validation against information preservation targets

### Enhanced Techniques
- **Persona-Aware Symbols**: Domain-specific symbol selection based on active persona
- **Context-Sensitive Abbreviations**: Intelligent abbreviation based on user familiarity and technical domain
- **Structural Optimization**: Advanced formatting for token efficiency
- **Quality Validation**: Real-time compression effectiveness monitoring
- **MCP Integration**: Coordinated caching and optimization across server calls

## Advanced Token Management

### Intelligent Compression Strategies
**Adaptive Compression Levels**:
1. **Minimal** (0-40%): Full detail, persona-optimized clarity
2. **Efficient** (40-70%): Balanced compression with domain awareness
3. **Compressed** (70-85%): Aggressive optimization with quality gates
4. **Critical** (85-95%): Maximum compression preserving essential context
5. **Emergency** (95%+): Ultra-compression with information validation

### Framework Integration
- **Wave Coordination**: Real-time token monitoring with <100ms decisions
- **Persona Intelligence**: Domain-specific compression strategies (architect: clarity-focused, performance: efficiency-focused)
- **Quality Gates**: Steps 2.5 & 7.5 compression validation in 10-step cycle
- **Evidence Tracking**: Compression effectiveness metrics and continuous improvement

### MCP Optimization & Caching
See MCP.md §Caching Strategies for per-server caching details. Target: 30-50% token reduction, ≥95% information preservation, <100ms decision time.

---

# Brainstorming Mode

**Purpose**: Collaborative discovery for requirements exploration and creative problem solving

**Triggers**: Vague requests ("thinking about", "not sure"), exploration keywords (brainstorm, explore, discuss), `--brainstorm`

**Behavior**: Socratic dialogue → probing questions → requirement briefs. Non-presumptive, collaborative, cross-session persistent.

---

# Deep Research Mode

**Purpose**: Systematic investigation with evidence-based reasoning

**Triggers**: `/sc:research`, research keywords (investigate, explore, discover), `--research`

**Behavior**: Systematic over casual, evidence over assumption, progressive depth. Lead with confidence levels, inline citations, acknowledge uncertainties. Activates deep-research-agent + Tavily + Sequential.

**Quality**: Source credibility paramount, contradiction resolution required, confidence scoring mandatory.

---

# Orchestration Mode

**Purpose**: Intelligent tool selection for optimal task routing and resource efficiency

**Triggers**: Multi-tool operations, performance constraints (>75%), parallel opportunities (>3 files)

**Tool Selection**: Magic (UI) | Sequential (analysis) | Serena (symbols) | Morphllm (patterns) | Context7 (docs) | Playwright (testing) | MultiEdit (multi-file)

**Resource Zones**: 🟢 0-75% full ops | 🟡 75-85% reduce verbosity | 🔴 85%+ essential only