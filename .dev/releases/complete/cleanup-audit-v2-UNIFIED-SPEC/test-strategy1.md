---
spec_source: .dev/releases/current/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-22T00:00:00Z
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 5
work_milestones: 5
interleave_ratio: "1:1"
major_issue_policy: stop-and-fix
complexity_class: HIGH
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** -- the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop -- work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:1 (one validation milestone per one work milestone), derived from complexity class HIGH (score: 0.799)

**Rationale for 1:1 Interleave**: The sc:cleanup-audit v2 spec has deep inter-phase data dependencies (Phase 0→1→2→3→4), 63 requirements across 4 domains, and 18 identified risks including 7 High-probability/High-impact risks. Errors in early milestones propagate through all subsequent work. Catching issues after every work milestone prevents expensive cascading rework.

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (M2) | M1: Foundation & v1 Spec Enforcement | Two-tier classification, file risk tiers, evidence-gated DELETE/KEEP, coverage tracking, checkpointing, spot-check validation | Any AC1-AC6 failure; any v1 spec promise still unimplemented |
| V2 (M4) | M3: Correctness & Schema Hardening | Credential scanning accuracy, gitignore detection, Phase 1+2 schema compliance | Credential values appear in output; real credentials missed; schema validation not enforcing |
| V3 (M6) | M5: Infrastructure & Profiling | Profiler domain detection, tier assignment, manifest completeness, static tool orchestration, cold-start | Manifest does not cover 100% of git-tracked files; cold-start fails |
| V4 (M8) | M7: Deep Analysis & Cross-Reference Synthesis | 8-field profile accuracy, dependency graph validity, duplication matrices, broken reference detection | Known dead code files not flagged; dependency graph has zero nodes; budget exceeds 120% of phase allocation |
| V5 (M10) | M9: Quality, Budget Controls & Extensions | Budget compliance, graceful degradation, report depth, resume, anti-lazy enforcement, failure handling | Any of AC1-AC20 fails; budget exceeded by >10%; minimum viable report not generated on failure |

**Placement rule**: Validation milestones are placed after every 1 work milestone per the 1:1 interleave ratio. Each validation milestone references the specific work milestone it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Credential values exposed in output; evidence-gated classification not enforcing; schema validation bypassed |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Coverage target not met for Tier 1; checkpoint not updating; spot-check below 85% consistency |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Documentation gap in report sections; style inconsistency in JSON output; minor edge case in tier assignment |
| Info | Log only, no action required | N/A | Optimization opportunity for batch sizing; alternative approach for domain detection noted |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | AC1: Classification categories present; AC2: Coverage report exists; AC3: Checkpointing works; AC4: DELETE evidence; AC5: KEEP evidence; AC6: Validation sample | All 6 ACs pass; no credential values in any output |
| M3 | AC7: .env.production correctly classified; AC8: Gitignore flagging works; AC11: Scanner schema compliance | All 3 ACs pass; zero false negatives on known credentials |
| M5 | AC13: Cold-start succeeds; AC19: --dry-run produces estimates; Manifest covers 100% files | All 3 ACs pass; static tools detected where available |
| M7 | AC12: Dependency graph with nodes; AC14: Broken references in checklist; Profile accuracy on known files | All 3 ACs pass; budget consumption within 120% of phase allocation |
| M9 | AC9: Budget compliance; AC10: Report depth; AC15: Backward compat; AC16: Directory assessments; AC17: INVESTIGATE cap; AC18: Cascading failure; AC20: Run isolation | All 7 ACs pass; end-to-end test on 2+ real repositories |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (5-phase execution) | V5 | M10 | End-to-end test: all 5 phases execute in sequence |
| FR-002 (Two-tier classification) | V1 | M2 | Structural test: output contains >=2 primary classifications |
| FR-003 (Phase 0 profiler) | V3 | M6 | Property test: manifest covers 100% files; domains detected |
| FR-004 (Phase 1 surface scan) | V1, V3 | M2, M6 | Structural test: batch outputs exist; schema compliance |
| FR-005 (Credential scanning) | V2 | M4 | Property test: real creds flagged, templates not, values hidden |
| FR-006 (Gitignore check) | V2 | M4 | Property test: tracked-despite-gitignore files flagged |
| FR-007 (Phase 2 structural audit) | V4 | M8 | Property test: 8 fields populated for all profiled files |
| FR-011 (Phase 3 cross-ref) | V4 | M8 | Structural test: dependency-graph.json with nodes |
| FR-013 (Minimal docs audit) | V4 | M8 | Structural test: broken-references.json in checklist format |
| FR-015 (Phase 4 consolidation) | V5 | M10 | Structural test: FINAL-REPORT.md with all 13 sections |
| FR-016 (Spot-check validation) | V1 | M2 | Property test: >=10% sample, consistency rate computed |
| FR-018 (Coverage report) | V1 | M2 | Structural test: coverage-report.json with per-tier data |
| FR-019 (Budget control) | V5 | M10 | Property test: actual usage within --budget +/-10% |
| FR-020 (Graceful degradation) | V5 | M10 | Integration test: degradation activates at 90% allocation |
| FR-025 (Checkpointing) | V1 | M2 | Property test: progress.json updated after each batch |
| FR-031 (Cold-start) | V3 | M6 | Integration test: audit succeeds without config |
| FR-033 (Backward compat) | V1 | M2 | Property test: v2 output maps to v1 categories |
| FR-036 (File risk tiers) | V1 | M2 | Property test: all files assigned Tiers 1-4 |
| FR-037 (Evidence-mandatory KEEP) | V1 | M2 | Property test: Tier 1-2 KEEP has import references |
| FR-038 (Scanner schemas) | V2 | M4 | Structural test: all outputs validate against schema |
| NFR-001 (500K budget default) | V5 | M10 | Integration test: default budget applied when no --budget |
| NFR-010 (Read-only operation) | V5 | M10 | Property test: no file modifications in target repo |
| NFR-011 (Credential protection) | V2 | M4 | Property test: grep for credential patterns returns 0 |
| NFR-012 (Run isolation) | V5 | M10 | Integration test: concurrent runs produce separate dirs |

## Test Tiers (from Spec Section 15)

### Tier 1: Structural Tests
- Output files exist (FINAL-REPORT.md, coverage-report.json, validation-results.json, progress.json)
- JSON outputs parse correctly
- Required sections present in FINAL-REPORT.md (all 13 sections)
- Schema fields populated in scanner outputs

### Tier 2: Property Tests
- Coverage percentages within valid range (0-100%)
- No credential values appear in any output file
- All Tier 1 files examined (100% coverage)
- INVESTIGATE <= 15% of examined files
- Evidence non-empty for DELETE and Tier 1-2 KEEP
- Confidence values in [0.0, 1.0] range

### Tier 3: Benchmark Tests
- Run against 2-3 real repositories with known characteristics
- One small repo (~100 files), one medium (~1000 files), one with known dead code
- Verify known dead code files are flagged
- Measure token consumption per phase
- Compare measured budget to spec estimates (document delta for calibration)
