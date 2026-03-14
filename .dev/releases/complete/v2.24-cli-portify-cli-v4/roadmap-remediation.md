---
deviations_addressed: DEV-002, DEV-003, DEV-008
severity_resolved: HIGH (x2), MEDIUM (x1)
source_agents: agent-2-dev-002, agent-3-dev-003
status: ready-to-apply
---

# Roadmap Remediation Plan — DEV-002, DEV-003, DEV-008

## Overview

This document merges the findings from two parallel brainstorm agents into a single
actionable remediation plan for the roadmap (`roadmap.md`). Both deviations are genuine
slips — they have zero coverage in the debate transcript, diff analysis, or
base-selection artifacts. Neither architect was tasked with auditing model or gate
completeness; both operated at the architectural level and these spec-defined
implementation contracts fell through.

| Deviation | Severity | Patch Location | Lines Changed |
|-----------|----------|---------------|---------------|
| DEV-002 | HIGH | Phase 1 — Domain Models | Replace 3-bullet block |
| DEV-003 | HIGH | Phase 2 — Gate Infrastructure | Add sub-section after existing bullets |
| DEV-008 | MEDIUM | Phase 2 — Gate Infrastructure | Covered by DEV-003 patch |

---

## Patch 1: DEV-002 — Domain Models Completeness (Phase 1)

### What to Change

In `roadmap.md`, locate `#### Domain Models (`models.py`)` in Phase 1.

**Replace this block:**

```
#### Domain Models (`models.py`)

- Define `PortifyConfig`, `ComponentInventory`, `PortifyResult`, return contract dataclass
- Gate function signature: `tuple[bool, str]` throughout (NFR-004)
- Include `resumable` flag and `resume_context` field on `StepResult` from the start (debate-resolved: additive fields designed early to avoid Phase 3 retrofitting)
```

**With this block:**

```markdown
#### Domain Models (`models.py`)

Define all 6 spec-defined domain models per Section 4.5. All types live in `models.py`
with no internal dependencies; every other module imports from here. See Section 4.5
for complete field types, default values, and method implementations (~280 lines). All
class signatures must match the spec exactly to preserve gate and executor compatibility.

**`PortifyConfig`** (extends `PipelineConfig`) — pipeline configuration with required
workflow identity fields (`workflow_path`, `cli_name`, `module_name`, `output_dir`),
behavioral controls (`skip_review`, `max_convergence`), budget fields (`max_turns`,
`stall_timeout`, `stall_action`), and 6 derived path properties (`analysis_file`,
`spec_file`, `prompts_file`, `release_spec_file`, `panel_report_file`, `template_path`).

**`PortifyStatus`** (Enum) — 13 values: 10 base pipeline states (`PENDING`, `RUNNING`,
`PASS`, `PASS_NO_SIGNAL`, `PASS_NO_REPORT`, `INCOMPLETE`, `HALT`, `TIMEOUT`, `ERROR`,
`SKIPPED`) plus 3 domain-specific states: `VALIDATION_FAIL` (Step 1 config validation
failed), `USER_REJECTED` (user rejected at review gate), `CONVERGENCE_EXHAUSTED` (3
iterations without resolution). The domain-specific values are used in precise
conditional logic in the executor and resume logic — they must be named exactly as
specified. Full enum in spec Section 4.5.

**`PortifyOutcome`** (Enum) — 6 terminal outcomes: `SUCCESS`, `PARTIAL` (convergence
escalated but run completed), `HALTED`, `INTERRUPTED`, `ERROR`, `DRY_RUN`. Note:
`PARTIAL` is distinct from `HALTED` — it means the panel review reached max iterations
without convergence but did not crash.

**`PortifyStepResult`** (extends `StepResult`) — per-step result. Fields: `status`
(`PortifyStatus`), `exit_code`, `started_at`, `finished_at`, `output_bytes`,
`error_bytes`, `convergence_iteration` (panel-review step only), `quality_scores`
(panel-review step only), `gate_details`. Properties: `duration_seconds` (computed
from timestamps). Include `resumable` flag and `resume_context` from the start
(debate-resolved: additive fields designed early to avoid Phase 3 retrofitting).

**`PortifyResult`** — aggregate pipeline result. Fields: `config`, `step_results`,
`outcome`, `started_at`, `finished_at`, `halt_step`, `convergence_state`,
`convergence_iterations`, `quality_scores`, `phase_timing`, `warnings`. Properties:
`downstream_ready` (overall score >= 7.0), `suggested_resume_budget` (remaining PENDING
steps × 30). Methods (all spec-defined, see Section 4.5 for full implementations):
`to_contract() -> dict` (emits 18-field return contract schema), `resume_command() ->
str | None` (generates CLI resume invocation), `_phase_contracts()` (maps 7 step IDs
to phase_0–phase_4 contract statuses), `_failure_phase()`, `_failure_type()`,
`_resume_phase()`, `_resume_substep()`.

**`PortifyMonitorState`** — TUI/monitor state tracking for the live dashboard (primary
consumer: `monitor.py`, Phase 2). Fields: `output_bytes`, `output_bytes_prev`,
`last_growth_time`, `last_event_time`, `step_started_at`, `events_received`,
`lines_total`, `growth_rate_bps`, `stall_seconds`, plus domain-specific:
`current_phase`, `current_persona`, `convergence_iteration`, `placeholders_remaining`,
`sections_populated`. Property: `stall_status` (returns "waiting...", "thinking...",
"STALLED", or "active" based on growth rate thresholds). Define in Phase 1 alongside
other models; instantiated in Phase 2.

> **Note on `ComponentInventory`**: The component discovery step (`discover_components.py`)
> emits `component-inventory.md` as a file artifact; this does not require a shared domain
> model in `models.py`. If the step implementation benefits from a local typed struct to
> hold inventory data in memory before writing the artifact, define it as a private
> dataclass within `discover_components.py` — it is not part of the shared domain model.

- Gate function signature: `tuple[bool, str]` throughout (NFR-004)
```

### What This Resolves

- **DEV-002 (HIGH)**: All 6 spec models now named; key non-obvious contracts called out; Section 4.5 reference explicit
- **DEV-004 (MEDIUM)**: `ComponentInventory` removed from shared model list; redirected to step-local implementation note

### Deviations This Does NOT Resolve

- **DEV-005 (MEDIUM)**: `to_contract()` placement — the roadmap still has a separate `contract.py` module. The patch accurately attributes `to_contract()` to `PortifyResult` per spec, which sharpens the DEV-005 conflict. DEV-005 must be resolved as a separate architectural decision: either revert `contract.py` to a method on the model (per spec), or formally document the extraction as an accepted roadmap enhancement. Do not silently paper over it here.

### Agent 2 Risk Notes

1. **`resumable` field inheritance**: The existing roadmap note about `resumable` and `resume_context` references debate resolution, but the spec's `PortifyStepResult` may inherit these from the base `StepResult`. Implementer should verify whether `resumable` needs to be re-declared or is inherited before finalizing `models.py`.

2. **Enum count**: Agent 2 found 13 values in `PortifyStatus` (not 11 as stated in the original DEV-002 description). The spec is the source of truth; use 13.

---

## Patch 2: DEV-003 + DEV-008 — Gate Infrastructure Completeness (Phase 2)

### Critical Pre-Finding (Agent 3)

Before applying this patch, note: **`_all_gates_defined()` is defined in spec Section
5.2.1 but is not assigned to any `GateCriteria` object in Section 5.2.2**, and does not
appear in the Section 5.2 gate-tier table. The spec has an orphaned function. The
roadmap must surface this without silently wiring it to an arbitrary gate.

### What to Change

In `roadmap.md`, locate `#### Gate Infrastructure (`gates.py` expansion)` in Phase 2.

**Keep the existing 4 bullets as-is:**
```
- STANDARD and STRICT gate semantic check functions
- YAML frontmatter parsing (PyYAML dependency)
- Section presence validation, line count enforcement
- Placeholder sentinel detection (`{{SC_PLACEHOLDER:*}}` -> SC-003)
```

**Append this new sub-section immediately after those bullets:**

```markdown
#### Gate Contract (spec Sections 5.2.1 and 5.2.2)

The spec defines 8 semantic check functions (Section 5.2.1, full implementations) and
7 `GateCriteria` objects (Section 5.2.2) that compose them. All must be implemented
in `gates.py`. Function bodies are in the spec; the tables below define the
architectural contracts.

**Semantic Check Functions** — implement exactly per spec Section 5.2.1:

| Function | Purpose | Spec Link |
|----------|---------|-----------|
| `_has_required_analysis_sections` | Verifies 5 required `##` sections present in `portify-analysis.md` | FR-003 |
| `_has_data_flow_diagram` | Verifies `-->` or `--->` arrow notation is present | FR-003 |
| `_has_step_mappings` | Verifies `Step(` or `step-` present in design artifact | FR-004 |
| `_all_gates_defined` | Verifies every step id has a corresponding gate definition | See note |
| `_zero_placeholders` | Verifies zero `{{SC_PLACEHOLDER:*}}` sentinels remain | SC-003 |
| `_has_section_12` | Verifies Section 12 (Brainstorm Gap Analysis) is present with content | FR-006 |
| `_quality_scores_valid` | Verifies 5-field quality_scores block present in YAML frontmatter | SC-012 |
| `_overall_is_mean` | Verifies overall == mean(clarity, completeness, testability, consistency) within 0.01 | SC-010 |

> **Note on `_all_gates_defined`**: This function is defined in spec Section 5.2.1 but
> is not assigned to any `GateCriteria` object in Section 5.2.2 and does not appear in
> the Section 5.2 gate table. Implement the function body per spec; its gate assignment
> (likely `DESIGN_PIPELINE_GATE`) requires spec clarification before wiring. Do not
> invent an assignment.

**GateCriteria Objects** — implement exactly per spec Section 5.2.2:

| Object Name | Tier | Frontmatter Required | Min Lines | Semantic Checks |
|-------------|------|---------------------|-----------|-----------------|
| `VALIDATE_CONFIG_GATE` | EXEMPT | none | 0 | none |
| `DISCOVER_COMPONENTS_GATE` | STANDARD | `source_skill`, `component_count` | 5 | none |
| `ANALYZE_WORKFLOW_GATE` | STRICT | `source_skill`, `step_count`, `parallel_groups`, `gate_count`, `complexity` | 100 | `_has_required_analysis_sections`, `_has_data_flow_diagram` |
| `DESIGN_PIPELINE_GATE` | STRICT | `step_mapping_count`, `model_count`, `gate_definition_count` | 200 | `_has_step_mappings` |
| `SYNTHESIZE_SPEC_GATE` | STRICT | `title`, `spec_type`, `complexity_class` | 150 | `_zero_placeholders` |
| `BRAINSTORM_GAPS_GATE` | STANDARD | none | 0 | `_has_section_12` |
| `PANEL_REVIEW_GATE` | STRICT | none | 0 | `_quality_scores_valid`, `_overall_is_mean` |
```

### What This Resolves

- **DEV-003 (HIGH)**: All 8 semantic check function names now explicitly listed with purpose and traceability; `_all_gates_defined()` surfaced with its spec-ambiguity noted
- **DEV-008 (MEDIUM)**: All 7 `GateCriteria` object names listed with their full compositions

### Agent 3 Risk Notes

1. **`_all_gates_defined()` ambiguity is a spec gap, not a roadmap gap.** The function exists in the spec but has no gate assignment. The note above correctly surfaces this without resolving it. If a spec clarification is issued before implementation, update the GateCriteria table to wire it appropriately.

2. **Minor naming inconsistency in spec**: Section 5.2.1 defines `_has_section_12` (with leading underscore); the `SemanticCheck` string key in Section 5.2.2 uses `has_section_12` (without). The roadmap uses the function name convention consistently. Implementers should verify which form the `SemanticCheck` constructor expects.

3. **Existing bullets overlap slightly** with the new sub-section (e.g., "Section presence validation" ↔ `_has_required_analysis_sections`). The existing bullets provide contextual framing; the table provides the precise contract. Both can coexist.

---

## Open Items Not Addressed by This Remediation

These deviations remain after applying both patches. They require separate decisions:

| DEV | Severity | Description | Recommended Next Step |
|-----|----------|-------------|----------------------|
| DEV-005 | MEDIUM | `to_contract()` extracted to `contract.py` vs spec's method on `PortifyResult` | Explicit architectural decision: accept extraction (update spec) or revert to method |
| DEV-006 | MEDIUM | `convergence.py` with `ConvergenceState` enum vs inline in executor | Accepted as debate-resolved (D-11) — document as enhancement in dev-001-accepted-deviation.md |
| DEV-007 | MEDIUM | `resume.py` as separate module vs methods on `PortifyResult` | Accepted as debate-resolved (D-12) — document as enhancement in dev-001-accepted-deviation.md |
| DEV-009 | MEDIUM | `monitor.py` merges `tui.py`/`logging_.py`/`diagnostics.py` | Debate-silent but architecturally coherent — document in accepted deviations |
| DEV-010 | MEDIUM | `diagnostics.py` absorbed into `monitor.py` | Same as DEV-009 |
| DEV-011 | MEDIUM | `--output` vs `--output-dir` CLI flag name | Low-effort fix: rename in roadmap Phase 1 Click CLI section |
| DEV-013 | MEDIUM | Test category grouping vs named test list | Add explicit test name list to Phase 6 matching spec Section 8.1 |
| DEV-014 | MEDIUM | Section hashing mechanism not in spec | Accepted as debate-resolved (D-14) — already in roadmap; spec should be updated |
| DEV-019 | LOW | 1MB file cap not in spec | Accepted implementation defense; annotate as enhancement in roadmap |
| DEV-020 | MEDIUM | Prompt builders not traced to Appendix C | Add explicit "see Appendix C" reference to Phase 2 prompt builders section |

---

## Applying the Patches

After both patches are applied to `roadmap.md`, re-run:

```bash
superclaude roadmap run .../portify-release-spec.md --resume
```

The `spec-fidelity` step will re-evaluate. Expected outcome:
- DEV-002 → resolved (HIGH removed)
- DEV-003 → resolved (HIGH removed)
- DEV-004 → resolved (MEDIUM removed, subsumed by DEV-002 patch)
- DEV-008 → resolved (MEDIUM removed)
- `high_severity_count` should drop from 3 to 0 (DEV-001 is handled by Agent 1's acceptance record)
- Gate should pass → pipeline proceeds to `extract`, `remediate`, `certify`
