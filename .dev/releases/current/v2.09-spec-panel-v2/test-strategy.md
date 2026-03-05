---
spec_source: ".dev/releases/current/v2.06-spec-panel-v2/spec-panel-release-spec.md"
generated: "2026-03-04T00:00:00Z"
generator: "sc:roadmap"
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 5
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
5. The interleave ratio is **1:2** (one validation milestone per two work milestones), derived from complexity class **MEDIUM** (score 0.561)

This release has 5 work milestones (M1, M2, M3, M5, M6) and 2 validation milestones (M4/Gate A, M7/Gate B), yielding a 2:1 work-to-validation ratio — correct for MEDIUM complexity.

---

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (Gate A / M4) | M3 (Guard Condition Boundary Table complete) | Phase 1 adversarial persona + Phase 2 boundary table; v0.04 run correctness; overhead budget | Any of: Whittaker findings absent from qualifying review; boundary table not blocking synthesis; cumulative overhead ≥25% |
| V2 (Gate B / M7) | M5 (Correctness Focus Mode) + M6 (Pipeline Analysis) | Full system integration; all 5 integration points; all success metrics | Any of: overhead ≥25% (standard) or ≥40% (correctness focus); formulaic entries ≥50%; missing integration point output; no GAP cells on guarded spec |

**Placement rule**: Validation milestones placed after every 2 work milestones per 1:2 interleave ratio. Gate A (M4) validates M1+M2+M3. Gate B (M7) validates M5+M6 (and confirms cumulative system behavior).

---

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Boundary table not blocking synthesis when incomplete; Whittaker findings absent from review run; dimensional mismatch not flagged CRITICAL |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Cumulative overhead exceeds gate budget; GAP cells not auto-generating findings; auto-suggest false positive rate ≥30% |
| Minor | Log, address in next validation pass | Accumulated count >5 triggers review | Missing provenance annotation in downstream format; minor wording in persona definition; non-blocking format deviation |
| Info | Log only, no action required | N/A | Alternative attack methodology wording; optimization opportunity in table format |

---

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 (Persona Definition) | Persona YAML follows existing structure; 5 attack methodologies documented; output format template present; boundaries count updated to 11 | All D1.1–D1.4 ACs met; no Critical/Major issues |
| M2 (Panel Integration) | Whittaker in every review run (post-Fowler/Nygard); overhead ≤10% on 2 representative specs; no regressions | All D2.1–D2.4 ACs met; no Critical/Major issues |
| M3 (Boundary Table) | 7-column table template; GAP/blank rules enforced as hard gates; synthesis blocking verified; trigger detection working | All D3.1–D3.7 ACs met; synthesis block demonstrated on test case |
| M4 / Gate A | v0.04 run logs show complete Whittaker + boundary table output; cumulative overhead <25%; explicit Phase 3 sign-off | All D4.1–D4.3 ACs met; overhead measurement passes |
| M5 (Correctness Focus) | `--focus correctness` activates 5-expert panel; all 3 mandatory outputs present; auto-suggest FP <30%; overhead ≤25% above standard | All D5.1–D5.7 ACs met; no Critical/Major issues |
| M6 (Pipeline Analysis) | Pipeline trigger fires on 2+ stage specs; CRITICAL severity on mismatches; overhead <5% (no pipelines) / ≤10% (with pipelines) | All D6.1–D6.6 ACs met; no Critical/Major issues |
| M7 / Gate B | All 5 integration points produce parseable output; all success metrics pass; go/no-go decision with rollback plan documented | All D7.1–D7.7 ACs met; explicit release authorization |

---

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (Whittaker persona) | V1 (Gate A) | M4 | v0.04 run log confirms persona present and active |
| FR-002 (5 attack methodologies) | V1 (Gate A) | M4 | Manual check: all 5 methodologies appear in run output |
| FR-003 (Attack finding format) | V1 (Gate A) | M4 | Format regex: "I can break this by…Invariant at…fails when…Concrete:" |
| FR-004 (Activation in all focus areas) | V2 (Gate B) | M7 | Run spec-panel with each focus area; confirm Whittaker present |
| FR-005 (Review order) | V1 (Gate A) | M4 | Verify Whittaker section appears after Fowler and Nygard in output |
| FR-006 (Boundary table trigger) | V1 (Gate A) | M4 | Run on spec with guards; confirm table generated |
| FR-007 (7-column / 6-row format) | V1 (Gate A) | M4 | Parse output; verify column count and row count per guard |
| FR-008 (GAP → MAJOR severity) | V1 (Gate A) | M4 | Inject GAP cell in test; verify MAJOR finding generated |
| FR-009 (Blank behavior → MAJOR) | V1 (Gate A) | M4 | Inject blank Specified Behavior cell; verify MAJOR finding |
| FR-010 (Synthesis blocking) | V1 (Gate A) | M4 | Submit incomplete table; verify synthesis output absent |
| FR-011 (Expert role assignments) | V1 (Gate A) | M4 | Run on guarded spec; verify Nygard lead, Crispin validation, Whittaker attacks present |
| FR-012 (--focus correctness flag) | V2 (Gate B) | M7 | Run `/sc:spec-panel @spec --focus correctness`; confirm output present |
| FR-013 (5-expert correctness panel) | V2 (Gate B) | M7 | Parse output; exactly Nygard+Fowler+Adzic+Crispin+Whittaker |
| FR-014.1–FR-014.6 (Modified behaviors) | V2 (Gate B) | M7 | Per-expert behavior delta verified in correctness-focus run |
| FR-015 (3 mandatory outputs) | V2 (Gate B) | M7 | State Variable Registry + Boundary Table + Pipeline Flow Diagram all present |
| FR-016 (Auto-suggest heuristic) | V2 (Gate B) | M7 | Test with 3+ mutable vars spec, guarded spec, pipeline spec; confirm suggestion fires; measure FP rate |
| FR-017 (Pipeline trigger) | V2 (Gate B) | M7 | Run on 2-stage filter spec; confirm heuristic activates |
| FR-018 (4-step process) | V2 (Gate B) | M7 | All 4 steps (Detection, Annotation, Tracing, Check) present in output |
| FR-019 (CRITICAL for mismatches) | V2 (Gate B) | M7 | Inject dimensional mismatch; verify CRITICAL finding |
| FR-020 (Fowler leads, Whittaker attacks) | V2 (Gate B) | M7 | Role attribution in pipeline output |
| FR-021 (Quantity Flow Diagram) | V2 (Gate B) | M7 | Diagram present with counts at each stage |
| NFR-001 (≤10% overhead for SP-2) | V1 (Gate A) | M4 | Token count comparison on v0.04 |
| NFR-004 (≤10% overhead for SP-3) | V1 (Gate A) | M4 | Token count comparison; cumulative ≤20% |
| NFR-007 (≤25% overhead correctness focus) | V2 (Gate B) | M7 | Token count comparison with/without `--focus correctness` |
| NFR-008 (<30% FP rate auto-suggest) | V2 (Gate B) | M7 | Run on benchmark set; count false positive triggers |
| NFR-009 (<5% overhead no pipelines) | V2 (Gate B) | M7 | Token count on non-pipeline spec with pipeline heuristic active |
| NFR-010 (≤10% overhead with pipelines) | V2 (Gate B) | M7 | Token count on pipeline spec |
