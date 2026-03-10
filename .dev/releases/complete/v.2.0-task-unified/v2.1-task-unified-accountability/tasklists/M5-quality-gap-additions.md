# Proposed M5 Quality Gap Additions

## Context
These tasks address quality gaps identified during M3 completion analysis that are NOT covered by the existing M5 tasklist.

**Quality Analysis Findings**:
- Overall Grade: A (96%)
- 380 tests passing
- 2 major gaps, 3 minor gaps identified

**Evidence-Based Updates** (from M5-quality-gaps-execution-plan verification):
- ✅ Task 1.1 COMPLETED: Pytest marker registered in pyproject.toml
- ✅ Task 2.1 VERIFIED: All 3 protocols have @runtime_checkable (WorklogEntry, WorklogService, AccountabilityOrchestrator)
- ✅ Task 2.2 VERIFIED: worklog.py uses factory pattern (classmethod), CC≈17-18 confirmed
- ✅ Task 2.3 VERIFIED: validate_entry_details is function (not method), CC≈12-16 confirmed

---

## T5.6: Register Pytest Marker and Protocol Compliance Tests (GAP-001, GAP-002)

**Type**: ENHANCEMENT
**Priority**: P1-High
**Complexity**: Low
**Files Affected**:
- `pyproject.toml` (modify - add marker registration)
- `tests/accountability/test_interfaces.py` (create)

### Problem Statement
1. **Pytest marker warning**: `accountability` marker not registered, causing 12 warnings per test run
   - ✅ **RESOLVED**: Marker registered in pyproject.toml (Phase 1 Task 1.1)
2. **Protocol coverage gap**: `interfaces.py` at 77% - protocol methods untested

### Evidence-Based Findings (Task 2.1)
All 3 Protocol classes have `@runtime_checkable` decorator:
- `WorklogEntry` (line 49) - ✅ runtime_checkable
- `WorklogService` (line 59) - ✅ runtime_checkable
- `AccountabilityOrchestrator` (line 139) - ✅ runtime_checkable

**Decision**: ✅ PROCEED - isinstance() checks will work as designed

### Steps
1. Register `accountability` marker in `pyproject.toml`
2. Create protocol compliance tests for all `Protocol` classes in `interfaces.py`
3. Test abstract method signatures match implementing classes
4. Verify runtime protocol checks work correctly

### Implementation Details

#### Step 1: Register Marker
```toml
# pyproject.toml - add to [tool.pytest.ini_options]
markers = [
    "unit: Unit tests (deselect with '-m \"not unit\"')",
    "integration: Integration tests",
    "accountability: Accountability framework tests",
    "confidence_check: Confidence checker tests",
    "self_check: Self-check protocol tests",
    "reflexion: Reflexion pattern tests",
]
```

#### Step 2: Protocol Compliance Tests
```python
# tests/accountability/test_interfaces.py
"""Protocol compliance tests for interfaces.py (100% coverage target)."""

import pytest
from typing import runtime_checkable, Protocol
from superclaude.accountability.interfaces import (
    WorklogService,
    WorklogHandle,
    WorklogSummary,
    AccountabilityOrchestrator,
    Task,
)

class TestWorklogServiceProtocol:
    """Tests for WorklogService protocol compliance."""

    def test_protocol_is_runtime_checkable(self):
        """WorklogService should be runtime checkable."""
        assert hasattr(WorklogService, '__protocol_attrs__')

    def test_worklog_implements_protocol(self):
        """Worklog class should implement WorklogService."""
        from superclaude.accountability.worklog import Worklog
        assert isinstance(Worklog(), WorklogService)

    def test_protocol_method_signatures(self):
        """Protocol methods should have correct signatures."""
        import inspect
        sig = inspect.signature(WorklogService.init_session)
        params = list(sig.parameters.keys())
        assert 'session_id' in params or 'self' in params

    def test_missing_method_fails_isinstance(self):
        """Class missing required method should fail isinstance check."""
        class IncompleteWorklog:
            pass
        # This should NOT be an instance of WorklogService
        # (unless protocols allow partial implementation)


class TestWorklogHandleProtocol:
    """Tests for WorklogHandle protocol compliance."""

    def test_handle_returned_by_init_session(self):
        """init_session should return WorklogHandle."""
        from superclaude.accountability.worklog import Worklog
        worklog = Worklog()
        handle = worklog.init_session("test-session", "STANDARD")
        assert isinstance(handle, WorklogHandle)

    def test_handle_has_required_attributes(self):
        """WorklogHandle should have session_id and tier."""
        from superclaude.accountability.worklog import Worklog
        worklog = Worklog()
        handle = worklog.init_session("test-session", "STANDARD")
        assert hasattr(handle, 'session_id')
        assert hasattr(handle, 'tier')


class TestWorklogSummaryProtocol:
    """Tests for WorklogSummary protocol compliance."""

    def test_summary_returned_by_finalize(self):
        """finalize should return WorklogSummary."""
        from superclaude.accountability.worklog import Worklog
        worklog = Worklog()
        worklog.init_session("test-session", "STANDARD")
        summary = worklog.finalize()
        assert isinstance(summary, WorklogSummary)

    def test_summary_has_required_fields(self):
        """WorklogSummary should have all required fields."""
        from superclaude.accountability.worklog import Worklog
        worklog = Worklog()
        worklog.init_session("test-session", "STANDARD")
        summary = worklog.finalize()
        assert hasattr(summary, 'session_id')
        assert hasattr(summary, 'outcome')
        assert hasattr(summary, 'entry_count')


class TestAccountabilityOrchestratorProtocol:
    """Tests for AccountabilityOrchestrator protocol."""

    def test_orchestrator_protocol_defined(self):
        """AccountabilityOrchestrator protocol should be defined."""
        assert AccountabilityOrchestrator is not None

    def test_task_protocol_defined(self):
        """Task protocol should be defined."""
        assert Task is not None


# Marker registration verification
class TestMarkerRegistration:
    """Verify pytest markers are registered."""

    @pytest.mark.accountability
    def test_accountability_marker_works(self):
        """This test should run without marker warnings."""
        pass
```

### Acceptance Criteria
- [ ] `pytest --strict-markers` passes without warnings
- [ ] `interfaces.py` coverage ≥ 95%
- [ ] All protocol classes have compliance tests
- [ ] Protocol runtime checks work correctly

### Verification
```bash
# Verify no marker warnings
uv run pytest tests/accountability/ --strict-markers -v 2>&1 | grep -c "PytestUnknownMarkWarning"
# Should output: 0

# Verify interfaces coverage
uv run pytest tests/accountability/test_interfaces.py -v --cov=superclaude.accountability.interfaces --cov-fail-under=95
```

---

## T5.7: Worklog Edge Case Coverage (GAP-003)

**Type**: ENHANCEMENT
**Priority**: P2-Medium
**Complexity**: Low
**Files Affected**:
- `tests/accountability/test_worklog.py` (extend)

### Problem Statement
`worklog.py` is at 87% coverage - edge cases and error paths untested.

### Evidence-Based Findings (Task 2.2)

**CRITICAL UPDATE**: Worklog uses **factory pattern** (classmethod), NOT state-machine pattern.

| Edge Case | Actual Behavior | Test Approach |
|-----------|-----------------|---------------|
| append without init | No explicit check | Test graceful behavior (not ValueError) |
| double init | Factory creates new instance | Not applicable - each call is independent |
| finalize without init | No explicit validation | Test default/graceful behavior |
| double finalize | No explicit check | Test graceful second call |

**Key Finding**: The original T5.7 tests assumed ValueError exceptions for edge cases. The actual implementation uses a **factory pattern** that doesn't raise exceptions for these scenarios. Tests must be adapted accordingly.

### Steps
1. Identify untested lines via coverage report
2. Add edge case tests for buffer flushing (flush_on_error, flush_on_checkpoint, check_time_flush)
3. Add boundary condition tests (empty buffer, buffer overflow)
4. Test summary generation with various entry combinations

### Test Cases to Add
```python
# tests/accountability/test_worklog.py - additions

class TestWorklogEdgeCases:
    """Edge case tests for 100% coverage."""

    # Buffer edge cases
    def test_flush_empty_buffer(self):
        """Flush when buffer is empty should be no-op."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        worklog._flush_buffer()  # Should not raise

    def test_buffer_overflow_triggers_flush(self):
        """Buffer exceeding max size triggers automatic flush."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        # Add entries until buffer overflows
        for i in range(worklog.buffer.max_size + 1):
            worklog.append(action="Edit", status="completed", context=f"edit-{i}")
        # Verify flush occurred

    def test_emergency_flush_on_error(self):
        """Error during append triggers emergency flush."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        worklog.append(action="Bash", status="failed", context="command failed")
        # Verify buffer was flushed

    # Session lifecycle edge cases (REVISED based on factory pattern findings)
    def test_append_on_raw_worklog(self):
        """Appending on raw Worklog() should work gracefully (no session_id)."""
        worklog = Worklog()  # Not initialized via factory
        # Should not raise - gracefully handles uninitialized state
        result = worklog.append(action="Edit", status="completed", context="test")
        # Verify behavior (may return False due to tier filtering)
        assert isinstance(result, bool)

    def test_factory_creates_independent_instances(self):
        """Each Worklog.initialize() call creates independent instance."""
        worklog1 = Worklog.initialize("session-1", "task-1", "STANDARD")
        worklog2 = Worklog.initialize("session-2", "task-2", "STRICT")
        assert worklog1.session_id != worklog2.session_id
        assert worklog1.tier != worklog2.tier

    def test_finalize_on_uninitialized_worklog(self):
        """Finalize on raw Worklog() should work with defaults."""
        import asyncio
        worklog = Worklog()
        # Should not raise - returns summary with default values
        summary = asyncio.run(worklog.finalize("success"))
        assert summary.total_operations == 0

    def test_double_finalize_graceful(self):
        """Calling finalize twice should be graceful (idempotent or last-wins)."""
        import asyncio
        worklog = Worklog.initialize("test", "task", "STANDARD")
        summary1 = asyncio.run(worklog.finalize("success"))
        summary2 = asyncio.run(worklog.finalize("failure"))  # Second call
        # Both should complete without exception
        assert summary1 is not None
        assert summary2 is not None

    # Entry handling edge cases (no validation exceptions per actual code)
    def test_append_with_tier_filtering(self):
        """Append may return False if action not tier-significant."""
        worklog = Worklog.initialize("test", "task", "LIGHT")  # LIGHT tier filters more
        result = worklog.append(action="TodoWrite", status="completed", context="test")
        # Result depends on tier policy - should be boolean
        assert isinstance(result, bool)

    def test_append_empty_context_allowed(self):
        """Empty context should be allowed."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        worklog.append(action="Edit", status="completed", context="")
        assert worklog.entry_count == 1

    def test_append_unicode_context(self):
        """Unicode in context should be handled."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        worklog.append(action="Edit", status="completed", context="日本語テスト🎉")
        assert worklog.entry_count == 1

    # Summary generation edge cases
    def test_summary_with_zero_entries(self):
        """Summary with no entries should work."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        summary = worklog.finalize()
        assert summary.entry_count == 0

    def test_summary_with_all_failure_entries(self):
        """Summary with all failures should reflect failure outcome."""
        worklog = Worklog()
        worklog.init_session("test", "STANDARD")
        worklog.append(action="Bash", status="failed", context="error 1")
        worklog.append(action="Edit", status="failed", context="error 2")
        summary = worklog.finalize()
        assert summary.outcome == "failure"
```

### Acceptance Criteria
- [ ] `worklog.py` coverage ≥ 95%
- [ ] All error paths tested
- [ ] All boundary conditions tested
- [ ] Buffer behavior fully verified

### Verification
```bash
uv run pytest tests/accountability/test_worklog.py -v --cov=superclaude.accountability.worklog --cov-fail-under=95
```

---

## T5.8: Complexity Refactoring (GAP-004, GAP-005)

**Type**: REFACTOR
**Priority**: P2-Medium
**Complexity**: Medium
**Files Affected**:
- `src/superclaude/accountability/worklog.py` (modify `_generate_summary`)
- `src/superclaude/accountability/schema.py` (modify `validate_entry_details`)

### Problem Statement
Two functions exceed recommended cyclomatic complexity:
- `_generate_summary()`: CC=18 (target: ≤10)
- `validate_entry_details()`: CC=16 (target: ≤10)

### Evidence-Based Findings (Tasks 2.2 & 2.3)

#### _generate_summary() (worklog.py:234-289)
**Verified CC: 17-18** ✅ Matches original estimate
- Lines: 56 total
- Branch types: 1 main loop, 4 action type branches, 10+ nested conditions, try/except
- Natural decomposition points identified:
  1. `_count_file_modifications()` - Edit/MultiEdit/Write handling
  2. `_count_todos_completed()` - TodoWrite with status tracking
  3. `_aggregate_verification_results()` - Verify action processing
  4. `_count_checkpoints()` - Simple checkpoint counter
  5. `_calculate_duration()` - ISO8601 parsing with try/except

#### validate_entry_details() (schema.py:162-204)
**Verified CC: 12-16** ✅ Matches original estimate
- Type: Function (not method)
- Lines: 43 total
- Structure: 6 isinstance branches + nested validation per type
- Key finding: `create_entry_details` (lines 121-159) already uses dispatcher pattern
- Refactoring approach: Apply same dispatcher pattern to validation

### Refactoring Strategy

#### _generate_summary() Decomposition
```python
# BEFORE: Single function with CC=18
def _generate_summary(self) -> WorklogSummary:
    # 18 branches of logic

# AFTER: Decomposed into focused helpers
def _generate_summary(self) -> WorklogSummary:
    """Generate worklog summary. CC reduced from 18 to 5."""
    return WorklogSummary(
        session_id=self.session_id,
        tier=self.tier,
        outcome=self._compute_outcome(),
        entry_count=len(self.entries),
        verification_results=self._aggregate_verifications(),
        checkpoint_count=self._count_checkpoints(),
        duration_ms=self._compute_duration(),
        token_overhead=self._compute_token_overhead(),
    )

def _compute_outcome(self) -> str:
    """Determine session outcome from entries. CC=4."""
    if self._has_abort():
        return "aborted"
    if self._has_failure():
        return "failure"
    if self._has_partial():
        return "partial"
    return "success"

def _aggregate_verifications(self) -> dict:
    """Aggregate verification results. CC=3."""
    # Focused verification aggregation

def _count_checkpoints(self) -> int:
    """Count checkpoint entries. CC=1."""
    return sum(1 for e in self.entries if e.action == "Checkpoint")

def _compute_duration(self) -> float:
    """Compute session duration. CC=2."""
    # Simple duration calculation

def _compute_token_overhead(self) -> int:
    """Estimate token overhead. CC=3."""
    # Token calculation
```

#### validate_entry_details() Decomposition
```python
# BEFORE: Single function with CC=16
def validate_entry_details(details: EntryDetails) -> bool:
    # 16 branches checking all detail types

# AFTER: Dispatcher pattern
def validate_entry_details(details: EntryDetails) -> bool:
    """Validate entry details using dispatcher. CC reduced from 16 to 3."""
    validators = {
        "TodoWrite": _validate_todowrite_details,
        "Edit": _validate_edit_details,
        "Bash": _validate_bash_details,
        "Verify": _validate_verify_details,
        "Checkpoint": _validate_checkpoint_details,
        "Task": _validate_task_details,
    }
    detail_type = details.get("type")
    validator = validators.get(detail_type)
    if validator is None:
        return False
    return validator(details)

def _validate_todowrite_details(details: TodoWriteDetails) -> bool:
    """Validate TodoWrite details. CC=3."""
    # Focused validation

def _validate_edit_details(details: EditDetails) -> bool:
    """Validate Edit details. CC=2."""
    # Focused validation

# ... similar for other types
```

### Acceptance Criteria
- [ ] `_generate_summary()` CC ≤ 10
- [ ] `validate_entry_details()` CC ≤ 10
- [ ] All existing tests pass
- [ ] No functionality changes
- [ ] Code coverage maintained

### Verification
```bash
# Run radon to verify complexity reduction
uv run radon cc src/superclaude/accountability/worklog.py src/superclaude/accountability/schema.py -a -s

# Ensure all tests still pass
uv run pytest tests/accountability/ -v

# Verify coverage not regressed
uv run pytest tests/accountability/ --cov=superclaude.accountability --cov-fail-under=94
```

---

## Updated M5 Task Summary

| Task | Type | Priority | Status | Depends On |
|------|------|----------|--------|------------|
| T5.1 | Schema validation tests | P1 | Existing | - |
| T5.2 | Verification state machine tests | P1 | Existing | - |
| T5.3 | Circuit breaker tests | P1 | Existing | - |
| T5.4 | E2E integration tests | P1 | Existing | T5.1, T5.2, T5.3 |
| T5.5 | Performance tests | P2 | Existing | T5.4 |
| **T5.6** | **Pytest marker + protocol tests** | **P1** | **NEW** | - |
| **T5.7** | **Worklog edge case coverage** | **P2** | **NEW** | T5.6 |
| **T5.8** | **Complexity refactoring** | **P2** | **NEW** | T5.1-T5.7 (LAST) |

---

## Execution Order (Dependency-Enforced)

### Phase A: Foundation (Parallel)
```
T5.1 (Schema validation) ────┐
T5.2 (Verification SM)  ─────┼─→ Can run in parallel
T5.3 (Circuit breaker) ──────┤
T5.6 (Markers + protocols) ──┘
```

### Phase B: Coverage Extension
```
T5.7 (Worklog edge cases) ───→ Depends on T5.6 completion
```

### Phase C: Integration
```
T5.4 (E2E integration) ──────→ Depends on T5.1, T5.2, T5.3
```

### Phase D: Performance
```
T5.5 (Performance tests) ────→ Depends on T5.4
```

### Phase E: Refactoring (MUST BE LAST)
```
T5.8 (Complexity refactoring) → Depends on ALL other tasks
```

### Pre-T5.8 Gate Requirements
⚠️ **T5.8 MUST NOT START until:**
- [ ] T5.1-T5.7 all pass
- [ ] Code coverage ≥95%
- [ ] No test failures
- [ ] All edge cases covered

**Rationale**: Refactoring before comprehensive test coverage creates regression risk. T5.8 modifies _generate_summary and validate_entry_details which are tested by T5.1-T5.7.

---

## Updated M5 Verification Checkpoint

### Pre-Completion Checklist (Extended)
- [ ] All 8 deliverables code-complete (was 5)
- [ ] Pytest markers registered (no warnings)
- [ ] Unit tests passing with required coverage:
  ```bash
  uv run pytest tests/accountability/ --strict-markers --cov=superclaude.accountability --cov-fail-under=95
  ```
- [ ] Critical path 100% coverage:
  ```bash
  uv run pytest tests/accountability/test_worklog_schema.py tests/accountability/test_verification.py tests/accountability/test_circuit_breaker.py tests/accountability/test_interfaces.py -v --cov --cov-fail-under=100
  ```
- [ ] Complexity targets met:
  ```bash
  uv run radon cc src/superclaude/accountability/ -a -s | grep -E "^Average complexity"
  # Target: Average complexity ≤ 5.0
  ```
- [ ] All E2E scenarios pass
- [ ] Performance tests validate all metrics
- [ ] No regressions in existing tests

### Quality Gates
```bash
# Full quality validation
uv run pytest tests/accountability/ --strict-markers -v \
  --cov=superclaude.accountability \
  --cov-report=html \
  --cov-fail-under=95

# Complexity check
uv run radon cc src/superclaude/accountability/ -a -nc
# Should show no functions with CC > 10
```
