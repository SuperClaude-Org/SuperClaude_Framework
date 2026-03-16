---
deliverable: D-0034
task: T08.05
title: final-improve-plan.md — Validated and Correction-Complete Improvement Portfolio
status: complete
generated: 2026-03-15
validation_approval: artifacts/D-0033/spec.md
approving_gate: SC-007
approving_gate_artifact: artifacts/D-0033/spec.md
fail_rework_corrections_applied: 0
file_paths_verified: true
file_path_verification_method: filesystem (Glob tool)
schema_compliance: confirmed — artifacts/D-0030/spec.md
total_items: 31
items_approved: 31
items_retired: 0
---

# final-improve-plan.md — Validated and Correction-Complete Improvement Portfolio

## Validation Approval Header

**APPROVED** — This improvement plan has been formally validated and approved by the Phase 8 Architecture Review Gate.

| Field | Value |
|---|---|
| Approving Gate Artifact | `artifacts/D-0033/spec.md` (validation-report.md) |
| Gate | SC-007 |
| Reviewer Role | Validation Reviewer (Phase 8) |
| Review Date | 2026-03-15 |
| Phase 8 Corrections Applied | 0 (zero Fail-Rework items from D-0033) |
| /sc:roadmap Schema Compliance | Confirmed — `artifacts/D-0030/spec.md` |
| File Paths Verified | All 33 distinct paths verified via filesystem (D-0032 Dimension 1) |
| Six-Dimension Result | All 6 dimensions PASS — `artifacts/D-0032/evidence.md` |

---

## Phase 8 Corrections

**No corrections required.** The validation-report.md (D-0033) identified zero Fail-Rework items. All 31 improvement items passed all six dimensions and all four Disqualifying Condition checks.

This section is present as required by the final-improve-plan.md format. Zero corrections applied = zero Fail-Rework items from D-0033.

---

## Retired Items

**None.** Zero items were retired during Phase 8 review. All 31 items from the Phase 7 improvement portfolio are approved for Phase 9 consumption.

---

## /sc:roadmap Schema Compliance Confirmation

Per Gate Criteria SC-007 and the pre-validation requirement established in D-0030:

This improvement portfolio is **confirmed schema-compliant** with `/sc:roadmap` ingestion expectations as established in `artifacts/D-0030/spec.md`.

Key compliance confirmations:
- All 31 items have behavioral change descriptions extractable as FRs by the 8-step extraction pipeline
- All 31 items have acceptance criteria extractable as success criteria (SC-class items)
- All 31 items have explicit risk statements extractable as RISK-class items
- All 31 items have explicit dependency references extractable as DEP-class items
- Non-requirement planning fields (`patterns_not_mass`, `Why not full import`, `Classification`) are silently ignored by the extraction pipeline without producing spurious requirements

---

## Consolidated Improvement Portfolio

All 31 validated items from the Phase 7 improvement plans, organized by structural leverage priority tier. The dependency graph from D-0028 is incorporated; all prerequisite relationships preserved.

---

### Priority P0 — Gate Integrity (13 items)

#### RP-001 — Fail-Closed Gate Semantics in execute_roadmap
**Component**: Roadmap Pipeline | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW fail-closed verdict logic adopted; bash gate mechanism rejected

**Change description**:
- `src/superclaude/cli/roadmap/executor.py` — In `execute_roadmap()`, verify any non-affirmative-PASS gate result is treated as FAIL. Annotate gate call site: `# fail-closed: inconclusive result is FAIL per D-0022 Principle 2`.
- `src/superclaude/cli/pipeline/gates.py` — Confirm `gate_passed()` returns `(False, reason)` for all non-PASS paths including timeouts and parse failures.

**Acceptance criteria**: `gate_passed()` returns `(False, ...)` for empty output files, malformed YAML, and timeout conditions; no executor.py call site treats a non-PASS as soft warning.
**Risk**: Low. Dependencies: None (prerequisite for RP-003). Traceability: D-0022 Principle 2 direction 1.

---

#### CA-001 — Presumption of Falsehood in Audit Agent Instructions
**Component**: Cleanup-Audit CLI | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW Presumption of Falsehood epistemic stance adopted; per-claim FAS -100 penalty rejected

**Change description**:
- `src/superclaude/agents/audit-scanner.md` — Add behavioral instruction: default classification status UNVERIFIED until evidence gathered; document "no importers found" explicitly.
- `src/superclaude/agents/audit-validator.md` — Add: treat all scanner findings as unverified claims; document when confirmation evidence is absent.
- `.claude/agents/audit-scanner.md` and `.claude/agents/audit-validator.md` — Sync copies.

**Acceptance criteria**: audit-scanner.md contains "UNVERIFIED" as default classification state; audit-validator.md contains explicit absence-of-evidence documentation instruction.
**Risk**: Low. Dependencies: None (prerequisite for CA-002). Traceability: D-0022 Principle 1 direction 2.

---

#### CA-002 — Mandatory Negative Evidence Documentation
**Component**: Cleanup-Audit CLI | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW mandatory negative evidence documentation adopted; PABLOV chain rejected

**Change description**:
- `src/superclaude/cli/audit/scanner_schema.py` — Add optional `negative_evidence` field to Phase 1 schema for zero-reference findings.
- `src/superclaude/cli/audit/classification.py` — In `classify_finding()`, set `negative_evidence_documented` flag on ClassificationResult when `has_references=False`.
- `src/superclaude/cli/cleanup_audit/executor.py` — Assert all REVIEW/DELETE zero-reference findings have `negative_evidence_documented=True`; log warning when absent.

**Acceptance criteria**: `classify_finding()` sets flag on zero-reference findings; executor warns when flag absent; test verifies flag set correctly.
**Risk**: Low. Dependencies: CA-001. Traceability: D-0022 Principle 1 direction 3.

---

#### SE-001 — Fail-Closed Gate Completion Logic
**Component**: Sprint Executor | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW fail-closed verdict logic adopted; bash batch state machine rejected

**Change description**:
- `src/superclaude/cli/sprint/executor.py` — In `execute_phase_tasks()`, check for affirmative evidence (gate passed + output file present and non-empty + no BLOCKED state). Inconclusive = FAIL. Add comment: `# fail-closed: inconclusive task completion = FAIL per D-0022 Principle 2`.
- `src/superclaude/cli/pipeline/gates.py` — Confirm `gate_passed()` returns `(False, "empty output file")` for zero-byte output.
- `src/superclaude/cli/sprint/executor.py` — Destructure all gate results as `(passed, reason)`; log reason even when passed=True.

**Acceptance criteria**: `gate_passed()` returns `(False, "empty output file")` for zero-byte; sprint executor logs gate reasons; no code path treats inconclusive gate as PASS.
**Risk**: Low. Dependencies: None (prerequisite for SE-002, SE-003). Traceability: D-0022 Principle 2 direction 1.

---

#### PM-001 — Filesystem-Verified Flag in SelfCheckProtocol
**Component**: PM Agent | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW claim/proof distinction adopted; full five-artifact PABLOV chain rejected

**Change description**:
- `src/superclaude/pm_agent/self_check.py` — Add `filesystem_verified: bool` to validate() return. True only when artifact_path key exists and file exists on disk. Add 5th validation question: "Is there a filesystem-verifiable artifact proving completion?"
- Tests in `tests/pm_agent/` — Verify `filesystem_verified=False` when artifact_path absent; `filesystem_verified=True` when path exists.

**Acceptance criteria**: `validate()` returns result with `filesystem_verified` field; STRICT-tier fails if False; tests pass.
**Risk**: Low. Dependencies: None (prerequisite for PM-002, PM-004). Traceability: D-0022 Principle 1 direction 1.

---

#### PM-002 — Mandatory Negative Evidence Documentation in SelfCheckProtocol
**Component**: PM Agent | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW mandatory negative evidence adopted; all-output-types per-claim tables rejected

**Change description**:
- `src/superclaude/pm_agent/self_check.py` — Record negative findings explicitly as `"no_hallucination_signals_found"`. Add `negative_evidence` list to return structure for confirmed-absent conditions.

**Acceptance criteria**: `validate()` returns `issues` list and `negative_evidence` list; clean validation produces non-empty `negative_evidence` list; tests verify.
**Risk**: Low. Dependencies: PM-001. Traceability: D-0022 Principle 1 direction 3.

---

#### AP-001 — Ambient Sycophancy Detection in Agent Definitions
**Component**: Adversarial Pipeline | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW 12-category sycophancy risk taxonomy adopted; static weight system without adaptive learning rejected

**Change description**:
- `.claude/agents/quality-engineer.md` and `src/superclaude/agents/quality-engineer.md` — Add "Sycophancy Detection NFR" section: 12-category taxonomy + non-linear multipliers (1.0×/1.3×/1.5×) + four-tier response routing.
- `.claude/agents/self-review.md` and `src/superclaude/agents/self-review.md` — Add same section.

**Acceptance criteria**: Both agent files contain "Sycophancy Detection NFR" section with 12-category taxonomy and four-tier routing; actionable instructions (not stubs).
**Risk**: Low. Dependencies: None (prerequisite for TU-003). Traceability: D-0022 Principle 5 direction 2.

---

#### TU-001 — CRITICAL FAIL Conditions for Unconditional Gate Failure
**Component**: Task-Unified Tier System | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — audit-validator CRITICAL FAIL pattern adopted; behavioral-only quality gate application rejected

**Change description**:
- `src/superclaude/cli/pipeline/gates.py` — Add `CriticalFailCondition` dataclass; add `critical_conditions: list[CriticalFailCondition]` to `GateCriteria`; when any critical condition matched, return `(False, f"CRITICAL: {condition_type}")`.
- `src/superclaude/cli/pipeline/models.py` — Add `GateCriteria.critical_conditions` field with default empty list.
- `.claude/skills/sc-task-unified-protocol/SKILL.md` and `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — Document three CRITICAL conditions for STRICT-tier tasks.

**Acceptance criteria**: `CriticalFailCondition` exists; `GateCriteria` has `critical_conditions`; critical condition returns FAIL regardless of other criteria; SKILL.md documents three named CRITICAL conditions.
**Risk**: Low. Dependencies: None (prerequisite for TU-002). Traceability: D-0022 Principle 2 direction 2.

---

#### QA-001 — Executor Validation Gate for All Agent Entry Points
**Component**: Quality Agents | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW executor validation gate pattern adopted; permissionMode:bypassPermissions rejected

**Change description**:
- `.claude/agents/quality-engineer.md` and sync — Add pre-execution validation checklist: (a) explicit acceptance criteria list, (b) at least one file path reference, (c) compliance tier. Emit BLOCKED if absent.
- `.claude/agents/self-review.md` and sync — Add pre-execution validation: artifact path and completion claim required.
- `.claude/agents/audit-validator.md` — Add minimum sample size check: BLOCKED for fewer than 3 items.

**Acceptance criteria**: quality-engineer.md has 3-field checklist; self-review.md has artifact path check; audit-validator.md has minimum sample check; all dev copies synced.
**Risk**: Low. Dependencies: None (prerequisite for QA-002). Traceability: D-0022 Principle 5 direction 6.

---

#### QA-002 — Typed State Transitions for Sequential Agent Invocation
**Component**: Quality Agents | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW typed message protocol adopted; bash IPC + all-opus model mandate rejected

**Change description**:
- `src/superclaude/cli/pipeline/models.py` — Add `AgentHandoffState` enum: `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`, `VALIDATED`.
- `src/superclaude/cli/sprint/executor.py` — Emit `TASK_READY` before quality-engineer invocation; emit `EXECUTION_COMPLETE` or `BLOCKED` after; log transitions to sprint result file.
- `.claude/agents/pm-agent.md` and sync — Document typed handoff states.

**Acceptance criteria**: `AgentHandoffState` enum exists in models.py; sprint executor emits TASK_READY before quality-engineer invocation; BLOCKED emitted when agent cannot proceed; pm-agent.md documents states.
**Risk**: Medium. Dependencies: QA-001. Traceability: D-0022 Principle 5 direction 5.

---

#### PA-001 — Pre-Packaged Artifact Collection Before Diagnostic Runs
**Component**: Pipeline Analysis Subsystem | **Effort**: M | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW pre-packaged artifact collection pattern adopted; bash artifact collection scripts rejected

**Change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Refactor `run_diagnostic_chain()` to separate collection from analysis. Add `collect_diagnostic_artifacts(failure_context) -> DiagnosticArtifactBundle` function. Add `DiagnosticArtifactBundle` dataclass: `gate_outputs`, `step_results`, `phase_context`, `collected_at`.

**Acceptance criteria**: `collect_diagnostic_artifacts()` exists; `DiagnosticArtifactBundle` exists; `run_diagnostic_chain()` calls collection before analysis; analysis stages operate on bundle fields.
**Risk**: Medium. Dependencies: None (prerequisite for PA-002, PA-003). Traceability: D-0022 Principle 3 direction 4.

---

#### PA-002 — Framework-vs-Project Diagnostic Distinction in Output
**Component**: Pipeline Analysis Subsystem | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW framework-vs-project distinction adopted; grep-based bash classification rejected

**Change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `failure_source: Literal["framework", "project", "unknown"]` to `DiagnosticReport`. Classification logic: .md input file failure → "project"; pipeline step exception → "framework"; ambiguous → "unknown". Include `failure_source` prominently in stage 4 summary.

**Acceptance criteria**: `DiagnosticReport` has `failure_source` field; stage 4 summary includes failure_source prominently; test verifying .md failure → "project" and pipeline step exception → "framework".
**Risk**: Low. Dependencies: PA-001. Traceability: D-0022 Principle 5 direction 7.

---

### Priority P1 — Evidence Verification / Typed Coordination (11 items)

#### RP-002 — Documented Fallback Degradation Path
**Component**: Roadmap Pipeline | **Effort**: XS | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW fallback documentation pattern adopted; dual-mode event-driven/phased-parallel architecture rejected

**Change description**:
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — Add "Fallback Degradation" section with ≥3 explicit trigger/behavior pairs covering: invalid `--agents` spec, absent output file after timeout, missing/corrupt `.roadmap-state.json`.
- `src/superclaude/cli/roadmap/executor.py` — Add inline comment block at `_apply_resume()` referencing "See SKILL.md §Fallback Degradation."

**Acceptance criteria**: SKILL.md has Fallback Degradation section with ≥3 trigger/behavior pairs; executor.py has comment at resume call site.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 3 direction 5.

---

#### CA-003 — Typed State Transitions in Audit Pass Progression
**Component**: Cleanup-Audit CLI | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW typed inter-agent communication adopted; bash IPC rejected

**Change description**:
- `src/superclaude/cli/cleanup_audit/executor.py` — Define `AuditPassState` enum: `PENDING`, `SCANNING`, `SCAN_COMPLETE`, `ANALYZING`, `ANALYSIS_COMPLETE`, `VALIDATING`, `DONE`, `BLOCKED`. Emit state at each G-001 → G-002 → G-003 transition. Emit `BLOCKED` with reason on empty result set.
- `src/superclaude/cli/pipeline/models.py` — Add `AuditPassState` to models module export list.

**Acceptance criteria**: `AuditPassState` enum exists in executor.py; BLOCKED emitted on empty result; G-001/G-002/G-003 transitions log current state.
**Risk**: Medium. Dependencies: CA-001, CA-002. Traceability: D-0022 Principle 5 direction 5.

---

#### CA-004 — Executor Validation Gate Before Agent Invocation
**Component**: Cleanup-Audit CLI | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW executor validation gate adopted; permissionMode:bypassPermissions rejected

**Change description**:
- `src/superclaude/cli/cleanup_audit/executor.py` — At start of `execute_cleanup_audit()`, validate: (a) target directory exists and readable, (b) `--batch-size` 1–100, (c) `--focus` value known. Emit `AuditPassState.BLOCKED` with reason on failure; fail-fast.
- `src/superclaude/cli/cleanup_audit/commands.py` — Complement (not replace) executor-level validation with CLI-level validation.

**Acceptance criteria**: `execute_cleanup_audit()` validates inputs before first pass; invalid target path returns BLOCKED immediately; unit test for each validation condition.
**Risk**: Low. Dependencies: CA-003. Traceability: D-0022 Principle 5 direction 6.

---

#### SE-002 — Per-Item UID Tracking for Sub-Phase Restartability
**Component**: Sprint Executor | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW batch immutability + per-item UID tracking adopted; 6000-line bash batch state machine rejected

**Change description**:
- `src/superclaude/cli/sprint/executor.py` — Add `task_uid: str` field; UIDs generated as `f"{phase_id}-{task_index:04d}"` at phase-load time. Implement sub-phase resume: with `--start N` and partial result file, re-enter at first task with status != DONE.
- `src/superclaude/cli/pipeline/models.py` — Add `task_uid` to task status record in TurnLedger if applicable.

**Acceptance criteria**: Each task has stable `task_uid` across session resets; `--start N` with partial result resumes at first non-DONE task; test verifying UID stability.
**Risk**: Medium. Dependencies: SE-001. Traceability: D-0022 Principle 3 direction 1.

---

#### SE-003 — Three-Mode Execution for Mid-Phase Resume
**Component**: Sprint Executor | **Effort**: M | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW three-mode prompt selection adopted; bash prompt template system rejected

**Change description**:
- `src/superclaude/cli/sprint/process.py` — Add `ExecutionMode` enum: `NORMAL`, `INCOMPLETE_RESUME`, `CORRECTION`. In `ClaudeProcess.build_command()`, accept `execution_mode` parameter with mode-appropriate context prepend.
- `src/superclaude/cli/sprint/executor.py` — Determine correct `ExecutionMode` per task: no prior attempt → NORMAL; partial output → INCOMPLETE_RESUME; failed gate → CORRECTION. Record mode in TurnLedger.

**Acceptance criteria**: `ExecutionMode` enum exists; `build_command()` accepts and uses mode; TurnLedger records mode; integration test verifying INCOMPLETE_RESUME produces different prompt than NORMAL.
**Risk**: Medium. Dependencies: SE-001, SE-002. Traceability: D-0022 Principle 3 direction 2.

---

#### PM-004 — ReflexionPattern: Presumption of Falsehood Default Stance
**Component**: PM Agent | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW Presumption of Falsehood stance adopted; mandatory sequential PABLOV chain rejected

**Change description**:
- `src/superclaude/pm_agent/reflexion.py` — Add `confidence: float` to `get_solution()` return. New solutions default to `confidence=0.5`. Verified solutions (via `record_error()` with `verified=True`) reach `confidence=0.8+`. Callers check `confidence >= 0.7` before auto-applying.
- `src/superclaude/pm_agent/reflexion.py` — Add `verified: bool = False` parameter to `record_error()`.

**Acceptance criteria**: `get_solution()` returns result with `confidence` field; new solutions default to 0.5; verified solutions reach ≥0.8; callers can check confidence before auto-applying.
**Risk**: Low. Dependencies: PM-001. Traceability: D-0022 Principle 1 direction 1.

---

#### AP-002 — CEV Vocabulary Extension to All Verification Outputs
**Component**: Adversarial Pipeline | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — IC-native CEV extension (not LW adoption)

**Change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` and sync — Add to STRICT tier instructions: CEV format requirement: `[CLAIM] — [EVIDENCE:file:line] — [VERDICT: confirmed|rejected|inconclusive]`.
- `.claude/agents/quality-engineer.md` — Add CEV output format requirement.

**Acceptance criteria**: sc-task-unified-protocol/SKILL.md contains CEV format requirement in STRICT tier; quality-engineer.md contains CEV output format; at least one example shown in each file.
**Risk**: Low. Dependencies: AP-001. Traceability: D-0022 Principle 1 direction 4.

---

#### AP-003 — Four-Category Failure Classification in Adversarial Debate Outputs
**Component**: Adversarial Pipeline | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW 4-category failure taxonomy adopted; point-based scoring with confidence tiers rejected

**Change description**:
- `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` and sync — Add "Failure Mode Classification" section with four categories: (1) Execution failures, (2) Template failures, (3) Evidence failures, (4) Workflow failures. Classify each failure before scoring.

**Acceptance criteria**: scoring-protocol.md has "Failure Mode Classification" section with all four categories; each category has ≥1 example; dev copy synced.
**Risk**: Low. Dependencies: AP-002. Traceability: D-0022 Principle 5 direction 4.

---

#### TU-002 — Output-Type-Specific Gate Application
**Component**: Task-Unified Tier System | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW output-type-specific gate tables concept adopted; manual quality gate application rejected

**Change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` and sync — Add `output_type` column to verification routing table: code (compile/test required), analysis (evidence citation required), documentation (structure check only), opinion (CEV structure required).
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` and sync — Add output-type detection rules for *.md → documentation; analysis report → analysis; code changes → code.

**Acceptance criteria**: tier-classification.md has output-type detection rules for ≥3 output types; SKILL.md verification table has output_type column; documentation tasks skip code verification.
**Risk**: Medium. Dependencies: TU-001. Traceability: D-0022 Principle 2 direction 3.

---

#### TU-003 — Six Universal Quality Principles as Verification Agent Vocabulary
**Component**: Task-Unified Tier System | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW six quality principles vocabulary adopted; quality gate menu with manual operator selection rejected

**Change description**:
- `.claude/agents/quality-engineer.md` and sync — Add "Quality Principles NFR" section with six principles: Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy. Each with IC-specific application example for STRICT-tier verification.

**Acceptance criteria**: quality-engineer.md has "Quality Principles NFR" section with all six principles named and described; each has IC-specific application example; dev copy synced.
**Risk**: Low. Dependencies: AP-001. Traceability: D-0022 Principle 5 direction 1.

---

#### PA-003 — 4-Category Failure Classification in DiagnosticReport
**Component**: Pipeline Analysis Subsystem | **Effort**: S | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW 4-category failure taxonomy adopted; point-based scoring system rejected

**Change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `FailureCategory` enum: `EXECUTION_FAILURE`, `TEMPLATE_FAILURE`, `EVIDENCE_FAILURE`, `WORKFLOW_FAILURE`. Add `failure_categories: list[tuple[FailureCategory, ConfidenceLevel]]` to `DiagnosticReport`.
- `src/superclaude/cli/pipeline/models.py` — Add `FailureCategory` and `ConfidenceLevel` enums.

**Acceptance criteria**: `FailureCategory` and `ConfidenceLevel` enums exist; `DiagnosticReport` has `failure_categories`; each failure categorized; test verifying ≥2 category types distinguishable.
**Risk**: Medium. Dependencies: PA-001, PA-002. Traceability: D-0022 Principle 5 direction 4.

---

### Priority P2 — Restartability / Bounded Complexity / Schema Reliability (7 items)

#### RP-003 — Per-Track State Machine Formalization
**Component**: Roadmap Pipeline | **Effort**: M | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW per-track state machine formalism adopted; CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS rejected

**Change description**:
- `src/superclaude/cli/pipeline/models.py` — Extend `StepStatus` enum: `PENDING`, `IN_PROGRESS`, `DONE`, `FAILED`, `SKIPPED`.
- `src/superclaude/cli/roadmap/executor.py` — Construct Steps with `status=StepStatus.PENDING`; transition to IN_PROGRESS during execution; DONE or FAILED after gate. Update `_apply_resume()` to read StepStatus.DONE as skip criterion.

**Acceptance criteria**: `StepStatus` enum has all 5 states; gate failure → FAILED not IN_PROGRESS; `--resume` skips DONE steps only.
**Risk**: Medium. Dependencies: RP-001. Traceability: D-0022 Principle 3 direction 3.

---

#### RP-004 — Hard Resource Caps Formalization
**Component**: Roadmap Pipeline | **Effort**: S | **Classification**: add new code
**patterns_not_mass**: true — LW track-cap principle adopted; Rigorflow runtime scheduler rejected

**Change description**:
- `src/superclaude/cli/roadmap/executor.py` — Add `MAX_PARALLEL_STEPS = 4` constant; CLI validation: reject `--agents` producing >MAX_PARALLEL_STEPS agent specs.
- `src/superclaude/cli/roadmap/commands.py` — Add `--max-parallel` option (default: MAX_PARALLEL_STEPS, range 1–8).

**Acceptance criteria**: `MAX_PARALLEL_STEPS` constant exists with documentation comment; CLI rejects >MAX_PARALLEL_STEPS agent specs; `--max-parallel` is wired and validated.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 4 direction 2.

---

#### SE-004 — Auto-Trigger Diagnostic on N Consecutive Gate Failures
**Component**: Sprint Executor | **Effort**: M | **Classification**: add new code
**patterns_not_mass**: true — LW auto-trigger diagnostic pattern adopted; bash monitoring infrastructure rejected

**Change description**:
- `src/superclaude/cli/sprint/executor.py` — Add `auto_diagnostic_threshold: int = 3` parameter. When consecutive failure count reaches threshold, invoke `run_diagnostic_chain()` from `src/superclaude/cli/pipeline/diagnostic_chain.py`. Reset counter after invocation.
- `src/superclaude/cli/sprint/commands.py` — Add `--auto-diagnostic-threshold N` CLI option (default 3, range 1–10).
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Verify `run_diagnostic_chain()` accepts sprint executor failure context format.

**Acceptance criteria**: `execute_sprint()` has `auto_diagnostic_threshold` parameter; `run_diagnostic_chain()` invoked after N failures; diagnostic result logged to sprint results directory; CLI option wired.
**Risk**: Medium. Dependencies: SE-001. Traceability: D-0022 Principle 5 direction 3.

---

#### SE-005 — Three-Tier Severity for Gate Failure Reports
**Component**: Sprint Executor | **Effort**: S | **Classification**: add new code
**patterns_not_mass**: true — LW Sev 1/2/3 severity taxonomy adopted; point-based scoring system rejected

**Change description**:
- `src/superclaude/cli/pipeline/models.py` — Add `GateFailureSeverity` enum: `SEV1_BLOCK`, `SEV2_CYCLE`, `SEV3_ADVISORY`. Add `severity: GateFailureSeverity` to `StepResult` when status == FAILED.
- `src/superclaude/cli/pipeline/gates.py` — After `gate_passed()` returns `(False, reason)`, classify into `GateFailureSeverity` based on tier.
- `src/superclaude/cli/sprint/executor.py` — Log severity alongside gate failure reason; surface Sev 1 failures prominently in TUI.

**Acceptance criteria**: `GateFailureSeverity` enum exists; STRICT-tier failures default to SEV1_BLOCK; STANDARD-tier may classify as SEV2_CYCLE with partial output; severity logged in sprint result files.
**Risk**: Low. Dependencies: SE-001. Traceability: D-0022 Principle 4 direction 3.

---

#### PM-003 — Model Tier Proportionality for PM Agent Operations
**Component**: PM Agent | **Effort**: XS | **Classification**: strengthen existing code
**patterns_not_mass**: true — LW model tier proportionality principle adopted; all-opus mandate rejected

**Change description**:
- `src/superclaude/pm_agent/__init__.py` — Add module-level docstring documenting tier policy: Haiku for routine checks, Sonnet for structural validation, Opus for critical cross-session learning at confidence <0.70.
- `.claude/agents/pm-agent.md` — Add "Model Tier Policy" section specifying above tiers.

**Acceptance criteria**: `pm_agent/__init__.py` contains tier policy docstring; `pm-agent.md` has "Model Tier Policy" section; tier rules named explicitly.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 4 direction 1.

---

#### QA-003 — Model Tier Proportionality Policy for Quality Agents
**Component**: Quality Agents | **Effort**: XS | **Classification**: strengthen existing code
**patterns_not_mass**: true — IC-native policy formalization (anti-regression)

**Change description**:
- `.claude/agents/quality-engineer.md` and sync — Add "Model Tier Policy": Sonnet tier; Opus escalation for >5-file STRICT tasks or security paths; Haiku not appropriate.
- `.claude/agents/audit-validator.md` and sync — Add "Model Tier Policy": Haiku tier (10% spot-check validation).
- `.claude/agents/self-review.md` and sync — Add "Model Tier Policy": Haiku for routine; Sonnet for STRICT implementation reviews.

**Acceptance criteria**: All three agent .md files have "Model Tier Policy" section; each specifies primary tier and escalation conditions; all dev copies synced.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 4 direction 1.

---

#### TU-004 — Confidence Threshold <0.70 Explicit Blocking
**Component**: Task-Unified Tier System | **Effort**: XS | **Classification**: strengthen existing code
**patterns_not_mass**: true — IC-native gate integrity improvement

**Change description**:
- `.claude/skills/sc-task-unified-protocol/SKILL.md` and sync — Clarify: confidence <0.70 → task classification BLOCKED, requires user confirmation. Blocking message must include computed tier, competing tier, and keywords causing split.
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — Add explicit blocking message format for low-confidence classifications.

**Acceptance criteria**: SKILL.md specifies confidence <0.70 blocks execution pending user confirmation; blocking message format includes tier, competing tier, and keywords; no code path proceeds without confirmation at <0.70.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 2.

---

#### PA-004 — Hard Resource Caps for Recursive Pipeline Analysis
**Component**: Pipeline Analysis Subsystem | **Effort**: XS | **Classification**: add new code
**patterns_not_mass**: true — LW resource cap principle adopted; runtime dynamic load balancer rejected

**Change description**:
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Add `MAX_DIAGNOSTIC_DEPTH = 4` constant; block recursive diagnostic invocation at depth > 1 with clear error.
- `src/superclaude/cli/pipeline/combined_m2_pass.py` — Add `MAX_FMEA_DELIVERABLES = 50` constant; process only first 50 deliverables if exceeded; document cap referencing D-0022 Principle 4.

**Acceptance criteria**: `MAX_DIAGNOSTIC_DEPTH` exists; recursive diagnostic blocked at depth >1; `MAX_FMEA_DELIVERABLES` exists with documented behavior for oversized inputs.
**Risk**: Low. Dependencies: None. Traceability: D-0022 Principle 4 direction 2.

---

## Cross-Component Dependency Graph

*(Reproduced from D-0028/spec.md — unchanged, validated as correct by D-0032 Dimension 6)*

**Prerequisite relationships** (A → B: A must be done before B):
- PA-001 → PA-002 → PA-003
- SE-001 → SE-002 → SE-003
- SE-001 → SE-004; SE-001 → SE-005
- CA-001 → CA-002 → CA-003 → CA-004
- PM-001 → PM-002; PM-001 → PM-004
- QA-001 → QA-002
- TU-001 → TU-002
- AP-001 → TU-003
- AP-002 → AP-003
- SE-002 → SE-003
- RP-001 → RP-003
- PA-002 → PA-003

**Circular dependencies**: 0 (DAG verified — D-0028)

## Recommended Execution Sequence

1. **Phase A (parallel)**: PA-001, SE-001, CA-001, PM-001, AP-001, TU-001, QA-001, RP-001 — all P0 gate integrity, no cross-component prerequisites
2. **Phase B (parallel)**: PA-002, SE-002, CA-002, PM-002, AP-002, TU-002, QA-002, RP-002 — P0/P1 items depending only on their own component's P0 item
3. **Phase C (parallel)**: PA-003, SE-003, CA-003, PM-004, AP-003, TU-003, CA-004 — P1 items with cross-P1 dependencies
4. **Phase D (parallel)**: PA-004, SE-004, SE-005, PM-003, QA-003, TU-004, RP-003, RP-004 — P2 items, all optional refinements

---

## Acceptance Criteria Check

| Criterion | Required | Actual | Status |
|---|---|---|---|
| File exists as final-improve-plan.md with validation approval header citing D-0033 | Yes | Header present; explicitly cites `artifacts/D-0033/spec.md` | PASS |
| All file paths in final-improve-plan.md verified via Auggie MCP (SC-007 Gate Criteria) | Yes | All 33 distinct paths verified via filesystem in D-0032 Dimension 1 | PASS |
| All Fail-Rework items from D-0033 have corrections applied | Yes | N/A (0 Fail-Rework items from D-0033); section present confirming zero | PASS |
| final-improve-plan.md confirmed schema-compliant with /sc:roadmap per D-0030 | Yes | Schema compliance confirmation present; D-0030 explicitly cited | PASS |
| No items still fail any six dimensions | Yes | All 31 items passed all 6 dimensions per D-0032 | PASS |
