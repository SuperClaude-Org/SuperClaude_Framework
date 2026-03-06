# Common Scoring Framework: Adversarial 2.0 Proposal Evaluation

## Purpose

Unified rubric for evaluating the 3 implementation proposals (A: Meta-Orchestrator, B: Recursive Pipeline, C: Phase DSL) for Adversarial 2.0 single-command multi-phase orchestration.

---

## Scoring Formula

```
Total Score = (0.30 × Complexity Score) + (0.30 × Efficiency Score) + (0.40 × Efficacy Score)
```

Each dimension normalized to 0–100. Higher is better.

---

## Dimension 1: Complexity (30% weight) — Lower is Better

Measures implementation size, coupling, and migration risk. **Inverted**: raw complexity is scored low-is-bad, then inverted so simpler proposals score higher.

### Sub-Criteria

| # | Criterion | Weight | Scoring Guide | Evidence Source |
|---|-----------|--------|---------------|-----------------|
| CX-1 | Implementation Size | 0.30 | 100: <400 lines, 75: 400-700, 50: 700-1000, 25: 1000-1400, 0: >1400 | "Lines (est.)" tables in each proposal |
| CX-2 | Pipeline Coupling | 0.25 | 100: Zero pipeline changes, 75: <5 lines changed, 50: 5-20 lines, 25: 20-50, 0: >50 | "Change Type" columns, refactoring scope |
| CX-3 | New Abstractions Introduced | 0.20 | 100: 0-1, 75: 2, 50: 3, 25: 4-5, 0: >5 | Component tables, new concepts |
| CX-4 | Migration Risk | 0.15 | 100: Zero breaking changes, 75: minor flag additions only, 50: new parsing paths, 25: existing flag semantics change, 0: backward incompatible | Risk Analysis sections |
| CX-5 | Cognitive Load (User) | 0.10 | 100: One new flag, 75: 2-3 new flags, 50: 4-5 flags + simple config, 25: config DSL, 0: full DSL + presets + interpolation | Interface Design sections |

### Complexity Calculation

```
raw_complexity = (CX-1 × 0.30) + (CX-2 × 0.25) + (CX-3 × 0.20) + (CX-4 × 0.15) + (CX-5 × 0.10)
ComplexityScore = raw_complexity  # Already inverted — simpler = higher score
```

---

## Dimension 2: Efficiency (30% weight)

Measures runtime/tool cost, agent count, and token/latency profile.

### Sub-Criteria

| # | Criterion | Weight | Scoring Guide | Evidence Source |
|---|-----------|--------|---------------|-----------------|
| EF-1 | Token Cost (8-step workflow) | 0.30 | 100: <25K, 75: 25-35K, 50: 35-50K, 25: 50-75K, 0: >75K | Token estimates per proposal |
| EF-2 | Parallelization Potential | 0.25 | 100: DAG-aware parallel, 75: manual parallel phases, 50: limited parallel, 25: mostly serial, 0: fully serial | Concurrency model sections |
| EF-3 | SKILL.md Token Overhead | 0.20 | 100: <300 lines added, 75: 300-500, 50: 500-800, 25: 800-1200, 0: >1200 | Implementation size estimates |
| EF-4 | Agent Spawning Overhead | 0.15 | 100: reuses existing agents, 75: 1 new agent type, 50: 2-3 new, 25: 4-5 new, 0: >5 new | Agent delegation sections |
| EF-5 | Incremental Execution (resume) | 0.10 | 100: full resume from manifest, 75: phase-level resume, 50: partial resume, 25: restart from scratch, 0: no resume support | Error handling sections |

### Efficiency Calculation

```
EfficiencyScore = (EF-1 × 0.30) + (EF-2 × 0.25) + (EF-3 × 0.20) + (EF-4 × 0.15) + (EF-5 × 0.10)
```

---

## Dimension 3: Efficacy (40% weight)

Measures correctness, contradiction resolution quality, and reproducibility. Highest weight because the primary goal is **better adversarial outcomes**.

### Sub-Criteria

| # | Criterion | Weight | Scoring Guide | Evidence Source |
|---|-----------|--------|---------------|-----------------|
| EC-1 | 8-Step Workflow Completeness | 0.25 | 100: exact match, 75: minor deviations, 50: achievable with workarounds, 25: partial coverage, 0: cannot express | Concrete examples in each proposal |
| EC-2 | Contradiction Resolution Quality | 0.20 | 100: multi-round cross-model debate preserved at every level, 75: preserved for most phases, 50: simplified at some levels, 25: degraded, 0: lost | Debate protocol integration |
| EC-3 | Steelman Preservation | 0.15 | 100: guaranteed at every phase, 75: guaranteed for primary phases, 50: advisory, 25: optional, 0: lost | Steelman protocol references |
| EC-4 | Position Bias Mitigation | 0.10 | 100: explicit at every level + shuffle, 75: explicit at every level, 50: inherited from pipeline, 25: partial, 0: absent | Bias mitigation sections |
| EC-5 | Reproducibility | 0.10 | 100: deterministic manifest + checksums, 75: manifest without checksums, 50: log-based, 25: partial logging, 0: non-reproducible | State management sections |
| EC-6 | Composability / Extensibility | 0.10 | 100: arbitrary DAG of phases, 75: tree structure, 50: linear chain, 25: fixed patterns only, 0: single hardcoded workflow | Architecture sections |
| EC-7 | Error Recovery Robustness | 0.10 | 100: phase-level recovery + resume + graceful degradation, 75: phase-level recovery, 50: retry only, 25: abort only, 0: catastrophic failure | Error handling sections |

### Efficacy Calculation

```
EfficacyScore = (EC-1 × 0.25) + (EC-2 × 0.20) + (EC-3 × 0.15) + (EC-4 × 0.10) + (EC-5 × 0.10) + (EC-6 × 0.10) + (EC-7 × 0.10)
```

---

## Scoring Protocol

### Process

1. **Independent scoring**: Each debate agent scores all 3 proposals independently
2. **Evidence requirement**: Every score MUST cite a specific section/line from the proposal
3. **Calibration check**: If any two agents disagree by >20 points on a sub-criterion, they must provide additional evidence
4. **Final aggregation**: Average across debate agents, weighted by formula

### Anti-Bias Rules

1. Score proposals in **alphabetical order** (A, B, C) in first pass
2. Score in **reverse order** (C, B, A) in second pass
3. If a sub-criterion score differs >15 points between passes, re-evaluate with explicit comparison
4. No proposal may receive all-100s or all-0s on any dimension (reject and re-score)

### Score Confidence

Each sub-criterion score includes a confidence indicator:
- **HIGH** (±5): Clear evidence, unambiguous scoring
- **MEDIUM** (±10): Some interpretation needed, evidence supports range
- **LOW** (±15): Limited evidence, significant judgment involved

---

## Output Template

Each debate agent produces a scoring table per proposal:

```markdown
## Proposal [A|B|C] Evaluation

### Complexity (30%)
| Criterion | Score | Confidence | Evidence |
|-----------|-------|------------|----------|
| CX-1 Implementation Size | XX | HIGH/MED/LOW | "Proposal states ~NNN lines in §Implementation Complexity" |
| CX-2 Pipeline Coupling | XX | ... | ... |
| ... | ... | ... | ... |
| **Subtotal** | **XX.X** | | |

### Efficiency (30%)
| ... |

### Efficacy (40%)
| ... |

### Total: XX.X / 100
```

---

## Tiebreaker Protocol

If top two proposals score within **5 points** of each other:

1. **First tiebreaker**: Higher Efficacy score wins (quality of adversarial outcomes matters most)
2. **Second tiebreaker**: Lower Complexity score wins (simpler is better when quality is equal)
3. **Third tiebreaker**: Debate agent consensus (which proposal did more agents rank first?)
4. **Fourth tiebreaker**: Lower migration risk (CX-4 score) wins

---

## Validation Checklist

- [ ] All 3 proposals scored on all 17 sub-criteria
- [ ] Every score has an evidence citation
- [ ] Anti-bias two-pass protocol followed
- [ ] No dimension has all-same scores across proposals (differentiation test)
- [ ] Confidence indicators provided for every sub-criterion
- [ ] Tiebreaker protocol ready if needed
