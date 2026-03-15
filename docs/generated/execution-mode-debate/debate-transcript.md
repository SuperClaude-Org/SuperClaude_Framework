# Debate Transcript -- execution_mode Annotation Value Set (Q7)

## Debate Configuration

- **Topic**: What annotation values should `execution_mode` support?
- **Dimensions**: Necessity, Clarity, Composability, Forward Compatibility, Implementation Cost
- **Positions**: Advocate-Minimal (3 values) vs Advocate-Expanded (5 values)
- **Rounds**: 3

---

## Round 1: Opening Arguments

### Advocate-Minimal Position: {claude, python, skip}

Three values cover all current and near-future needs:

1. **claude** (default): Current behavior. Implicit when no annotation present. Zero implementation cost.

2. **python**: Deterministic shell execution. Covers Phase 1's empirical validation gate (shell commands with output capture). The gate semantics are not a property of the execution mode -- they are a property of the phase's dependency graph. A phase that runs in `python` mode and produces a result artifact can be consumed by downstream phase dependencies regardless of whether we call it `python` or `python-gate`. The gate logic belongs in the dependency/condition system, not in the execution mode enum.

3. **skip**: Explicit deactivation. Covers conditional phases (Phase 5 when WORKING). Clear, unambiguous, zero-cost.

**Rejected values and reasoning:**

- **python-gate**: Conflates execution mechanism with flow control. The "gate" behavior should be expressed through the dependency system (e.g., `condition: "phase-1.result == BROKEN"`). Embedding flow control in the execution mode creates a parallel control-flow mechanism that competes with the dependency graph.

- **hybrid**: Violates phase-level annotation granularity. If you need mixed execution, split into two phases.

- **dry-run**: Already covered by `--dry-run` CLI flag on the sprint runner. An annotation value that duplicates a CLI flag is a design smell.

- **manual**: Interesting but premature. No current use case. When needed, it can be added as a fourth value without breaking anything.

### Advocate-Expanded Position: {claude, python, python-gate, skip, manual}

Five values provide complete coverage without overreach:

1. **claude**: Agreed with Minimal.

2. **python**: Agreed on mechanism, but insufficient alone for gating use cases.

3. **python-gate**: Essential distinction. The difference between "run these shell commands" and "run these shell commands AND use the result to activate/deactivate downstream phases" is semantically important. Consider:
   - A `python` phase that runs linting checks -- its results are informational, downstream phases always run.
   - A `python-gate` phase that checks CLI availability -- its results control whether Phase 5 exists at all.

   Pushing gate semantics into the dependency system is theoretically clean but practically awkward. The v2.24.5 tasklist already expresses this as prose ("Activates only if Phase 1 result is BROKEN"), which proves the current dependency system cannot handle it formally. `python-gate` makes this machine-readable.

4. **skip**: Agreed with Minimal.

5. **manual**: Not premature -- it addresses a real pattern. Phase 7 (Commit and Release) involves human decisions (version number confirmation, tag creation). Currently modeled as EXEMPT claude tasks, but the runner cannot actually pause for human input. `manual` formalizes this need and prevents the runner from attempting to automate inherently human decisions.

**Rejected values and reasoning:**

- **hybrid**: Agreed this breaks the annotation model. Split phases instead.
- **dry-run**: Agreed this duplicates CLI functionality.

---

## Round 2: Cross-Examination

### Dimension 1: Necessity (YAGNI Analysis)

**Advocate-Minimal attacks python-gate:**
> The v2.24.5 tasklist has exactly ONE gating phase (Phase 1). Building a dedicated `python-gate` mode for a single use case violates YAGNI. When a second gating pattern emerges, you can add it then. The current prose-based conditionality works -- the sprint runner already handles it (Phase 5's activation header says "Activates only if Phase 1 result is BROKEN").

**Advocate-Expanded defends python-gate:**
> The prose-based conditionality "works" only because a human reads it. The sprint runner's executor currently has NO code path that reads Phase 1's result and conditionally skips Phase 5. It relies on the Claude subprocess to interpret the prose. This is exactly the kind of non-determinism that `python-gate` eliminates. The annotation makes the gating machine-readable for the runner itself.

**Advocate-Minimal attacks manual:**
> Phase 7's tasks (git diff, commit, tag) are all automatable. The "human decision" (version number) is resolved earlier in the process. No current task genuinely requires pausing the sprint for human input. `manual` solves a problem that does not exist in practice.

**Advocate-Expanded defends manual:**
> Phase 7 task T07.05 ("Resolve version number: confirm v2.24.5 or v2.25.1 against project version history before tagging") is a genuine human decision point. The sprint runner cannot determine the correct version number -- it requires consulting release history and making a judgment call. Running this as a Claude task risks hallucinating a version number.

**Convergence on Necessity:** Both sides agree `claude`, `python`, and `skip` are necessary. Dispute centers on `python-gate` and `manual`.

| Point | Minimal | Expanded | Convergence |
|---|---|---|---|
| claude necessary | Yes | Yes | 100% |
| python necessary | Yes | Yes | 100% |
| skip necessary | Yes | Yes | 100% |
| python-gate necessary | No (YAGNI) | Yes (machine-readable gating) | 30% |
| manual necessary | No (no real use case) | Yes (version decisions) | 25% |
| hybrid necessary | No | No | 100% |
| dry-run necessary | No | No | 100% |

### Dimension 2: Clarity (Semantic Unambiguity)

**Advocate-Minimal attacks python-gate semantics:**
> What exactly does "the results determine whether subsequent phases activate" mean? Which subsequent phases? All of them? Only direct dependents? What if the gate result is ambiguous (not cleanly WORKING/BROKEN)? The semantics of `python-gate` require specifying a gate evaluation contract, which `python` does not.

**Advocate-Expanded defends:**
> The gate evaluation contract is defined by the phase's `condition` field, not by the execution mode. `python-gate` signals to the runner that this phase produces a machine-readable result (exit code, output artifact) that feeds into the condition system. The `condition` field specifies what to check. Clean separation: `execution_mode` says HOW to run; `condition` says WHAT the result means.

**Advocate-Minimal on python clarity:**
> `python` is clear: extract shell commands, run them, capture output. No ambiguity about what happens.

**Both agree on skip and claude clarity:** Unambiguous.

| Point | Minimal | Expanded | Convergence |
|---|---|---|---|
| claude clear | Yes | Yes | 100% |
| python clear | Yes | Yes | 100% |
| skip clear | Yes | Yes | 100% |
| python-gate clear | N/A (reject) | Partially (needs condition field) | 40% |
| manual clear | N/A (reject) | Yes (pause + resume) | N/A |

### Dimension 3: Composability

**Advocate-Expanded raises a composability concern with python:**
> If `python` phases are always EXEMPT tier (as the diff analysis suggests), should `execution_mode: python` automatically imply `tier: EXEMPT`? Or can you have a STRICT python phase?

**Advocate-Minimal responds:**
> `python` phases should NOT automatically imply EXEMPT. A python phase that runs security-critical validation commands (e.g., checking file permissions, scanning for secrets) could reasonably be STRICT. The tier controls the verification method, not the execution method. Keep them orthogonal.

**Both agree:** `skip` interacts cleanly with all fields (all fields become irrelevant for skipped phases). `claude` interacts cleanly (current behavior). `python` is mostly clean but the tier interaction needs documentation.

| Point | Minimal | Expanded | Convergence |
|---|---|---|---|
| claude composes well | Yes | Yes | 100% |
| skip composes well | Yes | Yes | 100% |
| python composes well | Mostly (tier orthogonal) | Mostly (tier should be EXEMPT for python) | 70% |
| python-gate composes well | N/A | Complex (cross-phase side effects) | N/A |

### Dimension 4: Forward Compatibility

**Advocate-Expanded argues for python-gate:**
> Future sprints will have more empirical gates. The annotation system should support them without ad-hoc prose conventions. Deferring `python-gate` until a second use case emerges means retrofitting the first use case.

**Advocate-Minimal responds:**
> Adding a value later is cheap. Removing one is expensive (breaking change). Start minimal, expand when evidence warrants. The v2.24.5 gate pattern may be unusual. Most sprints are linear sequences of claude phases.

**Advocate-Expanded argues for manual:**
> As the sprint runner matures, more tasks will involve human checkpoints (code review approvals, deployment confirmations, compliance sign-offs). Building `manual` now prepares for these patterns.

**Advocate-Minimal responds:**
> Speculative. The sprint runner is a developer productivity tool, not a compliance workflow engine. If compliance workflows emerge, they bring their own requirements that `manual` may not satisfy (e.g., audit trails, approval chains).

| Point | Minimal | Expanded | Convergence |
|---|---|---|---|
| 3 values sufficient for 2+ years | Minimal says yes | Expanded says no | 35% |
| Adding values later is cheap | Yes | Yes (but retrofitting is work) | 80% |
| python-gate prevents future tech debt | No | Yes | 30% |
| manual prevents future tech debt | No | Weak yes | 20% |

### Dimension 5: Implementation Cost

| Value | LOC Estimate | Complexity | Risk |
|---|---|---|---|
| claude | 0 (exists) | None | None |
| skip | ~10 | Trivial | None |
| python | ~80-120 | Medium (markdown parser + subprocess runner) | Low-Medium |
| python-gate | ~40-60 above python | Medium (gate result mapper + condition evaluator) | Medium |
| manual | ~60-80 | Medium (pause/resume + state persistence) | Medium |

**Advocate-Minimal:** Total for {claude, python, skip}: ~90-130 LOC new code.
**Advocate-Expanded:** Total for {claude, python, python-gate, skip, manual}: ~190-270 LOC new code. Roughly double for two values that may never be used.

| Point | Minimal | Expanded | Convergence |
|---|---|---|---|
| Implementation budget ~130 LOC | Acceptable | Acceptable | 100% |
| Implementation budget ~270 LOC | Unnecessary | Acceptable | 50% |
| Maintenance burden of 5 vs 3 values | Significant | Manageable | 45% |

---

## Round 3: Synthesis and Final Positions

### Advocate-Minimal Final Position

Three values: `claude`, `python`, `skip`.

**Strongest arguments:**
1. YAGNI: Only one gating phase exists today. Build `python-gate` when a second one appears.
2. Implementation cost: Half the code, half the maintenance, half the testing surface.
3. Flexibility: The dependency/condition system should handle flow control, not the execution mode enum.
4. Adding values later is cheap and non-breaking.

**Concession:** If the condition system gets a formal `condition` field in the tasklist format, the case for `python-gate` would strengthen because the gate semantics would have a defined contract.

### Advocate-Expanded Final Position

Five values: `claude`, `python`, `python-gate`, `skip`, `manual`.

**Strongest arguments:**
1. Machine-readable gating: `python-gate` eliminates prose-based conditionality, making the sprint runner autonomous.
2. Completeness: `manual` covers genuine human decision points that Claude cannot reliably automate.
3. Forward compatibility: Adding values later means retrofitting existing tasklists.
4. The cost delta (~100 LOC) is small relative to the sprint runner's total codebase.

**Concession:** `manual` has the weakest case. Could be deferred if the team commits to adding it when the first genuine human checkpoint arises.

### Convergence Assessment

| Debate Point | Convergence Score |
|---|---|
| claude, python, skip are the core set | 100% |
| hybrid should be rejected | 100% |
| dry-run should be rejected | 100% |
| python-gate adds real value | 50% |
| manual adds real value | 30% |
| 3 values sufficient for v1 | 65% |
| 5 values better for long-term | 40% |

**Overall Convergence: 69%**

### Moderator Observation

The debate reveals a genuine architectural tension: should `execution_mode` be purely about HOW a phase runs (mechanism), or should it also encode WHAT the result means for flow control (semantics)?

The Minimal position keeps `execution_mode` as a pure mechanism selector, pushing flow control to the dependency system. The Expanded position bundles mechanism + flow-control signal into the enum for pragmatic reasons (the dependency system lacks formal condition support today).

The strongest resolution may be a **4-value compromise**: `claude`, `python`, `skip`, plus a separate `condition` field on phases that handles gate semantics. This gives `python-gate`'s machine-readable gating without conflating mechanism and flow control.
