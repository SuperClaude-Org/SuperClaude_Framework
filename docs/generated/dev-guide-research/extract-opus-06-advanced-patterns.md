# Extraction: Advanced Patterns for Custom Commands, Skills, and Agents

**Source File**: `/config/workspace/SuperClaude_Framework/docs/reference/advanced-patterns.md`
**Extracted By**: Claude Opus 4.6
**Date**: 2026-02-21
**Purpose**: Extract all information relevant to developing custom commands, skills, agents, wave orchestration, and MCP integration for the SuperClaude framework.

---

## 1. Document Overview and Core Philosophy

The source document describes itself as:

> **Advanced Context Usage Patterns**: Sophisticated combinations of commands, agents, and flags for experienced SuperClaude users working on complex projects.

A critical framing statement governs the entire document:

> **Remember**: SuperClaude provides context to Claude Code. All patterns here are about guiding Claude's behavior through context, not executing code or coordinating processes.

This is reinforced in the summary:

> Advanced SuperClaude patterns are about sophisticated context management and command sequencing. They help Claude Code generate better outputs by providing richer, more structured context. Remember: all "coordination" and "optimization" happens in how Claude interprets the context, not in any actual execution or parallel processing.

**Key takeaway for developers**: SuperClaude commands, agents, and skills operate as context-loading mechanisms, not as runtime execution engines. Any "orchestration" is sequential context layering within a conversation.

---

## 2. Multi-Agent Context Patterns

### 2.1 Combining Specialist Contexts

The document shows how to layer multiple agent contexts for richer guidance.

**Security + Backend Pattern:**
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

**Frontend + UX + Accessibility Pattern:**
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

### 2.2 Manual vs Automatic Agent Selection

**Explicit Control Pattern** -- directly specifying which agent context loads:
```bash
# Manually control which contexts load
@agent-python-expert "implement data pipeline"
# Only Python context, no auto-activation

# vs Automatic selection
/sc:implement "Python data pipeline"
# May activate multiple agents based on keywords
```

**Override Auto-Selection** -- suppressing unwanted agent activation:
```bash
# Prevent unwanted agent activation
/sc:implement "simple utility" --no-mcp
@agent-backend-architect "keep it simple"
# Limits context to specified agent only
```

### 2.3 Cross-Technology Multi-Agent Coordination

For projects spanning multiple technology domains:
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

**Pattern**: Each technology domain gets its own agent invocation in sequence. The accumulated context from earlier invocations informs later ones within the same conversation.

---

## 3. Advanced Command Patterns

### 3.1 Command Sequencing -- Progressive Refinement

Start broad, then narrow focus across multiple commands:
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

### 3.2 Discovery to Implementation Pattern

A full lifecycle command sequence:
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

### 3.3 Iterative Improvement Pattern

Multiple passes of analysis and improvement:
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

### 3.4 Large Codebase Analysis Pattern

Systematic exploration of large projects in stages:
```bash
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

### 3.5 Multi-Module Development Pattern

Developing interconnected modules with context carry-over:
```bash
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

---

## 4. Flag Combination Strategies

### 4.1 Analysis Depth Control

The document defines four tiers of analysis depth:

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

### 4.2 MCP Server Selection Flags

Three modes of MCP control:
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

---

## 5. Migration and Legacy Modernization Patterns

### 5.1 Legacy System Analysis

```bash
# Understanding legacy systems
/sc:load legacy-system/
/sc:analyze . --focus architecture --verbose

@agent-refactoring-expert "identify modernization opportunities"
@agent-system-architect "propose migration strategy"

/sc:workflow "create migration plan"
```

### 5.2 Incremental Migration

```bash
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

## 6. Review and Audit Patterns

### 6.1 Security Audit

```bash
/sc:analyze . --focus security --think-hard
@agent-security "review authentication and authorization"
@agent-security "check for OWASP vulnerabilities"
/sc:document --type security-audit
```

### 6.2 Code Quality Review

```bash
/sc:analyze src/ --focus quality
@agent-quality-engineer "review test coverage"
@agent-refactoring-expert "identify code smells"
/sc:improve --fix --preview
```

### 6.3 Architecture Review

```bash
@agent-system-architect "review current architecture"
/sc:analyze . --focus architecture --think-hard
@agent-performance-engineer "identify bottlenecks"
/sc:design "optimization recommendations"
```

---

## 7. Clarifications on What Patterns Do and Do Not Do

The document is explicit about the boundaries of these patterns:

**What these patterns actually do:**
- Guide Claude's thinking -- provide structured approaches
- Combine contexts -- layer multiple expertise areas
- Improve output quality -- better code generation through better context
- Structure workflows -- organize complex tasks

**What these patterns do NOT do:**
- Execute in parallel -- everything is sequential context loading
- Coordinate processes -- no actual process coordination
- Optimize performance -- no code runs, so no performance impact
- Persist between sessions -- each conversation is independent

> - ❌ **Execute in Parallel**: Everything is sequential context loading
> - ❌ **Coordinate Processes**: No actual process coordination
> - ❌ **Persist Between Sessions**: Each conversation is independent

---

## 8. Best Practices for Advanced Usage

### 8.1 Context Management

Quoted directly from the source:
1. **Layer Deliberately**: Add contexts in logical order
2. **Avoid Overload**: Too many agents can dilute focus
3. **Use Manual Control**: Override auto-activation when needed
4. **Maintain Conversation Flow**: Keep related work in same conversation

### 8.2 Command Efficiency

1. **Progress Logically**: Broad -> Specific -> Implementation
2. **Reuse Context**: Later commands benefit from earlier context
3. **Document Decisions**: Use `/sc:save` for important summaries
4. **Scope Appropriately**: Focus on manageable chunks

### 8.3 Flag Usage

1. **Match Task Complexity**: Simple tasks don't need `--ultrathink`
2. **Control Output**: Use `--uc` for concise results
3. **Manage MCP**: Only activate needed servers
4. **Avoid Conflicts**: Don't use contradictory flags

---

## 9. Gaps and Observations

The following topics are **not covered** in this document, despite being referenced in the broader SuperClaude framework:

- **Custom command development**: No instructions on how to create new `/sc:*` commands (file structure, registration, argument parsing).
- **Custom skill architecture**: No details on building skill packages (SKILL.md structure, rules/, templates/, scripts/ directories).
- **Custom agent definitions**: No guide on writing new agent `.md` files or their required structure.
- **Wave orchestration implementation details**: While wave-enabled commands are referenced in COMMANDS.md and ORCHESTRATOR.md, this document does not describe how to make a new command wave-eligible or how waves execute internally.
- **MCP integration advanced usage**: MCP flags (`--magic`, `--c7`, `--all-mcp`, `--no-mcp`) are demonstrated for selection, but there is no guidance on integrating MCP servers into custom commands or skills.
- **Adversarial debate patterns**: The `/sc:adversarial` command and its debate-orchestrator/merge-executor agents are not discussed here.
- **Compliance tier integration**: The `/sc:task` command's compliance enforcement system is not referenced.

These gaps suggest that `advanced-patterns.md` focuses on **user-facing usage patterns** (how to combine existing commands/agents effectively) rather than **developer-facing extension patterns** (how to build new commands, skills, or agents). Developer-facing documentation for custom component creation would need to be sourced from other files such as COMMANDS.md, the skill source directories, and CLAUDE.md's component sync workflow.
