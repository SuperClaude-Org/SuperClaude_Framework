# /spawn - Spawn focused agent for specialized tasks

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
Spawn specialized sub-agents to handle specific tasks in $ARGUMENTS with focused expertise and parallel execution capabilities.

## Syntax
`/spawn [flags] [task-description]`

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

**Agent Specialization:**
- `--frontend`: Spawn UI/UX and frontend development agent
- `--backend`: Spawn API and backend services agent
- `--devops`: Spawn infrastructure and deployment agent
- `--data`: Spawn data analysis and database agent
- `--security`: Spawn security and compliance agent
- `--qa`: Spawn quality assurance and testing agent

**Task Configuration:**
- `--task [description]`: Define clear, focused assignment with specific objectives
- `--context [info]`: Provide necessary background context and constraints
- `--scope [boundaries]`: Set clear task boundaries and limitations
- `--timeline [duration]`: Specify expected completion timeframe

**Coordination:**
- `--parallel`: Enable parallel execution with main workflow
- `--sequential`: Require sequential execution after current tasks
- `--integrate`: Automatic integration of results with main context
- `--review`: Require manual review before integration

**Quality Control:**
- `--validate`: Validate agent output before integration
- `--test`: Include testing requirements in agent task
- `--document`: Require documentation of agent work

## Examples
- `/spawn --frontend --task "implement user dashboard" --think` → Frontend agent with coordination analysis
- `/spawn --security --task "implement auth system" --validate --think-hard` → Security agent with validation
- `/spawn --devops --task "setup CI/CD pipeline" --document --ultrathink` → DevOps agent with documentation
- `/spawn --data --task "optimize database queries" --test --parallel` → Data agent with testing in parallel
- `/spawn --qa --task "comprehensive test suite" --integrate` → QA agent with auto-integration

## Agent Specializations

**Frontend Agent:**
- User interface and user experience implementation
- Component development with modern frameworks
- State management and data flow
- Performance optimization and bundle analysis
- Accessibility compliance and responsive design
- Cross-browser compatibility and testing

**Backend Agent:**
- RESTful and GraphQL API development
- Database design and operations
- Business logic implementation
- Third-party service integrations
- Performance tuning and optimization
- Security implementation and hardening

**DevOps Agent:**
- CI/CD pipeline setup and optimization
- Infrastructure as Code (IaC) development
- Deployment strategy design and implementation
- Monitoring and observability configuration
- Security hardening and compliance
- Container orchestration and scaling

**Data Agent:**
- Data analysis and statistical modeling
- Database optimization and query tuning
- ETL pipeline development and maintenance
- Data quality assurance and validation
- Reporting and visualization solutions
- Data governance and compliance

**Security Agent:**
- Security vulnerability assessment and remediation
- Authentication and authorization implementation
- Encryption and data protection strategies
- Compliance framework implementation
- Security monitoring and incident response
- Penetration testing and security audits

**QA Agent:**
- Test strategy and framework development
- Automated testing implementation
- Manual testing procedures and protocols
- Performance and load testing
- Quality metrics and reporting
- Bug tracking and resolution workflows

## Agent Task Definition

**Clear Scope Definition:**
- Specific, measurable deliverables
- Clear task boundaries and limitations
- Time constraints and deadlines
- Quality expectations and standards
- Success criteria and acceptance conditions

**Context Provision:**
- Relevant code sections and documentation
- Architecture decisions and constraints
- Previous implementation decisions
- Technical requirements and dependencies
- Integration points with existing systems

**Success Criteria:**
- Measurable outcomes and metrics
- Quality standards and benchmarks
- Integration requirements and compatibility
- Testing expectations and coverage
- Performance targets and constraints

**Coordination Requirements:**
- Avoid conflicts with ongoing work
- Plan integration and merge points
- Handle inter-task dependencies
- Manage communication and updates
- Establish review and approval processes

## Agent Workflow

**1. Agent Spawning:**
- Analyze task requirements and complexity
- Select appropriate agent specialization
- Define clear task scope and objectives
- Provide necessary context and constraints
- Establish success criteria and timeline

**2. Independent Execution:**
- Agent works autonomously on assigned task
- Focused context and specialized expertise
- Progress tracking and status updates
- Problem-solving within defined scope
- Quality assurance and self-validation

**3. Progress Monitoring:**
- Regular status updates and checkpoints
- Issue escalation and dependency resolution
- Scope adjustment and timeline management
- Quality review and feedback incorporation
- Communication with main workflow

**4. Result Integration:**
- Comprehensive result review and validation
- Integration planning and execution
- Knowledge transfer to main context
- Documentation and lessons learned
- Quality verification and testing

**5. Completion Handoff:**
- Final deliverable validation
- Integration verification and testing
- Documentation and knowledge transfer
- Cleanup and resource management
- Success metrics and outcome assessment

## Benefits of Agent Spawning

**Efficiency Gains:**
- Parallel task execution and processing
- Specialized expertise and focused attention
- Reduced cognitive load on main workflow
- Faster task completion and delivery
- Improved resource utilization

**Quality Improvements:**
- Domain-specific expertise application
- Focused quality assurance and testing
- Specialized best practices implementation
- Reduced context switching overhead
- Enhanced problem-solving capabilities

**Scalability Advantages:**
- Distributed workload management
- Independent task scaling
- Flexible resource allocation
- Modular development approach
- Improved development velocity

## Deliverables
- **Task Results**: Completed work from spawned agent with quality validation
- **Integration Plan**: Strategy for merging agent work with main context
- **Knowledge Transfer**: Documentation of agent decisions and implementation
- **Coordination Summary**: Agent workflow and communication log
- **Quality Report**: Validation and testing results from agent work

## Output Locations
- **Agent Logs**: `.claudedocs/reports/agent-spawn-{timestamp}.md`
- **Task Results**: `.claudedocs/summaries/agent-results-{timestamp}.md`
- **Integration Plans**: `.claudedocs/summaries/integration-plan-{timestamp}.md`

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

## Best Practices

**Agent Management:**
- Define clear, specific task objectives
- Provide comprehensive context and constraints
- Establish measurable success criteria
- Plan integration points and dependencies
- Monitor progress and provide feedback

**Quality Assurance:**
- Validate agent output before integration
- Test agent deliverables thoroughly
- Review code quality and standards compliance
- Verify documentation completeness
- Assess performance and security implications

**Coordination:**
- Avoid task overlap and conflicts
- Manage dependencies and prerequisites
- Maintain clear communication channels
- Handle scope changes and adjustments
- Ensure knowledge transfer and documentation

## Troubleshooting
- **Complex Tasks**: Use `--think-hard` for comprehensive planning
- **Integration Issues**: Apply `--review --validate` for quality control
- **Parallel Execution**: Use `--parallel --coordinate` for workflow management
- **Quality Concerns**: Combine `--qa --test --document` for thorough validation

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
