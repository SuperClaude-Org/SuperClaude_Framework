# Extraction: v1.0-mcp-installer

**Source**: `/config/workspace/SuperClaude/docs/specs/MCP-INSTALLER-SPEC.md`
**Extracted**: 2026-01-21T12:00:00Z
**Generator Version**: v2.1

## Extracted Items

| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | CONFIG | Config file location detection - resolve `~/.claude/mcp.json` path cross-platform (Linux/macOS/Windows) | None | P1-High |
| REQ-002 | FEATURE | CONFIG | Config file creation - create `~/.claude/` directory and `mcp.json` if not exist with proper permissions (0700/0600) | REQ-001 | P1-High |
| REQ-003 | FEATURE | CONFIG | Config file preservation - preserve existing server entries when adding new servers | REQ-002 | P1-High |
| REQ-004 | FEATURE | CONFIG | Atomic write operations - use temp file + rename pattern to prevent corruption | REQ-002 | P0-Critical |
| REQ-005 | FEATURE | BACKEND | NPM-based server installation - configure servers with command/args/env JSON structure | REQ-003, REQ-004 | P1-High |
| REQ-006 | FEATURE | BACKEND | UVX-based server installation - parse uvx commands and configure with proper args | REQ-003, REQ-004 | P1-High |
| REQ-007 | FEATURE | BACKEND | SSE transport server installation - configure servers with url field | REQ-003, REQ-004 | P1-High |
| REQ-008 | FEATURE | SECURITY | Environment variable handling - securely store API keys in env object, mask in logs | REQ-005 | P1-High |
| REQ-009 | FEATURE | BACKEND | Idempotent installation - detect existing servers and skip re-installation | REQ-003 | P2-Medium |
| REQ-010 | FEATURE | BACKEND | Server uninstallation - remove server config without affecting other entries | REQ-003, REQ-004 | P2-Medium |
| REQ-011 | FEATURE | BACKEND | Graceful non-existent removal - handle uninstall of non-existent server without error | REQ-010 | P2-Medium |
| REQ-012 | FEATURE | BACKEND | Installation status detection - check config file for server presence | REQ-001, REQ-002 | P1-High |
| REQ-013 | FEATURE | BACKEND | SSE server health check - verify SSE endpoint availability for gateway servers | REQ-007 | P3-Low |
| IMP-001 | IMPROVEMENT | BACKEND | Performance - single server installation within 5 seconds (excluding network) | REQ-005, REQ-006, REQ-007 | P2-Medium |
| IMP-002 | IMPROVEMENT | CONFIG | Performance - config read/write within 100ms for files up to 100KB | REQ-003, REQ-004 | P2-Medium |
| IMP-003 | IMPROVEMENT | CONFIG | Failure recovery - ensure config never left corrupted on failure | REQ-004 | P1-High |
| IMP-004 | IMPROVEMENT | CONFIG | Concurrent access protection - file locking with timeout and retry | REQ-004 | P2-Medium |
| IMP-005 | IMPROVEMENT | SECURITY | API key masking - never log full API keys (mask all but last 4 chars) | REQ-008 | P1-High |
| IMP-006 | IMPROVEMENT | SECURITY | File permissions - create config with mode 0600 (owner read/write only) | REQ-002 | P1-High |
| REF-001 | REFACTOR | BACKEND | Remove CLI-based installation code - replace `claude mcp add` with JSON manipulation | REQ-005, REQ-006, REQ-007 | P0-Critical |
| REF-002 | REFACTOR | BACKEND | Unify installation interface - single entry point for all server types | REQ-005, REQ-006, REQ-007 | P2-Medium |
| DOC-001 | DOC | DOCS | API documentation - document public functions with examples | REQ-001 through REQ-013 | P2-Medium |
| DOC-002 | DOC | DOCS | Migration guide - document upgrade from CLI to JSON approach | REF-001 | P2-Medium |
| DOC-003 | DOC | DOCS | Troubleshooting guide - common errors and recovery procedures | IMP-003 | P3-Low |
| REQ-014 | FEATURE | API | Public API: get_config_file_path() function | REQ-001 | P1-High |
| REQ-015 | FEATURE | API | Public API: load_config() function with error handling | REQ-002 | P1-High |
| REQ-016 | FEATURE | API | Public API: save_config() function with atomic write | REQ-004 | P1-High |
| REQ-017 | FEATURE | API | Public API: register_server() function with overwrite option | REQ-003, REQ-005 | P1-High |
| REQ-018 | FEATURE | API | Public API: unregister_server() function (idempotent) | REQ-010, REQ-011 | P1-High |
| REQ-019 | FEATURE | API | Public API: check_server_installed() function | REQ-012 | P1-High |
| REQ-020 | FEATURE | CONFIG | JSON schema validation - validate config against defined schema | REQ-015 | P2-Medium |
| REQ-021 | FEATURE | BACKEND | Error code system - implement E001-E008 error codes | REQ-015, REQ-016, REQ-017 | P2-Medium |

## Summary Statistics

| Type | Count |
|------|-------|
| FEATURE (REQ-) | 21 |
| IMPROVEMENT (IMP-) | 6 |
| REFACTOR (REF-) | 2 |
| DOC (DOC-) | 3 |
| **TOTAL** | **32** |

## Domain Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
| BACKEND | 12 | 37.5% |
| CONFIG | 9 | 28.1% |
| API | 6 | 18.8% |
| SECURITY | 3 | 9.4% |
| DOCS | 3 | 9.4% |

---

**Extraction complete. 32 items identified.**
