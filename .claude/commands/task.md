# /task - Manage complex features and requirements

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
Manage complex features and requirements across sessions with automatic breakdown, context preservation, and recovery capabilities.

## Syntax
`/task [operation] [parameters]`

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

## Command-Specific Operations

**Task Operations:**
- `create <title>`: Create new task with automatic breakdown
- `list`: Show tasks filtered by status or priority
- `start <id>`: Begin working on specific task
- `pause <id>`: Pause current work and save context
- `resume <id>`: Resume previously paused task
- `complete <id>`: Mark task as completed with verification
- `cancel <id>`: Cancel task and clean up resources
- `show <id>`: Display detailed task information
- `update <id>`: Modify task status, priority, or details

**Task Types:**
- `--type feature`: New feature development
- `--type bugfix`: Bug resolution and fixes
- `--type refactor`: Code refactoring and improvement
- `--type docs`: Documentation creation or updates
- `--type test`: Testing implementation or enhancement

**Priority Levels:**
- `--priority high`: Critical or urgent tasks
- `--priority medium`: Standard priority tasks (default)
- `--priority low`: Nice-to-have or future enhancements

**Status Filters:**
- `--status pending`: Tasks waiting to be started
- `--status in-progress`: Currently active tasks
- `--status completed`: Finished tasks
- `--status cancelled`: Cancelled or abandoned tasks

## Examples
- `/task create "User authentication system" --type feature --priority high`
- `/task list --status pending --priority high`
- `/task start 20250623-143052`
- `/task pause 20250623-143052`
- `/task resume 20250623-143052`
- `/task complete 20250623-143052`
- `/task show 20250623-143052`
- `/task update 20250623-143052 --priority low`

## Task Workflow

**Task Creation:**
1. **Requirement Analysis**: Analyze complexity and scope
2. **ID Generation**: Create unique task ID (YYYYMMDD-HHMMSS)
3. **Breakdown**: Decompose into phases and actionable steps
4. **File Creation**: Generate task file from appropriate template
5. **Git Integration**: Create dedicated branch for task
6. **Organization**: Move to pending folder for tracking

**Task Execution:**
1. **Activation**: Move task to in-progress folder
2. **Checkpoint**: Create git checkpoint for safety
3. **Sequential Execution**: Work through steps systematically
4. **Progress Tracking**: Update progress and context continuously
5. **Session Management**: Handle interruptions and breaks gracefully

**Task Completion:**
1. **Verification**: Ensure all steps completed successfully
2. **Testing**: Run comprehensive tests and validation
3. **Checkpoint**: Create completion checkpoint
4. **Organization**: Move to completed folder
5. **Integration**: Merge git branch and clean up

## Auto-Detection

**Complexity Triggers:**
- "build feature X" or "implement functionality Y"
- "add component Z" or "create system W"
- Requirements affecting more than 3 files
- Multi-step work requiring coordination
- Complex integration or architectural changes

**System Response:**
- Analyze request complexity automatically
- Suggest task creation for complex work
- Provide options: [Create task breakdown] [Proceed directly]
- Explain benefits of task management approach
- Respect user preference for simple tasks

## Session Recovery

**Startup Process:**
1. **Scan**: Check `.claudedocs/tasks/in-progress/` directory
2. **Identify**: Find active tasks and their current state
3. **Restore**: Load context from task files and git history
4. **Suggest**: Recommend next steps for resumption

**Context Preservation:**
- Key architectural decisions and rationale
- Current implementation state and progress
- Known blockers and proposed solutions
- File modification history and dependencies
- Integration points and testing requirements

## Task File Structure

**Directory Organization:**
```
.claudedocs/tasks/
├── pending/          # Tasks waiting to be started
├── in-progress/      # Currently active tasks
├── completed/        # Finished tasks
├── cancelled/        # Cancelled or abandoned tasks
└── templates/        # Task templates by type
```

**File Naming Convention:**
```
{type}-{id}-{slug}.md

Examples:
feature-20250623-143052-user-auth.md
bugfix-20250623-144022-login-error.md
refactor-20250623-142033-api-cleanup.md
```

**Task File Content:**
- Task metadata (ID, type, priority, status)
- Detailed description and requirements
- Phase breakdown with progress tracking
- Context and architectural decisions
- Blockers and resolution strategies
- Testing and validation requirements

## Integration Capabilities

**Git Integration:**
- Automatic branch creation and management
- Checkpoint creation for safety and rollback
- Merge strategy and conflict resolution
- Commit message generation and conventions

**TodoWrite Synchronization:**
- Sync with existing todo system
- Convert todos to tasks when appropriate
- Maintain consistency across systems
- Provide unified task management experience

**Persona Activation:**
- Task-specific persona selection
- Specialized expertise for different task types
- Context-aware skill application
- Collaborative persona workflows

**MCP Integration:**
- Context preservation across MCP tools
- State management for complex operations
- Tool coordination for task execution
- Resource optimization and sharing

**Command Chaining:**
- Chain with other SuperClaude commands
- Workflow automation and optimization
- Cross-command context sharing
- Integrated development experience

## Advanced Features

**Task Dependencies:**
- Define prerequisite relationships
- Automatic dependency resolution
- Blocked task identification
- Parallel execution planning

**Progress Tracking:**
- Phase-based progress measurement
- Milestone tracking and reporting
- Time estimation and actual tracking
- Velocity and performance metrics

**Collaboration Support:**
- Multi-contributor task support
- Handoff procedures and documentation
- Knowledge transfer mechanisms
- Team coordination features

## Deliverables
- **Task Files**: Comprehensive task documentation with progress tracking
- **Git Branches**: Dedicated branches with checkpoint history
- **Progress Reports**: Regular status updates and metrics
- **Context Documentation**: Preserved decision-making rationale
- **Integration Plans**: Merge and deployment strategies

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

**Task Creation:**
- Define clear, specific objectives
- Break down complex work into manageable phases
- Set realistic timelines and expectations
- Include comprehensive context and requirements
- Plan for testing and validation

**Execution Management:**
- Update progress regularly and consistently
- Document decisions and changes promptly
- Handle blockers and dependencies proactively
- Maintain clean git history and commits
- Communicate status changes effectively

**Quality Assurance:**
- Verify completion criteria before marking done
- Run comprehensive tests and validation
- Review code quality and standards compliance
- Update documentation and knowledge base
- Plan for maintenance and future enhancements

## Troubleshooting
- **Complex Tasks**: Use automatic breakdown with phase management
- **Session Interruptions**: Leverage auto-save and context preservation
- **Integration Issues**: Apply git checkpoints and rollback capabilities
- **Progress Tracking**: Use detailed phase and milestone tracking

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
