# Wave 1 Coverage Matrix: Set A vs Set B Alignment

**Date**: 2026-02-20
**Purpose**: Section-by-section alignment between two independent analysis sets of the sc:cleanup-audit skill improvement effort.

**Set A** (single-agent, concise):
- `A1`: `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md` — Gap analysis comparing old prompts to new output
- `A2`: `SC_CLEANUP_AUDIT_VNEXT_PRD.md` — vNext PRD/specification

**Set B** (multi-agent, comprehensive):
- `B1`: `cleanup-audit-improvement-findings.md` — 15 findings from 4-agent parallel analysis
- `B2`: `cleanup-audit-improvement-proposals.md` — 12 debated proposals from 4-agent parallel debate
- `B3`: `cleanup-audit-reflection-validation.md` — 5-dimension reflection and validation
- `B4`: `cleanup-audit-v2-PRD.md` — v2 PRD with expert panel consensus

---

## Coverage Matrix Table

| # | Topic/Section | Set A Coverage | Set B Coverage | Status | Notes |
|---|--------------|----------------|----------------|--------|-------|
| 1 | **Missing Pass 4 (Docs Quality)** | A1 ss1 ("Docs quality pass absent"), A1 ss Pass 4 section, A2 ss4.1/4.3 (full Pass 4 spec) | B1 Finding 1 (CRITICAL), B2 Proposal 9 (opt-in doc audit), B4 ss5 Phase 5 (deferred) | **DIVERGENCE** | Both sets identify the gap. They disagree on priority and implementation approach. See Divergence Point 1. |
| 2 | **Known-issues suppression / continuity** | A1 ss2 ("Known-issues suppression absent"), A2 ss4.4 (full registry spec with JSON schema + signature matching) | B1 Finding 5 (HIGH), B2 Proposal 10 (post-hoc dedup in consolidator, NOT registry), B3 Dim 5 (agrees with post-hoc), B4 ss5 Phase 4 item 4 ("known-issue registry for cross-pass dedup") | **DIVERGENCE** | Both identify the gap. They disagree on mechanism. See Divergence Point 2. |
| 3 | **Per-file profile schema weakness** | A1 ss3 ("Per-file profile schema weaker"), A2 ss3 G3 (output schema hardening) | B1 Finding 2 (evidence-mandatory KEEP, CRITICAL), B1 Finding 3 (batch decomposition, CRITICAL), B2 Proposal 4 (tiered evidence KEEP), B4 ss5 Phase 2 (8-field profiles) | Both | Set B goes much deeper with tiered evidence requirements and quantified gaps (12 vs 527+ profiles). Set A identifies the gap; Set B proposes stratified solution. |
| 4 | **Broken-reference reporting format** | A1 ss4 ("Broken-reference reporting weaker"), A2 ss4.5 (systematic sweep spec with checklist format) | B1 Finding 14 (LOW — broken refs not consolidated), B2 Proposal 14 (mandatory output section), B4 ss5 Phase 3 pass3-summary includes cross-ref | Both | Set A treats this as P1; Set B downgrades to LOW/Tier 4. Coverage is equivalent in identifying the gap. |
| 5 | **ARCHIVE vs DELETE distinction** | A1 ss5 ("Archive-vs-delete missing"), A2 ss4.3.5 (TEMPORAL_ARTIFACTS with KEEP/ARCHIVE/DELETE) | B1 Finding 10 (recommendation categories, MEDIUM), B2 Proposal 8 (two-tier system: DELETE:archive-first), B4 ss4 (DELETE:archive-first qualifier) | Both | Set A proposes ARCHIVE as a top-level category. Set B subsumes it as a qualifier under DELETE. Functionally aligned but structurally different. |
| 6 | **Pass 1 (surface scan) gap analysis** | A1 Pass 1 section (gitignore recs, coverage bookkeeping) | B1 (no dedicated pass-1 gap section; individual findings touch on it) | Both (shallow in B) | Set A provides pass-by-pass synthesis; Set B restructures findings by topic rather than pass. |
| 7 | **Pass 2 (structural audit) gap analysis** | A1 Pass 2 section (profiles for subset only, nature taxonomy weaker, "Needs Flagging" missing) | B1 Finding 2 (evidence-mandatory KEEP), B1 Finding 4 (file-type-specific rules), B1 Finding 11 (progressive depth) | Both | Set A does pass-aligned analysis; Set B decomposes into cross-cutting findings. Similar substance. |
| 8 | **Pass 3 (cross-cutting) gap analysis** | A1 Pass 3 section (known-issues suppression, large dir assessment, completion tracking) | B1 Finding 8 (cross-reference resolution), B1 Finding 13 (coverage guarantee), B4 ss5 Phase 3 (dependency graph synthesis) | Both | Set B goes substantially deeper on cross-boundary detection. Set A focuses on completeness tracking. |
| 9 | **FLAG bucket (needs code changes)** | A1 P1 proposal ("Expand FLAG section"), A2 ss4.6 (FLAG bucket in Pass 3 and Final Report) | B1 Finding 10 (FLAG as missing category, MEDIUM), B2 Proposal 8 (MODIFY:flag:[issue] qualifier), B4 ss4 (MODIFY:flag:[issue]) | Both | Aligned on need. Set A proposes dedicated section; Set B subsumes under MODIFY qualifier. |
| 10 | **Directory-level assessment for large dirs** | A1 P1 proposal ("50+ file directories"), A2 ss7 A5 (acceptance criterion for large dirs) | B1 (not explicitly addressed as a standalone finding) | **Set A only** | Set B does not have a dedicated finding for large-directory assessment blocks, though B4 coverage tiers partially address the concern. |
| 11 | **.env key matrix comparison** | A1 P2 proposal ("cheap, high impact") | B1 Finding 6 (security content scanning, HIGH — focused on credential detection), B2 Proposal 2 (credential file scanning fix) | Both (different angle) | Set A proposes a cross-env key matrix; Set B focuses on detecting real vs template credentials. Complementary approaches to .env handling. |
| 12 | **Adversarial debate / risk analysis** | A1 ss "Adversarial debate" (3 proposals debated), A2 ss9 (3 risks with mitigations) | B2 (entire document is a 4-agent debate), B3 Dim 4 (7 missing risks), B4 ss11 (8 risks with mitigations) | Both | Set B's adversarial coverage is vastly more comprehensive (4 agents, 5 validation dimensions, 7+ additional risks identified). |
| 13 | **Implementation pointers (SuperClaude paths)** | A1 ss "Implementation pointers" (file paths for rules, templates, SKILL.md) | B3 Dim 2 (references `/config/.claude/commands/sc/cleanup-audit.md`), B4 ss12 (implementation roadmap with phases) | Both | Set A gives direct file paths. Set B gives phased implementation roadmap. Complementary. |
| 14 | **Expert panel critique** | A2 ss8 (Karl Wiegers, Martin Fowler, Lisa Crispin — simulated panel) | B4 ss14 (Karl Wiegers, Martin Fowler, Michael Nygard, Lisa Crispin — expert panel consensus) | Both | Set B adds Michael Nygard (production systems perspective). Both simulate the same framework. |
| 15 | **Acceptance criteria** | A2 ss7 (A1-A5 acceptance criteria) | B4 ss13 (13 testable acceptance criteria table) | Both | Set B is much more comprehensive: 13 criteria vs 5. Set B adds credential scanning, schema validation, budget control, cold-start, cross-reference tests. |
| 16 | **Data model (progress.json schema)** | A2 ss6 (progress.json schema additions: pass4_docs, known_issues, archive/flag counts) | B4 ss8 (full output directory structure with progress.json, coverage-report.json, validation-results.json, all phase outputs) | Both | Set B's output specification is substantially more complete with full directory tree and JSON schemas. |
| 17 | **Target users and use cases** | A2 ss3 (repo maintainers, onboarding authors, DevOps owners; 3 use cases) | B4 (no explicit user persona section) | **Set A only** | Set B's PRD jumps directly to problem statement and architecture without defining target users. |
| 18 | **Non-goals** | A2 ss2 (3 explicit non-goals: not executor, not semantic checker, no elimination of human judgment) | B4 (implicit in "read-only audit" mention, but no dedicated non-goals section) | **Set A only** | Set B PRD lacks explicit non-goals section. This is a structural omission. |
| 19 | **Subagent strategy** | A2 ss5.2 (Option A: reuse existing; Option B: add audit-docs) | B1 Finding 12 (5 specialized subagent types), B2 Proposal 11 (scan profile + model assignment), B4 ss3 (6-agent system with named roles) | Both | Set B goes much deeper. Names 6 agents with model assignments and phase roles. Set A offers two options without commitment. |
| 20 | **Cross-reference resolution phase** | A1 Pass 3 section (briefly: "compare, don't just catalog") | B1 Finding 8 (CRITICAL — cross-boundary dead code), B2 Proposal 1 (#1 priority, dependency graph), B4 ss5 Phase 3 (full spec with graph, confidence scoring, dynamic import detection) | Both (shallow in A) | This is Set B's highest-impact unique contribution. Set A mentions comparison intent; Set B builds a full dependency graph specification. |
| 21 | **Evidence-mandatory KEEP decisions** | A1 (not explicitly called out as a gap) | B1 Finding 2 (CRITICAL — 5,780 files KEEP without evidence), B2 Proposal 4 (tiered evidence), B4 ss4 (unified tier system) | **Set B only** | Set A discusses profile weakness but does not identify the core issue: KEEP files receiving zero evidence. |
| 22 | **Batch decomposition strategy** | A1 (not mentioned) | B1 Finding 3 (CRITICAL — 5,857 files monolithic), B2 Proposal 6 (dynamic two-phase risk-weighted), B4 ss5 Phase 0+1 (profiler + batch manifest) | **Set B only** | Set A does not identify the lack of batch decomposition as a gap. |
| 23 | **File-type-specific verification rules** | A1 Pass 2 ("nature taxonomy weaker") | B1 Finding 4 (HIGH — 5+ specialized rule sets in old), B2 Proposal 5 (contextual risk classification with YAML config), B4 ss5 Phase 2 (file-type-specific rules table) | Both (shallow in A) | Set A hints at the gap ("nature taxonomy"); Set B fully specifies the rule registry with per-type checks. |
| 24 | **Security / credential scanning** | A1 (not mentioned as a gap) | B1 Finding 6 (HIGH — real credentials misidentified), B2 Proposal 2 (CRITICAL — non-negotiable fix), B4 ss5 Phase 1 (credential scanning rules) | **Set B only** | Set A does not identify the credential scanning false negative. This is a correctness failure. |
| 25 | **Anti-lazy-agent enforcement** | A1 (not mentioned) | B1 Finding 9 (HIGH), B2 Proposal 7 (output validation + calibration), B3 Risk 2 (cold-start problem), B4 ss9 (anti-lazy enforcement section) | **Set B only** | Set A does not address agent quality enforcement at all. |
| 26 | **Incremental save / checkpointing** | A1 Pass 1 ("coverage bookkeeping per cluster/directory is less explicit") | B1 Finding 7 (MEDIUM — no save workflow), B3 Dim 2 (existing spec promises checkpointing), B4 ss5 (progress.json after each batch) | Both (shallow in A) | Set A notes the gap tangentially. Set B identifies both the gap AND that the existing spec already promises this feature. |
| 27 | **Progressive depth escalation** | A1 (not mentioned) | B1 Finding 11 (MEDIUM — all files same depth), B2 Proposal 12 (two-level signal-triggered), B4 ss5 Phase 2 (signal-triggered depth escalation) | **Set B only** | Set A does not identify the lack of depth progression across passes. |
| 28 | **Subagent specialization (model assignment)** | A2 ss5.2 (brief mention of Haiku/Sonnet options) | B1 Finding 12 (MEDIUM — 5 specialized types), B2 Proposal 11 (Pass 0 scan profile + model assignment), B4 ss3 (6-agent table with model assignments) | Both (shallow in A) | Set B provides concrete agent-to-model mapping; Set A only mentions it as an option. |
| 29 | **Coverage guarantee mechanism** | A1 Pass 3 ("Remaining/not-yet-audited completion artifacts missing") | B1 Finding 13 (HIGH — no coverage guarantee), B2 Proposal 3 (tiered manifest-first execution), B4 ss5 Phase 4 (coverage report JSON) | Both | Set A identifies the gap. Set B designs a full tiered coverage system with per-tier thresholds and manifest tracking. |
| 30 | **Gitignore consistency checking** | A1 Pass 1 ("Gitignore recommendations not consistently elevated") | B1 Finding 15 (MEDIUM — files tracked despite .gitignore), B2 Proposal 15 (pre-audit gate), B4 ss5 Phase 1 (gitignore consistency check) | Both | Set A mentions gitignore as an output formatting issue. Set B identifies a concrete correctness bug (tracked files violating .gitignore rules). |
| 31 | **Spec-implementation gap (v1 promises not implemented)** | A2 (implicit — does not call out existing spec non-compliance) | B3 Dim 2 ("spec already defines missing features" — CRITICAL), B3 Dim 5 (Phase 0: enforce existing spec), B4 ss2 (full spec-implementation gap table) | **Set B only** | This is Set B's most structurally important contribution. Set A writes a new PRD without acknowledging the existing spec's unfulfilled promises. |
| 32 | **Token cost / budget controls** | A2 ss5.2 (cost controls: sampling, cap broken links) | B2 Impact Summary (runtime/token estimates table), B3 Dim 3 (token estimates systematically low by 2-3x — CRITICAL), B4 ss6 (full budget system with --budget flag, phase allocation, graceful degradation) | Both (shallow in A) | Set B provides quantified cost analysis and discovers original estimates are 2-3x too low. Set A mentions cost control generically. |
| 33 | **Report depth / output volume control** | A2 (not addressed) | B3 Risk 6 (report overwhelming), B4 ss7 (--report-depth flag: summary/standard/detailed) | **Set B only** | Set A does not address the risk of output volume explosion. |
| 34 | **Config bootstrapping / cold-start** | A2 (not addressed) | B3 Risk 1 (config cold-start — HIGH), B4 ss10 (first-run experience with auto-generation) | **Set B only** | Set A does not address first-run experience at all. |
| 35 | **Dynamic import false positives** | A2 (not addressed) | B3 Risk 4 (HIGH — Next.js dynamic patterns), B4 ss5 Phase 3 (dynamic import detection patterns) | **Set B only** | Set A does not consider dynamic imports as a source of false positives. |
| 36 | **LLM output schema compliance** | A2 (not addressed) | B3 Risk 5 (MEDIUM — JSON malformation), B4 ss9 (schema validation post-processing) | **Set B only** | Set A does not address the risk of LLM subagents producing malformed output. |
| 37 | **Dependency chain ordering (implementation)** | A2 ss10 (simple 10-item backlog, no dependency ordering) | B3 Dim 1 (CRITICAL — hidden dependency chain P11->P6->P1->P10), B3 Dim 5 (5-phase revised ordering), B4 ss12 (5-phase roadmap with explicit dependencies) | **Set B only** | Set A lists a flat backlog. Set B discovers that the implementation order has critical dependency constraints. |
| 38 | **Verification approach / golden fixtures** | A2 ss7 (synthetic repo fixtures + regression checks) | B4 ss13 (13 acceptance tests), B3 Dim 2 (feasibility per proposal) | Both | Set A proposes golden-output fixtures. Set B proposes per-requirement acceptance tests. Complementary approaches. |
| 39 | **CLI interface / flags** | A2 ss4.1 (`--pass` updated to include `docs`) | B4 ss7 (full CLI spec: --budget, --report-depth, --tier, --resume, --config, --pass-docs, --dry-run) | Both (shallow in A) | Set B's CLI specification is vastly more complete. |
| 40 | **Claim spot-checks for docs** | A1 Pass 4 ("3-5 claims/doc"), A2 ss4.3.4 (structural claims only) | B1 Finding 1 (claim spot-checking mentioned), B2 Proposal 9 (3 claims per doc for API-ref/setup-guide only) | Both | Set A specifies 3-5 claims of any structural type. Set B narrows to 3 claims for only API-reference and setup-guide categories. |
| 41 | **Content overlap groups** | A1 Pass 4 ("overlap grouping"), A2 ss4.3.2 (cluster by topic, canonical doc recommendation) | B1 Finding 1 (content overlap groups mentioned) | Both (shallow in B) | Set A provides a detailed overlap group output spec. Set B mentions it as part of Finding 1 but does not spec the output format. |
| 42 | **--dry-run flag** | A2 (not addressed) | B4 ss14 (panel consensus addition: Phase 0 only, report estimates) | **Set B only** | Useful addition for cost visibility before committing resources. |
| 43 | **Resume from checkpoint** | A2 (not addressed) | B4 ss7 (`--resume` flag), B4 ss5 Phase 1 (checkpointing after each batch) | **Set B only** | Set A does not address audit resumability. |
| 44 | **Two-tier classification system** | A2 ss4.3.5 (uses flat KEEP/ARCHIVE/DELETE for temporal artifacts) | B2 Proposal 8 (primary + qualifier), B4 ss4 (full two-tier system with 4 primaries + 13 qualifiers + backward compatibility mapping) | Both (different models) | Set A uses flat categories. Set B designs a composable two-tier system. See Divergence Point 3. |
| 45 | **Backward compatibility with v1 categories** | A2 (not addressed) | B4 ss4 (explicit v1-to-v2 category mapping table) | **Set B only** | Set A does not address how v2 categories map back to v1. |

---

## Unique Contributions (Set A Only)

### 1. Target Users and Use Cases
- **Source**: A2, Section 3
- **Content**: Three defined user personas (repo maintainers, onboarding authors, DevOps owners) and three primary use cases (U1-U3)
- **Assessment**: Valuable addition. A PRD without defined users lacks grounding. Should be incorporated into the merged PRD.

### 2. Explicit Non-Goals Section
- **Source**: A2, Section 2 (Non-goals N1-N3)
- **Content**: Not a cleanup executor; not a semantic doc checker; no elimination of human judgment
- **Assessment**: Valuable addition. Explicit non-goals prevent scope creep. Should be incorporated.

### 3. Directory-Level Assessment Blocks for Large Directories
- **Source**: A1 P1 proposal, A2 Section 7 acceptance criterion A5
- **Content**: For directories with 50+ files, output a sample list, assessment label (actively maintained / stale / bulk dump / mixed), and recommendation
- **Assessment**: Valuable addition. Set B's tiered coverage system partially addresses this but does not include the "assessment label" concept for large directories. Should be incorporated as a Phase 4 consolidation output format.

### 4. Content Overlap Group Output Specification
- **Source**: A2, Section 4.3.2
- **Content**: Detailed spec for how overlap groups should be structured: cluster by topic, canonical doc recommendation, superseded candidates, short rationale
- **Assessment**: Valuable addition. Set B mentions overlap groups but never specs the output. Should be carried into the docs audit pass specification.

### 5. .env Key-Presence Matrix
- **Source**: A1 P2 proposal
- **Content**: Extract keys across `.env*` templates and output a key-presence matrix
- **Assessment**: Valuable addition. Cheap check with high signal. Set B focuses on credential detection (correct vs template) but not on cross-env key consistency. Complementary to Set B's credential scanning.

---

## Unique Contributions (Set B Only)

### 1. Spec-Implementation Gap Discovery (CRITICAL)
- **Source**: B3 Dimension 2, B4 Section 2
- **Content**: The existing v1 spec already promises 5 categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-checks -- none of which were implemented. Set B recommends "Phase 0: Enforce Existing Spec" before adding any new features.
- **Assessment**: The single most important structural finding across both sets. Set A writes a new PRD without recognizing the existing spec's unfulfilled promises, risking a repeat of the same gap. Must be incorporated.

### 2. Evidence-Mandatory KEEP Decisions
- **Source**: B1 Finding 2, B2 Proposal 4, B4 Section 4
- **Content**: ~5,780 files classified KEEP without any evidence. Proposes tiered evidence requirements (Tier A: full 3-field check; Tier B: pattern-match; Tier C: relational; Tier D: structural position).
- **Assessment**: Valuable addition. Set A identifies profile weakness but does not isolate the KEEP-without-evidence problem. Must be incorporated.

### 3. Batch Decomposition Strategy
- **Source**: B1 Finding 3, B2 Proposal 6, B4 Section 5 Phase 0+1
- **Content**: Current system processes 5,857 files monolithically with 6 unnamed scanners. Proposes dynamic two-phase batch decomposition with risk-weighted scanning and logged assignments.
- **Assessment**: Valuable addition. This is an architectural concern Set A does not identify at all. Must be incorporated.

### 4. Credential Scanning Correctness Fix
- **Source**: B1 Finding 6, B2 Proposal 2, B4 Section 5 Phase 1
- **Content**: Real credentials in `.env.production` misidentified as template values. Proposes explicit real-vs-template pattern matching with value-never-printed rule.
- **Assessment**: Non-negotiable correctness fix. Set A does not identify this issue. Must be incorporated.

### 5. Anti-Lazy-Agent Enforcement
- **Source**: B1 Finding 9, B2 Proposal 7, B4 Section 9
- **Content**: No enforcement preventing subagents from rubber-stamping files. Proposes structured output validation, calibration files, and cross-batch consistency checks.
- **Assessment**: Valuable addition. Set A does not address agent quality enforcement. Should be incorporated.

### 6. Token Cost Realism (2-3x Underestimate Discovery)
- **Source**: B3 Dimension 3
- **Content**: Original token estimates are systematically low by 2-3x. Evidence-mandatory KEEP alone could double total audit cost (175K-585K additional tokens). Proposes `--budget` flag with proportional allocation.
- **Assessment**: Critical for planning. Without this correction, any implementation would blow its budget. Must be incorporated.

### 7. Dependency Chain Ordering
- **Source**: B3 Dimension 1, B3 Dimension 5, B4 Section 12
- **Content**: Hidden dependency chain: P11 (Scan Profile) -> P6 (Batch Decomposition) -> P1 (Cross-Reference) -> P10 (Deduplication). Original ranking had P1 at #1 but it depends on infrastructure from P6 and P11.
- **Assessment**: Critical for implementation planning. Set A provides a flat backlog; Set B provides a dependency-aware phased roadmap. Must be incorporated.

### 8. Progressive Depth Escalation
- **Source**: B1 Finding 11, B2 Proposal 12, B4 Section 5 Phase 2
- **Content**: Two-level signal-triggered depth (50 lines default; full file on trigger signals like credential imports, TODO/FIXME, eval/exec).
- **Assessment**: Valuable addition. Improves token efficiency while catching important patterns. Should be incorporated.

### 9. Cross-Reference Resolution with Dependency Graph
- **Source**: B1 Finding 8, B2 Proposal 1, B4 Section 5 Phase 3
- **Content**: Full dependency graph specification with confidence-weighted output, dynamic import detection, and cross-boundary dead code identification.
- **Assessment**: Set B's highest-impact technical contribution. Set A mentions "compare, don't just catalog" but does not spec a dependency graph. Must be incorporated.

### 10. Cold-Start / Config Bootstrapping
- **Source**: B3 Risk 1, B4 Section 10
- **Content**: First-run users without `audit.config.yaml` should get auto-generated defaults, not failures. Framework/port/CI detection from project files.
- **Assessment**: Important for usability. Set A does not address first-run experience. Should be incorporated.

### 11. Report Depth Control
- **Source**: B3 Risk 6, B4 Section 7
- **Content**: `--report-depth summary|standard|detailed` flag to manage output volume (50 lines to 2000+ lines).
- **Assessment**: Practical addition. Set A does not address the risk of overwhelming output. Should be incorporated.

### 12. Dynamic Import False Positive Mitigation
- **Source**: B3 Risk 4, B4 Section 5 Phase 3
- **Content**: Next.js `dynamic()`, `React.lazy()`, `import()` patterns create false positives in dead code detection. Proposes explicit pattern scanning.
- **Assessment**: Technical correctness improvement. Should be incorporated.

### 13. Backward Compatibility Mapping (v1 to v2)
- **Source**: B4 Section 4
- **Content**: Explicit mapping table from v1 categories (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP) to v2 two-tier system.
- **Assessment**: Important for migration. Should be incorporated.

### 14. --dry-run and --resume Flags
- **Source**: B4 Section 7 and Section 14
- **Content**: `--dry-run` runs Phase 0 only for cost estimation; `--resume` recovers from interrupted audits.
- **Assessment**: Practical UX improvements. Should be incorporated.

### 15. Standardized Scanner Output Schema (JSON)
- **Source**: B2 Proposal 1, B4 Section 3
- **Content**: Full JSON schema specification for scanner output including external_dependencies, export_targets, confidence scores.
- **Assessment**: The key architectural enabler for cross-reference synthesis. Must be incorporated.

---

## Oversights

Topics that should have been addressed in both sets but were missed by one.

### Missed by Set A (should have been identified)

| # | Topic | Why It Should Have Been Covered |
|---|-------|-------------------------------|
| 1 | **Spec-implementation gap** | Set A writes a new PRD without checking whether the existing spec's promises were implemented. This is the most significant oversight -- it risks repeating the v1 failure. |
| 2 | **Credential scanning false negative** | Set A analyzed the same old prompts and new outputs but did not identify the `.env.production` misidentification. This is a correctness failure, not a depth issue. |
| 3 | **Batch decomposition architecture** | Set A focuses on output quality but ignores the architectural reason for low quality: monolithic scanning without explicit file assignments. |
| 4 | **Token cost realism** | Set A mentions cost controls but does not estimate actual token costs. Without estimates, cost controls are ungrounded. |
| 5 | **Cold-start / first-run UX** | Set A proposes a config-dependent system (known-issues registry, Pass 4) without addressing what happens when those configs do not exist. |

### Missed by Set B (should have been identified)

| # | Topic | Why It Should Have Been Covered |
|---|-------|-------------------------------|
| 1 | **Target users and use cases** | A PRD should define who uses the tool and why. Set B's PRD jumps to architecture without grounding in user needs. |
| 2 | **Explicit non-goals** | Set B's PRD lacks a non-goals section, which risks scope creep during implementation. |
| 3 | **Directory-level assessment blocks** | For repositories with very large directories (docs/, assets/, releases/), a sampling + assessment-label approach provides signal that per-file profiling cannot. |
| 4 | **.env key-presence matrix** | Set B addresses credential scanning correctness but misses the complementary cross-env key consistency check, which is cheap and high-signal. |
| 5 | **Content overlap group output specification** | Set B mentions doc overlap grouping in Finding 1 but never specifies the output format. Set A provides a structured spec. |

---

## Divergence Points

Topics covered by both sets where they disagree on approach, priority, or mechanism.

### Divergence Point 1: Pass 4 (Documentation Audit) — Priority and Scope

**Set A position** (A1 P0, A2 ss4.1/4.3):
> Pass 4 is **P0 (must-have)** and should be a first-class pass that runs when `--pass all` is specified. It includes 5 mandatory output sections: SCOPE, CONTENT_OVERLAP_GROUPS, BROKEN_REFERENCES, CLAIM_SPOT_CHECKS, TEMPORAL_ARTIFACTS.

**Set B position** (B2 Proposal 9, B3 Dim 3, B4 ss12 Phase 5):
> Pass 4 is **revised to MEDIUM priority** (down from CRITICAL) and deferred to Phase 5 (the final implementation phase). It is opt-in only via `--pass-docs`, capped at 20% of token budget, and pre-filters auto-generated/historical docs.

**Resolution guidance**: Set B's demotion is driven by token cost analysis (B3 Dim 3 shows estimates are 2-3x low). The demotion is defensible for initial v2 release but the feature should not be abandoned. Recommend: incorporate as opt-in (Set B approach) but with Set A's output spec (Set A provides the only structured output definition).

---

### Divergence Point 2: Known-Issues Mechanism — Registry vs Post-Hoc Dedup

**Set A position** (A2 ss4.4):
> A persistent **JSON registry** at a configurable path with structured entries (id, signature, category, created_at, status, reference). Suppression is signature-based, conservative, and produces an `ALREADY_TRACKED` output section. Cross-run persistence.

**Set B position** (B2 Proposal 10, B3 Dim 5, B4 ss5 Phase 4):
> **Post-hoc deduplication in the consolidator**, not an inter-pass registry. The consolidator groups findings by file, clusters by issue category, keeps highest-severity, and marks cross-pass-confirmed findings as high confidence. Cost: ~500 tokens. Zero parallelism loss.

**Resolution guidance**: These solve different problems. Set A's registry solves **cross-run** deduplication (don't re-flag known issues from prior audits). Set B's post-hoc dedup solves **within-run** deduplication (don't double-count across passes in the same audit). Both are needed. Recommend: incorporate Set B's post-hoc dedup as the within-run mechanism (Phase 4), and Set A's registry as an optional cross-run mechanism (Phase 5, alongside docs audit).

---

### Divergence Point 3: Classification System — Flat vs Two-Tier

**Set A position** (A2 ss4.3.5, A2 ss4.6):
> Flat categories: DELETE, KEEP, ARCHIVE, REVIEW (existing) + FLAG as a dedicated section. Temporal artifacts get explicit ARCHIVE label.

**Set B position** (B2 Proposal 8, B4 ss4):
> Two-tier composable system: 4 primary actions (DELETE/KEEP/MODIFY/INVESTIGATE) + 13 qualifiers. ARCHIVE becomes `DELETE:archive-first`. FLAG becomes `MODIFY:flag:[issue]`. CONSOLIDATE becomes `MODIFY:consolidate-with:[target]`. Includes explicit v1 backward compatibility mapping.

**Resolution guidance**: Set B's two-tier system is more expressive and provides a clean upgrade path from v1. The backward compatibility mapping ensures continuity. Recommend: adopt Set B's two-tier system but ensure Set A's TEMPORAL_ARTIFACTS output format is preserved within the `DELETE:archive-first` qualifier.

---

### Divergence Point 4: Implementation Priority Ordering

**Set A position** (A2 ss10):
> Flat 10-item backlog: (1) Pass 4 rules, (2) templates, (3) link extractor, (4) overlap grouping, (5) claim spot-check, (6) known-issues registry, (7) directory assessment, (8) .env matrix, (9) golden fixtures, (10) documentation.

**Set B position** (B3 Dim 5, B4 ss12):
> 5-phase dependency-aware roadmap: Phase 0 (enforce existing spec) -> Phase 1 (correctness fixes) -> Phase 2 (infrastructure: profiler + batches + coverage) -> Phase 3 (depth: evidence + cross-ref + rules) -> Phase 4 (quality: dedup + report control + resume) -> Phase 5 (extensions: docs audit + calibration).

**Resolution guidance**: Set B's phased approach is strictly superior. It respects dependency chains (you cannot build cross-reference synthesis without structured scanner output) and addresses the spec-implementation gap first. Recommend: adopt Set B's phase ordering, inserting Set A's unique items (directory assessment, .env matrix, overlap group spec) into the appropriate phases.

---

### Divergence Point 5: Subagent Strategy — Conservative vs Specialized

**Set A position** (A2 ss5.2):
> Prefer reusing existing agents (Option A). Only add `audit-docs` subagent if quality is consistently poor (Option B).

**Set B position** (B1 Finding 12, B4 ss3):
> 6 named agents with explicit model assignments: audit-profiler (Haiku), audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet). Each assigned to specific phases.

**Resolution guidance**: Set B's approach is more prescriptive but also more actionable. The model assignments (Haiku for mechanical tasks, Sonnet for semantic analysis) are cost-effective. Recommend: adopt Set B's agent system as the target architecture, with Set A's conservative Option A as the Phase 0-1 starting point (reuse existing agents) and progressive specialization in Phase 2+.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total topics identified | 45 |
| Covered by both sets | 27 (60%) |
| Set A only (unique contributions) | 5 (11%) |
| Set B only (unique contributions) | 15 (33%) |
| Divergence points | 5 |
| Set A oversights | 5 |
| Set B oversights | 5 |

**Overall assessment**: Set B provides substantially deeper architectural and operational analysis (15 unique contributions vs 5). Set A provides structural PRD elements (users, non-goals, output specs) that Set B omits. The two sets are highly complementary with 5 divergence points that require explicit resolution. The merged PRD should use Set B's phased architecture as the skeleton, enriched with Set A's user-facing specifications and output format definitions.

---

*Coverage matrix generated 2026-02-20*
