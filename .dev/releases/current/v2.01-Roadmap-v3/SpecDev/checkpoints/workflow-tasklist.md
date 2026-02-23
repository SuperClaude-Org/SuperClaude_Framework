# Workflow Tasklist: Sprint-Spec Refinement & Validation

> **Status**: CREATED — Not yet executed
> **Created**: 2026-02-23
> **Execute via**: `/sc:task-unified --compliance strict`
> **Progress file**: `.dev/releases/current/v2.01-Roadmap-v3/workflow-progress.md`
> **Save frequency**: `/sc:save` after each phase completion

## Overview

4-phase workflow to validate, debate, and optimize the sprint specification for the sc:roadmap adversarial pipeline remediation. All phases use SuperClaude custom commands for structured execution.

## Dependency Graph

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

## Key File References

| Alias | Path |
|-------|------|
| `sprint-spec` | `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md` |
| `ranked-root-causes` | `.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md` |
| `dvl-brainstorm` | `.dev/releases/current/v2.01-Roadmap-v3/dvl-verification-layer/DVL-BRAINSTORM.md` |
| `spec-panel-review` | `.dev/releases/current/v2.01-Roadmap-v3/spec-panel-review.md` |
| `reflection-final` | `.dev/releases/current/v2.01-Roadmap-v3/reflection-final.md` |
| `output-dir` | `.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/` |

---

## Phase 1: DVL Script Evaluation & Sprint-Spec Refactor Proposal

### T01: Evaluate Deferred DVL Scripts via /sc:spec-panel

**Command**: `/sc:spec-panel`
**Depends on**: None
**Output**: `{output-dir}/T01-dvl-evaluation.md`

**Prompt**:
```
/sc:spec-panel Review the deferred DVL (Deterministic Verification Layer) scripts defined in
@.dev/releases/current/v2.01-Roadmap-v3/dvl-verification-layer/DVL-BRAINSTORM.md

Context: The sprint specification at @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
implements 3 epics to fix the sc:roadmap adversarial pipeline failure. The DVL scripts were
deferred to backlog but represent programmatic verification that could catch non-adherence
to the sc:roadmap process at runtime.

Tasks for the panel:
1. Evaluate each of the 10 DVL scripts (3 tiers: pre-gate, post-gate, cross-phase) against
   their ability to CATCH instances where the sc:roadmap process is not being strictly followed
2. Rank the scripts by detection effectiveness (which would catch the MOST violations?)
3. Identify which scripts could be implemented as lightweight pre/post hooks vs. requiring
   full implementation effort
4. Propose a refactored version of the sprint-spec that incorporates creation and integration
   of the top-ranked DVL scripts as additional tasks within the existing 3-epic structure
5. For each proposed addition, estimate: LOC, complexity, dependencies on existing tasks

Write findings to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T01-dvl-evaluation.md
```

**Acceptance criteria**:
- [ ] All 10 DVL scripts evaluated with detection effectiveness scores
- [ ] Ranked list produced
- [ ] Sprint-spec refactor proposal with concrete task additions
- [ ] LOC/complexity estimates for each proposed addition

### T01-SAVE: Checkpoint

**Command**: `/sc:save`
**Depends on**: T01
**Action**: Save session state after Phase 1 completion. Update `workflow-progress.md` with T01 status.

---

## Phase 2: Adversarial Debate — Spec Effectiveness vs Root Causes

### T02: Parallel Adversarial Debate on Spec Coverage

**Depends on**: T01 (informational only — Phase 2 can start after T01-SAVE)

Spawn 5 parallel agents. Each agent debates whether the sprint-spec effectively mitigates one specific root cause.

#### T02.01: RC1 — Invocation Wiring Gap

**Command**: `/sc:adversarial --compare`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T02-debate-RC1.md`

**Prompt**:
```
/sc:adversarial --compare

Artifact A: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md (the proposed fix)
Artifact B: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md (section: RC1 Invocation Wiring Gap)

Debate question: Does the sprint specification EFFECTIVELY mitigate RC1 (Invocation Wiring Gap)?

RC1 Summary: The Skill tool is absent from allowed-tools in both roadmap.md and SKILL.md.
Zero precedents for cross-skill invocation exist. Likelihood: 0.90, Impact: 0.90, Score: 0.900.

Evaluate on 5 dimensions:
1. Root cause coverage — Does the spec address ALL aspects of RC1?
2. Completeness — Are there gaps in the proposed fix?
3. Feasibility — Can the fix be implemented as described?
4. Blast radius — Could the fix introduce new problems?
5. Confidence — How confident are we this fix resolves RC1?

Score each dimension 0.0-1.0. Provide FOR and AGAINST arguments.
Write output to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC1.md
```

#### T02.02: RC2 — Specification-Execution Gap

**Command**: `/sc:adversarial --compare`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T02-debate-RC2.md`

**Prompt**:
```
/sc:adversarial --compare

Artifact A: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
Artifact B: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md (section: RC2 Specification-Execution Gap)

Debate question: Does the sprint specification EFFECTIVELY mitigate RC2 (Specification-Execution Gap)?

RC2 Summary: The verb "Invoke" is undefined in tool-call terms. Wave 4 uses "Dispatch" (maps to Task agents)
while Wave 2 uses "Invoke" (maps to nothing). Five sub-operations compressed into one step.
Likelihood: 0.75, Impact: 0.80, Score: 0.770.

Evaluate on 5 dimensions (same as T02.01). Score each 0.0-1.0.
Write output to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC2.md
```

#### T02.03: RC3 — Agent Dispatch Mechanism

**Command**: `/sc:adversarial --compare`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T02-debate-RC3.md`

**Prompt**:
```
/sc:adversarial --compare

Artifact A: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
Artifact B: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md (section: RC3 Agent Dispatch Mechanism)

Debate question: Does the sprint specification EFFECTIVELY mitigate RC3 (Agent Dispatch Mechanism)?

RC3 Summary: No programmatic binding exists between sc:adversarial and debate-orchestrator.
System-architect was selected due to keyword affinity. Likelihood: 0.70, Impact: 0.75, Score: 0.720.

Evaluate on 5 dimensions (same as T02.01). Score each 0.0-1.0.
Write output to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC3.md
```

#### T02.04: RC4 — Return Contract Data Flow

**Command**: `/sc:adversarial --compare`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T02-debate-RC4.md`

**Prompt**:
```
/sc:adversarial --compare

Artifact A: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
Artifact B: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md (section: RC4 Return Contract Data Flow)

Debate question: Does the sprint specification EFFECTIVELY mitigate RC4 (Return Contract Data Flow)?

RC4 Summary: The return contract specifies 6 structured fields but defines no transport mechanism.
Only inter-agent data flow precedent (sc:cleanup-audit) uses file-based fan-out/fan-in which
the adversarial return contract does not adopt. Likelihood: 0.75, Impact: 0.75, Score: 0.750.

Evaluate on 5 dimensions (same as T02.01). Score each 0.0-1.0.
Write output to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC4.md
```

#### T02.05: RC5 — Claude Behavioral Interpretation

**Command**: `/sc:adversarial --compare`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T02-debate-RC5.md`

**Prompt**:
```
/sc:adversarial --compare

Artifact A: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
Artifact B: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md (section: RC5 Claude Behavioral Interpretation)

Debate question: Does the sprint specification EFFECTIVELY mitigate RC5 (Claude Behavioral Interpretation)?

RC5 Summary: Claude's fallback preserved ~20% of adversarial pipeline functionality (variant generation + rough merge)
while skipping 80% (diff analysis, debate, scoring, refactoring plan, provenance).
Likelihood: 0.85, Impact: 0.70, Score: 0.790.

Evaluate on 5 dimensions (same as T02.01). Score each 0.0-1.0.
Write output to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC5.md
```

#### T02.06: Synthesis — Aggregate Debate Results

**Command**: `/sc:analyze`
**Depends on**: T02.01, T02.02, T02.03, T02.04, T02.05
**Output**: `{output-dir}/T02-synthesis.md`

**Prompt**:
```
/sc:analyze Review and synthesize the 5 adversarial debate results:
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC1.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC2.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC3.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC4.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-debate-RC5.md

Produce a synthesis report containing:
1. Aggregate coverage matrix (RC × dimension scores)
2. Weakest coverage areas (lowest dimension scores across all RCs)
3. Strongest coverage areas
4. Overall spec effectiveness score (weighted by RC problem scores)
5. Specific gaps that require sprint-spec amendments
6. Recommendations ranked by urgency

Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-synthesis.md
```

### T02-SAVE: Checkpoint

**Command**: `/sc:save`
**Depends on**: T02.06
**Action**: Save session state after Phase 2 completion. Update `workflow-progress.md` with T02 status and key scores.

---

## Phase 3: Optimization Proposals via /sc:spec-panel

### T03: Propose 5 Time-Saving Optimizations

**Command**: `/sc:spec-panel`
**Depends on**: T02-SAVE (benefits from debate insights)
**Output**: `{output-dir}/T03-optimizations.md`

**Prompt**:
```
/sc:spec-panel Review @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md and propose
exactly 5 optimizations that will result in TIME SAVINGS while MINIMIZING the impact on
the spec's effectiveness at achieving its objectives.

Context files for understanding objectives:
- @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T02-synthesis.md (Phase 2 debate results)
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T01-dvl-evaluation.md (Phase 1 DVL eval)

For each optimization, provide:
1. **Name**: Short descriptive title
2. **Current state**: What the spec currently requires
3. **Proposed change**: What the optimization would change
4. **Time savings**: Estimated reduction (hours or percentage)
5. **Effectiveness impact**: Score 0.0-1.0 (0 = no impact, 1.0 = completely undermines spec)
6. **Risk assessment**: What could go wrong
7. **Net benefit formula**: time_saved * (1 - effectiveness_impact) = net_benefit

Constraints:
- Each optimization must have effectiveness_impact < 0.3 (cannot reduce spec effectiveness by >30%)
- Total time savings across all 5 must exceed 20%
- At least 2 optimizations must be zero-effectiveness-impact (pure efficiency gains)

Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
```

**Acceptance criteria**:
- [ ] Exactly 5 optimizations proposed
- [ ] Each has all 7 required fields
- [ ] All effectiveness_impact < 0.3
- [ ] At least 2 are zero-impact
- [ ] Total time savings > 20%

### T03-SAVE: Checkpoint

**Command**: `/sc:save`
**Depends on**: T03
**Action**: Save session state after Phase 3 completion. Update `workflow-progress.md` with T03 status.

---

## Phase 4: Adversarial Validation of Optimizations

### T04: 5 Parallel Adversarial Debates on Optimization Proposals

**Depends on**: T03

Spawn 5 parallel agents. Each agent runs `/sc:adversarial` to debate one optimization proposal from T03.

#### T04.01: Debate Optimization 1

**Command**: `/sc:adversarial`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T04-debate-opt1.md`

**Prompt**:
```
/sc:adversarial

Read @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
and extract Optimization 1.

Debate question: Should Optimization 1 be adopted into the sprint specification?

Context:
- Sprint spec: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
- Root causes: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md

Conduct a structured adversarial debate:
- FOR position: Argue why this optimization should be adopted (time savings, efficiency)
- AGAINST position: Argue why this optimization is risky or undermines effectiveness
- CROSS-EXAMINATION: Each side challenges the other's strongest argument
- VERDICT: Score on 5 dimensions (time_savings, effectiveness_preservation, feasibility, risk, net_benefit)
- RECOMMENDATION: adopt / adopt-with-modifications / reject
- If adopt-with-modifications: specify exact modifications needed

Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt1.md
```

#### T04.02: Debate Optimization 2

**Command**: `/sc:adversarial`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T04-debate-opt2.md`

**Prompt**: (Same structure as T04.01 but extract Optimization 2 from T03-optimizations.md)
```
/sc:adversarial

Read @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
and extract Optimization 2.

Debate question: Should Optimization 2 be adopted into the sprint specification?

Context:
- Sprint spec: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
- Root causes: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md

Conduct structured adversarial debate (FOR/AGAINST/CROSS-EXAMINATION/VERDICT/RECOMMENDATION).
Score on 5 dimensions. Recommend: adopt / adopt-with-modifications / reject.
Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt2.md
```

#### T04.03: Debate Optimization 3

**Command**: `/sc:adversarial`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T04-debate-opt3.md`

**Prompt**: (Same structure, extract Optimization 3)
```
/sc:adversarial

Read @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
and extract Optimization 3.

Debate question: Should Optimization 3 be adopted into the sprint specification?

Context:
- Sprint spec: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
- Root causes: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md

Conduct structured adversarial debate (FOR/AGAINST/CROSS-EXAMINATION/VERDICT/RECOMMENDATION).
Score on 5 dimensions. Recommend: adopt / adopt-with-modifications / reject.
Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt3.md
```

#### T04.04: Debate Optimization 4

**Command**: `/sc:adversarial`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T04-debate-opt4.md`

**Prompt**: (Same structure, extract Optimization 4)
```
/sc:adversarial

Read @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
and extract Optimization 4.

Debate question: Should Optimization 4 be adopted into the sprint specification?

Context:
- Sprint spec: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
- Root causes: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md

Conduct structured adversarial debate (FOR/AGAINST/CROSS-EXAMINATION/VERDICT/RECOMMENDATION).
Score on 5 dimensions. Recommend: adopt / adopt-with-modifications / reject.
Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt4.md
```

#### T04.05: Debate Optimization 5

**Command**: `/sc:adversarial`
**Agent**: Task (subagent_type: general-purpose)
**Output**: `{output-dir}/T04-debate-opt5.md`

**Prompt**: (Same structure, extract Optimization 5)
```
/sc:adversarial

Read @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T03-optimizations.md
and extract Optimization 5.

Debate question: Should Optimization 5 be adopted into the sprint specification?

Context:
- Sprint spec: @.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md
- Root causes: @.dev/releases/current/v2.01-Roadmap-v3/diagnostics/ranked-root-causes.md

Conduct structured adversarial debate (FOR/AGAINST/CROSS-EXAMINATION/VERDICT/RECOMMENDATION).
Score on 5 dimensions. Recommend: adopt / adopt-with-modifications / reject.
Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt5.md
```

#### T04.06: Synthesis — Final Optimization Verdicts

**Command**: `/sc:analyze`
**Depends on**: T04.01, T04.02, T04.03, T04.04, T04.05
**Output**: `{output-dir}/T04-synthesis.md`

**Prompt**:
```
/sc:analyze Synthesize the 5 adversarial debate results on optimization proposals:
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt1.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt2.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt3.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt4.md
- @.dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-debate-opt5.md

Produce a final synthesis:
1. Verdict table: Optimization × (adopt/modify/reject) with debate scores
2. Adopted optimizations: list with any required modifications from debates
3. Rejected optimizations: list with rejection rationale
4. Modified optimizations: original → debated version with specific changes
5. Projected total time savings (only counting adopted/modified optimizations)
6. Projected effectiveness preservation score
7. FINAL RECOMMENDATION: Ordered list of optimizations to apply to sprint-spec.md

Write to .dev/releases/current/v2.01-Roadmap-v3/workflow-outputs/T04-synthesis.md
```

### T04-SAVE: Checkpoint

**Command**: `/sc:save`
**Depends on**: T04.06
**Action**: Save session state after Phase 4 completion. Update `workflow-progress.md` with final status, all scores, and next steps.

---

## Execution Summary

| Phase | Tasks | Parallelism | Commands Used | Estimated Agents |
|-------|-------|-------------|---------------|------------------|
| 1 | T01 | Sequential | `/sc:spec-panel` | 1 |
| 2 | T02.01-T02.06 | 5 parallel + 1 sequential | `/sc:adversarial`, `/sc:analyze` | 6 |
| 3 | T03 | Sequential | `/sc:spec-panel` | 1 |
| 4 | T04.01-T04.06 | 5 parallel + 1 sequential | `/sc:adversarial`, `/sc:analyze` | 6 |
| Saves | 4 checkpoints | After each phase | `/sc:save` | 0 |
| **Total** | **16 tasks + 4 saves** | | | **14 agents** |

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
