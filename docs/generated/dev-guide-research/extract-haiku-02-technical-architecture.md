# Extraction — Developing Custom Commands, Agents, or Skills (Technical Architecture)

**Source file:** `/config/workspace/SuperClaude_Framework/docs/developer-guide/technical-architecture.md`

> Scope note: This extraction includes **all** content in the source that pertains to **developing/extending SuperClaude context artifacts**, especially **custom commands** and **custom agents**. The source file does **not** describe a “skills” package format; where “skills” are relevant, this extraction explicitly notes the absence of skill-specific details in the source.

---

## 1) Core architectural model (what you are building)

### SuperClaude is context files (not a running system)

Exact quote:

> "**Important**: SuperClaude is NOT standalone software with running processes, execution layers, or performance systems. It is a collection of `.md` instruction files that Claude Code reads to adopt specialized behaviors."

This matters for custom commands/agents because the “implementation” is **authoring markdown context** that Claude Code loads and follows.

---

## 2) Where custom commands/agents live (context file architecture)

### Directory structure (relevant excerpts)

The source defines the framework file layout under `~/.claude/` and explicitly calls out the `agents/` and `commands/` directories.

Exact quote and code block (directory layout):

```text
~/.claude/ (SuperClaude Framework Files Only)
├── CLAUDE.md                       # Main context file with imports
├── FLAGS.md                        # Flag definitions and triggers
├── RULES.md                        # Core behavioral rules
├── PRINCIPLES.md                   # Guiding principles
...
├── agents/                         # Domain specialist contexts (19 total)
│   ├── backend-architect.md        # Backend expertise
│   ├── business-panel-experts.md   # Business strategy panel
│   ├── deep-research-agent.md      # Deep research expertise
│   ├── devops-architect.md         # DevOps expertise
│   ├── frontend-architect.md       # Frontend expertise
│   ├── learning-guide.md           # Educational expertise
│   ├── performance-engineer.md     # Performance expertise
│   ├── python-expert.md            # Python expertise
│   ├── quality-engineer.md         # Quality assurance expertise
│   ├── refactoring-expert.md       # Code quality expertise
│   ├── requirements-analyst.md     # Requirements expertise
│   ├── root-cause-analyst.md       # Problem diagnosis expertise
│   ├── security-engineer.md        # Security expertise
│   ├── socratic-mentor.md          # Educational expertise
│   ├── spec-panel-experts.md       # Specification review panel
│   ├── system-architect.md         # System design expertise
│   ├── technical-writer.md         # Documentation expertise
│   ├── test-runner.md              # Test execution expertise
│   └── wave-orchestrator.md        # Wave orchestration patterns
└── commands/                       # Workflow pattern contexts
    └── sc/                         # SuperClaude command namespace (25 total)
        ├── analyze.md              # Analysis patterns
        ├── brainstorm.md           # Discovery patterns
        ├── build.md                # Build patterns
        ├── business-panel.md       # Business expert panel patterns
        ├── cleanup.md              # Cleanup patterns
        ├── design.md               # Design patterns
        ├── document.md             # Documentation patterns
        ├── estimate.md             # Estimation patterns
        ├── explain.md              # Explanation patterns
        ├── git.md                  # Git workflow patterns
        ├── help.md                 # Help and command listing
        ├── implement.md            # Implementation patterns
        ├── improve.md              # Improvement patterns
        ├── index.md                # Index patterns
        ├── load.md                 # Context loading patterns
        ├── reflect.md              # Reflection patterns
        ├── research.md             # Deep research patterns
        ├── save.md                 # Session persistence patterns
        ├── select-tool.md          # Tool selection patterns
        ├── spawn.md                # Multi-agent patterns
        ├── spec-panel.md           # Specification review panel
        ├── task.md                 # Task management patterns
        ├── test.md                 # Testing patterns
        ├── troubleshoot.md         # Troubleshooting patterns
        └── workflow.md             # Workflow planning patterns

Note: Other directories (backups/, logs/, projects/, serena/, etc.) are Claude Code
operational directories, not part of SuperClaude framework content.
```

### Context file types (how commands/agents/modes map to triggers)

Exact quote (table):

| File Type | Purpose | Activation | Example |
|-----------|---------|------------|---------|
| **Commands** | Define workflow patterns | `/sc:[command]` (context trigger) | User types `/sc:implement` → reads `implement.md` |
| **Agents** | Provide domain expertise | `@agent-[name]` or auto | `@agent-security` → reads `security-engineer.md` |
| **Modes** | Modify interaction style | Flags or triggers | `--brainstorm` → activates brainstorming mode |
| **Core** | Set fundamental rules | Always active | `RULES.md` always loaded |

---

## 3) Import system (how your custom contexts get loaded)

### How `CLAUDE.md` imports work

Exact quote:

> "The main `CLAUDE.md` file uses an import system to load multiple context files:"

Exact code block:

```markdown
# CLAUDE

*MANDATORY*
@FLAGS.md                  # Flag definitions and triggers
@RULES.md                  # Core behavioral rules
@PRINCIPLES.md             # Guiding principles
*SECONDARY*
@MCP_Context7.md           # Context7 MCP integration
@MCP_Magic.md              # Magic MCP integration
@MCP_Morphllm.md           # Morphllm MCP integration
@MCP_Playwright.md         # Playwright MCP integration
@MCP_Sequential.md         # Sequential MCP integration
@MCP_Serena.md             # Serena MCP integration
@MCP_Tavily.md             # Tavily MCP integration
@MCP_Zig.md                # Zig MCP integration
*CRITICAL*
@MODE_Brainstorming.md     # Collaborative discovery mode
@MODE_Business_Panel.md    # Business expert panel mode
@MODE_DeepResearch.md      # Deep research mode
@MODE_Introspection.md     # Transparent reasoning mode
@MODE_Task_Management.md   # Task orchestration mode
@MODE_Orchestration.md     # Tool coordination mode
@MODE_Token_Efficiency.md  # Compressed communication mode
*LANGUAGE SPECIFIC*
@ZIG.md                    # Zig language integration
```

### Import processing steps

Exact quote (numbered list):

1. "Claude Code reads `CLAUDE.md`"
2. "Encounters `@import` statements"
3. "Loads referenced files into context"
4. "Builds complete behavioral framework"
5. "Applies relevant contexts based on user input"

---

## 4) Developing custom agents

### Agent file anatomy (template you should follow)

Exact quote:

> "Each agent `.md` file follows this structure:"

Exact code block:

```markdown
---
name: agent-name
description: Brief description
category: specialized|architecture|quality
---

# Agent Name

## Triggers
- Keywords that activate this agent
- File types that trigger activation
- Complexity thresholds

## Behavioral Mindset
Core philosophy and approach

## Focus Areas
- Domain expertise area 1
- Domain expertise area 2

## Key Actions
1. Specific behavior pattern
2. Problem-solving approach
```

### Agent activation logic (how users and Claude Code invoke your agent)

Exact quote:

- "**Manual**: User types `@agent-python-expert \"task\"`"
- "**Automatic**: Keywords in request trigger agent loading"
- "**Contextual**: File types or patterns activate relevant agents"

### Adding new agents (extension procedure)

Exact quote:

> "### Adding New Agents"

Exact steps:

1. "Create `~/.claude/agents/new-specialist.md`"
2. "Define expertise, triggers, and behaviors"
3. "Agent becomes available"

---

## 5) Developing custom commands

### Command file anatomy (template you should follow)

Exact quote:

> "### Anatomy of a Command File"

Exact code block:

```markdown
---
name: command-name
description: Command purpose
category: utility|orchestration|analysis
complexity: basic|enhanced|advanced
mcp-servers: [context7, sequential]
personas: [architect, engineer]
---

# /sc:command-name

## Triggers
- When to use this command
- Context indicators

## Usage
/sc:command-name [target] [--options]

## Workflow Pattern
1. Step 1: Initial action
2. Step 2: Processing
3. Step 3: Validation

## Examples
Practical usage examples
```

### Command processing (what happens when a user runs `/sc:<command>`)

Exact quote:

> "When user types `/sc:implement \"feature\"` in Claude Code conversation:"

Exact sequence:

1. "Claude reads `commands/sc/implement.md`"
2. "Adopts implementation workflow pattern"
3. "May auto-activate related agents"
4. "Follows defined workflow steps"

### Adding new commands (extension procedure)

Exact quote:

> "### Adding New Commands"

Exact steps:

1. "Create `~/.claude/commands/sc/new-command.md`"
2. "Define metadata, triggers, and workflow"
3. "No code changes needed - just context"

---

## 6) Skills (what the source does and does not say)

This source file’s “context architecture” describes **Commands**, **Agents**, **Modes**, and **Core** context.

What it explicitly covers:
- Commands: `/sc:[command]` → `commands/sc/<command>.md`
- Agents: `@agent-[name]` / auto-activation → `agents/<agent>.md`
- Modes: flags/keywords → `MODE_*.md`

What it does **not** define in this document:
- A directory structure, metadata/frontmatter schema, activation rules, or installation workflow for **skills**.

(There is no “Skills” row in the “Context File Types” table, and no “Adding New Skills” section.)

---

## 7) How command/agent contexts combine at runtime (priority and loading)

### Context loading sequence (example)

Exact code block:

```text
User Input (in Claude Code): "/sc:analyze src/ --focus security"
                    ↓
1. Parse Command: identify 'analyze' command
                    ↓
2. Load Context: read commands/sc/analyze.md
                    ↓
3. Check Flags: --focus security
                    ↓
4. Auto-Activation: load security-engineer.md
                    ↓
5. Apply Patterns: follow analysis workflow
                    ↓
6. Generate Output: using loaded contexts
```

### Context priority rules

Exact quote:

1. "**Explicit Commands**: `/sc:` commands take precedence"
2. "**Manual Agents**: `@agent-` override auto-activation"
3. "**Flags**: Modify behavior of commands/agents"
4. "**Auto-Activation**: Based on keywords/context"
5. "**Default Behavior**: Standard Claude Code"

---

## 8) Best practices for authoring new command/agent context

Exact quote (best practices list):

- "**Keep Context Focused**: One concept per file"
- "**Clear Triggers**: Define when context activates"
- "**Workflow Patterns**: Provide step-by-step guidance"
- "**Examples**: Include practical usage examples"
- "**Metadata**: Use frontmatter for configuration"

---

## 9) MCP servers in command metadata (relevant to custom command design)

### Where MCP server configuration actually lives

This is relevant when your custom command declares `mcp-servers: [...]` in its frontmatter: the server definitions themselves are outside the SuperClaude context files.

Exact quote:

> "MCP servers are configured in `~/.claude.json` (NOT part of SuperClaude context):"

Exact code block:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "sequential-thinking-mcp@latest"]
    }
  }
}
```

### MCP integration responsibilities

Exact quote:

- "**MCP Servers**: Actual software providing tools"
- "**SuperClaude**: Context that tells Claude when to use them"
- "**Activation**: Flags or keywords trigger MCP usage"

---

## 10) Important clarifications (constraints that affect extension work)

### What SuperClaude is NOT (implications for custom commands/agents)

Exact quote:

- "❌ **No Execution Engine**: No code runs, no processes execute"
- "❌ **No Performance System**: No optimization possible (it's just text)"
- "❌ **No Detection Engine**: Claude Code does pattern matching"
- "❌ **No Orchestration Layer**: Context files guide, not control"
- "❌ **No Quality Gates**: Just instructional patterns"

### What SuperClaude IS (what you are authoring)

Exact quote:

- "✅ **Context Files**: `.md` instructions for Claude Code"
- "✅ **Behavioral Patterns**: Workflows and approaches"
- "✅ **Domain Expertise**: Specialized knowledge contexts"
- "✅ **Configuration**: Settings for actual tools (MCP)"
- "✅ **Framework**: Structured prompt engineering"
