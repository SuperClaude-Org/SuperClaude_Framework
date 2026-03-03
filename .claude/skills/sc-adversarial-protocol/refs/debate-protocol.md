# Debate Protocol Reference

Detailed protocol specification for the 5-step adversarial debate pipeline.

## Protocol Overview

The adversarial pipeline executes 5 sequential steps, each producing a documented artifact. Steps must execute in order — each step's output feeds into the next.

```
Step 1: Diff Analysis → diff-analysis.md
Step 2: Adversarial Debate → debate-transcript.md
Step 3: Base Selection → base-selection.md
Step 4: Refactoring Plan → refactor-plan.md
Step 5: Merge Execution → merge-log.md + merged output
```

---

## Step 1: Diff Analysis

### Purpose
Systematic comparison identifying structural differences, content differences, contradictions, and unique contributions across all variants.

### Input
- All variant artifacts (2-10 files)

### Process

#### 1.1 Structural Diff
Compare section ordering, hierarchy depth, and heading structure across variants.

```yaml
structural_comparison:
  section_ordering: "Compare top-level section sequence across variants"
  hierarchy_depth: "Measure max nesting level per variant"
  heading_structure: "Map heading types and counts"
  severity_rating:
    Low: "Cosmetic differences (ordering preference)"
    Medium: "Structural approaches differ meaningfully"
    High: "Incompatible organizational models"
```

#### 1.2 Content Diff
Compare approaches topic-by-topic, identifying coverage differences.

```yaml
content_comparison:
  topic_extraction: "Identify topics addressed by each variant"
  approach_comparison: "For shared topics, describe each variant's approach"
  coverage_gaps: "Topics covered by some variants but not others"
  detail_level: "Compare depth of coverage per topic"
```

#### 1.3 Contradiction Detection

A contradiction is identified when:
1. Two statements within the same variant make opposing claims about the same subject
2. A stated requirement conflicts with a stated constraint
3. A timeline or dependency creates an impossible sequence

**Structured scan protocol**:
- For each claim in each variant, check whether any other claim asserts the opposite or an incompatible position
- Claims must be specific enough to be falsifiable — vague statements cannot contradict
- Cross-variant contradictions are categorized separately from intra-variant contradictions

#### 1.4 Unique Contribution Extraction
Identify ideas present in only one variant with value assessment.

```yaml
unique_contributions:
  detection: "Ideas/sections/approaches present in exactly one variant"
  value_assessment:
    High: "Addresses a gap no other variant covers; high impact"
    Medium: "Useful addition but not critical"
    Low: "Nice to have, minimal impact"
```

### Output
`diff-analysis.md` — organized by category (structural, content, contradictions, unique) with severity ratings and variant attribution.

### Delegation
Analytical agent or `/sc:analyze` equivalent.

---

## Step 2: Adversarial Debate

### Purpose
Structured debate where agents argue for their variant's approach, using steelman strategy.

### Input
- All variants + diff-analysis.md

### Steelman Requirement
Advocates MUST construct the strongest possible version of opposing positions before critiquing them. This is not a zero-sum competition — the goal is to identify genuine strengths from all sides.

### Round Structure

#### Round 1: Advocate Statements (Parallel)
- Each variant gets one advocate agent
- Advocate receives: their variant + all other variants + diff-analysis.md
- Advocate produces:
  - Summary of their position
  - Key strengths claimed (with evidence from their variant)
  - Steelman of each opposing variant's strongest points
  - Weaknesses identified in other variants (with evidence)
- **Execution**: All advocates run in parallel via Task tool

#### Round 2: Rebuttals (Sequential)
- **Condition**: `--depth standard` or `--depth deep`
- Each advocate receives all Round 1 transcripts
- Advocate produces:
  - Response to criticisms of their variant
  - Counter-evidence or concessions where criticism is valid
  - Updated assessment of other variants based on their defenses
- **Execution**: Sequential — each advocate sees all previous rebuttals

#### Round 3: Final Arguments (Conditional)
- **Condition**: `--depth deep` AND convergence < threshold
- Final positions after considering all rebuttals
- Focus on remaining unresolved disagreements
- **Execution**: Sequential

### Depth Control

| Depth | Rounds | Convergence Check |
|-------|--------|-------------------|
| quick | 1 (advocate only) | No convergence check |
| standard | 2 (advocate + rebuttal) | Post-Round 2 convergence check |
| deep | Up to 3 | Convergence checked after each round; stop if threshold met |

### Convergence Detection

```yaml
convergence:
  metric: "Percentage of diff points where agents agree on superior approach"
  threshold: "Configurable via --convergence flag (default 0.80)"
  calculation: "agreed_points / total_diff_points"
  tracking: "Per-point agreement updated after each round"
  status:
    CONVERGED: "Agreement >= threshold"
    NOT_CONVERGED: "Agreement < threshold after max rounds"
```

### Per-Point Scoring Matrix
For each diff point from Step 1:
- **Winner**: Which variant's approach is superior for this point
- **Confidence**: Percentage confidence in the winner assessment
- **Evidence summary**: Key evidence supporting the winner determination

### Output
`debate-transcript.md` — full debate with per-point scoring matrix and convergence assessment.

### Delegation
debate-orchestrator coordinates; domain agents participate as advocates.

---

## Step 3: Base Selection

See `scoring-protocol.md` for the complete hybrid quantitative-qualitative scoring algorithm.

### Summary
- Quantitative layer (50%): 5 deterministic metrics
- Qualitative layer (50%): 25-criterion additive binary rubric with CEV protocol
- Position-bias mitigation: Forward + reverse evaluation order
- Tiebreaker: Debate performance → correctness count → input order

### Output
`base-selection.md` — full scoring breakdown with evidence citations and selection rationale.

---

## Step 4: Refactoring Plan

### Purpose
Generate actionable plan to incorporate strengths from non-base variants into the selected base.

### Input
- Selected base variant
- All non-base variants
- debate-transcript.md (for evidence of which approaches were determined superior)

### Plan Structure

For each non-base strength (as determined by debate):
1. **Source**: Which variant and section contains the strength
2. **Target**: Where it integrates into the base
3. **Rationale**: Debate evidence supporting incorporation
4. **Integration approach**: How to merge (replace, append, insert, restructure)
5. **Risk level**: Low (additive), Medium (modifies existing), High (restructures)

For each base weakness identified during debate:
1. **Issue**: What was identified as weak
2. **Better variant**: Which non-base variant addresses it
3. **Fix approach**: How to address the weakness

Changes NOT being made (with rationale):
- Differences where the base approach was determined superior in debate

### Review
- Default: Auto-approved
- Interactive mode: User approval required before Step 5

### Output
`refactor-plan.md` — actionable merge plan with integration points.

---

## Step 5: Merge Execution

### Purpose
Execute the refactoring plan to produce a unified output.

### Input
- Base variant + refactor-plan.md

### Process
1. Read base variant and plan
2. Apply each planned change methodically (in plan order)
3. Maintain structural integrity (heading hierarchy, section flow)
4. Add provenance annotations (source attribution per merged section)
5. Post-merge validation:
   - Structural integrity check
   - Internal reference validation
   - Contradiction re-scan
6. Produce merge-log.md

### Provenance Annotation Format
```markdown
<!-- Source: Variant A (opus:architect), Section 3.2 -->
<!-- Source: Variant B (sonnet:security), Section 4.1 — merged per refactor-plan Change #3 -->
<!-- Source: Base (original) -->
```

### Output
- Unified merged artifact
- `merge-log.md` — per-change execution log

### Delegation
merge-executor agent (dedicated specialist).

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Agent fails to generate variant | Retry once, then proceed with N-1 variants (min 2) |
| Variants too similar (<10% diff) | Skip debate, select either, log "substantially identical" |
| No convergence after max rounds | Force-select by score, document non-convergence |
| Merge produces invalid output | Preserve all artifacts, flag failure, provide plan for manual execution |
| Single variant remains | Abort adversarial, return surviving variant with warning |

---

*Reference document for sc:adversarial skill*
*Source: SC-ADVERSARIAL-SPEC.md FR-002, FR-006*
