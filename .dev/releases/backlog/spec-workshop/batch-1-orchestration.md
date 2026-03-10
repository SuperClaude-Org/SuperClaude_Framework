# Batch 1: Foundation & Orchestration Layer Analysis

> **Source workflow**: v2.01-Roadmap-v3 SpecDev (sc:roadmap adversarial failure diagnostic + sprint-spec refinement)
> **Analyzed files**: 8 files across checkpoints/ and diagnostics/
> **Purpose**: Extract the repeatable orchestration pattern for spec-workshop
> **Date**: 2026-02-23

---

## 1. Orchestration Pattern

### How the Workflow Was Structured

Two distinct workflow instances were found in the source files, representing two passes over the same problem domain. They share the same structural pattern but differ in task content.

**Workflow A** (diagnostics/tasklist-overview.md + tasklist-phases.md): The original 4-phase diagnostic and remediation workflow with 17 tasks.

**Workflow B** (checkpoints/workflow-tasklist.md + workflow-progress.md): A subsequent 4-phase refinement and validation workflow with 16 tasks + 4 saves.

Both follow the same meta-pattern:

```
Phase 1: Divergent analysis (parallel independent investigations)
    |
    v
Phase 1 synthesis (sequential fan-in that ranks/aggregates parallel results)
    |
    v
Phase 2: Divergent proposals (parallel independent solutions/debates)
    |
    v
Phase 2 synthesis (sequential fan-in)
    |
    v
Phase 3: Divergent validation (parallel adversarial debates on proposals)
    |
    v
Phase 3 synthesis (sequential fan-in)
    |
    v
Phase 4: Final integration (sequential — ranking, sprint design, or final spec)
```

The core pattern is **fan-out / fan-in** repeated across phases, with each phase consuming the synthesized output of the previous phase.

### Dependency Graphs (Copied Verbatim)

**Workflow A dependency graph** (from `diagnostics/tasklist-overview.md`):

```
T01.01 ──┐
T01.02 ──┤
T01.03 ──┼─→ T01.06 ─→ T02.01 ──┐
T01.04 ──┤              T02.02 ──┤
T01.05 ──┘              T02.03 ──┼─→ T03.01 ──┐
                         T02.04 ──┤   T03.02 ──┤
                         T02.05 ──┘   T03.03 ──┼─→ T04.01
                                      T03.04 ──┤
                                      T03.05 ──┘
```

**Workflow B dependency graph** (from `checkpoints/workflow-tasklist.md`):

```
T01 (spec-panel: DVL eval) ──────────────────┐
                                              ├──→ T01-SAVE
T02 (adversarial: spec vs root causes) ───────┘
    T02.01 (agent 1: RC1 coverage) ──┐
    T02.02 (agent 2: RC2 coverage) ──┤
    T02.03 (agent 3: RC3 coverage) ──┼──→ T02.06 (synthesis) ──→ T02-SAVE
    T02.04 (agent 4: RC4 coverage) ──┤
    T02.05 (agent 5: RC5 coverage) ──┘

T03 (spec-panel: 5 optimizations) ──→ T03-SAVE

T04 (adversarial: validate optimizations)
    T04.01 (debate: opt 1) ──┐
    T04.02 (debate: opt 2) ──┤
    T04.03 (debate: opt 3) ──┼──→ T04.06 (synthesis) ──→ T04-SAVE
    T04.04 (debate: opt 4) ──┤
    T04.05 (debate: opt 5) ──┘
```

### Structural Observations

1. **Fan-out width matches problem cardinality**: 5 root causes = 5 parallel agents. 5 optimizations = 5 parallel debates. The workflow does not use arbitrary parallelism; it is shaped by the number of independent concerns.

2. **Synthesis is always sequential and depends on ALL parallel branches**: T01.06 depends on T01.01-T01.05. T02.06 depends on T02.01-T02.05. No partial synthesis.

3. **Phase gates are hard barriers**: Phase N+1 cannot start until Phase N synthesis is complete. The dependency is on the synthesis output, not on individual parallel tasks.

4. **Save/checkpoint tasks are explicit nodes in the graph**, not implicit side-effects.

---

## 2. Checkpoint System

### What Was Saved at Each Checkpoint

Each checkpoint file follows a consistent format with three sections: verification (file existence + byte sizes), summary data (tables of key metrics), and key findings (narrative).

**CP-P1-END** (from `checkpoints/CP-P1-END.md`):

```markdown
# Checkpoint: CP-P1-END — Phase 1 Complete

**Timestamp**: 2026-02-22
**Phase**: Root Cause Investigation (T01.01–T01.06)

## Verification

- [x] `diagnostics/root-cause-01-invocation-wiring.md` (11,446 bytes)
- [x] `diagnostics/root-cause-02-spec-execution-gap.md` (15,186 bytes)
- [x] `diagnostics/root-cause-03-agent-dispatch.md` (14,357 bytes)
- [x] `diagnostics/root-cause-04-return-contract.md` (12,669 bytes)
- [x] `diagnostics/root-cause-05-claude-behavior.md` (12,365 bytes)
- [x] `diagnostics/ranked-root-causes.md` (13,463 bytes)

## Ranked Root Causes (Post-Adversarial Validation)

| Rank | Root Cause | Combined Score | Validated Likelihood | Validated Impact |
|------|-----------|---------------|---------------------|-----------------|
| 1 | RC1: Invocation Wiring Gap (Skill tool missing from allowed-tools) | 0.90 | 0.95 | 0.90 |
| 2 | RC5: Claude Behavioral Interpretation (rational fallback) | 0.79 | 0.85 | 0.70 |
| 3 | RC2: Specification-Execution Gap (ambiguous "Invoke" verb) | 0.77 | 0.80 | 0.85 |
| 4 | RC4: Return Contract Data Flow (no transport mechanism) | 0.75 | 0.80 | 0.75 |
| 5 | RC3: Agent Dispatch Mechanism (downstream of RC1) | 0.72 | 0.70 | 0.75 |

## Key Finding

The Skill tool is absent from sc:roadmap's allowed-tools list, making skill-to-skill invocation impossible. This is the primary root cause. All other root causes are either downstream consequences or compounding factors.

## Minimal Fix Set

3 fixes cover all 5 root causes:
1. Add `Skill` to allowed-tools in roadmap.md and SKILL.md
2. Rewrite Wave 2 step 3 with explicit tool-call syntax + fallback protocol
3. Define file-based return-contract.yaml convention for inter-skill data flow
```

**CP-P2-END** (from `checkpoints/CP-P2-END.md`):

```markdown
# Checkpoint: CP-P2-END — Phase 2 Complete

**Timestamp**: 2026-02-22
**Phase**: Solution Proposals (T02.01–T02.05)

## Verification

- [x] `solutions/solution-01-invocation-wiring.md` (18,364 bytes) — RC1 fix
- [x] `solutions/solution-02-spec-execution-gap.md` (16,252 bytes) — RC2 fix
- [x] `solutions/solution-03-agent-dispatch.md` (17,498 bytes) — RC3 fix
- [x] `solutions/solution-04-return-contract.md` (20,560 bytes) — RC4 fix
- [x] `solutions/solution-05-claude-behavior.md` (21,593 bytes) — RC5 fix

## Solution Summary

| Solution | Recommended Option | Confidence | Key Approach |
|----------|-------------------|------------|--------------|
| S01: Invocation Wiring | Option B (Task Agent Wrapper) + C fallback | 0.80 | Spawn Task agent to invoke sc:adversarial; fallback to inline protocol |
| S02: Spec-Execution Gap | Option B (Decompose into sub-steps) | ~0.85 | Expand step 3 into 3a-3f with explicit tool binding per sub-step |
| S03: Agent Dispatch | Option B (Agent Bootstrap Convention) | 0.82 | SKILL.md reads agent .md file and adopts its behavioral contract |
| S04: Return Contract | Option A (File-Based Contract) | 0.88 | Write return-contract.yaml to adversarial/ dir |
| S05: Claude Behavior | Combined B+C+D (Layered Defense) | 0.82 | Probe-and-branch + structured fallback + quality gate |
```

**CP-P3-END** (from `checkpoints/CP-P3-END.md`):

```markdown
# Checkpoint: CP-P3-END — Phase 3 Complete

**Timestamp**: 2026-02-22
**Phase**: Solution Debate (T03.01–T03.05)

## Verification

- [x] `debates/debate-01-invocation-wiring.md` (16,426 bytes)
- [x] `debates/debate-02-spec-execution-gap.md` (22,728 bytes)
- [x] `debates/debate-03-agent-dispatch.md` (25,985 bytes)
- [x] `debates/debate-04-return-contract.md` (24,761 bytes)
- [x] `debates/debate-05-claude-behavior.md` (23,823 bytes)

## Debate Results Summary

| Solution | Self-Reported Confidence | Debate Fix Likelihood | Delta | Verdict |
|----------|------------------------|----------------------|-------|---------|
| S01: Invocation Wiring | 0.80 | 0.760 | -0.04 | Implement with fallback |
| S02: Spec-Execution Gap | 0.85 | 0.749 | -0.10 | Implement after S01 |
| S03: Agent Dispatch | 0.82 | 0.700 | -0.12 | Implement last, with conditions |
| S04: Return Contract | 0.88 | 0.774 | -0.11 | Implement with refinements |
| S05: Claude Behavior | 0.82 | 0.716 | -0.10 | Implement with conditions |

## Key Cross-Debate Finding
All debates converged on implementation order: **S01 → S02 → S04 → S05 → S03**. S01 (Skill tool in allowed-tools) is the prerequisite for all others. S03 (Agent Dispatch) has zero observable effect until S01+S02 are applied.

## Top Unresolved Concerns (Cross-Debate)
1. Task agent Skill tool access is unverified (S01, S02)
2. Probe-and-branch failure classification uncertainty (S05)
3. Agent file "MANDATORY read" has no enforcement mechanism (S03)
4. Schema governance gap for return contract (S04)
```

**CP-P4-END** (from `checkpoints/CP-P4-END.md`):

```markdown
# Checkpoint: CP-P4-END — Phase 4 Complete (Final)

**Timestamp**: 2026-02-22
**Phase**: Ranking & Sprint Design (T04.01)

## Verification

- [x] `sprint-spec.md` (21,758 bytes)
- [x] Contains ranked problem list (5 root causes)
- [x] Contains ranked solution list (5 solutions)
- [x] Contains top 3 combined pairs with scores
- [x] Contains 3 epics with 15 total tasks
- [x] Contains risk register (7 risks)
- [x] Contains implementation order with dependency rationale
- [x] Contains Definition of Done checklist
- [x] Contains verification plan

## Top 3 Problem-Solution Pairs

| Rank | Pair | Combined Score |
|------|------|---------------|
| 1 | RC1 + S01: Invocation Wiring | 0.838 |
| 2 | RC4 + S04: Return Contract | 0.778 |
| 3 | RC2 + S02: Specification Rewrite | 0.776 |

## Workflow Complete

All 17 tasks across 4 phases executed successfully:
- Phase 1: 5 parallel root cause investigations + 1 adversarial ranking (6 tasks)
- Phase 2: 5 parallel solution proposals (5 tasks)
- Phase 3: 5 parallel adversarial debates (5 tasks)
- Phase 4: 1 final ranking + sprint design (1 task)

Total artifacts produced: 22 files across 4 directories.
```

### Checkpoint Format Summary

Every checkpoint contains:
1. **Header**: Checkpoint ID, timestamp, phase name, task range
2. **Verification checklist**: Every expected output file listed with `[x]` and byte size — this is the objective existence proof
3. **Summary table**: Key metrics from the phase in tabular form
4. **Key findings**: 1-3 sentences of narrative summary
5. **Unresolved concerns** (where applicable): Issues that carry forward to next phase

The byte-size verification is notable — it provides a non-trivial existence check. An empty or stub file would show as 0 bytes, making it detectable.

---

## 3. Progress Tracking

### Progress Table Format (Copied Verbatim from workflow-progress.md)

**Phase-level progress**:

```markdown
## Phase Status

| Phase | Status | Started | Completed | Key Findings |
|-------|--------|---------|-----------|--------------|
| 1: DVL Evaluation | COMPLETE | 15:09 | 15:19 | Top 3 scripts: verify_pipeline_completeness (0.95), verify_allowed_tools (0.95), validate_return_contract (0.85). 5 new tasks proposed for sprint-spec. |
| 2: Spec vs Root Causes | COMPLETE | 15:09 | 15:22 | Overall effectiveness: 0.737. All 5 debates: NEEDS AMENDMENTS. 15 gaps identified, 3 critical. |
| 3: Optimization Proposals | COMPLETE | 15:22 | 15:35 | 5 optimizations proposed totaling 5.75 hrs (38.3%) savings. Quality Advocate dissented on Opt 4. |
| 4: Optimization Debates | COMPLETE | 15:35 | 15:50 | All 5 adopted with modifications. Revised savings: 3.95 hrs (26.3%). Residual effectiveness impact: ~0.04. |
```

**Task-level progress**:

```markdown
## Task Status

| Task | Status | Output File | Notes |
|------|--------|-------------|-------|
| T01 | COMPLETE | T01-dvl-evaluation.md | 10 scripts evaluated, 5 sprint-spec additions proposed |
| T02.01 | COMPLETE | T02-debate-RC1.md | Score: 0.750, NEEDS AMENDMENTS (4 amendments) |
| T02.02 | COMPLETE | T02-debate-RC2.md | Score: 0.798, NEEDS AMENDMENTS (5 amendments) |
| T02.03 | COMPLETE | T02-debate-RC3.md | Score: 0.651, NEEDS AMENDMENTS (3 amendments) |
| T02.04 | COMPLETE | T02-debate-RC4.md | Score: 0.800, NEEDS AMENDMENTS (3 amendments) |
| T02.05 | COMPLETE | T02-debate-RC5.md | Score: 0.680, NEEDS AMENDMENTS (4 amendments) |
| T02.06 | COMPLETE | T02-synthesis.md | Aggregate score: 0.737, 15 gaps, 9 priority recommendations |
| T03 | COMPLETE | T03-optimizations.md | 5 optimizations: merge tasks, fold amendments, simplify fallback, defer validation, embed tests |
| T04.01 | COMPLETE | T04-debate-opt1.md | Score: 0.82, ADOPT-WITH-MODIFICATIONS |
| T04.02 | COMPLETE | T04-debate-opt2.md | Score: 0.80, ADOPT-WITH-MODIFICATIONS |
| T04.03 | COMPLETE | T04-debate-opt3.md | Score: 0.776, ADOPT-WITH-MODIFICATIONS |
| T04.04 | COMPLETE | T04-debate-opt4.md | Score: 0.64, ADOPT-WITH-MODIFICATIONS (most contentious) |
| T04.05 | COMPLETE | T04-debate-opt5.md | Score: 0.72, ADOPT-WITH-MODIFICATIONS |
| T04.06 | COMPLETE | T04-synthesis.md | All 5 adopted. Revised savings: 4.35 hrs (29.0%). Ordered by confidence. |
```

**Phase-specific metrics tables**:

```markdown
## Key Metrics (Phase 2)

| RC | Problem Score | Debate Score | Verdict | Weakest Dimension |
|----|--------------|-------------|---------|-------------------|
| RC1 | 0.900 | 0.750 | NEEDS AMENDMENTS | Confidence (0.65) |
| RC2 | 0.770 | 0.798 | NEEDS AMENDMENTS | Completeness (0.72) |
| RC3 | 0.720 | 0.651 | NEEDS AMENDMENTS | Root cause coverage (0.45) |
| RC4 | 0.750 | 0.800 | NEEDS AMENDMENTS | Completeness (0.72) |
| RC5 | 0.790 | 0.680 | NEEDS AMENDMENTS | Completeness (0.60) |

## Key Metrics (Phase 4)

| Opt# | Name | Debate Score | Recommendation | Net Savings |
|------|------|-------------|----------------|-------------|
| 1 | Merge Tasks 1.3+1.4+2.2 | 0.80 | ADOPT-WITH-MODIFICATIONS | 0.60 hrs |
| 2 | Fold amendments into parent ACs | 0.80 | ADOPT-WITH-MODIFICATIONS | 0.50 hrs |
| 3 | Simplify fallback 5→3 steps | 0.776 | ADOPT-WITH-MODIFICATIONS | 1.10 hrs |
| 4 | Defer fallback validation until after probe | 0.64 | ADOPT-WITH-MODIFICATIONS (conditional) | 1.25 hrs* |
| 5 | Embed Tests 1,3,4 into task ACs | 0.72 | ADOPT-WITH-MODIFICATIONS | 0.50 hrs |
```

**Save point registry**:

```markdown
## Save Points

| Checkpoint | Timestamp | Notes |
|------------|-----------|-------|
| T01-SAVE | 15:19 | Phase 1 complete |
| T02-SAVE | 15:22 | Phase 2 complete, synthesis written |
| T03-SAVE | 15:35 | Phase 3 complete, 5 optimizations proposed |
| T04-SAVE | 15:50 | Phase 4 complete, all optimizations debated and synthesized |
```

**Final summary**:

```markdown
## Final Summary

**Sprint-Spec Effectiveness**: 0.737 (all 5 root causes need amendments, estimated post-amendment: ~0.82)

**Optimization Savings**: 3.95 hrs = 26.3% of 15-hour sprint (down from 38.3% after debate modifications)

**Critical Actions**:
1. Fix G1: Missing-file guard contradiction (15 min, +0.03 RC4)
2. Add G2: Fallback validation test (1-2 hrs, +0.05 RC1)
3. Fix G5: Convergence sentinel in fallback (15 min, +0.03 RC5)
4. Add G3: Fallback-only sprint variant (30 min, +0.04 RC1)

**All 14 output files written to `workflow-outputs/`.**
```

### Observations on Progress Tracking

1. **Two levels of granularity**: Phase-level (coarse) and task-level (fine). Both are tracked in the same file.
2. **Metrics are domain-specific**: Phase 2 tracks debate scores and weakest dimensions. Phase 4 tracks debate scores and net savings. The progress file adapts its metric tables to what each phase produces.
3. **Timestamps are wall-clock**: Started/Completed times are recorded, enabling duration calculation.
4. **Output file is the proof**: Every task row references its output file. The file's existence IS the completion evidence.

---

## 4. Phase Gate Criteria

### Acceptance Criteria per Phase

**Phase 1 (Workflow A — Root Cause Investigation)**:
From `diagnostics/tasklist-phases.md`, T01.06:
```
**Checkpoint**: CP-P1-END — verify all outputs exist.
```
Verification in CP-P1-END: 6 files listed with byte sizes, all checked.

**Phase 1 (Workflow B — DVL Evaluation)**:
From `checkpoints/workflow-tasklist.md`, T01:
```
**Acceptance criteria**:
- [ ] All 10 DVL scripts evaluated with detection effectiveness scores
- [ ] Ranked list produced
- [ ] Sprint-spec refactor proposal with concrete task additions
- [ ] LOC/complexity estimates for each proposed addition
```

**Phase 2 gate** (Workflow A):
From `diagnostics/tasklist-phases.md`, after T02.05:
```
**Checkpoint**: CP-P2-END — verify all 5 solution files exist and reference their assigned root cause.
```
Note: Not just existence — also verifies cross-referencing (each solution must reference its assigned root cause).

**Phase 3 gate** (Workflow A):
From `diagnostics/tasklist-phases.md`, after T03.05:
```
**Checkpoint**: CP-P3-END — verify all 5 debate directories exist with scoring artifacts.
```
Note: Verifies both directory existence AND the presence of scoring artifacts within.

**Phase 3 (Workflow B — Optimization Proposals)**:
From `checkpoints/workflow-tasklist.md`, T03:
```
**Acceptance criteria**:
- [ ] Exactly 5 optimizations proposed
- [ ] Each has all 7 required fields
- [ ] All effectiveness_impact < 0.3
- [ ] At least 2 are zero-impact
- [ ] Total time savings > 20%
```
This is the most rigorous gate — it specifies quantitative constraints that can be objectively verified.

**Phase 4 gate** (Workflow A):
From `diagnostics/tasklist-phases.md`, T04.01:
```
**Checkpoint**: CP-P4-END — verify sprint-spec.md exists with all required sections.
```
CP-P4-END verification list:
```
- [x] `sprint-spec.md` (21,758 bytes)
- [x] Contains ranked problem list (5 root causes)
- [x] Contains ranked solution list (5 solutions)
- [x] Contains top 3 combined pairs with scores
- [x] Contains 3 epics with 15 total tasks
- [x] Contains risk register (7 risks)
- [x] Contains implementation order with dependency rationale
- [x] Contains Definition of Done checklist
- [x] Contains verification plan
```

### Gate Criteria Observations

1. **Escalating rigor**: Phase 1 gates check file existence. Phase 2 gates check cross-referencing. Phase 3 gates check quantitative constraints. Phase 4 gates check section completeness.
2. **Workflow B has more explicit acceptance criteria** than Workflow A, suggesting the pattern was refined between iterations.
3. **Gates are defined at two levels**: the tasklist defines what SHOULD be checked, and the checkpoint file records what WAS checked. This separation enables audit.

---

## 5. Tasklist Structure

### Task Registry Format (Copied from diagnostics/tasklist-overview.md)

```markdown
## Task Registry

| ID | Phase | Title | Depends On | Agent Type | Skill |
|----|-------|-------|------------|------------|-------|
| T01.01 | P1 | Invocation Wiring Gap | — | root-cause-analyst | /sc:troubleshoot |
| T01.02 | P1 | Spec-Execution Gap | — | root-cause-analyst | /sc:troubleshoot |
| T01.03 | P1 | Agent Dispatch Mechanism | — | root-cause-analyst | /sc:troubleshoot |
| T01.04 | P1 | Return Contract Data Flow | — | root-cause-analyst | /sc:troubleshoot |
| T01.05 | P1 | Claude Behavioral Interpretation | — | root-cause-analyst | /sc:troubleshoot |
| T01.06 | P1 | Adversarial Root Cause Ranking | T01.01–T01.05 | debate-orchestrator | /sc:adversarial |
| T02.01 | P2 | Solution: Invocation Wiring | T01.06 | self-review | /sc:reflect |
| T02.02 | P2 | Solution: Spec-Execution | T01.06 | self-review | /sc:reflect |
| T02.03 | P2 | Solution: Agent Dispatch | T01.06 | system-architect | /sc:design |
| T02.04 | P2 | Solution: Return Contract | T01.06 | system-architect | /sc:design |
| T02.05 | P2 | Solution: Claude Behavior | T01.06 | general-purpose | (raw analysis) |
| T03.01 | P3 | Debate: Invocation Wiring Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.02 | P3 | Debate: Spec-Execution Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.03 | P3 | Debate: Agent Dispatch Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.04 | P3 | Debate: Return Contract Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T03.05 | P3 | Debate: Claude Behavior Fix | T02.01–T02.05 | debate-orchestrator | /sc:adversarial |
| T04.01 | P4 | Ranking & Sprint Design | T03.01–T03.05 | system-architect | /sc:spec-panel |
```

### Per-Task Detail Format (from tasklist-phases.md)

Each task in the detailed tasklist has:

```markdown
### T01.01 — Invocation Wiring Gap Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-01-invocation-wiring.md`

**Description**:
[Multi-sentence description of what the task investigates]

**Analytical Lens**: [Single sentence framing the investigation angle]

**Investigation Steps**:
1. [Concrete step with file paths and line ranges]
2. [...]

**Evidence Requirements**:
- [What the output must contain]
- [Scoring requirement]
```

### Task Fields Summary

| Field | Required | Description |
|-------|----------|-------------|
| ID | Yes | Hierarchical: `T{phase}.{seq}` (e.g., T01.03) |
| Phase | Yes | Parent phase (P1-P4) |
| Title | Yes | Short descriptive name |
| Status | Yes | pending / in_progress / complete |
| Depends On | Yes | Task IDs or "—" for none |
| Agent Type | Yes | Agent persona to use (root-cause-analyst, debate-orchestrator, system-architect, self-review, general-purpose) |
| Skill | Yes | SuperClaude command to invoke (/sc:troubleshoot, /sc:adversarial, /sc:reflect, /sc:design, /sc:spec-panel, /sc:analyze) |
| Output | Yes | File path for the task's output artifact |
| Description | Yes | What the task does |
| Analytical Lens | Workflow A only | Framing for the investigation angle |
| Investigation Steps | Workflow A only | Numbered concrete steps |
| Evidence Requirements | Workflow A only | What the output must contain |
| Prompt | Workflow B only | Exact command + prompt text to execute |
| Acceptance Criteria | Workflow B only | Checklist of verifiable conditions |

### Scoring Dimensions (from tasklist-overview.md)

```markdown
## Scoring Dimensions

### Root Cause Ranking (Phase 1, T01.06)
- **Likelihood**: How probable is this root cause? (0.0–1.0)
- **Impact**: How much does this explain the observed failure? (0.0–1.0)
- **Combined**: `(likelihood * 0.6) + (impact * 0.4)`

### Solution Debate Scoring (Phase 3)
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Root cause coverage | 0.25 | Does the fix address the root cause completely? |
| Completeness | 0.20 | Does the fix handle edge cases and error paths? |
| Feasibility | 0.25 | Can the fix be implemented without major refactoring? |
| Blast radius | 0.15 | How many other skills/commands are affected? |
| Confidence | 0.15 | How confident are we this fix works? |

### Final Ranking (Phase 4, T04.01)
- **Problem rank**: `(likelihood * 0.6) + (impact * 0.4)` (from P1)
- **Solution rank**: `(fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)` (from P3)
```

---

## 6. File Registry

### Output File Registry (Workflow B, from workflow-tasklist.md)

```markdown
## Output File Registry

| File | Produced by | Phase |
|------|------------|-------|
| `workflow-outputs/T01-dvl-evaluation.md` | T01 | 1 |
| `workflow-outputs/T02-debate-RC1.md` | T02.01 | 2 |
| `workflow-outputs/T02-debate-RC2.md` | T02.02 | 2 |
| `workflow-outputs/T02-debate-RC3.md` | T02.03 | 2 |
| `workflow-outputs/T02-debate-RC4.md` | T02.04 | 2 |
| `workflow-outputs/T02-debate-RC5.md` | T02.05 | 2 |
| `workflow-outputs/T02-synthesis.md` | T02.06 | 2 |
| `workflow-outputs/T03-optimizations.md` | T03 | 3 |
| `workflow-outputs/T04-debate-opt1.md` | T04.01 | 4 |
| `workflow-outputs/T04-debate-opt2.md` | T04.02 | 4 |
| `workflow-outputs/T04-debate-opt3.md` | T04.03 | 4 |
| `workflow-outputs/T04-debate-opt4.md` | T04.04 | 4 |
| `workflow-outputs/T04-debate-opt5.md` | T04.05 | 4 |
| `workflow-outputs/T04-synthesis.md` | T04.06 | 4 |
| `workflow-progress.md` | All SAVE tasks | All |
```

### Checkpoint Registry (Workflow A, from tasklist-overview.md)

```markdown
## Checkpoint Registry

| Checkpoint | After | Verification |
|------------|-------|-------------|
| CP-P1-END | T01.06 | 5 root cause files + ranked-root-causes.md + adversarial/ dir in diagnostics/ |
| CP-P2-END | T02.05 | 5 solution files in solutions/, each referencing assigned root cause |
| CP-P3-END | T03.05 | 5 debate results in debates/, each with fix likelihood scores |
| CP-P4-END | T04.01 | sprint-spec.md with ranked lists, top 3 pairs, actionable sprint |
```

### Key File References (Workflow B, from workflow-tasklist.md)

```markdown
## Key File References

| Alias | Path |
|-------|------|
| `sprint-spec` | `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md` |
| `ranked-root-causes` | `.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md` |
| `dvl-brainstorm` | `.dev/releases/current/v2.01-Roadmap-v3/dvl-verification-layer/DVL-BRAINSTORM.md` |
| `spec-panel-review` | `.dev/releases/current/v2.01-Roadmap-v3/spec-panel-review.md` |
| `reflection-final` | `.dev/releases/current/v2.01-Roadmap-v3/reflection-final.md` |
| `output-dir` | `.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/` |
```

### Critical Source Files (Workflow A, from tasklist-overview.md)

```markdown
## Critical Source Files (Read-Only)

| File | Relevance |
|------|-----------|
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Wave 2 behavioral instructions (lines 130-143) |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Invocation patterns, return contract, agent parsing |
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Mode B stub (lines 505-513), full adversarial protocol |
| `src/superclaude/agents/debate-orchestrator.md` | Agent that should have been spawned |
| `.claude/commands/sc/roadmap.md` | Command entry point |
```

---

## 7. Execution Instructions

### Workflow B Execution Instructions (from workflow-tasklist.md)

```markdown
## Execution Instructions

To execute this tasklist:

```bash
/sc:task-unified --compliance strict --strategy systematic --parallel
```

The executor should:
1. Create `workflow-outputs/` directory before starting
2. Run Phase 1 (T01) → `/sc:save`
3. Run Phase 2 (T02.01-T02.05 in parallel) → T02.06 → `/sc:save`
4. Run Phase 3 (T03) → `/sc:save`
5. Run Phase 4 (T04.01-T04.05 in parallel) → T04.06 → `/sc:save`
6. Update `workflow-progress.md` after each phase with status and key findings
```

### Workflow B Execution Summary (from workflow-tasklist.md)

```markdown
## Execution Summary

| Phase | Tasks | Parallelism | Commands Used | Estimated Agents |
|-------|-------|-------------|---------------|------------------|
| 1 | T01 | Sequential | `/sc:spec-panel` | 1 |
| 2 | T02.01-T02.06 | 5 parallel + 1 sequential | `/sc:adversarial`, `/sc:analyze` | 6 |
| 3 | T03 | Sequential | `/sc:spec-panel` | 1 |
| 4 | T04.01-T04.06 | 5 parallel + 1 sequential | `/sc:adversarial`, `/sc:analyze` | 6 |
| Saves | 4 checkpoints | After each phase | `/sc:save` | 0 |
| **Total** | **16 tasks + 4 saves** | | | **14 agents** |
```

### Workflow A Execution Metadata (from tasklist-overview.md)

```markdown
**Format**: sc:task-unified (STRICT compliance)
**Total Tasks**: 17 across 4 phases
**Compliance**: STRICT (sub-agent verification, Sequential MCP required)
```

### Workflow A Phase Summary (from tasklist-overview.md)

```markdown
## Phase Summary

| Phase | Name | Tasks | Parallelism | Key Skill | Output Dir |
|-------|------|-------|-------------|-----------|------------|
| P1 | Root Cause Investigation | T01.01–T01.06 | 5 parallel + 1 sequential | /sc:troubleshoot, /sc:adversarial | diagnostics/ |
| P2 | Solution Proposals | T02.01–T02.05 | 5 parallel | /sc:reflect, /sc:design | solutions/ |
| P3 | Solution Debate | T03.01–T03.05 | 5 parallel | /sc:adversarial | debates/ |
| P4 | Ranking & Sprint Design | T04.01 | 1 sequential | /sc:spec-panel | ./ |
```

---

## 8. Recommendations for spec-workshop

Based on this analysis, here is how the orchestration layer of spec-workshop should be structured.

### 8.1 Core Orchestration Model: Plan-Then-Execute with Verification

The observed workflow has a clear two-stage nature:

1. **Plan stage**: A tasklist is generated as a complete, reviewable artifact BEFORE any execution begins. This tasklist contains the full dependency graph, all task definitions, all acceptance criteria, and the file registry.

2. **Execute stage**: The tasklist is executed mechanically — phases run in order, parallel tasks fan out, synthesis tasks fan in, checkpoints verify.

spec-workshop should formalize this separation:

```
PLAN PHASE:
  Input artifacts → Analysis → Tasklist generation → Tasklist review/improvement → Approved tasklist

EXECUTE PHASE:
  Approved tasklist → Phase-by-phase execution → Checkpoint verification → Progress tracking → Final output
```

The plan phase itself should be a mini-workflow (generate plan, review plan, revise plan). The execute phase is mechanical.

### 8.2 Recommended Tasklist Schema

Based on the two workflow instances, the following fields should be standardized:

```yaml
task:
  id: "T{phase}.{seq}"          # Hierarchical ID
  phase: "P{n}"                  # Parent phase
  title: string                  # Short descriptive name
  status: pending|in_progress|complete|blocked
  depends_on: [task_id, ...]     # Empty for independent tasks
  agent_type: string             # Agent persona
  skill: string                  # Command to invoke
  output: filepath               # Expected output artifact
  prompt: string                 # Exact prompt text (for automated execution)
  acceptance_criteria:            # Verifiable conditions
    - criterion: string
      type: existence|content|quantitative|cross-reference
      target: string             # What to check (file, field, value)
```

### 8.3 Recommended Checkpoint Format

```yaml
checkpoint:
  id: "CP-P{n}-END"
  timestamp: datetime
  phase: string
  verification:                  # Objective existence checks
    - file: filepath
      exists: true
      size_bytes: integer        # Non-zero proves non-trivial content
  metrics:                       # Phase-specific quantitative results
    - name: string
      value: number
      context: string
  key_findings: string           # 1-3 sentence narrative
  unresolved: [string, ...]      # Issues carrying forward
```

### 8.4 Parallel Verification Agents (Non-Interactive Mode)

When `--interactive` is NOT set, the design decisions specify that reviews go to parallel agents rather than humans. Based on the observed patterns, this should work as follows:

**Where human review would occur in interactive mode**:
1. After plan generation (review the tasklist)
2. At phase gates (review checkpoint data)
3. At synthesis points (review aggregated results)
4. At the final output (review the spec)

**Parallel verification agent design**:

For each review point, spawn at least 2 verification agents with different analytical lenses:

```
Verification Agent A: "Completeness Verifier"
  - Does the artifact contain all required sections?
  - Are all acceptance criteria met?
  - Are there any empty/stub sections?

Verification Agent B: "Consistency Verifier"
  - Do cross-references resolve correctly?
  - Are scores mathematically consistent?
  - Do summaries match their source data?

Verification Agent C: "Adversarial Verifier" (optional, for critical gates)
  - What is the weakest part of this output?
  - What claim is least supported by evidence?
  - What would an adversarial reviewer challenge?
```

The key insight from the observed workflow is that **the adversarial debate pattern IS the verification pattern**. Phases 2 and 4 of the workflow ARE verification phases. spec-workshop should make this explicit: every synthesis output gets at least a completeness + consistency check, and critical outputs get adversarial review.

### 8.5 Objective Progress Validation

The observed workflow uses two mechanisms for progress validation that do NOT rely on trusting agents:

1. **File existence + byte size**: If the checkpoint says the file should exist and be non-trivial, a simple file-system check confirms it. This is agent-independent.

2. **Quantitative constraints**: Acceptance criteria like "all effectiveness_impact < 0.3" and "total time savings > 20%" can be verified by parsing the output and checking the numbers. This is mechanically verifiable.

spec-workshop should build a **verification layer** that:

```
For each checkpoint:
  1. EXISTENCE CHECK: Verify all expected files exist with non-zero size
  2. STRUCTURAL CHECK: Parse each file for required sections/fields
  3. CONSTRAINT CHECK: Verify quantitative constraints from acceptance criteria
  4. CROSS-REFERENCE CHECK: Verify that files reference each other correctly
  5. RECORD: Write verification results to the progress file with pass/fail per check
```

This verification layer should be a **separate agent** (or deterministic script) that runs AFTER the producing agent completes and BEFORE the next phase begins. It should NOT be the same agent that produced the output.

### 8.6 Recommended Directory Structure for spec-workshop Outputs

```
{workspace}/
  plan/
    tasklist.md              # The generated plan
    plan-review.md           # Verification agent review of the plan
    tasklist-approved.md     # Final approved version
  phases/
    P1/                      # Phase 1 outputs
    P2/                      # Phase 2 outputs
    ...
  checkpoints/
    CP-P1-END.md
    CP-P2-END.md
    ...
  verification/
    V-P1-END.md              # Verification agent results for Phase 1
    V-P2-END.md
    ...
  progress.md                # Running progress tracker
  final-output.md            # The completed specification
```

### 8.7 Entry Point Design

The design decisions specify two entry modes: **problem-driven** and **improvement-driven**. Based on the observed workflows:

- **Workflow A** (diagnostics) is problem-driven: starts with a failure, investigates root causes, proposes solutions, debates them, produces a sprint spec.
- **Workflow B** (refinement) is improvement-driven: starts with an existing spec, evaluates it, proposes optimizations, debates them, produces an improved spec.

Both use the same orchestration pattern (fan-out/fan-in across phases). The difference is in Phase 1:

| Aspect | Problem-Driven | Improvement-Driven |
|--------|---------------|-------------------|
| Phase 1 input | Problem statement / failure evidence | Existing specification |
| Phase 1 task | Root cause investigation | Evaluation against criteria |
| Phase 1 output | Ranked root causes | Ranked improvement areas |
| Phases 2-4 | Solutions → Debates → Sprint | Optimizations → Debates → Revised spec |

spec-workshop should accept either entry point and route to the appropriate Phase 1 template while sharing Phases 2-4.

### 8.8 Key Anti-Patterns to Avoid

Based on what the observed workflow does well and what it could improve:

1. **Avoid self-assessment**: The CP-P3-END checkpoint reveals that self-reported confidence scores were consistently higher than adversarial debate scores (deltas of -0.04 to -0.12). The verification layer should ALWAYS use an independent agent, never ask the producing agent to verify its own work.

2. **Avoid unbounded parallelism**: Fan-out width should match the number of independent concerns, not be arbitrary. 5 root causes = 5 parallel agents. Do not spawn 10 agents "for speed."

3. **Avoid partial synthesis**: The synthesis task must wait for ALL parallel branches. No partial results. This is a hard constraint in the dependency graph.

4. **Avoid checkpoint-free execution**: The workflow checkpoints after EVERY phase. This enables resumability and provides a natural audit trail. spec-workshop should make checkpointing mandatory, not optional.

5. **Avoid prompt ambiguity**: Workflow B includes exact prompt text for every task. Workflow A does not — it describes investigation steps instead. For automated execution, exact prompts are better. For interactive mode, investigation steps are better (they guide human judgment). spec-workshop should generate both.

---

## Summary

The orchestration pattern observed in this workflow is a **phased fan-out/fan-in pipeline with checkpoint gates**. Its key properties are:

- **Parallel where independent, sequential where dependent**: Tasks within a phase run in parallel; phases run sequentially.
- **Synthesis as the gate**: Each phase ends with a synthesis task that aggregates parallel results. The synthesis output is the input to the next phase.
- **Checkpoint as proof**: Each phase boundary has a checkpoint file that records file existence (with byte sizes), key metrics, and narrative findings.
- **Two-level tracking**: Phase-level progress (coarse, for status at a glance) and task-level progress (fine, for debugging failures).
- **Explicit file registry**: Every expected output file is listed in advance, with its producing task and phase. This enables both planning and verification.
- **Adversarial validation as a first-class pattern**: The workflow uses adversarial debate not just as a quality measure but as the primary mechanism for validating proposals. This pattern recurs in both workflows.

The spec-workshop orchestration layer should implement this pattern as a generic, configurable framework — parameterized by the number of concerns (fan-out width), the scoring dimensions, the checkpoint verification criteria, and the entry point mode (problem-driven vs. improvement-driven).
