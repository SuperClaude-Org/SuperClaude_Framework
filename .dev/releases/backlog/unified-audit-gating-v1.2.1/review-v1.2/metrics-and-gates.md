# Unified Audit Gating System v1.2 — Metrics and Gates

## Measurement policy
Deterministic outcomes and operational efficiency are both release-gating dimensions.

Evidence basis:
- `01-requirements-spec.md` → **Non-Functional Requirements** (deterministic pass/fail, fast task-gate runtime)
- `03-adversarial-review.md` → **Risk Register**, **Go / No-Go conditions**
- `04-design-v1.1-delta-handoff.md` → **v1.1 Delta Summary (C,D,F,G)**, **Open Items**
- `05-review-checklist.md` → **9) Risk & Reliability Controls**, **10) Readiness**

## KPI/SLO table

> Status: all numeric thresholds below are **provisional** until calibrated from Shadow mode telemetry. They become normative at Soft/Full gate approval.

| ID | Metric | Scope | Pass threshold (provisional) | Warning band | Fail gate if | Why |
|---|---|---|---|---|---|---|
| M1 | Tier-1 runtime P95 | Task | <= 8s | >8s and <=10s | >10s for 2 windows | Limits workflow drag |
| M2 | Tier-2 runtime P95 | Milestone | <= 60s | >60s and <=75s | >75s for 2 windows | Keeps milestone operations predictable |
| M3 | Tier-3 runtime P95 | Release | <= 300s | >300s and <=360s | >360s in any release window | Controls release overhead |
| M4 | Deterministic replay match rate | All tiers | 100% (Tier-1/2), >=99.5% (Tier-3) | down to 99.7% (Tier-3 only) | below threshold | Ensures reproducibility |
| M5 | Evidence completeness rate | Failed checks | 100% have path or file:line | none | any missing evidence | Enforces traceability |
| M6 | Retry amplification factor | All tiers | <=1.10 | >1.10 and <=1.25 | >1.25 | Detects instability/flapping |
| M7 | Stuck-running incident rate | All tiers | 0 unresolved > timeout SLA | 1 transient stale run recovered | any unresolved stale run | Deadlock resistance |
| M8 | False-block rate | Tier-1/2 | <1.0% (T1), <0.5% (T2) | +0.25% above pass | exceeds pass+warning for 2 windows | Reduces incorrect blocking |
| M9 | Override governance completeness | task/milestone overrides | 100% with reason code/text, actor, timestamp | none | any incomplete record | Governance reliability |
| M10 | Rollback drill success | rollout | 100% success in rehearsal | none | any failed drill | Migration safety |
| M11 | Tool/token budget conformance | all tiers | within defined tier budgets (Appendix A) | <=10% over budget | >10% over budget in 2 windows | Operational efficiency |
| M12 | Parallelization gain | Tier-2/3 | >=25% median gain vs sequential baseline (Appendix B) | 15%-25% | <15% gain | Validates efficiency objective |

## Gate thresholds by rollout phase

### Shadow mode gate
- Must collect M1-M12 for at least 2 reporting windows.
- No hard blocking on business flow; collect evidence only.

### Soft enforcement gate
- Require pass on M1, M4, M5, M7, M9.
- If any fail: remain in shadow.

### Full enforcement gate
- Require pass on all M1-M12 for 2 consecutive windows.
- Rollback drill (M10) must pass in latest window.

## Pass/fail rollout success criteria
1. Determinism stable (M4 pass).
2. Runtime stable (M1-M3 pass).
3. Reliability stable (M6-M8 pass).
4. Governance complete (M9 pass).
5. Rollback proven (M10 pass).
6. Efficiency goals met (M11-M12 pass).

## Heuristic judgments
- If M1 is missed while M4/M5 pass, prefer optimization over policy relaxation.
- If M4 or M5 fail, halt progression regardless of runtime performance.
