======================================================================
  v2.01 Release Validation Report
======================================================================
  Runs:          1
  Models:        haiku
  Data points:   13 (5 structural + 8 behavioral)

STRUCTURAL TESTS
----------------------------------------------------------------------
  S1 lint-architecture         0/1  ░░░░░░░░░░░░░░░░░░░░  0%
  S2 verify-sync               1/1  ████████████████████  100%
  S3 stale-references          1/1  ████████████████████  100%
  S4 task-unified-size         1/1  ████████████████████  100%
  S5 frontmatter               1/1  ████████████████████  100%

  Structural aggregate: 80.0%

TIER CLASSIFICATION — By Model
----------------------------------------------------------------------
                 haiku      Mean
  B1      0.15±0.00    0.15
  B2      0.00±0.00    0.00
  B3      0.00±0.00    0.00
  B4      0.00±0.00    0.00

  Classification aggregate: 3.8%

SKILL WIRING — By Model
----------------------------------------------------------------------
                 haiku      Mean
  W1      0.79±0.00    0.79
  W2      0.15±0.00    0.15
  W3      0.15±0.00    0.15
  W4      0.62±0.00    0.62

  Wiring aggregate: 42.8%

MODEL COMPARISON
----------------------------------------------------------------------
     haiku:  Mean 23.3%  Std 30.4%  Min 0%  Max 79%

PER-RUN BREAKDOWN
----------------------------------------------------------------------
  Run 1: 45.1% overall  (structural: 80%, behavioral: 23.3%)

AGGREGATE VERDICT
======================================================================
  Overall mean:         45.1%
  Structural:           80.0%
  Behavioral mean:      23.3%
  Best model:           haiku (23.3%)
  Cross-model std:      0.0%
  Worst per-test min:   0%

  ❌ Structural = 100%: FAIL
  ❌ Behavioral (any model) >= 80%: FAIL
  ❌ Behavioral (best model) >= 90%: FAIL
  ✅ Cross-model std <= 15%: PASS
  ❌ Per-test minimum >= 50%: FAIL

  VERDICT: RELEASE NOT APPROVED ❌
  Review failing thresholds above and address issues.

======================================================================