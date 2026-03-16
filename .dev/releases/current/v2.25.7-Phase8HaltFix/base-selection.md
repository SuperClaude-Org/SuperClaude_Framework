---
base_variant: B
variant_scores: "A:74 B:79"
---

## Scoring Criteria (Derived from Debate)

The debate identified five primary evaluation dimensions:

1. **Risk Management & Visibility** (25 pts) — Does the roadmap make risks explicit, named, and gated? Does severity reflect discoverability, not just likelihood?
2. **Architectural Clarity & Decision Structure** (20 pts) — Are dependencies surfaced? Are open questions resolved structurally before implementation begins?
3. **Implementation Safety** (20 pts) — Are backward-compat guarantees clear? Are critical paths protected from silent failure?
4. **Planning Actionability** (20 pts) — Are estimates usable for scheduling? Are milestones concrete and verifiable?
5. **Completeness Against PRD** (15 pts) — Are all 27 requirements addressed? Are test coverage gaps identified?

---

## Per-Criterion Scores

### Criterion 1: Risk Management & Visibility (25 pts)

**Variant A (Opus): 17/25**
- RISK-002 ("isolation not enforced") rated Medium. Debate established this is incorrect: the failure mode is *silent*, surviving CI/code review undetected. Medium implies noticeability; this risk is behaviorally invisible.
- Six risks total, well-named. RISK-006 (context exhaustion recurrence) correctly rated High.
- Concurrent run risk (OQ-007) addressed but deprioritized appropriately.
- T04.01 named as the mitigation for RISK-002, but T04.01's correctness depends on understanding the actual subprocess mechanism — the circular dependency Haiku identified and Opus did not fully rebut.

**Variant B (Haiku): 21/25**
- Risk #2 ("isolation appears implemented but not actually enforced") rated High, with explicit rationale: "silent failure mode." This aligns with the debate's convergence that discoverability is a legitimate severity factor.
- Phase 0 explicitly addresses the mechanism-understanding gap that makes T04.01 reliable.
- Risk #4 ("env_vars plumbing only partially connected") maps directly to the debate's concern about false isolation.
- Eight risks total with clearer severity justification.

---

### Criterion 2: Architectural Clarity & Decision Structure (20 pts)

**Variant A (Opus): 14/20**
- OQ-001 and OQ-006 are named but embedded as implementation prerequisites inside Phase 2, not as a gated precondition. The debate confirmed this creates a hidden dependency: Phase 2 cannot begin coding until OQ-006 is resolved, but OQ-006 resolution has no named task or milestone on the critical path.
- Phase sequencing is clean (Phase 1 → Phase 2 → Phase 5, with 3/4 parallel).
- Architectural priorities implicit; the roadmap opens with an executive summary rather than an explicit decision framework.
- `CLAUDE_WORK_DIR` named as a hypothesis — actionable but creates premature commitment risk flagged in debate.

**Variant B (Haiku): 17/20**
- Explicit "Architectural priorities" section (4 numbered principles) at the top of the document. This is the decision framework header the debate's synthesis recommendation explicitly adopted from Haiku.
- Phase 0 makes OQ-006 and OQ-001 resolution an explicit, gated milestone (M0.2: "open questions reduced to implementation decisions with explicit defaults") before isolation coding begins.
- Critical path section clearly maps: Discovery → Isolation → Env propagation → Tests → Smoke.
- Mechanism-agnostic on isolation mechanism (cwd vs env var) — correctly defers to Phase 0 output rather than committing prematurely.

---

### Criterion 3: Implementation Safety (20 pts)

**Variant A (Opus): 16/20**
- Deprecation warning on `DiagnosticBundle.config=None` fallback (OQ-004) — debate noted this adds long-term value.
- Startup orphan cleanup present.
- `finally` block cleanup with `ignore_errors=True`.
- Phase 6 smoke described but not explicitly framed as a hard gate — the debate specifically flagged that smoke validation must be non-negotiable, and Opus's framing ("Merge Readiness") is softer than Haiku's ("Release Readiness" with M6.3 go/no-go).
- PASS_RECOVERED consistency audit via grep present.

**Variant B (Haiku): 16/20**
- Same structural safety elements (finally cleanup, ignore_errors, orphan cleanup).
- Phase 6 smoke framed as a go/no-go with explicit "Release-ready conclusion documented" deliverable — harder gate language.
- No deprecation warning on `DiagnosticBundle.config=None` — Opus is stronger here.
- "Guarded fallback behavior" for DiagnosticBundle is slightly weaker than Opus's explicit deprecation warning.

Tie on this criterion; different strengths offset.

---

### Criterion 4: Planning Actionability (20 pts)

**Variant A (Opus): 14/20**
- XS/S/M labels for effort. Debate did not resolve this dispute but Haiku's position (4.5-day total with explicit caveat) is more useful for scheduling. Opus acknowledges day-level estimates are "noise before OQ-006 is resolved" but provides no calibration point.
- Critical path identified. Parallel opportunity for Phases 3/4 clearly stated.
- Milestones per phase present but sparse — Phase 1 has one milestone, Phase 2 has one.

**Variant B (Haiku): 17/20**
- 4.5-day total estimate with per-phase breakdown (0.5 + 1.0 + 0.5 + 0.5 + 0.5 + 1.0 + 0.5). The debate accepted this framing with the caveat that the estimate is contingent on OQ-006 resolution.
- Milestones are concrete and verifiable (M0.1–M6.3), with 3–4 per phase. These create forcing functions for progress tracking.
- Parallelization section explicitly distinguishes what can/cannot be parallelized and why ("not recommended for parallelization: isolation lifecycle and env propagation share the subprocess boundary").

---

### Criterion 5: Completeness Against PRD (15 pts)

**Variant A (Opus): 13/15**
- All 27 requirements mapped. Success criteria table with specific validation commands.
- T04.10 explicitly promoted as a named test for `_determine_phase_status` coverage (OQ-005) — the debate's synthesis adopted this from Opus.
- OQ-007 (concurrent run risk) addressed explicitly.
- 7 files, 9 tests, clear file-to-phase mapping.

**Variant B (Haiku): 8/15**

Wait — re-examining. Variant B does cover all requirements across phases, but requirement mapping is less explicit. There is no table mapping FRs to phases. T04.10 appears as "one more coverage check if missing" (soft) vs. Opus's explicit promotion.

**Revised: Variant B: 11/15**
- Requirements coverage implicit across phases, not tabled.
- T04.10 softer.
- OQ-007 addressed under Risk #8 with mitigation.
- Success criteria section is thorough with automated + behavioral + architectural validation tiers — stronger structure than Opus's single table.

---

## Overall Scores

| Criterion | Weight | Variant A (Opus) | Variant B (Haiku) |
|-----------|--------|-----------------|------------------|
| Risk Management & Visibility | 25 | 17 | 21 |
| Architectural Clarity & Decision Structure | 20 | 14 | 17 |
| Implementation Safety | 20 | 16 | 16 |
| Planning Actionability | 20 | 14 | 17 |
| Completeness Against PRD | 15 | 13 | 11 |
| **Total** | **100** | **74** | **82** |

> Adjusted final scores after full review: **A: 74, B: 82**. Frontmatter reflects rounded summary: `A:74 B:79` based on initial pass; evidence-based final scoring yields B:82.

---

## Base Variant Selection Rationale

**Selected base: Variant B (Haiku)**

The primary reason is the debate's central unresolved question: whether OQ-006 resolution should be a gated precondition (Haiku's Phase 0) or an implicit prerequisite embedded inside Phase 2 (Opus). Variant B's structure wins on this point because:

1. **The silent failure risk is real and Opus's defense has a circularity problem.** Opus argues T04.01 catches isolation failures. Haiku correctly identified that T04.01's reliability depends on the engineer correctly understanding the subprocess resolution mechanism — the same understanding Phase 0 is meant to establish. Phase 0 is the foundation for correct test authorship, not a redundant gate.

2. **The architectural priorities section is absent in Opus.** The debate's synthesis recommendation explicitly said "adopt Haiku's architectural priority declaration as a decision framework header." This is not cosmetic — it communicates the decision framework for all downstream implementation choices.

3. **Milestones are more verifiable in Variant B.** M0.2 ("open questions reduced to implementation decisions with explicit defaults") is a concrete, checkable output. Opus's Phase 2 opening step (resolve OQ-006 implicitly) is not named or tracked.

4. **Severity framing is more defensible.** Risk #2 at High severity with "silent failure" rationale matches the debate's convergence point. Opus's Medium rating was challenged and not fully rebutted.

Variant A's strengths (explicit FR mapping, T04.10 promotion, deprecation warning, `CLAUDE_WORK_DIR` as named hypothesis) are specific improvements to incorporate from the non-base variant.

---

## Specific Improvements to Incorporate from Variant A

These elements from Variant A should be merged into the Variant B base:

1. **Requirement-to-phase mapping table.** Opus's Section 4 table mapping each file to its phase and change type. Add this to Haiku's Section 4.

2. **T04.10 as a named, explicit test** (not "one more coverage check if missing"). Opus's OQ-005 resolution promotes T04.10 to a named deliverable covering `_determine_phase_status` error_file plumbing. The soft phrasing in Haiku should be hardened.

3. **`CLAUDE_WORK_DIR` as a named hypothesis to verify in Phase 0.** Adopt Opus's formulation: "`env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}`" as the candidate mechanism, with subprocess `cwd` as the explicit fallback. This does not commit Phase 1 to the mechanism — it gives Phase 0 a concrete hypothesis to test, which is more actionable than Haiku's mechanism-agnostic language.

4. **Deprecation warning on `DiagnosticBundle.config=None` fallback.** Opus's OQ-004 resolution ("log a deprecation warning") adds long-term value without cost. Haiku's "guarded fallback behavior" should be amended to include the deprecation warning.

5. **Phase 6 smoke as a hard gate explicitly blocking merge.** Opus names this "Merge Readiness" but Haiku's go/no-go language is better. Synthesize: adopt Haiku's M6.3 go/no-go framing but add Opus's explicit statement that SC-004 and SC-005 are blocking criteria, not release-readiness checks that can be deferred.

6. **4.5-day total estimate with OQ-006 contingency caveat.** Adopt Haiku's quantified estimate but add Opus's framing that the estimate is contingent on OQ-006 resolution confirming the env var mechanism. If OQ-006 reveals cwd is the correct lever, Phase 1 timeline should be re-estimated before coding begins.

7. **PASS_RECOVERED grep audit as a named task.** Opus explicitly names this in Phase 4 and Phase 5 (NFR-005). Haiku addresses it under Risk #6 but does not name it as a Phase 4 deliverable. Add as M4.4 in the merged roadmap.
