# Phase 2 -- Structural Forcing Functions

Phase 2 introduces the guard condition boundary table -- a mandatory, structured artifact that forces the panel to enumerate guard conditions, identify gaps, and block synthesis until the table is complete. This phase builds on Phase 1's adversarial persona to validate boundary table entries.

---

### T02.01 -- Add Mandatory Output Artifacts Section to spec-panel.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | The Mandatory Output Artifacts section is the structural container for the boundary table and future mandatory artifacts; it must exist before table content is added. |
| Effort | S |
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
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/spec.md`

**Deliverables:**
1. "Mandatory Output Artifacts" section added to `spec-panel.md` after the Output Formats section, with subsection placeholder for Guard Condition Boundary Table

**Steps:**
1. **[PLANNING]** Locate the Output Formats section in spec-panel.md to determine insertion point
2. **[PLANNING]** Verify no existing Mandatory Output Artifacts section exists
3. **[EXECUTION]** Add "## Mandatory Output Artifacts" section after Output Formats with introductory text explaining when mandatory artifacts are triggered
4. **[EXECUTION]** Add "### Guard Condition Boundary Table" subsection heading as placeholder for T02.02 content
5. **[VERIFICATION]** Verify section heading hierarchy is consistent with surrounding sections; no existing content displaced
6. **[COMPLETION]** Record section addition in evidence artifact

**Acceptance Criteria:**
- File `spec-panel.md` contains "## Mandatory Output Artifacts" section positioned after Output Formats
- Section documents when mandatory artifacts are triggered (conditional logic, threshold checks, guards, sentinel comparisons)
- No existing sections are displaced or modified
- Traceable to R-009 via D-0009

**Validation:**
- Manual check: Mandatory Output Artifacts section present in spec-panel.md at correct position with Guard Condition Boundary Table subsection
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0009/spec.md`

**Dependencies:** T01.04 (Phase 1 integration complete; panel structure stable)
**Rollback:** Remove Mandatory Output Artifacts section from spec-panel.md

---

### T02.02 -- Define 7-Column Boundary Table Template

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The boundary table template forces explicit enumeration of boundary behaviors; FR-7 requires 7 columns with minimum 6 input condition rows per guard. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema definition scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0010/spec.md`

**Deliverables:**
1. 7-column table template in spec-panel.md Guard Condition Boundary Table subsection: Guard, Location, Input Condition, Variable Value, Guard Result, Specified Behavior, Status (OK/GAP) with minimum 6 input condition rows per guard (zero/empty, one/minimal, typical, max/overflow, sentinel match, legitimate edge case)

**Steps:**
1. **[PLANNING]** Review FR-7 column definitions and FR-6 trigger conditions from the spec
2. **[PLANNING]** Design table markdown format that is both human-readable and machine-parseable (NFR-5)
3. **[EXECUTION]** Write 7-column table template with column headers: Guard, Location, Input Condition, Variable Value, Guard Result, Specified Behavior, Status
4. **[EXECUTION]** Add 6 mandatory input condition rows per guard as template: zero/empty, one/minimal, typical, maximum/overflow, sentinel value match, legitimate edge case
5. **[VERIFICATION]** Verify template matches FR-7 exactly; confirm all 7 columns present; confirm 6 input condition rows present
6. **[COMPLETION]** Record template in evidence artifact

**Acceptance Criteria:**
- Guard Condition Boundary Table template in `spec-panel.md` has exactly 7 columns matching FR-7 (Guard, Location, Input Condition, Variable Value, Guard Result, Specified Behavior, Status)
- Template shows minimum 6 input condition row types per guard (zero/empty, one/minimal, typical, max/overflow, sentinel match, edge case)
- Table format is structured markdown (not prose) per NFR-5 for downstream consumption
- Traceable to R-010 via D-0010

**Validation:**
- Manual check: Table template in spec-panel.md contains 7 columns and 6 row types matching FR-7 specification
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0010/spec.md`

**Dependencies:** T02.01 (Mandatory Output Artifacts section must exist)
**Rollback:** Remove table template from Guard Condition Boundary Table subsection

---

### T02.03 -- Implement GAP Severity Rules and Synthesis-Blocking Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011, R-012 |
| Why | FR-8/FR-9 require GAP and blank cells to auto-generate MAJOR findings; FR-10 requires incomplete tables to block synthesis, making boundary analysis a structural gate. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (synthesis blocking), system-wide enforcement |
| Tier | STRICT |
| Confidence | `[█████████░] 90%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/spec.md`
- `TASKLIST_ROOT/artifacts/D-0011/notes.md`

**Deliverables:**
1. Completion enforcement rules in spec-panel.md: GAP cells generate MAJOR severity findings (FR-8), blank/unspecified Specified Behavior cells generate MAJOR severity findings (FR-9), and incomplete tables block synthesis output (FR-10)

**Steps:**
1. **[PLANNING]** Review FR-8, FR-9, FR-10 completion enforcement requirements from the spec
2. **[PLANNING]** Identify the synthesis output generation point in spec-panel.md where the blocking gate must be inserted
3. **[EXECUTION]** Add completion criteria rules to boundary table section: GAP -> MAJOR finding, blank Specified Behavior -> MAJOR finding
4. **[EXECUTION]** Add synthesis-blocking gate: "Table is complete before synthesis output is generated" with explicit hard gate (not advisory)
5. **[VERIFICATION]** Verify rules are specified as hard gates, not advisory; verify blocking logic is documented at the synthesis generation point
6. **[COMPLETION]** Record enforcement rules in evidence artifact

**Acceptance Criteria:**
- File `spec-panel.md` boundary table Completion Criteria states: GAP cells generate MAJOR severity minimum (FR-8)
- Blank or "unspecified" Specified Behavior cells classified as MAJOR severity minimum (FR-9)
- Synthesis-blocking logic explicitly documented: incomplete table prevents synthesis output generation (FR-10)
- Rules are hard gates, not advisory recommendations

**Validation:**
- Manual check: Completion Criteria in spec-panel.md contain all three enforcement rules (GAP->MAJOR, blank->MAJOR, incomplete->block synthesis) as hard gates
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0011/spec.md`

**Dependencies:** T02.02 (table template must exist before adding enforcement rules)
**Rollback:** Remove completion criteria and synthesis-blocking logic from boundary table section

---

### T02.04 -- Define Expert Role Assignments for Boundary Table

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | FR-11 assigns specific experts to boundary table construction: Nygard leads, Crispin validates completeness, Whittaker attacks entries. |
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
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0012/spec.md`

**Deliverables:**
1. Expert role assignments documented in boundary table section of `spec-panel.md`: Nygard (lead construction), Crispin (completeness validation), Whittaker (adversarial attack on entries)

**Steps:**
1. **[PLANNING]** Review FR-11 role assignment requirements from the spec
2. **[PLANNING]** Confirm Nygard, Crispin, and Whittaker personas exist in spec-panel.md
3. **[EXECUTION]** Add Responsibility line to boundary table section: "Nygard (lead construction), Crispin (completeness validation), Whittaker (adversarial attack on entries)"
4. **[EXECUTION]** Document that all three experts participate when the boundary table is triggered
5. **[VERIFICATION]** Verify role assignments match FR-11 exactly; no role conflicts with existing expert responsibilities
6. **[COMPLETION]** Record role assignments in evidence artifact

**Acceptance Criteria:**
- Boundary table section in `spec-panel.md` contains Responsibility line with Nygard (lead), Crispin (validate), Whittaker (attack)
- All three experts participate when boundary table is triggered
- Role assignments do not conflict with existing expert role definitions
- Traceable to R-013 via D-0012

**Validation:**
- Manual check: Responsibility line in boundary table section lists all three experts with correct roles per FR-11
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0012/spec.md`

**Dependencies:** T02.01 (section exists), T01.01 (Whittaker persona exists)
**Rollback:** Remove Responsibility line from boundary table section

---

### T02.05 -- Implement Table Trigger Detection Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | The boundary table must trigger automatically on specs with conditional logic, threshold checks, boolean guards, or sentinel comparisons (FR-6). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | detection logic scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0013/spec.md`

**Deliverables:**
1. Table trigger detection logic in `spec-panel.md` that activates boundary table on specifications containing conditional logic, threshold checks, boolean guards, or sentinel value comparisons, and produces "No guard conditions identified" when no triggers match (AC-7)

**Steps:**
1. **[PLANNING]** Review FR-6 trigger conditions and AC-7 no-trigger behavior from the spec
2. **[PLANNING]** Identify where trigger logic should be documented in the boundary table section
3. **[EXECUTION]** Write trigger condition: "Any specification containing conditional logic, threshold checks, boolean guards, or sentinel value comparisons"
4. **[EXECUTION]** Add no-trigger behavior: when no conditions match, section states "No guard conditions identified" and does not block synthesis (AC-7)
5. **[VERIFICATION]** Verify trigger covers all four condition types (conditional logic, thresholds, boolean guards, sentinels) and no-trigger path does not block synthesis
6. **[COMPLETION]** Record trigger logic in evidence artifact

**Acceptance Criteria:**
- Trigger section in `spec-panel.md` boundary table specifies activation on: conditional logic, threshold checks, boolean guards, sentinel value comparisons
- No-trigger path produces "No guard conditions identified" and does not block synthesis (AC-7)
- Trigger is broad enough to catch guard conditions but does not fire on specs with no conditional logic
- Traceable to R-014 via D-0013

**Validation:**
- Manual check: Trigger line in boundary table section lists all four condition types; no-trigger behavior documented
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0013/spec.md`

**Dependencies:** T02.02 (table template exists), T02.03 (enforcement rules exist for trigger to gate)
**Rollback:** Remove trigger detection logic from boundary table section

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.05

**Purpose:** Verify boundary table structure, enforcement rules, and trigger logic are complete before overhead measurement and downstream format work.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T01-T05.md`

**Verification:**
- Mandatory Output Artifacts section exists in spec-panel.md with boundary table subsection
- 7-column table template, GAP/blank severity rules, synthesis-blocking logic, role assignments, and trigger detection are all present
- All rules are documented as hard gates (not advisory)

**Exit Criteria:**
- Deliverables D-0009 through D-0013 have evidence artifacts at their intended paths
- Boundary table section is structurally complete (template + enforcement + roles + trigger)
- No existing spec-panel.md sections are displaced or broken

---

### T02.06 -- Measure NFR-4 Token Overhead for SP-3 Boundary Table

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | NFR-4 requires boundary table overhead <=10% above Phase 1 baseline; measurement must complete before M3 closes. |
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
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Deliverables:**
1. NFR-4 overhead measurement: SP-3 boundary table token cost measured on v0.04, compared against Phase 1 baseline, must be <=10% above Phase 1 baseline

**Steps:**
1. **[PLANNING]** Retrieve Phase 1 baseline token count from T01.05 measurement (D-0007)
2. **[PLANNING]** Identify v0.04 specification for boundary table measurement
3. **[EXECUTION]** Run panel with boundary table active on v0.04 specification and record token count
4. **[EXECUTION]** Calculate overhead: (with_boundary_table - phase1_baseline) / phase1_baseline * 100
5. **[VERIFICATION]** Verify overhead is <=10% above Phase 1 baseline per NFR-4; document result
6. **[COMPLETION]** Record measurement in evidence artifact

**Acceptance Criteria:**
- Measurement report at `TASKLIST_ROOT/artifacts/D-0014/evidence.md` documents Phase 1 baseline, Phase 2 token count, and overhead percentage
- Calculation methodology is explicit and reproducible
- Result compared against NFR-4 threshold (<=10% above Phase 1 baseline)
- Traceable to R-015 via D-0014

**Validation:**
- Manual check: Overhead measurement report contains Phase 1 baseline, Phase 2 count, and percentage calculation
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Dependencies:** T01.05 (Phase 1 baseline), T02.05 (trigger logic complete)
**Rollback:** N/A (measurement task; no specification changes)

---

### T02.07 -- Define Downstream Propagation Format for sc:adversarial AD-1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | SP-3's boundary table output must be machine-parseable for consumption by sc:adversarial AD-1 (invariant probe round); format compatibility is a release requirement. |
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
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Deliverables:**
1. Downstream Propagation section in boundary table documentation specifying machine-parseable markdown format for AD-1 consumer, with format documented for invariant probe input

**Steps:**
1. **[PLANNING]** Review integration contract: SP-3 boundary table feeds AD-1 invariant probe round
2. **[PLANNING]** Identify format requirements: machine-parseable structured markdown (NFR-5)
3. **[EXECUTION]** Add Downstream Propagation section to boundary table documentation specifying: format (structured markdown table), consumer (sc:adversarial AD-1), and GAP entries as priority targets
4. **[EXECUTION]** Document that SC-4→RM-3 and SP-2→RM-2 wiring is deferred to M6 (T04.05)
5. **[VERIFICATION]** Verify format specification is concrete enough for AD-1 to parse programmatically
6. **[COMPLETION]** Record format specification in evidence artifact

**Acceptance Criteria:**
- Downstream Propagation section in `spec-panel.md` boundary table specifies machine-parseable markdown format
- Format documentation names AD-1 as consumer and describes how GAP entries become priority targets
- Format is structured (table with defined columns) per NFR-5, not prose
- Traceable to R-016 via D-0015

**Validation:**
- Manual check: Downstream Propagation section in spec-panel.md specifies format, consumer (AD-1), and GAP-to-priority-target mapping
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Dependencies:** T02.02 (table template defines the format being propagated), T02.03 (GAP rules define what gets propagated)
**Rollback:** Remove Downstream Propagation section from boundary table documentation

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm Phase 2 (Structural Forcing Functions) is complete; boundary table is fully specified with enforcement, roles, trigger, measurement, and downstream format.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`

**Verification:**
- All 7 tasks (T02.01 through T02.07) completed with evidence artifacts
- Boundary table section is complete: template, enforcement rules, role assignments, trigger logic, overhead measurement, downstream format
- NFR-4 overhead measurement result is available for Gate A evaluation

**Exit Criteria:**
- All deliverables D-0009 through D-0015 have evidence artifacts
- Cumulative overhead (Phase 1 + Phase 2) is measurable from D-0007 and D-0014
- Phase 3 (Gate A) dependency (M1+M2+M3 complete) is satisfied
