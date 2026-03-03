# SUPERCLAUDE ROADMAP GENERATOR PROMPT v1.0

## Purpose
Generate a deterministic, file-driven release roadmap package for the `/sc:roadmap-gen` skill from existing analysis and proposal documents.

## Interface (file-driven)

### Input Files (REQUIRED - Read ALL before proceeding)

| File | Purpose | Read Order |
|------|---------|------------|
| `analysis-opencode-specific.md` | Documents 10 OpenCode CLI features requiring translation | 1 |
| `analysis-ibopencode-framework-specific.md` | Documents 11 IBOpenCode Framework features requiring translation | 2 |
| `claude-code-proposals-opencode.md` | 10 validated translation proposals for OpenCode features | 3 |
| `claude-code-proposals-framework.md` | 11 validated translation proposals for Framework features | 4 |
| `workflow-superclaude-refactoring.md` | Comprehensive refactoring workflow with path mappings | 5 |

### Output Location
All artifacts MUST be written under:
- `.roadmaps/v1.4-sc-roadmap-gen/`

### Required Artifacts (exactly these 5)
1. `.roadmaps/v1.4-sc-roadmap-gen/roadmap.md` - Master roadmap document
2. `.roadmaps/v1.4-sc-roadmap-gen/tasklists/` - Per-milestone task files
3. `.roadmaps/v1.4-sc-roadmap-gen/test-strategy.md` - Validation approach
4. `.roadmaps/v1.4-sc-roadmap-gen/execution-prompt.md` - Implementation instructions
5. `.roadmaps/v1.4-sc-roadmap-gen/extraction.md` - Extracted requirements summary

---

## Safety and Integrity Rules (MANDATORY)

1. **No fabrication**: Never invent data, paths, or capabilities not documented in input files
2. **SuperClaude accuracy**: Use ONLY verified SuperClaude patterns from:
   - ORCHESTRATOR.md (compliance tiers, wave system)
   - PERSONAS.md (11 personas, confidence thresholds)
   - MCP.md (server capabilities, circuit breakers)
   - COMMANDS.md (7 wave-enabled commands)
3. **Critical corrections applied**: Ensure ALL these are correct:
   - `subagent_type` is NOT a Task API parameter (embed in prompt)
   - TodoWrite has 3 states: `pending`, `in_progress`, `completed` (NO "blocked")
   - Wave-enabled commands: 7 (not 6)
   - Compliance tiers in ORCHESTRATOR.md (not RULES.md)
4. **Path accuracy**: Use only these SuperClaude paths:
   - Skills: `.claude/skills/{skill-name}/SKILL.md`
   - Agents: `plugins/superclaude/agents/*.md`
   - Templates: `plugins/superclaude/templates/roadmaps/`
   - Commands: `.claude/commands/*.md` or `src/superclaude/commands/*.md`

---

## Preflight Validation (STOP-conditions)

BEFORE PROCEEDING, VERIFY:
- [ ] All 5 input files exist and are readable
- [ ] Input files contain SuperClaude-applicable content (not IBOpenCode originals)
- [ ] Output directory `.roadmaps/v1.4-sc-roadmap-gen/` can be created
- [ ] You have read and understood ALL input files completely

IF ANY CHECK FAILS → STOP and report the issue (do not proceed).

---

## WAVE 1: DETECTION & ANALYSIS

### 1.1 Parse All Input Documents
Read each input file and extract:
- **From analysis files**: Feature categories, translation requirements, dependencies
- **From proposal files**: Specific implementations, validated patterns, limitations
- **From workflow file**: Path mappings, correction requirements, milestone structure

### 1.2 Score Complexity and Scope
| Metric | Value | Source |
|--------|-------|--------|
| Total features to implement | Count from proposals | proposals files |
| Critical corrections | 6 | workflow file |
| Affected file paths | Count unique paths | all files |
| Multi-domain scope | Yes/No | analysis files |

### 1.3 Activate Personas
Based on domain distribution from proposals:
- **Primary**: Identify persona with >50% domain coverage
- **Consulting**: List personas with >15% domain coverage
- **Fallback**: Architect for system-wide decisions

**Expected Personas for this project**:
- Primary: Backend (pipeline phases)
- Consulting: Architect (system design), Scribe (documentation)

### Output: `extraction.md`
```markdown
# Extraction: v1.4-sc-roadmap-gen

## Metadata
- Source: Analysis and proposal files from v.1.4-roadmap-gen
- Generated: [timestamp]
- Generator: SuperClaude Roadmap Generator v1.0

## Extracted Items
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
[Extract from proposals - each feature becomes a REQ/IMP/DOC item]

## Summary
| Type | Count | Percentage |
|------|-------|------------|
[Aggregate statistics]
```

---

## WAVE 2: PLANNING & TEMPLATE SELECTION

### 2.1 Template Discovery
Search order:
1. Local: `.roadmaps/templates/` (if exists)
2. User: `~/.claude/templates/roadmaps/`
3. Plugin: `plugins/superclaude/templates/roadmaps/`
4. Inline: Generate variant if no match

**Best Template Match**: `feature-release.md` (new skill implementation)

### 2.2 Persona Selection Confirmation
Apply PERSONAS.md thresholds:
- Confidence >= 85%: Full persona activation
- Confidence >= 70%: Consulting role
- Below 70%: No activation

### 2.3 Task Breakdown via TodoWrite
Create hierarchical task structure:
```
Plan → Phase → Task → Todo
```

Use TodoWrite with ONLY these states:
- `pending` - Ready for execution
- `in_progress` - Currently active (ONE at a time)
- `completed` - Successfully finished

**CRITICAL**: No "blocked" state exists. For blocked items, use:
```
status: pending
content: "[BLOCKED: reason] Task description"
```

---

## WAVE 3: GENERATION

### 3.1 Generate roadmap.md

**Structure**:
```markdown
# Release Roadmap: v1.4-sc-roadmap-gen - SuperClaude Roadmap Generator Skill

## Metadata
- Source Specification: `.roadmaps/v.1.4-roadmap-gen/` analysis and proposal files
- Generated: [timestamp]
- Generator Version: SuperClaude Roadmap Generator v1.0
- Item Count: [X] features, [Y] improvements, [Z] docs

### Persona Assignment
**Primary**: [Persona] — [X]% of items are [DOMAIN] work
**Consulting**: [List personas with rationale]

---

## Executive Summary
[2-3 sentences describing the skill being built]

---

## Milestones Overview
| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|
[5-6 milestones covering: Foundation, Core Features, Validation, Enhancement, Documentation, Testing]

---

### Milestone 1: [Name]
**Objective**: [Clear goal]
**Dependencies**: [List or None]

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
[Deliverables with SuperClaude-correct paths]

[Repeat for each milestone]

---

## Dependency Graph
[ASCII or mermaid diagram showing REQ/IMP/DOC dependencies]

---

## Risk Register
| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
[SuperClaude-specific risks: MCP availability, circuit breakers, etc.]

---

## Success Criteria
- [ ] Skill invocable via /sc:roadmap-gen
- [ ] Multi-agent validation working
- [ ] TodoWrite integration correct
- [ ] All paths use SuperClaude conventions
```

### 3.2 Generate tasklist files (per milestone)

**Location**: `.roadmaps/v1.4-sc-roadmap-gen/tasklists/M{N}-{name}.md`

**Structure**:
```markdown
# Tasklist: M{N} - {Milestone Name}

## Metadata
- Milestone: M{N}
- Dependencies: [List]
- Estimated Complexity: [Low/Medium/High]

## Tasks

### T{M}.{N}: [Task Name]
**Type**: [FEATURE/IMPROVEMENT/DOC]
**Priority**: [P0-Critical/P1-High/P2-Medium/P3-Low]
**Files Affected**: [List of SuperClaude-correct paths]

#### Steps
1. [Step with specific action]
2. [Step with specific action]
...

#### Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]

#### Verification
```bash
# Commands to verify completion
```

---

[Repeat for each task in milestone]
```

### 3.3 Generate test-strategy.md

**Structure**:
```markdown
# Test Strategy: v1.4-sc-roadmap-gen

## Test Environment
- Location: `tests/sc-roadmap-gen/`
- Fixtures: `tests/fixtures/roadmap-gen/`
- Test Runner: pytest with superclaude plugin

## Test Categories
1. **Unit Tests**: Individual function validation
2. **Integration Tests**: Multi-component workflows
3. **Compliance Tests**: Tier classification accuracy
4. **End-to-End Tests**: Full skill invocation

## Test Matrix
| Deliverable ID | Unit | Integration | Compliance | E2E |
|----------------|------|-------------|------------|-----|
[Map each deliverable to test types]

## SuperClaude-Specific Validation
- [ ] TodoWrite state transitions correct (3 states only)
- [ ] Task tool prompt embedding works (no subagent_type)
- [ ] Wave orchestration triggers correctly
- [ ] Compliance tier classification accurate
- [ ] MCP circuit breakers function
```

---

## WAVE 4: VALIDATION (Multi-Agent)

### 4.1 Quality Engineer Assessment
Spawn Task agent with this prompt:
```
You are a quality-engineer validating the roadmap for /sc:roadmap-gen.

Check for:
1. **Completeness**: All 21 features from proposals covered?
2. **Correctness**: All 6 critical corrections applied?
3. **Consistency**: IDs traceable across documents?
4. **Compliance**: SuperClaude patterns followed?
5. **Coverage**: Test strategy covers all deliverables?

Return: score (0-100), issues list, recommendations
```

### 4.2 Self-Review Validation
4-question protocol:
1. "Did I read all input files before generating?"
2. "Are all paths SuperClaude-correct?"
3. "Did I avoid the 6 critical mistakes?"
4. "Is every claim traceable to input documents?"

### 4.3 Score Aggregation
- Quality Engineer score >= 80%: PASS
- Quality Engineer score 60-79%: REVISE
- Quality Engineer score < 60%: REJECT and restart

---

## WAVE 5: COMPLETION

### 5.1 Completion Check
Call `think_about_whether_you_are_done()` (Serena MCP):
- All 5 artifacts generated?
- Validation passed?
- No unresolved issues?

### 5.2 Memory Persistence
Via Serena MCP:
```
write_memory("roadmap-gen-session", {
  version: "v1.4",
  artifacts_generated: [...],
  validation_score: X,
  completion_status: "success"
})
```

### 5.3 Final Output Summary
```markdown
## Generation Complete

**Artifacts Created**:
- [ ] roadmap.md
- [ ] tasklists/M1-M6
- [ ] test-strategy.md
- [ ] execution-prompt.md
- [ ] extraction.md

**Validation Score**: [X]/100
**Completion Time**: [timestamp]
**Next Steps**: Execute tasklists in order M1 → M6
```

---

## MCP Server Integration

| Server | Purpose | Usage |
|--------|---------|-------|
| Sequential | Wave analysis, multi-step validation | Primary for complex reasoning |
| Serena | Session persistence, memory management | Checkpoints and state |
| Context7 | Template patterns, best practices | Documentation lookup |

## Compliance Tier

This generation task is **STANDARD** tier:
- Single coherent output (roadmap package)
- No security-critical code
- Moderate complexity (~15 files)

**Verification Method**: Direct validation via quality-engineer Task

---

## Quick Reference: Critical Corrections

| # | Mistake | Correction |
|---|---------|------------|
| 1 | `subagent_type` as API param | Embed agent type in Task prompt |
| 2 | Templates exist at paths | Must CREATE `plugins/superclaude/templates/roadmaps/` |
| 3 | Compliance in RULES.md | Compliance tiers are in ORCHESTRATOR.md |
| 4 | TodoWrite has "blocked" | Only 3 states: pending, in_progress, completed |
| 5 | 6 wave-enabled commands | Correct count is 7 |
| 6 | /sc:git has tag/diff/log | These subcommands don't exist |

---

*SuperClaude Roadmap Generator Prompt v1.0*
*Generated: 2026-01-26*
