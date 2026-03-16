# Strategy: LW Component — Automated QA Workflow

**Component**: Automated QA Workflow
**Source**: `.gfdoc/scripts/automated_qa_workflow.sh`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The automated QA workflow is a 6000+ line bash orchestrator that implements the PABLOV methodology programmatically. Its rigor comes from deterministic state management and fail-closed verification.

**Core rigor mechanisms:**

- **Batch state machine**: Every batch progresses through immutable states (`initialized`, `worker_in_progress`, `worker_complete`, `qa_in_progress`, `qa_complete`). State transitions are logged and persisted in `batch_N_state.json`. `automated_qa_workflow.sh:4972-5322`
- **Batch immutability**: Batch numbers are permanent identifiers — Batch 5 always means the same items, regardless of task file changes. This prevents batch identity corruption and ensures QA feedback always references the correct items. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1624`
- **UID-based item tracking**: Batch items are augmented with UIDs for stable cross-session tracking. `automated_qa_workflow.sh:4391`
- **Fail-closed PASS/FAIL verdict**: The verdict logic explicitly checks taskspec completion AND programmatic handoff counts; a mismatch forces FAIL. `automated_qa_workflow.sh:3129-3132`
- **Batch overrun detection**: Detects when Worker completes unauthorized items beyond `expected_set`. Quarantines overrun handoffs. `automated_qa_workflow.sh:5302-5303`
- **Session event logging**: Every significant action logged with role, session ID, batch number, and reason. Full audit trail.
- **Three prompt modes**: `normal` (fresh batch), `incomplete` (resume interrupted), `correction` (QA failed). Mode selection preserves batch composition in correction/incomplete scenarios. `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:797-828`

**Rigor verdict**: The batch state machine and immutability contract are the strongest elements. The determinism of the orchestrator means failures are reproducible and debuggable, not random.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- 6000+ lines of bash is a significant maintenance burden. The complexity is partially justified but creates fragility: multiple backup files exist (`automated_qa_workflow_backup_*.sh`), suggesting the script is difficult to modify safely.
- The Python isolated parser (`parse_checklist.py`) called from bash, with sterile environment isolation, adds spawning overhead for each batch. `automated_qa_workflow.sh:792-798`
- Multiple fallback paths for UID matching (exact match → multiset → Python anchor-based fallback) add complexity and failure modes. `automated_qa_workflow.sh:2121-2153`

**Operational drag:**
- Two Claude CLI invocations per batch (Worker + QA), each with full context loading. For large tasks this compounds significantly.
- Session rollover handling (proactive + emergency + dead session recovery) adds branching complexity to every Worker invocation. `automated_qa_workflow.sh:4252-4297`
- The exponential backoff wait for worker_handoff file (up to 6 attempts) adds latency even in the success path. `automated_qa_workflow.sh:5427-5431`

**Token/runtime expense:**
- Each batch incurs: Worker session creation/resume + QA session creation + optional nudge sessions + programmatic handoff generation. The minimum per-batch cost is high.
- The verbose JSON output capture (`capture_json_with_verbose`) stores full conversation JSON for every batch. Disk I/O and parsing cost accumulates.

**Maintenance burden:**
- Multiple backup versions suggest the script has been iteratively patched rather than refactored. The presence of `automated_qa_workflow_backup_20250823_325p.sh`, `_20251018_157p.sh`, `_20251022_828a.sh`, `_20251031_505p.sh` as active tracked files is a code health warning.
- Bash is not well-suited to complex state management. jq-heavy JSON manipulation in bash is fragile.

---

## 3. Execution Model

The workflow is an **infinite-loop batch orchestrator**:

1. Parse task checklist state from MDTM task file
2. Identify current batch (new, incomplete, or correction mode)
3. Check session context thresholds (proactive rollover if needed)
4. Spawn Worker with batch prompt → await worker_handoff
5. Run DNSP if handoff missing (detect → nudge → synthesize)
6. Detect/correct batch overrun
7. Generate `programmatic_handoff` from PABLOV evidence
8. Spawn QA with handoff → await qa_report
9. If PASS: advance to next batch; if FAIL: enter correction mode
10. Repeat until all checklist items complete or MAX_ITERATIONS reached

**Quality enforcement**: Automated and programmatic. QA verdict is computed by comparing taskspec checkmarks against programmatic handoff counts — not by asking QA "did it pass?".

**Extension points**:
- `MAX_NUDGE_WORKER`, `MAX_NUDGE_QA`, `MAX_CORRECTION_ATTEMPTS`: all configurable
- `PABLOV_STRICT`, `PABLOV_INCLUDE_DIFF`, `PABLOV_FS_FILTER_BY_EVIDENCE`: tunable
- `AGENT_PROMPT_OVERRIDE`: swap agent prompts
- Batch size configurable mid-task

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The batch state machine pattern (explicit state transitions, persisted state) is directly adoptable for long-running SuperClaude sprint executions.
- The three-mode prompt selection (normal/incomplete/correction) maps well to SuperClaude's sprint runner scenarios.
- Fail-closed verdict logic (mismatch between claim and proof = FAIL) is a directly adoptable quality principle.

**Conditionally Adoptable:**
- The overall orchestration loop is conditionally adoptable in a Python or TypeScript implementation, not as bash. The logic is sound; the implementation language is inappropriate for maintainability.
- DNSP recovery as an automated mechanism is conditionally adoptable — the principle (never wedge; synthesize if nudge fails) is valuable but the full bash implementation is too heavy.

**Reject:**
- The 6000-line bash script as a delivery vehicle. The logic should be rewritten in a higher-level language if adopted.
- The multiple backup file pattern as a versioning strategy.
- The Python subprocess isolation for checklist parsing — this is a workaround for bash limitations.
