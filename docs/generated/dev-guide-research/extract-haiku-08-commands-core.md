# Source: /config/workspace/SuperClaude_Framework/src/superclaude/core/COMMANDS.md

This document extracts **all information pertaining to developing custom commands, skills, or agents** for the SuperClaude framework.

---

## Command system architecture (how commands are defined)

### Core command structure

Exact quote:

> "Each command specifies: `command`, `category`, `purpose`, `wave-enabled` (true|false), `performance-profile` (optimization|standard|complex)."

Implications for custom command development:
- A custom command definition should include:
  - `command`
  - `category`
  - `purpose`
  - `wave-enabled` (boolean)
  - `performance-profile` (one of: `optimization`, `standard`, `complex`)

---

## Command processing pipeline (how commands are executed)

Exact quotes:

> "1. **Input Parsing**: `$ARGUMENTS` with `@<path>`, `!<command>`, `--<flags>`"
>
> "2. **Context Resolution**: Auto-persona activation and MCP server selection"
>
> "3. **Wave Eligibility**: Complexity assessment and wave mode determination"
>
> "4. **Execution Strategy**: Tool orchestration and resource allocation"
>
> "5. **Quality Gates**: Validation checkpoints and error handling"

Implications for custom command development:
- Your command should be designed to accept argument patterns compatible with the system:
  - `$ARGUMENTS`
  - `@<path>` (path-style inputs)
  - `!<command>` (command-style inputs)
  - `--<flags>` (behavior/feature toggles)
- Commands participate in a standardized execution lifecycle:
  - persona selection + MCP server selection can be automatic based on context
  - wave-mode may apply depending on complexity
  - execution should be tool-orchestrated and quality-gated

---

## Integration layers (what systems custom commands interact with)

Exact quotes:

> "- **Claude Code**: Native slash command compatibility"
>
> "- **Persona System**: Auto-activation based on command context"
>
> "- **MCP Servers**: Context7, Sequential, Magic, Playwright integration"
>
> "- **Wave System**: Multi-stage orchestration for complex operations"

Implications for custom commands/agents/skills:
- Custom commands should be compatible with Claude Code slash-command semantics.
- Commands can rely on:
  - persona auto-activation
  - MCP servers (Context7/Sequential/Magic/Playwright)
  - wave orchestration for larger tasks

---

## Wave system integration (when complex multi-stage execution triggers)

### Wave Orchestration Engine (auto-activation conditions)

Exact quote:

> "**Wave Orchestration Engine**: Multi-stage command execution with compound intelligence. Auto-activates on complexity ≥0.7 + files >20 + operation_types >2."

Implications for custom command development:
- If your command can operate over many files/operations, it should be designed to support wave-style execution.
- Wave activation is driven by:
  - complexity ≥ 0.7
  - files > 20
  - operation_types > 2

### Wave-enabled command tiers

Exact quotes:

> "**Wave-Enabled Commands**:"
>
> "- **Tier 1**: `/analyze`, `/build`, `/implement`, `/improve`"
>
> "- **Tier 2**: `/design`, `/task`"

---

## Development commands (relevant patterns for building commands/skills/agents)

This section lists command behaviors including default personas, MCP servers, and tools. These are concrete reference patterns for implementing or extending command workflows.

### `/build $ARGUMENTS`

Exact quote:

> "**`/build $ARGUMENTS`** — Project builder with framework detection (wave-enabled, optimization profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Frontend, Backend, Architect, Scribe"
>
> "- **MCP**: Magic (UI), Context7 (patterns), Sequential (logic)"
>
> "- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit]"

Implications for custom commands:
- A custom development command can specify:
  - an auto-persona set
  - which MCP servers are expected
  - an allowed/expected tool set
  - whether it is wave-enabled and its performance profile

### `/implement $ARGUMENTS`

Exact quote:

> "**`/implement $ARGUMENTS`** — Feature implementation with intelligent persona activation (wave-enabled, standard profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Frontend, Backend, Architect, Security (context-dependent)"
>
> "- **MCP**: Magic (UI), Context7 (patterns), Sequential (complex logic)"
>
> "- **Tools**: [Read, Write, Edit, MultiEdit, Bash, Glob, TodoWrite, Task]"

Implications for custom commands:
- Implementation-oriented commands may:
  - use `Write` and `Edit` tooling
  - include `Task` for sub-agent or multi-step orchestration
  - expand persona activation based on context (including Security)

---

## Analysis & explanation commands (useful for agent/skill workflows)

### `/analyze $ARGUMENTS`

Exact quote:

> "**`/analyze $ARGUMENTS`** — Multi-dimensional code and system analysis (wave-enabled, complex profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Analyzer, Architect, Security"
>
> "- **MCP**: Sequential (primary), Context7 (patterns), Magic (UI analysis)"
>
> "- **Tools**: [Read, Grep, Glob, Bash, TodoWrite]"

### `/troubleshoot [symptoms] [flags]`

Exact quote:

> "**`/troubleshoot [symptoms] [flags]`** - Problem investigation | Auto-Persona: Analyzer, QA | MCP: Sequential, Playwright"

### `/explain [topic] [flags]`

Exact quote:

> "**`/explain [topic] [flags]`** - Educational explanations | Auto-Persona: Mentor, Scribe | MCP: Context7, Sequential"

Implications for custom agents/skills:
- Troubleshooting and explanation flows are explicitly tied to personas and MCP servers.
- If creating agents/skills that support these flows, they should align with:
  - `Analyzer` + `QA` + `Sequential/Playwright` for troubleshooting
  - `Mentor` + `Scribe` + `Context7/Sequential` for explanations

---

## Quality commands (patterns for refactoring/cleanup workflows)

### `/improve [target] [flags]`

Exact quote:

> "**`/improve [target] [flags]`** — Evidence-based code enhancement (wave-enabled, optimization profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Refactorer, Performance, Architect, QA"
>
> "- **MCP**: Sequential (logic), Context7 (patterns), Magic (UI)"
>
> "- **Tools**: [Read, Grep, Glob, Edit, MultiEdit, Bash]"

### `/cleanup [target] [flags]`

Exact quote:

> "**`/cleanup [target] [flags]`** - Project cleanup and technical debt reduction | Auto-Persona: Refactorer | MCP: Sequential"

### `/cleanup-audit ...` (subagents and multi-pass audit tooling)

Exact quote:

> "**`/cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`** — Multi-pass read-only repository audit (wave-enabled, complex profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Analyzer, Architect, DevOps, QA, Refactorer"
>
> "- **MCP**: Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns)"
>
> "- **Tools**: [Read, Grep, Glob, Bash(git/wc/find/du), TodoWrite, Task, Write]"
>
> "- **Subagents**: audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet)"

Implications for custom agents:
- The framework supports explicit sub-agent roles for large audits.
- This section provides a concrete example naming convention and division of labor:
  - scanner/analyzer/comparator/consolidator/validator
  - different model/persona assignments (e.g., "Haiku", "Sonnet")

---

## Documentation, planning, and meta commands (relevant to skills/agents that assist workflows)

### `/document [target] [flags]`

Exact quote:

> "**`/document [target] [flags]`** - Documentation generation | Auto-Persona: Scribe, Mentor | MCP: Context7, Sequential"

### `/estimate [target] [flags]`

Exact quote:

> "**`/estimate [target] [flags]`** - Evidence-based estimation | Auto-Persona: Analyzer, Architect | MCP: Sequential, Context7"

### `/task [operation] [flags]`

Exact quote:

> "**`/task [operation] [flags]`** - Long-term project management | Auto-Persona: Architect, Analyzer | MCP: Sequential"

### `/test [type] [flags]`

Exact quote:

> "**`/test [type] [flags]`** - Testing workflows | Auto-Persona: QA | MCP: Playwright, Sequential"

### `/git [operation] [flags]`

Exact quote:

> "**`/git [operation] [flags]`** - Git workflow assistant | Auto-Persona: DevOps, Scribe, QA | MCP: Sequential"

### `/design [domain] [flags]`

Exact quote:

> "**`/design [domain] [flags]`** - Design orchestration | Auto-Persona: Architect, Frontend | MCP: Magic, Sequential, Context7"

### `/index [query] [flags]`

Exact quote:

> "**`/index [query] [flags]`** - Command catalog browsing | Auto-Persona: Mentor, Analyzer | MCP: Sequential"

### `/load [path] [flags]`

Exact quote:

> "**`/load [path] [flags]`** - Project context loading | Auto-Persona: Analyzer, Architect, Scribe | MCP: All servers"

### Iterative operations

Exact quote:

> "**Iterative Operations** - Use `--loop` flag with improvement commands for iterative refinement"

### `/spawn [mode] [flags]`

Exact quote:

> "**`/spawn [mode] [flags]`** - Task orchestration | Auto-Persona: Analyzer, Architect, DevOps | MCP: All servers"

---

## Unified task command (compliance-enforced) — flags and flows

The `/sc:task` command defines a structured interface and policy model. This information is relevant to developing custom commands/skills/agents that must interact with compliance tiers, verification, and orchestration controls.

### `/sc:task [description] [flags]`

Exact quote:

> "**`/sc:task [description] [flags]`** — Unified task execution with tiered compliance (wave-enabled, adaptive profile)"

Exact quotes (execution context):

> "- **Auto-Persona**: Domain-specific (Security → security, Frontend → frontend, etc.)"
>
> "- **MCP**: Sequential (analysis), Serena (context), Context7 (patterns)"
>
> "- **Tools**: [TodoWrite, Read, Grep, Glob, Edit, MultiEdit, Task, Bash]"

### Strategy flags (orchestration dimension)

Exact quote (table):

| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

### Compliance flags (quality dimension)

Exact quote (table):

| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) |

### Verification flags

Exact quote (table):

| Flag | Description |
|------|-------------|
| `--verify critical` | Full sub-agent verification |
| `--verify standard` | Direct test execution only |
| `--verify skip` | Skip verification (use with caution) |
| `--verify auto` | Auto-select based on compliance tier (default) |

### Execution control flags

Exact quote (table):

| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--reason "..."` | Required justification for tier override |

### Tier classification flow (how compliance tier is determined)

Exact quote:

> "#### Tier Classification Flow"
>
> "1. Check for user override (`--compliance`)"
>
> "2. Detect compound phrases (highest priority)"
>
> "3. Score keywords by tier (STRICT > EXEMPT > LIGHT > STANDARD)"
>
> "4. Apply context boosters (file count, security paths)"
>
> "5. Resolve conflicts using priority ordering"
>
> "6. Display confidence and allow user override if <70%"

### Auto-activation triggers (tier suggestions)

Exact quote (table):

| Trigger | Condition | Suggested Tier |
|---------|-----------|----------------|
| Complexity score | ≥0.7 | STRICT |
| Multi-file scope | >3 files | STANDARD minimum |
| Security domain | auth/, security/, crypto/ paths | STRICT |
| Documentation-only | *.md, docs/ | EXEMPT |
| Single trivial change | typo, comment | LIGHT |

---

## Command execution matrix (how to classify commands)

### Performance profiles

Exact quotes:

> "- **optimization**: High-performance with caching and parallel execution"
>
> "- **standard**: Balanced performance with moderate resource usage"
>
> "- **complex**: Resource-intensive with comprehensive analysis"

### Command categories

Exact quotes:

> "- **Development**: build, implement, design"
>
> "- **Planning**: workflow, estimate, task"
>
> "- **Analysis**: analyze, troubleshoot, explain"
>
> "- **Quality**: improve, cleanup"
>
> "- **Testing**: test"
>
> "- **Documentation**: document"
>
> "- **Version-Control**: git"
>
> "- **Meta**: index, load, spawn"

### Wave-enabled commands list

Exact quote:

> "### Wave-Enabled Commands"
>
> "7 commands: `/analyze`, `/build`, `/design`, `/implement`, `/improve`, `/task`, `/workflow`"
