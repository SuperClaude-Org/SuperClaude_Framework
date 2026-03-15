# Solution Brainstorm: Preventing `OSError [Errno 7] Argument list too long`

**Primary root cause**: RC1 — `_EMBED_SIZE_LIMIT = 200 * 1024` set above `MAX_ARG_STRLEN` (128 KB)
**Secondary causes**: RC2 (unbounded spec file, no per-file guard), RC3 (large prompts via `-p` CLI arg)
**Date**: 2026-03-14

---

## Codebase Context

**Key files and locations**:
- `src/superclaude/cli/roadmap/executor.py:54` — `_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB`
- `src/superclaude/cli/roadmap/executor.py:173-192` — embed/fallback decision logic
- `src/superclaude/cli/pipeline/process.py:69-87` — `build_command()` always uses `-p self.prompt`
- `tests/roadmap/test_file_passing.py:108` — test named `"100KB guard"` but tests against 200 KB constant (test drift mirrors the bug)

**Critical observation from test file**:
The test docstring at line 106 reads `"100KB guard triggers fallback to --file flags"` but the test body uses `_EMBED_SIZE_LIMIT + 1024` as the threshold. This means the test passes with the miscalibrated constant — it validates the guard fires above 200 KB, not above 128 KB. The test is verifying the wrong invariant.

**`claude` CLI prompt delivery options** (from `claude --help`):
- `-p <prompt>` / `--print` — current mechanism (prompt as CLI arg)
- `--input-format stream-json` — accepts streaming JSON on stdin
- `--file <specs...>` — file resource attachment (different from prompt delivery)
- No native `--prompt-file` flag exists; stdin with `--input-format text` is unconfirmed

---

## Solution Space

### Level 1: Immediate Fix (RC1 — addresses this crash, low risk)

#### 1A: Derive `_EMBED_SIZE_LIMIT` from `MAX_ARG_STRLEN` with a safety margin

**Concept**: Replace the magic constant with a derived value that encodes its relationship to the OS constraint. This prevents future drift by making the relationship explicit.

```python
# Current (broken):
_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB  ← comment/value mismatch

# Proposed:
import resource
_MAX_ARG_STRLEN = 128 * 1024   # Linux kernel MAX_ARG_STRLEN (compile-time constant)
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024   # Conservative estimate for prompt template
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD  # ~120 KB
```

**Why 8 KB overhead**: The largest prompt template (`build_spec_fidelity_prompt`) is ~4.3 KB. 8 KB provides 2× safety margin for template growth.

**Trade-offs**:
- ✅ One-line conceptual change, minimum blast radius
- ✅ Self-documenting — future readers understand the derivation
- ✅ Prevents the constant from drifting above the OS limit again
- ❌ Does not prevent RC2 or RC3 from causing future failures as inputs grow
- ❌ Still relies on a single constant rather than measuring the actual `-p` argument size

**Test change required**: `test_file_passing.py:108` must be updated to assert fallback fires below `_MAX_ARG_STRLEN`, not at `_EMBED_SIZE_LIMIT + 1024`. The test name `"100KB guard"` was honest; the implementation drifted away from it.

---

#### 1B: Guard against total `-p` argument size, not just embedded content size

**Concept**: The current guard measures `len(embedded.encode("utf-8"))` — the embedded portion only. The prompt template is added after the check passes. Change the guard to measure the full composed string.

```python
# Current guard (measures embedded only):
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded

# Proposed guard (measures full -p argument):
composed = step.prompt + "\n\n" + embedded if embedded else step.prompt
if len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = composed
    extra_args = []
else:
    effective_prompt = step.prompt
    extra_args = [arg for path in step.inputs for arg in ("--file", str(path))]
```

**Trade-offs**:
- ✅ Closes the template-overhead blind spot the RC3 debate identified
- ✅ Measures the actual string that will become the `-p` value
- ✅ Compatible with 1A — both can be applied together
- ❌ Still requires `_EMBED_SIZE_LIMIT` to be correctly calibrated
- ❌ Does not handle the case where `step.prompt` alone exceeds `MAX_ARG_STRLEN`

**Recommended**: Apply 1A + 1B together. They address complementary gaps in the same guard.

---

### Level 2: Structural Improvement (RC2 — per-file awareness, medium effort)

#### 2A: Per-file size guard before accumulation

**Concept**: Add a pre-check that evaluates each input file individually before `_embed_inputs()` combines them. A single file exceeding a per-file budget immediately routes to `--file` without computing the combined total.

```python
_PER_FILE_EMBED_LIMIT = 64 * 1024  # No single file may exceed 64 KB inline

def _should_embed_inputs(input_paths: list[Path], prompt_size: int) -> bool:
    """True if all inputs can safely be embedded in the -p argument.

    Checks:
    1. Each individual file is within _PER_FILE_EMBED_LIMIT
    2. Combined total (all files + prompt) is within _EMBED_SIZE_LIMIT
    """
    total = prompt_size
    for p in input_paths:
        try:
            file_size = Path(p).stat().st_size
        except OSError:
            return False  # Fail closed: can't stat → don't embed
        if file_size > _PER_FILE_EMBED_LIMIT:
            return False  # Single file too large
        total += file_size
    return total <= _EMBED_SIZE_LIMIT
```

**Why 64 KB per-file**: The spec file alone (117.9 KB) would trip this limit independently, routing to `--file` before `roadmap.md` is even considered. It also catches the extract step's earlier failure where a single file exceeded the total budget.

**Trade-offs**:
- ✅ Addresses RC2 — the unbounded single-file problem
- ✅ Uses `.stat().st_size` (fast, no read) for the per-file check
- ✅ Fails closed on stat errors
- ✅ Catches edge case where one huge file + tiny prompt would still pass a total-only guard
- ❌ 64 KB per-file limit is conservative — useful pipeline files (extraction, roadmap) are 35 KB, fitting fine
- ❌ Two constants to maintain instead of one

---

#### 2B: Warn on spec file size at pipeline entry

**Concept**: Check the spec file size when `execute_roadmap()` is called and emit a WARNING (not a failure) if it exceeds a threshold. This surfaces the risk before the pipeline runs.

```python
_SPEC_FILE_WARN_THRESHOLD = 80 * 1024  # 80 KB — warn if spec is large

def execute_roadmap(config: RoadmapConfig, ...) -> None:
    spec_size = config.spec_file.stat().st_size
    if spec_size > _SPEC_FILE_WARN_THRESHOLD:
        _log.warning(
            "Spec file %s is %d KB — larger specs may trigger embed fallback "
            "to --file mode at some pipeline steps. Consider condensing if "
            "pipeline steps fail with OSError [Errno 7].",
            config.spec_file, spec_size // 1024,
        )
```

**Trade-offs**:
- ✅ No code path change — purely informational
- ✅ Gives operators early warning before a multi-hour pipeline run fails at step 9
- ❌ Does not prevent the crash — purely advisory
- ❌ A second threshold constant to maintain

---

### Level 3: Architectural Hardening (RC3 — eliminates the class, higher effort)

#### 3A: Write large prompts to temp files and pass via stdin

**Concept**: Modify `ClaudeProcess.start()` to detect when the prompt exceeds a safe threshold and write it to a temp file, then pipe it to the subprocess via stdin using `--input-format text`. This bypasses `MAX_ARG_STRLEN` entirely for prompt delivery.

```python
_PROMPT_FILE_THRESHOLD = 64 * 1024  # Prompts above 64 KB go via stdin

def start(self) -> subprocess.Popen:
    if len(self.prompt.encode("utf-8")) > _PROMPT_FILE_THRESHOLD:
        return self._start_with_stdin_prompt()
    # ...existing Popen path...

def _start_with_stdin_prompt(self) -> subprocess.Popen:
    """Deliver large prompt via stdin to bypass MAX_ARG_STRLEN."""
    cmd = self._build_command_without_prompt()  # omit -p flag
    # claude reads prompt from stdin when -p is absent with --print
    self._process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=self._stdout_fh,
        stderr=self._stderr_fh,
        env=self.build_env(),
        preexec_fn=os.setpgrp if hasattr(os, "setpgrp") else None,
    )
    self._process.stdin.write(self.prompt.encode("utf-8"))
    self._process.stdin.close()
    return self._process
```

**Prerequisite**: Verify that `claude --print` reads the prompt from stdin when `-p` is absent. From `claude --help`: the prompt is listed as a positional argument (`[prompt]`), suggesting stdin may work. **Must be tested before implementing.**

**Trade-offs**:
- ✅ Eliminates the OS arg limit as a failure mode for prompts of any size
- ✅ Localized to `ClaudeProcess` — no changes to executor logic needed
- ✅ Transparent to callers — same interface, different transport
- ❌ Requires validation that `claude --print` accepts stdin prompt delivery
- ❌ Slightly more complex subprocess lifecycle (stdin pipe management)
- ❌ Stdin + stdout pipes may interact with signal handling (test carefully)

---

#### 3B: Write large prompts to temp files and pass via `--file`

**Concept**: Alternative to 3A — write the prompt to a named temp file and pass via `--file`. Unlike 3A, this is confirmed to work (the existing `--file` fallback already passes input files this way).

```python
import tempfile

def _start_with_prompt_file(self) -> subprocess.Popen:
    """Write prompt to temp file and pass via --file to bypass MAX_ARG_STRLEN."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".prompt.txt", delete=False, encoding="utf-8"
    )
    tmp.write(self.prompt)
    tmp.close()
    self._prompt_tmp_path = Path(tmp.name)

    cmd = ["claude", "--print", "--verbose", self.permission_flag,
           "--no-session-persistence", "--max-turns", str(self.max_turns),
           "--output-format", self.output_format,
           "--file", str(self._prompt_tmp_path),  # prompt as file
    ]
    # ... Popen with cleanup in _close_handles()
```

**Note**: This assumes `--file` can deliver the main prompt content, not just auxiliary resources. The `--file` flag docs say "File resources to download at startup" — semantics differ from `-p`. **Requires validation.**

**Trade-offs**:
- ✅ Uses already-validated mechanism (`--file` already works for inputs)
- ✅ No stdin pipe complexity
- ❌ Temp file cleanup required (must delete on process exit)
- ❌ Semantics of `--file` for prompt delivery vs resource attachment are unclear

---

#### 3C: Structural separation — write prompts to output dir, pass as `--file`

**Concept**: Architectural redesign where all step prompts are written to the output directory as `<step-id>-prompt.txt` files before the subprocess is launched. The subprocess always receives the prompt via `--file`, never via `-p`. This is the maximal architectural fix.

**Trade-offs**:
- ✅ Complete elimination of the OS arg limit as a failure mode
- ✅ Prompts become inspectable artifacts (debugging benefit)
- ✅ No size checks needed anywhere — all prompts go via file
- ❌ Largest change surface — touches `ClaudeProcess`, `executor.py`, all tests
- ❌ Prompt files accumulate in output dir unless cleaned up
- ❌ Requires `--file` to work as a prompt delivery mechanism (unconfirmed)

---

## Recommended Implementation Path

### Phase 1: Stop the Bleeding (this sprint, ~2 hours)

Apply **1A + 1B together** in `executor.py`:
1. Define `_MAX_ARG_STRLEN = 128 * 1024` as a named constant
2. Set `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`
3. Set `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`
4. Change guard to measure `step.prompt + "\n\n" + embedded` (full composed string)
5. Fix `test_file_passing.py:108` — test must assert fallback fires below `_MAX_ARG_STRLEN`

**Expected outcome**: spec-fidelity step proceeds; 152.1 KB combined embed triggers fallback to `--file`; pipeline continues.

### Phase 2: Prevent Recurrence (next sprint, ~4 hours)

Apply **2A** (per-file guard) and **2B** (startup warning):
1. Add `_should_embed_inputs()` with per-file size check
2. Add spec file size warning at `execute_roadmap()` entry
3. Add tests: single 70 KB file routes to `--file`; startup warning fires at 80 KB spec

### Phase 3: Architectural Hardening (v2.26 candidate, ~1 day)

Validate and implement **3A** (stdin delivery) or **3C** (prompt-as-file):
1. Prototype: confirm `claude --print` reads prompt from stdin when `-p` is absent
2. If confirmed: implement `_start_with_stdin_prompt()` in `ClaudeProcess`
3. Add prompt size threshold: prompts > 64 KB use stdin delivery
4. Remove all size-limit guards from `executor.py` — they become unnecessary

---

## Open Questions

| # | Question | Blocking for Phase |
|---|----------|-------------------|
| OQ-1 | Does `claude --print` accept prompt from stdin when `-p` is absent? | Phase 3 |
| OQ-2 | Does `--file` deliver content as prompt context or as named resource? | Phase 3 |
| OQ-3 | What is the actual `_PROMPT_TEMPLATE_OVERHEAD` for the largest template? (`build_spec_fidelity_prompt` = 4.3 KB; 8 KB conservative) | Phase 1 (verify) |
| OQ-4 | Should the per-file limit (2A) and the total limit (1A) be the same constant or separate? | Phase 2 |
| OQ-5 | Should oversized prompt files be retained as debug artifacts or deleted? | Phase 3 |

---

## Summary Table

| Solution | RC Addressed | Risk | Effort | Prevents Recurrence |
|----------|-------------|------|--------|-------------------|
| 1A: Derive limit from `MAX_ARG_STRLEN` | RC1 | Low | XS | Partial (prevents constant drift) |
| 1B: Guard full composed string | RC1 | Low | XS | Partial (closes template blind spot) |
| 2A: Per-file size guard | RC2 | Low | S | Yes (for single-file overflows) |
| 2B: Startup size warning | RC2 | None | XS | No (advisory only) |
| 3A: Stdin prompt delivery | RC3 | Medium | M | Yes (eliminates class) |
| 3B: Prompt via `--file` | RC3 | Medium | M | Yes (eliminates class, if validated) |
| 3C: All prompts as files | RC3 | High | L | Yes (maximal hardening) |

**Recommended immediate action**: Apply 1A + 1B. Fix the test. Unblock the pipeline run.
