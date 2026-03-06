---
spec_source: docs/generated/unified-audit-gating-v1.2.1-release-spec.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 3
work_milestones: 3
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation
## Unified Audit Gating System v1.2.1

---

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:2** (one validation milestone per two work milestones), derived from complexity class **MEDIUM** (score 0.654)

**This feature is itself a gating mechanism.** The audit gating system controls task, milestone, and release completions. Any gap in validation coverage of illegal transitions, override governance failures, or rollback triggers becomes a production escape path. Validation cannot be deferred — it must be concurrent with implementation.

**The four current blockers (profile thresholds, retry/backoff/timeout, rollback triggers, unassigned owners) make certain tests non-deterministic until M1 closes.** Validation milestones below reflect this dependency: V1 cannot certify blocker-dependent test quality until M1 deliverables are signed off.

---

## Validation Milestones

Interleave ratio 1:2 over 6 work milestones → 3 validation milestones (V1, V2, V3).

| ID | After Work Milestones | Validates | Stop Criteria |
|----|----------------------|-----------|---------------|
| V1 | M1, M2 | Blocker closure quality; state machine correctness; closed-world enforcement; compile-time release prohibition; no sprint CLI regression from M2 changes | Any illegal transition not blocked; OverrideRecord accepts release scope at construction; sprint tests regress; blocker documents contain [TBD] fields |
| V2 | M3, M4 | Evaluator determinism; profile correctness; override governance completeness; fault-injection suite results; deadlock-resistance argument | Profile non-determinism; release override reachable; any single required OverrideRecord field not enforced; fault-injection suite fails; deadlock path identified |
| V3 | M5, M6 | Sprint CLI regression gate (zero regressions); rollout phase promotion quality; rollback drill results; Soft-to-Full gate sign-off completeness | Any regression in tests/sprint/; rollback drill fails or incomplete; Soft-to-Full promotion missing required signatories; any open NO-GO criteria from spec Section 12.2 |

**Placement rule**: V1 after M2, V2 after M4, V3 after M6. Each validation milestone references the specific work milestones it validates by M# ID.

---

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Release override path reachable; state machine bypass confirmed; non-deterministic evaluator detected; sprint CLI executor crash |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing required field in OverrideRecord validation; illegal transition not caught by validator; retry budget not enforced; blocker document still has [TBD] fields |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Test assertion using hard-coded threshold value instead of parameterized fixture; documentation gap in SKILL.md; incomplete risk mitigation in Risk Register |
| Info | Log only, no action required | N/A | Optimization opportunity in evaluator; alternative approach noted for post-v1.2.1 consideration |

---

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | D1.1-D1.5 documents exist, version-controlled, owner+deadline assigned, zero [TBD] fields | All 5 deliverable documents complete and signed; decision registry in PASS state for checklist section 10 |
| M2 | 17 legal + 6 illegal transition tests pass; closed-world test passes; compile-time prohibition test passes; no sprint regression | CI reports: 17/17 legal, 6/6 illegal, 1/1 closed-world, 1/1 compile-time; test_regression_gaps.py passes |
| M3 | 9 determinism assertions pass; major-severity behavior tests pass; evidence completeness tests pass; strictness alias tests pass | 9/9 determinism, all profile tests pass, zero failed checks with empty evidence_refs |
| M4 | 11+ override field tests pass; release override adversarial test passes; fault-injection 4/4 pass; deadlock property test (10K sequences) terminates | All override tests green; M4-D7 asserts allowed=False; fault scenarios produce clean transitions; all 10K sequences terminate |
| M5 | Baseline established before M2; zero new failures post-M2/M4 merge; backward-compatibility assertions pass | tests/sprint/ failing count = 0; PhaseStatus/SprintOutcome values unchanged |
| M6 (Sub-Phase A) | Two shadow windows complete; KPI report approved; provisional thresholds confirmed or revised; Shadow-to-Soft sign-off obtained | KPI report exists with required metrics; D6.9 signed by policy owner + program manager; Sub-Phase B not started until D6.9 signed |
| M6 (Sub-Phase B) | Soft/Full mode tests pass; 5 rollback trigger tests pass; rollback drill documented with pass verdict; Soft-to-Full sign-off obtained | D6.2-D6.4 green in CI; D6.8 drill log attached; D6.10 signed by 3 named approvers; no open NO-GO criteria |

---

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 Block task completion unless gate passes | V1, V2 | M2, M4 | validate_transition returns allowed=False for bypass; tui.py guard test |
| FR-002 Block milestone completion | V1, V2 | M2, M4 | Same pattern as FR-001 for milestone scope |
| FR-003 Block release unless gate passes | V1, V2 | M2, M4 | Release guard hard stop test; D4.2 acceptance criteria |
| FR-004 Configurable profile behavior | V2 | M3 | Profile determinism tests (D3.4); strictness-to-profile mapping (D3.8) |
| FR-005 Tier-1 gate required for LIGHT/EXEMPT | V3 | M6 | Full mode test (D6.3) asserts Tier-1 fires even for LIGHT/EXEMPT |
| FR-006 Release override forbidden | V1, V2 | M2, M4 | D2.8 compile-time prohibition; D4.7 adversarial valid-record test |
| FR-007 Single command interface /sc:audit-gate | V2 | M3 | Command SKILL.md acceptance criteria (D3.2) |
| FR-008 Explicit audit_* states | V1 | M2 | State enum test (D2.1) asserts all 6 states per scope exist |
| FR-009 --profile canonical; --strictness alias at shadow/soft | V2, V3 | M3, M6 | D3.8 alias tests; D6.5 deprecation path test |
| FR-010 Legal/illegal transition table authoritative | V1 | M2 | 17 legal + 6 illegal tests; closed-world test (D2.2) |
| FR-011 Task scope legal transitions | V1 | M2 | 6 task-scope legal transition tests |
| FR-012 Milestone scope legal transitions | V1 | M2 | 6 milestone-scope legal transition tests |
| FR-013 audit_release_failed → released forbidden | V1, V2 | M2, M4 | D2.4 illegal transition test #5; D4.7 adversarial test |
| FR-014 Illegal transitions enforced | V1 | M2 | D2.4 all 6 illegal transition classes |
| FR-015 Lease + heartbeat; missing heartbeat → failed(timeout) | V2 | M4 | D4.1 heartbeat timeout test; D4.10 parametrized timeout path |
| FR-016 Retry bounded by per-scope budget; exhaustion blocks | V1, V2 | M2, M4 | D2.5 retry budget exhaustion; D4.10 exhaustion assertion |
| FR-017 Runtime policy resolver consumes profile | V2 | M3 | Profile determinism (D3.4); evaluator contract (D3.1) |
| FR-018 GateResult required fields | V2 | M3 | D3.3 schema conformance test; all 14 required fields verified |
| FR-019 OverrideRecord required fields | V2 | M4 | D4.6 eleven field-absence tests; D4.4 validation enforcement |
| FR-020 GateTransitionEvent + GateCheckEvent schemas | V2 | M4 | D4.11 correlation ID propagation test |
| FR-021 Versioning policy; evaluator rejects unsupported major | V2 | M3 | D3.6 unsupported schema version → failed(unknown) |
| FR-022 Shadow/Soft/Full rollout phases | V3 | M6 | D6.1, D6.2, D6.3 mode-specific tests |
| FR-023 Shadow→Soft promotion criteria | V3 | M6 | D6.9 sign-off checklist confirms M1/M4/M5/M7/M9 equivalent gates |
| FR-024 Soft→Full promotion criteria (2 windows + drill) | V3 | M6 | D6.10 sign-off with drill log; D6.6 two-window KPI report |
| FR-025 Rollback triggers (5 normative triggers) | V3 | M6 | D6.4 five rollback trigger tests |
| FR-026 Rollback order full→soft→shadow; safe-disable | V3 | M6 | D6.8 rollback drill validates order; artifact retention verified |
| FR-027 Sprint CLI transition blocking | V1, V2 | M2, M4 | D2.6 tui.py guard test; D4.2 release guard test |
| FR-028 models.py audit states/enums | V1 | M2 | D2.1 enum test |
| FR-029 tui.py completion/release guards | V1, V2 | M2, M4 | D2.6, D4.2, D4.3 guard tests |
| FR-030 Phase 0: design/policy lock | V1 | M1 | D1.1-D1.5 documents signed |
| FR-031 Phase 1: contracts + evaluator + validator | V1, V2 | M2, M3 | State machine tests; evaluator SKILL.md |
| FR-032 Phase 2: runtime controls | V2 | M4 | D4.1, D4.12, D4.13 runtime control deliverables |
| FR-033 Phase 3: CLI + override governance + persistence | V2 | M4 | D4.2-D4.11 override test suite |
| FR-034 Phase 4: rollout + KPI gates + rollback drills | V3 | M6 | D6.1-D6.10 rollout deliverables |
| NFR-001 Deterministic pass/fail (replay stability) | V2 | M3 | D3.4 nine determinism assertions |
| NFR-002 Evidence completeness: file path or file:line | V2 | M3 | D3.7 evidence completeness tests |
| NFR-003 Fail-safe: unknown/missing inputs → failed | V2 | M3 | D3.6 unknown/missing input tests |
| NFR-004 Timeout/retry semantics: deadlock-resistant | V2 | M4 | D4.13 property-based test; D4.12 fault-injection suite |
| NFR-005 KPI thresholds provisional until calibration | V3 | M6 | D6.7 threshold calibration and normative promotion |
| NFR-006 Checklist sections 2,3,4,6,7 must fully pass | V3 | M6 | D6.10 sign-off confirmation of checklist status |
| NFR-007 All blocking decisions: owner+UTC deadline+phase | V1 | M1 | D1.4 decision registry with zero [TBD] |
| NFR-008 Override approval metadata complete | V2 | M4 | D4.6 field-absence tests; D4.4 all-or-nothing validation |
| NFR-009 Drift summary: edited vs non-edited | V2 | M3 | D3.7 drift_summary field test |
| NFR-010 KPI calibration: two shadow windows | V3 | M6 | D6.6 two-window KPI report |

---

## Stop-and-Fix Thresholds by Severity

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Critical issue found | Any occurrence (0 tolerance) | Stop all work immediately; block next milestone start until resolved |
| Major issue found | >1 occurrence OR any blocking dependency | Stop work on affected deliverable; fix before proceeding to next milestone |
| Minor issue accumulation | >5 accumulated minors without resolution | Trigger review session; resolve before next validation milestone |
| V1 gate fails | Any V1 gate criterion not met | Do not begin M3; fix M1/M2 issues first |
| V2 gate fails | Any V2 gate criterion not met | Do not begin M5; fix M3/M4 issues first |
| V3 gate fails | Any V3 gate criterion not met | No Soft-to-Full promotion; fix M5/M6 issues first |
| Rollback drill fails | D6.8 pass verdict not obtained | D6.10 sign-off cannot proceed; fix drill issues before promotion |
| Non-determinism detected | Any evaluator replay stability failure | Stop shadow deployment; investigate before continuing |
