# Phase 4 -- Edge Cases and Hardening

Address all identified risks, adversarial inputs, and operational edge cases. Full AC matrix passes including adversarial and failure-path scenarios. Proportional attention to failure paths: at least as many failure-path tests as happy-path tests.

---

### T04.01 -- Write edge case tests for boundary conditions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Absent/null/empty `spec_hash`, `.tmp` pre-existence, YAML 1.1 boolean coercion variants, and missing `started_at` must all be tested to satisfy FR-003/006 edge behaviors. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (boundary values), schema (null/empty handling) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0015/evidence.md

**Deliverables:**
- Test cases in `tests/roadmap/test_accept_spec_change.py` for: absent `spec_hash` key in state -> treated as mismatch, null `spec_hash` value -> treated as mismatch, empty string `spec_hash` -> treated as mismatch, pre-existing `.tmp` file -> overwritten (not error), YAML 1.1 boolean variants (`yes`, `on`, `1`, `True`, `TRUE`) all accepted, missing `started_at` -> retry condition not met (fail-closed)

**Steps:**
1. **[PLANNING]** Map each edge case to the specific FR and risk it validates
2. **[PLANNING]** Design fixtures with null, empty, absent `spec_hash` values
3. **[EXECUTION]** Implement test for absent `spec_hash` key -> mismatch behavior
4. **[EXECUTION]** Implement test for null/empty `spec_hash` -> mismatch behavior
5. **[EXECUTION]** Implement test for `.tmp` pre-existence -> overwritten without error
6. **[EXECUTION]** Implement test for missing `started_at` -> fail-closed (retry does not fire)
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "edge or null or empty or tmp or started_at"` -- all pass
8. **[COMPLETION]** Verify edge cases cover all RISK-004/RISK-007 mitigations

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "edge or null or empty or tmp or started_at"` exits 0 with all tests passing
- Absent/null/empty `spec_hash` all produce mismatch behavior (not crash or exception)
- Pre-existing `.tmp` file is silently overwritten during atomic write
- Missing `started_at` in state causes retry condition to evaluate as not-met (fail-closed)

**Validation:**
- `uv run pytest tests/roadmap/test_accept_spec_change.py -v -k "edge or null or empty or tmp or started_at"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T04.01-edge-tests.log

**Dependencies:** T01.04, T03.04
**Rollback:** Remove edge case test functions

---

### T04.02 -- Write failure-path tests for abort and exhaustion scenarios

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Failure paths carry the highest defect risk: atomic write failure abort, persistent spec-fidelity failure after retry, recursion guard block, and state integrity after abort. |
| Effort | M |
| Risk | High |
| Risk Drivers | data (state corruption on failure), rollback (abort path correctness), breaking (stale state if wrong) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0016/evidence.md

**Deliverables:**
- Test cases in `tests/roadmap/test_spec_patch_cycle.py` for: atomic write failure -> cycle abort -> normal halt path (AC-13), persistent spec-fidelity failure after retry -> exit with second-run results (AC-8), recursion guard blocks second retry -> suppression log + exit, state integrity after abort (all keys preserved, mtime unchanged)

**Steps:**
1. **[PLANNING]** Design test fixtures that simulate write failure (e.g., read-only directory, mock `os.replace` failure)
2. **[PLANNING]** Design fixture for persistent spec-fidelity failure (spec change that doesn't resolve the fidelity check)
3. **[EXECUTION]** Implement atomic write failure test: mock `os.replace` to raise `OSError`, verify cycle aborts to normal halt (AC-13)
4. **[EXECUTION]** Implement persistent failure test: trigger retry, make second run also fail, verify `sys.exit(1)` with second-run results (AC-8)
5. **[EXECUTION]** Implement recursion guard block test: trigger condition twice, verify suppression log and exit
6. **[EXECUTION]** Implement state integrity after abort test: verify all non-`spec_hash` keys preserved and mtime unchanged
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "failure or abort or exhaustion or integrity"` -- all pass
8. **[COMPLETION]** Verify failure-path test count is at least equal to happy-path test count

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "failure or abort or exhaustion or integrity"` exits 0 with all tests passing
- Atomic write failure (`os.replace` exception) aborts cycle with error logged to stderr (AC-13)
- Persistent spec-fidelity failure after retry exits with `sys.exit(1)` using second-run results (AC-8)
- State file mtime and non-`spec_hash` keys are unchanged after any abort path

**Validation:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "failure or abort or exhaustion or integrity"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T04.02-failure-tests.log

**Dependencies:** T03.03, T03.04
**Rollback:** Remove failure-path test functions
**Notes:** Architect Recommendation #3: write failure-path tests before or alongside implementation. At least as many failure-path tests as happy-path tests.

---

### T04.03 -- Add TOCTOU and filesystem documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | RISK-001 (single-writer assumption), NFR-005 (operator docs for exclusive access), and RISK-002 (mtime resolution) require prominent documentation in code and operator-facing docs. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0017/spec.md

**Deliverables:**
- Docstring in `spec_patch.py` module header documenting single-writer assumption (RISK-001 mitigation)
- Docstring in `_apply_resume_after_spec_patch()` documenting single-writer assumption
- Code comment in mtime comparison explaining strict `>` rationale and HFS+/NFS mtime-resolution limitation (RISK-002)
- Operator-facing documentation note about exclusive access requirement (NFR-005)

**Steps:**
1. **[PLANNING]** Review RISK-001, RISK-002, NFR-005 requirements from roadmap
2. **[PLANNING]** Identify exact locations for documentation: module docstring, function docstring, inline comment, operator docs
3. **[EXECUTION]** Add single-writer assumption to `spec_patch.py` module docstring prominently
4. **[EXECUTION]** Add single-writer assumption to `_apply_resume_after_spec_patch()` docstring
5. **[EXECUTION]** Add mtime-resolution comment at strict `>` comparison with HFS+/NFS rationale
6. **[VERIFICATION]** Run `grep -n "single.writer\|TOCTOU\|mtime.*resolution\|exclusive.*access" src/superclaude/cli/roadmap/spec_patch.py src/superclaude/cli/roadmap/executor.py` to confirm documentation present
7. **[COMPLETION]** Verify all three risk mitigations are documented

**Acceptance Criteria:**
- `grep -n "single.writer" src/superclaude/cli/roadmap/spec_patch.py` returns at least one match in module docstring
- `grep -n "single.writer" src/superclaude/cli/roadmap/executor.py` returns at least one match in `_apply_resume_after_spec_patch` docstring
- Mtime comparison has inline comment explaining strict `>` rationale and HFS+/NFS limitation
- Operator-facing documentation (in `docs/generated/` or inline CLI help text for `accept-spec-change`) explicitly mentions that `.roadmap-state.json` requires exclusive write access during execution

**Validation:**
- `grep -n "single.writer\|mtime.*resolution" src/superclaude/cli/roadmap/spec_patch.py src/superclaude/cli/roadmap/executor.py`
- Evidence: grep output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T04.03-docs-check.txt

**Dependencies:** T03.06
**Rollback:** Remove added docstrings and comments
**Notes:** Architect Recommendation #4: document single-writer assumption prominently. No locking implementation -- documentation-only mitigation.

---

### T04.04 -- Write state integrity validation tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | State integrity must be verified across all mutation paths: only `spec_hash` changes, abort preserves mtime, and disk-reread state (not in-memory) is passed to `_apply_resume()`. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (state mutation correctness), schema (key preservation) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0018/evidence.md

**Deliverables:**
- Dedicated state integrity tests verifying: (1) only `spec_hash` changes across accept-spec-change happy path, (2) only `spec_hash` changes across auto-resume happy path, (3) abort path leaves mtime unchanged in both CLI and executor paths, (4) `_apply_resume()` receives disk-reread state (mock/spy verification)

**Steps:**
1. **[PLANNING]** Design state snapshots: capture full state before and after each mutation path
2. **[PLANNING]** Design mtime assertion: record mtime before operation, verify equality after abort
3. **[EXECUTION]** Implement test: run accept-spec-change, diff state keys, assert only `spec_hash` changed
4. **[EXECUTION]** Implement test: run auto-resume cycle, diff state keys, assert only `spec_hash` changed
5. **[EXECUTION]** Implement test: abort both CLI and executor paths, assert mtime unchanged
6. **[EXECUTION]** Implement test: mock/spy `_apply_resume()` call, assert argument is post-write disk-read state object (AC-7)
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -v -k "spec_hash or mtime or disk_reread or only_spec_hash or key_preserved"` -- all pass
8. **[COMPLETION]** Record state integrity evidence across all mutation paths

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -v -k "spec_hash or mtime or disk_reread or only_spec_hash or key_preserved"` exits 0 with all tests passing
- State diff after accept-spec-change shows only `spec_hash` key changed; all other keys byte-identical
- State diff after auto-resume cycle shows only `spec_hash` key changed
- Abort paths (both CLI N-answer and executor write-failure) leave file mtime unchanged

**Validation:**
- `uv run pytest tests/roadmap/ -v -k "spec_hash or mtime or disk_reread or only_spec_hash or key_preserved"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T04.04-integrity-tests.log

**Dependencies:** T04.01, T04.02
**Rollback:** Remove state integrity test functions

---

### Checkpoint: End of Phase 4

**Purpose:** Verify all edge cases, failure paths, and state integrity are tested and documented before final validation.
**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/CP-P04-END.md

**Verification:**
- `uv run pytest tests/roadmap/ -v` exits 0 with all unit, integration, edge case, and failure-path tests passing
- Failure-path test count >= happy-path test count in `test_spec_patch_cycle.py`
- Single-writer assumption documented in both `spec_patch.py` and `executor.py`

**Exit Criteria:**
- Full AC matrix (AC-1 through AC-14) covered by automated tests
- All 10 roadmap risks (R1-R10) have corresponding test or documentation mitigation
- State integrity verified across all mutation and abort paths
