---
high_severity_count: 0
medium_severity_count: 8
low_severity_count: 5
total_deviations: 16
validation_complete: true
tasklist_ready: true
---

## Deviation Report

### DEV-001
- **ID**: DEV-001
- **Severity**: ~~HIGH~~ RESOLVED
- **Deviation**: Roadmap Phase 1 introduces a "Shared utility layer" work item (section hashing, frontmatter parsing helpers, line counting helpers) that has no corresponding specification requirement. More critically, the roadmap's Section 4.6 Implementation Order references files (`config.py`, `inventory.py`, `tui.py`, `logging_.py`, `diagnostics.py`, `commands.py`) that do not exist in the spec's Section 4.1 New Files table (which uses the DEV-001-accepted 18-module layout with `steps/` subdirectory and unified `monitor.py`).
- **Resolution**: Spec Section 4.6 replaced with implementation order matching the accepted 18-module structure: `models.py` → `convergence.py`, `resume.py`, `contract.py` (parallel) → `gates.py`, `prompts.py` (parallel) → `process.py`, `monitor.py` (parallel) → `steps/*.py` → `executor.py` → `cli.py` → `__init__.py` → `main.py` patch. Old filenames (`config.py`, `inventory.py`, `tui.py`, `logging_.py`, `diagnostics.py`, `commands.py`) removed.

### DEV-002
- **ID**: DEV-002
- **Severity**: ~~HIGH~~ RESOLVED
- **Deviation**: The roadmap omits the spec's explicit requirement that the `has_section_12` gate must validate structural content, not just heading presence. The spec's FR-PORTIFY-CLI.6 acceptance criterion [F-007] requires the gate to verify either a findings table (with Gap ID column) or the literal zero-gap summary text.
- **Resolution**: Roadmap Phase 5 Work Item 1 gate description updated to include explicit F-007 language: "must contain either a findings table (with Gap ID column) or the literal zero-gap summary text — heading-only content MUST fail the gate".

### DEV-003
- **ID**: DEV-003
- **Severity**: HIGH
- **Deviation**: The roadmap omits the spec's requirement for retry prompt augmentation on `synthesize-spec` gate failure (finding F-005). The spec requires that on gate failure due to remaining placeholders, the retry prompt includes the specific placeholder names.
- **Spec Quote**: FR-PORTIFY-CLI.5: "On gate failure (remaining placeholders), retry prompt includes the specific placeholder names that remain, enabling targeted fix rather than blind re-run [F-005]"
- **Roadmap Quote**: Phase 4 Work Item 3: "On gate failure: retry prompt includes specific remaining placeholder names." — present in Phase 4 but absent from Phase 3 prompt builder framework which states "Include retry augmentation for targeted failures (especially placeholder residue)" without specifying the placeholder-name-injection mechanism.
- **Impact**: After re-reading, the roadmap does mention this in Phase 4 Work Item 3. Downgrading — however, the prompt builder framework in Phase 3 ("retry augmentation for targeted failures") does not cross-reference the F-005 requirement identifier, creating traceability risk. This is actually adequately covered. Reclassifying.
- **Recommended Correction**: *(Withdrawn — adequately covered in Phase 4 Work Item 3. Cross-reference F-005 identifier for traceability.)*

**Revised DEV-003**:
- **ID**: DEV-003
- **Severity**: ~~HIGH~~ RESOLVED
- **Deviation**: The roadmap's SC validation matrix (Phase 7) did not include a test for the `_has_section_12` structural validation requirement [F-007], nor for the convergence per-iteration independent timeout behavior [F-004]. The SC validation matrix had 14 entries (SC-001 through SC-014) but neither F-007 nor F-004 appeared as explicit validation criteria.
- **Resolution**: Added SC-015 (F-007 structural content validation: gate rejects heading-only Section 12, accepts findings table with Gap ID column, accepts zero-gap summary text) and SC-016 (F-004 per-iteration independent timeout: each convergence iteration gets independent timeout default 300s, not total divided by max_convergence) to the SC validation matrix in Phase 7.

### DEV-004
- **ID**: DEV-004
- **Severity**: MEDIUM
- **Deviation**: The roadmap introduces a "Phase 0: Architecture Confirmation and Decision Record" phase that does not exist in the specification. While the spec has open items (Section 11) and notes requiring Phase 0 decisions, it does not define a formal phase for resolving them.
- **Spec Quote**: Section 11 Open Items: "GAP-005 ... Resolution Target: Implementation phase"; Section 4.1 Architecture Note: "DEV-001 accepted, 2026-03-13"
- **Roadmap Quote**: "Phase 0: Architecture Confirmation and Decision Record — Objective: Resolve blocking spec ambiguities and lock module layout before code changes. This lightweight phase (0.5-1 day, S)"
- **Impact**: Low risk — this is a reasonable roadmap addition that front-loads decision-making. However, the spec's downstream inputs (Section 10) expect 5 phases, not 8. Tasklist generation may misalign.
- **Recommended Correction**: Acceptable deviation. Note in the roadmap that Phase 0 is a roadmap-only addition not present in the spec, and adjust downstream phase counts accordingly.

### DEV-005
- **ID**: DEV-005
- **Severity**: MEDIUM
- **Deviation**: The spec defines 7 pipeline steps across 4 phases (Phase 0: Steps 1-2, Phase 1: Step 3, Phase 2: Step 4, Phase 3: Steps 5-6, Phase 4: Step 7). The roadmap defines 8 phases (Phase 0-7) with different step-to-phase mappings: Phase 2 covers Steps 1-2, Phase 4 covers Steps 3-5, Phase 5 covers Steps 6-7.
- **Spec Quote**: Section 2.2 Workflow/Data Flow shows phases implicitly: Steps 1-2 have no Claude subprocess, Steps 3-4 are analysis/design, Step 5 is synthesis, Steps 6-7 are quality. Section 10: "Milestone 1: Core models, gates, and pure-programmatic steps (FR-1, FR-2) ... Milestone 4: Executor, TUI, logging, diagnostics"
- **Roadmap Quote**: "Phase 2: Fast Deterministic Pipeline Steps ... Phase 4: Core Content Generation Steps (Steps 3-5) ... Phase 5: Quality Amplification Steps (Steps 6-7)"
- **Impact**: The roadmap's phasing is a valid restructuring for implementation purposes. However, the spec's Section 10 downstream inputs define 4 milestones which don't map 1:1 to the roadmap's 8 phases, potentially confusing tasklist generation.
- **Recommended Correction**: Add a mapping table in the roadmap showing how spec milestones (Section 10) map to roadmap phases.

### DEV-006
- **ID**: DEV-006
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 3 introduces a "Claude subprocess mock harness" work item that is not specified in the spec. While useful for development, it adds unspecified scope.
- **Spec Quote**: '[MISSING]' — no mention of mock harness in spec
- **Roadmap Quote**: Phase 3 Work Item 4: "Build Claude subprocess mock harness — Returns known-good outputs for each step type. Enables unit testing of all Claude-assisted steps without actual Claude invocations."
- **Impact**: Low risk — this is infrastructure tooling that supports testing. However, it is unspecified scope that consumes implementation time.
- **Recommended Correction**: Acceptable deviation. Note as implementation-phase tooling decision.

### DEV-007
- **ID**: DEV-007
- **Severity**: MEDIUM
- **Deviation**: The spec's Section 5.1 CLI Surface defines `WORKFLOW` as a positional argument (`PATH (argument)`), while the roadmap's Phase 1 CLI registration describes it as an option with `--start` for resume.
- **Spec Quote**: Section 5.1: "WORKFLOW | PATH (argument) | required | Path to skill directory to portify"
- **Roadmap Quote**: Phase 1 Work Item 2: "Define options: workflow path, output directory, `--dry-run`, `--skip-review`, `--start`, convergence/budget controls, timeout controls"
- **Impact**: The `--start` option for resume is implied by the spec's resume_command output (`--resume --start {self.halt_step}`) but not listed in Section 5.1 CLI Surface. The roadmap adds `--start` and `--resume` which are needed but unspecified in the CLI surface table.
- **Recommended Correction**: Add `--resume` (FLAG) and `--start` (STRING) to the spec's Section 5.1 CLI Surface table, matching the resume_command pattern in Section 4.5.

### DEV-008
- **ID**: DEV-008
- **Severity**: MEDIUM
- **Deviation**: The roadmap's convergence engine is described as a "standalone, testable component" extracted from the panel-review step. The spec defines convergence logic inline within FR-PORTIFY-CLI.7 and the executor, with `convergence.py` containing only the ConvergenceState enum and transition dictionary.
- **Spec Quote**: Section 4.1: "`convergence.py` — ConvergenceState enum (READY, ITERATING, CONVERGED, ESCALATED, FAILED) with valid-transition dictionary and transition assertion"
- **Roadmap Quote**: Phase 5 Work Item 2: "Implement convergence engine (standalone component) — Extract convergence logic (predicate checking, budget guards, escalation) into a testable engine independent of Claude subprocess management."
- **Impact**: The roadmap expands `convergence.py` beyond its spec-defined scope (enum + transitions) to include predicate checking and budget guards. This changes the module boundary defined in the spec.
- **Recommended Correction**: Clarify whether convergence predicate logic belongs in `convergence.py` (roadmap) or `executor.py` (spec). If the roadmap's extraction is preferred, update the spec's Section 4.1 convergence.py description.

### DEV-009
- **ID**: DEV-009
- **Severity**: MEDIUM
- **Deviation**: The roadmap introduces a "signal vocabulary" concept in Phase 0 and Phase 1 that is partially aligned with the spec's GAP-008 open item but resolves it earlier than the spec intended.
- **Spec Quote**: Section 11 Open Items: "GAP-008 | NDJSON signal patterns for monitor.py ... Resolution Target: Implementation phase: define signal vocabulary during monitor.py development"
- **Roadmap Quote**: Phase 0 Work Item 4: "Define minimal signal vocabulary — Initial constants: `step_start`, `step_complete`, `step_error`, `step_timeout`, `gate_pass`, `gate_fail`. Extend during Phase 3."
- **Impact**: The roadmap front-loads signal vocabulary definition, which is reasonable but changes the spec's intended resolution timeline. Minor alignment issue.
- **Recommended Correction**: Acceptable deviation — front-loading is an improvement. Note that GAP-008 is partially resolved in Phase 0/1 with extension in Phase 3.

### DEV-010
- **ID**: DEV-010
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds a "Recommendation #5" to validate template existence at startup, which is not in the spec's FR-PORTIFY-CLI.1 (validate-config). The spec only validates workflow path, name derivation, output directory, and name collision in Step 1.
- **Spec Quote**: FR-PORTIFY-CLI.1 acceptance criteria list 6 items: workflow path, name derivation, output directory, collision detection, result JSON, timing
- **Roadmap Quote**: Phase 4 Work Item 3: "Verify `release-spec-template.md` exists (fail-fast if missing — gate at startup per Recommendation #5)." Architectural Recommendation 5: "Gate the `release-spec-template.md` dependency at startup."
- **Impact**: Template validation at startup is a good practice but is not in the spec's validate-config step. This adds a new validation to Step 1 that isn't specified.
- **Recommended Correction**: Either add template existence check to FR-PORTIFY-CLI.1 acceptance criteria, or clarify in the roadmap that this is an implementation-phase enhancement beyond spec.

### DEV-011
- **ID**: DEV-011
- **Severity**: MEDIUM
- **Deviation**: The spec's `_has_section_12` semantic check function (Section 5.2.1) checks for `"## 12."` or `"## Brainstorm Gap Analysis"`, but the F-007 acceptance criterion requires structural validation (findings table or zero-gap text). The semantic check implementation doesn't match the acceptance criterion.
- **Spec Quote**: Section 5.2.1: `def _has_section_12(content: str) -> bool: return "## 12." in content or "## Brainstorm Gap Analysis" in content`; FR-PORTIFY-CLI.6 [F-007]: "must contain either a findings table (with Gap ID column) or the literal zero-gap summary text — heading alone is insufficient"
- **Roadmap Quote**: '[MISSING]' — roadmap does not address this internal spec inconsistency
- **Impact**: The spec itself has an internal inconsistency between the semantic check implementation and the F-007 requirement. The roadmap should have flagged this and specified which is authoritative.
- **Recommended Correction**: The roadmap should note this spec inconsistency and specify that the `_has_section_12` implementation must be updated to match F-007 (check for findings table or zero-gap text, not just heading presence). Add this to Phase 5 work items.

### DEV-012
- **ID**: DEV-012
- **Severity**: LOW
- **Deviation**: The roadmap uses "SC-012" for the async prohibition check, but the spec uses "SC-012" for the downstream readiness boundary test (7.0/6.9). The SC numbering is inconsistent between the two documents.
- **Spec Quote**: Section 4.5 PortifyResult: "Downstream ready gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false) (SC-012)"
- **Roadmap Quote**: Phase 7 SC validation matrix: "SC-012 | Zero `async def`/`await` in `cli_portify/` | Static | grep scan"
- **Impact**: SC identifier collision. SC-012 refers to different requirements in spec vs roadmap. This creates traceability confusion.
- **Recommended Correction**: Renumber the roadmap's SC validation matrix to match the spec's SC identifiers, or create a unified numbering scheme.

### DEV-013
- **ID**: DEV-013
- **Severity**: LOW
- **Deviation**: The spec defines `PortifyConfig.stall_timeout: int = 120` and `stall_action: str = "kill"`, but the roadmap does not reference stall detection or stall_action behavior anywhere.
- **Spec Quote**: Section 4.5: `stall_timeout: int = 120  # Seconds before stall detection` and `stall_action: str = "kill"`
- **Roadmap Quote**: '[MISSING]'
- **Impact**: Minor — stall detection is a monitoring concern that may be implicitly handled by the monitor/diagnostics layer, but the specific stall_action="kill" behavior is unaddressed.
- **Recommended Correction**: Add stall detection behavior to Phase 3 monitoring work items or Phase 6 operational hardening.

### DEV-014
- **ID**: DEV-014
- **Severity**: LOW
- **Deviation**: The spec's Section 8.1 test file paths use `tests/cli_portify/test_config.py` and `tests/cli_portify/test_executor.py`, but the roadmap does not specify test file organization.
- **Spec Quote**: Section 8.1: "test_config_load | tests/cli_portify/test_config.py", "test_convergence_converges | tests/cli_portify/test_executor.py"
- **Roadmap Quote**: '[MISSING]' — test file paths not specified
- **Impact**: Minor — test organization is an implementation detail, but the spec provides explicit paths that should be followed.
- **Recommended Correction**: Add test file paths to Phase 7 work items to match spec Section 8.1.

### DEV-015
- **ID**: DEV-015
- **Severity**: LOW
- **Deviation**: The roadmap adds "Team/Role Requirements" (architect, backend, QA, UX contributor) that are not in the spec.
- **Spec Quote**: '[MISSING]'
- **Roadmap Quote**: "Team/Role Requirements: 1. Architect / lead implementer... 2. Backend/Python implementer... 3. QA engineer... 4. Optional UX/TUI contributor"
- **Impact**: No impact on correctness — this is reasonable roadmap supplementary information.
- **Recommended Correction**: No action needed.

### DEV-016
- **ID**: DEV-016
- **Severity**: LOW
- **Deviation**: The roadmap total timeline is "12-18 days" across 8 phases, while the spec's Section 10 downstream inputs suggest 5 phases with "14-17 tasks". These are different planning units but could cause confusion.
- **Spec Quote**: Section 10: "Estimated total: 14-17 tasks across 5 phases"
- **Roadmap Quote**: "Total: 12-18 days" across 8 phases
- **Impact**: Minor — different planning granularity. The spec counts tasks, the roadmap counts days. Phase count mismatch (5 vs 8) could confuse downstream consumers.
- **Recommended Correction**: Add a mapping note showing how spec's 5 downstream phases map to roadmap's 8 implementation phases.

---

## Summary

**Severity Distribution**: ~~3 HIGH~~, 8 MEDIUM, 5 LOW (16 total — 3 HIGH resolved, 0 HIGH remaining)

**Resolved Findings**:

1. **DEV-001 (RESOLVED)**: Spec Section 4.6 Implementation Order updated to match the accepted 18-module structure with `steps/` subdirectory and unified `monitor.py`. Old filenames removed.

2. **DEV-002 (RESOLVED)**: Roadmap Phase 5 brainstorm-gaps gate description updated with explicit F-007 structural validation requirement (findings table with Gap ID column or zero-gap summary text; heading-only fails).

3. **DEV-003 (RESOLVED)**: SC validation matrix extended with SC-015 (F-007 structural content validation) and SC-016 (F-004 per-iteration independent timeout).

**Tasklist Readiness**: **READY** — All HIGH severity deviations resolved. Remaining MEDIUM and LOW deviations are either acceptable roadmap additions (DEV-004, DEV-006, DEV-009, DEV-010, DEV-015) or minor alignment issues that do not block implementation.
