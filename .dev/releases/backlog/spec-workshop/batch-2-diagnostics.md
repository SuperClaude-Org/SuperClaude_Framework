# Batch 2: Diagnostic Phase Analysis
## Spec Workshop -- Extracting a Repeatable Process

**Source**: v2.01-Roadmap-v3 SpecDev diagnostic artifacts
**Date**: 2026-02-23
**Scope**: Root cause investigation, scoring, ranking, and gap analysis patterns

---

## 1. ROOT CAUSE INVESTIGATION PATTERN

### 1.1 How Each Root Cause Was Investigated

Each of the 5 root causes was investigated by a **parallel sub-agent** (root-cause-analyst type) operating independently on the same problem statement but with a different hypothesis focus. The investigations ran concurrently -- there is no evidence of sequential dependency between RC1-RC5.

**Investigation approach per root cause**:
- **RC1 (Invocation Wiring)**: Infrastructure-focused. Examined tool availability, Skill tool design constraints, codebase precedents for cross-skill invocation.
- **RC2 (Spec-Execution Gap)**: Specification-focused. Compared Wave 2 vs Wave 4 instruction patterns, analyzed verb ambiguity, measured step density.
- **RC3 (Agent Dispatch)**: Registry/binding-focused. Catalogued all 30 agent files, checked for programmatic mappings, traced keyword-affinity heuristics.
- **RC4 (Return Contract)**: Data flow-focused. Examined transport mechanisms, compared against the only existing precedent (sc:cleanup-audit fan-out/fan-in), analyzed Task agent return value constraints.
- **RC5 (Claude Behavior)**: Behavioral-focused. Reconstructed Claude's decision chain, assessed the rationality of the fallback, quantified quality loss from the approximation.

### 1.2 Report Structure Template (Actual)

Every root cause report followed an identical structure. Copied verbatim from the files:

```
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
 Often includes comparison tables, reasoning chains, and "reasonable
 misinterpretation" analysis showing how Claude could rationally arrive
 at the wrong behavior.]

## Likelihood Score: X.XX/1.0
[Justification paragraph explaining the score and the residual uncertainty]

## Impact Score: X.XX/1.0
[Justification paragraph explaining the score and its bounds]

## Recommendation
### [Option A / Immediate Fix]: [Title]
[Description with code examples]

### [Option B / Structural Fix]: [Title]
[Description with code examples]

### [Option C / Long-term Fix]: [Title]
[Description]

### Additional Required Fix (if applicable)
[Cross-cutting fix needed regardless of which option is chosen]
```

### 1.3 Full Template From RC1 (Invocation Wiring)

The following is the exact section structure from `root-cause-01-invocation-wiring.md`:

```markdown
# Root Cause #1: Invocation Wiring Gap

## Summary
[1 paragraph]

## Evidence

### Evidence 1: The failing instruction (sc-roadmap SKILL.md, line 137)
### Evidence 2: The Skill tool's design constraint
### Evidence 3: No precedent for skill-to-skill invocation in the codebase
### Evidence 4: `sc:save` is a command, not a skill -- revealing a category confusion
### Evidence 5: The return contract assumes structured data flow that cannot exist
### Evidence 6: The Skill tool explicitly warns against re-invocation

## Analysis
[3-layer semantic gap analysis: design intent vs. behavioral instruction vs. runtime capability]

## Likelihood Score: 0.95/1.0
## Impact Score: 1.0/1.0

## Recommendation
### Option A: Explicit Skill Tool Call Syntax (Minimal Change)
### Option B: Task Agent Delegation (Recommended)
### Option C: Inline Behavioral Merge (Fallback)
### Additional Required Fix
```

RC1 used 6 evidence items. Other reports used 3-5. The evidence count was proportional to the root cause's complexity, not prescribed.

### 1.4 Full Template From RC2 (Spec-Execution Gap)

The following is the exact section structure from `root-cause-02-spec-execution-gap.md`:

```markdown
# Root Cause #2: Specification-Execution Gap

## Summary
[1 paragraph]

## Evidence

### Wave 2 Instructions (verbatim)
[Full code block from SKILL.md lines 130-143]

### Wave 4 Instructions (verbatim, for comparison)
[Full code block from SKILL.md lines 168-184]

### Adversarial Integration Ref (invocation pattern)
[Full code block from adversarial-integration.md lines 104-126]

## Analysis

### Ambiguity Points
[6 numbered ambiguity points with detailed analysis]

### Specificity Comparison (Wave 2 vs Wave 4)
[8-dimension comparison table]

### Reasonable Misinterpretation
[5-step reasoning chain showing how Claude could reach the wrong conclusion]

## Likelihood Score: 0.85/1.0
## Impact Score: 0.90/1.0

## Recommendation
### Immediate Fix: Make Wave 2 step 3 deterministic
### Structural Fix: Standardize invocation vocabulary across all waves
### Cross-Reference Fix: Inline critical invocation syntax
### Allowed-Tools Fix: Add Skill to allowed-tools
```

**Key difference from RC1**: RC2 used a **comparative analysis** pattern (Wave 2 vs Wave 4) with an explicit comparison table. RC1 used a **semantic gap** analysis (3-layer decomposition). The analysis section structure was not rigid -- it adapted to the root cause's nature.

### 1.5 Common Evidence Patterns Across All Reports

Every report:
1. **Cited specific file paths and line numbers** (e.g., `SKILL.md, line 137`)
2. **Included verbatim code/config blocks** -- never paraphrased critical content
3. **Cross-referenced other framework files** to establish absence of mechanisms (negative evidence)
4. **Searched codebase for precedents** and documented zero-match results as evidence
5. **Reconstructed Claude's probable reasoning chain** to explain the observed behavior

---

## 2. SCORING METHODOLOGY

### 2.1 Root Cause Scoring Dimensions

Each root cause report self-scored on exactly two dimensions:

| Dimension | Definition | Scale |
|-----------|-----------|-------|
| **Likelihood** | Probability that this root cause is an active cause of the observed failure | 0.0 - 1.0 |
| **Impact** | Degree to which this root cause explains the observed failure symptoms | 0.0 - 1.0 |

### 2.2 Self-Reported Scores (Before Validation)

| Root Cause | Likelihood | Impact | Notes |
|-----------|-----------|--------|-------|
| RC1: Invocation Wiring | 0.95 | 1.00 | Highest self-assessment |
| RC2: Spec-Execution Gap | 0.85 | 0.90 | |
| RC3: Agent Dispatch | 0.95 | 0.90 | Most inflated per validation |
| RC4: Return Contract | 0.85 | 0.80 | |
| RC5: Claude Behavior | 0.85 | 0.70 | Most honestly self-assessed |

### 2.3 Validation/Recalibration Methodology

A separate synthesis agent cross-validated all self-reported scores. The recalibration methodology (from `ranked-root-causes.md`):

**Recalibration criteria applied**:
1. **Evidence quality**: Is the evidence concrete/verifiable or inferential?
2. **Inflation detection**: Does the self-reported score overstate the root cause's independent contribution?
3. **Dependency chain membership**: Is this an active cause or a downstream consequence of another root cause?
4. **Overlap assessment**: Does this root cause substantially overlap with another?

**Validated Scores (After Recalibration)**:

| Root Cause | Likelihood (self -> validated) | Impact (self -> validated) | Change Rationale |
|-----------|-------------------------------|---------------------------|-----------------|
| RC1 | 0.95 -> 0.90 | 1.00 -> 0.90 | Impact reduced: explains WHY but not the specific degraded behavior |
| RC2 | 0.85 -> 0.75 | 0.90 -> 0.80 | Both reduced: overlaps with RC1, is a contributing factor not independent cause |
| RC3 | 0.95 -> 0.70 | 0.90 -> 0.75 | Most aggressive reduction: consequence of RC1/RC5, not independent; 0.95 was most inflated |
| RC4 | 0.85 -> 0.75 | 0.80 -> 0.75 | Slightly reduced: latent defect that never had a chance to manifest |
| RC5 | 0.85 -> 0.85 | 0.70 -> 0.70 | No change: most honest self-assessment, explicitly acknowledged compound causation |

### 2.4 Problem Scoring Formula

From the gap analysis, the actual formula used:

```
problem_score = (likelihood * 0.6) + (impact * 0.4)
```

**Rationale for weights**: Likelihood (0.6) weighted higher than impact (0.4) because a lower-likelihood high-impact problem has fewer expected-value consequences than a high-likelihood moderate-impact problem.

### 2.5 Solution Scoring Formula

```
solution_score = (fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)
```

**Dimensions**:
- **fix_likelihood**: Probability the proposed fix will resolve the root cause
- **feasibility**: How easy the fix is to implement within sprint constraints
- **low_blast_radius**: Inverse of the fix's potential for unintended side effects (1.0 = no side effects)

### 2.6 Combined Ranking Formula

```
combined = (problem_score * 0.5) + (solution_score * 0.5)
```

Equal weighting between problem severity and solution quality.

### 2.7 Scoring Critique (From Gap Analysis)

The gap analysis identified both strengths and weaknesses of this scoring approach:

**What the formulas got right**: Enforced discipline that prevented scope creep. Without explicit cutoffs, all five pairs might have been included, producing an undeliverable sprint. Made the RC3/RC5 deferral appear objective rather than arbitrary.

**What the formulas got wrong**: The precision is false. Inputting 0.90 vs. 0.85 for likelihood is not an empirically derivable distinction -- it is an expert estimate. The formula processes this apparent precision as if it were measurement, not estimation. Two panelists (Brooks, Weinberg) recommended replacing the formulas with a simple ordered list or qualitative assessments.

---

## 3. RANKING PROCESS

### 3.1 Ranking Table (Verbatim from ranked-root-causes.md)

```
### Rank 1: Invocation Wiring Gap (RC1)
- Likelihood: 0.95 (self-reported) -> 0.90 (validated)
- Impact: 1.00 (self-reported) -> 0.90 (validated)
- Combined Score: 0.90

### Rank 2: Claude Behavioral Interpretation (RC5)
- Likelihood: 0.85 (self-reported) -> 0.85 (validated)
- Impact: 0.70 (self-reported) -> 0.70 (validated)
- Combined Score: 0.79

### Rank 3: Specification-Execution Gap (RC2)
- Likelihood: 0.85 (self-reported) -> 0.75 (validated)
- Impact: 0.90 (self-reported) -> 0.80 (validated)
- Combined Score: 0.77

### Rank 4: Return Contract Data Flow (RC4)
- Likelihood: 0.85 (self-reported) -> 0.75 (validated)
- Impact: 0.80 (self-reported) -> 0.75 (validated)
- Combined Score: 0.75

### Rank 5: Agent Dispatch Mechanism (RC3)
- Likelihood: 0.95 (self-reported) -> 0.70 (validated)
- Impact: 0.90 (self-reported) -> 0.75 (validated)
- Combined Score: 0.72
```

### 3.2 Synthesis Steps in the Ranking

The ranking was not just a simple sort by combined score. The synthesis agent performed four additional analyses:

**A. Dependency Chain Analysis**

```
RC1 (No invocation mechanism) ─────┐
                                    ├──> RC5 (Claude falls back to approximation)
RC2 (Ambiguous spec language) ──────┘         │
                                              ├──> RC3 (Wrong agent selected for approximation)
                                              │
                                              └──> RC4 (No return contract produced)
```

Key insight: RC3 and RC4 are LATENT DEFECTS that would surface even if RC1 and RC2 were fixed, but they were not the ACTIVE CAUSES of the observed failure.

**B. Overlap Assessment**

- **High Overlap: RC1 + RC2** -- Same problem from different angles (infrastructure vs. specification).
- **High Overlap: RC3 + RC5** -- RC5's analysis subsumes RC3's; system-architect selection is a specific manifestation of the general fallback behavior.
- **Low Overlap: RC4** -- Genuinely independent. Exists regardless of whether invocation works.
- **Redundancy assessment**: 5 root causes could be reduced to 3 distinct problems: (1) Invocation Mechanism Gap, (2) Degraded Fallback Behavior, (3) Return Contract Transport.

**C. Minimal Fix Set Optimization**

Three fixes address all five root causes:

| Root Cause | Fix 1 (allowed-tools) | Fix 2 (rewrite Wave 2) | Fix 3 (return-contract.yaml) |
|-----------|-------|-------|-------|
| RC1 Invocation Wiring | PRIMARY | -- | partial |
| RC2 Spec-Execution Gap | -- | PRIMARY | -- |
| RC3 Agent Dispatch | -- | PRIMARY | -- |
| RC4 Return Contract | -- | -- | PRIMARY |
| RC5 Claude Behavior | PRIMARY | fallback | -- |

**D. Solution Task Assignments**

| Root Cause | Rank | Solution Task | Fix # |
|-----------|------|---------------|-------|
| RC1: Invocation Wiring Gap | 1 | T02.01: Add Skill to allowed-tools | Fix 1 |
| RC5: Claude Behavioral Interpretation | 2 | T02.02: Add fallback protocol to Wave 2 | Fix 2 |
| RC2: Spec-Execution Gap | 3 | T02.03: Rewrite Wave 2 step 3 with explicit tool-call syntax | Fix 2 |
| RC4: Return Contract Data Flow | 4 | T02.04: Define file-based return-contract.yaml convention | Fix 3 |
| RC3: Agent Dispatch Mechanism | 5 | T02.05: Add agent bootstrap step; update stale README | Fix 2 |

---

## 4. GAP ANALYSIS PATTERN

### 4.1 Structure of the Gap Analysis

The gap analysis (`v2.01-roadmap-v3-gap-analysis.md`) compared the full planning process output against the final sprint specification. It was structured as follows:

```markdown
# Gap Analysis: Planning Process vs. Final Sprint Specification

## 1. EXECUTIVE SUMMARY
[Quantitative summary: X ideas in spec, Y deferred, Z rejected, W silently dropped]

## 2. IDEAS THAT MADE IT INTO THE FINAL SPEC
[Per-element trace: origin, transformation, what was added/changed]

## 3. IDEAS CONTEMPLATED BUT DEFERRED TO FUTURE SPRINT
[Table: item, source, reason, future sprint candidate?]

## 4. IDEAS CONTEMPLATED BUT EXPLICITLY REJECTED (WITH REASONS)
[Table: idea, source, rejection rationale]

## 5. IDEAS CONTEMPLATED BUT SILENTLY DROPPED
[Table: idea, source, why it likely fell through]

## 6. FAILURE MODES IDENTIFIED BUT NOT ADDRESSED IN SPEC
[Table: failure mode, source, risk level, gap in spec]

## 7. METHODOLOGY INNOVATIONS FROM THE DIAGNOSTIC PROCESS
[Table: innovation, description, originated in, reusability]

## 8. SCORING AND RANKING DECISIONS
[Detailed analysis of the 3 scoring formulas and their effects on scope]

## 9. RECOMMENDATION: HIGH-VALUE ADDITIONS FOR THE NEXT SPRINT
[Priority 1 (amend current sprint), Priority 2 (next sprint), Priority 3 (backlog)]

## 10. APPENDIX: IDEA DISPOSITION SUMMARY
[Complete 70+ item table with status: IN SPEC, DEFERRED, REJECTED, SILENTLY DROPPED,
 UNADDRESSED FAILURE MODE, METHODOLOGY INNOVATION]
```

### 4.2 Idea Disposition Categories

The gap analysis classified every contemplated idea into exactly one of 6 categories:

| Category | Count | Description |
|----------|-------|-------------|
| IN SPEC | ~42 | Includes refined/transformed versions |
| DEFERRED | ~18 | Explicitly marked as future sprint candidate |
| REJECTED | ~11 | Formally evaluated with documented rejection rationale |
| SILENTLY DROPPED | ~19 | No formal rejection or deferral; fell through |
| UNADDRESSED FAILURE MODE | 7 | Risk identified but no corresponding spec task |
| METHODOLOGY INNOVATION | 6 | Reusable process patterns extracted |

### 4.3 Key Sections -- Idea Tracing Pattern

For each idea that made it into the spec, the gap analysis traced:

1. **What the spec says**: The final form of the idea
2. **Origin**: Which planning artifact(s) first proposed it
3. **Transformation**: How the idea changed from origin to final spec
4. **What was added from spec vs. origin**: Any net-new content introduced during spec writing

Example structure (from Section 2.1, Task 0.0):

```markdown
### 2.1 Task 0.0: Skill Tool Probe

**What the spec says**: Dispatch a single Task agent to empirically test whether
the Skill tool works cross-skill before all implementation begins. Four
decision-gate outcomes mapped to sprint adaptations.

**Origin**: Converged from four independent sources:
- spec-panel-review.md — all four panelists unanimously recommended this
- reflection-final.md (IMP-01) — self-review agent proposed "Task 0.1"
- debate-01 (Unresolved Concern 1) — debate produced Risk R1 at probability 0.40
- CP-P3-END.md — Phase 3 checkpoint carried UC-01 forward

**Transformation**: Originally "Task 0.1" in reflection-final.md. Panel reframed
as "Task 0.0" (must precede everything). Sprint-spec adopted panel framing.

**What was added from spec vs. reflection**: Explicit question about "already
running" semantics — came from Leveson's hazard analysis (H1).
```

### 4.4 Failure Mode Coverage

The gap analysis identified 7 failure modes that were surfaced during analysis but had no corresponding spec task:

| Failure Mode | Risk Level | Gap |
|-------------|-----------|-----|
| sc:adversarial execution timeout | HIGH | No timeout handling in Tasks 1.3, 1.4, or 3.1 |
| Context window exhaustion | HIGH | No context budget management |
| Partial file writes (malformed YAML) | MEDIUM | No YAML parse error handling |
| Recursive skill invocation depth | MEDIUM | No depth limit |
| RC3/RC5 second-order failures | MEDIUM | Explicitly deferred but no monitoring task |
| Fallback path masking by wrong output directory | MEDIUM | No verification test |
| "Already running" constraint applies to caller | HIGH | Task 0.0 probes but no pre-written adaptation plan |

---

## 5. AGENT CONFIGURATION

### 5.1 Agent Types Used

The diagnostic phase used the following agent configuration:

| Role | Agent Type | Count | Execution |
|------|-----------|-------|-----------|
| Root cause investigator | `root-cause-analyst` | 5 (one per hypothesis) | Parallel |
| Ranking/synthesis | Debate orchestrator mode | 1 | Sequential (after all 5 complete) |
| Gap analysis | Synthesis agent (claude-sonnet-4-6) | 1 | Sequential (final phase) |

### 5.2 Root Cause Agent Configuration

Each root-cause-analyst agent received:
- **Input**: The problem statement (failure description), the specific hypothesis to investigate, and access to the codebase
- **Tools**: Read, Grep, Glob (for evidence gathering from codebase)
- **Constraint**: Investigate ONE specific hypothesis per agent
- **Output format**: The standardized report template (Summary, Evidence, Analysis, Likelihood, Impact, Recommendation)

The agents did NOT receive each other's findings -- they operated independently to avoid anchoring bias.

### 5.3 Ranking Agent Configuration

The ranking agent received:
- **Input**: All 5 completed root cause reports
- **Role**: Cross-validate scores, detect overlap, build dependency chains, produce minimal fix set
- **Method**: Adversarial self-critique of self-reported scores

Key instruction from the process: "Cross-validation of self-reported scores against evidence quality, overlap detection, dependency chain analysis, and minimal fix set optimization."

### 5.4 Gap Analysis Agent Configuration

The gap analysis agent received:
- **Input**: Five parallel agent summaries + direct read of sprint-spec.md, reflection-final.md, spec-panel-review.md, DVL-BRAINSTORM.md, ranked-root-causes.md, CP-P4-END.md
- **Model**: claude-sonnet-4-6 (lighter model for synthesis, not opus)
- **Role**: Compare planning artifacts against final spec, classify every idea's disposition

---

## 6. INPUT REQUIREMENTS

### 6.1 What the Diagnostic Phase Needed

| Input | Purpose | Required? |
|-------|---------|-----------|
| **Problem statement** | Description of the observed failure (what went wrong, what was expected) | YES |
| **Source files to analyze** | The codebase files relevant to the failure (skill definitions, agent files, reference docs, config files) | YES |
| **Failure description** | Specific symptoms (e.g., "system-architect agents spawned instead of debate-orchestrator") | YES |
| **Hypothesis set** | 3-7 distinct hypotheses for what could have caused the failure | YES (generated or provided) |
| **Codebase access** | Ability to search, read, and grep the full codebase for evidence | YES |
| **Existing test artifacts** | Compliance tests, prior diagnostics that establish known constraints | HELPFUL |

### 6.2 Hypothesis Generation

In the observed workflow, 5 hypotheses were generated that covered different failure layers:

1. **Infrastructure layer**: Is the mechanism physically possible? (RC1)
2. **Specification layer**: Are the instructions clear enough? (RC2)
3. **Binding layer**: Is the right component connected? (RC3)
4. **Data flow layer**: Can structured data pass between components? (RC4)
5. **Behavioral layer**: Given constraints, what did the agent actually do and why? (RC5)

This layered approach ensures coverage from bottom (infrastructure) to top (behavior). It is a good default hypothesis generation strategy for any agent-system failure.

---

## 7. OUTPUT SCHEMA

### 7.1 Root Cause Report -- Mandatory Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | string | Short name for the root cause |
| Summary | text (1-2 paragraphs) | High-level description |
| Evidence | list of evidence items | Each with title, file paths, line numbers, verbatim quotes |
| Analysis | text (multi-paragraph) | Synthesis connecting evidence to causal explanation |
| Likelihood Score | float 0.0-1.0 | With justification paragraph |
| Impact Score | float 0.0-1.0 | With justification paragraph |
| Recommendation | list of options | At least 2 options with code examples |

### 7.2 Ranked Root Causes Report -- Mandatory Fields

| Field | Type | Description |
|-------|------|-------------|
| Executive Summary | text | 1 paragraph synthesizing the failure |
| Ranked list | ordered list | Each entry: self-reported scores, validated scores, combined score, key evidence, validation notes |
| Dependency Chain | diagram | Causal cascade showing which causes are primary vs. downstream |
| Overlap Assessment | text | Which root causes overlap, which are independent |
| Minimal Fix Set | table | N fixes that address all M root causes, with coverage matrix |
| Solution Task Assignments | table | Mapping from root causes to concrete fix tasks |

### 7.3 Gap Analysis Report -- Mandatory Fields

| Field | Type | Description |
|-------|------|-------------|
| Executive Summary | text with counts | Quantitative summary of idea dispositions |
| Ideas in spec | traced list | Each with origin, transformation, additions |
| Deferred ideas | table | With reason and future sprint candidacy |
| Rejected ideas | table | With rejection rationale |
| Silently dropped ideas | table | With likely reason for falling through |
| Unaddressed failure modes | table | With risk level and gap description |
| Methodology innovations | table | Reusable patterns extracted |
| Scoring analysis | formulas + critique | How scoring affected scope decisions |
| Prioritized recommendations | tiered list | Priority 1 (amend now), Priority 2 (next sprint), Priority 3 (backlog) |

---

## 8. ADAPTATION FOR IMPROVEMENT MODE

### 8.1 Design Decision Context

Two entry modes are planned:
- **Problem-driven**: Root cause -> debate -> solutions (the pattern analyzed above)
- **Improvement-driven**: General analysis -> weaknesses -> improvements

The diagnostic phase described in this batch is specific to problem-driven mode. For improvement-driven mode, a parallel "weakness analysis" phase replaces root causing.

### 8.2 Proposed Weakness Analysis Phase Structure

The weakness analysis phase adapts the root cause pattern by replacing "what caused the failure" with "what are the weakest points in this system."

#### Weakness Investigation Report Template

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

#### Key Differences from Root Cause Template

| Dimension | Problem-Driven (Root Cause) | Improvement-Driven (Weakness) |
|-----------|---------------------------|-------------------------------|
| **Focus question** | "What caused this failure?" | "What is weakest in this system?" |
| **Score dimension 1** | Likelihood (is this the cause?) | Severity (how bad is this weakness?) |
| **Score dimension 2** | Impact (does this explain the symptoms?) | Improvement Potential (how much better could things get?) |
| **Analysis pattern** | Causal chain reconstruction | Failure scenario projection + best practice comparison |
| **Evidence pattern** | Negative evidence (what's missing/broken) | Comparative evidence (current vs. ideal) |
| **Dependency chain** | Causal cascade (A causes B) | Compounding weaknesses (A makes B worse) |
| **Ranking output** | Minimal fix set | Improvement roadmap (prioritized by ROI) |

#### Weakness Scoring Formulas

Adapted from the problem-driven formulas:

```
weakness_score = (severity * 0.5) + (improvement_potential * 0.3) + (feasibility * 0.2)
```

Rationale: Severity weighted highest (address the worst weaknesses first), but improvement potential and feasibility are also considered to avoid investing in low-ROI improvements.

#### Hypothesis Generation for Improvement Mode

Instead of failure-layer hypotheses, use **quality dimension** hypotheses:

1. **Clarity**: Are the specifications clear and unambiguous?
2. **Completeness**: Are there gaps or missing specifications?
3. **Consistency**: Do different parts of the system agree with each other?
4. **Testability**: Can the specified behavior be verified?
5. **Maintainability**: Is the system easy to evolve and modify?
6. **Performance**: Are there efficiency bottlenecks or resource concerns?
7. **Security/Safety**: Are there unmitigated risks?

Each hypothesis becomes one parallel weakness investigation agent.

---

## 9. RECOMMENDATIONS FOR SPEC-WORKSHOP

### 9.1 What Should Be Templatized (Configurable)

| Component | Configurable Parameters | Default |
|-----------|------------------------|---------|
| **Number of hypotheses** | 3-7 | 5 |
| **Hypothesis generation strategy** | failure-layer (problem) or quality-dimension (improvement) | Auto-detect from entry mode |
| **Scoring dimensions** | 2 per report (names configurable) | Likelihood+Impact (problem) or Severity+Potential (improvement) |
| **Scoring formula weights** | All weights in all 3 formulas | 0.6/0.4 for problem, 0.5/0.5 for combined |
| **Validation/recalibration** | Enable/disable cross-validation step | Enabled |
| **Number of recommendations per report** | 2-4 options | 3 |
| **Gap analysis scope** | Which sections to include | All 10 sections |
| **Agent model for synthesis** | opus vs. sonnet for ranking/gap | sonnet for gap, opus for ranking |
| **Top-N cutoff for sprint scope** | How many root causes/weaknesses make it into the fix set | 3 |

### 9.2 What Should Be Hardcoded

| Component | Rationale |
|-----------|-----------|
| **Report structure** (Summary, Evidence, Analysis, Scores, Recommendation) | Consistency enables cross-report comparison and automated processing |
| **Evidence requirements** (file paths, line numbers, verbatim quotes) | Prevents hallucinated claims; grounds all analysis in verifiable data |
| **Two-score system per report** | Enables mathematical ranking; fewer scores = less false precision |
| **Dependency chain analysis** in ranking | Critical insight that distinguishes active causes from downstream consequences |
| **Overlap assessment** in ranking | Prevents redundant fixes and scope bloat |
| **Minimal fix set optimization** in ranking | The highest-value output of the diagnostic phase |
| **Parallel execution** of investigation agents | Prevents anchoring bias; essential for quality |
| **Independent ranking agent** (not the same as any investigator) | Investigators inflate their own scores; external review catches this |

### 9.3 Process Flow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    DIAGNOSTIC PHASE                          │
│                                                             │
│  INPUT: Problem statement OR improvement target             │
│         + source files + codebase access                    │
│                                                             │
│  Step 1: Generate N hypotheses (3-7)                        │
│          [failure-layer or quality-dimension strategy]       │
│                                                             │
│  Step 2: Dispatch N parallel investigation agents           │
│          [one per hypothesis, independent, no cross-talk]   │
│          Output: N reports with 2 scores each               │
│                                                             │
│  Step 3: Ranking synthesis (single agent)                   │
│          - Cross-validate scores (recalibrate inflation)    │
│          - Build dependency chain                           │
│          - Assess overlap                                   │
│          - Compute combined scores                          │
│          - Produce minimal fix set                          │
│          Output: Ranked list + fix coverage matrix           │
│                                                             │
│  Step 4: Gap analysis (optional, post-spec)                 │
│          - Compare planning artifacts vs. final spec        │
│          - Classify all ideas by disposition                 │
│          - Identify unaddressed failure modes               │
│          - Extract methodology innovations                  │
│          Output: Complete disposition table + recommendations│
│                                                             │
│  OUTPUT: Ranked root causes / weaknesses                    │
│          Minimal fix set / improvement roadmap              │
│          Solution task assignments                          │
└─────────────────────────────────────────────────────────────┘
```

### 9.4 Key Methodology Innovations to Preserve

These 6 innovations from the diagnostic process should be baked into the spec-workshop template:

1. **Score Recalibration via Cross-Validation**: Self-reported scores are systematically recalibrated by an independent agent. Catches inflation (RC3 went from 0.95 to 0.70).

2. **Dependency Chain Analysis**: Distinguishes active causes from latent defects. Prevents wasted effort on downstream symptoms.

3. **Minimal Fix Set Optimization**: N fixes covering M root causes, with explicit coverage matrix. Avoids redundant fixes.

4. **Overlap Assessment**: Identifies which root causes could be merged (5 reduced to 3 distinct problems).

5. **Compound Amplification Analysis**: Some combinations of root causes are worse than either alone (RC1+RC2). This changes prioritization.

6. **Idea Disposition Tracking**: Every contemplated idea gets a formal status (IN SPEC, DEFERRED, REJECTED, SILENTLY DROPPED). The "silently dropped" category is the most valuable -- it catches ideas that fell through the cracks.

### 9.5 Anti-Patterns to Avoid

Observed from the scoring critique in the gap analysis:

1. **False precision in scoring**: 0.90 vs. 0.85 is not an empirically derivable distinction. Consider whether qualitative tiers (HIGH/MEDIUM/LOW) would serve equally well with less false precision.

2. **Self-score inflation**: Every agent rated their own root cause as important. The recalibration step is essential, not optional.

3. **Latent defects ranked as active causes**: RC4 (return contract) was a latent defect that never manifested, yet it ranked #4 and made the sprint scope. The dependency chain analysis should gate what enters scope.

4. **Extremely tight margins driving scope decisions**: RC4+S04 and RC2+S02 differed by only 0.002 in combined score. At this precision level, the ranking is essentially a coin flip. Consider tie-breaking rules or explicit acknowledgment of margin-of-error.

---

*Analysis produced 2026-02-23 for the spec-workshop extraction project.*
*Source artifacts: 7 diagnostic files from v2.01-Roadmap-v3/SpecDev/diagnostics/*
