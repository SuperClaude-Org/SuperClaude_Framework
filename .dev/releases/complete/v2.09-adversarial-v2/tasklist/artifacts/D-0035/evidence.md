# D-0035: Evidence — Full Protocol Stack Validation (SC-005 through SC-009)

## Overview

Validates all protocol improvements simultaneously active in SKILL.md v2.07:
- **AD-2**: Shared Assumption Extraction (D-0011, D-0012, D-0013)
- **AD-5**: Debate Topic Taxonomy (D-0014, D-0015, D-0016)
- **AD-1**: Invariant Probe Round 2.5 (D-0028, D-0029, D-0030, D-0031)
- **AD-3**: Edge Case Scoring 6th dimension (D-0032)

## SC-005: V0.04 Variant Replay

| Bug Class | Catch Mechanism | Status |
|-----------|----------------|--------|
| Filter divergence | AD-2 shared assumption extraction (UNSTATED preconditions surfaced) + AD-1 invariant probe (state_variables/guard_conditions categories) | PASS |
| Sentinel collision | AD-5 taxonomy L3 coverage gate (blocks convergence at zero L3) + AD-1 invariant probe (collection_boundaries/interaction_effects categories) | PASS |

With all improvements active, both bug classes now have **dual-layer detection**: primary catch mechanism (AD-2/AD-5 from Phase 2) plus secondary validation via AD-1 invariant probe (Phase 4).

**SC-005 Verdict: PASS**

## SC-006: AD-2 Shared Assumption Extraction (4/4)

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-AD2-1 | UNSTATED preconditions surfaced as A-NNN | PASS | Shared assumption extraction engine with agreement_identification → assumption_enumeration → promotion |
| AC-AD2-2 | Classification: STATED/UNSTATED/CONTRADICTED | PASS | Three classification categories defined with clear criteria |
| AC-AD2-3 | Convergence denominator includes A-NNN points | PASS | `total_diff_points = count(S-NNN) + count(C-NNN) + count(X-NNN) + count(A-NNN)` |
| AC-AD2-4 | Omission flagged for unaddressed A-NNN | PASS | `[OMISSION]` flag for A-NNN points with no advocate response |

**SC-006 Verdict: PASS (4/4)**

## SC-007: AD-5 Taxonomy Coverage Gate (4/4)

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-AD5-1 | 87% convergence blocked at zero L3 coverage | PASS | `gate_condition: convergence requires (all_levels_covered == true) AND (score >= threshold) AND (no_high_unaddressed_invariants == true)` |
| AC-AD5-2 | Forced L3 round triggered when L3 has zero coverage | PASS | `forced_round_trigger` dispatches level-specific prompt |
| AC-AD5-3 | A-NNN auto-tagged L3 for state/guard/boundary terms | PASS | `shared_assumption_rule: A-NNN points containing state/guard/boundary terms auto-tag as L3` |
| AC-AD5-4 | Forced round triggers even at depth=quick | PASS | Taxonomy forced rounds exempt from depth restrictions |

**Note**: Gate condition now includes `no_high_unaddressed_invariants == true` (AD-1 integration). This is additive — does not change existing AD-5 behavior when no invariant probe runs.

**SC-007 Verdict: PASS (4/4)**

## SC-008: AD-1 Invariant Probe (4/4)

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-AD1-1 | Filter divergence detected via state_variables or guard_conditions | PASS | Fault-finder prompt probes state_variables ("State mutation ordering assumptions") and guard_conditions ("Silently swallowed error conditions") — per D-0028/evidence.md |
| AC-AD1-2 | Sentinel collision detected via collection_boundaries or interaction_effects | PASS | Fault-finder prompt probes collection_boundaries ("Implicit sort/uniqueness assumptions") and interaction_effects ("Sentinel value collisions across components") — per D-0028/evidence.md |
| AC-AD1-3 | 90% convergence with 2 HIGH UNADDRESSED items blocks convergence | PASS | `invariant_probe_gate` parses invariant-probe.md, counts HIGH+UNADDRESSED items, blocks if >0 — per D-0031/evidence.md |
| AC-AD1-4 | Round 2.5 skipped at --depth quick with log message | PASS | `skip_condition: "--depth quick → skip (log: 'Round 2.5 (invariant probe) skipped: --depth quick')"` — per D-0029/spec.md |

**SC-008 Verdict: PASS (4/4)**

## SC-009: AD-3 Edge Case Scoring (3/3)

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-AD3-1 | 24/25 variant with 0/5 edge case floor is ineligible as base | PASS | `floor_rule.threshold: "1/5"`, `enforcement: "Variants scoring <1/5 on this dimension are ineligible as base variant"` — per D-0032/evidence.md |
| AC-AD3-2 | Scoring differentiates 4/5 from 1/5 edge case coverage | PASS | `/30 formula` means 3-criterion gap = 0.10 score difference — per D-0032/evidence.md |
| AC-AD3-3 (floor suspension) | When all variants score 0/5, floor suspended with warning | PASS | `suspension: "When ALL variants score 0/5, suspend floor with warning"` — per D-0032/spec.md |

**SC-009 Verdict: PASS (3/3)**

## Combined Results

| SC | Scope | ACs Tested | Result |
|----|-------|------------|--------|
| SC-005 | V0.04 variant replay | 2 bug classes | PASS |
| SC-006 | AD-2 shared assumptions | 4/4 | PASS |
| SC-007 | AD-5 taxonomy | 4/4 | PASS |
| SC-008 | AD-1 invariant probe | 4/4 | PASS |
| SC-009 | AD-3 edge case scoring | 3/3 | PASS |

**Total: 5/5 SCs pass, 17/17 ACs pass, 0 at WARN level**

## All Improvements Active Simultaneously

Verified that all 4 protocol improvements coexist in SKILL.md without conflict:

1. **AD-2 + AD-5**: A-NNN points auto-tag as L3 (cross-reference working)
2. **AD-5 + AD-1**: Convergence gate includes `no_high_unaddressed_invariants` condition (additive gate)
3. **AD-1 + AD-3**: Invariant probe findings feed edge case coverage scoring (coverage data source)
4. **AD-2 + AD-1**: Shared assumptions provide richer probe input for fault-finder

No conflicts detected. Improvements are complementary and layered.

## Deliverable Status

- **Task**: T05.04 (originally T04.08)
- **Roadmap Item**: R-035
- **Status**: COMPLETE
- **Tier**: STANDARD
