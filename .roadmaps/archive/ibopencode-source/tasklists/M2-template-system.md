# TASKLIST — M2: Template System

## Metadata & Artifact Paths
- **TASKLIST_ROOT**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/tasklists/`
- **Tasklist Path**: `TASKLIST_ROOT/M2-template-system.md`
- **Execution Log Path**: `TASKLIST_ROOT/M2-execution-log.md`
- **Checkpoint Reports Path**: `TASKLIST_ROOT/checkpoints/M2/`
- **Evidence Root**: `TASKLIST_ROOT/evidence/M2/`
- **Artifacts Root**: `TASKLIST_ROOT/artifacts/M2/`

## Source Snapshot
- Milestone 2: Template System from v3.0-roadmap-gen roadmap
- 5 deliverables: DOC-001, DOC-002, DOC-003, REQ-006, REQ-007
- Objective: Create starter templates and template evaluation logic
- Dependencies: M1 (Phases 0-2 complete)
- Estimated Complexity: Medium
- Risk Level: Medium

## Deterministic Rules Applied
- Task IDs: `T02.XX` format (Phase 2, sequential tasks)
- Deliverable IDs: `D-M2-XXX` format for traceability
- Checkpoint cadence: After every 5 tasks + end of milestone
- QA tasks inserted after each implementation task
- Templates created in parallel (DOC-001, DOC-002, DOC-003)

## Roadmap Item Registry

| Extraction ID | Phase Bucket | Original Text (≤ 20 words) |
|---------------|--------------|---------------------------|
| DOC-001 | M2 | Create feature-release.md starter template |
| DOC-002 | M2 | Create quality-release.md starter template |
| DOC-003 | M2 | Create documentation-release.md starter template |
| REQ-006 | M2 | Template evaluation (Phase 2.5) |
| REQ-007 | M2 | Template scorer agent with scoring algorithm |

## Deliverable Registry

| Deliverable ID | Task ID | Extraction ID(s) | Deliverable (short) | Intended Artifact Paths | Effort | Risk |
|----------------|---------|------------------|---------------------|------------------------|--------|------|
| D-M2-001 | T02.01 | DOC-001 | feature-release.md template | `TASKLIST_ROOT/artifacts/M2/D-M2-001/spec.md` | S | Low |
| D-M2-002 | T02.02 | DOC-002 | quality-release.md template | `TASKLIST_ROOT/artifacts/M2/D-M2-002/spec.md` | S | Low |
| D-M2-003 | T02.03 | DOC-003 | documentation-release.md template | `TASKLIST_ROOT/artifacts/M2/D-M2-003/spec.md` | S | Low |
| D-M2-004 | T02.04 | DOC-001,DOC-002,DOC-003 | Template structure verification | `TASKLIST_ROOT/artifacts/M2/D-M2-004/evidence.md` | S | Low |
| D-M2-005 | T02.05 | REQ-007 | Template scorer agent | `TASKLIST_ROOT/artifacts/M2/D-M2-005/spec.md` | M | Medium |
| D-M2-006 | T02.06 | REQ-007 | Scorer algorithm verification | `TASKLIST_ROOT/artifacts/M2/D-M2-006/evidence.md` | S | Medium |
| D-M2-007 | T02.07 | REQ-006 | Phase 2.5 implementation | `TASKLIST_ROOT/artifacts/M2/D-M2-007/spec.md` | M | Medium |
| D-M2-008 | T02.08 | REQ-006 | Template selection verification | `TASKLIST_ROOT/artifacts/M2/D-M2-008/evidence.md` | S | Low |
| D-M2-009 | T02.09 | REQ-006 | Variant creation logic | `TASKLIST_ROOT/artifacts/M2/D-M2-009/spec.md` | M | Medium |
| D-M2-010 | T02.10 | REQ-006 | Variant creation verification | `TASKLIST_ROOT/artifacts/M2/D-M2-010/evidence.md` | S | Low |
| D-M2-011 | T02.11 | DOC-001,DOC-002,DOC-003,REQ-006,REQ-007 | M2 Integration test suite | `TASKLIST_ROOT/artifacts/M2/D-M2-011/evidence.md` | M | Low |

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome |
|-------|------------|----------|-----------------|
| 2 | Template System | T02.01–T02.11 | 3 templates, scorer agent, Phase 2.5 operational |

---

## Phase 2: Template System

Create the three starter templates (feature-release, quality-release, documentation-release) and implement the template evaluation system including the scorer agent and Phase 2.5 logic.

### T02.01 — Create feature-release.md Template

**Extraction ID(s):** DOC-001
**Why:** Feature-release template provides structure for releases focused on new features and enhancements.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-001
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-001/spec.md`

**Deliverables:**
- `.opencode/resources/templates/roadmaps/feature-release.md`

**Steps:**
1. Create template directory `.opencode/resources/templates/roadmaps/`
2. Create feature-release.md with common base sections
3. Add Feature Breakdown section
4. Add API Changes section
5. Add Migration Notes section
6. Add Deprecation Warnings section

**Acceptance Criteria:**
- Template exists at correct path
- Contains all common base sections (Executive Summary, Milestone Structure, etc.)
- Contains all feature-specific sections
- Follows markdown schema conventions

**Validation:**
- Manual check: Template structure matches specification
- Evidence: Template file committed to repository

**Dependencies:** M1 complete
**Rollback:** Delete template file
**Notes:** None

---

### T02.02 — Create quality-release.md Template

**Extraction ID(s):** DOC-002
**Why:** Quality-release template provides structure for releases focused on testing, performance, and security.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-002
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-002/spec.md`

**Deliverables:**
- `.opencode/resources/templates/roadmaps/quality-release.md`

**Steps:**
1. Create quality-release.md with common base sections
2. Add Test Coverage Matrix section
3. Add Performance Benchmarks section
4. Add Security Checklist section
5. Ensure compliance-related placeholders

**Acceptance Criteria:**
- Template exists at correct path
- Contains all common base sections
- Contains all quality-specific sections
- Performance and security sections well-structured

**Validation:**
- Manual check: Template structure matches specification
- Evidence: Template file committed to repository

**Dependencies:** M1 complete
**Rollback:** Delete template file
**Notes:** None

---

### T02.03 — Create documentation-release.md Template

**Extraction ID(s):** DOC-003
**Why:** Documentation-release template provides structure for documentation refactors and reorganizations.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-003
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-003/spec.md`

**Deliverables:**
- `.opencode/resources/templates/roadmaps/documentation-release.md`

**Steps:**
1. Create documentation-release.md with common base sections
2. Add Content Structure section
3. Add Migration Guide section
4. Add Cross-references section
5. Add Version History section

**Acceptance Criteria:**
- Template exists at correct path
- Contains all common base sections
- Contains all documentation-specific sections
- Cross-reference structure well-defined

**Validation:**
- Manual check: Template structure matches specification
- Evidence: Template file committed to repository

**Dependencies:** M1 complete
**Rollback:** Delete template file
**Notes:** None

---

### T02.04 — QA: Verify Template Structure

**Extraction ID(s):** DOC-001, DOC-002, DOC-003
**Why:** Ensure all three templates have consistent base structure and correct domain-specific sections.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-004
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-004/evidence.md`

**Deliverables:**
- Template structure verification results

**Steps:**
1. Verify all 3 templates exist at correct paths
2. Compare common sections across all templates
3. Verify feature-release has feature-specific sections
4. Verify quality-release has quality-specific sections
5. Verify documentation-release has docs-specific sections
6. Document any inconsistencies

**Acceptance Criteria:**
- All 3 templates in correct directory
- Common sections identical across templates
- Domain-specific sections present and distinct
- No structural inconsistencies

**Validation:**
- Manual check: Side-by-side comparison
- Evidence: Comparison checklist in evidence.md

**Dependencies:** T02.01, T02.02, T02.03
**Rollback:** N/A (verification task)
**Notes:** None

---

### T02.05 — Create Template Scorer Agent

**Extraction ID(s):** REQ-007
**Why:** Scorer agent evaluates templates against extraction content to select the best match.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** Scoring algorithm complexity
**Deliverable IDs:** D-M2-005
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-005/spec.md`
- `TASKLIST_ROOT/artifacts/M2/D-M2-005/notes.md`

**Deliverables:**
- `.opencode/agent/rf-roadmap-gen-template-scorer.md`

**Steps:**
1. Create `.opencode/agent/rf-roadmap-gen-template-scorer.md`
2. Define agent metadata: model (claude-sonnet-4-5), temperature (0.1)
3. Define input contract (extraction_content, persona, templates_path)
4. Define output contract (scores array, selected_template, action)
5. Implement scoring algorithm using Sequential Thinking MCP
6. Define 80% threshold for direct use vs variant creation

**Acceptance Criteria:**
- Agent file exists at correct path
- Input/output contracts clearly defined
- Scoring algorithm documented
- 80% threshold logic implemented

**Validation:**
- Manual check: Agent invocable with mock input
- Evidence: Agent definition committed to repository

**Dependencies:** T02.04
**Rollback:** Delete agent file
**Notes:** Use CoT for algorithm design per spec

---

### Checkpoint: Phase 2 / Tasks 01-05

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M2/CP-P02-T01-T05.md`

**Purpose:** Verify templates created and scorer agent defined before testing.

**Verification:**
- All 3 starter templates exist with correct structure
- Template scorer agent defined with input/output contracts
- No blocking issues identified

**Exit Criteria:**
- T02.01 through T02.05 marked complete
- Templates verified (T02.04)
- Ready for scorer testing

---

### T02.06 — QA: Verify Scorer Algorithm

**Extraction ID(s):** REQ-007
**Why:** Ensure scorer produces consistent, accurate results across different extraction inputs.
**Effort:** S
**Risk:** Medium
**Risk Drivers:** Algorithm consistency
**Deliverable IDs:** D-M2-006
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-006/evidence.md`

**Deliverables:**
- Scorer algorithm verification results

**Steps:**
1. Test with feature-heavy extraction (expect feature-release highest)
2. Test with quality-heavy extraction (expect quality-release highest)
3. Test with docs-heavy extraction (expect documentation-release highest)
4. Test with mixed extraction (expect reasonable ranking)
5. Verify score consistency on repeated runs
6. Document results

**Acceptance Criteria:**
- Domain-matched templates rank highest
- Scores are deterministic (same input = same output)
- Score differences are meaningful (not tied)
- Edge cases handled gracefully

**Validation:**
- Manual check: Execute 4 test scenarios
- Evidence: Scoring results in evidence.md

**Dependencies:** T02.05
**Rollback:** N/A (verification task)
**Notes:** None

---

### T02.07 — Implement Phase 2.5: Template Evaluation

**Extraction ID(s):** REQ-006
**Why:** Phase 2.5 orchestrates template evaluation, selection, and variant creation.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** Integration complexity
**Deliverable IDs:** D-M2-007
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-007/spec.md`
- `TASKLIST_ROOT/artifacts/M2/D-M2-007/notes.md`

**Deliverables:**
- Phase 2.5 implementation in orchestrator

**Steps:**
1. Add Phase 2.5 section to orchestrator after Phase 2
2. Implement template loading from `.opencode/resources/templates/roadmaps/`
3. Invoke template scorer agent with extraction and persona
4. Implement ≥80% selection logic (direct use)
5. Implement <80% logic (create variant)
6. Generate template-selection.md with rationale

**Acceptance Criteria:**
- Phase 2.5 executes after Phase 2
- Templates loaded from correct directory
- Scorer agent invoked correctly
- Selection/variant logic follows 80% threshold

**Validation:**
- Manual check: Test with different extraction inputs
- Evidence: template-selection.md samples

**Dependencies:** T02.05
**Rollback:** Revert Phase 2.5 section in orchestrator
**Notes:** None

---

### T02.08 — QA: Verify Template Selection

**Extraction ID(s):** REQ-006
**Why:** Ensure Phase 2.5 correctly selects templates based on scorer results.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-008
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-008/evidence.md`

**Deliverables:**
- Template selection verification results

**Steps:**
1. Test with input that should score ≥80% on feature-release
2. Verify feature-release selected (not variant)
3. Test with input that should score ≥80% on quality-release
4. Verify quality-release selected
5. Verify template-selection.md generated with rationale
6. Document results

**Acceptance Criteria:**
- High-scoring templates directly selected
- template-selection.md explains selection rationale
- Correct template used for Phase 3

**Validation:**
- Manual check: Execute 2 test scenarios
- Evidence: template-selection.md samples in evidence.md

**Dependencies:** T02.07
**Rollback:** N/A (verification task)
**Notes:** None

---

### T02.09 — Implement Variant Creation Logic

**Extraction ID(s):** REQ-006
**Why:** When no template scores ≥80%, a variant must be created from the best available template.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** Variant generation complexity
**Deliverable IDs:** D-M2-009
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-009/spec.md`
- `TASKLIST_ROOT/artifacts/M2/D-M2-009/notes.md`

**Deliverables:**
- Variant creation logic in Phase 2.5

**Steps:**
1. Identify highest-scoring template as base
2. Identify gaps between template and extraction needs
3. Implement section activation/deactivation logic
4. Save variant to `.opencode/resources/templates/roadmaps/variants/`
5. Log creation rationale
6. Use variant for Phase 3

**Acceptance Criteria:**
- Variant created from highest-scoring base
- Gaps addressed through section modifications
- Variant saved to variants/ directory
- Creation rationale logged

**Validation:**
- Manual check: Test with low-scoring input
- Evidence: Variant file and rationale

**Dependencies:** T02.07
**Rollback:** Revert variant creation logic
**Notes:** None

---

### T02.10 — QA: Verify Variant Creation

**Extraction ID(s):** REQ-006
**Why:** Ensure variant creation produces valid, usable templates when no direct match exists.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-010
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-010/evidence.md`

**Deliverables:**
- Variant creation verification results

**Steps:**
1. Test with input that scores <80% on all templates
2. Verify variant created from highest-scoring template
3. Verify variant saved to variants/ directory
4. Verify variant is structurally valid
5. Verify creation rationale logged
6. Document results

**Acceptance Criteria:**
- Variant created when all templates <80%
- Variant structurally valid (can be used by Phase 3)
- variants/ directory contains new file
- Rationale explains modifications

**Validation:**
- Manual check: Execute low-score scenario
- Evidence: Variant file and rationale in evidence.md

**Dependencies:** T02.09
**Rollback:** N/A (verification task)
**Notes:** None

---

### Checkpoint: Phase 2 / Tasks 06-10

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M2/CP-P02-T06-T10.md`

**Purpose:** Verify scorer and Phase 2.5 work correctly before integration testing.

**Verification:**
- Scorer algorithm produces accurate rankings
- Template selection works for ≥80% matches
- Variant creation works for <80% matches

**Exit Criteria:**
- T02.06 through T02.10 marked complete
- All QA tasks passed
- Ready for integration testing

---

### T02.11 — M2 Integration Test Suite

**Extraction ID(s):** DOC-001, DOC-002, DOC-003, REQ-006, REQ-007
**Why:** End-to-end integration test validates template system works with Phases 0-2.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M2-011
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M2/D-M2-011/evidence.md`

**Deliverables:**
- M2 integration test results

**Steps:**
1. **IT-M2-01**: Test template selection ≥80% match → direct template use
2. **IT-M2-02**: Test template selection <80% match → variant created
3. **IT-M2-03**: Test feature-heavy spec → feature-release.md selected
4. **IT-M2-04**: Test quality-heavy spec → quality-release.md selected
5. **IT-M2-05**: Test docs-heavy spec → documentation-release.md selected
6. Verify template-selection.md generated with correct rationale
7. Verify Phase 3 can consume selected template output
8. Document all test results with evidence

**Acceptance Criteria:**
- [ ] IT-M2-01: ≥80% match uses direct template
- [ ] IT-M2-02: <80% match creates variant
- [ ] IT-M2-03: Feature-heavy spec selects feature-release.md
- [ ] IT-M2-04: Quality-heavy spec selects quality-release.md
- [ ] IT-M2-05: Docs-heavy spec selects documentation-release.md
- [ ] Full pipeline executes without errors
- [ ] Phase 3 ready to consume template output

**Validation:**
- Execute all 5 integration tests (IT-M2-01 through IT-M2-05)
- Evidence: Complete test log in evidence.md

**Dependencies:** T02.01 through T02.10
**Rollback:** N/A (verification task)
**Notes:** Final gate before M3

---

### Checkpoint: End of Phase 2

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M2/CP-P02-END.md`

**Purpose:** Final verification that M2 Template System is complete and ready for M3.

**Verification:**
- All 11 tasks completed successfully
- 3 templates created and verified
- Scorer agent and Phase 2.5 operational

**Exit Criteria:**
- All deliverables code-complete
- All QA tasks passed
- Integration test suite passed
- Ready to proceed to M3: Core Generation Pipeline

---

## Traceability Matrix

| Extraction ID | Task ID(s) | Deliverable ID(s) | Artifact Paths (rooted) |
|---------------|------------|-------------------|-------------------------|
| DOC-001 | T02.01 | D-M2-001 | `TASKLIST_ROOT/artifacts/M2/D-M2-001/` |
| DOC-002 | T02.02 | D-M2-002 | `TASKLIST_ROOT/artifacts/M2/D-M2-002/` |
| DOC-003 | T02.03 | D-M2-003 | `TASKLIST_ROOT/artifacts/M2/D-M2-003/` |
| DOC-001,DOC-002,DOC-003 | T02.04 | D-M2-004 | `TASKLIST_ROOT/artifacts/M2/D-M2-004/` |
| REQ-007 | T02.05, T02.06 | D-M2-005, D-M2-006 | `TASKLIST_ROOT/artifacts/M2/D-M2-005/`, `TASKLIST_ROOT/artifacts/M2/D-M2-006/` |
| REQ-006 | T02.07, T02.08, T02.09, T02.10 | D-M2-007, D-M2-008, D-M2-009, D-M2-010 | `TASKLIST_ROOT/artifacts/M2/D-M2-007/` through `D-M2-010/` |
| DOC-001,DOC-002,DOC-003,REQ-006,REQ-007 | T02.11 | D-M2-011 | `TASKLIST_ROOT/artifacts/M2/D-M2-011/` |

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/M2-execution-log.md`

| Timestamp (ISO 8601) | Task ID | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run | Result | Evidence Path |
|---------------------|---------|-------------------|--------------------------|----------------|--------|---------------|
| | T02.01 | D-M2-001 | | Manual | TBD | |
| | ... | ... | | ... | ... | |

---

*Generated by Tasklist-Generator v2.1*
