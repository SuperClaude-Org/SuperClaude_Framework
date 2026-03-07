# D-0037 Evidence — KPI Report for Gate and Remediation Metrics

## Deliverable
KPI report generated after sprint completion containing: trailing gate latency (p50, p95), remediation frequency, conflict review rate, gate pass/fail distribution.

## Files Modified
- `src/superclaude/cli/sprint/kpi.py` — New module: GateKPIReport dataclass + build_kpi_report() aggregation function
- `tests/sprint/test_kpi_report.py` — 16 tests covering report properties, aggregation, and formatting

## Test Results
```
uv run pytest tests/sprint/test_kpi_report.py -v
16 passed in 0.05s
```

## Acceptance Criteria Verification
- [x] KPI report includes: gate latency (p50, p95), remediation frequency, conflict review rate
- [x] Metrics are accurate (verified against known test inputs with predetermined values)
- [x] Report generated after sprint completion (build_kpi_report takes gate results as input, not runtime state)
- [x] `uv run pytest tests/sprint/ -k kpi_report` exits 0
