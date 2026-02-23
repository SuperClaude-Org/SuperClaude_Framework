---
spec_source: .dev/releases/current/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-22T17:50:00Z
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

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:1 (one validation milestone per 1 work milestone), derived from complexity class HIGH (score: 0.814)

**Anti-Gap Enforcement**: The spec's CRITICAL risk is spec-implementation gap recurrence. Every validation gate includes a spec compliance check (not just functional testing). The pattern established at M2 (compliance matrix) recurs at M4, M6, M8, and M10.

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (M2) | M1: V1 Spec Enforcement & Baseline | v1 compliance: 5-category classification, coverage tracking, checkpointing, evidence-gated classification, 10% spot-check | Any v1 spec requirement fails compliance matrix → stop. Checkpoint recovery test fails → stop. Coverage manifest misses files → stop. |
| V2 (M4) | M3: Correctness Fixes & Scanner Schema | Credential scanning accuracy, gitignore exclusion, schema enforcement, schema rejection robustness | Credential detection rate < 90% → stop. Schema validator accepts malformed output → stop. Gitignore classified files that should be excluded → stop. |
| V3 (M6) | M5: Infrastructure: Profiling, Batching, Classification | Profiling accuracy, batch decomposition, classification migration, budget system, 5K-file scale test | Profiling accuracy < 85% → stop. Any file not assigned to batch → stop. Classification migration introduces category errors → stop. Budget exhaustion test fails to degrade gracefully → stop. 5K stress test reveals memory exhaustion → stop. |
| V4 (M8) | M7: Depth: Evidence Tiers, Cross-Ref, Budget Controls | Evidence tier compliance, cross-reference accuracy, file-type rules, anti-lazy enforcement, 8K-file scale test | Tier 1 KEEP missing evidence fields → stop. Zero-reference files not flagged → stop. Anti-lazy detection fails to catch identical justifications → stop. 8K test reveals performance cliff → stop (document and remediate). |
| V5 (M10) | M9: Quality Polish: Dedup, Resume, Anti-Lazy | Full system integration, resume robustness, 10K-file scale, v2 spec compliance matrix, Phase 5 readiness | Resume produces different output than non-interrupted run → stop. v2 compliance matrix has fails → stop. 10K-file test reveals blockers → stop (document limitation). |

**Placement rule**: Validation milestones are placed after every 1 work milestone per the 1:1 interleave ratio (HIGH complexity class). Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Spec compliance matrix failure, credential value exposure, schema validation bypass, evidence-gated classification bypass |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing evidence fields on Tier 1 KEEP, classification migration errors, budget tracking inaccuracy >10%, anti-lazy detection failure |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Documentation gap, inconsistent qualifier usage, token budget estimation off by 20-50%, non-critical report formatting issues |
| Info | Log only, no action required | N/A | Optimization opportunity, alternative approach noted, performance improvement suggestion, Phase 5 extension idea |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 (V1 Enforcement) | D1.1-D1.5 acceptance criteria met: 5-category classification, coverage tracking, checkpointing, evidence-gated classification, 10% spot-check | All deliverable ACs met. Spec compliance matrix 100% pass. No Critical/Major issues. |
| M2 (V1 Gate) | D2.1-D2.4: compliance matrix, reference repo test, coverage validation, checkpoint recovery | Agreement rate ≥ 80% on category. Coverage 100%. Checkpoint recovery produces identical output. |
| M3 (Correctness) | D3.1-D3.5: credential scanning, gitignore check, scanner schema, schema validation, credential config | Detection rate ≥ 90%. False positive rate ≤ 20%. 100% schema compliance. NEVER print credential values. |
| M4 (Correctness Gate) | D4.1-D4.4: credential accuracy, schema rejection, gitignore audit, end-to-end compliance | All schema test cases pass. All gitignore edge cases handled. |
| M5 (Infrastructure) | D5.1-D5.6: profiling, batching, classification system, coverage manifest, budget tracking, .env matrix | Profile < 60s. 100% file batch coverage. Budget degradation sequence works. |
| M6 (Infra Gate) | D6.1-D6.5: profiling accuracy, batch validation, classification migration, budget exhaustion, 5K scale | 3 reference repos validated. Budget thresholds fire correctly. 5K scale completes. |
| M7 (Depth) | D7.1-D7.6: evidence tiers, cross-ref, file-type rules, depth escalation, minimal docs audit, directory assessment | Tier 1-2 evidence compliance 100%. dependency-graph.json produced. broken-references.json in checklist format. |
| M8 (Depth Gate) | D8.1-D8.5: evidence compliance, cross-ref accuracy, file-type compliance, anti-lazy enforcement, 8K scale | Zero-reference files detected. Anti-lazy catches identical justifications. 8K scale completes. |
| M9 (Quality) | D9.1-D9.5: dedup, resume, report depth, enhanced anti-lazy, degradation priority | Resume idempotent. Report depth levels within bounds. INVESTIGATE cap enforced. |
| M10 (Final Gate) | D10.1-D10.5: v2 compliance matrix, integration test, 10K scale, Phase 5 readiness, gap prevention report | All 20 acceptance criteria from spec Section 15 verified. 10K scale documented. |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (5-phase execution) | V5 (M10) | M10 | End-to-end integration test: all 5 phases execute on reference repos |
| FR-002 (6-agent system) | V3 (M6) | M5-M6 | Agent profiler, scanner operational. Full agent system integration in M10 |
| FR-003 (Phase 1 schema) | V2 (M4) | M3-M4 | Schema rejection test suite: 15+ malformed inputs, 100% rejected |
| FR-004 (Phase 2 8-field profile) | V4 (M8) | M7-M8 | Evidence tier compliance test: all profiled files have 8 fields |
| FR-005 (4-primary classification) | V3 (M6) | M5-M6 | Classification migration test: v1→v2 mapping validated |
| FR-006 (Risk tiers) | V3 (M6) | M5-M6 | Coverage manifest validation: per-tier tracking with targets |
| FR-007 (Phase 0 profiling) | V3 (M6) | M5-M6 | Profiling accuracy test: 3 reference repos |
| FR-008 (Hybrid architecture) | V4 (M8) | M7-M8 | Cross-reference accuracy: static tools vs grep vs LLM compared |
| FR-009 (Phase 1 scanning) | V1 (M2) | M1-M2 | Full audit run against reference repo |
| FR-010 (Credential scanning) | V2 (M4) | M3-M4 | 20 seeded credentials, 10 false-positive traps |
| FR-011 (Gitignore check) | V2 (M4) | M3-M4 | Complex .gitignore edge cases (nested, negation, directory-only) |
| FR-012 (Phase 2 structural audit) | V4 (M8) | M7-M8 | File-type-specific rules compliance test |
| FR-013 (Depth escalation) | V4 (M8) | M7-M8 | Signal-triggered escalation validated against known triggers |
| FR-014 (.env key matrix) | V3 (M6) | M5-M6 | Matrix generated for multi-.env test repo |
| FR-015 (Phase 3 cross-ref) | V4 (M8) | M7-M8 | dependency-graph.json with labeled edges (A/B/C) |
| FR-016 (Dependency graph) | V4 (M8) | M7-M8 | Orphan detection: seeded zero-reference files detected |
| FR-017 (Duplication matrix) | V4 (M8) | M7-M8 | Groups with >70% overlap identified |
| FR-018 (Minimal docs audit) | V4 (M8) | M7-M8 | broken-references.json in checklist format |
| FR-019 (Post-hoc dedup) | V5 (M10) | M9-M10 | Dedup summary: X merged into Y, cost ~500 tokens |
| FR-020 (Dynamic import detection) | V4 (M8) | M7-M8 | Dynamic import patterns detected, KEEP:monitor applied |
| FR-021 (Phase 4 consolidation) | V5 (M10) | M9-M10 | FINAL-REPORT.md generated with all required sections |
| FR-022 (10% spot-check) | V1 (M2) | M1-M2 | validation-results.json with ≥10% sample |
| FR-023 (Coverage report) | V3 (M6) | M5-M6 | coverage-report.json with per-tier PASS/WARN/FAIL |
| FR-024 (Directory assessment) | V4 (M8) | M7-M8 | 50+ file directories have assessment labels |
| FR-025 (FINAL-REPORT.md) | V5 (M10) | M9-M10 | All required sections present per spec Section 9 |
| FR-026 (Budget system) | V3 (M6) | M5-M6 | Budget exhaustion test: 50K on medium repo |
| FR-027 (Graceful degradation) | V3 (M6) | M5-M6 | Degradation sequence activates in correct order |
| FR-028 (CLI flags) | V5 (M10) | M9-M10 | All flags operational in integration test |
| FR-029 (Report depth) | V5 (M10) | M9-M10 | summary < 100 lines, detailed includes profiles |
| FR-030 (Checkpointing) | V1 (M2) | M1-M2 | Checkpoint recovery: kill at 50%, resume identical |
| FR-031 (Resume) | V5 (M10) | M9-M10 | 5-scenario resume: 25%, 50%, 75%, 90%, budget exhaustion |
| FR-032 (Full docs audit) | Phase 5 (future) | — | Extension point documented in M10 readiness assessment |
| FR-033 (Within-run dedup) | V5 (M10) | M9-M10 | Dedup in consolidator phase |
| FR-034 (Known-issues registry) | Phase 5 (future) | — | Extension point documented in M10 readiness assessment |
| FR-035 (Cold-start config) | V3 (M6) | M5-M6 | Audit succeeds without pre-existing config |
| FR-036 (--dry-run) | V3 (M6) | M5-M6 | Dry-run produces estimates without executing scans |
| FR-037 (Monorepo detection) | V3 (M6) | M5-M6 | Workspace file detected, per-workspace batching |
| FR-038 (Backward compat) | V3 (M6) | M5-M6 | v2 output mappable to v1 categories |
| FR-039 (INVESTIGATE cap) | V5 (M10) | M9-M10 | >15% triggers re-analysis |
| FR-040 (Subagent failure) | V5 (M10) | M9-M10 | 3 consecutive failures → pause + minimum viable report |
| FR-041 (Anti-lazy) | V4 (M8) | M8 | Uniqueness check, distribution sanity, confidence calibration |
| FR-042 (Run isolation) | V5 (M10) | M9-M10 | Concurrent runs produce separate directories |
| FR-043 (Evidence-gated) | V1 (M2) | M1-M2 | DELETE has grep proof, Tier 1-2 KEEP has import info |
| FR-044 (Schema validation) | V2 (M4) | M3-M4 | Non-conforming output triggers retry, then FAILED |
| FR-045 (Degradation priority) | V5 (M10) | M9-M10 | --degrade-priority flag produces different degradation |
| NFR-001 (500K budget) | V3 (M6) | M5-M6 | Budget tracking accurate within ±10% |
| NFR-007-010 (Coverage targets) | V3 (M6) | M5-M6 | Per-tier targets tracked in coverage-report.json |
| NFR-011 (Consistency rate ≥85%) | V1 (M2), V5 (M10) | M1, M10 | Spot-check reports consistency rate |
| NFR-012 (INVESTIGATE ≤15%) | V5 (M10) | M9-M10 | Cap enforced with re-analysis trigger |
| NFR-016 (Read-only) | V5 (M10) | M10 | No file modifications in any audit run |
| NFR-017 (Never print credentials) | V2 (M4) | M3-M4 | Output scanning for credential patterns |

## Test Tiers

Per spec Section 15, tests are organized in three tiers:

### Tier 1: Structural Tests
- Output files exist (FINAL-REPORT.md, coverage-report.json, validation-results.json, phase outputs)
- JSON is valid (all .json outputs parse without error)
- Required sections present in FINAL-REPORT.md (per spec Section 9)
- Schema fields populated (per Phase 1 and Phase 2 schemas)
- YAML frontmatter valid in all artifacts

### Tier 2: Property Tests
- Coverage percentages within range (Tier 1 ≥ 100%, Tier 2 ≥ 90%, etc.)
- No credential values appear in any output file
- All Tier 1 files examined (never skipped by graceful degradation)
- INVESTIGATE ≤ 15% of examined files
- Budget consumption within ±10% of --budget
- Evidence non-empty for all DELETE and Tier 1-2 KEEP classifications

### Tier 3: Benchmark Tests
- Run against 2-3 real repositories with known characteristics:
  - Small (< 100 files): verify all files classified
  - Medium (500-2K files): verify budget tracking, degradation
  - Large (5K-10K files): verify scaling behavior, checkpoint/resume
- Verify known dead code files are flagged as DELETE or INVESTIGATE
- Measure token consumption per phase (calibration data for budget defaults)
- Compare classification distribution against expected baseline
