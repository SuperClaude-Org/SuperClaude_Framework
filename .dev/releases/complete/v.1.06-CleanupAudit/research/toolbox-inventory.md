# Custom Command Toolbox Inventory

**Generated**: 2026-02-19
**Purpose**: Comprehensive inventory of all tools, patterns, and strategies available when building SuperClaude custom commands. Each item describes WHAT it is, WHEN to use it, and HOW it increases reliability/quality/consistency.

---

## 1. Structural Components

### 1.1 Skill Directory Structure
**What**: A `.claude/skills/<name>/` directory containing `SKILL.md` plus supporting files (rules, templates, scripts).
**When**: Always — skills supersede single-file commands. Use for any non-trivial command.
**Reliability Impact**: Supporting files enable separation of concerns. Templates enforce consistent output. Rules files keep SKILL.md under 500 lines (recommended limit).

### 1.2 YAML Frontmatter (6 Required Fields)
**What**: `name`, `description`, `category`, `complexity`, `mcp-servers`, `personas` — matching SuperClaude conventions.
**When**: Every command file, without exception.
**Consistency Impact**: Enables the orchestration system to route, document, and validate commands automatically.

### 1.3 Extended Frontmatter (Skill-Specific Fields)
**What**: `allowed-tools`, `disable-model-invocation`, `model`, `context`, `argument-hint`, `hooks`.
**When**: Selectively based on command requirements.
**Quality Impact**: `allowed-tools` enforces safety boundaries at the platform level. `disable-model-invocation` prevents accidental auto-triggering of expensive commands.

### 1.4 Shell Preprocessing (`!`cmd``)
**What**: Shell commands that execute BEFORE Claude sees the prompt, with output injected into the skill content.
**When**: Commands that need live repo metadata (file counts, git status, branch info, dependency lists).
**Reliability Impact**: Eliminates wasteful initial discovery steps. Claude starts with facts, not guesses.

### 1.5 $ARGUMENTS Substitution
**What**: `$ARGUMENTS` (all args), `$0`/`$1`/`$N` (positional), `${CLAUDE_SESSION_ID}` (session tracking).
**When**: Any command accepting user input — target paths, flags, configuration values.
**Quality Impact**: Enables parameterized commands. Session ID enables unique output naming and resume capability.

---

## 2. Tool Calling Arsenal

### 2.1 Discovery Tools (Read-Only)
| Tool | Purpose | Best For |
|------|---------|----------|
| **Read** | Read file contents | Deep analysis of individual files |
| **Grep** | Regex search across files | Reference tracing, pattern detection |
| **Glob** | Find files by pattern | File inventory, batch creation |

**Reliability Impact**: Read-only tools form the safety foundation for audit commands. Use `allowed-tools: Read, Grep, Glob` to enforce read-only at the platform level.

### 2.2 Modification Tools
| Tool | Purpose | Best For |
|------|---------|----------|
| **Edit** | Single-file search-and-replace | Targeted fixes |
| **MultiEdit** | Batch edits across files | Systematic refactoring |
| **Write** | Create/overwrite files | Report generation, template output |

**Consistency Impact**: Group as "modification tools" in command specs. Never include in audit/analysis commands.

### 2.3 Execution Tools
| Tool | Purpose | Best For |
|------|---------|----------|
| **Bash** | Shell command execution | Running linters, test suites, build tools |
| **Bash(pattern)** | Restricted shell | Safety — allow only specific commands |

**Safety Impact**: `Bash(git log *)` allows git queries but blocks destructive operations.

### 2.4 Orchestration Tools
| Tool | Purpose | Best For |
|------|---------|----------|
| **TodoWrite** | Task list management | Progress tracking across long operations |
| **TodoRead** | Read task list | Status checks, dependency resolution |
| **Task** | Spawn subagents | Parallel batch processing, delegation |
| **Task(type)** | Spawn specific agent type | Restricting to safe agent types |
| **Skill** | Invoke other skills | Composing complex workflows from simpler skills |

**Reliability Impact**: TodoWrite provides visibility into completion state. Task enables parallelism. Skill enables composition.

### 2.5 MCP Tools (Context-Dependent)
| Server | Tools | Purpose |
|--------|-------|---------|
| **Sequential Thinking** | `sequentialthinking` | Structured multi-step reasoning |
| **Context7** | `resolve-library-id`, `query-docs` | Official documentation lookup |
| **Serena** | `find_symbol`, `get_symbols_overview`, etc. | Semantic code understanding |
| **Augment** | `codebase-retrieval` | Semantic codebase search |
| **Tavily** | `tavily-search`, `tavily-extract` | Web search and content extraction |
| **Playwright** | Browser automation tools | E2E testing, visual validation |

**Quality Impact**: MCP tools provide specialized intelligence. Sequential for analysis depth. Serena for import chain tracing. Context7 for framework-specific validation.

**CONSTRAINT**: MCP tools are NOT available in background subagents. Only foreground subagents or the orchestrator can use them.

---

## 3. Sub-Agent Architecture

### 3.1 Built-in Agent Types
| Type | Model | Tools | Best For |
|------|-------|-------|----------|
| **Explore** | Haiku (fast) | Read-only | Quick file scanning, surface-level analysis |
| **Plan** | Inherit | Read-only | Research and planning |
| **general-purpose** | Inherit | All tools | Deep analysis, multi-step operations |
| **Bash** | Inherit | Bash only | Running scripts, build operations |

### 3.2 Custom Subagent Definitions
**What**: Markdown files in `.claude/agents/<name>.md` with frontmatter defining tools, model, permissions, maxTurns, and a custom system prompt.
**When**: When you need workers with specialized behavior beyond built-in types.
**Reliability Impact**: Custom system prompts enforce output format, analysis methodology, and safety constraints per agent type.

**Key Frontmatter Fields**:
- `tools`: Restrict to specific tool set
- `model`: `haiku` for fast/cheap, `sonnet` for deep analysis, `opus` for critical reasoning
- `maxTurns`: Prevent runaway agents (e.g., 30 for batch audit)
- `permissionMode`: `plan` for read-only enforcement, `dontAsk` for autonomous execution
- `skills`: Preload specific skills into subagent context
- `mcpServers`: MCP servers available (foreground only)
- `memory`: Persistent memory scope (`user`, `project`, `local`)

### 3.3 Critical Constraints
| Constraint | Impact | Mitigation |
|-----------|--------|------------|
| **No nested spawning** | Subagents cannot spawn sub-subagents | All orchestration in top-level skill |
| **~7-10 concurrent limit** | Performance degrades beyond this | Run in waves of 7-8 |
| **~20K token overhead** | Per subagent invocation cost | Larger batches reduce overhead ratio |
| **No MCP in background** | Background subagents lack MCP | Use foreground for MCP-dependent work |
| **Context isolation** | Subagents don't see parent conversation | Pass all needed context in the prompt |
| **No inter-agent communication** | Agents can't message each other | Use files on disk as coordination channel |

### 3.4 Foreground vs Background Execution
| Mode | Behavior | Best For |
|------|----------|----------|
| **Foreground** | Blocking, sequential, full permissions | Deep analysis needing MCP, user interaction |
| **Background** | Concurrent, auto-deny permissions | Batch processing, parallel scanning |

---

## 4. Orchestration Strategies

### 4.1 Fan-Out / Fan-In
**Pattern**: Orchestrator divides work → spawns N parallel agents → agents write results to disk → orchestrator reads and merges.
**When**: Any batch processing operation (audit batches, multi-file analysis).
**Reliability**: File-based coordination is crash-safe. Each batch result is independently valuable.

### 4.2 Multi-Pass Escalation
**Pattern**: Pass 1 (broad/shallow) → findings inform Pass 2 (narrow/deep) → findings inform Pass 3 (cross-cutting).
**When**: Operations requiring increasing analytical depth.
**Quality**: Each pass builds on verified findings. Prevents wasting deep analysis on obvious junk.

### 4.3 Haiku-First Escalation
**Pattern**: Use Haiku agents for initial scan → flag items → use Sonnet/Opus only on flagged items.
**When**: Large-scale operations where most items are straightforward.
**Cost Impact**: 50-70% cost reduction. If Pass 1 flags 15%, cost = 100% Haiku + 15% Sonnet vs 100% Sonnet.

### 4.4 Adversarial Validation
**Pattern**: For critical findings, spawn a "devil's advocate" agent to argue false positive → if unconvincing, finding confirmed.
**When**: High-stakes findings where false positives are costly (DELETE recommendations, security issues).
**Quality**: Significantly reduces false positive rate. Adds ~20K tokens per validated finding.

### 4.5 Incremental Save / Checkpointing
**Pattern**: After each batch, write results to disk + update progress file → enables resume-from-checkpoint.
**When**: Long-running operations (>30 min), operations processing >100 items.
**Reliability**: Crash-safe. Partial results are preserved. Sessions can be resumed.

### 4.6 Adaptive Batch Sizing
**Pattern**: Weight files by complexity (size, type) → create batches by weight not count → ensures balanced agent workloads.
**When**: Repos with mixed file sizes/complexities.
**Quality**: Prevents agent overload on large files and underutilization on small files.

### 4.7 Structured Output Enforcement
**Pattern**: Inject report templates into agent prompts → agents fill in template sections → orchestrator validates completeness.
**When**: Any multi-agent operation producing reports.
**Consistency**: Ensures all agents produce identically structured output. Enables automated quality validation.

### 4.8 Quality Gates Between Phases
**Pattern**: Before advancing to next phase, verify: all tasks complete + required sections present + findings count valid.
**When**: Multi-phase operations where each phase depends on prior quality.
**Reliability**: Prevents cascading errors. Failed gates trigger remediation or user notification.

---

## 5. Persona Integration

### 5.1 Auto-Activation Mapping
| Domain Trigger | Persona | MCP Server | Concern |
|---------------|---------|------------|---------|
| Infrastructure/CI/deploy | **devops** | Sequential | Pipeline integrity |
| Code architecture | **architect** | Sequential | System design |
| Test files/quality | **qa** | Playwright | Test coverage |
| Security/auth/crypto | **security** | Sequential | Threat modeling |
| Code duplication/debt | **refactorer** | Sequential | Clean code |
| Documentation | **scribe** | Context7 | Documentation accuracy |
| Performance | **performance** | Playwright | Optimization |
| Root cause analysis | **analyzer** | Sequential | Investigation |

### 5.2 Multi-Persona Coordination
**Pattern**: Primary persona leads → consulting personas provide specialized input → validation personas review.
**When**: Commands spanning multiple domains (audit touches infra, code, docs, tests).
**Quality**: Each domain gets specialist attention. Cross-domain conflicts resolved via priority matrix.

---

## 6. Quality & Safety Mechanisms

### 6.1 Tool Restriction (allowed-tools)
**What**: Platform-level enforcement of which tools an agent can use.
**Reliability**: Cannot be bypassed by prompt injection. The only truly reliable safety mechanism.

### 6.2 Critical Boundaries Section
**What**: Explicit STOP directive + Will NOT list + defined output format + next-step recommendation.
**When**: Commands that should NEVER implement/execute (research, audit, analysis).
**Safety**: Prevents scope creep where Claude tries to act on findings.

### 6.3 Boundary Symmetry (Will / Will Not)
**What**: 3 positive capabilities + 3 negative constraints, balanced and specific.
**Consistency**: Sets clear expectations. Prevents both over-reach and under-delivery.

### 6.4 Validation Gates
**What**: Checkpoints where output is validated before proceeding.
**When**: Between phases, before aggregation, before final output.
**Quality**: Catches incomplete or malformed results before they compound.

### 6.5 Evidence Requirements
**What**: Specific evidence types required for each recommendation class (DELETE needs grep proof, KEEP needs reference citation).
**When**: Any command producing recommendations that others will act on.
**Reliability**: Prevents lazy recommendations. Every claim is verifiable.

---

## 7. Progress Tracking

### 7.1 TodoWrite Session Tasks
**What**: Built-in task list with states (pending, in_progress, completed, blocked).
**When**: Operations with 3+ steps.
**Visibility**: User can see real-time progress. Blocked dependencies are visible.

### 7.2 File-Based Checkpointing
**What**: State file on disk tracking completion status of all batches and phases.
**When**: Long-running operations where session interruption is possible.
**Resilience**: Enables resume-from-checkpoint. Partial results preserved.

### 7.3 Incremental Disk Saves
**What**: Write results to disk after every batch (not just at the end).
**When**: Any operation processing items in batches.
**Safety**: Context window loss doesn't lose results. Each batch independently recoverable.

---

## 8. Cost & Performance Optimization

### 8.1 Model Tiering
| Phase | Recommended Model | Rationale |
|-------|------------------|-----------|
| Surface scan | Haiku | Fast, cheap, sufficient for obvious issues |
| Deep analysis | Sonnet | Good balance of depth and cost |
| Critical reasoning | Opus | Maximum accuracy for high-stakes decisions |
| Synthesis/aggregation | Inherit (orchestrator model) | Needs full context understanding |

### 8.2 Batch Size Optimization
| Constraint | Impact | Recommendation |
|-----------|--------|----------------|
| 20K overhead per agent | Fewer large batches cheaper | 40-50 files for surface scan |
| Agent context limit | Too many files = truncation | 20-30 files for deep analysis |
| ~7-10 concurrent limit | Run in waves | Batch count ÷ 8 = wave count |

### 8.3 Progressive Disclosure
**What**: Skill description loads at startup (lightweight). Full content loads only on invocation.
**Cost**: Saves context budget when the command isn't in use. Essential for resource-intensive commands.

### 8.4 Conditional Depth
**What**: Start shallow, go deep only where warranted.
**Pattern**: Scan all → flag subset → analyze flagged → validate critical → report all.
**Cost**: Dramatically reduces total tokens for repos where most files are fine.

---

## 9. SuperClaude Consistency Requirements

### 9.1 Structural Rules (from Agent 1 analysis)
1. YAML frontmatter with 6 required fields in specified order
2. H1 title: `# /sc:<name> - <Short Title>`
3. Canonical 13-section ordering
4. Exactly 5-step behavioral flow (Assess → Prepare → Execute → Verify → Output)
5. MCP Integration section required when servers declared
6. Tool Coordination with bold-prefixed grouped bullets
7. Key Patterns with arrow notation (3-5 bullets)
8. Examples progressing simple → complex (3-4 examples)
9. Boundary symmetry (Will: 3 bullets, Will Not: 3 bullets)
10. Next-step chaining to other /sc:* commands

### 9.2 Naming Conventions
- Command names: lowercase, single-word or hyphenated
- Persona names: kebab-case (`qa-specialist`, `devops-engineer`)
- MCP server names: lowercase single words (`sequential`, `context7`)
- Categories: `utility`, `workflow`, `special`, `reference`
- Complexity: `basic`, `standard`, `enhanced`, `advanced`, `high`

### 9.3 Integration with Framework
- Commands listed in COMMANDS.md with category, purpose, auto-persona, MCP, tools
- Commands registered in ORCHESTRATOR.md routing tables
- Persona activation triggers documented in PERSONAS.md
- MCP usage patterns documented in MCP.md
