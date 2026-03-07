# Position B: Per-Task Subprocess with Turn-Budget Reimbursement

**Proposal**: Replace the per-phase subprocess model with per-task subprocess spawning. One subprocess per task. The runner manages task ordering, context passing, and budget allocation at task granularity. Trailing gates audit each task independently. On PASS, that task's turns are reimbursed at 90%.

---

## 1. Problem Context

The sprint runner's MaxTurn problem: Claude Code subprocesses silently exhaust their `--max-turns` budget, exit with code 0, and the runner classifies incomplete phases as successful (`PASS_NO_REPORT`). The Completion Protocol report — the agent's self-assessment — is always the first casualty because it's the last step.

**This position argues**: The root cause is that the runner delegates too much to a single subprocess. By giving one subprocess a 13-task phase, the runner loses visibility into per-task progress and can't distinguish "all done" from "ran out of turns mid-task-7." Per-task subprocess spawning structurally eliminates this visibility gap, and the TurnLedger provides the economic mechanism to make it sustainable.

---

## 2. Architecture

### 2.1 Subprocess Model (New)

One Claude Code subprocess per task. The runner owns task sequencing, context injection, and result aggregation.

```
Sprint Runner
  ├── Phase 1
  │   ├── T01.01 subprocess (--max-turns N)
  │   ├── T01.02 subprocess (--max-turns N)
  │   ├── ...
  │   └── T01.08 subprocess (--max-turns N)
  ├── Phase 2
  │   ├── T02.01 subprocess (--max-turns N)
  │   └── ...
  └── Phase 5
      ├── T05.01 subprocess (--max-turns N)
      ├── ...
      └── T05.09 subprocess (--max-turns N)
```

### 2.2 TurnLedger Integration

```
TurnLedger (per-sprint, runner-side only):
  initial_budget:     200
  consumed:           0
  reimbursed:         0
  reimbursement_rate: 0.90

  available() -> initial_budget - consumed + reimbursed
  debit(n)    -> consumed += n
  credit(n)   -> reimbursed += floor(n * reimbursement_rate)
```

### 2.3 Transaction Flow Per Task

```
1. BEFORE LAUNCH:  Check ledger.available() >= minimum_allocation (e.g., 5)
                   If not: HALT sprint (budget exhausted)
2. ALLOCATE:       max_turns = min(ledger.available(), default_task_budget)
3. BUILD PROMPT:   Include task description + context summary from prior tasks
4. LAUNCH:         claude --max-turns {max_turns} -p <task_prompt>
5. ON EXIT:        actual_turns = count_turns(output)
                   ledger.debit(actual_turns)
6. TRAILING GATE:  audit(task_output) -> PASS or FAIL
7. REIMBURSE:      if PASS: ledger.credit(actual_turns)
                   if FAIL: no credit → may trigger remediation retry
8. AGGREGATE:      Runner updates phase-level result from task results
```

### 2.4 Reimbursement Cycle (Worked Example)

Using task-level data extrapolated from the cleanup-audit-v2 sprint:

| Task | Allocated | Used | Overhead | Gate | Reimbursed (90%) | Budget |
|------|-----------|------|----------|------|-------------------|--------|
| T01.01 | 15 | 8 | ~2 | PASS | 7 | 199 |
| T01.02 | 15 | 6 | ~2 | PASS | 5 | 198 |
| T01.03 | 15 | 7 | ~2 | PASS | 6 | 197 |
| T01.04 | 15 | 5 | ~2 | PASS | 4 | 196 |
| ... | ... | ... | ... | ... | ... | ... |
| T05.06 | 15 | 10 | ~2 | PASS | 9 | ~185 |
| T05.07 | 15 | 8 | ~2 | PASS | 7 | ~184 |
| T05.08 | 15 | 6 | ~2 | PASS | 5 | ~183 |
| T05.09 | 15 | 12 | ~2 | PASS | 10 | ~181 |

Key observation: Every task — including T05.06 through T05.09 (the tasks that were never executed in the original sprint) — gets its own budget allocation. No task is starved because another task in the same phase consumed too many turns.

---

## 3. How This Solves the MaxTurn Problem

### 3.1 Structural Elimination of Silent Incompletion

The original failure mode:
1. Subprocess gets 13 tasks in one phase
2. Exhausts max-turns at task 10
3. Tasks 11-13 never execute
4. Runner can't tell → classifies as PASS_NO_REPORT

Under per-task subprocess:
1. Runner launches one subprocess per task
2. Runner knows exactly which task is running (it launched it)
3. If a task hits max-turns, the runner knows which task failed
4. Remaining tasks are visible in the runner's task queue — they haven't been launched yet
5. The runner constructs the phase report by aggregating individual task results

**The runner never depends on agent self-reporting.** The Completion Protocol becomes optional, not critical.

### 3.2 The Runner Becomes Source of Truth

The runner owns the task inventory (parsed from the tasklist file). It tracks:
- Which tasks have been launched
- Which tasks completed (subprocess exited)
- Which tasks passed their trailing gate
- Which tasks remain in the queue
- How many turns each task consumed

This information was previously invisible to the runner — it was locked inside the subprocess's session context.

### 3.3 Precise Retry on Failure

If T05.06 fails its trailing gate:
- Only T05.06 is retried (one subprocess spawn)
- T05.01-T05.05 are unaffected (already passed and reimbursed)
- The retry's turns are reimbursable if the second attempt passes
- No wasted re-execution of already-passing tasks

Under per-phase, retrying Phase 5 means re-running all 9 tasks, including the 5 that already passed.

### 3.4 The 90% Decay as Safety Valve

Same as per-phase: 90% reimbursement ensures natural budget decay. With ~2 turns of overhead per task (cold-start) that are NOT reimbursable, the effective drain per passing task is:

```
net_cost_per_task = (actual_turns × 0.10) + overhead_turns
                  = (8 × 0.10) + 2
                  = 2.8 turns per passing task
```

For a 46-task sprint: ~129 turns of net drain. A 200-turn budget sustains this comfortably with ~71 turns of margin.

---

## 4. Arguments For This Approach

### 4.1 The Completion Protocol Problem is Structurally Eliminated

This is the strongest argument. Under per-phase, the Completion Protocol (the agent writing a summary report) is the last step and the first casualty of budget exhaustion. Under per-task:

- Each subprocess does ONE task + a trivial report ("T05.06: PASS, files changed: [x.py, y.py]")
- Even this trivial report is optional — the runner knows the task was running and can infer outcome
- The runner aggregates task results into phase reports itself
- No dependence on agent self-reporting whatsoever

This is not a mitigation. It is a structural elimination of the failure mode.

### 4.2 Maximum Granularity for Turn Accounting

Per-task reimbursement means:
- Task T03.04 costs 8 turns → passed → 7 reimbursed
- Task T03.05 costs 12 turns → failed → 0 reimbursed
- Task T03.06 costs 6 turns → passed → 5 reimbursed

The ledger shows exactly which tasks are expensive, which fail, and where budget is consumed. This data is invaluable for:
- Optimizing tasklist design (split expensive tasks, combine trivial ones)
- Identifying patterns (security tasks cost 2x more than implementation tasks)
- Calibrating default_task_budget for future sprints

### 4.3 Isolated Failure Blast Radius

A failed task costs only its own turns. If task 10/13 in a phase fails:
- Per-phase: all 13 tasks' turns potentially lost (if phase gate fails)
- Per-task: only task 10's turns lost; tasks 1-9 and 11-13 are independently evaluated

This means the budget is spent more efficiently — good work is always recognized.

### 4.4 Natural Trailing Gate Alignment

The trailing gate design (v2.0) is fundamentally a per-step mechanism. One gate per step, one evaluation per step. Per-task subprocess creates a perfect 1:1 mapping:

```
subprocess(T05.06) → output → trailing_gate(T05.06) → PASS → reimburse
```

Per-phase forces an awkward many-to-one relationship where one gate evaluates the output of many tasks.

### 4.5 Best Portability Story

Per-task subprocess spawning maps naturally to:
- CI/CD job queues (one job per task)
- Distributed task runners (tasks as independent work items)
- Non-Claude-Code agent runtimes (each task = one API call or session)
- Container-based execution (one container per task)

This is the model the industry uses for scalable task execution. Porting away from Claude Code becomes a matter of swapping the subprocess implementation, not redesigning the orchestration.

### 4.6 Runner-Owned Intelligence

With per-task control, the runner can:
- Dynamically adjust task budgets based on observed costs ("security tasks average 12 turns, allocate 15")
- Reorder tasks based on priority or dependency
- Skip tasks that become irrelevant due to earlier failures
- Parallelize independent tasks (spawn multiple subprocesses simultaneously)
- Provide richer diagnostic data when the sprint halts

---

## 5. Acknowledged Weaknesses

### 5.1 Context Fragmentation

Task 5's subprocess doesn't know what task 4 did. If task 5 says "write tests for the function implemented in task 4," the agent must rediscover that function from scratch.

**Mitigations**:
- **Context injection**: Include a structured summary of prior task results in each task's prompt. The runner auto-generates this from the result files.
  ```
  ## Prior Work Context
  - T05.01: Added AuditState enum to models.py (lines 45-67)
  - T05.02: Implemented validate_transition() in gates.py (lines 89-134)
  - T05.03: ...
  ```
- **Git diff context**: Include `git diff --stat` since sprint start, showing what files changed and how.
- **Progressive summarization**: Maintain a running summary that grows across tasks but is compressed to stay within budget.

The context injection approach means the agent starts each task with a structured understanding of what happened before — arguably more reliable than remembering details from 40 turns ago in a long session.

### 5.2 Subprocess Cold-Start Overhead

Each Claude Code subprocess consumes tokens on startup:
- Without isolation: ~50K tokens on turn 1 (per dev.to analysis)
- With 4-layer isolation: ~5K tokens on turn 1

For 46 tasks:
- Without isolation: ~2.3M tokens of overhead
- With isolation: ~230K tokens of overhead

In turn terms (assuming ~5K tokens/turn):
- Without isolation: ~460 turns of overhead (more than the entire budget)
- With isolation: ~46 turns of overhead (manageable)

**Critical requirement**: 4-layer isolation (scoped working directory, git boundary, empty plugin dir, restricted settings) is MANDATORY for per-task viability. Without it, the overhead is prohibitive.

**Mitigations**:
- 4-layer isolation reduces overhead by 10x (50K → 5K per subprocess)
- Overhead turns (~2 per task with isolation) are a known, fixed cost
- The budget model accounts for this: it's part of the net drain calculation
- Future optimization: subprocess pooling, warm-start caching, persistent sessions

### 5.3 Loss of Inter-Task Optimization

An agent processing 8 tasks in one session reads a file once and applies knowledge across all tasks. Per-task forces redundant file reads.

**Mitigations**:
- Context injection reduces (but doesn't eliminate) redundant discovery
- In practice, many tasks touch different files — the overlap may be less than assumed
- The turns spent on re-reading are included in the task's cost and are reimbursable

### 5.4 More Total Turns Consumed

Cold-start + context re-acquisition + redundant reads = more total turns across the sprint.

**Analysis**: For a 46-task sprint with isolation:
- Overhead: ~92 turns (46 tasks × 2 turns/cold-start)
- Context re-acquisition: ~46 turns (1 turn/task estimated)
- Total overhead: ~138 turns
- vs. per-phase overhead: ~12 turns (6 phases × 2 turns)
- **Delta: ~126 extra turns**

With 90% reimbursement on passing tasks, the reimbursable work turns are recovered. The non-reimbursable overhead (~138 turns) must be covered by the initial budget. A 200-turn budget has margin for this, but it's tighter than per-phase.

### 5.5 Complex Orchestration

The runner must manage:
- Task dependency parsing from tasklist files
- Context injection prompt construction
- Per-task result file management
- Phase-level result aggregation
- Retry logic at task granularity (not just phase)
- Parallel task spawning for independent tasks

This is significantly more complex than the current "launch phase, wait" model.

**Mitigation**: This complexity lives in the runner, not the agent. The runner is deterministic Python code that can be thoroughly tested. The complexity is front-loaded in implementation, not ongoing in execution.

### 5.6 API Rate Limiting Risk

Rapid subprocess spawning (46 subprocesses for a sprint) may trigger rate limits on the Claude API.

**Mitigations**:
- Configurable concurrency limit (default: 1 sequential, optional parallel)
- Backoff between spawns if needed
- In practice, each task takes minutes — rate limiting is unlikely for sequential execution

---

## 6. The Completion Protocol Under This Model

The Completion Protocol is structurally irrelevant under per-task:

1. **The runner owns the task inventory**: It parsed the tasklist file. It knows tasks T05.01-T05.09 exist.
2. **The runner tracks execution**: It launched T05.01, waited for exit, launched T05.02, etc.
3. **The runner constructs the report**: Phase results are aggregated from individual task results. No agent self-assessment needed.
4. **If a task hits max-turns**: The runner knows which task was running (it launched it). It marks that task as INCOMPLETE. Remaining tasks in the queue are marked NOT_ATTEMPTED. The runner has full visibility.
5. **The phase report becomes**:
   ```yaml
   phase: 5
   status: PARTIAL
   tasks_total: 9
   tasks_passed: 5
   tasks_failed: 0
   tasks_incomplete: 1 (T05.06 - max_turns exhausted)
   tasks_not_attempted: 3 (T05.07, T05.08, T05.09)
   EXIT_RECOMMENDATION: HALT
   ```

The runner writes this report. The agent never needs to. The Completion Protocol becomes a nice-to-have, not a critical dependency.

---

## 7. Implementation Complexity

| Component | Effort | Risk |
|-----------|--------|------|
| TurnLedger dataclass | Trivial (~50 lines) | None |
| Task-level subprocess spawning | Moderate (~200 lines) | Medium (new orchestration) |
| Tasklist parser (extract individual tasks) | Moderate (~100 lines) | Low |
| Context injection prompt builder | Moderate (~150 lines) | Medium (prompt engineering) |
| Per-task result file management | Low (~80 lines) | Low |
| Phase result aggregation | Low (~60 lines) | Low |
| Task dependency ordering | Moderate (~120 lines) | Medium |
| 4-layer subprocess isolation | Low (~40 lines) | Low (well-documented) |
| Turn counting (post-hoc file-based) | Trivial (~15 lines) | Low |
| Retry logic at task granularity | Low (~50 lines) | Low |
| **Total** | **~3-4 weeks** | **Medium** |

This is a meaningful architectural change. The runner's executor loop is restructured from "iterate over phases" to "iterate over phases, then iterate over tasks within each phase." The subprocess management, prompt construction, and result handling all change.

---

## 8. The Context Fragmentation Trade-Off

This is the central tension. Per-task subprocess trades context continuity for visibility and control. Is this trade-off worth it?

**The case that it IS worth it**:
- Context injection (structured prior-work summaries) provides 80-90% of the continuity benefit
- The runner's structured summary may actually be MORE reliable than an agent's degrading memory in a long session (agents forget details after many turns)
- The visibility gain (the runner always knows exactly what happened) is transformative for diagnostics, recovery, and trust
- The cost is front-loaded (implementation complexity) not ongoing (execution overhead with isolation is manageable)

**The case that it is NOT worth it**:
- Inter-task dependencies within a phase are common and deep
- "Write tests for function X" requires understanding function X in detail — a summary may not be enough
- The overhead turns (138 extra for a 46-task sprint) are real budget pressure
- The orchestration complexity introduces new failure modes in the runner itself

This trade-off is the core question for adversarial debate.
