# Unified Root Cause Analysis: v2.01 Behavioral Test 100% Timeout Failure

**Date**: 2026-02-24
**Status**: 0% behavioral pass rate (48/48 tests timeout)
**Sources**: Agent 1 (Harness Mechanics), Agent 2 (Protocol Changes), Agent 3 (Environment)

---

## Executive Summary

Every behavioral test (B1-B4, W1-W4) across all runs, all models (sonnet, opus), times out at the exact computed ceiling (`per_turn * max_turns`). Zero partial completions exist. The failure is caused by a **compound of 3 primary and 4 contributing factors** that interact to guarantee timeout.

The single most impactful root cause is **the addition of `allowed-tools` to the command frontmatter** (Fix 6), which enabled the model to consume all turns making tool calls instead of producing text output. This interacts with the massive SuperClaude context (~23K tokens), high concurrency (30 processes), and insufficient timeout budgets to create a 100% failure rate.

---

## Root Causes (Ranked by Impact × Likelihood)

### RC-1: `allowed-tools` in Frontmatter Enables Tool-Call Exhaustion (Impact: CRITICAL, Likelihood: 95%)

**The primary root cause.** The restructured `task-unified.md` added `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` to the YAML frontmatter. The previous 567-line version had **no `allowed-tools` field**.

**Mechanism**: When `claude -p` loads this command, the model sees 9 available tools plus a task description like "fix security vulnerability in auth module." Instead of emitting the classification header as text, it begins investigating the task:

- Turn 1: `Grep` or `Read` to find the auth module
- Turn 2: `Skill sc:task-unified-protocol` invocation (loads 308 more lines)
- Turn 3-5: Protocol steps (activate_project, git status, codebase-retrieval, etc.)

All 5 turns are consumed by tool calls. No text output is ever produced. The process hits the timeout ceiling.

**Evidence**:
- Previous version (no `allowed-tools`) → some tests completed in 20-97s → 9.2% pass rate
- Current version (`allowed-tools` added) → 100% timeout → 0% pass rate
- Classification scores all 0.0 → zero text output produced
- Wiring `no_raw_dump = 1.0` → model engaged with command (didn't dump it), but `skill_invoked = 0.0`, `protocol_flow = 0.0`, `tool_engagement = 0.0`
- 100% failure rate across both models → structural issue, not model capability

**`allowed-tools` is the single discriminating variable**: Everything else (task descriptions, model behavior, prompt structure) is held constant across versions. The previous version lacked `allowed-tools`; the current version added it. This is the ONLY structural change that directly enables tool-call consumption of turns.

**Contradictory Instructions**: Three directives in the command file are mutually incompatible:
```
"Before ANY text, emit this exact header"   → wants: immediate text output
"allowed-tools: Read, Glob, Grep, ..."      → enables: tool calls before text
"> Skill sc:task-unified-protocol"           → wants: tool call to load skill
```

**`-p` mode dual-interpretation**: In `claude -p` mode, the prompt is the ENTIRE input. The model sees `/sc:task "fix security vulnerability in auth module"` as both a command invocation AND a real task to execute. This dual interpretation creates a competition: the command's "MANDATORY FIRST OUTPUT" instruction asks for immediate classification text, but the model's instinct is to actually investigate and fix the security vulnerability. Combined with `--dangerously-skip-permissions` (which removes all permission gates), the model has both the tools AND the permission to pursue full task execution rather than classification.

### RC-2: SuperClaude Context Explosion (~23K Tokens of System Instructions) (Impact: HIGH, Likelihood: 95%)

Each `claude -p` subprocess loads the full SuperClaude framework via CLAUDE.md `@`-references:

| File | Size |
|------|------|
| COMMANDS.md | 8,205 bytes |
| FLAGS.md | 5,457 bytes |
| RULES.md | 14,165 bytes |
| MCP.md | 12,260 bytes |
| PERSONAS.md | 10,376 bytes |
| ORCHESTRATOR.md | 17,855 bytes |
| MODES.md | 11,827 bytes |
| PRINCIPLES.md | 2,573 bytes |
| Project CLAUDE.md | 11,112 bytes |
| **Total** | **~93,830 bytes (~23,500 tokens)** |

These instructions direct the model to: activate specialist personas, use MCP servers, follow multi-step workflows (Understand → Plan → Execute → Validate), create TodoWrite tasks, never jump to conclusions. When the model receives "fix security vulnerability in auth module," it follows these instructions rather than outputting a simple classification header.

**This interacts with RC-1**: Even without `allowed-tools`, the SuperClaude context primes the model toward investigative behavior. With `allowed-tools`, it has the tools to act on that priming.

### RC-3: Insufficient Timeout Budgets Ignoring Fixed Startup Cost (Impact: HIGH, Likelihood: 95%)

**Key analytical distinction**: The question is not "does the model use all its turns?" but "can even a SINGLE turn complete within the per-turn budget given startup overhead?" If `claude -p` startup alone takes 30-60s and the per-turn budget is 45s (opus), the first turn may never complete regardless of `max_turns`.

**Spec deviation**: Classification tests use `max_turns=5` but the original spec called for `max_turns=3`. The previous working state (20-97s completions) likely used `max_turns=3` or lower, AND may have been run without the massive CLAUDE.md context overhead.

**Note**: `--max-turns` is NOT listed in `claude -p --help` output (v2.1.55) but is silently accepted. Its exact semantics in `-p` mode are undocumented.

The timeout formula `per_turn * max_turns` ignores a significant fixed startup cost:

| Component | Estimated Time |
|-----------|---------------|
| `claude -p` binary startup | 2-5s |
| CLAUDE.md + @-ref parsing | 5-10s |
| MCP server initialization (2 configured in mcp.json + up to 6 declared in command frontmatter) | 10-30s |
| API first-turn latency (~23K context) | 15-30s |
| **Total startup overhead** | **~30-60s** |

**Current timeout budgets**:
- Opus B tests (5 turns): 45 × 5 = 225s → Only 165-195s for actual turns after startup
- Sonnet B tests (5 turns): 60 × 5 = 300s → Only 240-270s for actual turns

Live testing confirmed even a trivial single-turn haiku call takes >30s from the repo root.

**Evidence**: Every behavioral test duration matches its timeout ceiling to within 200ms:

| Test | Model | Timeout | Actual Duration | Delta |
|------|-------|---------|-----------------|-------|
| B1 | opus | 225s | 225,163ms | +163ms |
| B1 | sonnet | 300s | 300,179ms | +179ms |
| W1 | opus | 360s | 360,200ms | +200ms |
| W4 | sonnet | 600s | 600,151ms | +151ms |

---

## Contributing Factors

### CF-1: Skill Invocation Cascades into Protocol Exceeding Turn Budget (Likelihood: 85%)

Line 70 of `task-unified.md`: `> Skill sc:task-unified-protocol` loads 308 lines of additional protocol. The STRICT tier execution path has 11 mandatory steps, each requiring a tool call. With `max_turns=5` and 1-2 turns already consumed, only 3-4 turns remain — insufficient for 11 steps.

Additionally, the Skill file **duplicates** the classification requirement (appears 3 times total across command + skill), creating ambiguity about when to classify.

### CF-1b: Classification Instruction Triplication Causes Deferral (Likelihood: 70%)

The "MANDATORY FIRST OUTPUT" classification instruction appears **three times**: once in the command file (line 46), once in the Skill warning banner (SKILL.md line 7), and once in Skill Section 0 (SKILL.md lines 57-69). This triplication does not just waste context — it creates ambiguity about WHEN to classify. The command says "before ANY text" but also says "invoke Skill" (line 70). The Skill then repeats "MANDATORY FIRST OUTPUT," potentially causing the model to **defer** classification until after tool calls (which consume all turns), rather than emitting it immediately.

**Evidence**: Classification scores are all 0.0 — the model never produces the header, consistent with deferral rather than inability. The model is capable of classification but the contradictory sequencing causes it to postpone the output.

### CF-2: Resource Contention from 30 Concurrent Processes (Likelihood: 85%)

Default concurrency is 30 (`asyncio.Semaphore(30)`). Each process:
- Spawns Node.js + 2 MCP server child processes via `npx`
- Loads ~23K tokens of context
- Makes API calls to a managed endpoint (`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`)

This creates: API rate limiting (~700K input tokens in burst, with possible exponential backoff and retry delays), MCP server connection exhaustion (~60 npx processes, with `@latest` npm registry resolution causing 30 simultaneous npm lookups), memory pressure (30+ Node.js processes, potentially 10-30 GB RAM causing swap thrashing), network saturation.

Additionally, `/config/.claude/plugins/` contains 9 marketplace plugin configs (serena, playwright, context7, asana, greptile, laravel-boost, slack, linear, stripe) — it is unclear which are actively loaded by `claude -p`, but any that are would multiply the per-process initialization overhead.

The 100% uniform timeout pattern across all models is consistent with a global throttle or resource starvation affecting all requests equally.

### CF-3: Nested Claude Code Session (CLAUDECODE=1 Inheritance) (Likelihood: 70%)

`CLAUDECODE=1` is set in the parent environment and inherited by all child processes because `runner.py` does not filter environment variables. Testing confirms `claude -p` **refuses to launch** with:
```
Error: Claude Code cannot be launched inside another Claude Code session.
```

**Nuance**: If the stored results were produced from a regular terminal (CLAUDECODE not set), this is a **prospective risk**, not the cause of stored results. If run from within Claude Code, the error goes to stderr and the process exits immediately with code 1 — which would NOT cause a timeout (exit is <1s). However, the stderr error is only captured when the process does NOT timeout (`runner.py` line 187), creating a **silent failure mode**.

### CF-4: `alwaysThinkingEnabled: true` in Global Settings (Likelihood: 50%)

The global `settings.json` sets `alwaysThinkingEnabled: true`, which may force extended thinking on every API call, further increasing response times and token consumption per turn.

---

## Additional Findings

### Missing Haiku Model
`ANTHROPIC_DEFAULT_HAIKU_MODEL=gpt-5.2` maps the haiku alias to a non-Anthropic model. The orchestrator was run with `--models sonnet,opus` to avoid haiku failures. This is a configuration issue unrelated to timeouts.

### `--` Separator: NOT a Factor
The `--` separator between options and prompt is correct POSIX practice and properly handled by `claude -p`.

### Process Cleanup: Minor Risk
`proc.kill()` sends SIGKILL to the direct child only. `claude -p` child processes (Node.js, MCP servers) may become orphans, compounding resource contention for subsequent tests. Fix: use `os.killpg` (process group kill) or `proc.terminate()` with a grace period followed by `proc.kill()`. Start each subprocess in its own process group via `start_new_session=True` in `asyncio.create_subprocess_exec`.

---

## Interaction Matrix

| Factor | Alone Causes Timeout? | Amplifies Others? | Fix Difficulty |
|--------|----------------------|-------------------|----------------|
| RC-1: allowed-tools | YES | YES (enables tool turns) | Easy: remove from frontmatter |
| RC-2: Context explosion | Unlikely alone | YES (primes tool behavior) | Medium: test isolation |
| RC-3: Timeout budget | Depends on turn count | YES (too tight for reality) | Easy: add startup overhead |
| CF-1: Skill cascade | YES (exceeds turn budget) | YES (loads 308 more lines) | Easy: remove Skill invocation |
| CF-2: Concurrency | Maybe (rate limiting) | YES (amplifies all latencies) | Easy: reduce to 5 |
| CF-3: CLAUDECODE nesting | NO (causes immediate exit with code 1, NOT a timeout) | NO (orthogonal failure mode) | Easy: env filtering |
| CF-4: Extended thinking | NO | YES (adds per-turn latency) | Easy: disable for tests |

---

## Recommended Fix Priority

### Immediate (Fix the 0% pass rate):

1. **Remove `allowed-tools` from `task-unified.md` frontmatter** — or reduce to empty/`Skill` only. This is the single change most likely to restore test completion. Without tools, the model MUST produce text output (the classification header).

2. **Add startup overhead to timeout calculation**:
   ```python
   _STARTUP_OVERHEAD = 60
   def _compute_timeout(model: str, max_turns: int) -> int:
       per_turn = _TIMEOUT_PER_TURN.get(model, _TIMEOUT_DEFAULT_PER_TURN)
       return min(_STARTUP_OVERHEAD + per_turn * max_turns, _TIMEOUT_MAX)
   ```

3. **Reduce default concurrency from 30 to 5** in orchestrator.py.

4. **Add environment filtering in runner.py** to remove `CLAUDECODE`:
   ```python
   import os
   clean_env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}
   proc = await asyncio.create_subprocess_exec(*cmd, env=clean_env, ...)
   ```

### Short-term (Improve reliability):

5. **Reduce `max_turns` for classification tests back to 2-3** — classification is a single-output task that should complete in 1 turn.

6. **Run tests from a clean directory** without CLAUDE.md `@`-references, or create a minimal test-specific CLAUDE.md.

7. **Remove the Skill invocation from the command file** for classification tests — the classification logic is already inlined.

8. **Use process group kills** for proper subprocess cleanup.

### Long-term (Architectural):

9. **Separate classification command from execution command** — classification should be a lightweight, tool-free operation. Execution (with tools) should be a separate step.

10. **Add test isolation infrastructure** — dedicated test runner that strips SuperClaude context, disables MCP, and runs with minimal configuration.

---

## Proposed Verification Experiments

| # | Experiment | Tests Hypothesis | Expected Result |
|---|-----------|-----------------|-----------------|
| 1 | Remove `allowed-tools`, run B1-B4 with max_turns=2 | RC-1 (tool exhaustion) | Tests complete with classification header |
| 2 | Run single test with --concurrency 1 from clean env | CF-2 + CF-3 | Establishes baseline completion time |
| 3 | Run from /tmp with no CLAUDE.md, same prompt | RC-2 (context explosion) | Faster completion, simpler behavior |
| 4 | Run with `env -u CLAUDECODE` from within session | CF-3 (nesting) | Tests can launch |
| 5 | Keep allowed-tools but set max_turns=1 | Interaction between RC-1 and RC-3 | If timeout persists, RC-3 is dominant |
| 6 | Remove `allowed-tools` entirely vs. reduce to `Skill` only | Isolate allowed-tools from Skill cascade | Identifies whether Skill alone causes failure |
| 7 | Keep `allowed-tools`, remove Skill invocation | Isolate Skill cascade from tool-call exhaustion | Identifies relative contribution of each |
| 8 | Add HTTP 429 status code logging to runner.py | CF-2 (rate limiting) | Confirms whether API throttling is active |
| 9 | Measure time-to-first-token: single `claude -p` vs. 30 concurrent | CF-2 (contention amplification) | Quantifies concurrency-induced latency |

---

## Change Diff Summary: Previous → Current

| Aspect | Previous (567 lines) | Current (107 lines) | Impact on Tests |
|--------|---------------------|---------------------|-----------------|
| `allowed-tools` | Not present | 9 tools listed | **Root cause**: enables tool-call turns |
| Skill invocation | None | Line 70 | Loads 308 more lines, consumes turn |
| "MANDATORY FIRST OUTPUT" | Not present | Lines 46-48 | Contradicts tool-call behavior |
| Classification logic | Implicit | Explicitly inlined | Duplicated with SKILL.md (3x total) |
| Self-contained protocol | Yes (all 567 lines) | Split: 107 + 308 | Two-phase loading, turn overhead |
| Total instruction volume | 567 lines | 107 + 308 = 415 lines | Less total, but structurally worse |
