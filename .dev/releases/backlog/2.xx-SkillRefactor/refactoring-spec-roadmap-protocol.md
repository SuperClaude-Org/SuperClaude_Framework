# Refactoring Spec: sc:roadmap-protocol

Analysis of sc:roadmap-protocol through two lenses: architectural uplift from cli-portify patterns and CLI runner pipeline optimization.

---

## Current Architecture Assessment

### Current Step Count and Flow

sc:roadmap-protocol operates across 5 waves (0-4) plus a Post-Wave completion phase, totaling approximately 25 discrete sub-steps:

```
Wave 0 (8 sub-steps):  Prerequisite validation
Wave 1A (6 sub-steps): Spec consolidation (conditional on --specs)
Wave 1B (10 sub-steps): 8-step extraction pipeline + complexity scoring + persona activation
Wave 2 (7 sub-steps):  4-tier template discovery + milestone planning + optional adversarial
Wave 3 (4 sub-steps):  Artifact generation (roadmap.md, test-strategy.md, extraction.md frontmatter)
Wave 4 (8 sub-steps):  Multi-agent validation + REVISE loop (max 2 iterations)
Post-Wave (6 sub-steps): Artifact verification, session persistence, summary
```

Data flow: `spec(s) -> extraction.md -> milestone structure -> roadmap.md -> test-strategy.md -> validation`

### Current Validation Mechanisms

1. **Wave 0**: Pure programmatic checks -- file existence, directory writability, collision detection, skill availability, flag compatibility. All deterministic.
2. **Wave 1A**: Convergence score routing with 3-tier thresholds (>=0.6 PASS, >=0.5 PARTIAL, <0.5 FAIL). Deterministic routing on a value produced by inference (sc:adversarial).
3. **Wave 1B**: 4-pass completeness verification on extraction output. Passes 1-2 (source coverage, anti-hallucination) are structural/programmatic. Passes 3-4 are mixed.
4. **Wave 2**: Template compatibility scoring (4-factor formula, fully deterministic). DAG cycle detection (fully programmatic). Adversarial convergence routing (same pattern as Wave 1A).
5. **Wave 4**: Dual-agent validation (quality-engineer + self-review) with weighted score aggregation (0.55/0.45). Thresholds: PASS >=85%, REVISE 70-84%, REJECT <70%. The aggregation formula and routing are deterministic; the scoring inputs are inference.

### Current Integration Points

- **sc:adversarial-protocol**: Invoked via `Skill` tool in Wave 1A (multi-spec) and Wave 2 (multi-roadmap). Return contract consumed inline with 9-field schema and consumer defaults.
- **Serena MCP**: Session persistence at wave boundaries. Fallback to `.session-memory.md` file.
- **Sequential MCP**: Used in Waves 1-4 for analysis reasoning.
- **Context7 MCP**: Used in Waves 1-2 for template patterns and domain best practices.
- **Task tool**: Used in Wave 4 for parallel agent dispatch (quality-engineer, self-review).

### Architectural Strengths to Preserve

1. **Wave architecture with explicit boundaries**: Clean separation of concerns per wave. Entry/exit criteria defined. This maps directly to pipeline Step groups.
2. **On-demand ref loading**: Prevents context bloat. Each wave loads only the refs it needs. This is a genuine optimization that should be preserved in any portification.
3. **YAML frontmatter contract stability**: "Fields may be added but never removed" (NFR-003). This is a backward-compatibility guarantee that makes gate validation reliable.
4. **Execution vocabulary binding**: Every verb maps to exactly one tool. This is already a form of the "deterministic flow control" principle from cli-portify.
5. **Error handling matrix**: 6 specific error conditions with detection methods and actions. Maps directly to diagnostic chain failure classifications.
6. **Session persistence with resume protocol**: Wave-boundary save points, spec hash mismatch detection, collision resolution on resume. Already approaching cli-portify's resume pattern.
7. **Read-only validation agents**: Wave 4 agents explicitly cannot modify artifacts. This is the subprocess isolation principle already in practice.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement over self-referential LLM validation** | HIGH | Wave 0 is already 100% programmatic. Wave 4 score aggregation (formula + thresholds + routing) should become a Python function. Wave 1A/2 convergence routing should become `_route_convergence(score: float, interactive: bool) -> ConvergenceDecision`. YAML frontmatter structural validation (field presence, type checking, mutual exclusion of spec_source/spec_sources) should be a pure gate function. The quality-engineer's consistency checks (ID schema regex, frontmatter-body cross-check) are partially automatable as semantic checks. | Medium -- 4-6 gate functions, 1 score aggregator, 1 convergence router | HIGH -- Without programmatic enforcement, the 0.55/0.45 aggregation formula, threshold routing, and REVISE loop termination depend on the LLM correctly applying arithmetic. Arithmetic errors silently produce wrong PASS/REJECT decisions. |
| **(b) Pure-function gate criteria: (str) -> tuple[bool, str]** | HIGH | Define these gate functions: `_artifacts_exist(dir: Path) -> tuple[bool, str]` (Wave 0 exit, Post-Wave). `_frontmatter_valid(content: str, schema: dict) -> tuple[bool, str]` (Wave 3 exit). `_convergence_above_threshold(score: float, threshold: float) -> tuple[bool, str]` (Wave 1A/2). `_milestone_dag_acyclic(deps: dict[str, list[str]]) -> tuple[bool, str]` (Wave 2). `_id_schemas_consistent(content: str) -> tuple[bool, str]` (Wave 4 subset). `_extraction_completeness(extraction: str, spec: str) -> tuple[bool, str]` (Wave 1B Pass 1). `_spec_source_mutex(content: str) -> tuple[bool, str]` (all artifacts). Pipeline's existing `gate_passed()` + `GateCriteria` + `SemanticCheck` infrastructure is a direct fit -- these functions slot into `SemanticCheck.check_fn`. | Low -- Pure functions with well-defined inputs/outputs. Existing `gate_passed()` provides the execution framework. | MEDIUM -- Without typed gates, validation depends on the LLM remembering to check each condition. Missing a check is silent. |
| **(c) Classification rubric: programmatic vs inference** | HIGH | See Pipeline Optimization Plan below for per-sub-step classification. Summary: Wave 0 (100% programmatic), Wave 1A orchestration (80% programmatic, 20% contract consumption routing), Wave 1B extraction (70% inference, 30% programmatic: complexity formula, domain classification by keyword dictionary, ID assignment, chunked extraction section index), Wave 2 planning (60% programmatic: template discovery, scoring, milestone count formula, dependency mapping, DAG validation; 40% inference: milestone content creation), Wave 3 generation (85% inference: content generation; 15% programmatic: sequencing constraint, frontmatter assembly), Wave 4 validation (40% programmatic: dispatch, score aggregation, threshold routing, REVISE loop control; 60% inference: quality evaluation). | Low -- Classification is analysis, not implementation | HIGH -- Without clear classification, portification will either over-automate (breaking inference-dependent steps) or under-automate (missing programmatic opportunities). |
| **(d) Step graph with dependency resolution** | HIGH | The wave architecture already encodes a linear dependency chain (Wave N depends on Wave N-1). Within waves, dependencies exist: Wave 3 has roadmap.md -> test-strategy.md (explicit sequencing constraint). Wave 4 has quality-engineer || self-review (explicit parallel group). Wave 2 Step 3a-3f is a sub-graph with its own dependency chain and fallback branches. Model this as: `steps = [wave0_group, wave1a_group_if_specs, wave1b_group, wave2_group, wave3_sequential, [wave4_quality, wave4_self_review], post_wave_group]`. The pipeline executor's `list[Step | list[Step]]` type signature already supports this exactly. | Medium -- Requires decomposing each wave into Step objects with proper `inputs` fields | LOW -- The existing wave architecture already enforces ordering. The uplift is primarily in explicit dependency tracking for resume/retry precision. |
| **(e) Resume/retry with exact CLI resume commands** | MEDIUM | Current resume is Serena-based with `last_completed_wave` tracking. Portification would add: `superclaude roadmap run --resume --start wave-1b --spec <path> --output <dir>`. The `StepResult` from each completed step persists to a state file (JSONL). Resume reads the state file, skips completed steps, and continues from the first incomplete step. This is superior to Serena memory because: (1) it survives Serena outages, (2) it provides exact CLI commands, (3) it enables retry of specific sub-steps within a wave. Current spec hash mismatch detection should be preserved. | Medium -- State serialization, resume argument parsing, step-skip logic | MEDIUM -- Current Serena resume works but lacks precision. A failed Wave 2 Step 3d (adversarial invocation) currently requires restarting all of Wave 2. With step-level resume, only the failed step reruns. |
| **(f) Budget economics via TurnLedger** | HIGH | Wave 4 dispatches 2 validation agents. Each REVISE iteration dispatches 2 more. Maximum: 6 agent invocations (2 initial + 2 per REVISE x 2 iterations). Wave 1A/2 adversarial invocations can spawn 2-10 debate agents each. Budget is currently unbounded -- an adversarial debate with 10 agents and 3 depth rounds could consume enormous context. TurnLedger integration would: pre-compute budget ceiling per wave, guard before agent dispatch, track cumulative consumption, enable budget-aware REVISE iteration decisions (skip iteration 2 if budget exhausted). | High -- Requires TurnLedger integration across all agent dispatch points, budget estimation heuristics for adversarial debates | HIGH -- Without budget tracking, adversarial modes can exhaust context windows or session budgets with no warning. The user has no visibility into consumption. |
| **(g) Diagnostic chain** | MEDIUM | Current error handling is per-wave with static abort messages. A diagnostic chain would: (1) Collect structured results from each wave (StepResult objects). (2) Classify failures: `SpecParseError`, `AdversarialConvergenceFailure`, `TemplateDiscoveryFailure`, `DAGCycleDetected`, `ValidationRejection`, `SerenaUnavailable`. (3) Generate targeted recovery: convergence failure -> suggest reducing agent count or depth; validation rejection -> show top 3 issues from agent reports; DAG cycle -> show the cycle path. (4) Emit resume command. The existing `diagnostic_chain.py` in the pipeline module provides the 4-stage framework (troubleshoot -> root causes -> solutions -> summary). sc:roadmap failures map cleanly to this. | Medium -- Failure classifier with 6 categories, recovery suggestion templates | LOW -- Current abort messages are adequate for simple failures. The diagnostic chain adds value primarily for adversarial mode failures where the cause is non-obvious. |
| **(h) 4-layer subprocess isolation** | HIGH | Wave 4 agents (quality-engineer, self-review) are already specified as read-only. But enforcement is behavioral (the prompt says "read-only"), not structural. Portification would use `ClaudeProcess` with: (1) Scoped work dir (read-only mount of output directory). (2) Git ceiling to prevent repo-wide access. (3) Isolated plugin dir (no access to sc:adversarial or other skills). (4) Isolated settings (no session persistence from validation agents). For adversarial invocations, the isolation model is different: sc:adversarial needs write access to its artifacts dir but should not modify the roadmap output dir. | Medium -- ClaudeProcess configuration per agent type, directory scoping | HIGH -- Without structural isolation, a validation agent could modify artifacts it is supposed to validate. A misbehaving adversarial subprocess could overwrite roadmap artifacts. The "read-only" behavioral instruction is a request, not a guarantee. |
| **(i) Context injection for inter-step data flow** | HIGH | Current data flow is implicit -- Wave 1B writes extraction.md, Wave 2 reads it. Wave 3 writes roadmap.md, then test-strategy.md references it. Making this explicit as typed data structures would improve reliability. Proposed types: `ExtractionResult(requirements: list[Requirement], complexity: ComplexityScore, domains: list[DomainDistribution], risks: list[Risk])`. `MilestoneGraph(milestones: list[Milestone], dependencies: dict[str, list[str]], effort_estimates: dict[str, EffortLevel])`. `RoadmapContent(frontmatter: dict, body: str, milestone_ids: list[str])`. `ValidationResult(quality_score: float, self_review_score: float, final_score: float, status: ValidationStatus, issues: list[ValidationIssue])`. Context injection: each Claude-assisted step receives a compressed summary of prior step outputs, not the full artifacts. | High -- Type definitions, serialization/deserialization, compression strategy for large extraction results | MEDIUM -- Current implicit data flow works because the LLM can read files. But it is fragile: if extraction.md is malformed, Wave 2 may silently produce incorrect milestone structures. Typed data structures make the contract explicit and enable programmatic validation at hand-off points. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Wave 0 Step 1**: Spec file validation | Inference (Read tool) | Pure programmatic | `_spec_files_exist(paths: list[Path]) -> tuple[bool, str]` -- BLOCKING, STRICT | File existence is `Path.exists()`. Zero inference needed. |
| **Wave 0 Step 2**: Output dir validation | Inference (Bash) | Pure programmatic | `_output_dir_writable(path: Path) -> tuple[bool, str]` -- BLOCKING, STANDARD | `os.access(path, os.W_OK)` or `Path.mkdir()`. |
| **Wave 0 Step 3**: Collision check | Inference (Glob + logic) | Pure programmatic | `_resolve_collisions(dir: Path, names: list[str]) -> tuple[list[str], str]` -- BLOCKING, STANDARD | Glob for existing files, increment suffix. Deterministic. |
| **Wave 0 Step 4**: Template dir check | Inference (Glob) | Pure programmatic | `_template_dirs_available() -> tuple[list[Path], str]` -- TRAILING, LIGHT | 4-tier path existence check. |
| **Wave 0 Step 5**: Adversarial skill check | Inference (Read) | Pure programmatic | `_adversarial_skill_installed() -> tuple[bool, str]` -- BLOCKING, STRICT (when --specs/--multi-roadmap) | `Path.exists()` on SKILL.md. |
| **Wave 0 Steps 6-7**: Flag validation | Inference (Parse) | Pure programmatic | `_validate_flags(flags: dict) -> tuple[bool, str]` -- BLOCKING, STRICT | Model ID validation, --resume-from compatibility checks. All deterministic. |
| **Wave 1A Step 1**: Agent spec parsing | Inference (Parse) | Pure programmatic | No gate (intermediate) | Regex split on `,` then `:`. Well-defined grammar. Existing `refs/adversarial-integration.md` documents the parsing algorithm completely. |
| **Wave 1A Step 2a-2b**: Build adversarial args + invoke | Inference (Skill) | Hybrid: programmatic arg construction + Claude subprocess | `_adversarial_return_contract_valid(response: str) -> tuple[bool, str]` -- BLOCKING, STRICT | Arg construction is string concatenation. Invocation is a subprocess. Gate validates return contract structure. |
| **Wave 1A Step 2e**: Convergence routing | Inference (logic) | Pure programmatic | `_convergence_routing(score: float, interactive: bool) -> ConvergenceDecision` -- inline, no gate | Three-tier threshold comparison. Pure arithmetic. |
| **Wave 1B Steps 1-2**: Spec parsing + chunking decision | Inference (Read + logic) | Hybrid: programmatic chunking (line count, section indexing), Claude for semantic parsing | `_extraction_artifact_valid(content: str) -> tuple[bool, str]` -- BLOCKING, STANDARD | Line counting and section heading detection are `str.splitlines()` + regex. The 500-line threshold is a comparison. Section grouping by relevance_tag is partially automatable. |
| **Wave 1B Steps 3-8**: 8-step extraction pipeline | Inference (primary) | Claude-assisted with strict gate | `_extraction_completeness(extraction: str, spec: str) -> tuple[bool, str]` -- BLOCKING, STRICT. Semantic checks: source coverage (grep-based), anti-hallucination (line range verification), ID schema compliance, requirement count non-zero. | The 8-step extraction is inherently inference-heavy -- it requires reading natural language and classifying requirements. But the output format is well-defined (YAML frontmatter + structured sections), making gate validation highly effective. |
| **Wave 1B Step 5**: Complexity scoring | Inference (formula) | Pure programmatic | No gate (intermediate computation) | The 5-factor weighted formula is fully specified in `refs/scoring.md`. All inputs are counts from extraction output. `complexity_score(req_count, dep_depth, domain_spread, risk_severity, scope_size) -> float`. |
| **Wave 1B Step 6**: Domain classification | Inference (matching) | Hybrid: programmatic keyword matching + inference for ambiguous cases | No gate (intermediate) | `refs/extraction-pipeline.md` provides domain keyword dictionaries. Keyword matching is `set.intersection()`. Ambiguous cases (domain not in dictionary) need inference. |
| **Wave 1B Step 7**: Persona activation | Inference (confidence calc) | Pure programmatic | No gate (intermediate) | `refs/scoring.md` provides the confidence formula: `base * domain_weight * coverage_bonus`. All inputs are domain percentages from classification. The persona-domain mapping table is static. |
| **Wave 2 Step 1**: Template discovery | Inference (Glob) | Pure programmatic | No gate (intermediate) | 4-tier glob across known paths. File validation (YAML frontmatter presence). |
| **Wave 2 Step 2**: Template scoring | Inference (formula) | Pure programmatic | No gate (intermediate) | 4-factor formula from `refs/scoring.md`: domain_match (Jaccard), complexity_alignment, type_match (lookup table), version_compatibility. All deterministic. |
| **Wave 2 Step 3**: Adversarial multi-roadmap | Inference (Skill) | Hybrid: programmatic agent expansion + Claude subprocess + programmatic routing | `_adversarial_return_contract_valid(response: str) -> tuple[bool, str]` -- BLOCKING, STRICT | Reuses same gate and routing as Wave 1A. Agent expansion (adding orchestrator at count >= 3) is a conditional append. |
| **Wave 2 Step 4**: Milestone structure creation | Inference (generation) | Claude-assisted with standard gate | `_milestone_structure_valid(content: str) -> tuple[bool, str]` -- BLOCKING, STANDARD. Semantic checks: milestone count in expected range, ID schema compliance, required sections present per milestone. | Milestone content creation (objectives, deliverable descriptions) requires inference. But the structural constraints (count range, ID format, required sections) are programmatic. |
| **Wave 2 Step 5**: Dependency mapping + DAG validation | Inference (logic) | Hybrid: inference for dependency identification + programmatic DAG validation | `_dag_acyclic(deps: dict[str, list[str]]) -> tuple[bool, str]` -- BLOCKING, STRICT | Dependency identification between milestones requires understanding content. DAG validation is topological sort -- pure algorithm. |
| **Wave 2 Step 6**: Effort estimation | Inference (formula) | Pure programmatic | No gate (intermediate) | `refs/templates.md` provides the algorithm: count deliverables, compute complexity contribution, apply risk multiplier, map to level. All arithmetic. |
| **Wave 3 Step 1**: Generate roadmap.md | Inference (generation) | Claude-assisted with strict gate | `_roadmap_artifact_valid(content: str) -> tuple[bool, str]` -- BLOCKING, STRICT. Semantic checks: frontmatter schema compliance, all required body sections present, milestone count matches frontmatter, ID schemas consistent, spec_source/spec_sources mutex. | Content generation is inference. Structural validation is programmatic. |
| **Wave 3 Step 2**: Generate test-strategy.md | Inference (generation) | Claude-assisted with standard gate | `_test_strategy_valid(content: str, roadmap: str) -> tuple[bool, str]` -- BLOCKING, STANDARD. Semantic checks: interleave ratio matches complexity class, validation milestone IDs reference real work milestones, required sections present. | Content generation is inference. Cross-reference validation (milestone IDs exist in roadmap.md) is programmatic. |
| **Wave 3 Step 3**: Update extraction.md frontmatter | Inference (Edit) | Hybrid: programmatic frontmatter assembly + Edit tool | `_frontmatter_valid(content: str, required_fields: list[str]) -> tuple[bool, str]` -- TRAILING, STANDARD | Frontmatter field values are known from prior waves. Assembly is string formatting. The Edit operation is the only tool needed. |
| **Wave 4 Steps 1-2**: Dispatch validation agents | Inference (Task) | Claude subprocess (parallel group) | Quality-engineer: `_quality_report_valid(content: str) -> tuple[bool, str]` -- BLOCKING, STRICT (JSON structure, all 4 dimensions present, scores in 0-100). Self-review: `_self_review_valid(content: str) -> tuple[bool, str]` -- BLOCKING, STRICT (JSON structure, all 4 questions present, scores in 0-100). | Agent dispatch via `ClaudeProcess` with read-only isolation. Prompt templates from `refs/validation.md`. Gate validates output structure, not content quality. |
| **Wave 4 Step 4**: Score aggregation + routing | Inference (formula) | Pure programmatic | `_final_validation_score(qe_score: float, sr_score: float) -> tuple[float, ValidationStatus]` | `final = qe * 0.55 + sr * 0.45`. Threshold comparison. Pure arithmetic. |
| **Wave 4 Step 7**: REVISE loop control | Inference (logic) | Pure programmatic | Loop controller: `_should_revise(score: float, iteration: int, max_iterations: int) -> ReviseDecision` | Iteration counter, threshold comparison, terminal condition (iteration >= 2 -> PASS_WITH_WARNINGS). |
| **Post-Wave Steps 1-4**: Artifact verification + persistence | Inference (Read + Serena) | Pure programmatic (verification) + Serena call (persistence) | `_all_artifacts_exist(dir: Path) -> tuple[bool, str]` -- BLOCKING, STRICT | File existence checks. Serena call is a side effect, not inference. |

### Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | 16 | Wave 0 (all 8), Wave 1A parsing, convergence routing, Wave 1B complexity scoring + persona activation, Wave 2 template discovery + scoring + effort estimation, Wave 4 score aggregation + REVISE control, Post-Wave verification |
| Claude-Assisted | 5 | Wave 1B extraction pipeline, Wave 2 milestone creation, Wave 3 roadmap generation + test-strategy generation, Wave 4 agent evaluation |
| Hybrid | 6 | Wave 1A adversarial invocation, Wave 1B chunking + domain classification, Wave 2 adversarial multi-roadmap + dependency mapping, Wave 3 frontmatter update |
| Total | 27 | |

---

## Portification Candidacy

**Recommendation: Selective adoption with a phased approach toward full portification.**

### Justification

sc:roadmap-protocol is the strongest candidate for portification among the SuperClaude skills because:

1. **Smallest gap to close**: It already has wave boundaries (maps to Step groups), session persistence (maps to state file), error handling matrix (maps to failure classifier), read-only validation agents (maps to subprocess isolation), and execution vocabulary binding (maps to deterministic flow control). The existing architecture is 60-70% aligned with cli-portify patterns.

2. **High programmatic surface area**: 16 of 27 sub-steps are pure programmatic. Only 5 are pure Claude-assisted. The orchestration logic (routing, scoring, threshold comparison, DAG validation, loop control) is almost entirely deterministic. This is the ideal profile for portification -- the control plane becomes Python, the content plane stays inference.

3. **Clear value from portification**: The highest-impact patterns are (a) programmatic enforcement of score aggregation (prevents arithmetic errors in validation), (f) budget economics (prevents adversarial debates from exhausting resources), and (h) subprocess isolation (enforces read-only validation structurally, not behaviorally).

4. **Existing pipeline infrastructure**: The `src/superclaude/cli/pipeline/` module provides every primitive needed: `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `SemanticCheck`, `gate_passed()`, `ClaudeProcess`, `execute_pipeline()`, `DiagnosticReport`, `run_diagnostic_chain()`. No new framework code is needed.

### What to adopt first (Phase 1: selective)

- Gate functions for all programmatic validations (patterns a, b)
- Score aggregation and convergence routing as Python functions (pattern a)
- Step graph modeling using existing `Step` and `list[Step]` types (pattern d)
- Subprocess isolation for Wave 4 validation agents (pattern h)

### What to adopt second (Phase 2: deeper integration)

- TurnLedger integration for budget tracking across agent dispatches (pattern f)
- Diagnostic chain for structured failure analysis (pattern g)
- Context injection with typed data structures (pattern i)
- Resume/retry with exact CLI commands (pattern e)

### What to defer (Phase 3: full portification)

- Full CLI runner with Rich TUI, NDJSON monitoring, and JSONL logging
- Complete `superclaude roadmap run` CLI subcommand
- Full code generation via sc:cli-portify Phase 3

### Why not full portification immediately

sc:roadmap's Wave 1B (8-step extraction) and Wave 3 (artifact generation) are heavily inference-dependent. Moving these to Claude subprocesses with prompt contracts and gates is valuable but requires careful prompt engineering -- the prompts must produce output that gates can reliably validate. This is Phase 2-3 work. The immediate value is in hardening the control plane (Phase 1).

---

## Testing Plan

### Phase 1: Unit tests for programmatic functions

Target: all 16 pure-programmatic sub-steps.

```
tests/pipeline/roadmap/
    test_gates.py           # All gate functions: _spec_files_exist, _frontmatter_valid,
                            # _convergence_above_threshold, _milestone_dag_acyclic,
                            # _id_schemas_consistent, _extraction_completeness,
                            # _spec_source_mutex, _artifacts_exist, _quality_report_valid,
                            # _self_review_valid, _roadmap_artifact_valid, _test_strategy_valid
    test_scoring.py         # complexity_score(), template_compatibility_score(),
                            # persona_confidence(), effort_estimation()
    test_routing.py         # _convergence_routing(), _final_validation_score(),
                            # _should_revise(), _resolve_collisions()
    test_flag_validation.py # _validate_flags(), _validate_resume_from()
    test_agent_parsing.py   # Agent spec parsing (split on comma then colon)
```

Property-based tests (using Hypothesis):
- `complexity_score` always in [0.0, 1.0] for any non-negative inputs
- `_milestone_dag_acyclic` correctly rejects all cycles in randomly generated dependency graphs
- `_convergence_routing` is monotonic: higher scores never produce lower-tier decisions
- `_final_validation_score` aggregation is commutative-weighted (qe*0.55 + sr*0.45 always equals the formula)
- `_spec_source_mutex` rejects content with both `spec_source` and `spec_sources` fields

### Phase 2: Integration tests for pipeline compatibility

```
tests/pipeline/roadmap/
    test_step_graph.py      # Verify step graph construction produces valid
                            # list[Step | list[Step]] accepted by execute_pipeline()
    test_gate_integration.py # Verify gate functions integrate with gate_passed()
                            # via SemanticCheck wrappers
    test_subprocess.py      # Verify ClaudeProcess configuration for validation
                            # agents (read-only scoping, env isolation)
    test_state.py           # Verify state serialization/deserialization for resume
```

### Phase 3: Regression tests ensuring current behavior preserved

```
tests/pipeline/roadmap/
    test_wave_equivalence.py # For each wave, verify that the portified pipeline
                             # produces equivalent results to the skill-based execution
                             # on a fixed set of spec inputs
    test_adversarial.py      # Verify adversarial mode convergence routing matches
                             # the Wave 1A/2 behavior tables
    test_revise_loop.py      # Verify REVISE loop terminates correctly at max 2
                             # iterations with PASS_WITH_WARNINGS
    test_collision.py        # Verify collision resolution produces expected -N suffixes
```

### Phase 4: Property-based tests for determinism guarantees

```
tests/pipeline/roadmap/
    test_determinism.py     # Given identical inputs, programmatic functions produce
                            # identical outputs across 100 runs
    test_idempotency.py     # Running collision resolution twice does not double-suffix
    test_budget_bounds.py   # TurnLedger never allows negative budget
    test_gate_consistency.py # A gate that passes on content C always passes on C
                            # (no state dependency in gate functions)
```

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Prompt drift**: Claude-assisted steps produce output that passes gates but semantically diverges from current behavior | Medium | High | Freeze current SKILL.md prompts as baseline prompt contracts. Run Wave equivalence tests on a corpus of 5+ real specs before switching over. |
| **Gate over-fitting**: Strict gates reject valid output due to minor formatting variations | Medium | Medium | Start gates at STANDARD tier, promote to STRICT only after validation against real outputs. Include format-tolerance in semantic checks (e.g., accept both `M1` and `M01`). |
| **Budget estimation inaccuracy**: TurnLedger pre-launch guards block valid operations due to overestimated budgets | Low | Medium | Set budget estimates conservatively high initially, then calibrate from actual consumption data. Always allow a 20% buffer above estimate. |
| **Resume state corruption**: State file becomes inconsistent due to partial writes during crashes | Low | High | Use atomic file writes (write to temp file, then rename). Include checksum in state file header. On checksum mismatch, prompt user: start fresh or attempt recovery. |
| **Adversarial subprocess escape**: Adversarial agents modify files outside their scoped work directory | Low | High | Use `ClaudeProcess` with `--git-ceiling` and scoped work dir. Validate output directory contents before and after adversarial invocation. Alert on unexpected file creation. |
| **Ref loading regression**: Portified pipeline loads refs at wrong phase, causing context bloat or missing context | Medium | Medium | Preserve the existing ref loading summary table as a test fixture. Verify each Step's `inputs` list matches the expected refs for its wave. |
| **Serena fallback interaction**: Portified pipeline's file-based state conflicts with Serena's session memory | Low | Low | Choose one persistence mechanism per deployment. If CLI runner is active, disable Serena persistence for roadmap sessions. If skill mode is active, disable state files. |
| **Breaking change in pipeline primitives**: Changes to `PipelineConfig`, `Step`, or `gate_passed()` break roadmap integration | Low | High | Pin to pipeline module version. Use abstract interfaces where possible. Include pipeline compatibility check in CI. |
