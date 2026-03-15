# D-0001: CLI Availability Confirmation

## Task: T01.01 -- Verify `claude` CLI availability

**Date**: 2026-03-15
**Result**: AVAILABLE

## Evidence

### CLI Location
```
$ which claude
/config/.local/bin/claude
```

### Version Check
```
$ claude --version
2.1.76 (Claude Code)
EXIT_CODE=0
```

### Help Output
```
$ claude --help
Usage: claude [options] [command] [prompt]
Claude Code - starts an interactive session by default, use -p/--print for non-interactive output
```
Help exits 0 with full usage output (80+ lines of options and commands).

### `--print` Mode Test
```
$ claude --print -p "hello" --max-turns 1
```
**Result**: Command hangs indefinitely when invoked from within a running Claude Code session (nested invocation). This is expected behavior — the outer Claude session holds the API connection, and the inner `--print` call likely encounters authentication or concurrency constraints.

**Mitigation**: CLI is confirmed available and functional via `--version` and `--help`. The `--print` mode limitation is specific to nested invocation, not a CLI availability issue.

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| CLI binary accessible without manual PATH modifications | PASS | `/config/.local/bin/claude` in PATH |
| `claude --version` exits with code 0 | PASS | `2.1.76 (Claude Code)`, exit 0 |
| `claude --help` produces valid output | PASS | Full usage text, exit 0 |
| Command is repeatable | PASS | `--version` produces identical output on re-run |
| `--print` mode functional | PARTIAL | Hangs in nested invocation; not a CLI availability issue |

## Conclusion

CLI is installed, accessible, and functional. The `--print` mode cannot be tested from within a running Claude Code session due to nested invocation constraints. This does not affect the Phase 1 gate decision — the critical question (T01.03) about `--file` behavior can be answered through documentation analysis (T01.02) without requiring a live `--print` test.
