# Canonical Deviation Report Schema

| Field | Value |
|---|---|
| Deliverable ID | D-0010 |
| Source Decision | D-0003 (OQ-006) |
| Schema Version | 1.0 |
| Date | 2026-03-09 |
| Status | PUBLISHED |

## Overview

This document defines the canonical deviation report format used by all pipeline steps, gates, CLI commands, and prompt builders in the v2.20 WorkflowEvolution release.

## YAML Frontmatter Schema

Every deviation report begins with YAML frontmatter containing the following required fields:

```yaml
---
source_pair: "<upstream_file> → <downstream_file>"
upstream_file: "<path to upstream document>"
downstream_file: "<path to downstream document>"
high_severity_count: <integer>
medium_severity_count: <integer>
low_severity_count: <integer>
total_deviations: <integer>
validation_complete: <boolean>
fidelity_check_attempted: <boolean>
tasklist_ready: <boolean>
---
```

### Frontmatter Field Definitions

| Field | Type | Description |
|---|---|---|
| source_pair | String | Human-readable label: `"<upstream> → <downstream>"` |
| upstream_file | String | Relative path to the upstream (source/spec) document |
| downstream_file | String | Relative path to the downstream (generated) document |
| high_severity_count | Integer | Count of HIGH-severity deviations |
| medium_severity_count | Integer | Count of MEDIUM-severity deviations |
| low_severity_count | Integer | Count of LOW-severity deviations |
| total_deviations | Integer | Total deviation count (should equal sum of severity counts) |
| validation_complete | Boolean | `true` if the fidelity check completed without errors |
| fidelity_check_attempted | Boolean | `true` if the fidelity check was invoked (may be `true` even if validation_complete is `false`) |
| tasklist_ready | Boolean | `true` only if `high_severity_count == 0` AND `validation_complete == true` |

## Deviation Table Schema (7 Columns)

The deviation table follows the frontmatter and uses standard Markdown table format:

| # | Column | Type | Description |
|---|---|---|---|
| 1 | ID | String | Unique deviation identifier. Format: `DEV-NNN` (zero-padded 3-digit). |
| 2 | Severity | Enum | One of: `HIGH`, `MEDIUM`, `LOW`. |
| 3 | Deviation | String | Concise description of what differs between upstream and downstream. |
| 4 | Upstream Quote | String | Verbatim quote from the upstream document demonstrating the expected content. |
| 5 | Downstream Quote | String | Verbatim quote from the downstream document showing the actual content (or `[MISSING]` if absent). |
| 6 | Impact | String | Assessment of how this deviation affects correctness, completeness, or downstream consumers. |
| 7 | Recommended Correction | String | Specific, actionable instruction to resolve the deviation. |

## Severity Classification Rules

| Level | Criteria | Examples |
|---|---|---|
| HIGH | Functional requirement missing, signature changed, constraint dropped, API contract broken | Missing FR, wrong parameter types, deleted validation rule |
| MEDIUM | Requirement simplified, parameter renamed, NFR softened | Reduced precision, name change without semantic loss, relaxed threshold |
| LOW | Formatting difference, section reordering, clarification added | Whitespace change, moved paragraph, added explanatory note |

## Gate Interactions

| Gate Check | Field Used | Logic | Blocking |
|---|---|---|---|
| `_high_severity_count_zero()` | `high_severity_count` | Returns `True` only if value is `0`; `False` if missing | Yes (v2.20) |
| `_tasklist_ready_consistent()` | `tasklist_ready`, `high_severity_count`, `validation_complete` | Returns `True` if `tasklist_ready` is consistent with `high_severity_count == 0 AND validation_complete == true` | Yes (v2.20) |
| Count cross-validation | All severity counts vs table rows | Warning log on mismatch; not blocking | No (warning only) |

## Example Report

```markdown
---
source_pair: "spec.md → roadmap.md"
upstream_file: "spec.md"
downstream_file: "roadmap.md"
high_severity_count: 1
medium_severity_count: 2
low_severity_count: 0
total_deviations: 3
validation_complete: true
fidelity_check_attempted: true
tasklist_ready: false
---

# Deviation Report: spec.md → roadmap.md

| ID | Severity | Deviation | Upstream Quote | Downstream Quote | Impact | Recommended Correction |
|---|---|---|---|---|---|---|
| DEV-001 | HIGH | Missing FR-019 implementation | "Cross-references must be validated" | [MISSING] | Pipeline cannot enforce cross-ref integrity | Add FR-019 to roadmap Phase 2 deliverables |
| DEV-002 | MEDIUM | NFR timeout relaxed | "120s hard limit" | "120s target, 600s timeout" | Performance measurement less strict | Clarify as p95 target per OQ-008 decision |
| DEV-003 | MEDIUM | Parameter renamed | "spec_file" | "source_file" | Import paths need updating | Rename to "spec_file" for consistency |
```

## Versioning

This schema is version 1.0, effective for v2.20 WorkflowEvolution. Changes to the schema require a new decision document updating D-0003 and incrementing this version number.
