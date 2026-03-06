---
spec_source: ".dev/releases/current/v2.13-CLIRunner-PipelineUnification/release-spec.md"
generated: "2026-03-05T00:00:00Z"
generator: sc:roadmap
functional_requirements: 10
nonfunctional_requirements: 4
total_requirements: 14
domains_detected: [backend, testing]
complexity_score: 0.367
complexity_class: LOW
risks_identified: 4
dependencies_identified: 3
success_criteria_count: 5
extraction_mode: standard
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  fallback_activated: false
---

# Extraction: v2.13 CLIRunner Pipeline Targeted Fixes

## Project Overview

- **Title**: v2.13 -- CLIRunner Pipeline Targeted Fixes
- **Version**: 2.13
- **Summary**: Implements Option 3 (Targeted Fixes) from adversarial-debated pipeline architecture decision. Eliminates process method duplication via lifecycle hooks, removes dead code, fixes file-passing in roadmap, and expands characterization test coverage for sprint executor.

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | Add optional lifecycle hook callbacks (on_spawn, on_signal, on_exit) to pipeline ClaudeProcess base class | backend | P0 | D1, L56-102 |
| FR-002 | Sprint ClaudeProcess removes start(), wait(), terminate() overrides and provides hook implementations via factory functions | backend | P0 | D1, L90-91 |
| FR-003 | Hook callbacks use primitive types only (int, str, bool, list) -- no process or config objects | backend | P0 | Section 9.3, L320-351 |
| FR-004 | Base class hooks fire before standard _log.debug calls; hooks are not wrapped in try/except | backend | P0 | Section 9.3 |
| FR-005 | Delete _build_subprocess_argv() and _FORBIDDEN_FLAGS from roadmap/executor.py (dead code) | backend | P0 | D2, L104-121 |
| FR-006 | Switch roadmap_run_step() to embed input file contents inline in the prompt instead of using --file flags | backend | P1 | D3, L123-140 |
| FR-007 | Add size guard: if total embedded content exceeds 100KB, fall back to --file flags with warning | backend | P1 | Section 9.8 |
| FR-008 | Write characterization tests for 6 untested sprint executor subsystems (watchdog, multi-phase, TUI resilience, diagnostics, tmux, monitor) | testing | P0 | D4, L142-182 |
| FR-009 | Add on_exit hook call to wait() success path (behavioral addition -- exit hook fires on all exit paths) | backend | P0 | Section 9.6, Edge Case 5 |
| FR-010 | Sprint hook factory for on_exit uses returncode == 124 as timeout indicator (drops _timed_out cross-reference) | backend | P0 | Section 9.6, Edge Case 3 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|-----------|--------|
| NFR-001 | All changes preserve existing CLI behavior -- no user-facing changes to sprint or roadmap commands | maintainability | Zero behavioral regression | Section 5.1 |
| NFR-002 | Pipeline module maintains zero imports from superclaude.cli.sprint or superclaude.cli.roadmap (NFR-007 compliance) | maintainability | grep -r returns 0 results | Section 5.2 |
| NFR-003 | No deliverable in M2 or M3 may merge until all D4 characterization tests pass before and after changes | reliability | Test gate enforced | Section 5.3 |
| NFR-004 | No new Python package dependencies introduced | maintainability | Zero new deps | Section 5.4 |

## Dependencies

| ID | Description | Type | Affected |
|----|-------------|------|----------|
| DEP-001 | M1 (characterization tests) must complete before M2 (targeted fixes) | internal | FR-001, FR-002, FR-005 |
| DEP-002 | M2c (dead code removal) should complete before M3 (file-passing fix) -- both modify roadmap/executor.py | internal | FR-005, FR-006 |
| DEP-003 | M2a (wait() deletion) has zero dependencies beyond M1 and can ship immediately | internal | FR-002 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | Lines removed (duplication) >= 58 net in sprint/process.py | FR-001, FR-002 | Yes -- git diff --stat |
| SC-002 | Lines removed (dead code) >= 25 in roadmap/executor.py | FR-005 | Yes -- git diff --stat |
| SC-003 | Sprint executor test coverage >= 70% (up from ~45%) | FR-008 | Yes -- pytest --cov |
| SC-004 | Regression count = 0 (full test suite green) | NFR-001 | Yes -- CI pass |
| SC-005 | NFR-007 violations = 0 | NFR-002 | Yes -- grep verification |

## Risk Register

| ID | Description | Probability | Impact | Affected |
|----|-------------|------------|--------|----------|
| RISK-001 | Logging hook refactor breaks SIGTERM/SIGKILL escalation path | Low | High | FR-001, FR-002 |
| RISK-002 | Dead code removal breaks an untested code path | Very Low | Medium | FR-005 |
| RISK-003 | File-passing change alters roadmap output format | Low | Medium | FR-006 |
| RISK-004 | Characterization tests incomplete, miss a subsystem | Medium | Medium | FR-008 |

## Domain Distribution

| Domain | Percentage | Rationale |
|--------|-----------|-----------|
| backend | 90% | All code changes in pipeline/process.py, sprint/process.py, roadmap/executor.py |
| testing | 10% | D4 characterization tests |
