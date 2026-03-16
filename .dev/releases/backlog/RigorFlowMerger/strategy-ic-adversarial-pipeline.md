---
component: adversarial-pipeline
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Adversarial Pipeline

## 1. Design Philosophy

The adversarial pipeline exists to produce higher-quality artifacts than any single model can generate by systematically exploiting model diversity: generating multiple variants with different model/persona configurations, then comparing them through structured debate, hybrid scoring, and evidence-tracked merging. The core design principle is **structured disagreement as a quality signal** — divergence between variants reveals assumptions and trade-offs that converged single-model output suppresses.

**Why this design exists**: A single LLM generation tends to commit early to a perspective and rationalize subsequent choices in its favor. By generating two or more variants under different personas (e.g., `opus:architect` vs. `haiku:analyzer`) and running a formal 5-step adversarial protocol, the system forces each variant's assumptions to be made explicit and scored against objective criteria.

**Trade-off**: The 5-step sequential protocol produces 6 artifacts and requires substantial wall-clock time (multiple LLM invocations per step). For simple artifacts where model variance is low (e.g., a trivial config file), the adversarial overhead produces diminishing returns. The protocol is most valuable when comparing architecturally substantive documents where real trade-offs exist.

## 2. Execution Model

The adversarial pipeline operates as a behavioral skill (`.claude/skills/sc-adversarial-protocol/SKILL.md`) with three invocation modes:

**Mode A** — Compare existing files: `--compare file1,file2[,...,fileN]` (2–10 files)
**Mode B** — Generate variants then compare: `--source <file> --generate <type> --agents <spec>[,...]`
**Pipeline Mode** — Multi-phase DAG: `--pipeline "shorthand"` or `--pipeline @pipeline.yaml`

**5-step sequential protocol** (each step produces a named artifact):
1. **Diff Analysis** → `diff-analysis.md`: Structural comparison (section ordering, hierarchy), content comparison (claim-level), and contradiction detection across all variants.
2. **Adversarial Debate** → `debate-transcript.md`: Per-point debate rounds where domain agents argue for their variant's approach. Convergence tracked as `agreed_points / total_diff_points`; threshold configurable (default 0.80). Round 2.5 (invariant probe) activates at `--depth standard|deep`. Max rounds: 1 (quick), 2 (standard), 3 (deep).
3. **Base Selection** → `base-selection.md`: Hybrid scoring: 50% quantitative (5 metrics: RC×0.30 + IC×0.25 + SR×0.15 + DC×0.15 + SC×0.15) + 50% qualitative (25-criterion additive binary rubric with CEV protocol). Position-bias mitigation via forward + reverse evaluation passes.
4. **Refactoring Plan** → `refactor-plan.md`: Actionable plan to incorporate non-base variant strengths into the selected base.
5. **Merge Execution** → `merge-log.md` + merged output: `merge-executor` agent applies refactoring plan changes, adds provenance annotations, validates merged output for structural integrity and cross-reference resolution.

**Tiebreaker protocol** (3 levels, deterministic):
1. Debate performance (more diff-point wins)
2. Correctness count (highest correctness criteria count; hallucination-resistant dimension)
3. Input order (first variant presented wins; arbitrary but deterministic) (`src/superclaude/skills/sc-adversarial-protocol/refs/scoring-protocol.md:189`).

## 3. Quality Enforcement

**CEV (Claim-Evidence-Verdict) protocol**: Every qualitative criterion score must be backed by an explicit evidence citation from the variant text. Unsupported criterion scores are disallowed, preventing hallucinated quality claims.

**Position-bias mitigation**: Qualitative evaluation runs twice per variant — forward and reverse input order — and scores are averaged. This eliminates the systematic LLM preference for items presented earlier in context.

**Convergence plateau detection**: Pipeline Mode includes convergence plateau detection to prevent infinite debate loops when variants have reached maximum achievable agreement below the threshold. The system recognizes plateau and halts rather than continuing fruitless rounds.

**Structural integrity validation**: The `merge-executor` agent performs post-merge validation: heading hierarchy check, section ordering validation, internal reference resolution, and contradiction re-scan on merged content. Any structural break is reported in `merge-log.md`.

**Trade-off**: The 25-criterion qualitative rubric and CEV protocol add significant evaluation time. For quick comparisons where depth of analysis is not required, `--depth quick` reduces to 1 debate round and may skip certain qualitative dimensions, trading thoroughness for speed.

## 4. Error Handling Strategy

**Pipeline resume**: Pipeline Mode writes a manifest tracking phase completion status. Interrupted pipelines can be resumed from the last completed phase without re-executing earlier phases.

**Partial convergence handling**: If debate does not converge to the threshold by the final round, the system records the unconverged state in `debate-transcript.md` and proceeds to scoring with a note indicating unresolved conflicts. The `unresolved_conflicts` count is included in the return contract.

**Merge failure escalation**: If `merge-executor` cannot apply a planned change (e.g., the merge target section does not exist in the base), it reports the issue back to the orchestrator rather than improvising. The `merge-log.md` records which changes failed and why.

**Return contract**: The pipeline returns a structured contract: `merged_output_path`, `convergence_score`, `artifacts_dir`, `status` (success|partial|failed), `base_variant`, `unresolved_conflicts`, `fallback_mode` (`src/superclaude/skills/sc-adversarial-protocol/SKILL.md:412`). Callers can inspect `status` and `unresolved_conflicts` to decide whether to accept the output.

**Trade-off**: The `fallback_mode: true` flag in the return contract signals that some pipeline steps used degraded behavior (e.g., skipped a debate round due to convergence plateau). The caller receives a valid artifact but without the guarantee of full adversarial scrutiny. The fallback condition is transparent but may not be caught by downstream consumers that do not inspect the contract.

## 5. Extension Points

- `--agents model[:persona[:"instruction"]]` — per-agent instructions enable fine-grained persona control (e.g., `opus:architect:"prioritize backward compatibility"`).
- `--depth quick|standard|deep` — controls debate rounds (1/2/up to 3) and feature gates (Round 2.5 invariant probe, extended convergence tracking).
- `--blind` — strips model identity from comparisons, preventing persona-biased evaluations.
- `--focus` — restricts comparison to specific dimensions, reducing evaluation time for targeted reviews.
- Pipeline Mode YAML: full DAG specification enables complex multi-phase pipelines with parallel generate phases routed to a single compare phase.
- `--convergence` threshold configurable (0.50–0.99) — allows looser or tighter convergence requirements per use case.

## 6. System Qualities

**Maintainability**: 5 sequential steps each producing a named artifact means intermediate results are reviewable. Each step has a clear input and output contract. The `merge-executor` agent is strictly plan-following (no strategic decisions), making its behavior predictable.

**Weakness**: The adversarial protocol is implemented entirely in a behavioral skill (SKILL.md), not in compiled code. This makes it impossible to unit-test individual steps without running full Claude sessions. Behavioral regressions in the protocol are difficult to detect without integration tests.

**Checkpoint Reliability**: Pipeline Mode manifest-based resume prevents re-running completed phases on interruption. Single-mode (Mode A/B) has no resume — an interrupted comparison must restart from Step 1.

**Extensibility**: Generic tool design — `/sc:adversarial` is invocable by any SuperClaude command (the roadmap pipeline calls it internally for the debate step). Mode B injectable agents and Pipeline Mode YAML support a wide range of use cases beyond roadmap generation.

**Weakness**: The pipeline produces 6 artifacts in a configurable output directory. There is no cleanup mechanism for orphaned artifact directories from incomplete runs. Long-running projects can accumulate many stale artifact directories.

**Operational Determinism**: Tiebreaker protocol produces deterministic base selection for a given set of debate results. Scoring formula (quant + qual weights) is fixed. Position-bias double-pass produces consistent averaged scores.

**Weakness**: The core generate and debate steps invoke LLM agents whose outputs are non-deterministic. Two identical runs may produce different debate transcripts, different scores, and potentially different base selections — even when the tiebreaker protocol is deterministic, because the debate inputs driving the tiebreaker differ.
