# Tasklist: M2 - Core Worklog System

## Metadata
- **Milestone**: M2
- **Dependencies**: M1 (Foundation Infrastructure)
- **Estimated Complexity**: Medium
- **Primary Persona**: Backend
- **Files to Create/Modify**: 4 source files, 4 test files

---

## Tasks

### T2.1: Component Interfaces (REF-001)
**Type**: REFACTOR
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/interfaces.py` (create)
- `tests/accountability/test_interfaces.py` (create)

#### Steps
1. Create `interfaces.py` with Protocol/ABC definitions
2. Define `WorklogService` interface from SPEC-REVISED.md Section 3.4
3. Define `AccountabilityOrchestrator` interface
4. Add type hints matching TypeScript specification
5. Write tests verifying interface contracts

#### Implementation Details
```python
# interfaces.py
from typing import Protocol, Any
from abc import ABC, abstractmethod

class WorklogService(Protocol):
    def initialize(self, session_id: str, task: str, tier: str) -> "WorklogHandle": ...
    def append(self, entry: "WorklogEntry") -> None: ...
    async def flush(self) -> None: ...
    async def finalize(self, outcome: str) -> "WorklogSummary": ...
    def on_error(self, error: Exception) -> None: ...

class AccountabilityOrchestrator(Protocol):
    def on_task_start(self, task: "Task") -> None: ...
    def on_operation(self, operation: str, result: Any) -> None: ...
    def on_phase_complete(self, phase: str) -> None: ...
    def on_task_complete(self, outcome: str) -> None: ...
    def on_error(self, error: Exception) -> None: ...
```

#### Acceptance Criteria
- [ ] GIVEN WorklogService interface WHEN implemented THEN all methods match TypeScript specification
- [ ] GIVEN AccountabilityOrchestrator WHEN implemented THEN callback pattern works
- [ ] GIVEN interface tests WHEN run THEN contract verification passes

#### Verification
```bash
uv run pytest tests/accountability/test_interfaces.py -v
```

---

### T2.2: Worklog Initialization (REQ-001)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/worklog.py` (create)
- `tests/accountability/test_worklog.py` (create)

#### Steps
1. Create `worklog.py` with `Worklog` class implementing WorklogService
2. Implement `initialize()` method creating worklog structure
3. Add session_id, tier, task_description, started_at fields
4. Ensure initialization completes within 500ms
5. Validate token cost ≤75 tokens
6. Write unit tests for initialization scenarios

#### Implementation Details
```python
# worklog.py
@dataclass
class Worklog:
    version: str = "1.0"
    session_id: str = ""
    task_description: str = ""
    tier: str = ""  # STRICT|STANDARD|LIGHT|EXEMPT
    started_at: str = ""  # ISO8601
    completed_at: str | None = None
    outcome: str = "in_progress"
    entries: list[WorklogEntry] = field(default_factory=list)
    summary: WorklogSummary | None = None

    @classmethod
    def initialize(cls, session_id: str, task: str, tier: str) -> "Worklog":
        """Create worklog within 500ms, ≤75 tokens"""
        ...
```

#### Acceptance Criteria
- [ ] GIVEN task initiated WHEN tier classified THEN worklog created at `_worklog/{session_id}`
- [ ] GIVEN worklog initialization WHEN timed THEN completes within 500ms
- [ ] GIVEN worklog initialization WHEN tokens counted THEN cost ≤75 tokens
- [ ] GIVEN different tiers WHEN worklog created THEN tier field matches

#### Verification
```bash
uv run pytest tests/accountability/test_worklog.py::TestWorklogInitialization -v
```

---

### T2.3: Entry Details Discriminated Unions (REQ-012)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/schema.py` (create)
- `tests/accountability/test_schema.py` (create)

#### Steps
1. Create `schema.py` with entry detail dataclasses
2. Implement discriminated union pattern for action types
3. Define TodoWriteDetails, EditDetails, BashDetails, VerifyDetails, CheckpointDetails, TaskDetails
4. Add validation for required fields per action type
5. Write comprehensive unit tests

#### Implementation Details
```python
# schema.py
from dataclasses import dataclass
from typing import Union, Literal

@dataclass
class TodoWriteDetails:
    action: Literal["TodoWrite"] = "TodoWrite"
    todos_affected: int = 0
    status_changes: list[dict] = field(default_factory=list)

@dataclass
class EditDetails:
    action: Literal["Edit"] = "Edit"
    files: list[str] = field(default_factory=list)
    change_summary: str = ""

@dataclass
class BashDetails:
    action: Literal["Bash"] = "Bash"
    command_type: str = ""  # "test", "build", "script"
    exit_code: int = 0

@dataclass
class VerifyDetails:
    action: Literal["Verify"] = "Verify"
    verification_result: str = ""  # pass|fail|timeout|user_accepted|bypassed
    expected_state: dict = field(default_factory=dict)
    actual_state: dict = field(default_factory=dict)
    mismatch_details: str | None = None

@dataclass
class CheckpointDetails:
    action: Literal["Checkpoint"] = "Checkpoint"
    phase: str = ""
    operations_count: int = 0
    deviations: list[str] = field(default_factory=list)

@dataclass
class TaskDetails:
    action: Literal["Task"] = "Task"
    agent_type: str = ""
    purpose: str = ""
    outcome: str = ""

EntryDetails = Union[TodoWriteDetails, EditDetails, BashDetails, VerifyDetails, CheckpointDetails, TaskDetails]
```

#### Acceptance Criteria
- [ ] GIVEN TodoWrite action WHEN entry created THEN TodoWriteDetails used with todos_affected
- [ ] GIVEN Edit action WHEN entry created THEN EditDetails used with files list
- [ ] GIVEN Bash test action WHEN entry created THEN BashDetails has command_type="test"
- [ ] GIVEN Verify action WHEN entry created THEN VerifyDetails has expected/actual states
- [ ] GIVEN invalid discriminator WHEN validated THEN error raised

#### Verification
```bash
uv run pytest tests/accountability/test_schema.py -v
```

---

### T2.4: Operation Logging (REQ-002)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/worklog.py` (extend)
- `tests/accountability/test_worklog.py` (extend)

#### Steps
1. Implement `append()` method in Worklog class
2. Add tier significance check before logging
3. Create WorklogEntry with timestamp, action, status, context, details
4. Ensure append latency ≤200ms
5. Validate token cost ≤30 tokens per entry
6. Write tests for tier-filtered logging

#### Implementation Details
```python
# worklog.py - WorklogEntry
@dataclass
class WorklogEntry:
    timestamp: str  # ISO8601
    action: str  # TodoWrite|Edit|MultiEdit|Write|Bash|Task|Checkpoint|Verify
    status: str  # initiated|completed|failed|retried|skipped|timeout
    context: str  # Brief description
    details: EntryDetails
    tokens_consumed: int = 0

# Worklog.append()
def append(self, entry: WorklogEntry) -> None:
    """Append entry if operation is tier-significant. Latency ≤200ms, ≤30 tokens."""
    if not self._is_tier_significant(entry.action, self.tier):
        return
    self.entries.append(entry)
```

#### Acceptance Criteria
- [ ] GIVEN STRICT tier and Edit operation WHEN completed THEN entry appended
- [ ] GIVEN LIGHT tier and Edit operation WHEN completed THEN NO entry appended
- [ ] GIVEN TodoWrite operation WHEN any tier THEN entry appended
- [ ] GIVEN append operation WHEN timed THEN latency ≤200ms
- [ ] GIVEN append operation WHEN tokens counted THEN cost ≤30 tokens

#### Verification
```bash
uv run pytest tests/accountability/test_worklog.py::TestOperationLogging -v
```

---

### T2.5: Batched Worklog Writes (REQ-003)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/buffer.py` (create)
- `tests/accountability/test_buffer.py` (create)

#### Steps
1. Create `buffer.py` with `WorklogBuffer` class
2. Implement threshold-based flush (10 entries)
3. Implement time-based flush (30 seconds)
4. Implement error-triggered flush
5. Implement completion-triggered flush
6. Verify MCP call reduction ≥80%
7. Write comprehensive unit tests

#### Implementation Details
```python
# buffer.py
import asyncio
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class WorklogBuffer:
    entries: list[WorklogEntry] = field(default_factory=list)
    threshold: int = 10
    time_threshold_seconds: int = 30
    last_flush_time: float = 0
    on_flush: Callable[[list[WorklogEntry]], None] | None = None

    def append(self, entry: WorklogEntry) -> None:
        self.entries.append(entry)
        if len(self.entries) >= self.threshold:
            self._trigger_flush("threshold_flush")

    def check_time_flush(self) -> None:
        """Called periodically to check time-based flush"""
        if time.time() - self.last_flush_time >= self.time_threshold_seconds:
            self._trigger_flush("time_flush")

    def flush_on_error(self) -> None:
        """Emergency flush on error"""
        self._trigger_flush("error_flush")

    def flush_on_completion(self) -> None:
        """Final flush on task completion"""
        self._trigger_flush("completion_flush")

    def _trigger_flush(self, trigger: str) -> None:
        if self.entries and self.on_flush:
            self.on_flush(self.entries.copy())
            self.entries.clear()
            self.last_flush_time = time.time()
```

#### Acceptance Criteria
- [ ] GIVEN 9 entries buffered WHEN 10th added THEN flush triggered
- [ ] GIVEN 5 entries WHEN 30s elapsed THEN time-based flush triggered
- [ ] GIVEN entries buffered WHEN Bash fails THEN emergency flush triggered
- [ ] GIVEN entries buffered WHEN task completes THEN completion flush triggered
- [ ] GIVEN 30 operations logged WHEN counted THEN only 3 MCP calls (≥80% reduction)

#### Verification
```bash
uv run pytest tests/accountability/test_buffer.py -v
```

---

### T2.6: Worklog Finalization (REQ-007)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/worklog.py` (extend)
- `tests/accountability/test_worklog.py` (extend)

#### Steps
1. Implement `finalize()` method in Worklog class
2. Flush all buffered entries
3. Generate WorklogSummary with total_operations, files_modified, etc.
4. Set outcome (success|failure|aborted|abandoned)
5. Set completed_at timestamp
6. Write to memory via Serena or fallback
7. Write unit tests for all outcomes

#### Implementation Details
```python
# worklog.py - WorklogSummary
@dataclass
class WorklogSummary:
    total_operations: int = 0
    files_modified: int = 0
    todos_completed: int = 0
    verification_results: dict = field(default_factory=lambda: {
        "passed": 0, "failed": 0, "skipped": 0, "user_accepted": 0
    })
    checkpoints_generated: int = 0
    total_tokens: int = 0
    duration_seconds: float = 0

# Worklog.finalize()
async def finalize(self, outcome: str) -> WorklogSummary:
    """Finalize worklog: flush buffer, generate summary, write to memory"""
    await self._buffer.flush_on_completion()

    self.outcome = outcome
    self.completed_at = datetime.utcnow().isoformat() + "Z"
    self.summary = self._generate_summary()

    # Write completion record
    await self._write_to_memory()

    return self.summary
```

#### Acceptance Criteria
- [ ] GIVEN task completes with success WHEN finalize called THEN outcome="success" and summary complete
- [ ] GIVEN task fails WHEN finalize called THEN outcome="failure" and summary includes failure details
- [ ] GIVEN task aborted WHEN finalize called THEN outcome="aborted" and partial summary
- [ ] GIVEN finalization WHEN summary generated THEN total_operations, duration, tokens all populated
- [ ] GIVEN finalization WHEN written THEN readable via `read_memory("_worklog/{session_id}")`

#### Verification
```bash
uv run pytest tests/accountability/test_worklog.py::TestWorklogFinalization -v
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 6 deliverables code-complete
- [ ] All unit tests passing: `uv run pytest tests/accountability/test_interfaces.py tests/accountability/test_worklog.py tests/accountability/test_schema.py tests/accountability/test_buffer.py -v`
- [ ] Coverage ≥95% for new code
- [ ] Integration test: STANDARD task creates worklog with correct entries
- [ ] Batch buffer reduces MCP calls by ≥80%
- [ ] Time-based flush triggers at 30 seconds
- [ ] No regressions in existing task execution

### Integration Tests (M2-INT)
```bash
# Run M2 integration tests
uv run pytest tests/accountability/ -m "m2_integration" -v
```

### Proceed to M3 When
- [ ] All checklist items verified
- [ ] No blocking issues identified
- [ ] M2 integration tests pass

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `src/superclaude/accountability/interfaces.py` | Service interfaces | Create |
| `src/superclaude/accountability/schema.py` | Entry detail types | Create |
| `src/superclaude/accountability/worklog.py` | Core worklog | Create |
| `src/superclaude/accountability/buffer.py` | Batch buffer | Create |
| `tests/accountability/test_interfaces.py` | Interface tests | Create |
| `tests/accountability/test_schema.py` | Schema tests | Create |
| `tests/accountability/test_worklog.py` | Worklog tests | Create |
| `tests/accountability/test_buffer.py` | Buffer tests | Create |
