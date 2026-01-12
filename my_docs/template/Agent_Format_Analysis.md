# Agent Format Analysis

*This analysis is based on the actual content of `SuperClaude/Agents/python-expert.md`.*

An agent is defined in a Markdown file, which includes two main parts:

1.  **Frontmatter (Metadata):** Located at the top of the file, enclosed by `---`. This section contains metadata about the agent.
2.  **Content:** Follows the frontmatter, using Markdown headers (`#`, `##`) to structure the agent's behavior.

---

### 1. Frontmatter Structure

This section consists of `key: value` pairs that define the agent's properties.

```yaml
---
name: [agent-name-kebab-case]
description: "[A brief description of the agent's purpose]"
category: [Category, e.g., specialized]
tools: "[List of tools the agent might need, e.g., Read, Write, Bash]"
---
```

-   `name`: A unique identifier for the agent.
-   `description`: A single sentence describing the core function.
-   `category`: The agent's category (e.g., `specialized`, `general`).
-   `tools`: The tools this agent is permitted or should prefer to use.

### 2. Content Structure

This section defines the agent's detailed behavior.

```markdown
# [Full Agent Name]

## Triggers
- A list of situations or request types that will activate this agent. This is the condition for the AI to "select" this agent for a task.

## Behavioral Mindset
- A paragraph describing the agent's core mindset and working philosophy. This serves as the guiding principle for all actions.

## Focus Areas
- A list of the main areas of expertise the agent will focus on, often formatted with `**Area Name**: Description`.

## Key Actions
- An ordered list (`1.`, `2.`, ...) describing the standard workflow or action steps the agent will perform.

## Outputs
- A list of the specific types of products or results this agent produces.

## Boundaries
- This section clearly defines what the agent **will do** (`Will:`) and what it **will not do** (`Will Not:`). This is a very important constraint.
```
