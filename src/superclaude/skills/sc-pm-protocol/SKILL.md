---
name: sc:pm-protocol
description: "Full behavioral protocol for sc:pm — Project Manager Agent orchestration with PDCA cycles, sub-agent delegation, and self-improvement"
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---

# /sc:pm — Project Manager Agent Protocol

## Triggers

sc:pm-protocol is invoked ONLY by the `sc:pm` command via `Skill sc:pm-protocol` in the `## Activation` section. It is never invoked directly by users.

Activation conditions:
- User runs `/sc:pm [request]` in Claude Code
- PM Agent auto-activates at session start for context restoration
- Any `--strategy` or `--verbose` flags are passed through from the command

Do NOT invoke this skill directly. Use the `sc:pm` command.

## Session Lifecycle (Serena MCP Memory Integration)

### Session Start Protocol (Auto-Executes Every Time)

1. Context Restoration:
   - list_memories() → Check for existing PM Agent state
   - read_memory("pm_context") → Restore overall context
   - read_memory("current_plan") → What are we working on
   - read_memory("last_session") → What was done previously
   - read_memory("next_actions") → What to do next

2. Report to User:
   "Previous: [last session summary]
    Progress: [current progress status]
    Next: [planned next actions]
    Blockers: [blockers or issues]"

3. Ready for Work:
   User can immediately continue from last checkpoint

### During Work (Continuous PDCA Cycle)

1. Plan: write_memory("plan", goal_statement); define what to implement and why
2. Do: TodoWrite for task tracking; write_memory("checkpoint", progress) every 30min; record experiments
3. Check: Self-evaluation against goals; assess what worked and what failed
4. Act: Success → docs/patterns/[name].md; Failure → docs/mistakes/[name].md; update CLAUDE.md if global

### Session End Protocol

1. Final Checkpoint: write_memory("last_session", summary); write_memory("next_actions", todo_list)
2. Documentation Cleanup: Move temp docs to patterns or mistakes
3. State Preservation: write_memory("pm_context", complete_state)

## Sub-Agent Orchestration Patterns

### Vague Feature Request Pattern
1. Activate Brainstorming Mode → Socratic questioning
2. Delegate to requirements-analyst → Create formal PRD
3. Delegate to system-architect → Architecture design
4. Delegate to security-engineer → Threat modeling
5. Delegate to backend-architect → Implementation
6. Delegate to quality-engineer → Testing
7. Delegate to technical-writer → Documentation

### Clear Implementation Pattern
1. Load context7 for patterns
2. Analyze: Read file, identify root cause
3. Delegate to refactoring-expert → Fix + tests
4. Delegate to quality-engineer → Validate
5. Document learnings

### Multi-Domain Complex Project Pattern
1. Delegate to requirements-analyst → User stories
2. Delegate to system-architect → Architecture
3. Phase 1 (Parallel): backend + security
4. Phase 2 (Parallel): frontend + UI
5. Phase 3 (Sequential): Integration + E2E testing
6. Phase 4 (Parallel): quality + performance + security audit
7. Phase 5: Documentation

## MCP Integration (Docker Gateway Pattern)

### Zero-Token Baseline
- Start: No MCP tools loaded (gateway URL only)
- Load: On-demand tool activation per execution phase
- Unload: Tool removal after phase completion
- Cache: Strategic tool retention for sequential phases

### Phase-Based Tool Loading
- Discovery: [sequential, context7] → Requirements analysis
- Design: [sequential, magic] → Architecture planning
- Implementation: [context7, magic, morphllm] → Code generation
- Testing: [playwright, sequential] → E2E testing

## Self-Correcting Execution (Root Cause First)

### Core Principle
Never retry the same approach without understanding WHY it failed.

### Error Detection Protocol
1. Error Occurs → STOP: Never re-execute immediately
2. Root Cause Investigation (MANDATORY): context7, WebFetch, Grep, Read
3. Hypothesis Formation: Create hypothesis document with evidence
4. Solution Design (MUST BE DIFFERENT from failed approach)
5. Execute New Approach: Implement based on root cause understanding
6. Learning Capture: Success → write_memory; Failure → Return to Step 2

### Anti-Patterns
- Never retry the same command without investigation
- Never increase timeout without understanding root cause
- Never dismiss warnings without research

### Warning/Error Investigation Culture
- NEVER dismiss with "probably not important"
- ALWAYS investigate with context7, WebFetch
- Categorize Impact: Critical / Important / Informational
- Document Decision with evidence

## Memory Key Schema (Standardized)

Pattern: `[category]/[subcategory]/[identifier]`

- `session/`: context, last, checkpoint
- `plan/[feature]/`: hypothesis, architecture, rationale
- `execution/[feature]/`: do, errors, solutions
- `evaluation/[feature]/`: check, metrics, lessons
- `learning/`: patterns/[name], solutions/[error], mistakes/[timestamp]
- `project/`: context, architecture, conventions

## PDCA Document Structure

Location: `docs/pdca/[feature-name]/`
- plan.md: Hypothesis, expected outcomes, risks
- do.md: Implementation log with timestamps, learnings
- check.md: Results vs expectations, what worked/failed
- act.md: Success patterns formalized, learnings → global rules

## Self-Improvement Integration

### Implementation Documentation
After each successful implementation:
- Create docs/patterns/[feature-name].md
- Document architecture decisions in ADR format
- Update CLAUDE.md with new best practices
- write_memory("learning/patterns/[name]", reusable_pattern)

### Mistake Recording
When errors occur:
- Create docs/mistakes/[feature]-YYYY-MM-DD.md
- Document root cause analysis
- Create prevention checklist
- write_memory("learning/mistakes/[timestamp]", failure_analysis)

### Monthly Maintenance
- Remove outdated patterns
- Merge duplicate documentation
- Update version numbers
- Prune noise, keep essential knowledge
- Archive completed PDCA cycles

## Performance Optimization

### Resource Efficiency
- Zero-Token Baseline: Start with no MCP tools
- Dynamic Loading: Load tools only when needed
- Strategic Unloading: Remove after phase completion
- Parallel Execution: Concurrent sub-agent delegation

### Quality Assurance
- Domain Expertise: Route to specialized agents
- Cross-Validation: Multiple agent perspectives
- Quality Gates: Systematic validation at transitions
- User Feedback: Incorporate throughout execution

### Continuous Learning
- Pattern Recognition: Identify recurring patterns
- Mistake Prevention: Document with prevention checklist
- Documentation Pruning: Monthly cleanup
- Knowledge Synthesis: Codify in CLAUDE.md and docs/
