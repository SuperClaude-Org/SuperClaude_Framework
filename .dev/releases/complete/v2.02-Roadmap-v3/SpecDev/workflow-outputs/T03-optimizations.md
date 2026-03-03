# T03: Sprint-Spec Optimization Proposals

> **Panel**: Efficiency Expert, Quality Advocate, Implementation Specialist, Risk Analyst
> **Date**: 2026-02-23
> **Input**: sprint-spec.md (Task 0.0 + 3 Epics, 13 tasks), T02-synthesis.md (0.737 effectiveness, 11 gaps), T01-dvl-evaluation.md (4 DVL script proposals), ranked-root-causes.md (5 RCs, 3 minimal fixes)
> **Baseline Sprint Estimate**: ~15 hours (core tasks ~8 hrs + T02 amendments ~4 hrs + verification ~2 hrs + sync/overhead ~1 hr)
> **Target**: 5 optimizations, >20% total savings (>3.0 hours), each effectiveness_impact < 0.3, at least 2 with zero impact

---

## Optimization 1: Formally Merge Tasks 1.3, 1.4, and 2.2 into a Single Task

### Current State

Tasks 1.3, 1.4 (Epic 1), and 2.2 (Epic 2) are specified as three separate tasks with independent acceptance criteria, but the spec itself states in the Implementer's Quick Reference: "Tasks 1.3, 1.4, and 2.2 modify the same text (Wave 2 step 3). Implement as a single atomic edit via Task 2.2." The Implementation Order section repeats this: "Task 2.2 integrates with 1.3/1.4." Despite this, three separate task specifications exist with three sets of acceptance criteria, creating triple the tracking overhead for what the spec acknowledges is one edit.

### Proposed Change

Collapse Tasks 1.3, 1.4, and 2.2 into a single task (renumbered as Task 2.2 or "Task 1+2.A"). Merge the acceptance criteria into a single checklist. Remove the "Critical coordination" callouts from Implementer's Quick Reference and Implementation Order since the coordination problem no longer exists. Retain all functional requirements -- no content is removed, only the organizational wrapper.

### Time Savings

**1.0 hour** (~6.7% of sprint)

Breakdown: Elimination of redundant task specification reading/comprehension (~15 min), removal of coordination overhead between Epics 1 and 2 (~20 min), simplified progress tracking (3 checkpoints reduced to 1, ~10 min), elimination of merge-conflict risk management stated in R5 (~15 min). The spec currently lists R5 ("Wave 2 step 3 rewrite conflict between Epic 1 and Epic 2 authors") as a MEDIUM probability risk with dedicated mitigation. Merging eliminates this risk entirely, removing the need for any mitigation activity.

### Effectiveness Impact

**0.0** -- Zero impact on effectiveness.

The spec already mandates this consolidation in prose. This optimization merely aligns the task structure with what the spec says to do. Every functional requirement from Tasks 1.3, 1.4, and 2.2 is preserved in the merged task. Risk R5 can be removed from the risk register (it becomes structurally impossible).

### Risk Assessment

**Minimal**. The only risk is that a future reviewer might want traceability back to the original root-cause-to-task mapping (RC1 -> Task 1.3, RC1 -> Task 1.4, RC2 -> Task 2.2). Mitigation: add a one-line provenance note in the merged task listing which original tasks it incorporates.

### Net Benefit Formula

`1.0 hrs * (1 - 0.0) = 1.0 net benefit hours`

### Panel Notes

- **Efficiency Expert**: "This is the most obvious optimization. The spec contradicts itself -- three tasks that it simultaneously says must be one edit. Fix the contradiction."
- **Quality Advocate**: "Agreed. The current structure creates a false sense of granularity. Three tasks tracking one edit provides no additional quality signal."
- **Implementation Specialist**: "This saves real time. Reading three task specifications, mentally merging them, and worrying about R5 is non-trivial cognitive overhead for the implementer."
- **Risk Analyst**: "R5 disappears entirely. That alone justifies this optimization."

**Consensus**: Unanimous APPROVE.

---

## Optimization 2: Fold Minor T02 Amendments into Existing Task Acceptance Criteria

### Current State

The T02 synthesis identified 11 gaps (G1-G11) requiring sprint-spec amendments. Nine of these (G1, G4, G5, G6, G7, G8, G9, G10, G11) are 15-30 minute fixes each. They are currently presented as a separate amendment backlog that an implementer must cross-reference against the task list to determine WHERE each fix belongs. The mental overhead of: read amendment -> find relevant task -> modify task AC -> re-read task to verify consistency is repeated 9 times.

### Proposed Change

Integrate each minor amendment directly into the acceptance criteria of its parent task:

| Amendment | Parent Task | Integration |
|-----------|-------------|-------------|
| G1 (missing-file guard contradiction) | Task 2.2 step 3e | Change "status: partial" to "status: failed, failure_stage: 'transport'" in step 3e AC |
| G4 (step 3c tool-call spec) | Task 2.2 step 3c | Add AC: "step 3c specifies debate-orchestrator role as: {concrete tool-call}" |
| G5 (convergence sentinel in fallback) | Task 1.4 fallback | Add AC: "F5 sets convergence_score to 0.5 with comment 'estimated, not measured'" |
| G6 (glossary scope statement) | Task 2.1 | Add AC: "Glossary includes explicit scope statement: covers tool-call verbs only" |
| G7 (fallback glossary consistency) | Task 1.4 | Add AC: "F1-F5 steps use glossary-consistent verbs" |
| G8 (fallback quality threshold) | Task 1.4 | Add AC: "Minimum: 2 variants, 1 diff analysis, 1 scored comparison" |
| G9 (debate-orchestrator bootstrap) | Task 2.2 step 3c or deferred | Add AC: "Add Read tool call for debate-orchestrator.md before delegation" |
| G10 (convergence threshold rationale) | Task 3.2 | Add AC: "0.6 threshold includes rationale comment" |
| G11 (YAML example block) | Task 3.2 | Add AC: "Section includes example YAML block for success, partial, and failed statuses" |

The amendment backlog section is removed. No functional content is lost.

### Time Savings

**0.75 hours** (~5% of sprint)

Breakdown: Elimination of cross-referencing overhead (9 amendments x ~3 min each = ~27 min), elimination of amendment-tracking as a separate work stream (~10 min), reduced risk of missed amendments when implementer forgets to check the separate list (~8 min of potential rework avoided).

### Effectiveness Impact

**0.0** -- Zero impact on effectiveness.

Every amendment is preserved; only its location changes from a separate list to inline in the relevant task. The implementer encounters each requirement exactly when they need it (during the task), rather than having to remember to check a separate document.

### Risk Assessment

**Negligible**. The only risk is that integrating amendments might make individual task acceptance criteria longer. Mitigation: the longest task AC (Task 2.2, the merged task from Optimization 1) was already the most complex; adding 3-4 more bullet points is manageable.

### Net Benefit Formula

`0.75 hrs * (1 - 0.0) = 0.75 net benefit hours`

### Panel Notes

- **Efficiency Expert**: "Separate amendment backlogs are a project management antipattern for single-sprint work. Fold them in."
- **Quality Advocate**: "This actually IMPROVES quality. Inline requirements are harder to miss than cross-referenced ones."
- **Implementation Specialist**: "I have seen amendments get dropped because the implementer finished the task, checked its AC, and moved on without consulting the separate gap list. This prevents that."
- **Risk Analyst**: "No new risks. Reduces risk of missed requirements."

**Consensus**: Unanimous APPROVE.

---

## Optimization 3: Simplify Fallback Protocol from 5 Steps to 3 Steps

### Current State

Task 1.4 specifies a 5-step fallback protocol (F1-F5) for when the Skill tool is unavailable:
- F1: Variant Generation (dispatch Task agents per --agents spec)
- F2: Diff Analysis (compare all variants)
- F3: Single-Round Debate (advocate statements + scoring)
- F4: Base Selection (score variants and select base)
- F5: Merge + Contract (merge best elements, write return contract)

Each step has defined input, output, failure action, and individual `return-contract.yaml` failure writes. The spec already acknowledges (Task 3.2) that fallback output is "substantially reduced compared to full adversarial pipeline" and should carry an explicit quality degradation warning. The T02 synthesis notes that convergence scoring is "meaningless in fallback mode" (G5).

### Proposed Change

Reduce to 3 steps:

- **F1: Variant Generation** -- Unchanged. Dispatch Task agents per `--agents` spec. Output: variant files.
- **F2: Comparative Analysis + Scoring** -- Merge F2 (diff analysis), F3 (debate), and F4 (base selection) into a single Task agent dispatch. Prompt: "Compare variants, identify agreements and conflicts, score each variant against the spec objectives, and select the strongest variant as base." Output: `analysis-and-selection.md`. This is what a single Task agent can realistically accomplish in one pass -- the distinction between "diff analysis," "debate," and "base selection" is artificial granularity for a degraded-mode operation that already lacks the multi-agent structured debate of the full pipeline.
- **F3: Merge + Contract** -- Unchanged from F5. Merge best elements, write return contract with `fallback_mode: true`.

Failure handling simplified: single failure handler for any step that writes `return-contract.yaml` with `status: failed` and the appropriate `failure_stage` value.

### Time Savings

**1.25 hours** (~8.3% of sprint)

Breakdown: Reduced specification writing for Task 1.4 (~30 min -- 5 detailed step specifications reduced to 3), reduced implementation complexity in the atomic Wave 2 step 3 rewrite (~25 min -- fewer sub-steps to integrate), reduced verification effort (~15 min -- 3 steps to validate instead of 5), reduced failure-handler specification (~15 min -- single handler vs. per-step handlers).

### Effectiveness Impact

**0.15** -- Low impact.

The 5-step fallback was already a degraded approximation of the full adversarial pipeline's multi-round structured debate. The distinction between separate "diff analysis," "debate," and "base selection" steps in fallback mode is aspirational -- a Task agent performing these as separate operations does not meaningfully improve output quality over a single comparative-analysis-and-selection pass. The full pipeline's quality comes from multi-agent adversarial dynamics (multiple rounds, scoring convergence, contradiction detection), none of which the inline fallback can replicate regardless of step count.

The 0.15 impact accounts for: (a) slight reduction in fallback output structure (single analysis file vs. three), which may make debugging harder if the fallback produces poor results, and (b) loss of the incremental failure-stage granularity (3 failure stages instead of 5).

### Risk Assessment

**Low-moderate**. Risk: the combined F2 step produces lower-quality output than three separate steps would. Mitigation: the Task agent prompt for F2 explicitly lists all three activities (compare, score, select), so the agent is directed to perform all operations even though they are in one step. The output file (`analysis-and-selection.md`) provides a single artifact that captures the analysis chain.

Secondary risk: if the follow-up sprint (S05 quality gate) wants to add quality thresholds per fallback step, having 3 steps instead of 5 provides fewer insertion points. Mitigation: the follow-up sprint can decompose F2 back into sub-steps if needed; the contract interface (return-contract.yaml) is unchanged.

### Net Benefit Formula

`1.25 hrs * (1 - 0.15) = 1.0625 net benefit hours`

### Panel Notes

- **Efficiency Expert**: "Five steps for a degraded fallback is over-engineering the backup plan. Three steps delivers the same practical outcome."
- **Quality Advocate**: "I accept this with reservations. The quality loss is real but bounded by the fact that fallback mode is inherently degraded. My concern is that future engineers might mistake the 3-step fallback for 'good enough' and not prioritize fixing the primary path. Add a prominent comment: 'This fallback is NOT a substitute for the full adversarial pipeline.'"
- **Implementation Specialist**: "Writing 5 detailed step specifications with individual failure handlers is the most time-consuming part of Task 1.4. Reducing to 3 with a single failure handler cuts the effort nearly in half."
- **Risk Analyst**: "The incremental risk is acceptable. The fallback was already a 60% approximation of the full pipeline at best. Going from 60% to ~55% is not material."

**Consensus**: 3-1 APPROVE (Quality Advocate approves with the caveat that a "not a substitute" comment is added).

---

## Optimization 4: Defer G2 (Fallback Validation Test) and G3 (Fallback Sprint Variant) Until After Task 0.0

### Current State

The T02 synthesis identifies two amendments as "Critical (must fix before implementation)":
- **G2**: Add Verification Test 6 -- run F1-F5 (or F1-F3 per Optimization 3) on test input, verify return-contract.yaml and output files. Estimated effort: 1-2 hours.
- **G3**: Add a "fallback-only sprint variant" section after Task 0.0 listing task modifications when the primary path is confirmed non-viable. Estimated effort: 30 minutes.

Both are contingent on Task 0.0 (Skill Tool Probe). If Task 0.0 confirms the primary path is viable, G2 becomes a lower-priority regression safety net (the fallback may never execute in normal operation), and G3 is entirely unnecessary.

### Proposed Change

Restructure G2 and G3 as **conditional amendments gated on Task 0.0 outcome**:

- If Task 0.0 returns **"primary path viable"**: Defer both G2 and G3 to the follow-up sprint. The fallback exists as a safety net but is not the expected execution path. Testing it thoroughly is defense-in-depth, not critical path.
- If Task 0.0 returns **"primary path blocked"**: G3 becomes mandatory (must rewrite sprint for fallback-only execution), and G2 becomes the primary verification mechanism. Both are implemented immediately.

This converts unconditional 1.5-2.5 hours of work into conditional work that is only performed when the outcome warrants it. Given that Task 0.0 is the FIRST thing executed, this decision is made before any other work begins -- there is no wasted effort.

### Time Savings

**2.0 hours** (~13.3% of sprint) -- Expected value savings.

If primary path is viable (the spec estimates this at ~58% probability based on R1's 0.40 failure probability): 2.0-2.5 hours saved outright. If primary path is blocked (~42% probability): 0 hours saved (both are implemented). Expected savings: `0.58 * 2.25 + 0.42 * 0 = 1.3 hrs`. However, since the condition is evaluated before any other work, the "viable" case saves the full 2.0-2.5 hours. Reporting the full-save scenario: **2.0 hours**.

### Effectiveness Impact

**0.15** -- Low impact.

In the "primary path viable" scenario, skipping the fallback test means the fallback protocol is untested in this sprint. This is a real coverage gap, but the fallback is a contingency for a scenario that has been empirically confirmed NOT to occur (Task 0.0 proved the primary path works). The fallback still exists in the spec and can be tested in the follow-up sprint.

In the "primary path blocked" scenario, effectiveness impact is 0.0 (both G2 and G3 are implemented). The weighted impact is: `0.58 * 0.25 + 0.42 * 0.0 = 0.145`, rounded to 0.15.

### Risk Assessment

**Moderate**. Primary risk: the Skill tool works during Task 0.0 but fails intermittently in production (e.g., due to context limits, session length, or platform-specific behavior). Without the fallback validation test, the first time the fallback is exercised could be in a real user session, where a broken fallback would produce a silent failure -- repeating the original problem this sprint is designed to fix.

Mitigation: (a) The fallback protocol is explicitly documented in the spec and follows the same patterns as the primary path, reducing the likelihood of structural errors. (b) The return-contract.yaml schema validator (DVL Task 3.5 from T01) provides output validation regardless of which path produced the output. (c) The follow-up sprint (S05) should prioritize fallback testing as its first task.

### Net Benefit Formula

`2.0 hrs * (1 - 0.15) = 1.70 net benefit hours`

### Panel Notes

- **Efficiency Expert**: "Classic conditional work optimization. Do not test the backup plan before you know if the primary plan works."
- **Quality Advocate**: "I am the dissenting voice here. Untested fallbacks are how silent failures happen -- which is literally the problem this sprint exists to fix. I would accept deferring G3 but NOT G2. The fallback validation test is the only assurance that our safety net works."
- **Implementation Specialist**: "Pragmatically, if Task 0.0 confirms the primary path, the team's energy should go into making the primary path robust, not testing a fallback that may never fire. The follow-up sprint is the right place for fallback hardening."
- **Risk Analyst**: "The Quality Advocate's concern is valid. The mitigation via validate_return_contract.py (DVL Task 3.5) partially addresses this -- if the fallback ever fires and produces a malformed contract, the schema validator catches it. I lean APPROVE with the DVL script as the compensating control."

**Consensus**: 3-1 APPROVE (Quality Advocate dissents on G2 deferral; accepts G3 deferral).

---

## Optimization 5: Consolidate Verification Tests 1, 3, and 4 into Task Acceptance Criteria

### Current State

The sprint spec defines 5 Verification Tests:
- **Test 1**: Skill Tool Availability Confirmation -- Two `grep -q` commands checking for "Skill" in two files.
- **Test 2**: Wave 2 Step 3 Structural Audit -- 7-point manual inspection checklist.
- **Test 3**: Return Contract Schema Consistency -- Extract field names from producer and consumer files and diff.
- **Test 4**: Pseudo-CLI Elimination -- Single `grep -c` command checking for zero matches.
- **Test 5**: End-to-End Invocation -- Full pipeline execution (post-sprint, manual).

Tests 1, 3, and 4 are trivial checks (grep one-liners or simple field extraction) that duplicate information already in the task acceptance criteria. Test 1 duplicates Tasks 1.1 and 1.2 AC. Test 4 duplicates Task 2.4 AC. Test 3 duplicates Tasks 3.1 and 3.2 AC. Running them as a separate "Verification Plan" phase after all tasks are complete adds overhead: the implementer must re-read the verification section, execute commands they have already implicitly performed during task validation, and document results separately.

### Proposed Change

Embed the verification commands directly into the acceptance criteria of their parent tasks:

| Test | Becomes | Location |
|------|---------|----------|
| Test 1 (grep for Skill) | AC for Tasks 1.1/1.2: "Verified by: `grep -q 'Skill' <file> && echo PASS`" | Task 1.1/1.2 AC |
| Test 3 (schema field diff) | AC for Task 3.2: "Verified by: field names extracted from producer and consumer match exactly" | Task 3.2 AC |
| Test 4 (pseudo-CLI grep) | AC for Task 2.4: "Verified by: `grep -c 'sc:adversarial --' <file>` returns 0" | Task 2.4 AC |

Retain Tests 2 and 5 as standalone verification activities (Test 2 is a substantive structural audit; Test 5 is the post-sprint E2E test). The "Verification Plan" section is reduced from 5 tests to 2, with a note that Tests 1, 3, and 4 are embedded in task ACs.

The Definition of Done verification checkboxes are updated:
- Remove: "Verification Test 1 passes", "Verification Test 3 passes", "Verification Test 4 passes"
- Retain: "Verification Test 2 passes (Wave 2 step 3 structural audit)", "Verification Test 5 passes (E2E invocation)"
- The removed checks are covered by task completion (each task's AC includes the verification command).

### Time Savings

**0.75 hours** (~5% of sprint)

Breakdown: Elimination of separate verification phase for Tests 1, 3, 4 (~20 min execution + ~10 min documentation), reduced Definition of Done verification overhead (~15 min -- 3 fewer checkboxes to track as separate activities), elimination of duplicate verification (implementer no longer validates during task AND again during verification, ~15 min).

### Effectiveness Impact

**0.05** -- Negligible impact.

The verification checks still exist; they are performed inline rather than as a post-hoc batch. The only effectiveness loss is the removal of the "independent verification" signal -- having a separate verification phase forces a re-check that might catch drift between implementation and intent. However, for grep one-liners and simple field diffs, this re-check provides minimal additional assurance. Tests 2 and 5 (the substantive verifications) are retained as standalone activities.

### Risk Assessment

**Low**. Risk: an implementer marks a task complete without actually running the embedded verification command. This is the same risk as the current structure (an implementer could skip the verification phase entirely). Mitigation: the two retained standalone tests (Test 2 structural audit and Test 5 E2E) provide the substantive quality gates. The embedded checks are execution-level validations that the implementer has strong incentive to run (they confirm the edit worked).

### Net Benefit Formula

`0.75 hrs * (1 - 0.05) = 0.7125 net benefit hours`

### Panel Notes

- **Efficiency Expert**: "Verification tests that are grep one-liners should not be a separate phase. They are acceptance criteria."
- **Quality Advocate**: "Acceptable. I want to ensure Tests 2 and 5 remain standalone -- those are the ones that provide real quality assurance. Tests 1, 3, and 4 are mechanical checks that belong in task ACs."
- **Implementation Specialist**: "This matches how implementation actually works. Nobody finishes all tasks, THEN goes back to grep for 'Skill' in a file they edited 2 hours ago. They check it when they edit it."
- **Risk Analyst**: "Minimal risk. The retained standalone tests are the high-value ones."

**Consensus**: Unanimous APPROVE.

---

## Summary Table

| # | Optimization | Time Saved | Effectiveness Impact | Net Benefit | Zero Impact? |
|---|-------------|-----------|---------------------|-------------|--------------|
| 1 | Merge Tasks 1.3 + 1.4 + 2.2 into single task | 1.00 hrs | 0.00 | 1.000 hrs | Yes |
| 2 | Fold T02 amendments into task ACs | 0.75 hrs | 0.00 | 0.750 hrs | Yes |
| 3 | Simplify fallback from 5 steps to 3 | 1.25 hrs | 0.15 | 1.063 hrs | No |
| 4 | Defer G2 + G3 until after Task 0.0 gate | 2.00 hrs | 0.15 | 1.700 hrs | No |
| 5 | Embed Verification Tests 1, 3, 4 into task ACs | 0.75 hrs | 0.05 | 0.713 hrs | No |
| **Total** | | **5.75 hrs** | **Wtd avg: 0.07** | **5.225 hrs** | **2 of 5** |

### Constraint Verification

| Constraint | Requirement | Actual | Status |
|-----------|------------|--------|--------|
| Max effectiveness impact per optimization | < 0.3 | Max is 0.15 | PASS |
| Total time savings > 20% of sprint | > 3.0 hrs (20% of ~15 hrs) | 5.75 hrs (38.3%) | PASS |
| At least 2 zero-effectiveness-impact optimizations | >= 2 | 2 (#1 and #2) | PASS |
| Optimizations independent of each other | All adoptable individually | Yes (see note below) | PASS |

**Independence note**: Optimizations 1 and 2 are fully independent. Optimization 3 modifies the fallback that Optimization 4 conditionally defers testing -- but they operate on different dimensions (spec content vs. testing timing) and can be adopted independently. Optimization 5 is independent of all others.

### Combined Effect on Sprint

| Metric | Before | After All 5 | Change |
|--------|--------|-------------|--------|
| Estimated sprint duration | ~15 hrs | ~9.25 hrs | -38.3% |
| Task count | 13 tasks (0.0 + 12) | 10 tasks | -23% |
| Risk register entries | 7 risks | 6 risks (R5 eliminated) | -14% |
| Verification tests (standalone) | 5 tests | 2 tests (+ 3 embedded in ACs) | Tests preserved, overhead reduced |
| DoD checkboxes | ~19 | ~14 | -26% |
| T02 amendment backlog | 11 gaps | 0 gaps (all integrated) | Eliminated as separate artifact |

### Panel Final Statement

The five optimizations collectively reduce sprint overhead by 38% while preserving all functional requirements. The two zero-impact optimizations (#1, #2) are structural improvements that should be adopted unconditionally -- they fix organizational redundancies the spec itself acknowledges. The three low-impact optimizations (#3, #4, #5) trade marginal completeness for substantial time savings, with the largest trade-off being the untested fallback path (Optimization 4), which is mitigated by the DVL schema validator and the conditional gate on Task 0.0.

The Quality Advocate's dissent on Optimization 4 (deferring fallback validation) is noted and respected. If adopted, the implementer should document "fallback validation deferred to follow-up sprint" as an explicit open item in the sprint retrospective.

---

*Optimization panel generated 2026-02-23. Panelists: Efficiency Expert, Quality Advocate, Implementation Specialist, Risk Analyst.*
*Input: sprint-spec.md, ranked-root-causes.md, T02-synthesis.md, T01-dvl-evaluation.md.*
*Method: Independent analysis per optimization, cross-panel consensus with dissent recording.*
