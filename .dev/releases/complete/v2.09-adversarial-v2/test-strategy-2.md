---
spec_sources:
  - .dev/releases/current/2.07-adversarial-v2/05-adversarial2.0-final-refactor-spec.md
  - .dev/releases/current/2.07-adversarial-v2/adversarial-release-spec.md
generated: "2026-03-04T00:00:00Z"
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
5. The interleave ratio is **1:2** (one validation milestone per two work milestones), derived from complexity class **MEDIUM** (score: 0.690)

**Dual-track coordination**: This release has two parallel implementation tracks (Meta-Orchestrator / Track A and Protocol Quality / Track B). Validation must verify both tracks independently and then verify their integration. V1 gates after M2+M3 (Track A foundation + Track B Phase 1 independently complete). V2 gates after M4+M5 (full integration).

**Backward compatibility is a hard gate**: Any regression in Mode A/B behavior causes an immediate stop regardless of issue severity. The existing 5-step pipeline must be provably unchanged at every validation milestone.

---

## Validation Milestones

| ID | After Work Milestones | Validates | Stop Criteria |
|----|----------------------|-----------|---------------|
| V1 | M2 (DAG Builder), M3 (Protocol Phase 1) | Backward compat regression; Track A DAG correctness; Track B AD-2/AD-5 correctness; M3 overhead budget | Any regression in Mode A/B output; Step 1 overhead >10%; AC-AD2 or AC-AD5 acceptance scenarios fail |
| V2 | M4 (Phase Execution Engine), M5 (Protocol Phase 2) | End-to-end canonical pipeline; full protocol stack (all 4 improvements active); total overhead budget; final backward compat check | Canonical 8-step pipeline fails; total overhead >40%; any regression in Mode A/B; AC-AD1 or AC-AD3 acceptance scenarios fail |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates M2+M3, V2 validates M4+M5.

---

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Mode A/B regression; backward compat violation; NFR-001/002/003 violated |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | AC acceptance scenario failure; overhead >15% per component; SKILL.md merge conflict unresolved |
| Minor | Log, address in next validation pass | Accumulated count >5 triggers review | Sub-optimal structured table format; edge case in dry-run output formatting; non-blocking convergence formula discrepancy |
| Info | Log only, no action required | N/A | AD-3 edge case floor suspension note; plateau detection false positive with low-quality synthetic variants |

---

## Acceptance Gates

### V1 Gate (after M2 + M3)

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M2 | All D2.1-D2.6 acceptance criteria met; dry-run output matches execution plan (SC-002) | 6/6 deliverables pass their ACs; 0 Critical, 0 Major issues |
| M3 | All D3.1-D3.6 acceptance criteria met; v0.04 regression replay passes (SC-005) | 6/6 deliverables pass their ACs; overhead ≤10% (NFR-004); SC-005/SC-006/SC-007 pass |
| Backward Compat | All D1.2 baseline Mode A/B invocations produce unchanged output | 100% baseline invocations pass (zero regressions) |

### V2 Gate (after M4 + M5)

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M4 | All D4.1-D4.8 acceptance criteria met; end-to-end canonical pipeline (SC-001, SC-003, SC-004) | 8/8 deliverables pass their ACs; 0 Critical, 0 Major issues |
| M5 | All D5.1-D5.6 acceptance criteria met; invariant probe/scoring (SC-008, SC-009) | 6/6 deliverables pass their ACs; SC-008/SC-009 pass |
| Full Stack | SC-010 overhead ≤40%; all 10 success criteria pass (or ≤1 at WARN) | Total overhead measured ≤40%; ≥9/10 success criteria pass |
| Final Backward Compat | All D1.2 baseline invocations produce unchanged output with final SKILL.md | 100% baseline invocations pass (zero regressions) |

---

## Validation Coverage Matrix

### Functional Requirements Coverage

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (`--pipeline` flag detection) | V1.1 (backward compat) | M2 | Existing invocations unchanged; pipeline flag routes to correct branch |
| FR-002 (inline shorthand parser) | V1 (D2.1 AC) | M2 | Parse all Spec1 examples; reject malformed syntax |
| FR-003 (YAML pipeline loader) | V1 (D2.2 AC) | M2 | Load 3-phase YAML; reject invalid schemas |
| FR-004 (DAG builder) | V1 (D2.3-D2.5 ACs) | M2 | Cycle detection test; reference integrity test |
| FR-005 (Phase Executor) | V2 (D4.1 AC) | M4 | Single-phase output == direct Mode A/B invocation |
| FR-006 (phase-scoped dirs + manifest) | V2 (D4.4 AC) | M4 | 3-phase pipeline produces correct directory structure and manifest |
| FR-007 (DAG scheduler + parallel) | V2 (D4.3 AC) | M4 | 2-phase parallel generate produces correct artifacts without race conditions |
| FR-008 (dry-run) | V1 (D2.6 AC), SC-002 | M2 | Dry-run output matches actual for canonical workflow |
| FR-009 (blind mode) | V2 (D4.6 AC), SC-003 | M4 | Zero model-name references in `--blind` merged output |
| FR-010 (plateau detection) | V2 (D4.7 AC), SC-004 | M4 | Synthetic plateau scenario triggers warning + halt |
| FR-011 (pipeline resume) | V2 (D4.5 AC) | M4 | Resume from phase 2 skips completed phase 1 (checksum valid) |
| FR-012 (`--pipeline-parallel N`) | V2 (D4.3 AC) | M4 | Concurrent phases capped at N |
| FR-013 (error policy continue) | V2 (D4.8 AC) | M4 | Failed phase dependents skipped; parallel branches unaffected |
| FR-014 (shared assumption extraction) | V1 (D3.1 AC), SC-006 | M3 | AC-AD2-1: 3-variant 1:1 mapping → UNSTATED precondition surfaced |
| FR-015 (synthetic diff points) | V1 (D3.2 AC), SC-006 | M3 | AC-AD2-3: convergence denominator includes A-NNN points |
| FR-016 (advocate prompt update) | V1 (D3.3 AC), SC-006 | M3 | AC-AD2-4: omitted shared assumption responses flagged |
| FR-017 (debate topic taxonomy) | V1 (D3.4 AC), SC-007 | M3 | Auto-tag signals produce correct L1/L2/L3 assignments |
| FR-018 (taxonomy convergence gate) | V1 (D3.5 AC), SC-007 | M3 | AC-AD5-1: 87% convergence blocked with zero L3 coverage |
| FR-019 (forced round) | V1 (D3.5 AC), SC-007 | M3 | AC-AD5-2: forced round produces scored diff points; AC-AD5-4: triggers at depth=quick |
| FR-020 (invariant probe round) | V2 (D5.2 AC), SC-008 | M5 | AC-AD1-1/AC-AD1-2: probe identifies filter divergence and sentinel collision |
| FR-021 (invariant convergence gate) | V2 (D5.4 AC), SC-008 | M5 | AC-AD1-3: 2 HIGH UNADDRESSED items block 90% convergence |
| FR-022 (edge case scoring dimension) | V2 (D5.5 AC), SC-009 | M5 | AC-AD3-2: 4/5 vs 1/5 scoring differentiation |
| FR-023 (edge case floor) | V2 (D5.5 AC), SC-009 | M5 | AC-AD3-1: 0/5 variant ineligible as base |
| FR-024 (return contract extension) | V2 (D5.6 AC) | M5 | `unaddressed_invariants` present in return contract; existing fields unchanged |

### Non-Functional Requirements Coverage

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| NFR-001 (zero pipeline changes) | V1, V2 backward compat | M2, M4 | D1.2 baseline invocations pass unchanged at both validation points |
| NFR-002 (zero Mode A/B changes) | V1, V2 backward compat | M2, M4 | Mode A and Mode B direct invocations produce unchanged output |
| NFR-003 (zero return contract removals) | V2 (D5.6 AC) | M5 | All existing return contract fields present; only additions made |
| NFR-004 (Step 1 overhead ≤10%) | V1 overhead measurement | M3 | Timed comparison of Step 1 with and without AD-2 on identical input |
| NFR-005 (debate overhead ≤15%) | V2 full stack measurement | M5 | Timed comparison of full debate with and without Round 2.5 |
| NFR-006 (scoring overhead ≤3%) | V2 full stack measurement | M5 | Timed comparison of scoring step with 5 vs 6 dimensions |
| NFR-007 (total overhead ≤40%) | V2 (SC-010) | V2 | End-to-end timing comparison pre/post v2.07 on standardized input |
| NFR-008 (structured table format) | V1 (D3.2 AC), V2 (D5.3 AC) | M3, M5 | Verify diff-analysis.md and invariant-probe.md use table format |
| NFR-009 (checklist extensibility) | V2 (D5.1 review) | M5 | Verify adding a 6th checklist category requires only data addition, not structural change |
| NFR-010 (blind mode zero leakage) | V2 (D4.6 AC), SC-003 | M4 | Grep merged output for model-name strings (opus, haiku, sonnet, gpt); expect zero matches |

---

## Stop-and-Fix Thresholds

The following conditions cause **immediate work stoppage** regardless of milestone progress:

1. **Backward compatibility regression**: Any Mode A or Mode B baseline invocation produces different output than the D1.2 documented baseline → STOP, investigate root cause, restore to documented behavior before proceeding
2. **NFR-001/002/003 violation**: Any change found in the existing 5-step pipeline, Mode A/B code paths, or existing return contract fields → STOP, revert the change
3. **SC-001 canonical pipeline failure after M4**: End-to-end 8-step workflow does not complete successfully → STOP, debug artifact routing or phase execution
4. **NFR-007 overhead ceiling breach**: Total measured overhead >40% at V2 → STOP, profile per-component overhead, consider deferring AD-3 (lowest priority, lowest impact) if overhead budget is consumed by AD-2+AD-5+AD-1

The following conditions cause **milestone-level stop** before advancing to the next milestone:

5. **Acceptance scenario suite failure**: If fewer than 6/8 acceptance criteria (AC-AD2 through AC-AD5) pass at V1 → fix before advancing to M4
6. **Overhead budget exceeded per component**: If M3 additions push Step 1 overhead >10% at V1 → optimize before adding AD-1 (M5/D5.1 would push it further)
