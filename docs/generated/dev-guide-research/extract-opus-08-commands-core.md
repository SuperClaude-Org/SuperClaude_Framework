# Extraction: COMMANDS.md - Command Execution Framework

**Source file**: `/config/workspace/SuperClaude_Framework/src/superclaude/core/COMMANDS.md`
**Extracted**: 2026-02-21
**Purpose**: Complete extraction of all information relevant to developing custom commands, skills, or agents for the SuperClaude framework.

---

## 1. Command Structure and Metadata Fields

Every command in the SuperClaude framework is defined by five metadata fields:

> "Each command specifies: `command`, `category`, `purpose`, `wave-enabled` (true|false), `performance-profile` (optimization|standard|complex)."

### Metadata Field Definitions

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `command` | string | The slash command name (e.g., `/build`, `/analyze`) | Identifier used to invoke the command |
| `category` | string | One of 8 categories (see Section 6) | Grouping for routing and orchestration |
| `purpose` | string | Free-text description | What the command does |
| `wave-enabled` | boolean | `true` or `false` | Whether the command supports multi-stage wave execution |
| `performance-profile` | enum | `optimization`, `standard`, or `complex` | Resource allocation and execution strategy |

### Per-Command Specification Pattern

Each command definition in the file follows a consistent structure with optional sub-fields:

- **Signature**: Command name with argument pattern and parenthetical noting wave-enabled status and performance profile
- **Auto-Persona**: Which personas auto-activate when this command runs
- **MCP**: Which MCP servers are used, with role annotations in parentheses
- **Tools**: Array of Claude Code tools the command may use
- **Subagents** (optional): Named sub-agents with model annotations (e.g., Haiku, Sonnet)

Example from source:

```
**`/build $ARGUMENTS`** — Project builder with framework detection (wave-enabled, optimization profile)
- **Auto-Persona**: Frontend, Backend, Architect, Scribe
- **MCP**: Magic (UI), Context7 (patterns), Sequential (logic)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit]
```

---

## 2. Command Processing Pipeline

The file defines a 5-step processing pipeline that all commands follow:

> ```
> 1. **Input Parsing**: `$ARGUMENTS` with `@<path>`, `!<command>`, `--<flags>`
> 2. **Context Resolution**: Auto-persona activation and MCP server selection
> 3. **Wave Eligibility**: Complexity assessment and wave mode determination
> 4. **Execution Strategy**: Tool orchestration and resource allocation
> 5. **Quality Gates**: Validation checkpoints and error handling
> ```

### Input Parsing Syntax

Commands accept three input modifiers:
- `@<path>` -- file or directory path references
- `!<command>` -- sub-command invocations
- `--<flags>` -- behavioral flags (see Section 7)

### Integration Layers

The pipeline connects to four integration layers:

> ```
> - **Claude Code**: Native slash command compatibility
> - **Persona System**: Auto-activation based on command context
> - **MCP Servers**: Context7, Sequential, Magic, Playwright integration
> - **Wave System**: Multi-stage orchestration for complex operations
> ```

---

## 3. Wave System Integration

### Activation Criteria

> "**Wave Orchestration Engine**: Multi-stage command execution with compound intelligence. Auto-activates on complexity >=0.7 + files >20 + operation_types >2."

### Wave-Enabled Command Tiers

Commands are divided into two tiers of wave eligibility:

> ```
> **Wave-Enabled Commands**:
> - **Tier 1**: `/analyze`, `/build`, `/implement`, `/improve`
> - **Tier 2**: `/design`, `/task`
> ```

A later section lists 7 total wave-enabled commands:

> "7 commands: `/analyze`, `/build`, `/design`, `/implement`, `/improve`, `/task`, `/workflow`"

### Wave-Enabled Status Per Command

| Command | Wave-Enabled | Performance Profile |
|---------|-------------|-------------------|
| `/build` | Yes | optimization |
| `/implement` | Yes | standard |
| `/analyze` | Yes | complex |
| `/improve` | Yes | optimization |
| `/cleanup-audit` | Yes | complex |
| `/sc:task` | Yes | adaptive |
| `/design` | Yes | (not explicitly stated) |
| `/task` | Yes | (not explicitly stated) |
| `/troubleshoot` | No | (not explicitly stated) |
| `/explain` | No | (not explicitly stated) |
| `/cleanup` | No | (not explicitly stated) |
| `/document` | No | (not explicitly stated) |
| `/estimate` | No | (not explicitly stated) |
| `/test` | No | (not explicitly stated) |
| `/git` | No | (not explicitly stated) |
| `/index` | No | (not explicitly stated) |
| `/load` | No | (not explicitly stated) |
| `/spawn` | No | (not explicitly stated) |

---

## 4. Performance Profiles

Three profiles control resource allocation and execution behavior:

> ```
> ### Performance Profiles
> - **optimization**: High-performance with caching and parallel execution
> - **standard**: Balanced performance with moderate resource usage
> - **complex**: Resource-intensive with comprehensive analysis
> ```

### Profile-to-Command Mapping (explicitly stated in source)

| Profile | Commands |
|---------|----------|
| `optimization` | `/build`, `/improve` |
| `standard` | `/implement` |
| `complex` | `/analyze`, `/cleanup-audit` |
| `adaptive` | `/sc:task` |

---

## 5. Complete Command Catalog

### Development Commands

**`/build $ARGUMENTS`**
> "Project builder with framework detection (wave-enabled, optimization profile)"
- Auto-Persona: Frontend, Backend, Architect, Scribe
- MCP: Magic (UI), Context7 (patterns), Sequential (logic)
- Tools: [Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit]

**`/implement $ARGUMENTS`**
> "Feature implementation with intelligent persona activation (wave-enabled, standard profile)"
- Auto-Persona: Frontend, Backend, Architect, Security (context-dependent)
- MCP: Magic (UI), Context7 (patterns), Sequential (complex logic)
- Tools: [Read, Write, Edit, MultiEdit, Bash, Glob, TodoWrite, Task]

### Analysis Commands

**`/analyze $ARGUMENTS`**
> "Multi-dimensional code and system analysis (wave-enabled, complex profile)"
- Auto-Persona: Analyzer, Architect, Security
- MCP: Sequential (primary), Context7 (patterns), Magic (UI analysis)
- Tools: [Read, Grep, Glob, Bash, TodoWrite]

**`/troubleshoot [symptoms] [flags]`**
> "Problem investigation"
- Auto-Persona: Analyzer, QA
- MCP: Sequential, Playwright

**`/explain [topic] [flags]`**
> "Educational explanations"
- Auto-Persona: Mentor, Scribe
- MCP: Context7, Sequential

### Quality Commands

**`/improve [target] [flags]`**
> "Evidence-based code enhancement (wave-enabled, optimization profile)"
- Auto-Persona: Refactorer, Performance, Architect, QA
- MCP: Sequential (logic), Context7 (patterns), Magic (UI)
- Tools: [Read, Grep, Glob, Edit, MultiEdit, Bash]

**`/cleanup [target] [flags]`**
> "Project cleanup and technical debt reduction"
- Auto-Persona: Refactorer
- MCP: Sequential

**`/cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`**
> "Multi-pass read-only repository audit (wave-enabled, complex profile)"
- Auto-Persona: Analyzer, Architect, DevOps, QA, Refactorer
- MCP: Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns)
- Tools: [Read, Grep, Glob, Bash(git/wc/find/du), TodoWrite, Task, Write]
- Subagents: audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet)

**`/sc:adversarial [--compare files|--source file --generate type --agents specs] [--depth quick|standard|deep] [--convergence N] [--interactive] [--focus areas]`**
> "Structured adversarial debate, comparison, and merge pipeline (wave-enabled, complex profile)"
- Auto-Persona: Architect, Analyzer, Scribe
- MCP: Sequential (debate scoring/convergence), Serena (memory persistence), Context7 (domain validation)
- Tools: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task]
- Agents: debate-orchestrator (coordinator), merge-executor (specialist), advocate agents (dynamic)

### Additional Commands

**`/document [target] [flags]`**
> "Documentation generation"
- Auto-Persona: Scribe, Mentor
- MCP: Context7, Sequential

**`/estimate [target] [flags]`**
> "Evidence-based estimation"
- Auto-Persona: Analyzer, Architect
- MCP: Sequential, Context7

**`/task [operation] [flags]`**
> "Long-term project management"
- Auto-Persona: Architect, Analyzer
- MCP: Sequential

**`/test [type] [flags]`**
> "Testing workflows"
- Auto-Persona: QA
- MCP: Playwright, Sequential

**`/git [operation] [flags]`**
> "Git workflow assistant"
- Auto-Persona: DevOps, Scribe, QA
- MCP: Sequential

**`/design [domain] [flags]`**
> "Design orchestration"
- Auto-Persona: Architect, Frontend
- MCP: Magic, Sequential, Context7

### Meta & Orchestration Commands

**`/index [query] [flags]`**
> "Command catalog browsing"
- Auto-Persona: Mentor, Analyzer
- MCP: Sequential

**`/load [path] [flags]`**
> "Project context loading"
- Auto-Persona: Analyzer, Architect, Scribe
- MCP: All servers

**`/spawn [mode] [flags]`**
> "Task orchestration"
- Auto-Persona: Analyzer, Architect, DevOps
- MCP: All servers

**Iterative Operations**:
> "Use `--loop` flag with improvement commands for iterative refinement"

---

## 6. Command Categories

Eight categories organize all commands:

> ```
> ### Command Categories
> - **Development**: build, implement, design
> - **Planning**: workflow, estimate, task
> - **Analysis**: analyze, troubleshoot, explain
> - **Quality**: improve, cleanup
> - **Testing**: test
> - **Documentation**: document
> - **Version-Control**: git
> - **Meta**: index, load, spawn
> ```

---

## 7. Flag Systems for Commands

### Unified Task Command (`/sc:task`) Flag System

The `/sc:task` command has the most elaborate flag system, organized into four dimensions:

#### Strategy Flags (Orchestration Dimension)

> | Flag | Description | Use Case |
> |------|-------------|----------|
> | `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
> | `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
> | `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
> | `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

#### Compliance Flags (Quality Dimension)

> | Flag | Description | Use Case |
> |------|-------------|----------|
> | `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
> | `--compliance standard` | Core rules enforcement | Single-file code changes |
> | `--compliance light` | Awareness only | Minor fixes, formatting |
> | `--compliance exempt` | No enforcement | Questions, exploration, docs |
> | `--compliance auto` | Auto-detect based on task (default) | Most tasks |

#### Verification Flags

> | Flag | Description |
> |------|-------------|
> | `--verify critical` | Full sub-agent verification |
> | `--verify standard` | Direct test execution only |
> | `--verify skip` | Skip verification (use with caution) |
> | `--verify auto` | Auto-select based on compliance tier (default) |

#### Execution Control Flags

> | Flag | Description |
> |------|-------------|
> | `--skip-compliance` | Escape hatch - skip all compliance enforcement |
> | `--force-strict` | Override auto-detection to STRICT |
> | `--parallel` | Enable parallel sub-agent execution |
> | `--delegate` | Enable sub-agent delegation |
> | `--reason "..."` | Required justification for tier override |

### Tier Classification Flow

The compliance tier is determined through a 6-step process:

> ```
> 1. Check for user override (`--compliance`)
> 2. Detect compound phrases (highest priority)
> 3. Score keywords by tier (STRICT > EXEMPT > LIGHT > STANDARD)
> 4. Apply context boosters (file count, security paths)
> 5. Resolve conflicts using priority ordering
> 6. Display confidence and allow user override if <70%
> ```

### Auto-Activation Triggers

> | Trigger | Condition | Suggested Tier |
> |---------|-----------|----------------|
> | Complexity score | >=0.7 | STRICT |
> | Multi-file scope | >3 files | STANDARD minimum |
> | Security domain | auth/, security/, crypto/ paths | STRICT |
> | Documentation-only | *.md, docs/ | EXEMPT |
> | Single trivial change | typo, comment | LIGHT |

### Command-Specific Flags (from `/cleanup-audit`)

- `--pass surface|structural|cross-cutting|all` -- Select audit pass type
- `--batch-size N` -- Control batch processing size
- `--focus infrastructure|frontend|backend|all` -- Target specific domain

### Command-Specific Flags (from `/sc:adversarial`)

- `--compare files` -- Compare multiple file variants
- `--source file --generate type --agents specs` -- Generate with agent specifications
- `--depth quick|standard|deep` -- Analysis depth control
- `--convergence N` -- Set convergence threshold
- `--interactive` -- Enable interactive mode
- `--focus areas` -- Target specific focus areas

---

## 8. Command-to-Persona Connections

### Complete Persona Activation Map

| Command | Auto-Activated Personas |
|---------|------------------------|
| `/build` | Frontend, Backend, Architect, Scribe |
| `/implement` | Frontend, Backend, Architect, Security (context-dependent) |
| `/analyze` | Analyzer, Architect, Security |
| `/troubleshoot` | Analyzer, QA |
| `/explain` | Mentor, Scribe |
| `/improve` | Refactorer, Performance, Architect, QA |
| `/cleanup` | Refactorer |
| `/cleanup-audit` | Analyzer, Architect, DevOps, QA, Refactorer |
| `/sc:adversarial` | Architect, Analyzer, Scribe |
| `/document` | Scribe, Mentor |
| `/estimate` | Analyzer, Architect |
| `/task` | Architect, Analyzer |
| `/sc:task` | Domain-specific (Security, Frontend, etc.) |
| `/test` | QA |
| `/git` | DevOps, Scribe, QA |
| `/design` | Architect, Frontend |
| `/index` | Mentor, Analyzer |
| `/load` | Analyzer, Architect, Scribe |
| `/spawn` | Analyzer, Architect, DevOps |

---

## 9. Command-to-MCP Server Connections

### Complete MCP Server Map

| Command | MCP Servers (with roles) |
|---------|--------------------------|
| `/build` | Magic (UI), Context7 (patterns), Sequential (logic) |
| `/implement` | Magic (UI), Context7 (patterns), Sequential (complex logic) |
| `/analyze` | Sequential (primary), Context7 (patterns), Magic (UI analysis) |
| `/troubleshoot` | Sequential, Playwright |
| `/explain` | Context7, Sequential |
| `/improve` | Sequential (logic), Context7 (patterns), Magic (UI) |
| `/cleanup` | Sequential |
| `/cleanup-audit` | Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns) |
| `/sc:adversarial` | Sequential (debate scoring/convergence), Serena (memory persistence), Context7 (domain validation) |
| `/document` | Context7, Sequential |
| `/estimate` | Sequential, Context7 |
| `/task` | Sequential |
| `/sc:task` | Sequential (analysis), Serena (context), Context7 (patterns) |
| `/test` | Playwright, Sequential |
| `/git` | Sequential |
| `/design` | Magic, Sequential, Context7 |
| `/index` | Sequential |
| `/load` | All servers |
| `/spawn` | All servers |

---

## 10. Tool Usage Per Command

### Complete Tool Map

| Command | Tools |
|---------|-------|
| `/build` | Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit |
| `/implement` | Read, Write, Edit, MultiEdit, Bash, Glob, TodoWrite, Task |
| `/analyze` | Read, Grep, Glob, Bash, TodoWrite |
| `/improve` | Read, Grep, Glob, Edit, MultiEdit, Bash |
| `/cleanup-audit` | Read, Grep, Glob, Bash(git/wc/find/du), TodoWrite, Task, Write |
| `/sc:adversarial` | Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task |
| `/sc:task` | TodoWrite, Read, Grep, Glob, Edit, MultiEdit, Task, Bash |

Note: Not all commands have their tool arrays explicitly listed. Only the commands shown above include explicit tool specifications in the source file.

---

## 11. Subagent Definitions

Two commands define named subagents:

### `/cleanup-audit` Subagents

> "**Subagents**: audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet)"

| Subagent | Model |
|----------|-------|
| audit-scanner | Haiku |
| audit-analyzer | Sonnet |
| audit-comparator | Sonnet |
| audit-consolidator | Sonnet |
| audit-validator | Sonnet |

### `/sc:adversarial` Agents

> "**Agents**: debate-orchestrator (coordinator), merge-executor (specialist), advocate agents (dynamic)"

| Agent | Role |
|-------|------|
| debate-orchestrator | coordinator |
| merge-executor | specialist |
| advocate agents | dynamic |

---

## 12. Key Observations for Custom Command Development

1. **Every command must specify 5 metadata fields**: command name, category, purpose, wave-enabled boolean, and performance-profile enum.

2. **Commands connect to the system through 4 integration layers**: Claude Code native compatibility, Persona auto-activation, MCP server selection, and Wave system orchestration.

3. **The processing pipeline is fixed at 5 steps**: Input Parsing, Context Resolution, Wave Eligibility, Execution Strategy, Quality Gates. Custom commands follow this same pipeline.

4. **Wave enablement is opt-in**: Only 7 commands are wave-enabled. The auto-activation threshold is complexity >= 0.7 + files > 20 + operation_types > 2.

5. **Performance profiles determine resource behavior**: `optimization` enables caching and parallelism, `standard` is balanced, `complex` is resource-intensive. The special `adaptive` profile is used by `/sc:task`.

6. **Persona auto-activation is per-command**: Each command declares which personas it activates. Commands like `/sc:task` use dynamic domain-specific activation.

7. **MCP server assignments include role annotations**: Servers are not just listed but annotated with their purpose for each command (e.g., "Sequential (primary)" vs. "Sequential (logic)").

8. **Flag systems are extensible**: The `/sc:task` command demonstrates the most complex flag system with strategy, compliance, verification, and execution control dimensions. Custom commands can define their own flag signatures.

9. **Subagents can be declared per-command**: Commands like `/cleanup-audit` and `/sc:adversarial` define named subagents with model-tier annotations.

10. **Categories are the organizational unit**: The 8 categories (Development, Planning, Analysis, Quality, Testing, Documentation, Version-Control, Meta) determine how commands are routed and discovered.
