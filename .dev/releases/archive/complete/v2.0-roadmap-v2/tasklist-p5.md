# TASKLIST — sc:roadmap v2 — Phase 5: Validation &amp; Quality Gates

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 5 of 7
**Task Range**: T05.01–T05.06
**Priority Wave**: P1
**Dependencies**: Phase 3 (M3: roadmap.md and test-strategy.md must exist for validation)
**Tier Distribution**: STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0

---

## Phase 5: Validation &amp; Quality Gates

Implement Wave 4 (multi-agent validation, REVISE loop) and the quality gate scoring system. This phase dispatches quality-engineer and self-review agents to validate roadmap artifacts, implements score aggregation with PASS/REVISE/REJECT thresholds, and builds the REVISE loop that re-runs generation when scores fall in the 70-84% range. Can be developed in parallel with Phase 4 (both depend on Phase 3).

---

### T05.01 — Implement quality-engineer agent dispatch

**Roadmap Item ID(s):** R-023
**Why:** The quality-engineer agent performs completeness, consistency, and traceability checks on roadmap artifacts, plus validates test-strategy.md against specific criteria.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0023
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0023/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0023/evidence.md`

**Deliverables:**
- quality-engineer agent dispatch in Wave 4: uses prompt from refs/validation.md to perform completeness, consistency, traceability checks on roadmap.md, plus test-strategy.md validation criteria

**Steps:**
1. **[PLANNING]** Load refs/validation.md (on-demand per ref loading protocol) for the quality-engineer agent prompt
2. **[PLANNING]** Confirm validation scope: roadmap.md completeness/consistency/traceability + test-strategy.md specific criteria
3. **[EXECUTION]** Implement agent dispatch mechanism using quality-engineer prompt from refs/validation.md
4. **[EXECUTION]** Implement completeness check: every extracted requirement maps to a milestone deliverable
5. **[EXECUTION]** Implement consistency check: milestone dependencies match roadmap dependency graph
6. **[EXECUTION]** Implement traceability check: deliverable IDs traceable from extraction.md through roadmap.md
7. **[VERIFICATION]** Validate agent produces numeric scores for each check dimension; verify test-strategy.md criteria are checked
8. **[COMPLETION]** Document agent dispatch flow and check dimensions

**Acceptance Criteria:**
- quality-engineer agent dispatched in Wave 4 using prompt from refs/validation.md
- Checks completeness (all requirements covered), consistency (no conflicting dependencies), and traceability (IDs traceable)
- Additionally validates test-strategy.md: interleave ratio matches complexity class, validation milestones reference real work milestones, philosophy is explicit not boilerplate, stop-and-fix thresholds defined
- Produces numeric scores per check dimension for aggregation

**Validation:**
- Manual check: Verify agent prompt matches refs/validation.md; verify all check dimensions produce scores; verify test-strategy.md criteria included
- Evidence: linkable artifact produced (evidence.md with check dimension inventory)

**Dependencies:** T01.05 (refs/validation.md), T03.04 (roadmap.md), T03.05 (test-strategy.md)
**Rollback:** TBD
**Notes:** Per spec FR-006 Wave 4, quality-engineer validates test-strategy.md against explicit criteria including interleave ratio, milestone references, philosophy encoding, and stop-and-fix thresholds.

---

### T05.02 — Implement self-review agent dispatch with 4-question protocol

**Roadmap Item ID(s):** R-024
**Why:** The self-review agent provides an independent validation perspective using a structured 4-question protocol that catches issues the quality-engineer may miss.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0024
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0024/spec.md`

**Deliverables:**
- self-review agent dispatch in Wave 4: uses 4-question validation protocol from refs/validation.md to independently assess roadmap quality

**Steps:**
1. **[PLANNING]** Load refs/validation.md for the self-review agent prompt and 4-question protocol
2. **[PLANNING]** Confirm the 4 questions in the self-review protocol
3. **[EXECUTION]** Implement self-review agent dispatch mechanism using prompt from refs/validation.md
4. **[EXECUTION]** Implement 4-question evaluation with numeric scoring per question
5. **[VERIFICATION]** Validate agent produces answers to all 4 questions with numeric scores
6. **[COMPLETION]** Document self-review protocol and scoring

**Acceptance Criteria:**
- self-review agent dispatched in Wave 4 using prompt from refs/validation.md
- 4-question protocol produces answers with numeric scores for each question
- Scores contribute to the aggregation formula in T05.03
- Agent operates independently from quality-engineer (separate dispatch, separate scoring)

**Validation:**
- Manual check: Verify 4-question protocol matches refs/validation.md; verify numeric scores produced
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.05 (refs/validation.md), T03.04 (roadmap.md)
**Rollback:** TBD
**Notes:** None.

---

### T05.03 — Implement score aggregation formula producing PASS/REVISE/REJECT

**Roadmap Item ID(s):** R-025
**Why:** Score aggregation combines quality-engineer and self-review scores into a single validation score that determines the roadmap's acceptance status.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0025
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0025/spec.md`

**Deliverables:**
- Score aggregation formula with defined weights, producing a validation_score (0.0-1.0) and validation_status (PASS/REVISE/REJECT)

**Steps:**
1. **[PLANNING]** Load refs/validation.md for the score aggregation formula and thresholds
2. **[PLANNING]** Confirm thresholds: PASS ≥85%, REVISE 70-84%, REJECT &lt;70%
3. **[EXECUTION]** Implement weighted aggregation of quality-engineer and self-review scores
4. **[EXECUTION]** Implement threshold classification: ≥85% → PASS, 70-84% → REVISE, &lt;70% → REJECT
5. **[EXECUTION]** Implement adversarial mode additional checks: missing adversarial artifacts → REJECT, missing convergence score → REVISE
6. **[VERIFICATION]** Test with scores at boundary values (69%, 70%, 84%, 85%); verify correct status assignment
7. **[COMPLETION]** Document aggregation formula and threshold verification

**Acceptance Criteria:**
- Aggregation formula produces deterministic validation_score from quality-engineer and self-review scores
- Thresholds applied correctly: PASS ≥85%, REVISE 70-84%, REJECT &lt;70%
- Adversarial mode checks: missing artifacts → REJECT, missing convergence → REVISE
- validation_score and validation_status written to roadmap.md frontmatter

**Validation:**
- Manual check: Verify boundary value behavior (69/70/84/85); verify adversarial mode checks; verify frontmatter update
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T05.01 (quality-engineer scores), T05.02 (self-review scores)
**Rollback:** TBD
**Notes:** None.

---

### T05.04 — Implement REVISE loop with max 2 iterations

**Roadmap Item ID(s):** R-026
**Why:** The REVISE loop re-runs Wave 3 generation with improvement recommendations when validation scores fall in the 70-84% range, improving roadmap quality before acceptance.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** cross-cutting scope (system-wide loop), data integrity
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0026
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0026/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0026/evidence.md`

**Deliverables:**
- REVISE loop implementation: collects improvement recommendations from validation agents, re-runs Wave 3 with recommendations as input, re-validates in Wave 4, caps at 2 iterations with PASS_WITH_WARNINGS fallback

**Steps:**
1. **[PLANNING]** Load spec FR-017 (REVISE loop) and refs/validation.md REVISE behavior specification
2. **[PLANNING]** Confirm loop parameters: max 2 iterations, PASS_WITH_WARNINGS fallback after 2nd REVISE
3. **[EXECUTION]** Implement improvement recommendation collection from quality-engineer and self-review agents
4. **[EXECUTION]** Implement Wave 3 re-execution with improvement recommendations as additional generation input
5. **[EXECUTION]** Implement Wave 4 re-validation after regeneration (iteration 2)
6. **[EXECUTION]** Implement PASS_WITH_WARNINGS fallback: if still REVISE after 2 iterations, accept with validation_status: PASS_WITH_WARNINGS
7. **[VERIFICATION]** Test REVISE loop with mock 75% score; verify re-generation occurs; verify PASS_WITH_WARNINGS after 2 failed iterations
8. **[COMPLETION]** Document loop flow, iteration tracking, and fallback behavior

**Acceptance Criteria:**
- REVISE triggers at 70-84% validation score with specific improvement recommendations
- Wave 3 re-runs with recommendations as additional input (not from scratch)
- Max 2 iterations enforced; 2nd REVISE → PASS_WITH_WARNINGS in frontmatter
- Iteration count tracked and reported in progress messages

**Validation:**
- Manual check: Verify REVISE triggers at correct threshold; verify max 2 iterations; verify PASS_WITH_WARNINGS status set correctly
- Evidence: linkable artifact produced (evidence.md with iteration flow trace)

**Dependencies:** T05.03 (score aggregation determines REVISE trigger), T03.04 (Wave 3 generation for re-execution)
**Rollback:** TBD
**Notes:** Per roadmap risk assessment, REVISE loop not converging is mitigated by max 2 iterations with PASS_WITH_WARNINGS fallback.

---

### Checkpoint: Phase 5 / Tasks 01-04

**Purpose:** Validate core validation pipeline before test-strategy validation and --no-validate flag tasks.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P05-T01-T04.md`
**Verification:**
- Both validation agents produce numeric scores from their respective prompts
- Score aggregation produces correct PASS/REVISE/REJECT at boundary values
- REVISE loop re-runs generation and caps at 2 iterations

**Exit Criteria:**
- Validation pipeline produces deterministic scores for a known roadmap input
- REVISE loop tested with mock REVISE-range score
- PASS_WITH_WARNINGS fallback verified after 2 iterations

---

### T05.05 — Implement test-strategy.md validation criteria in Wave 4

**Roadmap Item ID(s):** R-027
**Why:** test-strategy.md requires specific validation criteria beyond general quality checks to ensure the continuous parallel validation philosophy is correctly encoded.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0027
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0027/spec.md`

**Deliverables:**
- test-strategy.md-specific validation criteria integrated into quality-engineer Wave 4 checks: interleave ratio verification, milestone reference validation, philosophy encoding check, stop-and-fix threshold verification

**Steps:**
1. **[PLANNING]** Load spec FR-006 Wave 4 test-strategy.md validation requirements
2. **[PLANNING]** Confirm 4 validation criteria: interleave ratio, milestone references, philosophy encoding, stop-and-fix thresholds
3. **[EXECUTION]** Implement interleave ratio check: ratio matches complexity class (LOW→1:3, MEDIUM→1:2, HIGH→1:1)
4. **[EXECUTION]** Implement milestone reference validation: every V# references a real M# from roadmap.md
5. **[EXECUTION]** Implement philosophy encoding check: continuous parallel validation explicitly stated, not generic boilerplate
6. **[EXECUTION]** Implement stop-and-fix threshold verification: thresholds defined for each severity level
7. **[VERIFICATION]** Test with correct and incorrect test-strategy.md inputs; verify each criterion catches violations
8. **[COMPLETION]** Document validation criteria and test results

**Acceptance Criteria:**
- Validates interleave ratio matches complexity class exactly
- Every validation milestone references a real work milestone from roadmap.md
- Detects generic/boilerplate validation philosophy vs. explicit continuous parallel validation
- Stop-and-fix thresholds present for Critical, Major, Minor, Info severity levels

**Validation:**
- Manual check: Verify all 4 criteria implemented; verify each catches known violations
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T05.01 (quality-engineer dispatch framework), T03.05 (test-strategy.md must exist)
**Rollback:** TBD
**Notes:** These criteria are additions to the quality-engineer's general checks (T05.01), specifically targeting test-strategy.md quality.

---

### T05.06 — Implement --no-validate flag support

**Roadmap Item ID(s):** R-028
**Why:** The --no-validate flag allows users to skip Wave 4 validation when rapid iteration is more important than quality gates.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** LIGHT
**Confidence:** [████████░░] 78%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Quick sanity check (~100 tokens, 10s timeout)
**MCP Requirements:** None | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0028
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0028/spec.md`

**Deliverables:**
- --no-validate flag implementation: skips Wave 4 entirely, sets validation_score: 0.0 and validation_status: SKIPPED in roadmap.md frontmatter

**Steps:**
1. **[PLANNING]** Load spec flag definition for --no-validate and its frontmatter effects
2. **[PLANNING]** Confirm behavior: skip Wave 4, set validation_score: 0.0, set validation_status: SKIPPED
3. **[EXECUTION]** Implement flag detection in Wave 4 entry: if --no-validate, skip all validation agent dispatches
4. **[EXECUTION]** Implement frontmatter updates: validation_score: 0.0, validation_status: SKIPPED
5. **[VERIFICATION]** Verify Wave 4 is completely skipped; verify frontmatter values are correct
6. **[COMPLETION]** Document flag behavior

**Acceptance Criteria:**
- --no-validate flag completely skips Wave 4 (no agent dispatches, no scoring)
- validation_score set to 0.0 in roadmap.md frontmatter
- validation_status set to SKIPPED in roadmap.md frontmatter
- Progress message reflects skipped validation: "Wave 4 skipped: --no-validate flag set."

**Validation:**
- Manual check: Verify Wave 4 skipped; verify frontmatter values 0.0 and SKIPPED
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T05.03 (score aggregation framework must exist for the skip to bypass)
**Rollback:** TBD
**Notes:** Per spec Section 6.2, --no-validate defaults to false. LIGHT tier: "minor change" compound override — simple flag check with no data risk.

---

### Checkpoint: End of Phase 5

**Purpose:** Final gate for validation system; confirms multi-agent validation, REVISE loop, and skip flag are all functional.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P05-END.md`
**Verification:**
- Both validation agents dispatch correctly and produce numeric scores
- Score aggregation produces PASS/REVISE/REJECT at correct thresholds
- REVISE loop caps at 2 iterations with PASS_WITH_WARNINGS fallback

**Exit Criteria:**
- All 6 tasks (T05.01-T05.06) marked complete with evidence artifacts
- Wave 4 validation pipeline end-to-end functional
- --no-validate correctly skips validation and sets frontmatter

---

**End of Phase 5** | Tasks: 6 | Deliverables: 6 (D-0023–D-0028) | Tier Distribution: STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0
