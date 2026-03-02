# Group B Verdicts: Architecture & Feasibility Proposals
## Adversarial Assessment -- Final Merged Results

**Agents**: Architect (A1), DevOps (A2), Performance (A3)
**Depth**: Standard (2 rounds)
**Convergence achieved**: 1.0 (target: 0.80)
**Focus**: architectural-integrity, runtime-feasibility, cost-efficiency
**Date**: 2026-02-26

---

## Scoring Methodology

**Hybrid scoring** combines three weighted dimensions:
- Architectural Integrity (A1): 35% weight
- Runtime Feasibility (A2): 35% weight
- Cost Efficiency (A3): 30% weight

Scores are on a 0-10 scale. Verdicts are determined by:
- ACCEPT: weighted score >= 8.0 and no agent scores below 7.0
- MODIFY: weighted score >= 7.0 but at least one agent flags a required change
- REJECT: weighted score < 7.0 or any agent scores below 5.0

---

## PROPOSAL-011: Remove orchestrator-source-read fallback contradiction

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 7.0 (MODIFY) | 8.5 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 6.5 (MODIFY) | 8.2 (ACCEPT) | 30% |

**Weighted Score**: (9.2 * 0.35) + (8.5 * 0.35) + (8.2 * 0.30) = 3.22 + 2.975 + 2.46 = **8.66**

### VERDICT: ACCEPT

**Consensus specification**: Replace the current adversarial-failure fallback with a three-level degradation chain:

1. **Level 1**: Retry adversarial protocol with `--depth quick`
2. **Level 2**: Spawn a single Sonnet scoring agent with 60-second hard timeout and 1,000-token output cap. The agent reads all finding summaries and produces a ranked list by confidence score.
3. **Level 3**: If the scoring agent also fails, emit finding file paths directly in the phase output with metadata `"debate_status": "skipped"`. The orchestrator passes these through to Phase 3 without scoring -- all surviving hypotheses proceed to fix proposal generation.

**Spec changes required**:
- Section 14.1: Replace "orchestrator reads all findings and ranks by confidence score directly" with the three-level chain above
- Section 4.3: No change needed (orchestrator constraint preserved)

---

## PROPOSAL-012: Convert hard token ceilings to enforceable policy with overflow behavior

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 7.5 (MODIFY) | 8.8 (MODIFY) | 35% |
| Runtime Feasibility | A2 | 8.8 (ACCEPT) | 8.8 (MODIFY) | 35% |
| Cost Efficiency | A3 | 8.5 (ACCEPT) | 8.5 (ACCEPT) | 30% |

**Weighted Score**: (8.8 * 0.35) + (8.8 * 0.35) + (8.5 * 0.30) = 3.08 + 3.08 + 2.55 = **8.71**

### VERDICT: MODIFY

**Modification**: Implement as static per-phase rules in the spec (not runtime token monitoring). Define each phase's budget as a soft target (SHOULD) and hard stop (MUST) with a deterministic truncation action.

**Per-phase overflow policy table** (add to Section 4.3 or new Section 4.4):

| Phase | Context | Soft Target | Hard Stop | Overflow Action |
|-------|---------|-------------|-----------|-----------------|
| Phase 0 synthesis | FR-006 | 500 tokens | 750 tokens | Truncate domain descriptions to single sentence |
| Phase 1 collection | FR-011 | 1,000 tokens | 1,500 tokens | List file paths only; omit finding summaries |
| Phase 2 consumption | FR-016 | 500 tokens | 750 tokens | Read top-N hypotheses by confidence; skip lowest |
| Phase 3b consumption | FR-024 | 800 tokens | 1,200 tokens | Read top-N fixes by composite score; skip lowest |
| Phase 6 synthesis | FR-035 | 2,000 tokens | 3,000 tokens | Omit rejected-hypotheses section from final report |

**Warning artifact**: Each phase emits a `budget_status` field in `progress.json`:
```json
{
  "phase": "phase_0",
  "budget_status": "exceeded",
  "soft_target": 500,
  "hard_stop": 750,
  "overflow_action_taken": "truncate_descriptions"
}
```

**Spec changes required**:
- New Section 4.4 "Token Budget Overflow Policy" with the table above
- Section 12 (Checkpoint): Add `budget_status` to `progress.json` schema
- FR-006, FR-011, FR-016, FR-024, FR-035: Reword as soft targets with reference to overflow policy

---

## PROPOSAL-013: Add capability fallback for model-tier assignment

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.0 (ACCEPT) | 9.0 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.5 (ACCEPT) | 9.5 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.5 (ACCEPT) | 9.5 (ACCEPT) | 30% |

**Weighted Score**: (9.0 * 0.35) + (9.5 * 0.35) + (9.5 * 0.30) = 3.15 + 3.325 + 2.85 = **9.33**

### VERDICT: ACCEPT

**Consensus specification**: Add `requested_tier` and `actual_tier` fields to all phase metadata and agent invocation records.

**Implementation**:
1. Each agent invocation record in `progress.json` includes:
   ```json
   {
     "agent": "investigation-domain-3",
     "requested_tier": "sonnet",
     "actual_tier": "unknown",
     "tier_source": "best-effort"
   }
   ```
2. The `actual_tier` field defaults to `"unknown"` since Claude Code does not currently expose the model used by Task sub-agents. Future runtime improvements may populate this field.
3. The `tier_source` field indicates the enforcement mechanism: `"best-effort"` (prompt hinting), `"verified"` (runtime confirmation), `"overridden"` (user forced a different tier).
4. The final report includes a "Model Tier Compliance" section summarizing requested vs actual tiers across all phases.

**Spec changes required**:
- Section 8 (Agent Specifications): Add `requested_tier` to each agent definition
- Section 9 (Data Schemas): Add tier fields to agent invocation schema
- Section 12 (Checkpoint): Add tier tracking to `progress.json`
- Section 13 (Output Templates): Add tier compliance section to final report template

---

## PROPOSAL-014: Reconcile MCP tool assumptions with executable tool contract

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 8.7 (ACCEPT) | 8.7 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.3 (ACCEPT) | 9.3 (ACCEPT) | 30% |

**Weighted Score**: (8.7 * 0.35) + (9.2 * 0.35) + (9.3 * 0.30) = 3.045 + 3.22 + 2.79 = **9.06**

### VERDICT: ACCEPT

**Consensus specification**:

1. **Update `allowed-tools`** in both command (Section 5.1) and skill (Section 6.1) frontmatter:
   ```yaml
   allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill, Edit, MultiEdit
   ```

2. **Add MCP activation precondition** to agent prompt templates (Section 8):
   ```
   PRECONDITION: Before using any MCP tool (Serena, Context7, Sequential),
   invoke ToolSearch to load the required tool. Example:
     ToolSearch("select:mcp__serena__replace_symbol_body")
   If ToolSearch fails, fall back to native tool equivalents:
     - Serena replace_symbol_body -> Edit tool
     - Serena find_referencing_symbols -> Grep tool
     - Context7 -> WebSearch or WebFetch
   ```

3. **Update fallback chain** in Section 14.2 to reference only tools in the `allowed-tools` contract.

**Spec changes required**:
- Section 5.1: Add Edit, MultiEdit to allowed-tools
- Section 6.1: Add Edit, MultiEdit to allowed-tools
- Section 8: Add MCP activation precondition to agent templates
- Section 14.2: Verify all fallback tools are in the allowed-tools list

---

## PROPOSAL-015: Resolve minimum-domain rule for tiny targets

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 9.1 (ACCEPT) | 9.1 (ACCEPT) | 35% |
| Runtime Feasibility | A2 | 9.0 (ACCEPT) | 9.0 (ACCEPT) | 35% |
| Cost Efficiency | A3 | 9.2 (ACCEPT) | 9.2 (ACCEPT) | 30% |

**Weighted Score**: (9.1 * 0.35) + (9.0 * 0.35) + (9.2 * 0.30) = 3.185 + 3.15 + 2.76 = **9.10**

### VERDICT: ACCEPT

**Consensus specification**: Change domain count constraint from `3..10` to `1..10` with adaptive sizing heuristics.

**Domain count heuristic**:
| Source Files | Domain Range | Rationale |
|-------------|-------------|-----------|
| 1-3 files | 1 domain | Single investigation scope sufficient |
| 4-10 files | 1-3 domains | Group by module or concern |
| 11-50 files | 3-7 domains | Standard auto-discovery |
| 51+ files | 5-10 domains | Full-scale investigation |

**Schema change**: Update `investigation-domains.json` schema `minItems` from 3 to 1.

**Downstream impact**: When domain count is 1, Phase 2 adversarial debate operates on a single finding set. The adversarial protocol should handle this gracefully (skip debate, pass through with full confidence score).

**Spec changes required**:
- FR-005: Change "3-10 dynamically discovered domains" to "1-10 dynamically discovered domains"
- Section 9 (Data Schemas): Update `minItems` from 3 to 1
- Section 7.0: Add domain count heuristic table
- Section 7.2: Add single-domain handling (skip adversarial debate when N=1)

---

## PROPOSAL-022: Specify scheduler behavior for MCP concurrency caps

| Dimension | Agent | Pre-Debate | Post-Debate | Weight |
|-----------|-------|------------|-------------|--------|
| Architectural Integrity | A1 | 6.8 (MODIFY) | 8.5 (MODIFY) | 35% |
| Runtime Feasibility | A2 | 5.5 (MODIFY) | 8.0 (MODIFY) | 35% |
| Cost Efficiency | A3 | 4.0 (REJECT) | 7.5 (MODIFY) | 30% |

**Weighted Score**: (8.5 * 0.35) + (8.0 * 0.35) + (7.5 * 0.30) = 2.975 + 2.80 + 2.25 = **8.03**

### VERDICT: MODIFY

**Modification**: Reject the proposed full scheduler (semaphores, exponential backoff, deterministic queue ordering). Replace with prompt-based MCP access budgets and reduced default concurrency.

**Implementation**:

1. **Reduce default `--concurrency`** from 10 to 5 (Section 5.3).

2. **Add per-phase MCP access budgets** to agent prompt templates (Section 8):

   | Phase | Agent Type | Serena Calls (max) | Context7 Calls (max) | Sequential Calls (max) |
   |-------|-----------|-------------------|---------------------|----------------------|
   | Phase 0 | Recon (Haiku) | 0 | 0 | 0 |
   | Phase 1 | Investigation | 3 per domain | 1 per domain | 0 |
   | Phase 3 | Fix Proposal | 2 per proposal | 2 per proposal | 0 |
   | Phase 4a | Implementation | 5 per fix | 2 per fix | 0 |
   | Phase 4b | Test Creation | 0 | 3 per fix | 0 |

3. **Add advisory note** to Section 11 (MCP Routing Table):
   > MCP access budgets are enforced via agent prompt instructions, not runtime semaphores. Agents exceeding their MCP call budget should fall back to native tool equivalents. The `--concurrency` flag limits parallel agents but does not directly limit MCP call volume; the per-agent budgets provide the secondary constraint.

**Spec changes required**:
- Section 5.3: Change `--concurrency` default from 10 to 5
- Section 8: Add MCP access budget table to agent specification templates
- Section 11: Add advisory note on enforcement mechanism
- Remove any references to runtime scheduler, semaphores, or queue ordering

---

## Verdict Summary

| Proposal | Verdict | Weighted Score | Pre-Debate Spread | Post-Debate Spread | Convergence |
|----------|---------|---------------|--------------------|--------------------|-------------|
| P-011 | **ACCEPT** | 8.66 | 2.7 (6.5-9.2) | 1.0 (8.2-9.2) | 1.0 |
| P-012 | **MODIFY** | 8.71 | 1.3 (7.5-8.8) | 0.3 (8.5-8.8) | 1.0 |
| P-013 | **ACCEPT** | 9.33 | 0.5 (9.0-9.5) | 0.5 (9.0-9.5) | 1.0 |
| P-014 | **ACCEPT** | 9.06 | 0.6 (8.7-9.3) | 0.6 (8.7-9.3) | 1.0 |
| P-015 | **ACCEPT** | 9.10 | 0.2 (9.0-9.2) | 0.2 (9.0-9.2) | 1.0 |
| P-022 | **MODIFY** | 8.03 | 2.8 (4.0-6.8) | 1.0 (7.5-8.5) | 1.0 |

**Group B aggregate**: 4 ACCEPT, 2 MODIFY, 0 REJECT

---

## Priority Ordering (by implementation urgency)

1. **P-013** (9.33) -- Model-tier fallback: Highest score, addresses unenforceable assumption that impacts every phase
2. **P-015** (9.10) -- Domain minimum rule: Prevents operational absurdity for common small-target use case
3. **P-014** (9.06) -- MCP tool contract: Immediate implementation blocker if not fixed
4. **P-012** (8.71) -- Token overflow policy: Required before any budget-conscious implementation
5. **P-011** (8.66) -- Orchestrator fallback: Important but only fires in error scenarios
6. **P-022** (8.03) -- MCP concurrency: Lowest urgency; prompt-based budgets are a soft control

---

## Cross-Cutting Observations

**Theme 1 -- Aspirational vs Enforceable**: Three proposals (P-012, P-013, P-022) share a common root cause: the spec states requirements that cannot be enforced in the current Claude Code runtime. Token caps are not monitorable, model tiers are not selectable, and MCP concurrency is not schedulable. The consistent resolution is to define aspirational targets with observability hooks and deterministic fallback behavior.

**Theme 2 -- Contract Completeness**: Two proposals (P-014, P-015) address incomplete contracts -- the tool allowlist does not match the fallback chain, and the domain count constraint does not accommodate all valid inputs. Both are straightforward spec corrections.

**Theme 3 -- Fallback Chain Integrity**: Proposals P-011 and P-014 both reveal that the spec's error handling paths reference capabilities that are either architecturally prohibited (orchestrator reading findings) or contractually unavailable (Edit/MultiEdit not in allowed-tools). Every fallback path must be verified against both the architectural invariants and the tool contract.
