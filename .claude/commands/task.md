# /task: - Task Management & Session Recovery

@task-management.yml

## Purpose
Manage complex features & requirements across sessions with automatic breakdown, context preservation & recovery.

## Syntax
```bash
/task:create <title> [--type feature|bugfix|refactor|docs|test] [--priority high|medium|low]
/task:list [--status pending|in-progress|completed] [--priority high|medium|low]
/task:start <id>
/task:pause <id>
/task:complete <id>
/task:resume <id>
/task:cancel <id>
/task:show <id>
/task:update <id> --status <status> --priority <priority>
```

## Workflow
```yaml
Creation:
  1. Analyze requirement complexity
  2. Generate unique task ID (YYYYMMDD-HHMMSS)
  3. Break down into phases & steps
  4. Create task file from template
  5. Create git branch
  6. Move to pending folder

Execution:
  1. Move to in-progress folder
  2. Create git checkpoint
  3. Execute steps sequentially
  4. Update progress & context
  5. Handle session breaks gracefully

Completion:
  1. Verify all steps completed
  2. Run final tests
  3. Create completion checkpoint
  4. Move to completed folder
  5. Merge git branch
```

## Auto-Detection
```yaml
Triggers:
  - "build feature X"
  - "implement functionality Y"
  - "add component Z"
  - Requirements >3 files
  - Complex multi-step work

Response:
  "This looks like a multi-step task. Should I create a task breakdown?"
  Options: [Yes - create task] [No - proceed directly]
```

## Session Recovery
```yaml
Startup:
  1. Scan .tasks/in-progress/
  2. Identify active tasks
  3. Restore context from task files
  4. Suggest resumption steps

Context:
  - Key architectural decisions
  - Current implementation state
  - Known blockers & solutions
  - File modification history
```

## Examples
```bash
# Create new feature task
/task:create "User authentication system" --type feature --priority high

# List all pending tasks
/task:list --status pending

# Start working on a task
/task:start 20250623-143052

# Pause current work (auto-saves context)
/task:pause 20250623-143052

# Resume after session break
/task:resume 20250623-143052

# Mark task complete
/task:complete 20250623-143052
```

## Integration
- **Git**: Automatic branching & checkpoints
- **TodoWrite**: Sync with current todo system
- **Personas**: Task-specific persona activation
- **MCP**: Context preservation across tools
- **Commands**: Chain with other /user: commands

## File Structure
```
./claudedocs/tasks/
├── pending/feature-20250623-143052-user-auth.md
├── in-progress/bugfix-20250623-144022-login-error.md
├── completed/refactor-20250623-142033-api-cleanup.md
└── templates/feature-template.md
```