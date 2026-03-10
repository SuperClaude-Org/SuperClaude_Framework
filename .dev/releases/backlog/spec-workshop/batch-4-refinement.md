# Batch 4: Refinement Workflow Analysis

> **Scope**: The second stage of spec development -- validating a draft spec against root causes, proposing optimizations, and debating those optimizations.
> **Source files**: T01-dvl-evaluation.md, T02-debate-RC1 through RC5, T02-synthesis.md, T03-optimizations.md, T04-debate-opt1 through opt5, T04-synthesis.md
> **Date**: 2026-02-23

---

## 1. DVL Evaluation Pattern (T01)

### What the Panel Was Asked to Do

An expert panel of four specialists (Specification Expert, Testing Expert, DevOps Engineer, Architect) evaluated a set of proposed verification scripts against a single criterion: **detection effectiveness** -- "If the silent pipeline bypass happened again, would this script detect it?"

The evaluation had the following structure:

1. **Script Evaluation Table** -- Each script scored 0.0 to 1.0 with detailed rationale
2. **Ranked List** -- Scripts ordered by detection effectiveness with sprint priority recommendations
3. **Lightweight vs Full Implementation Classification** -- LOC estimates, time estimates, complexity ratings
4. **Sprint-Spec Refactor Proposal** -- Concrete task specifications for promoted scripts
5. **LOC/Complexity Summary Table**
6. **Panel Consensus Notes** -- Unanimous agreements, majority agreements, dissents

### Evaluation Structure (Copied from T01)

```
| # | Script | Tier | Detection Effectiveness | Rationale |
|---|--------|------|------------------------|-----------|
| 1 | `verify_allowed_tools.py` | Pre-Gate | **0.95** | Directly detects the root cause (RC1). If Skill is absent from allowed-tools, this script fails before any agent runs. Would have prevented the original failure entirely. Docked 0.05 because the failure could also occur with Skill present but unavailable at runtime. |
| 2 | `dependency_gate.sh` | Pre-Gate | **0.50** | Checks that predecessor output files exist before a task starts. The original failure was WITHIN a phase (steps skipped inside Wave 2), not BETWEEN phases. Catches inter-phase failures but not intra-phase pipeline bypass. |
...
```

### Ranked List Format (Copied from T01)

```
| Rank | Script | Score | Category | Sprint Priority (from brainstorm) |
|------|--------|-------|----------|-----------------------------------|
| 1 | `verify_pipeline_completeness.sh` | 0.95 | Symptom detector | DEFER |
| 2 | `verify_allowed_tools.py` | 0.95 | Root cause detector | KEEP |
| 3 | `validate_return_contract.py` | 0.85 | Output boundary validator | KEEP |
| 4 | `validate_wave2_spec.py` | 0.70 | Preventive spec validator | KEEP (if time) |
| 5 | `generate_checkpoint.py` | 0.60 | Audit trail generator | DEFER |
```

### Implementation Classification Format (Copied from T01)

```
### Lightweight: < 30 lines, < 1 hour

| Script | Est. LOC | Est. Time | Rationale |
|--------|----------|-----------|-----------|
| `verify_allowed_tools.py` | 15-20 | 20 min | Read file, regex extract allowed-tools line, check membership. Trivially simple. |

### Medium: 30-100 lines, 1-4 hours
...
### Full: > 100 lines, > 4 hours
...
```

### Sprint-Spec Refactor Proposal Task Template (Copied from T01)

Each proposed task addition used this 8-field format:

```
| Field | Value |
|-------|-------|
| Task # | 1.5 |
| Task Name | Create `verify_allowed_tools.py` pre-gate script |
| File | `scripts/dvl/tier1/verify_allowed_tools.py` |
| Change | Create script that parses frontmatter `allowed-tools` line from a given file and asserts all required tools are present. Accept file path and required tool names as CLI arguments. Exit 0 if all present, exit 1 with missing tools to stderr. |
| Dependencies | Tasks 1.1 and 1.2 (needs files to validate against) |
| Acceptance Criteria | Script exists; `uv run python scripts/dvl/tier1/verify_allowed_tools.py src/superclaude/commands/roadmap.md Skill` exits 0 after Epic 1 tasks complete; exits 1 on a test file missing Skill |
| LOC Estimate | 15-20 |
| Complexity | Low |
| Time Estimate | 20 min |
```

### Panel Consensus Structure (Copied from T01)

The panel consensus was organized into three tiers:

1. **Unanimous Agreements** -- Numbered list with bold statement + rationale
2. **Majority Agreements (3/4)** -- Numbered list with the dissenter's position explained
3. **Dissents** -- Numbered list identifying the dissenting panelist and their specific recommendation

### Key Pattern Observations

- The DVL evaluation uses a **single focal question** as the scoring criterion (detection effectiveness against the known failure)
- Scripts are classified in three implementation tiers: Lightweight (<30 LOC, <1hr), Medium (30-100 LOC, 1-4hrs), Full (>100 LOC, >4hrs)
- The panel can **override** brainstorm-phase priority recommendations (e.g., promoting `verify_pipeline_completeness.sh` from DEFER to KEEP)
- Conditional tasks use explicit triggers (e.g., "Implement only if Tasks 2.1-2.4 complete within 60% of Epic 2 time budget")

---

## 2. Spec-vs-Root-Cause Debate Pattern (T02)

### Debate Structure

Each of the 5 T02 debates followed a consistent structure:

1. **Header** -- Root cause ID, summary, combined score, sprint spec tasks addressing it
2. **FOR Position (Advocate)** -- 4-5 numbered arguments defending the spec's mitigation
3. **AGAINST Position (Challenger)** -- 4-5 numbered arguments attacking the spec's mitigation
4. **Cross-Examination** -- Advocate challenges Challenger's strongest argument, Challenger challenges Advocate's strongest argument (with responses)
5. **Scoring** -- 5 dimensions, each 0.0-1.0 with detailed rationale
6. **Verdict** -- One of: SUFFICIENT, NEEDS AMENDMENTS, INSUFFICIENT
7. **Recommended Amendments** -- Numbered list with effort estimates and impact ratings

### Five Scoring Dimensions

All T02 debates scored on these 5 dimensions:

| Dimension | Description |
|-----------|-------------|
| **Root cause coverage** | How completely does the spec address the identified root cause? |
| **Completeness** | Are there gaps in the spec's treatment? Missing scenarios, edge cases, contradictions? |
| **Feasibility** | Can the proposed changes be realistically implemented within sprint constraints? |
| **Blast radius** | What is the risk of unintended consequences from the proposed changes? |
| **Confidence** | How confident are we that the mitigation will work as intended? |

### Scoring Weights (from RC2 and RC5 debates)

The weighting scheme was made explicit in the RC2 and RC5 debates:

```
| Dimension | Weight |
|-----------|--------|
| Root Cause Coverage | 0.25 |
| Completeness | 0.25 |
| Feasibility | 0.20 |
| Blast Radius | 0.15 |
| Confidence | 0.15 |
```

Note: The RC1 debate used equal weights (0.20 each) instead. The RC4 debate used simple average (equal weights). This inconsistency across debates is worth noting for template standardization.

### Full Debate Template (Copied from T02-debate-RC1)

```markdown
# T02 Adversarial Debate: Does the Sprint Spec Effectively Mitigate RC1?

**RC1: Invocation Wiring Gap** -- [Root cause description with likelihood, impact, combined score]

**Debate question**: Does the sprint specification effectively mitigate RC1?

---

## FOR Position (Advocate)

[4-5 numbered arguments, each with a bold title and 1-3 paragraphs of evidence]

### Argument 1: [Title]
[Evidence and reasoning]

### Argument 2: [Title]
...

---

## AGAINST Position (Challenger)

[4-5 numbered arguments, each with a bold title and 1-3 paragraphs of evidence]

### Argument 1: [Title]
[Evidence and reasoning]

---

## CROSS-EXAMINATION

### Challenger to Advocate

**Question**: [Specific question targeting the Advocate's weakest point]

**Advocate's response**: [Direct response with concessions or rebuttals]

### Advocate to Challenger

**Question**: [Specific question targeting the Challenger's weakest point]

**Challenger's response**: [Direct response with concessions or rebuttals]

---

## SCORING

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **1. Root cause coverage** | 0.75 | [Detailed rationale] |
| **2. Completeness** | 0.70 | [Detailed rationale] |
| **3. Feasibility** | 0.85 | [Detailed rationale] |
| **4. Blast radius** | 0.80 | [Detailed rationale] |
| **5. Confidence** | 0.65 | [Detailed rationale] |

### Weighted Average
[Calculation shown]

---

## VERDICT: NEEDS AMENDMENTS

**Score: 0.750** -- [1-2 paragraph summary of why the verdict was reached]

### Recommended Amendments

| # | Amendment | Effort | Impact |
|---|-----------|--------|--------|
| A1 | [Description] | 1-2 hours | High |
| A2 | [Description] | 30 minutes | Medium |
...
```

### Full Debate Template (Copied from T02-debate-RC4 -- 3-round variant)

The RC4 debate used a more structured 3-round format:

```markdown
# Adversarial Debate: RC4 Return Contract Data Flow

**Debate Question**: Does the sprint specification effectively mitigate RC4?

**RC4 Summary**: [Root cause description with likelihood, impact, combined score]

**Sprint Spec Coverage**: [List of relevant tasks]

---

## Round 1: Opening Statements

### FOR Position (Advocate)
**1. [Statement].** [Evidence]
**2. [Statement].** [Evidence]
... [8 numbered points in the RC4 case]

### AGAINST Position (Challenger)
**1. [Statement].** [Evidence]
**2. [Statement].** [Evidence]
... [8 numbered points in the RC4 case]

---

## Round 2: Cross-Examination

### Advocate Cross-Examines Challenger
**Q1**: [Question]
**A1 (Challenger)**: [Response]
**Q2**: [Question]
**A2 (Challenger)**: [Response]
**Q3**: [Question]
**A3 (Challenger)**: [Response]

### Challenger Cross-Examines Advocate
**Q1**: [Question]
**A1 (Advocate)**: [Response]
...

---

## Round 3: Rebuttals

### Advocate Rebuttal
[Addresses the 3 strongest objections]

### Challenger Rebuttal
[Sharpens 3 remaining concerns]

---

## Scoring

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| **1. Root Cause Coverage** | 0.85 | [Rationale] |
...

**Weighted Average**: [calculation]

---

## Verdict: NEEDS AMENDMENTS
[Summary + Required Amendments + Acknowledged but Not Blocking items]
```

### Variation: Deferred Root Cause Debate (from T02-debate-RC3)

When a root cause was explicitly deferred from the sprint, the debate question changed to: "Is the combination of deferral + indirect coverage a SUFFICIENT strategy for RC3 in this sprint?"

The RC3 debate also used a different scoring format with adjudicated scores:

```
| Dimension | Weight | FOR Score | AGAINST Score | Adjudicated Score | Weighted | Rationale |
|-----------|--------|-----------|---------------|-------------------|----------|-----------|
| Root cause coverage | 0.25 | 0.40 | 0.70 | 0.58 | 0.145 | [Rationale explaining why adjudicated score falls between FOR and AGAINST] |
```

This format is notable because it makes the FOR/AGAINST disagreement visible and shows how the adjudicator resolved it.

---

## 3. Synthesis Pattern (T02-synthesis.md)

### Full Synthesis Template (Copied from T02-synthesis.md)

```markdown
# T02 Synthesis: Adversarial Debate Results -- Sprint-Spec vs Root Causes

> **Task**: T02.06 -- Aggregate debate results into coverage matrix and gap analysis
> **Generated**: [date]
> **Inputs**: T02-debate-RC1.md through T02-debate-RC5.md

## 1. Aggregate Coverage Matrix

| Dimension | RC1 (0.900) | RC2 (0.770) | RC3 (0.720) | RC4 (0.750) | RC5 (0.790) | Avg |
|-----------|-------------|-------------|-------------|-------------|-------------|-----|
| Root cause coverage | 0.75 | 0.82 | 0.45 | 0.85 | 0.65 | 0.704 |
| Completeness | 0.70 | 0.72 | 0.55 | 0.72 | 0.60 | 0.658 |
| Feasibility | 0.85 | 0.88 | 0.80 | 0.80 | 0.75 | 0.816 |
| Blast radius | 0.80 | 0.80 | 0.85 | 0.88 | 0.72 | 0.810 |
| Confidence | 0.65 | 0.78 | 0.63 | 0.75 | 0.68 | 0.698 |
| **Composite** | **0.750** | **0.798** | **0.651** | **0.800** | **0.680** | **0.736** |

**Problem-score weights** for overall effectiveness:

| RC | Problem Score | Debate Score | Weighted |
|----|--------------|-------------|----------|
| RC1 | 0.900 | 0.750 | 0.675 |
...

**Overall Spec Effectiveness Score**: Weighted by problem scores:
`(sum of weighted scores) / (sum of problem scores)` = **0.737**

## 2. Weakest Coverage Areas (Lowest Dimension Scores)

| Rank | Weakness | Score | RC | Issue |
|------|----------|-------|----|-------|
| 1 | RC3 Root cause coverage | 0.45 | RC3 | [Description] |
...

**Pattern**: [Observation about what dimensions are weakest]

## 3. Strongest Coverage Areas

| Rank | Strength | Score | RC | Why |
|------|----------|-------|----|-----|
| 1 | RC4 Blast radius | 0.88 | RC4 | [Description] |
...

**Pattern**: [Observation about what dimensions are strongest]

## 4. Overall Spec Effectiveness

**Score: 0.737** -- [Interpretation paragraph]

## 5. Specific Gaps Requiring Sprint-Spec Amendments

### Critical (must fix before implementation)

| # | Gap | Source | Effort | Fix |
|---|-----|--------|--------|-----|
| G1 | [Gap description] | [Which debate] | [Time estimate] | [Concrete fix] |

### Important (should fix before implementation)

| # | Gap | Source | Effort | Fix |
|---|-----|--------|--------|-----|

### Deferred (follow-up sprint)

| # | Gap | Source | Rationale for deferral |
|---|-----|--------|----------------------|

## 6. Recommendations Ranked by Urgency

| Priority | Action | Effort | Impact on Score |
|----------|--------|--------|----------------|
| 1 | Fix G1 | 15 min | +0.03 on RC4 |
...

**Total amendment effort**: ~4-5 hours
**Estimated post-amendment score**: ~0.82 (from 0.737)
```

### Key Synthesis Patterns

- **Three severity tiers**: Critical / Important / Deferred
- **Gap numbering**: G1-G15 continuous numbering across all debates
- **Impact quantification**: Each gap gets an estimated score improvement
- **Cross-debate pattern recognition**: "RC3 and RC5 are the weakest. Both were partially or fully deferred."
- **Weighted overall score**: Problem severity weights the debate scores, so high-severity root causes count more

---

## 4. Optimization Proposal Pattern (T03)

### Optimization Template (Copied from T03)

Each optimization followed this exact 7-field structure plus panel notes:

```markdown
## Optimization N: [Title]

### Current State
[Description of the status quo problem]

### Proposed Change
[Specific proposed modification]

### Time Savings
**X.XX hours** (~Y% of sprint)
Breakdown: [Itemized time savings with rationale per item]

### Effectiveness Impact
**0.XX** -- [Impact level label].
[Justification for why effectiveness is/isn't affected]

### Risk Assessment
**[Severity]**. [Description of primary risk]. Mitigation: [How risk is addressed].
[Secondary risks if applicable]

### Net Benefit Formula
`X.XX hrs * (1 - 0.XX) = Y.YY net benefit hours`

### Panel Notes
- **Efficiency Expert**: "[Quote]"
- **Quality Advocate**: "[Quote]"
- **Implementation Specialist**: "[Quote]"
- **Risk Analyst**: "[Quote]"

**Consensus**: [Unanimous/Majority] APPROVE [with caveats].
```

### Required Fields

1. **Current State** -- What exists now and why it is suboptimal
2. **Proposed Change** -- The specific modification
3. **Time Savings** -- Hours saved with percentage of sprint, itemized breakdown
4. **Effectiveness Impact** -- 0.0-1.0 scale with rationale
5. **Risk Assessment** -- Severity label + description + mitigation
6. **Net Benefit Formula** -- `time_saved * (1 - effectiveness_impact) = net_benefit`
7. **Panel Notes** -- Per-panelist quotes + consensus vote

### Constraints Applied (Copied from T03)

```
> **Target**: 5 optimizations, >20% total savings (>3.0 hours), each effectiveness_impact < 0.3, at least 2 with zero impact

| Constraint | Requirement | Actual | Status |
|-----------|------------|--------|--------|
| Max effectiveness impact per optimization | < 0.3 | Max is 0.15 | PASS |
| Total time savings > 20% of sprint | > 3.0 hrs (20% of ~15 hrs) | 5.75 hrs (38.3%) | PASS |
| At least 2 zero-effectiveness-impact optimizations | >= 2 | 2 (#1 and #2) | PASS |
| Optimizations independent of each other | All adoptable individually | Yes | PASS |
```

### Summary Table Format (Copied from T03)

```
| # | Optimization | Time Saved | Effectiveness Impact | Net Benefit | Zero Impact? |
|---|-------------|-----------|---------------------|-------------|--------------|
| 1 | Merge Tasks 1.3 + 1.4 + 2.2 into single task | 1.00 hrs | 0.00 | 1.000 hrs | Yes |
| 2 | Fold T02 amendments into task ACs | 0.75 hrs | 0.00 | 0.750 hrs | Yes |
| 3 | Simplify fallback from 5 steps to 3 | 1.25 hrs | 0.15 | 1.063 hrs | No |
| 4 | Defer G2 + G3 until after Task 0.0 gate | 2.00 hrs | 0.15 | 1.700 hrs | No |
| 5 | Embed Verification Tests 1, 3, 4 into task ACs | 0.75 hrs | 0.05 | 0.713 hrs | No |
| **Total** | | **5.75 hrs** | **Wtd avg: 0.07** | **5.225 hrs** | **2 of 5** |
```

### Combined Effect Table (Copied from T03)

```
| Metric | Before | After All 5 | Change |
|--------|--------|-------------|--------|
| Estimated sprint duration | ~15 hrs | ~9.25 hrs | -38.3% |
| Task count | 13 tasks (0.0 + 12) | 10 tasks | -23% |
| Risk register entries | 7 risks | 6 risks (R5 eliminated) | -14% |
| Verification tests (standalone) | 5 tests | 2 tests (+ 3 embedded in ACs) | Tests preserved, overhead reduced |
| DoD checkboxes | ~19 | ~14 | -26% |
| T02 amendment backlog | 11 gaps | 0 gaps (all integrated) | Eliminated as separate artifact |
```

---

## 5. Optimization Debate Pattern (T04)

### How T04 Debates Differ from T02 Debates

| Aspect | T02 (Root Cause Debates) | T04 (Optimization Debates) |
|--------|--------------------------|---------------------------|
| **Question** | "Does the spec effectively mitigate RC{N}?" | "Should Optimization {N} be adopted?" |
| **Stakes** | Spec correctness and completeness | Time/quality tradeoff |
| **FOR position** | Defends the spec's treatment | Argues for adopting the optimization |
| **AGAINST position** | Attacks the spec's treatment | Argues against adopting the optimization |
| **Scoring dimensions** | Root cause coverage, Completeness, Feasibility, Blast radius, Confidence | Time savings, Effectiveness preservation, Feasibility, Risk, Net benefit |
| **Verdict options** | SUFFICIENT / NEEDS AMENDMENTS / INSUFFICIENT | ADOPT / ADOPT-WITH-MODIFICATIONS / REJECT |
| **Outcome** | Required amendments | Required modifications to the optimization |

### Full Optimization Debate Template (Copied from T04-debate-opt1)

```markdown
# T04: Adversarial Debate -- Optimization N

> **Subject**: [Optimization title]
> **Date**: [date]
> **Format**: Structured adversarial debate with cross-examination and dimensional scoring
> **Inputs**: T03-optimizations.md (Optimization N), sprint-spec.md, ranked-root-causes.md

---

## Optimization N Summary

**Current state**: [What the optimization changes]
**Proposed change**: [The specific proposal]
**Claimed savings**: X.X hours (~Y% of sprint), with Z.Z effectiveness impact.

---

## FOR Position: Optimization N Should Be Adopted

### Argument 1: [Title]
[Evidence and reasoning]

### Argument 2: [Title]
[Evidence and reasoning]

### Argument 3: [Title]
[Evidence and reasoning]

### Argument 4: [Title]
[Evidence and reasoning]

---

## AGAINST Position: Optimization N Should Not Be Adopted

### Argument 1: [Title]
[Evidence and reasoning]

### Argument 2: [Title]
[Evidence and reasoning]

### Argument 3: [Title]
[Evidence and reasoning]

### Argument 4: [Title]
[Evidence and reasoning]

---

## Cross-Examination

### FOR challenges AGAINST's strongest argument ([identify which]):
**Question**: [Specific challenge]

### AGAINST challenges FOR's strongest argument ([identify which]):
**Question**: [Specific challenge]

---

## Rebuttals

### FOR responds to AGAINST's cross-examination:
[Rebuttal]

### AGAINST responds to FOR's cross-examination:
[Rebuttal]

---

## Dimensional Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| time_savings | 0.XX | [Rationale -- validates or adjusts claimed savings] |
| effectiveness_preservation | 0.XX | [Rationale -- all functional requirements preserved?] |
| feasibility | 0.XX | [Rationale -- can the optimization be cleanly applied?] |
| risk (higher = lower risk) | 0.XX | [Rationale -- downside risk assessment] |
| net_benefit | 0.XX | [Rationale -- overall benefit accounting for all dimensions] |
| **Weighted Average** | **0.XX** | |

---

## Recommendation: **[ADOPT / ADOPT-WITH-MODIFICATIONS / REJECT]**

### Rationale
[1-2 paragraphs explaining the recommendation]

### Required Modifications
1. [Modification with implementation detail]
2. [Modification with implementation detail]
3. [Modification with implementation detail]
```

### Full Optimization Debate Template (Copied from T04-debate-opt4 -- Contentious Variant)

The Opt4 debate demonstrated how a contentious optimization (lowest score: 0.64) requires more detailed cross-examination:

```markdown
## FOR Position: Optimization 4 Should Be Adopted

### Argument 1: The conditional gate is structurally sound
...
### Argument 5: G3 deferral is uncontroversial even the dissenter accepts it
[Note: 5 arguments instead of the typical 4, reflecting the need for more defense]

---

## AGAINST Position: Optimization 4 Is Risky and Undermines Sprint Purpose

### Argument 1: This sprint exists to fix silent failures -- deferring fallback testing creates a new one
...
### Argument 5: The time savings are inflated by the expected-value framing
[Note: Also 5 arguments, matching the expanded FOR]

---

## CROSS-EXAMINATION

### FOR challenges AGAINST's strongest argument (Argument 1: silent failure recurrence)

**FOR**: "[Extended quote with specific technical rebuttal]"

**AGAINST responds**: "[Extended counter-rebuttal]"

### AGAINST challenges FOR's strongest argument (Argument 3: largest time savings)

**AGAINST**: "[Extended quote with specific technical rebuttal]"

**FOR responds**: "[Extended counter-rebuttal]"

---

## SCORING
[Same 5 dimensions]

---

## RECOMMENDATION: Adopt-With-Modifications

### Exact Modifications

**1. Defer G3 unconditionally (accepted by all parties)**
- [Detail]
- **Savings**: 0.5 hours

**2. Replace G2 (full fallback validation test) with G2-lite (fallback smoke test)**
- [Detailed specification of the smoke test]
- **Does NOT test**: [Explicit scope exclusions]
- **Rationale**: [Why this compromise works]

**3. Gate G2-lite on Task 0.0 outcome (conditional)**
- If primary path is **viable**: [behavior]
- If primary path is **blocked**: [behavior]

### Modified Time Savings

| Scenario | Probability | G3 | G2 | Total Saved vs. Original |
|----------|------------|-----|-----|--------------------------|
| Primary viable | 58% | Deferred | G2-lite | ~1.5 hrs |
| Primary blocked | 42% | Implemented | Full G2 | 0 hrs |
| **Expected value** | | | | **0.87 hrs** |

### Sprint Impact

| Metric | Full Adoption | Modified Adoption | Full Rejection |
|--------|--------------|-------------------|----------------|
| Expected time saved | 1.3 hrs | 0.87 hrs | 0 hrs |
| Fallback test coverage | None | Smoke test | Full test |
| Silent failure risk | Moderate | Low | Minimal |
| Alignment with sprint purpose | Weak | Acceptable | Strong |
```

---

## 6. Final Synthesis Pattern (T04-synthesis.md)

### Full Synthesis Template (Copied from T04-synthesis.md)

```markdown
# T04 Synthesis: Final Optimization Verdicts

> **Task**: T04.06 -- Synthesize 5 adversarial debate results on optimization proposals
> **Generated**: [date]
> **Inputs**: T04-debate-opt1.md through T04-debate-opt5.md

## 1. Verdict Table

| Opt# | Name | Debate Score | Recommendation | Time Saved | Effectiveness Impact |
|------|------|-------------|----------------|------------|---------------------|
| 1 | [Name] | 0.XX | [ADOPT/ADOPT-WITH-MODS/REJECT] | X.XX hrs (realistic: ~Y.YY) | 0.XX |
...

## 2. Adopted Optimizations with Required Modifications

### Optimization N: [Name] (Score: 0.XX)

**Original**: [What it was before]
**Adopted as**: [What it became]

**Required modifications**:
- [Modification 1]
- [Modification 2]
...

**Revised savings**: ~X.XX hrs (down from Y.YY due to [reason])

## 3. Rejected Optimizations
[List or "None"]

## 4. Projected Total Time Savings

| Opt# | Original Savings | Revised Savings | Modification Cost | Net Savings |
|------|-----------------|----------------|-------------------|-------------|
...
| **Total** | **X.XX hrs** | **Y.YY hrs** | **~Z hr** | **W.WW hrs** |

**Revised total**: Y.YY hrs = **XX%** of estimated sprint

## 5. Projected Effectiveness Preservation

| Opt# | Impact Score | Modification Mitigation | Residual Impact |
|------|-------------|------------------------|----------------|
...

**Projected residual effectiveness impact**: ~0.XX weighted average

## 6. FINAL RECOMMENDATION: Ordered Adoption List

| Priority | Optimization | Adopt? | Savings | Confidence |
|----------|-------------|--------|---------|------------|
| 1 | [Name] | YES (with mods) | X.XX hrs | 0.XX |
...

**Adoption order rationale**: [Explanation of priority ordering]
**Implementation guidance**: [Practical notes on order of application]
```

### Key Synthesis Patterns

- **Realistic vs. claimed savings**: Every optimization's claimed savings were adjusted downward based on debate findings
- **Modification extraction**: Each debate's modifications are extracted and compiled
- **Residual impact calculation**: After modifications, the actual effectiveness impact is recalculated
- **Confidence-ordered adoption**: Optimizations are adopted in order of debate score (highest confidence first)
- **Conditional optimizations flagged**: Opt 4 is clearly marked as conditional on Task 0.0

---

## 7. Prompts Used

### T01: DVL Evaluation Prompt (Inferred from Output)

The T01 evaluation was framed with this context and instruction:

```
Panel: Specification Expert, Testing Expert, DevOps Engineer, Architect
Input: DVL-BRAINSTORM.md (10 scripts, 3 tiers), sprint-spec.md (3 epics, 12 tasks)
Context: The original sc:roadmap adversarial pipeline failure was SILENT -- it produced output
that looked reasonable but bypassed 80% of the pipeline. The core evaluation criterion is:
would this script have CAUGHT that failure?

Tasks:
1. Score each script's detection effectiveness (0.0-1.0) against the specific original failure
2. Rank scripts by detection effectiveness
3. Classify each as Lightweight (<30 LOC, <1hr), Medium (30-100 LOC, 1-4hrs), or Full (>100 LOC, >4hrs)
4. Propose sprint-spec additions for top-ranked scripts
5. Document panel consensus with unanimous agreements, majority agreements, and dissents
```

### T02: Root Cause Debate Prompt (Inferred from Output)

```
Debate Question: Does the sprint specification effectively mitigate RC{N}?

RC{N} Summary: [Root cause name] -- [Description with likelihood, impact, combined score]

Sprint Spec Tasks Addressing RC{N}: [List of relevant tasks]

Structure:
- Write FOR Position (Advocate): 4-5 numbered arguments defending the spec's mitigation
- Write AGAINST Position (Challenger): 4-5 numbered arguments attacking the spec's mitigation
- Conduct Cross-Examination: Each side challenges the other's strongest argument
- Score on 5 dimensions (0.0-1.0): Root cause coverage, Completeness, Feasibility, Blast radius, Confidence
- Deliver Verdict: SUFFICIENT (>=0.85), NEEDS AMENDMENTS (0.60-0.84), or INSUFFICIENT (<0.60)
- List Required Amendments with effort estimates and impact ratings
```

### T02: Synthesis Prompt (Inferred from Output)

```
Task: T02.06 -- Aggregate debate results into coverage matrix and gap analysis
Inputs: T02-debate-RC1.md through T02-debate-RC5.md

Produce:
1. Aggregate Coverage Matrix: All dimensions x all root causes, with composite scores
2. Problem-score-weighted overall effectiveness score
3. Weakest Coverage Areas (lowest dimension scores, ranked)
4. Strongest Coverage Areas (highest dimension scores, ranked)
5. Overall Spec Effectiveness interpretation
6. Specific Gaps Requiring Amendments: categorized as Critical / Important / Deferred
7. Recommendations Ranked by Urgency: effort, impact on score
8. Total amendment effort estimate and projected post-amendment score
```

### T03: Optimization Proposal Prompt (Inferred from Output)

```
Panel: Efficiency Expert, Quality Advocate, Implementation Specialist, Risk Analyst
Input: sprint-spec.md, T02-synthesis.md, T01-dvl-evaluation.md, ranked-root-causes.md
Baseline Sprint Estimate: ~15 hours
Target: 5 optimizations, >20% total savings (>3.0 hours), each effectiveness_impact < 0.3,
at least 2 with zero impact

For each optimization, produce:
1. Current State: description of the suboptimal status quo
2. Proposed Change: the specific modification
3. Time Savings: hours with itemized breakdown
4. Effectiveness Impact: 0.0-1.0 with rationale
5. Risk Assessment: severity + mitigation
6. Net Benefit Formula: time_saved * (1 - effectiveness_impact)
7. Panel Notes: per-panelist quotes + consensus vote

Summary: verification that all constraints are met, combined effect table
```

### T04: Optimization Debate Prompt (Inferred from Output)

```
Subject: [Optimization title from T03]
Format: Structured adversarial debate with cross-examination and dimensional scoring
Inputs: T03-optimizations.md (Optimization N), sprint-spec.md, ranked-root-causes.md

Structure:
- Optimization Summary: current state, proposed change, claimed savings/impact
- FOR Position: 4+ arguments for adoption
- AGAINST Position: 4+ arguments against adoption
- Cross-Examination: FOR challenges AGAINST's strongest argument, AGAINST challenges FOR's strongest
- Rebuttals (optional, used in some debates)
- Dimensional Scoring (0.0-1.0): time_savings, effectiveness_preservation, feasibility, risk, net_benefit
- Recommendation: ADOPT / ADOPT-WITH-MODIFICATIONS / REJECT
- Required Modifications: specific changes to the optimization if adopted
```

### T04: Synthesis Prompt (Inferred from Output)

```
Task: T04.06 -- Synthesize 5 adversarial debate results on optimization proposals
Inputs: T04-debate-opt1.md through T04-debate-opt5.md

Produce:
1. Verdict Table: all optimizations with debate scores, recommendations, savings, impact
2. Adopted Optimizations with Required Modifications: per-optimization detail
3. Rejected Optimizations (if any)
4. Projected Total Time Savings: original vs revised vs modification cost vs net
5. Projected Effectiveness Preservation: impact vs mitigation vs residual
6. FINAL RECOMMENDATION: confidence-ordered adoption list with implementation guidance
```

---

## 8. Scoring Dimensions & Weights

### T01: DVL Evaluation

| Metric | Scale | Description |
|--------|-------|-------------|
| Detection Effectiveness | 0.0-1.0 | "If the silent pipeline bypass happened again, would this script detect it?" |

Single dimension only. No weighting needed.

### T02: Spec-vs-Root-Cause Debates

| Dimension | Weight (RC2/RC3/RC5) | Weight (RC1/RC4) | Description |
|-----------|---------------------|-------------------|-------------|
| Root cause coverage | 0.25 | 0.20 | Completeness of root cause address |
| Completeness | 0.25 | 0.20 | Gaps, edge cases, contradictions |
| Feasibility | 0.20 | 0.20 | Implementability within sprint |
| Blast radius | 0.15 | 0.20 | Risk of unintended consequences |
| Confidence | 0.15 | 0.20 | Certainty that mitigation works |

**Verdict thresholds** (from RC3 debate):
- SUFFICIENT: >= 0.85
- NEEDS AMENDMENTS: 0.60 - 0.84
- INSUFFICIENT: < 0.60

Note: RC3 also mentions a 0.70 threshold for "SUFFICIENT" vs "below threshold", suggesting the thresholds may have been calibrated differently across debates. For template standardization, the 0.85/0.60 thresholds should be made explicit.

### T03: Optimization Proposals

| Metric | Constraint | Description |
|--------|-----------|-------------|
| Time Savings | Reported in hours + % of sprint | Must total >20% of sprint |
| Effectiveness Impact | 0.0-1.0, max 0.3 per optimization | Lower is better |
| Net Benefit | `time_saved * (1 - effectiveness_impact)` | Composite metric |

### T04: Optimization Debates

| Dimension | Scale | Description |
|-----------|-------|-------------|
| time_savings | 0.0-1.0 | Does this actually save the claimed time? |
| effectiveness_preservation | 0.0-1.0 | Does this preserve spec effectiveness? (higher = better preserved) |
| feasibility | 0.0-1.0 | Can this optimization be cleanly applied? |
| risk | 0.0-1.0 | What is the downside risk? (higher = lower risk) |
| net_benefit | 0.0-1.0 | Overall benefit accounting for all dimensions |

**Composite**: Simple average of all 5 dimensions.

**Verdict thresholds** (inferred from T04 outcomes -- all received ADOPT-WITH-MODIFICATIONS):
- ADOPT: >= 0.85 (none achieved this)
- ADOPT-WITH-MODIFICATIONS: 0.60 - 0.84 (all 5 fell here)
- REJECT: < 0.60 (none fell here)

### T02 Synthesis: Overall Effectiveness

```
Overall Spec Effectiveness = sum(problem_score_i * debate_score_i) / sum(problem_score_i)
```

This weights debate scores by the severity of their root cause, so high-severity root causes with low debate scores pull the overall score down more than low-severity ones.

---

## 9. Adaptation for Improvement Mode

### Problem-Driven vs Improvement-Driven: Where They Differ

In the original (problem-driven) workflow:
- T02 asks: "Does the spec fix root cause X?"
- The FOR/AGAINST arguments reference a specific failure with known symptoms, likelihood, and impact
- The scoring dimensions reference "root cause coverage"

In improvement mode (no root causes):
- T02 would ask: "Does the spec adequately address weakness X?"
- Arguments reference an identified weakness, gap, or opportunity (not a failure)
- Scoring dimensions reference "weakness coverage" or "opportunity coverage"

### Parameterized Template Design

The refinement templates should use a **context variable** that controls terminology:

```yaml
# Context variable set at workflow start
refinement_mode: "problem" | "improvement"

# Template substitutions
if refinement_mode == "problem":
  validation_subject: "root cause"
  validation_subjects: "root causes"
  validation_question: "Does the spec effectively mitigate {subject_id}?"
  coverage_dimension: "Root cause coverage"
  for_framing: "defending the spec's mitigation"
  against_framing: "attacking the spec's mitigation"
  verdict_meaning: "mitigation effectiveness"
  subject_score_field: "combined_score"  # from ranked-root-causes

if refinement_mode == "improvement":
  validation_subject: "weakness"
  validation_subjects: "weaknesses"
  validation_question: "Does the spec adequately address {subject_id}?"
  coverage_dimension: "Weakness coverage"
  for_framing: "defending the spec's treatment of this weakness"
  against_framing: "challenging whether the spec's treatment is sufficient"
  verdict_meaning: "improvement effectiveness"
  subject_score_field: "priority_score"  # from weakness ranking
```

### Specific Template Changes

**T02 Debate Header**:
- Problem mode: `RC1: Invocation Wiring Gap -- [description]. Likelihood: 0.90, Impact: 0.90, Combined Score: 0.900.`
- Improvement mode: `W1: Insufficient Error Handling -- [description]. Priority: 0.85, Current Gap: 0.70, Improvement Score: 0.850.`

**T02 Scoring Dimension 1**:
- Problem mode: "Root cause coverage -- How completely does the spec address the identified root cause?"
- Improvement mode: "Weakness coverage -- How completely does the spec address the identified weakness?"

**T02 Synthesis Overall Score**:
- Problem mode: `sum(problem_score * debate_score) / sum(problem_score)`
- Improvement mode: `sum(priority_score * debate_score) / sum(priority_score)`

**T03/T04 are mode-independent**: Optimization proposals and their debates operate on the draft spec regardless of whether it was generated from root causes or weaknesses. No changes needed.

### What Stays the Same

- The 5-dimension scoring framework (with renamed dimension 1)
- The FOR/AGAINST/CROSS-EXAMINATION/SCORING/VERDICT structure
- The synthesis aggregation pattern (matrix, gaps, recommendations)
- The optimization proposal format (7 fields + panel)
- The optimization debate format (5 dimensions)
- The synthesis format (verdict table, adoption list)
- All verdict thresholds

---

## 10. Verification Agent Pattern

### Overview

When running non-interactively, each refinement phase needs an automated verification agent that checks whether the output meets acceptance criteria. Based on the scoring rubrics and acceptance criteria found in T01-T04, here are the proposed checks.

### Phase T01: DVL Evaluation Verification

**Input**: T01 evaluation document
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| All scripts scored | Parse table for Detection Effectiveness column | Every script has a score in [0.0, 1.0] |
| Ranking consistency | Compare ranked list to score table | Rank order matches score descending order |
| Classification completeness | Parse implementation tables | Every script appears in exactly one tier (Lightweight/Medium/Full) |
| LOC estimates present | Parse each script entry | Every script has LOC range and time estimate |
| Panel consensus present | Check for "Unanimous" / "Majority" / "Dissent" sections | At least one consensus item exists |
| Sprint-spec refactor present | Check for task proposal tables | At least one concrete task proposal with all 8 fields |

### Phase T02: Spec-vs-Subject Debate Verification

**Input**: One T02 debate document
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| Subject identified | Parse header | Subject ID, description, and score present |
| FOR position present | Parse section | At least 3 numbered arguments |
| AGAINST position present | Parse section | At least 3 numbered arguments |
| Cross-examination present | Parse section | At least 1 challenge from each side |
| All 5 dimensions scored | Parse scoring table | 5 rows, each with score in [0.0, 1.0] and non-empty rationale |
| Scores internally consistent | Arithmetic check | Weighted average matches claimed composite within 0.02 |
| Verdict present | Parse verdict section | One of SUFFICIENT / NEEDS AMENDMENTS / INSUFFICIENT |
| Verdict consistent with score | Threshold check | Score >= 0.85 -> SUFFICIENT, 0.60-0.84 -> NEEDS AMENDMENTS, < 0.60 -> INSUFFICIENT |
| Amendments listed if needed | Parse amendments section | If NEEDS AMENDMENTS, at least 1 amendment with effort estimate |

### Phase T02 Synthesis Verification

**Input**: T02-synthesis.md + all T02 debate files
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| All debates represented | Cross-reference | Every debate file's composite score appears in the matrix |
| Matrix arithmetic correct | Recalculate | All averages and weighted scores match within 0.01 |
| Overall effectiveness calculated | Parse | Formula shown and result present |
| Gaps extracted from all debates | Cross-reference | Every amendment from every debate appears as a gap (G1-GN) |
| Gap severity classification | Parse | Every gap classified as Critical / Important / Deferred |
| Recommendations ordered | Check priority numbers | Ordered by effort/impact ratio |
| Post-amendment score estimated | Parse | Numeric estimate present |

### Phase T03: Optimization Proposal Verification

**Input**: T03 optimization document
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| All 7 fields present per optimization | Parse each optimization | Current State, Proposed Change, Time Savings, Effectiveness Impact, Risk Assessment, Net Benefit Formula, Panel Notes |
| Net benefit formula correct | Arithmetic | `time * (1 - impact)` matches claimed net benefit within 0.01 |
| All constraints met | Parse constraint table | Max impact < 0.3, total savings > 20%, at least 2 zero-impact |
| Panel consensus recorded | Parse | Each optimization has a vote (Unanimous/Majority APPROVE or REJECT) |
| Summary table complete | Parse | All optimizations appear with all columns populated |
| Independence verified | Parse | Independence note present confirming optimizations can be adopted individually |

### Phase T04: Optimization Debate Verification

**Input**: One T04 debate document
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| Optimization summary present | Parse header | Subject, claimed savings, claimed impact stated |
| FOR position present | Parse section | At least 3 numbered arguments |
| AGAINST position present | Parse section | At least 3 numbered arguments |
| Cross-examination present | Parse section | At least 1 challenge from each side |
| All 5 dimensions scored | Parse scoring table | 5 rows (time_savings, effectiveness_preservation, feasibility, risk, net_benefit) |
| Composite calculated correctly | Arithmetic | Simple average of 5 scores matches within 0.02 |
| Recommendation present | Parse | One of ADOPT / ADOPT-WITH-MODIFICATIONS / REJECT |
| Modifications listed if applicable | Parse | If ADOPT-WITH-MODIFICATIONS, at least 1 modification specified |

### Phase T04 Synthesis Verification

**Input**: T04-synthesis.md + all T04 debate files
**Checks**:

| Check | Method | Pass Condition |
|-------|--------|---------------|
| All debates represented | Cross-reference | Every debate file's composite score appears in verdict table |
| Verdict table complete | Parse | All optimizations have: name, score, recommendation, savings, impact |
| Revised savings calculated | Arithmetic | Original - modification cost = revised, total calculated correctly |
| Effectiveness preservation calculated | Parse | Residual impact computed for each optimization |
| Adoption order justified | Parse | Rationale for ordering present, typically by debate score |
| Implementation guidance present | Parse | At least 1 sentence on application order |

### Verification Agent Implementation Notes

1. **All checks are objective and automatable** -- they involve parsing, arithmetic, cross-referencing, and threshold comparison. No subjective judgment required.
2. **Checks should run AFTER each phase completes** before the next phase begins. This prevents garbage-in-garbage-out across phases.
3. **Failed checks should block progression** in strict mode. In standard mode, they should emit warnings.
4. **The verification agent itself should produce a brief report**: pass/fail per check, total pass rate, and blocking issues if any.

---

## Summary of the Refinement Workflow

The refinement stage consists of 4 phases that can be applied to any draft spec, regardless of whether it was produced from root-cause analysis (problem mode) or weakness analysis (improvement mode):

```
Draft Spec
    |
    v
[T01] DVL Evaluation (optional)
    Expert panel scores verification scripts against known failure modes
    Output: ranked scripts, sprint-spec additions, panel consensus
    |
    v
[T02] Spec-vs-Subject Debates (parallel, one per root cause or weakness)
    Adversarial FOR/AGAINST debate on each subject
    Output: 5-dimension scores, verdicts, required amendments
    |
    v
[T02-synthesis] Debate Synthesis
    Aggregates all debate scores into coverage matrix
    Output: overall effectiveness score, gap list (G1-GN), urgency-ranked recommendations
    |
    v
[T03] Optimization Proposals
    Expert panel proposes 5+ optimizations with constraints
    Output: optimization specs with time/effectiveness/risk analysis
    |
    v
[T04] Optimization Debates (parallel, one per optimization)
    Adversarial FOR/AGAINST debate on each optimization
    Output: 5-dimension scores, ADOPT/MODIFY/REJECT verdicts
    |
    v
[T04-synthesis] Optimization Synthesis
    Aggregates verdicts into final adoption list
    Output: ordered adoption list with revised savings and modifications
    |
    v
Refined Spec (ready for implementation)
```

The T01 (DVL evaluation) phase is specific to problem-driven workflows where verification scripts are relevant. In improvement mode, it can be replaced by a different evaluation step or omitted.

The T02-T04 phases are fully reusable across both modes with the parameterization described in Section 9.

---

*Analysis generated 2026-02-23 for the spec-workshop backlog.*
*Source: 14 workflow output files from the v2.01-Roadmap-v3 SpecDev process.*
