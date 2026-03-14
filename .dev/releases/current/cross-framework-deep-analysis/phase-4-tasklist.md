# Phase 4 — Cross-Framework Comparison & Debate

**Goal**: Systematically compare strategies between matched components and debate their merits.
**Tier**: STANDARD (comparison and debate, produces artifacts but no code changes)
**Phase Gate**: All 5 tasks complete; 7 `comparison-*.md` artifacts produced with evidence from both repos.

---

### T04.01 — Comparison: Audit Gating vs Quality Gates + PABLOV

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The quality enforcement comparison is the most consequential — it determines the merged quality model |
| **Effort** | L |
| **Risk** | Medium — requires balanced analysis across very different approaches |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Artifact cites specific file:line evidence from both repos; verdict includes confidence level |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (recommended for structured debate) |
| **Fallback Allowed** | Sequential fallback to native reasoning |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0030 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/comparison-audit-gating-vs-quality-gates.md` |

**Steps**:
1. [READ] `strategy-sc-audit-gating.md` and `strategy-lw-pablov.md` and `strategy-lw-quality-gates.md`
2. [QUERY] auggie MCP with `directory_path=/config/workspace/SuperClaude_Framework`, query: "GateResult schema state transitions gate enforcement failure handling" — extract specific implementation evidence
3. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "PABLOV validation gate enforcement severity levels pass fail" — extract specific implementation evidence
4. [STRUCTURE] adversarial debate format:
   - **Position A** (SuperClaude advantage): State machine formalism, typed GateResult, rollout phases
   - **Position B** (llm-workflows advantage): Battle-tested validation, PABLOV evidence chain, anti-sycophancy integration
   - **Evidence**: Specific file:line citations for each claim (R-RULE-03)
5. [ANALYZE] compatibility: which elements can merge? Which are fundamentally incompatible?
6. [WRITE] `comparison-audit-gating-vs-quality-gates.md` with sections: Position A | Position B | Evidence Table | What SC Does Better | What LW Does Better | Fundamental Differences | Merge Compatibility | Verdict & Confidence
7. [VERIFY] R-RULE-03: all claims have file:line evidence; R-RULE-04: every strength paired with trade-off

**Acceptance Criteria**:
1. Both positions articulated with specific evidence
2. Evidence table has ≥5 entries per side with file:line citations
3. Verdict states clear confidence level (High/Medium/Low)
4. Merge compatibility section identifies specific integration points

**Validation**:
1. Grep for `file:line` or path citations — ≥10 total
2. Both "What SC Does Better" and "What LW Does Better" sections are non-empty
3. No unsupported claims ("obviously better", "clearly superior")
4. Anti-sycophancy check: verdict is not "both are great"

**Dependencies**: T02.01, T03.01

---

### T04.02 — Comparison: Task-Unified Tiers vs Pipeline Orchestration + Task Builder

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Task execution model comparison determines how work gets classified, routed, and validated |
| **Effort** | L |
| **Risk** | Medium |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Artifact with evidence from both repos and merge compatibility analysis |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (recommended) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0031 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/comparison-task-unified-vs-pipeline.md` |

**Steps**:
1. [READ] `strategy-sc-task-unified.md`, `strategy-lw-pipeline.md`, `strategy-lw-task-builder.md`
2. [QUERY] auggie MCP (SC), query: "task-unified tier classification algorithm keyword scoring context boosters compound phrases auto-detection"
3. [QUERY] auggie MCP (LW), query: "pipeline orchestration event-driven track coordination task builder checklist completion gates"
4. [STRUCTURE] adversarial debate:
   - **Position A** (SC): Declarative tier system, auto-classification, compliance enforcement
   - **Position B** (LW): Self-contained task definition, completion gates, event-driven coordination
5. [ANALYZE] merge compatibility: tier system + self-contained tasks? Auto-classification + completion gates?
6. [WRITE] comparison artifact with standard debate structure
7. [VERIFY] R-RULE-03 and R-RULE-04

**Acceptance Criteria**:
1. Tier classification vs event-driven model clearly contrasted
2. Self-contained task builder pattern evaluated for SC adoption
3. ≥5 evidence citations per side

**Validation**:
1. ≥10 file:line citations total
2. Merge compatibility section is specific, not vague
3. Anti-sycophancy: at least one "neither does this well" finding

**Dependencies**: T02.01, T03.02, T03.05

---

### T04.03 — Comparison: Sprint CLI vs Automated QA; Adversarial vs Anti-Sycophancy

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Two comparisons in one task — both are execution engine comparisons with direct counterparts |
| **Effort** | XL |
| **Risk** | Medium — two comparisons require careful separation |
| **Tier** | STANDARD |
| **Confidence Bar** | [███████==-] 80% |
| **Requires Confirmation** | No |
| **Verification Method** | Two artifacts, each with standard debate structure and evidence |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (recommended) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | Recommended — one sub-agent per comparison |
| **Deliverable IDs** | D-0032 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/comparison-sprint-vs-qa.md`, `TASKLIST_ROOT/artifacts/comparison-adversarial-vs-antisyc.md` |

**Steps**:
1. [READ] `strategy-sc-sprint-cli.md`, `strategy-lw-automated-qa.md`
2. [QUERY] auggie MCP (SC), query: "sprint CLI executor phase execution task monitoring process management TUI"
3. [QUERY] auggie MCP (LW), query: "automated QA workflow Worker QA loops state management orchestration batch"
4. [STRUCTURE] debate 1: Sprint CLI (Python, structured, TUI) vs Automated QA (bash, monolithic, battle-tested)
5. [WRITE] `comparison-sprint-vs-qa.md`
6. [READ] `strategy-sc-adversarial.md`, `strategy-lw-anti-sycophancy.md`
7. [QUERY] auggie MCP (SC), query: "adversarial debate merge pipeline positions evidence structured"
8. [QUERY] auggie MCP (LW), query: "anti-sycophancy 12 patterns risk scoring detection enforcement"
9. [STRUCTURE] debate 2: Adversarial pipeline (general debate) vs Anti-sycophancy (specific risk patterns)
10. [WRITE] `comparison-adversarial-vs-antisyc.md`
11. [VERIFY] R-RULE-03 and R-RULE-04 for both artifacts

**Acceptance Criteria**:
1. Sprint vs QA comparison addresses: language choice impact, monolithic vs modular, state management approaches
2. Adversarial vs anti-sycophancy comparison addresses: generality vs specificity, pattern coverage, enforcement mechanisms
3. Both artifacts have complete evidence tables

**Validation**:
1. ≥10 file:line citations per artifact
2. Sprint comparison doesn't dismiss bash unfairly or overpraise Python
3. Adversarial comparison identifies patterns from anti-sycophancy that could enhance the adversarial pipeline

**Dependencies**: T02.02, T03.02, T03.03

---

### T04.04 — Comparison: PM Agent vs Anti-Hallucination + Failure Debugging

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The confidence/validation/learning comparison determines how the merged system prevents and learns from errors |
| **Effort** | L |
| **Risk** | Medium |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Artifact with evidence-backed positions on confidence vs presumption-of-falsehood |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (recommended) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0033 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/comparison-pm-agent-vs-antihalluc.md` |

**Steps**:
1. [READ] `strategy-sc-pm-agent.md`, `strategy-lw-anti-hallucination.md`, `strategy-lw-failure-debugging.md`
2. [QUERY] auggie MCP (SC), query: "confidence checker threshold 90 70 pre-execution assessment self-check protocol reflexion error learning"
3. [QUERY] auggie MCP (LW), query: "presumption of falsehood evidence requirements verification before claims failure classification silent failure chains"
4. [STRUCTURE] adversarial debate:
   - **Position A** (SC): Probabilistic confidence model, 3-pattern system, cross-session learning
   - **Position B** (LW): Presumption of falsehood (binary), evidence requirements, failure taxonomy, silent failure detection
5. [ANALYZE] key question: is probabilistic confidence complementary to or conflicting with presumption of falsehood?
6. [WRITE] comparison artifact
7. [VERIFY] R-RULE-03 and R-RULE-04

**Acceptance Criteria**:
1. Confidence threshold model vs presumption of falsehood clearly contrasted
2. Reflexion pattern vs failure debugging compared
3. Compatibility analysis: can both models coexist?

**Validation**:
1. ≥10 file:line citations total
2. The "can both coexist" question answered with reasoning, not just "yes"
3. Silent failure detection patterns identified for potential SC adoption

**Dependencies**: T02.03, T03.03, T03.05

---

### T04.05 — Comparison: Agent Definitions & Parallel Execution Models

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Agent architecture and parallel execution are infrastructure decisions that affect all other components |
| **Effort** | L |
| **Risk** | Medium |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Two comparison artifacts with evidence |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Sequential (recommended) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0034 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/comparison-agents-vs-agents.md`, `TASKLIST_ROOT/artifacts/comparison-parallel-vs-eventdriven.md` |

**Steps**:
1. [READ] `strategy-sc-persona-system.md`, relevant Phase 3 agent strategy notes
2. [QUERY] auggie MCP (SC), query: "agent definitions audit-scanner audit-analyzer quality-engineer debate-orchestrator agent markdown specification"
3. [QUERY] auggie MCP (LW), query: "agent definitions rf-team-lead rf-task-builder rf-executor rf-researcher agent roles responsibilities"
4. [STRUCTURE] debate 1: SC agents (20+ specialists, persona-driven) vs LW agents (role-based, tightly scoped)
5. [WRITE] `comparison-agents-vs-agents.md`
6. [QUERY] auggie MCP (SC), query: "parallel execution wave checkpoint dependency analysis batch operations"
7. [QUERY] auggie MCP (LW), query: "event-driven per-track parallel execution track coordination synchronization"
8. [STRUCTURE] debate 2: Wave→Checkpoint→Wave vs Event-driven tracks
9. [WRITE] `comparison-parallel-vs-eventdriven.md`
10. [VERIFY] R-RULE-03 and R-RULE-04

**Acceptance Criteria**:
1. Agent comparison addresses: specialization model, scope discipline, composition patterns
2. Parallel execution comparison addresses: coordination model, failure handling, performance characteristics
3. Both artifacts have complete evidence tables

**Validation**:
1. ≥10 file:line citations per artifact
2. Agent comparison identifies redundancy in both systems
3. Parallel comparison doesn't just declare one winner — identifies context-dependent advantages

**Dependencies**: T02.04, T03.02, T03.04

---

## Phase 4 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| comparison-audit-gating-vs-quality-gates.md complete | T04.01 | ☐ |
| comparison-task-unified-vs-pipeline.md complete | T04.02 | ☐ |
| comparison-sprint-vs-qa.md complete | T04.03 | ☐ |
| comparison-adversarial-vs-antisyc.md complete | T04.03 | ☐ |
| comparison-pm-agent-vs-antihalluc.md complete | T04.04 | ☐ |
| comparison-agents-vs-agents.md complete | T04.05 | ☐ |
| comparison-parallel-vs-eventdriven.md complete | T04.05 | ☐ |
| All 7 comparisons have file:line evidence (R-RULE-03) | All | ☐ |
| All strengths paired with weaknesses (R-RULE-04) | All | ☐ |
| No sycophantic verdicts ("both are great") | All | ☐ |
| R-RULE-01 compliance (auggie MCP used) | All | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
