# Refactoring Plan

**Base**: Approach 2 (claude -p as Primary Invocation)
**Sources**: Approach 1 (Empirical Probe First), Approach 3 (Hybrid Dual-Path)
**Date**: 2026-02-23

---

## Strengths to Absorb

### From Approach 1

| # | Element | Source Section | Target in Base | Integration Approach | Risk |
|---|---------|---------------|----------------|---------------------|------|
| A1-1 | Behavioral adherence rubric (20-point, 5 categories) | Ap1 §3 (Scoring Rubric for T05) | Extended Task 0.0 (4th test) + post-implementation verification | Simplify from 20-point to 3-category binary check for Task 0.0. Retain full 20-point rubric as post-implementation verification criteria in the Verification Plan (Section 7). | Low |
| A1-2 | Multi-round debate verification (automated grep checks) | Ap1 §T07 | Post-implementation verification criteria | Add round-marker grep checks from T07 to Verification Plan as automated validation step. | Low |
| A1-3 | Decision gate structure (Gate 2 quality thresholds) | Ap1 §4 (Gate 2) | Task 0.0 decision gate enhancement | Incorporate: behavioral adherence "present" for all 3 categories, artifact production check, multi-round marker check. Adapt from Ap1's 4-condition gate to a simplified 3-condition gate within the 4th probe test. | Low |
| A1-4 | Context window pressure awareness | Ap1 §T12 | Risk register addition | Add SKILL.md token measurement as informational output during Task 0.0. Not a gate — just logged for diagnostics. | Low |

### From Approach 3

| # | Element | Source Section | Target in Base | Integration Approach | Risk |
|---|---------|---------------|----------------|---------------------|------|
| A3-1 | Enhanced 5-step Task-agent fallback (F1-F5) | Ap3 §4 (Path B) | Replace Ap2's 3-step fallback (step 3d-iv) | Upgrade F1/F2-3/F4-5 to F1/F2/F3/F4/F5 with real convergence tracking. Adopt Ap3's prompt templates for F2 (diff analysis), F3 (multi-round debate), F4 (hybrid scoring), F5 (refactor+merge). Retain Ap2's primary/fallback framing — this is still a fallback, not a peer path. | Medium |
| A3-2 | Real convergence tracking in fallback | Ap3 §4 (real_convergence_tracking) | Fallback F3 (debate) orchestrator step | Replace hardcoded 0.5 sentinel with per-point convergence computation after each debate round. Adopt Ap3's orchestrator prompt that evaluates per-diff-point agreement. | Medium |
| A3-3 | `invocation_method` return contract field | Ap3 §5 (return_contract_schema_v2) | Task 3.1 return contract schema | Add as optional 10th field. Values: "headless" or "task_agent". Consumer must NOT branch on this field (informational only). Already proposed in Ap2 §3 Task 3.1 — Ap3 provides the full enum including "headless+task_agent" for mid-pipeline awareness. | Low |
| A3-4 | Simplified mid-pipeline awareness | Ap3 §3 (mid_pipeline_fallover) | Step 3d-iv fallback entry point | 3-state model: (A) no artifacts → full F1-F5, (B) variant files present → start from F2, (C) diff-analysis.md present → start from F3. Scan output directory before starting fallback. Log which artifacts were preserved from headless session. | Medium |
| A3-5 | Instruction delivery protocol for Task agents | Ap3 §4 (instruction_delivery_protocol) | Fallback F2-F5 Task agent dispatches | Each Task agent receives instructions inline (extracted from SKILL.md), NOT as a file reference. sc:roadmap reads SKILL.md once, extracts relevant sections, injects into each Task prompt. | Low |

---

## Weaknesses to Patch

### In the Base (Approach 2)

| # | Weakness | Evidence from Debate | Patch |
|---|----------|---------------------|-------|
| W-1 | Task 0.0 probe tests mechanics only, not behavioral adherence | Round 1 A1 critique; Round 2 A2 concession | Add 4th probe test: mini-pipeline execution on tiny fixtures with 3-category binary adherence check (Diff Analysis present? Multi-round debate present? Artifacts written to disk?). See A1-1. |
| W-2 | Fallback is compressed 3-step with 0.5 convergence sentinel | Round 1 A3 strength #3; Round 2 A2 partial concession | Upgrade to 5-step fallback (A3-1, A3-2). |
| W-3 | No mid-pipeline recovery | Round 1 A3 strength #2; Round 2 A2 partial concession | Add 3-state artifact scan before fallback execution (A3-4). |
| W-4 | No post-implementation quality verification criteria | Round 1 A1 strength #3 | Add Ap1's 20-point behavioral adherence rubric as Verification Plan acceptance criteria. |
| W-5 | SKILL.md token size not measured or documented | Ap1 T12, Ap2 R-NEW-3 | Add SKILL.md token estimation as Task 0.0 informational output. Log but don't gate on it. |

### In the Absorbed Elements

| # | Weakness | Evidence | Patch |
|---|----------|----------|-------|
| W-6 | Ap3's F1-F5 prompt templates reference SKILL.md line numbers that may change | Ap3 §4 instruction_delivery_protocol example references "lines 411-749" | Replace line-number references with section-heading references. Task agents receive content extracted by heading match, not line range. |
| W-7 | Ap3's convergence tracking requires an orchestrator Task agent per round | Ap3 §4 F3 convergence_tracking | Keep orchestrator pattern but note: this adds 1 Task agent dispatch per debate round. For `--depth standard` (2 rounds), that's 2 extra Task dispatches. Acceptable overhead for real convergence. |

---

## Elements Explicitly Rejected

| # | Element | Source | Rationale |
|---|---------|--------|-----------|
| R-1 | `--invocation-mode` flag | Ap3 §2 | YAGNI. Routing should be automatic and invisible. Adding a user-facing flag for an internal implementation detail violates the principle that consumers shouldn't know or care how the pipeline is invoked. |
| R-2 | Depth-based routing (quick→inline, standard/deep→headless) | Ap3 §2 step_3_depth_routing | Premature optimization. Headless startup overhead (5-10s) is negligible vs pipeline execution (2-30 min). All depths should attempt headless first. |
| R-3 | "First-class peer" framing for dual paths | Ap3 §1 Philosophy | The primary/fallback hierarchy is clearer, simpler, and easier to maintain. "Both paths are first-class" sounds egalitarian but doubles the testing and maintenance burden without proportional benefit. |
| R-4 | Full 5-level artifact inventory for fallover | Ap3 §3 resume_logic | Over-engineered. The 3-state model (nothing/variants/diff-analysis) captures the realistic failure modes. Steps 3-5 failures are rare enough that restarting from the last clean checkpoint is acceptable. |
| R-5 | 10-run reliability test (T11) | Ap1 §T11 | Costs $15-25 and 45 minutes. Not justified within sprint scope. If reliability issues emerge, they'll surface during normal usage and can be addressed with retry logic. |
| R-6 | Full 13-test probe suite | Ap1 §2 (T01-T13) | Over-scoped. T09 (model differentiation), T11 (10-run reliability), T12 (context pressure as a separate test), T13 (error handling edge cases) are not needed as pre-implementation gates. The 4-test reduced probe provides sufficient confidence. |
| R-7 | Probe runner shell script (probe-runner.sh) | Ap1 §3 (Test Harness) | Infrastructure for a one-time probe is over-engineering. The 4 tests can run as inline Bash commands within Claude Code. |
| R-8 | `fallback_mode` field deprecation | Ap3 §5 return_contract_schema_v2 | Don't deprecate a field in the same sprint you're modifying the schema. Keep `fallback_mode` with existing semantics: true when Task-agent fallback was used, false when headless succeeded. |
| R-9 | Routing decision cache | Ap3 §2 | YAGNI. There's only one adversarial invocation per sc:roadmap execution. No need to cache a routing decision. |
| R-10 | Task-agent smoke test in capability probe | Ap3 §5 phase_B_task_agent_smoke_test | The Task tool is a core Claude Code capability. It doesn't need a viability probe. If Task agents stop working, everything is broken, not just the adversarial pipeline. |

---

## Refactoring Priority Order

1. **W-1**: Extend Task 0.0 probe (behavioral adherence test) — Blocks implementation
2. **A3-1 + A3-2 + W-2**: Upgrade fallback to 5-step with real convergence — Core quality improvement
3. **A3-4 + W-3**: Add 3-state mid-pipeline awareness — Protects partial work
4. **A3-5 + W-6**: Instruction delivery via section-heading extraction — Enables quality fallback
5. **A1-1 + W-4**: Full 20-point rubric as verification criteria — Post-implementation quality gate
6. **A3-3**: `invocation_method` field — Observability improvement
7. **A1-2**: Automated round-marker verification — Regression safety
8. **A1-4 + W-5**: Context window measurement — Diagnostics
