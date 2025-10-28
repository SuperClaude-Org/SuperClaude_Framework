# Serena MCP Research Report
**Date**: 2025-01-16
**Research Depth**: Deep
**Confidence Level**: High (90%)

## Executive Summary

PM Agent documentation references Serena MCP for memory management, but the actual implementation uses repository-scoped local files instead. This creates a documentation-reality mismatch that needs resolution.

**Key Finding**: Serena MCP exposes **NO resources**, only **tools**. The attempted `ReadMcpResourceTool` call with `serena://memories` URI failed because Serena doesn't expose MCP resources.

---

## 1. Serena MCP Architecture

### 1.1 Core Components

**Official Repository**: https://github.com/oraios/serena (9.8k stars, MIT license)

**Purpose**: Semantic code analysis toolkit with LSP integration, providing:
- Symbol-level code comprehension
- Multi-language support (25+ languages)
- Project-specific memory management
- Advanced code editing capabilities

### 1.2 MCP Server Capabilities

**Tools Exposed** (25+ tools):
```yaml
Memory Management:
  - write_memory(memory_name, content, max_answer_chars=200000)
  - read_memory(memory_name)
  - list_memories()
  - delete_memory(memory_name)

Thinking Tools:
  - think_about_collected_information()
  - think_about_task_adherence()
  - think_about_whether_you_are_done()

Code Operations:
  - read_file, get_symbols_overview, find_symbol
  - replace_symbol_body, insert_after_symbol
  - execute_shell_command, list_dir, find_file

Project Management:
  - activate_project(path)
  - onboarding()
  - get_current_config()
  - switch_modes()
```

**Resources Exposed**: **NONE**
- Serena provides tools only
- No MCP resource URIs available
- Cannot use ReadMcpResourceTool with Serena

### 1.3 Memory Storage Architecture

**Location**: `.serena/memories/` (project-specific directory)

**Storage Format**: Markdown files (human-readable)

**Scope**: Per-project isolation via project activation

**Onboarding**: Automatic on first run to build project understanding

---

## 2. Best Practices for Serena Memory Management

### 2.1 Session Persistence Pattern (Official)

**Recommended Workflow**:
```yaml
Session End:
  1. Create comprehensive summary:
     - Current progress and state
     - All relevant context for continuation
     - Next planned actions

  2. Write to memory:
     write_memory(
       memory_name="session_2025-01-16_auth_implementation",
       content="[detailed summary in markdown]"
     )

Session Start (New Conversation):
  1. List available memories:
     list_memories()

  2. Read relevant memory:
     read_memory("session_2025-01-16_auth_implementation")

  3. Continue task with full context restored
```

### 2.2 Known Issues (GitHub Discussion #297)

**Problem**: "Broken code when starting a new session" after continuous iterations

**Root Causes**:
- Context degradation across sessions
- Type confusion in multi-file changes
- Duplicate code generation
- Memory overload from reading too much content

**Workarounds**:
1. **Compilation Check First**: Always run build/type-check before starting work
2. **Read Before Write**: Examine complete file content before modifications
3. **Type-First Development**: Define TypeScript interfaces before implementation
4. **Session Checkpoints**: Create detailed documentation between sessions
5. **Strategic Session Breaks**: Start new conversation when close to context limits

### 2.3 General MCP Memory Best Practices

**Duplicate Prevention**:
- Require verification before writing
- Check existing memories first

**Session Management**:
- Read memory after session breaks
- Write comprehensive summaries before ending

**Storage Strategy**:
- Short-term state: Token-passing
- Persistent memory: External storage (Serena, Redis, SQLite)

---

## 3. Current PM Agent Implementation Analysis

### 3.1 Documentation vs Reality

**Documentation Says** (pm.md lines 34-57):
```yaml
Session Start Protocol:
  1. Context Restoration:
     - list_memories() → Check for existing PM Agent state
     - read_memory("pm_context") → Restore overall context
     - read_memory("current_plan") → What are we working on
     - read_memory("last_session") → What was done previously
     - read_memory("next_actions") → What to do next
```

**Reality** (Actual Implementation):
```yaml
Session Start Protocol:
  1. Repository Detection:
     - Bash "git rev-parse --show-toplevel"
     → repo_root
     - Bash "mkdir -p $repo_root/docs/memory"

  2. Context Restoration (from local files):
     - Read docs/memory/pm_context.md
     - Read docs/memory/last_session.md
     - Read docs/memory/next_actions.md
     - Read docs/memory/patterns_learned.jsonl
```

**Mismatch**: Documentation references Serena MCP tools that are never called.

### 3.2 Current Memory Storage Strategy

**Location**: `docs/memory/` (repository-scoped local files)

**File Organization**:
```yaml
docs/memory/
  # Session State
  pm_context.md           # Complete PM state snapshot
  last_session.md         # Previous session summary
  next_actions.md         # Planned next steps
  checkpoint.json         # Progress snapshots (30-min)

  # Active Work
  current_plan.json       # Active implementation plan
  implementation_notes.json  # Work-in-progress notes

  # Learning Database (Append-Only Logs)
  patterns_learned.jsonl  # Success patterns
  solutions_learned.jsonl # Error solutions
  mistakes_learned.jsonl  # Failure analysis

docs/pdca/[feature]/
  plan.md, do.md, check.md, act.md  # PDCA cycle documents
```

**Operations**: Direct file Read/Write via Claude Code tools (NOT Serena MCP)

### 3.3 Advantages of Current Approach

✅ **Transparent**: Files visible in repository
✅ **Git-Manageable**: Versioned, diff-able, committable
✅ **No External Dependencies**: Works without Serena MCP
✅ **Human-Readable**: Markdown and JSON formats
✅ **Repository-Scoped**: Automatic isolation via git boundary

### 3.4 Disadvantages of Current Approach

❌ **No Semantic Understanding**: Just text files, no code comprehension
❌ **Documentation Mismatch**: Says Serena, uses local files
❌ **Missed Serena Features**: Doesn't leverage LSP-powered understanding
❌ **Manual Management**: No automatic onboarding or context building

---

## 4. Gap Analysis: Serena vs Current Implementation

| Feature | Serena MCP | Current Implementation | Gap |
|---------|------------|----------------------|-----|
| **Memory Storage** | `.serena/memories/` | `docs/memory/` | Different location |
| **Access Method** | MCP tools | Direct file Read/Write | Different API |
| **Semantic Understanding** | Yes (LSP-powered) | No (text-only) | Missing capability |
| **Onboarding** | Automatic | Manual | Missing automation |
| **Code Awareness** | Symbol-level | None | Missing integration |
| **Thinking Tools** | Built-in | None | Missing introspection |
| **Project Switching** | activate_project() | cd + git root | Manual process |

---

## 5. Options for Resolution

### Option A: Actually Use Serena MCP Tools

**Implementation**:
```yaml
Replace:
  - Read docs/memory/pm_context.md

With:
  - mcp__serena__read_memory("pm_context")

Replace:
  - Write docs/memory/checkpoint.json

With:
  - mcp__serena__write_memory(
      memory_name="checkpoint",
      content=json_to_markdown(checkpoint_data)
    )

Add:
  - mcp__serena__list_memories() at session start
  - mcp__serena__think_about_task_adherence() during work
  - mcp__serena__activate_project(repo_root) on init
```

**Benefits**:
- Leverage Serena's semantic code understanding
- Automatic project onboarding
- Symbol-level context awareness
- Consistent with documentation

**Drawbacks**:
- Depends on Serena MCP server availability
- Memories stored in `.serena/` (less visible)
- Requires airis-mcp-gateway integration
- More complex error handling

**Suitability**: ⭐⭐⭐ (Good if Serena always available)

---

### Option B: Remove Serena References (Clarify Reality)

**Implementation**:
```yaml
Update pm.md:
  - Remove lines 15, 119, 127-191 (Serena references)
  - Explicitly document repository-scoped local file approach
  - Clarify: "PM Agent uses transparent file-based memory"
  - Update: "Session Lifecycle (Repository-Scoped Local Files)"

Benefits Already in Place:
  - Transparent, Git-manageable
  - No external dependencies
  - Human-readable formats
  - Automatic isolation via git boundary
```

**Benefits**:
- Documentation matches reality
- No dependency on external services
- Transparent and auditable
- Simple implementation

**Drawbacks**:
- Loses semantic understanding capabilities
- No automatic onboarding
- Manual context management
- Misses Serena's thinking tools

**Suitability**: ⭐⭐⭐⭐⭐ (Best for current state)

---

### Option C: Hybrid Approach (Best of Both Worlds)

**Implementation**:
```yaml
Primary Storage: Local files (docs/memory/)
  - Always works, no dependencies
  - Transparent, Git-manageable

Optional Enhancement: Serena MCP (when available)
  - try:
      mcp__serena__think_about_task_adherence()
      mcp__serena__write_memory("pm_semantic_context", summary)
    except:
      # Fallback gracefully, continue with local files
      pass

Benefits:
  - Core functionality always works
  - Enhanced capabilities when Serena available
  - Graceful degradation
  - Future-proof architecture
```

**Benefits**:
- Works with or without Serena
- Leverages semantic understanding when available
- Maintains transparency
- Progressive enhancement

**Drawbacks**:
- More complex implementation
- Dual storage system
- Synchronization considerations
- Increased maintenance burden

**Suitability**: ⭐⭐⭐⭐ (Good for long-term flexibility)

---

## 6. Recommendations

### Immediate Action: **Option B - Clarify Reality** ⭐⭐⭐⭐⭐

**Rationale**:
- Documentation-reality mismatch is causing confusion
- Current file-based approach works well
- No evidence Serena MCP is actually being used
- Simple fix with immediate clarity improvement

**Implementation Steps**:

1. **Update `plugins/superclaude/commands/pm.md`**:
   ```diff
   - ## Session Lifecycle (Serena MCP Memory Integration)
   + ## Session Lifecycle (Repository-Scoped Local Memory)

   - 1. Context Restoration:
   -    - list_memories() → Check for existing PM Agent state
   -    - read_memory("pm_context") → Restore overall context
   + 1. Context Restoration (from local files):
   +    - Read docs/memory/pm_context.md → Project context
   +    - Read docs/memory/last_session.md → Previous work
   ```

2. **Remove MCP Resource Attempt**:
   - Document: "Serena exposes tools only, not resources"
   - Update: Never attempt `ReadMcpResourceTool` with "serena://memories"

3. **Clarify MCP Integration Section**:
   ```markdown
   ### MCP Integration (Optional Enhancement)

   **Primary Storage**: Repository-scoped local files (`docs/memory/`)
   - Always available, no dependencies
   - Transparent, Git-manageable, human-readable

   **Optional Serena Integration** (when available via airis-mcp-gateway):
   - mcp__serena__think_about_* tools for introspection
   - mcp__serena__get_symbols_overview for code understanding
   - mcp__serena__write_memory for semantic summaries
   ```

### Future Enhancement: **Option C - Hybrid Approach** ⭐⭐⭐⭐

**When**: After Option B is implemented and stable

**Rationale**:
- Provides progressive enhancement
- Leverages Serena when available
- Maintains core functionality without dependencies

**Implementation Priority**: Low (current system works)

---

## 7. Evidence Sources

### Official Documentation
- **Serena GitHub**: https://github.com/oraios/serena
- **Serena MCP Registry**: https://mcp.so/server/serena/oraios
- **Tool Documentation**: https://glama.ai/mcp/servers/@oraios/serena/schema
- **Memory Discussion**: https://github.com/oraios/serena/discussions/297

### Best Practices
- **MCP Memory Integration**: https://www.byteplus.com/en/topic/541419
- **Memory Management**: https://research.aimultiple.com/memory-mcp/
- **MCP Resources vs Tools**: https://medium.com/@laurentkubaski/mcp-resources-explained-096f9d15f767

### Community Insights
- **Serena Deep Dive**: https://skywork.ai/skypage/en/Serena MCP Server: A Deep Dive for AI Engineers/1970677982547734528
- **Implementation Guide**: https://apidog.com/blog/serena-mcp-server/
- **Usage Examples**: https://lobehub.com/mcp/oraios-serena

---

## 8. Conclusion

**Current State**: PM Agent uses repository-scoped local files, NOT Serena MCP memory management.

**Problem**: Documentation references Serena tools that are never called, creating confusion.

**Solution**: Clarify documentation to match reality (Option B), with optional future enhancement (Option C).

**Action Required**: Update `plugins/superclaude/commands/pm.md` to remove Serena references and explicitly document file-based memory approach.

**Confidence**: High (90%) - Evidence-based analysis with official documentation verification.
