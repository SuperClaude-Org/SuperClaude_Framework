# Release Roadmap: v3.0-roadmap-gen - Roadmap Generator Command

## Metadata
- **Source Specification**: `<project-root>/.dev/plans/v3.0_Roadmaps/v3.0_Roadmap-Generator-Specification.md`
- **Generated**: 2026-01-06T12:00:00Z
- **Generator Version**: v2.0
- **Codebase State**: N/A (new command)
- **Item Count**: 20 features, 0 bugs, 5 improvements, 1 refactor, 5 docs

### Persona Assignment

**Primary**: Backend — 54.8% of items are BACKEND work
**Consulting**:
- Architect for ARCHITECTURE items (16.1%)
- Scribe for DOCS items (16.1%)

**Rationale**: The majority of implementation work involves backend pipeline phases (extraction, generation, validation, crossLLM integration). Architecture expertise needed for command structure and integration protocol design. Documentation required for templates and user guides.

---

## Executive Summary

This release delivers `/rf:roadmap-gen`, a command that generates deterministic release roadmap packages from specification documents with automatic crossLLM-powered content upgrades. The implementation follows a 9-phase pipeline ensuring traceability, quality gates, and graceful degradation. Key outcomes include a production-ready command, 3 starter templates, comprehensive test coverage, and a reusable crossLLM Integration Protocol for future commands.

---

## Milestones Overview

| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|
| M1 | Foundation | 6 | None | Low |
| M2 | Template System | 5 | M1 | Medium |
| M3 | Core Generation Pipeline | 4 | M2 | Medium |
| M4 | crossLLM Integration | 8 | M3 | High |
| M5 | Enhancements & Polish | 5 | M4 | Low |
| M6 | Documentation & Testing | 3 | M5 | Low |

---

### Milestone 1: Foundation
**Objective**: Establish command infrastructure and core pipeline skeleton
**Dependencies**: None
**Estimated Complexity**: Low

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-001 | FEATURE | Command definition file `/rf:roadmap-gen` with full syntax, options parsing, and routing | GIVEN valid arguments WHEN command invoked THEN routes to orchestrator | `.opencode/command/rf:roadmap-gen.md` |
| REQ-002 | FEATURE | Orchestrator agent skeleton with 9-phase pipeline structure | GIVEN command routed WHEN orchestrator invoked THEN all phases callable | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-003 | FEATURE | Preflight validation (Phase 0) | GIVEN missing/invalid input WHEN Phase 0 executes THEN STOP with clear error | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-004 | FEATURE | Input extraction (Phase 1) | GIVEN valid spec WHEN Phase 1 executes THEN extraction.md created with unique IDs, valid types, domains, dependencies | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-005 | FEATURE | Persona selection (Phase 2) | GIVEN extraction complete WHEN Phase 2 executes THEN primary persona selected based on >40% domain, consulting personas >15% | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-005 | IMPROVEMENT | --output flag for custom output directory | GIVEN --output mydir WHEN command executes THEN artifacts written to .roadmaps/mydir/ | `.opencode/command/rf:roadmap-gen.md` |

#### Verification Checkpoint M1
- [ ] All deliverables code-complete
- [ ] Command definition parses all options correctly
- [ ] Orchestrator can be invoked and logs phase entry/exit
- [ ] Phase 0-2 execute without errors on valid input
- [ ] Phase 0 correctly rejects invalid inputs
- [ ] extraction.md follows required schema

---

### Milestone 2: Template System
**Objective**: Create starter templates and template evaluation logic
**Dependencies**: M1 (Phases 0-2 complete)
**Estimated Complexity**: Medium

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| DOC-001 | DOC | Create feature-release.md starter template | GIVEN feature-heavy spec WHEN template scored THEN this template ranks highest | `.opencode/resources/templates/roadmaps/feature-release.md` |
| DOC-002 | DOC | Create quality-release.md starter template | GIVEN QA/perf spec WHEN template scored THEN this template ranks highest | `.opencode/resources/templates/roadmaps/quality-release.md` |
| DOC-003 | DOC | Create documentation-release.md starter template | GIVEN docs refactor spec WHEN template scored THEN this template ranks highest | `.opencode/resources/templates/roadmaps/documentation-release.md` |
| REQ-006 | FEATURE | Template evaluation (Phase 2.5) | GIVEN persona selected WHEN Phase 2.5 executes THEN template selected or variant created | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-007 | FEATURE | Template scorer agent with scoring algorithm | GIVEN templates and extraction WHEN scorer invoked THEN scores returned with USE/VARIANT recommendation | `.opencode/agent/rf-roadmap-gen-template-scorer.md` |

#### Verification Checkpoint M2
- [ ] All 3 starter templates created with correct structure
- [ ] Templates placed in correct directory
- [ ] Template scorer agent defined and invocable
- [ ] Phase 2.5 correctly selects template ≥80% match
- [ ] Phase 2.5 correctly creates variant when <80% match
- [ ] template-selection.md generated with rationale

---

### Milestone 3: Core Generation Pipeline
**Objective**: Implement core artifact generation phases
**Dependencies**: M2 (Template system complete)
**Estimated Complexity**: Medium

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-008 | FEATURE | Roadmap construction (Phase 3) | GIVEN template selected WHEN Phase 3 executes THEN roadmap.md created with dependency-ordered milestones, acceptance criteria, traceability | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-009 | FEATURE | Test strategy generation (Phase 4) | GIVEN roadmap complete WHEN Phase 4 executes THEN test-strategy.md created with unit/integration/regression/acceptance matrix | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-010 | FEATURE | Execution prompt generation (Phase 5) | GIVEN test strategy complete WHEN Phase 5 executes THEN execution-prompt.md created with execution rules and checkpoints | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-011 | FEATURE | Self-validation (Phase 6) | GIVEN all artifacts generated WHEN Phase 6 executes THEN traceability verified: all extraction items appear exactly once | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

#### Verification Checkpoint M3
- [ ] All deliverables code-complete
- [ ] roadmap.md follows required schema with all sections
- [ ] test-strategy.md has coverage for all deliverables
- [ ] execution-prompt.md has valid artifact paths
- [ ] Phase 6 validates traceability and reports discrepancies
- [ ] All extraction items appear in exactly one milestone

---

### Milestone 4: crossLLM Integration
**Objective**: Implement upgrade pipeline with crossLLM and consistency validation
**Dependencies**: M3 (Core generation complete)
**Estimated Complexity**: High

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-012 | FEATURE | crossLLM integration (Phase 7) | GIVEN Phase 6 passed WHEN Phase 7 executes THEN /rf:crossLLM invoked for each upgradeable artifact | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-013 | FEATURE | Parallel upgrade execution | GIVEN 3 artifacts WHEN Phase 7 executes THEN all 3 upgrade concurrently | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-014 | FEATURE | Draft preservation | GIVEN artifact to upgrade WHEN crossLLM invoked THEN .draft.md copy created BEFORE upgrade | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-015 | FEATURE | Circuit breaker | GIVEN ≥50% artifacts fail WHEN failures detected THEN remaining upgrades stopped, drafts preserved | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-016 | FEATURE | Upgrade log generation | GIVEN upgrades complete WHEN Phase 7 ends THEN upgrade-log.md created with all results | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-020 | FEATURE | Version folder management | GIVEN --version N WHEN execution THEN v1/ through vN/ folders created | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-017 | FEATURE | Cross-artifact consistency validation (Phase 7.5) | GIVEN parallel upgrades complete WHEN Phase 7.5 executes THEN ID references, coverage, structural alignment verified | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-018 | FEATURE | Consistency report generation | GIVEN consistency validation complete WHEN Phase 7.5 ends THEN consistency-report.md created | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

#### Verification Checkpoint M4
- [ ] All deliverables code-complete
- [ ] crossLLM invoked correctly with proper chain
- [ ] Parallel execution confirmed (concurrent, not sequential)
- [ ] Draft files created before upgrade
- [ ] Circuit breaker triggers at correct threshold
- [ ] upgrade-log.md contains all required fields
- [ ] Phase 7.5 detects intentionally introduced inconsistencies
- [ ] consistency-report.md generated with findings

---

### Milestone 5: Enhancements & Polish
**Objective**: Implement optional flags and multi-iteration support
**Dependencies**: M4 (crossLLM integration complete)
**Estimated Complexity**: Low

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-019 | FEATURE | Multi-iteration upgrade support | GIVEN --version 3 WHEN execution THEN 2 sequential crossLLM iterations with chain cycling | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-001 | IMPROVEMENT | --chain flag | GIVEN --chain gpt>claude WHEN iteration 1 THEN specified chain used | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-002 | IMPROVEMENT | --upgrade-threshold flag | GIVEN --upgrade-threshold 15 WHEN crossLLM result THEN 15% threshold applied | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-003 | IMPROVEMENT | --upgrade-only flag | GIVEN --upgrade-only roadmap.md WHEN Phase 7 THEN only roadmap.md upgraded | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-004 | IMPROVEMENT | --sequential-upgrades flag | GIVEN --sequential-upgrades WHEN Phase 7 THEN upgrades run one-by-one, not parallel | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

#### Verification Checkpoint M5
- [ ] All deliverables code-complete
- [ ] --version 3 creates v1/, v2/, v3/ with correct chain sequence
- [ ] --chain overrides iteration 1 only
- [ ] --upgrade-threshold correctly filters results
- [ ] --upgrade-only limits which artifacts upgrade
- [ ] --sequential-upgrades forces sequential execution

---

### Milestone 6: Documentation & Testing
**Objective**: Complete documentation and validate all acceptance criteria
**Dependencies**: M5 (Enhancements complete)
**Estimated Complexity**: Low

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| DOC-004 | DOC | User documentation for /rf:roadmap-gen | GIVEN new user WHEN reading docs THEN can successfully invoke command | `docs/generated/Commands/roadmap-gen_UserDoc.md` |
| DOC-005 | DOC | Technical documentation | GIVEN developer WHEN reading docs THEN understands architecture, agents, protocol | `docs/generated/Commands/roadmap-gen_TD.md` |
| REF-001 | REFACTOR | Extract Integration Protocol to standalone document | GIVEN future command WHEN reading protocol THEN can integrate crossLLM | `docs/generated/crossLLM-Integration-Protocol.md` (update) |

#### Verification Checkpoint M6
- [ ] All deliverables code-complete
- [ ] User docs cover all syntax, options, examples
- [ ] Technical docs cover architecture, agents, protocol
- [ ] Integration Protocol is self-contained and reusable
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All acceptance criteria verified

---

## Dependency Graph

```
REQ-001 (Command definition)
    └── REQ-002 (Orchestrator skeleton)
            ├── REQ-003 (Phase 0: Preflight)
            │       └── REQ-004 (Phase 1: Extraction)
            │               └── REQ-005 (Phase 2: Persona)
            │                       └── REQ-006 (Phase 2.5: Template Eval)
            │                               ├── REQ-007 (Template Scorer)
            │                               └── REQ-008 (Phase 3: Roadmap)
            │                                       └── REQ-009 (Phase 4: Test Strategy)
            │                                               └── REQ-010 (Phase 5: Exec Prompt)
            │                                                       └── REQ-011 (Phase 6: Validation)
            │                                                               └── REQ-012 (Phase 7: crossLLM)
            │                                                                       ├── REQ-013 (Parallel upgrades)
            │                                                                       │       └── REQ-017 (Phase 7.5: Consistency)
            │                                                                       │               └── REQ-018 (Consistency Report)
            │                                                                       ├── REQ-014 (Draft preservation)
            │                                                                       ├── REQ-015 (Circuit breaker)
            │                                                                       ├── REQ-016 (Upgrade log)
            │                                                                       ├── REQ-019 (Multi-iteration)
            │                                                                       └── REQ-020 (Version folders)
            └── IMP-005 (--output flag)

DOC-001, DOC-002, DOC-003 (Templates) → None (can start immediately)

IMP-001, IMP-002, IMP-003, IMP-004 → REQ-012 (crossLLM integration)

DOC-004, DOC-005, REF-001 → All REQ complete
```

---

## Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R1 | crossLLM API changes break integration | Low | High | Version-lock interface contract; monitor crossLLM releases |
| R2 | Upgrade threshold too strict (many FAILs) | Medium | Medium | Make threshold configurable (IMP-002); default 25% |
| R3 | Large specs cause Phase 1 timeout | Medium | Medium | Implement chunking strategy; set reasonable timeout |
| R4 | Model availability issues | Low | High | Fallback to --no-upgrade; document graceful degradation |
| R5 | Template scoring algorithm produces inconsistent results | Medium | Medium | Use Sequential Thinking MCP for algorithm design; extensive testing |
| R6 | Parallel upgrades cause resource exhaustion | Low | Medium | IMP-004 provides --sequential-upgrades escape hatch |
| R7 | Phase 7.5 consistency validation too strict | Medium | Low | Log warnings only for minor issues; flag for review moderate issues |

---

## Success Criteria Tracking

| Criterion | Target | Verification Method |
|-----------|--------|---------------------|
| Command functional | All 9 phases execute | Integration test: full pipeline |
| Modularity maintained | 0 crossLLM imports | Code review: grep for imports |
| Upgrade success rate | ≥75% artifacts pass | Integration test: measure PASS rate |
| Template selection accuracy | Correct template for domain | Unit test: domain-specific fixtures |
| Documentation complete | User + Tech docs | Review: all sections filled |
| Tests passing | 100% pass rate | CI: run full test suite |

---

*Generated by Roadmap-Generator v2.0*
