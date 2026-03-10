# Phase 7 -- Integration Testing and Release Hardening

Release hardening with comprehensive testing against all 8 success criteria (SC-001 through SC-008). No regressions in existing pipeline steps 1–9. Performance benchmark report produced.

---

### T07.01 -- End-to-End Integration Test (Full 12-Step Pipeline)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-046 |
| Why | SC-001: roadmap run must complete all 12 steps without manual intervention when user approves remediation. No mocking of ClaudeProcess — use real subprocess execution. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | system-wide, pipeline |
| Tier | STRICT |
| Confidence | `[████████░░]` 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0035/evidence.md`

**Deliverables:**
- End-to-end integration test in `tests/roadmap/test_pipeline_integration.py` covering full 12-step pipeline

**Steps:**
1. **[PLANNING]** Design E2E test scenario with controlled validation findings (mix of BLOCKING, WARNING, INFO)
2. **[PLANNING]** Prepare test fixtures: spec file, validation report with known findings
3. **[EXECUTION]** Implement E2E test: steps 1-9 (existing) → validate → prompt (auto-approve) → remediate → certify
4. **[EXECUTION]** Verify all 12 steps complete with PASS status in `.roadmap-state.json`
5. **[EXECUTION]** Verify `certification-report.md` shows `certified: true` with all findings PASS
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_pipeline_integration.py -v` — E2E test passes
7. **[COMPLETION]** Document test results in `D-0035/evidence.md`

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_pipeline_integration.py -k "e2e"` exits 0
- All 12 steps complete with PASS status in `.roadmap-state.json`
- `certification-report.md` shows `certified: true`
- No mocking of ClaudeProcess (real subprocess execution per roadmap constraint)

**Validation:**
- `uv run pytest tests/roadmap/test_pipeline_integration.py -k "e2e"` exits 0
- Evidence: linkable artifact produced at `D-0035/evidence.md`

**Dependencies:** T06.05
**Rollback:** Remove E2E test (no production code changed)

---

### T07.02 -- Allowlist Enforcement Test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-047 |
| Why | SC-005: verify no files outside the allowed set (roadmap.md, extraction.md, test-strategy.md) are modified during remediation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0036/evidence.md`

**Deliverables:**
- Allowlist enforcement test verifying workspace diff restricted to allowed files

**Steps:**
1. **[PLANNING]** Design test: capture workspace file checksums before remediation
2. **[PLANNING]** Identify all files in release directory as baseline
3. **[EXECUTION]** Run remediation with findings targeting allowlist files
4. **[EXECUTION]** Compare post-remediation checksums: only allowed files should differ
5. **[VERIFICATION]** Assert no files outside allowlist were modified
6. **[COMPLETION]** Document test results in `D-0036/evidence.md`

**Acceptance Criteria:**
- Workspace diff before/after remediation restricted to allowlist files only
- Non-allowlist files have identical checksums before and after
- Test covers scenario with findings referencing non-allowlist files (should be SKIPPED)
- SC-005 explicitly verified

**Validation:**
- Manual check: workspace diff shows only allowlist file changes
- Evidence: linkable artifact produced at `D-0036/evidence.md`

**Dependencies:** T04.04
**Rollback:** Remove test

---

### T07.03 -- Performance Test (Steps 10-11 Overhead)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-048 |
| Why | SC-006: steps 10-11 (remediate + certify) must add ≤30% wall-clock time relative to steps 1-9. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance, latency |
| Tier | STANDARD |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0037/evidence.md`

**Deliverables:**
- Performance benchmark report measuring steps 10-11 overhead vs steps 1-9

**Steps:**
1. **[PLANNING]** Design benchmark: measure wall-clock time for steps 1-9 and steps 10-11 separately
2. **[PLANNING]** Identify measurement points: step start/end timestamps from `.roadmap-state.json`
3. **[EXECUTION]** Run full pipeline and extract timing data from state file timestamps
4. **[EXECUTION]** Calculate overhead: `(steps 10-11 time / steps 1-9 time) * 100`
5. **[VERIFICATION]** Assert overhead ≤ 30% (NFR-008)
6. **[COMPLETION]** Produce performance benchmark report in `D-0037/evidence.md`

**Acceptance Criteria:**
- Performance benchmark report produced with timing data
- Steps 10-11 overhead ≤ 30% of steps 1-9 wall-clock time
- Timing data extracted from `.roadmap-state.json` timestamps
- SC-006 explicitly verified

**Validation:**
- Manual check: overhead calculation shows ≤30%
- Evidence: linkable artifact produced at `D-0037/evidence.md`

**Dependencies:** T07.01
**Rollback:** Remove benchmark test

---

### T07.04 -- Tasklist Round-Trip Test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-049 |
| Why | SC-007: remediation-tasklist.md must survive parse → emit → re-parse without data loss. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[███████░░░]` 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0038/evidence.md`

**Deliverables:**
- Round-trip test: generate tasklist → parse → re-generate → compare

**Steps:**
1. **[PLANNING]** Design round-trip test: generate → parse → re-generate → compare
2. **[PLANNING]** Identify fields that must survive round-trip: all frontmatter, finding entries, statuses
3. **[EXECUTION]** Generate `remediation-tasklist.md` from test findings
4. **[EXECUTION]** Parse generated file back into Finding objects
5. **[VERIFICATION]** Re-generate from parsed objects and compare: original == regenerated
6. **[COMPLETION]** Document round-trip results in `D-0038/evidence.md`

**Acceptance Criteria:**
- Round-trip parse/emit produces identical output
- All frontmatter fields preserved through round-trip
- Finding IDs, statuses, and descriptions unchanged
- SC-007 explicitly verified

**Validation:**
- Manual check: diff between original and re-generated tasklist is empty
- Evidence: linkable artifact produced at `D-0038/evidence.md`

**Dependencies:** T03.04, T02.03
**Rollback:** Remove test

---

### T07.05 -- Backward-Compatibility Test with Old Consumers

| Field | Value |
|---|---|
| Roadmap Item IDs | R-050 |
| Why | SC-008: old consumers + new state schema must work without errors. Regression tests against pre-existing consumers. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | schema, breaking |
| Tier | STRICT |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0039/evidence.md`

**Deliverables:**
- Backward-compatibility regression test with old and new state schemas

**Steps:**
1. **[PLANNING]** Identify all state file consumers from T06.05 analysis
2. **[PLANNING]** Create test fixtures: old-format state (no remediate/certify), new-format state (all fields)
3. **[EXECUTION]** Run each consumer against old-format state → verify no errors
4. **[EXECUTION]** Run each consumer against new-format state → verify correct behavior
5. **[VERIFICATION]** All consumers handle both formats without errors
6. **[COMPLETION]** Document compatibility test results in `D-0039/evidence.md`

**Acceptance Criteria:**
- All state file consumers process old-format state without errors
- All state file consumers process new-format state correctly
- No KeyError, AttributeError, or TypeError on missing fields
- SC-008 explicitly verified

**Validation:**
- Manual check: consumers tested against both state formats
- Evidence: linkable artifact produced at `D-0039/evidence.md`

**Dependencies:** T06.05
**Rollback:** Remove test

---

### Checkpoint: Phase 7 / Tasks T07.01-T07.05

**Purpose:** Confirm core integration tests and success criteria SC-001, SC-005, SC-006, SC-007, SC-008 pass.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P07-T01-T05.md`
**Verification:**
- E2E test completes full 12-step pipeline
- Allowlist enforcement verified via workspace diff
- Performance overhead ≤ 30%
**Exit Criteria:**
- SC-001, SC-005, SC-006, SC-007, SC-008 all pass
- Backward-compatibility confirmed for old state formats
- Note: regression testing (steps 1-9) is covered by T07.08 at end-of-phase

---

### T07.06 -- Deliberate-Failure Test (Unfixed Findings Reported as FAIL)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-051 |
| Why | SC-003: certification must correctly identify unfixed findings as FAIL with justification. No false passes. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0040/evidence.md`

**Deliverables:**
- Deliberate-failure test with intentionally unfixed findings → FAIL with justification

**Steps:**
1. **[PLANNING]** Design test scenario: leave specific findings intentionally unfixed
2. **[PLANNING]** Identify which findings to leave unfixed for maximum test coverage
3. **[EXECUTION]** Run remediation with findings that will NOT be fixed by the agent (controlled failure)
4. **[EXECUTION]** Run certification against partially-remediated artifacts
5. **[VERIFICATION]** Assert unfixed findings are reported as FAIL with specific justification text
6. **[COMPLETION]** Document deliberate-failure test results in `D-0040/evidence.md`

**Acceptance Criteria:**
- Unfixed findings correctly reported as FAIL in `certification-report.md`
- Each FAIL entry includes a specific justification (not generic)
- No false passes on unfixed findings
- SC-003 explicitly verified

**Validation:**
- Manual check: certification report shows FAIL for intentionally unfixed findings
- Evidence: linkable artifact produced at `D-0040/evidence.md`

**Dependencies:** T05.03
**Rollback:** Remove test

---

### T07.07 -- Edge Case Coverage Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-052 |
| Why | Edge cases: SIGINT during remediation, out-of-allowlist findings, zero-findings path, fallback parser path. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide |
| Tier | STANDARD |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0041/evidence.md`

**Deliverables:**
- Edge case test suite covering 4 scenarios

**Steps:**
1. **[PLANNING]** List edge cases: SIGINT, out-of-allowlist, zero-findings, fallback parser
2. **[PLANNING]** Design test approach for each (some may require signal simulation)
3. **[EXECUTION]** Test SIGINT: interrupt during remediation → `.pre-remediate` files remain for manual recovery
4. **[EXECUTION]** Test out-of-allowlist: findings targeting non-allowed files → SKIPPED with WARNING
5. **[EXECUTION]** Test zero-findings: all findings filtered → stub tasklist → vacuous certification
6. **[EXECUTION]** Test fallback parser: merged report missing → individual reports parsed with dedup
7. **[VERIFICATION]** All 4 edge cases handled gracefully without crashes
8. **[COMPLETION]** Document edge case results in `D-0041/evidence.md`

**Acceptance Criteria:**
- SIGINT leaves `.pre-remediate` files for manual recovery (no data loss)
- Out-of-allowlist findings SKIPPED with WARNING per OQ-004
- Zero-findings path produces stub tasklist and vacuous certification
- Fallback parser correctly deduplicates across individual reports

**Validation:**
- Manual check: all 4 edge cases produce expected behavior
- Evidence: linkable artifact produced at `D-0041/evidence.md`

**Dependencies:** T02.04, T03.05, T04.04
**Rollback:** Remove tests

---

### T07.08 -- Regression Validation on Pre-Existing Pipeline Flows

| Field | Value |
|---|---|
| Roadmap Item IDs | R-053 |
| Why | New steps must not regress existing pipeline behavior (steps 1-9). Verify existing roadmap flows still work. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking |
| Tier | STANDARD |
| Confidence | `[████████░░]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0042 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0042/evidence.md`

**Deliverables:**
- Regression test confirming steps 1-9 unchanged behavior

**Steps:**
1. **[PLANNING]** Identify existing pipeline test suite for steps 1-9
2. **[PLANNING]** List critical regression points: step registration, gate evaluation, state persistence
3. **[EXECUTION]** Run existing pipeline tests: `uv run pytest tests/roadmap/ -k "not remediate and not certify"`
4. **[EXECUTION]** Verify steps 1-9 produce identical outputs with and without new steps registered
5. **[VERIFICATION]** All existing tests pass with no regressions
6. **[COMPLETION]** Document regression test results in `D-0042/evidence.md`

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -k "not remediate and not certify"` exits 0
- Steps 1-9 produce identical outputs to pre-v2.22 behavior
- No regressions in step registration, gate evaluation, or state persistence
- Existing pipeline flows unaffected by new step additions

**Validation:**
- `uv run pytest tests/roadmap/ -k "not remediate and not certify"` exits 0
- Evidence: linkable artifact produced at `D-0042/evidence.md`

**Dependencies:** T04.10, T05.06
**Rollback:** N/A (tests only)

---

### T07.09 -- Code Review Against Architectural Constraints

| Field | Value |
|---|---|
| Roadmap Item IDs | R-054 |
| Why | Final review verifying all code adheres to architectural constraints: pure prompts (NFR-004), unidirectional imports (NFR-007), atomic writes (NFR-005), ClaudeProcess reuse (NFR-006). |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | `[████████░░]` 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0043 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0043/notes.md`

**Deliverables:**
- Architecture constraint compliance review report

**Steps:**
1. **[PLANNING]** List all architectural constraints: pure prompts, unidirectional imports, atomic writes, ClaudeProcess reuse
2. **[PLANNING]** Identify all new modules: `remediate_parser.py`, `remediate_prompts.py`, `remediate_executor.py`, `certify_prompts.py`, `certify_gates.py`, `certify_executor.py`
3. **[EXECUTION]** Verify pure prompts: no I/O or side effects in prompt builder modules
4. **[EXECUTION]** Verify unidirectional imports: `remediate_*`/`certify_*` import from `pipeline.models` and `roadmap.models` only, not vice versa
5. **[EXECUTION]** Verify atomic writes: all file writes use `tmp + os.replace()` pattern
6. **[EXECUTION]** Verify ClaudeProcess reuse: no new subprocess abstractions, matching `validate_executor` pattern
7. **[VERIFICATION]** All constraints satisfied across all new modules
8. **[COMPLETION]** Write compliance report to `D-0043/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0043/notes.md` exists with compliance report
- All prompt builders confirmed as pure functions (no I/O)
- Import graph verified as unidirectional
- All file writes use atomic pattern (`tmp + os.replace`)

**Validation:**
- Manual check: compliance report covers all 4 constraint categories with evidence
- Review artifact produced at `D-0043/notes.md` (notes.md naming is intentional for EXEMPT review-type deliverables; all test-producing deliverables use evidence.md)

**Dependencies:** T07.01
**Rollback:** N/A (review only)

---

### Checkpoint: End of Phase 7

**Purpose:** Confirm all 8 success criteria pass and the release is ready.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P07-END.md`
**Verification:**
- All 8 success criteria (SC-001 through SC-008) pass with evidence
- No regressions in existing pipeline steps 1-9
- Performance benchmark report produced showing ≤30% overhead
**Exit Criteria:**
- Release-readiness checklist complete
- All tests pass: `uv run pytest tests/roadmap/ -v` exits 0
- Architecture constraint compliance verified across all new modules
