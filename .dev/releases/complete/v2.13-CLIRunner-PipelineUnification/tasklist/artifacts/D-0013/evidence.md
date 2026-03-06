# D-0013 Evidence: roadmap_run_step() inline embedding with 100KB guard

## Modification Summary

`roadmap_run_step()` in `src/superclaude/cli/roadmap/executor.py` now:

1. Calls `_embed_inputs(step.inputs)` to read input files into fenced code blocks
2. If `len(embedded.encode("utf-8")) <= 100 * 1024`: appends embedded content to prompt, sets `extra_args=[]` (no --file flags)
3. If embedded exceeds 100KB: logs warning and falls back to `--file` flags in `extra_args`
4. If no inputs: uses original prompt with empty `extra_args`

## Constant

```python
_EMBED_SIZE_LIMIT = 100 * 1024  # 100 KB
```

## Test Output

```
137 roadmap tests passed in 0.11s (zero regressions)
```
