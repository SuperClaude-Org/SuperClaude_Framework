# Phase 3 — Strategy Extraction: llm-workflows Deep Dive

**Goal**: Extract the core strategies and design patterns from each llm-workflows component.
**Tier**: EXEMPT (read-only analysis)
**Phase Gate**: All 5 tasks complete; 11 `strategy-lw-*.md` artifacts produced, each documenting rigor AND bloat.

---

### T03.01 — Strategy Extraction: PABLOV & Quality Gates

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | PABLOV is the core validation philosophy; quality gates enforce it — these are the heart of llm-workflows rigor |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Both artifacts contain rigor assessment AND bloat/cost analysis |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0020 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/strategy-lw-pablov.md`, `TASKLIST_ROOT/artifacts/strategy-lw-quality-gates.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "PABLOV programmatic artifact-based LLM output validation core method evidence requirements validation model"
2. [ANALYZE] PABLOV for: validation philosophy, artifact types, evidence chain, enforcement mechanism, what makes it rigorous, what makes it expensive
3. [QUERY] auggie MCP, query: "quality gates universal gate principles severity levels anti-sycophancy gate enforcement pass fail criteria"
4. [ANALYZE] quality gates for: gate types, severity model, enforcement strictness, bypass mechanisms, integration with PABLOV
5. [WRITE] `strategy-lw-pablov.md` — Design Philosophy | Execution Model | Quality Enforcement | Error Handling | Proven Patterns | What Makes It Rigorous | What Makes It Bloated/Slow/Expensive
6. [WRITE] `strategy-lw-quality-gates.md` — same structure
7. [VERIFY] R-RULE-04: rigor claims paired with cost/bloat trade-offs

**Acceptance Criteria**:
1. PABLOV strategy captures the complete validation model with evidence chain
2. Quality gates strategy documents all severity levels and enforcement mechanisms
3. Both artifacts honestly assess the cost of rigor

**Validation**:
1. "What Makes It Bloated" section present and substantive (not a token paragraph)
2. All cited file paths exist in llm-workflows repo
3. No claims of "efficient" or "fast" without evidence

**Dependencies**: T01.04

---

### T03.02 — Strategy Extraction: Automated QA Workflow & Pipeline Orchestration

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The 6000-line bash orchestrator is the execution engine; pipeline orchestration is the parallel model — direct counterparts to Sprint CLI and parallel execution |
| **Effort** | L |
| **Risk** | Medium — 6000-line bash file requires careful analysis |
| **Tier** | EXEMPT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Both artifacts document execution flow and identify key patterns worth extracting |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes — auggie may struggle with 6000-line bash; supplement with targeted Read |
| **Sub-Agent Delegation** | Recommended — use explore agent for the large bash file |
| **Deliverable IDs** | D-0021 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/strategy-lw-automated-qa.md`, `TASKLIST_ROOT/artifacts/strategy-lw-pipeline.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "automated QA workflow bash orchestrator Worker QA loops batch processing 6000-line state management"
2. [ANALYZE] automated QA for: orchestration model, Worker/QA loop structure, state transitions, error recovery, what makes the 6000 lines necessary vs what's bloat
3. [QUERY] auggie MCP, query: "pipeline orchestration event-driven per-track parallel execution track coordination synchronization"
4. [ANALYZE] pipeline for: track model, event system, parallel execution strategy, coordination mechanism, comparison to SuperClaude's wave model
5. [WRITE] `strategy-lw-automated-qa.md` with standard structure including bloat analysis
6. [WRITE] `strategy-lw-pipeline.md` with standard structure
7. [VERIFY] R-RULE-04: identify which parts of the 6000 lines are essential vs removable

**Acceptance Criteria**:
1. Automated QA strategy maps the Worker/QA loop lifecycle
2. Pipeline strategy documents the event-driven model
3. Bloat analysis identifies specific categories of code that could be eliminated

**Validation**:
1. "What Makes It Bloated" is specific — names code sections, not just "it's big"
2. All cited line ranges exist in the actual file
3. Execution flow documented with enough detail for Phase 4 comparison

**Dependencies**: T01.04

---

### T03.03 — Strategy Extraction: Anti-Hallucination & Anti-Sycophancy Systems

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | These are llm-workflows' most battle-tested quality controls — the patterns most worth extracting for SuperClaude |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Both artifacts document specific patterns and enforcement mechanisms |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0022 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/strategy-lw-anti-hallucination.md`, `TASKLIST_ROOT/artifacts/strategy-lw-anti-sycophancy.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "anti-hallucination presumption of falsehood evidence requirements task completion rules verification before claims"
2. [ANALYZE] for: core principles, evidence chain requirements, verification workflow, false positive rate considerations
3. [QUERY] auggie MCP, query: "anti-sycophancy 12-pattern risk scoring risk patterns comprehensive detection challenge assumptions"
4. [ANALYZE] for: pattern taxonomy, scoring algorithm, detection triggers, enforcement actions, false positive handling
5. [QUERY] auggie MCP, query: "RISK_PATTERNS_COMPREHENSIVE risk scoring weights calibration thresholds"
6. [WRITE] `strategy-lw-anti-hallucination.md` — emphasize extractable patterns
7. [WRITE] `strategy-lw-anti-sycophancy.md` — document all 12 patterns if possible
8. [VERIFY] R-RULE-04 compliance

**Acceptance Criteria**:
1. Anti-hallucination strategy documents the "presumption of falsehood" model
2. Anti-sycophancy strategy enumerates the risk patterns with scoring details
3. Both identify which patterns are transferable to SuperClaude vs which are tightly coupled to llm-workflows

**Validation**:
1. Anti-sycophancy artifact lists specific patterns (target: 12)
2. "Transferable" vs "tightly coupled" assessment present
3. Evidence chain requirements documented with examples

**Dependencies**: T01.04

---

### T03.04 — Strategy Extraction: DNSP, Session Management & Input Validation

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | DNSP, session management, and input validation are operational resilience patterns — less glamorous but critical for reliability |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | All 3 artifacts produced with standard structure |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0023 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/strategy-lw-dnsp.md`, `TASKLIST_ROOT/artifacts/strategy-lw-session-mgmt.md`, `TASKLIST_ROOT/artifacts/strategy-lw-input-validation.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "DNSP detect nudge synthesize proceed recovery protocol batch state flow guide error recovery"
2. [ANALYZE] DNSP for: 4-phase recovery model, trigger conditions, nudge strategies, synthesis patterns, proceed criteria
3. [QUERY] auggie MCP, query: "session message counter rollover context functions proactive context management context window tracking"
4. [ANALYZE] session management for: context tracking, rollover triggers, state preservation, proactive vs reactive management
5. [QUERY] auggie MCP, query: "input validation 3-layer defense-in-depth validation pipeline sanitization"
6. [ANALYZE] input validation for: layer structure, validation rules, defense-in-depth model, error messages
7. [WRITE] all 3 strategy artifacts with standard structure
8. [VERIFY] R-RULE-04 compliance

**Acceptance Criteria**:
1. DNSP strategy documents all 4 phases with trigger conditions
2. Session management documents context tracking and rollover mechanism
3. Input validation documents all 3 layers

**Validation**:
1. DNSP artifact has 4 clearly labeled phases
2. Session management artifact addresses token/context budget concerns
3. Input validation artifact identifies the 3 defense layers

**Dependencies**: T01.04

---

### T03.05 — Strategy Extraction: Task Builder, Failure Debugging & Phase 3 QC

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Task builder and failure debugging complete the llm-workflows picture; QC ensures Phase 3 quality before Phase 4 |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | All Phase 3 artifacts pass structural validation |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0024 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/strategy-lw-task-builder.md`, `TASKLIST_ROOT/artifacts/strategy-lw-failure-debugging.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "task builder self-contained checklist items completion gates acceptance criteria structured task definition"
2. [ANALYZE] for: task definition model, checklist structure, completion gates, self-containment principle
3. [QUERY] auggie MCP, query: "failure debugging automated failure classification silent failure chains multi-layer failure detection critical flaw analysis"
4. [ANALYZE] for: failure taxonomy, classification algorithm, silent failure detection, multi-layer chain analysis
5. [WRITE] `strategy-lw-task-builder.md` with standard structure
6. [WRITE] `strategy-lw-failure-debugging.md` with standard structure
7. [READ] all 11 Phase 3 `strategy-lw-*.md` artifacts
8. [VERIFY] all have 7 required sections, ≥3 bloat/cost entries, no unsupported claims
9. [FIX] any artifacts that fail validation
10. [UPDATE] phase checkpoint table

**Acceptance Criteria**:
1. Task builder strategy captures the self-contained checklist model
2. Failure debugging strategy documents classification taxonomy and silent failure patterns
3. All 11 Phase 3 artifacts pass structural validation
4. No artifact missing bloat/cost analysis

**Validation**:
1. Count of Phase 3 artifacts = 11
2. All artifacts have "What Makes It Bloated" section
3. Post-milestone review pattern documented in failure debugging context
4. No "TODO" or placeholder content

**Dependencies**: T01.04, T03.01, T03.02, T03.03, T03.04

---

## Phase 3 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| strategy-lw-pablov.md complete | T03.01 | ☐ |
| strategy-lw-quality-gates.md complete | T03.01 | ☐ |
| strategy-lw-automated-qa.md complete | T03.02 | ☐ |
| strategy-lw-pipeline.md complete | T03.02 | ☐ |
| strategy-lw-anti-hallucination.md complete | T03.03 | ☐ |
| strategy-lw-anti-sycophancy.md complete | T03.03 | ☐ |
| strategy-lw-dnsp.md complete | T03.04 | ☐ |
| strategy-lw-session-mgmt.md complete | T03.04 | ☐ |
| strategy-lw-input-validation.md complete | T03.04 | ☐ |
| strategy-lw-task-builder.md complete | T03.05 | ☐ |
| strategy-lw-failure-debugging.md complete | T03.05 | ☐ |
| All artifacts have bloat/cost analysis (R-RULE-04) | T03.05 | ☐ |
| R-RULE-01 compliance (auggie MCP used) | T03.01–T03.05 | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
