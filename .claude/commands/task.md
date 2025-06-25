**Purpose**: Complex feature management across sessions

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Manage complex features and requirements across sessions with automatic breakdown, context preservation, and recovery capabilities.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/task:create "Implement OAuth 2.0 authentication system"` - Create complex feature task
- `/task:status oauth-task-id` - Check task status  
- `/task:resume oauth-task-id` - Resume work after break
- `/task:update oauth-task-id "Found library conflict"` - Update with discoveries

## Operations

/task:create [description]:
- Create new task with automatic breakdown
- Generate subtasks & milestones
- Set up tracking structure
- Initialize context preservation

/task:update [task-id] [updates]:
- Update task progress
- Modify requirements
- Adjust timeline
- Add discoveries

/task:status [task-id]:
- Show current progress
- List completed subtasks
- Display blockers
- Estimate remaining work

/task:resume [task-id]:
- Load task context
- Continue from last point
- Restore working state
- Update progress

/task:complete [task-id]:
- Mark task as done
- Generate summary
- Archive artifacts
- Create documentation

## Task Structure

@include shared/task-management-patterns.yml#Task_Management_Hierarchy

Task Components:
- Title & description
- Acceptance criteria
- Technical requirements
- Subtask breakdown
- Progress tracking
- Context preservation

## Automatic Features

Smart Breakdown:
- Analyze complexity
- Create subtasks
- Identify dependencies
- Estimate effort
- Set milestones

Context Preservation:
- Save working state
- Track decisions
- Store code changes
- Maintain history
- Enable recovery

Progress Tracking:
- Update automatically
- Track blockers
- Monitor velocity
- Adjust estimates
- Report status

## Recovery System

@include shared/session-recovery.yml#Recovery_Patterns

Session Recovery:
- Auto-detect incomplete tasks
- Load previous context
- Resume from checkpoint
- Maintain continuity
- Preserve momentum

## Best Practices

Task Creation:
- Clear requirements
- Measurable outcomes
- Realistic scope
- Defined boundaries
- Success criteria

Task Management:
- Regular updates
- Track blockers early
- Document decisions
- Test incrementally
- Communicate progress

## Examples

```bash
# Create complex feature task
/task:create "Implement OAuth 2.0 authentication system"

# Check task status
/task:status oauth-task-id

# Resume work after break
/task:resume oauth-task-id

# Update with discoveries
/task:update oauth-task-id "Found library conflict, switching approach"

# Complete with summary
/task:complete oauth-task-id
```

## Integration

Works with:
- TodoWrite for subtasks
- Git for version control
- Test for validation
- Document for artifacts
- All development commands

## Deliverables

- Task breakdown document
- Progress tracking reports
- Technical decisions log
- Implementation artifacts
- Completion summary
- Lessons learned

@include shared/universal-constants.yml#Standard_Messages_Templates