# Phase 6 — Refactoring Plan Generation

**Goal**: Convert merged strategy into concrete, actionable refactoring plans per SuperClaude component.
**Tier**: STRICT (refactoring plans that will drive code changes)
**Phase Gate**: All 5 tasks complete; per-component `refactor-*.md` and unified `refactor-master.md` produced with dependency graph.

---

### T06.01 — Refactoring Plan: Quality Infrastructure (Audit Gating + Task-Unified)

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Quality infrastructure changes must be planned first — they affect all other components |
| **Effort** | L |
| **Risk** | High — quality gate changes can break existing workflows if not carefully planned |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Plan items have specific file paths, acceptance criteria, and risk assessments; Sequential MCP validates reasoning |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required for STRICT tier) |
| **Fallback Allowed** | No — Sequential required per tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `TASKLIST_ROOT/artifacts/refactor-audit-gating.md`, `TASKLIST_ROOT/artifacts/refactor-task-unified.md` |

**Steps**:
1. [READ] merged strategy sections for quality gates and task execution
2. [QUERY] auggie MCP (SC), query: "audit gating current implementation files classes functions interfaces" — map current code structure
3. [QUERY] auggie MCP (SC), query: "task-unified current implementation tier classification enforcement" — map current code structure
4. [PLAN] for audit gating, produce refactoring items:
   - Each item: File Path | Change Description | Why (linked to merged strategy) | Priority (P0-P3) | Effort (XS-XL) | Dependencies | Acceptance Criteria | Risk Assessment
5. [PLAN] for task-unified, produce refactoring items with same structure
6. [VERIFY] R-RULE-05: each plan item passes "patterns not mass" — no item proposes >100 new lines without justification
7. [WRITE] `refactor-audit-gating.md` and `refactor-task-unified.md`
8. [VALIDATE] all file paths in plan exist in current repo

**Acceptance Criteria**:
1. Each plan item references a specific merge decision from Phase 5
2. All file paths verified to exist
3. Priority, effort, and risk assigned to every item
4. Backward compatibility considered — existing workflows documented
5. R-RULE-05: no plan item imports >100 lines of new code without justification

**Validation**:
1. Cross-reference file paths with `ls` — all exist
2. Every plan item traces back to merged-strategy.md
3. Risk assessments include rollback strategy
4. No plan item has effort "XL" without being split into sub-items

**Dependencies**: T05.02, T05.03

---

### T06.02 — Refactoring Plan: Execution Infrastructure (Sprint CLI + Parallel Execution)

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Execution infrastructure changes affect how all other refactoring plans get implemented |
| **Effort** | L |
| **Risk** | High — sprint CLI changes affect the tool used to execute this very sprint |
| **Tier** | STRICT |
| **Confidence Bar** | [███████==-] 80% |
| **Requires Confirmation** | No |
| **Verification Method** | Plan items validated against current sprint CLI codebase |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `TASKLIST_ROOT/artifacts/refactor-sprint-cli.md`, `TASKLIST_ROOT/artifacts/refactor-parallel-execution.md` |

**Steps**:
1. [READ] merged strategy sections for orchestration and parallel execution
2. [QUERY] auggie MCP (SC), query: "sprint CLI current files executor process models config tmux tui modules" — map current structure
3. [QUERY] auggie MCP (SC), query: "parallel execution current implementation wave checkpoint dependency" — map current structure
4. [PLAN] sprint CLI refactoring items — focus on adopting Worker/QA loop pattern without bash monolith
5. [PLAN] parallel execution refactoring items — integrate event-driven patterns if merged strategy recommends
6. [VERIFY] R-RULE-05 for each item
7. [WRITE] both refactoring plan artifacts
8. [VALIDATE] file paths exist; no self-referential changes (modifying sprint CLI while using it)

**Acceptance Criteria**:
1. Sprint CLI plan addresses adopted LW orchestration patterns
2. Parallel execution plan addresses adopted LW event-driven patterns
3. Self-referential risk acknowledged and mitigated
4. All file paths verified

**Validation**:
1. File path verification
2. R-RULE-05 compliance
3. Risk assessment addresses "modifying the tool while using it" scenario
4. Rollback strategy defined for each plan item

**Dependencies**: T05.02, T05.03

---

### T06.03 — Refactoring Plan: Validation & Challenge Systems (PM Agent + Adversarial + Cleanup-Audit)

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Validation and challenge systems are where most llm-workflows rigor patterns get adopted |
| **Effort** | XL |
| **Risk** | High — this is where "patterns not mass" constraint is most tested |
| **Tier** | STRICT |
| **Confidence Bar** | [███████==-] 80% |
| **Requires Confirmation** | No |
| **Verification Method** | Plan items pass R-RULE-05 check; token cost estimates present |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | Recommended — adversarial agent to challenge plan items |
| **Deliverable IDs** | D-0050 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/refactor-pm-agent.md`, `TASKLIST_ROOT/artifacts/refactor-adversarial.md`, `TASKLIST_ROOT/artifacts/refactor-cleanup-audit.md` |

**Steps**:
1. [READ] merged strategy sections for confidence/validation, challenge system, and cleanup-audit
2. [QUERY] auggie MCP (SC), query: "PM agent confidence.py self_check.py reflexion.py current implementation interfaces"
3. [QUERY] auggie MCP (SC), query: "adversarial protocol current implementation debate structure merge"
4. [QUERY] auggie MCP (SC), query: "cleanup-audit protocol current implementation subagents passes"
5. [PLAN] PM agent refactoring:
   - Integrate presumption-of-falsehood pattern into confidence checker
   - Add failure taxonomy from LW failure debugging
   - Add silent failure detection pattern
   - Each item with token cost estimate
6. [PLAN] adversarial refactoring:
   - Integrate anti-sycophancy patterns (enumerate which of 12 to adopt)
   - Add risk scoring to debate evaluation
7. [PLAN] cleanup-audit refactoring:
   - Adopt any applicable PABLOV validation patterns
8. [VERIFY] R-RULE-05 rigorously — these plans have highest temptation to import mass
9. [WRITE] all 3 refactoring plan artifacts

**Acceptance Criteria**:
1. PM agent plan integrates ≥3 LW patterns with specific file changes
2. Adversarial plan identifies which anti-sycophancy patterns to adopt (by number/name)
3. Every plan item has token cost estimate
4. R-RULE-05: no item proposes >100 new lines without justification
5. Each plan item has accept criteria and rollback strategy

**Validation**:
1. Token cost estimates are plausible (not "0 tokens" or "1M tokens")
2. Anti-sycophancy pattern selection justified (why these patterns, not others)
3. File paths verified
4. No plan item depends on importing LW bash scripts

**Dependencies**: T05.02, T05.03

---

### T06.04 — Refactoring Plan: Agent Architecture & Persona System

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Agent and persona changes affect how all other components are invoked and coordinated |
| **Effort** | M |
| **Risk** | Medium — agent changes are mostly additive, not breaking |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Plan items validated; agent definition format maintained |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (required) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `TASKLIST_ROOT/artifacts/refactor-agents.md`, `TASKLIST_ROOT/artifacts/refactor-persona-system.md` |

**Steps**:
1. [READ] merged strategy section for agent architecture
2. [QUERY] auggie MCP (SC), query: "agent definitions current list all agents markdown format"
3. [PLAN] agent refactoring:
   - Adopt LW role-based scoping principles where applicable
   - Identify redundant agents for consolidation
   - Define new agents if merged strategy requires
4. [PLAN] persona system adjustments if merged strategy requires
5. [VERIFY] R-RULE-05
6. [WRITE] both refactoring plan artifacts

**Acceptance Criteria**:
1. Agent plan identifies specific agents to modify, consolidate, or create
2. Persona system plan is minimal (only changes driven by merged strategy)
3. Agent definition format preserved

**Validation**:
1. Current agent count documented; proposed change count reasonable
2. No persona changes without direct merged strategy justification
3. File paths verified

**Dependencies**: T05.02, T05.03

---

### T06.05 — Master Refactoring Plan Assembly & Dependency Graph

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The master plan unifies all per-component plans into an executable dependency graph |
| **Effort** | L |
| **Risk** | Medium — dependency conflicts between component plans |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Master plan has no circular dependencies; all items from component plans included |
| **MCP Requirements** | Sequential (required for dependency analysis) |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0051 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/refactor-master.md` |

**Steps**:
1. [READ] all 7 per-component refactoring plan artifacts
2. [COMPILE] all plan items into unified list with cross-component dependencies
3. [ANALYZE] dependency graph:
   - Identify circular dependencies → resolve
   - Identify critical path → mark P0
   - Identify parallelizable items → mark for concurrent execution
4. [ORDER] items by: priority tier, then dependency order, then effort (smallest first)
5. [WRITE] `refactor-master.md` with:
   - Unified item list with IDs (RF-001, RF-002, ...)
   - Dependency graph (text-based)
   - Critical path highlighted
   - Estimated total effort per priority tier
   - Recommended implementation order
6. [VERIFY] no circular dependencies; all component plan items included; R-RULE-05 applied

**Acceptance Criteria**:
1. All items from 7 component plans present in master plan
2. Dependency graph has no circular dependencies
3. Critical path identified
4. Total effort estimated per priority tier
5. Implementation order defined

**Validation**:
1. Item count in master = sum of items across all component plans
2. No orphaned items (referenced by others but missing from master)
3. Priority distribution: P0 ≤ 20% of total items (if more, priorities are inflated)
4. Estimated total effort is plausible for a team executing with SuperClaude

**Dependencies**: T06.01, T06.02, T06.03, T06.04

---

## Phase 6 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| refactor-audit-gating.md complete | T06.01 | ☐ |
| refactor-task-unified.md complete | T06.01 | ☐ |
| refactor-sprint-cli.md complete | T06.02 | ☐ |
| refactor-parallel-execution.md complete | T06.02 | ☐ |
| refactor-pm-agent.md complete | T06.03 | ☐ |
| refactor-adversarial.md complete | T06.03 | ☐ |
| refactor-cleanup-audit.md complete | T06.03 | ☐ |
| refactor-agents.md complete | T06.04 | ☐ |
| refactor-persona-system.md complete | T06.04 | ☐ |
| refactor-master.md with dependency graph | T06.05 | ☐ |
| All plan items have file paths verified | All | ☐ |
| All plan items pass R-RULE-05 (patterns not mass) | All | ☐ |
| Token cost estimates present for validation patterns | T06.03 | ☐ |
| No circular dependencies in master plan | T06.05 | ☐ |
| Sequential MCP used for all tasks (STRICT tier) | All | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
