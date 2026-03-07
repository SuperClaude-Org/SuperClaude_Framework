# D-0002: error_max_turns NDJSON Detection Evidence

## Deliverable
`detect_error_max_turns()` function in `src/superclaude/cli/sprint/monitor.py`

## Implementation
- Added `ERROR_MAX_TURNS_PATTERN` regex for `"subtype":"error_max_turns"`
- Added `detect_error_max_turns(output_path)` function that scans last NDJSON line
- Returns `True` when last non-empty line contains the pattern, `False` otherwise
- Handles edge cases: missing file, empty output, truncated NDJSON

## Test Results
```
uv run pytest tests/sprint/test_monitor.py -k DetectErrorMaxTurns -v
8 passed in 0.04s
```

## Acceptance Criteria Verification
- [x] Returns True when last NDJSON line contains `"subtype":"error_max_turns"`
- [x] No false positives on success, failure, or other error subtypes
- [x] Handles edge cases: empty output, truncated NDJSON, missing file
- [x] Function has inline docstring
