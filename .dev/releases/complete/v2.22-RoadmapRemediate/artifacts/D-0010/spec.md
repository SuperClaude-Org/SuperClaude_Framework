# D-0010: Scope Filter and Auto-SKIP Logic

## Implementation

`filter_findings(findings: list[Finding], scope: RemediationScope) -> tuple[list[Finding], list[Finding]]`
in `src/superclaude/cli/roadmap/remediate.py`

## Filtering Rules

### Auto-SKIP (applied first, regardless of scope)
- `agreement_category == "NO_ACTION_REQUIRED"` -> SKIPPED
- `agreement_category == "OUT_OF_SCOPE"` -> SKIPPED
- `status in ("FIXED", "SKIPPED")` -> already terminal, SKIPPED

### Scope Filtering (applied after auto-SKIP)
- `BLOCKING_ONLY`: keeps severity == BLOCKING
- `BLOCKING_WARNING`: keeps severity in (BLOCKING, WARNING)
- `ALL`: keeps all findings with non-empty fix_guidance

## Pure Function Guarantee

No I/O, no side effects per NFR-004. Return type provides both actionable and skipped lists.

## Verification

`uv run pytest tests/roadmap/test_remediate.py -k "filter or skip"` exits 0
