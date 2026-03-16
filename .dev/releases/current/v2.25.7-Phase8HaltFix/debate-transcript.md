---
convergence_score: 0.72
rounds_completed: 2
---

# Structured Adversarial Debate: Opus Roadmap vs. Haiku Roadmap
## Sprint Context Resilience (v2.25.7-phase8)

---

## Round 1: Initial Positions on Divergence Points

### Variant A (Opus) — Opening Position

**On Phase 0 (Discovery) as structural overhead:**

Phase 0 is process theater for a bounded, well-scoped sprint. This codebase has seven clearly identified files, eleven shared assumptions already confirmed between both variants, and a complexity score of 0.62. The interfaces are not novel — `ClaudeProcess.__init__()`, `build_env()`, `execute_sprint()` — these are the same call paths engineers on this team work with routinely. Treating interface validation as a half-day deliverable with formal milestones (M0.1 through M0.3) introduces calendar overhead without proportionate risk reduction.

More critically, Phase 0 can create a false gate. If discovery produces ambiguous answers — which it will on OQ-001 and OQ-006, since those require actually reading the subprocess wiring — the team ends up doing implementation-level investigation anyway. The better model is to front-load OQ resolution *within* Phase 1 and Phase 2 as the first implementation step, not as a separate phase that gates them.

**On OQ-001 resolution (`CLAUDE_WORK_DIR` env var):**

Naming `CLAUDE_WORK_DIR` by name is not premature specificity — it is the actionable output of architectural reasoning. The isolation mechanism requires the subprocess to resolve `@` references against a constrained directory. The two plausible levers are: subprocess `cwd`, or an env var. We name the env var candidate so it can be *verified* in Phase 1 before Phase 2 begins. Variant B leaves this as "add minimum viable plumbing" — which means the implementer discovers the answer during Phase 1 anyway, just without a named hypothesis to test.

**On Risk #2 / RISK-002 severity (isolation not enforced):**

Medium severity is appropriate because the risk is *mitigatable*. T04.01 in the test suite validates end-to-end isolation. The smoke test in Phase 6 verifies subprocess cannot reach `tasklist-index.md`. A high-severity classification implies the risk is either high-probability or not effectively mitigatable within the sprint — neither is true here. Medium severity with explicit test coverage and smoke validation is proportionate.

**On timeline qualitative vs. quantitative estimates:**

XS/S labels communicate relative effort without false precision. Day-level estimates anchor to a baseline that may be wrong once OQ-001 and OQ-006 are resolved. If the subprocess `cwd` mechanism turns out to be the correct lever — not an env var — the isolation implementation changes significantly. Quantified estimates before that question is answered are noise.

---

### Variant B (Haiku) — Opening Position

**On Phase 0 as required risk control:**

The diff analysis itself names "implementation drift" and "false sense of isolation" as the primary failure modes. Both are direct consequences of coding before understanding the mechanism. The interfaces are not novel, but the *wiring between them* at the subprocess boundary is. Specifically: does isolation require `env_vars` to be plumbed first, or does subprocess `cwd` suffice independently? Opus cannot answer this question without the same investigation it claims is overhead.

Phase 0 is not about reading known files — it is about mapping the call path from `execute_sprint()` through `ClaudeProcess` to subprocess launch, identifying where `@` resolution occurs, and confirming which mechanism controls it. That investigation takes 0.5 days and saves multiple days of implementation rework if the env var hypothesis is wrong. The ROI is asymmetric in favor of discovery.

The milestones M0.1–M0.3 are not ceremony. M0.2 specifically — "open questions reduced to implementation decisions with explicit defaults" — is the output that makes Phase 1 and Phase 2 deterministic rather than exploratory.

**On OQ-001 and the `CLAUDE_WORK_DIR` proposal:**

Naming `CLAUDE_WORK_DIR` is not a strength — it is a premature commitment that Opus itself hedges with "verify that `ClaudeProcess` respects this env var for `@` resolution (OQ-006)." If verification is required before Phase 2, and verification requires the same investigation Variant B calls Phase 0, then Opus has Phase 0 embedded silently inside Phase 2 without calling it that. The difference is Variant B makes the investigation explicit and gated; Opus makes it implicit and potentially blocking.

If `CLAUDE_WORK_DIR` turns out not to be the mechanism, Opus's Phase 2 implementation is wrong from the start.

**On Risk #2 severity elevation:**

The "isolation appears implemented but is not actually enforced" failure mode is uniquely severe because it is *silent*. Unlike a test failure or a syntax error, the sprint can merge, pass CI, and ship while `tasklist-index.md` remains fully accessible to subprocesses. The token waste continues unchanged. No alarm fires.

Medium severity implies the risk is noticeable and catchable during development. High severity is warranted here specifically because the failure mode is invisible in code review and only detectable through behavioral verification. The severity rating should reflect the *discoverability* of the failure, not just its likelihood. Opus's T04.01 test is valuable but only catches the issue if the test itself correctly verifies subprocess scope — which requires understanding the actual mechanism. Circular dependency.

**On day-level estimates:**

XS/S labels are not conservative — they are incomplete. A 4.5-day estimate that anchors poorly is more useful than no estimate, because it makes the sprint plannable and creates a forcing function to revise the estimate once OQ-001 is resolved. "Noise" is better than silence when scheduling work. Variant B explicitly notes estimates could anchor poorly if discovery reveals complexity — that caveat is the appropriate hedge, not abandoning quantification altogether.

---

## Round 2: Rebuttals

### Variant A (Opus) — Rebuttal

**Rebutting "Phase 0 prevents silent failure":**

Variant B argues that the isolation failure mode is silent. Accepted. But the proposed defense against a silent failure is not Phase 0 — it is T04.01 plus Phase 6 smoke validation. These are the only mechanisms that actually verify subprocess scope at runtime. A Phase 0 call-path map verifies *our understanding* of the mechanism; it does not verify that the mechanism works. If `CLAUDE_WORK_DIR` turns out to be wrong, T04.01 catches it. Phase 0 does not.

Variant B is conflating two different things: architectural uncertainty (which Phase 0 addresses) and behavioral uncertainty (which only tests and smoke address). We should spend the half-day on test coverage, not a map of call paths we can read in 20 minutes.

**Rebutting the circularity argument on T04.01:**

The claim that T04.01 "only catches the issue if the test itself correctly verifies subprocess scope" creates an infinite regress. At some point, an engineer must read the code and write a correct test. That is not a weakness of the test-first approach — it is a condition of all software verification. Phase 0's call-path map faces the same circularity: it is only useful if the engineer reading it understands the subprocess launch mechanism correctly. Neither Phase 0 nor T04.01 eliminates the need for competent implementation; they are both aids to it.

**Rebutting the severity framing:**

Variant B argues severity should reflect *discoverability* of a failure, not just likelihood. This is a reasonable framing, but it proves too much. Every integration bug is hard to detect in code review and only visible in behavioral testing. If discoverability alone warrants high severity, then every integration point in this sprint is high-severity. The practical risk taxonomy distinguishes between risks by their *impact if undetected* and their *mitigation cost*. The isolation enforcement risk has high impact if undetected but low mitigation cost (one behavioral test in Phase 6). Medium severity with explicit mitigation is the correct classification.

**Rebutting day-level estimates:**

Variant B says "4.5 days that anchors poorly is more useful than no estimate." This is only true if the anchor is recalibrated when the anchoring assumption is wrong. In practice, day-level estimates create psychological anchors that persist even after scope changes. XS/S labels communicate *relative* effort without implying a specific calendar commitment that may need to be walked back. The more important planning artifact is the critical path, which both variants agree on.

---

### Variant B (Haiku) — Rebuttal

**Rebutting "T04.01 is the real defense against silent failure":**

Opus argues Phase 0 does not verify the mechanism, only our understanding of it. Correct. But this is precisely the point: if our understanding is wrong, T04.01 will be written incorrectly and will pass even when isolation is not enforced. A test that mocks subprocess behavior based on an incorrect mental model of how `@` resolution works will not catch the failure it is supposed to catch. Phase 0 is the step that ensures T04.01 tests the *actual* subprocess resolution path, not a model of it.

The argument that "an engineer must read the code anyway" does not rebut Phase 0 — it describes what Phase 0 is. The difference is whether that reading happens unstructured (inside Phase 2, under time pressure, without explicit milestones) or structured (as Phase 0, with a defined output that feeds Phase 1 design decisions).

**Rebutting the "20 minutes to read call paths" claim:**

If `ClaudeProcess.__init__()`, `build_env()`, and the subprocess spawn boundary are truly understood in 20 minutes, then Phase 0 costs 20 minutes, not 0.5 days. Variant B's 0.5-day estimate implicitly acknowledges this is not a 20-minute task. The sprint touches a subprocess boundary that Opus itself flags as an open question requiring verification (OQ-006). That is not a 20-minute read.

**On `CLAUDE_WORK_DIR` as a premature commitment:**

Opus acknowledges OQ-006 must be resolved before Phase 2. Phase 0 is the explicit, structured place to resolve OQ-006. By embedding OQ-006 resolution inside Phase 2 as an implicit prerequisite, Opus creates a hidden dependency: Phase 2 cannot begin coding until OQ-006 is resolved, but OQ-006 resolution is not on the critical path as a named task. If OQ-006 takes longer than expected — the env var mechanism is more complex than anticipated, or it turns out `cwd` is the correct lever — Phase 2 delays without a visible indicator. Phase 0 makes this dependency explicit and surfaced.

**On severity framing concession with a caveat:**

Opus's rebuttal on severity is partially accepted: medium severity with explicit mitigation is defensible if the mitigation (behavioral smoke test) is treated as blocking, not optional. The remaining dispute is not severity label but gating behavior. Variant B's position: smoke validation in Phase 6 must be treated as a hard gate, not a release-readiness check that can be skipped under schedule pressure. If Opus agrees that Phase 6 smoke is non-negotiable, the severity label difference is cosmetic.

---

## Convergence Assessment

### Areas of Agreement Reached Through Debate

1. **Test coverage and smoke validation are the primary defenses against silent isolation failure.** Both variants converge that T04.01 and Phase 6 smoke verification are necessary. The dispute about Phase 0 does not change this shared conclusion.

2. **OQ-006 must be resolved before Phase 2 isolation code is written.** Opus embeds this as an implicit prerequisite; Haiku makes it an explicit Phase 0 milestone. Both agree the verification must happen. The debate is about whether it needs a formal phase structure or can be absorbed into Phase 2's opening step.

3. **The isolation failure mode warrants elevated attention regardless of severity label.** Opus moved toward Haiku's position by explicitly naming T04.01 and smoke validation as the mitigation. Haiku moved toward Opus's position by acknowledging medium-severity-with-explicit-mitigation is defensible if Phase 6 is treated as a hard gate.

4. **`env_vars` with override semantics is correct for isolation-specific variables.** No dispute on OQ-003.

5. **Deprecation warning on `DiagnosticBundle` fallback (Opus) adds long-term value**, though Haiku's "guarded fallback behavior" achieves the immediate compatibility goal. Minor difference with low stakes.

6. **T04.10 for `_determine_phase_status` coverage should be added.** Haiku's softer phrasing ("one more coverage check if missing") converges with Opus's explicit promotion of it as OQ-005. Both effectively recommend it.

### Remaining Disputes

1. **Phase 0 as a named phase vs. inline prerequisite to Phase 2.** The structural question is not resolved. The practical gap is small: both variants require OQ-006 resolution before isolation wiring. The debate is whether that work has a formal phase boundary and milestone structure (Haiku) or is absorbed silently into Phase 2 (Opus). Teams with strong codebase familiarity favor Opus's approach; teams with less context favor Haiku's.

2. **`CLAUDE_WORK_DIR` by name vs. mechanism-agnostic plumbing.** Opus's named-hypothesis approach is more actionable; Haiku's mechanism-agnostic approach is safer under uncertainty. The correct choice depends on OQ-006's actual answer — which neither variant knows without the investigation both require.

3. **Quantitative vs. qualitative timeline estimates.** No convergence reached. Opus's position that XS/S labels are sufficient for planning; Haiku's position that 4.5-day estimates are more actionable. Low-stakes for sprint execution but material for external scheduling.

### Synthesis Recommendation

The strongest merged approach:

- **Adopt Haiku's architectural priority declaration** as a decision framework header.
- **Adopt Opus's phase sequencing** (Phase 1 = env_vars, Phase 2 = isolation) but **prepend an explicit OQ-006 verification step** at the start of Phase 2 rather than a separate Phase 0 — call it "Phase 2 Gate" or embed as M2.0.
- **Adopt Haiku's high-severity framing for isolation enforcement risk**, but pair it with Opus's explicit mitigation path (T04.01 + Phase 6 smoke as blocking gates).
- **Adopt Opus's `CLAUDE_WORK_DIR` hypothesis as a named candidate** to verify, not a commitment, with subprocess `cwd` as the explicit fallback.
- **Adopt Opus's deprecation warning** on `DiagnosticBundle.config=None` fallback.
- **Adopt Haiku's 4.5-day estimate** with the explicit caveat that the estimate is contingent on OQ-006 resolution confirming the env var mechanism.
- **Adopt Opus's T04.10 promotion** as a named test, not an optional coverage check.
