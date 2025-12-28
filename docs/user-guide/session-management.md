# Session Management Guide

SuperClaude provides persistent session management through the Serena MCP server, enabling true context preservation across Claude Code conversations and long-term project continuity.

## Core Session Commands with Persistent Memory

### `/sc:load` - Context Loading with Persistent Memory
**Purpose**: Initialize session with project context and persistent memory from previous sessions  
**MCP Integration**: Triggers Serena MCP to read stored project memories  
**Syntax**: `/sc:load [project_path]`

**What Happens**:
- Serena MCP reads persistent memory files from previous sessions
- Project context is restored from stored memories
- Previous decisions, patterns, and progress are loaded
- Session state is initialized with historical context

**Use Cases**:
```bash
# Load existing project context from persistent memory
/sc:load src/

# Resume specific project work with full history
/sc:load "authentication-system"

# Initialize with codebase analysis and previous insights
/sc:load . --analyze
```

### `/sc:save` - Session Persistence to Memory
**Purpose**: Save current session state and decisions to persistent memory  
**MCP Integration**: Triggers Serena MCP to write memory files  
**Syntax**: `/sc:save "session_description"`

**What Happens**:
- Current context and decisions are written to Serena memory
- Project state and progress are persisted across conversations
- Key insights and patterns are stored for future sessions
- Session summary is created with timestamp for retrieval

**Use Cases**:
```bash
# Save completed feature work for future reference
/sc:save "user authentication implemented with JWT"

# Checkpoint during complex work
/sc:save "API design phase complete, ready for implementation"

# Store architectural decisions permanently
/sc:save "microservices architecture decided, service boundaries defined"
```

### `/sc:reflect` - Progress Assessment with Memory Context
**Purpose**: Analyze current progress against stored memories and validate session completeness  
**MCP Integration**: Uses Serena MCP to compare current state against stored memories  
**Syntax**: `/sc:reflect [--scope project|session]`

**What Happens**:
- Serena MCP reads previous memories and current context
- Progress is assessed against stored goals and milestones  
- Gaps and next steps are identified using historical context
- Session completeness is validated against project memory

**Use Cases**:
```bash
# Assess project progress against stored milestones
/sc:reflect --scope project

# Validate current session completeness
/sc:reflect

# Check if ready to move to next phase based on memory
/sc:reflect --scope session
```

## Persistent Memory Architecture

### How Serena MCP Enables True Persistence

**Memory Storage**:
- Session contexts stored as structured memory files
- Project decisions and architectural patterns preserved permanently
- Code analysis results and insights retained across conversations
- Progress tracking and milestone data maintained long-term

**Cross-Session Continuity**:
- Previous session context automatically available in new conversations
- Decisions and rationale preserved and accessible across conversations
- Learning from past patterns and solutions maintained
- Consistent project understanding maintained indefinitely

**Memory Types**:
- **Project Memories**: Long-term project context and architecture
- **Session Memories**: Specific conversation outcomes and decisions  
- **Pattern Memories**: Reusable solutions and architectural patterns
- **Progress Memories**: Milestone tracking and completion status

## Session Lifecycle Patterns with Persistence

### New Project Initialization
```bash
# 1. Start fresh project
/sc:brainstorm "e-commerce platform requirements"

# 2. Save initial decisions to persistent memory
/sc:save "project scope and requirements defined"

# 3. Begin implementation planning
/sc:workflow "user authentication system"

# 4. Save architectural decisions permanently
/sc:save "auth architecture: JWT + refresh tokens + rate limiting"
```

### Resuming Existing Work (Cross-Conversation)
```bash
# 1. Load previous context from persistent memory
/sc:load "e-commerce-project"

# 2. Assess current state against stored progress
/sc:reflect --scope project  

# 3. Continue with next phase using stored context
/sc:implement "payment processing integration"

# 4. Save progress checkpoint to memory
/sc:save "payment system integrated with Stripe API"
```

### Long-Term Project Management
```bash
# Weekly checkpoint pattern with persistence
/sc:load project-name
/sc:reflect --scope project
# ... work on features ...
/sc:save "week N progress: features X, Y, Z completed"

# Phase completion pattern with memory
/sc:reflect --scope project
/sc:save "Phase 1 complete: core authentication and user management"
/sc:workflow "Phase 2: payment and order processing"
```

## Cross-Conversation Continuity

### Starting New Conversations with Persistence

When starting a new Claude Code conversation, the persistent memory system allows:

1. **Automatic Context Restoration**
   ```bash
   /sc:load project-name
   # Automatically restores all previous context, decisions, and progress
   ```

2. **Progress Continuation**
   - Previous session decisions are immediately available
   - Architectural patterns and code insights are preserved
   - Project history and rationale are maintained

3. **Intelligent Context Building**
   - Serena MCP provides relevant memories based on current work
   - Past solutions and patterns inform new implementations
   - Project evolution is tracked and understood

### Memory Optimization

**Effective Memory Usage**:
- Use descriptive, searchable memory names
- Include project phase and timestamp context
- Reference specific features or architectural decisions
- Make future retrieval intuitive

**Memory Content Strategy**:
- Store decisions and rationale, not just outcomes
- Include alternative approaches considered
- Document integration patterns and dependencies
- Preserve learning and insights for future reference

**Memory Lifecycle Management**:
- Regular cleanup of outdated memories
- Consolidation of related session memories
- Archiving of completed project phases
- Pruning of obsolete architectural decisions

## Best Practices for Persistent Sessions

### Session Start Protocol
1. Always begin with `/sc:load` for existing projects
2. Use `/sc:reflect` to understand current state from memory
3. Plan work based on persistent context and stored patterns
4. Build on previous decisions and architectural choices

### Session End Protocol
1. Use `/sc:reflect` to assess completeness against stored goals
2. Save key decisions with `/sc:save` for future sessions
3. Document next steps and open questions in memory
4. Preserve context for seamless future continuation

### Memory Quality Maintenance
- Use clear, descriptive memory names for easy retrieval
- Include context about decisions and alternative approaches
- Reference specific code locations and patterns
- Maintain consistency in memory structure across sessions

## Integration with Other SuperClaude Features

### MCP Server Coordination
- **Serena MCP**: Provides the persistent memory infrastructure
- **Sequential MCP**: Uses stored memories for enhanced complex analysis
- **Context7 MCP**: References stored patterns and documentation approaches
- **Morphllm MCP**: Applies stored refactoring patterns consistently

### Agent Collaboration with Memory
- Agents access persistent memories for enhanced context
- Previous specialist decisions are preserved and referenced
- Cross-session agent coordination through shared memory
- Consistent specialist recommendations based on project history

### Command Integration with Persistence
- All `/sc:` commands can reference and build on persistent context
- Previous command outputs and decisions are available across sessions
- Workflow patterns are stored and reusable
- Implementation history guides future command decisions

## Troubleshooting Persistent Sessions

### Common Issues

**Memory Not Loading**:
- Verify Serena MCP is configured and running properly
- Check memory file permissions and accessibility
- Ensure consistent project naming conventions
- Validate memory file integrity and format

**Context Loss Between Sessions**:  
- Always use `/sc:save` before ending sessions
- Use descriptive memory names for easy retrieval
- Regular `/sc:reflect` to validate memory completeness
- Backup important memory files periodically

**Memory Conflicts**:
- Use timestamped memory names for version control
- Regular cleanup of obsolete memories
- Clear separation between project and session memories
- Consistent memory naming conventions across sessions

### Quick Fixes

**Reset Session State**:
```bash
/sc:load --fresh  # Start without previous context
/sc:reflect       # Assess current state
```

**Memory Cleanup**:
```bash
/sc:reflect --cleanup  # Remove obsolete memories
/sc:save --consolidate # Merge related memories
```

**Context Recovery**:
```bash
/sc:load --recent     # Load most recent memories
/sc:reflect --repair  # Identify and fix context gaps
```

## Advanced Persistent Session Patterns

### Multi-Phase Projects
- Use phase-specific memory naming for organization
- Maintain architectural decision continuity across phases
- Cross-phase dependency tracking through persistent memory
- Progressive complexity management with historical context

### Team Collaboration
- Shared memory conventions and naming standards
- Decision rationale preservation for team context
- Integration pattern documentation accessible to all team members
- Consistent code style and architecture enforcement through memory

### Long-Term Maintenance
- Memory archiving strategies for completed projects
- Pattern library development through accumulated memories
- Reusable solution documentation built over time
- Knowledge base building through persistent memory accumulation

## Key Benefits of Persistent Session Management

### Project Continuity
- Seamless work continuation across multiple conversations
- No context loss between Claude Code sessions
- Preserved architectural decisions and technical rationale
- Long-term project evolution tracking

### Enhanced Productivity
- Reduced need to re-explain project context
- Faster startup time for continued work
- Building on previous insights and patterns
- Cumulative project knowledge growth

### Quality Consistency
- Consistent architectural patterns across sessions
- Preserved code quality decisions and standards
- Reusable solutions and best practices
- Maintained technical debt awareness

---

**Key Takeaway**: Session management through Serena MCP transforms SuperClaude from single-conversation assistance to persistent project partnership, maintaining context, decisions, and learning across all development phases and Claude Code conversations.