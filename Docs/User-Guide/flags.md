# SuperClaude Flags Guide 🏁

**Most flags activate automatically** - Claude Code reads behavioral instructions to engage appropriate contexts based on keywords and patterns in your requests.

## Essential Auto-Activation Flags (90% of Use Cases)

### Core Analysis Flags
| Flag | When Activated | What It Does |
|------|---------------|--------------|
| `--think` | 5+ files OR complex analysis | Standard structured analysis (~4K tokens) |
| `--think-hard` | Architectural analysis, system dependencies | Deep analysis (~10K tokens) with enhanced tools |
| `--ultrathink` | Critical system redesign, legacy modernization | Maximum depth analysis (~32K tokens) with all tools |

### MCP Server Flags
| Flag | Server | Purpose | Auto-Triggers |
|------|---------|---------|---------------|
| `--c7` / `--context7` | Context7 | Official docs, framework patterns | Library imports, framework questions |
| `--seq` / `--sequential` | Sequential | Multi-step reasoning, debugging | Complex debugging, system design |
| `--magic` | Magic | UI component generation | `/ui` commands, frontend keywords |
| `--play` / `--playwright` | Playwright | Browser testing, E2E validation | Testing requests, visual validation |
| `--chrome` / `--devtools` | Chrome DevTools | Performance analysis, debugging | Performance auditing, debugging, layout issues |
| `--tavily` | Tavily | Web search, real-time info | Web search requests, research queries |
| `--morph` / `--morphllm` | Morphllm | Bulk transformations, pattern edits | Bulk operations, style enforcement |
| `--serena` | Serena | Project memory, symbol operations | Symbol operations, large codebases |

### Behavioral Mode Flags
| Flag | When Activated | What It Does |
|------|---------------|--------------|
| `--brainstorm` | Vague requests, exploration keywords | Collaborative discovery mindset |
| `--introspect` | Self-analysis, error recovery | Expose reasoning process with transparency |
| `--task-manage` | >3 steps, complex scope | Orchestrate through delegation |
| `--orchestrate` | Multi-tool operations, performance needs | Optimize tool selection and parallel execution |
| `--token-efficient` / `--uc` | Context >75%, efficiency needs | Symbol-enhanced communication, 30-50% reduction |

### Execution Control Flags
| Flag | When Activated | What It Does |
|------|---------------|--------------|
| `--loop` | "improve", "polish", "refine" keywords | Iterative enhancement cycles |
| `--safe-mode` | Production, >85% resource usage | Maximum validation, conservative execution |
| `--validate` | Risk >0.7, production environment | Pre-execution risk assessment |
| `--delegate` | >7 directories OR >50 files | Sub-agent parallel processing |

## Command-Specific Flags

### Analysis Command Flags (`/sc:analyze`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--focus` | Target specific domain | `security`, `performance`, `quality`, `architecture` |
| `--depth` | Analysis thoroughness | `quick`, `deep` |
| `--format` | Output format | `text`, `json`, `report` |

### Build Command Flags (`/sc:build`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Build configuration | `dev`, `prod`, `test` |
| `--clean` | Clean before build | Boolean |
| `--optimize` | Enable optimizations | Boolean |
| `--verbose` | Detailed output | Boolean |

### Design Command Flags (`/sc:design`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Design target | `architecture`, `api`, `component`, `database` |
| `--format` | Output format | `diagram`, `spec`, `code` |

### Explain Command Flags (`/sc:explain`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--level` | Complexity level | `basic`, `intermediate`, `advanced` |
| `--format` | Explanation style | `text`, `examples`, `interactive` |
| `--context` | Domain context | Any domain (e.g., `react`, `security`) |

### Improve Command Flags (`/sc:improve`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Improvement focus | `quality`, `performance`, `maintainability`, `style`, `security` |
| `--safe` | Conservative approach | Boolean |
| `--interactive` | User guidance | Boolean |
| `--preview` | Show without executing | Boolean |

### Task Command Flags (`/sc:task`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--strategy` | Task approach | `systematic`, `agile`, `enterprise` |
| `--parallel` | Parallel execution | Boolean |
| `--delegate` | Sub-agent coordination | Boolean |

### Workflow Command Flags (`/sc:workflow`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--strategy` | Workflow approach | `systematic`, `agile`, `enterprise` |
| `--depth` | Analysis depth | `shallow`, `normal`, `deep` |
| `--parallel` | Parallel coordination | Boolean |

### Troubleshoot Command Flags (`/sc:troubleshoot`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Issue category | `bug`, `build`, `performance`, `deployment` |
| `--trace` | Include trace analysis | Boolean |
| `--fix` | Apply fixes | Boolean |

### Cleanup Command Flags (`/sc:cleanup`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Cleanup target | `code`, `imports`, `files`, `all` |
| `--safe` / `--aggressive` | Cleanup intensity | Boolean |
| `--interactive` | User guidance | Boolean |
| `--preview` | Show without executing | Boolean |

### Estimate Command Flags (`/sc:estimate`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Estimate focus | `time`, `effort`, `complexity` |
| `--unit` | Time unit | `hours`, `days`, `weeks` |
| `--breakdown` | Detailed breakdown | Boolean |

### Index Command Flags (`/sc:index`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Index target | `docs`, `api`, `structure`, `readme` |
| `--format` | Output format | `md`, `json`, `yaml` |

### Reflect Command Flags (`/sc:reflect`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--type` | Reflection scope | `task`, `session`, `completion` |
| `--analyze` | Include analysis | Boolean |
| `--validate` | Validate completeness | Boolean |

### Spawn Command Flags (`/sc:spawn`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--strategy` | Coordination approach | `sequential`, `parallel`, `adaptive` |
| `--depth` | Analysis depth | `normal`, `deep` |

### Git Command Flags (`/sc:git`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--smart-commit` | Generate commit message | Boolean |
| `--interactive` | Guided operations | Boolean |

### Select-Tool Command Flags (`/sc:select-tool`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--analyze` | Tool analysis | Boolean |
| `--explain` | Explain selection | Boolean |

### Test Command Flags (`/sc:test`)
| Flag | Purpose | Values |
|------|---------|--------|
| `--coverage` | Include coverage | Boolean |
| `--type` | Test type | `unit`, `integration`, `e2e` |
| `--watch` | Watch mode | Boolean |

## Advanced Control Flags

### Scope and Focus
| Flag | Purpose | Values |
|------|---------|--------|
| `--scope` | Analysis boundary | `file`, `module`, `project`, `system` |
| `--focus` | Domain targeting | `performance`, `security`, `quality`, `architecture`, `accessibility`, `testing` |

### Execution Control
| Flag | Purpose | Values |
|------|---------|--------|
| `--concurrency [n]` | Control parallel ops | 1-15 |
| `--iterations [n]` | Improvement cycles | 1-10 |
| `--all-mcp` | Enable all MCP servers | Boolean |
| `--no-mcp` | Native tools only | Boolean |
| `--frontend-verify` | UI testing, frontend debugging, layout validation | Enable Playwright + Chrome DevTools + Serena |

### System Flags (SuperClaude Installation)
| Flag | Purpose | Values |
|------|---------|--------|
| `--verbose` / `-v` | Verbose logging | Boolean |
| `--quiet` / `-q` | Suppress output | Boolean |
| `--dry-run` | Simulate operation | Boolean |
| `--force` | Skip checks | Boolean |
| `--yes` / `-y` | Auto-confirm | Boolean |
| `--install-dir` | Target directory | Path |
| `--legacy` | Use legacy script | Boolean |
| `--version` | Show version | Boolean |
| `--help` | Show help | Boolean |

## Common Usage Patterns

### Frontend Development
```bash
/sc:implement "responsive dashboard" --magic --c7
/sc:design component-library --type component --format code
/sc:test ui-components/ --magic --play
/sc:improve legacy-ui/ --magic --morph --validate
```

### Backend Development
```bash
/sc:analyze api/ --focus performance --seq --think
/sc:design payment-api --type api --format spec
/sc:troubleshoot "API timeout" --type performance --trace
/sc:improve auth-service --type security --validate
```

### Large Projects
```bash
/sc:analyze . --ultrathink --all-mcp --safe-mode
/sc:workflow enterprise-system --strategy enterprise --depth deep
/sc:cleanup . --type all --safe --interactive
/sc:estimate "migrate to microservices" --type complexity --breakdown
```

### Quality & Maintenance
```bash
/sc:improve src/ --type quality --safe --interactive
/sc:cleanup imports --type imports --preview
/sc:reflect --type completion --validate
/sc:git commit --smart-commit
```

## Flag Interactions

### Compatible Combinations
- `--think` + `--c7`: Analysis with documentation
- `--magic` + `--play`: UI generation with testing
- `--serena` + `--morph`: Project memory with transformations
- `--safe-mode` + `--validate`: Maximum safety
- `--loop` + `--validate`: Iterative improvement with validation

### Conflicting Flags
- `--all-mcp` vs individual MCP flags (use one or the other)
- `--no-mcp` vs any MCP flags (--no-mcp wins)
- `--safe` vs `--aggressive` (cleanup intensity)
- `--quiet` vs `--verbose` (output level)

### Auto-Enabling Relationships
- `--safe-mode` auto-enables `--uc` and `--validate`
- `--ultrathink` auto-enables all MCP servers
- `--think-hard` auto-enables `--seq` + `--c7`
- `--magic` triggers UI-focused agents

## Troubleshooting Flags

### Common Issues
- **Too many tools**: Use `--no-mcp` to test with native tools only
- **Operation too slow**: Add `--uc` to compress output
- **Validation blocking**: Use `--validate` instead of `--safe-mode` in development
- **Context pressure**: Auto-activates `--token-efficient` at >75% usage

### Debug Flags
```bash
/sc:analyze . --verbose                      # Shows decision logic and flag activation
/sc:select-tool "operation" --explain        # Explains tool selection process
/sc:reflect --type session --analyze         # Reviews current session decisions
```

### Quick Fixes
```bash
/sc:analyze . --help                         # Shows available flags for command
/sc:analyze . --no-mcp                       # Native execution only
/sc:cleanup . --preview                      # Shows what would be cleaned
```

## Flag Priority Rules

1. **Safety First**: `--safe-mode` > `--validate` > optimization flags
2. **Explicit Override**: User flags > auto-detection
3. **Depth Hierarchy**: `--ultrathink` > `--think-hard` > `--think`  
4. **MCP Control**: `--no-mcp` overrides all individual MCP flags
5. **Scope Precedence**: system > project > module > file

## Related Resources
- [Commands Guide](commands.md) - Commands that use these flags
- [MCP Servers Guide](mcp-servers.md) - Understanding MCP flag activation
- [Session Management](session-management.md) - Using flags with persistent sessions