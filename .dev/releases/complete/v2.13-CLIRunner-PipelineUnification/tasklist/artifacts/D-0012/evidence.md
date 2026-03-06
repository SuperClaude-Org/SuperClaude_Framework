# D-0012 Evidence: _embed_inputs() helper

## Function Signature

```python
def _embed_inputs(input_paths: list[Path]) -> str:
```

Located at `src/superclaude/cli/roadmap/executor.py` line 56.

## Behavior
- Empty list → returns empty string (no-op)
- Non-empty list → reads each file, wraps in fenced code block with `# <path>` header
- Returns concatenated blocks separated by double newlines

## Test Output

```
tests/roadmap/test_embed_inputs.py::TestEmbedInputs::test_empty_list_returns_empty_string PASSED
tests/roadmap/test_embed_inputs.py::TestEmbedInputs::test_single_file_produces_fenced_block PASSED
tests/roadmap/test_embed_inputs.py::TestEmbedInputs::test_multiple_files_produce_multiple_blocks PASSED
tests/roadmap/test_embed_inputs.py::TestEmbedInputs::test_path_header_format PASSED
4 passed in 0.04s
```
