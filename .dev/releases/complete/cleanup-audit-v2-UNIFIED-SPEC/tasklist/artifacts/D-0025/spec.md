# D-0025: Documentation Audit Specification

## Audit Dimensions

| Dimension | Method | Output |
|-----------|--------|--------|
| Broken links | Parse `[text](path)` markdown patterns; verify each target path exists on disk | List of `{source_file, line_number, link_text, target_path, status}` |
| Staleness | Run `git log -1 --format=%aI` per doc file; flag if last modification > 365 days | List of `{file_path, last_modified, days_since_update, stale}` |

## Link Validation Rules

- Relative paths resolved against the source file's directory
- Anchor fragments (`#section`) are checked for heading existence when target is `.md`
- External URLs (http/https) are reported but not validated (no network calls during audit)

## Staleness Threshold

Default: 365 days since last git commit touching the file. Files with no git history (untracked) are flagged as `unknown_age` rather than stale.

## Implementation

- Module: `src/superclaude/cli/audit/docs_audit.py`
- `scan_links()`: extracts and validates markdown link references
- `check_staleness()`: queries git history for last-modified dates
- `full_docs_audit()`: combines both dimensions into a unified report
- Operates on `.md`, `.rst`, and `.txt` files within the project tree
