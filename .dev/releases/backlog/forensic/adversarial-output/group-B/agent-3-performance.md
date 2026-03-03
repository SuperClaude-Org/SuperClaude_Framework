# Agent 3: Performance Perspective Assessment
## Group B -- Architecture & Feasibility Proposals

**Evaluator**: Performance / Cost Efficiency Engineer
**Lens**: Token cost, latency overhead, benefit-to-cost ratio
**Date**: 2026-02-26

---

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

**Verdict**: MODIFY

**Cost/Latency Analysis**:
The current fallback (orchestrator reads findings directly) costs approximately 2,000-5,000 tokens depending on finding count -- expensive but bounded and fast (single-agent, no coordination overhead, no sub-agent spawn latency).

The proposed replacement (delegated lightweight scoring agents) adds:
- Sub-agent spawn latency: ~5-15 seconds per agent
- Agent prompt overhead: ~300-500 tokens per agent
- Coordination overhead: orchestrator must collect results
- Total additional cost: ~1,000-3,000 tokens above the direct-read approach

This is the fallback path -- it should optimize for speed and cost, not architectural purity. The fallback fires only when the adversarial protocol has already failed, meaning token budgets are likely already stressed.

**Modification Required**: Use a single scoring agent (not multiple) with a strict 1,000-token output cap. The benefit (preserving the dispatcher invariant) justifies the overhead of ONE agent but not multiple agents. If the single agent also fails, emit a passthrough result at zero additional cost.

**Benefit/Cost Ratio**: Low as proposed (multiple agents in error path). Acceptable with single-agent modification.

**Score**: 6.5/10 (as proposed), 8.2/10 (with modification)

---

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

**Verdict**: ACCEPT

**Cost/Latency Analysis**:
This proposal has net-positive cost impact. The current undefined overflow behavior means implementers will either silently exceed budgets (increasing cost) or panic-truncate (requiring reruns, increasing cost further). Explicit overflow policy with "warning artifact" output enables budget awareness without the cost of enforcement machinery.

The "summarize" fallback action is particularly cost-efficient -- it trades ~200 tokens of summarization overhead for potentially thousands of tokens in budget exceedance prevention.

Key cost concern: the "warning artifact" itself must be cheap. A simple JSON flag (`"budget_exceeded": true, "actual_tokens": 780, "target": 500`) costs ~30 tokens. A verbose warning report would defeat the purpose.

**Latency Impact**: Negligible. Overflow detection is a post-hoc check, not a blocking operation.

**Benefit/Cost Ratio**: High. Small implementation overhead for significant cost predictability improvement.

**Score**: 8.5/10

---

## PROPOSAL-013: Add capability fallback for model-tier assignment

**Verdict**: ACCEPT

**Cost/Latency Analysis**:
This proposal has the highest cost impact of any in Group B. The spec's cost model assumes Haiku ($0.25/1M input) for Phase 0, Sonnet ($3/1M input) for Phase 1 high-risk, and Opus ($15/1M input) for orchestrator only. If tier assignment is not enforceable and all agents run as Opus, the cost multiplier is:

- Phase 0: 60x over-budget (Opus vs Haiku)
- Phase 1 low-risk: 60x over-budget (Opus vs Haiku)
- Phase 1 high-risk: 5x over-budget (Opus vs Sonnet)
- Phase 3: 5x over-budget (Opus vs Sonnet)

Total pipeline cost could be 10-30x the spec projection. The "requested tier" vs "actual tier" logging adds approximately 50 tokens per phase transition -- negligible overhead for essential cost observability.

**Latency Impact**: Opus agents are slower than Haiku/Sonnet. If all agents run as Opus, Phase 0 (3 parallel agents) takes approximately 30-60 seconds instead of 5-10 seconds. Phase 1 with 10 parallel agents could take 2-5 minutes instead of 30-60 seconds.

**Benefit/Cost Ratio**: Extremely high. 50 tokens of logging overhead to detect potential 10-30x cost overruns.

**Score**: 9.5/10

---

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

**Verdict**: ACCEPT

**Cost/Latency Analysis**:
The cost of NOT fixing this is catastrophic. If Phase 4 agents fail to activate MCP tools and the fallback chain is also broken (Edit/MultiEdit not in allowed-tools), the entire implementation phase fails. The pipeline must then either abort (wasting all prior phase tokens, estimated 15,000-30,000 tokens) or be restarted with corrected tool contracts.

The fix itself is zero-cost at runtime -- it is a spec correction that updates the `allowed-tools` list and adds MCP activation preconditions. The only "cost" is ~100 tokens of additional agent prompt context for MCP activation instructions.

**Latency Impact**: MCP ToolSearch activation adds ~1-3 seconds per agent. For the 3-5 agents in Phase 4, this is 3-15 seconds of additional latency -- acceptable.

**Benefit/Cost Ratio**: Near-infinite. Zero runtime cost to prevent total phase failure.

**Score**: 9.3/10

---

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

**Verdict**: ACCEPT

**Cost/Latency Analysis**:
For tiny targets, the forced 3-domain minimum creates measurable waste:

**Single-file target cost comparison**:
- 3 domains (current): 3 Phase 1 agents (~4,500 tokens) + adversarial debate on 3 findings (~3,000 tokens) + 3 fix proposal agents (~4,500 tokens) = ~12,000 tokens
- 1 domain (proposed): 1 Phase 1 agent (~1,500 tokens) + simplified debate (~500 tokens) + 1 fix proposal agent (~1,500 tokens) = ~3,500 tokens

**Savings**: ~8,500 tokens (71% reduction) for single-file targets. Latency reduction proportional.

For large targets (50+ files), the proposal has no cost impact -- domain count will naturally reach 3-10.

**Latency Impact**: For single-file targets, pipeline time drops from ~3-5 minutes to ~1-2 minutes.

**Benefit/Cost Ratio**: Very high for small targets, neutral for large targets.

**Score**: 9.2/10

---

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

**Verdict**: REJECT

**Cost/Latency Analysis**:
The proposed scheduler (per-server semaphores, exponential backoff, deterministic queue ordering) adds significant overhead with questionable benefit:

**Overhead Analysis**:
- Semaphore state management: ~200-500 tokens of orchestrator context per phase
- Backoff delays: Exponential backoff on 10 agents hitting Serena means some agents wait 2^N seconds. For N=3 (reasonable with 10 concurrent agents), that is 8-second delays, cascading to 30+ seconds.
- Queue ordering logic: ~300-500 tokens of prompt context for deterministic ordering rules
- Total overhead: ~500-1,000 tokens per phase + significant latency increase

**The core problem**: Serializing MCP access defeats the purpose of parallel agents. If 10 agents must queue for Serena access, you get sequential execution with parallel overhead -- the worst of both worlds.

**Alternative**: Reduce default concurrency to 5 and define per-agent MCP call budgets in prompts. This is zero-overhead (no scheduler tokens) and achieves 80% of the benefit through demand reduction rather than supply management.

**Benefit/Cost Ratio**: Negative. The scheduler overhead exceeds the benefit of avoiding circuit breaker trips. Demand reduction (lower concurrency + call budgets) is cheaper.

**Score**: 4.0/10

---

## Summary

| Proposal | Verdict | Score | Key Reasoning |
|----------|---------|-------|---------------|
| P-011 | MODIFY | 6.5 -> 8.2 | Single agent fallback; error path must minimize cost |
| P-012 | ACCEPT | 8.5 | Net cost-positive; prevents budget overruns |
| P-013 | ACCEPT | 9.5 | Detects potential 10-30x cost overruns |
| P-014 | ACCEPT | 9.3 | Prevents total phase failure (wasting 15-30K tokens) |
| P-015 | ACCEPT | 9.2 | 71% cost reduction for small targets |
| P-022 | REJECT | 4.0 | Scheduler overhead exceeds benefit; demand reduction is cheaper |
