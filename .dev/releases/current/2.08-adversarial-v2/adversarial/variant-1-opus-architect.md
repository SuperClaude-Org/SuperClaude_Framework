# Roadmap: sc:adversarial v2.0 — Implementation-Level Bug Detection

## Overview

This roadmap addresses a structural gap in the sc:adversarial debate pipeline: the absence of operational state analysis. The current pipeline operates at the design abstraction layer, comparing architectural approaches without ever grounding debate in concrete data flow, state transitions, or failure mode enumeration. Two bugs that escaped adversarial review in the v0.04 Adaptive Replay post-mortem share a common root cause — no debater was prompted to trace concrete data through the proposed state machine. This roadmap phases six proposals into a coherent implementation plan that closes that gap.

The architectural approach is layered integration. Rather than rebuilding the pipeline, we inject new phases and roles into the existing orchestration flow. The four highest-synergy proposals — Devil's Advocate (P4), State Coverage Gate (P5), Concrete Scenario Traces (P2), and Invariant Challenge (P3) — form the core unit and are phased across the first four milestones in dependency order. The Devil's Advocate role is foundational: it produces the adversarial analysis that Scenario Traces ground in concrete values, that Invariant Challenge formalizes into correctness claims, and that the State Coverage Gate enforces as a convergence condition. Failure Mode Enumeration (P1) and Post-Merge Trace Validation (P6) are positioned as later milestones that extend coverage without disrupting the core unit.

A key architectural decision is that the Devil's Advocate agent is stateless across debates but persistent within a single pipeline run. It produces analysis before Round 1, receives advocate responses, and issues a final unresolved-concerns report that feeds the convergence formula. This avoids introducing cross-session state complexity while maximizing the agent's ability to identify gaps. All new pipeline phases are designed as composable middleware — each can be enabled, disabled, or depth-gated independently via the existing `--depth` flag hierarchy.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Devil's Advocate Agent | Foundation | P0 — Critical | Medium | None | D1.1, D1.2, D1.3 | Medium |
| M2 | State Coverage Gate | Process Gate | P0 — Critical | Low | M1 | D2.1, D2.2, D2.3 | Low |
| M3 | Concrete Scenario Traces | Analysis Phase | P1 — High | High | M1, M2 | D3.1, D3.2, D3.3 | Medium |
| M4 | Invariant Declaration and Challenge | Formal Reasoning | P1 — High | Medium | M1 | D4.1, D4.2, D4.3 | Medium |
| M5 | Failure Mode Enumeration Phase | Enumeration Phase | P2 — Standard | Low | M1, M4 | D5.1, D5.2, D5.3 | Low |
| M6 | Post-Merge Trace Validation | Validation Phase | P2 — Standard | Medium | M3 | D6.1, D6.2, D6.3 | Low |

## Dependency Graph

```
M1 (Devil's Advocate)
├──→ M2 (State Coverage Gate)
│    └──→ M3 (Scenario Traces)
├──→ M3 (Scenario Traces)
├──→ M4 (Invariant Challenge)
│    └──→ M5 (Failure Mode Enumeration)
└──→ M5 (Failure Mode Enumeration)

M3 (Scenario Traces)
└──→ M6 (Post-Merge Trace Validation)
```

Linearized critical path: **M1 → M2 → M3 → M6**, with **M4** parallelizable after M1, and **M5** parallelizable after M4.

---

## M1: Devil's Advocate Agent

### Objective

Introduce a permanent, non-advocacy agent role into the adversarial debate pipeline. The Devil's Advocate (DA) operates before Round 1, identifying assumptions, constructing adversarial inputs, flagging under-specified state transitions, and enumerating degenerate inputs for every variant. This is the foundational component — all subsequent milestones depend on the DA's analysis artifacts.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | DA agent prompt template and role specification | Agent produces structured analysis covering: (a) assumptions per variant, (b) adversarial input constructions, (c) under-specified state transitions, (d) degenerate input enumeration. Output schema is machine-parseable. |
| D1.2 | Pipeline orchestration integration — DA phase inserted before Round 1 | DA analysis is available to all advocates before opening statements. Advocates must explicitly address DA concerns (enforced by orchestrator). Unresolved DA concerns are tagged as convergence blockers in the pipeline state. |
| D1.3 | DA concern resolution tracking and final report | Pipeline produces a DA concern resolution matrix at debate conclusion. Each concern is marked resolved, partially-resolved, or unresolved. Unresolved concerns block convergence (feeds M2). |

### Dependencies

None. M1 is the root of the dependency graph.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DA analysis is too generic / shallow to catch implementation-level bugs | Medium | High | Prompt engineering iteration with v0.04 post-mortem bugs as regression tests. DA prompt must require concrete state variable references, not abstract claims. |
| DA produces excessive false positives, slowing debate | Medium | Medium | Introduce a relevance scoring mechanism. Advocates can challenge DA concerns as out-of-scope; orchestrator adjudicates. Cap initial DA concerns at 10 per variant. |
| DA role increases token consumption beyond budget | Low | Medium | DA analysis is bounded by output schema. Monitor token usage in first 5 pipeline runs. Apply `--depth` gating if needed. |

---

## M2: State Coverage Gate

### Objective

Modify the convergence formula to include a state coverage factor, ensuring the debate cannot converge without addressing required scenario categories. This transforms the DA's concerns and scenario coverage from advisory to enforceable.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | State coverage category taxonomy and classification logic | Required categories defined: happy path, empty/zero inputs, boundary conditions. Conditional categories defined: filter divergence, error paths, concurrent/reentrant. Classification logic maps debate points to categories. |
| D2.2 | Modified convergence formula: `convergence = (agreed_points / total_diff_points) * state_coverage_factor` | `state_coverage_factor` is < 1.0 when any required category is unaddressed. Factor computation is deterministic and auditable. Convergence threshold cannot be met without all required categories covered. |
| D2.3 | Coverage gap reporting in pipeline output | Pipeline output includes a coverage matrix showing which categories are addressed, partially addressed, or missing. Missing required categories are surfaced as explicit blockers with suggested remediation. |

### Dependencies

- **M1**: The DA's concern taxonomy feeds the state coverage categories. DA unresolved concerns reduce the coverage factor.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Coverage gate is too strict, preventing convergence on legitimate debates | Low | High | Provide an `--override-coverage` escape hatch (logged and auditable). Tune factor weights based on first 10 pipeline runs. |
| Category taxonomy is incomplete, missing real-world failure classes | Medium | Medium | Taxonomy is extensible by design. Conduct quarterly reviews against escaped bugs. |

---

## M3: Concrete Scenario Traces

### Objective

Add a Scenario Traces debate round type where each advocate traces concrete input scenarios step-by-step, showing state variable values at each transition. This grounds the debate in operational reality and exposes divergent end-states that abstract discussion misses.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Scenario generation engine — orchestrator produces 3-5 concrete input scenarios from diff analysis | Scenarios cover: happy path, boundary conditions, filter/transform scenarios, temporal edge cases, adversarial inputs (sourced from DA analysis in M1). Scenarios include concrete input values, not abstract descriptions. |
| D3.2 | Trace execution protocol — each advocate traces each scenario step-by-step | Trace output includes state variable values at each step. Format is tabular (step / state variable / value per variant). Divergent end-states are automatically flagged as unresolved divergences. |
| D3.3 | Divergence analysis and integration with convergence formula | Unresolved divergences feed into the state coverage factor (M2). Divergences are classified by severity (data loss, incorrect output, stall, crash). Severity classification influences convergence penalty. |

### Dependencies

- **M1**: DA adversarial inputs are a primary source for scenario generation.
- **M2**: Divergence analysis feeds the state coverage factor.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scenario traces are token-expensive, blowing pipeline budget on complex diffs | Medium | High | Gate scenario traces behind `--depth standard` or deeper. Limit to 3 scenarios at standard depth, 5 at deep. Implement early-exit when all scenarios converge. |
| Advocates produce inconsistent trace formats, making automated divergence detection unreliable | Medium | Medium | Enforce a strict trace output schema. Orchestrator validates format before divergence analysis. Reject malformed traces with re-prompt. |

---

## M4: Invariant Declaration and Challenge

### Objective

Introduce a formal reasoning discipline where each advocate declares the invariants their design relies upon, and opposing advocates (plus the DA) attempt to construct input sequences that violate those invariants. This makes correctness claims explicit and testable.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Invariant declaration protocol and schema | Each advocate declares invariants in a structured format: (name, formal statement, scope, assumed preconditions). Invariants are machine-parseable. Minimum 2 invariants per variant enforced by orchestrator. |
| D4.2 | Challenge round implementation | Opposing advocates and DA construct input sequences targeting declared invariants. Challenge output format: (target invariant, input sequence, expected violation, trace). Violated invariants are flagged as "unproven." |
| D4.3 | Invariant resolution and design modification protocol | Advocates with violated invariants must either (a) modify their design to restore the invariant or (b) weaken the invariant and accept the consequence. Unresolved violated invariants are convergence blockers. Resolution decisions are logged in the pipeline output. |

### Dependencies

- **M1**: DA participates in challenge rounds and sources challenge inputs from its pre-Round-1 analysis.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Advocates declare trivially true invariants to avoid challenge | Medium | Medium | DA is tasked with evaluating invariant strength. Trivial invariants (always true by construction) are rejected by orchestrator with re-prompt for substantive invariants. |
| Invariant formalization is too demanding for non-formal advocates | Low | Medium | Provide invariant templates with examples. Accept natural-language invariants with structured preconditions. Formalization is aspirational, not blocking. |

---

## M5: Failure Mode Enumeration Phase

### Objective

Add Step 1.5 between Diff Analysis and Adversarial Debate where each advocate enumerates concrete failure modes per variant. This overlaps with the DA role (M1) but provides advocate-perspective failure analysis that the DA can cross-reference against its own findings.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | Failure mode enumeration prompt and output schema | Each advocate enumerates >=3 failure modes per variant (including their own). Schema: Precondition / Trigger / Mechanism / Consequence / Detection difficulty. |
| D5.2 | Novelty scoring for failure mode findings | Unique failure modes (not identified by DA or other advocates) earn bonus debate weight. Novelty is determined by semantic similarity against DA analysis and other advocate enumerations. |
| D5.3 | Integration with DA analysis — cross-reference and gap detection | DA cross-references advocate failure modes against its own analysis. Gaps (failure modes found by DA but not by any advocate) are surfaced as blind-spot warnings. |

### Dependencies

- **M1**: DA analysis is the baseline for novelty scoring and cross-reference.
- **M4**: Invariant declarations inform failure mode enumeration (failure modes that violate declared invariants are higher priority).

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Redundancy with DA analysis makes Step 1.5 low-value | Low | Low | Novelty scoring ensures incremental value. If post-deployment metrics show <10% novel findings over 20 runs, consider merging into DA phase. |

---

## M6: Post-Merge Trace Validation

### Objective

Introduce a fresh validation agent (Step 5.5) that traces scenarios through the merged solution. This agent has no advocacy bias and catches merge artifacts — bugs introduced by the synthesis process itself that were not present in any individual variant.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Post-merge validation agent prompt and role specification | Agent is distinct from all debate participants. Agent receives merged solution and original scenarios (from M3) but not debate history. Agent traces 3-5 scenarios through merged solution independently. |
| D6.2 | Merge artifact detection and classification | Agent compares its trace results against the expected end-states from M3 scenario traces. Divergences are classified as merge artifacts. Merge artifacts are reported with: source scenario, expected state, actual state, root cause hypothesis. |
| D6.3 | Pipeline integration — Step 5.5 insertion and convergence impact | Merge artifacts discovered in Step 5.5 reopen the debate with artifact-specific focus. If >0 critical merge artifacts found, merged solution is rejected and debate re-enters with artifact constraints. Pipeline output includes merge validation report. |

### Dependencies

- **M3**: Scenario traces provide the baseline scenarios and expected end-states for post-merge validation.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Post-merge validation agent duplicates scenario trace work without finding new bugs | Low | Low | Monitor merge artifact discovery rate. If <5% of runs find merge artifacts after 30 runs, make Step 5.5 conditional on merge complexity score. |
| Reopening debate after merge artifact discovery creates unbounded iteration | Low | High | Cap merge-artifact re-debate to 1 iteration. If artifacts persist after re-merge, escalate to human review with full trace evidence. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R1 | Token budget overrun from added pipeline phases | M1, M3, M5 | Medium | High | Depth-gating (`--depth` flag controls which phases activate). Token budget monitoring per phase with early-exit. | Pipeline Architect |
| R2 | DA produces shallow or generic analysis that fails to catch implementation-level bugs | M1, M2, M3, M4 | Medium | High | Regression test suite using v0.04 post-mortem bugs. DA prompt requires concrete state variable references. Quarterly prompt refinement cycle. | DA Prompt Owner |
| R3 | Convergence gate (M2) is too strict, causing legitimate debates to stall | M2, M3 | Low | High | `--override-coverage` escape hatch with audit log. Factor weight tuning based on first 10 runs. | Pipeline Architect |
| R4 | Scenario trace format inconsistency breaks automated divergence detection | M3, M6 | Medium | Medium | Strict output schema enforcement. Orchestrator validates before analysis. Malformed traces trigger re-prompt. | Orchestrator Owner |
| R5 | Invariant declarations are gamed (trivially true invariants) | M4 | Medium | Medium | DA evaluates invariant strength. Trivial invariants rejected with re-prompt. | DA Prompt Owner |
| R6 | Merge-artifact re-debate creates unbounded iteration loops | M6 | Low | High | Cap re-debate to 1 iteration. Escalate to human review if artifacts persist. | Pipeline Architect |
| R7 | Phasing complexity — later milestones depend on stable M1 interfaces | M2, M3, M4, M5 | Medium | Medium | Define DA output schema as a versioned contract in M1. Schema changes require backward compatibility or migration. | Pipeline Architect |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|
| DA agent lifecycle | Stateless across debates, persistent within a single pipeline run | (a) Fully stateless per phase, (b) Cross-session persistent DA | Single-run persistence lets DA track concern resolution without cross-session state complexity. Avoids stale concern carryover. |
| Convergence formula modification | Multiplicative state_coverage_factor | (a) Additive bonus for coverage, (b) Hard gate (binary pass/fail) | Multiplicative factor degrades gracefully — partial coverage reduces but does not eliminate convergence. Hard gate was too brittle for early adoption. |
| Scenario trace depth gating | Gated at `--depth standard` and deeper | (a) Always-on, (b) Only at `--depth deep` | Standard depth is the most common usage. Gating below standard loses the primary bug-catch benefit. Always-on is too expensive for shallow/quick runs. |
| Failure Mode Enumeration positioning | Step 1.5 (before debate), integrated with DA | (a) Replace DA with enumeration, (b) Post-debate enumeration | Pre-debate enumeration feeds DA cross-reference. Replacing DA loses the permanent adversarial role. Post-debate is too late to influence discussion. |
| Post-merge validation agent isolation | No access to debate history | (a) Full debate context, (b) Summary-only context | No debate history eliminates confirmation bias. The agent must find bugs from the merged artifact alone, simulating a fresh reviewer. |
| M4/M5 dependency ordering | M5 depends on M4 (invariants inform failure modes) | (a) M5 independent of M4, (b) M5 before M4 | Invariant declarations provide a formal frame for failure mode enumeration. Failure modes that violate declared invariants are architecturally more significant. |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|------------------------|------------|
| SC1 | DA analysis identifies >=1 concrete implementation-level concern per pipeline run (measured over 20 runs) | M1 | Yes — count DA concerns with concrete state variable references per run. Target: mean >= 1.0. |
| SC2 | v0.04 post-mortem bugs (index tracking stall, replay guard bypass) are caught by the enhanced pipeline when replayed as regression inputs | M1, M2, M3 | Yes — binary pass/fail on regression test suite. Both bugs must be flagged. |
| SC3 | State coverage factor reduces convergence score when required categories are unaddressed (verified on 5 synthetic debates) | M2 | Yes — synthetic debates with intentionally missing categories must show factor < 1.0. |
| SC4 | Scenario trace divergences are detected and classified correctly for >=90% of synthetically injected divergences | M3 | Yes — inject known divergences into 10 test scenarios, measure detection rate. |
| SC5 | Invariant challenge rounds surface >=1 violated invariant per 10 pipeline runs (averaged over 30 runs) | M4 | Yes — count violated invariants per run. Target: mean >= 0.1 per run. |
| SC6 | Post-merge validation catches >=1 merge artifact in synthetic merge-with-known-artifact test cases | M6 | Yes — inject known merge artifacts into 5 test cases. All must be detected. |
| SC7 | Total pipeline token consumption increases by no more than 40% at `--depth standard` relative to v1.0 baseline | M1, M2, M3, M4 | Yes — measure mean token consumption over 20 runs at standard depth. Compare against v1.0 baseline. |
| SC8 | Pipeline convergence rate (debates that reach convergence without human intervention) remains >=80% after all milestones deployed | M2, M3, M4, M5 | Yes — measure convergence rate over 30 runs post-deployment. Baseline: current v1.0 rate. |
