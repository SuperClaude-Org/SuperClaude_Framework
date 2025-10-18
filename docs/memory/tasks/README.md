# Task Memory Index

This directory contains documentation of completed tasks, tracked by PM Agent.

## Purpose

- **Knowledge Capture**: Preserve implementation patterns and decisions
- **Learning Archive**: Accumulate project-specific learnings
- **Searchable History**: Grep-friendly task records

## Structure

```
tasks/
├── README.md (this file)
├── 2025-10-17-auth-implementation.md
├── 2025-10-17-api-redesign.md
└── [date]-[task-name].md
```

## Naming Convention

```
[YYYY-MM-DD]-[kebab-case-description].md
```

Examples:
- `2025-10-17-jwt-auth.md`
- `2025-10-18-database-migration.md`
- `2025-10-20-performance-optimization.md`

## Task File Template

See `superclaude/agents/pm-agent/workflows/task-management.md` for the standard template.

## Maintenance

**PM Agent Monthly Review**:
1. Prune outdated tasks (>6 months old)
2. Extract patterns to `docs/patterns/`
3. Update this index
4. Archive old tasks to `tasks/archive/` if needed

## Search Examples

```bash
# Find all authentication-related tasks
grep -r "auth" docs/memory/tasks/

# Find tasks with specific patterns
grep -r "middleware composition" docs/memory/tasks/

# List recent tasks
ls -lt docs/memory/tasks/ | head -10
```
