# Extraction: /sc:roadmap Command Feature Specification

## Metadata
- **Source**: `.roadmaps/v.1.4-roadmap-gen/SC-ROADMAP-FEATURE-SPEC.md`
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Specification Version**: 1.1.0

---

## Executive Summary

The `/sc:roadmap` command is a SuperClaude skill that generates comprehensive, structured release roadmaps from specification documents. It implements a 5-wave orchestration pipeline with multi-agent validation, transforming project requirements into actionable milestone-based roadmaps.

**Key Differentiator**: Unlike general planning tools, `/sc:roadmap` **requires** a specification file as mandatory input, ensuring roadmaps are grounded in documented requirements.

---

## Extracted Requirements

### Functional Requirements

| ID | Type | Domain | Description | Priority | Dependencies |
|----|------|--------|-------------|----------|--------------|
| FR-001 | FEATURE | backend | Command interface with required spec file input | P0-Critical | None |
| FR-002 | FEATURE | backend | 5-wave orchestration pipeline (Detection, Planning, Generation, Validation, Completion) | P0-Critical | FR-001 |
| FR-003 | FEATURE | backend | Wave 1: Specification parsing and requirements extraction | P0-Critical | FR-002 |
| FR-004 | FEATURE | backend | Wave 1: Complexity scoring with 5-factor weighted formula | P1-High | FR-003 |
| FR-005 | FEATURE | backend | Wave 1: Persona auto-activation based on domain distribution | P1-High | FR-004 |
| FR-006 | FEATURE | backend | Wave 2: Template discovery hierarchy (local → user → plugin → inline) | P1-High | FR-005 |
| FR-007 | FEATURE | backend | Wave 2: Inline template generation algorithm | P1-High | FR-006 |
| FR-008 | FEATURE | backend | Wave 2: TodoWrite task initialization (3 states only) | P0-Critical | FR-007 |
| FR-009 | FEATURE | backend | Wave 3: Generate roadmap.md master document | P0-Critical | FR-008 |
| FR-010 | FEATURE | backend | Wave 3: Generate extraction.md requirements summary | P1-High | FR-009 |
| FR-011 | FEATURE | backend | Wave 3: Generate tasklist files per milestone | P0-Critical | FR-009 |
| FR-012 | FEATURE | backend | Wave 3: Generate test-strategy.md validation approach | P1-High | FR-011 |
| FR-013 | FEATURE | backend | Wave 3: Generate execution-prompt.md implementation guide | P1-High | FR-011 |
| FR-014 | FEATURE | backend | Wave 4: Multi-agent validation with quality-engineer Task | P0-Critical | FR-013 |
| FR-015 | FEATURE | backend | Wave 4: Self-review validation protocol (4-question) | P1-High | FR-014 |
| FR-016 | FEATURE | backend | Wave 4: Score aggregation (PASS ≥85%, REVISE 70-84%, REJECT <70%) | P1-High | FR-015 |
| FR-017 | FEATURE | backend | Wave 5: Completion check via think_about_whether_you_are_done() | P1-High | FR-016 |
| FR-018 | FEATURE | backend | Wave 5: Memory persistence via Serena MCP | P1-High | FR-017 |

### Non-Functional Requirements

| ID | Type | Domain | Description | Priority | Metric |
|----|------|--------|-------------|----------|--------|
| NFR-001 | PERFORMANCE | backend | Wave 1 completion < 30 seconds | P1-High | Time |
| NFR-002 | PERFORMANCE | backend | Full generation (standard depth) < 2 minutes | P1-High | Time |
| NFR-003 | PERFORMANCE | backend | Full generation (deep depth) < 5 minutes | P2-Medium | Time |
| NFR-004 | PERFORMANCE | backend | Validation phase < 60 seconds | P1-High | Time |
| NFR-005 | QUALITY | architecture | Requirement coverage = 100% | P0-Critical | Percentage |
| NFR-006 | QUALITY | architecture | ID traceability = 100% | P0-Critical | Percentage |
| NFR-007 | QUALITY | qa | Validation score target ≥ 85% | P1-High | Percentage |
| NFR-008 | RELIABILITY | backend | MCP circuit breaker support | P1-High | Boolean |

### Implementation Items

| ID | Type | Domain | Description | Priority | Files Affected |
|----|------|--------|-------------|----------|----------------|
| IMP-001 | IMPROVEMENT | backend | Parallelization strategy across Wave 3 | P2-Medium | Orchestration logic |
| IMP-002 | IMPROVEMENT | backend | Error recovery patterns (partial roadmaps, drafts) | P2-Medium | Error handling |
| IMP-003 | IMPROVEMENT | backend | Compliance tier auto-classification | P1-High | Tier classifier |
| IMP-004 | IMPROVEMENT | architecture | ID schema with cross-document traceability | P1-High | All artifacts |

### Documentation Items

| ID | Type | Domain | Description | Priority | Files Affected |
|----|------|--------|-------------|----------|----------------|
| DOC-001 | DOC | scribe | Create SKILL.md definition file | P0-Critical | `.claude/skills/sc-roadmap/SKILL.md` |
| DOC-002 | DOC | scribe | Create 6 template files | P1-High | `plugins/superclaude/templates/roadmaps/*.md` |
| DOC-003 | DOC | scribe | Test strategy documentation | P1-High | `test-strategy.md` |
| DOC-004 | DOC | scribe | Execution prompt documentation | P1-High | `execution-prompt.md` |

---

## Domain Distribution Analysis

| Domain | Item Count | Percentage | Primary Persona Candidate |
|--------|------------|------------|--------------------------|
| Backend (orchestration, pipeline) | 18 | 45% | ✅ backend |
| Architecture (system design) | 10 | 25% | architect |
| Documentation (guides, templates) | 8 | 20% | scribe |
| QA (validation, testing) | 4 | 10% | qa |
| **TOTAL** | **40** | **100%** | |

---

## Complexity Analysis

### Factor Scoring

| Factor | Weight | Raw Score | Contribution | Rationale |
|--------|--------|-----------|--------------|-----------|
| Requirement count | 0.25 | 0.80 | 0.20 | 40 items (>20 = high) |
| Dependency depth | 0.25 | 0.75 | 0.19 | MCP servers, personas, templates |
| Domain spread | 0.20 | 0.70 | 0.14 | 4 distinct domains |
| Risk severity | 0.15 | 0.85 | 0.13 | Multi-file generation, validation |
| Scope size | 0.15 | 0.80 | 0.12 | New skill + infrastructure |

### Total Complexity Score: **0.78** (HIGH)

**Classification**: complexity > 0.7 → 5-8 milestones recommended

---

## Persona Assignment

### Primary Persona
**Backend** — 45% of items are backend/orchestration work
- Confidence: 88% (≥85% threshold for primary)
- Rationale: Wave pipeline implementation, artifact generation, MCP integration

### Consulting Personas
| Persona | Coverage | Confidence | Role |
|---------|----------|------------|------|
| Architect | 25% | 75% | System design, dependency management |
| Scribe | 20% | 72% | Documentation, templates, guides |
| QA | 10% | 68% | Validation, testing (below 70% threshold) |

### Fallback
**Architect** — Available for system-wide coordination decisions

---

## Dependencies Identified

### External Dependencies
| Dependency | Type | Risk Level | Mitigation |
|------------|------|------------|------------|
| Sequential MCP | MCP Server | Medium | Native Claude reasoning fallback |
| Serena MCP | MCP Server | Medium | Basic file operations fallback |
| Context7 MCP | MCP Server | Low | WebSearch fallback |

### Internal Dependencies
| Dependency | Type | Required By |
|------------|------|-------------|
| Specification file | Input | Wave 1 start |
| Extracted requirements | Wave Output | Wave 2 planning |
| Milestone structure | Wave Output | Wave 3 generation |
| Generated artifacts | Wave Output | Wave 4 validation |
| Validation score | Wave Output | Wave 5 completion |

---

## Critical Corrections (from spec Section 6)

| # | Incorrect Pattern | Correct Pattern | Status |
|---|-------------------|-----------------|--------|
| 1 | `subagent_type` as Task API parameter | Embed agent type in Task prompt | ⚠️ TO APPLY |
| 2 | Templates exist by default | CREATE `plugins/superclaude/templates/roadmaps/` | ⚠️ TO APPLY |
| 3 | Compliance tiers in RULES.md | Compliance tiers in **ORCHESTRATOR.md** | ⚠️ TO APPLY |
| 4 | TodoWrite has "blocked" state | Only 3 states: pending, in_progress, completed | ⚠️ TO APPLY |
| 5 | Wave-enabled command count | 7 commands (not 6) | ⚠️ TO APPLY |
| 6 | /sc:git has tag, diff, log | These subcommands don't exist | ⚠️ TO APPLY |

---

## Risks Identified

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R-001 | MCP server unavailability during generation | Medium | High | Circuit breaker + native fallbacks |
| R-002 | Specification parsing failure (malformed input) | Low | Medium | Graceful degradation with partial extraction |
| R-003 | Validation score < 70% causing rejection | Low | Medium | Draft preservation + improvement suggestions |
| R-004 | Template directory missing | High | Low | Inline template generation fallback |
| R-005 | Cross-document ID inconsistency | Medium | Medium | ID schema enforcement + validation |

---

## Success Criteria (from spec Section 11)

### Generation Quality Targets
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

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Functional Requirements | 18 |
| Total Non-Functional Requirements | 8 |
| Total Implementation Items | 4 |
| Total Documentation Items | 4 |
| **Total Items** | **34** |
| Complexity Score | 0.78 (HIGH) |
| Recommended Milestones | 6 |
| Primary Persona | Backend |
| Consulting Personas | Architect, Scribe |

---

*Generated by SuperClaude Roadmap Generator v1.0*
*Source Specification: SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
