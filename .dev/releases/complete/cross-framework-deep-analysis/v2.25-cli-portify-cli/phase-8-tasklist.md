# Phase 8 -- Panel Review Convergence

Implement the highest-risk quality-control stage: bounded expert review with convergence scoring. Uses internal convergence loop (not outer retry) with 3-iteration cap and graceful escalation.

### T08.01 -- Implement Convergence State Machine in review.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-094 |
| Why | FR-030 requires convergence state machine with states: NOT_STARTED → REVIEWING → INCORPORATING → SCORING → CONVERGED or ESCALATED. |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide, end-to-end |
| Tier | STRICT |
| Confidence | [█████████░] 92% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0046 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0046/spec.md

**Deliverables:**
- Convergence state machine in `src/superclaude/cli/cli_portify/review.py` with states: NOT_STARTED, REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED

**Steps:**
1. **[PLANNING]** Map state transitions: NOT_STARTED → REVIEWING → INCORPORATING → SCORING → {CONVERGED, ESCALATED}
2. **[PLANNING]** Define transition guards: CONVERGED when zero unaddressed CRITICALs, ESCALATED after 3 iterations
3. **[EXECUTION]** Implement state machine class using ConvergenceState enum from T03.01
4. **[EXECUTION]** Implement transition logic with iteration counting (max 3 per NFR-005)
5. **[EXECUTION]** Implement terminal state detection: CONVERGED (success) and ESCALATED (partial)
6. **[VERIFICATION]** Write unit tests: all valid transitions, invalid transition rejection, 3-iteration cap enforcement
7. **[COMPLETION]** Document state machine in D-0046/spec.md

**Acceptance Criteria:**
- State machine implements: NOT_STARTED → REVIEWING → INCORPORATING → SCORING → {CONVERGED, ESCALATED} (FR-030)
- CONVERGED reached when zero unaddressed CRITICALs remain (FR-032)
- ESCALATED reached after 3 iterations exhausted (FR-033)
- State machine documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0046/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_convergence_state_machine"` exits 0
- Evidence: linkable artifact produced at D-0046/spec.md

**Dependencies:** T07.04 (release spec produced)
**Rollback:** TBD (if not specified in roadmap)

---

### T08.02 -- Implement Per-Iteration Panel Review Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-095 |
| Why | FR-031 requires per-iteration logic: 4-expert focus pass (Fowler, Nygard, Whittaker, Crispin), finding incorporation with severity routing, full panel critique with quality scoring. |
| Effort | XL |
| Risk | High |
| Risk Drivers | system-wide, end-to-end, depends |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0047 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0047/spec.md

**Deliverables:**
- Per-iteration panel review logic implementing substeps 4a-4d: (4a) 4-expert focus pass, (4b) finding incorporation with severity routing (CRITICAL→mandatory, MAJOR→incorporated, MINOR→Section 11), (4c) full panel critique with quality scoring, (4d) convergence scoring

**Steps:**
1. **[PLANNING]** Define 4-expert panel: Fowler (architecture), Nygard (reliability), Whittaker (testing), Crispin (quality)
2. **[PLANNING]** Define severity routing rules: CRITICAL→mandatory, MAJOR→incorporated, MINOR→Section 11
3. **[EXECUTION]** Implement substep 4a: 4-expert focus pass via Claude subprocess with expert persona prompts
4. **[EXECUTION]** Implement substep 4b: finding incorporation applying severity routing rules
5. **[EXECUTION]** Implement substep 4c: full panel critique producing quality scores across clarity, completeness, testability, consistency
6. **[EXECUTION]** Implement substep 4d: convergence scoring evaluating whether to continue iteration
7. **[VERIFICATION]** Write integration test: per-iteration cycle processes findings, routes by severity, produces quality scores
8. **[COMPLETION]** Document panel review algorithm in D-0047/spec.md

**Acceptance Criteria:**
- 4-expert focus pass invokes Fowler, Nygard, Whittaker, Crispin personas via Claude subprocess (FR-031)
- Finding incorporation routes: CRITICAL→mandatory incorporation, MAJOR→incorporated, MINOR→Section 11
- Quality scoring produces scores across clarity, completeness, testability, consistency dimensions
- Panel review algorithm documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0047/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_panel_review"` exits 0
- Evidence: linkable artifact produced at D-0047/spec.md

**Dependencies:** T08.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** XL effort — 4 substeps with Claude subprocess invocations per iteration, up to 3 iterations.

---

### T08.03 -- Implement CONVERGED and ESCALATED Terminal Conditions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-096, R-097 |
| Why | FR-032 requires CONVERGED when zero unaddressed CRITICALs (status: success). FR-033 requires ESCALATED after 3 iterations (status: partial). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0048 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0048/spec.md

**Deliverables:**
- CONVERGED condition (zero unaddressed CRITICALs → status: success) and ESCALATED condition (3 iterations exhausted → status: partial) implementations

**Steps:**
1. **[PLANNING]** Define CONVERGED evaluation: scan findings for unaddressed CRITICALs after incorporation
2. **[PLANNING]** Define ESCALATED condition: iteration_count >= 3 and CRITICALs remain
3. **[EXECUTION]** Implement CONVERGED check: zero unaddressed CRITICALs → transition to CONVERGED state → status: success
4. **[EXECUTION]** Implement ESCALATED check: 3 iterations completed → transition to ESCALATED state → status: partial
5. **[VERIFICATION]** Write unit tests: CONVERGED on zero CRITICALs (SC-009), ESCALATED after 3 iterations with remaining CRITICALs
6. **[COMPLETION]** Document terminal conditions in D-0048/spec.md

**Acceptance Criteria:**
- CONVERGED reached when zero unaddressed CRITICALs remain → status: success (FR-032, SC-009)
- ESCALATED reached after 3 iterations exhausted with remaining CRITICALs → status: partial (FR-033)
- Terminal conditions are mutually exclusive and deterministic
- Terminal conditions documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0048/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_convergence_terminal"` exits 0
- Evidence: linkable artifact produced at D-0048/spec.md

**Dependencies:** T08.02
**Rollback:** TBD (if not specified in roadmap)

---

### T08.04 -- Implement downstream_ready Gating on Quality Score

| Field | Value |
|---|---|
| Roadmap Item IDs | R-098 |
| Why | FR-034 and NFR-005 require downstream_ready = true only when overall quality score >= 7.0 to prevent partial output from being mistaken for completion (Risk 4). |
| Effort | S |
| Risk | Medium |
| Risk Drivers | data (quality scoring), breaking (false readiness) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0049 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0049/spec.md

**Deliverables:**
- `downstream_ready` flag gated on `overall >= 7.0` quality score threshold

**Steps:**
1. **[PLANNING]** Review quality scoring dimensions from T08.02: clarity, completeness, testability, consistency, overall
2. **[PLANNING]** Confirm threshold: overall >= 7.0 for downstream_ready = true
3. **[EXECUTION]** Implement downstream_ready evaluation: set true only when overall score >= 7.0
4. **[EXECUTION]** Ensure downstream_ready is separate from convergence status (Risk 4 mitigation)
5. **[VERIFICATION]** Write unit tests: score 7.0+ → downstream_ready=true (SC-010), score <7.0 → downstream_ready=false
6. **[COMPLETION]** Document quality gating in D-0049/spec.md

**Acceptance Criteria:**
- `downstream_ready = true` set only when `overall >= 7.0` (FR-034, NFR-005, SC-010)
- `downstream_ready` is strictly separated from convergence status (Risk 4 mitigation)
- Quality score of 6.9 → downstream_ready=false; score of 7.0 → downstream_ready=true
- Quality gating documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0049/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_downstream_ready"` exits 0
- Evidence: linkable artifact produced at D-0049/spec.md

**Dependencies:** T08.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 8 / Tasks T08.01-T08.04

**Purpose:** Verify convergence state machine, panel review logic, terminal conditions, and downstream_ready gating function correctly.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P08-T01-T04.md

**Verification:**
- State machine transitions are valid and deterministic
- Panel review produces quality scores and routes findings by severity
- downstream_ready correctly gated on overall >= 7.0

**Exit Criteria:**
- SC-009 (convergence within 3 iterations) validated
- SC-010 (quality score >= 7.0, downstream_ready=true) validated
- Terminal conditions (CONVERGED/ESCALATED) are deterministic

---

### T08.05 -- Implement Panel Report Emission on Both Terminal Conditions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-099, R-100 |
| Why | FR-035 requires panel-report.md emitted on both CONVERGED and ESCALATED terminal conditions. AC-011 requires internal convergence loop, not outer retry. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0050 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0050/spec.md

**Deliverables:**
- Panel report emission: updated `portify-release-spec.md` and `panel-report.md` emitted on both CONVERGED (status: success) and ESCALATED (status: partial) conditions; internal convergence loop (not outer retry)

**Steps:**
1. **[PLANNING]** Define panel-report.md structure: iteration summaries, finding counts, quality scores, terminal condition, escalation details
2. **[PLANNING]** Confirm AC-011: internal convergence loop, not outer retry mechanism
3. **[EXECUTION]** Implement panel-report.md emission on CONVERGED: include quality scores, finding resolution summary
4. **[EXECUTION]** Implement panel-report.md emission on ESCALATED: include escalation details, remaining CRITICALs, partial quality scores
5. **[EXECUTION]** Ensure convergence loop runs internally (AC-011), not via executor retry mechanism
6. **[VERIFICATION]** Write tests: panel-report.md produced on both CONVERGED and ESCALATED; updated release spec also emitted
7. **[COMPLETION]** Document panel report format in D-0050/spec.md

**Acceptance Criteria:**
- `panel-report.md` emitted on both CONVERGED (status: success) and ESCALATED (status: partial) conditions (FR-035)
- Updated `portify-release-spec.md` also emitted alongside panel report on both conditions
- Convergence loop runs internally (AC-011), not via executor's outer retry mechanism
- Panel report output satisfies G-011 gate checks: has_quality_scores (clarity, completeness, testability, consistency, overall) and has_criticals_addressed (all CRITICAL findings marked [INCORPORATED] or [DISMISSED])
- Panel report format documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0050/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_panel_report"` exits 0
- Evidence: linkable artifact produced at D-0050/spec.md

**Dependencies:** T08.03, T08.04
**Rollback:** TBD (if not specified in roadmap)

---

### T08.06 -- Enforce 1200s Timeout for Convergence Step

| Field | Value |
|---|---|
| Roadmap Item IDs | R-101 |
| Why | NFR-001 requires 1200s timeout for the convergence step (Step 11) to accommodate up to 3 iterations of panel review. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (timeout) |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0051 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0051/evidence.md

**Deliverables:**
- 1200s timeout enforcement for the convergence step (Step 11)

**Steps:**
1. **[PLANNING]** Confirm timeout value: 1200s for convergence step per NFR-001
2. **[PLANNING]** Verify 1200s accommodates up to 3 iterations of panel review
3. **[EXECUTION]** Configure convergence step with 1200s timeout
4. **[VERIFICATION]** Verify timeout configuration matches NFR-001 specification
5. **[COMPLETION]** Document timeout setting in D-0051/evidence.md

**Acceptance Criteria:**
- Convergence step (Step 11) enforces 1200s timeout per NFR-001
- Timeout accommodates up to 3 iterations of panel review
- Timeout expiry triggers TIMEOUT status classification
- Timeout documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0051/evidence.md

**Validation:**
- Manual check: convergence step timeout configuration verified at 1200s
- Evidence: linkable artifact produced at D-0051/evidence.md

**Dependencies:** T08.05
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 8

**Purpose:** Verify Step 11 converges or escalates deterministically; downstream_ready correctly gated on quality score.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P08-END.md

**Verification:**
- SC-008 (G-010 passes), SC-009 (convergence within 3 iterations), SC-010 (quality >= 7.0, downstream_ready=true) all pass
- panel-report.md emitted on both CONVERGED and ESCALATED paths
- Internal convergence loop enforced (not outer retry)

**Exit Criteria:**
- Milestone M7 satisfied: convergence or escalation deterministic; downstream_ready gated correctly
- All 6 tasks (T08.01-T08.06) completed with deliverables D-0046 through D-0051 produced
- 1200s timeout enforced for convergence step
