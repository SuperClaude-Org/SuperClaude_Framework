# Wave 2: Set A Advocacy — Arguments FOR Set A's Position

**Date**: 2026-02-20
**Role**: Set A Advocate
**Core Philosophy**: "Add targeted capabilities to the existing structure. Fix the output gaps with specific, bounded additions (Pass 4, known-issues registry, output schema hardening). Don't overhaul the architecture."

---

## C-01: Phase/Pass Structure (Count and Architecture)

**Set A Position**: 4 passes -- keep existing 3-pass structure, add Pass 4 (Docs Quality). Additive design.

**Argument FOR Set A**:

Set A's additive approach is the safer, faster path to delivering value. The existing 3-pass architecture has been running in production and producing useful output -- the duplication matrices from Pass 3 were specifically praised as "the best part of the new output." Set A preserves this proven foundation and adds exactly one new capability (docs audit) to address the single largest observable gap.

Set B proposes restructuring the entire execution flow into 5 phases with new bookend phases (Phase 0 profiling and Phase 4 consolidation). This is a rewrite, not an improvement. Every rewrite carries the risk of breaking what already works. The existing Pass 1-3 outputs are not broken -- they are incomplete. The correct response to incomplete output is to add what is missing, not to tear down the scaffolding.

Furthermore, Set A's approach has a dramatically shorter time-to-value. Adding Pass 4 rules to the existing skill is a bounded task that can be shipped and validated independently. Set B's Phase 0 profiling is a prerequisite for everything else in their architecture, meaning nothing can ship until the foundation is built -- a classic waterfall risk.

The simplicity argument is not just about developer convenience. Simpler architectures are easier to debug, easier to modify, and less likely to have emergent failure modes. A 4-pass sequential pipeline has predictable behavior. A 5-phase architecture with inter-phase data dependencies, batch manifests, and dynamic batch decomposition has a much larger surface area for failure.

**Addressing Set B's Counter**: Set B argues that Phase 0 profiling is a "structural prerequisite" for other improvements. This is true only if you accept Set B's entire architectural vision as mandatory. If instead you accept that the existing scanning approach, while imperfect, produces useful output that can be incrementally improved, then Phase 0 is not a prerequisite -- it is an optimization that can be added later.

**Addressing Known Flaws**: F-A-03 (Pass 4 depends on undefined infrastructure) is a valid concern. The mitigation that preserves Set A's intent is to define a lightweight inter-pass data contract -- not a full JSON schema for all scanner output, but a minimal set of structured data that Pass 1-3 already emit in their markdown summaries (file lists, classification decisions, broken reference counts) that Pass 4 can consume. This is a bounded schema addition, not an architectural overhaul.

**Honest Concession**: Set B's insight that the dependency chain matters is valid. If the goal were to build a comprehensive system from scratch, 5 phases would be the right architecture. Set A's weakness is that it does not provide a path to that comprehensive system. However, the question is not "what is the ideal architecture?" but "what delivers the most value fastest with the least risk of breaking what works?"

---

## C-02: Documentation Audit -- Mandatory vs Opt-In

**Set A Position**: Pass 4 Docs Quality is mandatory when `--pass all` is used. Classified as P0 (must-have).

**Argument FOR Set A**:

This is the conflict where Set A's position is strongest and Set B's demotion is hardest to defend. The entire improvement effort was motivated by the observation that "the audit has near-zero signal about documentation correctness." The gap analysis that justified this project started from docs being the number one problem. Set B's own Finding 1 rated the docs audit gap as CRITICAL. Then the 4-agent debate downgraded it to MEDIUM and deferred it to Phase 5 (the last implementation phase).

This is a classic case of infrastructure enthusiasm displacing user value. The stakeholder complaint is "docs are never audited." Set B's response is "we will build a profiler, a batch decomposition system, a dependency graph, a coverage manifest, a budget system, an anti-lazy enforcement mechanism, and THEN, in Phase 5, maybe add a docs audit as an opt-in extension." By the time Phase 5 arrives, the project may have lost momentum, budget, or both.

Set A makes the docs audit P0 because it addresses the primary user need. The cost concern (Set B's reason for demotion) is real but manageable. Set A explicitly proposes cost controls: directory-level sampling (5-10 representative docs for large trees), structural claims only (no semantic analysis), capped output. These controls bound the token cost without sacrificing the feature entirely.

Making docs audit mandatory when `--pass all` is specified is the right default. Users who run `--pass all` are asking for a comprehensive audit. Omitting documentation from a comprehensive audit is a contradiction in terms.

**Addressing Set B's Counter**: Set B argues that token cost analysis shows estimates are 2-3x too low, making docs audit expensive. This is true, but the correct response is to budget for it (using Set A's sampling controls), not to defer it indefinitely. A bounded docs audit with sampling costs far less than Set B's dependency graph construction, yet delivers more directly actionable output.

**Addressing Known Flaws**: F-A-10 (sampling policy not defined concretely) is valid. The mitigation: define the sampling strategy as stratified by directory depth, prioritizing most-recently-modified docs and largest docs. Add a configurable `--docs-sample-size` parameter with a default of 10 docs per top-level directory.

**Honest Concession**: Set B's 20% token budget cap is a good mechanism that Set A should adopt. The mandatory vs opt-in distinction is less important than ensuring the feature exists in the v2 MVP at all. If the compromise is "mandatory when `--pass all` but budget-capped at 20%," that preserves Set A's intent while addressing Set B's cost concern.

---

## C-03: Classification System -- Categories and Structure

**Set A Position**: Expand from 3 categories by adding ARCHIVE, FLAG, and BROKEN_REFERENCES as distinct output buckets. Flat classification.

**Argument FOR Set A**:

Set A's flat classification system prioritizes human readability and immediate actionability. When an engineer reads an audit report, they want to scan for what to do: delete these files, archive those files, flag these for code changes, fix these broken references. Each action type maps to a distinct mental model and a distinct workflow. A flat list of named sections serves this use case directly.

The two-tier system (DELETE:archive-first, MODIFY:flag:[issue]) is more elegant as a data model but less scannable as a report format. Engineers will not grep for `MODIFY:consolidate-with:docker-compose.prod.yml` -- they will scan for a "CONSOLIDATE" heading. The two-tier system adds a layer of indirection between the engineer's mental model and the report structure.

Moreover, the flat system is simpler to implement, test, and validate. Each output bucket has clear acceptance criteria: does the ARCHIVE section exist? Does it contain files from temporal artifact directories? Does each entry have a suggested destination? The two-tier system requires parsing compound categories and validating qualifier syntax, adding implementation complexity for what is ultimately a presentation concern.

**Addressing Set B's Counter**: Set B correctly identifies that flat categories can create ambiguity (is CONSOLIDATE a DELETE or a KEEP?). This is a real concern, but it is better addressed by clear definitions per category than by adding qualifier syntax. Set A's ARCHIVE category has clear semantics: "preserve for historical value but remove from active tree." There is no ambiguity about the primary action.

**Addressing Known Flaws**: The lack of backward compatibility mapping is a genuine gap in Set A. The mitigation: add explicit mappings from Set A's categories to the v1 categories. ARCHIVE maps to v1's implicit "move to archive" action. FLAG maps to v1's "requires code changes" subset of REVIEW.

**Honest Concession**: Set B's two-tier system is more extensible and handles edge cases more gracefully. If the audit system is expected to evolve significantly, the composable model is superior. Set A's flat model is better for the v2 MVP where simplicity and speed-to-delivery matter more than extensibility. If the merger adopts Set B's two-tier model, Set A's named sections should be preserved as report formatting -- the two-tier data model can be rendered as flat sections in the human-readable report.

---

## C-04: Known-Issues Handling -- Registry vs Post-Hoc Dedup

**Set A Position**: Sequential registry loaded before passes. Known issues stored as JSON with structured fields. Cross-run persistence.

**Argument FOR Set A**:

This is Set A's strongest conflict point, and the conflict register correctly identifies it. Set A's known-issues registry solves a fundamentally different and more important problem than Set B's post-hoc dedup: the cross-run persistence problem.

The primary use case is U2 from Set A's PRD: "Run audit weekly without re-discovering known issues." This is the repeated-audit-over-time scenario. A team that runs cleanup audits monthly does not want to see the same 34 known issues flagged every single time. They want the audit to say "these 34 items are already tracked; here are the 3 new findings since last month."

Set B's post-hoc deduplication in the consolidator only deduplicates within a single audit run. It collapses duplicate findings from multiple passes within one execution. It does nothing for the cross-run scenario because the consolidator has no memory of previous runs.

Set A's registry design is mature and well-specified: JSON schema with 6 fields (id, signature, category, created_at, status, reference), signature-based matching (not path-based, so file renames do not cause false positives), conservative suppression rules, and a dedicated ALREADY_TRACKED output section. The old prompt set used a 34-item known issues list that worked in practice. This is not speculative -- it is proven by operational history.

The serialization bottleneck argument (Set B's concern) is overstated. Loading a JSON file of 50-200 entries at the start of each pass adds negligible latency compared to the LLM inference time of each pass. The registry is read-only during the audit; it does not create a write bottleneck.

**Addressing Set B's Counter**: Set B argues that post-hoc dedup is cheaper (500 tokens) and preserves parallelism. This is true for within-run dedup, which is a complementary mechanism, not a replacement. The two approaches solve different problems and should coexist. Post-hoc dedup handles cross-pass duplicates within a run; the registry handles cross-run suppression.

**Addressing Known Flaws**: F-A-04 (no versioning or lifecycle) is valid. The mitigation: add a TTL field per entry (default 90 days), automatic staleness detection (if referenced file no longer exists, mark entry as "stale" and do not suppress), and a max-entries limit (default 200) with oldest-first eviction. These additions preserve the registry's cross-run intent while preventing unbounded growth.

**Honest Concession**: None needed. Set A is genuinely stronger here. The only improvement is to explicitly state that Set B's within-run post-hoc dedup should also be adopted as a complementary mechanism.

---

## C-05: Priority Ordering of Improvements

**Set A Position**: P0 = Pass 4 Docs Quality + Known-issues suppression registry. P1 = Broken-reference checklist, FLAG section, large directory assessment. P2 = .env key matrix.

**Argument FOR Set A**:

Set A's priority ordering is user-centric: it prioritizes the features that address the most visible user pain points. The docs audit gap and the repeated-rediscovery problem are the two complaints that motivated this entire effort. Making them P0 is a direct response to user needs.

Set A's ordering also has a practical advantage: P0 items can be built and shipped independently. Pass 4 rules can be added without changing anything about Passes 1-3. The known-issues registry is an optional overlay that does not require architectural changes. This means Set A's P0 can be delivered in a single sprint and validated against real audits before committing to deeper changes.

The argument that "enforce existing spec first" should be Phase 0 is intellectually compelling but practically risky. "Enforce existing spec" is a large, vague task that could consume significant effort before delivering any user-visible improvement. Users do not care whether their tool implements its own spec -- they care whether the tool produces useful output.

**Addressing Set B's Counter**: Set B's discovery that the v1 spec has unimplemented promises is a genuine insight. However, the correct response is not to halt all user-facing work until the existing spec is fully implemented. The correct response is to audit which unimplemented promises matter (coverage tracking, checkpointing) and incorporate them alongside new features, not before them. Set A's P0 items are compatible with enforcing existing spec promises -- they are not mutually exclusive.

**Addressing Known Flaws**: F-A-14 (backlog lacks effort estimates and dependency ordering) is valid. The mitigation: add t-shirt sizing (S/M/L) and dependency annotations. Pass 4 rules (L), templates update (M), link extractor (M), known-issues registry (M) -- all are independent and can be parallelized.

**Honest Concession**: Set A's flat backlog without dependency ordering is genuinely weaker than Set B's phased roadmap. The lack of dependency analysis means Set A could accidentally start work that depends on infrastructure that does not exist yet. However, Set A's P0 items (Pass 4 and known-issues registry) have no such dependencies -- they are self-contained additions to the existing system. The dependency ordering problem only emerges if you attempt Set B's more ambitious architectural changes.

---

## C-06: Subagent Architecture

**Set A Position**: Reuse existing agents. Only add a new specialized audit-docs subagent if Pass 4 quality is consistently poor.

**Argument FOR Set A**:

Set A's conservative approach to subagent architecture follows the principle of least change. The existing agents (audit-scanner, audit-analyzer) are running and producing output. Before adding 4 more specialized agents with model assignments, the rational first step is to test whether the existing agents can handle the new docs audit pass.

Set B proposes 6 named specialized agents with explicit model assignments. This is a significant increase in system complexity: 6 agents to coordinate, 6 sets of prompts to maintain, 6 potential failure points to monitor. The 44x profiling gap that Set B cites as evidence for specialization is partly a comparison artifact -- the old approach used 27 manual batch reports with human curation, not 6 automated agents.

Set A's Option A (reuse existing agents) provides a low-risk starting point. If the existing agents produce poor docs audit output, Set A explicitly provides Option B (add audit-docs subagent) as the escalation path. This is the scientific approach: test the hypothesis that existing agents are sufficient before investing in specialization.

**Addressing Set B's Counter**: Set B argues that the 44x profiling gap proves generic scanners are insufficient. However, as the Flaw Hunter noted (F-B-01), this metric compares a multi-session human-guided process with a single automated run. The comparison is misleading. The right question is not "can we match the old profile count?" but "can we produce useful docs audit output with existing agents?" That question has not been tested.

**Addressing Known Flaws**: No specific Set A flaw applies here. The conservative approach has no known flaws -- it is a risk-management strategy.

**Honest Concession**: If the merged spec adopts Set B's broader architectural changes (Phase 0 profiling, batch decomposition, coverage manifests), then specialized agents with model assignments become more justified because there are more distinct tasks that benefit from specialization. Set A's conservative approach is most appropriate when the overall architecture remains simple.

---

## C-07: Evidence Requirements for KEEP -- Uniform vs Tiered

**Set A Position**: Per-file profiles demanded uniformly. Evidence is mandatory for KEEP decisions but the scheme is not tiered by risk.

**Argument FOR Set A**:

Set A's uniform evidence requirement embodies a strong principle: "Evidence for KEEP is mandatory. Don't just say 'looks legitimate.'" This principle prevents the most common failure mode of cleanup audits -- lazy classification where thousands of files receive KEEP without any justification.

The principle is derived from operational experience with the old prompt set, which demanded per-file structured profiles for audited files. The old approach did not distinguish between "important KEEP" and "unimportant KEEP" -- it required evidence for all KEEP decisions, and this discipline is what produced 527+ profiles instead of 12.

The uniform requirement is also simpler to implement, test, and enforce. "Every KEEP must have evidence" is a single rule. Tiered evidence requires: (1) a tier assignment mechanism (Phase 0 profiling), (2) per-tier evidence schemas, (3) per-tier coverage thresholds, and (4) handling of tier misassignment. Each layer adds complexity and potential failure modes.

**Addressing Set B's Counter**: Set B's token cost analysis (175K-585K additional tokens for uniform evidence on all 5,800 files) is the strongest argument against uniform evidence. This is a real constraint. However, the cost can be managed within Set A's framework through the same sampling approach used for docs: require evidence for all KEEP decisions on *examined* files, and use coverage accounting (REMAINING/NOT_YET_AUDITED) to transparently show which files were not examined.

**Addressing Known Flaws**: The token cost concern is legitimate. The mitigation that preserves Set A's principle: require uniform evidence for all KEEP decisions, but allow the *depth* of evidence to vary based on practical constraints. A one-line evidence annotation ("imported by 3 files in src/components/") is better than no evidence at all, and costs far less than a full 3-field profile. This preserves the "no lazy KEEP" principle while acknowledging budget reality.

**Honest Concession**: Set B's tiered approach is more practical for large repos where examining every file at full depth is infeasible. The token cost arithmetic is persuasive. Set A's uniform principle is the right *aspiration* but may need to be implemented as "uniform minimum evidence with tiered depth" rather than "uniform full evidence." This concession preserves Set A's core insight (no KEEP without evidence) while accepting Set B's cost reality.

---

## C-08: Budget and Cost Estimates

**Set A Position**: No explicit token budget numbers. Cost control mentioned via sampling and caps but not quantified.

**Argument FOR Set A**:

Set A's PRD deliberately focuses on *what* the audit should produce rather than micro-managing *how many tokens* it should consume. This is a defensible specification philosophy: PRDs define requirements and constraints, not resource allocation. Token budgets are an implementation concern that depends on the specific LLM, the repo size, and the user's willingness to pay.

Set A does address cost control -- through sampling policies (5-10 representative docs), output caps (first N broken links with total counts), and scope constraints (structural claims only, no semantic analysis). These are functional constraints that bound cost without requiring a numeric budget system.

Furthermore, Set B's own budget numbers are suspect. The Flaw Hunter (F-B-02) identified that Set B's "revised" estimates are still likely underestimates. The "Standard" scenario claims 300K tokens for 3,300 files at 90 tokens per file -- insufficient for 8-field profiles with grep evidence. If the budget numbers are wrong, a budget enforcement system built on wrong numbers will produce misleading results (labeling "Standard" what is actually "Minimal").

**Addressing Set B's Counter**: Set B argues that without explicit budget controls, the audit is unpredictable. This is fair. The mitigation that preserves Set A's intent: adopt a budget flag as a safeguard (Set B's `--budget` concept) but with fewer predetermined allocation percentages. Let the audit run with functional constraints (sampling, caps) and use the budget as a hard ceiling, not as a pre-allocated distribution.

**Addressing Known Flaws**: F-A-01 (no token budget model or cost ceiling) is the most valid criticism of Set A. The mitigation: add a `--budget` flag with a generous default and a simple rule -- "if budget is exhausted, complete current pass and generate report from available data." This is simpler than Set B's 5-level graceful degradation and less likely to produce mislabeled results.

**Honest Concession**: Set A is genuinely weaker here. A production tool needs some form of budget awareness. The concession is: adopt a budget mechanism, but keep it simple. A hard ceiling with pass-level granularity is sufficient. Per-phase percentage allocations and 5-level degradation sequences add complexity without proven value (since the base estimates are unreliable anyway).

---

## C-09: ARCHIVE as a Classification

**Set A Position**: ARCHIVE is a distinct top-level classification alongside DELETE and KEEP. Scoped to docs and release artifacts. Requires a suggested destination path.

**Argument FOR Set A**:

ARCHIVE and DELETE have different semantics, different engineer workflows, and different risk profiles. When an engineer sees "DELETE: deploy-v1.0-notes.md," they delete the file. When they see "ARCHIVE: deploy-v1.0-notes.md -> docs/archive/v1.0/," they move the file to preserve institutional history. Conflating these under a single DELETE action with a qualifier obscures this critical distinction.

The risk profile matters. A mistaken DELETE is destructive. A mistaken ARCHIVE is recoverable (the file still exists, just in a different location). Making ARCHIVE a top-level category forces the engineer to consciously choose between these different risk levels, rather than potentially overlooking a `:archive-first` qualifier on a long DELETE list.

Set A also requires a suggested destination path for each ARCHIVE recommendation. This is a practical detail that makes the audit actionable: "ARCHIVE: .dev/releases/current/v1.04/ -> .dev/releases/archive/v1.04/" tells the engineer exactly what to do. Set B's `DELETE:archive-first` qualifier does not specify where to archive.

**Addressing Set B's Counter**: Set B argues that the primary action (what the engineer does) is "remove from this location," making ARCHIVE a DELETE variant. This is a valid modeling perspective, but it optimizes for data model elegance over human workflow clarity. In practice, archiving is a multi-step workflow (create destination, copy file, verify copy, remove original) that is distinct from deletion (remove file).

**Addressing Known Flaws**: F-A-12 (archive destination guidance is underspecified) is valid. The mitigation: define a small set of canonical archive destinations with selection rules. For docs: `docs/archive/`. For release artifacts: `.dev/releases/archive/`. For other temporal artifacts: `archive/` at the same directory level. Provide these as defaults that can be overridden in the config.

**Honest Concession**: This is genuinely a modeling preference rather than a correctness issue. Both approaches capture the same information. If the merger adopts Set B's two-tier system, the critical requirement from Set A's perspective is that the report formatting renders ARCHIVE items in a visually distinct section with destination paths, regardless of the underlying data model.

---

## C-10: Cross-Reference / Cross-Boundary Detection

**Set A Position**: Cross-cutting analysis is handled within the existing Pass 3 with enhancements (broken reference checklists, large directory assessment blocks). No new architectural component.

**Argument FOR Set A**:

Set A's approach enhances what already works. Pass 3 currently produces duplication matrices that are praised as the strongest part of the audit output. Set A proposes to add broken-reference checklists and directory-level assessments to this existing pass, extending its capability without introducing a new architectural component.

Set B proposes building a directed dependency graph with files as nodes and import/export as edges. The Flaw Hunter (F-B-03) rated this as CRITICAL feasibility risk: "Dependency graph construction via LLM is infeasible for most languages." For Python (dynamic imports, `__import__`, importlib), JavaScript (dynamic `import()`, barrel re-exports, webpack aliases), and CSS (no import graph), an LLM reading 50-100 lines per file cannot build reliable import graphs. The flagship feature of Set B's architecture may not work.

Set A's broken-reference checklist is a more modest but more reliable capability. Checking whether a referenced file path exists is a binary, verifiable operation. Building a full dependency graph requires inferring import relationships from partial file reads -- a fundamentally harder problem with higher error rates.

**Addressing Set B's Counter**: Set B argues that cross-boundary dead code detection requires a dependency graph. This is true in theory, but the Flaw Hunter's analysis shows that LLM-based dependency graph construction has high false-negative and false-positive rates. A dependency graph that is 60% accurate is worse than no dependency graph because it creates false confidence. Set A's approach of surfacing broken references (a 100% verifiable check) is more honest and more useful than an unreliable dependency graph.

**Addressing Known Flaws**: Set A does not address the cross-boundary dead code detection use case at all. The mitigation that preserves Set A's intent: add a lightweight "reference count" to file profiles (how many other files reference this file, based on grep), without building a full dependency graph. A file with zero inbound references is a candidate for investigation, regardless of whether you have a complete dependency graph.

**Honest Concession**: Cross-boundary dead code detection is a real capability gap that Set A does not address. Set B's vision is the right long-term goal. However, the feasibility risk of LLM-based dependency graph construction is high enough that it should be implemented cautiously (perhaps using static analysis tools like `madge` via Bash, as the Flaw Hunter suggests) rather than as a core architectural dependency.

---

## C-11: Spot-Check Validation

**Set A Position**: No explicit spot-check validation pass. Verification is limited to acceptance criteria checking that sections exist and have correct format.

**Argument FOR Set A**:

Set A's acceptance criteria approach is simpler and more honest. It tests structural properties: do the required sections exist? Are they in the correct format? Do they contain the expected data types? These properties are verifiable, deterministic, and do not depend on LLM consistency.

Set B's 10% spot-check by an audit-validator agent is presented as a quality guarantee, but the Flaw Hunter (F-B-05) identified a fundamental problem: this is LLM-on-LLM validation. The validator (Sonnet) can make the same systematic errors as the scanner (Haiku). Two models can consistently agree on wrong answers. An "agreement rate" of 92% provides false confidence -- it measures model consistency, not ground truth correctness.

Set A's approach avoids this false confidence by not claiming runtime validation at all. Instead, it relies on acceptance criteria that can be verified by an engineer and golden-fixture tests that check the system against known-correct inputs. This is more honest than a spot-check mechanism that cannot distinguish between consistent correctness and consistent error.

**Addressing Set B's Counter**: Set B argues that the v1 spec already promised 10% spot-check validation and it was never implemented. This is true, but the fact that it was promised and never implemented may reflect the difficulty of doing meaningful runtime validation, not mere implementation neglect. The question is whether the spot-check provides enough value to justify its cost (the validator agent, additional token budget, and the false confidence risk).

**Addressing Known Flaws**: The absence of any runtime validation is a genuine gap. The mitigation that preserves Set A's intent: add a lightweight structural validation step (not a full re-analysis) that checks whether required evidence fields are populated, whether classification distributions are plausible (not 99% KEEP), and whether file paths in the report actually exist. This is cheaper and more reliable than LLM-on-LLM spot-checking.

**Honest Concession**: Some form of runtime quality signal is better than none. Set B's spot-check concept has merit if it is labeled honestly as a "consistency check" (not an "accuracy check") and supplemented with ground-truth calibration anchors. Set A's position of "no spot-check at all" is too conservative.

---

## C-12: Phase 0 / Pre-Audit Profiling

**Set A Position**: No pre-audit profiling phase. The audit begins directly with Pass 1 (Surface Scan).

**Argument FOR Set A**:

Set A's direct-to-scanning approach reflects how cleanup audits actually work: you start examining the repo, and your understanding deepens as you go. Pass 1 (surface scan) is itself a form of profiling -- it produces repo-scale metrics and top-level triage. Adding a separate Phase 0 before Pass 1 means doing two rounds of initial analysis, with the first being a lightweight summary that the second (Pass 1) will largely repeat.

For most repos, the overhead of a dedicated profiling phase is not justified. A repo maintainer who knows their repo does not need a Haiku model to tell them it is a Next.js project with Docker. They need the audit to start finding issues. Phase 0 adds 30-60 seconds and 5% of the token budget to produce information that is often already known.

Phase 0 is justified only if you commit to the full Set B architecture (dynamic batch decomposition, risk-weighted scanning, tiered coverage contracts). If you are following Set A's additive approach, Phase 0 is unnecessary overhead.

**Addressing Set B's Counter**: Set B argues that Phase 0 is a structural prerequisite for batch decomposition and coverage tracking. This is true within Set B's architecture but not within Set A's. Set A does not propose batch decomposition or tiered coverage contracts, so Phase 0 has no downstream consumers in Set A's design.

**Addressing Known Flaws**: The lack of domain detection means Set A cannot provide file-type-specific analysis. The mitigation that preserves Set A's intent: add lightweight domain detection within Pass 1 itself (detect framework from package.json, detect languages from file extensions) rather than as a separate preceding phase. This gives the same information without the architectural overhead of a new phase.

**Honest Concession**: If the merged spec adopts any of Set B's infrastructure features (batch decomposition, tiered coverage, risk-weighted scanning), then Phase 0 becomes necessary. Set A's position is defensible only within Set A's own simpler architecture. This is a conflict where the right answer depends on which architectural vision is adopted for the overall merger.

---

## C-13: Recommendation Category Count

**Set A Position**: 5 output buckets: DELETE, KEEP, ARCHIVE, FLAG, BROKEN_REFERENCES (plus REMAINING/NOT_YET_AUDITED).

**Argument FOR Set A**:

Set A's named output buckets directly correspond to engineer actions. Each bucket answers a specific question: What should I delete? What should I archive? What requires code changes before cleanup? What references are broken? What was not examined? An engineer can scan the table of contents and jump directly to the section relevant to their current task.

The 13+ secondary qualifiers in Set B's system require engineers to learn a taxonomy before they can use the report. An engineer who sees `MODIFY:consolidate-with:docker-compose.prod.yml` needs to understand the two-tier system, know what MODIFY means, and parse the qualifier syntax. An engineer who sees a "CONSOLIDATE" section heading understands immediately.

Set A's approach also maps cleanly to common project management workflows. A team can create Jira tickets directly from Set A's sections: "Address all FLAG items," "Process ARCHIVE candidates," "Fix BROKEN_REFERENCES." Set B's qualifier-based system requires filtering and grouping before tickets can be created.

**Addressing Set B's Counter**: Set B argues that flat categories proliferate and create ambiguity. This is partially true -- but the ambiguity is in edge cases (is a file that should be consolidated a DELETE or a KEEP?), not in the common cases that make up 80%+ of findings. The common cases (delete unused files, keep essential files, archive old releases) map cleanly to flat categories.

**Addressing Known Flaws**: The lack of extensibility is a valid concern. The mitigation: define the flat categories as a stable core with an explicit extension mechanism. New categories can be added as needed without restructuring the existing ones.

**Honest Concession**: Set B's composable system is objectively more elegant and handles edge cases better. If the report needs to serve both human readers and programmatic consumers, the composable system wins. Set A's approach is better for human-only consumption where simplicity and scannability matter most. The best merger is likely Set B's data model with Set A's report formatting.

---

## C-14: Batch Decomposition -- Static vs Dynamic

**Set A Position**: No explicit batch decomposition strategy.

**Argument FOR Set A**:

Set A's implicit approach to file assignment relies on the existing scanner behavior, which has been running in production. The scanners currently process files and produce output without explicit batch manifests. The output quality could be improved, but the mechanism works.

Adding dynamic batch decomposition introduces significant complexity: a profiling phase to generate the manifest, risk scoring per directory, depth calibration per batch, logged assignments, and batch-level checkpointing. Each of these is a non-trivial engineering task with its own failure modes. The batch manifest becomes a single point of failure -- if it is generated incorrectly, every subsequent scanning decision is wrong.

The 44x profiling gap that motivates Set B's batch decomposition is, as noted in F-B-01, a misleading comparison between human-guided multi-session work and a single automated run. The gap is real but its magnitude is overstated. Improving scanner prompts to produce more per-file profiles does not require a batch decomposition system -- it requires better prompts that emphasize file-level analysis over aggregate summaries.

**Addressing Set B's Counter**: Set B argues that without batch decomposition, scanners have no documented file assignments, depth calibration, or coverage guarantees. The first two can be addressed through improved scanner prompts (not architectural changes). Coverage guarantees do require some form of file tracking, but this can be achieved with a simple post-scan coverage check (compare files examined against `git ls-files` output) rather than a pre-scan batch manifest.

**Addressing Known Flaws**: The absence of any file assignment strategy is a legitimate gap. The mitigation: add a `--batch-size` parameter (already referenced in the COMMANDS.md) that controls how many files each scanner processes, and a post-scan coverage check that reports examined vs total files. This is simpler than a full batch manifest system.

**Honest Concession**: Set A is genuinely weaker here. Some form of explicit file assignment is needed to ensure coverage. The question is whether the solution should be a pre-scan manifest (Set B) or improved scanner prompts with a post-scan coverage check (Set A's philosophy). For large repos, Set B's manifest approach is more reliable.

---

## C-15: Spec-Implementation Gap Recognition

**Set A Position**: The gap analysis compares old manual prompts to new automated output. It does not examine the current v1 spec for unimplemented promises.

**Argument FOR Set A**:

Set A's framing is user-outcome-focused: "the old approach found these things; the new approach misses them; let's add the missing capabilities." This is a valid and practical problem framing. The engineer running the audit cares about output quality, not about whether the spec document matches the implementation.

The spec-implementation gap is an internal consistency concern, not a user-facing quality concern. If the v1 spec promises 5 categories but only 3 are implemented, and the 3 that are implemented produce useful output, the user does not suffer from the spec gap -- they suffer from the output gaps that Set A identifies (no docs audit, no known-issues suppression, weak broken-reference reporting).

Set A's focus on observable output deltas is methodologically sound. It compares concrete artifacts (old prompt outputs vs new audit outputs) rather than abstract documents (spec promises vs implementation). The output delta is the ground truth of what users experience.

**Addressing Set B's Counter**: Set B argues that adding features to a spec with unimplemented promises widens the gap. This is a valid meta-concern, but the correct mitigation is not "implement all existing promises first" -- it is "ensure new features are actually implemented." Set A's golden-fixture testing approach and acceptance criteria (A1-A5) are designed to prevent implementation gaps for the new features.

**Addressing Known Flaws**: F-A-02 (no spec-implementation gap acknowledgment) is the second most important flaw in Set A. The mitigation: add a section to Set A's PRD that audits the v1 spec for unimplemented promises and explicitly classifies each as "implement now," "defer," or "remove from spec." This preserves Set A's user-centric framing while acknowledging the meta-concern.

**Honest Concession**: Set B's discovery of the spec-implementation gap is genuinely important and Set A should have identified it. The risk of repeating the v1 pattern (promising features that never get implemented) is real. However, the mitigation is not to halt all user-facing work -- it is to pair each new feature with testable acceptance criteria and golden fixtures, which Set A already proposes.

---

## C-16: Coverage Tracking and Guarantee

**Set A Position**: Mentions "REMAINING / NOT_YET_AUDITED coverage accounting" as a schema requirement but provides no coverage thresholds or per-tier tracking.

**Argument FOR Set A**:

Set A's coverage accounting concept -- transparently showing what was and was not examined -- provides the essential information without the complexity of tiered contracts. The most important coverage signal is binary: was this file examined or not? The REMAINING/NOT_YET_AUDITED sections give engineers this information directly.

Setting numeric coverage thresholds (100%/95%/80%/60%) before having empirical data on what is achievable is premature. The Flaw Hunter (F-B-07) identified that Set B's coverage targets conflict with budget constraints: achieving 95% coverage on Tier 2 files with full evidence profiles may be infeasible at the default 300K token budget. Setting targets that are never met creates perpetual WARN/FAIL status, which teaches users to ignore warnings.

Set A's approach lets the audit produce what it can within budget and transparently reports the coverage gap. Users can then decide whether to increase the budget or accept partial coverage. This is more honest than setting ambitious targets that the system cannot meet.

**Addressing Set B's Counter**: Set B argues that without thresholds, "coverage tracking" is meaningless. This conflates "tracking" with "guaranteeing." Tracking coverage (what was examined, what was not) is useful even without guarantees. A report that says "387 files were not examined, primarily in docs/ and assets/" is actionable without a 60% threshold.

**Addressing Known Flaws**: The lack of any targets makes coverage unenforceable. The mitigation: add a single overall coverage metric (percentage of files examined) with a user-configurable threshold that defaults to "warn below 50%." This is simpler than 4-tier contracts and more likely to be achievable.

**Honest Concession**: Some form of coverage target is useful for setting expectations. Set B's tiered approach is more nuanced. The merger should adopt coverage thresholds, but they should be empirically validated against real repos before being published as defaults.

---

## C-17: Output Format -- Markdown vs JSON

**Set A Position**: Pass summaries as Markdown files.

**Argument FOR Set A**:

The primary consumer of audit output is a human engineer reading a report. Markdown is the format humans read. JSON is the format machines parse. Set A optimizes for the primary consumer.

In the SuperClaude ecosystem, audit reports are read as markdown files in editors and terminals. Engineers scan headings, read checklists, and review recommendations. They do not pipe audit output through `jq` to extract findings. The audit report is a communication artifact, not a data pipeline artifact.

Set B's JSON intermediate outputs are useful only if there are downstream consumers that parse them programmatically. In Set B's architecture, Phase 3 consumes Phase 1-2 JSON outputs to build a dependency graph. But in Set A's simpler architecture, there are no inter-phase programmatic consumers -- each pass produces a standalone summary.

**Addressing Set B's Counter**: Set B argues that JSON enables schema validation and structured cross-phase data flow. This is true and valuable if the architecture has inter-phase data dependencies. The best merger preserves JSON for inter-phase data and markdown for human-readable summaries.

**Addressing Known Flaws**: The lack of schema validation for pass outputs is a genuine gap. The mitigation: define a minimal set of structured data (file lists, classification counts, coverage statistics) that each pass must emit as a JSON appendix to the markdown summary. This gives schema validation for essential data while preserving markdown readability.

**Honest Concession**: JSON intermediate outputs are strictly superior for any architecture with inter-phase data flow. Set A's markdown-only approach is viable only in a simpler architecture without structured cross-phase communication. This conflict is largely determined by the architectural vision chosen for the merger.

---

## C-18: Quality Gate on Spot-Check Failure

**Set A Position**: No spot-check mechanism defined. If a quality gate fails, the remediation is undefined.

**Argument FOR Set A**:

Set A's quality gate is structural: acceptance criteria that test section presence, format correctness, and data completeness. These are deterministic and reliable. Set B's warning banner on <85% spot-check agreement adds a quality signal, but as discussed in C-11, this signal measures model consistency, not correctness.

A warning banner that says "spot-check agreement: 78%" provides ambiguous information. Does this mean the audit is unreliable? Or does it mean the validator applied different judgment criteria? Without ground-truth anchors, the banner is noise, not signal.

**Addressing Set B's Counter**: Set B's warning banner is a low-cost addition that provides some information. The mitigation: adopt the warning banner but label it "consistency rate" (not "agreement rate") and include a note explaining that this measures model-to-model consistency, not ground-truth accuracy.

**Addressing Known Flaws**: No specific flaw -- Set A simply does not address this topic.

**Honest Concession**: Some quality signal is better than none. Set B's approach is better here, with the labeling caveat above. Set A's silence on the topic is a gap, not a position.

---

## C-19: .env Handling Approach

**Set A Position**: `.env*` handling is a P2 enhancement -- a key-presence matrix comparing keys across `.env*` templates.

**Argument FOR Set A**:

Set A's .env key matrix is a complementary capability to Set B's credential scanning, not a replacement. The key matrix answers a different question: "are all environment variables consistently defined across development, staging, and production templates?" This catches configuration drift -- a common source of deployment failures -- without requiring content inspection.

The key matrix is also cheap and safe. It reads only key names (not values), making it appropriate for a read-only audit that must never expose credentials. It produces a compact, scannable output (a matrix table) that immediately shows which keys exist in which files.

Set B focuses on credential detection (real vs template values), which is a security concern. Set A focuses on key consistency, which is a configuration management concern. Both are valid.

**Addressing Set B's Counter**: Set B correctly identifies that the `.env.production` credential misidentification is a correctness failure. This should be fixed with higher priority than the key matrix. The mitigation: adopt Set B's credential scanning as a Phase 1 fix AND preserve Set A's key matrix as a complementary P2 enhancement. These are not competing features.

**Addressing Known Flaws**: F-A-09 (scope creep into configuration management) is partially valid. The mitigation: make the .env key matrix an opt-in feature activated by `--env-matrix` flag, clearly scoped as "configuration consistency check, not security audit."

**Honest Concession**: Set B's credential scanning fix is more urgent and more important. Set A's P2 prioritization is too low for the credential issue (which Set A did not identify at all). The merger should adopt Set B's credential scanning at high priority and Set A's key matrix as a complementary lower-priority feature.

---

## C-20: Progressive Depth Across Passes

**Set A Position**: Not explicitly addressed.

**Argument FOR Set A**:

Set A's implicit approach -- let each pass's rules determine read depth based on what the pass needs -- is conceptually sound even if not explicitly documented. Pass 1 (surface scan) naturally reads less per file than Pass 2 (structural audit), which reads less than Pass 3 (cross-cutting synthesis). The progressive depth emerges from the pass-specific rules, not from an explicit depth escalation mechanism.

Adding a formal two-level signal-triggered depth system introduces a new decision layer that must be maintained separately from the pass rules. If the depth trigger says "read full file on TODO/FIXME" but the pass rules say "focus on structural properties," there is a potential conflict. Keeping depth decisions within the pass rules avoids this.

**Addressing Set B's Counter**: Set B argues that without explicit depth rules, scanners default to shallow reads. This is a valid concern, but the fix is to improve pass-specific rules (e.g., "for files flagged as high-risk, read the full file") rather than to add a cross-cutting depth escalation mechanism.

**Addressing Known Flaws**: The lack of any depth specification is a gap. The mitigation: add explicit depth guidance to each pass's rules file. "Pass 1: read first 30 lines + last 10 lines. Pass 2: read up to 100 lines for files requiring profiles. Pass 3: read full file for cross-reference analysis."

**Honest Concession**: Set B's signal-triggered depth is a well-designed mechanism. The two-level approach (50-line default, full-file on trigger) is practical and addresses a real problem. This is a case where Set A's silence is a gap, not a principled position.

---

## C-21: Checkpointing Granularity

**Set A Position**: `progress.json` updated at pass level with pass status fields.

**Argument FOR Set A**:

Pass-level checkpointing is simpler and matches the user's mental model. An engineer checking on a running audit thinks "is Pass 2 done?" not "has batch 7 of 12 in Phase 2 completed?" Pass-level status (not_started, in_progress, complete) is immediately understandable.

Batch-level checkpointing adds complexity: the progress file must track batch counts, completion status per batch, and file assignments per batch. This requires the batch manifest system (Set B's Phase 0 output), creating another dependency on Phase 0 infrastructure.

For most repos and most audit runs, pass-level checkpointing is sufficient. A typical audit completes in 15-45 minutes. If interrupted, re-running from the beginning of a pass loses at most one pass's worth of work. Batch-level resume saves time only for very large repos with very long passes.

**Addressing Set B's Counter**: Set B argues that for large repos, pass-level checkpointing means losing all progress on session interruption. This is valid for repos where a single pass takes 20+ minutes. The mitigation: add an optional batch-level checkpoint for repos above a configurable file-count threshold (e.g., 5000 files), rather than mandating it for all repos.

**Addressing Known Flaws**: No specific flaw identified for Set A's pass-level approach beyond its limited granularity.

**Honest Concession**: Batch-level checkpointing with `--resume` is a strictly better user experience for large repos. The implementation cost is moderate but the user value is real. This is a case where Set B's approach is objectively superior and should be adopted.

---

## C-22: Claim Spot-Check Scope (Docs)

**Set A Position**: Claim spot-checks verify 3-5 structural claims per doc across sampled docs.

**Argument FOR Set A**:

Set A's broader scope (3-5 claims across all sampled docs) provides better coverage than Set B's narrower scope (3 claims, only API-reference and setup-guide categories). The most damaging stale claims are not limited to API docs -- they appear in architecture docs ("the system uses port 8080"), deployment docs ("run deploy-prod.sh"), and onboarding docs ("clone from this URL"). Restricting claim checks to API-reference and setup-guide misses these high-impact doc types.

The incremental cost of checking 5 claims instead of 3 per doc is small relative to the total docs audit budget. The incremental value is significant because stale claims in non-API docs cause real onboarding failures.

Set A also specifies the claim types explicitly: referenced file exists, referenced script name exists, referenced port matches spec, referenced docker-compose file exists. This enumeration provides clear implementation guidance.

**Addressing Set B's Counter**: Set B's narrower scope is a cost-control measure. The mitigation that preserves Set A's broader scope: check 3-5 claims across all doc categories, but allow the sampling mechanism to reduce the number of docs examined. This gives broader claim-type coverage with bounded total cost.

**Addressing Known Flaws**: F-A-05 (claim spot-checks vaguely defined) is valid. The mitigation: define explicit pass/fail criteria for each claim type. "Referenced file exists" = check `fs.existsSync()`. "Referenced port matches spec" = compare against ports in docker-compose.yml. "Referenced script name exists" = check if script file exists in repo.

**Honest Concession**: This is a minor conflict where both approaches are defensible. The cost difference between 3 and 5 claims per doc is small enough that the decision should be based on overall docs audit budget, not on the per-doc claim count.

---

## Overall Case for Set A

The conflict register rates Set B's evidence as stronger on 18 of 22 conflicts. As Set A's advocate, I acknowledge this imbalance honestly. Set B's multi-agent analysis process produced deeper architectural insights, quantified more gaps, and identified critical issues (credential scanning, spec-implementation gap, dependency ordering) that Set A missed entirely.

However, the evidence-strength ranking does not map directly to implementation risk. Set A's core philosophy -- incremental enhancement over architectural overhaul -- carries significant practical advantages that the evidence ranking does not capture:

**1. Time-to-value.** Set A's P0 items (Pass 4 docs audit, known-issues registry) can be shipped in a single sprint. Set B's Phase 0 (enforce existing spec) must be completed before any user-visible improvement ships. For a team that started this project because "docs are never audited," Set A delivers the headline feature first.

**2. Risk of the rewrite trap.** Set B proposes restructuring the entire execution flow into 5 phases with new pre-audit and post-audit phases, specialized agents, dynamic batch decomposition, tiered evidence requirements, budget enforcement, and anti-lazy mechanisms. This is not an improvement to the existing system -- it is a new system. Rewrites frequently fail, go over budget, or take 3x longer than estimated. The Flaw Hunter (F-B-14) noted that Set B's effort estimates are "unrealistically low" -- the realistic effort is 80-120+ hours, not the claimed 30.

**3. Feasibility concerns.** Set B's flagship features have critical feasibility risks that Set A's simpler features do not. LLM-based dependency graph construction (F-B-03) is infeasible for most languages. LLM-on-LLM spot-check validation (F-B-05) measures consistency, not correctness. Token cost estimates (F-B-02) are still underestimated. These are not minor concerns -- they affect Set B's most distinctive contributions.

**4. The known-issues registry.** Set A's strongest individual contribution (C-04) solves the cross-run persistence problem that Set B does not address. This is a real-world use case (weekly audits for long-lived repos) that Set A identified from operational experience with the legacy prompt set.

**5. User-facing specification.** Set A provides target users, use cases, non-goals, and actionable output specifications (Pass 4 sections, broken-reference format, claim spot-check types) that Set B's PRD omits. These are not trivial additions -- they ground the specification in user needs and prevent scope creep.

The strongest merger strategy is not "adopt Set B's architecture wholesale" -- it is to adopt Set B's insights (spec-implementation gap, credential scanning, budget awareness, dependency ordering) within Set A's incremental philosophy. Specifically:

- Ship Pass 4 docs audit and known-issues registry first (Set A's P0)
- Add Set B's credential scanning and gitignore consistency as correctness fixes alongside P0
- Adopt Set B's budget flag and coverage reporting as guardrails, not as architectural foundations
- Defer Set B's more ambitious architectural changes (dependency graphs, specialized agents, batch decomposition) to a subsequent release after empirical validation
- Preserve Set A's user-facing elements (target users, non-goals, output format specifications) in the merged PRD

This approach delivers the highest-confidence improvements first, avoids the rewrite trap, and creates a foundation for Set B's architectural improvements to be added incrementally as their feasibility is validated.

---

*Set A Advocacy document generated 2026-02-20*
*Advocate: Set A Advocate Agent*
*Conflicts addressed: 22/22*
