<!-- Copy of Variant 2: merged-adversarial-analysis.md -->
<!-- Original path: .dev/benchmark/adversarial-output/variant-a-vs-b/merged-adversarial-analysis.md -->

<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant 2 (original) -->
<!-- Merge date: 2026-03-05T00:00:00Z -->

# Pipeline Unification Decision Memo: Targeted Fixes Now, Phased Extraction Later

<!-- Source: Variant 2 (original, modified) — thesis reframed using debate outcome -->
This memo evaluates whether sprint should be refactored to use `execute_pipeline()` as the single orchestration point. Based on the compared analyses and direct code verification, the strongest conclusion is:

1. there **is** real duplication and cleanup debt across sprint, roadmap, and pipeline,
2. but the evidence does **not** currently justify a forced immediate refactor of sprint onto `execute_pipeline()`, and
3. the best near-term path is **targeted remediation plus narrower extractions**, with full executor unification treated as a later design option rather than a required conclusion.

## Verified Current-State Findings

<!-- Source: Variant 1, Section 2 — merged per Change #1 -->
### 1. Roadmap already uses the shared pipeline executor
- Verified in `src/superclaude/cli/roadmap/executor.py:494`: `execute_roadmap()` delegates to `execute_pipeline()`.
- Verified in `src/superclaude/cli/roadmap/executor.py:81`: roadmap-specific subprocess behavior lives in `roadmap_run_step()`.

<!-- Source: Variant 1, Section 2 — merged per Change #1 -->
### 2. Sprint still owns a separate orchestration loop
- Verified in `src/superclaude/cli/sprint/executor.py:32`: `execute_sprint()` runs its own phase loop.
- Verified in `src/superclaude/cli/sprint/executor.py:94`: the loop performs mid-execution monitoring, timeout enforcement, signal handling, watchdog action, debug logging, and TUI updates.

<!-- Source: Variant 1, Sections 2e/2f — merged per Change #2 -->
### 3. There is real duplication in process management
- Verified in `src/superclaude/cli/sprint/process.py:91`, `:128`, `:139`: sprint overrides `start()`, `wait()`, and `terminate()`.
- Compared with `src/superclaude/cli/pipeline/process.py:89`, `:115`, `:126`, those overrides are largely the same lifecycle logic with sprint-specific debug logging layered in.

<!-- Source: Variant 1, Sections 2c/2f — merged per Change #2 -->
### 4. There is also local roadmap debt
- Verified in `src/superclaude/cli/roadmap/executor.py:53`: `_build_subprocess_argv()` exists.
- Verified in `src/superclaude/cli/roadmap/executor.py:103`: actual execution uses `ClaudeProcess(...)` directly instead.
- Code search found no source call sites for `_build_subprocess_argv()`, so it appears to be dead code.
- Verified in `src/superclaude/cli/roadmap/executor.py:112`: roadmap passes input files as `--file` extra args.

## What the Stronger Challenge Gets Right

<!-- Source: Variant 2 (original) -->
### 5. Sprint is not just "roadmap with different callbacks"
Sprint's loop is materially concerned with **during-step** control, not only before/after-step notifications. The verified poll loop in `src/superclaude/cli/sprint/executor.py:94` needs access to:
- the live subprocess handle,
- monitor thread state,
- signal-handler state,
- watchdog configuration,
- and the ability to terminate the process mid-execution.

That means the current `execute_pipeline()` shape in `src/superclaude/cli/pipeline/executor.py:45` is not obviously sufficient to absorb sprint without either:
- broadening its interface substantially, or
- moving sprint's control loop into a `run_step` wrapper, which may reduce very little actual complexity.

### 6. Some claimed shared-executor benefits are overstated for sprint
<!-- Source: Variant 2 (original, modified) — synthesis with debate evidence -->
- `execute_pipeline()` does have retry logic (`src/superclaude/cli/pipeline/executor.py:120`), but retry is not automatically a benefit for side-effectful sprint phases.
- `execute_pipeline()` supports parallel groups (`src/superclaude/cli/pipeline/executor.py:82`), but sprint phases mutate shared working-tree state, so this is not a free win.
- Therefore, the existence of shared executor features is not by itself evidence that sprint should consume them.

## What the Stronger Proposal Still Contributes

<!-- Source: Variant 1, Section 3 — merged per Change #3 -->
### 7. The long-term direction should still be more extraction, not less
Even though immediate total unification is not justified, Variant 1 contributes a useful architectural direction:
- generic process lifecycle hooks should live in the shared layer where possible,
- consumer-specific state persistence can share interface boundaries even if formats remain different,
- and common sequencing/result abstractions should continue to converge when they reduce real duplication.

That makes the right conclusion **phased extraction**, not permanent architectural divergence.

## Recommended Plan

<!-- Source: Variant 2 (original, modified) — merged with Variant 1 architecture sketch per Change #3 -->
### Phase 1 — Low-risk targeted fixes now
1. Remove dead roadmap helper `_build_subprocess_argv()` from `src/superclaude/cli/roadmap/executor.py:53` if no hidden callers exist.
2. Normalize roadmap file-passing behavior deliberately in `roadmap_run_step()` / shared process command building, instead of treating it as an unresolved architectural side effect.
3. Add hook points to shared `pipeline.process.ClaudeProcess` so sprint can stop overriding `start()`, `wait()`, and `terminate()` just to inject debug logging.

### Phase 2 — Extract narrower shared primitives
1. Identify what part of sprint's loop is truly generic versus inherently sprint-specific.
2. Extract only the generic pieces first: state/result normalization, logging hooks, maybe shared cancellation/result interfaces.
3. Do **not** require sprint to adopt `execute_pipeline()` until a concrete `sprint_run_step` design proves that the live control loop becomes simpler rather than merely relocated.

### Phase 3 — Re-evaluate executor unification with a concrete design
Before deciding on full unification, answer these questions with code-level proposals:
1. What is the exact `sprint_run_step(...)` signature?
2. How does it receive monitor state and report TUI updates?
3. Does sprint still need its own internal poll loop?
4. If yes, what complexity is actually removed by wrapping it in `execute_pipeline()`?

If those answers show substantial simplification, revisit unification. If not, keep sprint's executor separate and continue sharing lower-level primitives.

## Confidence and Caveats

<!-- Source: debate synthesis — merged per Change #4 -->
### Verified
- Roadmap uses `execute_pipeline()`.
- Sprint has its own orchestration loop.
- Sprint process overrides duplicate much of the shared process lifecycle.
- Roadmap contains an apparently unused subprocess-argv helper.

### Unverified
- The claim that pipeline was historically extracted from sprint as a half-completed migration.
- The claim that full sprint-to-pipeline unification would reduce net complexity rather than repackage it.

## Final Verdict

<!-- Source: Variant 2 base, informed by Variant 1 strengths -->
Adopt the **targeted-fix approach immediately** and treat **executor unification as a hypothesis to validate**, not a decision already earned by the current evidence. Variant 1 is useful as a source of future extraction ideas; Variant 2 is the better present-tense decision document.
