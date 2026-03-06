# Refactoring Spec: sc:adversarial-protocol

Analysis of architectural uplift opportunities from cli-portify patterns and CLI runner pipeline optimization for the adversarial debate and merge pipeline.

---

## Current Architecture Assessment

### Current Step Count and Flow

The pipeline operates in three modes with the following step structure:

**Mode A/B Core Pipeline** (5 steps, strictly sequential):
1. **Diff Analysis** -- produces `diff-analysis.md`
2. **Adversarial Debate** -- produces `debate-transcript.md` (internal sub-steps: Round 1 parallel, Round 2 sequential, Round 2.5 invariant probe, Round 3 conditional)
3. **Hybrid Scoring and Base Selection** -- produces `base-selection.md`
4. **Refactoring Plan** -- produces `refactor-plan.md`
5. **Merge Execution** -- produces merged output + `merge-log.md`

**Mode B Pre-Step**: Parallel variant generation (N agents, 2-10)

**Pipeline Mode**: Meta-orchestrator that chains multiple Mode A/B passes with DAG-based phase dependencies.

Total artifact count per run: 5-7 intermediate artifacts plus final merged output.

### Current Validation Mechanisms

All validation is performed inside Claude's inference context. There is no programmatic output validation. Specific validation points that exist only as prompt instructions:

- Input mode parsing: flag mutual exclusivity checks, file existence, agent count bounds (2-10)
- Diff analysis assembly: section presence validation, ID sequence contiguity, metadata count consistency
- Debate output: advocate output format compliance, steelman requirement, shared assumption response completeness (A-NNN omission detection)
- Convergence detection: arithmetic formula (`agreed_points / total_diff_points`), taxonomy coverage gate, invariant probe gate
- Scoring: quantitative formula correctness, CEV protocol adherence, edge-case floor, dual-pass position bias mitigation
- Merge: structural integrity, internal reference resolution, contradiction re-scan
- Return contract: field completeness, write-on-failure guarantee

### Current Integration Points

- **MCP servers**: Sequential (Steps 2-4 scoring/analysis), Serena (Step 5 memory persistence), Context7 (Step 5 domain validation)
- **Agent delegation**: debate-orchestrator (coordinates Steps 1-5), advocate agents (Step 2, dynamic 2-10), merge-executor (Step 5), fault-finder (Round 2.5)
- **Tool usage**: Task (agent dispatch), Read/Write/Edit (file operations), Grep (scoring computations), Glob (file discovery)
- **Caller integration**: Return contract consumed by `/sc:roadmap` and other upstream commands

### Architectural Strengths to Preserve

1. **Well-defined artifact boundaries** -- Each step produces a named artifact with a documented template. This maps directly to Step/output_file in the pipeline model.
2. **Explicit data flow** -- Each step's inputs are clearly specified (variants -> diff-analysis -> debate-transcript -> base-selection -> refactor-plan -> merged output).
3. **Configurable depth** -- The quick/standard/deep depth parameter controls which rounds execute, providing natural step graph conditionals.
4. **Steelman protocol** -- The adversarial methodology (steelman before critique, CEV evidence protocol, position bias mitigation) is a genuine differentiator for output quality.
5. **Transparent scoring** -- The hybrid quantitative/qualitative approach with documented formulas and the 30-criterion rubric produce auditable decisions.
6. **Error handling taxonomy** -- The four error modes (agent_failure, variants_too_similar, no_convergence, merge_failure) cover the realistic failure space.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement** | HIGH | Extract quantitative scoring (RC, IC, SR, DC, SC), combined formula, tiebreaker cascade, edge-case floor, convergence arithmetic, taxonomy gate, and invariant probe gate into Python functions. Return contract field validation becomes a `GateCriteria` semantic check. | Medium (15-20 functions) | HIGH -- Currently all scoring runs inside inference. Claude can hallucinate intermediate arithmetic, skip edge-case floor checks, or compute convergence incorrectly. The quantitative layer is explicitly documented as "no LLM judgment involved" yet executes inside an LLM. |
| **(b) Pure-function gate criteria** | HIGH | Define gates for all 5 step artifacts plus invariant-probe.md. Semantic check functions: `_has_required_sections(content) -> tuple[bool, str]` for diff-analysis; `_all_rounds_present(content, expected) -> tuple[bool, str]` for debate-transcript; `_scoring_breakdown_present(content) -> tuple[bool, str]` for base-selection; `_all_improvements_have_rationale(content) -> tuple[bool, str]` for refactor-plan; `_provenance_annotations_present(content) -> tuple[bool, str]` for merged output. | Medium (12-15 check functions) | HIGH -- Without gates, a malformed Step 1 artifact propagates errors silently into Step 2, compounding across the pipeline. Currently nothing catches a missing "Shared Assumptions" section before debate advocates are asked to respond to A-NNN IDs that do not exist. |
| **(c) Classification rubric** | HIGH | See "Pipeline Optimization Plan" section below. The skill has an unusually clear programmatic/inference split because the scoring protocol itself documents which computations are deterministic. | Low (taxonomy already exists in spec) | MEDIUM -- Without classification, implementers will default to running everything as inference, missing the quantitative layer optimization. |
| **(d) Step graph with dependency resolution** | HIGH | 8 steps in the step graph: [0] input validation (programmatic), [1] variant generation (parallel, Mode B only), [2] diff analysis (Claude-assisted), [3] debate rounds (Claude, internal sub-graph), [4] invariant probe (Claude, conditional), [5] scoring and base selection (hybrid), [6] refactoring plan (Claude), [7] merge execution (Claude). Step 3 has an internal sub-graph: [3a] Round 1 (parallel group), [3b] Round 2 (sequential, conditional on depth), [3c] Round 3 (conditional on depth AND convergence). | Medium (step graph definition + conditional logic) | MEDIUM -- Without explicit dependency resolution, the current implicit sequencing works but cannot support resume/retry at sub-step granularity. |
| **(e) Resume/retry** | CRITICAL | Adversarial debates are the most expensive operation in SuperClaude. A 5-agent x 3-round debate at depth=deep represents 15+ subprocess invocations. If scoring fails after a successful debate, re-running the entire debate wastes significant compute. Resume commands: `superclaude adversarial --resume-from scoring --artifacts-dir <dir>` would reload debate-transcript.md and re-execute from Step 5 onward. Each step's artifact serves as a natural checkpoint. | Medium-High (checkpoint serialization, resume CLI parsing) | CRITICAL -- This is the single highest-ROI pattern. A failed merge after a 15-agent-turn debate currently forces a full restart. With typical debate costs of 50K-200K tokens, resume saves 80-95% of rerun cost. |
| **(f) TurnLedger budget** | CRITICAL | Budget formula: Mode B generation (N agents x ~5 turns each) + Round 1 (N agents x 1 turn) + Round 2 (N agents x 1 turn) + Round 2.5 (1 agent x 1 turn) + Round 3 (N agents x 1 turn, conditional) + scoring (1 orchestrator turn) + refactoring plan (1 turn) + merge (1 agent x ~3 turns). For N=5, depth=deep: ~35-40 turns minimum. Pre-launch guards prevent initiating Round 3 if budget is exhausted. Budget reimbursement for skipped rounds (depth=quick skips Rounds 2-3, reimbursing ~N*2 turns). | Medium (TurnLedger integration, per-step debit, guard checks) | CRITICAL -- Without budget tracking, a 10-agent deep debate can consume unbounded turns. The skill currently has no mechanism to detect or prevent runaway costs. A user running `--agents opus,opus,opus,opus,opus,opus,opus,opus,opus,opus --depth deep` would spawn 30+ agent invocations with no cost visibility. |
| **(g) Diagnostic chain** | HIGH | Map the 4 existing error modes to a `FailureClassifier`: `AGENT_FAILURE` (retry once then N-1), `VARIANTS_TOO_SIMILAR` (skip debate), `NO_CONVERGENCE` (force-select), `MERGE_FAILURE` (preserve artifacts). Add: `SCORING_FAILURE` (quant/qual computation error), `GATE_FAILURE` (artifact malformed), `BUDGET_EXHAUSTED` (TurnLedger guard triggered). Each produces a `DiagnosticReport` with: failure stage, partial results available, specific resume command, estimated cost to resume. | Medium (FailureClassifier enum, report generation, resume command formatting) | HIGH -- Current error handling is inline prompt instructions. Claude may not consistently follow the retry-once-then-N-1 protocol. Programmatic failure classification ensures deterministic error behavior. |
| **(h) 4-layer subprocess isolation** | HIGH | Layer 1 (scoped work dir): Each advocate agent operates on read-only copies in `adversarial/`. Layer 2 (git ceiling): Advocate agents must not access git history or modify tracked files. Layer 3 (isolated plugin dir): Prevents advocate agents from invoking other skills or modifying framework state. Layer 4 (isolated settings): Prevents configuration drift between agents in parallel dispatch. The merge-executor (Step 5) gets write access ONLY to the output directory. | Medium (ClaudeProcess configuration per agent type) | HIGH -- An advocate agent with unrestricted file access could modify another variant's file during parallel Round 1, corrupting the debate. The merge-executor could modify source files outside the adversarial directory. |
| **(i) Context injection** | HIGH | Define typed interfaces: `DiffAnalysisResult` (section counts, diff point IDs, severity distribution, shared assumption IDs), `DebateResult` (per-point winners, convergence score, taxonomy coverage, invariant probe results), `ScoringResult` (quant_scores per variant, qual_scores per variant, combined scores, selected base, tiebreaker used), `RefactoringPlan` (changes list with source/target/rationale, rejected changes). Serialize as YAML frontmatter in each artifact. Downstream steps parse frontmatter rather than re-reading full artifacts. | Medium (dataclass definitions, YAML serialization, frontmatter parsing) | MEDIUM -- Current implicit context passing works but is lossy. When Step 5 (scoring) reads the full debate-transcript.md, it re-interprets the document rather than consuming structured data. This introduces interpretation drift: Claude may read the same transcript differently in scoring vs. in refactoring plan generation. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Input validation and mode detection** | Inference (Claude parses flags) | Pure Programmatic | EXEMPT (pre-pipeline) | Flag parsing, file existence checks, agent spec validation, count bounds (2-10), mutual exclusivity checks are all deterministic string/file operations. No inference needed. Implement as `AdversarialConfig` extending `PipelineConfig` with validation in `__post_init__`. |
| **Mode B variant generation** | Inference (N parallel Task agents) | Claude-Assisted (parallel Step group) | STANDARD: `_variant_has_frontmatter(content)`, `_variant_min_length(content, threshold)`, `_variant_matches_type(content, generate_type)` | Each variant generation is an independent Claude subprocess. Natural parallel `list[Step]` group. Gate ensures each variant meets minimum structural requirements before proceeding to diff analysis. |
| **Step 1: Structural diff** | Inference (Claude compares headings) | Programmatic + Validation | STRICT: `_has_structural_section(content)`, `_severity_ratings_present(content)`, `_id_sequence_contiguous(content, 'S-')` | Heading extraction (`^#{1,6} ` regex), hierarchy comparison, section ordering comparison are pure text operations. Severity assignment needs inference only for borderline cases. Implement as Python function with Claude fallback for edge cases. |
| **Step 1: Content diff** | Inference | Claude-Assisted | (combined into diff-analysis gate) | Topic extraction uses fuzzy matching (>=60% word overlap), but approach comparison requires semantic understanding. Keep as Claude subprocess. |
| **Step 1: Contradiction detection** | Inference | Claude-Assisted | (combined into diff-analysis gate) | Requires reasoning about claim compatibility. Keep as Claude subprocess. |
| **Step 1: Shared assumption extraction** | Inference | Claude-Assisted | (combined into diff-analysis gate) | Requires reasoning about implicit preconditions. Keep as Claude subprocess. |
| **Step 1: diff-analysis.md assembly** | Inference | Programmatic + Validation | STRICT: `_has_all_five_sections(content)`, `_metadata_counts_match(content)`, `_shared_assumptions_section_exists(content)`, `_id_sequences_contiguous(content)` | Assembly of sub-component outputs into final artifact is templated. The gate validates structural completeness programmatically. |
| **Step 2: Round 1 (parallel advocates)** | Inference (parallel Task dispatch) | Claude-Assisted (parallel Step group) | STANDARD per advocate: `_has_steelman_section(content)`, `_has_evidence_citations(content)`, `_shared_assumption_responses_complete(content, expected_ids)` | Each advocate is an independent Claude subprocess. Natural parallel `list[Step]` group with N steps. Gate validates steelman requirement and A-NNN response completeness per advocate. |
| **Step 2: Round 2 (sequential rebuttals)** | Inference (sequential Task dispatch) | Claude-Assisted (sequential steps) | STANDARD per advocate: `_addresses_prior_criticisms(content)`, `_has_updated_assessment(content)` | Sequential because each rebuttal requires all prior transcripts. N sequential steps with context injection from Round 1. |
| **Step 2: Convergence detection** | Inference (Claude computes percentage) | Pure Programmatic | N/A (inline computation) | `convergence = agreed_points / total_diff_points` is arithmetic. Taxonomy coverage gate is boolean logic. Invariant probe gate is filter + count. All three are pure functions. Extract to: `compute_convergence(per_point_tracking) -> float`, `taxonomy_covered(per_point_tracking) -> bool`, `invariants_blocking(probe_results) -> list[str]`. |
| **Step 2: Round 2.5 (invariant probe)** | Inference | Claude-Assisted | STANDARD: `_has_five_categories(content)`, `_findings_well_formed(content)`, `_status_values_valid(content)` | Fault-finding requires creative reasoning. Gate validates output format (INV-NNN IDs, valid Status/Severity values). |
| **Step 2: Round 3 (conditional final arguments)** | Inference | Claude-Assisted | STANDARD: `_has_final_position(content)`, `_remaining_disagreements_listed(content)` | Same pattern as Round 2. Conditional on depth=deep AND convergence < threshold. |
| **Step 2: debate-transcript.md assembly** | Inference | Programmatic + Validation | STRICT: `_all_rounds_present(content, expected_rounds)`, `_scoring_matrix_complete(content)`, `_convergence_documented(content)` | Concatenation of round outputs with metadata header is templated. Gate validates completeness. |
| **Step 3: Quantitative scoring** | Inference (Claude runs grep-match formulas) | Pure Programmatic | N/A (inline computation) | RC (grep-match requirement IDs), IC (contradiction counting), SR (concrete/vague statement ratio), DC (internal reference resolution), SC (section count ratio) are ALL documented as "No LLM judgment involved." Implement as: `compute_quant_score(variant_content, source_content) -> QuantScoreBreakdown`. The weighted formula `(RC*0.30)+(IC*0.25)+(SR*0.15)+(DC*0.15)+(SC*0.15)` is pure arithmetic. |
| **Step 3: Qualitative scoring** | Inference | Claude-Assisted | STANDARD: `_cev_protocol_followed(content)`, `_all_30_criteria_scored(content)`, `_no_partial_credit(content)` | The 30-criterion binary rubric requires inference for each CEV assessment. Gate validates that all 30 criteria have verdicts and that no partial credit was awarded. |
| **Step 3: Position bias mitigation** | Inference (Claude runs dual pass) | Programmatic orchestration + Claude content | N/A (orchestration logic) | The dual-pass is an orchestration concern: run qualitative evaluation twice (forward order, reverse order), then compare. Agreement detection is string matching. Disagreement re-evaluation is inference. Implement as: `orchestrate_dual_pass(variants) -> list[tuple[CriterionID, Verdict]]` that dispatches two Claude subprocesses and reconciles results programmatically. |
| **Step 3: Combined scoring + tiebreaker + floor** | Inference | Pure Programmatic | N/A (inline computation) | `variant_score = (0.50 * quant_score) + (0.50 * qual_score)` is arithmetic. Tiebreaker cascade (5% margin check -> debate performance -> correctness count -> input order) is deterministic. Edge-case floor (Invariant & Edge Case Coverage >= 1/5) is a comparison. Implement as: `select_base(quant_scores, qual_scores, debate_performance) -> BaseSelection`. |
| **Step 3: base-selection.md assembly** | Inference | Programmatic + Validation | STRICT: `_scoring_breakdown_present(content)`, `_dual_pass_evidence(content)`, `_edge_case_floor_documented(content)`, `_tiebreaker_documented(content)` | Assembly from computed scores is templated. Gate validates all required sections. |
| **Step 4: Refactoring plan** | Inference | Claude-Assisted | STANDARD: `_all_improvements_have_rationale(content)`, `_integration_points_specified(content)`, `_changes_not_made_section(content)` | Selecting which non-base strengths to incorporate and how to integrate them requires judgment. Gate validates structural completeness. |
| **Step 5: Merge execution** | Inference | Claude-Assisted | STRICT: `_provenance_annotations_present(content)`, `_no_new_contradictions(content, diff_analysis)`, `_structural_integrity_check(content)`, `_internal_references_resolve(content)` | Content integration requires inference. Gate validates merge quality programmatically. The contradiction re-scan and internal reference resolution checks can be partially programmatic (section reference resolution is string matching). |
| **Return contract** | Inference (Claude writes YAML) | Pure Programmatic | N/A (post-pipeline) | Field population from step results is deterministic. Implement as: `build_return_contract(step_results, config) -> ReturnContract`. Write-on-failure guarantee becomes a `finally` block. |

---

## Portification Candidacy

**Recommendation: Selective Adoption**

### Justification

Full portification is inappropriate because the adversarial protocol's value proposition is fundamentally inference-dependent. The debate content (advocate arguments, steelman constructions, CEV criterion evaluations, refactoring plan decisions, merge execution) cannot be replaced by programmatic functions without destroying the skill's purpose.

However, selective adoption of cli-portify patterns yields outsized returns for three reasons:

**1. The orchestration/content boundary is unusually clean.** The skill itself documents this boundary explicitly: the quantitative scoring layer states "No LLM judgment is involved in this layer." The convergence formula, taxonomy gate, invariant probe gate, tiebreaker cascade, and edge-case floor are all specified as deterministic. This is not a judgment call about what *could* be programmatic -- the spec already classifies these as non-inference operations that happen to run inside inference.

**2. The cost multiplier is the highest in the framework.** With 2-10 agents, 1-3 rounds, plus fault-finder, scoring, and merge, a single adversarial run can spawn 15-35 agent invocations. Resume/retry and TurnLedger integration prevent the single most expensive failure mode in the entire SuperClaude skill set: re-running a completed debate because a downstream scoring or merge step failed.

**3. Gate validation prevents cascading artifact corruption.** Each step consumes the prior step's artifact. A malformed diff-analysis.md (missing Shared Assumptions section) causes advocates in Step 2 to receive prompts referencing A-NNN IDs that do not exist, producing debate transcripts that cannot be scored, producing scoring artifacts that miscount convergence. A single gate at Step 1's output prevents this entire cascade.

### What Gets Portified

- Input validation and config construction (Step 0)
- Quantitative scoring computation (Step 3 partial)
- Combined scoring formula, tiebreaker, edge-case floor (Step 3 partial)
- Convergence detection, taxonomy gate, invariant probe gate (Step 2 inter-round)
- Return contract assembly (Step 5 post)
- Step graph definition with conditional round logic
- Gate criteria for all 5+ artifacts
- TurnLedger budget tracking
- Resume/retry with checkpoint artifacts
- Subprocess isolation for advocate and merge-executor agents
- Diagnostic chain with failure classification

### What Stays as Inference

- Content diff analysis, contradiction detection, shared assumption extraction (Step 1 partial)
- All advocate debate content: arguments, steelman constructions, rebuttals, final positions (Step 2)
- Fault-finder invariant probing (Round 2.5)
- Qualitative rubric evaluation via CEV protocol (Step 3 partial)
- Position bias disagreement re-evaluation (Step 3 partial)
- Refactoring plan generation (Step 4)
- Merge execution with provenance annotation (Step 5)

### Estimated Split

- **Pure Programmatic**: ~35% of pipeline logic (input validation, quant scoring, formula computation, convergence arithmetic, gates, return contract, budget tracking)
- **Programmatic Orchestration with Claude Content**: ~25% (dual-pass dispatch, round sequencing, parallel advocate dispatch, conditional round logic)
- **Pure Inference**: ~40% (debate content, qualitative evaluation, refactoring decisions, merge execution)

---

## Testing Plan

### Phase 1: Unit Tests for Programmatic Functions

Target: All functions extracted from inference into Python code.

| Function | Test Cases | Property |
|----------|-----------|----------|
| `compute_requirement_coverage(variant, source)` | Empty source, no matches, partial matches, full matches, keyword fallback | RC in [0.0, 1.0], monotonic with more matches |
| `compute_internal_consistency(variant)` | No claims, no contradictions, all contradictions, mixed | IC in [0.0, 1.0], IC=1.0 when contradictions=0 |
| `compute_specificity_ratio(variant)` | All concrete, all vague, mixed, excluded lines skipped | SR in [0.0, 1.0] |
| `compute_dependency_completeness(variant)` | No refs, all resolved, broken refs, external refs excluded | DC in [0.0, 1.0] |
| `compute_section_coverage(variant, all_variants)` | Single variant (SC=1.0), fewer sections, equal sections | SC in [0.0, 1.0], max variant always 1.0 |
| `compute_quant_score(metrics)` | Boundary values, weight sum = 1.0, all zeros, all ones | Score in [0.0, 1.0] |
| `compute_combined_score(quant, qual)` | Equal weights, boundary values | Score = 0.5*quant + 0.5*qual |
| `apply_tiebreaker(scores, debate_perf)` | No tie, tie within 5%, tie at all three levels | Deterministic winner, level 3 = input order |
| `apply_edge_case_floor(qual_scores)` | Above floor, below floor, all zero (suspend) | Ineligible variants excluded, suspension warning |
| `compute_convergence(tracking)` | All agreed, none agreed, with A-NNN points | Convergence in [0.0, 1.0] |
| `check_taxonomy_coverage(tracking)` | All levels covered, L3 missing, all missing | Boolean + list of uncovered levels |
| `check_invariant_gate(probe_results)` | No findings, HIGH+UNADDRESSED present, only MEDIUM | Boolean + blocking item IDs |
| `build_return_contract(results, config)` | Success path, each failure stage, null field handling | All fields present, write-on-failure guarantee |
| Gate check functions (12-15) | Well-formed artifacts, missing sections, malformed IDs | tuple[bool, str] return, specific failure messages |

### Phase 2: Integration Tests for Pipeline Compatibility

- Step graph execution with conditional rounds (depth=quick skips Rounds 2/2.5/3)
- Parallel dispatch of N advocate steps via `_run_parallel_steps()`
- Gate failure at each step triggers correct halt behavior
- TurnLedger debit/guard integration prevents launch when budget exhausted
- Resume from checkpoint: simulate failure at Step 3 scoring, verify resume from `base-selection` step reloads `debate-transcript.md`
- Context injection: verify frontmatter from Step 1 artifact is correctly parsed by Step 2 prompt construction
- Subprocess isolation: verify advocate agents cannot write outside `adversarial/` directory

### Phase 3: Regression Tests for Current Behavior

- Mode A with 2 files, depth=standard produces equivalent artifacts to current skill
- Mode B with 3 agents, depth=deep produces equivalent artifacts to current skill
- Error handling: agent_failure retry-once-then-N-1 behavior preserved
- Error handling: variants_too_similar (<10% diff) skips debate
- Error handling: no_convergence force-selects by score
- Return contract field values match current spec for success, partial, and failed cases
- Convergence with A-NNN shared assumption points included in denominator
- Taxonomy coverage gate blocks convergence when L3 has zero coverage
- Invariant probe HIGH+UNADDRESSED blocks convergence

### Phase 4: Property-Based Tests for Determinism Guarantees

| Property | Scope | Method |
|----------|-------|--------|
| Quantitative scoring is deterministic | Same variant text always produces same quant_score | Hypothesis: generate variant text, assert `compute_quant_score(v) == compute_quant_score(v)` |
| Combined score formula is commutative in variant ordering | Score does not change based on which variant is evaluated first | Hypothesis: permute variant order, assert same final scores |
| Tiebreaker is total ordering | For any set of scores, exactly one winner is selected | Hypothesis: generate N score tuples, assert `len(select_base(scores)) == 1` |
| Edge-case floor is monotonic | Adding a met criterion never decreases eligibility | Hypothesis: generate criterion scores, assert `floor_pass(scores + [1]) >= floor_pass(scores)` |
| Convergence is monotonic in agreements | More agreed points never decreases convergence | Hypothesis: generate tracking data, assert `convergence(tracking + [agreed]) >= convergence(tracking)` |
| Return contract always has all fields | Every execution path (success, partial, failed) populates all contract fields | Hypothesis: generate step result combinations, assert all fields non-None or explicitly null per spec |
| Gate functions are pure | Same content always produces same (bool, str) result | Hypothesis: generate artifact content, assert `gate(c) == gate(c)` |
| Budget is monotonically consumed | Debit operations never decrease consumed count | Property from existing TurnLedger tests, extended to adversarial budget formulas |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Quantitative metric extraction produces different results than Claude's in-context computation** | Medium | HIGH -- Scoring divergence changes which variant is selected as base, altering the entire merge outcome | Parallel run period: execute both programmatic and inference scoring for 10-20 adversarial runs, compare results. Quantitative metrics use the same grep-match and counting logic described in the spec. Divergence indicates either a spec ambiguity or an implementation bug. |
| **Gate validation rejects artifacts that the current skill accepts** | Medium | MEDIUM -- Gates that are too strict cause pipeline halts for previously acceptable outputs | Start with STANDARD tier gates (structural checks only). Promote to STRICT after calibrating against 5+ real adversarial runs. Log gate results without blocking during calibration period. |
| **Resume/retry reloads stale context** | Low | HIGH -- Resuming from a checkpoint with outdated variant files produces inconsistent results | Checkpoint includes content hashes for all input artifacts. Resume validates hashes before proceeding. Hash mismatch forces re-execution from the last step with matching inputs. |
| **TurnLedger budget estimates are miscalibrated** | Medium | MEDIUM -- Over-conservative budgets halt pipelines prematurely; under-conservative budgets do not prevent runaway costs | Start with generous budgets (2x estimated turns) and track actual consumption. Adjust `minimum_allocation` and `minimum_remediation_budget` based on empirical data. Log budget utilization ratio per run. |
| **Subprocess isolation breaks advocate prompt injection** | Low | MEDIUM -- Advocate agents rely on reading variant files and diff-analysis.md. Over-isolation prevents access to required inputs | Isolation allows read access to `adversarial/` directory contents. Write access restricted to the agent's own output file. Test with real advocate prompts during integration testing. |
| **Parallel Round 1 dispatch exceeds system resource limits** | Low (2-5 agents), Medium (6-10 agents) | MEDIUM -- ThreadPoolExecutor with 10 concurrent Claude subprocesses may exhaust system resources | Use `--pipeline-parallel` (default 3) as the concurrency cap for advocate dispatch. Queue excess agents. This matches the existing pipeline mode parallel limit. |
| **Qualitative dual-pass orchestration changes scoring outcomes** | Medium | HIGH -- Programmatic reconciliation of forward/reverse pass disagreements may differ from Claude's in-context reconciliation | The disagreement case still invokes Claude for re-evaluation. Only the agreement case (both passes agree) uses programmatic reconciliation (identity check). Log all disagreement re-evaluations for audit. |
| **Step graph conditional logic (depth-based round skipping) introduces bugs in convergence tracking** | Low | MEDIUM -- Skipping Round 2 at depth=quick must correctly handle the case where convergence is computed with only Round 1 data | Explicit test cases for each depth level: quick (Round 1 only + forced taxonomy round if needed), standard (Rounds 1-2 + Round 2.5), deep (Rounds 1-3 + Round 2.5). |
| **Migration period: skill users receive different results from portified vs. non-portified runs** | Medium | HIGH -- If the portified pipeline and the current skill produce materially different merge outputs for the same inputs, user trust erodes | Feature-flag the portified pipeline. Default to current skill behavior. Users opt in with `--pipeline-runner` flag. Parity testing over 10+ runs before making portified the default. |
| **Context injection frontmatter parsing fails on edge cases** | Low | LOW -- Malformed YAML frontmatter in artifacts causes downstream parsing errors | The existing `_check_frontmatter()` function in `src/superclaude/cli/pipeline/gates.py` handles this pattern. Reuse the same parsing logic. Gate at each step validates frontmatter before downstream consumption. |

---

## Appendix: Programmatic vs. Inference Classification Detail

For reference, the complete sub-step classification used to derive the Pipeline Optimization Plan:

```
PURE PROGRAMMATIC (extract to Python):
  - Input mode parsing (flag detection, mutual exclusivity, file existence)
  - Agent spec parsing (colon-separated format, model/persona/instruction extraction)
  - Config validation (count bounds 2-10, convergence range 0.50-0.99, depth enum)
  - Output directory creation and naming convention
  - Structural diff: heading extraction (regex ^#{1,6}), hierarchy tree construction
  - Structural diff: section ordering comparison (sequence alignment)
  - Quantitative scoring: RC (grep-match requirement IDs)
  - Quantitative scoring: IC (contradiction count / total claims)
  - Quantitative scoring: SR (concrete indicator count / total statements)
  - Quantitative scoring: DC (resolved references / total references)
  - Quantitative scoring: SC (section count / max section count)
  - Quantitative formula: weighted sum
  - Combined score formula: 0.50 * quant + 0.50 * qual
  - Tiebreaker cascade: 5% margin check -> debate points -> correctness -> input order
  - Edge-case floor: Invariant dimension score >= 1/5
  - Edge-case floor suspension: all variants score 0/5
  - Convergence formula: agreed_points / total_diff_points
  - Taxonomy coverage gate: all three levels have > 0 addressed points
  - Invariant probe gate: count(HIGH + UNADDRESSED) == 0
  - Return contract assembly: field population from step results
  - Return contract write-on-failure: finally block guarantee
  - Dual-pass agreement detection: forward verdict == reverse verdict
  - A-NNN omission detection: set difference of expected vs. found IDs
  - ID sequence contiguity validation
  - Metadata count consistency validation

PROGRAMMATIC ORCHESTRATION (Python controls flow, Claude generates content):
  - Mode B variant generation dispatch (parallel Task group)
  - Round 1 advocate dispatch (parallel Task group)
  - Round 2 advocate dispatch (sequential, ordered)
  - Round 3 advocate dispatch (conditional on depth AND convergence)
  - Round 2.5 fault-finder dispatch (conditional on depth)
  - Forced taxonomy round dispatch (conditional on zero-coverage level)
  - Dual-pass qualitative evaluation dispatch (forward then reverse)
  - Dual-pass disagreement re-evaluation dispatch (for disagreeing criteria)
  - Merge-executor dispatch
  - TurnLedger debit/guard per dispatch
  - Convergence check after each round (compute + decide next action)

PURE INFERENCE (Claude subprocess):
  - Content diff: topic-by-topic approach comparison
  - Contradiction detection: claim extraction, compatibility reasoning
  - Unique contribution extraction: value assessment
  - Shared assumption extraction: precondition identification, classification
  - All advocate arguments: strengths, steelman, critiques, concessions
  - All advocate rebuttals: responding to criticisms, updated assessments
  - Fault-finder probing: invariant violation identification
  - Qualitative rubric: 30-criterion CEV evaluation per variant
  - Refactoring plan: improvement selection, integration approach, risk assessment
  - Merge execution: content integration, provenance annotation
  - Post-merge validation: structural integrity reasoning, contradiction re-scan reasoning
```
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
# Refactoring Spec: sc:tasklist-protocol

**Date**: 2026-03-06
**Scope**: Dual-lens architectural analysis -- cli-portify pattern adoption + CLI runner pipeline optimization
**Target**: `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` (v3.0)
**Reference**: `src/superclaude/skills/sc-cli-portify/SKILL.md` + `src/superclaude/cli/pipeline/`

---

## Current Architecture Assessment

### Current Step Count and Flow

The skill executes as a single Claude inference session across 6 sequential stages:

| Stage | Name | Mode | Primary Work |
|-------|------|------|-------------|
| 1 | Input Ingest | Read file, parse text | Read roadmap, identify sections |
| 2 | Parse + Phase Bucketing | Regex splitting, heading detection | Split into R-### items, assign to phase buckets |
| 3 | Task Conversion | Rule application + content generation | Convert items to T-format tasks with steps, criteria |
| 4 | Enrichment | Deterministic scoring + inference | Effort/Risk/Tier/Confidence computation, MCP tools, deliverable IDs |
| 5 | File Emission | Template filling + Write calls | mkdir + Write tasklist-index.md + phase-N-tasklist.md files |
| 6 | Self-Check | 17-point validation | Sprint compatibility, semantic, structural quality gates |

**Total stages**: 6, strictly sequential, all executed within one Claude session.

### Current Validation Mechanisms

**17-point self-check** (all executed as LLM self-referential validation):

- **Sprint Compatibility (checks 1-8)**: Index file exists, phase files referenced, contiguous phase numbers, valid T-format IDs, correct phase headings, end-of-phase checkpoints, no cross-phase metadata leakage, literal filenames in index.
- **Semantic Quality Gate (checks 9-12)**: Non-empty enrichment fields, globally unique D-#### IDs, no placeholder descriptions, roadmap item traceability.
- **Structural Quality Gate (checks 13-17)**: Task count bounds per phase, clarification task adjacency, circular dependency detection, XL splitting enforcement, confidence bar format consistency.

**Gate behavior**: Structural gates are designated "blocking" and semantic gates "advisory," but both are enforced only through inference -- there is no programmatic enforcement mechanism.

### Current Integration Points

- **Tool usage**: Read (stage 1), Grep (stage 2), Write (stage 5), Bash/mkdir (stage 5), Glob (stage 6), TodoWrite (stages 1-6)
- **MCP**: Sequential (optional, tier classification ambiguity), Context7 (optional, framework pattern validation)
- **Downstream consumer**: `superclaude sprint run` -- reads the generated phase-N-tasklist.md files via regex phase discovery

### Architectural Strengths to Preserve

1. **Deterministic algorithm specification**: The SKILL.md is exceptionally precise about its generation rules. Effort scoring, risk scoring, tier classification, and phase numbering are fully specified as deterministic algorithms with no discretionary choices. This precision is the skill's core value.
2. **Atomic write constraint**: The bundle is validated in-memory before any Write call. This is a sound design principle.
3. **Traceability chain**: R-### to T-format to D-#### with cross-referencing in registries and matrix is well-designed for auditability.
4. **Sprint CLI compatibility**: Output format is tightly coupled to sprint CLI regex expectations. Any refactoring must preserve this contract exactly.
5. **Clarification task pattern**: The mechanism for handling missing information (inserting clarification tasks rather than guessing) is a disciplined approach worth preserving.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement over self-referential LLM validation** | **High**. 14 of 17 self-checks are structurally verifiable (regex, counting, format matching). The LLM checking its own work is unreliable -- it may "pass" checks it actually violated. | Implement 14 Python functions in a `gates.py` module. Each reads the written markdown files and returns `tuple[bool, str]`. Run after stage 5 (File Emission). Checks 9 (non-empty fields), 10 (unique D-IDs), 13 (task count bounds), and 15 (circular deps) require cross-file analysis. Checks 11 (no placeholders), 12 (orphan tasks), 14 (clarification adjacency) are single-file regex. Checks 1-8 are file-existence and format checks. Only checks related to "content quality" (parts of check 11: is the description actually meaningful?) and "task specificity" (the generation-time sub-checks: named artifact, imperative verb) genuinely require inference. | **Medium** (2-3 days). Each check is a straightforward Python function operating on markdown text. Most are 10-30 lines. | **High**. Without programmatic enforcement, the self-check is theater -- the LLM will report "all 17 checks passed" even when violations exist. This is the single highest-value pattern to adopt. Observed failure modes include: duplicate D-IDs across phases, non-contiguous phase numbers after gap correction, missing end-of-phase checkpoints, and malformed T-format IDs. |
| **(b) Pure-function gate criteria: `(str) -> tuple[bool, str]`** | **High**. Direct mapping from the 17 checks to typed functions. | Define in `src/superclaude/cli/tasklist/gates.py`. Examples: `_phase_numbers_contiguous(content: str) -> tuple[bool, str]`, `_task_ids_valid_format(content: str) -> tuple[bool, str]`, `_deliverable_ids_unique(index_content: str, phase_contents: list[str]) -> tuple[bool, str]`, `_end_of_phase_checkpoint_present(content: str) -> tuple[bool, str]`, `_no_cross_phase_metadata(content: str) -> tuple[bool, str]`, `_task_count_bounds(content: str, min_tasks: int, max_tasks: int) -> tuple[bool, str]`, `_confidence_bar_format(content: str) -> tuple[bool, str]`. Wire into `SemanticCheck` dataclass from pipeline models. | **Low** (1-2 days). Functions are trivial regex/parsing operations. | **Medium**. Without typed gate functions, any future pipeline integration lacks the validation hooks it needs. The function signatures also serve as executable documentation of the self-check contract. |
| **(c) Classification rubric: programmatic vs inference** | **High**. The skill mixes heavily deterministic work (scoring, ID assignment, template filling) with genuinely inference-dependent work (understanding roadmap prose, generating task descriptions, creating acceptance criteria). | See Pipeline Optimization Plan below for per-stage classification. Summary: Stages 1, 2, 4 (scoring only), 5, 6 are largely or fully programmatic. Stage 3 (task content generation) and stage 4 (acceptance criteria, step generation) require inference. | **Low** (analysis only, no code). Classification informs which stages benefit from portification. | **Low** immediate risk, but skipping this analysis means future portification efforts will misclassify stages, either over-automating (losing inference quality) or under-automating (keeping unreliable self-checks). |
| **(d) Step graph with dependency resolution** | **Medium**. The 6 stages are strictly sequential with no parallelism opportunities in the current design. However, modeling them as a step graph enables the executor to manage retry, resume, and gate evaluation. Stage 4 (Enrichment) is internally decomposable: tier classification is a pure function that could run as a programmatic step separate from the inference-based enrichment. | Model as 7-8 steps in a `Step` graph: `ingest -> parse -> bucket -> convert_tasks (Claude) -> enrich_scores (programmatic) -> enrich_content (Claude) -> emit_files (programmatic) -> validate (programmatic)`. Dependencies are linear. No parallel groups needed for the current design, though batch parallelism over phase files during emission could be added later. | **Medium** (1-2 days for step definitions). | **Low**. The current sequential flow works. Step graph becomes valuable only when combined with resume/retry (pattern e) or subprocess isolation (pattern h). |
| **(e) Resume/retry with exact CLI resume commands** | **Medium**. If file emission (stage 5) fails partway through writing N+1 files, the current skill has no mechanism to resume. It must regenerate everything from scratch. For large roadmaps (10+ phases, 50+ tasks), this wastes significant inference budget. | Implement checkpoint serialization: after each stage, serialize intermediate state (parsed items, phase buckets, task stubs, enriched tasks) to a JSON file in a `.tasklist-work/` directory. On resume, detect the last successful checkpoint and resume from there. Resume command: `superclaude tasklist --resume .tasklist-work/checkpoint.json`. | **Medium-High** (2-3 days). Requires defining serializable intermediate representations for each stage boundary. | **Low-Medium**. The skill typically runs in 1-3 minutes for moderate roadmaps. Resume matters most for very large roadmaps or when Claude subprocess budget is constrained. |
| **(f) Budget economics via TurnLedger** | **Low** (current design). The skill runs as a single Claude session, so there is no multi-subprocess budget to track. | Becomes relevant only if the skill is portified with subprocess stages. In that case, integrate `TurnLedger` with debit/credit for each Claude-assisted step (task conversion, content enrichment). Pre-launch guards would prevent starting a new phase's task conversion if budget is exhausted. | **Low** (piggybacks on portification if done). | **Negligible** in current architecture. The single-session model has implicit budget management via Claude's own turn limits. |
| **(g) Diagnostic chain** | **Medium**. Currently if the self-check fails, the LLM tries to fix it inline -- an unreliable approach. A proper diagnostic chain would: (1) classify failures as structural (fixable programmatically), semantic (needs LLM re-generation of specific section), or content (roadmap ambiguity requiring clarification), then (2) route to appropriate remediation. | Implement `DiagnosticCollector` that captures all gate failures. `FailureClassifier` maps each failure to a remediation strategy: structural failures get programmatic fixes (renumber phases, regenerate IDs), semantic failures trigger targeted re-prompting of the specific task/section, content failures produce clarification task insertions. `ReportGenerator` produces a diagnostic summary if remediation fails. | **Medium** (2-3 days). Requires defining failure taxonomy and remediation strategies. | **Medium**. Without diagnostics, failures during self-check result in the LLM either silently ignoring the failure or attempting ad-hoc fixes that may introduce new violations. |
| **(h) 4-layer subprocess isolation** | **Low**. Only relevant if stages are decomposed into child Claude sessions. The current single-session design does not need isolation. | If portified: stages 3 (task conversion) and 4 (content enrichment) would run as isolated `ClaudeProcess` instances with scoped work directories, git ceiling, isolated plugin/settings dirs. Each subprocess receives only the context it needs (parsed items for stage 3, task stubs for stage 4). | **Medium** (1-2 days, but only if portifying). | **Negligible** in current architecture. Relevant only for full portification. |
| **(i) Context injection for inter-step data flow** | **High**. The stages have implicit data flow: parsed items (stage 1-2) feed task conversion (stage 3), which feeds enrichment (stage 4), which feeds emission (stage 5). Currently this data exists only in the LLM's context window. If the context window fills or the LLM loses track, data is silently lost. | Define typed intermediate data structures: `ParsedRoadmapItem(id: str, text: str, phase_bucket: int)`, `TaskStub(id: str, title: str, roadmap_items: list[str], phase: int)`, `EnrichedTask(...)` with all scoring fields. Serialize to JSON at stage boundaries. Inject into subsequent prompts or programmatic steps. | **Medium** (2 days). Requires defining dataclasses for each stage boundary. | **Medium**. Without explicit data flow, the LLM may silently drop roadmap items during conversion, lose deliverable IDs during enrichment, or produce inconsistent cross-references. Typed intermediates make data loss detectable. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Stage 1: Input Ingest** | Inference (Read + parse) | **Pure programmatic** | `LIGHT`: file exists, non-empty, contains at least one heading or bullet | Reading a file and detecting sections/headings/bullets is `pathlib.Path.read_text()` + regex. No inference needed. Python reads the roadmap, splits by headings/bullets, produces `list[ParsedRoadmapItem]`. |
| **Stage 2: Parse + Phase Bucketing** | Inference (Grep + categorize) | **Pure programmatic** | `STANDARD`: every item assigned to exactly one phase, phase count >= 1, no unassigned items | Phase detection (scan for "Phase N", "vN.N", "Milestone") is regex. Bucket assignment follows the deterministic rules in Section 4.2 exactly. Phase renumbering (Section 4.3) is arithmetic. All of this is implementable as a Python function with zero ambiguity. |
| **Stage 3: Task Conversion** | Inference (content generation) | **Hybrid**: programmatic ID assignment + Claude-assisted content | `STRICT`: valid T-format IDs (programmatic), non-empty titles, 3-8 steps per task, exactly 4 acceptance criteria, exactly 2 validation bullets | Splitting rules (Section 4.4) are deterministic -- Python can detect when an item should split. Task ID assignment (Section 4.5) is arithmetic. But generating meaningful task descriptions, steps, acceptance criteria, and validation bullets requires inference -- the LLM reads the roadmap prose and produces implementation-oriented content. Gate checks the structural envelope; content quality is advisory. |
| **Stage 4: Enrichment** | Inference (scoring + content) | **Split into two sub-stages**: (4a) **Pure programmatic** scoring + (4b) **Claude-assisted** content enrichment | (4a) `STANDARD`: all tasks have Effort/Risk/Tier/Confidence computed, scores match algorithm. (4b) `STANDARD`: deliverable descriptions non-empty, artifact paths follow pattern. | Effort scoring (Section 5.2.1), Risk scoring (Section 5.2.2), Tier classification (Section 5.3), and Confidence scoring (Section 5.4) are 100% deterministic algorithms with explicit formulas. These are the strongest candidates for programmatic extraction in the entire skill. The keyword matching, score computation, compound phrase detection, and context booster application are all string operations + arithmetic. Deliverable ID assignment (D-####) is also deterministic. Content enrichment (MCP tool requirements, sub-agent delegation decisions) follows lookup tables. Only deliverable descriptions and intended artifact path inference benefit from LLM assistance. |
| **Stage 5: File Emission** | Inference (template filling + Write) | **Pure programmatic** | `STRICT`: all N+1 files written, file sizes > 0, phase file count matches index, literal filenames in index table | Template filling with structured data is string formatting, not inference. Given the enriched task data as a typed data structure, a Python function can render `tasklist-index.md` and each `phase-N-tasklist.md` using f-strings or Jinja2 templates. The templates are fully specified in SKILL.md Sections 6A and 6B. This eliminates a major source of format drift (LLM forgetting em-dash separators, wrong heading levels, missing sections). |
| **Stage 6: Self-Check** | Inference (17-point validation) | **Pure programmatic** | `STRICT`: all 14 structural checks pass as `tuple[bool, str]` gate functions. 3 semantic checks (content quality, task specificity, acceptance criteria meaningfulness) remain advisory. | This is the pattern (a) adoption. 14 of 17 checks are trivially implementable as Python functions inspecting markdown files. The 3 remaining checks that genuinely require judgment (is the description "meaningful"? does the acceptance criterion name a "specific" artifact?) could optionally be implemented as a lightweight Claude subprocess with a focused prompt, but are more practically left as advisory warnings. |

### What Stays as Inference vs Becomes Programmatic

**Stays as inference (requires LLM)**:
- Understanding vague roadmap prose ("improve performance", "harden security")
- Generating task descriptions with implementation-oriented steps
- Creating acceptance criteria that are specific to the roadmap's domain
- Writing phase goals derived from roadmap context
- Producing "Why" fields that explain task motivation
- Near-field completion criterion generation (needs domain understanding)
- Deliverable descriptions (short human-readable summaries)

**Becomes programmatic (deterministic algorithms)**:
- Roadmap item parsing (regex splitting on headings/bullets/numbered lists)
- Phase bucket assignment (heading detection + default bucketing rules)
- Phase renumbering (sequential assignment, no gaps)
- Task splitting decision (keyword detection for split triggers)
- Task ID assignment (T<PP>.<TT> zero-padded arithmetic)
- Roadmap Item ID assignment (R-### sequential)
- Deliverable ID assignment (D-#### sequential)
- Effort scoring (EFFORT_SCORE algorithm: character count + split flag + keyword match + dependency words)
- Risk scoring (RISK_SCORE algorithm: keyword category matching)
- Tier classification (compound phrase overrides + keyword matching + context boosters + priority resolution)
- Confidence scoring (max tier score, ambiguity penalty, compound boost, vague input penalty)
- Verification method routing (tier-to-method lookup table)
- MCP tool requirements (tier-to-tools lookup table)
- Sub-agent delegation requirements (tier + risk lookup)
- Checkpoint insertion (every 5 tasks + end-of-phase, deterministic naming)
- File emission (template rendering with structured data)
- All 14 structural self-checks

### Output Format Changes for Pipeline Compatibility

If portified, the intermediate data flow would use JSON-serialized dataclasses rather than in-context LLM state:

1. **Stage 1-2 output**: `TasklistParseResult` JSON with `list[ParsedRoadmapItem]` and `list[PhaseBucket]`
2. **Stage 3 output**: `TaskConversionResult` JSON with `list[TaskStub]` (ID, title, phase, roadmap items, raw content from Claude)
3. **Stage 4a output**: `EnrichmentScores` JSON with effort/risk/tier/confidence per task
4. **Stage 4b output**: `EnrichedTaskBundle` JSON with full task data including Claude-generated content
5. **Stage 5 output**: The markdown files themselves (tasklist-index.md + phase-N-tasklist.md)
6. **Stage 6 output**: `ValidationReport` JSON with per-check pass/fail/reason

The final markdown output format remains unchanged -- Sprint CLI compatibility is preserved exactly.

### Gates Per Step (Portified Design)

| Step | Gate Tier | Gate Mode | Checks |
|------|-----------|-----------|--------|
| Ingest | LIGHT | BLOCKING | File read succeeded, non-empty content |
| Parse | STANDARD | BLOCKING | Item count > 0, all items have IDs, no duplicate R-### |
| Bucket | STANDARD | BLOCKING | Phase count >= 1, all items assigned, contiguous numbering |
| Task Convert (Claude) | STRICT | BLOCKING | Valid T-format IDs, non-empty titles, step count 3-8, AC count = 4, validation count = 2 |
| Enrich Scores (programmatic) | STANDARD | BLOCKING | All tasks have Effort/Risk/Tier/Confidence, scores within valid ranges |
| Enrich Content (Claude) | STANDARD | TRAILING | Deliverable descriptions non-empty, artifact paths match pattern |
| Emit Files | STRICT | BLOCKING | N+1 files exist, sizes > 0, index contains Phase Files table with literal filenames |
| Validate | STRICT | BLOCKING | 14 structural checks pass, 3 semantic checks advisory |

---

## Portification Candidacy

**Recommendation: Selective adoption**

### Justification

Full portification (decomposing all 6 stages into subprocess-managed steps with `ClaudeProcess`, `TurnLedger`, TUI, and NDJSON monitoring) is disproportionate to the skill's complexity. The tasklist-protocol is a single-pass generator that typically completes in 1-3 minutes. The overhead of subprocess management, isolation layers, and budget tracking would exceed the cost of the work being managed.

However, **selective adoption of patterns (a), (b), (c), and (i) delivers the majority of the reliability improvement** without the architectural overhead of full portification:

1. **Pattern (a) + (b): Programmatic post-write validation** -- This is the highest-value change. Implementing 14 gate functions that run after file emission and before the skill reports completion transforms self-check from unreliable inference to deterministic verification. This can be done as a Python module (`src/superclaude/cli/tasklist/gates.py`) that the skill invokes via `Bash` tool call after writing files, or that integrates into a lightweight pipeline wrapper.

2. **Pattern (c): Extraction of deterministic algorithms** -- Moving effort/risk/tier/confidence scoring into Python functions eliminates a major source of inconsistency. The LLM sometimes miscounts keywords, forgets to apply compound phrase overrides, or miscalculates confidence penalties. A Python implementation of these algorithms guarantees correct scores every time. This module (`src/superclaude/cli/tasklist/scoring.py`) can be invoked by the skill via `Bash` to compute scores for each task, or can be used to validate LLM-computed scores post-hoc.

3. **Pattern (i): Typed intermediate representations** -- Defining `ParsedRoadmapItem`, `PhaseBucket`, `TaskStub`, and `EnrichedTask` as Python dataclasses with JSON serialization creates a contract between stages. Even if the skill continues to run as a single Claude session, these types serve as validation schemas for the intermediate data.

4. **Pattern (g): Lightweight diagnostic chain** -- A `FailureClassifier` that categorizes gate failures and suggests targeted fixes (rather than asking the LLM to "fix all issues") improves remediation reliability.

**What NOT to adopt now**:
- Full subprocess isolation (pattern h) -- single-session execution is sufficient
- TurnLedger budget tracking (pattern f) -- single session does not need it
- Step graph with executor (pattern d) -- adds complexity without proportional benefit for a 6-stage linear pipeline
- Resume/retry (pattern e) -- low ROI for a 1-3 minute operation; revisit if roadmap size grows significantly

### Selective Adoption Architecture

```
src/superclaude/cli/tasklist/
  __init__.py
  scoring.py       # Effort, Risk, Tier, Confidence algorithms (pure functions)
  gates.py         # 14 structural gate functions + 3 advisory semantic checks
  models.py        # ParsedRoadmapItem, PhaseBucket, TaskStub, EnrichedTask
  diagnostics.py   # FailureClassifier + remediation routing
  parser.py        # Roadmap parsing + phase bucketing (pure programmatic)
  emitter.py       # Template rendering for index + phase files (pure programmatic)
```

The skill SKILL.md would be updated to call these modules via `Bash`:
- After stage 2: `uv run python -m superclaude.cli.tasklist.parser <roadmap-path> --output .tasklist-work/parse-result.json`
- After stage 4: `uv run python -m superclaude.cli.tasklist.scoring .tasklist-work/task-stubs.json --output .tasklist-work/scores.json`
- After stage 5: `uv run python -m superclaude.cli.tasklist.gates <tasklist-root> --format json`
- On gate failure: `uv run python -m superclaude.cli.tasklist.diagnostics <gate-results.json>`

---

## Testing Plan

### Phase 1: Unit Tests for Programmatic Functions

**Target**: `tests/tasklist/`

| Test Module | Coverage Target | Key Properties |
|-------------|----------------|----------------|
| `test_scoring.py` | Effort scoring algorithm | Score computation matches Section 5.2.1 exactly for all keyword combinations; score-to-label mapping is correct; Clarification Tasks always score 0 |
| `test_scoring.py` | Risk scoring algorithm | Score computation matches Section 5.2.2 exactly; risk driver extraction is correct; cross-cutting keywords detected |
| `test_scoring.py` | Tier classification | Compound phrase overrides take precedence; keyword matching accumulates correctly; context boosters apply; priority resolution (STRICT > EXEMPT > LIGHT > STANDARD) resolves ties correctly |
| `test_scoring.py` | Confidence scoring | Base score capped at 0.95; ambiguity penalty of 15% applied when top two within 0.1; compound boost of 15%; vague input penalty of 30% |
| `test_gates.py` | All 14 structural gates | Each gate function returns `(True, None)` for valid input and `(False, reason)` for invalid input with a descriptive reason string |
| `test_parser.py` | Roadmap parsing | Headings, bullets, numbered lists detected as item boundaries; R-### IDs assigned sequentially; multi-sentence splitting only when independently actionable |
| `test_parser.py` | Phase bucketing | Explicit phase labels detected; default 3-bucket fallback; phase renumbering eliminates gaps |
| `test_emitter.py` | Template rendering | Index file contains all required sections; phase files contain only phase-scoped content; literal filenames in Phase Files table; em-dash separators; heading levels correct |

### Phase 2: Integration Tests for Pipeline Compatibility

| Test | Description |
|------|-------------|
| `test_sprint_compat.py` | Generated output is discoverable by sprint CLI phase regex |
| `test_round_trip.py` | Parse roadmap -> generate tasklist -> validate gates -> all pass |
| `test_scoring_consistency.py` | Python scoring matches LLM scoring on 10 reference roadmaps |

### Phase 3: Regression Tests

| Test | Description |
|------|-------------|
| `test_golden_files.py` | Compare generated output against golden reference files for 3-5 canonical roadmaps |
| `test_format_stability.py` | Output format matches sprint CLI expectations across version changes |

### Phase 4: Property-Based Tests for Determinism

| Property | Test Strategy |
|----------|---------------|
| Determinism | Same roadmap input produces identical output (byte-for-byte) on repeated runs |
| Contiguity | Phase numbers are always 1..N with no gaps, for any N |
| ID uniqueness | No duplicate R-###, T<PP>.<TT>, or D-#### across any generated bundle |
| Traceability coverage | Every R-### appears in the traceability matrix; every task references at least one R-### |
| Effort monotonicity | Adding a keyword from the effort keyword list never decreases the effort score |
| Tier priority | STRICT always wins over any lower-priority tier when keywords conflict |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Programmatic scoring diverges from SKILL.md spec** | Medium | High -- incorrect tier classification changes verification routing, which affects sprint execution safety | Pin scoring algorithms to SKILL.md version; add version assertion in scoring.py header; test against reference vectors derived from SKILL.md examples |
| **Template rendering produces format that breaks sprint CLI** | Medium | High -- sprint CLI cannot discover phases, entire tasklist unusable | Integration test against actual sprint CLI phase discovery regex; golden file tests lock output format |
| **LLM stops calling Bash validation after file emission** | Medium | Medium -- reverts to unreliable self-check | Make the Bash validation call mandatory in the skill protocol (add to "File Emission Rules" as a hard requirement); consider enforcing via a thin pipeline wrapper that runs gates automatically |
| **Intermediate data model changes break stage boundaries** | Low | Medium -- if ParsedRoadmapItem schema changes, downstream stages fail | Version the JSON schema; add schema validation at deserialization boundaries |
| **Over-extraction of inference work into programmatic code** | Low | High -- if task description generation is made programmatic, output quality degrades severely | Maintain strict classification rubric; never extract stages that require understanding natural language or making domain judgments |
| **Selective adoption becomes a maintenance burden** | Medium | Medium -- two systems to maintain (SKILL.md protocol + Python modules) with potential drift | Single source of truth: Python modules are authoritative for scoring/gates/parsing; SKILL.md references them rather than duplicating algorithms |
| **Roadmap formats not covered by parser** | Medium | Low -- parser falls back to default 3-bucket strategy | Extensive parser tests with diverse roadmap formats; fallback behavior is well-defined in Section 4.2 |
| **Performance regression from Bash subprocess calls** | Low | Low -- adding 4-5 subprocess calls adds ~2-5 seconds to a 1-3 minute operation | Negligible overhead; monitor if roadmap size grows to 100+ phases |

---

## Summary of Recommendations (Priority-Ordered)

1. **Implement programmatic gate validation** (patterns a+b) -- Highest ROI. 14 Python functions replace unreliable self-referential LLM validation. Estimated effort: 2-3 days.

2. **Extract deterministic scoring algorithms** (pattern c) -- Eliminates the most common source of output inconsistency (miscounted keywords, missed compound phrases, wrong confidence penalties). Estimated effort: 1-2 days.

3. **Define typed intermediate data structures** (pattern i) -- Creates stage boundary contracts that make data loss detectable. Estimated effort: 1-2 days.

4. **Extract template rendering** (pattern c, stage 5) -- Eliminates format drift in file emission. The LLM forgets heading levels, em-dash separators, or section ordering with surprising frequency. Estimated effort: 1-2 days.

5. **Add lightweight diagnostics** (pattern g) -- Improves failure remediation when gates detect issues. Estimated effort: 1 day.

**Total estimated effort for selective adoption**: 6-10 days.
**Expected reliability improvement**: Elimination of the most common failure modes (format violations, scoring errors, missing sections, duplicate IDs) which currently occur in an estimated 15-25% of generations for complex roadmaps.
# Refactoring Spec: sc:task-unified-protocol

## Current Architecture Assessment

### Current Step Count and Flow

The system is split across two files with a handoff boundary:

1. **Command layer** (`src/superclaude/commands/task-unified.md`): Performs tier classification as pure text output (no tool invocation), emits the `<!-- SC:TASK-UNIFIED:CLASSIFICATION -->` header, then dispatches to the skill for STANDARD/STRICT tiers. LIGHT and EXEMPT execute inline without skill invocation.

2. **Skill layer** (`src/superclaude/skills/sc-task-unified-protocol/SKILL.md`): Receives the pre-classified tier and executes the tier-specific workflow. Step counts per tier:
   - STRICT: 11 steps (activate project, verify git clean, load context, check memories, identify files, make changes, find importers, update affected files, spawn verification agent, run tests, answer adversarial questions)
   - STANDARD: 5 steps (load context, search impacts, make changes, run tests, verify)
   - LIGHT: 4 steps (scope check, make changes, sanity check, proceed)
   - EXEMPT: 2 steps (execute immediately, no verification)

Total distinct execution phases across the full lifecycle: Classification (1) + Confidence Display (1) + Execution (4-11) + Verification (0-2) + Feedback (1) = 7 to 16 phases depending on tier.

### Current Validation Mechanisms

All validation is inference-based. There are zero programmatic checks:

- **Tier classification**: Claude performs keyword matching, compound phrase detection, context boosting, and confidence scoring entirely through natural language reasoning. The command file instructs Claude to do this as "TEXT-ONLY" (no tools), which means Claude is manually pattern-matching keywords from a list.
- **Git cleanliness check**: Claude runs `git status` via Bash and interprets the output.
- **Verification routing**: Claude decides whether to spawn a sub-agent or run tests based on its reading of the tier.
- **Critical path override**: Claude checks file paths against `auth/`, `security/`, `crypto/`, `models/`, `migrations/` patterns by inspection.
- **Confidence threshold**: Claude self-reports a confidence score and self-enforces the <0.70 prompt rule.
- **Feedback collection**: Claude self-reports whether the user overrode the tier.

### Current Integration Points

- **MCP servers**: Serena (activate_project, memories, find_referencing_symbols), Sequential (complex reasoning), Context7 (documentation), codebase-retrieval (context loading)
- **Sub-agent spawning**: Task tool with quality-engineer persona for STRICT verification
- **Git operations**: Bash tool for `git status`, `pytest` execution
- **TodoWrite**: Task tracking during execution
- **Configuration references**: `config/tier-keywords.yaml`, `config/verification-routing.yaml`, `config/tier-acceptance-criteria.yaml` (these files are referenced but do not appear to exist in the repository -- the actual keyword lists are embedded in the command and skill markdown)

### Architectural Strengths to Preserve

1. **Two-layer separation**: Command handles classification, skill handles execution. This is a clean responsibility boundary that maps directly to a pipeline architecture (classification step + execution steps).
2. **Tier-appropriate overhead**: The graduated response (EXEMPT=0 verification, STRICT=full verification) is well-designed. The pipeline should preserve this proportionality.
3. **Escape hatches**: `--skip-compliance`, `--force-strict`, and `--compliance [tier]` overrides give users control. Any pipeline must preserve these as CLI flags.
4. **"Better false positives than false negatives" philosophy**: When uncertain, escalate to a higher tier. This is a sound safety principle.
5. **MCP circuit breaker semantics**: STRICT blocks if Sequential/Serena unavailable; other tiers allow fallbacks. This maps naturally to gate prerequisites.

---

## Pattern Adoption Matrix

| Pattern | Applicable | Adoption Design | Effort | Risk if Skipped |
|---------|-----------|-----------------|--------|-----------------|
| **(a) Programmatic enforcement over self-referential LLM validation** | **HIGH** -- Single biggest win. Tier classification is a deterministic algorithm (keyword matching, compound phrase detection, context boosting, confidence scoring) currently executed by inference. Critical path override is regex. MCP requirement routing is a lookup table. All three are pure functions with no creative judgment required. | Implement `classify_tier(description: str, flags: dict, file_paths: list[str]) -> TierClassification` as a Python function. Returns `(tier, confidence, keywords_matched, rationale)`. Implement `check_critical_path(paths: list[str]) -> bool` as regex. Implement `resolve_mcp_requirements(tier: str) -> MCPRequirements` as lookup. The command layer becomes a CLI entry point that calls these functions before dispatching to the skill/pipeline. | **Medium** (2-3 days). The algorithm is fully specified in the command markdown; it needs translation to Python. | **CRITICAL**: Without this, classification depends on Claude correctly parsing 4 priority tiers, 40+ keywords, 8+ compound phrases, and 6+ context boosters from natural language instructions. Measured failure modes include inventing invalid tiers ("ITERATIVE", "SIMPLE", "IMPLEMENT") and inconsistent confidence scores. The command file has explicit warnings about these failures, which is evidence they occur. |
| **(b) Pure-function gate criteria** | **HIGH** -- Multiple verification points are currently subjective inference that could be objective checks. | Gates for: (1) `git_clean_gate: (str) -> tuple[bool, str]` -- parse `git status` output for clean working directory; (2) `affected_files_gate: (str) -> tuple[bool, str]` -- verify step output contains a file list with at least one entry; (3) `test_exit_code_gate: (str) -> tuple[bool, str]` -- parse pytest output for exit code 0; (4) `adversarial_coverage_gate: (str) -> tuple[bool, str]` -- verify N adversarial questions were answered (check for numbered list pattern); (5) `import_chain_gate: (str) -> tuple[bool, str]` -- verify all files importing changed modules were identified. | **Low-Medium** (1-2 days). Each gate is a simple regex/parsing function. | **HIGH**: Without gates, the only verification that STRICT steps were actually completed is Claude self-reporting. A STRICT task could skip step 7 (find importers) or step 11 (adversarial questions) and no programmatic mechanism would catch it. |
| **(c) Classification rubric: programmatic vs inference** | **HIGH** -- This is the architectural blueprint for the entire portification. | **100% Programmatic**: Tier classification (keyword + compound + context booster scoring), critical path override (regex), MCP requirement resolution (lookup), git status check (parse), test execution dispatch + exit code (subprocess), feedback logging (append to file), confidence display (template rendering). **Orchestration (programmatic dispatch, inference interpretation)**: Context loading (dispatch codebase-retrieval, Claude interprets), impact analysis (dispatch find_referencing_symbols, Claude interprets), memory check (dispatch list_memories/read_memory, Claude interprets). **100% Inference**: Code changes (Claude writes code), verification agent reasoning (sub-agent inference), adversarial question generation and answering (creative reasoning). | **Low** (0.5 days for the classification document). The classification is already implicit in the analysis; formalizing it ensures nothing is missed during implementation. | **MEDIUM**: Without an explicit rubric, implementers will either over-portify (trying to make code changes programmatic) or under-portify (leaving classification in inference). |
| **(d) Step graph with dependency resolution** | **HIGH** -- The 4 tier-specific execution paths have clear sequential dependencies that map directly to step graphs. | STRICT step graph: `classify` -> `git_clean_check` -> `[load_context, check_memories]` (parallel) -> `identify_files` -> `make_changes` -> `find_importers` -> `update_affected` -> `[spawn_verifier, run_tests]` (parallel) -> `adversarial_qa`. STANDARD step graph: `classify` -> `load_context` -> `search_impacts` -> `make_changes` -> `run_tests`. LIGHT: `classify` -> `scope_check` -> `make_changes` -> `sanity_check`. EXEMPT: `classify` -> `execute`. The step graph enables the executor to enforce ordering, parallelize where safe, and provide progress tracking. | **Medium** (1-2 days). Four step graphs to define, each with Step/GateCriteria/timeout definitions. | **HIGH**: Without a step graph, there is no mechanism to enforce that STRICT step 7 (find importers) runs before step 8 (update affected files). Steps could be reordered or skipped by inference without detection. |
| **(e) Resume/retry with exact CLI resume commands** | **MEDIUM-HIGH** -- STRICT tasks are long-running (11 steps, 60s+ verification timeout). Failure at step 8 means repeating steps 1-7 from scratch in the current architecture. | Implement state persistence: each step writes its result to a JSONL checkpoint file. On resume, the executor reads the checkpoint, identifies the last successful step, and resumes from the next step. CLI interface: `superclaude task --resume .task-unified/checkpoint.jsonl`. Context from completed steps is injected into the resume prompt. | **Medium** (2-3 days). Requires checkpoint serialization, resume logic, and context re-injection. The pipeline executor already supports step-level state tracking. | **MEDIUM**: Without resume, a STRICT task that fails at step 9 (verification) wastes all token budget from steps 1-8. For large codebases this could be 10K+ tokens lost. The risk scales with task complexity and STRICT tier frequency. |
| **(f) Budget economics via TurnLedger** | **MEDIUM** -- Token costs are specified per tier (STRICT verification: 3-5K, STANDARD: 300-500) but not enforced. Sub-agent spawning for STRICT has no budget cap. | Implement `TurnLedger` that tracks token spend per step. STRICT verification sub-agent gets a hard budget of 5K tokens (current max target). If the sub-agent exceeds budget, the diagnostic chain fires instead of allowing unbounded retry. Budget is allocated proportionally: classification (200), context loading (2K), code changes (variable, uncapped), verification (5K cap). | **Low-Medium** (1-2 days). TurnLedger pattern exists in the pipeline infrastructure; adapt for task-unified's budget targets. | **LOW-MEDIUM**: Runaway verification costs are a real risk but are bounded by Claude's max_turns. The bigger value is observability -- knowing where tokens are spent enables optimization. |
| **(g) Diagnostic chain** | **MEDIUM** -- When STRICT verification fails, the current skill provides no structured failure analysis. Claude reports "verification failed" and the user must debug manually. | Adapt the existing `DiagnosticCollector -> FailureClassifier -> ReportGenerator` pattern. For task-unified: (1) Collect: gate failure reason + step output + test stderr; (2) Classify: test failure (assertion mismatch), missing import (ModuleNotFoundError), type error (TypeError/mypy), behavioral regression (test passed before, fails now), missing file (FileNotFoundError); (3) Report: targeted fix suggestion per failure class, with exact file:line references where available. | **Low** (1 day). The `diagnostic_chain.py` module already exists in the pipeline package with the 4-stage chain (troubleshoot, root causes, solutions, summary). Adapt the stage implementations for task-unified failure patterns. | **MEDIUM**: Without diagnostics, STRICT task failures produce opaque "verification failed" messages. Users must manually investigate, which defeats the purpose of the compliance framework. |
| **(h) 4-layer subprocess isolation** | **LOW-MEDIUM** -- Only relevant for STRICT tier, which spawns a quality-engineer sub-agent. The sub-agent currently has unrestricted access to the workspace. | Layer 1 (process isolation): Sub-agent runs as a separate `claude -p` process via ClaudeProcess. Layer 2 (file scope): Sub-agent prompt specifies read-only access to changed files and test files only. Layer 3 (tool restriction): Sub-agent allowed-tools limited to Read, Grep, Bash (for pytest only). Layer 4 (output isolation): Sub-agent writes to a designated output file; gate validates output before main process consumes it. | **Medium** (2 days). ClaudeProcess exists. The main work is prompt engineering for the sub-agent to enforce file scope and tool restrictions, plus gate validation of the sub-agent's output. | **LOW**: The risk of a verification sub-agent modifying production files is real but mitigated by the sub-agent's purpose (verification, not modification). The more likely failure mode is the sub-agent consuming excessive tokens (addressed by pattern f). |
| **(i) Context injection for inter-step data flow** | **HIGH** -- The current architecture relies on Claude's context window to carry information between steps. This is fragile: if context is lost (window overflow, session reset, or simply not attended to), downstream steps operate on incomplete information. | Implement explicit context injection: (1) `classify` step outputs `TierClassification` dataclass; (2) `load_context` step outputs `ContextBundle` (file list, dependency graph); (3) `identify_files` step outputs `AffectedFileSet`; (4) `make_changes` step outputs `ChangeManifest` (files changed, diff summary); (5) `find_importers` step outputs `ImportChainMap`; (6) Each subsequent step receives the outputs of all predecessor steps as structured data in its prompt context. The pipeline executor handles this injection automatically via `step.inputs`. | **Medium** (2-3 days). Requires defining dataclass schemas for each step's output, serialization to/from the checkpoint format, and prompt injection logic. | **HIGH**: Context window loss is the primary failure mode for long-running STRICT tasks. Without explicit context injection, step 8 (update affected files) may not have access to step 5's file list if Claude's attention has drifted to step 6-7 outputs. This manifests as missed files, incomplete updates, and silent regressions. |

---

## Pipeline Optimization Plan

| Skill Phase | Current Mode | Recommended Mode | Gate Design | Rationale |
|-------------|-------------|------------------|-------------|-----------|
| **Tier Classification** | Inference (Claude pattern-matches keywords from markdown instructions) | **Pure programmatic** (`classify_tier()` Python function) | N/A -- deterministic, no gate needed | This is the single highest-value portification target. The algorithm is fully specified, entirely deterministic, and has documented failure modes (invalid tier values). A Python function eliminates all classification errors and runs in <1ms. |
| **Confidence Display** | Inference (Claude formats a progress bar and summary) | **Pure programmatic** (template rendering from `TierClassification` output) | N/A -- presentation only | String formatting is not a valid use of inference. `f"**Tier: {tier}** [{bar}] {confidence:.0%}"` is cheaper and more consistent. |
| **Git Clean Check** (STRICT step 2) | Inference (Claude runs `git status` and interprets output) | **Hybrid** -- programmatic dispatch + programmatic parse | `git_clean_gate: (stdout) -> tuple[bool, str]` -- checks for `nothing to commit, working tree clean` or empty `--porcelain` output | Parsing `git status` output is a solved problem. No inference needed. |
| **Context Loading** (STRICT step 3, STANDARD step 1) | Inference (Claude invokes codebase-retrieval) | **Hybrid** -- programmatic dispatch, inference interpretation | `context_loaded_gate: (output) -> tuple[bool, str]` -- verify output contains at least one file reference and is non-empty | Dispatch is mechanical; interpretation requires inference. Gate ensures the step produced usable output. |
| **Memory Check** (STRICT step 4) | Inference (Claude invokes list_memories, read_memory) | **Hybrid** -- programmatic dispatch, inference interpretation | `memory_checked_gate: (output) -> tuple[bool, str]` -- verify step completed (even if no relevant memories found) | Same pattern as context loading. The memory API calls are mechanical. |
| **Identify Affected Files** (STRICT step 5, related to STANDARD step 2) | Inference (Claude reasons about which files are affected) | **Inference with programmatic gate** | `affected_files_gate: (output) -> tuple[bool, str]` -- verify output contains a structured file list (at least one file path pattern) | File identification requires codebase understanding. Gate ensures the step produced a concrete list. |
| **Make Changes** (all tiers) | Inference (Claude writes code) | **Inference** -- no portification possible | `changes_made_gate: (output) -> tuple[bool, str]` -- verify at least one Edit/Write tool was invoked (check for tool call markers in output) | Code authorship is fundamentally creative. Gate ensures the step actually modified something. |
| **Find Importers** (STRICT step 7) | Inference (Claude invokes find_referencing_symbols or grep) | **Hybrid** -- programmatic dispatch, inference interpretation | `import_chain_gate: (output) -> tuple[bool, str]` -- verify output contains file references and covers all files from step 6's change manifest | Dispatch is mechanical; interpretation of results requires judgment. Gate cross-references against the change manifest from step 6. |
| **Update Affected Files** (STRICT step 8) | Inference (Claude edits downstream files) | **Inference with programmatic gate** | `downstream_updated_gate: (output) -> tuple[bool, str]` -- verify all files identified in step 7 were addressed (each file path appears in the step's tool invocations) | Like code changes, this is creative work. Gate ensures completeness by cross-referencing step 7 output. |
| **Verification Agent** (STRICT step 9) | Inference (sub-agent spawned via Task tool) | **Programmatic dispatch, inference execution, programmatic gate** | `verification_gate: (output) -> tuple[bool, str]` -- verify sub-agent output contains pass/fail determination with evidence | The dispatch is mechanical (spawn sub-agent with specific prompt). The sub-agent's reasoning is inference. The result interpretation is regex (look for PASS/FAIL marker). |
| **Test Execution** (STRICT step 10, STANDARD step 4) | Inference (Claude runs pytest via Bash) | **Pure programmatic** (subprocess call + exit code check) | `test_gate: (exit_code, stdout) -> tuple[bool, str]` -- exit code 0 = pass, non-zero = fail with parsed failure summary | Running pytest and checking the exit code requires zero inference. This should be a direct subprocess call with structured output parsing. |
| **Adversarial Questions** (STRICT step 11) | Inference (Claude generates and answers questions) | **Inference with programmatic gate** | `adversarial_gate: (output) -> tuple[bool, str]` -- verify N questions were posed and answered (check for numbered Q/A pattern, minimum 3 questions) | Question generation and answering is creative. Gate ensures the step was not skipped or insufficiently thorough. |
| **Feedback Collection** | Inference (Claude self-reports) | **Pure programmatic** (append to JSONL log) | N/A -- logging operation | Feedback logging (tier used, override status, completion time, error count) is structured data appending. No inference needed. |
| **MCP Requirement Resolution** | Inference (Claude reads the tier-to-server mapping from markdown) | **Pure programmatic** (lookup table) | `mcp_available_gate: (tier, available_servers) -> tuple[bool, str]` -- verify required servers are available for the tier | A lookup table: STRICT requires [Sequential, Serena], STANDARD prefers [Sequential, Context7], LIGHT/EXEMPT require none. |
| **Critical Path Override** | Inference (Claude checks paths against patterns) | **Pure programmatic** (regex match against `auth/|security/|crypto/|models/|migrations/`) | N/A -- deterministic, built into classification | This is `re.search(r'(auth|security|crypto|models|migrations)/', path)`. No inference needed. |

---

## Portification Candidacy

**Recommendation: SELECTIVE ADOPTION**

### Justification

sc:task-unified-protocol is a **meta-skill that orchestrates other work**. It is not a content generator like a documentation skill or an analysis skill. This fundamentally shapes the portification strategy:

1. **Full portification is not appropriate** because the core value of the skill is its ability to invoke Claude for creative work (writing code, analyzing impact, answering adversarial questions). These phases cannot be replaced by programmatic logic.

2. **No portification is not appropriate** because the orchestration layer itself -- classification, routing, gate enforcement, progress tracking, resume -- is entirely deterministic and gains no benefit from inference. Leaving these in inference introduces documented failure modes (invalid tiers, inconsistent confidence, skipped steps).

3. **Selective adoption is the correct strategy**: Portify the orchestration skeleton (classification, dispatch, gates, context injection, budget tracking, feedback logging) while preserving inference for the creative phases (code changes, impact analysis, adversarial reasoning).

### Specific Evidence

- The command markdown contains explicit warnings about invalid tier values ("ITERATIVE", "SIMPLE", "IMPLEMENT"), proving that inference-based classification fails in practice.
- The command mandates "TEXT-ONLY" classification (no tools), which is an attempt to constrain inference to behave deterministically -- a clear signal that this should be code.
- The 11-step STRICT workflow has no resume capability, meaning a failure at step 9 wastes all prior token spend.
- The verification sub-agent has no budget cap or output validation gate.
- Context flows between steps implicitly through Claude's attention, which degrades with window length.

### Architecture Sketch

```
superclaude task "description" [--compliance tier] [--resume checkpoint]
    |
    v
[Python: classify_tier()] --> TierClassification
    |
    v
[Python: resolve_steps(tier)] --> StepGraph
    |
    v
[Python: execute_pipeline(steps, config, run_step)]
    |
    +--> Step 1: git_clean_check  [programmatic: subprocess + parse]
    +--> Step 2: load_context     [claude -p: codebase-retrieval prompt]
    +--> Step 3: identify_files   [claude -p: file identification prompt]
    +--> Step 4: make_changes     [claude -p: code change prompt, context-injected]
    +--> Step 5: find_importers   [claude -p: impact analysis prompt, context-injected]
    +--> Step 6: update_affected  [claude -p: downstream update prompt, context-injected]
    +--> Step 7: run_tests        [programmatic: pytest subprocess + exit code]
    +--> Step 8: verify           [claude -p: quality-engineer prompt, isolated subprocess]
    +--> Step 9: adversarial_qa   [claude -p: adversarial prompt]
    |
    v
[Python: log_feedback()] --> feedback.jsonl
```

Steps 1 and 7 are fully programmatic (no Claude invocation). Steps 2-6, 8-9 are Claude-assisted with programmatic gates. The executor manages ordering, retry, resume, and budget tracking.

---

## Testing Plan

### Phase 1: Unit Tests for Programmatic Functions

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| `classify_tier()` | Parameterized unit tests | 100% of keyword list, all compound phrases, all context boosters, all priority ordering scenarios |
| `classify_tier()` edge cases | Property-based (hypothesis) | Random strings never produce invalid tier values; confidence is always in [0.0, 1.0]; STRICT keywords always beat STANDARD |
| `check_critical_path()` | Parameterized unit tests | All 5 path patterns (`auth/`, `security/`, `crypto/`, `models/`, `migrations/`), negative cases, path variations |
| `resolve_mcp_requirements()` | Exhaustive unit tests | All 4 tiers, fallback-allowed flag, server availability matrix |
| `git_clean_gate()` | Parameterized unit tests | Clean output, dirty output (staged, unstaged, untracked), empty output, malformed output |
| `test_exit_code_gate()` | Parameterized unit tests | Exit code 0, 1, 2, 5 (no tests collected), 124 (timeout) |
| `affected_files_gate()` | Unit tests | Non-empty file list, empty output, malformed output |
| `adversarial_gate()` | Unit tests | 3+ Q/A pairs, fewer than 3, no Q/A pattern |
| `confidence_display()` | Snapshot tests | Correct formatting for all tiers and confidence levels |
| `resolve_steps()` | Unit tests | Correct step graph for each tier, correct dependency ordering |

### Phase 2: Integration Tests for Pipeline Compatibility

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| Step graph execution | Integration test with mock StepRunner | STRICT 11-step graph completes in order, STANDARD 5-step graph completes, gates fire at correct points |
| Resume from checkpoint | Integration test | Write checkpoint at step N, resume, verify steps 1..N are skipped, step N+1 executes |
| Parallel step groups | Integration test | `[load_context, check_memories]` execute concurrently, cross-cancellation works |
| Budget enforcement | Integration test | TurnLedger halts execution when budget exceeded, diagnostic chain fires |
| Gate failure retry | Integration test | Step fails gate, retries, passes on second attempt |
| Gate failure exhaustion | Integration test | Step fails gate after max retries, pipeline halts with diagnostic report |

### Phase 3: Regression Tests

| Test Target | Test Type | Coverage Goal |
|-------------|-----------|---------------|
| Tier classification parity | Golden-file regression | 50+ real task descriptions from usage history, verify `classify_tier()` matches the expected tier from ORCHESTRATOR.md examples |
| Override behavior | Regression tests | `--compliance strict` always produces STRICT regardless of keywords; `--skip-compliance` bypasses classification; `--force-strict` overrides auto-detection |
| Backward compatibility | Smoke tests | Existing `/sc:task` invocations produce identical tier classifications under the new system |

### Phase 4: Property-Based Tests for Determinism

| Property | Generator | Assertion |
|----------|-----------|-----------|
| Tier stability | Random task descriptions | `classify_tier(desc)` called 100 times with same input always returns same output |
| Tier validity | Random strings | Output tier is always one of {STRICT, STANDARD, LIGHT, EXEMPT} |
| Confidence bounds | Random descriptions | `0.0 <= confidence <= 1.0` |
| Priority ordering | Descriptions containing both STRICT and STANDARD keywords | STRICT always wins |
| Compound phrase precedence | Descriptions matching compound phrases | Compound phrase tier overrides individual keyword tier |
| Critical path override | Random paths with/without security patterns | `check_critical_path()` is idempotent and deterministic |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Classification regression**: Python `classify_tier()` produces different results than inference-based classification for edge cases not covered by the keyword lists. | Medium (0.4) | High -- users experience unexpected tier changes, eroding trust | Golden-file regression suite with 50+ real descriptions. A/B testing: run both classifiers in parallel for 2 weeks, log disagreements, tune before cutover. |
| **Over-portification creep**: Pressure to make inference steps programmatic (e.g., "automate impact analysis") leads to brittle, low-quality automation. | Medium (0.3) | High -- programmatic impact analysis misses dependencies that Claude would catch, causing regressions | Strict adherence to the classification rubric (pattern c). Inference phases are inference by design. Code review gate: any new programmatic step must have a clear deterministic algorithm, not a heuristic. |
| **Context injection bloat**: Injecting all predecessor step outputs into each subsequent step's prompt inflates token usage beyond budget targets. | Medium (0.4) | Medium -- token costs increase, possibly exceeding STRICT budget targets | Selective injection: each step declares which predecessor outputs it needs (not all). Summary injection: large outputs (e.g., codebase-retrieval results) are summarized before injection. Budget monitoring via TurnLedger with early warning at 80% of budget. |
| **Resume state corruption**: Checkpoint file becomes inconsistent with actual workspace state (e.g., user manually edits files between resume attempts). | Low (0.2) | High -- resumed execution operates on stale assumptions, producing incorrect changes | Checkpoint includes workspace hash (git commit SHA). On resume, verify workspace matches checkpoint; if not, warn user and offer to restart from a specific step. |
| **Sub-agent escape**: Quality-engineer verification sub-agent modifies files it should only read, corrupting the workspace. | Low (0.15) | High -- verification step introduces bugs instead of catching them | Subprocess isolation via ClaudeProcess with restricted allowed-tools in the prompt. Git stash before verification; diff after; reject if unexpected changes detected. |
| **MCP server dependency**: STRICT tier requires Sequential and Serena. If either is unavailable, the pipeline blocks entirely. No graceful degradation path. | Medium (0.3) | Medium -- STRICT tasks cannot execute during server outages | Implement circuit breaker with configurable fallback: if servers unavailable for >30s, offer user choice between (a) wait, (b) downgrade to STANDARD with warning, (c) abort. Log the degradation decision. |
| **Step graph maintenance burden**: Four separate step graphs (one per tier) must be kept in sync with the skill's behavioral contract. Changes to the skill require updating the step graph. | Medium (0.35) | Low-Medium -- step graphs drift from intended behavior | Single source of truth: step graphs are defined in code, and the skill markdown is generated from them (or at minimum, a CI check verifies consistency). |
| **Pipeline executor overhead**: Adding subprocess management, gates, checkpoints, and TUI for a workflow that currently runs inline adds latency and complexity. | Medium (0.3) | Low -- increased execution time for simple tasks | LIGHT and EXEMPT tiers bypass the pipeline entirely (current behavior preserved). Only STANDARD and STRICT use the pipeline. Pipeline overhead target: <2s per programmatic step, <5s total for pipeline setup/teardown. |
| **Adoption friction**: Users accustomed to inline `/sc:task` execution may find the pipeline-based approach slower or harder to debug. | Low-Medium (0.25) | Medium -- users avoid the pipeline, negating the reliability improvements | Transparent mode: pipeline runs with Rich TUI showing step progress, making the pipeline visible and trustworthy. `--debug` flag shows full pipeline state. Inline mode preserved for LIGHT/EXEMPT. |
