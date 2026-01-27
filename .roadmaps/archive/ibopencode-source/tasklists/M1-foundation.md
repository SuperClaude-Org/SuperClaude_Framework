# TASKLIST — M1: Foundation

## Metadata & Artifact Paths
- **TASKLIST_ROOT**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/tasklists/`
- **Tasklist Path**: `TASKLIST_ROOT/M1-foundation.md`
- **Execution Log Path**: `TASKLIST_ROOT/M1-execution-log.md`
- **Checkpoint Reports Path**: `TASKLIST_ROOT/checkpoints/M1/`
- **Evidence Root**: `TASKLIST_ROOT/evidence/M1/`
- **Artifacts Root**: `TASKLIST_ROOT/artifacts/M1/`

## Source Snapshot
- Milestone 1: Foundation from v3.0-roadmap-gen roadmap
- 6 deliverables: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, IMP-005
- Objective: Establish command infrastructure and core pipeline skeleton
- Dependencies: None (first milestone)
- Estimated Complexity: Low
- Risk Level: Low

## Deterministic Rules Applied
- Task IDs: `T01.XX` format (Phase 1, sequential tasks)
- Deliverable IDs: `D-M1-XXX` format for traceability
- Checkpoint cadence: After every 5 tasks + end of milestone
- QA tasks inserted after each implementation task
- Effort mapping: XS/S/M/L/XL based on keyword analysis
- Risk mapping: Low/Medium/High based on security/data/auth keywords

## Roadmap Item Registry

| Extraction ID | Phase Bucket | Original Text (≤ 20 words) |
|---------------|--------------|---------------------------|
| REQ-001 | M1 | Command definition file `/rf:roadmap-gen` with full syntax, options parsing, and routing |
| REQ-002 | M1 | Orchestrator agent skeleton with 9-phase pipeline structure |
| REQ-003 | M1 | Preflight validation (Phase 0) |
| REQ-004 | M1 | Input extraction (Phase 1) |
| REQ-005 | M1 | Persona selection (Phase 2) |
| IMP-005 | M1 | --output flag for custom output directory |

## Deliverable Registry

| Deliverable ID | Task ID | Extraction ID(s) | Deliverable (short) | Intended Artifact Paths | Effort | Risk |
|----------------|---------|------------------|---------------------|------------------------|--------|------|
| D-M1-001 | T01.01 | REQ-001 | Command definition file | `TASKLIST_ROOT/artifacts/M1/D-M1-001/spec.md` | S | Low |
| D-M1-002 | T01.02 | REQ-001 | Command syntax validation | `TASKLIST_ROOT/artifacts/M1/D-M1-002/evidence.md` | XS | Low |
| D-M1-003 | T01.03 | REQ-002 | Orchestrator agent skeleton | `TASKLIST_ROOT/artifacts/M1/D-M1-003/spec.md` | M | Low |
| D-M1-004 | T01.04 | REQ-002 | Phase structure verification | `TASKLIST_ROOT/artifacts/M1/D-M1-004/evidence.md` | XS | Low |
| D-M1-005 | T01.05 | REQ-003 | Phase 0 preflight validation | `TASKLIST_ROOT/artifacts/M1/D-M1-005/spec.md` | S | Low |
| D-M1-006 | T01.06 | REQ-003 | Preflight error handling tests | `TASKLIST_ROOT/artifacts/M1/D-M1-006/evidence.md` | S | Low |
| D-M1-007 | T01.07 | REQ-004 | Phase 1 extraction logic | `TASKLIST_ROOT/artifacts/M1/D-M1-007/spec.md` | M | Low |
| D-M1-008 | T01.08 | REQ-004 | Extraction output verification | `TASKLIST_ROOT/artifacts/M1/D-M1-008/evidence.md` | S | Low |
| D-M1-009 | T01.09 | REQ-005 | Phase 2 persona selection | `TASKLIST_ROOT/artifacts/M1/D-M1-009/spec.md` | S | Low |
| D-M1-010 | T01.10 | REQ-005 | Persona calculation tests | `TASKLIST_ROOT/artifacts/M1/D-M1-010/evidence.md` | S | Low |
| D-M1-011 | T01.11 | IMP-005 | --output flag implementation | `TASKLIST_ROOT/artifacts/M1/D-M1-011/spec.md` | XS | Low |
| D-M1-012 | T01.12 | IMP-005 | Output directory verification | `TASKLIST_ROOT/artifacts/M1/D-M1-012/evidence.md` | XS | Low |
| D-M1-013 | T01.13 | REQ-001,REQ-002,REQ-003,REQ-004,REQ-005,IMP-005 | M1 Integration test suite | `TASKLIST_ROOT/artifacts/M1/D-M1-013/evidence.md` | M | Low |

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome |
|-------|------------|----------|-----------------|
| 1 | Foundation | T01.01–T01.13 | Command infrastructure and Phases 0-2 operational |

---

## Phase 1: Foundation

Establish the command infrastructure including the command definition file, orchestrator skeleton, and core pipeline phases 0-2. This foundation enables all subsequent milestone work.

### T01.01 — Create Command Definition File

**Extraction ID(s):** REQ-001
**Why:** Command definition is the entry point for `/rf:roadmap-gen`; all invocations route through this file.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-001
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-001/spec.md`
- `TASKLIST_ROOT/artifacts/M1/D-M1-001/notes.md`

**Deliverables:**
- `.opencode/command/rf:roadmap-gen.md` with full syntax specification

**Steps:**
1. Create `.opencode/command/rf:roadmap-gen.md` file
2. Define command syntax: `/rf:roadmap-gen <input_spec_path> [options]`
3. Document all options: --chain, --no-upgrade, --upgrade-only, --upgrade-threshold, --version, --parallel-upgrades, --sequential-upgrades, --output
4. Add routing directive to invoke `@rf-roadmap-gen-orchestrator`
5. Add validation section for invalid argument handling

**Acceptance Criteria:**
- Command file exists at `.opencode/command/rf:roadmap-gen.md`
- All 8 options documented with types and defaults
- Routing correctly points to orchestrator agent
- Syntax errors produce clear error messages

**Validation:**
- Manual check: File exists and follows OpenCode command schema
- Evidence: Command definition file committed to repository

**Dependencies:** None
**Rollback:** Delete `.opencode/command/rf:roadmap-gen.md`
**Notes:** None

---

### T01.02 — QA: Verify Command Syntax Parsing

**Extraction ID(s):** REQ-001
**Why:** Ensure command definition correctly parses all option combinations before building dependent components.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-002
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-002/evidence.md`

**Deliverables:**
- Syntax parsing test results documented

**Steps:**
1. Test valid invocation: `/rf:roadmap-gen ./spec.md`
2. Test with --output flag: `/rf:roadmap-gen ./spec.md --output mydir`
3. Test with --chain flag: `/rf:roadmap-gen ./spec.md --chain gpt>claude`
4. Test invalid syntax produces error
5. Document all test results

**Acceptance Criteria:**
- All valid syntax combinations accepted
- Invalid syntax produces actionable error message
- No unhandled exceptions on malformed input
- Evidence documented in artifacts folder

**Validation:**
- Manual check: Execute 4 test cases and verify expected behavior
- Evidence: Test results logged in evidence.md

**Dependencies:** T01.01
**Rollback:** N/A (verification task)
**Notes:** None

---

### T01.03 — Create Orchestrator Agent Skeleton

**Extraction ID(s):** REQ-002
**Why:** Orchestrator coordinates all 9 pipeline phases; skeleton establishes structure for incremental implementation.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-003
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-003/spec.md`
- `TASKLIST_ROOT/artifacts/M1/D-M1-003/notes.md`

**Deliverables:**
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` with 9-phase structure

**Steps:**
1. Create `.opencode/agent/rf-roadmap-gen-orchestrator.md`
2. Define agent metadata: model (gpt-5.2), temperature (0.1), tools
3. Create phase execution outline: Phase 0, 1, 2, 2.5, 3, 4, 5, 6, 7, 7.5
4. Add placeholder sections for each phase
5. Define phase entry/exit logging pattern
6. Add error handling structure

**Acceptance Criteria:**
- Agent file exists at correct path
- All 9 phases (0, 1, 2, 2.5, 3, 4, 5, 6, 7, 7.5) have sections
- Model and temperature configured correctly
- Tools section lists required tools

**Validation:**
- Manual check: Agent can be invoked without errors
- Evidence: Orchestrator skeleton committed to repository

**Dependencies:** T01.01
**Rollback:** Delete `.opencode/agent/rf-roadmap-gen-orchestrator.md`
**Notes:** Phases 2.5 and 7.5 use decimal notation per specification

---

### T01.04 — QA: Verify Phase Structure

**Extraction ID(s):** REQ-002
**Why:** Confirm all 9 phases are correctly defined and callable before implementing phase logic.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-004
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-004/evidence.md`

**Deliverables:**
- Phase structure verification results

**Steps:**
1. Review orchestrator for all 9 phase sections
2. Verify phase ordering is correct (0 → 1 → 2 → 2.5 → 3 → 4 → 5 → 6 → 7 → 7.5)
3. Confirm each phase has entry/exit points
4. Verify error handling structure present
5. Document verification results

**Acceptance Criteria:**
- All 9 phases present in correct order
- No missing phase sections
- Entry/exit logging pattern consistent
- Error handling structure complete

**Validation:**
- Manual check: Count and verify phase sections
- Evidence: Verification checklist in evidence.md

**Dependencies:** T01.03
**Rollback:** N/A (verification task)
**Notes:** None

---

### T01.05 — Implement Phase 0: Preflight Validation

**Extraction ID(s):** REQ-003
**Why:** Preflight validation prevents invalid inputs from propagating through the pipeline.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-005
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-005/spec.md`
- `TASKLIST_ROOT/artifacts/M1/D-M1-005/notes.md`

**Deliverables:**
- Phase 0 implementation in orchestrator with validation checks

**Steps:**
1. Implement input file existence check
2. Implement input file readability check
3. Implement actionable content detection (not empty/placeholder)
4. Implement output directory creation/validation
5. Add clear error messages for each failure mode
6. Implement STOP behavior on validation failure

**Acceptance Criteria:**
- Missing input file produces clear error and STOP
- Empty input file produces clear error and STOP
- Invalid output directory produces clear error and STOP
- Valid inputs pass through to Phase 1

**Validation:**
- Manual check: Test each validation failure mode
- Evidence: Error message screenshots in evidence.md

**Dependencies:** T01.03
**Rollback:** Revert Phase 0 section in orchestrator
**Notes:** None

---

### Checkpoint: Phase 1 / Tasks 01-05

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M1/CP-P01-T01-T05.md`

**Purpose:** Verify foundation components (command, orchestrator, preflight) are operational before proceeding.

**Verification:**
- Command definition file exists and parses all options
- Orchestrator skeleton has all 9 phases defined
- Phase 0 correctly validates inputs and produces clear errors

**Exit Criteria:**
- T01.01 through T01.05 marked complete
- All QA tasks (T01.02, T01.04) passed
- No blocking issues identified

---

### T01.06 — QA: Test Preflight Error Handling

**Extraction ID(s):** REQ-003
**Why:** Ensure preflight validation catches all invalid input scenarios with actionable error messages.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-006
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-006/evidence.md`

**Deliverables:**
- Preflight error handling test results

**Steps:**
1. Test with non-existent input file
2. Test with empty input file
3. Test with placeholder-only input file
4. Test with invalid output directory
5. Test with valid inputs (should pass)
6. Document all error messages

**Acceptance Criteria:**
- Each failure mode produces distinct error message
- Error messages include remediation guidance
- Valid inputs pass through without errors
- No unhandled exceptions

**Validation:**
- Manual check: Execute 5 test scenarios
- Evidence: Error messages documented in evidence.md

**Dependencies:** T01.05
**Rollback:** N/A (verification task)
**Notes:** None

---

### T01.07 — Implement Phase 1: Input Extraction

**Extraction ID(s):** REQ-004
**Why:** Phase 1 extracts all actionable items from the specification and assigns unique IDs for traceability.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-007
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-007/spec.md`
- `TASKLIST_ROOT/artifacts/M1/D-M1-007/notes.md`

**Deliverables:**
- Phase 1 implementation producing extraction.md

**Steps:**
1. Implement input file parsing
2. Implement item detection (headings, bullets, numbered lists)
3. Implement ID assignment scheme (REQ-###, BUG-###, IMP-###, REF-###, DOC-###)
4. Implement type normalization (FEATURE, BUGFIX, IMPROVEMENT, REFACTOR, DOC)
5. Implement domain categorization (FRONTEND, BACKEND, DEVOPS, SECURITY, ARCHITECTURE, DOCS)
6. Implement dependency extraction
7. Implement priority mapping (P0-Critical, P1-High, P2-Medium, P3-Low)
8. Generate extraction.md output

**Acceptance Criteria:**
- All items from input assigned unique IDs
- IDs follow correct prefix scheme by type
- Domain categorization accurate
- extraction.md follows required schema

**Validation:**
- Manual check: Run on test fixture, verify output
- Evidence: Sample extraction.md in evidence folder

**Dependencies:** T01.05
**Rollback:** Revert Phase 1 section in orchestrator
**Notes:** Preserve appearance order for deterministic output

---

### T01.08 — QA: Verify Extraction Output

**Extraction ID(s):** REQ-004
**Why:** Confirm extraction produces correct output format and accurate item categorization.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-008
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-008/evidence.md`

**Deliverables:**
- Extraction output verification results

**Steps:**
1. Run extraction on simple test fixture
2. Verify all items have unique IDs
3. Verify type assignments are correct
4. Verify domain categorizations are accurate
5. Verify extraction.md schema compliance
6. Document any discrepancies

**Acceptance Criteria:**
- All test fixture items extracted
- No duplicate IDs
- Type and domain assignments accurate
- Output follows required table schema

**Validation:**
- Manual check: Compare extraction output to test fixture
- Evidence: Verification checklist in evidence.md

**Dependencies:** T01.07
**Rollback:** N/A (verification task)
**Notes:** None

---

### T01.09 — Implement Phase 2: Persona Selection

**Extraction ID(s):** REQ-005
**Why:** Persona selection determines the primary expertise lens for roadmap construction.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-009
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-009/spec.md`
- `TASKLIST_ROOT/artifacts/M1/D-M1-009/notes.md`

**Deliverables:**
- Phase 2 implementation with persona selection logic

**Steps:**
1. Implement domain distribution calculation from extraction
2. Implement primary persona selection (>40% threshold)
3. Implement consulting persona identification (>15% threshold)
4. Implement fallback to ARCHITECTURE persona when no domain dominant
5. Generate persona rationale documentation
6. Add persona metadata to roadmap header

**Acceptance Criteria:**
- Domain percentages calculated correctly
- Primary persona selected based on >40% threshold
- Consulting personas identified for >15% domains
- ARCHITECTURE fallback works when no dominant domain

**Validation:**
- Manual check: Test with different domain distributions
- Evidence: Persona selection logs in evidence.md

**Dependencies:** T01.07
**Rollback:** Revert Phase 2 section in orchestrator
**Notes:** None

---

### T01.10 — QA: Test Persona Calculation

**Extraction ID(s):** REQ-005
**Why:** Verify persona selection algorithm produces correct results for various domain distributions.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-010
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-010/evidence.md`

**Deliverables:**
- Persona calculation test results

**Steps:**
1. Test with single dominant domain (>40%)
2. Test with no dominant domain (fallback to ARCHITECTURE)
3. Test with multiple consulting personas (>15%)
4. Verify percentage calculations are accurate
5. Document test results

**Acceptance Criteria:**
- Dominant domain correctly identifies primary persona
- No dominant domain correctly falls back to ARCHITECTURE
- Consulting personas correctly identified
- Percentages accurate to 1 decimal place

**Validation:**
- Manual check: Execute 3 test scenarios
- Evidence: Test results documented in evidence.md

**Dependencies:** T01.09
**Rollback:** N/A (verification task)
**Notes:** None

---

### Checkpoint: Phase 1 / Tasks 06-10

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M1/CP-P01-T06-T10.md`

**Purpose:** Verify Phase 1 and Phase 2 implementations are correct before final tasks.

**Verification:**
- Phase 1 extraction produces valid output
- Phase 2 persona selection calculates correctly
- All QA tasks (T01.06, T01.08, T01.10) passed

**Exit Criteria:**
- T01.06 through T01.10 marked complete
- extraction.md output verified
- Persona selection logic verified

---

### T01.11 — Implement --output Flag

**Extraction ID(s):** IMP-005
**Why:** Custom output directory allows users to organize roadmap artifacts in project-specific locations.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-011
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-011/spec.md`

**Deliverables:**
- --output flag implementation in command and orchestrator

**Steps:**
1. Add --output parameter parsing to command definition
2. Pass output directory to orchestrator
3. Implement directory creation in orchestrator
4. Update all artifact paths to use custom directory
5. Document default behavior (derive from input filename)

**Acceptance Criteria:**
- --output flag correctly parsed
- Custom directory created if not exists
- All artifacts written to specified directory
- Default derives directory from input filename

**Validation:**
- Manual check: Test with and without --output flag
- Evidence: Artifact locations documented

**Dependencies:** T01.03
**Rollback:** Remove --output handling
**Notes:** None

---

### T01.12 — QA: Verify Output Directory Handling

**Extraction ID(s):** IMP-005
**Why:** Ensure --output flag correctly creates and uses custom directories.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-012
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-012/evidence.md`

**Deliverables:**
- Output directory verification results

**Steps:**
1. Test without --output (verify default behavior)
2. Test with --output to existing directory
3. Test with --output to non-existent directory (should create)
4. Verify artifacts appear in correct location
5. Document test results

**Acceptance Criteria:**
- Default correctly derives from input filename
- Existing directories used without error
- Non-existent directories created
- All artifacts in correct location

**Validation:**
- Manual check: Execute 3 test scenarios
- Evidence: Directory listings in evidence.md

**Dependencies:** T01.11
**Rollback:** N/A (verification task)
**Notes:** None

---

### T01.13 — M1 Integration Test Suite

**Extraction ID(s):** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, IMP-005
**Why:** End-to-end integration test validates all M1 components work together correctly.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None
**Deliverable IDs:** D-M1-013
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/M1/D-M1-013/evidence.md`

**Deliverables:**
- M1 integration test results

**Steps:**
1. Create integration test fixture
2. Run full command with test fixture
3. Verify command routes to orchestrator
4. Verify Phase 0 validates inputs
5. Verify Phase 1 produces extraction.md
6. Verify Phase 2 selects correct persona
7. Verify --output flag works end-to-end
8. Document all results

**Acceptance Criteria:**
- Full pipeline executes without errors
- All artifacts generated correctly
- Phase logging shows correct execution order
- Integration with custom output directory works

**Validation:**
- Manual check: Execute full integration test
- Evidence: Complete test log in evidence.md

**Dependencies:** T01.01 through T01.12
**Rollback:** N/A (verification task)
**Notes:** Final gate before M2

---

### Checkpoint: End of Phase 1

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/M1/CP-P01-END.md`

**Purpose:** Final verification that M1 Foundation is complete and ready for M2.

**Verification:**
- All 13 tasks completed successfully
- Command definition, orchestrator, and Phases 0-2 operational
- Integration test suite passed

**Exit Criteria:**
- All deliverables code-complete
- All QA tasks passed
- Integration test suite passed
- Ready to proceed to M2: Template System

---

## Traceability Matrix

| Extraction ID | Task ID(s) | Deliverable ID(s) | Artifact Paths (rooted) |
|---------------|------------|-------------------|-------------------------|
| REQ-001 | T01.01, T01.02 | D-M1-001, D-M1-002 | `TASKLIST_ROOT/artifacts/M1/D-M1-001/`, `TASKLIST_ROOT/artifacts/M1/D-M1-002/` |
| REQ-002 | T01.03, T01.04 | D-M1-003, D-M1-004 | `TASKLIST_ROOT/artifacts/M1/D-M1-003/`, `TASKLIST_ROOT/artifacts/M1/D-M1-004/` |
| REQ-003 | T01.05, T01.06 | D-M1-005, D-M1-006 | `TASKLIST_ROOT/artifacts/M1/D-M1-005/`, `TASKLIST_ROOT/artifacts/M1/D-M1-006/` |
| REQ-004 | T01.07, T01.08 | D-M1-007, D-M1-008 | `TASKLIST_ROOT/artifacts/M1/D-M1-007/`, `TASKLIST_ROOT/artifacts/M1/D-M1-008/` |
| REQ-005 | T01.09, T01.10 | D-M1-009, D-M1-010 | `TASKLIST_ROOT/artifacts/M1/D-M1-009/`, `TASKLIST_ROOT/artifacts/M1/D-M1-010/` |
| IMP-005 | T01.11, T01.12 | D-M1-011, D-M1-012 | `TASKLIST_ROOT/artifacts/M1/D-M1-011/`, `TASKLIST_ROOT/artifacts/M1/D-M1-012/` |
| REQ-001,REQ-002,REQ-003,REQ-004,REQ-005,IMP-005 | T01.13 | D-M1-013 | `TASKLIST_ROOT/artifacts/M1/D-M1-013/` |

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/M1-execution-log.md`

| Timestamp (ISO 8601) | Task ID | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run | Result | Evidence Path |
|---------------------|---------|-------------------|--------------------------|----------------|--------|---------------|
| | T01.01 | D-M1-001 | | Manual | TBD | |
| | T01.02 | D-M1-002 | | Manual | TBD | |
| | T01.03 | D-M1-003 | | Manual | TBD | |
| | ... | ... | | ... | ... | |

---

## Checkpoint Report Template

**Template:**
- `# Checkpoint Report — <Checkpoint Title>`
- `**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/M1/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets)
- `## Exit Criteria Assessment` (exactly 3 bullets)
- `## Issues & Follow-ups`
- `## Evidence`

---

*Generated by Tasklist-Generator v2.1*
