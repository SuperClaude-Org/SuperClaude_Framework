# Phase 5 -- Verification, Testing & Documentation

Comprehensive test suite (unit + integration + known-defect detection), architecture and performance verification, and operational documentation. All success criteria (SC-001 through SC-009) validated in this phase.

---

### T05.01 -- Confirm Tier Classifications for Phase 5 Tasks

| Field | Value |
|---|---|
| Roadmap Item IDs | -- |
| Why | Tier classifications for Phase 5 tasks have confidence < 0.70. Confirm tiers before executing the test suite. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0018/notes.md`

**Deliverables:**
- Confirmed tier assignments for T05.02-T05.07 with justification for any overrides

**Steps:**
1. **[PLANNING]** Review tier assignments for T05.02 through T05.07
2. **[PLANNING]** Assess whether test-focused tasks warrant STANDARD or LIGHT tier
3. **[EXECUTION]** Record confirmed or overridden tier for each task
4. **[EXECUTION]** Document override reasoning if any tier is changed
5. **[VERIFICATION]** Verify all six tasks have confirmed tiers
6. **[COMPLETION]** Write decision artifact to D-0018/notes.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0018/notes.md` exists with confirmed tiers for T05.02-T05.07
- Each tier decision includes a one-line justification
- Override reasons documented if any tier differs from computed assignment
- Traceability maintained (task IDs referenced in decision artifact)

**Validation:**
- Manual check: all Phase 5 tasks have a confirmed tier recorded in D-0018/notes.md
- Evidence: linkable artifact produced (D-0018/notes.md)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Clarification task for batch tier confirmation.

---

### T05.02 -- Write Unit Tests for Gate Validation, Config Parsing, and Report Semantics

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025, R-026, R-027 |
| Why | Unit tests validate the foundational components in isolation: gate criteria enforce correct structure, config parsing handles defaults, report semantics maintain invariants. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0019/evidence.md`

**Deliverables:**
- Unit test file covering gate validation (missing frontmatter, empty semantics, line count, agreement table), config parsing (agent parsing, defaults), and report semantics (`tasklist_ready == (blocking_issues_count == 0)`)

**Steps:**
1. **[PLANNING]** Review existing unit test patterns in `tests/` for test organization and assertion styles
2. **[PLANNING]** Define test matrix: gate validation (4 cases), config parsing (3 cases), report semantics (2 cases)
3. **[EXECUTION]** Write gate validation tests: missing frontmatter fields, empty semantic values, line count below thresholds, agreement table enforcement for ADVERSARIAL_MERGE_GATE
4. **[EXECUTION]** Write config parsing tests: agent string parsing, default value handling, invalid input handling
5. **[EXECUTION]** Write report semantics tests: `tasklist_ready == true` when `blocking_issues_count == 0`, `tasklist_ready == false` when `blocking_issues_count > 0`
6. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
7. **[COMPLETION]** Record test evidence in D-0019/evidence.md

**Acceptance Criteria:**
- Unit test file exists with test functions covering gate validation, config parsing, and report semantics
- Gate tests verify: reject on missing frontmatter, reject on empty semantic values, reject below min line count, accept valid input
- Report semantics test verifies invariant: `tasklist_ready == (blocking_issues_count == 0)`
- `uv run pytest <test_file> -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0019/evidence.md)

**Dependencies:** T01.02, T01.03, T05.01
**Rollback:** TBD
**Notes:** None

---

### T05.03 -- Write Integration Tests for Standalone Validation Modes (SC-001, SC-003)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028, R-029 |
| Why | SC-001 and SC-003 are top-level success criteria requiring standalone single-agent and multi-agent validation to produce valid reports. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0020/evidence.md`

**Deliverables:**
- Integration tests for SC-001 (standalone single-agent validation) and SC-003 (standalone multi-agent validation)

**Steps:**
1. **[PLANNING]** Create or identify test fixture directory with valid pipeline outputs (`roadmap.md`, `test-strategy.md`, `extraction.md`)
2. **[PLANNING]** Define expected outcomes: single-agent produces 1 report file, multi-agent produces per-agent files + merged report
3. **[EXECUTION]** Write SC-001 test: run `execute_validate` with 1 agent, assert `validate/validation-report.md` exists, parse frontmatter
4. **[EXECUTION]** Write SC-003 test: run `execute_validate` with 2+ agents, assert per-agent reflection files and merged report exist, verify agreement table presence
5. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
6. **[COMPLETION]** Record test evidence in D-0020/evidence.md

**Acceptance Criteria:**
- SC-001 test: single-agent validation against sample directory produces `validate/validation-report.md` with valid frontmatter
- SC-003 test: multi-agent validation produces per-agent reflection files and merged report with agreement table
- Both tests verify frontmatter contains required fields (`blocking_issues_count`, `warnings_count`, `tasklist_ready`)
- `uv run pytest <test_file> -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0020/evidence.md)

**Dependencies:** T03.02, T05.01
**Rollback:** TBD
**Notes:** None

---

### T05.04 -- Write Integration Tests for CLI Integration and Resume Paths (SC-004, SC-005)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030, R-031, R-032, R-033 |
| Why | SC-004 and SC-005 verify auto-invocation and skip behavior; resume path tests ensure validation respects pipeline completion state. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0021/evidence.md`

**Deliverables:**
- Integration tests for SC-004 (auto-invocation), SC-005 (--no-validate skip), resume-success (validation runs), resume-failure (validation skipped)

**Steps:**
1. **[PLANNING]** Design test harness for `roadmap run` integration tests (may need Click CliRunner or subprocess invocation)
2. **[PLANNING]** Define test scenarios: successful run triggers validation, --no-validate skips, resume after success runs validation, resume after failure skips
3. **[EXECUTION]** Write SC-004 test: `roadmap run` completes successfully, assert `validate/` directory exists in output
4. **[EXECUTION]** Write SC-005 test: `roadmap run --no-validate` completes, assert `validate/` directory does NOT exist
5. **[EXECUTION]** Write resume-success test: pipeline completes via `--resume`, validation runs
6. **[EXECUTION]** Write resume-failure test: pipeline halts on failed step via `--resume`, validation does NOT run
7. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
8. **[COMPLETION]** Record test evidence in D-0021/evidence.md

**Acceptance Criteria:**
- SC-004 test: `roadmap run` auto-invokes validation, `validate/` directory exists after successful run
- SC-005 test: `roadmap run --no-validate` skips validation, `validate/` directory absent
- Resume-success test: resumed pipeline that completes all steps invokes validation
- Resume-failure test: resumed pipeline that halts on a failed step does NOT invoke validation

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0021/evidence.md)

**Dependencies:** T04.03, T04.04, T05.01
**Rollback:** TBD
**Notes:** Effort is M due to 4 grouped roadmap items requiring distinct test scenarios with different pipeline states.

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.05

**Purpose:** Verify core test suite passes before architecture/performance verification and documentation.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P05-T01-T05.md`

**Verification:**
- All unit tests (gate, config, semantics) pass
- Integration tests for SC-001, SC-003, SC-004, SC-005 pass
- Resume path tests pass

**Exit Criteria:**
- T05.01 through T05.05 (next task) marked completed
- No test failures across the verification suite
- Test coverage includes both positive and negative cases

---

### T05.05 -- Write Known-Defect Detection Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | Validation must reliably detect known classes of defects (duplicate D-IDs, missing milestones, untraced requirements) to justify its existence. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0022/evidence.md`

**Deliverables:**
- Tests with intentionally defective inputs that verify the validator detects: duplicate D-IDs, missing milestone references, untraced requirements, cross-file inconsistencies

**Steps:**
1. **[PLANNING]** Create test fixtures with known defects: roadmap with duplicate D-IDs, roadmap with missing milestone, extraction with untraced requirement, cross-file field-name mismatch
2. **[PLANNING]** Define expected detection outcomes (BLOCKING finding for each defect type)
3. **[EXECUTION]** Write test for duplicate D-ID detection: input contains duplicate D-0001, expect BLOCKING finding
4. **[EXECUTION]** Write test for missing milestone detection: phase references non-existent milestone, expect BLOCKING finding
5. **[EXECUTION]** Write test for untraced requirement: requirement not linked to any deliverable, expect BLOCKING finding
6. **[EXECUTION]** Write test for cross-file inconsistency: field name in roadmap doesn't match extraction, expect BLOCKING finding
7. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all defect detection tests pass
8. **[COMPLETION]** Record test evidence in D-0022/evidence.md

**Acceptance Criteria:**
- Test file contains at least 4 tests, one per known defect class (duplicate D-ID, missing milestone, untraced requirement, cross-file inconsistency)
- Each test uses intentionally defective input and asserts the validator produces a BLOCKING finding
- Tests verify the finding identifies the specific defect (not just generic failure)
- `uv run pytest <test_file> -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0022/evidence.md)

**Dependencies:** T03.02, T05.01
**Rollback:** TBD
**Notes:** SC-006 success criterion. These tests validate that the validation subsystem detects real classes of defects that have been observed in pipeline outputs.

---

### T05.06 -- Verify Architecture Constraints and Performance (SC-002, SC-009)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035, R-036, R-037 |
| Why | Architecture tests prevent dependency drift; performance tests ensure single-agent validation stays within the 2-minute budget; infrastructure reuse is verified. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (latency verification) |
| Tier | STANDARD |
| Confidence | [███░░░░░░░] 30% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0023/evidence.md`

**Deliverables:**
- Architecture verification (unidirectional dependency check), performance measurement (single-agent <= 2 min), infrastructure reuse confirmation (no new subprocess abstractions)

**Steps:**
1. **[PLANNING]** Define verification commands: `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` for SC-009
2. **[PLANNING]** Design performance measurement: timed execution of single-agent validation against sample input
3. **[EXECUTION]** SC-009: Run `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` and assert empty output (no reverse imports)
4. **[EXECUTION]** SC-002/NFR-001: Time single-agent validation execution, assert <= 120 seconds
5. **[EXECUTION]** Verify infrastructure reuse: grep for new subprocess class definitions in `validate_*.py`, assert none found
6. **[VERIFICATION]** All three verification checks pass
7. **[COMPLETION]** Record verification evidence in D-0023/evidence.md

**Acceptance Criteria:**
- SC-009: `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty (no reverse imports from pipeline into validate)
- SC-002: Single-agent validation completes in <= 120 seconds on standard test input
- No new subprocess management classes or abstractions in `validate_*.py` files (reuses existing `execute_pipeline` and `ClaudeProcess`)
- D-0023/evidence.md records all three verification results with timestamps

**Validation:**
- `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` exits with no output
- Evidence: linkable artifact produced (D-0023/evidence.md)

**Dependencies:** T03.02, T04.03, T05.01
**Rollback:** TBD
**Notes:** Risk includes performance keyword match. NFR-001 specifies <= 2 min as proxy for token cost control.

---

### T05.07 -- Write Operational Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | Users need documentation for standalone `validate` usage, multi-agent trade-offs, and interaction between `--no-validate`, `--resume`, and validation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [█████░░░░░] 50% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0024/spec.md`

**Deliverables:**
- Operational documentation covering standalone validate usage, multi-agent trade-offs, --no-validate/--resume interaction semantics, and default agent count asymmetry rationale

**Steps:**
1. **[PLANNING]** Review existing documentation patterns in `docs/` for structure and style
2. **[PLANNING]** Outline documentation sections: usage, options, multi-agent mode, skip/resume behavior, defaults rationale
3. **[EXECUTION]** Write standalone `validate` usage section with CLI examples
4. **[EXECUTION]** Write multi-agent trade-offs section (cost vs rigor, when to use each)
5. **[EXECUTION]** Write `--no-validate` and `--resume` interaction semantics section
6. **[EXECUTION]** Write default agent count asymmetry rationale (standalone: 1 for cost; roadmap run: 2 for rigor)
7. **[VERIFICATION]** Review documentation for completeness against roadmap requirements
8. **[COMPLETION]** Record documentation specification in D-0024/spec.md

**Acceptance Criteria:**
- Documentation file exists covering all 4 specified topics: standalone usage, multi-agent trade-offs, --no-validate/--resume interaction, agent count defaults
- CLI examples are syntactically valid and match implemented subcommand options
- Multi-agent trade-offs section explains cost vs rigor considerations
- Default agent count asymmetry rationale documented per OQ-1 decision

**Validation:**
- Manual check: documentation covers all 4 topics with no TODO placeholders
- Evidence: linkable artifact produced (D-0024/spec.md)

**Dependencies:** T04.02, T04.03, T05.01
**Rollback:** TBD
**Notes:** Tier is EXEMPT as documentation is read-only output with no code changes. Path booster (+0.5 EXEMPT from docs content).

---

### Checkpoint: End of Phase 5

**Purpose:** Final verification that all success criteria (SC-001 through SC-009) are met, all tests pass, and operational documentation is complete.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P05-END.md`

**Verification:**
- All unit tests pass: `uv run pytest tests/ -v` exits 0
- All integration tests pass: SC-001, SC-002, SC-003, SC-004, SC-005, SC-006 verified
- Architecture constraints verified: SC-009 (no reverse imports), infrastructure reuse confirmed

**Exit Criteria:**
- All Phase 5 tasks (T05.01-T05.07) marked completed
- SC-008: `uv run pytest` passes all unit and integration tests
- Operational documentation covers all 4 specified topics
