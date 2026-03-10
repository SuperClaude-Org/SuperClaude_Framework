# D-0013: Evidence — Static-Tool Orchestration

## Test Results
- 16/16 tests passed (`tests/audit/test_tool_orchestrator.py`)
- Cache hit/miss verified: second run shows 100% cache hits for unchanged files
- Cache invalidation verified: modified file triggers re-analysis

## Cache Statistics (from test)
```
First run:  misses=3, hits=0
Second run: misses=3, hits=3, hit_rate=0.50 (cumulative)
```

## Acceptance Criteria Verification
- [x] Static tools invoked once per unique file content
- [x] Repeated runs show cache hits (verified by counter)
- [x] Structured results match expected schema
- [x] Cache invalidation on content change verified
- [x] Pipeline documented in D-0013/spec.md
