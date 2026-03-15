# Base Selection: Post-Preflight Phase Handling (Q5)

## Quantitative Scoring

| Metric | Weight | 2a (Skip) | 2b (Claude) | 2c (Config) |
|--------|--------|-----------|-------------|-------------|
| Correctness | 0.25 | 8 | 7 | 7 |
| Cost efficiency | 0.20 | 10 | 4 | 9 |
| Trust model | 0.20 | 7 | 9 | 8 |
| Implementation complexity | 0.20 | 9 | 6 | 5 |
| User experience | 0.15 | 8 | 7 | 7 |
| **Weighted total** | **1.00** | **8.40** | **6.60** | **7.20** |

## Qualitative Assessment

### 2a Strengths
- Reuses `AggregatedPhaseReport.to_markdown()` -- already tested, already produces the exact format `_determine_phase_status()` expects
- Zero new interaction patterns with Claude (no prompt injection concerns)
- Failure mode is clean: preflight fails -> fall back to normal execution (no skip)
- Aligns with the sprint runner's existing philosophy of runner-constructed reports (see `aggregate_task_results()` docstring: "runner's authoritative source of task outcomes")

### 2a Weaknesses
- No reasoning trace in result files for preflight-passed phases
- If someone later adds semantic validation to `_determine_phase_status()`, Python's static output might not satisfy it
- "Silent success" -- operator cannot distinguish "preflight passed" from "Claude passed" without checking execution logs

### 2b Strengths
- Independent verification layer with different failure modes
- Consistent result file authorship (always Claude)
- Adapts to contract evolution without code changes

### 2b Weaknesses
- 60-80% of normal token cost for phases that are, by definition, mechanical
- Untested interaction pattern (injecting pre-computed results into Claude prompt)
- Claude may over-validate or under-validate depending on prompt engineering quality
- Adds latency: 2-5 minutes per phase for subprocess startup + validation

### 2c Strengths
- User agency over the trust/cost tradeoff
- Progressive adoption: start with skip, enable verification when needed
- Follows existing flag patterns (`--shadow-gates`)

### 2c Weaknesses
- Highest implementation complexity: both code paths + routing logic + CLI flag + tests for both
- The `--verify-preflight` path will receive less testing and may rot
- Adds cognitive load: users must understand what preflight verification means to decide whether to enable it

## Combined Score and Selection

**Selected base: 2a (Skip entirely)**

### Rationale

1. **The codebase already validates this approach.** `AggregatedPhaseReport.to_markdown()` exists at executor.py:244-282 and produces the exact output that `_determine_phase_status()` parses. This is not speculative -- it is reusing production code.

2. **The runner philosophy favors runner-constructed reports.** The `aggregate_task_results()` function (executor.py:285-330) is explicitly documented as "the runner's authoritative source of task outcomes" that "does not rely on agent self-reporting." Preflight results are an extension of this philosophy.

3. **Cost savings are the primary motivation for preflight.** If the system still spawns a Claude subprocess (2b), the preflight hook's value proposition collapses to "run tasks earlier" rather than "skip Claude entirely." The marginal benefit of earlier execution without token savings does not justify the feature's complexity.

4. **The "silent success" weakness is addressable without 2b/2c.** Add a `source: preflight` field to the YAML frontmatter and a log line in `execute_sprint()`: `"Phase {n} passed preflight -- skipping Claude subprocess"`. This gives operators visibility without the cost of a Claude subprocess.

5. **The contract evolution risk is manageable.** The result contract is defined in this codebase, not in an external system. Changes to the contract update both the writer (`AggregatedPhaseReport.to_markdown()`) and the parser (`_determine_phase_status()`) in the same commit. This is a standard software engineering practice.

### Mitigations for 2a Weaknesses

| Weakness | Mitigation |
|----------|------------|
| No reasoning trace | Add `source: preflight` YAML field; log preflight outcomes to execution log |
| Contract drift risk | Shared test fixtures that verify writer output satisfies parser expectations |
| Silent success | Distinct `PhaseStatus.PREFLIGHT_PASS` enum value for TUI differentiation |

## Selection Confidence: 85%

The 15% uncertainty comes from the irreducible disagreement about the value of AI verification for mechanical tasks. If empirical data from production sprint runs shows that preflight-passed phases later reveal issues that Claude would have caught, the recommendation should be revisited toward 2c.
