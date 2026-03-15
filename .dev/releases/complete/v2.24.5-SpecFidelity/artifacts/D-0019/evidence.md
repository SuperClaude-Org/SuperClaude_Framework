# D-0019 Evidence — Rename test_100kb_guard_fallback to test_embed_size_guard_fallback

## Task
T04.01 — Rename `test_100kb_guard_fallback` to `test_embed_size_guard_fallback`
in `tests/roadmap/test_file_passing.py`

## Verification Result: PASS (pre-existing)

The rename was completed in a prior phase session before this Phase 4 execution.
This evidence file documents the verification that the rename is fully in place.

## Acceptance Criteria Check

| Criterion | Status | Evidence |
|---|---|---|
| `test_embed_size_guard_fallback` exists in `tests/roadmap/test_file_passing.py` | PASS | Line 108 of the file |
| `test_100kb_guard_fallback` no longer exists in the file | PASS | Grep returned no matches in `.py` files |
| File parses without syntax errors | PASS | `python -c "import ast; ast.parse(...)"` → SYNTAX OK |

## Diff (state at verification)

```diff
--- a/tests/roadmap/test_file_passing.py (pre-rename, historical)
+++ b/tests/roadmap/test_file_passing.py (current)
 class TestEmbedSizeGuardFallback:
     """Scenario 3: _EMBED_SIZE_LIMIT (120 KB) guard triggers fallback to --file flags."""

-    def test_100kb_guard_fallback(self, tmp_path: Path, caplog):
+    def test_embed_size_guard_fallback(self, tmp_path: Path, caplog):
         """Verify that composed prompt exceeding _EMBED_SIZE_LIMIT falls back to --file flags."""
```

## Grep Verification

Command: `grep -r "test_100kb_guard_fallback" --include="*.py"`
Result: No matches found in Python source files.

Command: `grep -n "test_embed_size_guard_fallback" tests/roadmap/test_file_passing.py`
Result: Line 108 — `def test_embed_size_guard_fallback(self, tmp_path: Path, caplog):`

## Note on Historical References

The old name `test_100kb_guard_fallback` still appears in 25 `.md` and `.txt` release
planning/documentation files. This is expected and correct — those are historical
references in roadmap specs and prior sprint outputs. The spec's acceptance criteria
only required the old name to be absent from `tests/roadmap/test_file_passing.py`.
