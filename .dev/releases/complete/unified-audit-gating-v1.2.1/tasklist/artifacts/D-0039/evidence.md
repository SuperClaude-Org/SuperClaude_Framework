============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /config/workspace/SuperClaude_Framework/.venv/bin/python
cachedir: .pytest_cache
SuperClaude: 4.2.0
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
hypothesis profile 'default'
rootdir: /config/workspace/SuperClaude_Framework
configfile: pyproject.toml
plugins: superclaude-4.2.0, benchmark-5.2.3, anyio-4.12.1, hypothesis-6.151.9, cov-7.0.0
collecting ... collected 15 items

tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_grace_period_zero_is_default_across_all_configs PASSED [  6%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_default_gate_mode_is_blocking PASSED [ 13%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_resolve_gate_mode_all_scopes_blocking_when_grace_zero PASSED [ 20%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_zero_daemon_threads_grace_period_zero PASSED [ 26%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_no_trailing_runner_created_when_grace_zero PASSED [ 33%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_per_task_no_ledger_v121_behavior PASSED [ 40%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_sprint_result_format_v121_equivalence PASSED [ 46%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_phase_status_priority_chain_preserved PASSED [ 53%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_budget_guard_none_ledger_always_allows PASSED [ 60%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_aggregated_report_format_backward_compatible PASSED [ 66%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_gate_passed_tier_behavior_preserved PASSED [ 73%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_execution_log_format_v121 PASSED [ 80%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_task_result_context_summary_format PASSED [ 86%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_enum_values_backward_compatible PASSED [ 93%]
tests/sprint/test_backward_compat_regression.py::TestBackwardCompatRegression::test_sprint_config_path_helpers_unchanged PASSED [100%]

============================== 15 passed in 2.24s ==============================
