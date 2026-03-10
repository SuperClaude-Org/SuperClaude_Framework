# Phase 6 -- Release Readiness

Final validation that all gates pass, artifacts are consistent, and release criteria are met. This phase produces the release sign-off with evidence for all 14 success criteria and archives final validation results.

### T06.01 -- Run Full Pipeline Validation with All Gates Active

| Field | Value |
|---|---|
| Roadmap Item IDs | R-050 |
| Why | Final validation run confirms no regressions from Phase 5 hardening and verifies gate interaction ordering (reflect → spec-fidelity → tasklist-fidelity). |
| Effort | M |
| Risk | Low |
| Risk Drivers | cross-cutting (end-to-end, pipeline) |
| Tier | EXEMPT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0052 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0052/evidence.md

**Deliverables:**
- Full pipeline validation results with all new and existing gates enabled against representative specs

**Steps:**
1. **[PLANNING]** Select representative specs that exercise all gate types
2. **[PLANNING]** Verify gate interaction ordering: reflect → spec-fidelity → tasklist-fidelity
3. **[EXECUTION]** Execute complete pipeline with all gates active
4. **[EXECUTION]** Record per-gate pass/fail status and total pipeline timing
5. **[VERIFICATION]** Confirm no regressions from Phase 5; gate ordering is correct
6. **[COMPLETION]** Document final validation results with timing baselines

**Acceptance Criteria:**
- Validation results at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0052/evidence.md exist
- Gate interaction ordering verified: reflect → spec-fidelity → tasklist-fidelity
- No regressions from Phase 5 hardening
- Pipeline timing baseline recorded for future regression comparison

**Validation:**
- Manual check: pipeline completes with all gates active; gate order is correct
- Evidence: linkable artifact produced (validation results with timing)

**Dependencies:** Phase 5 complete
**Rollback:** TBD

---

### T06.02 -- Verify and Archive Release Artifacts

| Field | Value |
|---|---|
| Roadmap Item IDs | R-051 |
| Why | All .dev/releases/ outputs must be present, well-formed, and archived alongside final validation results. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0053 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0053/notes.md

**Deliverables:**
- Archived release artifacts with completeness verification

**Steps:**
1. **[PLANNING]** List all expected output artifacts from v2.20 implementation
2. **[PLANNING]** Define completeness criteria for artifact archive
3. **[EXECUTION]** Verify all .dev/releases/ outputs are present and well-formed
4. **[EXECUTION]** Archive final validation results alongside release artifacts
5. **[VERIFICATION]** Confirm deviation reports, state files, and documentation are complete and consistent
6. **[COMPLETION]** Record archive manifest with file list and verification status

**Acceptance Criteria:**
- Archive manifest at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0053/notes.md exists
- All expected artifacts present in .dev/releases/ with non-empty content
- Deviation reports, state files, and documentation verified as consistent
- Final validation results archived alongside release artifacts

**Validation:**
- Manual check: archive manifest lists all expected files with present/missing status
- Evidence: linkable artifact produced (archive manifest)

**Dependencies:** T06.01 (final validation results)
**Rollback:** TBD

---

### T06.03 -- Complete Release Sign-Off Checklist

| Field | Value |
|---|---|
| Roadmap Item IDs | R-052 |
| Why | Release requires documented sign-off with passing evidence for all 14 SC criteria and acknowledgment of known limitations. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0054 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0054/spec.md

**Deliverables:**
- Completed sign-off checklist with passing evidence per SC criterion and known limitations

**Steps:**
1. **[PLANNING]** Compile and cross-reference all 14 SC criteria verification results from prior output-phase artifacts and validation outputs
2. **[PLANNING]** Identify known limitations and deferred items (e.g., FR-012)
3. **[EXECUTION]** Walk through each SC criterion with passing evidence link
4. **[EXECUTION]** Document known limitations: FR-012 multi-agent deferred to v2.21
5. **[EXECUTION]** Record final pipeline timing baselines for future regression comparison
6. **[VERIFICATION]** All 14 criteria have explicit pass evidence
7. **[COMPLETION]** Sign-off checklist complete with date and evidence links

**Acceptance Criteria:**
- Sign-off checklist at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0054/spec.md exists
- All 14 SC criteria listed with pass/fail status and evidence link
- Known limitations documented (FR-012 deferral to v2.21)
- Final pipeline timing baselines recorded

**Validation:**
- Manual check: checklist has 14 entries, all marked pass with evidence
- Evidence: linkable artifact produced (sign-off checklist)

**Dependencies:** T06.01, T06.02, T05.14 (all verification results)
**Rollback:** TBD

---

### T06.04 -- Execute Final Test Suite and Validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-053, R-054 |
| Why | Final confirmation: full test suite passes with 0 failures, E2E pipeline runs clean, all 14 SC criteria independently verified. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0055 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0055/evidence.md

**Deliverables:**
- Final test suite results: 0 failures, all SC criteria verified with evidence

**Steps:**
1. **[PLANNING]** Prepare final test run with all test directories
2. **[PLANNING]** Verify test environment matches production configuration
3. **[EXECUTION]** Run `uv run pytest` for the roadmap-defined complete test suite
4. **[EXECUTION]** Run E2E: full pipeline with all gates active on representative spec
5. **[EXECUTION]** Independently verify all 14 SC-* criteria against evidence
6. **[VERIFICATION]** `uv run pytest` exits 0 with 0 failures
7. **[COMPLETION]** Record final test counts and SC verification evidence

**Acceptance Criteria:**
- `uv run pytest` exits 0 with 0 failures across the roadmap-defined full suite
- E2E pipeline run with all gates active produces clean pass on representative spec
- All 14 SC-* criteria independently verified with evidence links
- No test regressions across entire suite

**Validation:**
- `uv run pytest` — 0 failures
- Evidence: final test output and SC verification matrix

**Dependencies:** T06.01, T06.02, T06.03 (all Phase 6 tasks)
**Rollback:** TBD

---

### Checkpoint: End of Phase 6

**Purpose:** Final release gate confirming all success criteria pass and artifacts are archived.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P06-END.md

**Verification:**
- `uv run pytest` exits 0 with 0 failures
- All 14 SC criteria have documented passing evidence
- Release artifacts archived in .dev/releases/

**Exit Criteria:**
- All D-0052 through D-0055 artifacts created
- All 14 success criteria passing
- No regressions across entire suite
- All artifacts archived in .dev/releases/
- Release sign-off documented with evidence for each criterion
- No known blocking issues remain for v2.20 release
