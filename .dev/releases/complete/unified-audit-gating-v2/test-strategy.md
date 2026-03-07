---
spec_source: ".dev/releases/current/unified-audit-gating-v2/unified-audit-gating-v2.0-spec.md"
generated: "2026-03-06T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 4
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:2** (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.421)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Shell & CLI Alignment) | M1 + M2: All 12 source edits correct, no residual old defaults | Any FR target file:line mismatch; any `max_turns.*50` default remaining in source |
| V2 | M4 (Documentation & Spec Alignment) | M3 + M4: Full test suite passes, documentation complete | Any test failure; missing CHANGELOG entry; spec prose still showing 0.90 |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates M1+M2 (source integrity). V2 validates M3+M4 (tests + documentation).

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Wrong default value applied; test regression in Tier 3 (no-change) tests |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing source edit; test assertion not updated; boundary validation fails |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Help text formatting inconsistency; documentation wording improvement |
| Info | Log only, no action required | N/A | DRY consolidation opportunity (RISK-008); env var override suggestion (RISK-006) |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | 7 Python source defaults changed to target values | All 7 file:line pairs verified via grep; no Critical/Major issues |
| M2 | 5 shell/CLI defaults aligned with Python layer | All 5 file:line pairs verified; zero `MAX_TURNS=50` in source scripts |
| V1 | Cross-reference all 12 FRs against targets | Each FR maps to correct value at correct location |
| M3 | 4 assertions updated + 6 new tests passing | `uv run pytest` exits 0; coverage includes new test files |
| M4 | CHANGELOG + spec prose + budget guidance | CHANGELOG matches §11 template; spec §3.1 and §3.4 corrected |
| V2 | Full suite green + integration test + regression | Zero failures; 46-task sprint budget > 0; explicit override preserved |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 | M1 | Grep: `pipeline/models.py:175` contains `max_turns: int = 100` |
| FR-002 | V1 | M1 | Grep: `sprint/models.py:285` contains `max_turns: int = 100` |
| FR-003 | V1 | M1 | Grep: `sprint/commands.py:54` contains `default=100` |
| FR-004 | V1 | M1 | Grep: `sprint/commands.py:55` contains `"default: 100"` |
| FR-005 | V1 | M1 | Grep: `sprint/config.py:108` contains `max_turns: int = 100` |
| FR-006 | V1 | M1 | Grep: `pipeline/process.py:43` contains `max_turns: int = 100` |
| FR-007 | V1 | M1 | Grep: `sprint/models.py:476` contains `reimbursement_rate: float = 0.8` |
| FR-008 | V1 | M2 | Grep: `execute-sprint.sh:47` contains `MAX_TURNS=100` |
| FR-009 | V1 | M2 | Grep: `execute-sprint.sh:14` contains `"default: 100"` |
| FR-010 | V1 | M2 | Grep: `rerun-incomplete-phases.sh:4` contains `"max_turns (100)"` |
| FR-011 | V1 | M2 | Grep: `roadmap/commands.py:75` contains `default=100` |
| FR-012 | V1 | M2 | Grep: `roadmap/commands.py:76` contains `"Default: 100"` |
| NFR-001 | V2 | M3 | Unit test: `test_budget_decay_rate_08` passes |
| NFR-002 | V2 | M3 | Mathematical proof in spec (verified by spec update in M4) |
| NFR-003 | V2 | M3 | Integration test: `test_46_task_sprint_sustainability` passes |
| NFR-004 | V2 | M3 | Unit test: timeout computation = 12,300s (existing or new) |
| NFR-005 | V2 | M4 | Documentation: 30.75h bound acknowledged in CHANGELOG |
| NFR-006 | V2 | M3 | Regression test: `test_explicit_max_turns_override` passes |
| NFR-007 | — | — | Existing test (no change required; verified by Tier 3 no-change) |
| NFR-008 | V2 | M3 | Property-based test: `test_budget_exhaustion_property` passes |

---

*Generated by sc:roadmap v2.0.0 — continuous parallel validation, 1:2 interleave ratio*
