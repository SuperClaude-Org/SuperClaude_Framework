# SC Commands Reference

**Complete SuperClaude Framework Command Reference**

> This file serves two purposes: quick navigation for Claude Code and learning resource for humans.

**Last Updated**: 2026-01-18

---

## 📑 Table of Contents

- [📋 How to Use This Document](#-how-to-use-this-document)
- [📁 File Map: Where to Find Information](#-file-map-where-to-find-information)
- [🗂️ Command Categories](#️-command-categories)
- [📖 Detailed Description of Each Command](#-detailed-description-of-each-command)
- [🔀 Visual Map: When to Use What](#-visual-map-when-to-use-what)
- [⚡ Key Differences](#-key-differences-commonly-confused)
- [🎯 spawn vs task vs implement](#-spawn-vs-task-vs-implement--detailed-comparison)
- [🤔 task vs implement](#-task-vs-implement--when-to-choose-which)
- [📐 design vs workflow](#-design-vs-workflow--blueprint-vs-work-plan)
- [📂 index-repo vs Serena](#-index-repo-vs-serena--indexing-tools-comparison)
- [🔄 Typical Workflows](#-typical-workflows)
- [🔧 MCP Server Reference](#-mcp-server-reference)
- [📝 Notes for Future Sessions](#-notes-for-future-sessions)

---

## 📋 How to Use This Document

This reference contains sections for **different audiences**:

### 🤖 For Claude Code (skip these if you're human)
| Section | Purpose |
|---------|---------|
| [`📁 File Map`](#-file-map-where-to-find-information) | File paths for navigation in new sessions |
| [`🔧 MCP Server Reference`](#-mcp-server-reference) | Technical integration details |
| [`📝 Notes for Future Sessions`](#-notes-for-future-sessions) | Session start instructions |

### 👤 For Humans (learning SuperClaude)
| Section | Purpose |
|---------|---------|
| [`🗂️ Command Categories`](#️-command-categories) | Overview of all 30 commands by category |
| [`📖 Detailed Descriptions`](#-detailed-description-of-each-command) | Syntax, examples, when to use each command |
| [`🔀 Visual Map`](#-visual-map-when-to-use-what) | Decision tree: which command to use |
| [`⚡ Key Differences`](#-key-differences-commonly-confused) | spawn vs task vs implement, etc. |
| [`🔄 Typical Workflows`](#-typical-workflows) | Real-world usage patterns with examples |

> **💡 Recommendation**: Start with [`🗂️ Command Categories`](#️-command-categories) for overview, then read [`🔄 Typical Workflows`](#-typical-workflows) for practical examples.

---

## 📁 File Map: Where to Find Information

> 🤖 **For Claude Code**: This section helps navigate the codebase in new sessions.

This section is for quick lookups in future sessions (new context).

### ⚡ Quick Reference (read first!)
```
PROJECT_INDEX.md         # Project quick start (3K tokens)
```

### Command Sources (read for implementation details)
```
src/superclaude/commands/
├── pm.md              # /sc:pm - Project Manager Agent (593 lines, most detailed)
├── task.md            # /sc:task - Task Management
├── workflow.md        # /sc:workflow - Workflow Generator
├── spawn.md           # /sc:spawn - Meta-System Orchestration
├── brainstorm.md      # /sc:brainstorm - Requirements Discovery
├── implement.md       # /sc:implement - Feature Implementation
├── design.md          # /sc:design - System Design
├── research.md        # /sc:research - Web Research
├── analyze.md         # /sc:analyze - Code Analysis
├── troubleshoot.md    # /sc:troubleshoot - Issue Diagnosis
├── improve.md         # /sc:improve - Code Improvement
├── cleanup.md         # /sc:cleanup - Dead Code Removal
├── test.md            # /sc:test - Testing
├── build.md           # /sc:build - Building
├── explain.md         # /sc:explain - Code Explanation
├── document.md        # /sc:document - Documentation
├── git.md             # /sc:git - Git Operations
├── estimate.md        # /sc:estimate - Development Estimation
├── reflect.md         # /sc:reflect - Task Reflection
├── spec-panel.md      # /sc:spec-panel - Expert Spec Review (414 lines)
├── business-panel.md  # /sc:business-panel - Business Analysis
├── index-repo.md      # /sc:index-repo - Repository Indexing
├── index.md           # /sc:index - Project Documentation
├── load.md            # /sc:load - Session Load
├── save.md            # /sc:save - Session Save
├── select-tool.md     # /sc:select-tool - MCP Tool Selection
├── recommend.md       # /sc:recommend - Command Recommendation
├── help.md            # /sc:help - Help
├── sc.md              # /sc - Main dispatcher
└── agent.md           # /sc:agent - Custom agents
```

### Duplicate Copies (same files)
```
plugins/superclaude/commands/  # Copy for plugin distribution
```

### PM Agent Core (Python implementation)
```
src/superclaude/pm_agent/
├── confidence.py      # ConfidenceChecker (pre-execution)
├── self_check.py      # SelfCheckProtocol (post-implementation)
└── reflexion.py       # ReflexionPattern (error learning)
```

### Execution Patterns (Python)
```
src/superclaude/execution/
├── parallel.py        # Wave → Checkpoint → Wave pattern
├── reflection.py      # Session reflection
└── self_correction.py # Error correction
```

### Pytest Plugin
```
src/superclaude/pytest_plugin.py  # Fixtures: confidence_checker, self_check_protocol, etc.
```

### Key Documentation
```
CLAUDE.md              # Project setup, commands overview
PLANNING.md            # Architecture, design decisions
KNOWLEDGE.md           # Best practices, troubleshooting
TASK.md                # Current tasks
```

### Additional Skills
```
src/superclaude/skills/confidence-check/SKILL.md  # Confidence check skill
```

---

## 🗂️ Command Categories

### 1. ORCHESTRATION (Meta-level) - "What to do?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:pm`](#scpm---project-manager-agent) | Project Manager (always active) | `pm.md` |
| [`/sc:spawn`](#scspawn---meta-system-task-orchestration) | Decomposition Epic → Task | `spawn.md` |
| [`/sc:task`](#sctask---enhanced-task-management) | Execution with MCP coordination | `task.md` |
| [`/sc:workflow`](#scworkflow---implementation-workflow-generator) | Generate plan from PRD | `workflow.md` |

### 2. DISCOVERY - "What's needed?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:brainstorm`](#scbrainstorm---interactive-requirements-discovery) | Clarify requirements (Socratic) | `brainstorm.md` |
| [`/sc:research`](#scresearch---deep-web-research) | Web research via Tavily | `research.md` |

### 3. IMPLEMENTATION - "How to build?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:implement`](#scimplement---feature-implementation) | Write code | `implement.md` |
| [`/sc:design`](#scdesign---system-and-component-design) | Architecture, API, schemas | `design.md` |

### 4. QUALITY - "Is everything correct?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:analyze`](#scanalyze---code-analysis) | Code analysis (quality/security/perf) | `analyze.md` |
| [`/sc:troubleshoot`](#sctroubleshoot---issue-diagnosis) | Root cause analysis | `troubleshoot.md` |
| [`/sc:test`](#sctest---testing) | Tests + coverage | `test.md` |
| [`/sc:build`](#scbuild---project-building) | Build project | `build.md` |

### 5. IMPROVEMENT - "How to make it better?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:improve`](#scimprove---code-improvement) | Refactoring, optimization | `improve.md` |
| [`/sc:cleanup`](#sccleanup---code-cleanup) | Dead code, unused imports | `cleanup.md` |

### 6. DOCUMENTATION - "What is this?"

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:explain`](#scexplain---code-explanation) | Code explanation | `explain.md` |
| [`/sc:document`](#scdocument---documentation-generation) | Generate documentation | `document.md` |
| [`/sc:index-repo`](#scindex-repo---repository-indexing) | Repository indexing | `index-repo.md` |

### 7. EXPERT PANELS

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:spec-panel`](#scspec-panel---expert-specification-review) | Specification review (Wiegers, Fowler...) | `spec-panel.md` |
| [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel) | Business analysis (Porter, Drucker...) | `business-panel.md` |

### 8. UTILITIES

| Command | Purpose | File |
|---------|---------|------|
| [`/sc:git`](#scgit---git-operations) | Git + smart commits | `git.md` |
| [`/sc:estimate`](#scestimate---development-estimation) | Time/complexity estimation | `estimate.md` |
| [`/sc:reflect`](#screflect---task-reflection) | Progress validation | `reflect.md` |
| `/sc:load` | Load session | `load.md` |
| `/sc:save` | Save session | `save.md` |

---

## 📖 Detailed Description of Each Command

---

### `/sc:pm` - Project Manager Agent

**Status:** Always active automatically. This is a background layer, not a command.

**When to use:** No need to call explicitly — always running.

**What it does:**
- Automatically restores context from past sessions (Serena MCP)
- Delegates tasks to personas (backend, frontend, security...)
- Runs PDCA cycle: Plan → Do → Check → Act
- Saves progress between sessions

**Workflow:**
```
User: "I want to add authentication"
PM Agent:
  1. Activates Brainstorming Mode (if request is vague)
  2. Delegates to requirements-analyst
  3. Delegates to system-architect
  4. Delegates to security-engineer
  5. Delegates to backend-architect
  6. Delegates to quality-engineer
  7. Documents in CLAUDE.md
```

**MCP servers:** sequential, context7, magic, playwright, morphllm, serena, tavily, chrome-devtools

**Key patterns:**
- Session Start Protocol (context restoration)
- Self-Correcting Execution (root cause first!)
- PDCA Document Structure (`docs/pdca/[feature]/`)

---

### `/sc:spawn` - Meta-System Task Orchestration

**When to use:** Complex task that requires breaking down into many subtasks with dependencies.

**What it does:**
- Breaks down Epic → Story → Task → Subtask
- Selects strategy: sequential/parallel/adaptive
- Coordinates dependencies between tasks

**Syntax:**
```
/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

**Examples:**
```bash
# Monolith migration
/sc:spawn "migrate legacy monolith to microservices" --strategy adaptive --depth deep
# Creates: Database design → Backend API → Frontend → Testing

# Feature with dependencies
/sc:spawn "implement user authentication system"
# Breakdown: Database design → Backend API → Frontend UI → Testing
```

**Difference from `/sc:task`:**
- spawn = decomposition (breaking down)
- task = execution (doing work)

---

### `/sc:task` - Enhanced Task Management

**When to use:** Need to execute a specific complex task with MCP server coordination.

**What it does:**
- Activates needed personas (architect, security, frontend...)
- Routes to correct MCP servers
- Parallel execution where possible
- Cross-session persistence via Serena

**Syntax:**
```
/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```

**Examples:**
```bash
# Enterprise-level feature
/sc:task create "enterprise authentication system" --strategy systematic --parallel
# Activates architect + security + backend + frontend

# Agile sprint
/sc:task execute "feature backlog" --strategy agile --delegate
# Iterative execution with delegation
```

**MCP servers:** sequential, context7, magic, playwright, morphllm, serena

---

### `/sc:workflow` - Implementation Workflow Generator

**When to use:** Have a PRD/specification and need a step-by-step implementation plan.

**What it does:**
- Parses PRD document
- Generates workflow with dependencies
- Creates implementation plan by domains
- **Does NOT implement code**, only plans

**Syntax:**
```
/sc:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

**Examples:**
```bash
# From PRD file
/sc:workflow docs/PRD/auth-feature.md --strategy systematic --depth deep
# Result: "1. DB schema → 2. API → 3. UI → 4. Tests"

# From description
/sc:workflow "user authentication system" --strategy agile --parallel
```

**Difference from `/sc:task`:**
- workflow = planning (generates roadmap)
- task = execution (actually does work)

---

### `/sc:brainstorm` - Interactive Requirements Discovery

**When to use:** Idea is vague, need to understand requirements through dialogue.

**What it does:**
- Asks Socratic questions for clarification
- Checks feasibility
- Generates concrete specifications
- Creates brief for implementation

**Syntax:**
```
/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

**Examples:**
```bash
# New product
/sc:brainstorm "AI-powered project management tool" --strategy systematic --depth deep
# Claude: What problems should it solve? For what team? Integrations?
# Result: Clear requirements document

# Feature
/sc:brainstorm "real-time collaboration features" --strategy agile --parallel
```

**MCP servers:** sequential, context7, magic, playwright, morphllm, serena

---

### `/sc:research` - Deep Web Research

**When to use:** Need up-to-date information from the internet.

**What it does:**
- Parallel web searches via Tavily
- Multi-hop exploration (following link chains)
- Evidence-based synthesis
- Saves report to `claudedocs/research_*.md`

**Syntax:**
```
/sc:research "[query]" [--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]
```

**Examples:**
```bash
/sc:research "latest developments in quantum computing 2024" --depth deep
/sc:research "competitive analysis of AI coding assistants" --depth exhaustive
```

**MCP servers:** tavily, sequential, playwright, serena

---

### `/sc:implement` - Feature Implementation

**When to use:** Know exactly what to do, need to write code.

**What it does:**
- Activates needed personas (frontend/backend/security)
- Uses Context7 for framework-specific patterns
- Magic MCP for UI components
- Generates code with tests

**Syntax:**
```
/sc:implement [feature-description] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```

**Examples:**
```bash
# React component
/sc:implement user profile component --type component --framework react --with-tests

# API with security
/sc:implement user authentication API --type api --safe --with-tests

# Full-stack feature
/sc:implement payment processing system --type feature --with-tests
```

**MCP servers:** context7, sequential, magic, playwright

---

### `/sc:design` - System and Component Design

**When to use:** Need to design, but not implement.

**What it does:**
- Architecture diagrams
- API specifications
- Database schemas
- Component interfaces

**Syntax:**
```
/sc:design [target] [--type architecture|api|component|database] [--format diagram|spec|code]
```

**Examples:**
```bash
/sc:design user-management-system --type architecture --format diagram
/sc:design payment-api --type api --format spec
/sc:design e-commerce-db --type database --format diagram
```

**Difference from `/sc:implement`:**
- design = blueprint (documentation)
- implement = code (implementation)

---

### `/sc:analyze` - Code Analysis

**When to use:** Need a code audit.

**What it does:**
- Quality: code smells, maintainability
- Security: vulnerabilities, OWASP
- Performance: bottlenecks
- Architecture: technical debt

**Syntax:**
```
/sc:analyze [target] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]
```

**Examples:**
```bash
/sc:analyze src/auth --focus security --depth deep
/sc:analyze --focus performance --format report
/sc:analyze src/components --focus quality --depth quick
```

---

### `/sc:troubleshoot` - Issue Diagnosis

**When to use:** Something is broken, need to find the cause.

**What it does:**
- Root cause analysis
- Stack trace examination
- Log analysis
- Suggests fixes

**Syntax:**
```
/sc:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```

**Examples:**
```bash
/sc:troubleshoot "Null pointer exception in user service" --type bug --trace --fix
/sc:troubleshoot "TypeScript compilation errors" --type build --fix
/sc:troubleshoot "API response times degraded" --type performance
```

---

### `/sc:improve` - Code Improvement

**When to use:** Code works, but want to make it better.

**What it does:**
- Quality refactoring
- Performance optimization
- Maintainability improvements
- Technical debt reduction

**Syntax:**
```
/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

**Examples:**
```bash
/sc:improve src/ --type quality --safe
/sc:improve api-endpoints --type performance --interactive
/sc:improve auth-service --type security --validate
```

**MCP servers:** sequential, context7

---

### `/sc:cleanup` - Code Cleanup

**When to use:** Need to remove garbage: dead code, unused imports.

**What it does:**
- Dead code detection
- Import optimization
- Structure cleanup
- Safety validation

**Syntax:**
```
/sc:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]
```

**Examples:**
```bash
/sc:cleanup src/ --type code --safe
/sc:cleanup --type imports --preview
/sc:cleanup --type all --interactive
```

**MCP servers:** sequential, context7

---

### `/sc:test` - Testing

**When to use:** Need to run tests.

**What it does:**
- Detects test runner
- Coverage reports
- Playwright for E2E
- Failure analysis

**Syntax:**
```
/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

**Examples:**
```bash
/sc:test
/sc:test src/components --type unit --coverage
/sc:test --type e2e  # Activates Playwright MCP
/sc:test --watch --fix
```

**MCP servers:** playwright

---

### `/sc:build` - Project Building

**When to use:** Need to build the project.

**What it does:**
- Compilation
- Bundling
- Optimization
- Error analysis

**Syntax:**
```
/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]
```

**Examples:**
```bash
/sc:build
/sc:build --type prod --clean --optimize
/sc:build frontend --verbose
```

**MCP servers:** playwright

---

### `/sc:explain` - Code Explanation

**When to use:** Need to understand how code works.

**What it does:**
- Explains code at different levels (basic/advanced)
- Framework-specific explanations via Context7
- Interactive examples

**Syntax:**
```
/sc:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```

**Examples:**
```bash
/sc:explain authentication.js --level basic
/sc:explain react-hooks --level intermediate --context react
/sc:explain microservices-system --level advanced --format interactive
```

**MCP servers:** sequential, context7

---

### `/sc:document` - Documentation Generation

**When to use:** Need to create documentation.

**What it does:**
- Inline comments (JSDoc)
- API documentation
- User guides
- External docs

**Syntax:**
```
/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]
```

**Examples:**
```bash
/sc:document src/auth/login.js --type inline
/sc:document src/api --type api --style detailed
/sc:document payment-module --type guide --style brief
```

---

### `/sc:index-repo` - Repository Indexing

**When to use:** Starting work with a large repository.

**What it does:**
- Creates `PROJECT_INDEX.md` (3KB instead of 58KB)
- 94% token savings
- Entry points, modules, tests, dependencies

**Syntax:**
```
/sc:index-repo [mode=update|quick]
```

**Examples:**
```bash
/sc:index-repo                # Full indexing
/sc:index-repo mode=update    # Update existing
/sc:index-repo mode=quick     # Quick (without tests)
```

---

### `/sc:spec-panel` - Expert Specification Review

**When to use:** Need specification, API, or requirements review from "experts".

**What it does:**
Simulates a panel discussion of renowned software engineering experts.

**Expert Panel (10 personas):**

| Expert | Specialization | Typical Question/Critique |
|--------|---------------|---------------------------|
| **Karl Wiegers** | Requirements Engineering | "Requirement lacks measurable criteria" |
| **Gojko Adzic** | Specification by Example | "Can you provide Given/When/Then?" |
| **Alistair Cockburn** | Use Cases | "Who is the primary stakeholder?" |
| **Martin Fowler** | Architecture & Design | "This violates single responsibility" |
| **Michael Nygard** | Production Systems | "What happens when this fails?" |
| **Sam Newman** | Microservices | "How handle backward compatibility?" |
| **Gregor Hohpe** | Enterprise Integration | "What's the message exchange pattern?" |
| **Lisa Crispin** | Agile Testing | "How would QA validate this?" |
| **Janet Gregory** | Collaborative Testing | "Did whole team participate?" |
| **Kelsey Hightower** | Cloud Native | "How handle cloud deployment?" |

**Three Operating Modes:**

| Mode | What Happens |
|------|--------------|
| `--mode discussion` | Experts build on each other's ideas (collaborative) |
| `--mode critique` | Systematic review with severity and priorities |
| `--mode socratic` | Questions for deep understanding (learning) |

**Focus Areas:**

| Focus | Lead Expert | Analyzes |
|-------|-------------|----------|
| `--focus requirements` | Wiegers | Clarity, testability, acceptance criteria |
| `--focus architecture` | Fowler | Interfaces, boundaries, patterns |
| `--focus testing` | Crispin | Test strategy, edge cases, coverage |
| `--focus compliance` | Wiegers + Nygard | Security, audit, regulatory |

**Syntax:**
```
/sc:spec-panel [spec|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance] [--iterations N]
```

**Examples:**
```bash
# API specification review
/sc:spec-panel @auth_api.spec.yml --mode critique --focus requirements,architecture

# Requirements workshop
/sc:spec-panel "user story content" --mode discussion --experts "wiegers,adzic,cockburn"

# Learning through questions
/sc:spec-panel @my_first_spec.yml --mode socratic --iterations 2

# Iterative improvement (3 rounds)
/sc:spec-panel @complex_system.spec.yml --iterations 3 --format detailed
```

**Example output (critique mode):**
```
KARL WIEGERS - Requirements Quality:
❌ CRITICAL: Requirement R-001 lacks acceptance criteria
📝 RECOMMENDATION: Replace "handle gracefully" with "open circuit after 5 failures"
🎯 PRIORITY: High
📊 QUALITY IMPACT: +40% testability

MARTIN FOWLER - Interface Design:
⚠️ MINOR: CircuitBreaker couples state with execution
📝 RECOMMENDATION: Separate CircuitBreakerState from Executor
```

**MCP servers:** sequential, context7

---

### `/sc:business-panel` - Business Analysis Panel

**When to use:** Need business analysis of strategy, plan, or idea.

**What it does:**
Simulates a panel discussion of legendary business thinkers.

**Expert Panel (9 personas):**

| Expert | Framework | Typical Question |
|--------|-----------|------------------|
| **Clayton Christensen** | Disruption, Jobs-to-be-Done | "What job is customer hiring this for?" |
| **Michael Porter** | Five Forces, Competitive Strategy | "What's your sustainable advantage?" |
| **Peter Drucker** | Management by Objectives | "What results are you measuring?" |
| **Seth Godin** | Tribe Building, Permission Marketing | "Who is your tribe? What story?" |
| **Kim & Mauborgne** | Blue Ocean Strategy | "Competing or creating new market?" |
| **Jim Collins** | Good to Great, Flywheel | "What's your hedgehog concept?" |
| **Nassim Taleb** | Antifragility, Black Swan | "Does this benefit from volatility?" |
| **Donella Meadows** | Systems Thinking | "Where are the leverage points?" |
| **Jean-luc Doumont** | Structured Communication | "Is the message clear and actionable?" |

**Three Operating Modes:**

| Mode | What Happens |
|------|--------------|
| `--mode discussion` | Collaborative — experts build on each other's ideas |
| `--mode debate` | Adversarial — experts argue, stress-test ideas |
| `--mode socratic` | Question-driven — deep questions for understanding |

**Syntax:**
```
/sc:business-panel [content|@file] [--experts "porter,christensen"] [--mode discussion|debate|socratic] [--focus domain] [--synthesis-only]
```

**Examples:**
```bash
# Business plan analysis
/sc:business-panel @business_plan.md

# Competitive analysis
/sc:business-panel @market_analysis.md --experts "porter,christensen" --focus "competitive-analysis"

# Strategy debate (stress-test)
/sc:business-panel @strategy.md --mode debate

# Synthesis only (without detailed analysis)
/sc:business-panel @pitch_deck.md --synthesis-only
```

**Example output (discussion mode):**
```
PORTER: "The competitive position relies on cost leadership..."
CHRISTENSEN: "But cost leadership is vulnerable to disruption from below..."
KIM/MAUBORGNE: "Consider creating new market space instead..."
TALEB: "The real question: does this benefit from uncertainty?"
```

**MCP servers:** sequential, context7

---

### When to Use Which Panel

| Document | Panel |
|----------|-------|
| API specification | [`/sc:spec-panel`](#scspec-panel---expert-specification-review) |
| User stories / Requirements | [`/sc:spec-panel`](#scspec-panel---expert-specification-review) |
| Architecture Decision Record | [`/sc:spec-panel`](#scspec-panel---expert-specification-review) |
| Business plan | [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel) |
| Go-to-market strategy | [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel) |
| Pitch deck | [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel) |
| PRD (Product Requirements) | **Both** — spec for technical, business for strategy |

---

### `/sc:git` - Git Operations

**When to use:** Git operations with smart commit messages.

**Syntax:**
```
/sc:git [operation] [args] [--smart-commit] [--interactive]
```

**Examples:**
```bash
/sc:git status
/sc:git commit --smart-commit  # Generates conventional commit message
/sc:git merge feature-branch --interactive
```

---

### `/sc:estimate` - Development Estimation

**When to use:** Need time/complexity estimation.

**Syntax:**
```
/sc:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```

**Examples:**
```bash
/sc:estimate "user authentication system" --type time --unit days --breakdown
# Database design: 2 days
# Backend API: 3 days
# Frontend UI: 2 days
# Testing: 1 day
# Total: 8 days (85% confidence)

/sc:estimate "migrate to microservices" --type complexity --breakdown
```

**MCP servers:** sequential, context7

---

### `/sc:reflect` - Task Reflection

**When to use:** Need to check progress and validate work.

**Syntax:**
```
/sc:reflect [--type task|session|completion] [--analyze] [--validate]
```

**Examples:**
```bash
/sc:reflect --type task --analyze      # Current approach validation
/sc:reflect --type session --validate  # Session analysis
/sc:reflect --type completion          # Readiness check
```

**MCP servers:** serena

---

## 🔀 Visual Map: When to Use What

```
VAGUE IDEA?
    └─→ /sc:brainstorm (clarify requirements)
            │
            ▼
NEED RESEARCH?
    └─→ /sc:research (search the web)
            │
            ▼
PRD READY?
    └─→ /sc:workflow (generate plan)
            │
            ▼
COMPLEX DECOMPOSITION?
    └─→ /sc:spawn (Epic → Story → Task)
            │
            ▼
NEED DESIGN?
    └─→ /sc:design (architecture, API, schemas)
            │
            ▼
READY TO CODE?
    └─→ /sc:implement (write code)
            │
            ▼
NEED TESTS?
    └─→ /sc:test (run tests)
            │
            ▼
NEED BUILD?
    └─→ /sc:build (build project)
            │
            ▼
SOMETHING BROKEN?
    └─→ /sc:troubleshoot (find the cause)
            │
            ▼
WANT IT BETTER?
    └─→ /sc:improve or /sc:cleanup
            │
            ▼
NEED DOCUMENTATION?
    └─→ /sc:document
            │
            ▼
NEED REVIEW?
    └─→ /sc:analyze (code) or /sc:spec-panel (specs)
```

---

## ⚡ Key Differences (commonly confused)

| Command | Purpose | Result |
|---------|---------|--------|
| [`/sc:spawn`](#scspawn---meta-system-task-orchestration) | Decompose large task | Task hierarchy |
| [`/sc:task`](#sctask---enhanced-task-management) | Execute task with coordination | Finished result |
| [`/sc:workflow`](#scworkflow---implementation-workflow-generator) | Plan implementation | Roadmap/plan |
| [`/sc:design`](#scdesign---system-and-component-design) | Design | Diagrams, specs |
| [`/sc:implement`](#scimplement---feature-implementation) | Write code | Finished code |
| [`/sc:brainstorm`](#scbrainstorm---interactive-requirements-discovery) | Clarify requirements | Concrete specs |

---

## 🎯 spawn vs task vs implement — Detailed Comparison

### Analogy: Team Roles

| Command | Role | Writes code? |
|---------|------|--------------|
| [`/sc:spawn`](#scspawn---meta-system-task-orchestration) | Project Manager | ❌ **No** — only breaks down into tasks |
| [`/sc:task`](#sctask---enhanced-task-management) | Tech Lead | ⚠️ **Can** — through delegation |
| [`/sc:implement`](#scimplement---feature-implementation) | Developer | ✅ **Yes** — directly |

---

### `/sc:spawn` — Decomposition (planner)

**What it does:** Takes a large task and breaks it into a hierarchy of subtasks.

**Result:** Document/task structure, **NOT code**.

```
/sc:spawn "build e-commerce platform"

Result (structure only!):
Epic: E-commerce Platform
├── Story: User Authentication
│   ├── Task: Database schema for users
│   ├── Task: Auth API endpoints
│   └── Task: Login UI
├── Story: Product Catalog
│   ├── Task: Product model
│   └── Task: Search functionality
└── Story: Checkout
    ├── Task: Cart logic
    └── Task: Payment integration
```

**When to use:** Don't know where to start, task is huge, need to break into AI-friendly parts.

---

### `/sc:task` — Execution Coordination (Tech Lead)

**What it does:** Takes a specific task and executes with MCP server and persona orchestration.

**Result:** Can be code, but through delegation (activates needed tools).

```
/sc:task create "user authentication" --strategy systematic --parallel

Workflow:
1. Activates architect persona → designs
2. Activates security persona → reviews
3. Activates backend persona → writes code (calls implement internally)
4. Activates qa persona → tests
```

**When to use:** Complex task requiring coordination across domains (security + backend + frontend simultaneously).

---

### `/sc:implement` — Code Writing (Developer)

**What it does:** Directly writes code.

**Result:** Finished code.

```
/sc:implement user login form --type component --framework react --with-tests

Result:
- src/components/LoginForm.tsx (created)
- src/components/LoginForm.test.tsx (created)
```

**When to use:** Know exactly what's needed, just need to write it.

---

### How They Connect

```
/sc:spawn "build auth system"        ← Breaks into tasks
    │
    ├── Creates Task: "Design auth architecture"
    │       └── Can execute via /sc:design
    │
    ├── Creates Task: "Implement auth API"
    │       └── Can execute via /sc:task or /sc:implement
    │
    └── Creates Task: "Build login UI"
            └── Can execute via /sc:implement
```

Or `/sc:task` can call `/sc:implement` internally:

```
/sc:task execute "auth system" --parallel
    │
    ├── Delegates backend → calls /sc:implement auth API
    ├── Delegates frontend → calls /sc:implement login form
    └── Delegates security → calls /sc:analyze --focus security
```

---

### When to Use What — Quick Reference

| Situation | Command |
|-----------|---------|
| "Want to do X, but don't know how to break it down" | [`/sc:spawn`](#scspawn---meta-system-task-orchestration) |
| "Need to do X, requires backend + security + tests" | [`/sc:task`](#sctask---enhanced-task-management) |
| "Write me component Y" | [`/sc:implement`](#scimplement---feature-implementation) |
| "Need implementation plan from PRD" | [`/sc:workflow`](#scworkflow---implementation-workflow-generator) |

---

### Short Formula

- **spawn** = planner (task document only, **never writes code**)
- **task** = coordinator (can write code through delegation to other commands)
- **implement** = executor (writes code directly)

---

## 🤔 task vs implement — When to Choose Which?

### When task is better than implement

| Situation | Better |
|-----------|--------|
| Feature spans multiple domains (API + UI + security) | [`/sc:task`](#sctask---enhanced-task-management) |
| Need architectural review before coding | [`/sc:task`](#sctask---enhanced-task-management) |
| Working in unfamiliar codebase | [`/sc:task`](#sctask---enhanced-task-management) |
| Critical feature (auth, payments) | [`/sc:task`](#sctask---enhanced-task-management) |

### When implement is better than task

| Situation | Better |
|-----------|--------|
| Single component / single function | [`/sc:implement`](#scimplement---feature-implementation) |
| Know exactly what and how to do | [`/sc:implement`](#scimplement---feature-implementation) |
| Simple CRUD | [`/sc:implement`](#scimplement---feature-implementation) |
| Already did design/architecture | [`/sc:implement`](#scimplement---feature-implementation) |

### Why not always use task?

**Coordination overhead** — task spends tokens on "meetings":

```
/sc:task "add logout button"

task thinks:
  1. Activate architect? → overkill for a button
  2. Activate security? → logout is simple
  3. Activate frontend? → ok
  4. Activate qa? → for a button?

Result: spent tokens on coordination for a single button
```

vs

```
/sc:implement logout button --type component --framework react

implement:
  1. Reads existing code
  2. Writes button
  3. Done
```

### Analogy

- **task** = schedule a meeting with 5 people to solve the task
- **implement** = just do the task yourself

For complex tasks, meetings are needed. For "add a button" — no.

### Practical Rule

```
Task concerns 1 domain (only frontend OR only backend)?
  → /sc:implement

Task concerns 2+ domains (frontend + backend + security)?
  → /sc:task

Unsure about architecture?
  → /sc:task (or first /sc:design)

Critical code (auth, payments, data)?
  → /sc:task (extra checks don't hurt)
```

---

## 📐 design vs workflow — Blueprint vs Work Plan

| Command | Question | Result |
|---------|----------|--------|
| [`/sc:design`](#scdesign---system-and-component-design) | **WHAT** to build? | Architecture, schemas, specifications |
| [`/sc:workflow`](#scworkflow---implementation-workflow-generator) | **IN WHAT ORDER** to do it? | Work plan, roadmap, steps |

---

### `/sc:design` — Architecture (blueprint)

**Answers:** How is the system structured? What components? How are they connected?

```
/sc:design payment-system --type architecture

Result:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  API Gateway │────▶│  Payment    │
│   (React)   │     │  (Express)   │     │  Service    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │   Stripe    │
                                        │   Webhook   │
                                        └─────────────┘

+ API contracts
+ Database schema
+ Security requirements
```

---

### `/sc:workflow` — Work Plan (roadmap)

**Answers:** In what order to do it? What dependencies? What's parallel?

```
/sc:workflow payment-system --strategy systematic

Result:
Phase 1: Foundation (Week 1)
  ├── Task 1.1: Setup database schema
  ├── Task 1.2: Create Payment model
  └── Task 1.3: Configure Stripe SDK

Phase 2: Backend (Week 2)
  ├── Task 2.1: Implement payment endpoints ← depends on 1.1, 1.2
  ├── Task 2.2: Add webhook handler ← depends on 1.3
  └── Task 2.3: Write unit tests

Phase 3: Frontend (Week 2-3) ← can start parallel with 2.2
  ├── Task 3.1: Payment form component
  └── Task 3.2: Confirmation page

Phase 4: Integration (Week 3)
  └── Task 4.1: E2E tests ← depends on all above
```

---

### Analogy: Building a House

| Stage | Command | What you get |
|-------|---------|--------------|
| House blueprint | `/sc:design` | Where walls go, where windows, what materials |
| Construction plan | `/sc:workflow` | First foundation → walls → roof → finishing |

---

### How design and workflow are connected

```
1. /sc:brainstorm "payment system"     → Requirements (WHAT we want)
          │
          ▼
2. /sc:design payment-system           → Architecture (HOW it's structured)
          │
          ▼
3. /sc:workflow payment-system         → Plan (IN WHAT ORDER)
          │
          ▼
4. /sc:implement ... (following plan)  → Code
```

---

### When design, when workflow

| Situation | Command |
|-----------|---------|
| "How should system X be structured?" | [`/sc:design`](#scdesign---system-and-component-design) |
| "In what order to implement feature Y?" | [`/sc:workflow`](#scworkflow---implementation-workflow-generator) |
| "Need API spec for service Z" | [`/sc:design`](#scdesign---system-and-component-design) `--type api` |
| "Break PRD into tasks with dependencies" | [`/sc:workflow`](#scworkflow---implementation-workflow-generator) |
| "What database schema is needed?" | [`/sc:design`](#scdesign---system-and-component-design) `--type database` |
| "How many phases in implementation?" | [`/sc:workflow`](#scworkflow---implementation-workflow-generator) `--depth deep` |

---

## 📂 index-repo vs Serena — Indexing Tools Comparison

### What Each Tool Creates

| Tool | Creates files | Where stored |
|------|---------------|--------------|
| [`/sc:index-repo`](#scindex-repo---repository-indexing) | `PROJECT_INDEX.md` (3KB) | Project root |
| **Serena MCP** | `.serena/project.yml` + `.serena/memories/*.md` | `.serena/` folder in project |

### Serena File Structure

```
.serena/
├── project.yml              # Configuration (languages, encoding, LSP settings)
├── .gitignore               # Git ignore
└── memories/
    ├── project_overview.md      # About the project, tech stack
    ├── suggested_commands.md    # Development commands
    ├── style_conventions.md     # Code styles and conventions
    └── task_completion.md       # Task completion checklist
```

---

### Key Differences

| Aspect | [`/sc:index-repo`](#scindex-repo---repository-indexing) | **Serena MCP** |
|--------|------------------|----------------|
| **Type** | Static file | Live LSP server + memories |
| **Main goal** | Quick start (token savings) | Semantic code understanding |
| **What it understands** | File structure | Symbols (functions, classes, types) |
| **Updates** | Manual (`mode=update`) | Memories — manual, LSP — automatic |
| **Persistence** | File in project | Files in `.serena/memories/` |
| **LSP operations** | ❌ No | ✅ rename, find references, go to definition |
| **Cross-session** | ✅ Read file | ✅ Memories are persistent |
| **Tokens at start** | ~3K (reading INDEX) | On demand (reading needed memories) |

---

### When to Use What

**[`/sc:index-repo`](#scindex-repo---repository-indexing)** — for quick session start:
- Project structure overview
- Entry points and key modules
- Dependencies and configuration
- Quick start commands
- **Savings**: 58K → 3K tokens at start

**Serena MCP** — for deep code work:
- `find_symbol` — find class/function by name
- `find_referencing_symbols` — where symbol is used
- `rename_symbol` — rename everywhere safely via LSP
- `get_symbols_overview` — file structure (class methods etc.)
- **Memories** — persistent notes about project across sessions

---

### Recommendation

**Either one is sufficient** to start working:

| If you chose | What you get | Each session |
|--------------|--------------|--------------|
| **Serena** (recommended) | Memories + LSP + symbols | No need to read anything |
| [**index-repo**](#scindex-repo---repository-indexing) | PROJECT_INDEX.md | Can read for context |
| **Both** | Maximum information | Optional |

```bash
# Initial setup (once)
serena activate_project .         # Activate project
serena onboarding                 # Create memories
# and/or
/sc:index-repo                    # Create PROJECT_INDEX.md

# On structural changes
/sc:index-repo mode=update        # Update INDEX (if using)
serena edit_memory ...            # Update memories (if needed)
```

**Important**: SuperClaude commands automatically use Serena for code work.
Explicitly reading PROJECT_INDEX.md or calling `serena read_memory` each session is **not required**.

---

### Auto-update?

| What | Auto-updates? | How to update |
|------|---------------|---------------|
| `PROJECT_INDEX.md` | ❌ No | [`/sc:index-repo`](#scindex-repo---repository-indexing) `mode=update` |
| Serena memories | ❌ No | `write_memory` / `edit_memory` |
| Serena LSP understanding | ✅ Yes | Automatically sees file changes |

---

### When to Update?

| Event | [index-repo](#scindex-repo---repository-indexing) | Serena memories |
|-------|------------|-----------------|
| Added new module/folder | ✅ Update | ⚡ Optional |
| Renamed module | ✅ Update | ⚡ Optional |
| Fixed bug in file | ❌ Not needed | ❌ Not needed |
| Added dependency | ✅ Update | ❌ Not needed |
| Changed code conventions | ❌ Not needed | ✅ Update |
| Before PR/release | ⚡ Good practice | ❌ Not needed |

---

## 🔄 Typical Workflows

### New Project (initial setup)
```
# Option A: Via Serena (recommended)
1. serena activate_project .         # Activate project
2. serena onboarding                 # Create memories (project_overview, commands, etc.)

# Option B: Via index-repo
1. /sc:index-repo                    # Create PROJECT_INDEX.md

# Can use both — they complement each other
```

> **Important**: Add Serena auto-activation instruction to project CLAUDE.md:
> ```
> mcp__serena__activate_project project="."
> ```
> Then Claude will activate Serena automatically at the start of each session.

### New Feature
```
1. /sc:brainstorm "feature idea"     # Requirements gathering
2. /sc:design feature --type api     # Architecture design
3. /sc:workflow feature              # Implementation plan
4. /sc:implement step1               # Step-by-step implementation
5. /sc:test --coverage               # Testing
```
→ See: [`/sc:brainstorm`](#scbrainstorm---interactive-requirements-discovery), [`/sc:design`](#scdesign---system-and-component-design), [`/sc:workflow`](#scworkflow---implementation-workflow-generator), [`/sc:implement`](#scimplement---feature-implementation), [`/sc:test`](#sctest---testing)

### Bug Fix
```
1. /sc:troubleshoot "error" --trace  # Diagnosis (finds code via Serena)
2. /sc:implement fix                 # Fix
3. /sc:test                          # Verification
```
→ See: [`/sc:troubleshoot`](#sctroubleshoot---issue-diagnosis), [`/sc:implement`](#scimplement---feature-implementation), [`/sc:test`](#sctest---testing)

### Refactoring
```
1. /sc:analyze code --type quality   # Problem analysis (uses Serena)
2. /sc:improve code --focus X        # Improvement
3. /sc:cleanup --scope module        # Cleanup
4. /sc:test                          # Verification
```
→ See: [`/sc:analyze`](#scanalyze---code-analysis), [`/sc:improve`](#scimprove---code-improvement), [`/sc:cleanup`](#sccleanup---code-cleanup), [`/sc:test`](#sctest---testing)

### Code Review
```
1. /sc:analyze PR --type quality     # Code quality
2. /sc:analyze PR --type security    # Security
3. /sc:test --type integration       # Integration tests
```
→ See: [`/sc:analyze`](#scanalyze---code-analysis), [`/sc:test`](#sctest---testing)

### Business Idea Development (from idea to specification)
```
1. /sc:brainstorm "idea"                    # Clarify requirements through dialogue
2. /sc:research "market + competitors"      # Market research
3. /sc:business-panel @idea.md --mode discussion  # Expert analysis (Porter, Christensen...)
   # → Get strategic insights
4. /sc:business-panel @idea.md --mode debate      # Stress-test idea (optional)
5. /sc:design system --type architecture    # Technical architecture
6. /sc:spec-panel @design.md --mode critique      # Specification review (Fowler, Wiegers...)
   # → Get technical recommendations
```
→ See: [`/sc:brainstorm`](#scbrainstorm---interactive-requirements-discovery), [`/sc:research`](#scresearch---deep-web-research), [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel), [`/sc:design`](#scdesign---system-and-component-design), [`/sc:spec-panel`](#scspec-panel---expert-specification-review)

### Improving Specification/PRD
```
1. /sc:spec-panel @spec.md --mode socratic        # Questions to understand gaps
   # → Experts ask: "Who is primary stakeholder?"
2. Answer questions, expand spec
3. /sc:spec-panel @spec.md --mode critique        # Critical review
   # → Get: ❌ CRITICAL, ⚠️ MAJOR, priorities
4. /sc:spec-panel @spec.md --iterations 2         # Iterative improvement
```
→ See: [`/sc:spec-panel`](#scspec-panel---expert-specification-review)

### Architecture Validation Before Implementation
```
1. /sc:design system --type architecture    # Create architecture
2. /sc:spec-panel @architecture.md --focus architecture --experts "fowler,newman,nygard"
   # → Fowler: "This violates single responsibility"
   # → Newman: "How handle service evolution?"
   # → Nygard: "What happens when this fails?"
3. Fix based on recommendations
4. /sc:workflow system                      # Implementation plan
5. /sc:implement ...                        # Implementation
```
→ See: [`/sc:design`](#scdesign---system-and-component-design), [`/sc:spec-panel`](#scspec-panel---expert-specification-review), [`/sc:workflow`](#scworkflow---implementation-workflow-generator), [`/sc:implement`](#scimplement---feature-implementation)

### Pitch/Strategy Preparation
```
1. /sc:business-panel @pitch.md --mode discussion
   # → Porter: competitive advantage
   # → Christensen: disruption potential
   # → Godin: tribe and story
2. /sc:business-panel @pitch.md --mode debate     # Stress-test arguments
3. /sc:business-panel @pitch.md --synthesis-only  # Final synthesis
```
→ See: [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel)

### Enterprise-level Feature (full cycle)
```
1. /sc:brainstorm "enterprise feature"      # Requirements
2. /sc:business-panel @requirements.md      # Business validation
3. /sc:design feature --type architecture   # Architecture
4. /sc:spec-panel @design.md --focus architecture,testing  # Technical validation
5. /sc:workflow feature --depth deep        # Detailed plan
6. /sc:spawn "feature" --strategy adaptive  # Decompose into tasks
7. /sc:task execute task1 --parallel        # Execution with coordination
8. /sc:analyze feature --focus security     # Security review
9. /sc:test --type all --coverage           # Full testing
```
→ See: [`/sc:brainstorm`](#scbrainstorm---interactive-requirements-discovery), [`/sc:business-panel`](#scbusiness-panel---business-analysis-panel), [`/sc:design`](#scdesign---system-and-component-design), [`/sc:spec-panel`](#scspec-panel---expert-specification-review), [`/sc:workflow`](#scworkflow---implementation-workflow-generator), [`/sc:spawn`](#scspawn---meta-system-task-orchestration), [`/sc:task`](#sctask---enhanced-task-management), [`/sc:analyze`](#scanalyze---code-analysis), [`/sc:test`](#sctest---testing)

> **Note**: SuperClaude commands automatically use Serena for symbol search,
> dependency analysis, and code structure understanding. No need to explicitly call `serena find_symbol` etc.

---

## 🔧 MCP Server Reference

> 🤖 **For Claude Code**: Technical integration details for MCP routing.

| MCP Server | Purpose | Used in |
|------------|---------|---------|
| `sequential` | Multi-step reasoning | pm, task, workflow, brainstorm, spec-panel |
| `context7` | Official docs lookup | implement, improve, explain, design |
| `magic` | UI component generation | implement, task, workflow |
| `playwright` | E2E testing, browser | test, build, research |
| `serena` | Session persistence | pm, task, reflect |
| `tavily` | Web search | research, pm |
| `morphllm` | Large-scale transforms | task, workflow, brainstorm |
| `chrome-devtools` | Browser debugging | pm |

---

## 📝 Notes for Future Sessions

> 🤖 **For Claude Code**: Session start protocol and context restoration instructions.

When starting a new session:

1. **For quick start** → read `PROJECT_INDEX.md` (3K tokens)
2. **For command architecture understanding** → read this file (`SC_COMMANDS_REFERENCE.md`)
3. **For specific command details** → `src/superclaude/commands/{name}.md`
4. **For Python implementation** → `src/superclaude/pm_agent/` and `src/superclaude/execution/`
5. **For pytest fixtures** → `src/superclaude/pytest_plugin.py`
6. **For best practices** → `KNOWLEDGE.md`
7. **For current tasks** → `TASK.md`
8. **For architectural decisions** → `PLANNING.md`

### Serena MCP (if activated)

```bash
# Activate project
serena activate_project /path/to/SuperClaude_Framework

# Check memories
serena list_memories

# Read needed memory
serena read_memory project_overview.md
serena read_memory suggested_commands.md
```

**Available memories:**
- `project_overview.md` — about the project, tech stack, architecture
- `suggested_commands.md` — development commands (UV, pytest, make)
- `style_conventions.md` — code styles and conventions
- `task_completion.md` — task completion checklist

---

*This document is updated as the project evolves.*
