# Debate Transcript — Strategy 2: Single-Pass Clarification Rules

**Adversarial Pipeline Step 2**
**Date**: 2026-03-04
**Format**: FOR advocate vs AGAINST advocate — 3 rounds
**Subject**: Adopt Strategy 2 into `sc-tasklist-command-spec-v1.0.md`

---

## Round 1: Opening Arguments

---

### FOR Advocate — Opening

**Thesis**: Strategy 2 should be adopted as specified. It hardens the command layer against real failure modes without introducing any new behavior in the generation pipeline.

**Argument F1 — Fills a genuine spec gap**

The current §5.4 specifies four validation checks but says nothing about what happens when any of them fail. In a production tool consumed by CI pipelines, "undefined behavior on validation failure" is a defect, not just an omission. The command will emit some output on failure — without specification, that output is arbitrary, likely inconsistent, and potentially misleading to operators. Strategy 2 closes this gap with a one-sentence addition: fail-fast with a structured error listing the exact missing fields.

This is not new behavior. It is specification of behavior that is already occurring implicitly. Documenting it is always compatible with a parity constraint.

**Argument F2 — Preserves the non-interactive invariant perfectly**

The Non-Goals section states: "No interactive mode or progressive generation." Strategy 2 adds exactly zero interactive behavior. The one-pass fallback is a deterministic algorithm, not a prompt to the user. The structured error is an output, not an input request. The "ask once for gaps" inspiration from taskbuilder has been correctly stripped of its interactive nature in this adaptation. The result is purely non-interactive: attempt resolution → fail deterministically if unresolved.

**Argument F3 — Explicit fail-fast has concrete CI value**

Consider the automation case: `/sc:tasklist @roadmap.md` is invoked in a CI job. The roadmap doesn't contain a TASKLIST_ROOT marker. Without Strategy 2, the command fails silently or with an LLM-generated message of variable quality. With Strategy 2, the operator receives a structured error identifying exactly which required field failed derivation and why. The CI job can log this cleanly. This is a pure quality improvement with zero risk.

**Argument F4 — "One-pass" is not scope expansion**

The §5.4(4) algorithm already performs one derivation attempt for TASKLIST_ROOT from roadmap content. Strategy 2 labels this as the one-pass fallback and formalizes what happens when it fails. This is classification of existing behavior, not new behavior.

---

### AGAINST Advocate — Opening

**Thesis**: Strategy 2 as written should not be adopted without significant tightening. The strategy introduces genuine implementation risk through underspecification, and the proposed spec text is not tight enough to implement without ambiguity.

**Argument A1 — "One deterministic fallback resolution attempt" is not defined**

The strategy text says: "perform one deterministic fallback resolution attempt." What does this mean concretely for each of the four validation checks?

- Check 1 (`roadmap-path` exists): What is the fallback? Try a different path? Path normalization? There is no fallback for a file that doesn't exist.
- Check 2 (`--spec` exists): Same problem. If the file is missing, there is no recovery.
- Check 3 (`--output` parent exists): Create the directory? That is a side effect, not a validation fallback.
- Check 4 (`--output` absent → derive via §3.1): This already IS the fallback. There is nothing to add.

The strategy text implies a uniform "one-pass fallback" across all four checks, but the only case where a genuine algorithmic fallback is meaningful is Check 4. For Checks 1-3, the only valid behavior is immediate failure. Strategy 2 conflates these cases.

**Argument A2 — Structured error format is unspecified**

The proposed spec change says: "fail-fast with actionable diagnostics." What format? JSON? Markdown? A human-readable string? What fields are required? The spec text added to §5.4 and Boundaries does not answer this. Without a concrete format, two implementers of this spec will produce incompatible output. For CI integration (the stated value), format consistency is essential.

**Argument A3 — Parity constraint implication**

The v1.0 parity constraint requires: "Achieves exact functional parity with the current v3.0 generator — no new features." If the current v3.0 generator (manual prompt workflow) produces no structured error on failure — just whatever the LLM happens to say — then adding a structured error protocol is technically a new feature, not parity. The argument that "we're only documenting existing behavior" is only valid if the existing behavior is already structured. It is not.

**Argument A4 — Risk of over-engineering the validation layer**

The command layer (`tasklist.md`) is explicitly scoped to: parse arguments, validate, invoke skill, report paths. Adding a recovery-and-diagnostics protocol bloats the command file and creates a second concern at the command layer: validation recovery. This pushes the command layer toward complexity that properly belongs in test infrastructure or a separate diagnostic command.

---

## Round 2: Rebuttal

---

### FOR Advocate — Rebuttal

**Addressing A1 (fallback underspecified)**

The opponent is correct that a uniform one-pass fallback is not meaningful for Checks 1-3. However, this is a fixable specification problem, not a reason to reject the strategy. The resolution is to restrict the "one-pass fallback" explicitly to Check 4 (TASKLIST_ROOT derivation), which is the only case where a deterministic algorithmic fallback exists. For Checks 1-3, the behavior is immediate fail-fast with the structured error. The strategy text should be tightened to reflect this. The core value (structured error output) remains fully intact.

**Addressing A2 (format unspecified)**

Again, a fixable problem. The format can be specified inline: a structured block listing the failed check number, the expected input, the actual value, and the recovery attempted. This is a one-paragraph addition to §5.4. The absence of format specification in the current strategy text is a documentation debt, not a design flaw.

**Addressing A3 (parity constraint)**

The parity constraint applies to generator output, not to command-layer error messages. The acceptance criteria in §9 specify: "Functional parity: output is identical to running the v3.0 generator prompt manually." The "output" refers to the tasklist bundle (index + phase files). Error messages on validation failure are not generator output — they are command-layer error handling. A structured error on invalid input is not a new generator feature.

**Addressing A4 (over-engineering)**

Structured error output for a validation failure is three to five lines of formatted text. This is not over-engineering. It is the minimum viable contract for a command used in automation contexts. Every production CLI tool specifies its exit behavior and error format. Omitting this is not simplicity — it is incompleteness.

---

### AGAINST Advocate — Rebuttal

**Addressing F1 (fills spec gap)**

The spec gap argument proves too much. By this logic, any unspecified behavior should be specified. The question is which gaps to close in v1.0 vs defer. Error format is a legitimate v1.1 concern. The v1.0 goal is parity and installation; error formatting is polish. Prioritizing error format specification over completing the generator pipeline is an ordering error.

**Addressing F2 (non-interactive preserved)**

Agreed that the non-interactive invariant is preserved. This concession narrows the disagreement to implementation scope and format specification, not the fundamental design.

**Addressing F3 (CI value)**

The CI value argument is real but not unique to Strategy 2. Any validation failure will produce some error. Structured error format is a quality improvement but not a correctness requirement for v1.0. CI jobs can be designed to check exit codes rather than parse error message structure.

**Addressing F4 (labeling existing behavior)**

Partially accepted. Check 4 (§3.1 derivation) is indeed already a fallback. However, the strategy text as written implies broader scope. The opponent should have been clearer in the strategy text rather than relying on interpretation.

**Remaining opposition**: The strategy should be adopted only if (a) the fallback is restricted explicitly to the TASKLIST_ROOT derivation case and (b) a concrete error format is specified. Without these, the spec addition is too loose to implement deterministically.

---

## Round 3: Convergence Assessment

---

### FOR Advocate — Convergence

The AGAINST advocate has narrowed the dispute to two concrete requirements: restrict fallback scope to Check 4, and specify error format. Both are accepted. The strategy should be adopted with these tightening constraints incorporated into the spec text. The core value propositions — explicit fail-fast semantics and structured error output — are uncontested.

Accepted positions:
- Fallback applies only to TASKLIST_ROOT derivation (Check 4 in §5.4)
- Checks 1-3 are immediate fail-fast (no recovery attempt)
- Structured error format must be concretely specified in §5.4
- Parity constraint does not apply to command-layer error output

---

### AGAINST Advocate — Convergence

Concessions made:
- Non-interactive invariant is preserved (F2 accepted)
- Structured error output is not over-engineering (A4 withdrawn)
- Parity constraint scoped to generator output, not error messages (A3 partially withdrawn with qualifier: error format must not add LLM-generated prose that could vary between runs)

Remaining requirement:
- Error format must be deterministic (not LLM-generated free text), because determinism is a first-class requirement of the pipeline PRD (FR-3: deterministic rebuild; by extension, deterministic failure output is part of the deterministic pipeline contract).

---

## Per-Point Agreement Matrix

| Argument | Agreement | Notes |
|----------|-----------|-------|
| F1: Fills spec gap | Agreed | Opponents agree there is a gap |
| F2: Non-interactive preserved | Fully agreed | No dissent |
| F3: CI value real | Agreed | Magnitude disputed, not existence |
| F4: Labeling existing behavior | Partially agreed | Only for Check 4, not all checks |
| A1: Fallback underspecified | Resolved | Restrict to Check 4 |
| A2: Format unspecified | Resolved | Must be specified in adoption |
| A3: Parity constraint | Resolved | Scoped to generator output |
| A4: Over-engineering | Withdrawn | Not sustained |

**Convergence score**: 8/8 points resolved — 100% convergence with two mandatory tightening conditions.

---

## Debate Outcome Summary

The strategy is adoptable with two mandatory modifications:
1. Restrict the one-pass fallback explicitly to the TASKLIST_ROOT derivation case (Check 4)
2. Specify the error format concretely in the spec (deterministic, not LLM-generated free text)

All other objections were resolved or withdrawn.
