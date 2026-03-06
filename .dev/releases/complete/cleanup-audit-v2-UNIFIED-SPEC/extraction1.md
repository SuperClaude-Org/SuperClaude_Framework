---
spec_source: .dev/releases/current/v2.1-CleanupAudit-v2/cleanup-audit-v2-UNIFIED-SPEC.md
generated: 2026-02-22T00:00:00Z
generator: sc:roadmap
functional_requirements: 45
nonfunctional_requirements: 18
total_requirements: 63
domains_detected: [backend, performance, security, documentation]
complexity_score: 0.799
complexity_class: HIGH
risks_identified: 18
dependencies_identified: 10
success_criteria_count: 20
extraction_mode: chunked (4 chunks)
---

# Extraction: sc:cleanup-audit v2

## Project Overview

- **Title**: sc:cleanup-audit v2
- **Version**: 2.0-UNIFIED
- **Summary**: A 5-phase read-only repository audit system that transforms the existing sc:cleanup-audit v1 into a comprehensive, evidence-backed cleanup tool with structured batch decomposition, tiered file classification, static tool integration, budget controls, and multi-agent validation. Synthesized from two independent analysis runs via a 4-wave adversarial merge process.

## Domain Distribution

| Domain | Percentage | Representation |
|--------|-----------|----------------|
| Backend | 55% | Primary (core scanning, profiling, batch processing, schema, subagent orchestration) |
| Performance | 15% | Secondary (budget controls, graceful degradation, scaling, timing) |
| Security | 12% | Secondary (credential scanning, read-only constraint, value protection) |
| Documentation | 10% | Tertiary (docs audit, broken references, temporal artifacts) |
| Infrastructure | 8% | Minor (static tool integration, CLI, output structure) |

## Functional Requirements

| ID | Description | Domain | Priority | Source Lines |
|----|-------------|--------|----------|-------------|
| FR-001 | 5-phase execution model (Phase 0-4) with structured 6-agent subagent system | backend | P0 | L144-L194 |
| FR-002 | Two-tier classification system: 4 primary actions (DELETE/KEEP/MODIFY/INVESTIGATE) + 14 qualifiers | backend | P0 | L285-L326 |
| FR-003 | Phase 0 audit-profiler: domain detection, risk tier assignment, batch manifest generation, static tool orchestration | backend | P0 | L344-L377 |
| FR-004 | Phase 1 surface scan with domain-aware batches, explicit file lists, and simplified Haiku schema | backend | P0 | L378-L418 |
| FR-005 | Credential file scanning: priority-ordered .env enumeration, real vs template pattern detection, value non-exposure | security | P0 | L399-L407 |
| FR-006 | Gitignore consistency check: flag tracked files that should be ignored | backend | P1 | L408-L412 |
| FR-007 | Phase 2 structural audit with mandatory 8-field profiles for DELETE/INVESTIGATE/Tier 1-2 KEEP | backend | P0 | L419-L459 |
| FR-008 | Signal-triggered depth escalation (50-line default → full-file read on trigger patterns) | backend | P1 | L441-L444 |
| FR-009 | .env key-presence matrix across multiple .env* files | security | P1 | L446-L450 |
| FR-010 | Full documentation audit via --pass-docs flag with 5-section output (Phase 2 extension) | documentation | P2 | L451-L454 |
| FR-011 | Phase 3 cross-reference synthesis with 3-tier detection strategy (static tools > grep > LLM) | backend | P0 | L460-L526 |
| FR-012 | Duplication matrices: group files by similarity, compute overlap, recommend consolidation at >70% | backend | P1 | L488-L493 |
| FR-013 | Minimal docs audit in core flow: broken reference sweep + temporal artifact classification | documentation | P1 | L492-L499 |
| FR-014 | Dynamic import detection with configurable patterns; dynamic-only refs → KEEP:monitor | backend | P1 | L508-L519 |
| FR-015 | Phase 4 consolidation: merge all phase summaries, deduplicate, sort, generate executive summary | backend | P0 | L527-L586 |
| FR-016 | 10% spot-check validation labeled as "consistency rate" with stratified sampling | backend | P0 | L545-L554 |
| FR-017 | Directory-level assessment blocks for directories with 50+ files | backend | P1 | L538-L542 |
| FR-018 | Coverage report per tier with PASS/WARN/FAIL status and evidence depth metrics | backend | P0 | L555-L579 |
| FR-019 | Budget control system: --budget flag, 500K default, hard ceiling with proportional phase allocation | performance | P0 | L622-L642 |
| FR-020 | Graceful degradation sequence: 4 progressive cuts with configurable priority | performance | P0 | L643-L654 |
| FR-021 | CLI interface with 12 flags (--pass, --pass-docs, --batch-size, --focus, --budget, --report-depth, --tier, --resume, --config, --dry-run, --known-issues, --degrade-priority) | backend | P0 | L676-L700 |
| FR-022 | --dry-run: Phase 0 only, display cost estimates, batch preview, config preview | backend | P1 | L697 |
| FR-023 | Output directory structure: .claude-audit/run-{timestamp}/ with phase subdirectories | backend | P0 | L711-L748 |
| FR-024 | FINAL-REPORT.md structured output with 13 sections including Limitations, Coverage, Validation | backend | P0 | L750-L809 |
| FR-025 | Checkpointing via progress.json after each batch with phase/batch/token tracking | backend | P0 | L417 |
| FR-026 | Resume from checkpoint via --resume flag | backend | P1 | L695 |
| FR-027 | Anti-lazy enforcement: required output fields, evidence non-emptiness, confidence distribution, cross-batch consistency | backend | P1 | L832-L840 |
| FR-028 | Subagent failure handling: timeout, retry, cascading failure detection, minimum viable report | backend | P1 | L841-L848 |
| FR-029 | Within-run deduplication in Phase 4 consolidator | backend | P1 | L861-L870 |
| FR-030 | Cross-run known-issues registry via --known-issues flag with signature-based matching | backend | P2 | L872-L905 |
| FR-031 | Cold-start auto-config generation from project structure detection | backend | P0 | L907-L922 |
| FR-032 | Monorepo detection: workspace boundary respect for profiling and scanning | backend | P1 | L368 |
| FR-033 | Backward compatibility mapping from v1 categories to v2 two-tier system | backend | P0 | L316-L325 |
| FR-034 | INVESTIGATE cap at 15% of examined files; trigger re-analysis if exceeded | backend | P1 | L314 |
| FR-035 | Report depth control via --report-depth (summary/standard/detailed) | backend | P1 | L701-L708 |
| FR-036 | File risk tiers (1-4) with graduated coverage targets and evidence requirements | backend | P0 | L327-L338 |
| FR-037 | Evidence-mandatory KEEP for Tier 1-2 files (import references required) | backend | P0 | L430 |
| FR-038 | Standardized scanner output schemas for Phase 1 (simplified) and Phase 2 (full 8-field) | backend | P0 | L211-L261 |
| FR-039 | Post-hoc deduplication in Phase 3: group by file, cluster by category, keep highest-severity | backend | P1 | L501-L507 |
| FR-040 | Hybrid architecture: 3-tier detection (static tools > grep > LLM) with confidence labels | backend | P0 | L263-L282 |
| FR-041 | Schema validation with retry on malformed output; mark as FAILED after retry | backend | P1 | L261-L262 |
| FR-042 | Phase 5 full docs audit: 5-section format (scope, overlap, broken refs, claims, temporal) | documentation | P2 | L587-L618 |
| FR-043 | Content overlap groups detection: cluster docs by topic, recommend canonical doc | documentation | P2 | L596-L599 |
| FR-044 | Claim spot-checks: 3 claims per doc with binary pass/fail criteria | documentation | P2 | L606-L613 |
| FR-045 | Temporal artifact classification: KEEP/DELETE:archive-first/DELETE:standard with destination paths | documentation | P2 | L615-L618 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|-----------|-------------|
| NFR-001 | Default token budget | performance | 500,000 tokens | L625 |
| NFR-002 | Phase 0 execution time | performance | 30-60 seconds | L347 |
| NFR-003 | Phase 1 execution time | performance | 3-8 minutes | L381 |
| NFR-004 | Phase 2 execution time | performance | 5-12 minutes | L422 |
| NFR-005 | Phase 3 execution time | performance | 3-6 minutes | L462 |
| NFR-006 | Phase 4 execution time | performance | 3-5 minutes | L529 |
| NFR-007 | Per-subagent timeout | reliability | 120 seconds | L843 |
| NFR-008 | Consistency rate threshold | maintainability | >= 85% on spot-check | L829 |
| NFR-009 | Coverage targets by tier | maintainability | T1>=100%, T2>=90%, T3>=70%, T4>=50% | L327-L334 |
| NFR-010 | Read-only operation | security | No automated delete/move operations | L127 |
| NFR-011 | Credential value protection | security | Never print credential values in output | L404 |
| NFR-012 | Run isolation | reliability | Timestamped output directories | L716 |
| NFR-013 | Retry policy | reliability | Max 2 retries with exponential backoff | L844 |
| NFR-014 | Minimum viable report threshold | reliability | 50%+ batch completion required | L847 |
| NFR-015 | Schema validation enforcement | reliability | Post-processing validation on all scanner output | L261 |
| NFR-016 | Credential pattern configurability | maintainability | Patterns loadable from audit.config.yaml | L406 |
| NFR-017 | Dynamic import pattern configurability | maintainability | Patterns loadable from audit.config.yaml | L509 |
| NFR-018 | Budget estimates unvalidated | maintainability | Require empirical benchmarking before use | L627 |

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | Phase 1 depends on Phase 0 outputs (batch-manifest.json, static analysis results) | internal | FR-004, FR-005, FR-006 |
| DEP-002 | Phase 2 depends on Phase 1 output (pass1-summary.json, file-manifest.json) | internal | FR-007, FR-008, FR-009 |
| DEP-003 | Phase 3 depends on all Phase 1+2 outputs plus Phase 0 static analysis | internal | FR-011, FR-012, FR-013, FR-014 |
| DEP-004 | Phase 4 depends on all prior phase outputs for consolidation | internal | FR-015, FR-016, FR-017, FR-018 |
| DEP-005 | Full docs audit (--pass-docs) requires Phase 2 execution context | internal | FR-010, FR-042, FR-043, FR-044 |
| DEP-006 | Cross-run known-issues registry requires at least one prior audit run | internal | FR-030 |
| DEP-007 | Calibration files require prior run as baseline | internal | FR-016 |
| DEP-008 | Static analysis tools (madge, pydeps, ts-prune) are optional external dependencies | external | FR-003, FR-040 |
| DEP-009 | Implementation phases are strictly sequential: 0→1→2→3→4→5 | internal | All FRs |
| DEP-010 | Credential scanning depends on actual file content reading (not path-only) | internal | FR-005 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|-----------|
| SC-001 | FINAL-REPORT.md contains at least 2 of DELETE/KEEP/MODIFY/INVESTIGATE | FR-002, FR-024 | Yes |
| SC-002 | coverage-report.json exists with per-tier percentages | FR-018 | Yes |
| SC-003 | progress.json updated after every batch; --resume recovers from interrupted state | FR-025, FR-026 | Yes |
| SC-004 | Every DELETE entry has non-empty grep evidence with result count of 0 | FR-004, FR-037 | Yes |
| SC-005 | Every Tier 1-2 KEEP has non-empty import reference information | FR-037 | Yes |
| SC-006 | validation-results.json exists with >= 10% sample size | FR-016 | Yes |
| SC-007 | .env.production correctly identified: real credentials flagged, templates not flagged | FR-005 | Yes |
| SC-008 | Files tracked despite .gitignore rules flagged as MODIFY:flag:gitignore-inconsistency | FR-006 | Yes |
| SC-009 | Audit completes within --budget +/- 10% without crashing | FR-019, NFR-001 | Yes |
| SC-010 | --report-depth summary produces <100 lines; detailed includes 8-field profiles | FR-035 | Yes |
| SC-011 | All Phase 1 batch outputs validate against Phase 1 scanner schema | FR-038 | Yes |
| SC-012 | Phase 3 produces dependency-graph.json with node count > 0 | FR-011 | Yes |
| SC-013 | Audit succeeds on first run without pre-existing config file | FR-031 | Yes |
| SC-014 | Phase 3 output includes broken-references.json with checklist format | FR-013 | Yes |
| SC-015 | v2 output can be mapped to v1 categories using the mapping table | FR-033 | Yes |
| SC-016 | Directories with 50+ files have assessment labels in FINAL-REPORT.md | FR-017 | Yes |
| SC-017 | If INVESTIGATE > 15% of examined files, re-analysis is triggered | FR-034 | Yes |
| SC-018 | 3 consecutive batch failures trigger pause + minimum viable report | FR-028 | Yes |
| SC-019 | Running with --dry-run produces cost estimates without executing scans | FR-022 | Yes |
| SC-020 | Two concurrent audit runs produce separate output directories | NFR-012 | Yes |

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements |
|----|-------------|------------|--------|----------------------|
| RISK-001 | Token budget overrun -- 500K may be insufficient for comprehensive coverage | High | High | FR-019, NFR-001 |
| RISK-002 | Config cold-start failure -- auto-detection may misclassify project structure | High | Medium | FR-031 |
| RISK-003 | Dynamic import false positives -- files used via dynamic imports incorrectly classified DELETE | Medium | High | FR-014 |
| RISK-004 | LLM output schema non-compliance -- Haiku may produce malformed JSON | Medium | Medium | FR-038, FR-041 |
| RISK-005 | Report overwhelming users -- detailed output may be too verbose | Medium | Low | FR-035 |
| RISK-006 | Monorepo scaling failure -- system impractical beyond ~10K files | High | High | FR-032 |
| RISK-007 | Spec-implementation gap recurrence -- v2 spec promises may go unimplemented like v1 | High | High | All FRs |
| RISK-008 | Credential value exposure -- scanner may inadvertently print credential values | Low | High | FR-005, NFR-011 |
| RISK-009 | Phase 0 auto-config correctness -- detected config may be wrong | Medium | High | FR-031 |
| RISK-010 | LLM-on-LLM validation limitations -- consistency rate != accuracy | High | Medium | FR-016 |
| RISK-011 | Non-English documentation -- limited multilingual support | Medium | Low | FR-013, FR-042 |
| RISK-012 | Non-markdown documentation formats -- .rst support is best-effort only | Medium | Low | FR-042 |
| RISK-013 | Concurrent audit runs -- potential resource conflicts | Low | Low | NFR-012 |
| RISK-014 | Over-fitting to specific project patterns -- universal vs project-specific rules | Medium | Medium | FR-031 |
| RISK-015 | Implementation effort underestimate -- estimates may be 3-5x too low | High | High | All FRs |
| RISK-016 | Run-to-run non-determinism -- LLM outputs vary between runs | Medium | Medium | FR-016 |
| RISK-017 | Context window filling -- Phase 3-4 re-reading costs significant tokens | High | High | FR-011, FR-015, NFR-001 |
| RISK-018 | "Clean repo" output undefined -- no template for zero-findings case | Low | Low | FR-024 |

## Complexity Analysis

| Factor | Raw Value | Normalized | Weight | Weighted |
|--------|-----------|-----------|--------|----------|
| Requirement Count | 63 | 1.000 | 0.25 | 0.250 |
| Dependency Depth | 5 | 0.625 | 0.25 | 0.156 |
| Domain Spread | 4 | 0.800 | 0.20 | 0.160 |
| Risk Severity | 2.11 | 0.556 | 0.15 | 0.083 |
| Scope Size | 1214 lines | 1.000 | 0.15 | 0.150 |
| **Total** | | | | **0.799** |

**Classification**: HIGH (> 0.7) → 10 milestones, 1:1 interleave ratio

## Persona Selection

| Role | Persona | Confidence | Rationale |
|------|---------|-----------|-----------|
| Primary | architect | 0.501 | High complexity (0.799), 4 domains, deep dependency chains, system design focus |
| Consulting | backend | 0.501 | Dominant domain (55%), core scanning infrastructure |
| Consulting | security | 0.092 | Credential scanning, read-only enforcement |
