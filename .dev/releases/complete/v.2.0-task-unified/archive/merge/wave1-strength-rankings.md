# Wave 1: Strength Rankings

**Date**: 2026-02-20
**Method**: Systematic scoring of top elements across 4 dimensions (Specificity, Evidence Quality, Implementability, Architectural Soundness)
**Scoring Scale**: 1-10 per dimension, Composite = average of 4 dimensions

---

## Set A: Top 10 Strongest Elements

**Source Files**:
- A1: `SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
- A2: `SC_CLEANUP_AUDIT_VNEXT_PRD.md`

---

### A-1. Pass 4 Docs Quality Output Schema (Sections 1-5)
**Source**: A2, Section 4.3
**Composite Score: 8.8**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Defines 5 exact required sections (SCOPE, CONTENT_OVERLAP_GROUPS, BROKEN_REFERENCES, CLAIM_SPOT_CHECKS, TEMPORAL_ARTIFACTS) with sub-fields, checklist formatting, and cap rules |
| Evidence Quality | 8 | Derived from direct comparison of old Pass 4 outputs vs new output gap; cites "near-zero evidence about documentation correctness" |
| Implementability | 9 | Each section has a clear format spec (e.g., `- [ ] path/to/doc.md:line -> missing/relative/path`), claim types enumerated, cap rules specified |
| Architectural Soundness | 9 | Additive pass, no coupling to existing passes, cost controls (sampling, structural-only claims), clear non-goal boundary (no semantic correctness) |

**Standout Reason**: This is the most complete specification of a new pass in either set. An engineer could implement Pass 4 from this description alone with minimal ambiguity.

---

### A-2. Known Issues Suppression Registry Schema
**Source**: A2, Section 4.4
**Composite Score: 8.5**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Defines JSON schema with 6 exact fields (id, signature, category, created_at, status, reference), suppression matching rules, and conservative matching constraints |
| Evidence Quality | 8 | Cites "34 items" from old approach, identifies "audit thrash" failure mode with concrete example |
| Implementability | 9 | JSON schema is directly implementable, matching logic is specified (signature-based not path-based), edge case handled (file moved/renamed) |
| Architectural Soundness | 8 | Optional mechanism (does not break existing flow), conservative design (prefer false positive over false suppression), clear output bucket (ALREADY_TRACKED) |

**Standout Reason**: Complete data model with matching logic and edge case handling. The signature-based matching vs path-based matching distinction shows architectural maturity.

---

### A-3. Acceptance Criteria (A1-A5)
**Source**: A2, Section 7
**Composite Score: 8.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Five numbered criteria with exact format requirements (e.g., "filepath:line -> missing format"), count thresholds (3-5 per sampled doc), and structural test descriptions |
| Evidence Quality | 7 | Criteria derived from gap analysis findings but no measurement of what "substantially unchanged" means for regression |
| Implementability | 9 | Each criterion is directly testable; golden-output fixture approach specified with synthetic repo contents |
| Architectural Soundness | 8 | Includes both positive tests (new features work) and regression checks (existing passes unchanged); verification approach is practical |

**Standout Reason**: Testable acceptance criteria with a practical verification approach (synthetic repo fixtures). Bridges spec to implementation.

---

### A-4. progress.json Schema Additions
**Source**: A2, Section 6.1
**Composite Score: 8.0**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Exact field names, types, and nesting specified (e.g., `passes.pass4_docs.sampled_files` as count) |
| Evidence Quality | 7 | Derived from gap analysis but no current schema shown for comparison |
| Implementability | 9 | Direct JSON field additions; trivially implementable |
| Architectural Soundness | 7 | Extends existing schema cleanly, but does not address backward compatibility or versioning |

**Standout Reason**: Concrete data model change that is immediately implementable with zero ambiguity.

---

### A-5. Evidence-Backed Delta Analysis (Pass-by-Pass)
**Source**: A1, Section "Evidence-backed delta"
**Composite Score: 7.8**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 7 | Structured per-pass comparison with explicit "old prompt intent" vs "new output strengths" vs "new output gaps" |
| Evidence Quality | 9 | Directly references old prompt behaviors, new output artifacts (12 structural profiles, duplication matrices), and specific missing behaviors |
| Implementability | 7 | Diagnostic rather than prescriptive; identifies gaps but leaves solution design to PRD |
| Architectural Soundness | 8 | Systematic coverage of all 4 passes ensures no gap is missed; honest about Pass 3 strengths |

**Standout Reason**: The strongest evidence gathering in Set A. The pass-by-pass structure ensures comprehensive coverage and the honest assessment of new output strengths prevents throwing out what works.

---

### A-6. Adversarial Debate on Each Proposal
**Source**: A1, Section "Adversarial debate"
**Composite Score: 7.5**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 7 | FOR/AGAINST/MITIGATION structure for each of 3 proposals with specific counterarguments |
| Evidence Quality | 8 | Cites concrete risks (token cost, false suppression, noise from broken links) with mitigations |
| Implementability | 7 | Mitigations are actionable (restrict to structural claims, suppress by signature not path, cap output) |
| Architectural Soundness | 8 | Shows intellectual honesty about tradeoffs; mitigations address the core objection in each case |

**Standout Reason**: Self-critical analysis that strengthens the proposals by identifying and addressing weaknesses before implementation.

---

### A-7. Broken-Reference Checklist Format Specification
**Source**: A2, Section 4.5 and A1 P1 proposal
**Composite Score: 7.5**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Exact format: `- [ ] filepath:line -> missing/path - context`; scoped to relative links by default; capped output with total count |
| Evidence Quality | 7 | Cites old prompt requirement for checklist format and identifies new output gap |
| Implementability | 8 | Format is directly implementable; link extraction step specified |
| Architectural Soundness | 6 | Good format spec but lacks detail on how link extraction integrates with pass orchestration |

**Standout Reason**: Highly specific output format that is immediately actionable by engineers reading the audit report.

---

### A-8. Implementation Pointers (SuperClaude File Locations)
**Source**: A1, Section "Implementation pointers"
**Composite Score: 7.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Exact file paths for SKILL.md, rules/pass1-3, templates; explicitly notes "no Pass 4 rules file exists" |
| Evidence Quality | 8 | Verified against actual file system; factual statements about what exists and what is missing |
| Implementability | 7 | Points to exact files to modify but does not specify the changes needed within each file |
| Architectural Soundness | 5 | Descriptive rather than prescriptive; no discussion of how changes fit into the skill's existing patterns |

**Standout Reason**: Grounds the entire specification in the actual codebase, preventing the common failure mode of specs that cannot be mapped to implementation.

---

### A-9. Cost Control Mechanisms for Pass 4
**Source**: A2, Section 4.3 (caps) and A1 P0 proposal
**Composite Score: 7.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 8 | Directory-level sampling (5-10 representative docs), structural claims prioritized, capped output |
| Evidence Quality | 7 | Addresses the "high token cost" adversarial argument with concrete mitigations |
| Implementability | 7 | Sampling policy described but sampling algorithm not specified (how to select representative docs) |
| Architectural Soundness | 7 | Addresses the primary risk (unbounded doc analysis) but does not specify hard token limits |

**Standout Reason**: Directly addresses the main feasibility risk of the docs audit pass with practical constraints.

---

### A-10. Expert Panel Critique Synthesis
**Source**: A2, Section 8
**Composite Score: 7.0**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 7 | Named frameworks (Wiegers, Fowler, Crispin) with specific improvement recommendations |
| Evidence Quality | 6 | Simulated panel rather than real review; recommendations are reasonable but lack external validation |
| Implementability | 7 | Each recommendation is actionable (add default thresholds, treat ARCHIVE as label, define contract tests) |
| Architectural Soundness | 8 | Three complementary perspectives (requirements quality, evolutionary architecture, testability) cover the spec well |

**Standout Reason**: Multi-perspective review catches issues that single-viewpoint analysis misses (e.g., Fowler's point about ARCHIVE as label vs mandatory directory).

---

## Set B: Top 10 Strongest Elements

**Source Files**:
- B1: `cleanup-audit-improvement-findings.md`
- B2: `cleanup-audit-improvement-proposals.md`
- B3: `cleanup-audit-reflection-validation.md`
- B4: `cleanup-audit-v2-PRD.md`

---

### B-1. Standardized Scanner Output Schema (JSON)
**Source**: B4, Section 3 (Architecture) and B2, Proposal 1
**Composite Score: 9.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 10 | Complete JSON schema with exact field names, types, nesting, enum values for classification, evidence sub-object with grep_command/grep_result_count/import_references/last_commit_days, plus external_dependencies and export_targets arrays |
| Evidence Quality | 9 | Derived from the cross-reference synthesis requirement; the reflection doc (B3) validates that this schema is the architectural enabler for P1/P3/P8 |
| Implementability | 9 | JSON schema is directly codifiable; validation rule specified (retry once on non-compliance, then mark FAILED) |
| Architectural Soundness | 9 | Single schema unifies all scanner output, enables cross-reference synthesis, and provides the foundation for coverage tracking. The reflection doc identifies this as "the key architectural decision that makes everything else possible" |

**Standout Reason**: The single most important architectural element in either set. Without this schema, cross-reference synthesis, coverage tracking, and anti-lazy enforcement are all impossible. The schema is complete enough to implement directly.

---

### B-2. Unified Classification System (Two-Tier with Qualifiers)
**Source**: B4, Section 4; B2, Proposal 8
**Composite Score: 9.0**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 10 | 4 primary categories, 13 secondary qualifiers, each with exact meaning defined. Backward compatibility mapping from v1 categories explicitly specified. INVESTIGATE subcategories (cross-boundary, insufficient-evidence, dynamic-import) address edge cases |
| Evidence Quality | 8 | Finding 10 (B1) quantifies the gap: old had 5 categories with 179 FLAG findings; new has 3. Reflection (B3) validates INVESTIGATE as necessary bridge for P1 |
| Implementability | 9 | Enum values directly implementable; qualifier format (`Primary:Qualifier`) is parse-friendly; report structure template provided |
| Architectural Soundness | 9 | Two-tier design is composable and extensible without schema changes. Backward compatibility mapping preserves v1 interop. INVESTIGATE as explicit escape hatch prevents forced mis-classification |

**Standout Reason**: Elegant design that solves the 5-category problem while being extensible. The backward compatibility mapping is particularly valuable for migration.

---

### B-3. Tiered Coverage Guarantee with Manifest
**Source**: B4, Sections 4 (risk tiers) and 5 (Phase 4 coverage report); B2, Proposal 3
**Composite Score: 9.0**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | 4 tiers with exact coverage targets (100%/95%/80%/60%), path pattern rules in YAML, coverage report JSON with per-tier PASS/WARN/FAIL status, explicit handling of unexamined files |
| Evidence Quality | 9 | Finding 13 (B1) provides the evidence: "no mechanism to detect gaps or overlaps." Reflection (B3) validates feasibility and identifies the monorepo scaling risk with mitigation (per-directory tracking above 10K files) |
| Implementability | 9 | YAML config directly loadable, coverage report JSON directly serializable, quality gate criteria (Tier 1 >= 100%, Tier 2 >= 90%) are testable assertions |
| Architectural Soundness | 9 | Tiered approach avoids the all-or-nothing problem. Coverage as a report metric (not a hard gate) means the audit always completes. Scaling mitigation for monorepos shows production thinking |

**Standout Reason**: This is the structural prerequisite for trusting any audit output, as the reflection doc notes. The tiered design makes it practical for repos of all sizes.

---

### B-4. Budget System with Graceful Degradation
**Source**: B4, Section 6
**Composite Score: 8.8**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | `--budget` flag with default 300K, per-phase allocation percentages (5/25/35/20/15) with hard ceilings, 4-level graceful degradation sequence with explicit never-cut list, 4 runtime scenarios with estimated tokens/coverage/runtime |
| Evidence Quality | 9 | Reflection doc (B3) identified that original proposals underestimated by 2-3x and provided realistic estimates. PRD uses those corrected estimates. 4 scenarios (100K/300K/500K/800K) give practical reference points |
| Implementability | 9 | Budget enforcement is a simple counter (monitor after each batch, switch modes at 90%/100%). Degradation sequence is ordered and unambiguous. CLI flag is standard |
| Architectural Soundness | 8 | Addresses the #1 practical risk (token cost explosion). The "never cut" list (Phase 0 profiling, Phase 1 Tier 1-2, Phase 4 consolidation) shows understanding of which components are load-bearing |

**Standout Reason**: Transforms the audit from an unbounded operation into a predictable one. The graceful degradation sequence is particularly well-designed -- it preserves the highest-value work while shedding the lowest-value work first.

---

### B-5. Phase 0: Profile and Plan (Repository Profiling)
**Source**: B4, Section 5 (Phase 0 spec); B2, Proposal 11
**Composite Score: 8.5**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Agent (Haiku), duration (30-60s), budget (5%), 6-step process, 4 output artifacts with exact paths, quality gate (100% file assignment), auto-config generation from framework/port/CI detection |
| Evidence Quality | 8 | Reflection doc (B3) identifies this as infrastructure prerequisite: "P1 cannot work until P6 or P11 creates domain-aware scanners." PRD correctly places it as Phase 0 |
| Implementability | 9 | Process steps are concrete bash commands (git ls-files, scan directories, detect framework from package.json). Output artifacts have exact paths. Quality gate is a simple assertion |
| Architectural Soundness | 8 | Enables everything downstream (batch decomposition, coverage tracking, tier assignment). Cold-start handling (auto-generate config, never fail) follows principle of least surprise. Lightweight (Haiku, 30-60s) |

**Standout Reason**: The foundation phase that enables all other improvements. Well-specified with concrete outputs and a practical cold-start strategy.

---

### B-6. Credential File Scanning Fix
**Source**: B2, Proposal 2; B4, Section 5 (Phase 1 credential rules)
**Composite Score: 8.5**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | Priority-ordered enumeration (.env.production first), template detection patterns (CHANGE_ME_*, YOUR_*_HERE), real credential patterns (sk-*, ghp_*, AKIA*, base64 >40 chars, BEGIN RSA), explicit "NEVER print values" rule, disclaimer text specified |
| Evidence Quality | 9 | Finding 6 (B1) provides the smoking gun: "Real credentials in .env.production misidentified as template values" -- a correctness failure, not a depth issue. All 4 debate agents agreed "non-negotiable" |
| Implementability | 9 | Pattern lists are directly grep-able. Priority ordering is a simple list iteration. Template vs real detection is a classification with known patterns. No architectural changes needed |
| Architectural Soundness | 7 | Correctly scoped as "not a security audit substitute" with explicit disclaimer. However, the integration point (is this Phase 1 scanner logic or a separate pre-audit step?) could be clearer |

**Standout Reason**: The highest-confidence fix in either set. A correctness failure (wrong answer vs missing depth) with bounded cost and unanimous expert agreement.

---

### B-7. Dependency Ordering Correction (5-Phase Roadmap)
**Source**: B3, Dimension 5 (Priority Ranking Assessment); B4, Section 12 (Implementation Roadmap)
**Composite Score: 8.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 8 | 5 phases with explicit dependencies (Phase 0 -> 1 -> 2 -> 3 -> 4 -> 5), effort estimates per phase (4-6h, 2-3h, 6-8h, 8-12h, 4-6h, 6-10h), items per phase enumerated |
| Evidence Quality | 9 | Reflection doc provides the critical insight: P1 (Cross-Reference, ranked #1) depends on P6/P11 (ranked #6/#11). The hidden dependency chain `P11 -> P6 -> P1 -> P10` is explicitly traced. Also identifies "Phase 0: Enforce Existing Spec" as a prerequisite others missed |
| Implementability | 8 | Phase boundaries are clear. Effort estimates are present (though not validated). Dependencies are unambiguous |
| Architectural Soundness | 8 | Fixes the fundamental ordering error in the proposals. "Enforce existing spec before adding features" is architecturally sound. Each phase produces artifacts the next phase consumes |

**Standout Reason**: The reflection document's most valuable contribution. Without this correction, implementation would fail because Phase 1 (Cross-Reference) would have no structured input to operate on.

---

### B-8. Anti-Lazy Enforcement via Structured Output
**Source**: B4, Section 9; B2, Proposal 7
**Composite Score: 8.3**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | 4 enforcement mechanisms: required output fields, evidence non-emptiness rules (DELETE needs grep, Tier 1-2 KEEP needs imports), confidence distribution check (>90% identical = flag), cross-batch consistency check |
| Evidence Quality | 8 | Finding 9 (B1) provides the motivation with verbatim old-prompt quotes. Reflection (B3) validates the approach: "enforce output structure and calibration correctness instead" of tool-call counts |
| Implementability | 8 | Field presence/non-emptiness checks are trivial validators. Confidence distribution is a simple statistical check. Cross-batch consistency requires file-path intersection |
| Architectural Soundness | 8 | Reframes from "count tool calls" (gameable) to "validate output quality" (measurable). Defers calibration files to Phase 5 (acknowledging cold-start problem). The key insight is that output structure enforcement is both cheaper and more effective than procedural enforcement |

**Standout Reason**: Solves the "rubber-stamping" problem without the overhead of minimum tool-call counts. The confidence distribution heuristic (>90% identical values = suspicious) is a clever, low-cost quality signal.

---

### B-9. Spec-Implementation Gap Analysis
**Source**: B3, Dimension 2 (Feasibility); B4, Section 2
**Composite Score: 8.0**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 9 | 5 specific v1 spec promises identified with exact implementation status (NOT IMPLEMENTED, PARTIAL). Table format with spec promise vs status mapping |
| Evidence Quality | 9 | Directly verified against the current spec file (`/config/.claude/commands/sc/cleanup-audit.md`). Quotes spec language ("transparently report what was and was not audited") and shows it was never implemented |
| Implementability | 7 | Identifies the gap clearly but the "fix" is simply "implement what was promised" -- the how is left to the PRD |
| Architectural Soundness | 7 | Critical meta-insight that prevents building new features on an unreliable foundation. However, does not analyze WHY the gap exists (addressed separately as root cause) |

**Standout Reason**: The most important meta-finding. Without this, the PRD would add new features to a spec that already has unimplemented features, widening the credibility gap.

---

### B-10. Token Cost Realism Correction
**Source**: B3, Dimension 3 (Runtime/Token Impact Realism)
**Composite Score: 7.8**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Specificity | 8 | P4 token math: 585-1,171 files * 300-500 tokens/file = 175K-585K additional tokens. P6: 20+ batches * 2-3K prompt overhead = 40-60K. Revised table with proposed vs realistic estimates |
| Evidence Quality | 9 | Quantitative analysis showing proposals underestimate by 2-3x. Uses the proposals' own numbers (10-20% of 5,857 files) to derive the correction. Identifies P4 (Evidence KEEP) as the dominant cost factor |
| Implementability | 7 | Identifies the problem and proposes the `--budget` flag mitigation, but the budget allocation strategy is specified more fully in B4 |
| Architectural Soundness | 8 | Prevents a deployment failure by catching unrealistic estimates before implementation. The insight that "messy codebases have higher trigger rates" shows production thinking |

**Standout Reason**: Prevents the most likely implementation failure (token budget explosion). The quantitative correction is well-reasoned and directly influenced the PRD's budget system design.

---

## Cross-Set Comparison

### Average Composite Scores

| Set | Average Composite | Range |
|-----|------------------|-------|
| **Set A** | 7.70 | 7.0 - 8.8 |
| **Set B** | 8.55 | 7.8 - 9.3 |
| **Delta** | +0.85 in favor of Set B | |

### Dimension Excellence by Set

| Dimension | Set A Average | Set B Average | Winner | Margin |
|-----------|--------------|--------------|--------|--------|
| Specificity | 8.3 | 9.1 | **Set B** | +0.8 |
| Evidence Quality | 7.5 | 8.8 | **Set B** | +1.3 |
| Implementability | 7.9 | 8.5 | **Set B** | +0.6 |
| Architectural Soundness | 7.2 | 8.1 | **Set B** | +0.9 |

**Analysis**:

- **Set B excels on Evidence Quality** (largest margin: +1.3). The multi-agent process produced quantified gaps (44x fewer profiles, 527 vs 12 files profiled), real-world failure examples (credential false negative), and self-correcting validation (reflection doc caught 2-3x token underestimates).
- **Set B excels on Specificity** (+0.8). The standardized scanner output schema, two-tier classification system, and coverage report JSON are more complete and implementable than Set A's equivalents.
- **Set A has stronger adversarial self-critique proportionally** -- the gap analysis + debate structure surfaces tradeoffs effectively despite being more concise. However, Set B's reflection document takes this further by catching dependency ordering errors.
- **Set A is more concise** and could serve as a "quick reference" summary, whereas Set B is the implementation-ready specification.

### Which Set Excels Where

| Strength | Set A | Set B |
|----------|-------|-------|
| Conciseness and readability | Strong | Verbose |
| Pass 4 docs audit specification | Strong (self-contained) | Deferred to Phase 5 (opt-in) |
| Known-issues registry data model | Strong (complete JSON schema) | Simplified to post-hoc dedup |
| Scanner output standardization | Not addressed | Strong (complete JSON schema) |
| Budget and cost controls | Mentioned but unspecified | Strong (4-level degradation) |
| Dependency ordering | Not addressed | Strong (corrected via reflection) |
| Classification system | Simple (5 buckets) | Strong (two-tier composable) |
| Credential scanning | Not addressed | Strong (enumeration + patterns) |
| Anti-lazy enforcement | Not addressed | Strong (output validation) |
| Coverage tracking | Not addressed | Strong (tiered manifest) |

---

## Baseline Scores (for Wave 4 Quality Gate)

- **Set A average composite**: 7.70
- **Set B average composite**: 8.55
- **Combined baseline**: 8.13 (weighted by element count: 10+10=20 elements)

### Combined "Must Include" Elements List

These elements scored >= 8.0 composite OR are identified as structural prerequisites by both sets. Ordered by composite score.

| Rank | Element | Source | Composite | Rationale |
|------|---------|--------|-----------|-----------|
| 1 | Standardized Scanner Output Schema | B-1 | 9.3 | Architectural enabler for cross-reference, coverage, anti-lazy |
| 2 | Unified Two-Tier Classification System | B-2 | 9.0 | Solves category gap with backward compat and extensibility |
| 3 | Tiered Coverage Guarantee with Manifest | B-3 | 9.0 | Structural prerequisite for trusting audit output |
| 4 | Pass 4 Docs Quality Output Schema | A-1 | 8.8 | Most complete new-pass specification; fills the largest gap |
| 5 | Budget System with Graceful Degradation | B-4 | 8.8 | Prevents the #1 practical failure (token cost explosion) |
| 6 | Known Issues Suppression Registry | A-2 | 8.5 | Complete data model with matching logic and edge cases |
| 7 | Phase 0 Repository Profiling | B-5 | 8.5 | Foundation phase enabling batch decomposition and tier assignment |
| 8 | Credential File Scanning Fix | B-6 | 8.5 | Correctness fix (wrong answer), non-negotiable |
| 9 | Acceptance Criteria (A1-A5) | A-3 | 8.3 | Testable criteria with golden-fixture verification approach |
| 10 | Dependency Ordering Correction | B-7 | 8.3 | Prevents implementation failure from wrong build order |
| 11 | Anti-Lazy Enforcement via Structured Output | B-8 | 8.3 | Solves rubber-stamping without gameable metrics |
| 12 | progress.json Schema Additions | A-4 | 8.0 | Concrete data model, zero ambiguity |
| 13 | Spec-Implementation Gap Analysis | B-9 | 8.0 | Meta-insight: enforce existing spec before adding features |

### Reconciliation Notes for Merger

1. **Pass 4 (Docs Audit)**: Set A treats this as P0 must-have; Set B demotes to Phase 5 opt-in. The merged spec should include Set A's detailed output schema (A-1) but adopt Set B's opt-in activation and token cap (20% budget). This combines the best of both.

2. **Known Issues Registry**: Set A defines a full JSON registry with inter-pass suppression; Set B replaces this with post-hoc deduplication in the consolidator. The merged spec should use Set B's consolidator-based dedup (simpler, preserves parallelism) but adopt Set A's schema for cross-run persistence (enables "run weekly without re-discovering" use case).

3. **Classification Categories**: Set A uses 5 flat categories (DELETE/FLAG/CONSOLIDATE/ARCHIVE/KEEP); Set B uses 4 primary + 13 qualifiers. Set B's two-tier system subsumes Set A's categories via the backward compatibility mapping. Use Set B's system.

4. **Budget Controls**: Only Set B addresses this. Include as-is.

5. **Phase 0 Profiling**: Only Set B addresses this. Include as-is.

6. **Credential Scanning**: Only Set B addresses this. Include as-is.

7. **Anti-Lazy Enforcement**: Only Set B addresses this. Include as-is.

---

*Generated by Strength Extractor agent | 2026-02-20*
*Scoring method: 4-dimension analysis (Specificity, Evidence Quality, Implementability, Architectural Soundness)*
*Each dimension scored 1-10, Composite = arithmetic mean*
