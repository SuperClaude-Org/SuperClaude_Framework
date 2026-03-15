---
component: roadmap-pipeline
deliverable: D-0026
source_comparison: comparison-roadmap-pipeline.md
verdict: split by context
principle_primary: Restartability
principle_secondary: Bounded Complexity
generated: 2026-03-15
---

# Improvement Plan: Roadmap Pipeline

Traceability source: D-0022 merged-strategy.md. All items trace to one or more of the five architectural principles: Evidence Integrity (P1-E), Deterministic Gates (P1-D), Restartability (P1-R), Bounded Complexity (P1-B), Scalable Quality Enforcement (P1-Q).

---

## ITEM RP-001 — Fail-Closed Gate Semantics in execute_roadmap

**Priority**: P0
**Effort**: S
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's fail-closed verdict logic (not LW's bash gate mechanism)
**Why not full import**: LW's gate implementation is embedded in 6000-line bash batch orchestration; only the fail-closed semantic (inconclusive = FAIL) is adoptable into IC's Python gate_passed() call sites.

**File paths and change description**:
- `src/superclaude/cli/roadmap/executor.py` — In `execute_roadmap()`, verify that any gate result that is not an affirmative PASS is treated as FAIL. Review calls to `gate_passed()` to confirm no PASS-with-conditions path exists. Annotate the gate call site with a comment: `# fail-closed: inconclusive result is FAIL per D-0022 Principle 2`.
- `src/superclaude/cli/pipeline/gates.py` — Confirm `gate_passed()` returns `(False, reason)` for all non-PASS paths including timeouts and parse failures (not just criteria mismatches).

**Rationale**: D-0022 Principle 2 (Deterministic Gates), direction 1: "When a gate evaluation cannot definitively confirm PASS, the result is FAIL — not PASS with caveats." This prevents partial completion from being mistaken for success.

**Dependencies**: None (prerequisite for RP-003)
**Acceptance criteria**: `gate_passed()` returns `(False, ...)` for empty output files, malformed YAML, and timeout conditions; no call site in executor.py treats a non-PASS as a soft warning.
**Risk**: Low. Purely clarifying semantics; existing logic already returns False in error cases; change is annotation + explicit timeout handling.

---

## ITEM RP-002 — Documented Fallback Degradation Path

**Priority**: P1
**Effort**: XS
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's pattern of explicit fallback documentation (not LW's event-driven/phased-parallel dual-mode architecture)
**Why not full import**: LW's Rigorflow has a full event-driven primary and phased-parallel fallback with automated trigger conditions; IC's roadmap pipeline is single-track and does not need dual-mode architecture. Only the documentation pattern is adoptable.

**File paths and change description**:
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — Add a "Fallback Degradation" section specifying: (a) what happens when `--agents` specification is invalid (fall back to default model, log warning); (b) what happens when a step's output file is absent after timeout (mark step FAIL, skip to gate evaluation); (c) what happens when `--resume` is requested but `.roadmap-state.json` is missing or corrupt (restart from step 0, log warning). Each fallback must have an explicit trigger condition and documented behavior.
- `src/superclaude/cli/roadmap/executor.py` — Add inline comment block at `_apply_resume()` noting: "If state file is corrupt or absent, resume falls back to full restart. See SKILL.md §Fallback Degradation."

**Rationale**: D-0022 Principle 3 (Restartability), direction 5: "The fallback path and its trigger conditions should be explicitly documented in the component specification, not inferred."

**Dependencies**: None
**Acceptance criteria**: SKILL.md contains a Fallback Degradation section with ≥3 explicit trigger/behavior pairs; executor.py has a comment at the resume call site referencing the section.
**Risk**: Low. Documentation only; no behavioral change.

---

## ITEM RP-003 — Per-Track State Machine Formalization (Step-Level States)

**Priority**: P2
**Effort**: M
**Classification**: strengthen existing code
**patterns_not_mass**: true — adopting LW's per-track state machine formalism as an extension to StepResult, not importing LW's CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS infrastructure
**Why not full import**: LW's per-track state machine depends on experimental multi-agent team infrastructure (explicitly rejected in D-0022 Principle 3 reject inventory). IC's single-track model needs only the state enum formalization, not the multi-track orchestration.

**File paths and change description**:
- `src/superclaude/cli/pipeline/models.py` — Extend `StepStatus` enum to include: `PENDING`, `IN_PROGRESS`, `DONE`, `FAILED`, `SKIPPED` (matching LW's state formalism). Confirm that `StepResult` exposes the status via its `status` field.
- `src/superclaude/cli/roadmap/executor.py` — In `_build_steps()`, ensure each Step is constructed with `status=StepStatus.PENDING` at creation, transitions to `IN_PROGRESS` during execution, and `DONE` or `FAILED` after gate evaluation. This makes the state machine explicit and forward-compatible with future multi-track scenarios.
- `src/superclaude/cli/roadmap/executor.py` — Update `_apply_resume()` to read `StepStatus.DONE` (not just gate_passed history) as the skip criterion for resumed steps.

**Rationale**: D-0022 Principle 3 (Restartability), direction 3: "The step-level states in StepResult should be extended to match [per-track state machine] formalism for forward compatibility."

**Dependencies**: RP-001 (gate_passed semantics must be settled before DONE/FAILED transition logic is implemented)
**Acceptance criteria**: `StepStatus` enum has all 5 states; a step that fails its gate transitions to FAILED not remains IN_PROGRESS; `--resume` skips DONE steps only.
**Risk**: Medium. Model changes may affect serialization to `.roadmap-state.json`; require compatibility test.

---

## ITEM RP-004 — Hard Resource Caps Formalization

**Priority**: P2
**Effort**: S
**Classification**: add new code
**patterns_not_mass**: true — adopting LW's track-cap principle (5 tracks / 15 agents) as IC-native configuration constants, not LW's Rigorflow runtime scheduler
**Why not full import**: LW's track and agent caps are enforced by a complex Rigorflow runtime scheduler with dynamic load balancing; IC needs only configuration constants with validation at CLI entry point.

**File paths and change description**:
- `src/superclaude/cli/roadmap/executor.py` — Add `MAX_PARALLEL_STEPS = 4` constant (maximum parallel steps in roadmap generation, matching Step 2a/2b current limit). Add CLI validation: if `--agents` produces more than MAX_PARALLEL_STEPS agent specs, emit error and exit. Document constant with comment referencing D-0022 Principle 4.
- `src/superclaude/cli/roadmap/commands.py` — Add `--max-parallel` option (default: MAX_PARALLEL_STEPS) as an escape hatch for advanced users; validate range 1–8.

**Rationale**: D-0022 Principle 4 (Bounded Complexity), direction 2: "IC should formalize resource caps: maximum concurrent phases in sprint execution, maximum parallel steps in roadmap generation, maximum depth for recursive pipeline analysis."

**Dependencies**: None
**Acceptance criteria**: `MAX_PARALLEL_STEPS` constant exists in executor.py with documentation comment; CLI rejects `--agents` specs producing >MAX_PARALLEL_STEPS; `--max-parallel` flag is wired and validated.
**Risk**: Low. Adds a validation check; does not change existing behavior for current single-pair adversarial step (2 parallel steps, well within cap).
