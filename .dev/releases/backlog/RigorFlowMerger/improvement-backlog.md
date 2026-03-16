---
deliverable: D-0035-improvement-backlog
sprint: cross-framework-deep-analysis
generated: 2026-03-15
schema_source: artifacts/D-0030/spec.md
schema_validated: true
schema_incompatibilities: 0
source_plan: artifacts/D-0034/spec.md
approving_gate: SC-007
total_items: 31
items_by_priority:
  P0: 13
  P1: 11
  P2: 7
sc_roadmap_compatible: true
---

# IronClaude Cross-Framework Deep Analysis — Improvement Backlog

## Schema Compliance Statement

This document is produced in accordance with the `/sc:roadmap` ingestion schema pre-validated in `artifacts/D-0030/spec.md`. All 31 items conform to the extraction pipeline requirements: behavioral change descriptions (FR-extractable), explicit priority signals (P0/P1/P2), acceptance criteria (success_criteria), risk statements (risks field), and dependency references (dependencies field). Zero schema incompatibilities per D-0030.

Source document: `artifacts/D-0034/spec.md` (final-improve-plan.md — Phase 8 validated, SC-007 PASS)

---

## Priority P0 — Gate Integrity (13 items)

### RP-001 — Fail-Closed Gate Semantics in execute_roadmap

**Priority**: P0
**Effort**: S
**Component**: Roadmap Pipeline
**Classification**: strengthen existing code

**Change description**:
The `execute_roadmap()` function shall verify that any non-affirmative-PASS gate result is treated as FAIL. The gate call site shall be annotated with: `# fail-closed: inconclusive result is FAIL per D-0022 Principle 2`. The `gate_passed()` function shall return `(False, reason)` for all non-PASS paths including timeouts, parse failures, and empty output files.

Files:
- `src/superclaude/cli/roadmap/executor.py` — annotate gate call site; treat all non-PASS as FAIL
- `src/superclaude/cli/pipeline/gates.py` — confirm `gate_passed()` returns `(False, reason)` for all non-PASS paths

**Acceptance criteria**: `gate_passed()` returns `(False, ...)` for empty output files, malformed YAML, and timeout conditions; no executor.py call site treats a non-PASS as soft warning.
**Risk**: Low — targeted annotation and assertion; no gate logic restructuring required.
**Dependencies**: None (prerequisite for RP-003). Traceability: D-0022 Principle 2 direction 1.

---

### CA-001 — Presumption of Falsehood in Audit Agent Instructions

**Priority**: P0
**Effort**: S
**Component**: Cleanup-Audit CLI
**Classification**: strengthen existing code

**Change description**:
The audit-scanner.md agent definition shall add a behavioral instruction establishing UNVERIFIED as the default classification status until evidence is gathered, and requiring explicit documentation of "no importers found" findings. The audit-validator.md agent definition shall add an instruction to treat all scanner findings as unverified claims and document when confirmation evidence is absent.

Files:
- `src/superclaude/agents/audit-scanner.md` — add UNVERIFIED default classification instruction
- `src/superclaude/agents/audit-validator.md` — add absence-of-evidence documentation instruction
- `.claude/agents/audit-scanner.md` — sync copy
- `.claude/agents/audit-validator.md` — sync copy

**Acceptance criteria**: audit-scanner.md contains "UNVERIFIED" as default classification state; audit-validator.md contains explicit absence-of-evidence documentation instruction.
**Risk**: Low — agent instruction additions; no runtime behavior change.
**Dependencies**: None (prerequisite for CA-002). Traceability: D-0022 Principle 1 direction 2.

---

### CA-002 — Mandatory Negative Evidence Documentation

**Priority**: P0
**Effort**: S
**Component**: Cleanup-Audit CLI
**Classification**: strengthen existing code

**Change description**:
The scanner schema shall add an optional `negative_evidence` field to the Phase 1 schema for zero-reference findings. The `classify_finding()` function shall set a `negative_evidence_documented` flag on ClassificationResult when `has_references=False`. The cleanup audit executor shall assert all REVIEW/DELETE zero-reference findings have `negative_evidence_documented=True` and log a warning when absent.

Files:
- `src/superclaude/cli/audit/scanner_schema.py` — add optional `negative_evidence` field
- `src/superclaude/cli/audit/classification.py` — set flag in `classify_finding()` for zero-reference findings
- `src/superclaude/cli/cleanup_audit/executor.py` — assert flag on REVIEW/DELETE zero-reference findings

**Acceptance criteria**: `classify_finding()` sets flag on zero-reference findings; executor warns when flag absent; test verifies flag set correctly.
**Risk**: Low — additive field and flag; no existing classification paths altered.
**Dependencies**: CA-001. Traceability: D-0022 Principle 1 direction 3.

---

### SE-001 — Fail-Closed Gate Completion Logic

**Priority**: P0
**Effort**: S
**Component**: Sprint Executor
**Classification**: strengthen existing code

**Change description**:
The `execute_phase_tasks()` function shall check for affirmative evidence (gate passed + output file present and non-empty + no BLOCKED state); inconclusive results shall be treated as FAIL. The code shall include the comment `# fail-closed: inconclusive task completion = FAIL per D-0022 Principle 2`. The `gate_passed()` function shall return `(False, "empty output file")` for zero-byte output. All gate results shall be destructured as `(passed, reason)` and reason shall be logged even when passed=True.

Files:
- `src/superclaude/cli/sprint/executor.py` — fail-closed affirmative-evidence check; destructure all gate results
- `src/superclaude/cli/pipeline/gates.py` — confirm zero-byte returns `(False, "empty output file")`

**Acceptance criteria**: `gate_passed()` returns `(False, "empty output file")` for zero-byte; sprint executor logs gate reasons; no code path treats inconclusive gate as PASS.
**Risk**: Low — targeted assertion and logging additions.
**Dependencies**: None (prerequisite for SE-002, SE-003, SE-004, SE-005). Traceability: D-0022 Principle 2 direction 1.

---

### PM-001 — Filesystem-Verified Flag in SelfCheckProtocol

**Priority**: P0
**Effort**: S
**Component**: PM Agent
**Classification**: strengthen existing code

**Change description**:
The `validate()` method shall add a `filesystem_verified: bool` field to its return value. This field shall be True only when the `artifact_path` key exists in the implementation dict and the file exists on disk. A fifth validation question shall be added: "Is there a filesystem-verifiable artifact proving completion?" Tests shall verify `filesystem_verified=False` when `artifact_path` is absent and `filesystem_verified=True` when the path exists.

Files:
- `src/superclaude/pm_agent/self_check.py` — add `filesystem_verified` field to `validate()` return; add 5th validation question
- `tests/pm_agent/` — tests for `filesystem_verified` behavior

**Acceptance criteria**: `validate()` returns result with `filesystem_verified` field; STRICT-tier fails if False; tests pass.
**Risk**: Low — additive return field; no existing validation logic removed.
**Dependencies**: None (prerequisite for PM-002, PM-004). Traceability: D-0022 Principle 1 direction 1.

---

### PM-002 — Mandatory Negative Evidence Documentation in SelfCheckProtocol

**Priority**: P0
**Effort**: S
**Component**: PM Agent
**Classification**: strengthen existing code

**Change description**:
The `validate()` method shall record negative findings explicitly as `"no_hallucination_signals_found"` and shall add a `negative_evidence` list to the return structure for confirmed-absent conditions. A clean validation shall produce a non-empty `negative_evidence` list.

Files:
- `src/superclaude/pm_agent/self_check.py` — add `negative_evidence` list to return structure; record confirmed-absent findings

**Acceptance criteria**: `validate()` returns `issues` list and `negative_evidence` list; clean validation produces non-empty `negative_evidence` list; tests verify.
**Risk**: Low — additive return field; existing validation logic unchanged.
**Dependencies**: PM-001. Traceability: D-0022 Principle 1 direction 3.

---

### AP-001 — Ambient Sycophancy Detection in Agent Definitions

**Priority**: P0
**Effort**: M
**Component**: Adversarial Pipeline
**Classification**: add new code

**Change description**:
The quality-engineer.md and self-review.md agent definitions shall add a "Sycophancy Detection NFR" section containing: a 12-category sycophancy risk taxonomy, non-linear multipliers (1.0×/1.3×/1.5× for low/medium/high sycophancy-risk contexts), and a four-tier response routing system. All instructions shall be actionable, not stubs.

Files:
- `.claude/agents/quality-engineer.md` — add Sycophancy Detection NFR section
- `src/superclaude/agents/quality-engineer.md` — source copy
- `.claude/agents/self-review.md` — add Sycophancy Detection NFR section
- `src/superclaude/agents/self-review.md` — source copy

**Acceptance criteria**: Both agent files contain "Sycophancy Detection NFR" section with 12-category taxonomy and four-tier routing; actionable instructions (not stubs).
**Risk**: Low — agent instruction additions; no runtime behavior change.
**Dependencies**: None (prerequisite for TU-003). Traceability: D-0022 Principle 5 direction 2.

---

### TU-001 — CRITICAL FAIL Conditions for Unconditional Gate Failure

**Priority**: P0
**Effort**: S
**Component**: Task-Unified Tier System
**Classification**: strengthen existing code

**Change description**:
A `CriticalFailCondition` dataclass shall be added. `GateCriteria` shall add a `critical_conditions: list[CriticalFailCondition]` field with default empty list. When any critical condition is matched, `gate_passed()` shall return `(False, f"CRITICAL: {condition_type}")` unconditionally. The sc-task-unified-protocol SKILL.md shall document three named CRITICAL conditions for STRICT-tier tasks.

Files:
- `src/superclaude/cli/pipeline/gates.py` — add `CriticalFailCondition`; critical-condition short-circuit in `gate_passed()`
- `src/superclaude/cli/pipeline/models.py` — add `GateCriteria.critical_conditions` field
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — document three CRITICAL conditions
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — sync copy

**Acceptance criteria**: `CriticalFailCondition` exists; `GateCriteria` has `critical_conditions`; critical condition returns FAIL regardless of other criteria; SKILL.md documents three named CRITICAL conditions.
**Risk**: Low — additive dataclass and field; existing gate paths not removed.
**Dependencies**: None (prerequisite for TU-002). Traceability: D-0022 Principle 2 direction 2.

---

### QA-001 — Executor Validation Gate for All Agent Entry Points

**Priority**: P0
**Effort**: S
**Component**: Quality Agents
**Classification**: strengthen existing code

**Change description**:
The quality-engineer.md agent definition shall add a pre-execution validation checklist requiring: (a) explicit acceptance criteria list, (b) at least one file path reference, (c) compliance tier. The agent shall emit BLOCKED if any field is absent. The self-review.md agent shall add pre-execution validation requiring artifact path and completion claim. The audit-validator.md agent shall add a minimum sample size check: BLOCKED for fewer than 3 items.

Files:
- `.claude/agents/quality-engineer.md` — add 3-field pre-execution checklist; BLOCKED on absent fields
- `src/superclaude/agents/quality-engineer.md` — sync copy
- `.claude/agents/self-review.md` — add artifact path + completion claim validation
- `src/superclaude/agents/self-review.md` — sync copy
- `.claude/agents/audit-validator.md` — add minimum sample size check

**Acceptance criteria**: quality-engineer.md has 3-field checklist; self-review.md has artifact path check; audit-validator.md has minimum sample check; all dev copies synced.
**Risk**: Low — agent instruction additions; no runtime behavior change.
**Dependencies**: None (prerequisite for QA-002). Traceability: D-0022 Principle 5 direction 6.

---

### QA-002 — Typed State Transitions for Sequential Agent Invocation

**Priority**: P0
**Effort**: M
**Component**: Quality Agents
**Classification**: add new code

**Change description**:
An `AgentHandoffState` enum shall be added with values: `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`, `VALIDATED`. The sprint executor shall emit `TASK_READY` before quality-engineer invocation, and `EXECUTION_COMPLETE` or `BLOCKED` after. Transitions shall be logged to the sprint result file. The pm-agent.md agent definition shall document the typed handoff states.

Files:
- `src/superclaude/cli/pipeline/models.py` — add `AgentHandoffState` enum
- `src/superclaude/cli/sprint/executor.py` — emit handoff states; log transitions
- `.claude/agents/pm-agent.md` — document typed handoff states
- `src/superclaude/agents/pm-agent.md` — sync copy

**Acceptance criteria**: `AgentHandoffState` enum exists in models.py; sprint executor emits TASK_READY before quality-engineer invocation; BLOCKED emitted when agent cannot proceed; pm-agent.md documents states.
**Risk**: Medium — new enum and emission logic; integration test required.
**Dependencies**: QA-001. Traceability: D-0022 Principle 5 direction 5.

---

### PA-001 — Pre-Packaged Artifact Collection Before Diagnostic Runs

**Priority**: P0
**Effort**: M
**Component**: Pipeline Analysis Subsystem
**Classification**: strengthen existing code

**Change description**:
The `run_diagnostic_chain()` function shall be refactored to separate collection from analysis. A `collect_diagnostic_artifacts(failure_context) -> DiagnosticArtifactBundle` function shall be added. The `DiagnosticArtifactBundle` dataclass shall contain fields: `gate_outputs`, `step_results`, `phase_context`, `collected_at`. Analysis stages shall operate on bundle fields, not raw failure context.

Files:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — add `collect_diagnostic_artifacts()`; add `DiagnosticArtifactBundle`; refactor `run_diagnostic_chain()`

**Acceptance criteria**: `collect_diagnostic_artifacts()` exists; `DiagnosticArtifactBundle` exists; `run_diagnostic_chain()` calls collection before analysis; analysis stages operate on bundle fields.
**Risk**: Medium — internal refactor of diagnostic chain; existing API preserved.
**Dependencies**: None (prerequisite for PA-002, PA-003). Traceability: D-0022 Principle 3 direction 4.

---

### PA-002 — Framework-vs-Project Diagnostic Distinction in Output

**Priority**: P0
**Effort**: S
**Component**: Pipeline Analysis Subsystem
**Classification**: strengthen existing code

**Change description**:
A `failure_source: Literal["framework", "project", "unknown"]` field shall be added to `DiagnosticReport`. Classification logic: .md input file failure → "project"; pipeline step exception → "framework"; ambiguous → "unknown". The `failure_source` shall appear prominently in the stage 4 diagnostic summary.

Files:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — add `failure_source` field to `DiagnosticReport`; implement classification logic; surface in stage 4 summary

**Acceptance criteria**: `DiagnosticReport` has `failure_source` field; stage 4 summary includes failure_source prominently; test verifying .md failure → "project" and pipeline step exception → "framework".
**Risk**: Low — additive field; classification logic is deterministic.
**Dependencies**: PA-001. Traceability: D-0022 Principle 5 direction 7.

---

## Priority P1 — Evidence Verification / Typed Coordination (11 items)

### RP-002 — Documented Fallback Degradation Path

**Priority**: P1
**Effort**: XS
**Component**: Roadmap Pipeline
**Classification**: strengthen existing code

**Change description**:
The sc-roadmap-protocol SKILL.md shall add a "Fallback Degradation" section containing at least three explicit trigger/behavior pairs covering: invalid `--agents` spec, absent output file after timeout, and missing/corrupt `.roadmap-state.json`. The executor.py shall add an inline comment block at the `_apply_resume()` call site referencing "See SKILL.md §Fallback Degradation."

Files:
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — add Fallback Degradation section with ≥3 trigger/behavior pairs
- `src/superclaude/cli/roadmap/executor.py` — add comment at `_apply_resume()` call site

**Acceptance criteria**: SKILL.md has Fallback Degradation section with ≥3 trigger/behavior pairs; executor.py has comment at resume call site.
**Risk**: Low — documentation and comment addition; no logic change.
**Dependencies**: None. Traceability: D-0022 Principle 3 direction 5.

---

### CA-003 — Typed State Transitions in Audit Pass Progression

**Priority**: P1
**Effort**: M
**Component**: Cleanup-Audit CLI
**Classification**: add new code

**Change description**:
An `AuditPassState` enum shall be defined with values: `PENDING`, `SCANNING`, `SCAN_COMPLETE`, `ANALYZING`, `ANALYSIS_COMPLETE`, `VALIDATING`, `DONE`, `BLOCKED`. The executor shall emit current state at each G-001 → G-002 → G-003 transition and emit `BLOCKED` with reason on empty result set. `AuditPassState` shall be added to the models module export list.

Files:
- `src/superclaude/cli/cleanup_audit/executor.py` — add `AuditPassState` enum; emit states at transitions; emit BLOCKED with reason on empty result
- `src/superclaude/cli/pipeline/models.py` — add `AuditPassState` to module export list

**Acceptance criteria**: `AuditPassState` enum exists in executor.py; BLOCKED emitted on empty result; G-001/G-002/G-003 transitions log current state.
**Risk**: Medium — new enum and emission logic; integration test required.
**Dependencies**: CA-001, CA-002. Traceability: D-0022 Principle 5 direction 5.

---

### CA-004 — Executor Validation Gate Before Agent Invocation

**Priority**: P1
**Effort**: S
**Component**: Cleanup-Audit CLI
**Classification**: strengthen existing code

**Change description**:
The `execute_cleanup_audit()` function shall validate at entry: (a) target directory exists and is readable, (b) `--batch-size` is in range 1–100, (c) `--focus` value is a known value. On failure, it shall emit `AuditPassState.BLOCKED` with reason and fail-fast. CLI-level validation in commands.py shall complement (not replace) executor-level validation.

Files:
- `src/superclaude/cli/cleanup_audit/executor.py` — add entry validation; emit BLOCKED with reason on invalid inputs
- `src/superclaude/cli/cleanup_audit/commands.py` — complement CLI-level validation

**Acceptance criteria**: `execute_cleanup_audit()` validates inputs before first pass; invalid target path returns BLOCKED immediately; unit test for each validation condition.
**Risk**: Low — validation additions; fail-fast before any agent invocation.
**Dependencies**: CA-003. Traceability: D-0022 Principle 5 direction 6.

---

### SE-002 — Per-Item UID Tracking for Sub-Phase Restartability

**Priority**: P1
**Effort**: M
**Component**: Sprint Executor
**Classification**: add new code

**Change description**:
A `task_uid: str` field shall be added to task records, with UIDs generated as `f"{phase_id}-{task_index:04d}"` at phase-load time. Sub-phase resume shall be implemented: with `--start N` and a partial result file present, the executor shall re-enter at the first task with status != DONE. `task_uid` shall be added to the task status record in TurnLedger.

Files:
- `src/superclaude/cli/sprint/executor.py` — add `task_uid` field; implement sub-phase resume logic
- `src/superclaude/cli/pipeline/models.py` — add `task_uid` to task status record in TurnLedger

**Acceptance criteria**: Each task has stable `task_uid` across session resets; `--start N` with partial result resumes at first non-DONE task; test verifying UID stability.
**Risk**: Medium — new field and resume logic; backward-compatible with existing result files.
**Dependencies**: SE-001. Traceability: D-0022 Principle 3 direction 1.

---

### SE-003 — Three-Mode Execution for Mid-Phase Resume

**Priority**: P1
**Effort**: M
**Component**: Sprint Executor
**Classification**: strengthen existing code

**Change description**:
An `ExecutionMode` enum shall be added with values: `NORMAL`, `INCOMPLETE_RESUME`, `CORRECTION`. The `ClaudeProcess.build_command()` method shall accept an `execution_mode` parameter and prepend mode-appropriate context for each mode. The executor shall determine the correct `ExecutionMode` per task: no prior attempt → NORMAL; partial output → INCOMPLETE_RESUME; failed gate → CORRECTION. The TurnLedger shall record the mode used.

Files:
- `src/superclaude/cli/sprint/process.py` — add `ExecutionMode` enum; update `build_command()` to accept and use mode
- `src/superclaude/cli/sprint/executor.py` — determine and set `ExecutionMode` per task; record in TurnLedger

**Acceptance criteria**: `ExecutionMode` enum exists; `build_command()` accepts and uses mode; TurnLedger records mode; integration test verifying INCOMPLETE_RESUME produces different prompt than NORMAL.
**Risk**: Medium — new parameter and mode-dispatch logic; existing NORMAL path unchanged.
**Dependencies**: SE-001, SE-002. Traceability: D-0022 Principle 3 direction 2.

---

### PM-004 — ReflexionPattern: Presumption of Falsehood Default Stance

**Priority**: P1
**Effort**: S
**Component**: PM Agent
**Classification**: strengthen existing code

**Change description**:
The `get_solution()` method shall add a `confidence: float` field to its return value. New solutions shall default to `confidence=0.5`. Solutions verified via `record_error()` with `verified=True` shall reach `confidence=0.8+`. Callers shall check `confidence >= 0.7` before auto-applying solutions. The `record_error()` method shall add a `verified: bool = False` parameter.

Files:
- `src/superclaude/pm_agent/reflexion.py` — add `confidence` to `get_solution()` return; add `verified` parameter to `record_error()`

**Acceptance criteria**: `get_solution()` returns result with `confidence` field; new solutions default to 0.5; verified solutions reach ≥0.8; callers can check confidence before auto-applying.
**Risk**: Low — additive return field and parameter; existing callers unaffected unless they check confidence.
**Dependencies**: PM-001. Traceability: D-0022 Principle 1 direction 1.

---

### AP-002 — CEV Vocabulary Extension to All Verification Outputs

**Priority**: P1
**Effort**: S
**Component**: Adversarial Pipeline
**Classification**: strengthen existing code

**Change description**:
The sc-task-unified-protocol SKILL.md shall add to STRICT tier instructions the CEV format requirement: `[CLAIM] — [EVIDENCE:file:line] — [VERDICT: confirmed|rejected|inconclusive]`. The quality-engineer.md agent definition shall add the same CEV output format requirement. At least one example shall be shown in each file.

Files:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — add CEV format requirement in STRICT tier; include example
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — sync copy
- `.claude/agents/quality-engineer.md` — add CEV output format requirement; include example

**Acceptance criteria**: sc-task-unified-protocol/SKILL.md contains CEV format requirement in STRICT tier; quality-engineer.md contains CEV output format; at least one example shown in each file.
**Risk**: Low — documentation additions to skill and agent files.
**Dependencies**: AP-001. Traceability: D-0022 Principle 1 direction 4.

---

### AP-003 — Four-Category Failure Classification in Adversarial Debate Outputs

**Priority**: P1
**Effort**: S
**Component**: Adversarial Pipeline
**Classification**: strengthen existing code

**Change description**:
The sc-adversarial-protocol scoring-protocol.md shall add a "Failure Mode Classification" section with four categories: (1) Execution failures, (2) Template failures, (3) Evidence failures, (4) Workflow failures. Each category shall include at least one example. Failures shall be classified before scoring. The dev copy shall be synced.

Files:
- `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` — add Failure Mode Classification section with four categories and examples
- `src/superclaude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` — sync copy

**Acceptance criteria**: scoring-protocol.md has "Failure Mode Classification" section with all four categories; each category has ≥1 example; dev copy synced.
**Risk**: Low — documentation addition to scoring-protocol.md.
**Dependencies**: AP-002. Traceability: D-0022 Principle 5 direction 4.

---

### TU-002 — Output-Type-Specific Gate Application

**Priority**: P1
**Effort**: M
**Component**: Task-Unified Tier System
**Classification**: add new code

**Change description**:
The sc-task-unified-protocol SKILL.md shall add an `output_type` column to the verification routing table with four output types: code (compile/test required), analysis (evidence citation required), documentation (structure check only), opinion (CEV structure required). The sc-tasklist-protocol tier-classification.md shall add output-type detection rules for *.md → documentation; analysis report → analysis; code changes → code. Documentation tasks shall skip code verification.

Files:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — add output_type column to verification routing table
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — sync copy
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — add output-type detection rules for ≥3 output types
- `src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md` — sync copy

**Acceptance criteria**: tier-classification.md has output-type detection rules for ≥3 output types; SKILL.md verification table has output_type column; documentation tasks skip code verification.
**Risk**: Medium — new routing table column; integration with existing tier classification logic required.
**Dependencies**: TU-001. Traceability: D-0022 Principle 2 direction 3.

---

### TU-003 — Six Universal Quality Principles as Verification Agent Vocabulary

**Priority**: P1
**Effort**: S
**Component**: Task-Unified Tier System
**Classification**: strengthen existing code

**Change description**:
The quality-engineer.md agent definition shall add a "Quality Principles NFR" section with six named principles: Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy. Each principle shall include an IC-specific application example for STRICT-tier verification. The dev copy shall be synced.

Files:
- `.claude/agents/quality-engineer.md` — add Quality Principles NFR section with six principles and IC-specific examples
- `src/superclaude/agents/quality-engineer.md` — sync copy

**Acceptance criteria**: quality-engineer.md has "Quality Principles NFR" section with all six principles named and described; each has IC-specific application example; dev copy synced.
**Risk**: Low — agent instruction additions.
**Dependencies**: AP-001. Traceability: D-0022 Principle 5 direction 1.

---

### PA-003 — 4-Category Failure Classification in DiagnosticReport

**Priority**: P1
**Effort**: S
**Component**: Pipeline Analysis Subsystem
**Classification**: strengthen existing code

**Change description**:
A `FailureCategory` enum shall be added with values: `EXECUTION_FAILURE`, `TEMPLATE_FAILURE`, `EVIDENCE_FAILURE`, `WORKFLOW_FAILURE`. A `ConfidenceLevel` enum shall be added. A `failure_categories: list[tuple[FailureCategory, ConfidenceLevel]]` field shall be added to `DiagnosticReport`. Each failure shall be categorized before reporting.

Files:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — add `FailureCategory` enum; add `failure_categories` to `DiagnosticReport`
- `src/superclaude/cli/pipeline/models.py` — add `FailureCategory` and `ConfidenceLevel` enums

**Acceptance criteria**: `FailureCategory` and `ConfidenceLevel` enums exist; `DiagnosticReport` has `failure_categories`; each failure categorized; test verifying ≥2 category types distinguishable.
**Risk**: Medium — new enum and field; existing diagnostic report consumers need field-presence check.
**Dependencies**: PA-001, PA-002. Traceability: D-0022 Principle 5 direction 4.

---

## Priority P2 — Restartability / Bounded Complexity / Schema Reliability (7 items)

### RP-003 — Per-Track State Machine Formalization

**Priority**: P2
**Effort**: M
**Component**: Roadmap Pipeline
**Classification**: strengthen existing code

**Change description**:
The `StepStatus` enum shall be extended with values: `PENDING`, `IN_PROGRESS`, `DONE`, `FAILED`, `SKIPPED`. Steps shall be constructed with `status=StepStatus.PENDING`, transition to IN_PROGRESS during execution, and transition to DONE or FAILED after gate evaluation. The `_apply_resume()` function shall read `StepStatus.DONE` as the skip criterion.

Files:
- `src/superclaude/cli/pipeline/models.py` — extend `StepStatus` enum with 5 states
- `src/superclaude/cli/roadmap/executor.py` — set PENDING at construction; transition IN_PROGRESS → DONE/FAILED; resume skips DONE only

**Acceptance criteria**: `StepStatus` enum has all 5 states; gate failure → FAILED not IN_PROGRESS; `--resume` skips DONE steps only.
**Risk**: Medium — enum extension and state machine transitions; resume logic change requires testing.
**Dependencies**: RP-001. Traceability: D-0022 Principle 3 direction 3.

---

### RP-004 — Hard Resource Caps Formalization

**Priority**: P2
**Effort**: S
**Component**: Roadmap Pipeline
**Classification**: add new code

**Change description**:
A `MAX_PARALLEL_STEPS = 4` constant shall be added to executor.py with a documentation comment. CLI validation shall reject `--agents` values producing more than `MAX_PARALLEL_STEPS` agent specs. A `--max-parallel` CLI option shall be added with default value `MAX_PARALLEL_STEPS` and range 1–8.

Files:
- `src/superclaude/cli/roadmap/executor.py` — add `MAX_PARALLEL_STEPS` constant with comment; validation for `--agents`
- `src/superclaude/cli/roadmap/commands.py` — add `--max-parallel` option (default: MAX_PARALLEL_STEPS, range 1–8)

**Acceptance criteria**: `MAX_PARALLEL_STEPS` constant exists with documentation comment; CLI rejects >MAX_PARALLEL_STEPS agent specs; `--max-parallel` is wired and validated.
**Risk**: Low — new constant and CLI option; additive to existing CLI.
**Dependencies**: None. Traceability: D-0022 Principle 4 direction 2.

---

### SE-004 — Auto-Trigger Diagnostic on N Consecutive Gate Failures

**Priority**: P2
**Effort**: M
**Component**: Sprint Executor
**Classification**: add new code

**Change description**:
An `auto_diagnostic_threshold: int = 3` parameter shall be added to the sprint executor. When the consecutive failure count reaches the threshold, `run_diagnostic_chain()` from `diagnostic_chain.py` shall be invoked. The counter shall reset after invocation. A `--auto-diagnostic-threshold N` CLI option shall be added (default 3, range 1–10). The diagnostic chain shall accept the sprint executor failure context format.

Files:
- `src/superclaude/cli/sprint/executor.py` — add `auto_diagnostic_threshold`; invoke `run_diagnostic_chain()` on threshold; reset counter
- `src/superclaude/cli/sprint/commands.py` — add `--auto-diagnostic-threshold` CLI option
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — verify acceptance of sprint executor failure context

**Acceptance criteria**: `execute_sprint()` has `auto_diagnostic_threshold` parameter; `run_diagnostic_chain()` invoked after N failures; diagnostic result logged to sprint results directory; CLI option wired.
**Risk**: Medium — new trigger logic; integration with existing diagnostic chain required.
**Dependencies**: SE-001. Traceability: D-0022 Principle 5 direction 3.

---

### SE-005 — Three-Tier Severity for Gate Failure Reports

**Priority**: P2
**Effort**: S
**Component**: Sprint Executor
**Classification**: add new code

**Change description**:
A `GateFailureSeverity` enum shall be added with values: `SEV1_BLOCK`, `SEV2_CYCLE`, `SEV3_ADVISORY`. A `severity: GateFailureSeverity` field shall be added to `StepResult` when status == FAILED. After `gate_passed()` returns `(False, reason)`, the severity shall be classified based on tier. Sev 1 failures shall be surfaced prominently in the TUI. Severity shall be logged alongside gate failure reason.

Files:
- `src/superclaude/cli/pipeline/models.py` — add `GateFailureSeverity` enum; add `severity` to `StepResult`
- `src/superclaude/cli/pipeline/gates.py` — classify into `GateFailureSeverity` after gate failure
- `src/superclaude/cli/sprint/executor.py` — log severity; surface Sev 1 prominently in TUI

**Acceptance criteria**: `GateFailureSeverity` enum exists; STRICT-tier failures default to SEV1_BLOCK; STANDARD-tier may classify as SEV2_CYCLE with partial output; severity logged in sprint result files.
**Risk**: Low — new enum and field; TUI display enhancement.
**Dependencies**: SE-001. Traceability: D-0022 Principle 4 direction 3.

---

### PM-003 — Model Tier Proportionality for PM Agent Operations

**Priority**: P2
**Effort**: XS
**Component**: PM Agent
**Classification**: strengthen existing code

**Change description**:
A module-level docstring shall be added to `pm_agent/__init__.py` documenting the tier policy: Haiku for routine checks, Sonnet for structural validation, Opus for critical cross-session learning at confidence <0.70. The pm-agent.md agent definition shall add a "Model Tier Policy" section specifying the same tiers.

Files:
- `src/superclaude/pm_agent/__init__.py` — add module-level docstring with tier policy
- `.claude/agents/pm-agent.md` — add Model Tier Policy section

**Acceptance criteria**: `pm_agent/__init__.py` contains tier policy docstring; `pm-agent.md` has "Model Tier Policy" section; tier rules named explicitly.
**Risk**: Low — documentation additions only.
**Dependencies**: None. Traceability: D-0022 Principle 4 direction 1.

---

### QA-003 — Model Tier Proportionality Policy for Quality Agents

**Priority**: P2
**Effort**: XS
**Component**: Quality Agents
**Classification**: strengthen existing code

**Change description**:
The quality-engineer.md agent definition shall add a "Model Tier Policy" section specifying: Sonnet tier as primary; Opus escalation for >5-file STRICT tasks or security paths; Haiku not appropriate. The audit-validator.md agent definition shall add a "Model Tier Policy" section specifying: Haiku tier (10% spot-check validation). The self-review.md agent definition shall add a "Model Tier Policy" section specifying: Haiku for routine; Sonnet for STRICT implementation reviews. All dev copies shall be synced.

Files:
- `.claude/agents/quality-engineer.md` — add Model Tier Policy section
- `src/superclaude/agents/quality-engineer.md` — sync copy
- `.claude/agents/audit-validator.md` — add Model Tier Policy section
- `.claude/agents/self-review.md` — add Model Tier Policy section
- `src/superclaude/agents/self-review.md` — sync copy

**Acceptance criteria**: All three agent .md files have "Model Tier Policy" section; each specifies primary tier and escalation conditions; all dev copies synced.
**Risk**: Low — agent instruction additions only.
**Dependencies**: None. Traceability: D-0022 Principle 4 direction 1.

---

### TU-004 — Confidence Threshold <0.70 Explicit Blocking

**Priority**: P2
**Effort**: XS
**Component**: Task-Unified Tier System
**Classification**: strengthen existing code

**Change description**:
The sc-task-unified-protocol SKILL.md shall clarify that confidence <0.70 causes task classification to be BLOCKED pending user confirmation. The blocking message shall include the computed tier, competing tier, and keywords causing the split. No code path shall proceed without confirmation at <0.70. The sc-tasklist-protocol tier-classification.md shall add an explicit blocking message format for low-confidence classifications.

Files:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — clarify confidence <0.70 blocks execution; document blocking message format
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — sync copy
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — add blocking message format for low-confidence classifications

**Acceptance criteria**: SKILL.md specifies confidence <0.70 blocks execution pending user confirmation; blocking message format includes tier, competing tier, and keywords; no code path proceeds without confirmation at <0.70.
**Risk**: Low — documentation clarification; no runtime logic change.
**Dependencies**: None. Traceability: D-0022 Principle 2.

---

### PA-004 — Hard Resource Caps for Recursive Pipeline Analysis

**Priority**: P2
**Effort**: XS
**Component**: Pipeline Analysis Subsystem
**Classification**: add new code

**Change description**:
A `MAX_DIAGNOSTIC_DEPTH = 4` constant shall be added to diagnostic_chain.py. Recursive diagnostic invocation at depth > 1 shall be blocked with a clear error message. A `MAX_FMEA_DELIVERABLES = 50` constant shall be added to combined_m2_pass.py; if exceeded, only the first 50 deliverables shall be processed and the cap shall be documented referencing D-0022 Principle 4.

Files:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — add `MAX_DIAGNOSTIC_DEPTH`; block recursive invocation at depth >1
- `src/superclaude/cli/pipeline/combined_m2_pass.py` — add `MAX_FMEA_DELIVERABLES`; enforce cap with documentation

**Acceptance criteria**: `MAX_DIAGNOSTIC_DEPTH` exists; recursive diagnostic blocked at depth >1; `MAX_FMEA_DELIVERABLES` exists with documented behavior for oversized inputs.
**Risk**: Low — new constants and guards; additive to existing logic.
**Dependencies**: None. Traceability: D-0022 Principle 4 direction 2.

---

## Recommended Execution Sequence

Per D-0028 dependency graph (validated D-0032 Dimension 6):

**Phase A (parallel — all P0 gate integrity, no cross-component prerequisites)**:
RP-001, CA-001, SE-001, PM-001, AP-001, TU-001, QA-001, PA-001

**Phase B (parallel — P0/P1 items depending only on own-component P0 item)**:
RP-002, CA-002, SE-002, PM-002, AP-002, TU-002, QA-002, PA-002

**Phase C (parallel — P1 items with cross-P1 dependencies)**:
PA-003, SE-003, CA-003, PM-004, AP-003, TU-003, CA-004

**Phase D (parallel — P2 optional refinements)**:
PA-004, SE-004, SE-005, PM-003, QA-003, TU-004, RP-003, RP-004

---

## Summary Counts

| Priority | Items | Effort Breakdown |
|---|---|---|
| P0 | 13 | XS:0, S:9, M:4, L:0 |
| P1 | 11 | XS:1, S:6, M:4, L:0 |
| P2 | 7 | XS:4, S:2, M:1, L:0 |
| **Total** | **31** | XS:5, S:17, M:9, L:0 |

Components covered: Roadmap Pipeline (4), Cleanup-Audit CLI (4), Sprint Executor (5), PM Agent (4), Adversarial Pipeline (3), Task-Unified Tier System (4), Quality Agents (3), Pipeline Analysis Subsystem (4).
