# Decision D-0006: Count Cross-Validation Policy

| Field | Value |
|---|---|
| Decision ID | D-0006 |
| Open Question | OQ-003 |
| Related Requirements | NFR-006 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

Should the gate verify that frontmatter severity counts match actual table row counts? Would mismatches block the pipeline or log warnings?

## Decision

**Implement count cross-validation as a warning log, not a gate blocker.**

### Behavior

When the gate detects a mismatch between frontmatter severity counts (e.g., `high_severity_count: 2`) and the actual count of table rows with that severity:

1. **Log a warning** with the specific mismatch details:
   ```
   WARNING: Frontmatter high_severity_count=2 but table contains 3 HIGH rows
   ```
2. **Do not block** the pipeline. The gate returns `True` (pass) regardless of count mismatches.
3. **Include mismatch data** in the deviation report output for downstream audit.

### What Is Validated

| Check | Source | Target | Action on Mismatch |
|---|---|---|---|
| HIGH count | `high_severity_count` frontmatter | Rows with `Severity=HIGH` | Warning log |
| MEDIUM count | `medium_severity_count` frontmatter | Rows with `Severity=MEDIUM` | Warning log |
| LOW count | `low_severity_count` frontmatter | Rows with `Severity=LOW` | Warning log |
| Total count | `total_deviations` frontmatter | Total table rows | Warning log |

## Rationale

- **LLM inconsistency reduction**: LLMs frequently miscalculate counts in frontmatter relative to table content. Logging mismatches makes these inconsistencies visible without creating false-positive pipeline blocks.
- **False-positive risk**: Blocking on count mismatches would frequently halt pipelines for non-substantive errors (the deviations themselves are correct; only the summary count is wrong).
- **Auditability**: Warning logs provide evidence of LLM counting errors for quality tracking and prompt improvement.
- **NFR-006 compliance**: No new executor/process framework introduced; this is a lightweight check within existing gate logic.

## Impacts

- **Gate framework**: A new warning-only check is added to existing gate logic. No new gate type required.
- **Downstream consumers**: Count mismatch warnings are available in pipeline output for monitoring dashboards.
- **Prompt improvement**: Persistent count mismatches indicate prompt template issues that can be addressed iteratively.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-003 | Warning log for count mismatches, not gate blocker | NFR-006 |
