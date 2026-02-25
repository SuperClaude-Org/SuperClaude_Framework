# Release Roadmap: /sc:roadmap - SuperClaude Roadmap Generator Skill

## Metadata
- **Source Specification**: `.roadmaps/v.1.4-roadmap-gen/SC-ROADMAP-FEATURE-SPEC.md`
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Specification Version**: 1.1.0
- **Item Count**: 18 functional requirements, 8 NFRs, 4 improvements, 4 documentation items

### Persona Assignment
**Primary**: Backend (45%) — Orchestration pipeline, artifact generation, MCP integration
**Consulting**: Architect (25%), Scribe (20%)
**Fallback**: Architect for system-wide coordination

---

## Executive Summary

The `/sc:roadmap` command is a SuperClaude skill that transforms specification documents into comprehensive, milestone-based release roadmaps with integrated multi-agent validation. This roadmap covers the complete implementation from skill foundation through testing, organized into 6 milestones following the specification's 5-wave orchestration architecture.

**Key Deliverables**:
- Complete `/sc:roadmap` skill implementation
- 5-wave orchestration pipeline (Detection → Planning → Generation → Validation → Completion)
- Multi-agent validation system with quality-engineer Task integration
- Template infrastructure with inline generation fallback
- Comprehensive test coverage and documentation

---

## Milestones Overview

| Milestone | Name | Deliverables | Dependencies | Risk Level | Complexity |
|-----------|------|--------------|--------------|------------|------------|
| M1 | Foundation & Skill Setup | 4 | None | Low | Low |
| M2 | Wave 1 Implementation | 5 | M1 | Medium | High |
| M3 | Wave 2 Implementation | 4 | M2 | Low | Medium |
| M4 | Wave 3 - Artifact Generation | 6 | M3 | Medium | High |
| M5 | Wave 4-5 - Validation & Completion | 5 | M4 | Medium | Medium-High |
| M6 | Testing & Documentation | 4 | M5 | Low | Low-Medium |

---

## Milestone 1: Foundation & Skill Setup
**Objective**: Establish skill infrastructure, create SKILL.md, and set up template directory
**Dependencies**: None
**Risk Level**: Low
**Estimated Complexity**: Low

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D1.1 | DOC | Create SKILL.md definition file | Skill invocable via `/sc:roadmap` | `.claude/skills/sc-roadmap/SKILL.md` |
| D1.2 | FEATURE | Create skill directory structure | Directory exists with proper structure | `.claude/skills/sc-roadmap/` |
| D1.3 | DOC | Create template directory | Directory exists for template storage | `plugins/superclaude/templates/roadmaps/` |
| D1.4 | DOC | Create base template files | 6 template types available | `plugins/superclaude/templates/roadmaps/*.md` |

### Dependencies
```
D1.1 ← D1.2 (directory must exist before SKILL.md)
D1.3 ← D1.4 (directory must exist before templates)
D1.2 and D1.3 can execute in parallel
```

---

## Milestone 2: Wave 1 Implementation
**Objective**: Implement Detection & Analysis wave with specification parsing, complexity scoring, and persona activation
**Dependencies**: M1
**Risk Level**: Medium
**Estimated Complexity**: High

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D2.1 | FEATURE | Specification file validation | File existence, readability, content checks | `.claude/skills/sc-roadmap/SKILL.md` |
| D2.2 | FEATURE | Requirements extraction engine | Parse FR, NFR, scope, dependencies | `.claude/skills/sc-roadmap/SKILL.md` |
| D2.3 | FEATURE | Domain analysis classifier | Classify into frontend, backend, security, etc. | `.claude/skills/sc-roadmap/SKILL.md` |
| D2.4 | FEATURE | Complexity scoring system | 5-factor weighted scoring (0.0-1.0) | `.claude/skills/sc-roadmap/SKILL.md` |
| D2.5 | FEATURE | Persona auto-activation | Select primary (≥40%), consulting (≥15%) | `.claude/skills/sc-roadmap/SKILL.md` |

### Critical Implementation Notes
- Complexity scoring formula: `req_count(0.25) + dep_depth(0.25) + domain_spread(0.20) + risk_sev(0.15) + scope_size(0.15)`
- Persona confidence thresholds: Primary ≥85%, Consulting ≥70%
- Domain keywords per PERSONAS.md definitions

---

## Milestone 3: Wave 2 Implementation
**Objective**: Implement Planning & Template Selection wave with template discovery and task breakdown
**Dependencies**: M2
**Risk Level**: Low
**Estimated Complexity**: Medium

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D3.1 | FEATURE | Template discovery hierarchy | Search local → user → plugin → inline | `.claude/skills/sc-roadmap/SKILL.md` |
| D3.2 | FEATURE | Template scoring algorithm | Score ≥80% for direct selection | `.claude/skills/sc-roadmap/SKILL.md` |
| D3.3 | FEATURE | Inline template generation | Generate variant when no match | `.claude/skills/sc-roadmap/SKILL.md` |
| D3.4 | FEATURE | TodoWrite task initialization | Use 3 states only: pending, in_progress, completed | `.claude/skills/sc-roadmap/SKILL.md` |

### Critical Implementation Notes
- **NO "blocked" state in TodoWrite** - Use `[BLOCKED: reason]` prefix in content
- Milestone count formula from Section 3.3.1:
  ```
  base_count + floor((requirement_count - 5) / 5) + (1 if domain_spread > 2 else 0)
  ```
- Clamp milestones to complexity-appropriate range

---

## Milestone 4: Wave 3 - Artifact Generation
**Objective**: Implement artifact generation for all 5 required outputs
**Dependencies**: M3
**Risk Level**: Medium
**Estimated Complexity**: High

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D4.1 | FEATURE | Generate roadmap.md | Master document with milestones, deps, risks | Output: `roadmap.md` |
| D4.2 | FEATURE | Generate extraction.md | Requirements summary with domain analysis | Output: `extraction.md` |
| D4.3 | FEATURE | Generate tasklist files | Per-milestone task breakdowns | Output: `tasklists/M{N}-*.md` |
| D4.4 | FEATURE | Generate test-strategy.md | Testing approach with coverage matrix | Output: `test-strategy.md` |
| D4.5 | FEATURE | Generate execution-prompt.md | Implementation instructions | Output: `execution-prompt.md` |
| D4.6 | IMPROVEMENT | Parallelization within Wave 3 | test-strategy and execution-prompt concurrent | Orchestration logic |

### Parallelization Strategy (per Section 3.7)
```
Sequential: roadmap.md → tasklists/
Concurrent eligible: test-strategy.md || execution-prompt.md (both depend only on tasklists)
```

### Output Directory Structure
```
.roadmaps/<spec-name>/
├── roadmap.md
├── extraction.md
├── test-strategy.md
├── execution-prompt.md
└── tasklists/
    ├── M1-foundation.md
    ├── M2-wave1.md
    └── ...
```

---

## Milestone 5: Wave 4-5 - Validation & Completion
**Objective**: Implement multi-agent validation and session completion
**Dependencies**: M4
**Risk Level**: Medium
**Estimated Complexity**: Medium-High

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D5.1 | FEATURE | Quality-engineer Task validation | Embed agent type in prompt (NOT subagent_type param) | `.claude/skills/sc-roadmap/SKILL.md` |
| D5.2 | FEATURE | Self-review validation protocol | 4-question validation with evidence | `.claude/skills/sc-roadmap/SKILL.md` |
| D5.3 | FEATURE | Score aggregation system | PASS ≥85%, REVISE 70-84%, REJECT <70% | `.claude/skills/sc-roadmap/SKILL.md` |
| D5.4 | FEATURE | Completion check | think_about_whether_you_are_done() | `.claude/skills/sc-roadmap/SKILL.md` |
| D5.5 | FEATURE | Memory persistence | write_memory via Serena MCP | `.claude/skills/sc-roadmap/SKILL.md` |

### Critical Implementation Notes
- **Task tool does NOT have `subagent_type` parameter**
- Correct pattern: Embed agent specialization in prompt text
  ```
  Task:
    description: "Quality validation"
    prompt: |
      You are a quality-engineer agent...
  ```

### Score Weighting
- Quality Engineer: 60%
- Self Review: 40%

---

## Milestone 6: Testing & Documentation
**Objective**: Comprehensive testing, documentation updates, and user guide
**Dependencies**: M5
**Risk Level**: Low
**Estimated Complexity**: Low-Medium

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D6.1 | TEST | Unit tests for each wave | >80% coverage per wave | `tests/sc-roadmap/` |
| D6.2 | TEST | Integration tests | Full pipeline execution | `tests/sc-roadmap/integration/` |
| D6.3 | TEST | Compliance tier tests | Correct auto-classification | `tests/sc-roadmap/compliance/` |
| D6.4 | DOC | Update COMMANDS.md | Add /sc:roadmap entry | `COMMANDS.md` |

### Test Categories
1. **Unit Tests**: Individual function validation (parsing, scoring, generation)
2. **Integration Tests**: Multi-wave workflows
3. **Compliance Tests**: Tier classification accuracy
4. **E2E Tests**: Full skill invocation with sample specs

---

## Dependency Graph

```
M1 ─────────────────────────────────────────┐
│                                           │
└─► M2 (Wave 1)                             │
    │                                       │
    └─► M3 (Wave 2)                         │
        │                                   │
        └─► M4 (Wave 3)                     │
            │                               │
            └─► M5 (Wave 4-5)               │
                │                           │
                └─► M6 (Testing) ◄──────────┘

Internal D4 dependencies:
D4.1 (roadmap) → D4.3 (tasklists) → D4.4 (test-strategy)
                                  → D4.5 (execution-prompt)
                                    [D4.4 and D4.5 are concurrent eligible]
```

---

## Risk Register

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R-001 | MCP server unavailability (Sequential, Serena) | Medium | High | Circuit breaker + native Claude fallback |
| R-002 | Specification parsing failure | Low | Medium | Graceful degradation with partial extraction |
| R-003 | Validation score < 70% | Low | Medium | Draft preservation + improvement suggestions |
| R-004 | Template directory missing | High | Low | Inline template generation (Wave 0 check) |
| R-005 | Cross-document ID inconsistency | Medium | Medium | ID schema validation in Wave 4 |
| R-006 | TodoWrite state misuse | Medium | Low | Documentation + validation checks |

### Circuit Breaker Configuration (per MCP.md)
| Server | Failure Threshold | Timeout | Fallback |
|--------|-------------------|---------|----------|
| Sequential | 3 | 30s | Native Claude reasoning |
| Serena | 4 | 45s | Basic file operations |
| Context7 | 5 | 60s | WebSearch for patterns |

---

## Critical Corrections Checklist

| # | Correction | Applied In | Verification |
|---|------------|------------|--------------|
| 1 | Embed agent type in Task prompt (not subagent_type) | M5: D5.1 | Code review |
| 2 | CREATE template directory | M1: D1.3, D1.4 | Directory exists |
| 3 | Reference ORCHESTRATOR.md for compliance tiers | M5: D5.3 | Documentation check |
| 4 | TodoWrite has 3 states only | M3: D3.4 | Code validation |
| 5 | 7 wave-enabled commands | Documentation | Accuracy check |
| 6 | /sc:git subcommands don't exist | Documentation | Remove references |

---

## Success Criteria

### Functional Completion
- [ ] `/sc:roadmap` skill invocable via command
- [ ] 5-wave orchestration pipeline functional
- [ ] Multi-agent validation working (quality-engineer Task)
- [ ] All 5 required artifacts generated correctly
- [ ] TodoWrite integration correct (3 states only)
- [ ] All paths use SuperClaude conventions
- [ ] MCP circuit breakers functional

### Quality Metrics
- [ ] Requirement coverage: 100%
- [ ] ID traceability: 100%
- [ ] Validation score: ≥85%
- [ ] Template fit: ≥80%

### Performance Targets
- [ ] Wave 1 completion: < 30 seconds
- [ ] Full generation (standard): < 2 minutes
- [ ] Full generation (deep): < 5 minutes
- [ ] Validation phase: < 60 seconds

---

## Execution Summary

| Phase | Milestones | Key Deliverables | Risk Focus |
|-------|------------|------------------|------------|
| **Foundation** | M1 | Skill structure, templates | Directory creation |
| **Core Pipeline** | M2, M3, M4 | 5-wave orchestration | Parsing, generation |
| **Validation** | M5 | Multi-agent review | Task integration |
| **Quality** | M6 | Testing, docs | Coverage |

**Total Deliverables**: 28 across 6 milestones
**Estimated Timeline**: Based on complexity, execute M1 → M6 sequentially
**Primary Persona**: Backend (orchestration focus)

---

*Generated by SuperClaude Roadmap Generator v1.0*
*Specification: SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
*Validated against 6 critical corrections*
