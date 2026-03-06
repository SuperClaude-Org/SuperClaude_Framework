# Validation Report -- cleanup-audit-v2-UNIFIED-SPEC.md

**Date**: 2026-02-20
**Validator**: Quality Engineer (Validation Agent)
**Input**: Unified spec + 4 Wave 1 docs + 2 Wave 2 docs
**Method**: 7-check systematic validation against all quality criteria

---

## Check 1: Set A Unique Contributions

| # | Contribution | Status | Location in Spec |
|---|-------------|--------|-----------------|
| 1 | Target users and use cases | **PRESENT** | Section 3 "Target Users" (lines 132-138): Three personas table (repo maintainers, onboarding authors, DevOps owners) with use cases U1-U3 |
| 2 | Explicit non-goals section | **PRESENT** | Section 3 "Non-Goals" (lines 125-131): N1-N4 including "not a cleanup executor," "not a semantic doc checker," "no elimination of human judgment," and added N4 "not a security audit substitute" |
| 3 | Directory-level assessment blocks for large directories | **PRESENT** | Section 4 Architecture Phase 4 (line 189): "Directory-level assessment blocks for 50+ file dirs [Source: Set A unique #3]"; Section 6 Phase 4 Consolidation (lines 538-541): sample list, assessment labels, recommendation; Section 9 Output FINAL-REPORT.md (lines 801-802); Output directory structure (line 747) |
| 4 | Content overlap group output specification | **PRESENT** | Section 6 Phase 5 "CONTENT_OVERLAP_GROUPS" (lines 596-598): cluster by topic, canonical doc recommendation, superseded candidates, rationale. Also listed in Implementation Roadmap Phase 5 (line 1031) |
| 5 | .env key-presence matrix | **PRESENT** | Section 6 Phase 2 step 6 (lines 446-449): extract keys across .env* templates, output key-presence matrix. Output artifact at line 458: `env-key-matrix.json` |

**Result**: 5/5 PRESENT. All Set A unique contributions are preserved in the unified spec.

---

## Check 2: Set B Unique Contributions

| # | Contribution | Status | Location in Spec |
|---|-------------|--------|-----------------|
| 1 | Spec-implementation gap discovery | **PRESENT** | Section 2 "The Spec-Implementation Gap" (lines 75-89): Full table of v1 promises vs implementation status, root cause analysis, "All v1 spec promises MUST be implemented before any new features are added" |
| 2 | Credential scanning false negative fix | **PRESENT** | Section 6 Phase 1 "Credential Scanning Rules" (lines 399-406): Priority-ordered enumeration, real/template pattern lists, never-print-values rule, disclaimer |
| 3 | Batch decomposition architecture | **PRESENT** | Section 6 Phase 0 step 5 (line 357): "Generate batch manifest: group files by domain, assign to scanner batches"; Phase 1 (line 387): "Domain-aware batches with explicit file lists"; Output artifacts batch-manifest.json (line 373) |
| 4 | Token cost realism / budget arithmetic | **PRESENT** | Section 7 "Budget Arithmetic Honesty" (lines 655-663): Reproduces DA arithmetic, acknowledges 4-7x underestimate, default raised to 500K, all estimates labeled UNVALIDATED |
| 5 | Dependency chain ordering | **PRESENT** | Section 14 "Implementation Roadmap" (lines 968-1034): 5-phase dependency-aware roadmap with explicit dependencies per phase |
| 6 | Phase 0 profiling | **PRESENT** | Section 6 "Phase 0: Profile & Plan" (lines 344-376): Full specification with agent, duration, budget, process steps, outputs, quality gate |
| 7 | Anti-lazy enforcement | **PRESENT** | Section 10 "Anti-Lazy Enforcement" (lines 832-839): 4 enforcement mechanisms (required fields, evidence non-emptiness, confidence distribution check, cross-batch consistency) |
| 8 | Signal-triggered depth | **PRESENT** | Section 6 Phase 2 step 5 (lines 441-444): Default 50 lines, full-file triggers listed, configurable via audit.config.yaml |
| 9 | Dynamic import detection | **PRESENT** | Section 6 Phase 3 "Dynamic Import Detection" (lines 508-519): Extended pattern list including `__import__()`, `import.meta.glob`, `jest.mock()`, etc. Files referenced only via dynamic import -> KEEP:monitor |
| 10 | Coverage guarantee with tiered thresholds | **PRESENT** | Section 5 "File Risk Tiers" (lines 328-336): 4 tiers with coverage targets (>=100%, >=90%, >=70%, >=50%), labeled "initial estimates." Coverage report format in Phase 4 (lines 556-578) |
| 11 | Calibration files (deferred) | **PRESENT** | Section 12 "Calibration Files" (lines 935-937): Explicitly deferred to Phase 5 with rationale. Also referenced in Phase 4 validation (line 550) and Implementation Roadmap Phase 5 item 3 (line 1029) |
| 12 | Budget controls with graceful degradation | **PRESENT** | Section 7 "Graceful Degradation" (lines 643-653): 5-level degradation sequence with "never cut" list. Configurable via --degrade-priority flag (line 653) |
| 13 | Report depth levels | **PRESENT** | Section 8 "Report Depth Levels" (lines 701-708): summary (~50 lines), standard (~200-400 lines), detailed (~500-2000 lines) |
| 14 | Dry-run flag | **PRESENT** | Section 8 CLI flags table (line 697): `--dry-run` flag. Section 12 "--dry-run Integration" (lines 923-933): Phase 0 only, displays detected domains, tier assignments, estimated costs |
| 15 | Cold-start auto-generation | **PRESENT** | Section 12 "First-Run Experience" (lines 909-921): 5-step auto-generation process, written to audit output dir not repo root, confidence threshold at 70% |

**Result**: 15/15 PRESENT. All Set B unique contributions are preserved in the unified spec.

---

## Check 3: Conflict Resolution Compliance

| ID | Verdict | Implemented? | Notes |
|----|---------|-------------|-------|
| C-01 | **B** (5-phase architecture) | **YES** | Section 4 (lines 144-194): 5-phase model adopted with Phase 0 Profile and Phase 4 Consolidation |
| C-02 | **HYBRID** (minimal docs core + full docs opt-in) | **YES** | Phase 3 (lines 492-496): minimal docs audit (broken refs + temporal). Phase 5 (lines 587-618): full docs via --pass-docs. Budget capped at 20% (line 589) |
| C-03 | **B** (two-tier classification + modifications) | **YES** | Section 5 (lines 285-338): 4 primary + qualifiers. INVESTIGATE:human-review-needed added (line 312). 15% INVESTIGATE cap (line 314). Backward compat mapping (lines 316-325) with corrected REVIEW semantics (line 325) |
| C-04 | **HYBRID** (within-run dedup + cross-run registry) | **YES** | Section 11 (lines 859-903): Within-run Phase 4 dedup (lines 861-869). Cross-run registry (lines 872-903) with TTL 90d, auto-prune, max 200 entries, LRU eviction, --known-issues flag |
| C-05 | **B** (dependency-aware phased ordering) | **YES** | Section 14 (lines 968-1034): 5-phase roadmap. Set A items inserted into appropriate phases (directory assessment in Phase 3 line 1010, .env matrix in Phase 2 line 997, overlap groups in Phase 5 line 1031) |
| C-06 | **HYBRID** (target B architecture, start A conservative) | **YES** | Section 4 (lines 196-209): 6-agent table with model assignments. Line 198: "Implementation starts with Set A's conservative approach." Simplified Phase 1 schema (lines 213-233) |
| C-07 | **B** (tiered evidence) | **YES** | Section 5 (lines 328-338): 4 tiers with tiered evidence. Tier 2 relaxed to "1-field mandatory, 2-field target" (line 332). "Evidence depth actually achieved" metric in coverage report (lines 568-572). Set A principle preserved (line 338) |
| C-08 | **B** (explicit budget with modifications) | **YES** | Section 7 (lines 621-673): --budget flag, 500K default (increased from 300K, line 625). Phase allocations advisory not hard-wired (line 641). --dry-run for cost preview (line 629). All estimates UNVALIDATED (line 627). --degrade-priority configurable (line 653) |
| C-09 | **B** (DELETE:archive-first qualifier) | **YES** | Section 5 classification table (line 300): DELETE:archive-first with "suggested destination path" requirement. FINAL-REPORT.md (line 785): separate subsection "Archive Before Deletion." Canonical destinations (line 617) |
| C-10 | **HYBRID** (3-tier detection: static > grep > LLM) | **YES** | Section 4 (lines 263-281): 3-tier table with confidence labels. Phase 0 runs static tools (lines 358-362). Phase 3 (lines 468-476): 3-tier detection strategy. Tier C edges -> INVESTIGATE:cross-boundary only (line 474) |
| C-11 | **B** (spot-check with modifications) | **YES** | Phase 4 validation (lines 545-553): 10% stratified sample, "consistency rate" naming (line 549), calibration accuracy separate metric (lines 550-551), dual reporting with honest framing (line 553). Quality gates (line 829): >=85% consistency rate |
| C-12 | **B** (Phase 0 profiling) | **YES** | Section 6 Phase 0 (lines 344-376): Full specification. Auto-config to audit output dir not repo root (line 374). --dry-run shows config (lines 923-933). User config overrides (line 918). Low-confidence fields flagged (line 920) |
| C-13 | **B** (same as C-03) | **YES** | Same implementation as C-03. Section 5 (lines 285-338) |
| C-14 | **B** (dynamic batch decomposition) | **YES** | Phase 0 step 5 (line 357): batch manifest generation. Quality gate (line 376): "Manifest must account for 100% of git ls-files output" |
| C-15 | **B** (spec-implementation gap as opening section) | **YES** | Section 2 (lines 73-104): Full spec-implementation gap table, root cause analysis, v2 requirement to implement v1 promises first |
| C-16 | **B** (tiered coverage with thresholds) | **YES** | Section 5 risk tiers (lines 328-336): Targets relaxed from Set B originals (90% not 95% for Tier 2, 70% not 80% for Tier 3, 50% not 60% for Tier 4). Labeled "initial estimates" (line 336). Coverage report format (lines 556-578) with PASS/WARN/FAIL |
| C-17 | **B** (JSON intermediates + Markdown final) | **YES** | Section 9 (lines 811-813): "All intermediate phase outputs use JSON for machine parseability. The FINAL-REPORT.md is generated by the consolidator from these JSON artifacts" |
| C-18 | **B** (warning banner, same as C-11) | **YES** | Same implementation as C-11. Phase 4 validation (line 551): warning banner on <85% consistency. Line 552: CRITICAL warning on <80% calibration accuracy |
| C-19 | **HYBRID** (credential scan Phase 1 + key matrix Phase 2) | **YES** | Phase 1 (lines 399-406): credential scanning. Phase 2 step 6 (lines 446-449): .env key-presence matrix. Implementation roadmap: credential scanning in Roadmap Phase 1 (line 984), .env matrix in Roadmap Phase 2 (line 997) |
| C-20 | **B** (signal-triggered depth) | **YES** | Phase 2 step 5 (lines 441-444): Default 50 lines, specific triggers listed, configurable via audit.config.yaml |
| C-21 | **B** (batch-level checkpointing) | **YES** | Phase 1 (lines 417): checkpointing after each batch with specific fields. Section 8 flags (line 695): --resume flag. Output directory (line 717): run-{timestamp}/ for run isolation |
| C-22 | **HYBRID** (3 claims, broader doc types, explicit claim types) | **YES** | Phase 5 CLAIM_SPOT_CHECKS (lines 605-612): 3 claims per doc, applied to API-reference, setup-guide, AND architecture docs. Binary pass/fail criteria. Non-verifiable claims labeled as requiring human review |

**Result**: 22/22 verdicts correctly implemented. No deviations found.

---

## Check 4: Critical Flaw Mitigations

### CRITICAL Flaws

| Flaw ID | Severity | Mitigated? | How |
|---------|----------|-----------|-----|
| F-A-01 | CRITICAL (no token budget model) | **YES** | Section 7: Full budget system with --budget flag, 500K default, phase allocation, graceful degradation, --dry-run for cost preview |
| F-A-02 | CRITICAL (no spec-implementation gap acknowledgment) | **YES** | Section 2: Full spec-implementation gap table with v1 promises vs status. "Phase 0: Enforce Existing Spec" in roadmap |
| F-A-03 | CRITICAL (Pass 4 depends on undefined infrastructure) | **YES** | Docs audit runs within Phase 2/3 framework using structured JSON output from Phase 1. No standalone pass dependent on markdown |
| F-B-01 | CRITICAL (misleading 44x metric) | **YES** | Section 2 (line 93): "normalizing by effort still reveals a substantial gap." Section 1 (line 61): targets are "Budget-relative (not raw count)" |
| F-B-02 | CRITICAL (token estimates underestimated) | **YES** | Section 7 (lines 625-629): Default raised to 500K, all estimates UNVALIDATED, --dry-run recommended, 50% margin advised. Budget arithmetic honesty section (lines 655-663) |
| F-B-03 | CRITICAL (dependency graph via LLM infeasible) | **YES** | Section 4 (lines 263-281): 3-tier detection strategy with static tools as Tier A. Phase 0 runs madge/pydeps/ts-prune if available. Tier C (LLM) only produces INVESTIGATE, not DELETE |
| F-B-04 | CRITICAL (Phase 0 auto-config correctness risk) | **YES** | Section 12 (lines 909-921): Config written as visible artifact, --dry-run shows config, user config overrides, low-confidence fields use conservative defaults and are flagged |
| F-B-05 | CRITICAL (LLM-on-LLM validation = consistency not correctness) | **YES** | Section 10 (lines 849-856): Renamed to "consistency rate," calibration files recommended, dual metrics, honest framing in report. Section 17 (lines 1139-1142): Known limitation explicitly stated |

### HIGH Flaws

| Flaw ID | Severity | Mitigated? | How |
|---------|----------|-----------|-----|
| F-A-04 | HIGH (registry no lifecycle) | **YES** | Section 11 (lines 894-899): TTL 90d, auto-prune stale entries, max 200 entries with LRU eviction |
| F-A-05 | HIGH (claim spot-checks vague) | **YES** | Phase 5 (lines 608-612): Explicit binary pass/fail criteria for 3 claim types. Non-verifiable claims labeled as requiring human review |
| F-A-06 | HIGH (no error recovery) | **YES** | Section 10 (lines 841-848): Per-subagent 120s timeout, max 2 retries, FAILED batch marking, cascading failure detection (3 consecutive), minimum viable report at 50%+ batches |
| F-A-07 | HIGH (shallow adversarial review) | **YES** | Section 13 (lines 941-964): 18 risks including monorepo scaling (R6), non-English docs (R11), non-markdown formats (R12), concurrent runs (R13), GFxAI overfitting (R14). Section 17 (lines 1135-1179): 4 fundamental limitations + 5 known gaps |
| F-A-08 | HIGH (golden fixtures brittle) | **YES** | Section 15 "Test Tiers" (lines 1065-1069): 3-tier test strategy with structural tests, property tests, and benchmark tests -- not golden output matching |
| F-B-06 | HIGH (scanner schema too complex for Haiku) | **YES** | Section 4 (lines 209, 213-233): Simplified Phase 1 schema (path, classification, confidence, evidence_text). Complex fields moved to Phase 2 Sonnet (lines 239-257) |
| F-B-07 | HIGH (coverage targets unvalidated) | **YES** | Section 5 (line 336): Targets labeled "initial estimates -- validate on benchmark repository." Thresholds relaxed from Set B originals |
| F-B-08 | HIGH (evidence KEEP conflicts with budget) | **YES** | Section 5 (line 332): Tier 2 relaxed to "1-field mandatory, 2-field target." Evidence depth reported as metric (lines 568-572) |
| F-B-09 | HIGH (degradation order debatable) | **YES** | Section 7 (line 653): --degrade-priority flag with configurable order |
| F-B-10 | HIGH (no monorepo handling) | **YES** | Phase 0 step 8 (line 368): Monorepo detection from workspace files. Semi-independent unit treatment per workspace |
| F-B-11 | HIGH (INVESTIGATE dumping ground) | **YES** | Section 5 (line 314): 15% hard cap. Quality gate (line 830): re-analysis triggered when exceeded |
| F-B-12 | HIGH (exaggerated old system capabilities) | **YES** | Section 2 (line 93): "these numbers are not directly comparable (the manual approach involved 10-20 hours of human-guided work vs a single automated run)." Targets are budget-relative |
| F-B-13 | HIGH (reflection issues not fully resolved) | **YES** | Section 1 "Decision Lineage Summary" (lines 44-56): Full traceability table mapping each decision to source and reference |
| CS-04 | HIGH (subagent failure underspecified) | **YES** | Section 10 (lines 841-848): Comprehensive failure handling with timeout, retries, FAILED marking, cascading detection, minimum viable report threshold |
| CS-06 | HIGH (no realistic testability) | **YES** | Section 15 "Test Tiers" (lines 1065-1069): 3-tier strategy (structural, property, benchmark) with specific criteria per tier |

**Result**: 8/8 CRITICAL and 15/15 HIGH flaws mitigated. No unmitigated CRITICAL or HIGH flaws.

---

## Check 5: Devil's Advocate Concerns

| # | Concern | Addressed? | How |
|---|---------|-----------|-----|
| 1 | **Hybrid architecture (static tools + LLM)** -- the "single largest architectural blind spot" | **YES** | Section 4 (lines 263-281): "The Hybrid Architecture: Static Tools + LLM Judgment" with explicit acknowledgment of DA finding. 3-tier detection table. Phase 0 runs static tools (lines 358-362). Principle stated (line 267): "Ground truth must come from deterministic tools where possible." |
| 2 | **Budget arithmetic (300K->500K, but is it enough?)** | **YES** | Section 7 (lines 655-663): "Budget Arithmetic Honesty" section reproduces DA arithmetic. Acknowledges 4-7x underestimate. Default raised to 500K. Users told to expect 800K-1M+ for comprehensive 6K-file repo. All estimates labeled UNVALIDATED |
| 3 | **LLM confidence scores are tokens not probabilities** | **YES** | Section 17 (lines 1139-1142): "Confidence scores are not calibrated probabilities. An LLM saying 'confidence: 0.92' means it generated that token sequence, not that there is a 92% chance the classification is correct." Retained as ordering signals with explicit limitation |
| 4 | **Subagent spawn overhead** | **PARTIAL** | Section 7 budget arithmetic (lines 660-661): "Subagent spawn overhead (~70-120K tokens) is not accounted for in phase allocations." Acknowledged but not resolved -- spawn overhead is noted but phase allocations are not adjusted to account for it. The mitigation is the advisory (not hard-wired) nature of allocations and --dry-run |
| 5 | **"Consistency rate" vs "agreement rate" naming** | **YES** | Section 10 (line 549): Uses "consistency rate" throughout. Lines 849-856: Explicit explanation of the distinction. Report framing at line 553 |
| 6 | **15% INVESTIGATE cap** | **YES** | Section 5 (line 314): Cap at 15% triggers re-analysis. Quality gate (line 830): enforcement mechanism specified |
| 7 | **Scope creep beyond cleanup audit** | **YES** | Section 3 Non-Goals (lines 125-131): N1 (read-only), N2 (not semantic checker), N3 (no elimination of human judgment), N4 (not security audit). Clear boundaries established |
| 8 | **Competitive landscape acknowledgment** | **NO** | The unified spec does not acknowledge or benchmark against existing tools (SonarQube, CodeClimate, Snyk, etc.). This DA concern is neither addressed nor listed as a known limitation |
| 9 | **Run-to-run non-determinism** | **YES** | Section 13 Risk R16 (line 962): "LLM outputs are inherently non-deterministic. Grounding in static analysis output reduces variance. Diff between two runs is unreliable for trend tracking." Section 17 (lines 1143-1144): Explicit limitation |
| 10 | **User feedback loop missing** | **YES** | Section 17 (lines 1173-1179): Explicitly listed as a known limitation. "Does not include user correction mechanisms, learning from prior runs, or incremental audit." Stated as "out of scope for v2" |
| 11 | **Maintenance surface area** | **YES** | Section 17 (lines 1161-1170): Enumerated maintenance items (6 prompts, credential patterns, dynamic import patterns, token estimates, config defaults). Acknowledged as "not addressed beyond making pattern lists configurable" |
| 12 | **False precision trap** | **PARTIAL** | Confidence scores acknowledged as non-calibrated (Section 17 line 1139). However, the spec still uses confidence values throughout schemas without introducing explicit uncertainty markers or simplified output modes. The DA's suggestion of "simpler, less precise output with honest uncertainty" is not adopted |
| 13 | **Context window filling problem** | **YES** | Section 13 Risk R17 (lines 963): "Phase 3 and Phase 4 require reading large volumes of prior phase output. Write-to-disk architecture helps but re-reading costs tokens. Account for this in budget." |
| 14 | **System does not scale past ~10K files** | **YES** | Section 13 Risk R6 (line 952): "System does NOT scale linearly past ~10K files." Section 17 (lines 1145): "For monorepos exceeding 50,000 files, the system's current design is impractical." |
| 15 | **Read-only constraint not examined** | **NO** | The DA questioned why the tool must be read-only and suggested a `--execute` mode. The spec does not engage with this question -- N1 states "read-only" as a non-goal but does not justify the constraint or acknowledge the DA's challenge |
| 16 | **Guard Rail 1: Ground truth from tools** | **YES** | Section 4 (line 267): "Ground truth must come from deterministic tools where possible. LLMs provide judgment, classification, and reporting -- not data gathering." |
| 17 | **Guard Rail 2: Empirical budget validation** | **YES** | Section 7 (line 627): "UNVALIDATED -- they require empirical measurement." Section 12 (line 629): "Run --dry-run on your target repository before planning." |
| 18 | **Guard Rail 3: Schema compliance measured** | **PARTIAL** | Schema validation (line 261): retry + FAILED marking. But no benchmark measurement requirement is stated. The spec does not require measuring actual compliance rates before shipping |
| 19 | **Guard Rail 4: Degrade to useful minimum** | **YES** | Section 7 graceful degradation (lines 643-653): ordered degradation with "never cut" list. Section 10 (lines 841-848): minimum viable report from 50%+ batch success |
| 20 | **Guard Rail 5: Honest limitations in output** | **YES** | Section 9 FINAL-REPORT.md (lines 760-765): Dedicated Limitations section listing examined vs skipped files, deterministic vs LLM evidence, confidence non-calibration, dynamic import gaps, actual token cost |
| 21 | **Guard Rail 6: Cold path graceful** | **YES** | Section 12 (lines 907-921): Never fail on missing config, auto-generate sensible defaults |
| 22 | **Guard Rail 7: Complexity justified by user value** | **PARTIAL** | Target users defined (Section 3) but no explicit traceability from each qualifier/tier/field to a user action. The DA's specific test ("for each schema field, identify one user action it enables") is not performed |
| 23 | **Guard Rail 8: Effort from implementation not spec** | **YES** | Section 14 (line 979): "UNVALIDATED -- benchmark by implementing checkpointing first, then extrapolate." Section 13 Risk R15 (line 961): "Effort estimates are 3-5x too low per devil's advocate analysis" |

**Summary**: 17 YES, 3 PARTIAL, 2 NO out of 23 identifiable DA concerns.

**Unaddressed concerns**:
- **Competitive landscape**: No mention of existing tools (SonarQube, CodeClimate, etc.) or positioning against them
- **Read-only constraint justification**: Non-goal N1 asserts read-only but does not engage with the DA's `--execute` suggestion

**Partially addressed concerns**:
- **Subagent spawn overhead**: Acknowledged in budget arithmetic but not factored into phase allocations
- **False precision trap**: Confidence non-calibration acknowledged but schema still uses precision values throughout
- **Schema compliance measurement**: Retry mechanism exists but no pre-ship benchmark requirement

---

## Check 6: Internal Consistency

### Budget Allocations Sum

| Phase | Allocation |
|-------|-----------|
| Phase 0 | 5% |
| Phase 1 | 25% |
| Phase 2 | 35% |
| Phase 3 | 20% |
| Phase 4 | 15% |
| **Total** | **100%** |

- [x] Budget allocations sum to 100%

### Classification Categories Consistency

Checking that classifications used in Phase specs match definitions in Section 5:

- Section 5 defines: DELETE (standard, archive-first), KEEP (verified, unverified, monitor), MODIFY (consolidate-with, fix-references, update-content, move-to, flag), INVESTIGATE (cross-boundary, insufficient-evidence, dynamic-import, human-review-needed) = 4 primary + 14 qualifiers
- Section 1 key metrics table (line 65): "4 primary + 14 qualifiers" -- **CONSISTENT** (note: coverage matrix said 13, but the addition of human-review-needed per C-03 verdict brings it to 14)
- Phase 1 schema (line 228): uses "DELETE|KEEP|MODIFY|INVESTIGATE" -- **CONSISTENT**
- Phase 2 schema (line 241): uses "Primary:Qualifier" format -- **CONSISTENT**
- Phase 3 (line 474): "INVESTIGATE:cross-boundary" -- **CONSISTENT**
- Phase 3 (line 519): "KEEP:monitor" for dynamic imports -- **CONSISTENT**
- Backward compat mapping (lines 316-325): all mappings use defined categories -- **CONSISTENT**
- Gitignore check (line 411): "MODIFY:flag:gitignore-inconsistency" -- **CONSISTENT**

- [x] Classification categories consistent throughout

### Subagent Names Consistency

| Agent Name | Section 4 (line 200-207) | Phase Specs | Consistent? |
|-----------|-------------------------|-------------|------------|
| audit-profiler | Haiku, Phase 0 | Phase 0 (line 346): "audit-profiler (Haiku)" | YES |
| audit-scanner | Haiku, Phase 1 | Phase 1 (line 381): "audit-scanner (Haiku, parallel)" | YES |
| audit-analyzer | Sonnet, Phase 2 | Phase 2 (line 422): "audit-analyzer (Sonnet, parallel)" | YES |
| audit-comparator | Sonnet, Phase 3 | Phase 3 (line 463): "audit-comparator (Sonnet)" | YES |
| audit-consolidator | Sonnet, Phase 4 | Phase 4 (line 529): "audit-consolidator (Sonnet)" | YES |
| audit-validator | Sonnet, Phase 4 | Phase 4 (line 529): "audit-validator (Sonnet)" | YES |

- [x] Subagent names consistent throughout

### Flag Names Consistency

| Flag | CLI Section (lines 686-699) | Used in Phase Specs | Consistent? |
|------|---------------------------|-------------------|------------|
| --pass | "surface\|structural\|cross-cutting\|all" | Not referenced elsewhere in phase specs (used at invocation) | YES |
| --pass-docs | off by default | Phase 2 step 7 (line 451), Phase 5 (line 589) | YES |
| --budget | 500000 default | Section 7 (line 625): "default: 500000" | YES |
| --report-depth | summary\|standard\|detailed | Section 8 report depth (lines 701-708) | YES |
| --resume | Phase 1 checkpointing | Phase 1 (line 417) | YES |
| --dry-run | Phase 0 only | Section 12 (lines 923-933) | YES |
| --known-issues | File path | Section 11 (line 898) | YES |
| --degrade-priority | default\|cross-ref-last\|depth-first | Section 7 (line 653) | YES |
| --config | File path | Phase 0 (line 350) references audit.config.yaml | YES |
| --tier | 1\|2\|3\|4\|all | Not explicitly referenced in phase specs but implicitly used | YES |
| --batch-size | Auto from Phase 0 | Phase 0 generates batch manifest | YES |
| --focus | infrastructure\|frontend\|backend\|docs\|all | Not explicitly referenced in phase specs but available as domain filter | YES |

- [x] Flag names consistent between CLI section and phase specifications

### Acceptance Criteria vs Requirements

| AC# | Requirement Tested | Matches Spec Section? |
|-----|-------------------|----------------------|
| AC1 | 5-category classification | Section 5: 4 primary categories -- **MINOR INCONSISTENCY**: AC1 says "at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE" which tests for 4 categories not 5. But the spec itself defines 4 primary categories, so AC1 is correctly testing the actual requirement |
| AC2 | Coverage tracking | Section 6 Phase 4 (lines 556-578): coverage-report.json format defined -- **CONSISTENT** |
| AC3 | Checkpointing + resume | Phase 1 (line 417), CLI --resume (line 695) -- **CONSISTENT** |
| AC4 | Evidence for DELETE | Phase 1 (line 391): "require grep -r proof of zero references" -- **CONSISTENT** |
| AC5 | Evidence for Tier 1-2 KEEP | Phase 1 (line 392): "require at minimum import reference count" -- **CONSISTENT** |
| AC6 | Spot-check validation | Phase 4 (lines 545-553): 10% sample -- **CONSISTENT** |
| AC7 | Credential scanning | Phase 1 (lines 399-406) -- **CONSISTENT** |
| AC8 | Gitignore check | Phase 1 (lines 408-411) -- **CONSISTENT** |
| AC9 | Budget control | Section 7: --budget flag with +/- 10% tolerance -- **CONSISTENT** |
| AC10 | Report depth | Section 8 (lines 701-708): 3 levels defined -- **CONSISTENT** |
| AC11 | Scanner schema | Section 4 (lines 213-233): Phase 1 schema -- **CONSISTENT** |
| AC12 | Cross-reference | Phase 3: dependency-graph.json output -- **CONSISTENT** |
| AC13 | Cold-start | Section 12 (line 921): "Never fail on missing config" -- **CONSISTENT** |
| AC14 | Broken references | Phase 3 (lines 492-496): broken-references.json output -- **CONSISTENT** |
| AC15 | Backward compat | Section 5 (lines 316-325): mapping table -- **CONSISTENT** |
| AC16 | Directory assessment | Phase 4 (lines 538-541) -- **CONSISTENT** |
| AC17 | INVESTIGATE cap | Section 5 (line 314): 15% cap -- **CONSISTENT** |
| AC18 | Subagent failure | Section 10 (lines 841-848): cascading failure detection -- **CONSISTENT** |
| AC19 | --dry-run | Section 12 (lines 923-933) -- **CONSISTENT** |
| AC20 | Run isolation | Output directory (line 717): run-{timestamp}/ -- **CONSISTENT** |

- [x] Acceptance criteria match requirements (minor AC1 wording is acceptable -- tests 4 categories correctly)

### Additional Consistency Checks

**Phase 5 docs budget reference**: Phase 5 (line 589) says "Budget capped at 20% of total" AND Phase 2 step 7 (line 453) says "Budget capped at 20% of total" for full docs. These refer to the same feature triggered via --pass-docs -- **CONSISTENT** (same budget cap)

**Tier thresholds in Section 5 vs Section 10**: Section 5 (lines 328-334) has >=100%, >=90%, >=70%, >=50%. Quality gate (line 827) references "Tier 1 >= 100%, Tier 2 >= 90% (initial estimates)" -- **CONSISTENT**

**Phase 5 as "Extension" vs Phase 2**: Section 6 Phase 5 heading (line 587) says "Activated via --pass-docs. Executes as a Phase 2 extension." This is consistent with the C-02 verdict -- **CONSISTENT**

---

## Check 7: Quality Scoring

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Specificity** | **9.0** | JSON schemas fully specified for both Phase 1 and Phase 2 with exact field names/types (lines 215-257). Classification system has 4 primaries + 14 qualifiers with explicit meanings (lines 289-313). Risk tiers have concrete thresholds and evidence requirements (lines 328-334). CLI flags table has values, defaults, descriptions (lines 686-699). Coverage report format has full JSON example (lines 556-578). Output directory structure is complete (lines 716-748). Minor deductions: some process steps are described in natural language rather than pseudocode (e.g., Phase 0 domain detection step 2-3); credential pattern list is specific but configurable patterns lack a schema definition; the sampling algorithm for Phase 5 docs audit is unspecified. |
| **Evidence Quality** | **8.5** | Every section traces to source documents via inline citations (e.g., "[Source: Set B ss3, modified per Verdict C-01]"). Decision lineage table (lines 44-56) maps each major decision to source and reference. Budget arithmetic honesty section (lines 655-663) reproduces DA calculations. Spec-implementation gap table (lines 80-85) provides concrete v1 promise vs status data. Key metrics table (lines 59-69) shows v1 current vs v2 target with source attribution. Coverage targets labeled "initial estimates" (line 336). All estimates labeled UNVALIDATED. Minor deductions: some claims about static tool accuracy ("100% accurate for static imports") lack external citations; the token cost scenarios (lines 667-672) remain unvalidated estimates despite labels. |
| **Implementability** | **8.5** | Each phase has agent assignment, duration estimate, budget allocation, inputs, process steps, outputs, and quality gates. Schemas are directly codifiable. CLI interface is fully specified. Acceptance criteria (lines 1042-1063) provide 20 testable requirements. Test tiers (lines 1065-1069) describe 3 levels of validation. Implementation roadmap (lines 968-1034) has dependency ordering. Minor deductions: Phase 0 domain detection algorithm is described procedurally but lacks a concrete decision tree or YAML schema for detection rules; the interaction between static tool output and LLM classification prompts is acknowledged as needing "prompt engineering" (Section 17 line 1153) -- the actual prompt integration is unspecified; effort estimates are all labeled UNVALIDATED (appropriate honesty but reduces planning utility). |
| **Architectural Soundness** | **8.5** | 5-phase pipeline with clear data flow (Phase 0 generates manifests -> Phase 1 produces classified files -> Phase 2 produces profiles -> Phase 3 builds dependency graph -> Phase 4 consolidates). 3-tier detection strategy addresses the DA's core architectural concern. Graceful degradation with ordered cutback sequence and "never cut" list (lines 643-653). Subagent failure handling with cascading detection (lines 841-848). Schema split between Phase 1 (Haiku-appropriate) and Phase 2 (Sonnet-appropriate) respects model capabilities (line 209). Configurable pattern lists (credential, dynamic import, depth triggers) via audit.config.yaml allow adaptation. Run isolation prevents concurrent conflicts. Minor deductions: Phase 0 error propagation is noted but no post-Phase-1 sanity check exists to catch systematic misclassification (the Fowler concern from Section 18); the dependency between Phase 3 and prior phase outputs creates a context window concern (R17) that is acknowledged but not architecturally resolved; the 5-phase pipeline's sequential dependency means partial phase failure requires careful state management that is not fully specified. |
| **Composite** | **8.63** | Average of (9.0 + 8.5 + 8.5 + 8.5) / 4 |

---

## Quality Gate Result

| Metric | Value |
|--------|-------|
| Set A baseline | 7.70 |
| Set B baseline | 8.55 |
| Unified spec composite | **8.63** |
| Target | >= 8.6 |
| **RESULT** | **PASS** |

The unified spec scores above both individual set baselines and above the 8.6 composite target.

Per-dimension comparison:

| Dimension | Set A Avg | Set B Avg | Target | Unified | Status |
|-----------|----------|----------|--------|---------|--------|
| Specificity | 8.3 | 9.1 | >= 9.0 | 9.0 | **PASS** (at threshold) |
| Evidence Quality | 7.5 | 8.8 | >= 8.5 | 8.5 | **PASS** (at threshold) |
| Implementability | 7.9 | 8.5 | >= 8.5 | 8.5 | **PASS** (at threshold) |
| Architectural Soundness | 7.2 | 8.1 | >= 8.5 | 8.5 | **PASS** (at threshold) |

Note: Three dimensions pass at exactly the threshold. This is a narrow pass. The spec meets the quality bar but does not exceed it by a comfortable margin on Evidence Quality, Implementability, or Architectural Soundness.

---

## Issues Requiring Attention

### Unaddressed Devil's Advocate Concerns (2)

1. **Competitive landscape**: The spec does not position itself against existing tools (SonarQube, CodeClimate, Snyk, trunk.io). While this is a PRD concern rather than a technical spec concern, the DA raised it as a blind spot in both analysis sets and it remains unaddressed. **Recommendation**: Add a brief section or footnote acknowledging that this tool complements (not replaces) static analysis and security scanning tools, and that users should use specialized tools for comprehensive security and code quality analysis.

2. **Read-only constraint justification**: Non-goal N1 asserts "read-only" but does not engage with the DA's suggestion of a `--execute` mode. **Recommendation**: Low priority -- the read-only constraint is a reasonable design choice for a v2 audit tool. Consider adding a brief rationale ("read-only ensures safety and auditability; automated execution is a future consideration").

### Partially Addressed Concerns (3)

3. **Subagent spawn overhead in budget**: The spec acknowledges spawn overhead (~70-120K tokens) in the budget arithmetic section but does not adjust phase allocations to account for it. The advisory nature of allocations partially mitigates this. **Recommendation**: Consider noting that phase allocation percentages are "net of spawn overhead" or recommending users add 15-20% to budget estimates for spawn costs.

4. **False precision in confidence scores**: Confidence scores are acknowledged as non-calibrated but still appear prominently in schemas. **Recommendation**: Consider adding a note in the schema definition that confidence values are ordinal (useful for ranking) not cardinal (not probabilities).

5. **Schema compliance measurement before shipping**: The spec has retry + FAILED mechanisms but no requirement to benchmark actual compliance rates. **Recommendation**: Add to Implementation Roadmap Phase 1: "Measure Haiku JSON schema compliance rate on 100 representative inputs. If below 90%, simplify schema further."

### Marginal Quality Dimensions

6. **Specificity at 9.0** (threshold): Could be strengthened by adding concrete decision trees for Phase 0 domain detection and specifying the sampling algorithm for Phase 5 docs audit.

7. **Evidence Quality at 8.5** (threshold): Could be strengthened by adding external citations for static tool accuracy claims and providing empirical data from a pilot run.

8. **Implementability at 8.5** (threshold): Could be strengthened by specifying the prompt integration pattern for static tool output -> LLM classification and providing at least one worked example of Phase 1 scanner prompt + expected output.

9. **Architectural Soundness at 8.5** (threshold): Could be strengthened by adding a post-Phase-1 sanity check (distribution of classifications matches expected patterns for detected repo type) and specifying state management for partial phase failure recovery.

---

## Overall Assessment

The unified spec **passes validation**. All 5 Set A unique contributions and all 15 Set B unique contributions are present. All 22 conflict verdicts from the merge process are correctly implemented. All 8 CRITICAL and all 15 HIGH flaws have mitigations in the spec. The composite quality score of 8.63 exceeds both individual set baselines and the 8.6 target threshold.

The spec is a comprehensive, well-structured document that successfully synthesizes two independent analysis sets through a rigorous adversarial merge process. Its strongest features are:

- Complete traceability from source analyses through conflict resolution to final design decisions
- Honest acknowledgment of limitations (UNVALIDATED budget estimates, non-calibrated confidence scores, scalability boundaries)
- The hybrid architecture (static tools + LLM) that directly addresses the DA's primary architectural critique
- The 3-tier test strategy that provides a realistic path to validation

The spec passes narrowly on three of four quality dimensions (at the 8.5 threshold). A Wave 3 revision is not required but would strengthen the document. The nine issues listed above are improvement opportunities, not blockers. The spec is ready for implementation planning with the caveat that empirical benchmarking (budget validation, schema compliance measurement, pilot run on a representative repository) should occur before sprint planning.

**Verdict: PASS -- Ready for implementation planning.**

---

*Validation report generated 2026-02-20*
*Validator: Quality Engineer (Validation Agent)*
*Input: 1 unified spec + 4 Wave 1 docs + 2 Wave 2 docs*
*Method: 7-check systematic validation*
