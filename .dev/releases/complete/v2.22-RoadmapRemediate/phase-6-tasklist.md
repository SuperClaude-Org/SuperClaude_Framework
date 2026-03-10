# Phase 6 -- Resume Support and State Finalization

Finalize state schema fields based on implementation evidence from Phases 2-5. Implement --resume skip logic with stale hash detection. Validate backward compatibility with old state files.

---

### T06.01 -- Finalize State Schema Fields and Step Transitions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039, R-044 |
| Why | Complete metadata fields for remediate and certify state entries based on Phases 2-4 implementation evidence. Define correct state transitions at each step boundary. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | schema |
| Tier | STRICT |
| Confidence | `[█████████-]` 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0030/spec.md`

**Deliverables:**
- Finalized state schema implementation in `_save_state()` with complete remediate and certify metadata fields per spec §3.1

**Steps:**
1. **[PLANNING]** Review state schema shape from T02.02 (D-0005) and actual implementation evidence from Phases 3-5
2. **[PLANNING]** Map each step boundary to its state transition and metadata fields
3. **[EXECUTION]** Implement remediate state entry: status, scope, findings_total, findings_actionable, findings_fixed, findings_failed, findings_skipped, agents_spawned, tasklist_file
4. **[EXECUTION]** Implement certify state entry: status, findings_verified, findings_passed, findings_failed, certified, report_file
5. **[EXECUTION]** Implement validation status transitions: validated-with-issues → remediated → certified | certified-with-caveats
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "state or schema"` to verify state writes and reads
7. **[COMPLETION]** Document finalized schema in `D-0030/spec.md`

**Acceptance Criteria:**
- `.roadmap-state.json` contains complete remediate and certify entries matching spec §3.1
- State transitions are correct at each boundary: post-validate → post-remediate → post-certify
- All metadata fields populated with real values (not placeholders)
- Schema extension is additive-only (SC-008 prerequisite)

**Validation:**
- `uv run pytest tests/roadmap/ -k "state or schema"` exits 0
- Evidence: linkable artifact produced at `D-0030/spec.md`

**Dependencies:** T04.10 (remediate step), T05.06 (certify step)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`
**Notes:** Critical Path Override: Yes — models/ path. Two-stage design: shape defined in Phase 2 (T02.02), fields finalized here based on implementation evidence.

---

### T06.02 -- Implement Resume Skip Logic for Remediate and Certify Steps

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040, R-041 |
| Why | --resume must skip completed steps using gate evaluation of output files, consistent with existing _apply_resume() logic. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0031/spec.md`

**Deliverables:**
- Resume skip logic for remediate step: if `remediation-tasklist.md` exists and passes REMEDIATE_GATE → skip
- Resume skip logic for certify step: if `certification-report.md` exists and passes CERTIFY_GATE → skip

**Steps:**
1. **[PLANNING]** Review existing `_apply_resume()` logic from T01.01 notes
2. **[PLANNING]** Define gate-check resume conditions for both new steps
3. **[EXECUTION]** Extend `_apply_resume()` with remediate gate check: output file exists + passes REMEDIATE_GATE + hash check
4. **[EXECUTION]** Extend `_apply_resume()` with certify gate check: output file exists + passes CERTIFY_GATE
5. **[EXECUTION]** Ensure resume from post-certify is a no-op (pipeline complete)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "resume"` to verify skip behavior
7. **[COMPLETION]** Document resume logic in `D-0031/spec.md`

**Acceptance Criteria:**
- Resume from post-validate skips to remediate correctly
- Resume from post-remediate skips to certify correctly
- Resume from post-certify is a no-op (pipeline complete, nothing to do)
- Resume decisions are gate- and hash-based, not timestamp-only (gate check passes AND source_report_hash matches current report, consistent with existing `_apply_resume()` pattern)

**Validation:**
- `uv run pytest tests/roadmap/ -k "resume"` exits 0
- Evidence: linkable artifact produced at `D-0031/spec.md`

**Dependencies:** T03.05 (REMEDIATE_GATE), T05.05 (CERTIFY_GATE), T06.01 (state schema)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`

---

### T06.03 -- Implement Stale Hash Detection (SHA-256 Comparison)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042 |
| Why | On --resume, verify source_report_hash in remediation-tasklist.md matches current validation report's SHA-256. If mismatch (stale tasklist from prior run), re-run remediate from scratch. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0032/spec.md`

**Deliverables:**
- Stale hash detection: compare `source_report_hash` in tasklist YAML frontmatter against SHA-256 of current validation report file

**Steps:**
1. **[PLANNING]** Define hash comparison logic: read tasklist frontmatter hash, compute current report hash, compare
2. **[PLANNING]** Define failure semantics: hash mismatch → re-run remediate from scratch (fail closed)
3. **[EXECUTION]** Implement hash comparison in resume logic: `hashlib.sha256(report_content).hexdigest()`
4. **[EXECUTION]** On mismatch: log warning, invalidate existing remediation output, re-run remediate
5. **[EXECUTION]** On match: proceed with skip (output is current)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "stale or hash"` to verify hash detection
7. **[COMPLETION]** Document hash detection in `D-0032/spec.md`

**Acceptance Criteria:**
- Stale hash detected when `source_report_hash` differs from current report SHA-256
- Hash mismatch triggers re-execution of remediate step (fail closed)
- Hash match allows skip (output is current)
- SHA-256 computation consistent with T03.04 hash generation

**Validation:**
- `uv run pytest tests/roadmap/ -k "stale or hash"` exits 0
- Evidence: linkable artifact produced at `D-0032/spec.md`

**Dependencies:** T03.04 (tasklist generation computes hash), T06.02 (resume logic)
**Rollback:** N/A (detection logic, no state changes)

---

### T06.04 -- Test Resume from All Pipeline States

| Field | Value |
|---|---|
| Roadmap Item IDs | R-043 |
| Why | Verify resume works correctly from each pipeline state: post-validate, post-remediate, post-certify per SC-004. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[█████████-]` 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0033/evidence.md`

**Deliverables:**
- Resume test suite verifying correct behavior from each pipeline state

**Steps:**
1. **[PLANNING]** Define test scenarios: resume from post-validate, post-remediate, post-certify, stale-hash-mismatch
2. **[PLANNING]** Create test fixtures with appropriate state files and output artifacts
3. **[EXECUTION]** Write test: post-validate resume → skips to remediate
4. **[EXECUTION]** Write test: post-remediate resume with valid hash → skips to certify
5. **[EXECUTION]** Write test: post-remediate resume with stale hash → re-runs remediate
6. **[EXECUTION]** Write test: post-certify resume → no-op
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "resume"` to verify all resume paths
8. **[COMPLETION]** Record results in `D-0033/evidence.md`

**Acceptance Criteria:**
- All 4 resume scenarios tested and passing
- Stale hash triggers re-execution (fail closed on mismatch)
- Post-certify resume is a no-op
- Resume decisions are gate- and hash-based, not timestamp-only

**Validation:**
- `uv run pytest tests/roadmap/ -k "resume"` exits 0 with all 4 scenarios passing
- Evidence: linkable artifact produced at `D-0033/evidence.md`

**Dependencies:** T06.02 (resume logic), T06.03 (stale hash detection)
**Rollback:** N/A (test suite)

---

### Checkpoint: Phase 6 / Tasks T06.01-T06.04

**Purpose:** Verify state management and resume logic before backward-compatibility testing.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P06-T01-T04.md`
**Verification:**
- State schema fields match spec §3.1 with real values from implementation
- All 4 resume scenarios pass
- Stale hash detection correctly triggers re-execution
**Exit Criteria:**
- Resume from each state produces correct next-step behavior
- No timestamp-only resume decisions
- State writes are atomic and consistent

---

### T06.05 -- Validate Backward Compatibility with Old State Files

| Field | Value |
|---|---|
| Roadmap Item IDs | R-045 |
| Why | Old .roadmap-state.json files without remediate/certify fields must not crash. Additive schema extension validated per SC-008. |
| Effort | XS |
| Risk | High |
| Risk Drivers | schema, breaking |
| Tier | STRICT |
| Confidence | `[█████████-]` 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0034/evidence.md`

**Deliverables:**
- Backward-compatibility test suite verifying old state files (without remediate/certify fields) are handled gracefully

**Steps:**
1. **[PLANNING]** Create fixture: old state file with only steps 1-9 entries (no remediate/certify)
2. **[PLANNING]** Define graceful handling: missing fields default to appropriate values, no exceptions
3. **[EXECUTION]** Write test: load old state file → no crash, missing fields treated as "step not run"
4. **[EXECUTION]** Write test: old state file + --resume → pipeline starts from validate (or earliest incomplete step)
5. **[EXECUTION]** Write test: existing consumers of state file (fidelity_status, steps.validate) still work with new schema
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -k "backward or compat"` to verify all scenarios
7. **[COMPLETION]** Record results in `D-0034/evidence.md`

**Acceptance Criteria:**
- Old state files without remediate/certify fields load without exceptions
- Missing new fields default to "step not run" or equivalent
- Existing consumers (fidelity_status, steps.validate access) unaffected
- `uv run pytest tests/roadmap/ -k "backward or compat"` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/roadmap/ -k "backward or compat"` exits 0
- Evidence: linkable artifact produced at `D-0034/evidence.md`

**Dependencies:** T06.01 (finalized schema)
**Rollback:** N/A (test suite)
**Notes:** Critical Path Override: Yes — models/ path. Tier STRICT + Risk High due to schema/breaking keywords. SC-008 validation.

---

### Checkpoint: End of Phase 6

**Purpose:** Verify full resume support and backward compatibility before integration testing.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P06-END.md`
**Verification:**
- Resume from post-validate, post-remediate, post-certify all work correctly
- Stale hash mismatch triggers re-execution (fail closed)
- Old state files without new fields handled gracefully (no crashes)
**Exit Criteria:**
- All resume scenarios pass (SC-004)
- Backward-compatibility validated (SC-008)
- Resume decisions are gate- and hash-based, not timestamp-only
