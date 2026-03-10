# SuperClaude Custom Command Guide & Best Practices

**Generated**: 2026-02-19
**Purpose**: Reusable guide for building SuperClaude custom commands. Covers structure, conventions, tool selection, MCP integration, agent orchestration, quality gates, and output standards.
**Audience**: Anyone creating a new `/sc:*` command for the SuperClaude framework.

---

## 1. Decision: Skill vs Command vs Subagent

### Use a Skill when:
- You need supporting files (templates, rules, scripts)
- The command is resource-intensive (use `disable-model-invocation: true`)
- You want progressive disclosure (only description in startup context)
- You need directory-based organization

### Use a Command (.md file) when:
- The command is simple and self-contained (under 200 lines)
- No supporting files are needed
- Context cost is negligible

### Use a Custom Subagent when:
- You're defining a **worker** that will be spawned by a skill or command
- You need specific tool restrictions, model selection, or maxTurns per worker type
- Workers need persistent memory across sessions

### Recommended: Hybrid Approach
For complex commands, use BOTH:
```
.claude/skills/sc-<name>/     # Orchestrator (skill)
├── SKILL.md
├── rules/
├── templates/
└── scripts/

.claude/agents/<worker>.md    # Worker agents (subagents)
```

### Command + Skill Hybrid (for slash-command registration)
When using a Skill for supporting files, you **MUST ALSO** create a Command `.md`
entry point in `src/superclaude/commands/`. The skill provides the orchestration
engine; the command provides the `/sc:name` slash-command registration.

```
src/superclaude/commands/<name>.md    # Entry point (thin, ~70 lines)
src/superclaude/skills/sc-<name>/     # Orchestration engine (full spec)
├── SKILL.md
├── rules/
├── templates/
└── scripts/
src/superclaude/agents/<worker>.md    # Worker agents (if needed)
```

**Pattern**: Command = concise (frontmatter + usage + summary + examples + boundaries).
Skill = comprehensive (full behavioral flow + MCP + tools + patterns + supporting files).
Do NOT duplicate detailed behavioral content in both — the command references the skill,
and the skill contains the full orchestration spec.

**Reference implementation**: `cleanup-audit` (command: 93 lines, skill: 134 lines)
**Anti-pattern**: `task-unified` (567-line command duplicating skill content)

---

## 2. Skill File Structure

### Required: SKILL.md
Keep under 500 lines. Focus on orchestration logic. Move details to supporting files.

### Optional: Supporting Files
```
sc-<command-name>/
├── SKILL.md                   # Main orchestration (<500 lines)
├── rules/
│   └── <pass-or-phase>.md    # Criteria, rules, constraints per phase
├── templates/
│   └── <output-type>.md      # Templates for structured output
└── scripts/
    └── <helper>.sh           # Shell scripts for preprocessing
```

---

## 3. SKILL.md Anatomy (SuperClaude Convention)

Every SKILL.md must follow this structure, consistent with existing /sc:* commands:

```markdown
---
name: <command-name>
description: "<Verb-phrase describing what the command does>"
category: <utility|workflow|special|reference>
complexity: <basic|standard|enhanced|advanced|high>
mcp-servers: [<server1>, <server2>]
personas: [<persona1>, <persona2>]
disable-model-invocation: <true|false>
allowed-tools: <tool-list>
argument-hint: "<hint shown in autocomplete>"
---

# /sc:<command-name> - <Short Descriptive Title>

## Triggers
- <3-5 activation scenarios>

## Usage
\```
/sc:<command-name> [target] [--flag1 option1|option2] [--flag2]
\```

## Behavioral Flow
1. **<AssessVerb>**: <Assessment phase>
2. **<PrepareVerb>**: <Planning phase>
3. **<ExecuteVerb>**: <Action phase>
4. **<VerifyVerb>**: <Validation phase>
5. **<OutputVerb>**: <Reporting phase>

Key behaviors:
- <3-5 distinctive behavioral characteristics>

## MCP Integration
- **<Server> MCP**: <When activated and why>
- **Persona Coordination**: <Which personas and for what>

## Tool Coordination
- **Read/Grep/Glob**: <Discovery purpose>
- **Edit/MultiEdit**: <Modification purpose>
- **Write**: <Generation purpose>
- **Bash**: <Execution purpose>
- **TodoWrite**: <Tracking purpose>
- **Task**: <Delegation purpose>

## Key Patterns
- **<Pattern Name>**: <input> → <transformation> → <output>

## Examples
### <Basic Usage>
### <Focused Flag>
### <Combined Flags>
### <Advanced Usage>

## Boundaries
**Will:**
- <3 positive capabilities>

**Will Not:**
- <3 negative constraints>

## CRITICAL BOUNDARIES
<!-- For commands that should NOT implement -->
**<STOP DIRECTIVE>**

**Explicitly Will NOT**:
- <hard constraints>

**Output**: <defined output format>

**Next Step**: <workflow continuation to /sc:* commands>
```

---

## 4. Frontmatter Reference

### SuperClaude Fields (Required)
| Field | Values | Purpose |
|-------|--------|---------|
| `name` | lowercase, hyphenated | Command identifier |
| `description` | Quoted verb-phrase | What the command does |
| `category` | `utility`, `workflow`, `special`, `reference` | Routing category |
| `complexity` | `basic`, `standard`, `enhanced`, `advanced`, `high` | Feature gate |
| `mcp-servers` | Array of server names | Declared MCP dependencies |
| `personas` | Array of persona names | Declared persona activations |

### Platform Fields (Optional, Skill-Specific)
| Field | Values | Purpose |
|-------|--------|---------|
| `disable-model-invocation` | `true`/`false` | Prevent auto-triggering |
| `allowed-tools` | CSV tool list | Platform-level safety |
| `model` | `haiku`, `sonnet`, `opus`, `inherit` | Model selection |
| `context` | `fork`, inline | Execution isolation |
| `argument-hint` | String | Autocomplete hint |
| `hooks` | Object | Lifecycle hooks |

### Complexity-Driven Feature Matrix
| Complexity | MCP | Personas | TodoWrite | Task Delegation | Wave |
|-----------|-----|----------|-----------|----------------|------|
| basic | No | No | No | No | No |
| standard | Optional | Optional | If multi-file | No | No |
| enhanced | Yes | Yes | Standard | No | No |
| advanced | Full suite | Multi-persona | Required | Yes | Eligible |
| high | Full suite | Multi-persona | Required | Yes | Eligible |

---

## 5. Behavioral Flow Design

### The 5-Step Arc
Every command MUST have exactly 5 steps following:

| Step | Phase | Verb Pool | Purpose |
|------|-------|-----------|---------|
| 1 | Assessment | Analyze, Discover, Understand, Examine, Scan | Gather information |
| 2 | Preparation | Plan, Validate, Configure, Decompose, Choose | Organize approach |
| 3 | Execution | Execute, Generate, Orchestrate, Coordinate, Apply | Do the work |
| 4 | Verification | Validate, Analyze, Monitor, Assess, Verify | Check quality |
| 5 | Output | Report, Integrate, Optimize, Package, Document | Deliver results |

### Key Behaviors Section
After the 5 steps, include 3-5 bullets describing what makes this command distinctive:
- Orchestration patterns used
- MCP/persona coordination
- Safety characteristics
- Performance optimizations

---

## 6. Sub-Agent Orchestration Guide

### When to Use Sub-Agents
- Batch processing (>20 items to analyze)
- Operations benefiting from parallelism
- When context isolation is beneficial (each batch independent)
- When different model tiers are appropriate for different phases

### Sub-Agent Design Principles

1. **One agent type per concern**: Don't make a single agent do everything. Define scanner, analyzer, validator as separate types.

2. **Explicit tool restrictions**: Always specify `tools` in subagent definitions. Don't inherit all tools when you need a subset.

3. **Set maxTurns**: Prevent runaway agents. Typical values:
   - Surface scan: 15-20 turns
   - Deep analysis: 25-35 turns
   - Synthesis: 40-50 turns

4. **Model selection by phase**:
   - Haiku for surface/broad scans (fast, cheap)
   - Sonnet for analysis (good depth/cost balance)
   - Opus for critical decisions (maximum accuracy)

5. **Structured prompts**: Include the exact output format in the agent's system prompt. Agents produce consistent output only when explicitly told the structure.

6. **File-based coordination**: Agents communicate via files on disk. The orchestrator reads results and passes relevant context to subsequent agents.

### Concurrency Management
```
Total items: 200
Batch size: 25
Total batches: 8
Concurrent limit: 7

Wave 1: Batches 1-7 (parallel)
Wave 2: Batch 8 (parallel, or sequential if <7)

Between waves: Quality gate check
```

---

## 7. Safety & Quality Gates

### Platform-Level Safety
1. **allowed-tools**: Restrict at the skill level for the orchestrator
2. **tools**: Restrict at the subagent level for workers
3. **permissionMode**: `plan` forces read-only on subagents

### Prompt-Level Safety
1. **Critical Boundaries**: Explicit STOP directive in SKILL.md
2. **Will Not section**: Clear negative constraints
3. **Evidence requirements**: Per-recommendation-type proof standards

### Quality Gates
Define gates between phases:
```markdown
## Quality Gate: Phase N → Phase N+1
Before proceeding:
1. All batch tasks marked complete in TodoWrite
2. All batch reports contain required sections
3. Findings count > 0 (investigate if zero)
4. No malformed reports detected
5. Coverage % meets minimum threshold
```

### Validation Patterns
- **Spot-check sampling**: For every 50 items, randomly verify 5
- **Cross-reference verification**: Check recommendations against actual state
- **Adversarial challenge**: For critical findings, spawn a devil's advocate agent

---

## 8. Output Standards

### Report Structure
Every command should define its output format explicitly:
- Use markdown templates in `templates/` directory
- Include required sections and optional sections
- Define per-item profile fields (what must be present for each analyzed item)
- Include summary counts and coverage metrics

### Next-Step Chaining
Always end with a workflow recommendation:
```markdown
**Next Step**: Use `/sc:implement` to execute safe recommendations,
then `/sc:test` to verify no regressions, then `/sc:git` to commit.
```

### Incremental Output
For long-running commands:
- Save after each batch (never accumulate >10 unwritten results)
- Use a progress file for resume capability
- Each partial report should be independently useful

---

## 9. Shell Preprocessing Patterns

### Repository Context
```markdown
## Repository Context
- Total files: !`git ls-files | wc -l`
- File breakdown: !`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`
- Repo size: !`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null`
- Current branch: !`git branch --show-current`
- Last commit: !`git log --oneline -1`
```

### Scope Calculation
```markdown
## Target Scope
- Target: $ARGUMENTS
- Files in scope: !`find $0 -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | wc -l`
- File types: !`find $0 -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10`
```

---

## 10. Integration Checklist

When creating a new /sc:* command, update these framework files:

- [ ] **COMMANDS.md**: Add command entry with category, purpose, auto-persona, MCP, tools
- [ ] **ORCHESTRATOR.md**: Add routing table entry with pattern, complexity, auto-activates, confidence
- [ ] **PERSONAS.md**: Update persona triggers if adding new domain keywords
- [ ] **MCP.md**: Update server use cases if command introduces new MCP patterns
- [ ] **FLAGS.md**: Add any new flags the command introduces

---

## 11. Anti-Patterns to Avoid

1. **Monolith SKILL.md**: Don't put everything in one file. Use supporting files.
2. **Unrestricted tools**: Always specify `allowed-tools` for safety-critical commands.
3. **No maxTurns**: Always set limits on subagents to prevent runaway execution.
4. **Sequential when parallel works**: Default to parallel batch execution. Sequential only for dependencies.
5. **Same model for all phases**: Use Haiku for cheap scans, escalate to Sonnet/Opus for depth.
6. **Context accumulation**: Don't read all batch results into context. Process incrementally or in waves.
7. **Missing quality gates**: Always validate between phases before proceeding.
8. **Missing next-step**: Always chain to the next /sc:* command in the workflow.
9. **Inconsistent output**: Always use templates for structured output from subagents.
10. **No progress tracking**: Always use TodoWrite for operations with 3+ steps.

---

## 12. Quick Reference: Creating a New Command

```
1. Decide: Skill (complex) or Command (simple)?
2. If Skill: Create directory src/superclaude/skills/sc-<name>/
3. Write SKILL.md following the 13-section template
4. Add supporting files: rules/, templates/, scripts/
5. Define custom subagents if needed: src/superclaude/agents/<worker>.md
6. CRITICAL: Create thin command entry point at src/superclaude/commands/<name>.md
   (frontmatter + usage + summary + examples + boundaries — ~70 lines)
7. Set skill frontmatter: name, description, category, complexity, mcp-servers, personas, allowed-tools, argument-hint
8. Set command frontmatter: name, description, category, complexity, mcp-servers, personas (NO skill-only fields)
9. Design 5-step behavioral flow (in SKILL.md only, NOT in command)
10. Define quality gates between phases
11. Test with a small scope first
12. Update framework integration files (COMMANDS.md, ORCHESTRATOR.md)
13. Run `make sync-dev` and `make verify-sync` to validate
14. Document in the command catalog
```
