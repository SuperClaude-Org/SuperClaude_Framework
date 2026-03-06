# D-0005: Behavioral Detection Heuristic Specification

## Function Signature

```python
def is_behavioral(description: str) -> bool
```

## Location

`src/superclaude/cli/pipeline/deliverables.py`

## Detection Patterns

### 1. Computational Verbs
`compute, extract, filter, count, calculate, determine, select, track, increment, update, replace, introduce, implement, retry, parse, validate, transform, convert, aggregate, merge, split, normalize, encode, decode, generate, emit, dispatch, invoke, execute, process, build, construct, create, initialize, register`

### 2. State Mutation Patterns (regex)
- `self._\w+` — instance variable access
- `\bcounter\b`, `\boffset\b`, `\bcursor\b` — counting/position variables
- `\bmutate\b`, `\bstate\b` — explicit state references

### 3. Conditional Logic Patterns
`guard, sentinel, flag, early return, bounded, retry, fallback, threshold, limit, cap`

## Negative Signal Suppression

Documentation verbs suppress false positives: `document, describe, explain, list, outline, summarize, catalog, enumerate, write, draft, update readme, add readme`

**Rule**: If doc verb count >= behavioral verb count, classification is non-behavioral.

## Edge Cases

- Empty/whitespace descriptions → `False`
- "Add type definition for GateResult" → `False` (no computational verb match for "add" alone — "add" is not in the computational verbs set, only in the doc suppression context)
- "Update README" → `False` (suppressed by "update readme" doc pattern)
