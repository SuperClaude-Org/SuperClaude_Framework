# SuperClaude Commands Reference

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |

## Command Architecture

SuperClaude provides **18 professional commands** built with an advanced @include template system for maximum efficiency and consistency. All commands support universal flags plus specialized options for their domain.

**Usage Pattern**: `/command [flags] [arguments]`

## Universal Flags (Available on All Commands)

### Planning & Execution Control
- `--plan` - Show detailed execution plan before running
- `--dry-run` - Preview changes without execution
- `--watch` - Continuous monitoring with real-time feedback
- `--interactive` - Step-by-step guided process

### Thinking Depth Control
- `--think` - Multi-file analysis with expanded context (~4K tokens)
- `--think-hard` - Architecture-level depth analysis (~10K tokens)  
- `--ultrathink` - Critical system analysis with maximum depth (~32K tokens)

### Token Optimization
- `--uc` / `--ultracompressed` - Activate UltraCompressed mode (70% token reduction)

### MCP Server Control
- `--c7` / `--no-c7` - Enable/disable Context7 documentation lookup
- `--seq` / `--no-seq` - Enable/disable Sequential thinking analysis
- `--magic` / `--no-magic` - Enable/disable Magic UI component generation
- `--pup` / `--no-pup` - Enable/disable Puppeteer browser automation
- `--all-mcp` - Enable all MCP servers for maximum capability
- `--no-mcp` - Disable all MCP servers (native tools only)

### Quality & Validation
- `--validate` - Enhanced pre-execution safety checks
- `--security` - Security-focused analysis and validation
- `--coverage` - Generate comprehensive coverage analysis
- `--strict` - Zero-tolerance mode with enhanced validation

### Persona Integration  
- `--persona-architect` - Systems architect thinking mode
- `--persona-frontend` - Frontend developer mode (UI/UX focus)
- `--persona-backend` - Backend developer mode (scalability focus)
- `--persona-analyzer` - Deep analysis mode (root cause analysis)
- `--persona-security` - Security-focused mode (threat modeling)
- `--persona-mentor` - Teaching/mentoring mode (guided learning)
- `--persona-refactorer` - Code refactoring mode (quality improvements)
- `--persona-performance` - Performance optimization mode (profiling)
- `--persona-qa` - Quality assurance mode (testing focus)

---

# Development Commands (3)

## `/build` - Universal Project Builder

**Purpose**: Build projects, features, and components using modern stack templates with AI assistance.

### Core Flags
- `--init` - Initialize new project with stack setup (React|API|Fullstack|Mobile|CLI)
- `--feature` - Implement feature using existing patterns and maintain consistency
- `--tdd` - Test-driven development workflow with comprehensive coverage

### Stack & Technology Flags  
- `--react` - React application with Vite, TypeScript, Router, state management
- `--api` - Express.js API with TypeScript, authentication, validation, OpenAPI
- `--fullstack` - Complete React + Node.js + Docker setup
- `--mobile` - React Native with Expo framework
- `--cli` - Commander.js CLI with configuration and testing

### Integration Flags
- `--magic` - Use Magic MCP for AI-generated UI components
- `--watch` - Live reload with continuous building
- `--profile` - Build with performance profiling

### Professional Examples
```bash
# New React application with AI components
/build --init --react --magic --tdd

# Feature implementation with TDD
/build --feature "user authentication" --tdd --coverage

# Full-stack application
/build --init --fullstack --docker --ci

# Mobile application  
/build --init --mobile --expo --testing

# Professional API with documentation
/build --api --openapi --auth --validation --seq
```

**Output**: Working code, tests, documentation, and configuration files
**Location**: Project root with standard directory structure

---

## `/dev-setup` - Development Environment

**Purpose**: Configure professional development environments with CI/CD, monitoring, and team workflows.

### Setup Flags
- `--install` - Install and configure all project dependencies
- `--ci` - CI/CD pipeline configuration (GitHub Actions, GitLab CI)
- `--monitor` - Monitoring and observability setup
- `--docker` - Containerization with Docker and docker-compose
- `--testing` - Testing infrastructure and frameworks

### Team Flags
- `--team` - Team collaboration tools and workflows
- `--standards` - Code quality standards and pre-commit hooks
- `--docs` - Documentation generation and maintenance

### Professional Examples
```bash
# Complete development environment
/dev-setup --install --ci --monitor --docker

# Team collaboration setup
/dev-setup --team --standards --docs --git-hooks

# Production-ready infrastructure
/dev-setup --ci --monitor --security --backup
```

**Output**: Configured development environment, CI/CD pipelines, monitoring setup
**Location**: `.github/`, `docker/`, configuration files

---

## `/test` - Comprehensive Testing Framework

**Purpose**: Create, run, and maintain comprehensive testing strategies across the entire application stack.

### Testing Strategy Flags
- `--coverage` - Generate comprehensive test coverage analysis
- `--e2e` - End-to-end testing with browser automation
- `--integration` - Integration testing for APIs and services  
- `--unit` - Unit testing for individual components and functions
- `--visual` - Visual regression testing for UI components

### Execution Flags
- `--watch` - Auto-test on file changes with live feedback
- `--parallel` - Parallel test execution for faster feedback
- `--verbose` - Detailed test output and debugging information

### Quality Flags
- `--mutation` - Mutation testing for test quality validation
- `--performance` - Performance testing and benchmarking
- `--accessibility` - Accessibility testing compliance

### Professional Examples
```bash
# Comprehensive testing suite
/test --coverage --e2e --integration --unit

# Live development testing
/test --watch --coverage --fast

# Production quality validation
/test --e2e --performance --accessibility --pup

# Test quality assurance
/test --mutation --coverage --strict --persona-qa
```

**Output**: Test results, coverage reports, performance metrics
**Location**: `.claudedocs/test-reports/`, `coverage/`, test files

---

# Analysis & Improvement Commands (4)

## `/analyze` - Multi-Dimensional Analysis

**Purpose**: Perform comprehensive analysis of code, architecture, performance, and security across multiple dimensions.

### Analysis Types
- `--code` - Code quality, structure, complexity, maintainability analysis
- `--architecture` - System design, patterns, scalability assessment
- `--profile` - Performance profiling, bottlenecks, resource usage
- `--security` - Security vulnerabilities, OWASP compliance, threat assessment
- `--deps` - Dependency analysis, vulnerabilities, license compliance

### Analysis Depth
- `--surface` - Quick overview and obvious issues
- `--deep` - Comprehensive analysis with detailed recommendations
- `--forensic` - Detailed investigation for complex issues

### Professional Examples
```bash
# Comprehensive code review
/analyze --code --architecture --security --seq --persona-architect

# Performance investigation  
/analyze --profile --deps --performance --pup --persona-performance

# Security audit
/analyze --security --deps --owasp --strict --persona-security

# System architecture review
/analyze --architecture --scalability --patterns --ultrathink --seq
```

**Output**: Analysis reports, recommendations, metrics, action items
**Location**: `.claudedocs/analysis/`, structured reports with evidence

---

## `/troubleshoot` - Professional Debugging

**Purpose**: Systematic debugging and issue resolution using evidence-based methodologies and root cause analysis.

### Investigation Flags
- `--investigate` - Systematic issue analysis and evidence gathering
- `--five-whys` - Root cause analysis using five-whys methodology
- `--prod` - Production issue debugging with safety protocols
- `--perf` - Performance issue investigation and optimization

### Resolution Flags  
- `--fix` - Complete issue resolution with testing and validation
- `--hotfix` - Emergency production fixes with minimal risk
- `--rollback` - Safe rollback procedures and recovery

### Professional Examples
```bash
# Production issue investigation
/troubleshoot --investigate --prod --five-whys --seq --persona-analyzer

# Performance problem resolution
/troubleshoot --perf --profile --fix --pup --persona-performance

# System failure analysis
/troubleshoot --investigate --architecture --ultrathink --seq

# Emergency production fix
/troubleshoot --prod --hotfix --validate --checkpoint
```

**Output**: Root cause analysis, resolution steps, validation tests
**Location**: `.claudedocs/incidents/`, incident reports with timeline

---

## `/improve` - Enhancement & Optimization

**Purpose**: Evidence-based code and system improvements with measurable outcomes and validation.

### Improvement Types
- `--quality` - Code structure, maintainability, technical debt reduction
- `--performance` - Optimization, caching, resource efficiency
- `--security` - Security hardening, vulnerability remediation
- `--accessibility` - UI/UX accessibility compliance and improvement

### Process Flags
- `--iterate` - Iterative improvement cycles until threshold met
- `--threshold N%` - Set quality/performance targets (default: high)
- `--refactor` - Systematic refactoring with behavior preservation
- `--modernize` - Technology stack and pattern modernization

### Professional Examples
```bash
# Code quality improvement  
/improve --quality --iterate --threshold 95% --persona-refactorer

# Performance optimization
/improve --performance --cache --optimize --pup --persona-performance

# Security hardening
/improve --security --validate --scan --persona-security

# Accessibility compliance
/improve --accessibility --wcag --test --pup --persona-frontend
```

**Output**: Improved code, performance metrics, validation results
**Location**: Updated source files, `.claudedocs/improvements/`

---

## `/explain` - Technical Documentation

**Purpose**: Generate comprehensive technical explanations, documentation, and knowledge transfer materials.

### Explanation Depth
- `--depth [ELI5|beginner|intermediate|expert]` - Explanation complexity level
- `--visual` - Include diagrams, flowcharts, and visual aids
- `--examples` - Practical code examples and real-world usage
- `--interactive` - Interactive explanations with guided exploration

### Documentation Types
- `--api` - API documentation with endpoints and examples
- `--architecture` - System architecture documentation
- `--tutorial` - Step-by-step learning tutorials
- `--reference` - Comprehensive reference documentation

### Professional Examples
```bash
# Technical documentation for team
/explain --depth expert --visual --examples --seq --persona-mentor

# API documentation generation
/explain --api --openapi --examples --c7

# Architecture documentation
/explain --architecture --visual --patterns --seq --persona-architect

# Learning tutorial creation
/explain --tutorial --interactive --examples --persona-mentor
```

**Output**: Documentation, tutorials, API references, diagrams
**Location**: `docs/`, `.claudedocs/explanations/`

---

# Operations Commands (6)

## `/deploy` - Application Deployment

**Purpose**: Safe, professional application deployment with rollback capabilities and environment management.

### Environment Flags
- `--env [dev|staging|prod]` - Target deployment environment
- `--canary` - Canary deployment strategy with gradual rollout
- `--blue-green` - Blue-green deployment for zero downtime
- `--rolling` - Rolling deployment with health checks

### Safety Flags
- `--rollback` - Rollback to previous deployment version
- `--checkpoint` - Create deployment checkpoint before changes
- `--validate` - Pre-deployment validation and health checks
- `--monitor` - Post-deployment monitoring and alerting

### Professional Examples
```bash
# Production deployment with safety
/deploy --env prod --validate --checkpoint --monitor --plan

# Canary deployment strategy
/deploy --env prod --canary --monitor --rollback-ready

# Emergency rollback
/deploy --rollback --env prod --validate --immediate

# Staging deployment for testing
/deploy --env staging --validate --e2e-test
```

**Output**: Deployment status, health checks, rollback procedures
**Location**: `.claudedocs/deployments/`, infrastructure logs

---

## `/migrate` - Database & Code Migration

**Purpose**: Safe database and code migrations with rollback capabilities and data integrity validation.

### Migration Types
- `--database` - Database schema and data migrations
- `--code` - Code structure and API migrations  
- `--config` - Configuration and environment migrations
- `--dependencies` - Dependency and library migrations

### Safety Flags
- `--dry-run` - Preview migration changes without execution
- `--rollback` - Rollback migration with data recovery
- `--backup` - Create backup before migration execution
- `--validate` - Data integrity validation and testing

### Professional Examples
```bash
# Database migration with safety
/migrate --database --dry-run --backup --validate

# Code migration execution
/migrate --code --api-v2 --backward-compatible --test

# Configuration migration
/migrate --config --env --validate --rollback-ready

# Emergency rollback
/migrate --rollback --database --validate --recover
```

**Output**: Migration status, data validation, rollback procedures
**Location**: `migrations/`, `.claudedocs/migrations/`

---

## `/scan` - Security & Validation

**Purpose**: Comprehensive security auditing, vulnerability scanning, and compliance validation.

### Security Scans
- `--security` - General security vulnerability assessment
- `--owasp` - OWASP Top 10 compliance checking
- `--deps` - Dependency vulnerability scanning
- `--secrets` - Secret and credential exposure detection

### Validation Types
- `--validate` - Pre-execution safety and validation checks  
- `--compliance` - Regulatory compliance verification
- `--quality` - Code quality and standards validation
- `--performance` - Performance and resource validation

### Professional Examples
```bash
# Comprehensive security audit
/scan --security --owasp --deps --secrets --persona-security

# Pre-deployment validation
/scan --validate --security --performance --quality

# Compliance checking
/scan --compliance --gdpr --sox --security --strict

# Continuous monitoring
/scan --security --deps --monitor --automated
```

**Output**: Security reports, vulnerability assessments, compliance status
**Location**: `.claudedocs/security/`, security reports with recommendations

---

## `/estimate` - Project Estimation

**Purpose**: Professional project estimation with complexity analysis, resource planning, and risk assessment.

### Estimation Types
- `--detailed` - Comprehensive estimation with breakdown
- `--rough` - Quick estimation for initial planning
- `--worst-case` - Pessimistic estimation with risk factors
- `--agile` - Agile story point estimation

### Analysis Flags
- `--complexity` - Technical complexity assessment
- `--resources` - Resource requirement analysis
- `--timeline` - Timeline and milestone planning
- `--risk` - Risk assessment and mitigation planning

### Professional Examples
```bash
# Comprehensive project estimation
/estimate --detailed --complexity --resources --timeline --seq

# Quick estimation for planning
/estimate --rough --agile --story-points

# Risk-aware estimation
/estimate --worst-case --risk --mitigation --timeline

# Resource planning
/estimate --resources --team --timeline --budget
```

**Output**: Estimation reports, resource plans, timeline analysis
**Location**: `.claudedocs/estimates/`, planning documentation

---

## `/cleanup` - Project Maintenance

**Purpose**: Professional project cleanup and maintenance with safety validations and systematic organization.

### Cleanup Types
- `--code` - Remove dead code, debug statements, unused imports
- `--files` - Clean build artifacts, temporary files, cache
- `--deps` - Remove unused dependencies and outdated packages
- `--git` - Clean git branches, history, and repository optimization

### Scope Flags
- `--all` - Comprehensive cleanup across all categories
- `--aggressive` - Deep cleanup with more extensive changes
- `--conservative` - Safe cleanup with minimal risk
- `--interactive` - Interactive cleanup with user confirmation

### Professional Examples
```bash
# Comprehensive project cleanup
/cleanup --all --validate --backup --dry-run

# Code cleanup and optimization
/cleanup --code --deps --unused --dead-code

# Repository maintenance
/cleanup --git --branches --history --optimize

# Safe production cleanup
/cleanup --conservative --validate --monitoring
```

**Output**: Cleanup reports, space recovered, optimization results
**Location**: Updated project files, `.claudedocs/cleanup/`

---

## `/git` - Git Workflow Management

**Purpose**: Professional Git workflow management with checkpoints, collaborative features, and repository optimization.

### Core Git Operations
- `--status` - Comprehensive repository status and health
- `--commit` - Professional commit with validation and standards
- `--branch` - Branch management and workflow optimization
- `--sync` - Synchronization with remote repositories

### Advanced Features
- `--checkpoint` - Create checkpoint before risky operations
- `--rollback` - Rollback to previous checkpoint or commit
- `--merge` - Smart merge with conflict resolution
- `--history` - Repository history analysis and optimization

### Professional Examples
```bash
# Professional commit workflow
/git --commit --validate --test --message-template

# Checkpoint before risky changes
/git --checkpoint --message "Pre-refactor checkpoint"

# Repository synchronization
/git --sync --fetch --rebase --push --validate

# Branch management
/git --branch --cleanup --optimize --merge-check
```

**Output**: Git operations, commit messages, repository status
**Location**: Git repository, `.claudedocs/git/`

---

# Design & Architecture Commands (1)

## `/design` - System Architecture

**Purpose**: Professional system design with domain-driven design, API specifications, and scalability planning.

### Design Approaches
- `--api` - REST/GraphQL API design with documentation
- `--ddd` - Domain-driven design with bounded contexts
- `--microservices` - Microservices architecture design
- `--event-driven` - Event-driven architecture patterns

### Specification Flags
- `--openapi` - OpenAPI specification generation
- `--graphql` - GraphQL schema design and documentation
- `--bounded-context` - DDD bounded context modeling
- `--integration` - System integration patterns

### Professional Examples
```bash
# API design with documentation
/design --api --openapi --ddd --seq --persona-architect

# Microservices architecture
/design --microservices --event-driven --patterns --ultrathink

# Domain modeling
/design --ddd --bounded-context --aggregates --seq

# System integration design
/design --integration --api --event-driven --scalability
```

**Output**: Architecture documentation, API specifications, design diagrams
**Location**: `docs/architecture/`, `.claudedocs/design/`

---

# Workflow Commands (2)

## `/spawn` - Specialized Agents

**Purpose**: Spawn focused agents for parallel execution of specialized tasks with expertise routing.

### Agent Types
- `--task "description"` - Define specific task with requirements
- `--parallel` - Multiple agents working concurrently
- `--specialized` - Domain-specific expertise routing
- `--collaborative` - Multi-agent collaboration patterns

### Coordination Flags
- `--sync` - Synchronize results between agents
- `--merge` - Merge outputs from multiple agents
- `--monitor` - Monitor agent progress and health
- `--results` - Aggregate and analyze agent results

### Professional Examples
```bash
# Parallel development tasks
/spawn --task "frontend testing" --parallel
/spawn --task "backend optimization" --parallel  
/spawn --task "security audit" --parallel

# Specialized expertise
/spawn --task "performance analysis" --specialized --persona-performance

# Collaborative development
/spawn --collaborative --frontend --backend --qa
```

**Output**: Specialized task results, coordinated outputs
**Location**: `.claudedocs/agents/`, task-specific deliverables

---

## `/document` - Documentation Creation

**Purpose**: Professional documentation creation with multiple formats, audiences, and maintenance strategies.

### Documentation Types
- `--api` - API documentation with examples and specifications
- `--user` - User guides, tutorials, and help documentation
- `--technical` - Technical documentation for developers
- `--architecture` - System architecture and design documentation

### Format Flags
- `--markdown` - Markdown documentation with standards
- `--interactive` - Interactive documentation with examples
- `--visual` - Documentation with diagrams and visual aids
- `--multilingual` - Multi-language documentation support

### Professional Examples
```bash
# API documentation generation
/document --api --openapi --examples --interactive

# User documentation
/document --user --tutorial --visual --accessibility

# Technical documentation
/document --technical --architecture --patterns --seq

# Comprehensive documentation
/document --all --interactive --visual --maintain
```

**Output**: Documentation files, interactive guides, visual aids
**Location**: `docs/`, documentation sites, `.claudedocs/docs/`

---

# System Commands (1)

## `/load` - Project Context Loading

**Purpose**: Load and analyze project context for comprehensive understanding and intelligent assistance.

### Loading Depth
- `--depth [shallow|normal|deep]` - Analysis depth and scope
- `--context` - Context preservation and enhancement
- `--patterns` - Pattern recognition and learning
- `--relationships` - Dependency and relationship analysis

### Analysis Flags
- `--structure` - Project structure and organization analysis
- `--dependencies` - Dependency analysis and mapping
- `--health` - Project health and quality assessment
- `--standards` - Coding standards and pattern analysis

### Professional Examples
```bash
# Deep project analysis
/load --depth deep --patterns --relationships --seq

# Quick context loading
/load --context --structure --health

# Comprehensive project understanding
/load --depth deep --dependencies --standards --analyze

# Pattern recognition for consistency
/load --patterns --standards --conventions --learn
```

**Output**: Project context, analysis summary, pattern recognition
**Location**: `.claudedocs/context/`, project analysis reports

---

# Advanced Usage Patterns

## Command Chaining & Workflows

### Development Lifecycle
```bash
# Complete feature development
/load --depth deep                          # Context
/design --api --ddd --persona-architect     # Architecture
/build --feature --tdd --magic              # Implementation  
/test --coverage --e2e --pup               # Testing
/scan --security --validate                # Security
/deploy --env staging --plan               # Deployment
```

### Quality Assurance Pipeline
```bash
# Comprehensive quality pipeline
/analyze --code --architecture --security   # Analysis
/improve --quality --iterate --threshold 95% # Improvement
/test --coverage --mutation --e2e          # Testing
/scan --validate --compliance              # Validation
/cleanup --code --optimize                 # Cleanup
```

### Production Operations
```bash
# Production deployment pipeline
/git --checkpoint "Pre-production deploy"   # Safety
/scan --security --deps --validate         # Security
/test --e2e --performance --pup            # Validation
/deploy --env prod --canary --monitor      # Deployment
/analyze --performance --monitor           # Post-deploy
```

## Token Optimization Strategies

### UltraCompressed Mode
```bash
# Large project analysis
/analyze --architecture --uc --seq         # Compressed deep analysis
/improve --quality --uc --iterate          # Compressed improvements  
/document --api --uc --visual              # Compressed documentation
```

### MCP Orchestration
```bash
# Maximum capability mode
/build --react --magic --all-mcp           # All MCP servers
/analyze --architecture --seq --c7         # Sequential + Context7
/test --e2e --pup --coverage              # Puppeteer testing
```

### Native-Only Mode
```bash
# Minimal token usage
/analyze --code --no-mcp                   # Native tools only
/improve --quality --no-mcp --uc           # Compressed native
/cleanup --all --no-mcp --dry-run         # Safe native cleanup
```

## Persona-Driven Development

### Architecture-Focused Development
```bash
--persona-architect
/design --api --ddd --microservices        # System design
/analyze --architecture --scalability      # Architecture review
/estimate --complexity --resources         # Planning
```

### Security-First Development
```bash
--persona-security
/scan --security --owasp --deps           # Security audit
/analyze --security --threats             # Threat analysis
/improve --security --harden              # Security hardening
```

### Performance-Optimized Development
```bash
--persona-performance
/analyze --profile --bottlenecks          # Performance analysis
/improve --performance --optimize         # Optimization
/test --performance --load --pup          # Performance testing
```

## Output Organization

### Professional Documentation Structure
```
.claudedocs/
├── analysis/        # Analysis reports and findings
├── deployments/     # Deployment logs and status
├── estimates/       # Project estimation reports
├── incidents/       # Incident reports and resolutions
├── security/        # Security audit reports
├── test-reports/    # Test results and coverage
└── context/         # Project context and patterns

docs/
├── api/            # API documentation
├── architecture/   # System design documentation
├── user/           # User guides and tutorials
└── technical/      # Technical documentation
```

### Quality Assurance Integration
- **Evidence-Based Reports**: All claims backed by metrics and documentation
- **Research-First Methodology**: External libraries require official documentation
- **Validation Patterns**: Pre-execution safety checks and post-execution validation
- **Template System**: @include references ensure consistency and efficiency

---

**SuperClaude v4.0.0** - Professional command framework with 18 commands, 9 personas, advanced MCP integration, and evidence-based methodology for Claude Code excellence.