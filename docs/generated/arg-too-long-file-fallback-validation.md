# Validation: `--file` Fallback Mechanism in Roadmap Pipeline

**Date**: 2026-03-15
**Scope**: Read-only code investigation (no subprocess execution)
**Files examined**: 8 source files, 5 test files, 3 prior debate/analysis documents

---

## 1. What the Code Does

### Fallback Path (executor.py lines 173-192)

The `roadmap_run_step()` function in `src/superclaude/cli/roadmap/executor.py` uses a two-tier strategy for passing input files to `claude -p` subprocesses:

1. **Primary path (inline embedding)**: `_embed_inputs()` reads input files and wraps their contents in fenced markdown blocks. If the embedded content is <= `_EMBED_SIZE_LIMIT` (200KB), it is appended directly to the prompt string.

2. **Fallback path (--file flags)**: When embedded content exceeds `_EMBED_SIZE_LIMIT`, the executor instead passes bare filesystem paths via `--file` flags:
   ```python
   extra_args = [
       arg
       for input_path in step.inputs
       for arg in ("--file", str(input_path))
   ]
   ```

This produces CLI args like: `--file /absolute/path/to/spec.md --file /absolute/path/to/roadmap.md`

### Same Pattern in Three Executors

The identical `--file` fallback pattern appears in:
- `src/superclaude/cli/roadmap/executor.py` (line 188) - `_EMBED_SIZE_LIMIT = 200KB`
- `src/superclaude/cli/roadmap/validate_executor.py` (line 109) - `_EMBED_SIZE_LIMIT = 100KB`
- `src/superclaude/cli/tasklist/executor.py` (line 121) - `_EMBED_SIZE_LIMIT = 100KB`

### Direct Usage in Remediate Executor

`src/superclaude/cli/roadmap/remediate_executor.py` (line 177) uses `--file` unconditionally (not as a fallback) for the target file:
```python
extra_args=["--file", target_file],
```

### How Args Reach the CLI

`ClaudeProcess.build_command()` in `src/superclaude/cli/pipeline/process.py` appends `extra_args` to the end of the command list (line 86). The command is passed as a Python `list[str]` to `subprocess.Popen()`, so no shell interpolation occurs.

---

## 2. What the Tests Cover

### test_file_passing.py (line 108) - FULLY MOCKED

The `TestSizeGuardFallback.test_100kb_guard_fallback` test at line 108:

- Creates a file larger than `_EMBED_SIZE_LIMIT`
- **Mocks `ClaudeProcess` entirely** via `patch("superclaude.cli.roadmap.executor.ClaudeProcess")`
- Captures the `extra_args` kwarg passed to the mocked constructor
- Asserts `"--file"` appears in `extra_args` and the file path is present
- Asserts the warning log message fires

**What it validates**: The Python-side branching logic correctly detects oversized inputs and constructs the `extra_args` list with `--file` flags.

**What it does NOT validate**: Whether `claude` actually reads files when given `--file /absolute/path`. The mock replaces `ClaudeProcess` entirely, so no subprocess is spawned.

### test_process.py (line 72) - COMMAND BUILDING ONLY

The `test_extra_args` test verifies that `ClaudeProcess.build_command()` includes `--file` and `/tmp/spec.md` in the resulting command list. This is a unit test of command assembly; no subprocess runs.

### No Integration Tests

There are zero tests in the codebase that actually invoke `claude` with `--file /path/to/file` and verify the file content appears in the model's context. Every test mocks the subprocess boundary.

---

## 3. The `--file` Format Mismatch

### What `claude --help` Documents

Per the `claude --help` output (captured in the v2.09 debate transcript, dated 2026-03-05):

```
--file <specs...>  File resources to download at startup.
                   Format: file_id:relative_path (e.g., --file file_abc:doc.txt file_def:img.png)
```

### What the Code Passes

The code passes bare absolute filesystem paths: `--file /absolute/path/to/spec.md`

### Is This a Real Problem?

The documented `--file` format is `file_id:relative_path` -- a colon-separated pair where `file_id` is a remote identifier and `relative_path` is a local save location. This is described as a "file resources to download at startup" mechanism, meaning it fetches remote files by ID. It is NOT a local file injection mechanism.

When the code passes `--file /absolute/path/to/spec.md`, `claude` receives a string that:
- Contains no colon-separated `file_id` (unless it interprets everything before the first `:` in the path as a file_id, which would be an empty string since absolute paths start with `/`)
- Does not match the documented `file_id:relative_path` format

### Prior Analysis Agrees

The v2.09 adversarial debate transcript (`/.dev/releases/complete/v2.09-adversarial-v2/adversarial/file-passing-debate/debate-transcript.md`) explicitly called this out:

> "The `--file` flag is a **remote file download mechanism** that accepts `file_id:relative_path` pairs. It does NOT accept local filesystem paths and inject them as context."

The `arg-too-long-solution-validation.md` (lines 117-123) also flagged this:

> "The L3 debate surfaced that the **existing** `--file` fallback passes `("--file", str(input_path))` but `claude --help` documents `--file` as expecting `file_id:relative_path` format."

Both documents classify this as an open question requiring empirical validation.

---

## 4. Verdict: LIKELY BROKEN

**Confidence**: 80% broken, 20% undocumented-but-working

### Evidence Supporting "Broken"

1. **Format mismatch is clear**: The documented format is `file_id:relative_path` for remote file downloads; the code passes bare local paths. These are semantically incompatible.

2. **Never empirically tested**: No test in the codebase actually invokes `claude --file /path` and verifies file content appears. Every test mocks the subprocess.

3. **Prior debates concluded the same**: Two independent prior analyses (v2.09 debate, arg-too-long L3 debate) both concluded `--file` with bare paths is "semantically incorrect usage."

4. **Fallback rarely triggers**: The `_EMBED_SIZE_LIMIT` is 200KB (roadmap) or 100KB (validate/tasklist). Most pipeline artifacts are well under this. The fallback likely has never fired in production, which explains why the bug hasn't been noticed.

5. **The remediate executor uses it unconditionally** (line 177), which means if it IS broken, the remediation pipeline is also silently broken (the `--file` arg is simply ignored and the model operates without that file's context).

### Evidence Supporting "Might Work"

1. **`claude` may accept bare paths as undocumented behavior**: CLI tools sometimes accept more formats than documented. Without running `claude --file /path`, we cannot rule this out entirely.

2. **`claude` may silently ignore unrecognized `--file` args**: If it silently ignores them, the subprocess would still succeed (exit code 0) but without the file context. This would explain why no crash has been observed.

### Why "Silently Ignored" Is Still Broken

Even if `claude` does not crash when given `--file /bare/path`, the purpose of the fallback is to deliver file content to the model. If the file content is not delivered, the model operates without crucial context (spec files, prior roadmap outputs). The subprocess might produce output that looks plausible but lacks grounding in the input documents. This is a silent correctness failure.

---

## 5. Impact Assessment

| Component | Impact | Severity |
|-----------|--------|----------|
| `roadmap/executor.py` fallback | Files >200KB not delivered to model | **Medium** (rarely triggers) |
| `validate_executor.py` fallback | Files >100KB not delivered to model | **Medium** (rarely triggers) |
| `tasklist/executor.py` fallback | Files >100KB not delivered to model | **Medium** (rarely triggers) |
| `remediate_executor.py` unconditional use | Target file never delivered to model | **High** (always fires) |

The `remediate_executor.py` case (line 177) is the most concerning because it uses `--file` unconditionally, not as a fallback. If `--file` with bare paths is indeed broken, then the remediate pipeline has never correctly delivered the target file to the model.

---

## 6. Recommended Next Steps

### Immediate (15 min)

1. **Empirical test**: Run `claude --print --file /tmp/test.md -p "What is in the file I provided?"` with a known file and verify the response references the file content. This is the single fastest way to resolve the open question.

### If `--file` with bare paths is confirmed broken

2. **Fix remediate_executor.py first**: It uses `--file` unconditionally. Switch to inline embedding (read file, append to prompt) as the primary mechanism, matching the pattern in the other executors.

3. **Replace fallback in all three executors**: The fallback path should use stdin delivery (`Popen` with `stdin=PIPE` and `process.communicate(prompt_bytes)`) instead of `--file` flags. This was already recommended as solution 3A in the arg-too-long analysis and has no format ambiguity.

4. **Add integration test**: Create a test that actually invokes `claude` (or a test double) with the fallback path to verify file content delivery.

### If `--file` with bare paths works (undocumented behavior)

5. **Document the finding**: Note that `--file` accepts bare paths despite `claude --help` documenting `file_id:relative_path` format.

6. **Add regression test**: Pin the behavior with an integration test so future Claude CLI versions don't break it.

7. **Still consider stdin migration**: Relying on undocumented behavior is fragile. The stdin approach (3A) is architecturally sound and does not depend on any CLI flag semantics.

---

## Artifact Cross-References

| Document | Relevance |
|----------|-----------|
| `docs/generated/arg-too-long-solution-validation.md` (lines 117-135) | First identification of `--file` format mismatch as open question |
| `.dev/releases/complete/v2.09-adversarial-v2/adversarial/file-passing-debate/debate-transcript.md` | Detailed analysis concluding `--file` is a "remote file download mechanism" |
| `src/superclaude/cli/roadmap/executor.py` (lines 183-189) | The fallback code under investigation |
| `src/superclaude/cli/roadmap/remediate_executor.py` (line 177) | Unconditional `--file` usage (highest impact if broken) |
| `tests/roadmap/test_file_passing.py` (line 108) | Mocked test that validates branching logic but not CLI behavior |
