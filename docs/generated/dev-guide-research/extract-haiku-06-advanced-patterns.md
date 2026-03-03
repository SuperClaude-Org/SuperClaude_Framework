# Extraction: Custom Commands, Skills, and Agents — Advanced Patterns

Source: `/config/workspace/SuperClaude_Framework/docs/reference/advanced-patterns.md`

## Scope Note
This extraction includes **all information in the source file that pertains to developing or using custom commands, skills, or agents** in the SuperClaude framework context. The source document is primarily about **context usage patterns** (how to guide Claude Code via context) rather than implementation details for creating new command/skill/agent files.

---

## 1) Agents: Combining Specialist Contexts (Multi-Agent Context Patterns)

### 1.1 Security + Backend Pattern (agent context layering)

Exact quote + code block:

```bash
# Security-focused backend development
@agent-security "define authentication requirements"
@agent-backend-architect "design API with security requirements"
/sc:implement "secure API endpoints"

# What happens:
# 1. Security context loaded first
# 2. Backend context added
# 3. Implementation guided by both contexts
# Note: Contexts combine in Claude's understanding, not in execution
```

Key extracted guidance (verbatim):
- “**Security context loaded first**”
- “**Backend context added**”
- “**Implementation guided by both contexts**”
- “**Note: Contexts combine in Claude's understanding, not in execution**”

### 1.2 Frontend + UX + Accessibility Pattern (agent + command + MCP flag)

Exact quote + code block:

```bash
# Comprehensive frontend development
@agent-frontend-architect "design component architecture"
/sc:implement "accessible React components" --magic
@agent-quality-engineer "review accessibility compliance"

# Context layering:
# - Frontend patterns guide structure
# - Magic MCP may provide UI components (if configured)
# - Quality context ensures standards
```

Key extracted guidance (verbatim):
- “**Context layering:**”
  - “**Frontend patterns guide structure**”
  - “**Magic MCP may provide UI components (if configured)**”
  - “**Quality context ensures standards**”

### 1.3 Manual vs Automatic Agent Selection

#### Manual agent selection (explicit control)

Exact quote + code block:

```bash
# Manually control which contexts load
@agent-python-expert "implement data pipeline"
# Only Python context, no auto-activation

# vs Automatic selection
/sc:implement "Python data pipeline"
# May activate multiple agents based on keywords
```

Extracted points (verbatim):
- “**Manually control which contexts load**”
- “**Only Python context, no auto-activation**”
- “**May activate multiple agents based on keywords**”

#### Override auto-selection

Exact quote + code block:

```bash
# Prevent unwanted agent activation
/sc:implement "simple utility" --no-mcp
@agent-backend-architect "keep it simple"
# Limits context to specified agent only
```

Extracted point (verbatim):
- “**Limits context to specified agent only**”

---

## 2) Commands: Sequencing patterns that affect command/agent workflows

### 2.1 Progressive Refinement Pattern (command sequencing)

Exact quote + code block:

```bash
# Start broad, then focus
/sc:analyze project/
# General analysis

/sc:analyze project/core/ --focus architecture
# Focused on structure

/sc:analyze project/core/auth/ --focus security --think-hard
# Deep security analysis

# Each command builds on previous context within the conversation
```

Extracted point (verbatim):
- “**Each command builds on previous context within the conversation**”

### 2.2 Discovery to Implementation Pattern (end-to-end command flow)

Exact quote + code block:

```bash
# Complete feature development flow
/sc:brainstorm "feature idea"
# Explores requirements

/sc:design "feature architecture"
# Creates structure

@agent-backend-architect "review design"
# Expert review

/sc:implement "feature based on design"
# Implementation follows design

/sc:test --validate
# Verification approach
```

This includes a concrete pattern for how custom slash commands are intended to be used together:
- `/sc:brainstorm` → `/sc:design` → `@agent-...` review → `/sc:implement` → `/sc:test --validate`

### 2.3 Iterative Improvement Pattern (command + agent combo)

Exact quote + code block:

```bash
# Multiple improvement passes
/sc:analyze code/ --focus quality
# Identify issues

/sc:improve code/ --fix
# First improvement pass

@agent-refactoring-expert "suggest further improvements"
# Expert suggestions

/sc:improve code/ --fix --focus maintainability
# Refined improvements
```

---

## 3) Flags that matter for developing/using commands & agent workflows

### 3.1 Analysis depth control flags (used with commands)

Exact quote + code block:

```bash
# Quick overview
/sc:analyze . --overview --uc
# Fast, compressed output

# Standard analysis
/sc:analyze . --think
# Structured thinking

# Deep analysis
/sc:analyze . --think-hard --verbose
# Comprehensive analysis

# Maximum depth (use sparingly)
/sc:analyze . --ultrathink
# Exhaustive analysis
```

### 3.2 MCP server selection flags (used with commands)

Exact quote + code block:

```bash
# Selective MCP usage
/sc:implement "React component" --magic --c7
# Only Magic and Context7 MCP

# Disable all MCP
/sc:implement "simple function" --no-mcp
# Pure Claude context only

# All available MCP
/sc:analyze complex-system/ --all-mcp
# Maximum tool availability (if configured)
```

Extracted points (verbatim):
- “**Only Magic and Context7 MCP**”
- “**Disable all MCP**”
- “**Pure Claude context only**”
- “**Maximum tool availability (if configured)**”

---

## 4) Complex project workflows involving agents + commands

### 4.1 Large Codebase Analysis (agents + commands)

Exact quote + code block:

```bash
# Systematic exploration of large projects
# Step 1: Structure understanding
/sc:load project/
/sc:analyze . --overview --focus architecture

# Step 2: Identify problem areas
@agent-quality-engineer "identify high-risk modules"

# Step 3: Deep dive into specific areas
/sc:analyze high-risk-module/ --think-hard --focus quality

# Step 4: Implementation plan
/sc:workflow "improvement plan based on analysis"
```

### 4.2 Multi-Module Development (commands + agent checks)

Exact quote + code block:

```bash
# Developing interconnected modules
# Frontend module
/sc:implement "user interface module"
@agent-frontend-architect "ensure consistency"

# Backend module
/sc:implement "API module"
@agent-backend-architect "ensure compatibility"

# Integration layer
/sc:implement "frontend-backend integration"
# Context from both previous implementations guides this
```

Extracted point (verbatim):
- “**Context from both previous implementations guides this**”

### 4.3 Cross-Technology Projects (agents + documentation command)

Exact quote + code block:

```bash
# Projects with multiple technologies
# Python backend
@agent-python-expert "implement FastAPI backend"

# React frontend
@agent-frontend-architect "implement React frontend"

# DevOps setup
@agent-devops-architect "create deployment configuration"

# Integration documentation
/sc:document --type integration
```

---

## 5) Migration patterns involving commands + agents

### 5.1 Legacy System Analysis

Exact quote + code block:

```bash
# Understanding legacy systems
/sc:load legacy-system/
/sc:analyze . --focus architecture --verbose

@agent-refactoring-expert "identify modernization opportunities"
@agent-system-architect "propose migration strategy"

/sc:workflow "create migration plan"
```

### 5.2 Incremental Migration

Exact quote + code block:

```bash
# Step-by-step migration approach
# Phase 1: Analysis
/sc:analyze legacy-module/ --comprehensive

# Phase 2: Design new architecture
@agent-system-architect "design modern replacement"

# Phase 3: Implementation
/sc:implement "modern module with compatibility layer"

# Phase 4: Validation
/sc:test --focus compatibility
```

---

## 6) Review and audit patterns involving agents + commands

### 6.1 Security Audit Pattern

Exact quote + code block:

```bash
# Comprehensive security review
/sc:analyze . --focus security --think-hard
@agent-security "review authentication and authorization"
@agent-security "check for OWASP vulnerabilities"
/sc:document --type security-audit
```

### 6.2 Code Quality Review

Exact quote + code block:

```bash
# Multi-aspect quality review
/sc:analyze src/ --focus quality
@agent-quality-engineer "review test coverage"
@agent-refactoring-expert "identify code smells"
/sc:improve --fix --preview
```

### 6.3 Architecture Review

Exact quote + code block:

```bash
# System architecture assessment
@agent-system-architect "review current architecture"
/sc:analyze . --focus architecture --think-hard
@agent-performance-engineer "identify bottlenecks"
/sc:design "optimization recommendations"
```

---

## 7) Important clarifications for custom commands/agents usage

### 7.1 What these patterns actually do

Exact quotes:
- “✅ **Guide Claude's Thinking**: Provide structured approaches”
- “✅ **Combine Contexts**: Layer multiple expertise areas”
- “✅ **Improve Output Quality**: Better code generation through better context”
- “✅ **Structure Workflows**: Organize complex tasks”

### 7.2 What these patterns don’t do

Exact quotes:
- “❌ **Execute in Parallel**: Everything is sequential context loading”
- “❌ **Coordinate Processes**: No actual process coordination”
- “❌ **Optimize Performance**: No code runs, so no performance impact”
- “❌ **Persist Between Sessions**: Each conversation is independent”

These are directly relevant when building/using commands/agents/skills because they set correct expectations: patterns influence **context and output**, not runtime behavior.

---

## 8) Best practices for advanced usage (relevant to command/agent design and usage)

### 8.1 Context management

Exact quotes:
1. “**Layer Deliberately**: Add contexts in logical order”
2. “**Avoid Overload**: Too many agents can dilute focus”
3. “**Use Manual Control**: Override auto-activation when needed”
4. “**Maintain Conversation Flow**: Keep related work in same conversation”

### 8.2 Command efficiency

Exact quotes:
1. “**Progress Logically**: Broad → Specific → Implementation”
2. “**Reuse Context**: Later commands benefit from earlier context”
3. “**Document Decisions**: Use `/sc:save` for important summaries”
4. “**Scope Appropriately**: Focus on manageable chunks”

### 8.3 Flag usage

Exact quotes:
1. “**Match Task Complexity**: Simple tasks don't need `--ultrathink`”
2. “**Control Output**: Use `--uc` for concise results”
3. “**Manage MCP**: Only activate needed servers”
4. “**Avoid Conflicts**: Don't use contradictory flags”

---

## 9) Summary statement relevant to custom commands/agents

Exact quote:
- “Advanced SuperClaude patterns are about sophisticated context management and command sequencing. They help Claude Code generate better outputs by providing richer, more structured context. Remember: all "coordination" and "optimization" happens in how Claude interprets the context, not in any actual execution or parallel processing.”
