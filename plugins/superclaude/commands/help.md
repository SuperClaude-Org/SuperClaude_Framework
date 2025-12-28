---
name: help
description: "List all available /sc commands and their functionality"
category: utility
complexity: low
mcp-servers: []
personas: []
---

# /sc:help - Command Reference Documentation

## Triggers
- Command discovery and reference lookup requests
- Framework exploration and capability understanding needs
- Documentation requests for available SuperClaude commands

## Behavioral Flow
1. **Display**: Present complete command list with descriptions
2. **Complete**: End interaction after displaying information

Key behaviors:
- Information display only - no execution or implementation
- Reference documentation mode without action triggers

Here is a complete list of all available SuperClaude (`/sc`) commands.

| Command | Description |
|---|---|
| `/sc:analyze` | Comprehensive code analysis across quality, security, performance, and architecture domains |
| `/sc:brainstorm` | Interactive requirements discovery through Socratic dialogue and systematic exploration |
| `/sc:build` | Build, compile, and package projects with intelligent error handling and optimization |
| `/sc:business-panel` | Multi-expert business analysis with adaptive interaction modes |
| `/sc:cleanup` | Systematically clean up code, remove dead code, and optimize project structure |
| `/sc:design` | Design system architecture, APIs, and component interfaces with comprehensive specifications |
| `/sc:document` | Generate focused documentation for components, functions, APIs, and features |
| `/sc:estimate` | Provide development estimates for tasks, features, or projects with intelligent analysis |
| `/sc:explain` | Provide clear explanations of code, concepts, and system behavior with educational clarity |
| `/sc:git` | Git operations with intelligent commit messages and workflow optimization |
| `/sc:help` | List all available /sc commands and their functionality |
| `/sc:implement` | Feature and code implementation with intelligent persona activation and MCP integration |
| `/sc:improve` | Apply systematic improvements to code quality, performance, and maintainability |
| `/sc:index` | Generate comprehensive project documentation and knowledge base with intelligent organization |
| `/sc:load` | Session lifecycle management with Serena MCP integration for project context loading |
| `/sc:reflect` | Task reflection and validation using Serena MCP analysis capabilities |
| `/sc:save` | Session lifecycle management with Serena MCP integration for session context persistence |
| `/sc:select-tool` | Intelligent MCP tool selection based on complexity scoring and operation analysis |
| `/sc:spawn` | Meta-system task orchestration with intelligent breakdown and delegation |
| `/sc:spec-panel` | Multi-expert specification review and improvement using renowned specification and software engineering experts |
| `/sc:task` | Execute complex tasks with intelligent workflow management and delegation |
| `/sc:test` | Execute tests with coverage analysis and automated quality reporting |
| `/sc:troubleshoot` | Diagnose and resolve issues in code, builds, deployments, and system behavior |
| `/sc:workflow` | Generate structured implementation workflows from PRDs and feature requirements |

## SuperClaude Framework Flags

SuperClaude supports behavioral flags to enable specific execution modes and tool selection patterns. Use these flags with any `/sc` command to customize behavior.

### Mode Activation Flags

| Flag | Trigger | Behavior |
|------|---------|----------|
| `--brainstorm` | Vague project requests, exploration keywords | Activate collaborative discovery mindset, ask probing questions |
| `--introspect` | Self-analysis requests, error recovery | Expose thinking process with transparency markers |
| `--task-manage` | Multi-step operations (>3 steps) | Orchestrate through delegation, systematic organization |
| `--orchestrate` | Multi-tool operations, parallel execution | Optimize tool selection matrix, enable parallel thinking |
| `--token-efficient` | Context usage >75%, large-scale operations | Symbol-enhanced communication, 30-50% token reduction |

### MCP Server Flags

| Flag | Trigger | Behavior |
|------|---------|----------|
| `--c7` / `--context7` | Library imports, framework questions | Enable Context7 for curated documentation lookup |
| `--seq` / `--sequential` | Complex debugging, system design | Enable Sequential for structured multi-step reasoning |
| `--magic` | UI component requests (/ui, /21) | Enable Magic for modern UI generation from 21st.dev |
| `--morph` / `--morphllm` | Bulk code transformations | Enable Morphllm for efficient multi-file pattern application |
| `--serena` | Symbol operations, project memory | Enable Serena for semantic understanding and session persistence |
| `--play` / `--playwright` | Browser testing, E2E scenarios | Enable Playwright for real browser automation and testing |
| `--all-mcp` | Maximum complexity scenarios | Enable all MCP servers for comprehensive capability |
| `--no-mcp` | Native-only execution needs | Disable all MCP servers, use native tools |

### Analysis Depth Flags

| Flag | Trigger | Behavior |
|------|---------|----------|
| `--think` | Multi-component analysis needs | Standard structured analysis (~4K tokens), enables Sequential |
| `--think-hard` | Architectural analysis, system-wide dependencies | Deep analysis (~10K tokens), enables Sequential + Context7 |
| `--ultrathink` | Critical system redesign, legacy modernization | Maximum depth analysis (~32K tokens), enables all MCP servers |

### Execution Control Flags

| Flag | Trigger | Behavior |
|------|---------|----------|
| `--delegate [auto\|files\|folders]` | >7 directories OR >50 files | Enable sub-agent parallel processing with intelligent routing |
| `--concurrency [n]` | Resource optimization needs | Control max concurrent operations (range: 1-15) |
| `--loop` | Improvement keywords (polish, refine, enhance) | Enable iterative improvement cycles with validation gates |
| `--iterations [n]` | Specific improvement cycle requirements | Set improvement cycle count (range: 1-10) |
| `--validate` | Risk score >0.7, resource usage >75% | Pre-execution risk assessment and validation gates |
| `--safe-mode` | Resource usage >85%, production environment | Maximum validation, conservative execution |

### Output Optimization Flags

| Flag | Trigger | Behavior |
|------|---------|----------|
| `--uc` / `--ultracompressed` | Context pressure, efficiency requirements | Symbol communication system, 30-50% token reduction |
| `--scope [file\|module\|project\|system]` | Analysis boundary needs | Define operational scope and analysis depth |
| `--focus [performance\|security\|quality\|architecture\|accessibility\|testing]` | Domain-specific optimization | Target specific analysis domain and expertise application |

### Flag Priority Rules

- **Safety First**: `--safe-mode` > `--validate` > optimization flags
- **Explicit Override**: User flags > auto-detection
- **Depth Hierarchy**: `--ultrathink` > `--think-hard` > `--think`
- **MCP Control**: `--no-mcp` overrides all individual MCP flags
- **Scope Precedence**: system > project > module > file

### Usage Examples

```bash
# Deep analysis with Context7 enabled
/sc:analyze --think-hard --context7 src/

# UI development with Magic and validation
/sc:implement --magic --validate "Add user dashboard"

# Token-efficient task management
/sc:task --token-efficient --delegate auto "Refactor authentication system"

# Safe production deployment
/sc:build --safe-mode --validate --focus security
```

## Boundaries

**Will:**
- Display comprehensive list of available SuperClaude commands
- Provide clear descriptions of each command's functionality
- Present information in readable tabular format
- Show all available SuperClaude framework flags and their usage
- Provide flag usage examples and priority rules

**Will Not:**
- Execute any commands or create any files
- Activate implementation modes or start projects
- Engage TodoWrite or any execution tools

---

**Note:** This list is manually generated and may become outdated. If you suspect it is inaccurate, please consider regenerating it or contacting a maintainer.
