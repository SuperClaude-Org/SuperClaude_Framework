# Phase 6 -- Quality Amplification

Add controlled critique loops without surrendering orchestration authority to Claude. The convergence engine is extracted as a standalone, testable component. Brainstorm gaps and panel review operate within bounded iterations.

### T06.01 -- Implement brainstorm-gaps Step (Step 6)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Step 6 identifies specification gaps through /sc:brainstorm invocation with graceful fallback to inline prompt if skill is unavailable. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (spec augmentation), depends on external skill availability |
| Tier | STANDARD |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028, D-0029, D-0049 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0028/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0029/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0049/spec.md

**Deliverables:**
1. `brainstorm_gaps` step implementation in `src/superclaude/cli/cli_portify/steps/brainstorm_gaps.py` with: pre-flight check for `/sc:brainstorm` availability, invocation with `--strategy systematic --depth deep --no-codebase`, post-processing into structured findings objects (`gap_id`, `description`, `severity`, `affected_section`, `persona`)
2. Inline fallback multi-persona prompt with warning when `/sc:brainstorm` skill is unavailable
3. Post-processed structured findings: actionable items incorporated into spec sections marked `[INCORPORATED]`, unresolvable items routed to Section 11 marked `[OPEN]`, Section 12 summary appended

**Steps:**
1. **[PLANNING]** Pre-flight check: verify `/sc:brainstorm` skill is available
2. **[PLANNING]** Load synthesized spec from Step 5 as input artifact
3. **[EXECUTION]** If skill available: invoke `/sc:brainstorm` with `--strategy systematic --depth deep --no-codebase`
4. **[EXECUTION]** If skill unavailable: use inline multi-persona fallback prompt with warning
5. **[EXECUTION]** Post-process findings into structured objects: gap_id, description, severity, affected_section, persona
6. **[EXECUTION]** Incorporate actionable findings into spec sections marked `[INCORPORATED]`; route unresolvable items to Section 11 marked `[OPEN]`; append Section 12 summary
7. **[VERIFICATION]** Run SC-006 STANDARD gate: Section 12 present with structural content validation (findings table with Gap ID column OR zero-gap summary text; heading-only fails)
8. **[COMPLETION]** Log brainstorm findings count, fallback usage, and gate result

**Acceptance Criteria:**
- Section 12 exists with structural content: either a findings table (with Gap ID column) or the literal zero-gap summary text; heading-only content fails the gate (SC-006, SC-015)
- Pre-flight skill check executes and fallback activates with warning when `/sc:brainstorm` is unavailable
- Findings are post-processed into structured objects with gap_id, description, severity, affected_section, persona
- Actionable findings are marked `[INCORPORATED]` and unresolvable items are in Section 11 marked `[OPEN]`

**Validation:**
- `uv run pytest tests/cli_portify/test_brainstorm_gaps.py -v` exits 0 (testing skill path and fallback path)
- Evidence: linkable artifact produced at D-0028/spec.md, D-0029/spec.md, D-0049/spec.md

**Dependencies:** T05.03, T04.02, T04.05
**Rollback:** TBD (if not specified in roadmap)

---

### T06.02 -- Implement Standalone Convergence Engine

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | The convergence engine manages predicate checking, budget guards, and escalation as a standalone component independent of Claude subprocess management. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | performance (budget management), cross-cutting scope (convergence across iterations) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0030, D-0046 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0030/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0046/spec.md

**Deliverables:**
1. Standalone convergence engine in `src/superclaude/cli/cli_portify/convergence.py` with: convergence predicate (zero unaddressed CRITICALs -> CONVERGED), max iterations (`max_convergence`, default 3), terminal states (CONVERGED success, ESCALATED partial with user escalation), unit-testable with mock iteration results
2. TurnLedger pre-launch budget guard: checks estimated cost before each iteration, prevents budget exhaustion

**Steps:**
1. **[PLANNING]** Load TurnLedger API from `sprint.models` to understand budget guard integration
2. **[PLANNING]** Define convergence state machine: RUNNING -> CONVERGED | ESCALATED
3. **[EXECUTION]** Implement convergence predicate: zero unaddressed CRITICALs -> CONVERGED
4. **[EXECUTION]** Implement iteration loop with max_convergence limit (default 3)
5. **[EXECUTION]** Implement TurnLedger pre-launch budget guard before each iteration
6. **[EXECUTION]** Implement terminal states: CONVERGED (success) and ESCALATED (partial, user escalation with resume guidance)
7. **[VERIFICATION]** Test convergence engine with mock iteration results: convergence path, escalation path, budget exhaustion path
8. **[COMPLETION]** Document convergence engine API and state machine

**Acceptance Criteria:**
- Convergence engine is a standalone module testable without Claude subprocess management
- Convergence predicate: zero unaddressed CRITICALs -> CONVERGED terminal state
- Max iterations enforced: `max_convergence` (default 3) with ESCALATED terminal state on exhaustion
- TurnLedger pre-launch budget guard checks estimated cost before each iteration

**Validation:**
- `uv run pytest tests/cli_portify/test_convergence.py -v` exits 0 (testing convergence, escalation, budget exhaustion paths)
- Evidence: linkable artifact produced at D-0030/spec.md and D-0046/spec.md

**Dependencies:** T02.03, T04.03
**Rollback:** TBD (if not specified in roadmap)

---

### T06.03 -- Implement panel-review Step (Step 7) with Quality Scoring

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Step 7 runs focus+critique passes per iteration with quality scoring, downstream readiness gating (7.0 boundary), and convergence loop integration. |
| Effort | L |
| Risk | High |
| Risk Drivers | performance (convergence iterations), cross-cutting scope (quality scoring + gate + review), compliance (downstream readiness boundary) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0031, D-0032, D-0050, D-0051 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0031/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0032/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0050/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0051/spec.md

**Deliverables:**
1. `panel_review` step implementation in `src/superclaude/cli/cli_portify/steps/panel_review.py` with: pre-flight `/sc:spec-panel` check with inline fallback, each iteration runs both focus pass and critique pass as single Claude subprocess, per-iteration independent timeout (default 300s per SC-016)
2. Quality scoring: clarity, completeness, testability, consistency dimensions; overall = mean of 4 dimensions (SC-008)
3. Downstream readiness gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false per SC-009)
4. User review gate at end of panel-review step

**Steps:**
1. **[PLANNING]** Pre-flight check: verify `/sc:spec-panel` availability; prepare inline fallback
2. **[PLANNING]** Load convergence engine (D-0030) and synthesized spec as inputs
3. **[EXECUTION]** Implement iteration loop: each iteration runs focus+critique as single Claude subprocess with per-iteration independent timeout (default 300s)
4. **[EXECUTION]** Implement quality scoring: parse clarity, completeness, testability, consistency from panel output; compute overall = mean of 4 dimensions
5. **[EXECUTION]** Implement downstream readiness gate: overall >= 7.0 passes (7.0 true, 6.9 false)
6. **[EXECUTION]** Implement user review gate at end: stderr prompt, y/n, USER_REJECTED on n
7. **[VERIFICATION]** Run SC-007 STRICT gate: convergence terminal state reached, quality scores populated, downstream readiness evaluated
8. **[COMPLETION]** Log iteration count, quality scores, convergence state, and review decision

**Acceptance Criteria:**
- Each iteration runs both focus and critique as single Claude subprocess with per-iteration independent timeout (default 300s, SC-016)
- Quality scores computed: clarity, completeness, testability, consistency; overall = mean of 4 dimensions +/- 0.01 (SC-008)
- Downstream readiness gate: overall >= 7.0 passes, 6.9 fails (SC-009)
- SC-007 STRICT gate passes: convergence terminal state reached, quality scores populated, downstream readiness evaluated

**Validation:**
- `uv run pytest tests/cli_portify/test_panel_review.py -v` exits 0 (testing convergence, scoring, boundary, timeout)
- Evidence: linkable artifact produced at D-0031/spec.md, D-0032/spec.md, D-0050/spec.md, D-0051/spec.md

**Dependencies:** T06.01, T06.02, T04.05
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Risk: High due to R-2 (incorrect convergence prompt design) and R-3 (budget exhaustion). Per-iteration independent timeout per SC-016.

---

### T06.04 -- Implement Section Hashing for Additive-Only Modifications

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | NFR-008 requires section hashing to enforce that panel-review iterations only add content and never remove or modify existing sections. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data integrity (additive-only enforcement) |
| Tier | STANDARD |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0033/spec.md

**Deliverables:**
1. Section hashing integration in panel-review step using utilities from D-0010: hash sections before each iteration, verify no existing section hashes changed after iteration, reject iterations that modify existing content

**Steps:**
1. **[PLANNING]** Load section hashing utilities from shared utility layer (D-0010)
2. **[PLANNING]** Identify section boundaries in panel-review output for hashing
3. **[EXECUTION]** Implement pre-iteration section hash capture
4. **[EXECUTION]** Implement post-iteration hash comparison to detect modifications
5. **[EXECUTION]** Implement rejection logic for iterations that modify existing sections
6. **[VERIFICATION]** Test additive-only enforcement: verify additions pass, modifications are rejected
7. **[COMPLETION]** Document hashing behavior and rejection semantics

**Acceptance Criteria:**
- Section hashes are captured before each panel-review iteration
- Post-iteration hash comparison detects any modifications to existing sections
- Iterations that modify existing content (hash mismatch) are rejected per NFR-008
- New content additions (new sections, appended content) are accepted

**Validation:**
- `uv run pytest tests/cli_portify/test_section_hashing.py -v` exits 0
- Evidence: linkable artifact produced at D-0033/spec.md

**Dependencies:** T02.04, T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 6 / Tasks T06.01-T06.04

**Purpose:** Verify brainstorm and convergence components are operational before panel report generation.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P06-T01-T04.md
**Verification:**
- Brainstorm step passes with findings or zero-gap summary
- Convergence engine stops correctly on convergence or escalation
- Section hashing enforces additive-only modifications
**Exit Criteria:**
- SC-006 gate validates Section 12 structural content
- Convergence engine unit tests pass for all 3 paths (converge, escalate, budget exhaustion)
- Additive-only protection verified with hash comparison tests

---

### T06.05 -- Generate panel-report.md with Machine-Readable Convergence Block

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | The panel-report.md is the final quality artifact capturing convergence state, quality scores, and downstream readiness for release readiness verification. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (aggregates all quality data) |
| Tier | STANDARD |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0034/spec.md

**Deliverables:**
1. `panel-report.md` generation in `src/superclaude/cli/cli_portify/steps/panel_review.py` (or separate reporter module) with: machine-readable convergence block (YAML frontmatter with terminal state, iteration count, quality scores), human-readable summary, downstream readiness verdict

**Steps:**
1. **[PLANNING]** Collect convergence state, quality scores, and iteration history from panel-review execution
2. **[PLANNING]** Define panel-report.md structure with machine-readable and human-readable sections
3. **[EXECUTION]** Generate YAML frontmatter convergence block: terminal_state, iterations, quality scores (4 dimensions + overall)
4. **[EXECUTION]** Generate human-readable summary: iteration history, finding resolution, downstream readiness verdict
5. **[VERIFICATION]** Verify panel-report.md contains machine-readable convergence block with all required fields
6. **[COMPLETION]** Log report generation to diagnostics

**Acceptance Criteria:**
- `panel-report.md` exists with YAML frontmatter containing: terminal_state, iteration_count, quality scores (clarity, completeness, testability, consistency, overall)
- Machine-readable convergence block is parseable by downstream tooling
- Human-readable summary includes iteration history and downstream readiness verdict
- Report reflects actual convergence engine terminal state (CONVERGED or ESCALATED)

**Validation:**
- `uv run pytest tests/cli_portify/test_panel_report.py -v` exits 0
- Evidence: linkable artifact produced at D-0034/spec.md

**Dependencies:** T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 6

**Purpose:** Verify review and convergence pipeline is fully operational before UX and hardening begins.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P06-END.md
**Verification:**
- Brainstorm step passes with findings or zero-gap summary (SC-006)
- Panel review stops correctly on convergence or escalation (SC-007)
- Quality scoring and downstream readiness are computed deterministically (SC-008, SC-009)
**Exit Criteria:**
- Additive-only protection is enforced via section hashing (M5 criterion)
- Convergence engine passes unit tests independently of subprocess management (M5 criterion)
- panel-report.md contains machine-readable convergence block
