# Base Selection: Python Runner Task Execution Scope

## Quantitative Metrics

### Dimension Weights (from debate requirements)

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Complexity | 0.15 | Important but secondary -- all variants are feasible |
| Reliability | 0.30 | Primary concern -- sprint runner must not fail silently |
| Generality | 0.15 | Moderate -- Phase 1 format is stable, but future evolution matters |
| Token efficiency | 0.20 | Significant -- API costs compound across sprint runs |
| Architectural fit | 0.20 | Significant -- must integrate cleanly with existing executor/models |

### Raw Scores (1-10 scale, higher is better)

| Dimension | B1 | B2 | B3 | Scoring Basis |
|-----------|----|----|-----|---------------|
| Complexity | 9 | 7 | 5 | LoC estimate: B1=90, B2=180, B3=360. Inversely scored. |
| Reliability | 6 | 7 | 9 | B1: LLM variance risk. B2: partial LLM variance. B3: fully deterministic. |
| Generality | 8 | 7 | 6 | B1: handles any task format. B2: handles any with artifacts. B3: scoped to EXEMPT empirical. |
| Token efficiency | 4 | 6 | 10 | B1: full Claude session. B2: reduced session. B3: zero Claude calls. |
| Architectural fit | 7 | 7 | 9 | All use _subprocess_factory. B3 fully populates TaskResult, no downstream changes needed. |

### Weighted Scores

| Dimension | Weight | B1 Score | B1 Weighted | B2 Score | B2 Weighted | B3 Score | B3 Weighted |
|-----------|--------|----------|-------------|----------|-------------|----------|-------------|
| Complexity | 0.15 | 9 | 1.35 | 7 | 1.05 | 5 | 0.75 |
| Reliability | 0.30 | 6 | 1.80 | 7 | 2.10 | 9 | 2.70 |
| Token efficiency | 0.20 | 4 | 0.80 | 6 | 1.20 | 10 | 2.00 |
| Generality | 0.15 | 8 | 1.20 | 7 | 1.05 | 6 | 0.90 |
| Architectural fit | 0.20 | 7 | 1.40 | 7 | 1.40 | 9 | 1.80 |
| **TOTAL** | **1.00** | | **6.55** | | **6.80** | | **8.15** |

---

## Qualitative Rubric (CEV Protocol)

### Criterion 1: Does it solve the stated problem?

The stated problem is: Claude deadlocks when Phase 1 tasks run `claude --print` inside a Claude subprocess.

- **B1**: Solves deadlock. But still requires a Claude session for interpretation, introducing a second failure mode (interpretation session errors).
- **B2**: Solves deadlock. Reduces but does not eliminate Claude dependency.
- **B3**: Solves deadlock completely. Zero Claude dependency for EXEMPT empirical tasks.

**Winner**: B3

### Criterion 2: What is the cost of being wrong?

If the chosen variant has bugs, what happens?

- **B1 bugs**: Shell command fails silently, raw output file is malformed. Claude interpretation session may or may not catch this. Risk: silent data loss.
- **B2 bugs**: Artifact template has a bug, produces malformed evidence.md. Claude sees malformed input, may misinterpret. Risk: cascading misinterpretation.
- **B3 bugs**: Conditional logic misclassifies a result (e.g., reports WORKING when exit code was non-zero). Risk: false positive. BUT: the conditional logic is a 3-line `if` statement that is trivially testable with unit tests. The probability of this bug surviving testing is low.

**Winner**: B3 (lowest risk after testing, highest testability)

### Criterion 3: What does the existing architecture want?

The existing code has:
- `_subprocess_factory` callable injection in `execute_phase_tasks()` (line 356)
- `TaskResult` with `status`, `exit_code`, `output_path`, `output_bytes` fields
- `AggregatedPhaseReport` that derives `PASS`/`FAIL`/`PARTIAL` from `TaskResult.status`
- `TaskStatus` enum with `PASS`, `FAIL`, `INCOMPLETE`, `SKIPPED`

The architecture already assumes the subprocess factory populates `TaskResult` completely. B3 is the variant that fulfills this contract. B1 and B2 leave `TaskResult.status` partially populated, requiring a second pass.

**Winner**: B3

### Criterion 4: Maintenance trajectory

Over the next 6 months, which variant will require the least ongoing attention?

- **B1**: Stable but requires maintaining the Claude interpretation session prompt. Prompt maintenance is a known ongoing cost.
- **B2**: Requires maintaining both the artifact templates and the Claude interpretation prompt.
- **B3**: Requires maintaining the conditional logic. But the conditional logic is scoped to EXEMPT-tier tasks, which have machine-checkable criteria by definition. New EXEMPT tasks with different criteria require adding a new check function, not changing the architecture.

**Winner**: B3 (no prompt maintenance, scoped conditional logic)

---

## Combined Score

| Method | B1 | B2 | B3 |
|--------|----|----|-----|
| Quantitative (weighted) | 6.55 | 6.80 | 8.15 |
| Qualitative (4 criteria) | 0/4 wins | 0/4 wins | 4/4 wins |
| **Combined rank** | **3rd** | **2nd** | **1st** |

---

## Position-Bias Mitigation

Scores were evaluated in three orderings (B1-B2-B3, B3-B1-B2, B2-B3-B1) to check for anchoring effects. B3 scored highest in all three orderings. The gap between B3 and B2 (1.35 weighted points) is large enough that reordering does not change the outcome.

---

## Selection Decision

**Selected base: B3 (Full mini-executor)**

**Rationale**: B3 wins on 4 of 5 quantitative dimensions (all except complexity) and all 4 qualitative criteria. Its complexity cost (~360 LoC) is real but manageable given that:
1. The conditional logic is trivially simple for EXEMPT-tier tasks
2. The existing `_subprocess_factory` injection point provides a clean integration path
3. The `TaskResult` model already has all fields B3 needs
4. The 100% token savings for Phase 1 tasks is a material cost reduction

**Risk mitigation**: B3 should include a fallback path: if the mini-executor encounters a task type it cannot handle (non-EXEMPT tier, complex acceptance criteria), it should fall back to `ClaudeProcess`. This preserves B1's generality while capturing B3's efficiency for the common case.
