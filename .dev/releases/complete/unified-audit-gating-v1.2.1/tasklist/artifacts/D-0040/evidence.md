============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /config/workspace/SuperClaude_Framework/.venv/bin/python
cachedir: .pytest_cache
SuperClaude: 4.2.0
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
hypothesis profile 'default'
rootdir: /config/workspace/SuperClaude_Framework
configfile: pyproject.toml
plugins: superclaude-4.2.0, benchmark-5.2.3, anyio-4.12.1, hypothesis-6.151.9, cov-7.0.0
collecting ... collected 14 items

tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_consumed_never_decreases PASSED [  7%]
tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_accounting_identity_holds PASSED [ 14%]
tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_consumed_equals_sum_of_debits PASSED [ 21%]
tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_reimbursed_equals_sum_of_credits PASSED [ 28%]
tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_negative_debit_raises PASSED [ 35%]
tests/sprint/test_property_based.py::TestPropertyBudgetMonotonicity::test_negative_credit_raises PASSED [ 42%]
tests/sprint/test_property_based.py::TestPropertyGateResultOrdering::test_drain_returns_all_submitted PASSED [ 50%]
tests/sprint/test_property_based.py::TestPropertyGateResultOrdering::test_fifo_ordering_preserved PASSED [ 57%]
tests/sprint/test_property_based.py::TestPropertyGateResultOrdering::test_concurrent_put_no_loss PASSED [ 64%]
tests/sprint/test_property_based.py::TestPropertyGateResultOrdering::test_drain_then_empty PASSED [ 71%]
tests/sprint/test_property_based.py::TestPropertyRemediationIdempotency::test_double_mark_remediated_idempotent PASSED [ 78%]
tests/sprint/test_property_based.py::TestPropertyRemediationIdempotency::test_remediate_preserves_other_entries PASSED [ 85%]
tests/sprint/test_property_based.py::TestPropertyRemediationIdempotency::test_serialize_deserialize_roundtrip PASSED [ 92%]
tests/sprint/test_property_based.py::TestPropertyRemediationIdempotency::test_mark_nonexistent_returns_false PASSED [100%]

============================== 14 passed in 2.19s ==============================
