# Scoring Protocol Reference

Complete hybrid quantitative-qualitative scoring algorithm for base selection in the adversarial pipeline.

---

## A.1 Quantitative Layer (50% of final score)

All quantitative metrics are computed deterministically from artifact text. No LLM judgment is involved in this layer.

### Metrics

| Metric | Symbol | Weight | Computation |
|--------|--------|--------|-------------|
| Requirement Coverage | `RC` | 0.30 | Source requirements referenced in variant (grep-matched by ID or keyword) / total source requirements |
| Internal Consistency | `IC` | 0.25 | 1 - (contradictions detected / total scorable claims) |
| Specificity Ratio | `SR` | 0.15 | Concrete statements (numbers, dates, named entities, thresholds) / total substantive statements |
| Dependency Completeness | `DC` | 0.15 | Internal references that resolve to a definition / total internal references |
| Section Coverage | `SC` | 0.15 | Variant's top-level section count / max(section count across all variants) |

### Formula

```
quant_score = (RC × 0.30) + (IC × 0.25) + (SR × 0.15) + (DC × 0.15) + (SC × 0.15)
```

All metrics normalized to [0.0, 1.0]. `quant_score` ∈ [0.0, 1.0].

### Metric Computation Details

#### Requirement Coverage (RC)

```yaml
requirement_coverage:
  step_1: "Extract requirement IDs from source (FR-XXX, NFR-XXX, R-XXX patterns)"
  step_2: "For each requirement ID, grep-search the variant for matches"
  step_3: "Also keyword-match requirement descriptions (fuzzy match threshold: 3+ consecutive words)"
  step_4: "RC = matched_requirements / total_source_requirements"
  edge_case: "If source has no formal requirement IDs, use section-level topic matching"
```

#### Internal Consistency (IC)

```yaml
internal_consistency:
  step_1: "Extract all scorable claims (specific, falsifiable statements)"
  step_2: "For each claim, search for contradicting claims within the same variant"
  step_3: "Contradiction categories:"
  categories:
    - "Opposing claims about the same subject"
    - "Requirement-constraint conflicts"
    - "Impossible timeline/dependency sequences"
  step_4: "IC = 1 - (contradiction_count / total_claims)"
  rule: "Vague statements ('as appropriate', 'as needed') are not scorable claims"
```

#### Specificity Ratio (SR)

```yaml
specificity_ratio:
  concrete_indicators:
    - "Numbers and quantities (e.g., '5 milestones', '80% threshold')"
    - "Dates and timeframes (e.g., '2-week sprint', 'by Q3')"
    - "Named entities (e.g., 'PostgreSQL', 'OAuth2', 'WCAG 2.1')"
    - "Specific thresholds (e.g., '<200ms', '≥99.9%')"
    - "Measurable criteria (e.g., 'zero critical vulnerabilities')"
  vague_indicators:
    - "'appropriate', 'as needed', 'properly', 'adequate'"
    - "'should consider', 'might', 'various', 'etc.'"
    - "'best practices', 'industry standard' (without citation)"
  excluded: "Headings, boilerplate, metadata lines"
  formula: "SR = concrete_count / (concrete_count + vague_count)"
```

#### Dependency Completeness (DC)

```yaml
dependency_completeness:
  step_1: "Scan for internal references (section refs, milestone refs, component refs, term refs)"
  step_2: "For each reference, check if the referenced item is defined elsewhere in the document"
  step_3: "DC = resolved_references / total_references"
  reference_patterns:
    - "Section X.Y references"
    - "Milestone M{N} references"
    - "Deliverable D{M}.{N} references"
    - "See [section name] cross-references"
  edge_case: "External references (URLs, other documents) are excluded from this metric"
```

#### Section Coverage (SC)

```yaml
section_coverage:
  step_1: "Count top-level sections (H2 headings) in each variant"
  step_2: "Find max section count across all variants"
  step_3: "SC = variant_section_count / max_section_count"
  note: "Normalized so at least one variant always scores 1.0"
```

---

## A.2 Qualitative Layer (50% of final score)

Uses an additive binary rubric with mandatory evidence citation (Claim-Evidence-Verdict protocol).

### Dimensions and Criteria

#### Completeness (5 criteria)
1. Covers all explicit requirements from source input
2. Addresses edge cases and failure scenarios
3. Includes dependencies and prerequisites
4. Defines success/completion criteria
5. Specifies what is explicitly out of scope

#### Correctness (5 criteria)
1. No factual errors or hallucinated claims
2. Technical approaches are feasible with stated constraints
3. Terminology used consistently and accurately throughout
4. No internal contradictions (cross-validated with quantitative IC metric)
5. Claims supported by evidence or rationale within the document

#### Structure (5 criteria)
1. Logical section ordering (prerequisites before dependents)
2. Consistent hierarchy depth (no orphaned subsections)
3. Clear separation of concerns between sections
4. Navigation aids present (table of contents, cross-references, or index)
5. Follows conventions of the artifact type

#### Clarity (5 criteria)
1. Unambiguous language (no "should consider", "might", "as appropriate")
2. Concrete rather than abstract (specific actions, not general principles)
3. Each section has a clear purpose statement or can be summarized in one sentence
4. Acronyms and domain terms defined on first use
5. Actionable next steps or decision points clearly identified

#### Risk Coverage (5 criteria)
1. Identifies at least 3 risks with probability and impact assessment
2. Provides mitigation strategy for each identified risk
3. Addresses failure modes and recovery procedures
4. Considers external dependencies and their failure scenarios
5. Includes monitoring or validation mechanism for risk detection

### Evidence Citation Protocol (CEV)

Every criterion assessment MUST follow this structure:

```
CLAIM:    "[Criterion description] is met/not met in Variant X"
EVIDENCE: "[Direct quote or section reference from the variant]"
          OR "No evidence found — searched sections [list]"
VERDICT:  MET (1 point) | NOT MET (0 points)
```

**Rules**:
- No partial credit: Each criterion is 1 point (met) or 0 points (not met)
- If the evaluator cannot cite specific evidence for a MET verdict, the criterion defaults to NOT MET
- This prevents hallucinated quality assessments

### Formula

```
qual_score = total_criteria_met / 25
```

`qual_score` ∈ [0.0, 1.0]. Maximum: 25/25 = 1.0.

---

## A.3 Combined Scoring

```
variant_score = (0.50 × quant_score) + (0.50 × qual_score)
```

`variant_score` ∈ [0.0, 1.0].

---

## A.4 Tiebreaker Protocol

If the top two variants score within 5% of each other (`|score_A - score_B| < 0.05`):

1. **Debate performance**: The variant that won more diff points in Step 2 is selected
2. **Correctness count**: If debate performance also tied (within 5%), the variant with higher correctness criteria count wins (correctness is the most valuable dimension for hallucination detection)
3. **Input order**: If still tied, the variant presented first in input order is selected (arbitrary but deterministic)

---

## A.5 Position-Bias Mitigation

The qualitative evaluation runs twice per variant:

- **Pass 1**: Variants evaluated in input order (A, B, C, ...)
- **Pass 2**: Variants evaluated in reverse order (C, B, A, ...)

Per criterion, per variant:
- **Both passes agree** → Use the agreed verdict
- **Passes disagree** → Criterion is re-evaluated with explicit comparison prompt citing both passes' evidence; the re-evaluation verdict is final

This eliminates systematic position bias documented in LLM-as-judge research.

---

## Scoring Output Format

The base-selection.md artifact documents:

1. **Quantitative scoring table**: Per-metric scores with computation details per variant
2. **Qualitative rubric tables**: Per-dimension, per-criterion CEV assessments per variant
3. **Qualitative summary**: Dimension subtotals and qual_score per variant
4. **Combined scoring table**: Quant weighted, qual weighted, final score, and debate tiebreaker per variant
5. **Margin analysis**: Score difference and whether tiebreaker was needed
6. **Selection rationale**: Evidence-based explanation of why the selected base won
7. **Strengths to preserve**: From the selected base
8. **Strengths to incorporate**: From non-base variants (feeds into Step 4)

---

*Reference document for sc:adversarial skill*
*Source: SC-ADVERSARIAL-SPEC.md Appendix A (Sections A.1-A.5)*
