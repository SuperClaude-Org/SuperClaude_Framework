# Batch 5 - Adversarial Debate Artifacts (Group 1)

**Analyzed**: 2026-02-24
**Scope**: 3 adversarial pipeline artifacts from the sc:adversarial comparison process

---

## File 1: base-selection.md

**Path**: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/base-selection.md`
**Date**: 2026-02-23

### Purpose

Records the final decision from an sc:adversarial comparison of three competing approaches for headless (`claude -p`) invocation in the adversarial pipeline. Acts as the authoritative selection document that downstream implementation tasks reference.

### Content Summary

Three approaches were compared across six dimensions (Reliability, Implementation Complexity, Pipeline Fidelity, Risk Management, Maintainability, Sprint Fit):

| Approach | Combined Score | Description |
|----------|---------------|-------------|
| Approach 1 (Empirical Probe First) | 0.667 | Pre-gate validation strategy; tests whether `claude -p` works before committing to implementation |
| **Approach 2 (claude -p as Primary)** | **0.900** | Full implementation spec with `claude -p` as primary invocation and Task-agent as fallback |
| Approach 3 (Hybrid Dual-Path) | 0.825 | Dual-path architecture treating both headless and Task-agent as first-class peers |

### Key Decisions

1. **Approach 2 selected as base** -- wins on Implementation Complexity (8/10), Maintainability (8/10), Sprint Fit (9/10).
2. **Approach 3 rejected as base** despite highest Pipeline Fidelity (9/10) -- Sprint Fit (5/10) and Maintainability (5/10) disqualifying; dual-path architecture adds 40-60% more implementation work.
3. **Approach 1 reclassified** -- not a competing design but a pre-gate; its behavioral adherence rubric and multi-round verification absorbed into merged approach as Task 0.0 enhancements.
4. **Selective absorption defined** -- Approach 1's behavioral adherence testing and Approach 3's enhanced 5-step fallback with real convergence tracking absorbed into Approach 2's architecture as additive improvements (no architectural changes required).

### Cross-References

- Scoring evidence sourced from `scoring-rubric.md` (same directory)
- Debate evidence sourced from `debate-transcript.md` (same directory)
- References three source approach documents: `approach-1-empirical-probe-first.md`, `approach-2-claude-p-proposal.md`, `approach-3-hybrid-dual-path.md`
- References GitHub Issues #837 (slash commands in -p), #1048 (behavioral drift)

---

## File 2: scoring-rubric.md

**Path**: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/scoring-rubric.md`
**Date**: 2026-02-23

### Purpose

Defines and executes the hybrid scoring methodology used to produce the combined scores in `base-selection.md`. Provides full evidentiary basis for the selection decision through two scoring layers plus position-bias mitigation.

### Content Summary

**Layer 1 -- Quantitative Scoring (50% weight)**: Five weighted metrics:
- Requirement Coverage (RC, 0.30 weight)
- Internal Consistency (IC, 0.25 weight)
- Specificity Ratio (SR, 0.15 weight)
- Dependency Completeness (DC, 0.15 weight)
- Section Coverage (SC, 0.15 weight)

Results: Ap1 = 0.670, Ap2 = 0.924, Ap3 = 0.843. Each score has per-approach justification text explaining the assessment.

**Layer 2 -- Qualitative Scoring (50% weight)**: 25-criterion binary rubric across 5 dimensions (Completeness, Correctness, Structure, Clarity, Risk Coverage), 5 criteria each. Each criterion has MET/NOT MET/N/A per approach with evidence citations to specific approach document sections.

Key qualitative findings:
- Approach 1 fails Completeness (2/5) -- no command template, no fallback spec, no return contract changes
- Approach 2 scores 22/25 overall but fails two Risk Coverage criteria: behavioral instruction drift (#24) and mid-pipeline failure (#25)
- Approach 3 scores 20/25 but fails Structure criteria: no sprint-spec modification table (#12) and no implementation-ready spec text (#13)

**Position-Bias Mitigation**: Both forward and reverse scoring passes performed. Maximum delta was 0.006 (Approach 3). Final gap between top two (0.075) exceeds 5% threshold, so no tiebreaker needed.

**Final Combined Scores**: Ap1 = 0.667, Ap2 = 0.900, Ap3 = 0.825.

### Key Decisions

1. **Scoring methodology itself** -- the 50/50 quantitative-qualitative split with position-bias checking establishes the evaluation framework.
2. **Approach 2's gaps identified** -- behavioral adherence (criterion #7, #24) and mid-pipeline failure (#25) are specific deficiencies that inform what to absorb from other approaches.
3. **Approach 1's role clarified** -- high Internal Consistency (0.90) and strong Risk Coverage (4/5) but low Requirement Coverage (0.60) and Specificity Ratio (0.45) confirm it is a pre-gate, not a design.

### Cross-References

- Sections cited from approach documents (e.g., "Ap2 Section 2.2", "Ap3 Section 4", "Ap1 Section 3 T05")
- References GitHub Issues #837, #1048
- Feeds directly into `base-selection.md` combined scores

---

## File 3: debate-transcript.md

**Path**: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/adversarial/debate-transcript.md`
**Date**: 2026-02-23

### Purpose

Full transcript of the sc:adversarial Mode A debate (2 rounds + final scoring). Three advocates argue for their respective approaches, steelman opponents, identify weaknesses, make concessions, and converge on a merged resolution. This is the deliberative record that justifies the decisions in `base-selection.md`.

### Content Summary

**Round 1 -- Advocate Statements**: Each advocate presents position, steelmans both opponents, claims strengths, identifies weaknesses in others, and makes concessions.

Key Round 1 positions:
- **A1**: Probe-first is epistemically honest; 2hr/$25 to validate before 12-15hr implementation is 6-7x ROI. Concedes probe is a pre-gate, not an architecture.
- **A2**: Implementation design IS the deliverable; probe is additive cost without implementation output. Claims strongest implementation completeness (copy-paste-ready spec text, 14-row sprint-spec mapping).
- **A3**: Dual-path ensures reliability regardless of environment; mid-pipeline fallover preserves partial work. Concedes `--invocation-mode` flag may be YAGNI and dual-path doubles test surface.

**Round 2 -- Rebuttals**: Advocates respond to critiques and update positions.

Key convergence moves:
- A1 reduces probe scope from 13 tests/$25/2hr to 4-5 tests/$5-8/30-40min, proposes integration INTO Approach 2's Task 0.0
- A2 concedes behavioral adherence gap in viability probe, accepts extending Task 0.0 with adherence rubric
- A3 drops `--invocation-mode` flag, depth-based routing, and "first-class peer" framing; accepts Approach 2's primary/fallback architecture; contributes enhanced 5-step fallback

**Convergence Assessment**: 10 of 12 points resolved (0.83, exceeds 0.80 threshold).

**Final Resolution of 2 unresolved points**:
- **U-001 (Mid-pipeline fallover)**: 3-state model adopted (no artifacts -> full F1; variants present -> from F2; diff-analysis present -> from F3). Compromise between Ap2's 2-state and Ap3's 5-state.
- **U-002 (Probe scope)**: 4 tests total (~20min, ~$4). 3 mechanical + 1 behavioral adherence mini-test scoring 3 binary categories.

**Final convergence: 12/12 = 1.00**

### Key Decisions (10 resolved convergence points + 2 final resolutions)

| ID | Decision |
|----|----------|
| C-001 | Extend Task 0.0 with behavioral adherence rubric from Approach 1's T05 |
| C-002 | Upgrade fallback from 3-step (F1/F2-3/F4-5) to 5-step (F1-F5) with real convergence tracking |
| C-003 | Use primary/fallback architecture (Approach 2), not dual-path peer (Approach 3) |
| C-004 | Drop `--invocation-mode` flag (YAGNI) |
| C-005 | Drop depth-based routing (premature optimization) |
| C-006 | Add `invocation_method` field to return contract (observability) |
| C-007 | Adopt Approach 2's CLAUDECODE environment variable handling pattern |
| C-008 | Reduce full 13-test probe to 4 essential tests integrated into Task 0.0 |
| C-009 | Drop 10-run reliability test (YAGNI for sprint scope) |
| C-010 | Use Approach 2's 14-row sprint-spec modification table as implementation guide |
| U-001 | 3-state mid-pipeline fallover model (no artifacts / variants only / diff-analysis present) |
| U-002 | 4-test probe: 3 mechanical + 1 behavioral adherence (~20min, ~$4) |

### Cross-References

- Compares artifacts: `approach-1-empirical-probe-first.md`, `approach-2-claude-p-proposal.md`, `approach-3-hybrid-dual-path.md`
- References GitHub Issues #837, #1048, #1339
- Specific section citations throughout (e.g., "Ap2 Section 2.2", "Ap1 Section 3 T05", "Ap3 Section 4 F1-F5")
- Convergence decisions feed into `base-selection.md` selection rationale and absorption plan

---

## Cross-File Relationships

```
debate-transcript.md
  ├── Produces: 12 convergence decisions (C-001 through C-010, U-001, U-002)
  └── Feeds into ──► scoring-rubric.md
                        ├── Produces: Combined scores (0.667, 0.900, 0.825)
                        └── Feeds into ──► base-selection.md
                                            └── Produces: Final selection (Approach 2 + absorptions)
```

All three files reference the same three source approach documents (not in this batch) and the same GitHub issues (#837, #1048, #1339). The debate transcript provides the deliberative reasoning, the scoring rubric provides the quantitative/qualitative evidence, and the base selection provides the actionable decision with absorption plan.

## Summary of Merged Outcome

The adversarial process selected **Approach 2 (claude -p as Primary Invocation)** as the base architecture, enhanced with targeted absorptions:

- **From Approach 1**: Behavioral adherence testing integrated into Task 0.0 (4 tests, ~20min, ~$4)
- **From Approach 3**: Enhanced 5-step fallback pipeline with real convergence tracking, 3-state mid-pipeline fallover, `invocation_method` return contract field
- **Rejected from Approach 3**: `--invocation-mode` flag, depth-based routing, dual-path "first-class peer" architecture, 5-level artifact inventory
- **Rejected from Approach 1**: Full 13-test probe suite, 10-run reliability test, standalone pre-gate phase
