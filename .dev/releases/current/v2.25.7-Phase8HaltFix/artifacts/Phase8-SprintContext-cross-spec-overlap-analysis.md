# Cross-Spec Overlap & Conflict Analysis

**Spec A**: [`config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/phase8-halt-fix.md`](../../config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/phase8-halt-fix.md) — Phase 8 Halt Fix
**Spec B**: [`config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/sprint-context-exhaustion-prd.md`](../../config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/sprint-context-exhaustion-prd.md) — Context Exhaustion PRD
**Subsystem**: `src/superclaude/cli/sprint/`
**Generated**: 2026-03-15
**Method**: Symbol-grounded analysis against current codebase state (commit `8b70fd5`)

---

## Current Codebase State (Baseline)

All line references are to the current state of the code on branch `v2.25-Roadmap-v5`.

### `src/superclaude/cli/sprint/models.py`

**[`PhaseStatus`](../../src/superclaude/cli/sprint/models.py) — lines 203–241**

```python
# models.py:204-216
class PhaseStatus(Enum):
    """Lifecycle of a single phase."""

    PENDING = "pending"       # :207
    RUNNING = "running"       # :208
    PASS = "pass"             # :209
    PASS_NO_SIGNAL = "pass_no_signal"   # :210
    PASS_NO_REPORT = "pass_no_report"   # :211
    INCOMPLETE = "incomplete" # :212
    HALT = "halt"             # :213
    TIMEOUT = "timeout"       # :214
    ERROR = "error"           # :215
    SKIPPED = "skipped"       # :216
```

```python
# models.py:218-228 — is_terminal includes PASS, PASS_NO_SIGNAL, PASS_NO_REPORT,
#   INCOMPLETE, HALT, TIMEOUT, ERROR, SKIPPED
# models.py:231-237 — is_success includes PASS, PASS_NO_SIGNAL, PASS_NO_REPORT
# models.py:239-241 — is_failure includes INCOMPLETE, HALT, TIMEOUT, ERROR
```

**Key observation**: No `PASS_WITH_WARNINGS` or `PASS_RECOVERED` exists today. Both specs propose adding one.

---

### `src/superclaude/cli/sprint/executor.py`

**[`_determine_phase_status()`](../../src/superclaude/cli/sprint/executor.py) — lines 764–814**

Current signature (line 764):
```python
def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
) -> PhaseStatus:
```

Critical early return (line 783):
```python
    if exit_code != 0:
        return PhaseStatus.ERROR    # <-- Both specs target this line
```

**Call site** in `execute_sprint()` (lines 658–663):
```python
            # executor.py:658-663
            # Determine phase status
            status = _determine_phase_status(
                exit_code=exit_code,
                result_file=config.result_file(phase),
                output_file=config.output_file(phase),
            )
```

Note: `started_at` is captured at line 543 (`started_at = datetime.now(timezone.utc)`) but is **not passed** to `_determine_phase_status`.

**[`AggregatedPhaseReport`](../../src/superclaude/cli/sprint/executor.py) — lines 178–281**

Already exists with `to_markdown()` (lines 243–281) that produces `EXIT_RECOMMENDATION: CONTINUE` or `EXIT_RECOMMENDATION: HALT` based on `self.status`. **Currently never written to disk** — only used for YAML logging.

**[`aggregate_task_results()`](../../src/superclaude/cli/sprint/executor.py) — lines 285–330**

Constructs `AggregatedPhaseReport` from `TaskResult` list. Already called in the execution loop but its output is not persisted to the result file path.

**[`execute_sprint()`](../../src/superclaude/cli/sprint/executor.py) — lines 489–761**

Phase loop structure:
- Line 541: `proc_manager = ClaudeProcess(config, phase)` — subprocess launch
- Line 543: `started_at = datetime.now(timezone.utc)` — timestamp captured
- Lines 557–625: Poll loop (wait for process exit)
- Lines 635–643: Exit code extraction
- Lines 658–663: `_determine_phase_status()` call (3 args, no `started_at`)
- Lines 698–719: `if status.is_failure:` → diagnostics → HALTED

**Key gap**: Between lines 643 (exit code resolved) and 658 (`_determine_phase_status` called), there is no result-file write from the executor. The result file only exists if the *agent* wrote it during the subprocess session.

---

### `src/superclaude/cli/sprint/process.py`

**[`ClaudeProcess.build_prompt()`](../../src/superclaude/cli/sprint/process.py) — lines 115–157**

The "Completion Protocol" section (lines 137–150) instructs the agent to write the result file:
```python
            # process.py:137-150
            f"## Completion Protocol\n"
            f"When ALL tasks in this phase are complete "
            f"(or halted on STRICT failure):\n"
            f"1. Write a phase completion report to {result_file} containing:\n"
            f"   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), "
            f"tasks_total, tasks_passed, tasks_failed\n"
            f"   - Per-task status table: Task ID, Title, Tier, Status "
            f"(pass/fail/skip), Evidence\n"
            f"   - Files modified (list all paths)\n"
            f"   - Blockers for next phase (if any)\n"
            f"   - The literal string EXIT_RECOMMENDATION: CONTINUE "
            f"or EXIT_RECOMMENDATION: HALT\n"
            f"2. If any task produced file changes, list them under "
            f"## Files Modified\n"
```

**This is the text Spec A (SOL-A) wants to augment and Spec B (S1-R04) wants to remove.**

---

### `src/superclaude/cli/sprint/monitor.py`

**[`detect_error_max_turns()`](../../src/superclaude/cli/sprint/monitor.py) — lines 35–59**

```python
# monitor.py:35-59
def detect_error_max_turns(output_path: Path) -> bool:
    """Check if the last NDJSON line indicates budget exhaustion."""
    # Scans last non-empty line for "subtype":"error_max_turns" pattern
```

Spec B (S2-R01) proposes `detect_prompt_too_long()` following this exact architecture.

---

### `src/superclaude/cli/sprint/commands.py`

**[`run()`](../../src/superclaude/cli/sprint/commands.py) — lines 34–170**

The `run()` function body (lines 140–170) goes:
```python
    # commands.py:144-156 — load_sprint_config(...)
    # commands.py:162-164 — dry_run → _print_dry_run(config); return
    # commands.py:167-170 — tmux decision → launch_in_tmux(config) or execute_sprint(config)
```

**No fidelity check exists.** Spec A (SOL-G) proposes inserting one between lines 156 and 162.

---

### `src/superclaude/cli/sprint/diagnostics.py`

**[`FailureCategory`](../../src/superclaude/cli/sprint/diagnostics.py) — lines 19–26**

```python
# diagnostics.py:19-26
class FailureCategory(Enum):
    """Classification of phase failure root cause."""
    STALL = "stall"       # :22
    TIMEOUT = "timeout"   # :23
    CRASH = "crash"       # :24
    ERROR = "error"       # :25
    UNKNOWN = "unknown"   # :26
```

No `CONTEXT_EXHAUSTION` value. Spec B (S2-R07) proposes adding one.

---

## Section 1: Overlap Table — Same Problem, Two Solutions

### OV-1: `PhaseStatus` enum — new success-like value for non-zero exit recovery

| | Spec A (SOL-C, Step 3.1) | Spec B (S2-R03) |
|---|---|---|
| **Proposed name** | `PASS_WITH_WARNINGS` | `PASS_RECOVERED` |
| **Value** | `"pass_with_warnings"` | (implied `"pass_recovered"`) |
| **Semantics** | `is_terminal=True`, `is_success=True`, `is_failure=False` | `is_terminal=True`, `is_success=True`, `is_failure=False` |
| **Target file** | [`models.py:204`](../../src/superclaude/cli/sprint/models.py) | [`models.py:204`](../../src/superclaude/cli/sprint/models.py) |
| **Insertion point** | After `PASS_NO_REPORT` (line 211) | After `PASS_NO_REPORT` (line 211) |

**Superior approach**: **Spec B (`PASS_RECOVERED`)** — more semantically precise. "Recovered" conveys that the executor inferred success despite process failure. "With warnings" is vague. Spec B's name was selected through 3 adversarial rounds (88% convergence).

**Recommendation**: **Prefer Spec B's name; merge into single enum value.** Both specs need exactly one new `is_success=True` status for non-zero-exit recovery. Implement `PASS_RECOVERED` and use it for both checkpoint-inference (Spec A's SOL-C) and context-exhaustion recovery (Spec B's S2).

---

### OV-2: `_determine_phase_status()` — non-zero exit recovery logic

| | Spec A (SOL-C, Step 3.5) | Spec B (S2-R04) |
|---|---|---|
| **Target line** | [`executor.py:783`](../../src/superclaude/cli/sprint/executor.py) — `if exit_code != 0: return PhaseStatus.ERROR` | [`executor.py:783`](../../src/superclaude/cli/sprint/executor.py) — same line |
| **Recovery mechanism** | Checkpoint-presence inference: `_check_checkpoint_pass()` reads `checkpoints/CP-P{N:02d}-END.md` for `STATUS: PASS`, then `_check_contamination()` scans `artifacts/` for cross-phase task IDs | Context-exhaustion detection: `detect_prompt_too_long()` in monitor.py, then `_classify_from_result_file()` checks executor-written result file |
| **New helper functions** | `_check_checkpoint_pass()`, `_check_contamination()`, `_write_crash_recovery_log()` — all in executor.py | `detect_prompt_too_long()` in monitor.py, `_classify_from_result_file()` in executor.py |
| **Return value** | `PASS_WITH_WARNINGS` (if no contamination) or `ERROR` | `PASS_RECOVERED` (if result says CONTINUE), `HALT`, or `INCOMPLETE` |

**Superior approach**: **Merge required** — these are complementary, not competing. Spec B detects a *specific* failure mode (context exhaustion) and recovers via result-file parsing. Spec A detects a *general* failure mode (any crash with PASS checkpoint) and recovers via checkpoint + contamination check.

**Recommendation**: **Implement in sequence: Spec B's detection first (specific), then Spec A's checkpoint fallback (general).** The merged `if exit_code != 0` block becomes:

```python
# Proposed merged logic at executor.py:783
if exit_code != 0:
    # Path 1 — Specific: context exhaustion (Spec B S2-R04)
    if detect_prompt_too_long(output_file):
        return _classify_from_result_file(result_file, started_at=started_at, recovered=True)

    # Path 2 — General: checkpoint inference (Spec A SOL-C)
    if config is not None and phase is not None:
        if _check_checkpoint_pass(config, phase):
            contaminated = _check_contamination(config, phase)
            _write_crash_recovery_log(config, phase, contaminated)
            if not contaminated:
                return PhaseStatus.PASS_RECOVERED

    return PhaseStatus.ERROR
```

---

### OV-3: `_determine_phase_status()` — signature change

| | Spec A (SOL-C, Step 3.5 note) | Spec B (S2-R09) |
|---|---|---|
| **Current signature** | [`executor.py:764-768`](../../src/superclaude/cli/sprint/executor.py): `(exit_code, result_file, output_file) -> PhaseStatus` | Same |
| **Proposed additions** | `config: SprintConfig`, `phase: Phase` — for checkpoint/contamination helpers | `started_at: float` — for timestamp validation of result file |
| **Call site** | [`executor.py:658-663`](../../src/superclaude/cli/sprint/executor.py) — must pass `config` and `phase` | Same call site — must pass `started_at` (available at line 543) |

**Recommendation**: **Merge into single signature change** using keyword-only args with defaults for backward compatibility:

```python
# Proposed merged signature at executor.py:764
def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
    *,
    config: SprintConfig | None = None,
    phase: Phase | None = None,
    started_at: float = 0.0,
) -> PhaseStatus:
```

Updated call site at [`executor.py:658-663`](../../src/superclaude/cli/sprint/executor.py):
```python
            status = _determine_phase_status(
                exit_code=exit_code,
                result_file=config.result_file(phase),
                output_file=config.output_file(phase),
                config=config,
                phase=phase,
                started_at=started_at.timestamp(),  # convert datetime to float
            )
```

---

### OV-4: Pre-writing / executor-writing result file before `_determine_phase_status()`

| | Spec A (SOL-D, Phase 1) | Spec B (S1-R01/R03) |
|---|---|---|
| **Mechanism** | Pre-write `phase-N-result.md` with `EXIT_RECOMMENDATION: HALT` as dead-man's switch **before** subprocess launch (before line 541) | Executor writes `phase-N-result.md` from [`AggregatedPhaseReport.to_markdown()`](../../src/superclaude/cli/sprint/executor.py) (lines 243–281) **after** subprocess exits but **before** `_determine_phase_status()` (between lines 643 and 658) |
| **Content** | Static: `EXIT_RECOMMENDATION: HALT\n# Pre-written by executor; agent must overwrite with CONTINUE.\n` | Dynamic: Full aggregated report with YAML frontmatter, task status table, and correct `EXIT_RECOMMENDATION: CONTINUE/HALT` based on [`AggregatedPhaseReport.status`](../../src/superclaude/cli/sprint/executor.py) (lines 200–209) |
| **Atomicity** | `tempfile.NamedTemporaryFile` + `os.replace` | Not specified (simple write) |
| **New code** | ~20 lines (`_pre_write_result_file()` helper + call site) | ~5 lines (call `report.to_markdown()` and write to `config.result_file(phase)`) |

**Superior approach**: **Spec B (S1)** — strictly superior. The executor already has `AggregatedPhaseReport.to_markdown()` at lines 243–281 which produces a deterministic, data-rich result file. The `to_markdown()` method already emits `EXIT_RECOMMENDATION: CONTINUE` when `self.status == "PASS"` (line 278) and `EXIT_RECOMMENDATION: HALT` otherwise (line 280). Writing this to disk is ~5 lines of code vs SOL-D's ~20.

Spec A's dead-man's switch only covers the case where the *subprocess* crashes before writing the result file. But S1 makes the *executor* write it from its own data, so subprocess crashes don't matter — the executor always has `AggregatedPhaseReport` from `aggregate_task_results()` at lines 285–330.

**Recommendation**: **Prefer Spec B's S1; discard Spec A's SOL-D.** Insert the result-file write in `execute_sprint()` between lines 643 and 658:

```python
            # NEW: executor.py between lines 643 and 658
            # Write result file from executor's aggregated data (Spec B S1)
            report = aggregate_task_results(phase.number, task_results, remaining)
            config.result_file(phase).write_text(report.to_markdown())
```

---

### OV-5: Phase prompt — stop/boundary instruction

| | Spec A (SOL-A, Phase 2) | Spec B (S1-R04) |
|---|---|---|
| **Target** | [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) — Completion Protocol section of `build_prompt()` | Same lines |
| **Direction** | **ADD** ~200 tokens: `MANDATORY FINAL STEP` block with numbered instructions to write result file and stop | **REMOVE** the entire Completion Protocol section (lines 137–150) since executor writes the file |
| **Net token impact** | +200 tokens/phase | −200 tokens/phase (removal of lines 137–150) |

**Superior approach**: **Spec B (S1-R04)** — if the executor writes the result file, instructing the agent to also write it is redundant and wastes context. Spec A's SOL-A adds *more* prompt text for a problem S1 solves at the source.

**Recommendation**: **Implement S1-R04 (remove Completion Protocol from prompt). Discard SOL-A's result-file instructions.** However, extract the bleed-prevention "STOP" instruction from SOL-A as a 2-line addition:

Replace [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) with:
```python
            f"\n"
            f"## Scope Boundary\n"
            f"- After completing all tasks, STOP immediately.\n"
            f"- Do not read, open, or act on any subsequent phase file.\n"
```

---

## Section 2: Synergy Table — One Solution Serves Two Problems

| # | Shared Requirement | Spec A Need | Spec B Solution | Lines Saved | Code Reference |
|---|-------------------|-------------|-----------------|-------------|----------------|
| **SY-1** | Executor writes result file deterministically | SOL-D needs a pre-written result file as dead-man's switch; SOL-C needs result file to exist for checkpoint inference | **S1**: Executor writes [`AggregatedPhaseReport.to_markdown()`](../../src/superclaude/cli/sprint/executor.py) (lines 243–281) after subprocess exit | ~30 lines (entire `_pre_write_result_file()` helper + call site from SOL-D) | `AggregatedPhaseReport` already exists at [`executor.py:178-281`](../../src/superclaude/cli/sprint/executor.py). `aggregate_task_results()` exists at [`executor.py:285-330`](../../src/superclaude/cli/sprint/executor.py). Insert point: between [`executor.py:643`](../../src/superclaude/cli/sprint/executor.py) (exit code) and [`executor.py:658`](../../src/superclaude/cli/sprint/executor.py) (`_determine_phase_status`). |
| **SY-2** | Agent no longer responsible for result file | SOL-A's prompt stop instruction exists to ensure agent writes result file reliably | **S1-R04**: Remove result-file writing from agent's prompt at [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) | ~15 lines (entire `_append_phase_stop_instruction()` helper from SOL-A) | When the executor writes the result file, the entire class of problems SOL-A addresses (agent forgets to write, crashes before writing, bleeds into next phase while writing) is eliminated at the source. |
| **SY-3** | New `PhaseStatus` enum value for non-zero exit recovery | SOL-C needs `PASS_WITH_WARNINGS` for checkpoint inference | **S2-R03**: `PASS_RECOVERED` serves the same role | ~0 lines (same effort either way, avoid maintaining 2 values) | Insert at [`models.py:212`](../../src/superclaude/cli/sprint/models.py) (after `PASS_NO_REPORT`). Update [`is_terminal`](../../src/superclaude/cli/sprint/models.py) (line 218), [`is_success`](../../src/superclaude/cli/sprint/models.py) (line 231), [`is_failure`](../../src/superclaude/cli/sprint/models.py) (line 239). |
| **SY-4** | `_determine_phase_status` signature extension | SOL-C needs `config` + `phase` params | **S2-R09**: Needs `started_at` param | ~5 lines (single combined change vs two separate changes) | Current signature at [`executor.py:764-768`](../../src/superclaude/cli/sprint/executor.py). Current call site at [`executor.py:658-663`](../../src/superclaude/cli/sprint/executor.py). |
| **SY-5** | Context token reduction in phase prompt | SOL-A adds ~200 tokens of stop instruction to every prompt | **S3**: Directory isolation + summary header saves ~14K tokens/phase | Net +200 token savings by removing SOL-A instead of adding it | Current prompt at [`process.py:115-157`](../../src/superclaude/cli/sprint/process.py). |

**Total estimated savings from consolidation**: ~50 lines of production code, ~200 prompt tokens/phase, 1 fewer enum value to maintain.

---

## Section 3: Conflict Table — Solution A Breaks Spec B (or vice versa)

### C-1: Pre-write dead-man's switch vs executor-written result file (MEDIUM)

| | Detail |
|---|---|
| **Spec A element** | SOL-D: Pre-write `phase-N-result.md` with `EXIT_RECOMMENDATION: HALT` before subprocess launch (before [`executor.py:541`](../../src/superclaude/cli/sprint/executor.py)) |
| **Spec B element** | S1-R01: Executor writes result file from `AggregatedPhaseReport.to_markdown()` after subprocess exit (between [`executor.py:643`](../../src/superclaude/cli/sprint/executor.py) and [`executor.py:658`](../../src/superclaude/cli/sprint/executor.py)). S2-R06: Validate result file `mtime > phase_started_at` before trusting it. |
| **Failure mode** | **Write collision + timestamp incompatibility**: SOL-D pre-writes at time T₀ (before subprocess launch at line 541). `started_at` is captured at line 543 (time T₁). S2-R06 checks `mtime > started_at`. Since T₀ < T₁, the pre-written file's `mtime` will always fail the staleness check. The dead-man's switch can never fire because S2-R06 will reject it as stale. Additionally, if S1 runs successfully, SOL-D's pre-write is overwritten and becomes a no-op. If S1 does *not* run (executor crashes between lines 643 and 658), the stale pre-write causes incorrect behavior on next run. |
| **Severity** | **Medium** — SOL-D becomes both redundant (when S1 works) and subtly broken (when S2-R06 validates timestamps) |
| **Resolution** | **Discard SOL-D entirely.** S1 + S2's timestamp validation make SOL-D both redundant and incompatible. |

### C-2: Checkpoint inference vs context-exhaustion detection — control flow ordering (HIGH)

| | Detail |
|---|---|
| **Spec A element** | SOL-C (Step 3.5): In `_determine_phase_status()` at [`executor.py:783`](../../src/superclaude/cli/sprint/executor.py), replace `return PhaseStatus.ERROR` with checkpoint-presence inference → `PASS_WITH_WARNINGS` |
| **Spec B element** | S2-R04: At the same line, replace `return PhaseStatus.ERROR` with prompt-too-long detection → result-file classification → `PASS_RECOVERED` / `HALT` / `INCOMPLETE` |
| **Failure mode** | **Ordering ambiguity**: Both add branches inside the `if exit_code != 0` block. If SOL-C's checkpoint check runs first and returns `PASS_RECOVERED`, S2's `detect_prompt_too_long()` never runs — the diagnostic classification (`FailureCategory.CONTEXT_EXHAUSTION` at [`diagnostics.py:19`](../../src/superclaude/cli/sprint/diagnostics.py)) is lost. If S2 runs first and detects prompt-too-long, it correctly classifies the root cause. If S2 doesn't detect prompt-too-long, SOL-C serves as a broader fallback. |
| **Severity** | **High** — wrong ordering loses diagnostic specificity for context exhaustion events |
| **Resolution** | **Implement as ordered chain**: `exit_code != 0` → (1) `detect_prompt_too_long()` (Spec B, specific) → (2) `_check_checkpoint_pass()` (Spec A, general) → (3) `ERROR` (default). This preserves diagnostic specificity while retaining the broader safety net. |

### C-3: Two enum names for same concept (HIGH)

| | Detail |
|---|---|
| **Spec A element** | SOL-C Step 3.1: Add `PASS_WITH_WARNINGS = "pass_with_warnings"` to [`PhaseStatus`](../../src/superclaude/cli/sprint/models.py) at line 204 |
| **Spec B element** | S2-R03: Add `PASS_RECOVERED` to [`PhaseStatus`](../../src/superclaude/cli/sprint/models.py) at line 204 |
| **Failure mode** | **Enum collision**: Two different names for functionally identical values (`is_success=True`, `is_failure=False`, `is_terminal=True`). Both are used for the same purpose: non-zero exit code with evidence of successful completion. Having both creates confusion in: [`SprintTUI`](../../src/superclaude/cli/sprint/tui.py) display logic, [`SprintLogger`](../../src/superclaude/cli/sprint/logger.py) formatting, downstream consumers checking `status.is_success`. |
| **Severity** | **High** — two values for same concept is a maintenance hazard |
| **Resolution** | **Use `PASS_RECOVERED` only.** Drop `PASS_WITH_WARNINGS`. Both recovery paths (context exhaustion and checkpoint inference) return the same enum value. Root cause specificity is carried by `FailureCategory` in [`diagnostics.py`](../../src/superclaude/cli/sprint/diagnostics.py), not by `PhaseStatus`. |

### C-4: Add result-writing instruction vs remove it — direct contradiction (CRITICAL)

| | Detail |
|---|---|
| **Spec A element** | SOL-A (Phase 2, Step 2.2): Append `_append_phase_stop_instruction()` block to `build_prompt()` at [`process.py:115`](../../src/superclaude/cli/sprint/process.py) — adds ~200 tokens instructing agent to write result file with `EXIT_RECOMMENDATION` and stop |
| **Spec B element** | S1-R04: Remove the Completion Protocol section from `build_prompt()` at [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) — removes agent's result-file-writing responsibility |
| **Failure mode** | **Direct contradiction**: SOL-A adds a detailed instruction block telling the agent to write the result file. S1-R04 removes exactly that instruction. Implementing both is incoherent — the prompt would simultaneously tell the agent to write the file and not tell it to write the file. Even if applied sequentially (remove old, add new), the new instruction is redundant because the executor writes the file (S1-R01). |
| **Severity** | **Critical** — mutually exclusive approaches to the same prompt lines |
| **Resolution** | **Implement S1-R04 (remove agent result-writing from prompt at lines 137–150).** The executor writes the file deterministically (S1-R01), so the agent instruction is unnecessary. Extract only the "STOP immediately — do not act on subsequent phase files" bleed-prevention portion of SOL-A as a 2-line replacement (not the full SOL-A block). |

### C-5: Checkpoint file dependency vs executor-written result file (LOW)

| | Detail |
|---|---|
| **Spec A element** | SOL-C Step 3.2: `_check_checkpoint_pass()` reads `checkpoints/CP-P{N:02d}-END.md` — depends on the *agent* having written a checkpoint file during execution |
| **Spec B element** | S1-R01: Executor writes result file from `AggregatedPhaseReport` (at [`executor.py:178`](../../src/superclaude/cli/sprint/executor.py)) — deterministic, does not depend on agent |
| **Failure mode** | **Reliability asymmetry**: SOL-C's checkpoint inference depends on agent behavior (writing checkpoint files). In the crash scenarios SOL-C targets, the checkpoint file may or may not exist depending on when the crash occurred. S1's result file always exists because the *executor* writes it from its own data. SOL-C would produce false negatives (no checkpoint file → `ERROR`) in cases where S1 correctly produces `PASS_RECOVERED`. |
| **Severity** | **Low** — SOL-C is a fallback, not the primary path |
| **Resolution** | **SOL-C remains valuable as defense-in-depth** for the edge case where S1's result file is somehow missing or corrupt. But it should be the *last* fallback. Recovery priority chain: S2 (context exhaustion) → S1 result-file check → SOL-C checkpoint inference → `ERROR`. |

### C-6: Fidelity preflight — no conflict (NONE)

| | Detail |
|---|---|
| **Spec A element** | SOL-G: `_check_fidelity()` in [`commands.py`](../../src/superclaude/cli/sprint/commands.py) with `--force-fidelity-fail` option on `run()` at line 34 |
| **Spec B element** | No counterpart — Spec B does not touch `commands.py:run()` options |
| **Failure mode** | None — SOL-G inserts between [`commands.py:156`](../../src/superclaude/cli/sprint/commands.py) and [`commands.py:162`](../../src/superclaude/cli/sprint/commands.py), a region Spec B does not modify |
| **Severity** | **None** |
| **Resolution** | **Implement SOL-G as-is.** Fully independent of all Spec B changes. |

---

## Section 4: Recommended Implementation Order (Merged Sequence)

### Step 1: Add `PASS_RECOVERED` to `PhaseStatus` enum
- **Source**: Spec B S2-R03 (supersedes Spec A SOL-C Step 3.1 `PASS_WITH_WARNINGS`)
- **File**: [`src/superclaude/cli/sprint/models.py:204-241`](../../src/superclaude/cli/sprint/models.py)
- **Change**: Insert `PASS_RECOVERED = "pass_recovered"` after line 211. Add to `is_terminal` tuple (line 220), `is_success` tuple (line 233). Exclude from `is_failure` (line 240).
- **Rationale**: Foundation for all subsequent recovery logic. Single enum value serves both specs.
- **Risk**: Low. Additive change. Existing code doesn't reference the new value.

### Step 2: Executor writes result file from `AggregatedPhaseReport`
- **Source**: Spec B S1-R01/R03 (supersedes Spec A SOL-D)
- **File**: [`src/superclaude/cli/sprint/executor.py`](../../src/superclaude/cli/sprint/executor.py) — insert between line 643 (exit code resolved) and line 658 (`_determine_phase_status` call) inside `execute_sprint()`
- **Change**: ~5 lines: call `aggregate_task_results()` (already exists at line 285), write `report.to_markdown()` to `config.result_file(phase)`
- **Context**: `AggregatedPhaseReport.to_markdown()` at lines 243–281 already produces the correct `EXIT_RECOMMENDATION` token. `aggregate_task_results()` at lines 285–330 already constructs the report from `TaskResult` list. The `task_results` and `remaining` variables are available from the earlier call to `execute_phase_tasks()` at lines 348–445.
- **Rationale**: Eliminates root cause of Phase 8 halt. Makes SOL-D unnecessary. Ensures result file always exists before `_determine_phase_status()`.

### Step 3: Remove agent result-file-writing from prompt + add bleed-prevention stop line
- **Source**: Spec B S1-R04 (supersedes Spec A SOL-A), with 2-line extract from SOL-A
- **File**: [`src/superclaude/cli/sprint/process.py:137-150`](../../src/superclaude/cli/sprint/process.py)
- **Change**: Replace the "Completion Protocol" section (lines 137–150, ~14 lines) with a 4-line "Scope Boundary" section containing only the stop instruction. Remove reference to `result_file` variable (line 118) if no longer used.
- **Rationale**: Agent no longer writes result file; stop instruction prevents phase bleed.

### Step 4: Add `detect_prompt_too_long()` in `monitor.py`
- **Source**: Spec B S2-R01/R02/R08
- **File**: [`src/superclaude/cli/sprint/monitor.py`](../../src/superclaude/cli/sprint/monitor.py) — add after `detect_error_max_turns()` (line 59)
- **Change**: New function following the exact pattern of [`detect_error_max_turns()`](../../src/superclaude/cli/sprint/monitor.py) at lines 35–59. Pattern: `r'"Prompt is too long"'` matched against last 10 non-empty lines (not just last 1 as `detect_error_max_turns` does). Add `PROMPT_TOO_LONG_PATTERN` constant near line 32 alongside `ERROR_MAX_TURNS_PATTERN`.
- **Rationale**: Independent of other changes. Required for Step 6.

### Step 5: `_check_fidelity()` + `--force-fidelity-fail` in `commands.py`
- **Source**: Spec A SOL-G (fully independent)
- **File**: [`src/superclaude/cli/sprint/commands.py`](../../src/superclaude/cli/sprint/commands.py)
- **Change**: Add `--force-fidelity-fail` Click option (insert near line 115, after existing options). Add `_check_fidelity(index_path)` helper function. Wire preflight check into `run()` body between lines 156 and 162 (after `load_sprint_config`, before dry-run check).
- **Rationale**: Zero interaction with any Spec B change. Can be implemented in parallel with Steps 3–4.

### Step 6: Restructure `_determine_phase_status()` with merged recovery chain
- **Source**: Spec B S2-R04/R05/R06/R09 + Spec A SOL-C (checkpoint fallback)
- **File**: [`src/superclaude/cli/sprint/executor.py:764-814`](../../src/superclaude/cli/sprint/executor.py)
- **Change**:
  1. Extend signature (line 764) to add keyword-only `config`, `phase`, `started_at` params
  2. Replace `if exit_code != 0: return PhaseStatus.ERROR` (line 783) with ordered recovery chain:
     - Path 1: `detect_prompt_too_long(output_file)` → `_classify_from_result_file()` (Spec B S2)
     - Path 2: `_check_checkpoint_pass(config, phase)` + `_check_contamination()` → `PASS_RECOVERED` (Spec A SOL-C)
     - Path 3: `return PhaseStatus.ERROR` (unchanged default)
  3. Add `_classify_from_result_file()` helper (Spec B S2-R05) with `mtime` validation (S2-R06)
  4. Add `_check_checkpoint_pass()`, `_check_contamination()`, `_write_crash_recovery_log()` helpers (Spec A SOL-C)
  5. Update call site at [`executor.py:658-663`](../../src/superclaude/cli/sprint/executor.py) to pass `config`, `phase`, `started_at`
- **Rationale**: Specific detection (S2) before general inference (SOL-C). Both use `PASS_RECOVERED`. Timestamp validation prevents stale-file false positives.

### Step 7: Phase-specific directory isolation + summary header
- **Source**: Spec B S3-R01 through S3-R06
- **Files**: [`executor.py`](../../src/superclaude/cli/sprint/executor.py) (isolation lifecycle in `execute_sprint()` around line 530), [`process.py`](../../src/superclaude/cli/sprint/process.py) (summary header in `build_prompt()`)
- **Change**: Before subprocess launch (before line 541), create `config.results_dir/.isolation/phase-{N}/` and copy phase file. Set `scoped_work_dir` for `ClaudeProcess`. Add cleanup in finally block (after line 738). Add summary header to `build_prompt()`. Add orphan cleanup at sprint startup (after line 500).
- **Rationale**: Prevention layer. Independent of recovery logic. Saves ~14K tokens/phase.

### Step 8: Add `FailureCategory.CONTEXT_EXHAUSTION` to diagnostics
- **Source**: Spec B S2-R07
- **File**: [`src/superclaude/cli/sprint/diagnostics.py:19-26`](../../src/superclaude/cli/sprint/diagnostics.py)
- **Change**: Add `CONTEXT_EXHAUSTION = "context_exhaustion"` after line 26. Update `FailureClassifier` to detect this category when `detect_prompt_too_long()` returns True.
- **Rationale**: Low-risk additive change for diagnostic visibility.

### Step 9: Tests (merged)
- **Source**: Both specs' test requirements, deduplicated
- **File**: `tests/cli_portify/test_phase8_halt_fix.py` (expanded scope to cover both specs)
- **Test matrix**:

| Test | Source | What it validates |
|------|--------|-------------------|
| `PASS_RECOVERED` enum properties | SY-3 (merged) | `is_terminal=True`, `is_success=True`, `is_failure=False` |
| Executor writes result file with CONTINUE | Spec B S1 | `AggregatedPhaseReport.to_markdown()` written to `config.result_file(phase)` |
| Executor writes result file with HALT | Spec B S1 | Failed tasks → `EXIT_RECOMMENDATION: HALT` in file |
| Result file written before `_determine_phase_status()` | Spec B S1 | Ordering guarantee |
| `detect_prompt_too_long()` matches pattern | Spec B S2 | Pattern in last 10 lines → True |
| `detect_prompt_too_long()` clean output | Spec B S2 | No pattern → False |
| exit=1 + prompt-too-long + CONTINUE → `PASS_RECOVERED` | Spec B S2 | Context exhaustion recovery |
| exit=1 + prompt-too-long + stale mtime → `INCOMPLETE` | Spec B S2 | Timestamp validation |
| exit=1 + PASS checkpoint + no contamination → `PASS_RECOVERED` | Spec A SOL-C | Checkpoint inference |
| exit=1 + PASS checkpoint + contamination → `ERROR` | Spec A SOL-C | Contamination guard |
| Fidelity fail without override → SystemExit(1) | Spec A SOL-G | Preflight block |
| `--force-fidelity-fail` override → proceeds | Spec A SOL-G | Override escape hatch |
| Isolation directory created + cleaned up | Spec B S3 | Lifecycle management |
| Summary header in prompt | Spec B S3 | Metadata presence |

### Step 10: Integration verification
- **Change**: Dry-run smoke test, `ruff check`, `ruff format --check`, `uv run pytest tests/ -v --tb=short`
- **Acceptance**: Zero lint errors, all existing + new tests pass.

---

## Disposition Summary

### Spec A Elements

| Element | Disposition | Reason | Lines Affected |
|---------|------------|--------|----------------|
| **SOL-D** (pre-write dead-man's switch) | **DISCARD** | Superseded by S1. Incompatible with S2-R06 timestamp validation (C-1). | Would have touched [`executor.py:~540`](../../src/superclaude/cli/sprint/executor.py) |
| **SOL-A** (prompt stop instruction) | **PARTIAL DISCARD** | Result-file instructions removed (S1-R04). Bleed-prevention "STOP" line retained (2 lines). See C-4. | [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) |
| **SOL-C** (checkpoint inference) | **KEEP as fallback** | Demoted from primary to tertiary recovery path (after S2 and S1). Uses `PASS_RECOVERED` not `PASS_WITH_WARNINGS`. See C-2, C-5. | [`executor.py:783`](../../src/superclaude/cli/sprint/executor.py) |
| **SOL-G** (fidelity preflight) | **KEEP as-is** | Fully independent (C-6). | [`commands.py:~115, ~156`](../../src/superclaude/cli/sprint/commands.py) |

### Spec B Elements

| Element | Disposition | Reason | Lines Affected |
|---------|------------|--------|----------------|
| **S1** (executor writes result) | **KEEP — primary** | Highest-priority change. Eliminates root cause for both specs (SY-1, SY-2). | [`executor.py:643-658`](../../src/superclaude/cli/sprint/executor.py), [`process.py:137-150`](../../src/superclaude/cli/sprint/process.py) |
| **S2** (context exhaustion detection) | **KEEP — primary** | Specific detection + recovery. First branch in `exit_code != 0` chain (C-2). | [`monitor.py:~59`](../../src/superclaude/cli/sprint/monitor.py), [`executor.py:764-814`](../../src/superclaude/cli/sprint/executor.py), [`models.py:204`](../../src/superclaude/cli/sprint/models.py) |
| **S3** (directory isolation) | **KEEP — primary** | Prevention layer. Independent. Saves ~14K tokens/phase (SY-5). | [`executor.py:~530`](../../src/superclaude/cli/sprint/executor.py), [`process.py:~115`](../../src/superclaude/cli/sprint/process.py) |
| **S4** (artifact batching design) | **KEEP — deferred** | Design-only. No implementation overlap. | New document only |

---

## Risk Assessment for Merged Implementation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Merged `_determine_phase_status` has 3 recovery paths at [`executor.py:783`](../../src/superclaude/cli/sprint/executor.py) — increased complexity | Medium | Clear ordering (S2 → SOL-C → ERROR) with early returns. Each path is a separate helper function. |
| `PASS_RECOVERED` used for two different recovery mechanisms — loss of diagnostic specificity | Low | `FailureCategory` at [`diagnostics.py:19`](../../src/superclaude/cli/sprint/diagnostics.py) carries root cause specificity. Execution log entry distinguishes the trigger. |
| SOL-C checkpoint inference depends on agent-written checkpoint files — unreliable | Low | SOL-C is last-resort fallback only. S1 + S2 handle primary cases deterministically. |
| Removing Completion Protocol from prompt ([`process.py:137-150`](../../src/superclaude/cli/sprint/process.py)) while agent may still be expected to produce artifacts | Low | Agent still produces task artifacts (code, specs). Only the *result file* responsibility is removed. |
| `_determine_phase_status` signature change breaks existing test mocks | Low | Keyword-only args with defaults (`config=None`, `phase=None`, `started_at=0.0`). All existing 3-arg calls continue to work. |
| TUI/logger don't handle `PASS_RECOVERED` display | Medium | Verify [`SprintTUI.update()`](../../src/superclaude/cli/sprint/tui.py) and [`SprintLogger.write_phase_result()`](../../src/superclaude/cli/sprint/logger.py) handle unknown `PhaseStatus` values gracefully before adding the new status. |
