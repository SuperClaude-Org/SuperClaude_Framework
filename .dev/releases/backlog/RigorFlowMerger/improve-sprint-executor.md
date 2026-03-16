---
component: sprint-executor
deliverable: D-0026
source_comparison: comparison-sprint-executor.md
verdict: IC stronger
principle_primary: Restartability
principle_secondary: Deterministic Gates
generated: 2026-03-15
---

# Improvement Plan: Sprint Executor

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles.

---

## ITEM SE-001 — Fail-Closed Gate Completion Logic

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's fail-closed verdict logic for phase gate completion, not LW's bash batch state machine
**Why not full import**: LW's fail-closed logic is embedded in bash batch processing with multi-file comparison semantics; IC's sprint executor needs only to apply fail-closed semantics to its existing `gate_passed()` call sites and task completion detection.

**File paths and change description**:
- `src/superclaude/cli/sprint/executor.py` — In `execute_phase_tasks()`, when evaluating whether a task is "complete," explicitly check for affirmative evidence (gate passed + output file present and non-empty + no BLOCKED state). If any of these conditions is inconclusive, classify as FAIL, not as a soft completion. Add comment: `# fail-closed: inconclusive task completion = FAIL per D-0022 Principle 2`.
- `src/superclaude/cli/pipeline/gates.py` — Confirm that `gate_passed()` handles the case where the output file exists but is empty (should return `(False, "empty output file")` — not `(True, None)`).
- `src/superclaude/cli/sprint/executor.py` — For each gate call site in the sprint executor, ensure the result is destructured as `(passed, reason)` and `reason` is logged even when `passed` is True (for traceability).

**Rationale**: D-0022 Principle 2 (Deterministic Gates), direction 1: "A phase gate that is inconclusive is a FAIL." Principle 2 direction 1: "fail-closed principle at the gate level."

**Dependencies**: None (prerequisite for SE-002, SE-003)
**Acceptance criteria**: `gate_passed()` returns `(False, "empty output file")` for zero-byte output; sprint executor logs gate reasons for all evaluations; no code path treats an inconclusive gate result as PASS.
**Risk**: Low. Tightens existing behavior; edge case for empty output files that previously may have been treated as PASS.

---

## ITEM SE-002 — Per-Item UID Tracking for Sub-Phase Restartability

**Priority**: P1
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's batch immutability and per-item UID tracking principle as an extension to IC's TurnLedger, not importing LW's 6000-line bash batch state machine
**Why not full import**: LW's per-item UID tracking is implemented as a bash key-value store with inter-process file locking; IC needs only a stable identifier field on each task record in the TurnLedger, resolvable via Python dataclass extension.

**File paths and change description**:
- `src/superclaude/cli/sprint/executor.py` — Add `task_uid: str` field to the task representation within a phase. UIDs are generated at phase-load time as `f"{phase_id}-{task_index:04d}"` (stable across session resets for the same tasklist). UIDs are written to the phase result file and read during `--start` resume to identify the first failed task.
- `src/superclaude/cli/sprint/executor.py` — Implement sub-phase resume: when `--start N` is provided but the phase has a partial result file with per-task UIDs, re-enter at the first task with status != DONE (not at task 0). This closes the current gap where Phase 3 task 14 failure requires re-running all 15 tasks.
- `src/superclaude/cli/pipeline/models.py` — Add `task_uid` to task status record in `TurnLedger` if it exists there; otherwise, add it to the sprint-specific task model.

**Rationale**: D-0022 Principle 3 (Restartability), direction 1: "Adopt LW's batch immutability principle — task identifiers are frozen once a sprint phase begins." and "per-item UID tracking within a phase: each task should receive a stable identifier that persists across session resets."

**Dependencies**: SE-001 (DONE/FAIL task state must be deterministic before UID-based resume can work)
**Acceptance criteria**: Each task in a sprint phase has a stable `task_uid` that does not change across session resets for the same tasklist; `--start N` with a partial result file resumes at the first non-DONE task, not at task 0; test verifying UID stability across two executor runs on the same phase.
**Risk**: Medium. New field in task representation; requires compatibility with existing result files (may need migration for result files that lack UIDs — graceful fallback to full-phase restart is acceptable).

---

## ITEM SE-003 — Three-Mode Execution for Mid-Phase Resume

**Priority**: P1
**Effort**: M
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's three-mode prompt selection pattern (normal / incomplete / correction), not LW's bash prompt template system
**Why not full import**: LW's three modes are implemented as bash prompt template files with conditional substitution; IC's prompt construction is in `ClaudeProcess.build_command()`. The three-mode concept is adoptable as an enum + conditional logic in the existing prompt builder.

**File paths and change description**:
- `src/superclaude/cli/sprint/process.py` — Add `ExecutionMode` enum: `NORMAL`, `INCOMPLETE_RESUME`, `CORRECTION`. In `ClaudeProcess.build_command()`, accept an `execution_mode: ExecutionMode` parameter. When `INCOMPLETE_RESUME`, prepend context: "Resuming an incomplete task. Previous partial output: [excerpt from last output file]." When `CORRECTION`, prepend: "Correcting a failed task. Failure reason: [gate failure reason from previous run]."
- `src/superclaude/cli/sprint/executor.py` — In `execute_phase_tasks()`, determine the correct `ExecutionMode` for each task: tasks with no prior attempt → `NORMAL`; tasks with partial output → `INCOMPLETE_RESUME`; tasks that previously failed a gate → `CORRECTION`. Record the mode in the TurnLedger for traceability.

**Rationale**: D-0022 Principle 3 (Restartability), direction 2: "When resuming a phase, the execution mode (fresh / incomplete-resume / correction) should be explicitly declared in the TurnLedger and reflected in the prompt construction. This eliminates the current ambiguity where a resumed phase cannot distinguish between 'task never started' and 'task started but not completed.'"

**Dependencies**: SE-001 (fail-closed semantics), SE-002 (UID tracking to identify which tasks need which mode)
**Acceptance criteria**: `ExecutionMode` enum exists; `build_command()` accepts and uses the mode; TurnLedger records the mode for each task; integration test verifying INCOMPLETE_RESUME produces a different prompt than NORMAL.
**Risk**: Medium. Changes prompt construction; may affect output format for resumed phases. Requires careful testing.

---

## ITEM SE-004 — Auto-Trigger Diagnostic on N Consecutive Gate Failures

**Priority**: P2
**Effort**: M
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's auto-trigger diagnostic pattern (activate on 3rd QA FAIL / max retry exceeded / critical violation) without LW's specific trigger threshold (configurable in IC)
**Why not full import**: LW's auto-trigger is wired to its bash monitoring infrastructure; IC needs only a counter in `execute_phase_tasks()` that checks consecutive failures and invokes `run_diagnostic_chain()` from the existing pipeline analysis subsystem.

**File paths and change description**:
- `src/superclaude/cli/sprint/executor.py` — Add `auto_diagnostic_threshold: int = 3` parameter to `execute_sprint()` (configurable, default 3 consecutive gate failures). When the consecutive failure count reaches the threshold, invoke `run_diagnostic_chain()` from `src/superclaude/cli/pipeline/diagnostic_chain.py` with the accumulated failure context. Reset the counter after successful diagnostic invocation.
- `src/superclaude/cli/sprint/commands.py` — Add `--auto-diagnostic-threshold N` CLI option (default: 3, range: 1–10). Document the option with: "Automatically invoke diagnostic chain after N consecutive phase gate failures."
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — Verify that `run_diagnostic_chain()` accepts the sprint executor's failure context format (no interface changes should be required if the existing signature is generic).

**Rationale**: D-0022 Principle 5 (Scalable Quality Enforcement), direction 3: "The Sprint Executor should automatically invoke diagnostic analysis when a phase fails N consecutive times, without requiring operator intervention."

**Dependencies**: SE-001 (gate failures must be deterministic before counting them)
**Acceptance criteria**: `execute_sprint()` has `auto_diagnostic_threshold` parameter; `run_diagnostic_chain()` is invoked after N consecutive failures; diagnostic result is logged to the sprint results directory; CLI option is wired.
**Risk**: Medium. Adds a new invocation path for the diagnostic chain; requires that `run_diagnostic_chain()` is robust to sprint-context input.

---

## ITEM SE-005 — Three-Tier Severity for Gate Failure Reports

**Priority**: P2
**Effort**: S
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's Sev 1/2/3 severity taxonomy for gate failure classification, not LW's specific failure scoring system
**Why not full import**: LW's severity taxonomy uses a point-based scoring system (High ≥5 pts, Medium 3-4, Low ≤2) with complex FMEA integration; IC needs only the three-tier operator response policy (block/cycle/advisory) applied to gate failure report annotations.

**File paths and change description**:
- `src/superclaude/cli/pipeline/models.py` — Add `GateFailureSeverity` enum: `SEV1_BLOCK`, `SEV2_CYCLE`, `SEV3_ADVISORY`. Add `severity: GateFailureSeverity` field to `StepResult` when `status == FAILED`. Default to `SEV1_BLOCK` for STRICT-tier gates; `SEV2_CYCLE` for STANDARD-tier gate failures with partial output; `SEV3_ADVISORY` for LIGHT-tier gate failures.
- `src/superclaude/cli/pipeline/gates.py` — After `gate_passed()` returns `(False, reason)`, classify the failure into `GateFailureSeverity` based on tier (GateCriteria.tier). Return the severity as an annotation on the failure reason.
- `src/superclaude/cli/sprint/executor.py` — Log severity alongside gate failure reason; surface Sev 1 failures prominently in TUI output.

**Rationale**: D-0022 Principle 4 (Bounded Complexity), direction 3: "Introducing severity allows STANDARD-tier issues to cycle rather than block, while ensuring Sev 1 issues remain unconditional blockers."

**Dependencies**: SE-001 (gate_passed() semantics settled)
**Acceptance criteria**: `GateFailureSeverity` enum exists; STRICT-tier gate failures default to SEV1_BLOCK; STANDARD-tier may classify as SEV2_CYCLE with partial output; severity is logged in sprint result files.
**Risk**: Low. Additive field; no existing behavior changes required.
