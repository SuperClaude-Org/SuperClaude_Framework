# TASKLIST — M3: Core Generation Pipeline

## Metadata & Artifact Paths
- **TASKLIST_ROOT**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/tasklists/`
- **Tasklist Path**: `TASKLIST_ROOT/M3-core-generation.md`
- **Execution Log Path**: `TASKLIST_ROOT/M3-execution-log.md`
- **Checkpoint Reports Path**: `TASKLIST_ROOT/checkpoints/M3/`
- **Evidence Root**: `TASKLIST_ROOT/evidence/M3/`
- **Artifacts Root**: `TASKLIST_ROOT/artifacts/M3/`

## Source Snapshot
- Milestone 3: Core Generation Pipeline from v3.0-roadmap-gen roadmap
- 4 deliverables: REQ-008, REQ-009, REQ-010, REQ-011
- Objective: Implement core artifact generation phases (3, 4, 5, 6)
- Dependencies: M2 (Template system complete)
- Estimated Complexity: Medium
- Risk Level: Medium

## Deterministic Rules Applied
- Task IDs: `T03.XX` format (Phase 3, sequential tasks)
- Deliverable IDs: `D-M3-XXX` format for traceability
- Checkpoint cadence: After every 5 tasks + end of milestone
- QA tasks inserted after each implementation task
- Traceability verification mandatory for Phase 6

## Roadmap Item Registry

| Extraction ID | Phase Bucket | Original Text (≤ 20 words) |
|---------------|--------------|---------------------------|
| REQ-008 | M3 | Roadmap construction (Phase 3) |
| REQ-009 | M3 | Test strategy generation (Phase 4) |
| REQ-010 | M3 | Execution prompt generation (Phase 5) |
| REQ-011 | M3 | Self-validation (Phase 6) |

## Deliverable Registry

| Deliverable ID | Task ID | Extraction ID(s) | Deliverable (short) | Intended Artifact Paths | Effort | Risk |
|----------------|---------|------------------|---------------------|------------------------|--------|------|
| D-M3-001 | T03.01 | REQ-008 | Phase 3 milestone formation | `TASKLIST_ROOT/artifacts/M3/D-M3-001/spec.md` | M | Low |
| D-M3-002 | T03.02 | REQ-008 | Phase 3 traceability | `TASKLIST_ROOT/artifacts/M3/D-M3-002/spec.md` | S | Low |
| D-M3-003 | T03.03 | REQ-008 | Phase 3 verification | `TASKLIST_ROOT/artifacts/M3/D-M3-003/evidence.md` | S | Low |
| D-M3-004 | T03.04 | REQ-009 | Phase 4 test matrix | `TASKLIST_ROOT/artifacts/M3/D-M3-004/spec.md` | M | Low |
| D-M3-005 | T03.05 | REQ-009 | Phase 4 verification | `TASKLIST_ROOT/artifacts/M3/D-M3-005/evidence.md` | S | Low |
| D-M3-006 | T03.06 | REQ-010 | Phase 5 execution rules | `TASKLIST_ROOT/artifacts/M3/D-M3-006/spec.md` | M | Low |
| D-M3-007 | T03.07 | REQ-010 | Phase 5 verification | `TASKLIST_ROOT/artifacts/M3/D-M3-007/evidence.md` | S | Low |
| D-M3-008 | T03.08 | REQ-011 | Phase 6 traceability checks | `TASKLIST_ROOT/artifacts/M3/D-M3-008/spec.md` | M | Medium |
| D-M3-009 | T03.09 | REQ-011 | Phase 6 verification | `TASKLIST_ROOT/artifacts/M3/D-M3-009/evidence.md` | S | Low |
| D-M3-010 | T03.10 | REQ-008,REQ-009,REQ-010,REQ-011 | M3 Integration test suite | `TASKLIST_ROOT/artifacts/M3/D-M3-010/evidence.md` | M | Low |

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome |
|-------|------------|----------|-----------------|
| 3 | Core Generation Pipeline | T03.01–T03.10 | Phases 3-6 operational, all artifacts generated |

---

## Phase 3: Core Generation Pipeline

Implement the core artifact generation phases: roadmap construction (Phase 3), test strategy (Phase 4), execution prompt (Phase 5), and self-validation (Phase 6).

### T03.01 — Implement Phase 3: Roadmap Milestone Formation

**Extraction ID(s):** REQ-008
**Why:** Phase 3 transforms extracted items into dependency-ordered milestones using the selected template.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-001
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-001/spec.md`
- `TASKLIST_ROOT/artifacts/M3/D-M3-001/notes.md`

**Deliverables:**
- Phase 3 milestone formation logic in orchestrator

**Steps:**
1. Load selected template from Phase 2.5
2. Implement milestone formation rules (dependency-first, natural grouping)
3. Implement risk stratification (high-risk earlier)
4. Enforce max 7 deliverables per milestone size limit
5. Implement standard progression pattern (M1: Foundation, M2-N-2: Features, etc.)
6. Generate milestone overview table

**Acceptance Criteria:**
- Milestones follow dependency order
- Max 7 deliverables per milestone enforced
- Standard progression pattern applied
- Milestone overview table complete

**Validation:**
- Manual check: Run on test fixture, verify milestone structure
- Evidence: Sample roadmap.md milestones

**Dependencies:** M2 complete
**Rollback:** Revert Phase 3 section in orchestrator
**Notes:** None

---

### T03.02 — Implement Phase 3: Roadmap Traceability

**Extraction ID(s):** REQ-008
**Why:** Every extraction item must appear exactly once in roadmap milestones for traceability.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-002
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-002/spec.md`

**Deliverables:**
- Traceability logic ensuring all items mapped

**Steps:**
1. Implement extraction item tracking
2. Ensure each item assigned to exactly one milestone
3. Implement acceptance criteria generation per deliverable
4. Generate dependency graph section
5. Generate risk register section

**Acceptance Criteria:**
- All extraction items appear exactly once
- No orphaned items (in extraction but not roadmap)
- No duplicate items (in multiple milestones)
- Dependency graph accurately reflects relationships

**Validation:**
- Manual check: Compare extraction.md to roadmap.md
- Evidence: Traceability comparison in evidence.md

**Dependencies:** T03.01
**Rollback:** Revert traceability logic
**Notes:** None

---

### T03.03 — QA: Verify Phase 3 Output

**Extraction ID(s):** REQ-008
**Why:** Ensure roadmap.md follows required schema and contains all necessary sections.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-003
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-003/evidence.md`

**Deliverables:**
- Phase 3 output verification results

**Steps:**
1. Verify roadmap.md has all required sections (Metadata, Summary, Milestones, etc.)
2. Verify milestone overview table complete
3. Verify each milestone has deliverables table
4. Verify verification checkpoints present per milestone
5. Verify dependency graph section present
6. Verify risk register section present
7. Document any schema violations

**Acceptance Criteria:**
- All required schema sections present
- Milestones correctly formatted
- Verification checkpoints included
- No schema violations

**Validation:**
- Manual check: Schema compliance checklist
- Evidence: Verification results in evidence.md

**Dependencies:** T03.02
**Rollback:** N/A (verification task)
**Notes:** None

---

### T03.04 — Implement Phase 4: Test Strategy Generation

**Extraction ID(s):** REQ-009
**Why:** Phase 4 creates test coverage matrix mapping each deliverable to test types.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-004
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-004/spec.md`
- `TASKLIST_ROOT/artifacts/M3/D-M3-004/notes.md`

**Deliverables:**
- Phase 4 implementation producing test-strategy.md

**Steps:**
1. Define test categories (unit, integration, regression, acceptance)
2. Implement test matrix generation (deliverable × test type)
3. Generate test execution order section
4. Generate coverage targets section
5. Generate test constraints section (no writes outside .dev)
6. Map each deliverable to appropriate test types

**Acceptance Criteria:**
- All 4 test categories defined
- Test matrix covers all deliverables
- Execution order specified
- Coverage targets defined (80% unit, 100% critical paths)

**Validation:**
- Manual check: Test-strategy.md completeness
- Evidence: Sample test-strategy.md

**Dependencies:** T03.03
**Rollback:** Revert Phase 4 section in orchestrator
**Notes:** None

---

### T03.05 — QA: Verify Phase 4 Output

**Extraction ID(s):** REQ-009
**Why:** Ensure test-strategy.md covers all deliverables and follows required schema.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-005
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-005/evidence.md`

**Deliverables:**
- Phase 4 output verification results

**Steps:**
1. Verify all deliverables from roadmap.md appear in test matrix
2. Verify test categories correctly assigned
3. Verify execution order logical (unit → integration → acceptance → regression)
4. Verify coverage targets present
5. Verify test constraints documented
6. Document any gaps

**Acceptance Criteria:**
- All deliverables have test coverage
- Test categories appropriately assigned
- No missing deliverables in matrix
- Schema compliance verified

**Validation:**
- Manual check: Cross-reference roadmap.md and test-strategy.md
- Evidence: Coverage verification in evidence.md

**Dependencies:** T03.04
**Rollback:** N/A (verification task)
**Notes:** None

---

### Checkpoint: Phase 3 / Tasks 01-05

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M3/CP-P03-T01-T05.md`

**Purpose:** Verify Phases 3 and 4 produce correct output before Phase 5.

**Verification:**
- roadmap.md follows required schema
- All extraction items traced to milestones
- test-strategy.md covers all deliverables

**Exit Criteria:**
- T03.01 through T03.05 marked complete
- All QA tasks (T03.03, T03.05) passed
- Ready for Phase 5 implementation

---

### T03.06 — Implement Phase 5: Execution Prompt Generation

**Extraction ID(s):** REQ-010
**Why:** Phase 5 creates execution-prompt.md with context, rules, and checkpoints for implementation.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-006
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-006/spec.md`
- `TASKLIST_ROOT/artifacts/M3/D-M3-006/notes.md`

**Deliverables:**
- Phase 5 implementation producing execution-prompt.md

**Steps:**
1. Generate context loading section with artifact paths
2. Generate execution rules section (milestone order, dependencies)
3. Generate task execution pattern section (READ, PLAN, IMPLEMENT, TEST, VERIFY, DOCUMENT, COMMIT)
4. Generate verification checkpoints section
5. Generate stop conditions section
6. Generate rollback procedure section

**Acceptance Criteria:**
- Context loading references correct artifact paths
- Execution rules clearly defined
- Task pattern complete (7 steps)
- Stop conditions and rollback documented

**Validation:**
- Manual check: execution-prompt.md completeness
- Evidence: Sample execution-prompt.md

**Dependencies:** T03.05
**Rollback:** Revert Phase 5 section in orchestrator
**Notes:** None

---

### T03.07 — QA: Verify Phase 5 Output

**Extraction ID(s):** REQ-010
**Why:** Ensure execution-prompt.md has valid paths and complete execution guidance.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-007
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-007/evidence.md`

**Deliverables:**
- Phase 5 output verification results

**Steps:**
1. Verify all artifact paths in context section are valid
2. Verify execution rules cover milestone ordering
3. Verify task pattern has all 7 steps
4. Verify checkpoints align with roadmap milestones
5. Verify stop conditions comprehensive
6. Document any issues

**Acceptance Criteria:**
- All paths valid and resolvable
- Execution rules complete
- Checkpoints match roadmap structure
- No missing sections

**Validation:**
- Manual check: Path validation and section completeness
- Evidence: Verification results in evidence.md

**Dependencies:** T03.06
**Rollback:** N/A (verification task)
**Notes:** None

---

### T03.08 — Implement Phase 6: Self-Validation

**Extraction ID(s):** REQ-011
**Why:** Phase 6 verifies artifact completeness, traceability, and cross-reference integrity.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** Validation complexity
**Deliverable IDs:** D-M3-008
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-008/spec.md`
- `TASKLIST_ROOT/artifacts/M3/D-M3-008/notes.md`

**Deliverables:**
- Phase 6 self-validation implementation

**Steps:**
1. Implement artifact completeness check (all 4 files exist)
2. Implement traceability check (extraction items ↔ roadmap)
3. Implement schema compliance check per artifact
4. Implement cross-reference integrity check (paths, IDs)
5. Generate validation report
6. Implement STOP on critical validation failures

**Acceptance Criteria:**
- All 4 artifacts verified for existence
- Traceability verified (no orphans, no duplicates)
- Schema compliance verified per artifact
- Cross-references valid

**Validation:**
- Manual check: Introduce intentional errors, verify detection
- Evidence: Validation report samples

**Dependencies:** T03.07
**Rollback:** Revert Phase 6 section in orchestrator
**Notes:** Critical gate before Phase 7

---

### T03.09 — QA: Verify Phase 6 Detection

**Extraction ID(s):** REQ-011
**Why:** Ensure Phase 6 correctly detects and reports various validation failures.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-009
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-009/evidence.md`

**Deliverables:**
- Phase 6 detection verification results

**Steps:**
1. Test with missing artifact (should fail)
2. Test with orphaned extraction item (should fail)
3. Test with invalid cross-reference (should fail)
4. Test with valid artifacts (should pass)
5. **IT-M3-05**: Test self-validation failure path triggers STOP
6. Verify failure messages are actionable
7. Document all test results

**Acceptance Criteria:**
- Missing artifacts detected
- Traceability violations detected
- Invalid cross-references detected
- Valid artifacts pass without false positives
- IT-M3-05: Self-validation failure correctly halts pipeline

**Validation:**
- Manual check: Execute 4 test scenarios
- Evidence: Detection results in evidence.md

**Dependencies:** T03.08
**Rollback:** N/A (verification task)
**Notes:** None

---

### T03.10 — M3 Integration Test Suite

**Extraction ID(s):** REQ-008, REQ-009, REQ-010, REQ-011
**Why:** End-to-end integration test validates Phases 3-6 work together correctly.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M3-010
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M3/D-M3-010/evidence.md`

**Deliverables:**
- M3 integration test results

**Steps:**
1. Run full pipeline through Phases 0-6
2. Verify roadmap.md generated with correct structure
3. Verify test-strategy.md covers all deliverables
4. Verify execution-prompt.md has valid paths
5. Verify Phase 6 self-validation passes
6. Verify all artifacts traceable to extraction
7. Document all results

**Acceptance Criteria:**
- Full pipeline executes without errors
- All 4 artifacts generated correctly
- Phase 6 validation passes
- Ready for Phase 7 crossLLM integration

**Validation:**
- Manual check: Execute full integration test
- Evidence: Complete test log in evidence.md

**Dependencies:** T03.01 through T03.09
**Rollback:** N/A (verification task)
**Notes:** Final gate before M4

---

### Checkpoint: End of Phase 3

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M3/CP-P03-END.md`

**Purpose:** Final verification that M3 Core Generation Pipeline is complete and ready for M4.

**Verification:**
- All 10 tasks completed successfully
- Phases 3, 4, 5, 6 operational
- Integration test suite passed

**Exit Criteria:**
- All deliverables code-complete
- All QA tasks passed
- Integration test suite passed
- Ready to proceed to M4: crossLLM Integration

---

## Traceability Matrix

| Extraction ID | Task ID(s) | Deliverable ID(s) | Artifact Paths (rooted) |
|---------------|------------|-------------------|-------------------------|
| REQ-008 | T03.01, T03.02, T03.03 | D-M3-001, D-M3-002, D-M3-003 | `TASKLIST_ROOT/artifacts/M3/D-M3-001/` through `D-M3-003/` |
| REQ-009 | T03.04, T03.05 | D-M3-004, D-M3-005 | `TASKLIST_ROOT/artifacts/M3/D-M3-004/`, `D-M3-005/` |
| REQ-010 | T03.06, T03.07 | D-M3-006, D-M3-007 | `TASKLIST_ROOT/artifacts/M3/D-M3-006/`, `D-M3-007/` |
| REQ-011 | T03.08, T03.09 | D-M3-008, D-M3-009 | `TASKLIST_ROOT/artifacts/M3/D-M3-008/`, `D-M3-009/` |
| REQ-008,REQ-009,REQ-010,REQ-011 | T03.10 | D-M3-010 | `TASKLIST_ROOT/artifacts/M3/D-M3-010/` |

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/M3-execution-log.md`

| Timestamp (ISO 8601) | Task ID | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run | Result | Evidence Path |
|---------------------|---------|-------------------|--------------------------|----------------|--------|---------------|
| | T03.01 | D-M3-001 | | Manual | TBD | |
| | ... | ... | | ... | ... | |

---

*Generated by Tasklist-Generator v2.1*
