# Claude Code Proposals: IBOpenCode Framework Translation

**Document Date**: 2026-01-26
**Purpose**: Map IBOpenCode Framework features to SuperClaude/Claude Code equivalents
**Scope**: Complete translation strategy for 11 IBOpenCode components

---

## Executive Summary

This document provides comprehensive proposals for translating IBOpenCode Framework-specific features to SuperClaude and Claude Code native capabilities. Each section maps a specific IBOpenCode feature to its SuperClaude equivalent, explains the implementation approach, and identifies any gaps or limitations.

**Key Finding**: SuperClaude provides robust equivalents for all 11 IBOpenCode features, with several areas where SuperClaude's implementation is more mature or flexible.

---

## 1. Framework Architecture

### IBOpenCode Approach
```
.opencode/
├── command/           # Custom command definitions
├── agent/             # Agent specifications with model configs
└── resources/         # Templates and shared resources
    └── templates/
```

### SuperClaude Equivalent

**Primary Structure**: `.claude/` + `plugins/superclaude/`

```yaml
SuperClaude Architecture:
  .claude/
    ├── settings.json          # User configuration
    ├── commands/              # Installed slash commands
    └── skills/                # Skill definitions (SKILL.md format)
        ├── sc-task-unified/
        ├── sc-validate-tests/
        └── confidence-check/

  plugins/superclaude/
    ├── agents/                # Agent definitions (markdown)
    ├── commands/              # Command implementations
    ├── skills/                # Skill source files
    ├── modes/                 # Operational modes
    ├── mcp/                   # MCP server configurations
    │   └── configs/           # JSON configs per server
    ├── core/                  # Core framework files (FLAGS, RULES, etc.)
    └── scripts/               # Shell/Python utilities
```

**Key Differences**:
| Aspect | IBOpenCode | SuperClaude |
|--------|------------|-------------|
| Root Directory | `.opencode/` | `.claude/` + `plugins/superclaude/` |
| Config Format | Mixed (YAML, MD) | YAML frontmatter + Markdown |
| Distribution | Framework-specific | Claude Code plugin system |
| Installation | Custom CLI | `superclaude install` or Claude marketplace |

**Implementation Approach**:

1. **Commands**: Use `.claude/commands/` for installed slash commands
2. **Skills**: Use `.claude/skills/{skill-name}/SKILL.md` for complex behaviors
3. **Agents**: Use `plugins/superclaude/agents/*.md` for agent definitions
4. **Resources**: Use `src/superclaude/` for Python templates or `plugins/superclaude/` for plugin resources

**Advantages of SuperClaude**:
- Native Claude Code integration via plugin manifest
- Structured frontmatter format for metadata
- Clear separation between installed commands and source plugins
- Support for multiple installation methods (pipx, npm, manual)

**Example Skill Definition** (SuperClaude):
```markdown
---
name: sc:roadmap-gen
description: Generate roadmaps from project requirements
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap-gen - Roadmap Generation

## Purpose
[Command documentation here]

## Triggers
[When to use this command]

## Behavioral Flow
[Step-by-step execution process]
```

---

## 2. Agent System

### IBOpenCode Approach
```yaml
# IBOpenCode Agent Definition
Location: .opencode/agent/{agent-name}.md
Naming: @rf-{command}-{role}
Model: Specified in agent file (gpt-5.2, claude-sonnet-4-5)
Temperature: Explicit (0.1 for deterministic tasks)
Tools: bash, read, write, edit, list, glob, grep, task
```

### SuperClaude Equivalent

**Primary Location**: `plugins/superclaude/agents/*.md`

**Existing SuperClaude Agents**:
- `pm-agent.md` - Project Management orchestrator
- `quality-engineer.md` - Verification and testing
- `security-engineer.md` - Security analysis
- `backend-architect.md` - Backend system design
- `frontend-architect.md` - UI/UX architecture
- `deep-research-agent.md` - Research workflows
- `root-cause-analyst.md` - Investigation specialist

**Agent Definition Format** (SuperClaude):
```markdown
---
name: roadmap-orchestrator
description: Main pipeline coordinator for roadmap generation
category: orchestration
---

# Roadmap Orchestrator Agent

## Triggers
- Explicit invocation: `/sc:roadmap-gen`
- Context detection: Roadmap generation requests

## Behavioral Mindset
[Agent's cognitive approach]

## Focus Areas
[Primary responsibilities]

## Key Actions
[Step-by-step process]

## Outputs
[Deliverables and artifacts]

## Boundaries
**Will:** [What agent does]
**Will Not:** [Scope limitations]
```

**Model/Temperature Handling**:

SuperClaude does NOT specify models or temperature explicitly because:
1. Claude Code operates on a single model (Claude)
2. Temperature is controlled via thinking flags (`--think`, `--think-hard`, `--ultrathink`)
3. Behavior specialization comes from persona/mode activation, not model switching

**SuperClaude Thinking Depth** (replaces temperature/model):
| Thinking Level | Token Budget | Use Case |
|----------------|--------------|----------|
| `--think` | ~4K | Module-level analysis |
| `--think-hard` | ~10K | System-wide analysis |
| `--ultrathink` | ~32K | Critical system design |

**Translation Strategy**:

| IBOpenCode | SuperClaude Equivalent |
|------------|------------------------|
| `@rf-orchestrator` | `pm-agent.md` or dedicated `roadmap-orchestrator.md` |
| `@rf-template-scorer` | Custom agent or `/sc:analyze --focus quality` |
| Model: gpt-5.2 | Use `--think-hard` or `--ultrathink` for depth |
| Temperature: 0.1 | Use `--compliance strict` for deterministic behavior |

**Tool Mapping**:
```yaml
IBOpenCode Tools:
  bash → Bash
  read → Read
  write → Write
  edit → Edit, MultiEdit
  list → Glob, mcp__serena__list_dir
  glob → Glob, mcp__serena__find_file
  grep → Grep, mcp__serena__search_for_pattern
  task → Task (spawns subagents)
```

**Advantages of SuperClaude**:
- Rich persona system provides behavioral differentiation
- Thinking flags provide analysis depth control
- MCP integration provides specialized capabilities per domain
- No model-switching complexity (consistent Claude experience)

---

## 3. Command Definition System

### IBOpenCode Approach
```markdown
# IBOpenCode Command Format
Location: .opencode/command/{command-name}.md
Prefix: /rf: (release framework namespace)
Structure:
  - Syntax definition
  - Options parsing
  - Routing directive to orchestrator
```

### SuperClaude Equivalent

**Primary**: Skills System (`.claude/skills/{skill-name}/SKILL.md`)
**Secondary**: Commands (`plugins/superclaude/commands/*.md`)

**Namespace**: `/sc:` (SuperClaude prefix)

**Skill Structure** (SKILL.md):
```markdown
---
name: sc:roadmap-gen
description: Generate comprehensive project roadmaps
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap-gen - Roadmap Generator

## Purpose
Generate comprehensive project roadmaps with milestone tracking.

## Triggers
- Explicit: `/sc:roadmap-gen @spec-file.md`
- Keywords: "create roadmap", "generate roadmap"

## Usage
```bash
/sc:roadmap-gen @requirements.md                    # From requirements doc
/sc:roadmap-gen "feature description" --depth deep  # From description
/sc:roadmap-gen --template feature-release          # Use template
```

## Options
| Flag | Description | Default |
|------|-------------|---------|
| `--template` | Template type (feature, quality, docs) | auto-detect |
| `--depth` | Analysis depth (quick, standard, deep) | standard |
| `--output` | Output directory | `.roadmaps/<version>/` |

## Behavioral Flow
### 1. Input Analysis
- Parse input document or description
- Detect project type and scope
- Select appropriate template

### 2. Requirement Extraction
- Extract functional requirements
- Identify milestones and phases
- Map dependencies

### 3. Roadmap Generation
- Apply template structure
- Generate timeline estimates
- Create task breakdowns

### 4. Output Generation
- Create roadmap.md
- Generate tasklist files
- Produce artifact documentation

## MCP Integration
- **Sequential**: Complex analysis and planning
- **Context7**: Template patterns and best practices
- **Serena**: Session persistence and memory

## Outputs
- `roadmap.md` - Master roadmap document
- `tasklists/*.md` - Per-milestone task files
- `artifacts/*.md` - Supporting documents

## Boundaries
**Will:**
- Generate structured roadmaps from requirements
- Create milestone-based task breakdowns
- Apply appropriate templates

**Will Not:**
- Execute implementation tasks
- Make business prioritization decisions
- Override user-specified templates
```

**Command Registration**:

SuperClaude skills are invoked via the Skill tool:
```yaml
Available Skills (from Skill tool):
  - sc:task-unified  # Unified task execution
  - sc:research      # Deep research mode
  - sc:implement     # Feature implementation
  - sc:analyze       # Code analysis
  - sc:roadmap-gen   # [NEW] Roadmap generation
```

**Comparison**:
| Aspect | IBOpenCode | SuperClaude |
|--------|------------|-------------|
| Prefix | `/rf:` | `/sc:` |
| Definition | `.opencode/command/*.md` | `.claude/skills/*/SKILL.md` |
| Invocation | Native slash command | Skill tool or slash command |
| Routing | To orchestrator agent | Via behavioral flow + MCP |

**Advantages of SuperClaude**:
- Explicit `allowed-tools` specification in frontmatter
- Integrated with Claude Code's native skill system
- Clear boundaries section for scope control
- MCP server integration patterns documented inline

---

## 4. crossLLM Integration Protocol

### IBOpenCode Approach
```yaml
Command: /rf:crossLLM v2 file <chain> <artifact_path>
Purpose: Cross-model validation and upgrade
Output: .dev/runs/rf-crossLLM/<runId>/
Process:
  1. Invoke crossLLM for artifact
  2. Wait for completion
  3. Read scorecard.md
  4. If score >= threshold: replace with upgrade.md
  5. Else: keep original, log warning
```

### SuperClaude Equivalent

**Approach**: Multi-Agent Task Orchestration + Quality Gates

SuperClaude achieves cross-validation through **sub-agent delegation** and **verification tiers**, not cross-model calls.

**Implementation Strategy**:

1. **Sub-Agent Verification** (Task tool with specialized agents):
```yaml
Verification Pipeline:
  1. Primary Agent: Generates artifact
  2. Task(quality-engineer): Verifies quality
  3. Task(security-engineer): Security review (if applicable)
  4. Task(self-review): Self-check protocol
```

2. **Compliance Tier Enforcement** (`/sc:task --compliance strict`):
```yaml
STRICT Tier Verification:
  1. Spawn verification sub-agent (quality-engineer)
  2. Execute comprehensive tests
  3. Answer adversarial questions
  4. If passes: proceed
  5. If fails: block and report
```

3. **Multi-Agent Panel** (for critical artifacts):
```yaml
Panel Review Process:
  1. Generate artifact
  2. Spawn review panel:
     - quality-engineer: Quality assessment
     - security-engineer: Security review
     - root-cause-analyst: Gap analysis
  3. Collect verdicts
  4. Synthesize feedback
  5. Decision: accept, revise, or reject
```

**SuperClaude Implementation Example**:

```markdown
# /sc:validate-artifact - Artifact Validation Skill

## Purpose
Cross-validate artifacts through multi-agent review.

## Behavioral Flow

### 1. Artifact Analysis
- Load artifact via Read
- Identify artifact type (roadmap, spec, code)
- Select appropriate validation agents

### 2. Validation Pipeline
```yaml
validation_pipeline:
  step_1:
    agent: quality-engineer
    focus: "completeness, clarity, consistency"
    output: quality_score

  step_2:
    agent: self-review
    focus: "logical coherence, assumptions"
    output: coherence_score

  step_3:
    agent: requirements-analyst
    focus: "requirement coverage"
    output: coverage_score
```

### 3. Scoring and Decision
```yaml
scoring:
  threshold: 0.85
  weights:
    quality: 0.4
    coherence: 0.3
    coverage: 0.3

decision:
  if combined_score >= 0.85:
    action: accept
  elif combined_score >= 0.70:
    action: revise
    feedback: synthesized_improvements
  else:
    action: reject
    reason: detailed_gaps
```

### 4. Output Generation
- Write scorecard.md to output directory
- If accepted: mark as validated
- If revision needed: generate improvement suggestions
- If rejected: preserve original, document issues
```

**Advantages of SuperClaude Approach**:
- No external model dependencies (self-contained)
- Leverages specialized agents with domain expertise
- Compliance tier system provides built-in quality gates
- Sub-agent results are traceable and auditable

**Mapping Table**:
| crossLLM Concept | SuperClaude Equivalent |
|------------------|------------------------|
| Cross-model validation | Multi-agent panel review |
| Scorecard generation | Quality-engineer + scoring logic |
| Upgrade mechanism | Iterative revision via `/sc:improve` |
| Threshold comparison | Compliance tier gates (STRICT/STANDARD) |
| Run artifacts | TodoWrite + memory persistence |

---

## 5. Resource Structure (Templates)

### IBOpenCode Approach
```
.opencode/resources/templates/roadmaps/
├── feature-release.md
├── quality-release.md
├── documentation-release.md
└── variants/
    ├── security-release.md
    ├── performance-release.md
    └── migration-release.md
```

### SuperClaude Equivalent

**Location Options**:
1. `plugins/superclaude/templates/` - Plugin-bundled templates
2. `src/superclaude/templates/` - Python package templates
3. `.claude/templates/` - User-installed templates
4. Project-local: `templates/` or `docs/templates/`

**Recommended Structure**:
```
plugins/superclaude/
├── templates/
│   └── roadmaps/
│       ├── feature-release.md
│       ├── quality-release.md
│       ├── documentation-release.md
│       └── variants/
│           ├── security-release.md
│           ├── performance-release.md
│           └── migration-release.md
```

**Template Discovery Pattern**:
```yaml
Template Resolution Order:
  1. Project-local: ./templates/roadmaps/
  2. User config: ~/.claude/templates/roadmaps/
  3. Plugin bundled: plugins/superclaude/templates/roadmaps/
  4. Default: Inline generation based on type

Selection Logic:
  1. Detect project type from requirements
  2. Match against template variants
  3. Score relevance using keyword matching
  4. Select highest-scoring template
```

**Template Format** (SuperClaude style):
```markdown
---
template: feature-release
version: 1.0
applicable: ["new-feature", "enhancement", "expansion"]
personas: ["architect", "backend", "frontend"]
estimated-phases: 4
---

# Feature Release Roadmap Template

## Phase 1: Analysis & Design
### Milestone 1.1: Requirements Gathering
- [ ] Stakeholder interviews
- [ ] Use case documentation
- [ ] Technical feasibility assessment

### Milestone 1.2: Architecture Design
- [ ] System design document
- [ ] Component specifications
- [ ] Integration points

## Phase 2: Implementation
[...]

## Phase 3: Testing & Validation
[...]

## Phase 4: Release & Documentation
[...]

---
## Template Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `{{PROJECT_NAME}}` | Project identifier | MyApp |
| `{{VERSION}}` | Target version | v1.5.0 |
| `{{LEAD}}` | Project lead | @user |
```

**Advantages of SuperClaude**:
- YAML frontmatter for template metadata
- Template resolution with fallback chain
- Persona-aware template selection
- Variable interpolation support

---

## 6. File Naming Conventions

### IBOpenCode Conventions
| Convention | Pattern | Example |
|------------|---------|---------|
| Command Prefix | `/rf:` | `/rf:roadmap-gen` |
| Agent Naming | `@rf-{name}` | `@rf-roadmap-gen-orchestrator` |
| File Paths | `.opencode/` root | `.opencode/command/rf:roadmap-gen.md` |
| Agent Files | Markdown | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

### SuperClaude Conventions

**Naming Patterns**:
| Convention | Pattern | Example |
|------------|---------|---------|
| Command/Skill Prefix | `/sc:` | `/sc:roadmap-gen` |
| Agent Naming | `{role}-{domain}.md` | `roadmap-orchestrator.md` |
| Skill Path | `.claude/skills/{name}/` | `.claude/skills/sc-roadmap-gen/` |
| Skill Entry | `SKILL.md` | `.claude/skills/sc-roadmap-gen/SKILL.md` |
| Command Files | `{name}.md` | `plugins/superclaude/commands/roadmap-gen.md` |
| Agent Files | `{role}.md` | `plugins/superclaude/agents/roadmap-orchestrator.md` |

**File Naming Rules** (SuperClaude):
```yaml
Skills:
  directory: lowercase-with-hyphens
  entry_file: SKILL.md (uppercase)
  example: .claude/skills/sc-task-unified/SKILL.md

Commands:
  file: lowercase-with-hyphens.md
  example: plugins/superclaude/commands/roadmap-gen.md

Agents:
  file: lowercase-with-hyphens.md
  role-based: {role}-{domain}.md
  example: plugins/superclaude/agents/quality-engineer.md

Modes:
  file: MODE_{PascalCase}.md
  example: plugins/superclaude/modes/MODE_Task_Management.md

MCP Configs:
  file: lowercase.json
  example: plugins/superclaude/mcp/configs/sequential.json
```

**Translation Mapping**:
| IBOpenCode | SuperClaude |
|------------|-------------|
| `/rf:roadmap-gen` | `/sc:roadmap-gen` |
| `@rf-roadmap-gen-orchestrator` | `roadmap-orchestrator.md` |
| `.opencode/command/` | `.claude/skills/` or `plugins/superclaude/commands/` |
| `.opencode/agent/` | `plugins/superclaude/agents/` |

---

## 7. Persona System

### IBOpenCode Approach
```yaml
Phase 2: Persona Selection

Thresholds:
  Primary: >40% relevance
  Consulting: >15% relevance

Algorithm:
  For each domain in specification:
    score = domain_weight * relevance_factor
    if score > 40%: assign as Primary
    else if score > 15%: assign as Consulting
```

### SuperClaude Equivalent

**Reference**: `PERSONAS.md` - Comprehensive persona system with 11 specialists

**Persona Categories**:
```yaml
Technical Specialists:
  - architect: Systems design, scalability
  - frontend: UI/UX, accessibility
  - backend: APIs, reliability
  - security: Threat modeling, compliance
  - performance: Optimization, bottlenecks

Process & Quality Experts:
  - analyzer: Root cause, investigation
  - qa: Quality assurance, testing
  - refactorer: Code quality, tech debt
  - devops: Infrastructure, deployment

Knowledge & Communication:
  - mentor: Education, knowledge transfer
  - scribe: Documentation, localization
```

**Auto-Activation System** (Multi-factor scoring):
```yaml
Activation Scoring:
  keyword_matching: 30%      # Domain-specific terms
  context_analysis: 40%      # Project phase, urgency, complexity
  user_history: 20%          # Past preferences, successful outcomes
  performance_metrics: 10%   # Current system state, bottlenecks

Activation Thresholds:
  primary_activation: confidence >= 85%
  consulting_activation: confidence >= 70%
  manual_override: --persona-{name} flag
```

**SuperClaude Persona Definition Structure**:
```markdown
## `--persona-architect`

**Identity**: Systems architecture specialist, long-term thinking focus

**Priority Hierarchy**: Long-term maintainability > scalability > performance

**Core Principles**:
1. Systems Thinking: Analyze impacts across entire system
2. Future-Proofing: Design for growth
3. Dependency Management: Minimize coupling

**MCP Server Preferences**:
- Primary: Sequential (comprehensive analysis)
- Secondary: Context7 (patterns and best practices)

**Optimized Commands**:
- /analyze - System-wide analysis
- /design - Comprehensive system designs
- /estimate - Factors in complexity

**Auto-Activation Triggers**:
- Keywords: "architecture", "design", "scalability"
- Complex system modifications
- Multi-module estimation requests

**Quality Standards**:
- Maintainability: Solutions understandable and modifiable
- Scalability: Designs accommodate growth
- Modularity: Loose coupling, high cohesion
```

**Cross-Persona Collaboration** (SuperClaude feature):
```yaml
Collaboration Patterns:
  architect + performance:
    focus: "System design with performance budgets"
  security + backend:
    focus: "Secure server-side with threat modeling"
  frontend + qa:
    focus: "User-focused with accessibility testing"
  mentor + scribe:
    focus: "Educational content with cultural adaptation"
```

**Roadmap Generator Persona Selection** (Example):
```yaml
/sc:roadmap-gen persona_selection:
  primary:
    - architect (system-wide planning)
    - analyzer (requirement analysis)
  consulting:
    - scribe (documentation quality)
    - devops (deployment planning)

  activation_logic:
    if roadmap.type == "security-release":
      add_primary: security
    if roadmap.type == "performance-release":
      add_primary: performance
    if roadmap.type == "documentation-release":
      add_primary: scribe
```

**Advantages of SuperClaude**:
- Richer persona definitions with MCP preferences
- Cross-persona collaboration patterns
- Explicit quality standards per persona
- Command-specific optimizations documented

---

## 8. Quality Standards

### IBOpenCode Approach
```yaml
Safety Rules:
  - Fabrication Prevention: Never invent data without evidence
  - Schema Stability: Maintain output format consistency
  - Boundary Enforcement: NO writes outside .dev/ or .roadmaps/
  - Validation Gates: Multi-phase quality checks
```

### SuperClaude Equivalent

**Reference**: `RULES.md` + Compliance Tier System + Quality Gates

**Rule Priority System**:
```yaml
Priority Levels:
  CRITICAL (Red):
    - Security, data safety, production breaks
    - Never compromise
    examples:
      - Git workflow (feature branches only)
      - Read before Write/Edit
      - Root cause analysis (never skip)

  IMPORTANT (Yellow):
    - Quality, maintainability, professionalism
    - Strong preference
    examples:
      - TodoWrite for >3 step tasks
      - Complete all started implementations
      - Build only what's asked (MVP first)

  RECOMMENDED (Green):
    - Optimization, style, best practices
    - Apply when practical
    examples:
      - Parallel operations over sequential
      - MCP tools over basic alternatives
```

**Compliance Tier System** (from `/sc:task-unified`):
```yaml
STRICT:
  triggers: [security, auth, database, migration, refactor]
  requirements:
    - Full 6-category checklist
    - Sub-agent verification (quality-engineer)
    - Adversarial question answering
    - Comprehensive test execution

STANDARD:
  triggers: [implement, add, create, update, fix]
  requirements:
    - Context loading before editing
    - Downstream impact check
    - Direct test execution

LIGHT:
  triggers: [typo, comment, whitespace, lint]
  requirements:
    - Quick sanity check
    - No verification delay

EXEMPT:
  triggers: [explain, search, commit, plan]
  requirements:
    - Immediate execution
    - No compliance overhead
```

**Validation Gates** (8-Step Cycle):
```yaml
Quality Gates:
  1. Syntax: Language parsers, Context7 validation
  2. Type: Sequential analysis, type compatibility
  3. Lint: Context7 rules, quality analysis
  4. Security: Vulnerability assessment, OWASP
  5. Test: Playwright E2E, coverage (>=80% unit)
  6. Performance: Benchmarking, optimization
  7. Documentation: Completeness, accuracy
  8. Integration: Deployment validation
```

**Boundary Enforcement** (SuperClaude):
```yaml
File Safety Rules:
  - Always Read before Write/Edit
  - Absolute paths only (no relative)
  - No auto-commit without explicit request
  - Check existing structure before creating files

Output Location Rules:
  - Claude docs: claudedocs/
  - Tests: tests/, __tests__/, test/
  - Scripts: scripts/, tools/, bin/
  - Roadmaps: .roadmaps/<version>/
  - Artifacts: .roadmaps/<version>/artifacts/
```

**Advantages of SuperClaude**:
- Tiered compliance with automatic classification
- Confidence scoring with user override capability
- Integrated quality gates in execution flow
- Rule priority system for conflict resolution

---

## 9. Tasklist Generator

### IBOpenCode Approach
```yaml
Generator: Tasklist-Generator v2.1
Generation Mode: Deterministic
Root Path: .dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/tasklists/

Task ID Convention: T{milestone}.{sequence}
  Examples: T01.01, T02.03
```

### SuperClaude Equivalent

**Primary**: TodoWrite Tool + Task Management Mode
**Secondary**: PM Agent + Serena Memory

**TodoWrite Integration**:
```yaml
TodoWrite Tool:
  scope: Current Claude Code session
  states: [pending, in_progress, completed, blocked]
  capacity: 3-20 tasks per session

  usage:
    1. Create task list with >3 steps
    2. Update status in real-time
    3. One task in_progress at a time
    4. Quality gates before completion
```

**Task Management Mode Layers**:
```yaml
Layer 1 - TodoWrite (Session):
  scope: Current session
  states: [pending, in_progress, completed, blocked]

Layer 2 - /task Command (Project):
  scope: Multi-session features
  structure: Epic -> Story -> Task
  persistence: Cross-session state

Layer 3 - /spawn Command (Meta):
  scope: Complex multi-domain operations
  features: Parallel/sequential coordination

Layer 4 - /loop Command (Iterative):
  scope: Progressive refinement
  features: Iteration cycles with validation
```

**Task ID Convention** (SuperClaude):
```yaml
Hierarchical IDs:
  format: "{phase}.{milestone}.{task}"
  example: "1.2.3" = Phase 1, Milestone 2, Task 3

Status Markers:
  - pending: [square]
  - in_progress: [arrow]
  - completed: [check]
  - blocked: [x]

Example Tasklist:
  - [ ] 1.1.1: Requirements analysis
  - [>] 1.1.2: Stakeholder interviews (in progress)
  - [x] 1.1.3: Use case documentation (completed)
  - [!] 1.1.4: Technical feasibility (blocked on info)
```

**PM Agent Session Lifecycle**:
```yaml
Session Start:
  1. list_memories() -> Check existing state
  2. read_memory("current_plan") -> Restore context
  3. read_memory("last_session") -> Previous summary
  4. read_memory("next_actions") -> Planned tasks

During Work:
  1. TodoWrite: Track immediate tasks
  2. write_memory("checkpoint", progress) -> Every 30min
  3. think_about_task_adherence() -> Self-evaluation

Session End:
  1. think_about_whether_you_are_done() -> Verify completion
  2. write_memory("last_session", summary)
  3. write_memory("next_actions", todos)
```

**Tasklist File Structure** (SuperClaude):
```markdown
---
generator: SuperClaude Roadmap Generator v1.0
mode: deterministic
path: .roadmaps/<version>/tasklists/
created: 2026-01-26
---

# Milestone 1: Requirements Analysis

## Tasks

### T1.1: Stakeholder Requirements
- **ID**: 1.1
- **Status**: pending
- **Assignee**: architect
- **Depends**: none
- **Outputs**: requirements.md

#### Subtasks
- [ ] T1.1.1: Interview stakeholders
- [ ] T1.1.2: Document functional requirements
- [ ] T1.1.3: Identify constraints

### T1.2: Technical Feasibility
- **ID**: 1.2
- **Status**: pending
- **Depends**: T1.1
[...]
```

**Advantages of SuperClaude**:
- Native TodoWrite integration with Claude Code
- Session persistence via Serena memory
- Hierarchical task management across layers
- PM Agent provides PDCA cycle for continuous improvement

---

## 10. Version Management

### IBOpenCode Approach
```yaml
Version Convention:
  v1: Initial draft (pre-upgrade)
  v2+: Post-crossLLM upgrade
  vN: Progressive refinement
```

### SuperClaude Equivalent

**Approach**: Git-based versioning + Serena memory

**Git Integration** (from RULES.md):
```yaml
Git Workflow Rules:
  - Feature branches for ALL work
  - Never work on main/master directly
  - Incremental commits with meaningful messages
  - Create restore points before risky operations

Branch Structure:
  master (production)
    <- integration (testing)
      <- feature/*, fix/*, docs/*

Standard Workflow:
  1. Create branch: git checkout -b feature/roadmap-gen
  2. Develop with tests
  3. Commit: git commit -m "feat: roadmap generation"
  4. Merge to integration -> validate -> merge to master
```

**Version Tracking Pattern**:
```yaml
Roadmap Versions:
  directory: .roadmaps/<version>/
  format: v{major}.{minor}

  versioning_strategy:
    v0.1: Initial draft (WIP)
    v1.0: First complete version (MVP)
    v1.1: Refinements from review
    v2.0: Major revision (breaking changes)

Artifact Versioning:
  file_naming: "{artifact}-{version}.md"
  examples:
    - roadmap-v1.0.md
    - roadmap-v1.1.md (revised)
    - tasklist-milestone-1-v1.0.md
```

**Serena Memory for Version State**:
```yaml
Memory Keys:
  roadmap_version: "1.0"
  last_validation: "2026-01-26"
  revision_history:
    - version: "1.0"
      date: "2026-01-25"
      changes: "Initial generation"
    - version: "1.1"
      date: "2026-01-26"
      changes: "Incorporated review feedback"
```

**SuperClaude Version Commands**:
```markdown
# Version Management via /sc:git

## Create Version Tag
/sc:git tag v1.0 "Initial roadmap release"

## Compare Versions
/sc:git diff v1.0..v1.1

## Version History
/sc:git log --oneline .roadmaps/

## Rollback
/sc:git checkout v1.0 -- .roadmaps/v1.0/roadmap.md
```

**Advantages of SuperClaude**:
- Native Git integration with safety rules
- Serena memory for cross-session version state
- Branch-based development workflow
- Non-destructive versioning with rollback capability

---

## 11. 9-Phase Pipeline

### IBOpenCode Approach
```yaml
9-Phase Agent Pipeline:
  Phase 1: Input Validation
  Phase 2: Persona Selection
  Phase 3: Template Selection
  Phase 4: Roadmap Drafting
  Phase 5: Task Decomposition
  Phase 6: Artifact Generation
  Phase 7: Quality Gates
  Phase 8: crossLLM Integration
  Phase 9: Output Finalization
```

### SuperClaude Equivalent

**Primary**: Wave Orchestration System
**Reference**: `ORCHESTRATOR.md`, `MODES.md`

**Wave System Overview**:
```yaml
Wave Orchestration Engine:
  purpose: Multi-stage command execution with compound intelligence
  auto-activation: complexity >= 0.7 + files > 20 + operation_types > 2

wave-enabled commands:
  tier-1: [/analyze, /build, /implement, /improve]
  tier-2: [/design, /task]

wave-strategies:
  progressive: "Incremental enhancement"
  systematic: "Methodical analysis"
  adaptive: "Dynamic configuration"
```

**9-Phase to Wave Mapping**:

```yaml
IBOpenCode Phase -> SuperClaude Wave/Component:

Phase 1: Input Validation
  -> Wave 1: Detection Engine
  - Parse request for keywords and patterns
  - Match against domain/operation matrices
  - Score complexity (0.0-1.0)
  - Estimate resource requirements

Phase 2: Persona Selection
  -> Wave 1: Persona Auto-Activation
  - Multi-factor scoring (keyword 30%, context 40%, history 20%)
  - Activate primary persona (>85% confidence)
  - Activate consulting personas (>70% confidence)
  - Apply --persona-{name} overrides

Phase 3: Template Selection
  -> Wave 2: Resource Resolution
  - Template discovery chain (local -> user -> plugin -> default)
  - Score template relevance
  - Apply variant selection logic

Phase 4: Roadmap Drafting
  -> Wave 2-3: Planning & Generation
  - Apply TodoWrite for task breakdown
  - Generate roadmap structure
  - Populate milestones and phases

Phase 5: Task Decomposition
  -> Wave 3: Task Management Mode
  - Hierarchical decomposition (Epic -> Story -> Task)
  - Dependency mapping
  - Estimate generation

Phase 6: Artifact Generation
  -> Wave 3-4: Implementation
  - Generate tasklist files
  - Create supporting artifacts
  - Apply templates

Phase 7: Quality Gates
  -> Wave 4: Validation
  - 8-step validation cycle
  - Compliance tier enforcement
  - think_about_task_adherence()

Phase 8: crossLLM Integration
  -> Wave 4-5: Multi-Agent Verification
  - Sub-agent panel (quality-engineer, security-engineer)
  - Adversarial questioning
  - Scoring and decision

Phase 9: Output Finalization
  -> Wave 5: Completion
  - think_about_whether_you_are_done()
  - Memory persistence (write_memory)
  - Git operations (if requested)
```

**Wave Configuration for Roadmap Generation**:
```yaml
/sc:roadmap-gen wave-config:
  waves: 5

  wave-1-analysis:
    purpose: "Input validation and context gathering"
    tools: [Read, Glob, Grep, codebase-retrieval]
    persona: analyzer
    outputs: [requirement_analysis, scope_assessment]

  wave-2-planning:
    purpose: "Persona activation and template selection"
    tools: [TodoWrite, Context7]
    persona: architect
    outputs: [persona_assignment, template_selection]

  wave-3-generation:
    purpose: "Roadmap and task generation"
    tools: [Write, Edit, Sequential]
    personas: [architect, scribe]
    outputs: [roadmap.md, tasklist_files]

  wave-4-validation:
    purpose: "Quality gates and verification"
    tools: [Task(quality-engineer), Bash(tests)]
    gates: [syntax, completeness, consistency]
    outputs: [validation_report, scorecard]

  wave-5-finalization:
    purpose: "Output finalization and persistence"
    tools: [write_memory, git]
    outputs: [final_artifacts, session_state]

wave-transitions:
  1->2: "Analysis complete, scope defined"
  2->3: "Personas active, template selected"
  3->4: "Draft complete, ready for validation"
  4->5: "Validation passed (score >= 0.85)"
```

**Advantages of SuperClaude Wave System**:
- Dynamic wave count (adjusts based on complexity)
- Checkpoint-based transitions with gates
- Integrated validation at each wave boundary
- Parallel execution within waves where possible
- Clear persona and tool assignments per wave

---

## Summary: Translation Completeness

| IBOpenCode Feature | SuperClaude Equivalent | Coverage |
|-------------------|------------------------|----------|
| Framework Architecture | `.claude/` + `plugins/superclaude/` | Complete |
| Agent System | `plugins/superclaude/agents/*.md` + PERSONAS.md | Complete |
| Command Definition | `.claude/skills/*/SKILL.md` | Complete |
| crossLLM Integration | Multi-Agent Task + Compliance Tiers | Complete |
| Resource Structure | `plugins/superclaude/templates/` | Complete |
| File Naming | SuperClaude conventions | Complete |
| Persona System | PERSONAS.md (11 specialists) | Enhanced |
| Quality Standards | RULES.md + Compliance Tiers + Quality Gates | Enhanced |
| Tasklist Generator | TodoWrite + Task Mode + PM Agent | Enhanced |
| Version Management | Git + Serena Memory | Enhanced |
| 9-Phase Pipeline | Wave Orchestration System | Enhanced |

**Key Advantages of SuperClaude Translation**:
1. Native Claude Code integration via plugin/skill system
2. Richer persona system with MCP server preferences
3. Multi-layer task management (session -> project -> meta)
4. Compliance tier system with automatic classification
5. Wave orchestration with dynamic phase adjustment
6. Cross-session persistence via Serena memory
7. Git-based versioning with safety rules

**Gaps/Limitations**:
1. No explicit model/temperature specification (by design - uses thinking flags)
2. No cross-LLM calls (replaced with multi-agent internal validation)
3. Template system requires new files in SuperClaude structure

---

## Next Steps

1. **Create Skill Definition**: Implement `/sc:roadmap-gen` skill in `.claude/skills/sc-roadmap-gen/SKILL.md`
2. **Create Agent Definition**: Add `roadmap-orchestrator.md` to `plugins/superclaude/agents/`
3. **Create Templates**: Add roadmap templates to `plugins/superclaude/templates/roadmaps/`
4. **Implement Wave Config**: Define wave transitions and gates for roadmap generation
5. **Add Tests**: Create validation tests in `tests/sc-roadmap-gen/`
