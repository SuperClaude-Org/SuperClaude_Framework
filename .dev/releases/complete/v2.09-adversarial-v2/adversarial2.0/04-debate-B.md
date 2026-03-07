# Debate Agent B: Quality Engineer Evaluation

## Scoring Methodology

Scored A->B->C in first pass, then verified C->B->A in reverse pass per anti-bias protocol. All scores include evidence citations and confidence levels. My QA perspective prioritizes: error recovery robustness, testability, predictable behavior under stress, edge case handling, and failure mode clarity.

---

## Proposal A: Meta-Orchestrator

### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 25 | MED | "Total SKILL.md additions: 10,000-14,000 tokens" in Implementation Complexity Assessment. Translating token estimates to lines is imprecise, but the component table lists Meta-orchestrator + Phase executor + DAG builder + Artifact resolver + Manifest manager + Pipeline return contract + Inline parser, suggesting ~800-1200 lines of effective protocol logic. Score: 25 (1000-1400 range). |
| CX-2 Pipeline Coupling | 100 | HIGH | "Existing 5-step pipeline: No changes, Zero effort, Zero risk" -- repeated for Mode A, Mode B, error handling, and return contract in Change Impact Analysis table. Pure black-box composition. |
| CX-3 New Abstractions Introduced | 50 | HIGH | New abstractions: (1) Meta-Orchestrator, (2) Phase Executor, (3) Phase Schema/DAG. Three new abstractions per Component Responsibilities table. Score: 50. |
| CX-4 Migration Risk | 75 | HIGH | "No existing flag semantics change" in Backward Compatibility section. Only a new `--pipeline` flag added. Existing invocations documented as "No change" in Compatibility Matrix. Minor flag addition only. |
| CX-5 Cognitive Load (User) | 50 | MED | One primary new flag (`--pipeline`) but with 4 additional pipeline-level options (`--pipeline-halt-on-failure`, `--pipeline-output`, `--pipeline-interactive`, `--pipeline-parallel`) plus YAML schema and inline shorthand. Falls into 4-5 flags + simple config range. |

**Subtotal**: (25 x 0.30) + (100 x 0.25) + (50 x 0.20) + (75 x 0.15) + (50 x 0.10) = 7.5 + 25.0 + 10.0 + 11.25 + 5.0 = **58.75**

### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step) | 75 | MED | No explicit token estimate for the 8-step workflow in Proposal A. The token budget table shows "Total SKILL.md additions: 10,000-14,000" but this is implementation cost, not runtime cost. However, each phase invokes the standard pipeline. With 3 phases at 8-15K each (per Proposal B's single pipeline estimate), total is ~25-45K. Score: 75 (25-35K range, optimistic given DAG parallelism reduces wall time though not tokens). |
| EF-2 Parallelization Potential | 100 | HIGH | "DAG-based execution enabling parallel independent phases" in Summary. Concurrency Model section describes full topological sort with Level 0 parallel execution. "Task agent delegation -- one Task agent per phase" with configurable max_concurrent. |
| EF-3 SKILL.md Token Overhead | 50 | MED | "Keep SKILL.md additions to ~200 lines" in R1 mitigation, with meta-orchestrator in separate refs/pipeline-protocol.md. However, total additions are 10,000-14,000 tokens across all files. If we count total protocol additions, this is 500-800+ lines. Score: 50. |
| EF-4 Agent Spawning Overhead | 75 | HIGH | "one Task agent per phase" in Concurrency section. For the 3-phase workflow, this means reusing existing agent delegation model with one coordination agent. "Existing agent delegation model: No changes" in Change Impact Analysis. Score: 75 (1 new agent type: the meta-orchestrator coordination agent). |
| EF-5 Incremental Execution (resume) | 100 | HIGH | Full resume support documented: "--pipeline-resume <pipeline-output>" with "Read manifest, skip completed phases, retry failed/pending phases" and "Verify completed phase artifacts still exist on disk" and "Allow reconfiguring failed phase parameters before retry" in Error Handling section. Manifest records checksums per R5 mitigation. |

**Subtotal**: (75 x 0.30) + (100 x 0.25) + (50 x 0.20) + (75 x 0.15) + (100 x 0.10) = 22.5 + 25.0 + 10.0 + 11.25 + 10.0 = **78.75**

### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | Full concrete example in "Concrete Example: User's 8-Step Workflow" section maps all 8 steps to 3 phases. Execution trace shows step-by-step mapping. Both YAML and inline shorthand forms demonstrated. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "each phase invokes the full 5-step pipeline including steelman requirement. Meta-orchestrator cannot bypass pipeline steps" in R7 risk mitigation. Black-box composition guarantees debate quality at every level. |
| EC-3 Steelman Preservation | 100 | HIGH | "No risk -- each phase invokes the full 5-step pipeline including steelman requirement" in R7. Architectural guarantee by construction. |
| EC-4 Position Bias Mitigation | 75 | MED | Inherited from pipeline per black-box composition. However, R8 notes "Position bias in meta-compare (opus always variant-1)" as Medium probability risk. Only a recommendation to randomize, not a built-in guarantee. "--shuffle-inputs" flag is "Consider adding" -- not committed. |
| EC-5 Reproducibility | 100 | HIGH | "Manifest records checksums of completed phase outputs" per R5. manifest.yaml tracks all phases with timestamps, configs, return contracts. Full audit trail. |
| EC-6 Composability / Extensibility | 100 | HIGH | "arbitrary DAG of phases" per DAG construction in Concurrency Model. Full dependency-driven parallel execution with topological sort. |
| EC-7 Error Recovery Robustness | 100 | HIGH | Phase-level recovery with 4 status types (success/partial/failed/timeout). Three failure policies: halt_on_failure, continue_on_failure, resume. Error propagation rules handle: no-dependents, with-dependents, partial results. Manifest-based resume with checksum validation. This is the most comprehensive error model of all three proposals. |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (75 x 0.10) + (100 x 0.10) + (100 x 0.10) + (100 x 0.10) = 25.0 + 20.0 + 15.0 + 7.5 + 10.0 + 10.0 + 10.0 = **97.50**

### Total: (58.75 x 0.30) + (78.75 x 0.30) + (97.50 x 0.40) = 17.63 + 23.63 + 39.00 = **80.25 / 100**

---

## Proposal B: Recursive Pipeline

### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 50 | HIGH | "Total new/modified: ~590-820" lines in Component Sizing table. Midpoint ~700 lines. Score: 50 (700-1000 range, conservative since some extraction from existing code). |
| CX-2 Pipeline Coupling | 50 | MED | While the proposal states "5-Step Protocol Engine: Unchanged", the Input Mode Parser is "Modified" and existing Mode A/Mode B logic is "Extracted" into providers (FileVariantProvider, GenerativeVariantProvider). This extraction changes the internal structure. ~5-20 lines of parser changes plus significant refactoring of existing variant loading. Score: 50 (5-20 lines changed range, but extraction carries coupling risk). |
| CX-3 New Abstractions Introduced | 25 | HIGH | New abstractions: (1) VariantProvider interface, (2) PipelineVariantProvider, (3) RecursiveController, (4) NamespaceAllocator, (5) RecursionState. Five new abstractions per Component Inventory table. Score: 25 (4-5 range). |
| CX-4 Migration Risk | 50 | MED | "FileVariantProvider and GenerativeVariantProvider are just extractions of existing Mode A and Mode B logic" -- but extraction IS a refactoring that introduces new parsing paths. Mode exclusivity is conditionally bypassed ("with_recursive: Conflict check is bypassed"). This is a semantic change to existing flag behavior. Score: 50 (new parsing paths). |
| CX-5 Cognitive Load (User) | 50 | MED | New flags: --recursive, --children (repeatable), --max-depth, --meta-depth, --meta-model, --model-escalation, --model-map, --force-recurse, --pipeline-spec. That is 9 new flags. However, the simple case uses only --recursive + --children. The mental model ("pipelines all the way down") is elegant but recursion is inherently harder to reason about. Score: 50 (4-5 commonly used flags + recursive mental model complexity). |

**Subtotal**: (50 x 0.30) + (50 x 0.25) + (25 x 0.20) + (50 x 0.15) + (50 x 0.10) = 15.0 + 12.5 + 5.0 + 7.5 + 5.0 = **45.00**

### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step) | 75 | HIGH | Explicit estimate: "two_level_recursion: 25K-45K tokens" in Token Cost Analysis section. Midpoint ~35K. Score: 75 (25-35K range at the low end, but 35-50K at the high end). Splitting the difference. |
| EF-2 Parallelization Potential | 50 | HIGH | "Children at the same level are independent and could run in parallel (but serial execution is safer for state management)" and "execution_model: Depth-first, left-to-right". Default is serial. Parallel is possible but explicitly discouraged for safety. Score: 50 (limited parallel -- possible but not default). |
| EF-3 SKILL.md Token Overhead | 75 | MED | Total 590-820 lines. Since much is extracted from existing code (FileVariantProvider, GenerativeVariantProvider are extractions), net new protocol additions are lower. The SKILL.md additions would be the interface definitions, recursion control, and new flag parsing. Estimate ~300-500 lines net new to SKILL.md. Score: 75. |
| EF-4 Agent Spawning Overhead | 75 | HIGH | Reuses existing agent delegation model. The RecursiveController is not an agent but a protocol-level coordinator. Each child pipeline uses existing GenerativeVariantProvider or FileVariantProvider. Score: 75 (effectively 1 new coordination concept, but reuses agent infrastructure). |
| EF-5 Incremental Execution (resume) | 75 | MED | "crash_recovery: If the pipeline crashes mid-execution, the manifest records which phases completed. A re-invocation can skip completed phases by detecting existing manifest.json with completed phase records." Phase-level resume is supported through manifest, but no explicit --resume flag or reconfiguration capability documented. Score: 75 (phase-level resume). |

**Subtotal**: (75 x 0.30) + (50 x 0.25) + (75 x 0.20) + (75 x 0.15) + (75 x 0.10) = 22.5 + 12.5 + 15.0 + 11.25 + 7.5 = **68.75**

### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | Full execution trace in "Concrete Example" section maps all 8 steps through 7 execution steps. Single command expression provided with --recursive and --children flags. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "Reuse the 5-step protocol logic (diff, debate, score, plan, merge) at every recursion level. No duplication, no special-casing." Full debate preserved at every level by design. |
| EC-3 Steelman Preservation | 100 | HIGH | Pipeline reuse guarantees steelman at every recursion level. The 5-step protocol engine is unchanged, and steelman is embedded in that engine. |
| EC-4 Position Bias Mitigation | 100 | HIGH | "blind_evaluation: Variant source model is NOT revealed to the debate-orchestrator" with explicit "PipelineVariantProvider strips model-identifying metadata." Plus existing position bias mitigation preserved. This is the strongest position bias handling of all three proposals. |
| EC-5 Reproducibility | 75 | MED | manifest.json with full phase records, timestamps, configs, and execution order. However, no explicit checksums mentioned (unlike Proposal A's R5 mitigation). Score: 75 (manifest without checksums). |
| EC-6 Composability / Extensibility | 100 | HIGH | "naturally supports any depth" with recursive composition. Arbitrary tree structure of pipelines. "Extension path: Naturally supports any depth" in comparison table. This exceeds DAG -- it is arbitrary tree composition. Score: 100 (arbitrary DAG via tree structure). |
| EC-7 Error Recovery Robustness | 75 | HIGH | Termination conditions cover: depth limit, token budget exhaustion, all children failed, convergence already high, diminishing returns, single variant at level. Graceful degradation when 1 of N children fails. However, no explicit resume flag (crash recovery is implicit via manifest re-read). No continue-on-failure mode documented. Score: 75 (phase-level recovery but limited policy options). |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (100 x 0.10) + (75 x 0.10) + (100 x 0.10) + (75 x 0.10) = 25.0 + 20.0 + 15.0 + 10.0 + 7.5 + 10.0 + 7.5 = **95.00**

### Total: (45.00 x 0.30) + (68.75 x 0.30) + (95.00 x 0.40) = 13.50 + 20.63 + 38.00 = **72.13 / 100**

---

## Proposal C: Phase DSL

### Complexity (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | 0 | HIGH | "Total: ~1100-1400 lines" in Component Breakdown table. Score: 0 (>1400 at upper bound, and lower bound is right at the threshold). |
| CX-2 Pipeline Coupling | 100 | HIGH | "The 5-step pipeline is a black box -- the DSL composes pipelines, never reaches inside them" in Design Principles. "Pipeline Executor (existing): 5-step protocol per phase invocation (unchanged from current SKILL.md)" in Architecture. Zero pipeline changes. |
| CX-3 New Abstractions Introduced | 25 | HIGH | New abstractions: (1) DSL Parser, (2) Validator (5-stage), (3) Phase Orchestrator, (4) Artifact Store, (5) Variable Interpolator, plus presets and dry-run. At least 5 new concepts. Score: 25. |
| CX-4 Migration Risk | 75 | HIGH | "The --pipeline flag is entirely additive. Existing --compare and --source invocations are unchanged" in Risk 6. "No existing behavior changes." Minor flag addition. Score: 75. |
| CX-5 Cognitive Load (User) | 25 | HIGH | Full DSL with variable interpolation (`{{phase.field}}`), presets, parameters, inline --phase syntax with `<-` dependency arrows. The schema alone is 100+ lines. While presets reduce cognitive load for common cases, the full DSL is a config DSL + presets + interpolation system. Score: 25 (config DSL with presets and interpolation). |

**Subtotal**: (0 x 0.30) + (100 x 0.25) + (25 x 0.20) + (75 x 0.15) + (25 x 0.10) = 0.0 + 25.0 + 5.0 + 11.25 + 2.5 = **43.75**

### Efficiency (30%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EF-1 Token Cost (8-step) | 50 | MED | "estimated 3 pipeline invocations, ~45K tokens" in dry-run output example. Score: 50 (35-50K range). |
| EF-2 Parallelization Potential | 75 | MED | "Phases with no mutual dependencies may execute concurrently (future optimization)" in Phase Orchestrator description. DAG-aware topology described in Resolution Algorithm. However: "Phase execution is currently sequential (one pipeline at a time) in the initial implementation" in Execution Semantics. Score: 75 (manual/declared parallel phases with DAG support, but initial implementation is serial). |
| EF-3 SKILL.md Token Overhead | 25 | MED | Path 1 (recommended): "+400-600 lines added to SKILL.md." Path 2: "~800-1000 lines of Python + ~200 lines added to SKILL.md." Even Path 1 adds 400-600 lines to SKILL.md directly, and the total system is 1100-1400 lines. Score: 25 (800-1200 range when counting total protocol additions). |
| EF-4 Agent Spawning Overhead | 75 | HIGH | Reuses existing agent delegation. Phase Orchestrator is a coordinator, not a new agent type. Each phase invokes the existing pipeline with its standard agents. Score: 75 (1 new coordination type). |
| EF-5 Incremental Execution (resume) | 50 | MED | "Phase 4 (Hardening): Advanced validation, error propagation, partial pipeline resume" -- resume is deferred to Phase 4. Manifest provides state tracking: "Phase results are written to manifest immediately on completion. The orchestrator can re-read manifest if context is lost." But no explicit resume flag or protocol in MVP. Score: 50 (partial resume capability). |

**Subtotal**: (50 x 0.30) + (75 x 0.25) + (25 x 0.20) + (75 x 0.15) + (50 x 0.10) = 15.0 + 18.75 + 5.0 + 11.25 + 5.0 = **55.00**

### Efficacy (40%)

| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| EC-1 8-Step Workflow Completeness | 100 | HIGH | Full concrete example in "The User's 8-Step Workflow as a Preset" section. YAML, preset invocation, and inline forms all demonstrated. Dry-run output shows complete execution plan. |
| EC-2 Contradiction Resolution Quality | 100 | HIGH | "The 5-step pipeline is a black box" in Design Principles. "Steelman requirements and position bias mitigation are inherited properties of each pipeline invocation, not DSL-level concerns." Full debate preserved at every phase. |
| EC-3 Steelman Preservation | 100 | HIGH | Risk 7: "The steelman requirement (SKILL.md:117) and position bias mitigation (SKILL.md:182-186) are properties of the 5-step pipeline, not the orchestration layer. Since the DSL composes pipeline invocations without modifying them, these properties are automatically preserved." Architectural guarantee. |
| EC-4 Position Bias Mitigation | 75 | MED | Inherited from pipeline invocations per Risk 7. No additional cross-phase bias mitigation (unlike Proposal B's blind evaluation). In meta-compare, the order of `compare` entries determines variant ordering, and no shuffle mechanism is documented. Score: 75. |
| EC-5 Reproducibility | 75 | MED | manifest.json with full phase records, configs, timestamps, execution order, and lineage tracking (depends_on, depended_by). No checksums mentioned. Score: 75 (manifest without checksums). |
| EC-6 Composability / Extensibility | 100 | HIGH | "arbitrary DAG of pipeline invocations" per Architecture overview. Phase types support generate, compare, meta-compare, and future custom. Variable interpolation enables flexible composition. Presets add reusable patterns. Max 20 phases supported. |
| EC-7 Error Recovery Robustness | 75 | MED | Error propagation handles: phase failure (mark FAILED, downstream BLOCKED), partial success (warn, allow downstream), abort conditions. However: resume is "Phase 4 (Hardening)" -- not MVP. No halt-on-failure vs continue-on-failure policy toggle (unlike Proposal A). Score: 75 (phase-level recovery but limited policy options, resume deferred). |

**Subtotal**: (100 x 0.25) + (100 x 0.20) + (100 x 0.15) + (75 x 0.10) + (75 x 0.10) + (100 x 0.10) + (75 x 0.10) = 25.0 + 20.0 + 15.0 + 7.5 + 7.5 + 10.0 + 7.5 = **92.50**

### Total: (43.75 x 0.30) + (55.00 x 0.30) + (92.50 x 0.40) = 13.13 + 16.50 + 37.00 = **66.63 / 100**

---

## Reverse Pass Verification (C->B->A)

Rescored in reverse order. Differences >15 points flagged for re-evaluation:

| Criterion | Forward | Reverse | Delta | Action |
|-----------|---------|---------|-------|--------|
| A: CX-1 | 25 | 25 | 0 | No change |
| B: CX-2 | 50 | 50 | 0 | No change |
| B: EF-2 | 50 | 50 | 0 | No change |
| C: CX-1 | 0 | 0 | 0 | No change |
| C: EF-3 | 25 | 25 | 0 | No change |

No sub-criterion differed by >15 points between passes. All scores confirmed.

---

## Rankings

1. **Proposal A: Meta-Orchestrator** -- 80.25 / 100
2. **Proposal B: Recursive Pipeline** -- 72.13 / 100
3. **Proposal C: Phase DSL** -- 66.63 / 100

---

## Quality Engineering Analysis (500 words)

From a quality engineering perspective, the primary evaluation axis is: which proposal produces the most predictable, testable, and recoverable system under both normal and degraded conditions?

**Steelmanning Proposal C (Phase DSL)**: Proposal C deserves credit for the strongest pre-execution validation story. The 5-stage validation pipeline (syntax, graph, variables, semantics, resources) is the most rigorous pre-flight check of any proposal. The dry-run mode is genuinely valuable for QA -- it enables testing the orchestration logic without executing expensive pipeline invocations. Variable interpolation with lazy resolution and explicit recursion limits (3 levels of variable nesting) shows defensive thinking. The preset system reduces the surface area for user error in common workflows. For a QA engineer writing test harnesses, dry-run mode alone is a significant advantage.

**Steelmanning Proposal B (Recursive Pipeline)**: Proposal B's greatest QA strength is conceptual unity. There is exactly one abstraction (the pipeline) that operates identically at every level. This means test coverage at one level gives high confidence about behavior at all levels. The VariantProvider abstraction creates a clean seam for mocking in tests -- you can test the RecursiveController with stub providers without invoking real pipelines. The blind evaluation feature (stripping model metadata) is the strongest position bias mitigation and directly improves adversarial outcome quality. The termination conditions (convergence plateau detection, single-variant passthrough) demonstrate mature thinking about edge cases in recursive systems.

**Why Proposal A wins from a QA perspective**: Proposal A is the clear winner because it optimizes for the quality attribute that matters most in a system this complex: **failure mode predictability**.

First, error recovery. Proposal A documents three distinct failure policies (halt, continue, resume) with explicit user control via flags. The resume protocol includes checksum validation of completed phases before proceeding -- this prevents the insidious bug where a phase's output was manually modified between a failure and a resume, leading to inconsistent downstream results. Neither B nor C offers this level of recovery sophistication.

Second, testability through isolation. The black-box composition pattern means the meta-orchestrator can be tested completely independently of the pipeline. You can write a test that verifies DAG construction, phase sequencing, artifact routing, and error propagation using mock pipeline return contracts. The pipeline itself needs zero test modifications because it is not touched. Proposal B's extraction of existing code into providers introduces a refactoring risk -- the extraction itself could introduce bugs in previously working Mode A/B paths, and those bugs would be subtle because the interface changed while the behavior should not have.

Third, debuggability. When a 3-phase pipeline fails at phase 2, Proposal A's manifest gives you a flat list of phases with statuses. Proposal B gives you a recursion stack with nested frames. For a QA engineer investigating a production failure, flat is strictly better than nested. The cognitive overhead of tracing a recursive failure through L0-opus -> root -> failure is meaningfully higher than reading phase-1: success, phase-2: failed, phase-3: skipped.

Fourth, the migration risk profile. Proposal A introduces zero changes to existing code paths. Proposal B extracts and restructures existing code. From a regression testing perspective, "no changes to existing code" is the safest possible starting point. Every extraction, no matter how clean, carries the risk of behavioral drift.

The 8-point gap between A (80.25) and B (72.13) is primarily driven by Proposal A's superior complexity score (58.75 vs 45.00) and efficiency score (78.75 vs 68.75). Proposal B's recursive elegance comes at a concrete cost in implementation complexity, debuggability, and default serial execution that a quality engineer cannot ignore.

---

## Key Disagreement Points

1. **CX-1 scoring for Proposal A**: I scored A at 25 based on token-to-line estimation. Another evaluator might argue the 10K-14K token estimate includes documentation and examples, and the actual logic is closer to 700-800 lines, which would score 50. This would raise A's total by approximately 2.25 points.

2. **EF-2 for Proposal B**: I scored 50 (limited parallel) because the proposal explicitly states serial is the default and safer approach. An evaluator focused on architectural capability rather than default behavior might score 75 since the architecture supports parallel children. This would raise B's total by approximately 1.88 points.

3. **EC-7 for Proposals B and C**: I scored both at 75. A more lenient evaluator might argue that manifest-based crash recovery is functionally equivalent to full resume capability, scoring these at 100. This would raise both totals by approximately 1.0 point.

4. **CX-5 for Proposal B**: The 9 new flags could be scored more harshly (25) since the recursion mental model is genuinely difficult for most users. Conversely, one could argue the common case (--recursive + --children x2) is simple enough for 75. My score of 50 splits this.

5. **Proposal C's dry-run advantage**: I did not give Proposal C any bonus for dry-run mode since it is not captured in the scoring framework's sub-criteria. A QA engineer might argue this feature alone justifies a higher EC-7 score (validation before execution is a form of error prevention). This is a framework limitation rather than a scoring disagreement.

---

## Validation Checklist

- [x] All 3 proposals scored on all 17 sub-criteria
- [x] Every score has an evidence citation
- [x] Anti-bias two-pass protocol followed (A->B->C then C->B->A)
- [x] No dimension has all-same scores across proposals (differentiation confirmed)
- [x] Confidence indicators provided for every sub-criterion
- [x] Tiebreaker protocol ready if needed (not needed -- 8+ point gaps)
