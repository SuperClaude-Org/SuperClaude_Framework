# SuperClaude Architecture

**Last Updated**: 2025-10-14
**Version**: 4.1.5

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [PM Agent Mode: The Meta-Layer](#pm-agent-mode-the-meta-layer)
4. [Component Relationships](#component-relationships)
5. [Serena MCP Integration](#serena-mcp-integration)
6. [PDCA Engine](#pdca-engine)
7. [Data Flow](#data-flow)
8. [Extension Points](#extension-points)

---

## System Overview

### What is SuperClaude?

SuperClaude is a **Context-Oriented Configuration Framework** that transforms Claude Code into a structured development platform. It is NOT standalone software with running processes - it is a collection of `.md` instruction files that Claude Code reads to adopt specialized behaviors.

### Key Components

```
SuperClaude Framework
├── Commands (26)      → Workflow patterns
├── Agents (16)        → Domain expertise
├── Modes (7)          → Behavioral modifiers
├── MCP Servers (8)    → External tool integrations
└── PM Agent Mode      → Meta-layer orchestration (Always-Active)
```

### Version Information

- **Current Version**: 4.1.5
- **Commands**: 26 slash commands (`/sc:*`)
- **Agents**: 16 specialized domain experts
- **Modes**: 7 behavioral modes
- **MCP Servers**: 8 integrations (Context7, Sequential, Magic, Playwright, Morphllm, Serena, Tavily, Chrome DevTools)

---

## Core Architecture

### Context-Oriented Configuration

SuperClaude's architecture is built on a simple principle: **behavioral modification through structured context files**.

```
User Input
    ↓
Context Loading (CLAUDE.md imports)
    ↓
Command Detection (/sc:* pattern)
    ↓
Agent Activation (manual or auto)
    ↓
Mode Application (flags or triggers)
    ↓
MCP Tool Coordination
    ↓
Output Generation
```

### Directory Structure

```
~/.claude/
├── CLAUDE.md                   # Main context with @imports
├── FLAGS.md                    # Flag definitions
├── RULES.md                    # Core behavioral rules
├── PRINCIPLES.md               # Guiding principles
├── MODE_*.md                   # 7 behavioral modes
├── MCP_*.md                    # 8 MCP server integrations
├── agents/                     # 16 specialized agents
│   ├── pm-agent.md            # 🆕 Meta-layer orchestrator
│   ├── backend-architect.md
│   ├── frontend-architect.md
│   ├── security-engineer.md
│   └── ... (13 more)
└── commands/sc/               # 26 workflow commands
    ├── pm.md                  # 🆕 PM Agent command
    ├── implement.md
    ├── analyze.md
    └── ... (23 more)
```

---

## PM Agent Mode: The Meta-Layer

### Position in Architecture

PM Agent operates as a **meta-layer** above all other components:

```
┌─────────────────────────────────────────────┐
│         PM Agent Mode (Meta-Layer)          │
│   • Always Active (Session Start)           │
│   • Context Preservation                     │
│   • PDCA Self-Evaluation                     │
│   • Knowledge Management                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Specialist Agents (16)              │
│   backend-architect, security-engineer, etc. │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Commands & Modes                   │
│   /sc:implement, /sc:analyze, etc.          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│            MCP Tool Layer                    │
│   Context7, Sequential, Magic, etc.         │
└─────────────────────────────────────────────┘
```

### PM Agent Responsibilities

1. **Session Lifecycle Management**
   - Auto-activation at session start
   - Context restoration from Serena MCP memory
   - User report generation (前回/進捗/今回/課題)

2. **PDCA Cycle Execution**
   - Plan: Hypothesis generation
   - Do: Experimentation with checkpoints
   - Check: Self-evaluation
   - Act: Knowledge extraction

3. **Documentation Strategy**
   - Temporary documentation (`docs/temp/`)
   - Formal patterns (`docs/patterns/`)
   - Mistake records (`docs/mistakes/`)
   - Knowledge evolution to CLAUDE.md

4. **Sub-Agent Orchestration**
   - Auto-delegation to specialists
   - Context coordination
   - Quality gate validation
   - Progress monitoring

---

## Component Relationships

### Commands → Agents → Modes → MCP

```
User: "/sc:implement authentication" --security
         ↓
    [Command Layer]
    commands/sc/implement.md
         ↓
    [Agent Auto-Activation]
    agents/security-engineer.md
    agents/backend-architect.md
         ↓
    [Mode Application]
    MODE_Task_Management.md (TodoWrite)
         ↓
    [MCP Tool Coordination]
    Context7 (auth patterns)
    Sequential (complex analysis)
         ↓
    [PM Agent Meta-Layer]
    Document learnings → docs/patterns/
```

### Activation Flow

1. **Explicit Command**: User types `/sc:implement`
   - Loads `commands/sc/implement.md`
   - Activates related agents (backend-architect, etc.)

2. **Agent Activation**: `@agent-security` or auto-detected
   - Loads agent expertise context
   - May activate related MCP servers

3. **Mode Application**: `--brainstorm` flag or keywords
   - Modifies interaction style
   - Enables specific behaviors

4. **PM Agent Meta-Layer**: Always active
   - Monitors all interactions
   - Documents learnings
   - Preserves context across sessions

---

## Serena MCP Integration

### Memory Operations

Serena MCP provides semantic code analysis and session persistence through memory operations:

```
Session Start:
  PM Agent → list_memories()
  PM Agent → read_memory("pm_context")
  PM Agent → read_memory("last_session")
  PM Agent → read_memory("next_actions")
  PM Agent → Report to User

During Work (every 30min):
  PM Agent → write_memory("checkpoint", progress)
  PM Agent → write_memory("decision", rationale)

Session End:
  PM Agent → write_memory("last_session", summary)
  PM Agent → write_memory("next_actions", todos)
  PM Agent → write_memory("pm_context", complete_state)
```

### Memory Structure

```json
{
  "pm_context": {
    "project": "SuperClaude_Framework",
    "current_phase": "Phase 1: Documentation",
    "active_tasks": ["ARCHITECTURE.md", "ROADMAP.md"],
    "architecture": "Context-Oriented Configuration",
    "patterns": ["PDCA Cycle", "Session Lifecycle"]
  },
  "last_session": {
    "date": "2025-10-14",
    "accomplished": ["PM Agent mode design", "Salvaged implementations"],
    "issues": ["Serena MCP not configured"],
    "learned": ["Session Lifecycle pattern", "PDCA automation"]
  },
  "next_actions": [
    "Create docs/development/ structure",
    "Write ARCHITECTURE.md",
    "Configure Serena MCP server"
  ]
}
```

---

## PDCA Engine

### Continuous Improvement Cycle

```
┌─────────────┐
│    Plan     │ → write_memory("plan", goal)
│   (仮説)    │ → docs/temp/hypothesis-YYYY-MM-DD.md
└──────┬──────┘
       ↓
┌─────────────┐
│     Do      │ → TodoWrite tracking
│   (実験)    │ → write_memory("checkpoint", progress)
└──────┬──────┘ → docs/temp/experiment-YYYY-MM-DD.md
       ↓
┌─────────────┐
│   Check     │ → think_about_task_adherence()
│   (評価)    │ → think_about_whether_you_are_done()
└──────┬──────┘ → docs/temp/lessons-YYYY-MM-DD.md
       ↓
┌─────────────┐
│    Act      │ → Success: docs/patterns/[name].md
│   (改善)    │ → Failure: docs/mistakes/mistake-*.md
└──────┬──────┘ → Update CLAUDE.md
       ↓
   [Repeat]
```

### Documentation Evolution

```
Trial-and-Error (docs/temp/)
    ↓
Success → Formal Pattern (docs/patterns/)
    ↓
Accumulate Knowledge
    ↓
Extract Best Practices → CLAUDE.md (Global Rules)
```

```
Mistake Detection (docs/temp/)
    ↓
Root Cause Analysis → docs/mistakes/
    ↓
Prevention Checklist
    ↓
Update Anti-Patterns → CLAUDE.md
```

---

## Data Flow

### Session Lifecycle Data Flow

```
Session Start:
┌──────────────┐
│ Claude Code  │
│   Startup    │
└──────┬───────┘
       ↓
┌──────────────┐
│  PM Agent    │ list_memories()
│  Activation  │ read_memory("pm_context")
└──────┬───────┘
       ↓
┌──────────────┐
│   Serena     │ Return: pm_context,
│     MCP      │          last_session,
└──────┬───────┘          next_actions
       ↓
┌──────────────┐
│  Context     │ Restore project state
│ Restoration  │ Generate user report
└──────┬───────┘
       ↓
┌──────────────┐
│    User      │ 前回: [summary]
│   Report     │ 進捗: [status]
└──────────────┘ 今回: [actions]
                 課題: [blockers]
```

### Implementation Data Flow

```
User Request → PM Agent Analyzes
    ↓
PM Agent → Delegate to Specialist Agents
    ↓
Specialist Agents → Execute Implementation
    ↓
Implementation Complete → PM Agent Documents
    ↓
PM Agent → write_memory("checkpoint", progress)
PM Agent → docs/temp/experiment-*.md
    ↓
Success → docs/patterns/ | Failure → docs/mistakes/
    ↓
Update CLAUDE.md (if global pattern)
```

---

## Extension Points

### Adding New Components

#### 1. New Command
```markdown
File: ~/.claude/commands/sc/new-command.md
Structure:
  - Metadata (name, category, complexity)
  - Triggers (when to use)
  - Workflow Pattern (step-by-step)
  - Examples

Integration:
  - Auto-loads when user types /sc:new-command
  - Can activate related agents
  - PM Agent automatically documents usage patterns
```

#### 2. New Agent
```markdown
File: ~/.claude/agents/new-specialist.md
Structure:
  - Metadata (name, category)
  - Triggers (keywords, file types)
  - Behavioral Mindset
  - Focus Areas

Integration:
  - Auto-activates on trigger keywords
  - Manual activation: @agent-new-specialist
  - PM Agent orchestrates with other agents
```

#### 3. New Mode
```markdown
File: ~/.claude/MODE_NewMode.md
Structure:
  - Activation Triggers (flags, keywords)
  - Behavioral Modifications
  - Interaction Patterns

Integration:
  - Flag: --new-mode
  - Auto-activation on complexity threshold
  - Modifies all agent behaviors
```

#### 4. New MCP Server
```json
File: ~/.claude/.claude.json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["-y", "new-server-mcp@latest"]
    }
  }
}
```

```markdown
File: ~/.claude/MCP_NewServer.md
Structure:
  - Purpose (what this server provides)
  - Triggers (when to use)
  - Integration (how to coordinate with other tools)
```

### PM Agent Integration for Extensions

All new components automatically integrate with PM Agent meta-layer:

1. **Session Lifecycle**: New components' usage tracked across sessions
2. **PDCA Cycle**: Patterns extracted from new component usage
3. **Documentation**: Learnings automatically documented
4. **Orchestration**: PM Agent coordinates new components with existing ones

---

## Architecture Principles

### 1. Simplicity First
- No executing code, only context files
- No performance systems, only instructional patterns
- No detection engines, Claude Code does pattern matching

### 2. Context-Oriented
- Behavior modification through structured context
- Import system for modular context loading
- Clear trigger patterns for activation

### 3. Meta-Layer Design
- PM Agent orchestrates without interfering
- Specialist agents work transparently
- Users interact with cohesive system

### 4. Knowledge Accumulation
- Every experience generates learnings
- Mistakes documented with prevention
- Patterns extracted to reusable knowledge

### 5. Session Continuity
- Context preserved across sessions
- No re-explanation needed
- Seamless resumption from last checkpoint

---

## Technical Considerations

### Performance
- Framework is pure context (no runtime overhead)
- Token efficiency through dynamic MCP loading
- Strategic context caching for related phases

### Scalability
- Unlimited commands/agents/modes through context files
- Modular architecture supports independent development
- PM Agent meta-layer handles coordination complexity

### Maintainability
- Clear separation of concerns (Commands/Agents/Modes)
- Self-documenting through PDCA cycle
- Living documentation evolves with usage

### Extensibility
- Drop-in new contexts without code changes
- MCP servers add capabilities externally
- PM Agent auto-integrates new components

---

## Future Architecture

### Planned Enhancements

1. **Auto-Activation System**
   - PM Agent activates automatically at session start
   - No manual invocation needed

2. **Enhanced Memory Operations**
   - Full Serena MCP integration
   - Cross-project knowledge sharing
   - Pattern recognition across sessions

3. **PDCA Automation**
   - Automatic documentation lifecycle
   - AI-driven pattern extraction
   - Self-improving knowledge base

4. **Multi-Project Orchestration**
   - PM Agent coordinates across projects
   - Shared learnings and patterns
   - Unified knowledge management

---

## Summary

SuperClaude's architecture is elegantly simple: **structured context files** that Claude Code reads to adopt sophisticated behaviors. The addition of PM Agent mode as a meta-layer transforms this from a collection of tools into a **continuously learning, self-improving development platform**.

**Key Architectural Innovation**: PM Agent meta-layer provides:
- Always-active foundation layer
- Context preservation across sessions
- PDCA self-evaluation and learning
- Systematic knowledge management
- Seamless orchestration of specialist agents

This architecture enables SuperClaude to function as a **最高司令官 (Supreme Commander)** that orchestrates all development activities while continuously learning and improving from every interaction.

---

**Last Verified**: 2025-10-14
**Next Review**: 2025-10-21 (1 week)
**Version**: 4.1.5
