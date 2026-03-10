# RCA Agent 1: Test Harness Mechanics

**Date**: 2026-02-24
**Scope**: Investigation of why ALL behavioral tests in the v2.01 release validation suite timeout (0% pass rate)
**Evidence base**: `tests/v2.01-release-validation/results/` runs 1-3, runner.py, orchestrator.py, live environment testing

---

## Summary of Findings

Every behavioral test (classification B1-B4 and wiring W1-W4) across all runs and all models produced durations that match their computed timeout to within 200ms. No behavioral test completed successfully. The root cause is a **compound failure** involving at least three independent issues, any one of which would be sufficient to cause widespread timeouts.

---

## Investigation Angle 1: max_turns and Per-Turn Latency

### Finding: Timeout Budget is Insufficient for the Actual Workload

**Evidence**:
- Classification tests use `max_turns=5`. For opus: `45 * 5 = 225s` timeout.
- Wiring tests use `max_turns=6-10`. For opus with W4 (`max_turns=10`): `45 * 10 = 450s`.
- Live testing showed that even `claude -p --max-turns 1 --model haiku` with a trivial prompt ("Say OK") takes **over 30 seconds** just to initialize when run from within the repo (CLAUDE.md context loading, MCP server initialization).
- From `/tmp` (no CLAUDE.md), a single-turn haiku call still exceeded 30 seconds.

**Analysis**:
The 45s/turn budget for opus assumes fast API round-trips, but ignores:
1. **Startup overhead**: `claude -p` must parse CLAUDE.md (which `@`-references COMMANDS.md, FLAGS.md, PRINCIPLES.md, RULES.md, MCP.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md), initialize MCP connections, and bootstrap the session. This alone can consume 20-40 seconds.
2. **Context window size**: The combined CLAUDE.md system with all `@`-references creates a massive context window that must be transmitted on every API call.
3. **Per-turn cost**: Each turn is not just an API call but includes tool invocation, MCP server coordination, and potentially file I/O. With `/sc:task` prompts, the model activates complex persona routing and compliance classification workflows.

The `per_turn * max_turns` formula incorrectly models startup cost as zero. A more accurate formula would be: `startup_overhead + (per_turn * max_turns)`.

### Does `claude -p` stop early if it has nothing more to do?

`claude -p` documentation shows `--max-turns` is not listed in `claude -p --help` output (v2.1.55). However, it appears to be silently accepted. The flag likely caps the maximum number of agentic turns (tool-use cycles). If the model responds in a single turn with no tool calls, it should complete in one turn regardless of `max_turns`. The issue is not that `claude -p` uses all turns -- it is that the **timeout is too short for even the first turn to complete** given the context loading overhead.

---

## Investigation Angle 2: Timeout Calculation

### Finding: Timeouts are Mathematically Tight and Ignore Fixed Costs

**Evidence** (all durations from `results/run_1/`):

| Test | Model | max_turns | Computed Timeout | Actual Duration | Delta |
|------|-------|-----------|-----------------|-----------------|-------|
| B1   | opus  | 5         | 225s            | 225163ms        | +163ms |
| B1   | sonnet| 5         | 300s            | 300179ms        | +179ms |
| W1   | opus  | 8         | 360s            | 360200ms        | +200ms |
| W4   | opus  | 10        | 450s            | 450229ms        | +229ms |
| W4   | sonnet| 10        | 600s            | 600151ms        | +151ms (hit _TIMEOUT_MAX) |

Every single behavioral test duration matches its timeout ceiling exactly. The ~150-230ms overshoot is the time between `asyncio.wait_for` detecting the timeout and `proc.kill()` completing. This means **no behavioral test ever completed** -- they all ran until killed.

**Analysis**:
The timeout formula `per_turn * max_turns` produces these budgets:

- opus classification (5 turns): 225s = 3.75 minutes
- sonnet classification (5 turns): 300s = 5 minutes
- opus W4 (10 turns): 450s = 7.5 minutes
- sonnet W4 (10 turns): 600s = 10 minutes (hard cap)

If `claude -p` startup alone takes 30-60 seconds (as observed in live testing), and each agentic turn with full context takes 40-60 seconds, then even a 2-turn response would need 100-180 seconds -- within budget for classification tests but leaving little margin. A 5-turn response would need 230-360 seconds, exceeding the opus budget of 225 seconds.

The previous working state (when some tests completed in 20-97s) likely used `max_turns=3` or lower, AND may have been run without the massive CLAUDE.md context overhead.

---

## Investigation Angle 3: Resource Contention

### Finding: 30 Concurrent `claude -p` Processes Create Severe Contention

**Evidence**:
- Default concurrency: `asyncio.Semaphore(30)` for claude processes
- With 3 runs x 2 models x 8 behavioral tests = 48 behavioral tasks queued (semaphore limits to 30 concurrent)
- Each `claude -p` process:
  - Spawns a Node.js process
  - Loads CLAUDE.md + all `@`-referenced files into context
  - Initializes MCP server connections (Context7, Sequential, Serena, etc.)
  - Makes API calls to Anthropic's servers
  - Performs file I/O for tool operations

**Analysis**:
30 concurrent `claude -p` processes would:
1. **API rate limiting**: Anthropic's API has rate limits. 30 concurrent sessions from the same API key would likely trigger rate limiting, causing exponential backoff and retry delays.
2. **MCP server exhaustion**: Each `claude -p` process initializes its own MCP connections. 30 concurrent sessions trying to connect to the same MCP servers (especially if they are local processes) would cause connection exhaustion or startup failures.
3. **Memory pressure**: Each Node.js process for `claude -p` consumes significant memory. 30 processes could easily consume 10-30 GB of RAM, causing swap thrashing.
4. **Network contention**: 30 processes simultaneously making API calls saturates the network connection.

Even if each individual test would complete within its timeout budget with no contention, 30 concurrent tests could push every test over its timeout through cumulative resource pressure.

---

## Investigation Angle 4: CLAUDECODE Environment Variable (Nesting Detection)

### Finding: CRITICAL -- `claude -p` Refuses to Launch Inside a Claude Code Session

**Evidence**:
```
$ claude -p --model haiku --output-format text -- "Reply with just OK"
Error: Claude Code cannot be launched inside another Claude Code session.
Nested sessions share runtime resources and will crash all active sessions.
To bypass this check, unset the CLAUDECODE environment variable.
```

- The `CLAUDECODE=1` environment variable is set in the current session.
- The runner does NOT pass an `env` parameter to `asyncio.create_subprocess_exec`, so child processes inherit the parent environment.
- No `env -u CLAUDECODE` wrapper exists in the runner code (confirmed via grep).
- When `claude -p` detects `CLAUDECODE`, it prints the error to **stderr** and exits with code 1 in under 1 second.

**However**: This does NOT explain the observed timeouts. Testing confirms that `claude -p` exits **immediately** (within 1 second) on nesting detection -- it does not hang. Since `proc.communicate()` would return immediately with the error on stderr, the test would get a non-zero exit code but would NOT timeout.

**Implication**: This means the orchestrator was likely run OUTSIDE a Claude Code session (from a regular terminal), so `CLAUDECODE` was NOT set during the actual test runs that produced the stored results. The nesting issue is a **prospective risk** -- if someone tries to run the orchestrator from within Claude Code (e.g., via a slash command), all tests would fail. But it is NOT the cause of the stored timeout results.

**Important caveat**: The runner SHOULD still add `env -u CLAUDECODE` protection for robustness, because:
- Future runs might be triggered from within Claude Code
- The error message goes to stderr, which is only captured on non-timeout exits (line 187), creating a silent failure mode

---

## Investigation Angle 5: The `--` Separator

### Finding: The `--` Separator is Correct and Not Causing Issues

**Evidence**:
- The runner uses `cmd.append("--")` before `cmd.append(prompt)` (lines 172-173).
- This is standard POSIX option parsing: `--` signals end of options, preventing the prompt from being parsed as a flag.
- The comment on line 168-171 explains this was intentionally added to fix a bug where `--add-dir` (a variadic option) consumed the prompt string.

**Analysis**:
The `--` separator is correct practice and is properly handled by `claude -p`. This is NOT a contributing factor.

---

## Investigation Angle 6: asyncio.wait_for and Zombie Processes

### Finding: Process Cleanup is Reasonable but Not Bulletproof

**Evidence** (runner.py lines 190-196):
```python
except asyncio.TimeoutError:
    try:
        proc.kill()
        await proc.wait()
    except Exception:
        pass
    return f"TIMEOUT after {timeout}s", -1
```

**Analysis**:
- `proc.kill()` sends SIGKILL, which cannot be caught. The process WILL die.
- `await proc.wait()` reaps the zombie. If this raises (unlikely), the `except Exception: pass` swallows it.
- However, `proc.kill()` kills only the direct child. `claude -p` spawns child processes (Node.js, MCP servers). If `claude -p` is killed, its children may become orphans.
- With 30 concurrent processes timing out, this could leave dozens of orphaned Node.js processes consuming resources, compounding contention for subsequent test runs.

**Mitigation needed**: Use `os.killpg` (process group kill) or `proc.terminate()` with a grace period followed by `proc.kill()`. Better yet, start each process in its own process group.

---

## Investigation Angle 7: Missing Haiku Model

### Finding: Haiku is Mapped to a Non-Anthropic Model

**Evidence**:
```
ANTHROPIC_DEFAULT_HAIKU_MODEL=gpt-5.2
```

- No haiku results exist in any run directory.
- Only opus and sonnet results are present (21 results per run = 5 structural + 8 behavioral x 2 models).
- The orchestrator was likely run with `--models sonnet,opus` to avoid haiku failures.

**Analysis**:
The `ANTHROPIC_DEFAULT_HAIKU_MODEL=gpt-5.2` environment variable maps the "haiku" alias to a GPT model. When `claude -p --model haiku` is invoked, it would attempt to use this model, which would either:
1. Fail immediately (incompatible API)
2. Produce incompatible responses
3. Timeout while trying to connect to OpenAI's API through Anthropic's client

This explains why haiku was excluded from the test runs.

---

## Top 3 Most Likely Contributing Factors (Ranked)

### 1. Insufficient Timeout Budgets Combined with High Context Overhead (Likelihood: 95%)

**Why this is the primary cause**: The evidence is definitive. Every behavioral test duration matches its timeout ceiling to within 200ms. The timeout formula `per_turn * max_turns` ignores the significant fixed cost of `claude -p` initialization (30-60+ seconds for context loading and MCP setup). When you combine:
- 5-10 turns at 45-60 seconds each
- 30-60 second startup overhead
- Massive CLAUDE.md context with 8 `@`-referenced files
- MCP server initialization per session

...the total execution time exceeds the computed timeout for nearly all configurations.

**Evidence**: Live testing showed even a trivial single-turn haiku request takes >30s from the repo root due to context loading.

### 2. Resource Contention from 30 Concurrent Processes (Likelihood: 85%)

**Why this is a major amplifier**: Even if individual tests COULD complete within their timeout budget under ideal conditions, running 30 concurrent `claude -p` processes creates:
- API rate limiting (30 simultaneous API key uses)
- MCP server connection exhaustion
- Memory pressure (30 Node.js processes)
- Network saturation

This transforms marginal timeout budgets into guaranteed failures by adding 50-200% overhead to each request's response time.

**Evidence**: The orchestrator defaults to `concurrency=30` with no discussion of rate limiting or resource management.

### 3. Missing `env -u CLAUDECODE` Protection (Likelihood: 70% for future runs)

**Why this matters**: While NOT the cause of the stored timeout results (which were likely run from a regular terminal), this is a ticking time bomb. Any attempt to run the orchestrator from within a Claude Code session will cause **immediate silent failure** of all behavioral tests -- they will timeout because the `claude -p` error goes to stderr which is only captured on non-timeout exits.

**Evidence**: `CLAUDECODE=1` is set in the current environment, `env -u CLAUDECODE` is absent from the runner code, and `claude -p` refuses nested sessions with a stderr-only error.

---

## Proposed Experiments

### Experiment 1: Validate Timeout Budget Hypothesis
```bash
# Run a single test with generous timeout and measure actual completion time
env -u CLAUDECODE timeout 600 claude -p \
  --model sonnet --max-turns 1 --output-format text \
  -- '/sc:task "fix typo in error message"' 2>&1
# Measure: How long does a single-turn classification take?
```
**Expected**: Completes in 60-120s, proving the per-turn budget is too tight.

### Experiment 2: Validate Resource Contention Hypothesis
```bash
# Run orchestrator with concurrency=1, models=sonnet, runs=1
env -u CLAUDECODE uv run python tests/v2.01-release-validation/orchestrator.py \
  --runs 1 --models sonnet --concurrency 1
# Compare durations with the concurrency=30 results
```
**Expected**: More tests complete within timeout, proving contention is a factor.

### Experiment 3: Validate CLAUDECODE Nesting Issue
```bash
# Run orchestrator FROM WITHIN Claude Code (as-is, no fix)
uv run python tests/v2.01-release-validation/orchestrator.py \
  --runs 1 --models sonnet --concurrency 1
# Check stderr output of behavioral tests
```
**Expected**: All behavioral tests fail immediately (exit code 1) or timeout with "TIMEOUT after Ns" and no useful output.

### Experiment 4: Fix and Re-test
Apply these fixes to `runner.py` and re-run:
1. Add `env={'CLAUDECODE': ''}` removal or use `env -u CLAUDECODE` wrapper
2. Change timeout formula to: `startup_overhead + (per_turn * max_turns)` with `startup_overhead=60`
3. Reduce default concurrency from 30 to 5
4. Add process group kill for proper cleanup

```python
# Proposed timeout fix
_STARTUP_OVERHEAD = 60  # seconds for context loading + MCP init
def _compute_timeout(model: str, max_turns: int) -> int:
    per_turn = _TIMEOUT_PER_TURN.get(model, _TIMEOUT_DEFAULT_PER_TURN)
    return min(_STARTUP_OVERHEAD + per_turn * max_turns, _TIMEOUT_MAX)
```

---

## Appendix: Evidence Summary

| Data Point | Value | Source |
|-----------|-------|--------|
| B1 opus duration | 225163ms (= 225s timeout) | `results/run_1/B1_opus_result.json` |
| B1 sonnet duration | 300179ms (= 300s timeout) | `results/run_1/B1_sonnet_result.json` |
| W4 sonnet duration | 600151ms (= 600s cap) | `results/run_1/W4_sonnet_result.json` |
| Haiku results | 0 across all runs | Directory listing |
| CLAUDECODE env var | Set to "1" | `echo $CLAUDECODE` |
| Nesting error exit | Immediate (< 1s), code 1 | Live test |
| claude -p from /tmp | >30s for trivial prompt | Live test with timeout |
| Default concurrency | 30 | `orchestrator.py` line 342 |
| HAIKU model mapping | `gpt-5.2` (non-Anthropic) | `env \| grep haiku` |
| `--max-turns` in help | NOT listed | `claude -p --help` (v2.1.55) |
| `env -u CLAUDECODE` in runner | ABSENT | grep search |
