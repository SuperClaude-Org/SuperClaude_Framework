<context - prompt used to generate>
Prompt 1: /sc:spec-panel — Full Expert Review of
  sc:cli-portify

  /sc:spec-panel @src/superclaude/skills/sc-cli-portify/SKILL.md
   \
    --mode critique \
    --focus requirements,architecture,correctness \
    --iterations 2 \
    --format detailed

  Full prompt to paste after command invocation:

  Specification under review: sc:cli-portify (Workflow-to-CLI
  Pipeline Compiler)

  Include all ref files in scope:
  - @src/superclaude/skills/sc-cli-portify/refs/analysis-protoco
  l.md
  - @src/superclaude/skills/sc-cli-portify/refs/pipeline-spec.md
  -
  @src/superclaude/skills/sc-cli-portify/refs/code-templates.md

  ## Review Context (Prior Analysis Findings)

  A comparative analysis against sc:tasklist-protocol identified
   these issues:

  ### Structural Convention Violations
  1. **Missing command entry point**: Every other skill follows
  the pattern
     `commands/<name>.md` (thin) →
  `skills/sc-<name>-protocol/SKILL.md` (full).
     cli-portify has NO command .md entry point and the skill
  directory is named
     `sc-cli-portify/` not `sc-cli-portify-protocol/`. This
  breaks discoverability,
     the `superclaude install` distribution pipeline, and slash
  command invocation.
  2. **No __init__.py**: The .claude/ copy has no `__init__.py`
  but the
     src/ copy does. Inconsistency with sync expectations.

  ### Determinism & Enforcement Gaps (Scored 3/10 for generation
   process)
  3. The portification PROCESS is entirely inference-based with
  no self-validation
     gates equivalent to tasklist's 17-check pre-write
  validation.
  4. No Sprint Compatibility Self-Check equivalent for the
  GENERATION process
     (only the generated code has gates).
  5. No structural quality gate on emitted Python code — no
  `py_compile`,
     no import verification, no AST validation.

  ### Constraint Specification Gaps (Scored 7/10 for generated
  code, 3/10 for generation)
  6. Phase 1 analysis has an output format template but no
  validation that the
     analysis actually covers all steps in the source workflow.
  7. Phase 2 spec has no completeness check — no way to verify
  all source workflow
     steps were translated into pipeline steps.
  8. Phase 3 code generation has templates but no validation
  that generated code
     compiles, imports resolve, or base class contracts are
  satisfied.

  ### Integration Risks
  9. Depends on `pipeline/` module APIs that are actively being
  modified
     (v2.14-unified-audit-gating branch).
  10. Generated code must correctly implement `PipelineConfig`,
  `Step`,
      `StepResult`, `GateMode`, `GateCriteria` contracts — no
  compile-time
      verification during generation.

  ### Missing Elements Compared to Peer Skills
  11. No effort/risk scoring (tasklist has deterministic
  formulas)
  12. No compliance tier classification for the portification
  tasks themselves
  13. No checkpoint/review cadence within phases (only user
  review between phases)
  14. No TodoWrite integration for progress tracking
  15. No MCP usage specification (frontmatter claims sequential,
   serena, context7
      but SKILL.md body never references them)

  ## Panel Directives

  Ask each expert to specifically address:

  **Wiegers**: Are the requirements for each phase complete?
  What is unspecified
  that a developer would need to decide ad hoc? Compare
  constraint completeness
  to sc:tasklist-protocol's 17 self-checks and
  sc:roadmap-protocol's validation
  waves.

  **Fowler**: Is the 4-phase architecture sound? Where does the
  interface between
  "analysis" and "code generation" leak? How does this compare
  to sc:adversarial's
  clean 5-step pipeline?

  **Nygard**: What failure modes exist in each phase? What
  happens when Phase 3
  generates code that doesn't compile? Compare to sc:tasklist's
  write atomicity
  guarantee and sc:adversarial's convergence-gated merge.

  **Whittaker**: Attack the Phase 1 classification rubric. Can a
   workflow step be
  misclassified as "pure programmatic" when it requires
  judgment? What happens
  when the code templates don't cover a workflow pattern? Apply
  all 5 attack
  methodologies against the step decomposition algorithm.

  **Crispin**: What is the testing story? The skill generates a
  "structural test"
  in Phase 4 — is that sufficient? What testing would be needed
  to validate the
  GENERATION process, not just the generated code?

  **Adzic**: Provide concrete Given/When/Then scenarios for each
   phase. What does
  "correct portification" look like for a simple workflow vs a
  complex multi-agent
  workflow like sc:adversarial?

  ## Desired Output

  The panel review should produce findings that can be directly
  transformed into:
  1. A refactoring specification for cli-portify
  2. Input to /sc:roadmap for roadmap generation
  3. Input to /sc:tasklist for sprint execution
  4. A testing strategy for validating the refactored skill

  Organize findings by: CRITICAL (blocks usage), MAJOR (degrades
   quality),
  MINOR (convention/polish). For each finding, reference the
  specific section
  of SKILL.md or ref file, and cite which peer skill
  demonstrates the
  better pattern.
  </context - Prompt used to Generate>

 Specification Review: sc:cli-portify
                                                                                        
  Overall assessment
                                                                                        
  Verdict: promising concept, but not yet specified tightly enough to be safely      
  repeatable.

  - Strength: the generated artifact architecture is directionally sound and aligns with
   existing pipeline primitives (src/superclaude/cli/pipeline/models.py:17,
  src/superclaude/cli/pipeline/gates.py:19).
  - Weakness: the generation process itself is under-specified relative to peer
  protocols like:
    - sc:tasklist-protocol self-check + atomicity
  (src/superclaude/skills/sc-tasklist-protocol/SKILL.md:752, :812, :853)
    - sc:roadmap-protocol wave gating + persistence + explicit MCP usage
  (src/superclaude/skills/sc-roadmap-protocol/SKILL.md:104, :124, :228, :324)
    - sc:adversarial-protocol return-contract + convergence/failure routing
  (src/superclaude/skills/sc-adversarial-protocol/SKILL.md:409, :427)

  Quality scores
  - Requirements completeness: 5/10
  - Architecture soundness: 6/10
  - Generation correctness: 4/10
  - Testability: 3/10
  - Operational determinism: 3/10

  ---
  CRITICAL findings

  C1. Missing command entry point breaks the normal command→protocol architecture

  Evidence
  - sc-cli-portify exists only as a skill package:
  src/superclaude/skills/sc-cli-portify/SKILL.md:1
  - No matching command entry file exists under src/superclaude/commands/ from the
  command glob results.
  - Peer pattern:
    - thin command: src/superclaude/commands/tasklist.md:12
    - full protocol: src/superclaude/skills/sc-tasklist-protocol/SKILL.md:12

  Why it matters
  - Discoverability and invocation semantics are inconsistent with the rest of the
  framework.
  - The spec itself uses /sc:cli-portify usage syntax
  (src/superclaude/skills/sc-cli-portify/SKILL.md:57) but does not define the command
  shim that should validate arguments and invoke the protocol.

  Wiegers
  - The actor entry point is unspecified. A developer must decide ad hoc:
    - whether this is user-invocable directly as a skill,
    - whether a command file is required,
    - how argument validation should be split between command and protocol.

  Cockburn
  - Primary actor interaction is incomplete. The user story begins at /sc:cli-portify,
  but the specification only defines the protocol body.

  Better pattern
  - tasklist command delegates to protocol explicitly:
  src/superclaude/commands/tasklist.md:69-82

  Recommendation
  - Introduce:
    - src/superclaude/commands/cli-portify.md
    - rename/mirror protocol to src/superclaude/skills/sc-cli-portify-protocol/SKILL.md
  - Make the command responsible for input validation and protocol invocation, as
  tasklist does.

  ---
  C2. No blocking self-validation for the generation process

  Evidence
  - sc-cli-portify describes four phases, but no mandatory pre-write self-check exists:
  src/superclaude/skills/sc-cli-portify/SKILL.md:70-168
  - By contrast, sc-tasklist-protocol has mandatory self-check and write atomicity:
    - Sprint Compatibility Self-Check:
  src/superclaude/skills/sc-tasklist-protocol/SKILL.md:752
    - Write atomicity: :812
    - stage validation table: :855-862

  Why it matters
  - Portification is supposed to convert inference into deterministic flow, but the spec
   leaves correctness of the conversion largely inferential.
  - There is no stage gate that proves:
    - all workflow components were discovered,
    - all source steps were represented,
    - all generated files are syntactically valid,
    - integration wiring is internally consistent.

  Nygard
  - This is the largest reliability gap. If Phase 3 emits malformed Python, the current
  spec simply moves to Phase 4 and “verify imports” vaguely
  (src/superclaude/skills/sc-cli-portify/SKILL.md:165-167), with no failure protocol.

  Crispin
  - “Generate structural test” is not a test strategy; it is one artifact. It does not
  validate the generator.

  Better pattern
  - tasklist stage 6 blocks completion until all checks pass:
  src/superclaude/skills/sc-tasklist-protocol/SKILL.md:862

  Recommendation
  Add a mandatory pre-write and post-write validation matrix:
  1. Coverage check: every discovered workflow step mapped exactly once
  2. Template completeness check: all required modules for classified workflow emitted
  3. Python syntax check: ast.parse or py_compile
  4. Import resolution check
  5. Contract conformance check against live pipeline primitives
  6. Integration patch verification
  7. Sync/package layout verification

  ---
  C3. Phase interfaces leak; analysis does not produce machine-checkable handoff
  contracts

  Evidence
  - Phase outputs are prose artifacts:
    - portify-analysis.md: src/superclaude/skills/sc-cli-portify/SKILL.md:106
    - portify-spec.md: :153
  - No machine-readable return contract or schema.
  - Peer pattern:
    - sc:adversarial defines explicit return contract even on failure:
  src/superclaude/skills/sc-adversarial-protocol/SKILL.md:409-427
    - sc:roadmap consumes structured return fields with routing logic:
  src/superclaude/skills/sc-roadmap-protocol/SKILL.md:381-412

  Why it matters
  - Phase 2 depends on Phase 1, but Phase 1 only promises a markdown report.
  - Phase 3 depends on Phase 2, but Phase 2 only promises a narrative spec.
  - This forces the generator to “re-interpret” prior outputs, reintroducing inference.

  Fowler
  - The architecture is not cleanly layered. The “analysis” and “code generation”
  boundary leaks because the output is descriptive, not contractual.

  Hohpe
  - The handoff message lacks schema. This is a contract problem, not a formatting
  problem.

  Recommendation
  Each phase should emit both:
  - human review artifact (.md)
  - machine-readable contract (.yaml / .json) with stable fields, e.g.:
    - discovered_components
    - step_registry
    - classification_decisions
    - gate_definitions
    - planned_modules
    - required_imports
    - validation_status

  ---
  C4. Pipeline API drift risk is unmitigated

  Evidence
  - sc-cli-portify says generated files should import from superclaude.cli.pipeline:
  src/superclaude/skills/sc-cli-portify/SKILL.md:161, 202
  - Actual shared primitive signatures are concrete:
    - SemanticCheck fields are name, check_fn, failure_message:
  src/superclaude/cli/pipeline/models.py:58-64
    - GateCriteria fields are required_frontmatter_fields, min_lines, enforcement_tier,
  semantic_checks: :67-75
    - gate_passed() expects (output_file: Path, criteria: GateCriteria):
  src/superclaude/cli/pipeline/gates.py:19
  - But refs/pipeline-spec.md examples use incompatible names:
    - GateCriteria(tier="standard", required_frontmatter=[...]):
  src/superclaude/skills/sc-cli-portify/refs/pipeline-spec.md:149-164
    - semantic functions returning (bool, str): :169-185
  - Template text also assumes different shape in places.

  Why it matters
  - This is not hypothetical. The reference spec already diverges from the live
  codebase.
  - A generated pipeline following the current ref verbatim will not match current
  pipeline contracts.

  Fowler
  - This is the most concrete architecture leak: the protocol claims reuse of shared
  primitives, but its own reference examples are stale.

  Nygard
  - Failure mode: Phase 3 succeeds syntactically but generated code fails at
  import/runtime due to API mismatch.

  Recommendation
  - Add a contract verification stage that reads live shared APIs before generation and
  validates template compatibility against:
    - src/superclaude/cli/pipeline/models.py:58-90
    - src/superclaude/cli/pipeline/gates.py:19-68
  - Ref files must be updated to match live field names and call signatures.

  ---
  C5. No correctness guarantee that all source workflow steps are preserved

  Evidence
  - Phase 1 asks to “identify steps” and “map dependencies” but no completeness
  invariant is defined: src/superclaude/skills/sc-cli-portify/SKILL.md:88-105
  - Phase 2 asks to design the step graph, but again no bijection/completeness check:
  :116-151

  Why it matters
  - Portification can silently drop a source step, collapse two semantically distinct
  steps into one, or omit a user-facing gate.
  - The spec has no “count conservation” rule.

  Whittaker
  - This is vulnerable to sequence and divergence attacks: once a source workflow
  contains optional branches or nested delegation, the current decomposition algorithm
  can lose steps without detection.

  Recommendation
  Define invariants:
  1. Every source workflow step/delegation/gate is assigned a stable source ID.
  2. Every source ID maps to:
    - one generated step,
    - or one justified elimination record.
  3. No downstream phase may proceed if unmapped source IDs remain.

  ---
  MAJOR findings

  M1. Extended metadata is commented out, not real frontmatter

  Evidence
  - Metadata block is inside HTML comment:
  src/superclaude/skills/sc-cli-portify/SKILL.md:7-12
  - Peer command/skill files expose structured frontmatter directly, e.g.:
    - src/superclaude/commands/tasklist.md:1-9
    - src/superclaude/skills/sc-tasklist-protocol/SKILL.md:1-9

  Impact
  - Tooling cannot reliably inspect category, complexity, MCP servers, personas.
  - This supports your finding that MCP usage is claimed but not operationalized.

  Recommendation
  Promote metadata into actual frontmatter fields.

  ---
  M2. MCP usage is declared but not behaviorally integrated

  Evidence
  - sc-cli-portify comment lists sequential, serena, context7, auggie-mcp:
  src/superclaude/skills/sc-cli-portify/SKILL.md:10
  - Body never says when each is used.
  - Peer pattern:
    - tasklist explicitly documents MCP usage:
  src/superclaude/skills/sc-tasklist-protocol/SKILL.md:895-902
    - roadmap explicitly maps servers to waves:
  src/superclaude/skills/sc-roadmap-protocol/SKILL.md:324-335

  Recommendation
  Add a ## MCP Usage table with phase-level use:
  - Auggie/Semantic retrieval: peer-skill and pipeline API discovery
  - Serena: session persistence / resumability
  - Sequential: classification conflict resolution
  - Context7: if external framework/library APIs are referenced by target workflow

  ---
  M3. No progress-tracking contract

  Evidence
  - allowed-tools includes TodoWrite, but no body behavior uses it:
  src/superclaude/skills/sc-cli-portify/SKILL.md:4
  - Peer pattern: tasklist stage reporting contract + TodoWrite integration:
  src/superclaude/skills/sc-tasklist-protocol/SKILL.md:851-878

  Impact
  - Long-running multi-phase generation has no deterministic progress reporting.
  - Harder to resume or audit.

  Recommendation
  Define stage completion messages and required task updates for each phase and
  subphase.

  ---
  M4. Phase 4 “Verify imports” is too vague to be meaningful

  Evidence
  - Verify imports — Quick check for circular dependencies:
  src/superclaude/skills/sc-cli-portify/SKILL.md:166

  Issue
  - “Quick check” is not measurable.
  - It says nothing about:
    - import resolution,
    - package __init__.py,
    - command registration correctness,
    - syntax validity,
    - broken symbols,
    - cyclic import detection method.

  Recommendation
  Replace with explicit checks:
  - import every generated module
  - verify exported command symbol exists
  - verify main.py registration target name resolves
  - run ast.parse/py_compile
  - run isolated import smoke test

  ---
  M5. Generated-code templates do not define template applicability boundaries

  Evidence
  - Templates assume a standard module set and sprint-style execution:
  src/superclaude/skills/sc-cli-portify/refs/code-templates.md:7-22, :307-509
  - But no decision matrix says when a workflow pattern requires extra modules beyond
  inventory.py and filtering.py.

  Whittaker
  - If a workflow has:
    - nested debate rounds,
    - multi-artifact return contracts,
    - dynamic fan-out/fan-in,
    - resume from externally generated artifacts,
  then the current templates may not cover the pattern, but the skill has no
  “unsupported pattern” escape hatch.

  Recommendation
  Add a pattern-coverage matrix:
  - supported natively
  - supported with optional modules
  - unsupported → abort with explicit reason

  ---
  M6. No explicit failure routing for compile/import/test failures

  Evidence
  - Phases are linear, but failure routing is absent:
  src/superclaude/skills/sc-cli-portify/SKILL.md:70-168
  - Peer pattern:
    - roadmap defines per-wave failure/abort behavior:
  src/superclaude/skills/sc-roadmap-protocol/SKILL.md:427-445
    - adversarial writes failure contract on abort:
  src/superclaude/skills/sc-adversarial-protocol/SKILL.md:427

  Recommendation
  Introduce status model for generation process itself:
  - analysis_failed
  - spec_incomplete
  - template_mismatch
  - compile_failed
  - import_failed
  - integration_failed
  - validation_failed

  Each with:
  - blocking/advisory status
  - remediation guidance
  - resumable checkpoint

  ---
  M7. The output package location and CLI integration assumptions are underspecified

  Evidence
  - Output package under src/superclaude/cli/<name>/:
  src/superclaude/skills/sc-cli-portify/SKILL.md:33
  - Integration says “patch main.py”: :165
  - Actual main.py uses click and currently registers sprint and roadmap:
  src/superclaude/cli/main.py:354-360

  Issue
  - Spec does not define:
    - whether generated command name must be unique
    - collision behavior if package exists
    - naming transformation rules
    - whether install/distribution tooling must be updated too

  Recommendation
  Specify:
  - name normalization
  - collision suffix behavior
  - overwrite policy
  - package export contract
  - CLI registration convention

  ---
  MINOR findings

  N1. .claude / src sync inconsistency around __init__.py

  Evidence
  - .claude/skills/sc-cli-portify/** contains only SKILL.md and refs; no __init__.py in
  dev copy
  - This is inconsistent with sync expectations described in project CLAUDE.md

  Impact
  - Not a primary spec blocker, but it increases ambiguity around install/sync
  expectations.

  ---
  N2. “100% completion” is not measurable

  Evidence
  - Purpose statement: ensure 100% completion and consistency between runs:
  src/superclaude/skills/sc-cli-portify/SKILL.md:16

  Wiegers
  - This is aspirational language, not a verifiable requirement.

  Recommendation
  Replace with measurable claims:
  - “all required phases either pass blocking checks or halt with a resumeable failure
  state”
  - “same inputs produce same step graph and module inventory”

  ---
  N3. Boundaries omit unsupported-source cases

  Evidence
  - Will analyze any workflow: src/superclaude/skills/sc-cli-portify/SKILL.md:217-222

  Issue
  - “Any” is too broad. Some workflows may not fit sprint/pipeline architecture.

  Recommendation
  State unsupported cases explicitly:
  - recursive agent orchestration
  - workflows relying on interactive human decisions mid-pipeline
  - workflows with no stable artifact boundaries

  ---
  Expert-specific critique

  Karl Wiegers — Requirements completeness

  Main judgment: requirements are incomplete at every phase boundary.

  Missing measurable requirements:
  - Phase 1 completeness criteria
  - Phase 2 translation completeness criteria
  - Phase 3 code validity criteria
  - Phase 4 success/failure routing
  - MCP usage requirements
  - resume checkpoint behavior
  - unsupported-pattern behavior

  Compared to peer skills:
  - tasklist is much tighter because it defines stage validation and self-check criteria
   (src/superclaude/skills/sc-tasklist-protocol/SKILL.md:855-862)
  - roadmap is much tighter because each wave has entry/exit criteria and error paths
  (src/superclaude/skills/sc-roadmap-protocol/SKILL.md:104-245)

  Martin Fowler — Architecture

  Main judgment: 4 phases are conceptually right, but the interfaces are wrong.

  Good:
  - analysis → spec → generation → integration is a reasonable decomposition.

  Bad:
  - each boundary currently exports prose, not contract.
  - template refs drift from live code.
  - generated artifact architecture assumes stable shared primitives without verifying
  them.

  Compared to sc:adversarial:
  - adversarial has a cleaner pipeline because it defines return contract, convergence
  thresholds, and failure-stage routing
  (src/superclaude/skills/sc-adversarial-protocol/SKILL.md:409-427).

  Michael Nygard — Failure modes

  Main judgment: failure handling is the biggest missing subsystem.

  Per phase:
  - Phase 1: incomplete discovery, stale refs, missing agents
  - Phase 2: stale pipeline API assumptions, dropped steps, incorrect gate design
  - Phase 3: syntax errors, import errors, wrong shared primitive usage, unsupported
  pattern generation
  - Phase 4: partial integration patch, circular imports, structurally valid but
  unusable pipeline

  The spec should not merely “verify imports”; it should classify failures and halt with
   resume guidance.

  James Whittaker — Adversarial attack review

  Main judgment: Phase 1 classification rubric is breakable.

  Attack findings

  1. Zero/Empty Attack
    - I can break this specification by Zero/Empty Attack.
    - The invariant at SKILL.md Phase 1 classification rubric
  (src/superclaude/skills/sc-cli-portify/SKILL.md:95-99) fails when a step appears
  deterministic structurally but contains zero explicit semantic cues indicating
  judgment is required.
    - Concrete attack: a “classify file domain” step reads ambiguous filenames and
  comments. The spec labels it pure-programmatic, but correct behavior requires semantic
   interpretation. Generated code hardcodes heuristics and silently misclassifies.
  2. Divergence Attack
    - I can break this specification by Divergence Attack.
    - The invariant at step decomposition rules (:88-93) fails when one source action
  satisfies multiple step-boundary conditions simultaneously.
    - Concrete attack: a single operation both changes execution mode and produces an
  artifact. Different runs may split it into one or two generated steps, destroying
  determinism.
  3. Sentinel Collision Attack
    - I can break this specification by Sentinel Collision Attack.
    - The invariant at gate mode assignment (:102-104) fails when a step is marked
  TRAILING because it looks “quality-only,” but downstream prompts implicitly consume it
   as context.
    - Concrete attack: a “quality memo” is actually referenced later in context
  injection; trailing failure should have been blocking.
  4. Sequence Attack
    - I can break this specification by Sequence Attack.
    - The invariant at Phase handoff (:106, :153, :157) fails when Phase 3 begins from
  an incomplete Phase 2 artifact.
    - Concrete attack: missing prompt definitions are inferred from narrative text;
  generation continues with defaults, producing compilable but behaviorally incomplete
  code.
  5. Accumulation Attack
    - I can break this specification by Accumulation Attack.
    - The invariant at dynamic/batched workflow support (:100, :116) fails when batch
  count or step count expands beyond template assumptions.
    - Concrete attack: a large workflow fans out into many dynamic groups, but templates
   and dry-run previews assume a fixed module shape and step registry.

  Lisa Crispin — Testing strategy

  Main judgment: structural test generation is insufficient.

  Needed test layers:
  1. Spec-process tests
    - verify decomposition completeness
    - verify classification reproducibility
    - verify unsupported-pattern aborts
  2. Generator tests
    - golden tests from representative source skills
    - compile/import smoke tests
    - template coverage tests
  3. Contract tests
    - generated code vs live pipeline primitives
  4. End-to-end fixture tests
    - portify known simple workflow
    - portify complex adversarial workflow
    - assert emitted step graph, gates, files, imports

  Gojko Adzic — Examples

  Main judgment: the spec needs executable examples per phase.

  Good scenarios are missing for:
  - simple single-agent workflow
  - batched multi-pass workflow
  - multi-agent debate workflow
  - unsupported workflow

  ---
  Correctness focus artifacts

  State Variable Registry

  Variable Name: workflow_path
  Type: path/string
  Initial Value: user input
  Invariant: must resolve to valid skill
  Read Operations: Phase 1 discovery
  Write Operations: command input parse
  ────────────────────────────────────────
  Variable Name: component_inventory
  Type: list
  Initial Value: empty
  Invariant: every discovered component unique and typed
  Read Operations: Phase 1 output, Phase 2 mapping
  Write Operations: Phase 1 discovery
  ────────────────────────────────────────
  Variable Name: source_step_registry
  Type: list/map
  Initial Value: empty
  Invariant: every source step has stable ID
  Read Operations: Phase 1/2/3 validation
  Write Operations: Phase 1 decomposition
  ────────────────────────────────────────
  Variable Name: classification_map
  Type: map
  Initial Value: empty
  Invariant: each source step classified exactly once
  Read Operations: Phase 2 design
  Write Operations: Phase 1 classification
  ────────────────────────────────────────
  Variable Name: dependency_graph
  Type: graph
  Initial Value: empty
  Invariant: acyclic unless explicitly supported
  Read Operations: Phase 2 executor design
  Write Operations: Phase 1 mapping
  ────────────────────────────────────────
  Variable Name: gate_registry
  Type: map
  Initial Value: empty
  Invariant: every generated artifact has defined gate or exemption
  Read Operations: Phase 2/3/4
  Write Operations: Phase 1 extraction, Phase 2 design
  ────────────────────────────────────────
  Variable Name: module_plan
  Type: list
  Initial Value: empty
  Invariant: required generated modules reflect workflow pattern
  Read Operations: Phase 3 generation
  Write Operations: Phase 2 planning
  ────────────────────────────────────────
  Variable Name: generated_files
  Type: list
  Initial Value: empty
  Invariant: all required files present, no undeclared extras
  Read Operations: Phase 4 validation
  Write Operations: Phase 3 generation
  ────────────────────────────────────────
  Variable Name: integration_status
  Type: enum
  Initial Value: unset
  Invariant: main.py patch valid or explicitly skipped
  Read Operations: Phase 4 summary
  Write Operations: Phase 4
  ────────────────────────────────────────
  Variable Name: validation_status
  Type: enum
  Initial Value: unset
  Invariant: completion requires all blocking validations passed
  Read Operations: final reporting
  Write Operations: every phase
  ────────────────────────────────────────
  Variable Name: resume_checkpoint
  Type: phase marker
  Initial Value: none
  Invariant: latest completed validated phase only
  Read Operations: resume flow
  Write Operations: phase completion

  ---
  Guard Condition Boundary Table

  Guard: workflow provided
  Location: SKILL.md:68
  Input Condition: Zero/Empty
  Variable Value: missing --workflow
  Guard Result: stop
  Specified Behavior: explicitly stop
  Status: OK
  ────────────────────────────────────────
  Guard: workflow resolves
  Location: SKILL.md:68
  Input Condition: Legitimate Edge Case
  Variable Value: name matches multiple skills
  Guard Result: unclear
  Specified Behavior: unspecified disambiguation
  Status: GAP
  ────────────────────────────────────────
  Guard: classify as pure-programmatic
  Location: SKILL.md:95-99
  Input Condition: Zero/Empty
  Variable Value: no clear heuristic evidence
  Guard Result: ambiguous
  Specified Behavior: unspecified confidence threshold
  Status: GAP
  ────────────────────────────────────────
  Guard: gate mode trailing
  Location: SKILL.md:104
  Input Condition: Typical
  Variable Value: quality-only step
  Guard Result: continue
  Specified Behavior: partially specified
  Status: OK
  ────────────────────────────────────────
  Guard: gate mode trailing
  Location: SKILL.md:104
  Input Condition: Legitimate Edge Case
  Variable Value: “quality-only” step later used as prompt context
  Guard Result: should block
  Specified Behavior: unspecified
  Status: GAP
  ────────────────────────────────────────
  Guard: prompt split threshold
  Location: SKILL.md:132
  Input Condition: Maximum/Overflow
  Variable Value: prompts >300 lines
  Guard Result: split file
  Specified Behavior: specified
  Status: OK
  ────────────────────────────────────────
  Guard: prompt split threshold
  Location: SKILL.md:132
  Input Condition: Boundary
  Variable Value: prompts ≈300 lines
  Guard Result: unclear
  Specified Behavior: unspecified exact comparator
  Status: GAP
  ────────────────────────────────────────
  Guard: code generation order
  Location: SKILL.md:159-161
  Input Condition: Sequence
  Variable Value: one file fails generation mid-order
  Guard Result: should halt/rollback
  Specified Behavior: unspecified
  Status: GAP
  ────────────────────────────────────────
  Guard: main.py patch
  Location: SKILL.md:165
  Input Condition: Sentinel Value Match
  Variable Value: command name collides with existing CLI command
  Guard Result: should rename or abort
  Specified Behavior: unspecified
  Status: GAP
  ────────────────────────────────────────
  Guard: verify imports
  Location: SKILL.md:166
  Input Condition: Typical
  Variable Value: import smoke passes
  Guard Result: continue
  Specified Behavior: vague “quick check”
  Status: GAP
  ────────────────────────────────────────
  Guard: structural test generation
  Location: SKILL.md:167
  Input Condition: Zero/Empty
  Variable Value: no test file emitted
  Guard Result: should fail
  Specified Behavior: unspecified
  Status: GAP
  ────────────────────────────────────────
  Guard: optional inventory/filtering modules
  Location: SKILL.md:49-50
  Input Condition: Legitimate Edge Case
  Variable Value: workflow needs other optional modules
  Guard Result: should extend or abort
  Specified Behavior: unspecified
  Status: GAP

  Per the spec-panel hard-gate rules, every GAP above is at least MAJOR.

  ---
  Quantity Flow Diagram

  This spec clearly describes a multi-stage pipeline with count divergence risk.

  [Source workflow components: N discovered items]
      --> [Phase 1: decomposition]
      --> [S source steps]

  [S source steps]
      --> [Phase 2: pipeline design]
      --> [P planned generated steps/modules]

  Potential mismatch point:
  S != P when:
  - one source step split into multiple generated steps
  - multiple source steps collapsed into one generated step
  - unsupported patterns silently omitted

  [P planned items]
      --> [Phase 3: generated files]
      --> [F files emitted]

  Potential mismatch point:
  P requires F_expected, but templates may emit F_actual < F_expected

  [F emitted files]
      --> [Phase 4: integration + structural test]
      --> [I validated integration artifacts]

  Potential mismatch point:
  F_actual may be syntactically present, but I may not validate shared primitive
  compatibility

  Critical dimensional risk: the spec never states the conservation rule between source
  step count and generated step coverage.

  ---
  Given/When/Then scenarios

  Simple workflow

  Phase 1

  Given a simple single-skill workflow with 3 sequential steps and no agents
  When portification analysis runs
  Then portify-analysis.md must contain exactly 3 source steps, 0 parallel groups, 3
  classifications, and 3 gate decisions.

  Phase 2

  Given the Phase 1 analysis above
  When the step graph is designed
  Then every source step must map to one generated Step or one justified elimination
  record.

  Phase 3

  Given a spec with 3 mapped steps
  When code generation runs
  Then all required files are emitted, syntax-valid, importable, and contract-compatible
   with live pipeline primitives.

  Phase 4

  Given generated files and integration requested
  When integration runs
  Then the new CLI group is registered once in main.py and structural validation passes.

  Complex multi-agent workflow (sc:adversarial-like)

  Phase 1

  Given a workflow with variant generation, debate rounds, convergence checks, merge
  execution, and return contract
  When portification analysis runs
  Then the analysis must identify:
  - parallel generation group
  - sequential debate rounds
  - convergence gate
  - merge executor boundary
  - final return contract artifact

  Phase 2

  Given the above analysis
  When pipeline design runs
  Then the generated design must preserve:
  - debate sequencing
  - convergence threshold logic
  - failure-stage routing
  - machine-readable final contract

  Phase 3

  Given the complex design
  When code generation runs
  Then unsupported patterns must either be covered by explicit templates or cause a
  blocking abort before file emission.

  Phase 4

  Given generated files for the complex workflow
  When validation runs
  Then compile/import/contract tests must pass before integration is marked successful.

  ---
  Refactoring spec inputs

  Immediate refactor requirements

  1. Add command shim for /sc:cli-portify
  2. Rename or formalize protocol skill naming to match conventions
  3. Add phase contracts (analysis.yaml, spec.yaml)
  4. Add mandatory self-check before any write
  5. Add write atomicity
  6. Add live contract verification against src/superclaude/cli/pipeline/models.py and
  gates.py
  7. Add phase-level MCP usage
  8. Add TodoWrite progress contract
  9. Add failure routing + resume checkpoints
  10. Add unsupported-pattern detection

  Roadmap input themes

  - Convention alignment
  - Deterministic generation engine
  - Contract-driven phase boundaries
  - Validation harness for generator
  - Template coverage expansion
  - Pipeline API compatibility safeguards

  Tasklist input themes

  - Create command shim
  - Introduce protocol rename/migration plan
  - Define phase contract schemas
  - Implement self-check matrix
  - Implement compile/import/AST validation
  - Implement coverage mapping checks
  - Add golden fixture test suite
  - Add unsupported-pattern matrix

  Testing strategy for refactored skill

  Generator-process tests

  - decomposition completeness
  - classification reproducibility
  - phase contract validity
  - failure routing correctness

  Generated-code tests

  - syntax compilation
  - import smoke tests
  - pipeline primitive compatibility
  - command registration validation

  Golden-fixture tests

  - simple sequential skill
  - batched audit skill
  - adversarial multi-agent skill
  - intentionally unsupported skill

  ---
  Consensus summary

  Blocks usage

  - Missing command/protocol architecture
  - No generator self-check or atomicity
  - No machine-checkable phase contracts
  - No live pipeline contract verification

  Degrades quality

  - No MCP usage contract
  - No progress tracking
  - Vague import/integration validation
  - No failure routing or resume protocol

  Convention/polish

  - commented metadata instead of real frontmatter
  - sync/layout inconsistency
  - non-measurable wording like “100% completion”