# PRD: Sprint Executor Context Exhaustion Resilience

**Version**: 1.0
**Date**: 2026-03-15
**Status**: Draft
**Author**: Synthesized from 3 brainstorm analyses + 3 adversarial debates (88-94% convergence)
**Sprint Target**: v2.25.2

---

## 1. Problem Statement

The `superclaude sprint run` executor crashes when a Claude subprocess exhausts its context window (200K tokens for Sonnet). The API returns `"Prompt is too long"` with exit code 1. The executor classifies this as a generic `PhaseStatus.ERROR` and halts the entire sprint -- even when the phase's implementation work completed successfully.

**Observed incident**: CLI Portify sprint, Phase 2 (7 tasks, 192 tests passing). The subprocess completed all implementation tasks and wrote all artifact specs. It crashed at turn 106 while writing the final completion report. Sprint cost at crash: $24.96.

**Root cause chain**:
1. Single-subprocess model conflates implementation and documentation into one session
2. No detection of context exhaustion errors (only `error_max_turns` is detected)
3. Full tasklist-index.md (~14K tokens) may be loaded unnecessarily per phase
4. `_determine_phase_status()` treats all `exit_code != 0` as `ERROR` with no recovery path

---

## 2. Solution Architecture

Three changes implemented together provide defense in depth:

| # | Change | Category | Effort | Impact |
|---|--------|----------|--------|--------|
| S1 | Executor writes `phase-N-result.md` from `AggregatedPhaseReport` | Quick win | XS (~15 lines) | Prevents the observed crash entirely |
| S2 | Detect "Prompt is too long" in output; recover completed phases | Detection & Recovery | S (~160 lines) | Graceful handling of all context exhaustion events |
| S3 | Phase-specific directory isolation + summary header | Prevention | S (~30 lines) | Saves ~14K tokens/phase static overhead |

**Deferred** (design only, implement on recurrence):

| # | Change | Category | Trigger |
|---|--------|----------|---------|
| S4 | Post-phase artifact writer subprocess | Architecture | Second context exhaustion occurrence OR >8 deliverables/phase |

---

## 3. Detailed Requirements

### 3.1 S1: Executor-Written Result File

**Rationale**: The crash occurred while the agent wrote `phase-2-result.md`. The executor already has `AggregatedPhaseReport.to_markdown()` which produces an equivalent report deterministically, without consuming agent context.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| S1-R01 | After phase subprocess exits, the executor writes `phase-N-result.md` from `AggregatedPhaseReport.to_markdown()` to `config.result_file(phase)` | P0 |
| S1-R02 | The executor-written result file includes `EXIT_RECOMMENDATION: CONTINUE` when all tasks passed, `EXIT_RECOMMENDATION: HALT` when any task failed | P0 |
| S1-R03 | The executor-written result file is written BEFORE `_determine_phase_status()` is called | P0 |
| S1-R04 | The agent's prompt no longer instructs the agent to write the completion report (remove from `build_prompt()`) | P1 |

**Files to modify**:
- `src/superclaude/cli/sprint/executor.py` — write result file after phase completion (insert at ~line 694)
- `src/superclaude/cli/sprint/process.py` — remove completion report instruction from `build_prompt()`

**Convergence**: 100% (unanimous across all 3 debates)

---

### 3.2 S2: Context Exhaustion Detection & Recovery

**Rationale**: When context exhaustion occurs, the executor should distinguish it from generic errors and recover completed phases instead of halting.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| S2-R01 | Add `detect_prompt_too_long(output_path: Path) -> bool` to `monitor.py`, following the `detect_error_max_turns()` architecture | P0 |
| S2-R02 | Pattern: `r'"Prompt is too long"'` matched against last 10 non-empty lines of NDJSON output | P0 |
| S2-R03 | Add `PhaseStatus.PASS_RECOVERED` enum value with `is_terminal=True`, `is_success=True`, `is_failure=False` | P0 |
| S2-R04 | Restructure `_determine_phase_status()`: when `exit_code != 0` and prompt-too-long detected, classify via result file (PASS_RECOVERED if CONTINUE, HALT if HALT, INCOMPLETE if no result file) | P0 |
| S2-R05 | Extract result file parsing into `_classify_from_result_file(result_file, *, recovered=False)` helper for explicit dual-path control flow | P0 |
| S2-R06 | Validate result file `mtime > phase_started_at` before trusting it in the context exhaustion path (prevents stale file from previous runs) | P0 |
| S2-R07 | Add `FailureCategory.CONTEXT_EXHAUSTION` to `diagnostics.py` for diagnostic report classification | P1 |
| S2-R08 | Also scan `config.error_file(phase)` (stderr) for the pattern as defense-in-depth | P1 |
| S2-R09 | Add `started_at: float` parameter to `_determine_phase_status()` signature | P0 |

**Files to modify**:
- `src/superclaude/cli/sprint/monitor.py` — add `detect_prompt_too_long()`
- `src/superclaude/cli/sprint/executor.py` — restructure `_determine_phase_status()`, add `_classify_from_result_file()`, pass `started_at`
- `src/superclaude/cli/sprint/models.py` — add `PASS_RECOVERED` to `PhaseStatus`
- `src/superclaude/cli/sprint/diagnostics.py` — add `CONTEXT_EXHAUSTION` to `FailureCategory`

**Convergence**: 88% (debate refined original Approach B with 3 mandatory modifications: PASS_RECOVERED status, explicit control flow, timestamp validation)

**Key design decisions from debate**:
- Use `PASS_RECOVERED` (not raw `PASS`) to preserve diagnostic visibility while allowing sprint continuation
- Do NOT add `PhaseStatus.CONTEXT_EXHAUSTED` — the diagnostic layer (`FailureCategory`) carries root cause specificity
- Reuse `INCOMPLETE` for the no-result-file case (correct `is_failure` semantics)
- Per-task subprocess context exhaustion detection is deferred (lower priority, rarer occurrence)

---

### 3.3 S3: Phase-Specific Directory Isolation + Summary Header

**Rationale**: The `tasklist-index.md` (~14K tokens) may be loaded by the subprocess agent or by Claude Code's `@` file resolution. Eliminating it from the working directory prevents this overhead.

**Requirements**:

| ID | Requirement | Priority |
|----|-------------|----------|
| S3-R01 | Before spawning phase subprocess, copy only the phase file to an isolated directory under `config.results_dir/.isolation/phase-{N}/` | P0 |
| S3-R02 | Set `scoped_work_dir` for the subprocess to the isolated directory instead of `config.release_dir` | P0 |
| S3-R03 | Clean up isolated directory in the `finally` block of the phase execution loop | P0 |
| S3-R04 | On sprint startup, clean up any orphaned `.isolation/` directories from prior crashed runs | P1 |
| S3-R05 | Add a sprint summary header (~200 tokens) to `build_prompt()` containing: sprint name, phase number/total, artifact root path, results dir, execution log path, and prior-phase artifact directories | P0 |
| S3-R06 | Add explicit instruction in prompt: "All task details are in the phase file. Do not seek additional index files." | P1 |

**Files to modify**:
- `src/superclaude/cli/sprint/executor.py` — add isolation directory lifecycle (create, scope, cleanup)
- `src/superclaude/cli/sprint/process.py` — add summary header to `build_prompt()`

**Convergence**: 94% (debate promoted directory isolation from optional to mandatory; added prior-phase artifact paths to header; added empirical validation as pre-merge requirement)

**Pre-merge validation requirement**: Measure context consumption for at least one phase execution with and without the index accessible. If delta is <5K tokens, the index was likely never loaded and savings are lower than projected (~14K upper bound).

---

### 3.4 S4: Artifact Batching Architecture (Design Only)

**Rationale**: The single-subprocess model will hit context limits again as sprint complexity grows. Separating implementation from documentation is the correct long-term architecture.

**Requirements** (design spec only — no implementation):

| ID | Requirement | Priority |
|----|-------------|----------|
| S4-R01 | Write architecture spec for `ArtifactWriterProcess` class with `build_artifact_prompt()` method | P2 |
| S4-R02 | Design `PhaseResult` extension with `impl_status` and `artifacts_status` fields | P2 |
| S4-R03 | Design `SprintConfig.artifact_mode` field and `--artifact-mode inline\|deferred\|none` CLI flag | P2 |
| S4-R04 | Design manifest capture (lightweight YAML per task: task_id, status, key_decision) for decision record preservation | P2 |
| S4-R05 | Define implementation trigger: second context exhaustion occurrence OR phase spec with >8 deliverables OR `(artifact_count * 1500) > remaining_budget * 0.5` | P2 |

**Output**: Architecture spec document at `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/artifact-batching-architecture-spec.md`

**Convergence**: 82.5% (debate agreed on design-now-defer-implementation; contested default mode and quality gap magnitude)

---

## 4. Implementation Sequence

```
Phase 1 — Immediate (this sprint):
  [1] S1: Executor writes phase-N-result.md         (XS, ~15 lines)
  [2] S2: Context exhaustion detection + recovery    (S, ~160 lines)
  [3] S3: Directory isolation + summary header       (S, ~30 lines)

Phase 2 — Design only:
  [4] S4: Architecture spec for artifact batching    (document only)

Phase 3 — Triggered by recurrence:
  [5] S4: Full artifact batching implementation
```

**Total implementation effort (Phase 1)**: ~205 lines of production code + ~120 lines of tests

---

## 5. Test Requirements

### S1 Tests
| Test | Type |
|------|------|
| Executor writes result file with CONTINUE when all tasks pass | Unit |
| Executor writes result file with HALT when any task fails | Unit |
| Result file is written before `_determine_phase_status()` is called | Integration |

### S2 Tests
| Test | Type |
|------|------|
| `detect_prompt_too_long()` matches pattern in last 10 lines | Unit |
| `detect_prompt_too_long()` returns False on clean output | Unit |
| `detect_prompt_too_long()` returns False when pattern in middle of file (not tail) | Unit |
| `_determine_phase_status()`: exit=1 + prompt-too-long + result with CONTINUE → PASS_RECOVERED | Unit |
| `_determine_phase_status()`: exit=1 + prompt-too-long + result with HALT → HALT | Unit |
| `_determine_phase_status()`: exit=1 + prompt-too-long + no result → INCOMPLETE | Unit |
| `_determine_phase_status()`: exit=1 + prompt-too-long + stale result (old mtime) → INCOMPLETE | Unit |
| `_determine_phase_status()`: exit=1 + no prompt-too-long → ERROR (unchanged) | Unit |
| `PhaseStatus.PASS_RECOVERED.is_success` returns True | Unit |
| `PhaseStatus.PASS_RECOVERED.is_failure` returns False | Unit |
| Sprint continues to next phase on PASS_RECOVERED | Integration |

### S3 Tests
| Test | Type |
|------|------|
| Isolation directory created before subprocess spawn | Unit |
| Isolation directory contains only the phase file | Unit |
| Isolation directory cleaned up after phase completes | Unit |
| Isolation directory cleaned up after phase fails | Unit |
| Orphaned isolation directories cleaned on sprint startup | Unit |
| Summary header included in prompt with correct metadata | Unit |

---

## 6. Risk Register

| Risk | Severity | Probability | Mitigation | Owner |
|------|----------|-------------|------------|-------|
| Stale result file from previous run misclassified as PASS | High | Low | Timestamp validation (S2-R06) | S2 |
| Index never actually loaded (S3 savings = 0) | Medium | Medium | Empirical validation pre-merge | S3 |
| `@` file resolution loads index despite isolation | Medium | Low | Directory isolation (S3-R01/R02) | S3 |
| Agent ignores "do not read index" instruction | Low | Medium | Directory isolation makes instruction redundant | S3 |
| False positive on "Prompt is too long" pattern | Low | Very Low | Last-10-lines constraint + exit_code!=0 precondition | S2 |
| Orphaned temp directories on executor crash | Very Low | Low | Startup cleanup (S3-R04) | S3 |
| API changes "Prompt is too long" error message | Low | Low | Single-line regex constant update | S2 |

---

## 7. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| SC-01 | Sprint does not halt on context exhaustion when phase work completed (PASS_RECOVERED) |
| SC-02 | Sprint correctly halts on context exhaustion when phase work is incomplete (INCOMPLETE) |
| SC-03 | Sprint correctly halts on genuine errors unrelated to context (ERROR unchanged) |
| SC-04 | Execution log distinguishes PASS_RECOVERED from clean PASS |
| SC-05 | Diagnostic report shows `CONTEXT_EXHAUSTION` category (not CRASH or ERROR) |
| SC-06 | Phase subprocess working directory does not contain tasklist-index.md |
| SC-07 | All existing sprint tests continue to pass (no regressions) |
| SC-08 | `uv run pytest tests/sprint/` passes with ≥95% coverage on modified files |

---

## 8. Appendix: Source Documents

| Document | Path |
|----------|------|
| Solution #2 Brainstorm | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/sprint-context-exhaustion-solution2-brainstorm.md` |
| Solution #3 Brainstorm | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/solution-3-split-phase-prompts-brainstorm.md` |
| Solution #4 Brainstorm | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/solution-4-artifact-batching-brainstorm.md` |
| Solution #2 Adversarial Debate | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/adversarial-solution2-debate.md` |
| Solution #3 Adversarial Debate | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/adversarial-solution3-debate.md` |
| Solution #4 Adversarial Debate | `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/adversarial-solution4-debate.md` |

---

## 9. Debate Convergence Summary

| Solution | Brainstorm Recommendation | Debate Refinements | Final Convergence |
|----------|--------------------------|--------------------|--------------------|
| S2: Detection | Approach B (pattern match + result file fallthrough) | +PASS_RECOVERED status, +explicit control flow helper, +timestamp validation | 88% |
| S3: Prompt reduction | Approach D (summary header) with A3 optional | A3 promoted to mandatory, +prior-phase artifact paths, +empirical validation gate | 94% |
| S4: Artifact batching | Hybrid A+D+E (post-phase writer + reduced verbosity + config) | Downscoped to design-only; quick win (executor writes result) extracted as standalone; defer full implementation | 82.5% |

**Cross-solution consensus**: All 3 debates independently concluded that the executor writing `phase-N-result.md` from `AggregatedPhaseReport.to_markdown()` is the highest-priority change. All 3 debates agreed that Solutions #2 and #3 are complementary hardening measures that should be implemented together.
