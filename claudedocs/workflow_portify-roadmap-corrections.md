---
generated: 2026-03-14
source_doc: .dev/releases/backlog/portify-cli-portify/spec-fidelity.md
target_file: .dev/releases/backlog/portify-cli-portify/roadmap.md
correction_doc: .dev/releases/backlog/portify-cli-portify/spec-fidelity.md
verification_status: 14/15 accurate (DEV-003 has minor phase attribution error)
---

# Workflow: CLI Portify Roadmap Corrections

## Objective

Apply 15 targeted corrections to `roadmap.md` so it faithfully reflects the `portify-spec.md` source of truth. One correction also touches `spec-fidelity.md` to fix a minor inaccuracy in the report itself.

## Files Modified

| File | Edits |
|------|-------|
| `.dev/releases/backlog/portify-cli-portify/roadmap.md` | 14 targeted edits |
| `.dev/releases/backlog/portify-cli-portify/spec-fidelity.md` | 1 correction (DEV-003 phase attribution) |

---

## Phase 1 — HIGH Severity Corrections (4 tasks)

### TASK-001 — DEV-001: Add `PortifyPhaseType` to Phase 2 model deliverables

**File**: `roadmap.md`
**Section**: Phase 2 — Core Pipeline Model, Executor Skeleton, and Observability Baseline > Key Actions > Executor Skeleton > Action 1
**Current text**:
> Implement core domain models: `PortifyConfig`, `PortifyStep`, `PortifyStepResult`, `PortifyOutcome`, `PortifyStatus`, `MonitorState`, `TurnLedger` — all extending pipeline base types (AC-003, NFR-016)

**Corrected text**:
> Implement core domain models: `PortifyPhaseType`, `ConvergenceState`, `PortifyConfig`, `PortifyStep`, `PortifyStepResult`, `PortifyOutcome`, `PortifyStatus`, `MonitorState`, `TurnLedger` — all in `models.py` per spec module plan (AC-003, NFR-016). Note: `PortifyPhaseType` and `ConvergenceState` are enums required by executor phase routing and convergence state machine respectively.

**Verification**: Check that both `PortifyPhaseType` and `ConvergenceState` appear in action item 1.

---

### TASK-002 — DEV-002: (Covered by TASK-001 — both enums added in one atomic edit)

Handled jointly in TASK-001 to keep the model list contiguous.

---

### TASK-003 — DEV-003a: Remove `failures.py` from Phase 1 deliverables, fold into `models.py`/`config.py`

**File**: `roadmap.md`
**Section**: Phase 1 — Prerequisites, Discovery, and Config Foundation > Deliverables
**Current text**:
> - `failures.py` with all 5 error codes: `NAME_COLLISION`, `OUTPUT_NOT_WRITABLE`, `AMBIGUOUS_PATH`, `INVALID_PATH`, `DERIVATION_FAILED`

**Corrected text**:
> *(remove `failures.py` line entirely)*
> Add to `models.py` foundations bullet: `models.py` (including all 5 error code definitions: `NAME_COLLISION`, `OUTPUT_NOT_WRITABLE`, `AMBIGUOUS_PATH`, `INVALID_PATH`, `DERIVATION_FAILED` — see spec module plan; no separate `failures.py`)

**Verification**: `failures.py` does not appear in any deliverables list; error codes appear under `models.py` in Phase 1.

---

### TASK-004 — DEV-003b: Remove `resume.py` and `contract.py` from Phase 2 deliverables, fold into `executor.py`

**File**: `roadmap.md`
**Section**: Phase 2 — Core Pipeline Model, Executor Skeleton, and Observability Baseline > Deliverables
**Current text**:
```
- `models.py`
- `process.py`
- `executor.py`
- `resume.py`
- `contract.py`
- `monitor.py` (baseline)
- `logging_.py` (skeleton)
- `tui.py` (lifecycle)
```
**Corrected text**:
```
- `models.py`
- `process.py`
- `executor.py` (includes resume logic and return-contract emission per spec module plan)
- `monitor.py` (baseline)
- `logging_.py` (skeleton)
- `tui.py` (lifecycle)
```

**Verification**: `resume.py` and `contract.py` do not appear in any deliverables list; a note in `executor.py` line references their absorption.

---

### TASK-005 — DEV-003c: Fix spec-fidelity.md DEV-003 phase attribution error

**File**: `spec-fidelity.md`
**Section**: DEV-003 body
**Current text**:
> The roadmap introduces a `failures.py` module not present in the spec's module plan... `failures.py` with all 5 error codes (Phase 2 Deliverables)

**Corrected text**:
> Change "Phase 2 Deliverables" to "Phase 1 Deliverables" — `failures.py` appears in the roadmap's Phase 1 deliverables list, not Phase 2.

**Verification**: DEV-003 correctly states `failures.py` is in Phase 1 deliverables.

---

### TASK-006 — DEV-004: Fix Phase 3 per-gate check mapping table

**File**: `roadmap.md`
**Section**: Phase 3 — Gate System and Semantic Validation Layer > Key Actions > Per-Gate Check Mapping table
**Current table** (relevant rows):
```
| G-010 | `EXIT_RECOMMENDATION` marker present; `has_zero_placeholders` (zero `{{SC_PLACEHOLDER:*}}` sentinels) |
```
G-011 row: absent

**Corrected table**:
```
| G-010 | `EXIT_RECOMMENDATION` marker present; `has_zero_placeholders` (zero `{{SC_PLACEHOLDER:*}}` sentinels); `has_brainstorm_section` (Section 12 Brainstorm Gap Analysis present) |
| G-011 | `has_quality_scores` (clarity, completeness, testability, consistency, overall); `has_criticals_addressed` (all CRITICAL findings marked [INCORPORATED] or [DISMISSED]) |
```

**Verification**: G-010 has 3 checks matching spec lines 662–666; G-011 row is present with 2 checks matching spec lines 674–675.

---

## Phase 2 — MEDIUM Severity Corrections (8 tasks)

### TASK-007 — DEV-005: Align phase naming note in Phase 4/5 narrative

**File**: `roadmap.md`
**Section**: Phase 4 Goals block and Phase 5 Goals block
**Action**: Add a parenthetical mapping note to the Goals text:
- Phase 4: append *(spec Phase 1: steps 2–3)*
- Phase 5: append *(spec Phase 2: steps 5–8)*

**Verification**: Phase 4 and Phase 5 both reference their spec-internal phase designations; approval file names (`phase1-approval.yaml`, `phase2-approval.yaml`) align with spec phase numbering.

---

### TASK-008 — DEV-006: Qualify `TurnLedger` base-type assertion in Phase 2 action 1

**File**: `roadmap.md`
**Section**: Phase 2 > Key Actions > Executor Skeleton > Action 1
**Change**: After adding the enums per TASK-001, modify the `TurnLedger` entry to read:
> `TurnLedger` (executor-internal class; no spec-defined dataclass interface — do not assert base-type inheritance without Phase 0 confirmation)

**Verification**: The phrase "all extending pipeline base types" no longer applies unconditionally to `TurnLedger`.

---

### TASK-009 — DEV-007: Add ESCALATED path note to Phase 7

**File**: `roadmap.md`
**Section**: Phase 7 — Panel Review Convergence Loop > Key Actions > Action 6
**Current text**:
> Emit updated `portify-release-spec.md` and `panel-report.md` (FR-035)

**Corrected text**:
> Emit updated `portify-release-spec.md` and `panel-report.md` (FR-035). Note: `panel-report.md` is required on **both** CONVERGED (`status: success`) and ESCALATED (`status: partial`) terminal conditions — the return contract references it in both paths.

**Verification**: Action 6 explicitly covers both terminal conditions for `panel-report.md`.

---

### TASK-010 — DEV-008: Add SC-012 dry-run unit test to Phase 2 milestone

**File**: `roadmap.md`
**Section**: Phase 2 > Key Actions > Executor Skeleton
**Action**: Add new action item after action 4:
> 4a. Add unit test: assert dry-run execution filters steps to `PREREQUISITES`, `ANALYSIS`, `USER_REVIEW`, `SPECIFICATION` phase types only (SC-012 early validation — do not defer to Phase 9 integration test alone)

**Verification**: SC-012 validation appears in Phase 2 scope in addition to the Phase 9 integration test entry in the SC-to-phase matrix.

---

### TASK-011 — DEV-009: Add `suggested_resume_budget` formula to Phase 2 action 13

**File**: `roadmap.md`
**Section**: Phase 2 > Key Actions > Executor Skeleton > Action 13
**Current text**:
> Implement `suggested_resume_budget` calculation (NFR-011)

**Corrected text**:
> Implement `suggested_resume_budget` calculation: `remaining * 25` where `remaining` = count of steps with status `PENDING` or `INCOMPLETE` (NFR-011). This feeds directly into `resume_command()` output — do not use a static turn count.

**Verification**: Action 13 contains the formula `remaining * 25` and the status filter condition.

---

### TASK-012 — DEV-010: Add sub-step numbering note to Phase 6

**File**: `roadmap.md`
**Section**: Phase 6 — Release Spec Synthesis and Brainstorm Enrichment > Key Actions > Action 3
**Current text**:
> - 6a: working copy creation
> - 6b: populate all 13 template sections from Phase 1+2 outputs
> - 6c: 3-persona brainstorm pass...
> - 6d: incorporate actionable findings...

**Corrected text**: Change labels to spec-native `3a–3d`:
> - 3a: working copy creation (roadmap label: 6a)
> - 3b: populate all 13 template sections from Phase 1+2 outputs
> - 3c: 3-persona brainstorm pass (architect, analyzer, backend)...
> - 3d: incorporate actionable findings...
> *(Note: SKILL.md uses 3a–3d notation for these sub-steps — roadmap previously used 6a–6d)*

**Verification**: Phase 6 sub-steps use `3a–3d` labeling consistent with SKILL.md notation.

---

### TASK-013 — DEV-011: Add explicit `--file` argument action to Phase 6

**File**: `roadmap.md`
**Section**: Phase 6 > Key Actions > Action 7
**Current text**:
> Handle templates >50KB via file argument passing (R-011); confirm mechanism from Phase 0 OQ-008

**Corrected text**:
> Implement `--file` argument passing for templates exceeding 50KB in `build_release_spec_prompt()`: if `len(template_content) > 50_000`, write template to a temp file and pass via `--file <path>` to the Claude subprocess (R-011). Confirm exact subprocess API from Phase 0 OQ-008 resolution.

**Verification**: Action 7 specifies implementation location (`build_release_spec_prompt()`) and mechanism (`--file` arg with size threshold).

---

### TASK-014 — DEV-012: Add `PASS_NO_REPORT` retry clarification to Phase 3

**File**: `roadmap.md`
**Section**: Phase 3 — Gate System and Semantic Validation Layer > Key Actions
**Action**: Add a new note after action 3 (gate diagnostics formatting):
> Note on retry semantics: `PASS_NO_SIGNAL` (result file present, no `EXIT_RECOMMENDATION` marker) **does** trigger retry. `PASS_NO_REPORT` (artifact produced, no result file) does **not** trigger retry — it is treated as a passing outcome. Ensure gate retry logic distinguishes these two statuses.

**Verification**: Phase 3 key actions contain an explicit note distinguishing retry behavior for `PASS_NO_SIGNAL` vs `PASS_NO_REPORT`.

---

## Phase 3 — LOW Severity Corrections (3 tasks)

### TASK-015 — DEV-013: Complete Phase 3 per-gate check mapping table

**File**: `roadmap.md`
**Section**: Phase 3 > Key Actions > Per-Gate Check Mapping table

**Note from verification**: G-003 and G-009 ARE present in the roadmap table, but with wrong/incomplete content. G-000, G-001, and G-004 are genuinely absent. Applying this task requires three distinct operations:

**Operation A — Add missing rows** (G-000, G-001, G-004 are absent, insert before existing G-002 row):
```
| G-000 | `has_valid_yaml_config` (config YAML valid with required fields: workflow_path, cli_name, output_dir) |
| G-001 | `has_component_inventory` (inventory lists at least one component with SKILL.md) |
```
Insert G-004 row after G-003:
```
| G-004 | `has_approval_status` (approval status field present: approved/rejected/pending) |
```

**Operation B — Update existing G-003 row** (currently only lists `EXIT_RECOMMENDATION`, missing `has_required_analysis_sections`):
Current: `| G-003 | EXIT_RECOMMENDATION marker present |`
Replace with: `| G-003 | EXIT_RECOMMENDATION marker present; has_required_analysis_sections (Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow, Classifications, Recommendations) |`

**Operation C — Replace existing G-009 row content** (currently lists `EXIT_RECOMMENDATION marker present` — spec's GATE_G009 has `has_approval_status`, not exit_recommendation):
Current: `| G-009 | EXIT_RECOMMENDATION marker present |`
Replace with: `| G-009 | has_approval_status (approval status field present: approved/rejected/pending) |`

**Spec references**: G-000 → spec line 567, G-001 → spec line 576, G-003 → spec lines 595–596, G-004 → spec line 605, G-009 → spec lines 654.

**Verification**: Per-gate table has all 12 rows (G-000 through G-011) with content matching spec gate definitions. No duplicate rows. G-009 no longer incorrectly lists `EXIT_RECOMMENDATION`.

---

### TASK-016 — DEV-014: Change Phase 7 sub-step labels to `4a–4d`

**File**: `roadmap.md`
**Section**: Phase 7 > Key Actions > Action 2 sub-bullets
**Current text**:
> - 7a: 4-expert focus pass...
> - 7b: finding incorporation...
> - 7c: full panel critique...
> - 7d: convergence scoring...

**Corrected text**:
> - 4a: 4-expert focus pass (Fowler, Nygard, Whittaker, Crispin) (FR-031)
> - 4b: finding incorporation with severity routing: CRITICAL → mandatory, MAJOR → incorporated, MINOR → Section 11 (FR-031)
> - 4c: full panel critique with quality scoring across clarity, completeness, testability, consistency dimensions (FR-031)
> - 4d: convergence scoring (FR-031)
> *(Note: SKILL.md uses 4a–4d notation for panel review sub-steps)*

**Verification**: Phase 7 action 2 sub-steps use `4a–4d` labeling.

---

### TASK-017 — DEV-015: Add D-005 gap note to dependency table

**File**: `roadmap.md`
**Section**: Resource Requirements > Technical Dependencies table
**Action**: Add a row between D-004 and D-006:

```
| D-005 | *(reserved/not used — intentionally omitted from dependency table)* | — | — | — |
```

**Verification**: Dependency table contains a D-005 row explaining the gap.

---

## Execution Order

```
Sequential within tiers; tiers can proceed as each prior tier completes.

Tier 1 (HIGH — blocking for implementation):
  TASK-001 (DEV-001+002) → TASK-003 (DEV-003a) → TASK-004 (DEV-003b) → TASK-005 (DEV-003c fix) → TASK-006 (DEV-004)

Tier 2 (MEDIUM — correctness improvements):
  TASK-007 through TASK-014 (can be applied in any order within the tier)

Tier 3 (LOW — cosmetic/completeness):
  TASK-015 through TASK-017 (can be applied in any order within the tier)
```

## Validation Checklist

After all edits are applied, verify:

- [ ] `PortifyPhaseType` and `ConvergenceState` appear in Phase 2 action item 1
- [ ] `failures.py` does not appear in any deliverables section
- [ ] `resume.py` and `contract.py` do not appear in any deliverables section
- [ ] `executor.py` deliverable has a note about absorbing resume and contract logic
- [ ] Phase 3 per-gate table has all 12 rows
- [ ] G-010 has `has_brainstorm_section` check
- [ ] G-011 row exists with `has_quality_scores` and `has_criticals_addressed`
- [ ] Phase 7 Action 6 references both CONVERGED and ESCALATED for `panel-report.md`
- [ ] Phase 2 has SC-012 dry-run unit test action
- [ ] Phase 2 Action 13 contains formula `remaining * 25`
- [ ] Phase 6 sub-steps use `3a–3d` labels
- [ ] Phase 6 Action 7 has `build_release_spec_prompt()` and `--file` mechanism
- [ ] Phase 3 has retry distinction note for `PASS_NO_REPORT` vs `PASS_NO_SIGNAL`
- [ ] Phase 7 sub-steps use `4a–4d` labels
- [ ] Dependency table has D-005 row
- [ ] `spec-fidelity.md` DEV-003 correctly states `failures.py` is in Phase 1
