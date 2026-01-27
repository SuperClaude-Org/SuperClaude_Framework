# Release Roadmap: v1.0-mcp-installer - JSON-Based MCP Installation

## Metadata
- **Source Specification**: `/config/workspace/SuperClaude/docs/specs/MCP-INSTALLER-SPEC.md`
- **Generated**: 2026-01-21T12:00:00Z
- **Generator Version**: v2.1
- **Codebase State**: N/A (new implementation)
- **Item Count**: 21 features, 0 bugs, 6 improvements, 2 refactors, 3 docs

### Persona Assignment

**Primary**: BACKEND — 37.5% of items are BACKEND work
**Consulting**:
- CONFIG for configuration items (28.1%)
- API for public interface items (18.8%)

**Rationale**: The majority of work involves backend Python implementation of JSON manipulation functions. CONFIG is the second-largest domain covering file operations, while API work defines the public interface contracts.

---

## Executive Summary

This release implements a reliable, JSON-based MCP server installation system for SuperClaude Framework, replacing the problematic CLI-based approach that exhibited argument parsing bugs. The implementation provides atomic file operations, secure API key handling, and a clean public API for server registration and management.

---

## Milestones Overview

| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|
| M1 | Foundation | 6 | None | Low |
| M2 | Core Config Operations | 6 | M1 | Medium |
| M3 | Server Installation | 7 | M2 | Medium |
| M4 | Server Management | 5 | M3 | Low |
| M5 | Public API & Quality | 5 | M4 | Low |
| M6 | Documentation & Polish | 3 | M5 | Low |

---

### Milestone 1: Foundation

**Objective**: Establish core infrastructure for config file detection and basic file operations.
**Dependencies**: None
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-001 | FEATURE | Config file location detection | GIVEN any supported platform WHEN get_config_file_path() called THEN returns correct path (~/.claude/mcp.json) | `src/superclaude/mcp/config.py` |
| REQ-002 | FEATURE | Config file creation | GIVEN ~/.claude/ does not exist WHEN save_config() called THEN directory and file created with proper permissions | `src/superclaude/mcp/config.py` |
| IMP-006 | IMPROVEMENT | File permissions (0600) | GIVEN new config file created WHEN checking permissions THEN mode is 0600 (owner read/write only) | `src/superclaude/mcp/config.py` |
| REQ-014 | FEATURE | Public API: get_config_file_path() | GIVEN import of config module WHEN calling get_config_file_path() THEN returns Path object to config file | `src/superclaude/mcp/config.py` |
| REQ-015 | FEATURE | Public API: load_config() | GIVEN valid or non-existent config WHEN load_config() called THEN returns dict with mcpServers key (empty if new) | `src/superclaude/mcp/config.py` |
| REQ-012 | FEATURE | Installation status detection | GIVEN config with servers WHEN check_server_installed("name") called THEN returns True if present, False otherwise | `src/superclaude/mcp/config.py` |

#### Verification Checkpoint M1
- [ ] All deliverables code-complete
- [ ] Unit tests written and passing (per test-strategy.md)
- [ ] Cross-platform path detection verified (Linux, macOS, Windows)
- [ ] File permission tests passing
- [ ] No regressions in related functionality

---

### Milestone 2: Core Config Operations

**Objective**: Implement atomic write operations and config preservation with concurrency protection.
**Dependencies**: M1
**Estimated Complexity**: Medium

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-004 | FEATURE | Atomic write operations | GIVEN concurrent writes or failures WHEN save_config() called THEN original file never corrupted (uses temp+rename) | `src/superclaude/mcp/config.py` |
| REQ-003 | FEATURE | Config file preservation | GIVEN existing servers in config WHEN adding new server THEN all existing servers preserved unchanged | `src/superclaude/mcp/config.py` |
| REQ-016 | FEATURE | Public API: save_config() | GIVEN valid config dict WHEN save_config() called THEN file written atomically with validation | `src/superclaude/mcp/config.py` |
| IMP-002 | IMPROVEMENT | Config read/write performance | GIVEN config file up to 100KB WHEN read/write operations THEN complete within 100ms | `src/superclaude/mcp/config.py` |
| IMP-003 | IMPROVEMENT | Failure recovery | GIVEN write failure mid-operation WHEN checking config state THEN original config intact | `src/superclaude/mcp/config.py` |
| IMP-004 | IMPROVEMENT | Concurrent access protection | GIVEN two processes writing simultaneously WHEN both complete THEN no data corruption (file locking) | `src/superclaude/mcp/config.py` |

#### Verification Checkpoint M2
- [ ] All deliverables code-complete
- [ ] Atomic write tests passing (including simulated failures)
- [ ] Concurrent access tests passing
- [ ] Performance benchmarks met (<100ms for 100KB)
- [ ] Integration with M1 components verified

---

### Milestone 3: Server Installation

**Objective**: Implement all server type installation methods with secure API key handling.
**Dependencies**: M2
**Estimated Complexity**: Medium

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-005 | FEATURE | NPM-based server installation | GIVEN server config with npx command WHEN register_server() called THEN JSON includes command, args, env fields | `src/superclaude/mcp/config.py`, `src/superclaude/mcp/servers.py` |
| REQ-006 | FEATURE | UVX-based server installation | GIVEN uvx command string WHEN parsing and registering THEN args properly split and stored | `src/superclaude/mcp/servers.py` |
| REQ-007 | FEATURE | SSE transport server installation | GIVEN SSE endpoint URL WHEN registering THEN config includes url field | `src/superclaude/mcp/servers.py` |
| REQ-008 | FEATURE | Environment variable handling | GIVEN API key required WHEN registering server THEN key stored in env object securely | `src/superclaude/mcp/servers.py` |
| IMP-005 | IMPROVEMENT | API key masking in logs | GIVEN API key value WHEN logging installation THEN only last 4 chars visible | `src/superclaude/mcp/servers.py` |
| REQ-009 | FEATURE | Idempotent installation | GIVEN server already installed WHEN install requested THEN returns success without modification | `src/superclaude/mcp/servers.py` |
| REF-001 | REFACTOR | Remove CLI-based installation | GIVEN install_mcp.py exists WHEN completing refactor THEN no `claude mcp add` subprocess calls remain | `src/superclaude/cli/install_mcp.py` |

#### Verification Checkpoint M3
- [ ] All deliverables code-complete
- [ ] NPM server installation tests passing (context7, playwright)
- [ ] UVX server installation tests passing (serena)
- [ ] SSE server installation tests passing (airis-gateway)
- [ ] API key masking verified in log output
- [ ] Idempotency tests passing
- [ ] No CLI subprocess calls in codebase (grep verification)

---

### Milestone 4: Server Management

**Objective**: Implement server uninstallation, health checks, and unified registration API.
**Dependencies**: M3
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-010 | FEATURE | Server uninstallation | GIVEN server in config WHEN unregister_server() called THEN server removed, others preserved | `src/superclaude/mcp/config.py` |
| REQ-011 | FEATURE | Graceful non-existent removal | GIVEN server not in config WHEN unregister_server() called THEN returns success (idempotent) | `src/superclaude/mcp/config.py` |
| REQ-018 | FEATURE | Public API: unregister_server() | GIVEN server name WHEN calling unregister_server() THEN server removed or no-op if absent | `src/superclaude/mcp/config.py` |
| REQ-013 | FEATURE | SSE server health check | GIVEN SSE server configured WHEN checking status THEN HTTP connection attempted to verify endpoint | `src/superclaude/mcp/health.py` |
| REF-002 | REFACTOR | Unified installation interface | GIVEN any server type WHEN using register_server() THEN single entry point handles all types | `src/superclaude/mcp/servers.py` |

#### Verification Checkpoint M4
- [ ] All deliverables code-complete
- [ ] Uninstallation tests passing
- [ ] Idempotent removal tests passing
- [ ] SSE health check tests passing
- [ ] Unified interface used by all server types

---

### Milestone 5: Public API & Quality

**Objective**: Finalize public API, implement error codes and schema validation.
**Dependencies**: M4
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-017 | FEATURE | Public API: register_server() | GIVEN server config WHEN register_server(name, config) called THEN server added with overwrite option | `src/superclaude/mcp/config.py` |
| REQ-019 | FEATURE | Public API: check_server_installed() | GIVEN server name WHEN calling check_server_installed() THEN returns boolean | `src/superclaude/mcp/config.py` |
| REQ-020 | FEATURE | JSON schema validation | GIVEN config dict WHEN saving THEN validated against JSON schema | `src/superclaude/mcp/schema.py` |
| REQ-021 | FEATURE | Error code system | GIVEN error condition WHEN exception raised THEN uses E001-E008 codes | `src/superclaude/mcp/exceptions.py` |
| IMP-001 | IMPROVEMENT | Installation performance | GIVEN any server WHEN installing THEN completes within 5 seconds (excl. network) | `src/superclaude/mcp/servers.py` |

#### Verification Checkpoint M5
- [ ] All deliverables code-complete
- [ ] Public API documented with docstrings
- [ ] Schema validation tests passing
- [ ] Error codes properly raised and documented
- [ ] Performance benchmarks met

---

### Milestone 6: Documentation & Polish

**Objective**: Complete documentation and ensure release readiness.
**Dependencies**: M5
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| DOC-001 | DOC | API documentation | GIVEN new mcp module WHEN documentation generated THEN all public functions documented with examples | `docs/reference/mcp-api.md` |
| DOC-002 | DOC | Migration guide | GIVEN users on CLI approach WHEN reading guide THEN can migrate to JSON approach | `docs/user-guide/mcp-migration.md` |
| DOC-003 | DOC | Troubleshooting guide | GIVEN common errors WHEN users encounter them THEN troubleshooting steps available | `docs/troubleshooting/mcp-installation.md` |

#### Verification Checkpoint M6
- [ ] All documentation complete
- [ ] Migration guide tested with example upgrade
- [ ] Troubleshooting covers all E001-E008 errors
- [ ] README updated with new installation method
- [ ] CHANGELOG updated

---

## Dependency Graph

```
REQ-001 (path detection)
    └── REQ-002 (file creation)
            ├── REQ-003 (preservation)
            │       └── REQ-005, REQ-006, REQ-007 (installation methods)
            │               ├── REQ-008 (env handling)
            │               ├── REQ-009 (idempotent)
            │               └── REF-001 (remove CLI)
            └── REQ-004 (atomic write)
                    ├── IMP-003 (failure recovery)
                    └── IMP-004 (concurrency)

REQ-010 (uninstall) ──► REQ-011 (graceful removal)

REQ-012 (status check) ◄── REQ-001, REQ-002

REQ-014, REQ-015, REQ-016, REQ-017, REQ-018, REQ-019 (Public API)
    └── Depends on respective implementation items

DOC-001, DOC-002, DOC-003 ◄── All implementation complete
```

---

## Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R1 | Atomic write fails on Windows | Medium | High | Test extensively on Windows; use `os.replace()` which is atomic on NTFS |
| R2 | File locking incompatible across platforms | Medium | Medium | Use `fcntl` on Unix, `msvcrt` on Windows; provide fallback mode |
| R3 | JSON schema changes in Claude Code | Low | High | Version schema; implement migration logic for future changes |
| R4 | Concurrent processes corrupt config | Low | High | Implement file locking with timeout; document manual recovery |
| R5 | API key exposure in logs | Low | Critical | Mask keys before any logging; security review before release |
| R6 | Performance regression on large configs | Low | Medium | Benchmark with 100+ servers; implement lazy loading if needed |

---

## Traceability Matrix

| Extraction ID | Milestone | Deliverable Status |
|---------------|-----------|-------------------|
| REQ-001 | M1 | Planned |
| REQ-002 | M1 | Planned |
| REQ-003 | M2 | Planned |
| REQ-004 | M2 | Planned |
| REQ-005 | M3 | Planned |
| REQ-006 | M3 | Planned |
| REQ-007 | M3 | Planned |
| REQ-008 | M3 | Planned |
| REQ-009 | M3 | Planned |
| REQ-010 | M4 | Planned |
| REQ-011 | M4 | Planned |
| REQ-012 | M1 | Planned |
| REQ-013 | M4 | Planned |
| REQ-014 | M1 | Planned |
| REQ-015 | M1 | Planned |
| REQ-016 | M2 | Planned |
| REQ-017 | M5 | Planned |
| REQ-018 | M4 | Planned |
| REQ-019 | M5 | Planned |
| REQ-020 | M5 | Planned |
| REQ-021 | M5 | Planned |
| IMP-001 | M5 | Planned |
| IMP-002 | M2 | Planned |
| IMP-003 | M2 | Planned |
| IMP-004 | M2 | Planned |
| IMP-005 | M3 | Planned |
| IMP-006 | M1 | Planned |
| REF-001 | M3 | Planned |
| REF-002 | M4 | Planned |
| DOC-001 | M6 | Planned |
| DOC-002 | M6 | Planned |
| DOC-003 | M6 | Planned |

**Total Items**: 32
**Items in Milestones**: 32
**Traceability**: ✅ Complete

---

**Roadmap construction complete. 6 milestones with 32 total deliverables.**
