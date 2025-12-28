# SuperClaude Advanced Workflows Collection

**Status**: ✅ **Status: Current** - Complex command sequences and context combinations for sophisticated projects.

**Advanced Usage Guide**: Patterns for complex projects using multiple commands, agents, and careful context management within Claude Code conversations.

## Overview and Usage Guide

**Purpose**: Advanced SuperClaude patterns for complex, multi-step projects that require careful sequencing of commands and context management.

**Important**: These are conversation patterns, not executing workflows. All work happens within Claude Code based on context provided.

**Key Concepts**:
- Command sequences within a conversation
- Context layering through multiple agents
- Progressive refinement approaches
- Project phase management (manual, not automated)

## Multi-Context Project Patterns

### Full-Stack Development Sequence

```bash
# E-commerce platform using multiple contexts
# Step 1: Architecture context
@agent-system-architect "design e-commerce architecture"

# Step 2: Security requirements
@agent-security "define security requirements for payments"

# Step 3: Backend implementation
/sc:implement "API with authentication and payment processing"
# Claude uses accumulated context from previous steps

# Step 4: Frontend implementation
@agent-frontend-architect "design responsive UI"
/sc:implement "React frontend with TypeScript"

# Step 5: Review
/sc:analyze . --focus quality

# Note: Each step builds context within the conversation
# No actual coordination or parallel execution occurs
```

### Problem-Solving Workflow

```bash
# Complex troubleshooting approach
# Step 1: Problem understanding
/sc:troubleshoot "application performance issues"

# Step 2: Expert analysis
@agent-performance-engineer "analyze potential bottlenecks"
@agent-backend-architect "review architecture for issues"

# Step 3: Solution design
/sc:design "performance improvement plan"

# Step 4: Implementation
/sc:implement "performance optimizations"

# Context accumulates but doesn't execute
```

## Complex Project Phases

### Project Initialization Pattern

```bash
# Starting a new project
# Discovery phase
/sc:brainstorm "project concept"
# Claude explores requirements

# Planning phase
/sc:design "system architecture"
@agent-system-architect "review and refine"

# Documentation
/sc:document --type architecture
/sc:save "project-plan"
# Creates summary for your records (not persistent storage)
```

### Incremental Development Pattern

```bash
# Building features incrementally
# Feature 1: Authentication
/sc:implement "user authentication"
/sc:test --focus security
/sc:document --type api

# Feature 2: User Profiles (builds on auth context)
/sc:implement "user profile management"
/sc:test --focus functionality

# Feature 3: Admin Dashboard (uses previous context)
/sc:implement "admin dashboard"
@agent-frontend-architect "ensure consistency"

# Each feature builds on conversation context
```

### Migration Project Pattern

```bash
# Legacy system migration
# Phase 1: Analysis
/sc:load legacy-system/
/sc:analyze . --focus architecture --verbose
# Claude builds understanding

# Phase 2: Planning
@agent-system-architect "design migration strategy"
/sc:workflow "create migration plan"

# Phase 3: Implementation
/sc:implement "compatibility layer"
/sc:implement "new system components"

# Phase 4: Validation
/sc:test --focus compatibility
/sc:document --type migration

# Manual phases, not automated workflow
```

## Enterprise-Scale Patterns

### Large Codebase Analysis

```bash
# Systematic analysis of large projects
# Overview
/sc:analyze . --overview
# Get high-level understanding

# Focused analysis by module
/sc:analyze auth-module/ --focus security
/sc:analyze api-module/ --focus quality
/sc:analyze frontend/ --focus performance

# Synthesis
@agent-system-architect "synthesize findings"
/sc:workflow "improvement recommendations"

# Note: Sequential analysis, not parallel
```

### Multi-Technology Projects

```bash
# Projects with diverse tech stacks
# Backend (Python)
@agent-python-expert "implement FastAPI backend"
/sc:implement "Python API with async support"

# Frontend (React)
@agent-frontend-architect "implement React frontend"
/sc:implement "TypeScript React application"

# Mobile (React Native)
/sc:implement "React Native mobile app"

# Infrastructure
@agent-devops-architect "design deployment"
/sc:implement "Docker configuration"

# Each technology addressed sequentially
```

## Quality Assurance Workflows

### Comprehensive Review Pattern

```bash
# Multi-aspect code review
# Quality review
/sc:analyze . --focus quality
@agent-quality-engineer "identify improvements"

# Security review
/sc:analyze . --focus security
@agent-security "check for vulnerabilities"

# Architecture review
@agent-system-architect "evaluate design"

# Performance review
@agent-performance-engineer "suggest optimizations"

# Consolidated improvements
/sc:improve . --fix

# Sequential reviews, not parallel analysis
```

### Testing Strategy Pattern

```bash
# Comprehensive testing approach
# Test planning
/sc:design "testing strategy"

# Unit tests
/sc:test --type unit
# Claude generates unit test code

# Integration tests
/sc:test --type integration
# Claude generates integration test code

# E2E tests
/sc:test --type e2e
# Claude suggests E2E test scenarios

# Documentation
/sc:document --type testing

# Test code generation, not execution
```

## Session Management Patterns

### Long Project Sessions

```bash
# Managing context in long conversations
# Start with context
/sc:load project/

# Work progressively
/sc:implement "feature A"
/sc:implement "feature B"
# Context accumulates

# Create checkpoint
/sc:save "session-checkpoint"
# Creates summary for your notes

# Continue work
/sc:implement "feature C"

# Final summary
/sc:reflect
# Reviews conversation progress
```

### Context Refresh Pattern

```bash
# When conversation gets too long
# Save current state
/sc:save "work-complete"
# Copy output for next conversation

# In new conversation:
/sc:load project/
"Previous work: [paste summary]"
# Manually restore context

# Continue work
/sc:implement "next feature"
```

## Important Clarifications

### What These Workflows ARE

- ✅ **Conversation Patterns**: Sequences within a single Claude conversation
- ✅ **Context Building**: Progressive accumulation of understanding
- ✅ **Command Sequences**: Ordered use of commands for better results
- ✅ **Manual Phases**: User-controlled project progression

### What These Workflows ARE NOT

- ❌ **Automated Workflows**: No automatic execution or orchestration
- ❌ **Parallel Processing**: Everything is sequential
- ❌ **Persistent Sessions**: Context lost between conversations
- ❌ **Performance Optimization**: No code executes to optimize

## Best Practices

### Conversation Management

1. **Keep Related Work Together**: Don't split related tasks across conversations
2. **Build Context Progressively**: Start broad, then focus
3. **Document Key Decisions**: Use `/sc:save` for important points
4. **Manage Conversation Length**: Start new conversation if too long

### Command Sequencing

1. **Logical Order**: Analysis → Design → Implementation → Testing
2. **Context Accumulation**: Later commands benefit from earlier context
3. **Appropriate Depth**: Match analysis depth to task complexity
4. **Clear Scope**: Focus commands on specific areas

### Agent Usage

1. **Strategic Activation**: Use agents for specific expertise
2. **Avoid Overload**: Too many agents can dilute focus
3. **Manual Control**: Use `@agent-` for precise control
4. **Context Layering**: Add agents in logical order

## Summary

Advanced workflows in SuperClaude are sophisticated conversation patterns that build context progressively within a single Claude Code session. They help generate better outputs through careful command sequencing and context management, but do not involve any actual workflow execution, parallel processing, or automation. Success comes from understanding how to layer context effectively within Claude's conversation scope.