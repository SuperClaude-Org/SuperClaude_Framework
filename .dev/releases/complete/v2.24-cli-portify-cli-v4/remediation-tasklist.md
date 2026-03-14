---
source: roadmap-remediation.md
deviations: DEV-002, DEV-003, DEV-004, DEV-008 (HIGH x2, MEDIUM x2)
gate_target: spec-fidelity high_severity_count == 0
---

# Remediation Tasklist — v2.24-cli-portify-cli-v4

## Phase R1: Apply Roadmap Patches

### TASK-R1.1 — Patch Domain Models section (DEV-002, DEV-004)
**File**: `roadmap.md`
**Location**: `#### Domain Models (`models.py`)` in Phase 1
**Action**: Replace the existing 3-bullet block with the 6-model reference block from `roadmap-remediation.md` § Patch 1
**Acceptance**: All 6 model names present (`PortifyConfig`, `PortifyStatus`, `PortifyOutcome`, `PortifyStepResult`, `PortifyResult`, `PortifyMonitorState`); `ComponentInventory` absent from model list; Section 4.5 explicitly referenced; gate function signature bullet retained at bottom
**Resolves**: DEV-002 (HIGH), DEV-004 (MEDIUM)
**Risk**: Verify `resumable` field — may be inherited from base `StepResult`, not re-declared

---

### TASK-R1.2 — Add Gate Contract sub-section (DEV-003, DEV-008)
**File**: `roadmap.md`
**Location**: Immediately after the 4 existing bullets in `#### Gate Infrastructure (`gates.py` expansion)` in Phase 2
**Action**: Append the `#### Gate Contract (spec Sections 5.2.1 and 5.2.2)` sub-section from `roadmap-remediation.md` § Patch 2 — do not replace the existing bullets
**Acceptance**: Semantic check table present with all 8 functions named; `_all_gates_defined` note present flagging its unassigned status; GateCriteria table present with all 7 objects and their tier/frontmatter/check compositions
**Resolves**: DEV-003 (HIGH), DEV-008 (MEDIUM)
**Risk**: `_all_gates_defined()` has no gate assignment in spec — note must not invent one; naming inconsistency on `_has_section_12` (underscore vs none) to be verified against `SemanticCheck` constructor

---

## Phase R2: Validate Gate Will Pass

### TASK-R2.1 — Verify roadmap.md patch correctness
**Action**: Read the patched `roadmap.md` and confirm:
- [ ] Phase 1 Domain Models: 6 model names present, `ComponentInventory` absent from model list, Section 4.5 cited
- [ ] Phase 2 Gate Infrastructure: existing 4 bullets untouched; new `#### Gate Contract` sub-section appended
- [ ] Semantic check table: 8 rows, all function names correct, `_all_gates_defined` note present
- [ ] GateCriteria table: 7 rows, tiers correct (`VALIDATE_CONFIG_GATE`=EXEMPT, 3 STRICT, 2 STANDARD)
- [ ] No introduced formatting errors (headings, YAML frontmatter, code fences)

---

### TASK-R2.2 — Resume roadmap pipeline
**Command**:
```bash
superclaude roadmap run /config/workspace/IronClaude/.dev/releases/current/v2.24-cli-portify-cli-v4/portify-release-spec.md --resume --output .dev/releases/current/v2.24-cli-portify-cli-v4
```
**Expected**: `spec-fidelity` step re-evaluates; `high_severity_count` drops to 0; gate passes; pipeline proceeds to `extract` → `remediate` → `certify`
**On failure**: Re-read `spec-fidelity.md` to identify any remaining HIGH-severity deviations; do not re-run without diagnosis

---

## Phase R3: Post-Gate Open Items (After Pipeline Passes)

These are the remaining MEDIUM deviations that do not block the gate but should be tracked. Address after the pipeline completes successfully.

### TASK-R3.1 — Resolve DEV-005: `to_contract()` placement
**Severity**: MEDIUM
**Decision required**: Keep `contract.py` as separate module (roadmap choice) or revert to method on `PortifyResult` (spec choice)
- If keeping `contract.py`: add an entry to `dev-001-accepted-deviation.md` (Agent 1's file) documenting this as an additional accepted architectural deviation with rationale
- If reverting: remove `contract.py` from roadmap module list and re-attribute `to_contract()` to `PortifyResult` in Phase 1

---

### TASK-R3.2 — Fix DEV-011: `--output-dir` vs `--output` CLI flag name
**Severity**: MEDIUM (low effort)
**File**: `roadmap.md`
**Location**: Phase 1 `#### Click CLI Integration (`cli.py`)` — the option list
**Action**: Change `--output-dir` to `--output` to match spec Section 5.1 CLI surface
**Acceptance**: Roadmap CLI section matches spec flag name exactly

---

### TASK-R3.3 — Add Appendix C reference for prompt builders (DEV-020)
**Severity**: MEDIUM (low effort)
**File**: `roadmap.md`
**Location**: Phase 2 `#### Prompt Builders (`prompts.py`)` section
**Action**: Add a note: "Implement prompt builder functions per Appendix C, which provides full Python implementations for `build_analyze_prompt`, `build_pipeline_prompt`, `build_synthesize_prompt`, `build_brainstorm_prompt`, `build_panel_prompt`. Follow the `@path` reference patterns, output format markers, and machine-readable markers defined there exactly."
**Resolves**: DEV-020 (MEDIUM)

---

### TASK-R3.4 — Add named test list for DEV-013
**Severity**: MEDIUM
**File**: `roadmap.md`
**Location**: Phase 6 `#### Unit Test Suite (17 tests per SC-013)`
**Action**: Replace the category bullets with the 17 named tests from spec Section 8.1, maintaining category grouping as sub-headers
**Acceptance**: All 17 test function names explicitly listed (e.g., `test_validate_config_valid`, `test_convergence_converges`, `test_convergence_escalates`, `test_convergence_budget_guard`, etc.)

---

### TASK-R3.5 — Document DEV-006, DEV-007, DEV-009, DEV-010, DEV-014 as accepted
**Severity**: MEDIUM (documentation only)
**File**: `dev-001-accepted-deviation.md` (Agent 1's acceptance record)
**Action**: Add entries for each debate-resolved or debate-silent deviation:
- DEV-006: `convergence.py` — accepted per D-11
- DEV-007: `resume.py` — accepted per D-12
- DEV-009/DEV-010: `monitor.py` merge — accepted as architecturally coherent (debate-silent)
- DEV-014: Section hashing mechanism — accepted per D-14 (spec should be updated to include it)
**Acceptance**: Each deviation has a formal disposition entry with rationale; spec update requirements noted

---

### TASK-R3.6 — Annotate DEV-019 (1MB cap) in roadmap
**Severity**: LOW
**File**: `roadmap.md`
**Location**: Phase 1 `#### Component Discovery` — the 1MB cap bullet
**Action**: Append a parenthetical: "(enhancement beyond spec FR-002; included as defensive measure for pathological file sizes — note that the spec requires accurate line counts, so log a warning for any skipped files)"

---

## Execution Order

```
R1.1 → R1.2 → R2.1 → R2.2
                        ↓ (gate passes)
              R3.1 → R3.2 → R3.3 → R3.4 → R3.5 → R3.6
```

R1.1 and R1.2 can be applied in parallel (different sections of `roadmap.md`).
R2.1 must follow both R1 tasks.
R2.2 must follow R2.1.
R3 tasks are independent of each other and can be done in any order after R2.2 passes.

## Success Criteria

- `high_severity_count: 0` in regenerated `spec-fidelity.md`
- `tasklist_ready: true` in regenerated `spec-fidelity.md`
- Pipeline proceeds past `spec-fidelity` gate on next `--resume`
- All TASK-R3 items either resolved or formally accepted before implementation begins
