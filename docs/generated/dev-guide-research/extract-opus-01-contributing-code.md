# Extraction: Contributing Code Guide -- Custom Commands, Skills, and Agents

**Source**: `/config/workspace/SuperClaude_Framework/docs/developer-guide/contributing-code.md`
**Extracted**: 2026-02-21
**Focus**: All information pertaining to developing custom commands, skills, or agents

---

## 1. Framework Architecture Context

The document establishes SuperClaude as a **Context-Oriented Configuration Framework** -- not executing software, but instruction files that Claude Code reads to modify its behavior.

> "SuperClaude is a **Context-Oriented Configuration Framework** - not executing software, but instruction files that Claude Code reads to modify its behavior."

### Key Concepts (Exact Quote)

> - **Context Files**: .md instruction files that guide Claude Code behavior
> - **Agents**: Domain specialists (e.g., security-engineer.md, python-expert.md)
> - **Commands**: Workflow patterns (e.g., implement.md, analyze.md)
> - **Modes**: Interaction modifiers (e.g., brainstorming, introspection)
> - **MCP Integration**: Configuration for Model Context Protocol servers

---

## 2. Directory Structure and File Placement Rules

The documented framework structure:

```
SuperClaude_Framework/
├── superclaude/           # Framework components (the source of truth)
│   ├── Core/             # PRINCIPLES.md, RULES.md, FLAGS.md
│   ├── Agents/           # 15 specialized domain experts
│   ├── Commands/         # 21 context trigger patterns (/sc: behavioral instructions)
│   ├── Modes/            # 6 behavioral modification patterns
│   └── MCP/              # 6 MCP server configurations
├── setup/                # Python installation system
├── docs/                 # Documentation (what you're reading)
└── tests/                # File validation scripts
```

### Placement Rules

- New agents go in: `superclaude/Agents/`
- New commands go in: `superclaude/Commands/`
- New modes go in: `superclaude/Modes/`
- MCP configurations go in: `superclaude/MCP/`

**Note**: The CLAUDE.md in the project root describes a newer v4.2.0 architecture where the source of truth is `src/superclaude/` with subdirectories `agents/`, `commands/`, `skills/`. The contributing guide references the older `superclaude/Agents/`, `superclaude/Commands/` paths. Both should be considered.

---

## 3. Agent Development

### Agent Development Process (Exact Quote)

> **Agent Development Process:**
> 1. Identify domain expertise gap
> 2. Create agent file in `superclaude/Agents/`
> 3. Define triggers, behaviors, and boundaries
> 4. Test with various Claude Code scenarios
> 5. Document usage patterns and examples

### Agent Template (Full -- Exact Quote)

```markdown
---
name: agent-name
description: Domain expertise description
category: specialized
tools: Read, Write, Edit, Bash
---

# Agent Name

## Triggers
- Specific keywords: domain, expertise, area
- File patterns: *.domain, specific frameworks
- Complexity indicators: architectural decisions

## Behavioral Mindset
- Focus on domain best practices
- Systematic approach to problem-solving
- Quality and security considerations

## Focus Areas
- Core domain expertise
- Related technical areas
- Integration patterns

## Key Actions
1. Analyze requirements within domain context
2. Apply domain-specific best practices
3. Coordinate with related specialists
4. Validate solutions meet domain standards
```

### Agent Frontmatter/Metadata Requirements

Required fields in the YAML frontmatter:

| Field | Description | Example Values |
|-------|-------------|----------------|
| `name` | Agent identifier (kebab-case) | `agent-name`, `new-specialist` |
| `description` | Brief description of expertise | `"Domain expertise description"` |
| `category` | Classification | `specialized`, `architecture`, `quality` |
| `tools` | Available tools | `Read, Write, Edit, Bash` |

### Agent Sections

An agent file must contain these sections:

1. **Triggers** -- Keywords, file patterns, and complexity indicators that activate the agent
2. **Behavioral Mindset** -- Core philosophy and approach
3. **Focus Areas** -- Domain expertise areas
4. **Key Actions** -- Specific behavior patterns and problem-solving approaches

### Earlier/Simpler Agent Structure Example

The document also provides a simpler agent structure earlier in the file:

```markdown
---
name: new-specialist
description: Brief description of expertise
category: specialized|architecture|quality
---

# Agent Name

## Triggers
- Keywords that activate this agent
- File types that trigger activation

## Behavioral Mindset
Core philosophy and approach

## Focus Areas
- Domain expertise area 1
- Domain expertise area 2

## Key Actions
1. Specific behavior pattern
2. Problem-solving approach
```

---

## 4. Command Development

### Command Template (Full -- Exact Quote)

```markdown
---
name: command-name
description: Command purpose
category: workflow|utility|analysis
complexity: basic|standard|advanced
mcp-servers: [context7, sequential]
personas: [architect, engineer]
---

# /sc:command-name

## Triggers
- When to use this command
- Context indicators

## Usage
Type in Claude Code conversation:
```
/sc:command-name [target] [--options]
```
**Note**: This is a context trigger pattern, not a terminal command.

## Workflow Pattern
1. Initial analysis
2. Processing steps
3. Validation and output

## Examples
Practical usage examples
```

### Command Frontmatter/Metadata Requirements

Required fields in the YAML frontmatter:

| Field | Description | Example Values |
|-------|-------------|----------------|
| `name` | Command identifier (kebab-case) | `command-name` |
| `description` | Command purpose | `"Command purpose"` |
| `category` | Classification | `workflow`, `utility`, `analysis` |
| `complexity` | Complexity tier | `basic`, `standard`, `advanced` |
| `mcp-servers` | MCP server integrations (array) | `[context7, sequential]` |
| `personas` | Associated personas (array) | `[architect, engineer]` |

### Command Sections

A command file must contain these sections:

1. **Triggers** -- When to use the command and context indicators
2. **Usage** -- How to invoke the command in Claude Code conversation
3. **Workflow Pattern** -- Step-by-step processing logic
4. **Examples** -- Practical usage examples

### MCP Server Integration in Commands

Commands declare MCP server dependencies in frontmatter via the `mcp-servers` field. The execution flow described:

> 1. User types `/sc:implement "auth system"` **in Claude Code conversation** (not terminal)
> 2. Claude Code reads `superclaude/Commands/implement.md`
> 3. Command activates security-engineer agent context
> 4. Context7 MCP provides authentication patterns
> 5. Claude generates complete, secure implementation

---

## 5. Mode Development

### Mode Development Guidelines (Exact Quote)

> **Mode Development:**
> - Define activation triggers
> - Specify behavioral modifications
> - Create interaction patterns
> - Test across different Claude Code scenarios

No formal template is provided for modes in this document.

---

## 6. Skills

The contributing guide does **not** provide a dedicated template or section for skills. Skills are mentioned only in the project-level CLAUDE.md (v4.2.0 architecture) as:

- Installed via `superclaude install`
- Located in `src/superclaude/skills/` (source) and `.claude/skills/` (dev copies)
- Structured as directories containing `SKILL.md` + `rules/` + `templates/` + `scripts/`

This is a gap in the contributing guide -- no skill development template or process is documented there.

---

## 7. Naming Conventions

From the templates and examples:

- **Agent files**: kebab-case naming (e.g., `security-engineer.md`, `python-expert.md`, `new-specialist.md`)
- **Command files**: kebab-case naming matching command name (e.g., `implement.md`, `analyze.md`)
- **Frontmatter `name` field**: kebab-case (e.g., `agent-name`, `command-name`)
- **Category values**: lowercase, pipe-separated options in templates (e.g., `specialized|architecture|quality`)
- **Command invocation prefix**: `/sc:` (e.g., `/sc:command-name`)

---

## 8. Testing and Validation

### Manual Validation Process (Exact Quote)

> **Manual Validation Process:**
> 1. Install development version in Claude Code
> 2. Test agent/command activation triggers in Claude Code conversations
> 3. Verify behavioral modifications occur as expected
> 4. Validate context file structure and formatting
> 5. Test edge cases and error conditions

### Validation Checklist (Exact Quote)

> - [ ] Context files use valid markdown syntax
> - [ ] Triggers activate correctly in Claude Code
> - [ ] Behavior matches documentation
> - [ ] No conflicts with existing components
> - [ ] Examples produce expected results in Claude Code conversations

### File Structure Validation Commands

```bash
# Check file structure
find ~/.claude -name "*.md" | head -10

# Verify context file format
head ~/.claude/agents/python-expert.md

# Test import system
grep "@import" ~/.claude/CLAUDE.md
```

### PR Testing Checklist (Exact Quote)

> ## Testing
> - [ ] Manual testing with Claude Code
> - [ ] Context file validation passes
> - [ ] Examples validated in Claude Code conversations

---

## 9. Context File Standards

### Structure Requirements (Exact Quote)

> **Structure Requirements:**
> - Clear, actionable instructions for Claude Code
> - Specific triggers and activation patterns
> - Examples demonstrating usage
> - Boundaries defining scope

### Quality Standards (Exact Quote)

> **Quality Standards:**
> - Instructions are testable in Claude Code conversations
> - Examples produce expected behavioral changes
> - Clear activation triggers and context patterns
> - Professional language and formatting

### General Context File Guidelines (Exact Quote)

> **Context Files (`.md`):**
> - Write clear, actionable instructions for Claude Code
> - Use frontmatter metadata for configuration
> - Follow existing patterns and naming conventions
> - Test instructions produce expected behaviors

---

## 10. Contributing Do's and Don'ts

### Do's (Exact Quote)

> - **Follow existing patterns and conventions**
> - **Test context files thoroughly with Claude Code**
> - **Write clear, actionable behavioral instructions**
> - **Provide working examples**
> - **Focus on user experience improvements**
> - **Coordinate with related components**

### Don'ts (Exact Quote)

> - **Don't break existing functionality**
> - **Don't add untested context modifications**
> - **Don't ignore style guidelines**
> - **Don't create overly complex behavioral patterns**
> - **Don't duplicate existing functionality**

---

## 11. Quality Standards Summary

### For Context Files (Exact Quote)

> - Clear activation triggers
> - Specific behavioral instructions
> - Practical examples
> - Defined scope boundaries

### For Documentation (Exact Quote)

> - Accurate and up-to-date
> - Working context examples
> - Clear navigation structure
> - Accessibility considerations

---

## 12. Gaps and Observations

1. **No skill template**: The contributing guide lacks a template or process for developing skills, despite skills being a first-class component in the v4.2.0 architecture.
2. **Directory path discrepancy**: The guide references `superclaude/Agents/` and `superclaude/Commands/` while the project CLAUDE.md uses `src/superclaude/agents/` and `src/superclaude/commands/`. Both may be valid depending on version.
3. **No automated testing**: All validation is described as manual (testing in Claude Code conversations). No automated test framework for context files is documented.
4. **No MCP integration patterns for agents**: While commands have an `mcp-servers` frontmatter field, agents do not -- despite the PERSONAS.md defining MCP preferences per persona.
5. **Mode template missing**: Modes only get bullet-point guidance, no formal template like agents and commands receive.
