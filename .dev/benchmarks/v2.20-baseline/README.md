# v2.20 WorkflowEvolution — Pre-Release Benchmark Suite

**Purpose**: Establish baseline measurements for the 6 key findings identified in the forensic diagnostic (`forensic-foundation-validated.md`) BEFORE implementing v2.20 changes. Each test runs the real pipeline and produces quantifiable metrics that can be re-measured post-release.

**Sprint Scope**: v2.20 targets F-001 through F-006 — structural-only gates, confidence inflation, adversarial conclusion loss, mock-boundary exclusion, retrospective disconnect, and seam failures.

---

## Test Index

| # | Test Name | Findings Targeted | What It Measures |
|---|-----------|-------------------|------------------|
| 1 | Semantic Nonsense Gate Penetration | F-001, SC-007 | Whether structurally valid but semantically meaningless specs pass all gates |
| 2 | Adversarial Conclusion Preservation | F-003, F-006, SC-002 | Information loss rate at the adversarial→merge seam |
| 3 | Cross-Boundary Information Cascade | F-006, Evidence Chains 2+5 | Information density degradation across all 7 pipeline stages |
| 4 | Multi-Agent Validation Depth | F-001, F-002, validate pipeline | Whether validation catches planted structural-but-semantically-wrong defects |
| 5 | Gate False-Negative Stress Test | F-001, _cross_refs_resolve, _has_actionable_content | Gate pass rates against adversarial inputs designed to exploit known weaknesses |

---

## How to Run

Each test has its own script and scoring rubric. Run them in order:

```bash
# From repo root
cd /config/workspace/SuperClaude_Framework

# Test 1: Semantic Nonsense Gate Penetration
bash .dev/benchmarks/v2.20-baseline/test-1-nonsense-penetration.sh

# Test 2: Adversarial Conclusion Preservation
bash .dev/benchmarks/v2.20-baseline/test-2-adversarial-preservation.sh

# Test 3: Cross-Boundary Information Cascade
bash .dev/benchmarks/v2.20-baseline/test-3-information-cascade.sh

# Test 4: Multi-Agent Validation Depth
bash .dev/benchmarks/v2.20-baseline/test-4-validation-depth.sh

# Test 5: Gate False-Negative Stress Test
bash .dev/benchmarks/v2.20-baseline/test-5-gate-stress.sh
```

## Scoring

After each test, results are written to `.dev/benchmarks/v2.20-baseline/results/`. Post-release, the same tests are re-run and results compared. The comparison script produces a before/after delta report.

```bash
bash .dev/benchmarks/v2.20-baseline/compare-results.sh baseline post-release
```
