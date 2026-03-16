# D-0006: OQ-008 Decision Record — Auggie MCP Unavailability Definition

## Merged Multi-Criteria Definition

Auggie MCP is considered **unavailable** if **ANY ONE** of the following three criteria is met:

| # | Criterion | Measurable Threshold | Trigger Rule |
|---|---|---|---|
| 1 | Timeout | Any query to Auggie MCP does not return within the tool's default timeout period | Single occurrence triggers fallback |
| 2 | Consecutive failures | 3 consecutive `codebase-retrieval` query failures (error response or empty result) | 3rd consecutive failure triggers fallback |
| 3 | Coverage confidence | Auggie MCP results cover <50% of the expected codebase surface for a given query (assessed by the agent executing the phase) | Any query where confidence in coverage drops below 50% triggers fallback |

**Activation rule**: Fallback activates on the FIRST occurrence of ANY criterion. No waiting for multiple criteria to be simultaneously true.

## Fallback Tool Chain

When ANY criterion above is met:

1. **Activate**: Serena MCP (`mcp__serena__*` tools) for symbol-level search and project memory
2. **Activate**: Grep/Glob (native file search tools) for pattern matching and file discovery
3. **Annotate**: All claims derived from fallback tools must be explicitly annotated as `[FALLBACK: Serena+Grep]` in the producing artifact

## Downstream Impact

- **Phase 7 (Citation Verification)**: Any analysis artifact produced under fallback conditions will have its citations flagged as `[UNVERIFIED — produced under Auggie fallback]`
- **Re-verification**: If Auggie MCP is restored during the sprint, the affected phase's codebase claims should be re-verified using Auggie and annotations updated
- **Continuity**: Fallback does not block phase execution; work continues with reduced codebase awareness, with limitations documented

## Current Status

- As of Phase 1 execution: Auggie MCP is **available** — no fallback active
- Criteria 1, 2, 3 all unsatisfied (zero failures, zero timeouts, coverage confident)
- See D-0001 for connectivity verification evidence

## References

- T01.01 evidence: D-0001 (Auggie connectivity record)
- Roadmap OQ-008 specification: merged multi-criteria definition
- MCP.md §Auggie MCP Integration: fallback rules (Serena + Grep/Glob)
