---
title: "IronClaude x llm-workflows: Cross-Framework Deep Analysis"
version: "1.0.0"
status: draft
feature_id: FR-XFDA-001
parent_feature: null
spec_type: infrastructure
complexity_score: 0.85
complexity_class: high
target_release: "3.0.0"
authors: [user, claude]
created: 2026-03-14
quality_scores:
  clarity: 8.5
  completeness: 8.0
  testability: 7.5
  consistency: 9.0
  overall: 8.25
---

## 1. Problem Statement

IronClaude has grown substantially since its last systematic quality assessment. The
`llm-workflows` framework (`/config/workspace/llm-workflows`) contains battle-hardened
rigor patterns — PABLOV validation, anti-sycophancy scoring, DNSP recovery,
anti-hallucination rules, structured quality gates — that were identified as high-value
sources of insight but have never been formally compared against IronClaude's actual
current implementation.

Without a structured cross-framework analysis, we cannot know:
- Which rigor gaps exist in IronClaude's quality enforcement layer
- Which llm-workflows patterns are worth adopting (without the bloat)
- Which IronClaude components already have equivalent or superior approaches
- What a prioritized improvement backlog should contain for v3.0

The original bootstrapping prompt for this analysis (`artifacts/prompt.md`) was written
when IronClaude was significantly smaller. The component inventory, comparison targets,
and phase structure need to reflect the current state of IronClaude, which now includes
a programmatic roadmap pipeline, cleanup-audit CLI, pipeline analysis subsystem, sprint
executor, and 11 portified skill protocols — none of which existed when the prompt was
written.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| Original bootstrapping prompt references stale repo paths and a component inventory covering ~20% of current codebase | `artifacts/prompt.md` | Analysis would produce incorrect component map |
| Sprint execution halted in Phase 1 with exit code -9 after 1m 56s — no artifacts produced | `execution-log.md` | Zero analysis output exists |
| v2.24 roadmap pipeline failed spec-fidelity gate due to rigor gaps (no deviation annotation, futile retry) | `.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md` | Known quality gaps exist; root causes partially addressed but no systematic comparison done |
| llm-workflows contains anti-sycophancy 12-pattern risk scoring, PABLOV artifact validation, DNSP recovery — none of these patterns are formally present in IronClaude | `artifacts/prompt.md` (llm-workflows component list) | Potential high-value rigor patterns unassessed |

### 1.2 Scope Boundary

**In scope**:
- IronClaude quality-enforcement components: roadmap pipeline (fidelity/remediate/certify),
  cleanup-audit CLI, sprint executor, PM agent, adversarial pipeline, task-unified tier
  system, agents (quality-engineer, root-cause-analyst, pm-agent, requirements-analyst),
  pipeline analysis subsystem (FMEA, guards, invariants, contracts)
- llm-workflows components: PABLOV, automated QA workflow, quality gates, anti-hallucination
  rules, anti-sycophancy system, DNSP protocol, session management, input validation,
  pipeline orchestration, task builder, failure debugging, agent definitions
- Cross-framework comparison, adversarial debate, merged strategy synthesis
- Prioritized improvement backlog with per-component refactoring plans
- Consolidated rigor assessment report

**Out of scope**:
- `review-translation` command and workflow
- IronClaude commands not related to quality enforcement (brainstorm, design, document,
  explain, estimate, git, index, load, save, etc.)
- Implementation of any improvements identified (those feed downstream roadmap items)
- llm-workflows implementation changes of any kind
- Updating llm-workflows component inventory (treated as stable reference)

---

## 2. Solution Overview

A structured sprint (executed by the IronClaude sprint CLI with phase gates) that
systematically inventories, compares, debates, and synthesizes insights across both
frameworks. The sprint produces two artifact sets: the original multi-document set
(strategy docs, comparison docs, master plan) and a consolidated rigor-assessment +
improvement-backlog pair.

The core principle throughout: **adopt patterns, not implementation mass**. llm-workflows
is rigorous but bloated and expensive. The goal is to extract the control patterns,
validation logic, and quality enforcement mechanisms — not to replicate 6000-line bash
orchestrators.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Execution model | Sprint CLI with phase gates | Interactive session, manual process | Sprint ensures reproducibility, phase gates prevent cascade from bad inventory, restartable |
| IronClaude component scope | Quality-enforcement layer only | Full codebase | Focus comparison where llm-workflows has direct relevance; non-quality commands have no meaningful counterparts in llm-workflows |
| llm-workflows scope | Unchanged from original prompt | Re-survey llm-workflows | No changes to llm-workflows since prompt was written; re-surveying wastes sprint budget |
| Artifact strategy | Multi-doc original + consolidated pair | Multi-doc only, consolidated only | Multi-doc preserves traceability; consolidated enables downstream roadmap generation |
| Anti-sycophancy rule | Every claimed strength requires documented weakness | Omit rule | Core integrity requirement — prevents analysis from drifting into advocacy |
| Constraint framing | "Adopt patterns not mass" as explicit R-RULE | Implicit guidance | Explicit rule enables checkpoint enforcement and prevents scope creep into llm-workflows adoption wholesale |

### 2.2 Workflow / Data Flow

```
Phase 1: Component Inventory & Mapping
  [Auggie: IronClaude quality-layer]  [Auggie: llm-workflows]
              |                                  |
  inventory-ironclaude.md          inventory-llm-workflows.md
              \                                 /
               +---------> component-map.md <---+
                                  |
Phase 2: Strategy Extraction -- IronClaude (per-component strategy docs)
Phase 3: Strategy Extraction -- llm-workflows (per-component strategy docs)
                    |                    |
              strategy-ic-*.md     strategy-lw-*.md
                          \             /
Phase 4: Cross-Framework Comparison & Debate (sc:adversarial per pair)
                    comparison-{pair}.md x 8
                              |
Phase 5: Synthesis -- Merged Strategy
                    merged-strategy.md
                              |
Phase 6: Improvement Plan Generation (per-component + master)
          improve-{component}.md x N  +  improve-master.md
                              |
Phase 7: Validation & Adversarial Review
          validation-report.md  +  final-improve-plan.md
                              |
Phase 8: Artifact Assembly & Consolidation
          artifact-index.md  +  rigor-assessment.md  +  improvement-backlog.md
```

---

## 3. Functional Requirements

### FR-XFDA-001.1: Updated IronClaude Component Inventory

**Description**: Phase 1 produces a complete, verified inventory of IronClaude's
quality-enforcement layer reflecting the current codebase state, using Auggie MCP as
the primary discovery mechanism.

**Acceptance Criteria**:
- [ ] All 8 IronClaude component groups inventoried: roadmap pipeline, cleanup-audit CLI,
      sprint executor, PM agent, adversarial pipeline, task-unified tier system, quality
      agents, pipeline analysis subsystem
- [ ] Each component entry includes: verified file paths, interfaces exposed, internal
      dependencies, extension points
- [ ] No component listed without Auggie MCP evidence (no hallucinated paths)
- [ ] Cross-framework component map produced with ≥8 IronClaude-to-llm-workflows mappings
- [ ] Components with no llm-workflows counterpart explicitly annotated as "IC-only"

**Dependencies**: Auggie MCP connectivity to `/config/workspace/IronClaude`

### FR-XFDA-001.2: llm-workflows Component Inventory (Stable Reference)

**Description**: Phase 1 uses the llm-workflows component list from the original
bootstrapping prompt as the stable reference. No re-survey needed. The inventory
artifact is produced from the known component list.

**Acceptance Criteria**:
- [ ] `inventory-llm-workflows.md` produced from known component list in `artifacts/prompt.md`
- [ ] Auggie MCP verification query run against `/config/workspace/llm-workflows` to confirm
      file paths are still valid
- [ ] Any path that no longer exists flagged and annotated

**Dependencies**: Auggie MCP connectivity to `/config/workspace/llm-workflows`

### FR-XFDA-001.3: Per-Component Strategy Extraction (Both Frameworks)

**Description**: Phases 2 and 3 extract the design philosophy, execution model, quality
enforcement mechanism, error handling strategy, and extension points for each component.
Every strength claim must include a corresponding weakness or trade-off (anti-sycophancy rule).

**Acceptance Criteria**:
- [ ] IronClaude: strategy docs for all 8 component groups
- [ ] llm-workflows: strategy docs for all 11 components from original prompt
- [ ] Every "strength" claim paired with a documented weakness or cost
- [ ] All claims backed by specific file:line evidence from Auggie MCP results
- [ ] llm-workflows strategy docs explicitly note what makes each component rigorous AND
      what makes it bloated/slow/expensive

**Dependencies**: FR-XFDA-001.1, FR-XFDA-001.2

### FR-XFDA-001.4: Cross-Framework Adversarial Comparison

**Description**: Phase 4 runs a structured adversarial debate for each matched component
pair, producing comparison artifacts with positions, evidence, verdict, and confidence.
Uses `/sc:adversarial` patterns.

**Acceptance Criteria**:
- [ ] Minimum 8 comparison pairs debated:
      1. Roadmap fidelity/certify/remediate gates vs PABLOV + quality gates
      2. Task-unified tier system vs pipeline orchestration + task builder
      3. Sprint CLI executor vs automated QA workflow
      4. Adversarial pipeline vs anti-sycophancy system
      5. PM agent (confidence/reflexion/self-check) vs anti-hallucination rules + failure debugging
      6. Agent definitions (quality-engineer, root-cause-analyst, etc.) vs rf-* agents
      7. Pipeline analysis subsystem (FMEA, guards, invariants) vs quality gates + PABLOV
      8. Cleanup-audit CLI vs automated QA workflow (structural audit dimension)
- [ ] Each comparison cites specific file:line evidence from both repos
- [ ] Each comparison produces a clear verdict: which approach is stronger, why, and under what conditions
- [ ] "Adopt patterns not mass" constraint verified in verdict for every pair

**Dependencies**: FR-XFDA-001.3

### FR-XFDA-001.5: Merged Strategy Synthesis

**Description**: Phase 5 synthesizes comparison verdicts into a unified "best of both"
strategy document. For each component area: what to adopt from llm-workflows, what to
keep from IronClaude, what to discard from both.

**Acceptance Criteria**:
- [ ] `merged-strategy.md` covers all component areas from Phase 4
- [ ] Explicit "rigor without bloat" section defining efficiency constraints
- [ ] "Adopt patterns not mass" principle applied and documented for each adopted pattern
- [ ] Discard decisions justified — not just implied
- [ ] Merged strategy is internally consistent (no contradictions between component sections)

**Dependencies**: FR-XFDA-001.4

### FR-XFDA-001.6: Prioritized Improvement Plan

**Description**: Phase 6 converts merged strategy into concrete, actionable improvement
plans per IronClaude component. Plans specify file changes, priority tier, effort,
dependencies, acceptance criteria, and risk. Produces per-component docs and a master plan.

**Acceptance Criteria**:
- [ ] Per-component improvement plans for all 8 IronClaude component groups
- [ ] Each improvement item includes: specific file path(s), what to change, why,
      priority (P0/P1/P2/P3), effort (XS/S/M/L/XL), dependencies, acceptance criteria
- [ ] `improve-master.md` contains dependency graph across all component plans
- [ ] "Adopt patterns not mass" verified for every item that adopts a llm-workflows pattern
- [ ] Risk assessment per item (probability × impact)
- [ ] Items that require new code distinguished from items that strengthen existing code

**Dependencies**: FR-XFDA-001.5

### FR-XFDA-001.7: Adversarial Validation of Improvement Plan

**Description**: Phase 7 adversarially challenges the improvement plan: is it complete?
Over-engineered? Does it actually capture the llm-workflows rigor patterns? Verifies
all file references exist and proposed changes are compatible with current code.

**Acceptance Criteria**:
- [ ] `validation-report.md` with pass/fail per improvement plan item
- [ ] All file paths in plan verified to exist via Auggie MCP
- [ ] Scope creep check: no item violates "patterns not mass" constraint
- [ ] Missing connection check: no cross-framework insight dropped between Phase 5 and 6
- [ ] `final-improve-plan.md` produced with all corrections applied

**Dependencies**: FR-XFDA-001.6

### FR-XFDA-001.8: Artifact Assembly and Consolidated Outputs

**Description**: Phase 8 assembles all artifacts into a navigable index, verifies
traceability end-to-end, and produces the two consolidated outputs: a rigor assessment
report and an improvement backlog suitable for feeding directly into a v3.0 roadmap.

**Acceptance Criteria**:
- [ ] `artifact-index.md` links all produced artifacts with one-line descriptions
- [ ] Traceability verified: every IronClaude component in Phase 1 map → strategy → comparison → merged strategy → improvement plan
- [ ] No orphaned artifacts or dead references
- [ ] `rigor-assessment.md`: consolidated narrative covering findings, verdict per component area, overall rigor gap assessment
- [ ] `improvement-backlog.md`: machine-readable improvement items with priority, effort, component, and rationale — formatted for `/sc:roadmap` consumption
- [ ] `sprint-summary.md`: findings count, comparison verdicts summary, plan items by priority, estimated total effort, recommended implementation order

**Dependencies**: FR-XFDA-001.7

---

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `spec-cross-framework-deep-analysis.md` | This spec — feeds roadmap generation | None |
| `tasklist-index.md` | Sprint phase index for CLI executor | This spec |
| `phase-{1-8}-tasklist.md` | Per-phase task definitions (8 files) | `tasklist-index.md` |
| `artifacts/inventory-ironclaude.md` | IronClaude quality-layer component inventory | Phase 1 |
| `artifacts/inventory-llm-workflows.md` | llm-workflows component inventory (from known list) | Phase 1 |
| `artifacts/component-map.md` | Cross-framework component mapping | Phase 1 |
| `artifacts/strategy-ic-{component}.md` | Per-component IronClaude strategy (8 files) | Phase 2 |
| `artifacts/strategy-lw-{component}.md` | Per-component llm-workflows strategy (11 files) | Phase 3 |
| `artifacts/comparison-{pair}.md` | Per-pair adversarial comparison (8 files) | Phase 4 |
| `artifacts/merged-strategy.md` | Unified best-of-both strategy | Phase 5 |
| `artifacts/improve-{component}.md` | Per-component improvement plan (8 files) | Phase 6 |
| `artifacts/improve-master.md` | Master improvement plan with dependency graph | Phase 6 |
| `artifacts/validation-report.md` | Adversarial validation of improvement plan | Phase 7 |
| `artifacts/final-improve-plan.md` | Validated, corrected master plan | Phase 7 |
| `artifacts/artifact-index.md` | Index of all produced artifacts | Phase 8 |
| `artifacts/rigor-assessment.md` | Consolidated narrative rigor assessment | Phase 8 |
| `artifacts/improvement-backlog.md` | Machine-readable improvement items for sc:roadmap | Phase 8 |
| `artifacts/sprint-summary.md` | Sprint summary with findings and estimates | Phase 8 |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `artifacts/prompt.md` | Superseded by this spec — no edits, retained for reference | Preserve original intent documentation |

### 4.3 Removed Files

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| Original `tasklist-index.md` and `phase-{1-8}-tasklist.md` (deleted in git) | Stale component inventory, wrong repo paths, never executed | Replaced by new tasklist generated from this spec |

### 4.4 Module Dependency Graph

```
spec-cross-framework-deep-analysis.md
    |
    +--> tasklist-index.md
            |
            +--> phase-1: inventory-ironclaude.md + inventory-llm-workflows.md + component-map.md
            |        |
            +--> phase-2: strategy-ic-*.md (depends on phase-1)
            +--> phase-3: strategy-lw-*.md (depends on phase-1, parallel with phase-2)
            |        |
            +--> phase-4: comparison-*.md (depends on phase-2 + phase-3)
            |        |
            +--> phase-5: merged-strategy.md (depends on phase-4)
            |        |
            +--> phase-6: improve-*.md + improve-master.md (depends on phase-5)
            |        |
            +--> phase-7: validation-report.md + final-improve-plan.md (depends on phase-6)
            |        |
            +--> phase-8: artifact-index.md + rigor-assessment.md +
                          improvement-backlog.md + sprint-summary.md
                          (depends on phase-7, consolidates all)

improvement-backlog.md
    |
    +--> /sc:roadmap (v3.0 roadmap generation, downstream)
```

### 4.5 Data Models

```
IronClaude Component Groups (scope-bounded):
  1. roadmap-pipeline       -- cli/roadmap/ (fidelity, remediate, certify, spec_patch, gates, executor)
  2. cleanup-audit-cli      -- cli/cleanup_audit/ (gates, anti-lazy, evidence-gate, executor, prompts)
  3. sprint-executor        -- cli/sprint/ (tmux, TUI, KPI, diagnostics, process, logging)
  4. pm-agent               -- pm_agent/ (confidence, self_check, reflexion, token_budget)
  5. adversarial-pipeline   -- .claude/commands/sc/adversarial.md + skills/sc-adversarial-protocol/
  6. task-unified           -- .claude/commands/sc/task-unified.md + skills/sc-task-unified-protocol/
  7. quality-agents         -- agents/ (quality-engineer, root-cause-analyst, pm-agent, requirements-analyst)
  8. pipeline-analysis      -- cli/pipeline/ (FMEA, guards, invariants, contracts, dataflow, conflict)

llm-workflows Components (stable reference from artifacts/prompt.md):
  1. pablov                 -- .gfdoc/rules/core/ib_agent_core.md
  2. automated-qa-workflow  -- .gfdoc/scripts/automated_qa_workflow.sh
  3. quality-gates          -- .gfdoc/rules/core/quality_gates.md
  4. anti-hallucination     -- .gfdoc/rules/core/anti_hallucination_task_completion_rules.md
  5. anti-sycophancy        -- .gfdoc/rules/core/anti_sycophancy.md + RISK_PATTERNS_COMPREHENSIVE.md
  6. dnsp-protocol          -- .gfdoc/docs/guides/RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md
  7. session-management     -- .gfdoc/scripts/session_message_counter.sh + rollover_context_functions.sh
  8. input-validation       -- .gfdoc/scripts/input_validation.sh
  9. pipeline-orchestration -- .claude/commands/rf/pipeline.md
  10. task-builder          -- .claude/commands/rf/taskbuilder.md
  11. agent-definitions     -- .claude/agents/rf-*.md

Comparison Pairs (Phase 4):
  pair-1: roadmap-pipeline          vs  pablov + quality-gates
  pair-2: task-unified              vs  pipeline-orchestration + task-builder
  pair-3: sprint-executor           vs  automated-qa-workflow
  pair-4: adversarial-pipeline      vs  anti-sycophancy
  pair-5: pm-agent                  vs  anti-hallucination + failure-debugging
  pair-6: quality-agents            vs  agent-definitions (rf-*)
  pair-7: pipeline-analysis         vs  quality-gates + pablov (structural dimension)
  pair-8: cleanup-audit-cli         vs  automated-qa-workflow (audit dimension)
```

### 4.6 Implementation Order

```
1. Phase 1: Component Inventory & Mapping       -- unblocked, sprint start
   [parallel: IronClaude inventory + llm-workflows inventory verification]
   --> component-map.md gates Phase 2+3

2. Phase 2: IronClaude Strategy Extraction      -- depends on phase-1
   Phase 3: llm-workflows Strategy Extraction   -- [parallel with Phase 2]

3. Phase 4: Comparison & Debate                 -- depends on phase-2 + phase-3
   [sequential per pair, auggie MCP evidence required for each]

4. Phase 5: Synthesis                           -- depends on phase-4

5. Phase 6: Improvement Plan Generation         -- depends on phase-5
   [per-component plans can be parallel; master plan sequential after all]

6. Phase 7: Adversarial Validation              -- depends on phase-6

7. Phase 8: Assembly & Consolidation            -- depends on phase-7
   [parallel: artifact-index + rigor-assessment + improvement-backlog + sprint-summary]
```

---

## 5. Interface Contracts

### 5.1 CLI Surface

```
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --permission-flag "--dangerously-skip-permissions"

# Phase-range execution:
superclaude sprint run \
  .dev/releases/current/cross-framework-deep-analysis/tasklist-index.md \
  --start 1 --end 3 \
  --permission-flag "--dangerously-skip-permissions"
```

### 5.2 Gate Criteria

| Phase | Gate | Min Artifacts | Semantic Checks |
|-------|------|---------------|-----------------|
| Phase 1 | component-map.md produced | 3 (2 inventories + map) | ≥8 cross-framework mappings; ≥8 IC components; ≥11 LW components |
| Phase 2 | all IC strategy docs produced | 8 strategy-ic-*.md | Each has strength + weakness section |
| Phase 3 | all LW strategy docs produced | 11 strategy-lw-*.md | Each has rigorous AND bloat/cost section |
| Phase 4 | all comparison docs produced | 8 comparison-*.md | Each has verdict + file:line evidence |
| Phase 5 | merged-strategy.md produced | 1 | Has "rigor without bloat" section; no component area orphaned |
| Phase 6 | all improvement plans produced | 9 (8 component + master) | Each item has P-tier, effort, file path; "patterns not mass" verified |
| Phase 7 | validation-report.md + final plan | 2 | Pass/fail per item; final plan corrects all failures |
| Phase 8 | consolidated outputs produced | 4 (index + assessment + backlog + summary) | improvement-backlog.md is sc:roadmap-compatible |

### 5.3 Phase Contracts

```yaml
phase_gate_contract:
  enforcement: strict_sequential
  rule: no_phase_starts_until_prior_checkpoint_passes
  checkpoint_format: table_with_pass_fail_per_criterion

improvement_backlog_schema:
  fields:
    - id: string          # IC-{component}-{seq}
    - component: string   # IronClaude component group
    - title: string
    - priority: enum      # P0, P1, P2, P3
    - effort: enum        # XS, S, M, L, XL
    - pattern_source: string   # which llm-workflows pattern, or "IC-native"
    - rationale: string
    - file_targets: list[string]
    - acceptance_criteria: list[string]
    - risk: string
    - patterns_not_mass_verified: bool
```

---

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-XFDA.1 | All code-reading tasks use Auggie MCP as primary tool | 100% compliance | R-RULE-01 checkpoint per phase |
| NFR-XFDA.2 | Anti-sycophancy: every strength has a paired weakness | 100% of strength claims | Checkpoint scan per phase |
| NFR-XFDA.3 | All file:line citations must be verifiable | 100% of citations | Auggie verification in Phase 7 |
| NFR-XFDA.4 | "Adopt patterns not mass" verified for every llm-workflows adoption | 100% of adoption items | Phase 6 and Phase 7 checkpoints |
| NFR-XFDA.5 | Sprint is restartable from any phase gate | Phase-range --start flag works | CLI executor handles resume |
| NFR-XFDA.6 | improvement-backlog.md is directly consumable by /sc:roadmap | Schema compliance | Phase 8 validation |

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Auggie MCP unavailable for IronClaude repo | Low | High | Fallback: Serena get_symbols_overview + Grep/Glob; note limitation in artifacts |
| Auggie MCP unavailable for llm-workflows repo | Low | High | Same fallback; llm-workflows inventory is partially known from prompt.md |
| llm-workflows file paths have changed since prompt.md was written | Medium | Medium | Phase 1 T01.02 verifies all LW paths; flag and annotate any missing |
| Comparison pairs produce inconclusive verdicts | Medium | Medium | Require explicit "no clear winner" verdict with rationale rather than forcing conclusion |
| Phase 6 improvement plans drift into implementation mass | Medium | High | Explicit "patterns not mass" R-RULE enforced at checkpoint; Phase 7 adversarial check |
| Sprint crashes mid-phase (as happened with original) | Low | Medium | Phase-gate checkpoints enable --start resume; artifacts written incrementally |
| IronClaude component inventory incomplete (fast-moving codebase) | Medium | Medium | Auggie MCP queries are broad; Phase 7 cross-checks all file references |

---

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| improvement-backlog schema compliance | Manual review in Phase 8 | All required fields present; enum values valid |
| Component map completeness | Phase 1 checkpoint | ≥8 IC components + ≥11 LW components + ≥8 mappings |
| Anti-sycophancy rule coverage | Per-phase checkpoint | Grep for "strength" sections — each has paired weakness |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| Sprint resume from Phase 3 | `--start 3` picks up correctly after Phase 1+2 artifacts exist |
| Traceability end-to-end | Every Phase 1 IC component appears in strategy → comparison → merged → improvement plan |
| sc:roadmap ingestion of improvement-backlog.md | Roadmap generation accepts backlog as input without schema errors |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Full sprint execution | Run sprint phases 1-8 sequentially | All 35+ artifacts produced; improvement-backlog.md generated; sprint-summary.md complete |
| Phase gate enforcement | Manually delete a required artifact; attempt to start next phase | Sprint halts with clear error citing missing gate artifact |
| Adversarial challenge quality | Human review of 2 comparison docs | Each has file:line evidence from both repos; verdict is non-trivial |

---

## 9. Migration & Rollout

- **Breaking changes**: None — this is an analysis sprint, no production code changes
- **Backwards compatibility**: N/A — produces new artifacts only
- **Rollback plan**: Sprint artifacts are all new files; deleting the artifacts directory restores prior state

---

## 10. Downstream Inputs

### For sc:roadmap
The `improvement-backlog.md` artifact is the primary downstream input. It contains
machine-readable improvement items with priority tiers (P0-P3), effort estimates, component
groupings, and rationale — formatted to feed directly into a v3.0 roadmap generation run.

The `rigor-assessment.md` provides narrative context for roadmap framing (problem statement,
findings summary, overall gap assessment).

### For sc:tasklist
The `final-improve-plan.md` (validated master improvement plan) provides the implementation
dependency graph that `sc:tasklist` needs to produce a correctly-sequenced execution plan
for v3.0 implementation work.

---

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| OI-1 | Do llm-workflows file paths in prompt.md still match current repo state? | Medium — Phase 1 verification will resolve | Phase 1 execution |
| OI-2 | Should the pipeline-analysis subsystem (FMEA, guards, invariants) be treated as one component group or split into sub-components for comparison? | Low — affects granularity of comparison artifacts | Before Phase 2 |
| OI-3 | Feature ID assignment for v3.0 planning — does FR-XFDA-001 need to be registered in a FR registry? | Low — administrative | Before roadmap generation |

---

## 12. Brainstorm Gap Analysis

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-1 | llm-workflows path validity not pre-verified — could waste Phase 1 effort if paths are stale | Medium | Section 3 (FR-XFDA-001.2) | QA |
| GAP-2 | No explicit handling if a comparison pair produces a "discard both" verdict — what feeds Phase 6? | Low | Section 3 (FR-XFDA-001.6) | Architect |
| GAP-3 | improvement-backlog.md schema defined in spec but not validated by any existing test tooling | Medium | Section 5.3, Section 8 | QA |

Phase 1 T01.02 (llm-workflows path verification) directly mitigates GAP-1. GAP-2 is low-risk
because "discard both" is a valid Phase 5 outcome that feeds Phase 6 as "no adoption from
either; document why." GAP-3 is accepted risk — schema is simple enough for manual review
in Phase 8.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| PABLOV | Programmatic Artifact-Based LLM Output Validation — llm-workflows' core validation method |
| DNSP | Detect-Nudge-Synthesize-Proceed — llm-workflows' batch state recovery protocol |
| "Patterns not mass" | Core constraint: adopt the control logic and validation patterns from llm-workflows, not the bash/shell implementation machinery |
| IC | IronClaude (this framework) |
| LW | llm-workflows (the reference framework) |
| Phase gate | A checkpoint table at the end of each sprint phase; sprint halts if any criterion fails |
| R-RULE | Deterministic rule enforced at all sprint phase checkpoints |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `.dev/releases/current/cross-framework-deep-analysis/artifacts/prompt.md` | Original bootstrapping prompt — defines llm-workflows component list (stable reference) |
| `.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md` | Evidence of known IronClaude rigor gaps (v2.24 fidelity failure root causes) |
| `src/superclaude/examples/release-spec-template.md` | Spec template this document was written against |
