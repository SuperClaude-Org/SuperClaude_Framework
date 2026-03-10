# Wave 1 Conflict Register: Set A vs Set B

**Date**: 2026-02-20
**Detector**: Conflict Detector Agent
**Set A files**: `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`, `SC_CLEANUP_AUDIT_VNEXT_PRD.md`
**Set B files**: `cleanup-audit-improvement-findings.md`, `cleanup-audit-improvement-proposals.md`, `cleanup-audit-reflection-validation.md`, `cleanup-audit-v2-PRD.md`

---

## Conflict Register

### C-01: Phase/Pass Structure (Count and Architecture)

**Category**: Phase Structure
**Stakes**: HIGH

**Set A Position**: 4 passes -- Surface Scan (existing), Structural Audit (existing), Cross-Cutting (existing), and new **Pass 4: Docs Quality**. Additive design: keep the existing 3-pass structure and bolt on a 4th pass.
> "Pass 1: Surface Scan (existing) / Pass 2: Structural Audit (existing) / Pass 3: Cross-Cutting Audit (existing) / Pass 4: Docs Quality (new; mandatory when `--pass all`)" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.1

**Set B Position**: 5 phases -- **Phase 0: Profile & Plan** (new pre-pass), Phase 1: Surface Scan, Phase 2: Structural Audit, Phase 3: Cross-Reference Synthesis, **Phase 4: Consolidation & Validation** (new post-pass). No dedicated documentation pass in the main flow.
> "sc:cleanup-audit v2 is a 5-phase read-only repository audit" -- `cleanup-audit-v2-PRD.md` section 1
> "Phase 0: Profile & Plan (Haiku, 30-60s) ... Phase 4: Consolidation & Validation (Sonnet)" -- `cleanup-audit-v2-PRD.md` section 5

**Reasoning Chain A**: The biggest gap observed is the missing docs audit. The simplest fix is to add a dedicated pass. Reuses existing architecture with minimal disruption.

**Reasoning Chain B**: The reflection analysis identified that the existing spec already promises features (coverage tracking, checkpointing, spot-check validation) that were never implemented. The root cause is lack of infrastructure (profiling, structured output, consolidation). Adding a pre-pass (Phase 0) and a post-pass (Phase 4) addresses the systemic failure, not just the docs gap.

**Evidence Assessment**: B stronger. Set B's reflection validation (`cleanup-audit-reflection-validation.md` Dimension 2) identifies that the current spec already promises unimplemented features, making infrastructure fixes more fundamental than adding a new content pass.

---

### C-02: Documentation Audit -- Mandatory vs Opt-In

**Category**: Scope Decisions
**Stakes**: HIGH

**Set A Position**: Pass 4 Docs Quality is **mandatory** when `--pass all` is used. Classified as **P0 (must-have)**.
> "P0 (must-have): Add Pass 4 'Docs Quality' as a first-class pass" -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md` section "Concrete incorporation proposals"
> "Pass 4: Docs Quality (new; mandatory when `--pass all`)" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.1

**Set B Position**: Documentation audit is **opt-in** via `--pass-docs` flag, deferred to **Phase 5** of the implementation roadmap. Capped at 20% of token budget.
> "Activated via `--pass documentation` or `--pass all` flag ... Hard cap: 20% of total audit token budget" -- `cleanup-audit-improvement-proposals.md` Proposal 9
> "Documentation Audit Pass (F1) | CRITICAL | MEDIUM | Opt-in flag (`--pass documentation`). Cap at 20% of token budget." -- `cleanup-audit-improvement-proposals.md` Tier 3 table
> "Phase 5: Extensions (Future) -- 1. Documentation audit pass (`--pass-docs`)" -- `cleanup-audit-v2-PRD.md` section 12

**Reasoning Chain A**: The old prompts had a dedicated Pass 4 that caught real problems (stale links, misleading docs). The new audit has "near-zero signal about documentation correctness." Docs quality is the single biggest gap.

**Reasoning Chain B**: The 4-agent debate downgraded docs audit from CRITICAL to MEDIUM because: (1) it has high token cost, (2) other fixes (credential scanning, coverage guarantee, cross-ref synthesis) have higher ROI, and (3) the docs audit can be bounded as opt-in. The reflection validation agreed: infrastructure must come before content passes.

**Evidence Assessment**: Both have merit; A has stronger user-impact evidence, B has stronger cost-benefit analysis. Even.

---

### C-03: Classification System -- Categories and Structure

**Category**: Classification System
**Stakes**: HIGH

**Set A Position**: Expand from 3 categories (DELETE/REVIEW/KEEP) by adding **ARCHIVE**, **FLAG**, and **BROKEN_REFERENCES** as distinct output buckets. Classification remains flat (not two-tier).
> "G3. Harden output schemas so critical buckets are consistently emitted: BROKEN_REFERENCES in checklist format / ARCHIVE (temporal artifacts) distinct from DELETE / FLAG (requires code changes) / REMAINING / NOT_YET_AUDITED coverage accounting" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 2

**Set B Position**: Two-tier classification with **4 primary actions** (DELETE/KEEP/MODIFY/INVESTIGATE) each with **secondary qualifiers**. ARCHIVE becomes `DELETE:archive-first`. FLAG becomes `MODIFY:flag:[issue]`. CONSOLIDATE becomes `MODIFY:consolidate-with:[target]`. No REVIEW category at all.
> "Primary Action: DELETE / KEEP / MODIFY / INVESTIGATE ... Secondary Qualifier: DELETE: standard | archive-first / KEEP: verified | unverified | monitor / MODIFY: fix-references | consolidate-with:[target] | update-content | move-to:[destination] | flag:[issue] / INVESTIGATE: cross-boundary | insufficient-evidence | dynamic-import" -- `cleanup-audit-v2-PRD.md` section 4

**Reasoning Chain A**: The gap analysis identified specific missing output buckets (ARCHIVE, FLAG) from the legacy prompts. The simplest fix is to add those as named sections in the output.

**Reasoning Chain B**: The proposal debate recognized that flat categories create ambiguity (is CONSOLIDATE a DELETE or a KEEP?). A two-tier system with primary action + qualifier is more expressive and composable. The v1 spec already had 5 categories (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP) that were never implemented; the two-tier system subsumes all of them.

**Evidence Assessment**: B stronger. The two-tier system is more systematic and addresses the same gaps Set A identifies while also providing backward compatibility mapping.

---

### C-04: Known-Issues Handling -- Registry vs Post-Hoc Dedup

**Category**: Known-Issues Handling
**Stakes**: HIGH

**Set A Position**: **Sequential registry** loaded before passes. Known issues stored as JSON with `id`, `signature`, `category`, `created_at`, `status`, `reference` fields. Findings matching a signature are suppressed and reported in `ALREADY_TRACKED` section.
> "P0 (must-have): Known-issues suppression registry ... Pass 3 (and Pass 4) receives a 'Known issues list'" -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
> "The system must support an optional known issues registry ... If a finding matches a known issue signature, it must be reported once under an ALREADY_TRACKED section" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.4

**Set B Position**: **Post-hoc deduplication** in the consolidator agent, not an inter-pass registry. Preserves parallelism. Zero runtime overhead during scanning.
> "Post-hoc deduplication in consolidator instead of sequential registry. Preserves parallelism." -- `cleanup-audit-improvement-proposals.md` Proposal 10 (rated MEDIUM)
> "Add to consolidator prompt: 1. Group findings by file path 2. Cluster within-file findings by issue category 3. Keep highest-severity instance 4. Mark cross-pass-confirmed as high confidence 5. Remove remaining duplicates ... Cost: ~500 tokens in consolidator prompt. Zero runtime overhead. Zero parallelism loss." -- `cleanup-audit-improvement-proposals.md` Proposal 10

**Reasoning Chain A**: The old prompts used a 34-item known issues list that prevented re-flagging. The registry model is proven: it directly prevents audit thrash and allows focusing on net-new drift. It is a cross-run mechanism (persists between audit runs), not just cross-pass.

**Reasoning Chain B**: A sequential registry that must be loaded before each pass creates a serialization bottleneck. The performance engineers argued that deduplication is fundamentally a consolidation task. Post-hoc dedup in the consolidator is cheaper (500 tokens), preserves parallelism, and avoids the maintenance burden of a registry.

**Evidence Assessment**: A stronger for cross-run suppression (a registry persists between audit runs; post-hoc dedup only deduplicates within a single run). B stronger for within-run dedup efficiency. These solve different problems.

---

### C-05: Priority Ordering of Improvements

**Category**: Priority Ordering
**Stakes**: HIGH

**Set A Position**: **P0** = Pass 4 Docs Quality + Known-issues suppression registry. **P1** = Broken-reference checklist, FLAG section, large directory assessment. **P2** = .env key matrix.
> "P0 (must-have): Add Pass 4 'Docs Quality' as a first-class pass ... P0 (must-have): Known-issues suppression registry ... P1: Enforce broken-reference checklist ... P1: Expand 'FLAG' section ... P1: Directory-level assessment blocks" -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`

**Set B Position**: **Phase 0** = Enforce existing spec (5 categories, coverage tracking, checkpointing, evidence-gated classification, spot-check). **Phase 1** = Correctness fixes (credential scanning, gitignore). **Phase 2** = Infrastructure (profiling, batch decomposition, coverage manifest). **Phase 3** = Depth (evidence KEEP, cross-reference, file-type rules). **Phase 4** = Quality. **Phase 5** = Extensions (docs audit, calibration).
> "Phase 0: Enforce Existing Spec ... Phase 1: Correctness Fixes (P2, P15) ... Phase 2: Infrastructure (P6, P11, P3) ... Phase 3: Depth Improvements (P4, P1, P5) ... Phase 4: Quality & Polish (P8, P10, P12) ... Phase 5: Extensions (P9, P7, P13, P14)" -- `cleanup-audit-reflection-validation.md` section "Recommended Revised Ordering"
> Adopted nearly verbatim in `cleanup-audit-v2-PRD.md` section 12

**Reasoning Chain A**: The gap analysis is anchored on the delta between old and new outputs. The biggest observable gap is the missing docs pass and the re-discovery problem, so those are P0.

**Reasoning Chain B**: The reflection analysis discovered that the v1 spec already promises features that were never implemented. Adding new features on top of unimplemented promises creates a larger spec-implementation gap. The correct order is: enforce existing spec first, then fix correctness bugs, then build infrastructure, then add depth, then extensions.

**Evidence Assessment**: B stronger. The discovery that the existing spec has unimplemented features is a critical insight that changes the priority calculus. Set A never examines the current spec for implementation gaps.

---

### C-06: Subagent Architecture

**Category**: Architectural Decisions
**Stakes**: MEDIUM

**Set A Position**: Reuse existing agents. Only add a new specialized `audit-docs` subagent if Pass 4 quality is consistently poor.
> "Default approach: reuse existing agents and only add a new specialized agent if Pass 4 quality is consistently poor. Option A (preferred): Use existing audit-scanner/audit-analyzer for docs sampling + link extraction." -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 5.2

**Set B Position**: 6 named specialized agents with explicit model assignments: `audit-profiler` (Haiku), `audit-scanner` (Haiku), `audit-analyzer` (Sonnet), `audit-comparator` (Sonnet), `audit-consolidator` (Sonnet), `audit-validator` (Sonnet). The findings document also proposes 5 specialized scanner types: `infrastructure_auditor`, `source_code_auditor`, `asset_auditor`, `documentation_auditor`, `cross_reference_synthesizer`.
> "Agent: audit-profiler (Haiku) ... audit-scanner (Haiku) ... audit-analyzer (Sonnet) ... audit-comparator (Sonnet) ... audit-consolidator (Sonnet) ... audit-validator (Sonnet)" -- `cleanup-audit-v2-PRD.md` section 3
> "5 specialized subagent types: infrastructure_auditor, source_code_auditor, asset_auditor, documentation_auditor, cross_reference_synthesizer" -- `cleanup-audit-improvement-findings.md` Finding 12

**Reasoning Chain A**: Conservative approach. Minimize complexity and avoid premature specialization. Test whether existing agents can handle docs before adding new ones.

**Reasoning Chain B**: The generic scanners (6 unnamed parallel scanners) are the root cause of the 44x profiling gap. Specialized agents with documented capabilities, model assignments, and structured output schemas are necessary to produce quality results.

**Evidence Assessment**: B stronger. The quantified gap (12 vs 527+ profiles) provides concrete evidence that generic scanners are insufficient. However, the findings doc and the v2 PRD disagree internally about exactly which 5-6 agents to use.

---

### C-07: Evidence Requirements for KEEP -- Uniform vs Tiered

**Category**: Evidence Requirements
**Stakes**: HIGH

**Set A Position**: Per-file profiles demanded uniformly. Evidence is mandatory for KEEP decisions but the scheme is **not tiered by risk**.
> "Old prompts demanded per-file structured profiles for audited files" -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
> "Per-file evidence schema is not consistently applied outside the small subset of Pass 2 profiles" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 1

**Set B Position**: **Tiered evidence requirements** based on 4 file risk tiers. Tier 1 (Critical) = full 3-field check. Tier 2 (High) = 2-field. Tier 3 (Standard) = relational annotation. Tier 4 (Low) = pattern-match only.
> "Tier 1 (Critical) ... 100% coverage, Full 3-field (references + recency + test coverage) / Tier 2 (High) ... 95%, 2-field / Tier 3 (Standard) ... 80%, Relational / Tier 4 (Low) ... 60%, Pattern-match" -- `cleanup-audit-v2-PRD.md` section 4

**Reasoning Chain A**: The old prompts required evidence for every KEEP decision without exception. The principle is: "Evidence for KEEP is mandatory. Don't just say 'looks legitimate.'" Uniform application prevents lazy classification.

**Reasoning Chain B**: The reflection validation found that requiring full evidence for all ~5,800 files would cost 175K-585K additional tokens, potentially doubling or tripling the audit cost. Tiering by risk gives full evidence to the 10-20% of files where it matters most, while using lightweight checks for low-risk files.

**Evidence Assessment**: B stronger. The token cost analysis in the reflection validation (Dimension 3) provides quantified evidence that uniform evidence is infeasible. Tiering is a necessary cost-control mechanism.

---

### C-08: Budget and Cost Estimates

**Category**: Budget/Cost Estimates
**Stakes**: MEDIUM

**Set A Position**: No explicit token budget numbers. Cost control mentioned via sampling and caps but not quantified.
> "Cost control: Use directory-level sampling for huge trees (sample 5-10 representative docs). Constrain claim verification to structural claims first." -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
> "Avoid unbounded doc analysis and keep outputs scannable." -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 2 (G5)

**Set B Position**: Explicit `--budget` flag with **300K token default**. Proportional phase allocation (5%/25%/35%/20%/15%). Graceful degradation with 5-level cutback priority. Runtime estimates from 8-45 minutes depending on budget tier.
> "`--budget` flag with hard token ceiling ... Default: 300000" -- `cleanup-audit-v2-PRD.md` section 6
> "Minimal: 100K, ~8 min / Standard: 300K, ~18 min / Comprehensive: 500K, ~30 min / Deep: 800K, ~45 min" -- `cleanup-audit-v2-PRD.md` section 6

**Set B also notes** the reflection validation found original proposals underestimated costs by 2-3x:
> "Token cost estimates are systematically low by 2-3x ... After Tier 1: Proposed ~55 min, +25% tokens / Realistic ~80 min, +60-100% tokens" -- `cleanup-audit-reflection-validation.md` Dimension 3

**Reasoning Chain A**: Cost control is important but implementation-level detail. The PRD should focus on what to produce, not micro-manage token allocation.

**Reasoning Chain B**: Without explicit budget controls, the audit is unpredictable and may fail mid-run. Budget enforcement is an architectural concern, not an implementation detail.

**Evidence Assessment**: B stronger. B provides quantified estimates and a concrete enforcement mechanism. A's approach is too vague to be actionable.

---

### C-09: ARCHIVE as a Classification

**Category**: Classification System
**Stakes**: MEDIUM

**Set A Position**: ARCHIVE is a **distinct top-level classification** alongside DELETE and KEEP. Scoped to docs and release artifacts. Requires a suggested destination path.
> "TEMPORAL_ARTIFACTS: Explicitly label docs as one of: KEEP / ARCHIVE (move to archive tree) / DELETE. Provide short rationale and (if ARCHIVE) suggested destination." -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.3

**Set B Position**: ARCHIVE is a **secondary qualifier** on DELETE: `DELETE:archive-first`. It is not a standalone category.
> "DELETE: standard | archive-first" -- `cleanup-audit-v2-PRD.md` section 4
> "v1 CONSOLIDATE -> v2 MODIFY:consolidate-with:[target] ... v1 KEEP -> v2 KEEP:verified or KEEP:unverified" -- `cleanup-audit-v2-PRD.md` section 4 (backward compatibility mapping)

**Reasoning Chain A**: ARCHIVE has different semantics from DELETE. An archived file is preserved for historical value; a deleted file is gone. Making ARCHIVE a qualifier on DELETE conflates two distinct intentions.

**Reasoning Chain B**: ARCHIVE is fundamentally a DELETE with a pre-step (copy to archive tree). The two-tier system avoids proliferating top-level categories while still capturing the distinction. The primary action (what the engineer does) is "remove from this location."

**Evidence Assessment**: Even. Both are valid modeling choices. A is more explicit; B is more composable.

---

### C-10: Cross-Reference / Cross-Boundary Detection

**Category**: Architectural Decisions
**Stakes**: MEDIUM

**Set A Position**: Cross-cutting analysis is handled within the **existing Pass 3** with enhancements (broken reference checklists, large directory assessment blocks). No new architectural component.
> "Pass 3 (cross-cutting): key deltas ... Duplication matrices (compose/deploy/playwright/nginx/deployment systems) are the best part of the new output" -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
> The vNext PRD adds broken-reference sweeps to Pass 3 and Pass 4 but does not introduce dependency graph building.

**Set B Position**: Cross-reference synthesis is a **dedicated Phase 3** that builds a **directed dependency graph** (files as nodes, import/export as edges), identifies orphan nodes, applies confidence scoring by hop distance, and resolves INVESTIGATE classifications.
> "Phase 3: Cross-Reference Synthesis (Sonnet comparator) ... Build directed dependency graph from structured scanner output / Detect cross-boundary dead code / Produce duplication matrices" -- `cleanup-audit-v2-PRD.md` section 5
> "P1 (Cross-Reference Resolution Phase) ... Highest ROI improvement ... Build a directed graph (files as nodes, import/export as edges)" -- `cleanup-audit-improvement-proposals.md` Proposal 1

**Reasoning Chain A**: The existing cross-cutting pass already produces duplication matrices. The improvements needed are mostly output formatting (checklists, directory blocks, broken references). The pass architecture is sound.

**Reasoning Chain B**: The current parallel scanners cannot detect cross-boundary issues because each operates in isolation. A post-scan synthesis phase that builds a dependency graph is the only mechanism that can detect cross-boundary dead code. This is "the highest ROI improvement" per the 4-agent debate.

**Evidence Assessment**: B stronger. The specific example of cross-boundary dead code (files used only via dynamic import, API endpoints called from frontend) demonstrates a capability gap that output formatting alone cannot address.

---

### C-11: Spot-Check Validation

**Category**: Quality Gates
**Stakes**: MEDIUM

**Set A Position**: No explicit spot-check validation pass. Verification is limited to acceptance criteria checking that sections exist and have correct format.
> Acceptance criteria focus on section presence: "A2. Pass 4 output includes: overlap groups, broken references checklist ..." -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 7
> No mention of re-verifying a sample of classifications.

**Set B Position**: Dedicated **10% spot-check** by `audit-validator` agent in Phase 4. If agreement rate < 85%, a warning banner is added to the report.
> "Validation Process (10% spot-check): 1. Random sample 10% of all classifications (stratified by tier) 2. For each sampled file: Re-run evidence gathering independently / Compare classification with original / If disagreement: flag as 'disputed' ... If agreement rate < 85%: add warning to report header" -- `cleanup-audit-v2-PRD.md` section 5 (Phase 4)

**Reasoning Chain A**: The PRD focuses on what outputs must exist, assuming that correct prompts will produce correct outputs. Testing is via golden fixtures and regression checks.

**Reasoning Chain B**: The reflection validation noted that the v1 spec already promised "10% spot-check validation" but it was never implemented. LLM subagents can produce plausible but incorrect output; runtime validation catches this. The 85% threshold provides a meaningful quality signal.

**Evidence Assessment**: B stronger. Runtime validation is a defense-in-depth mechanism that golden fixtures cannot replace (fixtures test the prompt, not the actual subagent behavior on real data).

---

### C-12: Phase 0 / Pre-Audit Profiling

**Category**: Phase Structure
**Stakes**: MEDIUM

**Set A Position**: No pre-audit profiling phase. The audit begins directly with Pass 1 (Surface Scan).
> The vNext PRD section 4.1 lists passes starting with "Pass 1: Surface Scan (existing)." No Phase 0 or pre-pass step is defined.

**Set B Position**: **Phase 0: Profile & Plan** is a mandatory pre-pass that detects domains, classifies files into risk tiers, generates batch manifests, and auto-generates config if absent.
> "Phase 0: Profile & Plan (Haiku, 30-60s) ... Detect domains / Classify files into risk tiers (1-4) / Generate batch manifest (JSON) / Auto-generate config if absent" -- `cleanup-audit-v2-PRD.md` section 5

**Reasoning Chain A**: The current 3-pass architecture works. Adding infrastructure should happen within the existing pass framework, not by prepending a new phase.

**Reasoning Chain B**: Without domain detection and file tiering, scanners cannot be domain-aware, batch decomposition is impossible, and coverage tracking has no manifest to track against. Phase 0 is a structural prerequisite for most other improvements.

**Evidence Assessment**: B stronger. The reflection validation's dependency chain analysis shows that cross-reference synthesis (Phase 3) depends on structured scanner output, which depends on batch decomposition (Phase 2 infra), which depends on profiling (Phase 0).

---

### C-13: Recommendation Category Count

**Category**: Classification System
**Stakes**: MEDIUM

**Set A Position**: 5 output buckets: DELETE, KEEP, ARCHIVE, FLAG, BROKEN_REFERENCES (plus REMAINING/NOT_YET_AUDITED). REVIEW is retained from v1 but enhanced.
> Section 2 of vNext PRD lists: "BROKEN_REFERENCES ... ARCHIVE ... FLAG ... REMAINING / NOT_YET_AUDITED"
> Pass 4 adds: "KEEP / ARCHIVE / DELETE" for temporal artifacts

**Set B Position**: 4 primary categories (DELETE/KEEP/MODIFY/INVESTIGATE) with 13+ secondary qualifiers. REVIEW is eliminated entirely; its function is replaced by INVESTIGATE.
> The findings doc notes: "Old approach used 5 categories: DELETE, FLAG, CONSOLIDATE, ARCHIVE, KEEP. The new version uses 3: DELETE, REVIEW, KEEP." -- `cleanup-audit-improvement-findings.md` Finding 10
> The v2 PRD maps: "v1 REVIEW -> v2 INVESTIGATE:insufficient-evidence" -- `cleanup-audit-v2-PRD.md` section 4

**Reasoning Chain A**: Each distinct action type (archive, flag, broken reference) deserves its own named section in the output for scanability.

**Reasoning Chain B**: Flat categories proliferate and create ambiguity. A composable two-tier system is more systematic and handles edge cases via qualifiers rather than new top-level categories.

**Evidence Assessment**: B stronger. The two-tier system is more extensible and handles the same use cases with a cleaner model.

---

### C-14: Batch Decomposition -- Static vs Dynamic

**Category**: Architectural Decisions
**Stakes**: MEDIUM

**Set A Position**: No explicit batch decomposition strategy. The PRD does not specify how files are assigned to scanners.
> The vNext PRD mentions "Use directory-level sampling for huge trees" and "batch-size N" flag in the command syntax (from COMMANDS.md) but provides no batch generation mechanism.

**Set B Position**: **Dynamic batch decomposition** with risk-weighted parallel scanning. Phase 0 generates a batch manifest. Risk > 0.7 gets deep profile; Risk 0.4-0.7 gets standard; Risk < 0.4 gets shallow.
> "Two-Phase Risk-Weighted Scanning: Phase 1 (Pre-audit, 30-60s): Lightweight directory analysis producing batch manifest (JSON) mapping scanner IDs to file lists, risk scores per directory" -- `cleanup-audit-improvement-proposals.md` Proposal 6
> "Generate batch manifest: group files by domain, assign to scanner batches" -- `cleanup-audit-v2-PRD.md` section 5 (Phase 0)

**Reasoning Chain A**: Batch decomposition is an implementation concern that the prompt rules can handle implicitly.

**Reasoning Chain B**: The old manual approach had 26 targeted batches with explicit file lists and produced 44x more profiles. Without explicit batch decomposition, scanners have no documented file assignments, depth calibration, or coverage guarantees.

**Evidence Assessment**: B stronger. The 44x profiling gap is directly attributable to the lack of batch decomposition per the findings analysis.

---

### C-15: Spec-Implementation Gap Recognition

**Category**: Scope Decisions
**Stakes**: HIGH

**Set A Position**: The gap analysis compares old manual prompts to new automated output. It does **not examine the current v1 spec** for unimplemented promises. All proposals are framed as "new features to add."
> The gap analysis references "Old prompt set" and "New audit output" but never references the current `sc:cleanup-audit` spec (`/config/.claude/commands/sc/cleanup-audit.md`).

**Set B Position**: The reflection validation discovered that the v1 spec already promises 5 categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check -- **none of which were implemented**. The v2 PRD makes "Phase 0: Enforce Existing Spec" the top priority.
> "The current sc:cleanup-audit spec already includes: 5 classification categories: DELETE/CONSOLIDATE/MOVE/FLAG/KEEP / Coverage tracking / Incremental checkpointing / Evidence-gated classification / Spot-check validation: 10%" -- `cleanup-audit-reflection-validation.md` Dimension 2
> "v2 Requirement: All v1 spec promises MUST be implemented before any new features are added. This is Phase 0." -- `cleanup-audit-v2-PRD.md` section 2

**Reasoning Chain A**: The analysis focuses on observable output quality deltas between old and new approaches. The spec document was not in scope.

**Reasoning Chain B**: Adding features to a spec that already has unimplemented features widens the gap. The root cause of the quality deficit may be implementation failure, not spec insufficiency.

**Evidence Assessment**: B stronger. This is a critical insight that fundamentally reframes the problem. Set A's proposals may partially duplicate features the spec already requires.

---

### C-16: Coverage Tracking and Guarantee

**Category**: Quality Gates
**Stakes**: MEDIUM

**Set A Position**: Mentions "REMAINING / NOT_YET_AUDITED coverage accounting" as a schema requirement but provides no coverage thresholds or per-tier tracking.
> "REMAINING / NOT_YET_AUDITED coverage accounting" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 2 (G3)

**Set B Position**: Tiered coverage contracts: Critical 100%, High 95%, Standard 80%, Low 60%. Manifest-first execution with per-file tracking. Coverage below threshold triggers WARN, never blocks.
> "Critical: deployment scripts, CI/CD, migrations -> 100% coverage / High: configs, compose, env templates -> 95% / Standard: source code, tests -> 80% / Low: assets, generated, docs -> 60%" -- `cleanup-audit-improvement-proposals.md` Proposal 3
> "Coverage Threshold: Tier 1 >= 100%, Tier 2 >= 90% ... Warn if below, never block" -- `cleanup-audit-v2-PRD.md` section 9

**Reasoning Chain A**: Knowing what was not audited is important, but setting numeric thresholds is premature.

**Reasoning Chain B**: Without thresholds, "coverage tracking" is meaningless. Tiered thresholds aligned with file risk ensure that the most important files are always examined.

**Evidence Assessment**: B stronger. Concrete thresholds make the coverage guarantee testable and actionable.

---

### C-17: Output Format -- Markdown vs JSON

**Category**: Architectural Decisions
**Stakes**: LOW

**Set A Position**: Pass summaries as **Markdown** files. Output artifacts are `pass1-summary.md`, `pass2-summary.md`, `pass3-summary.md`, `pass4-summary.md`, `FINAL-REPORT.md`, plus `progress.json` and `known-issues.json`.
> "pass1/pass1-summary.md ... pass4/pass4-summary.md ... FINAL-REPORT.md" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.2

**Set B Position**: Phase summaries as **JSON** files for machine consumption. Separate human-readable FINAL-REPORT.md. Scanner outputs are structured JSON conforming to a schema.
> "pass1-summary.json ... pass2-summary.json ... pass3-summary.json ... dependency-graph.json ... duplication-matrix.json" -- `cleanup-audit-v2-PRD.md` section 8

**Reasoning Chain A**: Markdown is human-readable and directly scannable. Engineers reviewing audit results want to read prose, not parse JSON.

**Reasoning Chain B**: JSON enables programmatic consumption, schema validation, and inter-phase data flow. The FINAL-REPORT.md serves human readers; intermediate artifacts serve the pipeline.

**Evidence Assessment**: B stronger. JSON intermediate outputs enable schema validation (anti-lazy enforcement) and structured cross-phase data flow. The human-readable report is still present.

---

### C-18: Quality Gate on Spot-Check Failure

**Category**: Quality Gates
**Stakes**: LOW

**Set A Position**: No spot-check mechanism defined. If a quality gate fails, the remediation is undefined.
> Acceptance criteria are pass/fail on section presence. No failure remediation specified.

**Set B Position**: Spot-check agreement rate < 85% adds a **warning banner** to the report but does **not block** report generation.
> "If agreement rate < 85%: add warning to report header" -- `cleanup-audit-v2-PRD.md` section 5 (Phase 4)
> "Spot-Check Agreement | Phase 4 | >= 85% agreement rate | Add warning banner to report" -- `cleanup-audit-v2-PRD.md` section 9

**Reasoning Chain A**: N/A (not addressed).

**Reasoning Chain B**: Quality signals should inform, not block. A warning banner alerts users to lower confidence without preventing them from using the report.

**Evidence Assessment**: B stronger (A does not address the topic).

---

### C-19: .env Handling Approach

**Category**: Scope Decisions
**Stakes**: LOW

**Set A Position**: `.env*` handling is a **P2 enhancement** -- a key-presence matrix comparing keys across `.env*` templates.
> "P2: .env key matrix comparison (cheap, high impact) ... Extract keys across .env* templates. Output a key-presence matrix." -- `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`

**Set B Position**: `.env*` handling is a **Phase 1 correctness fix** -- read actual file contents to distinguish real credentials from template values. Key matrix is not mentioned. Credential scanning is rated **CRITICAL**.
> "Credential File Scanning Fix (F6) | HIGH | CRITICAL | False negative on real credentials is a correctness failure" -- `cleanup-audit-improvement-proposals.md` Tier 1 table
> "For any .env* file ... read actual contents and flag real credentials vs templates" -- `cleanup-audit-improvement-findings.md` Finding 6

**Reasoning Chain A**: The key matrix is a lightweight enhancement that reveals config drift. Credential detection is a separate security concern.

**Reasoning Chain B**: The new audit misidentified real credentials in `.env.production` as template values -- this is a correctness failure, not an enhancement. Reading actual .env content is non-negotiable and should be an early fix.

**Evidence Assessment**: B stronger. A false negative on real credentials is a correctness bug with security implications, not a nice-to-have enhancement.

---

### C-20: Progressive Depth Across Passes

**Category**: Architectural Decisions
**Stakes**: LOW

**Set A Position**: Not explicitly addressed. The PRD describes what each pass should output but does not specify read-depth escalation across passes.

**Set B Position**: **Two-level signal-triggered depth** -- 50-line default with full-file read triggered by specific signals (credential imports, TODO/FIXME, complex conditionals, eval, file size > 300 lines).
> "Default: 50-line read per file. Triggers for full-file read: Credential-adjacent imports, TODO/FIXME/HACK, Complex conditional logic, eval/exec/dangerouslySetInnerHTML, File size > 300 lines" -- `cleanup-audit-improvement-proposals.md` Proposal 12

The original findings proposed a 4-level system but the debate simplified it to 2 levels:
> "Two-level triggered approach (50 lines default, full file on signal triggers), not four-level ladder" -- `cleanup-audit-improvement-proposals.md` Tier 3 table

**Reasoning Chain A**: Depth is an implementation detail handled by the pass rules.

**Reasoning Chain B**: Without explicit depth rules, scanners default to shallow reads. Signal-triggered escalation balances cost and thoroughness.

**Evidence Assessment**: B stronger. Explicit depth rules prevent the shallow scanning problem identified in Finding 11.

---

### C-21: Checkpointing Granularity

**Category**: Architectural Decisions
**Stakes**: LOW

**Set A Position**: `progress.json` updated at pass level with pass status fields.
> "progress.json (updated schema): passes.pass4_docs.status / passes.pass4_docs.sampled_files / passes.pass4_docs.broken_refs_count" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 6.1

**Set B Position**: `progress.json` updated **after every batch** within a phase, enabling mid-phase resume.
> "Checkpointing: After each batch completes, update progress.json: { current_phase: 1, batches_completed: 4, batches_total: 12, files_examined: 240, ... }" -- `cleanup-audit-v2-PRD.md` section 5 (Phase 1)
> "`--resume` flag: Resume from last checkpoint" -- `cleanup-audit-v2-PRD.md` section 7

**Reasoning Chain A**: Pass-level checkpointing is sufficient for tracking progress.

**Reasoning Chain B**: For large repos with many batches per phase, pass-level checkpointing means losing all progress on session interruption. Batch-level checkpointing enables `--resume` within a phase.

**Evidence Assessment**: B stronger. Batch-level checkpointing is strictly more granular and enables the `--resume` flag which is a concrete user need.

---

### C-22: Claim Spot-Check Scope (Docs)

**Category**: Documentation Audit
**Stakes**: LOW

**Set A Position**: Claim spot-checks verify **3-5 structural claims per doc** across sampled docs. Claim types: referenced file exists, referenced script name exists, referenced port matches spec, referenced docker-compose file exists.
> "CLAIM_SPOT_CHECKS: For sampled docs: verify 3-5 structural claims per doc" -- `SC_CLEANUP_AUDIT_VNEXT_PRD.md` section 4.3

**Set B Position**: Claim spot-checks verify **3 claims per doc**, only for **API-reference and setup-guide** category docs. Other doc categories (architecture, conceptual) are excluded from claim checking.
> "Claim spot-checking: 3 claims per doc, only for API-reference and setup-guide categories" -- `cleanup-audit-improvement-proposals.md` Proposal 9

**Reasoning Chain A**: 3-5 claims per doc across all sampled docs provides broader coverage.

**Reasoning Chain B**: Narrowing to 3 claims and only API/setup docs reduces token cost while focusing on the doc types most likely to have verifiable structural claims.

**Evidence Assessment**: Even. A provides broader coverage; B provides better cost control. The difference is minor.

---

## Conflict Summary Table

| ID | Category | Set A Position (brief) | Set B Position (brief) | Evidence | Stakes |
|----|----------|----------------------|----------------------|----------|--------|
| C-01 | Phase Structure | 4 passes (add Pass 4 Docs) | 5 phases (add Phase 0 Profile + Phase 4 Consolidation) | B stronger | HIGH |
| C-02 | Scope Decisions | Docs audit mandatory (P0) | Docs audit opt-in (Phase 5) | Even | HIGH |
| C-03 | Classification System | Flat categories + new buckets (ARCHIVE, FLAG) | Two-tier: 4 primary + 13 qualifiers | B stronger | HIGH |
| C-04 | Known-Issues Handling | Sequential registry loaded before passes | Post-hoc dedup in consolidator | A stronger (cross-run) | HIGH |
| C-05 | Priority Ordering | P0 = docs pass + known-issues | Phase 0 = enforce existing spec first | B stronger | HIGH |
| C-06 | Architectural Decisions | Reuse existing agents | 6 specialized agents with model assignments | B stronger | MEDIUM |
| C-07 | Evidence Requirements | Uniform evidence for all KEEP | 4-tier evidence by file risk | B stronger | HIGH |
| C-08 | Budget/Cost Estimates | No explicit budget; qualitative cost control | 300K token default, --budget flag, proportional allocation | B stronger | MEDIUM |
| C-09 | Classification System | ARCHIVE as top-level category | ARCHIVE as DELETE:archive-first qualifier | Even | MEDIUM |
| C-10 | Architectural Decisions | Cross-cutting within existing Pass 3 | Dedicated Phase 3 with dependency graph | B stronger | MEDIUM |
| C-11 | Quality Gates | No spot-check validation | 10% spot-check, 85% agreement threshold | B stronger | MEDIUM |
| C-12 | Phase Structure | No pre-audit profiling | Phase 0: Profile & Plan (Haiku, 30-60s) | B stronger | MEDIUM |
| C-13 | Classification System | 5+ flat output buckets | 4 primary + 13 qualifiers (composable) | B stronger | MEDIUM |
| C-14 | Architectural Decisions | No batch decomposition strategy | Dynamic batch manifest from Phase 0 | B stronger | MEDIUM |
| C-15 | Scope Decisions | Does not examine v1 spec gaps | Phase 0: enforce existing unimplemented spec | B stronger | HIGH |
| C-16 | Quality Gates | Coverage accounting (no thresholds) | Tiered coverage contracts (100/95/80/60%) | B stronger | MEDIUM |
| C-17 | Architectural Decisions | Markdown intermediate outputs | JSON intermediate + Markdown final report | B stronger | LOW |
| C-18 | Quality Gates | No failure remediation defined | Warning banner on <85% spot-check agreement | B stronger | LOW |
| C-19 | Scope Decisions | .env key matrix as P2 enhancement | .env credential scan as Phase 1 correctness fix | B stronger | LOW |
| C-20 | Architectural Decisions | Depth not specified | Two-level signal-triggered depth | B stronger | LOW |
| C-21 | Architectural Decisions | Pass-level checkpointing | Batch-level checkpointing with --resume | B stronger | LOW |
| C-22 | Documentation Audit | 3-5 claims/doc, all sampled docs | 3 claims/doc, API-reference and setup-guide only | Even | LOW |

---

## Conflict Statistics

- **Total conflicts found**: 22
- **HIGH stakes**: 7 (C-01, C-02, C-03, C-04, C-05, C-07, C-15)
- **MEDIUM stakes**: 9 (C-06, C-08, C-09, C-10, C-11, C-12, C-13, C-14, C-16)
- **LOW stakes**: 6 (C-17, C-18, C-19, C-20, C-21, C-22)
- **Set A has stronger evidence**: 1 time (C-04)
- **Set B has stronger evidence**: 18 times
- **Even / Both valid**: 3 times (C-02, C-09, C-22)

---

## Key Observation

The disagreements between Set A and Set B are **not surface-level differences** -- they reflect a **fundamental difference in problem framing**. Set A frames the problem as "the old manual prompts caught things the new automated output misses; add the missing capabilities." Set B frames the problem as "the current system has a systemic architectural failure (generic scanners, no structured output, unimplemented spec promises); fix the architecture first, then add capabilities."

This framing difference cascades into nearly every conflict. Set A proposes **additive changes** to the existing 3-pass structure (add Pass 4, add ARCHIVE bucket, add known-issues registry). Set B proposes **structural changes** that reshape the entire execution flow (add Phase 0 profiling, restructure into 5 phases, implement two-tier classification, enforce existing spec before adding features).

The single area where Set A is clearly stronger is **C-04 (Known-Issues Handling)**: Set A's cross-run registry solves a problem (repeated re-discovery across audit runs) that Set B's within-run dedup does not address. This is likely because Set B's multi-agent analysis was focused on per-run quality and did not fully consider the repeated-audit-over-time use case that Set A identified from the legacy prompts' 34-item known-issues list.

The merger strategy should adopt Set B's architectural framework (5-phase structure, two-tier classification, tiered evidence, explicit budget) while incorporating Set A's cross-run known-issues registry and evaluating the docs audit as a bounded mandatory pass rather than fully deferring it.
