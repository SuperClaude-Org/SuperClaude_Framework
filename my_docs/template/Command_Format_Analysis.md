# Command Format Analysis

*This analysis is based on the actual content of `SuperClaude/Commands/implement.md`.*

A Command, like an Agent, has two parts: Frontmatter and Content.

---

### 1. Frontmatter Structure

```yaml
---
name: [command_name]
description: "[Brief description of the command's function]"
category: [Category, e.g., workflow]
complexity: [Complexity level, e.g., standard]
mcp-servers: [[List of relevant MCP servers]]
personas: [[List of relevant personas (agents)]]
---
```

-   `name`: The command name (without `/sc:`).
-   `description`: A description of the function.
-   `category`: The command's category.
-   `complexity`: The complexity level of the process.
-   `mcp-servers`: MCP servers that this command can integrate with.
-   `personas`: Expert agents that this command can activate for coordination.

### 2. Content Structure

```markdown
# /sc:[command_name] - [Full Command Name]

> [Context Framework Note - explains the purpose and activation method]

## Triggers
- A list of situations or requests that will trigger this command.

## Context Trigger Pattern
- A code block describing the full command pattern with its parameters.
- **Usage**: An explanation of how to use the command in practice.

## Behavioral Flow
- An ordered list (`1.`, `2.`, ...) describing the behavioral flow or main steps the AI will execute.
- Often includes additional bullet points explaining the key behaviors in more detail.

## MCP Integration
- Lists and explains how this command integrates with each MCP Server declared in the frontmatter.

## Tool Coordination
- Lists and explains the role of tools (Read, Write, Bash...) in the command's process.

## Key Patterns
- Describes the core behavioral patterns or logic that this command follows.

## Examples
- Provides examples of using the command in practice with different parameters.

## Boundaries
- **Will**: What this command will do.
- **Will Not**: What this command will not do.
```
