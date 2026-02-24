# Artifact Templates Reference

Output format specifications for all 6 artifacts produced by the adversarial pipeline.

---

## Section 1: diff-analysis.md Template

```markdown
# Diff Analysis: <artifact-type> Comparison

## Metadata
- Generated: <ISO-8601 timestamp>
- Variants compared: <count>
- Total differences found: <count>
- Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>)

## Structural Differences

| # | Area | Variant A | Variant B | ... | Severity |
|---|------|-----------|-----------|-----|----------|
| S-001 | <area> | <description> | <description> | ... | Low/Medium/High |
| S-002 | <area> | <description> | <description> | ... | Low/Medium/High |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | ... | Severity |
|---|-------|-------------------|-------------------|-----|----------|
| C-001 | <topic> | <approach> | <approach> | ... | Low/Medium/High |
| C-002 | <topic> | <approach> | <approach> | ... | Low/Medium/High |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | ... | Impact |
|---|-------------------|-------------------|-------------------|-----|--------|
| X-001 | <conflict> | <position> | <position> | ... | Low/Medium/High |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | <variant> | <description> | High/Medium/Low |
| U-002 | <variant> | <description> | High/Medium/Low |

## Summary
- Total structural differences: <N>
- Total content differences: <N>
- Total contradictions: <N>
- Total unique contributions: <N>
- Highest-severity items: <list>
```

### ID Scheme
- `S-NNN`: Structural differences
- `C-NNN`: Content differences
- `X-NNN`: Contradictions
- `U-NNN`: Unique contributions

### Scaling for >2 Variants
When comparing more than 2 variants, tables expand horizontally with one column per variant. Each row describes how each variant handles that particular area/topic/conflict.

---

## Section 2: debate-transcript.md Template

```markdown
# Adversarial Debate Transcript

## Metadata
- Depth: <quick|standard|deep>
- Rounds completed: <N>
- Convergence achieved: <percentage>%
- Convergence threshold: <configured>%
- Focus areas: <list or "All">
- Advocate count: <N>

## Round 1: Advocate Statements

### Variant A Advocate (<agent-spec>)
**Position**: [Summary of argument for Variant A]

**Steelman of Variant B**:
[Strongest version of Variant B's argument before critique]

**Key strengths claimed**:
1. [Strength with evidence — cite section/quote]
2. [Strength with evidence]

**Weaknesses identified in Variant B**:
1. [Critique with evidence]
2. [Critique with evidence]

**Concessions**:
- [Any acknowledged weaknesses in own variant]

### Variant B Advocate (<agent-spec>)
**Position**: [Summary of argument for Variant B]

**Steelman of Variant A**:
[Strongest version of Variant A's argument before critique]

**Key strengths claimed**:
1. [Strength with evidence]

**Weaknesses identified in Variant A**:
1. [Critique with evidence]

**Concessions**:
- [Any acknowledged weaknesses]

[... additional advocates for variants C through N ...]

## Round 2: Rebuttals

### Variant A Rebuttal
[Response to criticisms with counter-evidence or concessions]

### Variant B Rebuttal
[Response to criticisms with counter-evidence or concessions]

[... additional rebuttals ...]

## Round 3: Final Arguments (if applicable)

### Variant A Final Position
[Updated position after all rebuttals]

### Variant B Final Position
[Updated position after all rebuttals]

## Scoring Matrix

| Diff Point | Winner | Confidence | Evidence Summary |
|------------|--------|------------|-----------------|
| S-001 | <variant> | <N>% | <summary> |
| C-001 | <variant> | <N>% | <summary> |
| X-001 | <variant> | <N>% | <summary> |

## Convergence Assessment
- Points resolved: <N> of <total>
- Alignment: <percentage>%
- Threshold: <configured>%
- Status: CONVERGED | NOT_CONVERGED
- Unresolved points: [list of diff point IDs]
```

---

## Section 3: base-selection.md Template

```markdown
# Base Selection Report

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A (<spec>) | Variant B (<spec>) | ... |
|--------|--------|-------------------|-------------------|-----|
| requirement_coverage | 0.30 | <score> (<detail>) | <score> (<detail>) | ... |
| internal_consistency | 0.25 | <score> (<detail>) | <score> (<detail>) | ... |
| specificity_ratio | 0.15 | <score> (<detail>) | <score> (<detail>) | ... |
| dependency_completeness | 0.15 | <score> (<detail>) | <score> (<detail>) | ... |
| section_coverage | 0.15 | <score> (<detail>) | <score> (<detail>) | ... |
| **quant_score** | | **<score>** | **<score>** | ... |

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| Criterion | Variant A | Evidence | Variant B | Evidence |
|-----------|-----------|----------|-----------|----------|
| Covers all explicit requirements | MET/NOT MET | <CEV evidence> | MET/NOT MET | <CEV evidence> |
| Addresses edge cases/failures | MET/NOT MET | <evidence> | MET/NOT MET | <evidence> |
| Includes dependencies/prerequisites | MET/NOT MET | <evidence> | MET/NOT MET | <evidence> |
| Defines success/completion criteria | MET/NOT MET | <evidence> | MET/NOT MET | <evidence> |
| Specifies out-of-scope items | MET/NOT MET | <evidence> | MET/NOT MET | <evidence> |
| **Subtotal** | **<N>/5** | | **<N>/5** | |

### Correctness (5 criteria)
[Same table format as Completeness]

### Structure (5 criteria)
[Same table format as Completeness]

### Clarity (5 criteria)
[Same table format as Completeness]

### Risk Coverage (5 criteria)
[Same table format as Completeness]

### Qualitative Summary

| Dimension | Variant A | Variant B | ... |
|-----------|-----------|-----------|-----|
| Completeness | <N>/5 | <N>/5 | ... |
| Correctness | <N>/5 | <N>/5 | ... |
| Structure | <N>/5 | <N>/5 | ... |
| Clarity | <N>/5 | <N>/5 | ... |
| Risk Coverage | <N>/5 | <N>/5 | ... |
| **qual_score** | **<N>/25 = <score>** | **<N>/25 = <score>** | ... |

## Position-Bias Mitigation

| Criterion | Variant | Pass 1 | Pass 2 | Agreement | Final |
|-----------|---------|--------|--------|-----------|-------|
| [criterion] | A | MET | NOT MET | DISAGREE | [re-eval result] |

Disagreements re-evaluated: <N>
Final verdicts changed: <N>

## Combined Scoring

| Variant | Quant (×0.50) | Qual (×0.50) | **Final Score** | Debate Tiebreaker |
|---------|---------------|--------------|-----------------|-------------------|
| A (<spec>) | <weighted> | <weighted> | **<score>** | <wins>% (if needed) |
| B (<spec>) | <weighted> | <weighted> | **<score>** | <wins>% |

**Margin**: <percentage>% (<above/below> 5% threshold)
**Tiebreaker applied**: Yes/No

## Selected Base: Variant <X> (<agent-spec>)

### Selection Rationale
[Evidence-based explanation of why this variant was selected]

### Strengths to Preserve from Base
1. [Strength to keep]
2. [Strength to keep]

### Strengths to Incorporate from Non-Base Variants
1. [From Variant Y: specific strength + section reference]
2. [From Variant Z: specific strength + section reference]
```

---

## Section 4: refactor-plan.md Template

```markdown
# Refactoring Plan: Merge into Base (Variant <X>)

## Overview
- Base: Variant <X> (<agent-spec>)
- Incorporating strengths from: [list of non-base variants]
- Planned changes: <N>
- Risk level: Low/Medium/High (overall)

## Planned Changes

### Change 1: <Title> (from Variant <Y>)
- **Source**: Variant <Y>, Section <ref>
- **Target**: Base, Section <ref> (<replace|append|insert|restructure>)
- **Rationale**: <Debate evidence — cite round, diff point, confidence>
- **Integration point**: <Specific location and approach>
- **Risk**: Low/Medium/High — <reason>

### Change 2: <Title> (from Variant <Z>)
- **Source**: Variant <Z>, Section <ref>
- **Target**: Base, new Section <ref>
- **Rationale**: <Unique contribution U-NNN with <value> assessment>
- **Integration point**: <Specific insertion point>
- **Risk**: Low/Medium/High — <reason>

[... additional changes ...]

## Changes NOT Being Made (with rationale)

| Diff Point | Non-Base Approach | Rationale for Keeping Base |
|------------|-------------------|---------------------------|
| <ID> | <description> | <debate evidence for base superiority> |

## Risk Summary

| Change # | Risk | Impact if Failed | Rollback |
|----------|------|------------------|----------|
| 1 | Medium | Breaks 3 dependent sections | Revert to base Section <ref> |
| 2 | Low | Additive, no conflicts | Remove inserted section |

## Review Status
- [ ] Auto-approved (default)
- [ ] User-approved (--interactive)
- Approved by: <auto|user>
- Approval timestamp: <ISO-8601>
```

---

## Section 5: merge-log.md Template

```markdown
# Merge Execution Log

## Metadata
- Base: Variant <X> (<agent-spec>)
- Executor: merge-executor agent
- Changes applied: <N> of <total planned>
- Status: success/partial/failed
- Timestamp: <ISO-8601>

## Changes Applied

### Change 1: <Title>
- **Status**: Applied/Failed/Skipped
- **Source**: Variant <Y>, Section <ref>
- **Target**: Base, Section <ref>
- **Before**: [Brief summary of original content]
- **After**: [Brief summary of merged content]
- **Provenance tag**: `<!-- Source: Variant Y, Section ref -->`
- **Validation**: Structural integrity ✅ | References ✅ | Contradictions ✅

### Change 2: <Title>
- **Status**: Applied/Failed/Skipped
- **Source**: Variant <Z>, Section <ref>
- **Target**: Base, new Section <ref>
- **Before**: [Section did not exist]
- **After**: [Brief summary of new content]
- **Provenance tag**: `<!-- Source: Variant Z, Section ref -->`
- **Validation**: Structural integrity ✅ | References ✅ | Contradictions ✅

[... additional changes ...]

## Post-Merge Validation

### Structural Integrity
- Heading hierarchy: ✅/❌ [details]
- Section ordering: ✅/❌ [details]
- Document flow: ✅/❌ [details]

### Internal References
- Total references: <N>
- Resolved: <N>
- Broken: <N> [list if any]

### Contradiction Re-Scan
- New contradictions introduced: <N>
- Details: [list if any]

## Summary
- Total changes planned: <N>
- Successfully applied: <N>
- Failed: <N> [list reasons]
- Skipped: <N> [list reasons]
- Post-merge validation: PASS/FAIL
```

---

## Section 6: Merged Output Provenance Format

The merged output file itself includes inline provenance annotations:

```markdown
<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant A (opus:architect) -->
<!-- Merge date: ISO-8601 timestamp -->

# Document Title

<!-- Source: Base (original) -->
[Original base content preserved here]

<!-- Source: Variant B (sonnet:security), Section 3.2 — merged per Change #1 -->
[Content incorporated from Variant B]

<!-- Source: Base (original, modified) — adjusted per Change #3 to resolve contradiction X-001 -->
[Modified base content]
```

### Provenance Tag Rules
- Every section or significant block includes a `<!-- Source: ... -->` tag
- Tags identify the variant, section reference, and change number (if applicable)
- Original base content tagged as `<!-- Source: Base (original) -->`
- Modified base content tagged as `<!-- Source: Base (original, modified) — reason -->`
- Incorporated content tagged with source variant and change reference

---

*Reference document for sc:adversarial skill*
*Source: SC-ADVERSARIAL-SPEC.md Sections 8.1-8.4, FR-005*
