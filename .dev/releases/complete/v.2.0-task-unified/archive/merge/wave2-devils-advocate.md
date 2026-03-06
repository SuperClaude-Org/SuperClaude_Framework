# Wave 2: Devil's Advocate Attack

**Date**: 2026-02-20
**Role**: Devil's Advocate -- ruthless attack on both analysis sets
**Input**: Set A (2 docs), Set B (4 docs), Wave 1 outputs (4 docs)
**Mission**: Find what both advocates will miss. Be the hardest critic in the room.

---

## Part 1: Fundamental Design Attacks

### Attack 1: This is a static analysis problem being solved with the wrong tool

Both sets assume that an LLM-based multi-pass audit is the right approach to repository cleanup. Neither asks the obvious question: **why not use actual static analysis tools?**

- `madge` builds JavaScript dependency graphs in seconds with 100% accuracy for static imports
- `pydeps` does the same for Python
- `deadcode` detects unused Python code
- `ts-prune` finds unused TypeScript exports
- `unimported` finds unimported files in JS/TS projects
- `git log --diff-filter=A --name-only` gives you every file's creation date
- `grep -rL` finds unreferenced files faster than any LLM

These tools produce deterministic, reproducible results at zero token cost. An LLM reading 50 lines of a file and guessing whether it is "used" is strictly worse than `grep -r 'import.*filename'` for the import-detection use case. The entire dependency graph feature (Set B's flagship Phase 3) could be replaced by running `madge --orphans` and formatting the output.

**The uncomfortable question**: What percentage of this spec's value comes from things LLMs are actually good at (subjective judgment about code quality, natural-language report generation, nuanced "should we archive this?" decisions) versus things static tools do better (import graphs, reference counting, dead code detection, link checking)?

My estimate: 70% of the proposed token budget goes toward tasks that static tools handle better. The remaining 30% -- subjective classification, report synthesis, doc quality assessment -- is where LLMs add genuine value.

**Neither set proposes a hybrid architecture** where static tools do the deterministic work and the LLM does the judgment work. This is the single largest architectural blind spot in both analyses.

### Attack 2: Evidence-gated classification is circular reasoning

Set B makes "evidence-gated classification" the cornerstone of quality. But examine the evidence chain:

1. An LLM subagent reads a file (50-100 lines)
2. The same LLM runs a grep command
3. The same LLM interprets the grep results
4. The same LLM classifies the file based on its interpretation
5. The same LLM produces a "confidence" score for its own classification
6. A different LLM instance "validates" 10% of these classifications

At no point does a ground-truth oracle enter the picture. The "evidence" is gathered by the same entity making the judgment. The "validation" is another LLM agreeing with the first LLM. This is like having a student grade their own exam and then having another student check 10% of the answers.

The grep commands are real evidence, but the LLM's **interpretation** of grep results is not. A grep returning 0 results for `import Button` does not mean Button is unused -- it could be imported as `import { Button as Btn }`, loaded via barrel export, referenced in a webpack alias, or consumed by a test framework pattern.

**Neither set acknowledges that confidence scores self-assigned by LLMs are not calibrated.** An LLM saying "confidence: 0.92" does not mean there is a 92% chance the classification is correct. It means the LLM generated the token sequence "0.92" as a completion. These numbers have no statistical grounding.

### Attack 3: The "tiered coverage" system adds complexity without improving outcomes

Set B's 4-tier coverage system (100%/95%/80%/60%) sounds rigorous. But consider:

- **Who decides the tier?** A Haiku model in Phase 0, reading directory names and path patterns. If it misclassifies a critical deploy script as "standard" because it lives in an unexpected directory, that file gets 80% coverage instead of 100%.
- **What does "95% coverage" mean?** That 95% of Tier 2 files were "examined." But "examined" means an LLM read 50-100 lines and produced a classification. A file can be "examined" and still have a wrong classification.
- **The thresholds are arbitrary.** Why 95% for Tier 2 and not 90% or 97%? There is no empirical basis. They exist to create the appearance of rigor.
- **Coverage percentage conflates quantity with quality.** Examining 95% of files at a shallow depth is worse than examining 50% of files deeply. The metric optimizes for breadth, not accuracy.

The tiered system creates a false sense of precision. Users see "Tier 1: 100%, PASS" and believe the audit thoroughly checked their deploy scripts. In reality, a Haiku model read each file for 5 seconds and produced a JSON blob.

### Attack 4: Can LLM subagents reliably produce structured JSON?

Both sets depend on LLM subagents producing valid, schema-compliant JSON output. Set B requires a 12+ field JSON schema per file from Haiku scanners. Let us be honest about the failure modes:

1. **Malformed JSON**: Missing quotes, trailing commas, unescaped characters. Haiku is particularly prone to this on long outputs.
2. **Schema drift**: The LLM produces valid JSON but with wrong field names (`file_name` instead of `file_path`, `type` instead of `classification`).
3. **Hallucinated values**: `"grep_result_count": 14` when the actual count is 3. The LLM fills in plausible numbers rather than running the command.
4. **Truncation**: For large batches (42 files), the JSON output exceeds the model's output limit and gets truncated mid-object.
5. **Inconsistent enums**: `"KEEP"` in one file, `"keep"` in another, `"Keep"` in a third.

Set B proposes "retry once on non-compliance, then mark FAILED." But if the schema compliance rate is 70% on first attempt (realistic for Haiku on complex schemas), and 80% on retry, then 20% of batches are marked FAILED. For 12 batches, that is 2-3 failed batches, meaning 15-25% of the repository receives zero analysis.

**Neither set benchmarks actual schema compliance rates for their chosen models on representative inputs.** This is the kind of thing you must measure empirically, not assume.

---

## Part 2: Budget and Token Arithmetic

### The math Set B claims

Set B's "Standard" scenario: 300K tokens for ~3,300 files (Tier 1-3) in ~18 minutes.

### The math that actually works out

**Phase 0 (5% = 15K tokens):**
- `git ls-files` output for 6,000 files: ~120K characters = ~30K tokens just to read the file list
- Already over budget for Phase 0 before any classification happens
- **Verdict**: 15K is insufficient. Realistic minimum: 25-40K tokens

**Phase 1 (25% = 75K tokens for surface scan):**
- 3,300 files to examine (Tier 1-3)
- 75K / 3,300 = ~23 tokens per file
- A minimal classification (`{"path": "x.ts", "classification": "KEEP", "confidence": 0.8}`) is ~20 tokens of output alone
- This leaves ~3 tokens per file for the system prompt, file content, and evidence
- **Verdict**: 75K tokens for 3,300 files is physically impossible if you actually read any file content

**Phase 2 (35% = 105K tokens for structural audit):**
- Set B says Phase 2 examines DELETE/INVESTIGATE candidates plus Tier 1-2 KEEP files
- Assume 200 DELETE/INVESTIGATE + 1,200 Tier 2 KEEP = 1,400 files
- 105K / 1,400 = ~75 tokens per file
- An 8-field profile is ~150-300 tokens of output per file
- Plus input (system prompt + file content + prior pass data): ~500-1000 tokens per file
- Realistic cost: 1,400 files * 700 tokens = 980K tokens
- **Verdict**: Phase 2 alone needs 3-10x its allocated budget

**Phase 3 (20% = 60K tokens for cross-reference):**
- Input: all Phase 1 batch outputs (12 batches * ~5K tokens each = 60K tokens of input alone)
- This consumes the entire Phase 3 budget before any analysis begins
- **Verdict**: Phase 3 cannot fit its own input data

**Phase 4 (15% = 45K tokens for consolidation + validation):**
- Input: all phase summaries = ~40-80K tokens
- 10% spot-check of 3,300 files = 330 files * ~200 tokens each = 66K tokens
- **Verdict**: Phase 4 needs 2-3x its allocation for just the spot-check

### Total realistic budget for "Standard" coverage

| Phase | Set B claims | Realistic minimum |
|-------|-------------|-------------------|
| Phase 0 | 15K | 30-40K |
| Phase 1 | 75K | 400-600K |
| Phase 2 | 105K | 500K-1M |
| Phase 3 | 60K | 120-200K |
| Phase 4 | 45K | 100-150K |
| **Total** | **300K** | **1.15M - 2M** |

**The 300K "Standard" budget is 4-7x too low.** Even the "Deep" scenario at 800K is likely insufficient for comprehensive coverage of a 6,000-file repo.

Set B's reflection document (B3) caught that the proposals underestimated by 2-3x. But the PRD (B4) then claimed to incorporate "realistic" estimates that are STILL 2-3x too low. The correction was acknowledged but not actually applied.

### Subagent spawn overhead

Neither set accounts for the overhead of spawning subagents:

- Each Claude Code subagent spawn includes system prompt (~2-4K tokens)
- Each batch scanner gets: system prompt + batch manifest excerpt + file contents + output schema instructions = ~3-5K tokens of overhead
- For 12 batches: 36-60K tokens in overhead alone
- For Phase 2 with ~10 analyzer batches: another 30-50K tokens
- Total spawn overhead: ~70-120K tokens (23-40% of the 300K budget)

### The prompt overhead nobody counted

Every subagent call includes:
1. The scanner output schema definition (~500 tokens)
2. The classification system definition (~300 tokens)
3. The evidence requirements per tier (~400 tokens)
4. The file-type-specific rules (~300 tokens)
5. Anti-lazy enforcement rules (~200 tokens)

That is ~1,700 tokens of system prompt per subagent call. For 25 total subagent calls across all phases: 42,500 tokens just in repeated system prompt overhead.

---

## Part 3: Implementation Feasibility

### What actually works

1. **Running grep commands via Bash**: Works. This is the one reliable source of ground truth.
2. **Reading file contents**: Works, subject to the 50-line read depth limitation.
3. **Producing Markdown reports**: Works. LLMs are good at generating readable text.
4. **Classifying files as DELETE vs KEEP with a rationale**: Works at a coarse level, though with meaningful error rates.
5. **Detecting credential patterns**: Works with pattern matching (not LLM judgment).

### What is aspirational

1. **Producing schema-compliant JSON across dozens of batches**: Aspirational. Error rates of 15-30% on complex schemas from Haiku are realistic based on published benchmarks and practitioner experience.

2. **Building accurate dependency graphs from LLM-read file snippets**: Aspirational. An LLM reading 50 lines cannot see dynamic imports, webpack aliases, barrel re-exports, or runtime dependency injection. The resulting graph will have major gaps.

3. **Consistent classification across independent subagent instances**: Aspirational. Two Haiku instances given the same file and the same prompt will produce different classifications a non-trivial percentage of the time. There is no consistency guarantee across independently spawned subagents.

4. **Meaningful confidence scores**: Aspirational. LLM-generated confidence scores are tokens, not probabilities. There is no calibration mechanism. A confidence of 0.92 from one subagent and 0.85 from another do not have a meaningful ordinal relationship.

5. **8-field structural profiles at scale**: Aspirational at 300K tokens. Each 8-field profile requires reading the file, running 2-3 grep commands, interpreting results, and producing structured output. Realistically 500-1000 tokens per profile. For 1,400 files, that is 700K-1.4M tokens for Phase 2 alone.

6. **10% spot-check "validation"**: Aspirational as a quality measure. It measures LLM-LLM agreement, not accuracy. Two models can agree on wrong answers systematically (e.g., both miss dynamic imports, both misinterpret barrel exports).

### The context window filling problem

Neither set addresses what happens as the orchestrator accumulates results:

- Phase 0 output: ~10K tokens
- Phase 1 output (12 batches): ~60K tokens
- Phase 2 output (10 batches): ~50K tokens
- The orchestrator needs to read all of this to coordinate Phase 3

By Phase 3, the orchestrator's context window contains 120K+ tokens of accumulated data. This is approaching Claude's context limits. The orchestrator cannot hold all prior results in context while also doing new work.

**Set B's solution is "write to disk."** But then Phase 3 must read the disk artifacts back into context, which means Phase 3's token budget includes re-reading 120K tokens of prior phase outputs. This is not accounted for in the budget.

### What happens with 50,000 files?

Set B mentions monorepo scaling as a risk (F-B-10 in the flaw analysis) but does not resolve it. Let us trace through:

1. `git ls-files` returns 50,000 entries = ~1M characters = ~250K tokens just to read the file list
2. Phase 0 must classify all 50,000 files into tiers = processing 250K tokens of input
3. The batch manifest for 50,000 files is itself ~100K tokens
4. At 12 files per batch (Phase 1), that is 4,167 batches
5. At 3-5K overhead per batch spawn, that is 12-20M tokens in spawn overhead alone

**The system does not scale.** It was designed for a 6,000-file repo and breaks catastrophically on repos 5-10x larger.

---

## Part 4: Scope and Value Challenges

### Is this worth building as specified?

The v2 PRD describes a system that:
- Takes 18-45 minutes to run
- Costs 300K-800K tokens (realistically 1-2M tokens)
- Produces a report that may be 200-2000 lines
- Has an estimated development effort of 30-50 hours (realistically 80-120+ hours)
- Depends on 6 specialized subagents producing schema-compliant JSON

**Alternative 1: "grep scripts + simple classifier" (80% of the value, 5% of the cost)**

```bash
# Find unused files (static analysis)
madge --orphans src/ > orphans.txt

# Find large files
git ls-files | xargs wc -c | sort -rn | head -50 > large-files.txt

# Find old files
git log --diff-filter=A --format='%aI %H' --name-only | ...

# Find .env files with real credentials
grep -rn 'sk-\|ghp_\|AKIA\|BEGIN RSA' .env* > credential-scan.txt

# Find broken doc links
grep -roh '\[.*\](.*\.md)' docs/ | ... > broken-links.txt

# Feed results to a single LLM call for classification and report
```

Total cost: ~5K tokens for the LLM classification, plus negligible compute for grep/madge. Runtime: 30 seconds. Accuracy on deterministic checks: 100%.

**Alternative 2: "One smart pass" (90% of the value, 20% of the cost)**

Run static analysis tools first. Feed their structured output to a single Sonnet call that:
1. Classifies files based on static analysis evidence (not its own reading)
2. Adds subjective assessments where static tools cannot help
3. Produces the final report

Total cost: ~50-100K tokens. Runtime: 5 minutes. Accuracy on import graphs: near-perfect (static analysis). Accuracy on subjective judgments: comparable to the multi-pass system.

### Are users going to read a 2000-line report?

Set B provides `--report-depth summary|standard|detailed` with detailed producing up to 2000 lines. But who is the audience?

- **Repo maintainers** want a prioritized action list: "Delete these 50 files. Archive these 20. Fix these 10 broken links." That is 50 lines.
- **DevOps engineers** want config drift alerts. That is 20 lines.
- **Nobody** wants to read 1,400 8-field JSON profiles.

The detailed report is produced because the system can produce it, not because anyone asked for it. The token cost of producing comprehensive output that nobody reads is waste.

### The complexity of 6 specialized subagents vs 3 generic ones

Set B proposes 6 agents: profiler, scanner, analyzer, comparator, consolidator, validator. The findings document proposed 5 specialized scanners. The v2 PRD settled on 6.

Consider the engineering cost:
- 6 system prompts to write and maintain
- 6 output schemas to define and validate
- 6 * 5 = 30 inter-agent data flow paths to test
- 6 failure modes to handle
- 6 token budgets to calibrate

A simpler architecture with 3 agents (profiler, scanner, reporter) and static analysis tools handling the deterministic work would be:
- 60% less prompt engineering
- 90% fewer inter-agent data flow paths (3 * 2 = 6)
- Easier to debug, test, and maintain
- Comparable output quality (because static tools handle the hard parts)

---

## Part 5: Per-Conflict Attacks

### C-01: Phase/Pass Structure

**Attack on Set A**: Adding a 4th pass to a 3-pass system that already fails to implement its own spec is like adding a 4th floor to a building with cracked foundations. Set A never examines why the existing 3 passes underperform.

**Attack on Set B**: Adding Phase 0 (profiling) and Phase 4 (consolidation) transforms a 3-pass system into a 5-phase pipeline with sequential dependencies. Each added phase is a new failure point. Phase 0 adds 30-60 seconds of latency before any real work begins. If Phase 0 gets the domain detection wrong (which a Haiku model will, on non-standard repo layouts), every subsequent phase inherits the error.

### C-02: Documentation Audit -- Mandatory vs Opt-In

**Attack on Set A**: Making docs audit mandatory on `--pass all` means every audit pays the token cost whether the user cares about docs or not. For a repo with 50 markdown files in a 6,000-file codebase, spending 20% of the budget on docs audit is wildly disproportionate.

**Attack on Set B**: Deferring docs audit to Phase 5 means the primary gap that motivated this entire improvement effort remains unaddressed in v2. The project was justified by "docs are never audited" and the deliverable does not audit docs. This is a credibility problem.

### C-03: Classification System

**Attack on Set A**: Flat categories with 5+ buckets create ambiguity. Is a file that needs its references updated a FLAG or a CONSOLIDATE? What about a file that should be archived AND has broken references? Flat systems cannot express compound states.

**Attack on Set B**: The two-tier system with 4 primaries and 13 qualifiers is over-engineered for what is essentially a cleanup tool. A user does not need to distinguish `MODIFY:fix-references` from `MODIFY:update-content` from `MODIFY:flag:[issue]`. They need to know: "fix this file." The qualifier granularity exists to demonstrate design sophistication, not to serve user needs.

### C-04: Known-Issues Handling

**Attack on Set A**: The registry requires manual maintenance. Who creates the initial entries? Who marks issues as "closed"? Who handles merge conflicts? The 34-item list in the old prompts was hand-curated by a human -- that does not scale to automated tooling. The registry will either be empty (nobody maintains it) or stale (full of resolved issues that still suppress findings).

**Attack on Set B**: Post-hoc dedup only works within a single run. If you run the audit weekly, each run rediscovers the same 50 known issues. The consolidator dedup does not have access to prior runs. Set B's approach explicitly cannot solve the repeated-audit use case that Set A correctly identifies.

### C-05: Priority Ordering

**Attack on Set A**: Starting with "add docs pass + known-issues registry" means the first deliverable adds new complexity without fixing any existing quality problems. The v1 system already has wrong answers (credential false negatives, zero-evidence KEEP). Adding a docs pass on top of wrong answers does not help.

**Attack on Set B**: "Phase 0: Enforce existing spec" sounds disciplined but is actually a 4-6 hour (realistically 15-25 hour) yak shave before any user-visible improvement. The spec promises 5 categories, coverage tracking, checkpointing, evidence-gated classification, AND spot-check validation. Implementing all of these before adding a single new feature means the first deliverable is "the tool now does what it always claimed to do" -- which is a hard sell to stakeholders expecting improvement.

### C-06: Subagent Architecture

**Attack on Set A**: "Reuse existing agents" is not a plan. It is a hope. The existing agents produce 12 profiles for 6,000 files. Reusing them will produce 12 profiles again.

**Attack on Set B**: 6 named agents with model assignments sounds prescriptive, but the names are aspirational labels. An "audit-comparator (Sonnet)" is just a Sonnet model with a system prompt. It does not have special capabilities. The specialization comes from the prompt, not from the agent being "specialized." Calling it a "comparator" does not make it better at comparing things.

### C-07: Evidence Requirements -- Uniform vs Tiered

**Attack on Set A**: Uniform evidence for all KEEP files means spending 175K-585K additional tokens verifying files in `node_modules/`, `generated/`, and `assets/`. This is obviously wasteful.

**Attack on Set B**: The tier system depends on Phase 0 getting tier assignments right. If a Haiku model misclassifies `infrastructure/deploy-critical.sh` as Tier 3 (standard) because it is in a non-standard path, that critical file gets relational annotation instead of full 3-field evidence. The tier system is only as good as the classifier that assigns tiers.

### C-08: Budget and Cost Estimates

**Attack on Set A**: Having no budget model is not a philosophical choice -- it is a spec deficiency. You cannot build a system with bounded resource consumption if you do not know what the resources cost.

**Attack on Set B**: As shown in Part 2, the "realistic" estimates in B4 are still 4-7x too low. The budget system is well-designed in principle (graceful degradation is a good pattern) but the actual numbers are wrong. A user running `--budget 300000` expecting "Standard" coverage will get something closer to "Minimal."

### C-09: ARCHIVE as a Classification

**Attack on Set A**: ARCHIVE as a top-level category alongside DELETE creates confusion. "Should I archive this or delete this?" is the same kind of judgment call the tool is supposed to help with. Adding a third option makes the decision harder, not easier.

**Attack on Set B**: `DELETE:archive-first` implies the file SHOULD be deleted but SHOULD FIRST be archived. This is two actions disguised as one classification. The user must: (1) copy to archive, (2) verify the copy, (3) delete the original. Calling this "DELETE" undersells the work involved.

### C-10: Cross-Reference / Dependency Graph

**Attack on Set A**: Not building a dependency graph means the audit cannot detect cross-boundary dead code. This is the same gap the v1 system has. The "compare, don't just catalog" intent from the old prompts specifically demanded this capability.

**Attack on Set B**: Building a dependency graph from LLM-read file snippets is the wrong approach. Static analysis tools (madge, pydeps, ts-prune) build accurate graphs in seconds. An LLM reading 50 lines of a file and guessing its imports is strictly inferior. The graph will have false edges, missing edges, and the confidence scoring (">3 hops = INVESTIGATE") is arbitrary.

### C-11: Spot-Check Validation

**Attack on Set A**: No validation means no quality signal. The user has no way to know if the audit results are trustworthy.

**Attack on Set B**: LLM-on-LLM validation is a consistency check, not an accuracy check. Both models share the same systematic biases (miss dynamic imports, misinterpret barrel exports, hallucinate grep results). An "85% agreement rate" could mean both models are consistently wrong on 15% of files and consistently share the same errors on the other 85%.

### C-12: Phase 0 / Pre-Audit Profiling

**Attack on Set A**: Skipping profiling means every scanner gets the same treatment regardless of domain. This is why v1 produces only 12 profiles.

**Attack on Set B**: A Haiku model spending 30-60 seconds to profile a repo is doing pattern matching on directory names. It will misclassify non-standard repo layouts (monorepos with unconventional structures, repos using src/ for both frontend and backend, repos with infrastructure code inside application directories). The profile is only as good as the Haiku model's assumptions about repo structure conventions.

### C-13: Recommendation Category Count

**Attack on Set A**: 5+ flat buckets are not composable. What is the category for "delete this file but first update the 3 files that reference it"? FLAG? CONSOLIDATE? Both?

**Attack on Set B**: 4 primaries * 13 qualifiers = 52 possible classifications. This is too many. Users will not learn the taxonomy. The report will show categories like `MODIFY:consolidate-with:frontend/components/ButtonOld.tsx` which are so specific they are effectively unique per file, making aggregation meaningless.

### C-14: Batch Decomposition

**Attack on Set A**: No batch strategy means files are processed arbitrarily. Two files in the same directory might be examined by different scanners with no context sharing.

**Attack on Set B**: Dynamic batch generation in Phase 0 adds complexity and a new failure mode. If the batch manifest is wrong (files assigned to wrong domains, batches too large for context windows), every subsequent phase inherits the error. Static batch assignment (by directory) would be simpler and equally effective.

### C-15: Spec-Implementation Gap

**Attack on Set A**: Building a new PRD without checking what the old PRD promised is architectural negligence. This is the single most damaging oversight in Set A.

**Attack on Set B**: Identifying the gap is valuable. But "Phase 0: enforce existing spec" requires implementing 5 substantial features (5 categories, coverage tracking, checkpointing, evidence-gated classification, spot-check) before any new work. If the gap exists because these features are HARD to implement (not because nobody thought of them), then "just implement them" is not a helpful directive. The root cause analysis should ask: WHY were they not implemented? Resource constraints? Technical infeasibility? Prompt limitations?

### C-16: Coverage Tracking

**Attack on Set A**: "REMAINING / NOT_YET_AUDITED" without thresholds is a compliance checkbox, not a quality mechanism.

**Attack on Set B**: The thresholds (100/95/80/60%) are aspirational. As shown in the budget arithmetic, the "Standard" 300K budget cannot achieve 95% coverage on Tier 2 files with meaningful evidence depth. The thresholds will permanently show WARN/FAIL, training users to ignore them.

### C-17: Output Format

**Attack on Set A**: Markdown intermediate outputs cannot be programmatically validated or consumed by downstream phases. This is why Pass 4 cannot build on Pass 1-3 data.

**Attack on Set B**: JSON intermediate outputs from Haiku models will have high error rates. Every malformed JSON file breaks the pipeline. The system needs a robust JSON parser with error recovery, which neither set specifies.

### C-18: Quality Gate on Spot-Check Failure

**Attack on Set A**: Not addressed. No quality signal at all.

**Attack on Set B**: A "warning banner" that says "agreement rate was 82%, below the 85% threshold" is not actionable. What is the user supposed to do? Re-run the audit? Manually verify everything? The warning creates anxiety without providing a resolution path.

### C-19: .env Handling

**Attack on Set A**: A key-presence matrix is a nice-to-have that existing tools (dotenv-linter) handle better.

**Attack on Set B**: Reading actual `.env.production` content is correct. But the credential patterns (`sk-*`, `ghp_*`, `AKIA*`) are a static list. New credential formats (Anthropic API keys `sk-ant-*`, Vercel tokens, Supabase keys) will be missed unless the pattern list is regularly updated.

### C-20: Progressive Depth

**Attack on Set A**: Not specifying depth means relying on default LLM behavior, which varies by context window pressure and file content.

**Attack on Set B**: Signal-triggered depth (50 lines default, full on trigger) creates inconsistent analysis depth across files. A 299-line file gets 50 lines read; a 301-line file gets a full read. The boundary is arbitrary and creates cliff effects.

### C-21: Checkpointing

**Attack on Set A**: Pass-level checkpointing means losing an entire pass of work on interruption.

**Attack on Set B**: Batch-level checkpointing requires reliable JSON serialization after every batch. If the checkpoint write fails (disk full, permissions, malformed JSON), the system loses progress silently. Neither set specifies checkpoint validation or recovery-from-corrupt-checkpoint logic.

### C-22: Claim Spot-Check Scope

**Attack on Set A**: 3-5 claims per doc across all sampled docs is expensive and many claims will be unfalsifiable ("this architecture supports scalability").

**Attack on Set B**: 3 claims per doc only for API-reference and setup-guide categories misses the highest-value target: architecture documents that make verifiable claims about system structure ("the frontend communicates with the backend via port 8102"). These are the claims most likely to be stale and most dangerous when wrong.

---

## Part 6: What Both Advocates Will Miss

### 1. The hybrid architecture blind spot

Neither set proposes combining static analysis tools with LLM judgment. This is the most obvious architectural improvement and neither analysis considers it. Run `madge`, `grep`, `git log`, and `find` first. Feed their structured, deterministic output to the LLM for classification and reporting. This would:
- Reduce token cost by 60-80%
- Improve accuracy on import graphs from ~70% (LLM guess) to ~95% (static analysis)
- Reduce runtime from 18-45 minutes to 2-5 minutes
- Make the dependency graph feature actually reliable

### 2. The "same repo, different run" consistency problem

Neither set addresses run-to-run consistency. If you run the audit twice on the same repo without changes, do you get the same results? Almost certainly not, because LLM outputs are non-deterministic. This means:
- Diff between two audit runs is meaningless (you cannot tell what changed vs. what the LLM classified differently)
- Trend tracking ("are we improving?") is impossible
- Regression detection ("did this merge introduce cleanup debt?") is unreliable

**No amount of schema hardening fixes non-determinism.** The only fix is grounding classifications in deterministic evidence (static analysis output).

### 3. The user feedback loop is missing

Both sets design a one-shot tool. The audit runs, produces a report, and is done. Neither proposes:
- User correction: "You classified Button.tsx as DELETE but it is actually used via dynamic import" (feeding corrections back)
- Learning from prior runs: "Last time you flagged these 50 files and the user kept 48 of them" (improving future accuracy)
- Incremental audit: "Only scan files changed since the last audit" (reducing cost for repeated use)

Without a feedback loop, the tool makes the same mistakes every time.

### 4. The false precision trap

Both sets design for precision (8-field profiles, 13 qualifiers, 4 risk tiers, confidence scores to 2 decimal places) when the underlying LLM judgments have wide error bars. This creates a dangerous mismatch between the precision of the output format and the accuracy of the underlying data.

A user seeing `{"classification": "DELETE:standard", "confidence": 0.94, "grep_result_count": 0}` will trust this classification because it looks precise and evidence-backed. But the grep may have missed aliased imports, the confidence is a generated token not a probability, and the file may be loaded dynamically.

**Simpler, less precise output with honest uncertainty would be more trustworthy.**

### 5. The maintenance burden is unaddressed

Both sets design an initial system but neither addresses ongoing maintenance:
- Who updates the credential patterns when new services launch?
- Who updates the dynamic import patterns when new frameworks emerge?
- Who recalibrates the token budget estimates as models change?
- Who maintains the 6 system prompts as the tool evolves?
- Who updates the `audit.config.yaml` defaults as conventions shift?

A tool with 6 specialized agents, 12+ field schemas, 4 tier classifications, and 13 qualifiers has a high maintenance surface area. Every model version update potentially changes output formatting, requiring prompt re-engineering.

### 6. The competitive landscape is ignored

Neither set benchmarks against existing tools:
- **SonarQube**: Static analysis with technical debt tracking
- **CodeClimate**: Automated code review with maintainability scoring
- **Snyk**: Security vulnerability detection
- **Dependabot**: Dependency freshness tracking
- **trunk.io**: Automated code quality checking

What does this LLM audit provide that these tools do not? The answer is probably: subjective assessment of "should this file exist?" and natural-language report generation. Everything else (import graphs, dead code, credential scanning, link checking) is done better by purpose-built tools.

### 7. The "read-only" constraint is a bigger problem than either set admits

Both sets emphasize "this is a read-only audit." But the highest-value output of a cleanup audit is not the report -- it is the cleanup itself. A read-only tool that produces a 400-line report of recommendations creates work for humans. A tool that produces a `cleanup.sh` script with safe, reversible deletion commands (with git as the undo mechanism) would be 10x more valuable.

Neither set explores why the tool must be read-only, or whether a "read-only by default, `--execute` for brave users" mode would better serve the use case.

---

## Part 7: Recommended Guard Rails

For ANY version of this spec to succeed, the following must be true:

### Guard Rail 1: Ground truth must come from tools, not LLMs

Import graphs must come from static analysis tools (`madge`, `pydeps`, `grep -r`). File reference counts must come from `grep`. Last commit dates must come from `git log`. File sizes must come from `stat`. The LLM's role is interpretation and judgment, not data gathering.

**Test**: Can every factual claim in the audit output be verified by running a bash command? If not, the claim is LLM speculation and should be labeled as such.

### Guard Rail 2: Token budgets must be empirically validated

Before finalizing any budget numbers, run the system on 3 real repositories of different sizes (500, 5000, 50000 files) and measure actual token consumption per phase. Set budgets based on measurements, not estimates.

**Test**: Run the audit 3 times on the same repo. If token consumption varies by more than 20%, the budget model is unreliable.

### Guard Rail 3: Schema compliance must be measured, not assumed

Before shipping, measure the actual JSON schema compliance rate of each agent model on representative inputs. If compliance is below 90%, either simplify the schema or switch to a more capable model for that agent.

**Test**: Run 100 batch classifications through Haiku with the proposed schema. Measure the percentage that parse as valid JSON and conform to the schema. If below 90%, the system is unreliable.

### Guard Rail 4: The system must degrade to a useful minimum

If every subagent fails, the system should still produce SOMETHING useful -- even if it is just a file list with `git log` metadata and `grep` reference counts. The minimum viable output must not depend on any LLM producing correct structured output.

**Test**: Disconnect all LLM subagents. Does the system still produce a useful file inventory? If not, the architecture is too dependent on LLM reliability.

### Guard Rail 5: Output must honestly represent its limitations

Every audit report must include:
- Which files were examined vs skipped
- Which evidence is from deterministic tools (grep, git) vs LLM judgment
- That confidence scores are not calibrated probabilities
- That the dependency graph may miss dynamic imports
- The actual token cost and budget utilization

**Test**: Does the report contain a "Limitations" section that a skeptical engineer would find honest?

### Guard Rail 6: The system must handle the cold path gracefully

First-run experience without any config file, prior audit results, or known-issues registry must produce useful output. The system must never require setup ceremony before being useful.

**Test**: Clone a random GitHub repo. Run the audit with zero configuration. Is the output useful?

### Guard Rail 7: Complexity must be justified by user value

Every feature that adds complexity (additional agents, schema fields, classification qualifiers, tier levels) must trace to a concrete user story. If the user story is "as a developer, I want to know which files to delete," then 4 primary categories with 13 qualifiers is over-serving that story.

**Test**: For each schema field/qualifier/tier, identify one user action it enables. If no action is enabled, the feature is unnecessary.

### Guard Rail 8: The development effort must be estimated from implementation, not spec

The PRD estimates 30-50 hours. Realistic effort for prompt engineering, testing, and iterating 6 agents with structured output schemas against real repositories is 120-200 hours. Budget accordingly or reduce scope.

**Test**: Implement one phase completely (e.g., Phase 1 surface scan with schema validation). Measure actual hours. Extrapolate to full system. If extrapolated effort exceeds available budget, reduce scope.

---

## Summary Verdict

Both analysis sets contain valuable insights. Set B is architecturally superior. Neither set is ready to become a spec without addressing the fundamental issues raised here:

1. **Use static analysis tools for deterministic work.** LLMs should judge, not measure.
2. **The token budget arithmetic is wrong by 4-7x.** Either increase budgets dramatically or reduce scope dramatically.
3. **JSON schema compliance from Haiku is an unvalidated assumption.** Measure it before depending on it.
4. **Confidence scores from LLMs are not probabilities.** Stop treating them as such.
5. **The system does not scale past ~10,000 files.** Monorepo support requires fundamental architecture changes.
6. **A hybrid architecture (static tools + LLM judgment) would be cheaper, faster, and more accurate than an all-LLM approach.**
7. **Run-to-run consistency is impossible without deterministic grounding.** The tool cannot support trend tracking or regression detection as designed.
8. **The maintenance burden of 6 specialized agents with complex schemas is significant and unaddressed.**

The strongest path forward: build a thin LLM layer over static analysis tools, not a thick LLM pipeline that reinvents static analysis poorly.

---

*Devil's Advocate analysis complete | 2026-02-20*
*Attack surface: 7 fundamental design attacks, full budget arithmetic, 22 per-conflict attacks, 7 unique blind spots, 8 guard rails*
