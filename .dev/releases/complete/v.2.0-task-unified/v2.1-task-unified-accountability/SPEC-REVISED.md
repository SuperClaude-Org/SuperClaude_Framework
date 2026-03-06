# Specification: sc:task-unified Accountability Framework v1.3

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.3.1 |
| Status | Reviewed - Expert Panel Validated |
| Created | 2026-01-26 |
| Authors | Claude Opus 4.5, Adversarial Debate Panel |
| Reviewers | Wiegers, Adzic, Nygard, Fowler (spec-panel) |
| Classification | Feature Enhancement |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.3.0 | 2026-01-26 | Initial draft from adversarial debate |
| 1.3.1 | 2026-01-26 | Addressed P0/P1 issues from spec-panel review |
| 1.3.2 | 2026-01-26 | Added FR-007 (Checkpoint Detection), confirmed NFR-005 (Session ID MCP Independence) |

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
| Course corrections from checkpoints | ≥10% | Checkpoint triggers think_about_task_adherence() returning ADJUSTMENT_NEEDED |
| User skip-compliance rate | ≤12% | `--skip-compliance` tracking |
| Total overhead (weighted avg) | ≤300 tokens | Token accounting |

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-001: Worklog Initialization
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers

**Description**:
System SHALL create a worklog entry at task start when:
- Tier classification is determined (STRICT|STANDARD|LIGHT|EXEMPT)
- BEFORE any tier-significant operation begins

**Trigger Definition**:
```yaml
initialization_trigger:
  event: "Tier classification complete"
  precondition: "Task description parsed, compliance tier assigned"
  timing: "Before first tier-significant operation"
  explicit_signal: "After TodoWrite creates initial task breakdown OR before first Edit/Write/Bash"
```

**Acceptance Criteria**:
```gherkin
Scenario Outline: Worklog initialization for different tiers
  Given a task "<description>" is initiated via /sc:task
  When the tier is classified as <tier> with confidence <confidence>
  Then a worklog memory SHALL be created at "_worklog/<session_id>"
  And the worklog SHALL contain:
    | field | value |
    | tier | <tier> |
    | task_description | "<description>" |
    | started_at | ISO8601 timestamp |
  And initialization SHALL complete within 500ms
  And token cost SHALL NOT exceed 75 tokens

Examples:
  | description | tier | confidence | session_id_format |
  | "implement JWT auth" | STRICT | 0.92 | 20260126_143215 |
  | "add pagination" | STANDARD | 0.85 | 20260126_143216 |
  | "fix typo in README" | LIGHT | 0.88 | 20260126_143217 |
  | "explain auth flow" | EXEMPT | 0.95 | 20260126_143218 |
```

#### FR-002: Operation Logging
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers (scoped by significance)

**Description**:
System SHALL append entries to worklog for tier-significant operations.

**Tier Significance Policy**:
```yaml
tier_significance_policy:
  version: "1.0"

  included_operations:
    TodoWrite:
      tiers: [STRICT, STANDARD, LIGHT, EXEMPT]
      rationale: "State mutation - always tracked"
    Edit:
      tiers: [STRICT, STANDARD]
      rationale: "File modification - tracked for code-changing tiers"
    MultiEdit:
      tiers: [STRICT, STANDARD]
      rationale: "Batch file modification - tracked for code-changing tiers"
    Write:
      tiers: [STRICT, STANDARD]
      rationale: "File creation - tracked for code-changing tiers"
    Bash:
      tiers: [STRICT, STANDARD]
      filter: "Commands containing: test, pytest, jest, npm test, make test, cargo test, go test"
      rationale: "Test execution - tracked for verification"
    Task:
      tiers: [STRICT, STANDARD, LIGHT, EXEMPT]
      rationale: "Sub-agent spawn - always tracked for accountability"

  excluded_operations:
    Read: "Read-only, no state change"
    Glob: "Search only, no state change"
    Grep: "Search only, no state change"
    WebFetch: "External data retrieval, not local state"
    think_about_*: "Internal analysis, not external action"
```

**Acceptance Criteria**:
```gherkin
Scenario Outline: Operation logging for tier-significant operations
  Given a <tier> tier task is executing
  And the worklog buffer has <buffer_count> entries
  When a <operation> operation completes with status <status>
  Then an entry SHALL be appended to the worklog buffer
  And the entry SHALL include:
    | field | value |
    | timestamp | ISO8601 |
    | action | <operation> |
    | status | <status> |
    | context | Brief description of operation |
  And append latency SHALL NOT exceed 200ms
  And token cost per entry SHALL NOT exceed 30 tokens

Examples:
  | tier | buffer_count | operation | status |
  | STRICT | 3 | Edit | completed |
  | STRICT | 5 | TodoWrite | completed |
  | STANDARD | 2 | Bash | failed |
  | LIGHT | 0 | TodoWrite | completed |
```

#### FR-003: Batched Worklog Writes
**Priority**: P1 (Should Have)
**Tier Scope**: ALL tiers

**Description**:
To reduce MCP overhead, worklog entries SHALL be buffered and written in batches.

**Buffer Configuration**:
```yaml
buffer_config:
  threshold_entries: 10
  threshold_time_seconds: 30  # NEW: Time-based flush for durability

  flush_triggers:
    - condition: "buffer.length >= 10"
      name: "threshold_flush"
    - condition: "time_since_last_flush >= 30s"
      name: "time_flush"
    - condition: "checkpoint_triggered"
      name: "checkpoint_flush"
    - condition: "task_completing"
      name: "completion_flush"
    - condition: "error_may_terminate_execution"
      name: "error_flush"
      definition: "Bash exit code != 0, exception raised, user abort signal"
```

**Acceptance Criteria**:
```gherkin
Scenario: Threshold-based buffer flush
  Given a task has logged 9 operations to buffer
  When the 10th operation completes
  Then all 10 buffered entries SHALL be written to memory in a single call
  And the buffer SHALL be cleared
  And MCP calls SHALL be reduced by ≥80% compared to per-operation writes

Scenario: Time-based buffer flush for durability
  Given a task has logged 5 operations to buffer
  And 30 seconds have elapsed since last flush
  When the time threshold is reached
  Then all 5 buffered entries SHALL be flushed
  And the buffer SHALL be cleared
  And no entries SHALL be lost on unexpected termination within 30s window

Scenario: Error-triggered flush
  Given a task has 7 entries in the worklog buffer
  When a Bash operation fails with exit code 1
  Then the buffer SHALL be immediately flushed (including failure entry)
  And the worklog SHALL preserve the audit trail for post-mortem
```

#### FR-004: Status Verification (STRICT Tier)
**Priority**: P0 (Must Have)
**Tier Scope**: STRICT only

**Description**:
After each TodoWrite in STRICT tier tasks, system SHALL verify state consistency.

**State Consistency Criteria**:
```yaml
verification_criteria:
  required_matches:
    - field: "status"
      comparison: "exact"
      rationale: "Status is the primary verification target"
    - field: "count"
      comparison: "expected_count == actual_todos.length"
      rationale: "Ensure no todos were dropped"

  ignored_fields:
    - field: "content"
      rationale: "User may edit todo descriptions"
    - field: "activeForm"
      rationale: "Display variant, not semantic state"

  mismatch_types:
    status_mismatch: "todo.status != expected_status"
    count_mismatch: "todos.length != expected_count"
    missing_todo: "Expected todo not found by content match"
```

**Circuit Breaker**:
```yaml
verification_circuit_breaker:
  max_automatic_retries: 1
  max_total_attempts: 3  # Including user-initiated retries
  cooldown_after_max: 300s  # 5 minutes
  forced_resolution_options:
    - id: "accept"
      label: "Accept current state as correct"
      action: "Mark verification as 'user_accepted', continue"
    - id: "abort"
      label: "Abort task with partial worklog"
      action: "Finalize worklog with outcome='aborted', stop"
    - id: "continue"
      label: "Continue without verification (log risk)"
      action: "Mark verification as 'bypassed', continue with warning"
```

**Acceptance Criteria**:
```gherkin
Scenario: Verification passes on first attempt
  Given a STRICT tier task executes TodoWrite to mark "auth-impl" as "completed"
  When the system reads current todo state
  And the status matches: expected="completed", actual="completed"
  Then verification SHALL pass
  And worklog SHALL record: {action: "Verify", status: "completed", verification_result: "pass"}
  And task execution SHALL continue

Scenario: Verification fails, retry succeeds
  Given a STRICT tier task executes TodoWrite to mark "auth-impl" as "completed"
  When the first read shows: expected="completed", actual="pending"
  Then verification SHALL fail
  And system SHALL retry once after 100ms
  When the retry read shows: expected="completed", actual="completed"
  Then verification SHALL pass
  And worklog SHALL record both attempts

Scenario: Verification fails after retry, escalates to user
  Given a STRICT tier task has verification failure after retry
  When user is presented with resolution options
  And user selects "Accept current state as correct"
  Then verification SHALL be marked "user_accepted"
  And worklog SHALL record the user decision
  And task execution SHALL continue

Scenario: Circuit breaker prevents infinite retry loop
  Given a STRICT tier task has failed verification 3 times total
  When another retry is attempted
  Then the circuit breaker SHALL open
  And user SHALL be forced to select a resolution option
  And no automatic retries SHALL occur for 300 seconds
```

#### FR-005: Checkpoint Summaries
**Priority**: P1 (Should Have)
**Tier Scope**: STRICT (3 checkpoints), STANDARD (1 checkpoint)

**Description**:
System SHALL generate progress summaries at phase boundaries.

**Checkpoint Tier Mapping**:
```yaml
checkpoint_tier_mapping:
  STRICT:
    checkpoints:
      - name: "planning_complete"
        trigger: "Initial TodoWrite creates ≥3 todos"
      - name: "execution_complete"
        trigger: "Last Edit/Write operation with no pending file modifications"
      - name: "verification_complete"
        trigger: "Test execution completes (pass or fail)"
    count: 3

  STANDARD:
    checkpoints:
      - name: "execution_complete"
        trigger: "Last Edit/Write operation with no pending file modifications"
    count: 1

  LIGHT:
    checkpoints: []
    count: 0

  EXEMPT:
    checkpoints: []
    count: 0
```

**Checkpoint Content**:
```yaml
checkpoint_summary_schema:
  phase: string  # planning, execution, verification
  timestamp: string  # ISO8601
  operations_since_last: number
  files_modified: string[]
  todos_completed: number
  todos_remaining: number
  deviations:
    - type: enum[todo_incomplete, unplanned_file, test_failure]
      description: string
      severity: enum[low, medium, high]
  verification_results:
    passed: number
    failed: number
    skipped: number
```

**Acceptance Criteria**:
```gherkin
Scenario Outline: Checkpoint generation varies by tier
  Given a <tier> tier task is executing
  When the <phase> phase completes
  Then a checkpoint <should_generate>
  And if generated, the checkpoint SHALL include operations count, files modified, deviations

Examples:
  | tier | phase | should_generate |
  | STRICT | planning | SHALL be generated |
  | STRICT | execution | SHALL be generated |
  | STRICT | verification | SHALL be generated |
  | STANDARD | execution | SHALL be generated |
  | LIGHT | any | SHALL NOT be generated |
  | EXEMPT | any | SHALL NOT be generated |
```

#### FR-006: Worklog Finalization
**Priority**: P0 (Must Have)
**Tier Scope**: ALL tiers

**Description**:
On task completion (success, failure, or user abort), system SHALL finalize worklog.

**Acceptance Criteria**:
```gherkin
Scenario Outline: Worklog finalization for different outcomes
  Given a <tier> task has been executing with <operation_count> operations logged
  When the task completes with outcome <outcome>
  Then all buffered entries SHALL be flushed
  And a completion record SHALL be appended with:
    | field | value |
    | outcome | <outcome> |
    | duration | Elapsed time in seconds |
    | total_operations | <operation_count> |
  And worklog SHALL be readable via read_memory("_worklog/<session_id>")

Examples:
  | tier | operation_count | outcome |
  | STRICT | 25 | success |
  | STANDARD | 12 | success |
  | STRICT | 8 | failure |
  | STANDARD | 3 | aborted |
```

#### FR-007: Smart Checkpoint Detection
**Priority**: P2 (Could Have)
**Tier Scope**: STRICT, STANDARD only

**Description**:
System SHALL detect abandoned or in-progress worklogs from previous sessions and notify user of restoration options. This provides cross-session continuity without mandatory `/sc:load` integration.

**Detection Configuration**:
```yaml
checkpoint_detection:
  timing:
    trigger: "After tier classification completes"
    position: "Before worklog initialization"
    timeout_ms: 500  # Fits within 3000ms aggregate budget

  tier_scope:
    STRICT: "Always run detection"
    STANDARD: "Always run detection"
    LIGHT: "Skip detection (overhead not justified)"
    EXEMPT: "Skip detection"

  memory_patterns:
    - namespace: "_worklog/*"
      filter: "outcome IN ['abandoned', 'in_progress']"
      max_scan: 10  # LRU by started_at, prevents performance degradation

  matching_strategy:
    type: "exact_session"  # No fuzzy matching - performance and reliability
    match_fields: ["session_id"]  # Not task similarity

  restore_command:
    configurable: true
    default: "/sc:load --checkpoint {session_id}"

  failure_handling:
    timeout: "Skip detection silently, continue task"
    mcp_error: "Log warning, skip detection, continue task"
    no_results: "No notification, continue normally"
```

**Output Format**:
```yaml
notification_format:
  template: |
    ℹ️ Previous work detected: {task_description} ({outcome})
    Session: {session_id} | Started: {started_at}
    To restore: {restore_command}

  display_conditions:
    - "At least one matching worklog found"
    - "Worklog outcome is 'abandoned' or 'in_progress'"
    - "Detection completed within timeout"
```

**Acceptance Criteria**:
```gherkin
Scenario: Abandoned worklog detected for STRICT task
  Given a user starts /sc:task "implement user authentication"
  And tier classification completes as STRICT
  And memory "_worklog/20260125_143215_001" exists with:
    | field | value |
    | outcome | abandoned |
    | task_description | "implement user authentication" |
  When checkpoint detection runs
  Then notification SHALL display:
    | element | value |
    | message | "Previous work detected: implement user authentication (abandoned)" |
    | session | "20260125_143215_001" |
    | restore | "/sc:load --checkpoint 20260125_143215_001" |
  And detection SHALL complete within 500ms
  And task execution SHALL continue after notification

Scenario: No relevant previous work found
  Given a user starts /sc:task "add pagination to user list"
  And tier classification completes as STANDARD
  And no worklogs exist with outcome in ['abandoned', 'in_progress']
  When checkpoint detection runs
  Then no notification SHALL be displayed
  And task execution SHALL proceed immediately

Scenario: Detection skipped for LIGHT tier
  Given a user starts /sc:task "fix typo in README"
  And tier classification completes as LIGHT
  When execution begins
  Then checkpoint detection SHALL NOT run
  And no latency penalty SHALL be incurred

Scenario: Detection timeout handling
  Given a user starts /sc:task "implement feature"
  And tier classification completes as STANDARD
  And list_memories takes >500ms to respond
  When checkpoint detection times out
  Then detection SHALL be silently skipped
  And task execution SHALL continue
  And worklog SHALL log: {action: "CheckpointDetection", status: "timeout"}

Scenario: Successful worklog ignored (not actionable)
  Given a user starts /sc:task "refactor auth module"
  And memory "_worklog/20260126_100000_001" exists with outcome="success"
  When checkpoint detection runs
  Then no notification SHALL be displayed
  Because completed work doesn't need restoration
```

**Interface Definition**:
```typescript
interface CheckpointDetectionService {
  /**
   * Detect abandoned/in-progress worklogs from previous sessions.
   * Returns null if no relevant worklogs found or detection skipped.
   */
  detect(tier: Tier): Promise<DetectionResult | null>;

  /**
   * Format detection result as user notification.
   */
  formatNotification(result: DetectionResult): string;

  /**
   * Check if detection should run for this tier.
   */
  shouldDetect(tier: Tier): boolean;
}

interface DetectionResult {
  session_id: string;
  outcome: "abandoned" | "in_progress";
  task_description: string;
  started_at: string;  // ISO8601
  restore_command: string;
}
```

### 2.2 Non-Functional Requirements

#### NFR-001: Token Efficiency
**Description**: Accountability overhead SHALL remain within acceptable bounds.

**Token Bounds**:
```yaml
token_overhead:
  STRICT:
    with_batching: 750 tokens  # Expected with all optimizations
    without_batching: 1200 tokens  # Maximum if batching unavailable
    percentage_of_task: "15-25% of 3-5K task"

  STANDARD:
    with_batching: 300 tokens
    without_batching: 500 tokens
    percentage_of_task: "6-10% of 3-5K task"

  LIGHT:
    with_batching: 60 tokens
    without_batching: 100 tokens
    percentage_of_task: "2-4% of 1.5-3K task"

  EXEMPT:
    with_batching: 0 tokens
    without_batching: 0 tokens
    percentage_of_task: "0%"

degradation_behavior:
  condition: "Batching unavailable (e.g., flush failures)"
  action: "Log warning, proceed with per-entry writes"
  user_notification: "Accountability overhead increased due to batching unavailability"
```

#### NFR-002: Latency Impact
**Description**: Accountability operations SHALL NOT significantly impact task latency.

| Operation | Max Latency | Aggregate Budget |
|-----------|-------------|------------------|
| Worklog append (buffered) | 50ms | N/A (in-memory) |
| Worklog flush | 300ms | Part of 3000ms aggregate |
| Verification cycle | 1000ms | Part of 3000ms aggregate |
| Checkpoint generation | 2000ms | Part of 3000ms aggregate |
| **Total accountability phase** | **3000ms** | Hard ceiling |

**Timeout Handling**:
```yaml
aggregate_timeout:
  budget_ms: 3000
  enforcement: "If any accountability operation would exceed remaining budget, skip and log"
  adaptive_behavior:
    trigger: "Previous phase used >80% of its allocation"
    action: "Skip optional operations (checkpoints) in next phase"
```

#### NFR-003: Memory Management
**Description**: Worklog storage SHALL NOT cause memory bloat.

**Retention Policy**:
```yaml
retention_policy:
  current_session:
    content: "Full worklog retained"
    storage: "_worklog/{session_id}"

  previous_session:
    content: "Summary only"
    transformation: "Aggregate entries into summary statistics"
    storage: "_worklog_summary/{date}"

  older_sessions:
    age_threshold: "24 hours"
    content: "Deleted after summary extraction"
    cleanup_trigger: "On each session start"

cleanup_on_session_start:
  - "Scan for worklogs with outcome='in_progress' older than 24h"
  - "Mark as outcome='abandoned'"
  - "Extract summary to _worklog_summary/{date}"
  - "Delete raw worklog"

storage_limits:
  max_active_worklogs: 50
  eviction_policy: "LRU by last_modified"
  warning_threshold: 40
```

#### NFR-004: Graceful Degradation
**Description**: Accountability failures SHALL NOT block task execution.

| Failure Mode | Behavior | User Notification |
|--------------|----------|-------------------|
| Memory write fails | Log warning, continue task | "Worklog unavailable, continuing with session-only logging" |
| Verification timeout | Skip verification, log skip | "Verification timed out, proceeding without state confirmation" |
| Checkpoint generation fails | Continue without checkpoint | Silent (logged to worklog) |
| Serena MCP unavailable | Fall back to session-only | **REQUIRED**: Alert user at task start |

**Serena Fallback Specification**:
```yaml
serena_fallback:
  detection: "list_memories() timeout > 5s OR error response"

  fallback_mode:
    storage: "In-memory dict, session-scoped"
    queryable: true
    persistence: "Lost on session end"
    promotion_on_reconnect: false

  user_notification:
    timing: "On first operation after fallback detection"
    message: |
      ⚠️ Memory system unavailable. Continuing with session-only logging.
      Audit trail will not persist beyond this session.
      To retry with full logging, use: /sc:task --retry-memory

  tier_impact:
    STRICT: "Warn user but continue (compliance compromised)"
    STANDARD: "Continue with warning"
    LIGHT: "Continue silently"
    EXEMPT: "No impact"
```

#### NFR-005: Session ID MCP Independence
**Description**: Session ID generation SHALL NOT depend on any MCP server availability.

**Rationale**:
Session IDs are foundational to worklog initialization. If session ID generation depended on MCP, a Serena outage would prevent even basic task tracking. Local generation ensures accountability can always begin.

**Implementation Requirements**:
```yaml
session_id_generation:
  mcp_dependency: none  # CONFIRMED: No MCP calls required
  fallback_required: false  # No fallback needed since local-only
  failure_modes: []  # Local timestamp + counter cannot fail

  generation_algorithm:
    step_1: "Get current UTC timestamp"
    step_2: "Format as YYYYMMDD_HHMMSS"
    step_3: "Append monotonic counter (000-999)"
    step_4: "Return session_id string"

  uniqueness_guarantee:
    scope: "Per-process per-second"
    collision_prevention: "Monotonic counter resets each second"

  counter_overflow_handling:
    condition: "NNN reaches 999 within same second"
    action: "Wait for next second, reset counter to 000"
    probability: "Negligible (<0.0001% under normal usage)"
```

**Acceptance Criteria**:
```gherkin
Scenario: Session ID generated without MCP
  Given Serena MCP is unavailable (timeout or connection error)
  When a task starts and requires session ID
  Then session ID SHALL be generated locally
  And format SHALL be "YYYYMMDD_HHMMSS_NNN"
  And no MCP call SHALL be attempted for ID generation
  And worklog initialization SHALL proceed normally

Scenario: Concurrent tasks in same second
  Given two tasks start within the same second
  When session IDs are generated
  Then first task SHALL receive session_id ending in "001"
  And second task SHALL receive session_id ending in "002"
  And both IDs SHALL be unique

Scenario: High-volume task starts
  Given 1000 tasks start within one second (hypothetical stress test)
  When the counter would exceed 999
  Then generation SHALL wait for next second
  And counter SHALL reset to 000
  And no duplicate IDs SHALL be generated
```

### 2.3 Constraints

#### C-001: MCP Tool Availability
- Requires Serena MCP for persistent memory operations
- Falls back to session-only logging if Serena unavailable (see NFR-004)

#### C-002: Backward Compatibility
- Existing `/sc:task` invocations SHALL work without modification
- New flags are opt-out, not opt-in
- No breaking changes to tier classification or verification routing

**Clarification**:
```yaml
backward_compatibility_scope:
  unchanged:
    - "Tier classification algorithm"
    - "Verification routing"
    - "Command syntax"
    - "Task execution flow"

  new_default_behaviors:
    - "Worklog creation (silent, no user action required)"
    - "Checkpoint generation (silent)"

  definition: |
    Backward compatible means existing commands work without user modification.
    Users will see new artifacts (_worklog/ memories) but no action is required.
```

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
  session_id: string          # Format: YYYYMMDD_HHMMSS_NNN (NNN = monotonic counter)
  task_description: string
  tier: enum[STRICT, STANDARD, LIGHT, EXEMPT]
  started_at: string          # ISO8601
  completed_at: string | null # ISO8601, null if in-progress
  outcome: enum[success, failure, aborted, abandoned, in_progress]

  entries:
    - timestamp: string       # ISO8601
      action: enum[TodoWrite, Edit, MultiEdit, Write, Bash, Task, Checkpoint, Verify]
      status: enum[initiated, completed, failed, retried, skipped, timeout]
      context: string         # Brief description
      details: EntryDetails   # Discriminated union by action type
      tokens_consumed: number

  summary:                    # Generated at completion
    total_operations: number
    files_modified: number
    todos_completed: number
    verification_results:
      passed: number
      failed: number
      skipped: number
      user_accepted: number
    checkpoints_generated: number
    total_tokens: number
    duration_seconds: number
```

**Entry Details (Discriminated Union)**:
```yaml
EntryDetails:
  oneOf:
    - type: TodoWriteDetails
      action: "TodoWrite"
      properties:
        todos_affected: number
        status_changes:
          - id: string
            from: string
            to: string

    - type: EditDetails
      action: "Edit"
      properties:
        files: string[]
        change_summary: string

    - type: BashDetails
      action: "Bash"
      properties:
        command_type: string  # "test", "build", "script"
        exit_code: number

    - type: VerifyDetails
      action: "Verify"
      properties:
        verification_result: enum[pass, fail, timeout, user_accepted, bypassed]
        expected_state: object
        actual_state: object
        mismatch_details: string | null

    - type: CheckpointDetails
      action: "Checkpoint"
      properties:
        phase: string
        operations_count: number
        deviations: string[]

    - type: TaskDetails
      action: "Task"
      properties:
        agent_type: string
        purpose: string
        outcome: string
```

### 3.2 Memory Naming Convention

```yaml
memory_namespaces:
  worklog:
    pattern: "_worklog/{session_id}"
    retention: "Current session"

  worklog_summary:
    pattern: "_worklog_summary/{YYYY-MM-DD}"
    retention: "30 days"
    content: "Aggregated daily statistics"

  progress:
    pattern: "_progress/{task_hash}"
    retention: "Until task completion"
    content: "Real-time progress for active task"

  checkpoint:
    pattern: "_checkpoint/{session_id}/{n}"
    retention: "Ephemeral (deleted on task completion)"
    content: "Individual checkpoint data"

session_id_generation:
  format: "YYYYMMDD_HHMMSS_NNN"
  NNN: "Monotonic counter per process, 000-999"
  uniqueness: "Guaranteed per-process per-second"
  example: "20260126_143215_001"
```

### 3.3 Verification State Machine

```
                         ┌─────────────────┐
                         │   TodoWrite     │
                         │   Executed      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Read Todo     │
                         │   State         │──── timeout (1000ms) ────┐
                         └────────┬────────┘                          │
                                  │                                   │
                    ┌─────────────┴─────────────┐                     │
                    ▼                           ▼                     ▼
             ┌──────────┐                ┌──────────┐          ┌──────────┐
             │  Match   │                │ Mismatch │          │ Timeout  │
             └────┬─────┘                └────┬─────┘          └────┬─────┘
                  │                           │                     │
                  ▼                           ▼                     │
           ┌──────────┐                ┌──────────┐                │
           │ Log Pass │                │  Retry   │                │
           │ Continue │                │ (max: 1) │◄───────────────┘
           └──────────┘                └────┬─────┘
                                            │
                                   ┌────────┴────────┐
                                   ▼                 ▼
                            ┌──────────┐      ┌──────────┐
                            │  Match   │      │  Still   │
                            │ (retry)  │      │ Mismatch │
                            └────┬─────┘      └────┬─────┘
                                 │                 │
                                 ▼                 ▼
                          ┌──────────┐      ┌───────────────────┐
                          │ Log Pass │      │ Check Circuit     │
                          │ Continue │      │ Breaker (3 total) │
                          └──────────┘      └─────────┬─────────┘
                                                      │
                                        ┌─────────────┴─────────────┐
                                        ▼                           ▼
                                 ┌──────────┐                ┌──────────┐
                                 │ Escalate │                │ Forced   │
                                 │ to User  │                │ Resolution│
                                 └────┬─────┘                └──────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ┌──────────┐      ┌──────────┐      ┌──────────┐
             │ Accept   │      │  Abort   │      │ Continue │
             │ Current  │      │  Task    │      │ At Risk  │
             └──────────┘      └──────────┘      └──────────┘
```

### 3.4 Component Interfaces

```typescript
interface WorklogService {
  initialize(session: SessionId, task: TaskDescription, tier: Tier): WorklogHandle;
  append(entry: WorklogEntry): void;  // Buffers internally
  flush(): Promise<void>;             // Writes buffer to memory
  finalize(outcome: Outcome): Promise<WorklogSummary>;
  onError(error: Error): void;        // Triggers emergency flush
}

interface VerificationService {
  shouldVerify(tier: Tier): boolean;
  verifyTodoState(expected: TodoState, actual: TodoState): VerificationResult;
  handleMismatch(result: VerificationResult): Resolution;
  checkCircuitBreaker(): CircuitState;
  recordUserResolution(resolution: UserResolution): void;
}

interface CheckpointService {
  shouldCheckpoint(tier: Tier, phase: Phase): boolean;
  generateSummary(worklog: WorklogHandle, phase: Phase): CheckpointSummary;
  recordCheckpoint(checkpoint: CheckpointSummary): Promise<void>;
}

interface AccountabilityOrchestrator {
  onTaskStart(task: Task): void;
  onOperation(operation: Operation, result: Result): void;
  onPhaseComplete(phase: Phase): void;
  onTaskComplete(outcome: Outcome): void;
  onError(error: Error): void;
}
```

### 3.5 Configuration Schema

```yaml
accountability_config:
  version: "1.0"

  worklog:
    buffer_size: 10
    buffer_time_seconds: 30
    init_timeout_ms: 500
    append_timeout_ms: 200
    flush_timeout_ms: 300

  verification:
    enabled_tiers: [STRICT]
    max_automatic_retries: 1
    max_total_attempts: 3
    timeout_ms: 1000
    retry_delay_ms: 100
    circuit_breaker_cooldown_s: 300

  checkpoints:
    STRICT: [planning_complete, execution_complete, verification_complete]
    STANDARD: [execution_complete]
    LIGHT: []
    EXEMPT: []
    timeout_ms: 2000

  retention:
    current_session: full
    previous_session: summary
    older_sessions_ttl_hours: 24
    max_active_worklogs: 50

  aggregate_timeout_ms: 3000
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Worklog Foundation (Week 1-2)

**Scope**: Worklog initialization, operation logging, batched writes, finalization

**Deliverables**:
1. Worklog schema implementation (discriminated unions)
2. Session ID generation with uniqueness guarantee
3. Memory naming convention implementation
4. Batched write buffer with time-based flush (30s)
5. Entry append logic with tier significance policy
6. Finalization and summary generation
7. Emergency flush on error

**Acceptance Tests**:
- [ ] Worklog created on task start with correct schema
- [ ] Entries appended for all tier-significant operations
- [ ] Batch flush at threshold (10 entries)
- [ ] Time-based flush at 30 seconds
- [ ] Error-triggered flush preserves audit trail
- [ ] Finalization includes summary with all metrics

**Rollout**: All tiers, default enabled, no user-facing changes

### 4.2 Phase 2: STRICT Verification (Week 3-4)

**Scope**: Status verification loop for STRICT tier only

**Dependencies**: Phase 1 complete (worklog for verification context)

**Deliverables**:
1. Verification state machine implementation
2. State consistency criteria (status + count matching)
3. Single retry with 100ms delay
4. Circuit breaker (max 3 total attempts)
5. User escalation with resolution options
6. `--skip-verify` flag implementation
7. Serena fallback user notification

**Acceptance Tests**:
- [ ] Verification runs after each STRICT TodoWrite
- [ ] Mismatches logged with expected vs actual state
- [ ] Single retry on mismatch with delay
- [ ] Circuit breaker opens after 3 total attempts
- [ ] User resolution options work correctly
- [ ] `--skip-verify` bypasses verification
- [ ] Serena unavailable shows user notification

**Rollout**: STRICT tier only, default enabled

### 4.3 Phase 3: Checkpoint Summaries (Week 5-6)

**Scope**: Checkpoint generation at phase boundaries

**Dependencies**: Phase 1 complete (worklog for checkpoint content)

**Deliverables**:
1. Checkpoint trigger detection
2. Tier-based checkpoint mapping
3. Summary generation from worklog (consuming entries)
4. Progress memory management
5. Deviation detection and reporting
6. `--no-checkpoints` flag implementation
7. Aggregate timeout budget enforcement

**Acceptance Tests**:
- [ ] STRICT tasks generate 3 checkpoints at correct phases
- [ ] STANDARD tasks generate 1 checkpoint at execution complete
- [ ] LIGHT/EXEMPT tasks generate 0 checkpoints
- [ ] Checkpoints consume worklog entries correctly
- [ ] Deviations detected and reported
- [ ] `--no-checkpoints` disables generation
- [ ] Aggregate timeout prevents runaway latency

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
| Circuit breaker logic | 100% | tests/accountability/test_circuit_breaker.py |
| Checkpoint generation | 90% | tests/accountability/test_checkpoints.py |
| Tier significance policy | 100% | tests/accountability/test_tier_policy.py |

### 5.2 Integration Tests

| Scenario | Description | Expected Outcome |
|----------|-------------|------------------|
| STRICT task E2E | Full STRICT task with all accountability | Worklog + 3 verifications + 3 checkpoints |
| STANDARD task E2E | Full STANDARD task | Worklog + 1 checkpoint |
| Verification failure | Simulate TodoWrite mismatch | Retry, then escalate |
| Circuit breaker trip | 3 verification failures | User forced to resolve |
| Memory unavailable | Simulate Serena failure | Graceful degradation with notification |
| Flag overrides | Test all `--no-*` flags | Features disabled as expected |
| Time-based flush | 30s elapsed with partial buffer | Buffer flushed |
| Error recovery | Bash failure mid-task | Emergency flush, audit trail preserved |

### 5.3 Performance Tests

| Test | Metric | Target |
|------|--------|--------|
| Worklog overhead | Token count | ≤300 tokens (weighted avg) |
| Verification latency | Time | ≤1000ms per verification |
| Checkpoint latency | Time | ≤2000ms per checkpoint |
| Aggregate overhead | Time | ≤3000ms total per phase |
| Memory growth | Bytes/session | ≤50KB per session |

### 5.4 Error Scenarios

| Scenario | Trigger | Expected Behavior |
|----------|---------|-------------------|
| Memory write timeout | Simulate 5s delay | Skip write, log warning, continue |
| Verification infinite loop | User clicks retry repeatedly | Circuit breaker forces resolution |
| Buffer loss on crash | Kill process mid-buffer | Next session finds no pending data (acceptable) |
| Schema validation failure | Corrupted worklog in memory | Archive corrupted, start fresh |
| Concurrent task collision | Two tasks same second | Session IDs differ by counter (001, 002) |

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Memory bloat from worklogs | Medium | Medium | TTL-based cleanup, max 50 active worklogs |
| Verification false positives | Low | High | Single retry, user escalation, circuit breaker |
| Checkpoint overhead in tight token budgets | Medium | Low | Tier-scoped (LIGHT/EXEMPT exempt) |
| MCP latency spikes | Low | Medium | Aggregate timeout budget (3000ms) |
| Buffer loss on crash | Medium | Low | 30s time-based flush, explicit risk acceptance |
| Cascading timeouts | Low | High | Aggregate timeout budget, adaptive skipping |

### 6.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Users bypass with `--no-*` flags | Medium | Low | Track usage, adjust defaults |
| Accountability theater | Medium | Medium | Measure checkpoint correction rate |
| Increased complexity for contributors | Low | Medium | Documentation, examples, interfaces |
| Serena unavailable at critical moment | Low | Medium | Mandatory user notification, session-only fallback |

---

## 7. Appendices

### A. Token Budget Calculation

```yaml
STRICT task (10 todos, 30 operations):
  worklog:
    initialization: 50 tokens
    entries: 30 × 20 = 600 tokens (batched to 3 flushes)
    finalization: 75 tokens
    subtotal: 725 tokens
    with_batching: ~300 tokens (MCP overhead reduction)

  verification:
    verifications: 10 × 50 = 500 tokens
    retries (5% rate): 0.5 × 75 = 37.5 tokens
    subtotal: ~538 tokens

  checkpoints:
    checkpoints: 3 × 100 = 300 tokens
    subtotal: 300 tokens

  TOTAL without batching: ~1563 tokens
  TOTAL with batching: ~750 tokens (within NFR-001 bound)

WEIGHTED AVERAGE:
  10% STRICT × 750 = 75
  60% STANDARD × 300 = 180
  25% LIGHT × 60 = 15
  5% EXEMPT × 0 = 0
  TOTAL: 270 tokens/task average
```

### B. Flag Reference

| Flag | Effect | Feature Default | Recommendation |
|------|--------|-----------------|----------------|
| `--no-worklog` | Disable all worklog functionality | Worklog ON | Not recommended - breaks accountability |
| `--skip-verify` | Skip STRICT verification | Verification ON | Use for trusted environments |
| `--no-checkpoints` | Disable checkpoint summaries | Checkpoints ON | Use for time-critical tasks |
| `--verbose-log` | Include full tool results | Verbose OFF | Use for debugging |
| `--retry-memory` | Retry Serena connection | N/A | Use after fallback notification |

### C. Migration Guide

**Existing sc:task-unified users**:
1. No action required - accountability enabled by default
2. Worklog memories will appear with `_worklog/` prefix
3. To disable all accountability: `--no-worklog --skip-verify --no-checkpoints`

**SKILL.md maintainers**:
1. Add Section 6 (Accountability Framework) after Section 5
2. Update tier enforcement steps as specified
3. Add new flags to flag reference table
4. Import configuration from `config/accountability.yaml`

---

## 8. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3.0 | 2026-01-26 | Claude Opus 4.5 | Initial draft from adversarial debate |
| 1.3.1 | 2026-01-26 | Claude Opus 4.5 | Addressed P0/P1 issues from spec-panel review |

---

## 9. Expert Panel Review Summary

### Review Round 1 (v1.3.0 → v1.3.1)

| Expert | Score | Key Feedback | Status |
|--------|-------|--------------|--------|
| Wiegers (Requirements) | 7/10 | 4 P0 issues on ambiguity | ✅ Addressed |
| Adzic (Testability) | 5/10 | Missing concrete examples | ✅ Added Scenario Outlines |
| Nygard (Operations) | 5/10 | Failure modes underspecified | ✅ Added circuit breaker, timeouts |
| Fowler (Architecture) | 7/10 | Weak interfaces, hardcoded values | ✅ Added interfaces, config schema |

**Post-Revision Confidence**: 85-90%

### Review Round 2 (v1.3.1 → v1.3.2): Session Lifecycle Enhancements

**Context**: Adversarial debate between Architect and Performance personas concluded that full `/sc:load` integration would exceed token budgets and violate v1.3's accountability focus. The panel approved two low-cost, high-value enhancements instead.

#### FR-007: Smart Checkpoint Detection

| Expert | Initial | Final | Key Feedback |
|--------|---------|-------|--------------|
| Wiegers | 4/10 | 8/10 | P0: Ambiguous trigger definition → Added precise timing and constraints |
| Adzic | 3/10 | 8/10 | P0: No acceptance criteria → Added 5 Gherkin scenarios |
| Nygard | 4/10 | 8/10 | P0: Missing failure modes → Added timeout handling, tier scope |
| Fowler | 6/10 | 8/10 | P1: Interface missing → Added CheckpointDetectionService interface |

**Consensus**: ✅ APPROVED with revisions

**Key Improvements Applied**:
- Explicit timing: "After tier classification, before worklog init"
- 500ms timeout budget allocation
- Tier-scoped (STRICT/STANDARD only, skip LIGHT/EXEMPT)
- Exact session matching (no fuzzy matching)
- Graceful failure handling (timeout = silent skip)
- TypeScript interface definition

#### NFR-005: Session ID MCP Independence

| Expert | Score | Key Feedback |
|--------|-------|--------------|
| Wiegers | 9/10 | Clear and testable |
| Adzic | 8/10 | Added test for MCP-down scenario |
| Nygard | 8/10 | Added counter overflow handling |
| Fowler | 9/10 | Architecturally sound |

**Consensus**: ✅ APPROVED as-is with minor additions

**Key Improvements Applied**:
- Explicit `mcp_dependency: none` confirmation
- Counter overflow handling specification
- Three acceptance scenarios (MCP-down, concurrent, stress)

### Overall Post-v1.3.2 Confidence: 90%

**Deferred to v1.4**: Full `/sc:load` integration (per adversarial debate outcome)
