# Phase 9 -- Observability Completion

Complete operational visibility infrastructure beyond Phase 3 baseline. Full TUI display, monitor integration, failure diagnostics, and execution log finalization needed for real usage and troubleshooting.

### T09.01 -- Complete PortifyTUI with Real-Time Progress Display

| Field | Value |
|---|---|
| Roadmap Item IDs | R-105 |
| Why | NFR-008 requires full real-time progress display via rich beyond the basic start/stop lifecycle from tasklist Phase 3 (roadmap Phase 2). |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance (real-time display) |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0052 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0052/spec.md

**Deliverables:**
- Complete `tui.py` with `PortifyTUI` implementing full real-time progress display via `rich`: step progress, timing, status indicators, convergence iteration tracking

**Steps:**
1. **[PLANNING]** Review rich library Live, Progress, and Table APIs for real-time display patterns
2. **[PLANNING]** Define display layout: current step, elapsed time, step status, convergence iteration
3. **[EXECUTION]** Implement real-time progress display showing current step name and status
4. **[EXECUTION]** Add timing display (elapsed, estimated remaining), convergence iteration counter, and status indicators
5. **[VERIFICATION]** Write tests: TUI renders correctly during step execution, updates on step transitions
6. **[COMPLETION]** Document TUI features in D-0052/spec.md

**Acceptance Criteria:**
- `PortifyTUI` displays real-time progress with current step, timing, and status using `rich` (NFR-008)
- Display updates on step transitions, convergence iterations, and error conditions
- TUI is non-blocking and does not interfere with executor performance
- TUI features documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0052/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_tui_display"` exits 0
- Evidence: linkable artifact produced at D-0052/spec.md

**Dependencies:** T03.12 (basic TUI lifecycle)
**Rollback:** TBD (if not specified in roadmap)

---

### T09.02 -- Complete OutputMonitor Integration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-106 |
| Why | OutputMonitor must track convergence iteration, findings count, and placeholder count beyond baseline metrics from tasklist Phase 3 (roadmap Phase 2). |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance (monitoring) |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0053 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0053/spec.md

**Deliverables:**
- Complete `monitor.py` with `OutputMonitor` tracking: convergence iteration number, findings count per severity, placeholder count

**Steps:**
1. **[PLANNING]** Review baseline OutputMonitor from T03.11 for extension points
2. **[PLANNING]** Define additional fields: convergence_iteration, findings_count (by severity), placeholder_count
3. **[EXECUTION]** Add convergence_iteration tracking to OutputMonitor
4. **[EXECUTION]** Add findings_count (CRITICAL, MAJOR, MINOR) and placeholder_count tracking
5. **[VERIFICATION]** Write tests: monitor tracks all new fields correctly during convergence iterations
6. **[COMPLETION]** Document monitor fields in D-0053/spec.md

**Acceptance Criteria:**
- `OutputMonitor` tracks convergence_iteration, findings_count (by severity), and placeholder_count
- Monitor integrates with convergence loop from Phase 8 for real-time tracking
- All new fields update correctly during panel review iterations
- Monitor fields documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0053/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_monitor_integration"` exits 0
- Evidence: linkable artifact produced at D-0053/spec.md

**Dependencies:** T03.11 (baseline monitor), T08.05 (convergence loop)
**Rollback:** TBD (if not specified in roadmap)

---

### T09.03 -- Implement Failure Diagnostics Collection

| Field | Value |
|---|---|
| Roadmap Item IDs | R-107 |
| Why | FR-042 requires diagnostics collection capturing gate failure reason, exit code, missing artifacts, and resume guidance for failure investigation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end (failure analysis) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0054 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0054/spec.md

**Deliverables:**
- `diagnostics.py` implementing failure diagnostics collection: gate failure reason, exit code, missing artifacts, resume guidance

**Steps:**
1. **[PLANNING]** Enumerate diagnostic data sources: gate results (T04.03), executor outcomes (T03.06), monitor state (T03.11)
2. **[PLANNING]** Define diagnostic report structure: failure summary, gate details, exit code, missing artifacts, resume command
3. **[EXECUTION]** Implement `diagnostics.py` collecting failure context from gate, executor, and monitor subsystems
4. **[EXECUTION]** Include resume guidance from T03.10 resume_command() and suggested_resume_budget
5. **[VERIFICATION]** Write tests: diagnostics collected correctly for gate failure, timeout, and interrupted scenarios
6. **[COMPLETION]** Document diagnostics format in D-0054/spec.md

**Acceptance Criteria:**
- `diagnostics.py` collects: gate failure reason, exit code, missing artifacts list, and resume guidance (FR-042)
- Diagnostics include resume command and suggested_resume_budget from executor
- Failures are diagnosable without re-reading raw artifacts
- Diagnostics format documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0054/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_diagnostics"` exits 0
- Evidence: linkable artifact produced at D-0054/spec.md

**Dependencies:** T04.03 (gate diagnostics), T03.10 (resume command)
**Rollback:** TBD (if not specified in roadmap)

---

### T09.04 -- Finalize Execution Logs with Complete Event Coverage

| Field | Value |
|---|---|
| Roadmap Item IDs | R-108 |
| Why | NFR-007 requires execution-log.jsonl and execution-log.md with complete event coverage beyond the skeleton from Phase 3. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0055 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0055/spec.md

**Deliverables:**
- Finalized `logging_.py` with complete `execution-log.jsonl` and `execution-log.md` covering all event types: step start/end, gate results, retry events, convergence iterations, outcome

**Steps:**
1. **[PLANNING]** Enumerate all event types: step_start, step_end, gate_pass, gate_fail, retry, convergence_iteration, outcome
2. **[PLANNING]** Review logging skeleton from T03.11 for extension
3. **[EXECUTION]** Implement complete event logging for all event types in both JSONL and markdown formats
4. **[EXECUTION]** Wire all executor, gate, and convergence events to logging subsystem
5. **[VERIFICATION]** Verify all event types appear in logs during end-to-end test runs
6. **[COMPLETION]** Document log event schema in D-0055/spec.md

**Acceptance Criteria:**
- `execution-log.jsonl` contains structured entries for all event types (NFR-007)
- `execution-log.md` contains human-readable log with complete event coverage
- All executor, gate, retry, and convergence events captured in logs
- Log event schema documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0055/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_execution_logs"` exits 0
- Evidence: linkable artifact produced at D-0055/spec.md

**Dependencies:** T03.11 (logging skeleton)
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 9

**Purpose:** Verify failures are diagnosable without re-reading raw artifacts; TUI provides real-time progress visibility; logs capture all events.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P09-END.md

**Verification:**
- PortifyTUI displays real-time progress with step status and timing
- OutputMonitor tracks convergence iteration, findings count, and placeholder count
- Failure diagnostics provide gate failure reason, exit code, missing artifacts, and resume guidance

**Exit Criteria:**
- Milestone M8 satisfied: failures diagnosable; TUI provides progress visibility
- All 4 tasks (T09.01-T09.04) completed with deliverables D-0052 through D-0055 produced
- Logs capture complete event coverage for all pipeline stages
