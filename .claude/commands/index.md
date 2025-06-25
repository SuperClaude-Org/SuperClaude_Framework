# Command Directory & Navigation

@include shared/constants.yml#Process_Symbols

## Command Usage
All commands use `/user:` prefix. Examples:
- `/user:build --init` | `/user:analyze --code` | `/user:deploy --env prod`

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
| /user:build | Universal project builder | --init --feature --react --api --tdd |
| /user:dev-setup | Dev environment & CI/CD | --install --ci --monitor |
| /user:test | Testing framework | --coverage --watch --e2e |

## Analysis & Improvement Commands (4)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /user:analyze | Multi-dimensional analysis | --code --architecture --profile --security |
| /user:troubleshoot | Debug and fix issues | --investigate --fix --five-whys --prod |
| /user:improve | Enhance code/performance | --quality --performance --iterate --threshold |
| /user:explain | Deep explanations | --depth --visual --examples |

## Operations Commands (6)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /user:deploy | Application deployment | --env --rollback |
| /user:migrate | Database/code migration | --dry-run --rollback |
| /user:scan | Security & validation | --validate --security --owasp --deps |
| /user:estimate | Time/complexity predictions | --detailed --worst-case |
| /user:cleanup | Project cleanup & maintenance | --code --files --deps --git --all --dry-run |
| /user:git | Git workflow management | --status --commit --branch --sync --merge --stash --history --checkpoint --rollback |

## Design & Architecture Commands (1)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /user:design | System design | --api --ddd --prd --openapi --graphql --bounded-context |

## Workflow Commands (2)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /user:spawn | Spawn focused agent | --task |
| /user:document | Documentation creation | --api --user |

## System Commands (1)
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| /user:load | Load project context | --depth |

## Quick Reference & Workflow Examples

### Common Development Flows
```yaml
Project Setup:
  New Project: load → dev-setup --install → build --init → test --coverage
  Existing: load --depth deep → analyze --architecture → design

Full Development Cycle:
  Feature: load → analyze → design --api → build --tdd → test --e2e → deploy
  Bug Fix: troubleshoot --investigate → troubleshoot --fix → test → git --commit
  Refactor: analyze --code → improve --quality → test --coverage → git --commit

Quality Workflows:
  Code Review: analyze --code --think → improve --quality → scan --validate
  Performance: analyze --profile → improve --performance --iterate → test
  Security: scan --security --owasp → improve --quality → scan --validate

Maintenance:
  Cleanup: cleanup --all --dry-run → cleanup --all → analyze → test
  Update: migrate --dry-run → migrate → test --coverage → deploy --env staging
  Monitor: analyze --performance --watch → improve --threshold 90%
```

### Advanced Flag Combinations
```yaml
Power User Patterns:
  Deep Analysis: analyze --architecture --seq --think-hard
  UI Development: build --react --magic --pup --watch
  Production Deploy: scan --validate --seq → deploy --env prod --think-hard
  Emergency Debug: troubleshoot --prod --ultrathink --seq

Research & Learning:
  Library Study: explain --c7 --seq --depth expert "React hooks"
  Architecture: design --ddd --seq --think-hard → document --api
  Performance: analyze --profile --seq → improve --iterate --threshold 95%

Token Optimization:
  Compressed Docs: document --uc → explain --uc --c7
  Efficient Analysis: analyze --uc --no-mcp → improve --uc
  Rapid Workflow: build --uc → test --uc → deploy --uc
```

### Safety & Best Practices
```yaml
Pre-Deployment Safety:
  Full Gate: test --coverage → scan --security → scan --validate → deploy
  Staged: deploy --env staging → test --e2e → deploy --env prod --plan
  Rollback Ready: git --checkpoint → deploy → (if issues) deploy --rollback

Development Safety:
  Clean First: cleanup --code → build → test → commit
  Quality Gate: analyze → improve --quality → test → commit
  Secure: scan --security → fix issues → scan --validate

Planning for Complex Operations:
  Architecture: design --api --ddd --plan --think-hard
  Migration: migrate --dry-run → migrate --plan → verify
  Cleanup: cleanup --all --dry-run → review → cleanup --all
```

## Shared Resources (37 files)
- `ambiguity-check.yml`: Ambiguity detection & resolution
- `audit.yml`: Audit configurations & logging
- `checkpoint.yml`: Checkpoint management & rollback
- `cleanup-patterns.yml`: Cleanup safety rules & patterns
- `command-memory.yml`: Enhanced command result sharing & context management
- `command-templates.yml`: Token-optimized reusable command patterns
- `constants.yml`: Universal constants & shared values
- `documentation-dirs.yml`: Documentation directory standards
- `error-handling.yml`: Error handling & resilience patterns
- `evidence.yml`: Evidence tracking & validation
- `execution-lifecycle.yml`: Command execution flow & lifecycle management
- `git-workflow.yml`: Git integration patterns
- `implementation.yml`: Implementation hooks & behaviors
- `loading-config.yml`: Token optimization & lazy loading
- `mcp-flags.yml`: Enhanced MCP server control via flags
- `patterns.yml`: Enhanced common workflows & command integration patterns
- `performance.yml`: Performance monitoring & metrics
- `planning-mode.yml`: Risk assessment & planning configuration
- `research-first.yml`: Mandatory research & documentation requirements
- `severity-levels.yml`: Severity classification & escalation paths
- `task-system.yml`: Comprehensive task management & workflow system
- `thinking-modes.yml`: Thinking depth configuration & flags
- `ultracompressed.yml`: ~70% token reduction documentation mode
- `user-experience.yml`: User interface & interaction patterns (NEW)
- `validation.yml`: Validation rules & standards
- `workflow-chains.yml`: Command chaining & orchestration patterns (NEW)

---
*SuperClaude v4.0.0 - 18 commands with comprehensive configuration framework*