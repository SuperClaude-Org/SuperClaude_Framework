# Phase 6 -- Integration Verification

Full test suite green; no regressions. Empirical, unit, boundary, and workflow validation layers all have evidence. Corresponds to spec Section 4.6 Phase 3 (Full Validation) -- phase numbering differs from spec.

### T06.01 -- Combined test run (sprint/roadmap/pipeline)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | All three test directories must pass together to confirm no cross-suite regressions from FIX-001 and FIX-ARG-TOO-LONG changes. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0027/evidence.md

**Deliverables:**
- `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` output showing 0 failures

**Steps:**
1. **[PLANNING]** Confirm all prior phase changes are saved and complete
2. **[PLANNING]** Note: `test_remediate_executor.py` and `test_inline_fallback.py` within `tests/roadmap/` only exist if Phase 5 was activated; their absence when Phase 1 = WORKING is expected
3. **[EXECUTION]** Run `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v`
4. **[EXECUTION]** Capture full test output including pass/fail/skip counts
5. **[VERIFICATION]** Confirm 0 failures; note expected skips if Phase 5 was not activated
6. **[COMPLETION]** Record full test output in D-0027/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` exits with code 0
- Output shows 0 failures across all three test directories
- Absence of Phase 5 conditional test files when Phase 1 = WORKING is not a failure
- Full test output recorded in .dev/releases/current/v2.24.5/artifacts/D-0027/evidence.md

**Validation:**
- `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` exits 0
- Evidence: complete test output in .dev/releases/current/v2.24.5/artifacts/D-0027/evidence.md

**Dependencies:** T02.06, T03.07, T04.01 (and T05.07 if Phase 5 activated)
**Rollback:** N/A (test execution only)
**Notes:** SC-012. Corresponds to spec Section 4.6 Phase 3 Task 3.1 (roadmap Task 2.1).

---

### T06.02 -- CLI smoke test with `--dry-run`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | End-to-end CLI validation: `superclaude sprint run ... --dry-run` must complete without error to confirm pipeline integration. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0028/evidence.md

**Deliverables:**
- `superclaude sprint run ... --dry-run` output showing successful completion without error

**Steps:**
1. **[PLANNING]** Identify appropriate sprint run arguments for dry-run test
2. **[PLANNING]** Confirm CLI binary is available (validated in Phase 1)
3. **[EXECUTION]** Run `superclaude sprint run ... --dry-run`
4. **[EXECUTION]** Capture full output and exit code
5. **[VERIFICATION]** Confirm exit code 0 and no error messages in output
6. **[COMPLETION]** Record output in D-0028/evidence.md

**Acceptance Criteria:**
- `superclaude sprint run ... --dry-run` exits with code 0
- No error messages or tracebacks in output
- Dry-run output indicates successful pipeline construction
- Output recorded in .dev/releases/current/v2.24.5/artifacts/D-0028/evidence.md

**Validation:**
- `superclaude sprint run ... --dry-run` exits 0
- Evidence: CLI output in .dev/releases/current/v2.24.5/artifacts/D-0028/evidence.md

**Dependencies:** T06.01
**Rollback:** N/A (read-only dry-run)
**Notes:** SC-013. Corresponds to spec Section 4.6 Phase 3 Task 3.4 (roadmap Task 2.2).

---

### T06.03 -- Large file E2E test (>=120 KB spec)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Must verify the primary failure mode is resolved: a pipeline run with >=120 KB spec file must complete the `spec-fidelity` step without `OSError: [Errno 7] Argument list too long`. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (large file handling), end-to-end scope |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0029/evidence.md

**Deliverables:**
- Pipeline run with >=120 KB spec file completing `spec-fidelity` step without `OSError`

**Steps:**
1. **[PLANNING]** Create or identify a spec file >= 120 KB for testing
2. **[PLANNING]** Determine pipeline command to run `spec-fidelity` step with the large file
3. **[EXECUTION]** Run pipeline with the >=120 KB spec file
4. **[EXECUTION]** Monitor for `OSError: [Errno 7] Argument list too long`
5. **[VERIFICATION]** Confirm `spec-fidelity` step completes without `OSError`
6. **[COMPLETION]** Record pipeline output and file size in D-0029/evidence.md

**Acceptance Criteria:**
- Spec file used is >= 120 KB (verified by `wc -c` or equivalent)
- Pipeline `spec-fidelity` step completes without `OSError: [Errno 7] Argument list too long`
- No other unrelated errors mask the test outcome
- Pipeline output and file size recorded in .dev/releases/current/v2.24.5/artifacts/D-0029/evidence.md

**Validation:**
- Manual check: pipeline completes `spec-fidelity` step with >=120 KB file, no `OSError`
- Evidence: pipeline output in .dev/releases/current/v2.24.5/artifacts/D-0029/evidence.md

**Dependencies:** T06.01
**Rollback:** N/A (test execution only)
**Notes:** SC-014. Corresponds to spec Section 4.6 Phase 3 Task 3.5 (roadmap Task 2.3). Primary failure mode validation.

---

### Checkpoint: End of Phase 6

**Purpose:** Confirm release candidate is validated across all four validation layers before commit and release.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P06-END.md

**Verification:**
- Combined test suite (sprint/roadmap/pipeline) passes with 0 failures
- CLI smoke test completes without error
- Large file E2E test (>=120 KB) passes without `OSError`

**Exit Criteria:**
- SC-012 (combined suite), SC-013 (dry-run), SC-014 (large file) all met
- Four-layer validation model complete: empirical (Phase 1), unit (Phase 2-3), boundary (Phase 3), workflow (Phase 6)
- Evidence collection checklist items verified
