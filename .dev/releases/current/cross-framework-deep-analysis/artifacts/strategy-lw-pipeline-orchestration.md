# Strategy: LW Component — Pipeline Orchestration

**Component**: Pipeline Orchestration (Rigorflow Pipeline)
**Source**: `.claude/commands/rf/pipeline.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The pipeline orchestration system defines a structured, event-driven multi-agent execution model with explicit parallelism support and a clean fallback degradation path.

**Core rigor mechanisms:**

- **Multi-track architecture**: N independent work streams each get their own researcher→builder→executor chain. Tracks are isolated: a failure in one track does not prevent other tracks from completing. `pipeline.md:55-67`
- **Event-driven per-track progression**: Fast tracks are not blocked by slow tracks. When researcher-1 finishes, builder-1 starts immediately without waiting for researcher-2. Minimizes total pipeline time by eliminating synchronization barriers on the critical path. `pipeline.md:67`
- **Per-track state map**: Team lead maintains explicit state for each track (`research=[pending|done|skipped]`, `build=[pending|in_progress|done]`, `execute=[pending|in_progress|done|failed]`). State is tracked, not inferred. `pipeline.md:464-470`
- **Explicit fallback**: "If event-driven per-track doesn't work reliably, fall back to phased-parallel: wait for ALL researchers → spawn ALL builders → wait for ALL executors." The fallback is documented and the failure condition is specified. `pipeline.md:458-462, 769`
- **Maximum track limit**: Hard cap at 5 parallel tracks (15 agents: 5 researchers + 5 builders + 5 executors). `pipeline.md:83 (CHANGELOG)`
- **Structured handoff messages**: All inter-agent communication uses explicit typed messages: `RESEARCH_READY`, `TASK_READY`, `EXECUTION_COMPLETE`, `BLOCKED`, `EXECUTION_ERROR`. `pipeline.md:804 (message protocol table reference)`
- **Track isolation**: Each track's builder communicates only with its own track's researcher (`researcher-T`), not cross-track. `pipeline.md:779`

**Rigor verdict**: The per-track state map and the explicit fallback documentation are both rigorous design choices. The fallback is particularly notable — the design acknowledges that the experimental model may fail and provides a deterministic degradation path. Track isolation (no cross-track communication) prevents interference bugs.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The team lead must maintain per-track state and handle interleaved messages from multiple researchers. This is complex orchestration logic that introduces coordination bugs when message delivery is unreliable.
- Spawning up to 15 agents (5 researchers + 5 builders + 5 executors) for maximum parallelism creates significant overhead in agent team initialization and cleanup.
- The "phased-parallel" fallback (all researchers → all builders → all executors) synchronizes at each phase boundary, eliminating the fast-track advantage but adding three synchronization barriers.

**Operational drag:**
- Agent team creation requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` flag — this is explicitly experimental infrastructure. `pipeline.md:7-13`
- Each track creates separate task files with timestamped names. For 5-track execution, 5 separate task files must be created, tracked, and cleaned up.
- The team lead reviews research findings before spawning builders — this sequential review step blocks builder-T start even in the event-driven model. `pipeline.md:472-529`

**Token/runtime expense:**
- All 4 agent roles use `model: opus` with full tool access and `permissionMode: bypassPermissions`. Maximum cost model for all agents. `rf-team-lead.md:1-30, rf-task-researcher.md:1-26`
- Each agent in a 5-track pipeline has its own full context window. Memory overhead scales with track count.
- Research notes files are written to disk per-track, then read by builders — filesystem I/O as a communication channel.

**Maintenance burden:**
- The "EXPERIMENTAL" label on the event-driven model means it has known reliability issues and may not work in all environments. The fallback existence is an acknowledgment of this instability.
- Agent team feature requires non-standard settings configuration (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`). Users must know about this dependency.
- Cleanup after pipeline completion (shut down teammates) is manual — the team lead must explicitly handle cleanup. `pipeline.md: "Clean up when done" in team lead rules`

---

## 3. Execution Model

The pipeline operates as an **event-driven multi-agent orchestration system**:

**Single track**: Team lead → researcher (RESEARCH_READY) → builder (TASK_READY) → executor (EXECUTION_COMPLETE) → aggregate results

**Multi-track**:
1. Team lead spawns all researchers simultaneously
2. As each RESEARCH_READY arrives: team lead reviews findings, immediately spawns that track's builder
3. As each TASK_READY arrives: team lead immediately spawns that track's executor
4. Each track progresses independently; fast tracks complete without waiting for slow tracks
5. Team lead aggregates all EXECUTION_COMPLETE results when all tracks finish

**Quality enforcement**: Quality is enforced by `automated_qa_workflow.sh` inside each executor, not by the pipeline orchestrator itself. The pipeline ensures execution; PABLOV ensures quality within each execution.

**Extension points**:
- Track count: 1-5 (configurable per request)
- Template selection: per-track based on task complexity
- Inter-agent communication protocol: extensible via message types
- Fallback mode: configurable via coordination model selection

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The event-driven per-track progression pattern (fast tracks not blocked by slow tracks) is directly adoptable for SuperClaude's `/sc:spawn` and parallel task delegation.
- Track isolation (no cross-track agent communication) is directly adoptable as a sub-agent isolation rule.
- The explicit documented fallback (event-driven → phased-parallel with known trigger conditions) is directly adoptable as SuperClaude's degradation strategy for parallel agent failures.

**Conditionally Adoptable:**
- The per-track state map maintained by the orchestrator is conditionally adoptable. SuperClaude's TodoWrite already tracks task state; extending it with per-track sub-states is feasible.
- The structured handoff messages (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE) are conditionally adoptable as SuperClaude's sub-agent result protocol.

**Reject:**
- The `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` dependency as a required infrastructure feature. SuperClaude should not depend on experimental APIs.
- All-`opus` model selection for all agents. Cost is prohibitive for standard tasks. SuperClaude's agent model selection should be tiered by role complexity.
- The filesystem-as-communication-channel pattern (research notes written to disk) — in-context communication is more efficient for co-session agents.
