---
spec_source: ".dev/releases/backlog/v2.14-SprintReportScaffolding/release-spec.md"
generated: "2026-03-06"
generator: "sc:roadmap"
extraction_mode: "standard (544 lines)"
project_title: "v2.14 — Sprint Report Scaffolding"
project_version: "2.14"
functional_requirements: 13
nonfunctional_requirements: 5
total_requirements: 18
domains_detected: [backend, testing]
complexity_score: 0.396
complexity_class: LOW
risks_identified: 6
dependencies_identified: 4
success_criteria_count: 5
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  fallback_activated: false
  extraction_passes:
    source_coverage: "100%"
    anti_hallucination: "PASS"
    section_coverage: "100%"
    count_reconciliation: "PASS"
---

# Extraction Report: v2.14 Sprint Report Scaffolding

## Overview

When sprint phases hit the `max_turns` limit, the Claude agent never writes the `phase-N-result.md` file because report writing is the last action in the Completion Protocol. This caused 3 of 5 phases in a recent sprint to finish as `pass_no_report`.

v2.14 adds a two-layer defense: (1) deterministic Python scaffold created before agent launch, (2) prompt instructs incremental scaffold updates. No changes to status classification logic.

## Functional Requirements

| ID | Description | Priority | Domain | Source |
|----|-------------|----------|--------|--------|
| FR-001 | Parse task metadata (ID, title, tier) from phase tasklist files via `parse_phase_tasks()` | P0 | backend | L71-130 |
| FR-002 | Create scaffold result file with YAML frontmatter (`phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0`) before agent launch | P0 | backend | L131-182 |
| FR-003 | Scaffold YAML frontmatter must NOT contain a `status:` field | P0 | backend | L185 |
| FR-004 | Scaffold must NOT contain the string `EXIT_RECOMMENDATION` anywhere | P0 | backend | L186 |
| FR-005 | Untouched scaffold must map to `PASS_NO_SIGNAL` via `_determine_phase_status()` | P0 | backend | L219-229 |
| FR-006 | Call `scaffold_result_file()` in `execute_sprint()` between `ClaudeProcess` construction and `proc_manager.start()` | P0 | backend | L256-283 |
| FR-007 | Scaffold creation failure must not prevent sprint execution (graceful degradation) | P0 | backend | L231-235 |
| FR-008 | Scaffold failures logged to both `debug_log` (JSONL) and `stderr` (operator visibility) | P0 | backend | L232-233 |
| FR-009 | Replace "Completion Protocol" section with "Reporting Protocol" in `build_prompt()` | P0 | backend | L300-342 |
| FR-010 | Prompt instructs incremental scaffold updates as best-effort ("you may") | P0 | backend | L329-331, L345 |
| FR-011 | Prompt instructs mandatory final status + EXIT_RECOMMENDATION ("you MUST") | P0 | backend | L334-341, L347 |
| FR-012 | Create parent directories for scaffold if they don't exist | P1 | backend | L244 |
| FR-013 | Scaffold overwrites existing file at the same path | P1 | backend | L245 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Backward compatibility — preserve existing CLI behavior | maintainability | Fallback to `PASS_NO_REPORT` on scaffold failure | L472-473 |
| NFR-002 | No status classification changes | maintainability | `_determine_phase_status()` and `PhaseStatus` enum unchanged | L475-476 |
| NFR-003 | v2.13 test gate | reliability | Characterization tests must pass before and after scaffold changes | L478-479 |
| NFR-004 | No new Python dependencies | maintainability | Zero new packages introduced | L481-482 |
| NFR-005 | Graceful degradation | reliability | Scaffold failure logged to debug log + stderr; sprint continues | L484-485 |

## Dependencies

| ID | Description | Type | Affects | Source |
|----|-------------|------|---------|--------|
| DEP-001 | v2.13 M1 (characterization tests) must complete before v2.14 | external | All FRs | L18, L62-67, L478 |
| DEP-002 | scaffold.py (M1) must exist before executor integration (M2) | internal | FR-006, FR-007, FR-008 | L446-447 |
| DEP-003 | M1 + M2 must complete before tests (M3) | internal | D5 (tests) | L449-452 |
| DEP-004 | Scaffold format must be a subset of the final report format | design constraint | FR-002, FR-009 | L188, L246 |

## Success Criteria

| ID | Description | Target | Measurement | Source |
|----|-------------|--------|-------------|--------|
| SC-001 | Scaffold file exists after max_turns | 100% of phases | Re-run sprint, verify all phases have result files | L530 |
| SC-002 | No `PASS_NO_REPORT` status in new runs | 0 occurrences | `grep pass_no_report execution-log.jsonl` | L531 |
| SC-003 | All existing sprint tests pass | 100% | `uv run pytest tests/sprint/ -v` | L532 |
| SC-004 | Full project test suite passes | 100% | `uv run pytest tests/ -v` | L533 |
| SC-005 | New test count | >= 17 | Count tests in test_scaffold.py + new tests in test_process.py | L534 |

## Risk Register

| ID | Risk | Probability | Impact | Mitigation | Source |
|----|------|-------------|--------|------------|--------|
| RISK-001 | Agent ignores incremental update instructions | Medium | Low | Layer 1 scaffold provides guaranteed safety net | L507 |
| RISK-002 | Agent overwrites scaffold with incompatible format | Very Low | Low | Any valid report triggers correct status classification | L508 |
| RISK-003 | Task heading regex doesn't match future tasklist formats | Low | Medium | Regex validated against real fixtures; parser returns [] gracefully | L509 |
| RISK-004 | Scaffold creation fails (disk, permissions) | Very Low | Low | Graceful degradation to current behavior | L510 |
| RISK-005 | Merge conflict with v2.13 on sprint/process.py | Low | Low | v2.14 sequenced AFTER v2.13; different code locations | L511 |
| RISK-006 | v2.13 characterization tests need updating for scaffold | Medium | Low | M3 includes full regression verification | L512 |

## Domain Analysis

| Domain | Percentage | Key Indicators |
|--------|------------|----------------|
| Backend | 85% | Python module design, file I/O, subprocess integration, YAML/regex parsing, executor orchestration |
| Testing | 15% | 17+ unit tests, integration tests, fixture-based testing, status classification verification |

## Files Impact

| File | Change Type | Description |
|------|------------|-------------|
| `src/superclaude/cli/sprint/scaffold.py` | NEW | `TaskMeta`, `parse_phase_tasks()`, `scaffold_result_file()`, `SCAFFOLD_TEMPLATE` |
| `src/superclaude/cli/sprint/executor.py` | MODIFIED | Add scaffold call between ClaudeProcess construction and start() |
| `src/superclaude/cli/sprint/process.py` | MODIFIED | Replace "Completion Protocol" with "Reporting Protocol" in `build_prompt()` |
| `tests/sprint/test_scaffold.py` | NEW | Parser, scaffold, status classification, primary scenario tests |
| `tests/sprint/test_process.py` | MODIFIED | 3 prompt content tests added |
