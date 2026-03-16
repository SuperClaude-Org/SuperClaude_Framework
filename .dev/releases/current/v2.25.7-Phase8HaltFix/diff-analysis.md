---
total_diff_points: 14
shared_assumptions_count: 11
---

## Shared Assumptions and Agreements

Both variants agree on:

1. **Problem statement**: Phase subprocesses resolving `tasklist-index.md` via `@` references wastes ~14K tokens per phase and contributes to context exhaustion.
2. **Core solution**: Filesystem isolation via per-phase scoped directories (copy phase file into temporary directory).
3. **Isolation mechanism**: `config.results_dir / ".isolation" / f"phase-{phase.number}"` with `shutil.copy2()`.
4. **Cleanup strategy**: `shutil.rmtree(..., ignore_errors=True)` in `finally` block, plus startup orphan cleanup.
5. **Environment propagation**: `env_vars: dict[str, str] | None = None` keyword-only parameter on both `ClaudeProcess.__init__()` and `build_env()`, with override semantics.
6. **Sprint context header**: `## Sprint Context` block in `build_prompt()` with identical content (sprint name, phase N/M, artifact root, results dir, prior-phase dirs, "do not seek index files" instruction).
7. **Error path detection**: `detect_prompt_too_long()` extended with `error_path: Path | None = None`, same last-10-lines logic.
8. **`PASS_RECOVERED` fix**: Route through INFO branch in `write_phase_result()`, with codebase-wide grep for parity gaps.
9. **`FailureClassifier` fix**: Replace hardcoded path with `bundle.config.output_file(...)`, add `config: SprintConfig | None = None` to `DiagnosticBundle` with `None` default.
10. **Backward compatibility**: All new parameters keyword-only with `None` defaults; no new third-party dependencies.
11. **Test file location**: `tests/sprint/test_phase8_halt_fix.py` with 9+ test cases.

---

## Divergence Points

### 1. Phase 0 (Discovery) as explicit phase vs. implicit assumption

- **Opus**: Begins at Phase 1 with implementation. Open questions are resolved in a dedicated "Resolution Recommendations" table at the end (section 7), but no formal discovery phase is specified.
- **Haiku**: Dedicates an explicit Phase 0 (0.5 day) for discovery, interface validation, call-path mapping, and open-question resolution before any code is touched.
- **Impact (Opus)**: Faster start; risks partial wiring if open questions aren't resolved before coding begins. Implementation drift is the primary failure mode.
- **Impact (Haiku)**: Slower start; significantly reduces risk of mid-sprint architectural rework. Explicitly guards against the "false sense of isolation" failure mode.

---

### 2. Phase ordering and sequencing

- **Opus**: Phase 1 = env_vars plumbing → Phase 2 = isolation wiring → Phase 3 = context header → Phase 4 = error/diagnostics fixes → Phase 5 = tests → Phase 6 = smoke.
- **Haiku**: Phase 0 = discovery → Phase 1 = isolation lifecycle → Phase 2 = env propagation → Phase 3 = prompt/detection → Phase 4 = diagnostics/status → Phase 5 = tests → Phase 6 = smoke.
- **Impact (Opus)**: env_vars is treated as a prerequisite to isolation (Phase 1 → Phase 2 dependency). More technically driven sequencing.
- **Impact (Haiku)**: Isolation is treated as highest-value and tackled first (Phase 1), env propagation second (Phase 2). More value-delivery-driven sequencing.

---

### 3. Explicit dependency on env_vars before isolation wiring

- **Opus**: Declares a hard dependency — Phase 2 (isolation) cannot start until Phase 1 (env_vars) is complete. Critical path is `Phase 1 → Phase 2 → Phase 5 → Phase 6`.
- **Haiku**: Treats isolation and env propagation as related but separable — specifically notes isolation and env propagation should remain sequential (they share the subprocess boundary) but does not block Phase 1 on Phase 2.
- **Impact (Opus)**: More conservative; avoids partially-wired isolation. Slightly longer critical path.
- **Impact (Haiku)**: Allows isolation skeleton to be stubbed before env plumbing is finalized, but risks the "false sense of isolation" anti-pattern it explicitly identifies.

---

### 4. OQ-001 resolution: `CLAUDE_WORK_DIR` env var vs. `scoped_work_dir` parameter

- **Opus**: Explicitly recommends `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` over adding a separate `scoped_work_dir` parameter. Notes this reuses the env_vars mechanism being built, but flags a prerequisite: verify that `ClaudeProcess` respects this env var for `@` resolution (OQ-006).
- **Haiku**: Leaves this open — "Use `scoped_work_dir` if already supported. If not, add the minimum viable plumbing required." Does not propose a specific env var name.
- **Impact (Opus)**: Concrete and testable, but carries the OQ-006 unverified assumption risk.
- **Impact (Haiku)**: More flexible but less actionable; implementer must still resolve the question before coding.

---

### 5. OQ-006 treatment (whether `CLAUDE_WORK_DIR` actually controls `@` resolution)

- **Opus**: Lists as an open question with recommendation to verify before Phase 2, with `cwd` of subprocess as fallback.
- **Haiku**: Addresses this implicitly under Risk #2 ("Isolation appears implemented but is not actually enforced") and Smoke Phase milestones, but does not call out the specific env var mechanism by name.
- **Impact (Opus)**: More transparent about a potential architectural gap in its own recommendation.
- **Impact (Haiku)**: Risk framing is higher-signal (calls it high-severity) but resolution path is less specific.

---

### 6. Total phase count

- **Opus**: 6 phases (Phases 1–6).
- **Haiku**: 7 phases (Phases 0–6).
- **Impact**: Haiku's Phase 0 represents a genuine structural difference — it treats discovery as a deliverable with measurable milestones (M0.1–M0.3), not just planning commentary.

---

### 7. Timeline total

- **Opus**: No explicit total given. Effort labels are XS/S qualitative estimates without day counts.
- **Haiku**: Explicit 4.5 working days total with per-phase day estimates.
- **Impact (Opus)**: Less committal; may be appropriate given open questions, but harder to plan around.
- **Impact (Haiku)**: More actionable for scheduling, though estimates could anchor poorly if discovery reveals complexity.

---

### 8. Risk severity for "isolation not enforced"

- **Opus**: Listed as RISK-002 (medium severity) — "env_vars propagation gap."
- **Haiku**: Listed as High-priority Risk #2 — "Isolation appears implemented but is not actually enforced." Elevated framing.
- **Impact (Opus)**: May underweight a foundational architectural risk.
- **Impact (Haiku)**: Correct framing — if `@` resolution is not actually constrained by the mechanism chosen, the entire sprint delivers no value at its core objective.

---

### 9. `PASS_RECOVERED` grep policy

- **Opus**: NFR-005 enforces a policy; mentions the grep in both Phase 4 tasks and the risk table.
- **Haiku**: Mentioned in Phase 0 (discovery) and Phase 4, and referenced in Risk #6. Treated as a discovery artifact first, then a fix.
- **Impact (Opus)**: More prescriptive about what to do with findings.
- **Impact (Haiku)**: Better timing — surfacing gaps during discovery rather than mid-implementation is lower cost.

---

### 10. `DiagnosticBundle` fallback behavior specificity

- **Opus**: OQ-004 recommends fallback to hardcoded path with a deprecation warning log when `config is None`.
- **Haiku**: Recommends "guarded fallback behavior" without specifying deprecation logging. States "prefer migration toward always-supplied config over time."
- **Impact (Opus)**: More immediately actionable; deprecation warning creates a migration signal.
- **Impact (Haiku)**: More conservative; avoids over-specifying fallback behavior that may not be needed.

---

### 11. OQ-005 / extra test for `_determine_phase_status`

- **Opus**: Explicitly recommends adding T04.10 for `_determine_phase_status` error_file plumbing. Estimates "10 minutes of work for meaningful coverage."
- **Haiku**: Lists this as "one more coverage check if missing" in Phase 5 but does not promote it to a named open question.
- **Impact**: Minor. Both recognize the gap; Opus is more directive.

---

### 12. Parallelization of Phase 3 and Phase 4

- **Opus**: States Phases 3 and 4 can proceed concurrently and can both start after Phase 1 (noting Phase 3 has no dependency on Phase 1 at all).
- **Haiku**: States prompt/status work can proceed in parallel with diagnostics fixes after discovery, but explicitly says isolation and env propagation should remain sequential.
- **Impact**: Substantially the same outcome; Opus is slightly more aggressive (Phase 3 can start immediately, no Phase 1 dependency).

---

### 13. Concurrent sprint run risk severity

- **Opus**: RISK-006 (NEW) listed as medium severity. Recommendation: document as unsupported, defer PID-stamped dirs to S4.
- **Haiku**: Risk #8 listed as "Low to Medium." Same mitigation recommendation.
- **Impact**: Effectively identical position with minor severity framing difference.

---

### 14. Structural documentation of architectural priorities

- **Opus**: No explicit architectural priority enumeration. Architecture rationale is embedded in task descriptions and open question resolutions.
- **Haiku**: Opens with a numbered list of four explicit architectural priorities (contain prompt scope, preserve compatibility, harden lifecycle correctness, keep implementation bounded).
- **Impact (Haiku)**: Clearer decision framework for implementers encountering ambiguous tradeoffs. Opus embeds the same reasoning but requires extraction.

---

## Areas Where One Variant Is Clearly Stronger

**Haiku is stronger on:**
- **Risk framing for the core architectural risk** (Risk #2, high severity). The "isolation appears implemented but isn't enforced" failure mode is the scenario that would cause the sprint to ship with zero real value. Haiku's high-severity classification is correct.
- **Explicit discovery phase**. Resolving OQ-001 and OQ-006 (what mechanism actually constrains `@` resolution) before touching execution-critical code is the right sequencing for a hardening sprint.
- **Architectural priority declaration**. Useful as a decision framework when implementers hit ambiguous cases.
- **Timeline quantification**. Day-level estimates are more actionable than XS/S labels.

**Opus is stronger on:**
- **Concrete OQ-001 resolution**. Proposing `CLAUDE_WORK_DIR` env var by name gives the implementer a specific starting point, even if it requires verification.
- **OQ-006 explicit acknowledgment**. Naming the verification requirement and its fallback (subprocess `cwd`) is more honest about the gap in its own recommendation.
- **Deprecation warning on `DiagnosticBundle` fallback**. A concrete migration signal rather than a deferred intention.
- **T04.10 test promotion**. Calling it out as a named open question with an effort estimate makes it less likely to be dropped.

---

## Areas Requiring Debate to Resolve

1. **Is Phase 0 (discovery) a required phase, or can OQ resolution happen as an inline step before Phase 1?**
   The answer depends on how well the team knows the existing codebase. If `ClaudeProcess`, `build_env`, and the `@` resolution mechanism are already well-understood, Phase 0 is overhead. If not, skipping it risks the highest-severity risk in the sprint.

2. **Is `CLAUDE_WORK_DIR` the correct mechanism for constraining `@` resolution, or is subprocess `cwd` the actual lever?**
   This is unresolved in both variants. The answer determines whether Opus's OQ-001 recommendation is valid or whether a different approach is needed. This must be verified before any isolation code is written.

3. **Should Risk #2 / RISK-002 (isolation not actually enforced) be treated as high or medium severity?**
   Haiku's high-severity rating is the architecturally correct position — if isolation is illusory, the sprint's primary objective fails silently. Opus's medium rating may reflect that the risk is mitigatable, but the failure mode warrants high-severity treatment regardless.

4. **Should env_vars plumbing be a prerequisite to isolation wiring (Opus) or a parallel concern (Haiku)?**
   Depends on whether isolation requires env vars to propagate the work dir, or whether subprocess `cwd` is sufficient. Resolving question #2 above resolves this.

5. **Should the `DiagnosticBundle` fallback include a deprecation warning log (Opus) or just silent guarded behavior (Haiku)?**
   Minor debate point. Opus's position is better for long-term maintainability; Haiku's is more minimal. Low stakes but worth aligning on before implementation.
