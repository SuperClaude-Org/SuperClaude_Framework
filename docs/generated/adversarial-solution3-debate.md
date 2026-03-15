# Adversarial Debate: Solution #3 -- Split Phase Prompts to Reduce Context Consumption

**Date:** 2026-03-15
**Format:** 3-round structured adversarial debate
**Subject:** Approach D (Hybrid Summary Header) from the Solution #3 brainstorm
**Artifact:** `docs/generated/solution-3-split-phase-prompts-brainstorm.md`

---

## Grounding Evidence (Pre-Debate)

Before the debate begins, the following facts were verified against source code:

| Claim | Verified? | Evidence |
|-------|-----------|----------|
| `build_prompt()` does NOT reference `tasklist-index.md` | **YES** | `process.py` lines 115-157: prompt contains only `@{phase_file}` and inline instructions. No index path appears anywhere in the string. |
| Phase files are self-contained | **YES** | `phase-2-tasklist.md` (380 lines) contains per-task: deliverable IDs (D-0005 through D-0011), artifact paths, acceptance criteria with `uv run pytest` commands, dependencies, steps, checkpoint blocks with report paths and exit criteria. |
| ~14K token savings per phase is achievable | **PLAUSIBLE** | `tasklist-index.md` is 292 lines (cross-framework sprint). For the 11-phase portify sprint the brainstorm estimates 415 lines / ~14-16K tokens. This is a reasonable estimate at ~35 tokens/line for structured markdown. |
| 4-layer isolation scopes to `config.release_dir` | **YES** | `executor.py` lines 140-172: `setup_isolation()` sets `scoped_work_dir=config.release_dir`. The index file lives in this same directory alongside phase files. Isolation does NOT separate them. |
| The crash occurred at turn 106 with ~169K tokens consumed | **ACCEPTED** | Per brainstorm document, taken as given from the incident report. |

---

## Round 1: Elegance vs. Sufficiency

### PROPONENT

Approach D is the correct first move for three reasons:

**1. The implementation is trivially small.** The entire change is approximately 10 lines added to `build_prompt()` in `process.py`. A sprint summary header (~150-200 tokens) replaces zero-to-14K tokens of index overhead. The ratio of tokens saved to lines of code changed is roughly 1400:1. No new files, no parsing logic, no format coupling.

**2. Phase files are genuinely self-contained.** This is not a hopeful assumption -- it is verified. `phase-2-tasklist.md` contains 7 complete task blocks. Each block includes:
- Deliverable IDs (D-0005 through D-0011)
- Full artifact paths (e.g., `.dev/releases/current/.../artifacts/D-0008/spec.md`)
- Acceptance criteria with executable validation commands
- Task dependencies (e.g., "Dependencies: T02.03")
- Checkpoint blocks with report paths and exit criteria

The index adds the deliverable registry, traceability matrix, and roadmap item registry -- all planning artifacts, not execution artifacts. The agent executing T02.04 does not need to know that D-0008 maps to roadmap item R-016 in a global table. It needs to know where to write the artifact, what the acceptance criteria are, and what to verify. All of that is in the phase file.

**3. The prompt already does not inject the index.** `build_prompt()` (process.py line 122) constructs `f"/sc:task-unified Execute all tasks in @{phase_file}"`. The index is not referenced. The savings come from preventing the agent from voluntarily reading it, which a clear prompt instruction can accomplish: "All required context is in the phase file above. Do not seek additional index files."

This is a zero-risk, high-reward change. Even if it saves only 7% of the context window, that is 14K tokens -- equivalent to roughly 10-15 additional execution turns. For a sprint that crashed at turn 106, those turns matter.

### OPPONENT

I accept that the implementation is small and that phase files contain execution data. But I challenge three assumptions embedded in this proposal:

**Challenge 1: "~14K savings" assumes the index IS being loaded.** The brainstorm explicitly states (section 1, lines 32-37) that it is unknown HOW the index enters context. Three pathways are hypothesized:
1. Claude Code's `@` file resolution scanning adjacent files
2. The `/sc:task-unified` command's internal context-loading
3. The agent itself choosing to read the index

If pathway (1) is the cause, then neither a prompt instruction NOR a summary header will prevent loading -- the `@` resolution mechanism operates before the agent sees the prompt. If pathway (2) is the cause, the fix requires changes to `/sc:task-unified`, not to `build_prompt()`. Only pathway (3) is addressable by a prompt instruction.

The brainstorm does not determine which pathway is active. It lists all three and then proposes a solution that only addresses one. That is a gap in the analysis.

**Challenge 2: "A prompt instruction to not read the index is sufficient" is empirically unsupported.** LLM agents routinely ignore soft directives, especially under context pressure. The brainstorm itself acknowledges this risk (section 6.6, line 307): "If the agent discovers tasklist-index.md in the working directory and reads it for context, we have saved nothing."

The instruction "Do not read tasklist-index.md" is not a guardrail -- it is a suggestion. Agents that are struggling with a complex task and see a file named "tasklist-index.md" in their working directory will read it because it looks helpful. The name itself is an invitation.

**Challenge 3: ~14K is only ~7% of the 200K budget.** The crash occurred at turn 106 with ~169K tokens consumed. That means the agent consumed approximately 169K tokens across 106 turns -- roughly 1.6K tokens per turn on average. Saving 14K tokens buys approximately 8-9 additional turns. The agent had already used 106 turns. Adding 8 more gets it to turn 114. Is that enough? The brainstorm does not demonstrate that the crash was caused by a margin of 14K tokens. It could easily have been a margin of 50K or more.

This solution is not wrong, but it may be solving a problem that accounts for only a fraction of the actual deficit. Calling it "high-impact" overstates its contribution.

---

## Round 2: Combined Impact and Mechanism Robustness

### PROPONENT

I will address each challenge directly.

**On Challenge 1 (loading mechanism):** The opponent correctly identifies that we do not know which pathway loads the index. However, Approach D's summary header is not the only component -- the brainstorm recommends layering Approach A3 (directory isolation) as a hardening option. If the `@` resolution mechanism scans adjacent files (pathway 1), then copying only the phase file to an isolated temp directory blocks all three pathways simultaneously. The summary header addresses the prompt side; directory isolation addresses the filesystem side. Together, they cover all three hypothesized pathways.

I concede that prompt instruction alone is insufficient as a hard guarantee. But combined with directory isolation (~20 additional lines of code), the solution becomes mechanically deterministic: the agent literally cannot read a file that does not exist in its working directory.

**On Challenge 2 (agent compliance):** I agree that soft directives are unreliable. This is precisely why the brainstorm recommends A3 as hardening. But I want to push back on the framing: the prompt instruction is not the primary mechanism. It is a signal to the agent that reduces the probability of voluntary index-seeking. The hard mechanism is directory isolation.

Furthermore, the current 4-layer isolation system (executor.py lines 96-172) already restricts `scoped_work_dir` to `config.release_dir`. The gap is that the index lives in the same directory as the phase files. Changing `scoped_work_dir` to a phase-specific subdirectory is a targeted refinement of an existing isolation mechanism, not a new architectural pattern.

**On Challenge 3 (sufficiency):** I never claimed this solution alone prevents the crash. The brainstorm explicitly states (section 7, line 329): "This alone may not prevent exhaustion but combined with Solution #1 (turn budget) and Solution #2 (context compression) creates significant headroom." The combined impact estimate (section 8, line 342) projects 25-40K tokens recovered per phase across Solutions #1 + #2 + #3. Solution #3 contributes 14K of that budget.

The question is not "Does Solution #3 alone prevent the crash?" but "Is Solution #3 a necessary component of the combined mitigation?" The answer is yes: 14K tokens is the single largest recoverable static cost. No other single change recovers as many tokens for as few lines of code.

### OPPONENT

The proponent's defense is stronger with directory isolation included, but this shifts the proposal. The brainstorm recommends Approach D (summary header + prompt instruction) as the primary fix, with A3 as an "optional hardening." If A3 is actually required for correctness, then the recommendation should state that clearly -- not present it as optional.

**New Challenge 4: Cross-phase validation requires the index in some sprint configurations.** Consider a phase file that declares "Dependencies: T02.01, T02.02" -- the agent knows WHAT to check, but does it know WHERE the artifacts from those tasks are? In the current phase file format, the artifact paths are listed only for the current phase's tasks, not for dependency tasks from prior phases. If T03.01 depends on D-0005 (produced by T02.01), T03.01's task block says "Dependencies: T02.01" but does not list D-0005's artifact path. The agent currently resolves this by reading the index's deliverable registry.

With the index removed and no compensating context, the agent must either:
(a) Guess the artifact path convention (fragile)
(b) Search the filesystem for the artifact (token-expensive)
(c) Fail the dependency check (incorrect)

The brainstorm dismisses this concern (section 4, line 201): "Item 4 is already handled by the dependency annotations in each task." But dependency annotations specify task IDs, not artifact paths. This is a semantic gap.

**New Challenge 5: The `@` file resolution mechanism is a black box.** Claude Code's `@` syntax is not documented in this codebase. We do not know if `@{phase_file}` causes Claude Code to:
(a) Load only that exact file
(b) Load the file plus its parent directory listing
(c) Load the file plus files referenced within it
(d) Load the file plus contextually related files

If the answer is (b), (c), or (d), then the index might be loaded as a side effect of `@` resolution regardless of prompt instructions. Directory isolation (A3) addresses this, but again -- the brainstorm presents A3 as optional. If we cannot verify the `@` resolution behavior, A3 should be mandatory.

### PROPONENT

**On Challenge 4 (cross-phase artifact paths):** This is a valid concern but it has a simple solution that fits within Approach D. The summary header can include a "Previous phase artifacts" line:

```
- Previous phase artifacts: artifacts/D-0005/, artifacts/D-0006/, artifacts/D-0007/, artifacts/D-0008/
```

This adds approximately 50-100 tokens and resolves the path resolution gap completely. The brainstorm actually proposes this (section 4, lines 226-230). The agent sees the artifact directory listing, can locate any prior-phase deliverable by ID pattern, and does not need the full deliverable registry.

**On Challenge 5 (`@` resolution is a black box):** Conceded. We do not know the `@` resolution behavior. Given this uncertainty, A3 (directory isolation) should be promoted from "optional hardening" to "required component." The recommendation should be: **Approach D + A3 as a mandatory pair**, not Approach D alone with A3 as optional.

This does increase the implementation from ~10 lines to ~30 lines, but the complexity remains low: copy the phase file to a temp directory, set `scoped_work_dir` to that directory, and clean up after execution.

---

## Round 3: Synthesis and Refined Recommendation

### PROPONENT (Closing)

The debate has refined the proposal in three ways:

1. **Directory isolation (A3) must be mandatory, not optional.** The `@` resolution mechanism is undocumented and the index lives alongside phase files. Only filesystem-level separation guarantees the index is not loaded.

2. **The summary header should include prior-phase artifact paths.** This compensates for the cross-phase artifact resolution gap with ~50-100 additional tokens.

3. **Solution #3 is necessary but not sufficient.** It recovers ~14K tokens per phase -- the largest single static cost -- but must be combined with turn budget management (#1) and context compression (#2) to prevent the crash.

The solution remains low-effort (30 lines), high-impact (14K tokens/phase), and mechanically deterministic (no reliance on agent compliance).

### OPPONENT (Closing)

I accept the refined proposal with the caveats documented. My remaining concerns:

1. **The 14K savings estimate should be treated as an upper bound, not a guarantee.** If the index was never loaded in the first place (because the agent did not happen to read it in the crashing run), the savings are zero. The brainstorm does not prove the index WAS loaded -- it only shows it COULD be.

2. **Directory isolation introduces a temp directory lifecycle concern.** If the sprint executor crashes between creating the temp directory and cleaning it up, orphaned temp directories accumulate. This is minor but should be handled (e.g., cleanup in the `finally` block of `execute_sprint()`).

3. **The solution's impact should be measured empirically.** Before claiming 14K savings, run a controlled test: execute a phase with and without the index present, measure actual context consumption, and verify the delta.

These are implementation-quality concerns, not architectural objections. I concur that Approach D + A3 is a sound component of the combined mitigation strategy.

---

## Convergence Assessment

| Point | Proponent | Opponent | Converged? |
|-------|-----------|----------|------------|
| Phase files are self-contained for execution | Agree | Agree | **YES** (100%) |
| Index is a planning artifact, not execution artifact | Agree | Agree with caveat (cross-phase paths) | **YES** (90%) |
| ~14K token savings estimate | Accept as upper bound | Accept as upper bound | **YES** (85%) |
| Prompt instruction alone is insufficient | Conceded in R2 | Asserted in R1 | **YES** (100%) |
| Directory isolation (A3) must be mandatory | Accepted in R2 | Asserted in R2 | **YES** (100%) |
| Solution alone prevents the crash | Never claimed | Confirmed not sufficient | **YES** (100%) |
| Summary header should include prior-phase artifacts | Proposed in R2 | Accepted | **YES** (95%) |
| `@` resolution behavior is unknown | Conceded | Asserted | **YES** (100%) |
| Empirical validation needed | Not initially addressed | Asserted in R3 | **YES** (80%) |

**Overall convergence: 94%**

---

## Final Recommendation

### Classification

Solution #3 (Approach D + A3) is **NECESSARY but NOT SUFFICIENT**. It is a required component of the combined mitigation, not a standalone fix.

### Refined Implementation Specification

**Component 1: Sprint Summary Header (Approach D)**
- Add ~200 tokens of sprint context to `build_prompt()` in `process.py`
- Include: sprint name, phase number/total, artifact root, results dir, execution log path, prior-phase artifact directories
- Add explicit instruction: "All task details are in the phase file. Do not seek additional index files."
- Estimated token cost: ~200 tokens per phase

**Component 2: Phase-Specific Directory Isolation (Approach A3) -- MANDATORY**
- Before spawning subprocess, copy the phase file to a temp directory under `config.results_dir/.isolation/phase-{N}/`
- Set `scoped_work_dir` to this isolated directory instead of `config.release_dir`
- Clean up in the `finally` block of the execution loop
- Also add startup cleanup for any orphaned isolation directories from prior crashed runs
- Estimated implementation: ~30 lines in `executor.py`

**Component 3: Empirical Validation (pre-merge requirement)**
- Instrument context consumption measurement for at least one phase execution
- Compare: baseline (index accessible) vs. isolated (index removed from working directory)
- If delta is <5K tokens, the index was likely never loaded and the savings are lower than projected
- If delta is >10K tokens, the index was being loaded and the fix is confirmed effective

### Token Budget Summary

| Component | Tokens Added | Tokens Saved | Net |
|-----------|-------------|-------------|-----|
| Summary header | +200 | 0 | -200 |
| Index elimination (if was loaded) | 0 | ~14K | +14K |
| **Net savings per phase** | | | **~13.8K** |
| **Net savings (11-phase sprint)** | | | **~151.8K** |

### Scope Boundaries

**This solution addresses:** Static token overhead from the tasklist-index.md being present in the agent's working directory.

**This solution does NOT address:**
- Dynamic context growth from tool calls, file reads, and code generation during execution (addressed by Solution #2)
- Runaway turn consumption without budget enforcement (addressed by Solution #1)
- Fundamental context window limits for task-heavy phases (addressed by Solution #5, task splitting)
- The unknown `@` file resolution behavior in general (requires Claude Code documentation or experimentation)

### Risk Register (Post-Debate)

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| Index was never loaded (savings = 0) | Medium | Empirical validation before claiming victory | Open |
| `@` resolution loads adjacent files | Medium | Directory isolation (A3, now mandatory) | Mitigated |
| Agent ignores prompt instruction | Low | Directory isolation makes instruction redundant | Mitigated |
| Cross-phase artifact path resolution | Low | Prior-phase artifact list in summary header | Mitigated |
| Orphaned temp directories on crash | Very Low | Cleanup in `finally` block + startup sweep | Mitigated |
| Phase file format changes break assumption | Very Low | Phase files are generated by the same system | Accepted |

---

## Debate Metadata

- **Rounds completed:** 3
- **Convergence score:** 94%
- **Unresolved conflicts:** 1 (empirical validation not yet performed)
- **Key refinements from debate:**
  1. A3 promoted from optional to mandatory
  2. Prior-phase artifact paths added to summary header
  3. Empirical validation added as pre-merge gate
  4. 14K savings reframed as upper bound pending measurement
