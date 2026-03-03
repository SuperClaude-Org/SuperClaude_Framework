# RCA Agent 3: Environment and Infrastructure

## Problem Summary

All 48 behavioral tests (B1-B4 and W1-W4, across sonnet and opus, across 3 runs) timed out at their exact calculated timeout limits. Zero behavioral tests completed. Timeout durations ranged from 225s to 600s. Structural tests (S1-S5) completed normally in ~1s each.

No haiku model results exist at all, suggesting haiku was excluded from the run (the orchestrator was invoked with `--models sonnet,opus`).

---

## Investigation 1: CLAUDE.md Context Explosion

### Findings

The global `~/.claude/CLAUDE.md` at `/config/.claude/CLAUDE.md` contains `@` references to 8 large files:

| File | Size (bytes) |
|------|-------------|
| COMMANDS.md | 8,205 |
| FLAGS.md | 5,457 |
| PRINCIPLES.md | 2,573 |
| RULES.md | 14,165 |
| MCP.md | 12,260 |
| PERSONAS.md | 10,376 |
| ORCHESTRATOR.md | 17,855 |
| MODES.md | 11,827 |
| **Subtotal (@-refs)** | **82,718** |
| Project CLAUDE.md | 11,112 |
| **Total per process** | **93,830** |

**Approximate tokens per `claude -p` process**: ~23,500 tokens of system context before the test prompt is even processed.

With 30 concurrent processes (semaphore limit), this means up to **~700,000 tokens of system context** hitting the API simultaneously, just for the initial turn of each process.

### Evidence

- The `runner.py` subprocess call does not strip or override the working directory's CLAUDE.md or the global `~/.claude/CLAUDE.md`. Each `claude -p` invocation inherits all of this context.
- The `run_behavioral_test` function sets `cwd=str(repo_root)`, which means the project CLAUDE.md at `/config/workspace/SuperClaude_Framework/CLAUDE.md` is loaded. Since the global CLAUDE.md references the 8 `@`-files, those are also loaded.
- Each process also inherits the parent shell's environment, including MCP server configs.

### Impact Assessment

**HIGH**. The 23K+ token system context significantly increases:
1. Time-to-first-token for each API call (the model must process all context)
2. Total API cost per call, which may trigger rate limiting sooner
3. Model response complexity -- the model tries to follow all the SuperClaude framework instructions instead of just answering the simple classification question

---

## Investigation 2: MCP Server Initialization Per Subprocess

### Findings

The global MCP configuration at `/config/.claude/mcp.json` defines two MCP servers:

```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.2"],
      "env": { "TAVILY_API_KEY": "..." }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

Additionally, the `/config/.claude/plugins/` directory contains marketplace plugin configs for: serena, playwright, context7, asana, greptile, laravel-boost, slack, linear, stripe -- though it is unclear which of these are actively loaded by `claude -p`.

### Evidence

- Each `claude -p` process that starts in this repo will attempt to initialize MCP servers as defined in the global `mcp.json`.
- MCP servers are launched via `npx`, which:
  - Downloads packages on first run (if not cached)
  - Spawns Node.js child processes
  - Establishes JSON-RPC connections
- With 30 concurrent `claude -p` processes, this means up to **60 concurrent `npx` child processes** (2 MCP servers each) plus the `claude` processes themselves.
- If `@latest` resolution for context7 requires a network call, 30 simultaneous npm registry lookups could cause contention.
- `runner.py` does NOT set a custom `env` parameter on `asyncio.create_subprocess_exec`, so child processes inherit the full parent environment including all MCP configuration paths.

### Impact Assessment

**HIGH**. MCP initialization overhead per process could add 10-30 seconds of startup time. Combined with 30 concurrent processes competing for system resources (CPU, memory, network, file descriptors), this creates a compounding bottleneck.

---

## Investigation 3: Nested Claude Code Sessions

### Findings

The environment variable `CLAUDECODE=1` is set in the current shell environment. This confirms the orchestrator is being run from within an active Claude Code session.

### Evidence

- `env | grep CLAUDECODE` outputs `CLAUDECODE=1`
- The `runner.py` file does NOT filter environment variables when spawning subprocesses -- no `env` parameter is passed to `asyncio.create_subprocess_exec`.
- Each child `claude -p` process inherits `CLAUDECODE=1`, which may cause the Claude Code binary to detect it is running inside another Claude Code session.
- Possible effects of nested detection:
  - The child may attempt to coordinate with or defer to the parent session
  - Lock files or shared state in `~/.claude/` (tasks, todos, session-env, history.jsonl) may cause contention
  - The child may enter a degraded mode or queue behind the parent

### Impact Assessment

**MEDIUM-HIGH**. The `CLAUDECODE=1` environment variable being inherited by child processes is a likely contributor. The `claude -p` binary may behave differently when it detects it is nested, potentially waiting for resources held by the parent session. This would explain why ALL tests uniformly time out rather than some succeeding and others failing.

---

## Investigation 4: API Rate Limiting

### Findings

The test run creates 48 behavioral test invocations (3 runs x 2 models x 8 tests) with a concurrency limit of 30. Each test can make up to 5-10 API calls (one per turn, with `--max-turns` ranging from 5 to 10).

### Evidence

- Peak concurrent API load: 30 processes x ~23K input tokens each = ~700K tokens in a burst
- Over the test run: 48 processes x average 5 turns = 240 API calls total
- The `ANTHROPIC_BASE_URL` environment variable is set, indicating a custom API endpoint (possibly a proxy or internal deployment)
- The `ANTHROPIC_AUTH_TOKEN` is set (not `ANTHROPIC_API_KEY`), suggesting a managed/organizational setup
- Rate limits on organizational API endpoints may be more restrictive than direct Anthropic API access
- If the API rate-limits at 30 concurrent requests, subsequent requests queue, and each queued request adds to the total time, cascading delays would cause ALL tests to exceed their timeout

### Impact Assessment

**HIGH**. With 30 concurrent processes each sending ~23K token requests, API rate limiting is very likely. Rate-limited requests would appear as slow responses from the perspective of the test harness, and since the timeouts are calculated per-turn (45-90s), even moderate API queuing delays would cause timeouts. The uniform failure pattern (100% timeout, 0% completion) is consistent with a global throttle affecting all requests equally.

---

## Investigation 5: Container/CI Resource Constraints

### Findings

The system is running Linux 6.8.0-100-generic. The working directory is `/config/workspace/SuperClaude_Framework`, which suggests a containerized or managed environment.

### Evidence

- The path structure (`/config/workspace/`) is not a typical local development layout -- it resembles a container or cloud IDE environment.
- Running 30 concurrent `claude -p` processes, each spawning 2 MCP server child processes via `npx`, plus the Python orchestrator = potentially 90+ processes competing for resources.
- Each `claude` process loads ~23K tokens of context, and the Node.js MCP servers each consume memory.
- Container environments typically have memory and CPU limits that are lower than bare-metal.
- If memory pressure causes swapping, all processes slow down uniformly -- matching the observed pattern.

### Impact Assessment

**MEDIUM**. While resource constraints alone might not explain the complete 100% timeout rate, they compound with the other factors. In a memory-constrained container, 30 concurrent processes with MCP servers could push the system into swap, degrading performance uniformly.

---

## Investigation 6: `--dangerously-skip-permissions` and `--max-turns` Behavior

### Findings

The `runner.py` uses `--dangerously-skip-permissions` with `--max-turns` ranging from 5 to 10. The spec originally planned `--max-turns 3` for classification tests but the actual implementation uses 5.

### Evidence

- `max_turns` for B tests: 5 (spec said 3)
- `max_turns` for W tests: 6-10 (spec said 5)
- Higher turn counts = longer timeouts: B tests get 225s (opus) to 450s (haiku), W tests get up to 600s
- With `--dangerously-skip-permissions`, the model can use ALL tools without asking permission. Combined with the 23K token SuperClaude context instructing it to use MCP servers, sequential thinking, and multi-step workflows, the model may attempt complex multi-tool workflows for every simple prompt.
- A simple "fix typo in error message" prompt (B3) could trigger the model to: activate analyzer persona, invoke sequential thinking, attempt MCP server connections, scan the codebase with grep/glob, etc. -- all because the SuperClaude framework instructions tell it to.

### Impact Assessment

**HIGH**. The combination of `--dangerously-skip-permissions` + massive SuperClaude context creates a situation where the model attempts far more work per turn than intended. Instead of outputting a simple classification header, it tries to actually perform the task (finding the typo, scanning auth code, etc.), consuming all available turns with tool calls and never producing the expected classification output.

---

## Top 3 Contributing Factors (Ranked by Likelihood)

### 1. CLAUDE.md Context Explosion + Model Behavioral Overload (Likelihood: 95%)

**Root Cause**: Each `claude -p` process loads ~23,500 tokens of SuperClaude framework instructions (COMMANDS.md, FLAGS.md, RULES.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md, MCP.md, PRINCIPLES.md). These instructions tell the model to:
- Auto-activate specialist personas based on keywords
- Use MCP servers for analysis
- Follow multi-step workflows (Understand -> Plan -> Execute -> Validate)
- Create TodoWrite tasks for any multi-step operation
- Never jump to conclusions without systematic investigation

When the model receives "fix security vulnerability in auth module", instead of outputting a classification header, it follows the SuperClaude instructions: activates the security persona, attempts to use sequential thinking MCP, tries to scan the codebase, plans a multi-step workflow, etc. This consumes all 5 turns with tool calls and produces no classification output.

**Evidence**:
- The wiring tests score 0.15 (not 0.0), specifically on the "no raw dump" criterion, meaning the model DID produce some output but it was not the expected protocol flow -- consistent with the model doing something else entirely (following SuperClaude instructions).
- Classification tests score 0.0, meaning no classification header was found at all.
- This was not a problem before because either: (a) the CLAUDE.md was smaller, or (b) the `@`-referenced files were added/expanded recently as part of v2.01.

**Proposed Experiments**:
1. Run a single `claude -p` test with `--no-config` or from a directory without CLAUDE.md to see if it completes
2. Create a minimal CLAUDE.md (or none) in a temp directory and run tests from there
3. Run `time claude -p --model opus --max-turns 1 --output-format text "say hello"` from the repo root vs from /tmp to measure context loading overhead

### 2. API Rate Limiting from Concurrent Load (Likelihood: 80%)

**Root Cause**: 30 concurrent `claude -p` processes, each sending ~23K token requests through a managed API endpoint (indicated by `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`), exceed the rate limits of the API. Requests are queued or throttled, causing each request to take much longer than expected. Since the timeout is calculated as `per_turn_seconds * max_turns`, and the per-turn timeout assumes normal API response times (45-90s), rate-limited responses easily exceed these budgets.

**Evidence**:
- `ANTHROPIC_BASE_URL` is set, indicating a proxy/managed endpoint that may have its own rate limits
- `ANTHROPIC_AUTH_TOKEN` (not `ANTHROPIC_API_KEY`) suggests organizational/managed access
- 100% uniform timeout rate across all models and test types is consistent with a global throttle
- No partial completions -- if some requests got through, we would expect at least some tests to pass

**Proposed Experiments**:
1. Reduce concurrency to 1 (`--concurrency 1`) and run a single test to see if it completes
2. Reduce concurrency to 5 and measure completion rates
3. Add logging to capture HTTP response status codes (429 = rate limited)
4. Measure time-to-first-token for a single `claude -p` call vs. 30 concurrent calls

### 3. Nested Claude Code Session (`CLAUDECODE=1` Inheritance) (Likelihood: 70%)

**Root Cause**: The `CLAUDECODE=1` environment variable is inherited by all child `claude -p` processes because `runner.py` does not filter the environment. The `claude` binary may detect this variable and behave differently when nested -- potentially waiting for parent session resources, entering a queue, or taking a different initialization path that adds latency.

**Evidence**:
- `CLAUDECODE=1` confirmed in current environment
- `runner.py` does NOT pass an `env` parameter to `asyncio.create_subprocess_exec`, so full parent environment is inherited
- The Claude Code documentation mentions `env -u CLAUDECODE` as a way to prevent nested detection
- This would affect ALL child processes equally, matching the 100% timeout pattern

**Proposed Experiments**:
1. Modify `runner.py` to pass `env={**os.environ, 'CLAUDECODE': ''}` or filter out `CLAUDECODE` entirely
2. Run the orchestrator with `env -u CLAUDECODE uv run python tests/v2.01-release-validation/orchestrator.py --runs 1 --concurrency 1`
3. Compare behavior of `claude -p "say hello"` with and without `CLAUDECODE=1` set

---

## Additional Observations

### Missing Haiku Results
No haiku model results exist in any run directory. The orchestrator was likely invoked with `--models sonnet,opus`, reducing the test matrix from 145 to 63 data points. This is a configuration issue but not related to the timeout problem.

### MCP Server Configuration is Minimal
The project-level `.claude/settings.json` is empty (`{}`). The global `settings.json` sets `model: opus`, `alwaysThinkingEnabled: true`, and `effortLevel: medium`. The `alwaysThinkingEnabled: true` setting may cause extended thinking for each API call, further increasing response times and token consumption.

### Timeout Calculation Matches Exactly
Every behavioral output file contains `TIMEOUT after Ns` where N matches exactly `min(per_turn_timeout * max_turns, 600)`. This confirms that processes are being killed by the Python timeout, not crashing or erroring. The `claude -p` processes are still alive when killed -- they are simply taking too long to complete.

---

## Recommended Immediate Actions

1. **Strip SuperClaude context for tests**: Run `claude -p` from a clean directory without CLAUDE.md, or use environment variable overrides to disable context loading.
2. **Filter environment in runner.py**: Add `env` parameter to subprocess calls that removes `CLAUDECODE`, and optionally `ANTHROPIC_BASE_URL` if testing against a rate-limited proxy.
3. **Reduce concurrency drastically**: Start with `--concurrency 1 --runs 1 --models opus` to establish a baseline of whether a single test can complete at all.
4. **Disable `alwaysThinkingEnabled`**: The global setting may be forcing extended thinking on every API call.
5. **Increase timeouts or reduce max_turns**: If the model needs 5+ minutes per test due to context size, either accept longer timeouts or reduce `--max-turns` to 1-2 for classification tests (which should output the header on turn 1).
