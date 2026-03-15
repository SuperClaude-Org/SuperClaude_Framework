# Adversarial Debate: Level 3 Solutions for `OSError [Errno 7] Argument list too long`

**Date**: 2026-03-15
**Solutions under debate**: 3A (stdin prompt delivery), 3B (prompt via `--file`), 3C (all prompts as files)
**Context**: Levels 1 and 2 (1A+1B+2A+2B) already prevent the immediate crash by calibrating `_EMBED_SIZE_LIMIT` against `MAX_ARG_STRLEN` and adding per-file guards.

---

## Round 1

### ADVOCATE: Level 3 hardening is necessary for long-term reliability

**Opening position**: Levels 1 and 2 are band-aids on a fundamentally fragile architecture. The root problem is that `ClaudeProcess.build_command()` unconditionally passes the prompt as a CLI argument via `-p`. Every guard we add in executor.py is a bet that we can predict the prompt size before it reaches `Popen`. Level 3 eliminates the entire class of failure by changing the transport mechanism.

**Argument 1: Guard proliferation is a maintenance liability**

We now have (or propose): `_EMBED_SIZE_LIMIT`, `_MAX_ARG_STRLEN`, `_PROMPT_TEMPLATE_OVERHEAD`, `_PER_FILE_EMBED_LIMIT`, and `_SPEC_FILE_WARN_THRESHOLD`. That is five constants governing a single invariant: "the `-p` argument must be shorter than 128 KB." Each constant requires calibration, testing, and documentation. Each is a potential site of future drift -- exactly the kind of drift that caused this bug in the first place (the comment said "100 KB" while the value was 200 KB). Level 3 reduces this to zero constants at the `ClaudeProcess` layer because prompts of any size are delivered via a mechanism that has no OS-imposed upper bound.

**Argument 2: The problem space is growing, not shrinking**

The roadmap pipeline already generates prompts approaching 150 KB when spec files and multi-file embeddings combine. As the framework matures, several trends push prompt sizes upward:
- More sophisticated prompt templates with richer instructions
- Multi-step pipelines that chain outputs as inputs (extraction -> analysis -> synthesis)
- Users bringing larger spec files as the tool gains adoption
- Potential future steps that embed multiple large artifacts

With Level 1+2 only, every one of these growth vectors requires re-auditing the guard constants. With Level 3, prompt growth is a non-issue -- the transport scales with the content.

**Argument 3: 3A (stdin) is the most viable variant and has low blast radius**

Solution 3A modifies only `ClaudeProcess` -- zero changes to executor logic, step definitions, or test infrastructure outside of process tests. The change is:
1. Add `_build_command_without_prompt()` that omits `-p`
2. Add `_start_with_stdin_prompt()` that pipes the prompt via stdin
3. Modify `start()` with a size threshold check

This is approximately 30 lines of code. The blast radius is contained to `process.py` and `test_process.py`. Compare this to the dozens of lines of guard logic, constants, and test updates required across `executor.py`, `test_file_passing.py`, and potentially other executor variants (remediate, validate).

**Argument 4: The `--file` fallback may itself be broken**

The current fallback passes `("--file", str(input_path))` -- but `claude --help` documents `--file` as expecting `file_id:relative_path` format. The fallback does NOT use this format. Either:
- (a) The fallback silently fails and we have never noticed because it was rarely triggered, or
- (b) `claude` accepts bare paths after `--file` as an undocumented behavior

Either way, the Levels 1+2 strategy depends on a `--file` fallback whose correctness is itself unvalidated. Level 3A (stdin) sidesteps this entirely by using a different delivery mechanism.

---

### CRITIC: Level 3 has unvalidated assumptions and the lower levels are sufficient

**Opening position**: Level 3 proposes to solve a problem we do not yet have, using a mechanism we have not yet confirmed works, at a cost that is higher than advertised. Levels 1+2 are sufficient, battle-tested patterns (constant calibration + size guards), and they can be shipped today.

**Rebuttal 1: Guard proliferation is manageable, not a crisis**

Five constants is not "proliferation" -- it is explicit encoding of system constraints. The alternative (Level 3) does not eliminate constants; it replaces them with a different kind of complexity: subprocess pipe management, stdin lifecycle, and a threshold that decides which delivery path to use. You still need `_PROMPT_FILE_THRESHOLD = 64 * 1024` -- that is a constant too. The difference is that Level 3's constant gates a code path bifurcation in `start()`, which is harder to test and debug than a simple value comparison in `executor.py`.

Moreover, the constants in Level 1+2 have clear derivations: `_MAX_ARG_STRLEN` comes from the Linux kernel, `_PROMPT_TEMPLATE_OVERHEAD` from measured template sizes, `_PER_FILE_EMBED_LIMIT` from the largest observed single-file input. These are not arbitrary -- they are documented, testable, and auditable. The "drift" that caused this bug was a comment/value mismatch, not a systemic flaw. Fix the derivation (1A) and the problem disappears.

**Rebuttal 2: The "growing problem space" argument is speculative**

The Advocate claims prompt sizes are growing, but provides no evidence beyond the current 150 KB case -- which is already handled by Level 1+2. The pipeline has existed for multiple releases without hitting this limit. The one case that did hit it was caused by a miscalibrated constant, not by prompt growth exceeding architectural capacity. Fixing the constant (1A) and measuring the full string (1B) restores a 30% safety margin. That margin is sufficient for the foreseeable roadmap.

If prompt sizes genuinely grow to exceed 120 KB routinely, that is a signal that prompt design needs attention, not that the transport mechanism needs re-engineering. Prompts that large are likely inefficient -- most LLMs have diminishing returns on very long system prompts. The architectural response should be to improve prompt compression, not to accommodate unbounded growth.

**Rebuttal 3: 3A's feasibility is unconfirmed -- that is the fatal flaw**

The entire 3A proposal rests on the assumption that `claude --print` reads prompts from stdin when `-p` is absent. This has NOT been tested. The `claude --help` output shows the prompt as a positional argument `[prompt]`, which in most CLI frameworks means it is read from `argv`, not `stdin`. If `claude` does not read from stdin:
- 3A is completely unviable
- We have wasted implementation time on a dead-end
- We must fall back to 3B or 3C, both of which have their own unconfirmed dependencies

The Advocate characterizes 3A as "30 lines of code" but omits the validation cost: someone must write a prototype, test it against the actual `claude` binary in multiple scenarios (empty stdin, partial writes, large prompts, concurrent processes), and confirm behavior with process groups (`os.setpgrp`). This is a minimum half-day of investigation before any implementation begins.

**Rebuttal 4: The `--file` concern cuts both ways**

The Advocate correctly notes that the `--file` fallback format may not match documentation. But this observation undermines Level 3 solutions too:
- 3B explicitly depends on `--file` working for prompt delivery
- 3C depends on `--file` working universally for all prompts
- Even 3A must be validated against undocumented `claude` behavior

The right response is to validate `--file` behavior (a 15-minute test), not to build an entirely new delivery mechanism. If `--file` with bare paths works (and the existing test suite passing suggests it does), then Level 1+2's fallback is confirmed safe, and Level 3 loses its strongest motivation.

---

## Round 2

### ADVOCATE: Response to Critic

**On constants vs. pipe complexity**: The Critic claims five constants are "manageable." But the bug we are debugging exists precisely because constants drifted. The Critic's own fix (1A: derive from `MAX_ARG_STRLEN`) admits the problem -- if the derivation were truly stable, why did it drift? Because constants in application code are subject to human editing, and humans edit constants when they think they know better ("let's bump the limit to 200 KB, it's fine"). A code path that bypasses the constraint entirely cannot drift because there is no constant to change.

The `_PROMPT_FILE_THRESHOLD` in 3A is a performance optimization, not a safety constraint. If it is set wrong, prompts just take the stdin path unnecessarily -- there is no crash. Compare this to `_EMBED_SIZE_LIMIT`: if that is set wrong, the process crashes with an OS error. The asymmetry in failure modes is the core argument for Level 3.

**On speculative growth**: The Critic calls the growth argument speculative, but the pipeline is 4 months old and already hit the limit. The first spec file to exceed 100 KB caused a crash. The trend is clear: (a) the framework's own generated artifacts (extraction, roadmap) are already 30-50 KB each, (b) user spec files have no upper bound and grow with project complexity, (c) new pipeline steps are being added (the `portify` pipeline is in active development). Dismissing this as speculative is betting against the trajectory of the project's own usage patterns.

**On stdin feasibility**: The Critic is correct that 3A's feasibility is unconfirmed. I concede this point. The validation MUST happen before implementation work begins. However, the validation is a single test:

```bash
echo "Hello, what is 2+2?" | claude --print --output-format text
```

If this produces a response, stdin delivery works. If it does not, 3A is dead and we fall back to investigating 3B/3C or defer Level 3 entirely. This is a 5-minute test, not a half-day investigation. The Critic is inflating the validation cost.

**On `--file` cutting both ways**: Fair point, but the implications differ. For Level 1+2, `--file` must work correctly as a fallback for the crash path -- this is a safety-critical dependency. For Level 3A, `--file` is irrelevant because stdin is used instead. The Critic conflates 3A with 3B/3C. If 3A's stdin approach is validated, the `--file` question becomes moot for prompt delivery.

**Revised position**: 3A is the strongest variant IF stdin delivery is confirmed. 3B and 3C should be abandoned unless 3A fails validation -- they both depend on the same unconfirmed `--file` semantics that the Critic correctly identifies as problematic.

---

### CRITIC: Final response

**On failure mode asymmetry**: The Advocate makes a fair point about the asymmetry between a performance-optimization constant (3A) and a safety-critical constant (1A). I concede that a transport mechanism without an upper bound is architecturally superior to one that requires careful constant management. However, "architecturally superior" does not mean "necessary now."

**On the 5-minute test**: The Advocate simplifies the validation. A single `echo | claude` test confirms basic stdin reading, but does NOT validate:
1. Behavior with prompts containing special characters, newlines, Unicode
2. Interaction with `--output-format stream-json` vs `text`
3. Behavior when stdin is closed before `claude` finishes reading (race condition)
4. Interaction with `os.setpgrp` -- if the child is in a separate process group, does the stdin pipe remain valid?
5. Behavior under concurrent process launches (the pipeline may run multiple steps)

These are not theoretical concerns. Pipe-based IPC in subprocess management is a known source of subtle bugs (deadlocks, partial reads, broken pipes on signal). The `claude` binary is not our code -- we cannot inspect its stdin reading implementation. We are coupling our process lifecycle to undocumented behavior of an external tool.

**On timing and risk**: Levels 1+2 can be shipped in this sprint with high confidence. Level 3A requires:
1. Validation (even if 5 minutes for basic confirmation, more for edge cases)
2. Implementation (~30 lines, granted)
3. Test updates for the bifurcated `start()` path
4. Integration testing with the actual pipeline

This is not prohibitive, but it IS more than what is needed to fix the current bug. The question is not "should we ever do Level 3" but "should we do Level 3 NOW." My position: no. Ship 1A+1B+2A, validate stdin delivery as a separate spike, and implement 3A in v2.26 if the spike confirms feasibility. The pipeline is currently blocked; unblock it with the minimum viable fix.

**Concession on 3A vs 3B/3C**: I agree with the Advocate that 3B and 3C are weaker than 3A. The `--file` semantics are genuinely unclear, and building an architectural redesign (3C) on unconfirmed `--file` behavior is reckless. If Level 3 is pursued, 3A is the only defensible choice.

**Final position**: Level 3 is a sound long-term investment but a premature short-term priority. Defer to v2.26 as a spike-then-implement task.

---

## Verdict

### Confidence Score: 45/100 that Level 3 should be pursued NOW

Level 3 is architecturally sound but operationally premature. The arguments for its long-term value are compelling (failure mode asymmetry, growth trajectory, elimination of constant management). The arguments against immediate implementation are equally compelling (unvalidated feasibility, sufficient coverage from L1+L2, blocked pipeline needs a fast fix).

### Most Viable Variant: 3A (stdin prompt delivery)

**Rationale**:
- 3A is the only variant that does not depend on the ambiguous `--file` semantics
- 3A has the smallest blast radius (process.py only, no executor changes)
- 3A's threshold constant is fail-safe (wrong value = performance cost, not crash)
- 3B is weaker because it inherits the `--file` format ambiguity
- 3C is the highest-risk variant: largest change surface, depends on `--file`, and the "all prompts as files" design is over-engineered for a problem that only manifests above 128 KB

### Pre-Validation Requirements (BLOCKING)

Before ANY Level 3 implementation work begins, the following must be confirmed:

| # | Validation | Method | Pass Criteria | Estimated Time |
|---|-----------|--------|---------------|----------------|
| V1 | `claude --print` reads prompt from stdin | `echo "test prompt" \| claude --print --output-format text` | Produces a valid response | 5 min |
| V2 | Stdin works with large prompts (>128 KB) | Pipe a 200 KB prompt via stdin, confirm full processing | Response references content from late in the prompt | 10 min |
| V3 | Stdin + `os.setpgrp` compatibility | Run the stdin delivery in a child process group, confirm no broken pipe | Process completes normally | 15 min |
| V4 | Stdin + special characters | Pipe prompt containing Unicode, backticks, newlines, null bytes adjacent | No truncation or encoding errors | 10 min |
| V5 | Stdin closure timing | Close stdin immediately after write, confirm `claude` reads fully before processing | Complete response, no partial read | 10 min |

**Total validation cost**: ~50 minutes for a thorough spike. This is modest but should be a dedicated task, not embedded in an implementation PR.

### Recommendation: DEFER to v2.26

**Immediate action (this sprint)**:
1. Ship L1 (1A+1B) and L2 (2A+2B) to unblock the pipeline -- these are sufficient and low-risk
2. Create a spike ticket for v2.26: "Validate stdin prompt delivery for ClaudeProcess (3A)"

**v2.26 action (next release)**:
1. Execute the validation spike (V1-V5 above)
2. If all validations pass: implement 3A with the `_PROMPT_FILE_THRESHOLD` approach
3. If validations fail: close the spike, document findings, Level 1+2 remains the permanent solution
4. Do NOT pursue 3B or 3C regardless of 3A outcome -- the `--file` semantics are too unclear

**Rationale for deferral**:
- The pipeline is currently blocked. Shipping L1+L2 unblocks it in ~2 hours.
- L3 adds ~1 day of work (spike + implementation + testing) with an unconfirmed feasibility gate.
- L1+L2 provide complete crash prevention for all currently known scenarios.
- L3's value is insurance against future scenarios that have not yet materialized.
- Deferral is reversible -- nothing in L1+L2 prevents later L3 implementation.

### Risk Assessment if Level 3 is Skipped Entirely

| Risk | Probability | Impact | Mitigation (without L3) |
|------|------------|--------|------------------------|
| Prompt size exceeds recalibrated `_EMBED_SIZE_LIMIT` | Low (next 6 months) | Medium (crash, requires constant bump) | L2A per-file guard catches most cases |
| `--file` fallback silently fails | Unknown | High (data loss / wrong results) | Validate `--file` behavior independently (separate task) |
| New pipeline steps generate >120 KB prompts | Medium (next 12 months) | Low (guard triggers fallback safely) | L1B full-string measurement prevents crash |
| Constants drift again via human editing | Low | Medium (re-introduces bug) | L1A derivation from `MAX_ARG_STRLEN` makes intent explicit |

**Net assessment**: Skipping Level 3 entirely is acceptable for the next 1-2 releases. The compounding risk of constant management over 4+ releases tilts toward eventual Level 3 adoption, making it a v2.26-v2.27 candidate rather than a "never."
