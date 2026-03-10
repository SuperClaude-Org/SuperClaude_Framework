# Group C: Phase Contracts & Consistency -- Adversarial Verdicts

**Date**: 2026-02-26
**Mode**: Assessment (3 agents, independent perspectives)
**Depth**: Standard (2 debate rounds)
**Convergence Target**: 0.80
**Focus**: contract-clarity, minimalism, resume-safety

---

## Debate Summary

### Agent Perspectives
| Agent | Perspective | Focus Lens |
|-------|------------|------------|
| Agent 1 | Architect | Contract clarity, interoperability between independent implementers |
| Agent 2 | Refactorer | Simplicity, minimalism, avoidance of unnecessary complexity |
| Agent 3 | Security | Resume safety, data integrity, non-deterministic behavior prevention |

### Round 1: Independent Assessments

Each agent produced independent assessments. Initial alignment:

| Proposal | Agent 1 | Agent 2 | Agent 3 | Initial Agreement |
|----------|---------|---------|---------|-------------------|
| P-001 | ACCEPT | MODIFY | ACCEPT | 2/3 (66%) |
| P-002 | ACCEPT | ACCEPT | ACCEPT | 3/3 (100%) |
| P-004 | ACCEPT | ACCEPT | ACCEPT | 3/3 (100%) |
| P-005 | MODIFY | MODIFY | ACCEPT | 2/3 agree on change needed, disagree on direction |
| P-003 | ACCEPT | MODIFY | ACCEPT | 2/3 (66%) |

### Round 2: Structured Debate

**P-001 Debate**: Agent 2 (refactorer) proposed a lighter alternative: add normative cross-references from Section 3/9 to Section 17 rather than full integration. Agent 1 (architect) countered that cross-references create a "follow the pointers" reading burden and two-location maintenance. Agent 3 (security) sided with Agent 1, noting that FR-053 and FR-054 are safety controls that must be unmissable in the normative section. Agent 2 conceded but added a process constraint: the integration must be mechanical (move verbatim, then adjust numbering) to avoid introducing new inconsistencies.

**Resolution**: ACCEPT with process note. All three agents converged.

**P-005 Debate**: Three-way disagreement on directory structure.
- Agent 1 proposed `phase-3b/fix-selection.md` (clean ownership) but without migration fallback.
- Agent 2 proposed keeping `phase-3/fix-selection.md` (no new directory, simpler).
- Agent 3 preferred `phase-3b/` for resume integrity (phase ownership boundaries aid artifact validation).

Agent 1 challenged Agent 2: "If Phase 3 and Phase 3b share a directory, can the resume validator correctly determine which phase produced which artifact?" Agent 2 acknowledged this is a valid concern but argued it can be solved with naming conventions (`fix-proposal-*.md` = Phase 3, `fix-selection.md` = Phase 3b). Agent 3 countered: "Naming conventions are implicit contracts. Directory boundaries are explicit contracts. For resume safety, explicit is better." Agent 2 conceded the point conditionally: accept `phase-3b/` but drop the migration fallback since the spec is draft.

**Resolution**: MODIFY -- use `phase-3b/fix-selection.md`, update Section 12.1 directory tree, drop migration fallback. All three agents converged.

**P-003 Debate**: Agent 2 proposed avoiding `skipped_by_mode` status in favor of inferring skip from `flags.dry_run` + absent phases. Agent 3 presented a concrete resume scenario where this fails: a pipeline interrupted mid-Phase 3 also has phases 4-5 absent but `flags.dry_run` is false. The absence of phases 4-5 is ambiguous without an explicit status. Agent 1 supported Agent 3's reasoning: "The checkpoint schema must be self-describing. Relying on inference from flags creates a coupling between the status interpretation and the flag set." Agent 2 proposed a compromise: instead of a new status value, add a `skipped_phases` array to `progress.json` (e.g., `"skipped_phases": [4, 5]`). Agent 3 accepted this as equivalent in integrity value. Agent 1 accepted it as simpler than a per-phase status enum.

**Resolution**: MODIFY -- use `skipped_phases` array instead of per-phase `skipped_by_mode` status. All three agents converged.

### Final Convergence

| Proposal | Final Agreement | Convergence Score |
|----------|----------------|-------------------|
| P-001 | 3/3 ACCEPT (with process note) | 1.00 |
| P-002 | 3/3 ACCEPT | 1.00 |
| P-004 | 3/3 ACCEPT | 1.00 |
| P-005 | 3/3 MODIFY (converged) | 0.93 |
| P-003 | 3/3 MODIFY (converged) | 0.90 |

**Overall Convergence**: 0.97 (exceeds 0.80 target)

---

## Hybrid Scoring

Scoring dimensions weighted by focus areas:
- **Contract Clarity** (35%): Would two independent implementers produce interoperable artifacts?
- **Minimalism** (30%): Is this the simplest fix that resolves the inconsistency?
- **Resume Safety** (35%): Does this prevent data corruption or non-deterministic resume behavior?

### Per-Proposal Scoring Breakdown

#### PROPOSAL-001: Move panel additions into normative sections

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 6.0 | 0.30 | 1.80 |
| Resume Safety | 8.0 | 0.35 | 2.80 |
| **Composite** | | | **7.75** |

#### PROPOSAL-002: Resolve `--depth` semantic conflict

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 9.0 | 0.30 | 2.70 |
| Resume Safety | 7.0 | 0.35 | 2.45 |
| **Composite** | | | **8.30** |

#### PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 10.0 | 0.35 | 3.50 |
| Minimalism | 10.0 | 0.30 | 3.00 |
| Resume Safety | 10.0 | 0.35 | 3.50 |
| **Composite** | | | **10.00** |

#### PROPOSAL-005: Correct Phase 3b output location contract

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 8.0 | 0.35 | 2.80 |
| Minimalism | 7.0 | 0.30 | 2.10 |
| Resume Safety | 9.0 | 0.35 | 3.15 |
| **Composite** | | | **8.05** |

#### PROPOSAL-003: Normalize dry-run behavior and final report semantics

| Dimension | Score (0-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Contract Clarity | 9.0 | 0.35 | 3.15 |
| Minimalism | 7.0 | 0.30 | 2.10 |
| Resume Safety | 9.0 | 0.35 | 3.15 |
| **Composite** | | | **8.40** |

---

## Final Verdicts

### PROPOSAL-001: Move panel additions into normative sections
**Verdict: ACCEPT**
**Score: 7.75/10**
**Severity: Critical**

Integrate FR-047 through FR-055, NFR-009, NFR-010, and Schema 9.9 into their canonical normative sections (Sections 3.1, 3.2, 5.3, 7, 9, 12, 14, and Appendix A). Section 17 retains rationale text only, with each original requirement block replaced by a forward reference to its new location.

**Process constraint**: Integration must be mechanical (move content verbatim, adjust numbering) to avoid introducing new inconsistencies during the rewrite.

---

### PROPOSAL-002: Resolve `--depth` semantic conflict
**Verdict: ACCEPT**
**Score: 8.30/10**
**Severity: Major**

Add the following precedence rule to Section 5.3 (or FR-038):

> `--depth` precedence: circuit-breaker override > explicit `--depth` CLI flag > phase-specific default. Per-phase defaults (Phase 2: `deep`, Phase 3b: `standard`) apply only when `--depth` is omitted from the command.

Update Sections 7.2 and 7.4 invocation patterns to say "default: deep" / "default: standard" rather than hardcoding the depth value.

---

### PROPOSAL-004: Fix artifact path inconsistencies for adversarial outputs
**Verdict: ACCEPT**
**Score: 10.00/10**
**Severity: Major**

Standardize all references to adversarial output artifacts to use the `phase-2/` prefix:
- `phase-2/adversarial/base-selection.md`
- `phase-2/adversarial/debate-transcript.md`

Update FR-015, FR-033 (Phase 6 input list), and Section 7.7 to use the full path. No other changes required.

---

### PROPOSAL-005: Correct Phase 3b output location contract
**Verdict: MODIFY**
**Score: 8.05/10**
**Severity: Major**

**Accepted change**: Define canonical path as `phase-3b/fix-selection.md`.

**Required modifications to the proposal**:
1. Add `phase-3b/` directory to the Section 12.1 directory tree.
2. Update Section 7.4, FR-023, FR-024, and FR-033 to reference `phase-3b/fix-selection.md`.
3. **Remove** the migration fallback for legacy paths. The spec is version 1.0.0-draft with no existing implementations. Migration logic adds complexity for a non-existent concern.

**Rationale for `phase-3b/` over `phase-3/`**: Directory boundaries are explicit contracts that aid resume validation. The resume validator can determine phase ownership of artifacts by directory, eliminating ambiguity about which phase produced `fix-selection.md`. This is a net integrity gain that justifies the new directory.

---

### PROPOSAL-003: Normalize dry-run behavior and final report semantics
**Verdict: MODIFY**
**Score: 8.40/10**
**Severity: Major**

**Accepted changes**:
1. Codify dry-run phase plan: execute Phases 0 -> 1 -> 2 -> 3 -> 3b -> 6; skip Phases 4 and 5.
2. Require "would-implement" section in Phase 6 dry-run report (containing the implementation plan from fix-selection).

**Required modification to the proposal**:
3. Replace `skipped_by_mode` per-phase status with a `skipped_phases` array in `progress.json`. Example:
```json
{
  "completed_phases": [0, 1, 2, 3, "3b", 6],
  "skipped_phases": [4, 5],
  "flags": { "dry_run": true }
}
```
This is self-describing without extending the per-phase status enum. Resume logic can distinguish "skipped intentionally" (present in `skipped_phases`) from "not yet executed" (absent from both `completed_phases` and `skipped_phases`).

---

## Implementation Priority

Ordered by composite score and severity:

| Priority | Proposal | Verdict | Score | Severity |
|----------|----------|---------|-------|----------|
| 1 | P-004 | ACCEPT | 10.00 | Major (runtime file-not-found) |
| 2 | P-003 | MODIFY | 8.40 | Major (resume integrity) |
| 3 | P-002 | ACCEPT | 8.30 | Major (behavioral non-determinism) |
| 4 | P-005 | MODIFY | 8.05 | Major (resume artifact lookup) |
| 5 | P-001 | ACCEPT | 7.75 | Critical (spec authority) |

Note: P-001 is rated Critical severity but scored lowest because it is an editorial/structural fix with no runtime behavior change. Its impact is on implementer interpretation, not system execution. It should still be executed but is lower urgency than the runtime-affecting proposals.

---

## Appendix: Debate Transcript Summary

### Round 1 Positions
- **P-001**: Agent 2 proposed cross-reference alternative; Agents 1 and 3 favored full integration.
- **P-002**: Unanimous ACCEPT from the start.
- **P-004**: Unanimous ACCEPT from the start.
- **P-005**: Three different path preferences (`phase-3b/`, `phase-3/`, `phase-3b/`).
- **P-003**: Agent 2 wanted to avoid new schema status; Agents 1 and 3 wanted explicit skip tracking.

### Round 2 Resolutions
- **P-001**: Agent 2 conceded, added process constraint (mechanical move).
- **P-005**: Agent 2 conceded `phase-3b/` after Agent 3's resume integrity argument. All agreed to drop migration fallback.
- **P-003**: All converged on `skipped_phases` array as compromise between Agent 2's simplicity preference and Agent 3's integrity requirement.
