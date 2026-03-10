# D-0043: Conflict Detector Specification

## Conflict Categories

| Kind | Description | Severity | Detection Method |
|------|-------------|----------|-----------------|
| DIRECT_CONTRADICTION | Writer and reader state opposite things | high | Positive vs negative indicator sets |
| SCOPE_MISMATCH | Filtered subset vs full set | high | Scope indicator set comparison |
| TYPE_MISMATCH | Boolean vs integer, string vs numeric | medium | Type group intersection |
| COMPLETENESS_MISMATCH | Partial vs complete data | medium | Completeness indicator + invariant cross-ref |
| UNSPECIFIED_WRITER | Writer semantics unknown | high | writer_semantics == "UNSPECIFIED" → always conflicts |

## Detection Algorithms

### Direct Contradiction
Tokenize both sides. Check if writer tokens ∩ POSITIVE_INDICATORS ≠ ∅ AND reader tokens ∩ NEGATIVE_INDICATORS ≠ ∅ (or vice versa).

### Scope Mismatch
Check if one side contains scope-all indicators ({all, every, complete, full, entire, total, whole}) while the other contains scope-filtered indicators ({filtered, subset, partial, selected, matching, some}).

### Type Mismatch
Three type groups: boolean, integer, string. If writer tokens match group A and reader tokens match group B (A ≠ B) → type mismatch.

### Completeness Mismatch
Check completeness-full vs completeness-partial indicators. Enriched by M2 invariant predicate cross-reference: if invariant says "complete" but reader says "partial" → mismatch.

## Synonym Dictionary (R-014)

10 synonym groups covering:
- Quantity: total, count, number, quantity, sum, amount
- Scope: all, every, complete, full, entire, whole
- Filtering: filtered, subset, partial, selected, matching
- Operations: processed, handled, completed, finished, consumed, delivered
- Position: offset, position, index, cursor, pointer, location
- Boolean: flag, boolean, bool, toggle, switch, indicator
- Numeric: integer, int, number, numeric, count
- String: string, str, text, name, label
- Active: active, enabled, on, true, running
- Inactive: inactive, disabled, off, false, stopped

Union-merge for words appearing in multiple groups (e.g., "count" in both quantity and numeric groups).

## Resolution Suggestion Format

Each conflict includes a `suggested_resolution` string with:
- Action verb (Add, Align, Clarify, Standardize, Verify)
- Target variable name
- Affected deliverable IDs
