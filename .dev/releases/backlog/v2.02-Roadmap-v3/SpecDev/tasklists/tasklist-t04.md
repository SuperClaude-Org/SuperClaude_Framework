# Tasklist: T04 Synthesis Optimizations Applied to sprint-spec.md

> **Source**: `.dev/releases/current/v2.01-Roadmap-v3/T04-synthesis.md`
> **Target**: `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md`
> **Generated**: 2026-02-23
> **Optimizations**: 5 (all ADOPT-WITH-MODIFICATIONS)

---

## Application Order

Per T04-synthesis.md Section 6, optimizations are ordered by debate score confidence. Opt 2 is applied before Opt 1 because it is a prerequisite (amendments must be mapped before merging tasks that contain them). Opt 4 is conditional on Task 0.0 results.

| Order | Optimization | Task(s) Below |
|-------|-------------|---------------|
| 1 | Opt 2: Fold amendments into parent ACs | Task 1 |
| 2 | Opt 1: Merge Tasks 1.3+1.4+2.2 | Task 2 |
| 3 | Opt 3: Simplify fallback 5 to 3 steps | Task 3 |
| 4 | Opt 5: Embed Tests 1,3,4 into task ACs | Task 4 |
| 5 | Opt 4: Defer fallback validation until after probe | Task 5 |

---

## Task 1: Fold T02 Amendments into Parent Task Acceptance Criteria

**Source reference**: T04-synthesis.md, Section 2, "Optimization 2: Fold Amendments into Parent ACs (Score: 0.80)"

**Scope**: This is a cross-cutting change that affects the Acceptance Criteria columns of multiple task rows across the Epic 1, Epic 2, and Epic 3 task tables. The T02 synthesis document (`.dev/releases/current/v2.01-Roadmap-v3/T02-synthesis.md`) contains amendments G1-G11; each must be integrated into the AC of its parent task using `[T02-G{N}]` provenance prefixes.

**Instructions**:

1. Read T02-synthesis.md to obtain the full list of amendments G1-G11 and their parent task mappings.
2. For each amendment G1-G11, locate the parent task row in sprint-spec.md and append the amendment text to that task's Acceptance Criteria column, prefixed with `[T02-G{N}]`.
3. Per the required modification in T04-synthesis.md: document **two mapping variants** -- one assuming Opt 1 is adopted (Tasks 1.3+1.4+2.2 merged), one assuming it is not. Since Opt 1 IS adopted (Task 2 below), apply the merged-task mapping as the primary, and note the unmerged mapping in a comment for traceability.
4. Per T04-synthesis.md: preserve the T02 synthesis document as audit trail (do NOT delete it).
5. Per T04-synthesis.md: if any task's ACs exceed 20 bullet points after integration, organize into labeled subsections.

**Affected locations in sprint-spec.md**: The exact rows depend on the G1-G11 parent task assignments in T02-synthesis.md. The implementer must cross-reference T02-synthesis.md to determine which rows of the Epic 1 table (lines 92-98), Epic 2 table (lines 110-115), and Epic 3 table (lines 127-133) are affected.

**Conflict check**: No direct conflict with reflection-final.md or spec-panel-roadmap-v2-review.md. The spec-panel review's Change 1 modifies Task 3.1's Change column and AC column -- if any T02 amendment targets Task 3.1, the implementer must merge both sets of additions into the same cell. Apply spec-panel Change 1 first, then append T02 amendments.

---

## Task 2: Merge Tasks 1.3, 1.4, and 2.2 into a Single Task

**Source reference**: T04-synthesis.md, Section 2, "Optimization 1: Merge Tasks 1.3+1.4+2.2 (Score: 0.82)"

**Scope**: Three task rows in sprint-spec.md that all modify Wave 2 step 3 are merged into one. This directly restructures the Epic 1 and Epic 2 task tables.

**Instructions**:

### 2a. Merge the three task rows into one

**Location**: Epic 1 task table (sprint-spec.md lines 92-98), rows for Tasks 1.3 and 1.4. Epic 2 task table (lines 110-115), row for Task 2.2.

**BEFORE** -- Three separate rows exist:

Row in Epic 1 table (line 96):
```
| 1.3 | Rewrite Wave 2 step 3 with Task-agent Skill invocation | `src/superclaude/skills/sc-roadmap/SKILL.md` | Replace the single compressed "Invoke sc:adversarial" instruction with a Task agent dispatch that uses the Skill tool. Specify: (a) Task agent prompt naming the Skill tool explicitly with `skill: "sc:adversarial"` syntax, (b) arguments: `--agents`, `--compare`, `--depth`, `--output-dir`, (c) expected output: `return-contract.yaml` in output directory | New step 3 contains explicit `Skill` tool call syntax inside Task prompt; arguments are enumerated; output expectation is specified |
```

Row in Epic 1 table (line 97):
```
| 1.4 | Add fallback protocol for Skill tool unavailability | `src/superclaude/skills/sc-roadmap/SKILL.md` | In Wave 2 step 3, add sub-step 3d: ... [full fallback specification] ... | Fallback covers all three Skill tool error types; 5 fallback steps (F1-F5) each have defined input, output, and failure action; WARNING emission is instructed; each step writes `return-contract.yaml` on failure with appropriate `failure_stage`; fallback produces `fallback_mode: true` on success |
```

Row in Epic 2 table (line 113):
```
| 2.2 | Decompose Wave 2 step 3 into 6 atomic sub-steps | `src/superclaude/skills/sc-roadmap/SKILL.md` | Replace step 3 with sub-steps 3a-3f. ... [full sub-step specification] ... | Each sub-step has exactly one verb from the glossary; each sub-step has one explicit output; step 3e includes guard for missing return-contract.yaml ... |
```

**AFTER** -- Replace all three rows with a single merged row. The merged row should be placed in the **Epic 1 table** as Task 1.3 (replacing the old 1.3 and 1.4 rows). The old Task 2.2 row should be **removed** from the Epic 2 table.

The merged task row structure:

```
| 1.3 | Rewrite Wave 2 step 3: Skill invocation + fallback + atomic sub-steps (merged from 1.3+1.4+2.2) | `src/superclaude/skills/sc-roadmap/SKILL.md` | [Combine Change columns from all three original tasks into a single coherent specification -- see below] | [Combine AC sections with labeled provenance -- see below] |
```

Per T04-synthesis.md required modifications:
- The **Change column** must combine all three tasks' change specifications into one coherent rewrite instruction (Skill invocation from 1.3, fallback protocol from 1.4, atomic sub-steps 3a-3f from 2.2).
- The **Acceptance Criteria column** must retain separate labeled sections: `[From 1.3]`, `[From 1.4]`, `[From 2.2]` for traceability.
- The task description must include a provenance note: "This task merges original Tasks 1.3 (Skill invocation), 1.4 (fallback protocol), and 2.2 (atomic sub-steps). Root causes addressed: RC1 (invocation wiring) and RC2 (specification-execution gap). Merge rationale: all three tasks modify the same text block (Wave 2 step 3) and were implemented as a single atomic edit per the original sprint-spec coordination note."

### 2b. Remove Task 1.4 row from Epic 1 table

**Location**: sprint-spec.md line 97 (the Task 1.4 row).

Delete this row entirely. Its content is absorbed into the merged Task 1.3.

### 2c. Remove Task 2.2 row from Epic 2 table

**Location**: sprint-spec.md line 113 (the Task 2.2 row).

Delete this row entirely. Its content is absorbed into the merged Task 1.3 in Epic 1.

### 2d. Update the "Critical coordination" note in Implementer's Quick Reference

**Location**: sprint-spec.md line 20.

**BEFORE**:
```
**Critical coordination**: Tasks 1.3, 1.4, and 2.2 modify the same text (Wave 2 step 3). Implement as a single atomic edit via Task 2.2. Tasks 1.3 and 1.4 are specification inputs; Task 2.2 is the implementation vehicle.
```

**AFTER**:
```
**Critical coordination**: Tasks 1.3, 1.4, and 2.2 have been merged into a single Task 1.3 (per T04 Optimization 1). The merged task covers Skill invocation, fallback protocol, and atomic sub-step decomposition as one coherent rewrite of Wave 2 step 3.
```

### 2e. Update the "Critical coordination point" in Implementation Order section

**Location**: sprint-spec.md line 164.

**BEFORE**:
```
**Critical coordination point**: Epic 1 tasks 1.3-1.4 and Epic 2 task 2.2 all modify Wave 2 step 3 in `src/superclaude/skills/sc-roadmap/SKILL.md`. These must be implemented as a single atomic rewrite to avoid merge conflicts and contradictory instructions. Assign one author to the Wave 2 step 3 rewrite, incorporating requirements from both epics.
```

**AFTER**:
```
**Critical coordination point**: Original tasks 1.3, 1.4, and 2.2 have been merged into Task 1.3 (per T04 Optimization 1), eliminating the cross-epic coordination risk. Task 1.3 now contains all Wave 2 step 3 requirements from both Epic 1 and Epic 2.
```

### 2f. Update the Implementation Order diagram

**Location**: sprint-spec.md lines 139-152 (the ASCII diagram).

Update the diagram to reflect that Task 2.2 no longer exists in Epic 2. Remove the `Task 2.2 integrates with 1.3/1.4` sub-branch. Replace with a note that Task 1.3 is the merged implementation vehicle.

### 2g. Adjust time estimate

Per T04-synthesis.md: net savings from this merge is ~0.60 hrs. If any per-task time estimates exist in the spec, reduce accordingly.

**Conflict check**:
- **reflection-final.md IMP-04** also recommends expanding Task 1.4's fallback protocol detail. Since Task 1.4 is now merged into 1.3, IMP-04's expansion applies to the merged task's fallback section. No conflict -- additive.
- **reflection-final.md Section 4 "Epic 1 / Epic 2 Overlap"** explicitly recommends the same merge. T04 and reflection are aligned here. No conflict.
- **reflection-final.md Section 2 "Sprint Sync Tasks"** recommends consolidating sync tasks. The sprint-spec already has them struck through. No conflict.
- **Risk R5** in the Risk Register (line 176) references the merge coordination risk. After this merge, R5's probability drops to near-zero. Consider adding a note to R5: "Mitigated by T04 Optimization 1 (task merge)."

---

## Task 3: Simplify Fallback from 5 Steps to 3 Steps

**Source reference**: T04-synthesis.md, Section 2, "Optimization 3: Simplify Fallback 5 to 3 Steps (Score: 0.776)"

**Scope**: Modifies the fallback protocol within the merged Task 1.3 (previously Task 1.4). The 5-step fallback (F1-F5) is consolidated into 3 invocations while preserving diagnostic granularity.

**Location**: The fallback protocol text within the merged Task 1.3's Change column (which was originally Task 1.4's content in the Epic 1 table, sprint-spec.md line 97).

**Instructions**:

Apply the following changes per T04-synthesis.md required modifications:

1. **Merge F2+F3 into a single step (F2/3)**: Combine "Diff Analysis" (F2) and "Single-Round Debate" (F3) into one Task agent dispatch. The merged agent must output labeled sections (`diff-analysis` and `debate-summary`) for diagnostic decomposition.

2. **Merge F4+F5 into a single step (F4/5)**: Combine "Base Selection" (F4) and "Merge + Contract" (F5) into one Task agent dispatch.

3. **Retain F1-F5 numbering**: Even when merging steps, maintain the F1-F5 identifiers as F1, F2/3, F4/5 for consistency with `failure_stage` values used elsewhere.

4. **Use compound `failure_stage` values**: For merged steps, use compound values like `comparative_analysis:scoring_failed` to preserve S05 extensibility.

5. **Add extensibility note**: Append to the fallback section: "NOTE: This simplified fallback is not a substitute for the full adversarial pipeline. If future sc:adversarial pipeline adds steps, decompose the merged fallback steps accordingly."

**BEFORE** (within the fallback specification -- 5 steps):
```
F1 Variant Generation — ...
F2 Diff Analysis — ...
F3 Single-Round Debate — ...
F4 Base Selection — ...
F5 Merge + Contract — ...
```

**AFTER** (3 invocations with preserved numbering):
```
F1 Variant Generation — [unchanged from original]
F2/3 Comparative Analysis + Single-Round Debate — dispatch Task agent to compare all variants AND conduct one round of advocate statements + scoring. Input: all variant files. Output: `<output>/adversarial/diff-analysis.md` (labeled section: diff-analysis) + `<output>/adversarial/debate-transcript.md` (labeled section: debate-summary). Failure: abort, `failure_stage: comparative_analysis:scoring_failed`.
F4/5 Base Selection + Merge + Contract — dispatch Task agent to score variants, select base, merge best elements, and write return contract. Input: base + all variants + diff-analysis + debate-transcript. Output: `<output>/adversarial/base-selection.md` + `<output>/adversarial/merged-output.md` + `<output>/adversarial/return-contract.yaml` with `status: partial, fallback_mode: true`. Failure: abort, `failure_stage: base_selection:merge_failed`.

NOTE: This simplified fallback is not a substitute for the full adversarial pipeline. If future sc:adversarial pipeline adds steps, decompose the merged fallback steps accordingly.
```

Also update the **Acceptance Criteria** for the merged task's fallback section:

**BEFORE** (within Task 1.4 / now merged Task 1.3 AC):
```
5 fallback steps (F1-F5) each have defined input, output, and failure action
```

**AFTER**:
```
3 fallback invocations (F1, F2/3, F4/5) each have defined input, output, and failure action; F2/3 and F4/5 output labeled sections for diagnostic decomposition; compound failure_stage values used for merged steps
```

**Conflict check**:
- **reflection-final.md IMP-04** calls for expanding fallback detail to match sc:adversarial's SKILL.md step definitions. The simplification here reduces steps from 5 to 3, which is a structural conflict with IMP-04's call for more detail per step. Resolution: apply the 3-step structure from T04, but ensure each of the 3 steps has the level of prompt/input/output detail that IMP-04 requests. The 3-step simplification and the detail expansion are orthogonal -- both can be satisfied simultaneously.
- **spec-panel-roadmap-v2-review.md** does not modify the fallback protocol. No conflict.

---

## Task 4: Embed Tests 1 and 4 into Task Acceptance Criteria; Reposition Test 3

**Source reference**: T04-synthesis.md, Section 2, "Optimization 5: Embed Tests 1,3,4 into Task ACs (Score: 0.72)"

**Scope**: Modifies the Verification Plan section and the Acceptance Criteria of specific tasks. Tests 1 and 4 become AC items; Test 3 is repositioned; Tests 2 and 5 remain standalone.

**Instructions**:

### 4a. Embed Test 1 (grep one-liner) into Tasks 1.1 and 1.2 ACs

**Location**: Epic 1 task table, Task 1.1 row (sprint-spec.md line 94) and Task 1.2 row (line 95).

**BEFORE** (Task 1.1 AC):
```
`Skill` appears in allowed-tools; existing tools unchanged; `make verify-sync` passes after sync
```

**AFTER** (Task 1.1 AC):
```
`Skill` appears in allowed-tools; existing tools unchanged; `make verify-sync` passes after sync; verified by: `grep -q "Skill" src/superclaude/commands/roadmap.md` [embeds Verification Test 1]
```

**BEFORE** (Task 1.2 AC):
```
`Skill` appears in allowed-tools; existing tools unchanged
```

**AFTER** (Task 1.2 AC):
```
`Skill` appears in allowed-tools; existing tools unchanged; verified by: `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` [embeds Verification Test 1]
```

### 4b. Embed Test 4 (grep one-liner) into Task 2.4 ACs

**Location**: Epic 2 task table, Task 2.4 row (sprint-spec.md line 115).

Append to the Task 2.4 Acceptance Criteria:
```
; verified by: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns 0 [embeds Verification Test 4]
```

### 4c. Move Test 3 to immediately after Epic 3 completion

**Location**: Verification Plan section (sprint-spec.md lines 229-295).

Add a note to Test 3 (lines 257-269):

**BEFORE** (Test 3 heading area):
```
### Test 3: Return Contract Schema Consistency
```

**AFTER**:
```
### Test 3: Return Contract Schema Consistency (Run immediately after Epic 3 completion, not end-of-sprint)
```

### 4d. Mark Tests 1 and 4 as embedded in Verification Plan

Add a note to Test 1 (line 229) and Test 4 (line 271) indicating they are now embedded in task ACs but retained here as reference:

For Test 1, append after the "Expected" line:
```
**Note**: This test is now embedded in the acceptance criteria of Tasks 1.1 and 1.2 (per T04 Optimization 5). Retained here as reference.
```

For Test 4, append after the "Expected" line:
```
**Note**: This test is now embedded in the acceptance criteria of Task 2.4 (per T04 Optimization 5). Retained here as reference.
```

### 4e. Update Definition of Done Verification subsection

**Location**: sprint-spec.md lines 220-223.

No change needed to the DoD Verification checklist items themselves -- the tests still pass, they are just executed earlier via ACs. The DoD items for Tests 1 and 4 can optionally be annotated as "verified inline via task ACs."

**Conflict check**:
- **spec-panel-roadmap-v2-review.md Change 7** adds a new Verification Test 6 and a DoD item referencing it. No conflict -- Test 6 is additive and Tests 1/4 embedding does not affect it.
- **reflection-final.md IMP-05** adds a verification step 3.5 for cross-reference validation. No conflict -- this is a different test.

---

## Task 5: Defer Fallback Validation Until After Probe (Conditional)

**Source reference**: T04-synthesis.md, Section 2, "Optimization 4: Defer Fallback Validation Until After Probe (Score: 0.64)"

**Scope**: Conditionally modifies the sprint's treatment of G2 (fallback validation) and G3 (sprint variant plan) based on Task 0.0 probe results. This optimization is the most contentious (lowest score) and has conditional savings.

**IMPORTANT**: Per T04-synthesis.md Section 6 implementation guidance: "Optimization 5 (defer fallback validation) should only be applied after Task 0.0 completes and the decision gate is resolved." This task should be held until Task 0.0 is executed.

**Instructions**:

### 5a. Add conditional deferral gate to Task 0.0 decision outcomes

**Location**: Task 0.0 section (sprint-spec.md lines 62-80), specifically the "Decision gate" subsection (lines 70-74).

Append after the existing decision gate bullet points:

```
**Fallback validation deferral (per T04 Optimization 4)**:
- If Task 0.0 returns "primary path viable": Replace full G2 fallback validation test with a lightweight "smoke test" — single-input fallback run checking only that return-contract.yaml is written with valid schema (30 min instead of 1-2 hrs). The full G2 validation becomes a follow-up sprint item.
- If Task 0.0 returns "primary path blocked": G2 and G3 become mandatory and are NOT deferred. Execute full fallback validation as originally specified.
```

### 5b. Add follow-up sprint note for full G2 validation

**Location**: Future Work section (sprint-spec.md lines 182-193).

Append to the "Sprint-relevant scripts" list or add a new subsection:

```
**Deferred from this sprint (conditional on Task 0.0 "primary path viable" result)**:
- Full G2 fallback validation test (deferred from in-sprint to follow-up per T04 Optimization 4)
```

**Conflict check**:
- **reflection-final.md IMP-01** adds a Task 0.1 prerequisite validation that overlaps with Task 0.0. The T04 conditional deferral references Task 0.0 specifically. If reflection-final's Task 0.1 is also adopted, the implementer must decide whether the deferral gate references Task 0.0 or Task 0.1 results (or both, since they test different aspects). FLAG: potential conflict -- the deferral gate wording should reference whichever probe task produces the "primary path viable/blocked" determination.
- **spec-panel-roadmap-v2-review.md Change 4** adds Task 3.5 (Tier 1 quality gate), which is a form of validation. T04 Opt 4 defers a different validation (G2 fallback validation). No direct conflict, but the implementer should confirm that G2 and Task 3.5 are indeed separate concerns.

---

## Supplementary Changes

### S1. Update time estimates

**Location**: Any time estimate references throughout sprint-spec.md.

Per T04-synthesis.md Section 4, total projected savings are 3.95 hrs (26.3% of 15-hour sprint). If the sprint-spec contains an aggregate time estimate, reduce it by 3.95 hrs. No specific time estimate line was found in sprint-spec.md, so this may be a no-op unless one is added by another review document.

### S2. Add T04 optimization provenance header

**Location**: Top of sprint-spec.md, after the existing metadata.

Add a note documenting that T04 optimizations have been applied:

```
**T04 Optimizations Applied**: 5 adopted-with-modifications (Opt 1: task merge, Opt 2: amendment fold, Opt 3: fallback simplification, Opt 4: conditional deferral, Opt 5: test embedding). See T04-synthesis.md for details. Net savings: 3.95 hrs.
```

---

## Completeness Verification

### All 5 optimizations accounted for:

| Opt# | T04-synthesis.md Section | Tasklist Task | Status |
|------|-------------------------|---------------|--------|
| 1 | Merge Tasks 1.3+1.4+2.2 | Task 2 | Covered |
| 2 | Fold amendments into parent ACs | Task 1 | Covered |
| 3 | Simplify fallback 5 to 3 steps | Task 3 | Covered |
| 4 | Defer fallback validation | Task 5 | Covered (conditional) |
| 5 | Embed Tests 1,3,4 into task ACs | Task 4 | Covered |

### Location verification in sprint-spec.md:

| Target Location | Line(s) | Verified Exists |
|----------------|---------|-----------------|
| Epic 1 task table (Tasks 1.1-1.4) | 92-98 | Yes |
| Epic 2 task table (Tasks 2.1-2.4) | 110-115 | Yes |
| Epic 3 task table (Tasks 3.1-3.4) | 127-133 | Yes |
| Task 0.0 decision gate | 70-74 | Yes |
| Implementer's Quick Reference coordination note | 20 | Yes |
| Implementation Order diagram | 139-152 | Yes |
| Implementation Order coordination point | 164 | Yes |
| Risk Register (R1-R7) | 170-178 | Yes |
| Verification Plan (Tests 1-5) | 229-295 | Yes |
| Definition of Done | 196-224 | Yes |
| Future Work section | 182-193 | Yes |

### Conflict summary with other review documents:

| Conflict | Documents | Severity | Resolution |
|----------|-----------|----------|------------|
| Task 1.4 expansion vs. 3-step simplification | T04 Opt 3 vs. reflection-final IMP-04 | LOW | Both apply -- 3-step structure with expanded detail per step |
| Task merge vs. reflection recommendation | T04 Opt 1 vs. reflection-final Section 4 | NONE | Aligned -- both recommend the same merge |
| Probe task reference for deferral gate | T04 Opt 4 vs. reflection-final IMP-01 | LOW | Implementer decides whether deferral references Task 0.0 or Task 0.1 |
| Task 3.1 AC modifications | T04 Opt 2 (amendment fold) vs. spec-panel Change 1 | LOW | Apply spec-panel Change 1 first, then fold T02 amendments |
| Risk R5 post-merge status | T04 Opt 1 vs. sprint-spec R5 | LOW | Add note to R5 that merge mitigates this risk |

---

*Tasklist generated 2026-02-23. Source: T04-synthesis.md (5 adopted optimizations). Target: sprint-spec.md.*
*Cross-referenced against: reflection-final.md, spec-panel-roadmap-v2-review.md.*
