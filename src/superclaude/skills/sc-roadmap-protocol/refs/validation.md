# Validation Reference

Reference document for Wave 4: Validation (Multi-Agent). Contains the quality-engineer agent prompt, self-review agent prompt (4-question protocol), score aggregation formula, and decision thresholds.

---

## Quality-Engineer Agent Prompt

Dispatch this prompt to a `quality-engineer` sub-agent. The agent runs in **read-only** mode — it does not modify any artifacts.

### Prompt

```
You are a quality-engineer validation agent for sc:roadmap. Your task is to validate the generated roadmap artifacts against the source specification.

INPUT FILES:
- Source spec: {spec_path}
- roadmap.md: {roadmap_path}
- extraction.md: {extraction_path}
- test-strategy.md: {test_strategy_path}

Perform the following validation checks and score each dimension 0-100:

## 1. COMPLETENESS (weight: 0.35)
- Every FR and NFR in extraction.md has a corresponding deliverable in at least one milestone in roadmap.md
- Every risk in extraction.md appears in the roadmap.md Risk Register
- Every success criterion in extraction.md is traceable to at least one milestone
- No orphaned deliverables (deliverables not traceable to any extracted requirement)
- Score: (items_covered / total_items) * 100

## 2. CONSISTENCY (weight: 0.30)
- Milestone IDs follow the M{digit} schema consistently
- Deliverable IDs follow the D{milestone}.{seq} schema
- Risk IDs follow the R-{3digits} schema
- Dependency references between milestones are valid (no references to non-existent milestones)
- Frontmatter values match body content (e.g., milestone_count in frontmatter matches actual milestone count)
- Domain distribution in frontmatter matches extraction.md domain distribution
- Complexity score in frontmatter matches extraction.md complexity score
- Score: (consistent_items / total_checked_items) * 100

## 3. TRACEABILITY (weight: 0.20)
- Every milestone traces back to at least one requirement
- Every deliverable has acceptance criteria
- Source line references in extraction.md are valid (not fabricated)
- Decision Summary entries cite specific data points (not subjective justifications)
- Score: (traceable_items / total_items) * 100

## 4. TEST STRATEGY VALIDATION (weight: 0.15)
- Interleave ratio matches complexity class:
  - LOW complexity → 1:3 ratio
  - MEDIUM complexity → 1:2 ratio
  - HIGH complexity → 1:1 ratio
- Every validation milestone references a real work milestone from roadmap.md
- Continuous parallel validation philosophy is explicitly encoded (not generic boilerplate)
- Stop-and-fix thresholds are defined for each severity level (Critical, Major, Minor, Info)
- Issue classification table is present with clear actions per severity
- Score: (criteria_met / total_criteria) * 100

OUTPUT FORMAT:
Return a structured validation report:
{
  "completeness": {"score": <0-100>, "issues": [<list of specific issues>]},
  "consistency": {"score": <0-100>, "issues": [<list of specific issues>]},
  "traceability": {"score": <0-100>, "issues": [<list of specific issues>]},
  "test_strategy": {"score": <0-100>, "issues": [<list of specific issues>]},
  "weighted_score": <computed>,
  "recommendation": "<PASS|REVISE|REJECT>",
  "improvement_recommendations": [<specific, actionable improvements if REVISE>]
}
```

---

## Self-Review Agent Prompt

Dispatch this prompt to a `self-review` sub-agent. The agent runs in **read-only** mode.

### 4-Question Validation Protocol

```
You are a self-review validation agent for sc:roadmap. Answer each question with evidence from the artifacts.

INPUT FILES:
- Source spec: {spec_path}
- roadmap.md: {roadmap_path}
- extraction.md: {extraction_path}
- test-strategy.md: {test_strategy_path}

Answer these 4 questions. For each, provide a score (0-100) and evidence.

## Question 1: Does the roadmap faithfully represent the spec? (weight: 0.30)
- Are all spec requirements represented in the roadmap?
- Does the milestone ordering respect the spec's implicit or explicit priorities?
- Are any spec requirements distorted, merged incorrectly, or misinterpreted?
- Score: percentage of requirements faithfully represented

## Question 2: Are the milestones achievable and well-ordered? (weight: 0.25)
- Does each milestone have clear, measurable deliverables?
- Are dependencies correctly identified (no circular dependencies, no missing prerequisites)?
- Is the milestone ordering logical (foundations before features, features before integration)?
- Score: percentage of milestones with correct ordering and achievable scope

## Question 3: Does the risk assessment match the actual risks? (weight: 0.25)
- Are high-impact risks identified with appropriate mitigations?
- Are there obvious risks NOT in the register (blind spots)?
- Do risk probabilities and impacts seem calibrated (not all "Low" or all "High")?
- Score: (identified_risks / estimated_total_risks) * calibration_quality

## Question 4: Is the test strategy actionable? (weight: 0.20)
- Can a developer follow the test strategy to validate each milestone?
- Are stop-and-fix criteria specific enough to trigger action?
- Does the validation milestone placement make sense given the roadmap structure?
- Score: percentage of validation milestones with actionable criteria

OUTPUT FORMAT:
{
  "q1_faithfulness": {"score": <0-100>, "evidence": "<specific examples>"},
  "q2_achievability": {"score": <0-100>, "evidence": "<specific examples>"},
  "q3_risk_quality": {"score": <0-100>, "evidence": "<specific examples>"},
  "q4_test_actionability": {"score": <0-100>, "evidence": "<specific examples>"},
  "weighted_score": <computed>,
  "recommendation": "<PASS|REVISE|REJECT>",
  "improvement_recommendations": [<specific, actionable improvements if REVISE>]
}
```

---

## Score Aggregation

Both agents run in **parallel** (they are independent read-only validators). Their scores are aggregated into a final validation score.

### Aggregation Formula

```
final_score = (quality_engineer_weighted_score * 0.55) + (self_review_weighted_score * 0.45)
```

**Agent weights**: Quality-engineer (0.55) is weighted slightly higher because it performs structural validation. Self-review (0.45) provides holistic assessment.

### Per-Agent Weighted Score Calculation

**Quality-engineer**:
```
weighted_score = (completeness * 0.35) + (consistency * 0.30) + (traceability * 0.20) + (test_strategy * 0.15)
```

**Self-review**:
```
weighted_score = (q1_faithfulness * 0.30) + (q2_achievability * 0.25) + (q3_risk_quality * 0.25) + (q4_test_actionability * 0.20)
```

---

## Decision Thresholds

| Score Range | Status | Action |
|-------------|--------|--------|
| >= 85% | PASS | Accept roadmap. Write `validation_status: PASS` and `validation_score: <score>` to roadmap.md frontmatter |
| 70-84% | REVISE | Enter REVISE loop (see below) |
| < 70% | REJECT | Reject roadmap. Write `validation_status: REJECT` and `validation_score: <score>`. Report all issues to user |

### Adversarial Mode Additional Checks

When adversarial mode was used (multi-spec or multi-roadmap):
- Missing adversarial artifacts (no adversarial/ directory when adversarial mode was active) → automatic REJECT
- Missing convergence score in frontmatter → automatic REVISE (regardless of score)

---

## REVISE Loop

When the final score is 70-84% (REVISE), execute the following loop:

### Iteration 1

1. Collect `improvement_recommendations` from both agents
2. Combine into a prioritized improvement list (highest-impact issues first)
3. Re-run Wave 3 (Generation) with the improvement list as additional input context
4. Re-run Wave 4 (Validation) on the regenerated artifacts
5. If new score >= 85%: PASS. If 70-84%: proceed to Iteration 2. If < 70%: REJECT

### Iteration 2

1. Collect new `improvement_recommendations`
2. Re-run Wave 3 with both iteration 1 and iteration 2 recommendations
3. Re-run Wave 4
4. If new score >= 85%: PASS. If still 70-84%: accept with `validation_status: PASS_WITH_WARNINGS`. If < 70%: REJECT

### Maximum Iterations

**Hard limit**: 2 iterations. After 2 REVISE iterations without reaching PASS:
- Set `validation_status: PASS_WITH_WARNINGS`
- Set `validation_score: <final_score>`
- Append a warnings section to roadmap.md listing unresolved issues
- Report to user that roadmap passed with warnings and recommend manual review

### No-Validate Behavior

When `--no-validate` flag is set:
- Skip Wave 4 entirely
- Set `validation_status: SKIPPED`
- Set `validation_score: 0.0`
- No agents are dispatched

---

*Reference document for sc:roadmap v2.0.0 — loaded on-demand during Wave 4*
