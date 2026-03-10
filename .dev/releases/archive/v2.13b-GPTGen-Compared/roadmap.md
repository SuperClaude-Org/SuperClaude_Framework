---
spec_source: ".dev/releases/current/v2.13-CLIRunner-PipelineUnification/release-spec.md"
generated: "2026-03-05T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.367
complexity_class: LOW
domain_distribution:
  backend: 90
  testing: 10
primary_persona: refactorer
consulting_personas: [architect, qa]
milestone_count: 4
milestone_index:
  - id: M1
    title: "Sprint Executor Characterization Tests"
    type: TEST
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Medium
  - id: M2
    title: "Process Duplication Elimination"
    type: IMPROVEMENT
    priority: P0
    dependencies: [M1]
    deliverable_count: 7
    risk_level: Medium
  - id: M3
    title: "Roadmap File-Passing Fix"
    type: IMPROVEMENT
    priority: P1
    dependencies: [M2]
    deliverable_count: 3
    risk_level: Low
  - id: M4
    title: "Validation and Acceptance"
    type: TEST
    priority: P1
    dependencies: [M1, M2, M3]
    deliverable_count: 6
    risk_level: Low
total_deliverables: 20
total_risks: 5
estimated_phases: 4
validation_score: 0.9324
validation_status: PASS
---

# Roadmap: v2.13 CLIRunner Pipeline Targeted Fixes

## Overview

This roadmap implements Option 3 (Targeted Fixes) from the adversarial-debated pipeline architecture decision (convergence 0.72). The approach addresses all identified bugs and duplication at minimal risk without restructuring sprint's execution model.

The strategy is test-first: characterization tests are written before any refactoring begins, establishing a safety net for the hook migration. The refactoring itself is split into three independent sub-steps (wait deletion, hook migration, dead code removal) to minimize blast radius per commit.

The architectural decision to defer executor-level unification is documented as an explicit non-goal. Executor unification remains a hypothesis to validate in future phases, not a decision earned by current evidence.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Sprint Executor Characterization Tests | TEST | P0 | M | None | 4 | Medium |
| M2 | Process Duplication Elimination | IMPROVEMENT | P0 | M | M1 | 7 | Medium |
| M3 | Roadmap File-Passing Fix | IMPROVEMENT | P1 | S | M2 | 3 | Low |
| M4 | Validation and Acceptance | TEST | P1 | S | M1, M2, M3 | 5 | Low |

## Dependency Graph

```
M1 (Tests) → M2 (Hooks + Dead Code) → M3 (File-Passing)
                                          |
M1 ──────────────────────────────────────→ M4 (Validation)
M2 ──────────────────────────────────────→ M4
M3 ──────────────────────────────────────→ M4
```

Critical path: M1 → M2 → M3 → M4

---

## M1: Sprint Executor Characterization Tests

### Objective

Establish a characterization test safety net for sprint's executor by covering the 6 untested subsystems before any refactoring begins. Increase line coverage from ~45% to >= 70%.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Watchdog/stall detection tests (3 cases: kill action, warn action, reset on resume) | Tests pin current behavior of executor lines 126-162; stall_timeout, stall_action, _stall_acted all exercised |
| D1.2 | Multi-phase sequencing tests (2 cases: 3-phase happy path, halt at phase 3) | Tests verify phases execute in order and halt propagates correctly across >1 phase |
| D1.3 | TUI/monitor/tmux integration tests (4 cases: TUI updates, TUI error resilience, monitor lifecycle, tmux tail pane) | Tests verify TUI.update() called with MonitorState, TUI exceptions don't abort sprint, OutputMonitor.reset/start/stop called, tmux update called when session_name set |
| D1.4 | Diagnostics tests (2 cases: failure triggers collector, collection failure is non-fatal) | Tests verify DiagnosticCollector.collect() called on failure, exception in diagnostics doesn't abort sprint |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Characterization tests miss a subsystem | Medium | Medium | 70% coverage threshold enforced; code review of test plan against executor source |
| Mocking complexity for monitor/TUI threads | Low | Low | Use MagicMock for all external components; no real subprocess invocation |

---

## M2: Process Duplication Elimination

### Objective

Eliminate ~94 lines of duplicated process method overrides in sprint via lifecycle hooks in the pipeline base class, and remove confirmed dead code from roadmap executor. Split into 3 independent sub-steps to minimize blast radius.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | **M2a**: Delete sprint's wait() override (pure no-op duplication) | sprint/process.py no longer defines wait(); all existing tests pass unchanged |
| D2.2 | **M2b-base**: Add on_spawn, on_signal, on_exit hook params to pipeline ClaudeProcess.__init__ | 3 new optional params with None defaults; hook call sites in start(), terminate(), wait(); unit tests in tests/pipeline/test_process_hooks.py |
| D2.3 | **M2b-base**: Add on_exit call to wait() success path | wait() calls on_exit(pid, returncode) before _close_handles() on normal exit; unit test confirms hook fires on both wait() and terminate() paths |
| D2.4 | **M2b-migrate**: Add hook factory functions to sprint/process.py (_make_spawn_hook, _make_signal_hook, _make_exit_hook) | Factories capture phase/config context; produce closures that call debug_log with correct event names and kwargs |
| D2.5 | **M2b-migrate**: Wire hooks in sprint ClaudeProcess.__init__ and delete start(), terminate() overrides | Sprint ClaudeProcess defines only __init__ and build_prompt; all D4 characterization tests pass before AND after change |
| D2.6 | **M2b-migrate**: Verify NFR-007 compliance | `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results |
| D2.7 | **M2c**: Delete _FORBIDDEN_FLAGS and _build_subprocess_argv from roadmap/executor.py | `grep -rn "_build_subprocess_argv" src/` returns 0; `grep -rn "_FORBIDDEN_FLAGS" src/` returns 0; all tests pass |

### Dependencies

- M1: All D4 characterization tests must pass before any D2.x work begins (NFR-003 test gate)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hook refactor breaks SIGTERM/SIGKILL escalation | Low | High | D4 characterization tests pin signal handling; run full suite before and after D2.5 |
| was_timeout accuracy degrades after dropping _timed_out cross-reference | Very Low | Low | Executor handles timeout classification upstream (line 176-178); debug_log field is informational only |
| Dead code removal breaks untested path | Very Low | Medium | Grep verification + full test suite; _build_subprocess_argv has zero call sites confirmed |

---

## M3: Roadmap File-Passing Fix

### Objective

Fix the unreliable --file flag approach in roadmap step execution by embedding input file contents inline in the prompt, with a size guard for large files.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Add _embed_inputs() helper to roadmap/executor.py | Function reads input files, embeds as fenced code blocks with path headers; handles empty input list as no-op |
| D3.2 | Modify roadmap_run_step() to use inline embedding with 100KB size guard | extra_args=[] (no --file flags); if total content > 100KB, falls back to --file with warning logged |
| D3.3 | Integration test for file-passing | Test verifies prompt contains embedded content; test verifies paths with spaces handled correctly; test verifies 100KB guard triggers fallback |

### Dependencies

- M2 (specifically D2.7 -- dead code removal cleans up roadmap/executor.py before D3 modifies it)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Prompt size increase causes context overflow | Very Low | Medium | 100KB guard with --file fallback; roadmap inputs are typically 5-50KB markdown |
| Inline embedding changes output semantics | Low | Medium | Integration test with fixture comparison against current output |

---

## M4: Validation and Acceptance

### Objective

Verify all milestones meet their acceptance criteria and success metrics. Confirm zero regressions across the full test suite.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Full test suite passes (zero regressions) | `uv run pytest` exits 0 with all tests passing |
| D4.2 | Sprint executor coverage >= 70% | `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor` reports >= 70% |
| D4.3 | Net lines removed >= 58 from sprint/process.py | `git diff --stat` confirms reduction |
| D4.4 | Dead code lines removed >= 25 from roadmap/executor.py | `git diff --stat` confirms reduction |
| D4.5 | NFR-007 zero violations | `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 |
| D4.6 | No new Python package dependencies (NFR-004) | `git diff pyproject.toml` shows no additions to `[project.dependencies]` |

### Dependencies

- M1, M2, M3 (validates all prior milestones)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Coverage threshold not met | Low | Low | Test plan covers 12+ new cases across 6 subsystems; 70% is conservative |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Hook refactor breaks SIGTERM/SIGKILL escalation | M2 | Low | High | D4 characterization tests pin signal handling; run before/after D2.5 | refactorer |
| R-002 | Dead code removal breaks untested path | M2 | Very Low | Medium | Grep verification + full test suite | refactorer |
| R-003 | File-passing change alters roadmap output | M3 | Low | Medium | Integration test with fixture comparison | qa |
| R-004 | Characterization tests incomplete | M1 | Medium | Medium | 70% coverage threshold + code review | qa |
| R-005 | Hook exception in terminate() prevents SIGKILL escalation and orphans child process | M2 | Low | Medium | Document hook contract in docstring: hooks must not raise; hooks receive primitives only | refactorer |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | refactorer | architect (0.22 confidence), qa (0.15 confidence) | Spec frontmatter specifies refactorer; backend domain 90% aligns with code quality focus |
| Template | inline | No Tier 1/2/3 templates found | Fallback to inline generation |
| Milestone Count | 4 | 3-4 (LOW range) | base=3 + floor(2 domains / 2) = 4 |
| Adversarial Mode | none | N/A | No --specs or --multi-roadmap flags |
| Hook Design | Lifecycle callbacks (Option A) | Mixin (Option B -- NFR-007 violation), Decorator (Option C -- breaks inheritance) | Only approach preserving NFR-007 and existing inheritance hierarchy |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Lines removed (duplication) >= 58 net in sprint/process.py | M2, M4 | Yes |
| SC-002 | Lines removed (dead code) >= 25 in roadmap/executor.py | M2, M4 | Yes |
| SC-003 | Sprint executor test coverage >= 70% | M1, M4 | Yes |
| SC-004 | Regression count = 0 (full test suite green) | M4 | Yes |
| SC-005 | NFR-007 violations = 0 | M2, M4 | Yes |
