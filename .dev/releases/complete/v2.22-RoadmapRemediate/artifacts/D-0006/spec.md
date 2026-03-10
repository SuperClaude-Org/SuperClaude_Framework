# D-0006: Primary Report Parser API

## Location
`src/superclaude/cli/roadmap/remediate_parser.py`

## Public API

### `parse_validation_report(text: str) -> list[Finding]`

Pure function. Takes raw markdown text from a merged validation report and returns a list of `Finding` objects.

**Supported formats:**
1. `reflect-merged.md` -- Agreement Table with Remediation Status column + Consolidated Findings
2. `merged-validation-report.md` -- Agreement Table (no Remediation Status) + Consolidated Findings

**Extraction strategy:**
1. Look for `## Consolidated Findings` section first
2. Within that section, parse `### BLOCKING`, `### WARNING`, `### INFO` subsections
3. Extract structured finding blocks matching pattern: `**[F-XX] [SEVERITY] Dimension: Description**`
4. Extract sub-fields: Location, Evidence, Fix guidance, Agreement from indented bullet lines
5. Overlay agreement categories from Agreement Table if present
6. Overlay remediation status (FIXED/OUT_OF_SCOPE/NO_ACTION_REQUIRED) from Agreement Table if present

**Error behavior:**
- Raises `ValueError` if no findings can be extracted
- Raises `ValueError` (via `_validate_required_fields`) if a finding block lacks id, severity, or description

**Purity guarantee (NFR-004):** No file I/O, no subprocess calls, no side effects, no global state mutation.
