---
spec_source: .dev/releases/current/v2.19-roadmap-validate/spec-roadmap-validate.md
project_title: "FR-050: superclaude roadmap validate"
project_version: "1.0.0"
complexity_score: 0.42
complexity_class: MEDIUM
milestone_range: 5-7
interleave_ratio: "1:2"
primary_persona: backend
consulting_personas: [architect, scribe]
persona_confidence: 0.42
domain_distribution:
  backend: 55
  documentation: 20
  security: 10
  performance: 10
  frontend: 5
extraction_mode: "chunked (2 chunks)"
total_requirements: 25
total_frs: 20
total_nfrs: 5
total_dependencies: 9
total_success_criteria: 8
total_risks: 5
pipeline_diagnostics:
  prereq_checks:
    spec_exists: true
    spec_lines: 530
    output_dir_writable: true
    collision_detected: false
---

# Extraction Report: FR-050 — superclaude roadmap validate

## Summary

Add a `superclaude roadmap validate` subcommand that runs structured Claude subprocesses to validate merged roadmap artifacts against 7 dimensions (schema, structure, traceability, cross-file consistency, interleave, decomposition, parseability). Supports single-agent (default) and multi-agent adversarial modes. Auto-invoked after `roadmap run` pipeline success unless `--no-validate`.

## Functional Requirements

### FR-001: Validate Subcommand Entry Point
- **Description**: `superclaude roadmap validate <output-dir>` validates presence of 3 required files (roadmap.md, test-strategy.md, extraction.md) then runs the validation pipeline
- **Domain**: backend
- **Priority**: P0
- **Source**: L52-L60

### FR-002: Single-Agent Validation (Default)
- **Description**: When --agents is not specified or has exactly 1 agent, run a single reflect subprocess producing `validate/validation-report.md`
- **Domain**: backend
- **Priority**: P0
- **Source**: L62-L76

### FR-003: Multi-Agent Adversarial Validation
- **Description**: When --agents specifies 2+ agents, run parallel reflect steps per agent then an adversarial-merge step. Produces per-agent reflect files + merged validation-report.md
- **Domain**: backend
- **Priority**: P0
- **Source**: L78-L95

### FR-004: Auto-Invocation from `roadmap run`
- **Description**: After the 8-step pipeline succeeds, execute_roadmap() automatically invokes execute_validate() unless --no-validate. Inherits --agents, --model, --max-turns, --debug from parent invocation. Validation runs only after full pipeline success; skipped if pipeline halts
- **Domain**: backend
- **Priority**: P0
- **Source**: L97-L103

### FR-005: 7-Dimension Validation
- **Description**: The reflection prompt covers 7 dimensions with severity classification: Schema (BLOCKING), Structure (BLOCKING), Traceability (BLOCKING), Cross-file (BLOCKING), Interleave (WARNING), Decomposition (WARNING), Parseability (BLOCKING)
- **Domain**: backend, security
- **Priority**: P0
- **Source**: L105-L117

### FR-006: Validation Report Schema
- **Description**: validation-report.md has YAML frontmatter (blocking_issues_count, warnings_count, info_count, tasklist_ready, validation_agents, validation_mode) and structured body (Summary, Blocking Issues, Warnings, Info, Validation Metadata)
- **Domain**: documentation
- **Priority**: P0
- **Source**: L119-L161

### FR-007: Adversarial Merge Report
- **Description**: Multi-agent mode adds Agent Agreement Analysis table with finding-level agreement categorization: BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT (severity disagreement escalated to BLOCKING)
- **Domain**: documentation
- **Priority**: P1
- **Source**: L163-L175

### FR-008: New File Architecture
- **Description**: Create 3 new files in src/superclaude/cli/roadmap/: validate_executor.py (execute_validate, _build_validate_steps), validate_gates.py (REFLECT_GATE, ADVERSARIAL_MERGE_GATE), validate_prompts.py (build_reflect_prompt, build_adversarial_merge_prompt)
- **Domain**: backend
- **Priority**: P0
- **Source**: L179-L186

### FR-009: Modified Files
- **Description**: Modify 3 existing files: commands.py (add validate subcommand, --no-validate to run), executor.py (call execute_validate after pipeline success), models.py (add ValidateConfig dataclass)
- **Domain**: backend
- **Priority**: P0
- **Source**: L188-L195

### FR-010: ValidateConfig Data Model
- **Description**: Dataclass extending PipelineConfig with fields: output_dir, validate_dir, agents, roadmap_file, test_strategy_file, extraction_file. All paths derived from output_dir
- **Domain**: backend
- **Priority**: P0
- **Source**: L210-L222

### FR-011: Gate Criteria
- **Description**: REFLECT_GATE: frontmatter fields (blocking_issues_count, warnings_count, tasklist_ready), min 20 lines, STANDARD tier, semantic check for non-empty values. ADVERSARIAL_MERGE_GATE: adds validation_mode + validation_agents fields, min 30 lines, STRICT tier, semantic check for Agent Agreement Analysis table
- **Domain**: backend
- **Priority**: P0
- **Source**: L224-L283

### FR-012: Reflection Prompt Builder
- **Description**: build_reflect_prompt(agent, roadmap_file, test_strategy_file, extraction_file) instructs Claude to read 3 files, validate 7 dimensions, classify as BLOCKING/WARNING/INFO, output structured report, set tasklist_ready only if blocking_issues_count == 0
- **Domain**: backend
- **Priority**: P0
- **Source**: L297-L316

### FR-013: Adversarial Merge Prompt Builder
- **Description**: build_adversarial_merge_prompt(reflect_files, roadmap_file) instructs Claude to deduplicate findings (BOTH_AGREE), categorize uniques (ONLY_A/ONLY_B), escalate severity conflicts to higher severity, produce merged report with Agent Agreement Analysis table
- **Domain**: backend, documentation
- **Priority**: P1
- **Source**: L318-L339

### FR-014: Single-Agent Step Construction
- **Description**: _build_validate_steps() for 1 agent returns list with single Step (id=reflect, gate=REFLECT_GATE, timeout=300s, retry_limit=1, inputs=[roadmap, test-strategy, extraction])
- **Domain**: backend
- **Priority**: P0
- **Source**: L341-L359

### FR-015: Multi-Agent Step Construction
- **Description**: _build_validate_steps() for 2+ agents returns parallel group of reflect steps (one per agent) + sequential adversarial-merge Step with ADVERSARIAL_MERGE_GATE
- **Domain**: backend
- **Priority**: P0
- **Source**: L361-L393

### FR-016: --no-validate Flag
- **Description**: Add --no-validate is_flag to roadmap run command. When set, skip execute_validate() call after pipeline success
- **Domain**: backend
- **Priority**: P0
- **Source**: L395-L413

### FR-017: roadmap validate Subcommand
- **Description**: Standalone CLI: click.argument output_dir, options --agents (default opus:architect), --model, --max-turns (default 50), --debug. Note: default is single-agent for cost efficiency; roadmap run inherits parent --agents
- **Domain**: backend
- **Priority**: P0
- **Source**: L415-L432

### FR-018: Success Output Format
- **Description**: Console output showing agent count, step pass status with timing, summary counts, tasklist_ready status, report file path
- **Domain**: documentation
- **Priority**: P1
- **Source**: L434-L444

### FR-019: Blocking Issues Output Format
- **Description**: WARNING with blocking issue count + per-issue summary (ID, description). Non-zero exit not required (warn, don't fail)
- **Domain**: documentation
- **Priority**: P1
- **Source**: L446-L459

### FR-020: Gate Failure Output Format
- **Description**: FAIL with attempt count, timing, reason for failure. WARNING that validation-report.md may be incomplete with inspect path
- **Domain**: documentation
- **Priority**: P1
- **Source**: L461-L468

## Non-Functional Requirements

### NFR-001: Wall Time Budget
- **Description**: Validate step adds ≤10% wall time to overall pipeline (≤2 minutes for single agent)
- **Category**: performance
- **Constraint**: ≤2 min single-agent, ≤10% of pipeline wall time
- **Source**: L474

### NFR-002: No Reverse Imports
- **Description**: No imports from validate_* modules in pipeline/* modules. Maintains NFR-007 of the parent system
- **Category**: maintainability
- **Constraint**: Zero import references from pipeline/ to validate_*
- **Source**: L475

### NFR-003: Standalone Independence
- **Description**: validate subcommand works independently of roadmap run (can be invoked on pre-existing output directories)
- **Category**: maintainability
- **Constraint**: validate CLI functions without roadmap run context
- **Source**: L476

### NFR-004: Infrastructure Reuse
- **Description**: Reuses existing pipeline infrastructure (execute_pipeline, ClaudeProcess, gate_passed). Zero new infrastructure components
- **Category**: maintainability
- **Constraint**: No new infrastructure abstractions
- **Source**: L477

### NFR-005: Unified Code Path
- **Description**: Single-agent and multi-agent validation share identical code path (list of 1 vs list of N)
- **Category**: maintainability
- **Constraint**: One implementation, parameterized by agent count
- **Source**: L478

## Dependencies

### DEP-001: validate_executor → validate_gates + validate_prompts
- **Type**: internal
- **Description**: validate_executor.py imports gate criteria from validate_gates.py and prompt builders from validate_prompts.py
- **Affected**: FR-008, FR-011, FR-012, FR-013, FR-014, FR-015

### DEP-002: validate_executor → pipeline/executor
- **Type**: internal
- **Description**: validate_executor.py reuses execute_pipeline from existing pipeline infrastructure
- **Affected**: FR-008, NFR-004

### DEP-003: commands.py → validate_executor
- **Type**: internal
- **Description**: commands.py imports execute_validate() for the validate subcommand
- **Affected**: FR-009, FR-017

### DEP-004: executor.py → validate_executor
- **Type**: internal
- **Description**: executor.py calls execute_validate() after pipeline success for auto-invocation
- **Affected**: FR-004, FR-009

### DEP-005: ValidateConfig → PipelineConfig
- **Type**: internal
- **Description**: ValidateConfig dataclass extends PipelineConfig
- **Affected**: FR-010

### DEP-006: validate_gates → roadmap/gates
- **Type**: internal
- **Description**: validate_gates.py imports _frontmatter_values_non_empty from existing gates.py
- **Affected**: FR-011

### DEP-007: Multi-agent → Single-agent code path
- **Type**: internal
- **Description**: Multi-agent mode uses the same step construction as single-agent (list of N)
- **Affected**: FR-003, FR-015, NFR-005

### DEP-008: Pipeline Infrastructure (External)
- **Type**: external
- **Description**: Requires existing ClaudeProcess, gate_passed, execute_pipeline, GateCriteria, SemanticCheck, Step classes
- **Affected**: FR-008, FR-011, FR-014, FR-015, NFR-004

### DEP-009: Roadmap Pipeline Artifacts (External)
- **Type**: external
- **Description**: Requires roadmap.md, test-strategy.md, extraction.md to exist in output directory (produced by roadmap run steps 1-7)
- **Affected**: FR-001, FR-004

## Success Criteria

### SC-001: Cross-file consistency detection
- **Description**: Validation catches test-strategy milestone references that don't match roadmap milestones
- **Derived From**: FR-005 (dimension 4)
- **Measurable**: Yes

### SC-002: Duplicate deliverable ID detection
- **Description**: Validation catches duplicate D-xxxx IDs across milestones
- **Derived From**: FR-005 (dimension 2)
- **Measurable**: Yes

### SC-003: Bidirectional traceability validation
- **Description**: Every deliverable maps to a requirement AND every requirement maps to a deliverable
- **Derived From**: FR-005 (dimension 3)
- **Measurable**: Yes

### SC-004: Circular dependency detection
- **Description**: Milestone DAG has no cycles and all dependency refs resolve
- **Derived From**: FR-005 (dimension 2)
- **Measurable**: Yes

### SC-005: Parseability validation
- **Description**: Roadmap content is parseable into items via headings, bullets, numbered lists (sc:tasklist compatibility)
- **Derived From**: FR-005 (dimension 7)
- **Measurable**: Yes

### SC-006: Mode parity
- **Description**: Both single-agent and multi-agent modes produce structurally valid reports
- **Derived From**: FR-002, FR-003, NFR-005
- **Measurable**: Yes

### SC-007: Auto-invocation works seamlessly
- **Description**: roadmap run automatically invokes validation without user intervention
- **Derived From**: FR-004
- **Measurable**: Yes

### SC-008: --no-validate skips correctly
- **Description**: --no-validate flag prevents validation step from running
- **Derived From**: FR-016
- **Measurable**: Yes

## Risks

### RISK-001: Subprocess Context Independence
- **Description**: Validation subprocess lacks pipeline execution context, may miss issues that require understanding of generation decisions
- **Probability**: Medium
- **Impact**: Medium
- **Affected**: FR-002, FR-003

### RISK-002: False Positive Rate
- **Description**: Overly strict validation may flag legitimate patterns as issues, wasting user time on triaging non-issues
- **Probability**: Medium
- **Impact**: Low
- **Affected**: FR-005, FR-012

### RISK-003: Multi-Agent Cost Overhead
- **Description**: Running 2+ agents for validation may increase token costs without proportional quality improvement for simpler roadmaps
- **Probability**: Low
- **Impact**: Medium
- **Affected**: FR-003, FR-015

### RISK-004: Gate Calibration
- **Description**: REFLECT_GATE and ADVERSARIAL_MERGE_GATE thresholds (min_lines, required fields) may be too strict or too lenient in practice
- **Probability**: Medium
- **Impact**: Medium
- **Affected**: FR-011

### RISK-005: Executor Integration Regression
- **Description**: Modifying executor.py to call execute_validate() may introduce regression in the existing pipeline flow
- **Probability**: Low
- **Impact**: High
- **Affected**: FR-004, FR-009, DEP-004
