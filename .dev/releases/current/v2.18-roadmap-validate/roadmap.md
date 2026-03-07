---
spec_source: .dev/releases/current/v2.18-roadmap-validate/spec-roadmap-validate.md
generated: "2026-03-06"
generator: sc:roadmap
complexity_score: 0.510
complexity_class: MEDIUM
domain_distribution:
  backend: 55
  documentation: 25
  performance: 10
  frontend: 5
  security: 5
primary_persona: backend
consulting_personas: [architect, scribe]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Foundation & Data Model"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Low
  - id: M2
    title: "Core Validation Pipeline"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 6
    risk_level: Medium
  - id: M3
    title: "Foundation Validation Checkpoint"
    type: TEST
    priority: P3
    dependencies: [M1, M2]
    deliverable_count: 3
    risk_level: Low
  - id: M4
    title: "Multi-Agent Adversarial Mode"
    type: FEATURE
    priority: P1
    dependencies: [M2, M3]
    deliverable_count: 5
    risk_level: Medium
  - id: M5
    title: "CLI Integration & Auto-Invocation"
    type: FEATURE
    priority: P0
    dependencies: [M2, M4]
    deliverable_count: 5
    risk_level: Low
  - id: M6
    title: "Final Validation & Acceptance"
    type: TEST
    priority: P3
    dependencies: [M4, M5]
    deliverable_count: 4
    risk_level: Low
total_deliverables: 27
total_risks: 5
estimated_phases: 4
validation_score: 0.935
validation_status: PASS
---

# Roadmap: FR-050 — superclaude roadmap validate

## Overview

This roadmap defines the implementation plan for `superclaude roadmap validate`, a post-pipeline reflection and adversarial validation subcommand. The feature adds a structured validation layer that runs Claude subprocesses to verify roadmap artifacts across 7 dimensions (schema, structure, traceability, cross-file consistency, interleave, decomposition, parseability) before downstream `sc:tasklist` consumption.

The implementation follows a layered approach: foundation first (data model + infrastructure reuse), then single-agent validation pipeline, multi-agent adversarial mode, and CLI integration. The spec's emphasis on reusing existing pipeline infrastructure (execute_pipeline, ClaudeProcess, gate_passed) shapes the architecture — no new infrastructure classes are introduced.

Complexity is MEDIUM (0.510) with 6 milestones and a 1:2 interleave ratio (one validation checkpoint per two work milestones).

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Data Model | FEATURE | P0 | S | None | 4 | Low |
| M2 | Core Validation Pipeline | FEATURE | P0 | M | M1 | 6 | Medium |
| M3 | Foundation Validation Checkpoint | TEST | P3 | S | M1, M2 | 3 | Low |
| M4 | Multi-Agent Adversarial Mode | FEATURE | P1 | M | M2, M3 | 5 | Medium |
| M5 | CLI Integration & Auto-Invocation | FEATURE | P0 | S | M2, M4 | 5 | Low |
| M6 | Final Validation & Acceptance | TEST | P3 | S | M4, M5 | 4 | Low |

## Dependency Graph

```
M1 → M2 → M3 (validates M1, M2)
           ↓
           M4 → M5 → M6 (validates M4, M5)
           ↑
           M3
```

Textual: M1 → M2, M1 → M3, M2 → M3, M2 → M4, M3 → M4, M2 → M5, M4 → M5, M4 → M6, M5 → M6

---

## M1: Foundation & Data Model

### Objective

Establish the ValidateConfig data model and verify that existing pipeline infrastructure (execute_pipeline, ClaudeProcess, gate_passed, Step, GateCriteria, SemanticCheck) supports the validation use case without modification.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | ValidateConfig dataclass added to models.py extending PipelineConfig | Dataclass defines output_dir, validate_dir, agents, roadmap_file, test_strategy_file, extraction_file fields; passes type validation |
| D1.2 | Infrastructure compatibility audit — verify execute_pipeline, ClaudeProcess, gate_passed can be reused by validate_executor without changes | Written confirmation that no modifications to pipeline/* modules are needed; NFR-002 (no reverse imports) verified |
| D1.3 | validate_dir directory creation logic | ValidateConfig auto-creates `<output_dir>/validate/` directory if it does not exist |
| D1.4 | Required file presence check — roadmap.md, test-strategy.md, extraction.md | Clear error message if any file is missing; matches FR-001 requirement |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PipelineConfig interface may need extension for validate fields | Low | Medium | Audit existing fields before implementation; prefer composition if inheritance is limiting |

---

## M2: Core Validation Pipeline

### Objective

Implement single-agent validation mode: reflection prompt, gate criteria with semantic checks, step construction, and executor function. This milestone delivers the complete single-agent path (FR-002).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | validate_prompts.py — build_reflect_prompt() function | Prompt covers all 7 validation dimensions; includes context independence constraint, precision requirement, and location citation instruction per FR-008 |
| D2.2 | validate_gates.py — REFLECT_GATE instance | Gate checks frontmatter fields (blocking_issues_count, warnings_count, tasklist_ready), min_lines=20, includes _frontmatter_values_non_empty semantic check imported from roadmap/gates.py |
| D2.3 | validate_executor.py — _build_validate_steps() for single agent | Returns list with 1 Step (id="reflect", gate=REFLECT_GATE, timeout=300s, retry_limit=1); matches FR-016 |
| D2.4 | validate_executor.py — execute_validate() function | Calls execute_pipeline with steps from _build_validate_steps(); produces validation-report.md in validate_dir |
| D2.5 | Validation report output — YAML frontmatter + body structure | Report matches FR-006 schema: frontmatter with blocking_issues_count, warnings_count, info_count, tasklist_ready, validation_agents, validation_mode; body with Summary, Blocking Issues, Warnings, Info, Validation Metadata sections |
| D2.6 | tasklist_ready logic | tasklist_ready is true if and only if blocking_issues_count == 0; verified by unit test |

### Dependencies

- M1: ValidateConfig dataclass, infrastructure compatibility confirmed

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-001: Context independence limitation — subprocess may still have implicit state | Medium | Medium | Prompt explicitly states "You did NOT generate these artifacts"; run in isolated subprocess |
| RISK-002: Gate false positives on valid but unconventional report formats | Medium | Low | Keep gate criteria minimal; semantic checks focus on structural markers, not content style |

---

## M3: Foundation Validation Checkpoint

### Objective

Validate that M1 and M2 deliverables are correctly integrated, single-agent mode produces valid reports, and NFR constraints (module isolation, infrastructure reuse) are met.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Unit test suite: test_validate_models.py, test_validate_executor.py (single-agent), test_validate_gates.py, test_validate_prompts.py | All tests from spec Section 10.1 pass; covers config construction, step building, gate criteria, prompt content |
| D3.2 | NFR verification: no imports from validate_* in pipeline/* modules | grep/search confirms zero reverse imports (NFR-002) |
| D3.3 | Single-agent integration test: validate produces valid report from sample roadmap artifacts | End-to-end: provide sample roadmap.md/test-strategy.md/extraction.md → run validate → verify validation-report.md has correct frontmatter and body structure |

### Dependencies

- M1: Data model complete
- M2: Validation pipeline complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Test fixtures may not cover edge cases in report formats | Low | Low | Include both valid and malformed fixture files in test suite |

---

## M4: Multi-Agent Adversarial Mode

### Objective

Extend the validation pipeline to support multi-agent adversarial mode: parallel reflect steps, adversarial merge step, Agent Agreement Analysis table, and severity conflict resolution (FR-003, FR-007, FR-009, FR-017).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | validate_prompts.py — build_adversarial_merge_prompt() function | Prompt instructs deduplication, BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categorization, severity escalation, and merged report with Agent Agreement Analysis table per FR-009 |
| D4.2 | validate_gates.py — ADVERSARIAL_MERGE_GATE instance | Gate checks additional frontmatter fields (validation_mode, validation_agents), min_lines=30, includes _has_agreement_table semantic check |
| D4.3 | _has_agreement_table semantic check function | Verifies "## Agent Agreement Analysis" heading exists and is followed by a pipe-delimited table within 500 characters per spec section 4.5 |
| D4.4 | _build_validate_steps() for multi-agent | Returns parallel group of reflect steps + sequential adversarial-merge step; matches FR-017 structure |
| D4.5 | Agent Agreement Analysis table in merged report | Table contains Finding, Agent A, Agent B, Resolution columns with BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT entries per FR-007 |

### Dependencies

- M2: Single-agent pipeline (extended, not replaced — list of 1 vs list of N per NFR-005)
- M3: Validation checkpoint passed (single-agent mode confirmed working)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-003: Parallel reflect steps may hit rate limits | Low | High | Sequential fallback if parallel execution fails; document rate limit behavior |
| RISK-005: Adversarial merge may produce inconsistent severity resolution | Medium | Medium | Prompt specifies explicit escalation rule: conflicts always escalate to higher severity |

---

## M5: CLI Integration & Auto-Invocation

### Objective

Wire the validation pipeline into the CLI: add `roadmap validate` subcommand, add `--no-validate` flag to `roadmap run`, and implement auto-invocation from `execute_roadmap()` (FR-004, FR-013, FR-014, FR-018, FR-019).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | commands.py — `roadmap validate` subcommand | Accepts output_dir (required), --agents (default: opus:architect), --model, --max-turns (default: 50), --debug; matches FR-018 |
| D5.2 | commands.py — `--no-validate` flag on `roadmap run` | Flag is `is_flag=True`, skips validation step when set; matches FR-019 |
| D5.3 | executor.py — auto-invocation of execute_validate() | After successful pipeline execution, calls execute_validate() with inherited --agents, --model, --max-turns, --debug; skipped when --no-validate is set; matches FR-004, FR-014 |
| D5.4 | CLI output formatting — success, warning, and failure modes | Success output matches FR-020 format; blocking issues emit WARNING per FR-021; gate failures reported per FR-022 |
| D5.5 | Standalone operation verification | `roadmap validate <dir>` works independently without prior `roadmap run` in same session; matches NFR-003 |

### Dependencies

- M2: execute_validate() function
- M4: Multi-agent mode (CLI needs to support --agents with 2+ agents)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Flag inheritance from roadmap run may miss edge cases (e.g., --resume + validate) | Low | Medium | Spec section FR-050.4 documents resume interaction explicitly; test with --resume scenarios |

---

## M6: Final Validation & Acceptance

### Objective

Comprehensive validation of all deliverables against spec requirements, NFRs, and integration test scenarios. Verify the complete feature works end-to-end in both standalone and auto-invoked modes.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Integration tests: test_validate_dry_run, test_validate_missing_files, test_run_with_no_validate, test_run_auto_validates | All integration tests from spec Section 10.2 pass |
| D6.2 | Multi-agent unit tests: test_build_validate_steps_multi, test_merge_gate_has_agreement_table, test_merge_prompt_contains_categories | All multi-agent tests pass |
| D6.3 | NFR compliance verification | NFR-001: single-agent ≤120s; NFR-002: zero reverse imports; NFR-003: standalone works; NFR-004: no new infra classes; NFR-005: unified code path |
| D6.4 | Traceability matrix: every FR → deliverable AND every deliverable → FR | Complete bidirectional traceability verified |

### Dependencies

- M4: Multi-agent mode complete
- M5: CLI integration complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-004: Changes to execute_pipeline after implementation could break validate | Low | High | Pin integration tests to current infrastructure interface; add regression test for execute_pipeline compatibility |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Context independence limitation — subprocess may retain implicit session state | M2 | Medium | Medium | Prompt explicitly enforces independence; isolated subprocess execution | backend |
| R-002 | Gate semantic checks may false-positive on valid but unconventional reports | M2, M4 | Medium | Low | Minimal gate criteria; structural markers over content style checks | backend |
| R-003 | Multi-agent parallel execution may hit API rate limits | M4 | Low | High | Sequential fallback path; document rate limit thresholds | backend |
| R-004 | Pipeline infrastructure coupling — changes to execute_pipeline break validate | M6 | Low | High | Regression tests; interface stability contract with pipeline/* modules | architect |
| R-005 | Adversarial merge severity resolution may be inconsistent | M4 | Medium | Medium | Explicit escalation rule in prompt: conflicts always escalate to higher severity | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend (confidence: 0.42) | architect (generalist), scribe (0.18) | Backend domain at 55% — subprocess orchestration, data models, pipeline infrastructure |
| Template | inline (fallback) | No Tier 1-3 templates found (0 candidates) | No template files in project or user directories |
| Milestone Count | 6 | 5-7 (MEDIUM range) | base(5) + floor(3 domains / 2) = 6 |
| Adversarial Mode | none | N/A | No --specs or --multi-roadmap flags |
| Adversarial Base Variant | N/A | N/A | Adversarial mode not active |
| Compliance Tier | STRICT | Auto-detect would yield STANDARD | User override via --compliance strict |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | validate subcommand produces validation-report.md with correct YAML frontmatter | M2, M5 | Yes |
| SC-002 | tasklist_ready is true iff blocking_issues_count == 0 | M2 | Yes |
| SC-003 | Multi-agent mode produces Agent Agreement Analysis table | M4 | Yes |
| SC-004 | roadmap run auto-invokes validation after pipeline success | M5 | Yes |
| SC-005 | --no-validate skips validation step entirely | M5 | Yes |
| SC-006 | Single and multi-agent share unified code path (_build_validate_steps) | M2, M4 | Yes |
| SC-007 | Single-agent validation completes in ≤120 seconds | M6 | Yes |
