# Brainstorm: Turn-Budget Reimbursement via Unified Audit Gating

**Status**: BRAINSTORM OUTPUT — Ready for `/sc:adversarial`
**Date**: 2026-03-06
**Context**: Solving the MaxTurn Problem (silent incomplete phases) through economic turn-budget management integrated with trailing gate verification.

---

## 1. Problem Recap

The sprint runner spawns Claude Code subprocesses with a fixed `--max-turns` budget. When a subprocess exhausts its budget, Claude Code exits with code 0 (indistinguishable from normal completion), and any unfinished tasks — including the Completion Protocol report — are silently dropped. The sprint reports success when work is incomplete.

**Root cause**: The turn budget is a fixed, one-way drain. Once consumed, turns are gone regardless of outcome quality.

**Proposed solution**: Make the turn budget a **revolving credit line** where verified work earns back capacity through the Unified Audit Gating process.

---

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
  credit(n)   -> reimbursed += min(n * reimbursement_rate, n)
```

### 2.2 Transaction Flow

```
1. BEFORE LAUNCH:  Check ledger.available() >= minimum_allocation
                   If not: HALT sprint (budget exhausted)
2. ALLOCATE:       max_turns = min(ledger.available(), default_allocation)
3. LAUNCH:         claude --max-turns {max_turns} ...
4. ON EXIT:        actual_turns = track_turns(subprocess)
                   ledger.debit(actual_turns)
5. TRAILING GATE:  audit(output) -> PASS or FAIL
6. REIMBURSE:      if PASS: ledger.credit(actual_turns)
                   if FAIL: no credit (turns permanently spent)
```

### 2.3 Retry Reimbursement Rule

- First attempt fails audit → turns NOT reimbursed
- Remediation (second attempt) passes audit → only remediation turns reimbursed
- Both attempts fail → both sets of turns permanently lost → contributes to budget exhaustion → sprint halts

### 2.4 The 90% Reimbursement Rate

A 90% reimbursement rate creates **natural budget decay** even when everything passes. This is a safety valve:

- Sprint with 10 phases, each using 20 turns: 200 consumed, 180 reimbursed
- Net drain per perfect phase: 2 turns
- A 200-turn budget can sustain ~100 perfect phases before exhaustion
- This makes infinite-run mathematically impossible

The rate is configurable. 100% = no decay (pure revolving). Lower rates = faster termination.

---

## 3. Three Turn-Tracking Proposals

All three share the TurnLedger. They differ in HOW turns are counted.

### 3.1 Proposal A: NDJSON Stream Turn Counter

**How it works**: Extend the existing `OutputMonitor` to count turns in real-time by parsing the NDJSON stream that Claude Code already emits.

**Mechanism**:
- `OutputMonitor._process_chunk()` already parses every NDJSON line at 0.5s intervals
- Add `turns_consumed: int` to `MonitorState`
- Count events where `type == "assistant"` as one turn (each assistant response = one turn cycle)
- Alternative: count unique `"id":"msg_..."` patterns (the gist approach, but real-time)
- Runner reads `monitor.state.turns_consumed` after subprocess exits

**Implementation sketch**:
```python
# In OutputMonitor._extract_signals_from_event():
if event_type == "assistant":
    self.state.turns_consumed += 1
# OR: extract msg_ ID and add to a set for dedup
```

**Strengths**:
- Uses existing infrastructure (OutputMonitor already running)
- Real-time visibility — runner can see budget consumption DURING execution
- Enables future capability: interrupt subprocess when budget is nearly exhausted
- Minimal new code (~10 lines in monitor.py, new field in MonitorState)
- Tested against the same stream the runner already trusts

**Weaknesses**:
- Coupled to Claude Code's NDJSON event schema
- Definition of "turn" depends on Claude Code semantics (what constitutes a `type: assistant` event?)
- If Claude Code changes event types or adds internal events, count could drift
- Not portable to non-Claude-Code runtimes without adaptation

**Portability**: When porting to a new runtime, swap the NDJSON parser for the new runtime's event stream. TurnLedger is unchanged.

---

### 3.2 Proposal B: Output Artifact Turn Estimation (Post-Hoc)

**How it works**: After a subprocess exits, analyze its output file to count turns. Direct evolution of the [brumar/hook.sh gist](https://gist.github.com/brumar/4dd067342bd92031c21f7c0afae7ae32) approach.

**Mechanism**:
- Subprocess runs and exits
- Runner reads the output file (already captured at `config.output_file(phase)`)
- Count unique `msg_` IDs via regex (proven approach from the gist)
- Debit counted turns from TurnLedger

**Implementation sketch**:
```python
def count_turns_from_output(output_path: Path) -> int:
    """Count unique assistant message IDs in output file."""
    msg_ids: set[str] = set()
    with open(output_path) as f:
        for line in f:
            matches = re.findall(r'"id"\s*:\s*"(msg_[^"]+)"', line)
            msg_ids.update(matches)
    return len(msg_ids)
```

**Strengths**:
- Simplest implementation — zero changes to the monitoring loop
- Works retroactively on existing sprint output files (could audit past sprints)
- Battle-tested approach (the gist + community usage proves viability)
- Easy to unit test — feed it a file, assert a count
- No threading concerns — runs after subprocess exits on main thread

**Weaknesses**:
- Post-hoc only — no real-time visibility during execution
- Cannot interrupt a subprocess approaching budget exhaustion
- Regex-based parsing is fragile to format changes
- Slightly less accurate if output file is truncated or corrupted
- Same Claude Code coupling as Proposal A, just at the file level

**Portability**: Same as A — the output format is the coupling point.

---

### 3.3 Proposal C: Orchestrator Envelope Ledger (Runtime-Agnostic)

**How it works**: The runner doesn't count the subprocess's internal turns at all. It treats each subprocess invocation as a **budgeted transaction** with a known maximum cost (the `--max-turns` value it allocated). Actual cost is estimated from observable signals.

**Mechanism**:
```
1. PRE-LAUNCH:    ledger.hold(max_turns_allocated)        # pessimistic reservation
2. LAUNCH:        subprocess runs with --max-turns N
3. POST-EXIT:
   - If error_max_turns detected: actual = N              # hit the ceiling
   - If exited normally: actual = estimate(elapsed, events, output_size)
   - ledger.release_hold(N)                               # release reservation
   - ledger.debit(actual)                                  # charge real cost
4. POST-GATE:     if PASS: ledger.credit(actual)          # reimbursement
```

This is a **credit card authorization hold** model:
- Hold the max before the transaction
- Settle for the actual amount after
- Merchant (trailing gate) decides if you get a refund

**Estimation heuristics for "exited normally" case**:
- `events_received / expected_events_per_turn` (from MonitorState)
- `elapsed_seconds / avg_seconds_per_turn` (calibrated over the sprint)
- `output_bytes / avg_bytes_per_turn` (calibrated over the sprint)
- Weighted average of the three, with confidence bounds

**Strengths**:
- Completely runtime-agnostic — no NDJSON parsing, no msg_ ID counting
- Works with ANY subprocess runner (Claude Code, Aider, custom agents, future runtimes)
- Pessimistic hold prevents over-commitment: never launch what you can't afford
- Clean accounting model (hold → settle → reimburse) well-understood in financial systems
- Best portability story — the entire mechanism is self-contained in the runner

**Weaknesses**:
- Actual turn count is estimated, not measured — less precise
- Estimation heuristics need calibration data (first sprint is least accurate)
- Pessimistic holds temporarily reduce effective budget during execution
- Over-estimation means under-utilization; under-estimation means ledger inaccuracy
- The `error_max_turns` detection still requires NDJSON parsing (one coupling point)

**Portability**: Most portable. When porting, only the `error_max_turns` detection needs adaptation. Everything else is runtime-agnostic.

---

### 3.4 Proposal Comparison Matrix

| Dimension | A: NDJSON Stream | B: Post-Hoc File | C: Orchestrator Envelope |
|-----------|------------------|-------------------|--------------------------|
| Accuracy | High (real-time count) | High (exact msg IDs) | Medium (estimated) |
| Real-time visibility | Yes | No | Partial (hold amount) |
| Can interrupt mid-run | Future capability | No | No |
| Implementation effort | Low (~10 lines) | Very low (~15 lines) | Medium (~50 lines) |
| Claude Code coupling | NDJSON event types | Output file format | Only error_max_turns |
| Portability to new runtime | Swap parser | Swap parser | Swap error detection only |
| Works on past sprints | No | Yes | No |
| Threading concerns | Uses existing monitor thread | None (post-hoc) | Hold/release timing |

---

## 4. Per-Phase vs Per-Task Subprocess Granularity

### 4.1 Position A: Per-Phase Subprocess (Enhanced Current Model)

**Architecture**: One subprocess per phase (unchanged). Runner allocates `min(remaining_budget, default_phase_budget)` turns. Trailing gate audits at phase granularity. On PASS, phase turns are reimbursed.

**The reimbursement cycle**:
```
Phase 1 (8 tasks): allocated 50 turns, used 45
  → ledger.debit(45)      → available: 155
  → gate(Phase 1): PASS
  → ledger.credit(45 * 0.9 = 40.5 ≈ 40)  → available: 195
  → net cost of Phase 1: 5 turns

Phase 2 (6 tasks): allocated 50 turns, used 38
  → ledger.debit(38)      → available: 157
  → gate(Phase 2): PASS
  → ledger.credit(38 * 0.9 = 34.2 ≈ 34)  → available: 191
  → net cost of Phase 2: 4 turns
```

**Arguments FOR**:

1. **Minimal architectural change**: The sprint runner already works this way. Adding a TurnLedger is additive. No restructuring of the executor loop, prompt builder, or monitor.

2. **Context preservation**: A single subprocess running 8-13 tasks retains full context. The agent remembers task 1's work when executing task 8. This is critical for interdependent tasks ("implement function" → "write tests for it").

3. **Lower overhead**: 5-6 subprocess spawns per sprint vs 50+. Per the [dev.to analysis](https://dev.to/jungjaehoon/why-claude-code-subagents-waste-50k-tokens-per-turn-and-how-to-fix-it-41ma), each Claude Code subprocess consumes ~50K tokens on its first turn (or ~5K with 4-layer isolation). At 50 tasks, that's 250K-2.5M tokens of pure overhead.

4. **Amortized planning cost**: The agent plans once for the whole phase. Per-task spawning forces re-planning per task, consuming turns on orientation rather than work.

5. **The budget problem is sufficiently mitigated**: With reimbursement keeping the budget healthy, phases are far less likely to exhaust their allocation. Phase 5 in the original problem (5/9 tasks completed at turn 51) would have had a much larger budget if Phases 1-4 had been reimbursed.

6. **Phase-level reporting is natural**: The existing Completion Protocol and result file format capture all tasks in a phase. No new aggregation layer needed.

7. **Simpler error recovery**: "Re-run phase 5" is one subprocess. "Re-run tasks T05.06-T05.09" requires the runner to manage partial task lists.

**Arguments AGAINST**:

1. **Coarse-grained failure**: If Phase 3 (13 tasks) fails its gate because task 10 produced bad output, ALL 13 tasks' worth of turns are lost — including the 9 tasks that individually would have passed. This is wasteful.

2. **The Completion Protocol remains the last casualty**: More budget reduces the probability of hitting max-turns but doesn't eliminate it. The structural design gap (agent self-reports using the same budget it works with) persists.

3. **All-or-nothing reimbursement**: Can't reimburse "tasks 1-7 passed but 8-10 failed." The gate evaluates the whole phase.

4. **Harder cost attribution**: "Phase 3 cost 45 turns" is less actionable than per-task cost breakdowns for optimizing tasklist design.

5. **Partial completion is invisible to the ledger**: If the agent completes 5/9 tasks and hits max-turns, no reimbursement is possible for the 5 good tasks at phase granularity.

**Available mitigations**:
- Detect `error_max_turns` in NDJSON stream → reclassify `PASS_NO_REPORT` as `INCOMPLETE` → don't reimburse
- Reserve N turns for Completion Protocol by setting `--max-turns` to `budget - 5`
- Per-task trailing gate within the phase (evaluate individual task outputs, reimburse per-task)
- Runner parses tasklist file to know expected task count, compares against `last_task_id` from monitor

---

### 4.2 Position B: Per-Task Subprocess (New Granular Model)

**Architecture**: One subprocess per task. Runner spawns a fresh Claude Code process for each individual task in the tasklist. Each subprocess gets `min(remaining_budget, default_task_budget)` turns. Trailing gate audits each task independently.

**The reimbursement cycle**:
```
Task T03.01: allocated 15 turns, used 8
  → ledger.debit(8)       → available: 192
  → gate(T03.01): PASS
  → ledger.credit(8 * 0.9 = 7.2 ≈ 7)  → available: 199
  → net cost: 1 turn

Task T03.02: allocated 15 turns, used 12
  → ledger.debit(12)      → available: 187
  → gate(T03.02): FAIL
  → no credit             → available: 187
  → net cost: 12 turns (penalty for bad work)

Task T03.02 (retry): allocated 15 turns, used 10
  → ledger.debit(10)      → available: 177
  → gate(T03.02): PASS
  → ledger.credit(10 * 0.9 = 9)  → available: 186
  → net cost of retry: 1 turn (only successful attempt reimbursed)
```

**Arguments FOR**:

1. **Maximum granularity**: Turn accounting is precise per-task. Cost attribution is exact: "T03.04 cost 8 turns, T03.05 cost 12 turns." This enables data-driven tasklist optimization.

2. **The Completion Protocol problem is structurally eliminated**: Each subprocess has ONE task plus a trivial report. Even if max-turns is hit, the runner knows exactly which task was running (it launched it). The runner can construct the phase report itself by aggregating task results. No dependence on agent self-reporting.

3. **Isolated failure**: A failed task costs only its own turns. Tasks 1-9 passing are individually reimbursable even if task 10 fails. No collateral damage.

4. **Natural trailing gate alignment**: One gate per task, one reimbursement decision per task. The gate/task/reimbursement mapping is 1:1 — clean and auditable.

5. **Precise retry**: "Retry T03.04" spawns one subprocess for one task. No wasted re-execution of already-passed tasks.

6. **Runner becomes source of truth**: The runner knows which tasks exist (parsed from tasklist), which completed, and which remain. Zero dependence on agent self-reporting. This directly addresses the root cause identified in the MaxTurn Problem Statement.

7. **Best portability**: Per-task spawning maps naturally to any agent runtime. Each task is an independent job — this is the model used by CI/CD systems, job queues, and distributed task runners.

**Arguments AGAINST**:

1. **Context fragmentation**: Task 5's subprocess doesn't know what task 4 did. If task 5 depends on task 4's output (common within a phase), the agent must rediscover context from scratch. This costs turns — turns that would have been free in a shared session.

2. **Subprocess cold-start overhead**: Per [dev.to analysis](https://dev.to/jungjaehoon/why-claude-code-subagents-waste-50k-tokens-per-turn-and-how-to-fix-it-41ma), each Claude Code subprocess consumes ~50K tokens on turn 1 (or ~5K with isolation). For 50 tasks, that's:
   - Without isolation: ~2.5M tokens of pure overhead
   - With isolation: ~250K tokens of overhead
   - In turn terms at ~5K tokens/turn: 50-500 turns spent on startup alone
   - This overhead is NOT reimbursable (it's infrastructure, not task work)

3. **Loss of inter-task optimization**: An agent processing 8 tasks reads a file once and applies knowledge across all tasks. Per-task spawning forces redundant file reads, duplicating work.

4. **Context passing problem**: How does task 5's subprocess know about task 4's changes?
   - **Option**: Include prior task results in prompt → prompt grows with each task
   - **Option**: Git diff since sprint start → diff grows with each task
   - **Option**: Summary of prior work → lossy compression, may miss details
   - None are as good as the agent simply remembering its own work

5. **More total turns consumed**: Cold-start overhead + context re-acquisition + redundant file reads = more total turns across the sprint. Reimbursement may not offset the inflated consumption.

6. **Complex orchestration**: The runner must manage:
   - Task dependency ordering
   - Context injection between tasks
   - File change tracking per task
   - Result aggregation into phase reports
   - Retry logic at task granularity
   This is significantly more complex than "launch phase, wait."

7. **API rate limiting risk**: Rapid subprocess spawning may trigger rate limits on the underlying Claude API, adding delays or failures.

**Available mitigations**:
- 4-layer isolation (from dev.to) reduces cold-start from 50K to 5K tokens
- Context injection: auto-generate "prior work summary" from prior task results
- Batched spawning: group 2-3 related tasks per subprocess (micro-phases)
- Dependency-aware ordering: sequence spawns to minimize context gaps
- Pre-warm: pass consistent project context files to reduce orientation cost

---

### 4.3 Comparison Matrix for Adversarial Debate

| Dimension | A: Per-Phase | B: Per-Task |
|-----------|-------------|-------------|
| **Subprocess spawns per sprint** | 5-6 | 40-60 |
| **Cold-start overhead (total)** | ~250K-300K tokens | ~250K-3M tokens |
| **Context within phase** | Full (shared session) | None (must inject) |
| **Turn accounting granularity** | Phase-level | Task-level |
| **Completion Protocol risk** | Mitigated (bigger budget) | Eliminated (runner owns report) |
| **Failure blast radius** | All tasks in phase | Single task |
| **Reimbursement granularity** | Phase (all-or-nothing) | Task (individual) |
| **Retry precision** | Whole phase | Single task |
| **Runner complexity** | Low (additive changes) | High (new orchestration) |
| **Portability** | Good (subprocess model preserved) | Best (task = independent job) |
| **Time to implement** | Weeks (incremental) | Months (new architecture) |
| **Risk of increased total turns** | Low | High (overhead may exceed savings) |
| **Diagnostic value of ledger** | Moderate | High (per-task cost data) |
| **Alignment with trailing gate** | Good (gate per phase) | Perfect (1:1 gate-task) |
| **Dependence on agent self-report** | Reduced but present | Eliminated |

---

## 5. The Completion Protocol Under Both Models

### 5.1 Under Per-Phase + Reimbursement

- Reimbursement keeps budgets healthy → phases get generous allocations
- Phase 5 (from the real sprint) would have had ~50 turns instead of whatever it got after Phases 1-4 drained the budget
- The probability of hitting max-turns drops significantly
- **But**: a phase with 13 complex tasks can still exhaust 50 turns
- The report is still last-mile — bigger budget reduces probability, doesn't eliminate
- **Key mitigation**: Detect `error_max_turns` in NDJSON stream → reclassify `PASS_NO_REPORT` as `INCOMPLETE`. This is orthogonal to reimbursement and should be implemented regardless.

### 5.2 Under Per-Task Subprocess

- Each subprocess does ONE task + trivial report
- Even if max-turns is hit, the runner knows which task was active
- The runner constructs phase reports by aggregating individual task results
- **The Completion Protocol problem is structurally eliminated**
- Agent self-reporting becomes optional, not critical
- **But**: the overhead cost (cold-starts, context re-acquisition) inflates total turn consumption
- Reimbursement helps offset this, but the question is whether the math works out

### 5.3 Worked Example: The Real Sprint Under Both Models

**Original sprint** (no reimbursement, per-phase, --max-turns 50):

| Phase | Tasks | Turns Used | Status | Problem |
|-------|-------|------------|--------|---------|
| P1 | 8 | 51 (max) | pass_no_report | All done, no report |
| P2 | 6 | 51 (max) | pass_no_report | All done, no report |
| P3 | 10 | <50 | pass | OK |
| P4 | 13 | <50 | pass | OK |
| P5 | 9 | 51 (max) | pass_no_report | 4 tasks never run |

**Under Per-Phase + Reimbursement** (budget: 200, per-phase default: 50):

| Phase | Allocated | Used | Gate | Reimbursed (90%) | Budget After |
|-------|-----------|------|------|-------------------|-------------|
| P1 | 50 | 45 | PASS | 40 | 195 |
| P2 | 50 | 42 | PASS | 37 | 190 |
| P3 | 50 | 38 | PASS | 34 | 186 |
| P4 | 50 | 48 | PASS | 43 | 181 |
| P5 | 50 | 50 | ? | ? | ? |

P5 still gets its full 50 turns (budget is healthy at 181). With more headroom from the reimbursement cycle, P5 is more likely to complete all 9 tasks. But if the tasks are genuinely complex, it may still exhaust budget. The `error_max_turns` detection would catch this.

**Under Per-Task Subprocess** (budget: 200, per-task default: 15):

| Task | Allocated | Used | Overhead | Gate | Reimbursed | Budget |
|------|-----------|------|----------|------|------------|--------|
| T01.01 | 15 | 8 | ~2 | PASS | 7 | 199 |
| T01.02 | 15 | 6 | ~2 | PASS | 5 | 198 |
| ... | ... | ... | ... | ... | ... | ... |
| T05.06 | 15 | 10 | ~2 | PASS | 9 | ~185 |
| T05.07 | 15 | 8 | ~2 | PASS | 7 | ~184 |

Every task gets its own budget. No task is starved. Overhead is ~2 turns/task (with isolation), so ~90 overhead turns for 45 tasks. But reimbursement covers most of it.

---

## 6. Key Design Decisions (Resolved)

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Budget scope | Per-sprint | Simplest model; phases can draw from shared pool |
| Reimbursement rate | 90% | Natural decay ensures termination; configurable |
| Agent awareness | None | Budget is runner-side only; agent is untrusted for self-regulation |
| Adversarial structure | A vs B (clean) | Per-Phase vs Per-Task as two clear positions |

## 7. Open Questions for Adversarial Debate

1. **Does the per-task overhead math actually work?** If 50 tasks each add 2-5 turns of overhead, that's 100-250 turns of non-reimbursable infrastructure cost. Does the granular reimbursement savings exceed this cost?

2. **Is context fragmentation a dealbreaker?** Per-task subprocess loses inter-task memory. How much does this actually cost in practice? Are there tasks that fundamentally cannot work without prior context?

3. **Is the per-phase model "good enough"?** If `error_max_turns` detection + reclassification is added alongside reimbursement, does per-phase become sufficient? Or is the structural elimination of the Completion Protocol problem worth the per-task overhead?

4. **What happens at scale?** A sprint with 100 tasks: per-phase (10 phases × 10 tasks) = 10 subprocesses. Per-task = 100 subprocesses. Does the orchestration complexity become untenable?

5. **Hybrid viability**: Is "per-phase with per-task monitoring" (detect budget exhaustion mid-phase, spawn continuation) better than both pure approaches?
