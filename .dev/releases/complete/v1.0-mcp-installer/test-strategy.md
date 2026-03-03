# Test Strategy: v1.0-mcp-installer

**Source Roadmap**: `.roadmaps/v1.0-mcp-installer/roadmap.md`
**Generated**: 2026-01-21T12:00:00Z
**Generator Version**: v2.1

---

## Test Environment

- **Location**: `tests/mcp/`
- **Fixtures**: `tests/fixtures/mcp/`
- **Mock Services**: `tests/mocks/mcp/`
- **Test Framework**: pytest with superclaude pytest plugin

### Directory Structure

```
tests/
├── mcp/
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_servers.py
│   │   ├── test_schema.py
│   │   ├── test_exceptions.py
│   │   └── test_health.py
│   ├── integration/
│   │   ├── test_installation_flow.py
│   │   ├── test_concurrent_access.py
│   │   └── test_cross_platform.py
│   ├── acceptance/
│   │   ├── test_npm_servers.py
│   │   ├── test_uvx_servers.py
│   │   ├── test_sse_servers.py
│   │   └── test_api_keys.py
│   └── regression/
│       ├── test_no_cli_calls.py
│       └── test_variadic_env_bug.py
├── fixtures/
│   └── mcp/
│       ├── empty_config.json
│       ├── single_server.json
│       ├── multiple_servers.json
│       ├── malformed_config.json
│       └── large_config.json
└── mocks/
    └── mcp/
        ├── mock_filesystem.py
        └── mock_sse_server.py
```

---

## Test Matrix

| Deliverable ID | Unit Tests | Integration | Acceptance | Regression |
|----------------|------------|-------------|------------|------------|
| REQ-001 | 3 tests | M1-INT-01 | ACC-PATH | - |
| REQ-002 | 4 tests | M1-INT-02 | ACC-CREATE | - |
| REQ-003 | 3 tests | M2-INT-01 | ACC-PRESERVE | - |
| REQ-004 | 5 tests | M2-INT-02 | ACC-ATOMIC | - |
| REQ-005 | 4 tests | M3-INT-01 | ACC-NPM | REG-001 |
| REQ-006 | 4 tests | M3-INT-02 | ACC-UVX | REG-001 |
| REQ-007 | 3 tests | M3-INT-03 | ACC-SSE | REG-001 |
| REQ-008 | 4 tests | M3-INT-04 | ACC-APIKEY | REG-002 |
| REQ-009 | 3 tests | M3-INT-05 | ACC-IDEMPOTENT | - |
| REQ-010 | 3 tests | M4-INT-01 | ACC-UNINSTALL | - |
| REQ-011 | 2 tests | M4-INT-01 | ACC-GRACEFUL | - |
| REQ-012 | 3 tests | M1-INT-03 | ACC-STATUS | - |
| REQ-013 | 3 tests | M4-INT-02 | ACC-HEALTH | - |
| REQ-014 | 2 tests | M1-INT-01 | ACC-API-PATH | - |
| REQ-015 | 4 tests | M1-INT-02 | ACC-API-LOAD | - |
| REQ-016 | 4 tests | M2-INT-02 | ACC-API-SAVE | - |
| REQ-017 | 4 tests | M5-INT-01 | ACC-API-REG | - |
| REQ-018 | 3 tests | M4-INT-01 | ACC-API-UNREG | - |
| REQ-019 | 2 tests | M5-INT-01 | ACC-API-CHECK | - |
| REQ-020 | 5 tests | M5-INT-02 | ACC-SCHEMA | - |
| REQ-021 | 8 tests | M5-INT-03 | ACC-ERRORS | - |
| IMP-001 | 1 test | M5-INT-04 | ACC-PERF-INST | - |
| IMP-002 | 2 tests | M2-INT-03 | ACC-PERF-IO | - |
| IMP-003 | 3 tests | M2-INT-02 | ACC-RECOVERY | - |
| IMP-004 | 4 tests | M2-INT-04 | ACC-CONCURRENT | - |
| IMP-005 | 3 tests | M3-INT-04 | ACC-MASK | REG-002 |
| IMP-006 | 2 tests | M1-INT-02 | ACC-PERMS | - |
| REF-001 | 1 test | - | - | REG-001 |
| REF-002 | 2 tests | M4-INT-03 | ACC-UNIFIED | - |
| DOC-001 | - | - | ACC-DOCS | - |
| DOC-002 | - | - | ACC-MIGRATE | - |
| DOC-003 | - | - | ACC-TROUBLE | - |

---

## Test Specifications by Category

### Unit Tests

#### test_config.py (25 tests)

```python
class TestGetConfigFilePath:
    def test_returns_path_object(self):
        """get_config_file_path() returns pathlib.Path"""

    def test_linux_path(self, monkeypatch):
        """On Linux, returns $HOME/.claude/mcp.json"""

    def test_windows_path(self, monkeypatch):
        """On Windows, returns %USERPROFILE%\\.claude\\mcp.json"""

class TestLoadConfig:
    def test_nonexistent_returns_empty(self, tmp_path):
        """Loading non-existent file returns {"mcpServers": {}}"""

    def test_valid_json_loaded(self, tmp_path):
        """Valid JSON file loaded correctly"""

    def test_malformed_json_raises_error(self, tmp_path):
        """Malformed JSON raises MCPConfigError with E002"""

    def test_permission_denied_raises_error(self, tmp_path):
        """Unreadable file raises PermissionError with E003"""

class TestSaveConfig:
    def test_creates_directory_if_missing(self, tmp_path):
        """~/.claude/ created if doesn't exist"""

    def test_atomic_write_uses_temp_file(self, tmp_path, mocker):
        """Write uses temp file + rename pattern"""

    def test_failure_preserves_original(self, tmp_path, mocker):
        """On write failure, original file unchanged"""

    def test_file_permissions_0600(self, tmp_path):
        """Created file has mode 0600"""

class TestConfigPreservation:
    def test_adding_server_preserves_existing(self, tmp_path):
        """Adding new server doesn't modify existing entries"""

    def test_modification_timestamp_unchanged_on_no_op(self, tmp_path):
        """Re-registering same config doesn't touch file"""
```

#### test_servers.py (18 tests)

```python
class TestNpmServerInstallation:
    def test_context7_config_format(self):
        """context7 produces correct command/args structure"""

    def test_morphllm_with_api_key(self):
        """morphllm-fast-apply includes env with API key"""

    def test_playwright_latest_version(self):
        """playwright uses @latest tag correctly"""

class TestUvxServerInstallation:
    def test_serena_command_parsing(self):
        """serena uvx command parsed into correct args array"""

    def test_github_url_handling(self):
        """git+https:// URLs handled correctly"""

class TestSseServerInstallation:
    def test_airis_gateway_url_field(self):
        """airis-gateway uses url field not command"""

    def test_description_included(self):
        """SSE servers can include description field"""

class TestIdempotency:
    def test_reinstall_no_op(self):
        """Installing existing server returns success without changes"""

    def test_config_unchanged_on_reinstall(self):
        """Config file not modified on reinstall"""
```

#### test_exceptions.py (8 tests)

```python
class TestErrorCodes:
    def test_e001_config_not_found(self):
    def test_e002_config_malformed(self):
    def test_e003_config_permission(self):
    def test_e004_server_exists(self):
    def test_e005_server_not_found(self):
    def test_e006_lock_timeout(self):
    def test_e007_write_failed(self):
    def test_e008_validation_failed(self):
```

### Integration Tests

#### test_installation_flow.py

```python
class TestEndToEndInstallation:
    @pytest.fixture
    def clean_config(self, tmp_path, monkeypatch):
        """Provide clean config environment"""
        config_dir = tmp_path / ".claude"
        monkeypatch.setenv("HOME", str(tmp_path))
        return config_dir

    def test_fresh_system_installation(self, clean_config):
        """
        M1-INT-01: Fresh system installation
        Given: No ~/.claude/ exists
        When: Install context7
        Then: Directory created, config valid, server registered
        """

    def test_sequential_multi_server(self, clean_config):
        """
        M3-INT-01: Sequential multi-server installation
        Given: Empty config
        When: Install context7, then serena, then playwright
        Then: All three servers correctly configured
        """

class TestConcurrentAccess:
    def test_parallel_install_safety(self, clean_config):
        """
        M2-INT-04: Concurrent installation safety
        Given: Empty config
        When: Two threads install different servers simultaneously
        Then: Both servers configured, no corruption
        """

    def test_lock_timeout_handling(self, clean_config, mocker):
        """
        M2-INT-04: Lock timeout
        Given: Config locked by another process
        When: Installation attempted
        Then: Timeout after 30s with E006 error
        """
```

### Acceptance Tests

#### test_npm_servers.py

```python
class TestNpmServerAcceptance:
    def test_context7_installation(self):
        """
        ACC-NPM-001
        GIVEN fresh config
        WHEN install("context7")
        THEN config contains:
          {"mcpServers": {"context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]}}}
        """

    def test_morphllm_with_env(self, monkeypatch):
        """
        ACC-APIKEY-001
        GIVEN MORPH_API_KEY=sk-test-123 in environment
        WHEN install("morphllm-fast-apply")
        THEN config.mcpServers["morphllm-fast-apply"]["env"]["MORPH_API_KEY"] == "sk-test-123"
        """
```

### Regression Tests

#### test_no_cli_calls.py

```python
class TestNoCLICalls:
    def test_no_claude_mcp_add_in_codebase(self):
        """
        REG-001: No CLI subprocess calls
        GIVEN the codebase
        WHEN grepping for 'claude mcp add'
        THEN no matches in Python source files (excluding tests/docs)
        """
        import subprocess
        result = subprocess.run(
            ["grep", "-r", "claude mcp add", "src/"],
            capture_output=True, text=True
        )
        assert result.returncode == 1  # No matches

    def test_no_subprocess_for_registration(self):
        """
        REG-001: No subprocess for server registration
        GIVEN register_server() function
        WHEN inspecting implementation
        THEN no subprocess.run calls
        """
```

#### test_variadic_env_bug.py

```python
class TestVariadicEnvBugPrevented:
    def test_server_name_not_parsed_as_env(self):
        """
        REG-002: Server name with dashes not misinterpreted
        GIVEN server name "morphllm-fast-apply"
        WHEN registering with API key
        THEN server name is config key, not treated as env var
        """

    def test_api_key_isolated_in_env_object(self):
        """
        REG-002: API key properly isolated
        GIVEN API key MORPH_API_KEY=test
        WHEN registering morphllm-fast-apply
        THEN key only appears in env object, not elsewhere
        """
```

---

## Test Execution Order

1. **Unit tests** (fast, isolated) - ~30 seconds
   ```bash
   uv run pytest tests/mcp/unit/ -v
   ```

2. **Integration tests** (milestone scope) - ~2 minutes
   ```bash
   uv run pytest tests/mcp/integration/ -v
   ```

3. **Acceptance tests** (criteria verification) - ~1 minute
   ```bash
   uv run pytest tests/mcp/acceptance/ -v
   ```

4. **Regression tests** (critical guards) - ~30 seconds
   ```bash
   uv run pytest tests/mcp/regression/ -v
   ```

5. **Full suite**
   ```bash
   uv run pytest tests/mcp/ -v --cov=src/superclaude/mcp --cov-report=term-missing
   ```

---

## Coverage Targets

| Category | Target | Rationale |
|----------|--------|-----------|
| Unit tests | 80% of new code | Standard coverage threshold |
| Critical paths (atomic write, locking) | 100% | Data integrity critical |
| Error handling paths | 100% | All E001-E008 codes tested |
| Public API functions | 100% | Contract stability |
| Platform-specific code | 80% | Cross-platform validation |

---

## Test Fixtures

### empty_config.json
```json
{
  "mcpServers": {}
}
```

### single_server.json
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### multiple_servers.json
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"]
    },
    "airis-mcp-gateway": {
      "url": "http://localhost:9400/sse"
    }
  }
}
```

### malformed_config.json
```json
{
  "mcpServers": {
    "broken":
}
```

### large_config.json
(100 server entries for performance testing)

---

## Test Constraints (Mandatory)

1. **NO writes outside test directories** during test runs
2. **NO external API calls** to production systems
3. **NO destructive operations** on real config files
4. **ALL tests must be idempotent** (safe to re-run)
5. **Use tmp_path fixture** for all file operations
6. **Mock filesystem** for platform-specific tests

---

## CI Integration

```yaml
# .github/workflows/test-mcp.yml
name: MCP Installer Tests

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ['3.10', '3.11', '3.12']

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --dev
      - run: uv run pytest tests/mcp/ -v --cov=src/superclaude/mcp
```

---

**Test strategy complete. 32 deliverables mapped to test coverage.**
