---
spec_source: spec-cross-framework-deep-analysis.md
complexity_score: 0.85
primary_persona: architect
---

# 1. Executive summary

This roadmap delivers a gated, document-only analysis program for cross-framework comparison between IronClaude and llm-workflows, with a strong emphasis on architectural rigor, evidence integrity, and restartable execution.

## Architectural priorities

1. **Evidence-first execution**
   - Auggie MCP is the primary discovery and verification mechanism across both repositories.
   - Every meaningful claim must be traceable to verified file:line evidence.
   - Fallback tooling is permitted only as controlled degradation and must be explicitly annotated.

2. **Strict phase governance**
   - The program is sequential at the phase level with hard gate enforcement.
   - No downstream artifact is trusted unless upstream gate criteria pass.
   - Resume capability via `--start`/`--end` is a core reliability feature, not a convenience add-on.

3. **Rigor without scope inflation**
   - The roadmap must preserve the deterministic rule: **adopt patterns, not mass**.
   - The output is a decision-quality improvement plan, not an implementation sprint.
   - Any recommendation that implies framework cargo-culting or wholesale borrowing is a failure condition.

4. **Cross-artifact consistency**
   - The value of this effort depends on end-to-end traceability:
     `inventory → strategy → comparison → merged strategy → improvement plan → backlog`.
   - Architectural integrity requires that no component area becomes orphaned or contradictory across artifacts.

## Program outcome

If executed correctly, the sprint will produce:
- a verified component inventory,
- strategy analyses for both ecosystems,
- adversarial comparisons with evidence-backed verdicts,
- a unified merged strategy,
- actionable per-component improvement plans,
- a schema-valid backlog ready for `/sc:roadmap`,
- and consolidated validation/tracing artifacts.

---

# 2. Phased implementation plan with milestones

## Phase 0. Sprint setup and execution scaffolding

### Objectives
1. Establish execution scaffolding for the 8-phase sprint.
2. Define gate inputs/outputs and artifact destinations.
3. Confirm dependency availability before evidence work begins.

### Key actions
- Create or verify:
  - `tasklist-index.md`
  - `phase-{1..8}-tasklist.md`
- Confirm artifact target:
  - `.dev/releases/current/cross-framework-deep-analysis/artifacts/`
- Validate executor interface assumptions:
  - `superclaude sprint run <tasklist-index.md> [--start N] [--end N] [--permission-flag "..."]`
- Record dependency readiness:
  - Auggie MCP
  - IronClaude repo access
  - llm-workflows repo access
  - prompt/source documents
  - downstream command expectations (`/sc:roadmap`, `/sc:tasklist`)

### Milestone
- **M0**: Sprint scaffold is ready and phase contracts are defined.

### Exit criteria
- Phase tasklists exist or are confirmed.
- Artifact directory strategy is fixed.
- Dependency health is assessed and documented.

---

## Phase 1. Verified inventory and component mapping

### Objectives
1. Produce the authoritative current-state inventory for IronClaude’s quality-enforcement layer.
2. Verify llm-workflows file paths from `artifacts/prompt.md` without re-surveying the framework.
3. Create the cross-framework mapping baseline for all later phases.

### Key actions
1. Inventory all 8 IronClaude component groups:
   - roadmap pipeline
   - cleanup-audit CLI
   - sprint executor
   - PM agent
   - adversarial pipeline
   - task-unified tier system
   - quality agents
   - pipeline analysis subsystem
2. For each inventory entry, capture:
   - verified file paths
   - exposed interfaces
   - internal dependencies
   - extension points
3. Validate llm-workflows paths against `/config/workspace/llm-workflows`.
4. Produce:
   - `component-map.md`
   - `inventory-llm-workflows.md`
5. Annotate components with no counterpart as **IC-only**.

### Architectural recommendations
- Treat this phase as the canonical truth source.
- Do not allow downstream phases to “discover” new core scope casually; discoveries later should be flagged as inventory gaps, not silently absorbed.
- Resolve **OQ-002** here or immediately after this phase: whether pipeline-analysis remains one component group or is split for later comparison logic.

### Milestone
- **M1**: Verified dual-repo component map with cross-framework mappings completed.

### Exit criteria
- Meets SC-001.
- All file paths are verified or explicitly flagged stale.
- Cross-framework mapping count is at least 8.

### Timeline estimate
- **2-3 working sessions**

---

## Phase 2. IronClaude strategy extraction

### Objectives
1. Produce per-component strategy documents for all 8 IronClaude component groups.
2. Make current IronClaude design trade-offs explicit and evidence-backed.

### Key actions
- Produce 8 files:
  - `strategy-ic-*.md`
- For each component, document:
  - design philosophy
  - execution model
  - quality enforcement mechanism
  - error handling strategy
  - extension points
- Enforce anti-sycophancy:
  - every strength paired with a weakness/trade-off
- Attach file:line evidence to claims.

### Architectural recommendations
- Focus on **why the current design exists**, not just what code does.
- Prioritize system qualities:
  - maintainability
  - checkpoint reliability
  - extensibility boundaries
  - operational determinism
- Any “good” pattern without stated cost should fail review.

### Milestone
- **M2**: Full IronClaude strategy set completed with balanced trade-off analysis.

### Exit criteria
- Meets SC-002.
- Anti-sycophancy coverage is complete.
- Evidence is attached to each strategic claim.

### Timeline estimate
- **2-3 working sessions**

---

## Phase 3. llm-workflows strategy extraction

### Objectives
1. Produce strategy documents for all 11 llm-workflows components from the known prompt list.
2. Extract reusable patterns while explicitly documenting cost drivers.

### Key actions
- Produce 11 files:
  - `strategy-lw-*.md`
- For each component, document:
  - what is rigorous
  - what is bloated / slow / expensive
  - execution model
  - quality enforcement
  - extension points
- Restrict analysis to the prompt-defined component list plus path verification.
- Maintain evidence pairing and anti-sycophancy.

### Architectural recommendations
- This phase exists to identify **transferable discipline**, not implementation mass.
- Categorize findings into:
  1. directly adoptable patterns,
  2. conditionally adoptable patterns,
  3. patterns to reject.
- Costs should be explicit:
  - complexity overhead
  - operational drag
  - maintenance burden
  - token/runtime expense

### Milestone
- **M3**: llm-workflows strategic reference corpus completed.

### Exit criteria
- Meets SC-003.
- Each component includes both rigor and cost analysis.

### Timeline estimate
- **2-3 working sessions**

---

## Phase 4. Adversarial comparison and verdict generation

### Objectives
1. Compare the two ecosystems across 8 defined component pairs.
2. Produce verdicts that are specific, conditional, and architecturally useful.

### Key actions
- Produce 8 files:
  - `comparison-*.md`
- For each pair:
  - cite file:line evidence from both repositories
  - define debate positions
  - evaluate strengths and failure modes
  - issue a verdict with confidence
  - verify “adopt patterns not mass”
- Allow explicit verdict classes:
  - IronClaude stronger
  - llm-workflows stronger
  - split decision by context
  - no clear winner
  - discard both and define constraints for Phase 6

### Architectural recommendations
- Do not force convergence where architectures solve different problems.
- A “no clear winner” verdict is acceptable if conditions are explicit.
- Resolve **OQ-004** during this phase:
  - for “discard both,” Phase 6 should default to **IC-native improvement item required**, not placeholder omission.

### Milestone
- **M4**: Adversarial comparison set complete with defensible verdicts.

### Exit criteria
- Meets SC-004.
- Each comparison includes non-trivial verdict and evidence from both repos.

### Timeline estimate
- **2-3 working sessions**

---

## Phase 5. Merged strategy synthesis

### Objectives
1. Convert pairwise verdicts into one internally consistent cross-framework strategy.
2. Ensure architectural coherence across all component areas.

### Key actions
- Produce:
  - `merged-strategy.md`
- Include:
  - best-of-both strategy per component area
  - “rigor without bloat” section
  - explicit discard decisions and rationale
  - verification of “adopt patterns not mass”
- Run internal contradiction review across sections.

### Architectural recommendations
- This is the architectural center of gravity of the program.
- The merged strategy should define:
  1. what IronClaude keeps,
  2. what IronClaude strengthens,
  3. what IronClaude explicitly refuses to import.
- Organize synthesis around principles, not only components:
  - evidence integrity
  - deterministic gates
  - restartability
  - bounded complexity
  - scalable quality enforcement

### Milestone
- **M5**: Unified architectural strategy approved for planning use.

### Exit criteria
- Meets SC-005.
- No orphaned component areas.
- No internal contradictions.

### Timeline estimate
- **1-2 working sessions**

---

## Phase 6. Improvement planning and dependency graphing

### Objectives
1. Convert merged strategy into concrete, bounded improvement plans.
2. Produce a dependency-aware program view across all component groups.

### Key actions
- Produce:
  - 8 per-component improvement plans
  - `improve-master.md`
- Every improvement item must include:
  - specific file paths
  - change description
  - rationale
  - priority (`P0/P1/P2/P3`)
  - effort (`XS/S/M/L/XL`)
  - dependencies
  - acceptance criteria
  - risk assessment
- Distinguish:
  - strengthening existing code
  - adding new code
- Verify “patterns not mass” for each adopted pattern.

### Architectural recommendations
- Prioritize structural leverage:
  1. gate integrity
  2. evidence verification
  3. restartability/resume semantics
  4. traceability automation
  5. artifact schema reliability
- Use dependency graphing to isolate prerequisites from optional refinements.
- Keep backlog items implementation-ready but still analysis-scope only.

### Milestone
- **M6**: Full improvement portfolio and dependency graph completed.

### Exit criteria
- Meets SC-006.
- Every item is fully attributed and classified.

### Timeline estimate
- **2-3 working sessions**

---

## Phase 7. Adversarial validation and correction

### Objectives
1. Re-validate the entire improvement plan for completeness and rule compliance.
2. Correct failures before final backlog emission.

### Key actions
- Produce:
  - `validation-report.md`
  - `final-improve-plan.md`
- Validate:
  - file path existence
  - evidence coverage
  - anti-sycophancy coverage
  - patterns-not-mass compliance
  - completeness of cross-framework insights
  - absence of scope creep
- Re-open and correct failed items.

### Architectural recommendations
- Treat this as a formal architecture review gate, not a formatting pass.
- Nothing should pass if:
  - evidence is unverifiable,
  - copied mass appears,
  - cross-artifact lineage is broken,
  - or recommendations drift into implementation scope.

### Milestone
- **M7**: Validated and corrected final improvement plan approved.

### Exit criteria
- Meets SC-007, SC-012, SC-013, SC-014.
- All failed items are corrected or explicitly retired.

### Timeline estimate
- **1-2 working sessions**

---

## Phase 8. Consolidation, traceability, and downstream handoff

### Objectives
1. Produce the consolidated program outputs.
2. Ensure downstream usability for roadmap and tasklist tooling.

### Key actions
- Produce:
  - `artifact-index.md`
  - `rigor-assessment.md`
  - `improvement-backlog.md`
  - `sprint-summary.md`
- Validate:
  - backlog schema for `/sc:roadmap`
  - traceability from Phase 1 through backlog
  - zero orphaned artifacts
  - artifact count target
  - resume semantics and gate enforcement behavior
- Resolve **OQ-003** and **OQ-005** if still open.
  - Recommendation: add automated schema validation if low effort; otherwise document manual validation protocol and failure modes.

### Architectural recommendations
- This phase should produce executive clarity, not just files.
- `artifact-index.md` is a control-plane asset; it should make audit and future execution simple.
- `improvement-backlog.md` must be treated as an integration boundary artifact with strict schema discipline.

### Milestone
- **M8**: Final artifact package is complete, traceable, and consumable by downstream tooling.

### Exit criteria
- Meets SC-008 through SC-018.
- Backlog is accepted by `/sc:roadmap` without schema errors.

### Timeline estimate
- **1-2 working sessions**

---

# 3. Risk assessment and mitigation strategies

## High-priority risks

### 1. Auggie MCP unavailability for either repository
- **Related risks**: RISK-001, RISK-002
- **Impact**
  - Compromises evidence-backed discovery.
  - Threatens NFR-001 and NFR-003 directly.
- **Mitigation**
  1. Define fallback protocol in advance:
     - Serena `get_symbols_overview`
     - Grep/Glob
  2. Require annotation of every fallback-derived claim.
  3. Downgrade confidence in affected artifacts.
  4. Re-run validation when Auggie is restored if possible.
- **Architect recommendation**
  - Establish a binary rule for “unavailable” before execution:
    - timeout,
    - repeated failure threshold,
    - or incomplete result confidence threshold.
  - This resolves **OQ-008** and prevents inconsistent fallback behavior.

### 2. Stale llm-workflows file paths
- **Related risk**: RISK-003
- **Impact**
  - Invalidates downstream comparisons and evidence chain.
- **Mitigation**
  1. Make path verification a hard Phase 1 gate.
  2. Annotate stale entries explicitly.
  3. Prevent stale-path items from entering Phase 3 unmarked.
- **Architect recommendation**
  - Separate “path verified” from “strategy analyzable” status in inventory output.

### 3. Comparison verdicts are inconclusive
- **Related risk**: RISK-004
- **Impact**
  - Weakens merged strategy and planning specificity.
- **Mitigation**
  1. Permit “no clear winner” verdicts.
  2. Force condition-specific reasoning.
  3. Require explicit consequence for planning.
- **Architect recommendation**
  - Normalize a verdict taxonomy to avoid vague prose.

### 4. Phase 6 plan violates patterns-not-mass
- **Related risk**: RISK-005
- **Impact**
  - Creates roadmap bloat and undermines strategic intent.
- **Mitigation**
  1. Add explicit checklist at Phase 6 gate:
     - pattern extracted?
     - minimum viable adaptation?
     - no large-scale import implied?
  2. Re-test in Phase 7 adversarial review.
- **Architect recommendation**
  - Every adopted pattern should include a “why not full import” sentence.

### 5. Sprint crash or mid-phase interruption
- **Related risk**: RISK-006
- **Impact**
  - Loss of progress and rework.
- **Mitigation**
  1. Incremental artifact writing inside long phases.
  2. Gate-based restart via `--start`.
  3. Validate recovery from at least one known checkpoint.
- **Architect recommendation**
  - Make resume testing part of Phase 8 acceptance, not optional QA.

### 6. Incomplete IronClaude inventory due to codebase drift
- **Related risk**: RISK-007
- **Impact**
  - Produces downstream blind spots and incomplete backlog.
- **Mitigation**
  1. Broad inventory queries in Phase 1.
  2. Phase 7 cross-check against artifact references.
  3. Annotate late-discovered gaps.
- **Architect recommendation**
  - Treat inventory incompleteness as architecture debt and surface it in `rigor-assessment.md`.

## Cross-cutting risk controls

1. **Gate tables with pass/fail criteria**
   - Prevents subjective progression.
2. **Explicit invariant checks**
   - anti-sycophancy
   - evidence verification
   - patterns-not-mass
   - restartability
3. **Traceability enforcement**
   - Prevents orphaned outputs and reasoning gaps.
4. **Artifact isolation**
   - All outputs remain inside the designated artifacts tree.

---

# 4. Resource requirements and dependencies

## Core resources

### People / roles
1. **Architect lead**
   - Owns phase design, consistency, and strategy synthesis.
2. **Analysis operator**
   - Executes discovery, evidence gathering, and artifact drafting.
3. **Validation reviewer**
   - Performs adversarial and gate verification.
4. **Optional human reviewer**
   - Spot-checks comparison quality and verdict usefulness.

## Tooling dependencies

1. **Auggie MCP server**
   - Primary dependency for code retrieval and evidence validation.
2. **Serena MCP**
   - Fallback semantic retrieval.
3. **Grep/Glob**
   - Secondary fallback and coverage scans.
4. **`superclaude sprint run` executor**
   - Required for gated phase orchestration.
5. **`/sc:adversarial`**
   - Required for structured comparison phase.
6. **`/sc:roadmap`**
   - Downstream consumer of backlog schema.
7. **`/sc:tasklist`**
   - Downstream consumer of final improvement plan.

## Repository dependencies

1. **IronClaude**
   - `/config/workspace/IronClaude`
2. **llm-workflows**
   - `/config/workspace/llm-workflows`
3. **Reference inputs**
   - `artifacts/prompt.md`
   - extraction/spec documents
   - contextual spec references listed in dependency inventory

## Artifact dependencies

### Required control artifacts
- `tasklist-index.md`
- `phase-{1..8}-tasklist.md`

### Required outputs by chain
1. Inventory outputs
2. Strategy outputs
3. Comparison outputs
4. Merged strategy
5. Improvement plans
6. Validation outputs
7. Consolidated handoff outputs

## Recommended dependency handling strategy

1. **Preflight all mandatory dependencies before Phase 1**
2. **Record fallback state centrally**
3. **Prevent silent degradation**
4. **Validate downstream schema expectations before Phase 8 finalization**

---

# 5. Success criteria and validation approach

## Primary success criteria alignment

The program should validate explicitly against all 18 success criteria, organized into five validation domains.

## A. Coverage validation

1. Confirm all 8 IronClaude component groups are represented.
2. Confirm all 11 llm-workflows components are represented from prompt-based scope.
3. Confirm all required artifact classes are present.
4. Confirm final artifact count is at least 35.

### Validation methods
- artifact inventory scan
- component-to-artifact trace matrix
- file existence verification

## B. Evidence validation

1. Verify 100% of file:line citations.
2. Confirm evidence exists in both repos for all comparison artifacts.
3. Confirm stale paths are flagged, not hidden.

### Validation methods
- Auggie verification pass
- fallback annotation scan
- citation sampling plus full automated/structured review

## C. Rule compliance validation

1. Anti-sycophancy coverage is complete.
2. Patterns-not-mass verified for all relevant items.
3. No production code modifications occurred.
4. Artifacts only written to the permitted directory.

### Validation methods
- grep/checkpoint scans
- schema-style checklist on improvement items
- output path audit

## D. Flow and traceability validation

1. Every Phase 1 component maps through all later stages.
2. No orphaned artifacts remain in index.
3. Merged strategy covers all component areas.

### Validation methods
- end-to-end traceability matrix
- orphan detection review
- merged-strategy completeness audit

## E. Operability validation

1. Resume via `--start` works from an existing checkpoint.
2. Missing gate artifact blocks later phase execution.
3. `improvement-backlog.md` is accepted by `/sc:roadmap`.

### Validation methods
- targeted integration tests
- negative gate test
- schema ingestion validation

## Recommended validation cadence

1. **Per phase**
   - gate-specific pass/fail table
2. **At Phase 6**
   - dependency graph and planning completeness review
3. **At Phase 7**
   - adversarial re-validation of all major invariants
4. **At Phase 8**
   - downstream integration and traceability certification

---

# 6. Timeline estimates per phase

## Summary timeline

| Phase | Name | Estimated duration |
|---|---|---|
| 0 | Sprint setup and scaffolding | 0.5-1 working session |
| 1 | Verified inventory and mapping | 2-3 working sessions |
| 2 | IronClaude strategy extraction | 2-3 working sessions |
| 3 | llm-workflows strategy extraction | 2-3 working sessions |
| 4 | Adversarial comparison | 2-3 working sessions |
| 5 | Merged strategy synthesis | 1-2 working sessions |
| 6 | Improvement planning and dependency graph | 2-3 working sessions |
| 7 | Adversarial validation and correction | 1-2 working sessions |
| 8 | Consolidation and downstream handoff | 1-2 working sessions |

## Total program estimate
- **Core execution**: 14-22 working sessions
- **With contingency for tool degradation / path drift / open-question resolution**: 16-25 working sessions

## Schedule guidance

1. **Do not compress Phase 1**
   - Inventory defects cascade through the entire roadmap.
2. **Allow Phase 2 and Phase 3 coordination, but preserve gate logic**
   - If executor-level parallelism is unclear, sequence them conservatively.
3. **Protect Phase 7**
   - Validation time is what makes the backlog trustworthy.
4. **Reserve contingency for open questions**
   - Especially OQ-002, OQ-004, OQ-006, OQ-008.

---

# 7. Architect recommendations

## Immediate decisions to make before execution

1. **Define the operational threshold for Auggie “unavailable”**
   - Required to standardize fallback behavior.
2. **Decide whether pipeline-analysis remains one component or splits**
   - This affects strategy and comparison granularity.
3. **Define the mandatory handling for “discard both” verdicts**
   - Recommended: convert to IC-native improvement items.
4. **Clarify actual executor support for in-sprint parallelism**
   - Avoid designing concurrency the runner cannot honor.

## Priority recommendations

1. **P0: Protect evidence integrity**
   - Without evidence verification, the roadmap loses value.
2. **P0: Enforce gate determinism**
   - Sequential phase control is foundational to trust.
3. **P1: Preserve resume capability**
   - The prior crash history makes restartability essential.
4. **P1: Institutionalize traceability**
   - This converts analysis output into a reusable planning asset.
5. **P2: Automate schema checks where cheap**
   - Especially for `/sc:roadmap` backlog compatibility.

## Final architectural stance

This project should be run as a **high-discipline analysis pipeline**, not a loose research exercise. Its success depends less on document volume and more on four qualities:

1. **verified evidence**
2. **strict phase governance**
3. **bounded adoption strategy**
4. **end-to-end traceability**

If those four are maintained, the resulting roadmap and backlog will be credible, reusable, and safe to drive future implementation planning.
