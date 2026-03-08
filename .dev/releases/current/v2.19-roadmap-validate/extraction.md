---
spec_source: .dev/releases/current/v2.18-roadmap-validate/spec-roadmap-validate.md
generated_by: sc:roadmap v2.0.0
generated_at: "2026-03-06"
complexity_score: 0.510
complexity_class: MEDIUM
primary_persona: backend
primary_persona_confidence: 0.42
consulting_personas: [architect, scribe]
domain_distribution:
  backend: 55
  documentation: 25
  performance: 10
  frontend: 5
  security: 5
extraction_mode: single-pass
requirement_counts:
  functional: 23
  non_functional: 5
  dependencies: 8
  success_criteria: 7
  risks: 5
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  extraction_passes: 1
  dedup_removals: 0
  verification_status: PASS
  fallback_activated: false
---

# Extraction Report: FR-050 — superclaude roadmap validate

## Project Overview

- **Title**: Roadmap Validate — Post-Pipeline Reflection & Adversarial Validation
- **Version**: 1.0.0
- **Feature ID**: FR-050
- **Parent Feature**: roadmap-pipeline
- **Target Release**: v2.19

**Summary**: Adds a `superclaude roadmap validate` subcommand that runs structured Claude subprocesses to validate merged roadmap artifacts across 7 dimensions. Supports single-agent and multi-agent adversarial validation modes. Validates cross-file consistency, deliverable ID uniqueness, bidirectional traceability, milestone DAG validity, tasklist parseability, and content-level interleave.

---

## Functional Requirements

### FR-001: Validate Subcommand Core
- **Description**: Add `superclaude roadmap validate <output-dir>` subcommand that validates presence of roadmap.md, test-strategy.md, and extraction.md in the specified output directory, then runs the validation pipeline.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L52-L61

### FR-002: Single-Agent Validation Mode
- **Description**: Default validation mode when `--agents` is not specified or has exactly 1 agent. Runs a single `reflect` step producing `validate/validation-report.md`.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L63-L76

### FR-003: Multi-Agent Adversarial Validation
- **Description**: When `--agents` specifies 2+ agents, run parallel reflect steps per agent followed by a sequential adversarial-merge step. Produces per-agent reflect files and a merged validation-report.md.
- **Priority**: P1
- **Domain**: Backend
- **Source**: L78-L95

### FR-004: Auto-Invocation from `roadmap run`
- **Description**: After the 8-step pipeline succeeds, `execute_roadmap()` automatically invokes `execute_validate()` unless `--no-validate` is passed. Inherits `--agents`, `--model`, `--max-turns`, and `--debug` from parent invocation.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L97-L103

### FR-005: 7-Dimension Validation
- **Description**: The reflection prompt validates across 7 dimensions with severity classification: Schema (BLOCKING), Structure (BLOCKING), Traceability (BLOCKING), Cross-file (BLOCKING), Interleave (WARNING), Decomposition (WARNING), Parseability (BLOCKING).
- **Priority**: P0
- **Domain**: Backend, Documentation
- **Source**: L105-L117

### FR-006: Validation Report Schema
- **Description**: `validation-report.md` has YAML frontmatter with blocking_issues_count, warnings_count, info_count, tasklist_ready, validation_agents, validation_mode. Body contains Summary, Blocking Issues, Warnings, Info, and Validation Metadata sections.
- **Priority**: P0
- **Domain**: Documentation
- **Source**: L119-L161

### FR-007: Agent Agreement Analysis Table
- **Description**: Multi-agent adversarial merge report includes Agent Agreement Analysis table with BOTH_AGREE, ONLY_A, ONLY_B, and CONFLICT categories. Severity conflicts are escalated to higher severity.
- **Priority**: P1
- **Domain**: Backend, Documentation
- **Source**: L163-L175

### FR-008: Reflection Prompt Specification
- **Description**: `build_reflect_prompt()` instructs Claude to read all 3 input files, validate across 7 dimensions, classify findings by severity, output structured report. Key constraints: context independence ("You did NOT generate these artifacts"), precision ("false positives waste user time"), location citations required.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L299-L316

### FR-009: Adversarial Merge Prompt Specification
- **Description**: `build_adversarial_merge_prompt()` instructs Claude to read all reflection reports, deduplicate findings, categorize unique findings, resolve severity conflicts by escalation, produce merged report with Agent Agreement Analysis, and recalculate blocking_issues_count from merged findings.
- **Priority**: P1
- **Domain**: Backend
- **Source**: L318-L339

### FR-010: New File — validate_executor.py
- **Description**: Create `src/superclaude/cli/roadmap/validate_executor.py` containing `execute_validate()` and `_build_validate_steps()` functions.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L183-L186

### FR-011: New File — validate_gates.py
- **Description**: Create `src/superclaude/cli/roadmap/validate_gates.py` containing `REFLECT_GATE` and `ADVERSARIAL_MERGE_GATE` gate criteria with semantic checks.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L183-L186

### FR-012: New File — validate_prompts.py
- **Description**: Create `src/superclaude/cli/roadmap/validate_prompts.py` containing `build_reflect_prompt()` and `build_adversarial_merge_prompt()` functions.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L183-L186

### FR-013: Modify commands.py
- **Description**: Add `validate` subcommand to roadmap CLI group and add `--no-validate` flag to `run` command.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L189-L190

### FR-014: Modify executor.py
- **Description**: Add call to `execute_validate()` after successful pipeline execution in `execute_roadmap()`.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L191

### FR-015: Add ValidateConfig Dataclass
- **Description**: Add `ValidateConfig(PipelineConfig)` dataclass to `models.py` with fields: output_dir, validate_dir, agents, roadmap_file, test_strategy_file, extraction_file.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L192, L212-L222

### FR-016: Single-Agent Step Construction
- **Description**: `_build_validate_steps()` with 1 agent returns a list with a single `Step` (id="reflect", gate=REFLECT_GATE, timeout=300s, retry_limit=1).
- **Priority**: P0
- **Domain**: Backend
- **Source**: L346-L359

### FR-017: Multi-Agent Step Construction
- **Description**: `_build_validate_steps()` with 2+ agents returns a parallel group of reflect steps followed by a sequential adversarial-merge step (gate=ADVERSARIAL_MERGE_GATE).
- **Priority**: P1
- **Domain**: Backend
- **Source**: L365-L393

### FR-018: CLI validate Command Interface
- **Description**: `roadmap validate` subcommand accepts output_dir (required), `--agents` (default: opus:architect), `--model`, `--max-turns` (default: 50), `--debug` flag.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L417-L432

### FR-019: --no-validate Flag
- **Description**: Add `--no-validate` flag to `roadmap run` command that skips the post-pipeline validation step.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L399-L413

### FR-020: Success Output Format
- **Description**: On success (no blocking issues), output step progress, summary counts, tasklist_ready status, and report file path.
- **Priority**: P1
- **Domain**: Documentation
- **Source**: L438-L444

### FR-021: Blocking Issues Warning Behavior
- **Description**: When blocking issues are found, warn user with issue summary but do not exit non-zero. List each blocking issue briefly in CLI output.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L446-L459

### FR-022: Gate Failure Output
- **Description**: When the validation subprocess itself fails (gate check failure), output FAIL status with reason and point user to potentially incomplete report file.
- **Priority**: P1
- **Domain**: Documentation
- **Source**: L461-L468

### FR-023: Gate Semantic Checks
- **Description**: Implement `_has_agreement_table` semantic check verifying Agent Agreement Analysis section with table. Reuse `_frontmatter_values_non_empty` from `roadmap/gates.py` via import.
- **Priority**: P0
- **Domain**: Backend
- **Source**: L226-L283

---

## Non-Functional Requirements

### NFR-001: Wall Time Constraint
- **Description**: Validate step adds ≤10% wall time to pipeline. ≤2 min for single agent.
- **Category**: Performance
- **Constraint**: ≤120 seconds single-agent, ≤10% overhead
- **Source**: L473

### NFR-002: Module Isolation
- **Description**: No imports from validate_* modules in pipeline/* modules. Maintains NFR-007 (existing constraint).
- **Category**: Maintainability
- **Constraint**: Zero reverse imports
- **Source**: L474

### NFR-003: Standalone Operation
- **Description**: `validate` subcommand works independently of `roadmap run`.
- **Category**: Reliability
- **Constraint**: Standalone invocable
- **Source**: L475

### NFR-004: Infrastructure Reuse
- **Description**: Reuses existing pipeline infrastructure (execute_pipeline, ClaudeProcess, gate_passed). Zero new infrastructure.
- **Category**: Maintainability
- **Constraint**: No new infrastructure classes
- **Source**: L476

### NFR-005: Unified Code Path
- **Description**: Single-agent and multi-agent share identical code path (list of 1 vs list of N).
- **Category**: Maintainability
- **Constraint**: One implementation for both modes
- **Source**: L477

---

## Dependencies

### DEP-001: validate_executor.py → validate_gates.py, validate_prompts.py
- **Type**: Internal
- **Affected**: FR-010, FR-011, FR-012
- **Source**: L201-L207

### DEP-002: validate_gates.py → roadmap/gates.py
- **Type**: Internal (import reuse)
- **Affected**: FR-011, FR-023
- **Source**: L229-L230

### DEP-003: ValidateConfig → PipelineConfig
- **Type**: Internal (inheritance)
- **Affected**: FR-015
- **Source**: L214

### DEP-004: execute_validate() → execute_pipeline()
- **Type**: Internal (function reuse)
- **Affected**: FR-010
- **Source**: L203-L204

### DEP-005: commands.py → validate_executor.py
- **Type**: Internal
- **Affected**: FR-013, FR-010
- **Source**: L206-L207

### DEP-006: executor.py → execute_validate()
- **Type**: Internal
- **Affected**: FR-014, FR-010
- **Source**: L204

### DEP-007: Step/GateCriteria/SemanticCheck class reuse
- **Type**: Internal (infrastructure)
- **Affected**: FR-011, FR-016, FR-017
- **Source**: L244-L283

### DEP-008: ClaudeProcess, gate_passed reuse
- **Type**: Internal (infrastructure)
- **Affected**: NFR-004
- **Source**: L476

---

## Success Criteria

### SC-001: Validate Report Production
- **Description**: validate subcommand produces validation-report.md with correct YAML frontmatter containing all required fields.
- **Derived From**: FR-006
- **Measurable**: Yes

### SC-002: Tasklist Readiness Logic
- **Description**: tasklist_ready is true if and only if blocking_issues_count == 0.
- **Derived From**: FR-005, FR-006
- **Measurable**: Yes

### SC-003: Agent Agreement Table
- **Description**: Multi-agent mode produces Agent Agreement Analysis table with BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categories.
- **Derived From**: FR-007
- **Measurable**: Yes

### SC-004: Auto-Invocation
- **Description**: `roadmap run` (without --no-validate) triggers validation after successful pipeline completion.
- **Derived From**: FR-004
- **Measurable**: Yes

### SC-005: Skip Validation
- **Description**: `--no-validate` flag skips validation step entirely.
- **Derived From**: FR-019
- **Measurable**: Yes

### SC-006: Unified Code Path
- **Description**: Single-agent and multi-agent use the same _build_validate_steps() function (list of 1 vs list of N).
- **Derived From**: NFR-005
- **Measurable**: Yes

### SC-007: Performance Target
- **Description**: Single-agent validation completes in ≤120 seconds.
- **Derived From**: NFR-001
- **Measurable**: Yes

---

## Risk Register

### RISK-001: Context Independence Limitation
- **Description**: Subprocess execution assumes context independence, but implicit state from the session environment could influence validation quality.
- **Probability**: Medium
- **Impact**: Medium
- **Affected**: FR-008
- **Source**: Inferred

### RISK-002: Gate False Positives
- **Description**: Semantic checks (e.g., _has_agreement_table) may produce false positives on valid but unconventional report formats.
- **Probability**: Medium
- **Impact**: Low
- **Affected**: FR-023
- **Source**: Inferred

### RISK-003: Multi-Agent Resource Constraints
- **Description**: Parallel reflect steps may hit API rate limits or resource constraints when running multiple Claude subprocesses concurrently.
- **Probability**: Low
- **Impact**: High
- **Affected**: FR-003, FR-017
- **Source**: Inferred

### RISK-004: Pipeline Infrastructure Coupling
- **Description**: Dependency on existing execute_pipeline infrastructure means changes to that module could break validate functionality.
- **Probability**: Low
- **Impact**: High
- **Affected**: NFR-004, DEP-004
- **Source**: Inferred

### RISK-005: Adversarial Merge Inconsistency
- **Description**: Severity conflict resolution during adversarial merge may produce inconsistent escalation decisions across different finding types.
- **Probability**: Medium
- **Impact**: Medium
- **Affected**: FR-007, FR-009
- **Source**: Inferred

---

## Domain Distribution Analysis

| Domain | Percentage | Key Requirements |
|--------|-----------|-----------------|
| Backend | 55% | CLI integration, subprocess orchestration, data models, pipeline reuse, step construction |
| Documentation | 25% | Report schemas, structured output, validation dimensions, output formatting |
| Performance | 10% | Wall time constraints, parallel execution efficiency |
| Frontend | 5% | CLI output formatting |
| Security | 5% | Validation dimension (schema/structure checks) |
