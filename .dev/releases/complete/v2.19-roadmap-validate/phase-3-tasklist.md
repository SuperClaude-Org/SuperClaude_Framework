# Phase 3 -- Validation Executor

Build `validate_executor.py` implementing end-to-end validation in both single-agent and multi-agent modes, reusing existing `execute_pipeline` and `ClaudeProcess` infrastructure. Includes partial failure handling with degraded report marking.

---

### T03.01 -- Confirm Tier Classifications for Phase 3 Tasks

| Field | Value |
|---|---|
| Roadmap Item IDs | -- |
| Why | Tier classifications for Phase 3 tasks have confidence < 0.70 due to infrastructure-domain keyword mismatch. Confirm tiers before execution. |
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
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0008/notes.md`

**Deliverables:**
- Confirmed tier assignments for T03.02 (STANDARD), T03.03 (STANDARD), T03.04 (STANDARD) with justification for any overrides

**Steps:**
1. **[PLANNING]** Review tier assignments for T03.02, T03.03, T03.04
2. **[PLANNING]** Assess whether keyword-driven tier matches task risk profile
3. **[EXECUTION]** Record confirmed or overridden tier for each task
4. **[EXECUTION]** Document override reasoning if any tier is changed
5. **[VERIFICATION]** Verify all three tasks have confirmed tiers
6. **[COMPLETION]** Write decision artifact to D-0008/notes.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0008/notes.md` exists with confirmed tiers for T03.02, T03.03, T03.04
- Each tier decision includes a one-line justification
- Override reasons documented if any tier differs from computed assignment
- Traceability maintained (task IDs referenced in decision artifact)

**Validation:**
- Manual check: all Phase 3 tasks have a confirmed tier recorded in D-0008/notes.md
- Evidence: linkable artifact produced (D-0008/notes.md)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Clarification task for batch tier confirmation.

---

### T03.02 -- Create `validate_executor.py` with `execute_validate` Function

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010, R-011, R-012, R-013 |
| Why | The executor orchestrates the full validation workflow: reading inputs, routing by agent count, applying gates, and writing reports. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0009/spec.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/validate_executor.py` containing `execute_validate(config: ValidateConfig)` with single-agent and multi-agent routing, gate enforcement, and report writing

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/executor.py` to understand `execute_pipeline` and `ClaudeProcess` usage patterns
2. **[PLANNING]** Identify reusable subprocess management patterns (no new abstractions per roadmap constraint)
3. **[EXECUTION]** Create `src/superclaude/cli/roadmap/validate_executor.py`
4. **[EXECUTION]** Implement `execute_validate(config: ValidateConfig)` that reads 3 input files (`roadmap.md`, `test-strategy.md`, `extraction.md`) from `config.output_dir`, validates file presence
5. **[EXECUTION]** Implement agent routing: 1 agent -> sequential reflection -> REFLECT_GATE check -> write `validate/validation-report.md`; N agents -> N parallel reflections -> gate each -> sequential adversarial merge -> ADVERSARIAL_MERGE_GATE -> write merged report
6. **[EXECUTION]** Create `validate/` subdirectory within output_dir for all validation outputs
7. **[EXECUTION]** Return structured result dict with `blocking_count`, `warning_count`, `info_count` fields
8. **[VERIFICATION]** Run `uv run python -c "from superclaude.cli.roadmap.validate_executor import execute_validate"` to verify import
9. **[COMPLETION]** Record executor specification in D-0009/spec.md

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/validate_executor.py` exists with `execute_validate` function accepting `ValidateConfig` parameter
- Function reads `roadmap.md`, `test-strategy.md`, `extraction.md` from `config.output_dir` and raises `FileNotFoundError` if any missing
- Single-agent path writes `validate/validation-report.md`; multi-agent path writes per-agent reflections and merged report
- Function reuses `execute_pipeline` and `ClaudeProcess` (no new subprocess abstractions introduced)

**Validation:**
- `uv run python -c "from superclaude.cli.roadmap.validate_executor import execute_validate; print('OK')"` exits 0
- Evidence: linkable artifact produced (D-0009/spec.md)

**Dependencies:** T01.02, T01.03, T02.02, T03.01
**Rollback:** TBD
**Notes:** Effort is M due to 4 grouped roadmap items (R-010 through R-013) and complex routing logic (single vs multi-agent).

---

### T03.03 -- Implement Partial Failure Handling with Degraded Validation Reports

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | When one agent in a multi-agent validation fails after retry, the system must produce an incomplete report rather than silently failing. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | rollback, breaking (degraded output semantics) |
| Tier | STANDARD |
| Confidence | [███░░░░░░░] 30% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0010/spec.md`

**Deliverables:**
- Partial failure handling logic in `validate_executor.py` that writes degraded reports with `validation_complete: false` frontmatter and warning banner

**Steps:**
1. **[PLANNING]** Review retry semantics of `ClaudeProcess` to understand failure modes
2. **[PLANNING]** Define degraded report format: `validation_complete: false` in YAML frontmatter, warning banner text
3. **[EXECUTION]** Add partial failure handling to multi-agent path in `execute_validate`
4. **[EXECUTION]** When agent A succeeds and agent B fails after retry: write agent A's reflection file, produce degraded report with `validation_complete: false` and warning banner identifying failed agent(s)
5. **[VERIFICATION]** Write a test that simulates agent failure and verifies degraded report contains expected frontmatter and banner
6. **[COMPLETION]** Record specification in D-0010/spec.md

**Acceptance Criteria:**
- When one agent fails in multi-agent mode, `validate/validation-report.md` is written with `validation_complete: false` in YAML frontmatter
- Degraded report includes a prominent warning banner naming which agent(s) failed
- Successful agent's reflection file is preserved in `validate/` directory
- No silent degradation: report must be unmistakably marked as incomplete

**Validation:**
- Manual check: simulate agent failure scenario and verify degraded report output structure
- Evidence: linkable artifact produced (D-0010/spec.md)

**Dependencies:** T03.02
**Rollback:** TBD
**Notes:** Risk is Medium due to degraded output semantics that downstream consumers must handle. Per roadmap OQ-2: "Silent degradation is unacceptable."

---

### T03.04 -- Integration Test Executor Against Known-Good and Known-Bad Outputs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | End-to-end executor testing ensures the full validation workflow produces correct reports for both valid and invalid pipeline outputs. |
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
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0011/evidence.md`

**Deliverables:**
- Integration test file for `execute_validate` covering known-good (valid pipeline output) and known-bad (invalid output) scenarios

**Steps:**
1. **[PLANNING]** Identify or create test fixtures: known-good pipeline output directory with `roadmap.md`, `test-strategy.md`, `extraction.md`; known-bad directory with missing/malformed files
2. **[PLANNING]** Define expected outcomes for each fixture (pass vs blocking issues detected)
3. **[EXECUTION]** Create integration test file following project test organization patterns
4. **[EXECUTION]** Write test for known-good input: assert validation report produced, no blocking issues
5. **[EXECUTION]** Write test for known-bad input: assert blocking issues detected and reported
6. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
7. **[COMPLETION]** Record test evidence in D-0011/evidence.md

**Acceptance Criteria:**
- Integration test file exists in `tests/` directory with at least 2 test cases (known-good, known-bad)
- Known-good test verifies: validation report produced, result contains `blocking_count == 0`
- Known-bad test verifies: blocking issues detected, result contains `blocking_count > 0`
- `uv run pytest <test_file> -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0011/evidence.md)

**Dependencies:** T03.02, T03.03
**Rollback:** TBD
**Notes:** None

---

### Checkpoint: End of Phase 3

**Purpose:** Verify that the validation executor works end-to-end in both single and multi-agent modes before CLI integration.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P03-END.md`

**Verification:**
- `execute_validate` importable and callable with `ValidateConfig` parameter
- Single-agent mode produces `validate/validation-report.md` from valid inputs
- Multi-agent mode produces per-agent reflections and merged report; partial failure produces degraded report

**Exit Criteria:**
- All Phase 3 tasks (T03.01-T03.04) marked completed
- Integration tests pass for both known-good and known-bad inputs
- No reverse imports into `pipeline/` directory (`grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty)
