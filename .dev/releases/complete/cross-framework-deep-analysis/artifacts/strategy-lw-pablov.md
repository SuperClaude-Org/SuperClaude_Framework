# Strategy: LW Component — PABLOV Method

**Component**: PABLOV Method (Programmatic Artifact-Based LLM Output Validation)
**Source**: `.gfdoc/rules/core/ib_agent_core.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

PABLOV enforces a strict artifact-chain model where every stage of execution must produce a verifiable, machine-readable artifact before the pipeline proceeds. This eliminates "vibes-based" completion claims entirely.

**Core rigor mechanisms:**

- **Artifact chain completeness**: Five mandatory artifacts form an unbroken chain — `taskspec` (defines work), `expected_set` (defines batch), `worker_handoff` (claims completion), `qa_report` (validates claims), `programmatic_handoff` (proves work via filesystem evidence). No stage can be skipped. `ib_agent_core.md:106-112`
- **Agent Contracts**: Worker and QA are bound by formal contracts. Worker must complete items in `expected_set`, checkmark them in `taskspec`, and write `worker_handoff`. QA must validate item-by-item with filesystem verification and write `qa_report`. `ib_agent_core.md:87-97`
- **Zero-trust verification**: "Audit by default, trust nothing" — QA treats all Worker claims with skepticism and requires character-level verification for EXACT specifications. `ib_agent_core.md:99-104`
- **DNSP as a liveness guarantee**: The Detect-Nudge-Synthesize-Proceed protocol ensures the pipeline never permanently stalls on a missing artifact. Recovery is automatic. `ib_agent_core.md:103`
- **Five-Step Execution Pattern**: Every agent must follow READ → IDENTIFY → EXECUTE → UPDATE → REPEAT for each checklist item. Violations require task re-execution. `ib_agent_core.md:134-170`

**Rigor verdict**: PABLOV's core insight — that LLM output can only be trusted when it is backed by programmatic, filesystem-verifiable artifacts — is sound and battle-tested. The distinction between "claim" (worker_handoff) and "proof" (programmatic_handoff) is particularly rigorous.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The five-artifact chain adds significant coordination overhead. Each batch requires creation, tracking, and validation of five separate artifact types.
- The mandatory sequential pattern (READ → IDENTIFY → EXECUTE → UPDATE → REPEAT, one item at a time) explicitly prohibits parallelism, even when items are independent. `ib_agent_core.md:141-170`
- The "mandatory template usage protocol" adds a full pre-write checklist before every file creation. `ib_agent_core.md:400-413`

**Operational drag:**
- The bounded correction loop (max 5 per batch) means a single bad batch can cause 5 Worker re-executions + 5 QA re-executions before the system stops. `ib_agent_core.md:559-564`
- Session management overhead: proactive rollover at 375 messages or 175k tokens means long tasks routinely incur rollover cost even when no quality issue exists. `ib_agent_core.md:920-928`

**Token/runtime expense:**
- Two full Claude sessions (Worker + QA) per batch. For a 50-item task with batch size 5: 10 Worker sessions + 10 QA sessions + potential correction sessions.
- `PABLOV_STRICT=false` by default — meaning if the programmatic handoff fails, the batch continues anyway. The rigor is therefore partially opt-in. `ib_agent_core.md:926`
- Synthesizing a `programmatic_handoff` from conversation mining is expensive (grep over JSONL, jq transforms). This is the fallback path, not the exception.

**Maintenance burden:**
- Every new task type requires a template. The "CATASTROPHIC FAILURE WARNING" for missing templates indicates template compliance is fragile and high-friction. `ib_agent_core.md:401-413`

---

## 3. Execution Model

The PABLOV execution model is **sequential batch processing with dual-agent loops**:

1. Orchestrator creates `taskspec` with checklist items
2. Orchestrator generates `expected_set` (batch of N items from unchecked items)
3. Worker agent executes items one-at-a-time, marks `[x]`, writes `worker_handoff`
4. DNSP ensures `worker_handoff` exists (detect → nudge → synthesize)
5. QA agent validates `worker_handoff` against filesystem, writes `qa_report`
6. If QA fails: items unmarked, Worker receives `qa_report`, correction loop begins
7. After QA pass: next batch created, cycle repeats

**Quality enforcement**: Enforced at the artifact level (does the artifact exist? does the content match?) not at the intent level. This is a key design choice — programmatic over qualitative.

**Extension points**:
- `PABLOV_STRICT` flag: makes programmatic handoff failure fatal
- `PABLOV_INCLUDE_DIFF`: adds git diffs to evidence
- `PABLOV_FS_FILTER_BY_EVIDENCE`: filters filesystem changes by conversation evidence
- `AGENT_PROMPT_OVERRIDE`: substitutes custom agent prompts
- Task `assigned_to` field: auto-detects agent-specific prompts

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The artifact-chain principle (claim → proof separation) is directly adoptable. The `worker_handoff` (claim) vs `programmatic_handoff` (filesystem proof) distinction is a pattern SuperClaude can adopt without the full machinery.
- The five-step READ-before-EXECUTE enforcement is directly adoptable as a behavioral rule.
- DNSP "never wedge" principle: always produce an artifact even if synthesized. Adoptable as a fallback guarantee.

**Conditionally Adoptable:**
- The dual Worker+QA loop is conditionally adoptable. The verification separation is sound, but the cost (two full sessions per batch) is high. A lighter verification pass (single session with self-check) would capture most of the value.
- Agent Contracts (explicit output requirements per role) are adoptable in lighter form as structured delegation prompts.

**Reject:**
- The mandatory template pre-read checklist (catastrophic failure warning for every file write) is too high-friction for general use.
- Sequential-only execution (explicit prohibition on parallel item execution) should be rejected; SuperClaude's parallel-first doctrine is more appropriate for independent items.
- The full five-artifact chain is too heavy for single-session or lightweight tasks.
