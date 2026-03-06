# Variant 2 — Sonnet:backend (base candidate)

## Milestones
- M1 Enforce v1 spec promises first (classification map, coverage report, progress checkpoints, evidence-gated decisions, 10% consistency validation)
- M2 Correctness fixes (real .env scanning with safe redaction, gitignore drift detection, Phase-1 schema validation)
- M3 Infrastructure (audit-profiler, domain/tier assignment, monorepo-aware batching, static tool orchestration, auto-config + dry-run)
- M4 Depth improvements (8-field profiles, signal-triggered deep reads, 3-tier dependency detection, duplication matrix, minimal docs audit, INVESTIGATE cap)
- M5 Quality hardening (post-hoc dedup, resume semantics, report-depth modes, anti-lazy controls, failure handling)
- M6 Future extensions (full docs pass, known-issues registry, calibration baseline, progressive specialization)

## Risks & Mitigations
- Budget risk -> dry-run + degradation + benchmark calibration
- Ground truth risk -> static-tool-first dependency evidence
- Non-determinism risk -> consistency framing + calibration anchors
- Security leakage risk -> never print secrets, only presence flags

## AC Mapping
- M1: AC1-AC6, AC15
- M2: AC7-AC8, AC11
- M3: AC13, AC19, AC20
- M4: AC9, AC12, AC14, AC16, AC17
- M5: AC10, AC18
- M6: extension ACs to be defined