# D-0021: FMEA Input Domain Enumerator Specification

## Module
`src/superclaude/cli/pipeline/fmea_domains.py`

## Algorithm
1. Check if deliverable is behavioral (computational) via `is_behavioral()`
2. Match verb in description to domain rule set (filter, count, compute, aggregate, default)
3. Return up to max_domains domains, degenerate cases prioritized

## Domain Categories (Priority Order for Default)
normal, empty, null, zero, negative, single_element, maximum_size, duplicate

## Verb-Specific Rules
- **filter**: normal, empty, filter_removes_all, filter_removes_none, single, null, duplicate, maximum
- **count**: normal, zero, single, maximum, empty, negative, duplicate, null
- **compute**: normal, zero, negative, empty, single, maximum, null, out_of_order
- **aggregate**: normal, empty, single, zero, maximum, duplicate, null, negative

## R-007 Mitigation
8-domain limit. Configurable via `max_domains` parameter.
