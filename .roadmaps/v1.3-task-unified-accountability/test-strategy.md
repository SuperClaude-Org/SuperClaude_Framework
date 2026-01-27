# Test Strategy: v1.3-task-unified-accountability

## Test Environment
- **Location**: `tests/accountability/`
- **Fixtures**: `tests/fixtures/accountability/`
- **Mock services**: `tests/mocks/serena_mock.py`
- **Framework**: pytest with superclaude pytest plugin

## Test Constraints (Mandatory)
- NO writes outside `tests/` or `.dev/` directory during test runs
- NO external API calls to production Serena
- NO destructive operations on any data
- ALL tests must be idempotent (safe to re-run)

## Test Matrix

| Deliverable ID | Unit Tests | Integration | Acceptance | Regression |
|----------------|------------|-------------|------------|------------|
| REQ-001 | 5 tests | M2-INT-01 | ACC-001 | REG-TASK |
| REQ-002 | 8 tests | M2-INT-01 | ACC-002 | REG-TASK |
| REQ-003 | 6 tests | M2-INT-02 | ACC-003 | REG-TASK |
| REQ-004 | 10 tests | M3-INT-01 | ACC-004 | REG-STRICT |
| REQ-005 | 8 tests | M3-INT-02 | ACC-005 | REG-STRICT |
| REQ-006 | 6 tests | M4-INT-01 | ACC-006 | REG-TASK |
| REQ-007 | 4 tests | M2-INT-03 | ACC-007 | REG-TASK |
| REQ-008 | 5 tests | M1-INT-01 | ACC-008 | N/A |
| REQ-009 | 4 tests | M1-INT-01 | ACC-009 | N/A |
| REQ-010 | 4 tests | M1-INT-02 | ACC-010 | N/A |
| REQ-011 | 3 tests | M1-INT-02 | ACC-011 | N/A |
| REQ-012 | 7 tests | M2-INT-01 | ACC-012 | N/A |
| REQ-013 | 12 tests | M3-INT-01 | ACC-013 | REG-STRICT |
| REQ-014 | 5 tests | M3-INT-03 | ACC-014 | REG-STRICT |
| REQ-015 | 6 tests | M1-INT-03 | ACC-015 | REG-FALLBACK |
| IMP-001 | 3 tests | PERF-01 | ACC-016 | REG-PERF |
| IMP-002 | 4 tests | PERF-02 | ACC-017 | REG-PERF |
| IMP-003 | 3 tests | M4-INT-02 | ACC-018 | N/A |
| IMP-004 | 3 tests | PERF-02 | ACC-019 | REG-PERF |
| REF-001 | 8 tests | M2-INT-04 | ACC-020 | N/A |
| DOC-001 | 2 tests | DOC-INT-01 | ACC-021 | N/A |
| DOC-002 | 2 tests | DOC-INT-01 | ACC-022 | N/A |
| DOC-003 | 1 test | DOC-INT-02 | ACC-023 | N/A |
| DOC-004 | 1 test | DOC-INT-02 | ACC-024 | N/A |
| BUG-001 | Coverage validation | N/A | N/A | N/A |
| BUG-002 | Coverage validation | N/A | N/A | N/A |
| BUG-003 | Coverage validation | N/A | N/A | N/A |
| BUG-004 | N/A | All INT-* | N/A | N/A |
| BUG-005 | N/A | All PERF-* | N/A | N/A |

## Test Execution Order
1. **Unit tests** (fast, isolated) - ~2 minutes
2. **Integration tests** (milestone scope) - ~5 minutes
3. **Acceptance tests** (criteria verification) - ~3 minutes
4. **Regression tests** (full suite) - ~5 minutes
5. **Performance tests** (metrics validation) - ~3 minutes

## Coverage Targets
- **Unit**: 95% of new code (100% for state machine, circuit breaker)
- **Critical paths**: 100% coverage
- **Integration**: All milestone integration points
- **Performance**: All NFR metrics validated

---

## Unit Test Specifications

### test_worklog_schema.py (BUG-001)

```python
# Coverage: REQ-001, REQ-002, REQ-012
class TestWorklogSchema:
    def test_worklog_init_creates_valid_structure(): ...
    def test_session_id_format_valid(): ...
    def test_entry_timestamp_iso8601(): ...
    def test_entry_details_todowrite_discriminator(): ...
    def test_entry_details_edit_discriminator(): ...
    def test_entry_details_bash_discriminator(): ...
    def test_entry_details_verify_discriminator(): ...
    def test_entry_details_checkpoint_discriminator(): ...
    def test_entry_details_task_discriminator(): ...
    def test_summary_fields_complete(): ...
    def test_outcome_enum_values(): ...
    def test_tier_enum_values(): ...
    def test_status_enum_values(): ...
```

### test_verification.py (BUG-002)

```python
# Coverage: REQ-004, REQ-013
class TestVerificationStateMachine:
    # State transitions
    def test_todowrite_triggers_read(): ...
    def test_match_leads_to_pass(): ...
    def test_mismatch_leads_to_retry(): ...
    def test_timeout_leads_to_retry(): ...
    def test_retry_match_leads_to_pass(): ...
    def test_retry_mismatch_leads_to_escalate(): ...

    # State consistency checks
    def test_status_match_required(): ...
    def test_count_match_required(): ...
    def test_content_ignored(): ...
    def test_activeform_ignored(): ...

    # Edge cases
    def test_empty_todo_list(): ...
    def test_single_todo(): ...
```

### test_circuit_breaker.py (BUG-003)

```python
# Coverage: REQ-005
class TestCircuitBreaker:
    def test_initial_state_closed(): ...
    def test_failure_increments_counter(): ...
    def test_success_resets_counter(): ...
    def test_max_retries_opens_circuit(): ...
    def test_open_circuit_blocks_retries(): ...
    def test_cooldown_resets_circuit(): ...
    def test_user_accept_continues(): ...
    def test_user_abort_stops(): ...
```

### test_buffer.py

```python
# Coverage: REQ-003
class TestBatchBuffer:
    def test_append_adds_to_buffer(): ...
    def test_threshold_triggers_flush(): ...
    def test_time_triggers_flush(): ...
    def test_error_triggers_flush(): ...
    def test_completion_triggers_flush(): ...
    def test_flush_clears_buffer(): ...
```

### test_session.py

```python
# Coverage: REQ-010
class TestSessionId:
    def test_format_matches_spec(): ...
    def test_monotonic_counter_increments(): ...
    def test_uniqueness_same_second(): ...
    def test_uniqueness_across_seconds(): ...
```

### test_config.py

```python
# Coverage: REQ-008, REQ-009
class TestConfig:
    def test_tier_significance_strict(): ...
    def test_tier_significance_standard(): ...
    def test_tier_significance_light(): ...
    def test_tier_significance_exempt(): ...
    def test_config_defaults_valid(): ...
    def test_config_override_works(): ...
    def test_config_validation_rejects_invalid(): ...
```

### test_fallback.py

```python
# Coverage: REQ-015
class TestSerenaFallback:
    def test_timeout_triggers_fallback(): ...
    def test_error_triggers_fallback(): ...
    def test_fallback_stores_in_memory(): ...
    def test_user_notification_sent(): ...
    def test_retry_memory_flag_reconnects(): ...
    def test_tier_impact_strict_warning(): ...
```

### test_checkpoints.py

```python
# Coverage: REQ-006
class TestCheckpoints:
    def test_strict_generates_three(): ...
    def test_standard_generates_one(): ...
    def test_light_generates_zero(): ...
    def test_exempt_generates_zero(): ...
    def test_checkpoint_content_complete(): ...
    def test_deviation_detection(): ...
```

---

## Integration Test Specifications

### M1 Integration Tests

```python
# M1-INT-01: Config and Policy Integration
def test_config_loads_and_policy_applies():
    """Load config, verify tier significance policy works end-to-end"""

# M1-INT-02: Session and Memory Integration
def test_session_id_used_in_memory_paths():
    """Generate session ID, verify it appears in all memory namespace paths"""

# M1-INT-03: Fallback Integration
def test_serena_unavailable_activates_fallback():
    """Mock Serena timeout, verify fallback mode activates with notification"""
```

### M2 Integration Tests

```python
# M2-INT-01: Worklog Full Cycle
def test_worklog_init_log_finalize():
    """STANDARD task: init → 5 operations → finalize → verify worklog complete"""

# M2-INT-02: Batching Integration
def test_batch_buffer_reduces_mcp_calls():
    """Log 30 operations, verify only 3 MCP calls (batches of 10)"""

# M2-INT-03: Finalization Integration
def test_finalization_includes_summary():
    """Complete task, verify summary has correct counts"""

# M2-INT-04: Interface Contract
def test_worklog_service_implements_interface():
    """Verify WorklogService implements all interface methods"""
```

### M3 Integration Tests

```python
# M3-INT-01: Verification End-to-End
def test_strict_task_verification_pass():
    """STRICT task: TodoWrite → verification → pass"""

def test_strict_task_verification_retry():
    """STRICT task: TodoWrite → mismatch → retry → pass"""

# M3-INT-02: Circuit Breaker Integration
def test_circuit_breaker_escalates_to_user():
    """3 failures → user presented with options"""

# M3-INT-03: User Resolution Integration
def test_user_accept_continues_task():
    """User accepts → task continues → outcome logged"""

def test_user_abort_stops_task():
    """User aborts → task stops → outcome=aborted logged"""
```

### M4 Integration Tests

```python
# M4-INT-01: Checkpoint Integration
def test_strict_task_three_checkpoints():
    """STRICT task: planning → checkpoint, execution → checkpoint, verification → checkpoint"""

# M4-INT-02: Retention Integration
def test_cleanup_removes_old_worklogs():
    """Create old worklogs, run cleanup, verify archived/deleted"""
```

### Performance Tests (PERF)

```python
# PERF-01: Token Overhead
def test_strict_task_token_overhead():
    """STRICT task: measure total tokens ≤750 with batching"""

def test_weighted_average_overhead():
    """Run tier distribution (10% STRICT, 60% STANDARD, etc.), verify ≤300 avg"""

# PERF-02: Latency Budget
def test_aggregate_timeout_enforced():
    """Slow operations, verify 3000ms budget honored"""

def test_adaptive_timeout_skips_optional():
    """Slow previous phase, verify checkpoints skipped"""
```

### Documentation Tests (DOC-INT)

```python
# DOC-INT-01: SKILL.md Validation
def test_skill_md_section_6_exists():
    """Parse SKILL.md, verify Section 6 Accountability Framework exists"""

def test_skill_md_flags_documented():
    """Parse SKILL.md, verify all 5 new flags documented"""

# DOC-INT-02: Migration Guide Validation
def test_migration_guide_complete():
    """Parse migration guide, verify all sections present"""
```

---

## Acceptance Test Specifications

| ID | Deliverable | Acceptance Criteria | Test Method |
|----|-------------|---------------------|-------------|
| ACC-001 | REQ-001 | Worklog created within 500ms, ≤75 tokens | Timing + token count |
| ACC-002 | REQ-002 | Entry latency ≤200ms, ≤30 tokens | Timing + token count |
| ACC-003 | REQ-003 | MCP calls reduced ≥80% | MCP call counter |
| ACC-004 | REQ-004 | Verification completes within 1000ms | Timing |
| ACC-005 | REQ-005 | Circuit trips after 3 attempts | Attempt counter |
| ACC-006 | REQ-006 | STRICT=3, STANDARD=1, LIGHT/EXEMPT=0 checkpoints | Checkpoint counter |
| ACC-007 | REQ-007 | Summary includes all required fields | Schema validation |
| ACC-008 | REQ-008 | Policy returns correct boolean | Policy evaluation |
| ACC-009 | REQ-009 | Config validates against schema | Schema validation |
| ACC-010 | REQ-010 | Session ID matches format | Regex validation |
| ACC-011 | REQ-011 | Memory paths follow namespace | Path validation |
| ACC-012 | REQ-012 | Entry details match discriminator | Type validation |
| ACC-013 | REQ-013 | State machine transitions correctly | State assertions |
| ACC-014 | REQ-014 | User options displayed and actionable | UI interaction |
| ACC-015 | REQ-015 | Fallback activates on timeout | Timeout simulation |
| ACC-016 | IMP-001 | Total tokens ≤750 (STRICT w/ batching) | Token count |
| ACC-017 | IMP-002 | Aggregate timeout ≤3000ms | Timing |
| ACC-018 | IMP-003 | Cleanup removes >24h worklogs | Age verification |
| ACC-019 | IMP-004 | Optional ops skipped when budget tight | Skip assertion |
| ACC-020 | REF-001 | All interface methods implemented | Interface check |
| ACC-021 | DOC-001 | Section 6 present in SKILL.md | Doc parsing |
| ACC-022 | DOC-002 | All flags documented | Doc parsing |
| ACC-023 | DOC-003 | Migration guide complete | Doc parsing |
| ACC-024 | DOC-004 | Config options documented | Doc parsing |

---

## Regression Test Suite

| ID | Description | Scope | Frequency |
|----|-------------|-------|-----------|
| REG-TASK | Existing task execution unchanged | All tiers | Every commit |
| REG-STRICT | STRICT tier workflows work | STRICT | Every commit |
| REG-FALLBACK | Fallback behavior consistent | All tiers | Every commit |
| REG-PERF | Performance within bounds | All tiers | Daily |

### REG-TASK: Core Task Regression

```python
def test_standard_task_still_works():
    """Run existing STANDARD task, verify output unchanged"""

def test_light_task_still_works():
    """Run existing LIGHT task, verify output unchanged"""

def test_exempt_task_still_works():
    """Run existing EXEMPT task, verify no overhead"""

def test_existing_flags_still_work():
    """Run task with --skip-compliance, verify behavior"""
```

### REG-STRICT: STRICT Tier Regression

```python
def test_strict_task_completes_successfully():
    """Run full STRICT task, verify completion"""

def test_strict_verification_does_not_block():
    """Verification pass, task continues"""
```

### REG-FALLBACK: Fallback Regression

```python
def test_fallback_does_not_crash():
    """Simulate fallback, verify no crash"""

def test_fallback_notification_appears():
    """Fallback activates, notification shown"""
```

### REG-PERF: Performance Regression

```python
def test_token_overhead_stable():
    """Compare to baseline, verify no regression"""

def test_latency_stable():
    """Compare to baseline, verify no regression"""
```

---

## Test Fixtures

### `tests/fixtures/accountability/sample_worklog.json`
Sample complete worklog for schema validation

### `tests/fixtures/accountability/sample_config.yaml`
Sample configuration for config tests

### `tests/fixtures/accountability/mock_todo_states.py`
Mock todo states for verification tests

### `tests/fixtures/accountability/mock_serena_responses.py`
Mock Serena MCP responses for integration tests

---

## CI/CD Integration

```yaml
# .github/workflows/accountability-tests.yml
name: Accountability Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: uv run pytest tests/accountability/ -m unit --cov=superclaude.accountability --cov-fail-under=95

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - name: Run integration tests
        run: uv run pytest tests/accountability/ -m integration

  acceptance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - name: Run acceptance tests
        run: uv run pytest tests/accountability/ -m acceptance

  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - name: Run performance tests
        run: uv run pytest tests/accountability/ -m performance --benchmark-json=benchmark.json
```
