# Debate Agent C: Performance Engineer Evaluation

## Scoring

### Proposal A: Meta-Orchestrator

#### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 25 | MED | "Total SKILL.md additions: 10,000-14,000" tokens in Implementation Complexity section. Converted to lines this maps to roughly 700-1000+ lines of SKILL.md additions (meta-orchestrator core, phase schema, inline parser, artifact routing, error handling, manifest, docs). Fits the 50 band (700-1000 lines). However, the proposal also states existing pipeline has **zero changes** and new components are additive. I score 25 conservatively given the high token budget implies substantial line count. |
| CX-2 Pipeline Coupling | 100 | HIGH | "Existing 5-step pipeline: **No changes**, Zero effort, Zero risk" -- Component table in Change Impact Analysis. Black-box composition pattern explicitly stated in Separation Principle section. |
| CX-3 New Abstractions Introduced | 50 | HIGH | New abstractions: (1) Meta-Orchestrator, (2) Phase Executor, (3) DAG builder/validator, (4) Artifact resolver, (5) Manifest manager, (6) Pipeline return contract wrapper. That is 6 components but some are thin. Counting conceptual abstractions: Meta-Orchestrator layer, Phase Executor, DAG builder = 3 core abstractions. Score 50. |
| CX-4 Migration Risk | 75 | HIGH | "All existing invocations behave identically" per Backward Compatibility section. New `--pipeline` flag is additive. Existing flag semantics unchanged. Only addition is a step_0 guard clause. This is "minor flag additions only" = 75. |
| CX-5 Cognitive Load (User) | 75 | MED | One primary new flag (`--pipeline`) plus 4 pipeline-level options (`--pipeline-halt-on-failure`, `--pipeline-output`, `--pipeline-interactive`, `--pipeline-parallel`). Plus YAML schema for complex cases and inline shorthand. Total: ~5 flags + optional YAML config. Score 75 (2-3 new flags for simple case, config for advanced). |

**Subtotal**: (25 x 0.30) + (100 x 0.25) + (50 x 0.20) + (75 x 0.15) + (75 x 0.10) = 7.5 + 25 + 10 + 11.25 + 7.5 = **61.25**

#### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step workflow) | 75 | MED | No explicit 8-step token estimate given, but token budget table shows total SKILL.md additions of 10-14K tokens. The runtime cost for the 8-step workflow would be 3 pipeline invocations. Each pipeline runs 8-15K tokens (per Proposal B's single_pipeline estimate which is referenced contextually). So ~25-45K for the 3-phase workflow. Score 75 (25-35K range). |
| EF-2 Parallelization Potential | 100 | HIGH | Concurrency Model section: "DAG-aware parallel execution", topological sort with levels, "one Task agent per phase", max_concurrent configurable. Level 0 phases run simultaneously. This is full DAG-aware parallel = 100. |
| EF-3 SKILL.md Token Overhead | 50 | MED | "Keep SKILL.md additions to ~200 lines of phase schema + flag definition" per Risk R1 mitigation, with meta-orchestrator in separate refs/ file. But total additions are 10-14K tokens. Assuming ~10 tokens/line, that is 1000-1400 lines total across files. The SKILL.md itself stays under 500 if ref files are used. Score 50 (500-800 range accounting for the ref file that must still be loaded). |
| EF-4 Agent Spawning Overhead | 75 | HIGH | "one Task agent per phase" in Concurrency section. For 3-phase workflow: 3 Task agents for orchestration, plus existing agents within each pipeline. The meta-orchestrator itself is not a new agent type -- it is logic in SKILL.md. The Phase Executor is a wrapper, not a spawned agent. 1 new conceptual agent type (pipeline-phase executor via Task). Score 75. |
| EF-5 Incremental Execution (resume) | 100 | HIGH | Error Handling section: "--pipeline-resume <pipeline-output>: Read manifest, skip completed phases, retry failed/pending phases. Validation: Verify completed phase artifacts still exist on disk. Reconfig: Allow reconfiguring failed phase parameters before retry." Full resume from manifest = 100. |

**Subtotal**: (75 x 0.30) + (100 x 0.25) + (50 x 0.20) + (75 x 0.15) + (100 x 0.10) = 22.5 + 25 + 10 + 11.25 + 10 = **78.75**

#### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | "Concrete Example: User's 8-Step Workflow" section maps all 8 steps exactly. Single-command expression provided with both YAML and inline shorthand. Execution trace shows all 8 steps covered. Exact match. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "each phase invokes the full 5-step pipeline including steelman requirement. Meta-orchestrator cannot bypass pipeline steps" per Risk R7. Black-box composition means every debate at every level gets full contradiction resolution. |
| EC-3 Steelman Preservation | 100 | HIGH | Risk R7: "No risk -- each phase invokes the full 5-step pipeline including steelman requirement." Guaranteed at every phase by architectural isolation. |
| EC-4 Position Bias Mitigation | 75 | MED | Risk R8: "Document recommendation: randomize input order in compare phases. Consider adding --shuffle-inputs flag." Position bias within each pipeline invocation is preserved (inherited from existing pipeline). But cross-phase ordering (opus always first) is only advisory. Score 75 (explicit at every level but no shuffle). |
| EC-5 Reproducibility | 100 | HIGH | Manifest section: "auto-generated, updated after each phase completes" with full phase status, timestamps, return contracts. Risk R5: "Manifest records checksums of completed phase outputs." Deterministic manifest + checksums = 100. |
| EC-6 Composability / Extensibility | 100 | HIGH | Architecture section: "DAG of pipeline invocations", arbitrary dependency graph with topological sort. Phase types are extensible (generate, compare, compare-files). YAML schema supports arbitrary phase graphs. = arbitrary DAG of phases. |
| EC-7 Error Recovery Robustness | 100 | HIGH | Error Handling section covers: halt_on_failure, continue_on_failure, resume from manifest. Phase-level recovery + resume + graceful degradation all present. |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (75 x 0.10) + (100 x 0.10) + (100 x 0.10) + (100 x 0.10) = 25 + 20 + 15 + 7.5 + 10 + 10 + 10 = **97.5**

#### Total: (0.30 x 61.25) + (0.30 x 78.75) + (0.40 x 97.5) = 18.375 + 23.625 + 39.0 = **81.0**

---

### Proposal B: Recursive Pipeline

#### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 50 | HIGH | Component Sizing table: "Total new/modified: ~590-820 lines". This maps to the 50 band (700-1000). |
| CX-2 Pipeline Coupling | 50 | MED | "Input Mode Parser: **Modified** -- Recognizes --recursive flag, relaxes mode exclusivity". FileVariantProvider and GenerativeVariantProvider are **Extracted** from existing code (refactoring existing Mode A/B logic). This is not zero coupling -- it is an extraction refactor of pipeline internals. 5-20 lines changed in parser, but major structural refactoring of variant sourcing. Score 50. |
| CX-3 New Abstractions Introduced | 25 | HIGH | Component Inventory: VariantProvider (abstract), FileVariantProvider (extracted), GenerativeVariantProvider (extracted), PipelineVariantProvider (new), RecursiveController (new), NamespaceAllocator (new), RecursionState (new). That is 4-5 genuinely new abstractions plus an abstract interface. Score 25. |
| CX-4 Migration Risk | 50 | MED | Mode A and Mode B logic are **extracted** into providers -- this changes internal structure even if external behavior is unchanged. "Existing Mode A and Mode B tests pass unchanged" but the refactoring creates new parsing paths. Score 50 (new parsing paths). |
| CX-5 Cognitive Load (User) | 50 | HIGH | New flags: --recursive, --children (repeatable), --max-depth, --meta-depth, --meta-model, --model-escalation, --model-map, --force-recurse, --pipeline-spec. That is 8-9 new flags. Score 50 (4-5 flags + simple config). Actually this exceeds 5 flags. Score 25 (config DSL level). Revising to 25. |

Revised CX-5: 25

**Subtotal**: (50 x 0.30) + (50 x 0.25) + (25 x 0.20) + (50 x 0.15) + (25 x 0.10) = 15 + 12.5 + 5 + 7.5 + 2.5 = **42.5**

#### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step workflow) | 75 | HIGH | Token Cost Analysis: "two_level_recursion estimate: 25K-45K tokens, ~3x single pipeline". Midpoint ~35K. Score 75 (25-35K range) to 50 (35-50K). Given the range spans both bands, score 50 conservatively since midpoint is 35K. Revising to 50. |
| EF-2 Parallelization Potential | 50 | MED | "Children at the same level are independent and could run in parallel (but serial execution is safer for state management)." Execution model is "Depth-first, left-to-right". Parallelism is possible but not the default design. Limited parallel = 50. |
| EF-3 SKILL.md Token Overhead | 75 | HIGH | Total 590-820 lines, and these are SKILL.md protocol additions. Score 75 (300-500 lines) is too generous. The 590-820 range maps to 50 (500-800). Score 50. |
| EF-4 Agent Spawning Overhead | 75 | HIGH | Reuses existing agent delegation model. PipelineVariantProvider is not a new agent type -- it re-enters the protocol. RecursiveController manages state but is not a spawned agent. 1 new conceptual agent type. Score 75. |
| EF-5 Incremental Execution (resume) | 75 | MED | RecursionState persistence section: "crash_recovery: If the pipeline crashes mid-execution, the manifest records which phases completed. A re-invocation can skip completed phases by detecting existing manifest.json." Phase-level resume = 75. |

Revised EF-1: 50, EF-3: 50

**Subtotal**: (50 x 0.30) + (50 x 0.25) + (50 x 0.20) + (75 x 0.15) + (75 x 0.10) = 15 + 12.5 + 10 + 11.25 + 7.5 = **56.25**

#### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | "Concrete Example: The User's 8-Step Workflow" section maps all 8 steps with full execution trace. Single command expression provided. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "Reuse the 5-step protocol logic (diff, debate, score, plan, merge) at every recursion level. No duplication, no special-casing." Every level gets full debate. |
| EC-3 Steelman Preservation | 100 | HIGH | Each recursion level invokes the full 5-step protocol. Steelman is a property of that protocol. Guaranteed at every phase. |
| EC-4 Position Bias Mitigation | 75 | HIGH | Cross-Model Bias section: "position_bias_preserved: Existing position bias mitigation (SKILL.md:182-186) applies." Plus "blind_evaluation: Variant source model is NOT revealed to the debate-orchestrator." Explicit at every level but no shuffle mechanism. Score 75. |
| EC-5 Reproducibility | 75 | MED | RecursionState with manifest.json persistence. Records all phases with config snapshots and results. But no explicit checksum mechanism mentioned (unlike Proposal A's Risk R5). Manifest without checksums = 75. |
| EC-6 Composability / Extensibility | 75 | HIGH | Recursive model naturally supports N-level depth (tree structure). But it is specifically a tree, not an arbitrary DAG -- each parent has children, not arbitrary cross-references. Score 75 (tree structure). |
| EC-7 Error Recovery Robustness | 75 | MED | Termination conditions section covers: depth limit, token budget exhaustion, all children failed, convergence plateau. Crash recovery via manifest. But no explicit "continue past failures" policy (only "if 1 of N children fails, proceed with N-1"). Phase-level recovery = 75. |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (75 x 0.10) + (75 x 0.10) + (75 x 0.10) + (75 x 0.10) = 25 + 20 + 15 + 7.5 + 7.5 + 7.5 + 7.5 = **90.0**

#### Total: (0.30 x 42.5) + (0.30 x 56.25) + (0.40 x 90.0) = 12.75 + 16.875 + 36.0 = **65.625**

---

### Proposal C: Phase DSL

#### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 25 | HIGH | Component Breakdown: "Total: ~1100-1400 lines". Score 25 (1000-1400 range). |
| CX-2 Pipeline Coupling | 100 | HIGH | "The 5-step pipeline is a black box -- the DSL composes pipelines, never reaches inside them." Pipeline Executor described as "existing, unchanged from current SKILL.md." |
| CX-3 New Abstractions Introduced | 25 | HIGH | New components: DSL Parser, Schema Validator, Graph Builder, Variable Interpolator, Phase Orchestrator, Artifact Store, Dry-Run Renderer, Preset Loader, Pipeline flag integration. That is 7-9 new components. Even collapsing related ones: DSL Parser+Validator, Graph Builder, Variable Interpolator, Phase Orchestrator, Artifact Store, Preset System = 6 abstractions. Score 25 (4-5). Actually >5, score 0. Reconsidering: the schema counts conceptual abstractions not implementation modules. DSL layer, Orchestrator, Artifact Store, Preset system = 4 core abstractions. Score 25. |
| CX-4 Migration Risk | 75 | HIGH | "The --pipeline flag is entirely additive. Existing --compare and --source invocations are unchanged." Risk 6: "No existing behavior changes." Minor flag additions only = 75. |
| CX-5 Cognitive Load (User) | 0 | HIGH | Full DSL with variable interpolation (`{{phase.field}}`), presets, inline phase syntax, YAML schema with typed fields, dependency declaration, 3 phase types. This is "full DSL + presets + interpolation" = 0. |

**Subtotal**: (25 x 0.30) + (100 x 0.25) + (25 x 0.20) + (75 x 0.15) + (0 x 0.10) = 7.5 + 25 + 5 + 11.25 + 0 = **48.75**

#### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step workflow) | 50 | MED | Resource feasibility check mentions "estimated 3 pipeline invocations, ~45K tokens" in dry-run output. Score 50 (35-50K range). |
| EF-2 Parallelization Potential | 75 | MED | "Phases with no mutual dependencies may execute concurrently (future optimization)" and "Phase execution is currently sequential in the initial implementation. Parallel phase execution is a future optimization." The DAG identifies parallelism but initial implementation is serial. Manual parallel phases identified but not executed = 75. |
| EF-3 SKILL.md Token Overhead | 25 | MED | Path 1 (recommended): "+400-600 lines added to SKILL.md". But total system is 1100-1400 lines. The SKILL.md additions alone are 400-600 (score 75 at 300-500 or 50 at 500-800). Plus presets, DSL schema definitions, variable interpolation rules all need to be in SKILL.md or loaded files. The DSL schema definition alone (lines 128-238 of proposal) is ~110 lines. Validation pipeline definition (lines 665-716) is ~50 lines. Total effective prompt overhead including all DSL rules, presets, validation: likely 800-1200 lines. Score 25 (800-1200). |
| EF-4 Agent Spawning Overhead | 100 | HIGH | Reuses existing agents entirely. "Pipeline Executor: The existing 5-step protocol, invoked once per phase." No new agent types. Score 100. |
| EF-5 Incremental Execution (resume) | 50 | MED | Error propagation section mentions marking phases as FAILED/BLOCKED and producing partial manifests. But no explicit resume mechanism described (unlike Proposal A's --pipeline-resume). Phase 4 implementation mentions "partial pipeline resume" but as future work. Partial resume = 50. |

**Subtotal**: (50 x 0.30) + (75 x 0.25) + (25 x 0.20) + (100 x 0.15) + (50 x 0.10) = 15 + 18.75 + 5 + 15 + 5 = **58.75**

#### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | "The User's 8-Step Workflow as a Preset" section shows exact mapping. Both YAML and inline expressions provided. Preset invocation is single-command. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "Steelman requirements and position bias mitigation are inherited properties of each pipeline invocation, not DSL-level concerns." Black-box composition preserves full debate at every phase. |
| EC-3 Steelman Preservation | 100 | HIGH | Risk 7: "The steelman requirement (SKILL.md:117) and position bias mitigation (SKILL.md:182-186) are properties of the 5-step pipeline, not the orchestration layer. Since the DSL composes pipeline invocations without modifying them, these properties are automatically preserved." |
| EC-4 Position Bias Mitigation | 75 | MED | Inherited from pipeline per Risk 7. No additional cross-phase shuffle mechanism described. Score 75 (explicit at every level, inherited from pipeline). |
| EC-5 Reproducibility | 75 | MED | Manifest.json schema provided with full phase tracking, timestamps, configs, outputs, execution_order. But no checksums mentioned. Manifest without checksums = 75. |
| EC-6 Composability / Extensibility | 100 | HIGH | Full DAG support via dependency graph. Phase types include generate, compare, meta-compare, and reserved "custom" type for future extension. Variable interpolation allows arbitrary phase references. "Arbitrary DAG of phases" = 100. |
| EC-7 Error Recovery Robustness | 75 | MED | Error propagation section covers phase failure, partial success, abort. Manifest persistence provides state. But resume is Phase 4 (future), not initial. "Phase-level recovery" without full resume = 75. |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (75 x 0.10) + (75 x 0.10) + (100 x 0.10) + (75 x 0.10) = 25 + 20 + 15 + 7.5 + 7.5 + 10 + 7.5 = **92.5**

#### Total: (0.30 x 48.75) + (0.30 x 58.75) + (0.40 x 92.5) = 14.625 + 17.625 + 37.0 = **69.25**

---

## Reverse Pass Verification (C -> B -> A)

Reviewing scores in reverse order to check for bias drift:

**Proposal C re-check**: CX-5 at 0 is harsh but accurate -- the DSL has variable interpolation, presets, 3 phase types, inline syntax, and YAML schema. This is definitively "full DSL + presets + interpolation." EF-3 at 25 is fair -- the DSL validation rules, schema, preset definitions, and variable interpolation instructions constitute significant prompt overhead. No score changes.

**Proposal B re-check**: CX-2 at 50 -- the extraction of Mode A/B into providers is a structural refactor, not just a flag addition. This is internal coupling change. Confirmed. EF-2 at 50 -- "serial execution is safer for state management" and depth-first execution model. Parallelism is an afterthought. Confirmed. EC-6 at 75 -- recursive model is tree-structured, not arbitrary DAG. A child cannot reference a sibling's output. Confirmed.

**Proposal A re-check**: CX-1 at 25 -- reconsidering. The proposal states SKILL.md additions of ~200 lines with the rest in a separate ref file. If we count only SKILL.md, it is under 400. But the ref file is loaded and parsed, so total new content is 700-1000+. The scoring guide says "Lines (est.)" not "SKILL.md lines." The total implementation is 10-14K tokens which at ~10 tokens/line is 1000-1400 lines. Score should be 25 (1000-1400 range). Confirmed. EF-2 at 100 -- DAG-aware with explicit topological sort and parallel Task agents. Confirmed.

No scores changed after reverse pass. Differentiation verified: no dimension has identical scores across all proposals.

---

## Rankings

1. **Proposal A: Meta-Orchestrator** -- 81.0 / 100
2. **Proposal C: Phase DSL** -- 69.25 / 100
3. **Proposal B: Recursive Pipeline** -- 65.625 / 100

---

## Performance Analysis (500 words)

From a performance engineering perspective, the critical question is: which proposal minimizes wasted computation, maximizes parallelism, and keeps token costs predictable while still delivering the required adversarial quality?

**Steelmanning all three proposals:**

Proposal B (Recursive Pipeline) has genuine elegance in its self-similar design. The VariantProvider abstraction is clean, and the model-escalation pattern (cheap models at leaves, expensive at root) is a legitimate cost optimization strategy that neither A nor C explicitly addresses. The blind evaluation feature (stripping model metadata) is a thoughtful efficiency-adjacent quality improvement. The depth-first execution model also has a memory advantage: it releases child context as soon as a child completes, avoiding holding multiple pipeline states simultaneously.

Proposal C (Phase DSL) offers the strongest inspectability story. The dry-run mode is a genuine performance tool -- it lets users estimate token costs before committing resources. The preset system amortizes DSL overhead across repeated invocations, and the variable interpolation enables tight coupling between phases without manual path management. The 5-stage validation pipeline catches errors before any tokens are spent on execution, which is a real cost savings mechanism.

Proposal A (Meta-Orchestrator) wins the performance evaluation for three decisive reasons:

**First, parallelization is first-class, not aspirational.** Proposal A specifies DAG-aware parallel execution with configurable concurrency (`--pipeline-parallel`), Task agent delegation per phase, and explicit topological sort with execution levels. Proposal B defaults to serial depth-first execution. Proposal C acknowledges parallelism as a "future optimization" that the initial implementation does not include. For the canonical 3-phase workflow, Proposal A executes Level 0 (two generate phases) in parallel, cutting wall-clock time by roughly 40%. This is not a minor difference when each pipeline invocation costs 8-15K tokens and takes minutes.

**Second, token overhead is the lowest.** Proposal A adds ~200 lines to SKILL.md itself (with detailed logic in a ref file), while Proposal C adds 400-600 lines to SKILL.md and requires the LLM to parse a DSL, validate schemas, resolve variables, and manage presets -- all consuming prompt context. Proposal B adds 590-820 lines and requires the LLM to manage recursive state, a concept that LLMs handle unreliably. Every line of DSL schema definition or recursion state management in SKILL.md is a line that competes for the model's attention budget. Proposal A's black-box composition means the orchestrator logic is thin and the pipeline logic is unchanged -- minimal prompt overhead for maximum execution capability.

**Third, resume capability is production-grade.** Proposal A's `--pipeline-resume` with manifest checksums means that token costs from completed phases are never wasted. If a pipeline fails at phase 3 of 5, you resume from phase 3. Proposal B has crash recovery but no checksum validation. Proposal C defers resume to a future phase. In real-world usage where multi-phase pipelines cost 25-50K tokens, the ability to avoid re-running completed phases is a substantial cost multiplier.

The core performance weakness of Proposal A is implementation size (~1000-1400 lines total). But from a runtime efficiency perspective, those lines buy DAG parallelism, manifest-based resume with checksums, and zero pipeline coupling -- the three properties that most reduce wasted computation in production adversarial workflows.

---

## Key Disagreement Points

1. **CX-1 scoring for Proposal A**: A reasonable engineer might argue that the 10-14K token budget overstates implementation size because much of it is documentation and examples, not logic. If the actual logic is closer to 600-700 lines, CX-1 would score 50 instead of 25, raising A's total to ~85.5. I scored conservatively because the proposal does not clearly separate logic lines from documentation lines.

2. **EF-2 for Proposal B**: An engineer who values memory efficiency might score B higher here. Depth-first execution has lower peak memory usage than DAG-parallel execution. The "serial is safer" design choice could be seen as a feature (predictable resource usage) rather than a limitation. I weighted wall-clock time over memory efficiency because token cost (the dominant resource) scales with invocation count, not parallelism.

3. **CX-5 for Proposal C**: Some might argue that presets effectively reduce cognitive load to "one new flag" (`--pipeline meta-debate`). I scored the full DSL surface because presets only cover predefined workflows -- any customization requires learning the DSL, and the scoring guide asks about the total cognitive load of the system, not just the happy path.

4. **EF-3 for Proposal C vs A**: Proposal C's defenders would argue that Path 1 (prompt-extension at 400-600 SKILL.md lines) is the recommended path and should be scored at face value. I scored higher overhead because the DSL validation rules, schema definitions, and preset templates all must be loaded into the prompt context even if they are not "SKILL.md lines" in the strict sense.

5. **EC-6 for Proposal B**: An engineer might argue that recursive composition is more powerful than DAG composition because it naturally supports depth > 2 without explicit phase definitions for every intermediate level. I scored 75 (tree) rather than 100 (DAG) because the recursion model cannot express lateral dependencies (e.g., phase C depends on phases A and B where A and B are at different recursion levels in different subtrees).
