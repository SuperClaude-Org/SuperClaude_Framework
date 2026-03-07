---
spec_source: ".dev/releases/current/unified-audit-gating-v2/unified-audit-gating-v2.0-spec.md"
generated: "2026-03-06T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.421
complexity_class: MEDIUM
domain_distribution:
  frontend: 0
  backend: 60
  security: 5
  performance: 15
  documentation: 20
primary_persona: backend
consulting_personas: [architect, scribe]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Foundation & Source Defaults"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 7
    risk_level: Medium
    effort: M
  - id: M2
    title: "Shell & CLI Alignment"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Medium
    effort: S
  - id: V1
    title: "Validation: Source Integrity"
    type: TEST
    priority: P3
    dependencies: [M1, M2]
    deliverable_count: 3
    risk_level: Low
    effort: S
  - id: M3
    title: "Test Suite Updates"
    type: TEST
    priority: P1
    dependencies: [V1]
    deliverable_count: 10
    risk_level: Low
    effort: M
  - id: M4
    title: "Documentation & Spec Alignment"
    type: DOC
    priority: P2
    dependencies: [M3]
    deliverable_count: 4
    risk_level: Low
    effort: S
  - id: V2
    title: "Validation: End-to-End"
    type: TEST
    priority: P3
    dependencies: [M3, M4]
    deliverable_count: 4
    risk_level: Low
    effort: S
total_deliverables: 33
total_risks: 9
estimated_phases: 6
validation_score: 0.9198
validation_status: PASS
---

# Roadmap: unified-audit-gating v2.0

## Overview

This roadmap plans the execution of a **configuration change release** that corrects two sprint pipeline defaults (`max_turns`: 50→100, `reimbursement_rate`: 0.5→0.8) to resolve budget exhaustion and phase execution headroom issues. The release involves 12 source edits across Python and shell files, 4 test assertion updates, 6 new tests, and spec documentation alignment.

The approach is structured in 4 work milestones plus 2 interleaved validation milestones (1:2 ratio per MEDIUM complexity classification). Execution follows a tiered edit strategy: Python source defaults first (Tier 1), then shell/CLI alignment (Tier 1.5), then test suite updates, and finally documentation. This ordering ensures each tier validates against the previous one.

Compliance tier: **STRICT** (user-specified). All changes require validation before proceeding.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Source Defaults | FEATURE | P0 | M | None | 7 | Medium |
| M2 | Shell & CLI Alignment | FEATURE | P0 | S | M1 | 5 | Medium |
| V1 | Validation: Source Integrity | TEST | P3 | S | M1, M2 | 3 | Low |
| M3 | Test Suite Updates | TEST | P1 | M | V1 | 10 | Low |
| M4 | Documentation & Spec Alignment | DOC | P2 | S | M3 | 4 | Low |
| V2 | Validation: End-to-End | TEST | P3 | S | M3, M4 | 4 | Low |

## Dependency Graph

```
M1 → M2 → V1 → M3 → M4 → V2
M1 ──────→ V1
M3 ──────────────→ V2
```

All milestones form a DAG with no circular dependencies. Critical path: M1 → M2 → V1 → M3 → M4 → V2.

---

## M1: Foundation & Source Defaults

### Objective

Apply all 7 Tier 1 Python source default changes to establish the new `max_turns=100` and `reimbursement_rate=0.8` baseline across pipeline and sprint configuration layers.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `PipelineConfig.max_turns` default → 100 | `pipeline/models.py:175` reads `max_turns: int = 100` |
| D1.2 | `SprintConfig.max_turns` default → 100 | `sprint/models.py:285` reads `max_turns: int = 100` |
| D1.3 | CLI `--max-turns` default → 100 | `sprint/commands.py:54` reads `default=100` |
| D1.4 | CLI `--max-turns` help text → "default: 100" | `sprint/commands.py:55` help string updated |
| D1.5 | `load_sprint_config(max_turns)` default → 100 | `sprint/config.py:108` reads `max_turns: int = 100` |
| D1.6 | `ClaudeProcess.__init__(max_turns)` default → 100 | `pipeline/process.py:43` reads `max_turns: int = 100` |
| D1.7 | `TurnLedger.reimbursement_rate` default → 0.8 | `sprint/models.py:476` reads `reimbursement_rate: float = 0.8` |

### Dependencies

- None (foundation milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DRY violation across 5 max_turns locations | Medium | Medium | Apply all 6 max_turns changes atomically; verify with grep |
| Existing sprints silently get new behavior | Medium | Medium | CHANGELOG entry mandatory in M4; explicit overrides preserved per NFR-006 |

---

## M2: Shell & CLI Alignment

### Objective

Apply the 5 panel-identified edits (Tier 1.5) in shell scripts and roadmap CLI to eliminate configuration drift between Python defaults and external entry points.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `execute-sprint.sh` `MAX_TURNS=100` | `.dev/releases/execute-sprint.sh:47` reads `MAX_TURNS=100` |
| D2.2 | `execute-sprint.sh` help text → "default: 100" | `.dev/releases/execute-sprint.sh:14` updated |
| D2.3 | `rerun-incomplete-phases.sh` comment → "max_turns (100)" | `scripts/rerun-incomplete-phases.sh:4` updated |
| D2.4 | Roadmap CLI `--max-turns` default → 100 | `roadmap/commands.py:75` reads `default=100` |
| D2.5 | Roadmap CLI help text → "Default: 100" | `roadmap/commands.py:76` updated |

### Dependencies

- M1: Python source defaults must be in place before aligning shell/CLI entry points

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shell scripts use hardcoded values (hidden coupling) | High | High | Panel identified these; edit list is comprehensive |
| Additional undiscovered hardcoded locations | Low | Medium | Grep for `50` in context of `max_turns`/`MAX_TURNS` during V1 |

---

## V1: Validation — Source Integrity

### Objective

Verify all 12 source edits are correctly applied, no residual old values remain, and the configuration is internally consistent before proceeding to test updates.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D-V1.1 | Grep verification: no remaining `max_turns.*50` defaults | Zero matches in source files (excluding explicit test fixtures) |
| D-V1.2 | Grep verification: no remaining `reimbursement_rate.*0.5` defaults | Zero matches in source files (excluding explicit test fixtures) |
| D-V1.3 | Cross-reference check: all 12 FRs verified against file:line targets | Each FR's target file and line contains the expected value |

### Dependencies

- M1: All Python source defaults applied
- M2: All shell/CLI defaults applied

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False positives from grep (matches in comments/docs) | Low | Low | Context-aware grep excluding test fixtures |

---

## M3: Test Suite Updates

### Objective

Update 4 existing test assertions and add 6 new tests covering budget decay, sprint sustainability, boundary conditions, and backward compatibility at the new default values.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Update `test_models.py:54` assertion → `== 100` | Test passes |
| D3.2 | Update `test_models.py:188` assertion → `== 100` | Test passes |
| D3.3 | Update `test_config.py:215` assertion → `== 100` | Test passes |
| D3.4 | Update `test_models.py:527` assertion → `== 0.8` | Test passes |
| D3.5 | New: `test_budget_decay_rate_08` (unit) | Verifies net cost = 4 at rate=0.8, actual=8 |
| D3.6 | New: `test_max_sustainable_tasks_at_08` (unit) | Verifies exhaustion at ~50 tasks with budget=200 |
| D3.7 | New: `test_46_task_sprint_sustainability` (integration) | 46-task loop completes with budget > 0 |
| D3.8 | New: `test_budget_exhaustion_property` (property-based) | Random tasks/turns always reach budget=0 |
| D3.9 | New: `test_explicit_max_turns_override` (regression) | `--max-turns=50` overrides new default |
| D3.10 | New: `test_rate_boundary_validation` (boundary) | rate=0.0, 0.99, 1.0(rejected), -0.1(rejected) |

### Dependencies

- V1: Source integrity validated before updating tests

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Property-based test flakiness | Low | Low | Use deterministic seed; bound hypothesis space |
| Boundary test reveals missing validation | Medium | Medium | RISK-009 mitigation: verify SC-001 enforcement |

---

## M4: Documentation & Spec Alignment

### Objective

Write the mandatory CHANGELOG entry with migration guide, update spec prose to reflect 0.8 (Tier 4 edits), and add budget guidance per panel recommendation.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | CHANGELOG entry for v2.0.0 with migration guide | Entry matches spec §11 template |
| D4.2 | Update `unified-spec-v1.0.md` §3.1 → `rate = 0.80` | Line 178 corrected |
| D4.3 | Update `unified-spec-v1.0.md` §3.4 proof → rate=0.80 math | Lines 225-235 corrected with 4 turns/task, 184 drain |
| D4.4 | Add budget guidance note for >40 task sprints | `initial_budget ≥ 250` recommendation documented |

### Dependencies

- M3: Test suite passing confirms code is correct before documenting it

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Spec-implementation drift recurrence | Medium | Low | This milestone directly addresses it |
| Phase timeout implications not documented | Low | Low | Include in CHANGELOG per Hightower recommendation |

---

## V2: Validation — End-to-End

### Objective

Run the complete test suite, verify backward compatibility, and confirm the 46-task sprint sustainability claim before release.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D-V2.1 | Full test suite passes (existing + new) | Zero failures |
| D-V2.2 | 46-task sprint integration test passes | Budget remaining > 0 |
| D-V2.3 | Explicit override regression passes | `--max-turns=50` preserved |
| D-V2.4 | Tier 3 (no-change) tests still pass | No regressions in explicit-fixture tests |

### Dependencies

- M3: Test updates complete
- M4: Documentation complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration test reveals tight margin failure | Low | Medium | Document budget guidance; consider initial_budget increase |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | 16-turn margin tight for 46-task sprints | M3, V2 | Medium | Medium | Recommend `initial_budget ≥ 250` for >40 tasks | backend |
| R-002 | Phase timeout at 3.4h may surprise users | M4 | Low | Low | Document in CHANGELOG and release notes | scribe |
| R-003 | Shell scripts have hardcoded MAX_TURNS | M2, V1 | High | High | FR-008–FR-010 cover all known locations | backend |
| R-004 | Existing sprints silently get new behavior | M4 | Medium | Medium | CHANGELOG with migration guide mandatory | scribe |
| R-005 | Spec-implementation drift recurrence | M4 | Medium | Low | Tier 4 edits align spec to implementation | scribe |
| R-006 | No environment variable override path | — | Low | Low | Accept for v2.0; consider env var support in v2.1 | architect |
| R-007 | 9-phase sprint could run 30+ hours | M4 | Low | Low | Document timeout implications | scribe |
| R-008 | DRY violation in 5-location defaults | — | Medium | Medium | Follow-up issue for constant consolidation | architect |
| R-009 | rate=1.0 boundary not enforced strictly | M3 | Low | High | Verify SC-001 enforcement in boundary test | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | architect (0.455), scribe (0.140) | Backend domain at 60% — highest weighted confidence (0.504) |
| Template | inline | No templates found in Tiers 1-3 | Tier 4 fallback — inline generation from extraction data |
| Milestone Count | 6 | Range 5-7 (MEDIUM class) | base(5) + floor(3 domains / 2) = 6 |
| Adversarial Mode | none | N/A | No --specs or --multi-roadmap flags |
| Adversarial Base Variant | N/A | N/A | No adversarial mode active |
| Compliance Tier | STRICT | standard, light | User-specified --compliance strict |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | All 12 source edits applied and verified | M1, M2, V1 | Yes |
| SC-002 | All 4 existing test assertions updated and passing | M3 | Yes |
| SC-003 | 6 new tests written and passing | M3 | Yes |
| SC-004 | 46-task sprint completes with budget >0 at rate=0.8 | V2 | Yes |
| SC-005 | Explicit `--max-turns=50` override preserves old behavior | V2 | Yes |
| SC-006 | CHANGELOG entry written with migration guide | M4 | Yes |
| SC-007 | Spec prose updated to reflect 0.8 | M4 | Yes |

---

*Generated by sc:roadmap v2.0.0 — MEDIUM complexity, inline template, STRICT compliance*
