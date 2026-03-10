# Phase 3 -- Panel Review Rewrite

Replace integration Phase 4 with two-pass panel review and convergence loop. This phase implements the focus pass, focus incorporation, critique pass, critique incorporation with scoring, and the bounded convergence loop using state machine semantics.

### T03.01 -- Implement Focus Pass (4a) in SKILL.md with Expert Analysis

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022, R-023 |
| Why | The roadmap requires rewriting Phase 4 step 4a in SKILL.md (FR-014, FR-008): embed `sc:spec-panel` behavioral patterns inline with `--focus correctness,architecture`, applying Fowler (architecture), Nygard (reliability), Whittaker (adversarial), Crispin (testing) expert analysis. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0016/spec.md

**Deliverables:**
1. Phase 4 step 4a instructions in SKILL.md: focus pass with `--focus correctness,architecture` embedding Fowler (architecture), Nygard (reliability/failure modes), Whittaker (adversarial), Crispin (testing) expert analysis patterns, producing output format `{finding_id, severity(CRITICAL/MAJOR/MINOR), expert, location, issue, recommendation}`

**Steps:**
1. **[PLANNING]** Review `sc:spec-panel` behavioral patterns in `src/superclaude/commands/spec-panel.md` to identify expert analysis patterns
2. **[PLANNING]** Map each expert (Fowler, Nygard, Whittaker, Crispin) to their analysis focus areas
3. **[EXECUTION]** Write step 4a focus pass instructions embedding all 4 expert analysis patterns inline
4. **[EXECUTION]** Specify focus dimensions: `correctness` and `architecture`
5. **[EXECUTION]** Define output format: `{finding_id, severity(CRITICAL/MAJOR/MINOR), expert, location, issue, recommendation}`
6. **[VERIFICATION]** Verify all 4 experts are represented and output schema has all 6 required fields
7. **[COMPLETION]** Document embedded expert patterns and their mapping to focus dimensions

**Acceptance Criteria:**
- SKILL.md Phase 4 step 4a contains focus pass instructions with `--focus correctness,architecture` applying all 4 named experts
- Focus pass output format contains all 6 fields: `finding_id`, `severity(CRITICAL/MAJOR/MINOR)`, `expert`, `location`, `issue`, `recommendation`
- Expert analysis patterns are embedded inline per Constraint 1 (no inter-skill command invocation)
- Focus pass produces findings for both correctness and architecture dimensions (SC-006)

**Validation:**
- Manual check: SKILL.md Phase 4 step 4a references all 4 experts (Fowler, Nygard, Whittaker, Crispin) and produces structured findings with all 6 fields
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0016/spec.md)

**Dependencies:** T02.01, T02.02, T02.03
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
**Notes:** Tier STRICT due to "rewrite" of Phase 4 behavioral protocol in SKILL.md.

---

### T03.02 -- Implement Focus Incorporation (4b) in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | The roadmap requires Phase 4 step 4b (FR-009): CRITICAL findings must be addressed (incorporated or justified dismissal per Constraint 7), MAJOR incorporated into spec body, MINOR appended to Open Items, all modifications additive-only per Constraint 2 and NFR-008. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (additive-only constraint violation could introduce contradictions) |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0017/spec.md

**Deliverables:**
1. Phase 4 step 4b instructions in SKILL.md: severity-based incorporation rules — CRITICAL addressed (incorporated or justified dismissal), MAJOR incorporated into spec body, MINOR appended to Open Items — with additive-only constraint (Constraint 2, NFR-008)

**Steps:**
1. **[PLANNING]** Review Constraint 2 (additive-only) and Constraint 7 (CRITICAL incorporation or justified dismissal)
2. **[PLANNING]** Define the incorporation routing by severity level
3. **[EXECUTION]** Write step 4b CRITICAL handling: incorporate finding or document justified dismissal reason
4. **[EXECUTION]** Write step 4b MAJOR handling: incorporate into corresponding spec body section
5. **[EXECUTION]** Write step 4b MINOR handling: append to Section 11 (Open Items)
6. **[EXECUTION]** Enforce additive-only constraint: append/extend only, no rewrites of existing content
7. **[VERIFICATION]** Verify all 3 severity levels have explicit handling rules and additive-only constraint is documented
8. **[COMPLETION]** Document incorporation rules and constraint references

**Acceptance Criteria:**
- SKILL.md Phase 4 step 4b contains severity-routing rules for CRITICAL (address or justify), MAJOR (incorporate), and MINOR (append to Open Items)
- Additive-only constraint explicitly stated: modifications use append/extend only, no rewrites (Constraint 2, NFR-008)
- CRITICAL dismissal requires documented justification (Constraint 7)
- All modifications traceable by finding_id from step 4a output

**Validation:**
- Manual check: SKILL.md Phase 4 step 4b contains all 3 severity handlers and additive-only constraint
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0017/spec.md)

**Dependencies:** T03.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### T03.03 -- Implement Critique Pass (4c) in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | The roadmap requires Phase 4 step 4c (FR-010): critique pass with `--mode critique` producing quality scores `{clarity, completeness, testability, consistency}` as floats (0-10 range) and prioritized improvement recommendations. |
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
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0018/spec.md

**Deliverables:**
1. Phase 4 step 4c instructions in SKILL.md: critique pass with `--mode critique` producing 4 quality dimension scores (`clarity`, `completeness`, `testability`, `consistency`) as floats in 0-10 range, plus prioritized improvement recommendations

**Steps:**
1. **[PLANNING]** Review `sc:spec-panel` critique mode behavioral patterns
2. **[PLANNING]** Define quality score schema: 4 dimensions, float type, 0-10 range
3. **[EXECUTION]** Write step 4c critique pass instructions with `--mode critique` behavioral patterns embedded inline
4. **[EXECUTION]** Specify quality score output: `{clarity: float, completeness: float, testability: float, consistency: float}`
5. **[EXECUTION]** Specify prioritized improvement recommendations output
6. **[VERIFICATION]** Verify all 4 quality dimensions are named and typed as floats in 0-10 range (SC-007)
7. **[COMPLETION]** Document critique pass output schema and recommendation format

**Acceptance Criteria:**
- SKILL.md Phase 4 step 4c contains critique pass instructions with `--mode critique` producing all 4 quality scores
- Quality scores typed as floats in 0-10 range: `clarity`, `completeness`, `testability`, `consistency`
- Critique pass produces prioritized improvement recommendations
- All 4 quality dimension scores present per SC-007

**Validation:**
- Manual check: SKILL.md Phase 4 step 4c specifies all 4 quality dimensions as float (0-10) with critique behavioral patterns
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0018/spec.md)

**Dependencies:** T03.01, T03.02
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### T03.04 -- Implement Critique Incorporation and Scoring (4d) in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | The roadmap requires Phase 4 step 4d (FR-011): record quality scores in spec frontmatter, compute `overall = mean(clarity, completeness, testability, consistency)` (Constraint 6), and append full panel report as `panel-report.md`. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0019/spec.md

**Deliverables:**
1. Phase 4 step 4d instructions in SKILL.md: record 4 quality scores in spec frontmatter, compute `overall = mean(clarity, completeness, testability, consistency)` (Constraint 6), append full panel report as `panel-report.md`

**Steps:**
1. **[PLANNING]** Define spec frontmatter schema for quality score fields
2. **[PLANNING]** Verify mean computation formula matches Constraint 6
3. **[EXECUTION]** Write step 4d: record quality scores in spec frontmatter
4. **[EXECUTION]** Write step 4d: compute `overall = mean(clarity, completeness, testability, consistency)`
5. **[EXECUTION]** Write step 4d: append full panel report as `panel-report.md`
6. **[VERIFICATION]** Verify formula `overall = (clarity + completeness + testability + consistency) / 4` matches Constraint 6 (SC-010)
7. **[COMPLETION]** Document scoring computation and panel report generation

**Acceptance Criteria:**
- SKILL.md Phase 4 step 4d records all 4 quality scores in spec frontmatter
- Overall score computed as `mean(clarity, completeness, testability, consistency)` per Constraint 6
- Full panel report appended as `panel-report.md` in the working directory
- Quality formula verified: `overall == mean(4 scores)` per SC-010

**Validation:**
- Manual check: SKILL.md Phase 4 step 4d contains frontmatter scoring, mean computation formula, and panel report generation
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0019/spec.md)

**Dependencies:** T03.03
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.04

**Purpose:** Verify the four review pass steps (4a-4d) are complete before proceeding to convergence loop and cleanup.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P03-T01-T04.md
**Verification:**
- Focus pass (4a) produces findings with all 6 fields for both correctness and architecture dimensions
- Focus incorporation (4b) handles all 3 severity levels with additive-only constraint
- Critique pass (4c) produces all 4 quality dimension scores as floats in 0-10 range
**Exit Criteria:**
- Tasks T03.01-T03.04 completed with deliverables D-0016 through D-0019 produced
- All 4 review steps (4a-4d) present in SKILL.md Phase 4
- Additive-only constraint documented and enforced

---

### T03.05 -- Implement Convergence Loop with State Machine in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | The roadmap requires a convergence loop documented using state machine terminology (debate D-03): states REVIEWING→INCORPORATING→SCORING→{CONVERGED|ESCALATED}, max 3 iterations hard cap, terminal states for zero-CRITICAL convergence and iteration exhaustion. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0020/notes.md

**Deliverables:**
1. Convergence loop implementation in SKILL.md using state machine terminology: states (REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED), transition logic (unaddressed CRITICALs after SCORING → return to REVIEWING), max 3 iterations bound, terminal states (CONVERGED: zero unaddressed CRITICALs with `status: success`; ESCALATED: 3 iterations exhausted with `status: partial`)

**Steps:**
1. **[PLANNING]** Map state machine states to SKILL.md execution steps
2. **[PLANNING]** Define transition predicates: unaddressed CRITICALs check
3. **[EXECUTION]** Write convergence loop with REVIEWING → INCORPORATING → SCORING state transitions
4. **[EXECUTION]** Write transition logic: if unaddressed CRITICALs remain after SCORING, return to REVIEWING
5. **[EXECUTION]** Enforce max 3 iterations hard cap with iteration counter
6. **[EXECUTION]** Write terminal states: CONVERGED (`status: success`, zero unaddressed CRITICALs) and ESCALATED (`status: partial`, 3 iterations exhausted, escalate to user)
7. **[VERIFICATION]** Verify all 5 states are defined, transition logic is correct, and iteration bound is enforced (SC-008)
8. **[COMPLETION]** Document state machine diagram and terminal conditions

**Acceptance Criteria:**
- SKILL.md contains convergence loop with all 5 states: REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED
- Transition logic: unaddressed CRITICALs after SCORING triggers return to REVIEWING
- Max 3 iterations hard cap enforced with explicit iteration counter
- Terminal states produce correct contract fields: CONVERGED → `status: success`, ESCALATED → `status: partial`

**Validation:**
- Manual check: SKILL.md convergence loop has all 5 states, transition predicates, 3-iteration bound, and both terminal states
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0020/notes.md)

**Dependencies:** T03.04
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### T03.06 -- Remove Old Phase 4 Instructions from SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | The roadmap requires removing old Phase 4 instructions: main.py patching, import verification, structural tests, summary writing (FR-014). |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (removal of existing functionality) |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0021/evidence.md

**Deliverables:**
1. SKILL.md with old Phase 4 instructions removed: main.py patching, import verification, structural tests, summary writing

**Steps:**
1. **[PLANNING]** Identify all old Phase 4 instruction blocks in SKILL.md (main.py patching, import verification, structural tests, summary writing)
2. **[PLANNING]** Confirm new Phase 4 (panel review) is in place before removing old instructions
3. **[EXECUTION]** Remove main.py patching instructions from SKILL.md
4. **[EXECUTION]** Remove import verification instructions from SKILL.md
5. **[EXECUTION]** Remove structural tests and summary writing instructions from SKILL.md
6. **[VERIFICATION]** Grep SKILL.md for residual old Phase 4 keywords: `main.py`, `import_verification`, `structural_test`, `summary_writing`
7. **[COMPLETION]** Document removed instruction blocks

**Acceptance Criteria:**
- SKILL.md contains zero references to old Phase 4 operations: main.py patching, import verification, structural tests, summary writing
- New Phase 4 (panel review steps 4a-4d + convergence loop) is intact and unaffected by removal
- `grep -c 'main\.py\|import_verification\|structural_test' src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` returns 0 in phase execution sections
- Removal does not affect Phases 0-2 behavior

**Validation:**
- Manual check: Grep for old Phase 4 keywords returns zero matches in SKILL.md phase execution sections
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0021/evidence.md)

**Dependencies:** T03.01, T03.02, T03.03, T03.04, T03.05
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### T03.07 -- Add Phase 4 Timing Instrumentation and downstream_ready Gate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029, R-030 |
| Why | The roadmap requires adding `phase_4_seconds` timing instrumentation (SC-013) and implementing the `downstream_ready` gate: `overall >= 7.0` → true, else false (Constraint 8, SC-012). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022, D-0023 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0022/evidence.md
- TASKLIST_ROOT/artifacts/D-0023/evidence.md

**Deliverables:**
1. Phase 4 timing instrumentation in SKILL.md that records `phase_4_seconds` in the return contract's `phase_timing` field
2. `downstream_ready` gate logic: `overall >= 7.0` sets `downstream_ready: true`, else `downstream_ready: false` (Constraint 8, SC-012)

**Steps:**
1. **[PLANNING]** Identify Phase 4 entry/exit boundaries for timing instrumentation
2. **[PLANNING]** Define `downstream_ready` gate threshold (7.0 per Constraint 8)
3. **[EXECUTION]** Add timing start marker at Phase 4 entry and end marker at Phase 4 exit
4. **[EXECUTION]** Compute `phase_4_seconds` and populate in `phase_timing` contract field
5. **[EXECUTION]** Implement `downstream_ready` gate: `if overall >= 7.0 then downstream_ready = true else downstream_ready = false`
6. **[VERIFICATION]** Verify boundary behavior: `overall = 7.0` → true, `overall = 6.9` → false (SC-012)
7. **[COMPLETION]** Document timing instrumentation and gate threshold

**Acceptance Criteria:**
- SKILL.md Phase 4 contains timing instrumentation populating `phase_4_seconds` in return contract
- `downstream_ready` gate evaluates `overall >= 7.0` producing boolean result
- Boundary values verified: `overall = 7.0` → `downstream_ready: true`, `overall = 6.9` → `downstream_ready: false`
- NFR-002 15-minute advisory target documented alongside instrumentation

**Validation:**
- Manual check: SKILL.md Phase 4 has timing markers and `downstream_ready` gate with >= 7.0 threshold
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0022/evidence.md, D-0023/evidence.md)

**Dependencies:** T03.04, T03.05
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### Checkpoint: End of Phase 3

**Purpose:** Verify exit criteria: focus pass produces findings for correctness and architecture (SC-006), critique produces all 4 scores (SC-007), no unaddressed CRITICALs after <=3 iterations (SC-008), phase completes within 15-minute target (NFR-002).
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P03-END.md
**Verification:**
- Focus pass (4a) produces findings covering both correctness and architecture dimensions
- Critique pass (4c) produces all 4 quality dimension scores (clarity, completeness, testability, consistency)
- Convergence loop terminates with zero unaddressed CRITICALs or escalates after max 3 iterations
**Exit Criteria:**
- All 7 tasks (T03.01-T03.07) completed with deliverables D-0016 through D-0023 produced
- Old Phase 4 instructions fully removed from SKILL.md
- `downstream_ready` gate implemented with boundary behavior verified at 7.0 threshold
