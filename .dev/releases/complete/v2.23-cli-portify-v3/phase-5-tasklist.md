# Phase 5 -- Validation & Testing

Verify all success criteria using the 5-category validation taxonomy: structural, behavioral, contract, boundary, and end-to-end. This phase executes the comprehensive validation suite and produces evidence artifacts.

### T05.01 -- Execute Structural Validation Checks (SC-003, SC-004, SC-005)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | The roadmap requires structural validation: SC-003 (zero placeholder sentinels in generated spec), SC-004 (step mapping → FR count match), SC-005 (brainstorm section exists), frontmatter fields present, panel report exists when Phase 4 runs. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0030/evidence.md

**Deliverables:**
1. Structural validation results confirming: SC-003 (zero `{{SC_PLACEHOLDER:}}` sentinels in generated spec), SC-004 (every `step_mapping` entry has corresponding FR), SC-005 (brainstorm section exists in output), frontmatter quality score fields present, panel report exists when Phase 4 runs

**Steps:**
1. **[PLANNING]** List all structural validation checks from roadmap R-039
2. **[PLANNING]** Identify test inputs: a generated spec from a full pipeline run
3. **[EXECUTION]** Run SC-003: regex scan generated spec for `{{SC_PLACEHOLDER:` → expect zero matches
4. **[EXECUTION]** Run SC-004: count `step_mapping` entries and verify each maps to an FR
5. **[EXECUTION]** Run SC-005: verify brainstorm section heading exists in generated spec
6. **[EXECUTION]** Verify frontmatter contains quality score fields; verify `panel-report.md` exists
7. **[VERIFICATION]** All 4 structural checks pass with evidence
8. **[COMPLETION]** Record validation results in evidence artifact

**Acceptance Criteria:**
- SC-003: `grep -c '{{SC_PLACEHOLDER:' <generated-spec>` returns 0
- SC-004: count of `step_mapping` entries equals count of FR references in generated spec
- SC-005: generated spec contains brainstorm section heading
- Frontmatter contains `clarity`, `completeness`, `testability`, `consistency`, `overall` fields; `panel-report.md` exists

**Validation:**
- Manual check: All 4 structural validation checks pass with documented evidence
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0030/evidence.md)

**Dependencies:** T04.05
**Rollback:** TBD (validation-only task, no code changes)

---

### T05.02 -- Execute Behavioral Validation Checks (SC-006, SC-007)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040 |
| Why | The roadmap requires behavioral validation: SC-006 (focus findings per dimension), SC-007 (all 4 quality scores present), brainstorm findings follow required schema, zero-gap path produces correct summary, additive-only incorporation respected. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0031/evidence.md

**Deliverables:**
1. Behavioral validation results confirming: SC-006 (focus pass produces findings for both correctness and architecture dimensions), SC-007 (all 4 quality scores present and typed as floats), brainstorm findings follow `{gap_id, description, severity, affected_section, persona}` schema, zero-gap path produces "No gaps identified" summary, additive-only incorporation adds no rewrites

**Steps:**
1. **[PLANNING]** List all behavioral validation checks from roadmap R-040
2. **[PLANNING]** Identify test scenarios: normal run, zero-gap run, high-CRITICAL run
3. **[EXECUTION]** Run SC-006: verify focus pass output contains findings for `correctness` and `architecture` dimensions
4. **[EXECUTION]** Run SC-007: verify critique pass output contains all 4 quality scores as floats
5. **[EXECUTION]** Verify brainstorm findings match schema with all 5 required fields
6. **[EXECUTION]** Test zero-gap path: inject spec with no gaps → verify "No gaps identified" summary and `gaps_identified: 0`
7. **[VERIFICATION]** Verify additive-only: diff before/after incorporation shows only appends, no line removals
8. **[COMPLETION]** Record all behavioral validation results

**Acceptance Criteria:**
- SC-006: focus pass output contains findings tagged with both `correctness` and `architecture` dimensions
- SC-007: critique pass output contains `clarity`, `completeness`, `testability`, `consistency` as float values
- Brainstorm findings contain all 5 fields: `gap_id`, `description`, `severity`, `affected_section`, `persona`
- Zero-gap path produces explicit "No gaps identified" summary with `gaps_identified: 0` contract field
- Additive-only incorporation is verified: incorporation diffs append or extend content without rewrites or removals

**Validation:**
- Manual check: All behavioral checks pass with evidence for normal, zero-gap, and additive-only scenarios
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0031/evidence.md)

**Dependencies:** T05.01
**Rollback:** TBD (validation-only task, no code changes)

---

### T05.03 -- Execute Contract Validation Checks (SC-009, SC-010, SC-013, SC-014)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-041 |
| Why | The roadmap requires contract validation: SC-009 (contract emitted on all paths), SC-010 (quality formula correctness), SC-013 (phase timing populated), SC-014 (removed flag rejected), resume substep populated on resumable failures. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (contract completeness across paths) |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0032/evidence.md

**Deliverables:**
1. Contract validation results confirming: SC-009 (contract emitted on success, partial, failure, and dry-run paths), SC-010 (`overall == mean(clarity, completeness, testability, consistency)`), SC-013 (`phase_3_seconds` and `phase_4_seconds` populated for completed phases), SC-014 (`--skip-integration` flag returns error), resume substep populated on resumable failures

**Steps:**
1. **[PLANNING]** List all contract validation paths: success, partial, failure (7 types), dry-run
2. **[PLANNING]** Prepare test scenarios for each path
3. **[EXECUTION]** Run SC-009: verify contract emitted on all 4 path categories (success, partial, failure, dry-run)
4. **[EXECUTION]** Run SC-010: compute `mean(clarity, completeness, testability, consistency)` and verify equals `overall`
5. **[EXECUTION]** Run SC-013: verify `phase_3_seconds` and `phase_4_seconds` are populated after completed phases
6. **[EXECUTION]** Run SC-014: pass `--skip-integration` flag and verify it is rejected with error
7. **[VERIFICATION]** Verify resume substep: interrupt Phase 4, verify `resume_substep=4a` in contract
8. **[COMPLETION]** Record contract validation results with snapshots

**Acceptance Criteria:**
- SC-009: contract present in output for all 4 path categories with complete schema
- SC-010: `overall` field equals arithmetic mean of `clarity`, `completeness`, `testability`, `consistency`
- SC-013: `phase_3_seconds` and `phase_4_seconds` contain numeric values > 0 after phase completion
- SC-014: `--skip-integration` flag rejected with error message; resume substep populated on resumable failures only (`brainstorm_failed` → `3c`, `focus_failed` → `4a`)

**Validation:**
- Manual check: Contract snapshots collected for success, failure, and dry-run paths with formula verification
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0032/evidence.md)

**Dependencies:** T05.01, T05.02
**Rollback:** TBD (validation-only task, no code changes)

---

### T05.04 -- Execute Boundary Validation Checks (SC-012, SC-008)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042 |
| Why | The roadmap requires boundary validation: SC-012 (`overall = 7.0` → downstream-ready true, `overall = 6.9` → false), SC-008 (no unaddressed CRITICALs after <=3 iterations), mid-panel failure sets scores to `0.0`, iteration limit reached at 3. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (boundary behavior correctness) |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0033/evidence.md

**Deliverables:**
1. Boundary validation results confirming: SC-012 (`overall = 7.0` → `downstream_ready: true`, `overall = 6.9` → `downstream_ready: false`), SC-008 (no unaddressed CRITICALs after <=3 convergence iterations), mid-panel failure sets all quality scores to `0.0`, iteration limit terminates at exactly 3

**Steps:**
1. **[PLANNING]** Define boundary test cases: exact threshold (7.0), below threshold (6.9), mid-panel failure, max iterations
2. **[PLANNING]** Prepare test inputs that exercise each boundary
3. **[EXECUTION]** Test SC-012: set `overall = 7.0` → verify `downstream_ready: true`
4. **[EXECUTION]** Test SC-012: set `overall = 6.9` → verify `downstream_ready: false`
5. **[EXECUTION]** Test SC-008: force CRITICALs → verify convergence loop runs <=3 iterations then terminates
6. **[EXECUTION]** Test mid-panel failure: interrupt during Phase 4 → verify all quality scores = `0.0`
7. **[VERIFICATION]** All boundary values produce correct boolean/numeric results
8. **[COMPLETION]** Record boundary test results

**Acceptance Criteria:**
- `overall = 7.0` produces `downstream_ready: true`; `overall = 6.9` produces `downstream_ready: false`
- Convergence loop with persistent CRITICALs terminates after exactly 3 iterations with `status: partial`
- Mid-panel failure sets all quality scores to `0.0` (not null) and `downstream_ready: false`
- Iteration counter increments correctly: 1, 2, 3, then ESCALATED

**Validation:**
- Manual check: Boundary values 7.0/6.9 produce correct downstream_ready booleans; convergence terminates at 3
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0033/evidence.md)

**Dependencies:** T05.03
**Rollback:** TBD (validation-only task, no code changes)

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.04

**Purpose:** Verify all 4 validation categories (structural, behavioral, contract, boundary) pass before E2E testing.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P05-T01-T04.md
**Verification:**
- Structural validation: zero sentinels, step mapping matches, brainstorm exists
- Behavioral validation: focus findings per dimension, quality scores present, additive-only respected
- Contract validation: emitted on all paths, formula correct, timing populated, flag rejected
**Exit Criteria:**
- Tasks T05.01-T05.04 completed with deliverables D-0030 through D-0033 produced
- Zero test failures across structural, behavioral, contract, and boundary categories
- All SC-### success criteria verified with evidence

---

### T05.05 -- Execute End-to-End Validation Checks (SC-001, SC-002, SC-011)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-043, R-044 |
| Why | The roadmap requires E2E validation: SC-001 (full portify run → reviewed spec + panel report), SC-002 (dry run stops after Phase 2), SC-011 (downstream handoff → spec consumed by sc:roadmap), convergence loop forced CRITICALs test, resume test, low-quality spec recovery, and brainstorm timeout handling. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end (cross-cutting scope), breaking (integration correctness) |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034, D-0035 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0034/evidence.md
- TASKLIST_ROOT/artifacts/D-0035/evidence.md

**Deliverables:**
1. End-to-end validation results: SC-001 (full portify run produces reviewed spec + panel report), SC-002 (dry run stops after Phase 2 with only Phase 0-2 contracts), SC-011 (generated spec consumed by `sc:roadmap` downstream), convergence loop CRITICALs forced <=3 iterations, resume from `resume_substep` works, low-quality spec triggers brainstorm gap detection and panel flagging
2. Validation evidence package: test output logs, contract snapshots for success and failure paths, generated spec sample, panel report sample, downstream consumption proof

**Steps:**
1. **[PLANNING]** Define E2E test scenarios: full run, dry run, downstream handoff, forced CRITICALs, resume, low-quality input, brainstorm timeout
2. **[PLANNING]** Prepare test inputs for each scenario
3. **[EXECUTION]** SC-001: Execute full portify run → verify reviewed spec and `panel-report.md` produced
4. **[EXECUTION]** SC-002: Execute with `--dry-run` → verify stops after Phase 2 with only Phase 0-2 contracts
5. **[EXECUTION]** SC-011: Feed generated spec to `sc:roadmap` → verify downstream consumption succeeds
6. **[EXECUTION]** Convergence: force CRITICALs → verify <=3 iteration termination with `status: partial`
7. **[EXECUTION]** Resume: interrupt mid-Phase 4 → verify `resume_substep=4a` works to restart Phase 4
8. **[EXECUTION]** Low-quality recovery: introduce gaps in Phase 2 output → verify brainstorm catches gaps and panel flags them
9. **[VERIFICATION]** Collect evidence: test output logs, contract snapshots, spec sample, panel report sample, downstream proof
10. **[COMPLETION]** Assemble complete validation evidence package

**Acceptance Criteria:**
- SC-001: full portify run produces reviewed spec file and `panel-report.md` in working directory
- SC-002: `--dry-run` produces only Phase 0-2 contracts, no Phase 3/4 artifacts
- SC-011: generated spec successfully consumed by `sc:roadmap` as input (downstream interoperability confirmed)
- Validation evidence package contains: test output logs, contract snapshots (success + failure), generated spec sample, panel report sample, downstream consumption proof; this timeout validation scenario follows the roadmap's E2E wording and emits `failure_type=brainstorm_failed` with `resume_substep=3c`, while the broader contract schema separately retains `brainstorm_timeout` as an enumerated failure type

**Validation:**
- Manual check: All 7 E2E scenarios pass — full run, dry run, downstream, convergence, resume, low-quality recovery, timeout
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0034/evidence.md, TASKLIST_ROOT/artifacts/D-0035/evidence.md)

**Dependencies:** T05.01, T05.02, T05.03, T05.04
**Rollback:** TBD (validation-only task, no code changes)

---

### Checkpoint: End of Phase 5

**Purpose:** Verify all 14 success criteria (SC-001 through SC-014) are validated with evidence, covering structural, behavioral, contract, boundary, and end-to-end categories.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P05-END.md
**Verification:**
- All 14 SC-### success criteria validated with pass status
- Validation evidence package complete: logs, contract snapshots, spec sample, panel report, downstream proof
- Zero unaddressed test failures across all 5 validation categories
**Exit Criteria:**
- All 5 tasks (T05.01-T05.05) completed with deliverables D-0030 through D-0035 produced
- Complete validation evidence package assembled
- Downstream interoperability (sc:roadmap consuming generated spec) confirmed
