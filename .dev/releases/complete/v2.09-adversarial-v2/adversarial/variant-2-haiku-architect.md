# Roadmap: sc:adversarial v2.0 — Implementation-Level Bug Detection

## Overview
This roadmap upgrades `sc:adversarial` from architecture-focused debate into a state-aware verification pipeline that can detect implementation-level defects (cursor math, replay guards, boundary handling, merge artifacts). The plan is intentionally incremental: we ship the highest-ROI controls first, then layer deeper reasoning rounds, and finally add merge-specific validation. Each milestone is independently testable and releasable.

Architecturally, v2.0 adds three complementary control planes:
1) **Structural challenge** (Devil's Advocate + failure mode enumeration),
2) **State reasoning** (scenario traces + invariant declaration/challenge), and
3) **Process gating** (state coverage factor + post-merge trace validation).
This ensures defects are caught through multiple lenses rather than one debate style.

Sequencing prioritizes immediate risk reduction and low-cost safeguards early (M1/M2), followed by deeper bug-catch power (M3/M4), then breadth/novelty expansion (M5), and finally merge-integrity assurance (M6). The result is a milestone-based rollout where each step produces observable quality gains.

## Milestone Summary
| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|---|---|---|---|---|---|---|---|
| M1 | Devil's Advocate Role Integration | Role + Orchestration | P0 (Highest ROI) | M | None | D1.1–D1.3 | Medium |
| M2 | State Coverage Gate in Convergence | Scoring/Gate | P1 | S | M1 | D2.1–D2.3 | Low |
| M3 | Concrete Scenario Trace Rounds | Debate Round Engine | P1 | M-L | M1, M2 | D3.1–D3.4 | Medium |
| M4 | Invariant Declaration & Challenge | Formal Reasoning Layer | P2 | M | M3 | D4.1–D4.3 | Medium |
| M5 | Failure Mode Enumeration (Step 1.5) | Pre-Debate Analysis | P2 | M | M1, M3 | D5.1–D5.3 | Medium |
| M6 | Post-Merge Trace Validation (Step 5.5) | Validation/QA Gate | P2 | M | M2, M3, M4, M5 | D6.1–D6.4 | Medium-High |

## Dependency Graph
`M1 → M2 → M3 → M4 → M6`
`M1 → M5 → M6`
`M3 → M5`
`M2 + M3 + M4 + M5 → M6`

---

## M1: Devil's Advocate Role Integration
### Objective
Introduce a permanent non-advocacy role that actively breaks assumptions before Round 1 and blocks convergence on unresolved critical concerns.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D1.1 | New `devils_advocate` agent role contract and prompt template | Role instantiated for every run; output includes assumptions, adversarial inputs, and under-specified transitions for each variant |
| D1.2 | Orchestrator stage insertion: DA analysis before opening statements | Pipeline order validates DA stage executes pre-Round 1 in 100% of standard runs |
| D1.3 | Convergence blocker wiring for unresolved DA concerns | If DA critical concerns unresolved, convergence status marked blocked; verified by integration tests |

### Dependencies
None (foundational milestone).

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| DA output too noisy, causes false blockers | Medium | High | Severity taxonomy + blocker threshold (`critical` only blocks by default) |
| Advocate responses become performative vs substantive | Medium | Medium | Require explicit concern-to-response mapping in opening statement schema |
| Runtime increase | Low | Medium | Token/time budget cap for DA with structured output templates |

---

## M2: State Coverage Gate in Convergence
### Objective
Modify convergence scoring to require state-space coverage, preventing "agreement without execution realism."

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D2.1 | `state_coverage_factor` formula integrated into convergence calculation | Convergence score is mathematically reduced (<1.0 factor) when required categories are unaddressed |
| D2.2 | Coverage taxonomy implementation (required + conditional categories) | Required categories enforced: happy path, empty/zero, boundary. Conditional categories activate when detected |
| D2.3 | Coverage reporting in final decision output | Final report lists covered/missing categories and explicit factor value |

### Dependencies
M1 (DA helps identify missing categories and conditions early).

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Over-penalization blocks valid convergence | Low | Medium | Start with calibrated weights + tune from telemetry in first 2 sprints |
| Conditional category detection misses cases | Medium | Medium | Rule-based triggers + regression fixtures for filter/error/concurrency paths |
| Team confusion on new scoring | Medium | Low | Add score breakdown to output and docs with worked examples |

---

## M3: Concrete Scenario Trace Rounds
### Objective
Add depth-gated scenario traces where advocates step through concrete input/state transitions, surfacing divergent end states.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D3.1 | Scenario generator (3–5 scenarios from diff analysis) | Generated scenarios include happy path, boundary, and at least one adversarial/temporal/filter-transform case where applicable |
| D3.2 | New round type: `scenario_trace` (`--depth standard+`) | Round auto-included at standard/deep depth; omitted at shallow depth by design |
| D3.3 | State trace schema (state vars per step, transition rationale, end-state) | Trace outputs validate against schema; missing state fields fail validation |
| D3.4 | Divergence detector for end-state mismatch | Divergent end-states flagged as unresolved and surfaced in convergence input |

### Dependencies
M1, M2.

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Scenario quality too generic | Medium | High | Diff-driven scenario heuristics + seed templates by change type |
| Traces become too expensive in tokens/time | Medium | Medium | Depth gating + max scenario count + compact state schema |
| Advocates omit key state variables | Medium | Medium | Enforce required variable list inferred from diff and DA concerns |

---

## M4: Invariant Declaration & Challenge
### Objective
Introduce explicit correctness claims (invariants) and adversarial challenge rounds that attempt to break them.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D4.1 | Invariant declaration contract per variant | Each advocate must declare invariants with scope and assumptions; missing invariants fail pre-round validation |
| D4.2 | Challenge round where opposing advocates construct violating sequences | At least one challenge sequence per invariant class is generated and evaluated |
| D4.3 | Invariant status model (`proven`, `unproven`, `weakened`) | Violated invariants marked `unproven`; unresolved `unproven` items block final endorsement |

### Dependencies
M3 (scenario trace machinery reused for invariant test sequences).

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Invariants written too vaguely | Medium | Medium | Template requires quantifiable condition + scope + failure signal |
| Excess formalism slows routine runs | Low | Medium | Enable full challenge only at standard+ depth; lightweight mode for shallow |
| Disputes on what counts as "proven" | Medium | Medium | Define proof criteria in rubric (no violating trace across required categories) |

---

## M5: Failure Mode Enumeration (Step 1.5)
### Objective
Add mandatory pre-debate failure-mode enumeration for all variants with novelty scoring to reward unique, concrete risks.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D5.1 | Step 1.5 insertion after diff analysis | Pipeline enforces Step 1.5 before any advocacy rounds |
| D5.2 | Failure mode schema: Precondition/Trigger/Mechanism/Consequence/Detection difficulty | Each advocate provides ≥3 failure modes per variant; schema completeness checks pass |
| D5.3 | Novelty scoring and debate weight bonus | Unique failure modes receive bonus weight; duplicates de-weighted and shown in report |

### Dependencies
M1, M3 (DA signal + scenario infrastructure improve failure mode specificity).

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Redundant overlap with DA reduces value | Medium | Medium | Distinguish DA (break assumptions) vs Step 1.5 (systematic catalog + scoring) |
| Gaming novelty scoring | Medium | Medium | Semantic dedupe + minimum concreteness threshold |
| Pre-debate overhead grows | Low | Medium | Hard cap on modes and concise schema fields |

---

## M6: Post-Merge Trace Validation (Step 5.5)
### Objective
Add a fresh validation pass after merge synthesis to detect merge-introduced defects absent in individual variants.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D6.1 | New neutral validation agent (no advocacy memory) | Agent context excludes variant allegiance and prior stance metadata |
| D6.2 | Step 5.5 orchestration stage after merge candidate assembly | Pipeline runs post-merge trace before final output; failure blocks "approved" status |
| D6.3 | Scenario replay set (3–5) selected from prior unresolved/high-risk traces | At least one replay covers previously divergent or high-risk path |
| D6.4 | Merge-artifact defect report format | Report classifies defects as `merge-induced` vs `pre-existing` with trace evidence |

### Dependencies
M2, M3, M4, M5.

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Validator bias leaks from earlier stages | Low | High | Hard context isolation and separate prompt contract |
| Added cycle time delays decisions | Medium | Medium | Run only on merged candidate; cap replay count with risk-priority ordering |
| Ambiguous defect attribution | Medium | Medium | Add provenance tagging from variant-level trace IDs |

---

## Risk Register
| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R1 | Token/runtime growth from new rounds | M1–M6 | Medium | High | Depth gating, caps, compact schemas, telemetry tuning | Platform Architect |
| R2 | False blockers reduce throughput | M1, M2, M4, M6 | Medium | High | Severity tiers, blocker rubric, calibration period | Debate Orchestrator Owner |
| R3 | Inconsistent structured outputs across agents | M1, M3, M4, M5, M6 | Medium | Medium | Strict JSON/schema validation + retry policy | Prompt/Agent Engineer |
| R4 | Poor scenario generation quality | M3, M4, M6 | Medium | High | Diff-aware heuristics + curated scenario templates + regression corpus | QA Lead |
| R5 | Overlap/duplication between DA and failure mode phase | M1, M5 | Medium | Medium | Clear role boundaries, dedupe logic, scoring separation | Product Architect |
| R6 | Adoption friction due to scoring changes | M2 | Medium | Medium | Transparent score breakdown and phased rollout | Product Owner |

## Decision Summary
| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| First milestone focus | Devil's Advocate first | Scenario traces first; failure mode first | Highest ROI with immediate assumption-breaking value |
| Coverage enforcement method | Convergence multiplier (`state_coverage_factor`) | Hard boolean gate only | Preserves gradation while still penalizing blind spots |
| Trace activation | `--depth standard+` | Always-on traces | Controls cost while keeping strong default quality at standard depth |
| Invariant handling | Explicit declaration + adversarial challenge + status model | Implicit reasoning in free-form debate | Improves testability and objective correctness checks |
| Failure mode placement | Mandatory Step 1.5 after diff | Optional ad-hoc phase | Ensures consistent pre-debate risk surfacing |
| Post-merge validation model | Fresh neutral validator agent | Reuse existing advocates | Reduces advocacy bias; targets merge artifacts specifically |

## Success Criteria
| ID | Criterion | Validates Milestone(s) | Measurable |
|---|---|---|---|
| S1 | DA concerns are generated and resolved/blocked deterministically | M1 | 100% runs include DA output; blocker behavior passes integration tests |
| S2 | Convergence score reflects missing state categories | M2 | Test fixtures show score reduction when required categories absent |
| S3 | Scenario traces surface end-state divergences on seeded bug cases | M3 | Divergence detection rate improves on regression suite with known state bugs |
| S4 | Invariant violations are explicitly detected and reported | M4 | Seeded invariant-breaking inputs produce `unproven` status in >95% expected cases |
| S5 | Failure mode novelty improves breadth of identified risks | M5 | Unique high-quality failure modes per run increase vs baseline (tracked telemetry) |
| S6 | Merge-induced defects are detected before final approval | M6 | Seeded merge-artifact test cases caught in Step 5.5 before release decision |
| S7 | End-to-end quality improvement | M1–M6 | Reduction in escaped implementation-level bugs across 2 release cycles |
| S8 | Operational sustainability | M1–M6 | Median pipeline runtime remains within agreed budget after tuning |
