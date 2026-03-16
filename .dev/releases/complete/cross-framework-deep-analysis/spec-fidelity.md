---
high_severity_count: 3
medium_severity_count: 8
low_severity_count: 4
total_deviations: 15
validation_complete: true
tasklist_ready: false
---

## Deviation Report

---

### DEV-001
- **ID**: DEV-001
- **Severity**: HIGH
- **Deviation**: Phase 0 (Pre-Sprint Setup) is present in the roadmap but has no corresponding phase in the specification. The spec defines an 8-phase sprint (Phases 1–8); the roadmap introduces a Phase 0 not mentioned in any specification section.
- **Spec Quote**: "A structured sprint (executed by the IronClaude sprint CLI with phase gates) that systematically inventories, compares, debates, and synthesizes insights across both frameworks." (§2) and the workflow diagram shows phases 1–8 only.
- **Roadmap Quote**: "### Phase 0: Pre-Sprint Setup — Sprint infrastructure validated, all dependencies confirmed accessible, phase contracts defined."
- **Impact**: Phase 0 introduces new gate criteria, effort estimates, and open question resolutions (OQ-006, OQ-008) that are not in the spec. Implementers following the roadmap will perform work and produce artifacts (dependency readiness record, tasklists) not specified. This could be additive, but the phase creates binding gate criteria absent from the spec, which may cause confusion about what is required.
- **Recommended Correction**: Either add Phase 0 to the specification as a formal phase with defined artifacts and gate criteria, or restructure the roadmap so that Phase 0 activities are absorbed into Phase 1 preconditions rather than a separate gated phase.

---

### DEV-002
- **ID**: DEV-002
- **Severity**: HIGH
- **Deviation**: The roadmap adds Open Questions (OQ-001 through OQ-008) as a formal resolution structure with binding defaults and phase assignments. The specification does not define an OQ system; open items appear only in §11 (three items: OI-1, OI-2, OI-3) and are not tied to phase gates or enforcement mechanisms.
- **Spec Quote**: "| OI-1 | Do llm-workflows file paths in prompt.md still match current repo state? | Medium | Phase 1 execution | | OI-2 | Should the pipeline-analysis subsystem ... | Low | Before Phase 2 | | OI-3 | Feature ID assignment for v3.0 planning ... | Low | Before roadmap generation |" (§11)
- **Roadmap Quote**: "| OQ-001 | LW path staleness handling | Phase 1 (T01.02) | Proceed with verified paths; flag stale with `path_verified=false, strategy_analyzable=false` | ... | OQ-004 | 'Discard both' verdict content | Before Phase 6 | Produce IC-native improvement item with explicit rationale; placeholder omission not permitted | ... | OQ-005 | Schema validator: script vs. manual | Phase 8 | Produce lightweight schema validator ..." (Open Questions Resolution Plan)
- **Impact**: OQ-004 (discard-both handling), OQ-005 (schema validator), OQ-006 (executor parallelism), and OQ-008 (Auggie unavailability definition) are resolved in the roadmap as binding defaults with enforcement consequences that have no basis in the specification. Implementers may treat these resolutions as authoritative when they were not reviewed in the spec.
- **Recommended Correction**: Align the OQ list to the spec's OI items (OI-1 → OQ-001, OI-2 → OQ-002, OI-3 → OQ-003). OQ-004 through OQ-008 should either be added to the spec as new open items or scoped as implementation-level decisions not requiring spec-level authority.

---

### DEV-003
- **ID**: DEV-003
- **Severity**: HIGH
- **Deviation**: The roadmap omits the explicit `improvement_backlog_schema` field definitions specified in §5.3. The spec defines a YAML schema with 11 required fields; the roadmap references schema compliance but does not reproduce or validate the schema structure.
- **Spec Quote**: "improvement_backlog_schema:\n  fields:\n    - id: string          # IC-{component}-{seq}\n    - component: string\n    - title: string\n    - priority: enum      # P0, P1, P2, P3\n    - effort: enum        # XS, S, M, L, XL\n    - pattern_source: string\n    - rationale: string\n    - file_targets: list[string]\n    - acceptance_criteria: list[string]\n    - risk: string\n    - patterns_not_mass_verified: bool" (§5.3)
- **Roadmap Quote**: "**`improvement-backlog.md`** — Machine-readable items per AC-010 schema; confirm `/sc:roadmap` schema compatibility (SC-009)" (Phase 8 Key Actions)
- **Impact**: The roadmap references "AC-010 schema" which is not defined in either the spec or the roadmap. The 11 required fields from the spec are not enumerated in Phase 6 or Phase 8 actions, so implementers producing `improvement-backlog.md` lack a canonical field reference. This risks schema-incompatible backlog output.
- **Recommended Correction**: Phase 6 and Phase 8 should explicitly reference the 11-field schema from §5.3. Remove the undefined "AC-010 schema" reference and replace with a direct citation of the spec's `improvement_backlog_schema` definition.

---

### DEV-004
- **ID**: DEV-004
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 1 gate criteria adds `strategy_analyzable` dual-status tracking as a required output that is not present in the specification's Phase 1 gate criteria.
- **Spec Quote**: "| Phase 1 | component-map.md produced | 3 (2 inventories + map) | ≥8 cross-framework mappings; ≥8 IC components; ≥11 LW components |" (§5.2)
- **Roadmap Quote**: "≥8 IC components, ≥11 LW components, ≥8 cross-framework mappings, IC-only annotations present, all file paths explicitly verified or flagged stale with `path_verified`/`strategy_analyzable` dual status." (Phase 1 Gate Criteria SC-001)
- **Impact**: The dual-status tracking is a reasonable extension but represents an addition to the spec's gate criteria. Automated gate enforcement based on the spec would not check for `strategy_analyzable` status, creating a compliance gap between spec-defined gates and roadmap-defined gates.
- **Recommended Correction**: Add `path_verified`/`strategy_analyzable` dual-status tracking to the spec's Phase 1 gate criteria in §5.2, or mark it in the roadmap as an implementation detail below the gate threshold.

---

### DEV-005
- **ID**: DEV-005
- **Severity**: MEDIUM
- **Deviation**: The roadmap introduces five named architectural principles for Phase 5 synthesis (evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement) not specified in §3 FR-XFDA-001.5 or §5.2's Phase 5 gate criteria.
- **Spec Quote**: "`merged-strategy.md` covers all component areas from Phase 4 ... Explicit 'rigor without bloat' section defining efficiency constraints ... 'Adopt patterns not mass' principle applied and documented for each adopted pattern ... Discard decisions justified — not just implied ... Merged strategy is internally consistent" (FR-XFDA-001.5)
- **Roadmap Quote**: "Organize cross-component guidance under five architectural principles, with component references explicitly preserved within each principle section: Evidence integrity / Deterministic gates / Restartability / Bounded complexity / Scalable quality enforcement" (Phase 5 Key Actions)
- **Impact**: The five-principle framework reorganizes the synthesis output away from the component-centric structure implied by the spec ("covers all component areas from Phase 4"). If implementers follow the roadmap strictly, the merged strategy is organized by principle rather than by component, which could break the traceability requirement ("no orphaned component areas").
- **Recommended Correction**: Clarify in the spec that component-area coverage can be organized under architectural principles provided traceability is preserved, or align the roadmap to produce a component-centric structure first, then optionally cross-reference principles.

---

### DEV-006
- **ID**: DEV-006
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds a pre-Phase 8 action in Phase 7 — `/sc:roadmap` schema pre-validation before Phase 8 begins — which is not present in FR-XFDA-001.7 or the Phase 7 gate criteria in the spec.
- **Spec Quote**: "FR-XFDA-001.7 Acceptance Criteria: `validation-report.md` with pass/fail per improvement plan item ... All file paths in plan verified to exist via Auggie MCP ... Scope creep check ... Missing connection check ... `final-improve-plan.md` produced with all corrections applied" (§3, FR-XFDA-001.7)
- **Roadmap Quote**: "**Pre-gate action**: Validate `/sc:roadmap` schema expectations against `improvement-backlog.md` schema *before* Phase 8 begins. Schema incompatibilities discovered here are corrected at planning level; Phase 8 confirms schema compliance rather than discovering violations." (Phase 7 Key Actions)
- **Impact**: This is a useful operational addition, but it modifies the Phase 7 gate scope beyond what the spec requires. Teams validating Phase 7 against the spec would not know this pre-validation is required.
- **Recommended Correction**: Add schema pre-validation to the spec's FR-XFDA-001.7 acceptance criteria, or explicitly mark it in the roadmap as a recommended practice beyond spec requirements.

---

### DEV-007
- **ID**: DEV-007
- **Severity**: MEDIUM
- **Deviation**: The roadmap mandates resume testing as a Phase 8 gate condition ("Sprint SHALL NOT complete Phase 8 unless `--start 3` with Phase 1–2 artifacts present succeeds"). The spec lists this as an integration test scenario, not a mandatory gate condition.
- **Spec Quote**: "| Sprint resume from Phase 3 | `--start 3` picks up correctly after Phase 1+2 artifacts exist | (Integration Test)" (§8.2) and NFR-XFDA.5: "Sprint is restartable from any phase gate | Phase-range --start flag works | CLI executor handles resume"
- **Roadmap Quote**: "Verify mandatory **resume testing**: sprint SHALL NOT complete Phase 8 unless `--start 3` with Phase 1–2 artifacts present succeeds; this is a mandatory gate condition, not optional QA" (Phase 8 Key Actions)
- **Impact**: Elevating a test scenario to a hard gate condition changes the execution contract. If resume fails in Phase 8, the spec does not permit halting the sprint, but the roadmap does. This creates a behavioral divergence in failure handling.
- **Recommended Correction**: Either update the spec's §8.2 integration test to designate resume testing as a mandatory Phase 8 gate criterion, or soften the roadmap language to "strongly recommended" to align with the spec's test-scenario framing.

---

### DEV-008
- **ID**: DEV-008
- **Severity**: MEDIUM
- **Deviation**: The roadmap introduces a distinct **Validation reviewer role** (independent of the Architect lead) for Phase 7 execution, with explicit role-separation enforcement. The spec defines no team roles or role-separation requirements.
- **Spec Quote**: No team roles, role separation, or execution responsibility assignments appear anywhere in the specification.
- **Roadmap Quote**: "this phase shall be executed by the **Validation reviewer role**, not the Architect lead, to preserve adversarial independence" and the full Role/Responsibilities table (Resource Requirements section).
- **Impact**: The role structure introduces organizational requirements with no spec basis. In single-operator contexts (e.g., AI sprint execution), the "independent reviewer" constraint may be impossible to satisfy literally, potentially blocking Phase 7 progression.
- **Recommended Correction**: Add a team/role section to the spec (§4 or §5) or add a note that in single-operator execution, adversarial independence is achieved through sequential isolation (complete Phase 6 fully before beginning Phase 7 review). The spec should govern whether role separation is required.

---

### DEV-009
- **ID**: DEV-009
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds a structural leverage priority ordering for Phase 6 improvement planning (5-tier ordering: gate integrity → evidence verification → restartability → traceability automation → artifact schema reliability) that is absent from FR-XFDA-001.6.
- **Spec Quote**: "Each improvement item includes: specific file path(s), what to change, why, priority (P0/P1/P2/P3), effort (XS/S/M/L/XL), dependencies, acceptance criteria ... Risk assessment per item ... Items that require new code distinguished from items that strengthen existing code" (FR-XFDA-001.6)
- **Roadmap Quote**: "Apply structural leverage priority ordering: 1. Gate integrity improvements 2. Evidence verification improvements 3. Restartability/resume semantic improvements 4. Traceability automation improvements 5. Artifact schema reliability improvements" (Phase 6 Key Actions)
- **Impact**: The priority ordering constrains how improvement items are organized within plans in a way the spec does not require. If a component's most important improvement is in category 5, the ordering may de-emphasize it relative to spec-intended priority (P0/P1/P2/P3 tiers).
- **Recommended Correction**: Clarify that the structural leverage ordering is a secondary organizational aid subordinate to the P-tier priority system defined in the spec, or add the priority ordering rationale to FR-XFDA-001.6.

---

### DEV-010
- **ID**: DEV-010
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds four "disqualifying conditions" for Phase 7 that go beyond the spec's acceptance criteria for FR-XFDA-001.7. Specifically, "Recommendations drift into implementation scope" as a disqualifying condition has no direct spec basis.
- **Spec Quote**: FR-XFDA-001.7 acceptance criteria: file path verification, scope creep check, missing connection check, `final-improve-plan.md` production. (§3)
- **Roadmap Quote**: "**Disqualifying conditions** (items failing any of these must be reworked, not approved): Evidence is unverifiable / Copied mass appears in adoption recommendations / Cross-artifact lineage is broken / Recommendations drift into implementation scope" (Phase 7 Key Actions)
- **Impact**: "Disqualifying" status with mandatory rework is a stronger enforcement mechanism than the spec's pass/fail table. The "implementation scope drift" condition may cause valid improvement planning items to be rejected if the reviewer interprets the boundary strictly.
- **Recommended Correction**: Align the disqualifying conditions with the spec's Phase 7 acceptance criteria. Add "implementation scope drift" to the spec's FR-XFDA-001.7 if it is genuinely required, or soften the roadmap to "failing items" rather than "disqualifying conditions."

---

### DEV-011
- **ID**: DEV-011
- **Severity**: LOW
- **Deviation**: The roadmap renames the sprint artifact `sprint-summary.md` content requirements with different field ordering. The spec lists: "findings count, comparison verdicts summary, plan items by priority, estimated total effort, recommended implementation order." The roadmap restates these in the same order but embeds them in Phase 8 actions rather than as a standalone gate criterion.
- **Spec Quote**: "`sprint-summary.md`: findings count, comparison verdicts summary, plan items by priority, estimated total effort, recommended implementation order" (FR-XFDA-001.8)
- **Roadmap Quote**: "**`sprint-summary.md`** — Findings count, verdict summary, items by priority, estimated effort, recommended implementation order" (Phase 8 Key Actions)
- **Impact**: "Comparison verdicts summary" → "verdict summary" is a minor term variation. No correctness impact.
- **Recommended Correction**: No change required. Terminology is equivalent.

---

### DEV-012
- **ID**: DEV-012
- **Severity**: LOW
- **Deviation**: The roadmap adds a token budget breakdown table not present in the specification. The spec contains no token budget section.
- **Spec Quote**: [MISSING] — No token budget section exists in the specification.
- **Roadmap Quote**: "| Phase 0 | 2K | ... | **Total** | **~172K** |" (Token Budget section under Resource Requirements)
- **Impact**: This is an additive operational detail. The spec is silent on token budgeting, so the roadmap's estimates neither contradict nor violate it. However, framing these as planning estimates with caveats ("order-of-magnitude") appropriately signals their non-binding nature.
- **Recommended Correction**: No correction required. The roadmap's caveat language is appropriate.

---

### DEV-013
- **ID**: DEV-013
- **Severity**: LOW
- **Deviation**: The roadmap's Phase 5 gate criteria references five architectural principles sections ("all five principle sections cover relevant components") rather than the spec's component-area completeness framing ("no orphaned component areas").
- **Spec Quote**: "| Phase 5 | merged-strategy.md produced | 1 | Has 'rigor without bloat' section; no component area orphaned |" (§5.2)
- **Roadmap Quote**: "Rigor-without-bloat section present, all five principle sections cover relevant components, no orphaned areas, discard decisions justified, internal consistency verified." (Phase 5 Gate Criteria SC-005)
- **Impact**: Functionally equivalent if "all five principle sections cover relevant components" is interpreted as covering all component areas. The difference is organizational framing rather than a correctness gap. Minor risk if a future automated gate checks for "principle section coverage" rather than "component area coverage."
- **Recommended Correction**: Add "no orphaned component areas" as an explicit check in the roadmap's Phase 5 gate criteria alongside the five-principles check, to maintain direct alignment with the spec gate.

---

### DEV-014
- **ID**: DEV-014
- **Severity**: LOW
- **Deviation**: The roadmap references SC-010, SC-011, SC-012, SC-013, SC-014 as named success criteria but these identifiers are not defined anywhere in the roadmap or the specification.
- **Spec Quote**: [MISSING] — No SC-NNN identifier system is defined in the specification.
- **Roadmap Quote**: "#### Gate Criteria (SC-007, SC-012, SC-013, SC-014)" (Phase 7), "verify end-to-end traceability (SC-010, SC-011)" (Phase 8)
- **Impact**: Internal inconsistency in the roadmap; SC-001 through SC-009 appear to be defined implicitly by phase gates but SC-010 through SC-014 are referenced without definition. Readers cannot determine what these criteria specify.
- **Recommended Correction**: Either define all SC-NNN criteria explicitly in a roadmap section, or remove SC identifiers beyond SC-009 and describe the criteria inline.

---

### DEV-015
- **ID**: DEV-015
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 8 gate criteria adds "≥35 total artifacts in `artifacts/`" as a hard count requirement, but the spec's architecture section (§4.1) lists exactly 34 files (including the spec itself, which is not an artifact), making the ≥35 threshold misaligned with the spec's own file enumeration.
- **Spec Quote**: §4.1 New Files lists: spec (1) + tasklist-index (1) + phase tasklists (8) + inventory-ironclaude (1) + inventory-llm-workflows (1) + component-map (1) + strategy-ic (8) + strategy-lw (11) + comparison (8) + merged-strategy (1) + improve-component (8) + improve-master (1) + validation-report (1) + final-improve-plan (1) + artifact-index (1) + rigor-assessment (1) + improvement-backlog (1) + sprint-summary (1) = 56 total listed files. However, artifacts under `artifacts/` per §4.1 number approximately 35 (excluding spec, tasklist files, and prompt.md).
- **Roadmap Quote**: "`find artifacts/ -type f | wc -l` ≥ 35" (Success Criteria / Measurable Acceptance Criteria)
- **Impact**: The ≥35 count is directionally consistent with §4.1 but not precisely derived from it. If Phase 0 adds artifacts not in §4.1 (e.g., dependency readiness record, OQ resolution log), the count could exceed 35 for non-spec reasons. If some phase produces fewer artifacts than expected, a count-based gate could pass while artifact completeness fails.
- **Recommended Correction**: Replace the count-based gate with a named-artifact checklist gate (enumerate all required artifact filenames per §4.1), or explicitly reconcile the ≥35 count against §4.1's file listing and document how it was derived.

---

## Summary

**Total deviations**: 15 (3 HIGH, 8 MEDIUM, 4 LOW)

**Distribution**:
- HIGH (3): Phase 0 not in spec, OQ system extends beyond spec's OI items, improvement-backlog schema reference undefined
- MEDIUM (8): Dual-status tracking in Phase 1 gate, five-principle synthesis structure, Phase 7 schema pre-validation addition, resume testing elevated to gate condition, Validation reviewer role requirement, Phase 6 priority ordering, Phase 7 disqualifying conditions, artifact count vs. named checklist
- LOW (4): `sprint-summary.md` terminology variation, token budget addition, Phase 5 gate framing, undefined SC-NNN identifiers

**Overall assessment**: The roadmap is substantively faithful to the specification and demonstrates clear derivation from all 8 functional requirements. The deviations are predominantly additive enhancements (Phase 0, OQ system, role structure, schema pre-validation) rather than contradictions. However, the three HIGH deviations create genuine implementation risk: Phase 0 introduces binding gate criteria with no spec basis; the OQ system resolves decisions (OQ-004, OQ-005) that the spec treats as open; and the undefined "AC-010 schema" reference leaves the backlog schema without a traceable authority. These must be resolved before the roadmap can be used as an unambiguous implementation guide.
