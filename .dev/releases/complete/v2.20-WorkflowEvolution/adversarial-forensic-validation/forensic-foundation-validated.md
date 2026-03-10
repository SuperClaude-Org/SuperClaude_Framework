<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant 3 (forensic-diagnostic-report.md) -->
<!-- Merge date: 2026-03-08T00:00:00Z -->

# Forensic Foundation: Why Bugs Survive the SuperClaude Workflow

**Classification**: Diagnostic only — no fixes proposed
**Pipeline scope**: brainstorm → spec-panel → adversarial → roadmap → tasklist → CLI runner
**Sources**: Four peer artifacts compared under blind adversarial review; original three analyses treated as co-equal peers relative to the prior merged foundation

---

## Executive Summary

<!-- Source: Base (original, modified) — adjusted per Change #1 to preserve evidentiary hierarchy and unresolved conflicts -->
The strongest supported conclusion across the compared analyses is this:

**The pipeline validates that work looks right, not that work is right.**

Across the workflow, structural confidence accumulates faster than independent evidence. The system is highly effective at producing artifacts that are well-formed, reviewable, and consumable by downstream stages. It is materially weaker at proving that those artifacts are semantically correct, operationally trustworthy, and faithfully preserved across handoffs.

This does **not** fully resolve whether the failure system is best explained as a category error, a multi-factor process gap, or misallocated rigor. The evidence supports a more careful statement: the pipeline over-weights document quality, internal agreement, and process conformance relative to runtime truth and boundary fidelity.

---

## Part I: Validated Findings

These findings are supported by strong evidence across multiple compared artifacts and survived adversarial challenge.

### F-001: Structural Validation Is Systematically Mistaken for Semantic Correctness

<!-- Source: Base (original) -->
The pipeline’s gates primarily check structural properties. Content quality sits in the gap between what was deliberately excluded (LLM-evaluating-LLM) and what was never replaced by an independent semantic or runtime validator.

| Validates | Does NOT Validate |
|-----------|-------------------|
| File exists | Content is correct |
| File is non-empty | Content is complete |
| File has ≥N lines | Content is internally consistent |
| YAML frontmatter has required keys | Frontmatter values are semantically valid |
| Heading hierarchy has no gaps | Content under headings is relevant |
| Bulleted/numbered items exist | Items are actionable or feasible |
| Convergence score is in [0.0, 1.0] | Convergence reflects genuine agreement |
| Tasks have proper ID format | Tasks will produce working software |
| Subprocess exit code is 0 | Subprocess accomplished its goal |

<!-- Source: Variant 3, Section F-001 / code-level evidence — merged per Change #2 -->
Concrete examples support this claim:
- `_cross_refs_resolve()` in `roadmap/gates.py` scans references but is effectively non-failing.
- `_has_actionable_content()` can pass on the basis of minimal bullet presence rather than meaningful actionability.
- `_convergence_score_valid()` checks parseability and range, not semantic relationship to the debate.

### F-002: Confidence Inflates Across Stages Through Proxy Stacking

<!-- Source: Variant 2, confidence-signal table — merged per Change #3 -->
Each stage emits a confidence artifact that later stages treat as a trustworthy summary. The problem is not that these signals are numerically wrong; it is that they measure proxies that are easy to misread as evidence.

| Confidence Signal | What It Actually Measures | What It Is Often Taken to Mean | Gap |
|-------------------|--------------------------|--------------------------------|-----|
| Panel score: 8.6/10 | Document structure and apparent reviewability | The spec will work when implemented | Document quality ≠ implementation quality |
| Expert approval | Simulated persona agreement | Expert validation | Simulated approval ≠ external judgment |
| Convergence: 0.72 | Internal model agreement across debate roles | Design robustness or truth | Self-agreement ≠ correctness |
| Tasklist quality: 100% | Task description quality | Execution quality | Description quality ≠ behavioral success |
| Gate PASS | Structural compliance | Output correctness | Structural validity ≠ semantic correctness |
| Pass rate: 97.4% | Completion against process criteria | Feature completeness | Process completion ≠ working software |

### F-003: The Adversarial Stage Is Better at Design Critique Than Runtime Falsification

<!-- Source: Base (original, modified) — sharpened with retained opposing strengths -->
The adversarial stage can expose contradictions, scope ambiguity, and architecture-level disagreements inside the text of a plan. It cannot verify implementation behavior because no implementation exists yet at the point of debate.

| The Adversarial Stage Can Catch | It Cannot Catch |
|--------------------------------|-----------------|
| Logical contradictions in spec text | Implementation bugs in generated code |
| Missing requirements visible in text | Missing error handling in real code paths |
| Architectural inconsistencies | LLM output variability at runtime |
| Scope ambiguity | Whether prompts produce correct output |
| Conceptual risk gaps | Whether gates catch real failures |
| Process workflow issues | Whether mocks represent production reality |

It also has a secondary loss mode: even when the debate identifies useful conclusions, incorporation downstream is partial. Evidence from the compared artifacts repeatedly cited that roughly 10–15% of adversarial conclusions were simplified or dropped without systematic downstream tracking.

### F-004: Tests Systematically Exclude the Highest-Risk Boundary

<!-- Source: Variant 3 evidence chains + Variant 4 seam framing — merged per Changes #2 and #4 -->
The most failure-prone boundary is the one between executor logic and actual Claude CLI subprocess behavior. That is the place where signal parsing, formatting variability, monitoring assumptions, and timing behavior interact. The compared analyses consistently show that this boundary is mocked, hand-crafted, or otherwise bypassed rather than exercised directly.

Representative evidence cited across the source analyses includes:
- executor-loop tests that mock subprocess interaction,
- status-determination tests that use hand-crafted result files,
- mitigations aimed at signal handling that still mandate mocked subprocesses,
- diagnostic harnesses whose names imply end-to-end scope while their actual tests stay at subcomponent level.

### F-005: Retrospective Findings Fail to Become Immediate Forward Constraints

<!-- Source: Base (original) -->
The clearest evidence chain concerns `PARTIAL → PASS` promotion:
1. A retrospective identifies the bug and rates it as highest priority.
2. The next spec reproduces the same status-fidelity gap.
3. Chronology shows the retrospective post-dates the spec, so incorporation was structurally impossible on that cycle.

This is not merely “a missed lesson.” It shows a timing disconnect between discovery and prevention: the workflow learns backward while planning forward.

### F-006: Seam Failures Are a Primary Failure Habitat

<!-- Source: Variant 4 seam analysis — merged per Change #4 -->
The strongest boundary-centered reading is that many important defects are introduced or hidden at handoffs rather than inside any single artifact in isolation. High-risk seams include:
- spec → prompt,
- extract → generate,
- adversarial → merge,
- roadmap → tasklist,
- tasklist → CLI runner,
- runner → monitor/gates,
- retrospective → next spec.

This seam-centered framing is important because it explains why each local stage can look healthy while the cross-stage system still leaks critical constraints.

---

## Part II: Strongly Supported but Not Fully Resolved Theories

These theories are well-supported, but adversarial review did not justify promoting all of them to fully settled findings.

### T-001: The System May Contain a Category Error

<!-- Source: Variant 2 category-error framing — merged per Change #3, preserved as theory not finding -->
One strong interpretation is that the pipeline uses textual analysis to validate artifacts whose ultimate quality depends on execution behavior. Under that reading, document-quality methods are necessary but insufficient, and the workflow is being asked to answer a question it was not built to answer.

This theory was retained as a theory rather than a finding because the compared artifacts do not prove that this is the single governing cause. A more modest reading is that document-quality validation has been over-weighted relative to runtime proof.

### T-002: Misallocated Rigor Explains More Than Lack of Rigor

<!-- Source: Variant 4 core framing -->
Another strong theory is that the process is not weak because it is shallow; it is weak because its strongest rigor is concentrated in the wrong places: formatting, artifact shape, internal agreement, and planning decomposition rather than external truth and live-path verification.

### T-003: Schema Drift Can Propagate Silently Through Passing Gates

<!-- Source: Variant 3 and Variant 1 -->
A recurring example is extract-schema drift: the operational contract thins, the gate adapts to the thin contract, and downstream stages continue with less information while PASS signals remain green. This appears strongly evidenced in at least one important case, though broader generalization remains a theory.

### T-004: Prior Synthesis Can Itself Become a Lossy Compression Layer

<!-- Source: adversarial comparison itself -->
The prior merged foundation artifact was useful, but the comparison confirmed that starting from a synthesis can silently inherit previous losses. This is why the prior foundation was treated as a peer artifact rather than an authority during this run.

---

## Part III: Unresolved Conflicts That Should Not Be Flattened

<!-- Source: Variant 1 unresolved conflicts structure + Variant 4 plural framing — merged per Change #5 -->

### UC-001: Is the failure system monocausal or multi-causal?
- **Monocausal reading**: the deepest problem is a category mismatch between document validation and implementation quality.
- **Multi-causal reading**: several mechanisms co-occur — proxy inflation, seam loss, schema drift, mock-boundary exclusion, and retrospective disconnect.
- **Current verdict**: unresolved. The evidence is strongest for a multi-mechanism failure ecology, but not strong enough to eliminate the monocausal framing entirely.

### UC-002: Does convergence carry any truth-bearing signal?
- **Lower-value view**: convergence mostly shows the model agreeing with itself.
- **Weak-signal view**: convergence has internal process value but should not be treated as correctness evidence.
- **Current verdict**: unresolved. The safer conclusion is that convergence is structurally interesting and epistemically weak.

### UC-003: Is the architecture fundamentally flawed or incompletely defended?
- **Architecture-flaw reading**: the pipeline was built for the wrong validation problem.
- **Incomplete-defense reading**: the architecture is coherent but missing independent verification at critical seams.
- **Current verdict**: unresolved. The compared evidence supports both readings better than a forced single answer.

---

## Part IV: Hidden Assumptions Surfaced by the Adversarial Comparison

<!-- Source: Variant 1 hidden assumptions + shared assumption analysis — merged per Change #6 -->

### A-001: Structural validity is too weak to serve as a serious proxy for correctness
All compared artifacts assume this. It is strongly supported, but the exact strength of correlation between structure and quality was not empirically measured here.

### A-002: The highest-risk failures cluster at seams rather than only within stages
This assumption is strongly supported by repeated examples, but it remains an inference about failure distribution across the workflow.

### A-003: Some form of stronger external or runtime verification would improve trustworthiness
All artifacts imply this, but none proves which kind of verification would be sufficient, tractable, or free from new failure modes.

### A-004: The observed failures generalize beyond the examined releases
The evidence base spans several releases and related implementation artifacts, but full generalization remains an assumption.

---

## Part V: Strongest Evidence Chains

### Evidence Chain 1: PARTIAL→PASS propagation failure
1. Retrospective records `PARTIAL` being silently promoted to `PASS` and rates it as high priority.
2. The next spec omits `PARTIAL` from the relevant status model.
3. Chronology shows the retrospective came after the spec, making immediate incorporation impossible.
4. Therefore the learning loop is temporally disconnected from the spec-prevention loop.

### Evidence Chain 2: Schema drift through passing gates
1. Protocol expectations remain richer.
2. Operational prompts request a thinner schema.
3. Gates validate the thinner schema and still report PASS.
4. Downstream stages consume degraded inputs without escalation.
5. Therefore PASS reflects satisfaction of a weakened contract, not preservation of protocol richness.

### Evidence Chain 3: Mock-boundary exclusion
1. Highest-risk failures occur at the executor ↔ subprocess boundary.
2. Tests that should exercise this boundary use mocks or hand-crafted files.
3. The resulting green tests validate harness logic more than live interaction.
4. Therefore testing structurally excludes the very place where important failures emerge.

### Evidence Chain 4: Structural-gate bug propagation across layers
1. A brittle frontmatter-position assumption exists in one validation layer.
2. Equivalent assumptions are duplicated in adjacent semantic checks.
3. Fixing one layer leaves homologous failures alive elsewhere.
4. Therefore shared assumptions can survive local fixes and keep failure blast radius wide.

### Evidence Chain 5: Spec-to-implementation drift without detection
1. Implementations grow beyond their original specs.
2. APIs, formats, defaults, and subsystems change materially.
3. Tests continue validating against the spec’s intended contract rather than the drifted implementation reality.
4. Therefore spec drift can widen without an active detection mechanism.

---

## Part VI: Boundary Map — Where Failure Is Most Likely Introduced or Hidden

1. **Spec → Prompt**: full requirements compress into summarized task language.
2. **Extract → Generate**: thin schemas propagate as if complete.
3. **Adversarial → Merge**: findings can be simplified or dropped without tracking.
4. **Roadmap → Tasklist**: rich constraints become operational metadata.
5. **Tasklist → CLI Runner**: execution receives reduced context and structural acceptance criteria.
6. **Runner → Gates/Monitor**: structural compliance can substitute for semantic truth.
7. **Retrospective → Next Spec**: lessons arrive too late to constrain the already-written next cycle.
8. **Spec → Implementation**: drift can grow while official validation still points at the older contract.

---

## Methodological Note

This artifact was produced from a deep, blind adversarial comparison of four artifacts, including one prior synthesis and three original peer analyses. In accordance with the user’s instruction, the original three analyses were treated as co-equal peers and the prior synthesis was not granted authority by title, tone, or apparent comprehensiveness.

---

*Diagnostic only. No fixes proposed.*