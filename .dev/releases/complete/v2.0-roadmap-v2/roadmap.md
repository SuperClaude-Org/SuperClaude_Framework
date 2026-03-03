---
spec_source: .dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md
generated_by: sc:roadmap
generated_at: "2026-02-21"
depth: standard
template: inline
complexity_score: 0.645
complexity_class: MEDIUM
primary_persona: architect
domain_distribution:
  backend: 53
  architecture: 29
  quality: 12
  frontend: 6
total_requirements: 20
total_deliverables: 37
milestone_count: 7
milestone_index:
  - id: M1
    title: "Architecture Foundation"
    type: INFRASTRUCTURE
    priority: P0
    deliverable_count: 5
  - id: M2
    title: "Extraction Pipeline"
    type: FEATURE
    priority: P0
    deliverable_count: 6
  - id: M3
    title: "Core Generation Pipeline"
    type: FEATURE
    priority: P1
    deliverable_count: 6
  - id: M4
    title: "Adversarial Integration"
    type: FEATURE
    priority: P1
    deliverable_count: 5
  - id: M5
    title: "Validation & Quality Gates"
    type: FEATURE
    priority: P1
    deliverable_count: 6
  - id: M6
    title: "Command Interface & Session Management"
    type: FEATURE
    priority: P1
    deliverable_count: 5
  - id: M7
    title: "Polish, Edge Cases & Combined Mode"
    type: IMPROVEMENT
    priority: P2
    deliverable_count: 4
validation_status: PENDING
validation_score: null
---

# Roadmap: sc:roadmap v2 — Redesigned Planning Pipeline

## Overview

This roadmap implements the SC-ROADMAP-V2-SPEC, which redesigns the sc:roadmap command from a monolithic 2,490-line SKILL.md into a lean behavioral SKILL.md (~400 lines) backed by 5 reference files in a refs/ directory. The pipeline follows a 5-wave architecture (Wave 0 prerequisites → Wave 1A/1B analysis → Wave 2 planning → Wave 3 generation → Wave 4 validation) and produces three artifacts: roadmap.md, extraction.md, and test-strategy.md.

Key architectural decisions include the SKILL.md split pattern with on-demand ref loading, YAML frontmatter as a versioned contract for downstream consumption, chunked extraction for large specs, and integration with sc:adversarial for multi-spec consolidation and multi-roadmap generation modes.

The complexity score is 0.645 (MEDIUM), driven by 20 requirements across 4 domains, a 5-wave pipeline with internal dependencies, and integration with external systems (sc:adversarial, Serena MCP, sc:save/sc:load).

## Milestone Summary

| ID | Title | Type | Priority | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------------|--------------|------|
| M1 | Architecture Foundation | INFRASTRUCTURE | P0 | None | 5 | Medium |
| M2 | Extraction Pipeline | FEATURE | P0 | M1 | 6 | Medium |
| M3 | Core Generation Pipeline | FEATURE | P1 | M2 | 6 | Low |
| M4 | Adversarial Integration | FEATURE | P1 | M3 | 5 | Medium |
| M5 | Validation & Quality Gates | FEATURE | P1 | M3 | 6 | Low |
| M6 | Command Interface & Session | FEATURE | P1 | M1 | 5 | Low |
| M7 | Polish & Combined Mode | IMPROVEMENT | P2 | M4, M5, M6 | 4 | Low |

## Dependency Graph

```
M1 (Architecture Foundation)
├── M2 (Extraction Pipeline)
│   └── M3 (Core Generation Pipeline)
│       ├── M4 (Adversarial Integration)
│       └── M5 (Validation & Quality Gates)
├── M6 (Command Interface & Session)
│
└── M7 (Polish & Combined Mode) ← depends on M4, M5, M6
```

Note: M4 and M5 can be developed in parallel after M3. M6 can be developed in parallel with M2/M3 (only depends on M1).

---

## M1: Architecture Foundation

### Objective
Establish the SKILL.md split pattern, refs/ directory structure, and on-demand ref loading protocol that all subsequent milestones depend on.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Lean SKILL.md (~400 lines) with wave orchestration instructions | ≤500 lines, no YAML pseudocode, references each ref file by name |
| D1.2 | refs/extraction-pipeline.md with 8-step extraction + chunked protocol | Contains domain keyword dictionaries, ID assignment rules, 4-pass verification |
| D1.3 | refs/scoring.md with complexity + template compatibility scoring | 5-factor formula with weights, classification thresholds, persona confidence calc |
| D1.4 | refs/templates.md with 4-tier discovery + inline generation | Search paths, version resolution, milestone count selection, plugin tier annotated [future: v5.0] |
| D1.5 | refs/validation.md with agent prompts + score aggregation | quality-engineer prompt, self-review prompt, PASS/REVISE/REJECT thresholds |

### Dependencies
- None (first milestone)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SKILL.md split causes Claude to miss ref files | Medium | High | Explicit name references in SKILL.md; on-demand loading protocol |
| SKILL.md exceeds 500-line limit | Low | Medium | Strict content boundary: behavioral instructions only, all algorithms in refs/ |

---

## M2: Extraction Pipeline

### Objective
Implement Wave 0 (prerequisite validation) and Wave 1B (detection, analysis, extraction.md generation) including the chunked extraction protocol for large specs.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Wave 0: spec file validation, output dir setup, collision detection (-N suffix) | Validates file exists/readable, creates output dir, detects collisions |
| D2.2 | Wave 0: model identifier validation for --agents flag | Validates all model names before starting pipeline |
| D2.3 | Wave 1B: 8-step extraction pipeline (title → FRs → NFRs → scope → deps → success criteria → risks → IDs) | Produces complete extraction.md with all 9 structured sections |
| D2.4 | Wave 1B: domain classification with keyword weighting | Correct domain percentages, primary persona assignment with confidence score |
| D2.5 | Wave 1B: complexity scoring (5-factor weighted formula) | Score computable, classification thresholds applied correctly |
| D2.6 | Wave 1B: chunked extraction for >500 line specs | Section indexing, chunk assembly, per-chunk extraction, merge, dedup, 4-pass verification |

### Dependencies
- M1: refs/extraction-pipeline.md and refs/scoring.md must exist

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Large spec files overwhelm context | Medium | High | Chunked extraction with 400-line target chunks |
| Chunked extraction misses requirements | Medium | High | 4-pass completeness verification with zero-tolerance anti-hallucination |

---

## M3: Core Generation Pipeline

### Objective
Implement Wave 2 (template selection, milestone planning, dependency mapping) and Wave 3 (roadmap.md + test-strategy.md generation).

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Wave 2: template discovery (4-tier search) with compatibility scoring | Searches local → user → plugin [future] → inline; selects best match |
| D3.2 | Wave 2: milestone extraction with dependency mapping | Milestones have IDs, types, priorities, dependency graph |
| D3.3 | Wave 2: effort estimation per milestone | Each milestone has estimated effort and risk level |
| D3.4 | Wave 3: roadmap.md generation with full body template | Overview, milestone summary, dependency graph, per-milestone sections, risk register, Decision Summary |
| D3.5 | Wave 3: test-strategy.md generation (authored by SKILL.md, hardened) | Interleave ratio computed from complexity, validation milestones reference work milestones, continuous parallel validation philosophy |
| D3.6 | Wave 3: YAML frontmatter generation with all required fields | spec_source/spec_sources mutual exclusion, milestone_index, complexity fields |

### Dependencies
- M2: extraction.md and complexity score must be available

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Template matching produces poor fit | Low | Medium | Inline generation fallback always available |
| test-strategy.md quality dilution | Low | Medium | Hardened instructions: explicit generation order, structural template, detailed sections |

---

## M4: Adversarial Integration

### Objective
Implement Wave 1A (sc:adversarial invocation for multi-spec and multi-roadmap modes) and the refs/adversarial-integration.md reference file.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | refs/adversarial-integration.md with mode detection + invocation patterns | Documents both invocation patterns, return contract consumption, error handling |
| D4.2 | Wave 1A: multi-spec consolidation via sc:adversarial --compare | Invokes correctly, handles success/partial/failed status, records convergence_score |
| D4.3 | Wave 1A: multi-roadmap generation via sc:adversarial --generate | Invokes with agent specs, handles merged output, records artifacts_dir |
| D4.4 | Agent specification parsing (model:persona:"instruction" format) | Handles model-only, mixed, full specs; validates 2-10 range; orchestrator at ≥5 |
| D4.5 | --interactive flag propagation to sc:adversarial | Interactive prompts at convergence thresholds and decision points |

### Dependencies
- M3: core generation pipeline for single-spec mode must work first
- DEP-001: sc:adversarial skill must be available

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| sc:adversarial not installed | Low | High | Wave 0 checks availability; abort with install instructions |
| Partial convergence produces poor unified spec | Medium | Medium | Convergence ≥60% proceed with warning; <60% abort or prompt |
| Unrecognized model identifiers | Low | Medium | Wave 0 validates all models before starting |

---

## M5: Validation & Quality Gates

### Objective
Implement Wave 4 (multi-agent validation, REVISE loop) and the quality gate scoring system.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | quality-engineer agent dispatch with completeness/consistency/traceability checks | Agent prompt in refs/validation.md, dispatched in Wave 4 |
| D5.2 | self-review agent dispatch with 4-question protocol | Agent prompt in refs/validation.md, dispatched in Wave 4 |
| D5.3 | Score aggregation formula producing PASS/REVISE/REJECT | ≥85% PASS, 70-84% REVISE, <70% REJECT |
| D5.4 | REVISE loop: Wave 3 → Wave 4 re-execution (max 2 iterations) | Improvement recommendations fed back to Wave 3; 2nd failure → PASS_WITH_WARNINGS |
| D5.5 | test-strategy.md validation criteria in Wave 4 | Validates interleave ratio, milestone references, philosophy encoding, stop-and-fix thresholds |
| D5.6 | --no-validate flag support | Sets validation_score: 0.0, validation_status: SKIPPED, skips Wave 4 |

### Dependencies
- M3: roadmap.md and test-strategy.md must exist for validation

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Validation agents produce inconsistent scores | Low | Medium | Score aggregation formula with defined weights |
| REVISE loop does not converge | Low | Low | Max 2 iterations with PASS_WITH_WARNINGS fallback |

---

## M6: Command Interface & Session Management

### Objective
Update the roadmap.md command file with all flags and examples, and implement session persistence via sc:save/sc:load integration.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Updated roadmap.md command file with all flags (--specs, --multi-roadmap, --agents, --depth, --interactive, --no-validate, --output, --template, --dry-run, --compliance) | Complete flag documentation with types and defaults |
| D6.2 | Updated examples covering single-spec, multi-spec, multi-roadmap, combined, model-only | At least 7 examples demonstrating all modes |
| D6.3 | sc:save integration at wave boundaries | Save points after each wave with Serena memory schema |
| D6.4 | sc:load resume protocol with spec-hash mismatch detection | Detects incomplete sessions, offers resume, validates spec unchanged |
| D6.5 | Progress reporting at wave boundaries | Reports current wave, elapsed context, next steps |

### Dependencies
- M1: SKILL.md must exist for wave boundary definitions
- DEP-002: sc:save/sc:load must be available

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Interrupted session produces stale artifacts | Low | Medium | Spec-hash mismatch detection warns user |
| Serena MCP unavailable | Low | Low | Proceed without persistence, warn user |

---

## M7: Polish, Edge Cases & Combined Mode

### Objective
Implement combined mode (multi-spec + multi-roadmap chaining), interactive mode refinements, and handle remaining edge cases.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | Combined mode: chains multi-spec consolidation → multi-roadmap generation | Both adversarial passes execute in sequence; artifacts chained correctly |
| D7.2 | Interactive mode user prompts at all decision points | Prompts for persona selection, template choice, convergence thresholds |
| D7.3 | --dry-run flag: preview roadmap structure without writing files | Outputs structure to console, no files written |
| D7.4 | Edge case handling: empty specs, invalid YAML, circular dependencies | Graceful errors with actionable messages |

### Dependencies
- M4: adversarial integration for combined mode
- M5: validation for quality gate edge cases
- M6: command interface for flag handling

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Combined mode takes too long | Medium | Low | Progress reporting keeps user informed |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | SKILL.md split causes Claude to miss ref files | M1, M2, M3 | Medium | High | Explicit name references; on-demand loading protocol | architect |
| R-002 | sc:adversarial unavailable | M4, M7 | Low | High | Wave 0 detection; abort with install instructions | backend |
| R-003 | Frontmatter schema breaks tasklist generator | M3, M6 | Medium | Medium | Versioned contract; additions only, no removals | architect |
| R-004 | Multi-spec incoherent unified spec | M4 | Medium | Medium | Adversarial debate + convergence thresholds | architect |
| R-005 | Combined mode too slow | M7 | Medium | Low | Progress reporting; no timeout constraints | backend |
| R-006 | Adversarial partial status quality degradation | M4 | Medium | Medium | ≥60% proceed with warning; <60% abort or prompt | architect |
| R-007 | Large specs overwhelm context | M2 | Medium | High | Chunked extraction; 4-pass verification | backend |
| R-008 | Interrupted session stale artifacts | M6 | Low | Medium | sc:save at wave boundaries; spec-hash detection | backend |
| R-009 | Unrecognized model in --agents | M4 | Low | Medium | Wave 0 model validation | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect | backend (53% domain), qa (12%) | Pipeline orchestration and system design scope outweigh raw domain % |
| Template | inline | No project-local or user templates detected | Fallback to inline generation per 4-tier discovery |
| Milestone Count | 7 | 5-9 range for MEDIUM complexity | 7 milestones: 2 P0 foundation + 3 P1 parallel tracks + 1 P1 interface + 1 P2 polish |
| Adversarial Mode | none | N/A | Single-spec mode; no --specs or --multi-roadmap flags |
| Adversarial Base Variant | N/A | N/A | Not applicable in single-spec mode |
| test-strategy Authorship | SKILL.md (Wave 3, hardened) | quality-engineer (Wave 4), dedicated agent (Wave 3) | Temporal correctness + adversarial integrity preserved; zero coordination overhead |

## Success Criteria

- All 17 functional requirements traceable to at least one deliverable
- SKILL.md ≤500 lines; refs/ contains 5 files
- YAML frontmatter parseable by standard YAML parsers
- Single-spec, multi-spec, multi-roadmap, and combined modes functional
- Wave 4 validation produces score with PASS/REVISE/REJECT determination
- test-strategy.md encodes continuous parallel validation with computed interleave ratio
- Session persistence enables cross-session resumability
- Chunked extraction handles specs >500 lines without data loss
