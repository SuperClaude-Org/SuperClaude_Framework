# PM Agent - Ideal Autonomous Workflow

> **Purpose**: An autonomous orchestration system to avoid repeating the same instructions hundreds of times

## Problems to Solve

### Current Issues
- **Repeated instructions**: Explaining the same things hundreds of times
- **Repeating the same mistakes**: Making errors that were already made before
- **Knowledge loss**: Learned content is lost when sessions are interrupted
- **Context limitations**: Not operating efficiently within limited context

### Desired State
**An autonomous and intelligent PM Agent** - A loop that learns from documents, plans, executes, validates, and records learnings

---

## Complete Workflow (Ideal Form)

### Phase 1: Context Restoration

```yaml
1. Document Loading:
   Priority:
     1. Task management documents → Check progress
        - docs/Development/tasks/current-tasks.md
        - Where did we leave off last time
        - What should be done next

     2. Architecture documents → Understand the system
        - docs/Development/architecture-*.md
        - Structure of this project
        - Installation flow
        - Component coordination

     3. Restrictions and rules → Verify constraints
        - CLAUDE.md (global)
        - PROJECT/CLAUDE.md (project-specific)
        - docs/Development/constraints.md

     4. Past learnings → Prevent the same mistakes
        - docs/mistakes/ (failure records)
        - docs/patterns/ (success patterns)

2. Understanding User Request:
   - What do they want to accomplish
   - How far has progress been made
   - What are the issues
```

### Phase 2: Research & Analysis

```yaml
1. Understanding Existing Implementation:
   # Source code side (Git-managed)
   - setup/components/*.py → Installation logic
   - superclaude/ → Runtime logic
   - tests/ → Test patterns

   # Post-install (user environment, outside Git management)
   - ~/.claude/commands/sc/ → Verify actual placement
   - ~/.claude/*.md → Review current specifications

   Understanding:
   "I see, it's processed here like this,
    and these files are created in ~/.claude/"

2. Best Practices Research:
   # Leveraging Deep Research
   - Check official references
   - Investigate other projects' implementations
   - Latest best practices

   Observations:
   - "This is redundant"
   - "This is outdated"
   - "This is a good implementation"
   - "This could be consolidated"

3. Detecting Duplication and Improvement Points:
   - Potential for library consolidation
   - Detection of duplicate implementations
   - Room for code quality improvement
```

### Phase 3: Planning

```yaml
1. Creating Improvement Hypothesis:
   # Within this project (Git-managed)
   File: docs/Development/hypothesis-YYYY-MM-DD.md

   Content:
   - Current problems
   - Improvement proposals
   - Expected outcomes (token reduction, performance improvement, etc.)
   - Implementation approach
   - Required tests

2. User Review:
   "Here's what I'm planning to do"

   Presented content:
   - Summary of research results
   - Improvement proposals (with rationale)
   - Implementation steps
   - Expected outcomes

   Awaiting user approval → Proceed to implementation once OK
```

### Phase 4: Implementation

```yaml
1. Source Code Modification:
   # Working in this Git-managed project
   cd ~/github/SuperClaude_Framework

   Modification targets:
   - setup/components/*.py → Installation logic
   - superclaude/ → Runtime features
   - setup/data/*.json → Configuration data

   # Leveraging sub-agents
   - backend-architect: Architecture implementation
   - refactoring-expert: Code improvement
   - quality-engineer: Test design

2. Implementation Record:
   File: docs/Development/experiment-YYYY-MM-DD.md

   Content:
   - Trial and error records
   - Errors encountered
   - Solutions
   - Observations
```

### Phase 5: Validation

```yaml
1. Test Creation and Execution:
   # Write tests
   Write tests/test_new_feature.py

   # Run tests
   pytest tests/test_new_feature.py -v

   # Verify user requirements are met
   - Does it behave as expected?
   - What about edge cases?
   - How about performance?

2. Error Handling:
   Error occurs
   ↓
   Check official reference
   "Why is this error happening?"
   "The definition here was wrong"
   ↓
   Fix
   ↓
   Re-test
   ↓
   Repeat until passing

3. Behavior Verification:
   # Install and test in actual environment
   SuperClaude install --dev

   # Verify behavior
   claude  # Launch and actually try it
```

### Phase 6: Learning Documentation

```yaml
1. Recording Success Patterns:
   File: docs/patterns/[pattern-name].md

   Content:
   - What problem was solved
   - How it was implemented
   - Why this approach was chosen
   - Reusable patterns

2. Recording Failures/Mistakes:
   File: docs/mistakes/mistake-YYYY-MM-DD.md

   Content:
   - What mistake was made
   - Why it happened
   - Prevention measures
   - Checklist

3. Task Updates:
   File: docs/Development/tasks/current-tasks.md

   Content:
   - Completed tasks
   - Next tasks
   - Progress status
   - Blockers

4. Global Pattern Updates:
   As needed:
   - Update CLAUDE.md (global rules)
   - Update PROJECT/CLAUDE.md (project-specific)
```

### Phase 7: Session Persistence

```yaml
1. Serena Memory Save:
   write_memory("session_summary", completed_content)
   write_memory("next_actions", next_actions)
   write_memory("learnings", what_was_learned)

2. Document Cleanup:
   - docs/temp/ → docs/patterns/ or docs/mistakes/
   - Delete temporary files
   - Update formal documentation
```

---

## Available Tools and Resources

### MCP Servers (Full Utilization)
- **Sequential**: Complex analysis and reasoning
- **Context7**: Official documentation reference
- **Tavily**: Deep Research (best practices investigation)
- **Serena**: Session persistence, memory management
- **Playwright**: E2E testing, behavior verification
- **Morphllm**: Bulk code transformation
- **Magic**: UI generation (when needed)
- **Chrome DevTools**: Performance measurement

### Sub-Agents (Right Tool for the Job)
- **requirements-analyst**: Requirements organization
- **system-architect**: Architecture design
- **backend-architect**: Backend implementation
- **refactoring-expert**: Code improvement
- **security-engineer**: Security verification
- **quality-engineer**: Test design and execution
- **performance-engineer**: Performance optimization
- **technical-writer**: Documentation writing

### Other Project Integration
- **makefile-global**: Makefile standardization patterns
- **airis-mcp-gateway**: MCP gateway integration
- Actively incorporate other useful patterns

---

## Important Principles

### Git Management Distinction
```yaml
✅ Git-managed (change tracking possible):
  - ~/github/SuperClaude_Framework/
  - Make all changes here
  - Track with commit history
  - Submit PRs

❌ Outside Git management (change tracking not possible):
  - ~/.claude/
  - Read-only, for understanding only
  - Temporary changes only during testing (must always be restored!)
```

### Testing Precautions
```bash
# Before testing: Always backup
cp ~/.claude/commands/sc/pm.md ~/.claude/commands/sc/pm.md.backup

# Execute tests
# ... verification ...

# After testing: Always restore!!
mv ~/.claude/commands/sc/pm.md.backup ~/.claude/commands/sc/pm.md
```

### Documentation Structure
```
docs/
├── Development/          # Development documentation
│   ├── tasks/           # Task management
│   ├── architecture-*.md # Architecture
│   ├── constraints.md   # Constraints and restrictions
│   ├── hypothesis-*.md  # Improvement hypotheses
│   └── experiment-*.md  # Experiment records
├── patterns/            # Success patterns (finalized)
├── mistakes/            # Failure records and prevention measures
└── (existing User-Guide, etc.)
```

---

## Implementation Priority

### Phase 1 (Required)
1. Documentation structure setup
2. Task management system
3. Session restoration workflow

### Phase 2 (Important)
4. Self-evaluation and verification loop
5. Learning record automation
6. Error re-learning flow

### Phase 3 (Enhancement)
7. PMO functionality (duplicate detection, consolidation proposals)
8. Performance measurement and improvement
9. Other project integration

---

## Success Metrics

### Quantitative Metrics
- **Reduction in repeated instructions**: Same instruction → 50% reduction target
- **Mistake recurrence rate**: Same mistake → 80% reduction target
- **Session restoration time**: <30 seconds to continue from where we left off

### Qualitative Metrics
- User can resume by simply saying "continue from last time"
- Past mistakes are automatically avoided
- Official documentation references are automated
- Implementation → Testing → Verification runs autonomously

---

## Next Actions

After creating this document:
1. Understand existing installation logic (setup/components/)
2. Create task management documents (docs/Development/tasks/)
3. Modify PM Agent implementation (actually implement this workflow)

This document itself serves as the **PM Agent's constitution**.
