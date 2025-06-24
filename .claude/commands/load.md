# /load - Load and analyze project context

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
Load and analyze project context in $ARGUMENTS to build comprehensive understanding of codebase structure, architecture, and patterns.

## Syntax
`/load [flags] [path]`

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

**Analysis Depth:**
- `--depth shallow`: Quick overview of project structure and purpose
- `--depth normal`: Standard analysis of main files and architecture (default)
- `--depth deep`: Comprehensive analysis of entire codebase

**Analysis Focus:**
- `--architecture`: Focus on system design and component relationships
- `--dependencies`: Analyze dependency graph and package relationships
- `--security`: Include security considerations and potential issues
- `--performance`: Identify performance patterns and potential bottlenecks
- `--testing`: Analyze testing approach and coverage patterns

**Output Control:**
- `--summary`: Generate concise project overview
- `--detailed`: Include comprehensive analysis details
- `--recommendations`: Provide actionable next steps and improvements

## Examples
- `/load --depth shallow` → Quick project overview
- `/load --depth deep --architecture` → Comprehensive architectural analysis
- `/load --dependencies --security` → Focus on deps and security
- `/load --performance --testing --detailed` → Performance and testing analysis
- `/load --summary --recommendations` → Overview with actionable insights

## Loading Process

**1. Project Structure Scan:**
- Directory layout and organization
- File types and distribution
- Module boundaries and hierarchies
- Entry points and main components

**2. Configuration Analysis:**
- Package manifests (package.json, requirements.txt, go.mod)
- Build configurations (webpack, vite, rollup)
- Environment and deployment configs
- CI/CD pipeline definitions

**3. Code Architecture Review:**
- Design patterns and architectural style
- Component relationships and dependencies
- Data flow and state management
- API structure and endpoints

**4. Development Environment:**
- Git repository status and history
- Development workflow patterns
- Testing framework and approach
- Documentation quality and coverage

**5. Technology Stack Identification:**
- Frontend and backend technologies
- Database and data storage solutions
- Third-party integrations and services
- Development and deployment tools

## Analysis Depth Levels

**Shallow Depth:**
- Project purpose and business goals
- Primary technologies and frameworks
- High-level architecture overview
- Key dependencies and integrations
- Quick start and setup information
- Development team structure clues

**Normal Depth:**
- Detailed file and directory structure
- Main components and their responsibilities
- API endpoints, routes, and data models
- Database schema and relationships
- Testing strategy and coverage areas
- Development workflow and best practices

**Deep Depth:**
- Complete codebase analysis and mapping
- Detailed component interaction diagrams
- Comprehensive dependency relationships
- Performance characteristics and bottlenecks
- Security considerations and vulnerabilities
- Technical debt assessment
- Optimization opportunities and recommendations

## Essential Files Analysis

**Documentation:**
- README.md (project overview and setup)
- CONTRIBUTING.md (development guidelines)
- API documentation and specs
- Architecture decision records (ADRs)

**Configuration:**
- Package managers (package.json, yarn.lock, requirements.txt)
- Build tools (webpack.config.js, vite.config.ts)
- Environment configs (.env files, docker-compose.yml)
- CI/CD pipelines (.github/workflows, .gitlab-ci.yml)

**Source Code:**
- Entry points (main.js, app.py, index.html)
- Core modules and components
- Shared utilities and libraries
- Test files and test configurations

**Version Control:**
- Git history and commit patterns
- Branch strategy and naming conventions
- Recent changes and active development areas
- Contributor patterns and team structure

## Mental Model Construction

**System Understanding:**
- Component interaction patterns
- Data flow through the application
- External service integrations
- Deployment and infrastructure architecture
- User journey and experience flows

**Development Insights:**
- Code quality and consistency patterns
- Testing maturity and coverage
- Documentation completeness
- Development velocity indicators
- Technical debt and maintenance needs

## Deliverables
- **Project Overview**: Comprehensive understanding summary
- **Architecture Map**: System design and component relationships
- **Technology Inventory**: Complete stack and dependency analysis
- **Development Guide**: Quick reference for project navigation
- **Recommendations**: Next steps and improvement opportunities
- **Risk Assessment**: Potential issues and technical debt areas

## Output Locations
- **Analysis Reports**: `.claudedocs/summaries/project-analysis-{timestamp}.md`
- **Architecture Docs**: `.claudedocs/summaries/architecture-overview-{timestamp}.md`
- **Quick Reference**: `.claudedocs/summaries/project-guide-{timestamp}.md`

## Research Requirements
External_Library_Research:
  - Identify library/framework mentioned
  - Context7 lookup for official documentation
  - Verify API patterns and examples
  - Check version compatibility
  - Document findings in implementation
Pattern_Research:
  - Search existing codebase for similar patterns
  - Magic component search if UI-related
  - WebSearch for official documentation
  - Validate approach with Sequential thinking
  - Document pattern choice rationale
API_Integration_Research:
  - Official documentation lookup
  - Authentication requirements
  - Rate limiting and error handling
  - SDK availability and examples
  - Integration testing approach

## Report Notifications
📄 Analysis report saved to: {path}
📊 Metrics updated: {path}
📋 Summary saved to: {path}
💾 Checkpoint created: {path}
📚 Documentation created: {path}
📁 Created directory: {path}
✅ {operation} completed successfully
❌ {operation} failed: {reason}
⚠ {operation} completed w/ warnings

## Integration Patterns

**Workflow Integration:**
- Load project context before major development work
- Refresh understanding after significant changes
- Share context with team members and new contributors
- Use as foundation for architecture decisions

**Command Chaining:**
- `load` → `analyze --architecture` for design review
- `load` → `scan --security` for security assessment
- `load` → `improve --quality` for refactoring planning
- `load` → `document --architecture` for documentation

## Troubleshooting
- **Large Codebases**: Use `--depth shallow` for initial overview
- **Complex Architecture**: Combine `--architecture --detailed` for comprehensive analysis
- **Performance Issues**: Include `--performance` flag for optimization insights
- **Security Concerns**: Add `--security` flag for vulnerability assessment

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
