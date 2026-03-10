# SuperClaude custom command structure — extraction (Haiku-15)

## Source files (verifiable)
- /config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md
- /config/workspace/SuperClaude_Framework/src/superclaude/commands/spawn.md
- /config/workspace/SuperClaude_Framework/src/superclaude/commands/task-unified.md

---

## 1) What these files show about SuperClaude custom command structure

### 1.1 Command definition file format
Each custom command definition is a **single Markdown file** with:

1) **YAML frontmatter metadata block** (starts with `---` and ends with `---`)
2) A **Markdown body** that documents the command (purpose, usage, flags, flow, boundaries, examples, etc.)

This is consistent across:
- `/config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/commands/spawn.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/commands/task-unified.md`

### 1.2 YAML frontmatter fields used (observed)
The frontmatter defines the command’s identity and orchestration metadata.

**Common fields (seen in all 3):**
- `name`: command name (e.g., `adversarial`, `spawn`, `task`)
- `description`: short summary string
- `category`: command category (e.g., `analysis`, `special`)
- `complexity`: qualitative complexity (e.g., `advanced`, `high`)
- `mcp-servers`: list of MCP servers the command uses (may be empty)
- `personas`: list of personas involved/activated (may be empty)

**Additional fields (seen in `task-unified.md`):**
- `version`: explicit command spec version (e.g., `"2.0.0"`)

### 1.3 Markdown body: standard documentation sections/patterns
Across the three commands, the body tends to include these sections (names vary, but structure is recognizable):

- **Title header**: typically `# /sc:<name> - <Human readable title>`
- **Purpose / Required Input / Triggers**: what this command is for and when to use it
- **Usage**: command line examples in fenced code blocks
- **Arguments / Options / Flags**: tables listing flags, requirements, defaults, descriptions
- **Behavioral Flow / Behavioral Summary**: step-by-step protocol of what the command does
- **Tool / MCP integration**: which tools/servers are involved and how
- **Patterns / Matrices**: e.g., server selection matrix, persona matrix, delegation matrix
- **Examples**: several “copy/paste” invocations
- **Boundaries**: explicit “Will / Will Not” lists and critical constraints
- **Related Commands** (optional): where the command fits within the broader framework

### 1.4 Command-specific structural conventions (by file)

#### A) `/sc:adversarial` definition structure
- Frontmatter declares:
  - category: `analysis`
  - MCP servers: `[sequential, context7, serena]`
  - personas: `[architect, analyzer, scribe]`
- Body defines **two modes** with distinct required inputs:
  - Mode A: compare existing artifacts (`--compare file1,file2,...`)
  - Mode B: generate variants and compare (`--source`, `--generate`, `--agents`)
- A single **Options table** documents all flags with short aliases, required conditions, defaults.
- Includes a “Behavioral Summary” describing a **5-step protocol** and enumerating **6 produced artifacts**.
- Includes “Boundaries” with explicit “Will / Will Not” and responsibility constraints.
- Includes “Related Commands” mapping how it integrates with other `/sc:*` commands.

#### B) `/sc:spawn` definition structure
- Frontmatter declares:
  - category: `special`
  - MCP servers: `[]` (none)
  - personas: `[]` (none)
- Sections include “Triggers”, “Usage”, “Behavioral Flow”, “MCP Integration”, “Tool Coordination”, “Key Patterns”, “Examples”, “Boundaries”.
- Contains an explicit “CRITICAL BOUNDARIES” block stating:
  - **STOP AFTER TASK DECOMPOSITION**
  - Output is **task hierarchy only**
  - Explicitly will **not** execute tasks or modify code
  - Output must include Epic decomposition, dependencies, delegation assignments, strategy

#### C) `/sc:task` (unified task command) definition structure
- Frontmatter declares:
  - category: `special`
  - version: `2.0.0`
  - MCP servers includes multiple servers: `[sequential, context7, serena, playwright, magic, morphllm]`
  - personas includes a large matrix of roles
- Body is a comprehensive spec, including:
  - Purpose and philosophy
  - Triggers and auto-activation patterns
  - Usage and flag tables grouped by “Strategy”, “Compliance”, “Execution Control”, “Verification”
  - A structured “Behavioral Flow” list
  - A “Tiered Compliance Model” with 4 tiers (STRICT/STANDARD/LIGHT/EXEMPT)
  - Embedded markdown checklists/templates and SMART acceptance criteria
  - A YAML “Auto-Detection Algorithm” and “Compound Phrase Handling”
  - MCP server selection matrix (Always Active vs Conditional)
  - Persona coordination YAML
  - Tool coordination table and tier-specific tool requirements
  - Sub-agent delegation matrix
  - Escape hatches table
  - Success metrics table
  - Boundaries (Will / Will Not)
  - Migration guidance from legacy commands and version history

---

## 2) Exact content (verbatim) — adversarial.md

**Source:** /config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md

```markdown
---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---

# /sc:adversarial - Adversarial Debate & Merge Pipeline

## Required Input
- Mode A: `--compare file1,file2[,...,fileN]` (2-10 existing files)
- Mode B: `--source <file> --generate <type> --agents <spec>[,...]` (generate + compare)

## Usage

```bash
# Mode A: Compare existing files
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]

# Mode B: Generate variants from source + compare
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,...] [options]
```

### Arguments

**Mode A (Compare)**:
- `--compare`: Comma-separated file paths (2-10 existing files)

**Mode B (Generate + Compare)**:
- `--source`: Source file for variant generation
- `--generate`: Type of artifact to generate (roadmap, spec, design, etc.)
- `--agents`: Agent specifications in `model[:persona[:"instruction"]]` format

## Options

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--compare` | `-c` | Mode A | - | Comma-separated file paths (2-10) |
| `--source` | `-s` | Mode B | - | Source file for variant generation |
| `--generate` | `-g` | Mode B | - | Type of artifact to generate |
| `--agents` | `-a` | Mode B | - | Agent specs: `model[:persona[:"instruction"]]` |
| `--depth` | `-d` | No | `standard` | Debate depth: quick, standard, deep |
| `--convergence` | | No | `0.80` | Alignment threshold (0.50-0.99) |
| `--interactive` | `-i` | No | `false` | Pause for user input at decision points |
| `--output` | `-o` | No | Auto | Output directory for artifacts |
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |

## Behavioral Summary

5-step adversarial protocol: Step 1 (diff analysis across variants), Step 2 (structured adversarial debate with configurable depth), Step 3 (hybrid quantitative-qualitative scoring and base selection), Step 4 (refactoring plan generation), Step 5 (merge execution with provenance annotations). Produces 6 artifacts: diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, and the merged output.

## Examples

### Compare Two Roadmap Drafts
```bash
/sc:adversarial --compare draft-a.md,draft-b.md --depth standard
```

### Generate 3 Variants with Different Personas
```bash
/sc:adversarial --source auth-spec.md --generate roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer \
  --depth deep --convergence 0.85
```

### Compare 5 Specs with Interactive Mode
```bash
/sc:adversarial --compare spec1.md,spec2.md,spec3.md,spec4.md,spec5.md \
  --interactive --depth deep
```

### Quick Comparison with Focused Debate
```bash
/sc:adversarial --compare plan-a.md,plan-b.md \
  --depth quick --focus structure,completeness
```

### Full Pipeline with Custom Output
```bash
/sc:adversarial --source migration-plan.md --generate roadmap \
  --agents opus:architect:"prioritize backward compatibility",sonnet:security:"zero-trust" \
  --depth deep --output .dev/releases/current/migration-v2/
```

## Boundaries

**Will:**
- Compare 2-10 artifacts through structured adversarial debate
- Generate variant artifacts using different model/persona configurations
- Produce transparent, documented merge decisions with full scoring breakdown
- Execute refactoring plans to produce unified outputs with provenance annotations
- Support configurable depth, convergence thresholds, and focus areas
- Work as a generic tool invocable by any SuperClaude command

**Will Not:**
- Validate domain-specific correctness of merged output (calling command's responsibility)
- Execute the merged output (planning/merge tool, not execution tool)
- Manage git operations or version control
- Make decisions without documented rationale
- Operate with fewer than 2 variants (minimum for adversarial comparison)
- Override user decisions in interactive mode

## Related Commands

| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:roadmap` | Multi-spec/multi-roadmap modes | `/sc:roadmap --specs spec1.md,spec2.md` |
| `/sc:design` | Compare architectural designs | `/sc:adversarial --compare design-a.md,design-b.md` |
| `/sc:spec-panel` | Augment panel with adversarial review | Invoke adversarial post-panel |
| `/sc:improve` | Compare improvement approaches | Generate competing plans, merge best |
```

---

## 3) Exact content (verbatim) — spawn.md

**Source:** /config/workspace/SuperClaude_Framework/src/superclaude/commands/spawn.md

```markdown
---
name: spawn
description: "Meta-system task orchestration with intelligent breakdown and delegation"
category: special
complexity: high
mcp-servers: []
personas: []
---

# /sc:spawn - Meta-System Task Orchestration

## Triggers
- Complex multi-domain operations requiring intelligent task breakdown
- Large-scale system operations spanning multiple technical areas
- Operations requiring parallel coordination and dependency management
- Meta-level orchestration beyond standard command capabilities

## Usage
```
/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

## Behavioral Flow
1. **Analyze**: Parse complex operation requirements and assess scope across domains
2. **Decompose**: Break down operation into coordinated subtask hierarchies
3. **Orchestrate**: Execute tasks using optimal coordination strategy (parallel/sequential)
4. **Monitor**: Track progress across task hierarchies with dependency management
5. **Integrate**: Aggregate results and provide comprehensive orchestration summary

Key behaviors:
- Meta-system task decomposition with Epic → Story → Task → Subtask breakdown
- Intelligent coordination strategy selection based on operation characteristics
- Cross-domain operation management with parallel and sequential execution patterns
- Advanced dependency analysis and resource optimization across task hierarchies
## MCP Integration
- **Native Orchestration**: Meta-system command uses native coordination without MCP dependencies
- **Progressive Integration**: Coordination with systematic execution for progressive enhancement
- **Framework Integration**: Advanced integration with SuperClaude orchestration layers

## Tool Coordination
- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Read/Grep/Glob**: System analysis and dependency mapping for complex operations
- **Edit/MultiEdit/Write**: Coordinated file operations with parallel and sequential execution
- **Bash**: System-level operations coordination with intelligent resource management

## Key Patterns
- **Hierarchical Breakdown**: Epic-level operations → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Sequential (dependency-ordered) → Parallel (independent) → Adaptive (dynamic)
- **Meta-System Coordination**: Cross-domain operations → resource optimization → result integration
- **Progressive Enhancement**: Systematic execution → quality gates → comprehensive validation

## Examples

### Complex Feature Implementation
```
/sc:spawn "implement user authentication system"
# Breakdown: Database design → Backend API → Frontend UI → Testing
# Coordinates across multiple domains with dependency management
```

### Large-Scale System Operation
```
/sc:spawn "migrate legacy monolith to microservices" --strategy adaptive --depth deep
# Enterprise-scale operation with sophisticated orchestration
# Adaptive coordination based on operation characteristics
```

### Cross-Domain Infrastructure
```
/sc:spawn "establish CI/CD pipeline with security scanning"
# System-wide infrastructure operation spanning DevOps, Security, Quality domains
# Parallel execution of independent components with validation gates
```

## Boundaries

**Will:**
- Decompose complex multi-domain operations into coordinated task hierarchies
- Provide intelligent orchestration with parallel and sequential coordination strategies
- Execute meta-system operations beyond standard command capabilities

**Will Not:**
- Replace domain-specific commands for simple operations
- Override user coordination preferences or execution strategies
- Execute operations without proper dependency analysis and validation

## CRITICAL BOUNDARIES

**STOP AFTER TASK DECOMPOSITION**

This command produces a TASK HIERARCHY ONLY - delegates execution to other commands.

**Explicitly Will NOT**:
- Execute implementation tasks directly
- Write or modify code
- Create system changes
- Replace domain-specific commands

**Output**: Task breakdown document with:
- Epic decomposition
- Task hierarchy with dependencies
- Delegation assignments (which `/sc:*` command handles each task)
- Coordination strategy

**Next Step**: Execute individual tasks using delegated commands (`/sc:implement`, `/sc:design`, `/sc:test`, etc.)
```

---

## 4) Exact content (verbatim) — task-unified.md

**Source:** /config/workspace/SuperClaude_Framework/src/superclaude/commands/task-unified.md

```markdown
---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
version: "2.0.0"
---

# /sc:task - Unified Task Command

## Purpose

A unified command with **orthogonal dimensions** that merges orchestration capabilities with MCP compliance enforcement:

```
/sc:task [operation] --strategy [systematic|agile|enterprise] --compliance [strict|standard|light|exempt]
```

| Dimension | Purpose | Options |
|-----------|---------|---------|
| **Strategy** | HOW to coordinate work | systematic, agile, enterprise, auto |
| **Compliance** | HOW strictly to enforce quality | strict, standard, light, exempt, auto |

**Philosophy**: "Better false positives than false negatives" - when uncertain, escalate to higher compliance tier.

---

## Triggers

### Auto-Activation Patterns

| Trigger Type | Condition | Confidence |
|--------------|-----------|------------|
| **Complexity Score** | Task complexity >0.6 with code modifications | 90% |
| **Multi-file Scope** | Estimated affected files >2 | 85% |
| **Security Domain** | Paths contain `auth/`, `security/`, `crypto/` | 95% |
| **Refactoring Scope** | Keywords: refactor, remediate, multi-file | 90% |
| **Test Remediation** | Keywords: fix tests, test failures | 88% |

### Keyword Triggers

```yaml
explicit_invocation:
  - "/sc:task [description]"
  - "/sc:task [operation] --strategy [type]"
  - "/sc:task [operation] --compliance [tier]"

auto_suggest_keywords:
  high_confidence:
    - "implement feature"
    - "refactor system"
    - "fix security"
    - "add authentication"
    - "update database schema"

  moderate_confidence:
    - "add new"
    - "create component"
    - "update service"
    - "modify API"
```

### Context Signals

The command should be suggested when:
- User describes a multi-step implementation task
- Task involves code modifications with downstream impacts
- Security or data integrity domains are involved
- User explicitly requests compliance workflow
- Previous similar tasks benefited from structured execution

---

## Usage

```bash
/sc:task [operation] [target] [flags]
```

### Strategy Flags (Orchestration Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

### Compliance Flags (Quality Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) | Most tasks |

### Execution Control Flags

| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--reason "..."` | Required justification for tier override |

### Verification Flags

| Flag | Description |
|------|-------------|
| `--verify critical` | Full sub-agent verification |
| `--verify standard` | Direct test execution only |
| `--verify skip` | Skip verification (use with caution) |
| `--verify auto` | Auto-select based on compliance tier (default) |

---

## Behavioral Flow

1. **Analyze**: Parse task requirements, detect keywords, estimate scope
2. **Classify**: Determine compliance tier using auto-detection algorithm
3. **Display**: Announce determined tier with confidence and rationale
4. **Delegate**: Route to appropriate MCP servers and activate relevant personas
5. **Execute**: Apply appropriate checklist based on tier
6. **Verify**: Validate completion using tier-appropriate verification
7. **Report**: Summarize enforcement outcomes and learnings

---

## Tiered Compliance Model

### TIER 1: STRICT (Full Workflow Enforcement)

**Auto-Triggers:**
- Multi-file edits (>2 files)
- Security domain (auth/, security/, crypto/)
- Database/schema changes
- API contract modifications
- Refactoring operations
- Test remediation workflows
- Exploratory "try this and see" coding

**SMART Acceptance Criteria:**
- **S**pecific: All 6 checklist categories completed
- **M**easurable: 100% checklist completion rate
- **A**chievable: <25% overhead relative to task time
- **R**elevant: Prevents regressions in high-impact changes
- **T**ime-bound: Verification completes within 60 seconds

**Mandatory Checklist:**

```markdown
## PRE-WORK CHECKLIST (MUST COMPLETE)
[ ] Project activated? (mcp__serena__activate_project)
[ ] Git working directory clean? (git status)
[ ] Context loaded for task area? (codebase-retrieval)
[ ] Relevant memories read? (list_memories → read_memory)

## TASK EXECUTION TEMPLATE
### CONTEXT LOADING
1. [ ] Primary file(s) to edit: ___
2. [ ] Related files to understand: ___
3. [ ] Test files that validate: ___

### IMPLEMENTATION
1. [ ] View current code state (codebase-retrieval/view)
2. [ ] Make change using appropriate tool
3. [ ] List exact changes made: ___

### DOWNSTREAM IMPACT ANALYSIS
1. [ ] Files that import changed code: ___
2. [ ] Tests that exercise changed code: ___
3. [ ] Update all affected files: [list]

### VERIFICATION (MANDATORY)
Spawn: quality-engineer sub-agent
1. [ ] Run affected tests: pytest [path] -v
2. [ ] Verify no regressions
3. [ ] Check for error patterns in output

### ADVERSARIAL REVIEW
1. [ ] Could this break existing functionality? ___
2. [ ] Were ALL instances updated? ___
3. [ ] Are there edge cases? ___

### COMPLETION CRITERIA
- [ ] All implementation steps done
- [ ] All downstream impacts addressed
- [ ] Verification agent reports PASS
- [ ] Adversarial questions answered satisfactorily
```

**Post-Task "Did I?" Checklist:**
```markdown
[ ] Did I load context before editing?
[ ] Did I find and update downstream impacts?
[ ] Did I spawn a verification agent?
[ ] Did I ask adversarial questions?
[ ] Did I update memory with patterns discovered?
[ ] Did I verify completion criteria?
```

---

### TIER 2: STANDARD (Core Rules Enforcement)

**Auto-Triggers:**
- Single-file code changes
- Adding new files
- Configuration updates
- Code-adjacent documentation

**SMART Acceptance Criteria:**
- **S**pecific: Context loaded, impacts checked, basic verification performed
- **M**easurable: ≥1 codebase-retrieval call, ≥1 downstream impact search
- **A**chievable: <15% overhead relative to task time
- **R**elevant: Prevents common regressions in typical code changes
- **T**ime-bound: Verification completes within 30 seconds

**Required Checklist:**

```markdown
## CORE RULES CHECKLIST
[ ] Context loaded before editing (Rule 1: Always Retrieve Before Edit)
[ ] Downstream impacts checked (Rule 2: Find Downstream Impacts)
[ ] Changes verified working (Rule 6: Always Verify - can be manual)

## QUICK VALIDATION
- [ ] Code compiles/runs
- [ ] Basic functionality tested
- [ ] No obvious regressions
```

**Verification**: Manual verification acceptable; sub-agent optional but recommended.

---

### TIER 3: LIGHT (Awareness Only)

**Auto-Triggers:**
- Minor fixes (typos, formatting)
- Comment updates
- Single-line changes
- Non-functional changes (lint, whitespace)

**SMART Acceptance Criteria:**
- **S**pecific: Change made, no unexpected side effects
- **M**easurable: Modified files ≤2, changed lines ≤50
- **A**chievable: <5% overhead (essentially no process overhead)
- **R**elevant: Appropriate for truly trivial changes
- **T**ime-bound: No verification delay

**Guidance:**
- Be AWARE of MCP principles
- Apply judgment on verification needs
- Skip formal process unless uncertain
- Document if change has unexpected scope

---

### TIER 4: EXEMPT (No Enforcement)

**Auto-Triggers:**
- Questions/explanations ("what does X do?")
- Code exploration (read-only)
- Brainstorming/planning discussions
- Git operations (status, diff, log)
- Documentation-only changes

**SMART Acceptance Criteria:**
- **S**pecific: Task is read-only OR documentation-only
- **M**easurable: Zero code files modified
- **A**chievable: 0% overhead
- **R**elevant: No compliance needed for non-modification activities
- **T**ime-bound: Immediate execution

**Behavior:** No MCP workflow enforcement. Proceed normally.

---

## Auto-Detection Algorithm

```yaml
tier_detection:
  # Priority 1: STRICT (safety-critical)
  strict_triggers:
    keywords:
      security: [security, auth, authentication, password, token, encrypt, credential]
      data_integrity: [database, migration, schema, model, transaction]
      scope: [refactor, remediate, "fix tests", multi-file, system-wide]
      api: [api contract, breaking change, public interface]
    path_patterns: ["auth/", "security/", "crypto/", "models/", "migrations/"]
    file_count: "> 2"
    complexity_score: "> 0.7"

  # Priority 2: EXEMPT (non-code work)
  exempt_triggers:
    keywords: [what, how, why, explain, understand, explore, brainstorm, plan]
    patterns: ["^what (is|are|does)", "^how (do|does|can)", "^explain"]
    read_only: true
    documentation_only: true
    git_operations: ["git status", "git diff", "git log"]

  # Priority 3: LIGHT (trivial changes)
  light_triggers:
    keywords: [typo, format, comment, minor, quick, spacing, lint, rename]
    compound_phrases: ["quick fix", "minor change", "fix typo", "small update"]
    estimated_lines: "< 10"

  # Priority 4: STANDARD (typical code work)
  standard_triggers:
    keywords: [add, create, implement, build, update, modify, change, fix, remove]
    file_count: "1-2"
    single_component: true

  # Conflict resolution
  priority_order: [STRICT, EXEMPT, LIGHT, STANDARD]
  fallback: STANDARD  # When uncertain, moderate enforcement

  # Escalation rule
  ambiguity_handling: "When scores within 0.1, escalate to higher priority tier"
```

### Compound Phrase Handling

```yaml
compound_phrases:
  # LIGHT overrides
  light_wins:
    - "quick fix" → LIGHT (overrides "fix" → STANDARD)
    - "minor change" → LIGHT (overrides "change" → STANDARD)
    - "fix typo" → LIGHT (overrides "fix" → STANDARD)
    - "refactor comment" → LIGHT (overrides "refactor" → STRICT)

  # STRICT overrides
  strict_wins:
    - "fix security" → STRICT (overrides "fix" → STANDARD)
    - "add authentication" → STRICT (overrides "add" → STANDARD)
    - "quick security" → STRICT (security always wins)
    - "minor auth change" → STRICT (auth changes are never minor)
```

---

## MCP Integration

### Server Selection Matrix

| Server | Always Active | Conditional Activation | Purpose |
|--------|---------------|----------------------|---------|
| Sequential | Yes | - | Reasoning, analysis, tier classification |
| Context7 | Yes | - | Patterns, best practices, documentation |
| Serena | Yes | - | Memory persistence, project context |
| Playwright | No | STRICT + (UI or E2E tasks) | Browser verification |
| Magic | No | --with-ui flag | UI component generation |
| Morphllm | No | --with-bulk-edit flag | Large-scale transformations |

### Persona Coordination

```yaml
persona_matrix:
  core:
    - architect      # System design, dependencies
    - analyzer       # Root cause, investigation
    - qa             # Quality, verification
    - refactorer     # Code quality, cleanup

  domain:
    backend:
      personas: [python-expert, backend-architect]
      triggers: [".py files", "api/", "services/"]
    frontend:
      personas: [frontend]
      triggers: [".jsx", ".tsx", ".vue", "components/"]
    security:
      personas: [security-engineer]
      triggers: ["auth/", "security/", STRICT tier]

  verification:
    personas: [quality-engineer]
    triggers: [STRICT compliance tier]
```

---

## Tool Coordination

| Tool | Purpose | Usage Pattern |
|------|---------|---------------|
| **TodoWrite** | Task tracking | Create at planning, update during execution |
| **Read** | File inspection | Pre-work analysis, context gathering |
| **Edit/Write** | Code modification | Execute planned changes |
| **Glob** | File discovery | Identify affected files for classification |
| **Grep** | Pattern search | Find references, dependencies |
| **Bash** | Command execution | Run tests, linters, build commands |
| **Task** | Sub-agent delegation | Spawn verification agents |

### Tier-Specific Tool Usage

| Tier | Required Tools | Optional Tools |
|------|----------------|----------------|
| **STRICT** | TodoWrite, Read, Edit, Bash, Task, Sequential, Serena | Playwright, Magic |
| **STANDARD** | TodoWrite, Read, Edit, Bash, Sequential | Context7, Serena |
| **LIGHT** | Read, Edit | TodoWrite, Bash |
| **EXEMPT** | Read | Any |

---

## Sub-Agent Delegation Matrix (STRICT Tier)

| Task Type | Primary Agent | Verification Agent |
|-----------|---------------|-------------------|
| Python code fixes | python-expert | quality-engineer |
| Architecture decisions | backend-architect | quality-engineer |
| Test remediation | python-expert | quality-engineer |
| Refactoring | refactoring-expert | quality-engineer |
| Security concerns | security-engineer | quality-engineer |
| Performance issues | performance-engineer | quality-engineer |
| UI components | frontend | quality-engineer |

---

## Examples

### Systematic Feature Implementation
```bash
/sc:task "implement user authentication system" --strategy systematic --compliance strict
# Auto-detects: STRICT (authentication keyword, multi-file expected)
# Activates: architect, security, backend personas
# Enforces: Full checklist, verification agent, adversarial review
```

### Standard Code Update
```bash
/sc:task "add input validation to user endpoint"
# Auto-detects: STANDARD (add keyword, single component)
# Enforces: Core rules, basic validation
```

### Quick Fix
```bash
/sc:task "fix typo in error message" --compliance light
# Explicit LIGHT tier
# Enforces: Awareness only, proceed with judgment
```

### Exploration
```bash
/sc:task "explain how the auth middleware works"
# Auto-detects: EXEMPT (explain keyword, read-only)
# No enforcement, proceeds normally
```

### Override Examples
```bash
/sc:task "update logging format" --force-strict
# Forces STRICT even if auto-detected as STANDARD

/sc:task "experimental change" --skip-compliance
# Skips all compliance enforcement (escape hatch)

/sc:task "change config" --compliance standard --reason "Low risk, well understood"
# Explicit tier with documented reason
```

---

## Escape Hatches

| Escape Hatch | Usage | Requirements |
|--------------|-------|--------------|
| `--skip-compliance` | Bypass all compliance | Reason auto-logged |
| `--force-strict` | Force STRICT tier | None |
| `--verify skip` | Skip verification | Only valid for LIGHT/EXEMPT |
| Manual override | Request different tier | `--reason` flag required |

### When to Use Escape Hatches

Use `--skip-compliance` when:
- You're absolutely certain the task doesn't need workflow
- Rapid prototyping in non-production branch
- Task is truly trivial and well-understood
- You've already completed the workflow mentally

**Warning**: Overuse defeats the purpose. If frequently skipping, reconsider task categorization.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tier classification accuracy | ≥80% | User feedback on appropriateness |
| User confusion rate | <10% | "Which command?" questions |
| Skip rate | <12% | Override tracking |
| Regression prevention | ≥85% | Post-verification bug detection |
| STRICT overhead | <25% of task time | Execution telemetry |
| Context loaded before edit | 100% | STRICT/STANDARD tiers |
| Verification agents spawned | 100% | STRICT tier |

---

## Boundaries

### Will

| Capability | Description | Applicable Tiers |
|------------|-------------|------------------|
| **Classify Tasks** | Automatically determine compliance tier | All |
| **Enforce Checklists** | Execute pre/post-work verification | STRICT, STANDARD |
| **Spawn Verification Agents** | Create sub-agents for verification | STRICT |
| **Track Decisions** | Persist task context to memory | All |
| **Generate Documentation** | Auto-document changes and rationale | STRICT, STANDARD |
| **Coordinate MCP Servers** | Orchestrate Sequential, Context7, Serena | All |
| **Escalate Uncertainty** | Higher tier when confidence <0.7 | All |
| **Support Overrides** | Allow tier overrides with justification | All |

### Will Not

| Restriction | Rationale |
|-------------|-----------|
| **Modify Code Without Verification** | STRICT requires verification |
| **Skip Security Checks** | Security domains always STRICT |
| **Execute Destructive Operations Silently** | Requires explicit confirmation |
| **Override User Selection Without Consent** | User can always force tier |
| **Store Sensitive Data in Memory** | Passwords, tokens excluded |
| **Bypass Circuit Breakers** | MCP failures respect breakers |
| **Execute Unbounded Batches** | Max 15 changes per batch |
| **Learn from Overrides** | --skip-compliance excluded from learning |

---

## Migration from Legacy Commands

### From `/sc:task` (v1.x)
```bash
# Old
/sc:task create "feature" --strategy systematic

# New (equivalent)
/sc:task "feature" --strategy systematic --compliance auto
```

### From `/sc:task-mcp`
```bash
# Old
/sc:task-mcp "fix tests" --tier strict

# New (equivalent)
/sc:task "fix tests" --compliance strict
```

### Deprecation Notice

`/sc:task-mcp` is deprecated. Use `/sc:task --compliance [tier]` instead.
Migration assistance: Run `/sc:task --help migrate` for guidance.

---

## Version History

- **v2.0.0** - Unified command merging sc:task and sc:task-mcp
- **v1.0.0** - Original sc:task orchestration command
```
