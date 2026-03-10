---
high_severity_count: 3
medium_severity_count: 7
low_severity_count: 5
total_deviations: 15
validation_complete: true
tasklist_ready: false
remediation_status: complete
findings_fixed: 10
findings_no_action: 5
---

## Deviation Report

### DEV-001 — `NO_ACTION_REQUIRED`
- **ID**: DEV-001
- **Status**: **NO_ACTION_REQUIRED** — Reclassified to LOW; roadmap correctly focuses on delta
- **Severity**: HIGH
- **Deviation**: Spec lists the pipeline as "12 steps" with steps 1-11 (step 2 being parallel 2a/2b), but the roadmap describes only "two new post-validation steps" (remediate + certify). The spec explicitly lists a step count as "12 steps" in §2.1 — the roadmap's executive summary says the same but omits the detailed step listing entirely.
- **Spec Quote**: "Step 1: extract / Step 2a: generate-A } parallel / Step 2b: generate-B } / Step 3: diff / Step 4: debate / Step 5: score / Step 6: merge / Step 7: test-strategy / Step 8: spec-fidelity / Step 9: validate / Step 10: remediate / Step 11: certify"
- **Roadmap Quote**: "This release extends the `roadmap run` pipeline with two new post-validation steps — **remediate** (step 10) and **certify** (step 11)."
- **Impact**: LOW — The roadmap correctly identifies the two new steps and their positions. The existing steps 1-9 are inherited infrastructure and not the roadmap's responsibility to re-enumerate. Reclassifying to LOW on reflection.
- **Recommended Correction**: No action needed; the roadmap correctly focuses on the delta.

*Reclassified: This is actually LOW, not HIGH. Revising.*

### DEV-001 (Revised) — `FIXED`
- **ID**: DEV-001
- **Status**: **FIXED** — Roadmap aligned to `remediate_parser.py` per spec §4.1
- **Severity**: HIGH
- **Deviation**: Spec §4.1 names the parser module `remediate_parser.py`. Roadmap Phase 1 names it `finding_parser.py`. This naming inconsistency affects the implementation plan's new-file inventory.
- **Spec Quote**: "`remediate_parser.py` | Parse validation reports → `Finding` objects | 120-150"
- **Roadmap Quote**: "Primary report parser (`finding_parser.py`) for `validate/reflect-merged.md` and `validate/merged-validation-report.md`" and in module table: "`finding_parser.py` | `roadmap.models` | `remediate_executor.py`"
- **Impact**: Implementers following the roadmap will create `finding_parser.py` while the spec mandates `remediate_parser.py`. Import statements, test file names, and cross-references will diverge from spec.
- **Recommended Correction**: Align roadmap module name to `remediate_parser.py` per spec §4.1, or document the rename rationale if intentional.

### DEV-002 — `FIXED`
- **ID**: DEV-002
- **Status**: **FIXED** — `certify_gates.py` added as separate module; `certify_executor.py` retained with proper import chain
- **Severity**: HIGH
- **Deviation**: Spec §4.1 lists exactly 5 new files. Roadmap Phase 4 introduces a `certify_executor.py` module not present in the spec's new file inventory. The spec lists `certify_gates.py` for gate definitions but the roadmap does not list `certify_gates.py` as a standalone module — instead it bundles gate logic into `certify_executor.py`.
- **Spec Quote**: New files table: "`certify_gates.py` | Gate definition for certification step | 40-50"
- **Roadmap Quote**: Phase 4 new modules: "`certify_executor.py` | `pipeline.models`, `roadmap.models` | `execute_pipeline()`"
- **Impact**: The roadmap adds an unspecified module (`certify_executor.py`) and omits a specified one (`certify_gates.py`). This changes the module inventory, import graph, and test file mapping.
- **Recommended Correction**: Either add `certify_gates.py` as a separate module per spec, or document the consolidation decision. Also reconcile `certify_executor.py` with the spec's file inventory.

### DEV-003 — `FIXED`
- **ID**: DEV-003
- **Status**: **FIXED** — Phase mapping table added to §6 mapping spec's 4 phases to roadmap's 7 phases (P0-P6)
- **Severity**: HIGH
- **Deviation**: Roadmap adds a "Phase 0: Discovery and Architecture Lock" (0.5 days) not present in the spec's §4.4 implementation phases. The spec defines 4 phases; the roadmap defines 7 phases (P0-P6). This restructures the implementation plan significantly.
- **Spec Quote**: "Phase 1: Parser + Models (1 sprint) / Phase 2: Remediation Executor (1-2 sprints) / Phase 3: Certification (1 sprint) / Phase 4: Pipeline Integration (0.5-1 sprint)"
- **Roadmap Quote**: "Phase 0: Discovery and Architecture Lock / Duration: 0.5 days / Phase 1: Foundation ... / Phase 2: Interactive Prompt ... / Phase 3: Remediation Orchestrator ... / Phase 4: Certification ... / Phase 5: Resume & State ... / Phase 6: Integration & Hardening"
- **Impact**: The spec's 4-phase plan is restructured into 7 phases with different scoping. Spec Phase 2 (Remediation Executor) maps to roadmap Phases 2+3. Spec Phase 4 (Pipeline Integration) is split across roadmap Phases 5+6. While the roadmap is more granular, it diverges from the spec's phase structure and numbering, which will cause confusion when referencing "Phase 2" across documents.
- **Recommended Correction**: Add a phase mapping table showing spec phases → roadmap phases to maintain traceability.

### DEV-004 — `FIXED`
- **ID**: DEV-004
- **Status**: **FIXED** — Sprint-to-days conversion note added to §6 (1 sprint = 3-5 working days)
- **Severity**: MEDIUM
- **Deviation**: Spec §4.4 uses "sprint" as the time unit for phases. Roadmap uses "days" throughout. The spec states "estimated_effort: 3-5 sprints" in frontmatter. Roadmap total is "13.5-19 days" / "~11-15 with overlap".
- **Spec Quote**: "Phase 1: Parser + Models (1 sprint)" / "Phase 2: Remediation Executor (1-2 sprints)" / "estimated_effort: 3-5 sprints"
- **Roadmap Quote**: "Phase 1: Foundation — 2–3 days" / "Phase 3: Remediation Orchestrator — 4–6 days" / "Total: 13.5–19 days"
- **Impact**: Without a defined sprint-to-days mapping, it's unclear whether the roadmap's timeline aligns with the spec's 3-5 sprint estimate. If 1 sprint = 5 days, then 3-5 sprints = 15-25 days, which roughly aligns with 13.5-19 days. But this is ambiguous.
- **Recommended Correction**: State the sprint duration assumption explicitly, or note the conversion from the spec's sprint-based estimate to the roadmap's day-based timeline.

### DEV-005 — `FIXED`
- **ID**: DEV-005
- **Status**: **FIXED** — Dual-nature clarification appended to Phase 3 deliverable #11
- **Severity**: MEDIUM
- **Deviation**: Spec §2.3.7 states the remediate step "presents as a single Step to `execute_pipeline()`" but then clarifies it "does NOT use `execute_pipeline()` for its internal agents." The roadmap's §2.5 execution flow correctly captures this but the roadmap's Phase 3 deliverable #11 says "Step registration: `remediate` step with `REMEDIATE_GATE`" without clarifying the dual nature (outer step registration vs. internal ClaudeProcess dispatch).
- **Spec Quote**: "The remediate step presents as a **single Step** to `execute_pipeline()`... The `remediate_executor` does NOT use `execute_pipeline()` for its internal agents."
- **Roadmap Quote**: "Step registration: `remediate` step with `REMEDIATE_GATE` — FR-017, FR-020"
- **Impact**: Minor — the roadmap does correctly describe this architecture elsewhere (Phase 3 deliverable #6, architectural constraints). The deliverable line is just abbreviated.
- **Recommended Correction**: Add a note to Phase 3 deliverable #11 clarifying that step registration exposes the step to the outer pipeline while internal dispatch uses ClaudeProcess directly.

### DEV-006 — `FIXED`
- **ID**: DEV-006
- **Status**: **FIXED** — Finding lifecycle updated to `PENDING → FIXED / FAILED / SKIPPED`
- **Severity**: MEDIUM
- **Deviation**: Spec §2.3.1 defines `Finding.status` with four possible values: "PENDING", "FIXED", "FAILED", "SKIPPED". Roadmap Phase 0 defines the finding lifecycle as "SKIPPED → FIXED / FAILED", omitting "PENDING" as an initial state.
- **Spec Quote**: "`status: str  # 'PENDING', 'FIXED', 'FAILED', 'SKIPPED'`"
- **Roadmap Quote**: "Define canonical finding lifecycle: `SKIPPED` → `FIXED` / `FAILED`"
- **Impact**: The roadmap's lifecycle omits PENDING, which the spec defines as one of the four valid status values. Findings start as PENDING before being processed; the roadmap's lifecycle description skips this initial state.
- **Recommended Correction**: Update the lifecycle to include PENDING as the initial state: `PENDING → FIXED / FAILED / SKIPPED`.

### DEV-007 — `FIXED`
- **ID**: DEV-007
- **Status**: **FIXED** — Added "Prompt template per spec §2.3.4" to Phase 3 deliverable #3
- **Severity**: MEDIUM
- **Deviation**: Spec §2.3.4 provides a detailed agent prompt template with exact wording ("You are a remediation specialist...") and constraint list. The roadmap references FR-014 for prompt building but does not reproduce or reference the exact prompt template.
- **Spec Quote**: "You are a remediation specialist. Apply ONLY the fixes listed below. Do not change anything else. Do not add commentary or explanations. ## Target File: {file_path} ## Findings to Fix ... ## Constraints ..."
- **Roadmap Quote**: "Prompt builder (`remediate_prompts.py`): pure function producing agent prompts with target file, finding details, constraints — FR-014, NFR-004"
- **Impact**: The roadmap relies on FR-014 traceability, but since the spec itself IS the source document, implementers need to refer back to spec §2.3.4 for the actual prompt template. This is acceptable if FR-014 traces to spec §2.3.4, but the traceability is implicit.
- **Recommended Correction**: Add an explicit reference: "Prompt template per spec §2.3.4" in the Phase 3 prompt builder deliverable.

### DEV-008 — `FIXED`
- **ID**: DEV-008
- **Status**: **FIXED** — Added cross-file prompt structure spec reference (§2.3.4) to Phase 3 deliverable #2
- **Severity**: MEDIUM
- **Deviation**: Spec §2.3.4 specifies cross-file finding prompt examples with exact wording for how each agent's prompt fragment should be structured. The roadmap mentions cross-file handling (Phase 3 deliverable #2) but provides no detail on the scoped prompt fragment pattern.
- **Spec Quote**: "Agent 1 (roadmap.md) prompt fragment: ### F-05 [WARNING] test phase assignment conflict - Location: roadmap.md:§3.1 Phase 1 Tests ... - Fix Guidance (YOUR FILE): ... - Note: The test-strategy.md side of this fix is handled by a separate agent."
- **Roadmap Quote**: "Cross-file finding handling: include in both agents' prompts with scoped guidance — FR-013"
- **Impact**: The spec's detailed cross-file prompt pattern (including "Fix Guidance (YOUR FILE):" and "Note:" fields) is critical for correct agent behavior but is only referenced by requirement ID in the roadmap.
- **Recommended Correction**: Add a note that cross-file prompt structure follows spec §2.3.4 examples verbatim.

### DEV-009 — `FIXED`
- **ID**: DEV-009
- **Status**: **FIXED** — Consolidated test file inventory table added to §4 with all 6 test files
- **Severity**: MEDIUM
- **Deviation**: Spec §4.3 lists 6 test files. Roadmap does not enumerate test files in a consolidated list; test expectations are spread across phase exit criteria.
- **Spec Quote**: "`tests/roadmap/test_remediate_parser.py` | Finding extraction from various report formats / `tests/roadmap/test_remediate_prompts.py` | Prompt construction... / `tests/roadmap/test_remediate_executor.py` | Orchestration flow... / `tests/roadmap/test_certify_prompts.py` | Certification prompt... / `tests/roadmap/test_certify_gates.py` | Gate criteria validation / `tests/roadmap/test_pipeline_integration.py` | End-to-end..."
- **Roadmap Quote**: [MISSING — no consolidated test file inventory]
- **Impact**: Implementers must infer test file names from phase deliverables rather than having an explicit inventory. Some spec test files (e.g., `test_certify_gates.py`) may be overlooked if `certify_gates.py` is consolidated into `certify_executor.py` (per DEV-002).
- **Recommended Correction**: Add a consolidated test file inventory section to the roadmap, aligned with the module changes.

### DEV-010 — `FIXED`
- **ID**: DEV-010
- **Status**: **FIXED** — Requirements Traceability Matrix added as §9 mapping all FR/NFR IDs to spec sections
- **Severity**: MEDIUM
- **Deviation**: Roadmap introduces requirement IDs (FR-001 through FR-032, NFR-001 through NFR-014) not defined in the spec. These appear to be derived from the spec but are never enumerated or defined anywhere.
- **Spec Quote**: [No FR/NFR numbering system used — requirements are stated in prose]
- **Roadmap Quote**: "FR-007", "FR-001", "NFR-004", "FR-029", "NFR-009", etc. (used extensively throughout all phases)
- **Impact**: The requirement IDs provide useful traceability but since they have no definition source, they cannot be verified against the spec. An implementer cannot look up "FR-013" to confirm what it means.
- **Recommended Correction**: Either add a requirements traceability matrix mapping FR/NFR IDs to spec section references, or remove the IDs and reference spec sections directly.

### DEV-011 — `NO_ACTION_REQUIRED`
- **ID**: DEV-011
- **Status**: **NO_ACTION_REQUIRED** — Spec serves as prompt template source; no roadmap change needed
- **Severity**: LOW
- **Deviation**: Spec §2.4.2 provides an exact certification prompt template. Roadmap Phase 4 deliverable #1 references it abstractly.
- **Spec Quote**: "You are a certification specialist. The following N findings were reported during validation and remediated. For each finding, verify the fix was applied correctly..."
- **Roadmap Quote**: "Certification prompt builder (`certify_prompts.py`): pure function, scoped sections only (not full file) — FR-024, NFR-004, NFR-011"
- **Impact**: Low — the roadmap correctly conveys the scoped-sections approach. The exact prompt wording is an implementation detail that the prompt builder will encode.
- **Recommended Correction**: None required; the spec serves as the prompt template source.

### DEV-012 — `NO_ACTION_REQUIRED`
- **ID**: DEV-012
- **Status**: **NO_ACTION_REQUIRED** — Valid additive elaborations; no contradiction with spec
- **Severity**: LOW
- **Deviation**: Roadmap adds OQ-004 through OQ-008 as "deferred with defaults" open questions not present in the spec. The spec resolves OQ-001 through OQ-003 only.
- **Spec Quote**: "OQ-001 [RESOLVED]... OQ-002 [RESOLVED]... OQ-003 [RESOLVED]..."
- **Roadmap Quote**: "OQ-004: Findings referencing non-allowlist files / OQ-005: Section-to-line resolution for deduplication / OQ-006: Certify gate when certification-report.md doesn't exist / OQ-007: CONFLICT agreement findings / OQ-008: Schema version bump"
- **Impact**: These are reasonable implementation-time questions with sensible defaults. They don't contradict the spec but extend it.
- **Recommended Correction**: None required — these are valid additive elaborations.

### DEV-013 — `NO_ACTION_REQUIRED`
- **ID**: DEV-013
- **Status**: **NO_ACTION_REQUIRED** — Additive risk entries; no contradiction
- **Severity**: LOW
- **Deviation**: Roadmap adds risk entries R-007 through R-011 not present in the spec's §6 risk table. The spec has 5 risks; the roadmap has 11.
- **Spec Quote**: Spec §6 lists 5 risks: "Remediation agent introduces new issues", "Report format changes break parser", "Cross-file findings cause conflicting edits", "User interrupts during remediation", "Certification agent is too lenient"
- **Roadmap Quote**: Roadmap §3 adds: "R-007: Atomic write race during rollback", "R-008: ClaudeProcess behavior drift", "R-009: Allowlist mismatch", "R-010: Performance overhead exceeds SC-006", "R-011: State schema breaks existing consumers"
- **Impact**: Additive improvement — the roadmap identifies additional risks with mitigations. No contradiction.
- **Recommended Correction**: None required.

### DEV-014 — `NO_ACTION_REQUIRED`
- **ID**: DEV-014
- **Status**: **NO_ACTION_REQUIRED** — Additive operational guidance; no contradiction
- **Severity**: LOW
- **Deviation**: Roadmap adds an "Implementation Checklist" section (§8) and "Resource Requirements" section (§4) not present in the spec.
- **Spec Quote**: [MISSING — no implementation checklist or resource requirements sections]
- **Roadmap Quote**: "§8. Implementation Checklist: 1. Do not start with agent orchestration... 7. State schema is a two-stage design" and "§4. Resource Requirements and Dependencies"
- **Impact**: Additive improvement — provides operational guidance for implementers.
- **Recommended Correction**: None required.

### DEV-015 — `NO_ACTION_REQUIRED`
- **ID**: DEV-015
- **Status**: **NO_ACTION_REQUIRED** — Both documents are consistent; no deviation
- **Severity**: LOW
- **Deviation**: Spec §2.3.6 remediation-tasklist frontmatter includes a `generated` timestamp field. The roadmap's REMEDIATE_GATE `required_frontmatter_fields` (Phase 2 deliverable #8) does not explicitly list `generated` as a required field, though the spec's gate definition in §2.3.7 also omits it.
- **Spec Quote**: Tasklist example frontmatter: "generated: 2026-03-09T14:30:00Z" / REMEDIATE_GATE required fields: "type, source_report, source_report_hash, total_findings, actionable, skipped"
- **Roadmap Quote**: "`REMEDIATE_GATE` definition with required fields, minimum line count, semantic validation — FR-017, FR-020"
- **Impact**: The `generated` field appears in the spec's example output but is not in the gate's required fields list. This is consistent between spec and roadmap (both omit it from required fields), so there is no actual deviation — just an observation.
- **Recommended Correction**: None required — both documents are consistent.

## Summary

**Remediation Status**: COMPLETE

**Severity Distribution**:
- **HIGH**: 3 deviations — 2 FIXED (DEV-001 Revised, DEV-002), 1 FIXED (DEV-003) = **3/3 FIXED**
- **MEDIUM**: 7 deviations — **7/7 FIXED** (DEV-004 through DEV-010)
- **LOW**: 5 deviations — **5/5 NO_ACTION_REQUIRED** (DEV-011 through DEV-015)

**Remediation Ledger**:

| Finding | Severity | Status | Fix Applied |
|---------|----------|--------|-------------|
| DEV-001 | HIGH (reclassified LOW) | NO_ACTION_REQUIRED | Roadmap correctly focuses on delta |
| DEV-001 (Revised) | HIGH | FIXED | Module name aligned to `remediate_parser.py` |
| DEV-002 | HIGH | FIXED | `certify_gates.py` added as separate module |
| DEV-003 | HIGH | FIXED | Phase mapping table added to §6 |
| DEV-004 | MEDIUM | FIXED | Sprint-to-days conversion note added to §6 |
| DEV-005 | MEDIUM | FIXED | Dual-nature clarification on Phase 3 deliverable #11 |
| DEV-006 | MEDIUM | FIXED | Finding lifecycle includes PENDING initial state |
| DEV-007 | MEDIUM | FIXED | Spec §2.3.4 reference added to prompt builder |
| DEV-008 | MEDIUM | FIXED | Spec §2.3.4 cross-file prompt reference added |
| DEV-009 | MEDIUM | FIXED | Test file inventory table added to §4 |
| DEV-010 | MEDIUM | FIXED | Requirements Traceability Matrix added as §9 |
| DEV-011 | LOW | NO_ACTION_REQUIRED | — |
| DEV-012 | LOW | NO_ACTION_REQUIRED | — |
| DEV-013 | LOW | NO_ACTION_REQUIRED | — |
| DEV-014 | LOW | NO_ACTION_REQUIRED | — |
| DEV-015 | LOW | NO_ACTION_REQUIRED | — |

**Key Findings**:

The three HIGH-severity deviations center on structural divergences between the spec and roadmap:

1. **Module naming** (`remediate_parser.py` vs `finding_parser.py`) — a direct naming conflict that will cause confusion.
2. **Module inventory** (`certify_executor.py` added, `certify_gates.py` missing) — changes the file structure without documenting the rationale.
3. **Phase restructuring** (4 spec phases → 7 roadmap phases) — while more granular, the renumbering breaks cross-document traceability.

The MEDIUM deviations largely concern insufficient detail in the roadmap for spec elements that have precise definitions (prompt templates, status lifecycles, test file inventory) and the use of undefined FR/NFR requirement IDs that cannot be traced back to the spec.

The roadmap is overall faithful to the spec's design intent and adds valuable elaboration (additional risks, resource requirements, implementation checklist, open question defaults). The deviations are primarily structural/organizational rather than behavioral — the roadmap does not contradict any functional requirement, but it renames, reorganizes, and under-references the spec's precise definitions.
