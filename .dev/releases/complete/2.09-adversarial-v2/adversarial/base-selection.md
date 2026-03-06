# Base Selection: sc:adversarial v2.0 Roadmap Merge

**Date**: 2026-03-04
**Convergence**: 79% (NOT_CONVERGED -- below 80% threshold)
**Selection method**: Score-based base selection from 3-round adversarial debate

---

## Scoring Summary

| ID | Dimension | Winner | Confidence | Key Rationale |
|----|-----------|--------|------------|---------------|
| X-001 | M4 dependency | V1 (opus) | 78% | CEGAR + parallelism; M4 depends on M1 only |
| X-002 | M5 dependency | V2 (haiku) | 62% | M5 requires M1+M3+M4-final; default path needs M3 |
| X-003 | M6 dependency | V1 (opus) | 71% | SRP + transitive M4 through M5 |
| S-001 | M4 DAG arc | V1 (opus) | 80% | M4 not gated by M3 |
| S-002 | M5 topology | V2 (haiku) | 62% | M5 gated by M3 in addition to M1+M4 |
| S-003 | M6 DAG | V1 (opus) | 71% | M6 depends on M3+M5 only |
| S-004 | Critical path | V1 (opus) | 75% | M1->M2->M3->M6 with M4 parallel |
| S-005 | M4/M5 ordering | Merged | 68% | Synthesis of both positions |
| S-006 | Deliverable count | V2 (haiku) | 73% | D3.4 + D6.4 additive deliverables |
| C-001 | DA lifecycle | V1 (opus) | 85% | Stateless within single run |
| C-002 | FME sequencing | Merged | 70% | Invariants-inform-FME with M3 fallback |
| C-003 | M6 scope | V1 (opus) | 74% | D6.4 provenance added but deps stay V1 |
| C-004 | SC style | Merged | 77% | Both adopted: quantitative + operational |
| C-005 | Overview framing | V2 (haiku) | 72% | Three control planes framework |

## Tally

| Outcome | Count | Points |
|---------|-------|--------|
| Variant 1 (opus:architect) wins | 7 | X-001, X-003, S-001, S-003, S-004, C-001, C-003 |
| Variant 2 (haiku:architect) wins | 4 | X-002, S-002, S-006, C-005 |
| Merged (neither) | 3 | S-005, C-002, C-004 |

## Decision

**Base variant: Variant 1 (opus:architect)**

Variant 1 wins 7 of 14 contested points versus 4 for Variant 2, with 3 requiring merged synthesis. Variant 1's dependency topology (parallel M4 branch), DA lifecycle specification, and quantitative success criteria provide the stronger structural foundation for the merged artifact.

Variant 2 contributions to be integrated into the base: three control planes framework (U-006), D3.4 divergence detector (U-007), D6.4 provenance tagging (U-008), DA severity taxonomy (U-009), R6 adoption friction (U-010), S8 operational sustainability (U-011), and the M5 dependency update (X-002).
