# Tasklist: M5 - Testing & Quality

## Metadata
- **Milestone**: M5
- **Dependencies**: M3 (Verification System), M4 (Checkpoint & Optimization)
- **Estimated Complexity**: Medium
- **Primary Persona**: QA, Testing
- **Files to Create**: 5 test files, 4 fixture files

---

## Tasks

### T5.1: Unit Tests for Worklog Schema Validation (BUG-001)
**Type**: BUGFIX
**Priority**: P1-High
**Files Affected**:
- `tests/accountability/test_worklog_schema.py` (create)
- `tests/fixtures/accountability/sample_worklog.json` (create)

#### Steps
1. Create comprehensive schema validation tests
2. Test all entry detail discriminated unions
3. Test all enum values (tier, status, outcome)
4. Test required fields and optional fields
5. Test malformed data rejection
6. Ensure 100% coverage of schema.py

#### Test Cases
```python
# test_worklog_schema.py
class TestWorklogSchema:
    """100% coverage for worklog schema validation"""

    # Structure tests
    def test_worklog_init_creates_valid_structure(self): ...
    def test_worklog_requires_session_id(self): ...
    def test_worklog_requires_tier(self): ...
    def test_worklog_started_at_iso8601(self): ...
    def test_worklog_completed_at_optional(self): ...

    # Session ID tests
    def test_session_id_format_valid(self): ...
    def test_session_id_format_invalid_rejected(self): ...

    # Entry tests
    def test_entry_timestamp_iso8601(self): ...
    def test_entry_action_enum_valid(self): ...
    def test_entry_status_enum_valid(self): ...

    # Discriminated union tests
    def test_entry_details_todowrite_discriminator(self): ...
    def test_entry_details_edit_discriminator(self): ...
    def test_entry_details_bash_discriminator(self): ...
    def test_entry_details_verify_discriminator(self): ...
    def test_entry_details_checkpoint_discriminator(self): ...
    def test_entry_details_task_discriminator(self): ...
    def test_entry_details_wrong_discriminator_rejected(self): ...

    # Summary tests
    def test_summary_fields_complete(self): ...
    def test_summary_verification_results_structure(self): ...

    # Enum tests
    def test_outcome_enum_values(self): ...
    def test_tier_enum_values(self): ...
    def test_status_enum_values(self): ...
    def test_invalid_enum_rejected(self): ...

    # Edge cases
    def test_empty_entries_valid(self): ...
    def test_large_entry_list_valid(self): ...
    def test_unicode_in_context(self): ...
    def test_null_optional_fields(self): ...
```

#### Acceptance Criteria
- [ ] 100% test coverage for `src/superclaude/accountability/schema.py`
- [ ] All enum values tested for validity
- [ ] All discriminated unions tested
- [ ] Malformed data properly rejected
- [ ] Edge cases covered (empty lists, unicode, null optionals)

#### Verification
```bash
uv run pytest tests/accountability/test_worklog_schema.py -v --cov=superclaude.accountability.schema --cov-fail-under=100
```

---

### T5.2: Unit Tests for Verification State Machine (BUG-002)
**Type**: BUGFIX
**Priority**: P1-High
**Files Affected**:
- `tests/accountability/test_verification.py` (extend)
- `tests/fixtures/accountability/mock_todo_states.py` (create)

#### Steps
1. Test all state transitions per SPEC-REVISED.md diagram
2. Test timeout handling
3. Test retry logic
4. Test escalation trigger
5. Ensure 100% coverage of verification.py state machine

#### Test Cases
```python
# test_verification.py (extend)
class TestVerificationStateMachine:
    """100% coverage for verification state machine"""

    # State transitions
    def test_todowrite_triggers_read(self): ...
    def test_match_leads_to_pass(self): ...
    def test_mismatch_leads_to_retry(self): ...
    def test_timeout_leads_to_retry(self): ...
    def test_retry_match_leads_to_pass(self): ...
    def test_retry_mismatch_leads_to_escalate(self): ...

    # State consistency checks
    def test_status_match_required(self): ...
    def test_count_match_required(self): ...
    def test_content_ignored(self): ...
    def test_activeform_ignored(self): ...

    # Retry logic
    def test_retry_delay_100ms(self): ...
    def test_max_automatic_retries_one(self): ...
    def test_retry_count_increments(self): ...

    # Timeout handling
    def test_timeout_1000ms(self): ...
    def test_timeout_handled_as_mismatch(self): ...

    # Edge cases
    def test_empty_todo_list(self): ...
    def test_single_todo(self): ...
    def test_many_todos(self): ...
    def test_concurrent_verification(self): ...

    # Worklog integration
    def test_pass_logged_to_worklog(self): ...
    def test_fail_logged_to_worklog(self): ...
    def test_retry_logged_to_worklog(self): ...
```

#### Acceptance Criteria
- [ ] 100% test coverage for verification state machine
- [ ] All state transitions tested
- [ ] Retry logic verified (1 auto retry, 100ms delay)
- [ ] Timeout handling verified (1000ms)
- [ ] Worklog entries created for all outcomes

#### Verification
```bash
uv run pytest tests/accountability/test_verification.py -v --cov=superclaude.accountability.verification --cov-fail-under=100
```

---

### T5.3: Unit Tests for Circuit Breaker Logic (BUG-003)
**Type**: BUGFIX
**Priority**: P1-High
**Files Affected**:
- `tests/accountability/test_circuit_breaker.py` (extend)

#### Steps
1. Test all circuit states (CLOSED, OPEN)
2. Test state transitions
3. Test cooldown behavior
4. Test user resolution handling
5. Ensure 100% coverage of circuit_breaker.py

#### Test Cases
```python
# test_circuit_breaker.py (extend)
class TestCircuitBreaker:
    """100% coverage for circuit breaker logic"""

    # Initial state
    def test_initial_state_closed(self): ...

    # Counter behavior
    def test_failure_increments_counter(self): ...
    def test_success_resets_counter(self): ...
    def test_counter_persists_across_operations(self): ...

    # State transitions
    def test_max_retries_opens_circuit(self): ...
    def test_open_circuit_blocks_retries(self): ...
    def test_three_total_attempts_max(self): ...

    # Cooldown
    def test_cooldown_300_seconds(self): ...
    def test_cooldown_resets_circuit(self): ...
    def test_partial_cooldown_stays_open(self): ...

    # User resolution
    def test_user_accept_continues(self): ...
    def test_user_abort_stops(self): ...
    def test_user_continue_with_risk(self): ...
    def test_user_resolution_logged(self): ...

    # Edge cases
    def test_rapid_failures(self): ...
    def test_interleaved_success_failure(self): ...
    def test_reset_after_user_accept(self): ...
```

#### Acceptance Criteria
- [ ] 100% test coverage for `src/superclaude/accountability/circuit_breaker.py`
- [ ] All state transitions tested
- [ ] 3 total attempts max verified
- [ ] 300s cooldown verified
- [ ] User resolution options all tested

#### Verification
```bash
uv run pytest tests/accountability/test_circuit_breaker.py -v --cov=superclaude.accountability.circuit_breaker --cov-fail-under=100
```

---

### T5.4: Integration Tests for E2E Scenarios (BUG-004)
**Type**: BUGFIX
**Priority**: P1-High
**Files Affected**:
- `tests/accountability/test_e2e.py` (create)
- `tests/fixtures/accountability/mock_serena_responses.py` (create)

#### Steps
1. Create E2E test for STRICT task (full accountability)
2. Create E2E test for STANDARD task (worklog + 1 checkpoint)
3. Create E2E test for failure scenarios
4. Create E2E test for flag overrides
5. Create E2E test for Serena fallback

#### Test Cases
```python
# test_e2e.py
class TestE2EScenarios:
    """End-to-end integration tests"""

    # STRICT tier E2E
    def test_strict_task_full_accountability(self):
        """
        STRICT task: init → ops → verification × N → checkpoints × 3 → finalize
        Verify: worklog complete, 3 verifications, 3 checkpoints
        """

    def test_strict_task_verification_failure_recovery(self):
        """Simulate verification failure, retry, success"""

    def test_strict_task_circuit_breaker_trip(self):
        """Simulate 3 verification failures, user resolution"""

    # STANDARD tier E2E
    def test_standard_task_worklog_and_checkpoint(self):
        """
        STANDARD task: init → ops → 1 checkpoint → finalize
        Verify: worklog complete, 1 checkpoint
        """

    # LIGHT tier E2E
    def test_light_task_minimal_overhead(self):
        """
        LIGHT task: init → todowrite only → finalize
        Verify: minimal worklog, no checkpoint
        """

    # EXEMPT tier E2E
    def test_exempt_task_zero_overhead(self):
        """
        EXEMPT task: no worklog created
        Verify: zero accountability overhead
        """

    # Failure scenarios
    def test_task_failure_worklog_preserved(self):
        """Task fails, worklog has outcome=failure"""

    def test_task_abort_worklog_preserved(self):
        """User aborts, worklog has outcome=aborted"""

    def test_error_triggers_emergency_flush(self):
        """Bash fails, buffer flushed immediately"""

    # Flag override scenarios
    def test_no_worklog_flag(self):
        """--no-worklog disables all worklog"""

    def test_skip_verify_flag(self):
        """--skip-verify disables STRICT verification"""

    def test_no_checkpoints_flag(self):
        """--no-checkpoints disables checkpoint generation"""

    # Fallback scenarios
    def test_serena_unavailable_fallback(self):
        """Serena timeout → session-only logging with notification"""

    def test_retry_memory_reconnects(self):
        """--retry-memory restores Serena connection"""
```

#### Acceptance Criteria
- [ ] STRICT E2E: worklog + 3 verifications + 3 checkpoints
- [ ] STANDARD E2E: worklog + 1 checkpoint
- [ ] LIGHT E2E: minimal worklog, 0 checkpoints
- [ ] EXEMPT E2E: 0 overhead
- [ ] All failure scenarios preserve audit trail
- [ ] All flag overrides work correctly
- [ ] Fallback scenario works with notification

#### Verification
```bash
uv run pytest tests/accountability/test_e2e.py -v
```

---

### T5.5: Performance Tests (BUG-005)
**Type**: BUGFIX
**Priority**: P2-Medium
**Files Affected**:
- `tests/accountability/test_performance.py` (create)

#### Steps
1. Create token overhead measurement tests
2. Create latency measurement tests
3. Create memory growth tests
4. Add pytest-benchmark integration
5. Create baseline comparison tests

#### Test Cases
```python
# test_performance.py
import pytest

class TestPerformance:
    """Performance validation tests"""

    # Token overhead tests
    @pytest.mark.benchmark
    def test_strict_task_token_overhead(self, benchmark):
        """STRICT task total tokens ≤750 with batching"""
        result = benchmark(run_strict_task_with_accountability)
        assert result.total_tokens <= 750

    @pytest.mark.benchmark
    def test_standard_task_token_overhead(self, benchmark):
        """STANDARD task total tokens ≤300"""
        result = benchmark(run_standard_task_with_accountability)
        assert result.total_tokens <= 300

    @pytest.mark.benchmark
    def test_light_task_token_overhead(self, benchmark):
        """LIGHT task total tokens ≤60"""
        result = benchmark(run_light_task_with_accountability)
        assert result.total_tokens <= 60

    def test_weighted_average_overhead(self):
        """
        Weighted average ≤300 tokens
        Distribution: 10% STRICT, 60% STANDARD, 25% LIGHT, 5% EXEMPT
        """
        # Run representative task mix
        avg = calculate_weighted_average_overhead()
        assert avg <= 300

    # Latency tests
    @pytest.mark.benchmark
    def test_worklog_init_latency(self, benchmark):
        """Initialization ≤500ms"""
        result = benchmark(worklog_init)
        assert result.time_ms <= 500

    @pytest.mark.benchmark
    def test_entry_append_latency(self, benchmark):
        """Entry append ≤200ms"""
        result = benchmark(worklog_append)
        assert result.time_ms <= 200

    @pytest.mark.benchmark
    def test_verification_latency(self, benchmark):
        """Verification cycle ≤1000ms"""
        result = benchmark(run_verification)
        assert result.time_ms <= 1000

    @pytest.mark.benchmark
    def test_checkpoint_latency(self, benchmark):
        """Checkpoint generation ≤2000ms"""
        result = benchmark(generate_checkpoint)
        assert result.time_ms <= 2000

    def test_aggregate_timeout_enforced(self):
        """Total accountability phase ≤3000ms"""
        start = time.time()
        run_full_accountability_phase()
        elapsed = (time.time() - start) * 1000
        assert elapsed <= 3000

    # Memory tests
    def test_memory_growth_per_session(self):
        """Memory growth ≤50KB per session"""
        before = get_memory_usage()
        run_typical_session()
        after = get_memory_usage()
        assert (after - before) <= 50 * 1024  # 50KB

    def test_memory_stable_after_cleanup(self):
        """Memory returns to baseline after cleanup"""
        baseline = get_memory_usage()
        for _ in range(10):
            run_typical_session()
            run_cleanup()
        current = get_memory_usage()
        assert current <= baseline * 1.1  # 10% tolerance
```

#### Acceptance Criteria
- [ ] STRICT token overhead ≤750 with batching
- [ ] STANDARD token overhead ≤300
- [ ] LIGHT token overhead ≤60
- [ ] Weighted average ≤300 tokens
- [ ] All latency targets met (init ≤500ms, append ≤200ms, etc.)
- [ ] Aggregate timeout ≤3000ms
- [ ] Memory growth ≤50KB per session

#### Verification
```bash
uv run pytest tests/accountability/test_performance.py -v --benchmark-json=benchmark.json
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 5 deliverables code-complete
- [ ] Unit tests passing with required coverage:
  ```bash
  uv run pytest tests/accountability/ --cov=superclaude.accountability --cov-fail-under=95
  ```
- [ ] Critical path 100% coverage:
  ```bash
  uv run pytest tests/accountability/test_worklog_schema.py tests/accountability/test_verification.py tests/accountability/test_circuit_breaker.py -v --cov --cov-fail-under=100
  ```
- [ ] All E2E scenarios pass
- [ ] Performance tests validate all metrics
- [ ] No regressions in existing tests

### Full Test Suite Run
```bash
# Complete test suite
uv run pytest tests/accountability/ -v --cov=superclaude.accountability --cov-report=html

# Performance tests with benchmarks
uv run pytest tests/accountability/test_performance.py -v --benchmark-json=benchmark.json
```

### Proceed to M6 When
- [ ] All checklist items verified
- [ ] ≥95% overall coverage
- [ ] 100% coverage on critical paths
- [ ] All performance metrics within bounds
- [ ] M5 integration tests pass

---

## File Summary

| File | Purpose | Coverage Req |
|------|---------|--------------|
| `tests/accountability/test_worklog_schema.py` | Schema validation | 100% (target) |
| `tests/accountability/test_verification.py` | State machine tests | 100% (target) |
| `tests/accountability/test_circuit_breaker.py` | Circuit breaker tests | 100% (target) |
| `tests/accountability/test_e2e.py` | E2E integration | - |
| `tests/accountability/test_performance.py` | Performance validation | - |
| `tests/fixtures/accountability/sample_worklog.json` | Test fixture | - |
| `tests/fixtures/accountability/mock_todo_states.py` | Mock data | - |
| `tests/fixtures/accountability/mock_serena_responses.py` | Mock responses | - |
