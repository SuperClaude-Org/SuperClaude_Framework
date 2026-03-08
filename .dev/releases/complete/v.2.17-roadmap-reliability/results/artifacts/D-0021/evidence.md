---
deliverable: D-0021
task: T05.03
title: Verification evidence - extraction frontmatter contains all 13+ required fields
date: 2026-03-08
status: PASS
---

# D-0021: Extraction Frontmatter Verification

## Source Protocol (FR-031 Required Fields)

13 required fields from the spec:

1. `spec_source`
2. `generated`
3. `generator`
4. `functional_requirements`
5. `nonfunctional_requirements`
6. `total_requirements`
7. `complexity_score`
8. `complexity_class`
9. `domains_detected`
10. `risks_identified`
11. `dependencies_identified`
12. `success_criteria_count`
13. `extraction_mode`

## Extraction.md Frontmatter (YAML parsed)

Total keys found: **14** (13 required + 1 executor-injected)

| Field | Present | Value | Type Valid |
|-------|---------|-------|------------|
| spec_source | YES | spec-roadmap-pipeline-reliability.md | string |
| generated | YES | 2026-03-08T00:00:00Z | ISO-8601 |
| generator | YES | claude-opus-4-6/requirements-extractor | string |
| functional_requirements | YES | 20 | integer |
| nonfunctional_requirements | YES | 6 | integer |
| total_requirements | YES | 26 | integer |
| complexity_score | YES | 0.72 | float |
| complexity_class | YES | moderate | string |
| domains_detected | YES | 4 | integer |
| risks_identified | YES | 5 | integer |
| dependencies_identified | YES | 6 | integer |
| success_criteria_count | YES | 5 | integer |
| extraction_mode | YES | full | string |
| pipeline_diagnostics | YES | (nested object) | FR-033 executor-injected |

## Verification

- **13/13 required fields present**: PASS
- **All values non-null**: PASS
- **Types appropriate**: PASS
- **14th field (pipeline_diagnostics)**: Injected by executor per FR-033 — expected bonus field
- **No fields from source protocol template are missing**: PASS
