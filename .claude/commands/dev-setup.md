# /dev-setup - Configure development environment and CI/CD

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
Configure comprehensive development environments and CI/CD pipelines based on project requirements in $ARGUMENTS.

## Syntax
`/dev-setup [flags] [target]`

## Universal Flags
--plan: "Show execution plan before running"
--uc: "UltraCompressed mode (~70% token reduction)"
--ultracompressed: "Alias for --uc"
--think: "Multi-file analysis w/ context (4K tokens)"
--think-hard: "Deep architectural analysis (10K tokens)"
--ultrathink: "Critical system redesign (32K tokens)"
--c7: "Enable Context7→library documentation lookup"
--seq: "Enable Sequential→complex analysis & thinking"
--magic: "Enable Magic→UI component generation"
--pup: "Enable Puppeteer→browser automation & testing"
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"

## Command-Specific Flags

**Setup Types:**
- `--install`: Install and configure development tools (Node.js, Git, Docker, databases)
- `--ci`: Configure CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
- `--monitor`: Setup observability tools (logging, monitoring, error tracking)
- `--docker`: Configure Docker development environment
- `--env`: Setup environment configuration and secrets management

**Development Tools:**
- `--ide`: Configure IDE settings and extensions
- `--git`: Setup Git workflows, hooks, and repository configuration
- `--deps`: Configure dependency management and security scanning
- `--testing`: Setup testing frameworks and coverage tools
- `--linting`: Configure code quality tools (ESLint, Prettier, etc.)

**Infrastructure:**
- `--local`: Local development environment setup
- `--cloud`: Cloud development environment configuration
- `--database`: Database setup and migration tools
- `--security`: Security tools and vulnerability scanning

## Examples
- `/dev-setup --install --docker --think` → Docker dev environment with analysis
- `/dev-setup --ci --security --think-hard` → Secure CI/CD pipeline design
- `/dev-setup --monitor --cloud --ultrathink` → Enterprise observability infrastructure
- `/dev-setup --git --testing --linting` → Complete development workflow
- `/dev-setup --env --database --local` → Local development with database

## Installation Setup (--install)

**Core Development Tools:**
- Node.js with version management (nvm/fnm)
- Git with global configuration
- Docker and Docker Compose
- Database tools (PostgreSQL, Redis)
- Package managers (npm, yarn, pnpm)

**IDE Configuration:**
- VS Code settings and extensions
- Consistent formatting and linting
- Debugging configurations
- Integrated terminal setup

**Development Scripts:**
- npm/yarn scripts for common tasks
- Pre-commit hooks for code quality
- Git hooks for automated checks
- Build and deployment scripts

## CI/CD Setup (--ci)

**Pipeline Stages:**
- **Build**: Compile, bundle, and optimize code
- **Test**: Unit, integration, and E2E testing
- **Security**: Vulnerability scanning and code analysis
- **Deploy**: Automated deployment to environments
- **Monitor**: Post-deployment verification

**Platform Configurations:**
- GitHub Actions workflows
- GitLab CI/CD pipelines
- Jenkins pipeline scripts
- Azure DevOps pipelines

**Environment Management:**
- Development, staging, production environments
- Secret management and environment variables
- Infrastructure as Code (Terraform, CloudFormation)
- Container orchestration (Kubernetes, Docker Swarm)

## Monitoring Setup (--monitor)

**Observability Stack:**
- Application performance monitoring (APM)
- Centralized logging (ELK stack, Splunk)
- Metrics collection (Prometheus, Grafana)
- Distributed tracing (Jaeger, Zipkin)
- Error tracking (Sentry, Rollbar)

**Alerting & Notifications:**
- Critical issue alerts
- Performance threshold monitoring
- Service health checks
- Deployment notifications

## Deliverables
- **Configuration Files**: Complete development and CI/CD configurations
- **Documentation**: Setup guides, workflows, and best practices
- **Scripts**: Automation scripts for environment setup
- **Templates**: Reusable configurations for new projects
- **Security Policies**: Development security guidelines and tools


```yaml
Mandatory_Research_Flows:
  External_Library_Research:
    Step_1: "Identify library/framework mentioned"
    Step_2: "Context7 lookup for official documentation"
    Step_3: "Verify API patterns and examples"
    Step_4: "Check version compatibility"
    Step_5: "Document findings in implementation"
    
  Pattern_Research:
    Step_1: "Search existing codebase for similar patterns"
    Step_2: "Magic component search if UI-related"
    Step_3: "WebSearch for official documentation"
    Step_4: "Validate approach with Sequential thinking"
    Step_5: "Document pattern choice rationale"
    
  API_Integration_Research:
    Step_1: "Official documentation lookup"
    Step_2: "Authentication requirements"
    Step_3: "Rate limiting and error handling"
    Step_4: "SDK availability and examples"
    Step_5: "Integration testing approach"
```


```yaml
Standard_Notifications:
  Operation_Start: "▶ Starting {operation}"
  Operation_Complete: "✅ {operation} completed successfully"
  File_Created: "📝 Created: {file_path}"
  File_Updated: "✏ Updated: {file_path}"
  Report_Generated: "📄 Report saved to: {path}"
  Error_Occurred: "❌ {operation} failed: {reason}"
  Warning_Issued: "⚠ {warning_message}"
  Info_Message: "ℹ {information}"

Output_Notifications:
  Success_Format: "✅ {operation} completed in {duration}"
  Error_Format: "❌ {operation} failed: {error_details}"
  Warning_Format: "⚠ {warning}: {details}"
  Info_Format: "ℹ {message}"
  Progress_Format: "🔄 {operation}: {current}/{total} ({percentage}%)"
```

## Best Practices & Security

**Security First:**
- Secure secret management (never commit secrets)
- Vulnerability scanning in CI/CD
- Code analysis and security linting
- Environment isolation and access controls
- Regular security updates and patches

**Development Standards:**
- Consistent code formatting and linting
- Automated testing at all levels
- Git workflow with protected branches
- Code review requirements
- Documentation standards

**Performance & Reliability:**
- Fast feedback loops in CI/CD
- Efficient caching strategies
- Parallel execution where possible
- Robust error handling and recovery
- Monitoring and observability from day one

## Environment-Specific Configurations

**Local Development:**
- Hot reload and fast refresh
- Local database and service mocking
- Debug-friendly configurations
- Offline-first development tools

**CI/CD Environments:**
- Optimized build times
- Comprehensive testing suites
- Security scanning integration
- Automated deployment gates

**Production Monitoring:**
- Real-time performance metrics
- Error tracking and alerting
- Log aggregation and analysis
- User experience monitoring

## Troubleshooting
- **Installation Issues**: Check system requirements and permissions
- **CI/CD Failures**: Review pipeline logs and dependency conflicts
- **Environment Conflicts**: Use containerization for consistency
- **Complex Setups**: Use `--think-hard` for architectural planning

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
