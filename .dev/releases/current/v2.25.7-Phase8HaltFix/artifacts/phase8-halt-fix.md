# Implementation Workflow: Phase 8 Sprint Halt Fix

**Source Analysis**: `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/phase8-halt-analysis.md`
**Generated**: 2026-03-15
**Strategy**: Systematic — ordered by dependency, lowest-risk first
**Scope**: `src/superclaude/cli/sprint/` subsystem only

---

## Summary of Changes

| Solution | Root Cause | File(s) | Risk |
|---|---|---|---|
| SOL-D | RC-003 (proximate) | `executor.py` | Low |
| SOL-A | RC-001 (bleed prevention) | `executor.py` or `config.py` | Low |
| SOL-C | RC-001 (primary) | `executor.py`, `models.py` | Medium |
| SOL-G | RC-002 (enabling) | `commands.py` | Low |

**Dependency order**: SOL-D must precede SOL-C (SOL-C's fallback logic depends on understanding the result file state that SOL-D normalizes). SOL-A is independent. SOL-G is fully independent.

---

## Phase 1 — SOL-D: Atomic Result File Pre-Write

**Goal**: Before launching each phase subprocess, pre-write `results/phase-{N}-result.md` with `EXIT_RECOMMENDATION: HALT` as a dead-man's switch. Agent overwrites with `CONTINUE` on success; crash-before-overwrite → correct HALT preserved.

### Step 1.1 — Read `executor.py` execution loop

Read `src/superclaude/cli/sprint/executor.py` lines 540–700 to locate the exact position in the execution loop where `ClaudeProcess` / the subprocess is launched, before the `proc_manager` poll loop.

**Acceptance criteria**: Identify the line number where subprocess launch begins (before `proc_manager._process.wait()` or equivalent poll loop).

### Step 1.2 — Implement `_pre_write_result_file(config, phase)` helper

Add a new private function in `executor.py`:

```python
def _pre_write_result_file(config: SprintConfig, phase: Phase) -> None:
    """Pre-write result file with HALT default before subprocess launch.

    Uses write-then-rename for atomicity. If the pre-write fails (e.g.
    disk full), log a warning but do not abort — the existing behavior
    (no result file → ERROR on non-zero exit) is preserved.
    """
    import tempfile
    result_path = config.result_file(phase)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    content = "EXIT_RECOMMENDATION: HALT\n# Pre-written by executor; agent must overwrite with CONTINUE.\n"
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=result_path.parent,
            delete=False,
            suffix=".tmp",
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, result_path)
    except OSError as exc:
        import sys
        print(f"[WARN] pre-write result file failed: {exc}", file=sys.stderr)
```

**Acceptance criteria**:
- Function exists in `executor.py`
- Uses `tempfile.NamedTemporaryFile` + `os.replace` (not direct open/write)
- Catches `OSError` and logs warning without aborting
- Pre-written file contains `EXIT_RECOMMENDATION: HALT`

### Step 1.3 — Call `_pre_write_result_file` before subprocess launch

In the execution loop in `executor.py`, insert a call to `_pre_write_result_file(config, phase)` immediately before the subprocess is launched (before `ClaudeProcess` is started or the equivalent launch call).

**Acceptance criteria**:
- Call occurs before any subprocess `wait()` / poll loop
- Call occurs after `results_dir` is guaranteed to exist
- No change to subprocess launch logic itself

### Step 1.4 — Verify `config.result_file(phase)` method exists

Check `SprintConfig` (in `models.py`) for a `result_file(phase)` method. If it does not exist, locate the equivalent expression (e.g., `config.results_dir / f"phase-{phase.number}-result.md"`) and use that directly in `_pre_write_result_file`.

**Acceptance criteria**: Pre-write writes to the same path that `_determine_phase_status` reads from.

---

## Phase 2 — SOL-A: Phase Prompt Hard Stop Instruction

**Goal**: Append a mandatory boundary instruction to every phase prompt, making the result file write and session stop explicit and salient at the end of the agent's task list.

### Step 2.1 — Locate phase prompt assembly

Search `executor.py` and `config.py` for the function or code block that constructs the prompt passed to the Claude subprocess. Look for string concatenation or template formatting involving phase file content.

**Acceptance criteria**: Identify the exact line/function where phase content becomes the subprocess prompt string.

### Step 2.2 — Implement `_append_phase_stop_instruction(prompt, phase, config)` helper

Add a helper that appends a formatted stop block to the assembled phase prompt:

```python
def _append_phase_stop_instruction(prompt: str, phase: Phase, config: SprintConfig) -> str:
    """Append mandatory boundary instruction to phase prompt."""
    result_path = config.result_file(phase)  # or equivalent expression
    stop_block = (
        "\n\n---\n"
        "## MANDATORY FINAL STEP — DO NOT SKIP\n\n"
        f"After completing ALL tasks in Phase {phase.number}:\n\n"
        f"1. Write `{result_path}` containing exactly:\n"
        "   ```\n"
        "   EXIT_RECOMMENDATION: CONTINUE\n"
        "   ```\n"
        "2. **STOP immediately.** Do not read, open, or act on any subsequent "
        "phase file. Your session ends here.\n"
    )
    return prompt + stop_block
```

**Acceptance criteria**:
- Function appended to prompt string (not prepended — must appear after task content)
- Result file path is resolved per-phase (not hardcoded)
- Stop instruction is visually distinct (heading + numbered steps)

### Step 2.3 — Wire `_append_phase_stop_instruction` into prompt assembly

Call the helper at the point identified in Step 2.1, wrapping the final prompt before it is passed to the subprocess.

**Acceptance criteria**:
- Every phase gets the stop instruction appended
- Dry-run mode (`config.dry_run`) still appends the instruction (it's part of the prompt spec)
- No change to any other prompt content

---

## Phase 3 — SOL-C: Checkpoint-to-Result Inference Fallback

**Goal**: When `exit_code≠0`, check for a PASS checkpoint + all deliverables before unconditionally returning `ERROR`. Reclassify to `PASS_WITH_WARNINGS` if evidence confirms completion. Includes contamination check for cross-phase task ID patterns.

**Depends on**: Phase 1 (SOL-D) complete — understanding result file pre-write state is necessary context.

### Step 3.1 — Add `PASS_WITH_WARNINGS` to `PhaseStatus` enum

In `src/superclaude/cli/sprint/models.py`, add to the `PhaseStatus` enum:

```python
PASS_WITH_WARNINGS = "pass_with_warnings"
```

Update `is_terminal` to include `PASS_WITH_WARNINGS`. Update `is_success` to include `PASS_WITH_WARNINGS`. Update `is_failure` to **not** include `PASS_WITH_WARNINGS`.

**Acceptance criteria**:
- `PhaseStatus.PASS_WITH_WARNINGS` exists with value `"pass_with_warnings"`
- `PhaseStatus.PASS_WITH_WARNINGS.is_terminal` → `True`
- `PhaseStatus.PASS_WITH_WARNINGS.is_success` → `True`
- `PhaseStatus.PASS_WITH_WARNINGS.is_failure` → `False`

### Step 3.2 — Implement `_check_checkpoint_pass(config, phase)` helper

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

**Acceptance criteria**:
- Checks path `checkpoints/CP-P{N:02d}-END.md` relative to `release_dir`
- Returns False if file missing or unreadable
- Returns True only if content contains a PASS status marker
- Case-insensitive check

### Step 3.3 — Implement `_check_contamination(config, phase)` helper

```python
import re as _re

def _check_contamination(config: SprintConfig, phase: Phase) -> list[str]:
    """Return list of artifact files containing cross-phase task ID patterns.

    Checks all .md files in the artifacts directory for references to task IDs
    from phases later than phase.number (e.g., T09.xx in Phase 8 artifacts).
    Returns empty list if no contamination found.
    """
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

**Acceptance criteria**:
- Scans `artifacts/` subtree for `.md` files only
- Pattern is `T{N+1:02d}.\d{2}` (next phase task IDs)
- Returns list of relative paths (not full paths)
- Returns empty list if `artifacts/` does not exist

### Step 3.4 — Implement `_write_crash_recovery_log(config, phase, contaminated)` helper

```python
def _write_crash_recovery_log(
    config: SprintConfig,
    phase: Phase,
    contaminated: list[str],
) -> None:
    """Write crash_recovery_log.md to results dir for post-sprint review."""
    from datetime import datetime, timezone
    log_path = config.results_dir / "crash_recovery_log.md"
    entry = (
        f"\n## Phase {phase.number} — PASS_WITH_WARNINGS Recovery\n"
        f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}\n"
        f"**Checkpoint**: checkpoints/CP-P{phase.number:02d}-END.md (PASS)\n"
        f"**Contamination check**: "
        + (f"CLEAN" if not contaminated else f"WARNING — {len(contaminated)} file(s): {contaminated}")
        + "\n"
        f"**Action**: Phase reclassified ERROR→PASS_WITH_WARNINGS. Review before proceeding.\n"
    )
    try:
        with open(log_path, "a") as f:
            f.write(entry)
    except OSError:
        pass  # Non-fatal — log failure should not abort sprint
```

**Acceptance criteria**:
- Appends (not overwrites) to `results/crash_recovery_log.md`
- Records phase number, timestamp, contamination result
- Non-fatal on OSError

### Step 3.5 — Modify `_determine_phase_status` to use inference fallback

Update `_determine_phase_status` in `executor.py`. The current early-return on `exit_code != 0` must be replaced with a fallback check:

**Before** (current):
```python
if exit_code != 0:
    return PhaseStatus.ERROR
```

**After**:
```python
if exit_code != 0:
    # Attempt checkpoint-presence inference before declaring ERROR
    if _check_checkpoint_pass(config, phase):
        contaminated = _check_contamination(config, phase)
        _write_crash_recovery_log(config, phase, contaminated)
        if contaminated:
            # Contamination detected — do not promote; stay as ERROR
            return PhaseStatus.ERROR
        return PhaseStatus.PASS_WITH_WARNINGS
    return PhaseStatus.ERROR
```

**Note**: `_determine_phase_status` must accept `config` and `phase` as additional parameters, or the helpers must be called from the call site in the execution loop instead, passing results in. Choose whichever requires fewer signature changes.

**Acceptance criteria**:
- Non-zero exit with PASS checkpoint + no contamination → `PASS_WITH_WARNINGS`
- Non-zero exit with PASS checkpoint + contamination → `ERROR` (not promoted)
- Non-zero exit with no checkpoint → `ERROR` (unchanged behavior)
- Zero exit → existing logic unchanged
- `crash_recovery_log.md` written in all PASS_WITH_WARNINGS cases

### Step 3.6 — Update call sites for `_determine_phase_status`

`_determine_phase_status` is called at approximately `executor.py:659`. Update the call to pass `config` and `phase` if the signature was extended, or verify the helpers are called from the call site instead.

**Acceptance criteria**: No `TypeError` on call; existing test mocks do not break.

---

## Phase 4 — SOL-G: Preflight Fidelity Block

**Goal**: At sprint start, check `.roadmap-state.json` for `tasklist_ready: false`. If found, print HIGH severity deviations and abort unless `--force-fidelity-fail` is provided.

**Depends on**: None (fully independent).

### Step 4.1 — Implement `_check_fidelity(index_path)` helper in `commands.py`

```python
def _check_fidelity(index_path: Path) -> tuple[bool, str]:
    """Check sprint dir for spec-fidelity fail state.

    Returns (blocked: bool, message: str).
    blocked=True means execution should be blocked.
    """
    import json
    sprint_dir = index_path.parent
    state_file = sprint_dir / ".roadmap-state.json"
    if not state_file.exists():
        return False, ""

    try:
        state = json.loads(state_file.read_text())
    except (json.JSONDecodeError, OSError):
        return False, ""

    fidelity_status = state.get("fidelity_status", "")
    steps = state.get("steps", {})
    spec_fidelity_step = steps.get("spec-fidelity", {})
    tasklist_ready = spec_fidelity_step.get("output_file")  # path to spec-fidelity.md

    if fidelity_status != "fail":
        return False, ""

    # Read HIGH severity deviations from spec-fidelity.md if available
    deviations_summary = ""
    if tasklist_ready:
        fidelity_file = Path(tasklist_ready)
        if fidelity_file.exists():
            lines = fidelity_file.read_text(errors="replace").splitlines()
            high_lines = [l for l in lines if "HIGH" in l or "### DEV-" in l][:20]
            deviations_summary = "\n".join(high_lines)

    msg = (
        f"Sprint blocked: spec-fidelity check FAILED (fidelity_status=fail).\n"
        f"The tasklist was generated from a spec with unresolved HIGH severity deviations:\n"
        f"{deviations_summary or '(see spec-fidelity.md for details)'}\n\n"
        f"To override: add --force-fidelity-fail '<justification>' to your command."
    )
    return True, msg
```

**Acceptance criteria**:
- Returns `(False, "")` if `.roadmap-state.json` absent or `fidelity_status != "fail"`
- Returns `(True, message)` with deviation summary if `fidelity_status == "fail"`
- Does not crash on missing/malformed `.roadmap-state.json`

### Step 4.2 — Add `--force-fidelity-fail` CLI option to `run` command

In `commands.py`, add to the `run` Click command:

```python
@click.option(
    "--force-fidelity-fail",
    "force_fidelity_fail",
    default="",
    help="Override fidelity block. Provide non-empty justification string.",
)
```

Pass through to `run()` function signature.

**Acceptance criteria**:
- `--force-fidelity-fail ""` (empty string) does NOT override (treated as not provided)
- `--force-fidelity-fail "reason"` (non-empty) overrides the block
- Option is hidden from help unless needed (add `hidden=False` for discoverability)

### Step 4.3 — Wire fidelity check into `run()` before execution

In the `run()` function body, after `config = load_sprint_config(...)` and before the tmux/execution branch:

```python
# Preflight: fidelity block
blocked, fidelity_msg = _check_fidelity(index_path)
if blocked:
    if not force_fidelity_fail:
        click.echo(fidelity_msg, err=True)
        raise SystemExit(1)
    else:
        # Log override to execution log
        logger.log_event("fidelity_override", justification=force_fidelity_fail)
        click.echo(
            f"[WARN] Fidelity block overridden: {force_fidelity_fail}",
            err=True,
        )
```

**Acceptance criteria**:
- `fidelity_status=fail` without `--force-fidelity-fail` → sprint aborts with exit 1 and deviation list printed
- `fidelity_status=fail` with `--force-fidelity-fail "reason"` → sprint proceeds with warning logged
- `fidelity_status` absent or `pass` → no effect

---

## Phase 5 — Tests

**Goal**: Cover all 6 required test scenarios. Tests go in a new file `tests/cli_portify/test_phase8_halt_fix.py` (following existing test file naming in that directory).

### Step 5.1 — Test (a): PASS_WITH_WARNINGS reclassification

```python
def test_pass_with_warnings_on_checkpoint_and_deliverables():
    """exit_code=1 + PASS checkpoint + no contamination → PASS_WITH_WARNINGS"""
    # Setup: write checkpoint with STATUS: PASS, no T09.xx in artifacts
    # Call: _determine_phase_status(exit_code=1, ...)
    # Assert: PhaseStatus.PASS_WITH_WARNINGS
```

### Step 5.2 — Test (b): Contamination blocks PASS_WITH_WARNINGS

```python
def test_contamination_blocks_pass_with_warnings():
    """exit_code=1 + PASS checkpoint + T09.xx found in artifacts → ERROR"""
    # Setup: write T09.01 in an artifact .md file
    # Assert: PhaseStatus.ERROR (not promoted despite PASS checkpoint)
```

### Step 5.3 — Test (c): Pre-write HALT default on crash

```python
def test_prewrite_halt_default():
    """Pre-written result file contains EXIT_RECOMMENDATION: HALT"""
    # Call _pre_write_result_file(config, phase)
    # Assert: result_file_path.read_text() contains "EXIT_RECOMMENDATION: HALT"
```

### Step 5.4 — Test (d): CONTINUE preserved on overwrite

```python
def test_continue_preserved_on_overwrite():
    """Agent overwriting with CONTINUE is read as PASS by _determine_phase_status"""
    # Pre-write HALT, then overwrite with CONTINUE + exit_code=0
    # Assert: PhaseStatus.PASS
```

### Step 5.5 — Test (e): Preflight block on fidelity fail

```python
def test_preflight_blocks_on_fidelity_fail(tmp_path):
    """fidelity_status=fail without override → SystemExit(1)"""
    # Write .roadmap-state.json with fidelity_status: fail
    # Invoke run() without --force-fidelity-fail
    # Assert: SystemExit(1) raised
```

### Step 5.6 — Test (f): `--force-fidelity-fail` override

```python
def test_force_fidelity_fail_override(tmp_path):
    """fidelity_status=fail with --force-fidelity-fail <reason> → proceeds"""
    # Write .roadmap-state.json with fidelity_status: fail
    # Invoke run() with force_fidelity_fail="test justification"
    # Assert: no SystemExit; override logged
```

**Acceptance criteria for all tests**:
- Each test is isolated (uses `tmp_path` or mocks)
- No real subprocess launched in any test
- Tests runnable via `uv run pytest tests/cli_portify/test_phase8_halt_fix.py -v`

---

## Phase 6 — Integration Verification

### Step 6.1 — Dry-run smoke test

```bash
uv run python -m superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --dry-run --start 8 --end 8
```

**Acceptance criteria**: Dry-run shows Phase 8 with stop instruction in prompt preview; no error on fidelity check (`.roadmap-state.json` fidelity_status=fail will trigger the block — expected).

### Step 6.2 — Lint and typecheck

```bash
uv run ruff check src/superclaude/cli/sprint/
uv run ruff format --check src/superclaude/cli/sprint/
```

**Acceptance criteria**: Zero new lint errors introduced.

### Step 6.3 — Full test suite

```bash
uv run pytest tests/ -v --tb=short
```

**Acceptance criteria**: All existing tests pass; 6 new tests pass.

---

## Dependency Graph

```
Phase 1 (SOL-D: pre-write)
    │
    ├─→ Phase 2 (SOL-A: prompt stop) [independent, can run parallel]
    │
    └─→ Phase 3 (SOL-C: inference fallback) [depends on P1 context]
            │
            └─→ Phase 5 (Tests) [depends on P1+P2+P3+P4]

Phase 4 (SOL-G: fidelity block) [fully independent]
    │
    └─→ Phase 5 (Tests)

Phase 6 (Integration) [depends on P5]
```

**Recommended execution order**: P1 → P2 (parallel with P4) → P3 → P5 → P6

---

## Risk Register

| Risk | Mitigation |
|---|---|
| SOL-C false positive: checkpoint PASS but phase work incomplete | Contamination check guards against cross-phase state; log always written for human review |
| SOL-D partial write corruption | `tempfile` + `os.replace` is atomic on POSIX; Windows `os.replace` is not fully atomic but acceptable for this use case |
| SOL-G blocks legitimate re-runs | `--force-fidelity-fail` escape hatch; justification logged for audit |
| `_determine_phase_status` signature change breaks existing tests | Pass `config`/`phase` as keyword args with defaults; verify existing mock compatibility in Step 3.6 |
| `PASS_WITH_WARNINGS` not handled by TUI/logger | Verify `SprintLogger.write_phase_result` and `SprintTUI.update` handle unknown enum values gracefully before adding new status |

---

## Files Modified

| File | Change |
|---|---|
| `src/superclaude/cli/sprint/executor.py` | Add `_pre_write_result_file`, `_append_phase_stop_instruction`, `_check_checkpoint_pass`, `_check_contamination`, `_write_crash_recovery_log`; modify `_determine_phase_status`; wire all into execution loop |
| `src/superclaude/cli/sprint/models.py` | Add `PASS_WITH_WARNINGS` to `PhaseStatus`; update `is_terminal`, `is_success`, `is_failure` |
| `src/superclaude/cli/sprint/commands.py` | Add `--force-fidelity-fail` option; add `_check_fidelity` helper; wire preflight check |
| `tests/cli_portify/test_phase8_halt_fix.py` | New file: 6 test cases |

**No changes to**: `config.py`, `models.py` (beyond PhaseStatus), `monitor.py`, `process.py`, `tui.py`, any agent skills/commands, any `.md` tasklist files.
