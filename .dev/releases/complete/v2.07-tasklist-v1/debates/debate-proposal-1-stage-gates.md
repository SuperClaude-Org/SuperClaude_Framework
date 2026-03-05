# Adversarial Debate: Integration Strategy 1 — Stage-Gated Generation Contract

**Date**: 2026-03-04
**Proposal**: Add strict internal stage gates to `/sc:tasklist` v1.0 SKILL execution pipeline
**Debate Format**: ADVOCATE vs CRITIC with structured synthesis
**Agents**: Opus (Advocate), Haiku (Critic)

---

## Proposal Under Review

Add a strict internal stage contract to the SKILL execution pipeline:

```
Stage 1: Input ingest       → validate before advancing
Stage 2: Parse + phase bucketing → validate before advancing
Stage 3: Task conversion    → validate before advancing
Stage 4: Enrichment         → validate before advancing
Stage 5: File emission      → validate before advancing
Stage 6: Self-check         → final validation
```

Each stage must complete and validate before advancing. No stage skipping. Generation reports completed stages in order and halts on failed stage validation.

**Concrete spec changes proposed** (from `tasklist-spec-integration-strategies.md`):
- Strengthen `sc-tasklist-command-spec-v1.0.md` §6.2 with: "Each stage must complete and validate before advancing; no stage skipping."
- Add acceptance criterion: "Generation reports completed stages in order and halts on failed stage validation."

---

## ADVOCATE Position: Stage Gates Are Essential for Production Reliability

### Argument 1: Debugging Observability

**Claim**: Without stage gates, a malformed output gives you no signal about WHERE the pipeline broke.

The current v3.0 generator (§4.1-4.5, §5, §6, §8) runs as one continuous prompt execution. When it produces bad output — wrong phase numbering, missing tier classifications, orphaned dependencies — the operator sees only the final result. They cannot distinguish between:

- A parsing failure (roadmap items extracted incorrectly in §4.1)
- A bucketing failure (items assigned to wrong phases in §4.2-4.3)
- A conversion failure (tasks generated incorrectly from items in §4.4-4.5)
- An enrichment failure (tier/effort/risk misclassified in §5)
- A formatting failure (file emission violated §6 template)

Stage gates with per-stage validation reports transform "the output is wrong" into "Stage 2 failed: phase bucketing produced 0 phases from 14 roadmap items." This is the difference between root cause analysis and guesswork.

**Evidence**: The existing `TodoWrite` usage in §6.4 already tracks progress (`parse -> enrich -> generate -> validate`), but without halt semantics. TodoWrite entries show "in_progress" or "completed" but never "failed at Stage 2 with reason X." The infrastructure for stage tracking exists; it just lacks teeth.

### Argument 2: Partial Failure Recovery

**Claim**: Stage gates create natural recovery points that prevent wasted computation.

Consider a roadmap with 12 phases and 80+ tasks. The generator reads the roadmap (Stage 1), parses items (Stage 2), buckets them into phases (Stage 3), converts to tasks (Stage 4), enriches all 80 tasks with tier/effort/risk (Stage 5), writes all 13 files (Stage 6), then runs the self-check (Stage 7) which catches that the roadmap contained an ambiguous version token causing `TASKLIST_ROOT` derivation to fail.

Without stage gates, the entire pipeline ran to completion before discovering a Stage 1 input problem. All enrichment and file emission was wasted work.

With stage gates, Stage 1 validation catches "TASKLIST_ROOT derivation ambiguous: found `v2.1` and `v2.1.1` — halting." The operator fixes the input and re-runs. Stages 2-6 never execute on bad input.

**Quantification**: In the SuperClaude release history, examining `.dev/releases/complete/`, there are 40+ generated tasklist files across 7 releases. Re-runs due to input issues are common enough that preventing wasted downstream computation has measurable value.

### Argument 3: Deterministic Re-Runs and Idempotency

**Claim**: Stage gates enforce the determinism guarantee (§1, FR-3) by making each transformation explicit and verifiable.

The v1.0 spec claims "same input -> same output" (deterministic). But without stage boundaries, there is no way to verify that each transformation step is individually deterministic. A generator could produce correct final output through non-deterministic intermediate steps (e.g., random ordering in §4.1 that happens to sort correctly by §4.3).

Stage gates with intermediate validation make determinism verifiable at each step:
- Stage 2 output: "14 roadmap items parsed, IDs R-001 through R-014" (verifiable)
- Stage 3 output: "4 phase buckets: [Phase 1: R-001..R-004], [Phase 2: R-005..R-008], ..." (verifiable)
- Stage 4 output: "22 tasks generated, IDs T01.01 through T04.06" (verifiable)

This per-stage determinism verification is stronger than only checking final output, because it catches bugs that produce correct output for one input but break on others.

### Argument 4: CI/CD Integration Path

**Claim**: Stage gates are a prerequisite for automated pipeline integration, which is the natural evolution of `/sc:tasklist`.

The PRD (`tasklist-generation-pipeline-prd.md`) explicitly describes a multi-stage pipeline:
- Stage A: Generate canonical `tasklist.md`
- Stage B: Deterministic compile to sprint artifacts
- Stage C: Preflight gate (mandatory `--dry-run`)
- Stage D: Execution handoff

The PRD's Stages A-D already assume stage-gated behavior at the macro level. Strategy 1 brings the same discipline inside Stage A (the generation itself). This is consistent: if the outer pipeline has gates, the inner pipeline should too.

Furthermore, FR-3 (deterministic rebuild) and FR-6 (dry-run gate) are both easier to implement when the generator itself produces stage completion evidence. A CI pipeline can parse stage reports to identify regressions without running the full pipeline.

### Argument 5: Alignment with Strategy 5 (Pre-Write Validation Checklist)

**Claim**: Stage gates provide the structural framework that Strategy 5 requires.

The integration strategies document recommends implementing Strategy 5 (Pre-Write Validation Checklist) FIRST, before Strategy 1 (Stage Gates). But Strategy 5's "Pre-Write Validation Checklist" is itself a stage gate — it runs before `Write()` and blocks on failure. Implementing Strategy 5 without stage gates creates an inconsistency: one stage has a gate, others do not.

Stage gates generalize Strategy 5 from "one gate before writing" to "gates at every transition." This is architecturally cleaner and avoids the ad-hoc feeling of a single checkpoint in an otherwise unstructured flow.

---

## CRITIC Position: Stage Gates Are Process Theater That Adds Complexity Without Changing Output

### Argument 1: The Pipeline Is Already Sequential by Nature

**Claim**: Adding formal stage gates to an inherently sequential process is redundant ceremony.

The generator is a prompt executed in a single Claude Code session. The algorithm (§4.1 through §8) is already strictly ordered:

1. You cannot bucket into phases (§4.2) without first parsing roadmap items (§4.1)
2. You cannot convert to tasks (§4.4) without phase buckets
3. You cannot enrich tasks (§5) without tasks to enrich
4. You cannot write files (§6) without enriched tasks
5. You cannot self-check (§8) without written files

This is not a concurrent pipeline where stages might execute out of order. It is a sequential prompt execution where each step necessarily depends on the previous step's output. The dependencies are structural, not contractual. Adding formal gates does not prevent stage-skipping because stage-skipping is physically impossible in this architecture.

The Advocate's concern about "no stage skipping" addresses a failure mode that cannot actually occur.

### Argument 2: Stage Validation Overhead Without Meaningful Output Change

**Claim**: Per-stage validation adds token cost and execution time without improving the final artifact.

Consider what "validate before advancing" means concretely for each stage:

- **Stage 1 (Input ingest)**: Validate that the roadmap was read. This is already handled by §5.4 Input Validation in the command layer. Adding a second validation inside the skill is redundant.
- **Stage 2 (Parse + bucket)**: Validate that roadmap items were parsed. What would failure look like? Zero items parsed from a non-empty roadmap? This is a pathological case that indicates the input is not a roadmap at all — which should be caught at the command layer.
- **Stage 3 (Task conversion)**: Validate that tasks were generated. Again, zero tasks from non-zero roadmap items is pathological.
- **Stage 4 (Enrichment)**: Validate that all tasks have tier/effort/risk. This is already enforced by the §8 Self-Check which verifies all required metadata fields.
- **Stage 5 (File emission)**: Validate that files were written. The §8 Self-Check already verifies "Glob for all expected phase files."
- **Stage 6 (Self-check)**: This IS the existing validation.

Each intermediate validation either duplicates existing checks (command-layer input validation, §8 self-check) or validates conditions that are structurally guaranteed by the sequential nature of prompt execution. The cost is real: each validation checkpoint consumes tokens for validation logic, stage reports, and halt/continue decisions. The benefit is illusory.

### Argument 3: Single-Session Execution Makes Partial Failure Rare

**Claim**: The Advocate's partial failure recovery argument assumes a failure mode that barely exists in practice.

`/sc:tasklist` runs in a single Claude Code session. The LLM generates the entire pipeline output in one pass. "Partial failure" in this context means the LLM produced output for stages 1-3 but then hallucinated or lost coherence at stage 4. This is not how LLM execution works in practice — the model either produces a coherent response or the session fails entirely (timeout, context overflow, API error).

The scenarios where partial failure recovery would help are:
1. **Context overflow mid-generation**: Possible for very large roadmaps (>100 items), but the solution is input chunking, not stage gates.
2. **Hallucination at a specific stage**: If the model hallucinates bad phase assignments, stage gates don't prevent the hallucination — they only detect it after it happens. The model would need to validate its own output, which is the same model that produced the error.
3. **Session crash**: Stage gates don't help because there are no recoverable checkpoints. The v1.0 non-goals explicitly state "no interactive mode" and the skill runs without persistent state.

The recovery benefit is theoretical at best. In practice, when generation fails, you re-run it. Stage gates don't change this.

### Argument 4: "Deterministic Re-Runs" Is a Category Error

**Claim**: Stage gates do not make re-runs more deterministic; they add observation points to an already-deterministic process.

The Advocate argues that stage gates enforce determinism by making each step verifiable. But determinism is a property of the transformation function, not the observation of its intermediate states. If the parsing algorithm (§4.1) is deterministic, adding a validation gate after it does not make it "more deterministic." It just adds an observation point.

Moreover, the intermediate representations are internal to the LLM's generation. There is no serializable intermediate state between "parse roadmap items" and "bucket into phases" — these are conceptual steps in a continuous text generation. Stage gates in a prompt are not equivalent to stage gates in a compiled pipeline where each stage produces a concrete, inspectable artifact.

The spec already has the only meaningful determinism check: "same input -> same output" at the final output level. Checking intermediate steps requires defining what "intermediate output" even means in a prompt execution context, which the proposal does not address.

### Argument 5: The CI/CD Argument Is Premature for v1.0

**Claim**: Building CI/CD infrastructure for a v1.0 skill is premature optimization.

The PRD (`tasklist-generation-pipeline-prd.md`) describes a future multi-stage pipeline with Stages A-D. But v1.0 explicitly excludes:
- No Python CLI integration (non-goal)
- No MCP-driven auto-detection (non-goal)
- No interactive mode (non-goal)

The CI/CD pipeline described in the PRD is a v2.0+ concern. Adding internal stage gates now to support future CI/CD integration is speculative engineering — building infrastructure for requirements that don't exist yet. This directly violates YAGNI.

If v2.0 needs stage gates, v2.0 can add them with full knowledge of the actual CI/CD requirements. Adding them now based on speculation means:
1. The gates may not align with actual CI/CD needs
2. The gate validation logic becomes tech debt if the CI/CD design differs
3. v1.0 ships with unnecessary complexity

### Argument 6: Self-Validation by the Same Model Is Circular

**Claim**: Stage gates where the generator validates its own output provide false confidence.

The proposal says "each stage must complete and validate before advancing." Who performs the validation? The same LLM that just executed the stage. This creates a circular validation problem:

- If the model incorrectly parsed roadmap items (Stage 2), can the same model reliably detect that error in its Stage 2 validation? The bias that caused the parsing error likely also biases the validation.
- If the model assigned wrong tiers (Stage 4), the same model reviewing its own tier assignments will likely confirm them as correct.

Self-validation is weaker than independent validation. The existing §8 Self-Check at least validates structural properties (file existence, heading format, contiguous numbering) which are objectively checkable. But "validate that parsing was correct" requires semantic understanding of whether the parsing correctly captured the roadmap's intent — exactly the kind of judgment that can go wrong.

Stage gates create an illusion of rigor: "we validated at every step!" But if the validator and the executor are the same entity, the validation is theater.

---

## SYNTHESIS

### Points of Agreement

Both positions agree on:
1. The pipeline IS sequential — stages cannot execute out of order
2. The §8 Self-Check already validates structural output correctness
3. The v1.0 spec's TodoWrite usage already tracks progress, just without halt semantics
4. Full CI/CD integration is not a v1.0 requirement
5. Better debugging observability has real value when generation fails

### Verdict: CONDITIONAL ACCEPT with Significant Modifications

The Advocate makes a legitimate case for debugging observability (Argument 1) and alignment with the pre-write validation checklist (Argument 5). When generation produces bad output, knowing which stage failed is genuinely valuable. The Critic's strongest arguments are about circular self-validation (Argument 6) and the overhead of redundant checks (Argument 2).

**The core tension**: Stage gates are valuable for observability but weak for validation when the validator is the same model that executed the stage.

### Recommended Modifications

**1. Adopt Stage Reporting, Reject Stage Validation Gates**

Instead of "validate before advancing" (which is circular), adopt **stage completion reporting**:

```markdown
## Stage Completion Reporting (Required)

The generator MUST report stage completion in TodoWrite with concrete metrics:

- Stage 1 (Input): "Read {N} chars from roadmap, TASKLIST_ROOT = {path}"
- Stage 2 (Parse): "Parsed {N} roadmap items (R-001..R-{N}), {M} phase buckets"
- Stage 3 (Convert): "Generated {N} tasks across {M} phases (T01.01..T{MM}.{NN})"
- Stage 4 (Enrich): "All {N} tasks enriched: {strict}S/{standard}D/{light}L/{exempt}E tiers"
- Stage 5 (Emit): "Wrote {N+1} files: tasklist-index.md + {N} phase files"
- Stage 6 (Check): "Self-check: {pass|fail} — {details}"

Reports are observability artifacts. They do NOT include halt-on-failure logic
except at Stage 6 (Self-Check), which already has halt semantics in §8.
```

This gives the Advocate their debugging observability without the Critic's overhead and circular validation concerns.

**2. Consolidate Validation at Two Points, Not Six**

Instead of per-stage gates, validate at exactly two points:

- **Pre-generation**: Input validation (command layer, §5.4 — already exists)
- **Pre-write**: Structural + semantic validation (Strategy 5's checklist — proposed for §7.5)

This avoids redundant intermediate validation while still catching errors before they manifest as bad output files.

**3. Drop the "Halt on Failed Stage Validation" Language**

The proposed acceptance criterion "Generation reports completed stages in order and halts on failed stage validation" should be revised to:

> "Generation reports completed stages with metrics via TodoWrite. Generation halts only on: (a) input validation failure, (b) pre-write validation checklist failure (§7.5), or (c) self-check failure (§8)."

This preserves three meaningful halt points while removing the four intermediate halt points that provide false confidence.

**4. Preserve the Stage Contract for Future Extensibility**

Keep the stage enumeration (Input -> Parse -> Convert -> Enrich -> Emit -> Check) as a documented execution contract, even without per-stage gates. This gives v2.0 a clear structure to add gates IF CI/CD integration requires them, without requiring v1.0 to pay the complexity cost now.

### Final Assessment

| Aspect | Verdict | Rationale |
|--------|---------|-----------|
| Stage enumeration | ACCEPT | Documents the pipeline clearly |
| Stage completion reporting | ACCEPT | Debugging observability with low overhead |
| Per-stage halt-on-failure | REJECT | Circular self-validation, redundant with existing checks |
| Two-point validation | ACCEPT | Input + pre-write covers the meaningful failure modes |
| CI/CD readiness | DEFER to v2.0 | YAGNI applies; document the contract, don't build the gates |

**Net recommendation**: Accept Strategy 1 in modified form as "Stage Completion Reporting Contract" rather than "Stage-Gated Generation Contract." The observability value is real; the gate enforcement value is not, given the single-session, single-model execution context.

---

## Appendix: Evidence References

| Document | Location | Relevance |
|----------|----------|-----------|
| v1.0 Command Spec | `.dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md` | §4.3 invocation flow, §6.4 tool usage (TodoWrite) |
| Integration Strategies | `.dev/releases/current/v2.07-tasklist-v1/tasklist-spec-integration-strategies.md` | Strategy 1 definition, recommended patch order |
| Pipeline PRD | `.dev/releases/current/v2.07-tasklist-v1/tasklist-generation-pipeline-prd.md` | Stages A-D, FR-3 determinism, FR-6 dry-run gate |
| v3.0 Generator | `.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md` | §4.1-4.5 algorithm, §8 self-check |
| Taskbuilder Proposals | `.dev/releases/current/v2.07-tasklist-v1/taskbuilder-integration-proposals.md` | Strategy 5 pre-write validation |
