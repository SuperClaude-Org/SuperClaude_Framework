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
