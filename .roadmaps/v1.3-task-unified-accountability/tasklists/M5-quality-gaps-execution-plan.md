# M5 Quality Gaps - Granular Execution Plan

## Overview
This execution plan converts the 4 recommendations from `/sc:reflect` into granular tasks designed for `sc:task-unified` execution.

**Recommendations to Address:**
1. Fix pytest marker immediately (trivial, no task overhead)
2. Read 3 files to verify assumptions
3. Update task specifications based on actual code
4. Enforce proper task ordering with T5.8 last

---

## Phase 1: Immediate Fix (LIGHT Tier)

### Task 1.1: Register Pytest Accountability Marker
```yaml
command: /sc:task-unified "Register accountability pytest marker in pyproject.toml"
tier: LIGHT
estimated_tokens: 60
verification: syntax-check
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

### Task 2.1: Verify Protocol Runtime Checkability
```yaml
command: /sc:task-unified "Verify @runtime_checkable decorator usage in interfaces.py and document findings"
tier: STANDARD
estimated_tokens: 300
verification: direct-test
```

**Description**: Read `interfaces.py` and verify whether Protocol classes use `@runtime_checkable` decorator.

**Steps**:
1. Read `src/superclaude/accountability/interfaces.py`
2. Check each Protocol class for `@runtime_checkable` decorator
3. Document findings in memory
4. Update T5.6 specification if assumptions incorrect

**Acceptance Criteria**:
- [ ] All Protocol classes inventoried
- [ ] `@runtime_checkable` usage documented per class
- [ ] T5.6 test cases updated to match reality
- [ ] Findings recorded for task planning

**Decision Matrix**:
| Finding | Action |
|---------|--------|
| All protocols have `@runtime_checkable` | T5.6 tests valid as designed |
| Some protocols missing decorator | Add decorator OR modify tests to use structural checks |
| No protocols have decorator | Redesign T5.6 to use `typing.get_type_hints()` approach |

---

### Task 2.2: Verify Worklog Error Handling Behavior
```yaml
command: /sc:task-unified "Verify error handling behavior in worklog.py for edge cases"
tier: STANDARD
estimated_tokens: 300
verification: direct-test
```

**Description**: Read `worklog.py` and verify actual error handling behavior for edge cases.

**Steps**:
1. Read `src/superclaude/accountability/worklog.py`
2. Check behavior for: append without init, double init, finalize without init, double finalize
3. Document actual behavior (raises exception vs defensive return vs logging)
4. Update T5.7 test cases to match actual behavior

**Acceptance Criteria**:
- [ ] Error handling pattern identified (exceptions vs defensive)
- [ ] Each edge case behavior documented
- [ ] T5.7 test assertions updated to match reality
- [ ] Any missing error handling flagged for implementation

**Decision Matrix**:
| Behavior Found | T5.7 Update |
|----------------|-------------|
| Raises `ValueError` | Keep `pytest.raises(ValueError)` assertions |
| Raises `RuntimeError` | Change to `pytest.raises(RuntimeError)` |
| Returns `None`/logs | Change to `assert result is None` or check logs |
| No error handling | Add "implement error handling" subtask first |

---

### Task 2.3: Analyze _generate_summary Complexity
```yaml
command: /sc:task-unified "Analyze _generate_summary implementation and design targeted refactoring"
tier: STANDARD
estimated_tokens: 400
verification: direct-test
```

**Description**: Read actual `_generate_summary()` implementation and design evidence-based refactoring.

**Steps**:
1. Read `src/superclaude/accountability/worklog.py` method `_generate_summary`
2. Map actual complexity sources (conditionals, loops, branches)
3. Identify natural decomposition points based on actual logic
4. Design refactoring that preserves exact behavior
5. Update T5.8 with implementation-specific plan

**Acceptance Criteria**:
- [ ] Actual CC score verified (claimed CC=18)
- [ ] Branch-by-branch analysis documented
- [ ] Decomposition plan matches actual structure
- [ ] Refactoring preserves all existing test behavior

**Output**: Refactoring plan with:
- Current function structure diagram
- Proposed helper method signatures
- Line-by-line mapping old → new
- Risk assessment for each decomposition

---

### Task 2.4: Analyze validate_entry_details Complexity
```yaml
command: /sc:task-unified "Analyze validate_entry_details implementation and design targeted refactoring"
tier: STANDARD
estimated_tokens: 400
verification: direct-test
```

**Description**: Read actual `validate_entry_details()` implementation and design evidence-based refactoring.

**Steps**:
1. Read `src/superclaude/accountability/schema.py` function `validate_entry_details`
2. Identify whether it's a function or method
3. Map discriminated union handling logic
4. Design dispatcher pattern that fits actual implementation
5. Update T5.8 with implementation-specific plan

**Acceptance Criteria**:
- [ ] Actual CC score verified (claimed CC=16)
- [ ] Function signature and location confirmed
- [ ] Discriminated union handling pattern documented
- [ ] Dispatcher design matches actual detail types

---

## Phase 3: Task Specification Updates (STANDARD Tier)

### Task 3.1: Update T5.6 Based on Verification Findings
```yaml
command: /sc:task-unified "Update T5.6 specification in M5-quality-gap-additions.md based on verification findings"
tier: STANDARD
estimated_tokens: 300
verification: direct-test
depends_on: [2.1]
```

**Description**: Revise T5.6 test cases based on actual `@runtime_checkable` findings.

**Steps**:
1. Read findings from Task 2.1
2. Update `test_interfaces.py` specification in `M5-quality-gap-additions.md`
3. Adjust assertions to match actual protocol behavior
4. Update acceptance criteria and verification commands

**Acceptance Criteria**:
- [ ] T5.6 tests match actual interfaces.py implementation
- [ ] All protocol classes have appropriate tests
- [ ] Coverage target achievable (adjust if needed)

---

### Task 3.2: Update T5.7 Based on Verification Findings
```yaml
command: /sc:task-unified "Update T5.7 specification in M5-quality-gap-additions.md based on error handling findings"
tier: STANDARD
estimated_tokens: 300
verification: direct-test
depends_on: [2.2]
```

**Description**: Revise T5.7 test cases based on actual worklog error handling.

**Steps**:
1. Read findings from Task 2.2
2. Update edge case tests in `M5-quality-gap-additions.md`
3. Adjust assertions to match actual error handling behavior
4. Add any missing error handling implementation tasks

**Acceptance Criteria**:
- [ ] T5.7 tests match actual worklog.py behavior
- [ ] All edge cases have appropriate assertions
- [ ] Any implementation gaps documented as subtasks

---

### Task 3.3: Update T5.8 Based on Complexity Analysis
```yaml
command: /sc:task-unified "Update T5.8 specification with evidence-based refactoring plans"
tier: STANDARD
estimated_tokens: 400
verification: direct-test
depends_on: [2.3, 2.4]
```

**Description**: Replace speculative refactoring with evidence-based plans.

**Steps**:
1. Read analysis from Tasks 2.3 and 2.4
2. Replace proposed decomposition with actual-implementation-based plan
3. Add line-by-line transformation mappings
4. Include benchmark requirements (before/after performance)
5. Add rollback strategy

**Acceptance Criteria**:
- [ ] Refactoring plan based on actual code structure
- [ ] Helper method signatures match actual logic
- [ ] Performance benchmark step included
- [ ] Git checkpoint/rollback strategy documented

---

## Phase 4: Enforce Task Ordering (LIGHT Tier)

### Task 4.1: Update M5 Tasklist with Dependency Ordering
```yaml
command: /sc:task-unified "Add explicit dependency ordering to M5-testing-quality.md ensuring T5.8 executes last"
tier: LIGHT
estimated_tokens: 100
verification: syntax-check
depends_on: [3.1, 3.2, 3.3]
```

**Description**: Add `depends_on` metadata and execution order constraints to M5 tasklist.

**Steps**:
1. Add dependency metadata to each task in M5-testing-quality.md
2. Add execution order section showing: T5.6 → T5.7 → T5.1-T5.5 → T5.8
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

## Execution Summary

### Phase Execution Order
```
Phase 1: [1.1] ─────────────────────────────────────→ Immediate (LIGHT)
Phase 2: [2.1] ──┬── [2.2] ──┬── [2.3] ──┬── [2.4] → Verification (STANDARD)
Phase 3:        └── [3.1] ──┴── [3.2] ──┴── [3.3] → Specification (STANDARD)
Phase 4: [4.1] ─────────────────────────────────────→ Ordering (LIGHT)
```

### Token Budget Estimate
| Phase | Tasks | Est. Tokens | Tier |
|-------|-------|-------------|------|
| 1 | 1.1 | 60 | LIGHT |
| 2 | 2.1-2.4 | 1,400 | STANDARD |
| 3 | 3.1-3.3 | 1,000 | STANDARD |
| 4 | 4.1 | 100 | LIGHT |
| **Total** | **8 tasks** | **2,560** | Mixed |

### Success Metrics
- [ ] 0 pytest marker warnings
- [ ] All T5.6-T5.8 specifications verified against actual code
- [ ] Dependency ordering enforced in M5 tasklist
- [ ] Ready for M5 execution with high confidence

---

## sc:task-unified Command Sequence

```bash
# Phase 1: Immediate fix
/sc:task-unified "Register accountability pytest marker in pyproject.toml" --compliance light

# Phase 2: Verification (can run in parallel)
/sc:task-unified "Verify @runtime_checkable decorator usage in interfaces.py"
/sc:task-unified "Verify error handling behavior in worklog.py for edge cases"
/sc:task-unified "Analyze _generate_summary implementation and design targeted refactoring"
/sc:task-unified "Analyze validate_entry_details implementation and design targeted refactoring"

# Phase 3: Specification updates (sequential, depends on Phase 2)
/sc:task-unified "Update T5.6 specification based on verification findings"
/sc:task-unified "Update T5.7 specification based on error handling findings"
/sc:task-unified "Update T5.8 specification with evidence-based refactoring plans"

# Phase 4: Finalize ordering
/sc:task-unified "Add explicit dependency ordering to M5 tasklist" --compliance light
```
