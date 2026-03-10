# Extract: SuperClaude Command Definition Patterns

**Extraction date**: 2026-02-21
**Source files**:
1. `/config/workspace/SuperClaude_Framework/src/superclaude/commands/adversarial.md`
2. `/config/workspace/SuperClaude_Framework/src/superclaude/commands/spawn.md`
3. `/config/workspace/SuperClaude_Framework/src/superclaude/commands/task-unified.md`

**Purpose**: Document the complete anatomy of a SuperClaude command `.md` file by comparing three distinct command patterns (analysis pipeline, meta-orchestrator, unified task executor).

---

## 1. Command File Anatomy - Universal Structure

Every SuperClaude command `.md` file follows this structure:

```
1. YAML Frontmatter (metadata block)
2. Title heading with command name
3. Triggers / Required Input
4. Usage section with CLI syntax
5. Options / Flags tables
6. Behavioral Flow (numbered steps)
7. Domain-specific content (tiers, algorithms, etc.)
8. MCP Integration section
9. Tool Coordination section
10. Key Patterns section (some commands)
11. Examples section
12. Boundaries section (Will / Will Not)
13. Related Commands / Migration (optional)
```

Not all commands include every section. The sections present depend on the command's complexity and category.

---

## 2. YAML Frontmatter (Metadata Block)

The frontmatter is enclosed in `---` delimiters and declares the command's identity to the framework.

### Pattern A: adversarial.md (Analysis Pipeline)

```yaml
---
name: adversarial
description: "Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts"
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
---
```

### Pattern B: spawn.md (Meta-Orchestrator)

```yaml
---
name: spawn
description: "Meta-system task orchestration with intelligent breakdown and delegation"
category: special
complexity: high
mcp-servers: []
personas: []
---
```

### Pattern C: task-unified.md (Unified Task Executor)

```yaml
---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
version: "2.0.0"
---
```

### Frontmatter Field Reference

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Command identifier (used after `/sc:`) |
| `description` | Yes | string | One-line purpose summary |
| `category` | Yes | string | Routing category: `analysis`, `special`, `development`, `quality`, `meta` |
| `complexity` | Yes | string | Complexity level: `simple`, `moderate`, `high`, `advanced` |
| `mcp-servers` | Yes | array | MCP servers the command uses. Empty array `[]` if none |
| `personas` | Yes | array | Personas the command activates. Empty array `[]` if none |
| `version` | No | string | Semantic version (only task-unified uses this) |

**Key observations**:
- `spawn` declares empty arrays for both `mcp-servers` and `personas`, signaling it is a pure orchestrator with no direct MCP dependencies.
- `task-unified` lists the most MCP servers (6) and personas (10), reflecting its role as the framework's most comprehensive execution command.
- `adversarial` is selective: 3 MCP servers, 3 personas -- scoped to its analysis domain.

---

## 3. Trigger Definitions

Triggers tell the framework when to suggest or auto-activate the command.

### Pattern A: adversarial.md -- Required Input (No Auto-Triggers)

Adversarial does not define auto-activation triggers. Instead, it defines **required input modes**:

```markdown
## Required Input
- Mode A: `--compare file1,file2[,...,fileN]` (2-10 existing files)
- Mode B: `--source <file> --generate <type> --agents <spec>[,...]` (generate + compare)
```

This means adversarial is always explicitly invoked, never auto-suggested. It operates in one of two mutually exclusive modes.

### Pattern B: spawn.md -- Bullet-List Triggers

```markdown
## Triggers
- Complex multi-domain operations requiring intelligent task breakdown
- Large-scale system operations spanning multiple technical areas
- Operations requiring parallel coordination and dependency management
- Meta-level orchestration beyond standard command capabilities
```

Spawn uses a simple bullet list of natural-language conditions. No keyword tables, no confidence scores, no YAML.

### Pattern C: task-unified.md -- Structured Multi-Level Triggers

Task-unified defines the most sophisticated trigger system with three sub-sections:

**Auto-Activation Patterns** (table with confidence scores):

```markdown
| Trigger Type | Condition | Confidence |
|--------------|-----------|------------|
| **Complexity Score** | Task complexity >0.6 with code modifications | 90% |
| **Multi-file Scope** | Estimated affected files >2 | 85% |
| **Security Domain** | Paths contain `auth/`, `security/`, `crypto/` | 95% |
| **Refactoring Scope** | Keywords: refactor, remediate, multi-file | 90% |
| **Test Remediation** | Keywords: fix tests, test failures | 88% |
```

**Keyword Triggers** (YAML block with confidence levels):

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

**Context Signals** (prose list):

```markdown
The command should be suggested when:
- User describes a multi-step implementation task
- Task involves code modifications with downstream impacts
- Security or data integrity domains are involved
- User explicitly requests compliance workflow
- Previous similar tasks benefited from structured execution
```

### Trigger Pattern Comparison

| Aspect | adversarial | spawn | task-unified |
|--------|-------------|-------|--------------|
| Auto-activation | No | Yes (implicit) | Yes (explicit with confidence) |
| Required input | Mode A / Mode B | Free-form task description | Operation + optional flags |
| Confidence scoring | N/A | N/A | 85-95% per trigger type |
| Keyword matching | N/A | Natural language | YAML-structured with tiers |
| Context signals | N/A | Natural language | Prose list |
| Invocation style | Always explicit | Always explicit | Explicit or auto-suggested |

---

## 4. Usage Section

### Pattern A: adversarial.md

Defines two distinct modes with detailed argument tables:

```bash
# Mode A: Compare existing files
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]

# Mode B: Generate variants from source + compare
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,...] [options]
```

Options table with 9 flags including short forms, required status, and defaults:

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

### Pattern B: spawn.md

Minimal usage with inline options:

```
/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

No separate options table. Strategy and depth are the only flags, documented inline.

### Pattern C: task-unified.md

Multi-table flag system organized by dimension:

```bash
/sc:task [operation] [target] [flags]
```

Four separate flag tables:
1. **Strategy Flags** (4 options: systematic, agile, enterprise, auto)
2. **Compliance Flags** (5 options: strict, standard, light, exempt, auto)
3. **Execution Control Flags** (5 options: skip-compliance, force-strict, parallel, delegate, reason)
4. **Verification Flags** (4 options: critical, standard, skip, auto)

This is the most flag-rich command in the framework, reflecting its role as the unified entry point for all task execution.

---

## 5. Behavioral Flow Definitions

### Pattern A: adversarial.md -- Behavioral Summary (Compact)

Uses a single prose paragraph instead of a numbered list:

```markdown
## Behavioral Summary

5-step adversarial protocol: Step 1 (diff analysis across variants), Step 2 (structured
adversarial debate with configurable depth), Step 3 (hybrid quantitative-qualitative scoring
and base selection), Step 4 (refactoring plan generation), Step 5 (merge execution with
provenance annotations). Produces 6 artifacts: diff-analysis.md, debate-transcript.md,
base-selection.md, refactor-plan.md, merge-log.md, and the merged output.
```

**Key characteristic**: Defines concrete output artifacts (6 named files). This is unique to adversarial -- the other commands don't enumerate specific output files.

### Pattern B: spawn.md -- Behavioral Flow (Numbered + Key Behaviors)

```markdown
## Behavioral Flow
1. **Analyze**: Parse complex operation requirements and assess scope across domains
2. **Decompose**: Break down operation into coordinated subtask hierarchies
3. **Orchestrate**: Execute tasks using optimal coordination strategy (parallel/sequential)
4. **Monitor**: Track progress across task hierarchies with dependency management
5. **Integrate**: Aggregate results and provide comprehensive orchestration summary

Key behaviors:
- Meta-system task decomposition with Epic -> Story -> Task -> Subtask breakdown
- Intelligent coordination strategy selection based on operation characteristics
- Cross-domain operation management with parallel and sequential execution patterns
- Advanced dependency analysis and resource optimization across task hierarchies
```

**Key characteristic**: The "Key behaviors" sub-section expands on the numbered flow with architectural patterns (Epic -> Story -> Task -> Subtask).

### Pattern C: task-unified.md -- Behavioral Flow (Numbered, 7 Steps)

```markdown
## Behavioral Flow

1. **Analyze**: Parse task requirements, detect keywords, estimate scope
2. **Classify**: Determine compliance tier using auto-detection algorithm
3. **Display**: Announce determined tier with confidence and rationale
4. **Delegate**: Route to appropriate MCP servers and activate relevant personas
5. **Execute**: Apply appropriate checklist based on tier
6. **Verify**: Validate completion using tier-appropriate verification
7. **Report**: Summarize enforcement outcomes and learnings
```

**Key characteristic**: Steps 2-3 (Classify/Display) are unique to task-unified and relate to its compliance tier system. Step 4 explicitly mentions MCP server routing and persona activation.

### Behavioral Flow Comparison

| Aspect | adversarial | spawn | task-unified |
|--------|-------------|-------|--------------|
| Format | Prose paragraph | Numbered list + bullets | Numbered list |
| Step count | 5 | 5 | 7 |
| Named outputs | 6 artifacts | Task hierarchy document | Reports + learnings |
| Classification step | No | No | Yes (tier detection) |
| User interaction | Optional (--interactive) | No | Display step shows rationale |
| Delegation | To merge-executor agent | To other /sc:* commands | To MCP servers + personas |

---

## 6. MCP Integration Sections

### Pattern A: adversarial.md -- No Explicit MCP Section

Adversarial declares MCP servers in frontmatter (`[sequential, context7, serena]`) but has **no dedicated MCP Integration section** in the body. Server usage is implied by the frontmatter and the framework-level COMMANDS.md reference:

From COMMANDS.md:
```
- **MCP**: Sequential (debate scoring/convergence), Serena (memory persistence), Context7 (domain validation)
```

### Pattern B: spawn.md -- MCP Integration (Minimal)

```markdown
## MCP Integration
- **Native Orchestration**: Meta-system command uses native coordination without MCP dependencies
- **Progressive Integration**: Coordination with systematic execution for progressive enhancement
- **Framework Integration**: Advanced integration with SuperClaude orchestration layers
```

Spawn explicitly states it uses **no MCP dependencies** (matching the empty `mcp-servers: []` in frontmatter). This section explains the design choice.

### Pattern C: task-unified.md -- MCP Integration (Comprehensive)

Two sub-sections:

**Server Selection Matrix** (table):

| Server | Always Active | Conditional Activation | Purpose |
|--------|---------------|----------------------|---------|
| Sequential | Yes | - | Reasoning, analysis, tier classification |
| Context7 | Yes | - | Patterns, best practices, documentation |
| Serena | Yes | - | Memory persistence, project context |
| Playwright | No | STRICT + (UI or E2E tasks) | Browser verification |
| Magic | No | --with-ui flag | UI component generation |
| Morphllm | No | --with-bulk-edit flag | Large-scale transformations |

**Persona Coordination** (YAML block):

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

**Key observation**: Task-unified is the only command that defines a full persona coordination matrix with domain-specific trigger conditions for persona activation.

---

## 7. Tool Coordination Sections

### Pattern A: adversarial.md -- No Explicit Tool Coordination Section

Tools are declared in COMMANDS.md but not in the command file itself:

From COMMANDS.md:
```
- **Tools**: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task]
- **Agents**: debate-orchestrator (coordinator), merge-executor (specialist), advocate agents (dynamic)
```

### Pattern B: spawn.md -- Tool Coordination (Bullet List)

```markdown
## Tool Coordination
- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic -> Story -> Task levels
- **Read/Grep/Glob**: System analysis and dependency mapping for complex operations
- **Edit/MultiEdit/Write**: Coordinated file operations with parallel and sequential execution
- **Bash**: System-level operations coordination with intelligent resource management
```

Format: Simple bullet list pairing tool names with their purpose within this command's context.

### Pattern C: task-unified.md -- Tool Coordination (Multi-Table)

**General tool table**:

| Tool | Purpose | Usage Pattern |
|------|---------|---------------|
| **TodoWrite** | Task tracking | Create at planning, update during execution |
| **Read** | File inspection | Pre-work analysis, context gathering |
| **Edit/Write** | Code modification | Execute planned changes |
| **Glob** | File discovery | Identify affected files for classification |
| **Grep** | Pattern search | Find references, dependencies |
| **Bash** | Command execution | Run tests, linters, build commands |
| **Task** | Sub-agent delegation | Spawn verification agents |

**Tier-Specific Tool Usage** (unique to task-unified):

| Tier | Required Tools | Optional Tools |
|------|----------------|----------------|
| **STRICT** | TodoWrite, Read, Edit, Bash, Task, Sequential, Serena | Playwright, Magic |
| **STANDARD** | TodoWrite, Read, Edit, Bash, Sequential | Context7, Serena |
| **LIGHT** | Read, Edit | TodoWrite, Bash |
| **EXEMPT** | Read | Any |

**Key observation**: Task-unified is the only command that defines required vs. optional tool sets per compliance tier. This creates a progressive tool requirement pyramid.

---

## 8. Key Patterns Sections

### Pattern A: adversarial.md -- No Key Patterns Section

Does not include a Key Patterns section.

### Pattern B: spawn.md -- Key Patterns (Bullet List)

```markdown
## Key Patterns
- **Hierarchical Breakdown**: Epic-level operations -> Story coordination -> Task execution -> Subtask granularity
- **Strategy Selection**: Sequential (dependency-ordered) -> Parallel (independent) -> Adaptive (dynamic)
- **Meta-System Coordination**: Cross-domain operations -> resource optimization -> result integration
- **Progressive Enhancement**: Systematic execution -> quality gates -> comprehensive validation
```

Format: Named patterns with arrow-chain descriptions showing flow direction.

### Pattern C: task-unified.md -- No Dedicated Key Patterns Section

Task-unified embeds its patterns within the Tiered Compliance Model and Auto-Detection Algorithm sections rather than a standalone Key Patterns section.

---

## 9. Boundary Definitions

All three commands define boundaries as Will/Will Not sections.

### Pattern A: adversarial.md

```markdown
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
```

Format: Two bullet lists with explanatory parentheticals.

### Pattern B: spawn.md

```markdown
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

**Key observation**: Spawn has a unique **CRITICAL BOUNDARIES** section that emphatically constrains the command to planning-only. It explicitly names its output format and specifies the next step. This pattern prevents scope creep in meta-orchestration commands.

### Pattern C: task-unified.md

Uses tables instead of bullet lists:

```markdown
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
```

**Key observation**: Task-unified adds an "Applicable Tiers" column to Will and a "Rationale" column to Will Not, tying boundaries to the compliance tier system. It also specifies concrete limits (max 15 changes per batch).

---

## 10. Domain-Specific Sections

These are sections unique to a command's problem domain that don't fit the universal template.

### adversarial.md -- Behavioral Summary with Artifact Enumeration

The Behavioral Summary names 6 specific output artifacts:
```
diff-analysis.md, debate-transcript.md, base-selection.md,
refactor-plan.md, merge-log.md, and the merged output
```

This is the only command that enumerates its output files.

### spawn.md -- CRITICAL BOUNDARIES + Output Specification

Spawn uniquely specifies its output format and delegation model:
```markdown
**Output**: Task breakdown document with:
- Epic decomposition
- Task hierarchy with dependencies
- Delegation assignments (which `/sc:*` command handles each task)
- Coordination strategy

**Next Step**: Execute individual tasks using delegated commands
```

### task-unified.md -- Multiple Domain-Specific Sections

1. **Tiered Compliance Model** (4 tiers, each with auto-triggers, SMART criteria, checklists)
2. **Auto-Detection Algorithm** (full YAML specification with keyword lists, path patterns, conflict resolution)
3. **Compound Phrase Handling** (YAML mapping phrases to tier overrides)
4. **Sub-Agent Delegation Matrix** (table mapping task types to primary + verification agents)
5. **Escape Hatches** (override mechanisms with usage guidance)
6. **Success Metrics** (target percentages for classification accuracy, overhead, etc.)
7. **Migration from Legacy Commands** (version migration guidance)
8. **Version History**

---

## 11. How Commands Reference Skills, Agents, and MCP Servers

### MCP Server References

**In frontmatter** (declarative):
```yaml
mcp-servers: [sequential, context7, serena]
```

**In MCP Integration section** (behavioral):
```markdown
| Server | Always Active | Conditional Activation | Purpose |
```

**In Tool Coordination** (operational):
```markdown
| **STRICT** | TodoWrite, Read, Edit, Bash, Task, Sequential, Serena | Playwright, Magic |
```

### Agent References

**In frontmatter** (only adversarial references agents indirectly via personas):
```yaml
personas: [architect, analyzer, scribe]
```

**In COMMANDS.md** (external reference):
```markdown
- **Agents**: debate-orchestrator (coordinator), merge-executor (specialist), advocate agents (dynamic)
```

**In task-unified Sub-Agent Delegation Matrix**:
```markdown
| Python code fixes | python-expert | quality-engineer |
```

### Persona References

**In frontmatter**:
```yaml
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
```

**In persona coordination YAML**:
```yaml
persona_matrix:
  core: [architect, analyzer, qa, refactorer]
  domain:
    backend:
      personas: [python-expert, backend-architect]
      triggers: [".py files", "api/", "services/"]
```

### Skill References

None of the three command files directly reference skills or `SKILL.md` files. The connection between commands and skills is made through:
1. The `COMMANDS.md` framework file (which lists agents and tools per command)
2. The persona system (personas activate skills implicitly)
3. The skill installation system (`superclaude install` places skills in `.claude/skills/`)

Commands and skills are loosely coupled -- a command declares what personas and MCP servers it needs, and the framework routes to the appropriate skill packages at runtime.

---

## 12. Related Commands / Cross-Command Integration

### adversarial.md -- Related Commands Table

```markdown
| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:roadmap` | Multi-spec/multi-roadmap modes | `/sc:roadmap --specs spec1.md,spec2.md` |
| `/sc:design` | Compare architectural designs | `/sc:adversarial --compare design-a.md,design-b.md` |
| `/sc:spec-panel` | Augment panel with adversarial review | Invoke adversarial post-panel |
| `/sc:improve` | Compare improvement approaches | Generate competing plans, merge best |
```

### spawn.md -- Delegation References

```markdown
**Next Step**: Execute individual tasks using delegated commands (`/sc:implement`, `/sc:design`, `/sc:test`, etc.)
```

### task-unified.md -- Migration References

```markdown
## Migration from Legacy Commands
### From `/sc:task` (v1.x)
### From `/sc:task-mcp`
```

---

## 13. Examples Section Patterns

All three commands provide examples in fenced code blocks.

### adversarial.md (5 examples, most detailed)

Each example has a descriptive heading and shows a complete CLI invocation:
```bash
# Mode A: Compare existing files
/sc:adversarial --compare draft-a.md,draft-b.md --depth standard

# Mode B: Generate variants
/sc:adversarial --source auth-spec.md --generate roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer \
  --depth deep --convergence 0.85
```

### spawn.md (3 examples with comments)

Each example includes inline comments explaining the breakdown strategy:
```
/sc:spawn "implement user authentication system"
# Breakdown: Database design -> Backend API -> Frontend UI -> Testing
# Coordinates across multiple domains with dependency management
```

### task-unified.md (7 examples including overrides)

Examples demonstrate the full flag system including escape hatches:
```bash
/sc:task "implement user authentication system" --strategy systematic --compliance strict
# Auto-detects: STRICT (authentication keyword, multi-file expected)
# Activates: architect, security, backend personas
# Enforces: Full checklist, verification agent, adversarial review

/sc:task "experimental change" --skip-compliance
# Skips all compliance enforcement (escape hatch)
```

---

## 14. Summary: Three Command Archetypes

### Archetype 1: Analysis Pipeline (adversarial.md)

- **Purpose**: Process artifacts through a structured multi-step pipeline
- **Frontmatter**: Targeted MCP servers and personas
- **Triggers**: Required input modes, never auto-activated
- **Flow**: Linear pipeline producing named artifacts
- **Boundaries**: Clear input/output contract, no execution
- **Distinctive features**: Behavioral Summary paragraph, artifact enumeration, Mode A/B input patterns, agent specification format (`model[:persona[:"instruction"]]`)

### Archetype 2: Meta-Orchestrator (spawn.md)

- **Purpose**: Decompose complex tasks and delegate to other commands
- **Frontmatter**: Empty MCP and persona arrays (pure orchestrator)
- **Triggers**: Natural language conditions
- **Flow**: Analyze -> Decompose -> Orchestrate -> Monitor -> Integrate
- **Boundaries**: CRITICAL BOUNDARIES section, planning-only, explicit "will not execute"
- **Distinctive features**: Key Patterns section, hierarchical breakdown model (Epic -> Story -> Task -> Subtask), delegation assignments to other `/sc:*` commands

### Archetype 3: Unified Executor (task-unified.md)

- **Purpose**: Single entry point for all task execution with compliance enforcement
- **Frontmatter**: Maximum MCP servers and personas, version field
- **Triggers**: Multi-level (auto-activation + keywords + context signals) with confidence scores
- **Flow**: 7-step including classification, display, and reporting
- **Boundaries**: Tabular with tier applicability and rationale columns
- **Distinctive features**: Tiered compliance model (4 tiers with SMART criteria and checklists), auto-detection algorithm (full YAML spec), compound phrase handling, sub-agent delegation matrix, escape hatches, success metrics, migration guidance, version history

---

## 15. Command File Checklist for New Commands

Based on the patterns above, a new SuperClaude command file should include:

```markdown
---
name: <command-name>
description: "<one-line purpose>"
category: <analysis|special|development|quality|meta>
complexity: <simple|moderate|high|advanced>
mcp-servers: [<server-list or empty>]
personas: [<persona-list or empty>]
---

# /sc:<command-name> - <Title>

## Triggers (or Required Input)
[When this command activates or what input it requires]

## Usage
[CLI syntax with flag tables]

## Behavioral Flow
[Numbered steps describing execution sequence]

## MCP Integration
[Server usage details, or explicit statement of no MCP dependency]

## Tool Coordination
[Tool-to-purpose mappings, optionally tier-specific]

## Key Patterns (optional)
[Named architectural patterns used by this command]

## Examples
[3-7 examples showing different usage scenarios]

## Boundaries
**Will:** [capabilities]
**Will Not:** [restrictions with rationale]

## Related Commands (optional)
[Cross-command integration table]
```
