# Implementation Workflow: Adversarial-Validated Phase 8 Halt Fix

**Source**: `docs/generated/Phase8-SprintContext-cross-spec-overlap-analysis-adversarial/cross-spec-overlap-validation.md`
**Original Analysis**: `docs/generated/Phase8-SprintContext-cross-spec-overlap-analysis.md`
**Spec A**: `docs/generated/phase8-halt-fix.md` (Phase 8 Halt Fix)
**Spec B**: `docs/generated/sprint-context-exhaustion-prd.md` (Context Exhaustion PRD)
**Strategy**: systematic
**Compliance**: strict
**Generated**: 2026-03-15

---

## Design Decision: Step 2 Corrective Approach

The adversarial validation **REJECTED** the original Step 2 because `execute_sprint()` does not call `execute_phase_tasks()` and has no `task_results` in scope. Two corrective options were identified:

- **(a)** Wire `execute_phase_tasks()` into `execute_sprint()` — substantial refactor, high risk
- **(b)** Write a minimal result file from phase-level data — implementable now, degraded but functional

**This tasklist implements option (b)**: construct a minimal `AggregatedPhaseReport` from the exit code and `MonitorState` data available in `execute_sprint()`. This produces a valid result file with `EXIT_RECOMMENDATION: CONTINUE/HALT` without requiring the per-task execution model. The minimal report will have `tasks_total=1`, treating each phase as a single logical task, and derive status from exit code (0=PASS, 124=TIMEOUT, else=FAIL).

**Circularity resolution (OV-2/Step 6)**: Since the executor now writes the result file, `_classify_from_result_file()` in `_determine_phase_status()` must read the **agent-written** result file (if it exists and is newer than `started_at`), not the executor-written one. The executor writes its file AFTER `_determine_phase_status()` returns, not before. This means: (1) `_determine_phase_status` reads the agent's file (or no file), (2) the executor writes its own file afterward for downstream consumers. This eliminates the circularity.

---

## Dependency Graph

```
T01 (PASS_RECOVERED enum)
 │
 ├─→ T02 (detect_prompt_too_long)     [independent, parallel-safe]
 │
 ├─→ T03 (fidelity preflight)         [independent, parallel-safe]
 │
 ├─→ T04 (FailureCategory.CONTEXT_EXHAUSTION)  [independent]
 │
 ├─→ T05 (restructure _determine_phase_status) [depends: T01, T02]
 │    │
 │    └─→ T06 (executor writes result file AFTER status) [depends: T05]
 │         │
 │         └─→ T07 (remove Completion Protocol from prompt) [depends: T06]
 │
 ├─→ T08 (directory isolation)         [independent, parallel-safe]
 │
 └─→ T09 (tests)                       [depends: T01-T08]
      │
      └─→ T10 (integration verification) [depends: T09]
```

**Key ordering change vs original**: The executor result-file write (T06) now occurs **AFTER** `_determine_phase_status` (T05), not before. This eliminates the circularity identified by the adversarial validation.

---

## Phase 1: Foundation — Additive, Zero-Risk Changes

### T01: Add `PASS_RECOVERED` to `PhaseStatus` enum
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/models.py`
- **Verdict**: CONFIRMED by adversarial validation
- **Risk**: Low — additive only
- **Depends on**: nothing

#### T01.01: Insert `PASS_RECOVERED` enum value
- **Action**: In `class PhaseStatus(Enum)` at line 204, insert `PASS_RECOVERED = "pass_recovered"` after `PASS_NO_REPORT` (line 211) and before `INCOMPLETE` (line 212).
- **Exact location**: `models.py:212` — insert new line before current line 212
- **Code**:
  ```python
  PASS_RECOVERED = "pass_recovered"  # non-zero exit but evidence of success
  ```
- **Acceptance**: `PhaseStatus.PASS_RECOVERED.value == "pass_recovered"`

#### T01.02: Add `PASS_RECOVERED` to `is_terminal` property
- **Action**: In the `is_terminal` property tuple (lines 218-229), add `PhaseStatus.PASS_RECOVERED` to the tuple. Insert after `PhaseStatus.PASS_NO_REPORT`.
- **Exact location**: `models.py` — inside the `is_terminal` return tuple, after the `PhaseStatus.PASS_NO_REPORT,` entry
- **Acceptance**: `PhaseStatus.PASS_RECOVERED.is_terminal is True`

#### T01.03: Add `PASS_RECOVERED` to `is_success` property
- **Action**: In the `is_success` property tuple (lines 231-237), add `PhaseStatus.PASS_RECOVERED`. Insert after `PhaseStatus.PASS_NO_REPORT`.
- **Exact location**: `models.py` — inside the `is_success` return tuple
- **Acceptance**: `PhaseStatus.PASS_RECOVERED.is_success is True`

#### T01.04: Verify `PASS_RECOVERED` excluded from `is_failure`
- **Action**: Confirm that the `is_failure` property tuple (lines 239-241) does NOT list `PASS_RECOVERED`. It should not — `is_failure` only includes `INCOMPLETE, HALT, TIMEOUT, ERROR`. No change needed; this is a verification step.
- **Acceptance**: `PhaseStatus.PASS_RECOVERED.is_failure is False`

---

### T02: Add `detect_prompt_too_long()` in `monitor.py`
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/monitor.py`
- **Verdict**: CONFIRMED by adversarial validation
- **Risk**: Low — additive, follows existing pattern exactly
- **Depends on**: nothing

#### T02.01: Add `PROMPT_TOO_LONG_PATTERN` constant
- **Action**: Add a new regex constant near line 32 (alongside the existing `ERROR_MAX_TURNS_PATTERN`).
- **Exact location**: `monitor.py:33` — insert new line after `ERROR_MAX_TURNS_PATTERN`
- **Code**:
  ```python
  PROMPT_TOO_LONG_PATTERN = re.compile(r'"Prompt is too long"')
  ```
- **Acceptance**: `PROMPT_TOO_LONG_PATTERN` defined in module scope

#### T02.02: Add `detect_prompt_too_long()` function
- **Action**: Add a new function after `detect_error_max_turns()` (which ends at line 59). Follow the exact pattern of `detect_error_max_turns()` but scan the last 10 non-empty lines (not just the last 1) because the prompt-too-long error may appear in non-final NDJSON lines.
- **Exact location**: `monitor.py:61` — insert after the blank line following `detect_error_max_turns`
- **Code**:
  ```python
  def detect_prompt_too_long(output_path: Path) -> bool:
      """Check if NDJSON output contains a prompt-too-long error.

      Scans the last 10 non-empty lines of the output file for the
      ``"Prompt is too long"`` pattern, which signals that the subprocess
      context window was exhausted.

      Returns True if the pattern is found, False otherwise.
      """
      try:
          content = output_path.read_text(errors="replace")
      except (FileNotFoundError, OSError):
          return False

      if not content.strip():
          return False

      lines = content.strip().splitlines()
      # Scan last 10 non-empty lines (pattern may not be in the final line)
      count = 0
      for line in reversed(lines):
          line = line.strip()
          if not line:
              continue
          if PROMPT_TOO_LONG_PATTERN.search(line):
              return True
          count += 1
          if count >= 10:
              break

      return False
  ```
- **Acceptance**: `detect_prompt_too_long(path_with_pattern)` returns True; `detect_prompt_too_long(clean_path)` returns False

#### T02.03: Export `detect_prompt_too_long` for use in executor
- **Action**: Verify the function is importable. No `__all__` list exists in `monitor.py`, so it will be importable by default. Add an import in `executor.py` at line 28 (alongside the existing `detect_error_max_turns` import).
- **Exact location**: `executor.py:28` — modify the import line
- **Current**: `from .monitor import OutputMonitor, detect_error_max_turns`
- **Change to**: `from .monitor import OutputMonitor, detect_error_max_turns, detect_prompt_too_long`
- **Acceptance**: `from superclaude.cli.sprint.monitor import detect_prompt_too_long` succeeds

---

### T03: Add `_check_fidelity()` + `--force-fidelity-fail` in `commands.py`
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/commands.py`
- **Verdict**: CONFIRMED by adversarial validation (with insertion point correction)
- **Risk**: Low — fully independent of all other changes
- **Depends on**: nothing

#### T03.01: Add `--force-fidelity-fail` Click option
- **Action**: Add a new Click option to the `run` command. Insert after the `--shadow-gates` option (line 113), before the `def run(` line (line 114).
- **Exact location**: `commands.py:113` — insert new decorator after `shadow-gates`
- **Code**:
  ```python
  @click.option(
      "--force-fidelity-fail",
      "force_fidelity_fail",
      default="",
      help="Override fidelity block with justification string.",
  )
  ```
- **Acceptance**: `superclaude sprint run --help` shows `--force-fidelity-fail`

#### T03.02: Add `force_fidelity_fail` parameter to `run()` signature
- **Action**: Add `force_fidelity_fail: str,` parameter to the `run()` function signature (currently lines 114-128). Insert after `shadow_gates: bool,`.
- **Exact location**: `commands.py:128` — add new parameter before the closing `)`
- **Acceptance**: `run()` accepts `force_fidelity_fail` parameter

#### T03.03: Implement `_check_fidelity()` helper
- **Action**: Add a new function above the `run` command definition (before line 34). This function checks `.roadmap-state.json` for `fidelity_status: fail`.
- **Exact location**: `commands.py` — insert before `@sprint_group.command()` (line 35). Add necessary imports at top of file (`json`, `Path` already imported).
- **Code**:
  ```python
  def _check_fidelity(index_path: Path) -> tuple[bool, str]:
      """Check sprint dir for spec-fidelity fail state.

      Returns (blocked, message). blocked=True means execution should be blocked.
      """
      import json as _json
      sprint_dir = index_path.parent
      state_file = sprint_dir / ".roadmap-state.json"
      if not state_file.exists():
          return False, ""
      try:
          state = _json.loads(state_file.read_text())
      except (ValueError, OSError):
          return False, ""
      if state.get("fidelity_status") != "fail":
          return False, ""
      deviations_summary = ""
      fidelity_output = state.get("steps", {}).get("spec-fidelity", {}).get("output_file")
      if fidelity_output:
          fidelity_file = Path(fidelity_output)
          if fidelity_file.exists():
              lines = fidelity_file.read_text(errors="replace").splitlines()
              high_lines = [l for l in lines if "HIGH" in l or "### DEV-" in l][:20]
              deviations_summary = "\n".join(high_lines)
      msg = (
          f"Sprint blocked: spec-fidelity check FAILED.\n"
          f"The tasklist was generated from a spec with unresolved HIGH severity deviations:\n"
          f"{deviations_summary or '(see spec-fidelity.md for details)'}\n\n"
          f"To override: add --force-fidelity-fail '<justification>' to your command."
      )
      return True, msg
  ```
- **Acceptance**: Returns `(False, "")` when no `.roadmap-state.json`; returns `(True, message)` when `fidelity_status == "fail"`

#### T03.04: Wire fidelity check into `run()` body
- **Action**: Insert fidelity check into `run()` after `tmux_session_name` threading (line 160) and before the `if dry_run:` check (line 162). **Note**: The adversarial validation (FACT-26) confirmed that lines 158-160 contain tmux session threading, so insertion must be after line 160.
- **Exact location**: `commands.py:161` — insert between line 160 (`config.tmux_session_name = tmux_session_name`) and line 162 (`if dry_run:`)
- **Code**:
  ```python
      # Preflight: fidelity block
      blocked, fidelity_msg = _check_fidelity(index_path)
      if blocked:
          if not force_fidelity_fail:
              click.echo(fidelity_msg, err=True)
              raise SystemExit(1)
          else:
              click.echo(
                  f"[WARN] Fidelity block overridden: {force_fidelity_fail}",
                  err=True,
              )
  ```
- **Acceptance**: `fidelity_status=fail` without `--force-fidelity-fail` exits with code 1; with `--force-fidelity-fail "reason"` proceeds with warning

---

### T04: Add `FailureCategory.CONTEXT_EXHAUSTION` to diagnostics
- **Tier**: STANDARD
- **File**: `src/superclaude/cli/sprint/diagnostics.py`
- **Verdict**: CONFIRMED by adversarial validation
- **Risk**: Low — additive
- **Depends on**: nothing

#### T04.01: Add `CONTEXT_EXHAUSTION` enum value
- **Action**: In `class FailureCategory(Enum)` at line 19, add `CONTEXT_EXHAUSTION = "context_exhaustion"` after `UNKNOWN` (line 26).
- **Exact location**: `diagnostics.py:27` — insert new line after `UNKNOWN = "unknown"`
- **Code**:
  ```python
  CONTEXT_EXHAUSTION = "context_exhaustion"
  ```
- **Acceptance**: `FailureCategory.CONTEXT_EXHAUSTION.value == "context_exhaustion"`

#### T04.02: Update `FailureClassifier.classify()` to detect context exhaustion
- **Action**: In the `classify` method (lines 148-194), add a new classification check between the TIMEOUT check (line 177) and the CRASH check (line 179). Import `detect_prompt_too_long` at the top of the method or at module level.
- **Exact location**: `diagnostics.py:178` — insert new block after timeout return, before crash check
- **Code**:
  ```python
          # 2.5. Context exhaustion (prompt too long)
          from .monitor import detect_prompt_too_long
          output_file = bundle.phase_result.phase.file.parent.parent / "results" / f"phase-{bundle.phase_result.phase.number}-output.jsonl"
          # Use the output path from the phase result if available
          if hasattr(bundle, 'output_path') and bundle.output_path:
              output_file = bundle.output_path
          if exit_code != 0 and detect_prompt_too_long(output_file):
              evidence.append(f"Context exhaustion detected (exit code {exit_code})")
              bundle.classification_evidence = evidence
              return FailureCategory.CONTEXT_EXHAUSTION
  ```
- **Note**: The exact output path resolution depends on how `DiagnosticBundle` stores it. Read `DiagnosticCollector.collect()` to find the correct field name for the output file path. Adjust accordingly.
- **Acceptance**: When `detect_prompt_too_long()` returns True for a non-zero exit, classification returns `CONTEXT_EXHAUSTION`

---

## Phase 2: Core Recovery Logic

### T05: Restructure `_determine_phase_status()` with merged recovery chain
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/executor.py`
- **Verdict**: AMEND — ordering correct, circularity resolved by writing result file AFTER status determination
- **Risk**: Medium — modifies critical path
- **Depends on**: T01 (PASS_RECOVERED), T02 (detect_prompt_too_long)

#### T05.01: Extend `_determine_phase_status` signature
- **Action**: Add keyword-only parameters with defaults to preserve backward compatibility. The function starts at line 765.
- **Exact location**: `executor.py:765-769`
- **Current**:
  ```python
  def _determine_phase_status(
      exit_code: int,
      result_file: Path,
      output_file: Path,
  ) -> PhaseStatus:
  ```
- **Change to**:
  ```python
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
- **Import needed**: `Phase` is already imported via `from .models import ...` at line 15. `SprintConfig` is already imported. No new imports needed.
- **Acceptance**: Existing 3-arg calls continue to work; new kwargs accepted

#### T05.02: Add `_classify_from_result_file()` helper
- **Action**: Add a new helper function before `_determine_phase_status` (before line 765). This function reads the agent-written result file and classifies the outcome. It validates that the file's mtime is after `started_at` to reject stale files from prior runs.
- **Exact location**: `executor.py:764` — insert before the `_determine_phase_status` function
- **Code**:
  ```python
  def _classify_from_result_file(
      result_file: Path,
      started_at: float,
  ) -> PhaseStatus | None:
      """Classify phase outcome from the agent-written result file.

      Returns a PhaseStatus if the result file exists, is fresh (mtime > started_at),
      and contains a recognizable EXIT_RECOMMENDATION. Returns None if the file is
      missing, stale, or unreadable.
      """
      if not result_file.exists():
          return None
      try:
          mtime = result_file.stat().st_mtime
      except OSError:
          return None
      if started_at > 0 and mtime < started_at:
          # Stale file from a previous run — do not trust
          return None
      try:
          content = result_file.read_text(errors="replace")
      except OSError:
          return None
      upper = content.upper()
      if "EXIT_RECOMMENDATION: HALT" in upper:
          return PhaseStatus.HALT
      if "EXIT_RECOMMENDATION: CONTINUE" in upper:
          return PhaseStatus.PASS_RECOVERED
      if re.search(r"status:\s*PASS\b", content, re.IGNORECASE):
          return PhaseStatus.PASS_RECOVERED
      if re.search(r"status:\s*FAIL(?:ED|URE)?\b", content, re.IGNORECASE):
          return PhaseStatus.HALT
      if re.search(r"status:\s*PARTIAL\b", content, re.IGNORECASE):
          return PhaseStatus.INCOMPLETE
      return None
  ```
- **Acceptance**: Returns `PASS_RECOVERED` for fresh CONTINUE file; returns `None` for stale or missing file

#### T05.03: Add `_check_checkpoint_pass()` helper (SOL-C)
- **Action**: Add a new helper function near `_classify_from_result_file`. Reads checkpoint files written by the agent during execution.
- **Exact location**: `executor.py` — insert after `_classify_from_result_file`
- **Code**:
  ```python
  def _check_checkpoint_pass(config: SprintConfig, phase: Phase) -> bool:
      """Return True if the end-of-phase checkpoint file exists with status PASS."""
      checkpoint_path = config.release_dir / "checkpoints" / f"CP-P{phase.number:02d}-END.md"
      if not checkpoint_path.exists():
          return False
      try:
          content = checkpoint_path.read_text(errors="replace").upper()
          return "STATUS: PASS" in content or "**RESULT**: PASS" in content
      except OSError:
          return False
  ```
- **Acceptance**: Returns True when checkpoint file exists with PASS marker; False otherwise

#### T05.04: Add `_check_contamination()` helper (SOL-C)
- **Action**: Add contamination scanner.
- **Exact location**: `executor.py` — insert after `_check_checkpoint_pass`
- **Code**:
  ```python
  def _check_contamination(config: SprintConfig, phase: Phase) -> list[str]:
      """Return list of artifact files containing cross-phase task ID patterns."""
      import re as _re
      contaminated: list[str] = []
      artifacts_dir = config.release_dir / "artifacts"
      if not artifacts_dir.exists():
          return contaminated
      next_phase = phase.number + 1
      pattern = _re.compile(rf"T{next_phase:02d}\.\d{{2}}", _re.IGNORECASE)
      for md_file in artifacts_dir.rglob("*.md"):
          try:
              if pattern.search(md_file.read_text(errors="replace")):
                  contaminated.append(str(md_file.relative_to(config.release_dir)))
          except OSError:
              pass
      return contaminated
  ```
- **Acceptance**: Returns empty list when no contamination; returns file paths when next-phase task IDs found

#### T05.05: Add `_write_crash_recovery_log()` helper (SOL-C)
- **Action**: Add recovery log writer.
- **Exact location**: `executor.py` — insert after `_check_contamination`
- **Code**:
  ```python
  def _write_crash_recovery_log(
      config: SprintConfig,
      phase: Phase,
      contaminated: list[str],
  ) -> None:
      """Append crash recovery entry to results/crash_recovery_log.md."""
      log_path = config.results_dir / "crash_recovery_log.md"
      entry = (
          f"\n## Phase {phase.number} — PASS_RECOVERED Recovery\n"
          f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}\n"
          f"**Checkpoint**: checkpoints/CP-P{phase.number:02d}-END.md (PASS)\n"
          f"**Contamination check**: "
          + ("CLEAN" if not contaminated else f"WARNING — {len(contaminated)} file(s): {contaminated}")
          + "\n"
          f"**Action**: Phase reclassified ERROR→PASS_RECOVERED.\n"
      )
      try:
          with open(log_path, "a") as f:
              f.write(entry)
      except OSError:
          pass
  ```
- **Acceptance**: Appends to `crash_recovery_log.md`; non-fatal on write error

#### T05.06: Restructure the `if exit_code != 0` block in `_determine_phase_status`
- **Action**: Replace the early return at lines 783-784 with the ordered recovery chain. The ordering follows the adversarial-validated priority: specific detection (S2 context exhaustion) → checkpoint inference (SOL-C general) → ERROR (default).
- **Exact location**: `executor.py:783-784`
- **Current**:
  ```python
      if exit_code != 0:
          return PhaseStatus.ERROR
  ```
- **Change to**:
  ```python
      if exit_code != 0:
          # Path 1 — Specific: context exhaustion (Spec B S2)
          # detect_prompt_too_long reads NDJSON output for "Prompt is too long"
          if detect_prompt_too_long(output_file):
              # Check if the agent managed to write a result file before exhaustion
              result_status = _classify_from_result_file(result_file, started_at)
              if result_status is not None:
                  return result_status
              # No valid result file — context exhausted without completing
              return PhaseStatus.INCOMPLETE

          # Path 2 — General: checkpoint inference (Spec A SOL-C)
          # Reads agent-written checkpoint files (pre-crash evidence)
          if config is not None and phase is not None:
              if _check_checkpoint_pass(config, phase):
                  contaminated = _check_contamination(config, phase)
                  _write_crash_recovery_log(config, phase, contaminated)
                  if not contaminated:
                      return PhaseStatus.PASS_RECOVERED

          # Path 3 — Default: unchanged
          return PhaseStatus.ERROR
  ```
- **Acceptance**: (a) exit=1 + prompt-too-long + CONTINUE file → `PASS_RECOVERED`; (b) exit=1 + prompt-too-long + stale/missing file → `INCOMPLETE`; (c) exit=1 + PASS checkpoint + no contamination → `PASS_RECOVERED`; (d) exit=1 + PASS checkpoint + contamination → `ERROR`; (e) exit=1 + nothing → `ERROR`

#### T05.07: Update call site in `execute_sprint()` to pass new kwargs
- **Action**: Update the `_determine_phase_status` call at lines 659-663 to pass `config`, `phase`, and `started_at`.
- **Exact location**: `executor.py:659-663`
- **Current**:
  ```python
              status = _determine_phase_status(
                  exit_code=exit_code,
                  result_file=config.result_file(phase),
                  output_file=config.output_file(phase),
              )
  ```
- **Change to**:
  ```python
              status = _determine_phase_status(
                  exit_code=exit_code,
                  result_file=config.result_file(phase),
                  output_file=config.output_file(phase),
                  config=config,
                  phase=phase,
                  started_at=started_at.timestamp(),
              )
  ```
- **Note**: `started_at` is a `datetime` object (line 543), so `.timestamp()` converts it to a `float` for the `mtime` comparison.
- **Acceptance**: No `TypeError`; all existing tests still pass (keyword-only defaults protect backward compat)

---

### T06: Executor writes result file AFTER status determination
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/executor.py`
- **Verdict**: Redesigned per adversarial validation (option b — minimal result file from exit code + monitor state)
- **Risk**: Medium — new code path, but isolated
- **Depends on**: T05

#### T06.01: Add `_write_executor_result_file()` helper
- **Action**: Add a helper that constructs a minimal result file from phase-level data. This is NOT used by `_determine_phase_status` (which reads the agent's file). This is for downstream consumers (next sprint run, post-sprint analysis).
- **Exact location**: `executor.py` — insert near the other helper functions (before `_determine_phase_status`)
- **Code**:
  ```python
  def _write_executor_result_file(
      config: SprintConfig,
      phase: Phase,
      status: PhaseStatus,
      exit_code: int,
      monitor_state: MonitorState,
      started_at: datetime,
      finished_at: datetime,
  ) -> None:
      """Write executor-sourced result file for downstream consumers.

      This is written AFTER _determine_phase_status returns, so it does not
      create circularity. It provides a deterministic result file even when
      the agent failed to write one.
      """
      duration = (finished_at - started_at).total_seconds()
      recommendation = "CONTINUE" if status.is_success else "HALT"
      content = (
          "---\n"
          f"phase: {phase.number}\n"
          f"status: {'PASS' if status.is_success else 'FAIL'}\n"
          f"tasks_total: 1\n"
          f"tasks_passed: {1 if status.is_success else 0}\n"
          f"tasks_failed: {0 if status.is_success else 1}\n"
          "---\n"
          "\n"
          f"# Phase {phase.number} — Executor Result Report\n"
          "\n"
          f"| Phase | Status | Exit Code | Duration |\n"
          f"|-------|--------|-----------|----------|\n"
          f"| {phase.number} | {status.value} | {exit_code} | {duration:.1f}s |\n"
          "\n"
          f"**Source**: executor (not agent self-report)\n"
          f"**Output bytes**: {monitor_state.output_bytes}\n"
          f"**Last task ID**: {monitor_state.last_task_id or 'n/a'}\n"
          f"**Files changed**: {monitor_state.files_changed}\n"
          "\n"
          f"EXIT_RECOMMENDATION: {recommendation}\n"
      )
      result_path = config.result_file(phase)
      try:
          result_path.parent.mkdir(parents=True, exist_ok=True)
          result_path.write_text(content)
      except OSError:
          pass  # Non-fatal — best effort
  ```
- **Acceptance**: Result file written with correct EXIT_RECOMMENDATION; non-fatal on error

#### T06.02: Wire `_write_executor_result_file` into `execute_sprint()` AFTER status determination
- **Action**: Insert a call to `_write_executor_result_file` AFTER `_determine_phase_status` returns and AFTER the `PhaseResult` is constructed, but BEFORE the `if status.is_failure:` check. This ensures the result file exists for downstream consumers (e.g., next sprint run, diagnostic reporting) regardless of whether the agent wrote one.
- **Exact location**: `executor.py` — insert between line 663 (end of `_determine_phase_status` call) and line 665 (`# Collect stderr size`). Specifically, between the status determination and the PhaseResult construction.
- **Code**:
  ```python
              # Write executor result file for downstream consumers.
              # Written AFTER status determination to avoid circularity.
              # Overwrites any agent-written file — executor is authoritative.
              _write_executor_result_file(
                  config=config,
                  phase=phase,
                  status=status,
                  exit_code=exit_code,
                  monitor_state=monitor.state,
                  started_at=started_at,
                  finished_at=finished_at,
              )
  ```
- **Acceptance**: After every phase completion, `config.result_file(phase)` exists on disk with correct EXIT_RECOMMENDATION

---

### T07: Remove Completion Protocol from prompt + add bleed-prevention stop line
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/process.py`
- **Verdict**: AMEND — safe now that T06 provides the executor result file writer
- **Risk**: Medium — removes existing prompt content; mitigated by T06
- **Depends on**: T06

#### T07.01: Replace Completion Protocol with Scope Boundary
- **Action**: Replace the "Completion Protocol" section (lines 137-150) with a minimal "Scope Boundary" section. The agent no longer needs to write the result file (the executor does it), but still needs to know to STOP and not bleed into subsequent phases.
- **Exact location**: `process.py:137-150`
- **Current** (lines 137-150):
  ```python
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
- **Replace with**:
  ```python
              f"## Scope Boundary\n"
              f"- After completing all tasks, STOP immediately.\n"
              f"- Do not read, open, or act on any subsequent phase file.\n"
  ```
- **Note**: This removes ~12 lines and ~200 tokens from the prompt. The `result_file` variable (line 118) is still used by the executor, so it should NOT be removed from `build_prompt()` if referenced elsewhere. However, since it's only used in the Completion Protocol text, and we're removing that, the `result_file` local variable at line 118 becomes dead code. Remove it.
- **Acceptance**: `build_prompt()` output contains "Scope Boundary" and "STOP immediately"; does NOT contain "Completion Protocol" or "EXIT_RECOMMENDATION"

#### T07.02: Remove dead `result_file` variable from `build_prompt()`
- **Action**: The variable `result_file = self.config.result_file(self.phase)` at line 118 is now dead code (only used in the removed Completion Protocol text). Remove it.
- **Exact location**: `process.py:118`
- **Current**: `result_file = self.config.result_file(self.phase)`
- **Action**: Delete this line
- **Acceptance**: `ruff check` reports no unused variables in `build_prompt`

---

## Phase 3: Prevention Layer

### T08: Phase-specific directory isolation + summary header
- **Tier**: STRICT
- **File**: `src/superclaude/cli/sprint/executor.py`, `src/superclaude/cli/sprint/process.py`
- **Verdict**: CONFIRMED by adversarial validation
- **Risk**: Medium — touches execution loop, but isolated
- **Depends on**: nothing (independent)

#### T08.01: Design note — deferred
- **Action**: This task (S3 directory isolation) is a substantial feature from Spec B that requires detailed design for: (a) isolation directory lifecycle, (b) phase file copying, (c) scoped work directory for ClaudeProcess, (d) cleanup in finally block, (e) orphan cleanup at sprint startup, (f) summary header in build_prompt. This is a **deferred task** — it should be implemented in a follow-up sprint after the core recovery logic (T01-T07) is validated. The adversarial validation confirmed it is fully independent and can be added later without conflict.
- **Acceptance**: Design doc created for follow-up implementation. No code changes in this tasklist.

---

## Phase 4: Tests

### T09: Test suite for all changes
- **Tier**: STRICT
- **File**: `tests/sprint/test_phase8_halt_fix.py` (new file, in existing `tests/sprint/` directory following project convention)
- **Risk**: Low — additive test code only
- **Depends on**: T01-T07

#### T09.01: Test `PASS_RECOVERED` enum properties
- **Test**: Verify `PhaseStatus.PASS_RECOVERED` has correct property values.
- **Code**:
  ```python
  def test_pass_recovered_properties():
      """PASS_RECOVERED: is_terminal=True, is_success=True, is_failure=False."""
      s = PhaseStatus.PASS_RECOVERED
      assert s.value == "pass_recovered"
      assert s.is_terminal is True
      assert s.is_success is True
      assert s.is_failure is False
  ```
- **Acceptance**: Test passes

#### T09.02: Test `detect_prompt_too_long()` positive match
- **Test**: Write a file with `"Prompt is too long"` in the last 10 lines; verify detection.
- **Code**:
  ```python
  def test_detect_prompt_too_long_positive(tmp_path):
      """detect_prompt_too_long returns True when pattern present."""
      output = tmp_path / "output.jsonl"
      output.write_text('{"type":"error","error":{"type":"invalid_request_error","message":"Prompt is too long"}}\n')
      from superclaude.cli.sprint.monitor import detect_prompt_too_long
      assert detect_prompt_too_long(output) is True
  ```
- **Acceptance**: Test passes

#### T09.03: Test `detect_prompt_too_long()` negative (clean output)
- **Test**: Write a clean output file; verify no false positive.
- **Code**:
  ```python
  def test_detect_prompt_too_long_negative(tmp_path):
      """detect_prompt_too_long returns False on clean output."""
      output = tmp_path / "output.jsonl"
      output.write_text('{"type":"assistant","content":"hello"}\n')
      from superclaude.cli.sprint.monitor import detect_prompt_too_long
      assert detect_prompt_too_long(output) is False
  ```
- **Acceptance**: Test passes

#### T09.04: Test exit=1 + prompt-too-long + CONTINUE file → `PASS_RECOVERED`
- **Test**: Context exhaustion recovery path.
- **Code**:
  ```python
  def test_context_exhaustion_recovery(tmp_path):
      """exit=1 + prompt-too-long + fresh CONTINUE file → PASS_RECOVERED."""
      import time
      result_file = tmp_path / "result.md"
      output_file = tmp_path / "output.jsonl"
      output_file.write_text('{"error":{"message":"Prompt is too long"}}\n')
      started_at = time.time() - 10  # 10 seconds ago
      result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
      status = _determine_phase_status(
          exit_code=1,
          result_file=result_file,
          output_file=output_file,
          started_at=started_at,
      )
      assert status == PhaseStatus.PASS_RECOVERED
  ```
- **Acceptance**: Test passes

#### T09.05: Test exit=1 + prompt-too-long + stale mtime → `INCOMPLETE`
- **Test**: Stale result file should not be trusted.
- **Code**:
  ```python
  def test_context_exhaustion_stale_file(tmp_path):
      """exit=1 + prompt-too-long + stale file → INCOMPLETE."""
      import os, time
      result_file = tmp_path / "result.md"
      output_file = tmp_path / "output.jsonl"
      output_file.write_text('{"error":{"message":"Prompt is too long"}}\n')
      result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
      # Make file appear to be from before the phase started
      old_time = time.time() - 3600
      os.utime(result_file, (old_time, old_time))
      started_at = time.time() - 10  # phase started 10s ago, file is 1h old
      status = _determine_phase_status(
          exit_code=1,
          result_file=result_file,
          output_file=output_file,
          started_at=started_at,
      )
      assert status == PhaseStatus.INCOMPLETE
  ```
- **Acceptance**: Test passes

#### T09.06: Test exit=1 + PASS checkpoint + no contamination → `PASS_RECOVERED`
- **Test**: SOL-C checkpoint inference path.
- **Code**:
  ```python
  def test_checkpoint_inference_pass(tmp_path):
      """exit=1 + PASS checkpoint + no contamination → PASS_RECOVERED."""
      config = _make_config(tmp_path)
      phase = config.phases[0]
      # Create checkpoint file with PASS
      cp_dir = tmp_path / "checkpoints"
      cp_dir.mkdir()
      cp_file = cp_dir / f"CP-P{phase.number:02d}-END.md"
      cp_file.write_text("## Checkpoint\n**RESULT**: PASS\n")
      result_file = tmp_path / "result.md"
      output_file = tmp_path / "output.jsonl"
      output_file.write_text('{"type":"assistant"}\n')
      status = _determine_phase_status(
          exit_code=1,
          result_file=result_file,
          output_file=output_file,
          config=config,
          phase=phase,
      )
      assert status == PhaseStatus.PASS_RECOVERED
  ```
- **Acceptance**: Test passes

#### T09.07: Test exit=1 + PASS checkpoint + contamination → `ERROR`
- **Test**: Contamination guard prevents false recovery.
- **Code**:
  ```python
  def test_checkpoint_inference_contaminated(tmp_path):
      """exit=1 + PASS checkpoint + contamination → ERROR."""
      config = _make_config(tmp_path)
      phase = config.phases[0]
      # Create checkpoint with PASS
      cp_dir = tmp_path / "checkpoints"
      cp_dir.mkdir()
      cp_file = cp_dir / f"CP-P{phase.number:02d}-END.md"
      cp_file.write_text("STATUS: PASS\n")
      # Create contaminated artifact
      art_dir = tmp_path / "artifacts"
      art_dir.mkdir()
      (art_dir / "test.md").write_text("Working on T02.01 task\n")
      result_file = tmp_path / "result.md"
      output_file = tmp_path / "output.jsonl"
      output_file.write_text('{"type":"assistant"}\n')
      status = _determine_phase_status(
          exit_code=1,
          result_file=result_file,
          output_file=output_file,
          config=config,
          phase=phase,
      )
      assert status == PhaseStatus.ERROR
  ```
- **Acceptance**: Test passes

#### T09.08: Test fidelity fail without override → SystemExit
- **Test**: Preflight blocks on fidelity failure.
- **Code**:
  ```python
  def test_fidelity_blocks(tmp_path):
      """fidelity_status=fail without override → blocked."""
      import json
      state_file = tmp_path / ".roadmap-state.json"
      state_file.write_text(json.dumps({"fidelity_status": "fail"}))
      from superclaude.cli.sprint.commands import _check_fidelity
      blocked, msg = _check_fidelity(tmp_path / "index.md")
      assert blocked is True
      assert "FAILED" in msg
  ```
- **Acceptance**: Test passes

#### T09.09: Test fidelity pass → not blocked
- **Test**: No block when fidelity passes.
- **Code**:
  ```python
  def test_fidelity_passes(tmp_path):
      """fidelity_status=pass → not blocked."""
      import json
      state_file = tmp_path / ".roadmap-state.json"
      state_file.write_text(json.dumps({"fidelity_status": "pass"}))
      from superclaude.cli.sprint.commands import _check_fidelity
      blocked, _ = _check_fidelity(tmp_path / "index.md")
      assert blocked is False
  ```
- **Acceptance**: Test passes

#### T09.10: Test `_write_executor_result_file()` produces valid output
- **Test**: Verify executor result file contains EXIT_RECOMMENDATION.
- **Code**:
  ```python
  def test_executor_result_file(tmp_path):
      """Executor result file contains correct EXIT_RECOMMENDATION."""
      config = _make_config(tmp_path)
      phase = config.phases[0]
      from superclaude.cli.sprint.executor import _write_executor_result_file
      from superclaude.cli.sprint.models import MonitorState
      ms = MonitorState()
      now = datetime.now(timezone.utc)
      _write_executor_result_file(
          config=config, phase=phase, status=PhaseStatus.PASS,
          exit_code=0, monitor_state=ms, started_at=now, finished_at=now,
      )
      content = config.result_file(phase).read_text()
      assert "EXIT_RECOMMENDATION: CONTINUE" in content
  ```
- **Acceptance**: Test passes

#### T09.11: Test `FailureCategory.CONTEXT_EXHAUSTION` value
- **Test**: Verify enum value exists.
- **Code**:
  ```python
  def test_failure_category_context_exhaustion():
      """FailureCategory.CONTEXT_EXHAUSTION exists."""
      from superclaude.cli.sprint.diagnostics import FailureCategory
      assert FailureCategory.CONTEXT_EXHAUSTION.value == "context_exhaustion"
  ```
- **Acceptance**: Test passes

#### T09.12: Test backward compatibility of `_determine_phase_status` 3-arg call
- **Test**: Verify existing 3-arg calls still work (keyword-only defaults).
- **Code**:
  ```python
  def test_determine_phase_status_backward_compat(tmp_path):
      """3-arg call continues to work (keyword-only defaults)."""
      result_file = tmp_path / "result.md"
      output_file = tmp_path / "output.jsonl"
      output_file.write_text("some output")
      # 3-arg call should not raise TypeError
      status = _determine_phase_status(
          exit_code=0,
          result_file=result_file,
          output_file=output_file,
      )
      assert status == PhaseStatus.PASS_NO_REPORT
  ```
- **Acceptance**: Test passes

---

## Phase 5: Integration Verification

### T10: Lint, format, and full test suite
- **Tier**: STRICT
- **File**: N/A — verification only
- **Depends on**: T09

#### T10.01: Ruff lint check
- **Command**: `uv run ruff check src/superclaude/cli/sprint/`
- **Acceptance**: Zero errors

#### T10.02: Ruff format check
- **Command**: `uv run ruff format --check src/superclaude/cli/sprint/`
- **Acceptance**: All files formatted

#### T10.03: Full test suite
- **Command**: `uv run pytest tests/sprint/ -v --tb=short`
- **Acceptance**: All existing tests pass; all 12 new tests pass

#### T10.04: New test file specifically
- **Command**: `uv run pytest tests/sprint/test_phase8_halt_fix.py -v`
- **Acceptance**: 12/12 tests pass

---

## Summary

### Files Modified

| File | Changes |
|------|---------|
| `src/superclaude/cli/sprint/models.py` | Add `PASS_RECOVERED` to `PhaseStatus` enum, `is_terminal`, `is_success` |
| `src/superclaude/cli/sprint/monitor.py` | Add `PROMPT_TOO_LONG_PATTERN`, `detect_prompt_too_long()` |
| `src/superclaude/cli/sprint/executor.py` | Add import of `detect_prompt_too_long`; add helpers `_classify_from_result_file`, `_check_checkpoint_pass`, `_check_contamination`, `_write_crash_recovery_log`, `_write_executor_result_file`; restructure `_determine_phase_status` with recovery chain; update call site with new kwargs; wire `_write_executor_result_file` into execution loop |
| `src/superclaude/cli/sprint/process.py` | Replace Completion Protocol with Scope Boundary; remove dead `result_file` variable |
| `src/superclaude/cli/sprint/commands.py` | Add `_check_fidelity()` helper; add `--force-fidelity-fail` option; wire preflight check |
| `src/superclaude/cli/sprint/diagnostics.py` | Add `CONTEXT_EXHAUSTION` to `FailureCategory`; update `FailureClassifier.classify()` |
| `tests/sprint/test_phase8_halt_fix.py` | New file: 12 test cases |

### Files NOT Modified
- `config.py`, `tui.py`, `logger.py`, `tmux.py`, `debug_logger.py`
- Any `.md` tasklist files, agent skills, or commands

### Deferred to Follow-Up
- T08: Phase-specific directory isolation + summary header (Spec B S3) — fully independent, substantial feature, confirmed by adversarial validation as safe to defer

### Key Adversarial Corrections Applied
1. **Step 2 redesigned**: Executor writes result file AFTER `_determine_phase_status` (not before), eliminating circularity
2. **Minimal result file**: Uses exit code + `MonitorState` instead of non-existent `task_results` data
3. **Insertion points corrected**: Commands.py fidelity check after line 160 (not in empty gap)
4. **SOL-C elevated**: Checkpoint inference is the only pre-crash evidence reader, not merely a "last resort"
