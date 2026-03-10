# D-0014 Evidence: Integration tests for roadmap file-passing

## Test File

`tests/roadmap/test_file_passing.py` — 3 integration test scenarios

## Test Output

```
tests/roadmap/test_file_passing.py::TestPromptContainsEmbeddedContent::test_prompt_contains_embedded_content PASSED
tests/roadmap/test_file_passing.py::TestPathsWithSpaces::test_paths_with_spaces PASSED
tests/roadmap/test_file_passing.py::TestSizeGuardFallback::test_100kb_guard_fallback PASSED
3 passed in 0.04s
```

## Scenario Details

1. **test_prompt_contains_embedded_content**: Verifies prompt string includes fenced code blocks with file content; extra_args is empty (no --file flags)
2. **test_paths_with_spaces**: Verifies paths containing spaces are embedded correctly in the prompt
3. **test_100kb_guard_fallback**: Verifies >100KB input falls back to --file flags; warning logged; prompt does not contain large content
