# /index - SuperClaude Commands Reference

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |
| > | greater than | | val | validation |
| ∀ | for all/every | | req | requirements |
| ∃ | exists/there is | | deps | dependencies |
| ∴ | therefore | | env | environment |
| ∵ | because | | db | database |
| ≡ | equivalent | | api | interface |
| ≈ | approximately | | docs | documentation |
| 📁 | directory/path | | std | standard |
| 🔢 | number/count | | def | default |
| 📝 | text/string | | ctx | context |
| ⚙ | setting/config | | err | error |
| 🎛 | control/flags | | exec | execution |
| 🔧 | configuration | | qual | quality |
| 📋 | group/category | | rec | recovery |
| 🚨 | critical/urgent | | sev | severity |
| ⚠ | warning/caution | | resp | response |
| 🔄 | retry/recovery | | esc | escalation |
| ✅ | success/fixed | | tok | token |
| ❌ | failure/error | | opt | optimization |
| ℹ | information | | UX | user experience |
| ⚡ | fast/quick | | UI | user interface |
| 🐌 | slow/delayed | | C | critical |
| ✨ | complete/done | | H | high |
| 📖 | read operation | | M | medium |
| ✏ | edit operation | | L | low |
| 🗑 | delete operation | | |

## Purpose
Comprehensive reference guide for all SuperClaude commands, workflows, and system capabilities.

## Optimization Update (v4.0.0)
🎯 **Major Streamlining Completed**: All 18 command files optimized using @include references
- **Token Reduction**: ~70% reduction in command file size
- **Maintainability**: Single source of truth for all shared content
- **Consistency**: Guaranteed uniformity across commands
- **Reference System**: Commands now use shared patterns from `shared/*.yml` files

@include shared/flag-inheritance.yml#Universal_Always
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"

## Command Usage
All commands use `/` prefix. Examples:
- `/build --init` | `/analyze --code` | `/deploy --env prod`

## Universal Flags (All Commands)

**Planning & Thinking:**
- `--plan` - Show execution plan before running
- `--think` - Standard analysis mode (multi-file context, ~4K tokens)
- `--think-hard` - Deep analysis mode (architecture level, ~10K tokens)
- `--ultrathink` - Critical analysis mode (system-wide, ~32K tokens)

**Documentation Control:**
- `--ultracompressed` / `--uc` - ~70% token reduction mode w/ telegram-style formatting

**MCP Server Control:**
- `--c7` / `--no-c7` - Enable/disable Context7 docs lookup
- `--seq` / `--no-seq` - Enable/disable Sequential thinking analysis
- `--magic` / `--no-magic` - Enable/disable Magic UI component builder
- `--pup` / `--no-pup` - Enable/disable Puppeteer browser automation
- `--all-mcp` - Enable all MCP servers→maximum capability
- `--no-mcp` - Disable all MCP servers (native tools only)

## Development Commands (3)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /build | Universal project builder | --init --feature --react --api --tdd |
| /dev-setup | Dev environment & CI/CD | --install --ci --monitor |
| /test | Testing framework | --coverage --watch --e2e |

## Analysis & Improvement Commands (4)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /analyze | Multi-dimensional analysis | --code --architecture --profile --security |
| /troubleshoot | Debug and fix issues | --investigate --fix --five-whys --prod |
| /improve | Enhance code/performance | --quality --performance --iterate --threshold |
| /explain | Deep explanations | --depth --visual --examples |

## Operations Commands (6)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /deploy | Application deployment | --env --rollback |
| /migrate | Database/code migration | --dry-run --rollback |
| /scan | Security & validation | --validate --security --owasp --deps |
| /estimate | Time/complexity predictions | --detailed --worst-case |
| /cleanup | Project cleanup & maintenance | --code --files --deps --git --all --dry-run |
| /git | Git workflow management | --status --commit --branch --sync --merge --stash --history --checkpoint --rollback |

## Design & Architecture Commands (1)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /design | System design | --api --ddd --prd --openapi --graphql --bounded-context |

## Workflow Commands (2)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /spawn | Spawn focused agent | --task |
| /document | Documentation creation | --api --user |

## System Commands (1)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /load | Load project context | --depth |

## Quick Reference & Workflow Examples

### Common Development Flows
```yaml
Project Setup:
  New Project: /load → /dev-setup --install → /build --init → /test --coverage
  Existing: /load --depth deep → /analyze --architecture → /design
  
Full Development Cycle:
  Feature: /load → /analyze → /design --api → /build --tdd → /test --e2e → /deploy
  Bug Fix: /troubleshoot --investigate → /troubleshoot --fix → /test → /git --commit
  Refactor: /analyze --code → /improve --quality → /test --coverage → /git --commit
  
Quality Workflows:
  Code Review: /analyze --code --think → /improve --quality → /scan --validate
  Performance: /analyze --profile → /improve --performance --iterate → /test
  Security: /scan --security --owasp → /improve --quality → /scan --validate
  
Maintenance:
  Cleanup: /cleanup --all --dry-run → /cleanup --all → /analyze → /test
  Update: /migrate --dry-run → /migrate → /test --coverage → /deploy --env staging
  Monitor: /analyze --performance --watch → /improve --threshold 90%
```

### Advanced Flag Combinations
```yaml
Power User Patterns:
  Deep Analysis: /analyze --architecture --seq --think-hard
  UI Development: /build --react --magic --pup --watch
  Production Deploy: /scan --validate --seq → /deploy --env prod --think-hard
  Emergency Debug: /troubleshoot --prod --ultrathink --seq
  
Research & Learning:
  Library Study: /explain --c7 --seq --depth expert "React hooks"
  Architecture: /design --ddd --seq --think-hard → /document --api
  Performance: /analyze --profile --seq → /improve --iterate --threshold 95%
  
Token Optimization:
  Compressed Docs: /document --uc → /explain --uc --c7
  Efficient Analysis: /analyze --uc --no-mcp → /improve --uc
  Rapid Workflow: /build --uc → /test --uc → /deploy --uc
```

### Safety & Best Practices
```yaml
Pre-Deployment Safety:
  Full Gate: /test --coverage → /scan --security → /scan --validate → /deploy
  Staged: /deploy --env staging → /test --e2e → /deploy --env prod --plan
  Rollback Ready: /git --checkpoint → /deploy → (if issues) /deploy --rollback
  
Development Safety:
  Clean First: /cleanup --code → /build → /test → /git --commit
  Quality Gate: /analyze → /improve --quality → /test → /git --commit
  Secure: /scan --security → fix issues → /scan --validate
  
Planning for Complex Operations:
  Architecture: /design --api --ddd --plan --think-hard
  Migration: /migrate --dry-run → /migrate --plan → verify
  Cleanup: /cleanup --all --dry-run → review → /cleanup --all
```

## Shared Resources (12 core files)

**Pattern Files:**
- `architecture-patterns.yml`: DDD/microservices/event patterns
- `command-patterns.yml`: Reusable command patterns & templates
- `compression-patterns.yml`: Token reduction & UltraCompressed mode
- `docs-patterns.yml`: Documentation system & formatting
- `execution-patterns.yml`: Unified workflow, MCP orchestration & lifecycle
- `quality-patterns.yml`: Validation, error handling & quality control
- `research-patterns.yml`: Research flow & evidence validation
- `security-patterns.yml`: Security patterns & threat controls
- `task-patterns.yml`: Task management & workflow patterns

**Core System:**
- `flag-inheritance.yml`: Consolidated flag system with inheritance
- `reference-patterns.yml`: Optimized reference system with  shortcuts
- `universal-constants.yml`: Universal constants, symbols & shared values

**Templates & Tools:**
- `feature-template.md`: Standard feature development template
- `task-ultracompressed.md`: Ultra-compressed task template
- `validate-references.sh`: Reference validation & integrity checking

---
*SuperClaude v4.0.0 - 18 commands with comprehensive configuration framework*