# SuperClaude Commands Guide

SuperClaude provides 25 commands for Claude Code: `/sc:*` commands for workflows and `@agent-*` for specialists.

## Command Types

| Type | Where Used | Format | Example |
|------|------------|--------|---------|
| **Slash Commands** | Claude Code | `/sc:[command]` | `/sc:implement "feature"` |
| **Agents** | Claude Code | `@agent-[name]` | `@agent-security "review"` |
| **Installation** | Terminal | `SuperClaude [command]` | `SuperClaude install` |

## Quick Test
```bash
# Terminal: Verify installation
python3 -m SuperClaude --version
# Claude Code CLI verification: claude --version

# Claude Code: Test commands
/sc:brainstorm "test project"    # Should ask discovery questions
/sc:analyze README.md           # Should provide analysis
```

**Workflow**: `/sc:brainstorm "idea"` → `/sc:implement "feature"` → `/sc:test`

## 🎯 Understanding SuperClaude Commands

## How SuperClaude Works

SuperClaude provides behavioral context files that Claude Code reads to adopt specialized behaviors. When you type `/sc:implement`, Claude Code reads the `implement.md` context file and follows its behavioral instructions.

**SuperClaude commands are NOT executed by software** - they are context triggers that modify Claude Code's behavior through reading specialized instruction files from the framework.

### Command Types:
- **Slash Commands** (`/sc:*`): Trigger workflow patterns and behavioral modes
- **Agent Invocations** (`@agent-*`): Manually activate specific domain specialists
- **Flags** (`--think`, `--safe-mode`): Modify command behavior and depth

### The Context Mechanism:
1. **User Input**: You type `/sc:implement "auth system"`
2. **Context Loading**: Claude Code reads `~/.claude/superclaude/Commands/implement.md`
3. **Behavior Adoption**: Claude applies domain expertise, tool selection, and validation patterns
4. **Enhanced Output**: Structured implementation with security considerations and best practices

**Key Point**: This creates sophisticated development workflows through context management rather than traditional software execution.

### Installation vs Usage Commands

**🖥️ Terminal Commands** (Actual CLI software):
- `SuperClaude install` - Installs the framework components
- `SuperClaude update` - Updates existing installation  
- `SuperClaude uninstall` - Removes framework installation
- `python3 -m SuperClaude --version` - Check installation status

**💬 Claude Code Commands** (Context triggers):
- `/sc:brainstorm` - Activates requirements discovery context
- `/sc:implement` - Activates feature development context
- `@agent-security` - Activates security specialist context
- All commands work inside Claude Code chat interface only


> **Quick Start**: Try `/sc:brainstorm "your project idea"` → `/sc:implement "feature name"` → `/sc:test` to experience the core workflow.

## 🧪 Testing Your Setup

### 🖥️ Terminal Verification (Run in Terminal/CMD)
```bash
# Verify SuperClaude is working (primary method)
python3 -m SuperClaude --version
# Example output: SuperClaude 4.1.5

# Claude Code CLI version check
claude --version

# Check installed components
python3 -m SuperClaude install --list-components | grep mcp
# Example output: Shows installed MCP components
```

### 💬 Claude Code Testing (Type in Claude Code Chat)
```
# Test basic /sc: command
/sc:brainstorm "test project"
# Example behavior: Interactive requirements discovery starts

# Test command help
/sc:help
# Example behavior: List of available commands
```

**If tests fail**: Check [Installation Guide](../Getting-Started/installation.md) or [Troubleshooting](#troubleshooting)

### 📝 Command Quick Reference

| Command Type | Where to Run | Format | Purpose | Example |
|-------------|--------------|--------|---------|----------|
| **🖥️ Installation** | Terminal/CMD | `SuperClaude [command]` | Setup and maintenance | `SuperClaude install` |
| **🔧 Configuration** | Terminal/CMD | `python3 -m SuperClaude [command]` | Advanced configuration | `python3 -m SuperClaude --version` |
| **💬 Slash Commands** | Claude Code | `/sc:[command]` | Workflow automation | `/sc:implement "feature"` |
| **🤖 Agent Invocation** | Claude Code | `@agent-[name]` | Manual specialist activation | `@agent-security "review"` |
| **⚡ Enhanced Flags** | Claude Code | `/sc:[command] --flags` | Behavior modification | `/sc:analyze --think-hard` |

> **Remember**: All `/sc:` commands and `@agent-` invocations work inside Claude Code chat, not your terminal. They trigger Claude Code to read specific context files from the SuperClaude framework.

## Table of Contents

- [Essential Commands](#essential-commands) - Start here (8 core commands)
- [Common Workflows](#common-workflows) - Command combinations that work
- [Full Command Reference](#full-command-reference) - All 25 commands organized by category
- [Troubleshooting](#troubleshooting) - Common issues and solutions
- [Command Index](#command-index) - Find commands by category

---

## Essential Commands

**Core workflow commands for immediate productivity:**

### `/sc:brainstorm` - Project Discovery
**Purpose**: Interactive requirements discovery and project planning  
**Syntax**: `/sc:brainstorm "your idea"` `[--strategy systematic|creative]`  

**Use Cases**: 
- New project planning: `/sc:brainstorm "e-commerce platform"`
- Feature exploration: `/sc:brainstorm "user authentication system"`  
- Problem solving: `/sc:brainstorm "slow database queries"`

### `/sc:help` - Command Reference
**Purpose**: Displays a list of all available `/sc` commands and their descriptions.
**Syntax**: `/sc:help`

**Use Cases**:
- Discovering available commands: `/sc:help`
- Getting a quick reminder of command names: `/sc:help`

### `/sc:research` - Deep Research Command
**Purpose**: Comprehensive web research with adaptive planning and intelligent search  
**Syntax**: `/sc:research "[query]"` `[--depth quick|standard|deep|exhaustive] [--strategy planning|intent|unified]`

**Use Cases**:
- Technical research: `/sc:research "latest React 19 features" --depth deep`
- Market analysis: `/sc:research "AI coding assistant landscape 2024" --strategy unified`
- Academic investigation: `/sc:research "quantum computing breakthroughs" --depth exhaustive`
- Current events: `/sc:research "latest AI developments 2024"`

**Key Capabilities**:
- **6-Phase Workflow**: Understand → Plan → TodoWrite → Execute → Track → Validate
- **Adaptive Depth**: Quick (basic search), Standard (extended), Deep (comprehensive), Exhaustive (maximum depth)
- **Planning Strategies**: Planning (direct), Intent (clarify first), Unified (collaborative)
- **Parallel Execution**: Default parallel searches and extractions
- **Evidence Management**: Clear citations with relevance scoring
- **Output Standards**: Reports saved to `claudedocs/research_[topic]_[timestamp].md`

### `/sc:implement` - Feature Development  
**Purpose**: Full-stack feature implementation with intelligent specialist routing  
**Syntax**: `/sc:implement "feature description"` `[--type frontend|backend|fullstack] [--focus security|performance]`  

**Use Cases**:
- Authentication: `/sc:implement "JWT login system"`
- UI components: `/sc:implement "responsive dashboard"`
- APIs: `/sc:implement "REST user endpoints"`
- Database: `/sc:implement "user schema with relationships"`

### `/sc:analyze` - Code Assessment
**Purpose**: Comprehensive code analysis across quality, security, and performance  
**Syntax**: `/sc:analyze [path]` `[--focus quality|security|performance|architecture]`

**Use Cases**:
- Project health: `/sc:analyze .`
- Security audit: `/sc:analyze --focus security`
- Performance review: `/sc:analyze --focus performance`

### `/sc:business-panel` - Strategic Business Analysis
**Purpose**: Multi-expert business strategy analysis with 9 renowned thought leaders  
**Syntax**: `/sc:business-panel "content"` `[--mode discussion|debate|socratic] [--experts "name1,name2"]`

**Use Cases**:
- Strategy evaluation: `/sc:business-panel "our go-to-market strategy"`
- Competitive analysis: `/sc:business-panel @competitor_analysis.pdf --mode debate`
- Innovation assessment: `/sc:business-panel "AI product idea" --experts "christensen,drucker"`
- Strategic learning: `/sc:business-panel "competitive strategy" --mode socratic`

**Expert Panel**: Christensen, Porter, Drucker, Godin, Kim/Mauborgne, Collins, Taleb, Meadows, Doumont

### `/sc:spec-panel` - Expert Specification Review
**Purpose**: Multi-expert specification review and improvement using renowned specification and software engineering experts  
**Syntax**: `/sc:spec-panel [content|@file]` `[--mode discussion|critique|socratic] [--focus requirements|architecture|testing|compliance]`

**Use Cases**:
- Specification review: `/sc:spec-panel @api_spec.yml --mode critique --focus requirements,architecture`
- Requirements workshop: `/sc:spec-panel "user story content" --mode discussion`
- Architecture validation: `/sc:spec-panel @microservice.spec.yml --mode socratic --focus architecture`
- Compliance review: `/sc:spec-panel @security_requirements.yml --focus compliance`
- Iterative improvement: `/sc:spec-panel @complex_system.spec.yml --iterations 3`

**Expert Panel**: Wiegers, Adzic, Cockburn, Fowler, Nygard, Newman, Hohpe, Crispin, Gregory, Hightower

### `/sc:troubleshoot` - Problem Diagnosis
**Purpose**: Systematic issue diagnosis with root cause analysis  
**Syntax**: `/sc:troubleshoot "issue description"` `[--type build|runtime|performance]`

**Use Cases**:
- Runtime errors: `/sc:troubleshoot "500 error on login"`
- Build failures: `/sc:troubleshoot --type build`
- Performance problems: `/sc:troubleshoot "slow page load"`

### `/sc:test` - Quality Assurance
**Purpose**: Comprehensive testing with coverage analysis  
**Syntax**: `/sc:test` `[--type unit|integration|e2e] [--coverage] [--fix]`

**Use Cases**:
- Full test suite: `/sc:test --coverage`
- Unit testing: `/sc:test --type unit --watch`
- E2E validation: `/sc:test --type e2e`

### `/sc:improve` - Code Enhancement  
**Purpose**: Apply systematic code improvements and optimizations  
**Syntax**: `/sc:improve [path]` `[--type performance|quality|security] [--preview]`

**Use Cases**:
- General improvements: `/sc:improve src/`
- Performance optimization: `/sc:improve --type performance`
- Security hardening: `/sc:improve --type security`

### `/sc:document` - Documentation Generation
**Purpose**: Generate comprehensive documentation for code and APIs  
**Syntax**: `/sc:document [path]` `[--type api|user-guide|technical] [--format markdown|html]`

**Use Cases**:
- API docs: `/sc:document --type api`
- User guides: `/sc:document --type user-guide`
- Technical docs: `/sc:document --type technical`

### `/sc:workflow` - Implementation Planning
**Purpose**: Generate structured implementation plans from requirements  
**Syntax**: `/sc:workflow "feature description"` `[--strategy agile|waterfall] [--format markdown]`

**Use Cases**:
- Feature planning: `/sc:workflow "user authentication"`
- Sprint planning: `/sc:workflow --strategy agile`
- Architecture planning: `/sc:workflow "microservices migration"`

---

## Common Workflows

**Proven command combinations:**

### New Project Setup
```bash
/sc:brainstorm "project concept"      # Define requirements
/sc:design "system architecture"      # Create technical design  
/sc:workflow "implementation plan"    # Generate development roadmap
```

### Feature Development
```bash
/sc:implement "feature name"          # Build the feature
/sc:test --coverage                   # Validate with tests
/sc:document --type api               # Generate documentation  
```

### Code Quality Improvement
```bash
/sc:analyze --focus quality           # Assess current state
/sc:improve --preview                 # Preview improvements
/sc:test --coverage                   # Validate changes
```

### Bug Investigation
```bash
/sc:troubleshoot "issue description"  # Diagnose the problem
/sc:analyze --focus problem-area      # Deep analysis
/sc:improve --fix --safe-mode         # Apply targeted fixes
```

### Specification Development
```bash
/sc:spec-panel @existing_spec.yml --mode critique  # Expert review
/sc:spec-panel @improved_spec.yml --iterations 2    # Iterative refinement
/sc:document --type technical                        # Generate documentation
```

## Full Command Reference

### Development Commands
| Command | Purpose | Best For |
|---------|---------|----------|
| **workflow** | Implementation planning | Project roadmaps, sprint planning |
| **implement** | Feature development | Full-stack features, API development |
| **build** | Project compilation | CI/CD, production builds |
| **design** | System architecture | API specs, database schemas |

### Analysis Commands  
| Command | Purpose | Best For |
|---------|---------|----------|
| **analyze** | Code assessment | Quality audits, security reviews |
| **research** | Web research with intelligent search | Technical research, current events, market analysis |
| **business-panel** | Strategic analysis | Business decisions, competitive assessment |
| **spec-panel** | Specification review | Requirements validation, architecture analysis |
| **troubleshoot** | Problem diagnosis | Bug investigation, performance issues |
| **explain** | Code explanation | Learning, code reviews |

### Quality Commands
| Command | Purpose | Best For |
|---------|---------|----------|
| **improve** | Code enhancement | Performance optimization, refactoring |
| **cleanup** | Technical debt | Dead code removal, organization |
| **test** | Quality assurance | Test automation, coverage analysis |
| **document** | Documentation | API docs, user guides |

### Project Management
| Command | Purpose | Best For |
|---------|---------|----------|
| **estimate** | Project estimation | Timeline planning, resource allocation |
| **task** | Task management | Complex workflows, task tracking |
| **spawn** | Meta-orchestration | Large-scale projects, parallel execution |

### Utility Commands
| Command | Purpose | Best For |
|---------|---------|----------|
| **help** | List all commands | Discovering available commands |
| **git** | Version control | Commit management, branch strategies |
| **index** | Command discovery | Exploring capabilities, finding commands |

### Session Commands  
| Command | Purpose | Best For |
|---------|---------|----------|
| **load** | Context loading | Session initialization, project onboarding |
| **save** | Session persistence | Checkpointing, context preservation |
| **reflect** | Task validation | Progress assessment, completion validation |
| **select-tool** | Tool optimization | Performance optimization, tool selection |

---

## Command Index

**By Function:**
- **Planning**: brainstorm, design, workflow, estimate
- **Development**: implement, build, git
- **Analysis**: analyze, business-panel, spec-panel, troubleshoot, explain  
- **Quality**: improve, cleanup, test, document
- **Management**: task, spawn, load, save, reflect
- **Utility**: help, index, select-tool

**By Complexity:**
- **Beginner**: brainstorm, implement, analyze, test, help
- **Intermediate**: workflow, design, business-panel, spec-panel, improve, document  
- **Advanced**: spawn, task, select-tool, reflect

## Troubleshooting

**Command Issues:**
- **Command not found**: Verify installation: `python3 -m SuperClaude --version`
- **No response**: Restart Claude Code session
- **Processing delays**: Use `--no-mcp` to test without MCP servers

**Quick Fixes:**
- Reset session: `/sc:load` to reinitialize
- Check status: `SuperClaude install --list-components`
- Get help: [Troubleshooting Guide](../Reference/troubleshooting.md)

## Next Steps

- [Flags Guide](flags.md) - Control command behavior
- [Agents Guide](agents.md) - Specialist activation
- [Examples Cookbook](../Reference/examples-cookbook.md) - Real usage patterns