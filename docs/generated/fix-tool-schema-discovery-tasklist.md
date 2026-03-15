# Fix Tasklist: Tool Schema Discovery Failure in Sprint Subprocess

## Context for Executing Agent

### What broke and why

`superclaude sprint run <tasklist-index.md> --start 2 --end 9` fails consistently
with Phase 2 exiting code 1. The root cause is that `claude` subprocesses spawned
by the sprint runner do not have tool schemas injected at session start when running
in `--print --output-format stream-json` mode. The model attempts to call `TodoWrite`
and `Bash` but their schemas are absent from the "discovered-tool set derived from
message history", causing `InputValidationError` on parameter types.

Evidence from `results/phase-2-output.txt`:
```
<tool_use_error>InputValidationError: TodoWrite failed:
The parameter `todos` type is expected as `array` but provided as `string`
This tool's schema was not sent to the API — it was not in the discovered-tool set
derived from message history.

<tool_use_error>InputValidationError: Bash failed:
The required parameter `command` is missing
An unexpected parameter `cmd` was provided
This tool's schema was not sent to the API — it was not in the discovered-tool set
derived from message history.
```

### The fix

Add `--tools` `default` to the `build_command()` method in
`src/superclaude/cli/pipeline/process.py`. This flag explicitly injects all
built-in tool schemas at session start, bypassing the message-history discovery
mechanism entirely.

**Validated**: The flag combination was confirmed to work in the exact subprocess
invocation mode (stream-json + verbose + no-session-persistence +
dangerously-skip-permissions). The `init` event from the validation run showed the
full tool list including `Bash`, `TodoWrite`, `Glob`, `Read`, `Edit`, `Write`, etc.
all present from the first message.

### Key files

| File | Purpose |
|------|---------|
| `src/superclaude/cli/pipeline/process.py` | **Edit this** — contains `build_command()` at line 69 |
| `tests/pipeline/test_process.py` | **Edit this** — add new test asserting `--tools default` present |
| `tests/sprint/test_process.py` | **Read this** — check for any `build_command` assertions to update |
| `tests/roadmap/test_executor.py` | **Read this** — check for command-building assertions |
| `.dev/releases/current/cross-framework-deep-analysis/` | Sprint directory for smoke test |

### Project conventions

- Use `uv run pytest` (never `python -m pytest` or `pytest` directly)
- Use `uv run pytest tests/pipeline/test_process.py -v` for targeted runs
- The project uses hatchling + uv; no need to reinstall after editing source files
  in `src/` (editable install via `make dev` already active)
- Commit convention: `fix(sprint): add --tools default to subprocess command`

---

## Tasks

### T01 — Read and understand current `build_command()` implementation

**File**: `src/superclaude/cli/pipeline/process.py`, lines 69–87

Read the method to understand the current command construction. Confirm:
- `--tools` flag is NOT present
- `extra_args` is appended at the end
- `--model` is conditional on `self.model` being non-empty

The fix inserts `"--tools", "default"` into the `cmd` list. Best placement is
immediately after `"--no-session-persistence"` (line 77) and before
`"--max-turns"` — keeping flags grouped logically (session control flags
together).

**Deliverable**: Confirm current state matches description. No file changes yet.

---

### T02 — Read existing test file to understand assertions that must be updated

**File**: `tests/pipeline/test_process.py`

Read the full file. Key test to be aware of:
- `test_required_flags` (line 36): asserts specific flags ARE in `cmd`. After the
  fix, `--tools` and `default` must also be assertable here OR in a new dedicated
  test. This test does NOT need to be modified — it uses positive assertions only.
- `test_stream_json_matches_sprint_flags` (line 111): same pattern — positive
  assertions. No modification needed.

Also read:
- `tests/sprint/test_process.py` — check for any assertions on `build_command()`
  output that would break if `--tools default` is added
- `tests/roadmap/test_executor.py` — same check

**Deliverable**: List of any tests that check `cmd` contents in a way that would
break (e.g., asserting exact length or specific index positions). These must be
updated alongside the fix.

---

### T03 — Apply the fix to `build_command()`

**File**: `src/superclaude/cli/pipeline/process.py`

Edit `build_command()` to add `"--tools", "default"` after
`"--no-session-persistence"`:

```python
def build_command(self) -> list[str]:
    """Build the claude CLI command."""
    cmd = [
        "claude",
        "--print",
        "--verbose",
        self.permission_flag,
        "--no-session-persistence",
        "--tools",
        "default",
        "--max-turns",
        str(self.max_turns),
        "--output-format",
        self.output_format,
        "-p",
        self.prompt,
    ]
    if self.model:
        cmd.extend(["--model", self.model])
    cmd.extend(self.extra_args)
    return cmd
```

**Deliverable**: `build_command()` in `pipeline/process.py` contains
`"--tools"` and `"default"` in the returned list.

---

### T04 — Add test asserting `--tools default` is present in command

**File**: `tests/pipeline/test_process.py`

Add a new test to `TestClaudeProcessCommand` class:

```python
def test_tools_default_in_command(self, tmp_path):
    """Regression test: --tools default must be present to ensure tool schema
    injection at session start (fixes InputValidationError on TodoWrite/Bash
    when schemas absent from discovered-tool set)."""
    p = ClaudeProcess(
        prompt="test",
        output_file=tmp_path / "out.txt",
        error_file=tmp_path / "err.txt",
    )
    cmd = p.build_command()
    assert "--tools" in cmd
    idx = cmd.index("--tools")
    assert cmd[idx + 1] == "default"
```

Also update `test_required_flags` to include `--tools` and `default` in its
assertions:

```python
def test_required_flags(self, tmp_path):
    p = ClaudeProcess(
        prompt="hello",
        output_file=tmp_path / "out.txt",
        error_file=tmp_path / "err.txt",
    )
    cmd = p.build_command()
    assert "claude" in cmd
    assert "--print" in cmd
    assert "--verbose" in cmd
    assert "--no-session-persistence" in cmd
    assert "--tools" in cmd
    assert "default" in cmd
    assert "--dangerously-skip-permissions" in cmd
    assert "-p" in cmd
    assert "hello" in cmd
```

Also update `test_stream_json_matches_sprint_flags` to assert `--tools default`:

```python
assert "--tools" in cmd
idx_tools = cmd.index("--tools")
assert cmd[idx_tools + 1] == "default"
```

**Deliverable**: New test `test_tools_default_in_command` added; two existing tests
updated with `--tools` / `default` assertions.

---

### T05 — Run the pipeline test suite and confirm all tests pass

```bash
uv run pytest tests/pipeline/test_process.py -v
```

Expected: all existing tests pass plus new `test_tools_default_in_command` passes.

If any test fails due to the added flags (e.g., index-based assertions), fix those
tests to use `cmd.index()` lookups instead of positional assumptions.

**Deliverable**: `tests/pipeline/test_process.py` — all tests green.

---

### T06 — Run broader sprint and roadmap test suites to confirm no regressions

```bash
uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v --tb=short 2>&1 | tail -40
```

These test suites use mocked subprocesses so they don't invoke the real `claude`
binary. The `build_command()` output is checked in several places. Confirm:
- No test fails due to unexpected `--tools default` in the command list
- If any test does fail, it will be due to an exact-match or positional assertion —
  update it to use `assert "--tools" in cmd` style

**Deliverable**: Full suite green. Note any tests updated and why.

---

### T07 — Smoke test with dry-run to confirm sprint configuration still loads

```bash
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --start 2 --end 9 \
  --dry-run
```

Expected output:
```
Dry run: 8 phases discovered
  Phase 2: ...
  Phase 3: ...
  ...
Would execute phases 2–9
```

This confirms the CLI still parses and the config loads correctly. The `--tools`
flag is not invoked at this stage (no subprocess is spawned in dry-run mode) so
this only validates the CLI layer is intact.

**Deliverable**: Dry-run completes with phases listed, no error.

---

### T08 — Verify the fix resolves the actual failure (optional live test)

> **WARNING**: This spawns a real claude subprocess and will run Phase 2 of the
> cross-framework-deep-analysis sprint. It costs tokens and takes ~5–10 minutes.
> Only run if you have budget and intent to resume the sprint.

```bash
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --start 2 --end 2 \
  --no-tmux
```

Watch the execution log:
```bash
superclaude sprint logs --follow
```

Expected: Phase 2 completes with `status: pass` or `status: partial` (not `error`).
The `InputValidationError` on `TodoWrite`/`Bash` should not appear in
`results/phase-2-output.txt`.

If Phase 2 still exits 1, check `results/phase-2-errors.txt` and
`results/phase-2-output.txt` for a new error class. The tool schema issue should
be resolved; any new failure is a different root cause.

**Deliverable**: Phase 2 exits with code 0 and no `InputValidationError` in output.

---

## Acceptance Criteria

| # | Criterion | How to verify |
|---|-----------|--------------|
| AC-1 | `build_command()` includes `--tools default` | `assert "--tools" in cmd and cmd[cmd.index("--tools")+1] == "default"` |
| AC-2 | `test_tools_default_in_command` passes | `uv run pytest tests/pipeline/test_process.py::TestClaudeProcessCommand::test_tools_default_in_command -v` |
| AC-3 | No existing tests broken | `uv run pytest tests/pipeline/ tests/sprint/ tests/roadmap/ -v` — all green |
| AC-4 | Dry-run still works | `superclaude sprint run ... --dry-run` — phases listed, no error |
| AC-5 | (If live test run) Phase 2 exits 0 | No `InputValidationError` in phase-2-output.txt |

---

## What NOT to do

- Do not add `--tools default` to `sprint/process.py` or any other file —
  `pipeline/process.py` is the single correct location (all consumers inherit from it)
- Do not change the `extra_args` mechanism — it exists for callers that need
  additional flags and must remain functional
- Do not modify the prompt in `sprint/process.py:build_prompt()` — the fix is
  purely at the CLI flag level
- Do not run `python -m pytest` — always use `uv run pytest`
