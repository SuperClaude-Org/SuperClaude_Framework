---
name: load
description: "Session lifecycle management with Serena MCP integration for project context loading"
category: session
complexity: standard
mcp-servers: [serena]
personas: []
---

# /sc:load - Project Context Loading

## Triggers
- Session initialization and project context loading requests
- Cross-session persistence and memory retrieval needs
- Project activation and context management requirements
- Session lifecycle management and checkpoint loading scenarios

## Usage
```
/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze] [--bluelink]
```

**`--bluelink`** *(optional)*: also query the Bluelink MCP knowledge base for docs relevant to the
project being loaded — its service meta-spec, architecture, dependencies, and standards — and inject
that need-to-know context into the session alongside Serena memory. **Invoked only when
`--bluelink` is explicitly passed — never auto-activated, and not enabled by `--all-mcp`.** Requires
a configured Bluelink server (see `mcp/MCP_Bluelink.md`); degrades gracefully if unavailable.

## Behavioral Flow
1. **Initialize**: Establish Serena MCP connection and session context management
2. **Discover**: Analyze project structure and identify context loading requirements
3. **Load**: Retrieve project memories, checkpoints, and cross-session persistence data
4. **Activate**: Establish project context and prepare for development workflow
5. **Validate**: Ensure loaded context integrity and session readiness

Key behaviors:
- Serena MCP integration for memory management and cross-session persistence
- Project activation with comprehensive context loading and validation
- Performance-critical operation with <500ms initialization target
- Session lifecycle management with checkpoint and memory coordination

## MCP Integration
- **Serena MCP**: Mandatory integration for project activation, memory retrieval, and session management
- **Memory Operations**: Cross-session persistence, checkpoint loading, and context restoration
- **Performance Critical**: <200ms for core operations, <1s for checkpoint creation
- **Bluelink MCP** *(optional, `--bluelink` only)*: query the internal KB for context relevant to
  this repository (service meta-spec, architecture, dependencies, standards) and inject the
  need-to-know subset into session context. Read-only. **Manual-only — invoked solely via
  `--bluelink`; never auto-activated; not part of `--all-mcp`.** Auto-degrades if unavailable.

## Tool Coordination
- **activate_project**: Core project activation and context establishment
- **list_memories/read_memory**: Memory retrieval and session context loading
- **Read/Grep/Glob**: Project structure analysis and configuration discovery
- **Write**: Session context documentation and checkpoint creation

## Key Patterns
- **Project Activation**: Directory analysis → memory retrieval → context establishment
- **Session Restoration**: Checkpoint loading → context validation → workflow preparation
- **Memory Management**: Cross-session persistence → context continuity → development efficiency
- **Performance Critical**: Fast initialization → immediate productivity → session readiness

## Examples

### Basic Project Loading
```
/sc:load
# Loads current directory project context with Serena memory integration
# Establishes session context and prepares for development workflow
```

### Specific Project Loading
```
/sc:load /path/to/project --type project --analyze
# Loads specific project with comprehensive analysis
# Activates project context and retrieves cross-session memories
```

### Checkpoint Restoration
```
/sc:load --type checkpoint --checkpoint session_123
# Restores specific checkpoint with session context
# Continues previous work session with full context preservation
```

### Dependency Context Loading
```
/sc:load --type deps --refresh
# Loads dependency context with fresh analysis
# Updates project understanding and dependency mapping
```

## Boundaries

**Will:**
- Load project context using Serena MCP integration for memory management
- Provide session lifecycle management with cross-session persistence
- Establish project activation with comprehensive context loading

**Will Not:**
- Modify project structure or configuration without explicit permission
- Load context without proper Serena MCP integration and validation
- Override existing session context without checkpoint preservation