---
spec_source: .dev/releases/current/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-22T17:45:00Z
generator: sc:roadmap
complexity_score: 0.814
complexity_class: HIGH
domain_distribution:
  frontend: 0
  backend: 44
  security: 18
  performance: 22
  documentation: 16
primary_persona: architect
consulting_personas: [backend, security]
milestone_count: 10
milestone_index:
  - id: M1
    title: "V1 Spec Enforcement & Baseline"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 5
    risk_level: High
    effort: L
  - id: M2
    title: "V1 Compliance Validation Gate"
    type: TEST
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Medium
    effort: M
  - id: M3
    title: "Correctness Fixes & Scanner Schema"
    type: FEATURE
    priority: P0
    dependencies: [M2]
    deliverable_count: 5
    risk_level: High
    effort: L
  - id: M4
    title: "Correctness & Schema Validation Gate"
    type: TEST
    priority: P0
    dependencies: [M3]
    deliverable_count: 4
    risk_level: Medium
    effort: M
  - id: M5
    title: "Infrastructure: Profiling, Batching, Classification"
    type: FEATURE
    priority: P1
    dependencies: [M4]
    deliverable_count: 6
    risk_level: High
    effort: XL
  - id: M6
    title: "Infrastructure Validation Gate"
    type: TEST
    priority: P1
    dependencies: [M5]
    deliverable_count: 5
    risk_level: High
    effort: L
  - id: M7
    title: "Depth: Evidence Tiers, Cross-Ref, Budget Controls"
    type: FEATURE
    priority: P1
    dependencies: [M6]
    deliverable_count: 6
    risk_level: High
    effort: XL
  - id: M8
    title: "Depth & Budget Validation Gate"
    type: TEST
    priority: P1
    dependencies: [M7]
    deliverable_count: 5
    risk_level: High
    effort: L
  - id: M9
    title: "Quality Polish: Dedup, Resume, Anti-Lazy"
    type: IMPROVEMENT
    priority: P2
    dependencies: [M8]
    deliverable_count: 5
    risk_level: Medium
    effort: L
  - id: M10
    title: "Final Integration & Scale Validation Gate"
    type: TEST
    priority: P2
    dependencies: [M9]
    deliverable_count: 5
    risk_level: Medium
    effort: M
total_deliverables: 50
total_risks: 18
estimated_phases: 5
validation_score: 0.88
validation_status: PASS
validation_details:
  quality_engineer: 88.6
  self_review: 88.1
  aggregation: "QE*0.55 + SR*0.45 = 88.375"
  threshold: 85.0
adversarial:
  mode: multi-roadmap
  agents: ["opus:architect", "haiku:architect"]
  convergence_score: 0.78
  base_variant: "opus:architect"
  artifacts_dir: .dev/releases/current/v2.1-CleanupAudit-v2/adversarial/
---

# Roadmap: sc:cleanup-audit v2 — Multi-Phase Read-Only Repository Audit

## Overview

This roadmap implements sc:cleanup-audit v2 as specified in the unified specification (2.0-UNIFIED), replacing an underperforming v1 that achieved only 12 file profiles from 5,857 files (99.8% miss rate). The implementation follows 10 milestones in a strictly sequential dependency chain with 1:1 validation interleaving (HIGH complexity class), ensuring that no milestone begins until its predecessor's validation gate passes.

The roadmap was generated via multi-roadmap adversarial synthesis (opus:architect vs haiku:architect). The opus variant's emphasis on architectural correctness and spec-implementation gap prevention was selected as the base, augmented by the haiku variant's progressive scale testing (5K→8K→10K files) and efficient phase consolidation strategies. Key synthesis decisions are documented in the Decision Summary.

The single most important constraint: **all v1 spec promises must be implemented before any new features** (spec Section 14, Phase 0). This roadmap enforces that constraint through M1-M2 before proceeding to v2-specific capabilities.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | V1 Spec Enforcement & Baseline | FEATURE | P0 | L | None | 5 | High |
| M2 | V1 Compliance Validation Gate | TEST | P0 | M | M1 | 4 | Medium |
| M3 | Correctness Fixes & Scanner Schema | FEATURE | P0 | L | M2 | 5 | High |
| M4 | Correctness & Schema Validation Gate | TEST | P0 | M | M3 | 4 | Medium |
| M5 | Infrastructure: Profiling, Batching, Classification | FEATURE | P1 | XL | M4 | 6 | High |
| M6 | Infrastructure Validation Gate | TEST | P1 | L | M5 | 5 | High |
| M7 | Depth: Evidence Tiers, Cross-Ref, Budget Controls | FEATURE | P1 | XL | M6 | 6 | High |
| M8 | Depth & Budget Validation Gate | TEST | P1 | L | M7 | 5 | High |
| M9 | Quality Polish: Dedup, Resume, Anti-Lazy | IMPROVEMENT | P2 | L | M8 | 5 | Medium |
| M10 | Final Integration & Scale Validation Gate | TEST | P2 | M | M9 | 5 | Medium |

## Dependency Graph

```
M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9 → M10
```

All milestones are strictly sequential. No milestone begins until its predecessor's validation gate passes. This is intentional — the cost of rework from building on an unvalidated foundation exceeds the cost of sequential delivery. The spec's CRITICAL risk (spec-implementation gap recurrence) demands this discipline.

---

## M1: V1 Spec Enforcement & Baseline

### Objective

Implement all v1 spec promises that were never delivered: 5-category classification, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check validation. No new features — only compliance with the existing contract.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | 5-category classification enforcement via backward-compatible two-tier mapping (DELETE→DELETE:standard, CONSOLIDATE→MODIFY:consolidate-with, MOVE→MODIFY:move-to, FLAG→MODIFY:flag, KEEP→KEEP:verified/unverified) | All agent outputs use the two-tier classification system. Backward compatibility mapping validated against v1 test outputs. |
| D1.2 | Coverage tracking manifest (JSON) listing every git-tracked file with classification status (classified/skipped/errored) and responsible agent | Manifest accounts for 100% of `git ls-files` output. Zero unaccounted files. |
| D1.3 | Checkpointing mechanism: progress.json updated after each batch with current_phase, batches_completed, batches_total, files_examined, files_total, token_usage, token_budget, timestamp | Crashed run resumes from last checkpoint without re-processing completed batches. |
| D1.4 | Evidence-gated classification: DELETE requires grep proof with result count 0; Tier 1-2 KEEP requires import reference information; all classifications include evidence_text field | Classifications missing required evidence are rejected by post-processing validator. |
| D1.5 | 10% spot-check validation: stratified random sample re-evaluated by independent agent pass, reported as "consistency rate" (not accuracy) | validation-results.json emitted with sample size ≥ 10%. Report states limitation: "consistency measures model-to-model agreement, not ground-truth accuracy." |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| V1 spec ambiguity — underspecified behaviors require interpretation, leading to subjective compliance | Medium | High | Document every interpretation decision in `v1-spec-interpretations.md`. Each interpretation reviewed in M2 validation gate. |
| Auto-config cascading errors — Phase 0 auto-configuration produces incorrect profiles that silently corrupt downstream classification (RISK-009) | High | High | Auto-config outputs logged verbosely. Validated against known-good profile for test repository. Divergence halts run with explicit error. |

---

## M2: V1 Compliance Validation Gate

### Objective

Answer with evidence: "Does the implementation now match the v1 spec?" If no, M3 does not begin. This establishes the anti-gap pattern enforced at every subsequent gate.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Spec compliance matrix mapping every v1 spec requirement to implementation location (file, function, line range) with pass/fail status | 100% of requirements have entries. 100% pass. |
| D2.2 | Test run against reference repository: full audit against repo of known characteristics, output compared against manually-curated expected classifications | Agreement rate ≥ 80% on category, ≥ 70% on evidence quality. |
| D2.3 | Coverage report validation: manifest verified to account for 100% of reference repo files | Any file marked skipped/errored has explicit documented reason. |
| D2.4 | Checkpoint recovery test: run killed at 50% progress, resumed from checkpoint, output compared to non-interrupted run | Final output identical (modulo timestamps) to non-interrupted run. |

### Dependencies

- M1: V1 Spec Enforcement & Baseline

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False compliance — tests too lenient, implementation passes despite spec drift | Medium | High | At least 3 negative test cases per requirement. Inputs that should fail classification, trigger warnings, or be rejected. |

---

## M3: Correctness Fixes & Scanner Schema

### Objective

Address known correctness deficiencies: credential scanning (wrong answers on .env.production), gitignore inconsistency detection, and standardized scanner output schemas. These are correctness issues, not enhancements.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Credential file scanning: priority-ordered .env enumeration (.env.production → .env.prod → .env → .env.local → .env.staging → .env.test), real vs template pattern detection, configurable pattern list, NEVER print credential values | .env.production with real credentials correctly flagged. Template files (.env.example) not flagged. Disclaimer included: "Not a security audit substitute." |
| D3.2 | Gitignore consistency check: compare git ls-files against .gitignore patterns, flag tracked-but-ignored files | Tracked files matching .gitignore patterns flagged as MODIFY:flag:gitignore-inconsistency. |
| D3.3 | Standardized Phase 1 scanner schema (simplified for Haiku): scanner_id, domain, batch_id, files_assigned, files_examined, per-file path/risk_tier/classification/evidence_text/credential_scan | Runtime validator rejects non-conforming outputs. All scanner outputs conform. |
| D3.4 | Schema validation with retry: scanners producing non-conforming output trigger validation error, orchestrator retries batch once, then marks FAILED in coverage manifest | Retry logic handles malformed Haiku JSON. FAILED batches tracked in coverage manifest. |
| D3.5 | Credential pattern configuration: configurable pattern list via audit.config.yaml for new credential formats beyond defaults (sk-*, ghp_*, AKIA*, sk-ant-*, base64 >40 chars, BEGIN RSA PRIVATE KEY) | Custom patterns in audit.config.yaml detected and applied. |

### Dependencies

- M2: V1 Compliance Validation Gate (passed)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM schema non-compliance — Haiku scanners produce malformed JSON despite explicit instructions (RISK-004) | Medium | Medium | Three-layer defense: (1) Schema in agent system prompt with examples, (2) Post-generation runtime validator, (3) Auto-retry with validation error fed back (max 2 retries, then FAILED). Simplified Phase 1 schema reduces Haiku malformation risk. |
| Credential scanner false positives — overly aggressive patterns flag test fixtures or documentation examples | Medium | Medium | Template pattern exclusion list (CHANGE_ME_*, YOUR_*_HERE, etc.). Allowlist mechanism via audit.config.yaml. Confidence scoring on matches. |

---

## M4: Correctness & Schema Validation Gate

### Objective

Validate that correctness fixes work and schema enforcement is robust against adversarial inputs (malformed LLM outputs, edge-case file types, unusual credential patterns).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Credential scan accuracy: test repo seeded with 20 known credentials (various formats) and 10 false-positive traps (hashed values, documentation examples) | Detection rate ≥ 90% (18/20). False positive rate ≤ 20% (≤ 2/10 traps flagged). |
| D4.2 | Schema rejection test suite: 15+ test cases of malformed agent output (missing fields, wrong types, invalid enums, empty evidence) | 100% rejected by validator. 0% false rejections on valid output. |
| D4.3 | Gitignore exclusion audit: repo with complex .gitignore (nested ignores, negation patterns, directory-only patterns) | Zero classified files that should be excluded. Zero excluded files that should be classified. |
| D4.4 | End-to-end schema compliance run: full audit of reference repo | 100% of outputs conform to schema. All retries succeed or produce explicit FAILED entries. |

### Dependencies

- M3: Correctness Fixes & Scanner Schema

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Schema too rigid — rejects valid but unexpected LLM outputs containing useful non-standard fields | Low | Medium | Phase 1 schema simplified to essential fields only. Complex structured fields (import_references, export_targets) deferred to Phase 2 Sonnet schema. |

---

## M5: Infrastructure — Profiling, Batching, Classification

### Objective

Implement the three pillars of v2 infrastructure: repository profiling (understanding what you're auditing), intelligent batch decomposition (domain-aware scanning with explicit file lists), and the unified 4-primary classification system with 14 qualifiers.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | Repository profiling engine (Phase 0 audit-profiler agent, Haiku): domain detection, file risk tier classification, static analysis tool detection (madge, pydeps, ts-prune, cargo-deps), framework detection from package.json/requirements.txt/Cargo.toml | Profile generation completes in <60s. Detected domains match manual classification ≥ 85%. Static tool availability correctly detected. |
| D5.2 | Batch decomposition engine: domain-aware batches with explicit file lists, configurable batch size (default from profile), batch manifest JSON with scanner assignments | Every file in repo appears in exactly one batch. No batch exceeds configured size. Domain grouping accuracy ≥ 70%. |
| D5.3 | Unified 4-primary classification system: DELETE/KEEP/MODIFY/INVESTIGATE with 14 secondary qualifiers. Backward compatibility mapping from v1 categories. | All qualifiers from spec Section 5 implemented. Backward compat mapping validated. Classification outputs use Primary:Qualifier format. |
| D5.4 | Coverage manifest v2: per-tier tracking with PASS/WARN/FAIL status, evidence depth achieved per tier, unexamined files accounting | coverage-report.json exists with per-tier percentages. Tier 1 coverage ≥ 100%, Tier 2 ≥ 90% (initial targets). |
| D5.5 | Token budget tracking system: --budget flag (default 500K), phase allocation (5%/25%/35%/20%/15%), graceful degradation sequence when budget pressure activates | Budget tracked per phase. Degradation activates at 90% allocation. Never cuts: Phase 0 profiling, Phase 1 Tier 1-2, Phase 4 consolidation. |
| D5.6 | .env key-presence matrix: extract keys across .env* templates, output key-presence matrix showing configuration drift | Matrix generated when multiple .env* files detected. Keys with zero codebase references flagged. ~2K token cost. |

### Dependencies

- M4: Correctness & Schema Validation Gate (passed)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Budget estimation inaccuracy — repo profiling underestimates token costs, 500K may be 4-7x too low for comprehensive coverage (RISK-001) | High | High | Conservative estimation with 1.5x safety factor. Warnings at 70%/90%. Graceful degradation sequence. --dry-run for cost preview. Post-run actual-vs-predicted analysis for calibration. |
| Classification category migration — moving from v1 5-category to v2 4-primary + qualifiers causes confusion or incorrect mappings (RISK-007) | Medium | High | Explicit backward compatibility mapping table. REVIEW→INVESTIGATE:human-review-needed. Migration validated against reference repo in M6. |

---

## M6: Infrastructure Validation Gate

### Objective

Validate profiling accuracy, batching correctness, classification migration fidelity, and budget system behavior. Includes progressive scale testing (5K files) adopted from haiku variant.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Profiling accuracy test across 3 reference repos (small <100 files, medium 500-2K, large 5K-10K) | Language detection ≥ 95%. File count = 100%. Framework detection ≥ 85%. Profile generation < 60s for all three. |
| D6.2 | Batch decomposition validation: every file in repo in exactly one batch, no batch exceeds size, token predictions within 2x of actual | 100% file coverage. Batch size constraints met. Token prediction accuracy validated. |
| D6.3 | Classification migration test: v1 and v2 run against same repo, migration report produced | No file changes category inappropriately due to 5-to-4 migration. Qualifier distribution reasonable (no single qualifier on >50% of files). |
| D6.4 | Budget exhaustion test: deliberately low budget (50K tokens) against medium repo | 70% and 90% warnings fire at correct thresholds. Graceful degradation activates correctly. Run terminates gracefully with partial results. Unprocessed files listed. |
| D6.5 | 5K-file scale stress test (from haiku variant) | Profiling completes in <60s. Batching completes in <10s. No memory exhaustion. Checkpoint/resume works correctly mid-run. |

### Dependencies

- M5: Infrastructure

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scaling past 10K files — spec identifies system does not scale linearly past ~10K (RISK-006, NFR-018) | High | High | 5K stress test surfaces issues before they hit production. If issues found, documented as known limitations with remediation plan. |
| Monorepo detection failure — workspace boundaries not correctly identified, batches cross workspace lines (RISK-006) | Medium | Medium | Test against repo with workspace file (package.json workspaces). Verify per-workspace batch decomposition. |

---

## M7: Depth — Evidence Tiers, Cross-Ref, Budget Controls

### Objective

Add the depth that differentiates v2 from v1: mandatory evidence for high-tier KEEP classifications, cross-reference analysis using the 3-tier detection strategy (static tools > grep > LLM), file-type-specific verification rules, signal-triggered depth escalation, and minimal docs audit.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | Evidence-mandatory KEEP for Tier 1-2: full 3-field evidence for Tier 1 (references + recency + test_file_exists), 1-field mandatory + 2-field target for Tier 2. Tier 3-4 get minimum one-line annotation. | 100% of Tier 1-2 KEEP classifications include required evidence fields. Classifications with missing evidence demoted to INVESTIGATE:insufficient-evidence. |
| D7.2 | 3-tier cross-reference analysis: Tier A (static tools — madge/pydeps/ts-prune output), Tier B (grep-based import/require patterns), Tier C (LLM-inferred relationships). All edges carry confidence tier label. | dependency-graph.json produced with node count > 0. Edges labeled A/B/C. Orphan nodes (0 incoming edges + Tier A/B evidence) → DELETE:standard candidates. Tier C only → INVESTIGATE:cross-boundary. |
| D7.3 | File-type-specific verification rules: test files (pytest patterns, skip markers), deploy scripts (port validation, destructive ops), Docker/Compose (service comparison), config/env (real vs template detection), documentation (3 structural claims checked for Tier 1-2 docs) | Rules configurable via audit.config.yaml. Each file type has ≥ 3 rules. |
| D7.4 | Signal-triggered depth escalation: default 50-line read, full-file triggers for credential-adjacent imports, TODO/FIXME/HACK, complex conditionals (>3 nested), eval/exec, file size > 300 lines | Triggers configurable. Escalation logged. Token cost of escalation tracked against budget. |
| D7.5 | Minimal docs audit (core flow, Phase 3): broken reference sweep (extract relative links from .md files, verify targets exist), temporal artifact classification (KEEP/DELETE:archive-first/DELETE:standard). Checklist output format. | broken-references.json produced with checklist format: `- [ ] filepath:line -> missing/path`. Budget: 5-8% of total. |
| D7.6 | Directory-level assessment blocks for directories with 50+ files: sample list (10 representative files), assessment label (actively-maintained/stale/bulk-dump/mixed), recommendation | Directories with 50+ files have assessment labels in FINAL-REPORT.md. |

### Dependencies

- M6: Infrastructure Validation Gate (passed)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cross-reference false negatives — static analysis cannot detect dynamic imports, reflection, string-based module loading, framework magic (RISK-003) | High | High | Cross-ref results are advisory. Tier C evidence → INVESTIGATE:cross-boundary only. Dynamic import detection pattern list (configurable). Files referenced only via dynamic import → KEEP:monitor (not DELETE). |
| Context window filling — Phase 3 cross-ref requires reading large volumes of prior phase output, token-intensive (RISK-017) | High | Medium | Write-to-disk architecture. Budget allocation reserves 20% for Phase 3. Graceful degradation: skip cross-ref as third cut if budget pressure. |

---

## M8: Depth & Budget Validation Gate

### Objective

Validate evidence tiers, cross-references, and file-type rules under pressure (high file counts, low budgets, edge-case file types). Anti-lazy enforcement validated here (from opus variant emphasis).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D8.1 | Evidence tier compliance: all Tier 1 KEEP have 3-field evidence, all Tier 2 KEEP have 1-field mandatory | 100% compliance. No tier misclassification to avoid evidence requirements. |
| D8.2 | Cross-reference accuracy: reference repo seeded with 10 files of known reference counts (3 with zero references) | Tier 1 reference counts within 20% of actual. All 3 zero-reference files receive potentially-unused/DELETE:standard signal. No file with >5 references flagged as unused. |
| D8.3 | File-type rules compliance: reference repo includes test files, config files, generated files, lock files, documentation | Each receives type-specific treatment. No test file classified DELETE. Generated files flagged with qualifier. Lock files always KEEP. |
| D8.4 | Anti-lazy enforcement: evidence string uniqueness check (>30% identical justifications within batch → re-review), evidence length minimums, confidence calibration against evidence depth | Lazy batches detected and flagged. Confidence distribution anomaly detection active (>90% identical values → re-review). |
| D8.5 | 8K-file progressive scale test (from haiku variant) | Full audit on 8K-file repo completes. Budget tracking accurate. Checkpoint/resume works. Performance degradation from 5K documented. |

### Dependencies

- M7: Depth

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Agent laziness under budget pressure — LLM agents produce superficial evidence or copy-paste justifications (RISK-015) | High | High | Runtime anti-lazy detection: uniqueness check, length minimums, confidence calibration. Lazy outputs rejected and re-processed during the run, not post-hoc. |
| Run-to-run non-determinism — two runs on same repo may disagree, undermining validation (RISK-016) | Medium | Medium | Grounding in static analysis output reduces variance. Consistency rate framed honestly. Diff between runs documented as unreliable for trending. |

---

## M9: Quality Polish — Dedup, Resume, Anti-Lazy

### Objective

Harden existing capabilities: post-hoc deduplication of findings across phases, robust resume from any failure point, enhanced anti-lazy enforcement, report depth control, and configurable degradation priority.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D9.1 | Post-hoc deduplication (Phase 4 consolidator): group findings by file path, cluster by issue category, keep highest-severity instance, mark cross-phase-confirmed as high confidence | Dedup summary in report (X findings merged into Y). Cost: ~500 tokens. Cross-phase confirmed findings labeled. |
| D9.2 | Robust resume system (--resume flag): loads progress.json, skips completed batches, continues from interruption point. Idempotent — resume on completed run produces no changes. | Run interrupted at 25%, 50%, 75%, 90%: all produce identical final output to non-interrupted run. |
| D9.3 | Report depth control (--report-depth): summary (<100 lines, top 5 issues), standard (200-400 lines with per-category lists and evidence snippets), detailed (500-2000 lines with full 8-field profiles) | Each depth level produces output within line count bounds. Detailed includes full profiles. Summary is actionable standalone. |
| D9.4 | Enhanced anti-lazy enforcement: cross-batch evidence diversity (identical justifications across batches flagged), classification distribution sanity (>80% same classification in batch → flagged), INVESTIGATE cap enforcement (>15% → re-analysis triggered) | Anti-lazy mechanisms integrated into consolidator. INVESTIGATE cap enforced per FR-039. |
| D9.5 | Configurable degradation priority (--degrade-priority): default/cross-ref-last/depth-first controls graceful degradation order | Each mode produces different degradation behavior. cross-ref-last preserves Phase 3 at cost of Phase 2 depth. |

### Dependencies

- M8: Depth & Budget Validation Gate (passed)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dedup incorrectness — merging duplicate findings may incorrectly merge distinct issues affecting same file | Medium | Medium | Dedup key: file path + classification category + primary qualifier. Same file with different categories NOT merged. Merge decision logged. |
| Resume state corruption — partial state from crashed run may be inconsistent | Medium | Medium | Checkpoint includes checksum. Resume validates checksum. Corruption detected → prompt user to restart from scratch or last valid checkpoint. |

---

## M10: Final Integration & Scale Validation Gate

### Objective

Validate the complete system end-to-end, including 10K-file scale test, spec-compliance matrix, and Phase 5 readiness documentation. This gate produces the definitive anti-gap artifact.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D10.1 | Full v2 spec compliance matrix: every requirement from unified spec (Sections 4-14) mapped to implementation with pass/fail status | 100% coverage. 100% pass. Deviations documented as intentional (design decision) or bug. |
| D10.2 | End-to-end integration test against 3 repos (small, medium, large): all phases execute, report complete, budget tracking accurate, checkpoint/resume works, credential scan runs, cross-references computed, evidence tiers enforced | All 20 acceptance criteria from spec Section 15 verified. |
| D10.3 | 10K-file scale validation (from haiku variant progressive testing): full audit on 10K-file repo | Completes without memory exhaustion. Budget tracking accurate. Known performance degradation documented. Scaling limitation acknowledged per NFR-018. |
| D10.4 | Phase 5 readiness assessment: architectural extension points documented for --pass-docs full documentation audit, cross-run known-issues registry (--known-issues), calibration files, progressive agent specialization (6-agent target) | Design document (not implementation). Each extension point describes: interfaces that exist, what needs to be built, estimated effort. |
| D10.5 | Spec-implementation gap prevention report: retrospective analysis of where gaps were found in M2/M4/M6/M8, root causes, prevention mechanisms now in place, recommendations for ongoing compliance monitoring | Report produced. Mechanisms catalogued: schema validation, coverage manifest, compliance matrices, anti-lazy detection, reference repo testing, budget tracking, checkpoint/resume. |

### Dependencies

- M9: Quality Polish

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Spec-implementation gap in the validation gate itself — compliance matrix may miss requirements never tested (RISK-007) | Medium | High | Compliance matrix cross-referenced against spec table of contents and section headers. Second reviewer independently produces requirement list from spec; two lists compared for completeness. |
| Implementation effort underestimate — estimates may be 3-5x too low per devil's advocate analysis (RISK-015) | High | High | Phase 5 scoped explicitly as future. M10 documents effort actuals vs. estimates for calibration. No commitments beyond M10 until calibrated. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Token budget overrun — 500K may be 4-7x too low for comprehensive coverage of large repos | M5, M7, M8 | High | High | --budget flag, --dry-run for cost preview, graceful degradation sequence, budget warnings at 70%/90% | architect |
| R-002 | Config cold-start failure — auto-detection produces incorrect profiles | M5, M6 | High | High | Auto-config as visible artifact, --dry-run shows config, user config overrides, low-confidence fields use conservative defaults | backend |
| R-003 | Dynamic import false positives — files referenced via dynamic import incorrectly classified as DELETE | M7, M8 | High | High | Configurable dynamic import pattern list, KEEP:monitor for dynamically-imported files, Tier C evidence → INVESTIGATE only | backend |
| R-004 | LLM output schema non-compliance — Haiku produces malformed JSON | M3, M4 | Medium | Medium | Simplified Phase 1 schema, runtime validator, auto-retry (max 2), then FAILED marking | backend |
| R-005 | Report overwhelming — detailed reports too large for consumption | M9 | Medium | Medium | --report-depth flag with 3 levels (summary/standard/detailed) | architect |
| R-006 | Monorepo scaling — system doesn't scale linearly past ~10K files | M6, M10 | High | High | Progressive scale testing (5K→8K→10K), monorepo detection in Phase 0, per-workspace treatment, documented scaling limitation | architect |
| R-007 | Spec-implementation gap recurrence — v2 repeats v1's pattern of untested promises (CRITICAL) | All | High | High | Compliance matrices at M2/M4/M6/M8/M10, schema validation, anti-lazy enforcement, reference repo testing | architect |
| R-008 | Credential value exposure — scanner accidentally prints credential values | M3, M4 | Medium | High | Scanner prompts explicitly prohibit printing values, runtime output scanning for credential patterns | security |
| R-009 | Phase 0 auto-config cascading errors — incorrect tier assignments corrupt all downstream phases | M5, M6 | High | High | Auto-config as visible artifact, validation against known-good profile, divergence halts with explicit error | architect |
| R-010 | LLM-on-LLM validation limitations — consistency rate mistaken for ground-truth accuracy | M1, M10 | High | Medium | Named "consistency rate" not "accuracy", calibration files recommended, honest limitations in report | architect |
| R-011 | Non-English documentation — limited multilingual support | M7 | Medium | Medium | UTF-8 handling required, full multilingual support out of scope for v2 | backend |
| R-012 | Non-markdown documentation — only .md first-class | M7 | Medium | Low | .md first-class, .rst best-effort, other formats out of scope | backend |
| R-013 | Concurrent audit runs — potential output directory collision | M9 | Low | Medium | Run-ID isolation via .claude-audit/run-{timestamp}/ | backend |
| R-014 | Project-specific over-fitting — audit rules too tailored | M5 | Medium | Medium | Separate universal audit features from project-specific rules, all rules loadable from config | architect |
| R-015 | Implementation effort underestimate — estimates 3-5x too low per devil's advocate analysis | All | High | High | Phase 5 deferred, M10 documents effort actuals for calibration, benchmark by implementing one feature before planning sprints | architect |
| R-016 | Run-to-run non-determinism — LLM outputs inherently non-deterministic | M1, M8 | Medium | Medium | Grounding in static analysis output, consistency rate framed honestly, diff-based trending documented as unreliable | architect |
| R-017 | Context window filling — Phase 3-4 require reading large prior output volumes | M7, M9 | High | Medium | Write-to-disk architecture, budget allocation reserves, graceful degradation skips cross-ref as third cut | architect |
| R-018 | Clean repo edge case — undefined behavior when zero significant findings | M9 | Low | Low | Define clean report template that positively confirms repo health | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect (confidence: 0.72) | backend (0.55), security (0.35), performance (0.30) | System design focus spans all domains (5-phase pipeline, 6-agent system, dependency graphs). Backend dominant at 44% but architecture is the unifying concern. |
| Template | inline | No templates scored ≥ 0.6. quality template closest at 0.52. | Spec is a novel multi-phase audit system with no matching template type. Inline generation from extraction data. |
| Milestone Count | 10 | Range 8-12 (HIGH class). base(8) + floor(4 domains / 2) = 10. | 5 work milestones + 5 validation milestones at 1:1 interleave ratio. |
| Adversarial Mode | multi-roadmap | Single roadmap (no adversarial) | --multi-roadmap --agents opus,haiku flags present. Two competing variants generated and synthesized. |
| Adversarial Base Variant | opus:architect | haiku:architect | Opus variant's emphasis on spec-implementation gap prevention (the CRITICAL risk) and architectural correctness selected as base. Haiku variant's progressive scale testing and efficient phase consolidation adopted as augmentations. Convergence: 78%. |
| M1 Scope | Pure v1 enforcement (opus) | v1 + credential scanning merged (haiku) | Spec Section 14 Phase 0 explicitly requires "all v1 spec promises MUST be implemented before any new features." Credential scanning is a new feature (correctness fix). |
| Scale Testing | Progressive 5K→8K→10K (haiku) | Single 10K stress test at M6 (opus) | Progressive testing surfaces scaling issues incrementally, reducing risk of late-stage surprises. Adopted from haiku variant. |
| Phase 5 Handling | Extension points documented in M10 (opus) | Deferred entirely (haiku) | Documenting extension points has near-zero cost and provides high handoff value for v2.1 planning. |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | FINAL-REPORT.md contains at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE | M5, M9 | Yes |
| SC-002 | coverage-report.json exists with per-tier percentages | M5, M10 | Yes |
| SC-003 | progress.json updated after every batch; --resume recovers from interrupted state | M1, M9, M10 | Yes |
| SC-004 | Every DELETE entry has non-empty grep evidence with result count of 0 | M1, M7 | Yes |
| SC-005 | Every Tier 1-2 KEEP has non-empty import reference information | M7, M8 | Yes |
| SC-006 | validation-results.json exists with ≥ 10% sample size | M1, M10 | Yes |
| SC-007 | .env.production correctly identified: real credentials flagged, templates not flagged | M3, M4 | Yes |
| SC-008 | Tracked-but-gitignored files flagged as MODIFY:flag:gitignore-inconsistency | M3, M4 | Yes |
| SC-009 | Audit completes within --budget +/- 10% without crashing | M5, M8 | Yes |
| SC-010 | --report-depth summary < 100 lines; detailed includes 8-field profiles | M9 | Yes |
| SC-011 | All Phase 1 batch outputs validate against Phase 1 scanner schema | M3, M4 | Yes |
| SC-012 | Phase 3 produces dependency-graph.json with node count > 0 | M7, M8 | Yes |
| SC-013 | Audit succeeds on first run without pre-existing config file | M5, M6 | Yes |
| SC-014 | Phase 3 output includes broken-references.json with checklist format | M7, M8 | Yes |
| SC-015 | v2 output can be mapped to v1 categories using the mapping table | M5 | Yes |
| SC-016 | Directories with 50+ files have assessment labels in FINAL-REPORT.md | M7, M8 | Yes |
| SC-017 | If INVESTIGATE > 15%, re-analysis is triggered | M9 | Yes |
| SC-018 | 3 consecutive batch failures trigger pause + minimum viable report | M5, M10 | Yes |
| SC-019 | --dry-run produces cost estimates without executing scans | M5 | Yes |
| SC-020 | Two concurrent audit runs produce separate output directories | M9 | Yes |
