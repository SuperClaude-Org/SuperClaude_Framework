# Phase 8 -- TUI Integration & Rollout Hardening

Add the TUI gate column for user visibility and implement production hardening features: shadow mode for safe rollout and KPI reporting for observability. This phase is lower risk and focused on user experience and operational metrics.

### T08.01 -- Implement GateDisplayState Enum for TUI Rendering

| Field | Value |
|---|---|
| Roadmap Item IDs | R-044 |
| Why | The TUI needs discrete visual states for gate status to provide clear, at-a-glance feedback on gate lifecycle progress per task. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0034/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0034/evidence.md

**Deliverables:**
- GateDisplayState enum (~30 lines) with 7 visual states: NONE, CHECKING, PASS, FAIL_DEFERRED, REMEDIATING, REMEDIATED, HALT

**Steps:**
1. **[PLANNING]** Read existing TUI enums in sprint module to follow naming conventions
2. **[PLANNING]** Map gate lifecycle stages to the 7 display states
3. **[EXECUTION]** Implement GateDisplayState enum with 7 values and display properties (color, icon, label)
4. **[EXECUTION]** Add state transition validation: define valid transitions between display states
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k gate_display_state -v`
6. **[COMPLETION]** Record deliverable evidence in D-0034/evidence.md

**Acceptance Criteria:**
- GateDisplayState enum has exactly 7 values: NONE, CHECKING, PASS, FAIL_DEFERRED, REMEDIATING, REMEDIATED, HALT
- State transitions follow gate lifecycle (NONE → CHECKING → PASS|FAIL_DEFERRED → REMEDIATING → REMEDIATED|HALT)
- Each state has distinct display properties for TUI rendering
- `uv run pytest tests/sprint/ -k gate_display_state` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k gate_display_state -v`
- Evidence: linkable artifact produced at D-0034/evidence.md

**Dependencies:** T05.01 (trailing gate lifecycle defines states)
**Rollback:** Remove GateDisplayState enum

---

### T08.02 -- Add TUI Gate Column in sprint/tui.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-045 |
| Why | Users need inline visibility of gate status per task in the TUI phase table to monitor trailing gate progress without checking logs. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0035/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0035/evidence.md

**Deliverables:**
- TUI gate column (~40 lines) in `src/superclaude/cli/sprint/tui.py`: inline gate status column in the phase task table using GateDisplayState for rendering

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/tui.py` to understand existing table column patterns
2. **[PLANNING]** Identify insertion point for gate column in the task table layout
3. **[EXECUTION]** Add gate column to task table using GateDisplayState for per-task rendering
4. **[EXECUTION]** Ensure non-blocking TUI reads (follow existing best-effort snapshot pattern)
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k tui_gate_column -v`
6. **[COMPLETION]** Record deliverable evidence in D-0035/evidence.md

**Acceptance Criteria:**
- Gate column renders GateDisplayState per task in the phase table
- Column uses non-blocking reads following existing TUI snapshot pattern (no locks added)
- Gate column hidden when grace_period=0 (backward compatibility: no UI change for blocking-only mode)
- `uv run pytest tests/sprint/ -k tui_gate_column` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k tui_gate_column -v`
- Evidence: linkable artifact produced at D-0035/evidence.md

**Dependencies:** T08.01 (GateDisplayState enum)
**Rollback:** Remove gate column from TUI; table reverts to v1.2.1 layout

---

### T08.03 -- Implement Shadow Mode (--shadow-gates)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-046 |
| Why | Shadow mode enables safe rollout: trailing gate metrics collected alongside blocking behavior without affecting sprint execution, providing confidence before enabling trailing gates in production. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0036/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0036/evidence.md

**Deliverables:**
- Shadow mode: when `--shadow-gates` is passed, trailing gate evaluation runs in parallel with blocking gates but results are collected as metrics only (do not affect behavior); comparison to blocking baseline available in KPI report

**Steps:**
1. **[PLANNING]** Define shadow mode behavior: trailing gates run but results are metrics-only, not actionable
2. **[PLANNING]** Identify integration point: parallel evaluation alongside blocking path
3. **[EXECUTION]** Implement `--shadow-gates` CLI flag in sprint command
4. **[EXECUTION]** When enabled, submit gates to TrailingGateRunner in parallel with blocking evaluation; collect results as metrics
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k shadow_mode -v` verifying metrics collected without behavior change
6. **[COMPLETION]** Record deliverable evidence in D-0036/evidence.md

**Acceptance Criteria:**
- `--shadow-gates` flag enables shadow mode; metrics collected without affecting sprint behavior
- Blocking gate results determine task outcome (shadow results are informational only)
- Shadow metrics include: trailing gate latency, pass/fail rate comparison with blocking
- `uv run pytest tests/sprint/ -k shadow_mode` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k shadow_mode -v`
- Evidence: linkable artifact produced at D-0036/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner), T05.05 (executor branching)
**Rollback:** Remove shadow mode; `--shadow-gates` flag produces no effect

---

### T08.04 -- Implement KPI Report for Gate and Remediation Metrics

| Field | Value |
|---|---|
| Roadmap Item IDs | R-047 |
| Why | KPI reporting provides observability into trailing gate performance (latency, pass rates) and remediation frequency, enabling data-driven decisions about gate configuration. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (metric collection) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0037/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0037/evidence.md

**Deliverables:**
- KPI report generated after sprint completion containing: trailing gate latency (p50, p95), remediation frequency, conflict review rate, gate pass/fail distribution

**Steps:**
1. **[PLANNING]** Define KPI metrics: gate latency percentiles, remediation frequency, conflict rate, pass/fail distribution
2. **[PLANNING]** Identify data sources: TrailingGateResult.evaluation_ms, DeferredRemediationLog, conflict_review results
3. **[EXECUTION]** Implement KPI collection: aggregate metrics from gate results and remediation log
4. **[EXECUTION]** Implement KPI report output: formatted summary emitted after sprint completion
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k kpi_report -v`
6. **[COMPLETION]** Record deliverable evidence in D-0037/evidence.md

**Acceptance Criteria:**
- KPI report includes: gate latency (p50, p95), remediation frequency, conflict review rate
- Metrics are accurate (verified against known test inputs with predetermined metric values)
- Report generated after sprint completion (not during execution)
- `uv run pytest tests/sprint/ -k kpi_report` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k kpi_report -v`
- Evidence: linkable artifact produced at D-0037/evidence.md

**Dependencies:** T05.01 (gate results), T05.03 (remediation log), T07.04 (conflict review)
**Rollback:** Remove KPI report; sprint completes without metrics summary

---

### Checkpoint: End of Phase 8

**Purpose:** Confirm TUI integration and rollout hardening are complete before final end-to-end validation.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P08-END.md

**Verification:**
- GateDisplayState enum renders all 7 states correctly in TUI gate column
- Shadow mode collects metrics without affecting sprint behavior
- KPI report produces accurate metrics from gate and remediation data

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k "gate_display or tui_gate or shadow_mode or kpi_report" -v` exits 0
- All 4 deliverables (D-0034 through D-0037) have evidence artifacts
- TUI renders correctly with and without gate column (backward compat: grace_period=0 hides column)
