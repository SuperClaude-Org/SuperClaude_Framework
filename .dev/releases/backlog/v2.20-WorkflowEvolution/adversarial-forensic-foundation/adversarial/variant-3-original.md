# Workflow Failure Theories — Forensic Memo

## Executive memo

### Core finding
The workflow appears to generate **confidence faster than it generates independent evidence**.

Across brainstorm → spec-panel → adversarial → roadmap → tasklist → CLI runner, the process produces increasingly persuasive artifacts:
- clearer specs
- structured debates
- validation scores
- confidence percentages
- executable tasklists
- passing gates
- partial or mocked-path tests

But the strongest recurring failure pattern is that these signals mostly prove:
- structural completeness
- internal consistency
- contract-shaped output
- process conformance

not that the system works correctly in the real end-to-end path.

### Executive conclusion
The workflow’s weakness is **not lack of rigor**. It is **misallocated rigor**.

It is strongest at validating:
- whether artifacts match the workflow’s expected format
- whether downstream stages can consume metadata-shaped outputs
- whether planning documents agree with one another

It is weaker at validating:
- whether upstream constraints survive each handoff
- whether live runner behavior matches intended contracts
- whether downstream consumers actually use the information they require
- whether a “PASS” artifact is semantically true rather than merely parseable

### Most likely systemic cause
The workflow has become highly effective at checking **what it asked itself to produce**, but less effective at checking **whether the produced thing is true, sufficient, and operationally correct**.

---

## Scope

This is a diagnostic-only synthesis across:
- `.dev/releases/current/v.2.17-roadmap-reliability/spec-roadmap-pipeline-reliability.md`
- `.dev/releases/complete/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md`
- `.dev/releases/complete/v2.05-sprint-cli-specification/`
- `.dev/releases/complete/v2.08-RoadmapCLI/v2.07-sprint-retrospective-consolidated.md`
- `.dev/releases/complete/v2.08-RoadmapCLI/merged-spec.md`
- `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/release-spec.md`
- `src/superclaude/cli/roadmap/`
- related workflow artifacts in `src/superclaude/skills/sc-roadmap-protocol/refs/`

This document proposes **theories only**. It does **not** propose fixes.

---

## Forensic theories

### Theory 1: Structural validity is repeatedly mistaken for semantic correctness
The workflow repeatedly accepts outputs because they are well-formed, parseable, and contract-shaped, even when they are not proven to be semantically correct.

### Theory 2: Confidence compounds stage-to-stage faster than evidence quality improves
Each stage emits scores, PASS markers, and confidence indicators that later stages treat as trustworthy summaries, even when they are based on shallow or indirect validation.

### Theory 3: Adversarial and review stages are stronger at architecture critique than execution falsification
The workflow debates plans and compares variants effectively, but does not apply equivalent rigor to runtime behavior or consumer-facing correctness.

### Theory 4: Handoffs compress context and quietly drop constraints
Important requirements survive in upstream docs and rationale, but are narrowed, abstracted, or lost as the workflow moves into prompts, gates, task metadata, and runner behavior.

### Theory 5: Mocked or harnessed execution creates confidence in control logic without proving live integration
The workflow often proves the harness, synthetic protocol, or mocked boundary rather than the real Claude/runtime interaction where failures actually happen.

### Theory 6: Shared abstractions reduce apparent complexity while increasing blast radius
Refactors and unifications are often framed as low-risk because the abstraction is clean, even when shared behavior changes in subtle but meaningful ways.

### Theory 7: The system often validates internal agreement, not external truth
A spec defines the contract, prompts request it, gates check visible traces of it, and tests verify those checks. That loop is consistent, but can become self-sealing.

---

## Evidence by workflow stage

## Stage 1 — Brainstorm / early problem framing

### Primary pattern
Early framing is good at surfacing objectives and plausible causes, but it often converts uncertainty into a coherent root-cause narrative before enough live evidence exists.

### Evidence excerpts

#### Reliability spec turns one observed failure into a generalized causal chain
Source: `.dev/releases/current/v.2.17-roadmap-reliability/spec-roadmap-pipeline-reliability.md`

> “Root cause chain:
> 1. Claude's subprocess output contains conversational preamble before YAML frontmatter
> 2. `ClaudeProcess` captures raw stdout directly to disk with no post-processing
> 3. `_check_frontmatter()` requires `---` as the absolute first non-whitespace content”

This is a plausible chain, but later in the same spec an unresolved causal variable remains open:

> “`--verbose` flag interaction ... should be confirmed.”

### Forensic reading
The workflow is capable of producing a convincing explanation quickly. That is useful, but it also means the early narrative can harden before the remaining uncertainty is resolved.

---

## Stage 2 — Spec-panel / requirements formalization

### Primary pattern
Spec rigor is high, but much of it is concentrated on reviewability, decomposition, and acceptance formatting rather than proving that the resulting system will behave correctly under real execution.

### Evidence excerpts

#### Validation and quality are described in strong terms before equivalent runtime proof exists
Source: `.dev/releases/current/v.2.17-roadmap-reliability/roadmap-spec-panel-correctness-adversarial-v1.md`

> “catches design and architecture issues well, but misses a class of bugs that only surface at execution time”

This is a direct admission that the panel process is biased toward architectural correctness over execution correctness.

#### Diagnostic framework spec emphasizes observability plumbing before full reality-based coverage
Source: `.dev/releases/complete/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md`

> “Phase 1: Unblock the User (Critical Path)
> 1. `--debug` flag + `debug.log` creation ...
> 2. Event coverage across all 6 components ...
> 3. Logger architecture ...”

Real-Claude coverage and automated failure analysis are deferred later:

> “Phase 4: Full Test Coverage ... Levels 1-3 graduated tests (require claude binary) ... Auto-analysis + DiagnosticCollector + report generation”

### Forensic reading
The spec process is rigorous, but it tends to formalize instrumentation, decomposition, and architecture sooner than it formalizes real-path falsification.

---

## Stage 3 — Adversarial / debate / comparison

### Primary pattern
Adversarial stages are effective at comparing options and surfacing design disagreements, but not at independently falsifying implementation behavior.

### Evidence excerpts

#### Roadmap CLI adversarial flow is document-centric
Source: `src/superclaude/cli/roadmap/executor.py`

The implemented pipeline is:
- extract
- generate A/B
- diff
- debate
- score
- merge
- test-strategy

These are all artifact-producing and artifact-comparing steps. None of them execute the produced design in a live operational context.

#### Prompt layer confirms debate is narrative, not behavioral
Source: `src/superclaude/cli/roadmap/prompts.py`

The debate/scoring prompts ask for:
- divergence analysis
- structured debate
- variant scoring
- merged synthesis

They do not ask for implementation-level falsification, downstream parseability testing, or contract-usage verification.

#### Retrospective admits adversarial lessons were only partially carried through
Source: `.dev/releases/complete/v2.08-RoadmapCLI/v2.07-sprint-retrospective-consolidated.md`

> “~85-90% of adversarial conclusions were incorporated.”

and specifically:

> “Strategy 2's 6-field structured error format was simplified to 2-field”
> “Three v1.1 forward/deferral notes were not documented”
> “Strategy 3's fourth standalone criterion (‘session-start executable’) was dropped”

### Forensic reading
The adversarial layer adds sophistication and credibility, but it mostly operates on the level of plans, arguments, and documents. It does not reliably force execution truth into the pipeline.

---

## Stage 4 — Roadmap generation / validation scoring

### Primary pattern
Roadmaps and validation layers generate machine-readable confidence artifacts that look authoritative, even when the live codebase has not yet caught up to the contract being scored.

### Evidence excerpts

#### Validation scores become artifacts in their own right
Source: `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`

> `validation_score`
> `validation_status`

Source: `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md`

Validation is rubric-weighted across criteria like faithfulness, achievability, and risk quality.

#### Current reliability roadmap reports strong validation despite runner contract mismatch
Source: `.dev/releases/current/v.2.17-roadmap-reliability/roadmap.md`

> `validation_score: 0.92`
> `validation_status: PASS`

But the current live roadmap implementation still asks for only 3 extract fields:
- `src/superclaude/cli/roadmap/prompts.py`
- `src/superclaude/cli/roadmap/gates.py`

while the reliability spec requires 13+ parity fields:
- `.dev/releases/current/v.2.17-roadmap-reliability/spec-roadmap-pipeline-reliability.md`

### Forensic reading
The roadmap can be “validated” against protocol-derived criteria even while the live runner still enforces an older, weaker contract. That is a direct confidence-vs-reality divergence.

---

## Stage 5 — Tasklist generation / execution planning

### Primary pattern
Tasklists preserve structure and execution discipline, but compress rationale into operational metadata. Confidence becomes attached to tasks even when verification is skipped.

### Evidence excerpts

#### High confidence coexists with EXEMPT tier and skipped verification
Source: `.dev/releases/current/v.2.17-roadmap-reliability/phase-5-tasklist.md`

Examples in the validation phase show combinations like:
- high confidence percentages
- `Tier | EXEMPT`
- `Verification Method | Skip verification`

### Forensic reading
This creates a subtle but dangerous semantic drift:
- “confidence” starts to mean “this task is clearly specified and administratively ready”
- but is easy to misread as “this behavior has been empirically revalidated”

#### Constraint compression example
The reliability spec requires extract-step protocol parity with 13+ fields.
By the time this becomes execution planning, it is represented as tasks and validation milestones, but the runner still does not enforce the full contract.

### Forensic reading
The tasklist stage is not necessarily wrong; it is lossy. It turns rich upstream constraints into executable metadata, and some constraints do not survive that translation intact.

---

## Stage 6 — CLI runner / gate enforcement / live implementation

### Primary pattern
The live runner is where the workflow’s structural confidence collides with runtime reality. Its gates, prompts, and tests strongly favor artifact-shape validation.

### Evidence excerpts

#### Extract contract drift is real in code
Source: `src/superclaude/cli/roadmap/prompts.py`

`build_extract_prompt()` requests:
- `functional_requirements`
- `complexity_score`
- `complexity_class`

Source: `src/superclaude/cli/roadmap/gates.py`

`EXTRACT_GATE` requires only those same three fields.

But the reliability spec requires 13+ fields for protocol parity.

#### Gates are largely structural
Sources:
- `src/superclaude/cli/pipeline/gates.py`
- `src/superclaude/cli/roadmap/gates.py`

Checks mostly cover:
- file exists
- non-empty
- minimum lines
- frontmatter fields present
- a few heuristic semantic checks

Some “semantic” checks are weaker than they sound.
Example:
- `_cross_refs_resolve()` effectively does not fail the merge gate because it returns true even when reference resolution is fragile.

#### Tests prove gate satisfaction with synthetic content
Source: `tests/roadmap/test_executor.py`

Mock outputs are assembled from required frontmatter plus repeated content to satisfy line-count and gate expectations.

### Forensic reading
The runner is well-structured, but its enforcement model is still much closer to “artifact passes protocol-shaped gates” than to “artifact is operationally trustworthy.”

---

## Stage 7 — Retrospective / learning loop

### Primary pattern
The workflow does learn, but often as acknowledgment rather than as immediate protection in the affected execution path.

### Evidence excerpts

#### Retrospective clearly identifies the missing proof
Source: `.dev/releases/complete/v2.08-RoadmapCLI/v2.07-sprint-retrospective-consolidated.md`

> “validated at the design/structure level but lack an observed end-to-end invocation trace”

#### Yet merged roadmap spec preserves sprint’s status-trust behavior
Source: `.dev/releases/complete/v2.08-RoadmapCLI/merged-spec.md`

> “Wrap each Phase as a Step (no gate criteria — sprint uses EXIT_RECOMMENDATION)”
> “execute_pipeline trusts the returned `StepResult.status`.”

#### Retrospective also records telemetry truthfulness failures
Source: `.dev/releases/complete/v2.08-RoadmapCLI/v2.07-sprint-retrospective-consolidated.md`

> “Phase 3 status: `"pass"` (should be `"partial"`)”
> “`EXIT_RECOMMENDATION: CONTINUE` overrides `status: PARTIAL` in priority chain”

### Forensic reading
The learning loop captures important failures accurately, but the protective change often lands in the next conceptual design rather than immediately in the currently failing execution path.

---

## Cross-stage blind spots

### 1. End-to-end invocation truth is repeatedly deferred
The retrospective identifies it explicitly, later specs acknowledge it, but earlier stages still emit high confidence before it is proven.

### 2. Downstream contract consumption is under-validated
The workflow frequently checks whether fields exist, not whether later consumers meaningfully use them.

### 3. Confidence artifacts are easy to misread as evidence artifacts
Validation scores, PASS statuses, and task confidence numbers look evidentiary even when derived from heuristics, rubrics, or skipped verification.

### 4. Seam failures are underweighted
The most important bugs live between artifacts and stages:
- spec → prompt
- prompt → runner
- runner → monitor
- roadmap → tasklist
- tasklist → execution
- artifact producer → artifact consumer

### 5. Mock realism is over-credited
Mocked subprocesses, fake Claude scripts, and synthetic outputs are useful, but their success is often treated as stronger evidence than it should be.

### 6. Shared abstractions are trusted too early
Architectural cleanliness and low duplication are sometimes used as a proxy for behavioral safety.

### 7. External behavior assumptions remain weakly revalidated
Claude CLI behavior, output formatting, regex extraction, tmux behavior, and concurrency assumptions are discussed but not continuously re-proven.

---

## Confidence vs reality gaps

### Gap A
**Claimed confidence:** validated, PASS, high quality, low risk.

**Observed reality:** often means structurally checked, not operationally proven.

### Gap B
**Claimed confidence:** adversarial rigor.

**Observed reality:** mostly architecture/debate rigor, not runtime falsification.

### Gap C
**Claimed confidence:** task confidence percentages.

**Observed reality:** can coexist with EXEMPT tier and skipped verification.

### Gap D
**Claimed confidence:** resume/gate pass means safe reuse.

**Observed reality:** often means only that current files still satisfy shallow gates.

### Gap E
**Claimed confidence:** shared refactor is low-risk.

**Observed reality:** shared abstractions can silently widen blast radius.

### Gap F
**Claimed confidence:** no criteria were not met.

**Observed reality:** can still coexist with missing end-to-end proof.

---

## Bottom line

The workflow is not failing because it lacks thought, documentation, or process.
It is failing because those strengths are concentrated in **internal agreement** rather than **independent proof**.

The system is highly capable of producing artifacts that:
- look complete
- score well
- debate well
- gate well
- serialize well
- hand off cleanly

while still allowing defects to survive in:
- semantic correctness
- downstream contract fidelity
- runtime behavior
- seam integrity
- live end-to-end execution

That is why buggy deliverables can emerge from a workflow that appears, on paper, extremely rigorous.
