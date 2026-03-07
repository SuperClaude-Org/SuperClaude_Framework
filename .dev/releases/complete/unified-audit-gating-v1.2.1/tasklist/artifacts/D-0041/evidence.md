============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /config/workspace/SuperClaude_Framework/.venv/bin/python
cachedir: .pytest_cache
SuperClaude: 4.2.0
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
hypothesis profile 'default'
rootdir: /config/workspace/SuperClaude_Framework
configfile: pyproject.toml
plugins: superclaude-4.2.0, benchmark-5.2.3, anyio-4.12.1, hypothesis-6.151.9, cov-7.0.0
collecting ... collected 7 items

tests/sprint/test_nfr_benchmarks.py::TestNFRGatePerformance::test_gate_evaluation_100kb_under_50ms PASSED [ 14%]
tests/sprint/test_nfr_benchmarks.py::TestNFRGatePerformance::test_gate_evaluation_deterministic PASSED [ 28%]
tests/sprint/test_nfr_benchmarks.py::TestNFRTurnLedgerConstantTime::test_debit_constant_time PASSED [ 42%]
tests/sprint/test_nfr_benchmarks.py::TestNFRTurnLedgerConstantTime::test_credit_constant_time PASSED [ 57%]
tests/sprint/test_nfr_benchmarks.py::TestNFRTurnLedgerConstantTime::test_available_constant_time PASSED [ 71%]
tests/sprint/test_nfr_benchmarks.py::TestNFRTurnLedgerConstantTime::test_can_launch_constant_time PASSED [ 85%]
tests/sprint/test_nfr_benchmarks.py::TestNFRTurnLedgerConstantTime::test_operation_timing_absolute PASSED [100%]

============================== 7 passed in 0.15s ===============================
