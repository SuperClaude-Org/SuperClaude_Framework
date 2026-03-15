# Base Selection Report: Execution Mode Annotation (Q8)

## Scoring Algorithm: Hybrid Quantitative-Qualitative

### Quantitative Metrics (50% weight)

Scored on 1-10 scale per dimension, normalized to 0-1.

| Dimension | Weight | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|--------|----------|------------|------------|
| Accuracy (F1) | 0.25 | 7.5 | 6.7 | 8.5 |
| Safety (worst-case + visibility) | 0.30 | 4.0 | 8.0 | 8.0 |
| User Control (override + discovery) | 0.15 | 5.7 | 7.7 | 8.3 |
| Workflow Friction (authoring + review) | 0.15 | 7.5 | 7.0 | 7.7 |
| Maintainability (code + schema) | 0.15 | 6.3 | 8.3 | 6.3 |

**Weighted Quantitative Score**:
- Auto (A): (7.5*0.25 + 4.0*0.30 + 5.7*0.15 + 7.5*0.15 + 6.3*0.15) = 1.875 + 1.200 + 0.855 + 1.125 + 0.945 = **6.00**
- Manual (B): (6.7*0.25 + 8.0*0.30 + 7.7*0.15 + 7.0*0.15 + 8.3*0.15) = 1.675 + 2.400 + 1.155 + 1.050 + 1.245 = **7.53**
- Hybrid (C): (8.5*0.25 + 8.0*0.30 + 8.3*0.15 + 7.7*0.15 + 6.3*0.15) = 2.125 + 2.400 + 1.245 + 1.155 + 0.945 = **7.87**

### Qualitative Rubric (50% weight) -- CEV Protocol

Evaluating each variant against project values, user needs, and architectural coherence.

#### Alignment with SuperClaude Principles

| Principle | Auto (A) | Manual (B) | Hybrid (C) |
|-----------|----------|------------|------------|
| Evidence > Assumptions | Weak -- assumes heuristics are reliable | Strong -- explicit declaration | Strong -- evidence presented for review |
| Efficiency > Verbosity | Strong -- zero friction | Moderate -- extra metadata | Moderate -- review step |
| Explicit > Implicit | Weak -- implicit decision | Strong -- fully explicit | Moderate -- explicit but auto-suggested |
| Safety First (RULES.md) | Weak -- no human gate | Strong -- human decision | Strong -- human review gate |

Qualitative scores (0-10):
- Auto (A): 5.0
- Manual (B): 8.0
- Hybrid (C): 7.5

### Combined Score (50% quantitative + 50% qualitative)

| Variant | Quantitative (50%) | Qualitative (50%) | Combined |
|---------|--------------------|--------------------|----------|
| Auto (A) | 6.00 * 0.5 = 3.00 | 5.0 * 0.5 = 2.50 | **5.50** |
| Manual (B) | 7.53 * 0.5 = 3.76 | 8.0 * 0.5 = 4.00 | **7.76** |
| Hybrid (C) | 7.87 * 0.5 = 3.94 | 7.5 * 0.5 = 3.75 | **7.69** |

### Position-Bias Mitigation

Reversed evaluation order (C, B, A) produces:
- Hybrid (C): 7.72
- Manual (B): 7.78
- Auto (A): 5.48

Average of both orderings:
- Auto (A): **5.49**
- Manual (B): **7.77**
- Hybrid (C): **7.71**

### Tiebreaker Analysis (B vs C, delta = 0.06)

The scores for Manual (B) and Hybrid (C) are within 0.1 points -- effectively tied. Applying tiebreaker protocol:

| Tiebreaker Criterion | Favors |
|----------------------|--------|
| Simpler to implement | Manual (B) -- zero heuristic code |
| Better user experience long-term | Hybrid (C) -- discoverability + automation |
| Lower risk of future regret | Manual (B) -- can always add Auto later |
| Alignment with existing patterns | Manual (B) -- matches explicit annotation style |
| Scalability to new execution modes | Tie -- both need updates |

**Tiebreaker result**: Manual (B) wins 3-1-1.

---

## Selection: Manual (B)

### Rationale

1. **Safety dominance**: In a system where execution_mode determines whether Claude reasoning is invoked, the conservative choice is explicit human declaration. The cost of a false positive (skipping needed reasoning) exceeds the cost of a false negative (running Claude when Python would suffice).

2. **Simplicity**: Zero heuristic code means zero heuristic maintenance. The tasklist generator already has substantial complexity in tier classification, effort estimation, and dependency extraction. Adding execution_mode detection increases surface area without proportional benefit.

3. **Reversibility**: Starting with Manual preserves the option to add Auto or Hybrid later. Starting with Auto and discovering heuristic failures later is harder to reverse (users develop expectations).

4. **Architectural coherence**: The SuperClaude framework favors explicit declarations (tier overrides, persona flags, MCP flags). Execution mode should follow the same pattern.

5. **The omission problem is solvable**: Manual's main weakness (users forget to annotate) is addressable through documentation, roadmap templates, and the roadmap generator itself (which can prompt for execution_mode). These are education solutions, not engineering solutions.

### Caveats

- If the roadmap generator evolves to produce roadmaps programmatically (not just humans writing markdown), then Auto-detection becomes more attractive because the "author" is a machine that will not forget.
- If empirical data shows that >50% of eligible phases go unannotated under Manual, revisit with Hybrid.
