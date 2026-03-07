============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /config/workspace/SuperClaude_Framework/.venv/bin/python
cachedir: .pytest_cache
SuperClaude: 4.2.0
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
hypothesis profile 'default'
rootdir: /config/workspace/SuperClaude_Framework
configfile: pyproject.toml
plugins: superclaude-4.2.0, benchmark-5.2.3, anyio-4.12.1, hypothesis-6.151.9, cov-7.0.0
collecting ... collected 11 items

tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_multi_task_sprint_with_trailing_gates PASSED [  9%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_budget_accounting_identity PASSED [ 18%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_no_silent_incompletion_error_max_turns PASSED [ 27%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_budget_exhaustion_skips_remaining PASSED [ 36%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_trailing_gate_remediation_and_context PASSED [ 45%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_gate_mode_resolution_with_grace_period PASSED [ 54%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_mixed_outcomes_comprehensive PASSED [ 63%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_halt_produces_resume_output_and_diagnostic PASSED [ 72%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_conflict_review_passthrough PASSED [ 81%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_phase_report_formats PASSED [ 90%]
tests/sprint/test_e2e_trailing.py::TestE2ETrailingGates::test_remediation_log_persistence PASSED [100%]

============================== 11 passed in 0.13s ==============================
