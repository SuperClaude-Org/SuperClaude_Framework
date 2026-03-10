# D-0017: File Allowlist Enforcement

## Module
`src/superclaude/cli/roadmap/remediate_executor.py`

## Constants
`EDITABLE_FILES = frozenset({"roadmap.md", "extraction.md", "test-strategy.md"})`

## Function
`enforce_allowlist(findings: list[Finding]) -> tuple[list[Finding], list[Finding]]`

## Enforcement Rules
- Findings with ALL files in allowlist -> allowed
- Findings with ANY file outside allowlist -> SKIPPED with WARNING (OQ-004)
- Findings with no files_affected -> rejected
- Basename matching (path prefixes stripped)

## NFR Compliance
- NFR-004: Pure function (logging is side-effect-safe)
