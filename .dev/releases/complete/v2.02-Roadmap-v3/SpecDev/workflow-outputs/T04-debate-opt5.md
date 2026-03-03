# T04: Adversarial Debate -- Optimization 5

> **Subject**: Consolidate Verification Tests 1, 3, and 4 into Task Acceptance Criteria
> **Date**: 2026-02-23
> **Format**: Structured adversarial debate with cross-examination and scoring
> **Input**: T03-optimizations.md (Optimization 5), sprint-spec.md, ranked-root-causes.md

---

## Optimization 5 Summary

**Proposal**: Embed Verification Tests 1 (Skill tool grep), 3 (return contract schema field diff), and 4 (pseudo-CLI grep elimination) directly into the acceptance criteria of their parent tasks, reducing the standalone Verification Plan from 5 tests to 2 (retaining Test 2: Wave 2 step 3 structural audit, and Test 5: E2E invocation). The Definition of Done checkboxes for Tests 1, 3, and 4 are replaced by task-completion coverage.

**Claimed savings**: 0.75 hours (5% of sprint)
**Claimed effectiveness impact**: 0.05
**Claimed net benefit**: 0.7125 hours

---

## FOR Position: Optimization 5 Should Be Adopted

### Argument 1: The Verification Tests Are Mechanically Redundant

Tests 1, 3, and 4 are trivially mechanical checks -- `grep -q` one-liners and field-name diffs. They duplicate validations that an implementer MUST already perform to confirm their task acceptance criteria are met:

- **Test 1** checks that `Skill` appears in `allowed-tools` in two files. Tasks 1.1 and 1.2 already have acceptance criteria requiring exactly this. An implementer who completes Tasks 1.1/1.2 has, by definition, already verified this.
- **Test 4** checks that zero standalone `sc:adversarial --` patterns remain in `adversarial-integration.md`. Task 2.4's acceptance criteria require exactly this conversion. An implementer who completes Task 2.4 has already run or mentally verified this check.
- **Test 3** checks that producer and consumer return contract field names match. Tasks 3.1 and 3.2 define these fields. An implementer who completes both tasks in sequence will have verified field alignment.

Performing these checks AGAIN as a separate "Verification Plan" phase is pure ceremony. It adds a context switch (re-reading the verification section after finishing all tasks), forces redundant command execution, and adds documentation overhead (recording results separately) -- all for checks that provide zero incremental assurance beyond task completion.

### Argument 2: Inline Verification Is Actually Superior

Embedding verification commands directly into task ACs means the check runs at the moment of maximum context -- the implementer has just edited the file, knows exactly what changed, and can immediately catch errors. A post-hoc verification phase introduces a temporal gap: the implementer finishes all tasks, switches mental context to "verification mode," and re-reads files they edited potentially hours earlier.

Cognitive science consistently shows that immediate feedback loops are more effective than delayed batch verification. The sprint spec's Implementation Order shows Epic 1 is done before Epic 2, which is done before Epic 3. By the time a separate Verification Plan runs Test 1, the Epic 1 edits may be hours old. Catching an error inline (during Task 1.1) costs minutes to fix. Catching it post-hoc (during Verification Test 1, after all 3 epics) could require unwinding later work that assumed the edit was correct.

### Argument 3: The Retained Tests Provide the Real Quality Gates

Tests 2 and 5 are substantive, non-trivial verifications:

- **Test 2** (Wave 2 step 3 structural audit) is a 7-point manual inspection checklist that validates the most complex edit in the sprint -- the atomic Wave 2 step 3 rewrite. This cannot be reduced to a grep one-liner. It requires human judgment about whether sub-steps use glossary-consistent verbs, whether the fallback covers all three error types, and whether the return contract routing is correctly structured.
- **Test 5** (E2E invocation) is the ultimate integration test: does the full pipeline work end-to-end?

These two tests provide the meaningful quality signal. Tests 1, 3, and 4 are "did you actually do what the task said?" checks -- which is what acceptance criteria ARE. Retaining T2 and T5 as standalone activities preserves the verification plan's substantive value while eliminating its ceremonial overhead.

### Argument 4: Sprint Duration Is Under Pressure

The sprint baseline is ~15 hours. Even after the four other optimizations, every saved minute matters. 0.75 hours (45 minutes) is the cost of reading the verification section, re-executing three trivially redundant commands, and documenting their results separately. This is time better spent on the actual complex tasks (the Wave 2 step 3 rewrite, the return contract schema, the fallback protocol) or on the DVL verification scripts mentioned in the sprint spec, which provide deterministic programmatic validation far beyond what grep one-liners achieve.

---

## AGAINST Position: Optimization 5 Is Risky and Undermines Verification Integrity

### Argument 1: Separate Verification Exists for a Reason -- Independence

The verification plan is intentionally separate from task acceptance criteria. This separation enforces a "second look" -- a distinct phase where the implementer steps back from task-level tunnel vision and validates the sprint's deliverables holistically. This is not redundancy; it is defense-in-depth.

Consider the failure mode this sprint exists to fix: Claude was supposed to "Invoke sc:adversarial" but never did, because the Skill tool was missing from `allowed-tools`. The original SKILL.md author presumably believed the invocation was set up correctly. The problem persisted because there was no independent verification step that checked "is the Skill tool actually in allowed-tools?" If this sprint's Task 1.1 implementer believes they completed the edit correctly but made a subtle error (e.g., added `Skill` to a comment line instead of the `allowed-tools` frontmatter line), the task-level AC check might pass under confirmation bias. A separate verification phase, with an explicit `grep -q` command, forces a concrete, unambiguous re-check.

The very problem this sprint fixes was caused by insufficient verification of basic structural requirements. Removing verification steps from the verification plan is philosophically opposed to the sprint's purpose.

### Argument 2: Task Completion Does Not Guarantee AC Verification

The FOR position assumes that completing a task means verifying its acceptance criteria. In practice, this is not guaranteed. Task completion can mean:

1. The implementer edited the file and visually confirmed the change (but did not run the grep command).
2. The implementer marked the task complete based on their understanding of the edit (without re-reading the AC checklist).
3. The implementer completed the task under time pressure and deferred verification to the "Verification Plan" phase (which now does not exist for these tests).

A separate verification phase provides a structural forcing function. The Definition of Done currently has 3 explicit checkboxes: "Verification Test 1 passes," "Verification Test 3 passes," "Verification Test 4 passes." These checkboxes cannot be checked without running the specific commands. Replacing them with "all task ACs met" dilutes the forcing function -- "all task ACs met" is a meta-assertion that is easier to rubber-stamp than a specific "run this grep command and confirm output."

### Argument 3: Test 3 (Schema Consistency) Is Not Trivially Redundant

Tests 1 and 4 are arguably simple enough to embed in task ACs. But Test 3 -- return contract schema consistency -- is a cross-task verification. It checks that the PRODUCER (Task 3.1, sc:adversarial SKILL.md) and the CONSUMER (Task 3.2, adversarial-integration.md) define identical field sets. These are two different tasks, potentially implemented at different times, possibly even in different files simultaneously (since Epic 3 can parallel Epic 2).

Embedding Test 3 into Task 3.2's AC means the schema consistency check only runs when Task 3.2 is completed. But what if Task 3.1 is modified AFTER Task 3.2 is done (e.g., during a later revision or cleanup)? The standalone Verification Test 3 would catch this drift because it runs at the END of the sprint, after all tasks are complete. The embedded version would not, because Task 3.2's AC was already checked and marked complete.

The root cause analysis (ranked-root-causes.md) specifically flags RC4 (Return Contract Data Flow) as having a combined score of 0.75 and notes that "no transport mechanism" existed for structured data. Schema consistency between producer and consumer is the linchpin of RC4's fix. Weakening the verification of this consistency -- even marginally -- is counter to the sprint's goals.

### Argument 4: 0.75 Hours Is an Overestimate

The claimed 0.75-hour savings includes:
- 20 min executing Tests 1, 3, 4 + 10 min documenting results = 30 min
- 15 min DoD verification overhead (3 checkboxes)
- 15 min "elimination of duplicate verification"

The last item (15 min) assumes the implementer currently validates during the task AND again during verification. But if the implementer validates during the task (as the FOR position argues they naturally do), they can skip the redundant re-execution during the verification phase in under 1 minute per test ("I already confirmed this during Task 1.1 -- check"). The real overhead of the verification phase for these three trivial tests is ~10-15 minutes total, not 45 minutes. The optimization overstates its savings by 2-3x.

---

## CROSS-EXAMINATION

### FOR Challenges AGAINST's Strongest Argument (Argument 1: Independence)

**FOR**: You argue that separate verification provides "independence" and "defense-in-depth." But the verification commands ARE the same commands. Test 1 runs `grep -q "Skill" <file>`. The proposed embedded AC says: `Verified by: grep -q 'Skill' <file> && echo PASS`. They are literally the same check, run by the same person, on the same file. Where is the "independence"?

True independent verification would be a DIFFERENT person running the checks, or a CI pipeline executing them automatically, or the DVL scripts (verify_allowed_tools.py) providing programmatic validation. None of those properties change whether the grep is in the verification section or in the task AC. You are conflating "separate document section" with "independent verification." They are not the same thing.

Furthermore, you cite the original failure (Skill tool missing from allowed-tools) as evidence for more verification. But that failure persisted across an entire feature development cycle -- not because there was no verification step, but because there was no verification AT ALL. Adding the verification command to the task AC, where it is encountered at the point of edit, is MORE likely to be executed than a separate phase at the end of a 15-hour sprint.

### AGAINST Challenges FOR's Strongest Argument (Argument 2: Inline Verification Is Superior)

**AGAINST**: You argue that inline verification provides "immediate feedback" and is cognitively superior. But this ignores a critical property of the verification plan: it operates on the FINAL STATE of the codebase, not an intermediate state.

Consider this scenario: The implementer completes Task 1.1 (adds Skill to roadmap.md's allowed-tools). The inline AC check passes. Later, while implementing Task 2.4 (rewriting adversarial-integration.md), the implementer accidentally reverts the roadmap.md edit (e.g., an editor undo, a git checkout of the wrong version, or a merge conflict resolution that drops the change). Task 1.1 is already marked complete with its AC verified. Without the standalone Verification Test 1 running at the END of the sprint, this regression goes undetected until the E2E test (Test 5) -- which is a post-sprint manual test that may not run for days.

The standalone verification plan catches regressions between tasks. Inline ACs only catch errors at the time of the specific task. This is not a theoretical concern -- the sprint spec itself identifies R5 (merge conflict between Epic 1 and Epic 2 authors) as a risk, and the Implementation Order shows that later tasks modify the same files as earlier tasks. The regression risk is real.

### FOR Rebuttal

The regression scenario is valid but addressed by two factors: (1) The sprint spec mandates `make verify-sync` as a post-edit step, which catches file-level inconsistencies. (2) Test 2 (the retained structural audit) performs a 7-point manual inspection of the Wave 2 step 3 rewrite at sprint end, which would surface a missing Skill reference. (3) The DVL scripts (if implemented) provide automated regression detection. The regression risk exists but has multiple compensating controls independent of the verification plan structure.

### AGAINST Rebuttal

`make verify-sync` checks that `.claude/` mirrors `src/superclaude/` -- it does NOT check that the Skill tool is in allowed-tools. Test 2 audits Wave 2 step 3 structure -- it does NOT check Task 1.1's edit to `roadmap.md`. Neither compensating control covers the specific regression scenario described. The DVL scripts are explicitly marked "implement if time permits" and cannot be relied upon as a compensating control for a verification step being removed in the same sprint.

---

## SCORING

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **time_savings** | 0.55 | Claimed 0.75 hrs is likely overstated. Realistic savings are 0.3-0.5 hrs (the three trivial tests take ~15 min to execute and ~10 min to document; the "duplicate verification" elimination is double-counted). Score reflects moderate but real savings. |
| **effectiveness_preservation** | 0.80 | The verification checks still exist in task ACs. Tests 2 and 5 (the substantive ones) are retained. However, the loss of final-state verification for Tests 1, 3, 4 creates a real regression detection gap, particularly for Test 3 (cross-task schema consistency). The 0.05 effectiveness impact claimed in T03 is likely understated; 0.10-0.15 is more realistic when accounting for inter-task regression risk. |
| **feasibility** | 0.90 | Straightforward restructuring. Moving verification commands from one document section to another is trivially implementable. No technical barriers. |
| **risk** (higher = lower risk) | 0.70 | Primary risk: regression between tasks goes undetected until E2E test. Secondary risk: implementer skips embedded verification under time pressure without the forcing function of a separate verification phase. Both are real but bounded by the retained Test 2 (structural audit) and Test 5 (E2E). The cross-task schema consistency concern (Test 3) is the most significant risk. |
| **net_benefit** | 0.65 | Moderate positive net benefit. The optimization is directionally correct (inline verification is more natural) but slightly undervalues the independent verification signal, particularly for Test 3. The savings are real but smaller than claimed. |

**Weighted composite**: `(0.55 + 0.80 + 0.90 + 0.70 + 0.65) / 5 = 0.72`

---

## RECOMMENDATION: adopt-with-modifications

### Rationale

The core argument FOR is sound: Tests 1 and 4 are trivially redundant with their parent task ACs, and executing them as a separate phase provides negligible additional assurance. However, the AGAINST position raises a legitimate concern about Test 3 (schema consistency), which is a cross-task, cross-file verification that checks a property central to the sprint's RC4 fix. Embedding it in a single task's AC loses the final-state, cross-task verification property.

### Exact Modifications

1. **Embed Tests 1 and 4 into task ACs as proposed**. These are single-task, single-file checks that are genuinely redundant with task completion. Move them inline.

2. **Retain Test 3 as a standalone verification test**. Schema consistency between the return contract producer (sc:adversarial SKILL.md) and consumer (adversarial-integration.md) is a cross-task property that should be verified at sprint end, after all edits are final. This is the verification most closely aligned with RC4's root cause, and the one most susceptible to inter-task regression.

3. **Update Definition of Done accordingly**:
   - Remove: "Verification Test 1 passes", "Verification Test 4 passes"
   - Retain: "Verification Test 2 passes", "Verification Test 3 passes", "Verification Test 5 passes"
   - Add note in Tasks 1.1, 1.2: `Verified by: grep -q 'Skill' <file> && echo PASS`
   - Add note in Task 2.4: `Verified by: grep -c 'sc:adversarial --' <file> returns 0`

4. **Revised savings estimate**: 0.50 hours (retaining Test 3 as standalone adds ~15 min back vs. the full optimization's claimed 0.75 hrs, and the original savings were already overstated).

5. **Revised effectiveness impact**: 0.02 (near-zero, since the only substantive cross-task verification is retained).

### Revised Net Benefit

`0.50 hrs * (1 - 0.02) = 0.49 net benefit hours`

This is lower than the original 0.7125 but eliminates the most significant risk (cross-task schema regression) while preserving the majority of the savings from the two uncontroversially redundant tests.

---

*Debate conducted 2026-02-23. Method: Structured adversarial with cross-examination.*
*Input: T03-optimizations.md (Optimization 5), sprint-spec.md (verification plan, Definition of Done), ranked-root-causes.md (RC4 context).*
*Panel consensus: adopt-with-modifications (retain Test 3 as standalone).*
