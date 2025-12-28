# Serena MCP Server

**Purpose**: Semantic code understanding with project memory and session persistence

## Triggers
- Symbol operations: rename, extract, move functions/classes
- Project-wide code navigation and exploration
- Multi-language projects requiring LSP integration
- Session lifecycle: `/sc:load`, `/sc:save`, project activation
- Memory-driven development workflows
- Large codebase analysis (>50 files, complex architecture)

## Choose When
- **Over Morphllm**: For symbol operations, not pattern-based edits
- **For semantic understanding**: Symbol references, dependency tracking, LSP integration
- **For session persistence**: Project context, memory management, cross-session learning
- **For large projects**: Multi-language codebases requiring architectural understanding
- **Not for simple edits**: Basic text replacements, style enforcement, bulk operations

## Works Best With
- **Morphllm**: Serena analyzes semantic context → Morphllm executes precise edits
- **Sequential**: Serena provides project context → Sequential performs architectural analysis

## Examples
```
"rename getUserData function everywhere" → Serena (symbol operation with dependency tracking)
"find all references to this class" → Serena (semantic search and navigation)
"load my project context" → Serena (/sc:load with project activation)
"save my current work session" → Serena (/sc:save with memory persistence)
"update all console.log to logger" → Morphllm (pattern-based replacement)
"create a login form" → Magic (UI component generation)
```