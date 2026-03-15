# Base Selection -- execution_mode Value Set

## Candidates

| ID | Value Set | Advocate |
|---|---|---|
| A | {claude, python, skip} | Minimal |
| B | {claude, python, python-gate, skip, manual} | Expanded |
| C | {claude, python, skip} + separate `condition` field | Moderator synthesis |

## Quantitative Scoring (40% weight)

### Metric 1: YAGNI Compliance (0-10)

How many values have zero current use cases?

| Candidate | Values with no current use case | Score |
|---|---|---|
| A | 0 of 3 | 10 |
| B | 1 of 5 (manual) | 7 |
| C | 0 of 3 + condition field has 1 use case | 9 |

### Metric 2: Implementation Cost (0-10, inverted: lower cost = higher score)

| Candidate | Estimated LOC | Score |
|---|---|---|
| A | ~90-130 | 9 |
| B | ~190-270 | 6 |
| C | ~130-180 (3 modes + condition parser) | 7 |

### Metric 3: Semantic Overlap (0-10, inverted: less overlap = higher score)

How many values are strict supersets of other values?

| Candidate | Overlapping pairs | Score |
|---|---|---|
| A | 0 | 10 |
| B | 1 (python-gate superset of python) | 7 |
| C | 0 | 10 |

### Metric 4: Composability Complexity (0-10, inverted: less complexity = higher score)

How many problematic interactions with Tier/Dependencies/Verification?

| Candidate | Problematic interactions | Score |
|---|---|---|
| A | 1 (python + tier orthogonality needs docs) | 8 |
| B | 3 (python-gate cross-phase effects, manual blocks downstream, python + tier) | 5 |
| C | 1 (python + tier) + condition field is explicitly designed for cross-phase | 8 |

### Quantitative Subtotal

| Candidate | YAGNI | Cost | Overlap | Composability | Total (max 40) | Normalized (max 10) |
|---|---|---|---|---|---|---|
| A | 10 | 9 | 10 | 8 | 37 | 9.25 |
| B | 7 | 6 | 7 | 5 | 25 | 6.25 |
| C | 9 | 7 | 10 | 8 | 34 | 8.50 |

## Qualitative Scoring (60% weight)

### Rubric 1: Forward Compatibility (0-10)

**A**: Adding `python-gate` later requires no breaking changes (new enum value). Adding a `condition` field later also works. Loses points only for lack of machine-readable gating today. **Score: 7**

**B**: All foreseeable patterns covered. `manual` may not match future compliance requirements. `python-gate` semantics depend on an undefined condition contract. **Score: 7**

**C**: Clean separation of mechanism (execution_mode) and semantics (condition). The `condition` field is extensible to arbitrary expressions. Best forward-compatibility story. **Score: 9**

### Rubric 2: Conceptual Integrity (0-10)

Does the value set have a coherent single-axis meaning?

**A**: Yes. `execution_mode` answers "who runs this?" -- Claude, Python, or nobody. Pure mechanism. **Score: 9**

**B**: Mixed. `python-gate` encodes both mechanism (Python) and semantics (gate). `manual` is mechanism (human). The axis is not purely mechanism nor purely semantics. **Score: 5**

**C**: Yes. `execution_mode` is pure mechanism. `condition` is pure flow control. Each field has one axis. **Score: 10**

### Rubric 3: Alignment with Existing Codebase (0-10)

How well does the candidate match the current sprint runner architecture?

**A**: Sprint runner already dispatches to Claude. Adding Python dispatch is a clean extension. Skip is trivial. No architectural changes needed. **Score: 9**

**B**: Requires gate-result propagation mechanism, pause/resume state machine. Moderate architectural changes. **Score: 5**

**C**: Python dispatch is clean. `condition` field requires a condition evaluator in the tasklist parser, but this is a well-understood pattern. **Score: 7**

### Rubric 4: Risk of Regret (0-10, inverted: lower regret = higher score)

What is the cost if we get it wrong?

**A**: Low regret. If we need `python-gate` later, we add it. If we need `manual`, we add it. Enum values are append-only. **Score: 9**

**B**: Medium regret. If `python-gate` semantics are wrong, we have a deprecated value polluting the enum. If `manual` never gets used, it is dead code. **Score: 5**

**C**: Low-medium regret. If the `condition` field expression language is wrong, that is a more expensive fix than a bad enum value. But the field is optional and can be iterated. **Score: 7**

### Qualitative Subtotal

| Candidate | Forward | Integrity | Alignment | Regret | Total (max 40) | Normalized (max 10) |
|---|---|---|---|---|---|---|
| A | 7 | 9 | 9 | 9 | 34 | 8.50 |
| B | 7 | 5 | 5 | 5 | 22 | 5.50 |
| C | 9 | 10 | 7 | 7 | 33 | 8.25 |

## Combined Score

| Candidate | Quantitative (40%) | Qualitative (60%) | Combined |
|---|---|---|---|
| A | 9.25 x 0.4 = 3.70 | 8.50 x 0.6 = 5.10 | **8.80** |
| B | 6.25 x 0.4 = 2.50 | 5.50 x 0.6 = 3.30 | **5.80** |
| C | 8.50 x 0.4 = 3.40 | 8.25 x 0.6 = 4.95 | **8.35** |

## Selection: Candidate A wins, with Candidate C as the recommended evolution path.

### Rationale

Candidate A ({claude, python, skip}) wins on:
1. **YAGNI compliance**: Every value has a concrete current use case.
2. **Conceptual integrity**: `execution_mode` is purely about mechanism (who runs the code).
3. **Low regret**: Enum values are append-only. Adding `python-gate` or `manual` later costs nothing.
4. **Implementation simplicity**: Roughly half the code of Candidate B.

Candidate C is the recommended next step when machine-readable gating is needed: add a separate `condition` field rather than encoding gate semantics in `execution_mode`.

### Position-Bias Mitigation

Scoring was performed with candidates in alphabetical order (A, B, C) rather than advocacy order (Minimal presented first). Quantitative metrics use objective criteria (LOC counts, overlap counts). Qualitative rubrics were evaluated for each candidate independently before comparison.

### Tiebreaker Note

No tiebreaker needed. Candidate A leads by 0.45 points over Candidate C and by 3.00 points over Candidate B.
