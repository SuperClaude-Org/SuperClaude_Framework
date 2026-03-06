# Phase 1 -- Sprint Executor Tests

This phase establishes the characterization safety net that the roadmap requires before refactoring. The work focuses on pinning current sprint executor behavior across the named subsystems so later changes can be validated against stable expectations.

### T01.01 -- Add watchdog and stall characterization tests for sprint executor behavior

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-005 |
| Why | The roadmap requires a test-first safety net before refactoring begins. Watchdog and stall detection are explicitly named coverage gaps that must be pinned first. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/evidence.md`

**Deliverables:**
- Characterization task spec for watchdog and stall coverage
- Evidence note linking the three named watchdog and stall cases
- Test execution evidence placeholder for pinned executor behavior

**Steps:**
1. **[PLANNING]** Load roadmap context for sprint executor watchdog and stall expectations.
2. **[PLANNING]** Check dependency status and confirm this task starts Phase 1 with no blockers.
3. **[EXECUTION]** Add characterization cases for kill action, warn action, and reset on resume in the sprint executor test target.
4. **[EXECUTION]** Record the expected behavior for `stall_timeout`, `stall_action`, and `_stall_acted` in the task artifact notes.
5. **[VERIFICATION]** Run the sprint executor tests covering the added watchdog and stall cases.
6. **[COMPLETION]** Document outcomes in the intended artifact files and attach execution evidence references.

**Acceptance Criteria:**
- Manual check: the watchdog and stall characterization outputs described in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/spec.md` are recorded for kill, warn, and resume-reset cases.
- The task preserves the roadmap's test-first requirement by defining behavior before refactoring work starts.
- The characterization can be repeated against the same sprint executor subsystem scope without changing the expected cases.
- Traceability from `R-004` and `R-005` to `D-0001` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/notes.md`.

**Validation:**
- Manual check: watchdog and stall coverage includes kill action, warn action, and reset on resume.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/evidence.md`

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)

### T01.02 -- Add multi-phase sequencing characterization tests for sprint executor phases

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-006 |
| Why | The roadmap calls out multi-phase sequencing as untested behavior that must be pinned before hook migration begins. These tests protect phase ordering and halt propagation across more than one phase. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/evidence.md`

**Deliverables:**
- Characterization task spec for multi-phase ordering and halt propagation
- Evidence note for the happy-path and halt-at-phase-3 cases
- Test execution evidence placeholder for sequencing behavior

**Steps:**
1. **[PLANNING]** Load roadmap context for multi-phase sequencing expectations.
2. **[PLANNING]** Check dependencies and confirm the characterization suite still precedes any Phase 2 refactoring.
3. **[EXECUTION]** Add a characterization case for a three-phase happy path in the sprint executor tests.
4. **[EXECUTION]** Add a characterization case for halting at phase 3 and capture the expected cross-phase propagation.
5. **[VERIFICATION]** Run the sprint executor tests that cover multi-phase sequencing behavior.
6. **[COMPLETION]** Document the observed sequence expectations in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/spec.md` records both the three-phase happy path and halt-at-phase-3 outputs.
- The task preserves the roadmap requirement that phase execution order and halt propagation are explicitly verified.
- Re-running the same sequencing scenarios yields the same expected ordering and halt checkpoints.
- Traceability from `R-004` and `R-006` to `D-0002` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/notes.md`.

**Validation:**
- Manual check: the sequencing scope covers phase order and halt propagation across more than one phase.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/evidence.md`

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)

### T01.03 -- Add TUI, monitor, and tmux integration characterization tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-007 |
| Why | The roadmap explicitly names TUI, monitor, and tmux integration as uncovered behavior. Pinning these interactions reduces regression risk when process hooks are migrated in the next phase. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/evidence.md`

**Deliverables:**
- Characterization task spec for TUI, monitor, and tmux integration behavior
- Evidence note covering TUI update resilience, monitor lifecycle, and tmux tail-pane behavior
- Test execution evidence placeholder for integration coverage

**Steps:**
1. **[PLANNING]** Load roadmap context for TUI, monitor, and tmux integration expectations.
2. **[PLANNING]** Check dependencies and confirm external component behavior is still only being characterized.
3. **[EXECUTION]** Add characterization cases for TUI updates and TUI exception resilience.
4. **[EXECUTION]** Add characterization cases for `OutputMonitor` reset/start/stop and tmux tail-pane updates when `session_name` is set.
5. **[VERIFICATION]** Run the sprint executor tests that cover TUI, monitor, and tmux integration.
6. **[COMPLETION]** Record the named interactions and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/spec.md` names TUI updates, TUI exception resilience, monitor lifecycle, and tmux tail-pane behavior.
- The task preserves the roadmap requirement that TUI exceptions do not abort sprint and monitor lifecycle events are exercised.
- The integration characterization can be repeated without changing the listed integration expectations.
- Traceability from `R-004` and `R-007` to `D-0003` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/notes.md`.

**Validation:**
- Manual check: the characterization scope includes TUI updates, monitor lifecycle calls, and tmux session-name behavior.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/evidence.md`

**Dependencies:** T01.02
**Rollback:** TBD (if not specified in roadmap)

### T01.04 -- Add diagnostics characterization tests for failure collection behavior

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-008 |
| Why | The roadmap requires diagnostics behavior to be pinned before refactoring. These cases verify that failure collection is invoked and that collection errors remain non-fatal. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/evidence.md`

**Deliverables:**
- Characterization task spec for diagnostics failure handling
- Evidence note for collector invocation and non-fatal collection failure
- Test execution evidence placeholder for diagnostics coverage

**Steps:**
1. **[PLANNING]** Load roadmap context for diagnostics collection behavior.
2. **[PLANNING]** Check dependencies and confirm all earlier characterization tasks are defined.
3. **[EXECUTION]** Add a characterization case that records failure-triggered diagnostics collection behavior.
4. **[EXECUTION]** Add a characterization case that records non-fatal behavior when diagnostics collection fails.
5. **[VERIFICATION]** Run the sprint executor tests that cover diagnostics collection behavior.
6. **[COMPLETION]** Document the expected diagnostics outcomes in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/spec.md` records the failure-triggered collector case and the collection-failure-is-non-fatal case.
- The task preserves the roadmap requirement that diagnostics exceptions do not abort sprint execution.
- The diagnostics characterization can be re-run with the same two expected outcomes.
- Traceability from `R-004` and `R-008` to `D-0004` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/notes.md`.

**Validation:**
- Manual check: diagnostics coverage includes both collector invocation and non-fatal collection failure behavior.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/evidence.md`

**Dependencies:** T01.03
**Rollback:** TBD (if not specified in roadmap)

### Checkpoint: End of Phase 1
**Purpose:** Confirm the characterization safety net is fully defined before any refactoring tasks begin.
**Checkpoint Report Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/CP-P01-END.md`
**Verification:**
- Confirm all Phase 1 tasks map to the named sprint executor subsystems from the roadmap.
- Confirm each Phase 1 task has a linked deliverable artifact set under the tasklist root.
- Confirm characterization evidence placeholders exist for watchdog, sequencing, integration, and diagnostics coverage.
**Exit Criteria:**
- T01.01 through T01.04 are complete or explicitly recorded as blocked.
- D-0001 through D-0004 are traceable in the index and this phase file.
- Phase 2 refactoring tasks can reference the characterization scope without adding new subsystem gaps.
