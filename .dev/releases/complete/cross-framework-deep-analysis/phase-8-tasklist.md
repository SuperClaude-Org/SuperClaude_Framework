# Phase 8 -- Adversarial Validation

Execute formal architecture review gate by an independent Validation reviewer (not the Architect lead) to preserve adversarial integrity. Pre-gate schema validation occurs before Phase 8 proper; all disqualifying conditions must be resolved before final-improve-plan.md is produced.

---

### T08.01 -- Pre-Gate: Validate /sc:roadmap Schema Against improvement-backlog.md Schema

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | Schema incompatibilities discovered before Phase 9 are corrected at planning level; Phase 9 confirms compliance rather than discovering violations mid-sprint |
| Effort | S |
| Risk | Medium |
| Risk Drivers | analysis (schema validation is a cross-artifact integration check; improvement-backlog.md is an integration boundary artifact) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0030/spec.md`

**Deliverables:**
- D-0030: `/sc:roadmap` schema pre-validation report at `artifacts/D-0030/spec.md` confirming compatibility between the expected improvement-backlog.md schema and `/sc:roadmap` ingestion requirements

**Steps:**
1. **[PLANNING]** Load context: review the schema expectations from the `/sc:roadmap` command definition; review D-0026/D-0028 improvement plan schemas for comparison
2. **[PLANNING]** Check dependencies: D-0028 (improve-master.md) complete; Phase 7 gate SC-006 passed
3. **[EXECUTION]** Extract the `/sc:roadmap` expected schema fields for improvement backlog ingestion (per the `/sc:roadmap` command definition — not an invented identifier)
4. **[EXECUTION]** Compare the schema against the actual improvement item structure in the 8 improve-*.md files and improve-master.md
5. **[EXECUTION]** Identify any incompatibilities: missing required fields, wrong field formats, extra fields not accepted
6. **[EXECUTION]** For any incompatibility: document the correction needed at planning level (add/rename/reformat field)
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify schema compatibility report is complete; zero incompatibilities entering Phase 9; D-0030 findings are referenced in validation-report.md (D-0033) per Gate Criteria requirement
8. **[COMPLETION]** Write schema pre-validation report to `artifacts/D-0030/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0030/spec.md` exists with schema comparison table: `/sc:roadmap` command-defined required fields vs. actual improvement item fields
- Zero schema incompatibilities remain unresolved at end of this task (any found are corrected before Phase 9 begins)
- D-0030 findings are referenced in validation-report.md (D-0033) per Gate Criteria requirement
- Report explicitly confirms `/sc:roadmap` schema is pre-validated for Phase 9 consumption and is reproducible: same schema comparison produces same incompatibility findings

**Validation:**
- Manual check: `artifacts/D-0030/spec.md` contains schema comparison table with zero unresolved incompatibilities; D-0033 references D-0030 findings
- Evidence: linkable artifact produced (`artifacts/D-0030/spec.md`)

**Dependencies:** T07.03, T07.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Pre-gate action that must occur before the formal Phase 8 review gate. Roadmap explicitly requires this runs before Phase 9 (Consolidated Outputs). "AC-010 schema" identifier removed — schema source is the `/sc:roadmap` command definition.

---

### T08.02 -- Execute Formal Architecture Review Gate by Independent Validation Reviewer

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | The formal gate must be executed by the Validation reviewer role (not Architect lead) to preserve adversarial independence; this is an architectural review, not a formatting pass or compliance scan |
| Effort | M |
| Risk | High |
| Risk Drivers | analysis (end-to-end adversarial review; independent reviewer required; phase-wide scope) |
| Tier | STRICT |
| Confidence | [█████████-] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0031/evidence.md`

**Deliverables:**
- D-0031: Formal architecture review gate execution record at `artifacts/D-0031/evidence.md` confirming the Validation reviewer role executed the review (not Architect lead) and gate initiated

**Steps:**
1. **[PLANNING]** Load context: confirm Validation reviewer identity is distinct from Architect lead; review scope of formal gate (architectural review, not formatting scan, not compliance scan)
2. **[PLANNING]** Check dependencies: D-0030 (schema pre-validation) complete; Phase 7 gate SC-006 passed
3. **[EXECUTION]** Confirm that the Validation reviewer role is active and distinct from the Architect lead who produced Phases 5-7 artifacts
4. **[EXECUTION]** Initiate formal architecture review gate: review all improvement plan documents for architectural quality — this is a formal architecture review, not a formatting pass or compliance scan
5. **[EXECUTION]** Record: reviewer role identity, gate start timestamp, scope declaration (formal architecture review — explicitly not a formatting pass or compliance scan)
6. **[EXECUTION]** Note any optional human reviewer participation (recommended per roadmap for Phase 7/8)
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify gate is executed by Validation reviewer role; architectural review scope is explicitly declared as formal architecture review (not a formatting pass or compliance scan)
8. **[COMPLETION]** Write gate execution record to `artifacts/D-0031/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0031/evidence.md` exists confirming Validation reviewer role executed the gate (not Architect lead)
- Gate scope is declared as "formal architecture review, not a formatting pass or compliance scan" — this exact negative definition must appear in the record
- Gate start is recorded with scope declaration
- If optional human reviewer participated, their participation is noted

**Validation:**
- Manual check: `artifacts/D-0031/evidence.md` contains reviewer role declaration and scope statement explicitly reading "formal architecture review, not a formatting pass or compliance scan"
- Evidence: linkable artifact produced (`artifacts/D-0031/evidence.md`)

**Dependencies:** T08.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT with Sub-Agent Delegation Required (Risk=High + STRICT tier). Roadmap AC mandates independent Validation reviewer; cannot be self-reviewed by the Architect lead. Patch L12 applied: gate scope AC now includes the negative definition per roadmap Key Action 2.

---

### T08.03 -- Validate Six Dimensions: Evidence, Anti-Sycophancy, Patterns-Not-Mass, Completeness, Scope, Lineage

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Six-dimension validation with four Disqualifying Conditions catches evidence gaps, mass adoption, broken lineage, and scope drift that would invalidate the improvement plan before Phase 9 |
| Effort | M |
| Risk | High |
| Risk Drivers | analysis, security (end-to-end adversarial validation; disqualifying conditions; cross-artifact lineage check) |
| Tier | STRICT |
| Confidence | [█████████-] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0032/evidence.md`

**Deliverables:**
- D-0032: Six-dimension validation pass results at `artifacts/D-0032/evidence.md` with per-item pass/fail for all improvement plan items across all six validation dimensions and four Disqualifying Conditions

**Steps:**
1. **[PLANNING]** Load context: review all improve-*.md files (D-0026), improve-master.md (D-0028), merged-strategy.md (D-0022); identify the six validation dimensions and four Disqualifying Conditions from roadmap
2. **[PLANNING]** Check dependencies: D-0031 (formal gate initiated); all Phase 7 deliverables complete
3. **[EXECUTION]** Dimension 1 — File path existence: verify all file paths cited in improvement items exist in the IronClaude repo via Auggie MCP (NFR-003)
4. **[EXECUTION]** Dimension 2 — Anti-sycophancy coverage: verify complete anti-sycophancy coverage across all improvement plan documents
5. **[EXECUTION]** Dimension 3 — Patterns-not-mass compliance: verify all LW-sourced items have `patterns_not_mass: true` and "why not full import" sentence
6. **[EXECUTION]** Dimension 4 — Completeness: verify all **Phase 1** component groups are represented in improvement plans (no orphaned component areas); note: "Phase 1" is the tasklist-numbered phase (roadmap Phase 0 — Pre-Sprint Setup is not the source; the component inventory from roadmap Phase 1 / tasklist Phase 2 is the source)
7. **[EXECUTION]** Dimension 5 — Scope control: verify no improvement item drifts into implementation scope (all items describe planning-level improvements, not code changes)
8. **[EXECUTION]** Dimension 6 — Cross-artifact lineage: verify traceability chain inventory → strategy → comparison → merged → plan → backlog is intact with no broken links
9. **[EXECUTION]** For each item, evaluate against the four Disqualifying Conditions (items triggering any condition are classified Fail-Rework and must not be approved):
   - (1) **Evidence unverifiable**: any claim whose supporting evidence cannot be verified via Auggie MCP or documented fallback
   - (2) **Copied mass in adoption**: any LW-sourced item that imports bulk patterns rather than extracting minimum-viable pattern adaptation
   - (3) **Broken cross-artifact lineage**: any item whose traceability chain back to Phase 1 inventory is interrupted
   - (4) **Implementation-scope drift**: any item that describes actual code implementation rather than planning-level improvement
10. **[VERIFICATION]** Sub-agent (quality-engineer): verify all six dimensions show Pass; verify all four Disqualifying Conditions evaluated per item; zero items approved with an unresolved Disqualifying Condition
11. **[COMPLETION]** Write six-dimension validation results (including Disqualifying Condition evaluation per item) to `artifacts/D-0032/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0032/evidence.md` exists with per-item pass/fail results for all six validation dimensions
- All four Disqualifying Conditions evaluated per item: (1) evidence unverifiable, (2) copied mass in adoption, (3) broken cross-artifact lineage, (4) implementation-scope drift — any triggered condition classifies the item Fail-Rework
- Zero items approved with an unresolved Disqualifying Condition
- Dimension 4 (Completeness) references **Phase 1** component groups (not Phase 2); validation results are reproducible: same input documents produce same six-dimension results

**Validation:**
- Manual check: six dimension sections in `artifacts/D-0032/evidence.md` each show Pass; Disqualifying Condition evaluation table present; zero unresolved Fail-Rework entries
- Evidence: linkable artifact produced (`artifacts/D-0032/evidence.md`)

**Dependencies:** T08.01, T08.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Patches H10 + H11 applied. H10: Dimension 4 corrected from "Phase 2 components" to "Phase 1 components" (roadmap Key Action 3 item 4). H11: Four Disqualifying Conditions added to steps 9 and AC per roadmap Key Action 4 — items triggering any condition are Fail-Rework, not approvable.

---

### T08.04 -- Produce validation-report.md with Per-Item Pass/Fail Status

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | validation-report.md is the formal gate artifact required by SC-007; it must document per-item pass/fail status for all improvement plan items reviewed in T08.03 |
| Effort | M |
| Risk | Medium |
| Risk Drivers | analysis (per-item pass/fail documentation across all improvement plan items) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0033/spec.md`

**Deliverables:**
- D-0033: `validation-report.md` at `artifacts/D-0033/spec.md` with per-item pass/fail status for all improvement plan items reviewed in the Phase 8 formal gate

**Steps:**
1. **[PLANNING]** Load context: review D-0032 (six-dimension validation results) as primary input; identify all improvement items reviewed; identify all Fail-Rework items by Disqualifying Condition for T08.05 consumption
2. **[PLANNING]** Check dependencies: D-0032 complete (all six dimensions resolved; all Disqualifying Conditions evaluated)
3. **[EXECUTION]** Produce validation-report.md with: (a) gate summary (Validation reviewer role, date, scope), (b) per-item pass/fail table covering all improvement items from D-0026 and D-0028, (c) per-dimension summary counts (pass/fail/retired), (d) D-0030 schema pre-validation findings referenced explicitly
4. **[EXECUTION]** For each Fail-Rework item: list it with Fail classification and its specific Disqualifying Condition reference (identifies which of the four conditions was triggered) — this list is for T08.05 consumption; do not include correction text here
5. **[EXECUTION]** Include explicit status for each of the `/sc:roadmap` schema criteria from D-0030; reference D-0030 findings
6. **[EXECUTION]** Mark all retired items with explicit retirement rationale
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify validation-report.md has per-item pass/fail for all improvement plan items; no item is omitted; Fail items list Disqualifying Condition references; D-0030 findings are referenced
8. **[COMPLETION]** Write validation-report.md to `artifacts/D-0033/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0033/spec.md` exists as validation-report.md with per-item pass/fail table covering all improvement plan items
- Every improvement item from D-0026 and D-0028 appears in the per-item table with a non-empty status (Pass/Fail-Rework/Retired)
- Failed items are listed with Fail classification and Disqualifying Condition reference for T08.05 consumption (not with correction text — corrections are T08.05's responsibility)
- `/sc:roadmap` schema confirmation from D-0030 is included in the validation summary with D-0030 explicitly referenced

**Validation:**
- Manual check: item count in validation-report.md per-item table matches total improvement item count across all improve-*.md files; Fail items include Disqualifying Condition references
- Evidence: linkable artifact produced (`artifacts/D-0033/spec.md`)

**Dependencies:** T08.02, T08.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Patch M13 applied. Removed "list of reworked items with corrections" from AC — corrections are T08.05's scope. Fail items in this report list classification + Disqualifying Condition reference only; T08.05 applies the actual corrections.

---

### T08.05 -- Correct All Failures and Produce final-improve-plan.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | final-improve-plan.md is the corrected, validation-approved improvement plan that Phase 9 consolidated outputs consume; it must have all Phase 8 corrections applied, all file paths verified, and confirmed /sc:roadmap schema compliance |
| Effort | M |
| Risk | Medium |
| Risk Drivers | analysis (correction application across multiple improvement documents; cross-artifact update required) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0034/spec.md`

**Deliverables:**
- D-0034: `final-improve-plan.md` at `artifacts/D-0034/spec.md` incorporating all Phase 8 corrections, verified file paths, and `/sc:roadmap` schema compliance confirmation

**Steps:**
1. **[PLANNING]** Load context: review D-0033 (validation-report.md) for all Fail-Rework items with their Disqualifying Condition references; review D-0028 (improve-master.md) as the base document
2. **[PLANNING]** Check dependencies: D-0033 complete; all Fail-Rework items identified with Disqualifying Condition references from T08.04
3. **[EXECUTION]** For each Fail-Rework item in D-0033: apply the specific correction targeting the identified Disqualifying Condition (fix unverifiable evidence, fix mass adoption flag, restore broken lineage, or narrow scope drift)
4. **[EXECUTION]** For each Retired item in D-0033: include in final-improve-plan.md with explicit retirement annotation and rationale
5. **[EXECUTION]** Verify all file paths referenced in final-improve-plan.md via Auggie MCP — this is a Gate Criteria SC-007 requirement: "all file paths verified"
6. **[EXECUTION]** Produce final-improve-plan.md as a consolidated document incorporating: validated improvement items from all 8 component plans, dependency graph from D-0028, all Phase 8 corrections applied, validation approval header citing D-0033 as the approving gate artifact
7. **[EXECUTION]** Verify final-improve-plan.md does not contain any items that still fail the six dimensions from D-0032
8. **[VERIFICATION]** Sub-agent (quality-engineer): verify final-improve-plan.md has validation approval header citing D-0033; all corrections applied; all file paths verified via Auggie MCP; zero dimension failures remain; schema compliance confirmed against D-0030
9. **[COMPLETION]** Write final-improve-plan.md to `artifacts/D-0034/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0034/spec.md` exists as final-improve-plan.md with validation approval header citing `artifacts/D-0033/spec.md` as the approving gate artifact
- All file paths in final-improve-plan.md are verified via Auggie MCP (Gate Criteria SC-007: "all file paths verified")
- All Fail-Rework items from D-0033 have corrections applied and now pass the relevant Disqualifying Condition check
- final-improve-plan.md is confirmed schema-compliant with `/sc:roadmap` expectations established in D-0030, satisfying Gate Criteria pre-validation requirement

**Validation:**
- Manual check: `artifacts/D-0034/spec.md` contains validation approval header; file path verification record present; correction count matches Fail-Rework count from D-0033; schema compliance confirmation cites D-0030
- Evidence: linkable artifact produced (`artifacts/D-0034/spec.md`)

**Dependencies:** T08.03, T08.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Patches H12 + M14 applied. H12: file path verification via Auggie MCP added to step 5 and AC (Gate Criteria SC-007 requirement). M14: `/sc:roadmap` schema compliance confirmation added to AC, satisfying Gate Criteria pre-validation requirement established in D-0030.

---

### Checkpoint: End of Phase 8

**Purpose:** Gate validation (SC-007, SC-012, SC-013, SC-014) that all improvements are formally validated, all file paths verified, schema compliance confirmed, and the final improvement plan is correction-complete before consolidated outputs are produced.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P08-END.md`

**Verification:**
- `artifacts/D-0033/spec.md` (validation-report.md) exists with per-item pass/fail status, D-0030 findings referenced, and Fail items listing Disqualifying Condition references for T08.05 consumption
- `artifacts/D-0034/spec.md` (final-improve-plan.md) exists with validation approval header, all Phase 8 corrections applied, all file paths verified via Auggie MCP, and `/sc:roadmap` schema compliance confirmed against D-0030
- Six-dimension validation at D-0032 shows all Pass; all four Disqualifying Conditions evaluated per item; zero unresolved Fail-Rework entries

**Exit Criteria:**
- Gate SC-007 passes: validation-report.md with per-item status, final-improve-plan.md with corrections applied, all file paths Auggie-MCP-verified, `/sc:roadmap` schema pre-validated via D-0030, all failed items corrected or explicitly retired
- SC-012 (all file paths Auggie MCP verified per T08.05 step 5), SC-013 (patterns-not-mass compliant), SC-014 (cross-artifact lineage intact) all pass
- D-0031 confirms Validation reviewer role executed the gate with scope declared as "formal architecture review, not a formatting pass or compliance scan" (adversarial independence preserved)
