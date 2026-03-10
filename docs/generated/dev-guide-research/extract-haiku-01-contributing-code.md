# Extraction: Developing custom commands, skills, or agents (SuperClaude)

**Source file:** `/config/workspace/SuperClaude_Framework/docs/developer-guide/contributing-code.md`

> Extraction scope: ALL information pertaining to developing custom commands, skills, or agents for the SuperClaude framework, including templates/structures, file organization patterns, frontmatter/metadata requirements, trigger definitions, behavioral specifications, MCP integration patterns, and testing/validation approaches.

---

## 1) Where components live (file organization patterns)

### 1.1 Framework structure (source of truth)

Exact quote:

```text
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

### 1.2 What “agents”, “commands”, and “modes” are

Exact quotes:

- “**Context Files**: .md instruction files that guide Claude Code behavior”
- “**Agents**: Domain specialists (e.g., security-engineer.md, python-expert.md)”
- “**Commands**: Workflow patterns (e.g., implement.md, analyze.md)”
- “**Modes**: Interaction modifiers (e.g., brainstorming, introspection)”
- “**MCP Integration**: Configuration for Model Context Protocol servers”

---

## 2) Custom Agents: templates, metadata/frontmatter, triggers, behaviors

### 2.1 Agent development process

Exact quote:

“**Agent Development Process:**
1. Identify domain expertise gap
2. Create agent file in `superclaude/Agents/`
3. Define triggers, behaviors, and boundaries
4. Test with various Claude Code scenarios
5. Document usage patterns and examples”

### 2.2 Example agent structure (minimal section layout + frontmatter)

Exact quote (template):

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

This provides:
- **Frontmatter fields**: `name`, `description`, `category`
- **Required sections** (suggested): Triggers, Behavioral Mindset, Focus Areas, Key Actions
- **Trigger definitions**: keywords and file types

### 2.3 Agent template (expanded, includes tools + complexity indicators)

Exact quote (template):

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

Key extracted requirements/specifications:
- **Frontmatter fields**: `name`, `description`, `category`, `tools`
- **Trigger types**: keywords, file patterns, complexity indicators
- **Behavioral specs**: best practices + systematic approach + quality/security considerations
- **Integration behavior**: “Coordinate with related specialists”
- **Validation expectation**: “Validate solutions meet domain standards”

---

## 3) Custom Commands: templates, metadata/frontmatter, triggers, MCP integration

### 3.1 Command structure (frontmatter + required sections)

Exact quote (template):

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

Extracted requirements/specifications:
- **Frontmatter fields**:
  - `name`
  - `description`
  - `category: workflow|utility|analysis`
  - `complexity: basic|standard|advanced`
  - `mcp-servers: [context7, sequential]` (MCP server integration pattern)
  - `personas: [architect, engineer]` (persona integration pattern)
- **Trigger definitions**:
  - “When to use this command”
  - “Context indicators”
- **Behavioral / workflow specification**:
  - “Initial analysis” → “Processing steps” → “Validation and output”
- **Usage rule**:
  - “Type in Claude Code conversation”
  - “**Note**: This is a context trigger pattern, not a terminal command.”

### 3.2 How commands integrate with agents + MCP servers (example flow)

Exact quotes (How It Works):

1) “User types `/sc:implement "auth system"` **in Claude Code conversation** (not terminal)”

2) “Claude Code reads `superclaude/Commands/implement.md`”

3) “Command activates security-engineer agent context”

4) “Context7 MCP provides authentication patterns”

5) “Claude generates complete, secure implementation”

This is a concrete **integration pattern**:
- Command → reads command context file → activates agent context → uses MCP server → produces output

---

## 4) Custom Modes (behavioral modification patterns)

### 4.1 Mode development checklist

Exact quote:

“**Mode Development:**
- Define activation triggers
- Specify behavioral modifications
- Create interaction patterns
- Test across different Claude Code scenarios”

(While this is not a “skill”, it is part of the same context-file extension mechanism and is explicitly listed under “Contributing to Components”.)

---

## 5) Skills: what the source describes (and what it does not)

The source file explicitly covers **Agents**, **Commands**, and **Modes** as component types, but it does **not** define a “Skills” directory, a skill template, or skill-specific frontmatter requirements.

What it does say that’s relevant to skills (as context files):
- “**Context Files**: .md instruction files that guide Claude Code behavior”
- “Use frontmatter metadata for configuration”
- “Follow existing patterns and naming conventions”
- “Test instructions produce expected behaviors”

No additional skill-specific structure is provided in this source.

---

## 6) Triggers & behavioral specs (cross-cutting standards)

### 6.1 Context file standards (applies to agents/commands/modes)

Exact quotes:

**Structure Requirements:**
- “Clear, actionable instructions for Claude Code”
- “Specific triggers and activation patterns”
- “Examples demonstrating usage”
- “Boundaries defining scope”

**Quality Standards:**
- “Instructions are testable in Claude Code conversations”
- “Examples produce expected behavioral changes”
- “Clear activation triggers and context patterns”
- “Professional language and formatting”

---

## 7) MCP server integration patterns (explicit + implied)

### 7.1 Frontmatter-driven MCP server selection (commands)

Exact quote (command template frontmatter field):

```yaml
mcp-servers: [context7, sequential]
```

### 7.2 Example of MCP usage in a workflow

Exact quote:

- “Context7 MCP provides authentication patterns”

---

## 8) Testing, validation, and verification approaches

### 8.1 Manual validation process

Exact quote:

“**Manual Validation Process:**
1. Install development version in Claude Code
2. Test agent/command activation triggers in Claude Code conversations
3. Verify behavioral modifications occur as expected
4. Validate context file structure and formatting
5. Test edge cases and error conditions”

### 8.2 Validation checklist

Exact quote:

“**Validation Checklist:**
- [ ] Context files use valid markdown syntax
- [ ] Triggers activate correctly in Claude Code
- [ ] Behavior matches documentation
- [ ] No conflicts with existing components
- [ ] Examples produce expected results in Claude Code conversations”

### 8.3 File structure validation (commands shown in guide)

Exact quote:

```bash
# Check file structure
find ~/.claude -name "*.md" | head -10

# Verify context file format
head ~/.claude/agents/python-expert.md

# Test import system
grep "@import" ~/.claude/CLAUDE.md
```

---

## 9) Contribution workflow notes that impact custom component development

### 9.1 PR testing expectations (useful for component dev)

Exact quote (PR template section):

```markdown
## Testing
- [ ] Manual testing with Claude Code
- [ ] Context file validation passes
- [ ] Examples validated in Claude Code conversations
```

### 9.2 Manual review focus areas (what reviewers look for)

Exact quote:

“**Manual Review:**
- Context file clarity and effectiveness
- Agent/command logic and triggers
- Documentation accuracy and completeness
- Integration with existing components
- Claude Code behavioral testing results”
