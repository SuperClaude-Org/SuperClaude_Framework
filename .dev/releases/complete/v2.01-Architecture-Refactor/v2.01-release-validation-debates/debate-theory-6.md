# Adversarial Debate: Theory CF-2 — Resource Contention from 30 Concurrent Processes

**Date**: 2026-02-24
**Theory Under Examination**: CF-2 — Resource Contention from 30 Concurrent Processes
**Assigned Likelihood (RCA)**: 85%
**Debate Agent Role**: Rigorous evaluator — argue both FOR and AGAINST with maximum evidence fidelity

---

## Theory Statement

Default concurrency of 30 creates API rate limiting (~700K input tokens burst), MCP connection exhaustion (~60 npx processes), memory pressure, npm registry contention from @latest lookups, and network saturation. The 100% uniform timeout pattern is consistent with global throttling.

---

## Prosecution: The Case FOR CF-2

### Argument 1: The Token Burst Mathematics Are Real and Severe

The arithmetic is not speculative. Each `claude -p` subprocess loads ~23,500 tokens of SuperClaude context (confirmed in rca-agent-3-environment.md: 93,830 bytes across 9 files). With `asyncio.Semaphore(30)`, the harness allows 30 simultaneous processes.

30 processes x 23,500 tokens = **705,000 input tokens** hitting the API simultaneously before any prompt token is even counted.

This is not a theoretical ceiling — it is the actual burst load on the first API call for each concurrent process. This kind of burst is precisely what triggers rate-limit responses from managed API endpoints. The environment uses `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` (not the standard `ANTHROPIC_API_KEY`), which strongly implies a proxy, internal gateway, or organizational account with rate limits that differ from — and are likely more restrictive than — direct Anthropic API access. Organizational/managed endpoints routinely apply per-minute token quotas, concurrent request ceilings, or per-IP limits that bare-metal Anthropic API accounts do not encounter.

### Argument 2: The MCP Process Explosion Is Documented and Compounding

The global `mcp.json` defines two MCP servers (tavily, context7), both launched via `npx`. With 30 concurrent `claude -p` processes, this means **60 concurrent `npx` child processes** are spawned, each:

- Downloading or resolving Node.js packages
- Establishing JSON-RPC connections
- Consuming file descriptors, ports, and memory

The context7 server uses `@latest` tag resolution (`@upstash/context7-mcp@latest`). In a containerized `/config/workspace/` environment, 30 simultaneous npm registry lookups for `@latest` could cause network contention, DNS exhaustion, or npm registry throttling entirely independent of the Anthropic API. This is an orthogonal resource contention path that amplifies total startup time.

Additionally, the `/config/.claude/plugins/` directory contains 9 marketplace plugin configs (serena, playwright, context7, asana, greptile, laravel-boost, slack, linear, stripe). If any of these are loaded by `claude -p` at startup, the per-process MCP server count could be significantly higher than 2, multiplying the npx process count and resource drain.

### Argument 3: Container Environment Amplifies Resource Contention

The path `/config/workspace/SuperClaude_Framework` is a containerized or managed cloud IDE environment (not a typical `~/github/` local path). Container environments impose:

- Memory limits (often 4-16 GB for dev containers, compared to 32+ GB bare-metal)
- CPU quotas (often 2-4 vCPUs shared with other tenants)
- Network bandwidth limits

Running 30 claude processes + 60 npx MCP processes + the Python orchestrator = 91+ concurrent processes. If the container has a 4 GB memory limit and each Node.js MCP process uses 100-200 MB, the MCP processes alone consume 6-12 GB — exceeding a 4 GB container limit and forcing swap. Swap thrashing degrades ALL processes uniformly, which matches the observed pattern.

### Argument 4: Uniform 100% Failure Pattern Is Consistent With Global Throttle

Rate limiting and resource starvation produce characteristically different failure patterns than application-level bugs:

- Application bugs: partial failures, model-specific failures, test-specific failures
- Global resource throttle: uniform, total, model-agnostic, test-agnostic failures

The observed data shows **zero variance**: sonnet and opus both produce 0.00±0.00 on B1-B4 and identical 0.15±0.00 on W1-W4. Cross-model standard deviation is 0.0%. Every behavioral test hits its timeout to within 200ms. This statistical uniformity is more consistent with a shared external constraint (API throttle, memory ceiling, resource gate) than with a per-process behavioral bug in the command file.

### Argument 5: Startup Overhead Amplification Under Contention

Under contention, startup costs are not additive — they are multiplicative. When 30 processes simultaneously compete for API access:

- Each process waits for the API to respond to its first-turn request
- While waiting, the process holds its asyncio slot (semaphore acquired but not released)
- No other test can start until one of the 30 completes or times out
- If ALL 30 are rate-limited simultaneously, the timeout clock runs for all of them in parallel

The result is that rate limiting does not just add latency to individual tests — it creates a **deadlock pattern** where all 30 semaphore slots are occupied by stuck processes, blocking all 18 remaining tests (48 total - 30 concurrent = 18 queued) from even starting until the first wave times out. This explains why NO tests complete: even tests that would have succeeded under serial execution get queued until after the timeout wave hits.

---

## Defense: The Case AGAINST CF-2

### Counter-Argument 1: The Previous Version Also Used High Concurrency and Got 9.2% Pass Rate

This is the most damaging counter-evidence in the entire RCA. The previous `task-unified.md` (567-line version, no `allowed-tools`) produced a **9.2% pass rate** (some tests completed in 20-97 seconds). The RCA documents confirm: "Previous version (no `allowed-tools`) → some tests completed in 20-97s → 9.2% pass rate."

Both versions used the same test harness with the same default concurrency of 30. If resource contention from 30 concurrent processes were the root cause, the previous version would also have produced 100% timeouts. It did not. The only structural change between the two versions is `allowed-tools`. This directly falsifies CF-2 as a **sufficient** cause of the 100% failure rate.

The prosecution's "deadlock pattern" argument (all 30 slots occupied) is undermined by the fact that some tests DID complete under the previous version, meaning the semaphore slots DO cycle and release — the infrastructure is capable of allowing completions.

### Counter-Argument 2: Rate Limiting Would Produce Partial Completions, Not 100% Failure

Genuine API rate limiting does not typically cause 100% failure rates unless the rate limit is absolute zero throughput. Real-world rate limiting behavior:

- The first N requests before the limit hit are processed normally
- Requests beyond the limit receive HTTP 429 responses
- The client either retries (with backoff) or fails
- Some tests that launched before the rate limit was reached complete successfully

In a 48-test run with concurrency 30, the first wave of tests would begin before any rate limit is triggered. Tests B1 and B2 for sonnet and opus (the earliest to acquire semaphore slots) should complete if the only issue were rate limiting — because they hit the API before the burst overwhelms it.

The observed data shows **zero completions across all 3 runs**. If rate limiting were the cause, statistical variance alone should produce at least some completions in early-batch tests before the throttle fully activates. The total uniformity points away from rate limiting and toward a structural cause that affects every test regardless of execution order.

### Counter-Argument 3: The Actual Concurrency During the Failing Run Was NOT 30 for Behavioral Tests

The orchestrator was invoked with `--models sonnet,opus` (haiku excluded). The full test matrix at default concurrency:

- 5 runs x 2 models x 8 behavioral tests = 80 behavioral test slots
- But structural tests use a SEPARATE semaphore (`structural_semaphore=25`)
- Behavioral semaphore controls only the `claude -p` processes

With 2 models (instead of 3) and 5 runs, there are 80 behavioral tests total. The semaphore is 30, so at most 30 run simultaneously. However, with 5 parallel teams each running 16 behavioral tests (2 models x 8 tests), the actual simultaneous `claude -p` processes would approach 30 — but only if all 5 teams are in their behavioral phase simultaneously and have enough tests queued.

More critically: the actual invocation used `--runs 3` (the report shows "Runs: 3"), reducing to 48 behavioral tests total. With 48 tests and a semaphore of 30, the peak concurrent processes would be 30 for the first wave and then fewer as tests complete/timeout. This does not materially change the burst math, but it means the post-first-wave concurrency drops as tests timeout and free semaphore slots.

### Counter-Argument 4: The 700K Token Burst Is a Theoretical Maximum, Not a Measured Rate

The 700K token calculation assumes all 30 processes send their first API request simultaneously. In practice:

- asyncio is cooperative, not truly parallel — coroutines yield at await points
- The 30 processes do not all acquire the semaphore at exactly the same millisecond
- subprocess startup for each `claude -p` adds 2-5s of stagger
- npm resolution for MCP servers adds variable startup time per process

The actual burst is staggered across a window of 2-30 seconds of startup variance. This does not eliminate rate-limiting risk, but it significantly reduces the severity of the burst. An API endpoint that throttles at 500K simultaneous tokens might handle 700K tokens spread over a 30-second window without triggering rate limits.

### Counter-Argument 5: No HTTP 429 Evidence Was Collected

The RCA notes that `runner.py` only captures stderr when the process does NOT timeout (line 187). If a rate-limited process exits with HTTP 429 embedded in stderr and ALSO times out (because retries exhaust the timeout), the 429 is silently discarded. The absence of 429 evidence is therefore not evidence of absence — but it means CF-2 rests entirely on inference, not on observed rate-limit responses.

The proposed Experiment 8 (add HTTP 429 status code logging) would be necessary to confirm this theory. Without it, CF-2 remains an unverified hypothesis.

### Counter-Argument 6: The CLAUDECODE=1 Nesting Issue Offers a Competing Total-Failure Explanation

CF-3 (CLAUDECODE=1 inheritance) is documented to cause `claude -p` to refuse launch entirely with an immediate error. If the failing runs were executed from within a Claude Code session (which the environment confirms: `CLAUDECODE=1` is set), every subprocess attempt would fail immediately — not with a timeout, but with an exit code 1 and stderr error.

The RCA correctly notes this would NOT cause timeouts (immediate exit, not prolonged process). However, the interaction with the silent stderr capture (stderr only captured on non-timeout exit) means: if the process exits fast due to CLAUDECODE rejection, the harness would return `("TIMEOUT after Ns", -1)` only if there's ALSO a timeout... but a fast-exit process would NOT trigger the asyncio timeout. The harness would capture the fast exit as a non-timeout failure with exit code 1.

This means the timeout pattern actually ARGUES AGAINST CLAUDECODE nesting as the cause — and by extension, does not support the "global resource failure causes all-zero pattern" framing that CF-2 relies on for its uniform-pattern argument.

---

## Critical Evidence Gaps

1. **No HTTP status code logging**: No 429 responses were captured. Cannot confirm or deny API rate limiting.
2. **No single-test baseline**: No experiment was run with `--concurrency 1 --runs 1` to test whether a single isolated process completes. This is the definitive experiment to separate CF-2 (concurrency-dependent) from RC-1 (structurally guaranteed regardless of concurrency).
3. **No resource monitoring data**: No CPU/memory/network metrics during the failing run. The container resource ceiling claim is inference, not measurement.
4. **No timing data on process start stagger**: Unknown how spread out the 30 concurrent process startups actually are in practice.
5. **Previous-version concurrency not confirmed**: The 9.2% pass rate may have been achieved with different concurrency settings, or under conditions where the managed API endpoint had higher limits.

---

## Verdict

### Dimension Scores

| Dimension | Score (0-10) | Rationale |
|-----------|-------------|-----------|
| **Evidence Strength** | 4/10 | The token math and process count are real, but no 429 responses captured, no resource metrics collected, and the previous version produced partial completions under the same concurrency, directly weakening the causal claim. All evidence is inferential. |
| **Root Cause Likelihood** | 3/10 | CF-2 cannot be the primary root cause. The previous version used identical concurrency and produced 9.2% completions, directly falsifying CF-2 as sufficient. CF-2 is a real amplifier but not a discriminating cause — it was present in both the failing AND the partially-working runs. |
| **Fix Impact** | 5/10 | Reducing concurrency from 30 to 5 would reduce API burst load, MCP process overhead, and memory pressure. However, if RC-1 (allowed-tools) is the true root cause, reducing concurrency would not restore completions — tests would still exhaust all turns on tool calls rather than producing classification headers. The fix addresses a real problem, but not the right problem. |
| **Fix Feasibility** | 9/10 | Trivially easy to implement. A single `--concurrency 5` flag change, or modifying the default in orchestrator.py from `default=30` to `default=5`. Zero risk of introducing new failures. Should be done regardless of whether CF-2 is the root cause. |

### Composite Assessment

**CF-2 is a real contributing factor but an overweighted one.** The assigned likelihood of 85% in the RCA is too high. The single most damning counter-evidence is the previous version's 9.2% pass rate under the same concurrency — this demonstrates the infrastructure CAN produce completions at concurrency 30. The change to `allowed-tools` is the discriminating variable, not the concurrency level.

CF-2's true role is **amplification**, not causation. It amplifies RC-1 (tool-call exhaustion) and RC-3 (insufficient timeout budgets) by:
- Reducing the time budget available for actual model response (startup overhead competes with per-turn time)
- Increasing the probability that any per-turn API call is slower than the per-turn budget allows
- Creating orphan MCP processes from killed subprocesses (proc.kill() sends SIGKILL to direct child only) that compound resource pressure on subsequent test waves

**Revised likelihood estimate**: 50-60% as a contributing factor, with less than 15% probability of being a sufficient root cause in isolation.

**Recommended action**: Reduce concurrency to 5 as a low-risk, high-feasibility improvement that costs nothing to implement and eliminates one amplification pathway. But do not treat this as a substitute for fixing RC-1 (remove `allowed-tools` from frontmatter). If concurrency reduction alone is applied without addressing RC-1, the 0% behavioral pass rate will persist.

---

## Summary Table

| | CF-2 Claim | Verdict |
|---|---|---|
| 700K token burst causes rate limiting | Plausible but unverified | UNCONFIRMED |
| 60 npx processes cause MCP exhaustion | Real overhead, real risk | AMPLIFIER |
| 100% uniform failure consistent with global throttle | True but not discriminating | WEAK EVIDENCE |
| Previous version also used 30 concurrency | Directly falsifies CF-2 as sufficient cause | PROSECUTION LOSS |
| Fix (reduce to 5) restores completions | Only if RC-1 is also fixed | CONDITIONAL |
| Fix feasibility | One-line change | STRONG |
