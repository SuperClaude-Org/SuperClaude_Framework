# Wave 2: Synthesis Judge -- Merge Verdicts

**Date**: 2026-02-20
**Judge**: Synthesis Judge (System Architect agent)
**Input**: Wave 1 outputs (coverage matrix, strength rankings, flaw analysis, conflict register)
**Advocate Status**: Wave 2 advocate files were not available at judgment time. Verdicts are based on the evidence documented in Wave 1 analysis, which is comprehensive and sufficient for resolution.

---

## Part 1: Verdicts on All 22 Conflicts

---

### C-01: Phase/Pass Structure (Count and Architecture)
**Set A Position**: 4 passes -- keep existing 3-pass structure and add a 4th Pass for Docs Quality.
**Set B Position**: 5 phases -- add Phase 0 (Profile & Plan) before scanning and Phase 4 (Consolidation & Validation) after scanning; no dedicated docs pass in the main flow.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-03 (Pass 4 depends on undefined infrastructure -- if passes 1-3 emit markdown, Pass 4 cannot programmatically consume their output). F-B-04 (Phase 0 auto-config is a correctness risk if framework detection fails).

**VERDICT**: B

**Reasoning**: The conflict register's own key observation identifies the root issue: Set A frames the problem as "add missing capabilities to the existing structure" while Set B frames it as "fix the systemic architectural failure first." The flaw analysis supports Set B's framing -- F-A-03 demonstrates that adding Pass 4 atop unstructured markdown outputs creates a dependency on infrastructure that does not exist. Set B's Phase 0 (profiling) and Phase 4 (consolidation) address the architectural prerequisites that make any content pass viable.

Set A's simplicity argument has merit for initial adoption, but the evidence from the spec-implementation gap (the v1 spec already promised features that were never built) suggests that additive changes to a structurally weak architecture will repeat the same failure pattern. The existing 3-pass structure is not "working" -- it is producing 12 profiles instead of 527+.

The mitigation for F-B-04 (auto-config risk) is addressed by the `--dry-run` flag that shows generated config before committing to a full audit run. This is a bounded risk with a concrete mitigation.

**For the Merged Spec**: Adopt Set B's 5-phase structure (Phase 0: Profile & Plan, Phase 1: Surface Scan, Phase 2: Structural Audit, Phase 3: Cross-Reference Synthesis, Phase 4: Consolidation & Validation). Documentation audit is incorporated as an opt-in extension that executes within Phase 2 (structural) when activated via `--pass-docs`, not as a separate sequential pass. The docs audit uses the structured scanner output schema from Phase 1 as input, avoiding the infrastructure dependency that F-A-03 identified.

---

### C-02: Documentation Audit -- Mandatory vs Opt-In
**Set A Position**: Pass 4 Docs Quality is mandatory when `--pass all` is used, classified as P0 (must-have).
**Set B Position**: Documentation audit is opt-in via `--pass-docs`, deferred to Phase 5 of implementation, capped at 20% of token budget.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-01 (no token budget model -- adding a mandatory pass without cost estimates is irresponsible). F-B-18 (deferring docs to Phase 5 creates an incoherent MVP since the docs gap was the primary finding that motivated the improvement effort). F-B-02 (token estimates are still underestimated even after correction).

**VERDICT**: HYBRID

**Reasoning**: Both positions have genuine weaknesses identified by the flaw hunter. Set A mandates a pass without any cost model (F-A-01), which is reckless. Set B defers the feature that motivated the entire effort (F-B-18), which is strategically incoherent. Neither position taken alone is defensible.

The resolution is to separate the docs audit into two tiers. A minimal docs audit (broken reference detection + temporal artifact classification) is cheap, high-signal, and can execute within the cross-reference synthesis phase since broken references are a special case of cross-boundary analysis. This minimal tier should be included in the core flow when `--pass all` is specified. The full docs audit (overlap groups, claim spot-checks, content quality assessment) is expensive and should be opt-in via `--pass-docs` with a 20% budget cap.

This preserves Set A's insight (the docs gap is the primary user complaint) while respecting Set B's cost-benefit analysis (the full docs audit is expensive relative to its incremental value over the minimal version).

**For the Merged Spec**: Two-tier docs audit. **Tier 1 (included in `--pass all`)**: Broken reference sweep + temporal artifact classification (KEEP/ARCHIVE/DELETE). Runs within Phase 3 cross-reference synthesis. Budget: 5-8% of total. **Tier 2 (opt-in via `--pass-docs`)**: Content overlap groups + claim spot-checks + full docs quality assessment. Runs as a Phase 2 extension. Budget: capped at 20% of total. Both tiers use Set A's output format specification (SCOPE, CONTENT_OVERLAP_GROUPS, BROKEN_REFERENCES, CLAIM_SPOT_CHECKS, TEMPORAL_ARTIFACTS -- with only the applicable sections populated per tier).

---

### C-03: Classification System -- Categories and Structure
**Set A Position**: Flat categories with new buckets (ARCHIVE, FLAG, BROKEN_REFERENCES) added alongside existing DELETE/REVIEW/KEEP.
**Set B Position**: Two-tier composable system with 4 primary actions (DELETE/KEEP/MODIFY/INVESTIGATE) and 13 secondary qualifiers.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-11 (INVESTIGATE may become a dumping ground without limits). F-B-19 (backward compatibility mapping has semantic drift -- v1 REVIEW maps to INVESTIGATE:insufficient-evidence but they mean different things).

**VERDICT**: B

**Reasoning**: Set B's two-tier system is architecturally superior for three reasons. First, it is composable -- new qualifiers can be added without schema changes, while Set A's flat approach requires a new top-level category for each new distinction. Second, it provides a backward compatibility mapping from v1 categories, which Set A does not address. Third, the primary/qualifier structure captures important distinctions (e.g., DELETE:archive-first vs DELETE:standard) that flat categories cannot express without proliferation.

The flaw concerns (F-B-11, F-B-19) are valid and must be mitigated in the merged spec. For F-B-11, a hard cap of 15% on INVESTIGATE classifications prevents dumping. For F-B-19, add an `INVESTIGATE:human-review-needed` qualifier that captures the semantic intent of v1's REVIEW category (human should look at this) as distinct from `INVESTIGATE:insufficient-evidence` (audit could not determine classification).

**For the Merged Spec**: Adopt Set B's two-tier classification system with these modifications: (1) Add `INVESTIGATE:human-review-needed` qualifier to preserve the semantic intent of v1 REVIEW. (2) Add a hard cap: if INVESTIGATE exceeds 15% of examined files, trigger a re-analysis pass on those files with elevated budget. (3) Retain Set B's backward compatibility mapping table with the corrected REVIEW mapping. (4) The report must display classifications in a scannable format that surfaces the primary action prominently (Set A's concern about scanability is valid).

---

### C-04: Known-Issues Handling -- Registry vs Post-Hoc Dedup
**Set A Position**: Sequential JSON registry loaded before passes, with signature-based suppression and ALREADY_TRACKED output section. Enables cross-run deduplication.
**Set B Position**: Post-hoc deduplication in the consolidator agent. Zero overhead during scanning. Within-run only.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-04 (registry has no versioning, lifecycle, or staleness management -- will accumulate noise over time).

**VERDICT**: HYBRID

**Reasoning**: The conflict register correctly identifies that these solve different problems. Set B's post-hoc dedup solves within-run deduplication (do not double-count findings across phases in a single audit). Set A's registry solves cross-run deduplication (do not re-flag known issues from prior audits). Both problems are real and both solutions are needed.

Set B's approach is the right mechanism for within-run dedup because it preserves scanning parallelism and has near-zero overhead (500 tokens in the consolidator prompt). Set A's registry is the right mechanism for cross-run suppression because it enables the weekly-audit use case (U2 in Set A's user stories).

However, F-A-04 raises a legitimate concern about registry lifecycle. The registry needs TTL per entry, automatic staleness detection (file no longer exists in repo), and a max-entry limit.

**For the Merged Spec**: Two mechanisms. **(1) Within-run dedup (Phase 4)**: Set B's consolidator-based approach. Group findings by file, cluster by issue category, keep highest-severity, mark cross-phase-confirmed as high confidence, remove duplicates. Cost: ~500 tokens. **(2) Cross-run registry (opt-in, Phase 5)**: Set A's JSON schema with additions -- TTL field (default: 90 days), auto-prune entries where the file no longer exists, max 200 entries with LRU eviction, `--known-issues <path>` flag to activate. The registry is loaded as read-only context for the consolidator (not injected into scanner prompts), preserving parallelism.

---

### C-05: Priority Ordering of Improvements
**Set A Position**: P0 = Pass 4 Docs Quality + Known-issues suppression registry. P1 = Broken-reference checklist, FLAG section, large directory assessment. P2 = .env key matrix.
**Set B Position**: Phase 0 = Enforce existing spec. Phase 1 = Correctness fixes (credential scanning, gitignore). Phase 2 = Infrastructure (profiling, batch decomposition, coverage). Phase 3 = Depth (evidence KEEP, cross-reference, file-type rules). Phase 4 = Quality. Phase 5 = Extensions (docs audit, calibration).
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-02 (Set A never examines spec-implementation gap -- risks repeating v1 failure). F-A-14 (Set A's backlog lacks effort estimates and dependency ordering). F-B-14 (Set B's effort estimates are unrealistically low -- Phase 0 at "4-6 hours" for 5 major features is probably 15-25 hours).

**VERDICT**: B

**Reasoning**: Set B's phased ordering is strictly superior because it respects dependency chains. The reflection analysis discovered that the highest-priority improvement (cross-reference synthesis, P1 in Set B's debate) depends on structured scanner output, which depends on batch decomposition, which depends on repository profiling. This chain (P11 -> P6 -> P1 -> P10) was invisible in Set A's flat backlog.

More fundamentally, Set B's "Phase 0: Enforce Existing Spec" addresses the root cause of the v1 quality deficit. Set A's proposal to add new features atop unimplemented existing features is the exact pattern that led to v1's spec-implementation gap. This is the single strongest argument in the entire analysis -- you cannot build new capabilities on a foundation that does not enforce its own promises.

The mitigation for F-B-14 (unrealistic effort estimates) is to benchmark by implementing one concrete feature and extrapolating, rather than adjusting estimates speculatively.

**For the Merged Spec**: Adopt Set B's 5-phase implementation roadmap (Phase 0: Enforce Existing Spec -> Phase 1: Correctness Fixes -> Phase 2: Infrastructure -> Phase 3: Depth -> Phase 4: Quality -> Phase 5: Extensions). Insert Set A's unique contributions into appropriate phases: directory-level assessment blocks into Phase 4 consolidation, .env key matrix into Phase 1, content overlap group output spec into Phase 5. Label all effort estimates as "unvalidated -- benchmark before sprint planning."

---

### C-06: Subagent Architecture
**Set A Position**: Reuse existing agents. Only add a specialized `audit-docs` subagent if quality is consistently poor.
**Set B Position**: 6 named specialized agents with explicit model assignments (Haiku for mechanical tasks, Sonnet for semantic analysis).
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-06 (scanner output schema is overly complex for Haiku -- high malformed JSON rates likely). F-B-12 (findings document exaggerates old system capabilities by conflating human-guided output with automated capability).

**VERDICT**: HYBRID

**Reasoning**: Set B's agent specialization addresses the documented root cause of the profiling gap (generic unnamed scanners produced 12 profiles vs 527+). The model assignment strategy (Haiku for fast/cheap mechanical tasks, Sonnet for semantic analysis) is cost-effective and well-reasoned.

However, F-B-06 raises a legitimate concern: asking Haiku to produce complex nested JSON with arrays of import references and export targets may produce high malformation rates. The mitigation is to simplify the Phase 1 (Haiku) schema to essential fields only (path, classification, confidence, evidence_summary) and move complex structured fields (import_references, export_targets, external_dependencies) to Phase 2 (Sonnet analyzers). This respects each model's strengths.

Set A's conservative approach (reuse existing agents) is the right strategy for Phase 0-1 of implementation. Progressive specialization in Phase 2+ aligns with Set B's target architecture without requiring all 6 agents to be implemented upfront.

**For the Merged Spec**: Target architecture is Set B's 6-agent system with model assignments. Implementation starts with Set A's conservative approach (reuse existing scanners) for Phase 0-1, adding specialized agents incrementally. Modify the Phase 1 Haiku schema to contain only essential fields (path, classification, primary_action, qualifier, confidence, evidence_text). Complex structured fields (import_references, export_targets, dependency arrays) move to Phase 2 Sonnet analyzers. This reduces Haiku malformation risk while preserving the dependency graph data pipeline.

---

### C-07: Evidence Requirements for KEEP -- Uniform vs Tiered
**Set A Position**: Per-file profiles demanded uniformly. Evidence is mandatory for all KEEP decisions without tiering by risk.
**Set B Position**: Tiered evidence requirements based on 4 file risk tiers (Tier 1: full 3-field, Tier 2: 2-field, Tier 3: relational, Tier 4: pattern-match).
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-07 (coverage tier targets are not empirically validated -- 95% on Tier 2 may be infeasible within budget). F-B-08 (evidence-mandatory KEEP for Tier 1-2 conflicts with budget constraints at ~87 tokens per file).

**VERDICT**: B

**Reasoning**: The token cost analysis in the reflection validation (Dimension 3) provides quantified evidence that uniform evidence requirements for all ~5,800 files would cost 175K-585K additional tokens, potentially tripling the audit cost. Uniform evidence is theoretically desirable but practically infeasible within any reasonable token budget.

Tiering by risk is the only mechanism that delivers full evidence for the files that matter most (deployment scripts, CI/CD, migration files) while using lightweight checks for low-risk files (assets, vendor code, generated files). This is a necessary cost-control mechanism, not a quality compromise.

The flaw findings (F-B-07, F-B-08) correctly identify that the tier targets need empirical validation. The merged spec must label these as initial estimates subject to benchmarking.

**For the Merged Spec**: Adopt Set B's tiered evidence requirements with these modifications: (1) Tier targets are labeled "initial estimates -- validate on benchmark repo before finalizing." (2) Tier 2 relaxed from "2-field mandatory" to "1-field mandatory, 2-field target" to resolve F-B-08's budget conflict. (3) Add "evidence depth actually achieved" as a report metric so users can see what was possible within their budget. (4) The principle from Set A is preserved as a quality aspiration: "All KEEP decisions should have evidence. Tiering determines depth of evidence, not whether evidence exists."

---

### C-08: Budget and Cost Estimates
**Set A Position**: No explicit token budget numbers. Cost control mentioned via sampling and caps but not quantified.
**Set B Position**: Explicit `--budget` flag with 300K token default, proportional phase allocation (5/25/35/20/15%), graceful degradation, 4 runtime scenarios.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-01 (Set A has zero cost estimates -- engineers cannot plan). F-B-02 (Set B's estimates are still underestimated -- 90 tokens per file is insufficient for 8-field profiles). F-B-07 (coverage targets may be infeasible within default budget).

**VERDICT**: B

**Reasoning**: This is one of the clearest verdicts. A PRD for a token-consuming tool that provides zero cost estimates (Set A) is fundamentally incomplete. Set B provides concrete estimates, a budget enforcement mechanism, and graceful degradation -- all of which are architectural requirements, not implementation details.

F-B-02's concern about remaining underestimation is valid. The merged spec should increase the default budget recommendation and prominently note that all estimates are unvalidated.

**For the Merged Spec**: Adopt Set B's budget system with modifications: (1) Increase default budget recommendation from 300K to 500K based on flaw analysis evidence that 300K is insufficient for "Standard" coverage. (2) Add a `--dry-run` step that runs Phase 0 only and reports estimated token cost for the full audit at each depth level. (3) All budget estimates in the spec are labeled "UNVALIDATED -- benchmark on real repos before hardcoding." (4) Graceful degradation order is configurable via `--degrade-priority` flag (addressing F-B-09). (5) Phase allocation percentages are advisory, not hard-wired -- phases can borrow from underutilized phases.

---

### C-09: ARCHIVE as a Classification
**Set A Position**: ARCHIVE is a distinct top-level classification alongside DELETE and KEEP, with a required destination path.
**Set B Position**: ARCHIVE is a secondary qualifier on DELETE: `DELETE:archive-first`.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-12 (ARCHIVE destination guidance is underspecified in Set A).

**VERDICT**: B

**Reasoning**: The semantic question is: "Is archiving a different action from deleting, or is it the same action with a pre-step?" Set B's framing is more precise. When an engineer processes an `ARCHIVE` recommendation, they (1) copy the file to an archive location, then (2) delete it from the current location. The primary action is still "remove from this location," which is DELETE semantics. The qualifier `archive-first` captures the pre-step.

Set A's concern about semantic clarity is valid -- users should clearly see archive recommendations. This is addressed by ensuring the report output format groups `DELETE:archive-first` items in a visually distinct section with destination suggestions.

**For the Merged Spec**: Use Set B's `DELETE:archive-first` qualifier. The report template must render `DELETE:archive-first` items in a separate, clearly labeled subsection titled "Archive Before Deletion" with destination suggestions. Adopt Set A's requirement that each archive-first item include a suggested destination path. Define canonical archive destinations: `docs/archive/` for documentation, `.dev/archive/` for development artifacts, `releases/archive/` for release-related files.

---

### C-10: Cross-Reference / Cross-Boundary Detection
**Set A Position**: Cross-cutting analysis handled within existing Pass 3 with formatting enhancements (broken reference checklists, directory assessment blocks).
**Set B Position**: Dedicated Phase 3 with directed dependency graph construction, orphan node detection, confidence scoring by hop distance, and dynamic import detection.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-03 (CRITICAL -- dependency graph construction via LLM is infeasible for most languages; dynamic imports, barrel re-exports, and webpack aliases defeat LLM-based extraction). F-B-23 (dynamic import pattern list is incomplete).

**VERDICT**: HYBRID

**Reasoning**: Set B's ambition is correct -- cross-boundary dead code detection is the highest-value novel capability. The current parallel scanners cannot detect cross-boundary issues because each operates in isolation. However, F-B-03 raises a critical feasibility concern: asking an LLM to build reliable import graphs from source code is extremely unreliable across languages.

The resolution is to use a hybrid approach: (1) For languages with available static analysis tools (e.g., `madge` for JS/TS, `pydeps` for Python), run the tool via Bash in Phase 0 and feed the results into Phase 3. (2) For languages without tooling, use grep-based import scanning (searching for import/require/include patterns) with results explicitly labeled as "approximate." (3) The dependency graph is always labeled with confidence levels and the detection method used.

This preserves Set B's architectural vision while addressing the feasibility concern with a practical fallback chain.

**For the Merged Spec**: Phase 3 performs cross-reference synthesis using a 3-tier detection strategy: **Tier A (high confidence)**: Static analysis tools when available (`madge`, `pydeps`, `cargo-deps`). Run in Phase 0 profiling step. **Tier B (medium confidence)**: grep-based import/require pattern scanning from Phase 1 scanner output. **Tier C (low confidence)**: LLM-inferred relationships from Phase 2 analysis. All edges in the dependency graph carry a confidence tier label (A/B/C). Dead code detection only triggers DELETE recommendations for Tier A/B edges; Tier C edges produce INVESTIGATE:cross-boundary. Set A's broken reference checklist format is the output format for the human-readable report.

---

### C-11: Spot-Check Validation
**Set A Position**: No spot-check validation mechanism. Verification limited to section-presence acceptance criteria.
**Set B Position**: 10% spot-check by audit-validator agent in Phase 4. Agreement rate < 85% triggers a warning banner.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-05 (CRITICAL -- LLM-on-LLM validation measures consistency, not correctness; two models can consistently agree on wrong answers).

**VERDICT**: B (with mitigation)

**Reasoning**: Set A's absence of runtime validation is a clear gap. Golden-fixture testing (Set A) validates the prompt, not the actual subagent behavior on real data. Some form of runtime quality signal is necessary.

F-B-05's concern is valid: LLM-on-LLM agreement measures consistency, not ground truth accuracy. However, consistency is still a useful signal -- if two independent runs produce wildly different classifications for the same file, something is wrong. The key is in how the metric is presented.

**For the Merged Spec**: Adopt Set B's spot-check mechanism with these modifications: (1) Call the metric "consistency rate" not "agreement rate" (per F-B-05). (2) Include 3-5 manually curated calibration files in the test fixtures that have known-correct classifications. Measure validator accuracy against these ground-truth files separately. (3) Report both metrics: "Consistency rate: X% (across random sample)" and "Calibration accuracy: Y% (against known-correct files)." (4) If consistency rate < 85%, add a warning banner. If calibration accuracy < 80%, add a CRITICAL warning.

---

### C-12: Phase 0 / Pre-Audit Profiling
**Set A Position**: No pre-audit profiling phase. Audit begins directly with Pass 1.
**Set B Position**: Phase 0: Profile & Plan is mandatory, detects domains, classifies files into risk tiers, generates batch manifests, auto-generates config if absent.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-04 (auto-config generation is a correctness risk if framework detection fails).

**VERDICT**: B

**Reasoning**: The dependency chain analysis in Set B's reflection document demonstrates that Phase 0 is a structural prerequisite. Cross-reference synthesis (Phase 3) depends on structured scanner output, which depends on batch decomposition (Phase 1 infrastructure), which depends on domain detection and file tiering (Phase 0). Without Phase 0, none of the downstream improvements are possible.

The cold-start risk (F-B-04) is real but bounded. The mitigation (auto-generated config is written as a visible artifact, `--dry-run` shows config before full run) is sufficient. The alternative (no profiling at all) is worse because it makes all downstream improvements impossible.

**For the Merged Spec**: Adopt Set B's Phase 0 specification. Add mitigations: (1) Auto-generated config is always written to `.claude-audit/auto-config.yaml` and included in the report with a note "AUTO-DETECTED -- review for accuracy." (2) `--dry-run` runs Phase 0 only and displays the generated config + estimated costs. (3) User-provided config at `audit.config.yaml` always overrides auto-detection. (4) If auto-detection confidence is below 70% for any field, the field is set to a conservative default and flagged in the report.

---

### C-13: Recommendation Category Count
**Set A Position**: 5+ flat output buckets (DELETE, KEEP, ARCHIVE, FLAG, BROKEN_REFERENCES, REMAINING, NOT_YET_AUDITED).
**Set B Position**: 4 primary categories with 13+ secondary qualifiers (composable two-tier system).
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: Same as C-03 (F-B-11, F-B-19).

**VERDICT**: B

**Reasoning**: This conflict is a restatement of C-03. The two-tier system subsumes all of Set A's named categories via qualifiers: ARCHIVE -> DELETE:archive-first, FLAG -> MODIFY:flag:[issue], BROKEN_REFERENCES -> MODIFY:fix-references, REMAINING/NOT_YET_AUDITED -> coverage report metrics. The composable design is more extensible and systematic.

**For the Merged Spec**: Same as C-03. The two-tier system with 4 primaries + qualifiers. The report template renders each qualifier grouping as a visually distinct section to preserve Set A's scanability concern.

---

### C-14: Batch Decomposition -- Static vs Dynamic
**Set A Position**: No explicit batch decomposition strategy.
**Set B Position**: Dynamic batch decomposition with risk-weighted parallel scanning. Phase 0 generates a batch manifest mapping scanner IDs to file lists.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-01 (the "44x more profiles" headline is misleading -- it compares a multi-session human process to a single automated run).

**VERDICT**: B

**Reasoning**: The 44x profiling gap (12 vs 527+) is attributable to the lack of batch decomposition per the findings analysis. The old approach used 26 targeted batches with explicit file lists and produced dramatically more per-file profiles. Without explicit file-to-scanner assignment, scanners have no coverage guarantees and no depth calibration.

F-B-01's concern about misleading metrics is valid for expectation-setting but does not affect the architectural argument. Even normalizing for cost (profiles per 100K tokens), the structured batch approach is more efficient because it eliminates redundant scanning and ensures no files are missed.

**For the Merged Spec**: Adopt Set B's dynamic batch decomposition. Phase 0 generates a batch manifest (JSON) mapping each file to a scanner batch with assigned risk tier and read depth. Quality gate: 100% of repo files must appear in exactly one batch (no gaps, no duplicates). Batch manifests are persisted as artifacts for audit traceability.

---

### C-15: Spec-Implementation Gap Recognition
**Set A Position**: Does not examine the current v1 spec for unimplemented promises. All proposals are framed as "new features."
**Set B Position**: Discovered that v1 spec promises 5 categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-checks -- none implemented. Makes "Phase 0: Enforce Existing Spec" the top priority.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-02 (CRITICAL -- Set A risks repeating v1's exact failure pattern by adding features to a spec that already has unimplemented features).

**VERDICT**: B

**Reasoning**: This is the single most important structural finding in the entire analysis. The v1 spec already promises 5 classification categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check validation. None were implemented. Set A writes a new PRD without acknowledging this gap, which means its proposals may duplicate existing unimplemented requirements and will certainly repeat the pattern of spec-without-enforcement.

Set B's "Phase 0: Enforce Existing Spec" is the architecturally correct response. You cannot trust new feature additions to a system that does not enforce its own existing promises. The spec-implementation gap must be closed first.

**For the Merged Spec**: The merged spec opens with a "Current State Assessment" section that lists all v1 spec promises and their implementation status. Phase 0 of the implementation roadmap is "Enforce Existing Spec" -- implementing the 5 already-promised features before any new capabilities are added. This section also includes a root cause analysis explaining WHY the gap exists (generic scanners, no structured output schema, no enforcement mechanism).

---

### C-16: Coverage Tracking and Guarantee
**Set A Position**: Mentions "REMAINING / NOT_YET_AUDITED coverage accounting" as a schema requirement but provides no thresholds or per-tier tracking.
**Set B Position**: Tiered coverage contracts: Critical 100%, High 95%, Standard 80%, Low 60%. Manifest-first execution with per-file tracking. Coverage below threshold triggers WARN, never blocks.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-07 (coverage tier targets are not empirically validated -- 95% on Tier 2 may be infeasible within budget).

**VERDICT**: B

**Reasoning**: Coverage tracking without thresholds (Set A) is meaningless -- it produces numbers without any quality signal about whether the audit was thorough enough. Set B's tiered thresholds provide actionable quality gates. The WARN-never-block design is pragmatic -- the audit always completes, but the report indicates where coverage fell short.

F-B-07's concern about empirical validation is addressed by labeling thresholds as initial estimates. The manifest-first execution pattern (enumerate all files, track which were examined, report the delta) is the structural enabler for any coverage guarantee.

**For the Merged Spec**: Adopt Set B's tiered coverage system. Thresholds labeled "initial estimates -- validate on benchmark repo": Tier 1 >= 100%, Tier 2 >= 90%, Tier 3 >= 70%, Tier 4 >= 50% (note: relaxed from Set B's originals based on budget feasibility analysis in F-B-07). Coverage report is a required Phase 4 output artifact in JSON format with per-tier PASS/WARN/FAIL status. WARN and FAIL are informational -- they never block report generation.

---

### C-17: Output Format -- Markdown vs JSON
**Set A Position**: Pass summaries as Markdown files. Human-readable throughout.
**Set B Position**: Phase summaries as JSON for machine consumption. Separate human-readable FINAL-REPORT.md.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-03 (Pass 4 depends on undefined infrastructure -- markdown outputs cannot be consumed programmatically by downstream passes).

**VERDICT**: B

**Reasoning**: JSON intermediate outputs are an architectural requirement, not a preference. Schema validation (anti-lazy enforcement), structured cross-phase data flow, and coverage tracking all depend on machine-readable intermediate artifacts. F-A-03 demonstrates the failure mode: if Phase 1 emits markdown, Phase 3 cannot programmatically build a dependency graph from it. The human-readable FINAL-REPORT.md serves the user-facing need that Set A rightly prioritizes.

**For the Merged Spec**: JSON for all intermediate artifacts (phase summaries, scanner outputs, dependency graphs, coverage reports). Markdown for the FINAL-REPORT.md (human-readable). Both are persisted in the output directory. The FINAL-REPORT.md is generated from the JSON artifacts by the consolidator, ensuring consistency.

---

### C-18: Quality Gate on Spot-Check Failure
**Set A Position**: No spot-check mechanism. No failure remediation defined.
**Set B Position**: Spot-check agreement rate < 85% adds a warning banner. Does not block report generation.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-05 (LLM-on-LLM validation measures consistency not correctness).

**VERDICT**: B

**Reasoning**: Same as C-11. Any quality signal is better than none. The warning-banner approach is pragmatic. See C-11 verdict for full details.

**For the Merged Spec**: Same as C-11. Warning banner on consistency rate < 85%. Critical warning on calibration accuracy < 80%. Report always generates regardless of quality gate results.

---

### C-19: .env Handling Approach
**Set A Position**: .env key-presence matrix as a P2 enhancement (cross-env consistency check).
**Set B Position**: .env credential scanning as a Phase 1 correctness fix (detect real vs template credentials).
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: No specific flaw findings for this conflict, but the credential scanning fix is identified as "non-negotiable" in the strength rankings (B-6, composite 8.5).

**VERDICT**: HYBRID

**Reasoning**: These are complementary, not competing. Set B's credential scanning is a correctness fix (the new audit misidentified real credentials as template values -- a wrong answer, not a missing feature). This must be Phase 1 priority. Set A's key-presence matrix is a cross-env consistency check that catches config drift. It is cheaper and lower priority but adds genuine value.

**For the Merged Spec**: **(1) Phase 1**: Credential scanning fix per Set B -- read actual .env contents, distinguish real credentials from templates using pattern matching, never print values, add disclaimer. **(2) Phase 2 or later**: .env key-presence matrix per Set A -- extract keys across `.env*` files, output a consistency matrix showing which keys exist in which files. Both are included; credential scanning is non-negotiable and comes first.

---

### C-20: Progressive Depth Across Passes
**Set A Position**: Not explicitly addressed. Depth is an implementation detail.
**Set B Position**: Two-level signal-triggered depth -- 50-line default, full-file read on specific trigger signals.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: No specific flaw findings for this conflict.

**VERDICT**: B

**Reasoning**: Without explicit depth rules, scanners default to shallow reads or inconsistent behavior across runs. Signal-triggered escalation is a simple, effective mechanism that balances token cost with thoroughness. The trigger list (credential imports, TODO/FIXME/HACK, eval/exec, large files) targets the patterns most likely to reveal actionable findings.

**For the Merged Spec**: Adopt Set B's two-level depth. Default: 50-line header read. Full-file triggers: credential-adjacent imports, TODO/FIXME/HACK comments, eval/exec/dangerouslySetInnerHTML patterns, file size > 300 lines. Trigger patterns are configurable via `audit.config.yaml` to accommodate project-specific patterns.

---

### C-21: Checkpointing Granularity
**Set A Position**: Pass-level checkpointing via progress.json with pass status fields.
**Set B Position**: Batch-level checkpointing after every batch within a phase, enabling mid-phase resume via `--resume` flag.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-B-16 (no handling of concurrent audit runs -- both write to the same progress.json).

**VERDICT**: B

**Reasoning**: Batch-level checkpointing is strictly more granular than pass-level. For large repos with many batches per phase, pass-level checkpointing means losing all within-phase progress on session interruption. The `--resume` flag is a concrete user need for long-running audits.

F-B-16's concern about concurrent runs is valid. The mitigation is to use run-ID isolation in the output directory.

**For the Merged Spec**: Batch-level checkpointing per Set B. progress.json updated after each batch with fields: current_phase, batches_completed, batches_total, files_examined, files_remaining. `--resume` flag resumes from the last completed batch. Run isolation: output directory is `.claude-audit/run-{timestamp}/` to prevent conflicts between concurrent runs. Set A's progress.json schema additions (pass4_docs, known_issues counts) are incorporated into the expanded schema.

---

### C-22: Claim Spot-Check Scope (Docs)
**Set A Position**: 3-5 structural claims per doc across all sampled docs.
**Set B Position**: 3 claims per doc, only for API-reference and setup-guide category docs.
**Set A Advocate's Best Argument**: Not available.
**Set B Advocate's Best Argument**: Not available.
**Devil's Advocate Concern**: Not available.
**Flaw Hunter Findings**: F-A-05 (claim spot-checks are vaguely defined -- what is an "authoritative spec"?).

**VERDICT**: HYBRID

**Reasoning**: Set B's narrowing to API-reference and setup-guide docs is good for initial cost control, but architecture and conceptual docs can also contain verifiable claims (referenced file paths, referenced component names). The right approach is to define which claim types are verifiable for which doc categories.

F-A-05's concern about vague verification is valid. Claim types must have binary pass/fail criteria.

**For the Merged Spec**: 3 claims per doc (Set B's count for cost control). Applied to API-reference, setup-guide, AND architecture docs (broader than Set B, narrower than Set A's "all sampled docs"). Claim types must be structural and verifiable: (1) referenced file exists, (2) referenced script/command is executable, (3) referenced port appears in a config file. Claims that cannot be verified programmatically (e.g., "port should be 8102") are out of scope for automated checking and explicitly labeled as requiring human review.

---

## Part 2: Unique Contributions Integration

### Set A Unique Contributions

| # | Contribution | Value | Where in Merged Spec |
|---|-------------|-------|---------------------|
| 1 | Target Users and Use Cases (U1-U3) | HIGH -- grounds the PRD in user needs | Section 1 (after Executive Summary). Three personas: repo maintainers, onboarding authors, DevOps owners. Three use cases: immediate action list, weekly audit without re-discovery, find broken docs links. |
| 2 | Explicit Non-Goals (N1-N3) | HIGH -- prevents scope creep | Section 2 (Goals and Non-Goals). N1: not a cleanup executor (read-only). N2: not a semantic doc correctness checker. N3: no elimination of human judgment. |
| 3 | Directory-Level Assessment Blocks for Large Dirs | MEDIUM -- provides signal for 50+ file directories | Phase 4 Consolidation output format. For directories with 50+ files: sample list, assessment label (actively maintained / stale / bulk dump / mixed), recommendation. |
| 4 | Content Overlap Group Output Specification | MEDIUM -- the only structured output format for docs overlap | Phase 5 docs audit output format, Section "CONTENT_OVERLAP_GROUPS". Cluster by topic, canonical doc recommendation, superseded candidates, short rationale. |
| 5 | .env Key-Presence Matrix | LOW-MEDIUM -- complementary to credential scanning | Phase 2+ enhancement. Cross-env key consistency matrix. Optional, triggered by presence of multiple `.env*` files. |

### Set B Unique Contributions

| # | Contribution | Value | Where in Merged Spec |
|---|-------------|-------|---------------------|
| 1 | Spec-Implementation Gap Discovery | CRITICAL -- the foundational framing insight | Section 2 (Current State Assessment). Table of v1 promises vs implementation status. Root cause analysis. Phase 0 requirement. |
| 2 | Evidence-Mandatory KEEP Decisions (Tiered) | HIGH -- addresses 5,780 files classified without evidence | Section 4 (Classification System) under evidence requirements. Tiered per C-07 verdict. |
| 3 | Batch Decomposition Strategy | HIGH -- architectural enabler | Section 5 Phase 0 (batch manifest generation) and Phase 1 (domain-aware batches). |
| 4 | Credential Scanning Correctness Fix | HIGH -- non-negotiable correctness fix | Section 5 Phase 1. Priority-ordered .env scanning, template vs real detection patterns, never-print-values rule. |
| 5 | Anti-Lazy-Agent Enforcement | HIGH -- prevents rubber-stamping | Section 9 (Quality Gates). Required output fields, evidence non-emptiness rules, confidence distribution check, cross-batch consistency. |
| 6 | Token Cost Realism (2-3x correction) | HIGH -- prevents deployment failure | Section 6 (Budget System). Corrected estimates, `--budget` flag, graceful degradation. |
| 7 | Dependency Chain Ordering | HIGH -- prevents implementation failure | Section 12 (Implementation Roadmap). 5-phase dependency-aware roadmap. |
| 8 | Progressive Depth Escalation | MEDIUM -- improves token efficiency | Section 5 Phase 2. Two-level signal-triggered depth. |
| 9 | Cross-Reference Resolution with Dependency Graph | HIGH -- highest-impact technical contribution | Section 5 Phase 3. 3-tier detection strategy (static tools / grep / LLM). |
| 10 | Cold-Start / Config Bootstrapping | MEDIUM -- important for first-run UX | Section 10. Auto-generation from framework/port/CI detection. Visible artifact. |
| 11 | Report Depth Control | MEDIUM -- manages output volume | Section 7 CLI flags. `--report-depth summary\|standard\|detailed`. |
| 12 | Dynamic Import False Positive Mitigation | MEDIUM -- technical correctness | Section 5 Phase 3. Configurable pattern list via audit.config.yaml. |
| 13 | Backward Compatibility Mapping (v1 to v2) | MEDIUM -- migration support | Section 4. Explicit mapping table with corrected REVIEW semantics. |
| 14 | --dry-run and --resume Flags | MEDIUM -- practical UX improvements | Section 7 CLI flags. `--dry-run` for cost estimation. `--resume` for interrupted audits. |
| 15 | Standardized Scanner Output Schema (JSON) | CRITICAL -- architectural enabler | Section 3 (Architecture). Complete JSON schema for scanner output. Simplified for Phase 1 Haiku, expanded for Phase 2 Sonnet. |

---

## Part 3: Flaw Mitigations

### CRITICAL Flaws

| Flaw ID | Description | Merged Spec Mitigation |
|---------|-------------|----------------------|
| F-A-01 | No token budget model | Adopted Set B's budget system with increased default (500K). `--dry-run` for cost preview. |
| F-A-02 | No spec-implementation gap acknowledgment | Adopted Set B's "Phase 0: Enforce Existing Spec." Current State Assessment section in merged spec. |
| F-A-03 | Pass 4 depends on undefined infrastructure | Docs audit runs within Phase 2/3 framework using structured JSON output from Phase 1. No standalone pass depending on markdown. |
| F-B-01 | "44x more profiles" metric is misleading | Merged spec uses profiles-per-100K-tokens as the normalization metric, not raw counts. Targets are budget-relative. |
| F-B-02 | Token estimates still underestimated | Default budget increased to 500K. All estimates labeled "UNVALIDATED." `--dry-run` provides per-repo estimates. Margin of 50% recommended. |
| F-B-03 | Dependency graph via LLM is infeasible | 3-tier detection strategy: static tools (high confidence) > grep patterns (medium) > LLM inference (low). Dead code recommendations only from Tier A/B. |
| F-B-04 | Phase 0 auto-config correctness risk | Auto-config written as visible artifact. `--dry-run` shows config before full run. User config always overrides. Low-confidence fields use conservative defaults. |
| F-B-05 | LLM-on-LLM validation measures consistency not correctness | Renamed to "consistency rate." Added calibration files with known-correct classifications. Dual metrics: consistency rate + calibration accuracy. |

### HIGH Flaws

| Flaw ID | Description | Merged Spec Mitigation |
|---------|-------------|----------------------|
| F-A-04 | Known-issues registry has no lifecycle | TTL per entry (90d default), auto-prune for deleted files, max 200 entries with LRU eviction. |
| F-A-05 | Claim spot-checks vaguely defined | Explicit claim types with binary pass/fail criteria. Only structural claims (file exists, command executable, port in config). |
| F-A-06 | No error recovery or partial failure handling | Per-subagent timeout, max 2 retries, FAILED batch marking with continuation. Minimum viable report from 50%+ batch completion. |
| F-A-07 | Adversarial review is shallow | Expanded risk section with monorepo, polyglot, binary-heavy, non-English edge cases. |
| F-A-08 | Golden-output fixtures are brittle | Test for structural properties (section presence, JSON validity, required fields) not golden output matching. |
| F-B-06 | Scanner schema too complex for Haiku | Simplified Phase 1 schema (essential fields only). Complex fields moved to Phase 2 Sonnet. |
| F-B-07 | Coverage tier targets unvalidated | Targets labeled "initial estimates." Relaxed from Set B originals. Benchmark-before-hardcode requirement. |
| F-B-08 | Evidence-mandatory KEEP conflicts with budget | Tier 2 relaxed to "1-field mandatory, 2-field target." Evidence depth reported as metric. |
| F-B-09 | Graceful degradation order debatable | Degradation order configurable via `--degrade-priority` flag. |
| F-B-10 | No monorepo handling | Monorepo detection in Phase 0. Workspace boundaries respected for batch decomposition and dependency graphs. |
| F-B-11 | INVESTIGATE as dumping ground | Hard cap at 15% of examined files. Exceeded cap triggers re-analysis. |
| F-B-12 | Findings exaggerate old system capabilities | Merged spec clearly distinguishes "human-in-the-loop findings" from "automatable findings." Targets only the latter. |
| F-B-13 | Reflection issues not fully resolved in PRD | Traceability matrix: each reflection correction maps to a specific merged spec section with pass/partial/fail status. |
| CS-04 | Both sets underspecify subagent failure handling | Per-subagent: 120s timeout, max 2 retries, mark FAILED and continue. Minimum viable report requires 50%+ batch success. Cascading failure detection (if 3 consecutive batches fail, pause and report). |
| CS-06 | Neither set has realistic testability | 3-tier test strategy: (1) structural tests (files exist, JSON valid, sections present), (2) property tests (coverage in range, no credential values in output, all Tier 1 files examined), (3) benchmark tests against 2-3 real repos. |

---

## Part 4: Preliminary Merge Plan

### Structural Outline of the Unified Spec

```
1. Executive Summary — Source: Set B ss1 / New
   - Problem statement using Set B's framing (spec-implementation gap + capability gaps)
   - Solution summary (5-phase architecture)
   - Key metrics table (budget-relative targets, not raw counts per F-B-01)

2. Current State Assessment — Source: Set B ss2 / New
   - Spec-implementation gap table (Set B)
   - Root cause analysis (Set B)
   - Added: explicit comparison methodology disclaimer

3. Goals and Non-Goals — Source: Set A ss2 / New
   - Goals: Set B's 5 solution pillars + Set A's user-facing goals (G1-G5)
   - Non-goals: Set A's N1-N3 (not executor, not semantic checker, no human elimination)
   - Added: Non-goal N4: "Not a security audit substitute"

4. Target Users and Use Cases — Source: Set A ss3
   - Three personas: repo maintainers, onboarding authors, DevOps owners
   - Three use cases: U1-U3
   - No modifications needed

5. Architecture — Source: Set B ss3 / Modified
   - 6-agent system with model assignments (Set B)
   - Modified: Phase 1 Haiku schema simplified per F-B-06
   - Modified: progressive specialization starting from existing agents
   - Execution flow diagram (Set B)

6. Classification System — Source: Set B ss4 / Modified
   - Two-tier system: 4 primary + qualifiers (Set B)
   - Added: INVESTIGATE:human-review-needed qualifier per F-B-19
   - Added: 15% INVESTIGATE cap per F-B-11
   - Backward compatibility mapping (Set B, corrected)
   - File risk tiers with evidence requirements (Set B, relaxed per F-B-08)

7. Phase Specification — Source: Set B ss5 / Hybrid
   - Phase 0: Profile & Plan (Set B + monorepo detection per F-B-10)
   - Phase 1: Surface Scan (Set B + credential scanning fix + gitignore check)
   - Phase 2: Structural Audit (Set B + .env key matrix from Set A + progressive depth)
   - Phase 3: Cross-Reference Synthesis (Hybrid: 3-tier detection per C-10 verdict)
     - Sub-section: Minimal Docs Audit (broken refs + temporal classification from Set A)
   - Phase 4: Consolidation & Validation (Set B + directory assessment blocks from Set A)
     - Within-run dedup (Set B)
     - Spot-check validation (Set B, renamed per F-B-05)

8. Budget System — Source: Set B ss6 / Modified
   - --budget flag with 500K default (increased from 300K per F-B-02)
   - Phase allocation (Set B, advisory not hard-wired)
   - Graceful degradation (Set B, configurable order per F-B-09)
   - --dry-run for cost estimation
   - All estimates labeled UNVALIDATED

9. CLI Interface — Source: Set B ss7 / Enriched
   - Set B flags: --budget, --report-depth, --tier, --resume, --config, --dry-run
   - Added: --pass-docs (Tier 2 docs audit), --degrade-priority, --known-issues
   - Set A flag addition: --pass updated to include docs

10. Output Specification — Source: Set B ss8 / Enriched
    - JSON intermediate artifacts (Set B)
    - FINAL-REPORT.md (Set B + Set A's output format specifications)
    - Coverage report JSON (Set B)
    - Run-ID isolation per F-B-16
    - Added: Set A's content overlap group output format
    - Added: Set A's broken reference checklist format

11. Quality Gates — Source: Set B ss9 / Modified
    - Anti-lazy enforcement (Set B)
    - Consistency rate + calibration accuracy (modified per F-B-05)
    - Coverage thresholds (Set B, relaxed)
    - INVESTIGATE cap (15%)
    - Subagent failure handling (new, per CS-04)

12. Cold-Start & Configuration — Source: Set B ss10
    - Auto-config generation (Set B)
    - --dry-run integration
    - Visible artifact + confidence marking per F-B-04

13. Risks and Mitigations — Source: Set B ss11 / Enriched
    - Set B's 8 risks + mitigations
    - Added: monorepo risk (F-B-10)
    - Added: non-English docs risk (CS-01)
    - Added: markdown-only limitation (CS-02)
    - Added: concurrent run risk (F-B-16)
    - Added: GFxAI over-fitting risk (CS-05)

14. Cross-Run Known Issues Registry — Source: Set A ss4.4 / Modified (Phase 5)
    - JSON schema (Set A)
    - Added: TTL, auto-prune, max entries per F-A-04
    - Opt-in via --known-issues flag
    - Loaded as read-only consolidator context (preserves parallelism)

15. Documentation Audit (Full) — Source: Set A ss4.3 / Modified (Phase 5)
    - Set A's 5-section output format
    - Set B's opt-in activation and 20% budget cap
    - Claim types restricted to structural per F-A-05

16. Acceptance Criteria — Source: Hybrid
    - Set A's 5 criteria (A1-A5) for output structure
    - Set B's 13 criteria for phase behavior
    - Added: 3-tier test strategy per CS-06
    - All criteria mapped to specific spec sections

17. Implementation Roadmap — Source: Set B ss12 / Enriched
    - 5-phase dependency-aware roadmap (Set B)
    - Set A unique items inserted into appropriate phases
    - All effort estimates labeled "UNVALIDATED"
    - Benchmark-first requirement before sprint planning

18. Expert Panel Assessment — Source: New
    - Labeled as "self-assessment using named analytical frameworks"
    - Not presented as external expert review
    - Standardized panel per F-B-22
```

---

## Part 5: Devil's Advocate Response

The devil's advocate file was not available at judgment time. However, the Flaw Analysis document serves as a comprehensive adversarial review with 43 identified flaws. The top concerns from the flaw analysis are addressed as follows:

### Concerns That Must Be Incorporated as Known Risks

1. **Token cost estimates remain unvalidated (F-B-02)**: The merged spec cannot resolve this without empirical benchmarking. It is recorded as Known Risk #1 with the mitigation: "All estimates are UNVALIDATED. Run `--dry-run` on your repo before planning. Add 50% margin to all estimates."

2. **LLM-on-LLM validation is consistency not correctness (F-B-05)**: This is a fundamental limitation of the approach. Recorded as Known Risk #2 with the mitigation: "Renamed to consistency rate. Calibration files provide ground-truth anchor. Report both metrics separately."

3. **Dependency graph infeasibility for dynamic languages (F-B-03)**: Recorded as Known Risk #3 with the mitigation: "3-tier detection strategy. Only Tier A/B edges produce DELETE recommendations. Tier C edges produce INVESTIGATE."

4. **Implementation effort estimates are unrealistic (F-B-14)**: Recorded as Known Risk #4: "Effort estimates are 3-5x too low. Benchmark by implementing one feature before planning sprints."

5. **GFxAI-specific requirements masquerading as universal (CS-05)**: Recorded as Known Risk #5: "Separate universal audit features from project-specific rule examples. Make project-specific rules loadable from config."

### Concerns Addressed by the Merge Design

1. **Spec-implementation gap repetition (F-A-02)**: Addressed by Phase 0: Enforce Existing Spec and the Current State Assessment section.

2. **INVESTIGATE dumping ground (F-B-11)**: Addressed by 15% cap with re-analysis trigger.

3. **Scanner schema too complex for Haiku (F-B-06)**: Addressed by splitting schema between Phase 1 (simplified) and Phase 2 (full).

4. **No error recovery (F-A-06, CS-04)**: Addressed by per-subagent timeout/retry/FAILED-and-continue policy with minimum viable report threshold.

5. **Coverage targets infeasible (F-B-07, F-B-08)**: Addressed by relaxing targets and labeling as initial estimates.

### Concerns That Are Out of Scope

1. **Non-English documentation (CS-01)**: Acknowledged as a limitation. UTF-8 handling required; full multilingual support is out of scope for v2.

2. **Non-markdown documentation formats (CS-02)**: v2 supports `.md` first-class and `.rst` best-effort. Other formats are out of scope.

3. **Concurrent audit runs (F-B-16)**: Addressed by run-ID isolation, but true distributed coordination is out of scope.

---

## Part 6: Quality Gate Baseline

### Composite Scores from Strength Rankings

| Metric | Value |
|--------|-------|
| **Set A average composite** | 7.70 |
| **Set B average composite** | 8.55 |
| **Combined baseline** | 8.13 |

### Per-Dimension Averages

| Dimension | Set A | Set B | Target for Unified |
|-----------|-------|-------|--------------------|
| Specificity | 8.3 | 9.1 | >= 9.0 |
| Evidence Quality | 7.5 | 8.8 | >= 8.5 |
| Implementability | 7.9 | 8.5 | >= 8.5 |
| Architectural Soundness | 7.2 | 8.1 | >= 8.5 |

### Quality Gate for the Unified Spec

The unified spec must exceed BOTH individual set averages on every dimension:

- **Overall composite target**: >= 8.6 (exceeds both Set A's 7.70 and Set B's 8.55)
- **Specificity target**: >= 9.0 (matches Set B's strength; Set A's output format specs raise the floor)
- **Evidence Quality target**: >= 8.5 (all claims must reference source documents or quantified analysis)
- **Implementability target**: >= 8.5 (every section must be implementable by an engineer without ambiguity)
- **Architectural Soundness target**: >= 8.5 (exceeds both; the merge must resolve the architectural flaws identified in both sets)

### Measurement Method

The unified spec will be scored by re-applying the same 4-dimension rubric to its top 15 elements. If any dimension falls below the target, the section is revised before finalization.

---

## Verdict Summary Table

| ID | Verdict | Key Factor |
|----|---------|-----------|
| C-01 | **B** | Infrastructure-first framing addresses root cause |
| C-02 | **HYBRID** | Minimal docs in core flow + full docs opt-in |
| C-03 | **B** | Two-tier system is composable and extensible |
| C-04 | **HYBRID** | Within-run dedup (B) + cross-run registry (A) |
| C-05 | **B** | Dependency-aware phasing prevents implementation failure |
| C-06 | **HYBRID** | Target architecture (B) with progressive adoption (A) |
| C-07 | **B** | Uniform evidence is infeasible; tiering is necessary |
| C-08 | **B** | Explicit budget is architectural, not implementation detail |
| C-09 | **B** | DELETE:archive-first is semantically precise |
| C-10 | **HYBRID** | 3-tier detection strategy (static tools > grep > LLM) |
| C-11 | **B** | Runtime validation needed; renamed to consistency rate |
| C-12 | **B** | Phase 0 is structural prerequisite for all improvements |
| C-13 | **B** | Same as C-03 |
| C-14 | **B** | Batch decomposition explains the 44x profiling gap |
| C-15 | **B** | Spec-implementation gap is the foundational insight |
| C-16 | **B** | Coverage without thresholds is meaningless |
| C-17 | **B** | JSON intermediates are architectural requirement |
| C-18 | **B** | Same as C-11 |
| C-19 | **HYBRID** | Credential scanning (B, Phase 1) + key matrix (A, Phase 2+) |
| C-20 | **B** | Explicit depth rules prevent shallow scanning |
| C-21 | **B** | Batch-level checkpointing enables --resume |
| C-22 | **HYBRID** | Set B's count (3) + broader doc categories + explicit claim types |

### Final Tally

| Verdict | Count |
|---------|-------|
| **B** | 14 |
| **HYBRID** | 7 |
| **A** | 0 |
| **NEITHER** | 0 |

**Note**: Zero pure A verdicts does not mean Set A contributed nothing. Set A's unique contributions (target users, non-goals, output format specs, directory assessment blocks, .env key matrix, content overlap groups) are all integrated into the merged spec via the Unique Contributions Integration (Part 2). Set A's primary weakness was architectural framing (additive changes to a broken structure), not content quality. Every HYBRID verdict incorporates Set A elements.

---

*Synthesis Judge verdicts rendered 2026-02-20*
*Based on Wave 1 analysis (4 documents, 43 flaws, 22 conflicts, 45 coverage topics)*
*Advocate files not available -- verdicts based on evidence in Wave 1 outputs*
