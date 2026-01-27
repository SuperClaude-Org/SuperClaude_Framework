# Tasklist: M4 - Checkpoint & Optimization

## Metadata
- **Milestone**: M4
- **Dependencies**: M2 (Core Worklog System)
- **Estimated Complexity**: Medium
- **Primary Persona**: Backend, Performance
- **Files to Create/Modify**: 5 source files, 5 test files

---

## Tasks

### T4.1: Checkpoint Summaries (REQ-006)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/checkpoints.py` (create)
- `tests/accountability/test_checkpoints.py` (create)

#### Steps
1. Create `checkpoints.py` with `CheckpointService` class
2. Implement tier-based checkpoint mapping (STRICT=3, STANDARD=1, LIGHT/EXEMPT=0)
3. Define checkpoint triggers per SPEC-REVISED.md Section FR-005
4. Generate summary consuming worklog entries
5. Detect deviations (todo_incomplete, unplanned_file, test_failure)
6. Write comprehensive unit tests

#### Implementation Details
```python
# checkpoints.py
from dataclasses import dataclass, field
from enum import Enum

class CheckpointPhase(Enum):
    PLANNING_COMPLETE = "planning_complete"
    EXECUTION_COMPLETE = "execution_complete"
    VERIFICATION_COMPLETE = "verification_complete"

@dataclass
class CheckpointSummary:
    phase: str
    timestamp: str
    operations_since_last: int = 0
    files_modified: list[str] = field(default_factory=list)
    todos_completed: int = 0
    todos_remaining: int = 0
    deviations: list[dict] = field(default_factory=list)
    verification_results: dict = field(default_factory=lambda: {
        "passed": 0, "failed": 0, "skipped": 0
    })

class CheckpointService:
    TIER_CHECKPOINTS = {
        "STRICT": [
            CheckpointPhase.PLANNING_COMPLETE,
            CheckpointPhase.EXECUTION_COMPLETE,
            CheckpointPhase.VERIFICATION_COMPLETE
        ],
        "STANDARD": [CheckpointPhase.EXECUTION_COMPLETE],
        "LIGHT": [],
        "EXEMPT": []
    }

    def should_checkpoint(self, tier: str, phase: CheckpointPhase) -> bool:
        return phase in self.TIER_CHECKPOINTS.get(tier, [])

    def generate_summary(
        self,
        worklog: "Worklog",
        phase: CheckpointPhase
    ) -> CheckpointSummary:
        """Generate checkpoint summary from worklog entries"""
        entries_since_last = self._get_entries_since_last_checkpoint(worklog)

        return CheckpointSummary(
            phase=phase.value,
            timestamp=datetime.utcnow().isoformat() + "Z",
            operations_since_last=len(entries_since_last),
            files_modified=self._extract_modified_files(entries_since_last),
            todos_completed=self._count_completed_todos(worklog),
            todos_remaining=self._count_remaining_todos(worklog),
            deviations=self._detect_deviations(worklog, phase)
        )

    def _detect_deviations(self, worklog: "Worklog", phase: CheckpointPhase) -> list[dict]:
        """Detect deviations from expected progress"""
        deviations = []
        # Check for incomplete todos at phase boundary
        # Check for unplanned file modifications
        # Check for test failures
        return deviations
```

#### Acceptance Criteria
- [ ] GIVEN STRICT tier WHEN planning complete THEN checkpoint 1 generated
- [ ] GIVEN STRICT tier WHEN execution complete THEN checkpoint 2 generated
- [ ] GIVEN STRICT tier WHEN verification complete THEN checkpoint 3 generated
- [ ] GIVEN STANDARD tier WHEN execution complete THEN checkpoint generated
- [ ] GIVEN LIGHT tier WHEN any phase THEN NO checkpoint generated
- [ ] GIVEN EXEMPT tier WHEN any phase THEN NO checkpoint generated
- [ ] GIVEN checkpoint WHEN deviations exist THEN listed with severity

#### Verification
```bash
uv run pytest tests/accountability/test_checkpoints.py -v
```

---

### T4.2: Token Efficiency (IMP-001)
**Type**: IMPROVEMENT
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/metrics.py` (create)
- `tests/accountability/test_metrics.py` (create)

#### Steps
1. Create `metrics.py` with `TokenMetrics` class
2. Track token consumption per operation type
3. Implement tier-specific bounds checking
4. Calculate weighted average overhead
5. Alert when approaching bounds
6. Write unit tests validating bounds

#### Implementation Details
```python
# metrics.py
from dataclasses import dataclass, field

@dataclass
class TokenBounds:
    """Token overhead bounds per tier with batching"""
    STRICT_WITH_BATCHING: int = 750
    STRICT_WITHOUT_BATCHING: int = 1200
    STANDARD_WITH_BATCHING: int = 300
    STANDARD_WITHOUT_BATCHING: int = 500
    LIGHT_WITH_BATCHING: int = 60
    LIGHT_WITHOUT_BATCHING: int = 100
    EXEMPT: int = 0

@dataclass
class TokenMetrics:
    tier: str
    batching_enabled: bool = True
    tokens_by_operation: dict[str, int] = field(default_factory=dict)
    total_tokens: int = 0

    def record_tokens(self, operation: str, tokens: int) -> None:
        self.tokens_by_operation[operation] = self.tokens_by_operation.get(operation, 0) + tokens
        self.total_tokens += tokens

    def get_bound(self) -> int:
        bounds = TokenBounds()
        if self.tier == "STRICT":
            return bounds.STRICT_WITH_BATCHING if self.batching_enabled else bounds.STRICT_WITHOUT_BATCHING
        elif self.tier == "STANDARD":
            return bounds.STANDARD_WITH_BATCHING if self.batching_enabled else bounds.STANDARD_WITHOUT_BATCHING
        elif self.tier == "LIGHT":
            return bounds.LIGHT_WITH_BATCHING if self.batching_enabled else bounds.LIGHT_WITHOUT_BATCHING
        return bounds.EXEMPT

    def is_within_bounds(self) -> bool:
        return self.total_tokens <= self.get_bound()

    def get_utilization(self) -> float:
        bound = self.get_bound()
        return self.total_tokens / bound if bound > 0 else 0

    @staticmethod
    def calculate_weighted_average(task_distribution: dict[str, float]) -> float:
        """
        Calculate weighted average overhead.
        Default distribution: STRICT=10%, STANDARD=60%, LIGHT=25%, EXEMPT=5%
        Target: ≤300 tokens
        """
        bounds = TokenBounds()
        return (
            task_distribution.get("STRICT", 0.1) * bounds.STRICT_WITH_BATCHING +
            task_distribution.get("STANDARD", 0.6) * bounds.STANDARD_WITH_BATCHING +
            task_distribution.get("LIGHT", 0.25) * bounds.LIGHT_WITH_BATCHING +
            task_distribution.get("EXEMPT", 0.05) * bounds.EXEMPT
        )
```

#### Acceptance Criteria
- [ ] GIVEN STRICT task with batching WHEN complete THEN total tokens ≤750
- [ ] GIVEN STANDARD task with batching WHEN complete THEN total tokens ≤300
- [ ] GIVEN LIGHT task WHEN complete THEN total tokens ≤60
- [ ] GIVEN EXEMPT task WHEN complete THEN total tokens = 0
- [ ] GIVEN default task distribution WHEN weighted avg calculated THEN ≤300 tokens
- [ ] GIVEN tokens approaching bound WHEN threshold crossed THEN warning logged

#### Verification
```bash
uv run pytest tests/accountability/test_metrics.py -v
```

---

### T4.3: Memory Retention Policy (IMP-003)
**Type**: IMPROVEMENT
**Priority**: P2-Medium
**Files Affected**:
- `src/superclaude/accountability/retention.py` (create)
- `tests/accountability/test_retention.py` (create)

#### Steps
1. Create `retention.py` with `RetentionManager` class
2. Implement 24h TTL for raw worklogs
3. Implement 30d TTL for summaries
4. Implement max 50 active worklogs limit
5. Add LRU eviction when limit reached
6. Implement cleanup on session start
7. Write unit tests for all retention scenarios

#### Implementation Details
```python
# retention.py
from dataclasses import dataclass
import time

@dataclass
class RetentionPolicy:
    raw_worklog_ttl_hours: int = 24
    summary_ttl_days: int = 30
    max_active_worklogs: int = 50
    warning_threshold: int = 40

class RetentionManager:
    policy: RetentionPolicy = RetentionPolicy()

    async def cleanup_on_session_start(self, memory_service) -> dict:
        """Run cleanup at session start"""
        results = {
            "abandoned_marked": 0,
            "summaries_extracted": 0,
            "raw_deleted": 0,
            "evicted_lru": 0
        }

        # Find worklogs with outcome='in_progress' older than 24h
        old_worklogs = await self._find_stale_worklogs(memory_service)
        for worklog_id in old_worklogs:
            await self._mark_abandoned(worklog_id, memory_service)
            await self._extract_summary(worklog_id, memory_service)
            await self._delete_raw(worklog_id, memory_service)
            results["abandoned_marked"] += 1
            results["summaries_extracted"] += 1
            results["raw_deleted"] += 1

        # Enforce max active worklogs
        active_count = await self._count_active_worklogs(memory_service)
        if active_count > self.policy.max_active_worklogs:
            to_evict = active_count - self.policy.max_active_worklogs
            await self._evict_lru(to_evict, memory_service)
            results["evicted_lru"] = to_evict

        return results

    async def should_warn(self, memory_service) -> bool:
        """Check if approaching limit"""
        count = await self._count_active_worklogs(memory_service)
        return count >= self.policy.warning_threshold
```

#### Acceptance Criteria
- [ ] GIVEN session start WHEN cleanup runs THEN worklogs >24h marked abandoned
- [ ] GIVEN abandoned worklog WHEN processed THEN summary extracted to `_worklog_summary/`
- [ ] GIVEN raw worklog archived WHEN cleanup completes THEN raw deleted
- [ ] GIVEN 55 active worklogs WHEN cleanup runs THEN oldest 5 evicted (LRU)
- [ ] GIVEN 40 active worklogs WHEN checked THEN warning threshold reached
- [ ] GIVEN summaries >30d old WHEN cleanup runs THEN deleted

#### Verification
```bash
uv run pytest tests/accountability/test_retention.py -v
```

---

### T4.4: Adaptive Timeout Behavior (IMP-004)
**Type**: IMPROVEMENT
**Priority**: P2-Medium
**Files Affected**:
- `src/superclaude/accountability/timeout.py` (extend)
- `tests/accountability/test_timeout.py` (extend)

#### Steps
1. Extend `timeout.py` with adaptive behavior
2. Track budget utilization per phase
3. Skip optional operations if previous phase used >80% of allocation
4. Define optional vs required operations
5. Log skipped operations to worklog
6. Write unit tests for adaptive behavior

#### Implementation Details
```python
# timeout.py (extend)
@dataclass
class AdaptiveTimeout:
    phases: dict[str, float] = field(default_factory=dict)  # phase -> utilization
    skip_threshold: float = 0.8  # 80%

    OPTIONAL_OPERATIONS = ["checkpoint", "metrics_log", "summary_update"]
    REQUIRED_OPERATIONS = ["worklog_init", "worklog_finalize", "verification"]

    def record_phase_completion(self, phase: str, utilization: float) -> None:
        self.phases[phase] = utilization

    def should_skip_optional(self, operation: str) -> bool:
        """Skip optional ops if previous phase was tight on budget"""
        if operation not in self.OPTIONAL_OPERATIONS:
            return False  # Required ops never skipped

        # Check last phase utilization
        if self.phases:
            last_phase = list(self.phases.keys())[-1]
            if self.phases[last_phase] > self.skip_threshold:
                return True

        return False

    def get_adjusted_timeout(self, operation: str, base_timeout_ms: int) -> int:
        """Reduce timeout for optional ops when budget tight"""
        if self.should_skip_optional(operation):
            return 0  # Skip entirely
        return base_timeout_ms
```

#### Acceptance Criteria
- [ ] GIVEN planning phase used 85% of allocation WHEN execution starts THEN checkpoints skipped
- [ ] GIVEN planning phase used 60% of allocation WHEN execution starts THEN checkpoints run
- [ ] GIVEN operation marked optional WHEN skipped THEN logged to worklog
- [ ] GIVEN operation marked required WHEN budget tight THEN still runs
- [ ] GIVEN multiple phases WHEN tracked THEN can detect trend

#### Verification
```bash
uv run pytest tests/accountability/test_timeout.py::TestAdaptiveTimeout -v
```

---

### T4.5: Checkpoint Detection Service (FR-007)
**Type**: FEATURE
**Priority**: P2-Medium
**Files Affected**:
- `src/superclaude/accountability/checkpoint_detection.py` (create)
- `tests/accountability/test_checkpoint_detection.py` (create)

#### Steps
1. Create `checkpoint_detection.py` with `CheckpointDetectionService` class implementing interface from SPEC-REVISED.md
2. Implement `should_detect(tier)` - returns True for STRICT/STANDARD, False for LIGHT/EXEMPT
3. Implement `detect(tier)` with `list_memories` scan for `_worklog/*` where outcome in ['abandoned', 'in_progress']
4. Implement LRU ordering (max 10 worklogs) by `started_at` timestamp
5. Implement 500ms timeout with silent skip on timeout
6. Implement `format_notification(result)` using template from SPEC-REVISED.md
7. Integrate into task startup flow after tier classification, before worklog init
8. Write unit tests for all 5 Gherkin scenarios from SPEC
9. Write integration tests for STRICT/STANDARD detection

#### Implementation Details
```python
# checkpoint_detection.py
from dataclasses import dataclass
from typing import Optional, Protocol
import asyncio

@dataclass
class DetectionResult:
    """Result of checkpoint detection scan."""
    session_id: str
    outcome: str  # "abandoned" | "in_progress"
    task_description: str
    started_at: str  # ISO8601
    restore_command: str

class MemoryService(Protocol):
    """Protocol for memory service dependency."""
    async def list_memories(self, pattern: str, limit: int) -> list[dict]: ...

class CheckpointDetectionService:
    """
    Smart checkpoint detection service (FR-007).

    Detects abandoned/in-progress worklogs after tier classification
    and notifies user of restoration options.

    Timing: After tier classification, before worklog initialization
    Scope: STRICT and STANDARD tiers only
    Timeout: 500ms hard limit, silent skip on timeout
    """
    TIMEOUT_MS = 500
    MAX_SCAN = 10
    DETECTABLE_TIERS = ["STRICT", "STANDARD"]
    ACTIONABLE_OUTCOMES = ["abandoned", "in_progress"]

    def __init__(self, restore_command_template: str = "/sc:load --checkpoint {session_id}"):
        self.restore_command_template = restore_command_template

    def should_detect(self, tier: str) -> bool:
        """Check if detection should run for this tier."""
        return tier in self.DETECTABLE_TIERS

    async def detect(
        self,
        tier: str,
        memory_service: MemoryService
    ) -> Optional[DetectionResult]:
        """
        Detect abandoned or in-progress worklogs.

        Returns the most recent actionable worklog, or None if:
        - Tier is LIGHT/EXEMPT (skip detection)
        - No actionable worklogs found
        - Timeout exceeded (silent skip)
        - MCP error (silent skip with warning log)
        """
        if not self.should_detect(tier):
            return None

        try:
            worklogs = await asyncio.wait_for(
                self._scan_worklogs(memory_service),
                timeout=self.TIMEOUT_MS / 1000
            )

            # Filter to actionable outcomes only
            actionable = [
                w for w in worklogs
                if w.get("outcome") in self.ACTIONABLE_OUTCOMES
            ]

            if not actionable:
                return None

            # Return most recent (first in LRU-sorted scan)
            most_recent = actionable[0]
            return DetectionResult(
                session_id=most_recent["session_id"],
                outcome=most_recent["outcome"],
                task_description=most_recent.get("task_description", "Unknown task"),
                started_at=most_recent["started_at"],
                restore_command=self.restore_command_template.format(
                    session_id=most_recent["session_id"]
                )
            )
        except asyncio.TimeoutError:
            # Silent skip per FR-007 specification
            return None
        except Exception:
            # MCP error - silent skip with logged warning
            return None

    async def _scan_worklogs(self, memory_service: MemoryService) -> list[dict]:
        """Scan worklogs ordered by started_at (LRU)."""
        memories = await memory_service.list_memories(
            pattern="_worklog/*",
            limit=self.MAX_SCAN
        )
        # Sort by started_at descending (most recent first)
        return sorted(
            memories,
            key=lambda m: m.get("started_at", ""),
            reverse=True
        )

    def format_notification(self, result: DetectionResult) -> str:
        """Format user notification for detected worklog."""
        return f"""ℹ️ Previous work detected: {result.task_description} ({result.outcome})
Session: {result.session_id} | Started: {result.started_at}
To restore: {result.restore_command}"""
```

#### Acceptance Criteria
- [ ] GIVEN STRICT task AND abandoned worklog exists WHEN tier classification completes THEN notification displayed
- [ ] GIVEN STANDARD task AND in_progress worklog exists WHEN detection runs THEN notification displayed
- [ ] GIVEN LIGHT tier WHEN execution begins THEN `should_detect` returns False and no scan performed
- [ ] GIVEN EXEMPT tier WHEN execution begins THEN `should_detect` returns False and no scan performed
- [ ] GIVEN `list_memories` takes >500ms WHEN timeout exceeded THEN returns None silently
- [ ] GIVEN no worklogs with outcome in ['abandoned', 'in_progress'] WHEN detection runs THEN returns None
- [ ] GIVEN worklog with outcome='success' WHEN detection runs THEN excluded from results
- [ ] GIVEN multiple abandoned worklogs WHEN detection runs THEN most recent (by started_at) returned
- [ ] Detection completes within 500ms for ≤10 worklogs

#### Verification
```bash
uv run pytest tests/accountability/test_checkpoint_detection.py -v
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 5 deliverables code-complete
- [ ] Unit tests passing with ≥90% coverage:
  ```bash
  uv run pytest tests/accountability/test_checkpoints.py tests/accountability/test_metrics.py tests/accountability/test_retention.py tests/accountability/test_timeout.py -v --cov --cov-fail-under=90
  ```
- [ ] STRICT tasks generate exactly 3 checkpoints
- [ ] STANDARD tasks generate exactly 1 checkpoint
- [ ] LIGHT/EXEMPT tasks generate 0 checkpoints
- [ ] Token overhead ≤750 for STRICT with batching
- [ ] Weighted average ≤300 tokens
- [ ] Memory cleanup runs on session start
- [ ] Adaptive timeout skips optional operations when appropriate
- [ ] Checkpoint detection completes within 500ms for STRICT/STANDARD
- [ ] LIGHT/EXEMPT tasks skip checkpoint detection (no latency penalty)
- [ ] Detection notification format matches SPEC template

### Integration Tests (M4-INT)
```bash
# Run M4 integration tests
uv run pytest tests/accountability/ -m "m4_integration" -v
```

### Proceed to M5 When
- [ ] All checklist items verified
- [ ] No blocking issues identified
- [ ] M4 integration tests pass

---

## File Summary

| File | Purpose | Coverage Req |
|------|---------|--------------|
| `src/superclaude/accountability/checkpoints.py` | Checkpoint generation | 90% |
| `src/superclaude/accountability/metrics.py` | Token tracking | 90% |
| `src/superclaude/accountability/retention.py` | Memory retention | 90% |
| `src/superclaude/accountability/timeout.py` | Adaptive timeout | 90% |
| `src/superclaude/accountability/checkpoint_detection.py` | Checkpoint detection (FR-007) | 90% |
| `tests/accountability/test_checkpoints.py` | Checkpoint tests | - |
| `tests/accountability/test_metrics.py` | Metrics tests | - |
| `tests/accountability/test_retention.py` | Retention tests | - |
| `tests/accountability/test_timeout.py` | Timeout tests | - |
| `tests/accountability/test_checkpoint_detection.py` | Detection tests | - |
