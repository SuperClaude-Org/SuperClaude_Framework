# D-0007: Fallback Parser with Deduplication

## Location
`src/superclaude/cli/roadmap/remediate_parser.py`

## Public API

### `parse_individual_reports(report_texts: list[str]) -> list[Finding]`

Pure function. Takes a list of raw markdown texts from individual `reflect-*.md` reports and returns a deduplicated list of `Finding` objects.

**Deduplication rule (spec §8/OQ-003):**
1. **Location match**: Same file + within 5 lines = candidate duplicate
2. **Severity resolution**: Higher severity wins (BLOCKING > WARNING > INFO)
3. **Fix guidance**: Merged from both reports (winner's guidance first, loser's appended with `[Additional]:` prefix)
4. **Files affected**: Union of both findings' files

**Non-matching findings** are included as-is from their source report.

**Supported format:** Individual reflect-*.md reports with `## Findings` section containing structured finding blocks.

**Purity guarantee (NFR-004):** No file I/O, no subprocess calls, no side effects.
