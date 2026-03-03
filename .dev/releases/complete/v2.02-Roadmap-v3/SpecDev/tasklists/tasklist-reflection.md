# Tasklist: Apply reflection-final.md Changes to sprint-spec.md

**Source**: `.dev/releases/current/v2.01-Roadmap-v3/reflection-final.md`
**Target**: `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md`
**Generated**: 2026-02-23

---

## Section A: Prioritized Improvements (IMP-01 through IMP-08)

### Task 1: Insert Task 0.1 — Prerequisite Validation

**Source**: reflection-final.md Section 1, IMP-01
**Action**: INSERT new section
**Anchor**: After the `---` horizontal rule that follows Task 0.0's closing line (sprint-spec.md line 81), and BEFORE the `## Epic 1:` heading (line 84)
**Content**: Apply the IMP-01 "Specific change to sprint-spec.md" code block VERBATIM (the `## Task 0.1: Prerequisite Validation ...` block from reflection-final.md lines 22-43). Insert a `---` horizontal rule after the new section to maintain visual separation before Epic 1.

**Additionally**: In the Implementation Order diagram (sprint-spec.md lines 139-152), update the flow to show Task 0.1 between Task 0.0 and Epic 1. Change:

```
BEFORE: Task 0.0 (Skill Tool Probe) ─── decision gate
AFTER:  Task 0.0 (Skill Tool Probe) ─── decision gate
          |
          +──> Task 0.1 (Prerequisite Validation) ─── blocks Epic 1
```

---

### Task 2: Add Alternative Paths to Epic 1 Task 1.3

**Source**: reflection-final.md Section 1, IMP-02
**Action**: MODIFY Task 1.3 in the Epic 1 tasks table
**Location**: sprint-spec.md line 96, the Task 1.3 row in the Epic 1 table

Apply the IMP-02 "Specific change" code block (reflection-final.md lines 56-65) by appending the Option A / Option B structure to Task 1.3's "Change" column. The existing text describing the Task-agent Skill invocation becomes Option B. Option A (direct Skill tool call from main agent) is added as preferred path per the source.

Specifically, in the "Change" cell of row 1.3, after the current text ending with `...output expectation is specified`, append a line break and the following (from reflection-final.md):

```
Option A (preferred if Task 0.1 confirms): Direct Skill tool call from main agent — the main sc:roadmap agent calls the Skill tool directly with skill: "sc:adversarial", args: "..." — no Task agent intermediary.
Option B (fallback): Task-agent-mediated invocation — as currently specified above.
```

---

### Task 3: Rewrite Task 2.4 Acceptance Criteria

**Source**: reflection-final.md Section 1, IMP-03
**Action**: MODIFY Task 2.4 acceptance criteria
**Location**: sprint-spec.md line 115, the Task 2.4 row in the Epic 2 table

The current acceptance criteria text already reflects the IMP-03 fix. Verify that the acceptance criteria column for Task 2.4 contains the corrected language from IMP-03 (reflection-final.md lines 87-91):

> "All standalone invocation examples are wrapped in Skill tool call format; the args string within Skill tool calls MAY contain `--flag` syntax"

**Status**: Sprint-spec.md line 115 already contains this language. **NO CHANGE NEEDED** — the spec was already updated. Mark this task as PRE-APPLIED.

---

### Task 4: Expand Task 1.4 Fallback with Agent Prompt Detail

**Source**: reflection-final.md Section 1, IMP-04
**Action**: MODIFY Task 1.4 in the Epic 1 tasks table
**Location**: sprint-spec.md line 97, the Task 1.4 row

IMP-04 states that Task 1.4's five fallback steps (F1-F5) lack prompt templates, inter-agent data passing, and pass/fail criteria at the same level of detail as sc:adversarial's SKILL.md Step 1-5 definitions.

The source does NOT provide verbatim replacement text. The implementer must:

1. Read sc:adversarial's SKILL.md pipeline steps 1-5 (the full step definitions, not just the names)
2. For each of the 5 fallback steps (F1 Variant Generation, F2 Diff Analysis, F3 Single-Round Debate, F4 Base Selection, F5 Merge + Contract), add to the Task 1.4 "Change" column:
   - A prompt template for the Task agent (what the agent is told to do)
   - Input data specification (exact file paths or globs the agent reads)
   - Output artifact path (exact file path the agent writes)
   - Pass/fail criteria (how to determine if the step succeeded)
3. These additions go inside the existing F1-F5 structure in Task 1.4's "Change" cell

---

### Task 5: Add Verification Test 3.5 — Cross-Reference Validation

**Source**: reflection-final.md Section 1, IMP-05
**Action**: INSERT new verification test
**Anchor**: After Verification Test 3 (sprint-spec.md line 269, after the `**Expected**: Identical field sets...` paragraph) and BEFORE `### Test 4: Pseudo-CLI Elimination` (line 271)

Insert the following (from reflection-final.md lines 112-117), adapting to match the existing test format:

```markdown
### Test 3.5: Cross-Reference Field Consistency

**Purpose**: Validate that the fields referenced in Wave 2 step 3e (consumer) match the fields defined in sc:adversarial's Return Contract section (producer).

**Method**: Manual cross-reference.

1. List all fields referenced in Wave 2 step 3e (status, convergence_score, etc.)
2. List all fields defined in sc:adversarial SKILL.md Return Contract section
3. Confirm: every field referenced by the consumer exists in the producer schema
4. Confirm: the convergence threshold in step 3e (0.6) matches the threshold in adversarial-integration.md status routing (60%)

**Expected**: All consumer-referenced fields exist in the producer schema. Thresholds are consistent.
```

**Additionally**: Add a corresponding checkbox to the Definition of Done, Verification section (sprint-spec.md line 224). After the line `- [ ] Verification Test 3 passes ...`, insert:
```
- [ ] Verification Test 3.5 passes (cross-reference field consistency between Wave 2 step 3e and Return Contract schema)
```

---

### Task 6: Resolve `unresolved_conflicts` Type Inconsistency

**Source**: reflection-final.md Section 1, IMP-06
**Action**: ADD a decision note to Task 3.1
**Location**: sprint-spec.md line 129, the Task 3.1 row

The sprint-spec already uses `integer` for `unresolved_conflicts` in Task 3.1 (line 129: "unresolved_conflicts (integer or null)"). The inconsistency is with sc:adversarial SKILL.md line 349 which types it as `list[string]`.

Add a note to Task 3.1's "Change" cell, after the existing `unresolved_conflicts` field definition:

```
BEFORE: `unresolved_conflicts` (integer or null),
AFTER:  `unresolved_conflicts` (integer or null — NOTE: sc:adversarial SKILL.md line 349 currently types this as `list[string]`; resolve to `integer` during implementation per reflection-final.md IMP-06),
```

**Status**: Task 3.1 already specifies `integer`. The note makes the known inconsistency explicit for the implementer. The actual fix happens in sc:adversarial SKILL.md during implementation, not in sprint-spec.md.

---

### Task 7: Flag Implementation Reorder as Decision Point

**Source**: reflection-final.md Section 1, IMP-07
**Action**: ADD decision-point note to Implementation Order section
**Location**: sprint-spec.md lines 137-164, the "Implementation Order" section

IMP-07 proposes reordering: Task 0.1 -> Epic 1 (1.1-1.2) -> Epic 3 -> Epic 1 (1.3-1.4) + Epic 2.

This is flagged as OPTIONAL. Do NOT rewrite the implementation order. Instead, insert the following note after the `**Rationale**:` block (after line 163, before the `**Critical coordination point**` paragraph):

```markdown
**Alternative ordering (decision point)**: reflection-final.md IMP-07 proposes: Task 0.1 -> Epic 1 Tasks 1.1-1.2 -> Epic 3 -> Epic 1 Tasks 1.3-1.4 + Epic 2 (unified). Rationale: Epic 3 defines the contract that Epic 2 references; implementing Epic 3 first gives Epic 2 a concrete schema instead of a forward reference. Evaluate at sprint start.
```

---

### Task 8: IMP-08 — No Change Required

**Source**: reflection-final.md Section 1, IMP-08
**Action**: NONE
**Rationale**: IMP-08 is informational only. It notes that ranked-root-causes.md omits `schema_version` from its example YAML, but sprint-spec.md Task 3.1 already correctly specifies all 9 fields. No change to sprint-spec.md.

---

## Section B: Kill List Changes

### Task 9: Consolidate Sync Tasks 1.5, 2.5, 3.5 into Single Post-Sprint Task

**Source**: reflection-final.md Section 2, "Sprint Sync Tasks"
**Action**: VERIFY already applied; ADD consolidated Task 4.1 if missing
**Location**: sprint-spec.md lines 98, 133

The sprint-spec already shows Tasks 1.5 and 3.5 as struck through (`~~1.5~~`, `~~3.5~~`) with "Consolidated into post-edit step" notes. There is no Task 2.5 row (Epic 2 has no sync task).

Verify the Implementer's Quick Reference (sprint-spec.md line 18) contains the consolidated sync instruction: `make sync-dev && make verify-sync`. It does.

**Status**: PRE-APPLIED. The consolidation is already reflected in sprint-spec.md. No change needed.

---

### Task 10: Trim DVL Section — Cut and Defer Scripts

**Source**: reflection-final.md Section 2, "DVL Scripts to Cut or Defer"
**Action**: MODIFY the DVL section
**Location**: sprint-spec.md lines 182-192, "Future Work: Deterministic Verification Layer (DVL)"

The current DVL section lists 3 sprint-relevant scripts. Per the kill list:
- KEEP: `verify_allowed_tools.py`, `validate_return_contract.py`, `validate_wave2_spec.py` (already listed)
- DEFER: `verify_pipeline_completeness.sh`, `dependency_gate.sh`, `check_file_references.py`, `generate_checkpoint.py`
- CUT: `content_hash_tracker.py`, `verify_numeric_scores.py`, `context_rot_canary.py`

The sprint-spec only lists the 3 KEEP scripts. The deferred/cut scripts are only in DVL-BRAINSTORM.md.

**Status**: Sprint-spec.md already only lists the 3 KEEP scripts. No change needed to sprint-spec.md.

**Additional change per kill list**: Add a note after line 191:

```markdown
**Deferred scripts** (not sprint-critical): `verify_pipeline_completeness.sh`, `dependency_gate.sh`, `check_file_references.py`, `generate_checkpoint.py`. See reflection-final.md Section 2 for rationale.
**Cut scripts** (redundant for this sprint): `content_hash_tracker.py`, `verify_numeric_scores.py`, `context_rot_canary.py`.
```

---

### Task 11: Add Note to Defer AH Techniques

**Source**: reflection-final.md Section 2, "Anti-Hallucination Techniques to Defer"
**Action**: ADD note to DVL section
**Location**: sprint-spec.md line 192, after the last DVL script entry and before the `---` separator

Insert:

```markdown
**Anti-hallucination techniques (AH-1 through AH-6)**: Deferred. These are design patterns for future DVL scripts, not sprint deliverables. See `dvl-design-notes.md` or DVL-BRAINSTORM.md for details.
```

---

## Section C: Integration Blind Spots

### Task 12: Add Cross-Reference Comment for Epic 2/3 Boundary

**Source**: reflection-final.md Section 4, "Epic 2 / Epic 3 Boundary"
**Action**: MODIFY Task 2.2 acceptance criteria
**Location**: sprint-spec.md line 113, Task 2.2 row

In the Task 2.2 "Acceptance Criteria" cell, after the existing text, append:

```
; step 3e includes inline comment referencing the canonical schema location: "# Contract schema: see src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section"
```

---

### Task 13: Add Merge Recommendation for Tasks 1.3/1.4/2.2

**Source**: reflection-final.md Section 4, "Epic 1 / Epic 2 Overlap"
**Action**: STRENGTHEN the existing coordination note
**Location**: sprint-spec.md line 164, the "Critical coordination point" paragraph

The current text already says these must be "a single atomic rewrite" and "assign one author." The reflection recommends formally merging them into a single task.

Replace:

```
BEFORE: **Critical coordination point**: Epic 1 tasks 1.3-1.4 and Epic 2 task 2.2 all modify Wave 2 step 3 in `src/superclaude/skills/sc-roadmap/SKILL.md`. These must be implemented as a single atomic rewrite to avoid merge conflicts and contradictory instructions. Assign one author to the Wave 2 step 3 rewrite, incorporating requirements from both epics.

AFTER: **Critical coordination point**: Epic 1 tasks 1.3-1.4 and Epic 2 task 2.2 all modify Wave 2 step 3 in `src/superclaude/skills/sc-roadmap/SKILL.md`. These MUST be implemented as a single atomic rewrite by one author. **Recommendation (reflection-final.md Section 4)**: Formally merge Tasks 1.3, 1.4, and 2.2 into a single task ("Task 1.3: Rewrite Wave 2 step 3 with Skill invocation, fallback, atomic sub-steps, and glossary verbs"). Task 2.2 becomes the implementation vehicle; Tasks 1.3 and 1.4 are specification inputs.
```

---

### Task 14: Sequence Task 3.2 Before Task 2.4

**Source**: reflection-final.md Section 4, "adversarial-integration.md Dual Role"
**Action**: ADD sequencing note
**Location**: sprint-spec.md, Implementation Order section, after the new "Alternative ordering" note added in Task 7 (or after line 163 if Task 7 is not applied)

Insert:

```markdown
**File conflict avoidance**: Task 3.2 (adds new section to adversarial-integration.md) must complete before Task 2.4 (modifies existing sections in the same file). This prevents parallel-edit conflicts. See reflection-final.md Section 4, "adversarial-integration.md Dual Role."
```

---

## Section D: Uncovered Failure Modes

### Task 15: Add 5 Failure Modes to Risk Register

**Source**: reflection-final.md Section 6, "Failure Modes NOT Covered" (items 1-5)
**Action**: INSERT 5 new rows into the Risk Register table
**Location**: sprint-spec.md lines 169-178, after the last risk row (R7) and before the `---` separator (line 180)

Add the following rows to the Risk Register table. The descriptions are summarized here; implementer should reference reflection-final.md Section 6 for full context:

```markdown
| R8 | sc:adversarial execution timeout — adversarial pipeline may take 10+ minutes; if Skill tool call times out, return contract may not be written | reflection-final.md Section 6, item 1 | MEDIUM (0.25) | MEDIUM -- return contract missing on timeout | Add timeout handling guidance to Task 1.3/2.2 Skill tool call; document expected duration range |
| R9 | Context window exhaustion during sc:adversarial — multiple full-text variants may exhaust context; write-on-failure may not execute | reflection-final.md Section 6, item 2 | LOW (0.20) | HIGH -- silent total failure | Document as known limitation; consider spec size warnings in sc:roadmap |
| R10 | Partial file writes — return-contract.yaml may be malformed YAML if sc:adversarial crashes mid-write | reflection-final.md Section 6, item 3 | LOW (0.15) | MEDIUM -- parse error in step 3e | Step 3e routing should attempt YAML parsing and treat parse errors as `status: failed` |
| R11 | Recursive skill invocation — sc:roadmap -> sc:adversarial -> (another skill) could hit platform depth limits | reflection-final.md Section 6, item 4 | LOW (0.10) | LOW -- theoretical edge case | Document invocation depth limit of 1 (no nested skill calls from sc:adversarial) |
| R12 | Deferred root causes RC3/RC5 surfacing as second-order failures — correct wiring but wrong agent selection within sc:adversarial | reflection-final.md Section 6, item 5 | MEDIUM (0.30) | MEDIUM -- degraded output quality | Flag as post-sprint monitoring item; add to follow-up sprint scope |
```

---

### Task 16: Add YAML Parse Error Handling to Task 2.2 Step 3e

**Source**: reflection-final.md Section 6, item 3 (partial file writes)
**Action**: MODIFY Task 2.2 acceptance criteria
**Location**: sprint-spec.md line 113, Task 2.2 row, "Acceptance Criteria" column

After the existing acceptance criterion about the missing-file guard, append:

```
; step 3e treats YAML parse errors in return-contract.yaml as `status: failed` with `failure_stage: transport`
```

---

## Section E: Completeness Verification

### Checklist: All reflection-final.md items accounted for

| Source Section | Item | Tasklist Entry | Status |
|---|---|---|---|
| Section 1 | IMP-01 (Task 0.1) | Task 1 | Covered |
| Section 1 | IMP-02 (Alternative paths) | Task 2 | Covered |
| Section 1 | IMP-03 (Pseudo-CLI paradox) | Task 3 | Pre-applied |
| Section 1 | IMP-04 (Fallback detail) | Task 4 | Covered |
| Section 1 | IMP-05 (Verification 3.5) | Task 5 | Covered |
| Section 1 | IMP-06 (unresolved_conflicts type) | Task 6 | Covered |
| Section 1 | IMP-07 (Reorder) | Task 7 | Covered (decision point) |
| Section 1 | IMP-08 (schema_version) | Task 8 | No change needed |
| Section 2 | DVL scripts cut/defer | Task 10 | Covered |
| Section 2 | AH techniques defer | Task 11 | Covered |
| Section 2 | Sync task consolidation | Task 9 | Pre-applied |
| Section 3 | DVL feasibility (top 3) | N/A | Informational only; no sprint-spec.md change needed |
| Section 4 | Epic 2/3 boundary | Task 12 | Covered |
| Section 4 | Epic 1/2 overlap (merge) | Task 13 | Covered |
| Section 4 | adversarial-integration.md dual role | Task 14 | Covered |
| Section 5 | Prerequisite test | Task 1 | Covered (subsumed by IMP-01 Task 0.1) |
| Section 6 | 5 failure modes | Tasks 15, 16 | Covered |
| Section 7 | Confidence assessment | N/A | Informational; no sprint-spec.md change |

### Gaps Identified

**None.** All actionable recommendations from reflection-final.md are accounted for in this tasklist. Sections 3 (DVL Feasibility), 5 (Prerequisite Test, which is the detailed version of IMP-01), and 7 (Confidence Assessment) are informational/analytical and do not require changes to sprint-spec.md.

---

## Implementation Order for This Tasklist

Recommended sequence (dependencies noted):

1. **Task 1** (IMP-01: Task 0.1) — structural addition, no dependencies
2. **Task 2** (IMP-02: Alternative paths) — modifies Task 1.3
3. **Task 4** (IMP-04: Fallback detail) — modifies Task 1.4
4. **Task 5** (IMP-05: Verification 3.5) — structural addition
5. **Task 6** (IMP-06: type note) — minor addition to Task 3.1
6. **Task 7** (IMP-07: reorder note) — addition to Implementation Order
7. **Task 10** (DVL trim note) — addition to DVL section
8. **Task 11** (AH defer note) — addition to DVL section (after Task 10)
9. **Task 12** (Epic 2/3 cross-ref) — modifies Task 2.2 acceptance criteria
10. **Task 16** (YAML parse error) — also modifies Task 2.2 acceptance criteria (combine with Task 12)
11. **Task 13** (Merge recommendation) — modifies Critical coordination point
12. **Task 14** (Sequencing note) — addition to Implementation Order (after Task 7)
13. **Task 15** (5 failure modes) — addition to Risk Register
14. **Tasks 3, 8, 9** — no changes needed (pre-applied or informational)

---

*Tasklist generated 2026-02-23 from reflection-final.md analysis.*
*16 tasks total: 11 requiring changes, 2 pre-applied, 3 no-change-needed.*
