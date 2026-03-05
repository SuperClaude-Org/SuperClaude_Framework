# Adversarial Debate Verdict: Sprint CLI Stall Root Cause

## Metadata
- Generated: 2026-03-04
- Depth: deep (3 rounds: initial positions, empirical testing, convergence)
- Convergence: 95% (unanimous on corrected diagnosis)
- Advocates: Opus (prosecution — fix won't work), Haiku (defense — fix will work)

## Original Diagnosis (INCORRECT)

**Claimed**: `CLAUDECODE=""` in `build_env()` triggers nested session detection because Claude Code checks for variable existence.

**Proposed Fix**: Change `env["CLAUDECODE"] = ""` to `env.pop("CLAUDECODE", None)`.

## Debate Outcome

### Round 1: Opus Prosecution — 5 Arguments Against the Fix

| # | Argument | Confidence | Verdict |
|---|----------|------------|---------|
| 1 | Binary shows `==="1"` strict equality — `""` already bypasses guard | 85% | **CONFIRMED** |
| 2 | Exit code -9 (SIGKILL) inconsistent with exit(1) from permission check | 92% | **CONFIRMED** |
| 3 | Diagnostic test ran with inherited CLAUDECODE=1, not CLAUDECODE="" | 78% | **PARTIALLY CONFIRMED** |
| 4 | 0 bytes + SIGKILL + 89s duration points to resource kill, not permission check | 88% | **REFINED** (see below) |
| 5 | Tmux may be involved | 65% | **REFUTED** (tmux not available in env) |

### Round 2: Empirical Verification

| Test | Input | Result | Conclusion |
|------|-------|--------|------------|
| `CLAUDECODE=""` simple prompt | `"Say: HELLO"` max-turns 1 | `HELLO` (success) | Old code bypasses guard correctly |
| `CLAUDECODE="1"` simple prompt | `"Say: TEST"` max-turns 1 | Error: nested sessions | Guard fires on `"1"` only |
| `CLAUDECODE=""` with @file (tiny) | `@/tmp/tiny.txt` max-turns 1 | Success (40B output) | @file works with small files |
| `CLAUDECODE=""` with @file (12KB) | `@phase-1-tasklist.md` max-turns 3 | 0B, runs until killed | **HANGS** — subprocess doing work but no stdout |
| `CLAUDECODE=""` with /sc:task-unified | Skill invocation, max-turns 3 | 0B, runs until killed | **HANGS** — same pattern |
| `CLAUDECODE=""` file read (no @) | pyproject.toml via tool use | `4.2.0` (success, 6B) | Tool use works fine |
| setpgrp vs no setpgrp | Tool-using prompt | Both succeed | Process groups not the issue |

### Round 3: Convergence — True Root Cause

**Both advocates converge on the corrected diagnosis:**

The sprint CLI stall is NOT caused by the `CLAUDECODE` environment variable. The actual issue is:

1. **`--output-format text` buffers ALL output until the session completes.** With `claude --print --output-format text`, stdout only receives content when the entire agentic session finishes. During execution (tool use, file reads, skill loading), the output file remains at 0 bytes.

2. **The sprint prompt triggers a complex multi-turn agentic session.** The prompt contains `@<12KB file>` + `/sc:task-unified` + 50 max turns. This creates a session that legitimately runs for many minutes (potentially hours) without producing text output.

3. **The user likely killed the sprint** (Ctrl+C or `superclaude sprint kill`) after observing 0 output and apparent stall. The signal handler sends SIGTERM → wait 10s → SIGKILL to the process group, producing exit code -9.

4. **The sprint monitor cannot distinguish "working but no output yet" from "stuck"** because `--output-format text` provides no incremental output.

## Confirmed Root Causes (Multiple)

### Root Cause 1: Output Format Creates False Stall Appearance
- **Severity**: HIGH
- **File**: `src/superclaude/cli/sprint/process.py:79-95`
- **Issue**: `--output-format text` produces 0 bytes until session completion
- **Fix**: Change to `--output-format stream-json` (requires `--verbose` flag in current Claude Code version) OR pipe through a stream processor
- **Alternative Fix**: Accept that output monitoring will show 0 bytes during execution and adjust TUI/monitor to not classify this as stalled

### Root Cause 2: No Incremental Progress Signal
- **Severity**: MEDIUM
- **File**: `src/superclaude/cli/sprint/monitor.py`, `src/superclaude/cli/sprint/tui.py`
- **Issue**: Monitor thread watches output file size, which stays at 0. TUI shows "STALLED" after 60s of no growth. User sees "stalled" and kills the process.
- **Fix**: Either use `stream-json` format for incremental updates, or monitor the `claude` process's stderr/activity differently

### Root Cause 3: @file Expansion Creates Very Large Prompts
- **Severity**: LOW (not a bug, but a performance concern)
- **Issue**: `@<path>` in the prompt expands the full 12KB file into the context window before the first turn
- **Mitigation**: Consider whether the prompt should reference the file path for Claude to read via tools instead of @-expanding it inline

## Status of Applied Fix (env.pop)

The `env.pop("CLAUDECODE", None)` change is **not harmful but not the fix for this issue**. It is better hygiene than `env["CLAUDECODE"] = ""` and should be kept as a defensive measure. But it does not address the actual stall.

## Recommended Fixes (Priority Order)

1. **P0**: Change `--output-format text` to `json` in `build_command()`, then extract the text response from the JSON. This allows the sprint to detect when the subprocess is actually done vs still running.

2. **P1**: Adjust the TUI stall detection to account for text-mode buffering — don't classify 0-byte output as "stalled" when the process is still alive and consuming CPU.

3. **P2**: Consider using `--output-format stream-json` (if Claude Code supports it without `--verbose`) to get incremental output for real-time monitoring.

4. **P3**: Replace `@<path>` in the prompt with a directive for Claude to read the file via tools, reducing initial prompt size.

## Scoring

| Advocate | Initial Position | Final Position | Score |
|----------|-----------------|----------------|-------|
| Opus (prosecution) | Fix won't work (82% conf) | **CORRECT** — fix addresses wrong root cause | Winner |
| Haiku (defense) | Fix will work (88% conf) | Conceded after empirical evidence | — |

**Debate quality**: High. The prosecution's static analysis of the binary guard (`==="1"`) was the key insight that redirected investigation. Empirical testing in Round 2 confirmed the prosecution's position and revealed the true root cause.

---

## Implementation Context for Tasklist Generation

### Affected Files (Complete Inventory)

| File | Lines | Role | Changes Needed |
|------|-------|------|----------------|
| `src/superclaude/cli/sprint/process.py` | 212 lines | Subprocess lifecycle, command construction | **P0**: Change `--output-format` in `build_command()` |
| `src/superclaude/cli/sprint/monitor.py` | 130 lines | Daemon thread watching output file | **P1**: Adapt signal extraction to new output format |
| `src/superclaude/cli/sprint/tui.py` | 241 lines | Rich-based terminal dashboard | **P1**: Adjust stall display logic |
| `src/superclaude/cli/sprint/executor.py` | 248 lines | Core orchestration loop | **P1**: Parse new output format for status determination |
| `src/superclaude/cli/sprint/models.py` | 222 lines | Enums, dataclasses, pure data types | May need new fields for stream progress |
| `src/superclaude/cli/sprint/commands.py` | 219 lines | Click CLI group and subcommands | No changes expected |
| `src/superclaude/cli/sprint/config.py` | 166 lines | Phase discovery, validation, config loading | No changes expected |
| `src/superclaude/cli/sprint/logging_.py` | (check) | Sprint logger, status reader, log tailer | May need updates for new output format |
| `src/superclaude/cli/sprint/tmux.py` | (check) | Tmux session management | No changes expected |

### Current Command Construction (`process.py:79-95`)

The exact command built by `ClaudeProcess.build_command()`:

```python
cmd = [
    "claude",
    "--print",
    self.config.permission_flag,          # "--dangerously-skip-permissions"
    "--no-session-persistence",
    "--max-turns", str(self.config.max_turns),  # "50"
    "--output-format", "text",            # <-- ROOT CAUSE: buffers ALL output
    "-p", self.build_prompt(),
]
```

### Claude CLI `--output-format` Options (from `claude --help`)

```
--output-format <format>  Output format (only works with --print):
                          "text" (default),
                          "json" (single result),
                          "stream-json" (realtime streaming)
                          (choices: "text", "json", "stream-json")
```

Key behaviors observed during diagnostic session:
- `text`: Buffers ALL output until session fully completes. Output file stays 0 bytes throughout multi-turn execution. Only writes when the session ends.
- `json`: Single JSON blob at completion (same buffering behavior as text, but structured).
- `stream-json`: Emits newline-delimited JSON objects incrementally as the session progresses. Each tool use, message, and result produces a JSON line.

There is also a related flag observed in `claude --help`:
```
--include-partial-messages  Include partial message chunks as they arrive
                            (only works with --print and --output-format=stream-json)
```

### Current Monitor Design (`monitor.py:65-89`)

The monitor daemon thread polls the output file every 0.5 seconds:

```python
def _poll_once(self):
    size = self.output_path.stat().st_size
    self.state.output_bytes = size
    if size > self._last_read_pos:
        self.state.last_growth_time = now
        self.state.stall_seconds = 0.0  # reset stall on growth
        new_text = self._read_new_bytes(size)
        self._extract_signals(new_text)
    else:
        # No growth -- update stall counter
        self.state.stall_seconds = now - self.state.last_growth_time
```

Signal extraction (`monitor.py:110-129`) parses raw text for:
- Task IDs: regex `T\d{2}\.\d{2}` (e.g., T01.03)
- Tool names: `Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task`
- Files changed: `(?:modified|created|edited|wrote|updated)\s+[`'"]?([^\s`'"]+\.\w+)`

With `stream-json`, these patterns would need to parse JSON lines instead of raw text.

### Current TUI Stall Display (`tui.py:196-203`)

```python
stall_display = ms.stall_status  # "STALLED" if >60s, "thinking..." if >30s, "active"
stall_style = (
    "bold red blink" if stall_display == "STALLED"
    else "yellow" if stall_display == "thinking..."
    else "green"
)
```

The `MonitorState.stall_status` property (`models.py:208-213`):
```python
@property
def stall_status(self) -> str:
    if self.stall_seconds > 60:
        return "STALLED"
    if self.stall_seconds > 30:
        return "thinking..."
    return "active"
```

With `--output-format text`, `stall_seconds` climbs from 0 immediately and never resets because the output file never grows. TUI shows `STALLED` after 60 seconds even though claude is actively working.

### Current Result Parsing (`executor.py:202-247`)

`_determine_phase_status()` reads the result file and output file:
```python
if exit_code == 124: return PhaseStatus.TIMEOUT
if exit_code != 0: return PhaseStatus.ERROR
if result_file.exists():
    # Searches for EXIT_RECOMMENDATION: CONTINUE/HALT
    # Searches for status: PASS/FAIL/PARTIAL
if output_file.exists() and output_file.stat().st_size > 0:
    return PhaseStatus.PASS_NO_REPORT
return PhaseStatus.ERROR  # 0 bytes output = error
```

With `--output-format json`, the output file would contain a JSON object, and the result file is still written by the claude agent itself (via the prompt's Completion Protocol). The output format change primarily affects the monitor, not the result parser — unless the JSON wrapper interferes with raw text result detection.

With `--output-format stream-json`, the output file would contain multiple JSON lines. The final text response is in the last `assistant` message. The result file is still written separately by the agent.

### Environment Variables Present During Sprint Execution

Observed in diagnostic session (`env | grep -i claude`):
```
ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=cli
```

The `env.pop("CLAUDECODE", None)` fix already applied at `process.py:97-101` is correct hygiene but was not the root cause. Both `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` should be popped. Current state of the file after the (already applied) fix:

```python
def build_env(self) -> dict[str, str]:
    """Build environment for the child process."""
    env = os.environ.copy()
    # Claude Code checks for the *existence* of CLAUDECODE to detect nested
    # sessions.  Setting it to "" is not enough — we must remove it entirely.
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    return env
```

**NOTE**: The debate established that `CLAUDECODE=""` actually DOES bypass the guard (strict `==="1"` check in binary). However, the `env.pop` approach is still better hygiene and should be kept. The implementing agent should NOT revert this change.

### Prompt Structure (`process.py:35-77`)

The prompt passed via `-p` is ~1560 bytes and structured as:
```
/sc:task-unified Execute all tasks in @{absolute_path_to_phase_file} --compliance strict --strategy systematic

## Execution Rules
- Execute tasks in order (T{NN}XX.01, T{NN}XX.02, etc.)
- For STRICT tier tasks: use Sequential MCP for analysis...
- For STANDARD tier tasks: run direct test execution...
...

## Completion Protocol
When ALL tasks in this phase are complete:
1. Write a phase completion report to {result_file} containing:
   - YAML frontmatter...
   - The literal string EXIT_RECOMMENDATION: CONTINUE or HALT
...

## Important
- This is Phase {N} of a multi-phase sprint
- Previous phases have already been executed in separate sessions
- Do not re-execute work from prior phases
```

The `@{path}` syntax is a Claude Code file reference that expands inline. For phase-1-tasklist.md this adds ~12KB to the context. The P3 recommendation to replace `@{path}` with a "read this file" instruction would reduce initial prompt size but add a tool-use turn.

### Execution Timing Context

From the execution log of the failed run:
```json
{"event": "phase_complete", "phase": 1, "status": "error", "exit_code": -9,
 "started_at": "2026-03-04T15:09:03.057954+00:00",
 "finished_at": "2026-03-04T15:10:32.165686+00:00",
 "duration_seconds": 89.107732, "output_bytes": 0}
```

- Duration: 89 seconds (1m 29s)
- Exit code: -9 (SIGKILL, from process group kill via `os.killpg(pgid, signal.SIGKILL)`)
- Output bytes: 0
- Error file: 0 bytes

This timeline is consistent with: user sees TUI showing "STALLED" (after 60s of 0 output) → waits ~30 more seconds → kills sprint (Ctrl+C or `superclaude sprint kill`) → SignalHandler sets `shutdown_requested` → executor calls `proc_manager.terminate()` → SIGTERM then SIGKILL after 10s → exit code -9.

### Test Files

Existing sprint tests that will need updating:
```
tests/sprint/test_cli_contract.py   (modified in current branch)
tests/sprint/test_config.py         (modified in current branch)
tests/sprint/test_e2e_halt.py       (modified in current branch)
tests/sprint/test_e2e_success.py    (modified in current branch)
tests/sprint/test_executor.py       (modified in current branch)
tests/sprint/test_process.py        (modified in current branch)
tests/sprint/test_regression_gaps.py (modified in current branch)
```

All of these are already modified on the current branch (`v2.05-sprint-cli-specifications`). The implementing agent should read them to understand the existing test patterns before writing new tests.

### stream-json Output Format Structure

When using `--output-format stream-json`, Claude Code emits newline-delimited JSON. Each line is a JSON object with a `type` field. Relevant types for the monitor:

- `{"type": "assistant", "message": {...}}` — assistant text output
- `{"type": "tool_use", "tool": "Read", ...}` — tool invocation
- `{"type": "tool_result", ...}` — tool result
- `{"type": "result", "result": "...", ...}` — final session result

The monitor could parse these JSON lines to extract:
- Task IDs and tool names from `tool_use` events
- File changes from `tool_result` events
- Progress signals from any `assistant` messages mentioning task completions

This is significantly richer than text-mode monitoring but requires JSON parsing in the monitor thread.

### Design Constraints for Implementation

1. **Backward compatibility**: The sprint CLI should still work if someone has an older claude binary that doesn't support `stream-json` well. Consider a `--output-format` pass-through option or feature detection.

2. **Monitor thread safety**: `OutputMonitor._poll_once()` runs in a daemon thread. Any JSON parsing must handle partial writes (a JSON line being written mid-poll) gracefully.

3. **Result file independence**: The result file (`phase-N-result.md`) is written by the claude agent via the prompt's Completion Protocol, NOT by the sprint CLI. It is separate from stdout. The `_determine_phase_status()` parser should NOT need changes for the output format — it reads the result file, not stdout.

4. **TUI update frequency**: Currently 2 Hz (`refresh_per_second=2` in `tui.py:65`). With stream-json, the monitor will have much more frequent data. The TUI refresh rate doesn't need to increase — the monitor thread can buffer.

5. **File handle management**: `process.py:111-112` opens stdout/stderr file handles. With stream-json, the stdout file will contain JSON lines, and the monitor needs to handle this. The stderr file remains plain text (claude debug/error output).
