# Wave 1 Flaw Analysis -- sc:cleanup-audit vNext

**Date**: 2026-02-20
**Analyst**: Flaw Hunter (Security Engineer agent)
**Input**: Set A (2 docs, single-agent) + Set B (4 docs, multi-agent)
**Method**: Adversarial analysis across 8 flaw categories

---

## Set A Flaws

**Source documents**:
- A1: `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
- A2: `SC_CLEANUP_AUDIT_VNEXT_PRD.md`

### CRITICAL

#### F-A-01: No Token Budget Model or Cost Ceiling
- **Category**: Unrealistic Assumptions
- **Description**: Set A's PRD defines Pass 4, known-issues registry, broken-reference sweeps, claim spot-checks, and coverage accounting -- but provides ZERO token cost estimates for any of them. The "Cost controls" section mentions sampling and capping output but never quantifies the actual token budget required. For a ~6,000-file repo, Pass 4 alone (reading docs, extracting links, verifying claims) could easily consume 50-100K+ tokens with no mechanism to bound it.
- **Source**: A2, Section 5.2 ("Cost controls"), Section 9 ("Adversarial review")
- **Severity**: CRITICAL
- **Impact**: Implementation will either blow budgets or silently produce shallow results. Engineers cannot plan resource allocation without cost estimates.
- **Proposed Mitigation**: Add per-phase token budget allocations with hard ceilings and graceful degradation strategy.

#### F-A-02: No Spec-Implementation Gap Acknowledgment
- **Category**: Specification Gaps
- **Description**: Set A never examines whether the CURRENT sc:cleanup-audit spec already promises features that went unimplemented. If the existing spec already defines 5 categories, coverage tracking, and checkpointing (as Set B discovered), then adding MORE features to the spec without addressing WHY the existing ones failed is a recipe for the same outcome.
- **Source**: A1 (entire document), A2 (entire document)
- **Severity**: CRITICAL
- **Impact**: The PRD may repeat the exact failure pattern of v1: spec features that sound good but never get implemented because the underlying architecture does not enforce them.
- **Proposed Mitigation**: Add a "Phase 0: Enforce Existing Spec" section that audits current implementation against current spec before proposing additions.

#### F-A-03: Pass 4 Depends on Undefined Infrastructure
- **Category**: Architectural Risks
- **Description**: Pass 4 "Docs Quality" requires structured outputs from Pass 1-3 (broken references, overlap candidates, temporal artifact lists) but the PRD does not define what structured data Pass 1-3 must emit FOR Pass 4 to consume. The existing passes produce summary markdown -- Pass 4 cannot programmatically consume markdown summaries.
- **Source**: A2, Section 4.3 ("Pass 4 outputs"), Section 5.1 ("Where changes live")
- **Severity**: CRITICAL
- **Impact**: Pass 4 will operate in isolation, re-scanning the repo instead of building on prior pass data, wasting tokens and producing inconsistent results.
- **Proposed Mitigation**: Define a structured inter-pass data schema (JSON) that all passes emit and consume.

### HIGH

#### F-A-04: Known-Issues Registry Has No Versioning or Lifecycle
- **Category**: Missing Edge Cases
- **Description**: The known-issues registry (Section 4.4) defines `status: open|closed|monitor` but does not address: (a) who updates the registry after an audit run, (b) what happens when the registry grows to 500+ entries across many runs, (c) how stale entries (files deleted, issues resolved) are pruned, (d) merge conflicts when multiple audits run in parallel.
- **Source**: A2, Section 4.4
- **Severity**: HIGH
- **Impact**: The registry becomes a maintenance burden that accumulates noise over time, eventually suppressing real findings.
- **Proposed Mitigation**: Add TTL per entry, automatic staleness detection (file no longer exists), and max-entry limits with eviction policy.

#### F-A-05: "Claim Spot-Checks" Verification is Vaguely Defined
- **Category**: Specification Gaps
- **Description**: Section 4.3 item 4 says "verify 3-5 structural claims per doc" with examples like "referenced file exists" and "referenced port matches authoritative spec (if present)." But: (a) what constitutes an "authoritative spec"? (b) how does the system locate it? (c) what is the tolerance for false claims (1 false = OUTDATED? 3 false = DELETE?)? (d) how does the system handle claims that are neither verifiable nor falsifiable?
- **Source**: A2, Section 4.3 item 4 ("CLAIM_SPOT_CHECKS")
- **Severity**: HIGH
- **Impact**: Different subagent runs will apply different verification standards, producing inconsistent results.
- **Proposed Mitigation**: Define explicit claim types with binary pass/fail criteria and a minimum threshold for document classification.

#### F-A-06: No Error Recovery or Partial Failure Handling
- **Category**: Missing Error Handling
- **Description**: The PRD describes 4 passes as a sequential pipeline but never addresses: what happens if Pass 2 fails partway through? Can Pass 3 run on partial Pass 2 data? What if the link extractor crashes on malformed markdown? What if the known-issues JSON is corrupted?
- **Source**: A2, Sections 4.1-4.6 (all pass descriptions)
- **Severity**: HIGH
- **Impact**: Any single failure cascades to total audit failure with no recovery path.
- **Proposed Mitigation**: Define per-pass quality gates, partial-success handling, and explicit fallback behaviors for each failure mode.

#### F-A-07: Adversarial Review is Shallow and Self-Congratulatory
- **Category**: Unrealistic Assumptions
- **Description**: Section 9 "Adversarial review" lists three risks, all with tidy mitigations. It misses: (a) monorepo scaling (50K+ files), (b) binary-heavy repos where docs are a tiny fraction, (c) repos with no tests, (d) repos with 100+ .env files across microservices, (e) non-English documentation, (f) dynamic link generation in docs (template variables in URLs).
- **Source**: A2, Section 9
- **Severity**: HIGH
- **Impact**: The spec will fail on edge-case repositories and the team will be surprised because the adversarial review gave false confidence.
- **Proposed Mitigation**: Expand risk section with realistic edge cases including monorepos, polyglot repos, and non-standard directory structures.

#### F-A-08: "Golden-Output Fixtures" Testing Strategy is Brittle
- **Category**: Feasibility Issues
- **Description**: Section 7 proposes a "small synthetic repo" for verification. LLM-based tools produce non-deterministic output. Golden-output testing against LLM output is inherently flaky -- two runs on the same input can produce different section orderings, different wording, and different sampling choices.
- **Source**: A2, Section 7 ("Verification approach")
- **Severity**: HIGH
- **Impact**: Tests will be perpetually flaky, eroding confidence in the test suite.
- **Proposed Mitigation**: Test for structural properties (section headings present, checklist format correct, required fields populated) rather than golden output matching.

### MEDIUM

#### F-A-09: ".env Key Matrix" is Scope Creep
- **Category**: Scope Creep
- **Description**: P2 proposal for ".env key matrix comparison" goes beyond cleanup audit into configuration management territory. This is better handled by dedicated tools like `dotenv-linter` or `env-verify`.
- **Source**: A1, Section "P2: .env key matrix comparison"
- **Severity**: MEDIUM
- **Impact**: Adds implementation cost and token cost for a feature that overlaps with existing tooling.
- **Proposed Mitigation**: Defer to external tooling or make explicitly optional with a dedicated flag.

#### F-A-10: Pass 4 Sampling Policy Not Defined Concretely
- **Category**: Specification Gaps
- **Description**: The PRD says "sample 5-10 representative docs" for large trees but never defines: what makes a doc "representative"? Random? Stratified by directory? Most recently modified? Largest? This is a critical decision that affects coverage quality.
- **Source**: A2, Section 4.3 item 1 ("Sampling policy used")
- **Severity**: MEDIUM
- **Impact**: Different implementations will sample differently, producing incomparable results across runs.
- **Proposed Mitigation**: Define a concrete sampling strategy (e.g., stratified by directory depth + most recently modified + largest files).

#### F-A-11: No Handling of Empty or Trivial Repos
- **Category**: Missing Edge Cases
- **Description**: The spec assumes a repo large enough to warrant multi-pass analysis. What happens with a 10-file repo? A repo with zero documentation? A repo with only binary assets?
- **Source**: A2 (all sections assume a GFxAI-scale repo)
- **Severity**: MEDIUM
- **Impact**: The tool fails or produces useless output on small/unusual repositories.
- **Proposed Mitigation**: Add minimum-complexity thresholds; for trivial repos, collapse all passes into a single lightweight scan.

#### F-A-12: ARCHIVE Destination Guidance is Underspecified
- **Category**: Specification Gaps
- **Description**: Section 4.3 item 5 says "if ARCHIVE: suggested destination" but does not define the rules for choosing destinations. Is it always `docs/archive/`? Is it relative to the file's current location? What about non-docs files?
- **Source**: A2, Section 4.3 item 5
- **Severity**: MEDIUM
- **Impact**: Inconsistent archival suggestions across runs and across different parts of the repo.
- **Proposed Mitigation**: Define a small set of canonical archive destinations (e.g., `docs/archive/`, `.dev/archive/`) with rules for selection.

### LOW

#### F-A-13: Expert Panel Critique is Simulated, Not Real
- **Category**: Unrealistic Assumptions
- **Description**: Section 8 "simulates" Karl Wiegers, Martin Fowler, and Lisa Crispin. These are fictional assessments presented as authoritative review. The recommendations are generic ("add default thresholds", "ensure testability") and do not reflect deep domain analysis.
- **Source**: A2, Section 8
- **Severity**: LOW
- **Impact**: Creates false confidence that the spec has been expertly reviewed when it has only been self-assessed.
- **Proposed Mitigation**: Label as "self-assessment using named frameworks" rather than "expert panel critique."

#### F-A-14: Implementation Backlog Lacks Effort Estimates
- **Category**: Specification Gaps
- **Description**: Section 10 lists 10 implementation items but provides no effort estimates, dependency ordering, or parallelization analysis.
- **Source**: A2, Section 10
- **Severity**: LOW
- **Impact**: Cannot plan sprints or allocate resources.
- **Proposed Mitigation**: Add rough t-shirt sizing (S/M/L) and dependency arrows.

---

## Set B Flaws

**Source documents**:
- B1: `cleanup-audit-improvement-findings.md`
- B2: `cleanup-audit-improvement-proposals.md`
- B3: `cleanup-audit-reflection-validation.md`
- B4: `cleanup-audit-v2-PRD.md`

### CRITICAL

#### F-B-01: "44x More Per-File Profiles" Metric is Misleading
- **Category**: Unrealistic Assumptions
- **Description**: The headline metric "527+ vs 12 per-file profiles" (B1, Executive Summary) compares a manual multi-session process (likely 10-20 hours of human-guided LLM work across multiple sessions) with a single automated run. The old approach used 27 batch reports across 4 passes with manual curation. Claiming the automated tool should match this without acknowledging the fundamentally different cost model is misleading and sets unrealistic expectations.
- **Source**: B1, Executive Summary table; B4, Section 1 ("44x fewer per-file profiles")
- **Severity**: CRITICAL
- **Impact**: Stakeholders expect v2 to produce 500+ profiles at comparable cost to v1's 12. The PRD targets "200-700+" (B4, Section 1) without acknowledging this requires 5-10x the token budget of v1.
- **Proposed Mitigation**: Normalize comparison by cost (profiles per 100K tokens) not raw count. Set targets relative to budget, not absolute counts.

#### F-B-02: Token Cost Estimates in PRD are Still Underestimated
- **Category**: Unrealistic Assumptions
- **Description**: B3 correctly identified that B2's estimates were 2-3x too low. B4 provides "revised" estimates (Section 6) but these are still likely underestimates. The "Standard" scenario claims 300K tokens for ~3,300 files at 18 minutes. At 300K tokens and 3,300 files, that is ~90 tokens per file on average. An 8-field profile with grep evidence for a single file realistically requires 300-800 tokens of output alone, plus input context. The math does not add up for Tier 1-2 files.
- **Source**: B4, Section 6 ("Realistic Token Estimates")
- **Severity**: CRITICAL
- **Impact**: Users will run `--budget 300000` expecting "Standard" coverage and get significantly less. The graceful degradation may cut Tier 3-4 entirely, producing a result labeled "Standard" that is actually "Minimal."
- **Proposed Mitigation**: Benchmark token costs empirically on a real repository before finalizing estimates. Add a margin of at least 50% to all estimates. The "Standard" tier likely requires 500-700K tokens.

#### F-B-03: Dependency Graph Construction is Infeasible for Most Languages
- **Category**: Feasibility Issues
- **Description**: Phase 3 (B4, Section 5) requires building a "directed dependency graph" from scanner output. This assumes scanners can reliably extract `external_dependencies` and `export_targets` from source code. For Python (dynamic imports, `__import__`, `importlib`), JavaScript (dynamic `import()`, `require()`, barrel re-exports, webpack aliases), and CSS (no import graph), this is extremely difficult. The scanner is a Haiku model reading 50-100 lines -- it cannot build reliable import graphs.
- **Source**: B4, Section 5 ("Phase 3: Cross-Reference Synthesis"), B2 Proposal 1
- **Severity**: CRITICAL
- **Impact**: The dependency graph will have high false-negative rates (missing real dependencies) and moderate false-positive rates (hallucinated dependencies), making cross-boundary dead code detection unreliable.
- **Proposed Mitigation**: Use static analysis tools (e.g., `madge` for JS, `pydeps` for Python) as a pre-step via Bash, not LLM-based extraction. If static tools are unavailable, fall back to grep-based import scanning and label results as "approximate."

#### F-B-04: Phase 0 Auto-Config Generation is a Correctness Risk
- **Category**: Architectural Risks
- **Description**: Phase 0 auto-generates `audit.config.yaml` by detecting frameworks and ports from project files (B4, Section 10). A Haiku model scanning `docker-compose.yml` and `package.json` to infer port mappings, framework conventions, and risk tiers introduces a new class of errors: misconfigured audits. If the auto-detection gets the framework wrong (e.g., identifies a Next.js app as plain React), all file-type-specific rules and risk tier assignments will be wrong.
- **Source**: B4, Section 10 ("Cold-Start & Configuration"), Section 5 ("Phase 0")
- **Severity**: CRITICAL
- **Impact**: Wrong config cascades to wrong tier assignments, wrong evidence requirements, and wrong classifications for every file in the repo.
- **Proposed Mitigation**: Auto-generated config must be written as a visible artifact and the report must prominently note which config values were auto-detected vs user-specified. Add a `--dry-run` step that shows the generated config before running the full audit.

#### F-B-05: 10% Spot-Check Validation is Statistically Insufficient for Confidence Claims
- **Category**: Unrealistic Assumptions
- **Description**: Phase 4 spot-checks 10% of classifications and declares the audit valid if agreement is >= 85% (B4, Section 9). For a 6,000-file repo, 10% = 600 files. But the validator is ALSO a Sonnet model -- it can make the same systematic errors as the original scanner. LLM-on-LLM validation measures consistency, not correctness. Two models can consistently agree on wrong answers.
- **Source**: B4, Section 5 ("Phase 4"), Section 9 (Quality Gates)
- **Severity**: CRITICAL
- **Impact**: Users will see "92% agreement rate" and trust the audit, when in reality the agreement measures model consistency, not ground truth accuracy.
- **Proposed Mitigation**: (a) Call it "consistency rate" not "agreement rate." (b) Add at least 3-5 manually verified ground-truth files as calibration anchors. (c) Acknowledge this limitation prominently in the report.

### HIGH

#### F-B-06: Scanner Output Schema is Overly Complex for Haiku
- **Category**: Feasibility Issues
- **Description**: Phase 1 uses Haiku scanners that must produce a complex JSON schema with `import_references`, `external_dependencies`, `export_targets`, `grep_command`, `grep_result_count`, `last_commit_days`, and `confidence` per file (B4, Section 3). Haiku is optimized for speed and cost, not complex structured output. JSON generation with nested objects and arrays is error-prone in smaller models.
- **Source**: B4, Section 3 ("Standardized Scanner Output Schema"), Section 5 ("Phase 1")
- **Severity**: HIGH
- **Impact**: High rate of malformed JSON output, triggering retries that consume budget. Schema compliance rate may be below 80% on first attempt.
- **Proposed Mitigation**: Simplify Phase 1 schema to essential fields only (path, classification, confidence, evidence_summary_text). Move complex structured fields to Phase 2 Sonnet analyzers.

#### F-B-07: Coverage Tier Targets are Not Empirically Validated
- **Category**: Unrealistic Assumptions
- **Description**: The PRD sets coverage targets of 100%/95%/80%/60% for Tiers 1-4 (B4, Section 4). These numbers appear to be chosen for aesthetic appeal rather than empirical validation. For a 6,000-file repo with 300K token budget, achieving 95% coverage on Tier 2 (~1,200 files) while also doing 8-field profiles requires approximately 360K-960K tokens for Tier 2 alone, which exceeds the entire budget.
- **Source**: B4, Section 4 ("File Risk Tiers"), Section 6 ("Token Budget System")
- **Severity**: HIGH
- **Impact**: The graceful degradation system will ALWAYS activate, and the coverage targets will NEVER be met at the default budget. Users will see perpetual WARN/FAIL status.
- **Proposed Mitigation**: Validate targets against actual token costs on a benchmark repository. Set targets relative to budget tier, not absolute.

#### F-B-08: "Evidence-Mandatory KEEP for Tier 1-2" Conflicts with Budget Constraints
- **Category**: Internal Contradictions
- **Description**: Section 4 requires "Full 3-field (references + recency + test coverage)" evidence for Tier 1 files and "2-field" for Tier 2. Section 6 allocates 35% of budget to Phase 2. For a repo with 1,200 Tier 2 files, the Phase 2 budget of ~105K tokens allows ~87 tokens per file -- insufficient for 3 grep operations + content read + structured JSON output per file.
- **Source**: B4, Section 4 vs Section 6
- **Severity**: HIGH
- **Impact**: The system promises evidence-mandatory KEEP but the budget cannot deliver it. Graceful degradation will silently reduce evidence depth, producing "KEEP:unverified" for files that the spec says MUST be verified.
- **Proposed Mitigation**: Either increase the default budget to 500K+ or relax Tier 2 evidence requirements to "1-field minimum" (import reference count only).

#### F-B-09: Graceful Degradation Priority Order is Debatable
- **Category**: Architectural Risks
- **Description**: Section 6 defines degradation as: skip Tier 4 first, then reduce Tier 3, then skip Phase 3 cross-references, then reduce Phase 2. But Phase 3 cross-references detect dead code across boundaries -- arguably more valuable than deep profiles on individual files. Skipping Phase 3 before reducing Phase 2 depth may be the wrong tradeoff.
- **Source**: B4, Section 6 ("Graceful Degradation")
- **Severity**: HIGH
- **Impact**: Under budget pressure, the most novel feature (cross-boundary detection) is cut before routine profiling depth.
- **Proposed Mitigation**: Make degradation order configurable or tie it to `--focus` flag. If `--focus infrastructure`, preserve cross-references and cut source code depth.

#### F-B-10: No Handling of Monorepos or Workspace-Based Repos
- **Category**: Missing Edge Cases
- **Description**: The entire PRD assumes a single-root repository. Monorepos (Nx, Turborepo, Lerna, Cargo workspaces) have multiple independent packages, each with their own dependency graphs, configs, and test suites. The Phase 0 profiler, batch decomposition, and dependency graph construction do not account for workspace boundaries.
- **Source**: B4 (all sections)
- **Severity**: HIGH
- **Impact**: For monorepos, the dependency graph will conflate cross-package dependencies with intra-package dependencies, producing false positives. Batch assignment may split a package across multiple scanners, losing context.
- **Proposed Mitigation**: Add monorepo detection in Phase 0. If workspace file detected (package.json workspaces, Cargo.toml workspace, nx.json), treat each workspace as a semi-independent unit for profiling and scanning.

#### F-B-11: INVESTIGATE Category May Become a Dumping Ground
- **Category**: Architectural Risks
- **Description**: The INVESTIGATE category (B4, Section 4) with 3 qualifiers (`cross-boundary`, `insufficient-evidence`, `dynamic-import`) is designed as an honest "we don't know" bucket. But without limits, budget pressure and lazy agents will classify many files as INVESTIGATE rather than making hard DELETE/KEEP calls. The anti-lazy enforcement checks for uniform confidence -- but uniform INVESTIGATE classifications with varying confidence values would pass validation.
- **Source**: B4, Section 4, Section 9
- **Severity**: HIGH
- **Impact**: Reports dominated by INVESTIGATE items are not actionable, defeating the audit's purpose.
- **Proposed Mitigation**: Add a hard cap on INVESTIGATE (e.g., max 15% of examined files). If exceeded, trigger re-analysis of INVESTIGATE items with elevated budget.

#### F-B-12: Findings Document Exaggerates Old System Capabilities
- **Category**: Unrealistic Assumptions
- **Description**: B1 claims the old system found "6 real credentials" in `.env.production` and caught "deploy-prod-simple.sh had port 8000 (should be 8102)." These findings were made by a human operating an LLM in an interactive session, not by an automated system. Attributing these findings to "the old approach" and expecting an automated system to replicate them conflates human judgment with automated capability.
- **Source**: B1, Findings 2, 6; all "old approach found X" claims
- **Severity**: HIGH
- **Impact**: Sets unrealistic expectations for what automated scanning can achieve. Some findings (like knowing the correct port should be 8102) require domain knowledge that no scanner possesses.
- **Proposed Mitigation**: Clearly distinguish "human-in-the-loop findings" from "automatable findings" in the gap analysis. Only target automatable findings in the PRD.

#### F-B-13: Reflection Report Identifies Issues but PRD Does Not Fully Resolve Them
- **Category**: Internal Contradictions
- **Description**: B3 identified 8 critical corrections needed (dependency ordering, co-design P3/P4, budget controls, cold-start, etc.) and scored the proposals 5.6/10. The PRD (B4) claims to address all 8 corrections, but: (a) the INVESTIGATE category orphan is partially addressed but not fully integrated into the two-tier system display, (b) the config bootstrapping generates defaults but the quality of those defaults is untested, (c) token estimates are described as "realistic" but remain unvalidated.
- **Source**: B3 Section "Critical Changes for PRD" vs B4 implementation
- **Severity**: HIGH
- **Impact**: The PRD inherits unresolved issues from the proposal phase while claiming they are resolved.
- **Proposed Mitigation**: Add an explicit traceability matrix: each B3 correction maps to a specific B4 section with a pass/partial/fail assessment.

### MEDIUM

#### F-B-14: Implementation Effort Estimates are Unrealistically Low
- **Category**: Unrealistic Assumptions
- **Description**: B4 Section 12 estimates "Phase 0: 4-6 hours" to implement 5-category classification, coverage tracking, checkpointing, evidence-gated classification, and spot-check validation. Each of these is a substantial feature involving prompt engineering, output parsing, JSON schema validation, and test coverage. A more realistic estimate is 15-25 hours for Phase 0 alone.
- **Source**: B4, Section 12 ("Implementation Roadmap")
- **Severity**: MEDIUM
- **Impact**: Project planning will be based on ~30 hours total when realistic effort is 80-120+ hours.
- **Proposed Mitigation**: Benchmark by implementing one feature (e.g., checkpointing) and extrapolating from actual effort.

#### F-B-15: "Never Cut Phase 0 and Phase 4" Creates Minimum Floor
- **Category**: Missing Edge Cases
- **Description**: Section 6 says Phase 0 (5%) and Phase 4 (15%) are never cut. For a `--budget 100000` run, this reserves 20K tokens for overhead, leaving only 80K for actual scanning (Phases 1-3). For repos larger than ~2,000 files, this may mean Tier 1 files barely get covered.
- **Source**: B4, Section 6
- **Severity**: MEDIUM
- **Impact**: Very low budgets produce audits where the overhead (profiling + consolidation) dominates actual scanning.
- **Proposed Mitigation**: Add a minimum useful budget calculation in Phase 0 dry-run. If budget < estimated minimum, warn the user.

#### F-B-16: No Discussion of Concurrent/Parallel Audit Runs
- **Category**: Missing Edge Cases
- **Description**: What happens if two audit runs execute simultaneously on the same repo? Both write to `.claude-audit/`, both update `progress.json`, both read/write the manifest. There is no locking, no run-ID isolation, no conflict detection.
- **Source**: B4, Section 8 ("Output Specification")
- **Severity**: MEDIUM
- **Impact**: Concurrent runs corrupt each other's output, producing unreliable results.
- **Proposed Mitigation**: Add run-ID to output directory (e.g., `.claude-audit/run-{timestamp}/`) or use file locking.

#### F-B-17: Binary and Asset File Handling is Underspecified
- **Category**: Missing Edge Cases
- **Description**: Tier 4 includes "assets, generated files, vendor code, binaries" with "Metadata only" read depth. But the PRD does not define what "metadata" means for a binary file. Binary files cannot be meaningfully read by LLMs. The system should acknowledge this and use only file-system metadata (size, extension, last-modified) plus reference counting.
- **Source**: B4, Section 4 (Tier 4)
- **Severity**: MEDIUM
- **Impact**: Scanners may attempt to read binary files, wasting tokens on garbage output.
- **Proposed Mitigation**: Explicitly list binary file extensions to skip content reading. Use only `file` command output, git metadata, and grep-based reference counting.

#### F-B-18: Documentation Audit Deferred to Phase 5 Creates Incoherent MVP
- **Category**: Internal Contradictions
- **Description**: Set A's primary finding was "Pass 4 docs audit is critically missing." Set B's PRD defers the docs audit to Phase 5 (future work). This means the v2 MVP still has the same gap that motivated the entire improvement effort. The reflection (B3) correctly noted that the proposals downgraded the docs audit from CRITICAL to MEDIUM -- but the gap analysis that justified the project started from docs being the #1 problem.
- **Source**: B1 Finding 1 (CRITICAL) vs B2 Proposal 9 (MEDIUM) vs B4 Section 12 Phase 5
- **Severity**: MEDIUM
- **Impact**: The primary stakeholder complaint (docs are never audited) will not be addressed by v2 MVP.
- **Proposed Mitigation**: Include a minimal docs audit (broken links + temporal classification) in Phase 3 or Phase 4, not as a separate deferred pass.

#### F-B-19: Backward Compatibility Mapping Has Semantic Drift
- **Category**: Internal Contradictions
- **Description**: B4 Section 4 maps v1 `REVIEW` to v2 `INVESTIGATE:insufficient-evidence`. But v1 `REVIEW` meant "human should look at this" (an action recommendation), while v2 `INVESTIGATE:insufficient-evidence` means "the audit couldn't determine classification" (an admission of failure). These are semantically different. Files that v1 would classify as REVIEW because they are ambiguous are not the same as files where evidence gathering failed.
- **Source**: B4, Section 4 ("Backward Compatibility")
- **Severity**: MEDIUM
- **Impact**: Users migrating from v1 to v2 will misinterpret INVESTIGATE items as audit failures rather than review recommendations.
- **Proposed Mitigation**: Add `INVESTIGATE:human-review-needed` qualifier for genuinely ambiguous files (distinct from evidence-gathering failure).

#### F-B-20: Proposal Debate Artificially Downgrades Findings
- **Category**: Unrealistic Assumptions
- **Description**: B2 re-ranks Finding 1 (Pass 4 Docs Audit) from CRITICAL to MEDIUM and Finding 3 (Batch Decomposition) from CRITICAL to HIGH. The rationale for downgrading docs ("opt-in, cap at 20%") does not change the severity of the gap -- it changes the cost of addressing it. A gap remains CRITICAL regardless of whether the fix is cheap or expensive. The debate conflates "priority" (when to implement) with "severity" (how bad is the gap).
- **Source**: B2, "Debated Priority Ranking"
- **Severity**: MEDIUM
- **Impact**: True severity is obscured, potentially causing stakeholders to underestimate the impact of unaddressed gaps.
- **Proposed Mitigation**: Maintain separate severity and priority rankings. Severity measures impact of the gap; priority measures when to fix it.

### LOW

#### F-B-21: Per-File Evidence Schema References "test_coverage" but No Mechanism to Obtain It
- **Category**: Feasibility Issues
- **Description**: The 8-field profile includes `test_coverage: "covered" | "uncovered" | "unknown"` (B4, Section 5 Phase 2). Determining test coverage requires either running tests with coverage instrumentation or parsing existing coverage reports. The PRD provides no mechanism for either.
- **Source**: B4, Section 5 ("Phase 2")
- **Severity**: LOW
- **Impact**: The field will always be "unknown" in practice, adding noise without signal.
- **Proposed Mitigation**: Replace with `test_file_exists: bool` (check if a corresponding test file exists) which is cheaply verifiable.

#### F-B-22: "Expert Panel Consensus" Includes a Non-Existent Expert
- **Category**: Unrealistic Assumptions
- **Description**: B4 Section 14 includes "Michael Nygard (Production Systems)" as a panel member who was not in Set A's panel (which had Wiegers, Fowler, Crispin). The panels are simulated anyway, but inconsistency between the two sets creates confusion about which fictional experts were "consulted."
- **Source**: B4, Section 14 vs A2, Section 8
- **Severity**: LOW
- **Impact**: Minor credibility issue; reinforces that the panels are fictional.
- **Proposed Mitigation**: Drop the expert panel framing entirely or standardize the panel across documents.

#### F-B-23: Dynamic Import Detection Pattern List is Incomplete
- **Category**: Specification Gaps
- **Description**: B4 lists `import(`, `require(`, `React.lazy`, `next/dynamic`, `importlib.import_module` as dynamic import patterns (Section 5 Phase 3). Missing: `__import__()` (Python), `System.import()` (legacy), `define()` (AMD), `require.resolve()`, `jest.mock()`, `jest.requireActual()`, `proxyquire`, `rewire`, Vite's `import.meta.glob`.
- **Source**: B4, Section 5 ("Phase 3")
- **Severity**: LOW
- **Impact**: Some dynamically imported files may be incorrectly classified as dead code.
- **Proposed Mitigation**: Make the pattern list configurable via `audit.config.yaml` rather than hardcoded.

---

## Cross-Set Flaws (Issues Present in BOTH Sets)

### CS-01: Neither Set Addresses Non-English Documentation
- **Category**: Missing Edge Cases
- **Severity**: MEDIUM
- **Description**: Both sets focus on English-language documentation. Neither addresses repos with multilingual docs, CJK filenames, or RTL text in markdown files. Link extraction, claim verification, and overlap detection may fail on non-ASCII content.
- **Source**: A2 Section 4.3, B4 Section 5 Phase 2
- **Impact**: The audit silently produces incomplete results for internationalized repos.
- **Proposed Mitigation**: Acknowledge limitation explicitly. Add UTF-8 handling requirements for link extractors.

### CS-02: Both Sets Assume Markdown-Only Documentation
- **Category**: Missing Edge Cases
- **Severity**: MEDIUM
- **Description**: Both sets focus exclusively on `.md` files for documentation analysis. Neither addresses `.rst` (reStructuredText), `.adoc` (AsciiDoc), `.txt` (plain text), `.html` (generated docs), Jupyter notebooks (`.ipynb`), or in-code documentation (docstrings).
- **Source**: A2 Section 4.3, B4 Section 5
- **Impact**: Repos using non-markdown documentation formats receive no docs coverage.
- **Proposed Mitigation**: Define supported formats explicitly. Start with `.md` and `.rst` as first-class; others as "best-effort."

### CS-03: Both Sets Lack a "Do Nothing" Escape Path
- **Category**: Missing Edge Cases
- **Severity**: MEDIUM
- **Description**: Neither set considers that the audit might conclude "this repo is well-maintained; no significant cleanup needed." All output structures assume there will be findings. What does the FINAL-REPORT look like when there are zero DELETE candidates and zero broken references?
- **Source**: A2 Section 7, B4 Section 8
- **Impact**: A clean repo produces a confusing report with empty sections.
- **Proposed Mitigation**: Define a "clean report" template that positively confirms repo health.

### CS-04: Both Sets Underspecify Subagent Failure Handling
- **Category**: Missing Error Handling
- **Severity**: HIGH
- **Description**: Both sets describe multi-agent architectures but neither fully specifies what happens when a subagent fails, times out, produces garbage output, or exceeds its token budget. Set A mentions no error handling at all. Set B has schema validation with one retry but does not address: persistent failures, partial batch completion, or cascading failures across phases.
- **Source**: A2 Section 5.2, B4 Sections 5 and 9
- **Impact**: In production, subagent failures are common (timeout, malformed output, context overflow). Without robust handling, the audit becomes unreliable.
- **Proposed Mitigation**: Define per-subagent timeout, max retries (2), fallback behavior (mark batch as FAILED, continue with remaining batches), and a minimum viable report that can be generated even if 50% of batches fail.

### CS-05: Both Sets Reference GFxAI Repository Specifics as Universal Requirements
- **Category**: Scope Creep
- **Severity**: MEDIUM
- **Description**: Both sets were derived from analyzing a specific repository (GFxAI) with specific characteristics (Docker, Next.js, Playwright, 5,800 files). Requirements like "port validation against network spec" and "Playwright config consolidation" are GFxAI-specific but are presented as universal audit features.
- **Source**: A1 (entire doc references GFxAI), B1 Findings 4 and 6 (GFxAI-specific examples)
- **Impact**: The tool may be over-fitted to one repo's patterns and underperform on repos with different stacks.
- **Proposed Mitigation**: Clearly separate "universal audit features" from "project-specific rule examples." Make project-specific rules loadable from config.

### CS-06: Neither Set Has a Realistic Testability Story
- **Category**: Feasibility Issues
- **Severity**: HIGH
- **Description**: Set A proposes golden-output fixtures (brittle for LLM output). Set B proposes acceptance criteria per requirement (good) but many criteria are vague ("FINAL-REPORT.md contains at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE" -- this passes even if the report is garbage). Neither set proposes integration tests against real repositories, performance benchmarks, or regression test baselines.
- **Source**: A2 Section 7, B4 Section 13
- **Impact**: The spec cannot be validated as "working" in any meaningful way.
- **Proposed Mitigation**: Define 3 test tiers: (1) structural tests (output files exist, JSON valid, required sections present), (2) property tests (coverage percentages in range, no credential values in output, all Tier 1 files examined), (3) benchmark tests against 2-3 real repos with known characteristics.

---

## Flaw Summary Statistics

### Set A
| Severity | Count |
|----------|-------|
| CRITICAL | 3 |
| HIGH | 5 |
| MEDIUM | 4 |
| LOW | 2 |
| **Total** | **14** |

### Set B
| Severity | Count |
|----------|-------|
| CRITICAL | 5 |
| HIGH | 8 |
| MEDIUM | 7 |
| LOW | 3 |
| **Total** | **23** |

### Cross-Set (Shared)
| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 4 |
| LOW | 0 |
| **Total** | **6** |

### Grand Total: 43 flaws

### Top 5 Flaws by Impact (Across Both Sets)

1. **F-B-02 / F-A-01**: Token cost estimates are absent (Set A) or still underestimated (Set B). This is the single highest-risk issue -- if budgets are wrong, everything built on them fails.

2. **F-A-02**: No spec-implementation gap acknowledgment in Set A. Set B correctly identified this but Set A built an entire PRD without noticing the existing spec already promised unimplemented features.

3. **F-B-03**: Dependency graph construction via LLM is infeasible for most languages. This is the flagship new feature of v2 and it may not work reliably.

4. **F-B-05**: LLM-on-LLM validation measures consistency not correctness. The quality gate that makes users trust the audit is fundamentally flawed.

5. **CS-04**: Subagent failure handling is underspecified in both sets. In real-world use, this will be the most common source of audit failures.

---

*Flaw analysis complete | 2026-02-20*
*43 flaws identified: 8 CRITICAL, 15 HIGH, 15 MEDIUM, 5 LOW*
