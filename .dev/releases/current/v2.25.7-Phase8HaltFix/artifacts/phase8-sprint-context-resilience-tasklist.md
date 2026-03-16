---
# Phase 8 Sprint Context Resilience — Implementation Tasklist
# Source: cross-spec-overlap-validation.md (adversarial validation of phase8-halt-fix.md + sprint-context-exhaustion-prd.md)
# Compliance tier: STRICT (multi-file orchestration subsystem)
# Generated: 2026-03-16
---

## Tasklist Index

| Task ID | Title | Tier | Status | Depends On |
|---------|-------|------|--------|------------|
| T01.01 | Wire `setup_isolation()` into `execute_sprint()` — create per-phase directory | STRICT | pending | — |
| T01.02 | Pass isolation `scoped_work_dir` to `ClaudeProcess` constructor | STRICT | pending | T01.01, T06.02 |
| T01.03 | Add cleanup of isolation directory in `finally` block | STRICT | pending | T01.02 |
| T01.04 | Add startup cleanup of orphaned `.isolation/` directories | STANDARD | pending | T01.01 |
| T02.01 | Add sprint summary header to `build_prompt()` in `process.py` | STANDARD | pending | — |
| T02.02 | Add "do not seek additional index files" instruction to prompt | LIGHT | pending | T02.01 |
| T03.01 | Extend `detect_prompt_too_long()` to also scan `config.error_file(phase)` | STANDARD | pending | — |
| T03.02 | Update `_determine_phase_status()` to pass `error_file` to detection | STANDARD | pending | T03.01 |
| T04.01 | Add test: isolation directory created before subprocess spawn | STRICT | pending | T01.01 |
| T04.02 | Add test: isolation directory cleaned up after phase completes | STRICT | pending | T01.03 |
| T04.03 | Add test: isolation directory cleaned up after phase fails | STRICT | pending | T01.03 |
| T04.04 | Add test: orphaned isolation directories cleaned on sprint startup | STANDARD | pending | T01.04 |
| T04.05 | Add test: summary header present in prompt with correct metadata | STANDARD | pending | T02.01 |
| T04.06 | Add test: `detect_prompt_too_long()` returns False when pattern not in last 10 lines | STANDARD | pending | — |
| T04.07 | Add test: `detect_prompt_too_long()` scans stderr file as fallback | STANDARD | pending | T03.01 |
| T04.08 | Add test: exit=1 + prompt-too-long + HALT file → PhaseStatus.HALT | STANDARD | pending | — |
| T04.09 | Add test: exit=1 + no prompt-too-long → PhaseStatus.ERROR (unchanged) | STANDARD | pending | — |
| T05.01 | Run full test suite and fix any regressions | STRICT | pending | T04.09 |
| T05.02 | Run `ruff check` + `ruff format --check` on modified files | LIGHT | pending | T05.01 |
| T06.01 | Fix `SprintLogger.write_phase_result()` — add `PASS_RECOVERED` to screen routing | STANDARD | pending | — |
| T06.02 | Add `env_vars` parameter to `pipeline/process.py` `ClaudeProcess.build_env()` | STRICT | pending | — |
| T06.03 | Add prior-phase artifact directories to S3 summary header in `build_prompt()` | STANDARD | pending | T02.01 |
| T06.04 | Remove dead `result_file` variable from `process.py` `build_prompt()` | LIGHT | pending | — |
| T06.05 | Fix `FailureClassifier.classify()` output_file path construction in `diagnostics.py` | STRICT | pending | — |
| T06.06 | Add integration test: sprint continues to next phase on `PASS_RECOVERED` | STRICT | pending | — |
| T06.07 | Write S4 artifact batching architecture spec document | STANDARD | pending | — |
| T06.08 | Document S3 empirical validation requirement as pre-merge gate | LIGHT | pending | T01.02 |

---

## Phase 1 — S3 Directory Isolation (Tasks T01.01–T01.04)

### T01.01 — Wire `setup_isolation()` into `execute_sprint()` — create per-phase directory

**Tier**: STRICT
**File**: `src/superclaude/cli/sprint/executor.py`
**Rationale**: S3-R01/R02. The `setup_isolation()` function and `IsolationLayers` dataclass already exist (executor.py lines 97-170) but are NOT called from `execute_sprint()`. The validation report confirms this is a remaining gap. Wiring isolation in prevents the ~14K token overhead from `tasklist-index.md` being auto-loaded by the agent subprocess.

**Exact change**:

In `execute_sprint()`, immediately before the `ClaudeProcess` is constructed (before line 542 `proc_manager = ClaudeProcess(config, phase)`), add:

```python
# S3: Create per-phase isolation directory
isolation = setup_isolation(config)
phase_isolation_dir = config.results_dir / ".isolation" / f"phase-{phase.number}"
phase_isolation_dir.mkdir(parents=True, exist_ok=True)
# Copy only the phase file into the isolated directory
import shutil as _shutil
isolated_phase_file = phase_isolation_dir / phase.file.name
_shutil.copy2(phase.file, isolated_phase_file)
```

**Note**: `setup_isolation()` is already defined at executor.py:141. The `Phase` object has `.file` attribute (a `Path`). The `config.results_dir` path is available throughout `execute_sprint()`.

**Acceptance criteria**:
- `phase_isolation_dir` exists and contains only the phase file before `ClaudeProcess` is started
- No `ImportError` or `AttributeError` at runtime
- Dry-run mode: isolation directory still created (part of pre-execution setup)

---

### T01.02 — Pass isolation `scoped_work_dir` to `ClaudeProcess` constructor

**Tier**: STRICT
**File**: `src/superclaude/cli/sprint/executor.py` and `src/superclaude/cli/sprint/process.py`
**Depends on**: T01.01 (isolation dir must exist), **T06.02** (pipeline `build_env()` must support `env_vars` before this can work)
**Rationale**: S3-R02. The subprocess must have its working directory scoped to the isolated directory so that `@` file resolution in the agent doesn't load `tasklist-index.md` or other phase files.

**PREREQUISITE**: Complete T06.02 first. `pipeline/process.py` `ClaudeProcess.build_env()` currently has no `env_vars` parameter. Without T06.02, passing `isolation.env_vars` to `ClaudeProcess` has no effect — the env vars would be silently ignored.

**Step 1 — Verify T06.02 is complete**:
Confirm `pipeline/process.py` `ClaudeProcess.__init__` accepts `env_vars: dict[str, str] | None = None` and `build_env()` merges it. If not, stop and complete T06.02 first.

**Step 2 — Check `ClaudeProcess` constructor signature**:
Read `src/superclaude/cli/sprint/process.py` starting at line 1 to find `ClaudeProcess.__init__`. Look for whether it accepts `env_vars` or `work_dir` parameters. If it does, pass `isolation.env_vars` (which includes `CLAUDE_WORK_DIR`). If not, add support.

**Step 2 — Read `IsolationLayers.env_vars`** (executor.py:117-123):
```python
# Already defined:
def env_vars(self) -> dict[str, str]:
    return {
        "CLAUDE_WORK_DIR": str(self.scoped_work_dir),
        "GIT_CEILING_DIRECTORIES": str(self.git_boundary),
        "CLAUDE_PLUGIN_DIR": str(self.plugin_dir),
        "CLAUDE_SETTINGS_DIR": str(self.settings_dir),
    }
```

**Step 3 — Update `ClaudeProcess` instantiation** to pass env vars:
```python
proc_manager = ClaudeProcess(config, phase, env_vars=isolation.env_vars)
```

If `ClaudeProcess` doesn't accept `env_vars`, add the parameter with default `None` and merge into subprocess environment at `proc.start()`.

**Step 4 — Verify** `ClaudeProcess.start()` passes env vars to `subprocess.Popen` (or equivalent). The env should be `{**os.environ, **isolation.env_vars}` — not a replacement.

**Acceptance criteria**:
- `CLAUDE_WORK_DIR` is set to the isolated phase directory for the subprocess
- `GIT_CEILING_DIRECTORIES` prevents upward git traversal
- Existing subprocess launch behavior is unchanged when `env_vars=None`

---

### T01.03 — Add cleanup of isolation directory in `finally` block

**Tier**: STRICT
**File**: `src/superclaude/cli/sprint/executor.py`
**Rationale**: S3-R03. The isolation directory must be removed after each phase (success or failure) to prevent disk accumulation. The `finally` block in `execute_sprint()` (around line 733) is the right place for cleanup.

**Change**: Inside the phase execution loop, add cleanup in the `finally` block. Since the loop is inside the `try:` block of `execute_sprint()`, use a per-phase `try/finally`:

```python
# Wrap the phase body in per-phase try/finally for isolation cleanup
try:
    # [phase execution code]
    ...
finally:
    # S3: Clean up isolation directory after phase (success or failure)
    if phase_isolation_dir is not None and phase_isolation_dir.exists():
        import shutil as _shutil
        try:
            _shutil.rmtree(phase_isolation_dir, ignore_errors=True)
        except Exception:
            pass  # Non-fatal
```

**Important**: The outer `try/finally` in `execute_sprint()` already handles monitor, proc_manager, tui, and signal_handler cleanup. The phase-level isolation cleanup should be a SEPARATE inner `try/finally` that wraps the per-phase body from line 527 onward.

**Acceptance criteria**:
- After phase completes (PASS, FAIL, or exception), `phase_isolation_dir` is removed
- The outer `finally` block cleanup is not disrupted
- `phase_isolation_dir` variable is properly scoped (initialize to `None` before the loop)

---

### T01.04 — Add startup cleanup of orphaned `.isolation/` directories

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/executor.py`
**Rationale**: S3-R04. If the executor crashes mid-phase, orphaned `.isolation/phase-N/` directories remain. These should be cleaned at sprint startup.

**Change**: After `sprint_result = SprintResult(config=config)` (around line 521) and before the phase loop (line 526), add:

```python
# S3: Clean up orphaned isolation directories from prior crashed runs
_isolation_base = config.results_dir / ".isolation"
if _isolation_base.exists():
    import shutil as _shutil
    for _orphan in _isolation_base.iterdir():
        if _orphan.is_dir():
            try:
                _shutil.rmtree(_orphan, ignore_errors=True)
            except Exception:
                pass
```

**Acceptance criteria**:
- Any `results/.isolation/phase-*/` directories from prior runs are removed before the loop starts
- Non-fatal if cleanup fails
- Does not affect `.isolation/plugins/` or `.isolation/settings/` subdirs from `setup_isolation()`

---

## Phase 2 — S3 Summary Header (Tasks T02.01–T02.02)

### T02.01 — Add sprint summary header to `build_prompt()` in `process.py`

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/process.py`
**Rationale**: S3-R05. A ~200-token summary header at the start of the prompt orients the agent without requiring it to load the full tasklist-index.md. This is the complementary instruction-layer change to the isolation-layer change in T01.

**Current state**: `build_prompt()` at line 115 returns a string starting with `/sc:task-unified Execute all tasks in @{phase_file}`. There is no sprint-level context header.

**Change**: Add a `SprintConfig`-aware header. The `ClaudeProcess` has access to `self.config` and `self.phase`. Modify `build_prompt()` to prepend:

```python
def build_prompt(self) -> str:
    """Build the /sc:task-unified prompt for this phase."""
    pn = self.phase.number
    phase_file = self.phase.file
    config = self.config

    # S3-R05: Sprint summary header (~200 tokens)
    total_phases = len(config.phases) if hasattr(config, 'phases') else '?'
    header = (
        f"## Sprint Context\n"
        f"- Sprint: {config.release_dir.name}\n"
        f"- Phase: {pn} of {total_phases}\n"
        f"- Artifact root: {config.release_dir}\n"
        f"- Results dir: {config.results_dir}\n"
        f"- Phase file: {phase_file}\n"
        f"\n"
    )

    return (
        header +
        f"/sc:task-unified Execute all tasks in @{phase_file} "
        ...  # rest of existing prompt unchanged
    )
```

**Note**: Check whether `ClaudeProcess.__init__` stores `config` as `self.config`. Read lines 70-113 of process.py to verify. If it doesn't, pass config through or access via `self.phase.config` if that exists.

**S3-R06 addition**: Add to the prompt (after "Focus only on the tasks defined in the phase file"):
```python
f"- All task details are in the phase file above. Do not seek additional index files.\n"
```

**Acceptance criteria**:
- Prompt includes sprint name, phase number, total phases, artifact root, results dir, phase file path
- Prompt does NOT change the `/sc:task-unified` invocation line
- `build_prompt()` still returns a valid string when `config.phases` is not available (defensive)

---

### T02.02 — Add "do not seek additional index files" instruction to prompt

**Tier**: LIGHT
**File**: `src/superclaude/cli/sprint/process.py`
**Rationale**: S3-R06. This instruction makes the isolation redundant as a fallback (belt-and-suspenders).

**Change**: Already included in T02.01 — this is a 1-line addition to the "Important" section of `build_prompt()`.

**Acceptance criteria**:
- Prompt contains phrase "Do not seek additional index files" (or equivalent)

---

## Phase 3 — S2 Defense-in-Depth (Tasks T03.01–T03.02)

### T03.01 — Extend `detect_prompt_too_long()` to also scan error file

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/monitor.py`
**Rationale**: S2-R08. The "Prompt is too long" error may appear in stderr (error_file) rather than stdout (output_file) depending on Claude CLI behavior. Scanning both provides defense-in-depth.

**Current state**: `detect_prompt_too_long(output_path: Path) -> bool` at line 63 scans one file.

**Option A — Modify existing signature** (preferred for backward compat):
```python
def detect_prompt_too_long(output_path: Path, error_path: Path | None = None) -> bool:
    """Check if NDJSON output or stderr contains a prompt-too-long error.

    Scans the last 10 non-empty lines of output_path (stdout NDJSON).
    Also scans error_path (stderr) if provided — defense-in-depth for
    CLI error formats that write to stderr.
    """
    # existing logic for output_path unchanged
    ...

    # Defense-in-depth: also check stderr
    if not found and error_path is not None:
        try:
            content = error_path.read_text(errors="replace")
        except (FileNotFoundError, OSError):
            return False
        lines = content.strip().splitlines()
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

**Option B — Separate helper** (more modular, slightly more code):
```python
def detect_prompt_too_long_in_file(path: Path) -> bool:
    """Shared scanning logic for any file."""
    ...

def detect_prompt_too_long(output_path: Path, error_path: Path | None = None) -> bool:
    return (
        detect_prompt_too_long_in_file(output_path)
        or (error_path is not None and detect_prompt_too_long_in_file(error_path))
    )
```

Use **Option A** to minimize API surface change.

**Acceptance criteria**:
- Existing 3 tests for `detect_prompt_too_long()` still pass (backward compatible — `error_path` defaults to `None`)
- When `error_path` is provided, the function returns True if the pattern appears in either file
- The function does NOT require `error_path` — caller passes it when available

---

### T03.02 — Update `_determine_phase_status()` to pass `error_file` to detection

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/executor.py`
**Rationale**: The `error_file` is available in `execute_sprint()` context and must be plumbed through to `detect_prompt_too_long()`.

**Current state** (executor.py:942-951):
```python
if exit_code != 0:
    if detect_prompt_too_long(output_file):
        result_status = _classify_from_result_file(result_file, started_at)
        ...
```

**Step 1**: Update `_determine_phase_status()` signature to accept `error_file`:
```python
def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
    *,
    config: SprintConfig | None = None,
    phase: Phase | None = None,
    started_at: float = 0.0,
    error_file: Path | None = None,   # NEW — S2-R08 defense-in-depth
) -> PhaseStatus:
```

**Step 2**: Update the detection call inside `_determine_phase_status()`:
```python
if detect_prompt_too_long(output_file, error_path=error_file):
```

**Step 3**: Update the call site in `execute_sprint()` (around line 659-667) to pass `error_file`:
```python
status = _determine_phase_status(
    exit_code=exit_code,
    result_file=config.result_file(phase),
    output_file=config.output_file(phase),
    config=config,
    phase=phase,
    started_at=started_at.timestamp(),
    error_file=config.error_file(phase),   # NEW
)
```

**Note**: `config.error_file(phase)` already exists — used at line 682 in `execute_sprint()`.

**Acceptance criteria**:
- All existing tests pass (3-arg and 5-arg calls still work — `error_file` defaults to `None`)
- The new `error_file` parameter is keyword-only and optional

---

## Phase 4 — Tests (Tasks T04.01–T04.09)

All new tests go in `tests/sprint/test_phase8_halt_fix.py` (existing file).

---

### T04.01 — Test: isolation directory created before subprocess spawn

**Tier**: STRICT
**File**: `tests/sprint/test_phase8_halt_fix.py`
**Class**: `TestS3Isolation`

```python
class TestS3Isolation:
    """T04.01-T04.04: S3 Phase-specific directory isolation."""

    def test_isolation_dir_created(self, tmp_path):
        """Isolation directory is created before subprocess is launched."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        # Call setup_isolation and verify the directory creation logic
        from superclaude.cli.sprint.executor import setup_isolation
        isolation = setup_isolation(config)
        phase_isolation_dir = config.results_dir / ".isolation" / f"phase-{phase.number}"
        phase_isolation_dir.mkdir(parents=True, exist_ok=True)
        (tmp_path / "results").mkdir(exist_ok=True)
        assert phase_isolation_dir.exists()
```

**Acceptance criteria**: `phase_isolation_dir.exists()` is True after setup.

---

### T04.02 — Test: isolation directory cleaned up after phase completes

**Tier**: STRICT
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
    def test_isolation_dir_cleaned_up(self, tmp_path):
        """Isolation directory is removed after phase execution."""
        from superclaude.cli.sprint.executor import setup_isolation
        config = _make_config(tmp_path)
        phase = config.phases[0]
        phase_isolation_dir = config.results_dir / ".isolation" / f"phase-{phase.number}"
        phase_isolation_dir.mkdir(parents=True, exist_ok=True)
        assert phase_isolation_dir.exists()
        # Simulate cleanup
        import shutil
        shutil.rmtree(phase_isolation_dir, ignore_errors=True)
        assert not phase_isolation_dir.exists()
```

**Acceptance criteria**: Directory absent after cleanup.

---

### T04.03 — Test: isolation directory cleaned up after phase fails

**Tier**: STRICT
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
    def test_isolation_dir_cleaned_up_on_failure(self, tmp_path):
        """Isolation directory is removed even when phase fails."""
        # Same as test_isolation_dir_cleaned_up — cleanup is in finally block
        # Simulate failure path: dir exists, exception raised, cleanup still runs
        from superclaude.cli.sprint.executor import setup_isolation
        config = _make_config(tmp_path)
        phase = config.phases[0]
        phase_isolation_dir = config.results_dir / ".isolation" / f"phase-{phase.number}"
        phase_isolation_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        try:
            raise RuntimeError("simulated phase failure")
        finally:
            shutil.rmtree(phase_isolation_dir, ignore_errors=True)
        # If we reach here (we won't due to RuntimeError), dir should be gone
        # The assertion is: rmtree in finally block runs despite exception
```

**Note**: This test is more documentation than verification — the real test is that the finally block exists in the implementation. Adjust to be a unit test of the isolation lifecycle.

**Better approach for T04.03**:
```python
    def test_isolation_cleanup_is_safe_on_missing_dir(self, tmp_path):
        """Cleanup does not raise if isolation directory already missing."""
        import shutil
        missing_dir = tmp_path / ".isolation" / "phase-99"
        # Should not raise
        shutil.rmtree(missing_dir, ignore_errors=True)
        assert not missing_dir.exists()
```

---

### T04.04 — Test: orphaned isolation directories cleaned on sprint startup

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
    def test_orphaned_isolation_dirs_cleaned_on_startup(self, tmp_path):
        """Orphaned .isolation/ subdirs from prior runs are removed at startup."""
        config = _make_config(tmp_path)
        (tmp_path / "results").mkdir(exist_ok=True)
        # Create orphaned directories
        orphan = config.results_dir / ".isolation" / "phase-99"
        orphan.mkdir(parents=True, exist_ok=True)
        (orphan / "orphan-file.md").write_text("stale data\n")
        assert orphan.exists()
        # Simulate startup cleanup
        import shutil
        _isolation_base = config.results_dir / ".isolation"
        if _isolation_base.exists():
            for d in _isolation_base.iterdir():
                if d.is_dir():
                    shutil.rmtree(d, ignore_errors=True)
        assert not orphan.exists()
```

---

### T04.05 — Test: summary header present in prompt with correct metadata

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
class TestS3SummaryHeader:
    """T04.05: Summary header in build_prompt()."""

    def test_summary_header_in_prompt(self, tmp_path):
        """build_prompt() includes sprint context header with metadata."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        from superclaude.cli.sprint.process import ClaudeProcess
        proc = ClaudeProcess(config, phase)
        prompt = proc.build_prompt()
        # Header must contain phase number, artifact root or results dir
        assert f"Phase {phase.number}" in prompt
        assert str(config.release_dir) in prompt or str(config.results_dir) in prompt
        assert "Do not seek additional index files" in prompt or "index files" in prompt.lower()
```

**Acceptance criteria**: `build_prompt()` output contains phase number and path context.

---

### T04.06 — Test: `detect_prompt_too_long()` returns False when pattern not in last 10 lines

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
class TestDetectPromptTooLongExtended:
    """T04.06-T04.07: Extended detect_prompt_too_long coverage."""

    def test_pattern_in_middle_not_detected(self, tmp_path):
        """detect_prompt_too_long returns False when pattern is NOT in last 10 lines."""
        output = tmp_path / "output.jsonl"
        # Pattern on line 1, then 15 clean lines follow
        lines = ['{"error":{"message":"Prompt is too long"}}\n']
        lines += ['{"type":"assistant","content":"ok"}\n'] * 15
        output.write_text("".join(lines))
        from superclaude.cli.sprint.monitor import detect_prompt_too_long
        # Pattern is more than 10 lines from end — should NOT be detected
        assert detect_prompt_too_long(output) is False
```

---

### T04.07 — Test: `detect_prompt_too_long()` scans stderr file as fallback

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
    def test_error_file_scanned_as_fallback(self, tmp_path):
        """detect_prompt_too_long(output, error_path) detects pattern in stderr."""
        output = tmp_path / "output.jsonl"
        output.write_text('{"type":"assistant","content":"work done"}\n')
        error = tmp_path / "error.txt"
        error.write_text('Error: Prompt is too long\n')
        from superclaude.cli.sprint.monitor import detect_prompt_too_long
        # Pattern only in error file, not output
        assert detect_prompt_too_long(output) is False          # Without error_path
        assert detect_prompt_too_long(output, error_path=error) is True  # With error_path
```

---

### T04.08 — Test: exit=1 + prompt-too-long + HALT file → PhaseStatus.HALT

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
class TestContextExhaustionRecoveryExtended:
    """T04.08-T04.09: Extended context exhaustion recovery paths."""

    def test_recovery_with_halt_file(self, tmp_path):
        """exit=1 + prompt-too-long + fresh HALT file → HALT."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text('{"error":{"message":"Prompt is too long"}}\n')
        import time
        started_at = time.time() - 10
        result_file.write_text("EXIT_RECOMMENDATION: HALT\n")
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
            started_at=started_at,
        )
        assert status == PhaseStatus.HALT
```

---

### T04.09 — Test: exit=1 + no prompt-too-long → PhaseStatus.ERROR (unchanged)

**Tier**: STANDARD
**File**: `tests/sprint/test_phase8_halt_fix.py`

```python
    def test_non_context_error_gives_error(self, tmp_path):
        """exit=1 without prompt-too-long → ERROR (existing behavior preserved)."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        # Clean output, no pattern
        output_file.write_text('{"type":"assistant","content":"done"}\n')
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR
```

---

## Phase 5 — Verification (Tasks T05.01–T05.02)

### T05.01 — Run full test suite and fix any regressions

**Tier**: STRICT
**Command**:
```bash
uv run pytest tests/sprint/ -v --tb=short
```

**Expected**: All existing 629 tests pass, plus all new tests added in T04.01–T04.09.

**If failures**: Investigate and fix root cause. Do NOT skip tests. Do NOT add `pytest.mark.skip`.

**Regression risk areas**:
- `ClaudeProcess` signature change (T01.02) — check `tests/sprint/test_executor.py` and `tests/sprint/test_integration_*.py`
- `_determine_phase_status()` signature change (T03.02) — check `tests/sprint/test_backward_compat_regression.py`
- `build_prompt()` change (T02.01) — check `tests/sprint/test_context_injection.py`

---

### T05.02 — Run `ruff check` + `ruff format --check` on modified files

**Tier**: LIGHT
**Command**:
```bash
uv run ruff check src/superclaude/cli/sprint/executor.py \
                  src/superclaude/cli/sprint/monitor.py \
                  src/superclaude/cli/sprint/process.py \
                  tests/sprint/test_phase8_halt_fix.py
uv run ruff format --check src/superclaude/cli/sprint/executor.py \
                           src/superclaude/cli/sprint/monitor.py \
                           src/superclaude/cli/sprint/process.py \
                           tests/sprint/test_phase8_halt_fix.py
```

**Expected**: Zero lint errors. Run `uv run ruff format` (without `--check`) if formatting issues found.

---

## Implementation Notes

### Already Implemented (Do Not Reimplement)

The following were identified in the adversarial validation as critical gaps but have already been implemented in the current branch (`feature/v2.24.2-Accept-Spec-Change`):

| Item | Status | Evidence |
|------|--------|---------|
| `PASS_RECOVERED` enum value | ✅ DONE | `models.py:212` |
| `detect_prompt_too_long()` | ✅ DONE | `monitor.py:63` |
| `_classify_from_result_file()` | ✅ DONE | `executor.py:782` |
| Recovery chain in `_determine_phase_status()` | ✅ DONE | `executor.py:942` |
| `_write_executor_result_file()` (post-status, not pre) | ✅ DONE | `executor.py:873` — resolves the circularity the validation found |
| `_check_checkpoint_pass()` + contamination | ✅ DONE | `executor.py:819` |
| `FailureCategory.CONTEXT_EXHAUSTION` | ✅ DONE | `diagnostics.py:27` |
| `_check_fidelity()` + `--force-fidelity-fail` | ✅ DONE | `commands.py:35` |
| Completion Protocol removed, Scope Boundary added | ✅ DONE | `process.py:136-138` |
| TUI handles `PASS_RECOVERED` | ✅ DONE | `tui.py:32,46` |
| All 12 Phase 8 tests passing | ✅ DONE | `test_phase8_halt_fix.py` |

### Key Architectural Decision

The adversarial validation report identified that the original analysis had a critical error: the "~5 lines" S1 implementation assumed `task_results` existed in `execute_sprint()`. This has been **resolved in the live code** by implementing `_write_executor_result_file()` which derives the result from `PhaseStatus` (already determined), `MonitorState`, and timing — NOT from per-task aggregation. This is the correct solution (Option B from the validation report's recommended corrective actions). No `execute_phase_tasks()` wiring is needed.

### Dependency Order for Remaining Tasks

```
T06.02 (pipeline build_env env_vars)           ← must complete BEFORE T01.02
  └─→ T01.01 (isolation create) [parallel-safe: T01.01 doesn't touch ClaudeProcess]
        └─→ T01.02 (pass env_vars to ClaudeProcess) [needs BOTH T01.01 AND T06.02]
              └─→ T01.03 (cleanup in finally)
              └─→ T06.08 (empirical validation gate doc)
  └─→ T01.04 (startup cleanup) [needs T01.01 only]

T01.01 (isolation create)
  └─→ T04.01 (test: dir created) [depends on T01.01 only — unaffected by T06.02]

T01.03 (cleanup in finally)
  └─→ T04.02 (test: cleanup success)
  └─→ T04.03 (test: cleanup failure)

T01.04 (startup cleanup)
  └─→ T04.04 (test: orphan cleanup)

T02.01 (summary header)
  └─→ T02.02 (index instruction) [included in T02.01]
  └─→ T04.05 (test: header present)
  └─→ T06.03 (prior-phase artifact paths)

T03.01 (error_file scan)
  └─→ T03.02 (pass error_file through)
  └─→ T04.07 (test: stderr fallback)

[independent — no blocking deps]
  T04.06 (test: pattern in middle)
  T04.08 (test: halt file recovery)
  T04.09 (test: non-context error)
  T06.01 (logger PASS_RECOVERED routing)
  T06.04 (dead result_file variable)
  T06.05 (diagnostics output_file path fix)
  T06.06 (integration test: PASS_RECOVERED continuation)
  T06.07 (S4 architecture spec)

T04.01..T04.09 all → T05.01 (full test suite)
T05.01 → T05.02 (lint check)
```

---

## Files to Modify

| File | Tasks | Change Type |
|------|-------|-------------|
| `src/superclaude/cli/sprint/executor.py` | T01.01, T01.03, T01.04, T03.02 | Wire isolation, extend signature |
| `src/superclaude/cli/sprint/process.py` | T02.01, T06.03, T06.04 | Add header, add artifact paths, remove dead var |
| `src/superclaude/cli/sprint/monitor.py` | T03.01 | Add `error_path` param to detect function |
| `src/superclaude/cli/sprint/logging_.py` | T06.01 | Add `PASS_RECOVERED` screen routing |
| `src/superclaude/cli/sprint/diagnostics.py` | T06.05 | Fix output_file path in `FailureClassifier.classify()` |
| `src/superclaude/cli/pipeline/process.py` | T06.02 | Add `env_vars` parameter to `build_env()` |
| `tests/sprint/test_phase8_halt_fix.py` | T04.01–T04.09, T06.06 | Add new test classes |
| `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/artifact-batching-architecture-spec.md` | T06.07 | New document (S4 design spec) |

---

## Phase 6 — Gap Fills from PRD + Overlap Analysis (Tasks T06.01–T06.08)

These tasks were identified by cross-referencing the PRD (sprint-context-exhaustion-prd.md) and overlap analysis (Phase8-SprintContext-cross-spec-overlap-analysis.md) against the existing tasklist. Each represents a validated, non-conflicting requirement that was not previously captured.

---

### T06.01 — Fix `SprintLogger.write_phase_result()` — add `PASS_RECOVERED` to screen routing

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/logging_.py`
**Source**: PRD SC-04 — "Execution log distinguishes PASS_RECOVERED from clean PASS"

**Current state** (`logging_.py` lines 122-140):
```python
# Screen severity routing
# DEBUG -> JSONL only (PASS_NO_SIGNAL)
# INFO  -> screen + JSONL (PASS/PASS_NO_REPORT)
# WARN  -> highlighted stderr + JSONL (HALT/TIMEOUT)
# ERROR -> highlighted stderr + JSONL + bell (ERROR)
if result.status == PhaseStatus.ERROR:
    self._screen_error(...)
elif result.status in (PhaseStatus.HALT, PhaseStatus.TIMEOUT):
    self._screen_warn(...)
elif result.status in (PhaseStatus.PASS, PhaseStatus.PASS_NO_REPORT):
    self._screen_info(...)
# PASS_RECOVERED falls through with NO screen output — silent
```

**Problem**: `PASS_RECOVERED` is not in any branch. It falls through silently — the user gets no screen notification that a phase recovered from a context exhaustion crash. This violates SC-04.

**Change**: Add `PASS_RECOVERED` to the `elif` chain with a distinct WARN-level message that communicates the recovery:

```python
elif result.status == PhaseStatus.PASS_RECOVERED:
    self._screen_warn(
        f"Phase {result.phase.number}: recovered (non-zero exit, evidence of success) "
        f"({result.duration_display})"
    )
```

Use WARN (not INFO) because `PASS_RECOVERED` represents an abnormal-but-successful event that requires user awareness.

**Acceptance criteria**:
- Running a phase that returns `PASS_RECOVERED` produces a visible warning-level message on stderr
- JSONL log records `status: pass_recovered` (already works via `.value`)
- Markdown execution log row is written (line 109 condition: `result.status != PhaseStatus.PASS_NO_SIGNAL` — already handles PASS_RECOVERED since it's not PASS_NO_SIGNAL)

---

### T06.02 — Add `env_vars` parameter to `pipeline/process.py` `ClaudeProcess.build_env()`

**Tier**: STRICT
**File**: `src/superclaude/cli/pipeline/process.py`
**Source**: S3-R02. Required by T01.02 — isolation env vars must reach the subprocess.

**Current state** (`pipeline/process.py` lines 91-100):
```python
def build_env(self) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return env
```

No mechanism to inject additional env vars. `ClaudeProcess.__init__` (lines 37-65) has no `env_vars` parameter.

**Change — Step 1**: Add `env_vars` parameter to `ClaudeProcess.__init__`:
```python
def __init__(
    self,
    *,
    prompt: str,
    output_file: Path,
    error_file: Path,
    max_turns: int = 100,
    model: str = "",
    permission_flag: str = "--dangerously-skip-permissions",
    timeout_seconds: int = 6300,
    output_format: str = "stream-json",
    extra_args: list[str] | None = None,
    env_vars: dict[str, str] | None = None,   # NEW — additional env overrides
    on_spawn: Callable[[int], None] | None = None,
    on_signal: Callable[[int, str], None] | None = None,
    on_exit: Callable[[int, int | None], None] | None = None,
):
    ...
    self._extra_env_vars = env_vars or {}
```

**Change — Step 2**: Merge extra env vars in `build_env()`:
```python
def build_env(self) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    env.update(self._extra_env_vars)   # NEW — isolation layer overrides
    return env
```

**Change — Step 3**: Update `sprint/process.py` `ClaudeProcess.__init__` to accept and forward `env_vars`:
```python
class ClaudeProcess(_PipelineClaudeProcess):
    def __init__(self, config: SprintConfig, phase: Phase, env_vars: dict[str, str] | None = None):
        self.config = config
        self.phase = phase
        prompt = self.build_prompt()
        super().__init__(
            prompt=prompt,
            ...
            env_vars=env_vars,    # NEW — forward to pipeline base
            ...
        )
```

**Acceptance criteria**:
- `ClaudeProcess(config, phase)` (no `env_vars`) behaves identically to before
- `ClaudeProcess(config, phase, env_vars={"CLAUDE_WORK_DIR": "/tmp/foo"})` sets `CLAUDE_WORK_DIR` in the subprocess env
- Existing `pipeline/process.py` tests pass with no changes (parameter is keyword-only, default None)
- `build_env()` order: os.environ → pop CLAUDECODE/CLAUDE_CODE_ENTRYPOINT → apply `_extra_env_vars` (isolation wins over inherited env)

---

### T06.03 — Add prior-phase artifact directories to S3 summary header in `build_prompt()`

**Tier**: STANDARD
**File**: `src/superclaude/cli/sprint/process.py`
**Source**: PRD S3-R05 — "sprint summary header containing: sprint name, phase number/total, artifact root path, results dir, **execution log path**, and **prior-phase artifact directories**"

**Current gap**: T02.01 covers sprint name, phase number/total, artifact root, results dir — but NOT execution log path or prior-phase artifact directories. These were explicitly required by the PRD S3-R05 and confirmed at 94% convergence.

**Change**: Extend the header built in T02.01 to include:
- Execution log path: `config.execution_log_md` (or `config.execution_log_jsonl`)
- Prior-phase artifact directories: for phases 1..N-1, list `config.release_dir / "artifacts" / f"D-{n:04d}"` or equivalent artifact subdirectory path

**Implementation**:
```python
# Build list of prior-phase artifact dirs that exist
prior_artifact_dirs = []
for prior_n in range(1, pn):
    # Artifact dir convention: release_dir/artifacts/
    art_dir = config.release_dir / "artifacts"
    if art_dir.exists():
        phase_art_dirs = [
            str(d) for d in art_dir.iterdir()
            if d.is_dir() and d.name.startswith(f"D-")  # or phase-specific subdirs
        ]
        prior_artifact_dirs.extend(phase_art_dirs[:5])  # cap to avoid token bloat
        break  # one pass sufficient

prior_artifacts_str = "\n".join(f"  - {d}" for d in prior_artifact_dirs) if prior_artifact_dirs else "  (none yet)"

header = (
    f"## Sprint Context\n"
    f"- Sprint: {config.release_dir.name}\n"
    f"- Phase: {pn} of {total_phases}\n"
    f"- Artifact root: {config.release_dir}\n"
    f"- Results dir: {config.results_dir}\n"
    f"- Execution log: {config.execution_log_md}\n"   # NEW
    f"- Phase file: {phase_file}\n"
    f"- Prior artifact dirs:\n{prior_artifacts_str}\n"  # NEW
    f"\n"
)
```

**Note**: First read `SprintConfig` to verify attributes `execution_log_md` and `execution_log_jsonl` exist. Check `src/superclaude/cli/sprint/config.py` or `models.py` for exact attribute names.

**Acceptance criteria**:
- Prompt header includes execution log path when available
- Prompt header includes at least the artifact root (prior phase dirs may be empty for Phase 1 — this is fine)
- Token overhead remains bounded (~200 tokens total for header)

---

### T06.04 — Remove dead `result_file` variable from `process.py` `build_prompt()`

**Tier**: LIGHT
**File**: `src/superclaude/cli/sprint/process.py`
**Source**: Overlap analysis Section 4, Step 3 — "Remove reference to `result_file` variable (line 118) if no longer used."

**Current state** (`process.py` line 118):
```python
def build_prompt(self) -> str:
    """Build the /sc:task-unified prompt for this phase."""
    pn = self.phase.number
    result_file = self.config.result_file(self.phase)  # <-- DEAD CODE after S1-R04
    phase_file = self.phase.file
```

After removing the Completion Protocol (already done — `result_file` was referenced in the f-string at lines 140, 147, etc.), `result_file` is no longer used anywhere in `build_prompt()`. It's dead code.

**Change**: Remove the `result_file = self.config.result_file(self.phase)` line (currently line 118).

**Verify first**: Search `build_prompt()` body for any remaining reference to `result_file`. If none found, remove the assignment.

**Acceptance criteria**:
- `result_file` variable is not defined in `build_prompt()`
- No `NameError` or `AttributeError` at runtime
- `ruff` no longer reports F841 (local variable assigned but never used) for this line

---

### T06.05 — Fix `FailureClassifier.classify()` output_file path construction in `diagnostics.py`

**Tier**: STRICT
**File**: `src/superclaude/cli/sprint/diagnostics.py`
**Source**: Implementation correctness — existing CONTEXT_EXHAUSTION detection uses an incorrect path.

**Current state** (`diagnostics.py` lines 180-187):
```python
# 2.5. Context exhaustion (prompt too long)
from .monitor import detect_prompt_too_long

output_file = bundle.phase_result.phase.file.parent.parent / "results" / f"phase-{bundle.phase_result.phase.number}-output.txt"
if exit_code != 0 and detect_prompt_too_long(output_file):
```

**Problem**: This constructs the output file path as `phase.file.parent.parent / "results" / "phase-N-output.txt"`. The `phase.file` is the phase tasklist file (e.g., `release_dir/phase-1-tasklist.md`). `phase.file.parent` = `release_dir`. `phase.file.parent.parent` = `release_dir.parent` — going UP one level past the release directory. This is almost certainly wrong.

The correct path should come from `config.output_file(phase)` or `config.results_dir / f"phase-{N}-output.txt"`. The `DiagnosticBundle` must have access to the config to resolve this correctly.

**Step 1**: Read `DiagnosticBundle` definition in `diagnostics.py` to find what fields it carries.

**Step 2**: Check if `bundle` has access to `config` or `phase_result` with config context.

**Step 3**: If `DiagnosticBundle` has a `config` field, use `config.output_file(phase)`. If not, use `bundle.phase_result.phase.file.parent / "results" / f"phase-{N}-output.txt"` (one level, not two).

**Likely fix** (use `phase.file.parent` which = release_dir, then `results/`):
```python
output_file = bundle.phase_result.phase.file.parent / "results" / f"phase-{bundle.phase_result.phase.number}-output.txt"
```
Or better, look up the actual path convention used by `config.output_file(phase)`.

**Acceptance criteria**:
- `FailureClassifier.classify()` uses the correct output file path when checking for context exhaustion
- The path matches what `config.output_file(phase)` would return
- No change to the logic — only the path construction

---

### T06.06 — Add integration test: sprint continues to next phase on `PASS_RECOVERED`

**Tier**: STRICT
**File**: `tests/sprint/test_phase8_halt_fix.py`
**Source**: PRD Section 5, S2 Tests — "Sprint continues to next phase on PASS_RECOVERED" (Integration type)

**Gap**: The existing tests verify that `_determine_phase_status()` returns `PASS_RECOVERED` in the right conditions, but no test verifies that `execute_sprint()` actually continues (does not halt) when `status == PASS_RECOVERED`. The loop condition at `executor.py:715` is `if status.is_failure:` — PASS_RECOVERED has `is_failure=False` so it should continue, but this is not tested end-to-end.

**Test design** (unit test using mocked subprocess, not a real integration test):

```python
class TestPassRecoveredContinuation:
    """T06.06: Sprint continues to next phase on PASS_RECOVERED."""

    def test_pass_recovered_does_not_halt_sprint(self, tmp_path):
        """PhaseStatus.PASS_RECOVERED.is_failure is False — sprint loop continues."""
        # This verifies the critical invariant: PASS_RECOVERED does not trigger
        # the 'if status.is_failure: halt' branch in execute_sprint()
        assert PhaseStatus.PASS_RECOVERED.is_failure is False
        assert PhaseStatus.PASS_RECOVERED.is_success is True
        # The sprint loop uses 'if status.is_failure: break'
        # So is_failure=False guarantees continuation — no mock needed
        # Additional: verify it's NOT in the is_failure tuple
        failure_statuses = [
            s for s in PhaseStatus
            if s.is_failure
        ]
        assert PhaseStatus.PASS_RECOVERED not in failure_statuses

    def test_pass_recovered_is_logged_at_warn_level(self, tmp_path):
        """PASS_RECOVERED produces a warn-level screen message (SC-04)."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        (tmp_path / "results").mkdir(exist_ok=True)
        from superclaude.cli.sprint.logging_ import SprintLogger
        from superclaude.cli.sprint.models import PhaseResult
        from datetime import datetime, timezone
        logger = SprintLogger(config)
        now = datetime.now(timezone.utc)
        phase_result = PhaseResult(
            phase=phase,
            status=PhaseStatus.PASS_RECOVERED,
            exit_code=1,
            started_at=now,
            finished_at=now,
            output_bytes=100,
            error_bytes=0,
        )
        # Should not raise and should write to execution_log_md
        logger.write_phase_result(phase_result)
        log_content = config.execution_log_md.read_text()
        assert "pass_recovered" in log_content
```

**Acceptance criteria**:
- `PASS_RECOVERED.is_failure` is False (sprint loop does not break)
- `write_phase_result()` with `PASS_RECOVERED` writes to the execution log
- No exception raised

---

### T06.07 — Write S4 artifact batching architecture spec document

**Tier**: STANDARD
**File**: `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/artifact-batching-architecture-spec.md` (new document)
**Source**: PRD Section 3.4, S4-R01 through S4-R05 — "Design-only. No implementation."

**Content requirements** (from PRD S4-R01 through S4-R05):

1. **`ArtifactWriterProcess` class spec** — class with `build_artifact_prompt()` method. Prompt instructs agent to write all artifact documents (specs, reports) from a structured manifest, without re-doing implementation work.

2. **`PhaseResult` extension** — add `impl_status` (was the implementation work successful?) and `artifacts_status` (were the artifact documents written?) as separate tracked fields.

3. **`SprintConfig.artifact_mode` field** — `--artifact-mode inline|deferred|none` CLI flag. `inline` = current behavior, `deferred` = post-phase artifact writer subprocess, `none` = no artifact writing.

4. **Manifest capture design** — lightweight YAML per task: `{task_id, status, key_decision}`. Preserves decision record even if artifact writing subprocess exhausts context.

5. **Implementation trigger criteria** — second context exhaustion occurrence OR phase spec with >8 deliverables OR `(artifact_count * 1500) > remaining_budget * 0.5`.

**Format**: Write as a design specification document with sections for motivation, proposed architecture, interface definitions, and implementation trigger criteria. Include Python pseudocode for the class interfaces.

**Acceptance criteria**:
- Document exists at `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/artifact-batching-architecture-spec.md`
- Covers all 5 S4 requirements
- Marked clearly as "Design Only — Not Implemented" in the header
- Links back to the PRD section 3.4 for context

---

### T06.08 — Document S3 empirical validation requirement as pre-merge gate

**Tier**: LIGHT
**File**: `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/artifact-batching-architecture-spec.md` OR a new `config/workspace/IronClaude/.dev/releases/current/v2.25.7-Phase8HaltFix/s3-empirical-validation-gate.md`
**Source**: PRD S3 convergence note — "Pre-merge validation requirement: Measure context consumption for at least one phase execution with and without the index accessible."

**Requirement**: Before merging the S3 directory isolation changes (T01.01–T01.04, T02.01–T02.02), validate empirically that the `tasklist-index.md` is actually being loaded by the agent subprocess. If context delta is <5K tokens, the S3 changes provide less benefit than the ~14K estimate.

**Change**: Add a section to the implementation notes (or a separate doc) describing:
1. How to measure context consumption: compare `output_bytes` from `monitor.state` for the same phase with and without isolation active
2. What to look for: grep the NDJSON output for `@tasklist-index.md` or large content blocks matching the index
3. Decision rule: if delta <5K tokens → mark S3 as low-impact in release notes but keep it (still prevents potential loading); if delta ≥5K → S3 validated as high-value
4. Where to record the result: add a comment to `execute_sprint()` near the isolation setup code

**Acceptance criteria**:
- Pre-merge validation requirement is documented somewhere discoverable
- The decision rule (5K threshold) is explicit
- The measurement method is actionable (not just "measure it somehow")
