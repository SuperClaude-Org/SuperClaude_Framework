---
spec_source: ".dev/releases/current/2.07-adversarial-v2/brainstorm-adversarial.md"
generated: "2026-03-04T00:00:00Z"
generator: "sc:roadmap v2.0.0"
validation_philosophy: continuous-parallel
validation_milestones: 3
work_milestones: 6
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
5. The interleave ratio is **1:2** (one validation milestone per 2 work milestones), derived from complexity class **MEDIUM**

---

## Validation Milestones

| ID | After Work Milestones | Validates | Stop Criteria |
|----|----------------------|-----------|---------------|
| V1 | M1 + M2 (Devil's Advocate Agent + State Coverage Gate) | DA agent produces structured output; convergence formula modification is deterministic; DA concern resolution tracking functional | DA analysis returns no output → STOP. Coverage factor computation yields unexpected results on synthetic test case → STOP. |
| V2 | M3 + M4 (Concrete Scenario Traces + Invariant Declaration) | Scenario traces surface divergent end-states on regression inputs; D3.4 divergence detector fires correctly; M4 v0 invariants declared and marked provisional; refinement protocol runs after M3 completes | Divergence detector fails to flag known divergence in regression test → STOP. M4 v0 invariants consumed by downstream without refinement pass → STOP. |
| V3 | M5 + M6 (Failure Mode Enumeration + Post-Merge Validation) | FME enumerates ≥3 failure modes per variant; novelty scoring assigns bonus weight correctly; post-merge trace validation catches at least 1 seeded merge artifact; D6.4 provenance tagging links conclusions to source milestones | FME produces 0 novel failure modes not found by DA → STOP and review FME quality. Post-merge validator fails to detect seeded merge artifact → STOP. |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

---

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | DA agent produces no output; divergence detector misses seeded divergence; merge artifact undetected by V3 |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking downstream | FME failure mode schema missing required fields; M4 invariants not marked as v0; D6.4 provenance trace broken |
| Minor | Log, address in next validation pass | Accumulated count >5 triggers review | DA concern classification threshold requires calibration; novelty scoring boundaries need tuning; coverage report formatting issues |
| Info | Log only, no action required | N/A | Token consumption within budget; convergence rate trending positive; pipeline telemetry within expected range |

---

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | D1.1: DA output schema is machine-parseable and includes all 4 required fields (assumptions, adversarial inputs, state transitions, degenerate inputs). D1.2: DA phase executes before Round 1 in 100% of test runs. D1.3: Concern resolution matrix produced with severity classification. | All 3 deliverables verified. v0.04 regression inputs surface ≥1 critical DA concern each. |
| M2 | D2.1: Taxonomy covers all 3 required + 3 conditional categories. D2.2: Formula modification verified on 5 synthetic debates with intentionally missing categories — factor < 1.0 in all cases. D2.3: Coverage matrix present in pipeline output with blocker surfacing. | All 3 deliverables verified. Synthetic debates with uncovered required categories cannot reach convergence. `--override-coverage` escape hatch functional and logged. |
| V1 | M1 + M2 acceptance gates both pass. No Critical issues. | No Critical or >1 Major issue. |
| M3 | D3.1: Scenarios generated include all 5 required types for at least 3 test inputs. D3.2: Trace format tabular and schema-validated; divergent end-states auto-flagged. D3.3: Severity classification produces correct class for seeded divergences. D3.4: Divergence detector fires binary signal before qualitative analysis; ≥90% detection rate on injected divergences. | All 4 deliverables verified. Regression test suite (v0.04 bugs) shows detection improvement. |
| M4 | D4.1: v0 invariants produced; marked as draft; not consumed by downstream until refinement pass completes. Refinement pass demonstrates each invariant grounded in ≥1 M3 trace scenario. D4.2: Challenge round generates ≥1 violating sequence per invariant class. D4.3: Violated invariants marked "unproven"; unresolved unproven invariants block final endorsement. | All 3 deliverables verified. End-to-end test: seeded invariant-breaking inputs produce `unproven` status in ≥95% of cases. |
| V2 | M3 + M4 acceptance gates both pass. No Critical issues. | No Critical or >1 Major issue. |
| M5 | D5.1: FME enumerates ≥3 failure modes per variant; schema completeness passes. D5.2: Novelty scoring assigns bonus weight to at least 1 unique failure mode not found by DA in 80% of test runs. D5.3: DA cross-reference identifies ≥1 blind-spot warning per run on regression inputs. | All 3 deliverables verified. Exploratory-grade mode documented and upgrade pass protocol functional if activated. |
| M6 | D6.1: Validation agent context excludes prior debate history; verified by context inspection. D6.2: Step 5.5 executes before final output in 100% of test runs. D6.3: Scenario replay set includes ≥1 previously divergent path. D6.4: Provenance tagging links each post-merge conclusion to source milestone and artifact ID; cross-artifact contradiction check passes. | All 4 deliverables verified. Seeded merge-artifact test cases: 5/5 detected in Step 5.5. |
| V3 | M5 + M6 acceptance gates both pass. No Critical issues. | No Critical or >1 Major issue. |

---

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-010 (Devil's Advocate agent role) | V1 | M1 | DA output schema validation + regression inputs |
| FR-011 (DA ordering before Round 1) | V1 | M1 | Pipeline execution trace verification |
| FR-012 (DA concerns as convergence blockers) | V1 | M1 | Synthetic debate with unresolved critical concern |
| FR-013 (DA prompt engineering) | V1 | M1 | Prompt inspection + v0.04 regression test |
| FR-014 (State coverage gate formula) | V1 | M2 | Synthetic debates with intentionally missing categories |
| FR-015 (Coverage category definitions) | V1 | M2 | Category taxonomy completeness check |
| FR-016 (Coverage gate enforcement) | V1 | M2 | Convergence blocked when required category missing |
| FR-003 (Scenario traces round type) | V2 | M3 | Trace format validation + regression inputs |
| FR-004 (Scenario category requirements) | V2 | M3 | Scenario inventory check across 5 types |
| FR-005 (Diff-driven scenario selection) | V2 | M3 | Scenario relevance check against diff points |
| FR-006 (Divergent trace flagging) | V2 | M3 | D3.4 divergence detector on injected divergences |
| FR-007 (Invariant declaration) | V2 | M4 | Schema validation + v0 contract verification |
| FR-008 (Invariant challenge round) | V2 | M4 | Challenge sequence generation per invariant class |
| FR-009 (Invariant resolution) | V2 | M4 | Unproven invariants as convergence blockers |
| FR-001 (Failure mode enumeration) | V3 | M5 | Schema completeness + ≥3 failure modes per variant |
| FR-002 (Novelty scoring) | V3 | M5 | Bonus weight assignment + semantic dedup |
| FR-017 (Post-merge trace validation) | V3 | M6 | Step 5.5 execution + seeded merge-artifact detection |
| FR-018 (Fresh validation agent) | V3 | M6 | Context isolation verification |
| FR-019 (Depth-gated scenario traces) | V2 | M3 | Scenario traces absent at `--depth quick` |
| NFR-001 (Token cost containment) | V2 | M3 | Token consumption ≤40% increase at `--depth standard` |
| NFR-002 (Convergence quality gate) | V1 | M2 | State coverage factor < 1.0 when required categories missing |
| NFR-003 (Validation agent independence) | V3 | M6 | Context inspection confirms no prior debate history |
| NFR-004 (Minimum failure mode count) | V3 | M5 | ≥3 failure modes per variant per run |

---

## Regression Test Specification

**Primary regression suite**: The v0.04 post-mortem bugs serve as the canonical regression inputs. Both bugs must be caught by the enhanced pipeline.

### Regression Input 1: Index Tracking Stall

**Input**: Debate comparing variants for paginated event window rendering. Events include types that are filtered during widget creation (CondensationRequest, empty user messages).
**Expected behavior**: DA agent (M1) flags assumption "widget count from a slice equals event count in that slice." Scenario traces (M3) produce trace showing cursor stall when filtered events are present. Divergence detector (D3.4) flags cursor end-state mismatch.
**Pass condition**: At least 2 of {M1 DA flag, M3 trace divergence, M4 invariant violation} trigger on this input.

### Regression Input 2: Replay Guard Bypass

**Input**: Debate comparing variants for condensation-based replay. Conversation ending with Condensation event and no subsequent messages.
**Expected behavior**: DA agent (M1) flags assumption "after condensation, at least one tail event exists." Scenario traces (M3) produce trace showing guard evaluates false when tail is empty. M4 invariant declaration catches "after replay completes, `_replayed_event_offset > 0`" as unproven.
**Pass condition**: At least 2 of {M1 DA flag, M3 trace divergence, M4 invariant violation} trigger on this input.

---

*Generated by sc:roadmap v2.0.0 from adversarial multi-roadmap pipeline. Adversarial convergence: 79% (PARTIAL). Unresolved: X-002 M5 dependency model (62% confidence).*
