# Base Selection: Assertion Engine for Python Pre-Sprint Executor

## Selection: Option C -- Hardcoded Python Classifiers

---

## Quantitative Scoring

### Dimension 1: Benefit (weight: 0.35)

| Sub-dimension | Weight | A (Inline DSL) | B (Structured Block) | C (Hardcoded Python) |
|---|---|---|---|---|
| Expressiveness (known needs) | 0.25 | 9 | 9 | 10 |
| Generality (future needs) | 0.30 | 4 | 5 | 10 |
| Readability | 0.25 | 6 | 8 | 6 |
| Generator fit | 0.20 | 7 | 7 | 9 |
| **Weighted sub-total** | | **6.25** | **7.15** | **8.80** |

### Dimension 2: Risk (weight: 0.35, inverted: lower risk = higher score)

| Sub-dimension | Weight | A | B | C |
|---|---|---|---|---|
| Parsing fragility (10=no risk) | 0.30 | 4 | 6 | 10 |
| Security (10=no risk) | 0.20 | 8 | 8 | 10 |
| Semantic ambiguity (10=no risk) | 0.25 | 5 | 7 | 10 |
| Migration cost (10=easy to change) | 0.25 | 6 | 6 | 9 |
| **Weighted sub-total** | | **5.55** | **6.65** | **9.75** |

### Dimension 3: Complexity (weight: 0.30, inverted: lower complexity = higher score)

| Sub-dimension | Weight | A | B | C |
|---|---|---|---|---|
| Implementation effort (10=minimal) | 0.30 | 4 | 5 | 9 |
| Testing surface (10=minimal) | 0.25 | 4 | 5 | 9 |
| Maintenance burden (10=minimal) | 0.25 | 3 | 5 | 9 |
| Cognitive load (10=minimal) | 0.20 | 4 | 5 | 9 |
| **Weighted sub-total** | | **3.75** | **5.00** | **9.00** |

### Combined Final Scores

| Option | Benefit (x0.35) | Risk (x0.35) | Complexity (x0.30) | **Final Score** |
|---|---|---|---|---|
| A (Inline DSL) | 2.19 | 1.94 | 1.13 | **5.25** |
| B (Structured Block) | 2.50 | 2.33 | 1.50 | **6.33** |
| C (Hardcoded Python) | 3.08 | 3.41 | 2.70 | **9.19** |

**Score gap**: C leads B by 2.86 points (45% margin). No tiebreaker needed.

---

## Qualitative Assessment (CEV Protocol)

### Position-Bias Mitigation
Evaluation order rotated to C-A-B (not alphabetical) to avoid anchoring on first-presented option.

### Option C -- Hardcoded Python Classifiers
**Strengths**: Strongest architectural alignment with existing `FailureClassifier`, `TrailingGatePolicy`, `GateCriteria` patterns. Standard Python testability with pytest. Zero parsing risk. Unlimited future expressiveness. Lowest implementation, maintenance, and cognitive costs.

**Weakness**: Tasklist is not self-describing for classification logic. Reader must consult Python source to understand exact classification rules. Requires code deployment for new classifiers.

**Mitigations**: Descriptive classifier names (e.g., `empirical_gate_v1`). Docstrings on classifier functions. Optional `| Classifier Notes |` metadata row for human-readable summary.

### Option A -- Inline DSL
**Strengths**: Maximum information density. Everything visible in metadata table.

**Weaknesses**: Highest parsing fragility. Introduces new micro-language. No existing codebase pattern to build on. Highest cognitive load for contributors.

### Option B -- Structured Block
**Strengths**: Best readability of the DSL options. `required` keyword provides useful semantic distinction. Per-line parsing is more robust.

**Weaknesses**: Still introduces a custom language. Still requires custom parser. The `required` vs `label=` distinction adds complexity for 3 known use cases.

---

## Selection Rationale

Option C is selected as the base for four decisive reasons:

1. **Architectural consistency**: The codebase already classifies outputs in Python (`FailureClassifier`, `TrailingGatePolicy`). Option C follows the established pattern. Options A and B would introduce a competing paradigm, violating DRY at the architectural level.

2. **Proportionality (YAGNI)**: The known need is 3 tasks in 1 phase. Building a DSL parser (100-150 LOC) with its testing surface, error handling, and documentation for 3 classification rules is disproportionate. Option C requires ~30 LOC.

3. **Irreversibility analysis**: If C proves insufficient, a DSL layer can be added on top (the DSL parser would produce classifier functions). The reverse migration -- from DSL to Python classifiers -- would require rewriting all tasklists AND the parser. C preserves more future options.

4. **DSL evolution trap**: Both A and B will face pressure to add regex, numeric comparisons, boolean logic, multi-field assertions, and error handling. Each addition compounds the maintenance burden. The natural end-state of this evolution is reinventing a programming language. Option C starts at that end-state.

### Acknowledged Trade-off
The readability concern from Advocates A/B is valid. The refactoring plan addresses this by integrating classifier name visibility into the tasklist metadata table and recommending descriptive naming conventions.
