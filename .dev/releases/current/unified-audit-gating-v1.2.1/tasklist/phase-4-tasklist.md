# Phase 4 -- Context Injection & Runner Reporting

Implement deterministic context injection and runner-constructed reporting to ensure task N+1 has full visibility into prior work, including gate outcomes and remediation history. This enables informed task execution without relying on agent self-reporting.

### T04.01 -- Implement Context Injection Builder in sprint/process.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | Without deterministic context injection, per-task subprocesses lose visibility into prior work, causing repeated or contradictory changes across tasks in the same sprint. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data (context state), system-wide (cross-task coordination) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0014/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0014/evidence.md

**Deliverables:**
- Context injection builder (~180 lines) in `src/superclaude/cli/sprint/process.py` that constructs a deterministic summary from result files, gate outcomes, and remediation history for inclusion in each task prompt

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/process.py` to identify existing prompt construction patterns
2. **[PLANNING]** Define context injection schema: prior task results, gate outcomes, remediation history, file change summary
3. **[EXECUTION]** Implement `build_task_context()` function that aggregates prior TaskResult summaries into structured markdown
4. **[EXECUTION]** Include gate outcomes (pass/fail/deferred) and remediation history (attempts, outcomes) in context
5. **[EXECUTION]** Integrate context builder into per-task subprocess prompt construction (called before each task launch)
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k context_injection -v` verifying all context fields present
7. **[COMPLETION]** Record deliverable evidence in D-0014/evidence.md

**Acceptance Criteria:**
- `build_task_context()` in `sprint/process.py` produces structured markdown containing prior task results, gate outcomes, and remediation history
- Each task prompt includes context from all preceding tasks in the same phase
- Gate outcomes are visible in context (pass/fail/deferred status per prior task)
- `uv run pytest tests/sprint/test_process.py -k context_injection` exits 0

**Validation:**
- `uv run pytest tests/sprint/test_process.py -k context_injection -v`
- Evidence: linkable artifact produced at D-0014/evidence.md

**Dependencies:** T02.02 (per-task subprocess), T02.04 (TaskResult/PhaseResult)
**Rollback:** Remove context builder; tasks launch without prior-work context

---

### T04.02 -- Implement TaskResult Dataclass in sprint/models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | A runner-constructed TaskResult dataclass eliminates dependency on agent self-reporting for task outcome tracking, ensuring accurate results even from budget-exhausted subprocesses. |
| Effort | M |
| Risk | Low |
| Risk Drivers | model (models.py) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0015/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0015/evidence.md

**Deliverables:**
- TaskResult dataclass in `src/superclaude/cli/sprint/models.py` combining execution data (status, turns consumed, output), gate outcome (pass/fail/pending), and reimbursement amount

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/models.py` to identify existing dataclass patterns
2. **[PLANNING]** Define TaskResult fields: task_id, status, turns_consumed, output_path, gate_outcome, reimbursement_amount
3. **[EXECUTION]** Implement TaskResult dataclass with all fields, constructed by the runner from subprocess output
4. **[EXECUTION]** Add serialization method for context injection and phase report consumption
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py -k TaskResult -v`
6. **[COMPLETION]** Record deliverable evidence in D-0015/evidence.md

**Acceptance Criteria:**
- TaskResult dataclass in `sprint/models.py` contains fields: task_id, status, turns_consumed, output_path, gate_outcome, reimbursement_amount
- All fields populated from subprocess output by the runner (not agent self-reported)
- Serialization method produces deterministic output suitable for context injection
- `uv run pytest tests/sprint/test_models.py -k TaskResult` exits 0

**Validation:**
- `uv run pytest tests/sprint/test_models.py -k TaskResult -v`
- Evidence: linkable artifact produced at D-0015/evidence.md

**Dependencies:** T02.04 (result aggregation uses TaskResult)
**Rollback:** Remove TaskResult dataclass from models.py

---

### T04.03 -- Implement Phase-Level YAML Report Aggregation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Phase YAML reports provide structured, machine-readable sprint output with standardized fields for downstream tooling and TUI display. |
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
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0016/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0016/evidence.md

**Deliverables:**
- Phase-level YAML report aggregation: runner constructs phase YAML from TaskResults with fields tasks_total, tasks_passed, tasks_failed, tasks_incomplete, tasks_not_attempted, budget_remaining

**Steps:**
1. **[PLANNING]** Define YAML report schema with required fields from roadmap specification
2. **[PLANNING]** Identify where phase report is emitted in the sprint runner lifecycle
3. **[EXECUTION]** Implement YAML report construction from list of TaskResult objects
4. **[EXECUTION]** Include all required fields: tasks_total, tasks_passed, tasks_failed, tasks_incomplete, tasks_not_attempted, budget_remaining
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k phase_yaml -v`
6. **[COMPLETION]** Record deliverable evidence in D-0016/evidence.md

**Acceptance Criteria:**
- Phase YAML report contains: tasks_total, tasks_passed, tasks_failed, tasks_incomplete, tasks_not_attempted, budget_remaining
- Field values match actual TaskResult aggregation (verified against known test inputs)
- YAML output is valid and parseable by standard YAML libraries
- `uv run pytest tests/sprint/ -k phase_yaml` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k phase_yaml -v`
- Evidence: linkable artifact produced at D-0016/evidence.md

**Dependencies:** T04.02 (TaskResult dataclass)
**Rollback:** Revert to existing phase report format

---

### T04.04 -- Implement Git Diff Context Integration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Appending `git diff --stat` since sprint start gives each task a structural overview of prior changes, reducing redundant file reads and conflicting modifications. |
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
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0017/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0017/evidence.md

**Deliverables:**
- Git diff context integration that appends `git diff --stat` output (since sprint start commit) to each task's context injection

**Steps:**
1. **[PLANNING]** Identify sprint start commit reference (stored at sprint initialization)
2. **[PLANNING]** Determine integration point in context builder from T04.01
3. **[EXECUTION]** Implement `get_git_diff_context()` that runs `git diff --stat <start_commit>` and captures output
4. **[EXECUTION]** Append git diff summary to task context as a structured section
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k git_diff_context -v`
6. **[COMPLETION]** Record deliverable evidence in D-0017/evidence.md

**Acceptance Criteria:**
- Git diff summary appended to each task's context injection after the prior-work summary
- Diff is computed relative to sprint start commit (not working tree)
- Graceful handling when git is not available or no changes exist (empty diff section)
- `uv run pytest tests/sprint/ -k git_diff_context` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k git_diff_context -v`
- Evidence: linkable artifact produced at D-0017/evidence.md

**Dependencies:** T04.01 (context injection builder)
**Rollback:** Remove git diff section from context injection

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.04

**Purpose:** Verify context injection components before adding progressive summarization.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P04-T01-T04.md

**Verification:**
- Context injection builder produces structured markdown with all required fields
- TaskResult dataclass fields populated correctly from subprocess output
- Git diff context appended without errors in both clean and dirty working trees

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k "context_injection or TaskResult or phase_yaml or git_diff" -v` exits 0
- Context output includes prior task results, gate outcomes, and git diff summary
- No regressions in existing sprint tests

---

### T04.05 -- Implement Progressive Summarization for Token Budget

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Without progressive summarization, context injection grows linearly with task count and eventually overflows the token budget for long sprints, causing task prompt truncation. |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance (token budget) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0018/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0018/evidence.md

**Deliverables:**
- Progressive summarization logic that compresses the running context summary every N tasks to stay within token budget, preserving key outcomes while reducing detail for older tasks

**Steps:**
1. **[PLANNING]** Define summarization threshold: trigger compression every N tasks (N derived from budget allocation)
2. **[PLANNING]** Define summarization strategy: keep last 3 tasks at full detail, compress older tasks to status + key outcome
3. **[EXECUTION]** Implement `compress_context_summary()` that reduces older task context while preserving gate outcomes and remediation status
4. **[EXECUTION]** Integrate into context builder: trigger compression when task count exceeds threshold
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k progressive_summary -v` with 10+ task sequences
6. **[COMPLETION]** Record deliverable evidence in D-0018/evidence.md

**Acceptance Criteria:**
- Context summary size is bounded: does not grow linearly with task count beyond compression threshold
- Compressed summaries preserve: task status, gate outcome, file changes (at minimum)
- Full detail retained for most recent 3 tasks; older tasks compressed to status line
- `uv run pytest tests/sprint/ -k progressive_summary` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k progressive_summary -v`
- Evidence: linkable artifact produced at D-0018/evidence.md

**Dependencies:** T04.01 (context injection builder)
**Rollback:** Disable progressive summarization; context grows unbounded

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm context injection and runner reporting are complete before proceeding to trailing gate infrastructure.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P04-END.md

**Verification:**
- Context injection includes prior results, gate outcomes, remediation history, and git diff
- Progressive summarization bounds context size for long sprints
- Phase YAML reports contain all required fields

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k "context or TaskResult or phase_yaml or git_diff or summary" -v` exits 0
- All 5 deliverables (D-0014 through D-0018) have evidence artifacts
- Context injection verified with ≥10 task sequences without token overflow
