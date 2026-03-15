---
high_severity_count: 4
medium_severity_count: 8
low_severity_count: 3
total_deviations: 15
validation_complete: true
tasklist_ready: false
---

## Deviation Report

### DEV-001
- **Severity**: HIGH
- **Deviation**: The roadmap omits the `PortifyPhaseType` enum entirely from its model deliverables and Phase 2 scope.
- **Spec Quote**: `class PortifyPhaseType(Enum): PREREQUISITES = "prerequisites" / ANALYSIS = "analysis" / USER_REVIEW = "user_review" / SPECIFICATION = "specification" / SYNTHESIS = "synthesis" / PANEL_REVIEW = "panel_review"`
- **Roadmap Quote**: `Implement core domain models: PortifyConfig, PortifyStep, PortifyStepResult, PortifyOutcome, PortifyStatus, MonitorState, TurnLedger`
- **Impact**: `PortifyPhaseType` is used extensively in `PortifyStep.phase_type`, the dry-run filter logic in the executor, and the super-milestone validation matrix. Its omission from Phase 2 deliverables leaves the step builder and dry-run filtering unimplemented.
- **Recommended Correction**: Add `PortifyPhaseType` to the Phase 2 model deliverables list and Phase 2 scope explicitly.

---

### DEV-002
- **Severity**: HIGH
- **Deviation**: The roadmap omits `ConvergenceState` enum from all deliverables and scope sections.
- **Spec Quote**: `class ConvergenceState(Enum): NOT_STARTED = "NOT_STARTED" / REVIEWING = "REVIEWING" / INCORPORATING = "INCORPORATING" / SCORING = "SCORING" / CONVERGED = "CONVERGED" / ESCALATED = "ESCALATED"`
- **Roadmap Quote**: `[MISSING]` — `ConvergenceState` does not appear in Phase 2 deliverables or Phase 7 deliverables.
- **Impact**: `PortifyResult.convergence_state: ConvergenceState` and the return contract field `convergence_state` both depend on this enum. Without it, the convergence state machine in Phase 7 has no typed state representation.
- **Recommended Correction**: Add `ConvergenceState` to Phase 2 `models.py` deliverables.

---

### DEV-003
- **Severity**: HIGH
- **Deviation**: The roadmap introduces a `failures.py` module not present in the spec's module plan, while the spec's module plan (`__init__.py`, `models.py`, `gates.py`, etc.) does not include `failures.py`, `resume.py`, or `contract.py` — three roadmap-invented modules.
- **Spec Quote**: `module_plan: [models.py, gates.py, prompts.py, config.py, inventory.py, executor.py, monitor.py, process.py, tui.py, logging_.py, diagnostics.py, commands.py, __init__.py]`
- **Roadmap Quote**: `failures.py with all 5 error codes` / `resume.py` / `contract.py` (Phase 1 Deliverables)
- **Impact**: Implementing three undocumented modules violates the spec's explicit module plan. Return contract logic specified in `executor.py` (via `_emit_return_contract()`) would be split into `contract.py`, potentially creating interface mismatches. Resume logic is part of `executor.py` per spec.
- **Recommended Correction**: Fold error code definitions into `models.py` or `config.py` per the spec's module plan. Fold return contract and resume logic into `executor.py`. Remove `failures.py`, `resume.py`, and `contract.py` from Phase 2 deliverables.

---

### DEV-004
- **Severity**: HIGH
- **Deviation**: The roadmap omits the G-010 `brainstorm_section` semantic check (`has_brainstorm_section`) and the G-011 `has_criticals_addressed` check from the per-gate check mapping table in Phase 3.
- **Spec Quote**: `GATE_G010: SemanticCheck("brainstorm_section", has_brainstorm_section, ...)` / `GATE_G011: SemanticCheck("criticals_addressed", has_criticals_addressed, ...)`
- **Roadmap Quote**: `G-010: EXIT_RECOMMENDATION marker present; has_zero_placeholders (zero {{SC_PLACEHOLDER:*}} sentinels)` / `G-011` is not listed in the per-gate check mapping table at all.
- **Impact**: G-010 would be implemented without the `has_brainstorm_section` check, allowing artifacts missing Section 12 to pass the gate despite the spec's explicit SC-008 requirement. G-011 would lack `has_criticals_addressed`, allowing CONVERGED state to be reached without verifying CRITICAL findings resolution.
- **Recommended Correction**: Add `has_brainstorm_section` to G-010 in the Phase 3 per-gate check mapping table. Add G-011 row with `has_quality_scores` and `has_criticals_addressed` checks.

---

### DEV-005
- **Severity**: MEDIUM
- **Deviation**: The roadmap renames Phase 3 of the spec (steps 5–8, specification design) as "Phase 2" in its narrative, and the spec's Phase 3 (synthesis) as "Phase 3" — creating a numbering mismatch with the spec's internal phase references used in the approval file names and `phase_contracts` field.
- **Spec Quote**: `phase1-approval.yaml` / `phase2-approval.yaml` / `"Phase 1+2 outputs"` (step 10 synthesis inputs)
- **Roadmap Quote**: `Phase 2→3 entry gate verifies: portify-spec.md status: completed` / `Phase 1 artifact generation` (Phase 4) / `Phase 2 design/spec generation` (Phase 5)
- **Impact**: Implementers reading the roadmap would produce approval files and `phase_contracts` keys using different numbering than the spec, potentially breaking resume logic and contract parsing.
- **Recommended Correction**: Align roadmap phase naming with the spec's internal naming: steps 2–3 = Phase 1 (analysis), steps 5–8 = Phase 2 (specification), steps 10–11 = Phases 3–4.

---

### DEV-006
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 2 lists `TurnLedger` in its model deliverables but the spec does not define a `TurnLedger` dataclass — it is referenced only as an executor concept. The roadmap elevates it to a first-class model without a spec-defined interface.
- **Spec Quote**: `ledger = TurnLedger(initial_budget=config.max_turns)` / `ledger.can_launch()` — referenced inline in executor pseudocode only; no dataclass definition provided.
- **Roadmap Quote**: `Implement core domain models: ... TurnLedger — all extending pipeline base types (AC-003, NFR-016)`
- **Impact**: Roadmap implies `TurnLedger` extends pipeline base types (`PipelineConfig` etc.), which the spec does not specify. This could produce an incompatible interface if base types don't have a suitable parent.
- **Recommended Correction**: Note that `TurnLedger` is an executor-internal class without a spec-defined dataclass interface. Do not assert it extends pipeline base types without Phase 0 confirmation.

---

### DEV-007
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 7 omits the `panel-report.md` additional output file from its deliverables list, listing only `review.py`, convergence state machine, scoring model, and `panel-report.md` — but the spec specifies this is a required output alongside the updated `portify-release-spec.md`, with its own gate implications.
- **Spec Quote**: `Additional output: panel-report.md with all findings, scores, convergence status.`
- **Roadmap Quote**: `panel-report.md` appears in the Phase 7 deliverables list — **this deviation is partially correct**: it IS listed. However, the roadmap omits specifying that `panel-report.md` must be emitted even in the ESCALATED case.
- **Impact**: MEDIUM — the ESCALATED path (`status: partial`) must still produce `panel-report.md` so the return contract can reference it. The roadmap does not explicitly cover this requirement.
- **Recommended Correction**: Add explicit note in Phase 7 that `panel-report.md` is required on both CONVERGED and ESCALATED terminal conditions.

---

### DEV-008
- **Severity**: MEDIUM
- **Deviation**: The roadmap maps SC-012 (`--dry-run` limits) to Phase 9 for validation, but dry-run filtering logic is implemented in Phase 2 (executor skeleton). Testing it only at Phase 9 leaves the logic unvalidated across Phases 2–8.
- **Spec Quote**: `if config.dry_run: steps = [s for s in steps if s.phase_type in (PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION)]`
- **Roadmap Quote**: `SC-012: --dry-run limits to correct phase types / Phase 9 / Integration test: assert no Phase 3–4 artifacts produced`
- **Impact**: The dry-run executor logic is coded in Phase 2 but not validated until Phase 9, leaving 7 phases of implementation without coverage of this behavior. A bug here affects all long-running phases.
- **Recommended Correction**: Add SC-012 dry-run validation to the Phase 2 milestone or add a unit test task in Phase 2 scope.

---

### DEV-009
- **Severity**: MEDIUM
- **Deviation**: The roadmap omits the `PortifyResult.resume_command()` method's exact CLI command format from its Phase 2 scope, referencing it only as `resume_command()` without specifying the `--max-turns {self.suggested_resume_budget}` computed field.
- **Spec Quote**: `def resume_command(self) -> str | None: ... return f"superclaude cli-portify run --workflow {self.config.workflow_path} --name {self.config.cli_name} --resume {self.halt_step} --max-turns {self.suggested_resume_budget}"`
- **Roadmap Quote**: `Implement resume_command() with exact CLI command (NFR-010)`
- **Impact**: The roadmap correctly identifies the requirement but does not reproduce the computed `suggested_resume_budget` linkage. An implementer may emit a static turn count rather than a dynamic computation.
- **Recommended Correction**: Include the `suggested_resume_budget` formula (`remaining * 25`) explicitly in Phase 2 action items.

---

### DEV-010
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 6 references "6a–6d" sub-step numbering but renumbers them from the spec's "3a–3d" without noting the discrepancy, which may confuse implementers cross-referencing with the spec's SKILL.md mapping table.
- **Spec Quote**: `Sub-steps within single Claude call: 1. 3a: Load template... 2. 3b: Populate 13 template sections... 3. 3c: Automated brainstorm pass... 4. 3d: Gap incorporation`
- **Roadmap Quote**: `6a: working copy creation / 6b: populate all 13 template sections / 6c: 3-persona brainstorm pass / 6d: incorporate actionable findings`
- **Impact**: The SKILL.md mapping table uses 3a–3d notation. Prompt builders referencing these sub-steps may use inconsistent numbering in output artifacts, causing gate mismatches.
- **Recommended Correction**: Use spec-native 3a–3d numbering in Phase 6, or explicitly note the renaming.

---

### DEV-011
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds OQ-008 resolution as a prerequisite for Phase 6 template handling, but does not include the >50KB template file-argument mechanism as an explicit action item with an implementation note.
- **Spec Quote**: `References release-spec-template.md (loads via --file arg if >50KB)`
- **Roadmap Quote**: `Handle templates >50KB via file argument passing (R-011); confirm mechanism from Phase 0 OQ-008`
- **Impact**: The mechanism is acknowledged but deferred to an open question resolution without specifying where or how the `--file` argument is passed to the Claude subprocess. This leaves implementation ambiguous.
- **Recommended Correction**: Add explicit action: "Implement `--file` argument passing for templates exceeding 50KB in `build_release_spec_prompt()`."

---

### DEV-012
- **Severity**: MEDIUM
- **Deviation**: The roadmap does not include `PASS_NO_REPORT` as a non-failing status in the executor's failure handling gate check, though the spec explicitly lists it alongside `PASS` and `PASS_NO_SIGNAL` as acceptable outcomes.
- **Spec Quote**: `if step_result.status not in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL, PortifyStatus.PASS_NO_REPORT, PortifyStatus.SKIPPED)`
- **Roadmap Quote**: `Failure handling / if step_result.status not in (PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, SKIPPED)` — **correction**: the roadmap does include this correctly in Phase 2 action item 8. However, the Phase 3 per-gate check mapping table omits `PASS_NO_REPORT` from the retry trigger discussion.
- **Impact**: LOW-MEDIUM. The executor handles it correctly but the gate system discussion may not trigger retries appropriately for `PASS_NO_REPORT` vs `PASS_NO_SIGNAL`.
- **Recommended Correction**: Clarify in Phase 3 that `PASS_NO_REPORT` (artifact present, no result file) does not trigger retry, unlike `PASS_NO_SIGNAL` (result file present, no EXIT_RECOMMENDATION).

---

### DEV-013
- **Severity**: LOW
- **Deviation**: The roadmap's Phase 3 per-gate check mapping table omits G-000, G-001, G-003, G-004, and G-009 rows entirely, presenting an incomplete reference table.
- **Spec Quote**: `GATE_G000: SemanticCheck("valid_yaml_config", has_valid_yaml_config...)` / `GATE_G001: SemanticCheck("component_inventory", has_component_inventory...)` / `GATE_G004: SemanticCheck("approval_status", has_approval_status...)` / `GATE_G009: SemanticCheck("approval_status", has_approval_status...)`
- **Roadmap Quote**: Table begins at G-002 with no rows for G-000, G-001, G-003, G-004, G-009.
- **Impact**: The table is explicitly framed as an "inline reference" — its incompleteness may lead implementers to believe these gates have no semantic checks.
- **Recommended Correction**: Add all 12 gates to the per-gate check mapping table, or note explicitly that omitted gates have checks defined in the spec directly.

---

### DEV-014
- **Severity**: LOW
- **Deviation**: The roadmap uses "Phase 3" and "Phase 4" labels for the synthesis and panel review steps in the `_build_steps()` notes, diverging from the spec's flat 12-step labeling.
- **Spec Quote**: Step descriptions use step IDs only (`release-spec-synthesis`, `spec-panel-review`), with `PortifyPhaseType` enum values for classification.
- **Roadmap Quote**: `7b: Focus incorporation (CRITICAL/MAJOR/MINOR routing)` — internal "7a–7d" sub-step labeling (roadmap-invented, not in spec).
- **Impact**: Minor. Sub-step numbering within Phase 7 doesn't match any spec artifact format requirement, but won't break implementation.
- **Recommended Correction**: Use spec-native labeling (4a–4d) for panel review sub-steps, consistent with SKILL.md.

---

### DEV-015
- **Severity**: LOW
- **Deviation**: The roadmap lists D-005 as absent from its dependency table without explanation; the spec's module plan and integration plan reference no D-005.
- **Spec Quote**: `[No D-005 in spec]`
- **Roadmap Quote**: The dependency table jumps from D-004 to D-006, omitting D-005 with no note.
- **Impact**: Cosmetic. No functional impact, but creates a gap in the dependency numbering that may confuse future readers.
- **Recommended Correction**: Either add a note explaining D-005 was intentionally omitted (reserved/unused), or renumber dependencies sequentially.

---

## Summary

**Total deviations: 15** (4 HIGH, 8 MEDIUM, 3 LOW)

**HIGH severity findings** are concentrated in two areas: missing enumerations (`PortifyPhaseType`, `ConvergenceState`) from the model deliverables, introduction of undocumented modules (`failures.py`, `resume.py`, `contract.py`) not in the spec's module plan, and incomplete gate check coverage in the Phase 3 per-gate mapping table (G-010 `brainstorm_section` and G-011 missing entirely).

**MEDIUM severity findings** are primarily organizational: phase numbering misalignment with spec-internal naming, `TurnLedger` type assertion, dry-run validation timing, sub-step renumbering in Phase 6, and incomplete template handling specification.

**LOW severity findings** are cosmetic: incomplete per-gate table rows, internal sub-step label mismatch, and dependency numbering gap.

The roadmap is architecturally sound and covers the majority of functional requirements correctly. The HIGH severity items must be resolved before implementation proceeds, as the missing enums affect the executor's phase routing and convergence state machine, and the module plan deviation would produce an architecture incompatible with the spec's integration contract.
