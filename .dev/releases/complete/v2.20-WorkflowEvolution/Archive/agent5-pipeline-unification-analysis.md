# Agent 5: Pipeline Unification Spec Diagnostic Analysis

**Source**: `.dev/releases/complete/v2.13-CLIRunner-PipelineUnification/release-spec.md`
**Supporting**: `merged-pipeline-decision.md`, `extraction.md`, `test-strategy.md`
**Scope**: Diagnostic only — no fixes proposed

---

## 1. Top 3 Theories for Why Bugs Survive Despite Planning Rigor

### Theory 1: Spec Designs Against Existing Behavior, Not Against Actual Runtime Interactions

The v2.13 spec is extremely thorough at analyzing *static code structure* — line-by-line diffs of method overrides, grep verification of imports, inheritance hierarchies. But it systematically avoids analyzing *dynamic runtime behavior*: what actually happens when these components interact under real subprocess workloads.

**Evidence**: The entire Section 9.2 ("Precise Diff Analysis: What Actually Differs") compares code **textually** — "Sprint lines 91-126 vs Pipeline lines 89-113." It concludes `wait()` is "pure no-op duplication" based on reading the source. But the analysis never validates this claim by instrumenting the running system. The assertion "Delete it with zero behavioral change" (Section 9.2, wait() analysis) is a *code-reading conclusion*, not a *runtime-verified conclusion*.

The spec acknowledges this gap implicitly: D4 (characterization tests) exists precisely because "Sprint's `execute_sprint()` has partial test coverage — 4 integration tests exist... 6 subsystems remain untested" (Section 3, D4). The spec plans to write the safety net *during* the release, meaning all the design decisions in Sections 9.1–9.10 were made without the safety net being in place. The analysis of what's safe to delete was conducted without tests to confirm it.

**Why bugs survive**: Specs analyze code as text, declare equivalences based on reading, and defer runtime validation to a later phase. By the time tests exist, design decisions are already locked.

### Theory 2: The Validation Architecture Has a Single Checkpoint For All Work

The test strategy document reveals a structural flaw: with a 1:3 interleave ratio and 3 work milestones, there is **exactly one validation milestone (V1)** placed **after all work is complete** (after M3).

> "With a 1:3 interleave ratio and 3 work milestones (M1, M2, M3), one validation milestone V1 is placed after M3. V1 (= M4 in the roadmap) validates all preceding work milestones." — test-strategy.md, Validation Milestones table

This means M1 (characterization tests), M2a (delete wait), M2b (add hooks + migrate sprint), M2c (delete dead code), and M3 (file-passing fix) all execute sequentially before any external validation checkpoint. The spec *says* "D4 tests must pass before and after changes" (NFR-003), but the validation *architecture* places the only formal check at the end. The intermediate "run tests before/after" steps are informal — they depend on the implementing agent's discipline, not on a structural gate.

**Why bugs survive**: The workflow trusts that implementers will self-validate at each step, but the formal validation architecture is end-loaded. By the time the single checkpoint fires, the change surface is large and failure attribution is harder.

### Theory 3: Edge Cases Are Enumerated But Not Converted Into Mandatory Test Cases

Section 9.6 enumerates five edge cases with remarkable precision. But the spec does not mandate that each edge case becomes a test:

- **Edge Case 1** (hook exception during SIGTERM): "This is acceptable — a buggy hook should surface loudly." The spec explicitly decides NOT to handle this and NOT to test it. No characterization test pins this behavior.
- **Edge Case 3** (`was_timeout` in exit hook): The spec acknowledges dropping the `_timed_out` cross-reference and says "Accept `was_timeout=(returncode == 124)`." But the D4 characterization test matrix (Section 3, D4 table) has no row testing the timeout-indicator discrepancy between the old `_timed_out` flag and the new `returncode == 124` heuristic.
- **Edge Case 5** (`on_exit` not called in `wait()` path): The spec identifies this as a gap and proposes adding the call. This is a **behavioral addition** acknowledged as such ("This is a **behavioral addition**"). But the characterization tests are supposed to "pin current behavior — they document what IS, not what SHOULD BE" (D4 AC-3). This creates a contradiction: the spec simultaneously requires tests that pin current behavior AND a change that adds new behavior to the same code path.

**Why bugs survive**: Edge cases are identified through analysis but treated as documentation rather than being converted into mandatory test requirements. The analysis demonstrates awareness without creating enforcement.

---

## 2. Blind Spots Identified

### Blind Spot A: No Integration Testing Between Hook Migration and Executor Behavior

The spec designs hooks in isolation (pipeline base class) and designs hook factories in isolation (sprint process). But the D4 test matrix only covers executor subsystems — it never tests the *interaction* between the new hooks and the executor's poll loop, signal handling, or TUI.

The test plan (Section 3, D4 table) has rows for "Phase sequencing," "Subprocess lifecycle," "Signal handling," "TUI integration," "Monitor thread," "Stall detection," "Multi-phase," "Diagnostics," and "Tmux." None of these explicitly test that the hook callbacks correctly fire during executor-managed subprocess lifecycle. The hooks are base-class features; the executor tests are executor-level features. The integration between these two layers is assumed, never verified.

### Blind Spot B: The `was_timeout` Behavioral Change Is Buried in Edge Case Notes

The spec's Section 9.6 Edge Case 3 documents a subtle behavioral change: sprint currently uses `was_timeout=(rc == 124 or getattr(self, "_timed_out", False))`, but after migration it will use only `returncode == 124`. The spec argues this is acceptable because "the executor handles timeout classification upstream."

But the spec never validates this claim. It asserts that `_timed_out` was "belt-and-suspenders" but doesn't trace all code paths where `_timed_out` is set vs where `returncode == 124` occurs. What if the executor sets `_timed_out = True` and then calls `terminate()`, resulting in returncode -15 (SIGTERM), not 124? The exit hook would now report `was_timeout=False` when the old code would have reported `was_timeout=True`. The spec acknowledges this exact scenario ("When the executor sets `_timed_out = True` and calls `terminate()`, the process returncode after SIGTERM/SIGKILL will NOT be 124 — it'll be -15 or -9") but dismisses it as acceptable without verifying downstream consumers of `was_timeout`.

### Blind Spot C: The Complexity Classification Contradicts Its Own Evidence

The extraction document classifies the release as `complexity_class: LOW` with `complexity_score: 0.367`. The test strategy also declares `complexity_class: LOW`. But the release spec itself says "complexity_class: MEDIUM" in its frontmatter. The adversarial decision document describes the effort as "Large" for the rejected options and "Small to Medium" for the selected option.

This inconsistency means the validation rigor (interleave ratio 1:3, single validation checkpoint) was calibrated for LOW complexity. If the actual complexity is MEDIUM — as the spec's own frontmatter declares — the validation is under-provisioned.

### Blind Spot D: The Spec Assumes Mocked Subprocess Tests Are Sufficient for Process Lifecycle

D4 AC-2 requires: "Tests use mocked subprocess (no real claude invocation)." The spec never questions whether mocked subprocesses faithfully represent the signal-handling, timeout, and process-group behaviors that the hooks are designed to observe.

The SIGTERM/SIGKILL escalation path (the highest-risk behavioral concern, RISK-001) involves real OS signals, real process group semantics, and real timing. Mocked subprocess objects don't have process groups, don't respond to signals, and don't have real timeouts. The spec's risk mitigation for RISK-001 is "D4 characterization tests pin signal handling; run before/after D1" — but D4 AC-2 mandates mocks. The mitigation strategy is structurally incapable of catching the risk it claims to mitigate.

### Blind Spot E: No Validation of the "Zero Imports" NFR Under Hook Architecture

NFR-002 requires "Pipeline module maintains zero imports from superclaude.cli.sprint or superclaude.cli.roadmap." The verification is `grep -r`. But the hook architecture introduces a new coupling vector: the *semantic contract* of what hooks receive. If pipeline's `on_spawn` hook starts passing different arguments, sprint's hook factories silently break. Grep can't detect semantic coupling — only import-level coupling. The spec's compliance mechanism (grep) doesn't match the new risk profile (semantic contracts across module boundaries without shared type definitions).

---

## 3. Confidence vs Reality Gaps

### Gap 1: "Pure no-op duplication — delete with zero behavioral change" vs. Untested Reality

The spec declares sprint's `wait()` override is "pure no-op duplication" and can be deleted "with zero behavioral change" (Section 9.2). This is stated with absolute confidence. Yet the same spec acknowledges that sprint has ~45% executor test coverage and 6 untested subsystems. The confidence in the deletion safety is derived from code reading, not from test evidence.

**Confidence level asserted**: Absolute ("zero behavioral change")
**Evidence level available**: Code reading only; no tests verify `wait()` behavior equivalence at runtime

### Gap 2: Complexity Score 0.367 ("LOW") vs. 10 Functional Requirements and 7 Interleaved Subsystems

The extraction pipeline scores this release at 0.367 (LOW). The spec itself contains 10 functional requirements, 4 non-functional requirements, 5 edge cases requiring design decisions, and touches code managing 7 interleaved subsystems (subprocess lifecycle, monitor threads, monotonic timeouts, watchdog, tmux, diagnostics, structured logs). The adversarial debate required 3 rounds to reach 0.72 convergence and never fully converged.

**Confidence level asserted**: LOW complexity (automated scoring)
**Reality indicators**: MEDIUM-to-HIGH design complexity, cross-cutting concerns, behavioral changes buried in edge case notes

### Gap 3: "All Actual Bugs Fixed" vs. Bug Discovery Limited to Static Analysis

The decision document's Option 3 summary states: "All actual bugs fixed: Yes." The spec declares all known bugs addressed. But bug discovery was limited to code reading and adversarial debate about architecture. No fuzzing, no integration test runs against the current code, no production telemetry analysis. The spec fixes bugs it *found through reading*. It cannot claim to fix bugs that require *running the system* to discover.

**Confidence level asserted**: All bugs addressed
**Reality gap**: Only bugs discoverable through static analysis and debate were in scope; runtime bugs, race conditions in the poll loop, and environment-specific subprocess behaviors were never examined

### Gap 4: "Characterization Tests Pin Current Behavior" vs. D4 AC-3 Contradiction

D4 AC-3 states: "Tests pin current behavior — they document what IS, not what SHOULD BE." But Section 9.6 Edge Case 5 proposes adding `on_exit` to the `wait()` success path — described as "a behavioral addition." The characterization tests are supposed to be written in M1 *before* changes, pinning current behavior. But the hook migration in M2b *adds* the `on_exit` call to `wait()`. Any characterization test pinning the current `wait()` behavior (no exit logging) would *fail* after M2b.

The spec does not address this: should the characterization test be updated after M2b to reflect the new behavior? If so, it's no longer a characterization test — it's a specification test. This semantic confusion means the test's role shifts mid-release without explicit acknowledgment.

**Confidence level asserted**: Characterization tests provide safety net for refactoring
**Reality gap**: The tests must change during the same release they're supposed to protect, undermining their safety-net function

---

## 4. Evidence Citations

| Finding | Source Document | Section/Location | Exact Quote or Reference |
|---------|----------------|------------------|--------------------------|
| Static-only analysis of wait() | release-spec.md | Section 9.2, wait() table | "Conclusion: Sprint's `wait()` override is a pure no-op duplication. Delete it with zero behavioral change." |
| Single validation checkpoint | test-strategy.md | Validation Milestones table | "one validation milestone V1 is placed after M3. V1 (= M4 in the roadmap) validates all preceding work milestones" |
| Interleave ratio calibrated to LOW | test-strategy.md | Frontmatter | "complexity_class: LOW" and "interleave_ratio: 1:3" |
| Spec self-declares MEDIUM | release-spec.md | Frontmatter | "complexity_class: MEDIUM" |
| Edge case identified but not tested | release-spec.md | Section 9.6, Edge Case 1 | "This is acceptable — a buggy hook should surface loudly... Do NOT wrap hooks in try/except" |
| was_timeout behavioral change | release-spec.md | Section 9.6, Edge Case 3 | "When the executor sets `_timed_out = True` and calls `terminate()`, the process returncode after SIGTERM/SIGKILL will NOT be 124" |
| Mocked subprocess mandate | release-spec.md | D4 AC-2 | "Tests use mocked subprocess (no real claude invocation)" |
| RISK-001 mitigation via D4 | release-spec.md | Section 6, Risk Register | "D4 characterization tests pin signal handling; run before/after D1" |
| Zero executor tests at design time | merged-pipeline-decision.md | Challenge 4 | "Sprint currently has zero executor-level unit tests (a pre-existing gap)" |
| Corrected to ~45% coverage | release-spec.md | Section 9.5 | "Actual coverage... Coverage is approximately 45%" |
| Characterization test role | release-spec.md | D4 AC-3 | "Tests pin current behavior — they document what IS, not what SHOULD BE" |
| Behavioral addition to wait() | release-spec.md | Section 9.6, Edge Case 5 | "This is a **behavioral addition** (new logging in the normal exit path) but is the correct design" |
| All bugs claimed fixed | merged-pipeline-decision.md | Option 3 table | "All actual bugs fixed: Yes" |
| Poll loop complexity | merged-pipeline-decision.md | Challenge 3 | "Sprint's poll loop... interleaves concerns that operate during step execution, not before or after" — lists 4 concurrent concerns |
| Convergence never reached | merged-pipeline-decision.md | Frontmatter | "convergence: 0.72" (below the typical 0.85+ threshold for high confidence) |
| Hook semantic coupling | release-spec.md | Section 9.3 | "Hook type signatures: OnSpawnHook = Callable[[int, list[str]], None]" — no shared type definition enforced across consumers |

---

*Analysis generated by Agent 5 — Pipeline Unification Spec Review*
*Date: 2026-03-08*
