# PM Agent Task Management Workflow

**Purpose**: Lightweight task tracking and progress documentation integrated with PM Agent's learning system.

## Design Philosophy

```yaml
Storage: docs/memory/tasks/ (visible, searchable, Git-tracked)
Format: Markdown (human-readable, grep-friendly)
Lifecycle: Plan → Execute → Document → Learn
Integration: PM Agent coordinates all phases
```

## Task Management Flow

### 1. Planning Phase

**Trigger**: Multi-step tasks (>3 steps), complex scope

**PM Agent Actions**:
```markdown
1. Analyze user request
2. Break down into steps
3. Identify dependencies
4. Map parallelization opportunities
5. Create task plan in memory
```

**Output**: Mental model only (no file created yet)

### 2. Execution Phase

**During Implementation**:
```markdown
1. Execute steps systematically
2. Track progress mentally
3. Note blockers and decisions
4. Adapt plan as needed
```

**No intermediate files** - keep execution fast and lightweight.

### 3. Documentation Phase

**After Completion** (PM Agent auto-activates):
```markdown
1. Extract implementation patterns
2. Document key decisions
3. Record learnings
4. Save to docs/memory/tasks/[date]-[task-name].md
```

**Template**:
```markdown
# Task: [Name]
Date: YYYY-MM-DD
Status: Completed

## Request
[Original user request]

## Implementation Steps
1. Step 1 - [outcome]
2. Step 2 - [outcome]
3. Step 3 - [outcome]

## Key Decisions
- Decision 1: [rationale]
- Decision 2: [rationale]

## Patterns Discovered
- Pattern 1: [description]
- Pattern 2: [description]

## Learnings
- Learning 1
- Learning 2

## Files Modified
- file1.ts: [changes]
- file2.py: [changes]
```

### 4. Learning Phase

**PM Agent Knowledge Extraction**:
```markdown
1. Identify reusable patterns
2. Extract to docs/patterns/ if applicable
3. Update PM Agent knowledge base
4. Prune outdated patterns
```

## When to Use Task Management

**Use When**:
- Complex multi-step operations (>3 steps)
- Cross-file refactoring
- Learning-worthy implementations
- Need to track decisions

**Skip When**:
- Simple single-file edits
- Trivial bug fixes
- Routine operations
- Quick experiments

## Storage Structure

```
docs/
└── memory/
    └── tasks/
        ├── 2025-10-17-auth-implementation.md
        ├── 2025-10-17-api-redesign.md
        └── README.md (index of all tasks)
```

## Integration with PM Agent

```yaml
PM Agent Activation Points:
  1. Task Planning: Analyze and break down
  2. Mid-Task: Note blockers and pivots
  3. Post-Task: Extract patterns and document
  4. Monthly: Review and prune task history

PM Agent Responsibilities:
  - Task complexity assessment
  - Step breakdown and dependency mapping
  - Pattern extraction and knowledge capture
  - Documentation quality and pruning
```

## Comparison: Old vs New

```yaml
Old Design (Serena + TodoWrite):
  Storage: ~/.claude/todos/*.json (invisible)
  Format: JSON (machine-only)
  Lifecycle: Created → Abandoned → Garbage
  Result: Empty files, wasted tokens

New Design (PM Agent + Markdown):
  Storage: docs/memory/tasks/*.md (visible)
  Format: Markdown (human-readable)
  Lifecycle: Plan → Execute → Document → Learn
  Result: Knowledge accumulation, no garbage
```

## Example Workflow

**User**: "Implement JWT authentication"

**PM Agent Planning**:
```markdown
Mental breakdown:
1. Install dependencies (parallel: jwt lib + types)
2. Create middleware (sequential: after deps)
3. Add route protection (parallel: multiple routes)
4. Write tests (sequential: after implementation)

Estimated: 4 main steps, 2 parallelizable
```

**Execution**: PM Agent coordinates, no files created

**Documentation** (after completion):
```markdown
File: docs/memory/tasks/2025-10-17-jwt-auth.md

# Task: JWT Authentication Implementation
Date: 2025-10-17
Status: Completed

## Request
Implement JWT authentication for API routes

## Implementation Steps
1. Dependencies - Installed jsonwebtoken + @types/jsonwebtoken
2. Middleware - Created auth.middleware.ts with token validation
3. Route Protection - Applied to /api/user/* routes
4. Tests - Added 8 test cases (auth.test.ts)

## Key Decisions
- Used RS256 (not HS256) for better security
- 15min access token, 7day refresh token
- Stored keys in environment variables

## Patterns Discovered
- Middleware composition pattern for auth chains
- Error handling with custom AuthError class

## Files Modified
- src/middleware/auth.ts: New auth middleware
- src/routes/user.ts: Applied middleware
- tests/auth.test.ts: New test suite
```

## Benefits

```yaml
Visibility: All tasks visible in docs/memory/
Searchability: grep-friendly markdown
Git History: Task evolution tracked
Learning: Patterns extracted automatically
No Garbage: Only completed, valuable tasks saved
```

## Anti-Patterns

❌ **Don't**: Create task file before completion
❌ **Don't**: Document trivial operations
❌ **Don't**: Create TODO comments in code
❌ **Don't**: Use for session management (separate concern)

✅ **Do**: Let PM Agent decide when to document
✅ **Do**: Focus on learning and patterns
✅ **Do**: Keep task files concise
✅ **Do**: Review and prune old tasks monthly
