# Extraction — Custom commands, skills, and agents (Integration Patterns)

**Source**: `/config/workspace/SuperClaude_Framework/docs/reference/integration-patterns.md`

This extraction includes **all content in the source file that pertains to developing and using custom commands, skills, or agents** in the SuperClaude framework.

---

## 1) Core concept: commands/agents/flags provide context (not execution)

Exact quotes:

- “**Context Integration Guide**: Patterns for using SuperClaude commands effectively with different frameworks and tools. Remember: SuperClaude provides context to Claude Code - all actual work is done by Claude.”

- “**Key Principle**: SuperClaude tells Claude Code WHAT to do and HOW to think about it. Claude Code does the actual work.”

- “**What This Is**: Command combinations and flag patterns that work well for specific technologies”

- “**What This Isn't**: Performance optimization or parallel execution (no code runs)”

- “Remember that all patterns are about providing better context to Claude Code - the actual code generation, not execution, is what Claude does based on these contexts.”

These clarifications matter when developing or extending custom commands/agents/skills: the “integration patterns” are primarily about **how to compose** command usage, agent invocation, and MCP flags to steer Claude Code.

---

## 2) Command usage patterns relevant to custom command development

The source file demonstrates a repeated, compositional pattern that is relevant when authoring new custom commands (or advising users how to use them):

- Use `/sc:implement ...` for implementation guidance
- Use `/sc:design ...` for design planning guidance
- Use `/sc:document ...` for documentation guidance
- Use `/sc:test ...` for testing guidance
- Use `/sc:analyze ...` and `/sc:troubleshoot ...` for analysis/debug flows
- Use `/sc:explain ...` for explanations
- Use `/sc:brainstorm ...` for ideation
- Use `/sc:load` and `/sc:save` as session scaffolding

Exact quote (Best Practices → Effective Pattern Usage):

- “1. **Start with context**: Use `/sc:load` to establish project understanding”
- “5. **Document decisions**: Use `/sc:save` to create summaries”

These provide a “command lifecycle” model: load → implement/design/analyze → test/document → save.

---

## 3) Agent invocation patterns (custom agents / specialist routing)

The file contains multiple examples of **explicit agent routing** via `@agent-...` directives. This is directly relevant to developing or using custom agents: it shows how agents are composed with commands.

### 3.1 Agent + command composition (general pattern)

The “Agent and Command Combinations” section shows a reusable pattern:

```bash
# Security-focused development
@agent-security "review authentication requirements"
/sc:implement "secure authentication system"
/sc:analyze --focus security

# Quality-focused workflow
/sc:implement "new feature"
@agent-quality-engineer "review code quality"
/sc:test --focus quality

# Architecture-focused approach
@agent-system-architect "design microservices"
/sc:design "service boundaries"
/sc:implement "service communication"
```

Key idea: invoke an agent to set or apply specialist context, then run one or more `/sc:*` commands to generate outcomes.

### 3.2 Agents referenced in the source file

All agent identifiers shown (verbatim):

- `@agent-frontend-architect`
- `@agent-backend-architect`
- `@agent-python-expert`
- `@agent-system-architect`
- `@agent-security`
- `@agent-quality-engineer`
- `@agent-root-cause-analyst`
- `@agent-performance-engineer`

### 3.3 Agent examples embedded in framework patterns

React component architecture example (verbatim block excerpt):

```bash
# Component development pattern
@agent-frontend-architect "design component architecture"
/sc:implement "reusable component library"
```

Node database schema review example:

```bash
# Database integration pattern
/sc:implement "database models with Prisma"
@agent-backend-architect "review database schema"
```

Python implementation review and optimization suggestions:

```bash
/sc:implement "FastAPI application" --c7
@agent-python-expert "review implementation"

@agent-python-expert "optimize pandas operations"
# Claude provides optimization suggestions (not actual optimization)
```

Troubleshooting workflow routing:

```bash
# Root cause investigation
@agent-root-cause-analyst "analyze symptoms"
```

Performance review routing:

```bash
# Performance review
@agent-performance-engineer "suggest improvements"
# Note: Suggestions only, no actual performance measurement
```

---

## 4) MCP/server flags that influence how custom commands and agents operate

The “Using MCP Servers Effectively” section shows how flags can be layered onto commands. This is relevant to custom command authoring because custom commands typically need to:

- define which flags they accept,
- describe the intended MCP usage,
- and show composable examples.

Exact code block:

```bash
# Context7 for documentation
/sc:explain "React hooks" --c7
# If Context7 is configured, it may fetch React docs

# Sequential for complex reasoning
/sc:troubleshoot "complex bug" --seq
# Sequential MCP helps with structured problem-solving

# Magic for UI components
/sc:implement "UI components" --magic
# Magic MCP can help generate modern UI patterns

# No MCP for simple tasks
/sc:implement "utility function" --no-mcp
# Uses only Claude's built-in knowledge
```

Additionally, earlier examples explicitly connect flags to behavior:

- “`--c7` flag suggests using Context7 MCP for documentation”

---

## 5) End-to-end workflows that combine commands + agents (templates you can reuse)

These workflow patterns are effectively “templates” for how a custom command/skill/agent should be used and composed.

### 5.1 API development workflow

```bash
# Step 1: Design
/sc:design "REST API structure"

# Step 2: Implementation
/sc:implement "API endpoints with validation"

# Step 3: Documentation
/sc:document --type api

# Step 4: Testing
/sc:test --focus api
```

### 5.2 Database integration workflow

```bash
# Schema design
@agent-backend-architect "design database schema"

# Model implementation
/sc:implement "database models"

# Migration creation
/sc:implement "database migrations"

# Query optimization suggestions
@agent-backend-architect "suggest query optimizations"
# Note: Claude suggests optimizations, doesn't actually optimize
```

### 5.3 Testing strategy workflow

```bash
# Test planning
/sc:design "testing strategy"

# Unit tests
/sc:test --type unit

# Integration tests
/sc:test --type integration

# E2E test suggestions
/sc:test --type e2e
# Claude provides test code, not execution
```

### 5.4 Debugging workflow

```bash
# Problem analysis
/sc:troubleshoot "describe the issue"

# Root cause investigation
@agent-root-cause-analyst "analyze symptoms"

# Solution implementation
/sc:implement "fix based on analysis"

# Verification
/sc:test --validate
```

### 5.5 Code review workflow (analysis + specialist agents + improvement)

```bash
# Code analysis
/sc:analyze code/ --focus quality

# Security review
@agent-security "review for vulnerabilities"

# Performance review
@agent-performance-engineer "suggest improvements"
# Note: Suggestions only, no actual performance measurement

# Implementation of improvements
/sc:improve code/ --fix
```

---

## 6) Pattern selection guidance (how to decide what a custom command/agent should recommend)

Exact quote (Best Practices → Pattern Selection):

- “**Simple tasks**: Use basic commands without MCP”
- “**Complex tasks**: Add appropriate agents and MCP servers”
- “**Security-critical**: Always include `@agent-security`”
- “**UI development**: Consider `--magic` flag if configured”
- “**Documentation needs**: Use `--c7` for framework docs”

This maps directly to “decision rules” that a custom command, skill, or agent could encode in its own usage guidance.

---

## 7) Explicit constraints (important for custom commands/skills/agents)

The source file emphasizes what these integrations do *not* do, which should be reflected in custom command/skill/agent documentation to avoid misleading behavior.

Exact quotes:

### What these patterns DO

- “✅ Provide structured approaches to development tasks”
- “✅ Combine commands and agents effectively”
- “✅ Suggest appropriate tools and frameworks”
- “✅ Guide Claude to generate better code”

### What these patterns DON'T DO

- “❌ Execute code or measure performance”
- “❌ Run tests or deploy applications”
- “❌ Optimize actual execution speed”
- “❌ Provide real monitoring or metrics”
- “❌ Coordinate parallel processes (everything is sequential text)”
