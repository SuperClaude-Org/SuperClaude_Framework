# Workflow Plan: SuperClaude Refactoring of v3.0-roadmap-gen

**Generated**: 2026-01-26
**Purpose**: Comprehensive workflow plan for translating IBOpenCode roadmap.md and tasklists to SuperClaude/Claude Code equivalents
**Input Documents**:
- `/config/workspace/SuperClaude/.roadmaps/v.1.4-roadmap-gen/roadmap.md`
- `/config/workspace/SuperClaude/.roadmaps/v.1.4-roadmap-gen/tasklists/M1-M6`
- Validation reports from 21 proposal validations (avg score: 69.6/100)

---

## Executive Summary

This workflow refactors the IBOpenCode `/rf:roadmap-gen` command specification into a SuperClaude `/sc:roadmap-gen` skill. Based on 21 validated proposals with an average score of 69.6/100, significant corrections are required in multiple areas. The refactoring spans 6 milestones affecting 31 deliverables across all IBOpenCode-specific components.

**Critical Corrections Required**:
1. `subagent_type` is NOT a Task tool API parameter (embed in prompt)
2. Templates directories don't exist (need to be created)
3. Compliance tier system is in ORCHESTRATOR.md, not RULES.md
4. TodoWrite only supports 3 states (no "blocked")
5. Wave-enabled commands count is 7, not 6
6. /sc:git subcommands (tag, diff, log) don't exist

---

## Phase 1: Global Search-Replace Mappings

### 1.1 Path Translations

| IBOpenCode Pattern | SuperClaude Equivalent | Notes |
|-------------------|------------------------|-------|
| `.opencode/command/rf:roadmap-gen.md` | `.claude/skills/sc-roadmap-gen/SKILL.md` | Skill, not command |
| `.opencode/agent/rf-roadmap-gen-orchestrator.md` | `plugins/superclaude/agents/roadmap-orchestrator.md` | Agent definition |
| `.opencode/agent/rf-roadmap-gen-template-scorer.md` | `plugins/superclaude/agents/template-scorer.md` | Optional agent |
| `.opencode/resources/templates/roadmaps/` | `plugins/superclaude/templates/roadmaps/` | **CREATE** directory |
| `.dev/plans/` | `.roadmaps/` | Existing convention |
| `TASKLIST_ROOT` | `.roadmaps/<version>/tasklists/` | Direct path |

### 1.2 Command/Syntax Translations

| IBOpenCode | SuperClaude | Notes |
|------------|-------------|-------|
| `/rf:roadmap-gen` | `/sc:roadmap-gen` | Skill invocation |
| `/rf:crossLLM v2 file` | `Task(quality-engineer)` + `Task(self-review)` | Sequential multi-agent |
| `@rf-roadmap-gen-orchestrator` | Embedded agent instructions in Task prompt | No `subagent_type` param |

### 1.3 Configuration Translations

| IBOpenCode | SuperClaude | Notes |
|------------|-------------|-------|
| `model: gpt-5.2` | `--think-hard` or `--ultrathink` | Thinking depth flags |
| `temperature: 0.1` | Sequential MCP + structured prompts | No direct equivalent |
| `tools: bash, read, write...` | `allowed-tools:` in SKILL.md frontmatter | YAML array format |

### 1.4 Persona Translations

| IBOpenCode | SuperClaude | Notes |
|------------|-------------|-------|
| `>40% domain = Primary` | `confidence >= 85%` per domain | Domain-specific thresholds |
| `>15% domain = Consulting` | Cross-persona collaboration | Dynamic, not threshold |
| `ARCHITECTURE fallback` | `--persona-architect` | Manual or auto-activation |

---

## Phase 2: Document-Specific Refactoring Tasks

### 2.1 roadmap.md Refactoring (31 changes)

#### Metadata Section (Lines 1-18)
| Line | Original | Replacement |
|------|----------|-------------|
| 1 | `v3.0-roadmap-gen` | `v1.4-sc-roadmap-gen` |
| 4 | `Source Specification: .../IBOpenCode/...` | `Source Specification: .../SuperClaude/.roadmaps/v.1.4-roadmap-gen/` |
| 6 | `Generator Version: v2.0` | `Generator Version: SuperClaude Roadmap Generator v1.0` |
| 12-16 | Backend/Architect/Scribe persona assignment | Update thresholds per PERSONAS.md (85%/70% confidence) |

#### Executive Summary (Lines 20-24)
| Change | Original | Replacement |
|--------|----------|-------------|
| Command name | `/rf:roadmap-gen` | `/sc:roadmap-gen` |
| Pipeline | `9-phase pipeline` | `5-wave orchestration system` |
| crossLLM | `crossLLM-powered content upgrades` | `Multi-agent verification via compliance tier system` |
| Protocol | `crossLLM Integration Protocol` | `Multi-Agent Validation Protocol` |

#### Milestones Section (Lines 26-186)
- **M1**: Replace `.opencode/command/` → `.claude/skills/`, agent paths → `plugins/superclaude/agents/`
- **M2**: Update template paths to `plugins/superclaude/templates/roadmaps/`
- **M4**: Complete rewrite - replace crossLLM with SuperClaude multi-agent validation

#### Dependency Graph (Lines 188-218)
- Update all file paths
- Change REQ-012 (crossLLM) to describe Task(quality-engineer) sequential flow

#### Risk Register (Lines 222-233)
| Risk ID | Original Risk | Updated Risk |
|---------|---------------|--------------|
| R1 | crossLLM API changes | MCP server availability (use circuit breakers) |
| R4 | Model availability | MCP server unavailable (fallback documented in MCP.md) |
| R5 | Template scoring | Use Sequential MCP for algorithm |

### 2.2 Tasklist Refactoring (per file)

#### Common Changes (All M1-M6 files)

1. **Metadata Section**:
   - `TASKLIST_ROOT: .dev/plans/...` → `TASKLIST_ROOT: .roadmaps/v1.4-sc-roadmap-gen/tasklists/`

2. **Path References**:
   - All `.opencode/` paths → SuperClaude equivalents
   - All agent references → `plugins/superclaude/agents/`

3. **Task Steps**:
   - Replace agent model specifications with thinking flags
   - Replace crossLLM invocations with Task(agent) calls

#### M1-foundation.md Specific Changes

| Task ID | Current | Updated |
|---------|---------|---------|
| T01.01 | Create `.opencode/command/rf:roadmap-gen.md` | Create `.claude/skills/sc-roadmap-gen/SKILL.md` |
| T01.03 | Create orchestrator with `model: gpt-5.2, temperature: 0.1` | Create orchestrator agent in `plugins/superclaude/agents/` with `--think-hard` depth |
| T01.05-T01.10 | References to 9-phase pipeline | Update to 5-wave structure |

#### M2-template-system.md Specific Changes

| Task ID | Current | Updated |
|---------|---------|---------|
| DOC-001-003 | `.opencode/resources/templates/roadmaps/` | `plugins/superclaude/templates/roadmaps/` |
| REQ-006 | Phase 2.5 template selection | Wave 2 resource resolution |
| REQ-007 | Template scorer agent | Embed scoring logic in skill or create `template-scorer.md` agent |

#### M4-crossllm-integration.md **CRITICAL REWRITE**

This milestone requires complete redesign:

| Original Concept | SuperClaude Equivalent |
|------------------|------------------------|
| `/rf:crossLLM v2 file <chain> <artifact>` | `Task(quality-engineer): "Assess artifact..."` → AWAIT → `Task(self-review): "Validate..."` |
| Parallel upgrade execution | **Sequential** verification (one agent at a time) |
| Score ≥ threshold → upgrade | compliance tier scoring → accept/revise/reject |
| `.dev/runs/rf-crossLLM/<runId>/` | `.roadmaps/<version>/validation/<timestamp>/` |
| `upgrade.md` | Iterative revision via `/sc:improve` |
| `scorecard.md` | `quality_report.md` + `validation_report.md` |
| Circuit breaker (50% fail) | Circuit breaker config in MCP.md |

**New M4 Structure**:
```yaml
REQ-012: Multi-agent verification (Sequential)
  - Step 1: Task(quality-engineer) with AWAIT
  - Step 2: Task(self-review) with AWAIT
  - Step 3: Score aggregation (native)

REQ-013: REMOVE - No parallel execution (crossLLM was sequential)

REQ-014: Draft preservation → Same (copy before validation)

REQ-015: Circuit breaker → Reference MCP.md circuit breaker config

REQ-016: Upgrade log → validation-report.md

REQ-017: Consistency validation → Wave 4 validation gates

REQ-018: Consistency report → quality_report.md
```

---

## Phase 3: New Files to Create

### 3.1 Skill Definition
**Path**: `.claude/skills/sc-roadmap-gen/SKILL.md`

```markdown
---
name: sc:roadmap-gen
description: Generate comprehensive project roadmaps with milestone tracking and multi-agent validation
category: planning
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, scribe, analyzer]
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap-gen - Roadmap Generator

## Purpose
Generate deterministic release roadmap packages from specification documents with multi-agent verification.

## Triggers
- Explicit: `/sc:roadmap-gen @requirements.md`
- Keywords: "generate roadmap", "create roadmap", "roadmap from spec"

## Usage
```bash
/sc:roadmap-gen @spec.md                           # From spec file
/sc:roadmap-gen @spec.md --output custom-dir/      # Custom output
/sc:roadmap-gen @spec.md --compliance strict       # Force strict verification
/sc:roadmap-gen @spec.md --template feature-release # Use specific template
```

## Behavioral Flow (5-Wave Orchestration)

### Wave 1: Detection & Analysis
- Parse input specification
- Score complexity and scope
- Activate personas: analyzer (primary), architect (consulting)

### Wave 2: Planning & Template Selection
- Template discovery: local → user → plugin → inline
- Persona selection based on domain distribution
- TodoWrite for task breakdown

### Wave 3: Generation
- Generate roadmap.md with dependency-ordered milestones
- Generate tasklist files per milestone
- Generate test-strategy.md

### Wave 4: Validation (Multi-Agent)
- Task(quality-engineer): completeness, clarity, consistency
- Task(self-review): 4-question validation protocol
- Score aggregation and decision

### Wave 5: Completion
- think_about_whether_you_are_done()
- Memory persistence via Serena
- Git operations if requested

## MCP Integration
- **Sequential**: Wave analysis and multi-step validation
- **Context7**: Template patterns and best practices
- **Serena**: Session persistence and version state

## Boundaries
**Will:**
- Generate structured roadmaps from requirements
- Apply multi-agent verification
- Track progress via TodoWrite

**Will Not:**
- Execute implementation tasks
- Override compliance tier verification
- Skip validation for STRICT tier artifacts
```

### 3.2 Agent Definition
**Path**: `plugins/superclaude/agents/roadmap-orchestrator.md`

```markdown
---
name: roadmap-orchestrator
description: Main coordinator for roadmap generation pipeline
category: orchestration
---

# Roadmap Orchestrator Agent

## Triggers
- Invoked by `/sc:roadmap-gen` skill
- Context detection: Roadmap generation requests

## Behavioral Mindset
- Systematic 5-wave execution
- Evidence-based progress tracking
- Quality-gate enforcement at each wave boundary

## Focus Areas
- Coordinating detection, planning, generation, validation, completion waves
- Managing persona activation based on domain analysis
- Ensuring traceability between requirements and deliverables

## Key Actions
1. Analyze input specification for actionable items
2. Assign unique IDs and categorize by domain/type
3. Select primary/consulting personas based on distribution
4. Apply appropriate template (or generate variant)
5. Generate roadmap with dependency-ordered milestones
6. Execute multi-agent validation via Task tool
7. Persist session state via Serena memory

## Outputs
- roadmap.md (master roadmap document)
- tasklists/*.md (per-milestone task files)
- validation/*.md (quality and validation reports)

## Boundaries
**Will:** Coordinate all roadmap generation phases
**Will Not:** Make business prioritization decisions, skip verification
```

### 3.3 Template Directory
**Path**: `plugins/superclaude/templates/roadmaps/`

Create these template files:
- `feature-release.md`
- `quality-release.md`
- `documentation-release.md`
- `variants/security-release.md`
- `variants/performance-release.md`
- `variants/migration-release.md`

---

## Phase 4: Execution Workflow

### Step 1: Create Infrastructure (Day 1)
```yaml
tasks:
  - Create plugins/superclaude/templates/roadmaps/ directory
  - Create .claude/skills/sc-roadmap-gen/ directory
  - Create SKILL.md with frontmatter and behavioral flow
  - Create roadmap-orchestrator.md agent
```

### Step 2: Refactor roadmap.md (Day 1-2)
```yaml
tasks:
  - Apply global search-replace mappings (Section 1)
  - Update Metadata section
  - Update Executive Summary
  - Update all 6 milestone sections
  - Update Dependency Graph
  - Update Risk Register
```

### Step 3: Refactor M1-M3 Tasklists (Day 2-3)
```yaml
tasks:
  - Update Metadata/paths in each file
  - Replace all .opencode/ references
  - Update agent references
  - Update model/temperature to thinking flags
```

### Step 4: Rewrite M4 Tasklist (Day 3-4) **CRITICAL**
```yaml
tasks:
  - Complete conceptual redesign per Section 2.2
  - Replace crossLLM with multi-agent Task flow
  - Update all REQ-012 through REQ-018
  - Remove parallel execution assumptions
  - Add AWAIT semantics between agent calls
```

### Step 5: Refactor M5-M6 Tasklists (Day 4)
```yaml
tasks:
  - Update enhancement flags to SuperClaude equivalents
  - Update documentation paths
  - Update Integration Protocol references
```

### Step 6: Validation (Day 5)
```yaml
tasks:
  - Verify all paths resolve correctly
  - Verify all agent references exist
  - Run consistency check on ID references
  - Verify TodoWrite states are valid (3 states only)
  - Test skill invocation pattern
```

---

## Phase 5: Validation Checklist

### Path Verification
- [ ] All `.opencode/` paths replaced
- [ ] All `.dev/` paths replaced
- [ ] All agent paths point to `plugins/superclaude/agents/`
- [ ] All template paths point to `plugins/superclaude/templates/`
- [ ] SKILL.md exists at `.claude/skills/sc-roadmap-gen/SKILL.md`

### Conceptual Verification
- [ ] No references to `subagent_type` as API parameter
- [ ] No references to crossLLM (replaced with multi-agent)
- [ ] No references to model names (gpt-5.2, etc.)
- [ ] No references to temperature values
- [ ] All "blocked" states replaced with workaround pattern
- [ ] All persona thresholds use SuperClaude values

### Consistency Verification
- [ ] All REQ/IMP/DOC IDs traceable in refactored docs
- [ ] All milestone dependencies preserved
- [ ] Risk register updated for SuperClaude context
- [ ] Success criteria appropriate for SuperClaude

---

## Phase 6: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Template directory doesn't exist | Create as part of Step 1 |
| Multi-agent validation slower than crossLLM | Document expected latency, provide --skip-validation flag |
| Thinking flags don't provide temperature control | Document limitation, use Sequential MCP for structure |
| STRICT tier blocks progress | Provide --compliance standard override with justification |

---

## Appendix: Quick Reference

### IBOpenCode → SuperClaude Mapping Summary

| Category | IBOpenCode | SuperClaude |
|----------|------------|-------------|
| Command | `/rf:roadmap-gen` | `/sc:roadmap-gen` |
| Command Location | `.opencode/command/` | `.claude/skills/*/SKILL.md` |
| Agent Location | `.opencode/agent/` | `plugins/superclaude/agents/` |
| Template Location | `.opencode/resources/templates/` | `plugins/superclaude/templates/` |
| Pipeline | 9-phase sequential | 5-wave orchestration |
| Validation | crossLLM cross-model | Multi-agent Task(quality-engineer) |
| Model Config | `model: gpt-5.2` | `--think-hard` flag |
| Temperature | `temperature: 0.1` | Sequential MCP + structured prompts |
| Run Artifacts | `.dev/runs/` | `.roadmaps/<version>/validation/` |
| Session State | N/A | Serena memory |

---

*Generated by SuperClaude Workflow Generator*
*Based on 21 validated proposals (avg score: 69.6/100)*
