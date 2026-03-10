# Modular Firewalled Agentic Development: Comprehensive Research Report

**Date**: January 23, 2026
**Research Focus**: Breaking down large specifications into isolated modules for AI/LLM agent development with minimal cross-module context requirements

---

## Executive Summary

This research investigates methodologies, frameworks, and best practices for **modular, firewalled agentic development** - an approach where large specifications are decomposed into isolated modules that AI agents can develop independently with minimal context of the overall system.

### Key Findings

1. **MASAI Architecture** (Microsoft Research, 2024) achieved state-of-the-art results by decomposing software engineering into sub-agents with well-defined objectives
2. **Self-Organized Agents (SoA)** enables ultra-large-scale code generation by dynamically scaling agents based on complexity while keeping individual context windows manageable
3. **12-Factor Agents Framework** provides principles specifically designed for LLM context limitations
4. **Hexagonal Architecture (Ports & Adapters)** offers proven interface contract patterns for module isolation
5. **Spec-Driven Development (SDD)** is gaining momentum as the methodology to guide AI agent development with structured specifications

---

## 1. Academic Papers & Research Foundations

### 1.1 MASAI: Modular Architecture for Software-engineering AI Agents

**Source**: Microsoft Research India, arXiv:2406.11638 (June 2024)

**Core Concept**: Divide complex software engineering problems into multiple sub-problems, with different LLM-powered sub-agents instantiated with well-defined objectives and strategies.

**Key Advantages**:
1. **Strategy Customization**: Different problem-solving strategies across sub-agents
2. **Distributed Information Gathering**: Sub-agents gather from different repository sources
3. **Context Optimization**: Avoids unnecessarily long trajectories that inflate costs and add extraneous context

**Results**: Achieved 28.33% resolution rate on SWE-bench Lite (state-of-the-art at time of publication)

**Architecture Pattern**:
```
┌─────────────────────────────────────────────────────────┐
│                    MASAI Framework                       │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Localization │   Analysis   │   Planning   │ Execution  │
│   Sub-Agent   │  Sub-Agent   │  Sub-Agent   │ Sub-Agent  │
├──────────────┴──────────────┴──────────────┴────────────┤
│              Well-Defined Interfaces                     │
│           (Each agent: specific objectives)              │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Self-Organized Agents (SoA)

**Source**: TsukushiAI, arXiv:2404.02183 (April 2024)

**Core Innovation**: A multi-agent framework that **automatically multiplies agents based on problem complexity**, allowing dynamic scalability while each agent maintains a manageable portion of code.

**Key Features**:
- Each agent operates within its own **fixed-size context window**
- Central controller keeps subspaces of all agents **structurally aligned**
- Prevents information sparsity and confusion in large codebases
- **Bionic memory system**: Short-term memory, long-term knowledge base, evolutionary growth units

**Critical Insight**:
> "The overall code volume can be increased indefinitely according to the number of agents, while the amount of code managed by each agent remains constant."

### 1.3 SALLMA: Software Architecture for LLM-Based Multi-Agent Systems

**Source**: University of Florence, 2025

**Architecture Layers**:
1. **Operational Layer**: Agent execution and task management
2. **Knowledge Layer**: Information sharing and memory management

**Key Design Principle**: Uses Docker containerization to enable each LLM-powered agent to **operate independently within its own dedicated environment**.

### 1.4 The Modular Imperative: Rethinking LLMs for Maintainable Software

**Source**: Harvard SEAS

**Core Finding**: LLMs consistently violate modular principles by default. The paper proposes **Rubric DSL** - a "semantic contract" layer between natural language prompts and AI output that encodes and enforces modular design principles.

**Key Quote**:
> "It is not enough for LLM-generated code to appear modular by splitting functionality across multiple files or modules. Effective modularity requires coherent boundaries, reusable abstractions, and minimal coupling."

---

## 2. GitHub Projects & Frameworks

### 2.1 12-Factor Agents (HumanLayer)

**Repository**: github.com/humanlayer/12-factor-agents
**Stars**: Active community adoption

**The 12 Factors for LLM Applications**:

| Factor | Principle | Relevance to Modular Development |
|--------|-----------|----------------------------------|
| 1 | Natural Language to Tool Calls | Structure outputs, not free-form generation |
| 2 | Own Your Prompts | Treat prompts as code artifacts |
| 3 | **Own Your Context Window** | Critical for isolation |
| 4 | Tools Are Just Structured Outputs | Clean interfaces |
| 5 | Unify Execution and Business State | Simplify state management |
| 6 | Launch/Pause/Resume | Support modular workflows |
| 7 | Contact Humans with Tool Calls | Human-in-the-loop checkpoints |
| 8 | Own Your Control Flow | Explicit module coordination |
| 9 | Compact Errors into Context | Efficient error propagation |
| 10 | **Small, Focused Agents** | Core modular principle |
| 11 | Trigger from Anywhere | Loose coupling |
| 12 | Stateless Reducer Design | Module independence |

**Critical Context Window Insight**:
> "Fill your context window past 40% and you enter the 'dumb zone' - where signal-to-noise degrades, attention fragments, and agents start making mistakes."

### 2.2 MetaGPT

**Repository**: github.com/geekan/MetaGPT
**Architecture**: Simulates a software company with specialized roles

**Key Innovation**: **Structured communication through documents and diagrams** rather than dialogue, preventing "telephone game" information degradation.

**Role Decomposition**:
- Product Manager → Requirements
- Architect → System Design
- Project Manager → Task Breakdown
- Engineer → Implementation
- QA Engineer → Testing

**Performance**: 100% task completion rate, 40% improvement over ChatDev in many metrics

### 2.3 ChatDev

**Repository**: github.com/OpenBMB/ChatDev
**Architecture**: Virtual software company with communicative agents

**Key Patterns**:
- **Phase Decomposition**: Design → Coding → Testing → Documentation
- **Role-Based Isolation**: CEO, CTO, Programmer, Tester
- **Cooperative Communication**: Autonomously proposing and refining through blend of natural and programming languages

### 2.4 Claude-Flow

**Repository**: github.com/ruvnet/claude-flow
**Stars**: 12.7k

**Features**:
- Multi-agent swarm orchestration
- Distributed swarm intelligence
- Enterprise-grade architecture
- Native Claude Code support via MCP protocol

### 2.5 AgentForge

**Source**: arXiv:2601.13383v1

**Design Principles**:
1. **Modularity**: Decompose agent functionality into independent, interchangeable components with minimal coupling
2. **Simplicity**: Core abstractions minimal and intuitive
3. **Explicit Control**: No implicit magic

**Key Innovation**: Formally specified skill abstraction with well-defined input-output contracts enabling:
- Compositional agent construction
- Independent skill testing, versioning, and sharing

---

## 3. Interface Contract Patterns for Isolated Development

### 3.1 Hexagonal Architecture (Ports & Adapters)

**Origin**: Alistair Cockburn (2005)
**Purpose**: Isolate business logic from external concerns

**Core Principles**:
1. **Separate API, Domain, and SPI** clearly
2. **Dependencies flow inward** toward the domain
3. **Isolate domain** from outside concerns via ports and adapters

**Application to Agentic Development**:

```
┌─────────────────────────────────────────────────────────┐
│                    Module A (Isolated)                   │
├──────────────────────────────────────────────────────────┤
│  ┌─────────┐         ┌─────────────┐        ┌─────────┐ │
│  │ Primary │ ──────► │   DOMAIN    │ ◄───── │Secondary│ │
│  │  Port   │         │   (Core     │        │  Port   │ │
│  │(Inbound)│         │   Logic)    │        │(Outbound│ │
│  └─────────┘         └─────────────┘        └─────────┘ │
│       ▲                                          │       │
│       │                                          ▼       │
│  ┌─────────┐                              ┌─────────┐   │
│  │ Adapter │                              │ Adapter │   │
│  │(Driver) │                              │(Driven) │   │
│  └─────────┘                              └─────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Benefits for AI Agent Development**:
- Agents only need to know the **port interface**, not implementation details
- Modules can be developed and tested **in complete isolation**
- Implementation can be **swapped** without affecting other modules

### 3.2 Contract-First Development

**Key Insight from MIT Research**:
> "Think of concepts as modules that are completely clean and independent. Synchronizations then act like contracts — they say exactly how concepts are supposed to interact."

**Contract Types**:
1. **Input Contracts**: What the module expects
2. **Output Contracts**: What the module produces
3. **Invariants**: What the module guarantees
4. **Non-Functional Requirements**: Performance, reliability constraints

### 3.3 Dependency Injection for Module Isolation

**Pattern**: Classes receive dependencies through their constructor rather than creating them internally.

**Application to AI Development**:
- Module interfaces defined as **abstract contracts**
- Concrete implementations injected at runtime
- AI agents work against **abstractions**, not implementations
- Enables testing modules in isolation with mock dependencies

---

## 4. Context Window Management Strategies

### 4.1 The Context Window Problem

**Research Finding** (Lost in the Middle, 2023):
> "LLMs perform best when relevant information is at the beginning or end of context, with significant degradation for information buried in long sequences."

**The "Dumb Zone"**:
- At 40-60% context utilization, model recall degrades
- Reasoning falters
- Hallucinations increase

### 4.2 Strategies for Module Isolation

| Strategy | Description | Benefit |
|----------|-------------|---------|
| **Modular Context** | Each module gets dedicated, isolated context | No cross-contamination |
| **Hierarchical Summarization** | Summarize completed modules | Preserve knowledge, reduce tokens |
| **Interface-Only Context** | Include only contracts, not implementations | Minimal necessary context |
| **Progressive Enhancement** | Start with core, add incrementally | MVP-first development |
| **Sub-Agent Delegation** | Spawn sub-agents for complex sub-tasks | Keep individual contexts manageable |

### 4.3 Context Engineering Best Practices

**From Anthropic's Guidelines**:
1. **Curate Context Actively**: Don't blindly append; manage what the LLM sees
2. **Compact Errors**: Distill failures into concise context, not verbose logs
3. **Pre-fetch Context**: Retrieve information upfront, not mid-execution
4. **Sub-agent Architectures**: Long-horizon tasks require specialized techniques

**GCC Framework** (Git-Context-Controller):
- Treats context as version-controlled artifacts
- Commands: COMMIT, BRANCH, MERGE for context management
- Enables long-horizon workflows and reproducibility

---

## 5. MVP-First Modular Development Strategies

### 5.1 Core Principles

1. **Start with Minimum Viable Module Set**: Identify the smallest set of modules that provide functional value
2. **Validate Core Before Expanding**: Get core modules working before adding non-core
3. **Define Clear Module Boundaries**: Use contracts/interfaces before implementation
4. **Iterate Based on Feedback**: Each module release informs next priorities

### 5.2 Recommended Release Strategy

```
Phase 1: Core Foundation (MVP)
├── Core Module 1: Essential functionality
├── Core Module 2: Essential functionality
└── Interface Contracts for ALL modules (even future ones)

Phase 2: First Extension
├── Non-Core Module A (connects via established contracts)
└── Non-Core Module B (connects via established contracts)

Phase 3: Additional Extensions
├── Non-Core Module C
├── Non-Core Module D
└── (Each module developed in isolation)
```

### 5.3 MoSCoW Prioritization for Modules

| Priority | Module Type | Development Approach |
|----------|-------------|---------------------|
| **Must Have** | Core modules | Develop first, refine continuously |
| **Should Have** | High-value non-core | Develop after core stable |
| **Could Have** | Enhancement modules | Optional inclusion |
| **Won't Have** | Future scope | Define contracts only |

---

## 6. Firewall Isolation Techniques

### 6.1 Module Isolation Patterns

**From Modular Architecture Research**:

1. **Fault Isolation**: Failures in one module don't cascade
2. **Independent Evolution**: Each module updated/replaced independently
3. **Clear Boundaries**: Well-defined interfaces prevent leakage
4. **Technology Agnostic**: Modules can use different technologies

### 6.2 Preventing Regression Bugs

| Technique | Implementation |
|-----------|----------------|
| **Contract Testing** | Verify modules meet interface contracts |
| **Isolation Testing** | Test modules with mocked dependencies |
| **Change Detection** | Monitor for contract violations |
| **Version Pinning** | Lock module versions for stability |

### 6.3 Communication Patterns

**From Android Modularization Guidelines**:
> "It's important to keep the coupling low even when modules work together and exchange information frequently."

**Recommended Patterns**:
1. **Event-Driven**: Modules communicate via events, not direct calls
2. **Message Passing**: Structured messages between modules
3. **Shared Contracts**: Common interface definitions
4. **Dependency Inversion**: High-level modules don't depend on low-level details

---

## 7. Spec-Driven Development (SDD) for Agentic Development

### 7.1 Definition

> "Spec-driven development means writing a 'spec' before writing code with AI. The spec becomes the source of truth for the human and the AI."

**Key Artifacts**:
- `SPEC.md`: Defines intent, constraints, and contracts
- `CLAUDE.md`/`AGENTS.md`: Explains how agents should operate
- Interface Contracts: Define module boundaries

### 7.2 Four-Phase Workflow (GitHub Spec Kit)

1. **Specify**: Define user journeys, success criteria, high-level goals
2. **Plan**: Create technical architecture, constraints, implementation approach
3. **Tasks**: Break work into small, testable units with clear acceptance criteria
4. **Implement**: AI generates code while developers verify at checkpoints

### 7.3 Benefits for Modular Development

- **Clear Boundaries**: Specs define module scope
- **Testable Units**: Each task independently verifiable
- **Traceability**: From requirements through deployment
- **AI Guidance**: Structured specs prevent AI drift

---

## 8. Recommended Architecture for Your Spec Generator Framework

Based on this research, here's a recommended approach:

### 8.1 Core vs Non-Core Module Classification

```
CORE MODULES (Always Loaded)
├── Spec Parser Engine
├── Module Registry
├── Interface Contract Manager
└── Output Generator (Base)

NON-CORE MODULES (Loadable)
├── Domain Analyzers
│   ├── API Spec Analyzer
│   ├── UI Component Analyzer
│   └── Data Model Analyzer
├── Validators
│   ├── Contract Validator
│   ├── Dependency Validator
│   └── Completeness Validator
├── Output Formatters
│   ├── Markdown Formatter
│   ├── Mermaid Diagram Generator
│   └── JSON Schema Generator
└── Enhancement Modules
    ├── AI Suggestion Engine
    ├── Pattern Library Integrator
    └── Test Case Generator
```

### 8.2 Module Interface Contract Template

```typescript
interface ModuleContract {
  // Identity
  moduleId: string;
  version: string;

  // Dependencies
  requiredCoreModules: string[];
  optionalModules: string[];

  // Inputs (What this module needs)
  inputSchema: JSONSchema;

  // Outputs (What this module produces)
  outputSchema: JSONSchema;

  // Invariants (What this module guarantees)
  guarantees: string[];

  // Context Requirements
  contextBudget: number; // Max tokens this module needs
  isolationLevel: 'full' | 'shared-contracts' | 'shared-state';
}
```

### 8.3 Development Workflow

```
1. Define ALL module contracts first (even for future modules)
2. Implement Core Modules (full context available)
3. For each Non-Core Module:
   a. Load only: Module contract + Required interfaces
   b. Implement in isolation
   c. Verify contract compliance
   d. Integrate via defined interfaces
4. Test module combinations
5. Release incrementally
```

---

## 9. Key Recommendations

### 9.1 For Minimizing Agent Context

1. **Keep modules small and focused** (3-10 steps per agent task)
2. **Define contracts before implementation** (agents only see contracts)
3. **Use hierarchical summarization** for completed work
4. **Spawn sub-agents** for complex sub-tasks
5. **Target <40% context utilization** per agent session

### 9.2 For Preventing Regressions

1. **Contract testing** at module boundaries
2. **Version pinning** for stable modules
3. **Isolation testing** with mocked interfaces
4. **Change detection** for contract violations

### 9.3 For MVP-First Development

1. **Identify minimum viable module set**
2. **Define ALL interfaces upfront** (even for future modules)
3. **Implement core first**, validate, then extend
4. **Use feature flags** for optional module inclusion

### 9.4 For Agent Development

1. **Each module = one focused agent task**
2. **Provide only necessary context** (contracts, not implementations)
3. **Use structured outputs** (not free-form text)
4. **Implement validation gates** at module boundaries

---

## 10. Sources & References

### Academic Papers
- MASAI: Modular Architecture for Software-engineering AI Agents (Microsoft Research, 2024)
- Self-Organized Agents: Ultra Large-Scale Code Generation (TsukushiAI, 2024)
- SALLMA: Software Architecture for LLM-Based Multi-Agent Systems (U Florence, 2025)
- The Modular Imperative: Rethinking LLMs for Maintainable Software (Harvard SEAS)
- ChatDev: Communicative Agents for Software Development (ACL 2024)
- MetaGPT: Meta Programming for Multi-Agent Collaborative Framework (ICLR 2024)

### Frameworks & Tools
- 12-Factor Agents: github.com/humanlayer/12-factor-agents
- MetaGPT: github.com/geekan/MetaGPT
- ChatDev: github.com/OpenBMB/ChatDev
- Claude-Flow: github.com/ruvnet/claude-flow
- GitHub Spec Kit: github.com/github/spec-kit

### Industry Resources
- Anthropic: Effective Context Engineering for AI Agents
- Google Cloud: 12-Factor to 16-Factor App for AI
- Martin Fowler: Understanding Spec-Driven Development

---

## Confidence Assessment

| Finding | Confidence | Evidence Strength |
|---------|------------|-------------------|
| Modular architecture improves AI agent performance | **High** | Multiple academic papers, production systems |
| Context window limits require module isolation | **High** | Research + industry validation |
| Interface contracts enable isolated development | **High** | Decades of software engineering practice |
| MASAI/SoA patterns applicable to spec generation | **Medium** | Requires adaptation but principles transfer |
| MVP-first approach reduces risk | **High** | Well-established software practice |
| 12-Factor Agents principles are production-ready | **Medium-High** | Growing adoption, early production evidence |

---

*Report generated from exhaustive web research on modular, firewalled agentic development approaches.*
