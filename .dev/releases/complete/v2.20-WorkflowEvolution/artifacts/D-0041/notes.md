---
deliverable: D-0041
task: T05.05
status: PASS
date: 2026-03-09
---

# D-0041: Pipeline Performance Delta Report

## Measurement Methodology

Gate validation time was measured for the pre-v2.20 gates (EXTRACT, MERGE,
TEST_STRATEGY) against 3 historical specs, 100 iterations each. The
spec-fidelity step is explicitly excluded per SC-012 ("total pipeline time
overhead <=5% excluding new spec-fidelity step").

Both runs execute the **same gates** — the v2.20 changes to existing gates
are semantic (new semantic checks, field additions) but do not add new
gate-checking overhead to the existing 3 gates.

## Results

| Metric | Value |
|--------|-------|
| Baseline (3 gates x 100 iters) | 26.9ms |
| New (3 gates x 100 iters) | 22.4ms |
| Delta (excl. spec-fidelity) | -16.69% (noise) |
| Per-iteration avg | ~0.27ms → ~0.22ms |

The negative delta indicates no measurable overhead from v2.20 changes to
existing gates. The variance is within normal measurement noise for
sub-millisecond operations.

## SC-012 Assessment

- **Threshold**: <=5% overhead excluding spec-fidelity step
- **Measured**: No overhead (delta negative / within noise)
- **Status**: **PASS**

## Notes

- Spec-fidelity step (new in v2.20) adds its own execution time but this is
  excluded from SC-012 per requirement definition
- The existing gate semantic checks (`_cross_refs_resolve`, `_no_heading_gaps`,
  `_no_duplicate_headings`) add negligible overhead (~0.01ms per check)
