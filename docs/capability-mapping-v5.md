# SuperClaude v5: Capability-Driven Architecture

## Executive Summary

SuperClaude v4.x has 30 commands that create cognitive overhead ("command flood").
v5 proposes collapsing these into **7 canonical capabilities** with intent-based routing.

## The 7-Verb Capability Model

| Capability | Description | Primary MCP Implementation |
|------------|-------------|---------------------------|
| **search** | Web/docs/code search | tavily, fetch, context7 |
| **summarize** | Extract, analyze, compare | sequential-thinking |
| **retrieve** | Knowledge base access | mindbase |
| **plan** | Task decomposition, strategy | airis-agent |
| **edit** | File editing, PR, fixes | serena |
| **execute** | Scripts, workflows, builds | bash, docker |
| **record** | Memory storage, observations | mindbase |

## Current Command → Capability Mapping

### Primary Search Commands (→ `search`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:research` | Deep web research | `search` + `summarize` |
| `/sc:index-repo` | Codebase indexing | `search` + `record` |
| `/sc:troubleshoot` | Debug/investigate | `search` + `summarize` |

### Primary Summarize Commands (→ `summarize`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:analyze` | Code quality analysis | `summarize` |
| `/sc:explain` | Code explanation | `summarize` |
| `/sc:estimate` | Effort estimation | `summarize` |
| `/sc:recommend` | Recommendations | `summarize` |
| `/sc:business-panel` | Business analysis | `summarize` |

### Primary Retrieve Commands (→ `retrieve`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:load` | Session loading | `retrieve` |
| `/sc:index` | General index | `retrieve` |
| `/sc:help` | Help/guidance | `retrieve` |
| `/sc:select-tool` | Tool selection | `retrieve` |

### Primary Plan Commands (→ `plan`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:brainstorm` | Requirements discovery | `plan` + `summarize` |
| `/sc:design` | Architecture design | `plan` |
| `/sc:spec-panel` | Specification | `plan` |
| `/sc:workflow` | Workflow generation | `plan` + `execute` |

### Primary Edit Commands (→ `edit`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:implement` | Feature implementation | `edit` + `execute` |
| `/sc:improve` | Code improvement | `edit` |
| `/sc:cleanup` | Code cleanup | `edit` |
| `/sc:document` | Documentation | `edit` + `record` |

### Primary Execute Commands (→ `execute`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:build` | Build/compile | `execute` |
| `/sc:test` | Test execution | `execute` |
| `/sc:git` | Git operations | `execute` |
| `/sc:spawn` | Agent spawning | `execute` |
| `/sc:task` | Task execution | `plan` + `execute` |

### Primary Record Commands (→ `record`)
| Command | Current Purpose | Capability Mapping |
|---------|-----------------|-------------------|
| `/sc:save` | Session persistence | `record` |
| `/sc:reflect` | Task reflection | `record` + `summarize` |

### Meta/Orchestration Commands
| Command | Current Purpose | v5 Handling |
|---------|-----------------|-------------|
| `/sc:pm` | Project manager | **Absorbed into core** - PM Agent becomes default orchestration layer |
| `/sc:agent` | Agent control | **Absorbed into core** - Multi-agent is automatic |
| `/sc:sc` | Super command | **Deprecated** - Intent routing replaces explicit commands |

## v5 Intent → Implementation Routing

### Example: User says "Check if this code has security issues"

**v4 (Command-driven):**
```bash
/sc:analyze src/ --focus security
```

**v5 (Capability-driven):**
```
User: "Check if this code has security issues"
↓
Intent Detection: security_analysis
↓
Capability: summarize
↓
Implementation: sequential-thinking + serena (code read)
↓
Output: Security analysis report
```

### Example: User says "Remember this pattern for next time"

**v4 (Command-driven):**
```bash
/sc:save --type learnings
```

**v5 (Capability-driven):**
```
User: "Remember this pattern for next time"
↓
Intent Detection: store_knowledge
↓
Capability: record
↓
Implementation: mindbase.store_memory()
↓
Output: Pattern stored with semantic embedding
```

## gateway-config.yaml Schema (Proposed)

```yaml
# AIRIS MCP Gateway Configuration
version: "1.0"
capabilities:
  search:
    description: "Web/docs/code search"
    implementations:
      - name: tavily
        priority: 1
        conditions:
          - intent: "web_search"
          - intent: "current_events"
      - name: context7
        priority: 2
        conditions:
          - intent: "library_docs"
          - intent: "api_reference"
      - name: fetch
        priority: 3
        conditions:
          - intent: "specific_url"
          - intent: "http_request"
    fallback: fetch

  summarize:
    description: "Extract, analyze, compare"
    implementations:
      - name: sequential-thinking
        priority: 1
        conditions:
          - complexity: "high"
          - multi_step: true
      - name: native
        priority: 2
        conditions:
          - complexity: "low"
    fallback: native

  retrieve:
    description: "Knowledge base access"
    implementations:
      - name: mindbase
        priority: 1
        conditions:
          - scope: "project"
          - scope: "cross_session"
      - name: memory
        priority: 2
        conditions:
          - scope: "session_only"
    fallback: memory

  plan:
    description: "Task decomposition and strategy"
    implementations:
      - name: airis-agent
        priority: 1
        conditions:
          - complexity: "high"
          - pdca: true
      - name: sequential-thinking
        priority: 2
        conditions:
          - complexity: "medium"
    fallback: native

  edit:
    description: "File editing and refactoring"
    implementations:
      - name: serena
        priority: 1
        conditions:
          - scope: "multi_file"
          - refactoring: true
      - name: native
        priority: 2
        conditions:
          - scope: "single_file"
    fallback: native

  execute:
    description: "Script and workflow execution"
    implementations:
      - name: bash
        priority: 1
        conditions:
          - type: "shell_command"
      - name: docker
        priority: 2
        conditions:
          - type: "container"
    fallback: bash

  record:
    description: "Memory storage and observations"
    implementations:
      - name: mindbase
        priority: 1
        conditions:
          - persistence: "long_term"
          - semantic: true
      - name: memory
        priority: 2
        conditions:
          - persistence: "session"
    fallback: memory

# Intent patterns for automatic routing
intent_patterns:
  web_search:
    keywords: ["search", "find online", "latest", "current"]
    capability: search
    implementation_hint: tavily

  library_docs:
    keywords: ["docs", "documentation", "how to use", "api"]
    capability: search
    implementation_hint: context7

  security_analysis:
    keywords: ["security", "vulnerability", "owasp", "audit"]
    capability: summarize
    implementation_hint: sequential-thinking

  code_explanation:
    keywords: ["explain", "what does", "how does"]
    capability: summarize

  store_knowledge:
    keywords: ["remember", "save", "store", "note"]
    capability: record
    implementation_hint: mindbase

  task_planning:
    keywords: ["plan", "break down", "steps", "how to implement"]
    capability: plan
    implementation_hint: airis-agent
```

## Migration Path: v4 → v5

### Phase 1: Soft Deprecation
- v4 commands continue to work
- Commands route to capability layer internally
- Warning: "Consider using natural language"

### Phase 2: Capability Aliases
- `/search "query"` as shorthand for search capability
- `/plan "task"` as shorthand for plan capability
- Natural language always works

### Phase 3: Command Removal
- v4 `/sc:*` commands deprecated
- Only 7 capability verbs + natural language
- Full intent-based routing

## Implementation Priority

1. **Core Framework**: Intent detection + capability routing
2. **AIRIS Integration**: airis-agent as plan/execute implementation
3. **Mindbase Integration**: retrieve/record implementation
4. **MCP Gateway**: Hot/cold server management
5. **Legacy Compatibility**: v4 command translation layer

## Token Efficiency Comparison

| Scenario | v4 Tokens | v5 Tokens | Savings |
|----------|-----------|-----------|---------|
| Security analysis | ~500 (command parsing) | ~100 (intent) | 80% |
| Research task | ~800 (multi-command) | ~200 (single intent) | 75% |
| Memory storage | ~300 (command + args) | ~50 (natural) | 83% |

## Conclusion

The 7-verb capability model:
- Reduces cognitive load from 30 commands to 7 concepts
- Enables natural language interaction
- Allows vendor-neutral MCP implementation swapping
- Provides cleaner Plugin ABI for extensions
- Maintains backwards compatibility during transition
