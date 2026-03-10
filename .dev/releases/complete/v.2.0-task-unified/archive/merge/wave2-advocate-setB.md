# Wave 2: Advocate Brief for Set B

**Date**: 2026-02-20
**Role**: Set B Advocate Agent
**Input**: Wave 1 outputs (coverage matrix, strength rankings, flaw analysis, conflict register) + Set B source documents (4 files)

**Set B's Core Philosophy**: Fix the architectural root cause first. The v1 spec already promises features that were not implemented because the architecture could not enforce them. Adding more features to a broken architecture will produce the same gap. Restructure with phased execution, structured output schemas, and tiered evidence requirements.

---

## Conflict-by-Conflict Advocacy

### C-01: Phase/Pass Structure (Count and Architecture)
**Set B Position**: 5 phases (Phase 0: Profile & Plan, Phase 1-3: scanning/analysis, Phase 4: Consolidation & Validation) rather than bolting a 4th pass onto the existing 3-pass architecture.

**Argument FOR Set B**: The existing 3-pass architecture is not merely incomplete -- it is structurally incapable of delivering on its own promises. The v1 spec already defined 5 classification categories, coverage tracking, checkpointing, and evidence-gated classification, yet none were implemented. Set A's response to this systemic failure is to add a 4th pass, which is equivalent to adding a room to a building with a cracked foundation.

Set B's 5-phase architecture addresses this by bookending the core scanning with infrastructure. Phase 0 (Profile & Plan) creates the batch manifests, tier assignments, and domain detection that scanners need to produce structured output. Phase 4 (Consolidation & Validation) provides the quality gate that ensures scanner output actually meets requirements. These are not optional enhancements -- they are the enforcement mechanisms that were absent in v1.

The reflection validation document (B3, Dimension 1) traces a hidden dependency chain: P11 (Scan Profile) depends on P6 (Batch Decomposition) depends on P1 (Cross-Reference) depends on P10 (Deduplication). Without Phase 0 to create structured inputs and Phase 4 to validate structured outputs, the pipeline has no enforcement points. Set A never examines this dependency chain because Set A never examines the existing spec at all.

The evidence is quantitative: v1 produced 12 per-file profiles out of 5,857 files. That is a 99.8% miss rate. This is not a "missing pass 4" problem -- it is a pipeline architecture problem. Phase 0 and Phase 4 exist to prevent Phase 1-3 from repeating that failure.

**Addressing Set A's Counter**: Set A argues that the simplest fix is additive: keep the 3-pass structure and bolt on a 4th pass. This argument has surface appeal (minimal disruption) but ignores that the existing 3-pass structure is the root cause of the quality deficit. Adding Pass 4 to an architecture that already fails to deliver its promises will produce a spec with 4 underperforming passes instead of 3.

**Addressing Known Flaws**: The Flaw Hunter (F-B-04) correctly notes that Phase 0 auto-config generation is a correctness risk. This is addressable by making Phase 0 output a visible, editable `audit.config.yaml` artifact and by adding `--dry-run` (which the PRD already includes) to let users review the config before committing to a full run. The architectural intent (front-load infrastructure before scanning) is preserved while the implementation risk is mitigated.

**Honest Concession**: Set B's 5-phase structure is more complex to implement and understand. The effort estimates in B4 Section 12 (4-6 hours for Phase 0) are almost certainly too low, as F-B-14 notes. However, the complexity is inherent to the problem -- the alternative is not "simpler," it is "deferred."

---

### C-02: Documentation Audit -- Mandatory vs Opt-In
**Set B Position**: Documentation audit is opt-in via `--pass-docs`, deferred to Phase 5 of the implementation roadmap, capped at 20% of token budget.

**Argument FOR Set B**: The 4-agent debate reached consensus to downgrade the documentation audit from CRITICAL to MEDIUM priority. The reasoning was rigorous: (1) credential scanning, coverage tracking, and cross-reference synthesis all have higher ROI because they catch correctness failures, not just depth gaps; (2) the docs audit is the most expensive new capability at 175K-585K additional tokens (B3, Dimension 3); and (3) the docs audit can be bounded as opt-in without degrading the core audit.

Set B's approach does not reject the docs audit -- it sequences it correctly. The reflection validation (B3) demonstrated that token cost estimates for the proposals were systematically low by 2-3x. Adding a mandatory docs pass to an audit that already risks budget overruns is irresponsible engineering. The opt-in mechanism with a 20% budget cap ensures the docs audit can be used when budget permits, without jeopardizing the core audit.

The underlying logic is priority inversion prevention. Set A elevates docs audit to P0 because it is the most visible gap. But visible does not mean most important. A false negative on real credentials in `.env.production` (Finding 6) is objectively more severe than missing a broken link in `docs/DOCUMENTATION_INDEX.md`. Set B's ordering reflects severity of consequence, not visibility of gap.

**Addressing Set A's Counter**: Set A's strongest argument is that the docs audit was the motivating complaint. This is true at the surface level. But Set B's analysis reveals that the motivating complaint masks a deeper issue: the architecture does not enforce any of its promises. Fixing the architecture (so that v2 actually delivers on its spec) is a prerequisite for any new pass to succeed. If the docs pass is added to the same architecture that failed to deliver coverage tracking, the docs pass will also fail to deliver.

**Addressing Known Flaws**: F-B-18 correctly identifies that deferring docs to Phase 5 creates an incoherent MVP if the primary stakeholder complaint is "docs are never audited." The mitigation is to include a minimal docs audit (broken links + temporal classification only, no claim spot-checking) within Phase 3 as part of cross-reference synthesis. This addresses the most visible gap without the full token cost of a standalone pass. Set A's detailed output schema (A-1, scored 8.8) can be adopted for this minimal scope.

**Honest Concession**: Set B genuinely underweights the user-facing impact of the missing docs audit. The demotion from CRITICAL to MEDIUM conflates severity (how bad is the gap) with priority (when to fix it). A better framing would be: severity remains HIGH, but implementation priority is Phase 3 (minimal) and Phase 5 (full), not Phase 0.

---

### C-03: Classification System -- Categories and Structure
**Set B Position**: Two-tier classification with 4 primary actions (DELETE/KEEP/MODIFY/INVESTIGATE) and 13+ secondary qualifiers, with explicit backward compatibility mapping from v1 categories.

**Argument FOR Set B**: The two-tier system was designed to solve a concrete problem: the v1 spec defined 5 categories (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP) but only 3 were ever used. Set A's response is to add more flat categories (ARCHIVE, FLAG, BROKEN_REFERENCES). This repeats the v1 pattern -- proliferate categories and hope they get implemented.

Set B's two-tier system is architecturally superior for three reasons. First, it is composable: new use cases are handled by adding qualifiers, not primary categories. `ARCHIVE` becomes `DELETE:archive-first`. `CONSOLIDATE` becomes `MODIFY:consolidate-with:[target]`. This means the schema never needs to change for new classification needs. Second, the primary action tells an engineer what to DO (delete it, keep it, modify it, investigate it), while the qualifier tells them HOW. This separation of concerns makes the output more actionable. Third, the backward compatibility mapping (B4, Section 4) ensures that v1 consumers can still interpret v2 output, which Set A does not address.

The classification system scored 9.0 composite in the strength rankings (B-2), second only to the scanner output schema. The strength rankings confirmed: "Two-tier design is composable and extensible without schema changes. Backward compatibility mapping preserves v1 interop. INVESTIGATE as explicit escape hatch prevents forced mis-classification."

**Addressing Set A's Counter**: Set A argues that each distinct action type deserves its own named section for scanability. This is a presentation concern, not a data model concern. The two-tier system can render `DELETE:archive-first` items under an "ARCHIVE" heading in the final report while maintaining the composable data model underneath. The report template is independent of the classification schema.

**Addressing Known Flaws**: F-B-11 correctly warns that INVESTIGATE may become a dumping ground. The mitigation is a hard cap (max 15% of examined files classified as INVESTIGATE). If exceeded, the consolidator triggers re-analysis of INVESTIGATE items. F-B-19 correctly identifies semantic drift between v1 REVIEW and v2 INVESTIGATE. The mitigation is adding `INVESTIGATE:human-review-needed` as a distinct qualifier for genuinely ambiguous files (separate from `insufficient-evidence` which indicates evidence-gathering failure).

**Honest Concession**: None significant. The two-tier system is strictly more expressive than flat categories while being equally readable when rendered.

---

### C-04: Known-Issues Handling -- Registry vs Post-Hoc Dedup
**Set B Position**: Post-hoc deduplication in the consolidator agent rather than a sequential inter-pass registry. Zero runtime overhead during scanning. Zero parallelism loss.

**Argument FOR Set B**: Set B's post-hoc dedup is architecturally cleaner for within-run deduplication. The consolidator is already the natural aggregation point -- it receives all scanner output and produces the final report. Adding dedup logic here costs ~500 tokens of prompt overhead and requires zero changes to the scanning pipeline. The performance engineers in the 4-agent debate specifically argued that a sequential registry introduces a serialization bottleneck: every pass must load, query, and potentially update the registry before proceeding. In a parallel scanning architecture, this creates a chokepoint.

The cost differential is significant. Set A's registry requires: a JSON file schema, loading logic before each pass, signature matching logic, update logic after each pass, and corruption handling. Set B's consolidator dedup requires: 5 additional instructions in the consolidator prompt. The complexity ratio is approximately 10:1 for equivalent within-run dedup quality.

**Addressing Set A's Counter**: Set A's registry has a genuine advantage that Set B does not address: cross-run suppression. A registry that persists between audit runs prevents re-discovering the same issues week after week. This is a real user need derived from the legacy prompts' 34-item known-issues list. However, the cross-run use case is separable from the within-run dedup use case. The registry can be implemented as an optional overlay on top of post-hoc dedup, not as a replacement for it.

**Addressing Known Flaws**: F-A-04 (from the Flaw Hunter's critique of Set A) actually strengthens Set B's case: the registry "has no versioning or lifecycle" and risks becoming "a maintenance burden that accumulates noise over time." Set B's post-hoc dedup avoids this entire class of problems because it has no persistent state to maintain.

**Honest Concession**: This is the one conflict where Set A is clearly stronger on a specific dimension. Set B does not address the cross-run suppression use case at all. The correct resolution is to adopt Set B's post-hoc dedup for within-run deduplication (Phase 4) and Set A's registry schema for optional cross-run persistence (Phase 5 extension). Set B's weakness here is addressable but real.

---

### C-05: Priority Ordering of Improvements
**Set B Position**: Phase 0 = enforce existing unimplemented spec features. Then correctness fixes, then infrastructure, then depth improvements, then extensions. The docs audit and known-issues registry are Phase 5 extensions, not Phase 0 must-haves.

**Argument FOR Set B**: This is the conflict where Set B's analytical process produced its most valuable insight. The reflection validation (B3, Dimension 2) discovered that the v1 spec already promises 5 classification categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check validation -- none of which were implemented. Set A's priority ordering (P0 = docs pass + known-issues registry) is predicated on the assumption that the existing spec is complete and the gap is "missing features." Set B's analysis reveals the gap is "unimplemented promises."

The dependency chain analysis (B3, Dimension 1) provides additional evidence. The original proposal ranking had Cross-Reference Resolution at #1, but cross-reference resolution depends on structured scanner output (Proposal 6) and scan profiling (Proposal 11), which were ranked #6 and #11. Building the top-ranked feature before its prerequisites exist guarantees failure. Set B's phased ordering respects these dependencies.

Set A's flat 10-item backlog has no dependency ordering at all. Item 1 (Pass 4 rules) and Item 6 (known-issues registry) have no specified ordering relationship. This means an implementer could start with the registry, discover that it needs structured scanner output to work, and waste significant effort.

**Addressing Set A's Counter**: Set A argues that the most visible gap (docs audit) should be P0. This is output-focused thinking. Set B argues that the most impactful fix (enforce existing spec) should come first because it addresses the systemic cause of ALL gaps, including the docs gap. Implementing spec enforcement first means that when the docs pass is eventually added, the infrastructure to support it (structured output, coverage tracking, checkpointing) already exists.

**Addressing Known Flaws**: F-B-14 notes that implementation effort estimates are unrealistically low (4-6 hours for Phase 0 vs a realistic 15-25 hours). This is a planning error, not a priority ordering error. The phases are in the right order even if the time estimates are wrong. The mitigation is to benchmark Phase 0 implementation on a real repository before estimating subsequent phases.

**Honest Concession**: None. This is Set B's strongest position. The spec-implementation gap discovery is the single most important finding across both sets, and it fundamentally reframes the priority calculus.

---

### C-06: Subagent Architecture
**Set B Position**: 6 named specialized agents with explicit model assignments (Haiku for mechanical tasks, Sonnet for semantic analysis), assigned to specific phases.

**Argument FOR Set B**: The 44x profiling gap (12 vs 527+ files profiled) is directly attributable to the v1 architecture of 6 unnamed generic scanners. Set B's analysis identifies this as the root cause: without specialization, scanners have no documented capabilities, no structured output requirements, and no model-appropriate task assignments.

Set B's 6-agent system addresses this by assigning each agent a specific role in a specific phase with a specific model. The audit-profiler (Haiku) handles Phase 0 because domain detection is a pattern-matching task that does not require deep reasoning. The audit-analyzer (Sonnet) handles Phase 2 because 8-field structural profiles require semantic understanding. This cost-optimized assignment means Haiku handles the high-volume mechanical work while Sonnet handles the lower-volume analytical work.

The strength rankings scored this element highly: the scanner output schema (B-1) received the highest composite score of 9.3 across both sets. The schema is the enabler; the specialized agents are the enforcers.

**Addressing Set A's Counter**: Set A advocates conservative reuse of existing agents. This is the approach that produced 12 profiles out of 5,857 files. "Reuse what failed and hope for different results" is not a defensible engineering strategy. The specialization is not premature -- it is a direct response to measured failure.

**Addressing Known Flaws**: F-B-06 correctly warns that the JSON schema may be too complex for Haiku. The mitigation is to simplify Phase 1 output to essential fields only (path, classification, confidence, evidence_summary) and defer complex structured fields (external_dependencies, export_targets) to Phase 2 Sonnet analyzers. This preserves the specialized agent architecture while respecting model capabilities. F-B-01 also correctly notes an internal inconsistency between the findings doc (5 specialized scanner types) and the PRD (6 named agents). The PRD's 6-agent system is the authoritative specification; the findings doc's 5-type proposal was superseded by the debate and reflection process.

**Honest Concession**: The 6-agent system is more complex to implement and orchestrate than reusing existing agents. If implementation resources are severely constrained, a phased approach (start with existing agents for Phase 0-1, specialize in Phase 2+) is a pragmatic compromise that preserves Set B's architectural direction.

---

### C-07: Evidence Requirements for KEEP -- Uniform vs Tiered
**Set B Position**: 4-tier evidence requirements based on file risk. Tier 1 (Critical) = full 3-field check. Tier 2 (High) = 2-field. Tier 3 (Standard) = relational annotation. Tier 4 (Low) = pattern-match only.

**Argument FOR Set B**: The reflection validation (B3, Dimension 3) provides the decisive evidence: requiring full evidence for all ~5,800 files would cost 175K-585K additional tokens, potentially doubling or tripling the audit cost. Uniform evidence is not merely expensive -- it is infeasible within any reasonable budget. Set A's position ("evidence for KEEP is mandatory") is correct as a principle but silent on cost, which makes it an unfunded mandate.

Set B's tiered approach applies the principle of proportional investment. The 10-20% of files classified as Tier 1 (Critical) -- deployment scripts, CI/CD pipelines, migrations -- receive full evidence because misclassification here has the highest consequence. The 60-70% of files classified as Tier 3-4 (Standard/Low) receive lighter evidence because misclassifying a generated file or a vendor dependency is low-consequence.

This is not a compromise of quality -- it is resource allocation under constraint. Military doctrine, medical triage, and risk management all use tiered investment. The alternative (uniform evidence) guarantees budget exhaustion before Tier 1 files are fully examined, which is a worse outcome than tiered evidence for everyone.

**Addressing Set A's Counter**: Set A cites the old prompt rule: "Evidence for KEEP is mandatory. Don't just say 'looks legitimate.'" Set B agrees with this rule and implements it -- the question is what constitutes sufficient evidence for different risk levels. For a `node_modules/` vendor file, confirming it is listed in `package.json` IS evidence. For a `deploy-prod.sh` script, confirming it is listed in `package.json` is NOT sufficient evidence. The tier system formalizes this distinction.

**Addressing Known Flaws**: F-B-07 notes that coverage tier targets (100/95/80/60%) are not empirically validated. F-B-08 identifies a budget conflict: evidence-mandatory KEEP for Tier 1-2 may exceed the Phase 2 budget allocation. These are legitimate concerns. The mitigation is to validate targets on a benchmark repository and adjust the default budget upward (from 300K to 500K for "Standard" tier) or relax Tier 2 to 1-field minimum evidence. The architectural intent (tiered investment) is correct even if the specific numbers need calibration.

**Honest Concession**: The specific threshold numbers (100/95/80/60%) were chosen without empirical validation. They need benchmarking. However, the principle of tiered evidence is sound regardless of the specific thresholds chosen.

---

### C-08: Budget and Cost Estimates
**Set B Position**: Explicit `--budget` flag with 300K token default, proportional phase allocation (5/25/35/20/15%), graceful degradation with 5-level cutback priority, runtime estimates from 8-45 minutes.

**Argument FOR Set B**: Set A provides zero token cost estimates for any of its proposals. The Flaw Hunter rated this F-A-01 (CRITICAL): "Implementation will either blow budgets or silently produce shallow results. Engineers cannot plan resource allocation without cost estimates." Set B's budget system is not an optional enhancement -- it is a structural prerequisite for predictable operation.

The budget system scored 8.8 composite in the strength rankings (B-4), tied with Set A's highest-scoring element. The key design insight is the graceful degradation sequence: when budget pressure activates, the system sheds the lowest-value work first (Tier 4 files, then Tier 3 depth, then Phase 3 cross-references, then Phase 2 depth). The "never cut" list (Phase 0 profiling, Phase 1 Tier 1-2 scanning, Phase 4 consolidation) ensures that the load-bearing phases always complete.

The reflection validation's 2-3x cost correction (B3, Dimension 3) is itself evidence of Set B's self-correcting analytical process. The original proposals underestimated costs. The reflection layer caught this and the PRD incorporated corrected estimates. Set A has no equivalent self-correction mechanism because it never estimated costs in the first place.

**Addressing Set A's Counter**: Set A argues that cost control is "implementation-level detail." This is incorrect. A cleanup audit that consumes unpredictable tokens is not a tool -- it is a liability. Budget is an architectural constraint that shapes every other design decision (evidence depth, coverage targets, number of batches). Treating it as an afterthought is how v1 ended up with 12 profiles from a 5,857-file repo.

**Addressing Known Flaws**: F-B-02 correctly identifies that even Set B's revised estimates may be underestimated. The 300K "Standard" scenario may require 500-700K tokens in practice. The mitigation is empirical benchmarking before finalizing defaults, plus the `--dry-run` flag (already in the PRD) which runs Phase 0 only to produce cost estimates before committing resources. F-B-09 challenges the degradation order, arguing Phase 3 cross-references are more valuable than Phase 2 depth. The mitigation is making degradation order configurable via `--focus` flag.

**Honest Concession**: The specific token estimates need empirical validation. The 300K "Standard" default is likely too low for a 6,000-file repo. However, having a budget system with wrong defaults is still better than having no budget system at all, because defaults are easily corrected once benchmarked.

---

### C-09: ARCHIVE as a Classification
**Set B Position**: ARCHIVE is a secondary qualifier on DELETE (`DELETE:archive-first`), not a standalone top-level category.

**Argument FOR Set B**: The two-tier system treats ARCHIVE as what it fundamentally is: a DELETE operation with a pre-step. When an engineer receives a `DELETE:archive-first` classification, the action is clear: (1) copy to archive location, (2) delete from current location. The primary action is deletion. If ARCHIVE were a top-level category, the engineer must first determine whether it means "preserve permanently" or "save before removing." The qualifier eliminates this ambiguity.

The composability argument also applies. If ARCHIVE is a top-level category, then CONSOLIDATE, MOVE, FLAG, and every future action type also need top-level categories, leading to category proliferation. The two-tier system handles all of these through qualifiers on 4 stable primary actions. This is the difference between a fixed enumeration and an extensible taxonomy.

**Addressing Set A's Counter**: Set A argues that ARCHIVE has different semantics from DELETE. This is partially true -- the intent differs (preserve vs discard). But the engineer action is the same: remove the file from its current location. The qualifier captures the intent difference while keeping the action clear. Martin Fowler's panel critique (A2, Section 8) actually supports Set B: "treat ARCHIVE as a label, not a mandatory directory."

**Addressing Known Flaws**: No significant flaws identified for this specific element.

**Honest Concession**: This is genuinely a matter of modeling preference. Both approaches work. Set B's approach is more composable; Set A's is more explicit for this specific case. The difference is minor.

---

### C-10: Cross-Reference / Cross-Boundary Detection
**Set B Position**: Dedicated Phase 3 with dependency graph construction, orphan node detection, confidence scoring by hop distance, and INVESTIGATE classifications for cross-boundary candidates.

**Argument FOR Set B**: Cross-reference synthesis was rated the #1 highest-ROI improvement by unanimous consensus of all 4 debate agents (B2, Proposal 1). The reasoning is that cross-boundary dead code -- files that appear alive within their module but are not imported by any other module -- is the one category of finding that parallel, isolated scanners are structurally incapable of detecting. No amount of per-file depth improvement will catch a component that is exported but never imported elsewhere.

Set A treats cross-cutting analysis as an enhancement to the existing Pass 3 (better checklists, broken reference formatting). This addresses output formatting but not the fundamental capability gap. The current Pass 3 cannot detect that `frontend/components/LegacyWizard.tsx` is exported by `frontend/components/index.ts` but never imported by any page or layout, because each scanner only sees its own batch of files.

The dependency graph specification (B4, Section 5 Phase 3) provides the mechanism: build a directed graph from structured scanner output (files as nodes, import/export as edges), identify orphan nodes (no incoming edges), and apply confidence scoring by hop distance. Files more than 3 hops from any entry point get `DELETE` candidacy; files 1-3 hops get `INVESTIGATE`.

**Addressing Set A's Counter**: Set A correctly notes that the existing Pass 3 already produces duplication matrices. Set B preserves this capability (duplication matrix production is part of Phase 3) while adding the dependency graph as a new capability. There is no regression.

**Addressing Known Flaws**: F-B-03 raises the most serious challenge: dependency graph construction via LLM is infeasible for dynamic imports. This is a legitimate concern. The mitigation is twofold: (1) use static analysis tools (e.g., `madge` for JS, `pydeps` for Python) via Bash as a pre-step where available, falling back to grep-based import scanning; (2) label all dynamic-import results as "approximate" and classify them as `INVESTIGATE:dynamic-import` rather than `DELETE`. The architectural intent (cross-boundary analysis) is preserved while the implementation acknowledges its limitations.

**Honest Concession**: The dependency graph will have false negatives (missed dynamic imports) and false positives (hallucinated dependencies). It is not a substitute for static analysis tools. But an approximate graph that catches 70% of cross-boundary dead code is still infinitely better than no cross-boundary detection at all.

---

### C-11: Spot-Check Validation
**Set B Position**: Dedicated 10% spot-check by `audit-validator` agent in Phase 4. If agreement rate < 85%, a warning banner is added to the report.

**Argument FOR Set B**: The v1 spec already promises "10% spot-check validation" -- it was never implemented. Set B implements the existing promise. The mechanism is simple: randomly sample 10% of classifications (stratified by tier), re-run evidence gathering independently for each, compare with the original classification, and flag disagreements. This provides a measurable quality signal that users can evaluate.

Set A provides no spot-check mechanism at all. Its verification approach (golden-output fixtures against a synthetic repo) tests the prompt, not the actual subagent behavior on real data. A prompt that passes fixture tests can still produce garbage output on a repository with unexpected patterns. Runtime validation catches this class of failure.

**Addressing Set A's Counter**: Set A does not address spot-check validation, so there is no direct counter-argument to rebut.

**Addressing Known Flaws**: F-B-05 raises a fundamental challenge: LLM-on-LLM validation measures consistency, not correctness. Two models can consistently agree on wrong answers. This is valid. The mitigations are: (1) rename "agreement rate" to "consistency rate" to set correct expectations; (2) include 3-5 manually verified ground-truth calibration files as anchors; (3) acknowledge the limitation prominently in the report. The spot-check is not a guarantee of correctness -- it is a smoke test that catches gross failures (e.g., a scanner that classifies everything as KEEP). Even with the limitation, it provides more signal than Set A's approach of no runtime validation at all.

**Honest Concession**: F-B-05's critique is fundamentally correct. LLM-on-LLM validation has limited epistemic value. The 85% threshold provides a false sense of precision. A more honest framing is "consistency check that catches systematic scanner failures" rather than "quality gate." The mitigation (ground-truth calibration files) partially addresses this but requires manual setup.

---

### C-12: Phase 0 / Pre-Audit Profiling
**Set B Position**: Phase 0: Profile & Plan is a mandatory pre-pass that detects domains, classifies files into risk tiers, generates batch manifests, and auto-generates config if absent.

**Argument FOR Set B**: Phase 0 is the structural prerequisite for almost every other improvement. Without domain detection, scanners cannot be domain-aware. Without file tiering, evidence requirements cannot be calibrated. Without a batch manifest, there is no coverage tracking (you cannot track coverage if you do not know the universe of files). Without auto-config generation, first-time users face a cold-start failure.

The dependency chain analysis (B3, Dimension 1) demonstrates this concretely: cross-reference synthesis (Phase 3) depends on structured scanner output, which depends on batch decomposition (Phase 2 infrastructure), which depends on profiling (Phase 0). Remove Phase 0 and the entire downstream dependency chain collapses.

Phase 0 is designed to be cheap: Haiku model, 30-60 seconds, 5% of token budget. The output is a JSON batch manifest and (optionally) an auto-generated `audit.config.yaml`. This is not a significant cost -- it is an investment that pays dividends in every subsequent phase.

**Addressing Set A's Counter**: Set A begins directly with Pass 1 (Surface Scan). This means scanners receive files with no domain awareness, no tier assignment, and no batch manifest. The result is what v1 produced: 6 unnamed scanners processing 5,857 files monolithically with no coverage guarantees. Phase 0 is the fix.

**Addressing Known Flaws**: F-B-04 warns that auto-config generation is a correctness risk (wrong framework detection cascades to wrong tier assignments). The mitigation is: (1) Phase 0 output is a visible artifact (`audit.config.yaml`) that users can inspect and correct; (2) `--dry-run` runs Phase 0 only, showing the generated config without proceeding to scanning; (3) the report prominently notes which config values were auto-detected vs user-specified. These mitigations transform Phase 0 from a black box into a transparent, correctable step.

**Honest Concession**: The auto-config generation adds a new failure mode that the current system does not have. If the Haiku model misidentifies the framework, downstream results will be wrong. The `--dry-run` mitigation is essential, not optional.

---

### C-13: Recommendation Category Count
**Set B Position**: 4 primary categories (DELETE/KEEP/MODIFY/INVESTIGATE) with 13+ secondary qualifiers. REVIEW is eliminated; its function is replaced by INVESTIGATE.

**Argument FOR Set B**: This is an extension of the C-03 argument. Set A's 5+ flat categories (DELETE, KEEP, ARCHIVE, FLAG, BROKEN_REFERENCES, REMAINING, NOT_YET_AUDITED) create a parsing burden for consumers. Each new use case requires a new top-level category. Set B's 4-primary system is closed (no new primary categories needed) while being open for extension (new qualifiers can be added freely).

The elimination of REVIEW is deliberate. REVIEW was the v1 catch-all for "we don't know" -- it was used for both "ambiguous files that need human judgment" and "files where evidence gathering failed." Set B splits these into distinct INVESTIGATE qualifiers (`human-review-needed` vs `insufficient-evidence` vs `cross-boundary` vs `dynamic-import`), providing more actionable information.

**Addressing Set A's Counter**: Set A argues that each action type deserves its own named section for scanability. As noted in C-03, this is a report rendering concern, not a data model concern. The report can group `MODIFY:flag:[issue]` items under a "FLAG" heading while maintaining the composable data model.

**Addressing Known Flaws**: Same as C-03 (F-B-11 dumping ground, F-B-19 semantic drift). See C-03 mitigations.

**Honest Concession**: None beyond C-03.

---

### C-14: Batch Decomposition -- Static vs Dynamic
**Set B Position**: Dynamic batch decomposition with risk-weighted parallel scanning. Phase 0 generates a batch manifest. Risk-weighted depth: > 0.7 deep, 0.4-0.7 standard, < 0.4 shallow.

**Argument FOR Set B**: The 44x profiling gap is the smoking gun. The old manual approach used 26 targeted batches with explicit file lists and produced 527+ per-file profiles. The new automated approach uses 6 unnamed parallel scanners with no documented file assignments and produced 12 profiles. The single biggest architectural difference between these approaches is batch decomposition.

Set A does not address batch decomposition at all. The vNext PRD mentions `--batch-size N` as a flag but provides no batch generation mechanism. Without explicit file assignment to batches, scanners have no documented responsibility, no depth calibration, and no coverage accountability. This is the root cause of the v1 quality deficit, not a "nice to have."

Set B's dynamic batch decomposition (B2, Proposal 6) replaces the manual 26-batch approach with automated batch generation from Phase 0's risk-weighted file classification. Each batch gets a JSON manifest specifying exactly which files to examine at what depth. This makes coverage tracking possible (compare manifest to results) and batch assignment auditable (the manifest is a visible artifact).

**Addressing Set A's Counter**: Set A treats batch decomposition as an "implementation concern." This is a categorization error. Batch decomposition is an architectural decision that determines coverage quality, profile depth, and scanner accountability. Calling it an implementation detail is like calling database schema design an implementation detail.

**Addressing Known Flaws**: No flaws specific to batch decomposition were identified. The related concern (F-B-10, monorepo handling) is about workspace boundary detection, which is a Phase 0 profiling concern addressed by adding workspace file detection.

**Honest Concession**: None. Batch decomposition is a clear gap in Set A that Set B addresses thoroughly.

---

### C-15: Spec-Implementation Gap Recognition
**Set B Position**: Phase 0 of the implementation roadmap is "Enforce Existing Spec" -- implement all v1 promises before adding any new features.

**Argument FOR Set B**: This is Set B's foundational insight and it changes the entire problem framing. The reflection validation (B3, Dimension 2) discovered that the v1 spec already promises 5 classification categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check validation. None were implemented. Set A writes a new PRD without examining the existing spec, effectively proposing to add features to a spec that already has unimplemented features.

The Flaw Hunter rated Set A's omission as F-A-02 (CRITICAL): "The PRD may repeat the exact failure pattern of v1: spec features that sound good but never get implemented because the underlying architecture does not enforce them." This is not a minor oversight -- it is the central thesis of the entire improvement effort.

Set B's "enforce existing spec first" requirement prevents the credibility gap from widening. If v2 adds Pass 4 Docs Quality, a known-issues registry, and ARCHIVE classification on top of 5 existing unimplemented features, the result is a spec with 8+ unimplemented features instead of 5. The spec loses all credibility as a contract.

**Addressing Set A's Counter**: Set A frames the problem as "old prompts caught things new output misses." This is an output-level framing. Set B frames the problem as "the architecture does not enforce its own spec." The output-level framing leads to additive fixes (add more passes). The architecture-level framing leads to structural fixes (enforce existing promises, then add new ones). History favors the structural approach: the v1 failure was not caused by an insufficient spec but by an architecture that could not enforce it.

**Addressing Known Flaws**: F-B-13 notes that the PRD claims to address all reflection corrections but some are only partially resolved. The mitigation is an explicit traceability matrix mapping each v1 spec promise to its v2 implementation section with pass/partial/fail assessment. This makes enforcement auditable.

**Honest Concession**: None. This is Set B's most important contribution and there is no legitimate counter-argument. Set A simply did not examine the existing spec.

---

### C-16: Coverage Tracking and Guarantee
**Set B Position**: Tiered coverage contracts: Critical 100%, High 95%, Standard 80%, Low 60%. Manifest-first execution with per-file tracking. Coverage below threshold triggers WARN, never blocks.

**Argument FOR Set B**: Coverage tracking without thresholds is meaningless accounting. Set A proposes "REMAINING / NOT_YET_AUDITED coverage accounting" but provides no thresholds, no tiering, and no enforcement. This is the equivalent of tracking test coverage but never setting a minimum threshold.

Set B's tiered coverage contracts align coverage requirements with file risk. Critical files (deployment scripts, CI/CD, migrations) must have 100% coverage because missing even one could mean missing a critical vulnerability. Low-risk files (assets, generated code, vendor) need only 60% coverage because the expected finding rate is near zero.

The "WARN, never block" design is pragmatic. An audit that blocks on coverage failure produces no output -- which is worse than an audit with incomplete coverage. The warning banner communicates the limitation without denying users any value.

**Addressing Set A's Counter**: Set A's coverage accounting (list what was not audited) is a subset of Set B's approach. Set B includes the accounting (the coverage report JSON lists unexamined files) AND adds actionable thresholds.

**Addressing Known Flaws**: F-B-07 notes that the specific thresholds are not empirically validated. The mitigation is benchmarking on real repositories and making thresholds configurable via `audit.config.yaml`. The structural mechanism (tiered contracts) is sound; only the default numbers may need adjustment.

**Honest Concession**: The 100% threshold for Critical files may be aspirational under tight budgets. In practice, graceful degradation may reduce Critical coverage to 95%+ under the 100K "Minimal" budget tier.

---

### C-17: Output Format -- Markdown vs JSON
**Set B Position**: Phase summaries as JSON files for machine consumption. Separate human-readable FINAL-REPORT.md. Scanner outputs conform to a structured schema.

**Argument FOR Set B**: JSON intermediate outputs are the architectural enabler for three capabilities: (1) schema validation (anti-lazy enforcement -- verify that required fields are populated); (2) structured cross-phase data flow (Phase 3 can programmatically consume Phase 1-2 JSON to build the dependency graph); (3) coverage tracking (compare manifest JSON to results JSON). None of these work with Markdown intermediates because Markdown is not machine-parseable.

The human-readable FINAL-REPORT.md is still present. Users read the report; the pipeline reads JSON. This is standard practice in CI/CD tooling (JUnit XML for machines, HTML reports for humans).

**Addressing Set A's Counter**: Set A argues Markdown is human-readable and directly scannable. This is true for the final report, which Set B also produces as Markdown. The disagreement is about intermediate artifacts, which are consumed by the pipeline, not by humans. Making intermediates human-readable at the cost of machine-parseability is an anti-pattern.

**Addressing Known Flaws**: F-B-06 warns that Haiku may struggle with complex JSON output. The mitigation (simplify Phase 1 schema to essential fields) preserves JSON output while reducing schema complexity for Haiku.

**Honest Concession**: None. JSON intermediates with Markdown final reports is strictly superior to Markdown everywhere.

---

### C-18: Quality Gate on Spot-Check Failure
**Set B Position**: Spot-check agreement rate < 85% adds a warning banner to the report but does not block report generation.

**Argument FOR Set B**: Set A does not address quality gates on spot-check failure because Set A does not have a spot-check mechanism. Set B's approach is pragmatic: a warning banner communicates reduced confidence without denying the user any output. Blocking on quality gate failure would mean that messy repositories (the primary target audience) might never produce a report.

The 85% threshold was chosen to balance sensitivity and false alarm rate. At 85%, approximately 1 in 7 spot-checked files can disagree before triggering the warning. This is strict enough to catch systematic scanner failures but loose enough to tolerate legitimate edge cases (dynamic imports, conditional compilation, platform-specific code).

**Addressing Set A's Counter**: N/A -- Set A does not address the topic.

**Addressing Known Flaws**: F-B-05's critique (LLM-on-LLM consistency vs correctness) applies here. The mitigation is transparent labeling: the report should say "Consistency check: 92% agreement on 10% sample" rather than "Quality score: 92%."

**Honest Concession**: The 85% threshold is arbitrary and needs empirical calibration.

---

### C-19: .env Handling Approach
**Set B Position**: `.env*` handling is a Phase 1 correctness fix: read actual file contents to distinguish real credentials from template values. Credential scanning is rated CRITICAL.

**Argument FOR Set B**: Set B's Finding 6 (B1) provides the smoking gun: real credentials in `.env.production` were misidentified as template values by the v1 audit. This is not a depth issue or an enhancement opportunity -- it is a correctness failure with security implications. All 4 debate agents agreed unanimously: "non-negotiable fix."

Set A classifies `.env` handling as a P2 enhancement (key-presence matrix). This conflates two distinct concerns: (1) correctly identifying real credentials (a correctness fix), and (2) tracking key consistency across env files (an enhancement). Set B prioritizes the correctness fix in Phase 1 because a false negative on real credentials is categorically more severe than missing a key consistency check.

The implementation is bounded: enumerate 5-10 `.env*` files, pattern-match for real credential patterns (`sk-*`, `ghp_*`, `AKIA*`, base64 > 40 chars), and never print values. Cost: ~10K tokens. Risk of not fixing: real credentials in a repository going undetected.

**Addressing Set A's Counter**: Set A's key-presence matrix is a complementary feature, not a substitute for credential detection. Both could coexist. The disagreement is about priority: Set B correctly identifies credential scanning as Phase 1 (correctness) while Set A defers it to P2 (enhancement).

**Addressing Known Flaws**: No significant flaws were identified for the credential scanning proposal specifically.

**Honest Concession**: None. The credential scanning correctness fix is the highest-confidence, lowest-cost improvement in either set.

---

### C-20: Progressive Depth Across Passes
**Set B Position**: Two-level signal-triggered depth: 50-line default with full-file read triggered by specific signals (credential imports, TODO/FIXME, complex conditionals, eval, file size > 300 lines).

**Argument FOR Set B**: Without explicit depth rules, scanners default to whatever depth the model chooses -- which in v1's case meant shallow reads for the vast majority of files. Signal-triggered depth escalation ensures that files with high-risk indicators receive full examination while files without indicators receive a cost-effective 50-line read.

The two-level system (simplified from the original 4-level proposal through debate) balances cost and thoroughness. The signal triggers are evidence-based: credential imports, TODO/FIXME patterns, and eval/exec usage are all indicators of files that need deeper examination.

**Addressing Set A's Counter**: Set A does not address depth escalation at all. The omission leaves depth as an implicit, undocumented parameter that varies per model run.

**Addressing Known Flaws**: No significant flaws specific to this element.

**Honest Concession**: The trigger rate assumption (15-20%) may be too low for messy codebases (B3, Dimension 3 notes this could be 40-50%). The budget system's graceful degradation handles this by reducing depth under budget pressure, but the cost estimate is likely underestimated.

---

### C-21: Checkpointing Granularity
**Set B Position**: `progress.json` updated after every batch within a phase, enabling mid-phase resume via `--resume` flag.

**Argument FOR Set B**: For large repositories with many batches per phase, pass-level checkpointing means losing all progress on session interruption. If Phase 1 has 20 batches and the session interrupts after batch 15, pass-level checkpointing means re-running all 20 batches. Batch-level checkpointing means re-running only batches 16-20.

The `--resume` flag (B4, Section 7) is a concrete user need: audit sessions can be interrupted by token limits, timeouts, or user action. Without mid-phase resume, interrupted audits must restart from scratch, wasting all tokens spent on completed batches.

The v1 spec already promises "resume-from-checkpoint on session interruption" -- another unimplemented feature that Set B's Phase 0 (enforce existing spec) would address.

**Addressing Set A's Counter**: Set A's pass-level checkpointing (`progress.json` with pass status fields) is a subset of batch-level checkpointing. Set B's approach is strictly more granular.

**Addressing Known Flaws**: F-B-16 raises the concern of concurrent audit runs corrupting shared output. The mitigation is run-ID isolation (e.g., `.claude-audit/run-{timestamp}/`).

**Honest Concession**: Batch-level checkpointing adds implementation complexity. For small repos with few batches, the benefit over pass-level checkpointing is negligible.

---

### C-22: Claim Spot-Check Scope (Docs)
**Set B Position**: 3 claims per doc, limited to API-reference and setup-guide category docs.

**Argument FOR Set B**: Set B's narrowing to API-reference and setup-guide docs is driven by cost-benefit analysis. These are the doc categories most likely to contain verifiable structural claims (file paths, port numbers, command examples). Architecture docs and conceptual docs contain claims that are harder to verify programmatically ("the system uses event-driven architecture") and more likely to produce false positives.

Limiting to 3 claims (vs Set A's 3-5) is a minor token savings that adds up across many docs. The expected finding rate for claims 4-5 is lower than for claims 1-3 (the most important claims are checked first).

**Addressing Set A's Counter**: Set A provides broader coverage (3-5 claims across all sampled docs). The breadth advantage is real but the cost is higher and the marginal return on claim 4-5 is low. This is a genuine tradeoff.

**Addressing Known Flaws**: No significant flaws specific to this element.

**Honest Concession**: This is a minor optimization. Set A's broader coverage is a defensible alternative. The difference is LOW stakes as the conflict register correctly identifies.

---

## Overall Case for Set B

Set B's approach is the correct one for a fundamental reason: **the v1 failure was architectural, not scope-related**. The v1 spec already promised 5 classification categories, coverage tracking, checkpointing, evidence-gated classification, and 10% spot-check validation. None were implemented. This was not because the spec was insufficient -- it was because the architecture (6 unnamed generic scanners, no structured output, no coverage tracking, no batch decomposition) could not enforce the spec's requirements.

Set A's response to this failure is to add more scope: a 4th pass for docs, a known-issues registry, more output categories. This is additive thinking applied to a structural problem. It is the equivalent of adding rooms to a building with a cracked foundation. The rooms may be individually well-designed (and Set A's Pass 4 output schema is genuinely excellent, scoring 8.8 composite), but they will settle along with the rest of the building.

Set B's response is to fix the foundation first: enforce the existing spec (Phase 0), fix correctness bugs (Phase 1), build infrastructure (Phase 2), then add depth and extensions (Phases 3-5). This ordering respects dependency chains, prevents credibility erosion, and ensures that new features are built on a substrate that can actually enforce them.

The quantitative evidence supports Set B across the board:

- **Strength rankings**: Set B average composite 8.55 vs Set A average 7.70 (+0.85 delta)
- **Coverage**: Set B has 15 unique contributions vs Set A's 5
- **Evidence quality**: Set B average 8.8 vs Set A average 7.5 (+1.3 delta, the largest margin)
- **Conflict register**: Set B has stronger evidence in 18 of 22 conflicts

Set B is not without flaws. The token cost estimates need empirical validation (F-B-02). The dependency graph may be unreliable for dynamic imports (F-B-03). The LLM-on-LLM validation has limited epistemic value (F-B-05). The implementation effort estimates are too low (F-B-14). These are all addressable weaknesses that can be mitigated without abandoning Set B's architectural framework.

The single area where Set A is genuinely stronger -- cross-run known-issues suppression (C-04) -- is a feature that can be incorporated into Set B's Phase 5 extensions without changing the architectural direction. Similarly, Set A's detailed Pass 4 output schema and target user definitions can be adopted into Set B's framework.

The correct merger strategy is: **Set B's architecture as the skeleton, enriched with Set A's best elements where they fill genuine gaps.** Not the reverse. Adding Set A's features to Set B's architecture will produce a coherent, enforceable spec. Adding Set B's features to Set A's architecture will produce a longer list of promises that the architecture still cannot enforce.

---

*Set B Advocate brief complete | 2026-02-20*
*22 conflicts analyzed | 18 strong advocacy positions, 3 concessions with mitigations, 1 genuine weakness acknowledged (C-04)*
