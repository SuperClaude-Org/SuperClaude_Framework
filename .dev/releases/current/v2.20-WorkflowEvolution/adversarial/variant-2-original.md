  ---                                                                                                    
  title: "v2.20 WorkflowEvolution — Boundary Fidelity Harnesses and Semantic Gate Promotion"             
  version: "1.0.0"                                                                                       
  status: draft                                                                                          
  feature_id: FR-052                                                                                     
  parent_feature: FR-050
  spec_type: refactoring
  complexity_score: 0.88
  complexity_class: high
  target_release: v2.20
  authors: [user, claude]
  created: 2026-03-09
  ---

  ## 1. Problem Statement

  The current SuperClaude workflow is strong at producing structurally valid artifacts, but materially
  weaker at proving that those artifacts faithfully preserve upstream intent or remain trustworthy across
   pipeline seams.

  The highest-confidence diagnostic finding is that the pipeline validates that work *looks right*, not
  that work *is right*. Structural checks, simulated agreement, and process conformance are treated as
  quality evidence, while semantic fidelity and boundary-truth verification remain under-enforced. This
  allows roadmap simplifications, schema thinning, dropped constraints, fabricated traceability, and
  execution-boundary failures to propagate through apparently healthy stages.

  The most urgent architectural issue is not lack of validation infrastructure, but misallocated rigor:
  - structural gates are blocking,
  - semantic conformance is lighter or advisory,
  - highest-risk seams are weakly defended,
  - retrospective learning arrives too late to constrain the next upstream artifact.

  This spec addresses that by introducing reusable boundary-fidelity harnesses at artifact handoffs and
  promoting semantic fidelity from advisory signal to blocking gate where downstream propagation risk is
  highest.

  ### 1.1 Evidence

  | Evidence | Source | Impact |
  |----------|--------|--------|
  | The pipeline “validates that work looks right, not that work is right”; structural confidence
  accumulates faster than independent evidence | Weight 1.0 — `forensic-foundation-validated.md` |
  Establishes the primary failure mode to design against |
  | Structural validation is systematically mistaken for semantic correctness; merge/test/task gates
  prove shape, not truth | Weight 1.0 — `forensic-foundation-validated.md` | Justifies adding semantic
  fidelity gates instead of only strengthening formatting checks |
  | Highest-risk failures cluster at seams: spec→prompt, extract→generate, adversarial→merge,
  roadmap→tasklist, tasklist→runner, runner→gates, retrospective→next spec | Weight 1.0 —
  `forensic-foundation-validated.md` | Defines where to inject new harnesses |
  | v2.19 case study found 29 spec→roadmap deviations, 15 roadmap→tasklist deviations, but only 1
  tasklist→implementation deviation | Weight 0.75 — `spec-fidelity-gap-analysis-merged.md` | Shows that
  most defects originate before implementation and should be caught earlier |
  | 75% of the implementation deviations traced back to roadmap generation, not execution | Weight 0.75 —
   `spec-fidelity-gap-analysis-merged.md` | Makes post-roadmap fidelity validation the highest-ROI first
  step |
  | Existing validation prompt compares roadmap against extraction, not raw spec; if extraction loses
  information, validation can still pass | Weight 0.75 — `spec-fidelity-gap-analysis-merged.md` |
  Demonstrates the need for upstream source-of-truth comparison |
  | Semantic checks are effectively non-blocking/advisory in protocol practice while structural checks
  block | Weight 0.75 — `spec-fidelity-gap-analysis-merged.md` | Supports explicit gate-tier promotion
  for semantic deviations |
  | Confidence signals are proxy measurements: panel score, convergence, tasklist quality, gate pass,
  pass rate | Weight 1.0 and 0.5 — `forensic-foundation-validated.md`, `05-workflow-meta-analysis.md` |
  Requires normalized deviation evidence rather than scalar confidence alone |

  ### 1.2 Scope Boundary

  **In scope**:
  - Add reusable fidelity-validation harnesses at key artifact boundaries
  - Compare artifacts against their immediate upstream source of truth
  - Promote semantic fidelity findings to blocking at selected boundaries
  - Normalize deviation reporting for roadmap and tasklist-era validators
  - Extend validate pipeline architecture without introducing new subprocess abstractions
  - Preserve current layered validation model: roadmap↔spec, tasklist↔roadmap, runner↔tasklist

  **Out of scope**:
  - Full end-to-end implementation-vs-spec audit across all source files
  - Replacing all prompt-based validation with deterministic parsing
  - Redesigning brainstorm/spec-panel/adversarial command families wholesale
  - Solving all executor↔subprocess runtime boundary issues in this release
  - Retrofitting historical artifacts or backfilling old release bundles

  ## 2. Solution Overview

  Introduce a **Boundary Fidelity Harness** architecture that validates each generated artifact against
  its immediate upstream source-of-truth artifact before downstream progression.

  This release adds a new semantic validation layer to the existing roadmap/validate subsystem, centered
  on:

  1. **Spec→Roadmap fidelity validation** as the first blocking semantic harness
  2. **Roadmap→Tasklist fidelity validation** as the next reusable harness contract
  3. **Normalized deviation report contracts** shared across harnesses
  4. **Severity-based blocking policy** that escalates HIGH-severity fidelity deviations into gate
  failures
  5. **Preservation of current layered architecture** by extending `validate_executor.py`,
  `validate_prompts.py`, `validate_gates.py`, and `models.py` rather than creating a separate execution
  stack

  The architecture remains hybrid:
  - **Prompt-based review** catches semantic drift, omission, reinterpretation, fabricated traceability,
  and layered mismatch
  - **Deterministic gates** enforce report shape, frontmatter, and minimum evidence presence
  - **Blocking policy** is driven by normalized deviations, not only frontmatter or formatting shape

  ### 2.1 Key Design Decisions

  | Decision | Choice | Alternatives Considered | Rationale |
  |----------|--------|------------------------|-----------|
  | Validation layering | Validate each artifact against its immediate upstream source | Compare all
  downstream artifacts directly to original spec | Immediate-upstream validation preserves layering and
  localizes blame accurately |
  | First implementation target | Add spec→roadmap fidelity harness first | Start with runner/output
  auditing or full end-to-end audit | Weighted evidence shows the roadmap boundary is the
  highest-leverage defect source |
  | Validation mechanism | Hybrid prompt-based semantic review + deterministic gate policy | Prompt-only
  or deterministic-only | Prompt-only is flexible but unstable; deterministic-only misses semantic drift
  |
  | Integration point | Extend current `roadmap validate` subsystem | Build separate “audit” command |
  Current code already has validation orchestration, gates, prompts, and report parsing |
  | Output schema | Normalized deviation rows with evidence quotes and severity | Freeform narrative
  findings | Structured findings support gating, dedupe, merge, and downstream revise loops |
  | Gate severity policy | HIGH fidelity deviations block; MEDIUM/LOW warn unless explicitly escalated |
  Advisory-only semantic review | Advisory semantics are a documented root cause of drift survival |
  | Scope of runtime fixes | Defer full runner-boundary overhaul | Include subprocess/live execution
  redesign in same release | The validated diagnostics support seam defense, but this release should
  focus on upstream artifact fidelity first |

  ### 2.2 Workflow / Data Flow

  ```text
  SPEC
    ↓
  [extract]
    ↓
  EXTRACTION
    ↓
  [generate A/B → diff → debate → score → merge]
    ↓
  ROADMAP
    ↓
  [NEW: spec_fidelity validate step]
      inputs: spec.md + roadmap.md + extraction.md (+ optional test-strategy.md)
      output: validate/spec-fidelity-report.md
      gate: SPEC_FIDELITY_GATE
      block on: HIGH deviations / tasklist_ready=false
    ↓
  [existing validate reflection/adversarial path, strengthened]
    ↓
  VALIDATED ROADMAP
    ↓
  [NEW: roadmap_tasklist_fidelity harness]
      inputs: roadmap.md + tasklist bundle
      output: tasklist-fidelity-report.md
      gate: TASKLIST_FIDELITY_GATE
    ↓
  TASKLIST
    ↓
  [future: output↔tasklist conformance harness]
    ↓
  RUNNER / EXECUTION

  3. Functional Requirements

  FR-052.1: Add blocking spec→roadmap fidelity validation

  Description: The roadmap validation subsystem shall support a fidelity-validation step that compares
  spec.md against the merged roadmap.md and emits a normalized deviation report.

  Acceptance Criteria:
  - The validate subsystem can read the raw spec file in addition to roadmap pipeline outputs
  - The fidelity prompt explicitly checks preservation of function signatures, data models, CLI options,
  gate criteria, FRs, NFRs, and constraints
  - Every deviation includes evidence quoted from both upstream and downstream artifacts
  - HIGH-severity fidelity deviations cause the fidelity gate to fail
  - A roadmap with only structural compliance but missing upstream requirements does not pass validation

  Dependencies: src/superclaude/cli/roadmap/validate_executor.py, validate_prompts.py, validate_gates.py,
   models.py, commands.py

  FR-052.2: Introduce a reusable boundary-fidelity report contract

  Description: All fidelity harnesses shall emit a common structured schema for deviations so they can be
   merged, summarized, gated, and consumed by downstream revise loops.

  Acceptance Criteria:
  - Every deviation row includes source_pair, severity, deviation, evidence, likely_impact, and
  recommended_correction
  - Reports include machine-parseable counts for blocking/warning/info severities
  - Reports distinguish between “no deviations found” and “validation incomplete/degraded”
  - The contract supports both single-agent reflection and multi-agent adversarial merge modes

  Dependencies: validate_prompts.py, validate_gates.py, validate_executor.py

  FR-052.3: Promote semantic fidelity from advisory to blocking at artifact boundaries

  Description: Semantic conformance at selected boundaries shall be gate-enforced rather than advisory
  when deviations threaten downstream correctness.

  Acceptance Criteria:
  - The spec→roadmap harness blocks downstream progression on HIGH-severity deviations
  - Conflict resolution in multi-agent validation escalates unresolved severity conflicts conservatively
  - Gate frontmatter includes explicit readiness fields derived from semantic findings, not only
  structural presence
  - Validation state written to .roadmap-state.json records semantic pass/fail/skipped status

  Dependencies: validate_gates.py, validate_executor.py, executor.py

  FR-052.4: Preserve layered validation architecture

  Description: The system shall validate roadmap against spec, tasklist against roadmap, and execution
  against tasklist rather than collapsing all layers into spec-vs-everything comparisons.

  Acceptance Criteria:
  - Prompt and report language identify the source boundary being validated
  - Tasklist validation logic, when added, consumes roadmap as upstream truth rather than raw spec
  - No new validation flow couples sprint execution directly to spec for blocking decisions
  - Design docs and CLI terminology consistently reflect boundary-local validation

  Dependencies: commands.py, validate_prompts.py, future tasklist validator entrypoint

  FR-052.5: Support degraded-but-explicit validation outcomes

  Description: Partial validation failure in multi-agent mode shall remain explicit and non-silent.

  Acceptance Criteria:
  - If one or more validation agents fail, the system writes a degraded report with validation_complete:
  false
  - Degraded reports cannot be mistaken for clean passes
  - Gate readiness reflects incompleteness conservatively
  - The report names failed and successful agents

  Dependencies: existing degraded-report handling in validate_executor.py

  4. Architecture

  4.1 New Files

  File: src/superclaude/cli/roadmap/validate_prompts.py (new prompt functions within existing file, no
  new
    module required)
  Purpose: Adds prompt builders for boundary-fidelity checks
  Dependencies: existing validate prompt patterns
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/validate_gates.py (new gate definitions within existing file)
  Purpose: Adds fidelity gate criteria and semantic readiness rules
  Dependencies: pipeline.models, roadmap semantic helpers
  ────────────────────────────────────────
  File: tests/roadmap/test_validate_fidelity.py
  Purpose: Unit/integration coverage for spec-fidelity prompt/gate/executor behavior
  Dependencies: roadmap validate modules
  ────────────────────────────────────────
  File: tests/roadmap/test_tasklist_fidelity_contract.py
  Purpose: Contract tests for reusable deviation schema and boundary naming
  Dependencies: validate prompts/gates

  4.2 Modified Files

  File: src/superclaude/cli/roadmap/models.py
  Change: Extend ValidateConfig with upstream artifact paths / boundary mode metadata
  Rationale: Validation currently only knows output_dir and agents; fidelity validation needs explicit
    upstream source awareness
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/commands.py
  Change: Extend roadmap validate CLI surface to accept raw spec path or infer it from state/output
    metadata
  Rationale: Current validate command only accepts output_dir; fidelity validation needs the source spec
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/validate_executor.py
  Change: Add step builders and orchestration path for spec-fidelity validation before/within current
    validation flow
  Rationale: This is the natural orchestration point and already handles single vs multi-agent validation
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/validate_gates.py
  Change: Define SPEC_FIDELITY_GATE and shared fidelity report criteria
  Rationale: Current gates validate reflection/merge structure but not fidelity semantics
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/validate_prompts.py
  Change: Add prompt builders for spec→roadmap and roadmap→tasklist fidelity checks; add normalized
  report
    contract instructions
  Rationale: Current reflect prompt validates roadmap/test-strategy/extraction, but not raw upstream
    fidelity
  ────────────────────────────────────────
  File: src/superclaude/cli/roadmap/executor.py
  Change: Pass spec context into auto-validation and persist fidelity validation state in
    .roadmap-state.json
  Rationale: Auto-invoked validation must be able to run the fidelity harness without user re-specifying
    inputs
  ────────────────────────────────────────
  File: src/superclaude/cli/pipeline/gates.py or existing gate consumers
  Change: No core gate engine rewrite required; ensure current gate engine can enforce new readiness
    semantics through existing criteria
  Rationale: Minimize blast radius by using existing gate engine

  4.3 Removed Files [CONDITIONAL]

  Not applicable.

  4.4 Module Dependency Graph

  commands.py
    └── models.py
    └── executor.py
         └── validate_executor.py
              ├── validate_prompts.py
              ├── validate_gates.py
              ├── pipeline.executor
              ├── pipeline.models
              └── pipeline.process

  executor.py
    └── .roadmap-state.json
    └── auto-invokes validate_executor.execute_validate()

  future tasklist validator
    └── reuses normalized fidelity prompt/gate/report contract

  4.5 Data Models [CONDITIONAL]

  @dataclass
  class ValidateConfig(PipelineConfig):
      output_dir: Path
      agents: list[AgentSpec]
      spec_file: Path | None = None
      boundary_mode: Literal[
          "roadmap_reflect",
          "spec_to_roadmap_fidelity",
          "roadmap_to_tasklist_fidelity",
      ] = "roadmap_reflect"


  @dataclass
  class FidelityDeviation:
      source_pair: str              # "spec→roadmap", "roadmap→tasklist"
      severity: Literal["HIGH", "MEDIUM", "LOW", "INFO"]
      deviation: str
      evidence: str
      likely_impact: str
      recommended_correction: str

  4.6 Implementation Order

  1. Extend ValidateConfig + CLI plumbing for upstream artifact awareness
     — required so validation can access raw spec without changing pipeline shape

  2. Add normalized fidelity prompt contract and SPEC_FIDELITY_GATE
     — establishes reusable interface and blocking policy
     2a. Add single-agent fidelity prompt/report path      — [parallel with 2b]
     2b. Add multi-agent merge semantics for fidelity      — [parallel with 2a]

  3. Integrate fidelity step into validate_executor and roadmap auto-validation
     — depends on 1, 2

  4. Add tests for report schema, blocking behavior, degraded mode, and state persistence
     — depends on 2, 3

  5. Define roadmap→tasklist harness contract and placeholder integration path
     — depends on validated spec→roadmap implementation, but can ship as reusable contract in same
  release

  5. Interface Contracts

  5.1 CLI Surface

  superclaude roadmap validate OUTPUT_DIR [--spec-file PATH] [--agents ...] [--model ...]
  superclaude roadmap run SPEC_FILE [--no-validate]

  ┌───────────────┬────────┬──────────────────────────┬──────────────────────────────────────────────┐
  │    Option     │  Type  │         Default          │                 Description                  │
  ├───────────────┼────────┼──────────────────────────┼──────────────────────────────────────────────┤
  │ --spec-file   │ path   │ inferred from state if   │ Source spec used for spec→roadmap fidelity   │
  │               │        │ available                │ validation                                   │
  ├───────────────┼────────┼──────────────────────────┼──────────────────────────────────────────────┤
  │ --agents      │ string │ existing behavior        │ Validation agents for single- or multi-agent │
  │               │        │                          │  mode                                        │
  ├───────────────┼────────┼──────────────────────────┼──────────────────────────────────────────────┤
  │ --model       │ string │ existing behavior        │ Override model for validation steps          │
  ├───────────────┼────────┼──────────────────────────┼──────────────────────────────────────────────┤
  │ --no-validate │ flag   │ false                    │ Skip post-pipeline validation including      │
  │               │        │                          │ fidelity harnesses                           │
  └───────────────┴────────┴──────────────────────────┴──────────────────────────────────────────────┘

  5.2 Gate Criteria

  Step: reflect
  Gate Tier: STANDARD
  Frontmatter: blocking_issues_count, warnings_count, tasklist_ready
  Min Lines: 20
  Semantic Checks: non-empty frontmatter values
  ────────────────────────────────────────
  Step: adversarial-merge
  Gate Tier: STRICT
  Frontmatter: existing fields + agent metadata
  Min Lines: 30
  Semantic Checks: agreement table present
  ────────────────────────────────────────
  Step: spec-fidelity
  Gate Tier: STRICT
  Frontmatter: blocking_issues_count, warnings_count, tasklist_ready, source_pair, validation_complete
  Min Lines: 30
  Semantic Checks: frontmatter values non-empty; deviation table present when counts > 0; source pair
    matches requested boundary; HIGH severity implies tasklist_ready: false
  ────────────────────────────────────────
  Step: tasklist-fidelity
  Gate Tier: STRICT
  Frontmatter: same normalized fidelity frontmatter
  Min Lines: 30
  Semantic Checks: same contract, boundary-specific checks

  5.3 Phase Contracts [CONDITIONAL]

  boundary_fidelity_contract:
    source_pair: "spec→roadmap | roadmap→tasklist | tasklist→execution"
    validation_complete: true|false
    blocking_issues_count: int
    warnings_count: int
    tasklist_ready: bool
    deviations:
      - source_pair: string
        severity: HIGH|MEDIUM|LOW|INFO
        deviation: string
        evidence: string
        likely_impact: string
        recommended_correction: string

  6. Non-Functional Requirements

  ┌───────────┬────────────────────┬─────────────────────────────────┬──────────────────────────────┐
  │    ID     │    Requirement     │             Target              │         Measurement          │
  ├───────────┼────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │           │ Minimal            │ Extend existing roadmap         │ No new executor/process      │
  │ NFR-052.1 │ architectural      │ validate subsystem without new  │ framework introduced         │
  │           │ disruption         │ subprocess abstraction layer    │                              │
  ├───────────┼────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │           │ Explicit           │ Multi-agent partial failures    │ Presence of                  │
  │ NFR-052.2 │ degraded-state     │ must remain unmistakably        │ validation_complete: false   │
  │           │ reporting          │ incomplete                      │ and degraded banner          │
  ├───────────┼────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │           │ Evidence-based     │ Every blocking fidelity         │ Tests assert evidence fields │
  │ NFR-052.3 │ findings           │ deviation cites both upstream   │  present                     │
  │           │                    │ and downstream evidence         │                              │
  ├───────────┼────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │           │ Layer-preserving   │ Boundary validators only        │ Prompt and report fixtures   │
  │ NFR-052.4 │ validation         │ compare immediate               │ reflect correct source pair  │
  │           │                    │ source-of-truth pairs           │                              │
  ├───────────┼────────────────────┼─────────────────────────────────┼──────────────────────────────┤
  │           │                    │ Added fidelity validation       │ Validate run adds            │
  │ NFR-052.5 │ Reasonable runtime │ should not materially exceed    │ approximately one extra step │
  │           │  overhead          │ one additional validation       │  for spec→roadmap path       │
  │           │                    │ subprocess per boundary in MVP  │                              │
  └───────────┴────────────────────┴─────────────────────────────────┴──────────────────────────────┘

  7. Risk Assessment

  ┌──────────────────────────────┬─────────────┬────────┬────────────────────────────────────────────┐
  │             Risk             │ Probability │ Impact │                 Mitigation                 │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ Prompt-based fidelity        │             │        │ Require paired evidence quotes,            │
  │ validator produces false     │ MED         │ MED    │ conservative wording, and severity         │
  │ positives                    │             │        │ normalization                              │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ Prompt-based fidelity        │             │        │ Keep design hybrid and add deterministic   │
  │ validator misses subtle      │ MED         │ HIGH   │ checks for obvious schema/field            │
  │ deviations                   │             │        │ preservation where feasible                │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ CLI surface becomes          │             │        │ Keep roadmap validate as the single        │
  │ confusing with multiple      │ MED         │ MED    │ entrypoint and infer defaults from state   │
  │ validation modes             │             │        │                                            │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ Blocking semantic gates      │             │        │ Block only on HIGH severity in initial     │
  │ increase friction on noisy   │ HIGH        │ MED    │ rollout; MEDIUM/LOW remain warnings        │
  │ outputs                      │             │        │                                            │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ State/inference of spec path │             │        │ Persist spec_file in .roadmap-state.json   │
  │  fails during resume flows   │ MED         │ MED    │ and allow explicit override via            │
  │                              │             │        │ --spec-file                                │
  ├──────────────────────────────┼─────────────┼────────┼────────────────────────────────────────────┤
  │ Scope creep into             │             │        │ Limit v2.20 to artifact-boundary           │
  │ runner/runtime verification  │ HIGH        │ HIGH   │ harnesses; defer runner seam redesign      │
  │ delays release               │             │        │                                            │
  └──────────────────────────────┴─────────────┴────────┴────────────────────────────────────────────┘

  8. Test Plan

  8.1 Unit Tests

  Test: test_build_spec_fidelity_prompt_includes_boundary_contract
  File: tests/roadmap/test_validate_fidelity.py
  Validates: Prompt includes source_pair, evidence requirements, and severity schema
  ────────────────────────────────────────
  Test: test_spec_fidelity_gate_requires_boundary_frontmatter
  File: tests/roadmap/test_validate_fidelity.py
  Validates: Gate rejects malformed fidelity reports
  ────────────────────────────────────────
  Test: test_high_severity_fidelity_report_blocks_readiness
  File: tests/roadmap/test_validate_fidelity.py
  Validates: HIGH deviation forces blocking outcome
  ────────────────────────────────────────
  Test: test_degraded_fidelity_report_marks_validation_incomplete
  File: tests/roadmap/test_validate_fidelity.py
  Validates: Partial multi-agent failure remains explicit
  ────────────────────────────────────────
  Test: test_validate_config_accepts_spec_file
  File: tests/roadmap/test_validate_unit.py
  Validates: Data model supports upstream source path
  ────────────────────────────────────────
  Test: test_validation_state_persists_fidelity_status
  File: tests/roadmap/test_validate_executor.py
  Validates: .roadmap-state.json records semantic validation result

  8.2 Integration Tests

  ┌────────────────────────────────────────────────────────────────────┬──────────────────────────────┐
  │                                Test                                │          Validates           │
  ├────────────────────────────────────────────────────────────────────┼──────────────────────────────┤
  │                                                                    │ Spec→roadmap validator       │
  │ test_roadmap_validate_reads_raw_spec_and_reports_deviation         │ catches omitted or renamed   │
  │                                                                    │ required fields              │
  ├────────────────────────────────────────────────────────────────────┼──────────────────────────────┤
  │                                                                    │ Auto-validation path invokes │
  │ test_roadmap_run_auto_validate_executes_fidelity_harness           │  fidelity validation after   │
  │                                                                    │ successful roadmap run       │
  ├────────────────────────────────────────────────────────────────────┼──────────────────────────────┤
  │                                                                    │ Conflicting severities are   │
  │ test_multi_agent_fidelity_merge_escalates_conflicts_conservatively │ merged without silent        │
  │                                                                    │ downgrade                    │
  ├────────────────────────────────────────────────────────────────────┼──────────────────────────────┤
  │ test_tasklist_fidelity_contract_is_reusable_for_future_boundary    │ Contract generalizes beyond  │
  │                                                                    │ spec→roadmap                 │
  └────────────────────────────────────────────────────────────────────┴──────────────────────────────┘

  8.3 Manual / E2E Tests [CONDITIONAL]

  ┌────────────────────────┬──────────────────────────────────┬──────────────────────────────────────┐
  │        Scenario        │              Steps               │           Expected Outcome           │
  ├────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
  │ Roadmap drops a        │ Run roadmap pipeline on a spec   │ Spec-fidelity report lists deviation │
  │ required config field  │ fixture with known required      │  with upstream/downstream evidence   │
  │ from spec              │ field; validate output           │ and blocks readiness                 │
  ├────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
  │ Roadmap structurally   │ Use roadmap fixture with all     │ Structural gates pass, fidelity gate │
  │ valid but semantically │ frontmatter/line checks passing  │  fails                               │
  │  simplified            │ but missing FR details           │                                      │
  ├────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
  │ One validation agent   │ Simulate partial failure during  │ Degraded report written with         │
  │ times out in           │ fidelity validation              │ validation_complete: false           │
  │ multi-agent mode       │                                  │                                      │
  └────────────────────────┴──────────────────────────────────┴──────────────────────────────────────┘

  9. Migration & Rollout

  - Breaking changes: No user-facing breaking change required if --spec-file remains optional and
  inferred from state when possible
  - Backwards compatibility: Existing roadmap validate OUTPUT_DIR should continue to work for legacy
  structural validation; fidelity mode activates when spec path is available or explicitly provided
  - Rollback plan: Disable fidelity step from auto-validation path while retaining codepaths; existing
  reflect/merge validation remains operational

  10. Downstream Inputs

  For sc:roadmap

  - Introduce milestone theme: Boundary fidelity before downstream progression
  - Add implementation milestone for:
    - config/plumbing
    - spec-fidelity prompt/gate
    - multi-agent merge support
    - state persistence
    - contract reuse for tasklist fidelity

  For sc:tasklist

  - Break work into:
    a. Extend config/CLI surface
    b. Implement fidelity prompt builders
    c. Implement fidelity gates
    d. Integrate executor flow
    e. Persist validation state
    f. Add unit/integration coverage
    g. Define roadmap→tasklist validator contract reuse

  11. Open Items

  ┌──────────┬──────────────────────────────────────────┬────────────────────────┬───────────────────┐
  │   Item   │                 Question                 │         Impact         │ Resolution Target │
  ├──────────┼──────────────────────────────────────────┼────────────────────────┼───────────────────┤
  │          │ Should spec→roadmap fidelity run before  │ Affects executor step  │ Before            │
  │ OI-052-1 │ or after existing reflect validation, or │ ordering and report    │ implementation    │
  │          │  replace part of it?                     │ composition            │                   │
  ├──────────┼──────────────────────────────────────────┼────────────────────────┼───────────────────┤
  │          │ Should MEDIUM severity become blocking   │ Affects gate           │                   │
  │ OI-052-2 │ for certain boundary classes such as     │ strictness and         │ Before gate       │
  │          │ fabricated traceability IDs?             │ false-positive         │ finalization      │
  │          │                                          │ tolerance              │                   │
  ├──────────┼──────────────────────────────────────────┼────────────────────────┼───────────────────┤
  │          │ Should the normalized deviation schema   │ Affects implementation │ During            │
  │ OI-052-3 │ be parsed into Python objects or remain  │  complexity and future │ implementation    │
  │          │ markdown+frontmatter only in v2.20?      │  reuse                 │ planning          │
  ├──────────┼──────────────────────────────────────────┼────────────────────────┼───────────────────┤
  │          │ Where should roadmap→tasklist validation │ Affects ownership and  │ Before follow-on  │
  │ OI-052-4 │  live: roadmap subsystem, tasklist       │ long-term architecture │ FR definition     │
  │          │ subsystem, or sprint preflight?          │                        │                   │
  └──────────┴──────────────────────────────────────────┴────────────────────────┴───────────────────┘

  ---
  Appendix A: Glossary

  ┌───────────────────┬──────────────────────────────────────────────────────────────────────────────┐
  │       Term        │                                  Definition                                  │
  ├───────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Boundary fidelity │ A repeatable validation wrapper that compares a downstream artifact against  │
  │  harness          │ its immediate upstream source of truth and emits normalized deviations       │
  ├───────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Structural        │ Checks that artifact shape, metadata, and formatting conform to expected     │
  │ validation        │ schema                                                                       │
  ├───────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Semantic fidelity │ Checks that meaning, requirements, constraints, and intent are preserved     │
  │                   │ across a boundary                                                            │
  ├───────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Proxy stacking    │ Treating local confidence signals as evidence of truth across multiple       │
  │                   │ stages                                                                       │
  ├───────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ Degraded          │ A validation outcome where one or more agents/steps fail, making the report  │
  │ validation        │ incomplete but explicitly marked                                             │
  └───────────────────┴──────────────────────────────────────────────────────────────────────────────┘

  Appendix B: Reference Documents

  Document: /config/workspace/SuperClaude_Framework/.dev/releases/current/v2.20-WorkflowEvolution/adversa
  rial-forensic-validation/forensic-foundation-validated.md
  Relevance: Highest-authority diagnostic source; establishes validated findings and seam map
  ────────────────────────────────────────
  Document: /config/workspace/SuperClaude_Framework/.dev/releases/current/v2.20-WorkflowEvolution/Archive
  /spec-fidelity-gap-analysis-merged.md
  Relevance: Provides concrete v2.19 boundary-deviation evidence and proposed harness strategy
  ────────────────────────────────────────
  Document: /config/workspace/SuperClaude_Framework/.dev/releases/current/v2.20-WorkflowEvolution/Archive
  /adversarial-forensic-foundation/adversarial/refactor-plan.md
  Relevance: Lower-weight structural framing for findings/theories taxonomy
  ────────────────────────────────────────
  Document: /config/workspace/SuperClaude_Framework/.dev/releases/current/v2.20-WorkflowEvolution/Archive
  /05-workflow-meta-analysis.md
  Relevance: Lower-weight but useful support for proxy-stacking and category-error framing
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/commands.py:128
  Relevance: Current CLI validation surface
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/executor.py:618
  Relevance: Auto-validation integration point after roadmap completion
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/models.py:65
  Relevance: Current ValidateConfig shape
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/validate_executor.py:365
  Relevance: Current validation orchestration entrypoint
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/validate_prompts.py:16
  Relevance: Existing reflection validation prompt
  ────────────────────────────────────────
  Document: src/superclaude/cli/roadmap/validate_gates.py:30
  Relevance: Existing validate gate definitions

  Key architecture anchors from current code:
  - CLI validate entrypoint: `src/superclaude/cli/roadmap/commands.py:154`
  - Auto-validation hook: `src/superclaude/cli/roadmap/executor.py:666`
  - Current validation orchestrator: `src/superclaude/cli/roadmap/validate_executor.py:365`
  - Current validation prompt surface: `src/superclaude/cli/roadmap/validate_prompts.py:16`
  - Current gate surface: `src/superclaude/cli/roadmap/validate_gates.py:30`
  - Current validate config shape: `src/superclaude/cli/roadmap/models.py:65`