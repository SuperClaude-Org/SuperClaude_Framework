# v2.21 Workflow Parallelization — Session Findings & Design Brief

**Date**: 2026-03-09
**Branch**: fix/v2.20-WorkflowEvolution
**Status**: Brainstormed, debated, ranked — ready for spec/design
**Related**: v2.19 spec-fidelity gap analysis, adversarial merge pipeline

---

## 1. Context: Why Parallelization

The SuperClaude pipeline (spec → extraction → roadmap → validation → tasklist → sprint) currently runs **mostly sequentially**, taking **20-60 minutes end-to-end**. Each LLM subprocess call takes 30-120 seconds. Sprint execution alone is 10-30 minutes.

Two investigations in this session informed these proposals:

1. **Adversarial comparison** of `spec-fidelity-gap-analysis-gpt.md` vs `spec-fidelity-gap-analysis.md` — produced a merged analysis identifying that 75% of pipeline deviations originate at the roadmap level and propagate unchecked. The merged output is at `docs/generated/spec-fidelity-gap-analysis-merged.md`.

2. **Brainstorming session** with 3 parallel brainstorm agents + adversarial debate, producing 5 ranked parallelization proposals.

---

## 2. The Spec-Fidelity Gap (Prerequisite Context)

Before parallelizing validation, understand what's being validated. The merged gap analysis found:

### Current State
- **No spec-fidelity gate exists** at any pipeline boundary
- All existing gates check **structural properties** (frontmatter, line counts) not semantic fidelity
- The `sc-roadmap-protocol` skill docs **contain** spec-fidelity prompts but they are **not wired into the CLI executor**
- `_cross_refs_resolve()` in MERGE_GATE **always returns True**
- `build_reflect_prompt` accepts 3 parameters **never interpolated** into prompt text (dead code)
- Semantic gates are classified as **advisory**, not blocking (SKILL.md:864-868)

### Deviation Counts from v2.19

| Boundary | Deviations | HIGH | MEDIUM | LOW |
|----------|-----------|------|--------|-----|
| Spec → Roadmap | 29 | 5 | 12 | 12 |
| Roadmap → Tasklist | 15 | 3 | 6 | 6 |
| Tasklist → Implementation | 1 | 0 | 0 | 1 |

### Proposed Validation Architecture (from merged analysis)
- **Layered validation**: each artifact validated against its **immediate upstream** (not original spec)
- **Harness pattern**: repeatable, read-only validation wrapper emitting normalized deviation reports
- **Normalized output contract**: 6-field schema (source_pair, severity, deviation, evidence, likely_impact, recommended_correction)
- **4 solutions proposed** — see `docs/generated/spec-fidelity-gap-analysis-merged.md` Sections 5.1-5.5

---

## 3. Five Parallelization Proposals (Ranked)

### Adversarial Debate Methodology
- 3 parallel brainstorm agents generated P3-P5 independently
- 2-advocate adversarial debate (Risk & Complexity vs Effectiveness & Impact)
- 2 rounds of structured debate with rebuttals
- Scoring: Effectiveness × 0.4 + (10 - Complexity) × 0.3 + (10 - Risk) × 0.3

### Final Ranking

| Rank | ID | Proposal | Eff. | Cmplx. | Risk | Score |
|------|-----|----------|:---:|:---:|:---:|:---:|
| 1 | P1 | Phase-Level Spec-Fidelity Validation | 5 | 3 | 2 | **5.6** |
| 2 | P2 | Tasklist Batch Validation | 6 | 5 | 4 | **5.2** |
| 3 | P5 | DAG Wave Executor | 9 | 8 | 7 | **5.1** |
| 4 | P4 | Warm-Started Boundary Sentinels | 7 | 7 | 6 | **4.6** |
| 5 | P3 | Speculative Scoring | 6 | 6 | 8 | **3.6** |

### Recommended Build Order
```
P1 (foundation) → P2 (new validation layer) → P5-A (sprint parallelism) → P4 (sentinels) → P5-B (cross-phase) → P3
```

---

## 4. Proposal Details

### P1: Phase-Level Spec-Fidelity Validation (RANK 1 — Score 5.6)

**What**: After roadmap generation completes, split the roadmap by phases (M1-M5). Spawn one parallel agent per phase, each given identical instructions: "Compare this phase against the source spec and enumerate deviations." Aggregate results into a unified deviation report.

**Why first**: Nearly trivial to implement. Proves the parallel fan-out + result aggregation infrastructure that P2, P4, and P5 all reuse. Best risk-adjusted ROI.

**How it works**:
1. Roadmap is generated (complete, merged)
2. Parse roadmap into phase sections (M1, M2, M3, M4, M5)
3. Spawn N parallel validation agents, each receiving: (a) the spec, (b) one phase section, (c) identical validation instructions
4. Each agent outputs a deviation report for its phase using the normalized 6-field contract
5. Aggregator merges deviation reports, deduplicates, assigns severity
6. Gate: block on HIGH-severity deviations, warn on MEDIUM

**Key risk**: Cross-phase deviations (M2 references something M3 defines) missed by both agents.
**Mitigation**: Lightweight cross-reference pass after parallel results merge.

**Infrastructure created**: Parallel agent fan-out, result aggregation, deviation-report merge pattern — reused by P2 and P4.

---

### P2: Tasklist Batch Validation (RANK 2 — Score 5.2)

**What**: After tasklist generation, validate each tasklist file against the roadmap. Within each tasklist, group tasks into batches of 5 and assign each batch to a parallel agent checking roadmap-to-tasklist fidelity.

**Why second**: Creates a validation layer that **doesn't exist today**. Currently there is ZERO automated roadmap-to-tasklist fidelity checking. Reuses P1's fan-out infrastructure.

**How it works**:
1. Tasklist files generated (phase-1-tasklist.md through phase-5-tasklist.md)
2. For each tasklist file, spawn a parallel agent given: (a) the roadmap, (b) the tasklist file, (c) validation instructions
3. Within each tasklist, group tasks into batches of 5
4. Each batch agent validates: deliverables present, signatures preserved, traceability IDs valid, dependency chains match roadmap
5. Agents get full tasklist as read-only context but only validate their assigned batch
6. Aggregate results into unified fidelity report

**Key risk**: Cross-batch dependencies — task 6 in batch 2 depends on task 2 in batch 1.
**Mitigation**: Give each agent read-only access to full task list while scoping validation to their batch.

**Debate outcome**: Both advocates agreed the "zero existing validation" point was decisive — this creates new value, not just parallelizes existing work.

---

### P5: Dependency-Graph Wave Executor (RANK 3 — Score 5.1)

**What**: Parse all tasklist files, build a DAG of task dependencies across phases. Phase boundaries become soft constraints. Tasks run as soon as all dependencies complete, dispatched to a bounded worker pool (3-5 concurrent Claude subprocesses).

**Why third (but phased)**: Targets the dominant bottleneck (sprint execution: 10-30 min). 40-60% savings potential. But implicit dependencies are a silent correctness killer.

**Phase A** (build first): Within-phase task parallelism only, using declared dependencies, 3-worker pool. Captures 20-30% savings with bounded risk.

**Phase B** (build later): Cross-phase pipelining with soft phase boundaries. Only after dependency tooling matures.

**Key risk**: Implicit dependencies not captured in tasklist metadata.
**Mitigation**: Pre-flight scan of task input file references vs other tasks' declared deliverables; auto-inject missing edges or conservatively serialize ambiguous tasks.

**Debate outcome**: Both advocates agreed on phased rollout. "Distributed systems problem" framing is accurate but the complexity ceiling is knowable with bounded worker pool.

---

### P4: Warm-Started Boundary Sentinels (RANK 4 — Score 4.6)

**What**: When an artifact is produced, simultaneously: (1) next pipeline step begins, and (2) a validation agent spawns to ingest and index the artifact into a structured checklist ("baseline"). Agent idles until downstream artifact is ready, then only performs the comparison pass. WARNING-level checks run in parallel with downstream generation.

**How it works**:
1. Extraction.md produced → sentinel spawns, builds FR/NFR checklist → idles
2. Roadmap generation begins concurrently
3. Roadmap produced → sentinel activates, compares roadmap against baseline
4. Simultaneously, roadmap sentinel spawns for roadmap→tasklist boundary
5. WARNING checks (Interleave, Decomposition) run concurrent with tasklist generation

**Key risk**: Stale baseline on retry — if upstream artifact is regenerated, sentinel holds outdated baseline.
**Mitigation**: Content hash check before comparison; re-ingest if hash mismatch.

**Key dependency**: Artifact-level event emission from executor (fire when file written, not when step completes).

---

### P3: Speculative Scoring with Debate-Gated Merge (RANK 5 — Score 3.6)

**What**: After adversarial debate Round 1, begin scoring speculatively. 3 qualitative scorers (10 criteria each) + 1 quantitative metrics agent run concurrently with debate Rounds 2-3. Reconciliation step after debate checks if >20% of scores invalidated.

**Why last**: Highest downside variance. If Round 1 doesn't predict final conclusions, speculative scoring is waste and makes the pipeline slower than sequential.

**Key risk**: Late-round debate reversals invalidate speculative scores.
**Prerequisite**: Empirical data on Round 1 signal quality before attempting.

---

## 5. Key Debate Insights

### What both advocates agreed on:
- **P1 is the foundation** — its infrastructure (fan-out, aggregation, deviation-report merge) is reused by everything else
- **P2 creates new value** — the "zero existing validation" argument was decisive
- **P5 needs phased rollout** — within-phase first, cross-phase later
- **Implicit dependencies are the hardest problem** — affects P2 (cross-batch) and P5 (cross-task)
- **P3 should be deferred** until empirical debate signal quality data exists

### Key architectural decisions surfaced:
1. **Normalized deviation report contract** should be the shared output format for P1, P2, and P4
2. **Parallel agent fan-out pattern** (identical instructions, partitioned input, aggregated output) is the reusable primitive
3. **Layered validation principle** (each artifact vs immediate upstream, not original spec) must be enforced
4. **Advisory → blocking policy change** for semantic gates is a prerequisite for all validation proposals

---

## 6. Dependencies and Prerequisites

### Before P1:
- Spec-fidelity validation prompt exists (Solution A from gap analysis)
- Normalized deviation report contract defined
- Roadmap parser that can split by phase sections

### Before P2:
- P1's fan-out/aggregation infrastructure
- Roadmap-to-tasklist validation prompt
- Tasklist parser that can group tasks into batches

### Before P5 Phase A:
- Task dependency declarations are machine-parseable in tasklist format
- Bounded worker pool implementation for Claude subprocesses
- DAG builder from tasklist dependency fields

### Before P4:
- Artifact-level event emission from pipeline executor
- Content hashing for artifact versioning
- Sentinel lifecycle management (spawn, idle, activate, teardown)

---

## 7. Related Files

### Adversarial Merge Artifacts (this session)
- `docs/generated/spec-fidelity-gap-analysis-merged.md` — merged gap analysis (base document)
- `docs/generated/spec-fidelity-gap-analysis-gpt.md` — Variant A (GPT briefing)
- `docs/generated/spec-fidelity-gap-analysis.md` — Variant B (Claude analysis)
- `docs/generated/adversarial/diff-analysis.md` — Step 1
- `docs/generated/adversarial/debate-transcript.md` — Step 2
- `docs/generated/adversarial/base-selection.md` — Step 3
- `docs/generated/adversarial/refactor-plan.md` — Step 4
- `docs/generated/adversarial/merge-log.md` — Step 5

### Pipeline Infrastructure
- `src/superclaude/cli/pipeline/gates.py` — gate engine
- `src/superclaude/cli/roadmap/gates.py` — roadmap step gates
- `src/superclaude/cli/roadmap/executor.py` — roadmap pipeline orchestrator
- `src/superclaude/cli/roadmap/validate_executor.py` — validate orchestrator
- `src/superclaude/cli/roadmap/validate_gates.py` — validate gates
- `src/superclaude/cli/roadmap/validate_prompts.py` — validate prompts

### Sprint Runner
- `src/superclaude/cli/sprint/executor.py` — sprint execution engine
- `src/superclaude/cli/sprint/process.py` — Claude subprocess management

### Skill Protocols
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — roadmap protocol (Wave 1-4)
- `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md` — spec-fidelity prompts (NOT wired)
- `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` — tasklist protocol

### Existing Validation Implementation
- `src/superclaude/cli/roadmap/commands.py` — CLI surface
- `src/superclaude/cli/roadmap/models.py` — pipeline data models
- `tests/roadmap/test_validate_*.py` — 7 test files (96 tests total)

---

## 8. Open Questions for Spec/Design Phase

1. Should P1 agents receive the **full spec** or just the **spec sections relevant to their phase**? Full spec is simpler but higher token cost.
2. What is the right **batch size** for P2? 5 tasks per batch? Or dynamic based on task complexity?
3. Should the normalized deviation report contract be a **Python dataclass** or a **YAML/Markdown schema**?
4. Should the parallel fan-out use **Claude Code Task agents** or **direct subprocess spawning** via the sprint runner?
5. How should **cross-phase/cross-batch deviations** be detected? Post-aggregation pass? Or overlap in agent context windows?
6. Should P5's DAG builder be a **pre-sprint analysis step** or **runtime dynamic dispatch**?
