# Decision D-0003: Deviation Table Schema

| Field | Value |
|---|---|
| Decision ID | D-0003 |
| Open Question | OQ-006 |
| Related Requirements | FR-051.4 (AC-2), FR-026 |
| Supersedes | FR-051.1 AC-5 (8-column schema) |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

FR-051.1 AC-5 specifies an 8-column deviation table while FR-051.4 AC-2 specifies a 7-column table. Column names also differ (`Spec Quote`/`Roadmap Quote` vs `Upstream Quote`/`Downstream Quote`). Which schema is canonical?

## Decision

**The 7-column FR-051.4 schema is canonical. The `Source Pair` column is dropped from the table body and encoded in YAML frontmatter instead.**

### Canonical 7-Column Schema

| # | Column Name | Data Type | Description |
|---|---|---|---|
| 1 | ID | String | Unique deviation identifier (e.g., `DEV-001`) |
| 2 | Severity | Enum | `HIGH` \| `MEDIUM` \| `LOW` |
| 3 | Deviation | String | Description of the deviation found |
| 4 | Upstream Quote | String | Verbatim quote from the upstream (source/spec) document |
| 5 | Downstream Quote | String | Verbatim quote from the downstream (generated/roadmap) document |
| 6 | Impact | String | Assessment of the deviation's impact on correctness or completeness |
| 7 | Recommended Correction | String | Specific action to resolve the deviation |

### Severity Classification

| Level | Criteria |
|---|---|
| HIGH | Functional requirement missing, signature changed, constraint dropped, API contract broken |
| MEDIUM | Requirement simplified, parameter renamed, NFR softened |
| LOW | Formatting difference, section reordering, clarification added |

### Source Pair Encoding

The `Source Pair` information (which two documents were compared) is encoded in the YAML frontmatter:

```yaml
source_pair: "spec.md → roadmap.md"
upstream_file: "spec.md"
downstream_file: "roadmap.md"
```

### Column Name Rationale

Generic names `Upstream Quote` / `Downstream Quote` are used instead of `Spec Quote` / `Roadmap Quote` because:
- The fidelity check is reusable across document pairs (spec→roadmap, roadmap→tasklist)
- Generic names avoid coupling the schema to a specific comparison direction
- Frontmatter `source_pair` provides the specific document context

## Impacts

- **FR-051.4 AC-2**: This decision ratifies the 7-column schema as canonical.
- **FR-051.1 AC-5**: The 8-column schema is superseded. Implementations referencing AC-5 must use this 7-column schema.
- **FR-026**: The deviation report format reference document will use this schema definition.
- **Downstream consumers**: Gates, CLI, and prompt builders all consume this single schema.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-006 | 7-column FR-051.4 schema; Source Pair in frontmatter; generic column names | FR-051.4, FR-026 |
