# COMMANDS.md - SuperClaude Command Execution Framework

Command execution framework for Claude Code SuperClaude integration.

## Command System Architecture

### Core Command Structure
Each command specifies: `command`, `category`, `purpose`, `wave-enabled` (true|false), `performance-profile` (optimization|standard|complex).

### Command Processing Pipeline
1. **Input Parsing**: `$ARGUMENTS` with `@<path>`, `!<command>`, `--<flags>`
2. **Context Resolution**: Auto-persona activation and MCP server selection
3. **Wave Eligibility**: Complexity assessment and wave mode determination
4. **Execution Strategy**: Tool orchestration and resource allocation
5. **Quality Gates**: Validation checkpoints and error handling

### Integration Layers
- **Claude Code**: Native slash command compatibility
- **Persona System**: Auto-activation based on command context
- **MCP Servers**: Context7, Sequential, Magic, Playwright integration
- **Wave System**: Multi-stage orchestration for complex operations

## Wave System Integration

**Wave Orchestration Engine**: Multi-stage command execution with compound intelligence. Auto-activates on complexity ≥0.7 + files >20 + operation_types >2.

**Wave-Enabled Commands**:
- **Tier 1**: `/analyze`, `/build`, `/implement`, `/improve`
- **Tier 2**: `/design`, `/task`

### Development Commands

**`/build $ARGUMENTS`** — Project builder with framework detection (wave-enabled, optimization profile)
- **Auto-Persona**: Frontend, Backend, Architect, Scribe
- **MCP**: Magic (UI), Context7 (patterns), Sequential (logic)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit]

**`/implement $ARGUMENTS`** — Feature implementation with intelligent persona activation (wave-enabled, standard profile)
- **Auto-Persona**: Frontend, Backend, Architect, Security (context-dependent)
- **MCP**: Magic (UI), Context7 (patterns), Sequential (complex logic)
- **Tools**: [Read, Write, Edit, MultiEdit, Bash, Glob, TodoWrite, Task]

### Analysis Commands

**`/analyze $ARGUMENTS`** — Multi-dimensional code and system analysis (wave-enabled, complex profile)
- **Auto-Persona**: Analyzer, Architect, Security
- **MCP**: Sequential (primary), Context7 (patterns), Magic (UI analysis)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite]

**`/troubleshoot [symptoms] [flags]`** - Problem investigation | Auto-Persona: Analyzer, QA | MCP: Sequential, Playwright

**`/explain [topic] [flags]`** - Educational explanations | Auto-Persona: Mentor, Scribe | MCP: Context7, Sequential


### Quality Commands

**`/improve [target] [flags]`** — Evidence-based code enhancement (wave-enabled, optimization profile)
- **Auto-Persona**: Refactorer, Performance, Architect, QA
- **MCP**: Sequential (logic), Context7 (patterns), Magic (UI)
- **Tools**: [Read, Grep, Glob, Edit, MultiEdit, Bash]


**`/cleanup [target] [flags]`** - Project cleanup and technical debt reduction | Auto-Persona: Refactorer | MCP: Sequential

### Additional Commands

**`/document [target] [flags]`** - Documentation generation | Auto-Persona: Scribe, Mentor | MCP: Context7, Sequential

**`/estimate [target] [flags]`** - Evidence-based estimation | Auto-Persona: Analyzer, Architect | MCP: Sequential, Context7

**`/task [operation] [flags]`** - Long-term project management | Auto-Persona: Architect, Analyzer | MCP: Sequential

### Unified Task Command (Compliance-Enforced)

**`/sc:task [description] [flags]`** — Unified task execution with tiered compliance (wave-enabled, adaptive profile)
- **Auto-Persona**: Domain-specific (Security → security, Frontend → frontend, etc.)
- **MCP**: Sequential (analysis), Serena (context), Context7 (patterns)
- **Tools**: [TodoWrite, Read, Grep, Glob, Edit, MultiEdit, Task, Bash]

#### Strategy Flags (Orchestration Dimension)
| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

#### Compliance Flags (Quality Dimension)
| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) | Most tasks |

#### Verification Flags
| Flag | Description |
|------|-------------|
| `--verify critical` | Full sub-agent verification |
| `--verify standard` | Direct test execution only |
| `--verify skip` | Skip verification (use with caution) |
| `--verify auto` | Auto-select based on compliance tier (default) |

#### Execution Control Flags
| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--reason "..."` | Required justification for tier override |

#### Tier Classification Flow
1. Check for user override (`--compliance`)
2. Detect compound phrases (highest priority)
3. Score keywords by tier (STRICT > EXEMPT > LIGHT > STANDARD)
4. Apply context boosters (file count, security paths)
5. Resolve conflicts using priority ordering
6. Display confidence and allow user override if <70%

#### Auto-Activation Triggers
| Trigger | Condition | Suggested Tier |
|---------|-----------|----------------|
| Complexity score | ≥0.7 | STRICT |
| Multi-file scope | >3 files | STANDARD minimum |
| Security domain | auth/, security/, crypto/ paths | STRICT |
| Documentation-only | *.md, docs/ | EXEMPT |
| Single trivial change | typo, comment | LIGHT |

**`/test [type] [flags]`** - Testing workflows | Auto-Persona: QA | MCP: Playwright, Sequential

**`/git [operation] [flags]`** - Git workflow assistant | Auto-Persona: DevOps, Scribe, QA | MCP: Sequential

**`/design [domain] [flags]`** - Design orchestration | Auto-Persona: Architect, Frontend | MCP: Magic, Sequential, Context7

### Meta & Orchestration Commands

**`/index [query] [flags]`** - Command catalog browsing | Auto-Persona: Mentor, Analyzer | MCP: Sequential

**`/load [path] [flags]`** - Project context loading | Auto-Persona: Analyzer, Architect, Scribe | MCP: All servers

**Iterative Operations** - Use `--loop` flag with improvement commands for iterative refinement

**`/spawn [mode] [flags]`** - Task orchestration | Auto-Persona: Analyzer, Architect, DevOps | MCP: All servers

## Command Execution Matrix

### Performance Profiles
- **optimization**: High-performance with caching and parallel execution
- **standard**: Balanced performance with moderate resource usage
- **complex**: Resource-intensive with comprehensive analysis

### Command Categories
- **Development**: build, implement, design
- **Planning**: workflow, estimate, task
- **Analysis**: analyze, troubleshoot, explain
- **Quality**: improve, cleanup
- **Testing**: test
- **Documentation**: document
- **Version-Control**: git
- **Meta**: index, load, spawn

### Wave-Enabled Commands
7 commands: `/analyze`, `/build`, `/design`, `/implement`, `/improve`, `/task`, `/workflow`

