# Agent 2: DevOps Perspective Assessment
## Group B -- Architecture & Feasibility Proposals

**Evaluator**: DevOps / Runtime Feasibility Engineer
**Lens**: Runtime constraints, operational reality, failure modes in production
**Date**: 2026-02-26

---

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

**Verdict**: MODIFY

**Runtime Analysis**:
The proposal is directionally correct, but replacing the adversarial fallback with "delegated lightweight scoring agent(s)" introduces a new failure mode. When the adversarial protocol has already failed, spawning additional agents increases the probability of cascading failure -- the very scenario this fallback is meant to handle. In production, when things go wrong, you want the simplest possible recovery path, not more delegation.

The current fallback (orchestrator reads findings directly) is architecturally impure but operationally robust. It is a single-agent operation with no coordination overhead.

**Modification Required**: The fallback should use a SINGLE lightweight scoring agent (not plural), with a hard timeout of 60 seconds. If even that agent fails, the orchestrator should emit the raw findings file paths in the final report with a "debate-skipped" flag, rather than attempting further delegation. The fallback chain should be: (1) adversarial protocol, (2) single scoring agent, (3) passthrough with degradation notice. Three levels, no more.

**Production Failure Scenario**: Adversarial protocol fails due to token exhaustion. Spawning multiple scoring agents compounds the token problem. A single agent with a hard cap is safer.

**Score**: 7.0/10 (as proposed), 8.5/10 (with modification)

---

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

**Verdict**: ACCEPT

**Runtime Analysis**:
This is the most operationally critical proposal in the group. The current spec states hard token caps as SHOULD requirements but provides zero guidance on what happens when they are exceeded. In practice, token consumption is non-deterministic -- a Phase 0 synthesis on a large monorepo will almost certainly exceed 500 tokens. Without overflow policy, implementers will either (a) silently ignore the caps, making them meaningless, or (b) hard-truncate mid-sentence, corrupting downstream artifacts.

The soft-target + hard-stop + fallback-action model is exactly what production systems need. The "warning artifact" component is especially valuable -- it provides observability into budget exceedances without blocking the pipeline.

**Production Failure Scenario**: Phase 0 discovers 10 domains with rich descriptions, exceeding the 500-token synthesis budget. Without overflow policy, the orchestrator either truncates arbitrarily (corrupting domain definitions) or exceeds budget silently (breaking cost assumptions). The proposed policy handles this explicitly.

**Implementation Concern**: The "summarize, sample, or defer" actions need to be deterministic per phase. "Summarize" for Phase 0 domain synthesis, "sample" (top-N by risk score) for Phase 1 collection, "defer" is not applicable in a pipeline context. The spec should map actions to phases.

**Score**: 8.8/10

---

## PROPOSAL-013: Add capability fallback for model-tier assignment

**Verdict**: ACCEPT

**Runtime Analysis**:
This is the single most important feasibility fix. Claude Code's `Task` tool spawns sub-agents but does not expose a model-selection parameter. The spec's assumption that you can assign Haiku vs Sonnet vs Opus per agent is not enforceable in the current runtime. Every single tier assignment in the spec (FR-010, Phase 0 Haiku agents, Phase 3 Sonnet agents, Phase 6 Opus synthesis) is aspirational at best.

The "requested tier" vs "actual tier" metadata fields are the minimum viable solution. Without this, the entire cost model and quality model are unverifiable.

**Production Failure Scenario**: All agents run as Opus (the default for Task sub-agents in some configurations). Cost is 10-30x the spec's projection. Quality is fine, but the cost model is meaningless. With tier logging, at least you can detect and report the divergence.

**Additional Recommendation**: The spec should also define a "tier enforcement strategy" field that is currently "best-effort" but could evolve to "prompt-based hinting" (asking the agent to self-limit its reasoning depth) as a soft enforcement mechanism.

**Score**: 9.5/10

---

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

**Verdict**: ACCEPT

**Runtime Analysis**:
This is a real and immediate implementation blocker. The `allowed-tools` frontmatter in Claude Code is enforced -- if Edit/MultiEdit are not in the list, the command literally cannot fall back to them. The fallback in Section 14.2 ("falls back to Edit/MultiEdit tools") is dead code under the current tool contract.

The MCP deferred-tool loading issue is equally real. MCP tools like Serena's `replace_symbol_body` require explicit `ToolSearch` activation before use. The spec assumes they are available but never specifies the activation step. In production, the first Serena call in Phase 4 would fail with a "tool not found" error.

**Production Failure Scenario**: Phase 4 implementation agent calls `replace_symbol_body` without prior `ToolSearch` activation. The call fails. The agent retries. The retry fails. The circuit breaker trips. The entire implementation phase falls back to... Edit/MultiEdit, which are also not in the allowed-tools list. Complete Phase 4 failure.

**Score**: 9.2/10

---

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

**Verdict**: ACCEPT

**Runtime Analysis**:
Forcing 3 domains for a 1-file target creates operational absurdity. Three Phase 1 investigation agents would be spawned to investigate a single file, each producing findings that overlap heavily. The adversarial debate in Phase 2 would then compare three nearly-identical findings sets, producing meaningless debate.

The adaptive 1..10 range is correct. For tiny targets (1-3 files), a single domain is sufficient and dramatically reduces pipeline cost and latency.

**Production Failure Scenario**: User runs `/sc:forensic src/auth/middleware.py` on a single file. Phase 0 is forced to invent 3 domains (e.g., "middleware logic", "middleware imports", "middleware tests"). Three agents investigate the same file from nearly identical angles. The adversarial debate finds no contradictions because all three agree. Cost is 3x what it should be, time is 3x, and the report adds no value over a single-domain analysis.

**Score**: 9.0/10

---

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

**Verdict**: MODIFY

**Runtime Analysis**:
The operational concern is valid -- running 10 Phase 1 agents each hitting Serena simultaneously will trigger circuit breakers. This is explicitly acknowledged in Section 17 of the spec. However, the proposed solution (per-server semaphores, exponential backoff, deterministic queue ordering) is over-engineered for the current runtime.

Claude Code's Task tool does not expose semaphore or queue primitives. The orchestrator cannot enforce per-server concurrency because it does not control when sub-agents make MCP calls -- the agents run autonomously once spawned.

**Modification Required**: Instead of a scheduler, define MCP access budgets per phase in the agent prompt templates. For example: "You may make at most 3 Serena calls per domain investigation." This is enforceable via prompt engineering, not runtime infrastructure. Additionally, reduce the default `--concurrency` value from 10 to 5 to provide a safety margin against MCP saturation.

**Production Failure Scenario**: 10 agents spawn simultaneously, each calling Serena 5+ times in the first 10 seconds. Serena circuit breaker trips at 4 failures. All subsequent Serena calls in the pipeline fail. By the time the HALF_OPEN state is tested, the agents have already fallen back to Grep, producing lower-quality findings.

**Score**: 5.5/10 (as proposed -- not implementable), 8.0/10 (with modification)

---

## Summary

| Proposal | Verdict | Score | Key Reasoning |
|----------|---------|-------|---------------|
| P-011 | MODIFY | 7.0 -> 8.5 | Single fallback agent + passthrough, not plural agents |
| P-012 | ACCEPT | 8.8 | Critical operational gap, needs phase-specific action mapping |
| P-013 | ACCEPT | 9.5 | Most important feasibility fix; tier control is aspirational |
| P-014 | ACCEPT | 9.2 | Immediate implementation blocker; dead fallback code |
| P-015 | ACCEPT | 9.0 | Operational absurdity for tiny targets |
| P-022 | MODIFY | 5.5 -> 8.0 | Not implementable as specified; use prompt budgets instead |
