# rf:crossLLM Scope-Corrected Analysis

**Date**: 2026-01-02
**Purpose**: Re-analyze review findings to separate in-scope improvements from out-of-scope additions

---

## rf:crossLLM Command Purpose

> "rf-crossLLM is for upgrading LLM-generated content (answers, proposals, prompts, markdown, scripts). It is NOT for codebase/code review work."

The command improves **existing content quality** through multi-model debate and QAG evaluation. It does **not** add new features, enforce prompt engineering principles, or create framework compliance systems.

---

## QAG Rubric Analysis

The existing rubric evaluates 6 dimensions with specific binary questions:

| Dimension | Key Questions Relevant to Review Findings |
|-----------|------------------------------------------|
| Q3.1 | "Is the content logically organized?" |
| Q3.3 | "Is formatting consistent and appropriate?" |
| Q4.2 | "Are next steps or implementation paths clear?" |
| Q5.1 | "Are critical assumptions explicitly stated?" |
| Q5.3 | "Are edge cases or limitations acknowledged?" |

---

## Weakness Classification

All identified weaknesses are **IN-SCOPE** for rf:crossLLM. When the content being upgraded is a prompt, missing controls that affect output quality are quality issues in the prompt itself.

### Roadmap Review - Prompt A Weaknesses (7 items, all IN-SCOPE)

| Weakness | QAG Coverage | Expected Fix |
|----------|--------------|--------------|
| Missing safety section | Q2.3 significant gaps | Add input handling guidance |
| No fabrication controls | Q2.3 gaps, Q5.3 edge cases | Add fabrication prevention |
| XML-like tags | Q3.3 appropriate format | Convert to standard markdown |
| Embedded sections | Q3.1 organization | Restructure hierarchy |
| No unknown handling | Q5.3 edge cases | Add TBD/unknown guidance |
| No default priority | Q5.1 assumptions stated | Specify defaults |
| Less explicit ordering | Q4.2 clear paths | Make ordering explicit |

### Tasklist Review - Prompt A Weaknesses (6 items, all IN-SCOPE)

| Weakness | QAG Coverage | Expected Fix |
|----------|--------------|--------------|
| Structural bugs (unclosed fences) | Q3.3 formatting | Close all fences |
| Phase numbering inconsistency | Q3.3 formatting | Fix numbering sequence |
| Non-deterministic ranges ("3-5 tasks") | Q5.1 assumptions | Specify exact values |
| No anti-fabrication rules | Q2.3 gaps, Q5.3 edge cases | Add fabrication prevention |
| No traceability matrix | Q2.3 gaps, Q4.2 clear paths | Add traceability |
| Multiple output files | Q3.1 organization, Q4.1 actionable | Consolidate structure |

**Root Cause**: The proposers and debate agents lack explicit guidance to:
1. Validate structural integrity (formatting, numbering)
2. Identify missing robustness controls (fabrication, unknown handling)
3. Assess completeness for prompt-type content (traceability, defaults)

---

## In-Scope Improvements

### 1. Strengthen Proposer Structural Guidance

**Current** (proposer-1):
```
Strategy: minimal-delta, value-preserving.
- Preserve structure and voice unless clearly harmful.
- Fix correctness gaps, missing requirements, and ambiguity.
- Improve formatting lightly.
```

**Proposed Addition**:
```
- Verify structural integrity:
  - All code fences properly opened and closed
  - Numbered lists sequential without gaps
  - Section references point to existing sections
  - Phase/step counts match actual content
```

### 2. Add Structural Validation to Debate Agent

Add a structural analysis section to the debate output:

```markdown
# Structural Validation

| Check | Proposal 1 | Proposal 2 | Proposal 3 |
|-------|------------|------------|------------|
| Code fences balanced | YES/NO | YES/NO | YES/NO |
| List numbering sequential | YES/NO | YES/NO | YES/NO |
| Cross-references valid | YES/NO | YES/NO | YES/NO |
| Counts match content | YES/NO | YES/NO | YES/NO |
```

### 3. Add Explicit QAG Questions for Structural Integrity

Add to generic.md under Clarity/Structure:

```markdown
| Q3.4 | Are all code fences and markdown structures properly closed? |
| Q3.5 | Are numbered sequences consecutive without gaps? |
```

---

## Summary

| Review | Weaknesses | All In-Scope |
|--------|------------|--------------|
| Roadmap | 7 | ✅ |
| Tasklist | 6 | ✅ |
| **Total** | **13** | **All within QAG rubric coverage** |

The rf:crossLLM pipeline should have caught all 13 weaknesses based on existing QAG questions. The fix is to strengthen the proposers, debate, and evaluation to better detect:
- Structural issues (Q3.x)
- Missing robustness controls (Q2.3, Q5.3)
- Assumption gaps (Q5.1)
- Actionability problems (Q4.x)

---

## File References

- Original roadmap review: `roadmap-upgrade-review.md`
- Original tasklist review: `tasklist-upgrade-review.md`
- Previous (incorrect) analysis: `rf-crossLLM-universal-improvements-proposal.md` (superseded)
