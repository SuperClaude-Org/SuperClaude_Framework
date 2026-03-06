<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant 1 (merged-decision.md) -->
<!-- Merge date: 2026-03-05 -->

---
title: "Pipeline Architecture Decision: Should Sprint Adopt execute_pipeline()?"
authors:
  - analysis-agent-alpha (pro-unification)
  - analysis-agent-beta (skeptical-counterargument)
scope: src/superclaude/cli/{pipeline,sprint,roadmap}/
analysis_type: adversarial-merged-architectural-decision
convergence: 0.72
base_variant: Variant 1 (merged-decision.md)
status: merged
---

# Pipeline Architecture Decision: Sprint and execute_pipeline()

<!-- Source: Base (original, modified) — framing updated to reflect debate conclusions -->

This document presents the adversarial-debated analysis of whether sprint should be refactored to use `execute_pipeline()`. It originated from two competing positions — a pro-unification proposal and a skeptical counterargument — subjected to 3 rounds of structured adversarial debate. The debate settled several empirical questions and produced a three-option recommendation.

## Current Architecture: Evidence Summary

<!-- Source: Base (original) -->

The following facts are established by code evidence and confirmed by both advocates:

1. **Pipeline was extracted from sprint.** `pipeline/process.py`, line 3: "Extracted from sprint/process.py." Commit `6548f17` atomically created `pipeline/`, created `roadmap/`, and reparented sprint's models and process classes to inherit from pipeline base types.

2. **Sprint already depends on pipeline at the type and process level.** `sprint/models.py` imports `PipelineConfig`, `Step`, `StepResult`, `StepStatus` from pipeline. `sprint/process.py` inherits from `pipeline.process.ClaudeProcess`. The extraction is 2/3 complete (models + process), with the executor as the remaining boundary.

3. **Sprint does NOT use the pipeline executor.** `execute_pipeline` has zero import sites in `src/superclaude/cli/sprint/`. Sprint has its own 273-line `execute_sprint()` function.

4. **Roadmap cleanly uses the pipeline.** `roadmap/executor.py` delegates to `execute_pipeline()` with `roadmap_run_step` as the StepRunner.

5. **NFR-007 proves generic-infrastructure intent.** Every pipeline module contains "No imports from superclaude.cli.sprint or superclaude.cli.roadmap" — a deliberate dependency inversion rule.

6. **Dead code exists.** `roadmap/executor.py:53-76` defines `_build_subprocess_argv()` which is never called from production code.

7. **Process method overrides are near-identical.** `sprint/process.py` overrides `start()`, `wait()`, and `terminate()` with ~90 lines of code whose only difference from the base class is `debug_log()` calls.

## Challenge 1: Sprint and Roadmap Are Not the Same Execution Model

<!-- Source: Base (original) -->

Sprint and roadmap have fundamentally different execution paradigms that share surface-level vocabulary but differ in substance:

**Roadmap** is a stateless DAG of short-lived transformations:
- Each step produces a single output file from input files
- Steps are pure functions: input -> LLM -> output -> gate check
- No human interaction during execution
- Steps are independent — each runs in a fresh subprocess with no shared state
- Retry is simple: re-run the same step
- The entire pipeline takes 5-20 minutes

**Sprint** is a stateful, long-running process orchestrator:
- Each phase runs an LLM agent that modifies the actual codebase (file edits, test runs, git operations)
- Phases have side effects that accumulate — phase 3 depends on files changed by phase 2
- Real-time monitoring is critical (TUI, stall detection, tmux)
- Human operators need live observability during multi-hour runs
- "Retry" would mean re-running a phase that already modified files — semantically different from roadmap retry
- A sprint can run for hours across 5-10 phases

The callback interfaces needed to accommodate sprint's features would be so broad that `execute_pipeline()` becomes a god function, or sprint reimplements its own poll loop inside a callback, achieving indirection without simplification.

## Challenge 2: The Extraction Reached Its Natural Boundary

<!-- Source: Base (original, modified) — updated per Changes #1, #4, #5 to reflect debate evidence -->

### What the evidence shows

The extraction narrative is confirmed: pipeline WAS extracted from sprint (documented in `pipeline/process.py:3` and commit `6548f17`). The extraction proceeded bottom-up:

1. **Models extracted**: Sprint's `SprintConfig` inherits from `PipelineConfig`, `PhaseResult` inherits from `StepResult`
2. **Process extracted**: Sprint's `ClaudeProcess` inherits from pipeline's `ClaudeProcess`
3. **Executor NOT extracted**: Sprint's `execute_sprint()` remains independent

### Why the executor boundary is the correct stopping point

The models and process extractions succeeded because they have genuine semantic overlap:
- `PipelineConfig` fields (`work_dir`, `dry_run`, `max_turns`, `model`) are truly shared
- `ClaudeProcess` methods (`build_command`, `build_env`, `start`, `wait`, `terminate`) are truly shared

The executor extraction would NOT succeed the same way because orchestration semantics diverge:
- **Roadmap executor uses**: gates, retry, parallel dispatch, stateless callbacks
- **Sprint executor uses**: poll loop, TUI, monitor threads, watchdog/stall detection, signal handling, tmux, diagnostics, result-file status parsing

The overlap at the executor level is a for-loop over steps. The divergence is everything else.

## Challenge 3: The Callback Architecture Does Not Scale to Sprint's Needs

<!-- Source: Base (original) -->

Sprint's poll loop (`sprint/executor.py`, lines 94-171) interleaves concerns that operate **during step execution**, not before or after:

- TUI updates at 2 Hz with monitor state (output bytes, growth rate, stall seconds, last task ID, files changed)
- Watchdog stall timeout checks with potential process kill
- Signal handler checks with graceful termination
- Debug event logging with phase-specific context

These require concurrent access to:
- The running subprocess handle
- The monitor thread's state
- The signal handler's flag
- The config's stall timeout settings
- The ability to terminate the process mid-execution

The `StepRunner` Protocol signature is `(Step, PipelineConfig, cancel_check) -> StepResult`. A `sprint_run_step` implementation would need to capture `SprintConfig`, `SprintLogger`, `SprintTUI`, `OutputMonitor`, `SignalHandler`, and `DiagnosticCollector` — containing the entire poll loop as a 100-150 line closure. This relocates sprint's execution logic rather than eliminating it.

**Key question (settled by debate):** Can sprint's poll loop become a callback without becoming a nested poll loop? **Answer: No.** The poll loop would relocate into `sprint_run_step`. The "unification" eliminates 60-80 lines of step-sequencing boilerplate while adding a new abstraction layer.

## Challenge 4: Claimed Benefits Do Not Apply to Sprint

<!-- Source: Base (original, modified) — updated to reflect debate concessions -->

### "Bug fixes apply everywhere" — Partially true
Sprint would gain retry logic "for free" from `execute_pipeline()`. However, **sprint deliberately does NOT retry** failed phases because phases have side effects. A failed phase that modified 50 files cannot be blindly retried — the codebase is in an intermediate state. Sprint would set `retry_limit=0`, gaining infrastructure it opts out of. *(Debate outcome: Variant A conceded retry absence is correct-by-design.)*

### "New features compose — parallel phases" — Does not apply
Sprint phases are inherently sequential because phase N depends on the codebase state left by phase N-1. Running phases in parallel would produce data races on the working tree. *(Debate outcome: Variant A conceded this point in Round 1.)*

### "Testing surface shrinks" — Shifts, does not shrink
After refactoring, sprint would need: tests for the `sprint_run_step` closure, tests for TUI integration during step execution, tests for watchdog/stall detection, tests for signal handler interaction, and **new integration tests** verifying `sprint_run_step` correctly composes with `execute_pipeline`. Sprint currently has zero executor-level unit tests (a pre-existing gap), so any testing approach provides net improvement — but adoption of `execute_pipeline` is not required to close this gap.

### "The --file vs inline debate disappears" — True but trivially fixable
This is achievable without full unification. Fix the file-passing strategy in `ClaudeProcess.build_command()` — a small standalone change.

## Challenge 5: The Scope Estimate Is Large, Not Medium

<!-- Source: Base (original, modified) — updated to reflect debate consensus -->

Both advocates agreed in debate that the effort is **Large**:

The sprint executor manages 7 interleaved subsystems:
1. Subprocess lifecycle with SIGTERM/SIGKILL escalation
2. Monitor threads parsing NDJSON output
3. Monotonic timeouts immune to NTP adjustments
4. Watchdog stall detection with configurable actions
5. Tmux integration for detachable sessions
6. Diagnostic collection on failure with classification
7. Structured execution logs

Refactoring into callbacks requires designing interfaces, reimplementing the poll loop inside `sprint_run_step`, updating all tests, regression testing TUI/monitoring/tmux/diagnostic paths, and handling cross-callback edge cases.

*(Debate outcome: Variant A conceded Large effort in Rounds 1 and 2.)*

## What the Pro-Unification Proposal Still Contributes

<!-- Source: Variant 2 (merged-adversarial-analysis.md), Section 7 — incorporated per Change #2 -->

Even though immediate executor unification is not justified, the pro-unification analysis contributes a useful architectural direction:
- Generic process lifecycle hooks should live in the shared layer where possible
- Consumer-specific state persistence can share interface boundaries even if formats remain different
- Common sequencing/result abstractions should continue to converge when they reduce real duplication

This makes the right long-term conclusion **phased extraction**, not permanent architectural divergence. Executor unification should be treated as a hypothesis to validate with concrete designs, not a decision already earned by current evidence.

## Three Options: Decision Framework

<!-- Source: Base (original) -->

### Option 1: Full Unification (Original Variant A — NOT RECOMMENDED)

Refactor sprint to use `execute_pipeline()` completely, pushing all sprint features into callbacks.

| Metric | Assessment |
|--------|------------|
| Code reduction | ~60-80 lines eliminated from sprint |
| New code | ~100-150 line sprint_run_step closure + callback wiring |
| Net reduction | Approximately zero |
| Effort | Large |
| Risk | High (regression in production-critical path) |
| Benefits gained | Retry (not used), gates (incompatible), parallel (not applicable) |

**Rejected by debate:** Both advocates moved away from this by Round 3.

### Option 2: Partial Unification (Variant A Round 3 — CONDITIONAL)

Adopt `execute_pipeline()` for step sequencing only. Keep sprint_run_step as substantial closure. Add Phase 0 test audit prerequisite.

| Metric | Assessment |
|--------|------------|
| Code reduction | ~60-80 lines of orchestration boilerplate |
| New code | ~100 line sprint_run_step + Phase 0 test audit |
| Effort | Large (but phased: Phase 0 tests -> Phase 1 hooks -> Phase 2 extraction -> Phase 3 swap) |
| Risk | Medium (phased approach reduces blast radius) |
| Benefits gained | Tested step sequencing, halt-on-fail logic, state update hooks |
| Prerequisite | Sprint must have comprehensive executor tests BEFORE refactoring begins |

**Conditional recommendation:** Only pursue if sprint gains additional pipeline features (gates, new callback needs) that increase the semantic overlap. Currently, the overlap is too narrow to justify the effort.

### Option 3: Targeted Fixes (Variant B — RECOMMENDED)

<!-- Source: Base (original) -->

Fix the actual problems without restructuring sprint's execution model:

| Problem | Targeted Fix | Effort |
|---------|-------------|--------|
| Process method overrides (~90 lines duplication) | Add logging hooks to pipeline `ClaudeProcess` base class | Small |
| Dead `_build_subprocess_argv()` | Delete it | Trivial |
| --file broken in roadmap | Switch roadmap to inline file embedding in `roadmap_run_step()` | Small |
| Sprint has zero executor tests | Write characterization tests pinning current behavior | Medium |
| Two state management systems | Accept — they serve different domains with different semantics | None |
| Sprint doesn't use execute_pipeline() | Accept — sprint's execution model is legitimately different | None |

| Metric | Assessment |
|--------|------------|
| Code reduction | ~90 lines (process overrides) + dead code removal |
| New code | Logging hooks (~20 lines) + characterization tests (~200 lines) |
| Effort | Small to Medium |
| Risk | Minimal |
| All actual bugs fixed | Yes |

**Total effort: Small-Medium. Risk: Minimal. All real bugs addressed.**

## Summary: Questions Settled and Open

<!-- Source: Base (original, modified) — updated to reflect debate outcomes -->

| # | Question | Status | Answer |
|---|----------|--------|--------|
| 1 | Is sprint's poll loop expressible as callbacks without becoming a nested poll loop? | **SETTLED** | No. The poll loop relocates into sprint_run_step. Unification eliminates 60-80 lines of sequencing, not the 200+ lines of domain logic. |
| 2 | Was the pipeline module built for roadmap or extracted from sprint? | **SETTLED** | Extracted from sprint. Documented in code (pipeline/process.py:3), commit message (6548f17), and NFR-007. |
| 3 | What is the concrete signature of sprint_run_step? | **SETTLED** | `(Step, PipelineConfig, cancel_check) -> StepResult` per StepRunner Protocol. Would require closure capturing 5-6 stateful objects. |
| 4 | Can sprint phases ever be retried or parallelized? | **SETTLED** | No. Phases mutate the filesystem sequentially. Retry requires rollback infrastructure not proposed. |
| 5 | What is the actual regression risk in sprint? | **PARTIALLY OPEN** | Large effort with High regression risk. Sprint has zero executor tests today. Phase 0 test audit required before any refactoring. |
| 6 | Does the targeted fix approach miss any real bugs? | **SETTLED** | No. All identified bugs (process overrides, dead code, file-passing) are addressed by targeted fixes. |

## Recommendation

<!-- Source: Base (original, modified) — updated per Changes #1, #3 to incorporate phased framing and hypothesis language -->

**Proceed with Option 3 (Targeted Fixes).** This addresses every real bug at minimal risk. Document the architectural decision that executor-level unification was evaluated through adversarial debate and deferred pending increased semantic overlap between sprint and pipeline executor capabilities.

<!-- Source: Variant 2 (merged-adversarial-analysis.md), Final Verdict — incorporated per Change #3 -->
Executor unification should be treated as **a hypothesis to validate**, not a decision already earned by the current evidence. The targeted fixes represent Phase 1 of a longer extraction roadmap, not a terminal decision.

<!-- Source: Variant 2 (merged-adversarial-analysis.md), Recommended Plan — incorporated per Change #1 -->
**Phased extraction roadmap:**
- **Phase 1 (now)**: Execute Option 3 targeted fixes — logging hooks, dead code removal, file-passing fix, characterization tests
- **Phase 2 (when triggered)**: Extract narrower shared primitives — state/result normalization, shared cancellation/result interfaces — only where they reduce real duplication
- **Phase 3 (re-evaluate)**: Revisit executor unification with a concrete `sprint_run_step` design that answers: Does sprint still need its own poll loop? If yes, what complexity is actually removed?

**Revisit Option 2 (Partial Unification) if:**
- Sprint adopts gate-based validation (replacing result-file parsing)
- Sprint needs retry with rollback infrastructure
- A third consumer of `execute_pipeline()` is introduced, increasing the value of the shared executor
