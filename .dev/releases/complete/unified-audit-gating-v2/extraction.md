---
spec_source: ".dev/releases/current/unified-audit-gating-v2/unified-audit-gating-v2.0-spec.md"
generated: "2026-03-06T00:00:00Z"
generator: sc:roadmap
functional_requirements: 12
nonfunctional_requirements: 8
total_requirements: 20
domains_detected: [backend, documentation, performance]
complexity_score: 0.421
complexity_class: MEDIUM
risks_identified: 9
dependencies_identified: 3
success_criteria_count: 7
extraction_mode: standard
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  fallback_activated: false
---

# Extraction: unified-audit-gating v2.0

## Overview

**Project**: unified-audit-gating v2.0
**Version**: 2.0
**Summary**: Configuration change release that corrects two default values (`max_turns`: 50→100, `reimbursement_rate`: 0.5→0.8) across 12 source locations and 4 test assertions to fix budget exhaustion and phase execution headroom issues in the sprint pipeline.

**Classification**: Panel-reviewed configuration change release (no structural changes, no new files, no logic changes).

---

## Functional Requirements

| ID | Description | Priority | Domain | Source |
|----|------------|----------|--------|--------|
| FR-001 | Default `PipelineConfig.max_turns` SHALL be 100 | P0 | backend | L47 |
| FR-002 | Default `SprintConfig.max_turns` SHALL be 100 | P0 | backend | L48 |
| FR-003 | CLI `--max-turns` option SHALL default to 100 | P0 | backend | L49 |
| FR-004 | CLI `--max-turns` help text SHALL read "default: 100" | P1 | documentation | L50 |
| FR-005 | Default `load_sprint_config(max_turns)` SHALL be 100 | P0 | backend | L51 |
| FR-006 | Default `ClaudeProcess.__init__(max_turns)` SHALL be 100 | P0 | backend | L52 |
| FR-007 | Default `TurnLedger.reimbursement_rate` SHALL be 0.8 | P0 | backend | L53 |
| FR-008 | `execute-sprint.sh` SHALL set `MAX_TURNS=100` | P0 | backend | L54 |
| FR-009 | `execute-sprint.sh` help text SHALL reference "default: 100" | P1 | documentation | L55 |
| FR-010 | `rerun-incomplete-phases.sh` comment SHALL reference "max_turns (100)" | P1 | documentation | L56 |
| FR-011 | Roadmap CLI `--max-turns` option SHALL default to 100 | P0 | backend | L57 |
| FR-012 | Roadmap CLI `--max-turns` help text SHALL read "Default: 100" | P1 | documentation | L58 |

**Summary**: 12 FRs — 8 P0 (must-have), 4 P1 (should-have)

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|------------|----------|-----------|--------|
| NFR-001 | Budget decay: net cost ≥ 4 turns at rate=0.8, actual=8, overhead=2 | reliability | Unit test verification | L68 |
| NFR-002 | No infinite run: geometric series Σ(rate^n) converges for rate < 1.0 | reliability | Mathematical proof | L69 |
| NFR-003 | 46-task sprint sustainability at rate=0.8, budget=200 | reliability | Integration test verification | L70 |
| NFR-004 | Phase timeout at max_turns=100: 12,300s (3.4 hours) | performance | Unit test verification | L71 |
| NFR-005 | Sprint timeout bound: 9-phase sprint ≤ 30.75 hours | performance | Documentation acknowledgment | L72 |
| NFR-006 | Backward compatibility: explicit overrides preserved | maintainability | Regression test | L73 |
| NFR-007 | Gate evaluation performance: <50ms for ≤100KB output | performance | Existing test (no change) | L74 |
| NFR-008 | Budget monotonic decay: available() non-increasing | reliability | Property-based test | L75 |

**Summary**: 8 NFRs — reliability(4), performance(3), maintainability(1)

---

## Domain Distribution

| Domain | Requirements | Percentage | ≥10% Threshold |
|--------|-------------|------------|----------------|
| backend | 13 | 60% | Yes |
| documentation | 4 | 20% | Yes |
| performance | 3 | 15% | Yes |
| security | 0 | 5% | No |

**Domains with ≥10% representation**: 3 (backend, documentation, performance)

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|------------|------|----------------------|
| DEP-001 | Test assertion edits (Tier 2) depend on source edits (Tier 1/1.5) | internal | FR-001–FR-012 → test edits |
| DEP-002 | Spec documentation edits (Tier 4) depend on source edits completing | internal | FR-001–FR-012 → spec prose |
| DEP-003 | New tests (6 recommended) require source changes in place | internal | FR-001–FR-012 → new tests |

**Dependency depth**: 2 (Tier 1 → Tier 2 → Tier 4)

---

## Success Criteria

| ID | Description | Validates | Measurable |
|----|------------|-----------|-----------|
| SC-001 | All 12 source edits applied and verified | FR-001–FR-012 | Yes |
| SC-002 | All 4 existing test assertions updated and passing | Tier 2 edits | Yes |
| SC-003 | 6 new tests written and passing | NFR-001,003,006,008 | Yes |
| SC-004 | 46-task sprint completes with budget >0 at rate=0.8 | NFR-003 | Yes |
| SC-005 | Explicit `--max-turns=50` override preserves old behavior | NFR-006 | Yes |
| SC-006 | CHANGELOG entry written with migration guide | Documentation | Yes |
| SC-007 | Spec prose (unified-spec-v1.0.md) updated to reflect 0.8 | RISK-005 | Yes |

---

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|------------|-------------|--------|----------------------|--------|
| RISK-001 | 16-turn margin at rate=0.8 tight for 46-task sprints | Medium | Medium | NFR-003 | L220 |
| RISK-002 | Phase timeout at 3.4h may surprise users | Low | Low | NFR-004, NFR-005 | L221 |
| RISK-003 | Shell scripts have hardcoded MAX_TURNS (missed by initial analysis) | High | High | FR-008, FR-009, FR-010 | L222 |
| RISK-004 | Existing sprints silently get new behavior with defaults | Medium | Medium | NFR-006 | L223 |
| RISK-005 | Spec-implementation drift recurrence | Medium | Low | All FRs | L224 |
| RISK-006 | No environment variable override path exists | Low | Low | NFR-006 | L225 |
| RISK-007 | 9-phase sprint at max_turns=100 could run 30+ hours | Low | Low | NFR-005 | L226 |
| RISK-008 | DRY violation in 5-location defaults may cause future drift | Medium | Medium | FR-001–FR-006 | inferred (Fowler) |
| RISK-009 | rate=1.0 boundary not enforced strictly (sentinel collision) | Low | High | NFR-002, NFR-008 | L286 (Whittaker) |

**Risk Summary**: 2 High-impact, 4 Medium-impact, 3 Low-impact. Weighted avg: (2×3 + 4×2 + 3×1) / 9 = 1.89

---

## Complexity Analysis

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 20 | 0.40 | 0.25 | 0.100 |
| dependency_depth | 2 | 0.25 | 0.25 | 0.063 |
| domain_spread | 3 | 0.60 | 0.20 | 0.120 |
| risk_severity | 1.89 | 0.44 | 0.15 | 0.067 |
| scope_size | 472 | 0.47 | 0.15 | 0.071 |
| **Total** | | | **1.00** | **0.421** |

**Classification**: MEDIUM (0.4 ≤ 0.421 ≤ 0.7)
**Milestone range**: 5-7
**Interleave ratio**: 1:2

---

## Persona Selection

| Persona | Domain Weight | Coverage Bonus | Confidence |
|---------|-------------|----------------|-----------|
| **backend** (Primary) | 0.60 | 1.2 (perf secondary) | **0.504** |
| architect (Consulting) | generalist | 1.3 | 0.455 |
| scribe (Consulting) | 0.20 | 1.0 | 0.140 |

**Primary persona**: backend (confidence 0.504)
**Consulting personas**: architect, scribe

---

*Extracted by sc:roadmap v2.0.0 — standard extraction mode*
