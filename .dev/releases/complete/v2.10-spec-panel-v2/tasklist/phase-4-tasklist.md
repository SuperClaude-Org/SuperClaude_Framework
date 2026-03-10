# Phase 4 -- Depth and Breadth

Phase 4 delivers two parallel workstreams: M5 builds the `--focus correctness` mode that reconfigures the panel for correctness-intensive review, and M6 adds pipeline dimensional analysis for catching data count mismatches. Both depend on Gate A (Phase 3) but not on each other. Tasks are ordered M5-first then M6 by roadmap appearance; within-phase dependencies are explicit.

---

### T04.01 -- Add --focus correctness Flag and 5-Expert Panel Configuration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020, R-021 |
| Why | FR-12 adds a fifth focus area; FR-13 defines the specialized 5-expert panel (Nygard lead, Fowler, Adzic, Crispin, Whittaker) that activates under correctness focus. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0019, D-0020 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0019/spec.md`
- `TASKLIST_ROOT/artifacts/D-0020/spec.md`

**Deliverables:**
1. `--focus correctness` flag definition added to Focus Areas section of `spec-panel.md` per FR-12, targeting execution correctness of stateful specifications
2. 5-expert panel configuration: Nygard (lead), Fowler, Adzic, Crispin, Whittaker activated when `--focus correctness` is specified per FR-13

**Steps:**
1. **[PLANNING]** Locate the Focus Areas section and Usage line in spec-panel.md
2. **[PLANNING]** Review FR-12 and FR-13 for correctness focus area requirements
3. **[EXECUTION]** Add "### Correctness Focus (`--focus correctness`)" subsection to Focus Areas with Expert Panel, Analysis Areas, Mandatory Outputs, and Auto-Suggestion fields
4. **[EXECUTION]** Update the Usage line to include `correctness` in focus options: `--focus requirements|architecture|testing|compliance|correctness`
5. **[VERIFICATION]** Verify exactly 5 experts listed with correct lead assignment (Nygard); Usage line updated
6. **[COMPLETION]** Record flag definition and panel configuration in evidence artifacts

**Acceptance Criteria:**
- File `spec-panel.md` Focus Areas section contains "### Correctness Focus" subsection with `--focus correctness` flag
- Expert Panel field lists exactly 5 experts: Nygard (lead), Fowler, Adzic, Crispin, Whittaker
- Usage line includes `correctness` option alongside existing focus areas
- Traceable to R-020 and R-021 via D-0019 and D-0020

**Validation:**
- Manual check: Correctness Focus subsection present in Focus Areas with 5-expert panel and updated Usage line in spec-panel.md
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0019/spec.md` and `TASKLIST_ROOT/artifacts/D-0020/spec.md`

**Dependencies:** T03.02 (Gate A go decision authorizes Phase 4)
**Rollback:** Remove Correctness Focus subsection from Focus Areas; revert Usage line

---

### T04.02 -- Implement Modified Expert Behaviors and State Variable Registry

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022, R-023 |
| Why | FR-14.1 through FR-14.6 define how each expert shifts methodology under correctness focus; FR-15.1 defines the State Variable Registry as a mandatory output. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-file scope (6 expert behavior modifications), system-wide behavioral change |
| Tier | STRICT |
| Confidence | `[█████████░] 90%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0021, D-0022 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0021/spec.md`
- `TASKLIST_ROOT/artifacts/D-0022/spec.md`

**Deliverables:**
1. Modified expert behaviors FR-14.1 through FR-14.6 documented in correctness focus section: Wiegers (implicit state assumptions), Fowler (data flow annotation with count divergence), Nygard (guard boundary analysis including zero/empty), Adzic (state-annotated scenarios with degenerate inputs), Crispin (boundary value tests), Whittaker (five attack methodologies on each invariant)
2. State Variable Registry output template per FR-15.1: table listing every mutable variable with type, initial value, invariant, and read/write operations

**Steps:**
1. **[PLANNING]** Review FR-14.1 through FR-14.6 behavior specifications from the spec
2. **[PLANNING]** Review FR-15.1 State Variable Registry requirements
3. **[EXECUTION]** Document each expert's correctness-focus behavior shift in the Correctness Focus subsection of spec-panel.md
4. **[EXECUTION]** Add State Variable Registry template to Mandatory Outputs field: columns for variable name, type, initial value, invariant, read operations, write operations
5. **[VERIFICATION]** Verify all 6 expert behaviors (FR-14.1 through FR-14.6) are documented; State Variable Registry template has all required columns
6. **[COMPLETION]** Record behavior specifications and registry template in evidence artifacts

**Acceptance Criteria:**
- Correctness Focus subsection in `spec-panel.md` documents behavior shifts for all 6 experts (Wiegers, Fowler, Nygard, Adzic, Crispin, Whittaker) per FR-14.1-FR-14.6
- State Variable Registry template in Mandatory Outputs catalogs: variable name, type, initial value, invariant, read/write operations per FR-15.1
- Behavior descriptions are additive shifts (not replacements of existing behaviors)
- Traceable to R-022 and R-023 via D-0021 and D-0022

**Validation:**
- Manual check: All 6 FR-14 behavior shifts documented; State Variable Registry template present with all required columns
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0021/spec.md` and `TASKLIST_ROOT/artifacts/D-0022/spec.md`

**Dependencies:** T04.01 (correctness focus section must exist)
**Rollback:** Remove FR-14 behavior descriptions and State Variable Registry template from correctness focus section

---

### T04.03 -- Add Mandatory Artifacts Under Correctness Focus

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024, R-025 |
| Why | FR-15.2 makes the boundary table always produced (not just triggered) under correctness focus; FR-15.3 adds Pipeline Flow Diagram annotated with counts. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023, D-0024 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0023/spec.md`
- `TASKLIST_ROOT/artifacts/D-0024/spec.md`

**Deliverables:**
1. Guard Condition Boundary Table specified as always-produced (not trigger-gated) when `--focus correctness` is active per FR-15.2
2. Pipeline Flow Diagram output specification: annotated with counts at each stage when pipelines are present per FR-15.3

**Steps:**
1. **[PLANNING]** Review FR-15.2 and FR-15.3 mandatory output requirements
2. **[PLANNING]** Identify where mandatory outputs are documented in correctness focus section
3. **[EXECUTION]** Update Mandatory Outputs in correctness focus section: boundary table is always produced (override trigger-gating from Phase 2 when correctness flag is active)
4. **[EXECUTION]** Add Pipeline Flow Diagram specification: annotated with counts at each pipeline stage, produced when pipelines are present
5. **[VERIFICATION]** Verify boundary table override is correctly scoped to `--focus correctness` only; Pipeline Flow Diagram specification is concrete
6. **[COMPLETION]** Record mandatory artifact specifications in evidence artifacts

**Acceptance Criteria:**
- Correctness Focus Mandatory Outputs in `spec-panel.md` lists Guard Condition Boundary Table as always-produced (not trigger-gated) under `--focus correctness`
- Pipeline Flow Diagram specification describes: annotated with counts at each stage, produced when pipelines present
- Standard (non-correctness) panel behavior unchanged: boundary table still trigger-gated per Phase 2 logic
- Traceable to R-024 and R-025 via D-0023 and D-0024

**Validation:**
- Manual check: Mandatory Outputs in correctness focus section lists boundary table (always) and Pipeline Flow Diagram (when pipelines present)
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0023/spec.md` and `TASKLIST_ROOT/artifacts/D-0024/spec.md`

**Dependencies:** T04.01 (correctness focus section exists), T02.02 (boundary table template from Phase 2)
**Rollback:** Remove mandatory artifact overrides from correctness focus section

---

### T04.04 -- Implement Auto-Suggestion Heuristic FR-16

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | FR-16 auto-suggests `--focus correctness` when specs have 3+ mutable state variables, numeric threshold guards, or pipeline/filter operations; false positive rate must be <30%. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | detection accuracy, false positive risk |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0025/spec.md`
- `TASKLIST_ROOT/artifacts/D-0025/notes.md`

**Deliverables:**
1. Auto-suggestion heuristic FR-16 in `spec-panel.md`: triggers recommendation (not forced activation) when specification introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations; target false positive rate <30%

**Steps:**
1. **[PLANNING]** Review FR-16 trigger conditions and NFR-8 false positive rate target from the spec
2. **[PLANNING]** Review AC-10 (should suggest) and AC-11 (should not suggest) scenarios
3. **[EXECUTION]** Add Auto-Suggestion section to correctness focus documentation: "Panel recommends --focus correctness when spec introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations"
4. **[EXECUTION]** Specify that suggestion is advisory-only (recommendation in output, not forced activation per FR-16)
5. **[VERIFICATION]** Verify trigger conditions match FR-16 exactly; confirm suggestion is advisory-only; verify AC-10 would trigger and AC-11 would not
6. **[COMPLETION]** Record heuristic specification in evidence artifact

**Acceptance Criteria:**
- Auto-Suggestion section in `spec-panel.md` correctness focus documentation specifies three trigger conditions: 3+ mutable state vars, numeric threshold guards, pipeline/filter operations
- Suggestion is advisory-only (recommendation in output, not forced activation)
- False positive rate target (<30%) is documented per NFR-8; measurement deferred to Gate B (M7/T05.02)
- Traceable to R-026 via D-0025

**Validation:**
- Manual check: Auto-Suggestion section specifies all three FR-16 trigger conditions as advisory recommendations
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0025/spec.md`

**Dependencies:** T04.01 (correctness focus section exists)
**Rollback:** Remove Auto-Suggestion section from correctness focus documentation

---

### T04.05 -- Define Pipeline Dimensional Analysis Heuristic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027, R-028, R-029, R-030, R-031 |
| Why | SP-4 adds a heuristic detecting multi-stage pipelines with count mismatches: trigger detection, 4-step analysis, CRITICAL severity, Quantity Flow Diagram, and 5 downstream integration points. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | detection logic scope, multi-component integration |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0026, D-0027, D-0028, D-0029, D-0030 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0026/spec.md`
- `TASKLIST_ROOT/artifacts/D-0027/spec.md`
- `TASKLIST_ROOT/artifacts/D-0028/spec.md`
- `TASKLIST_ROOT/artifacts/D-0029/spec.md`
- `TASKLIST_ROOT/artifacts/D-0030/spec.md`

**Deliverables:**
1. Pipeline detection trigger in `spec-panel.md`: activates on specs with 2+ stage data flow where output count may differ from input count; does not trigger on CRUD-only specs (FR-17)
2. 4-step analysis process: Pipeline Detection (Fowler leads), Quantity Annotation (N in/M out), Downstream Tracing (verify count usage), Consistency Check (flag mismatches) per FR-18
3. CRITICAL severity classification for any dimensional mismatch per FR-19
4. Quantity Flow Diagram output artifact template: shows counts at each pipeline stage, annotates which count each downstream consumer uses per FR-21
5. Downstream integration wiring: SP-4 Quantity Flow to sc:roadmap RM-3, SP-2 Attack Findings to sc:roadmap RM-2, SP-1 Correctness to sc:adversarial AD-5, SP-2 Assumptions to sc:adversarial AD-2

**Steps:**
1. **[PLANNING]** Review FR-17 through FR-21 pipeline analysis requirements from the spec
2. **[PLANNING]** Identify insertion point in spec-panel.md for Review Heuristics section (after Mandatory Output Artifacts)
3. **[EXECUTION]** Add "## Review Heuristics" section with "### Pipeline Dimensional Analysis" subsection containing trigger condition, responsibility assignments (Fowler identification/annotation, Whittaker divergence attack), 4-step process, CRITICAL severity rule
4. **[EXECUTION]** Add Quantity Flow Diagram output specification with count annotations per pipeline stage
5. **[EXECUTION]** Document all 5 downstream integration points: SP-3→AD-1, SP-2→AD-2, SP-1→AD-5, SP-4→RM-3, SP-2→RM-2
6. **[VERIFICATION]** Verify all 5 deliverables are present; trigger condition matches FR-17; severity matches FR-19; all integration points documented
7. **[COMPLETION]** Record all specifications in evidence artifacts

**Acceptance Criteria:**
- File `spec-panel.md` contains Review Heuristics section with Pipeline Dimensional Analysis subsection
- Trigger fires on 2+ stage data flow with possible count divergence; does not fire on CRUD-only specs
- 4-step process (Detection, Annotation, Tracing, Check) is documented with expert assignments (Fowler leads, Whittaker attacks)
- Dimensional mismatches classified as CRITICAL severity with concrete scenario requirement
- All 5 integration points (SP-3→AD-1, SP-2→AD-2, SP-1→AD-5, SP-4→RM-3, SP-2→RM-2) documented

**Validation:**
- Manual check: Review Heuristics section contains trigger, 4-step process, CRITICAL severity rule, Quantity Flow Diagram spec, and all 5 integration points
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0026/` through `TASKLIST_ROOT/artifacts/D-0030/`

**Dependencies:** T03.02 (Gate A go decision), T02.07 (downstream format from Phase 2 for AD-1 wiring)
**Rollback:** Remove Review Heuristics section from spec-panel.md
**Notes:** No dependency on T04.01-T04.04 (M5 tasks); M5 and M6 execute in parallel per roadmap.

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Verify correctness focus mode and pipeline analysis are structurally complete before overhead measurement.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-T01-T05.md`

**Verification:**
- Correctness focus section exists with 5-expert panel, FR-14 behaviors, mandatory outputs, and auto-suggestion heuristic
- Pipeline Dimensional Analysis section exists with trigger, 4-step process, severity rule, and diagram spec
- All 5 downstream integration points are documented

**Exit Criteria:**
- Deliverables D-0019 through D-0030 have evidence artifacts at intended paths
- No existing spec-panel.md sections are displaced or broken
- Both M5 and M6 deliverables are structurally complete

---

### T04.06 -- Validate Token Overhead for Pipeline Analysis

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | NFR-9 requires <5% overhead when no pipelines detected; NFR-10 requires <=10% when pipelines detected. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (token overhead measurement) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0031/evidence.md`

**Deliverables:**
1. Token overhead validation report: pipeline analysis adds <5% overhead when no pipelines detected (NFR-9) and <=10% when pipelines detected (NFR-10), measured against Phase 2 baseline

**Steps:**
1. **[PLANNING]** Retrieve Phase 2 baseline token count from D-0014
2. **[PLANNING]** Select two test specifications: one with pipelines, one CRUD-only (no pipelines)
3. **[EXECUTION]** Run panel with pipeline analysis active on CRUD-only spec; measure overhead against baseline
4. **[EXECUTION]** Run panel with pipeline analysis active on pipeline-containing spec; measure overhead against baseline
5. **[VERIFICATION]** Verify CRUD-only overhead <5% (NFR-9) and pipeline-containing overhead <=10% (NFR-10)
6. **[COMPLETION]** Record overhead measurements in evidence artifact

**Acceptance Criteria:**
- Measurement report at `TASKLIST_ROOT/artifacts/D-0031/evidence.md` documents overhead for both pipeline and non-pipeline specs
- Non-pipeline overhead is <5% per NFR-9
- Pipeline overhead is <=10% per NFR-10
- Traceable to R-032 via D-0031

**Validation:**
- Manual check: Overhead report contains baseline, pipeline, and non-pipeline measurements with percentage calculations
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0031/evidence.md`

**Dependencies:** T04.05 (pipeline analysis defined), T02.06 (Phase 2 baseline)
**Rollback:** N/A (measurement task; no specification changes)

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm Phase 4 (Depth and Breadth) is complete: correctness focus mode and pipeline analysis are fully specified, overhead validated.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`

**Verification:**
- All 6 tasks (T04.01 through T04.06) completed with evidence artifacts
- Correctness focus mode has: flag, 5-expert panel, FR-14 behaviors, mandatory outputs, auto-suggestion
- Pipeline analysis has: trigger, 4-step process, CRITICAL severity, Quantity Flow Diagram, integration wiring
- Overhead measurements within NFR-9 and NFR-10 budgets

**Exit Criteria:**
- All deliverables D-0019 through D-0031 have evidence artifacts
- Both M5 and M6 workstreams are complete
- Phase 5 (Gate B) dependency (M5+M6 complete) is satisfied
