**Purpose**: SuperClaude Commands Reference

@include shared/universal-constants.yml#Universal_Legend

## Ultra-Compressed Reference
Commands: `/cmd --flags` | 18 total | Universal flags available

@include shared/flag-inheritance.yml#Universal_Always

## Command Categories
**Analysis**: `/analyze` `/scan` `/explain`
**Build**: `/build` `/deploy` `/migrate` 
**Manage**: `/task` `/load` `/cleanup`
**Dev**: `/test` `/troubleshoot` `/improve`
**Utils**: `/design` `/document` `/estimate` `/dev-setup` `/git` `/spawn`

## Commands w/ Primary Flags
**Dev**: `/build` --init|feature|react | `/dev-setup` --install|ci | `/test` --coverage|e2e
**Analysis**: `/analyze` --code|arch | `/troubleshoot` --fix|prod | `/improve` --perf|quality | `/explain` --depth
**Ops**: `/deploy` --env|rollback | `/migrate` --dry-run | `/scan` --security | `/estimate` --detailed | `/cleanup` --all | `/git` --commit|sync
**Design**: `/design` --api|ddd | `/document` --api|user | `/spawn` --task
**Manage**: `/task` --create|status | `/load` --context
## Workflow Patterns
**Setup**: `/load` → `/dev-setup --install` → `/build --init` → `/test`
**Feature**: `/analyze` → `/design --api` → `/build --tdd` → `/test --e2e` → `/deploy`
**Debug**: `/troubleshoot --fix` → `/test` → `/git --commit`
**Quality**: `/analyze --code --think` → `/improve --quality` → `/scan --validate`
**Security**: `/scan --security --owasp` → `/improve` → `/scan --validate`

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
- `command-architecture-patterns.yml`: Command design & architecture patterns
- `compression-performance-patterns.yml`: Token optimization & performance monitoring
- `docs-patterns.yml`: Documentation system & formatting
- `execution-patterns.yml`: Unified workflow, MCP orchestration & lifecycle
- `feature-template.yml`: Task template for feature development
- `quality-patterns.yml`: Validation, error handling & quality control
- `research-patterns.yml`: Research flow & evidence validation
- `security-patterns.yml`: Security patterns & threat controls
- `task-management-patterns.yml`: Task & todo management patterns
- `recovery-state-patterns.yml`: Recovery & state management patterns

**Core System:**
- `flag-inheritance.yml`: Consolidated flag system with inheritance
- `reference-patterns.yml`: Optimized reference system with  shortcuts
- `universal-constants.yml`: Universal constants, symbols & shared values

**Tools:**
- `validate-references.sh`: Reference validation & integrity checking

---