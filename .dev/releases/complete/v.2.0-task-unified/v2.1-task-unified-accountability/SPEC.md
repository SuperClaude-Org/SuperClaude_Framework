# Specification: sc:task-unified Accountability Framework v1.3

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.3.0 |
| Status | Draft |
| Created | 2026-01-26 |
| Authors | Claude Opus 4.5, Adversarial Debate Panel |
| Reviewers | Pending spec-panel review |
| Classification | Feature Enhancement |

---

## 1. Executive Summary

### 1.1 Problem Statement

The current `sc:task-unified` command lacks accountability mechanisms:

1. **Task Status Drift**: TodoWrite calls are not verified; status may not reflect actual state
2. **No Audit Trail**: No persistent record of operations performed during task execution
3. **No Progress Visibility**: Users cannot see what work was done or verify compliance

### 1.2 Proposed Solution

A three-phase accountability framework that creates a closed-loop verification system scaling with task risk:

| Phase | Component | Purpose | Token Cost |
|-------|-----------|---------|------------|
| 1 | Worklog | Information flow substrate | ~20/entry |
| 2 | Verification | Closed-loop feedback (STRICT only) | ~50/verification |
| 3 | Checkpoints | Progress aggregation & course correction | ~100/checkpoint |

### 1.3 Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Worklog capture rate | ≥95% | Entries vs tier-significant operations |
| Verification success rate | ≥98% | Pass/fail ratio for STRICT tasks |
| Course corrections from checkpoints | ≥10% | Checkpoint analysis triggering changes |
| User skip-compliance rate | ≤12% | `--skip-compliance` tracking |
| Total overhead (weighted avg) | ≤300 tokens | Token accounting |

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-001: Worklog Initialization
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers

**Description**:
System SHALL create a worklog entry at task start containing:
- Session identifier (ISO8601 timestamp-based)
- Task description (from user input)
- Classified compliance tier
- Initial todo breakdown (if applicable)

**Acceptance Criteria**:
```gherkin
Given a task is initiated via /sc:task
When the classification phase completes
Then a worklog memory SHALL be created at "_worklog/{session_id}"
And the worklog SHALL contain tier, timestamp, and task description
And the initialization SHALL complete within 500ms
And token cost SHALL NOT exceed 75 tokens
```

#### FR-002: Operation Logging
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers (scoped by significance)

**Description**:
System SHALL append entries to worklog for tier-significant operations:

| Operation | Tier Significance | Logged Fields |
|-----------|-------------------|---------------|
| TodoWrite | ALL | timestamp, action, todos_affected, status_changes |
| Edit/MultiEdit/Write | STRICT, STANDARD | timestamp, files_modified, change_summary |
| Bash (tests) | STRICT, STANDARD | timestamp, command, exit_code, summary |
| Task (sub-agent) | ALL | timestamp, agent_type, purpose, outcome |

**Acceptance Criteria**:
```gherkin
Given a tier-significant operation occurs
When the operation completes (success or failure)
Then an entry SHALL be appended to the worklog
And the entry SHALL include timestamp, operation type, and outcome
And append latency SHALL NOT exceed 200ms
And token cost per entry SHALL NOT exceed 30 tokens
```

#### FR-003: Batched Worklog Writes
**Priority**: P1 (Should Have)
**Tier Scope**: ALL tiers

**Description**:
To reduce MCP overhead, worklog entries SHALL be buffered and written in batches:
- Buffer threshold: 10 entries OR checkpoint trigger
- Flush on: buffer full, checkpoint, task completion, error

**Acceptance Criteria**:
```gherkin
Given 10 operations have been logged to buffer
When the 10th operation completes
Then all buffered entries SHALL be written to memory in a single call
And the buffer SHALL be cleared
And MCP calls SHALL be reduced by ≥80% compared to per-operation writes
```

#### FR-004: Status Verification (STRICT Tier)
**Priority**: P0 (Must Have)
**Tier Scope**: STRICT only

**Description**:
After each TodoWrite in STRICT tier tasks, system SHALL verify state consistency:

```
1. Capture intended state from TodoWrite arguments
2. Execute TodoWrite
3. Read current todo state
4. Assert: expected_status == actual_status for each todo
5. If mismatch:
   a. Log verification_failed to worklog
   b. Retry once
   c. If still failed: escalate to user
6. Log verification_passed to worklog
```

**Acceptance Criteria**:
```gherkin
Given a STRICT tier task executes TodoWrite
When the TodoWrite completes
Then system SHALL read current todo state
And system SHALL compare expected vs actual status
And mismatches SHALL be logged with context
And retry SHALL occur once on mismatch
And persistent mismatch SHALL escalate to user
And verification SHALL complete within 1000ms
And token cost SHALL NOT exceed 75 tokens per verification
```

#### FR-005: Checkpoint Summaries
**Priority**: P1 (Should Have)
**Tier Scope**: STRICT (3 checkpoints), STANDARD (1 checkpoint)

**Description**:
System SHALL generate progress summaries at phase boundaries:

| Checkpoint | Trigger | Content |
|------------|---------|---------|
| Planning Complete | Initial TodoWrite creates breakdown | Tier, approach, todo count |
| Execution Complete | Last Edit/Write operation | Operations summary, files changed |
| Verification Complete | Tests pass/fail | Test results, verification status |

**Acceptance Criteria**:
```gherkin
Given a STRICT task completes the execution phase
When the last Edit/Write operation finishes
Then system SHALL call think_about_task_adherence()
And system SHALL generate checkpoint summary from worklog
And summary SHALL include: operations count, files modified, deviations
And summary SHALL be appended to progress memory
And checkpoint SHALL complete within 2000ms
And token cost SHALL NOT exceed 150 tokens per checkpoint
```

#### FR-006: Worklog Finalization
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers

**Description**:
On task completion (success, failure, or user abort), system SHALL:
1. Flush any buffered worklog entries
2. Append completion record with outcome, duration, operation count
3. Generate final summary if STRICT/STANDARD tier

**Acceptance Criteria**:
```gherkin
Given a task completes (any outcome)
When the completion phase executes
Then all buffered entries SHALL be flushed
And a completion record SHALL be appended
And completion record SHALL include: outcome, duration, total operations
And worklog SHALL be queryable for post-mortem analysis
```

### 2.2 Non-Functional Requirements

#### NFR-001: Token Efficiency
**Description**: Accountability overhead SHALL remain within acceptable bounds.

| Tier | Max Overhead | Percentage of Typical Task |
|------|--------------|---------------------------|
| STRICT | 750 tokens | 15-25% of 3-5K task |
| STANDARD | 300 tokens | 6-10% of 3-5K task |
| LIGHT | 60 tokens | 2-4% of 1.5-3K task |
| EXEMPT | 0 tokens | 0% |

**Measurement**: Token accounting comparison before/after implementation.

#### NFR-002: Latency Impact
**Description**: Accountability operations SHALL NOT significantly impact task latency.

| Operation | Max Latency |
|-----------|-------------|
| Worklog append (buffered) | 50ms |
| Worklog flush | 300ms |
| Verification cycle | 1000ms |
| Checkpoint generation | 2000ms |

**Measurement**: Timing instrumentation in execution flow.

#### NFR-003: Memory Management
**Description**: Worklog storage SHALL NOT cause memory bloat.

| Retention Policy | Scope |
|-----------------|-------|
| Current session | Full worklog retained |
| Previous session | Summary only (aggregated) |
| Older sessions | Patterns extracted, raw logs deleted |

**Measurement**: Memory usage monitoring over 100-session sample.

#### NFR-004: Graceful Degradation
**Description**: Accountability failures SHALL NOT block task execution.

| Failure Mode | Behavior |
|--------------|----------|
| Memory write fails | Log warning, continue task |
| Verification timeout | Skip verification, log skip |
| Checkpoint generation fails | Continue without checkpoint |

**Measurement**: Error injection testing.

### 2.3 Constraints

#### C-001: MCP Tool Availability
- Requires Serena MCP for memory operations
- Falls back to session-only logging if Serena unavailable

#### C-002: Backward Compatibility
- Existing `/sc:task` invocations SHALL work without modification
- New flags are opt-out, not opt-in
- No breaking changes to tier classification or verification routing

#### C-003: No External Dependencies
- All accountability features use existing MCP tools
- No new infrastructure required
- No file system writes outside memory system

---

## 3. Technical Design

### 3.1 Worklog Schema

```yaml
worklog:
  version: "1.0"
  session_id: string          # Format: YYYYMMDD_HHMMSS
  task_description: string
  tier: enum[STRICT, STANDARD, LIGHT, EXEMPT]
  started_at: string          # ISO8601
  completed_at: string | null # ISO8601, null if in-progress
  outcome: enum[success, failure, aborted, in_progress]

  entries:
    - timestamp: string       # ISO8601
      action: enum[TodoWrite, Edit, Write, Bash, Task, Checkpoint, Verify]
      status: enum[initiated, completed, failed, retried, skipped]
      context: string         # Brief description
      details:                # Action-specific fields
        files?: string[]
        todos_affected?: number
        exit_code?: number
        verification_result?: enum[pass, fail, timeout]
      tokens_consumed: number

  summary:                    # Generated at completion
    total_operations: number
    files_modified: number
    todos_completed: number
    verification_results:
      passed: number
      failed: number
      skipped: number
    checkpoints_generated: number
    total_tokens: number
    duration_seconds: number
```

### 3.2 Memory Naming Convention

```
Worklog memories:
  _worklog/{session_id}           # Current session worklog
  _worklog_summary/{date}         # Daily aggregated summary

Progress memories:
  _progress/{task_hash}           # Task-specific progress

Checkpoint memories:
  _checkpoint/{session_id}/{n}    # Individual checkpoint (ephemeral)
```

**Rationale**: `_` prefix signals operational (not semantic) memories, enabling filtered `list_memories()` calls.

### 3.3 Verification State Machine

```
                    ┌─────────────┐
                    │ TodoWrite   │
                    │ Executed    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Read Todo   │
                    │ State       │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
             ┌──────────┐  ┌──────────┐
             │ Match    │  │ Mismatch │
             └────┬─────┘  └────┬─────┘
                  │             │
                  ▼             ▼
           ┌──────────┐  ┌──────────┐
           │ Log Pass │  │ Retry    │
           │ Continue │  │ (max: 1) │
           └──────────┘  └────┬─────┘
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                ┌──────────┐  ┌──────────┐
                │ Match    │  │ Still    │
                │ (retry)  │  │ Mismatch │
                └────┬─────┘  └────┬─────┘
                     │             │
                     ▼             ▼
              ┌──────────┐  ┌──────────┐
              │ Log Pass │  │ Escalate │
              │ Continue │  │ to User  │
              └──────────┘  └──────────┘
```

### 3.4 Checkpoint Triggers

```yaml
checkpoint_triggers:
  planning_complete:
    condition: "Initial TodoWrite creates ≥3 todos"
    actions:
      - think_about_task_adherence()
      - generate_checkpoint_summary(phase="planning")
      - write_memory("_checkpoint/{session}/{n}", summary)
    tier_scope: [STRICT]

  execution_complete:
    condition: "Last Edit/Write operation with no pending file modifications"
    actions:
      - think_about_task_adherence()
      - generate_checkpoint_summary(phase="execution")
      - write_memory("_checkpoint/{session}/{n}", summary)
    tier_scope: [STRICT, STANDARD]

  verification_complete:
    condition: "Test execution completes (pass or fail)"
    actions:
      - think_about_whether_you_are_done()
      - generate_checkpoint_summary(phase="verification")
      - write_memory("_checkpoint/{session}/{n}", summary)
    tier_scope: [STRICT]
```

### 3.5 Integration Points

#### 3.5.1 Existing SKILL.md Modification

Insert after "### 5. Feedback Collection":

```markdown
### 6. Accountability Framework

#### 6.1 Worklog (All Tiers)
[See Section 3.1 for schema]

#### 6.2 Status Verification (STRICT Only)
[See Section 3.3 for state machine]

#### 6.3 Checkpoint Summaries (STRICT/STANDARD)
[See Section 3.4 for triggers]

#### 6.4 Accountability Flags
--no-worklog       # Disable worklog (not recommended)
--skip-verify      # Skip STRICT verification
--no-checkpoints   # Disable checkpoint summaries
--verbose-log      # Include full tool results in worklog
```

#### 3.5.2 Tier Enforcement Modifications

```yaml
strict_tier_enforcement:
  existing_steps:
    # Steps 1-11 unchanged
  new_steps:
    - step: 12
      action: "Verify final todo state matches expectations"
      tool: "Internal verification loop"
    - step: 13
      action: "Generate final worklog summary"
      tool: "write_memory"

standard_tier_enforcement:
  existing_steps:
    # Steps 1-5 unchanged
  new_steps:
    - step: 6
      action: "Generate execution checkpoint"
      tool: "think_about_task_adherence, write_memory"
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Worklog Foundation (Week 1-2)

**Scope**: Worklog initialization, operation logging, batched writes, finalization

**Deliverables**:
1. Worklog schema implementation
2. Memory naming convention
3. Batched write buffer
4. Entry append logic for tier-significant operations
5. Finalization and summary generation

**Acceptance Tests**:
- [ ] Worklog created on task start
- [ ] Entries appended for Edit, Write, Bash, Task, TodoWrite
- [ ] Batch flush at threshold (10 entries)
- [ ] Finalization includes summary

**Rollout**: All tiers, no user-facing changes

### 4.2 Phase 2: STRICT Verification (Week 3-4)

**Scope**: Status verification loop for STRICT tier only

**Dependencies**: Phase 1 complete (worklog for verification context)

**Deliverables**:
1. Verification state machine implementation
2. Retry logic with exponential backoff
3. User escalation flow
4. `--skip-verify` flag implementation

**Acceptance Tests**:
- [ ] Verification runs after each STRICT TodoWrite
- [ ] Mismatches logged to worklog
- [ ] Single retry on mismatch
- [ ] User escalation on persistent mismatch
- [ ] `--skip-verify` bypasses verification

**Rollout**: STRICT tier only, default enabled

### 4.3 Phase 3: Checkpoint Summaries (Week 5-6)

**Scope**: Checkpoint generation at phase boundaries

**Dependencies**: Phase 1 complete (worklog for checkpoint content)

**Deliverables**:
1. Checkpoint trigger detection
2. Summary generation from worklog
3. Progress memory management
4. `--no-checkpoints` flag implementation

**Acceptance Tests**:
- [ ] STRICT tasks generate 3 checkpoints
- [ ] STANDARD tasks generate 1 checkpoint
- [ ] Checkpoints consume worklog entries
- [ ] `--no-checkpoints` disables generation

**Rollout**: STRICT and STANDARD tiers, default enabled

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test Category | Coverage Target | Location |
|---------------|-----------------|----------|
| Worklog schema validation | 100% | tests/accountability/test_worklog_schema.py |
| Entry append logic | 95% | tests/accountability/test_worklog_append.py |
| Batch buffer behavior | 95% | tests/accountability/test_batch_buffer.py |
| Verification state machine | 100% | tests/accountability/test_verification.py |
| Checkpoint generation | 90% | tests/accountability/test_checkpoints.py |

### 5.2 Integration Tests

| Scenario | Description | Expected Outcome |
|----------|-------------|------------------|
| STRICT task E2E | Full STRICT task with all accountability | Worklog + 3 verifications + 3 checkpoints |
| STANDARD task E2E | Full STANDARD task | Worklog + 1 checkpoint |
| Verification failure | Simulate TodoWrite mismatch | Retry, then escalate |
| Memory unavailable | Simulate Serena failure | Graceful degradation, warning logged |
| Flag overrides | Test all `--no-*` flags | Features disabled as expected |

### 5.3 Performance Tests

| Test | Metric | Target |
|------|--------|--------|
| Worklog overhead | Token count | ≤300 tokens (weighted avg) |
| Verification latency | Time | ≤1000ms per verification |
| Checkpoint latency | Time | ≤2000ms per checkpoint |
| Memory growth | Bytes/session | ≤50KB per session |

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Memory bloat from worklogs | Medium | Medium | TTL-based cleanup, summary aggregation |
| Verification false positives | Low | High | Single retry, user escalation path |
| Checkpoint overhead in tight token budgets | Medium | Low | Tier-scoped (LIGHT/EXEMPT exempt) |
| MCP latency spikes | Low | Medium | Timeouts, graceful degradation |

### 6.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Users bypass with `--no-*` flags | Medium | Low | Track usage, adjust defaults |
| Accountability theater (process without value) | Medium | Medium | Measure checkpoint utility rate |
| Increased complexity for contributors | Low | Medium | Documentation, examples |

---

## 7. Appendices

### A. Token Budget Calculation

```yaml
STRICT task (10 todos, 30 operations):
  worklog:
    initialization: 50 tokens
    entries: 30 × 20 = 600 tokens (but batched to 3 writes × 200 = 600)
    finalization: 75 tokens
    subtotal: 725 tokens (actual MCP cost: ~300 due to batching)

  verification:
    verifications: 10 × 50 = 500 tokens (only for TodoWrite)
    retries (5%): 0.5 × 75 = 37.5 tokens
    subtotal: 537.5 tokens

  checkpoints:
    checkpoints: 3 × 100 = 300 tokens
    subtotal: 300 tokens

  TOTAL: ~1137 tokens (before batching optimization)
  ACTUAL: ~750 tokens (with batching)
```

### B. Worklog Entry Examples

```yaml
# TodoWrite entry
- timestamp: "2026-01-26T14:32:15Z"
  action: "TodoWrite"
  status: "completed"
  context: "Updated task 'Implement auth' to in_progress"
  details:
    todos_affected: 1
    status_changes: [{ id: "1.1", from: "pending", to: "in_progress" }]
  tokens_consumed: 45

# Edit entry
- timestamp: "2026-01-26T14:33:22Z"
  action: "Edit"
  status: "completed"
  context: "Added validateToken() to auth/middleware.js"
  details:
    files: ["auth/middleware.js"]
  tokens_consumed: 120

# Verification entry
- timestamp: "2026-01-26T14:33:45Z"
  action: "Verify"
  status: "completed"
  context: "TodoWrite verification for task 1.1"
  details:
    verification_result: "pass"
  tokens_consumed: 52

# Checkpoint entry
- timestamp: "2026-01-26T14:45:00Z"
  action: "Checkpoint"
  status: "completed"
  context: "Execution phase complete"
  details:
    operations_since_last: 12
    files_modified: 3
    deviations: []
  tokens_consumed: 95
```

### C. Flag Reference

| Flag | Effect | Default | Recommendation |
|------|--------|---------|----------------|
| `--no-worklog` | Disable all worklog functionality | Enabled | Not recommended |
| `--skip-verify` | Skip STRICT verification | Enabled | Use for trusted environments |
| `--no-checkpoints` | Disable checkpoint summaries | Enabled | Use for time-critical tasks |
| `--verbose-log` | Include full tool results | Disabled | Use for debugging |

### D. Migration Guide

**Existing sc:task-unified users**:
1. No action required - accountability enabled by default
2. Worklog memories will appear with `_worklog/` prefix
3. To disable, use `--no-worklog --skip-verify --no-checkpoints`

**SKILL.md maintainers**:
1. Add Section 6 (Accountability Framework) after Section 5
2. Update tier enforcement steps as specified in Section 3.5.2
3. Add new flags to flag reference table

---

## 8. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | Claude Opus 4.5 | Initial draft from adversarial debate |
| 1.1.0 | TBD | Pending | Post spec-panel review |
| 1.2.0 | TBD | Pending | Post reflection verification |
| 1.3.0 | TBD | Pending | Final approved version |
