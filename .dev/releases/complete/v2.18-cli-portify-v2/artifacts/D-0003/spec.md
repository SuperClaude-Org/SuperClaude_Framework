# D-0003: Specification — Stale-Ref Detector Script

**Task**: T01.02
**Roadmap Items**: R-006, R-007
**Date**: 2026-03-08

## Script Location

`scripts/check-ref-staleness.py`

## Purpose

Compares field names in ref files (`pipeline-spec.md`, `code-templates.md`) against the live Python API in `models.py` and `gates.py`. Exits non-zero on any mismatch.

## Detection Capabilities

1. **GateCriteria field name drift**: Detects old `tier=` vs correct `enforcement_tier=`
2. **Frontmatter field name drift**: Detects `required_frontmatter=` vs correct `required_frontmatter_fields=`
3. **Tier casing errors**: Flags lowercase tier values that should be UPPER_CASE
4. **SemanticCheck field drift**: Detects `fn=` vs correct `check_fn=`
5. **Signature drift**: Detects `tuple[bool, str]` return type vs correct `Callable[[str], bool]`

## Checked Locations

- `src/superclaude/skills/sc-cli-portify/refs/pipeline-spec.md`
- `src/superclaude/skills/sc-cli-portify/refs/code-templates.md`
- `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` (if exists)
- `src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md` (if exists)

## Usage

```bash
uv run python scripts/check-ref-staleness.py
```

Exit code 0 = all refs match live API. Exit code 1 = mismatches found.

## Reusability

Designed for reuse in Phase 4 (M4.1) conformance checking and CI integration.
