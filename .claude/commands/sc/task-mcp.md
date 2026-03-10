---
name: task-mcp
description: "MCP-enforced task execution with tiered workflow compliance and best practices enforcement"
category: special
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, qa, refactorer, python-expert, backend-architect]
deprecated: true
deprecated_by: "task-unified"
migration_guide: "Use /sc:task --compliance [tier] instead"
---

# /sc:task-mcp - MCP Best Practices Enforced Task Execution

> **DEPRECATION NOTICE**: This command is deprecated as of v2.0.0.
> Use `/sc:task --compliance [tier]` instead.
> See [Migration Guide](#migration-to-unified-command) below.

## Purpose

Execute tasks with enforced MCP best practices workflow. Automatically determines enforcement tier based on task characteristics and ensures compliance with the MCP-BEST-PRACTICES-CHEATSHEET.md.

**Philosophy**: Better false positives (over-enforce) than false negatives (miss important cases).

## Triggers

- Code modification tasks requiring MCP workflow enforcement
- Multi-file operations needing strict compliance
- Refactoring, test remediation, and complex implementations
- Exploratory "try this and see" coding sessions
- Any task where MCP best practices would improve outcomes

## Usage

```
/sc:task-mcp [task-description] [--tier strict|standard|light|auto] [--skip-mcp] [--force-strict]
```

### Flags

| Flag | Description |
|------|-------------|
| `--tier strict` | Force STRICT enforcement (full cheatsheet) |
| `--tier standard` | Force STANDARD enforcement (core rules) |
| `--tier light` | Force LIGHT enforcement (awareness only) |
| `--tier auto` | Auto-detect tier based on task analysis (default) |
| `--skip-mcp` | **Escape hatch**: Skip MCP workflow entirely |
| `--force-strict` | Override auto-detection, use STRICT regardless |

---

## Tiered Enforcement Model

### TIER 1: STRICT (Full Cheatsheet Compliance)

**Auto-Triggers:**
- Multi-file edits (>2 files)
- Sub-agent delegation tasks
- Test remediation/fixing workflows
- Refactoring operations
- Bug fixes affecting multiple components
- Exploratory "try this and see" coding
- Any production code changes

**Mandatory Steps:**

```markdown
## PRE-WORK CHECKLIST (MUST COMPLETE)
[ ] Project activated? (mcp__serena__activate_project)
[ ] Git working directory clean? (git status)
[ ] Context loaded for task area? (codebase-retrieval)
[ ] Relevant memories read? (list_memories → read_memory)

## TASK EXECUTION TEMPLATE
### CONTEXT LOADING
1. [ ] Primary file(s) to edit: ___
2. [ ] Related files to understand: ___
3. [ ] Test files that validate: ___

### IMPLEMENTATION
1. [ ] View current code state (codebase-retrieval/view)
2. [ ] Make change using appropriate tool
3. [ ] List exact changes made: ___

### DOWNSTREAM IMPACT ANALYSIS
1. [ ] Files that import changed code: ___
2. [ ] Tests that exercise changed code: ___
3. [ ] Update all affected files: [list]

### VERIFICATION (MANDATORY)
Spawn: sub-agent-quality-engineer
1. [ ] Run affected tests: pytest [path] -v
2. [ ] Verify no regressions
3. [ ] Check for error patterns in output

### ADVERSARIAL REVIEW
1. [ ] Could this break existing functionality? ___
2. [ ] Were ALL instances updated? ___
3. [ ] Are there edge cases? ___

### COMPLETION CRITERIA
- [ ] All implementation steps done
- [ ] All downstream impacts addressed
- [ ] Verification agent reports PASS
- [ ] Adversarial questions answered satisfactorily
```

**Post-Task "Did I?" Checklist:**
```markdown
[ ] Did I load context before editing?
[ ] Did I find and update downstream impacts?
[ ] Did I spawn a verification agent?
[ ] Did I ask adversarial questions?
[ ] Did I update memory with patterns discovered?
[ ] Did I verify completion criteria?
```

---

### TIER 2: STANDARD (Core Rules Enforcement)

**Auto-Triggers:**
- Single-file code changes
- Adding new files
- Configuration updates
- Code-adjacent documentation

**Required Steps:**

```markdown
## CORE RULES CHECKLIST
[ ] Context loaded before editing (Rule 1: Always Retrieve Before Edit)
[ ] Downstream impacts checked (Rule 2: Find Downstream Impacts)
[ ] Changes verified working (Rule 6: Always Verify - can be manual)

## QUICK VALIDATION
- [ ] Code compiles/runs
- [ ] Basic functionality tested
- [ ] No obvious regressions
```

**Verification**: Manual verification acceptable; sub-agent optional but recommended for uncertainty.

---

### TIER 3: LIGHT (Awareness Only)

**Auto-Triggers:**
- Minor fixes (typos, formatting)
- Comment updates
- Single-line changes
- Non-functional changes

**Guidance:**
- Be AWARE of MCP principles
- Apply judgment on verification needs
- Skip formal process unless uncertain
- Document if change has unexpected scope

---

### TIER 4: EXEMPT (No Enforcement)

**Auto-Triggers:**
- Questions/explanations ("what does X do?")
- Code exploration (read-only)
- Brainstorming/planning discussions
- Git operations (status, diff, log)
- Documentation-only changes (non-code .md files)
- Reflection/analysis tasks

**Behavior:** No MCP workflow enforcement. Proceed normally.

---

## Auto-Detection Algorithm

```yaml
tier_detection:
  strict_triggers:
    - file_count > 2
    - keywords: [refactor, remediate, fix tests, multi-file, exploratory, "try this"]
    - sub_agent_needed: true
    - complexity_score > 0.7

  standard_triggers:
    - file_count: 1-2
    - keywords: [add, update, modify, change, implement]
    - single_component: true

  light_triggers:
    - keywords: [typo, format, comment, minor, quick]
    - estimated_lines < 10
    - non_functional: true

  exempt_triggers:
    - keywords: [what, how, explain, understand, explore, brainstorm]
    - read_only: true
    - documentation_only: true
    - git_operation: true

  fallback: standard  # When uncertain, default to STANDARD (false positive preference)
```

---

## Behavioral Flow

1. **Analyze Task**: Parse task description, detect keywords, estimate scope
2. **Determine Tier**: Apply auto-detection algorithm (or use explicit --tier flag)
3. **Display Tier**: Announce determined tier and rationale
4. **Enforce Workflow**: Execute appropriate checklist based on tier
5. **Validate Completion**: Ensure all tier-required steps completed
6. **Report**: Summarize what was enforced and outcomes

---

## MCP Integration

- **Sequential MCP**: Complex task analysis and systematic execution planning
- **Context7 MCP**: Framework patterns and implementation best practices
- **Serena MCP**: Memory persistence, project context, cheatsheet reference

**Cheatsheet Reference**: `.serena/MCP-BEST-PRACTICES-CHEATSHEET.md` (v2.0)

---

## Tool Coordination

- **TodoWrite**: Track checklist completion and task progress
- **Task**: Delegate to specialized sub-agents (quality-engineer, python-expert, etc.)
- **codebase-retrieval**: Load context before any edit
- **Read/Edit/Write**: Execute code changes
- **Bash**: Run tests, validation commands

---

## Sub-Agent Delegation Matrix (STRICT Tier)

| Task Type | Sub-Agent | Verification Agent |
|-----------|-----------|-------------------|
| Python code fixes | python-expert | quality-engineer |
| Architecture decisions | backend-architect | quality-engineer |
| Test remediation | python-expert | quality-engineer |
| Refactoring | refactoring-expert | quality-engineer |
| Security concerns | security-engineer | quality-engineer |
| Performance issues | performance-engineer | quality-engineer |

---

## Examples

### STRICT Tier Example
```
/sc:task-mcp "Fix all async test failures in backend/tests/"
# Auto-detects: STRICT (multi-file, test remediation)
# Enforces: Full cheatsheet, verification agent, "Did I?" checklist
```

### STANDARD Tier Example
```
/sc:task-mcp "Add input validation to user registration endpoint"
# Auto-detects: STANDARD (single component, implementation)
# Enforces: Core rules, basic validation
```

### LIGHT Tier Example
```
/sc:task-mcp "Fix typo in error message" --tier light
# Explicit LIGHT tier
# Enforces: Awareness only, proceed with judgment
```

### Escape Hatch Example
```
/sc:task-mcp "Quick experimental change" --skip-mcp
# Skips all MCP enforcement
# Use when you're certain workflow not needed
```

### Force Strict Example
```
/sc:task-mcp "Update logging format" --force-strict
# Forces STRICT even though might auto-detect as STANDARD
# Use when task seems simple but has broad impact
```

---

## Boundaries

**Will:**
- Enforce appropriate MCP best practices based on task tier
- Ensure verification and validation for code-modifying tasks
- Spawn sub-agents for complex operations (STRICT tier)
- Track and report on workflow compliance

**Will Not:**
- Apply heavy process to simple questions or read-only operations
- Skip verification for multi-file or high-impact changes
- Allow false negatives on important tasks (prefers over-enforcement)
- Compromise quality standards for convenience

---

## Escape Hatch Guidelines

Use `--skip-mcp` when:
- You're absolutely certain the task doesn't need workflow
- You're doing rapid prototyping in a non-production branch
- The task is truly trivial and well-understood
- You've already completed the workflow mentally

**Warning**: Overuse of `--skip-mcp` defeats the purpose. If you're frequently skipping, reconsider whether tasks are being categorized correctly.

---

## Success Metrics

Track these to measure effectiveness:

| Metric | Target |
|--------|--------|
| Context loaded before edit | 100% (STRICT/STANDARD) |
| Downstream impacts found | 100% (STRICT), 80% (STANDARD) |
| Verification agents spawned | 100% (STRICT) |
| Test pass rate after changes | 100% |
| Regressions introduced | 0 |

---

## Version

v1.0 - Initial implementation with tiered enforcement model
v1.1 - **DEPRECATED** - Merged into unified /sc:task command

---

## Migration to Unified Command

This command has been merged into the unified `/sc:task` command which provides:
- All MCP compliance enforcement capabilities
- Strategy-based orchestration (systematic, agile, enterprise)
- Enhanced auto-detection algorithm
- Better persona and MCP server coordination

### Migration Examples

```bash
# Old command
/sc:task-mcp "fix tests" --tier strict

# New equivalent
/sc:task "fix tests" --compliance strict
```

```bash
# Old command
/sc:task-mcp "add validation" --tier standard

# New equivalent
/sc:task "add validation" --compliance standard
```

```bash
# Old command
/sc:task-mcp "quick change" --skip-mcp

# New equivalent
/sc:task "quick change" --skip-compliance
```

### Full Documentation

See `/sc:task-unified` for complete documentation of the unified command.
