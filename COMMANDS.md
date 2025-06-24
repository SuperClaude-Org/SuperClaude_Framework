# SuperClaude Commands Reference

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |

## Quick Reference
All commands use `/` prefix. Built with @pattern template system for significant efficiency gains.

Example: `/analyze --code --security --think`

## Universal Flags (Apply to All Commands)

### Planning & Thinking
- `--plan` - Show execution plan before running
- `--think` - Multi-file analysis (moderate depth)
- `--think-hard` - Architecture-level depth (comprehensive)
- `--ultrathink` - Critical system analysis (maximum depth)

### Documentation Control
- `--uc` / `--ultracompressed` - Substantial token reduction mode

### MCP Server Control
- `--c7` / `--no-c7` - Enable/disable Context7 docs lookup
- `--seq` / `--no-seq` - Enable/disable Sequential thinking
- `--magic` / `--no-magic` - Enable/disable Magic UI generation
- `--pup` / `--no-pup` - Enable/disable Puppeteer browser automation
- `--all-mcp` - Enable all MCP servers
- `--no-mcp` - Disable all MCP servers (native tools only)

## Development Commands (3)

### `/build` - Universal project builder
- `--init` - Initialize new project
- `--feature` - Feature implementation
- `--react` - React application
- `--api` - API with documentation
- `--tdd` - Test-driven development
- `--magic` - AI-generated UI components
- `--watch` - Live reload mode

### `/dev-setup` - Development environment
- `--install` - Install dependencies
- `--ci` - CI/CD configuration
- `--monitor` - Monitoring setup

### `/test` - Testing framework
- `--coverage` - Code coverage analysis
- `--watch` - Auto-test on changes
- `--e2e` - End-to-end tests
- `--integration` - Integration tests
- `--interactive` - Real-time feedback

## Analysis & Improvement Commands (4)

### `/analyze` - Multi-dimensional analysis
- `--code` - Code quality review
- `--architecture` - System architecture analysis
- `--profile` - Performance profiling
- `--security` - Security assessment
- `--watch` - Continuous monitoring

### `/troubleshoot` - Debug and fix issues
- `--investigate` - Issue analysis
- `--fix` - Complete bug fixing
- `--five-whys` - Root cause analysis
- `--prod` - Production issues

### `/improve` - Enhancement & optimization
- `--quality` - Code structure improvement
- `--performance` - Performance optimization
- `--iterate` - Iterative improvement
- `--threshold N%` - Quality threshold (default: high)

### `/explain` - Technical explanations
- `--depth [ELI5/Beginner/Intermediate/Expert]` - Explanation depth
- `--visual` - Include diagrams
- `--examples` - Code examples

## Operations Commands (6)

### `/deploy` - Application deployment
- `--env [dev/staging/prod]` - Target environment
- `--rollback` - Revert deployment

### `/migrate` - Database/code migration
- `--dry-run` - Preview changes
- `--rollback` - Revert migration

### `/scan` - Security & validation
- `--validate` - Pre-execution safety checks
- `--security` - Security audit
- `--owasp` - OWASP compliance
- `--deps` - Dependency vulnerabilities

### `/estimate` - Time/complexity predictions
- `--detailed` - Comprehensive estimation
- `--worst-case` - Pessimistic scenarios

### `/cleanup` - Project maintenance
- `--code` - Remove dead code, debug logs
- `--files` - Clean build artifacts
- `--deps` - Remove unused dependencies
- `--git` - Clean branches/history
- `--all` - Comprehensive cleanup
- `--dry-run` - Preview changes

### `/git` - Git workflow management
- `--status` - Repository status
- `--commit` - Commit changes
- `--branch` - Branch management
- `--sync` - Fetch/pull/push operations
- `--merge` - Merge branches
- `--stash` - Temporary changes
- `--history` - Commit history
- `--checkpoint` - Create snapshot
- `--rollback` - Revert to checkpoint

## Design & Architecture Commands (1)

### `/design` - System design
- `--api` - REST/GraphQL API design
- `--ddd` - Domain-driven design
- `--prd` - Product requirements
- `--openapi` - OpenAPI specification
- `--graphql` - GraphQL schema
- `--bounded-context` - DDD bounded contexts

## Workflow Commands (2)

### `/spawn` - Spawn focused agent
- `--task "description"` - Define specific task
- Parallel execution capability
- Specialized expertise routing

### `/document` - Documentation creation
- `--api` - API documentation
- `--user` - User guides

## System Commands (1)

### `/load` - Load project context
- `--depth [shallow/normal/deep]` - Analysis depth

## Common Workflow Patterns

### New Project Setup
```bash
/load --depth deep
/dev-setup --install
/build --init --tdd
/test --coverage
```

### Feature Development
```bash
/design --api --ddd
/build --feature --tdd --magic
/test --e2e --coverage
/git --commit
```

### Debugging Flow
```bash
/troubleshoot --investigate --prod
/analyze --profile
/improve --performance
/test --integration
```

### Code Review & Quality
```bash
/analyze --code --security
/improve --quality
/scan --validate
/cleanup --code --dry-run
```

### Production Deployment
```bash
/scan --security --deps
/test --e2e --coverage
/deploy --env staging
/deploy --env prod --plan
```

## Output Locations
- **Reports**: `.claudedocs/reports/`
- **Metrics**: `.claudedocs/metrics/`
- **Tasks**: `.claudedocs/tasks/`
- **Documentation**: `docs/`

## Advanced Usage

### Thinking Mode Combinations
- `--think --c7` - Research-backed analysis
- `--think-hard --seq` - Deep sequential reasoning
- `--ultrathink --all-mcp` - Maximum analysis power

### Token Optimization
- `--uc --no-mcp` - Minimal token usage
- `--uc --c7` - Compressed docs lookup
- Standard mode for complex operations

### Parallel Operations
```bash
/spawn --task "frontend testing"
/spawn --task "backend optimization"
/spawn --task "security audit"
```

## Template System Features

### @pattern Reference System
- **Command Templates**: Standardized flag & structure definitions
- **Validation System**: `validate-references.sh` ensures integrity  
- **Token Efficiency**: Significant reduction in command duplication
- **Maintenance**: Single source of truth for common elements

### Quality Assurance
- Evidence-based standards enforcement
- Research-first methodology for external libraries
- Automated reference validation
- Error handling & recovery patterns

---
**SuperClaude v4.0.0** - 18 commands • 25 shared resources • 9 personas • @pattern templates