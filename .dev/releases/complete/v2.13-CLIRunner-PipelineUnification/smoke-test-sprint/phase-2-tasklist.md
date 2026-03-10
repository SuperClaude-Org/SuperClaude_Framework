# Phase 2 - Validate & Report

This phase validates that Phase 1 produced all expected artifacts and generates a final summary report.

---

### T02.01 -- Validate all Phase 1 artifacts exist and are correct

| Field | Value |
|---|---|
| Effort | XS |
| Risk | Low |
| Tier | STRICT |
| Verification Method | Sub-agent (quality-engineer) |
| Deliverable IDs | D-0004 |

**Deliverables:**
- Validate that all three Phase 1 artifact files exist and contain expected content. Write a validation report to `.dev/releases/current/smoke-test-sprint/artifacts/validation-report.txt`.

**Steps:**
1. Check `.dev/releases/current/smoke-test-sprint/artifacts/smoke-output.txt` exists and first line is `SMOKE_TEST_PHASE_1_OK`
2. Check `.dev/releases/current/smoke-test-sprint/artifacts/defaults-check.txt` exists and contains `ALL_DEFAULTS_OK`
3. Check `.dev/releases/current/smoke-test-sprint/artifacts/pytest-results.txt` exists, is non-empty, contains "passed", and does NOT contain "FAILED"
4. Write validation results to `.dev/releases/current/smoke-test-sprint/artifacts/validation-report.txt` with one line per check: `CHECK_N: PASS` or `CHECK_N: FAIL: reason`

**Acceptance Criteria:**
- All three artifact files from Phase 1 are present and valid
- Validation report shows all checks passed

**Dependencies:** T01.01, T01.02, T01.03

---

### T02.02 -- Generate final smoke test summary

| Field | Value |
|---|---|
| Effort | XS |
| Risk | Low |
| Tier | STANDARD |
| Verification Method | Direct test execution |
| Deliverable IDs | D-0005 |

**Deliverables:**
- Generate a markdown summary file at `.dev/releases/current/smoke-test-sprint/artifacts/SUMMARY.md` containing: sprint name, timestamp, number of tasks completed, list of artifact files with sizes, and a final PASS/FAIL verdict.

**Steps:**
1. Read the validation report from T02.01
2. List all files in `.dev/releases/current/smoke-test-sprint/artifacts/` with sizes
3. Write `.dev/releases/current/smoke-test-sprint/artifacts/SUMMARY.md` with a structured markdown report

**Acceptance Criteria:**
- Summary file exists and contains a verdict line with "PASS" or "FAIL"
- Summary file lists all artifact files

**Dependencies:** T02.01
