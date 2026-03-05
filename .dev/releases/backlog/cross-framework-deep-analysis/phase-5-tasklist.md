# Phase 5 — Synthesis: Merged Strategy Document

**Goal**: Synthesize comparison results into a unified "best of both" strategy.
**Tier**: STANDARD (synthesis, no code changes)
**Phase Gate**: All 4 tasks complete; `merged-strategy.md` produced covering all 7 comparison areas with "rigor without bloat" constraints.

---

### T05.01 — Synthesis Framework & Merge Criteria Definition

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Before merging, establish explicit criteria for what "adopt patterns not mass" means in practice |
| **Effort** | S |
| **Risk** | Medium — vague criteria lead to scope creep in Phase 6 |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Merge criteria document with measurable constraints |
| **MCP Requirements** | Sequential (recommended for structured reasoning) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `TASKLIST_ROOT/artifacts/merge-criteria.md` |

**Steps**:
1. [READ] all 7 Phase 4 comparison artifacts — extract verdicts and merge compatibility assessments
2. [DEFINE] "adopt patterns not mass" operationally:
   - **Pattern**: A reusable control principle or decision algorithm (e.g., "presumption of falsehood" is a pattern)
   - **Mass**: Implementation-specific code, infrastructure, or framework coupling (e.g., 6000-line bash orchestrator is mass)
   - **Test**: Can the pattern be expressed in ≤50 lines of configuration/rules? If yes → pattern. If no → evaluate if simplification is possible.
3. [DEFINE] merge decision rubric for each component area:
   - **Adopt**: Take the pattern wholesale (possibly re-implemented in SC style)
   - **Adapt**: Modify the pattern to fit SC architecture
   - **Enhance**: Add the pattern to existing SC capability
   - **Discard**: Reject from both frameworks
4. [DEFINE] "rigor without bloat" constraints:
   - No new >500-line files
   - No new external dependencies unless justified
   - Every adopted pattern must have a measurable quality improvement hypothesis
   - Token cost per validation step must be estimated
5. [WRITE] `merge-criteria.md`

**Acceptance Criteria**:
1. "Pattern vs mass" distinction is operationally testable
2. Merge decision rubric has 4 categories with clear criteria
3. "Rigor without bloat" constraints are measurable, not aspirational

**Validation**:
1. Criteria can be applied to each Phase 4 comparison — test with one example
2. No criteria use subjective terms without measurable proxies
3. Token cost estimation method defined

**Dependencies**: T04.01, T04.02, T04.03, T04.04, T04.05

---

### T05.02 — Merged Strategy Document: Core Quality & Execution Models

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The merged strategy is the master document driving all Phase 6 refactoring plans |
| **Effort** | XL |
| **Risk** | High — synthesis quality determines Phase 6-7 value |
| **Tier** | STANDARD |
| **Confidence Bar** | [███████==-] 80% |
| **Requires Confirmation** | No |
| **Verification Method** | merged-strategy.md covers all 7 comparison areas with adopt/adapt/enhance/discard decisions |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required for verification), Sequential (recommended) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | Recommended — use adversarial debate agent for contested merges |
| **Deliverable IDs** | D-0040 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/merged-strategy.md` |

**Steps**:
1. [READ] `merge-criteria.md` and all 7 comparison artifacts
2. [SYNTHESIZE] for each comparison area, apply merge criteria:
   - **Quality Gates**: Merge SC audit gating formalism with LW PABLOV evidence chain → define merged quality model
   - **Task Execution**: Merge SC tier classification with LW self-contained task builder → define merged task model
   - **Orchestration**: Extract LW Worker/QA loop pattern for SC sprint CLI → define merged orchestration model
   - **Challenge System**: Enhance SC adversarial with LW 12-pattern anti-sycophancy → define merged challenge model
   - **Confidence/Validation**: Integrate LW presumption-of-falsehood into SC confidence checker → define merged validation model
   - **Agent Architecture**: Merge agent definition approaches → define merged agent model
   - **Parallel Execution**: Compare wave vs event-driven → define merged execution model
3. [QUERY] auggie MCP on both repos to verify that proposed merges are technically feasible (interfaces compatible, no architectural conflicts)
4. [WRITE] `merged-strategy.md` with sections for each area:
   - Current State (SC) | Current State (LW) | Merged Strategy | Adopt from LW | Keep from SC | Discard from Both | Rationale | Estimated Impact | Risk
5. [INCLUDE] "Rigor Without Bloat" section applying constraints from T05.01
6. [VERIFY] R-RULE-05: every merge decision passes "patterns not mass" test

**Acceptance Criteria**:
1. All 7 comparison areas have merge decisions
2. Each decision categorized as adopt/adapt/enhance/discard with rationale
3. "Rigor Without Bloat" section enforces measurable constraints
4. No merge decision proposes importing >500 lines of LW code
5. Every "adopt" decision has an estimated impact and risk assessment

**Validation**:
1. Traceability: every Phase 4 verdict referenced in merged strategy
2. R-RULE-05: grep for "adopt" entries — each must have "patterns not mass" assessment
3. No contradictions between merge decisions (e.g., adopting conflicting models)
4. Impact estimates are realistic (no "10x improvement" claims without evidence)

**Dependencies**: T05.01

---

### T05.03 — Rigor Without Bloat: Efficiency Constraints Definition

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The efficiency constraints prevent Phase 6 from producing plans that replicate llm-workflows bloat |
| **Effort** | M |
| **Risk** | Medium — too tight constraints block useful patterns; too loose allows bloat |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Constraints are specific, measurable, and applied to merged-strategy.md |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required for current state measurement) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | Section appended to `TASKLIST_ROOT/artifacts/merged-strategy.md` |

**Steps**:
1. [QUERY] auggie MCP (SC), query: "file sizes line counts module complexity current codebase metrics" — establish SC baseline
2. [QUERY] auggie MCP (LW), query: "file sizes line counts script complexity codebase metrics" — establish LW baseline
3. [DEFINE] efficiency constraints per category:
   - **File size**: No new file >500 lines; refactored files stay within 120% of current size
   - **Complexity**: No new module with cyclomatic complexity >15
   - **Dependencies**: No new external dependencies; internal dependency graph depth ≤4
   - **Token cost**: Each adopted validation pattern must estimate token cost per invocation
   - **Execution time**: No adopted pattern adds >5s to critical path
4. [APPLY] constraints to each merge decision in `merged-strategy.md` — flag any that violate
5. [ADJUST] merge decisions that violate constraints — simplify or split
6. [APPEND] constraints section to `merged-strategy.md`

**Acceptance Criteria**:
1. All 5 efficiency constraint categories defined with measurable thresholds
2. Every merge decision in `merged-strategy.md` assessed against constraints
3. Violations identified and resolved (simplified or marked as requiring Phase 7 review)

**Validation**:
1. Constraints have numeric thresholds, not just aspirational language
2. At least one merge decision was adjusted due to constraint violation (proves constraints are binding)
3. No constraint is so tight that it blocks all LW pattern adoption

**Dependencies**: T05.02

---

### T05.04 — Phase 5 Cross-Validation & Completeness Check

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Ensure merged strategy is complete, consistent, and ready to drive Phase 6 planning |
| **Effort** | S |
| **Risk** | Low |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Traceability check passes; no orphaned comparisons or missing merges |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `merged-strategy.md` — verify all 7 comparison areas covered
2. [CROSS-REFERENCE] against `component-map.md` — verify every mapped component pair has a merge decision
3. [CHECK] for internal contradictions — do any merge decisions conflict?
4. [CHECK] for completeness — are there components from Phase 1 that were dropped without explanation?
5. [CHECK] R-RULE-05: every adopt/adapt decision passes "patterns not mass" test
6. [FIX] any gaps or contradictions found
7. [UPDATE] phase checkpoint table

**Acceptance Criteria**:
1. All 7 comparison areas have merge decisions in merged-strategy.md
2. No component from Phase 1 map is missing without explanation
3. No contradictions between merge decisions
4. All efficiency constraints applied

**Validation**:
1. Component count in merged strategy ≥ component pairs in component-map.md
2. No "TBD" or "TODO" entries in merged strategy
3. Traceability: Phase 1 → Phase 2/3 → Phase 4 → Phase 5 chain intact for all components

**Dependencies**: T05.02, T05.03

---

## Phase 5 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| merge-criteria.md with operational definitions | T05.01 | ☐ |
| merged-strategy.md covers all 7 comparison areas | T05.02 | ☐ |
| Every merge decision categorized (adopt/adapt/enhance/discard) | T05.02 | ☐ |
| Efficiency constraints defined with measurable thresholds | T05.03 | ☐ |
| At least one constraint is binding (caused adjustment) | T05.03 | ☐ |
| No orphaned components or contradictions | T05.04 | ☐ |
| R-RULE-05 compliance (patterns not mass) | T05.02, T05.04 | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
