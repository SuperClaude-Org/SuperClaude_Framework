# D-0014: Fix embed guard to measure composed string

## Task: T03.03

**Status**: PASS

## Diff

```diff
-    embedded = _embed_inputs(step.inputs)
-    if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
-        effective_prompt = step.prompt + "\n\n" + embedded
-        extra_args: list[str] = []
-    elif embedded:
-        _log.warning(
-            "Step '%s': embedded inputs exceed %d bytes, falling back to --file flags",
-            step.id,
-            _EMBED_SIZE_LIMIT,
-        )
-        effective_prompt = step.prompt
-        extra_args = [
-            arg
-            for input_path in step.inputs
-            for arg in ("--file", str(input_path))
-        ]
+    embedded = _embed_inputs(step.inputs)
+    if embedded:
+        composed = step.prompt + "\n\n" + embedded
+        # <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB
+        if len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
+            effective_prompt = composed
+            extra_args: list[str] = []
+        else:
+            _log.warning(
+                "Step '%s': composed prompt exceeds %d bytes, falling back to --file flags",
+                step.id,
+                _EMBED_SIZE_LIMIT,
+            )
+            effective_prompt = step.prompt
+            extra_args = [
+                arg
+                for input_path in step.inputs
+                for arg in ("--file", str(input_path))
+            ]
```

## Verification

```
$ uv run pytest tests/roadmap/test_file_passing.py -v
6 passed in 0.10s
```

- Guard evaluates `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` ✅
- `composed = step.prompt + "\n\n" + embedded` used as measurement target ✅
- Verbatim comment `# <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB` present ✅
- Warning log reports "composed prompt" and byte count ✅
