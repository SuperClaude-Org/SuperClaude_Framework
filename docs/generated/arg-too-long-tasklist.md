# Task List: Fix `OSError [Errno 7] Argument list too long`

**Branch**: Create from current branch (`v2.25-Roadmap-v5`)
**Status**: Ready for implementation
**Priority**: P0 — pipeline is blocked

---

## CRITICAL BLOCKER: `--file` Fallback Likely Broken

**Verdict**: 80% confidence the `--file` fallback is **silently broken**.

The fallback path passes bare filesystem paths (`--file /absolute/path/to/spec.md`) but `claude --help` documents `--file` as `file_id:relative_path` format for remote file downloads. These are semantically incompatible. All tests mock `ClaudeProcess` — zero tests actually invoke `claude` with `--file /path`.

**Impact**: Four executors use this pattern:
- `roadmap/executor.py` (fallback, rarely triggers)
- `validate_executor.py` (fallback, rarely triggers)
- `tasklist/executor.py` (fallback, rarely triggers)
- **`remediate_executor.py` line 177 (UNCONDITIONAL — always fires)**

**Before implementing Phase 1, run this empirical test (Task 0.1)** to determine whether the fallback mechanism works at all. If broken, the Phase 1 fix (which relies on the fallback) needs a different approach.

See: `docs/generated/arg-too-long-file-fallback-validation.md` for full investigation.

---

## Background for New Agents

The SuperClaude roadmap pipeline spawns `claude` subprocesses via `subprocess.Popen` with the prompt passed as a `-p` CLI argument. The Linux kernel enforces `MAX_ARG_STRLEN = 128 KB` as a hard per-argument limit. The pipeline's embed guard (`_EMBED_SIZE_LIMIT`) is set to 200 KB — above the kernel limit — so combined inputs between 128–200 KB pass the guard but crash `Popen` with `OSError [Errno 7]`.

The `spec-fidelity` step fails because it embeds the spec file (117.9 KB) + roadmap (34.2 KB) = 152.1 KB, which exceeds 128 KB but passes the 200 KB guard.

### Key Files
- `src/superclaude/cli/roadmap/executor.py` — embed guard and step execution
- `src/superclaude/cli/pipeline/process.py` — `ClaudeProcess.build_command()` (uses `-p self.prompt`)
- `src/superclaude/cli/roadmap/remediate_executor.py` — **unconditional** `--file` usage (line 177)
- `src/superclaude/cli/roadmap/validate_executor.py` — `--file` fallback (line 109)
- `src/superclaude/cli/tasklist/executor.py` — `--file` fallback (line 121)
- `tests/roadmap/test_file_passing.py` — tests for embed/fallback behavior (all mocked)
- `tests/roadmap/test_embed_inputs.py` — tests for `_embed_inputs()` helper

### Reference Documents
- `docs/generated/arg-too-long-solution-validation.md` — validated implementation plan
- `docs/generated/arg-too-long-solution-brainstorm.md` — full solution space with code snippets
- `docs/generated/arg-too-long-debate-solutions-L1.md` — L1 debate (88/100 confidence)
- `docs/generated/arg-too-long-file-fallback-validation.md` — `--file` fallback validation findings

---

## Phase 0: Validate `--file` Fallback (BLOCKING)

**Goal**: Determine if the `--file` fallback mechanism actually delivers file content to the model.
**Effort**: ~15 minutes
**Risk**: If broken, Phase 1's fallback path doesn't work — requires alternative approach.

### Task 0.1: Empirical test of `--file` with bare path

**Run manually** (not automated — requires actual `claude` CLI):

```bash
# Create test file
echo "The secret answer is PINEAPPLE." > /tmp/file-test.md

# Test 1: --file with bare path (what our code does)
claude --print -p "What is the secret answer in the file I provided?" --file /tmp/file-test.md

# Test 2: --file with file_id:path format (what the docs say)
claude --print -p "What is the secret answer in the file I provided?" --file test:/tmp/file-test.md

# Cleanup
rm /tmp/file-test.md
```

**Pass criteria**: Test 1 response mentions "PINEAPPLE". If it does, the fallback works (undocumented but functional). If it doesn't, the fallback is broken.

**If Test 1 FAILS** (file content not delivered):
- Phase 1 is still valid (the constant fix prevents the crash by keeping content inline)
- But the fallback path produces **silent correctness failures** when it fires
- `remediate_executor.py` (line 177) is actively broken and needs immediate fix
- Add Task 0.2: Fix `remediate_executor.py` to use inline embedding instead of `--file`
- Add Task 0.3: Fix the fallback in all 3 executors to use stdin delivery (3A) instead of `--file`
- Phase 3 (stdin delivery) becomes Phase 1 priority

**If Test 1 PASSES** (file content delivered):
- Document the undocumented behavior
- Phase 1 proceeds as planned (fallback path is confirmed working)
- Add a regression test that actually invokes `claude` with `--file /path` to pin the behavior

---

## Phase 1: Immediate Fix (1A + 1B) — Unblock Pipeline

**Goal**: Fix the miscalibrated constant and close the template-overhead measurement gap.
**Effort**: ~2 hours
**Risk**: Low — behavioral change is "crash → fallback to --file" (strictly better)

### Task 1.1: Replace `_EMBED_SIZE_LIMIT` with derived constants

**File**: `src/superclaude/cli/roadmap/executor.py`
**Lines**: 53–54

**Current code (line 53-54)**:
```python
# Threshold above which inline embedding falls back to --file flags
_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB
```

**Replace with**:
```python
# Linux kernel MAX_ARG_STRLEN: hard per-argument limit in execve() (compile-time constant).
# See: include/uapi/linux/binfmts.h — cannot be changed at runtime.
_MAX_ARG_STRLEN = 128 * 1024

# Conservative headroom for prompt template text that gets prepended to embedded content.
# Largest template (build_spec_fidelity_prompt) is ~3.4 KB. 8 KB provides 2.3× margin.
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024

# Threshold above which inline embedding falls back to --file flags.
# Derived from OS constraint minus template overhead.
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD
```

**Do NOT add `import resource`** — the brainstorm snippet included it erroneously as dead code.

**Verification**: `uv run pytest tests/roadmap/test_file_passing.py -v` should still pass (test uses the constant by import).

---

### Task 1.2: Change guard to measure full composed string (1B)

**File**: `src/superclaude/cli/roadmap/executor.py`
**Lines**: 173–192

**Current code (lines 173-192)**:
```python
    # Inline embedding: read input files into the prompt instead of --file flags
    embedded = _embed_inputs(step.inputs)
    if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
        effective_prompt = step.prompt + "\n\n" + embedded
        extra_args: list[str] = []
    elif embedded:
        _log.warning(
            "Step '%s': embedded inputs exceed %d bytes, falling back to --file flags",
            step.id,
            _EMBED_SIZE_LIMIT,
        )
        effective_prompt = step.prompt
        extra_args = [
            arg
            for input_path in step.inputs
            for arg in ("--file", str(input_path))
        ]
    else:
        effective_prompt = step.prompt
        extra_args = []
```

**Replace with**:
```python
    # Inline embedding: read input files into the prompt instead of --file flags.
    # Guard measures the FULL composed string that becomes the -p argument,
    # not just the embedded portion (closes template-overhead blind spot).
    embedded = _embed_inputs(step.inputs)
    composed = step.prompt + "\n\n" + embedded if embedded else step.prompt

    if len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
        effective_prompt = composed
        extra_args: list[str] = []
    elif embedded:
        _log.warning(
            "Step '%s': composed prompt (%d bytes) exceeds %d bytes, "
            "falling back to --file flags",
            step.id,
            len(composed.encode("utf-8")),
            _EMBED_SIZE_LIMIT,
        )
        effective_prompt = step.prompt
        extra_args = [
            arg
            for input_path in step.inputs
            for arg in ("--file", str(input_path))
        ]
    else:
        effective_prompt = step.prompt
        extra_args = []
```

**Key changes**:
1. Compute `composed = step.prompt + "\n\n" + embedded` before the guard
2. Guard checks `len(composed.encode("utf-8"))` instead of `len(embedded.encode("utf-8"))`
3. Log message now says "composed prompt" and reports actual composed size

**Verification**: `uv run pytest tests/roadmap/ -v`

---

### Task 1.3: Rename and update fallback test

**File**: `tests/roadmap/test_file_passing.py`
**Lines**: 105–136

**Changes**:
1. Rename class `TestSizeGuardFallback` docstring: `"Scenario 3: 100KB guard triggers fallback"` → `"Scenario 3: Embed size guard triggers fallback to --file flags."`
2. Rename method `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`
3. Update docstring: `"Verify that inputs exceeding 100KB fall back"` → `"Verify that inputs exceeding _EMBED_SIZE_LIMIT fall back to --file flags."`
4. Update comment on line 111: `"# Write content exceeding 100KB"` → `"# Write content exceeding _EMBED_SIZE_LIMIT"`

**Do not change test logic** — the test already imports `_EMBED_SIZE_LIMIT` and uses `_EMBED_SIZE_LIMIT + 1024` as the threshold, which will automatically use the new derived value.

**Verification**: `uv run pytest tests/roadmap/test_file_passing.py -v` — test should pass with new name.

---

### Task 1.4: Add a test for the new composed-string guard behavior

**File**: `tests/roadmap/test_file_passing.py`
**Add after** the renamed `TestSizeGuardFallback` class

**New test class**:
```python
class TestComposedStringGuard:
    """Scenario 4: Guard measures full composed string (prompt + embedded), not just embedded."""

    def test_prompt_plus_embedded_exceeds_limit(self, tmp_path: Path, caplog):
        """Verify fallback triggers when prompt + embedded exceeds limit,
        even if embedded alone would fit."""
        # Create a file that is 90% of _EMBED_SIZE_LIMIT
        file_size = int(_EMBED_SIZE_LIMIT * 0.9)
        input_file = tmp_path / "large-but-under-limit.md"
        input_file.write_text("x" * file_size)

        # Create a step with a prompt large enough that prompt + file > limit
        # but file alone < limit
        overhead_needed = _EMBED_SIZE_LIMIT - file_size + 1024  # push over by 1 KB
        large_prompt = "y" * overhead_needed

        step = Step(
            id="test-composed",
            prompt=large_prompt,
            output_file=tmp_path / "output.md",
            gate=None,
            timeout_seconds=60,
            inputs=[input_file],
        )
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.return_value = instance
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            with caplog.at_level(logging.WARNING, logger="superclaude.roadmap.executor"):
                result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        # File content should NOT be in prompt (fallback fired)
        assert "x" * 100 not in captured_prompt["value"]
        # --file flags should be present
        assert "--file" in captured_prompt["extra_args"]
        assert str(input_file) in captured_prompt["extra_args"]
```

**Verification**: `uv run pytest tests/roadmap/test_file_passing.py::TestComposedStringGuard -v`

---

### Task 1.5: Run full test suite and verify pipeline

**Commands**:
```bash
# Run all roadmap tests
uv run pytest tests/roadmap/ -v

# Run the full test suite
uv run pytest

# Lint
make lint
```

**Expected**: All tests pass. No lint errors.

---

## Phase 2: Defense-in-Depth (Optional, Next Sprint)

**Goal**: Add per-file size awareness and operator-visible startup warning.
**Effort**: ~4 hours
**Risk**: Low
**Prerequisite**: Phase 1 complete and merged

### Task 2.1: Add `_should_embed_inputs()` pre-check

**File**: `src/superclaude/cli/roadmap/executor.py`
**Add after** `_embed_inputs()` function (after line 70)

```python
# Per-file embed budget: no single file may exceed 50% of total embed budget.
# This is a policy decision (not derived from OS constraint) to prevent one large file
# from dominating the embed space. The total-size guard remains the authoritative safety check.
_PER_FILE_EMBED_LIMIT = _EMBED_SIZE_LIMIT // 2


def _should_embed_inputs(input_paths: list[Path], prompt_size: int) -> bool:
    """Pre-check whether inputs can safely be embedded in the -p argument.

    Uses stat() (fast metadata call, no file read) to estimate sizes.
    This is an approximation — the total-size guard in roadmap_run_step()
    remains the authoritative check after actual content is read.

    Returns False (fail closed) on any stat error.
    """
    if not input_paths:
        return True

    total = prompt_size
    for p in input_paths:
        try:
            file_size = Path(p).stat().st_size
        except OSError:
            return False  # Fail closed: can't stat → don't embed
        if file_size > _PER_FILE_EMBED_LIMIT:
            _log.debug(
                "File %s (%d bytes) exceeds per-file embed limit (%d bytes), "
                "routing to --file",
                p, file_size, _PER_FILE_EMBED_LIMIT,
            )
            return False
        total += file_size
    return total <= _EMBED_SIZE_LIMIT
```

**Then modify `roadmap_run_step()`** to call the pre-check before `_embed_inputs()`:
```python
    # Pre-check: can inputs be safely embedded based on file sizes?
    if step.inputs and not _should_embed_inputs(step.inputs, len(step.prompt.encode("utf-8"))):
        effective_prompt = step.prompt
        extra_args = [
            arg for input_path in step.inputs for arg in ("--file", str(input_path))
        ]
    else:
        # Existing composed-string guard path (from Task 1.2)
        embedded = _embed_inputs(step.inputs)
        composed = step.prompt + "\n\n" + embedded if embedded else step.prompt
        # ... rest of existing guard logic ...
```

**Test**: Add `tests/roadmap/test_per_file_guard.py` with cases:
- Single file at 70 KB (> `_PER_FILE_EMBED_LIMIT` ~60 KB) → routes to `--file`
- Two files at 30 KB each (< per-file, combined < total) → embeds inline
- Stat error → returns False (fail closed)

---

### Task 2.2: Add spec file startup warning

**File**: `src/superclaude/cli/roadmap/executor.py`
**Location**: Inside `execute_roadmap()`, after config validation, before `_build_steps()`

```python
    # Operator warning for large spec files
    try:
        spec_size = config.spec_file.stat().st_size
        if spec_size > _EMBED_SIZE_LIMIT:
            _log.warning(
                "Spec file %s is %d KB — some pipeline steps will use --file "
                "fallback mode instead of inline embedding.",
                config.spec_file.name, spec_size // 1024,
            )
    except OSError:
        pass  # Don't block pipeline on stat failure
```

**Test**: Add a test in `tests/roadmap/test_executor.py` that verifies the warning fires when spec file exceeds `_EMBED_SIZE_LIMIT`.

---

### Task 2.3: Export new constants for test access

**File**: `src/superclaude/cli/roadmap/executor.py`

Ensure `_PER_FILE_EMBED_LIMIT`, `_MAX_ARG_STRLEN`, and `_PROMPT_TEMPLATE_OVERHEAD` can be imported by test files (they already can since they're module-level, but verify the test imports work).

**Verification**: `uv run pytest tests/roadmap/ -v`

---

## Phase 3: Architectural Hardening (v2.26 Spike)

**Goal**: Validate and implement stdin prompt delivery to eliminate the entire failure class.
**Effort**: ~1 day (including validation)
**Risk**: Medium (depends on unconfirmed `claude` CLI behavior)
**Prerequisite**: Phase 1 merged; Phase 2 optional

### Task 3.1: Validation spike — stdin prompt delivery

**Create a test script** `scripts/validate-stdin-delivery.sh`:
```bash
#!/usr/bin/env bash
# V1: Basic stdin delivery
echo "What is 2+2? Reply with just the number." | claude --print --output-format text

# V2: Large prompt via stdin (>128 KB)
python3 -c "print('x' * 200000 + '\n\nWhat is 2+2?')" | claude --print --output-format text

# V3: Unicode and special characters
echo "Summarize: 日本語テスト — ñ, ü, €, 🎯" | claude --print --output-format text
```

**Pass criteria**: All three produce valid Claude responses. If V1 fails, stdin delivery is not viable — close the spike.

### Task 3.2: Process group compatibility test

Write a Python test that runs `claude --print` with stdin delivery inside a child process group (`os.setpgrp`), matching the pipeline's actual subprocess setup. Verify no broken pipe errors.

### Task 3.3: Implement `_start_with_stdin_prompt()` (only if 3.1 + 3.2 pass)

**File**: `src/superclaude/cli/pipeline/process.py`

Add to `ClaudeProcess`:
```python
_PROMPT_STDIN_THRESHOLD = 64 * 1024  # Prompts above 64 KB go via stdin

def _build_command_without_prompt(self) -> list[str]:
    """Build command without -p flag (for stdin delivery)."""
    cmd = [
        "claude", "--print", "--verbose",
        self.permission_flag, "--no-session-persistence",
        "--max-turns", str(self.max_turns),
        "--output-format", self.output_format,
    ]
    if self.model:
        cmd.extend(["--model", self.model])
    cmd.extend(self.extra_args)
    return cmd

def _start_with_stdin_prompt(self) -> subprocess.Popen:
    """Deliver large prompt via stdin to bypass MAX_ARG_STRLEN."""
    self.output_file.parent.mkdir(parents=True, exist_ok=True)
    self._stdout_fh = open(self.output_file, "w")
    self._stderr_fh = open(self.error_file, "w")

    popen_kwargs = {
        "stdin": subprocess.PIPE,
        "stdout": self._stdout_fh,
        "stderr": self._stderr_fh,
        "env": self.build_env(),
    }
    if hasattr(os, "setpgrp"):
        popen_kwargs["preexec_fn"] = os.setpgrp

    self._process = subprocess.Popen(
        self._build_command_without_prompt(), **popen_kwargs
    )
    self._process.stdin.write(self.prompt.encode("utf-8"))
    self._process.stdin.close()
    return self._process
```

Modify `start()`:
```python
def start(self) -> subprocess.Popen:
    prompt_size = len(self.prompt.encode("utf-8"))
    if prompt_size > _PROMPT_STDIN_THRESHOLD:
        _log.debug("Prompt size %d exceeds stdin threshold, using stdin delivery", prompt_size)
        return self._start_with_stdin_prompt()
    # ... existing Popen path unchanged ...
```

### Task 3.4: Add tests for stdin delivery path

**File**: `tests/pipeline/test_process_stdin.py` (new)

Test cases:
- Small prompt (< threshold) → uses `-p` path (unchanged)
- Large prompt (> threshold) → uses stdin path
- Verify stdin path produces correct output format
- Verify `_close_handles()` cleanup works for stdin path

### Task 3.5: Update Phase 1 constants (if Phase 3 ships)

If stdin delivery is implemented, the `_EMBED_SIZE_LIMIT` guard in executor.py becomes a performance optimization only (not a safety gate). The comment should be updated to reflect this:

```python
# Performance optimization: embed small inputs inline for better Claude context.
# Large inputs fall back to --file. ClaudeProcess handles the OS arg limit
# independently via stdin delivery for prompts > _PROMPT_STDIN_THRESHOLD.
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD
```

---

## Checklist Summary

### Phase 0 (BLOCKING — before anything else)
- [ ] Task 0.1: Empirical test of `--file` with bare path (15 min manual test)
- [ ] Decision gate: If broken → Phase 3 becomes P0; if working → proceed to Phase 1

### Phase 1 (P0 — this sprint)
- [ ] Task 1.1: Replace `_EMBED_SIZE_LIMIT` with derived constants
- [ ] Task 1.2: Change guard to measure full composed string
- [ ] Task 1.3: Rename and update fallback test
- [ ] Task 1.4: Add composed-string guard test
- [ ] Task 1.5: Run full test suite and lint
- [ ] Commit: `fix(roadmap): derive _EMBED_SIZE_LIMIT from MAX_ARG_STRLEN and guard full composed prompt`

### Phase 1.5 (if `--file` is broken — P0)
- [ ] Fix `remediate_executor.py:177` — switch from `--file` to inline embedding
- [ ] Fix fallback path in `roadmap/executor.py`, `validate_executor.py`, `tasklist/executor.py`
- [ ] Add integration test that verifies file content delivery through the fallback path
- [ ] Commit: `fix(pipeline): replace broken --file fallback with inline embedding`

### Phase 2 (next sprint, optional)
- [ ] Task 2.1: Add `_should_embed_inputs()` per-file pre-check
- [ ] Task 2.2: Add spec file startup warning
- [ ] Task 2.3: Verify constant exports for tests
- [ ] Commit: `feat(roadmap): add per-file embed guard and spec size warning`

### Phase 3 (v2.26 spike)
- [ ] Task 3.1: Validate stdin delivery (blocking gate)
- [ ] Task 3.2: Process group compatibility test
- [ ] Task 3.3: Implement `_start_with_stdin_prompt()` (if 3.1 passes)
- [ ] Task 3.4: Add stdin delivery tests
- [ ] Task 3.5: Update executor constants/comments
- [ ] Commit: `feat(pipeline): stdin prompt delivery for large prompts (bypass MAX_ARG_STRLEN)`
