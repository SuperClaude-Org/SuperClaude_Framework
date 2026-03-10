# Agent 1: Architect Perspective Assessment
## Group B -- Architecture & Feasibility Proposals

**Evaluator**: System Architect
**Lens**: Architectural purity, invariant preservation, orchestrator-as-dispatcher principle
**Date**: 2026-02-26

---

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

**Verdict**: ACCEPT

**Architectural Analysis**:
This proposal directly addresses a violation of Design Principle 2 (Section 4.1): "The orchestrator never reads source code directly; it reads only agent summaries and phase artifacts." The current fallback in Section 14.1 asks the orchestrator to "read all findings and rank by confidence score directly" upon adversarial protocol failure. While "findings" are agent-produced artifacts (not raw source), the phrase "reads all findings" is ambiguous and the ranking operation itself exceeds the dispatcher role -- the orchestrator should never perform analytical scoring, only consume pre-scored results.

Replacing this with a delegated lightweight scoring agent preserves the architectural invariant cleanly. The orchestrator remains a dispatcher even in degraded mode.

**Invariant Impact**: Strengthens Principle 2. Removes the single point where the orchestrator could be interpreted as exceeding its bounded role.

**Consistency Check**: Consistent with the entire phase architecture (Section 4.2) where every analytical operation is delegated to sub-agents.

**Score**: 9.2/10

---

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

**Verdict**: MODIFY

**Architectural Analysis**:
The proposal correctly identifies that fixed token caps (FR-006: 500 tokens, FR-011: 1000 tokens, FR-016: 500 tokens, FR-024: 800 tokens, FR-035: 2000 tokens) lack overflow semantics. Architecturally, these are stated as SHOULD requirements, not MUST -- so they already have implicit flexibility. However, the absence of explicit overflow behavior creates an undefined state that violates the principle of deterministic phase transitions.

The soft-target + hard-stop + fallback-action model is architecturally sound. However, the proposal should NOT introduce runtime token counting at the orchestrator level -- that would add coupling between the orchestrator and the execution runtime. Instead, overflow policy should be defined as a static contract in the spec (e.g., "if Phase 0 synthesis exceeds 750 tokens, truncate domain descriptions to single sentences").

**Modification Required**: Define overflow behavior as static rules in the spec rather than runtime monitoring. The orchestrator should not gain token-counting capabilities -- it should receive pre-truncated inputs from agents who own their own budgets.

**Invariant Impact**: Neutral if implemented as static rules; weakens dispatcher principle if implemented as runtime monitoring.

**Score**: 7.5/10 (as proposed), 8.8/10 (with modification)

---

## PROPOSAL-013: Add capability fallback for model-tier assignment

**Verdict**: ACCEPT

**Architectural Analysis**:
This proposal addresses a real architectural gap. The spec assumes deterministic model tier control (FR-010: "High-risk domains SHALL use Sonnet-tier agents"), but Claude Code's Task tool does not guarantee model selection for sub-agents. The "requested tier" vs "actual tier" distinction is architecturally sound -- it introduces observability without changing the dispatcher model.

The key insight is that tier assignment is an intent declaration, not a runtime guarantee. Logging substitutions preserves the spec's quality and cost model as aspirational targets while acknowledging runtime constraints. This is consistent with the checkpoint/resume model -- if a phase ran with Haiku instead of Sonnet, the checkpoint should record that fact for auditability.

**Invariant Impact**: Strengthens observability (NFR-006) without altering the orchestrator's role.

**Score**: 9.0/10

---

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

**Verdict**: ACCEPT

**Architectural Analysis**:
The frontmatter in Section 5.1 lists `allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill`. Section 6.1 repeats the same list. However, Section 14.2 states that Phase 4 falls back to "Edit/MultiEdit tools" when Serena is unavailable -- tools not in the allowed set. Furthermore, MCP servers (sequential, serena, context7) are listed in the frontmatter but the spec never addresses the deferred-tool loading protocol required by the Claude Code runtime.

This is an architectural inconsistency. The tool contract must be the single source of truth for what the command can invoke. Either Edit/MultiEdit must be added to `allowed-tools`, or the fallback must use only tools already in the contract.

The proposal to add explicit MCP availability preconditions is also architecturally correct -- the current assumption of MCP availability is implicit and fragile.

**Invariant Impact**: Strengthens the tool contract boundary. Makes the fallback chain verifiable against declared capabilities.

**Score**: 8.7/10

---

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

**Verdict**: ACCEPT

**Architectural Analysis**:
FR-005 mandates 3-10 domains with a schema enforcing `minItems=3`. For a target of 1-3 files, forcing 3 domains creates synthetic boundaries that violate Principle 1 (Generic-first) and Principle 4 (Leverage existing patterns). The cleanup-audit protocol handles small targets by reducing domain count -- the forensic spec should follow the same pattern.

Making domain count adaptive (1..10) with merge/split heuristics preserves the auto-discovery invariant while allowing the system to degrade gracefully for small inputs. The orchestrator's dispatcher role is unaffected -- it still reads domain definitions from Phase 0, just fewer of them.

**Invariant Impact**: Strengthens Principle 1 (Generic-first) by making the system work correctly at all scales.

**Score**: 9.1/10

---

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

**Verdict**: MODIFY

**Architectural Analysis**:
The proposal correctly identifies that NFR-010 mentions per-server concurrency caps without scheduling semantics. However, the proposed solution (per-server semaphores, exponential backoff, deterministic queue ordering) introduces significant architectural complexity. The orchestrator is a dispatcher -- adding a scheduler to it conflates two responsibilities.

The scheduling concern is legitimate but belongs at the runtime infrastructure layer, not in the forensic spec. The forensic spec should declare its concurrency requirements and MCP access patterns; the Claude Code runtime (or a shared MCP scheduling layer) should enforce them.

**Modification Required**: Instead of specifying a full scheduler in the forensic spec, define MCP access patterns per phase (e.g., "Phase 1 agents each make at most 2 Serena calls") and recommend that the runtime layer enforce per-server semaphores. The forensic spec should specify backoff behavior only for its own retry logic (Section 14.1), not for MCP infrastructure.

**Invariant Impact**: Risk of violating single-responsibility if scheduler is embedded in orchestrator. Modification preserves clean boundaries.

**Score**: 6.8/10 (as proposed), 8.5/10 (with modification)

---

## Summary

| Proposal | Verdict | Score | Key Reasoning |
|----------|---------|-------|---------------|
| P-011 | ACCEPT | 9.2 | Removes invariant violation in fallback path |
| P-012 | MODIFY | 7.5 -> 8.8 | Static overflow rules, not runtime monitoring |
| P-013 | ACCEPT | 9.0 | Observability gain, no dispatcher impact |
| P-014 | ACCEPT | 8.7 | Tool contract must be authoritative |
| P-015 | ACCEPT | 9.1 | Generic-first principle demands scale adaptivity |
| P-022 | MODIFY | 6.8 -> 8.5 | Scheduling belongs at runtime layer, not in spec |
