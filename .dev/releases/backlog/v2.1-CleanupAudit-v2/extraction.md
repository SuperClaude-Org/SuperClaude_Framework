---
spec_source: .dev/releases/current/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-22T17:35:00Z
generator: sc:roadmap
functional_requirements: 45
nonfunctional_requirements: 18
total_requirements: 63
domains_detected: [backend, security, performance, documentation]
complexity_score: 0.814
complexity_class: HIGH
risks_identified: 18
dependencies_identified: 14
success_criteria_count: 20
extraction_mode: chunked (4 chunks)
---

# Extraction: sc:cleanup-audit v2 Unified Specification

## Project Overview

**Title**: sc:cleanup-audit v2 — Multi-Phase Read-Only Repository Audit
**Version**: 2.0-UNIFIED
**Summary**: A comprehensive redesign of the sc:cleanup-audit system, replacing the underperforming v1 with a 5-phase, 6-agent architecture that combines static analysis tools with LLM judgment. The spec addresses a 99.8% miss rate in v1 (12 profiles from 5,857 files), implements all previously-promised-but-undelivered v1 features, adds credential scanning, budget controls, and a tiered classification system. Synthesized via 4-wave adversarial merge of two independent analysis runs.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source Lines |
|----|-------------|--------|----------|--------------|
| FR-001 | 5-phase execution model: Phase 0 (Profile & Plan), Phase 1 (Surface Scan), Phase 2 (Structural Audit), Phase 3 (Cross-Reference Synthesis), Phase 4 (Consolidation & Validation) | backend | P0 | L144-194 |
| FR-002 | 6-agent subagent system: audit-profiler (Haiku), audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet) | backend | P0 | L196-208 |
| FR-003 | Standardized Phase 1 scanner output schema (simplified for Haiku: path, classification, evidence_text, confidence, credential_scan) | backend | P0 | L211-234 |
| FR-004 | Phase 2 full 8-field profile schema (file_path, classification, size_bytes, evidence, risk_tier, rationale, confidence, related_files) | backend | P0 | L236-258 |
| FR-005 | 4-primary classification system (DELETE/KEEP/MODIFY/INVESTIGATE) with 14 secondary qualifiers in a two-tier system | backend | P0 | L285-313 |
| FR-006 | File risk tier classification (Tier 1 Critical, Tier 2 High, Tier 3 Standard, Tier 4 Low) with per-tier coverage targets and evidence requirements | backend | P0 | L327-338 |
| FR-007 | Phase 0 repository profiling: domain detection, file classification, batch manifest generation, static tool orchestration, auto-config generation | backend | P0 | L344-376 |
| FR-008 | Hybrid architecture: 3-tier detection strategy integrating static analysis tools (madge, pydeps, ts-prune, cargo-deps) with grep-based scanning and LLM inference, each edge carrying confidence tier label (A/B/C) | backend | P0 | L263-281 |
| FR-009 | Phase 1 surface scanning: domain-aware batches with explicit file lists, classification per simplified schema, checkpointing after each batch | backend | P0 | L378-417 |
| FR-010 | Credential file scanning: priority-ordered .env enumeration, real vs template pattern detection, configurable pattern list, NEVER print credential values | security | P0 | L399-406 |
| FR-011 | Gitignore consistency check: compare git ls-files against .gitignore patterns, flag tracked-but-ignored files as MODIFY:flag:gitignore-inconsistency | security | P1 | L408-411 |
| FR-012 | Phase 2 structural audit: mandatory 8-field profiles for DELETE/INVESTIGATE candidates and Tier 1-2 KEEP files, file-type-specific verification rules | backend | P0 | L419-458 |
| FR-013 | Signal-triggered depth escalation: default 50-line read with configurable triggers for full-file read (credential-adjacent imports, TODO/FIXME/HACK, complex conditionals, eval/exec, file size > 300 lines) | backend | P1 | L441-444 |
| FR-014 | .env key-presence matrix: extract keys across .env* templates, output key-presence matrix showing configuration drift | backend | P2 | L446-449 |
| FR-015 | Phase 3 cross-reference synthesis: build dependency graph using 3-tier detection, identify orphan nodes, apply confidence-tiered classification | backend | P0 | L460-526 |
| FR-016 | Dependency graph construction: directed graph with nodes (files) and edges (import/export relationships), edges carrying confidence tier (A/B/C), orphan detection for dead code candidates | backend | P0 | L468-476 |
| FR-017 | Duplication matrix generation: group files by similarity (content hash, function overlap), calculate overlap percentages, recommend consolidation for >70% overlap | backend | P1 | L488-491 |
| FR-018 | Minimal docs audit (core flow): broken reference sweep (extract relative links from .md files, verify targets exist), temporal artifact classification (KEEP/DELETE:archive-first/DELETE:standard), checklist output format | documentation | P1 | L492-498 |
| FR-019 | Post-hoc deduplication in Phase 3: group by file path, cluster by issue category, keep highest-severity, mark cross-phase-confirmed as high confidence | backend | P1 | L501-506 |
| FR-020 | Dynamic import detection: configurable pattern list (import(), require(), React.lazy, next/dynamic, importlib, __import__, import.meta.glob, jest.mock), files referenced only via dynamic import → KEEP:monitor | backend | P1 | L508-519 |
| FR-021 | Phase 4 consolidation: merge all phase summaries, deduplicate across phases, sort by classification → risk tier → confidence, generate coverage report and executive summary | backend | P0 | L527-586 |
| FR-022 | 10% spot-check validation: random stratified sample, independent re-verification, consistency rate calculation (NOT accuracy), warning banner if <85% | backend | P0 | L545-553 |
| FR-023 | Coverage report generation: per-tier coverage table with PASS/WARN/FAIL status, evidence depth achieved per tier, unexamined files tracking | backend | P0 | L555-578 |
| FR-024 | Directory-level assessment blocks for directories with 50+ files: sample list (10 representative files), assessment label (actively-maintained/stale/bulk-dump/mixed), recommendation | backend | P1 | L538-540 |
| FR-025 | FINAL-REPORT.md generation with sections: Audit Metadata, Limitations, Coverage Summary, Validation Summary, Executive Summary, Critical Issues, DELETE/MODIFY/KEEP recommendations, Broken References, Duplication Matrix, Directory Assessments, Unexamined Files, Verification Commands | documentation | P0 | L750-809 |
| FR-026 | Token budget system: --budget flag (default 500K), phase allocation (5%/25%/35%/20%/15%), phases can borrow from underutilized phases | performance | P0 | L621-663 |
| FR-027 | Graceful degradation sequence: (1) skip Tier 4, (2) reduce Tier 3 to pattern-match, (3) skip Phase 3 cross-ref, (4) reduce Phase 2 to DELETE/INVESTIGATE only. Never cut: Phase 0, Phase 1 Tier 1-2, Phase 4 | performance | P0 | L643-653 |
| FR-028 | CLI interface with flags: --pass, --pass-docs, --batch-size, --focus, --budget, --report-depth, --tier, --resume, --config, --dry-run, --known-issues, --degrade-priority | backend | P1 | L676-700 |
| FR-029 | Report depth control: summary (<100 lines), standard (200-400 lines), detailed (500-2000 lines with full 8-field profiles) | documentation | P1 | L701-708 |
| FR-030 | Checkpointing via progress.json: updated after each batch with current_phase, batches_completed/total, files_examined/total, token_usage/budget, timestamp | performance | P0 | L417 |
| FR-031 | Resume from checkpoint: --resume flag loads progress.json, skips completed batches, continues from interruption point | performance | P1 | L695 |
| FR-032 | Full documentation audit pass (--pass-docs, Phase 5 extension): 5-section output (SCOPE, CONTENT_OVERLAP_GROUPS, BROKEN_REFERENCES, CLAIM_SPOT_CHECKS, TEMPORAL_ARTIFACTS), budget capped at 20% | documentation | P2 | L587-618 |
| FR-033 | Within-run post-hoc deduplication in Phase 4 consolidator: group by file path, cluster by issue category, keep highest-severity, ~500 token cost | backend | P1 | L861-870 |
| FR-034 | Cross-run known-issues registry (--known-issues flag): JSON schema with signature-based matching, TTL per entry (90 days), max 200 entries with LRU eviction, loaded as read-only consolidator context | backend | P2 | L872-904 |
| FR-035 | Cold-start auto-config generation: framework detection, port detection, CI/CD detection, static tool detection, written to audit output dir, never fail on missing config | backend | P1 | L907-937 |
| FR-036 | --dry-run: run Phase 0 only, display detected domains, tier assignments, available static tools, estimated token budget per phase, batch manifest preview | backend | P1 | L923-933 |
| FR-037 | Monorepo detection: workspace file detection (package.json workspaces, Cargo.toml workspace, nx.json, pnpm-workspace.yaml), per-workspace treatment, batch decomposition respects workspace boundaries | backend | P1 | L368 |
| FR-038 | Backward compatibility mapping: v1 categories (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP/REVIEW) map to v2 two-tier system | backend | P1 | L316-325 |
| FR-039 | INVESTIGATE cap: if INVESTIGATE exceeds 15% of examined files, trigger re-analysis pass on excess items with elevated budget | backend | P0 | L314 |
| FR-040 | Subagent failure handling: 120s per-subagent timeout, max 2 retries with exponential backoff, cascading failure detection (3 consecutive batch failures → pause + minimum viable report) | performance | P0 | L841-847 |
| FR-041 | Anti-lazy enforcement: required output fields validation, evidence non-emptiness checks, confidence distribution anomaly detection (>90% identical → re-review), cross-batch consistency checks | backend | P0 | L832-839 |
| FR-042 | Run isolation: output to .claude-audit/run-{timestamp}/ directories, concurrent audit runs produce separate output directories | backend | P1 | L713-748 |
| FR-043 | Evidence-gated classification: DELETE requires grep proof with result count 0, Tier 1-2 KEEP requires import reference information, even Tier 3-4 KEEP gets minimum one-line evidence annotation | backend | P0 | L393-395 |
| FR-044 | Schema validation: scanners producing non-conforming output trigger validation error, orchestrator retries batch once then marks FAILED in coverage manifest | backend | P1 | L261 |
| FR-045 | Configurable degradation priority: --degrade-priority flag (default/cross-ref-last/depth-first) controls graceful degradation order | performance | P2 | L653 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|------------|--------------|
| NFR-001 | Default token budget ceiling | performance | 500,000 tokens (configurable via --budget) | L625 |
| NFR-002 | Phase 0 profiling duration | performance | 30-60 seconds | L347 |
| NFR-003 | Phase 1 surface scan duration | performance | 3-8 minutes (depends on file count) | L381 |
| NFR-004 | Phase 2 structural audit duration | performance | 5-12 minutes | L421 |
| NFR-005 | Phase 3 cross-reference duration | performance | 3-6 minutes | L463 |
| NFR-006 | Phase 4 consolidation duration | performance | 3-5 minutes | L529 |
| NFR-007 | Tier 1 (Critical) coverage target | reliability | >= 100% of Tier 1 files examined | L330 |
| NFR-008 | Tier 2 (High) coverage target | reliability | >= 90% of Tier 2 files examined | L331 |
| NFR-009 | Tier 3 (Standard) coverage target | reliability | >= 70% of Tier 3 files examined | L332 |
| NFR-010 | Tier 4 (Low) coverage target | reliability | >= 50% of Tier 4 files examined | L333 |
| NFR-011 | Spot-check consistency rate threshold | reliability | >= 85% consistency rate on 10% sample | L829 |
| NFR-012 | INVESTIGATE classification cap | reliability | <= 15% of examined files as INVESTIGATE | L314 |
| NFR-013 | Per-subagent timeout | performance | 120 seconds | L843 |
| NFR-014 | Subagent max retries | reliability | 2 retries with exponential backoff | L844 |
| NFR-015 | Minimum viable report threshold | reliability | 50%+ of batches completed successfully | L847 |
| NFR-016 | Read-only audit principle | security | No automated delete/move operations, all recommendations only | L127 |
| NFR-017 | Credential value protection | security | NEVER print credential values in any output | L404 |
| NFR-018 | Scalability boundary | performance | System does not scale linearly past ~10,000 files | L1145 |

---

## Domain Distribution

| Domain | Percentage | Requirements | Weight |
|--------|-----------|-------------|--------|
| Backend | 44% | FR-001 through FR-009, FR-012-017, FR-019-025, FR-028, FR-030-031, FR-033-044 | Primary |
| Security | 18% | FR-010, FR-011, NFR-016, NFR-017, plus security aspects of FR-043 | Secondary |
| Performance | 22% | FR-026, FR-027, FR-030, FR-031, FR-040, FR-045, NFR-001 through NFR-006, NFR-013-015, NFR-018 | Secondary |
| Documentation | 16% | FR-018, FR-025, FR-029, FR-032 | Tertiary |

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | Phase 0 profiling must complete before Phase 1 scanning can begin (batch manifest required) | internal | FR-001, FR-007, FR-009 |
| DEP-002 | Phase 1 surface scan outputs required as input for Phase 2 structural audit | internal | FR-009, FR-012 |
| DEP-003 | Phase 1 and Phase 2 outputs both required for Phase 3 cross-reference synthesis | internal | FR-009, FR-012, FR-015 |
| DEP-004 | All prior phase outputs required for Phase 4 consolidation | internal | FR-021 |
| DEP-005 | Static analysis tools (madge, pydeps, ts-prune) are external dependencies — optional but strongly recommended | external | FR-008 |
| DEP-006 | Standardized scanner output schema must be implemented before domain-aware batch scanning | internal | FR-003, FR-009 |
| DEP-007 | Classification system must be implemented before scanners can use it | internal | FR-005, FR-009, FR-012 |
| DEP-008 | Evidence-gated classification depends on grep infrastructure and reference counting | internal | FR-043, FR-009 |
| DEP-009 | Checkpointing (progress.json) must be implemented before resume capability | internal | FR-030, FR-031 |
| DEP-010 | Coverage manifest depends on file risk tier classification and batch manifest | internal | FR-006, FR-007, FR-023 |
| DEP-011 | Dependency graph construction requires static tool output or grep-based scanning output | internal | FR-008, FR-016 |
| DEP-012 | FINAL-REPORT.md generation depends on all phase outputs being available | internal | FR-025, FR-021 |
| DEP-013 | Known-issues registry (cross-run) depends on within-run deduplication being implemented | internal | FR-033, FR-034 |
| DEP-014 | Full docs audit (--pass-docs) depends on minimal docs audit being implemented first | internal | FR-018, FR-032 |

---

## Success Criteria

| ID | Criterion | Derived From | Measurable |
|----|-----------|-------------|------------|
| SC-001 | FINAL-REPORT.md contains at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE classifications | FR-005, AC1 | Yes |
| SC-002 | coverage-report.json exists with per-tier percentages | FR-023, AC2 | Yes |
| SC-003 | progress.json updated after every batch; --resume recovers from interrupted state | FR-030, FR-031, AC3 | Yes |
| SC-004 | Every DELETE entry has non-empty grep evidence with result count of 0 | FR-043, AC4 | Yes |
| SC-005 | Every Tier 1-2 KEEP has non-empty import reference information | FR-043, AC5 | Yes |
| SC-006 | validation-results.json exists with >= 10% sample size | FR-022, AC6 | Yes |
| SC-007 | .env.production correctly identified: real credentials flagged, templates not flagged | FR-010, AC7 | Yes |
| SC-008 | Tracked-but-gitignored files flagged as MODIFY:flag:gitignore-inconsistency | FR-011, AC8 | Yes |
| SC-009 | Audit completes within --budget +/- 10% without crashing | FR-026, AC9 | Yes |
| SC-010 | --report-depth summary produces <100 lines; detailed includes 8-field profiles | FR-029, AC10 | Yes |
| SC-011 | All Phase 1 batch outputs validate against Phase 1 scanner schema | FR-003, AC11 | Yes |
| SC-012 | Phase 3 produces dependency-graph.json with node count > 0 | FR-016, AC12 | Yes |
| SC-013 | Audit succeeds on first run without pre-existing config file | FR-035, AC13 | Yes |
| SC-014 | Phase 3 output includes broken-references.json with checklist format | FR-018, AC14 | Yes |
| SC-015 | v2 output can be mapped to v1 categories using the mapping table | FR-038, AC15 | Yes |
| SC-016 | Directories with 50+ files have assessment labels in FINAL-REPORT.md | FR-024, AC16 | Yes |
| SC-017 | If INVESTIGATE > 15%, re-analysis is triggered | FR-039, AC17 | Yes |
| SC-018 | 3 consecutive batch failures trigger pause + minimum viable report | FR-040, AC18 | Yes |
| SC-019 | --dry-run produces cost estimates without executing scans | FR-036, AC19 | Yes |
| SC-020 | Two concurrent audit runs produce separate output directories | FR-042, AC20 | Yes |

---

## Risk Register

| ID | Risk | Probability | Impact | Affected Requirements | Source Lines |
|----|------|-------------|--------|----------------------|--------------|
| RISK-001 | Token budget overrun — 500K may be insufficient for large repos (devil's advocate showed estimates may be 4-7x too low) | High | High | FR-026, FR-027, NFR-001 | L947 |
| RISK-002 | Config cold-start failure — auto-detection produces incorrect framework/port/CI detection | High | High | FR-035, FR-007 | L948 |
| RISK-003 | Dynamic import false positives — files referenced only via dynamic import incorrectly classified as DELETE | High | High | FR-020, FR-015 | L949 |
| RISK-004 | LLM output schema non-compliance — Haiku scanners produce malformed JSON | Medium | Medium | FR-003, FR-044 | L950 |
| RISK-005 | Report overwhelming — detailed reports too large for user consumption | Medium | Medium | FR-029, FR-025 | L951 |
| RISK-006 | Monorepo scaling — system does not scale linearly past ~10K files | High | High | FR-037, NFR-018 | L952 |
| RISK-007 | Spec-implementation gap recurrence — v2 repeats v1 pattern of untested promises (rated CRITICAL in spec) | High | High | All | L953 |
| RISK-008 | Credential value exposure — scanner accidentally prints credential values | Medium | High | FR-010, NFR-017 | L954 |
| RISK-009 | Phase 0 auto-config correctness — incorrect tier assignments cascade to all downstream phases | High | High | FR-007, FR-006 | L955 |
| RISK-010 | LLM-on-LLM validation limitations — consistency rate mistaken for ground-truth accuracy | High | Medium | FR-022 | L956 |
| RISK-011 | Non-English documentation — limited support for non-English docs | Medium | Medium | FR-018, FR-032 | L957 |
| RISK-012 | Non-markdown documentation — only .md first-class, .rst best-effort | Medium | Low | FR-032 | L958 |
| RISK-013 | Concurrent audit runs — potential output directory collision | Low | Medium | FR-042 | L959 |
| RISK-014 | Project-specific over-fitting — audit rules too tailored to one project | Medium | Medium | FR-035 | L960 |
| RISK-015 | Implementation effort underestimate — estimates 3-5x too low per devil's advocate analysis | High | High | All | L961 |
| RISK-016 | Run-to-run non-determinism — LLM outputs inherently non-deterministic, diff-based trending unreliable | Medium | Medium | FR-022, NFR-011 | L962 |
| RISK-017 | Context window filling — Phase 3-4 require reading large volumes of prior output, token-intensive | High | Medium | FR-015, FR-021 | L963 |
| RISK-018 | Clean repo edge case — undefined behavior when repo has zero significant findings | Low | Low | FR-025 | L964 |

---

## Complexity Assessment

### Scoring Breakdown

| Factor | Raw Value | Normalized | Weight | Weighted |
|--------|-----------|-----------|--------|----------|
| requirement_count | 63 (45 FR + 18 NFR) | 1.000 | 0.25 | 0.250 |
| dependency_depth | 5 (Phase 0→1→2→3→4 chain) | 0.625 | 0.25 | 0.156 |
| domain_spread | 4 domains ≥ 10% | 0.800 | 0.20 | 0.160 |
| risk_severity | 2.31 weighted avg (7 High, 8 Medium, 3 Low) | 0.653 | 0.15 | 0.098 |
| scope_size | 1213 lines | 1.000 | 0.15 | 0.150 |

**Complexity Score**: 0.814
**Classification**: HIGH (> 0.7) → 8-12 milestones, 1:1 interleave ratio

### Persona Selection

| Role | Persona | Confidence | Rationale |
|------|---------|-----------|-----------|
| Primary | architect | 0.72 | System design focus (5-phase pipeline, 6-agent system, dependency graphs). Backend at 44% but architecture spans all domains |
| Consulting | backend | 0.55 | Dominant domain (44%) with heavy data pipeline and schema work |
| Consulting | security | 0.35 | Credential scanning (P0), evidence-gating, read-only principle |

---

## Verification Summary

| Pass | Name | Result | Notes |
|------|------|--------|-------|
| 1 | Source Coverage | PASS (100%) | All spec sections with "must", "shall", "required" keywords mapped to FRs |
| 2 | Anti-Hallucination | PASS (100%) | All FRs traceable to specific source lines in spec |
| 3 | Section Coverage | PASS (100%) | All 18 spec sections processed across 4 chunks |
| 4 | Count Reconciliation | PASS | 45 FR + 18 NFR + 14 DEP + 20 SC + 18 RISK = consistent |
