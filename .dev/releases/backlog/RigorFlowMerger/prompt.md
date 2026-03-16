# Cross-Framework Deep Analysis Sprint — Bootstrapping Prompt

> **Usage**: Paste this entire prompt into a fresh Claude Code session opened at `/config/workspace/SuperClaude_Framework`. It will generate a sprint-compatible tasklist that can be executed via `superclaude sprint run`.

---

## Context

You have access to two repositories:

1. **SuperClaude Framework** (`/config/workspace/IronClaudek`) — A Claude Code enhancement framework with skills, agents, personas, and CLI tooling. Key components to analyze:

   | Component | Location | Purpose |
   |-----------|----------|---------|


2. **llm-workflows** (`/config/workspace/llm-workflows`) — A battle-hardened QA pipeline (Rigorflow/PABLOV). Bloated, slow, expensive but incredibly rigorous and reliable. Key components:

   | Component | Location | Purpose |
   |-----------|----------|---------|
   | PABLOV method | `.gfdoc/rules/core/ib_agent_core.md` | Programmatic Artifact-Based LLM Output Validation |
   | Automated QA workflow | `.gfdoc/scripts/automated_qa_workflow.sh` | 6000-line bash orchestrator with Worker/QA loops |
   | Quality gates | `.gfdoc/rules/core/quality_gates.md` | Universal gate principles, severity levels, anti-sycophancy |
   | Anti-hallucination rules | `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | Presumption of falsehood, evidence requirements |
   | Anti-sycophancy system | `.gfdoc/rules/core/anti_sycophancy.md` + `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | 12-pattern risk scoring |
   | DNSP protocol | `.gfdoc/docs/guides/RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md` | Detect→Nudge→Synthesize→Proceed recovery |
   | Session management | `.gfdoc/scripts/session_message_counter.sh` + `rollover_context_functions.sh` | Proactive context rollover |
   | Input validation | `.gfdoc/scripts/input_validation.sh` | 3-layer defense-in-depth |
   | Task builder | `.claude/commands/rf/taskbuilder.md` | Self-contained checklist items with completion gates |
   | Pipeline orchestration | `.claude/commands/rf/pipeline.md` | Event-driven per-track parallel execution |
   | Agent definitions | `.claude/agents/rf-*.md` | Team lead, task builder, executor, researcher |
   | Failure debugging | `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | Automated failure classification |
   | Critical flaw analysis | `.dev/taskplanning/backlog/FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md` | Known multi-layer silent failure chains |
   | Post-milestone review | `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md` | Structured retrospective with forward propagation |

## Your Task

Generate a complete sprint tasklist (index + phase files) in the format used by SuperClaude's sprint CLI. Write the files to:

```
.dev/releases/current/cross-framework-deep-analysis/
├── tasklist-index.md
├── phase-1-tasklist.md
├── phase-2-tasklist.md
├── phase-3-tasklist.md
├── phase-4-tasklist.md
├── phase-5-tasklist.md
├── phase-6-tasklist.md
├── phase-7-tasklist.md
└── phase-8-tasklist.md
```

### Sprint Format Requirements

**Index file** must contain a metadata table and phase file references in this pattern:
```markdown
| Phase N Tasklist | `TASKLIST_ROOT/phase-N-tasklist.md` |
```

**Phase files** must use this task format:
```markdown
### T{NN}.{NN} — {Task Title}
**Roadmap Item IDs**: {cross-refs}
**Tier**: {STRICT|STANDARD|LIGHT|EXEMPT}
**Effort**: {XS|S|M|L|XL}
**Steps**: numbered [VERB] steps
**Acceptance Criteria**: numbered list
**Validation**: numbered list
**Dependencies**: {task IDs or "None"}
```

Task IDs follow `T{phase}.{sequence}` pattern (e.g., T01.01, T03.05). Monitor regex: `T\d{2}\.\d{2}`.

### Sprint Structure (8 Phases)

Design the sprint with these 8 phases. Each phase should have 3-6 tasks. Every task must use the auggie MCP codebase-retrieval tool (`mcp__auggie-mcp__codebase-retrieval`) as the primary search mechanism for both repos.

---

#### Phase 1: Component Inventory & Mapping
**Goal**: Build a complete component map of both frameworks.

Tasks should:
- Use `/sc:analyze` patterns to systematically inventory both repos
- Use auggie MCP to discover all components, their entry points, dependencies, and interfaces
- Map SuperClaude components to their llm-workflows counterparts (the "connection map")
- Produce a structured `component-map.md` artifact with: component name, file paths, interfaces exposed, dependencies, and cross-framework counterpart
- Cover: orchestration systems, quality gates, agent definitions, execution engines, evidence collection, error handling, configuration management

---

#### Phase 2: Strategy Extraction — SuperClaude Deep Dive
**Goal**: Extract the core strategies and design patterns from each SuperClaude component.

Tasks should:
- Use auggie MCP + `/sc:analyze --focus architecture` patterns for each major SuperClaude component
- Extract: design philosophy, execution model, quality enforcement mechanism, error handling strategy, extension points
- Document strengths AND weaknesses honestly (no sycophancy)
- Produce per-component `strategy-{component}.md` artifacts
- Components to cover: audit gating, task-unified, sprint CLI, adversarial pipeline, cleanup-audit, PM agent, parallel execution, persona system

---

#### Phase 3: Strategy Extraction — llm-workflows Deep Dive
**Goal**: Extract the core strategies and design patterns from each llm-workflows component.

Tasks should:
- Use auggie MCP + `/sc:analyze --focus architecture` patterns for each major llm-workflows component
- Extract: design philosophy, execution model, quality enforcement mechanism, error handling strategy, proven patterns
- Document what makes each component rigorous AND what makes it bloated/slow/expensive
- Produce per-component `strategy-{component}.md` artifacts
- Components to cover: PABLOV, automated QA workflow, quality gates, anti-hallucination, anti-sycophancy, DNSP, session management, input validation, pipeline orchestration, task builder, failure debugging

---

#### Phase 4: Cross-Framework Comparison & Debate
**Goal**: Systematically compare strategies between matched components and debate their merits.

Tasks should:
- Use `/sc:adversarial` patterns — for each matched component pair, structure a debate
- Use auggie MCP to pull specific implementation details as evidence for each position
- For each comparison: identify what SuperClaude does better, what llm-workflows does better, what's fundamentally different in approach, and what's compatible for merging
- Apply anti-sycophancy: challenge assumptions, require evidence for claims, flag hallucinated quality assessments
- Produce `comparison-{pair}.md` artifacts with: positions, evidence, verdict, and confidence
- Comparison pairs (minimum):
  1. Audit Gating vs Quality Gates + PABLOV
  2. task-unified tiers vs Pipeline orchestration + Task builder
  3. Sprint CLI vs Automated QA workflow
  4. Adversarial pipeline vs Anti-sycophancy system
  5. PM Agent (confidence/reflexion) vs Anti-hallucination rules + Failure debugging
  6. Agent definitions vs Agent definitions (rf-*)
  7. Parallel execution vs Event-driven per-track execution

---

#### Phase 5: Synthesis — Merged Strategy Document
**Goal**: Synthesize comparison results into a unified "best of both" strategy.

Tasks should:
- Use `/sc:adversarial --depth deep` patterns to merge comparison verdicts
- For each component area, define: the merged strategy, what to adopt from llm-workflows, what to keep from SuperClaude, what to discard from both, and the rationale
- Apply the "adopt patterns not implementation mass" principle — extract control patterns, reject bloated machinery
- Produce `merged-strategy.md` — the master document of merged approaches
- Include a "rigor without bloat" section defining the efficiency constraints

---

#### Phase 6: Refactoring Plan Generation
**Goal**: Convert merged strategy into concrete, actionable refactoring plans per SuperClaude component.

Tasks should:
- Use `/sc:roadmap` patterns to convert strategy into implementation roadmap
- For each SuperClaude component, produce a refactoring plan with:
  - Specific file changes (file path, what to change, why)
  - Priority tier (P0/P1/P2/P3)
  - Effort estimate (XS/S/M/L/XL)
  - Dependencies on other changes
  - Acceptance criteria
  - Risk assessment
- Produce per-component `refactor-{component}.md` artifacts
- Produce `refactor-master.md` — the unified cross-component plan with dependency graph

---

#### Phase 7: Validation & Adversarial Review
**Goal**: Validate the refactoring plan through adversarial challenge.

Tasks should:
- Use `/sc:adversarial` to debate the refactoring plan itself — is it complete? Is it over-engineered? Does it actually capture the llm-workflows rigor?
- Use auggie MCP to verify all file references in the plan actually exist and the proposed changes are compatible with current code
- Check for scope creep: does the plan stay within "patterns not mass"?
- Check for missing connections: did any cross-framework insight get dropped?
- Produce `validation-report.md` with pass/fail per plan item
- Produce `final-refactor-plan.md` — the validated, corrected master plan

---

#### Phase 8: Sprint Checkpoint & Artifact Assembly
**Goal**: Assemble all artifacts into a navigable deliverable and validate sprint completeness.

Tasks should:
- Build `artifact-index.md` linking all 30+ produced artifacts
- Verify traceability: every component in Phase 1 map → has strategy extraction → has comparison → appears in merged strategy → has refactoring plan
- Verify no orphaned artifacts or dead references
- Produce `sprint-summary.md` with: findings count, comparison verdicts, plan items by priority, estimated total effort, and recommended implementation order
- Final quality gate: all artifacts pass structural validation

---

### Deterministic Rules

Apply these rules in the generated tasklist:

- **R-RULE-01**: Every task that reads code must use `mcp__auggie-mcp__codebase-retrieval` as the primary search tool, with `directory_path` set to the appropriate repo root.
- **R-RULE-02**: Phase sequencing is strict: no phase begins until the prior phase's checkpoint passes.
- **R-RULE-03**: All comparison tasks must cite specific file:line evidence from both repos — no unsupported claims.
- **R-RULE-04**: Anti-sycophancy check: every "strength" claimed must have a corresponding "weakness" or trade-off documented.
- **R-RULE-05**: The "adopt patterns not mass" constraint must be verified in every Phase 6 refactoring plan item.
- **R-RULE-06**: Artifacts are written to `.dev/releases/current/cross-framework-deep-analysis/artifacts/`.
- **R-RULE-07**: Each phase ends with a checkpoint table verifying all acceptance criteria.

### Compliance Tiers

- **Phases 1-3**: EXEMPT (read-only analysis, no code changes)
- **Phase 4**: STANDARD (comparison and debate, produces artifacts but no code changes)
- **Phase 5**: STANDARD (synthesis, no code changes)
- **Phase 6**: STRICT (refactoring plans that will drive code changes)
- **Phase 7**: STRICT (validation of plans that will drive code changes)
- **Phase 8**: LIGHT (assembly and verification)

### MCP Requirements

Every task must specify MCP requirements. Recommended:
- **auggie MCP** (`mcp__auggie-mcp__codebase-retrieval`): Required for ALL code search tasks across both repos
- **Sequential**: Required for STRICT tier tasks, recommended for comparison/debate tasks
- **Serena**: Optional for symbol-level analysis when auggie results need deeper resolution
- **Context7**: Only for tasks referencing external library documentation

---

## Execution

After generating the tasklist files, the sprint can be executed with:

```bash
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --permission-flag "--dangerously-skip-permissions"
```

Or phase-by-phase:
```bash
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --start 1 --end 3 \
  --permission-flag "--dangerously-skip-permissions"
```

---

**Now generate the complete tasklist-index.md and all 8 phase files.**
