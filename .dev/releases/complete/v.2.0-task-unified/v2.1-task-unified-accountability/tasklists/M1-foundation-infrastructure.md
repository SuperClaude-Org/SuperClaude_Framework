# Tasklist: M1 - Foundation Infrastructure

## Metadata
- **Milestone**: M1
- **Dependencies**: None
- **Estimated Complexity**: Low
- **Primary Persona**: Backend
- **Files to Create**: 6 source files, 4 test files, 1 config file (T1.6 extends existing files)

---

## Tasks

### T1.1: Session ID Generation (REQ-010)
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `src/superclaude/accountability/session.py` (create)
- `tests/accountability/test_session.py` (create)

#### Steps
1. Create `src/superclaude/accountability/__init__.py` module initialization
2. Create `session.py` with `SessionIdGenerator` class
3. Implement format `YYYYMMDD_HHMMSS_NNN` with monotonic counter
4. Add thread-safe counter for same-second uniqueness
5. Write unit tests for format validation and uniqueness

#### Implementation Details
```python
# session.py skeleton
class SessionIdGenerator:
    _counter: int = 0
    _last_second: str = ""
    _lock: threading.Lock

    @classmethod
    def generate(cls) -> str:
        """Generate unique session ID in format YYYYMMDD_HHMMSS_NNN"""
        ...
```

#### Acceptance Criteria
- [ ] GIVEN a new task starts WHEN session ID generated THEN format matches `YYYYMMDD_HHMMSS_NNN`
- [ ] GIVEN two tasks in same second WHEN session IDs generated THEN counter increments (001, 002)
- [ ] GIVEN session ID generation WHEN called concurrently THEN all IDs unique

#### Verification
```bash
uv run pytest tests/accountability/test_session.py -v
```

---

### T1.2: Tier Significance Policy Configuration (REQ-008)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/config.py` (create)
- `config/accountability.yaml` (create)
- `tests/accountability/test_config.py` (create)

#### Steps
1. Create `config.py` with `TierSignificancePolicy` class
2. Define YAML schema for tier_significance_policy
3. Implement operation lookup by tier
4. Create `config/accountability.yaml` with defaults from SPEC-REVISED.md
5. Write unit tests for all tier/operation combinations

#### Implementation Details
```yaml
# accountability.yaml - tier_significance_policy section
tier_significance_policy:
  version: "1.0"
  included_operations:
    TodoWrite:
      tiers: [STRICT, STANDARD, LIGHT, EXEMPT]
    Edit:
      tiers: [STRICT, STANDARD]
    # ... per SPEC-REVISED.md Section 3.5
```

#### Acceptance Criteria
- [ ] GIVEN STRICT tier and Edit operation WHEN checked THEN returns True
- [ ] GIVEN LIGHT tier and Edit operation WHEN checked THEN returns False
- [ ] GIVEN TodoWrite operation WHEN checked for any tier THEN returns True
- [ ] GIVEN Bash with "pytest" WHEN checked for STRICT THEN returns True

#### Verification
```bash
uv run pytest tests/accountability/test_config.py::TestTierSignificancePolicy -v
```

---

### T1.3: Accountability Configuration Schema (REQ-009)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/config.py` (extend)
- `config/accountability.yaml` (extend)
- `tests/accountability/test_config.py` (extend)

#### Steps
1. Define `AccountabilityConfig` dataclass with all settings
2. Add YAML parsing with validation
3. Implement default values from SPEC-REVISED.md Section 3.5
4. Add schema validation for invalid configurations
5. Write unit tests for config loading and validation

#### Implementation Details
```python
# config.py - AccountabilityConfig
@dataclass
class AccountabilityConfig:
    worklog_buffer_size: int = 10
    worklog_buffer_time_seconds: int = 30
    worklog_init_timeout_ms: int = 500
    verification_enabled_tiers: list[str] = field(default_factory=lambda: ["STRICT"])
    verification_max_retries: int = 1
    verification_timeout_ms: int = 1000
    checkpoint_strict: list[str] = field(default_factory=lambda: [...])
    aggregate_timeout_ms: int = 3000
    # ... all fields from SPEC-REVISED.md
```

#### Acceptance Criteria
- [ ] GIVEN config file WHEN loaded THEN all values match spec defaults
- [ ] GIVEN invalid config (negative timeout) WHEN loaded THEN validation error raised
- [ ] GIVEN missing optional field WHEN loaded THEN default used

#### Verification
```bash
uv run pytest tests/accountability/test_config.py::TestAccountabilityConfig -v
```

---

### T1.4: Memory Naming Convention (REQ-011)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/memory.py` (create)
- `tests/accountability/test_memory.py` (create)

#### Steps
1. Create `memory.py` with `MemoryNamespace` class
2. Implement path generation for all namespace patterns
3. Add session ID integration from REQ-010
4. Write unit tests for all namespace patterns

#### Implementation Details
```python
# memory.py
class MemoryNamespace:
    WORKLOG = "_worklog/{session_id}"
    WORKLOG_SUMMARY = "_worklog_summary/{date}"
    PROGRESS = "_progress/{task_hash}"
    CHECKPOINT = "_checkpoint/{session_id}/{n}"

    @staticmethod
    def worklog_path(session_id: str) -> str: ...
    @staticmethod
    def checkpoint_path(session_id: str, n: int) -> str: ...
```

#### Acceptance Criteria
- [ ] GIVEN session_id "20260126_143215_001" WHEN worklog_path called THEN returns "_worklog/20260126_143215_001"
- [ ] GIVEN session_id and n=2 WHEN checkpoint_path called THEN returns "_checkpoint/20260126_143215_001/2"
- [ ] GIVEN date "2026-01-26" WHEN summary_path called THEN returns "_worklog_summary/2026-01-26"

#### Verification
```bash
uv run pytest tests/accountability/test_memory.py -v
```

---

### T1.5: Serena Fallback Mode (REQ-015)
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/fallback.py` (create)
- `tests/accountability/test_fallback.py` (create)

#### Steps
1. Create `fallback.py` with `SerenaFallbackManager` class
2. Implement timeout detection (>5s)
3. Create in-memory session-scoped storage fallback
4. Add mandatory user notification on fallback activation
5. Implement `--retry-memory` flag handling
6. Write unit tests with mock timeouts

#### Implementation Details
```python
# fallback.py
class SerenaFallbackManager:
    fallback_active: bool = False
    session_storage: dict[str, Any] = {}

    def detect_unavailability(self, timeout_ms: int = 5000) -> bool: ...
    def activate_fallback(self) -> str:  # Returns notification message
        """Returns mandatory user notification"""
        return """⚠️ Memory system unavailable. Continuing with session-only logging.
Audit trail will not persist beyond this session.
To retry with full logging, use: /sc:task --retry-memory"""
    def store(self, key: str, value: Any) -> None: ...
    def retrieve(self, key: str) -> Any | None: ...
```

#### Acceptance Criteria
- [ ] GIVEN Serena timeout >5s WHEN worklog operation attempted THEN fallback activates
- [ ] GIVEN fallback active WHEN store called THEN data saved to in-memory dict
- [ ] GIVEN fallback activated WHEN notification checked THEN user message displayed
- [ ] GIVEN STRICT tier with fallback WHEN warned THEN compliance warning included
- [ ] GIVEN --retry-memory flag WHEN connection restored THEN fallback deactivates

#### Verification
```bash
uv run pytest tests/accountability/test_fallback.py -v
```

---

### T1.6: Session ID MCP Independence Confirmation (NFR-005)
**Type**: VERIFICATION
**Priority**: P1-High
**Files Affected**:
- `src/superclaude/accountability/session.py` (extend docstring)
- `tests/accountability/test_session.py` (extend with MCP-independence tests)

#### Steps
1. Add docstring to `SessionIdGenerator` stating: "Session ID generation is MCP-independent and will succeed even if Serena is unavailable."
2. Add unit test: `test_session_id_without_mcp()` that mocks Serena unavailable and verifies ID generation succeeds
3. Add unit test: `test_session_id_no_mcp_call()` that verifies no MCP imports or calls in session.py
4. Add unit test: `test_counter_overflow_waits()` that verifies waiting behavior at 999 overflow
5. Update any documentation referencing session ID to note MCP independence

#### Implementation Details
```python
# test_session.py - Additional tests for NFR-005
import ast
import inspect

def test_session_id_without_mcp(monkeypatch):
    """Verify session ID generation succeeds when Serena MCP is unavailable."""
    # Mock any potential MCP-like calls to raise
    # Session ID should still generate successfully
    from superclaude.accountability.session import SessionIdGenerator
    session_id = SessionIdGenerator.generate()
    assert session_id is not None
    assert len(session_id) == 19  # YYYYMMDD_HHMMSS_NNN

def test_session_id_no_mcp_call():
    """Verify session.py contains no MCP-related imports or calls."""
    import superclaude.accountability.session as session_module
    source = inspect.getsource(session_module)
    tree = ast.parse(source)

    # Check for forbidden imports
    forbidden_patterns = ['mcp', 'serena', 'memory_service', 'write_memory', 'read_memory']
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not any(p in alias.name.lower() for p in forbidden_patterns), \
                    f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert not any(p in node.module.lower() for p in forbidden_patterns), \
                    f"Forbidden import found: {node.module}"

def test_counter_overflow_waits():
    """Verify counter overflow (>999 same second) waits for next second."""
    import time
    from superclaude.accountability.session import SessionIdGenerator

    # Force counter to 999
    SessionIdGenerator._counter = 999
    SessionIdGenerator._last_second = time.strftime("%Y%m%d_%H%M%S")

    start = time.time()
    session_id = SessionIdGenerator.generate()
    elapsed = time.time() - start

    # Should have waited for next second
    assert elapsed >= 0.9 or SessionIdGenerator._counter == 0
    assert session_id.endswith("_000")
```

#### Acceptance Criteria
- [ ] GIVEN Serena MCP unavailable (simulated timeout) WHEN session ID generated THEN generation succeeds
- [ ] GIVEN session.py source code WHEN analyzed THEN no MCP-related imports present
- [ ] GIVEN 1000 concurrent ID generations in same second WHEN overflow occurs THEN wait and reset counter to 000
- [ ] SessionIdGenerator docstring explicitly mentions MCP independence guarantee

#### Verification
```bash
uv run pytest tests/accountability/test_session.py::test_session_id_without_mcp tests/accountability/test_session.py::test_session_id_no_mcp_call tests/accountability/test_session.py::test_counter_overflow_waits -v
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 6 deliverables code-complete (including T1.6 verification)
- [ ] All unit tests passing: `uv run pytest tests/accountability/test_session.py tests/accountability/test_config.py tests/accountability/test_memory.py tests/accountability/test_fallback.py -v`
- [ ] Coverage ≥90% for new code
- [ ] Session ID uniqueness verified across concurrent calls
- [ ] Config schema validates correctly
- [ ] Fallback mode triggers correctly on Serena timeout
- [ ] Session ID MCP independence verified (no MCP imports in session.py)
- [ ] Counter overflow handling tested (waits for next second at 999)
- [ ] No linting errors: `uv run ruff check src/superclaude/accountability/`

### Integration Test (M1-INT)
```bash
# Run M1 integration tests
uv run pytest tests/accountability/ -m "m1_integration" -v
```

### Proceed to M2 When
- [ ] All checklist items verified
- [ ] No blocking issues identified
- [ ] Integration tests pass

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `src/superclaude/accountability/__init__.py` | Module init | Create |
| `src/superclaude/accountability/session.py` | Session ID generation | Create |
| `src/superclaude/accountability/config.py` | Config and tier policy | Create |
| `src/superclaude/accountability/memory.py` | Memory namespace | Create |
| `src/superclaude/accountability/fallback.py` | Serena fallback | Create |
| `config/accountability.yaml` | Configuration file | Create |
| `tests/accountability/__init__.py` | Test module init | Create |
| `tests/accountability/test_session.py` | Session tests | Create |
| `tests/accountability/test_config.py` | Config tests | Create |
| `tests/accountability/test_memory.py` | Memory tests | Create |
| `tests/accountability/test_fallback.py` | Fallback tests | Create |
