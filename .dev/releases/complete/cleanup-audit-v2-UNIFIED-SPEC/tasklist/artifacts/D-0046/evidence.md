# D-0046 Evidence: Concurrent-Run Isolation

## Test Execution

```
$ uv run pytest tests/audit/test_concurrent_isolation.py -v

tests/audit/test_concurrent_isolation.py::TestProgressIsolation::test_separate_progress_files PASSED
tests/audit/test_concurrent_isolation.py::TestProgressIsolation::test_concurrent_checkpoint_writes PASSED
tests/audit/test_concurrent_isolation.py::TestCacheIsolation::test_separate_caches PASSED
tests/audit/test_concurrent_isolation.py::TestCacheIsolation::test_cache_stats_independent PASSED
tests/audit/test_concurrent_isolation.py::TestRegistryIsolation::test_registries_on_separate_paths PASSED
tests/audit/test_concurrent_isolation.py::TestRegistryIsolation::test_match_does_not_cross_registries PASSED
tests/audit/test_concurrent_isolation.py::TestOutputIsolation::test_decomposition_deterministic PASSED
tests/audit/test_concurrent_isolation.py::TestOutputIsolation::test_batch_ids_unique_within_run PASSED

============================== 8 passed in 0.05s ==============================
```

## Concurrent-Run Comparison Results

| Aspect | Test | Result |
|--------|------|--------|
| Progress files | Independent per run | PASS |
| Concurrent writes | No corruption | PASS |
| Cache entries | Separate instances | PASS |
| Cache stats | Independent counters | PASS |
| Registries | Per-path isolation | PASS |
| Registry matching | No cross-run leakage | PASS |
| Decomposition | Deterministic output | PASS |
| Batch IDs | Unique within run | PASS |
