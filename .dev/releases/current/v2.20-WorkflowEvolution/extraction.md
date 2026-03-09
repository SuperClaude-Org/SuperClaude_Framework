---
spec_source: "spec-workflow-evolution-merged.md"
generated: "2026-03-09T12:00:00Z"
generator: "requirements-extraction-agent/opus-4.6"
functional_requirements: 31
nonfunctional_requirements: 10
total_requirements: 41
complexity_score: 0.72
complexity_class: moderate
domains_detected: 5
risks_identified: 8
dependencies_identified: 9
success_criteria_count: 14
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 141.0, started_at: "2026-03-09T16:06:30.416214+00:00", finished_at: "2026-03-09T16:08:51.441023+00:00"}
---

## Functional Requirements

### FR-001: Spec-Fidelity Prompt Builder
New prompt builder `build_spec_fidelity_prompt(spec_content: str, roadmap_content: str) -> str` in `roadmap/prompts.py` that instructs the model to compare every function signature, data model, gate criteria, CLI option, and NFR in the spec against the roadmap representation.
*Source: FR-051.1 AC-1, AC-2*

### FR-002: Spec-Fidelity Prompt Quoting Requirement
Prompt requires the model to quote both spec and roadmap text for each identified deviation.
*Source: FR-051.1 AC-3*

### FR-003: Spec-Fidelity Prompt Structured Output
Prompt requires structured YAML frontmatter output containing `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`, `validation_complete`, `fidelity_check_attempted`, `tasklist_ready`.
*Source: FR-051.1 AC-4*

### FR-004: Spec-Fidelity Deviation Table Format
Prompt requires a deviation table with columns: `ID`, `Severity`, `Source Pair`, `Deviation`, `Spec Quote`, `Roadmap Quote`, `Impact`, `Recommended Correction`.
*Source: FR-051.1 AC-5*

### FR-005: SPEC_FIDELITY_GATE Definition
New gate `SPEC_FIDELITY_GATE` in `roadmap/gates.py` with enforcement tier STRICT.
*Source: FR-051.1 AC-6*

### FR-006: SPEC_FIDELITY_GATE Blocking Logic
Gate blocks pipeline if `high_severity_count > 0` via semantic check on frontmatter value.
*Source: FR-051.1 AC-7*

### FR-007: SPEC_FIDELITY_GATE Degraded Mode Pass-Through
Gate passes with warning (does not block) if `validation_complete: false` and `fidelity_check_attempted: true`.
*Source: FR-051.1 AC-8*

### FR-008: Spec-Fidelity Step in Pipeline
New step `spec-fidelity` added to `_build_steps()` in `roadmap/executor.py` after test-strategy, receiving `spec_file` and `roadmap.md` as inputs.
*Source: FR-051.1 AC-9, AC-10*

### FR-009: Spec-Fidelity Step Configuration
Step timeout: 600 seconds. Step retry_limit: 1. Output file: `{output_dir}/spec-fidelity.md`.
*Source: FR-051.1 AC-11, AC-12, AC-13*

### FR-010: Spec-Fidelity Bypass Protection
Existing `--no-validate` flag skips only the validate pipeline, not spec-fidelity (spec-fidelity is a generation quality gate).
*Source: FR-051.1 AC-14*

### FR-011: Fidelity State Persistence
After spec-fidelity step completes (pass, fail, or degraded), write `fidelity_status: pass|fail|skipped|degraded` to `.roadmap-state.json`.
*Source: FR-051.1 AC-15*

### FR-012: Multi-Agent Severity Conflict Resolution
When run in multi-agent mode, conflicting severity ratings for the same deviation are resolved conservatively: highest stated severity from any agent is used; `validation_complete: false` if any agent fails.
*Source: FR-051.1 AC-16*

### FR-013: Tasklist-Fidelity Prompt Builder
New prompt builder `build_tasklist_fidelity_prompt(roadmap_content: str, tasklist_content: str) -> str` that checks deliverable coverage, signature preservation, traceability ID validity, and dependency chain correctness.
*Source: FR-051.2 AC-1, AC-2*

### FR-014: Tasklist-Fidelity Deviation Format Reuse
Tasklist fidelity prompt requires the same normalized deviation report format as the spec-fidelity harness.
*Source: FR-051.2 AC-3*

### FR-015: TASKLIST_FIDELITY_GATE Definition
New gate `TASKLIST_FIDELITY_GATE` with enforcement tier STRICT that blocks if `high_severity_count > 0`.
*Source: FR-051.2 AC-4, AC-5*

### FR-016: Tasklist Validate CLI Subcommand
New CLI subcommand `superclaude tasklist validate <output-dir>` with options `--roadmap-file`, `--tasklist-dir`, `--model`, `--max-turns`, `--debug`. Returns exit code 1 if HIGH-severity deviations found. Output file: `{output_dir}/tasklist-fidelity.md`.
*Source: FR-051.2 AC-6, AC-7, AC-8*

### FR-017: Tasklist Validate Standalone Invocability
Subcommand can be invoked standalone or wired into future pipeline automation.
*Source: FR-051.2 AC-9*

### FR-018: REFLECT_GATE Tier Promotion
`REFLECT_GATE` in `validate_gates.py` promoted from `STANDARD` to `STRICT` enforcement tier so semantic checks actually execute.
*Source: FR-051.3 AC-1*

### FR-019: Cross-Reference Resolution Fix
`_cross_refs_resolve()` in `roadmap/gates.py` changed from always-return-True to actual validation: extract heading anchors, find cross-references, return False if any reference targets a non-existent heading.
*Source: FR-051.3 AC-2*

### FR-020: Gate Fix Test Updates
Existing tests updated for STRICT enforcement behavior on REFLECT_GATE. New tests added for `_cross_refs_resolve()` with both passing and failing inputs. No regression in existing gate behavior.
*Source: FR-051.3 AC-3, AC-4, AC-5*

### FR-021: Deviation Report YAML Frontmatter Schema
Deviation reports must include YAML frontmatter with fields: `source_pair`, `high_severity_count`, `medium_severity_count`, `low_severity_count`, `total_deviations`, `upstream_file`, `downstream_file`, `validation_complete`, `fidelity_check_attempted`, `tasklist_ready`.
*Source: FR-051.4 AC-1*

### FR-022: Deviation Report Table Schema
Deviation table with columns: `ID`, `Severity`, `Deviation`, `Upstream Quote`, `Downstream Quote`, `Impact`, `Recommended Correction`.
*Source: FR-051.4 AC-2*

### FR-023: Severity Classification Definitions
HIGH: Functional requirement missing, signature changed, constraint dropped, API contract broken. MEDIUM: Requirement simplified, parameter renamed, NFR softened. LOW: Formatting difference, section reordering, clarification added.
*Source: FR-051.4 AC-3*

### FR-024: High Severity Count Semantic Check
Gate semantic check `_high_severity_count_zero(content: str) -> bool` returns True only if `high_severity_count` is 0; returns False if field missing.
*Source: FR-051.4 AC-4*

### FR-025: Tasklist Ready Consistency Semantic Check
Gate semantic check `_tasklist_ready_consistent(content: str) -> bool` validates that `tasklist_ready` is consistent with `high_severity_count == 0` AND `validation_complete == true`.
*Source: FR-051.4 AC-5*

### FR-026: Deviation Format Documentation
Deviation report format documented in a reference file accessible to prompt builders.
*Source: FR-051.4 AC-6*

### FR-027: Retrospective Parameter in Extract Prompt
`build_extract_prompt()` in `roadmap/prompts.py` accepts optional `retrospective_content: str | None` parameter. When provided, the extraction prompt includes a "Known Issues from Prior Releases" section.
*Source: FR-051.5 AC-1, AC-2*

### FR-028: RoadmapConfig Retrospective Extension
`RoadmapConfig` extended with optional `retrospective_file: Path | None` field. `_build_steps()` passes retrospective content to extract prompt when file exists.
*Source: FR-051.5 AC-3, AC-4*

### FR-029: Retrospective CLI Flag
CLI `roadmap run` accepts optional `--retrospective` flag pointing to a retrospective file. If file doesn't exist, extraction proceeds normally (no error).
*Source: FR-051.5 AC-5, AC-6*

### FR-030: Degraded Fidelity State Persistence
When fidelity agent fails after retry_limit exhausted, write `fidelity_check_attempted: true, validation_complete: false, fidelity_status: degraded` to `.roadmap-state.json`. Produce `spec-fidelity.md` with `validation_complete: false` frontmatter even on agent failure with error summary in body.
*Source: FR-051.6 AC-1, AC-2*

### FR-031: FidelityDeviation Typed Dataclass
New `FidelityDeviation` dataclass with fields: `source_pair`, `severity` (Literal["HIGH","MEDIUM","LOW"]), `deviation`, `upstream_quote`, `downstream_quote`, `impact`, `recommended_correction`. Provides typed, serializable backing model for deviation table rows.
*Source: §4.5 Data Models*

## Non-Functional Requirements

### NFR-001: Spec-Fidelity Execution Time
Spec-fidelity step execution time ≤120 seconds per run, measured by wall-clock time.
*Source: NFR-051.1*

### NFR-002: Tasklist-Fidelity Execution Time
Tasklist-fidelity validation time ≤120 seconds per run, measured by wall-clock time.
*Source: NFR-051.2*

### NFR-003: No Pipeline Regression
No regression in existing pipeline execution time — ≤5% increase in total pipeline time (excluding new step).
*Source: NFR-051.3*

### NFR-004: Gate Fix Backward Compatibility
All existing passing tests continue to pass after gate fixes. Measured by `uv run pytest tests/roadmap/`.
*Source: NFR-051.4*

### NFR-005: Deviation Report Parseability
Gate can extract severity counts from 100% of well-formed deviation reports. Verified via unit tests with varied report formats.
*Source: NFR-051.5*

### NFR-006: Minimal Architectural Disruption
No new executor/process framework introduced. Verified by code review (no new subprocess abstraction layer).
*Source: NFR-051.6*

### NFR-007: Degraded Report Distinguishability
Degraded reports must be distinguishable from clean passes: `validation_complete: false` is never present on a clean pass.
*Source: FR-051.6 AC-5 (implicit NFR)*

### NFR-008: Conservative Tasklist Readiness
`tasklist_ready: false` when `validation_complete: false` — unknown fidelity = not ready.
*Source: FR-051.6 AC-6 (implicit NFR)*

### NFR-009: Step Timeout Budget
Spec-fidelity step timeout of 600 seconds with retry_limit of 1, comparable to merge step token budget.
*Source: FR-051.1 AC-11, AC-12*

### NFR-010: Validation Layering Integrity
Each artifact validated against its immediate upstream source of truth (roadmap vs spec, tasklist vs roadmap), not against the original spec. Prevents validation-layer coupling.
*Source: §2 Solution Overview*

## Complexity Assessment

**Complexity Score**: 0.72
**Complexity Class**: moderate

**Scoring Rationale**:

| Factor | Weight | Score | Contribution |
|--------|--------|-------|--------------|
| Domain count (5: pipeline, CLI, gate engine, prompt engineering, state management) | 0.15 | 0.7 | 0.105 |
| File scope (8 new files, 7 modified files) | 0.20 | 0.75 | 0.150 |
| Integration complexity (2 pipeline boundaries, state persistence, multi-agent) | 0.20 | 0.8 | 0.160 |
| Existing code modifications (gate fixes, tier promotions, cross-ref resolution) | 0.15 | 0.7 | 0.105 |
| LLM-dependent validation (prompt-based fidelity, non-deterministic output) | 0.15 | 0.8 | 0.120 |
| Test coverage requirement (22 unit + 8 integration + 4 E2E) | 0.10 | 0.6 | 0.060 |
| Breaking change potential (2 gate behavior changes) | 0.05 | 0.7 | 0.035 |
| **Total** | **1.00** | | **0.735** |

The spec self-assesses at 0.70 complexity; independent assessment yields 0.735 — confirming **moderate** classification. The work is well-scoped with clear boundaries but involves non-trivial integration across pipeline, gate engine, CLI, and prompt layers. The LLM-dependent validation introduces inherent non-determinism that elevates integration testing complexity.

## Architectural Constraints

### AC-001: Pipeline Framework Reuse
No new executor/process framework may be introduced. All new steps must use the existing `pipeline/executor.py` and `pipeline/gates.py` abstractions.
*Source: NFR-051.6, §4.3*

### AC-002: Markdown Artifact Format
All output artifacts (spec-fidelity.md, tasklist-fidelity.md) must use structured markdown with YAML frontmatter, consistent with all existing pipeline artifacts.
*Source: §2.1 Design Decision 3*

### AC-003: Gate Engine Tier Semantics
Gates use the existing STANDARD/STRICT tier system. Semantic checks only execute at STRICT tier. No new tier types or special modes may be added to the gate engine.
*Source: §2.1 Design Decision 5, FR-051.3*

### AC-004: Validation Layering Principle
Each artifact is validated against its immediate upstream source of truth only (roadmap↔spec, tasklist↔roadmap). No skip-level validation (e.g., tasklist against original spec).
*Source: §2 Solution Overview*

### AC-005: Spec-Fidelity Cannot Be Skipped by --no-validate
The `--no-validate` flag controls only the validate pipeline, not the spec-fidelity generation quality gate.
*Source: FR-051.1 AC-14*

### AC-006: Existing Module Boundaries
The `pipeline/` module (models.py, gates.py, executor.py) remains unchanged. All new logic extends the `roadmap/` module or creates the new `tasklist/` module.
*Source: §4.3 Module Dependency Graph*

### AC-007: Python ≥3.10 Type Syntax
Data models use `Path | None` union syntax requiring Python 3.10+. `FidelityDeviation.severity` uses `Literal["HIGH", "MEDIUM", "LOW"]`.
*Source: §4.5, pyproject.toml*

### AC-008: Click CLI Framework
All CLI extensions use Click (existing dependency). New `tasklist validate` subcommand and `--retrospective` option follow Click patterns.
*Source: §5.1, project dependencies*

## Risk Inventory

### RSK-001: LLM Count Inconsistency (Severity: Medium)
LLM produces inconsistent deviation counts — frontmatter says 0 HIGH but table contains HIGH rows.
**Mitigation**: Gate checks frontmatter only; prompt emphasizes consistency requirement; `_tasklist_ready_consistent` cross-validates derived field.
*Source: §7 Risk 1*

### RSK-002: Pipeline Time Increase for Large Specs (Severity: Low)
Spec-fidelity step increases pipeline time significantly for large specs (>100KB).
**Mitigation**: 600s timeout with retry; specs >100KB could be summarized before comparison.
*Source: §7 Risk 2*

### RSK-003: Cross-Reference Fix Breaking Existing Roadmaps (Severity: Medium)
`_cross_refs_resolve()` fix causes existing valid roadmaps to fail MERGE_GATE due to dangling references.
**Mitigation**: Test against existing artifacts in `.dev/releases/complete/`; add warning-only mode initially if needed.
*Source: §7 Risk 3*

### RSK-004: Retrospective Bias in Extraction (Severity: Low)
Retrospective wiring biases extraction toward prior failures, missing new risks.
**Mitigation**: Prompt frames retrospective as "areas to watch" not "requirements to add"; extraction retains its own analysis independence.
*Source: §7 Risk 4*

### RSK-005: Tasklist Token Cost (Severity: Medium)
Tasklist fidelity check requires reading multiple phase files, increasing token cost.
**Mitigation**: Concatenate tasklist-index.md with phase files into single input; limit to index + 2 most relevant phases.
*Source: §7 Risk 5*

### RSK-006: REFLECT_GATE Promotion Breaking Reports (Severity: Medium)
REFLECT_GATE promotion to STRICT causes existing valid validation reports to fail if `_frontmatter_values_non_empty` check was silently skipped.
**Mitigation**: Run REFLECT_GATE against existing validation artifacts before deploying.
*Source: §7 Risk 6*

### RSK-007: Semantic Drift in LLM Deviation Classification (Severity: Medium)
LLM may inconsistently classify deviations across runs — same deviation rated HIGH in one run and MEDIUM in another.
**Mitigation**: Severity definitions documented explicitly in prompt (FR-023); multi-agent conservative resolution (FR-012).
*Source: Implicit from LLM-as-judge architecture*

### RSK-008: State File Corruption (Severity: Low)
Concurrent pipeline runs or crashes during `.roadmap-state.json` writes could corrupt state.
**Mitigation**: State writes are additive fields (FR-011); file-level atomicity is sufficient for single-process execution.
*Source: Implicit from FR-051.1 AC-15, §9 Rollback plan*

## Dependency Inventory

### DEP-001: Pipeline Framework
`src/superclaude/cli/pipeline/` — models.py (GateCriteria, Step, StepResult, SemanticCheck), gates.py (gate_passed), executor.py (execute_pipeline). Used unchanged as foundation.

### DEP-002: Roadmap Module
`src/superclaude/cli/roadmap/` — gates.py, validate_gates.py, executor.py, prompts.py, models.py, commands.py. Modified in-place.

### DEP-003: Click CLI Framework
click>=8.0.0 — used for CLI subcommand registration and option parsing.

### DEP-004: Python re Module
Standard library `re` — used by `_high_severity_count_zero()` and `_tasklist_ready_consistent()` for frontmatter field extraction.

### DEP-005: Python dataclasses Module
Standard library `dataclasses` — used for `FidelityDeviation` and `RoadmapConfig` extension.

### DEP-006: LLM API (Claude)
Prompt-based fidelity validation requires Claude API access. Agent timeout and retry behavior depend on API reliability.

### DEP-007: Existing Gate Test Suite
`tests/roadmap/` — existing tests must continue passing after gate engine fixes. Regression baseline.

### DEP-008: `.roadmap-state.json` State File
Existing state file format for pipeline state persistence. New `fidelity_status` field is additive.

### DEP-009: Existing Pipeline Artifacts
`.dev/releases/complete/` — existing roadmap/validation artifacts used for regression testing cross-reference fix (RSK-003, RSK-006).

## Success Criteria

### SC-001: Spec-Fidelity Gate Blocks HIGH Deviations
Pipeline halts when `high_severity_count > 0` in spec-fidelity report. Verified by integration test `test_spec_fidelity_blocks_on_high_deviation`.

### SC-002: Spec-Fidelity Gate Passes Clean Roadmaps
Pipeline continues when `high_severity_count == 0`. Verified by integration test `test_spec_fidelity_passes_clean_roadmap`.

### SC-003: Cross-Reference Validation Enforced
`_cross_refs_resolve()` returns False for dangling references, True for valid references. Verified by unit tests `test_cross_refs_resolve_valid` and `test_cross_refs_resolve_invalid`.

### SC-004: REFLECT_GATE Semantic Checks Execute
Semantic checks on REFLECT_GATE run at STRICT tier (previously silently skipped at STANDARD). Verified by `test_reflect_gate_semantic_checks_execute`.

### SC-005: Tasklist Validation Catches Fabricated Traceability
`superclaude tasklist validate` identifies fabricated traceability IDs in tasklist bundles. Verified by E2E test against v2.19 artifacts.

### SC-006: Retrospective Context Reaches Extraction
When `--retrospective` is provided, extraction prompt includes "Known Issues from Prior Releases" section. Verified by `test_extract_prompt_with_retrospective`.

### SC-007: Degraded Validation Explicit and Non-Blocking
Agent failure produces `validation_complete: false` report, pipeline continues with warning. Verified by `test_degraded_fidelity_pipeline_continues`.

### SC-008: State Persistence Records Fidelity Status
`.roadmap-state.json` records `fidelity_status: pass|fail|skipped|degraded` after step. Verified by `test_state_persistence_writes_fidelity_status`.

### SC-009: Tasklist Ready Consistency
`tasklist_ready` field is always consistent with `high_severity_count == 0 AND validation_complete == true`. Verified by `test_tasklist_ready_consistent_check_passes` and `test_tasklist_ready_consistent_check_fails_on_mismatch`.

### SC-010: No Test Regression
All existing passing tests continue to pass: `uv run pytest tests/roadmap/` shows 0 regressions. Threshold: 100%.

### SC-011: Execution Time Budget
Spec-fidelity step completes within 120 seconds (NFR-001). Tasklist validation completes within 120 seconds (NFR-002).

### SC-012: Pipeline Time Overhead
Total pipeline time (excluding new step) increases ≤5% compared to baseline.

### SC-013: Deviation Report 100% Parseable
Gate can extract severity counts from 100% of well-formed deviation reports. Verified by unit tests with varied formats.

### SC-014: Spec-Fidelity Not Skippable by --no-validate
`--no-validate` flag does not skip the spec-fidelity step. Verified by integration test `test_pipeline_includes_spec_fidelity_step`.

## Open Questions

### OQ-001: Cross-Reference Strictness Rollout
Should `_cross_refs_resolve()` fix be warning-first (log but don't block) for one release cycle before becoming blocking? Existing roadmaps may have dangling refs.
**Impact**: Medium — affects gate blocking behavior and migration risk.
**Resolution Target**: Before implementation begins.
*Source: Open Item 1*

### OQ-002: Tasklist Module Placement
Should tasklist validation live under `cli/tasklist/` (new module) or `cli/roadmap/` (extend existing)?
**Impact**: Low — organizational, not functional.
**Resolution Target**: During Phase 3 implementation.
*Source: Open Item 2*

### OQ-003: Deviation Count Cross-Validation
Should the gate verify that frontmatter severity counts match actual table row counts? This would catch LLM count inconsistency (RSK-001).
**Impact**: Medium — prevents silent count mismatches but adds parsing complexity.
**Resolution Target**: During Phase 2 implementation.
*Source: Open Item 3*

### OQ-004: Fidelity vs. Reflect Step Ordering
Should spec-fidelity step run before or after the existing reflect validation step? Does spec-fidelity make reflect redundant for roadmap fidelity checking?
**Impact**: Medium — affects executor step ordering and total pipeline time.
**Resolution Target**: Before implementation begins.
*Source: Open Item 4*

### OQ-005: MEDIUM Severity Blocking Policy
Should MEDIUM severity become blocking for certain deviation categories (e.g., fabricated traceability IDs per Gap Analysis TD-001)?
**Impact**: Medium — affects gate strictness and false-positive tolerance.
**Resolution Target**: During gate finalization (Phase 2).
*Source: Open Item 5*

### OQ-006: Deviation Table Column Mismatch
FR-051.1 AC-5 specifies an 8-column deviation table (`ID`, `Severity`, `Source Pair`, `Deviation`, `Spec Quote`, `Roadmap Quote`, `Impact`, `Recommended Correction`) while FR-051.4 AC-2 specifies a 7-column table (`ID`, `Severity`, `Deviation`, `Upstream Quote`, `Downstream Quote`, `Impact`, `Recommended Correction`). The column names also differ (`Spec Quote`/`Roadmap Quote` vs `Upstream Quote`/`Downstream Quote`). Which schema is canonical?
**Impact**: Medium — affects prompt builders, gate parsers, and report consumers.
**Resolution Target**: Before implementation begins.
*Source: Extracted inconsistency between FR-051.1 and FR-051.4*

### OQ-007: Multi-Agent Mode Specification Gap
FR-051.1 AC-16 references "multi-agent mode" with conservative severity resolution, but no other part of the spec defines how multi-agent mode is invoked, how agents are coordinated, or how individual agent reports are merged before severity conflict resolution.
**Impact**: Medium — under-specified feature that could block implementation.
**Resolution Target**: Before Phase 2 implementation.
*Source: FR-051.1 AC-16*

### OQ-008: Step Timeout vs. NFR Mismatch
FR-051.1 AC-11 specifies a step timeout of 600 seconds, but NFR-051.1 requires the step to complete within 120 seconds. The 600s timeout allows runs 5x longer than the NFR target. Should the timeout be reduced, or does the NFR represent a p95 target while 600s is the hard cutoff?
**Impact**: Low — operational, but NFR measurement needs clarification.
**Resolution Target**: During Phase 2 implementation.
*Source: FR-051.1 AC-11 vs NFR-051.1*
