---
spec_source: v2.25-spec-merged.md
complexity_score: 0.92
primary_persona: analyzer
---

# 1. Executive summary

This roadmap addresses an enterprise-complexity pipeline upgrade that introduces two new control points—`annotate-deviations` and `deviation-analysis`—to prevent deviation laundering, improve remediation targeting, and preserve backward compatibility without changing generic executor primitives.

## Analyzer assessment

1. **Primary delivery objective**
   - Convert the v4 fidelity/remediation flow into a **classification-driven v5 flow** that:
     1. distinguishes intentional changes from actual slips,
     2. routes only actionable slips into remediation,
     3. enforces fail-closed integrity checks,
     4. halts safely when ambiguity or repeated remediation failure persists.

2. **Why this is high risk**
   - The change surface spans **7 technical domains**, **115 total requirements**, **9 risks**, and **14 dependencies**.
   - The most failure-prone areas are:
     - gate semantics,
     - artifact integrity/freshness,
     - resume correctness,
     - parsing robustness,
     - backward compatibility of `Finding` consumers.

3. **Delivery strategy**
   - Implement in **5 tightly scoped phases** with mandatory checkpoints.
   - Resolve open architecture decisions **before coding**.
   - Validate each phase with unit and integration tests before enabling the next.
   - Treat `deviation-analysis` and freshness invalidation as the highest-risk integration points.

4. **Recommended execution principle**
   - Prioritize **correctness and observability over speed**.
   - This spec introduces new blocking semantics; an incorrect implementation can silently corrupt pipeline decisions. Validation depth should therefore exceed normal feature work.

---

# 2. Phased implementation plan with milestones

## Phase 0 — Pre-implementation decisions and baselining

### Goals
Establish implementation constraints, resolve deferred decisions, and freeze the intended architecture before modifying behavior.

### Scope
1. Resolve open questions that materially affect implementation:
   - **OQ-A / OQ-B**: decide whether `GateCriteria.aux_inputs` exists and whether FR-079 / FR-088 use Option A or Option B.
   - **OQ-C**: define how `PRE_APPROVED` IDs are extracted for gate validation.
   - **OQ-E / OQ-F**: confirm or define `_extract_fidelity_deviations()` and `_extract_deviation_classes()`.
   - **OQ-G / OQ-H / OQ-I**: confirm `build_remediate_step()`, `roadmap_run_step()`, and token-count access.
   - **OQ-J**: document v2.25 handling for FR-077 note behavior.

2. Confirm architecture constraints against the codebase:
   - no modifications to generic pipeline layer,
   - no new executor primitives,
   - no normal execution reads of `dev-*-accepted-deviation.md`,
   - module dependency hierarchy remains acyclic.

3. Produce an implementation mapping:
   - requirement → file(s) → test(s) → milestone.

### Deliverables
- Implementation decision log.
- Requirement traceability matrix.
- Confirmed module ownership map.
- Test plan aligned to SC-1 through SC-10.

### Milestone
- **M0: Architecture freeze approved**
  - All blocking open questions resolved or explicitly deferred with documented fallback behavior.

### Exit criteria
- No unresolved decision remains that could force rework in gates, parsing, or executor resume flow.

### Timeline estimate
- **Effort:** 0.5–1.5 engineering days

---

## Phase 1 — Data model, parsing, and gate foundation

### Goals
Build the fail-closed foundation needed by the new pipeline artifacts and routing logic.

### Scope
1. **Model updates**
   - Add `deviation_class: str = "UNCLASSIFIED"` to `Finding`.
   - Add `VALID_DEVIATION_CLASSES`.
   - Enforce validation in `Finding.__post_init__()`.

2. **Frontmatter and parsing hardening**
   - Make `_parse_frontmatter()` public as `parse_frontmatter()`.
   - Ensure downstream callers are updated.
   - Implement or place `_parse_routing_list()` to avoid circular imports.
   - Enforce `DEV-\d+` token validation and whitespace stripping.

3. **New semantic checks in `gates.py`**
   - `_certified_is_true()`
   - `_validation_complete_true()`
   - `_routing_consistent_with_slip_count()`
   - `_routing_ids_valid()`
   - `_pre_approved_not_in_fix_roadmap()`
   - `_slip_count_matches_routing()`
   - `_total_annotated_consistent()`
   - `_total_analyzed_consistent()`

4. **Gate definitions**
   - Add `ANNOTATE_DEVIATIONS_GATE`.
   - Add `DEVIATION_ANALYSIS_GATE`.
   - Downgrade `SPEC_FIDELITY_GATE` to STANDARD.
   - Retain deprecated semantic check functions with `[DEPRECATED v2.25]` docstrings.
   - Append `certified_true` to `CERTIFY_GATE`.
   - Update `ALL_GATES`.

### Deliverables
- Updated `models.py`
- Updated `gates.py`
- Public frontmatter parsing API
- Routing validation utilities

### Milestone
- **M1: Fail-closed validation layer complete**
  - All new artifact schemas and gate semantics exist and are testable independently.

### Analyzer focus areas
- Distinguish **missing**, **malformed**, and **failing-value** cases in integer parsing logs.
- Validate order of semantic checks, not just their existence.
- Confirm new defaults do not break old `Finding` constructors.

### Exit criteria
- Unit tests cover all new check functions, invalid routing tokens, malformed frontmatter, and default compatibility.

### Timeline estimate
- **Effort:** 1.5–3 engineering days

---

## Phase 2 — Prompt and artifact generation integration

### Goals
Introduce the two new artifacts and wire them into the step graph without breaking existing step semantics.

### Scope
1. **Annotate deviations prompt integration**
   - Add prompt builder behavior that reads the **original spec file**, not `extraction.md`.
   - Enforce required deviation classes:
     - `INTENTIONAL_IMPROVEMENT`
     - `INTENTIONAL_PREFERENCE`
     - `SCOPE_ADDITION`
     - `NOT_DISCUSSED`
   - Enforce exact citation requirements for intentional improvement.
   - Ensure `spec-deviations.md` schema includes:
     - `schema_version: "2.25"` first,
     - counts,
     - `roadmap_hash`.

2. **Spec fidelity prompt update**
   - Add `spec_deviations_path: Path | None = None`.
   - Implement verification instructions for annotated intentional improvements.
   - Ensure invalid annotations are promoted to HIGH severity.
   - Ensure `NOT_DISCUSSED` items are independently analyzed.

3. **Deviation analysis prompt integration**
   - Add classification into:
     - `PRE_APPROVED`
     - `INTENTIONAL`
     - `SLIP`
     - `AMBIGUOUS`
   - Implement routing outputs:
     - `routing_fix_roadmap`
     - `routing_update_spec`
     - `routing_no_action`
     - `routing_human_review`
   - Include bounded blast-radius analysis for intentional deviations.
   - Add `routing_intent` distinction (`superior` vs `preference`).
   - Add `Spec Update Recommendations` subsection when needed.

4. **Step graph updates**
   - Insert `annotate-deviations` between `merge` and `test-strategy`.
   - Insert `deviation-analysis` after `spec-fidelity`.
   - Update `_build_steps()`.
   - Update `_get_all_step_ids()`.

### Deliverables
- Updated prompt builders
- Step registration updates
- Artifact schema compliance for both new outputs

### Milestone
- **M2: New v5 artifacts generated in correct pipeline order**
  - Pipeline can produce `spec-deviations.md` and `deviation-analysis.md` with required frontmatter and body structure.

### Analyzer focus areas
- The strongest integrity requirement here is **anti-laundering**.
- Prompt wording must be unambiguous on:
  - exact citation requirements,
  - classification exclusivity,
  - routing consequences,
  - prohibition on architectural-quality inference as proof of intentionality.

### Exit criteria
- Prompt-level golden tests or fixture assertions confirm required instructions and expected schema fields.

### Timeline estimate
- **Effort:** 2–3.5 engineering days

---

## Phase 3 — Executor, state, resume, and artifact freshness

### Goals
Make the new flow operational under real pipeline execution and safe under repeated `--resume`.

### Scope
1. **Artifact integrity**
   - Inject `roadmap_hash` into `spec-deviations.md` after sanitization using SHA-256.
   - Use atomic write pattern `.tmp` + `os.replace()`.

2. **Freshness and resume correctness**
   - Implement `_check_annotate_deviations_freshness()` as fail-closed.
   - Ensure `_apply_resume()`:
     - checks freshness before skipping `annotate-deviations`,
     - re-adds `annotate-deviations` when stale,
     - resets pass-state for `spec-fidelity` and `deviation-analysis` when needed.

3. **State management**
   - Add `remediation_attempts` to `.roadmap-state.json`.
   - Coerce attempts to `int` safely on read/increment.
   - Record `started_at`, `completed_at`, and best-effort `token_count` for both new steps.
   - Ensure atomic state writes.

4. **Retirement / dormancy handling**
   - Retire or disable spec-patch auto-resume behavior per FR-059 while preserving required compatibility behavior from NFRs.
   - Keep remediation budget independent from spec-patch counters.

5. **Terminal halt behavior**
   - Implement `_check_remediation_budget()` with max 2 attempts.
   - Ensure `_print_terminal_halt()` outputs:
     - attempts used,
     - remaining failing findings,
     - per-finding detail,
     - certification report path,
     - resume/manual-fix guidance.
   - Ensure caller owns `sys.exit(1)`.

### Deliverables
- Updated `executor.py`
- Atomic write handling
- Freshness invalidation logic
- Resume-safe state persistence

### Milestone
- **M3: Resume-safe v5 execution flow complete**
  - Pipeline can skip valid steps, rerun stale ones, and halt deterministically when recovery is exhausted.

### Analyzer focus areas
- This is the **highest regression-risk phase**.
- Most likely hidden failures:
  1. stale `spec-deviations.md` incorrectly reused,
  2. remediation attempts miscounted,
  3. state corruption on interrupted writes,
  4. downstream gates not invalidated when annotate freshness fails.

### Exit criteria
- All specified freshness test cases pass.
- Resume behavior verified across:
  - fresh resume,
  - stale roadmap hash,
  - exhausted remediation budget,
  - malformed state file attempt values.

### Timeline estimate
- **Effort:** 2–4 engineering days

---

## Phase 4 — Remediation routing and downstream behavior

### Goals
Ensure only valid slips become findings and only those findings drive remediation.

### Scope
1. **Routing to findings**
   - Implement `deviations_to_findings()`.
   - Convert only `fix_roadmap` deviations into `Finding` objects.
   - Severity mapping:
     - `HIGH` → `BLOCKING`
     - `MEDIUM` → `WARNING`
     - `LOW` → `INFO`
   - Exclude `no_action` and `update_spec`.
   - Raise `ValueError` when routing is empty despite positive `slip_count` after gate pass.
   - Warn when routing IDs are missing from fidelity output.

2. **Remediate prompt behavior**
   - Shift primary source from `spec-fidelity.md` to `deviation-analysis.md`.
   - Instruct agent to fix only SLIPs.
   - Explicitly prohibit modification of `INTENTIONAL` and `PRE_APPROVED` items.

3. **Certify behavior alignment**
   - Ensure certification properly blocks on `certified: false`.
   - Ensure manual-fix recovery path works after repeated failure.

### Deliverables
- Updated `remediate.py`
- Updated `remediate_prompts.py`
- Downstream remediation/certify flow aligned with v5 classification logic

### Milestone
- **M4: Action routing correctness proven**
  - Only actionable slips are remediated; intentional/pre-approved items are preserved.

### Analyzer focus areas
- The key validation is **negative validation**:
  - prove that intentional deviations are **not** changed.
- This phase should include before/after roadmap diffs as evidence, not just passing tests.

### Exit criteria
- Controlled fixture runs show:
  - SLIPs routed correctly,
  - intentional items excluded,
  - certify blocks on false certification,
  - halt behavior triggers after 2 failed attempts.

### Timeline estimate
- **Effort:** 1.5–3 engineering days

---

## Phase 5 — End-to-end validation, hardening, and release readiness

### Goals
Validate the entire v5 pipeline against the reference v2.24 scenario and ensure release safety.

### Scope
1. **Unit test completion**
   - Gates
   - routing parsing
   - finding conversion
   - certification check
   - freshness logic
   - state coercion and atomic writes

2. **Integration test completion**
   - Add/complete `tests/roadmap/test_integration_v5_pipeline.py`
   - Use prerecorded/mock subprocess outputs
   - Verify SC-1 through SC-10

3. **Manual validation run**
   - Replay v2.24 scenario end to end.
   - Inspect generated artifacts:
     - `spec-deviations.md`
     - `spec-fidelity.md`
     - `deviation-analysis.md`
     - certification output
     - terminal halt behavior

4. **Release safeguards**
   - Diff check on prohibited files:
     - generic pipeline layer unchanged,
     - sprint pipeline unaffected.
   - Compatibility review for `.roadmap-state.json` and old `Finding` callers.

### Deliverables
- Passing unit/integration suite
- Manual validation evidence package
- Release-readiness checklist

### Milestone
- **M5: Production release candidate**
  - All success criteria met with evidence.

### Analyzer focus areas
- Require evidence for every success criterion, not narrative confirmation.
- Release should be blocked if any of the following remain unverified:
  - ambiguity halting,
  - routing semantics,
  - freshness invalidation,
  - certification hard fail,
  - backward compatibility.

### Exit criteria
- SC-1 through SC-10 explicitly marked verified with test or artifact references.

### Timeline estimate
- **Effort:** 2–3 engineering days

---

# 3. Risk assessment and mitigation strategies

## A. High-priority delivery risks

### 1. Deviation laundering / over-approval
- **Source:** R-1, R-2
- **Impact:** False intentional classifications reduce real defect counts and bypass remediation.
- **Mitigation**
  1. Require exact debate citation (`D-XX`, round number).
  2. Treat missing citation as `NOT_DISCUSSED`.
  3. Revalidate intentional improvement claims in `spec-fidelity`.
  4. Promote invalid annotations to HIGH severity.
- **Control owner:** Prompt + gate + fidelity logic
- **Validation evidence**
  - negative tests for bogus citations,
  - fixture cases where intentional claims are rejected.

### 2. Resume and freshness corruption
- **Source:** R-6, FR-071, FR-084
- **Impact:** Stale `spec-deviations.md` causes invalid downstream decisions.
- **Mitigation**
  1. Inject `roadmap_hash` atomically.
  2. Fail closed on missing/malformed freshness inputs.
  3. Reset downstream pass-state when annotate freshness fails.
- **Control owner:** Executor/state logic
- **Validation evidence**
  - all 9 freshness tests,
  - integration test with changed `roadmap.md`.

### 3. Routing/frontmatter parsing fragility
- **Source:** R-9
- **Impact:** Valid slips fail to remediate, or invalid IDs silently pass.
- **Mitigation**
  1. Use flat comma-separated routing fields only.
  2. Strip whitespace and validate all IDs with regex.
  3. Gate on routing consistency when `slip_count > 0`.
  4. Add defense-in-depth `ValueError` in `deviations_to_findings()`.
- **Control owner:** Gates + remediate parser
- **Validation evidence**
  - malformed token tests,
  - empty routing with slips tests,
  - token-presence cross-check tests.

## B. Medium-priority delivery risks

### 4. Ambiguity handling not enforced
- **Impact:** pipeline continues with unresolved operator decisions.
- **Mitigation**
  1. STRICT gate blocks on `ambiguous_count > 0`.
  2. Document operator manual reclassification flow.
- **Validation evidence**
  - gate failure test,
  - resume-after-manual-fix scenario.

### 5. Remediation non-convergence
- **Impact:** repeated automated cycles waste time and obscure operator action.
- **Mitigation**
  1. cap remediation at 2 attempts,
  2. halt with detailed manual-fix instructions,
  3. keep budget independent from spec-patch counters.
- **Validation evidence**
  - integration test with failing certify mock,
  - stderr assertion coverage.

### 6. Backward compatibility drift
- **Impact:** old consumers fail unexpectedly.
- **Mitigation**
  1. keep `deviation_class` default safe,
  2. avoid changing generic pipeline layer,
  3. preserve existing state compatibility with missing `remediation_attempts`.
- **Validation evidence**
  - constructor compatibility tests,
  - state migration tests,
  - static diff review.

## C. Low-priority but certain risk

### 7. Pipeline runtime increase
- **Source:** R-3
- **Impact:** additional run time due to two new steps.
- **Mitigation**
  1. cap each new step at 300s,
  2. emphasize net savings on failure paths,
  3. capture timing data for both steps.
- **Validation evidence**
  - step duration metrics in state file,
  - observed run delta during validation.

---

# 4. Resource requirements and dependencies

## Team roles

1. **Primary engineer**
   - Owns prompt, gates, executor, remediation integration.
2. **QA/test engineer**
   - Owns unit/integration fixture design and success-criteria verification.
3. **Reviewer with architecture context**
   - Validates open question resolutions and module-boundary compliance.

## Required code areas

1. `src/superclaude/cli/roadmap/prompts.py`
2. `src/superclaude/cli/roadmap/gates.py`
3. `src/superclaude/cli/roadmap/executor.py`
4. `src/superclaude/cli/roadmap/models.py`
5. `src/superclaude/cli/roadmap/remediate.py`
6. `src/superclaude/cli/roadmap/remediate_prompts.py`
7. `src/superclaude/cli/roadmap/fidelity.py`
8. Potentially `src/superclaude/cli/roadmap/parsing.py`

## External/runtime dependencies

1. **Claude subprocess API**
   - Needed for both new pipeline steps.
   - Token-count availability is best-effort and must be confirmed.

2. **Stdlib dependencies**
   - `hashlib`
   - `os`
   - `re`
   - `json`

3. **State/artifact dependencies**
   - `.roadmap-state.json`
   - `spec-deviations.md`
   - `deviation-analysis.md`

## Test dependencies

1. New or expanded test coverage in:
   - `tests/roadmap/test_integration_v5_pipeline.py`
   - `tests/roadmap/test_executor.py`
   - `tests/roadmap/test_gates_data.py`
   - routing/fidelity/remediation unit tests

## Dependency management priorities

1. **Must confirm first**
   - `aux_inputs` availability
   - public frontmatter parser migration
   - existing extraction helpers/signatures
   - post-step hook location for roadmap hash injection

2. **Can be implemented in parallel**
   - model updates,
   - most gate checks,
   - prompt schema updates,
   - test fixtures for artifact validation.

3. **Must be sequenced**
   - gate foundation before prompt/generator integration,
   - prompt integration before resume logic,
   - executor freshness before end-to-end validation.

---

# 5. Success criteria and validation approach

## Validation strategy

Use a **three-layer validation model**:

1. **Unit validation**
   - Semantic checks
   - parsing behavior
   - model validation
   - routing conversion
   - state coercion

2. **Integration validation**
   - step ordering
   - resume behavior
   - remediation budget
   - certification blocking
   - end-to-end routing behavior

3. **Artifact inspection**
   - verify frontmatter shape,
   - verify schema version ordering,
   - verify routing contents,
   - verify before/after roadmap diffs.

## Success criteria mapping

### SC-1 — Pipeline reaches certify without halting at spec-fidelity
- **Validation**
  - integration test replay and manual validation run.
- **Evidence**
  - run logs,
  - state progression,
  - certify reached.

### SC-2 — Intentional deviations D-02 and D-04 are pre-approved
- **Validation**
  - inspect `spec-deviations.md`, `spec-fidelity.md`, `deviation-analysis.md`.
- **Evidence**
  - D-02 and D-04 cited, verified, excluded from HIGH, routed to `no_action`.

### SC-3 — DEV-002 and DEV-003 route to `fix_roadmap`
- **Validation**
  - inspect `deviation-analysis.md` routing fields.
- **Evidence**
  - IDs present,
  - `ambiguous_count == 0`.

### SC-4 — Remediation modifies only SLIPs
- **Validation**
  - roadmap diff before/after remediation.
- **Evidence**
  - changed sections map only to slip IDs.

### SC-5 — Certify blocks on `certified: false`
- **Validation**
  - unit tests for `_certified_is_true()`.
- **Evidence**
  - explicit pass/fail cases.

### SC-6 — Halt after 2 failed remediation attempts
- **Validation**
  - failing-certify integration test.
- **Evidence**
  - `sys.exit(1)`,
  - stderr details,
  - resume instructions present.

### SC-7 — No new executor primitives
- **Validation**
  - static diff review.
- **Evidence**
  - zero new classes in generic pipeline layer.

### SC-8 — Freshness checker passes all required cases
- **Validation**
  - executor test suite.
- **Evidence**
  - 100% pass on specified cases.

### SC-9 — `DEVIATION_ANALYSIS_GATE` enforces all semantic checks
- **Validation**
  - targeted gate tests.
- **Evidence**
  - pass/fail boundary coverage for each check.

### SC-10 — Both artifacts include `schema_version: "2.25"` first
- **Validation**
  - artifact inspection from integration/manual run.
- **Evidence**
  - frontmatter ordering assertions.

## Recommended quality gates before release

1. All unit tests green.
2. All integration tests green.
3. Manual v2.24 replay reviewed.
4. No unresolved ambiguity in test artifacts.
5. No prohibited file modifications.
6. No unverified open question left in code comments or docs.

---

# 6. Timeline estimates per phase

## Recommended delivery cadence

1. **Phase 0 — Pre-implementation decisions**
   - **Estimate:** 0.5–1.5 days
   - **Output:** architecture freeze, resolved open questions, traceability matrix

2. **Phase 1 — Data model, parsing, and gate foundation**
   - **Estimate:** 1.5–3 days
   - **Output:** fail-closed validation layer complete

3. **Phase 2 — Prompt and artifact generation integration**
   - **Estimate:** 2–3.5 days
   - **Output:** new artifacts generated with correct schema and step ordering

4. **Phase 3 — Executor, state, resume, and freshness**
   - **Estimate:** 2–4 days
   - **Output:** resume-safe, freshness-aware execution flow

5. **Phase 4 — Remediation routing and downstream behavior**
   - **Estimate:** 1.5–3 days
   - **Output:** actionable slips only flow into remediation/certify

6. **Phase 5 — End-to-end validation and release readiness**
   - **Estimate:** 2–3 days
   - **Output:** verified release candidate with SC-1 to SC-10 evidence

## Total estimate
- **Implementation-only effort band:** 9.5–17 days
- **Recommended release target:** proceed only after Phase 5 evidence review, not on code-complete status alone

## Timeline risk factors that may expand effort
1. unresolved `aux_inputs` decision,
2. missing helper definitions for fidelity/deviation extraction,
3. unexpected executor hook complexity for roadmap hash injection,
4. fragile fixture generation for v2.24 replay scenarios.

---

# 7. Recommended execution order and parallelization plan

## Sequential work
1. Phase 0 decisions
2. Phase 1 gate/parsing foundation
3. Phase 2 prompt/step integration
4. Phase 3 executor/state/freshness
5. Phase 4 remediation routing
6. Phase 5 end-to-end validation

## Parallelizable work
1. While Phase 1 is in progress:
   - draft unit tests for new gate functions,
   - prepare fixture schemas for new artifacts.

2. While Phase 2 is in progress:
   - build golden artifact samples,
   - write body/frontmatter schema assertions.

3. While Phase 3 is in progress:
   - prepare resume/freshness integration fixtures,
   - draft stderr/halt assertions.

4. During Phase 4:
   - run negative validation on roadmap diffs in parallel with certify-block tests.

---

# 8. Final analyzer recommendations

1. **Do not start coding before resolving OQ-A/OQ-B.**
   - That decision affects gate architecture, parsing strategy, and test design.

2. **Treat `deviation-analysis` gate semantics as the primary correctness boundary.**
   - The v5 design intentionally shifts blocking decisions there.

3. **Require explicit evidence for intentionality everywhere.**
   - This is the core anti-laundering defense and the main reason for the redesign.

4. **Make freshness invalidation visible in logs.**
   - Silent re-execution or silent reuse will complicate operations and incident analysis.

5. **Validate negative behavior as rigorously as positive behavior.**
   - The most important outcome is often what the pipeline refuses to do:
     - refuse bogus intentional claims,
     - refuse stale deviation artifacts,
     - refuse ambiguous continuation,
     - refuse false certification,
     - refuse a third remediation attempt.

6. **Block release on evidence, not implementation confidence.**
   - For a 0.92 enterprise-complexity change, passing tests and artifact inspection are the acceptance threshold.
