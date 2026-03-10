# D-0045 Evidence: Benchmark Results

## Test Execution

```
$ uv run pytest tests/audit/test_benchmark.py -v

tests/audit/test_benchmark.py::TestBenchmarkSmallRepo::test_small_repo_completes_without_errors PASSED
tests/audit/test_benchmark.py::TestBenchmarkSmallRepo::test_small_repo_report_completeness PASSED
tests/audit/test_benchmark.py::TestBenchmarkSmallRepo::test_small_repo_profiling PASSED
tests/audit/test_benchmark.py::TestBenchmarkMediumRepo::test_medium_repo_completes_without_errors PASSED
tests/audit/test_benchmark.py::TestBenchmarkMediumRepo::test_medium_repo_budget_estimation PASSED
tests/audit/test_benchmark.py::TestBenchmarkMediumRepo::test_medium_repo_coverage_tracking PASSED
tests/audit/test_benchmark.py::TestBenchmarkDeadCodeRepo::test_dead_code_detection_accuracy PASSED
tests/audit/test_benchmark.py::TestBenchmarkDeadCodeRepo::test_dead_code_no_false_positives_on_live PASSED
tests/audit/test_benchmark.py::TestBenchmarkDeadCodeRepo::test_dead_code_exclusion_rules PASSED

============================== 9 passed in 0.05s ==============================
```

## Benchmark Metric Tables

| Tier | Metric | Result |
|------|--------|--------|
| Small | Completes | Yes |
| Small | Token estimate | >0 |
| Small | Profile all files | Yes |
| Medium | Completes | Yes |
| Medium | Token estimate | >0 |
| Medium | Coverage 100+ | Yes |
| Dead Code | Detection >= 80% | Yes |
| Dead Code | FP on entry points | 0 |
| Dead Code | Exclusion reasons | All present |
