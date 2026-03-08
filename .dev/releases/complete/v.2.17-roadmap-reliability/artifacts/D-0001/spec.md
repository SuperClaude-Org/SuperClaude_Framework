# D-0001: Regex-based `_check_frontmatter()` Implementation

## Summary

Replaced the byte-0 `startswith("---")` check in `_check_frontmatter()` with a compiled `re.MULTILINE` regex that discovers YAML frontmatter anywhere in the document.

## Regex Pattern

```python
_FRONTMATTER_RE = re.compile(
    r"^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$",
    re.MULTILINE,
)
```

## Key Design Decisions

- **`re.MULTILINE`**: `^` anchors to line beginnings, not byte 0, allowing preamble before `---`
- **`.search()` over `.match()`**: Finds frontmatter anywhere in the document
- **Compiled regex**: `_FRONTMATTER_RE` is module-level for performance (compiled once)

## File Modified

`src/superclaude/cli/pipeline/gates.py` — lines 72-75 (regex), lines 78-108 (function)

## Verification

- All 18 pre-existing tests pass (backward compatibility confirmed)
- 8 new spec §6.1 tests pass
- Full suite: 2070 passed, 1 pre-existing failure (unrelated credential scanner test)
