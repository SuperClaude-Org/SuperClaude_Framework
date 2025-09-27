# MCP Format Analysis

*This analysis is based on the actual content of `SuperClaude/MCP/MCP_Context7.md`.*

Like `Modes`, an `MCP` file does not have a Frontmatter section and focuses entirely on the Markdown content to define its behavior.

---

### Content Structure

```markdown
# [MCP Server Name]

**Purpose**: [Describes the main purpose of this MCP server in one sentence.]

## Triggers
- A list of keywords, commands (e.g., `import`), or specific situations that will trigger or suggest the use of this MCP server.

## Choose When
- Provides specific guidance on when to prioritize using this MCP over other tools (like web search or the AI's native knowledge).
- Lists ideal use cases.

## Works Best With
- Describes how this MCP server coordinates with other MCP servers or system components to create an effective workflow.

## Examples
- Provides examples of user prompts or requests and the resulting activation of this MCP server, sometimes with a comparison to not using it.
```

In summary, an MCP file defines a "protocol" or a "specialized server" that the AI can "call" to handle a specific type of task, such as looking up official documentation (Context7). It specifies when to call it, how to coordinate, and the expected result.
