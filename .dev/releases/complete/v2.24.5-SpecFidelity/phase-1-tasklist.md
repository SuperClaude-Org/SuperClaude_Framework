# Phase 1 -- Empirical Validation Gate

This phase determines whether `claude --file /path` delivers file content to the model. The result (WORKING or BROKEN) gates whether Phase 5 (conditional --file fallback remediation) activates. No code changes are permitted before this phase completes.

### T01.01 -- Verify `claude` CLI availability

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-003 |
| Why | Must confirm `claude` CLI is installed and functional before any empirical testing or code changes can proceed. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0001/evidence.md

**Deliverables:**
- CLI availability confirmation: `claude --print -p "hello" --max-turns 1` exits 0 with valid output

**Steps:**
1. **[PLANNING]** Identify the `claude` CLI binary location and confirm PATH availability
2. **[PLANNING]** Review expected output format for `--print` mode
3. **[EXECUTION]** Run `claude --print -p "hello" --max-turns 1`
4. **[EXECUTION]** Capture exit code and stdout
5. **[VERIFICATION]** Confirm exit code is 0 and output is non-empty
6. **[COMPLETION]** Record result in D-0001/evidence.md

**Acceptance Criteria:**
- `claude --print -p "hello" --max-turns 1` exits with code 0 and produces non-empty stdout
- CLI binary is accessible without manual PATH modifications
- Command is repeatable with identical exit code on re-run
- Result recorded in .dev/releases/current/v2.24.5/artifacts/D-0001/evidence.md

**Validation:**
- Manual check: `claude --print -p "hello" --max-turns 1` produces exit code 0
- Evidence: CLI output captured in .dev/releases/current/v2.24.5/artifacts/D-0001/evidence.md

**Dependencies:** None
**Rollback:** N/A (read-only verification)
**Notes:** Blocking prerequisite for all subsequent phases. If CLI is unavailable, no further work proceeds.

---

### T01.02 -- Check `claude --help` for `--file` format

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Need to determine whether `--file` requires `file_id:path` prefix format to correctly construct the empirical test in T01.03. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0002/notes.md

**Deliverables:**
- Documentation of `--file` argument format (whether `file_id:path` prefix is required or plain path suffices)

**Steps:**
1. **[PLANNING]** Identify help flag format for `claude` CLI
2. **[PLANNING]** Determine which help section covers `--file`
3. **[EXECUTION]** Run `claude --help` and search output for `--file` documentation
4. **[EXECUTION]** Record whether `file_id:path` prefix is required
5. **[VERIFICATION]** Cross-reference help text with OQ-5 from roadmap
6. **[COMPLETION]** Document format finding in D-0002/notes.md

**Acceptance Criteria:**
- `claude --help` output captured and `--file` section identified
- Format requirement (plain path vs `file_id:path`) explicitly documented
- Finding addresses OQ-5 from roadmap (not in spec Section 11)
- Result recorded in .dev/releases/current/v2.24.5/artifacts/D-0002/notes.md

**Validation:**
- Manual check: `--file` format documented with evidence from `claude --help` output
- Evidence: Help text excerpt saved in .dev/releases/current/v2.24.5/artifacts/D-0002/notes.md

**Dependencies:** T01.01
**Rollback:** N/A (read-only investigation)
**Notes:** Related to OQ-5 — roadmap addition not in spec Section 11.

---

### T01.03 -- Execute empirical `--file` test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Empirically determine whether `claude --file` delivers file content to the model, which gates Phase 5 activation. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0003/evidence.md

**Deliverables:**
- Empirical test output: whether response mentions PINEAPPLE when file content is passed via `--file`

**Steps:**
1. **[PLANNING]** Prepare test file content (`echo "The secret answer is PINEAPPLE." > /tmp/file-test.md`)
2. **[PLANNING]** Construct CLI command using `--file` format determined in T01.02
3. **[EXECUTION]** Create `/tmp/file-test.md` with secret answer content
4. **[EXECUTION]** Run `claude --print -p "What is the secret answer?" --file /tmp/file-test.md`
5. **[VERIFICATION]** Inspect response for presence of "PINEAPPLE" and record exit code
6. **[COMPLETION]** Capture full command, output, and exit code in D-0003/evidence.md

**Acceptance Criteria:**
- `/tmp/file-test.md` created with content `The secret answer is PINEAPPLE.`
- `claude --print -p "What is the secret answer?" --file /tmp/file-test.md` executed and output captured
- Exit code and full response text recorded verbatim
- Result recorded in .dev/releases/current/v2.24.5/artifacts/D-0003/evidence.md

**Validation:**
- Manual check: command output and exit code captured in evidence file
- Evidence: full CLI transcript in .dev/releases/current/v2.24.5/artifacts/D-0003/evidence.md

**Dependencies:** T01.01, T01.02
**Rollback:** `rm /tmp/file-test.md`
**Notes:** The ~80% probability of BROKEN means Phase 5 should be treated as likely.

---

### T01.04 -- Record Phase 0 result

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Formalize the empirical test outcome into one of three named categories for gate decision in T01.05. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0004/evidence.md

**Deliverables:**
- Phase 0 result categorized as one of: WORKING (response mentions PINEAPPLE), BROKEN (exit 0 but no PINEAPPLE), or CLI FAILURE (non-zero exit)

**Steps:**
1. **[PLANNING]** Review T01.03 output (exit code and response text)
2. **[PLANNING]** Map output to the three named outcomes from roadmap
3. **[EXECUTION]** If exit code != 0: record CLI FAILURE, resolve CLI issue, re-run T01.01
4. **[EXECUTION]** If exit code == 0 and response mentions PINEAPPLE: record WORKING
5. **[EXECUTION]** If exit code == 0 and response does not mention PINEAPPLE: record BROKEN
6. **[COMPLETION]** Write categorized result to D-0004/evidence.md

**Acceptance Criteria:**
- Result is exactly one of: WORKING, BROKEN, or CLI FAILURE — where WORKING and BROKEN apply only when exit code is 0
- CLI FAILURE triggers re-investigation (not WORKING or BROKEN)
- Categorization logic matches roadmap Task 0.4 three-outcome definition
- Result recorded in .dev/releases/current/v2.24.5/artifacts/D-0004/evidence.md

**Validation:**
- Manual check: result matches one of three named outcomes with evidence
- Evidence: categorized result in .dev/releases/current/v2.24.5/artifacts/D-0004/evidence.md

**Dependencies:** T01.03
**Rollback:** N/A (documentation only)
**Notes:** None.

---

### T01.05 -- Gate decision on Phase 5 activation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Determine whether Phase 5 (conditional --file fallback remediation) activates based on Phase 0 empirical result. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0005/spec.md

**Deliverables:**
- Gate decision document: WORKING → skip Phase 5, proceed to Phase 2; BROKEN → Phase 5 activates after Phases 2-4

**Steps:**
1. **[PLANNING]** Read T01.04 result (WORKING or BROKEN)
2. **[PLANNING]** Map result to gate decision per roadmap
3. **[EXECUTION]** If WORKING: document that Phase 5 is skipped; Phases 2, 3, 4, 6, 7 proceed
4. **[EXECUTION]** If BROKEN: document that Phase 5 activates and becomes release-blocking
5. **[VERIFICATION]** Confirm decision aligns with roadmap gate logic
6. **[COMPLETION]** Write gate decision to D-0005/spec.md

**Acceptance Criteria:**
- Gate decision is binary: Phase 5 activated or skipped
- Decision correctly maps WORKING→skip and BROKEN→activate per roadmap Task 0.5
- All downstream phase dependencies updated in execution context
- Decision recorded in .dev/releases/current/v2.24.5/artifacts/D-0005/spec.md

**Validation:**
- Manual check: gate decision matches Phase 0 result per roadmap logic
- Evidence: decision document in .dev/releases/current/v2.24.5/artifacts/D-0005/spec.md

**Dependencies:** T01.04
**Rollback:** N/A (documentation only)
**Notes:** Roadmap estimates ~80% probability of BROKEN. Phase 5 should be treated as likely. Roadmap "Phase 1.5" = tasklist Phase 5 (renumbered for contiguous sequencing).

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm Phase 0 empirical validation gate is complete with a recorded binary result before any code changes proceed.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P01-END.md

**Verification:**
- T01.04 result is exactly WORKING or BROKEN (CLI FAILURE resolved before reaching this point)
- T01.05 gate decision documented with Phase 5 activation status
- All evidence artifacts (D-0001 through D-0005) have intended paths established

**Exit Criteria:**
- Phase 0 result recorded as WORKING or BROKEN
- Gate decision on Phase 5 activation documented
- No code changes have been made (Phase 1 is read-only investigation)
