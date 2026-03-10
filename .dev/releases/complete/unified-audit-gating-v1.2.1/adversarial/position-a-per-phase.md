# Position A: Per-Phase Subprocess with Turn-Budget Reimbursement

**Proposal**: Enhance the current per-phase subprocess model with a TurnLedger that reimburses turns upon trailing gate verification. One subprocess per phase (unchanged architecture). The runner allocates `min(remaining_budget, default_phase_budget)` turns to each phase subprocess. Trailing gates audit at phase granularity. On PASS, phase turns are reimbursed at 90%.

---

## 1. Problem Context

The sprint runner's MaxTurn problem: Claude Code subprocesses silently exhaust their `--max-turns` budget, exit with code 0, and the runner classifies incomplete phases as successful (`PASS_NO_REPORT`). The Completion Protocol report — the agent's self-assessment — is always the first casualty because it's the last step.

**This position argues**: The per-phase subprocess model is the right architecture. The real problem is the fixed, one-way budget drain — not the subprocess granularity. Adding a revolving turn budget via the TurnLedger solves the economic problem while preserving the strengths of the current architecture.

---

## 2. Architecture

### 2.1 Subprocess Model (Unchanged)

One Claude Code subprocess per phase. Each subprocess receives a tasklist file containing 5-13 tasks and executes them autonomously within a single session.

```
Sprint Runner
  ├── Phase 1 subprocess (8 tasks, --max-turns N)
  ├── Phase 2 subprocess (6 tasks, --max-turns N)
  ├── Phase 3 subprocess (10 tasks, --max-turns N)
  ├── Phase 4 subprocess (13 tasks, --max-turns N)
  └── Phase 5 subprocess (9 tasks, --max-turns N)
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

### 2.3 Transaction Flow Per Phase

```
1. BEFORE LAUNCH:  Check ledger.available() >= minimum_allocation (e.g., 10)
                   If not: HALT sprint (budget exhausted)
2. ALLOCATE:       max_turns = min(ledger.available(), default_phase_budget)
3. LAUNCH:         claude --max-turns {max_turns} -p <phase_prompt>
4. MONITOR:        OutputMonitor tracks NDJSON stream, counts turns in real-time
5. ON EXIT:        actual_turns = monitor.state.turns_consumed
                   ledger.debit(actual_turns)
6. TRAILING GATE:  audit(phase_output) -> PASS or FAIL
7. REIMBURSE:      if PASS: ledger.credit(actual_turns)
                   if FAIL: no credit (turns permanently spent)
```

### 2.4 Reimbursement Cycle (Worked Example)

Using real data from the cleanup-audit-v2 sprint:

| Phase | Tasks | Allocated | Used | Gate | Reimbursed (90%) | Budget After |
|-------|-------|-----------|------|------|-------------------|-------------|
| P1 | 8 | 50 | 45 | PASS | 40 | 195 |
| P2 | 6 | 50 | 42 | PASS | 37 | 190 |
| P3 | 10 | 50 | 38 | PASS | 34 | 186 |
| P4 | 13 | 50 | 48 | PASS | 43 | 181 |
| P5 | 9 | 50 | ~50 | ? | ? | ? |

Key observation: P5 still gets its full 50-turn allocation because the budget remains healthy at 181. Under the original fixed-budget model, each phase consumed from the same `--max-turns 50` independently — there was no cross-phase budget awareness. Under the TurnLedger, the runner actively manages the pool.

---

## 3. How This Solves the MaxTurn Problem

### 3.1 Budget Health Through Reimbursement

The original problem: Phase 5 exhausted its 50-turn budget at task 5/9, leaving 4 tasks unexecuted. With reimbursement:

- Phases 1-4 collectively consume 173 turns, reimburse 154 turns
- Net drain: 19 turns across 4 phases
- Budget remains at 181/200 entering Phase 5
- Phase 5 gets a full 50-turn allocation (not starved by prior phases)

The 90% reimbursement rate means the budget drains slowly (net ~5 turns/phase for passing work), providing generous headroom.

### 3.2 Detection of Budget Exhaustion

Orthogonal to reimbursement, the runner gains the ability to detect `error_max_turns` in the NDJSON output stream (the problem statement notes this event is already present). This reclassifies `PASS_NO_REPORT` as `INCOMPLETE`:

```
Priority 9 (REVISED):
  no result file, output exists, error_max_turns detected → INCOMPLETE (is_failure)
  no result file, output exists, no error_max_turns       → PASS_NO_REPORT (is_success)
```

This detection is cheap (regex on the last NDJSON line) and eliminates the "silent data loss" problem entirely, regardless of reimbursement.

### 3.3 The 90% Decay as Safety Valve

Even with perfect work (all phases PASS), the budget decays:
- 200 → 195 → 190 → 186 → 181 → 176 → ...
- After ~40 perfect phases, the budget would reach 0
- This makes infinite-run mathematically impossible
- A sprint that produces consistently bad work (FAIL) drains the budget rapidly

---

## 4. Arguments For This Approach

### 4.1 Minimal Architectural Change

The sprint runner already works with per-phase subprocesses. Adding a TurnLedger is purely additive:
- New `TurnLedger` dataclass (< 50 lines)
- New field on `MonitorState`: `turns_consumed: int` (1 line)
- New counting logic in `OutputMonitor._extract_signals_from_event()` (~5 lines)
- Budget check before `ClaudeProcess` launch (~10 lines in executor)
- Reimbursement call after trailing gate (~5 lines)

No changes to: prompt construction, process spawning, status classification chain, TUI, logging, diagnostics, or the trailing gate infrastructure itself.

### 4.2 Context Preservation

A single subprocess running 8-13 tasks retains full conversational context. The agent remembers:
- What files it read in task 1 when working on task 8
- Design decisions made in task 3 that affect task 7
- Error patterns encountered in task 2 that inform task 5

This is not a minor benefit. Interdependent tasks within a phase are the norm:
- "Implement function X" → "Write tests for X" → "Update docs for X"
- "Add state enum" → "Wire enum into validator" → "Test transitions"

Per-phase context means zero re-orientation cost between tasks.

### 4.3 Lower Overhead

5-6 subprocess spawns per sprint vs. 40-60 for per-task. Each Claude Code subprocess has cold-start cost:
- Without isolation: ~50K tokens on turn 1 (per dev.to analysis)
- With 4-layer isolation: ~5K tokens on turn 1
- Per-phase (6 phases): 30K-300K tokens of overhead
- Per-task (50 tasks): 250K-2.5M tokens of overhead

This overhead is NOT reimbursable — it's infrastructure cost, not task work. Per-phase minimizes it.

### 4.4 Amortized Planning Cost

The agent plans once for the whole phase — reading the tasklist, understanding dependencies, planning execution order. Per-task spawning forces this planning cost on every single task, consuming turns on orientation rather than productive work.

### 4.5 Phase-Level Reporting is Natural

The existing Completion Protocol and result file format capture all tasks in a phase. No aggregation layer needed. The runner's `_determine_phase_status()` chain works unchanged.

### 4.6 Simpler Error Recovery

"Re-run phase 5" = one subprocess spawn with the same tasklist file. The trailing gate's remediation mechanism already handles this: remediate → retry → halt-with-diagnostics. No new orchestration needed.

### 4.7 Alignment with Trailing Gate Design

The trailing gate design (v2.0) already operates at phase granularity in the sprint executor. Adding reimbursement is a one-line extension to the gate result handler:

```python
if gate_result.passed:
    ledger.credit(phase_result.turns_consumed)
```

---

## 5. Acknowledged Weaknesses

### 5.1 Coarse-Grained Failure

If Phase 3 (13 tasks) fails its trailing gate because task 10 produced bad output, ALL 13 tasks' turns are lost — including the 9 tasks that individually would have passed.

**Mitigation**: The trailing gate could evaluate per-task within the phase (inspect individual task outputs in the result file), enabling partial reimbursement. This is an enhancement, not a redesign.

### 5.2 The Completion Protocol Remains Probabilistic

More budget makes max-turns exhaustion less likely but doesn't guarantee the report gets written. The structural design gap persists: the agent's self-reporting ability is constrained by the same budget.

**Mitigations**:
- `error_max_turns` detection (Section 3.2) catches the case with zero extra turns
- Turn reservation: set `--max-turns` to `budget - 5`, reserving headroom for the report
- The OutputMonitor already tracks `last_task_id` — the runner can infer completion state from this

### 5.3 All-or-Nothing Reimbursement

Can't natively reimburse "tasks 1-7 passed but 8-10 failed" at phase granularity.

**Mitigation**: Per-task evaluation within the phase gate (same as 5.1).

### 5.4 Harder Cost Attribution

"Phase 3 cost 45 turns" is less actionable than per-task breakdowns for optimizing tasklist design.

**Mitigation**: The NDJSON stream contains task IDs (via `last_task_id` in MonitorState). A turn-per-task breakdown can be estimated by correlating task ID changes with turn counts — this is a reporting enhancement, not an architectural change.

---

## 6. The Completion Protocol Under This Model

The Completion Protocol is the last step in the agent's prompt. Under per-phase + reimbursement:

1. **Budget health reduces exhaustion probability**: With reimbursement, each phase gets a healthy budget allocation. The original Phase 5 problem (9 tasks in 50 turns) becomes less likely.

2. **Detection eliminates silent failure**: `error_max_turns` detection reclassifies `PASS_NO_REPORT` as `INCOMPLETE`. The sprint halts or flags, rather than silently continuing.

3. **Turn reservation provides headroom**: Setting `--max-turns` to `budget - 5` ensures the agent has turns reserved for the report.

4. **The runner has fallback intelligence**: `MonitorState.last_task_id` tells the runner which task the agent was working on when it stopped. Combined with the parsed tasklist (task count), the runner can determine "completed 5/9 tasks" without the agent's self-report.

The Completion Protocol problem is not structurally eliminated, but it is mitigated on three independent axes (budget, detection, reservation), making failure improbable.

---

## 7. Implementation Complexity

| Component | Effort | Risk |
|-----------|--------|------|
| TurnLedger dataclass | Trivial (~50 lines) | None |
| MonitorState.turns_consumed | Trivial (1 field + 5 lines) | Low (NDJSON format coupling) |
| Budget check before launch | Trivial (~10 lines) | None |
| Reimbursement after gate | Trivial (~5 lines) | None |
| error_max_turns detection | Low (~15 lines) | Low |
| Turn reservation | Trivial (arithmetic) | None |
| **Total** | **~1 week** | **Low** |

This is an incremental enhancement to the existing architecture, not a redesign.
