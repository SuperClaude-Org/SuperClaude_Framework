# Tasklist: M3 - Verification System

## Metadata
- **Milestone**: M3
- **Dependencies**: M2 (Core Worklog System)
- **Estimated Complexity**: High
- **Primary Persona**: Backend
- **Risk Level**: High (state machine complexity, circuit breaker edge cases)
- **Coverage Requirement**: 100% for state machine and circuit breaker

---

## Tasks

### T3.1: Status Verification Loop (REQ-004)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/verification.py` (create)
- `tests/accountability/test_verification.py` (create)

#### Steps
1. Create `verification.py` with `VerificationService` class
2. Implement `shouldVerify()` method (STRICT tier only)
3. Implement `verifyTodoState()` method comparing expected vs actual
4. Add status and count matching per SPEC-REVISED.md
5. Implement 100ms retry delay
6. Ensure verification completes within 1000ms
7. Write unit tests with mocked todo states

#### Implementation Details
```python
# verification.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class VerificationResult:
    status: Literal["pass", "fail", "timeout"]
    expected_state: dict
    actual_state: dict
    mismatch_details: str | None = None

class VerificationService:
    def should_verify(self, tier: str) -> bool:
        """Only STRICT tier requires verification"""
        return tier == "STRICT"

    async def verify_todo_state(
        self,
        expected: dict,
        actual: dict
    ) -> VerificationResult:
        """
        Compare expected vs actual todo state.
        Match criteria: status (exact), count (exact)
        Ignore: content, activeForm
        """
        # Status comparison
        if expected.get("status") != actual.get("status"):
            return VerificationResult(
                status="fail",
                expected_state=expected,
                actual_state=actual,
                mismatch_details=f"status: expected={expected.get('status')}, actual={actual.get('status')}"
            )

        # Count comparison
        expected_count = expected.get("count", 0)
        actual_count = actual.get("count", 0)
        if expected_count != actual_count:
            return VerificationResult(
                status="fail",
                expected_state=expected,
                actual_state=actual,
                mismatch_details=f"count: expected={expected_count}, actual={actual_count}"
            )

        return VerificationResult(
            status="pass",
            expected_state=expected,
            actual_state=actual
        )
```

#### Acceptance Criteria
- [ ] GIVEN STRICT tier WHEN shouldVerify called THEN returns True
- [ ] GIVEN STANDARD tier WHEN shouldVerify called THEN returns False
- [ ] GIVEN matching status/count WHEN verified THEN result.status="pass"
- [ ] GIVEN mismatched status WHEN verified THEN result.status="fail" with details
- [ ] GIVEN verification WHEN timed THEN completes within 1000ms

#### Verification
```bash
uv run pytest tests/accountability/test_verification.py::TestVerificationLoop -v
```

---

### T3.2: Verification State Machine (REQ-013)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/verification.py` (extend)
- `tests/accountability/test_verification.py` (extend)

#### Steps
1. Implement full state machine per SPEC-REVISED.md Section 3.3
2. Add state transitions: TodoWrite → Read → Match/Mismatch → Retry/Escalate
3. Implement single retry with 100ms delay
4. Add timeout handling (1000ms)
5. Log all state transitions to worklog
6. Write 100% coverage unit tests

#### Implementation Details
```python
# verification.py - State Machine
from enum import Enum, auto

class VerificationState(Enum):
    TODOWRITE_EXECUTED = auto()
    READ_STATE = auto()
    MATCH = auto()
    MISMATCH = auto()
    RETRY = auto()
    TIMEOUT = auto()
    ESCALATE = auto()
    PASS = auto()

class VerificationStateMachine:
    state: VerificationState = VerificationState.TODOWRITE_EXECUTED
    retry_count: int = 0
    max_automatic_retries: int = 1
    retry_delay_ms: int = 100
    timeout_ms: int = 1000

    async def execute(self, expected: dict, read_actual: Callable) -> VerificationResult:
        """Execute verification state machine"""
        self.state = VerificationState.READ_STATE

        try:
            actual = await asyncio.wait_for(
                read_actual(),
                timeout=self.timeout_ms / 1000
            )
        except asyncio.TimeoutError:
            self.state = VerificationState.TIMEOUT
            return await self._handle_retry(expected, read_actual)

        result = await self._compare(expected, actual)

        if result.status == "pass":
            self.state = VerificationState.PASS
            return result
        else:
            self.state = VerificationState.MISMATCH
            return await self._handle_retry(expected, read_actual)

    async def _handle_retry(self, expected: dict, read_actual: Callable) -> VerificationResult:
        if self.retry_count < self.max_automatic_retries:
            self.state = VerificationState.RETRY
            self.retry_count += 1
            await asyncio.sleep(self.retry_delay_ms / 1000)
            return await self.execute(expected, read_actual)
        else:
            self.state = VerificationState.ESCALATE
            return VerificationResult(status="fail", ...)
```

#### Acceptance Criteria
- [ ] GIVEN TodoWrite executed WHEN state machine starts THEN transitions to READ_STATE
- [ ] GIVEN match WHEN compared THEN transitions to PASS
- [ ] GIVEN mismatch WHEN first attempt THEN transitions to RETRY after 100ms
- [ ] GIVEN mismatch on retry WHEN retry exhausted THEN transitions to ESCALATE
- [ ] GIVEN timeout WHEN reading state THEN handles as mismatch
- [ ] GIVEN any transition WHEN logged THEN worklog entry created

#### Verification
```bash
uv run pytest tests/accountability/test_verification.py::TestVerificationStateMachine -v --cov --cov-fail-under=100
```

---

### T3.3: Verification Circuit Breaker (REQ-005)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/circuit_breaker.py` (create)
- `tests/accountability/test_circuit_breaker.py` (create)

#### Steps
1. Create `circuit_breaker.py` with `VerificationCircuitBreaker` class
2. Implement max 3 total attempts counter (including user retries)
3. Implement circuit OPEN state blocking further retries
4. Add 300s (5 min) cooldown period
5. Implement forced resolution when circuit opens
6. Write 100% coverage unit tests

#### Implementation Details
```python
# circuit_breaker.py
from enum import Enum, auto
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = auto()  # Normal operation
    OPEN = auto()    # Blocking retries

@dataclass
class CircuitBreaker:
    state: CircuitState = CircuitState.CLOSED
    total_attempts: int = 0
    max_total_attempts: int = 3
    cooldown_seconds: int = 300
    opened_at: float | None = None

    def record_attempt(self, success: bool) -> None:
        """Record verification attempt"""
        self.total_attempts += 1
        if success:
            self.reset()
        elif self.total_attempts >= self.max_total_attempts:
            self._open()

    def can_retry(self) -> bool:
        """Check if retry is allowed"""
        if self.state == CircuitState.OPEN:
            # Check cooldown
            if self.opened_at and (time.time() - self.opened_at) >= self.cooldown_seconds:
                self._half_open()
                return True
            return False
        return self.total_attempts < self.max_total_attempts

    def _open(self) -> None:
        self.state = CircuitState.OPEN
        self.opened_at = time.time()

    def reset(self) -> None:
        self.state = CircuitState.CLOSED
        self.total_attempts = 0
        self.opened_at = None
```

#### Acceptance Criteria
- [ ] GIVEN initial state WHEN checked THEN circuit CLOSED
- [ ] GIVEN failure WHEN recorded THEN total_attempts increments
- [ ] GIVEN success WHEN recorded THEN counter resets
- [ ] GIVEN 3 total failures WHEN next retry attempted THEN circuit OPEN
- [ ] GIVEN circuit OPEN WHEN can_retry called THEN returns False
- [ ] GIVEN circuit OPEN after 300s WHEN checked THEN allows test request

#### Verification
```bash
uv run pytest tests/accountability/test_circuit_breaker.py -v --cov --cov-fail-under=100
```

---

### T3.4: User Escalation Interface (REQ-014)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/escalation.py` (create)
- `tests/accountability/test_escalation.py` (create)

#### Steps
1. Create `escalation.py` with `UserEscalation` class
2. Define resolution options: Accept, Abort, Continue
3. Implement option presentation to user
4. Handle each resolution action
5. Log user decision to worklog
6. Write unit tests for each resolution path

#### Implementation Details
```python
# escalation.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

class ResolutionOption(Enum):
    ACCEPT = "accept"   # Accept current state as correct
    ABORT = "abort"     # Abort task with partial worklog
    CONTINUE = "continue"  # Continue without verification (log risk)

@dataclass
class ResolutionChoice:
    option: ResolutionOption
    rationale: str | None = None

class UserEscalation:
    def present_options(self) -> str:
        """Present resolution options to user"""
        return """
Verification failed after 3 attempts. Please choose:

[1] Accept - Accept current state as correct
[2] Abort  - Abort task with partial worklog
[3] Continue - Continue without verification (logged as risk)

Enter choice (1/2/3): """

    async def handle_resolution(
        self,
        choice: ResolutionChoice,
        worklog: "Worklog",
        on_accept: Callable,
        on_abort: Callable,
        on_continue: Callable
    ) -> None:
        """Handle user's resolution choice"""
        # Log decision to worklog
        worklog.append(WorklogEntry(
            action="Verify",
            status="user_" + choice.option.value,
            context=f"User selected: {choice.option.value}",
            details=VerifyDetails(
                verification_result=choice.option.value,
                ...
            )
        ))

        match choice.option:
            case ResolutionOption.ACCEPT:
                await on_accept()
            case ResolutionOption.ABORT:
                await on_abort()
            case ResolutionOption.CONTINUE:
                await on_continue()
```

#### Acceptance Criteria
- [ ] GIVEN circuit breaker open WHEN user presented options THEN 3 choices shown
- [ ] GIVEN user selects Accept WHEN handled THEN verification marked "user_accepted" and continues
- [ ] GIVEN user selects Abort WHEN handled THEN task stops with outcome="aborted"
- [ ] GIVEN user selects Continue WHEN handled THEN continues with "bypassed" warning
- [ ] GIVEN any choice WHEN logged THEN worklog contains user decision

#### Verification
```bash
uv run pytest tests/accountability/test_escalation.py -v
```

---

### T3.5: Latency Budget Enforcement (IMP-002)
**Type**: IMPROVEMENT
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/timeout.py` (create)
- `tests/accountability/test_timeout.py` (create)

#### Steps
1. Create `timeout.py` with `LatencyBudget` class
2. Implement 3000ms aggregate budget for all accountability operations
3. Track time spent by each operation type
4. Skip optional operations when budget tight
5. Implement adaptive timeout behavior
6. Write unit tests for budget enforcement

#### Implementation Details
```python
# timeout.py
from dataclasses import dataclass, field
import time

@dataclass
class LatencyBudget:
    total_budget_ms: int = 3000
    remaining_ms: int = 3000
    operation_times: dict[str, float] = field(default_factory=dict)

    def start_operation(self, name: str) -> "OperationTimer":
        return OperationTimer(self, name)

    def record_operation(self, name: str, elapsed_ms: float) -> None:
        self.operation_times[name] = elapsed_ms
        self.remaining_ms -= elapsed_ms

    def can_afford(self, estimated_ms: int) -> bool:
        return self.remaining_ms >= estimated_ms

    def should_skip_optional(self) -> bool:
        """Skip optional ops if <20% budget remaining"""
        return self.remaining_ms < (self.total_budget_ms * 0.2)

@dataclass
class OperationTimer:
    budget: LatencyBudget
    name: str
    start_time: float = field(default_factory=time.time)

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        elapsed = (time.time() - self.start_time) * 1000
        self.budget.record_operation(self.name, elapsed)
```

#### Acceptance Criteria
- [ ] GIVEN accountability phase starts WHEN budget created THEN 3000ms available
- [ ] GIVEN operations consuming budget WHEN tracked THEN remaining decrements
- [ ] GIVEN <600ms remaining (<20%) WHEN checkpoint requested THEN skipped
- [ ] GIVEN operation would exceed budget WHEN checked THEN can_afford returns False
- [ ] GIVEN aggregate timeout reached WHEN operation attempted THEN raises or skips

#### Verification
```bash
uv run pytest tests/accountability/test_timeout.py -v
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 5 deliverables code-complete
- [ ] Unit tests passing with **100% coverage** for verification and circuit breaker:
  ```bash
  uv run pytest tests/accountability/test_verification.py tests/accountability/test_circuit_breaker.py -v --cov --cov-fail-under=100
  ```
- [ ] Integration test: Verification pass on first attempt
- [ ] Integration test: Verification fail, retry succeeds
- [ ] Integration test: Circuit breaker trips after 3 failures
- [ ] User escalation options function correctly
- [ ] No infinite loops possible in verification
- [ ] Latency budget enforced (total ≤3000ms)

### Integration Tests (M3-INT)
```bash
# Run M3 integration tests
uv run pytest tests/accountability/ -m "m3_integration" -v
```

### Proceed to M4 When
- [ ] All checklist items verified
- [ ] 100% coverage achieved for critical paths
- [ ] No blocking issues identified
- [ ] M3 integration tests pass

---

## File Summary

| File | Purpose | Coverage Req |
|------|---------|--------------|
| `src/superclaude/accountability/verification.py` | State machine | 100% |
| `src/superclaude/accountability/circuit_breaker.py` | Circuit breaker | 100% |
| `src/superclaude/accountability/escalation.py` | User resolution | 90% |
| `src/superclaude/accountability/timeout.py` | Latency budget | 90% |
| `tests/accountability/test_verification.py` | Verification tests | - |
| `tests/accountability/test_circuit_breaker.py` | Circuit tests | - |
| `tests/accountability/test_escalation.py` | Escalation tests | - |
| `tests/accountability/test_timeout.py` | Timeout tests | - |
