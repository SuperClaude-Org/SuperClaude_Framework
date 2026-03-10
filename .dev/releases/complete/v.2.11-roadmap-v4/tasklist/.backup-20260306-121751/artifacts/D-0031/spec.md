# D-0031: Guard and Sentinel Analyzer Specification

## Guard Detection Patterns

The analyzer detects five guard kinds:
1. **IF_ELSE**: `if <var> ... else ...`, `check if/whether <var>`
2. **EARLY_RETURN**: `early return ... <var>`
3. **SENTINEL_VALUE**: `<var> sentinel`, `sentinel for <var>`, `bounded by`, `threshold`
4. **FLAG_CHECK**: `<var> guard`, `guard on/for <var>`, `<var> flag`, `flag <var>`, `check if <var>`
5. **TYPE_CHANGE**: `replace bool <var> with int`, `<var> from bool to int`, `bool->int`

## Type Transition Detection

| Source | Target | Transition Kind | Trigger |
|--------|--------|-----------------|---------|
| bool   | int    | BOOL_TO_INT     | Always triggers transition analysis |
| bool   | enum   | BOOL_TO_ENUM    | Exhaustive state enumeration |
| enum   | string | ENUM_TO_STRING  | Unknown string handling |

## State Enumeration Algorithm

For each detected guard, enumerate all possible values:
- **FLAG_CHECK**: `{true, false}` with single semantic meaning each
- **SENTINEL_VALUE**: `{sentinel, normal}` with marker vs. range meanings
- **IF_ELSE / EARLY_RETURN**: `{truthy, falsy}` based on condition
- **TYPE_CHANGE (bool->int)**: `{0, N>0, N<0}` where 0 inherits dual semantics
- **TYPE_CHANGE (bool->enum)**: `{state_A, state_B, state_C}` with migration mapping
- **TYPE_CHANGE (enum->string)**: `{valid, empty, unknown}` string states

## Ambiguity Flagging Criteria

A guard state is **ambiguous** when its value maps to 2+ semantic meanings.

**Always-ambiguous**: bool->int transition for value `0` (original false + zero numeric)

**Never-ambiguous**: bool flags with clear true/false, enum with exhaustive match

## Suppression

`@no-ambiguity-check(rationale)` suppresses detection. Rationale is mandatory.

## Known Archetypes (R-010)

- **replay**: `{0: [no events, start offset], N>0: [offset into list]}` — seeded from `_replayed_event_offset` pattern
- **boolean**: `{true: [active], false: [inactive]}` — baseline flag pattern

## Implementation

- File: `src/superclaude/cli/pipeline/guard_analyzer.py`
- Exports: `detect_guards`, `GuardDetection`, `GuardKind`, `TypeTransitionKind`, `GuardState`, `SemanticMeaning`
- NFR-007 compliant: no imports from sprint or roadmap modules
