# Group B: Architecture & Feasibility (6 proposals)

These proposals address architectural invariants, runtime feasibility, and system-level design concerns.

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

**Category**: architecture | **Severity**: major
**Affected sections**: [4.1 principle 2, 4.3, 14.1]
**Current state**: Architecture says orchestrator never reads source code; error fallback for adversarial failure asks orchestrator to directly rank findings content, potentially exceeding bounded role and token budget.
**Proposed change**: Replace fallback with delegated lightweight scoring agent(s); orchestrator should only read generated summaries.
**Rationale**: Preserves architectural invariant and token model while maintaining degraded operation.
**Impact**: Error handling pipeline, token budget assumptions, implementation complexity.

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

**Category**: feasibility | **Severity**: major
**Affected sections**: [3.1 FR-006/011/016/024/035, 4.3, 16.1, Appendix B]
**Current state**: Strict per-phase token caps are specified but no policy defines what to do when context inputs exceed those budgets.
**Proposed change**: Define budget policy: soft target + hard stop + fallback action (summarize, sample, or defer) with explicit warning artifact.
**Rationale**: Fixed caps are not realistically guaranteed for variable-size artifacts without deterministic truncation rules.
**Impact**: Orchestrator implementation, observability, quality metric interpretation.

## PROPOSAL-013: Add capability fallback for model-tier assignment

**Category**: feasibility | **Severity**: critical
**Affected sections**: [3.1 FR-010, 4.3, 7, 8, 10]
**Current state**: Spec assumes direct control over Haiku/Sonnet/Opus assignment per agent, which may not always be enforceable in runtime/delegation contexts.
**Proposed change**: Define "requested tier" vs "actual tier" fields in phase metadata and require logging of tier substitution when hard assignment is unavailable.
**Rationale**: Prevents silent divergence between spec intent and runtime behavior.
**Impact**: Agent invocation contracts, quality metrics, cost reporting.

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

**Category**: feasibility | **Severity**: major
**Affected sections**: [5.1, 6.1, 11, 14.2]
**Current state**: Command frontmatter allows only basic tools plus Skill/Task, yet fallback rules rely on Edit/MultiEdit; MCP calls are assumed available without explicit deferred-tool loading protocol.
**Proposed change**: Update allowed tool contract and add explicit MCP availability/activation preconditions (including fallback to native tool set).
**Rationale**: Current spec can fail at runtime due to undeclared tool dependencies.
**Impact**: Command/skill metadata, implementation guardrails, error handling.

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

**Category**: edge-case | **Severity**: critical
**Affected sections**: [3.1 FR-005, 7.0, 9.4]
**Current state**: Domain count is fixed to 3-10 and schema enforces minItems=3, which is impossible for tiny scopes (e.g., 1-3 files).
**Proposed change**: Make domain count adaptive (`1..10`) with merge/split heuristics and explicit minimum of 1 when source files exist.
**Rationale**: Prevents forced synthetic domains that dilute analysis quality and distort risk.
**Impact**: Domain generation algorithm, schema validation, downstream agent count.

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

**Category**: architecture | **Severity**: major
**Affected sections**: [3.2 NFR-010 (panel), 7.1, 11, 14.3, 17]
**Current state**: Per-server concurrency cap is mentioned in commentary but no scheduling contract exists (queueing, fairness, backoff, priority).
**Proposed change**: Define MCP-aware scheduler: per-server semaphores, exponential backoff policy, and deterministic queue ordering for resumability.
**Rationale**: Without scheduling rules, high parallelism can trigger avoidable circuit-breaker degradation and non-deterministic outcomes.
**Impact**: Runtime orchestration, performance characteristics, reproducibility.
