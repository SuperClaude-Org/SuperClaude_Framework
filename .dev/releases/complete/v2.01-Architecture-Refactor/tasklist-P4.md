# TASKLIST — v2.01 Architecture Refactor — Phase 4

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 4: Structural Validation & Testing

Implement integration tests for return contract routing, adversarial pipeline integration, and artifact gate specifications. Verify all tests pass and triage any discovered issues to zero Critical/Major before proceeding to polish work.

---

### T04.01 — Return Contract Consumer Routing Tests

**Roadmap Item ID(s):** R-021
**Why:** The return contract routing logic (Pass ≥0.6, Partial ≥0.5, Fail <0.5) must be validated with explicit tests covering all 3 routing paths plus edge cases (missing file, parse error). Without these tests, consumer behavior is unverified.
**Effort:** `M`
**Risk:** `High`
**Risk Drivers:** end-to-end scope, breaking change (contract schema), system-wide dependency
**Tier:** `STRICT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0022
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0022/spec.md`
- `TASKLIST_ROOT/artifacts/D-0022/evidence.md`

**Deliverables:**
1. Test suite validating Pass/Partial/Fail routing paths with convergence thresholds (0.6/0.5)
2. Edge case tests: missing return-contract.yaml file, YAML parse error, malformed convergence_score

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §10 (return contract schema), §9 (convergence thresholds), D-0009 (Step 3e routing)
2. **[PLANNING]** Check dependencies: Phase 3 complete (enforcement in place); T02.03 (routing logic defined)
3. **[EXECUTION]** Create test fixtures: valid return-contract.yaml with scores 0.7 (Pass), 0.55 (Partial), 0.3 (Fail)
4. **[EXECUTION]** Implement routing tests: verify consumer correctly routes to Pass/Partial/Fail paths
5. **[EXECUTION]** Implement edge case tests: missing file → skip, parse error → fallback score 0.5, boundary values (0.6 exact, 0.5 exact)
6. **[VERIFICATION]** All routing tests pass for all 3 paths plus edge cases
7. **[COMPLETION]** Document test results in D-0022 artifacts

**Acceptance Criteria:**
- Tests pass for all 3 routing paths: Pass (score ≥ 0.6), Partial (score ≥ 0.5), Fail (score < 0.5)
- Edge cases covered: missing file, parse error, boundary values (exact 0.6, exact 0.5)
- Test fixtures use the canonical 10-field schema from sprint-spec §10
- SC-007 validated: "Return contract routing handles Pass/Partial/Fail correctly"

**Validation:**
- `uv run pytest tests/ -k "return_contract"` — all tests pass
- Evidence: linkable artifacts produced at D-0022 spec and evidence paths

**Dependencies:** T02.03, Phase 3 complete
**Rollback:** Remove test files; no production code changes
**Notes:** SC-007: "Return contract routing handles Pass/Partial/Fail correctly" — this task directly validates that success criterion.

---

### T04.02 — Adversarial Pipeline Integration Tests

**Roadmap Item ID(s):** R-022
**Why:** The fallback protocol F1/F2-3/F4-5 must be validated end-to-end to confirm it produces a valid `return-contract.yaml`. Without integration tests, the entire adversarial pipeline invocation path is unverified.
**Effort:** `M`
**Risk:** `High`
**Risk Drivers:** end-to-end scope, system-wide dependency, breaking change (protocol)
**Tier:** `STRICT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0023
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0023/spec.md`
- `TASKLIST_ROOT/artifacts/D-0023/evidence.md`

**Deliverables:**
1. Integration test suite verifying fallback protocol F1 → F2/3 → F4/5 produces valid return-contract.yaml
2. Test coverage for: variant generation, diff+debate, selection+merge, contract output

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §9 (fallback protocol), D-0010 (F1/F2-3/F4-5 spec)
2. **[PLANNING]** Check dependencies: T04.01 complete (routing tests establish contract format)
3. **[EXECUTION]** Create test harness for fallback protocol execution
4. **[EXECUTION]** Test F1: variant generation produces agent outputs
5. **[EXECUTION]** Test F2/3: diff analysis + adversarial debate produces scored variants
6. **[EXECUTION]** Test F4/5: base selection + merge produces return-contract.yaml with valid schema
7. **[VERIFICATION]** End-to-end fallback path produces valid return-contract.yaml with 10 required fields
8. **[COMPLETION]** Document test results in D-0023 artifacts

**Acceptance Criteria:**
- Integration tests cover all 3 fallback stages (F1, F2/3, F4/5)
- Output return-contract.yaml validates against canonical 10-field schema
- Fallback sentinel value (0.5) correctly used when convergence unmeasurable
- Test demonstrates FALLBACK-ONLY variant works end-to-end

**Validation:**
- `uv run pytest tests/ -k "adversarial_pipeline"` — all tests pass
- Evidence: linkable artifacts produced at D-0023 spec and evidence paths

**Dependencies:** T04.01, T02.03
**Rollback:** Remove test files; no production code changes
**Notes:** Risk R-001: Partial application during testing. Run tests in isolated environment; verify atomicity.

---

### T04.03 — Artifact Gate Specification and Standards

**Roadmap Item ID(s):** R-023
**Why:** Artifact gates must be defined for all 3 output artifacts (roadmap.md, extraction.md, test-strategy.md) to establish quality standards for pipeline outputs.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** end-to-end scope, system-wide applicability
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended (STRICT tier)
**Deliverable IDs:** D-0024
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0024/spec.md`

**Deliverables:**
1. Artifact gate specification defining quality gates for roadmap.md, extraction.md, and test-strategy.md outputs

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §10 (return contract), §9 (convergence thresholds); existing artifact formats
2. **[PLANNING]** Check dependencies: T04.01, T04.02 complete (contract and pipeline validated)
3. **[EXECUTION]** Define artifact gate for roadmap.md: required sections, minimum content, structural validation
4. **[EXECUTION]** Define artifact gate for extraction.md: required fields, format constraints
5. **[EXECUTION]** Define artifact gate for test-strategy.md: required sections, coverage requirements
6. **[VERIFICATION]** Verify gates are testable (each criterion can be checked programmatically or via manual checklist)
7. **[COMPLETION]** Document specification in `TASKLIST_ROOT/artifacts/D-0024/spec.md`

**Acceptance Criteria:**
- Gates defined for all 3 output artifacts (roadmap.md, extraction.md, test-strategy.md)
- Each gate specifies: required sections, structural validation rules, minimum content criteria
- Gates are deterministic (same input → same pass/fail result)
- Specification references return contract schema for consistency

**Validation:**
- Manual check: artifact gate specification is complete with testable criteria for all 3 artifacts
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0024/spec.md`

**Dependencies:** T04.01, T04.02
**Rollback:** N/A (specification document; no code changes)
**Notes:** —

---

### T04.04 — M7 Test Results Documentation

**Roadmap Item ID(s):** R-024
**Why:** All Phase 4 test results must be documented in a structured report with pass/fail counts and coverage metrics before proceeding to polish work.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0025
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Deliverables:**
1. Structured test report with pass/fail counts, coverage metrics, and issue summary

**Steps:**
1. **[PLANNING]** Load context: T04.01–T04.03 test results (D-0022, D-0023, D-0024)
2. **[PLANNING]** Check dependencies: T04.01–T04.03 complete
3. **[EXECUTION]** Aggregate pass/fail counts from all Phase 4 tests
4. **[EXECUTION]** Calculate coverage metrics: routing paths tested, edge cases covered, schema fields validated
5. **[VERIFICATION]** Report is complete with all test results documented
6. **[COMPLETION]** Write report to `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Acceptance Criteria:**
- Report includes pass/fail counts for all T04.01–T04.03 tests
- Coverage metrics documented (routing paths, edge cases, schema fields)
- Any failing tests explicitly listed with failure details
- Report format supports Phase 4 exit criteria assessment

**Validation:**
- Manual check: test report exists with complete pass/fail and coverage data
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Dependencies:** T04.01, T04.02, T04.03
**Rollback:** N/A (documentation only)
**Notes:** —

---

### T04.05 — Issue Triage: Zero Critical/Major Issues

**Roadmap Item ID(s):** R-025
**Why:** Before proceeding to Phase 5 polish work, all Critical and Major issues from Phase 4 testing must be resolved. Any unresolved Critical issues block the release.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0026
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Deliverables:**
1. Issue triage report confirming zero Critical issues and all Major issues resolved

**Steps:**
1. **[PLANNING]** Load context: T04.04 test results report (D-0025)
2. **[PLANNING]** Check dependencies: T04.04 complete (test results documented)
3. **[EXECUTION]** Classify all findings as Critical, Major, Minor, or Informational
4. **[EXECUTION]** Resolve any Critical or Major issues (fix, retest, document)
5. **[VERIFICATION]** Confirm zero Critical issues; zero unresolved Major issues
6. **[COMPLETION]** Write triage report to `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Acceptance Criteria:**
- Zero Critical issues remaining
- All Major issues resolved before proceeding to Phase 5
- Minor and Informational issues documented for future reference
- Triage methodology documented (classification criteria)

**Validation:**
- Manual check: triage report confirms zero Critical/Major issues
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Dependencies:** T04.04
**Rollback:** N/A (triage is assessment; fixes may need separate rollback)
**Notes:** If Major issues discovered: allocate rework budget per M8 mitigation; fix before proceeding.

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm all structural validation tests pass and the codebase is ready for polish and integration work.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`

**Verification:**
- Return contract routing tests pass for all 3 paths plus edge cases (D-0022)
- Adversarial pipeline integration tests produce valid return-contract.yaml (D-0023)
- Artifact gate specification complete for all 3 outputs (D-0024)

**Exit Criteria:**
- D-0022 through D-0026 artifacts exist with valid content
- Zero Critical issues; all Major issues resolved (D-0026)
- All success criteria testable by Phase 4 work are verified (SC-007)

---

*End of Phase 4 — see `tasklist-P5.md` for Phase 5: Polish*
