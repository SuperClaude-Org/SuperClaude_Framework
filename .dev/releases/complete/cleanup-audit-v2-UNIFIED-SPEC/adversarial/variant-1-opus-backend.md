# Variant 1 — Opus:backend

## Milestones
- M1 Spec compliance baseline (classification, coverage, checkpointing, evidence gates, spot-check)
- M2 Correctness fixes (credential scanning, gitignore consistency, scanner schema)
- M3 Infrastructure (profiling, batch manifest, static tools, auto-config, dry-run)
- M4 Depth (phase2 profiles, cross-reference graph, minimal docs audit, INVESTIGATE cap)
- M5 Quality/polish (dedup, report-depth, resume, anti-lazy)
- M6 Extensions (full docs pass, known-issues registry, calibration)

## Key Risks
1. Token budget underestimation
2. Spec-implementation gap recurrence
3. Schema malformation in Phase 1
4. Dynamic import false positives
5. Auto-config tier misclassification
6. Large repo scaling
7. Context-window pressure in Phase 3/4
8. Credential exposure risk

## Success Criteria
Map AC1-AC20 across M1-M6 with structural/property/benchmark verification.