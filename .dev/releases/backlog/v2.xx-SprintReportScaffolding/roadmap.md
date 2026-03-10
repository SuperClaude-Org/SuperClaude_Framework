---
spec_source: ".dev/releases/backlog/v2.14-SprintReportScaffolding/release-spec.md"
generated: "2026-03-06"
generator: "sc:roadmap"
complexity_score: 0.396
complexity_class: LOW
domain_distribution:
  backend: 85
  testing: 15
primary_persona: backend
consulting_personas: [qa, refactorer]
milestone_count: 3
milestone_index:
  - id: M1
    title: "Parser and Scaffold Module"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    effort: S
    risk_level: Low
  - id: M2
    title: "Executor Integration and Prompt Update"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    effort: S
    risk_level: Low
  - id: M3
    title: "Tests and Validation"
    type: TEST
    priority: P1
    dependencies: [M1, M2]
    deliverable_count: 4
    effort: S
    risk_level: Medium
total_deliverables: 12
total_risks: 6
estimated_phases: 3
validation_score: 0.0
validation_status: SKIPPED
---

# Roadmap: v2.14 Sprint Report Scaffolding

## Overview

This roadmap addresses the lost-report problem in sprint execution. When Claude agents hit the `max_turns` limit, report writing is the first casualty because the Completion Protocol places it as the final action. Evidence from the `cleanup-audit-v2-UNIFIED-SPEC` sprint shows 3 of 5 phases finished as `pass_no_report`.

The approach is a two-layer defense: Layer 1 creates a deterministic scaffold result file via Python code before the agent launches (guaranteed), and Layer 2 updates the prompt to instruct incremental scaffold updates (best-effort). The design deliberately avoids modifying `_determine_phase_status()`, `PhaseStatus`, or any status classification logic — the scaffold naturally maps to the existing `PASS_NO_SIGNAL` status.

All work is sequenced after v2.13 M1 (characterization tests) to ensure a safety net exists before any sprint module modifications land.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Parser and Scaffold Module | FEATURE | P0 | S | v2.13 M1 (external) | 4 | Low |
| M2 | Executor Integration and Prompt Update | FEATURE | P0 | S | M1 | 4 | Low |
| M3 | Tests and Validation | TEST | P1 | S | M1, M2 | 4 | Medium |

## Dependency Graph

```
v2.13 M1 (characterization tests — external prerequisite)
    |
    v
M1 (Parser + Scaffold Module)
    |
    v
M2 (Executor Integration + Prompt Update)
    |
    v
M3 (Tests + Validation)
```

Linear dependency chain. No parallel milestones. Each milestone produces artifacts consumed by the next.

---

## M1: Parser and Scaffold Module

### Objective

Create a self-contained `scaffold.py` module that can parse task metadata from phase tasklist files and generate scaffold result files. This module has zero dependencies on executor, process, or monitor code.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `TaskMeta` dataclass in `scaffold.py` | Fields: `id: str`, `title: str`, `tier: str`. Tier defaults to `"UNKNOWN"`. |
| D1.2 | `parse_phase_tasks()` function | Extracts task ID, title, tier from `### T01.01 -- Title` headings and `\| Tier \| STRICT \|` metadata rows. Returns `[]` on missing file, empty file, or no matching headings. Handles all four tiers: STRICT, STANDARD, LIGHT, EXEMPT. |
| D1.3 | `SCAFFOLD_TEMPLATE` constant | Template string with YAML frontmatter (`phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0`). No `status:` field. No `EXIT_RECOMMENDATION` string. |
| D1.4 | `scaffold_result_file()` function | Creates scaffold at specified path. Creates parent dirs. Overwrites existing files. All input tasks appear in markdown table with `pending` status. |

### Dependencies

- **v2.13 M1** (external): Characterization tests must be in place before any sprint module modifications. This is a hard gate.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Task heading regex doesn't match future tasklist formats | Low | Medium | Validate regex against real tasklist fixture (AC-5). Parser returns `[]` gracefully on no match. |
| Phase file encoding issues with non-ASCII task titles | Very Low | Low | Use `errors="replace"` when reading, `encoding="utf-8"` when writing. |

---

## M2: Executor Integration and Prompt Update

### Objective

Wire the scaffold module into the sprint execution pipeline at the correct lifecycle point and update the agent prompt to reference the scaffold.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Scaffold call in `execute_sprint()` | Call site between `ClaudeProcess(config, phase)` construction and `proc_manager.start()`. Scaffold file exists at `config.result_file(phase)` before agent launches. |
| D2.2 | Graceful degradation on scaffold failure | Scaffold creation wrapped in try/except. Failure logged to both `debug_log` (JSONL) and `stderr`. Sprint continues without scaffold — falls back to current `PASS_NO_REPORT` behavior. |
| D2.3 | Replace "Completion Protocol" with "Reporting Protocol" | `build_prompt()` output contains "scaffold report already exists", "you MUST finalize", "EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT". Does NOT contain "Completion Protocol". |
| D2.4 | Prompt references correct result file path | Prompt contains the exact path returned by `config.result_file(phase)`. |

### Dependencies

- **M1**: `scaffold.py` module must exist (provides `parse_phase_tasks` and `scaffold_result_file`).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Merge conflict with v2.13 on executor.py | Low | Low | v2.14 sequenced after v2.13. Scaffold call site and v2.13 changes are at different code locations. |
| Merge conflict with v2.13 on process.py | Low | Low | v2.13 doesn't modify `build_prompt()`. Different code sections. |
| Agent ignores incremental update instructions | Medium | Low | Layer 1 scaffold is deterministic Python — zero reliance on agent behavior. |

---

## M3: Tests and Validation

### Objective

Comprehensive test coverage for the scaffold lifecycle: parsing, creation, status classification, executor integration, and prompt content. Regression verification against the full sprint test suite.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `TestParsePhaseTasks` class (5 tests) | Covers: ID/title/tier extraction, missing tier defaults, missing file, empty file, real tasklist fixture. |
| D3.2 | `TestScaffoldResultFile` class (7 tests) | Covers: file creation, YAML frontmatter correctness, no `status:` field, no `EXIT_RECOMMENDATION`, task table, parent dir creation, overwrite, empty tasks. |
| D3.3 | `TestScaffoldStatusClassification` class (5 tests) + `TestScaffoldPrimaryScenario` (1 test) | Covers: untouched scaffold → `PASS_NO_SIGNAL`, partial update → `PASS_NO_SIGNAL`, full completion → `PASS`, halt signal → `HALT`, overwrite → normal classification. Primary scenario: 10 tasks, 6 pass, 4 pending, max_turns → `PASS_NO_SIGNAL`. |
| D3.4 | Prompt content tests in `test_process.py` (3 tests) + full regression | Covers: "scaffold report already exists", "you MUST finalize", no "Completion Protocol". Full suite: `uv run pytest tests/sprint/ -v` and `uv run pytest tests/ -v` both pass. |

### Dependencies

- **M1**: Test targets (`parse_phase_tasks`, `scaffold_result_file`) must exist.
- **M2**: Integration targets (executor scaffold call, prompt content) must exist.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| v2.13 characterization tests need updating for scaffold | Medium | Low | Run full sprint test suite before and after changes. Update any broken characterization tests. |
| Agent overwrites scaffold with incompatible format | Very Low | Low | Test `test_scaffold_overwritten_entirely` validates this path explicitly. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Agent ignores incremental update instructions | M2 | Medium | Low | Layer 1 scaffold provides guaranteed safety net regardless of agent behavior | backend |
| R-002 | Agent overwrites scaffold with incompatible format | M2, M3 | Very Low | Low | Any valid report triggers correct status classification via `_determine_phase_status()` | backend |
| R-003 | Task heading regex doesn't match future tasklist formats | M1 | Low | Medium | Regex validated against real tasklist fixtures; parser returns `[]` gracefully | backend |
| R-004 | Scaffold creation fails (disk, permissions) | M2 | Very Low | Low | Graceful degradation to current `PASS_NO_REPORT` behavior; logged to stderr | backend |
| R-005 | Merge conflict with v2.13 on sprint/ files | M2 | Low | Low | v2.14 sequenced after v2.13; different code locations in shared files | backend |
| R-006 | v2.13 characterization tests need updating for scaffold | M3 | Medium | Low | M3 includes full regression verification against entire sprint test suite | qa |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | architect (0.21), qa (0.11) | 85% backend domain distribution → backend persona confidence 0.655 |
| Template | inline | No project templates found (Tiers 1-3 empty) | Inline generation from extraction data |
| Milestone Count | 3 | 4 (algorithm base=3 + floor(2/2)=4) | Spec defines 3 natural milestones matching deliverable boundaries; 3 is within LOW range (3-4) |
| Adversarial Mode | none | N/A | Single spec, no --multi-roadmap or --specs flags |
| Module Placement | Dedicated `scaffold.py` | Adding to `executor.py` or `config.py` | Separation of concerns: parsing markdown and creating templates is a different concern from subprocess orchestration or config loading |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Scaffold file exists after max_turns for 100% of phases | M1, M2 | Re-run sprint, verify all phases have result files |
| SC-002 | Zero `PASS_NO_REPORT` occurrences in new sprint runs | M1, M2 | `grep pass_no_report execution-log.jsonl` returns 0 |
| SC-003 | All existing sprint tests pass | M3 | `uv run pytest tests/sprint/ -v` exits 0 |
| SC-004 | Full project test suite passes | M3 | `uv run pytest tests/ -v` exits 0 |
| SC-005 | New test count >= 17 | M3 | Count tests in `test_scaffold.py` + new tests in `test_process.py` |
