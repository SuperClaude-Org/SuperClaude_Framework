# Strategy: LW Component — DNSP Protocol

**Component**: DNSP Protocol (Detect-Nudge-Synthesize-Proceed)
**Source**: `.gfdoc/docs/guides/RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

DNSP is a structured recovery protocol that guarantees pipeline liveness in the face of agent non-compliance. It provides a bounded, deterministic path from failure detection to continuation without human intervention.

**Core rigor mechanisms:**

- **Detect phase**: Active monitoring for missing artifacts. System waits with exponential backoff (up to 6 attempts, 1-6 second intervals) to tolerate filesystem latency and tool flush delays. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1167-1170`
- **Nudge phase**: Bounded retry with imperative instructions. Maximum `MAX_NUDGE_WORKER` (default 2) attempts. Each nudge is a specific directive: "Write worker_handoff_batchN.md now using programmatic_handoff_batchN.json and task file. Do NOT redo work." `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1172-1177`
- **Synthesize phase**: When nudge limit exceeded, system programmatically constructs the missing artifact from conversation evidence: mines tool calls for `files_created`/`files_modified`, extracts context mentioning batch items, creates minimal viable artifact. Marked with `<!-- PABLOV v1 (SYNTHESIZED) -->`. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1183-1188`
- **Proceed phase**: System always produces a handoff (Worker-created, nudge-created, or synthesized) and continues. "Never wedges" on recoverable errors. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1190-1193`
- **Two distinct recovery paths**: Path 1 (Active DNSP) for live sessions; Path 2 (Incomplete batch recovery) for dead sessions at startup. Each path is appropriate to its context. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1153-1303`
- **Full audit trail**: Every recovery action is logged with timestamp, role, session ID, batch number, and reason. `ib_agent_core.md:647-650`

**Rigor verdict**: The "never wedge" guarantee combined with a bounded escalation path is the key insight. DNSP ensures that a non-compliant agent cannot halt the pipeline indefinitely. The synthesis-from-evidence fallback is particularly rigorous — it produces a verifiable artifact even when the agent failed.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- Two separate recovery paths (Path 1: active session DNSP; Path 2: startup recovery) with overlapping but distinct logic add implementation complexity. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1284-1303`
- The conversation mining for synthesis (grep JSONL, extract tool calls, build evidence) is expensive and requires access to raw conversation files in a specific format.

**Operational drag:**
- The exponential backoff wait (up to 6 attempts × exponential timing) in the Detect phase adds wall-clock latency to every batch where the Worker fails to write a handoff. Even in success cases, filesystem latency can trigger the wait.
- `MAX_NUDGE_WORKER=2` means up to 2 additional Claude invocations before synthesis. Each nudge is a full session resume.

**Token/runtime expense:**
- A full DNSP recovery sequence (detect wait + 2 nudge sessions + synthesis + proceed) adds significant overhead to a batch that should have been simple.
- The synthesis phase requires reading and mining the entire conversation JSONL — this is I/O intensive and increases linearly with session length.

**Maintenance burden:**
- The DNSP logic is embedded in the 6000-line bash script. Modifying recovery behavior requires navigating the full orchestrator.
- The synthesis artifact is marked as synthesized, but QA agents must understand this distinction and not fail on synthesized handoffs — adding implicit coupling between DNSP and QA behavior.

---

## 3. Execution Model

DNSP operates as an **automatic recovery middleware** invoked whenever an expected artifact is missing after agent execution:

**Path 1 (Active Session)**:
- Worker completes → handoff missing → wait with backoff → if still missing: nudge (bounded) → if nudge fails: synthesize from conversation → proceed to QA

**Path 2 (Dead Session Recovery)**:
- Script resumes → finds `worker_in_progress` batch → checks item completion in taskspec → all items marked [x] → creates recovery handoff directly → proceeds to QA

The protocol is invoked automatically by the orchestrator, transparent to the Worker and QA agents (they do not know recovery occurred, except via the synthesis marker in the handoff).

**Quality enforcement**: DNSP does not relax QA standards — QA still validates the synthesized handoff as rigorously as a Worker-written one. The synthesis marker is for audit purposes, not for QA leniency.

**Extension points**:
- `MAX_NUDGE_WORKER` and `MAX_NUDGE_QA` are configurable
- Nudge prompt content can be customized
- Context extraction depth configurable via `PABLOV_CONVO_CONTEXT_LINES_BEFORE/AFTER`

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The "never wedge" principle is directly adoptable as a SuperClaude sprint execution rule: when a sub-agent fails to produce an expected artifact, the orchestrator synthesizes a minimal viable artifact and continues rather than halting.
- The bounded nudge pattern (specific directive + retry limit) is directly adoptable for SuperClaude's agent delegation failures.
- The audit trail requirement (log every recovery action) is directly adoptable.

**Conditionally Adoptable:**
- The exponential backoff detect phase is conditionally adoptable. Useful for filesystem-I/O contexts; less relevant for in-memory agent invocations.
- The two-path recovery model (live session vs. dead session) is conditionally adoptable, specifically for sprint CLI contexts where sessions can be interrupted and resumed.

**Reject:**
- The conversation JSONL mining for synthesis — this is tightly coupled to Claude's session file format and not portable to other execution contexts.
- The bash implementation of recovery logic — should be reimplemented in a higher-level language if adopted.
