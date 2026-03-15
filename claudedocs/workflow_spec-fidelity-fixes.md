# Workflow: Implement Spec-Fidelity Fixes for v2.24.5 Roadmap

**Source**: `.dev/releases/current/v2.24.5/spec-fidelity.md`
**Target**: `.dev/releases/current/v2.24.5/roadmap.md`
**Goal**: Patch 14 deviations (3 HIGH, 8 MEDIUM, 3 LOW) so `tasklist_ready` flips to `true`
**Command**: `sc:task-unified` (each task below is a discrete invocation)
**Status**: PLAN ONLY — no code or file changes occur until `/sc:implement` is invoked

---

## Context Summary

The `spec-fidelity.md` report found that `roadmap.md` is structurally sound but contains
constraint-specificity losses that make it unsafe to generate a tasklist from. The fixes are
**edits to `roadmap.md` only** — no source code is touched in this workflow. The goal is to
make the roadmap a faithful, verifiable translation of the spec so that a downstream tasklist
generator can produce unambiguous implementation tasks.

Three HIGH deviations block tasklist generation:
- **DEV-001**: OQ-4 mislabel on Task 1.2.2 risks deferral of a mandatory assertion
- **DEV-003**: Missing verbatim comment text for the `<=` operator guard
- **DEV-008**: `<=` operator semantics absent from implementation task 1.2.3

All remaining MEDIUM/LOW deviations should be resolved in the same pass to produce a clean,
fully traceable roadmap.

---

## Phase 0: Setup and Verification

**Objective**: Confirm the roadmap file can be safely edited and all deviation IDs are mapped
to precise edit locations before any changes are made.

### Task W-0.1 — Map deviation IDs to roadmap line locations

```
/sc:task-unified "Read roadmap.md at .dev/releases/current/v2.24.5/roadmap.md and
produce a mapping of each deviation ID (DEV-001 through DEV-014) from spec-fidelity.md
to the exact task row(s) or section(s) in roadmap.md that require editing. Output as a
table: deviation ID | roadmap section | roadmap task # | edit type (add/modify/remove).
Do not edit any files." --compliance exempt --verify skip
```

**Exit criterion**: Table produced with all 14 deviations mapped. No files changed.

---

## Phase 1: HIGH Severity Fixes (Blocking — Must Complete First)

These three fixes are required before `tasklist_ready` can flip to `true`. They must be
applied in order as each builds on a clean prior state.

### Task W-1.1 — Fix DEV-001: Remove OQ-4 mislabel from Task 1.2.2

**Deviation**: Task 1.2.2 in roadmap.md carries `| OQ-4 |` in its OQ column. The spec's
OQ-4 concerns non-inheriting executors and `--tools default`, not this assertion. The
assertion is a hard FR-ATL.1 requirement, not an open question.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.2.2:
1. Remove the OQ-4 reference from the task row's OQ column (replace with — or blank)
2. Add placement constraint to the Detail column: assertion must appear immediately after
   the three constant definitions (not elsewhere in the module)
3. Add required error message content: the error message must state the kernel margin
   rationale and the measured template peak (~3.4 KB)
Spec reference: FR-ATL.1. Do not change any other tasks." --compliance standard --verify standard
```

**Exit criterion**: Task 1.2.2 OQ column shows `—`. Detail column includes placement
constraint and error message content requirement. OQ-4 only appears in Phase 1.5 Task 1.5.5
where it belongs.

---

### Task W-1.2 — Fix DEV-003 and DEV-008: Add verbatim comment text and `<=` operator requirement to Task 1.2.3

**Deviation (DEV-003)**: Task 1.2.3 says "Add `<=` intentionality comment" but omits the
verbatim text mandated by FR-ATL.2 acceptance criteria.
**Deviation (DEV-008)**: The `<=` operator requirement appears only in test Task 1.2.6, not
in the implementation task where the operator must be chosen.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.2.3:
1. Replace 'Add <= intentionality comment' with the verbatim required comment text from
   FR-ATL.2: '<= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below
   MAX_ARG_STRLEN = 128 KB'
2. Add to the Detail column: 'Use <= operator (not <) — boundary semantics require
   at-limit inputs to embed inline, not trigger fallback'
Spec references: FR-ATL.2 acceptance criterion (operator choice), FR-ATL.2 acceptance
criterion (verbatim comment). Do not change any other tasks." --compliance standard --verify standard
```

**Exit criterion**: Task 1.2.3 Detail contains verbatim comment text and explicit `<=`
operator requirement. Boundary semantics are documented at the point of implementation, not
only in the test task.

---

## Phase 2: MEDIUM Severity Fixes

Apply all eight MEDIUM deviations. Tasks W-2.1 through W-2.6 are independent edits to
different sections of roadmap.md and can be executed sequentially (single file, serial edits
are safest).

### Task W-2.1 — Fix DEV-002: Expand per-constant comment requirements in Task 1.2.1

**Deviation**: "Each with inline derivation comment" is too generic. Each constant has
specific required comment content per FR-ATL.1.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.2.1:
Expand 'Each with inline derivation comment' to enumerate per-constant requirements:
- _MAX_ARG_STRLEN: comment must state it is the Linux kernel compile-time constant
- _PROMPT_TEMPLATE_OVERHEAD: comment must note the 2.3x safety factor and the
  measured template peak (~3.4 KB)
- _EMBED_SIZE_LIMIT: comment must note its derivation (MAX_ARG_STRLEN minus overhead)
  and the resulting byte value (120 KB = 122,880 bytes)
Spec reference: FR-ATL.1 per-constant comment requirements. Do not change other tasks." --compliance standard --verify standard
```

---

### Task W-2.2 — Fix DEV-004: Foreground import-and-use requirement in Task 1.2.4

**Deviation**: "Import and use the constant" is present but buried. Should be a checklist
item to ensure traceability with FR-ATL.3 acceptance criterion.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.2.4:
Add an explicit checklist item or sub-requirement: 'Test must import _EMBED_SIZE_LIMIT
from executor and use it in assertions (auto-adapts to new value — no hardcoded bytes)'.
This is required by FR-ATL.3 acceptance criterion. Do not change other tasks." --compliance light --verify skip
```

---

### Task W-2.3 — Fix DEV-005: Add test method name to Task 1.2.5

**Deviation**: Task 1.2.5 names the class (`TestComposedStringGuard`) but not the test
method name (`test_prompt_plus_embedded_exceeds_limit`) required by spec Section 8.1.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.2.5:
Add test method name to the Detail column: the test method must be named
'test_prompt_plus_embedded_exceeds_limit' (per spec Section 8.1 test table).
Also add class name confirmation: class is 'TestComposedStringGuard' (per Section 4.2).
Spec reference: Section 8.1 test inventory. Do not change other tasks." --compliance light --verify skip
```

---

### Task W-2.4 — Fix DEV-006: Surface Phase 1.3 rename as a parallel task (not embedded in 1.2)

**Deviation**: The spec calls Task 1.3 (rename test in test_file_passing.py) a parallel task
with Phase 1.2. Roadmap embeds it inside Phase 1.2 as Task 1.2.4, hiding the parallelization
opportunity.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md:
1. Extract the rename content from Task 1.2.4 into a new Phase 1.3 section after Phase 1.2
2. Title the section 'Phase 1.3: FR-ATL.3 — Rename Test (Parallel with Phase 1.2)'
3. Add note that this task can execute concurrently with Phase 1.2 on a multi-person team
4. Remove the rename content from Task 1.2.4 (keep only the docstring update and
   import-and-use requirement there)
Spec reference: Section 4.6 Phase ordering '[parallel with 1.2]'. Preserve all existing
task content — only reorganize." --compliance standard --verify standard
```

---

### Task W-2.5 — Fix DEV-007: Add CLI FAILURE as third named outcome in Task 0.4

**Deviation**: Task 0.4 documents only WORKING and BROKEN outcomes. The spec defines a
third mandatory outcome — CLI FAILURE (exit non-zero) — with a specific resolution path.
Without it, an implementer may misclassify a CLI configuration error as BROKEN and
incorrectly activate Phase 1.5.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 0.4:
Add CLI FAILURE as a third named outcome with this resolution path:
'CLI FAILURE: subprocess exits non-zero for any reason. Do NOT record WORKING or BROKEN.
Resolve CLI configuration issue and re-run Task 0.1 before proceeding.'
Spec reference: Section defining three named outcomes (exit code 0 only). Do not change
other tasks." --compliance standard --verify standard
```

---

### Task W-2.6 — Fix DEV-009: Add parameterization requirement to Task 1.5.6

**Deviation**: Task 1.5.6 names both conditional tests but omits the parameterization
requirement from spec Section 8.1: `test_inline_embed_fallback_when_file_broken` must be
parameterized over each of the three affected executors' `_EMBED_SIZE_LIMIT` values.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.5.6:
Add parameterization requirement to Detail column:
'test_inline_embed_fallback_when_file_broken must be parameterized over each of the
three affected conditional executors (remediate_executor, validate_executor,
tasklist/executor) using their respective _EMBED_SIZE_LIMIT values'
Spec reference: Section 8.1 '(new, parameterized)' annotation. Do not change other tasks." --compliance light --verify skip
```

---

### Task W-2.7 — Fix DEV-011: Add cross-reference note for phase numbering misalignment

**Deviation**: Spec Phase 3 validation tasks appear in roadmap Phase 2. Phase numbering
mismatch could confuse cross-reference during implementation reviews.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Phase 2 section header:
Add a cross-reference note immediately after the Phase 2 heading:
'Note: The validation tasks in this phase correspond to spec Section 4.6 Phase 3
(Full Validation). Phase numbering differs from the spec — spec Phase 3 tasks 3.1,
3.4, and 3.5 appear here as roadmap Tasks 2.1, 2.2, and 2.3 respectively.'
Do not change any task content." --compliance light --verify skip
```

---

### Task W-2.8 — Fix DEV-012: Add conditional note to Task 2.1 for Phase 1.5 test files

**Deviation**: Task 2.1 runs `tests/roadmap/` broadly but does not flag that Phase 1.5
test files (`test_remediate_executor.py`, `test_inline_fallback.py`) only exist if
Phase 1.5 was activated.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 2.1:
Add conditional note to Detail column: 'Note: test_remediate_executor.py and
test_inline_fallback.py within tests/roadmap/ only exist if Phase 1.5 was activated
(Phase 0 = BROKEN). Their absence when Phase 0 = WORKING is expected and not a failure.'
Spec reference: Section 8.2 conditional integration test note. Do not change other tasks." --compliance light --verify skip
```

---

## Phase 3: LOW Severity Fixes

Three low-severity deviations. All are additive clarifications — no content removal.

### Task W-3.1 — Fix DEV-010: Add test method name to Task 1.2.5 (cross-reference)

> Note: DEV-005 (W-2.3) already adds the method name. DEV-010 is the complementary
> concern that both class name and method name appear together for full traceability between
> spec Sections 4.2 and 8.1. Verify W-2.3 covered both before running this task.

```
/sc:task-unified "Read .dev/releases/current/v2.24.5/roadmap.md Task 1.2.5 and
confirm it contains both:
1. Class name: TestComposedStringGuard (Section 4.2)
2. Method name: test_prompt_plus_embedded_exceeds_limit (Section 8.1)
If both are present (from W-2.3), mark this task complete with no changes.
If either is missing, add the missing name to the Detail column." --compliance exempt --verify skip
```

---

### Task W-3.2 — Fix DEV-013: Label OQ-5 as a roadmap addition

**Deviation**: Task 0.2 introduces OQ-5 not present in spec Section 11 open items.
The addition is beneficial but should be labeled so it is not confused with spec-derived OQs.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 0.2:
Add annotation to the OQ column entry for OQ-5: change '| OQ-5 |' to
'| OQ-5 (roadmap addition) |' or add a footnote: 'OQ-5 is a roadmap-added discovery
task; it does not appear in spec Section 11 Open Items. Related to OQ-1 (--file behavior).'
Do not change other tasks." --compliance light --verify skip
```

---

### Task W-3.3 — Fix DEV-014: Label OQ-6 as a roadmap addition

**Deviation**: Task 1.1.1 introduces OQ-6 not present in spec Section 11. The task itself
is appropriate (it implements RISK-002 mitigation) but the OQ label is non-standard.

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/roadmap.md Task 1.1.1:
Change '| OQ-6 |' to '| OQ-6 (roadmap addition) |' or add a footnote:
'OQ-6 is a roadmap-added verification step implementing RISK-002 mitigation from
spec Section 7. It does not appear in spec Section 11 Open Items.'
Do not change other tasks." --compliance light --verify skip
```

---

## Phase 4: Validation

### Task W-4.1 — Update spec-fidelity.md header to reflect resolved status

```
/sc:task-unified "Edit .dev/releases/current/v2.24.5/spec-fidelity.md front-matter:
Change 'tasklist_ready: false' to 'tasklist_ready: true'.
Add field: 'fixes_applied: true'
Add field: 'fixes_workflow: claudedocs/workflow_spec-fidelity-fixes.md'
Only change the YAML front-matter block (lines 1-8). Do not edit the deviation report body." --compliance light --verify skip
```

---

### Task W-4.2 — Verify roadmap consistency after all edits

```
/sc:task-unified "Read .dev/releases/current/v2.24.5/roadmap.md in full and verify:
1. Task 1.2.2 OQ column shows — (not OQ-4)
2. Task 1.2.3 contains verbatim comment: '<= is intentional; _EMBED_SIZE_LIMIT = 120 KB
   is safely below MAX_ARG_STRLEN = 128 KB'
3. Task 1.2.3 contains explicit <= operator requirement
4. Task 1.2.1 has per-constant comment requirements (not generic 'derivation comment')
5. Task 0.4 has CLI FAILURE as a third named outcome
6. Phase 1.5 Task 1.5.6 has parameterization requirement
7. OQ-5 and OQ-6 are labeled as roadmap additions
8. Phase 1.3 rename task exists as a parallel section (or equivalent note)
9. Phase 2 has cross-reference note to spec Phase 3
10. Task 2.1 has conditional note about Phase 1.5 test files
Report pass/fail for each check. Do not modify any files." --compliance exempt --verify skip
```

**Exit criterion**: All 10 checks pass. If any fail, re-run the corresponding W-x.x task.

---

## Execution Order and Dependencies

```
W-0.1 (mapping)
  │
  ├── W-1.1 (DEV-001: OQ-4 removal)       ← HIGH, must be first
  ├── W-1.2 (DEV-003 + DEV-008: <= comment) ← HIGH, must be first
  │
  ├── W-2.1 (DEV-002: per-constant comments)
  ├── W-2.2 (DEV-004: import foreground)
  ├── W-2.3 (DEV-005: test method name)
  ├── W-2.4 (DEV-006: Phase 1.3 extraction)  ← structural, do after W-2.3
  ├── W-2.5 (DEV-007: CLI FAILURE outcome)
  ├── W-2.6 (DEV-009: parameterization)
  ├── W-2.7 (DEV-011: phase numbering note)
  ├── W-2.8 (DEV-012: conditional test note)
  │
  ├── W-3.1 (DEV-010: verify class+method both present)  ← after W-2.3
  ├── W-3.2 (DEV-013: OQ-5 label)
  ├── W-3.3 (DEV-014: OQ-6 label)
  │
  ├── W-4.1 (update spec-fidelity.md header)
  └── W-4.2 (consistency verification)
```

**Parallelization opportunities**:
- W-2.1 through W-2.3 and W-2.5 through W-2.8 are independent edits to different sections
  and could run concurrently, but serial execution is recommended for a single file to
  prevent edit conflicts.
- W-3.2 and W-3.3 are independent of everything except W-0.1.

**Hard sequential constraints**:
- W-1.1 and W-1.2 must complete before W-4.2 validation
- W-2.3 must complete before W-3.1 (W-3.1 verifies W-2.3's output)
- W-2.4 must come after W-2.3 (Phase 1.3 extraction depends on 1.2.4 being correct first)
- W-4.1 must be last (do not flip tasklist_ready until W-4.2 passes)

---

## Summary

| Phase | Tasks | Deviations | Compliance Tier |
|-------|-------|------------|-----------------|
| Phase 0 | W-0.1 | — | EXEMPT |
| Phase 1 (HIGH) | W-1.1, W-1.2 | DEV-001, DEV-003, DEV-008 | STANDARD |
| Phase 2 (MEDIUM) | W-2.1 – W-2.8 | DEV-002, DEV-004 – DEV-007, DEV-009, DEV-011, DEV-012 | STANDARD / LIGHT |
| Phase 3 (LOW) | W-3.1 – W-3.3 | DEV-010, DEV-013, DEV-014 | EXEMPT / LIGHT |
| Phase 4 (Validate) | W-4.1, W-4.2 | — | LIGHT / EXEMPT |

**Total tasks**: 14 (1 mapping + 2 HIGH fixes + 8 MEDIUM fixes + 3 LOW fixes + 2 validation)
**Files modified**: `roadmap.md` (all edits), `spec-fidelity.md` (header only, W-4.1)
**No source code is modified in this workflow.**
