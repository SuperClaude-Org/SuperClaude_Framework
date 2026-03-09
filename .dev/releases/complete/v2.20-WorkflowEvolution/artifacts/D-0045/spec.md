---
deliverable: D-0045
task: T05.09
status: PASS
date: 2026-03-09
---

# Monitoring Metrics Definition

## Metric 1: False Positive Rate

| Property | Value |
|----------|-------|
| **Definition** | Percentage of gate failures on artifacts that are actually correct |
| **Measurement** | Count gate failures on known-good artifacts / total gate checks |
| **Alert Threshold** | >5% false positive rate per gate |
| **Data Source** | Gate validation logs, historical replay results |
| **Frequency** | Per release cycle |

## Metric 2: Degraded-Run Frequency

| Property | Value |
|----------|-------|
| **Definition** | Percentage of validation runs that produce DEGRADED status |
| **Measurement** | Count DEGRADED outcomes / total validation runs |
| **Alert Threshold** | >15% degraded runs in a 30-day window |
| **Data Source** | Validation executor output logs |
| **Frequency** | Rolling 30-day window |

## Metric 3: Pipeline Time Drift

| Property | Value |
|----------|-------|
| **Definition** | Change in total pipeline execution time (excluding spec-fidelity) |
| **Measurement** | (new_time - baseline_time) / baseline_time * 100 |
| **Alert Threshold** | >5% overhead (SC-012) |
| **Data Source** | Pipeline executor timing data |
| **Frequency** | Per release cycle |

## Metric 4: LLM Severity Drift

| Property | Value |
|----------|-------|
| **Definition** | Change in distribution of HIGH/MEDIUM/LOW severities across runs |
| **Measurement** | Compare severity distribution against baseline from v2.19 |
| **Alert Threshold** | HIGH severity count increases >50% vs baseline |
| **Data Source** | Spec-fidelity and tasklist-fidelity deviation reports |
| **Frequency** | Per release cycle |
