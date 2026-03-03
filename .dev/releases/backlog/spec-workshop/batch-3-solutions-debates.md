# Batch 3: Solutions & Debates Layer Analysis

**Scope**: Solution proposals (5 files), adversarial debates (5 files), deferral confidence matrix, spec panel review
**Source**: `.dev/releases/current/v2.01-Roadmap-v3/SpecDev/solutions/` and `debates/`
**Date**: 2026-02-23
**Analyst**: claude-opus-4-6

---

## 1. Solution Proposal Pattern

### Observed Template Structure

All five solution files follow a consistent template with minor variations. The template has these sections in order:

1. **Title line** with solution number and root cause reference
2. **Problem Summary** -- concise restatement of the root cause with evidence
3. **Options Analysis** -- multiple options (A through D) with pros/cons/feasibility/verdict
4. **Recommended Solution** -- selection with rationale
5. **Implementation Details** -- specific file changes with before/after code
6. **Blast Radius Assessment** -- files modified, files not modified, risk matrix
7. **Confidence Score** -- numeric score with dimension breakdown
8. **Footer** -- date, analyst identity, root cause cross-references

### Full Template Copy: Solution 01 (Invocation Wiring)

```markdown
# Solution #1: Invocation Wiring Fix

## Problem Summary

[Concise restatement of the root cause. Includes evidence from codebase -- specific file paths,
line numbers, and the exact gap identified. States the root cause rank and combined score.]

**Root cause rank**: N of 5, combined score X.XX.

---

## Options Analysis

### Option A: [Name]

**Description**: [What the option does]

**Pros**:
- [Pro 1]
- [Pro 2]

**Cons**:
- [Con 1 -- with specific technical detail, not hand-waving]
- **Critical question**: [Specific uncertainty that needs resolution]

**Feasibility**: LOW | MEDIUM | HIGH | VERY LOW
**Blast radius**: [Assessment of change scope]

### Option B: [Name]
[Same structure as Option A]

### Option C: [Name]
[Same structure as Option A]

### Option D: [Name]
[Same structure as Option A]

---

## Recommended Solution: [Option X] with [Option Y fallback]

### Rationale
[Numbered reasons why this option is correct, referencing architectural principles
and established patterns in the codebase]

**Why not Option A**: [One-sentence rejection with reason]
**Why not Option C**: [One-sentence rejection with reason]
**Why not Option D**: [One-sentence rejection with reason]

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

#### Change 2: [Description]
[Same structure]

### Blast Radius Assessment

**Directly affected files** (N files):
1. [file] -- [change type] ([scope])

**Indirectly affected**:
- [downstream effects]

**Not affected**:
- [explicit exclusions with reasons]

**Risk assessment**:
- [risk level] risk for [change description]

---

## Confidence Score: X.XX/1.0

**Justification**:
[Narrative explaining the score with specific factors that increase or decrease confidence.
Each factor includes a numeric adjustment.]

**What would raise confidence to 0.90+**: [Specific verifiable condition]

---

*Solution designed [date]. Analyst: [model-id] ([persona]).*
*Addresses: [RC reference].*
*Partially addresses: [other RC references].*
```

### Full Template Copy: Solution 04 (Return Contract)

Solution 04 demonstrates a variant with a comparative scoring matrix in the Options Analysis:

```markdown
# Solution 04: Return Contract Data Flow

## Problem Summary

[Root cause description with specific field counts and gap identification]

**Root cause rank**: N of 5 (combined score X.XX). [Latent defect characterization.]

---

## Options Analysis

### Option A: [Name]

| Dimension | Assessment |
|-----------|------------|
| **Reliability** | [Assessment with reasoning] |
| **Inspectability** | [Assessment with reasoning] |
| **Precedent** | [Assessment with codebase reference] |
| **Coupling** | [Assessment] |
| **Complexity** | [Assessment] |
| **Failure modes** | [Enumerated failure modes] |

### Option B: [Name]
[Same table structure]

### Comparative Matrix

| Criterion | Weight | A: [Name] | B: [Name] | C: [Name] | D: [Name] |
|-----------|--------|-----------|-----------|-----------|-----------|
| Reliability | 0.30 | 9 | 4 | 6 | 9 |
| Simplicity | 0.25 | 9 | 5 | 4 | 7 |
| Precedent alignment | 0.20 | 10 | 2 | 5 | 5 |
| Inspectability | 0.15 | 9 | 4 | 7 | 9 |
| Maintenance cost | 0.10 | 8 | 4 | 3 | 6 |
| **Weighted Score** | | **9.15** | **3.95** | **5.15** | **7.45** |

---

## Recommended Solution: Option A -- [Name]

[Rationale]

---

## Implementation Details

### Data Flow Diagram

```
[ASCII art showing the data flow between components with numbered steps]
```

### Changes Required

#### 1. [Component] -- [Description]

**Location**: [file path, line reference]

**Change**: [What to do]

```markdown
[Exact content to add/replace]
```

## YAML Schema Definition

```yaml
# [schema name] v1.0
# Location: [path]
# Producer: [component]
# Consumer: [component]

field_name:
  type: [type]
  enum: [values] (if applicable)
  description: >
    [multi-line description]
  required: true|false
  example: [example value]
```

### Example: [Scenario]

```yaml
[Complete example YAML]
```

---

## Blast Radius Assessment

### Files Modified

| File | Change Type | Risk |
|------|-------------|------|
| [path] | [type] | [risk level] |

### Files NOT Modified

| File | Reason |
|------|--------|
| [path] | [reason] |

### Downstream Impact

| System | Impact | Severity |
|--------|--------|----------|
| [system] | [impact] | [severity] |

### Risk Factors

| Risk | Probability | Mitigation |
|------|-------------|------------|
| [risk] | [probability] | [mitigation] |

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

---

*Solution designed [date]. Analyst: [model-id] ([persona]).*
*Addresses: [RC reference].*
```

### Key Observations About Solution Structure

1. **All solutions include a "Why not" section** -- explicit rejection rationale for non-selected options.
2. **All solutions cross-reference other solutions** -- they track overlapping changes (e.g., "Change 4 is shared with Solution 01").
3. **Confidence scores are broken into dimensions** -- not a single number but a justified breakdown.
4. **Implementation details are specific to the line level** -- not abstract descriptions but exact before/after diffs.
5. **Blast radius is bidirectional** -- both "files modified" and "files NOT modified" are enumerated.
6. **Each solution names its analyst model and persona** -- e.g., "claude-opus-4-6 (self-review agent)" or "claude-opus-4-6 (system architect)".

---

## 2. Debate Structure

### Observed Template Structure

All five debate files follow a consistent adversarial structure:

1. **Header** -- date, orchestrator identity, solution under review, root cause reference
2. **Advocate FOR** -- 3-6 numbered arguments supporting the solution
3. **Advocate AGAINST** -- 3-6 numbered arguments challenging the solution
4. **Rebuttal** -- FOR responds to AGAINST, AGAINST responds to FOR (some debates alternate, some batch)
5. **Scoring Matrix** -- 5 dimensions with weights, FOR/AGAINST/adjudicated scores
6. **Fix Likelihood** -- weighted composite score computation
7. **Unresolved Concerns** -- numbered list with severity and description
8. **Footer** -- date, orchestrator, inputs, outputs

### Full Template Copy: Debate 01 (Invocation Wiring)

```markdown
# Debate: Solution #1 -- Invocation Wiring Fix

*Conducted [date]. Debate orchestrator: [model-id].*
*Solution under review: [option selected] with [fallback].*
*Root cause addressed: [RC reference with rank and score].*

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

### Argument 5: [Thesis statement]
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

### Argument 5: [Thesis statement]
[Same structure]

---

## Rebuttal (FOR responds to AGAINST)

### Rebuttal to Argument 1 ([topic])

[Direct response to the AGAINST argument. Must address the specific evidence
presented, not a strawman. May concede partially.]

### Rebuttal to Argument 2 ([topic])
[Same structure]

[In some debates, AGAINST also rebuts FOR's arguments in a second rebuttal round]

---

## Scoring Matrix

| Dimension | Weight | Score | Justification |
|-----------|--------|-------|---------------|
| Root cause coverage | 0.25 | X.XX | [Multi-sentence justification referencing both FOR and AGAINST arguments] |
| Completeness | 0.20 | X.XX | [Multi-sentence justification] |
| Feasibility | 0.25 | X.XX | [Multi-sentence justification] |
| Blast radius | 0.15 | X.XX | [Multi-sentence justification] |
| Confidence | 0.15 | X.XX | [Multi-sentence justification] |

## Fix Likelihood: X.XX

**Computation**:

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Root cause coverage | 0.25 | X.XX | X.XXX |
| Completeness | 0.20 | X.XX | X.XXX |
| Feasibility | 0.25 | X.XX | X.XXX |
| Blast radius | 0.15 | X.XX | X.XXX |
| Confidence | 0.15 | X.XX | X.XXX |
| **Total** | **1.00** | -- | **X.XXX** |

**Rounded fix likelihood: X.XX**

**Interpretation**: [2-3 sentences explaining what the score means for implementation decisions]

---

## Unresolved Concerns

### 1. [Concern title] (Critical|Medium|Low -- [category])

[Description of the unresolved concern with specific technical detail.
Includes what would need to happen to resolve it.]

### 2. [Concern title] (severity)
[Same structure]

---

*Debate conducted [date]. Analyst: [model-id] ([role]).*
*Input: [solution file] + [root causes file].*
*Fix likelihood: X.XX (weighted). [Additional interpretation].*
```

### Full Template Copy: Debate 03 (Agent Dispatch) -- Variant with Three-Column Scoring

Debate 03 uses a variant scoring matrix that shows FOR score, AGAINST score, and adjudicated score:

```markdown
# Debate 03: Agent Dispatch Fix (Solution #3)

**Root Cause**: [reference]
**Solution**: [option name]
**Date**: [date]
**Orchestrator**: [model-id] ([mode])

---

## Context

[Brief summary of the solution under review and its ranked position]

---

## Advocate FOR: [Position title]

### Opening Position
[Summary thesis for the FOR side]

### Argument 1: [Thesis]
[Evidence-based argument]

### Argument 2: [Thesis]
[Evidence-based argument]

[...]

### Summary FOR
[1-paragraph synthesis of the FOR case]

---

## Advocate AGAINST: [Position title]

### Opening Position
[Summary thesis for the AGAINST side]

### Argument 1: [Thesis]
[Evidence-based argument]

[...]

### Summary AGAINST
[1-paragraph synthesis of the AGAINST case]

---

## Rebuttal: Resolution of Key Disagreements

### On [Topic 1]

[Both advocates' positions stated. Explicit agreement/disagreement identified.
A resolution is proposed by the orchestrator.]

**Resolution**: [Concrete resolution or recommendation]

### On [Topic 2]
[Same structure]

[This variant has the orchestrator actively mediating rather than just
letting advocates respond to each other]

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

**[Dimension] (adjudicated: X.XX)**
[Multi-sentence rationale explaining how FOR and AGAINST scores were weighted
to produce the adjudicated score]

[Repeat for each dimension]

---

## Fix Likelihood

**Fix Likelihood: X.XX (Apply with conditions)**

This solution should be applied, but with N mandatory conditions:

1. **[Condition]**: [Description]
2. **[Condition]**: [Description]
3. **[Condition]**: [Description]

---

## Unresolved Concerns

### Concern 1: [Title]
**Severity**: [High|Medium|Low]
**Description**: [Detail]
**Resolution path**: [What would resolve this]

[Repeat for each concern]

---

## Summary Verdict

[Paragraph synthesis of the debate outcome, acknowledging both sides' strongest points]

**Adjudicated overall score**: X.XXX
**Fix likelihood**: [Apply|Apply with conditions|Defer]
**Priority**: [Implementation sequence position]

---

*Debate conducted [date]. Orchestrator: [model-id].*
*Input: [solution file], [root causes file].*
*Methodology: Two-advocate adversarial scoring with rebuttal and adjudicated resolution.*
```

### Debate Position Structure

The debate positions consistently follow this pattern:

**FOR position arguments** focus on:
- Root cause is correctly identified (evidence chain)
- Solution uses established patterns (precedent in codebase)
- Fallback eliminates single-point-of-failure
- Blast radius is minimal and bounded
- Forward compatibility / reusable pattern

**AGAINST position arguments** focus on:
- Unverified assumptions that underpin the solution
- Dependencies on other solutions not yet implemented
- Maintenance burden introduced
- Edge cases not handled
- Confidence score inflation relative to actual uncertainties

---

## 3. Scoring Rubric

### Dimensions and Weights (Consistent Across All 5 Debates)

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Root cause coverage | 0.25 | Does the solution address the identified root cause? Does it address related causes? |
| Completeness | 0.20 | Are all paths handled (happy, degraded, failure)? Are edge cases covered? |
| Feasibility | 0.25 | Can the solution be implemented with existing tools and patterns? What is the effort? |
| Blast radius | 0.15 | How many files are affected? Are changes additive or structural? |
| Confidence | 0.15 | How certain are we the solution works? What are the untested assumptions? |

**Total weight**: 1.00

### Verdict Determination

The fix likelihood is computed as the weighted sum:

```
Fix Likelihood = SUM(dimension_weight * dimension_score) for all 5 dimensions
```

Each dimension is scored 0.0 to 1.0. The final fix likelihood determines the recommendation:

| Fix Likelihood Range | Recommendation |
|---------------------|----------------|
| 0.80+ | Implement as specified |
| 0.70-0.79 | Implement with conditions/amendments |
| 0.60-0.69 | Implement with significant rework |
| Below 0.60 | Reconsider or defer |

### Actual Scores Across All 5 Debates

| Debate | Root Cause Coverage | Completeness | Feasibility | Blast Radius | Confidence | **Fix Likelihood** |
|--------|-------------------|-------------|------------|-------------|-----------|-------------------|
| Debate 01 (Invocation) | 0.80 | 0.65 | 0.75 | 0.85 | 0.72 | **0.76** |
| Debate 02 (Spec-Exec) | 0.70 | 0.68 | 0.82 | 0.80 | 0.75 | **0.75** |
| Debate 03 (Agent Dispatch) | 0.62 | 0.63 | 0.73 | 0.83 | 0.74 | **0.70** |
| Debate 04 (Return Contract) | 0.75 | 0.68 | 0.83 | 0.85 | 0.77 | **0.77** |
| Debate 05 (Claude Behavior) | 0.72 | 0.65 | 0.70 | 0.82 | 0.72 | **0.72** |

### Scoring Process (Three-Column Variant)

In debates 03-05, the scoring uses a three-column approach:

1. **FOR Score**: The advocate FOR's assessment of how well the solution performs on this dimension
2. **AGAINST Score**: The advocate AGAINST's assessment
3. **Adjudicated Score**: The debate orchestrator's final assessment after weighing both positions

The adjudicated score is NOT a simple average -- it is the orchestrator's judgment considering the strength of each side's arguments on that specific dimension. The justification text explains why the adjudicated score falls where it does.

---

## 4. Deferral/Confidence Matrix

### What It Is

The deferral confidence matrix is a structured adversarial assessment of 18 explicitly deferred solutions/features. Its purpose is to validate that deferral decisions were correct by debating each item using the adversarial methodology (advocate FOR deferral, advocate AGAINST deferral, synthesis + scoring).

### Scoring Rubric

```markdown
| Score Range | Interpretation | Recommended Action |
|-------------|---------------|-------------------|
| 0.0 - 0.25 | Deferral strongly unjustified -- item should have been in sprint | Escalate to sprint amendment |
| 0.26 - 0.50 | Deferral questionable -- item close to sprint threshold | Add to priority backlog with urgency flag |
| 0.51 - 0.75 | Deferral justified with minor concerns | Defer but schedule explicitly in next sprint |
| 0.76 - 1.00 | Deferral clearly correct | Maintain deferral; revisit per planned timeline |
```

### Full Matrix (18 Items)

```markdown
| # | Deferred Item | Deferral Confidence | Risk If Deferred | Recommendation | Agent |
|---|--------------|--------------------:|-----------------|----------------|-------|
| 1 | RC3+S03: Agent Dispatch Convention | 0.71 | MEDIUM-HIGH | NEXT-SPRINT | Agent 1 |
| 2 | RC5+S05: Claude Behavioral Fallback (unabsorbed) | 0.57 | MEDIUM | ESCALATE (quality gate); DEFER (probe-and-branch) | Agent 1 |
| 3 | Two-tier quality gate for S05 | 0.48 | MEDIUM-HIGH | ESCALATE (Tier 1); DEFER (Tier 2) | Agent 1 |
| 4 | S03 Change 1: Agent Taxonomy Docs | 0.72 | MEDIUM | NEXT-SPRINT | Agent 2 |
| 5 | S03 Change 2: agent_bootstrap field | 0.63 | MEDIUM | NEXT-SPRINT | Agent 2 |
| 6 | S03 Change 3: Dead subagent_type fields | 0.38 | MEDIUM | ESCALATE | Agent 2 |
| 7 | S03 Change 4: debate-orchestrator frontmatter | 0.62 | MEDIUM | NEXT-SPRINT | Agent 3 |
| 8 | S03 Change 5: merge-executor frontmatter | 0.65 | MEDIUM | NEXT-SPRINT | Agent 3 |
| 9 | S03 Change 6: agents/README.md update | 0.58 | MEDIUM | NEXT-SPRINT | Agent 3 |
| 10 | DVL verify_pipeline_completeness.sh | 0.79 | LOW-MEDIUM | MAINTAIN DEFERRAL | Agent 4 |
| 11 | DVL dependency_gate.sh | 0.83 | LOW | MAINTAIN DEFERRAL | Agent 4 |
| 12 | DVL check_file_references.py | 0.73 | MEDIUM | DEFER WITH CONCERN | Agent 4 |
| 13 | DVL generate_checkpoint.py | 0.82 | LOW-MEDIUM | NEXT-SPRINT (v2.1) | Agent 5 |
| 14 | Framework-level Skill Return Protocol | 0.85 | LOW-MEDIUM | BACKLOG | Agent 5 |
| 15 | Agent Registry (refs/agent-registry.md) | 0.73 | MEDIUM | NEXT-SPRINT | Agent 5 |
| 16 | Framework-level Agent Dispatch (TS v5.0) | 0.97 | LOW | MAINTAIN DEFERRAL | Agent 6 |
| 17 | Concurrency namespacing | 0.82 | LOW-MEDIUM | DEFER WITH CONCERN | Agent 6 |
| 18 | Debt register / tracking mechanism | 0.55 | MEDIUM | DEFER WITH CONCERN | Agent 6 |
```

### Role in the Workflow

The deferral confidence matrix serves three purposes:

1. **Validation of sprint scoping decisions** -- confirms that items excluded from the sprint were correctly excluded (or flags classification errors)
2. **Priority ordering for the next sprint** -- items with low deferral confidence (below 0.50) are flagged for escalation back into the current sprint
3. **Detection of bundling errors** -- several items that were deferred as part of a package were found to have heterogeneous risk profiles (e.g., S03 Change 3 at 0.38 was incorrectly bundled with higher-risk S03 changes)

### Method

6 parallel agents each debated 3 items sequentially. Each debate used the sc:adversarial methodology:
- Advocate FOR deferral (steelman case for keeping it deferred)
- Advocate AGAINST deferral (steelman case for including it)
- Synthesis with scoring

Key structural elements of each item debate:
- "Why is NOW the wrong time?"
- "What must be true first?"
- "What is the blast radius risk if included now?"
- "Does the sprint succeed without it?"
- vs.
- "What specific failure mode does deferral enable?"
- "How close to the sprint threshold?"
- "Actual effort vs. risk of not implementing?"
- "Incorrect assumptions behind deferral?"

---

## 5. Spec Panel Review

### What It Is

A simulated expert panel review of the sprint specification, using four named software engineering authorities as expert personas. Each expert reviews independently, then a structured synthesis identifies consensus and contested points.

### The Experts

| Expert | Domain | Role in Review |
|--------|--------|----------------|
| **Fred Brooks** | Software engineering, complexity, conceptual integrity | Scope discipline, second-system effect detection |
| **Leslie Lamport** | Specification precision, state machines, temporal properties | Formal correctness, state machine completeness |
| **Nancy Leveson** | System safety, STAMP, hazard analysis | Safety-critical interaction analysis, hazard identification |
| **Gerald Weinberg** | Psychology of programming, human factors, cognitive load | Implementer experience, cognitive load assessment |

### Review Structure

Each expert review follows this format:

```markdown
### [Expert Name] ([Domain])

#### Top Concern: [One-sentence thesis]

[2-4 paragraphs explaining the concern with specific line references to the sprint spec,
technical reasoning, and identification of the hazard or deficiency]

#### Specific Improvements

1. **[Improvement title].** [Concrete description with exact location, current text,
   and proposed replacement text]
2. **[Improvement title].** [Same structure]
3. **[Improvement title].** [Same structure]
4. **[Improvement title].** [Same structure]

#### What I Would Cut

- [Item to remove with rationale]
- [Item to remove with rationale]
```

### Panel Synthesis Structure

```markdown
## Panel Synthesis

### Consensus Improvements (All 4 Experts Agree)

1. **[Improvement]** [Which experts said what. **Concrete change**: exact text to add/modify]
2. [Same structure]

### Contested Points

**[Topic]: [Options]**
- **[Expert A and B] say [position].** [Rationale]
- **[Expert C and D] say [other position].** [Rationale]
- **Resolution**: [Panel's decision]

### Final Recommendations

Ordered by `(impact * likelihood_of_success) / effort`:

| Rank | Recommendation | Impact | Success Likelihood | Effort | Score |
|------|---------------|--------|-------------------|--------|-------|
| 1 | [rec] | X.XX | X.XX | [qualitative] | X.XX |

### Confidence Votes

| Expert | Confidence | Reasoning |
|--------|-----------|-----------|
| [name] | XX% | "[Quote with reasoning]" |

**Panel average**: XX% confidence.
**Primary confidence gap**: [The single most impactful unknown]
```

### Actual Panel Consensus Findings

The four experts agreed on four improvements:

1. **Add Task 0.0: Empirical Skill tool probe** (all four identified Risk R1 as the critical unknown)
2. **Remove DVL from sprint spec** (second-system effect, false safety, cognitive load)
3. **Fix fallback_mode schema inconsistency** (referenced but not defined in schema)
4. **Add implementer's summary** (spec organized for analysis not implementation)

### Actual Confidence Votes

| Expert | Confidence |
|--------|-----------|
| Fred Brooks | 55% |
| Leslie Lamport | 40% |
| Nancy Leveson | 45% |
| Gerald Weinberg | 60% |
| **Panel average** | **50%** |

---

## 6. Prompts Used

### Solution Agent Prompts

No explicit prompts for solution generation were found in the files. The solutions were authored by named agents with specific personas:

- Solution 01: `claude-opus-4-6 (self-review agent)`
- Solution 02: `claude-opus-4-6 (self-review agent)`
- Solution 03: `claude-opus-4-6 (system architect)`
- Solution 04: `claude-opus-4-6 (system-architect persona)`
- Solution 05: No explicit persona stated in footer

### Debate Orchestrator Configuration

All five debates were orchestrated by `claude-sonnet-4-6` in `debate orchestrator mode`.

### Task Agent Prompts Found in Solution 01

The following Task agent prompt was specified verbatim in Solution 01, Change 3:

```
You are the adversarial pipeline orchestrator. Your sole job is to execute the
sc:adversarial skill and write its return contract to a file.

STEP 1: Use the Skill tool to invoke sc:adversarial with these arguments:
  --source {spec_path} --generate roadmap --agents {expanded_agents}
  --depth {depth} --output {output_dir} {--interactive if set}

STEP 2: After sc:adversarial completes, write the return contract to:
  {output_dir}/adversarial/return-contract.yaml

The return contract MUST contain these fields:
  status: success | partial | failed
  merged_output_path: <path to merged file>
  convergence_score: <0.0-1.0>
  artifacts_dir: <path to adversarial/ directory>
  unresolved_conflicts: <count of unresolved items>
  base_variant: <model:persona of winning variant>

STEP 3: If the Skill tool is unavailable or fails, respond with:
  "SKILL_UNAVAILABLE: sc:adversarial could not be invoked via Skill tool."
```

### Fallback Protocol Prompts Found in Solution 05

Solution 05 contains explicit Task agent prompts for the F1-F5 fallback steps:

**F2 (Diff Analysis)**:
```
You are a diff analyst. Compare these {N} variants and produce a structured diff analysis.
For each topic covered by the variants:
1. Identify structural differences (section ordering, hierarchy)
2. Identify content differences (different approaches to same topic)
3. Detect contradictions (opposing claims, requirement-constraint conflicts)
4. Extract unique contributions (ideas in only one variant)
Organize output with severity ratings: Low/Medium/High.
```

**F3 (Simplified Debate)**:
```
You are an advocate for Variant {N}. Given the diff analysis and all variants:
1. STEELMAN each opposing variant (state their strongest argument)
2. Present your variant's strengths with evidence (cite sections)
3. Critique opposing variants with evidence
4. Acknowledge genuine weaknesses in your variant
For each diff point, state which variant's approach is superior and why.
```

**F4 (Scoring)**:
```
You are a scoring judge. Given {N} variants, the diff analysis, and advocate arguments:
1. For each diff point, determine winner variant and confidence (50-100%)
2. Score each variant on: requirement coverage, internal consistency, specificity, clarity
3. Select the strongest variant as base
4. List strengths from non-base variants to incorporate
5. Estimate convergence: (agreed diff points / total diff points)
```

**F5 (Merge)**:
```
You are a merge executor. Given the base variant and the incorporation list from scoring:
1. Start from the base variant text
2. For each strength to incorporate: integrate it at the appropriate location
3. Add provenance comments: <!-- Source: Variant N, Section X -->
4. Validate: no contradictions introduced, all references resolve
5. Produce the merged output.
```

### Deferral Matrix Debate Prompts (Structural Pattern)

Each deferral debate uses these structured questions:

**FOR deferral (steelman)**:
- "Why is NOW the wrong time?"
- "What must be true first before this is safe/useful to add?"
- "What is the blast radius risk if included in this sprint?"
- "Does the sprint succeed without it?"

**AGAINST deferral (steelman)**:
- "What specific failure mode does deferral enable?"
- "How close to the sprint threshold was this item?"
- "What is the actual effort to implement vs. the risk of not implementing?"
- "Does any evidence suggest the deferral decision was based on incorrect assumptions?"

### Spec Panel Review Prompt (Per Expert)

Each expert review follows a structured brief:

```
#### Top Concern: [Single most important concern]
[Analysis]

#### Specific Improvements
[Numbered, concrete changes with location and replacement text]

#### What I Would Cut
[Items to remove with rationale]
```

The panel synthesis then has a Task 0.0 probe prompt specified verbatim:

```
Dispatch a single Task agent with this prompt: "Use the Skill tool with
skill: 'sc:adversarial'. Report the exact result: success, error message,
or tool not available."
```

---

## 7. Agent Types Used

### Solution Phase

| Agent | Model | Persona | Role |
|-------|-------|---------|------|
| Solution author | claude-opus-4-6 | self-review agent | Solutions 01, 02 |
| Solution author | claude-opus-4-6 | system architect | Solutions 03, 04 |
| Solution author | claude-opus-4-6 | (unspecified) | Solution 05 |

All solutions were authored by `claude-opus-4-6` with different persona activations depending on the domain.

### Debate Phase

| Agent | Model | Role |
|-------|-------|------|
| Debate orchestrator | claude-sonnet-4-6 | Orchestrated all 5 debates |
| Advocate FOR | (same as orchestrator) | Simulated within orchestrator context |
| Advocate AGAINST | (same as orchestrator) | Simulated within orchestrator context |

The debates were conducted by a single orchestrator agent (`claude-sonnet-4-6`) that simulated both advocate positions. The advocates were not separate agent dispatches -- they were structural sections within a single agent's output.

### Deferral Matrix Phase

| Agent | Model | Items |
|-------|-------|-------|
| Agent 1 | claude-sonnet-4-6 | Items 1, 2, 3 |
| Agent 2 | claude-sonnet-4-6 | Items 4, 5, 6 |
| Agent 3 | claude-sonnet-4-6 | Items 7, 8, 9 |
| Agent 4 | claude-sonnet-4-6 | Items 10, 11, 12 |
| Agent 5 | claude-sonnet-4-6 | Items 13, 14, 15 |
| Agent 6 | claude-sonnet-4-6 | Items 16, 17, 18 |

6 parallel agents, each handling 3 items sequentially. All were `claude-sonnet-4-6`.

### Spec Panel Phase

| Agent | Persona | Domain |
|-------|---------|--------|
| Panel reviewer | Fred Brooks | Software engineering, complexity |
| Panel reviewer | Leslie Lamport | Specification precision, state machines |
| Panel reviewer | Nancy Leveson | System safety, STAMP |
| Panel reviewer | Gerald Weinberg | Psychology of programming, human factors |

The panel reviewers were simulated expert personas. The synthesis was performed by the orchestrating agent.

### Configuration Pattern

- **Solutions**: Authored by the highest-capability model (opus) with domain-specific personas
- **Debates**: Orchestrated by a mid-tier model (sonnet) running both advocate positions
- **Deferral matrix**: Parallelized across 6 sonnet agents (3 items each)
- **Panel review**: Single agent simulating 4 expert personas independently, then synthesizing

---

## 8. Input/Output Contracts

### Solution Proposal Phase

| | Detail |
|---|--------|
| **Input** | `ranked-root-causes.md` (from diagnostics phase) |
| **Input format** | Markdown with ranked root causes, combined scores, dependency chains |
| **Output** | One `solution-NN-[slug].md` per root cause |
| **Output format** | Markdown following the solution template (Problem Summary, Options Analysis, Recommended Solution, Implementation Details, Blast Radius, Confidence Score) |
| **Key fields produced** | Confidence score (0-1), recommended option, files to modify, implementation diffs, overlap with other solutions |
| **Naming convention** | `solution-01-invocation-wiring.md` through `solution-05-claude-behavior.md` |

### Debate Phase

| | Detail |
|---|--------|
| **Input** | `solution-NN-[slug].md` + `ranked-root-causes.md` |
| **Input format** | The solution document plus the root cause analysis that validates scores |
| **Output** | One `debate-NN-[slug].md` per solution |
| **Output format** | Markdown following the debate template (FOR/AGAINST/Rebuttal/Scoring Matrix/Fix Likelihood/Unresolved Concerns) |
| **Key fields produced** | Fix likelihood (0-1), 5-dimension scoring matrix, unresolved concerns list, verdict (implement/implement with conditions/defer) |
| **Naming convention** | `debate-01-invocation-wiring.md` through `debate-05-claude-behavior.md` |

### Deferral Confidence Matrix

| | Detail |
|---|--------|
| **Input** | Sprint spec, gap analysis, all debate files, all solution files |
| **Input format** | Multiple markdown documents |
| **Output** | `deferral-confidence-matrix.md` |
| **Output format** | Summary matrix table + individual debate transcripts per item |
| **Key fields produced** | Per-item deferral confidence (0-1), risk-if-deferred, risk-if-included, recommendation (ESCALATE/NEXT-SPRINT/MAINTAIN DEFERRAL/DEFER WITH CONCERN/BACKLOG) |
| **Agent structure** | 6 parallel agents, 3 items each |

### Spec Panel Review

| | Detail |
|---|--------|
| **Input** | Sprint spec (the implementation plan synthesized from debates) |
| **Input format** | Markdown sprint specification |
| **Output** | `spec-panel-review.md` |
| **Output format** | Individual expert reviews + panel synthesis + consensus improvements + confidence votes |
| **Key fields produced** | Per-expert top concern, specific improvements, what to cut, confidence vote (%), panel average confidence, ranked recommendations |

### Full Pipeline Flow

```
ranked-root-causes.md (from diagnostics)
    |
    v
[Solution Phase: 1 opus agent per root cause, 5 parallel]
    |
    v
solution-01.md ... solution-05.md
    |
    v
[Debate Phase: 1 sonnet agent per solution, 5 parallel]
    |
    v
debate-01.md ... debate-05.md
    |
    v
[Sprint Spec Synthesis: combines debate verdicts into implementation plan]
    |
    v
sprint-spec.md
    |               |
    v               v
[Deferral Matrix]   [Panel Review]
6 parallel agents   4 expert personas
    |               |
    v               v
deferral-           spec-panel-
confidence-         review.md
matrix.md
```

---

## 9. Pattern for Parallel Verification

### Proposed Verification Agent Pattern

Based on the debate scoring rubrics and quality gates observed in the artifacts, here is a verification agent pattern for non-interactive mode:

#### Verification Agent: Solution Completeness Checker

```markdown
## Verification Agent: solution-completeness

**Trigger**: After each solution file is generated
**Model**: sonnet (fast, sufficient for structural checks)
**Input**: solution-NN-[slug].md
**Output**: solution-NN-verification.json

**Checks**:
1. STRUCTURAL COMPLETENESS
   - [ ] Problem Summary section exists and references a ranked root cause
   - [ ] Options Analysis has >= 3 options with pros/cons/feasibility
   - [ ] Recommended Solution section exists with rationale
   - [ ] Implementation Details has a Files to Modify table
   - [ ] Each code change has BEFORE and AFTER blocks
   - [ ] Blast Radius section includes both "modified" and "not modified" lists
   - [ ] Confidence Score exists with dimension breakdown

2. CROSS-REFERENCE INTEGRITY
   - [ ] Root cause rank matches ranked-root-causes.md
   - [ ] File paths in Implementation Details exist in the codebase
   - [ ] Line number references are within the actual file length
   - [ ] Overlap references to other solutions name existing solution files

3. CONSISTENCY
   - [ ] Confidence score is between 0.0 and 1.0
   - [ ] Recommended option is one of the analyzed options
   - [ ] Rejected options each have a "Why not" explanation
   - [ ] Fallback protocol exists if confidence < 0.85

**Verdict**: PASS | PASS_WITH_WARNINGS | FAIL
**Failure action**: Return to solution author with specific failing checks
```

#### Verification Agent: Debate Quality Checker

```markdown
## Verification Agent: debate-quality

**Trigger**: After each debate file is generated
**Model**: sonnet
**Input**: debate-NN-[slug].md + solution-NN-[slug].md
**Output**: debate-NN-verification.json

**Checks**:
1. STRUCTURAL COMPLETENESS
   - [ ] FOR section has >= 3 arguments
   - [ ] AGAINST section has >= 3 arguments
   - [ ] Rebuttal section exists with responses to >= 2 AGAINST arguments
   - [ ] Scoring Matrix has all 5 dimensions with weights summing to 1.00
   - [ ] Fix Likelihood computation matches the weighted sum of scores
   - [ ] Unresolved Concerns section exists

2. ARGUMENT QUALITY
   - [ ] FOR arguments cite specific evidence (file paths, line numbers, precedents)
   - [ ] AGAINST arguments challenge specific claims from the solution (not strawmen)
   - [ ] Rebuttals address the AGAINST argument directly (not tangential)
   - [ ] At least 1 AGAINST argument is partially conceded in rebuttal

3. SCORING INTEGRITY
   - [ ] All dimension scores are between 0.0 and 1.0
   - [ ] Dimension justifications reference specific FOR/AGAINST arguments
   - [ ] Fix likelihood matches weighted computation (arithmetic check)
   - [ ] Fix likelihood is lower than solution's self-reported confidence
        (debate should stress-test, not confirm)

4. INDEPENDENCE
   - [ ] AGAINST position identifies at least 1 concern not in the solution document
   - [ ] Unresolved concerns include at least 1 item not raised in FOR or AGAINST

**Verdict**: PASS | PASS_WITH_WARNINGS | FAIL
**Failure action**: Return to debate orchestrator with specific failing checks
```

#### Verification Agent: Deferral Matrix Validator

```markdown
## Verification Agent: deferral-validator

**Trigger**: After deferral confidence matrix is generated
**Model**: sonnet
**Input**: deferral-confidence-matrix.md + sprint-spec.md
**Output**: deferral-validation.json

**Checks**:
1. COMPLETENESS
   - [ ] All deferred items from sprint spec are represented
   - [ ] Each item has FOR and AGAINST debate transcripts
   - [ ] Each item has a confidence score and recommendation

2. CALIBRATION
   - [ ] No confidence score uses the full 0.0-1.0 range (should cluster 0.3-0.9)
   - [ ] Items with ESCALATE recommendation have confidence < 0.50
   - [ ] Items with MAINTAIN DEFERRAL have confidence > 0.75
   - [ ] Recommendations are consistent with score ranges in the rubric

3. BUNDLING CHECK
   - [ ] Items that were originally part of a bundle are evaluated independently
   - [ ] Heterogeneous risk profiles within bundles are identified
   - [ ] Classification errors (e.g., low-risk item bundled with high-risk) are flagged

**Verdict**: PASS | PASS_WITH_WARNINGS | FAIL
```

---

## 10. Recommendations for spec-workshop

### What Is Reusable (Domain-Independent)

The following elements can be directly templatized for any software specification workshop:

1. **Solution template structure** -- Problem Summary, Options Analysis (with comparative matrix), Recommended Solution, Implementation Details, Blast Radius, Confidence Score. This structure works for any problem domain.

2. **Debate template structure** -- FOR/AGAINST/Rebuttal/Scoring Matrix/Fix Likelihood/Unresolved Concerns. The adversarial format is domain-independent.

3. **Scoring rubric** -- The 5-dimension scoring matrix (root cause coverage, completeness, feasibility, blast radius, confidence) with fixed weights (0.25, 0.20, 0.25, 0.15, 0.15). These dimensions apply to any software fix.

4. **Deferral confidence scoring** -- The 0.0-1.0 deferral confidence scale with the four-band interpretation (strongly unjustified / questionable / justified with concerns / clearly correct). The structured debate questions (FOR: "Why is NOW the wrong time?" / AGAINST: "What specific failure mode does deferral enable?") generalize to any sprint scoping decision.

5. **Panel review format** -- Expert personas with independent reviews followed by structured synthesis. The per-expert format (Top Concern, Specific Improvements, What I Would Cut) is reusable. The confidence vote aggregation provides a quality signal.

6. **Verification agent patterns** -- Structural completeness checkers, cross-reference integrity, scoring arithmetic validation.

### What Is Domain-Specific (Needs Adaptation)

1. **Expert personas** -- Brooks/Lamport/Leveson/Weinberg were chosen for software specification. Other domains need different expert perspectives (e.g., security audits might use Schneier/Saltzer/Schroeder/Anderson).

2. **Root cause ranking formula** -- The `problem_score = (likelihood * 0.6) + (impact * 0.4)` formula is specific to the failure investigation. Other workflows may weight differently.

3. **Fallback protocol prompts** -- The F1-F5 Task agent prompts are specific to the adversarial pipeline. Each domain needs its own fallback procedure prompts.

4. **Blast radius dimensions** -- The specific risk factors (file count, wave disruption, SKILL.md coordination) are SuperClaude-specific. Other projects have different blast radius concerns.

### Recommended Template Files for spec-workshop

```
spec-workshop/
  templates/
    solution-template.md          # From Section 1 above
    debate-template.md            # From Section 2 above
    debate-template-3col.md       # Three-column scoring variant
    scoring-rubric.md             # From Section 3 above
    deferral-matrix-template.md   # From Section 4 above
    panel-review-template.md      # From Section 5 above
    verification-agents/
      solution-completeness.md    # From Section 9 above
      debate-quality.md           # From Section 9 above
      deferral-validator.md       # From Section 9 above
  config/
    scoring-weights.yaml          # Configurable dimension weights
    expert-personas.yaml          # Domain-specific expert profiles
    agent-config.yaml             # Model selection: opus for solutions, sonnet for debates
```

### Key Design Decisions to Preserve

1. **Solutions authored by highest-capability model, debates by mid-tier** -- opus generates solutions, sonnet stress-tests them. This asymmetry is intentional: the solution needs creative depth, the debate needs critical breadth.

2. **Full artifact trail always produced** -- Every step writes a file. No in-memory-only state. This enables debugging, review, and post-mortem analysis.

3. **Debates always reduce confidence** -- Across all 5 debates, the fix likelihood was lower than the solution's self-reported confidence. This is the correct behavior for adversarial validation.

4. **Deferral matrix uses parallel agents** -- 6 agents x 3 items is more efficient than 1 agent x 18 items. The items are independent, so parallelism is safe.

5. **Panel review uses named expert personas** -- Not generic "reviewer 1, 2, 3" but named experts with known domains. This produces more differentiated and specific feedback.

6. **Unresolved concerns are first-class outputs** -- Every debate produces a numbered list of unresolved concerns with severity ratings. These flow into the sprint spec as risks.

### Process Flow for Automated spec-workshop

```
Input: ranked-root-causes.md
  |
  v
[PARALLEL: 1 opus agent per root cause]
  Generate: solution-NN.md (using solution-template.md)
  |
  v
[PARALLEL: 1 sonnet verification agent per solution]
  Validate: solution-NN-verification.json
  |
  v (fix any FAIL results, re-generate)
  |
[PARALLEL: 1 sonnet debate agent per solution]
  Generate: debate-NN.md (using debate-template.md)
  |
  v
[PARALLEL: 1 sonnet verification agent per debate]
  Validate: debate-NN-verification.json
  |
  v (fix any FAIL results, re-generate)
  |
[SEQUENTIAL: synthesis agent]
  Generate: sprint-spec.md (combining debate verdicts)
  |
  v
[PARALLEL: deferral matrix + panel review]
  |--- 6 sonnet agents: deferral-confidence-matrix.md
  |--- 1 opus agent: spec-panel-review.md (4 expert personas)
  |
  v
[SEQUENTIAL: final integration]
  Apply panel recommendations to sprint-spec.md
  Escalate deferral matrix items as needed
  |
  v
Output: final sprint-spec.md + full artifact trail
```

---

*Analysis completed 2026-02-23. Source files: 12 documents across solutions/, debates/.*
*Total content analyzed: ~45,000 words across solution proposals, adversarial debates, deferral confidence scoring, and expert panel review.*
