# D-0002: Structural Decisions -- SIGINT, Hash, Step Wiring

## Overview

Three structural decisions locked for v2.22 implementation phases. Each decision cites codebase evidence from the T01.01 pipeline foundation review.

---

## Decision 1: SIGINT Strategy During Remediation Agents

### Question (OQ-001)
Does `ClaudeProcess` require additional signal-forwarding code for remediation agent cleanup, or does snapshot-based manual recovery (`.pre-remediate` files) suffice?

### Decision
**Snapshot-based manual recovery suffices. No additional signal-forwarding code is required.**

### Evidence

1. **ClaudeProcess already handles SIGINT/SIGTERM robustly** (`pipeline/process.py:143-184`):
   - `terminate()` implements graceful shutdown: SIGTERM -> wait 10s -> SIGKILL
   - Uses process groups (`os.setpgrp` at line 114, `os.killpg` at lines 156, 169) to kill the entire child tree
   - Handles `ProcessLookupError` gracefully (lines 160-162, 174)
   - File handles are always closed via `_close_handles()` (lines 146-147, 183-184)

2. **Roadmap executor already polls for cancellation** (`roadmap/executor.py:206-218`):
   - `roadmap_run_step()` polls `cancel_check()` every 1 second during subprocess execution
   - On cancel: calls `proc.terminate()` and returns `StepStatus.CANCELLED`
   - This pattern is directly reusable for remediation agents

3. **Pipeline executor supports cross-cancellation** (`pipeline/executor.py:264-274`):
   - Parallel step groups use `threading.Event` for cross-cancellation
   - If any parallel step fails, remaining steps are cancelled
   - This handles the multi-agent remediation case natively

4. **Snapshot-based recovery adds defense-in-depth**:
   - `.pre-remediate` file copies provide recovery even if process cleanup somehow fails
   - This is a manual recovery path (user inspects and restores), not an automated rollback
   - The combination of ClaudeProcess signal handling + snapshot files covers both automated and manual recovery

### Risk Assessment
- **ClaudeProcess signal handling is well-tested** in the existing pipeline (used by all 9 roadmap steps + validation steps)
- **No evidence of signal-forwarding gaps** in the codebase -- `os.killpg` kills the entire process group
- **Confidence**: 90% (raised from roadmap's 72% after validating actual ClaudeProcess behavior)

---

## Decision 2: Hash Algorithm -- SHA-256

### Question (OQ-002)
Which hash algorithm should be used for `source_report_hash` in the remediation state?

### Decision
**SHA-256, consistent with existing pipeline patterns. No conflicts detected.**

### Evidence

1. **SHA-256 is the established pattern** for content integrity in the pipeline:
   - `roadmap/executor.py:529`: `hashlib.sha256(config.spec_file.read_bytes()).hexdigest()` for spec file hash in state
   - `roadmap/executor.py:825`: Same pattern for resume stale-detection
   - `audit/tool_orchestrator.py:101`: `hashlib.sha256(content.encode("utf-8")).hexdigest()` for audit content deduplication

2. **No SHA-256 conflicts** exist in the codebase:
   - SHA-1 usage (`sprint/tmux.py:29`): only for short session naming hashes, non-security
   - MD5 usage (`execution/self_correction.py:292`): only for failure ID generation, non-security
   - Neither interferes with adopting SHA-256 for `source_report_hash`

3. **Consistency with existing state schema**:
   - `.roadmap-state.json` already stores `spec_hash` as a SHA-256 hexdigest
   - Using the same algorithm for `source_report_hash` maintains consistency

### Risk Assessment
- **Zero risk**: SHA-256 is already the standard; this decision simply extends the existing pattern
- **Confidence**: 98%

---

## Decision 3: Step Wiring -- Remediate via ClaudeProcess, Certify via execute_pipeline()

### Question (OQ-003)
Should `remediate` use `ClaudeProcess` directly or go through `execute_pipeline()`? What about `certify`?

### Decision
**Remediate uses `ClaudeProcess` directly (like `validate_run_step`). Certify uses `execute_pipeline()` (like standard roadmap steps).**

### Evidence

1. **Precedent: `validate_run_step` uses ClaudeProcess directly** (`validate_executor.py:77-173`):
   - `validate_run_step()` builds its own ClaudeProcess, manages lifecycle, and returns StepResult
   - The validate executor then passes this as the StepRunner to `execute_pipeline()`
   - This two-tier pattern is the established approach: custom ClaudeProcess management wrapped in a StepRunner

2. **Remediate needs direct ClaudeProcess control** because:
   - Remediation agents operate on specific file batches, requiring per-finding prompt construction
   - Each agent needs unique input context (finding details, file contents, fix guidance)
   - The `validate_executor.py` multi-agent pattern (parallel ClaudeProcess instances) is the exact precedent

3. **Certify fits the standard pipeline pattern** because:
   - Certification is a single-pass operation: read remediated files + findings, produce a pass/fail report
   - It follows the same shape as existing steps (prompt + inputs -> output + gate check)
   - Using `execute_pipeline()` gives automatic retry, gate checking, and state management

4. **Wiring implementation pattern**:
   - Create `remediate_executor.py` with `remediate_run_step()` (ClaudeProcess, like `validate_run_step`)
   - Create `certify_executor.py` or add certify steps to `_build_steps()` (execute_pipeline, like standard steps)
   - Wire both into `execute_roadmap()` as post-validation phases

### Risk Assessment
- **Low risk**: Both patterns are already proven in the codebase
- **Confidence**: 95%

---

## Summary

| Decision | Resolution | Confidence | Evidence Source |
|----------|-----------|------------|-----------------|
| OQ-001: SIGINT | Snapshot + existing ClaudeProcess signal handling | 90% | `process.py:143-184`, `executor.py:206-218` |
| OQ-002: Hash | SHA-256 (consistent with existing) | 98% | `executor.py:529`, `tool_orchestrator.py:101` |
| OQ-003: Step Wiring | remediate=ClaudeProcess, certify=execute_pipeline | 95% | `validate_executor.py:77-173`, `executor.py:293-392` |

All three decisions are validated against codebase evidence and locked for Phase 2 implementation.
