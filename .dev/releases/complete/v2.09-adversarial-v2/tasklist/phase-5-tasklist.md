# Phase 5 -- Remaining Protocol Quality & Final Validation

Completes the 6 tasks that were not finished in Phase 4 due to turn exhaustion. Implements the 6th scoring dimension (edge case coverage), extends the return contract, and runs the full end-to-end validation suite (SC-001, SC-003, SC-005–SC-010) confirming the complete v2.07 release is functional and backward compatible.

**Context:** Phase 4 completed T04.01–T04.04 (D-0028–D-0031). The following tasks correspond to the original T04.05–T04.10 and are renumbered T05.01–T05.06. All prior deliverables (D-0001 through D-0031) are available in `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/`.

---

### T05.01 -- Implement 6th qualitative dimension for Invariant & Edge Case Coverage

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Original Task ID | T04.05 |
| Why | AD-3 adds a scoring dimension "Invariant & Edge Case Coverage" with 5 CEV criteria, /30 formula, and floor=1/5 for base variant eligibility, creating incentives for invariant coverage. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (modifies scoring system) |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0032/spec.md
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0032/evidence.md

**Deliverables:**
- 6th qualitative scoring dimension "Invariant & Edge Case Coverage" with 5 CEV criteria, /30 formula, and floor=1/5 requirement for base variant eligibility

**Steps:**
1. **[PLANNING]** Review existing 5 qualitative dimensions in SKILL.md to understand scoring integration point
2. **[PLANNING]** Define 5 CEV criteria for edge case coverage scoring
3. **[EXECUTION]** Implement 6th dimension: add scoring rubric with 5 CEV criteria and /30 formula
4. **[EXECUTION]** Implement floor enforcement: variants scoring <1/5 on edge case dimension are ineligible as base variant
5. **[EXECUTION]** Implement suspension rule: when all variants score 0/5, suspend floor with warning
6. **[VERIFICATION]** Test AC-AD3-1 (24/25 variant with 0/5 edge case floor ineligible) and AC-AD3-2 (scoring differentiates 4/5 from 1/5)
7. **[COMPLETION]** Document scoring dimension and formula in D-0032/spec.md

**Acceptance Criteria:**
- AC-AD3-1 passes: 24/25 variant with 0/5 edge case floor is ineligible as base variant
- AC-AD3-2 passes: scoring differentiates variants with 4/5 from variants with 1/5 edge case coverage
- Floor suspension activates when all variants score 0/5 (with warning)
- Scoring dimension documented in `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0032/spec.md`

**Validation:**
- Manual check: verify scoring with known edge case coverage values; test floor enforcement and suspension
- Evidence: linkable artifact produced (D-0032/spec.md)

**Dependencies:** T04.03 (invariant-probe.md provides coverage data) — COMPLETED in Phase 4
**Rollback:** Remove 6th dimension; revert to 5-dimension scoring

---

### T05.02 -- Extend return contract with `unaddressed_invariants` field

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Original Task ID | T04.06 |
| Why | The return contract must include `unaddressed_invariants` listing HIGH-severity UNADDRESSED items from the invariant probe; existing fields must remain unchanged (NFR-003). |
| Effort | S |
| Risk | Low |
| Risk Drivers | api contract (return contract modification) |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0033/spec.md

**Deliverables:**
- Return contract extension: `unaddressed_invariants` field added listing HIGH-severity UNADDRESSED items; empty list `[]` on success; populated list when HIGH items remain; existing fields unchanged

**Steps:**
1. **[PLANNING]** Review current return contract structure to identify extension point (NFR-003 backward compatibility)
2. **[PLANNING]** Define field schema: `unaddressed_invariants: [{id, category, assumption, severity}]`
3. **[EXECUTION]** Add `unaddressed_invariants` field to return contract output
4. **[EXECUTION]** Populate field from invariant-probe.md: filter HIGH-severity UNADDRESSED items
5. **[VERIFICATION]** Verify: return contract contains `unaddressed_invariants: []` on success; populated list when HIGH items remain; existing fields unchanged
6. **[COMPLETION]** Document field schema in D-0033/spec.md

**Acceptance Criteria:**
- Return contract contains `unaddressed_invariants: []` on successful convergence with no HIGH items
- Return contract contains populated `unaddressed_invariants` list when HIGH-severity UNADDRESSED items exist
- All existing return contract fields are unchanged (NFR-003 compliance)
- Field schema documented in `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0033/spec.md`

**Validation:**
- Manual check: verify return contract output with and without unaddressed invariants
- Evidence: linkable artifact produced (D-0033/spec.md)

**Dependencies:** T04.04 (convergence gate reads invariant data) — COMPLETED in Phase 4
**Rollback:** Remove `unaddressed_invariants` field from return contract

---

### T05.03 -- Run end-to-end SC-001 canonical pipeline with `--blind`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Original Task ID | T04.07 |
| Why | V2 gate: SC-001 validates the complete 8-step pipeline with `--blind` flag, executing all 3 phases end-to-end and producing a merged roadmap with no model-name references (SC-003). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (end-to-end pipeline), performance |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0034/evidence.md

**Deliverables:**
- End-to-end execution pass for SC-001: canonical 8-step `--pipeline "generate:... -> generate:... -> compare --blind"` completes all 3 phases; final output is a merged roadmap with no model-name references

**Steps:**
1. **[PLANNING]** Prepare canonical pipeline definition: `generate:<agent1> -> generate:<agent2> -> compare --blind`
2. **[PLANNING]** Verify all prerequisite components are functional (executor, routing, scheduler, manifest, blind)
3. **[EXECUTION]** Execute canonical pipeline end-to-end with `--blind` flag
4. **[EXECUTION]** Capture pipeline manifest, phase outputs, and merged result
5. **[VERIFICATION]** Verify SC-001: pipeline completes all 3 phases; SC-003: merged output has zero model-name references
6. **[COMPLETION]** Record execution results and evidence in D-0034/evidence.md

**Acceptance Criteria:**
- SC-001 passes: canonical 3-phase pipeline completes end-to-end without errors
- SC-003 passes: merged output contains zero model-name references after `--blind` execution
- Pipeline manifest records all 3 phases as completed with return contracts
- Results documented in `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0034/evidence.md`

**Validation:**
- Manual check: verify pipeline completion and grep merged output for model names
- Evidence: linkable artifact produced (D-0034/evidence.md)

**Dependencies:** T03.04-T03.11 (Phase Execution Engine) — COMPLETED in Phase 3
**Rollback:** N/A (validation task, non-destructive)

---

### T05.04 -- Run full protocol stack validation (SC-005 through SC-009)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Original Task ID | T04.08 |
| Why | V2 gate: all protocol improvements must work simultaneously; SC-005 through SC-009 acceptance suites must pass with >=9 of 10 success criteria and no more than 1 SC at WARN level. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (all protocol improvements active simultaneously) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0035/evidence.md

**Deliverables:**
- Full protocol stack validation report: SC-005 through SC-009 pass with all improvements active; >=9 of 10 success criteria pass; <=1 SC at WARN level

**Steps:**
1. **[PLANNING]** Load SC-005 through SC-009 test scenarios with all protocol improvements enabled
2. **[PLANNING]** Verify all improvements are active: AD-2 (shared assumptions), AD-5 (taxonomy), AD-1 (invariant probe), AD-3 (edge case scoring)
3. **[EXECUTION]** Execute SC-005: v0.04 variant replay with all improvements active
4. **[EXECUTION]** Execute SC-006 through SC-009: run all acceptance assertion suites
5. **[VERIFICATION]** Count passing criteria: verify >=9 of 10 pass; <=1 at WARN level
6. **[COMPLETION]** Record per-SC results in D-0035/evidence.md

**Acceptance Criteria:**
- >=9 of 10 success criteria (SC-001 through SC-010) pass
- No more than 1 SC at WARN level
- All 4 protocol improvements (AD-1, AD-2, AD-3, AD-5) are active simultaneously during validation
- Per-SC results documented in `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0035/evidence.md`

**Validation:**
- Manual check: review per-SC pass/fail/warn status in evidence report
- Evidence: linkable artifact produced (D-0035/evidence.md)

**Dependencies:** T05.01-T05.02 (remaining protocol improvements complete)
**Rollback:** N/A (validation task, non-destructive)

---

### T05.05 -- Measure total overhead (SC-010, <=40% NFR-007)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Original Task ID | T04.09 |
| Why | V2 gate: total overhead with all improvements enabled must not exceed 40% above baseline (NFR-007); if exceeded, AD-3 is the primary deferral candidate. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (overhead measurement) |
| Tier | STANDARD |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0036/evidence.md

**Deliverables:**
- Overhead measurement report: total overhead delta with all improvements enabled, measured empirically against baseline, confirming <=40% (NFR-007)

**Steps:**
1. **[PLANNING]** Define measurement methodology: baseline execution (no improvements) vs full execution (all improvements)
2. **[PLANNING]** Select representative debate input consistent with V1 measurement (T03.03)
3. **[EXECUTION]** Measure baseline: full debate cycle without AD-1/AD-2/AD-3/AD-5 improvements
4. **[EXECUTION]** Measure full: full debate cycle with all improvements enabled
5. **[VERIFICATION]** Calculate total overhead delta; verify <=40% (NFR-007 compliance)
6. **[COMPLETION]** Record measurements in D-0036/evidence.md

**Acceptance Criteria:**
- SC-010 passes: total overhead <=40% above baseline measured empirically
- Measurement includes: baseline tokens, full tokens, delta percentage, per-improvement breakdown
- Report at `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0036/evidence.md` includes methodology and raw data
- If overhead >40%, report identifies AD-3 as primary deferral candidate per roadmap risk register

**Validation:**
- Manual check: verify delta calculation and NFR-007 compliance
- Evidence: linkable artifact produced (D-0036/evidence.md)

**Dependencies:** T05.01-T05.02 (all improvements must be active for measurement)
**Rollback:** N/A (measurement task, non-destructive)

---

### T05.06 -- Run final backward compatibility regression check

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Original Task ID | T04.10 |
| Why | V2 gate: final confirmation that all D1.2 baseline invocations produce unchanged output with the complete v2.07 SKILL.md, ensuring zero regressions in the release candidate. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0037/evidence.md

**Deliverables:**
- Final regression pass report confirming 100% of D1.2 baseline invocations produce unchanged output with complete v2.07 SKILL.md (0 regressions)

**Steps:**
1. **[PLANNING]** Load backward compatibility baseline (D-0002/spec.md from T01.02, located at `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0002/spec.md`)
2. **[PLANNING]** Prepare execution environment with complete v2.07 SKILL.md (all M2-M5 modifications)
3. **[EXECUTION]** Execute each baseline invocation and capture output
4. **[EXECUTION]** Diff each output against documented expected output from baseline
5. **[VERIFICATION]** Confirm 0 regressions: all diffs are empty
6. **[COMPLETION]** Record final regression results in D-0037/evidence.md

**Acceptance Criteria:**
- 100% of D1.2 baseline invocations produce output matching documented baseline with v2.07 SKILL.md
- Zero regressions detected across Mode A and Mode B outputs
- Final report at `.dev/releases/complete/2.09-adversarial-v2/tasklist/artifacts/D-0037/evidence.md` lists all invocations with pass status
- Report explicitly states "Release Candidate: PASS" or "Release Candidate: FAIL"

**Validation:**
- Manual check: review final regression report for any non-empty diffs
- Evidence: linkable artifact produced (D-0037/evidence.md)

**Dependencies:** T01.02 (baseline document) — COMPLETED in Phase 1; T05.01-T05.05 (all modifications and validations complete)
**Rollback:** N/A (validation task, non-destructive)
**Notes:** EXEMPT tier -- read-only validation task comparing outputs against baseline.

---

### Checkpoint: End of Phase 5

**Purpose:** Verify complete v2.07 release is functional: all protocol improvements work simultaneously, end-to-end pipeline passes, overhead is within bounds, and backward compatibility is preserved.
**Checkpoint Report Path:** .dev/releases/complete/2.09-adversarial-v2/tasklist/checkpoints/CP-P05-END.md

**Verification:**
- SC-001 (end-to-end pipeline) and SC-003 (blind evaluation) pass (T05.03)
- SC-005 through SC-009 pass with >=9 of 10 criteria (T05.04)
- SC-010 overhead <=40% (T05.05) and 0 regressions (T05.06)

**Exit Criteria:**
- All 6 Phase 5 tasks completed with deliverables D-0032 through D-0037 produced
- >=9 of 10 success criteria pass; <=1 at WARN level
- Total overhead <=40% (NFR-007) and 0 regressions in final check
