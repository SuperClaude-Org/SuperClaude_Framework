# Phase 1 — Component Inventory & Mapping

**Goal**: Build a complete component map of both frameworks.
**Tier**: EXEMPT (read-only analysis)
**Phase Gate**: All 5 tasks complete; `component-map.md` produced with ≥14 component entries and cross-framework mappings.

---

### T01.01 — Establish Artifact Directory and Sprint Conventions

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | All downstream tasks depend on consistent artifact paths and naming conventions |
| **Effort** | XS |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [██████████] 100% |
| **Requires Confirmation** | No |
| **Verification Method** | Directory exists, README written |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `TASKLIST_ROOT/artifacts/README.md` |

**Steps**:
1. [CREATE] directory `TASKLIST_ROOT/artifacts/` if not exists
2. [WRITE] `artifacts/README.md` documenting naming conventions: `inventory-*.md`, `strategy-*.md`, `comparison-*.md`, `refactor-*.md`, `merged-strategy.md`, `validation-report.md`, `final-refactor-plan.md`, `artifact-index.md`, `sprint-summary.md`
3. [VERIFY] directory structure matches expected layout

**Acceptance Criteria**:
1. `TASKLIST_ROOT/artifacts/` directory exists
2. `README.md` documents all artifact naming conventions
3. Naming conventions align with Deliverable Registry in `tasklist-index.md`

**Validation**:
1. `ls -la TASKLIST_ROOT/artifacts/README.md` returns file
2. All deliverable IDs from index are referenced in README

**Dependencies**: None

---

### T01.02 — Repository Access Verification

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Confirm auggie MCP can reach both repos before investing in deep analysis |
| **Effort** | XS |
| **Risk** | Medium — MCP connectivity issues would block entire sprint |
| **Tier** | EXEMPT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Successful auggie MCP queries to both repos |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | No — auggie MCP is required per R-RULE-01 |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/SuperClaude_Framework`, query: "project entry points and main modules"
2. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "project entry points and main modules"
3. [VERIFY] both queries return meaningful results with file paths
4. [DOCUMENT] any access limitations or repo structure notes for downstream tasks

**Acceptance Criteria**:
1. Auggie MCP returns results for SuperClaude Framework repo
2. Auggie MCP returns results for llm-workflows repo
3. Both result sets include recognizable file paths from the known component locations

**Validation**:
1. SuperClaude query returns paths containing `src/superclaude/`
2. llm-workflows query returns paths containing `.gfdoc/`
3. No MCP errors or timeouts

**Dependencies**: None

---

### T01.03 — SuperClaude Framework Component Inventory

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Establishes the SuperClaude side of the component map — all downstream analysis depends on this |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Artifact contains all 9+ known components with file paths, interfaces, and dependencies |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required), Serena (optional for symbol resolution) |
| **Fallback Allowed** | Yes — Serena optional |
| **Sub-Agent Delegation** | Optional — explore agent for parallel directory scanning |
| **Deliverable IDs** | D-0001 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/inventory-superclaude.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/SuperClaude_Framework`, query: "unified audit gating state machine GateResult schema rollout phases" — document entry points, exports, dependencies
2. [QUERY] auggie MCP, query: "sc:task-unified tiered compliance STRICT STANDARD LIGHT EXEMPT classification" — document tier system, interfaces
3. [QUERY] auggie MCP, query: "sprint CLI executor process models tmux TUI orchestration" — document CLI architecture
4. [QUERY] auggie MCP, query: "adversarial debate merge pipeline structured comparison" — document pipeline stages
5. [QUERY] auggie MCP, query: "cleanup-audit multi-pass repository audit scanner analyzer comparator" — document pass structure
6. [QUERY] auggie MCP, query: "PM agent confidence checker self-check reflexion pattern" — document three core patterns
7. [QUERY] auggie MCP, query: "parallel execution wave checkpoint dependency analysis" — document execution model
8. [QUERY] auggie MCP, query: "persona system auto-activation decision framework specialist" — document persona architecture
9. [QUERY] auggie MCP, query: "agent definitions audit-scanner audit-analyzer quality-engineer debate-orchestrator" — document agent inventory
10. [COMPILE] all results into `inventory-superclaude.md` with structured table: Component | File Paths | Interfaces Exposed | Dependencies | Extension Points

**Acceptance Criteria**:
1. All 9 known components documented: audit gating, task-unified, sprint CLI, adversarial, cleanup-audit, PM agent, parallel execution, persona system, agent definitions
2. Each component entry includes: file paths (verified), interfaces exposed, internal dependencies, external dependencies
3. No component listed without verified file path evidence from auggie MCP

**Validation**:
1. Cross-reference file paths against `ls` output — all cited paths must exist
2. Component count ≥ 9
3. Every component has at least one interface documented (R-RULE-04: document limitations where interfaces are unclear)

**Dependencies**: T01.02

---

### T01.04 — llm-workflows Component Inventory

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Establishes the llm-workflows side of the component map |
| **Effort** | M |
| **Risk** | Low |
| **Tier** | EXEMPT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Artifact contains all 11+ known components with file paths, interfaces, and dependencies |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required) |
| **Fallback Allowed** | Yes — can supplement with Grep/Read |
| **Sub-Agent Delegation** | Optional — explore agent for parallel directory scanning |
| **Deliverable IDs** | D-0002 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/inventory-llm-workflows.md` |

**Steps**:
1. [QUERY] auggie MCP with `directory_path=/config/workspace/llm-workflows`, query: "PABLOV programmatic artifact-based LLM output validation method" — document validation model
2. [QUERY] auggie MCP, query: "automated QA workflow bash orchestrator Worker QA loops batch processing" — document orchestration architecture
3. [QUERY] auggie MCP, query: "quality gates universal gate principles severity levels gate enforcement" — document gate system
4. [QUERY] auggie MCP, query: "anti-hallucination presumption of falsehood evidence requirements task completion rules" — document validation rules
5. [QUERY] auggie MCP, query: "anti-sycophancy risk patterns risk scoring 12-pattern detection" — document risk system
6. [QUERY] auggie MCP, query: "DNSP detect nudge synthesize proceed recovery protocol batch state flow" — document recovery model
7. [QUERY] auggie MCP, query: "session message counter rollover context functions proactive context management" — document session system
8. [QUERY] auggie MCP, query: "input validation 3-layer defense-in-depth validation pipeline" — document validation layers
9. [QUERY] auggie MCP, query: "pipeline orchestration event-driven per-track parallel execution tracks" — document pipeline model
10. [QUERY] auggie MCP, query: "task builder self-contained checklist completion gates" — document task model
11. [QUERY] auggie MCP, query: "failure debugging automated failure classification silent failure chains" — document debugging system
12. [QUERY] auggie MCP, query: "agent definitions rf-team-lead rf-task-builder rf-executor rf-researcher" — document agent inventory
13. [COMPILE] all results into `inventory-llm-workflows.md` with structured table: Component | File Paths | Interfaces Exposed | Dependencies | Proven Patterns

**Acceptance Criteria**:
1. All 11 known components documented: PABLOV, automated QA, quality gates, anti-hallucination, anti-sycophancy, DNSP, session management, input validation, pipeline orchestration, task builder, failure debugging
2. Agent definitions inventoried separately
3. Each component entry includes: file paths (verified), interfaces, dependencies, and a "what makes it rigorous" note
4. No component listed without verified file path evidence

**Validation**:
1. Cross-reference file paths against `ls` output — all cited paths must exist
2. Component count ≥ 11
3. R-RULE-04: every "rigorous" claim includes a corresponding bloat/cost trade-off note

**Dependencies**: T01.02

---

### T01.05 — Cross-Framework Component Map Assembly

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The connection map is the foundation for all Phase 4 comparisons — incorrect mappings cascade downstream |
| **Effort** | S |
| **Risk** | Medium — some mappings may be imprecise (1:many or partial) |
| **Tier** | EXEMPT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | component-map.md contains all components from both inventories with explicit mappings or "no counterpart" annotations |
| **MCP Requirements** | `mcp__auggie-mcp__codebase-retrieval` (required for verification queries) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0003 |
| **Artifacts** | `TASKLIST_ROOT/artifacts/component-map.md` |

**Steps**:
1. [READ] `inventory-superclaude.md` and `inventory-llm-workflows.md`
2. [MAP] each SuperClaude component to its functional counterpart(s) in llm-workflows using this rubric: same domain? similar execution model? overlapping quality concerns?
3. [QUERY] auggie MCP on both repos to verify mappings — search for shared concepts, terminology, or patterns that confirm the connection
4. [DOCUMENT] mapping table with columns: SC Component | LW Counterpart(s) | Mapping Confidence (High/Medium/Low) | Mapping Rationale | Comparison Priority (P1-P3)
5. [ANNOTATE] components with no clear counterpart as "SC-only" or "LW-only" with explanation
6. [WRITE] `component-map.md` with: mapping table, methodology notes, confidence summary, list of planned Phase 4 comparison pairs

**Acceptance Criteria**:
1. Every component from both inventories appears in the map
2. At least 7 cross-framework mappings established (the 7 comparison pairs from Phase 4)
3. Each mapping includes confidence level and rationale
4. Components without counterparts explicitly annotated
5. Planned comparison pairs listed and justified

**Validation**:
1. Component count in map = sum of unique components from both inventories
2. All 7 Phase 4 comparison pairs can be derived from the map
3. No component orphaned without mapping or "no counterpart" annotation
4. R-RULE-04: mapping rationale includes limitations and caveats

**Dependencies**: T01.03, T01.04

---

## Phase 1 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| Artifact directory established | T01.01 | ☐ |
| Auggie MCP verified for both repos | T01.02 | ☐ |
| SuperClaude inventory ≥9 components | T01.03 | ☐ |
| llm-workflows inventory ≥11 components | T01.04 | ☐ |
| Component map with ≥7 cross-framework mappings | T01.05 | ☐ |
| All artifacts in `TASKLIST_ROOT/artifacts/` | All | ☐ |
| R-RULE-01 compliance (auggie MCP used) | T01.02–T01.05 | ☐ |
| R-RULE-07 compliance (this checkpoint exists) | — | ☐ |
