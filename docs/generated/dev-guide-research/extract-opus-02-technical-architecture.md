# Extraction: Technical Architecture for Commands, Skills, and Agents

**Source**: `/config/workspace/SuperClaude_Framework/docs/developer-guide/technical-architecture.md`
**Extracted**: 2026-02-21
**Focus**: Developing custom commands, skills, and agents for the SuperClaude framework

---

## 1. Fundamental Architecture Concept

SuperClaude is a **Context-Oriented Configuration Framework** -- not standalone software. This is critical context for extension development:

> "SuperClaude is NOT standalone software with running processes, execution layers, or performance systems. It is a collection of `.md` instruction files that Claude Code reads to adopt specialized behaviors."

> "SuperClaude's architecture is intentionally simple: it's a well-organized collection of context files that Claude Code reads to modify its behavior. The power comes from the careful crafting of these contexts and their systematic organization, not from any executing code or running processes."

### What SuperClaude IS vs IS NOT

**IS**:
- Context Files: `.md` instructions for Claude Code
- Behavioral Patterns: Workflows and approaches
- Domain Expertise: Specialized knowledge contexts
- Configuration: Settings for actual tools (MCP)
- Framework: Structured prompt engineering

**IS NOT**:
- No Execution Engine: No code runs, no processes execute
- No Performance System: No optimization possible (it's just text)
- No Detection Engine: Claude Code does pattern matching
- No Orchestration Layer: Context files guide, not control
- No Quality Gates: Just instructional patterns

---

## 2. Directory Structure and Component Layout

All framework files live under `~/.claude/`:

```
~/.claude/ (SuperClaude Framework Files Only)
├── CLAUDE.md                       # Main context file with imports
├── FLAGS.md                        # Flag definitions and triggers
├── RULES.md                        # Core behavioral rules
├── PRINCIPLES.md                   # Guiding principles
├── ZIG.md                          # Zig language integration
├── MCP_Context7.md                 # Context7 MCP integration
├── MCP_Magic.md                    # Magic MCP integration
├── MCP_Morphllm.md                 # Morphllm MCP integration
├── MCP_Playwright.md               # Playwright MCP integration
├── MCP_Sequential.md               # Sequential MCP integration
├── MCP_Serena.md                   # Serena MCP integration
├── MCP_Tavily.md                   # Tavily MCP integration
├── MCP_Zig.md                      # Zig MCP integration
├── MODE_Brainstorming.md           # Collaborative discovery mode
├── MODE_Business_Panel.md          # Business expert panel mode
├── MODE_DeepResearch.md            # Deep research mode
├── MODE_Introspection.md           # Transparent reasoning mode
├── MODE_Orchestration.md           # Tool coordination mode
├── MODE_Task_Management.md         # Task orchestration mode
├── MODE_Token_Efficiency.md        # Compressed communication mode
├── agents/                         # Domain specialist contexts (19 total)
│   ├── backend-architect.md
│   ├── business-panel-experts.md
│   ├── deep-research-agent.md
│   ├── devops-architect.md
│   ├── frontend-architect.md
│   ├── learning-guide.md
│   ├── performance-engineer.md
│   ├── python-expert.md
│   ├── quality-engineer.md
│   ├── refactoring-expert.md
│   ├── requirements-analyst.md
│   ├── root-cause-analyst.md
│   ├── security-engineer.md
│   ├── socratic-mentor.md
│   ├── spec-panel-experts.md
│   ├── system-architect.md
│   ├── technical-writer.md
│   ├── test-runner.md
│   └── wave-orchestrator.md
└── commands/                       # Workflow pattern contexts
    └── sc/                         # SuperClaude command namespace (25 total)
        ├── analyze.md
        ├── brainstorm.md
        ├── build.md
        ├── business-panel.md
        ├── cleanup.md
        ├── design.md
        ├── document.md
        ├── estimate.md
        ├── explain.md
        ├── git.md
        ├── help.md
        ├── implement.md
        ├── improve.md
        ├── index.md
        ├── load.md
        ├── reflect.md
        ├── research.md
        ├── save.md
        ├── select-tool.md
        ├── spawn.md
        ├── spec-panel.md
        ├── task.md
        ├── test.md
        ├── troubleshoot.md
        └── workflow.md
```

> "Note: Other directories (backups/, logs/, projects/, serena/, etc.) are Claude Code operational directories, not part of SuperClaude framework content."

---

## 3. Context File Types and Activation Mechanisms

The document defines four context file types:

| File Type | Purpose | Activation | Example |
|-----------|---------|------------|---------|
| **Commands** | Define workflow patterns | `/sc:[command]` (context trigger) | User types `/sc:implement` -> reads `implement.md` |
| **Agents** | Provide domain expertise | `@agent-[name]` or auto | `@agent-security` -> reads `security-engineer.md` |
| **Modes** | Modify interaction style | Flags or triggers | `--brainstorm` -> activates brainstorming mode |
| **Core** | Set fundamental rules | Always active | `RULES.md` always loaded |

---

## 4. The Import System (CLAUDE.md Entry Point)

### How It Works

> "The main `CLAUDE.md` file uses an import system to load multiple context files"

The `@` prefix denotes an import statement. Files are organized by priority:

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

### Import Processing Sequence

> 1. Claude Code reads `CLAUDE.md`
> 2. Encounters `@import` statements
> 3. Loads referenced files into context
> 4. Builds complete behavioral framework
> 5. Applies relevant contexts based on user input

---

## 5. Agent Context Structure (How to Create Agents)

### Required File Anatomy

Each agent `.md` file follows this structure:

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

### Agent Activation Logic (Three Methods)

- **Manual**: User types `@agent-python-expert "task"`
- **Automatic**: Keywords in request trigger agent loading
- **Contextual**: File types or patterns activate relevant agents

### Current Agent Roster (19 agents)

The document lists these installed agents: backend-architect, business-panel-experts, deep-research-agent, devops-architect, frontend-architect, learning-guide, performance-engineer, python-expert, quality-engineer, refactoring-expert, requirements-analyst, root-cause-analyst, security-engineer, socratic-mentor, spec-panel-experts, system-architect, technical-writer, test-runner, wave-orchestrator.

---

## 6. Command Context Structure (How to Create Commands)

### Required File Anatomy

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

### Frontmatter Fields for Commands

- `name`: The command identifier
- `description`: Purpose description
- `category`: One of `utility`, `orchestration`, or `analysis`
- `complexity`: One of `basic`, `enhanced`, or `advanced`
- `mcp-servers`: Array of MCP servers the command should use
- `personas`: Array of personas (agents) to auto-activate

### Command Processing Flow

> When user types `/sc:implement "feature"` in Claude Code conversation:
> 1. Claude reads `commands/sc/implement.md`
> 2. Adopts implementation workflow pattern
> 3. May auto-activate related agents
> 4. Follows defined workflow steps

### Command Namespace

All commands live under `commands/sc/` and are invoked as `/sc:command-name`. There are currently 25 commands in the namespace.

---

## 7. Mode Context Structure (How to Create Modes)

### Required File Anatomy

```markdown
# MODE_[Name].md

## Activation Triggers
- Flag: --mode-name
- Keywords: [triggers]
- Complexity: threshold

## Behavioral Modifications
- Communication style changes
- Decision-making adjustments
- Output format modifications

## Interaction Patterns
- How to respond
- What to prioritize
```

### Mode Naming Convention

Mode files follow the pattern `MODE_[Name].md` and are placed at the root level of `~/.claude/`.

---

## 8. Context Loading Sequence and Data Flow

The full context loading sequence when a command is invoked:

```
User Input (in Claude Code): "/sc:analyze src/ --focus security"
                    |
1. Parse Command: identify 'analyze' command
                    |
2. Load Context: read commands/sc/analyze.md
                    |
3. Check Flags: --focus security
                    |
4. Auto-Activation: load security-engineer.md
                    |
5. Apply Patterns: follow analysis workflow
                    |
6. Generate Output: using loaded contexts
```

### Context Priority Order

> 1. **Explicit Commands**: `/sc:` commands take precedence
> 2. **Manual Agents**: `@agent-` override auto-activation
> 3. **Flags**: Modify behavior of commands/agents
> 4. **Auto-Activation**: Based on keywords/context
> 5. **Default Behavior**: Standard Claude Code

---

## 9. MCP Server Configuration

MCP servers are configured separately from SuperClaude context files:

> "MCP servers are configured in `~/.claude.json` (NOT part of SuperClaude context)"

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

### MCP Integration Model

> - **MCP Servers**: Actual software providing tools
> - **SuperClaude**: Context that tells Claude when to use them
> - **Activation**: Flags or keywords trigger MCP usage

Commands reference MCP servers in their frontmatter (`mcp-servers` field) to declare which servers they need. The `MCP_*.md` files at the root level provide Claude with instructions on when and how to use each MCP server.

---

## 10. Extension Points (How to Extend the Framework)

### Adding New Commands

> 1. Create `~/.claude/commands/sc/new-command.md`
> 2. Define metadata, triggers, and workflow
> 3. No code changes needed - just context

### Adding New Agents

> 1. Create `~/.claude/agents/new-specialist.md`
> 2. Define expertise, triggers, and behaviors
> 3. Agent becomes available

### Adding New Modes

> 1. Create `~/.claude/MODE_NewMode.md`
> 2. Define activation triggers and modifications
> 3. Mode activates based on triggers

---

## 11. Best Practices for Extension Development

The document provides these guidelines:

> - **Keep Context Focused**: One concept per file
> - **Clear Triggers**: Define when context activates
> - **Workflow Patterns**: Provide step-by-step guidance
> - **Examples**: Include practical usage examples
> - **Metadata**: Use frontmatter for configuration

---

## 12. Key Takeaways for Component Development

1. **All components are markdown files** -- no code compilation or registration is needed.
2. **Frontmatter (YAML)** provides structured metadata that drives activation and configuration.
3. **Three activation models exist**: manual invocation, keyword-based auto-activation, and contextual file-type triggers.
4. **Commands use the `/sc:` namespace** and live in `commands/sc/`.
5. **Agents use the `@agent-` prefix** and live in `agents/`.
6. **Modes use flags** (e.g., `--brainstorm`) and live at the root level as `MODE_*.md`.
7. **MCP server integration** is declared in command frontmatter and described in separate `MCP_*.md` context files.
8. **Context priority** flows: Explicit Commands > Manual Agents > Flags > Auto-Activation > Default.
9. **The import system** in `CLAUDE.md` loads core files; commands and agents are loaded on-demand.
10. **No installation step** is needed for new components beyond placing the file in the correct directory (though the `superclaude install` CLI handles this for distribution).
