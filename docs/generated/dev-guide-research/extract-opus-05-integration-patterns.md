# Extraction: Integration Patterns for Custom Command/Skill/Agent Development

**Source**: `/config/workspace/SuperClaude_Framework/docs/reference/integration-patterns.md`
**Extracted**: 2026-02-21
**Purpose**: All information relevant to developing custom commands, skills, or agents for the SuperClaude framework.

---

## 1. Core Architectural Principle

The document establishes a fundamental design principle that governs all integration:

> "SuperClaude tells Claude Code WHAT to do and HOW to think about it. Claude Code does the actual work."

And further:

> "SuperClaude provides context to Claude Code - all actual work is done by Claude."

This means commands, skills, and agents are **context providers**, not executors. They shape Claude's behavior through structured prompts and flag-driven context injection.

---

## 2. Command + Agent Integration Patterns

### 2.1 Agent-Then-Command Sequencing

The document shows a recurring pattern where an agent is invoked first for design/review, followed by a command for implementation:

```bash
# Architecture-focused approach
@agent-system-architect "design microservices"
/sc:design "service boundaries"
/sc:implement "service communication"
```

```bash
# Security-focused development
@agent-security "review authentication requirements"
/sc:implement "secure authentication system"
/sc:analyze --focus security
```

```bash
# Quality-focused workflow
/sc:implement "new feature"
@agent-quality-engineer "review code quality"
/sc:test --focus quality
```

**Key Insight**: Agents provide domain-specific context/review, while commands drive the actual generation workflow. The pattern is: **Agent (context/design) -> Command (implement) -> Agent or Command (validate)**.

### 2.2 Multi-Agent Layering Across Domains

Full-stack patterns demonstrate how multiple agents coordinate across domains:

```bash
# Full-stack application pattern
/sc:brainstorm "full-stack application architecture"
@agent-system-architect "design system components"

# Frontend implementation
/sc:implement "React frontend with TypeScript"
@agent-frontend-architect "review component structure"

# Backend implementation
/sc:implement "Node.js API with authentication"
@agent-backend-architect "review API design"

# Integration
/sc:implement "connect frontend to backend API"
```

**Key Insight**: Each domain (frontend, backend, system) has its own specialist agent. Commands handle cross-cutting implementation while agents provide domain-specific expertise.

### 2.3 Agent Naming Convention

Agents referenced in the document use the `@agent-<specialty>` prefix pattern:

- `@agent-frontend-architect`
- `@agent-backend-architect`
- `@agent-system-architect`
- `@agent-security`
- `@agent-quality-engineer`
- `@agent-performance-engineer`
- `@agent-root-cause-analyst`
- `@agent-python-expert`

---

## 3. MCP Server Integration Patterns

### 3.1 Flag-Driven MCP Activation

MCP servers are activated via flags on commands:

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

### 3.2 MCP Server Selection by Task Type

| Task Type | MCP Flag | Server | Purpose |
|-----------|----------|--------|---------|
| Documentation lookup | `--c7` | Context7 | Fetch framework/library docs |
| Complex reasoning | `--seq` | Sequential | Structured problem-solving |
| UI generation | `--magic` | Magic | Modern UI component patterns |
| Simple/fast tasks | `--no-mcp` | None | Built-in knowledge only |

### 3.3 MCP + Command Combinations

```bash
# React development with Context7
/sc:implement "React 18 application with TypeScript" --c7
# Context7 MCP can provide React documentation if available
# Magic MCP can help with UI components if configured
```

The document notes what happens under the hood:

> "1. Claude reads implement.md for implementation patterns
> 2. --c7 flag suggests using Context7 MCP for documentation
> 3. Claude generates React code based on these contexts"

**Key Insight for Custom Development**: Commands read their corresponding `.md` file for patterns. MCP flags layer additional context on top. Custom commands should follow this same pattern: define behavior in a markdown file, accept MCP flags for enhanced context.

---

## 4. Tool Coordination Patterns

### 4.1 Multi-Step Workflow Pattern (Design -> Implement -> Document -> Test)

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

### 4.2 Debugging Workflow Pattern (Troubleshoot -> Analyze -> Fix -> Verify)

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

### 4.3 Code Review Pattern (Analyze -> Review -> Suggest -> Improve)

```bash
# Code analysis
/sc:analyze code/ --focus quality

# Security review
@agent-security "review for vulnerabilities"

# Performance review
@agent-performance-engineer "suggest improvements"

# Implementation of improvements
/sc:improve code/ --fix
```

---

## 5. Persona Activation Patterns

### 5.1 Implicit Persona Activation Through Commands

The document demonstrates that certain commands implicitly activate personas:

- `/sc:implement` with frontend context activates frontend persona
- `/sc:implement` with backend context activates backend persona
- `/sc:analyze --focus security` activates security persona
- `/sc:test` activates QA persona
- `/sc:troubleshoot` activates analyzer persona

### 5.2 Explicit Persona Activation Through Agents

Agents serve as explicit persona activators:

```bash
@agent-frontend-architect "review component structure"   # frontend persona
@agent-backend-architect "review API design"              # backend persona
@agent-security "review for vulnerabilities"              # security persona
@agent-performance-engineer "suggest improvements"        # performance persona
```

### 5.3 Combined Persona Layering

The document shows patterns where multiple personas are active across a workflow:

```bash
# Frontend persona (via agent) + implementation context (via command)
@agent-frontend-architect "recommend state management approach"
/sc:implement "state management with Zustand/Redux"
```

---

## 6. Best Practices for Integration

### 6.1 Pattern Selection Guidelines

From the document's "Best Practices" section:

> 1. **Start with context**: Use `/sc:load` to establish project understanding
> 2. **Layer expertise**: Combine general commands with specific agents
> 3. **Focus appropriately**: Use `--focus` flags for targeted results
> 4. **Manage scope**: Work on specific modules rather than entire codebases
> 5. **Document decisions**: Use `/sc:save` to create summaries

### 6.2 Complexity-Based MCP Selection

> - **Simple tasks**: Use basic commands without MCP
> - **Complex tasks**: Add appropriate agents and MCP servers
> - **Security-critical**: Always include `@agent-security`
> - **UI development**: Consider `--magic` flag if configured
> - **Documentation needs**: Use `--c7` for framework docs

### 6.3 Clarification of Boundaries

The document explicitly states what integration patterns do and do not provide:

**What patterns DO**:
> - Provide structured approaches to development tasks
> - Combine commands and agents effectively
> - Suggest appropriate tools and frameworks
> - Guide Claude to generate better code

**What patterns DON'T do**:
> - Execute code or measure performance
> - Run tests or deploy applications
> - Optimize actual execution speed
> - Provide real monitoring or metrics
> - Coordinate parallel processes (everything is sequential text)

---

## 7. Multi-Agent Orchestration Examples

### 7.1 Full-Stack Orchestration

The most complete multi-agent example in the document:

```bash
# Phase 1: Architecture (system-architect agent)
/sc:brainstorm "full-stack application architecture"
@agent-system-architect "design system components"

# Phase 2: Frontend (frontend-architect agent)
/sc:implement "React frontend with TypeScript"
@agent-frontend-architect "review component structure"

# Phase 3: Backend (backend-architect agent)
/sc:implement "Node.js API with authentication"
@agent-backend-architect "review API design"

# Phase 4: Integration (command-only, no specific agent)
/sc:implement "connect frontend to backend API"
```

### 7.2 Microservices Orchestration

```bash
# Architecture design
@agent-system-architect "design microservices architecture"

# Service implementation (repeated per service)
/sc:implement "user service with Express"
/sc:implement "auth service with JWT"

# Inter-service communication
/sc:implement "service communication patterns"

# Testing approach
/sc:test --focus microservices
```

### 7.3 Security-Layered Orchestration

```bash
# Security-focused development
@agent-security "review authentication requirements"
/sc:implement "secure authentication system"
/sc:analyze --focus security
```

---

## 8. Key Takeaways for Custom Development

1. **Commands are markdown-driven**: Each command reads its corresponding `.md` file (e.g., `implement.md`) for behavioral patterns. Custom commands should follow this convention.

2. **MCP flags are additive context**: The `--c7`, `--seq`, `--magic`, `--no-mcp` flags layer MCP server capabilities on top of base command behavior. Custom commands should accept these flags.

3. **Agents are domain specialists**: They use the `@agent-<name>` convention and provide focused expertise. They work best when paired with commands in a review/implement cycle.

4. **Workflow patterns are sequential**: Despite the framework's support for parallel execution at the tool level, the integration patterns themselves follow sequential phases (design -> implement -> test -> review).

5. **The `--focus` flag is a key routing mechanism**: It directs analysis, testing, and improvement commands toward specific domains (security, performance, quality, react, api, python, etc.).

6. **Scope management matters**: The document recommends working on "specific modules rather than entire codebases" -- custom commands and skills should support scoped operation.
