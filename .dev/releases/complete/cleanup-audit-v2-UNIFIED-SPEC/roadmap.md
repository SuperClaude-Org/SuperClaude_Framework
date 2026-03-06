---
spec_source: /config/workspace/SuperClaude_Framework/.dev/releases/backlog/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-25T00:00:00Z
generator: sc:roadmap
complexity_score: 0.799
complexity_class: HIGH
domain_distribution:
  backend: 55
  performance: 15
  security: 12
  documentation: 10
  infrastructure: 8
primary_persona: backend
consulting_personas: [architect, security]
milestone_count: 10
milestone_index:
  - id: M1
    title: Enforce Existing Spec Promises
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 5
    risk_level: High
  - id: M2
    title: Correctness Fixes and Scanner Schema Hardening
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: High
  - id: M3
    title: Profile and Batch Planning Infrastructure
    type: FEATURE
    priority: P1
    dependencies: [M2]
    deliverable_count: 6
    risk_level: Medium
  - id: M4
    title: Structural Audit Depth Implementation
    type: FEATURE
    priority: P1
    dependencies: [M3]
    deliverable_count: 5
    risk_level: High
  - id: M5
    title: Cross-Reference Synthesis and Hybrid Graphing
    type: FEATURE
    priority: P1
    dependencies: [M4]
    deliverable_count: 5
    risk_level: High
  - id: M6
    title: Consolidation and Validation Engine
    type: TEST
    priority: P1
    dependencies: [M5]
    deliverable_count: 5
    risk_level: Medium
  - id: M7
    title: Budget Controls and Degradation Logic
    type: IMPROVEMENT
    priority: P1
    dependencies: [M3, M4, M5]
    deliverable_count: 4
    risk_level: High
  - id: M8
    title: Reporting, Resume, and Anti-Lazy Enforcement
    type: IMPROVEMENT
    priority: P2
    dependencies: [M6]
    deliverable_count: 4
    risk_level: Medium
  - id: M9
    title: Optional Full Docs Audit and Known-Issues Registry
    type: DOC
    priority: P3
    dependencies: [M8]
    deliverable_count: 4
    risk_level: Medium
  - id: M10
    title: Final Acceptance and Benchmark Validation
    type: TEST
    priority: P1
    dependencies: [M1, M2, M3, M4, M5, M6, M7, M8]
    deliverable_count: 5
    risk_level: High
total_deliverables: 48
total_risks: 18
estimated_phases: 5
validation_score: 0.89
validation_status: PASS
adversarial:
  mode: multi-roadmap
  agents: [opus:backend, sonnet:backend, haiku:backend]
  convergence_score: 0.86
  base_variant: sonnet:backend
  artifacts_dir: /config/workspace/SuperClaude_Framework/.dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/adversarial
---

# Roadmap: sc:cleanup-audit v2

## Overview
This roadmap implements the unified cleanup-audit v2 specification by prioritizing closure of existing v1 promise gaps before adding optional extensions. The strategy emphasizes deterministic evidence collection, tiered analysis depth, and resilient execution under token constraints.

The selected base variant came from adversarial multi-roadmap comparison and was merged with high-value non-base improvements. Specifically, we retained strict AC-to-milestone traceability and static-tools-first dependency synthesis, while also incorporating explicit budget realism and context-window pressure controls.

Given HIGH complexity (0.799), the roadmap uses 10 milestones with explicit dependency sequencing and continuous validation interleaving.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|---|---|---|---|---|---|---:|---|
| M1 | Enforce Existing Spec Promises | FEATURE | P0 | M | None | 5 | High |
| M2 | Correctness Fixes and Scanner Schema Hardening | FEATURE | P0 | M | M1 | 5 | High |
| M3 | Profile and Batch Planning Infrastructure | FEATURE | P1 | M | M2 | 6 | Medium |
| M4 | Structural Audit Depth Implementation | FEATURE | P1 | M | M3 | 5 | High |
| M5 | Cross-Reference Synthesis and Hybrid Graphing | FEATURE | P1 | M | M4 | 5 | High |
| M6 | Consolidation and Validation Engine | TEST | P1 | M | M5 | 5 | Medium |
| M7 | Budget Controls and Degradation Logic | IMPROVEMENT | P1 | S | M3,M4,M5 | 4 | High |
| M8 | Reporting, Resume, and Anti-Lazy Enforcement | IMPROVEMENT | P2 | S | M6 | 4 | Medium |
| M9 | Optional Full Docs Audit and Known-Issues Registry | DOC | P3 | S | M8 | 4 | Medium |
| M10 | Final Acceptance and Benchmark Validation | TEST | P1 | M | M1-M8 | 5 | High |

## Dependency Graph
M1 → M2 → M3 → M4 → M5 → M6 → M8 → M9

M3 → M7
M4 → M7
M5 → M7

M1,M2,M3,M4,M5,M6,M7,M8 → M10

## M1: Enforce Existing Spec Promises

### Objective
Implement all v1-promised but missing behaviors as a non-negotiable baseline before introducing additional features.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D1.1 | Two-tier classification with backward mapping | AC1, AC15 |
| D1.2 | Coverage tracking by risk tier | AC2 |
| D1.3 | Batch-level checkpointing (`progress.json`) | AC3 |
| D1.4 | Evidence-gated DELETE/KEEP rules | AC4, AC5 |
| D1.5 | 10% consistency validation pass | AC6 |

### Dependencies
- None

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Spec drift persists | Medium | High | AC-gated completion with explicit traceability checks |

## M2: Correctness Fixes and Scanner Schema Hardening

### Objective
Eliminate known correctness failures and lock scanner output contracts.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D2.1 | Real credential scanning with safe redaction | AC7 |
| D2.2 | Gitignore inconsistency detection | AC8 |
| D2.3 | Phase-1 simplified scanner schema | AC11 |
| D2.4 | Phase-2 full profile schema alignment | AC11 (extended) |
| D2.5 | Batch failure/retry handling policy | AC18 (partial) |

### Dependencies
- M1

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Secret leakage in output | Low | High | Never print secret values; output-scrub checks |

## M3: Profile and Batch Planning Infrastructure

### Objective
Build robust Phase-0 profiling and manifest generation as the substrate for all subsequent phases.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D3.1 | Domain/risk-tier profiling | AC13 |
| D3.2 | Monorepo-aware batch decomposition | AC20 (supporting) |
| D3.3 | Static-tool orchestration and caching | AC12 (supporting) |
| D3.4 | Auto-config generation for cold start | AC13 |
| D3.5 | Dry-run profile and estimate output | AC19 |
| D3.6 | Manifest completeness gate | AC2 (quality extension) |

### Dependencies
- M2

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Mis-tiering cascades downstream | Medium | High | Conservative defaults + visible profile outputs |

## M4: Structural Audit Depth Implementation

### Objective
Implement deep per-file profiling and evidence depth controls for high-risk decisions.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D4.1 | 8-field profile generation for target sets | AC10 (detailed profile presence) |
| D4.2 | File-type specific verification rules | AC12 (supporting) |
| D4.3 | Signal-triggered full-file escalation | AC17 (supporting) |
| D4.4 | Tiered KEEP evidence enforcement | AC5 |
| D4.5 | Env key-presence matrix for drift | AC7 (supporting) |

### Dependencies
- M3

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Token overuse in deep reads | High | Medium | Trigger-based escalation + bounded defaults |

## M5: Cross-Reference Synthesis and Hybrid Graphing

### Objective
Synthesize static-tools, grep, and inference evidence into dependency and duplication intelligence.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D5.1 | 3-tier dependency graph with confidence labels | AC12 |
| D5.2 | Cross-boundary dead code candidate logic | AC12 (supporting) |
| D5.3 | Duplication matrix with consolidation thresholds | AC12 (supporting) |
| D5.4 | Minimal docs audit (broken refs + temporal) | AC14 |
| D5.5 | Dynamic-import-safe classification policy | AC17 (supporting) |

### Dependencies
- M4

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| False deletes from low-confidence links | Medium | High | Tier-C never promotes to DELETE |

## M6: Consolidation and Validation Engine

### Objective
Merge findings, deduplicate, and run stratified revalidation for consistency.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D6.1 | Cross-phase dedup consolidation | AC18 (supporting) |
| D6.2 | Stratified 10% spot-check validation | AC6 |
| D6.3 | Consistency-rate and calibration framing | AC6 (quality extension) |
| D6.4 | Coverage + validation output artifacts | AC2, AC6 |
| D6.5 | Directory assessment blocks for large dirs | AC16 |

### Dependencies
- M5

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Misleading validation interpretation | Medium | Medium | Explicit limitations language in report |

## M7: Budget Controls and Degradation Logic

### Objective
Implement practical budget governance with predictable degradation behavior.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D7.1 | Budget accounting and enforcement | AC9 |
| D7.2 | Degradation sequence implementation | AC9 (supporting) |
| D7.3 | Degrade-priority override handling | AC9 (supporting) |
| D7.4 | Budget realism caveat/reporting | AC19 (supporting) |

### Dependencies
- M3, M4, M5

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Underestimated runtime/token needs | High | High | Dry-run + benchmark calibration |

## M8: Reporting, Resume, and Anti-Lazy Enforcement

### Objective
Deliver operator-facing reliability and output usability guarantees.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D8.1 | Report depth modes (summary/standard/detailed) | AC10 |
| D8.2 | Resume semantics from checkpoints | AC3 |
| D8.3 | Anti-lazy distribution and consistency guards | AC18 (supporting) |
| D8.4 | Final report section completeness checks | AC1, AC16 |

### Dependencies
- M6

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Incomplete or noisy operator output | Medium | Medium | Depth control + strict report schema |

## M9: Optional Full Docs Audit and Known-Issues Registry

### Objective
Add opt-in depth for documentation quality and cross-run suppression workflows.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D9.1 | Full docs pass (`--pass-docs`) with 5-section output | AC14 (extended) |
| D9.2 | Known-issues registry load/match/output | AC20 (supporting) |
| D9.3 | TTL/LRU lifecycle rules in registry behavior | AC20 (supporting) |
| D9.4 | ALREADY_TRACKED report section integration | AC1 (supporting) |

### Dependencies
- M8

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Extension complexity without baseline stability | Low | Medium | Gate behind completion of M1-M8 |

## M10: Final Acceptance and Benchmark Validation

### Objective
Validate the full v2 contract against AC1-AC20 and benchmark repos.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D10.1 | AC1-AC20 automated validation suite | AC1-AC20 |
| D10.2 | Benchmark runs (small/medium/known-dead-code repo) | AC9, AC12, AC17 |
| D10.3 | Concurrent-run isolation validation | AC20 |
| D10.4 | Non-determinism/limitations reporting | AC6 (quality extension) |
| D10.5 | Final release readiness decision record | AC completion evidence |

### Dependencies
- M1, M2, M3, M4, M5, M6, M7, M8

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Hidden gaps despite implementation progress | Medium | High | End-to-end AC matrix and benchmark evidence |

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-001 | Token budget underestimation | M3, M4, M5, M7, M10 | High | High | Dry-run estimates, degradation controls, benchmark calibration | performance |
| R-002 | Spec-implementation gap recurrence | M1, M10 | High | High | AC traceability enforcement before close | architect |
| R-003 | Schema malformation from Haiku outputs | M2, M8 | Medium | Medium | Schema validation + retry + FAILED handling | backend |
| R-004 | Dynamic import false positives | M5 | Medium | High | Dynamic import checks + KEEP:monitor default | backend |
| R-005 | Large-repo scaling limits | M3, M7, M10 | High | High | Monorepo segmentation + bounded degradation | architect |
| R-006 | Context-window pressure in synthesis/consolidation | M5, M6, M7 | High | High | Summary-first artifact reads + budget caveats | performance |
| R-007 | Credential value exposure | M2, M8, M10 | Low | High | Non-disclosure policy + output scrub checks | security |
| R-008 | Validation interpreted as accuracy | M6, M10 | Medium | Medium | Consistency-rate language + calibration notes | qa |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Primary Persona | backend | architect, security | Backend domain is dominant at 55% in extraction |
| Template | inline | local/user templates | No viable roadmap template discovered in project/user paths |
| Milestone Count | 10 | 8-12 (HIGH complexity range) | Complexity class HIGH with 5 detected domains and broad dependency spread |
| Adversarial Mode | multi-roadmap | none | `--multi-roadmap --agents opus,sonnet,haiku` requested |
| Adversarial Base Variant | sonnet:backend | opus:backend, haiku:backend | Highest combined score and strongest AC traceability coverage |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|---|---|---|---|
| SC-001 | Report includes core action sections | M1, M8 | Yes |
| SC-002 | Coverage artifact includes per-tier metrics | M1, M6 | Yes |
| SC-003 | Resume reliably recovers interrupted runs | M1, M8 | Yes |
| SC-004 | DELETE entries carry zero-reference evidence | M1 | Yes |
| SC-005 | Tier 1-2 KEEP includes reference evidence | M1, M4 | Yes |
| SC-006 | Validation sample meets >=10% threshold | M1, M6 | Yes |
| SC-007 | Credential scanning distinguishes real vs template | M2 | Yes |
| SC-008 | Gitignore inconsistency flagging works | M2 | Yes |
| SC-009 | Budget-limited run completes gracefully | M7 | Yes |
| SC-010 | Report-depth mode outputs conform to depth | M8 | Yes |
| SC-011 | Phase-1 outputs are schema-valid | M2 | Yes |
| SC-012 | Dependency graph emitted with valid nodes | M5 | Yes |
| SC-013 | Cold-start run succeeds without config | M3 | Yes |
| SC-014 | Broken-reference checklist generated | M5, M9 | Yes |
| SC-015 | v2-to-v1 category mapping holds | M1 | Yes |
| SC-016 | Large-directory assessments emitted | M6 | Yes |
| SC-017 | INVESTIGATE cap triggers re-analysis | M5 | Yes |
| SC-018 | Cascading failures produce minimum viable report | M2, M8 | Yes |
| SC-019 | Dry-run returns estimates only | M3 | Yes |
| SC-020 | Concurrent runs remain isolated | M3, M10 | Yes |
