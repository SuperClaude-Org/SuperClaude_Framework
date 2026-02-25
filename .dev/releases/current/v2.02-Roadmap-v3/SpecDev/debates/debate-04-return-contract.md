# Debate 04: Return Contract Fix (Solution #4)

**Date**: 2026-02-22
**Orchestrator**: claude-sonnet-4-6 (debate orchestrator mode)
**Subject**: Solution #4 — File-Based Return Contract Data Flow
**Root Cause Addressed**: RC4 (Return Contract Data Flow, Rank 4 of 5, combined score 0.75)
**Fix Reference**: Fix 3 from ranked-root-causes.md minimal fix set

---

## Context Summary

Solution #4 proposes establishing a file-based data transport mechanism for the return contract between sc:adversarial (producer) and sc:roadmap (consumer). The current state defines 6 structured fields in the return contract schema but provides zero transport mechanism — no file write instruction in sc:adversarial, no file read instruction in sc:roadmap. The recommended implementation writes `return-contract.yaml` to `<output-dir>/adversarial/` as a mandatory final step, following the sc:cleanup-audit fan-out/fan-in precedent.

The debate evaluates whether this solution is the correct, complete, and feasibly implementable fix for RC4.

---

## Advocate FOR: File-Based Return Contract

### Opening Statement

Solution #4 is the most architecturally sound fix in the entire minimal fix set. Unlike Fix 1 (which requires infrastructure decisions about the Skill tool ecosystem) and Fix 2 (which requires extensive specification rewrites with uncertain behavioral consequences), Fix 4 is a narrow, additive, verifiable change that directly closes a documented structural gap.

**The problem is concrete and binary.** Six contract fields are defined. Zero transport instructions exist. The solution adds exactly one write instruction and one read instruction. This is the smallest possible fix surface for a clearly bounded problem.

### Evidence Points FOR

**1. The sc:cleanup-audit precedent validates the entire approach.**
The only working inter-agent data flow in this codebase is file-based. sc:cleanup-audit's subagents write structured batch reports to `.claude-audit/`, and the orchestrator reads and merges them. Solution #4 applies the identical pattern. This is not a novel design decision — it is an extension of an already-working architecture. The risk of "will this work?" is already answered by the existing codebase.

**2. The failure mode is binary and detectable.**
A file either exists or it does not. If `return-contract.yaml` is present, the data was written. If absent, the pipeline crashed before completion. This eliminates the silent failure modes that plague text-parsing approaches (Option B) and multi-file convention approaches (Option C). The solution converts an ambiguous failure (no data) into an explicit failure (file missing, reason reportable).

**3. The schema is already designed — the fix is purely about transport.**
The 6 fields are defined in sc:adversarial SKILL.md. The consumption logic is implemented in `refs/adversarial-integration.md` (status routing, convergence thresholds, frontmatter population). The fix bridges an already-designed contract — it does not require schema design from scratch. This dramatically reduces implementation risk.

**4. The blast radius is minimal and purely additive.**
Two files change: sc:adversarial SKILL.md (add write instruction) and sc:roadmap refs/adversarial-integration.md (add read instruction). No existing behavior is modified. No schema migration is needed. No downstream skills are broken. The `base_variant` field addition resolves an existing schema discrepancy (field expected by consumer, absent from producer definition) without architectural impact.

**5. The `schema_version` field provides safe evolution.**
By including a versioned schema from the start, Solution #4 avoids the most common failure mode of inter-process contracts: breaking changes that have no upgrade path. Consumers are instructed to warn (not abort) on unknown versions. This is the correct design for a file format that will likely need to extend over time.

**6. The fix is independently verifiable.**
After implementation, a developer can invoke sc:adversarial, then `cat <output-dir>/adversarial/return-contract.yaml` and verify the contract was written correctly. No integration harness, no mock framework, no session replay required. The artifact persists across session crashes, enabling post-mortem debugging.

**7. The solution correctly handles the failed pipeline case.**
The "write even on failure" requirement with explicit sentinel values (`merged_output_path: ""`, `convergence_score: 0.0`, `unresolved_conflicts: -1`) is precise engineering. It distinguishes three states: pipeline crashed (file absent), pipeline ran and failed (file present, `status: failed`), and pipeline succeeded (file present, `status: success`). This three-state model supports reliable orchestration logic.

### Closing FOR

The case for Solution #4 is essentially uncontested on architectural grounds. File-based contracts are the only proven inter-agent data flow in this codebase. The schema is already designed. The fix is additive. The failure modes are detectable. The blast radius is two files. The only legitimate debates are about (a) whether RC4 is critical enough to fix now and (b) whether the solution is complete enough relative to edge cases. Those are addressed in the Against position below.

---

## Advocate AGAINST: Objections and Risks

### Opening Statement

Solution #4 is technically correct but strategically premature and incomplete in ways the solution document underplays. Four objections deserve serious consideration: (1) the latency position of RC4 in the causal chain, (2) the dependency on Fix 1 for any testability, (3) the agent compliance assumption that is central to the whole solution, and (4) edge cases around partial pipeline failure that the solution handles with sentinel values but does not fully reason through.

### Evidence Points AGAINST

**1. RC4 is a tertiary latent defect, not an active cause of the observed failure.**

The ranked-root-causes.md analysis is explicit: "this is a latent defect — it would surface once RC1 and RC2 are fixed, even if never the active cause of the observed failure." The observed failure was caused by RC1 (no Skill tool invocation mechanism) compounding with RC5 (Claude's rational fallback behavior). RC4 never had a chance to manifest because sc:adversarial was never invoked. Fixing RC4 before RC1 is complete delivers zero user-observable value. The fix order recommended in the solution document itself (`Fix 1 -> Fix 3 -> Fix 2`) acknowledges this — but that ordering creates a testing gap: Fix 3 cannot be validated until Fix 1 is applied, which means Fix 3 ships untested.

**2. The entire solution depends on agent instruction compliance — an assumption that is stated but not validated.**

The core requirement is: "sc:adversarial MUST write the return contract to disk as its final step, regardless of pipeline outcome." But sc:adversarial is not a deterministic program with a guaranteed execution path. It is a skill whose steps are executed by a language model following natural-language instructions. The solution assumes Claude will:
- Remember to write the YAML file after completing the 5-step pipeline
- Write it even when status is "failed"
- Use the correct field names and types
- Write it LAST (after all pipeline artifacts), not at an arbitrary point

None of these behaviors are tested in the current codebase. The sc:cleanup-audit precedent does not directly validate these assumptions — cleanup-audit's subagents write batch reports (their primary task output), not a structured handoff contract at pipeline termination. The compliance pattern is different in kind.

**3. Sentinel values for failed states introduce semantic ambiguity.**

The solution uses `unresolved_conflicts: -1` as a sentinel for "conflict counting was not reached." This is a common but imprecise pattern. It conflates two distinct states: (a) the pipeline attempted conflict counting and produced a valid count of -1 (logically impossible but structurally indistinguishable) and (b) the pipeline aborted before conflict counting. A better design would use `null` (YAML null) or a separate `failure_stage` field indicating which pipeline step failed, enabling the consumer to distinguish early failures from late failures without sentinel magic.

Similarly, `merged_output_path: ""` (empty string) for a non-attempted merge is ambiguous. An empty string could also represent a merge that was attempted but produced no output path due to a separate bug. A null value or an `attempted` boolean field would be cleaner.

**4. The solution is silent on concurrent invocations.**

The data flow diagram shows a clean sequential flow: sc:roadmap invokes sc:adversarial, waits for completion, reads the contract. But sc:roadmap's Wave 2 description suggests multiple variant generation cycles may run in parallel. If two sc:adversarial invocations write to the same output directory, `return-contract.yaml` will be overwritten by the second invocation, and the consuming orchestrator may read inconsistent data. The solution does not address the concurrency scenario or define how the output directory should be namespaced per invocation.

**5. Schema version 1.0 at initial release is architecturally premature optimism.**

Including a `schema_version: "1.0"` field is pragmatically good but creates an implicit stability promise. Once this schema is in production, consumers will check for `schema_version: "1.0"` and warn on other values. Any field addition or type change requires a version bump and handling in consumer code. The solution says consumers should "warn (not abort) on unknown versions" — but this guidance is in the producer spec, not in the consumer code in `refs/adversarial-integration.md`. The consumer may silently ignore a version 1.1 contract and miss new fields, producing incorrect behavior without an error signal.

**6. The "base_variant field was missing" finding reveals an underlying schema governance problem that is not solved by this fix.**

The solution notes that `base_variant` is present in the consumer's expected fields (sc:roadmap's `adversarial-integration.md`, line 152) but absent from the producer's schema definition (sc:adversarial SKILL.md). This discrepancy was introduced at some point and went undetected. Fix 4 adds `base_variant` to the producer schema — but it does not address the process failure that allowed the discrepancy to exist. If the schema is maintained in two places (producer definition + consumer expectation), future changes will likely diverge again. A single canonical schema definition (e.g., a shared schema block referenced by both skills) would prevent recurrence.

### Closing AGAINST

Solution #4 is the right fix for the right problem. The objections are not fatal — they are precision concerns about implementation completeness and strategic sequencing. The sentinel value ambiguity is real but minor. The concurrency blind spot is low-probability but unaddressed. The schema governance concern is structural and will likely resurface. The most significant concern is the untestable-until-Fix-1-ships nature of this fix, which means it ships with lower validated confidence than the 0.88 score suggests.

---

## Rebuttal

### FOR Rebuts AGAINST

**On RC4's latent vs. active status**: The Against position correctly identifies that RC4 was not the active failure cause. However, this does not diminish the value of fixing it proactively. If Fix 1 and Fix 2 are applied without Fix 3, the system will gain the ability to invoke sc:adversarial but will still have no way to transport results back to the orchestrator. The failure mode will shift from "invocation never happens" to "invocation happens but data is lost." Fix 3 is the closing step of a three-part repair sequence — its latent status makes it third in priority, not optional.

**On agent compliance**: The concern is valid but overstated. The sc:cleanup-audit precedent is not identical, but it demonstrates that Claude can reliably execute "write a structured file as a final step" instructions when those instructions are prominent and explicit. The solution places the write instruction in a clearly named "Write Timing" section with mandatory language ("MUST write"). This is exactly how sc:cleanup-audit's write instructions are structured. The risk is not zero but is mitigated by clear instruction design.

**On sentinel values**: The `-1` sentinel for `unresolved_conflicts` is a fair criticism. Using YAML null (`unresolved_conflicts: ~`) would be cleaner and avoid the semantic confusion. This is an implementation detail that can be refined without changing the overall solution design. Similarly, adding a `failure_stage` field would improve debuggability. These are additive improvements, not blockers.

**On concurrency**: The concurrency scenario requires sc:roadmap to invoke sc:adversarial multiple times to the same output directory simultaneously. Review of the Wave 2 specification shows that parallel invocations are not part of the current design — Wave 2 runs a single adversarial comparison. If parallel invocations become a future requirement, output directory namespacing is the correct solution, and it can be added without changing the contract schema.

**On schema governance**: The base_variant discrepancy is a valid governance finding. A shared schema definition would reduce divergence risk. However, in a markdown-based skill system without a formal schema registry, the current approach (define in producer, reference in consumer) is pragmatically reasonable. Adding a comment in both files pointing to the canonical definition location would reduce future drift.

### AGAINST Rebuts FOR

**On precedent**: The FOR position overstates the directness of the sc:cleanup-audit precedent. Cleanup-audit subagents write their primary output to files — that is their job. sc:adversarial is being asked to write a structured contract file in addition to its primary output (the merged roadmap). The compliance expectation is similar but not identical. An agent that successfully generates a merged roadmap but forgets the return contract file is a plausible failure mode not captured in the precedent.

**On blast radius**: The two-file assessment is accurate for the fix itself but does not account for the fix's dependency: Fix 1 must ship first, and Fix 1 touches the same files (roadmap.md and SKILL.md) for the allowed-tools change. Coordinating two fixes to the same files in sequence increases integration risk relative to the isolated blast radius analysis.

**On binary failure mode**: The binary signal (file present/absent) is only binary for the transport mechanism. The pipeline status field (`success/partial/failed`) reintroduces gradation. sc:roadmap's status routing logic (the "existing status routing logic remains unchanged" section) must handle all three values correctly. The solution defers to existing routing logic without verifying that logic is correct for all status values, particularly `partial`.

---

## Scoring Matrix

| Dimension | Weight | FOR Score | AGAINST Score | Adjudicated Score | Weighted Score |
|-----------|--------|-----------|---------------|-------------------|----------------|
| Root cause coverage | 0.25 | 0.85 | 0.65 | 0.75 | 0.1875 |
| Completeness | 0.20 | 0.80 | 0.55 | 0.68 | 0.1360 |
| Feasibility | 0.25 | 0.90 | 0.75 | 0.83 | 0.2075 |
| Blast radius | 0.15 | 0.90 | 0.80 | 0.85 | 0.1275 |
| Confidence | 0.15 | 0.88 | 0.65 | 0.77 | 0.1155 |
| **Composite** | **1.00** | | | | **0.774** |

### Dimension Rationale

**Root cause coverage (adjudicated: 0.75)**
Solution #4 directly addresses RC4 as its primary target and does so completely: the schema is defined, the write instruction is specified, the read instruction is specified, and the failure modes are enumerated. Score is not higher because RC4 is rank 4 of 5 (latent defect, combined score 0.75), meaning this fix addresses a tertiary cause. FOR argued 0.85 based on the fix's completeness relative to RC4; AGAINST argued 0.65 based on RC4's low active causal weight. Adjudicated at 0.75, reflecting the fix's technical completeness against a lower-priority target.

**Completeness (adjudicated: 0.68)**
The solution covers the happy path and failure paths well. Deductions for: (1) sentinel value ambiguity (`-1` for unresolved_conflicts, `""` for missing paths) that creates potential semantic confusion; (2) absence of concurrency analysis for multi-invocation scenarios; (3) no validation that the consumer's "existing status routing logic" correctly handles all three status values; (4) schema governance gap not structurally resolved. FOR argued 0.80; AGAINST argued 0.55. Adjudicated at 0.68 — the completeness concerns are real but are implementation-detail level, not design-level.

**Feasibility (adjudicated: 0.83)**
The implementation is straightforward: add one write section to sc:adversarial SKILL.md, add one read section to refs/adversarial-integration.md. No code changes, no schema migrations, no infrastructure dependencies. The dependency on Fix 1 for testability is real but does not block implementation. The agent compliance risk is manageable with clear, prominent instruction wording. FOR argued 0.90; AGAINST argued 0.75. Adjudicated at 0.83 — high feasibility with a moderate untestable-until-Fix-1 qualification.

**Blast radius (adjudicated: 0.85)**
Two files modified, purely additive changes, no existing behavior altered, no downstream skills affected. The coordination risk with Fix 1 (both fixes touch overlapping files) is low because they modify different sections. Positive downstream impact: future skills that consume sc:adversarial gain a documented, versioned contract to program against. FOR argued 0.90; AGAINST argued 0.80. Adjudicated at 0.85 — minimal blast radius with a small coordination overhead flag.

**Confidence (adjudicated: 0.77)**
The file-based transport mechanism is technically sound and precedent-backed. Confidence is reduced by: (1) inability to test Fix 3 until Fix 1 ships, meaning the 0.88 self-reported confidence assumes a testing context that does not yet exist; (2) agent compliance with mandatory write instructions is assumed, not empirically validated; (3) the base_variant discrepancy reveals underlying schema governance processes that may produce future drift. FOR argued 0.88; AGAINST argued 0.65. Adjudicated at 0.77 — genuine confidence in the approach, appropriately reduced for the validation dependency.

---

## Fix Likelihood

**Recommendation: IMPLEMENT with minor refinements**

**Composite score**: 0.774 / 1.000

**Likelihood to fix RC4**: HIGH (0.83)

The solution will resolve the return contract data flow problem with high probability when both Fix 1 and Fix 3 are applied together. The file-based transport mechanism is architecturally sound, precedent-backed, and correctly designed for the three-state pipeline outcome model.

**Likelihood to introduce new defects**: LOW (0.12)

Additive changes to markdown skill files carry minimal regression risk. The primary new-defect vector is agent non-compliance with the write instruction on failure paths, which is detectable via file-existence checking.

**Recommended refinements before implementation**:

1. Replace `unresolved_conflicts: -1` sentinel with YAML null (`~` or `null`) to avoid semantic confusion. Update consumer validation to handle null as a valid "not reached" value.
2. Replace `merged_output_path: ""` sentinel with YAML null for the same reason.
3. Add a `failure_stage` field (optional, null on success) indicating which pipeline step triggered abort, enabling precise debugging of failed runs.
4. Add a comment in both producer and consumer spec pointing to the other location where the schema is referenced, reducing future governance drift.
5. Verify that sc:roadmap's existing `partial` status routing logic in `refs/adversarial-integration.md` handles the specific partial-state field values (non-zero `unresolved_conflicts`, low `convergence_score`) before implementing Fix 3.

---

## Unresolved Concerns

### Priority 1: Agent Compliance on Failure Paths (Medium Risk)

**Description**: The "write return-contract.yaml even when status is failed" requirement is critical for distinguishing pipeline crash from pipeline failure. However, this instruction is harder to enforce than success-path writes because on the failure path, the agent may abort before reaching the write step, or may prioritize error reporting over structured output.

**Why unresolved**: Agent compliance with end-of-pipeline instructions has no test coverage in the current framework. The sc:cleanup-audit precedent validates success-path file writes by subagents, not failure-path mandatory writes by a terminating skill.

**Suggested investigation**: Add a negative test case in the test strategy: invoke sc:adversarial with inputs designed to trigger early abort (e.g., malformed spec file) and verify that `return-contract.yaml` is still written with `status: failed`.

### Priority 2: Concurrency and Output Directory Namespacing (Low Risk, Future Concern)

**Description**: If sc:roadmap evolves to invoke sc:adversarial in parallel for multiple spec comparisons, multiple instances writing to the same `<output-dir>/adversarial/return-contract.yaml` will produce race conditions and data loss.

**Why unresolved**: The current Wave 2 design does not specify parallel invocations, but the solution document does not explicitly prohibit them or define isolation guarantees.

**Suggested investigation**: Add a note in both skill SKILL.md files that output directories must be unique per invocation. If sc:roadmap eventually supports parallel adversarial comparisons, the output directory parameter must include an invocation-unique component (e.g., `<output-dir>/adversarial-<spec-pair-hash>/`).

### Priority 3: Schema Governance Process (Structural Gap)

**Description**: The `base_variant` field discrepancy (present in consumer expectations, absent from producer schema) was introduced at some point without detection. Fix 3 corrects this specific instance but does not prevent recurrence.

**Why unresolved**: A single canonical schema definition would prevent producer-consumer drift, but the current skill system has no schema registry mechanism. Implementing one is out of scope for Fix 3.

**Suggested mitigation**: Both files should contain a comment: `# Schema definition: src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section`. Changes to one must be mirrored to the other. This is a process control, not a technical control, and is therefore imperfect.

### Priority 4: Partial Status Routing Validation (Implementation Risk)

**Description**: The solution adds a read step and schema validation before the existing status routing logic in `refs/adversarial-integration.md`, explicitly leaving the routing logic "unchanged." The routing logic was written against an assumption of how partial contract data would look, but it has never been exercised with real data.

**Why unresolved**: Validating the routing logic requires running the adversarial pipeline with a known partial-outcome input, which requires Fix 1 first. Until Fix 1 ships, the routing logic's correctness for `partial` status values remains unverified.

**Suggested mitigation**: Before merging Fix 3, conduct a static review of the `partial` routing branch in `refs/adversarial-integration.md` against the solution's field value definitions for partial status (specifically: `convergence_score` in the 0.60-1.00 range, non-zero `unresolved_conflicts`, valid `merged_output_path`).

---

## Summary Verdict

Solution #4 is technically correct, architecturally sound, and well-scoped. It is the right implementation of the right fix for a real structural deficiency. The debate surfaces four concerns — agent compliance on failure paths, concurrency blind spot, schema governance process gap, and partial status routing validation — none of which are blockers. The composite score of 0.774 reflects high confidence with appropriate recognition that this fix is tertiary in the causal chain, ships untestable until Fix 1 is applied, and carries minor but real implementation risks that can be mitigated through the refinements listed above.

**Implement Fix 3 after Fix 1 is confirmed working. Apply the five recommended refinements at implementation time. Treat the four unresolved concerns as post-implementation verification tasks, not pre-implementation blockers.**

---

*Debate conducted 2026-02-22. Orchestrator: claude-sonnet-4-6.*
*Inputs: solution-04-return-contract.md, ranked-root-causes.md.*
*Output: debate-04-return-contract.md.*
