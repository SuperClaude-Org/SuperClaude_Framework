# D-0021: TodoWrite Integration — 23 Subphase Tasks and Checkpoint Wiring

**Task**: T02.10
**Roadmap Items**: R-044, R-045, R-046, R-047
**Date**: 2026-03-08
**Depends On**: D-0014 through D-0019 (Phase 0-1 implementation must exist)

---

## 1. 23 Subphase Task Definitions (FR-051)

### Phase 0: Prerequisites (5 tasks)

| # | Task ID | Content | Active Form | Phase |
|---|---------|---------|-------------|-------|
| 1 | P0-01 | Resolve workflow path and discover components | Resolving workflow path | 0 |
| 2 | P0-02 | Capture live API snapshot with hash | Capturing API snapshot | 0 |
| 3 | P0-03 | Check output directory for collisions | Checking for collisions | 0 |
| 4 | P0-04 | Scan for unsupported patterns | Scanning for unsupported patterns | 0 |
| 5 | P0-05 | Emit portify-prerequisites.yaml contract | Emitting Phase 0 contract | 0 |

### Phase 1: Workflow Analysis (7 tasks)

| # | Task ID | Content | Active Form | Phase |
|---|---------|---------|-------------|-------|
| 6 | P1-01 | Build component inventory with C-NNN IDs | Building component inventory | 1 |
| 7 | P1-02 | Decompose steps with S-NNN IDs | Decomposing workflow steps | 1 |
| 8 | P1-03 | Classify steps (programmatic/claude/hybrid) | Classifying steps | 1 |
| 9 | P1-04 | Build dependency DAG and validate acyclicity | Building dependency DAG | 1 |
| 10 | P1-05 | Assign gate tiers and modes | Assigning gates | 1 |
| 11 | P1-06 | Run 7 self-validation checks | Running self-validation | 1 |
| 12 | P1-07 | Present analysis for user review | Awaiting user review | 1 |

### Phase 2: Pipeline Specification (5 tasks)

| # | Task ID | Content | Active Form | Phase |
|---|---------|---------|-------------|-------|
| 13 | P2-01 | Map source steps to generated steps | Mapping step graph | 2 |
| 14 | P2-02 | Design models, gates, and prompts | Designing pipeline components | 2 |
| 15 | P2-03 | Implement pure-programmatic steps | Implementing programmatic steps | 2 |
| 16 | P2-04 | Run 8 self-validation checks | Running spec validation | 2 |
| 17 | P2-05 | Present spec for user approval | Awaiting spec approval | 2 |

### Phase 3: Code Generation (3 tasks)

| # | Task ID | Content | Active Form | Phase |
|---|---------|---------|-------------|-------|
| 18 | P3-01 | Generate 12 Python files in dependency order | Generating pipeline code | 3 |
| 19 | P3-02 | Run per-file AST and import validation | Validating generated code | 3 |
| 20 | P3-03 | Run cross-file validation (4 checks) | Running cross-file validation | 3 |

### Phase 4: Integration (3 tasks)

| # | Task ID | Content | Active Form | Phase |
|---|---------|---------|-------------|-------|
| 21 | P4-01 | Patch main.py and verify imports | Integrating CLI command | 4 |
| 22 | P4-02 | Run integration smoke test | Running smoke test | 4 |
| 23 | P4-03 | Generate structural test and write summary | Generating tests and summary | 4 |

**Total**: 23 subphase tasks ✅

---

## 2. Checkpoint Trigger Conditions

Checkpoints fire TodoWrite updates at these points:

| Trigger | When | TodoWrite Action |
|---------|------|-----------------|
| Phase completion | After all sub-tasks in a phase pass | Mark all phase tasks completed |
| User review gate | When analysis/spec presented to user | Mark current task "awaiting review" |
| Before write operation | Before emitting contracts or generating files | Mark task in_progress |
| On failure | When a blocking check fails or process errors | Mark task as blocked with failure reason |

### Checkpoint Payload Format

```python
TodoWrite(todos=[
    {
        "content": task.content,
        "activeForm": task.active_form,
        "status": new_status,  # "pending" | "in_progress" | "completed"
    }
    for task in phase_tasks
])
```

---

## 3. Phase 0 Wiring

TodoWrite updates during Phase 0 execution:

```
1. Initialize: Create tasks P0-01 through P0-05 (all "pending")
2. P0-01 → in_progress: "Resolving workflow path"
3. P0-01 → completed | P0-02 → in_progress: "Capturing API snapshot"
4. P0-02 → completed | P0-03 → in_progress: "Checking for collisions"
5. P0-03 → completed | P0-04 → in_progress: "Scanning for unsupported patterns"
6. P0-04 → completed | P0-05 → in_progress: "Emitting Phase 0 contract"
7. P0-05 → completed: Phase 0 complete

On failure at any step:
- Current task status stays "in_progress" (blocked)
- Remaining tasks stay "pending"
- Error details logged in execution log
```

---

## 4. Phase 1 Wiring

TodoWrite updates during Phase 1 execution:

```
1. Initialize: Create tasks P1-01 through P1-07 (all "pending")
2. P1-01 → in_progress → completed (component inventory built)
3. P1-02 → in_progress → completed (steps decomposed)
4. P1-03 → in_progress → completed (steps classified)
5. P1-04 → in_progress → completed (DAG built and validated)
6. P1-05 → in_progress → completed (gates assigned)
7. P1-06 → in_progress → completed (self-validation passed)
8. P1-07 → in_progress: "Awaiting user review"
   [USER REVIEW CHECKPOINT — pipeline pauses]
9. P1-07 → completed: User approved analysis

On blocking self-validation failure:
- P1-06 stays "in_progress" (blocked)
- P1-07 stays "pending"
- Phase 1 contract emitted with status: "failed"
```

---

## 5. Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| 23 subphase tasks defined with phase assignments covering all 5 phases | ✅ PASS (5+7+5+3+3=23) |
| Checkpoint triggers fire after phase completion, at user review gates, before write operations, and on failure | ✅ PASS |
| TodoWrite updates visible during Phase 0 and Phase 1 execution | ✅ PASS (wiring detailed above) |
| Task count verified: exactly 23 subphase tasks defined | ✅ PASS |
