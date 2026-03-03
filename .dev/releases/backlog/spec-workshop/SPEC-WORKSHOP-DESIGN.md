# SPEC-WORKSHOP-DESIGN.md
# Complete Blueprint for `/sc:spec-workshop`

**Version**: 1.0.0
**Date**: 2026-02-23
**Status**: Design Complete -- Ready for Implementation
**Source**: Extracted from v2.01-Roadmap-v3 SpecDev process (5 batch analyses)

---

## 1. Executive Summary

`/sc:spec-workshop` is a structured, multi-phase specification development and refinement command that orchestrates parallel investigation, adversarial debate, expert panel review, and optimization to produce high-quality software specifications.

### Two Modes

**Problem-driven mode**: Starts from a specific failure or bug. Investigates root causes in parallel, proposes solutions, stress-tests them through adversarial debate, and produces a sprint specification with ranked problem-solution pairs.

**Improvement-driven mode**: Starts from an existing specification (no specific failure). Identifies weaknesses in parallel, proposes improvements, debates them adversarially, and produces a refined specification with prioritized enhancements.

### Value Proposition

- Replaces ad-hoc spec review with a repeatable, auditable process
- Adversarial debate consistently deflates confidence scores by 0.04-0.12 (catches overconfidence)
- Cross-validation catches self-score inflation (observed: RC3 dropped from 0.95 to 0.70)
- Minimal fix set optimization reduces N root causes to M fixes (observed: 5 root causes covered by 3 fixes)
- Full artifact trail enables post-mortem analysis and resumability
- Parallel fan-out/fan-in architecture maximizes throughput while preserving quality gates

---

## 2. Command Interface

### Syntax

```bash
# Problem-driven mode
/sc:spec-workshop --mode problem \
  --input <problem-statement-path> \
  --spec <draft-spec-path> \
  [--sources <file1> <file2> ...] \
  [--interactive] \
  [--breadth N] \
  [--dry-run] \
  [--resume <checkpoint-id>] \
  [--output-dir <path>]

# Improvement-driven mode
/sc:spec-workshop --mode improve \
  --spec <existing-spec-path> \
  [--sources <file1> <file2> ...] \
  [--interactive] \
  [--breadth N] \
  [--dry-run] \
  [--resume <checkpoint-id>] \
  [--output-dir <path>]
```

### Flag Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | (required) | `problem` or `improve` |
| `--input` | (required for problem mode) | Path to problem statement / failure description |
| `--spec` | (required) | Path to draft specification (problem mode) or existing spec (improve mode) |
| `--sources` | `[]` | Additional source files for evidence gathering (codebase files, configs, prior diagnostics) |
| `--interactive` | `false` | When true, pause for human review at plan review, phase gates, and final output. When false, parallel verification agents handle all reviews. |
| `--breadth` | `5` | Number of parallel investigation hypotheses (range: 3-7). Controls fan-out width. |
| `--dry-run` | `false` | Generate and display the execution plan only. Do not execute. |
| `--resume` | `null` | Checkpoint ID to resume from (e.g., `CP-P2-END`). Skips completed phases. |
| `--output-dir` | `.dev/spec-workshop/{timestamp}/` | Root directory for all output artifacts |
| `--scoring-preset` | `default` | Scoring weight preset: `default`, `security-focused`, `performance-focused`, or path to custom YAML |
| `--panel-experts` | `default` | Expert persona set: `default` (Brooks/Lamport/Leveson/Weinberg), `requirements` (Wiegers/Adzic/Cockburn/...), or path to custom YAML |
| `--skip-refinement` | `false` | Skip the common refinement stage (Phases R1-R4). Produce spec from core pipeline only. |

### Usage Examples

```bash
# Investigate why sc:roadmap adversarial pipeline silently bypasses
/sc:spec-workshop --mode problem \
  --input .dev/diagnostics/failure-report.md \
  --spec .dev/sprint-spec-draft.md \
  --sources src/superclaude/skills/sc-roadmap/SKILL.md \
           src/superclaude/skills/sc-adversarial/SKILL.md \
  --breadth 5

# Improve an existing feature spec with expert review
/sc:spec-workshop --mode improve \
  --spec docs/feature-specs/auth-redesign.md \
  --interactive

# Resume from a checkpoint after context limit
/sc:spec-workshop --mode problem \
  --input .dev/diagnostics/failure-report.md \
  --spec .dev/sprint-spec-draft.md \
  --resume CP-P2-END \
  --output-dir .dev/spec-workshop/2026-02-23T1500/

# Dry run to inspect the plan before committing
/sc:spec-workshop --mode improve \
  --spec docs/specs/api-v3.md \
  --dry-run
```

---

## 3. Architecture Overview

### Skill Package Structure

```
src/superclaude/skills/sc-spec-workshop/
  SKILL.md                    # Skill definition (wave structure, allowed-tools, agent config)
  refs/
    scoring-weights.yaml      # Configurable scoring dimensions and weights
    expert-personas.yaml      # Panel expert definitions (multiple presets)
    agent-config.yaml         # Model selection per phase (opus for creation, sonnet for debate)
    pipeline-config.yaml      # Phase ordering, gate thresholds, constraint defaults
  templates/
    root-cause-report.md      # Phase 1 problem-mode template
    weakness-report.md        # Phase 1 improve-mode template
    solution-proposal.md      # Phase 2 problem-mode template
    improvement-proposal.md   # Phase 2 improve-mode template
    debate-transcript.md      # Phase 3 adversarial debate template
    debate-3col.md            # Three-column scoring variant
    optimization-proposal.md  # Phase R3 optimization template
    optimization-debate.md    # Phase R4 optimization debate template
    synthesis.md              # Fan-in synthesis template
    checkpoint.md             # Phase gate checkpoint template
    progress.md               # Progress tracking template
    plan.md                   # Execution plan template
    execution-log.md          # Agent execution log template
    reflection.md             # Self-review reflection template
    panel-review.md           # Expert panel review template
  scripts/
    verify_file_exists.sh     # Tier 1: File existence check
    verify_section_headings.py # Tier 2: Required section validation
    verify_numeric_scores.py  # Tier 2: Scoring arithmetic validation
    verify_cross_references.py # Tier 2: Cross-reference integrity
    generate_checkpoint.py    # Tier 3: Programmatic checkpoint generation
    generate_sentinel.py      # Tier 3: Immutable verification sentinel
```

### Relationship to Existing Skills

| Existing Skill | Relationship | Usage |
|---------------|-------------|-------|
| `sc:adversarial` | **Primary dependency** | Adversarial debate orchestration in Phases 3, R2, R4 |
| `sc:spec-panel` | **Primary dependency** | Expert panel evaluation in Phases R1, R3 |
| `sc:analyze` | **Secondary dependency** | Synthesis and gap analysis |
| `sc:troubleshoot` | **Secondary dependency** | Root cause investigation agents (Phase 1, problem mode) |
| `sc:reflect` | **Optional** | Self-review reflection on draft spec |
| `sc:design` | **Optional** | Solution architecture proposals |

### Agent Types

| Agent Type | Model | New/Existing | Role |
|-----------|-------|--------------|------|
| `root-cause-analyst` | opus | Existing persona | Phase 1 parallel investigators (problem mode) |
| `weakness-analyst` | opus | New (adapts root-cause-analyst) | Phase 1 parallel investigators (improve mode) |
| `solution-architect` | opus | Existing (system-architect) | Phase 2 solution/improvement proposals |
| `debate-orchestrator` | sonnet | Existing | Phase 3 adversarial debates |
| `synthesis-agent` | sonnet | Existing | Fan-in synthesis at phase boundaries |
| `panel-reviewer` | opus | Existing (spec-panel) | Expert persona reviews in refinement |
| `verification-agent` | sonnet | New | Parallel verification (non-interactive mode) |
| `plan-reviewer` | sonnet | New | Plan review before execution |

---

## 4. Pipeline Stages (Both Modes)

### 4.1 Stage 0: Plan Generation

**Purpose**: Generate a complete, inspectable execution plan before any work begins.

**Process**:

1. **Input analysis**: Read all provided artifacts (problem statement, spec, source files)
2. **Mode detection**: Determine problem-driven or improvement-driven
3. **Hypothesis generation**: Generate N hypotheses based on mode:
   - Problem mode: Failure-layer hypotheses (infrastructure, specification, binding, data flow, behavioral)
   - Improve mode: Quality-dimension hypotheses (clarity, completeness, consistency, testability, maintainability, performance, security)
4. **Plan assembly**: Generate the full tasklist with dependency graph, file registry, checkpoint schedule, and acceptance criteria for every task
5. **Plan review**:
   - If `--interactive`: Present plan to human for review, collect feedback, revise
   - If not `--interactive`: Dispatch 2 parallel plan-reviewer agents (completeness verifier + consistency verifier), collect findings, auto-revise
6. **Plan approval**: Write `plan/tasklist-approved.md`

**Plan document contains**:
- Task registry (all tasks with IDs, dependencies, agent types, skills, outputs)
- Dependency graph (ASCII art)
- File registry (all expected output files with producing tasks)
- Checkpoint registry (phase boundaries with verification criteria)
- Scoring configuration (dimensions, weights, thresholds for this run)
- Estimated resource usage (agent count, parallel width, token budget)

### 4.2 Problem-Driven Mode Pipeline

#### Phase 1: Root Cause Investigation (parallel fan-out)

**Input**: Problem statement + source files + codebase access
**Parallelism**: N agents (one per hypothesis), completely independent
**Agent**: `root-cause-analyst` (opus)

Each agent receives:
- The problem statement (failure description, expected vs. actual behavior)
- One specific hypothesis to investigate
- Access to codebase via Read, Grep, Glob tools
- The root cause report template

Each agent does NOT receive other agents' findings (prevents anchoring bias).

**Output**: N root cause report files + 1 ranked synthesis

**Synthesis task** (sequential, after all N complete):
- Cross-validate self-reported scores (recalibrate inflation)
- Build dependency chain (which causes are primary vs. downstream)
- Assess overlap (which root causes could be merged)
- Compute combined scores using `problem_score = (likelihood * 0.6) + (impact * 0.4)`
- Produce minimal fix set (N fixes covering M root causes)
- Assign solution tasks

**Gate**: CP-P1-END -- All N report files exist with non-zero size, ranked synthesis file exists, all scores in [0.0, 1.0], dependency chain present.

#### Phase 2: Solution Proposals (parallel fan-out)

**Input**: Ranked root causes + source files
**Parallelism**: N agents (one per root cause)
**Agent**: `solution-architect` (opus, with domain-specific persona)

Each agent receives:
- The ranked root causes document (full context)
- Their assigned root cause
- The solution proposal template

**Output**: N solution proposal files

**Gate**: CP-P2-END -- All N solution files exist, each references its assigned root cause, each has >= 3 options analyzed, confidence scores present.

#### Phase 3: Solution Debates (parallel adversarial)

**Input**: Solution proposals + ranked root causes
**Parallelism**: N debates (one per solution)
**Agent**: `debate-orchestrator` (sonnet)

Each debate is a single agent simulating FOR and AGAINST positions with cross-examination and dimensional scoring.

**Output**: N debate transcript files

**Gate**: CP-P3-END -- All N debate files exist, each has 5-dimension scoring matrix, fix likelihood computed, unresolved concerns listed.

#### Phase 4: Ranking and Sprint Spec Design

**Input**: All debate results + ranked root causes + solution proposals
**Parallelism**: Sequential (single synthesis agent)
**Agent**: `solution-architect` (opus, system-architect persona)

**Processing**:
1. Compute combined ranking: `combined = (problem_score * 0.5) + (solution_score * 0.5)`
2. Select top-N problem-solution pairs for sprint scope
3. Design sprint structure (epics, tasks, dependency order)
4. Build risk register from unresolved concerns
5. Create Definition of Done checklist
6. Create verification plan

**Output**: `sprint-spec.md` (draft specification)

**Gate**: CP-P4-END -- sprint-spec.md exists with ranked lists, top-N pairs, epics with tasks, risk register, DoD, verification plan.

### 4.3 Improvement-Driven Mode Pipeline

#### Phase 1: Weakness Analysis (parallel fan-out)

**Input**: Existing specification + source files + codebase access
**Parallelism**: N agents (one per quality dimension)
**Agent**: `weakness-analyst` (opus)

Each agent investigates one quality dimension:
1. Clarity: Are specifications clear and unambiguous?
2. Completeness: Are there gaps or missing specifications?
3. Consistency: Do different parts agree with each other?
4. Testability: Can specified behavior be verified?
5. Maintainability: Is the system easy to evolve?
6. Performance: Are there efficiency concerns?
7. Security/Safety: Are there unmitigated risks?

Uses the weakness report template (adapted from root cause template).

**Synthesis task**: Cross-validate scores, assess compounding weaknesses, compute `weakness_score = (severity * 0.5) + (improvement_potential * 0.3) + (feasibility * 0.2)`, produce improvement roadmap.

**Gate**: CP-P1-END -- All N weakness files exist, ranked synthesis present.

#### Phase 2: Improvement Proposals (parallel fan-out)

**Input**: Ranked weaknesses + existing spec
**Parallelism**: N agents
**Agent**: `solution-architect` (opus)

Same structure as problem-mode Phase 2 but targeting weaknesses instead of root causes.

**Gate**: CP-P2-END -- All N improvement proposal files exist.

#### Phase 3: Improvement Debates (parallel adversarial)

Identical structure to problem-mode Phase 3.

**Gate**: CP-P3-END -- All N debate files exist with scoring.

#### Phase 4: Optimization and Revised Spec

Identical to problem-mode Phase 4, producing a revised specification.

**Gate**: CP-P4-END -- revised-spec.md exists with all required sections.

### 4.4 Common Refinement Stage (both modes)

Applied to the draft/revised spec produced by Phase 4. This stage is optional (`--skip-refinement` bypasses it).

#### Phase R1: Expert Panel Evaluation

**Input**: Draft spec from Phase 4 + all prior artifacts
**Agent**: Panel of 4 expert personas (configurable via `--panel-experts`)

**Default panel** (software specification):
- Fred Brooks: Scope discipline, conceptual integrity, second-system effect
- Leslie Lamport: Specification precision, state machines, temporal properties
- Nancy Leveson: System safety, STAMP, hazard analysis
- Gerald Weinberg: Psychology of programming, cognitive load

Each expert independently reviews using this structure:
1. Top Concern (single most important issue)
2. Specific Improvements (numbered, with exact location and replacement text)
3. What I Would Cut (scope reduction recommendations)

Panel synthesis produces:
- Consensus improvements (all experts agree)
- Contested points (with resolution)
- Ranked recommendations by `(impact * success_likelihood) / effort`
- Confidence votes (per expert + panel average)

**Gate**: CP-R1-END -- Panel review file exists, >= 1 consensus improvement, confidence votes present.

#### Phase R2: Spec-vs-Findings Adversarial Validation (parallel)

**Input**: Draft spec + all root causes/weaknesses from Phase 1
**Parallelism**: N debates (one per root cause or weakness)
**Agent**: `debate-orchestrator` (sonnet)

Each debate asks: "Does the spec effectively mitigate {subject}?"

**Debate structure**:
- FOR Position (Advocate): 4-5 arguments defending the spec's treatment
- AGAINST Position (Challenger): 4-5 arguments attacking the spec's treatment
- Cross-Examination: Each side challenges the other's strongest argument
- Scoring: 5 dimensions (subject coverage, completeness, feasibility, blast radius, confidence)
- Verdict: SUFFICIENT (>= 0.85) / NEEDS AMENDMENTS (0.60-0.84) / INSUFFICIENT (< 0.60)
- Required Amendments with effort estimates

**Synthesis**: Aggregate coverage matrix, overall effectiveness score, gap list (G1-GN) classified as Critical/Important/Deferred, urgency-ranked recommendations.

**Gate**: CP-R2-END -- All N debate files exist, synthesis file exists with overall effectiveness score.

#### Phase R3: Optimization Proposals (expert panel)

**Input**: Draft spec + R2 synthesis (gap analysis)
**Agent**: Panel of 4 specialists (Efficiency Expert, Quality Advocate, Implementation Specialist, Risk Analyst)

**Constraints**:
- Produce exactly 5 optimizations
- Total time savings > 20% of estimated sprint
- Each effectiveness_impact < 0.3
- At least 2 with zero effectiveness impact
- All optimizations independently adoptable

Each optimization uses the 7-field template:
1. Current State
2. Proposed Change
3. Time Savings (hours + %)
4. Effectiveness Impact (0.0-1.0)
5. Risk Assessment (severity + mitigation)
6. Net Benefit Formula: `time_saved * (1 - effectiveness_impact)`
7. Panel Notes (per-panelist quotes + consensus vote)

**Gate**: CP-R3-END -- Optimization file exists, all constraints verified.

#### Phase R4: Optimization Debates (parallel adversarial)

**Input**: Optimization proposals + draft spec + root causes/weaknesses
**Parallelism**: 5 debates (one per optimization)
**Agent**: `debate-orchestrator` (sonnet)

**Scoring dimensions**: time_savings, effectiveness_preservation, feasibility, risk, net_benefit

**Verdict options**: ADOPT / ADOPT-WITH-MODIFICATIONS / REJECT

**Synthesis**: Verdict table, adopted optimizations with modifications, revised savings, confidence-ordered adoption list.

**Gate**: CP-R4-END -- All debate files exist, synthesis file with final adoption list.

#### Final Integration

Apply panel recommendations and adopted optimizations to produce the final specification. Write final-spec.md.

---

## 5. Templates

### 5.1 Root Cause Report Template (Phase 1, Problem Mode)

```markdown
# Root Cause #N: [Title]

## Summary
[1-2 paragraph high-level description of the root cause]

## Evidence

### Evidence 1: [Specific evidence title]
[Detailed evidence with file paths, line numbers, verbatim code/config quotes]

### Evidence 2: [Specific evidence title]
[...]

### Evidence N: [Specific evidence title]
[...]

## Analysis
[Multi-paragraph synthesis connecting all evidence into a causal explanation.
 Includes comparison tables, reasoning chains, and "reasonable
 misinterpretation" analysis showing how the system could rationally arrive
 at the wrong behavior.]

## Likelihood Score: X.XX/1.0
[Justification paragraph explaining the score and the residual uncertainty]

## Impact Score: X.XX/1.0
[Justification paragraph explaining the score and its bounds]

## Recommendation
### Option A: [Immediate Fix]
[Description with code examples]

### Option B: [Structural Fix]
[Description with code examples]

### Option C: [Long-term Fix]
[Description]

### Additional Required Fix (if applicable)
[Cross-cutting fix needed regardless of which option is chosen]
```

### 5.2 Weakness Report Template (Phase 1, Improve Mode)

```markdown
# Weakness #N: [Title]

## Summary
[1-2 paragraph description of the weakness and why it matters]

## Evidence

### Evidence 1: [Specific evidence title]
[File paths, line numbers, verbatim quotes showing the weakness]

### Evidence N: [...]

## Analysis

### Severity Assessment
[How bad is this weakness? What could go wrong if left unaddressed?]

### Exploitation/Failure Scenarios
[Concrete scenarios where this weakness causes problems]

### Comparison to Best Practices
[How does this compare to known good patterns? What would "good" look like?]

## Severity Score: X.XX/1.0
[Justification -- replaces "Likelihood" since there is no specific failure to explain]

## Improvement Potential: X.XX/1.0
[How much better could things get if this weakness were addressed?
 Replaces "Impact" since the question is about potential gain, not failure explanation]

## Recommendation
### Option A: [Minimal improvement]
### Option B: [Recommended improvement]
### Option C: [Aspirational improvement]
```

### 5.3 Solution / Improvement Proposal Template (Phase 2)

```markdown
# Solution #N: [Title]

## Problem Summary
[Concise restatement of the root cause / weakness with evidence from codebase.
 Includes specific file paths, line numbers, and the exact gap identified.]

**Root cause rank**: N of M, combined score X.XX.

---

## Options Analysis

### Option A: [Name]

**Description**: [What the option does]

**Pros**:
- [Pro 1]
- [Pro 2]

**Cons**:
- [Con 1 -- with specific technical detail]
- **Critical question**: [Specific uncertainty that needs resolution]

**Feasibility**: LOW | MEDIUM | HIGH
**Blast radius**: [Assessment]

### Option B: [Name]
[Same structure]

### Option C: [Name]
[Same structure]

### Comparative Matrix (optional, for complex solutions)

| Criterion | Weight | A: [Name] | B: [Name] | C: [Name] |
|-----------|--------|-----------|-----------|-----------|
| [criterion] | 0.XX | N | N | N |
| **Weighted Score** | | **X.XX** | **X.XX** | **X.XX** |

---

## Recommended Solution: Option X with [Option Y fallback]

### Rationale
[Numbered reasons referencing architectural principles and codebase patterns]

**Why not Option A**: [One-sentence rejection with reason]
**Why not Option C**: [One-sentence rejection with reason]

### Fallback Protocol
[What happens if the recommended option proves unworkable]

---

## Implementation Details

### Files to Modify

| File | Change | Lines |
|------|--------|-------|
| [path] | [description] | [line reference] |

### Code Changes

#### Change 1: [Description]

**File**: [path], line N

```yaml
# BEFORE:
[exact current content]

# AFTER:
[exact proposed content]
```

### Blast Radius Assessment

**Directly affected files** (N files):
1. [file] -- [change type] ([scope])

**Not affected**:
- [explicit exclusions with reasons]

**Risk assessment**:
- [risk level] risk for [change description]

---

## Confidence Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Problem diagnosis accuracy | X.XX | [rationale] |
| Solution correctness | X.XX | [rationale] |
| Implementation completeness | X.XX | [rationale] |
| Blast radius containment | X.XX | [rationale] |
| Forward compatibility | X.XX | [rationale] |
| **Overall confidence** | **X.XX** | [summary] |

**What would raise confidence to 0.90+**: [Specific verifiable condition]

---

*Solution designed [date]. Analyst: [model-id] ([persona]).*
*Addresses: [subject reference]. Partially addresses: [other references].*
```

### 5.4 Debate Template (Phase 3 -- FOR/AGAINST/CROSS-EXAMINATION/VERDICT)

```markdown
# Debate: Solution #N -- [Title]

*Conducted [date]. Debate orchestrator: [model-id].*
*Solution under review: [option selected] with [fallback].*
*Subject addressed: [reference with rank and score].*

---

## Advocate FOR

### Argument 1: [Thesis statement]
[Supporting evidence with specific file paths, line numbers, and codebase references.
Each argument is self-contained with enough evidence to stand alone.]

### Argument 2: [Thesis statement]
[Same structure]

### Argument 3: [Thesis statement]
[Same structure]

### Argument 4: [Thesis statement]
[Same structure]

---

## Advocate AGAINST

### Argument 1: [Thesis statement targeting a specific weakness]
[Evidence-based challenge. Must reference specific claims from the solution document
and present concrete counter-evidence or identify specific gaps.]

### Argument 2: [Thesis statement]
[Same structure]

### Argument 3: [Thesis statement]
[Same structure]

### Argument 4: [Thesis statement]
[Same structure]

---

## Cross-Examination

### Challenger to Advocate
**Question**: [Specific question targeting the Advocate's weakest point]
**Advocate's response**: [Direct response with concessions or rebuttals]

### Advocate to Challenger
**Question**: [Specific question targeting the Challenger's weakest point]
**Challenger's response**: [Direct response with concessions or rebuttals]

---

## Scoring Matrix

| Dimension | Weight | FOR Score | AGAINST Score | Adjudicated Score | Weighted |
|-----------|--------|-----------|---------------|-------------------|---------|
| Root cause coverage | 0.25 | X.XX | X.XX | X.XX | X.XXX |
| Completeness | 0.20 | X.XX | X.XX | X.XX | X.XXX |
| Feasibility | 0.25 | X.XX | X.XX | X.XX | X.XXX |
| Blast radius | 0.15 | X.XX | X.XX | X.XX | X.XXX |
| Confidence | 0.15 | X.XX | X.XX | X.XX | X.XXX |
| **TOTAL** | **1.00** | | | | **X.XXX** |

### Scoring Rationale
**[Dimension] (adjudicated: X.XX)**: [Multi-sentence rationale explaining how FOR
and AGAINST scores were weighted to produce the adjudicated score]
[Repeat for each dimension]

---

## Fix Likelihood: X.XX

**Interpretation**: [2-3 sentences explaining what the score means]

---

## Verdict: [SUFFICIENT / NEEDS AMENDMENTS / INSUFFICIENT]

### Recommended Amendments (if NEEDS AMENDMENTS)

| # | Amendment | Effort | Impact |
|---|-----------|--------|--------|
| A1 | [Description] | [time] | [High/Medium/Low] |

---

## Unresolved Concerns

### 1. [Concern title] (Critical|Medium|Low)
[Description with resolution path]

---

*Debate conducted [date]. Orchestrator: [model-id].*
*Input: [solution file] + [root causes file].*
*Fix likelihood: X.XX (weighted).*
```

### 5.5 Synthesis Template (Phase boundaries)

```markdown
# Synthesis: [Phase Name] Results

> **Task**: [Task ID] -- [Description]
> **Generated**: [date]
> **Inputs**: [list of input files]

## 1. Aggregate Coverage Matrix

| Dimension | Subject 1 (score) | Subject 2 (score) | ... | Avg |
|-----------|-------------------|-------------------|-----|-----|
| [dim 1] | X.XX | X.XX | | X.XX |
| **Composite** | **X.XX** | **X.XX** | | **X.XX** |

**Overall Effectiveness Score**: [formula shown] = **X.XX**

## 2. Weakest Coverage Areas (ranked)

| Rank | Weakness | Score | Subject | Issue |
|------|----------|-------|---------|-------|
| 1 | [description] | X.XX | [ref] | [detail] |

## 3. Strongest Coverage Areas (ranked)

| Rank | Strength | Score | Subject | Why |
|------|----------|-------|---------|-----|
| 1 | [description] | X.XX | [ref] | [detail] |

## 4. Specific Gaps Requiring Amendments

### Critical (must fix)

| # | Gap | Source | Effort | Fix |
|---|-----|--------|--------|-----|
| G1 | [description] | [debate ref] | [time] | [concrete fix] |

### Important (should fix)
[Same table format]

### Deferred (follow-up)
[Same table format with deferral rationale]

## 5. Recommendations Ranked by Urgency

| Priority | Action | Effort | Impact on Score |
|----------|--------|--------|----------------|
| 1 | [action] | [time] | [+X.XX on subject] |

**Total amendment effort**: ~X hours
**Estimated post-amendment score**: ~X.XX (from X.XX)
```

### 5.6 Optimization Proposal Template (Phase R3)

Each optimization MUST contain all 7 fields:

```markdown
## Optimization N: [Title]

### Current State
[Description of the suboptimal status quo]

### Proposed Change
[Specific proposed modification]

### Time Savings
**X.XX hours** (~Y% of sprint)
Breakdown:
- [Item 1]: X.XX hours (rationale)
- [Item 2]: X.XX hours (rationale)

### Effectiveness Impact
**0.XX** -- [Impact level].
[Justification for why effectiveness is/isn't affected]

### Risk Assessment
**[Severity]**. [Description of primary risk]. Mitigation: [How risk is addressed].

### Net Benefit Formula
`X.XX hrs * (1 - 0.XX) = Y.YY net benefit hours`

### Panel Notes
- **Efficiency Expert**: "[Quote]"
- **Quality Advocate**: "[Quote]"
- **Implementation Specialist**: "[Quote]"
- **Risk Analyst**: "[Quote]"

**Consensus**: [Unanimous/Majority] APPROVE [with caveats].
```

**Constraint verification table** (must accompany all 5 optimizations):

```markdown
| Constraint | Requirement | Actual | Status |
|-----------|------------|--------|--------|
| Max effectiveness impact per opt | < 0.3 | [max] | PASS/FAIL |
| Total time savings > 20% | > X.X hrs | [actual] | PASS/FAIL |
| At least 2 zero-impact optimizations | >= 2 | [count] | PASS/FAIL |
| All independently adoptable | Yes | [status] | PASS/FAIL |
```

### 5.7 Checkpoint Template

```markdown
# Checkpoint: CP-P{N}-END -- Phase {N} Complete

**Timestamp**: [datetime]
**Phase**: [Phase name] ([Task range])

## Verification

- [x] `[filepath]` ([size] bytes)
- [x] `[filepath]` ([size] bytes)
...

## Key Metrics

| Metric | Value | Context |
|--------|-------|---------|
| [metric name] | [value] | [interpretation] |

## Key Finding
[1-3 sentences of narrative summary]

## Unresolved Concerns (carrying forward)
1. [Concern description]
```

### 5.8 Progress Tracking Template

```markdown
# Spec Workshop Progress

**Run ID**: [timestamp]
**Mode**: [problem / improve]
**Started**: [datetime]

## Phase Status

| Phase | Status | Started | Completed | Key Findings |
|-------|--------|---------|-----------|--------------|
| P1: [Name] | [status] | [time] | [time] | [summary] |

## Task Status

| Task | Status | Output File | Notes |
|------|--------|-------------|-------|
| T01.01 | [status] | [filepath] | [notes] |

## Save Points

| Checkpoint | Timestamp | Notes |
|------------|-----------|-------|
| CP-P1-END | [time] | [summary] |
```

### 5.9 Execution Log Template

```markdown
# Execution Log: [Agent Name]

**Tasklist**: [path to tasklist]
**Target**: [path to target file]
**Date**: [date]
**Agent**: [model-id]

---

## Pre-Execution State Assessment
[What other agents had already modified before this agent started]

## Task-by-Task Log

### Task N: [Title]
**Status**: APPLIED | PRE-APPLIED | NO-CHANGE-NEEDED | ADAPTED
**Change**: [What was changed]
**Method**: [Edit method used]
**Adaptation note** (if any): [Why the agent deviated from tasklist]

---

## Adaptation Notes
[Summary of all deviations from the planned tasklist]

## Final State

- **Tasks applied**: N
- **Tasks pre-applied**: N
- **Tasks no-change-needed**: N
- **Errors or failures**: [description or None]
- **Adaptations**: [summary]
```

### 5.10 Reflection Template (Self-Review)

```markdown
# Reflection: [Spec Title]

**Date**: [date]
**Reviewer**: [model-id] ([persona])
**Input**: [spec file], [N] diagnostic artifacts, [N] source files

---

## 1. Prioritized Improvements

### HIGH Impact x LOW Effort
**IMP-01**: [Title]
[Analysis, rationale, specific change to spec with code block]

### HIGH Impact x MEDIUM Effort
[...]

### MEDIUM Impact x LOW Effort
[...]

## 2. Kill List -- Simplify or Remove
[Table: item, verdict (KEEP/DEFER/CUT), rationale]

## 3. Integration Blind Spots
[Cross-component boundary risks]

## 4. Failure Modes NOT Covered
[Numbered list of uncovered scenarios]

## 5. Confidence Assessment
**Probability of success on first attempt: XX%**

| Factor | Probability | Rationale |
|--------|------------|-----------|
| [factor] | X.XX | [reasoning] |

**Composite**: XX% as specified, YY% with mitigations.
```

---

## 6. Scoring System

### 6.1 Root Cause / Weakness Scoring

**Problem-driven (root cause ranking)**:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Likelihood | 0.6 | Probability this is an active cause of the failure |
| Impact | 0.4 | Degree to which this explains the observed symptoms |

```
problem_score = (likelihood * 0.6) + (impact * 0.4)
```

**Improvement-driven (weakness ranking)**:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Severity | 0.5 | How bad is the weakness? |
| Improvement Potential | 0.3 | How much better could things get? |
| Feasibility | 0.2 | How easy is the improvement? |

```
weakness_score = (severity * 0.5) + (improvement_potential * 0.3) + (feasibility * 0.2)
```

### 6.2 Solution Debate Scoring (Phase 3)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Root cause coverage | 0.25 | Does the solution address the identified root cause completely? |
| Completeness | 0.20 | Are all paths handled (happy, degraded, failure)? Edge cases? |
| Feasibility | 0.25 | Can the solution be implemented with existing tools and patterns? |
| Blast radius | 0.15 | How many files affected? Additive or structural changes? |
| Confidence | 0.15 | How certain are we the solution works? Untested assumptions? |

```
fix_likelihood = SUM(dimension_weight * dimension_score) for all 5 dimensions
```

**Verdict thresholds**:

| Score Range | Verdict | Action |
|-------------|---------|--------|
| >= 0.85 | SUFFICIENT / Implement as specified | Proceed |
| 0.70-0.84 | NEEDS AMENDMENTS / Implement with conditions | List amendments |
| 0.60-0.69 | NEEDS AMENDMENTS / Implement with rework | List significant rework |
| < 0.60 | INSUFFICIENT / Reconsider or defer | Block |

### 6.3 Solution Ranking Formula (Phase 4)

```
solution_score = (fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)
```

### 6.4 Combined Ranking Formula (Phase 4)

```
combined = (problem_score * 0.5) + (solution_score * 0.5)
```

### 6.5 Optimization Debate Scoring (Phase R4)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| time_savings | 0.20 | Does this actually save the claimed time? |
| effectiveness_preservation | 0.20 | Does this preserve spec effectiveness? |
| feasibility | 0.20 | Can this optimization be cleanly applied? |
| risk | 0.20 | What is the downside risk? (higher = lower risk) |
| net_benefit | 0.20 | Overall benefit accounting for all dimensions |

```
optimization_score = simple_average(all 5 dimensions)
```

**Verdict thresholds**:

| Score Range | Verdict |
|-------------|---------|
| >= 0.85 | ADOPT |
| 0.60-0.84 | ADOPT-WITH-MODIFICATIONS |
| < 0.60 | REJECT |

### 6.6 Overall Spec Effectiveness (Phase R2 Synthesis)

```
overall_effectiveness = sum(subject_score_i * debate_score_i) / sum(subject_score_i)
```

Weights debate scores by the severity of their subject, so high-severity subjects with low debate scores pull the overall score down disproportionately.

### 6.7 Optimization Net Benefit

```
net_benefit = time_saved * (1 - effectiveness_impact)
```

### 6.8 Deferral Confidence Scoring (used in gap analysis)

| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| 0.00-0.25 | Deferral strongly unjustified | Escalate to sprint amendment |
| 0.26-0.50 | Deferral questionable | Add to priority backlog with urgency flag |
| 0.51-0.75 | Deferral justified with minor concerns | Defer but schedule for next sprint |
| 0.76-1.00 | Deferral clearly correct | Maintain deferral |

### 6.9 Score Recalibration (Cross-Validation)

Applied by the synthesis agent to all self-reported scores. Recalibration criteria:

1. **Evidence quality**: Is the evidence concrete/verifiable or inferential?
2. **Inflation detection**: Does the score overstate independent contribution?
3. **Dependency chain membership**: Active cause or downstream consequence?
4. **Overlap assessment**: Does this substantially overlap with another subject?

Recalibration can adjust scores up or down. Adjustments must include rationale.

---

## 7. Verification Architecture

### 7.1 Design Principles

1. **Never trust agent self-reports for verifiable facts**: File existence, content matching, schema validation, numeric consistency -- all checked programmatically.
2. **Separate creative work from verification work**: The executing agent does creative work; a separate mechanism checks results.
3. **Immutable evidence trail**: Sentinel files with timestamps and hashes that no agent can fabricate.
4. **Hard stops, not soft warnings**: Verification failure = phase failure. No "warn and proceed."

### 7.2 Three-Tier Verification

```
Tier 1: PRE-GATES       (before agent starts a phase)
Tier 2: POST-GATES      (after agent claims phase complete)
Tier 3: CROSS-PHASE     (at checkpoint boundaries)
```

### 7.3 Pre-Gate Verification (before each phase)

| Check | Script | Input | Pass Condition |
|-------|--------|-------|---------------|
| Input files exist | `verify_file_exists.sh` | List of required source files | All exist and are non-empty |
| Prerequisites met | `verify_file_exists.sh` | List of prerequisite sentinel files | All `.verified-<phase>` sentinels exist |
| Target snapshot | `snapshot_target.sh` | Target file path | SHA-256 hash written to `.pre-<phase>.sha256` |

### 7.4 Post-Gate Verification (after each phase)

| Check | Script | Pass Condition |
|-------|--------|---------------|
| File modified | Compare pre-hash to current hash | If identical, agent claimed edit but didn't |
| Required sections | `verify_section_headings.py` | All expected headings present in output |
| Scoring arithmetic | `verify_numeric_scores.py` | Weights sum to 1.0, weighted = weight * score, composite = sum |
| Cross-references | `verify_cross_references.py` | All referenced files/sections exist |
| Tasklist coverage | `verify_tasklist_log_coverage.py` | Every task in tasklist has corresponding log entry |
| Score ranges | Parse scoring tables | All scores in [0.0, 1.0] |

### 7.5 Phase-Specific Verification Checks

**Phase 1 (Root Cause / Weakness Investigation)**:
- All N report files exist with non-zero byte size
- Each report has Summary, Evidence, Analysis, Score 1, Score 2, Recommendation sections
- All scores in [0.0, 1.0]
- Ranked synthesis file has dependency chain and overlap assessment

**Phase 2 (Solution / Improvement Proposals)**:
- All N proposal files exist
- Each proposal references its assigned subject (cross-reference to Phase 1)
- Each proposal has >= 3 options analyzed
- Each has confidence score with dimension breakdown
- File paths in Implementation Details exist in codebase
- Overlap references to other solutions name existing files

**Phase 3 (Adversarial Debates)**:
- All N debate files exist
- Each has FOR section with >= 3 arguments
- Each has AGAINST section with >= 3 arguments
- Each has cross-examination section
- Scoring matrix has all required dimensions with weights summing to 1.00
- Fix likelihood matches weighted sum computation (arithmetic check within 0.02)
- Fix likelihood is lower than solution's self-reported confidence
- Unresolved concerns section exists
- At least 1 AGAINST argument is partially conceded in rebuttal

**Phase R2 (Spec-vs-Findings Debates)**:
- All dimension scores in [0.0, 1.0]
- Verdict consistent with score thresholds
- If NEEDS AMENDMENTS, at least 1 amendment with effort estimate

**Phase R3 (Optimization Proposals)**:
- All 7 required fields present per optimization
- Net benefit formula arithmetic correct within 0.01
- All constraints met (max impact < 0.3, total savings > 20%, >= 2 zero-impact)
- Panel consensus recorded per optimization

**Phase R4 (Optimization Debates)**:
- All 5 dimensions scored per debate
- Composite is simple average (arithmetic check within 0.02)
- Modifications listed if ADOPT-WITH-MODIFICATIONS

### 7.6 Parallel Verification Agents (Non-Interactive Mode)

When `--interactive` is false, every review point dispatches parallel verification agents instead of pausing for human review.

**Plan Review** (Stage 0):
- Agent A (Completeness Verifier): Are all tasks defined? All dependencies resolved? All acceptance criteria present?
- Agent B (Consistency Verifier): Do cross-references resolve? Are task IDs unique? Are file paths valid?

**Phase Gate Reviews**:
- Agent A (Completeness Verifier): Does the artifact contain all required sections? Are acceptance criteria met?
- Agent B (Consistency Verifier): Do cross-references resolve? Are scores mathematically consistent?
- Agent C (Adversarial Verifier -- critical gates only): What is the weakest part? What claim is least supported?

**Synthesis Reviews**:
- Verify all source debates are represented in the matrix
- Verify all amendments extracted from debates appear as gaps
- Verify gap severity classification is consistent with scores

### 7.7 Sentinel File Convention

On successful verification, the verification system writes:

```
{output-dir}/verification/.verified-{phase-id}
```

Sentinel contains: timestamp, all check results (pass/fail), input file hashes, verification script versions. Creates an immutable audit trail.

**Key constraint**: Post-gate verification for Phase N must complete and produce a sentinel before Phase N+1's executing agent starts.

---

## 8. Checkpoint and Resumption System

### 8.1 Checkpoint Format

```yaml
checkpoint:
  id: "CP-P{n}-END"
  timestamp: "YYYY-MM-DDTHH:MM:SS"
  phase: "Phase name"
  mode: "problem | improve"
  run_id: "timestamp identifier"

  verification:
    - file: "relative/path/to/artifact.md"
      exists: true
      size_bytes: 12345
      sha256: "abc123..."
    - file: "relative/path/to/another.md"
      exists: true
      size_bytes: 6789

  metrics:
    - name: "overall_effectiveness"
      value: 0.737
      context: "Weighted by problem scores"

  key_findings: "1-3 sentence narrative summary"

  unresolved:
    - "Concern carrying forward to next phase"

  next_phase: "Phase N+1 name"

  resumption_data:
    completed_tasks: ["T01.01", "T01.02", ...]
    pending_tasks: ["T02.01", "T02.02", ...]
    scoring_state:
      problem_scores: {"RC1": 0.90, "RC2": 0.77, ...}
```

### 8.2 Checkpoint Schedule

| Checkpoint | After | Required Before |
|------------|-------|-----------------|
| CP-PLAN | Stage 0 (plan approved) | Phase 1 |
| CP-P1-END | Phase 1 synthesis | Phase 2 |
| CP-P2-END | Phase 2 (all proposals) | Phase 3 |
| CP-P3-END | Phase 3 (all debates) | Phase 4 |
| CP-P4-END | Phase 4 (draft spec) | Phase R1 |
| CP-R1-END | Phase R1 (panel review) | Phase R2 |
| CP-R2-END | Phase R2 (synthesis) | Phase R3 |
| CP-R3-END | Phase R3 (optimizations) | Phase R4 |
| CP-R4-END | Phase R4 (final synthesis) | Final integration |
| CP-FINAL | Final integration | Done |

### 8.3 Resumption

When `--resume CP-P2-END` is specified:

1. Read the checkpoint file at `{output-dir}/checkpoints/CP-P2-END.md`
2. Verify all artifacts listed in the checkpoint still exist with matching hashes
3. Load `resumption_data.scoring_state` to restore scores from previous phases
4. Skip Phases 1 and 2 synthesis
5. Begin Phase 3 using the outputs listed in the checkpoint

If artifact verification fails (files missing or modified since checkpoint), emit an error and refuse to resume.

---

## 9. Output Directory Structure

```
{output-dir}/
  plan/
    tasklist-draft.md           # Generated plan (before review)
    plan-review-A.md            # Completeness verifier review
    plan-review-B.md            # Consistency verifier review
    tasklist-approved.md        # Final approved plan

  phases/
    P1-investigation/
      root-cause-01-{slug}.md   # (problem mode) or weakness-01-{slug}.md (improve mode)
      root-cause-02-{slug}.md
      ...
      ranked-synthesis.md       # Ranked root causes / weaknesses

    P2-proposals/
      solution-01-{slug}.md     # (problem mode) or improvement-01-{slug}.md (improve mode)
      solution-02-{slug}.md
      ...

    P3-debates/
      debate-01-{slug}.md
      debate-02-{slug}.md
      ...

    P4-sprint-design/
      sprint-spec.md            # (problem mode) or revised-spec.md (improve mode)

    R1-panel-review/
      panel-review.md

    R2-validation/
      debate-RC1.md
      debate-RC2.md
      ...
      synthesis.md

    R3-optimizations/
      optimizations.md

    R4-optimization-debates/
      debate-opt1.md
      debate-opt2.md
      ...
      synthesis.md

  checkpoints/
    CP-PLAN.md
    CP-P1-END.md
    CP-P2-END.md
    CP-P3-END.md
    CP-P4-END.md
    CP-R1-END.md
    CP-R2-END.md
    CP-R3-END.md
    CP-R4-END.md
    CP-FINAL.md

  verification/
    .verified-P1
    .verified-P2
    .verified-P3
    .verified-P4
    .verified-R1
    .verified-R2
    .verified-R3
    .verified-R4
    V-P1-END.md               # Verification agent results
    V-P2-END.md
    ...

  logs/
    log-P1.md                  # Execution logs per phase
    log-P2.md
    ...

  progress.md                  # Running progress tracker
  final-spec.md                # The completed specification
```

---

## 10. Configuration and Extensibility

### 10.1 Configurable Parameters

| Parameter | File | Default | Description |
|-----------|------|---------|-------------|
| `breadth` | CLI flag | 5 | Number of parallel hypotheses (3-7) |
| `scoring_weights.problem` | `scoring-weights.yaml` | `{likelihood: 0.6, impact: 0.4}` | Weights for problem-mode Phase 1 |
| `scoring_weights.weakness` | `scoring-weights.yaml` | `{severity: 0.5, potential: 0.3, feasibility: 0.2}` | Weights for improve-mode Phase 1 |
| `scoring_weights.debate` | `scoring-weights.yaml` | `{coverage: 0.25, completeness: 0.20, feasibility: 0.25, blast_radius: 0.15, confidence: 0.15}` | Debate scoring dimension weights |
| `scoring_weights.optimization` | `scoring-weights.yaml` | Equal weights (0.20 each) | Optimization debate weights |
| `verdict_thresholds` | `pipeline-config.yaml` | `{sufficient: 0.85, needs_amendments: 0.60}` | Score thresholds for debate verdicts |
| `optimization_constraints` | `pipeline-config.yaml` | `{max_impact: 0.3, min_total_savings: 0.20, min_zero_impact: 2}` | Optimization proposal constraints |
| `expert_personas` | `expert-personas.yaml` | Brooks/Lamport/Leveson/Weinberg | Panel expert definitions |
| `agent_config.investigation` | `agent-config.yaml` | opus | Model for Phase 1 investigators |
| `agent_config.proposals` | `agent-config.yaml` | opus | Model for Phase 2 proposal authors |
| `agent_config.debates` | `agent-config.yaml` | sonnet | Model for debate orchestration |
| `agent_config.synthesis` | `agent-config.yaml` | sonnet | Model for fan-in synthesis |
| `agent_config.verification` | `agent-config.yaml` | sonnet | Model for verification agents |
| `top_n_cutoff` | `pipeline-config.yaml` | 3 | How many subjects make it into the sprint spec |

### 10.2 Hardcoded (Not Configurable)

| Element | Rationale |
|---------|-----------|
| Pipeline structure (fan-out/fan-in phases) | Core architectural pattern; changing it would require redesign |
| Template format (required sections per report) | Enables cross-report comparison and automated verification |
| Evidence requirements (file paths, line numbers, verbatim quotes) | Prevents hallucination; grounds analysis in verifiable data |
| Two-score system per investigation report | Enables mathematical ranking with minimal false precision |
| Dependency chain analysis in synthesis | Critical for distinguishing active causes from downstream effects |
| Overlap assessment in synthesis | Prevents redundant fixes and scope bloat |
| Independent ranking agent (not same as investigators) | Investigators inflate their own scores; external review catches this |
| Parallel execution of investigation agents | Prevents anchoring bias; essential for quality |
| Checkpoint after every phase | Enables resumability and audit trail; mandatory |
| Full artifact trail (every intermediate file preserved) | Enables debugging, review, and post-mortem |
| Sentinel-based verification | Immutable proof that verification occurred |

### 10.3 Extensibility Points

**Custom hypothesis strategies**: Provide a YAML file listing hypothesis names and descriptions instead of using the built-in failure-layer or quality-dimension strategies.

**Custom expert panels**: Define expert personas in YAML with name, domain, review focus, and signature concerns.

**Custom scoring presets**: Override any weight or threshold via `scoring-weights.yaml`.

**Domain adaptation**: The templates use a `refinement_mode` context variable that controls terminology:

```yaml
if refinement_mode == "problem":
  validation_subject: "root cause"
  coverage_dimension: "Root cause coverage"
  subject_score_field: "combined_score"

if refinement_mode == "improvement":
  validation_subject: "weakness"
  coverage_dimension: "Weakness coverage"
  subject_score_field: "priority_score"
```

This allows the same debate and synthesis templates to serve both modes.

---

## 11. Anti-Patterns

### What NOT to Do

1. **Do not allow self-assessment**: Self-reported confidence scores were consistently 0.04-0.12 higher than adversarial debate scores. The verification layer must ALWAYS use an independent agent or script. Never ask the producing agent to verify its own work.

2. **Do not use arbitrary parallelism**: Fan-out width should match the number of independent concerns. 5 root causes = 5 parallel agents. Do not spawn 10 agents "for speed."

3. **Do not allow partial synthesis**: The synthesis task must wait for ALL parallel branches. No partial results. This is a hard dependency constraint.

4. **Do not skip checkpoints**: The workflow checkpoints after EVERY phase. This enables resumability and provides audit trail. Checkpointing is mandatory.

5. **Do not rely on false precision**: Scores of 0.90 vs. 0.85 are expert estimates, not measurements. The formulas process this as if it were measurement. When combined scores differ by < 0.05, treat them as essentially tied and use qualitative tie-breaking (e.g., dependency chain position).

6. **Do not trust agent-claimed completion**: File existence + byte size + section heading checks are the minimum verification. An agent saying "I wrote the file" is not proof.

7. **Do not conflate latent defects with active causes**: RC4 (return contract) was a latent defect that never manifested in the observed failure, yet it ranked #4. The dependency chain analysis should gate what enters sprint scope.

8. **Do not bundle heterogeneous items for deferral**: Deferral confidence matrix revealed that items bundled together had wildly different risk profiles (e.g., S03 Change 3 at 0.38 vs. S03 Change 4 at 0.72). Evaluate each item independently.

9. **Do not use inconsistent scoring weights across debates**: The original process used 0.25/0.25/0.20/0.15/0.15 for some debates and 0.20/0.20/0.20/0.20/0.20 for others. Standardize weights in configuration.

10. **Do not generate prompts without exact tool-call syntax**: Workflow A described "investigation steps" (vague). Workflow B included exact prompts (precise). For automated execution, always generate exact prompts. Include investigation steps as supplementary guidance for `--interactive` mode.

11. **Do not proceed with garbage-in after verification failure**: Post-gate verification failures must block the next phase. Garbage-in-garbage-out across phases compounds errors.

---

## 12. Dependency Map

### Required Skills/Commands

| Dependency | Status | Usage | Gap? |
|-----------|--------|-------|------|
| `sc:adversarial` | Exists | Debate orchestration (Phases 3, R2, R4) | Mode B needs testing |
| `sc:spec-panel` | Exists | Expert panel evaluation (Phases R1, R3) | Needs configurable expert personas |
| `sc:analyze` | Exists | Synthesis and gap analysis | None |
| `sc:troubleshoot` | Exists | Root cause investigation | None |
| `sc:reflect` | Exists | Self-review reflection | None |
| `sc:design` | Exists | Solution architecture | None |
| `sc:save` | Exists | Checkpoint persistence | None |

### Required Agents

| Agent | Status | Gap? |
|-------|--------|------|
| `root-cause-analyst` | Exists (persona) | None |
| `weakness-analyst` | **NEW** | Adaptation of root-cause-analyst for improve mode |
| `debate-orchestrator` | Exists | None |
| `system-architect` | Exists (persona) | None |
| `verification-agent` | **NEW** | Structural/arithmetic checking agent |
| `plan-reviewer` | **NEW** | Plan review agent (completeness + consistency) |

### Required Scripts (New)

| Script | Purpose | Complexity |
|--------|---------|------------|
| `verify_file_exists.sh` | Check file existence + non-empty | Trivial (~5 lines) |
| `verify_section_headings.py` | Grep for required headings in markdown | Simple (~30 lines) |
| `verify_numeric_scores.py` | Validate scoring arithmetic | Medium (~60 lines) |
| `verify_cross_references.py` | Check referenced files exist on disk | Medium (~50 lines) |
| `verify_tasklist_log_coverage.py` | Match tasklist entries to log entries | Medium (~40 lines) |
| `generate_checkpoint.py` | Programmatic checkpoint from filesystem | Medium (~80 lines) |
| `generate_sentinel.py` | Write immutable verification sentinel | Simple (~30 lines) |

### Infrastructure Requirements

| Requirement | Status |
|-------------|--------|
| Parallel Task agent dispatch | Available via SuperClaude Task tool |
| File I/O (Read, Write, Edit) | Available |
| Codebase search (Grep, Glob) | Available |
| MCP Sequential Thinking | Available (used for complex synthesis) |
| Checkpoint file I/O | Available (standard file operations) |

### Implementation Priority

1. **SKILL.md** -- Skill definition with wave structure and pipeline configuration
2. **Templates** -- All 10 templates from Section 5
3. **Verification scripts** -- 7 scripts from the scripts/ directory
4. **Configuration files** -- scoring-weights.yaml, expert-personas.yaml, agent-config.yaml, pipeline-config.yaml
5. **weakness-analyst agent** -- New agent definition for improve mode
6. **verification-agent** -- New agent for non-interactive verification
7. **plan-reviewer agent** -- New agent for Stage 0 plan review
8. **Integration testing** -- End-to-end test with a known problem + spec

---

*Design document generated 2026-02-23 by synthesis agent.*
*Source: 5 batch analysis reports totaling ~60,000 words from v2.01-Roadmap-v3 SpecDev process.*
*This document is self-contained: it contains all templates, scoring formulas, verification checks, and configuration needed to build spec-workshop.*
