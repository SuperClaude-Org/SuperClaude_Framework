---
component: pipeline-analysis
deliverable: D-0026
source_comparison: comparison-pipeline-analysis.md
verdict: IC stronger
principle_primary: Deterministic Gates
principle_secondary: Restartability
generated: 2026-03-15
---

# Improvement Plan: Pipeline Analysis Subsystem

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM PA-001 — Pre-Packaged Artifact Collection Before Diagnostic Runs

**Priority**: P0
**Effort**: M
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's pattern of assembling all relevant artifacts before analysis begins, not LW's bash-based artifact collection system
**Why not full import**: LW's pre-packaged artifact collection uses bash file-gathering scripts and grep-based pattern matching (explicitly rejected in D-0022 Principle 2); IC needs only the sequential ordering (collect then analyze) applied to `run_diagnostic_chain()`.

**File paths and change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Refactor `run_diagnostic_chain()` to separate artifact collection from analysis. Add a `collect_diagnostic_artifacts(failure_context) -> DiagnosticArtifactBundle` function that reads all relevant files (gate output files, step result files, prior phase results) into memory before any analysis begins. The analysis stages then operate on the bundle, not on live files. This ensures the diagnostic has a consistent evidence snapshot even if the pipeline continues running.
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `DiagnosticArtifactBundle` dataclass: `gate_outputs: list[str]`, `step_results: list[StepResult]`, `phase_context: dict`, `collected_at: datetime`.

**Rationale**: D-0022 Principle 3 (Restartability), direction 4: "IC's diagnostic chain should adopt LW's pattern of assembling all relevant artifacts before analysis begins... Pre-packaging ensures the diagnostic has a complete, consistent evidence snapshot even if the pipeline continues running."

**Dependencies**: None
**Acceptance criteria**: `collect_diagnostic_artifacts()` function exists in diagnostic_chain.py; `DiagnosticArtifactBundle` dataclass exists; `run_diagnostic_chain()` calls collection before analysis; analysis stages operate on bundle fields, not on live file reads.
**Risk**: Medium. Refactoring diagnostic chain; requires that the bundle covers all artifact types currently read during analysis. Risk of missing an artifact type during collection.

---

## ITEM PA-002 — Framework-vs-Project Diagnostic Distinction in Output

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's framework-vs-project failure distinction as an output format addition to IC's diagnostic chain, not LW's grep-based bash failure classification
**Why not full import**: LW's framework-vs-project distinction is implemented through bash grep pattern matching (explicitly rejected in D-0022 Principle 2); IC needs only the distinction as a classification field in the `DiagnosticReport` output structure.

**File paths and change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `failure_source: Literal["framework", "project", "unknown"]` field to `DiagnosticReport`. The classification logic: if the failing gate is for a task specification (`.md` input file) → `"project"`; if the failing gate is for a pipeline step (Python code execution) → `"framework"`; if ambiguous → `"unknown"`.
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — In the summary stage (stage 4), include the `failure_source` prominently: "FRAMEWORK ISSUE: The sprint CLI encountered an internal error. Check IC pipeline code." vs "PROJECT ISSUE: The task specification caused the failure. Check tasklist input."

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 7: "IC's diagnostic output should distinguish between sprint CLI failures (framework issues) and task specification failures (project issues)."

**Dependencies**: PA-001 (pre-packaged artifacts include the gate output context needed to classify framework vs. project)
**Acceptance criteria**: `DiagnosticReport` has `failure_source` field with three allowed values; stage 4 summary includes the failure_source prominently; test verifying that a .md input failure is classified as "project" and a pipeline step exception is classified as "framework."
**Risk**: Low. Additive field; classification logic is deterministic based on input type.

---

## ITEM PA-003 — 4-Category Failure Classification in DiagnosticReport

**Priority**: P1
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's 4-category failure taxonomy (execution, template, evidence, workflow failures) as a structured output field in IC's DiagnosticReport, not LW's point-based scoring system
**Why not full import**: LW's failure classification uses a point-based confidence scoring system (High ≥5 pts, Medium 3-4, Low ≤2) tied to its batch execution model; IC needs only the four-category labels plus the confidence level concept as a simplified tier (High/Medium/Low based on evidence count, not point arithmetic).

**File paths and change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `FailureCategory` enum: `EXECUTION_FAILURE`, `TEMPLATE_FAILURE`, `EVIDENCE_FAILURE`, `WORKFLOW_FAILURE`. Add `failure_categories: list[tuple[FailureCategory, ConfidenceLevel]]` to `DiagnosticReport` where `ConfidenceLevel` is `HIGH | MEDIUM | LOW`.
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — In the analysis stages, classify each identified failure into one of the four categories. `EXECUTION_FAILURE`: model refused, output truncated, timeout. `TEMPLATE_FAILURE`: output does not match expected gate schema. `EVIDENCE_FAILURE`: missing file:line citations, CEV violations. `WORKFLOW_FAILURE`: stage skipped, gate evaluation bypassed.
- `src/superclaude/cli/pipeline/models.py` — Add `FailureCategory` and `ConfidenceLevel` enums to models module.

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 4: "IC's current diagnostic chain produces free-text analysis without a structured classification. Adopting this taxonomy allows IC to produce scored, categorized failure reports that are actionable and comparable across runs."

**Dependencies**: PA-001 (artifact bundle provides the evidence to classify failures), PA-002 (framework/project distinction is a prerequisite context for accurate category assignment)
**Acceptance criteria**: `FailureCategory` and `ConfidenceLevel` enums exist in models.py; `DiagnosticReport` has `failure_categories` field; each failure identified by the diagnostic chain is categorized; test verifying at least two category types are distinguishable.
**Risk**: Medium. Requires that the existing free-text analysis stages are augmented with structured classification logic; staged rollout acceptable (uncategorized failures emit WORKFLOW_FAILURE as fallback).

---

## ITEM PA-004 — Hard Resource Caps for Recursive Pipeline Analysis

**Priority**: P2
**Effort**: XS
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's resource cap principle as IC configuration constants for the pipeline analysis subsystem, not LW's runtime dynamic load balancer
**Why not full import**: LW's caps are enforced by a runtime scheduler with dynamic agent scaling; IC needs only configuration constants with validation at analysis entry points.

**File paths and change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `MAX_DIAGNOSTIC_DEPTH = 4` constant (current stages: troubleshoot → adversarial × 2 → summary, matching the existing design). Add validation: if a recursive diagnostic invocation (diagnostic within a diagnostic) is attempted, block at depth > 1 with a clear error.
- `src/superclaude/cli/pipeline/combined_m2_pass.py` — Add `MAX_FMEA_DELIVERABLES = 50` constant. If `run_combined_m2_pass()` is called with more than 50 deliverables, log a warning and process only the first 50 (highest-priority by FMEA severity score). Document the cap with a comment referencing D-0022 Principle 4.

**Rationale**: D-0022 Principle 4 (Bounded Complexity), direction 2: "IC should formalize resource caps: maximum concurrent phases in sprint execution, maximum parallel steps in roadmap generation, maximum depth for recursive pipeline analysis."

**Dependencies**: None
**Acceptance criteria**: `MAX_DIAGNOSTIC_DEPTH` constant exists in diagnostic_chain.py; recursive diagnostic invocation is blocked at depth >1; `MAX_FMEA_DELIVERABLES` constant exists in combined_m2_pass.py with documented behavior for oversized inputs.
**Risk**: Low. Constants with validation checks; existing behavior is unchanged for inputs within the caps.
