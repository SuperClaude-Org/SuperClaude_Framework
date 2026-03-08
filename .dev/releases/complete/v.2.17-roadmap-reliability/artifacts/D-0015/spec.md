# D-0015: Expanded Extract Prompt Frontmatter

## Deliverable

`build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` updated to request all 13 frontmatter fields.

## Fields Added (10 new, 3 existing)

| Field | Type | Status |
|-------|------|--------|
| spec_source | string | NEW |
| generated | string (ISO-8601) | NEW |
| generator | string | NEW |
| functional_requirements | integer | existing |
| nonfunctional_requirements | integer | NEW |
| total_requirements | integer | NEW |
| complexity_score | float 0.0-1.0 | existing |
| complexity_class | string enum | existing |
| domains_detected | integer | NEW |
| risks_identified | integer | NEW |
| dependencies_identified | integer | NEW |
| success_criteria_count | integer | NEW |
| extraction_mode | string enum | NEW |

## Verification

- All 13 field names present in prompt return value
- Each field has type annotation and description
- `<output_format>` XML block remains at end of prompt
