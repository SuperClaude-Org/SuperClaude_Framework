# M5 Quality Gaps - Execution Plan (REVISED)

## Overview
This execution plan converts the 4 recommendations from `/sc:reflect` into granular tasks designed for `sc:task-unified` execution.

**Recommendations to Address:**
1. Fix pytest marker immediately (trivial, no task overhead)
2. Read 3 files to verify assumptions
3. Update task specifications based on actual code
4. Enforce proper task ordering with T5.8 last

---

## ⚠️ Revision Notes (Post-Adversarial Debate)

**Weaknesses Addressed:**
| Issue | Original | Revised |
|-------|----------|---------|
| Task count | 8 tasks | **5 tasks** (consolidated) |
| Verification methods | "direct-test" everywhere | Task-appropriate methods |
| Parallelization | False claim (4 parallel) | Honest (2 parallel streams) |
| Token budget | 2,560 (optimistic) | **3,300** (with 30% buffer) |
| Exit criteria | Missing | Added to each verification task |
| Persistence | Implicit | Explicit write_memory calls |
| Rollback | Missing | Git checkpoint added |

**Consolidation Changes:**
- Tasks 2.2 + 2.3 merged → Task 2.2 (both analyze worklog.py)
- Tasks 3.1 + 3.2 + 3.3 merged → Task 3.1 (single specification update)
- Result: 8 tasks → 5 tasks (37.5% reduction)

---

## Phase 0: Pre-Execution Setup

### Checkpoint: Create Rollback Point
```bash
# Before any changes, create restore point
git stash push -m "M5-quality-gaps-pre-execution-$(date +%Y%m%d)"
# OR if working tree clean:
git tag m5-quality-gaps-checkpoint-$(date +%Y%m%d)
```

**Rollback Command** (if needed):
```bash
git stash pop  # OR git checkout m5-quality-gaps-checkpoint-YYYYMMDD
```

---

## Phase 1: Immediate Fix (LIGHT Tier)

### Task 1.1: Register Pytest Accountability Marker
```yaml
command: /sc:task-unified "Register accountability pytest marker in pyproject.toml"
tier: LIGHT
estimated_tokens: 60
verification: syntax-check
rollback: "git checkout pyproject.toml"
```

**Description**: Add `accountability` marker to pytest configuration to eliminate 12 warnings per test run.

**Acceptance Criteria**:
- [ ] Marker registered in `pyproject.toml` under `[tool.pytest.ini_options]`
- [ ] `uv run pytest --strict-markers tests/accountability/ -v` passes without warnings
- [ ] Existing tests unaffected

**Implementation**:
```toml
# pyproject.toml - [tool.pytest.ini_options] section
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "accountability: Accountability framework tests",
    "confidence_check: Confidence checker tests",
    "self_check: Self-check protocol tests",
    "reflexion: Reflexion pattern tests",
]
```

---

## Phase 2: Verification & Assumption Validation (STANDARD Tier)

### Task 2.1: Verify Protocol Runtime Checkability (interfaces.py)
```yaml
command: /sc:task-unified "Verify @runtime_checkable decorator usage in interfaces.py and document findings"
tier: STANDARD
estimated_tokens: 400
verification: output-validation
persistence: write_memory("m5_interfaces_findings", findings)
parallelizable_with: [2.3]
```

**Description**: Read `interfaces.py` and verify whether Protocol classes use `@runtime_checkable` decorator.

**Steps**:
1. Read `src/superclaude/accountability/interfaces.py`
2. Check each Protocol class for `@runtime_checkable` decorator
3. Document findings in Serena memory
4. Determine T5.6 test strategy based on findings

**Exit Criteria** (Decision Points):
| Finding | Decision | Action |
|---------|----------|--------|
| All protocols have `@runtime_checkable` | ✅ PROCEED | T5.6 tests valid as designed |
| Some protocols missing decorator | 🔄 ADAPT | Either add decorator OR modify tests |
| No protocols have decorator | 🔄 PIVOT | Redesign T5.6 to use structural checks |
| Protocols use different pattern | ❌ ABORT T5.6 | Document incompatibility, skip T5.6 |

**Memory Persistence**:
```python
# After analysis, persist findings
mcp__serena__write_memory(
    memory_file_name="m5_interfaces_findings.md",
    content="""
    # interfaces.py Analysis
    ## Protocol Classes Found: [list]
    ## @runtime_checkable Status: [yes/no per class]
    ## Recommended T5.6 Approach: [approach]
    ## Evidence: [code snippets]
    """
)
```

**Acceptance Criteria**:
- [ ] All Protocol classes inventoried
- [ ] `@runtime_checkable` usage documented per class
- [ ] Decision made and documented (proceed/adapt/pivot/abort)
- [ ] Findings persisted in Serena memory

---

### Task 2.2: Verify Worklog Implementation Details (CONSOLIDATED)
```yaml
command: /sc:task-unified "Analyze worklog.py: verify error handling AND analyze _generate_summary complexity"
tier: STANDARD
estimated_tokens: 600
verification: output-validation
persistence: write_memory("m5_worklog_findings", findings)
parallelizable_with: []
note: "CONSOLIDATED from original Tasks 2.2 + 2.3 - both analyze same file"
```

**Description**: Comprehensive analysis of `worklog.py` covering both error handling behavior AND `_generate_summary` complexity.

**Steps**:
1. Read `src/superclaude/accountability/worklog.py`
2. **Part A**: Check error handling for edge cases (append without init, double init, etc.)
3. **Part B**: Analyze `_generate_summary()` - map complexity sources, identify decomposition points
4. Document ALL findings in single Serena memory entry

**Exit Criteria - Part A (Error Handling)**:
| Behavior Found | Decision | T5.7 Update |
|----------------|----------|-------------|
| Raises `ValueError` | ✅ PROCEED | Keep `pytest.raises(ValueError)` |
| Raises `RuntimeError` | 🔄 ADAPT | Change exception type |
| Returns `None`/logs | 🔄 ADAPT | Change to `assert result is None` |
| No error handling | 📝 ADD TASK | First implement error handling |

**Exit Criteria - Part B (Complexity)**:
| Finding | Decision | T5.8 Update |
|---------|----------|-------------|
| CC=18 confirmed, clear decomposition | ✅ PROCEED | Apply proposed refactoring |
| CC lower than reported | 🔄 ADAPT | Reduce refactoring scope |
| CC higher, tightly coupled | 📝 REASSESS | May need larger refactoring effort |
| Function structure different than assumed | 🔄 REDESIGN | New decomposition plan needed |

**Memory Persistence**:
```python
mcp__serena__write_memory(
    memory_file_name="m5_worklog_findings.md",
    content="""
    # worklog.py Analysis

    ## Part A: Error Handling
    - append_without_init: [raises/returns/none]
    - double_init: [raises/returns/none]
    - finalize_without_init: [raises/returns/none]
    - double_finalize: [raises/returns/none]
    - Recommended T5.7 approach: [approach]

    ## Part B: _generate_summary Complexity
    - Measured CC: [number]
    - Branch breakdown: [list]
    - Natural decomposition points: [list]
    - Recommended helper methods: [list]
    - T5.8 refactoring plan: [plan]
    """
)
```

**Acceptance Criteria**:
- [ ] Error handling pattern identified and documented
- [ ] Each edge case behavior documented
- [ ] _generate_summary CC measured and branch structure mapped
- [ ] Refactoring plan based on actual implementation
- [ ] All findings persisted in single Serena memory entry

---

### Task 2.3: Analyze validate_entry_details Complexity (schema.py)
```yaml
command: /sc:task-unified "Analyze validate_entry_details in schema.py and design evidence-based refactoring"
tier: STANDARD
estimated_tokens: 400
verification: output-validation
persistence: write_memory("m5_schema_findings", findings)
parallelizable_with: [2.1]
```

**Description**: Read actual `validate_entry_details()` implementation and design evidence-based refactoring.

**Steps**:
1. Read `src/superclaude/accountability/schema.py`
2. Locate `validate_entry_details` (function or method?)
3. Map discriminated union handling logic
4. Design dispatcher pattern that fits actual implementation
5. Document findings and update T5.8 plan

**Exit Criteria**:
| Finding | Decision | Action |
|---------|----------|--------|
| CC=16 confirmed, dispatcher fits | ✅ PROCEED | Apply proposed dispatcher pattern |
| Already uses dispatcher | ✅ SKIP | No refactoring needed |
| CC lower than reported | 🔄 ADAPT | Reduce refactoring scope |
| Structure incompatible with dispatcher | 🔄 REDESIGN | Alternative refactoring approach |

**Memory Persistence**:
```python
mcp__serena__write_memory(
    memory_file_name="m5_schema_findings.md",
    content="""
    # schema.py Analysis

    ## validate_entry_details Location
    - Type: [function/method]
    - Line numbers: [start-end]

    ## Complexity Analysis
    - Measured CC: [number]
    - Discriminated unions handled: [list]
    - Branch structure: [diagram]

    ## Refactoring Plan
    - Approach: [dispatcher/other]
    - Proposed helper functions: [list]
    - Expected CC after refactoring: [number]
    """
)
```

**Acceptance Criteria**:
- [ ] Function/method location confirmed
- [ ] Actual CC score measured
- [ ] Discriminated union handling documented
- [ ] Refactoring plan matches actual implementation
- [ ] Findings persisted in Serena memory

---

## Phase 3: Specification Updates (STANDARD Tier)

### Task 3.1: Update All M5 Task Specifications (CONSOLIDATED)
```yaml
command: /sc:task-unified "Update M5-quality-gap-additions.md with all verification findings from Phase 2"
tier: STANDARD
estimated_tokens: 500
verification: diff-review
depends_on: [2.1, 2.2, 2.3]
note: "CONSOLIDATED from original Tasks 3.1 + 3.2 + 3.3"
```

**Description**: Single task to update ALL specifications based on ALL Phase 2 findings.

**Steps**:
1. Read all Phase 2 memory entries:
   - `m5_interfaces_findings.md`
   - `m5_worklog_findings.md`
   - `m5_schema_findings.md`
2. Update T5.6 specification based on interfaces.py findings
3. Update T5.7 specification based on worklog.py error handling
4. Update T5.8 specification based on complexity analysis
5. Generate diff for review

**Acceptance Criteria**:
- [ ] T5.6 tests match actual interfaces.py implementation
- [ ] T5.7 tests match actual worklog.py error handling
- [ ] T5.8 refactoring plan based on actual code structure
- [ ] All changes reviewed via diff
- [ ] M5-quality-gap-additions.md updated and saved

**Verification**:
```bash
# Show changes for review
git diff --stat .roadmaps/v1.3-task-unified-accountability/tasklists/M5-quality-gap-additions.md
```

---

## Phase 4: Enforce Task Ordering (LIGHT Tier)

### Task 4.1: Add Dependency Ordering to M5 Tasklist
```yaml
command: /sc:task-unified "Add explicit dependency ordering to M5-testing-quality.md ensuring T5.8 executes last"
tier: LIGHT
estimated_tokens: 100
verification: syntax-check
depends_on: [3.1]
```

**Description**: Add `depends_on` metadata and execution order constraints to M5 tasklist.

**Steps**:
1. Add dependency metadata to each task in M5-testing-quality.md
2. Add execution order section: T5.6 → T5.7 → T5.1-T5.5 → T5.8
3. Add pre-T5.8 gate requiring all other M5 tests to pass

**Acceptance Criteria**:
- [ ] Each task has explicit `depends_on` field
- [ ] T5.8 depends on all other M5 tasks
- [ ] Execution order section added
- [ ] Pre-refactoring gate documented

**Dependency Chain**:
```
T5.6 (markers + protocols)
  ↓
T5.7 (worklog edge cases)
  ↓
T5.1 (schema validation) ─┐
T5.2 (verification)       ├─→ T5.8 (refactoring - LAST)
T5.3 (circuit breaker)    │
T5.4 (E2E tests)         ─┘
T5.5 (performance) ───────┘
```

---

## Execution Summary (REVISED)

### Phase Execution Order
```
Phase 0: [Checkpoint] ──────────────────────────────→ Setup
Phase 1: [1.1] ─────────────────────────────────────→ Immediate (LIGHT)
Phase 2: [2.1] ──────┬── [2.3] ─────────────────────→ Parallel Stream A (interfaces + schema)
         [2.2] ──────┴──────────────────────────────→ Sequential Stream B (worklog - comprehensive)
Phase 3: [3.1] ─────────────────────────────────────→ Unified Update (STANDARD)
Phase 4: [4.1] ─────────────────────────────────────→ Ordering (LIGHT)
```

### Token Budget Estimate (REVISED)
| Phase | Tasks | Est. Tokens | Contingency (30%) | Total |
|-------|-------|-------------|-------------------|-------|
| 1 | 1.1 | 60 | 18 | 78 |
| 2 | 2.1, 2.2, 2.3 | 1,400 | 420 | 1,820 |
| 3 | 3.1 | 500 | 150 | 650 |
| 4 | 4.1 | 100 | 30 | 130 |
| **Total** | **5 tasks** | **2,060** | **618** | **2,678** |

*Note: Original estimate was 2,560 for 8 tasks. Consolidated to 5 tasks with contingency = 2,678 tokens.*

### Parallelization Reality (HONEST)
```
TRUE PARALLEL:  [2.1 interfaces.py] || [2.3 schema.py]
SEQUENTIAL:     [2.2 worklog.py] (comprehensive analysis)
DEPENDENT:      [3.1] waits for all Phase 2
                [4.1] waits for Phase 3
```

**Time Savings**: ~30% reduction from true parallelization of 2.1 + 2.3

### Success Metrics
- [x] 0 pytest marker warnings ✅ (Task 1.1 completed)
- [x] All Serena memory entries created (3 findings files) ✅
  - m5_interfaces_findings.md
  - m5_worklog_findings.md
  - m5_schema_findings.md
- [x] M5-quality-gap-additions.md updated with evidence-based specifications ✅
- [x] Dependency ordering enforced in M5 tasklist ✅ (Task 4.1 completed)
- [x] Ready for M5 execution with ≥90% confidence ✅

### Execution Summary
**All 5 tasks completed successfully!**
- Phase 0: Git checkpoint created (stash@{0})
- Phase 1 (Task 1.1): Pytest marker registered ✅
- Phase 2 (Tasks 2.1, 2.2, 2.3): All verification tasks completed ✅
- Phase 3 (Task 3.1): M5 specifications updated with evidence ✅
- Phase 4 (Task 4.1): Dependency ordering added ✅

**Final Verification**: 380 tests passing with --strict-markers

---

## sc:task-unified Command Sequence (REVISED)

```bash
# Phase 0: Create checkpoint
git tag m5-quality-gaps-checkpoint-$(date +%Y%m%d)

# Phase 1: Immediate fix
/sc:task-unified "Register accountability pytest marker in pyproject.toml" --compliance light

# Phase 2: Verification (2 parallel streams)
# Stream A (can run in parallel):
/sc:task-unified "Verify @runtime_checkable decorator usage in interfaces.py"
/sc:task-unified "Analyze validate_entry_details in schema.py and design evidence-based refactoring"

# Stream B (runs independently):
/sc:task-unified "Analyze worklog.py: verify error handling AND analyze _generate_summary complexity"

# Phase 3: Unified specification update (waits for all Phase 2)
/sc:task-unified "Update M5-quality-gap-additions.md with all verification findings from Phase 2"

# Phase 4: Finalize ordering
/sc:task-unified "Add explicit dependency ordering to M5 tasklist" --compliance light
```

---

## Adversarial Debate Outcomes Applied

| Critique | Resolution |
|----------|------------|
| 8 tasks is over-engineering | ✅ Consolidated to 5 tasks |
| False parallelization claims | ✅ Honest: 2 streams (interfaces+schema \|\| worklog) |
| "direct-test" for read-only tasks | ✅ Changed to "output-validation" |
| Missing exit criteria | ✅ Decision matrices added to each verification task |
| No persistence | ✅ Explicit write_memory calls specified |
| No rollback | ✅ Phase 0 checkpoint added |
| Token budget optimistic | ✅ 30% contingency buffer added |
