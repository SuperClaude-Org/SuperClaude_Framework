<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant B (Per-Task Subprocess) -->
<!-- Merge date: 2026-03-06 -->

# Turn-Budget Reimbursement via Unified Audit Gating: Per-Task Subprocess Architecture

**Status**: ADVERSARIAL MERGE OUTPUT — Consensus recommendation
**Date**: 2026-03-06
**Base**: Position B (Per-Task Subprocess), score 0.939
**Runner-up**: Position A (Per-Phase Subprocess), score 0.894
**Convergence**: 80% (8/10 diff points resolved)
**Debate depth**: Standard (2 rounds)

---

<!-- Source: Base (original) -->
## 1. Problem Recap

The sprint runner spawns Claude Code subprocesses with a fixed `--max-turns` budget. When a subprocess exhausts its budget, Claude Code exits with code 0 (indistinguishable from normal completion), and any unfinished tasks — including the Completion Protocol report — are silently dropped. The sprint reports success when work is incomplete.

**Root cause**: The runner delegates too much to a single subprocess. By giving one subprocess a 13-task phase, the runner loses visibility into per-task progress and can't distinguish "all done" from "ran out of turns mid-task-7."

**Solution**: Per-task subprocess spawning with a revolving turn budget (TurnLedger) where verified work earns back capacity through the Unified Audit Gating process. The runner — not the agent — owns task completion state.

---

<!-- Source: Base (original) -->
## 2. Core Economic Model

### 2.1 The Turn Ledger

A per-sprint budget managed by the runner (never visible to the agent doing the work):

```
TurnLedger:
  initial_budget:     200       # configurable per sprint
  consumed:           0         # total turns debited
  reimbursed:         0         # total turns credited back
  reimbursement_rate: 0.90      # 90% reimbursement on PASS (natural decay)

  available() -> initial_budget - consumed + reimbursed
  debit(n)    -> consumed += n
  credit(n)   -> reimbursed += floor(n * reimbursement_rate)
```

### 2.2 Subprocess Model

One Claude Code subprocess per task. The runner owns task sequencing, context injection, and result aggregation.

```
Sprint Runner
  ├── Phase 1
  │   ├── T01.01 subprocess (--max-turns N)
  │   ├── T01.02 subprocess (--max-turns N)
  │   └── ... (one per task)
  ├── Phase 2
  │   └── ... (one per task)
  └── Phase K
      └── ... (one per task)
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

<!-- Source: Variant A, Section U-001 — merged per Change #4 -->
**Optional: Turn Reservation** — For additional safety, allocate `max_turns = min(ledger.available(), default_task_budget) - 2`, reserving 2 turns for output formatting. This is a minor enhancement; the runner does not depend on agent output for completion state, but well-formatted output improves diagnostics.

### 2.4 Retry Reimbursement Rule

- First attempt fails audit → turns NOT reimbursed
- Remediation (second attempt) passes audit → only remediation turns reimbursed
- Both attempts fail → both sets of turns permanently lost → budget drains → sprint halts

### 2.5 The 90% Reimbursement Rate

A 90% reimbursement rate creates natural budget decay even when everything passes:

```
net_cost_per_task = (actual_turns × 0.10) + overhead_turns
                  = (8 × 0.10) + 2
                  = 2.8 turns per passing task
```

For a 46-task sprint: ~129 turns of net drain. A 200-turn budget sustains this with ~71 turns of margin. This makes infinite-run mathematically impossible while providing generous capacity for legitimate work.

---

<!-- Source: Base (original) -->
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

Phase reports are runner-constructed:
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

### 3.3 Precise Retry on Failure

If T05.06 fails its trailing gate:
- Only T05.06 is retried (one subprocess spawn)
- T05.01-T05.05 are unaffected (already passed and reimbursed)
- The retry's turns are reimbursable if the second attempt passes
- No wasted re-execution of already-passing tasks

<!-- Source: Variant A, Section 3.2 — merged per Change #1 -->
### 3.4 Defense-in-Depth: error_max_turns Detection

Orthogonal to per-task subprocess, the runner should also detect the `error_max_turns` event in the NDJSON output stream. This event is already present as the final `"subtype":"error_max_turns"` JSON line when Claude Code hits its turn ceiling.

**Implementation**: Regex on the last NDJSON line of the subprocess output. Zero extra turn cost.

**Value**: Provides explicit confirmation of WHY a subprocess exited, strengthening diagnostic capability beyond binary "exited/didn't exit." Under per-task, this distinguishes:
- Task completed normally (no error_max_turns, output present)
- Task exhausted budget (error_max_turns detected, partial/no output)
- Task crashed (non-zero exit code)

This detection should be implemented regardless of subprocess granularity.

### 3.5 The 90% Decay as Safety Valve

Even with perfect work (all tasks PASS), the budget decays:
- 200 → 199 → 198 → ... (net ~2.8 turns/task)
- After ~71 passing tasks, budget reaches 0
- Failed tasks drain budget faster (full debit, no credit)
- A sprint producing consistently bad work halts rapidly

---

<!-- Source: Base (original) -->
## 4. Arguments For This Approach

### 4.1 The Completion Protocol Problem is Structurally Eliminated

Each subprocess does ONE task. Even if max-turns is hit, the runner knows exactly which task was running. The runner constructs phase reports itself. No dependence on agent self-reporting. This is not a mitigation — it is a structural elimination of the failure mode that already materialized in production (Phase 5 of cleanup-audit-v2: 4 tasks never executed, sprint reported success).

### 4.2 Maximum Granularity for Turn Accounting

Per-task reimbursement provides exact cost attribution:
- Task T03.04 costs 8 turns → passed → 7 reimbursed
- Task T03.05 costs 12 turns → failed → 0 reimbursed

This data enables: tasklist optimization (split expensive tasks), pattern identification (security tasks cost 2x implementation), and budget calibration for future sprints.

### 4.3 Isolated Failure Blast Radius

A failed task costs only its own turns. Tasks 1-9 passing are individually reimbursable even if task 10 fails. No collateral damage.

### 4.4 Natural Trailing Gate Alignment

One gate per task, one reimbursement decision per task. The gate/task/reimbursement mapping is 1:1 — clean and auditable.

### 4.5 Best Portability Story

Per-task spawning maps naturally to CI/CD job queues, Kubernetes Jobs, AWS Step Functions, Temporal.io. The industry has converged on per-task isolation for the same reasons: observability, retry, and budget control. Porting away from Claude Code becomes a matter of swapping the subprocess implementation, not redesigning the orchestration.

### 4.6 Runner-Owned Intelligence

The runner can dynamically adjust task budgets based on observed costs, reorder tasks, skip irrelevant tasks, and parallelize independent tasks.

---

<!-- Source: Base (original, modified) — strengthened context injection per Change #3 -->
## 5. Acknowledged Weaknesses

### 5.1 Context Fragmentation

Task 5's subprocess doesn't know what task 4 did. This is a real cost, not a dismissible one.

**Mitigations** (ordered by effectiveness):

1. **Structured context injection**: Include a deterministic summary of prior task results in each task's prompt. The runner auto-generates this from result files:
   ```
   ## Prior Work Context
   - T05.01: Added AuditState enum to models.py (lines 45-67)
     Files changed: src/superclaude/cli/pipeline/models.py
   - T05.02: Implemented validate_transition() in gates.py (lines 89-134)
     Files changed: src/superclaude/cli/pipeline/gates.py
   - T05.03: Added legal transition tests
     Files changed: tests/pipeline/test_gates.py
   ```

2. **Git diff context**: Include `git diff --stat` since sprint start, providing a structural overview of changes. This is deterministic and verifiable — unlike an agent's degrading memory in a long session.

3. **Dependency-aware prompt enrichment**: For tasks with explicit dependencies (e.g., "write tests for function X"), include the output of the dependency task (the file containing function X) directly in the prompt. The tasklist format already supports dependency annotations.

4. **Progressive summarization**: Maintain a running summary that grows across tasks but is compressed every N tasks to stay within budget.

**Context injection vs. session memory trade-off**: The structured summary approach provides deterministic, verifiable context. A long-running session's memory degrades — the agent may silently forget details from 30+ turns ago. Per-task subprocess trades implicit, opaque context for explicit, inspectable context.

**Observed data**: The cleanup-audit-v2 sprint showed tasks averaging 6-8 turns each. At this granularity, intra-task context needs are modest — most tasks read files, make changes, and write output without deep cross-task reasoning.

### 5.2 Subprocess Cold-Start Overhead

**Mandatory requirement**: 4-layer subprocess isolation is required for per-task viability:
1. Scoped working directory (already in `ClaudeProcess`)
2. Git boundary (`.git/HEAD` in workspace)
3. Empty plugin directory (`--plugin-dir` pointing to empty folder)
4. Restricted settings (`--setting-sources project,local`)

With isolation: ~5K tokens per cold-start (~2 turns). For 46 tasks: ~92 turns overhead.
Without isolation: ~50K tokens per cold-start (~10 turns). For 46 tasks: ~460 turns. **Prohibitive.**

The ~92 turns of overhead is a known, fixed infrastructure cost. It is NOT reimbursable but is accounted for in the budget model (Section 2.5 shows 71 turns of margin after all costs).

### 5.3 Loss of Inter-Task Optimization

Per-task forces redundant file reads. Mitigated by context injection (5.1) and the observation that many tasks touch different files — overlap may be less than assumed.

### 5.4 More Total Turns Consumed

Cold-start (92 turns) + context re-acquisition (~46 turns) = ~138 turns of overhead vs. ~12 turns for per-phase. **Delta: ~126 extra turns.** The budget model accommodates this, but it's real pressure.

### 5.5 Complex Orchestration

The runner must manage: task dependency parsing, context injection, per-task result files, phase aggregation, retry logic, parallel spawning. The ~865 lines of new code break into 10 independently testable components:

| Component | Lines | Complexity |
|-----------|-------|------------|
| TurnLedger | ~50 | Trivial (arithmetic) |
| Tasklist parser | ~100 | Standard (regex/markdown) |
| Context injection builder | ~150 | Moderate (prompt engineering) |
| Subprocess orchestration | ~200 | Standard (loop + spawn + wait) |
| Result file management | ~80 | Standard (file I/O) |
| Phase aggregation | ~60 | Simple (reduction) |
| Task dependency ordering | ~120 | Standard (topological sort) |
| 4-layer isolation setup | ~40 | Simple (directory ops) |
| Turn counting | ~15 | Trivial (file read + count) |
| Retry logic | ~50 | Simple (conditional re-spawn) |

### 5.6 API Rate Limiting Risk

46+ subprocess spawns per sprint may trigger rate limits. Mitigated by: configurable concurrency (default: sequential), backoff between spawns, and the observation that each task takes minutes — sequential execution is unlikely to trigger limits.

---

<!-- Source: Base (original) -->
## 6. Reimbursement Cycle (Worked Example)

Using task-level data extrapolated from the cleanup-audit-v2 sprint:

| Task | Allocated | Used | Overhead | Gate | Reimbursed (90%) | Budget |
|------|-----------|------|----------|------|-------------------|--------|
| T01.01 | 15 | 8 | ~2 | PASS | 7 | 199 |
| T01.02 | 15 | 6 | ~2 | PASS | 5 | 198 |
| T01.03 | 15 | 7 | ~2 | PASS | 6 | 197 |
| ... | ... | ... | ... | ... | ... | ... |
| T05.06 | 15 | 10 | ~2 | PASS | 9 | ~185 |
| T05.07 | 15 | 8 | ~2 | PASS | 7 | ~184 |
| T05.08 | 15 | 6 | ~2 | PASS | 5 | ~183 |
| T05.09 | 15 | 12 | ~2 | PASS | 10 | ~181 |

Every task — including T05.06 through T05.09 (the 4 tasks that were never executed in the original sprint) — gets its own budget allocation. No task is starved because another task consumed too many turns.

---

<!-- Source: Variant A Round 2 new evidence + Base Section 7 — merged per Changes #2, #5 -->
## 7. Implementation Strategy

### 7.1 Staged Delivery Plan

The full per-task architecture is a 3-4 week effort. To deliver value incrementally:

**Phase 1: TurnLedger + Detection (Week 1)**
- Implement TurnLedger dataclass (~50 lines)
- Add error_max_turns detection to OutputMonitor (~15 lines)
- Reclassify PASS_NO_REPORT + error_max_turns as INCOMPLETE
- Wire budget check before subprocess launch (~10 lines)
- **Value**: Immediately detects silent incompletion; budget tracking begins

**Phase 1.5: Intra-Phase Checkpointing (Week 2, optional)**
- After each task within a phase subprocess, write a completion marker
- On phase retry, skip tasks with valid completion markers
- **Value**: ~80% of per-task blast-radius benefit at ~20% of cost
- **Trade-off**: Still per-phase subprocess; still depends on agent cooperation for markers

**Phase 2: Per-Task Subprocess Migration (Weeks 3-5)**
- Implement tasklist parser (~100 lines)
- Implement context injection builder (~150 lines)
- Implement per-task subprocess orchestration (~200 lines)
- Implement 4-layer isolation setup (~40 lines)
- Implement result aggregation + phase report construction (~140 lines)
- Implement retry logic (~50 lines)
- Wire turn counting into reimbursement (~15 lines)
- **Value**: Full structural elimination of Completion Protocol dependence

**Phase 3: Optimization (Week 6+, as needed)**
- Dynamic task budget calibration from observed costs
- Parallel task spawning for independent tasks
- Progressive summarization for context injection
- Subprocess warm-start caching

### 7.2 Implementation Complexity

| Component | Effort | Risk |
|-----------|--------|------|
| TurnLedger dataclass | Trivial (~50 lines) | None |
| Task-level subprocess spawning | Moderate (~200 lines) | Medium |
| Tasklist parser | Moderate (~100 lines) | Low |
| Context injection prompt builder | Moderate (~150 lines) | Medium |
| Per-task result file management | Low (~80 lines) | Low |
| Phase result aggregation | Low (~60 lines) | Low |
| Task dependency ordering | Moderate (~120 lines) | Medium |
| 4-layer subprocess isolation | Low (~40 lines) | Low |
| Turn counting (post-hoc) | Trivial (~15 lines) | Low |
| Retry logic at task granularity | Low (~50 lines) | Low |
| **Total** | **~865 lines, 3-4 weeks** | **Medium** |

---

## 8. Key Design Decisions

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Budget scope | Per-sprint | Simplest model; phases draw from shared pool |
| Reimbursement rate | 90% | Natural decay ensures termination; configurable |
| Agent awareness | None | Budget is runner-side only; agent is untrusted |
| Subprocess granularity | Per-task | Structural elimination of Completion Protocol dependence |
| 4-layer isolation | Mandatory | Without it, cold-start overhead is prohibitive (50K→5K tokens) |
| error_max_turns detection | Included | Orthogonal defense-in-depth, zero cost |
| Staged delivery | Yes | Phase 1 delivers value in 1 week; full migration in 3-5 weeks |
| Context injection | Structured summaries | Deterministic, verifiable, inspectable |

---

## 9. Adversarial Debate Summary

This recommendation was produced through a structured adversarial debate (2 rounds, standard depth) comparing per-phase and per-task subprocess architectures. Key outcomes:

- **Per-task won 5 of 8 resolved diff points**, particularly on Completion Protocol elimination (80% confidence) and failure blast radius (85% confidence)
- **Per-phase won 3 points**, particularly on context preservation (65% confidence) and cold-start overhead (60% confidence)
- **2 points were split** (runner role, recovery simplicity)
- **Convergence**: 80% (at threshold)

The per-phase approach's strongest contribution — the error_max_turns detection mechanism and staged adoption strategy — is incorporated into the merged output. The per-task architecture is the recommended long-term target, with immediate value delivered through the Phase 1 TurnLedger deployment.
