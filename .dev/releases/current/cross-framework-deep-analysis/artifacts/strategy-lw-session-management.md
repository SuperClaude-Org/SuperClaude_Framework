# Strategy: LW Component — Session Management

**Component**: Session Management
**Source**: `.gfdoc/scripts/session_message_counter.sh` + `.gfdoc/scripts/rollover_context_functions.sh`
**Path Verified**: true (both paths)
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

Session management in llm-workflows is a proactive, dual-threshold system that prevents context overflow before it causes "Prompt is too long" failures, while preserving work-in-progress context across session boundaries.

**Core rigor mechanisms:**

- **Dual-threshold detection**: Session rollover triggered by EITHER message count (default 375, 87.5% of limit) OR token count (default 175,000, 87.5% of 200k). Using both prevents scenarios where few long messages exhaust tokens before the message count threshold triggers. `session_message_counter.sh:113-147`
- **Proactive vs. reactive rollover**: Rollover is checked BEFORE attempting `--resume`, not after failure. This eliminates "Prompt is too long" errors and context loss mid-batch. `session_message_counter.sh:114-116 comment`
- **Calibrated token estimation**: Python-based token counting with empirical constant `CHARS_PER_TOKEN = 2.8` (calibrated for technical content with code/paths/JSON). "Using 2.8 to be slightly conservative." `session_message_counter.sh:103-108`
- **Context injection on rollover**: When rolling to new session, `generate_rollover_context()` creates a structured summary (batch state, completed items count, current role, workspace paths) that is prepended to the new session's prompt. `rollover_context_functions.sh:37-55`
- **Three rollover scenarios handled**: Proactive (threshold exceeded), emergency (context overflow error during execution), dead session recovery (session file exists but session is dead). `rigorflow_workflow_deep_dive_guide.md:622-630`
- **State file persistence**: Session IDs stored in `WORKER_SESSION_FILE`; removed on rollover to force new session creation. Prevents stale session resume. `session_message_counter.sh:170-171`

**Rigor verdict**: The proactive dual-threshold approach is more rigorous than reactive rollover. Detecting overflow before it happens prevents data loss. The context injection mechanism ensures the new session is not starting blind.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- Token estimation requires spawning a Python subprocess (via `estimate_session_tokens()`) for every pre-resume check. This is a non-trivial overhead for what is essentially a counting operation. `session_message_counter.sh:33-110`
- Two separate script files for session management, with some logic duplicated in the main orchestrator (inline rollover at `automated_qa_workflow.sh:4252-4297`). Architecture is split across three files.
- The `run_worker_with_message_check()` wrapper and `run_worker_with_rollover()` in `rollover_context_functions.sh` appear to be incomplete integrations (integration example code, not production paths). Actual rollover is handled inline in `automated_qa_workflow.sh`.

**Operational drag:**
- Pre-resume session checks add a Python spawn + JSONL file read to every Worker invocation. For large tasks with many short batches, this overhead accumulates.
- The rollover context generation reads task file, counts completed items, queries batch state — multiple filesystem operations added to every rollover.

**Token/runtime expense:**
- The `generate_rollover_context()` function produces a structured context block that is prepended to the new session prompt. This context itself consumes tokens in the new session. For a long task, rollover contexts can chain.
- Emergency rollover (from "Prompt is too long" error) requires retrying the same batch with a new session — doubling the cost of that batch.

**Maintenance burden:**
- The `CHARS_PER_TOKEN = 2.8` constant requires re-calibration as content types change. The script comments note this was "tested" — but there is no automated test to detect drift.
- The rollover functions in `rollover_context_functions.sh` contain integration examples that appear aspirational rather than production-ready, creating confusion about what is actually used.

---

## 3. Execution Model

Session management operates as a **pre-invocation health check** with an **automatic migration path**:

1. Before each Worker (or QA) resume: read session file, check if session exists
2. If session exists: call `check_session_needs_rollover()` → count messages + estimate tokens
3. If rollover needed: generate context → clear session file → new session will be created
4. Worker invocation: if no session ID → create new session with rollover context prepended; if session ID → `--resume`
5. If context overflow error mid-execution: roll to new session without `--resume`, retry same batch

**Quality enforcement**: Session management is a reliability mechanism, not a quality enforcement mechanism. It prevents pipeline failures due to context limits, but does not verify output quality.

**Extension points**:
- `MAX_MESSAGES_PER_SESSION` and `MAX_TOKENS_PER_SESSION`: configurable thresholds
- Context generation is customizable — `generate_rollover_context()` can be modified to include additional state
- Three rollover scenarios are independent and can be handled differently per context

---

## 4. Pattern Categorization

**Directly Adoptable:**
- The dual-threshold proactive rollover principle (check BEFORE resume, not after failure) is directly adoptable for SuperClaude's sprint CLI long-running pipelines.
- The calibrated 87.5% threshold (not 100%) with a safety buffer is directly adoptable as a general context management principle.
- Context injection on rollover (generate structured summary → prepend to new session prompt) is directly adoptable.

**Conditionally Adoptable:**
- The Python-based token estimation is conditionally adoptable. The approach is sound; a more efficient implementation using native token counting APIs would be preferred.
- The state file-based session ID persistence (`WORKER_SESSION_FILE`) is conditionally adoptable for SuperClaude's sprint runner state management.

**Reject:**
- The bash-based implementation with Python subprocesses for counting. Should be reimplemented in the sprint runner language.
- The `rollover_context_functions.sh` integration example functions — they duplicate logic from the main orchestrator and create confusion about the actual production code path.
