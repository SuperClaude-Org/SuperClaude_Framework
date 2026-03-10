# D-0011: InvariantEntry Data Structure Specification

## Module
`src/superclaude/cli/pipeline/invariants.py`

## MutationSite Dataclass
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| deliverable_id | str | (required) | ID of deliverable containing this mutation |
| expression | str | (required) | Mutation expression text |
| context | str | "" | Surrounding context |

## InvariantEntry Dataclass
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| variable_name | str | (required) | State variable name |
| scope | str | (required) | Scope where variable lives |
| invariant_predicate | str | (required) | Constrained grammar predicate (validated) |
| mutation_sites | list[MutationSite] | [] | All known write paths |
| verification_deliverable_ids | list[str] | [] | Cross-milestone verification IDs |

## Constrained Grammar Syntax
```
predicate := clause (('AND'|'OR') clause)*
clause    := variable_name comparison_op expression
comparison_op := '==' | '!=' | '<' | '<=' | '>' | '>=' | 'is' | 'is not' | 'in' | 'not in'
```

### Valid examples
- `offset >= 0`
- `_loaded_start_index >= 0 AND _loaded_start_index <= len(events)`
- `state is not None`
- `status in VALID_STATES`

### Invalid (rejected with ValueError)
- `"the offset should always be positive"` (free-form text)
- `"offset positive"` (no comparison operator)
- `""` (empty)

## Validation Behavior
- `__post_init__` calls `validate_predicate()` on construction
- Invalid predicates raise `ValueError` with descriptive message
- `check_duplicate_variables()` produces warnings (not errors) for same variable_name+scope

## Serialization
- `to_dict()` / `from_dict()` round-trip preserves all fields including nested MutationSite objects
- JSON-serializable output
