# SuperClaude Basic Examples Collection

**Status**: ✅ **Status: Current** - Essential commands, single-agent workflows, and common development tasks.

**Quick Reference Guide**: Copy-paste ready examples for beginners, focused on essential SuperClaude usage patterns and fundamental development workflows.

> **📝 Context Note**: These examples show `/sc:` commands and `@agent-` invocations that trigger Claude Code to read specific context files and adopt the behaviors defined there. The sophistication comes from the behavioral instructions, not from executable software.

## Overview and Usage Guide

**Purpose**: Essential SuperClaude commands and patterns for everyday development tasks. Start here for your first SuperClaude experience.

**Target Audience**: New users, developers learning SuperClaude fundamentals, immediate task application

**Usage Pattern**: Copy → Adapt → Execute → Learn from results

**Key Features**:
- Examples demonstrate core SuperClaude functionality
- Clear patterns for immediate application  
- Single-focus examples for clear learning
- Progressive complexity within basic scope

## Essential One-Liner Commands

### Core Development Commands

#### Command: /sc:brainstorm
**Purpose**: Interactive project discovery and requirements gathering
**Syntax**: `/sc:brainstorm "project description"`
**Example**:
```bash
/sc:brainstorm "mobile app for fitness tracking"
# Expected: Socratic dialogue, requirement elicitation, feasibility analysis
```
**Behavior**: Triggers interactive discovery dialogue and requirements analysis

#### Command: /sc:analyze
**Purpose**: Analyze existing codebase for issues and improvements
**Syntax**: `/sc:analyze [target] --focus [domain]`
**Example**:
```bash
/sc:analyze src/ --focus security
# Expected: Comprehensive security audit, vulnerability report, improvement suggestions
```
**Behavior**: Provides comprehensive security analysis and improvement recommendations

#### Command: /sc:implement
**Purpose**: Implement a complete feature with best practices
**Syntax**: `/sc:implement "feature description with requirements"`
**Example**:
```bash
/sc:implement "user authentication with JWT and rate limiting"
# Expected: Complete auth implementation, security validation, tests included
```
**Behavior**: Delivers complete implementation following security and quality standards

#### Command: /sc:troubleshoot
**Purpose**: Troubleshoot and fix a problem systematically
**Syntax**: `/sc:troubleshoot "problem description"`
**Example**:
```bash
/sc:troubleshoot "API returns 500 error on user login"
# Expected: Step-by-step diagnosis, root cause identification, solution ranking
```
**Verification**: Activates root-cause-analyst + Sequential reasoning + systematic debugging

#### Command: /sc:test
**Purpose**: Generate comprehensive tests for existing code
**Syntax**: `/sc:test [target] --focus [domain]`
**Example**:
```bash
/sc:test --focus quality
# Expected: Test suite, quality metrics, coverage reporting
```
**Verification**: Activates quality-engineer + test automation

### Quick Analysis Commands

#### Command: /sc:analyze (Quality Focus)
**Purpose**: Project structure and quality overview
**Syntax**: `/sc:analyze [target] --focus quality`
**Example**:
```bash
/sc:analyze . --focus quality
```
**Verification**: 

#### Command: /sc:analyze (Security Focus)
**Purpose**: Security-focused code review
**Syntax**: `/sc:analyze [target] --focus security [--think]`
**Example**:
```bash
/sc:analyze src/ --focus security --think
```
**Verification**: 

#### Command: /sc:analyze (Performance Focus)
**Purpose**: Performance bottleneck identification
**Syntax**: `/sc:analyze [target] --focus performance`
**Example**:
```bash
/sc:analyze api/ --focus performance
```
**Verification**: 

#### Command: /sc:analyze (Architecture Focus)
**Purpose**: Architecture assessment for refactoring
**Syntax**: `/sc:analyze [target] --focus architecture [--serena]`
**Example**:
```bash
/sc:analyze . --focus architecture --serena
```
**Verification**: 

## Manual Agent Invocation Examples

### Direct Specialist Activation

#### Pattern: @agent-[specialist]
**Purpose**: Manually invoke specific domain experts instead of auto-activation
**Syntax**: `@agent-[specialist] "task or question"`

#### Python Expert
```bash
@agent-python-expert "optimize this data processing pipeline for performance"
# Expected: Python-specific optimizations, async patterns, memory management
```

#### Security Engineer
```bash
@agent-security "review this authentication system for vulnerabilities"
# Expected: OWASP compliance check, vulnerability assessment, secure coding recommendations
```

#### Frontend Architect
```bash
@agent-frontend-architect "design a responsive component architecture"
# Expected: Component patterns, state management, accessibility considerations
```

#### Quality Engineer
```bash
@agent-quality-engineer "create comprehensive test coverage for payment module"
# Expected: Test strategy, unit/integration/e2e tests, edge cases
```

### Combining Auto and Manual Patterns

#### Pattern: Command + Manual Override
```bash
# Step 1: Use command with auto-activation
/sc:implement "user profile management system"
# Auto-activates: backend-architect, possibly frontend

# Step 2: Add specific expert review
@agent-security "review the profile system for data privacy compliance"
# Manual activation for targeted review

# Step 3: Performance optimization
@agent-performance-engineer "optimize database queries for profile fetching"
# Manual activation for specific optimization
```

#### Pattern: Sequential Specialist Chain
```bash
# Design phase
@agent-system-architect "design microservices architecture for e-commerce"

# Security review
@agent-security "review architecture for security boundaries"

# Implementation guidance
@agent-backend-architect "implement service communication patterns"

# DevOps setup
@agent-devops-architect "configure CI/CD for microservices"
```

## Basic Usage Patterns

### Discovery → Implementation Pattern
```bash
# Step 1: Explore and understand requirements
/sc:brainstorm "web dashboard for project management"
# Expected: Requirements discovery, feature prioritization, technical scope

# Step 2: Analyze technical approach
/sc:analyze "dashboard architecture patterns" --focus architecture --c7
# Expected: Architecture patterns, technology recommendations, implementation strategy

# Step 3: Implement core functionality
/sc:implement "React dashboard with task management and team collaboration"
# Expected: Complete dashboard implementation with modern React patterns
```

### Development → Quality Pattern
```bash
# Step 1: Build the feature
/sc:implement "user registration with email verification"
# Expected: Registration system with email integration

# Step 2: Test thoroughly
/sc:test --focus quality
# Expected: Comprehensive test coverage and validation

# Step 3: Review and improve
/sc:analyze . --focus quality && /sc:implement "quality improvements"
# Expected: Quality assessment and targeted improvements
```

### Problem → Solution Pattern
```bash
# Step 1: Understand the problem
/sc:troubleshoot "slow database queries on user dashboard"
# Expected: Systematic problem diagnosis and root cause analysis

# Step 2: Analyze affected components
/sc:analyze db/ --focus performance
# Expected: Database performance analysis and optimization opportunities

# Step 3: Implement solutions
/sc:implement "database query optimization and caching"
# Expected: Performance improvements with measurable impact
```

## Getting Started Examples

### Your First Project Analysis
```bash
# Complete project understanding workflow
/sc:load . && /sc:analyze --focus quality

# Expected Results:
# - Project structure analysis and documentation
# - Code quality assessment across all files
# - Architecture overview with component relationships
# - Security audit and performance recommendations

# Activates: Serena (project loading) + analyzer + security-engineer + performance-engineer
# Output: Comprehensive project report with actionable insights


# Variations for different focuses:
/sc:analyze src/ --focus quality          # Code quality only
/sc:analyze . --scope file               # Quick file analysis
/sc:analyze backend/ --focus security    # Backend security review
```

### Interactive Requirements Discovery
```bash
# Transform vague ideas into concrete requirements
/sc:brainstorm "productivity app for remote teams"

# Expected Interaction:
# - Socratic questioning about user needs and pain points
# - Feature prioritization and scope definition
# - Technical feasibility assessment
# - Structured requirements document generation

# Activates: Brainstorming mode + system-architect + requirements-analyst
# Output: Product Requirements Document (PRD) with clear specifications

# Follow-up commands for progression:
/sc:analyze "team collaboration architecture" --focus architecture --c7
/sc:implement "real-time messaging system with React and WebSocket"
```

### Simple Feature Implementation
```bash
# Complete authentication system
/sc:implement "user login with JWT tokens and password hashing"

# Expected Implementation:
# - Secure password hashing with bcrypt
# - JWT token generation and validation
# - Login/logout endpoints with proper error handling
# - Frontend login form with validation

# Activates: security-engineer + backend-architect + Context7
# Output: Production-ready authentication system


# Variations for different auth needs:
/sc:implement "OAuth integration with Google and GitHub"
/sc:implement "password reset flow with email verification"
/sc:implement "two-factor authentication with TOTP"
```

## Common Development Tasks

### API Development Basics
```bash
# REST API with CRUD operations
/sc:implement "Express.js REST API for blog posts with validation"
# Expected: Complete REST API with proper HTTP methods, validation, error handling


# API documentation generation
/sc:analyze api/ --focus architecture --c7
# Expected: Comprehensive API documentation with usage examples


# API testing setup
/sc:test --focus api --type integration
# Expected: Integration test suite for API endpoints

```

### Frontend Component Development
```bash
# React component with modern patterns
/sc:implement "React user profile component with form validation and image upload"
# Activates: frontend-architect + Magic MCP + accessibility patterns
# Expected: Modern React component with hooks, validation, accessibility


# Component testing
/sc:test src/components/ --focus quality
# Expected: Component tests with React Testing Library


# Responsive design implementation
/sc:implement "responsive navigation component with mobile menu"
# Expected: Mobile-first responsive navigation with accessibility

```

### Database Integration
```bash
# Database setup with ORM
/sc:implement "PostgreSQL integration with Prisma ORM and migrations"
# Expected: Database schema, ORM setup, migration system


# Database query optimization
/sc:analyze db/ --focus performance
# Expected: Query performance analysis and optimization suggestions


# Data validation and security
/sc:implement "input validation and SQL injection prevention"
# Expected: Comprehensive input validation and security measures

```

## Basic Troubleshooting Examples

### Common API Issues
```bash
# Performance problems
/sc:troubleshoot "API response time increased from 200ms to 2 seconds"
# Activates: root-cause-analyst + performance-engineer + Sequential reasoning
# Expected: Systematic diagnosis, root cause identification, solution ranking

# Authentication errors
/sc:troubleshoot "JWT token validation failing for valid users"
# Expected: Token validation analysis, security assessment, fix implementation

# Database connection issues
/sc:troubleshoot "database connection pool exhausted under load"
# Expected: Connection analysis, configuration fixes, scaling recommendations
```

### Frontend Debugging
```bash
# React rendering issues
/sc:troubleshoot "React components not updating when data changes"
# Expected: State management analysis, re-rendering optimization, debugging guide

# Performance problems
/sc:troubleshoot "React app loading slowly with large component tree"
# Expected: Performance analysis, optimization strategies, code splitting recommendations

# Build failures
/sc:troubleshoot "webpack build failing with dependency conflicts"
# Expected: Dependency analysis, conflict resolution, build optimization
```

### Development Environment Issues
```bash
# Setup problems
/sc:troubleshoot "Node.js application not starting after npm install"
# Expected: Environment analysis, dependency troubleshooting, configuration fixes

# Testing failures
/sc:troubleshoot "tests passing locally but failing in CI"
# Expected: Environment comparison, CI configuration analysis, fix recommendations

# Deployment issues
/sc:troubleshoot "application crashes on production deployment"
# Expected: Production environment analysis, configuration validation, deployment fixes
```

## Copy-Paste Quick Solutions

### Immediate Project Setup
```bash
# New React project with TypeScript
/sc:implement "React TypeScript project with routing, state management, and testing setup"
@agent-frontend-architect "review and optimize the project structure"

# New Node.js API server
/sc:implement "Express.js REST API with JWT authentication and PostgreSQL integration"
@agent-backend-architect "ensure scalability and best practices"

# Python web API
/sc:implement "FastAPI application with async PostgreSQL and authentication middleware"
@agent-python-expert "optimize async patterns and dependency injection"

# Next.js full-stack app
/sc:implement "Next.js 14 application with App Router, TypeScript, and Tailwind CSS"
@agent-system-architect "design optimal data fetching strategy"
```

### Quick Quality Improvements
```bash
# Code quality enhancement
/sc:analyze . --focus quality && /sc:implement "code quality improvements"
@agent-quality-engineer "create quality metrics dashboard"

# Security hardening
/sc:analyze . --focus security && /sc:implement "security improvements"

# Test coverage improvement  
/sc:test --focus quality && /sc:implement "additional test coverage"
```

### Common Feature Implementations
```bash
# User authentication system
/sc:implement "complete user authentication with registration, login, and password reset"

# File upload functionality
/sc:implement "secure file upload with image resizing and cloud storage"

# Real-time features
/sc:implement "real-time chat with WebSocket and message persistence"

# Payment processing
/sc:implement "Stripe payment integration with subscription management"

# Email functionality
/sc:implement "email service with templates and delivery tracking"
```

## Basic Flag Examples

### Analysis Depth Control
```bash
# Quick analysis
/sc:analyze src/ --scope file

# Standard analysis
/sc:analyze . --think

# Deep analysis
/sc:analyze . --think-hard --focus architecture

```

### Focus Area Selection
```bash
# Security-focused analysis
/sc:analyze . --focus security


# Implementation with specific focus
/sc:implement "API optimization" --focus architecture


# Quality-focused testing
/sc:test --focus quality

```

### Tool Integration
```bash
# Use Context7 for official patterns
/sc:implement "React hooks implementation" --c7


# Use Serena for project memory
/sc:analyze . --serena --focus architecture


# Efficient token usage
/sc:analyze large-project/ --uc

```

## Learning Progression Workflow

### Week 1: Foundation
```bash
# Day 1-2: Basic commands
/sc:analyze . --focus quality
/sc:implement "simple feature"
/sc:test --focus quality

# Day 3-4: Troubleshooting
/sc:troubleshoot "specific problem"
/sc:analyze problem-area/ --focus relevant-domain

# Day 5-7: Integration
/sc:brainstorm "project idea"
/sc:implement "core feature"
/sc:test --focus quality
```

### Week 2: Patterns
```bash
# Workflow patterns
/sc:brainstorm → /sc:analyze → /sc:implement → /sc:test

# Problem-solving patterns
/sc:troubleshoot → /sc:analyze → /sc:implement

# Quality patterns
/sc:analyze → /sc:implement → /sc:test → /sc:analyze
```

### Week 3-4: Integration
```bash
# Multi-step projects
/sc:brainstorm "larger project"
/sc:implement "phase 1"
/sc:test --focus quality
/sc:implement "phase 2"
/sc:test --focus integration
```

## Next Steps

### Ready for Intermediate?
- Comfortable with all basic commands
- Can complete simple workflows independently
- Understanding of agent activation and tool selection
- Ready for multi-step projects

### Continue Learning:
- **Advanced Workflows**: Complex orchestration and multi-agent coordination
- **Integration Patterns**: Framework integration and cross-tool coordination
- **Best Practices Guide**: Optimization strategies and expert techniques

### Success Indicators:
- Can solve common development problems independently
- Understands when to use different flags and focuses
- Can adapt examples to specific project needs
- Ready to explore more complex SuperClaude capabilities

---

**Remember**: Start simple, practice frequently, and gradually increase complexity. These basic examples form the foundation for all advanced SuperClaude usage.