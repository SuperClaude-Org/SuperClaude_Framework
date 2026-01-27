# OpenCode MCP Integration Capabilities Research

**Research Date**: 2026-01-17
**Objective**: Investigate MCP integration in OpenCode (IBOpenCode) for porting /sc:spec-panel
**Confidence Level**: HIGH (Based on official documentation, existing research in IBOpenCode, and source analysis)

---

## Executive Summary

OpenCode **fully supports** MCP (Model Context Protocol) integration as a client, with comprehensive capabilities that parallel Claude Code's MCP support. Key findings:

| Capability | OpenCode | Claude Code | Compatibility |
|------------|----------|-------------|---------------|
| MCP Client Support | Full | Full | Direct |
| Sequential Thinking | Via MCP Server | Native `mcp__sequential-thinking` | Equivalent |
| Documentation Lookup | Via MCP Server (Context7) | Native `context7` MCP | Equivalent |
| Tool Orchestration | JSON-based with Zod validation | XML-like function calls | Translation needed |
| Parallel Execution | Synchronous by default (plugins available) | Native subagent parallelization | Gap identified |

**Bottom Line**: Porting /sc:spec-panel to OpenCode is **feasible** with moderate adaptation effort. The primary work involves translating Claude Code's frontmatter configuration format to OpenCode's JSON/YAML configuration system.

---

## 1. MCP Support Status in OpenCode

### Full MCP Client Implementation

OpenCode implements comprehensive MCP client functionality:

```json
{
  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"],
      "enabled": true,
      "timeout": 5000
    },
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@context7/mcp-server"],
      "environment": {
        "API_KEY": "{env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

### Supported Transport Types

| Type | Description | Configuration Key |
|------|-------------|-------------------|
| **Local** | Run as child processes using stdio | `type: "local"` |
| **Remote** | Communicate over HTTP/SSE with OAuth 2.0 | `type: "remote"` |

### Authentication Methods

1. **Automatic OAuth 2.0**: Detects 401 responses and initiates OAuth flows
2. **Pre-registered Credentials**: Store client ID, secret, and scopes
3. **API Keys**: Disable OAuth with `"oauth": false` and pass keys via headers
4. **Manual Authentication**: `opencode mcp auth server-name`

---

## 2. Tool System Comparison

### OpenCode Built-in Tools (13 total)

| Tool | Description | Claude Code Equivalent |
|------|-------------|----------------------|
| `read` | File reading with line range | `Read` |
| `write` | Create/overwrite files | `Write` |
| `edit` | Exact string replacement | `Edit` |
| `patch` | Apply patch files/diffs | N/A |
| `grep` | Regex search (ripgrep) | `Grep` |
| `glob` | Pattern file matching | `Glob` |
| `list` | Directory listing | Bash `ls` |
| `bash` | Shell execution | `Bash` |
| `task` | Subagent delegation | `Task` |
| `todowrite` | Task list creation | `TodoWrite` |
| `todoread` | Task list reading | N/A (implicit) |
| `webfetch` | Web page fetching | `WebFetch` |
| `question` | User prompts | N/A |
| `skill` | Load SKILL.md files | `Skill` |
| `lsp` (experimental) | Code intelligence | N/A |

### Tool Call Syntax Differences

**OpenCode (JSON with Zod validation)**:
```json
{
  "name": "read",
  "arguments": {
    "filePath": "/path/to/file.ts",
    "lineStart": 1,
    "lineEnd": 100
  }
}
```

**Claude Code** uses XML-like function calls handled by the assistant model.

### Tool Permission Configuration

OpenCode provides granular tool permissions:

```json
{
  "tools": {
    "bash": true,
    "read": true,
    "write": true,
    "edit": true
  },
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

---

## 3. Sequential Thinking Capabilities

### Claude Code Implementation

Claude Code has native `mcp__sequential-thinking__sequentialthinking` tool with parameters:
- `thought`: Current thinking step
- `nextThoughtNeeded`: Boolean for continuation
- `thoughtNumber`: Sequence position
- `totalThoughts`: Estimated total
- `isRevision`: For revising previous thoughts
- `branchFromThought`: For branching reasoning

### OpenCode Implementation

OpenCode achieves equivalent functionality via MCP server integration:

```json
{
  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"]
    }
  }
}
```

**Capabilities provided by Sequential Thinking MCP**:
- Breaking down complex problems into steps
- Branching into alternative reasoning paths
- Dynamic thought count adjustment
- Hypothesis generation and verification
- Revisable thought sequences

### Native Model Reasoning Support

OpenCode also supports native model reasoning effort configuration:

| Provider | Reasoning Levels |
|----------|-----------------|
| **Anthropic** | `max` (maximum thinking budget) |
| **OpenAI** | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| **Google** | `low`, `high` |

```json
{
  "models": {
    "claude-sonnet-4": {
      "provider": "anthropic",
      "variants": {
        "thinking": {
          "reasoningEffort": "max"
        }
      }
    }
  }
}
```

---

## 4. Documentation Lookup (Context7 Equivalent)

### Claude Code Implementation

Claude Code uses Context7 MCP for:
- Official library documentation
- Framework patterns and best practices
- Version-specific implementation guidance

### OpenCode Implementation

OpenCode can integrate Context7 as an MCP server:

```json
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@context7/mcp-server"],
      "environment": {
        "API_KEY": "{env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

**Alternative**: OpenCode also supports `webfetch` for documentation lookup, though less structured than dedicated Context7 integration.

---

## 5. Command/Skill Configuration Comparison

### Claude Code Frontmatter Format

```yaml
---
name: spec-panel
description: "Multi-expert specification review"
category: analysis
complexity: enhanced
mcp-servers: [sequential, context7]
personas: [technical-writer, system-architect, quality-engineer]
---
```

### OpenCode Equivalent

**Command Definition** (`.opencode/command/spec-panel.md`):

```yaml
---
description: Multi-expert specification review and improvement
agent: spec-panel-agent
model: anthropic/claude-sonnet-4-20250514
---

# Prompt template content here with $ARGUMENTS
```

**Agent Definition** (`.opencode/agent/spec-panel-agent.md`):

```yaml
---
description: Specification review expert panel orchestrator
mode: subagent
temperature: 0.3
maxSteps: 20
tools:
  read: true
  write: true
  bash: false
  task: true
permission:
  edit: ask
---

System prompt content defining expert panel behavior...
```

### Key Configuration Differences

| Aspect | Claude Code | OpenCode |
|--------|-------------|----------|
| MCP Declaration | Frontmatter `mcp-servers: []` | Global `opencode.json` config |
| Persona System | Frontmatter `personas: []` | Agent definitions with prompts |
| Tool Access | Implicit in skill | Explicit `tools:` block |
| Model Override | Via skill config | Via `model:` key |
| Sub-delegation | Native parallel | `task` tool (synchronous) |

---

## 6. Gaps Identified for Spec-Panel Porting

### Gap 1: Parallel Subagent Execution

**Claude Code**: Supports parallel subagent execution natively
**OpenCode**: Currently synchronous by default

**Mitigation**: Use community plugins:
- `oh-my-opencode`: Hub-and-spoke architecture with specialist agents
- `Open Orchestra`: Multi-agent orchestration with worker management
- `Agent Orchestrator`: High-performance parallel execution framework

### Gap 2: Persona Auto-Activation

**Claude Code**: Automatic persona activation based on context
**OpenCode**: Must be explicitly configured in agent definitions

**Mitigation**: Implement persona logic in agent system prompts and use task delegation for persona switching.

### Gap 3: MCP Server Declaration Scope

**Claude Code**: Per-skill MCP server declaration
**OpenCode**: Global MCP configuration (all commands share access)

**Mitigation**: Use tool filtering per agent:
```json
{
  "agent": {
    "spec-panel": {
      "tools": {
        "sequential-thinking*": true,
        "context7*": true
      }
    }
  }
}
```

### Gap 4: Thinking Depth Flags

**Claude Code**: `--think`, `--think-hard`, `--ultrathink` flags
**OpenCode**: Model variants with `reasoningEffort`

**Mitigation**: Create command variants or use model variant switching:
```json
{
  "command": {
    "spec-panel-deep": {
      "template": "...",
      "model": "anthropic/claude-sonnet-4-20250514:thinking"
    }
  }
}
```

---

## 7. Porting Strategy for /sc:spec-panel

### Phase 1: Core Infrastructure

1. **Create MCP Configuration** in `opencode.json`:
```json
{
  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"]
    }
  }
}
```

2. **Create Base Agent** (`.opencode/agent/spec-panel.md`):
```yaml
---
description: Multi-expert specification review panel
mode: subagent
temperature: 0.3
maxSteps: 30
tools:
  read: true
  write: true
  grep: true
  glob: true
  task: true
  webfetch: true
permission:
  edit: ask
---

[System prompt with expert panel definitions]
```

### Phase 2: Expert Panel Implementation

Translate expert definitions from Claude Code skill into agent system prompt:

```markdown
## Expert Panel System

### Karl Wiegers (Requirements Engineering)
- Focus: SMART criteria, testability analysis
- Voice: Methodical, precise, measurability-focused
- Key Question: "How would we verify this requirement?"

### Gojko Adzic (Specification by Example)
- Focus: Concrete examples, executable specifications
- Voice: Pragmatic, example-driven
- Key Question: "Can you give me a concrete example?"

[Continue for all 10 experts...]
```

### Phase 3: Analysis Modes

Create mode-specific command variants:

```yaml
# .opencode/command/spec-panel.md (default: discussion)
---
description: Specification review - Discussion mode
agent: spec-panel
---
Analyze specification with collaborative expert discussion...

# .opencode/command/spec-panel-critique.md
---
description: Specification review - Critique mode
agent: spec-panel
---
Perform adversarial specification analysis...

# .opencode/command/spec-panel-socratic.md
---
description: Specification review - Socratic mode
agent: spec-panel
---
Guide specification understanding through expert questioning...
```

### Phase 4: Quality Metrics System

Implement scoring in agent prompt:

```markdown
## Quality Dimensions

### Clarity (0-10)
- Sub-criteria: Language precision, terminology consistency, structure
- Expert weights: Wiegers 40%, Adzic 30%, Cockburn 30%

### Completeness (0-10)
- Sub-criteria: Section coverage, edge cases, error handling
- Expert weights: Wiegers 30%, Nygard 25%, Newman 25%, Hohpe 20%

### Testability (0-10)
- Sub-criteria: Acceptance criteria, examples, measurability
- Expert weights: Adzic 35%, Crispin 30%, Gregory 25%, Wiegers 10%

### Consistency (0-10)
- Sub-criteria: No contradictions, terminology alignment, cross-refs
- Expert weights: Fowler 30%, Wiegers 30%, Newman 20%, Hohpe 20%
```

### Phase 5: Integration Testing

1. Validate MCP server connectivity
2. Test expert panel simulation quality
3. Verify quality scoring accuracy
4. Confirm output format compliance
5. Performance and token usage validation

---

## 8. Existing IBOpenCode Implementation Reference

The IBOpenCode repository at `<opencode-root>` already implements a multi-model adversarial debate system (`/rf:crossLLM`) that demonstrates:

### Relevant Patterns

1. **Agent Definition Format**: `.opencode/agent/*.md` with YAML frontmatter
2. **Command Routing**: `.opencode/command/*.md` with argument parsing
3. **Multi-Model Coordination**: Orchestrator pattern with task delegation
4. **Quality Scoring**: QAG-based evaluation with multi-model consensus

### Key Files to Reference

| File | Relevance |
|------|-----------|
| `.opencode/agent/rf-crossLLM-orchestrator.md` | Complex orchestration patterns |
| `.opencode/agent/rf-crossLLM-evaluator-qag.md` | Quality assessment implementation |
| `.opencode/agent/rf-crossLLM-debate.md` | Multi-perspective analysis |
| `.opencode/command/rf:crossLLM.md` | Command routing and argument handling |

### Adaptation Opportunity

The rf-crossLLM system's:
- Proposer pattern could map to expert panel simulation
- Debate phase maps to critique mode
- Evaluator pattern maps to quality scoring
- Orchestrator pattern provides delegation model

---

## 9. Recommendations

### Immediate Actions

1. **Configure MCP Servers**: Add sequential-thinking to `opencode.json`
2. **Create Agent Definition**: Port expert panel to agent system prompt
3. **Implement Command**: Create `/spec-panel` command with mode variants

### Design Decisions Required

1. **Parallelization Strategy**: Accept sequential or implement plugin-based parallelism
2. **Persona Implementation**: Inline in prompt vs separate agents
3. **Quality Scoring**: Static weights vs configurable per-domain
4. **Output Format**: Adapt SuperClaude symbol system for OpenCode

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Sequential execution slower | Batch operations, optimize prompts |
| MCP server availability | Graceful fallback to native tools |
| Expert voice inconsistency | Explicit voice guidelines in prompt |
| Quality metric drift | Calibration test suite |

---

## 10. Source References

### Official Documentation
- [OpenCode Tools Documentation](https://opencode.ai/docs/tools/)
- [OpenCode MCP Servers Guide](https://opencode.ai/docs/mcp-servers/)
- [OpenCode Agents](https://opencode.ai/docs/agents/)
- [OpenCode Commands](https://opencode.ai/docs/commands/)

### IBOpenCode Research
- `<project-root>/.dev/releases/backlog/v.4.0-Spec-generator-framework/research/opencode-tools-mcp.md`
- `<project-root>/.dev/releases/backlog/v.4.0-Spec-generator-framework/research/opencode-architecture.md`
- `<project-root>/.dev/releases/backlog/v.4.0-Spec-generator-framework/research/superclaude-spec-panel-extraction.md`

### MCP Protocol
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Sequential Thinking MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)

---

## Appendix A: Configuration Templates

### Minimal OpenCode Configuration for Spec-Panel

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",

  "mcp": {
    "sequential-thinking": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-sequentialthinking"],
      "enabled": true
    }
  },

  "agent": {
    "spec-panel": {
      "description": "Multi-expert specification review panel",
      "mode": "subagent",
      "temperature": 0.3,
      "maxSteps": 30,
      "tools": {
        "read": true,
        "write": true,
        "grep": true,
        "glob": true,
        "task": true,
        "sequential-thinking*": true
      }
    }
  },

  "command": {
    "spec-panel": {
      "template": "Analyze the following specification using the expert panel methodology:\n\n$ARGUMENTS",
      "description": "Multi-expert specification review",
      "agent": "spec-panel"
    }
  },

  "instructions": ["AGENTS.md"]
}
```

### Agent System Prompt Template

```markdown
You are a specification review orchestrator managing a panel of 10 software engineering experts. Each expert brings unique domain expertise and methodology to specification analysis.

## Expert Panel

### Requirements Engineering
1. **Karl Wiegers**: SMART criteria, testability, acceptance criteria quality
2. **Gojko Adzic**: Specification by Example, Given/When/Then scenarios
3. **Alistair Cockburn**: Use cases, actor-goal analysis, scenario modeling

### Architecture & Integration
4. **Martin Fowler**: API design, DDD, bounded contexts, design patterns
5. **Michael Nygard**: Production systems, failure modes, operational resilience
6. **Sam Newman**: Microservices, service boundaries, API contracts
7. **Gregor Hohpe**: Enterprise integration, messaging patterns, event-driven

### Quality & Testing
8. **Lisa Crispin**: Testing quadrants, acceptance criteria, automation strategy
9. **Janet Gregory**: ATDD, continuous testing, quality coaching

### Cloud & Operations
10. **Kelsey Hightower**: Cloud-native patterns, Kubernetes, declarative configuration

## Analysis Modes

When mode=discussion: Collaborative analysis with experts building on each other's insights
When mode=critique: Adversarial challenge with specific improvement recommendations
When mode=socratic: Question-driven exploration for learning and understanding

## Quality Metrics

Score each dimension 0-10:
- Clarity: Language precision, terminology consistency, structure
- Completeness: Coverage, edge cases, error handling, operational concerns
- Testability: Acceptance criteria, examples, measurability
- Consistency: No contradictions, aligned terminology, accurate cross-refs

Overall = (Clarity * 0.25) + (Completeness * 0.30) + (Testability * 0.25) + (Consistency * 0.20)
```

---

*Research completed: 2026-01-17*
*Author: Claude Opus 4.5 (Deep Research Agent)*
