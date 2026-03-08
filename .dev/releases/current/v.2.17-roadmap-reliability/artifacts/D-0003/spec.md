# D-0003: Required Fields Validation

## Summary

After regex discovery, `_check_frontmatter()` extracts keys from the captured frontmatter block and validates all `required_fields` are present.

## Implementation

```python
found_keys: set[str] = set()
for line in frontmatter_text.splitlines():
    line = line.strip()
    if ":" in line:
        key = line.split(":", 1)[0].strip()
        if key:
            found_keys.add(key)

for field in required_fields:
    if field not in found_keys:
        return False, f"Missing required frontmatter field '{field}' in {output_file}"
```

## Behavior

- Extracts keys by splitting on first `:` in each line
- Builds a `set` of found keys for O(1) lookup
- Returns `(False, "Missing required frontmatter field '...'")` for any missing field
- Empty values (`title: `) are accepted — key presence is sufficient

## Verification

Tests `test_missing_required_field` and `test_clean_frontmatter` confirm this behavior.
